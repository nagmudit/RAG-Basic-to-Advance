"""Inspectable, single-threaded HNSW teaching index. No external ANN library.

Squared L2, lexicographic ID ties; construction only on a static eligible roster.
No compression, live ACL service, durable mutation or production concurrency.
"""
from __future__ import annotations

import hashlib
import heapq
import json
import math
import random
from pathlib import Path


def vector(values, dimension=None):
    out = tuple(float(x) for x in values)
    if not out or (dimension is not None and len(out) != dimension):
        raise ValueError("Vector dimension mismatch")
    if not all(math.isfinite(x) for x in out):
        raise ValueError("Nonfinite vector")
    return out


def squared_l2(a, b):
    if len(a) != len(b):
        raise ValueError("Vector dimension mismatch")
    result = sum((x-y)**2 for x, y in zip(a, b))
    if not math.isfinite(result):
        raise ValueError("Nonfinite distance")
    return result


class ReverseID(str):
    """Invert ID ordering for the worst-first heap without scanning the corpus."""
    def __lt__(self, other):
        return str.__gt__(self, other)


def search_layer(query, vectors, adjacency, entry_ids, ef, *, blocked=(), cache=None,
                 capture=True):
    """Two heaps: nearest expansion frontier C, worst retained neighbor W.

    ef bounds W, not distance evaluations, visits, or C. Blocked vertices are
    neither scored nor traversed. Full snapshots are intentionally expensive.
    The caller supplies a validated graph and query of the same dimension.
    """
    if not isinstance(ef, int) or isinstance(ef, bool) or ef < 1:
        raise ValueError("ef must be a positive integer")
    blocked, cache = set(blocked), {} if cache is None else cache
    frontier, retained, visited, scored, events = [], [], set(), [], []

    def distance(item):
        if item not in cache:
            cache[item] = squared_l2(query, vectors[item])
        scored.append(item)
        return cache[item]

    def offer(item, value):
        heapq.heappush(frontier, (value, item))
        heapq.heappush(retained, (-value, ReverseID(item), item))
        evicted = heapq.heappop(retained)[2] if len(retained) > ef else None
        return evicted

    def worst():
        return -retained[0][0], retained[0][2]

    def snapshot(action, current=None, decisions=None):
        if capture:
            event = {"action": action, "current_id": current, "decisions": decisions or []}
            # Initial state + exact mutations reconstruct every subsequent queue.
            # Full snapshots are reserved for the hand trace; deltas avoid large logs.
            if capture == "full" or action == "initialize":
                event.update(frontier=[[i, d] for d, i in sorted(frontier)],
                    retained=[[i, -neg] for neg, _, i in
                              sorted(retained, key=lambda x: (-x[0], x[2]))])
            events.append(event)

    for item in sorted(set(entry_ids)):
        if item in blocked:
            continue
        if item not in vectors or item not in adjacency:
            raise ValueError("Invalid graph entry")
        visited.add(item)
        offer(item, distance(item))
    snapshot("initialize")
    reason = "frontier_exhausted"
    while frontier:
        value, current = heapq.heappop(frontier)
        if len(retained) >= ef and (value, current) > worst():
            reason = "frontier_bound"
            snapshot("stop_bound", current)
            break
        decisions = []
        for item in sorted(adjacency[current]):
            if item in blocked or item in visited:
                continue
            visited.add(item)
            d = distance(item)
            admitted = len(retained) < ef or (d, item) < worst()
            evicted = offer(item, d) if admitted else None
            decisions.append({"item_id": item, "squared_distance": d,
                              "admitted": admitted, "evicted_id": evicted})
        snapshot("expand", current, decisions)
    result = sorted(((item, -neg) for neg, _, item in retained),
                    key=lambda pair: (pair[1], pair[0]))
    return result, {"events": events, "scored_ids": scored,
                    "visited_ids": sorted(visited), "stop_reason": reason}


def select_neighbors(center, candidates, vectors, limit, *, keep_pruned=False):
    """Diversity heuristic: reject c if a selected s is closer to c than center.

    Squared distances preserve all comparisons; equal distances are accepted.
    No candidate-set extension. Optional refill is an explicit policy choice.
    """
    ordered = sorted(set(candidates), key=lambda i: (squared_l2(center, vectors[i]), i))
    selected, rejected = [], []
    for item in ordered:
        if len(selected) >= limit:
            break
        own = squared_l2(center, vectors[item])
        if all(squared_l2(vectors[item], vectors[s]) >= own for s in selected):
            selected.append(item)
        else:
            rejected.append(item)
    if keep_pruned:
        selected.extend(rejected[:max(0, limit-len(selected))])
    return selected


