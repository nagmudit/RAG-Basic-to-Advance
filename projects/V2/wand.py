"""Chapter 8: a transparent exact-top-k WAND variant over Chapter 7 BM25.

Index time caches eligible per-term impacts and conservative global bounds.
Query time uses document-at-a-time cursors, a min-heap, and a pivot bound.
This is a teaching implementation, not a compressed-disk search engine.
"""

import argparse
import heapq
import json
import math
from bisect import bisect_left
from dataclasses import dataclass
from pathlib import Path
from time import perf_counter

from bm25 import BM25Index, build_bm25_index, saturation
from lexical_index import load_corpus


@dataclass(frozen=True)
class TermColumn:
    ordinals: tuple
    impacts: tuple
    upper_bound: float


@dataclass(frozen=True)
class WANDIndex:
    bm25: BM25Index
    by_scope: dict
    version: str
    impact_build_ms: float
    stored_impacts: int


@dataclass
class Cursor:
    term: str
    column: TermColumn
    pos: int = 0

    @property
    def current(self):
        return (self.column.ordinals[self.pos]
                if self.pos < len(self.column.ordinals) else math.inf)

    def seek(self, target):
        before = self.pos
        self.pos = bisect_left(self.column.ordinals, target, self.pos)
        return self.pos - before


def _tie_key(segment):
    return (int(segment["document_id"][1:]), segment["section_order"],
            segment["segment_number"])


def build_wand_index(corpus_or_bm25, *, k1=1.2, b=.75, title_boost=1.0):
    bm25 = (corpus_or_bm25 if isinstance(corpus_or_bm25, BM25Index)
            else build_bm25_index(corpus_or_bm25, k1=k1, b=b,
                                  title_boost=title_boost))
    started = perf_counter()
    by_scope = {}
    impacts_count = 0
    for scope, stats in bm25.by_scope.items():
        eligible = bm25.base.scope_ordinals[scope]
        columns = {}
        for term, postings in bm25.base.postings.items():
            idf = stats.idf(term)
            rows = []
            for posting in postings:
                if posting.ordinal not in eligible:
                    continue
                tf = (len(posting.body_positions)
                      + bm25.title_boost * len(posting.title_positions))
                impact = idf * saturation(
                    tf, stats.lengths[posting.ordinal], stats.avgdl, bm25.k1, bm25.b
                )
                rows.append((posting.ordinal, impact))
            if rows:
                ordinals, impacts = zip(*rows)
                # One outward ULP keeps the stored term bound conservative.
                upper = math.nextafter(max(impacts), math.inf)
                columns[term] = TermColumn(ordinals, impacts, upper)
                impacts_count += len(rows)
        by_scope[scope] = columns
    return WANDIndex(
        bm25, by_scope, f"v2-ch08-wand-global-ub-{bm25.version}",
        (perf_counter() - started) * 1000, impacts_count,
    )


def _bound(columns):
    """Round a positive upper-bound sum outward for float scoring safety."""
    if not columns:
        return 0.0
    value = math.fsum(column.upper_bound for column in columns)
    # Standard float accumulation of these same positive terms can round up.
    # The margin covers query-length accumulation error; ties remain eligible.
    return value + (len(columns) + 2) * math.ulp(value)


def exhaustive_cached_search(index, question, *, scope="support-team", top_k=8):
    """Score every eligible posting-union candidate from the SAME impact cache.

    This is the controlled Chapter 8 execution baseline. Chapter 7's direct
    formula scorer remains the independent exact-score oracle.
    """
    if top_k < 1:
        raise ValueError("top_k must be positive")
    base = index.bm25.base
    terms = sorted(set(base.analyzer.terms(question)))
    columns = index.by_scope.get(scope, {})
    scores = {}
    contributions = 0
    for term in terms:
        column = columns.get(term)
        if column is None:
            continue
        for ordinal, impact in zip(column.ordinals, column.impacts):
            scores[ordinal] = scores.get(ordinal, 0.0) + impact
            contributions += 1
    ranked = sorted(scores, key=lambda ordinal: (
        -scores[ordinal], *_tie_key(base.segments[ordinal]), ordinal
    ))
    candidates = [
        {**base.segments[ordinal], "score": scores[ordinal]}
        for ordinal in ranked[:top_k]
    ]
    return candidates, {
        "eligible_segments": len(base.scope_ordinals.get(scope, frozenset())),
        "query_term_count": len(terms),
        "query_posting_lists": sum(term in columns for term in terms),
        "fully_scored_segments": len(scores),
        "score_contributions": contributions,
    }


