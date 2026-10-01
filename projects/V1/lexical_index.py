"""Chapter 5: transparent positional index over the fictional V0 corpus.

Run from the repository root:
    python -X utf8 projects/V1/lexical_index.py
    python -X utf8 projects/V1/lexical_index.py --phrase "initial response target"

V1 at Chapter 5 changes candidate generation, not V0's answer contract or
unweighted overlap score. Chapter 6 will add weighted lexical ranking.
"""

import argparse
import json
import re
import sys
import unicodedata
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "V0"))
from engine import (  # noqa: E402 - explicit dependency on the frozen V0 snapshot
    FROZEN_QUESTIONS,
    build_context,
    build_prompt,
    load_corpus,
    segment_corpus,
    stub_answer,
    tokenize as v0_tokenize,
)


UNICODE_TERM = re.compile(r"[^\W_]+(?:-[^\W_]+)*", re.UNICODE)


@dataclass(frozen=True)
class Analyzer:
    name: str = "v0"

    @property
    def version(self):
        return self.name if self.name == "v0" else f"{self.name}-u{unicodedata.unidata_version}"

    def terms(self, text):
        if self.name == "v0":
            return v0_tokenize(text)
        if self.name == "unicode_nfc":
            # NFC preserves more distinctions than NFKC. Casefold may change
            # code-point sequences, so normalize again before tokenization.
            normalized = unicodedata.normalize(
                "NFC", unicodedata.normalize("NFC", text).casefold()
            )
            return UNICODE_TERM.findall(normalized)
        raise ValueError(f"Unknown analyzer: {self.name}")


@dataclass(frozen=True)
class Posting:
    ordinal: int
    segment_id: str
    title_positions: tuple
    body_positions: tuple

    @property
    def term_frequency(self):
        return len(self.title_positions) + len(self.body_positions)


@dataclass
class Index:
    snapshot: str
    analyzer: Analyzer
    segments: tuple
    postings: dict
    scope_ordinals: dict
    field_lengths: dict
    version: str
    build_ms: float
    term_document_pairs: int
    position_count: int
    source_identities: dict

    def posting(self, term):
        return self.postings.get(term, ())


def build_index(corpus, analyzer=Analyzer()):
    """Prepare field positions and scope membership once, before requests."""
    started = perf_counter()
    # Additive evidence identities do not change analyzer, rankings or index version.
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "common"))
    from qrel_identity import document_identity
    segments = tuple(segment_corpus(corpus))
    mutable = {}
    scopes = {}
    field_lengths = {}
    position_count = 0
    for ordinal, segment in enumerate(segments):
        for scope in segment["allowed_scopes"]:
            scopes.setdefault(scope, set()).add(ordinal)
        field_lengths[ordinal] = {}
        for field, text in (("title", segment["title"]), ("body", segment["text"])):
            terms = analyzer.terms(text)
            field_lengths[ordinal][field] = len(terms)
            for position, term in enumerate(terms):
                entry = mutable.setdefault(term, {}).setdefault(
                    ordinal, {"title": [], "body": []}
                )
                entry[field].append(position)
                position_count += 1
    postings = {
        term: tuple(
            Posting(
                ordinal,
                segments[ordinal]["segment_id"],
                tuple(fields["title"]),
                tuple(fields["body"]),
            )
            for ordinal, fields in sorted(by_ordinal.items())
        )
        for term, by_ordinal in mutable.items()
    }
    return Index(
        snapshot=corpus["snapshot"],
        analyzer=analyzer,
        segments=segments,
        postings=postings,
        scope_ordinals={scope: frozenset(ords) for scope, ords in scopes.items()},
        field_lengths=field_lengths,
        version=f"v1-ch05-{corpus['snapshot']}-{analyzer.version}",
        build_ms=(perf_counter() - started) * 1000,
        term_document_pairs=sum(len(rows) for rows in postings.values()),
        position_count=position_count,
        source_identities={d["id"]: document_identity(d) for d in corpus["documents"]},
    )


def search(index, question, scope="support-team", top_k=8):
    """Union eligible postings; retain V0's distinct-overlap score and order."""
    if top_k < 1:
        raise ValueError("top_k must be positive")
    query_terms = set(index.analyzer.terms(question))
    eligible = index.scope_ordinals.get(scope, frozenset())
    matched = {}
    eligible_posting_visits = 0
    for term in query_terms:
        for posting in index.posting(term):
            if posting.ordinal not in eligible:
                continue  # never fetch source text or score an ineligible segment
            eligible_posting_visits += 1
            matched.setdefault(posting.ordinal, set()).add(term)
    ranked = sorted(
        matched,
        key=lambda ordinal: (
            -len(matched[ordinal]),
            int(index.segments[ordinal]["document_id"][1:]),
            index.segments[ordinal]["section_order"],
            index.segments[ordinal]["segment_number"],
        ),
    )
    candidates = [
        {**index.segments[ordinal], "score": len(matched[ordinal])}
        for ordinal in ranked[:top_k]
    ]
    return candidates, {
        "eligible_segments": len(eligible),
        "eligible_posting_visits": eligible_posting_visits,
        "scored_segments": len(matched),
        "query_term_count": len(query_terms),
    }


