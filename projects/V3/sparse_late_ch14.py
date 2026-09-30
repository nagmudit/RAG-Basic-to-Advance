"""Chapter 14 mechanism sandbox; fixed toy logits/vectors are not trained models.

The functions expose the scoring and storage boundaries of SPLADE-style
vocabulary vectors and ColBERT-style MaxSim without pretending to implement
their transformer encoders, training losses, or production candidate indexes.
"""

from __future__ import annotations

import math
from collections import defaultdict
from dataclasses import dataclass


def sparse_pool(token_logits: list[dict[str, float]]) -> dict[str, float]:
    """max over positions of log(1 + ReLU(logit)) for each vocabulary term."""
    if not token_logits:
        raise ValueError("At least one non-padding token position is required")
    pooled: dict[str, float] = {}
    for position in token_logits:
        for term, logit in position.items():
            if not math.isfinite(logit):
                raise ValueError("Vocab logits must be finite")
            value = math.log1p(max(0.0, logit))
            if value > pooled.get(term, 0.0):
                pooled[term] = value
    return pooled


@dataclass(frozen=True)
class SparseRow:
    item_id: str
    scope: str
    weights: dict[str, float]


class SparseIndex:
    """Exact weighted-posting union, with eligibility before accumulation."""

    def __init__(self, rows: list[SparseRow]):
        self.rows = {row.item_id: row for row in rows}
        if len(self.rows) != len(rows):
            raise ValueError("Duplicate IDs")
        self.postings: dict[str, list[tuple[str, float]]] = defaultdict(list)
        for row in rows:
            for term, weight in row.weights.items():
                if not math.isfinite(weight) or weight <= 0:
                    raise ValueError("Stored weights must be finite and positive")
                self.postings[term].append((row.item_id, weight))
        for postings in self.postings.values():
            postings.sort()

    def search(self, query: dict[str, float], scope: str, k: int):
        if k < 1:
            raise ValueError("k must be positive")
        scores: dict[str, float] = defaultdict(float)
        visited = 0
        eligible = sum(row.scope == scope for row in self.rows.values())
        for term, query_weight in sorted(query.items()):
            if not math.isfinite(query_weight) or query_weight < 0:
                raise ValueError("Query weights must be finite and nonnegative")
            if query_weight == 0:
                continue
            for item_id, document_weight in self.postings.get(term, []):
                if self.rows[item_id].scope != scope:
                    continue
                visited += 1
                scores[item_id] += query_weight * document_weight
        ranked = sorted(scores.items(), key=lambda pair: (-pair[1], pair[0]))[:k]
        return ranked, {"eligible_rows": eligible, "posting_entries_scored": visited,
                        "positive_score_candidates": len(scores)}


def _validated_tokens(tokens: list[tuple[float, ...]], dimension: int | None = None):
    if not tokens:
        raise ValueError("At least one unmasked token vector is required")
    dimension = dimension or len(tokens[0])
    if dimension < 1:
        raise ValueError("Empty vector")
    for vector in tokens:
        if len(vector) != dimension or not all(math.isfinite(x) for x in vector):
            raise ValueError("Mismatched dimension or nonfinite coordinate")
        if not math.isclose(sum(x*x for x in vector), 1.0, abs_tol=1e-6):
            raise ValueError("Toy token vectors must be unit-normalized")
    return dimension


def maxsim(query: list[tuple[float, ...]], document: list[tuple[float, ...]]):
    """Exact sum over query tokens of their best document-token dot score."""
    dimension = _validated_tokens(query)
    _validated_tokens(document, dimension)
    grid = [[sum(a*b for a, b in zip(q, d)) for d in document] for q in query]
    winners = [max(range(len(row)), key=lambda j: row[j]) for row in grid]
    return sum(grid[i][j] for i, j in enumerate(winners)), grid, winners


def pooled_cosine(query: list[tuple[float, ...]], document: list[tuple[float, ...]]):
    """Cosine of mean-pooled toy tokens; not the Chapter 11 trained encoder."""
    dimension = _validated_tokens(query)
    _validated_tokens(document, dimension)
    q = [sum(vector[i] for vector in query)/len(query) for i in range(dimension)]
    d = [sum(vector[i] for vector in document)/len(document) for i in range(dimension)]
    qnorm = math.sqrt(sum(x*x for x in q))
    dnorm = math.sqrt(sum(x*x for x in d))
    if qnorm == 0 or dnorm == 0:
        raise ValueError("Mean-pooled cosine is undefined for a zero vector")
    return sum(a*b for a, b in zip(q, d))/(qnorm*dnorm)
