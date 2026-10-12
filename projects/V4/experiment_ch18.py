"""Matched native indexes, public-tag filtering foil and Part IV evidence card."""
from __future__ import annotations
import argparse
import json
import platform
import random
import statistics
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter_ns

HERE = Path(__file__).resolve().parent
for name in ("common", "V1", "V2", "V3"):
    sys.path.insert(0, str(HERE.parent/name))
from experiment_trace import TraceCollector, versions, context_ids
from lexical_index import load_corpus, build_index
from eval_ch09 import evaluate_ranking, summarize, nearest_rank
from dense_snapshot import load_snapshot
from experiment_ch11 import embed, load_encoder, sha256
from experiment_ch13 import QRELS, load_stress_qrels
from experiment_ch15 import synthetic_rows, rank_recall, source_hash
from hnsw_ch17 import HNSW
from native_ch18 import NativeIndex, FAISS_VERSION, NUMPY_VERSION, single_thread, oracle, digest
from storage_ch18 import read_beam
import faiss
import numpy as np

SEED = 18012026
K, DEPTH, TRIALS = 2, 8, 5


def timing(values):
    return {"unit": "ms", "sample_count": len(values), "samples": values,
            "p50_nearest_rank": nearest_rank(values, .5), "p95_nearest_rank": nearest_rank(values, .95)}


def call(trace, qid, mode, trial, op, base=None):
    result, rec = trace.execute(qid, mode, trial, op,
        context_selector=(lambda r: context_ids(base, r)) if base else None)
    work = result[1]
    rec["stage_timings_ms"].update(work.get("stage_timings_ms", {}))
    rec["raw_pool_semantics"] = work.get("raw_pool_semantics", "actually_scored_vectors")
    rec["internal_trace_availability"] = work.get("internal_trace_availability", "inspectable_reference")
    rec["native_frontier"] = work.get("native_frontier")
    rec["native_work"] = work.get("native_work")
    if "graph_trace" in work:
        rec["graph_trace"] = work["graph_trace"]
    rec["score_kind"] = work.get("score_kind", "negative_squared_l2")
    return result, rec


