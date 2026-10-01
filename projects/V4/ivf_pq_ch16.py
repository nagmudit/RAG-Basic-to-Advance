"""Chapter 16 teaching IVF-Flat and residual IVF-PQ, with explicit error sites.

Pure Python and deliberately unoptimized. The caller supplies a trusted static
eligible roster; `scope` is an additional fixture gate, not authentication.
"""

from __future__ import annotations

import heapq
import math
import random

from ann_ch15 import squared_l2, unit, vector


def train_kmeans(samples, k, *, seed=16, iterations=8):
    """Deterministic farthest-first initialization followed by Lloyd updates."""
    if not samples or not 1 <= k <= len(samples) or iterations < 1:
        raise ValueError("Need at least k training vectors and positive iterations")
    dimensions = len(samples[0])
    points = [vector(row, dimensions) for row in samples]
    first = random.Random(seed).randrange(len(points))
    centers = [points[first]]
    chosen = {first}
    while len(centers) < k:
        idx = max((i for i in range(len(points)) if i not in chosen),
                  key=lambda i: (min(squared_l2(points[i], c) for c in centers), -i))
        chosen.add(idx)
        centers.append(points[idx])
    for _ in range(iterations):
        groups = [[] for _ in centers]
        for point in points:
            closest = min(range(k), key=lambda j: (squared_l2(point, centers[j]), j))
            groups[closest].append(point)
        updated = [tuple(math.fsum(p[j] for p in group) / len(group)
                         for j in range(dimensions)) if group else centers[i]
                   for i, group in enumerate(groups)]
        if updated == centers:
            break
        centers = updated
    return tuple(centers)


