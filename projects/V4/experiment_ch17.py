"""Registered, matched graph ANN experiment; preserve historical result files."""
from __future__ import annotations
import argparse
import hashlib
import json
import platform
import random
import statistics
import sys
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter_ns

HERE = Path(__file__).resolve().parent
for name in ("common", "V1", "V2", "V3"):
    sys.path.insert(0, str(HERE.parent / name))
from experiment_trace import TraceCollector, versions, eligible, context_ids
from lexical_index import build_index, load_corpus
from eval_ch09 import evaluate_ranking, summarize, nearest_rank
from dense_snapshot import load_snapshot
from experiment_ch11 import embed, load_encoder, sha256
from experiment_ch13 import QRELS, load_stress_qrels
from experiment_ch15 import synthetic_rows, rank_recall, source_hash
from ann_ch15 import exact_cosine
from ivf_pq_ch16 import IVFPQ
from hnsw_ch17 import HNSW, squared_l2, search_layer, canonical_digest

SEED = 17022026
K = 2
M_GRID = (2, 4, 8)
EF_GRID = (2, 8, 24)


def timing(values):
    return {"unit": "ms", "sample_count": len(values), "samples": values,
            "p50_nearest_rank": nearest_rank(values, .5),
            "p95_nearest_rank": nearest_rank(values, .95)}


def exact_l2(rows, query):
    scored = [(r["item_id"], -squared_l2(query, r["vector"])) for r in rows]
    return sorted(scored, key=lambda p: (-p[1], p[0]))[:K], {
        "scored_vectors": len(rows), "candidate_stages": {"scored": scored},
        "score_kind": "negative_squared_l2"}


def traced(trace, qid, mode, trial, operation, context_source=None):
    result, record = trace.execute(qid, mode, trial, operation, context_selector=context_source)
    work = result[1]
    record["graph_trace"] = work.get("graph_trace")
    record["graph_stop_reason"] = work.get("stop_reason")
    record["scored_vectors"] = work.get("scored_vectors", work.get("eligible_scored"))
    record["score_kind"] = work.get("score_kind", "negative_squared_l2")
    return result, record


def compare(rows, queries, trace, *, scope, nlist, source_version, qrels=None, base=None):
    graphs, builds = {}, {}
    # One construction ablation at fixed M; all other graphs use efConstruction=32.
    for M, efc in [(m, 32) for m in M_GRID] + [(4, 8)]:
        name = f"m{M}_c{efc}"
        tick = perf_counter_ns()
        graphs[name] = HNSW(rows, scope=scope, M=M, ef_construction=efc,
                             seed=SEED, source_version=source_version)
        builds[name] = {"build_ms": (perf_counter_ns()-tick)/1e6,
            "graph_sha256": graphs[name].snapshot()["sha256"],
            "entry_id": graphs[name].entry_id,
            "levels": graphs[name].levels, "adjacency_by_layer": graphs[name].layers,
            "level_population": [len(layer) for layer in graphs[name].layers],
            "payload_lower_bounds": graphs[name].payload_lower_bounds(),
            "query_to_existing_build_distance_evaluations": graphs[name].build_distance_evaluations,
            "M": M, "efConstruction": efc}
    tick = perf_counter_ns()
    ivf = IVFPQ(rows, nlist=nlist, subspaces=1, bits=2, seed=SEED,
               training_ids=[r["item_id"] for r in rows][:min(256, len(rows))],
               source_version=source_version)
    ivf_build = (perf_counter_ns()-tick)/1e6
    configs = {f"{name}_e{ef}": {"M": graph.M, "efConstruction": graph.ef_construction,
                 "efSearch": ef, "graph": name} for name, graph in graphs.items()
               for ef in (EF_GRID if name != "m4_c8" else (24,))}
    modes = ["exact", "ivf_flat_p1", f"ivf_flat_p{nlist}", *configs]
    identities = {"exact": source_version+"/exact-l2",
                  "ivf_flat_p1": source_version+"/fresh-ivf-flat-seed-"+str(SEED),
                  f"ivf_flat_p{nlist}": source_version+"/fresh-ivf-flat-seed-"+str(SEED)}
    identities.update({name: builds[cfg["graph"]]["graph_sha256"] for name, cfg in configs.items()})
    trace.versions["index_version"] = identities
    samples = {name: [] for name in modes}
    cases, rng = [], random.Random(SEED+1)
    context_source = (lambda result: context_ids(base, result)) if base else None
    for qid, query in queries.items():
        methods = {"exact": lambda: exact_l2(rows, query),
                   "ivf_flat_p1": lambda: ivf.search(query, scope=scope, k=K, nprobe=1, mode="flat"),
                   f"ivf_flat_p{nlist}": lambda: ivf.search(query, scope=scope, k=K, nprobe=nlist, mode="flat")}
        for name, cfg in configs.items():
            methods[name] = lambda cfg=cfg: graphs[cfg["graph"]].search(
                query, scope=scope, k=K, ef_search=cfg["efSearch"])
        exact_ids = [i for i, _ in exact_l2(rows, query)[0]]
        cosine_ids = [i for i, _ in exact_cosine(rows, query, scope=scope, k=K)[0]]
        if cosine_ids != exact_ids:
            raise AssertionError("Unit-vector L2/cosine oracle ordering mismatch")
        case = {"query_id": qid, "oracle_ids": exact_ids, "modes": {}}
        for name, op in methods.items():
            result, rec = traced(trace, qid, name, "quality", op, context_source)
            ranked, work = result
            ids = [i for i, _ in ranked]
            value = {"candidate_ids": ids, "candidate_scores": [s for _, s in ranked],
                     "exact_neighbor_recall_at_2": rank_recall(ids, exact_ids),
                     "scored_vectors": work.get("scored_vectors", work.get("eligible_scored")),
                     "request_id": rec["request_id"], "context_ids": rec["context_ids"],
                     "answer_correctness": None, "faithfulness": None,
                     "citation_support": None, "abstention": None}
            if qrels:
                value["ranking_metrics"] = evaluate_ranking(ids, qrels[qid]["grades"], K)
                value["slice"] = qrels[qid]["slice"]
            case["modes"][name] = value
        if case["modes"][f"ivf_flat_p{nlist}"]["candidate_ids"] != exact_ids:
            raise AssertionError("Full-probe Flat must match exact")
        # Quality calls also warm every method. No sample is used for selection.
        for trial in range(2):
            for name in rng.sample(modes, len(modes)):
                _, rec = traced(trace, qid, name, trial, methods[name], context_source)
                samples[name].append(rec["stage_timings_ms"]["search"])
        cases.append(case)
    summaries = {}
    for name in modes:
        values = [case["modes"][name] for case in cases]
        summaries[name] = {"workload_id": trace.workload_id,
            "mean_exact_neighbor_recall_at_2": statistics.mean(v["exact_neighbor_recall_at_2"] for v in values),
            "mean_scored_vectors": statistics.mean(v["scored_vectors"] for v in values),
            "search_only_timing": timing(samples[name])}
        if qrels:
            summaries[name]["qrel"] = summarize([v["ranking_metrics"] for v in values])
    return {"workload_id": trace.workload_id, "versions": trace.versions,
            "row_count": len(rows), "dimension": len(rows[0]["vector"]),
            "query_count": len(queries), "k": K, "scope": scope,
            "vector_rows_sha256": canonical_digest(rows),
            "query_vectors_sha256": canonical_digest(queries),
            "insertion_order_sha256": canonical_digest([r["item_id"] for r in rows]),
            "configuration": configs, "graphs": builds,
            "ivf_control": {"nlist": nlist, "build_including_unused_pq_ms": ivf_build,
                "note": "Fresh coarse training; only Flat searched. Not the Chapter 16 trained graph/codebook. PQ construction overhead included in this control build."},
            "summaries": summaries, "cases": cases, "request_samples": trace.records}


