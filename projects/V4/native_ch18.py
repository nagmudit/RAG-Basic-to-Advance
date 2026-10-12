"""Pinned Faiss candidate-index adapter, not a database or serving API.

The native returned shortlist is observable; internal scored IDs/frontiers are
not exposed by this binding. The inspectable Chapter17 route remains available.
"""
from __future__ import annotations
import hashlib
import json
from contextlib import contextmanager
from pathlib import Path
from threading import RLock
from time import perf_counter_ns

import faiss
import numpy as np

FAISS_VERSION = "1.13.2"
NUMPY_VERSION = "2.4.2"
LOCK = RLock()


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                    allow_nan=False).encode()).hexdigest()


def array_digest(matrix):
    return hashlib.sha256(np.asarray(matrix, dtype="<f4").tobytes(order="C")).hexdigest()


@contextmanager
def single_thread():
    """Global OpenMP setting, suitable only for this isolated serial experiment."""
    with LOCK:
        previous = faiss.omp_get_max_threads()
        faiss.omp_set_num_threads(1)
        try:
            yield
        finally:
            faiss.omp_set_num_threads(previous)


def checked_query(values, dimension):
    with np.errstate(over="ignore", invalid="ignore"):
        q = np.asarray(values, dtype=np.float32)
    if q.shape != (dimension,) or not np.all(np.isfinite(q)):
        raise ValueError("Invalid float32 query vector")
    return np.ascontiguousarray(q.reshape(1, dimension))


def oracle(rows, query, *, k=2):
    """Independent exhaustive float64 accumulation over float32 stored inputs."""
    q = checked_query(query, len(query))[0].astype(np.float64)
    if not isinstance(k, int) or isinstance(k, bool) or k < 1:
        raise ValueError("Invalid oracle cutoff")
    if any(len(r["vector"]) != len(q) or not np.all(np.isfinite(np.asarray(r["vector"],dtype=np.float32))) for r in rows):
        raise ValueError("Invalid oracle vectors")
    ranked = [(r["item_id"], -sum((float(np.float32(x))-float(y))**2
               for x, y in zip(r["vector"], q))) for r in rows]
    return sorted(ranked, key=lambda p: (-p[1], p[0]))[:k]