class IVFPQ:
    """One coarse assignment per vector; residual PQ and optional originals."""

    def __init__(self, rows, *, nlist, subspaces, bits, training_ids=None,
                 seed=16, iterations=8, keep_originals=True, source_version="toy"):
        if not rows or nlist < 1 or subspaces < 1 or bits < 1 or bits > 8:
            raise ValueError("Invalid IVF/PQ parameters")
        ids = [row["item_id"] for row in rows]
        if len(set(ids)) != len(ids):
            raise ValueError("Item IDs must be unique")
        self.dimension = len(rows[0]["vector"])
        if self.dimension % subspaces:
            raise ValueError("Dimension must be divisible by subspaces")
        self.nlist, self.subspaces, self.bits = nlist, subspaces, bits
        self.width = self.dimension // subspaces
        self.keep_originals = keep_originals
        self.source_version = source_version
        normalized = {row["item_id"]: unit(vector(row["vector"], self.dimension))
                      for row in rows}
        train_ids = ids if training_ids is None else list(training_ids)
        if len(set(train_ids)) != len(train_ids) or not set(train_ids) <= set(ids):
            raise ValueError("Training IDs must be unique indexed IDs")
        if len(train_ids) < max(nlist, 1 << bits):
            raise ValueError("Insufficient training vectors for centroids/codewords")
        self.training_ids = tuple(train_ids)
        self.centroids = train_kmeans([normalized[i] for i in train_ids], nlist,
                                     seed=seed, iterations=iterations)
        assignments = {i: self._assign(normalized[i]) for i in ids}
        residuals = [tuple(normalized[i][j] - self.centroids[assignments[i]][j]
                           for j in range(self.dimension)) for i in train_ids]
        self.codebooks = tuple(train_kmeans(
            [r[m*self.width:(m+1)*self.width] for r in residuals], 1 << bits,
            seed=seed + 100 + m, iterations=iterations) for m in range(subspaces))
        self.lists = [[] for _ in range(nlist)]
        self.rows = {}
        self.deleted = set()
        for row in rows:
            self.add(row, precomputed=normalized[row["item_id"]])

    def _assign(self, x):
        return min(range(self.nlist), key=lambda j: (squared_l2(x, self.centroids[j]), j))

    def _encode(self, x, list_id):
        residual = tuple(x[j] - self.centroids[list_id][j]
                         for j in range(self.dimension))
        return tuple(min(range(len(self.codebooks[m])),
                         key=lambda c: (squared_l2(residual[m*self.width:(m+1)*self.width],
                                                    self.codebooks[m][c]), c))
                     for m in range(self.subspaces))

    def add(self, row, *, precomputed=None):
        item_id = row["item_id"]
        if item_id in self.rows:
            raise ValueError("Duplicate ID; versioned update needs delete/rebuild")
        x = precomputed if precomputed is not None else unit(vector(row["vector"], self.dimension))
        list_id = self._assign(x)
        code = self._encode(x, list_id)
        self.rows[item_id] = {"list_id": list_id, "code": code,
                              "vector": x if self.keep_originals else None,
                              "allowed_scopes": tuple(row["allowed_scopes"])}
        self.lists[list_id].append(item_id)

    def delete(self, item_id):
        if item_id not in self.rows:
            raise KeyError(item_id)
        self.deleted.add(item_id)

    def reconstruct(self, item_id):
        """Decode one residual code; useful for auditing geometric distortion."""
        row = self.rows[item_id]
        center = self.centroids[row["list_id"]]
        return tuple(center[j] + self.codebooks[j//self.width]
                     [row["code"][j//self.width]][j % self.width]
                     for j in range(self.dimension))

    def squared_reconstruction_error(self, item_id):
        if not self.keep_originals:
            raise ValueError("Reconstruction error needs a retained original")
        return squared_l2(self.rows[item_id]["vector"], self.reconstruct(item_id))

    def search(self, query, *, scope, k, nprobe, mode="flat", rerank_depth=0):
        if k < 1 or not 1 <= nprobe <= self.nlist or mode not in ("flat", "adc"):
            raise ValueError("Invalid search parameters")
        if (mode == "flat" or rerank_depth) and not self.keep_originals:
            raise ValueError("Exact scoring requires retained originals")
        if rerank_depth and (mode != "adc" or rerank_depth < k):
            raise ValueError("Rerank requires ADC and depth >= k")
        q = unit(vector(query, self.dimension))
        probes = sorted(range(self.nlist),
                        key=lambda j: (squared_l2(q, self.centroids[j]), j))[:nprobe]
        scores = []
        eligible = 0
        for list_id in probes:
            if mode == "adc":
                qr = tuple(q[j] - self.centroids[list_id][j] for j in range(self.dimension))
                lookup = [[squared_l2(qr[m*self.width:(m+1)*self.width], word)
                           for word in self.codebooks[m]] for m in range(self.subspaces)]
            for item_id in self.lists[list_id]:
                row = self.rows[item_id]
                if item_id in self.deleted or scope not in row["allowed_scopes"]:
                    continue
                eligible += 1
                dist = (squared_l2(q, row["vector"]) if mode == "flat" else
                        math.fsum(lookup[m][row["code"][m]] for m in range(self.subspaces)))
                scores.append((dist, item_id))
        ordered = heapq.nsmallest(rerank_depth or k, scores)
        reranked_count = len(ordered) if rerank_depth else 0
        if rerank_depth:
            ordered = sorted((squared_l2(q, self.rows[item_id]["vector"]), item_id)
                             for _, item_id in ordered)[:k]
        result = [(item_id, -dist) for dist, item_id in ordered[:k]]
        return result, {"probed_lists": probes,
                        "list_lengths": [len(self.lists[j]) for j in probes],
                        "eligible_scored": eligible,
                        "distance_mode": mode,
                        "original_reranked": reranked_count,
                        "empty_eligible_probe": eligible == 0}

    def storage_lower_bounds(self):
        n = len(self.rows)
        return {"raw_float32_vectors_bytes": 4*n*self.dimension,
                "ids_uint64_bytes": 8*n,
                "coarse_float32_bytes": 4*self.nlist*self.dimension,
                "pq_code_payload_bits": n*self.subspaces*self.bits,
                "pq_code_packed_bytes": (n*self.subspaces*self.bits + 7)//8,
                "pq_codebook_float32_bytes": 4*self.subspaces*(1 << self.bits)*self.width,
                "note": "Payload lower bounds exclude Python objects, list offsets, scopes, tombstones and allocator overhead; exact reranking also retains originals."}
