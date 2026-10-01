"""Chapter 15: exact KD versus exact vector oracle; LSH loss and work."""

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
from eval_ch09 import evaluate_ranking, nearest_rank, summarize  # noqa: E402
from dense_snapshot import load_snapshot  # noqa: E402
from experiment_ch11 import embed, load_encoder, sha256  # noqa: E402
from experiment_ch13 import QRELS, load_stress_qrels, source_rows  # noqa: E402
from ann_ch15 import KDTree, HyperplaneLSH, exact_cosine, unit  # noqa: E402

SEED = 15102026
K = 2
LSH_CONFIGS = tuple((tables, bits) for tables in (2, 4, 8)
                    for bits in (4, 6, 8))


def source_hash(path):
    return hashlib.sha256(Path(path).read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def synthetic_rows(n, dimension, seed):
    rng = random.Random(seed)
    rows = [{"item_id": f"s{i:05d}",
             "vector": unit(tuple(rng.gauss(0, 1) for _ in range(dimension))),
             "allowed_scopes": ["benchmark"]} for i in range(n)]
    queries = [unit(tuple(rows[rng.randrange(n)]["vector"][j] +
                          rng.gauss(0, 0.08) for j in range(dimension)))
               for _ in range(20)]
    return rows, queries


def rank_recall(observed, oracle, k=K):
    return len(set(observed[:k]) & set(oracle[:k])) / min(k, len(oracle))


def timing_summary(samples_ms):
    return {"unit": "ms", "sample_count": len(samples_ms),
            "samples": [round(x, 6) for x in samples_ms],
            "p50_nearest_rank": round(nearest_rank(samples_ms, .5), 6),
            "p95_nearest_rank": round(nearest_rank(samples_ms, .95), 6)}


def synthetic_case(n, dimension, seed):
    rows, queries = synthetic_rows(n, dimension, seed)
    tick = perf_counter_ns()
    kd = KDTree([{**row} for row in rows], leaf_size=8)
    kd_build_ms = (perf_counter_ns()-tick)/1e6
    tick = perf_counter_ns()
    lsh = HyperplaneLSH(rows, tables=4, bits=6, seed=seed, source_version=f"synthetic-{n}-{dimension}-{seed}")
    lsh_build_ms = (perf_counter_ns()-tick)/1e6
    cases, timings = [], {name: [] for name in ("exact", "kd", "lsh")}
    rng = random.Random(seed+1)
    for qid, q in enumerate(queries):
        exact, exact_work = exact_cosine(rows, q, scope="benchmark", k=K)
        kd_rank, kd_work = kd.search(q, k=K)
        lsh_rank, lsh_work = lsh.search(q, scope="benchmark", k=K)
        oracle_ids = [item_id for item_id, _ in exact]
        kd_ids = [item_id for item_id, _ in kd_rank]
        lsh_ids = [item_id for item_id, _ in lsh_rank]
        if kd_ids != oracle_ids:
            raise AssertionError("Exact KD tree disagrees with unit-vector cosine oracle")
        cases.append({"query_id": f"synth-{qid:02d}", "oracle_ids": oracle_ids,
                      "kd_ids": kd_ids, "lsh_ids": lsh_ids,
                      "kd_work": kd_work, "lsh_work": lsh_work,
                      "exact_work": exact_work,
                      "lsh_exact_neighbor_recall_at_2": rank_recall(lsh_ids, oracle_ids)})
        methods = {"exact": lambda: exact_cosine(rows, q, scope="benchmark", k=K),
                   "kd": lambda: kd.search(q, k=K),
                   "lsh": lambda: lsh.search(q, scope="benchmark", k=K)}
        for name in methods:
            methods[name]()
        for _ in range(3):
            for name in rng.sample(list(methods), len(methods)):
                tick = perf_counter_ns()
                methods[name]()
                timings[name].append((perf_counter_ns()-tick)/1e6)
    return {"n": n, "dimension": dimension, "query_count": len(queries), "k": K,
            "distribution": "independent Gaussian unit vectors; query is a randomly selected stored vector plus independent Gaussian noise σ=.08, renormalized",
            "seed": seed, "kd_leaf_size": 8, "lsh_tables": 4, "lsh_bits": 6,
            "build_ms": {"kd": round(kd_build_ms, 4), "lsh": round(lsh_build_ms, 4)},
            "raw_float32_vector_bytes_lower_bound": n*dimension*4,
            "lsh_signature_bits_lower_bound": n*4*6,
            "quality": {"kd_rank_agreement": sum(c["kd_ids"] == c["oracle_ids"] for c in cases),
                        "lsh_mean_exact_neighbor_recall_at_2": statistics.mean(
                            c["lsh_exact_neighbor_recall_at_2"] for c in cases)},
            "mean_scored_vectors": {"exact": n,
                                    "kd": statistics.mean(c["kd_work"]["scored_vectors"] for c in cases),
                                    "lsh": statistics.mean(c["lsh_work"]["scored_vectors"] for c in cases)},
            "timings": {name: timing_summary(values) for name, values in timings.items()},
            "cases": cases}


def v0_case(*, allow_download=False):
    corpus = load_corpus()
    base = build_index(corpus)
    data, queries = load_stress_qrels(base)
    manifest, dense = load_snapshot(base, HERE.parent / "V3" / "index_ch13")
    rows = [{"item_id": entry.item_id, "vector": entry.unit_vector,
             "allowed_scopes": entry.allowed_scopes} for entry in dense.entries]
    support_rows = [{**row} for row in rows if "support-team" in row["allowed_scopes"]]
    tick = perf_counter_ns()
    kd = KDTree(support_rows, leaf_size=2)
    kd_build_ms = (perf_counter_ns()-tick)/1e6
    indexes, build_ms = {}, {}
    for tables, bits in LSH_CONFIGS:
        name = f"lsh_t{tables}_b{bits}"
        tick = perf_counter_ns()
        indexes[name] = HyperplaneLSH(rows, tables=tables, bits=bits,
                                      seed=SEED, source_version=manifest["index_version"])
        build_ms[name] = (perf_counter_ns()-tick)/1e6
    model, model_info = load_encoder(allow_download=allow_download)
    cases, encode_ms = [], []
    search_samples = {name: [] for name in ("exact", "kd", *indexes)}
    rng = random.Random(SEED)
    for qid, item in queries.items():
        tick = perf_counter_ns()
        q = embed(model, [item["question"]], batch_size=1)[0]
        encoded_elapsed_ms = (perf_counter_ns()-tick)/1e6
        encode_ms.append(encoded_elapsed_ms)
        oracle, oracle_work = dense.search(q, scope="support-team", metric="cosine",
                                           top_k=K, plan="heap")
        exact_ids = [row["item_id"] for row in oracle]
        kd_rank, kd_work = kd.search(q, k=K)
        if [item_id for item_id, _ in kd_rank] != exact_ids:
            raise AssertionError(f"KD exact parity failed on {qid}")
        modes = {"exact": {"ranked": [(row["item_id"], row["value"]) for row in oracle],
                           "work": oracle_work},
                 "kd": {"ranked": kd_rank, "work": kd_work}}
        for name, index in indexes.items():
            ranked, work = index.search(q, scope="support-team", k=K)
            modes[name] = {"ranked": ranked, "work": work}
        for name, mode in modes.items():
            ids = [item_id for item_id, _ in mode["ranked"]]
            candidate_rows = source_rows(base, mode["ranked"])
            context, _ = build_context(candidate_rows, 120)
            mode.update({"candidate_ids": ids,
                         "candidate_scores_raw": [value for _, value in mode["ranked"]],
                         "context_ids": [row["segment_id"] for row in context],
                         "ranking_metrics": evaluate_ranking(ids, item["grades"], K),
                         "exact_neighbor_recall_at_2": rank_recall(ids, exact_ids),
                         "generation_status": None,
                         "status": "empty_bucket" if name.startswith("lsh") and not ids else "scored"})
            del mode["ranked"]
            if any(sid.startswith("D10:") for sid in ids + mode["context_ids"]):
                raise AssertionError("Restricted segment entered candidate/context")
        methods = {"exact": lambda: dense.search(q, scope="support-team", metric="cosine", top_k=K, plan="heap"),
                   "kd": lambda: kd.search(q, k=K),
                   **{name: (lambda index=index: index.search(q, scope="support-team", k=K))
                      for name, index in indexes.items()}}
        for name in methods:
            methods[name]()
        for _ in range(3):
            for name in rng.sample(list(methods), len(methods)):
                tick = perf_counter_ns()
                methods[name]()
                search_samples[name].append((perf_counter_ns()-tick)/1e6)
        cases.append({"request_id": f"ch15-{qid}", "query_id": qid,
                      "index_version": manifest["index_version"],
                      "scope_fixture": "support-team", "query_encode_ms": round(encoded_elapsed_ms, 6),
                      "slice": item["slice"], "grades_1": item["grade_1"],
                      "grades_2": item["grade_2"], "modes": modes})
    summaries = {}
    for name in ("exact", "kd", *indexes):
        ranked = [case["modes"][name]["ranking_metrics"] for case in cases]
        summaries[name] = {"qrel": summarize(ranked),
                           "mean_exact_neighbor_recall_at_2": statistics.mean(
                               case["modes"][name]["exact_neighbor_recall_at_2"] for case in cases),
                           "mean_scored_vectors": statistics.mean(
                               case["modes"][name]["work"]["scored_vectors"] for case in cases),
                           "search_only_timing": timing_summary(search_samples[name])}
    return {"corpus_snapshot": base.snapshot, "corpus_sha256": sha256(HERE.parent / "V0" / "corpus.json"),
            "qrels_version": data["version"], "qrels_sha256": sha256(QRELS),
            "qrel_review_policy": data["review_method"],
            "question_count": len(queries), "judged_pairs": len(queries)*12,
            "eligible_vectors": len(support_rows), "all_indexed_vectors": len(rows),
            "scope_fixture": "support-team", "k": K, "model": model_info,
            "index_manifest": manifest, "kd_leaf_size": 2,
            "lsh_configurations": [{"name": f"lsh_t{t}_b{b}", "tables": t, "bits": b,
                                    "seed": SEED} for t, b in LSH_CONFIGS],
            "index_build_ms": {"kd": kd_build_ms, **build_ms},
            "query_encode_timing": timing_summary(encode_ms),
            "summaries": summaries, "cases": cases}


def run(*, allow_download=False):
    began = datetime.now(timezone.utc).isoformat()
    synthetic = [synthetic_case(n, dimension, SEED+n+dimension)
                 for dimension in (2, 32) for n in (128, 512, 2048)]
    real = v0_case(allow_download=allow_download)
    exact = real["summaries"]["exact"]
    kd = real["summaries"]["kd"]
    lsh = real["summaries"]["lsh_t2_b4"]
    return {
        "experiment_id": "ch15-v4-exact-kd-lsh-v1", "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "measurement_window_utc": {"start": began, "end": datetime.now(timezone.utc).isoformat()},
        "question": "When do geometric partitions or random-hyperplane buckets reduce comparisons without losing exact neighbors or judged evidence?",
        "hypothesis": "KD backtracking preserves exact top two but loses pruning advantage as ambient dimension grows; LSH visits fewer vectors but may omit oracle neighbors and judged evidence.",
        "baseline": "Chapter 13 checked, normalized exact cosine scan with bounded top-k heap; synthetic exact cosine scores every eligible vector and uses bounded top-k heap selection",
        "primary_variables": ["exact KD bounding-box traversal at fixed leaf size", "predeclared 3×3 factorial LSH table/bit grid on inspected V0 questions"],
        "controls": ["same vectors, query coordinates, support-team scope, k=2 and stable ID ties within each comparison",
                     "synthetic seed/distribution fixed per n/dimension; no labels are inferred from geometric proximity"],
        "procedure": "On synthetic unit vectors at n=128/512/2048 and d=2/32, compare exact scan, exact KD and fixed LSH(4 tables,6 bits) on 20 queries; repeat warm randomized-order search timing three times. On the existing Chapter 13 judged V0 fixture, load the pinned manifest, encode each fixed question once, compare exact/KD/a predeclared 3×3 table-count by bit-count LSH grid, then repeat warmed search-only timings three times. Report exact-neighbor and qrel quality separately.",
        "acceptance_gate": "KD must match exact ordered top two on all tested vectors; LSH is retained only as an illustrative approximation, not a V0 replacement, unless independent qrels and representative latency show a useful frontier.",
        "versions": {"seed": SEED, "synthetic_generator": "Gaussian-unit-v1",
                     "ann_code_sha256": source_hash(HERE / "ann_ch15.py"),
                     "runner_sha256": source_hash(HERE / "experiment_ch15.py")},
        "environment": {"python": platform.python_version(), "platform": platform.platform()},
        "synthetic": synthetic, "v0_diagnostic": real,
        "timing_policy": "Warmed local Python scoring only, three randomized method-order samples per query; model construction and V0 query encoding, index build, context, generation, network and service queue are outside search-only latency. Nearest-rank p95 on small samples is diagnostic.",
        "failure_examples": ["style-ticket: LSH 2-table/4-bit bucket union is empty although exact top two include direct D7 incident evidence",
                             "acronym-sla: exact dense itself omits current signed D2 at top two; an exact-neighbor match cannot solve this representation/status failure",
                             "code-segment: metadata ID is absent from the embedded title/body text and needs an authorized exact-ID route",
                             "none-private: legal-only D10 remains ineligible, and an empty LSH bucket cannot establish answerable abstention"],
        "conclusion": (f"On inspected V0 questions KD agrees with all exact ordered top-two rankings while its search-only p50 is {kd['search_only_timing']['p50_nearest_rank']:.3f} ms versus {exact['search_only_timing']['p50_nearest_rank']:.3f} ms exact. "
                       f"LSH 2-table/4-bit has mean exact-neighbor Recall@2 {lsh['mean_exact_neighbor_recall_at_2']:.3f} and judged macro Recall@2 {lsh['qrel']['macro_positive_query_mean']['recall_at_k']:.3f} versus {exact['qrel']['macro_positive_query_mean']['recall_at_k']:.3f} exact. "
                       "The synthetic low-dimensional KD gain and high-dimensional LSH speed/recall trade-off do not transfer automatically to a production corpus."),
        "decision": "Keep Chapter 13 exact dense as V4 oracle; do not deploy Chapter 15 toy LSH or infer general ANN speedup.",
        "limitations": ["Chapter 13 questions are inspected one-author fictional diagnostics, not a fresh held-out set; LSH settings were chosen before this run but are not a production model selection.",
                        "Synthetic Gaussian unit vectors and planted noisy queries have no human qrels and do not represent production embeddings or query mix.",
                        "Python objects and loops, tiny V0 corpus and local CPU timings cannot predict optimized vector kernels, cache/memory bandwidth or service tail latency.",
                        "Static scope is not authentication; live ACL, updates, deletes, disk, shard and cache behavior are absent.",
                        "No generation runs on the V0 diagnostic questions; answer correctness, faithfulness, citations and abstention are unmeasured."]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--allow-download", action="store_true")
    parser.add_argument("--output", type=Path, default=HERE / "chapter-15-experiment-local.json")
    args = parser.parse_args()
    record = run(allow_download=args.allow_download)
    args.output.write_text(json.dumps(record, indent=2, ensure_ascii=False)+"\n", encoding="utf-8")
    print(f"wrote {args.output}")