def canonical_digest(payload):
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"),
                                    allow_nan=False).encode()).hexdigest()


class HNSW:
    def __init__(self, rows=(), *, scope, M=4, ef_construction=32, seed=17022026,
                 source_version="teaching-v1", keep_pruned=False):
        if not isinstance(M, int) or isinstance(M, bool) or M < 2:
            raise ValueError("M must be an integer >= 2")
        if not isinstance(ef_construction, int) or ef_construction < M:
            raise ValueError("efConstruction must be >= M")
        self.scope, self.M, self.ef_construction = scope, M, ef_construction
        self.seed, self.source_version, self.keep_pruned = seed, source_version, keep_pruned
        self.rng = random.Random(seed)
        self.vectors, self.levels, self.layers = {}, {}, []
        self.deleted, self.entry_id, self.dimension = set(), None, None
        self.insertion_order, self.build_distance_evaluations = [], 0
        # Reject duplicate IDs even in excluded input; never index protected vectors.
        rows = list(rows)
        ids = [row["item_id"] for row in rows]
        if len(ids) != len(set(ids)):
            raise ValueError("Duplicate item ID")
        for row in rows:
            if scope in row["allowed_scopes"]:
                self.add(row)

    def add(self, row, *, level=None):
        if self.rng is None:
            raise ValueError("Restored teaching snapshot is query-only")
        if self.scope not in row["allowed_scopes"]:
            raise ValueError("Ineligible insertion")
        item = row["item_id"]
        if not isinstance(item, str) or not item or item in self.vectors:
            raise ValueError("Invalid or duplicate item ID")
        point = vector(row["vector"], self.dimension)
        if level is None:
            level = int(-math.log(1-self.rng.random()) / math.log(self.M))
        if not isinstance(level, int) or isinstance(level, bool) or level < 0:
            raise ValueError("Invalid level")
        old_top = len(self.layers)-1
        active = [i for i in self.vectors if i not in self.deleted] if self.deleted else None
        entry = self.entry_id
        if entry in self.deleted:
            entry = min(active, key=lambda i: (-self.levels[i], i)) if active else None
        cache, construction = {}, []
        entries = [entry] if entry else []
        if entry:
            # A deleted former top entry may leave the active starting level lower.
            for layer in range(self.levels[entry], level, -1):
                found, _ = search_layer(point, self.vectors, self.layers[layer], entries, 1,
                                         blocked=self.deleted, cache=cache, capture=False)
                entries = [found[0][0]]
        self.dimension = len(point)
        self.vectors[item], self.levels[item] = point, level
        self.insertion_order.append(item)
        while len(self.layers) <= level:
            self.layers.append({})
        for layer in range(level+1):
            self.layers[layer][item] = []
        if entry:
            for layer in range(min(level, self.levels[entry]), -1, -1):
                found, detail = search_layer(point, self.vectors, self.layers[layer], entries,
                    self.ef_construction, blocked=self.deleted, cache=cache, capture=False)
                candidates = [i for i, _ in found]
                chosen = select_neighbors(point, candidates, self.vectors, self.M,
                                          keep_pruned=self.keep_pruned)
                self.layers[layer][item] = chosen
                pruned = {}
                for neighbor in chosen:
                    links = self.layers[layer][neighbor]
                    if item not in links:
                        links.append(item)
                    capacity = 2*self.M if layer == 0 else self.M
                    if len(links) > capacity:
                        # Pruning one outgoing list need not remove the reverse edge.
                        self.layers[layer][neighbor] = select_neighbors(
                            self.vectors[neighbor], links, self.vectors, capacity,
                            keep_pruned=self.keep_pruned)
                        pruned[neighbor] = list(self.layers[layer][neighbor])
                construction.append({"layer": layer, "candidate_ids": candidates,
                                     "selected_ids": chosen, "pruned_adjacency": pruned,
                                     "scored_ids": detail["scored_ids"]})
                entries = candidates
        if self.entry_id is None or level > old_top or self.entry_id in self.deleted:
            self.entry_id = item if entry is None or level >= self.levels[entry] else entry
        self.build_distance_evaluations += len(cache)
        return {"item_id": item, "level": level, "layers": construction,
                "query_to_existing_distance_evaluations": len(cache)}

    def search(self, query, *, scope, k=2, ef_search=8, capture=True):
        if scope != self.scope:
            raise ValueError("Static roster scope mismatch; rebuild a trusted eligible graph")
        if not isinstance(k, int) or isinstance(k, bool) or k < 1:
            raise ValueError("k must be positive")
        if not isinstance(ef_search, int) or isinstance(ef_search, bool) or ef_search < k:
            raise ValueError("efSearch must be >= k")
        q = vector(query, self.dimension)
        entry = self.entry_id
        if entry in self.deleted:
            active = [i for i in self.vectors if i not in self.deleted]
            entry = min(active, key=lambda i: (-self.levels[i], i)) if active else None
        if entry is None:
            return [], {"reason": "no_eligible_vectors", "scored_vectors": 0,
                        "candidate_stages": {"scored": [], "base_retained": []},
                        "graph_trace": [], "stop_reason": "empty_graph"}
        cache, traces, stages = {}, [], {}
        for layer in range(self.levels[entry], -1, -1):
            found, detail = search_layer(q, self.vectors, self.layers[layer], [entry],
                1 if layer else ef_search, blocked=self.deleted, cache=cache, capture=capture)
            traces.append({"layer": layer, "entry_id": entry, **detail})
            stages[f"layer_{layer}_retained"] = [(i, -d) for i, d in found]
            entry = found[0][0]
        stages["scored"] = [(i, -d) for i, d in cache.items()]
        stages["base_retained"] = [(i, -d) for i, d in found]
        ranked = stages["base_retained"][:k]
        return ranked, {"scored_vectors": len(cache),
            "layer_distance_evaluations": sum(len(t["scored_ids"]) for t in traces),
            "expanded_vertices": sum(sum(e["action"] == "expand" for e in t["events"]) for t in traces),
            "candidate_stages": stages, "graph_trace": traces,
            "stop_reason": traces[-1]["stop_reason"], "score_kind": "negative_squared_l2"}

    def delete(self, item):
        if item not in self.vectors:
            raise ValueError("Unknown deletion ID")
        self.deleted.add(item)

    def payload_lower_bounds(self):
        arcs = sum(len(ns) for layer in self.layers for ns in layer.values())
        return {"directed_adjacency_entries": arcs, "vector_float32_bytes": len(self.vectors)*(self.dimension or 0)*4,
                "adjacency_uint32_bytes": arcs*4, "level_uint32_bytes": len(self.vectors)*4,
                "note": "Payload lower bounds only; excludes ID mappings, offsets, capacity, Python objects, replicas and trace buffers"}

    def snapshot(self):
        body = {"schema": "ch17-hnsw-1", "metric": "squared_l2/id-ascending",
                "scope": self.scope, "M": self.M, "ef_construction": self.ef_construction,
                "seed": self.seed, "source_version": self.source_version,
                "keep_pruned": self.keep_pruned, "vectors": self.vectors, "levels": self.levels,
                "layers": self.layers, "entry_id": self.entry_id, "deleted": sorted(self.deleted),
                "insertion_order": self.insertion_order}
        return {"body": body, "sha256": canonical_digest(body)}

    def save(self, path):
        Path(path).write_text(json.dumps(self.snapshot(), indent=2)+"\n", encoding="utf-8")

    @classmethod
    def load(cls, path, *, expected_source_version, expected_digest):
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        body = data["body"]
        if data["sha256"] != canonical_digest(body) or data["sha256"] != expected_digest:
            raise ValueError("Graph checksum/version mismatch")
        if body["schema"] != "ch17-hnsw-1" or body["metric"] != "squared_l2/id-ascending" or body["source_version"] != expected_source_version:
            raise ValueError("Graph source/metric/schema mismatch")
        obj = cls(scope=body["scope"], M=body["M"], ef_construction=body["ef_construction"],
                  seed=body["seed"], source_version=body["source_version"], keep_pruned=body["keep_pruned"])
        for item in body["insertion_order"]:
            obj.add({"item_id": item, "vector": body["vectors"][item], "allowed_scopes": [obj.scope]}, level=body["levels"][item])
        obj.layers, obj.entry_id, obj.deleted = body["layers"], body["entry_id"], set(body["deleted"])
        obj.validate_structure()
        # Restored snapshots are query-only in this chapter; RNG continuation is not persisted.
        obj.rng = None
        return obj

    def validate_structure(self):
        if self.entry_id is not None and self.entry_id not in self.vectors:
            raise ValueError("Invalid graph entry")
        if not self.deleted <= self.vectors.keys():
            raise ValueError("Invalid tombstone")
        for layer, graph in enumerate(self.layers):
            if set(graph) != {i for i, level in self.levels.items() if level >= layer}:
                raise ValueError("Non-nested graph layers")
            for item, links in graph.items():
                if len(links) > (2*self.M if layer == 0 else self.M) or len(links) != len(set(links)):
                    raise ValueError("Invalid graph degree")
                if item in links or not set(links) <= graph.keys():
                    raise ValueError("Invalid graph edge")
