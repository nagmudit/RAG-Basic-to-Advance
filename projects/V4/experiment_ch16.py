"""Frozen Chapter 16 IVF-Flat versus residual PQ experiment."""

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
sys.path.insert(0, str(HERE.parent / "V1"))
sys.path.insert(0, str(HERE.parent / "V2"))
sys.path.insert(0, str(HERE.parent / "V3"))
from lexical_index import build_context, build_index, load_corpus  # noqa: E402
from eval_ch09 import evaluate_ranking, summarize, nearest_rank  # noqa: E402
from dense_snapshot import load_snapshot  # noqa: E402
from experiment_ch11 import embed, load_encoder, sha256  # noqa: E402
from experiment_ch13 import QRELS, load_stress_qrels, source_rows  # noqa: E402
from experiment_ch15 import synthetic_rows, rank_recall, source_hash  # noqa: E402
from ann_ch15 import exact_cosine  # noqa: E402
from ivf_pq_ch16 import IVFPQ  # noqa: E402

SEED = 16012026
K = 2


def timing(samples):
    return {"unit": "ms", "sample_count": len(samples),
            "samples": [round(x, 6) for x in samples],
            "p50_nearest_rank": round(nearest_rank(samples, .5), 6),
            "p95_nearest_rank": round(nearest_rank(samples, .95), 6)}


def modes(index, nprobes, *, rerank_depth=4):
    return {f"{method}_p{probe}": (probe, mode, depth)
            for probe in nprobes
            for method, mode, depth in (("flat", "flat", 0),
                                        ("adc", "adc", 0),
                                        ("refine", "adc", rerank_depth))}


def measure(index, rows, queries, *, scope, nprobes, qrels=None,
            context_source=None, rerank_depth=4):
    configs = modes(index, nprobes, rerank_depth=rerank_depth)
    rng = random.Random(SEED + len(rows))
    cases, samples = [], {name: [] for name in ("exact", *configs)}
    list_of = {item_id: row["list_id"] for item_id, row in index.rows.items()}
    for qid, q in queries.items():
        exact, _ = exact_cosine(rows, q, scope=scope, k=K)
        oracle = [i for i, _ in exact]
        result = {"query_id": qid, "exact_ids": oracle, "modes": {}}
        for name, (probe, mode, depth) in configs.items():
            ranked, work = index.search(q, scope=scope, k=K, nprobe=probe,
                                        mode=mode, rerank_depth=depth)
            ids = [i for i, _ in ranked]
            if any(i in index.deleted or scope not in index.rows[i]["allowed_scopes"] for i in ids):
                raise AssertionError("Ineligible candidate")
            value = {"candidate_ids": ids, "scores_negative_l2_squared": [v for _, v in ranked],
                     "work": work, "exact_neighbor_recall_at_2": rank_recall(ids, oracle),
                     "oracle_list_coverage_at_2": sum(list_of[i] in work["probed_lists"] for i in oracle)/len(oracle),
                     "generation_status": None}
            if qrels is not None:
                value["ranking_metrics"] = evaluate_ranking(ids, qrels[qid]["grades"], K)
                candidate_rows = context_source(ranked)
                context, _ = build_context(candidate_rows, 120)
                value["context_ids"] = [row["segment_id"] for row in context]
                if any(i.startswith("D10:") for i in ids + value["context_ids"]):
                    raise AssertionError("Restricted source entered V0 output")
            result["modes"][name] = value
        methods = {"exact": lambda q=q: exact_cosine(rows, q, scope=scope, k=K)}
        methods.update({name: (lambda p=p, m=m, d=d, q=q:
                               index.search(q, scope=scope, k=K, nprobe=p,
                                            mode=m, rerank_depth=d))
                        for name, (p, m, d) in configs.items()})
        for fn in methods.values():
            fn()
        for _ in range(2):
            for name in rng.sample(list(methods), len(methods)):
                tick = perf_counter_ns()
                methods[name]()
                samples[name].append((perf_counter_ns()-tick)/1e6)
        cases.append(result)
    summaries = {}
    for name in configs:
        values = [c["modes"][name] for c in cases]
        summaries[name] = {"mean_exact_neighbor_recall_at_2": statistics.mean(
                            v["exact_neighbor_recall_at_2"] for v in values),
                           "mean_oracle_list_coverage_at_2": statistics.mean(
                            v["oracle_list_coverage_at_2"] for v in values),
                           "mean_eligible_scored": statistics.mean(
                            v["work"]["eligible_scored"] for v in values),
                           "search_only_timing": timing(samples[name])}
        if qrels is not None:
            summaries[name]["qrel"] = summarize([v["ranking_metrics"] for v in values])
    if qrels is not None:
        summaries["exact"] = {"qrel": summarize([evaluate_ranking(
            c["exact_ids"], qrels[c["query_id"]]["grades"], K) for c in cases]),
                              "search_only_timing": timing(samples["exact"])}
    else:
        summaries["exact"] = {"search_only_timing": timing(samples["exact"])}
    full = max(nprobes)
    for case in cases:
        if case["modes"][f"flat_p{full}"]["candidate_ids"] != case["exact_ids"]:
            raise AssertionError("IVF-Flat with all lists must match exact top-k")
    return {"cases": cases, "summaries": summaries, "configuration": configs}