def synthetic_case(n, dimension, nlist):
    # EXACT prior bytes, including the coordinate-wise row selection in the generator.
    seed = 16012026+n+dimension
    rows, vectors = synthetic_rows(n, dimension, seed)
    queries = {f"synth-{i:02d}": q for i, q in enumerate(vectors[:16])}
    trace = TraceCollector(f"ch16-synthetic-n{n}-d{dimension}-v1",
        versions(f"synth-{seed}", "planted-16-v1", "geometric-exact-top2", None, None),
        [r["item_id"] for r in rows])
    return {"n": n, "seed": seed,
        "distribution": "Gaussian unit document vectors; each query coordinate independently selects a stored row, adds Gaussian noise sigma=.08, then the assembled query is normalized. Legacy planted-16-v1 is an identifier, not a claim of one planted neighbor.",
        **compare(rows, queries, trace, scope="benchmark", nlist=nlist, source_version=f"synth-{seed}")}


def v0_case(allow_download):
    base = build_index(load_corpus())
    data, questions = load_stress_qrels(base)  # validates content-bound judgments
    manifest, dense = load_snapshot(base, HERE.parent / "V3" / "index_ch13")
    rows = [{"item_id": e.item_id, "vector": e.unit_vector, "allowed_scopes": list(e.allowed_scopes)}
            for e in dense.entries if "support-team" in e.allowed_scopes]
    tick = perf_counter_ns()
    model, model_info = load_encoder(allow_download=allow_download)
    load_ms = (perf_counter_ns()-tick)/1e6
    trace = TraceCollector("ch13-stress-probes-v1", versions(base.snapshot, data["version"], data["version"],
        manifest["index_version"], model_info["model_revision"]), eligible(base))
    queries, encode_samples = {}, []
    for qid, item in questions.items():
        with trace.guard(qid, "query_encode", 0):
            tick = perf_counter_ns()
            queries[qid] = embed(model, [item["question"]], batch_size=1)[0]
            elapsed = (perf_counter_ns()-tick)/1e6
            encode_samples.append(elapsed)
            trace.record(qid, "query_encode", 0, ([], {}), {"query_encode": elapsed},
                         status="ok", reason="candidate_search_not_run")
    result = compare(rows, queries, trace, scope="support-team", nlist=3,
                     source_version=manifest["index_version"], qrels=questions, base=base)
    result.update(model=model_info, model_load_ms=load_ms, query_encode_timing=timing(encode_samples),
        corpus_sha256=sha256(HERE.parent / "V0" / "corpus.json"), qrels_sha256=sha256(QRELS),
        evidence_manifest_sha256=data["evidence_identity"]["manifest_sha256"],
        question_count=len(questions), judged_pairs=len(questions)*len(rows), index_manifest=manifest,
        split_semantics="Already authored and inspected diagnostic questions. No train/dev/test or generalization claim.")
    return result


