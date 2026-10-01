"""Separate worked answer: attempt the learner task first. Standard library only."""

import math


def weighted_sparse_score(query, postings, eligible_ids):
    scores = {}
    for term, qweight in sorted(query.items()):
        if not math.isfinite(qweight) or qweight < 0:
            raise ValueError("Invalid query weight")
        if qweight == 0:
            continue
        for item_id, dweight in postings.get(term, []):
            if item_id not in eligible_ids:
                continue
            if not math.isfinite(dweight) or dweight <= 0:
                raise ValueError("Invalid stored weight")
            scores[item_id] = scores.get(item_id, 0) + qweight*dweight
    return sorted(scores.items(), key=lambda p: (-p[1], p[0]))


def maxsim(query, document):
    if not query or not document:
        raise ValueError("Empty unmasked token set")
    dimension = len(query[0])
    if not dimension or any(len(v) != dimension or not all(math.isfinite(x) for x in v)
                            or not math.isclose(sum(x*x for x in v), 1, abs_tol=1e-6)
                            for v in query + document):
        raise ValueError("Expected equal-dimension unit token vectors")
    grid = [[sum(a*b for a, b in zip(q, d)) for d in document] for q in query]
    winners = [max(range(len(row)), key=lambda j: row[j]) for row in grid]
    return sum(grid[i][j] for i, j in enumerate(winners)), grid, winners