def synthetic_case(n, dimension, *, nlist, subspaces):
    seed = SEED + n + dimension
    rows, query_vectors = synthetic_rows(n, dimension, seed)
    queries = {f"synth-{i:02d}": q for i, q in enumerate(query_vectors[:16])}
    train_ids = random.Random(seed + 4).sample([row["item_id"] for row in rows], min(n, 256))
    tick = perf_counter_ns()
    index = IVFPQ(rows, nlist=nlist, subspaces=subspaces, bits=2,
                  training_ids=train_ids, seed=seed, source_version=f"synth-{seed}")
    build_ms = (perf_counter_ns()-tick)/1e6
    tests = measure(index, rows, queries, scope="benchmark",
                    nprobes=(1, 2, 4, nlist), rerank_depth=8)
    return {"n": n, "dimension": dimension, "query_count": len(queries),
            "distribution": "Gaussian unit vectors; query is stored vector plus σ=.08 Gaussian noise, then normalized",
            "seed": seed, "nlist": nlist, "nprobe_grid": [1, 2, 4, nlist],
            "subspaces": subspaces, "bits_per_subspace": 2,
            "training_size": len(train_ids), "training_ids_sha256": hashlib.sha256(
                "\n".join(train_ids).encode()).hexdigest(),
            "training_procedure": "Sample indexed rows without replacement; deterministic farthest-first Lloyd training; 8 iterations; residual PQ trained on assigned training vectors",
            "build_ms": round(build_ms, 6),
            "list_occupancy": [len(x) for x in index.lists],
            "mean_squared_reconstruction_error": statistics.mean(
                index.squared_reconstruction_error(row["item_id"]) for row in rows),
            "storage_lower_bounds": index.storage_lower_bounds(), **tests}


def v0_case(*, allow_download=False):
    base = build_index(load_corpus())
    qrel_data, questions = load_stress_qrels(base)
    manifest, dense = load_snapshot(base, HERE.parent / "V3" / "index_ch13")
    rows = [{"item_id": e.item_id, "vector": e.unit_vector,
             "allowed_scopes": e.allowed_scopes} for e in dense.entries
            if "support-team" in e.allowed_scopes]
    tick = perf_counter_ns()
    index = IVFPQ(rows, nlist=3, subspaces=8, bits=2, seed=SEED,
                  source_version=manifest["index_version"])
    build_ms = (perf_counter_ns()-tick)/1e6
    model, model_info = load_encoder(allow_download=allow_download)
    queries, encode_samples = {}, []
    for qid, item in questions.items():
        tick = perf_counter_ns()
        queries[qid] = embed(model, [item["question"]], batch_size=1)[0]
        encode_samples.append((perf_counter_ns()-tick)/1e6)
    tests = measure(index, rows, queries, scope="support-team", nprobes=(1, 2, 3),
                    qrels=questions, context_source=lambda ranking: source_rows(base, ranking),
                    rerank_depth=4)
    return {"corpus_snapshot": base.snapshot,
            "corpus_sha256": sha256(HERE.parent / "V0" / "corpus.json"),
            "qrels_version": qrel_data["version"], "qrels_sha256": sha256(QRELS),
            "qrel_review_policy": qrel_data["review_method"],
            "question_count": len(questions), "judged_pairs": len(questions)*len(rows),
            "scope_fixture": "support-team", "eligible_vectors": len(rows),
            "model": model_info, "index_manifest": manifest,
            "nlist": 3, "subspaces": 8, "bits_per_subspace": 2,
            "training_size": len(rows),
            "training_procedure": "All twelve already indexed support-team vectors train the tiny teaching codebooks; no independent training corpus",
            "build_ms": round(build_ms, 6), "query_encode_timing": timing(encode_samples),
            "list_occupancy": [len(x) for x in index.lists],
            "mean_squared_reconstruction_error": statistics.mean(
                index.squared_reconstruction_error(row["item_id"]) for row in rows),
            "storage_lower_bounds": index.storage_lower_bounds(), **tests}


