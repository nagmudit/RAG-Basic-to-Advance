"""Chapter 6: explicit TF-IDF variants on Chapter 5's positional index.

The default score is sum(tf * ln(N/df)) over distinct query terms. Here N and
df use eligible *segments* in the chosen static scope. This is one declared
TF-IDF convention, not a claim that every search engine uses this formula.
"""

import argparse
import json
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter

from lexical_index import (
    Analyzer, FROZEN_QUESTIONS, Index, build_context, build_index, build_prompt,
    load_corpus, stub_answer,
)


MODES = ("raw", "sublinear", "cosine")


@dataclass
class ScopeStats:
    n_segments: int
    df: dict
    raw_vector_norm: dict

    def idf(self, term):
        count = self.df.get(term, 0)
        # An unseen term has no postings; never evaluate log(N/0).
        if not count or not self.n_segments:
            return 0.0
        return math.log(self.n_segments / count)


@dataclass
class WeightedIndex:
    base: object
    by_scope: dict
    title_boost: float
    version: str
    statistics_build_ms: float


def weighted_tf(posting, title_boost):
    return len(posting.body_positions) + title_boost * len(posting.title_positions)


def sublinear_tf(posting, title_boost):
    """Scale integer field counts first, then apply the title multiplier."""
    body_count = len(posting.body_positions)
    title_count = len(posting.title_positions)
    body_weight = 1 + math.log(body_count) if body_count else 0.0
    title_weight = 1 + math.log(title_count) if title_count else 0.0
    return body_weight + title_boost * title_weight


def build_weighted_index(corpus, analyzer=Analyzer(), title_boost=1.0):
    """Build scope-local DF and norms from a corpus or a prepared V1 index."""
    if not math.isfinite(title_boost) or title_boost <= 0:
        raise ValueError("title_boost must be positive and finite")
    base = corpus if isinstance(corpus, Index) else build_index(corpus, analyzer)
    started = perf_counter()
    by_scope = {}
    for scope, eligible in base.scope_ordinals.items():
        n = len(eligible)
        df = {
            term: count
            for term, rows in base.postings.items()
            if (count := sum(row.ordinal in eligible for row in rows)) > 0
        }
        norms_sq = {ordinal: 0.0 for ordinal in eligible}
        for term, rows in base.postings.items():
            if term not in df:
                continue
            idf = math.log(n / df[term])
            for row in rows:
                if row.ordinal in eligible:
                    weight = weighted_tf(row, title_boost) * idf
                    norms_sq[row.ordinal] += weight * weight
        by_scope[scope] = ScopeStats(
            n_segments=n,
            df=df,
            raw_vector_norm={ordinal: math.sqrt(value) for ordinal, value in norms_sq.items()},
        )
    return WeightedIndex(
        base=base,
        by_scope=by_scope,
        title_boost=title_boost,
        version=f"v1-ch06-lnNdf-{base.version}-title{title_boost!r}",
        statistics_build_ms=(perf_counter() - started) * 1000,
    )


def search(index, question, *, scope="support-team", top_k=8, mode="raw"):
    """Score posting-union candidates; return source records and redacted work."""
    if top_k < 1:
        raise ValueError("top_k must be positive")
    if mode not in MODES:
        raise ValueError(f"mode must be one of {MODES}")
    base = index.base
    eligible = base.scope_ordinals.get(scope, frozenset())
    stats = index.by_scope.get(scope, ScopeStats(0, {}, {}))
    query_terms = sorted(set(base.analyzer.terms(question)))
    scores = {}
    visited = 0
    query_norm_sq = 0.0
    for term in query_terms:
        idf = stats.idf(term)
        query_norm_sq += idf * idf
        for posting in base.posting(term):
            if posting.ordinal not in eligible:
                continue
            visited += 1
            tf = weighted_tf(posting, index.title_boost)
            if mode == "raw":
                contribution = tf * idf
            elif mode == "sublinear":
                contribution = sublinear_tf(posting, index.title_boost) * idf
            else:
                # Query vector uses binary query TF and one IDF factor;
                # document vector uses raw TF times IDF.
                contribution = tf * idf * idf
            scores[posting.ordinal] = scores.get(posting.ordinal, 0.0) + contribution
    if mode == "cosine":
        query_norm = math.sqrt(query_norm_sq)
        for ordinal, dot in scores.items():
            denominator = stats.raw_vector_norm[ordinal] * query_norm
            scores[ordinal] = dot / denominator if denominator else 0.0
    ranked = sorted(
        scores,
        key=lambda ordinal: (
            -scores[ordinal],
            int(base.segments[ordinal]["document_id"][1:]),
            base.segments[ordinal]["section_order"],
            base.segments[ordinal]["segment_number"],
        ),
    )
    candidates = [
        {**base.segments[ordinal], "score": scores[ordinal]}
        for ordinal in ranked[:top_k]
    ]
    return candidates, {
        "eligible_segments": len(eligible),
        "eligible_posting_visits": visited,
        "scored_segments": len(scores),
        "query_term_count": len(query_terms),
        "zero_score_candidates": sum(scores[ordinal] == 0 for ordinal in scores),
    }