def search(index, question, *, scope="support-team", top_k=8,
           capture_steps=False):
    """Return Chapter 7's exact ordered top-k, with pruning work counters.

    capture_steps reveals query terms and candidate positions; use it only on
    fictional data or within a protected local debugging boundary.
    """
    if top_k < 1:
        raise ValueError("top_k must be positive")
    base = index.bm25.base
    terms = sorted(set(base.analyzer.terms(question)))
    columns = index.by_scope.get(scope, {})
    cursors = [Cursor(term, columns[term]) for term in terms if term in columns]
    heap = []  # worst retained item: (score, reverse tie key, ordinal)
    steps = [] if capture_steps else None
    scored = contributions = seeks = postings_skipped = pivots = 0
    early_terminated = False
    while True:
        active = sorted((c for c in cursors if c.current != math.inf),
                        key=lambda c: (c.current, c.term))
        if not active:
            break
        full = len(heap) == top_k
        threshold = heap[0][0] if full else -math.inf
        prefix = []
        pivot = None
        pivot_bound = None
        for cursor in active:
            prefix.append(cursor.column)
            possible = _bound(prefix)
            if not full or possible >= threshold:  # >= preserves score ties
                pivot = cursor.current
                pivot_bound = possible
                break
        if pivot is None:
            early_terminated = True
            if steps is not None:
                steps.append({"action": "terminate", "threshold": threshold,
                              "active": {c.term: c.current for c in active},
                              "remaining_upper_bound": _bound([c.column for c in active])})
            break
        pivots += 1
        first = active[0]
        if first.current < pivot:
            before = first.current
            skipped = first.seek(pivot)
            seeks += 1
            postings_skipped += skipped
            if steps is not None:
                steps.append({"action": "seek", "term": first.term,
                              "from": before, "to": first.current,
                              "pivot": pivot, "threshold": threshold,
                              "pivot_upper_bound": pivot_bound,
                              "postings_advanced": skipped})
            continue
        ordinal = pivot
        matched = sorted((c for c in active if c.current == ordinal),
                         key=lambda c: c.term)
        # Same term order and float addition as Chapter 7's exhaustive scorer.
        score = 0.0
        for cursor in matched:
            score += cursor.column.impacts[cursor.pos]
        scored += 1
        contributions += len(matched)
        tie = _tie_key(base.segments[ordinal])
        heap_key = (score, *(-part for part in tie), -ordinal)
        if len(heap) < top_k:
            heapq.heappush(heap, heap_key)
        elif heap_key > heap[0]:
            heapq.heapreplace(heap, heap_key)
        if steps is not None:
            steps.append({"action": "score", "ordinal": ordinal,
                          "segment_id": base.segments[ordinal]["segment_id"],
                          "score": score, "matched_terms": [c.term for c in matched],
                          "threshold_before": threshold if full else None,
                          "threshold_after": heap[0][0] if len(heap) == top_k else None})
        for cursor in matched:
            cursor.pos += 1
    ranked = sorted(heap, key=lambda x: (-x[0], -x[1], -x[2], -x[3]))
    candidates = [
        {**base.segments[-item[4]], "score": item[0]} for item in ranked
    ]
    work = {
        "eligible_segments": len(base.scope_ordinals.get(scope, frozenset())),
        "query_term_count": len(terms),
        "query_posting_lists": len(cursors),
        "fully_scored_segments": scored,
        "score_contributions": contributions,
        "pivot_checks": pivots,
        "seek_calls": seeks,
        "postings_advanced_by_seek": postings_skipped,
        "early_terminated": early_terminated,
    }
    return candidates, work, steps


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--question", default="12000 credits")
    parser.add_argument("--scope", default="support-team")
    parser.add_argument("--top-k", type=int, default=2)
    parser.add_argument("--toy-trace", action="store_true",
                        help="use fictional pruning fixture and print cursor details")
    args = parser.parse_args()
    if args.toy_trace:
        corpus = json.loads((Path(__file__).parent / "toy_pruning_corpus.json")
                            .read_text(encoding="utf-8"))
        question = "rare common"
        top_k = 1
    else:
        corpus = load_corpus()
        question = args.question
        top_k = args.top_k
    index = build_wand_index(corpus)
    candidates, work, steps = search(
        index, question, scope=args.scope, top_k=top_k,
        capture_steps=args.toy_trace,
    )
    print(json.dumps({
        "index_version": index.version,
        "impact_build_ms": round(index.impact_build_ms, 3),
        "stored_impacts": index.stored_impacts,
        "candidate_scores": [
            {"segment_id": item["segment_id"], "score": round(item["score"], 6)}
            for item in candidates
        ],
        "work": work,
        **({"local_fictional_steps": steps} if args.toy_trace else {}),
    }, ensure_ascii=True, allow_nan=False, indent=2))


if __name__ == "__main__":
    main()