def run(*, allow_download=False):
    started = datetime.now(timezone.utc).isoformat()
    synthetic = [synthetic_case(256, 8, nlist=8, subspaces=4),
                 synthetic_case(1024, 32, nlist=16, subspaces=8)]
    v0 = v0_case(allow_download=allow_download)
    large = synthetic[1]["summaries"]
    judged = v0["summaries"]
    return {"experiment_id": "ch16-v4-ivf-pq-v1",
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
            "measurement_window_utc": {"start": started, "end": datetime.now(timezone.utc).isoformat()},
            "question": "How much geometric and judged recall is lost by coarse probing versus residual compression, and what does exact refinement recover?",
            "hypothesis": "Increasing nprobe recovers list misses; full-probe IVF-Flat matches exact; PQ may misorder scanned vectors, while reranking only repairs items inside its shortlisted pool.",
            "baseline": "Chapter 13/15 exact cosine on the same normalized eligible vectors, top-k=2 and stable IDs",
            "primary_variables": ["nprobe across fixed nlist", "IVF-Flat versus residual PQ ADC versus top-R exact refinement"],
            "controls": ["Fixed corpus/queries/scope/model per case", "Identical trained centroids and assignments within each case", "Fixed codebooks and seed within each case", "Same top-two oracle and qrels"],
            "procedure": "Build once per corpus. Synthetic: 16 planted queries each at N=256,d=8 and N=1024,d=32, sample up to 256 indexed training rows, then run nprobe 1/2/4/all and Flat/ADC/refine. V0: train on all 12 eligible rows, encode 14 frozen questions once, run nprobe 1/2/3 and each mode. Warm each method then time two randomized-order search-only passes per query.",
            "acceptance_gate": "All-list IVF-Flat must match exact ordered top two. Do not replace the V0 exact index based on inspected qrels or toy Python latency; require fresh judged workload, memory and quality/latency gates.",
            "versions": {"seed": SEED, "index_code_sha256": source_hash(HERE / "ivf_pq_ch16.py"),
                         "runner_sha256": source_hash(HERE / "experiment_ch16.py")},
            "environment": {"python": platform.python_version(), "platform": platform.platform()},
            "synthetic": synthetic, "v0_diagnostic": v0,
            "timing_policy": "Local warmed Python search only, 2 randomized-order samples per fixed query; nearest-rank p95 is diagnostic. Training/build, model load, query encoding, context, generation, network and service queue are excluded and recorded separately where measured.",
            "failure_examples": [
                "spanish-fee: one-probe IVF-Flat misses both exact top-two lists; all-probe ADC has both available but returns two different IDs; top-four refinement recovers the exact pair.",
                "code-segment: all-probe top-four refinement cannot recover the exact second neighbor from below the ADC shortlist; even the exact dense top two omit the direct metadata-ID qrel.",
                "acronym-sla: the exact dense oracle itself misses the signed current clause, so changing ANN probes or codebooks does not fix the source/representation route.",
                "none-private: D10 is outside the support-team eligible roster before centroid/codebook training, candidate scoring and context construction; no-evidence behavior remains unmeasured as answer abstention."],
            "conclusion": (f"At N=1024,d=32, all-list Flat has exact-neighbor Recall@2 "
                           f"{large['flat_p16']['mean_exact_neighbor_recall_at_2']:.3f}, while ADC "
                           f"has {large['adc_p16']['mean_exact_neighbor_recall_at_2']:.3f} and "
                           f"top-eight refinement {large['refine_p16']['mean_exact_neighbor_recall_at_2']:.3f}. "
                           f"On inspected V0 qrels, one-probe Flat macro judged Recall@2 "
                           f"{judged['flat_p1']['qrel']['macro_positive_query_mean']['recall_at_k']:.3f} "
                           f"versus {judged['exact']['qrel']['macro_positive_query_mean']['recall_at_k']:.3f} exact. "
                           "Full-probe PQ ranking remains lossy even when coarse coverage is complete."),
            "uncertainty": "No confidence interval: repeated timings share the same 16 or 14 fixed queries, one corpus, one training sample/seed and one local CPU. Per-query outcomes and small-sample p95 are diagnostic, not production estimates.",
            "decision": "Retain exact dense as V4 oracle; use IVF/PQ only as measured candidate-index experiments until representative independently judged data and memory/latency budgets justify a change.",
            "limitations": ["Synthetic Gaussian vectors with planted queries have geometric labels only.",
                            "V0 qrels were written and inspected in Chapter 13; all twelve V0 vectors also train the coarse and PQ codebooks, so no independent gain claim is made.",
                            "Pure Python objects and local CPU loops do not measure optimized compressed-code SIMD/GPU paths or real resident memory.",
                            "Packed bytes are payload lower bounds; Python arrays/lists, IDs, scopes and original rerank vectors cost more.",
                            "Static support-team roster is not live ACL enforcement; deletes, re-training, source retention, shard ownership and index migration need later lifecycle work.",
                            "No generation is run; answer correctness, faithfulness, citations and abstention are unmeasured."]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--allow-download", action="store_true")
    parser.add_argument("--output", type=Path, default=HERE / "chapter-16-experiment-local.json")
    args = parser.parse_args()
    record = run(allow_download=args.allow_download)
    args.output.write_text(json.dumps(record, indent=2, ensure_ascii=False)+"\n", encoding="utf-8")
    print(f"wrote {args.output}")