def hand_case():
    f = json.loads((HERE / "graph_fixture_ch17.json").read_text(encoding="utf-8"))
    trace = TraceCollector(f["workload_id"], versions(f["corpus_version"], f["query_set_version"],
        f["qrels_version"], canonical_digest(f), None), f["vectors"])
    for ef in f["ef_grid"]:
        def operation():
            ranked, detail = search_layer(f["query"], f["vectors"], f["adjacency"], f["entry_ids"], ef, capture="full")
            scored = [(i, -squared_l2(f["query"], f["vectors"][i])) for i in detail["scored_ids"]]
            return [(i, -d) for i, d in ranked[:f["k"]]], {
                "candidate_stages": {"scored": scored, "base_retained": [(i, -d) for i, d in ranked]},
                "graph_trace": [{"layer": 0, **detail}], "stop_reason": detail["stop_reason"],
                "scored_vectors": len(scored), "score_kind": "negative_squared_l2"}
        traced(trace, f["query_id"], f"ef{ef}", "hand", operation)
    return {"workload_id": f["workload_id"], "fixture": f, "request_samples": trace.records}


def run(allow_download=False):
    started = datetime.now(timezone.utc).isoformat()
    result = {"experiment_id": "ch17-v4-hnsw-v1", "date": "2026-10-02",
        "question": "Can bounded graph exploration recover exact neighbors while reducing distance work, and what do hierarchy and graph quality cost?",
        "hypothesis": "Larger efSearch often improves geometric recall at additional search work; larger M/efConstruction change graph quality at construction/memory cost. No monotonic or deployment gain is assumed.",
        "seed": SEED, "baseline": "Same-vector exhaustive squared L2; ordered top-two parity checked against exact cosine. Fresh one/all-probe IVF-Flat controls.",
        "controls": ["Frozen rows, query vectors, scope, top-k=2, metric and ID ties within each workload", "Fixed insertion order and random seed per construction", "Fixed graph when varying efSearch", "M changes level distribution as well as degree; this is a joint configuration effect", "efConstruction=8 versus32 at M=4 uses identical levels"],
        "procedure": "Build four graphs per corpus. Quality/warm call per query/mode followed by two randomized-order timed calls. Search includes queue/trace construction, excludes envelope/context serialization, model load and query encoding. All actual lossy stages and frontier deltas retained.",
        "acceptance_gate": "Full-probe Flat equals exhaustive top two; no ineligible vertex scored; frontier replay matches retained IDs. Keep exact/BM25 until independent judged scale and a service budget support replacement.",
        "uncertainty": "No confidence intervals: 16 synthetic or14 inspected queries, one insertion order/seed, one local Python process, two dependent timing repeats/query. p95 is descriptive, not an availability/SLO estimate.",
        "limitations": ["No production library, filter service, compression, concurrency, distributed serving or RSS benchmark", "Synthetic oracle memberships are geometric, not relevance judgments", "V0 judgments inspected previously; no held-out or multilingual generalization", "Graph trace allocations are included in search; fresh timings cannot be compared directly with uninstrumented historical runs", "Construction distance counter excludes candidate-to-candidate diversity work; build wall time includes it"],
        "environment": {"python": platform.python_version(), "platform": platform.platform()},
        "code_sha256": {name: source_hash(HERE/name) for name in ("hnsw_ch17.py", "experiment_ch17.py", "experiment_ch15.py", "ivf_pq_ch16.py")},
        "hand": hand_case(), "synthetic": [synthetic_case(256, 8, 8), synthetic_case(1024, 32, 16)],
        "v0_diagnostic": v0_case(allow_download)}
    result["measurement_window_utc"] = {"start": started, "end": datetime.now(timezone.utc).isoformat()}
    result["decision"] = "Retain exact dense and BM25. Treat graph ANN as a candidate-index experiment, not a replacement retriever or evidence/answer improvement."
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=HERE/"chapter-17-experiment-local.json")
    parser.add_argument("--allow-download", action="store_true")
    args = parser.parse_args()
    result = run(args.allow_download)
    # Compact JSON retains every sample/frontier mutation without whitespace bloat.
    args.output.write_text(json.dumps(result, separators=(",", ":"), allow_nan=False)+"\n", encoding="utf-8")
    print(f"Wrote {args.output}; {result['decision']}")