class NativeIndex:
    def __init__(self, rows, *, dimension, scope, kind="flat", M=8,
                 ef_construction=64, seed=18012026, source_version, model_version=None):
        if kind not in ("flat", "hnsw") or dimension < 1 or M < 2 or ef_construction < M:
            raise ValueError("Invalid index configuration")
        self.scope, self.kind, self.dimension = scope, kind, dimension
        self.M, self.ef_construction, self.seed = M, ef_construction, seed
        self.source_version, self.model_version = source_version, model_version
        rows = list(rows)
        ids = [r["item_id"] for r in rows]
        if len(ids) != len(set(ids)) or any(not isinstance(i, str) or not i for i in ids):
            raise ValueError("Invalid/duplicate item ID")
        # Hard eligibility boundary: excluded vectors are never converted/indexed.
        self.rows = sorted((r for r in rows if scope in r["allowed_scopes"]), key=lambda r: r["item_id"])
        self.ids = [r["item_id"] for r in self.rows]
        with np.errstate(over="ignore", invalid="ignore"):
            self.matrix = np.asarray([r["vector"] for r in self.rows], dtype=np.float32).reshape(len(self.rows), -1) if self.rows else np.empty((0, dimension), dtype=np.float32)
        if self.matrix.shape != (len(self.rows), dimension) or not np.all(np.isfinite(self.matrix)):
            raise ValueError("Invalid float32 indexed vectors")
        self.matrix = np.ascontiguousarray(self.matrix)
        self.matrix.flags.writeable = False
        self.roster_digest = digest({"scope": scope, "ids": self.ids,
            "matrix_float32_sha256": array_digest(self.matrix),
            "scopes": [sorted(r["allowed_scopes"]) for r in self.rows]})
        if kind == "flat":
            self.index = faiss.IndexFlatL2(dimension)
        else:
            self.index = faiss.IndexHNSWFlat(dimension, M, faiss.METRIC_L2)
            self.index.hnsw.efConstruction = ef_construction
            self.index.hnsw.rng = faiss.RandomGenerator(seed)
        tick = perf_counter_ns()
        self.index.add(self.matrix)
        self.build_ms = (perf_counter_ns()-tick)/1e6
        # No centroid/codebook training phase for either of these full-vector indexes.
        self.payload = faiss.serialize_index(self.index).tobytes()
        self.index_digest = hashlib.sha256(self.payload).hexdigest()

    def search(self, query, *, scope, k=2, depth=8, ef_search=32, public_predicate=None):
        if scope != self.scope:
            raise ValueError("Static authorized roster mismatch")
        if not isinstance(k, int) or k < 1 or not isinstance(depth, int) or depth < k:
            raise ValueError("Invalid k/shortlist depth")
        if self.kind == "hnsw" and ef_search < depth:
            raise ValueError("efSearch must cover requested native shortlist depth")
        if faiss.omp_get_max_threads() != 1:
            raise ValueError("Teaching native counters require serial one-thread mode")
        tick = perf_counter_ns()
        q = checked_query(query, self.dimension)
        convert_ms = (perf_counter_ns()-tick)/1e6
        if not self.ids:
            return [], {"candidate_stages": {"scored": [], "native_returned": [], "metadata_survivors": [], "exact_refinement_pool": []},
                        "reason": "no_eligible_vectors", "stage_timings_ms": {"query_conversion": convert_ms, "native_search": 0., "shortlist_refinement": 0.},
                        "native_frontier": None, "raw_pool_semantics": "native_returned_shortlist_only"}
        with LOCK:
            if self.kind == "hnsw":
                self.index.hnsw.efSearch = ef_search
                faiss.cvar.hnsw_stats.reset()
            tick = perf_counter_ns()
            distances, ordinals = self.index.search(q, min(depth, len(self.ids)))
            native_ms = (perf_counter_ns()-tick)/1e6
            stats = ({"distance_evaluations": int(faiss.cvar.hnsw_stats.ndis),
                      "hops": int(faiss.cvar.hnsw_stats.nhops)} if self.kind == "hnsw" else
                     {"distance_evaluations": len(self.ids), "hops": None})
        raw = [(self.ids[int(i)], -float(d)) for i, d in zip(ordinals[0], distances[0]) if i >= 0]
        if len(raw) != len(ordinals[0]) or any(not np.isfinite(score) for _, score in raw):
            raise ValueError("Invalid native result")
        # Predicate is a public, nonsecurity tag in the demonstration, never an ACL.
        survivors = [(i, score) for i, score in raw if public_predicate is None or public_predicate(i)]
        tick = perf_counter_ns()
        ordinal_by_id = {i: int(o) for i, o in zip((i for i, _ in raw), ordinals[0])}
        scored = []
        q64 = q[0].astype(np.float64)
        for item, _ in survivors:
            difference = self.matrix[ordinal_by_id[item]].astype(np.float64)-q64
            scored.append((item, -float(np.dot(difference, difference))))
        ranked = sorted(scored, key=lambda p: (-p[1], p[0]))[:k]
        refinement_ms = (perf_counter_ns()-tick)/1e6
        return ranked, {"candidate_stages": {"scored": raw, "native_returned": raw,
            "metadata_survivors": survivors, "exact_refinement_pool": scored},
            "stage_timings_ms": {"query_conversion": convert_ms, "native_search": native_ms,
                                 "shortlist_refinement": refinement_ms},
            "native_frontier": None, "native_scored_ids": None,
            "raw_pool_semantics": "native_returned_shortlist_only",
            "internal_trace_availability": "not_exposed_by_faiss_python_binding",
            "native_work": stats, "requested_depth": depth, "actual_depth": len(raw),
            "efSearch": ef_search if self.kind == "hnsw" else None,
            "underfilled": len(ranked) < min(k, len(self.ids)),
            "reason": "no_metadata_survivor_in_shortlist" if not ranked else None,
            "score_kind": "negative_squared_l2; native=float32, refinement=float64 over float32 inputs"}

    def batch_kernel(self, queries, *, depth=8, ef_search=32):
        """One matrix call; no per-query latency, filtering, refinement or context."""
        if not queries or depth < 1 or (self.kind == "hnsw" and ef_search < depth) or not self.ids or faiss.omp_get_max_threads() != 1:
            raise ValueError("Invalid controlled batch call")
        matrix = np.concatenate([checked_query(q, self.dimension) for q in queries])
        with LOCK:
            if self.kind == "hnsw":
                self.index.hnsw.efSearch = ef_search
            tick = perf_counter_ns()
            distances, ordinals = self.index.search(matrix, min(depth, len(self.ids)))
            elapsed = (perf_counter_ns()-tick)/1e6
        return {"native_batch_ms": elapsed,
            "queries_per_second": len(queries)/(elapsed/1000),
            "candidate_ids_by_query": [[self.ids[int(i)] for i in row if i >= 0] for row in ordinals],
            "candidate_scores_by_query": [[-float(x) for x in row] for row in distances]}

    def save(self, directory):
        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)
        (directory/"index.faiss").write_bytes(self.payload)
        manifest = {"schema": "ch18-faiss-snapshot-1", "faiss_version": faiss.__version__,
            "kind": self.kind, "dimension": self.dimension, "scope": self.scope,
            "source_version": self.source_version, "model_version": self.model_version,
            "M": self.M, "efConstruction": self.ef_construction, "seed": self.seed,
            "row_ids": self.ids, "roster_digest": self.roster_digest,
            "matrix_float32_sha256": array_digest(self.matrix), "metric": "squared_l2",
            "payload_sha256": self.index_digest, "payload_bytes": len(self.payload),
            "query_settings": "efSearch and shortlist depth supplied explicitly at each query"}
        (directory/"manifest.json").write_text(json.dumps(manifest, indent=2)+"\n", encoding="utf-8")
        return {"manifest_sha256": digest(manifest), "payload_bytes": len(self.payload),
                "manifest_file_bytes": (directory/"manifest.json").stat().st_size}

    @classmethod
    def load(cls, directory, rows, *, expected_manifest_digest, scope,
             expected_source_version, expected_model_version):
        directory = Path(directory)
        manifest = json.loads((directory/"manifest.json").read_text(encoding="utf-8"))
        if digest(manifest) != expected_manifest_digest or manifest["scope"] != scope or manifest["source_version"] != expected_source_version or manifest["model_version"] != expected_model_version:
            raise ValueError("Trusted snapshot identity mismatch")
        if manifest["faiss_version"] != faiss.__version__ or manifest["metric"] != "squared_l2" or manifest["schema"] != "ch18-faiss-snapshot-1":
            raise ValueError("Native snapshot software/metric mismatch")
        obj = cls.__new__(cls)
        obj.rows = sorted((r for r in rows if scope in r["allowed_scopes"]), key=lambda r: r["item_id"])
        obj.ids = [r["item_id"] for r in obj.rows]
        obj.scope, obj.dimension, obj.kind = scope, manifest["dimension"], manifest["kind"]
        obj.matrix = np.asarray([r["vector"] for r in obj.rows], dtype=np.float32).reshape(len(obj.rows), obj.dimension)
        roster = digest({"scope": scope, "ids": obj.ids, "matrix_float32_sha256": array_digest(obj.matrix),
                         "scopes": [sorted(r["allowed_scopes"]) for r in obj.rows]})
        if roster != manifest["roster_digest"] or obj.ids != manifest["row_ids"] or array_digest(obj.matrix) != manifest["matrix_float32_sha256"]:
            raise ValueError("Changed source vectors/eligibility/ID mapping")
        payload = (directory/"index.faiss").read_bytes()
        if hashlib.sha256(payload).hexdigest() != manifest["payload_sha256"] or len(payload) != manifest["payload_bytes"]:
            raise ValueError("Native payload checksum mismatch")
        # Only deserialize after independent trusted metadata/payload checks.
        obj.index = faiss.deserialize_index(np.frombuffer(payload, dtype=np.uint8).copy())
        if obj.index.ntotal != len(obj.ids) or obj.index.d != obj.dimension:
            raise ValueError("Native index shape mismatch")
        obj.matrix.flags.writeable = False
        obj.M, obj.ef_construction, obj.seed = manifest["M"], manifest["efConstruction"], manifest["seed"]
        obj.source_version, obj.model_version = expected_source_version, expected_model_version
        obj.roster_digest, obj.index_digest, obj.payload, obj.build_ms = roster, manifest["payload_sha256"], payload, None
        return obj
