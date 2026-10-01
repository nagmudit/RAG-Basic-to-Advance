"""Chapter 15 exact KD branch-and-bound and toy random-hyperplane LSH.

These standard-library implementations expose work and errors. The scope
strings are static teaching fixtures, never authenticated identities.
"""

from __future__ import annotations

import math
import random
import heapq
from dataclasses import dataclass


def vector(values, dimension=None):
    try:
        result = tuple(float(x) for x in values)
    except (ValueError, TypeError) as exc:
        raise ValueError("Coordinates must be numeric") from exc
    if not result or (dimension is not None and len(result) != dimension):
        raise ValueError("Positive and matching dimension required")
    if not all(math.isfinite(x) for x in result):
        raise ValueError("Nonfinite coordinate")
    return result


def squared_l2(a, b):
    return math.fsum((x-y)**2 for x, y in zip(a, b))


def dot(a, b):
    return math.fsum(x*y for x, y in zip(a, b))


def unit(values):
    values = vector(values)
    magnitude = math.sqrt(dot(values, values))
    if magnitude == 0 or not math.isfinite(magnitude):
        raise ValueError("Zero/overflowing vector cannot be normalized")
    return tuple(x/magnitude for x in values)


def exact_cosine(rows, query, *, scope, k):
    """Scan pre-normalized rows; return (ID, cosine) pairs and work."""
    if k < 1:
        raise ValueError("k must be positive")
    q = unit(query)
    ranked = [(row["item_id"], dot(q, row["vector"])) for row in rows
              if scope in row["allowed_scopes"]]
    best = heapq.nsmallest(k, ranked, key=lambda pair: (-pair[1], pair[0]))
    return best, {"eligible": len(ranked), "scored_vectors": len(ranked),
                        "coordinate_products": len(ranked)*len(q)}


@dataclass
class KDNode:
    lower: tuple
    upper: tuple
    indices: tuple | None = None
    axis: int | None = None
    pivot: float | None = None
    left: "KDNode | None" = None
    right: "KDNode | None" = None


class KDTree:
    """Exact Euclidean KNN using bounding-box lower bounds and backtracking."""

    def __init__(self, rows, *, leaf_size=8):
        self.rows = [{**row} for row in rows]  # caller supplies authorized roster
        if not self.rows or leaf_size < 1:
            raise ValueError("Nonempty rows and positive leaf size required")
        self.dimension = len(vector(self.rows[0]["vector"]))
        seen = set()
        for row in self.rows:
            row["vector"] = vector(row["vector"], self.dimension)
            if row["item_id"] in seen:
                raise ValueError("Duplicate ID")
            seen.add(row["item_id"])
        self.leaf_size = leaf_size
        self.root = self._build(tuple(range(len(self.rows))))

    def _build(self, indices):
        lower = tuple(min(self.rows[i]["vector"][axis] for i in indices)
                      for axis in range(self.dimension))
        upper = tuple(max(self.rows[i]["vector"][axis] for i in indices)
                      for axis in range(self.dimension))
        if len(indices) <= self.leaf_size:
            return KDNode(lower, upper, indices=indices)
        axis = max(range(self.dimension), key=lambda j: upper[j]-lower[j])
        ordered = sorted(indices, key=lambda i: (self.rows[i]["vector"][axis],
                                                 self.rows[i]["item_id"]))
        midpoint = len(ordered)//2
        left_edge = self.rows[ordered[midpoint-1]]["vector"][axis]
        right_edge = self.rows[ordered[midpoint]]["vector"][axis]
        return KDNode(lower, upper, axis=axis, pivot=(left_edge+right_edge)/2,
                      left=self._build(tuple(ordered[:midpoint])),
                      right=self._build(tuple(ordered[midpoint:])))

    @staticmethod
    def lower_bound_squared(node, q):
        return math.fsum((low-x)**2 if x < low else (x-high)**2 if x > high else 0.0
                         for x, low, high in zip(q, node.lower, node.upper))

    def search(self, query, *, k):
        if k < 1:
            raise ValueError("k must be positive")
        q = vector(query, self.dimension)
        best = []  # ascending (squared distance, ID)
        work = {"visited_nodes": 0, "pruned_nodes": 0, "scored_vectors": 0,
                "eligible": len(self.rows), "dimension": self.dimension}

        def visit(node):
            work["visited_nodes"] += 1
            bound = self.lower_bound_squared(node, q)
            # Strict > retains equal-distance candidates for stable ID ties.
            if len(best) >= k and bound > best[-1][0] + 1e-14:
                work["pruned_nodes"] += 1
                return
            if node.indices is not None:
                for i in node.indices:
                    row = self.rows[i]
                    best.append((squared_l2(q, row["vector"]), row["item_id"]))
                    best.sort()
                    if len(best) > k:
                        best.pop()
                    work["scored_vectors"] += 1
                return
            children = sorted((node.left, node.right),
                              key=lambda child: self.lower_bound_squared(child, q))
            for child in children:
                visit(child)

        visit(self.root)
        return [(item_id, math.sqrt(distance)) for distance, item_id in best], work