def explain(index, question, segment_id, *, scope="support-team", mode="raw"):
    """Local teaching breakdown. Avoid logging arbitrary query terms broadly."""
    if mode not in MODES:
        raise ValueError(f"mode must be one of {MODES}")
    base = index.base
    eligible = base.scope_ordinals.get(scope, frozenset())
    matching = [i for i, segment in enumerate(base.segments) if segment["segment_id"] == segment_id]
    if not matching or matching[0] not in eligible:
        raise PermissionError("Segment is unavailable under this scope")
    ordinal = matching[0]
    stats = index.by_scope[scope]
    result = []
    for term in sorted(set(base.analyzer.terms(question))):
        posting = next((row for row in base.posting(term) if row.ordinal == ordinal), None)
        tf = weighted_tf(posting, index.title_boost) if posting else 0.0
        idf = stats.idf(term)
        if mode == "raw":
            contribution = tf * idf
        elif mode == "sublinear":
            contribution = sublinear_tf(posting, index.title_boost) * idf if posting else 0.0
        else:
            query_norm = math.sqrt(sum(stats.idf(t) ** 2 for t in set(base.analyzer.terms(question))))
            denominator = query_norm * stats.raw_vector_norm[ordinal]
            contribution = tf * idf * idf / denominator if denominator else 0.0
        result.append({
            "term": term, "tf": tf, "df": stats.df.get(term, 0),
            "n": stats.n_segments, "idf": idf, "contribution": contribution,
        })
    return result


class RankedEngine:
    def __init__(self, corpus, analyzer=Analyzer(), title_boost=1.0):
        self.index = build_weighted_index(corpus, analyzer, title_boost)

    def run(self, query_id, *, mode="raw", scope="support-team", top_k=8,
            context_budget_words=120, question=None, request_id="r-v1-ch06-001"):
        if query_id not in FROZEN_QUESTIONS:
            raise ValueError("Use one of the two frozen V0 query IDs")
        question = question or FROZEN_QUESTIONS[query_id]
        started = perf_counter()
        search_started = perf_counter()
        candidates, work = search(self.index, question, scope=scope, top_k=top_k, mode=mode)
        search_ms = (perf_counter() - search_started) * 1000
        context_started = perf_counter()
        context, context_words = build_context(candidates, context_budget_words)
        prompt = build_prompt(question, context)
        context_ms = (perf_counter() - context_started) * 1000
        answer_started = perf_counter()
        answer, status, reason, evidence_ids = stub_answer(query_id, context)
        if status == "abstained" and not candidates:
            reason = "no_result"
        elif status == "abstained" and not context:
            reason = "context_empty"
        answer_ms = (perf_counter() - answer_started) * 1000
        trace = {
            "request_id": request_id,
            "query_id": query_id,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "corpus_snapshot": self.index.base.snapshot,
            "index_version": self.index.base.version,
            "analyzer_version": self.index.base.analyzer.version,
            "scoring_version": self.index.version,
            "score_mode": mode,
            "candidate_scores": [
                {"segment_id": part["segment_id"], "score": round(part["score"], 6)}
                for part in candidates
            ],
            "context_ids": [part["segment_id"] for part in context],
            "evidence_ids": evidence_ids,
            "work": work,
            "context_words": context_words,
            "estimated_prompt_tokens": (len(prompt) + 3) // 4,
            "status": status,
            "reason": reason,
            "latency_ms": {
                "search": round(search_ms, 3),
                "context": round(context_ms, 3),
                "stub_answer": round(answer_ms, 3),
                "wall": round((perf_counter() - started) * 1000, 3),
            },
        }
        return answer, trace, prompt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--query-id", choices=sorted(FROZEN_QUESTIONS), default="q-contract-change")
    parser.add_argument("--mode", choices=MODES, default="raw")
    parser.add_argument("--scope", default="support-team")
    parser.add_argument("--top-k", type=int, default=8)
    parser.add_argument("--title-boost", type=float, default=1.0)
    parser.add_argument("--context-budget-words", type=int, default=120)
    parser.add_argument("--show-prompt", action="store_true")
    args = parser.parse_args()
    engine = RankedEngine(load_corpus(), title_boost=args.title_boost)
    answer, trace, prompt = engine.run(
        args.query_id, mode=args.mode, scope=args.scope, top_k=args.top_k,
        context_budget_words=args.context_budget_words,
    )
    print(json.dumps({
        "index_version": engine.index.base.version,
        "scoring_version": engine.index.version,
        "postings_build_ms": round(engine.index.base.build_ms, 3),
        "statistics_build_ms": round(engine.index.statistics_build_ms, 3),
        "eligible_segments": engine.index.by_scope.get(args.scope, ScopeStats(0, {}, {})).n_segments,
    }, indent=2))
    if args.show_prompt:
        print("\nLOCAL FICTIONAL PROMPT PREVIEW (contains source text):\n" + prompt)
    print("\nAnswer:\n" + answer)
    print("\nRedacted request trace:\n" + json.dumps(trace, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