def benchmark(rows, queries, trace, *, dimension, scope, source_version, model_version=None, qrels=None,
              base=None, artifact_dir):
    flat = NativeIndex(rows, dimension=dimension, scope=scope, source_version=source_version,
                       model_version=model_version)
    graph = NativeIndex(rows, dimension=dimension, scope=scope, kind="hnsw", M=8,
                        ef_construction=64, seed=SEED, source_version=source_version, model_version=model_version)
    builds = {}
    for name, index in (("flat", flat), ("hnsw", graph)):
        metadata = index.save(artifact_dir/name)
        tick = perf_counter_ns()
        restored = NativeIndex.load(artifact_dir/name, rows, expected_manifest_digest=metadata["manifest_sha256"],
                    scope=scope, expected_source_version=source_version, expected_model_version=model_version)
        load_ms = (perf_counter_ns()-tick)/1e6
        builds[name] = {"add_build_ms": index.build_ms, "training_ms": None,
            "training_semantics": "No centroid/codebook training for Flat or HNSWFlat",
            "serialized_native_bytes": len(index.payload), "id_manifest_bytes": metadata["manifest_file_bytes"],
            "float32_vector_payload_bytes": len(index.ids)*dimension*4,
            "trusted_manifest_sha256": metadata["manifest_sha256"], "native_index_sha256": index.index_digest,
            "checked_reload_ms": load_ms, "ntotal": index.index.ntotal,
            "scope": scope, "roster_digest": index.roster_digest,
            "reload_note": "Includes roster digest validation and native deserialize; no service startup/network/cache measurement"}
        first_q = next(iter(queries.values()))
        if index.search(first_q, scope=scope)[0] != restored.search(first_q, scope=scope)[0]:
            raise AssertionError("Checked native snapshot changed ranking")
    modes = ["flat_r8", "hnsw_e8_r8", "hnsw_e32_r8", "hnsw_e64_r8"]
    trace.versions["index_version"] = {name: flat.index_digest if name.startswith("flat") else graph.index_digest for name in modes}
    rng = random.Random(SEED)
    cases, times = [], {name: {"search": [], "native_search": []} for name in modes}
    for qid, query in queries.items():
        methods = {"flat_r8": lambda: flat.search(query, scope=scope, depth=DEPTH),
            **{f"hnsw_e{ef}_r8": (lambda ef=ef: graph.search(query, scope=scope, depth=DEPTH, ef_search=ef))
               for ef in (8,32,64)}}
        expected = [i for i, _ in oracle(flat.rows, query, k=K)]
        case = {"query_id": qid, "oracle_ids": expected, "modes": {}}
        for name, op in methods.items():
            result, rec = call(trace, qid, name, "quality", op, base)
            ids = [i for i, _ in result[0]]
            value = {"candidate_ids": ids, "candidate_scores": [s for _, s in result[0]],
                "exact_neighbor_recall_at_2": rank_recall(ids, expected), "request_id": rec["request_id"],
                "context_ids": rec["context_ids"], "native_work": rec["native_work"],
                "answer_correctness": None, "faithfulness": None, "citation_support": None, "abstention": None}
            if qrels:
                value["ranking_metrics"] = evaluate_ranking(ids, qrels[qid]["grades"], K)
                value["slice"] = qrels[qid]["slice"]
            case["modes"][name] = value
        if case["modes"]["flat_r8"]["candidate_ids"] != expected:
            raise AssertionError("Native Flat/float64-accumulated oracle ordering mismatch")
        for trial in range(TRIALS):
            for name in rng.sample(modes, len(modes)):
                _, rec = call(trace, qid, name, trial, methods[name], base)
                for stage in times[name]:
                    times[name][stage].append(rec["stage_timings_ms"][stage])
        cases.append(case)
    summaries = {}
    for name in modes:
        values = [case["modes"][name] for case in cases]
        summaries[name] = {"workload_id": trace.workload_id,
            "mean_exact_neighbor_recall_at_2": statistics.mean(v["exact_neighbor_recall_at_2"] for v in values),
            "adapter_search_timing": timing(times[name]["search"]),
            "native_kernel_timing": timing(times[name]["native_search"]),
            "mean_distance_evaluations": statistics.mean(v["native_work"]["distance_evaluations"] for v in values)}
        if qrels:
            summaries[name]["qrel"] = summarize([v["ranking_metrics"] for v in values])
    batch = []
    for name, index in (("flat_batch_r8", flat), ("hnsw_batch_e32_r8", graph)):
        index.batch_kernel(list(queries.values()))  # excluded warmup
        for trial in range(TRIALS):
            with trace.guard("batch:"+digest(list(queries))[:12], name, trial):
                result = index.batch_kernel(list(queries.values()))
                rec = trace.record("batch:"+digest(list(queries))[:12], name, trial, ([], {}),
                    {"native_batch": result["native_batch_ms"]}, status="ok", reason="per_query_outputs_in_batch_fields")
                rec["index_version"] = index.index_digest
                rec["raw_pool_semantics"] = "batch_has_no_single_ranked_candidate_list"
                rec["batch_query_ids"] = list(queries)
                rec.update(result)
                batch.append({"workload_id": trace.workload_id, "mode": name, "trial_id": trial,
                              "query_count": len(queries), "request_id": rec["request_id"], **result})
    # Preserve actual full-frontier observability on a separate reference route.
    # This is NOT represented as the native search's internal execution.
    reference = HNSW(rows, scope=scope, M=4, ef_construction=32, seed=17022026, source_version=source_version)
    trace.versions["index_version"]["inspectable_reference_e24"] = reference.snapshot()["sha256"]
    for qid, query in queries.items():
        _, rec = call(trace, qid, "inspectable_reference_e24", "diagnostic", lambda: reference.search(query, scope=scope, k=K, ef_search=24), base)
        rec["reference_warning"] = "Independent teaching graph; not the native Faiss frontier"
    return {"workload_id": trace.workload_id, "versions": trace.versions,
        "row_count": len(flat.ids), "dimension": dimension, "query_count": len(queries), "k": K,
        "native_shortlist_depth": DEPTH, "query_vectors_sha256": digest(queries),
        "float32_query_vectors_sha256": digest({i: np.asarray(q,dtype=np.float32).tolist() for i,q in queries.items()}),
        "insertion_order": flat.ids, "builds": builds, "summaries": summaries, "cases": cases,
        "batch_samples": batch, "request_samples": trace.records,
        "precision_policy": "Native float32 squared L2; rerank returned pool with float64 accumulation over float32 inputs; stable ID ties only inside pool. No globally tied shortlist boundary occurs in frozen probes."}