class HyperplaneLSH:
    """Independent random sign-bit tables; empty buckets return no candidates."""

    def __init__(self, rows, *, tables, bits, seed, source_version):
        self.rows = list(rows)
        if not self.rows or tables < 1 or bits < 1 or not source_version:
            raise ValueError("Nonempty rows/version and positive tables/bits required")
        self.dimension = len(vector(self.rows[0]["vector"]))
        self.by_id = {}
        for row in self.rows:
            item_id = row["item_id"]
            if not isinstance(item_id, str) or not item_id or item_id in self.by_id:
                raise ValueError("Unique nonempty IDs required")
            self.by_id[item_id] = {"vector": unit(vector(row["vector"], self.dimension)),
                                   "allowed_scopes": frozenset(row["allowed_scopes"])}
        self.tables, self.bits, self.seed = tables, bits, seed
        self.source_version = source_version
        rng = random.Random(seed)
        self.planes = [[unit(tuple(rng.gauss(0, 1) for _ in range(self.dimension)))
                        for _ in range(bits)] for _ in range(tables)]
        self.buckets = [{} for _ in range(tables)]
        for item_id, row in self.by_id.items():
            for table, planes in zip(self.buckets, self.planes):
                signature = self._signature(row["vector"], planes)
                table.setdefault(signature, []).append(item_id)
        for table in self.buckets:
            for members in table.values():
                members.sort()

    @staticmethod
    def _signature(values, planes):
        signature = 0
        for plane in planes:
            signature = (signature << 1) | int(dot(values, plane) >= 0)
        return signature

    def search(self, query, *, scope, k):
        if k < 1:
            raise ValueError("k must be positive")
        q = unit(vector(query, self.dimension))
        seen = set()
        bucket_entries = 0
        signatures = []
        for table, planes in zip(self.buckets, self.planes):
            signature = self._signature(q, planes)
            signatures.append(signature)
            members = table.get(signature, [])
            bucket_entries += len(members)
            seen.update(item_id for item_id in members
                        if scope in self.by_id[item_id]["allowed_scopes"])
        ranked = [(item_id, dot(q, self.by_id[item_id]["vector"])) for item_id in seen]
        ranked.sort(key=lambda pair: (-pair[1], pair[0]))
        return ranked[:k], {"eligible": sum(scope in row["allowed_scopes"]
                                             for row in self.by_id.values()),
                            "bucket_entries": bucket_entries,
                            "candidate_union": len(seen), "scored_vectors": len(seen),
                            "query_plane_dots": self.tables*self.bits,
                            "signatures": signatures,
                            "no_bucket_match": not seen,
                            "candidate_stages": {"scored": ranked, "eligible_bucket_union": ranked}}
