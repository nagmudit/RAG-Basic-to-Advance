"""Chapter 10: transparent exact vector scoring over a static scope fixture.

Coordinates are caller-supplied numeric features. They are not learned
embeddings, calibrated relevance scores, or authorization decisions.
"""

import heapq
import math
from dataclasses import dataclass


METRICS = ("dot", "cosine", "l2", "l1")


def checked_vector(values, dimension=None):
    try:
        vector = tuple(float(value) for value in values)
    except (TypeError, ValueError) as exc:
        raise ValueError("Vector coordinates must be numeric") from exc
    if not vector or (dimension is not None and len(vector) != dimension):
        raise ValueError("Vector must have the declared positive dimension")
    if not all(math.isfinite(value) for value in vector):
        raise ValueError("Vector coordinates must be finite")
    return vector


def dot(a, b):
    if len(a) != len(b):
        raise ValueError("Dimension mismatch")
    return math.fsum(x * y for x, y in zip(a, b))


def norm(a):
    return math.hypot(*a)


def unit(a):
    magnitude = norm(a)
    if magnitude == 0 or not math.isfinite(magnitude):
        raise ValueError("Cosine is undefined for a zero or overflowing norm")
    return tuple(x / magnitude for x in a)


def measure(a, b, metric):
    if len(a) != len(b):
        raise ValueError("Dimension mismatch")
    if metric == "dot":
        value = dot(a, b)
    elif metric == "cosine":
        value = dot(unit(a), unit(b))
    elif metric == "l2":
        value = math.sqrt(math.fsum((x - y) ** 2 for x, y in zip(a, b)))
    elif metric == "l1":
        value = math.fsum(abs(x - y) for x, y in zip(a, b))
    else:
        raise ValueError(f"Unknown metric: {metric}")
    if not math.isfinite(value):
        raise ValueError("Score overflow")
    return value


@dataclass(frozen=True)
class Entry:
    item_id: str
    vector: tuple
    allowed_scopes: frozenset
    unit_vector: tuple | None


class ExactIndex:
    def __init__(self, records, *, version):
        records = list(records)
        if not records or not version:
            raise ValueError("Nonempty records and index version are required")
        first = checked_vector(records[0]["vector"])
        self.dimension = len(first)
        self.version = version
        seen = set()
        entries = []
        for record in records:
            item_id = record["item_id"]
            if not isinstance(item_id, str) or not item_id or item_id in seen:
                raise ValueError("Item IDs must be unique nonempty strings")
            seen.add(item_id)
            vector = checked_vector(record["vector"], self.dimension)
            scopes = frozenset(record["allowed_scopes"])
            if not scopes or not all(isinstance(x, str) and x for x in scopes):
                raise ValueError("Each item needs declared scopes")
            entries.append(Entry(item_id, vector, scopes,
                                 unit(vector) if norm(vector) else None))
        self.entries = tuple(entries)

    def search(self, query, *, scope, metric="cosine", top_k=2, plan="sort"):
        """Return exact top-k and work. Apply static eligibility before scoring.

        Scope is a controlled fixture, not caller authentication. In production,
        derive and enforce it from a trusted authorization service.
        """
        if metric not in METRICS or plan not in ("sort", "heap"):
            raise ValueError("Unknown metric or execution plan")
        if not isinstance(top_k, int) or top_k < 1:
            raise ValueError("top_k must be a positive integer")
        q = checked_vector(query, self.dimension)
        q_unit = unit(q) if metric == "cosine" else None
        eligible = [entry for entry in self.entries if scope in entry.allowed_scopes]
        if metric == "cosine" and any(entry.unit_vector is None for entry in eligible):
            raise ValueError("Cosine is undefined for an eligible zero vector")
        work = {"indexed_vectors": len(self.entries),
                "eligible_vectors": len(eligible), "scored_vectors": 0,
                "dimension": self.dimension,
                "coordinate_comparisons": 0, "plan": plan}

        def scored():
            for entry in eligible:
                value = (dot(q_unit, entry.unit_vector) if metric == "cosine"
                         else measure(q, entry.vector, metric))
                if not math.isfinite(value):
                    raise ValueError("Score overflow")
                work["scored_vectors"] += 1
                work["coordinate_comparisons"] += self.dimension
                yield {"item_id": entry.item_id, "value": value}

        # Minimize distance; maximize similarity. Equal raw values use ID.
        key = (lambda row: (-row["value"], row["item_id"])) if metric in ("dot", "cosine") else (lambda row: (row["value"], row["item_id"]))
        rows = (sorted(scored(), key=key)[:top_k] if plan == "sort"
                else heapq.nsmallest(top_k, scored(), key=key))
        return rows, work