def filtered_case(rows, queries, stride):
    selected = [r for r in rows if int(r["item_id"][1:]) % stride == 0]
    predicate = lambda item: int(item[1:]) % stride == 0
    scope, source = "benchmark", "ch18-tagged-synth-16013082-v1"
    flat = NativeIndex(rows, dimension=32, scope=scope, source_version=source)
    graph = NativeIndex(rows, dimension=32, scope=scope, kind="hnsw", seed=SEED, source_version=source)
    pre = NativeIndex(selected, dimension=32, scope=scope, source_version=source)
    trace = TraceCollector(f"ch18-public-tag-stride{stride}-v1",
        versions(source, "planted-16-v1", "geometric-exact-eligible-top2-v1", None, None), [r["item_id"] for r in rows])
    methods_meta = {"prefilter_flat": pre.index_digest, "post_flat_r8": flat.index_digest,
        "post_flat_r32": flat.index_digest, "post_hnsw_e32_r8": graph.index_digest,
        "post_hnsw_e64_r32": graph.index_digest}
    trace.versions["index_version"] = methods_meta
    cases, times = [], {name: [] for name in methods_meta}
    rng = random.Random(SEED+stride)
    for qid, query in queries.items():
        methods = {"prefilter_flat": lambda: pre.search(query,scope=scope,depth=DEPTH),
            "post_flat_r8": lambda: flat.search(query,scope=scope,depth=8,public_predicate=predicate),
            "post_flat_r32": lambda: flat.search(query,scope=scope,depth=32,public_predicate=predicate),
            "post_hnsw_e32_r8": lambda: graph.search(query,scope=scope,depth=8,ef_search=32,public_predicate=predicate),
            "post_hnsw_e64_r32": lambda: graph.search(query,scope=scope,depth=32,ef_search=64,public_predicate=predicate)}
        expected = [i for i, _ in oracle(selected, query)]
        case = {"query_id": qid, "oracle_ids": expected, "modes": {}}
        for name, op in methods.items():
            result, rec = call(trace, qid, name, "quality", op)
            ids = [i for i, _ in result[0]]
            case["modes"][name] = {"candidate_ids": ids, "exact_neighbor_recall_at_2": rank_recall(ids,expected),
                "underfilled": len(ids)<K, "request_id": rec["request_id"], "final_count": len(ids)}
        if case["modes"]["prefilter_flat"]["candidate_ids"] != expected:
            raise AssertionError("Prefilter Flat oracle disagreement")
        for trial in range(3):
            for name in rng.sample(list(methods),len(methods)):
                _,rec=call(trace,qid,name,trial,methods[name])
                times[name].append(rec["stage_timings_ms"]["search"])
        cases.append(case)
    return {"workload_id": trace.workload_id, "versions": trace.versions, "scope": scope,
        "authorized_count": len(rows), "predicate_eligible_count": len(selected), "stride": stride,
        "predicate": "Public nonsecurity tag: ordinal % stride == 0; all indexed vectors already authorized",
        "query_count": len(queries), "k": K, "human_judgments": 0,
        "eligible_ids": pre.ids, "eligible_roster_sha256": pre.roster_digest,
        "cases": cases, "request_samples": trace.records,
        "summaries": {name: {"workload_id": trace.workload_id,
            "mean_filtered_exact_neighbor_recall_at_2": statistics.mean(c["modes"][name]["exact_neighbor_recall_at_2"] for c in cases),
            "underfill_rate": statistics.mean(c["modes"][name]["underfilled"] for c in cases),
            "adapter_search_timing": timing(times[name])} for name in methods_meta}}