def _ordinals_for(index, text, eligible):
    terms = index.analyzer.terms(text)
    if len(terms) != 1:
        raise ValueError(f"Expected one analyzed term, got {terms!r}")
    return {row.ordinal for row in index.posting(terms[0]) if row.ordinal in eligible}


def boolean_ids(index, *, all_terms=(), any_terms=(), not_terms=(), scope="support-team"):
    """Return eligible IDs for (AND all) AND (OR any) AND NOT excluded.

    At least one positive term is required; complementing an entire corpus is
    neither an information need nor a safe default API operation.
    """
    if not all_terms and not any_terms:
        raise ValueError("At least one positive term is required")
    eligible = index.scope_ordinals.get(scope, frozenset())
    found = set(eligible)
    for term in all_terms:
        found &= _ordinals_for(index, term, eligible)
    if any_terms:
        union = set()
        for term in any_terms:
            union |= _ordinals_for(index, term, eligible)
        found &= union
    for term in not_terms:
        found -= _ordinals_for(index, term, eligible)
    return [index.segments[ordinal]["segment_id"] for ordinal in sorted(found)]


def phrase_ids(index, phrase, *, field="body", scope="support-team"):
    """Intersect document postings, then require consecutive field positions."""
    if field not in ("title", "body"):
        raise ValueError("field must be title or body")
    terms = index.analyzer.terms(phrase)
    if not terms:
        return []
    eligible = index.scope_ordinals.get(scope, frozenset())
    by_term = [
        {row.ordinal: row for row in index.posting(term) if row.ordinal in eligible}
        for term in terms
    ]
    possible = set(by_term[0])
    for rows in by_term[1:]:
        possible &= rows.keys()
    result = []
    for ordinal in sorted(possible):
        positions = [set(getattr(rows[ordinal], f"{field}_positions")) for rows in by_term]
        if any(all(start + offset in positions[offset] for offset in range(1, len(terms)))
               for start in positions[0]):
            result.append(index.segments[ordinal]["segment_id"])
    return result


class IndexedEngine:
    def __init__(self, corpus, analyzer=Analyzer()):
        self.index = build_index(corpus, analyzer)

    def run(self, query_id, *, scope="support-team", top_k=8, context_budget_words=120,
            question=None, request_id="r-v1-001"):
        if query_id not in FROZEN_QUESTIONS:
            raise ValueError("Use one of the two frozen V0 query IDs")
        question = question or FROZEN_QUESTIONS[query_id]
        started = perf_counter()
        search_started = perf_counter()
        candidates, work = search(self.index, question, scope, top_k)
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
            "corpus_snapshot": self.index.snapshot,
            "index_version": self.index.version,
            "analyzer_version": self.index.analyzer.version,
            "candidate_scores": [
                {"segment_id": part["segment_id"], "score": part["score"]}
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
    parser.add_argument("--analyzer", choices=("v0", "unicode_nfc"), default="v0")
    parser.add_argument("--query-id", choices=sorted(FROZEN_QUESTIONS), default="q-contract-change")
    parser.add_argument("--scope", default="support-team")
    parser.add_argument("--top-k", type=int, default=8)
    parser.add_argument("--context-budget-words", type=int, default=120)
    parser.add_argument("--phrase", help="Also inspect body phrase matches")
    parser.add_argument("--show-prompt", action="store_true")
    args = parser.parse_args()
    engine = IndexedEngine(load_corpus(), Analyzer(args.analyzer))
    index = engine.index
    print(json.dumps({
        "index_version": index.version,
        "segments": len(index.segments),
        "vocabulary_terms": len(index.postings),
        "term_document_pairs": index.term_document_pairs,
        "position_count": index.position_count,
        "build_ms": round(index.build_ms, 3),
    }, indent=2))
    if args.phrase:
        print("Body phrase IDs:", phrase_ids(index, args.phrase, scope=args.scope))
    answer, trace, prompt = engine.run(
        args.query_id, scope=args.scope, top_k=args.top_k,
        context_budget_words=args.context_budget_words,
    )
    if args.show_prompt:
        print("\nLOCAL FICTIONAL PROMPT PREVIEW (contains source text):\n" + prompt)
    print("\nAnswer:\n" + answer)
    print("\nRedacted request trace:\n" + json.dumps(trace, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
