"""Separate worked answer: attempt the learner task first. Standard library only."""

import math


def safe_top_k(items, k, score):
    if k < 1 or len({i for i, _ in items}) != len(items):
        raise ValueError("Invalid k or duplicate ID")
    if any(not math.isfinite(bound) or bound < 0 for _, bound in items):
        raise ValueError("Bounds must be finite and nonnegative")
    best, scored, skipped, thresholds = [], [], [], []
    for item_id, bound in sorted(items, key=lambda p: (-p[1], p[0])):
        threshold = best[-1][1] if len(best) == k else -math.inf
        thresholds.append((item_id, threshold))
        # Equality cannot skip: a lexicographically earlier ID might win a tie.
        if bound < threshold:
            skipped.append(item_id)
            continue
        value = score(item_id)
        if not math.isfinite(value) or value < 0 or value > bound + 1e-12:
            raise ValueError("Scored value violates bound contract")
        scored.append(item_id)
        best = sorted(best + [(item_id, value)], key=lambda p: (-p[1], p[0]))[:k]
    return dict(ranking=best, scored_ids=scored, skipped_ids=skipped, thresholds=thresholds)