def storage_case():
    pages = {"A": 0, "B": 0, "C": 1, "D": 2}
    cache, cases = [1], []
    trace = TraceCollector("ch18-logical-page-cache-v1",
        versions("ch18-four-node-pages-v1", "ch18-two-beams-v1", None, "lru-capacity2-entry-residency-v1", None), pages)
    for number, beam in enumerate((["A","B","C","D"], ["B","D","C"])):
        tick=perf_counter_ns()
        result = read_beam(beam,pages,cache,2)
        rec=trace.record(f"beam-{number}","logical_page_plan",0,([],{}),
            {"page_plan":(perf_counter_ns()-tick)/1e6}, status="ok", reason="no_vector_search_or_storage_io_run")
        rec.update(beam_node_ids=beam,cache_before=cache,**result)
        cases.append({"request_id":rec["request_id"],"beam":beam,"cache_before":cache,**result})
        cache=result["cache_after"]
    return {"workload_id":"ch18-logical-page-cache-v1", "node_to_page":pages,
        "capacity_pages":2,"cases":cases,"request_samples":trace.records,
        "measurement_kind":"logical counts only; page_plan times Python computation, no SSD or OS cache timed"}


def run(*, allow_download=False, artifact_dir):
    if faiss.__version__ != FAISS_VERSION or np.__version__ != NUMPY_VERSION:
        raise ValueError("Use the pinned Chapter18 native/numpy versions for this record")
    started=datetime.now(timezone.utc).isoformat()
    rows, qv=synthetic_rows(1024,32,16013082)
    queries={f"synth-{i:02d}": q for i,q in enumerate(qv[:16])}
    base=build_index(load_corpus())
    qrel_data,questions=load_stress_qrels(base)
    manifest,dense=load_snapshot(base,HERE.parent/"V3/index_ch13")
    support=[{"item_id":e.item_id,"vector":e.unit_vector,"allowed_scopes":list(e.allowed_scopes)}
             for e in dense.entries if "support-team" in e.allowed_scopes]
    model,model_info=load_encoder(allow_download=allow_download)
    trace=TraceCollector("ch13-stress-probes-v1",versions(base.snapshot,qrel_data["version"],qrel_data["version"],manifest["index_version"],model_info["model_revision"]),[r["item_id"] for r in support])
    judged_queries={}
    for qid,item in questions.items():
        with trace.guard(qid,"query_encode",0):
            tick=perf_counter_ns()
            judged_queries[qid]=embed(model,[item["question"]],batch_size=1)[0]
            trace.record(qid,"query_encode",0,([],{}),{"query_encode":(perf_counter_ns()-tick)/1e6},status="ok",reason="candidate_search_not_run")
    synth_trace=TraceCollector("ch16-synthetic-n1024-d32-v1",versions("synth-16013082","planted-16-v1","geometric-exact-top2",None,None),[r["item_id"] for r in rows])
    with single_thread():
        synthetic=benchmark(rows,queries,synth_trace,dimension=32,scope="benchmark",source_version="synth-16013082",artifact_dir=artifact_dir/"synthetic")
        judged=benchmark(support,judged_queries,trace,dimension=384,scope="support-team",source_version=manifest["index_version"],model_version=model_info["model_revision"],qrels=questions,base=base,artifact_dir=artifact_dir/"support")
        filtered=[filtered_case(rows,queries,stride) for stride in (8,64)]
    judged.update(qrels_sha256=sha256(QRELS), evidence_manifest_sha256=qrel_data["evidence_identity"]["manifest_sha256"],
                  judged_pairs=168,model=model_info,source_index_manifest=manifest)
    return {"experiment_id":"ch18-native-and-system-boundaries-v1", "date":"2026-10-12",
        "measurement_window_utc":{"start":started,"end":datetime.now(timezone.utc).isoformat()},
        "question":"Does a native graph beat native exhaustive search at a declared quality gate, and what does post-shortlist metadata filtering lose?",
        "hypothesis":"Native graph search may save distance work without winning tiny-workload latency. Filtering a fixed public shortlist can underfill and miss the filtered oracle even with exhaustive unfiltered scoring.",
        "baseline":"Faiss IndexFlatL2 plus same bounded exact refinement; independent exhaustive float64-accumulated oracle over float32 inputs",
        "controls":["Same stored vectors/queries/source/qrels/scope/top2; sorted IDs","One native OpenMP thread, one process, AVX2 CPU","M8/efConstruction64/seed18012026 fixed within graph sweep; native depth8 fixed","Query conversion/refinement separated from native kernel; context/encoding excluded","Postfilter foil uses only public tags on an already authorized roster"],
        "procedure":"Quality/warm call then five randomized-order adapter trials per query/mode; five warmed matrix-call batch samples per index; three randomized trials for each public-tag filter mode. Check reload, exact oracle and historical IDs.",
        "acceptance_gate":"No protected vectors indexed/scored; Flat agrees with independent oracle on frozen probes; do not replace operating route based on inspected diagnostics, batch throughput or unobservable native internals",
        "environment":{"python":platform.python_version(),"platform":platform.platform(),"faiss":faiss.__version__,"compile_options":faiss.get_compile_options(),"numpy":np.__version__,"native_threads":1},
        "code_sha256":{name:source_hash(HERE/name) for name in ("native_ch18.py","experiment_ch18.py","storage_ch18.py","hnsw_ch17.py","experiment_ch15.py")},
        "synthetic":synthetic,"v0_diagnostic":judged,"public_tag_filters":filtered,"logical_storage":storage_case(),
        "uncertainty":"One machine, graph seed/order and inspected query set; repeated timing trials are dependent. No confidence intervals or production SLOs; matrix-call throughput excludes per-query adapter/refinement/encoding/queue/network.",
        "decision":"Complete V4 as an index comparison laboratory. Keep exact dense and BM25; native indexes are experiments, not a database/service deployment or a validated answer-quality gain.",
        "limitations":["No DiskANN/SSD timing, ScaNN execution, vector database or distributed service implemented","Native binding hides internal scored IDs/frontiers; preserve separate Chapter17 diagnostic route without attributing it to native search","Serialized bytes are measured files, not RSS/replicas or original-source/context storage","No new human judgments; V0 questions already inspected; no train/dev/test/generalization claim","Native float32 arithmetic and stable reranking within a bounded returned pool do not establish global tie completeness","No generation/abstention measured"]}


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path,default=HERE/"chapter-18-experiment-local.json")
    parser.add_argument("--artifact-dir",type=Path)
    parser.add_argument("--allow-download",action="store_true")
    args=parser.parse_args()
    if args.artifact_dir:
        result=run(allow_download=args.allow_download,artifact_dir=args.artifact_dir)
    else:
        with tempfile.TemporaryDirectory(prefix="rag-ch18-indexes-") as temporary:
            result=run(allow_download=args.allow_download,artifact_dir=Path(temporary))
    args.output.write_text(json.dumps(result,separators=(",",":"),allow_nan=False)+"\n",encoding="utf-8")
    print(f"Wrote {args.output}; {result['decision']}")
