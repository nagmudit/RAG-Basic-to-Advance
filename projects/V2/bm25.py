"""Chapter 7: transparent BM25 over V1's eligible positional postings.

This educational scorer uses eligible *segments* as documents, one combined
title/body field (default equal weight), and Lucene-style nonnegative IDF.
It exhaustively scores the posting union. Chapter 8 adds safe top-k pruning.
"""

import argparse
import json
import math
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "V1"))
from lexical_index import (  # noqa: E402 - explicit versioned V1 dependency
    Analyzer, FROZEN_QUESTIONS, Index, build_context, build_index,
    build_prompt, load_corpus, stub_answer,
)


@dataclass(frozen=True)
class ScopeStats:
    n_segments: int
    df: dict
    lengths: dict
    avgdl: float

    def idf(self, term):
        count = self.df.get(term, 0)
        if count == 0 or self.n_segments == 0:
            return 0.0  # no posting, not a scored zero-weight match
        return math.log1p((self.n_segments - count + 0.5) / (count + 0.5))


@dataclass(frozen=True)
class BM25Index:
    base: Index
    by_scope: dict
    k1: float
    b: float
    title_boost: float
    version: str
    statistics_build_ms: float


def saturation(tf, length, avgdl, k1=1.2, b=0.75):
    """BM25 positive-match term factor; length and avgdl are analyzed terms."""
    if tf <= 0:
        return 0.0
    if avgdl <= 0:
        raise ValueError("positive tf requires a positive average length")
    return tf * (k1 + 1) / (tf + k1 * (1 - b + b * length / avgdl))


def build_bm25_index(corpus, analyzer=Analyzer(), *, k1=1.2, b=0.75,
                     title_boost=1.0):
    if not math.isfinite(k1) or k1 <= 0:
        raise ValueError("k1 must be positive and finite")
    if not math.isfinite(b) or not 0 <= b <= 1:
        raise ValueError("b must be finite in [0, 1]")
    if not math.isfinite(title_boost) or title_boost <= 0:
        raise ValueError("title_boost must be positive and finite")
    base = corpus if isinstance(corpus, Index) else build_index(corpus, analyzer)
    started = perf_counter()
    by_scope = {}
    for scope, eligible in base.scope_ordinals.items():
        lengths = {
            ordinal: sum(base.field_lengths[ordinal].values())
            for ordinal in eligible
        }
        df = {
            term: count
            for term, rows in base.postings.items()
            if (count := sum(row.ordinal in eligible for row in rows)) > 0
        }
        by_scope[scope] = ScopeStats(
            n_segments=len(eligible), df=df, lengths=lengths,
            avgdl=sum(lengths.values()) / len(eligible),
        )
    version = (f"v2-ch07-bm25-segment-log1p-{base.version}-"
               f"k1{k1!r}-b{b!r}-title{title_boost!r}")
    return BM25Index(base, by_scope, k1, b, title_boost, version,
                     (perf_counter() - started) * 1000)


def search(index, question, *, scope="support-team", top_k=8):
    """Exhaustively score eligible posting-union candidates, then exact sort."""
    if top_k < 1:
        raise ValueError("top_k must be positive")
    base = index.base
    eligible = base.scope_ordinals.get(scope, frozenset())
    stats = index.by_scope.get(scope, ScopeStats(0, {}, {}, 0.0))
    terms = sorted(set(base.analyzer.terms(question)))
    scores = {}
    visits = 0
    for term in terms:
        idf = stats.idf(term)
        for posting in base.posting(term):
            if posting.ordinal not in eligible:
                continue
            visits += 1
            tf = (len(posting.body_positions)
                  + index.title_boost * len(posting.title_positions))
            contribution = idf * saturation(
                tf, stats.lengths[posting.ordinal], stats.avgdl, index.k1, index.b
            )
            scores[posting.ordinal] = scores.get(posting.ordinal, 0.0) + contribution
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
        "eligible_posting_visits": visits,
        "scored_segments": len(scores),
        "query_term_count": len(terms),
        "zero_score_candidates": sum(score == 0 for score in scores.values()),
    }


def explain(index, question, segment_id, *, scope="support-team"):
    """Local fictional-data breakdown; never log private query terms broadly."""
    base = index.base
    eligible = base.scope_ordinals.get(scope, frozenset())
    matching = [i for i, segment in enumerate(base.segments)
                if segment["segment_id"] == segment_id]
    if not matching or matching[0] not in eligible:
        raise PermissionError("Segment is unavailable under this scope")
    ordinal = matching[0]
    stats = index.by_scope[scope]
    rows = []
    for term in sorted(set(base.analyzer.terms(question))):
        posting = next((row for row in base.posting(term)
                        if row.ordinal == ordinal), None)
        tf = (len(posting.body_positions) + index.title_boost * len(posting.title_positions)
              if posting else 0.0)
        idf = stats.idf(term)
        rows.append({
            "term": term, "tf": tf, "df": stats.df.get(term, 0),
            "n": stats.n_segments, "length": stats.lengths[ordinal],
            "avgdl": stats.avgdl, "idf": idf,
            "contribution": idf * saturation(tf, stats.lengths[ordinal],
                                             stats.avgdl, index.k1, index.b),
        })
    return rows


class BM25Engine:
    def __init__(self, corpus, analyzer=Analyzer(), *, k1=1.2, b=0.75,
                 title_boost=1.0):
        self.index = build_bm25_index(corpus, analyzer, k1=k1, b=b,
                                      title_boost=title_boost)

    def run(self, query_id, *, scope="support-team", top_k=8,
            context_budget_words=120, question=None, request_id="r-v2-ch07-001"):
        if query_id not in FROZEN_QUESTIONS:
            raise ValueError("Use a frozen V0 query ID")
        question = question or FROZEN_QUESTIONS[query_id]
        started = perf_counter()
        search_started = perf_counter()
        candidates, work = search(self.index, question, scope=scope, top_k=top_k)
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
            "candidate_scores": [
                {"segment_id": item["segment_id"], "score": round(item["score"], 6)}
                for item in candidates
            ],
            "context_ids": [item["segment_id"] for item in context],
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
    parser.add_argument("--query-id", choices=sorted(FROZEN_QUESTIONS),
                        default="q-contract-change")
    parser.add_argument("--scope", default="support-team")
    parser.add_argument("--top-k", type=int, default=8)
    parser.add_argument("--k1", type=float, default=1.2)
    parser.add_argument("--b", type=float, default=0.75)
    parser.add_argument("--title-boost", type=float, default=1.0)
    parser.add_argument("--show-prompt", action="store_true")
    args = parser.parse_args()
    engine = BM25Engine(load_corpus(), k1=args.k1, b=args.b,
                        title_boost=args.title_boost)
    answer, trace, prompt = engine.run(args.query_id, scope=args.scope,
                                       top_k=args.top_k)
    print(json.dumps({
        "postings_build_ms": round(engine.index.base.build_ms, 3),
        "statistics_build_ms": round(engine.index.statistics_build_ms, 3),
        "scoring_version": engine.index.version,
    }, indent=2))
    if args.show_prompt:
        print("LOCAL FICTIONAL PROMPT PREVIEW:\n" + prompt)
    print("Answer:\n" + answer)
    print("Redacted trace:\n" + json.dumps(trace, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
