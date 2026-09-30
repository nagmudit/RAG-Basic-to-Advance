"""Chapter 13: materialized exact dense candidate retrieval and diagnostic slices."""

import argparse
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
from lexical_index import build_context, build_index, load_corpus  # noqa: E402
from bm25 import build_bm25_index, search as bm25_search  # noqa: E402
from eval_ch09 import evaluate_ranking, load_judgments as load_generic_qrels, nearest_rank, summarize  # noqa: E402
from experiment_ch11 import (MODEL_REVISION, build_dense_index, dense_search, embed,
                             load_encoder, load_judgments as load_ch11_qrels, sha256)  # noqa: E402
from dense_snapshot import (encode_batches, load_snapshot, searchable_text,
                            write_snapshot)  # noqa: E402

QRELS = HERE / "judgments_ch13.json"
INDEX_DIR = HERE / "index_ch13"
SEED = 13092026
DEPTHS = (2, 8)
SLICES = ("acronym", "exact_code", "negation", "numeric_constraint",
          "out_of_domain_style", "exploratory_cross_lingual", "no_eligible_evidence")


def load_stress_qrels(base, path=QRELS):
    data, queries = load_generic_qrels(base, path)
    if len(queries) != 14 or set(item["slice"] for item in queries.values()) != set(SLICES):
        raise ValueError("Chapter 13 diagnostic query or slice roster changed")
    if any(sum(item["slice"] == slice_name for item in queries.values()) != 2
           for slice_name in SLICES):
        raise ValueError("Each diagnostic slice must contain two queries")
    for item in queries.values():
        if (item["slice"] == "no_eligible_evidence") != (
                not item["grade_1"] and not item["grade_2"]):
            raise ValueError("No-evidence slice contradicts qrels")
    return data, queries


def source_rows(base, pairs):
    segments = {s["segment_id"]: s for s in base.segments}
    return [{**segments[sid], "score": value} for sid, value in pairs]


def dense_candidates(index, base, query_vector, k):
    rows, work = index.search(query_vector, scope="support-team", metric="cosine",
                              top_k=k, plan="heap")
    return source_rows(base, [(row["item_id"], row["value"]) for row in rows]), work


def evaluate_queries(queries, base, bm25, dense, model):
    cases = []
    vectors = {qid: embed(model, [item["question"]], batch_size=1)[0]
               for qid, item in queries.items()}
    for qid, item in queries.items():
        for k in DEPTHS:
            modes = {}
            for name in ("bm25", "dense"):
                candidates, work = (bm25_search(bm25, item["question"], scope="support-team",
                                                top_k=k) if name == "bm25" else
                                    dense_candidates(dense, base, vectors[qid], k))
                ids = [row["segment_id"] for row in candidates]
                context, source_words = build_context(candidates, 120)
                context_ids = [row["segment_id"] for row in context]
                if any(sid.startswith("D10:") for sid in ids + context_ids):
                    raise AssertionError("Legal-only result entered support-team path")
                modes[name] = {
                    "candidate_ids": ids, "candidate_scores_raw": [row["score"] for row in candidates],
                    "context_ids": context_ids, "context_source_words": source_words,
                    "context_direct_recall": (len(set(item["grade_2"]) & set(context_ids)) /
                                              len(item["grade_2"]) if item["grade_2"] else None),
                    "ranking_metrics": evaluate_ranking(ids, item["grades"], k),
                    "generation_status": None, "work": work,
                }
            cases.append({"query_id": qid, "slice": item["slice"], "k": k, "modes": modes})
    summaries = {}
    for k in DEPTHS:
        rows = [case for case in cases if case["k"] == k]
        summaries[str(k)] = {}
        for name in ("bm25", "dense"):
            overall = summarize([row["modes"][name]["ranking_metrics"] for row in rows])
            by_slice = {}
            for slice_name in SLICES:
                part = [row for row in rows if row["slice"] == slice_name]
                if slice_name == "no_eligible_evidence":
                    by_slice[slice_name] = {
                        "queries": len(part),
                        "candidate_return_rate": statistics.mean(
                            bool(row["modes"][name]["candidate_ids"]) for row in part)}
                else:
                    by_slice[slice_name] = summarize(
                        [row["modes"][name]["ranking_metrics"] for row in part])
            summaries[str(k)][name] = {**overall, "by_slice": by_slice}
    return cases, summaries, vectors


def batch_benchmark(model, texts, *, trials=3):
    results = {}
    for batch_size in (1, 4, 16):
        encode_batches(model, texts, batch_size)  # one untimed warm pass
        samples = []
        for _ in range(trials):
            tick = perf_counter_ns()
            encode_batches(model, texts, batch_size)
            samples.append(round((perf_counter_ns() - tick) / 1e6, 3))
        median = statistics.median(samples)
        results[str(batch_size)] = {
            "texts": len(texts), "samples_ms": samples, "median_ms": median,
            "texts_per_second_from_median": round(len(texts) * 1000 / median, 2),
        }
    return results


def timed_queries(queries, base, bm25, dense, model, *, trials=5):
    rng = random.Random(SEED)
    result = {name: {"samples_us": [], "by_slice": {}}
              for name in ("bm25", "dense_encode", "dense_scan", "dense_total")}
    items = list(queries.values())
    for _ in range(trials):
        rng.shuffle(items)
        for item in items:
            q = item["question"]
            slice_name = item["slice"]
            bm25_search(bm25, q, scope="support-team", top_k=2)
            embed(model, [q], batch_size=1)
            for name in rng.sample(["bm25", "dense"], 2):
                tick = perf_counter_ns()
                if name == "bm25":
                    bm25_search(bm25, q, scope="support-team", top_k=2)
                    components = {"bm25": (perf_counter_ns() - tick) / 1000}
                else:
                    vector = embed(model, [q], batch_size=1)[0]
                    encoded = perf_counter_ns()
                    dense_candidates(dense, base, vector, 2)
                    finished = perf_counter_ns()
                    components = {"dense_encode": (encoded - tick) / 1000,
                                  "dense_scan": (finished - encoded) / 1000,
                                  "dense_total": (finished - tick) / 1000}
                for stage, elapsed in components.items():
                    value = round(elapsed, 3)
                    result[stage]["samples_us"].append(value)
                    result[stage]["by_slice"].setdefault(slice_name, []).append(value)
    for stage in result:
        values = result[stage]["samples_us"]
        result[stage]["p50_us"] = nearest_rank(values, .5)
        result[stage]["p95_us"] = nearest_rank(values, .95)
        result[stage]["by_slice"] = {
            key: {"samples": len(vals), "p50_us": nearest_rank(vals, .5),
                  "p95_us": nearest_rank(vals, .95)}
            for key, vals in result[stage]["by_slice"].items()}
    return result


def run(*, index_dir=INDEX_DIR, allow_download=False, trials=5):
    if trials < 1:
        raise ValueError("trials must be positive")
    began = datetime.now(timezone.utc).isoformat()
    corpus = load_corpus()
    base = build_index(corpus)
    old_data, old_queries = load_ch11_qrels(base)
    data, queries = load_stress_qrels(base)
    model, model_info = load_encoder(allow_download=allow_download)
    texts = [searchable_text(segment) for segment in base.segments]
    batch_results = batch_benchmark(model, texts)
    tick = perf_counter_ns()
    manifest = write_snapshot(base, model, index_dir, batch_size=16)
    build_ms = round((perf_counter_ns() - tick) / 1e6, 3)
    tick = perf_counter_ns()
    loaded_manifest, dense = load_snapshot(base, index_dir)
    load_ms = round((perf_counter_ns() - tick) / 1e6, 3)
    assert manifest == loaded_manifest
    in_memory, _ = build_dense_index(base, model)
    parity = []
    for qid, item in old_queries.items():
        vector = embed(model, [item["question"]], batch_size=1)[0]
        for k in DEPTHS:
            old_rows, _ = dense_search(in_memory, base, vector, k)
            new_rows, _ = dense_candidates(dense, base, vector, k)
            old_ids = [row["segment_id"] for row in old_rows]
            new_ids = [row["segment_id"] for row in new_rows]
            max_delta = max((abs(a["score"] - b["score"])
                             for a, b in zip(old_rows, new_rows)), default=0)
            parity.append({"query_id": qid, "k": k, "in_memory_ids": old_ids,
                           "materialized_ids": new_ids, "max_score_delta": max_delta,
                           "rank_equal": old_ids == new_ids})
    bm25 = build_bm25_index(base)
    cases, summaries, _ = evaluate_queries(queries, base, bm25, dense, model)
    timings = timed_queries(queries, base, bm25, dense, model, trials=trials)
    return {
        "experiment_id": "ch13-v3-materialized-dense-v1",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "measurement_window_utc": {"start": began, "end": datetime.now(timezone.utc).isoformat()},
        "question": "Can a version-checked materialized exact dense index reproduce in-memory retrieval, and where does fixed dense retrieval fail against BM25 on diagnostic slices?",
        "hypothesis": "Materialized and in-memory top-k IDs agree at k=2,8; dense gains colloquial paraphrases but cannot be assumed to solve metadata IDs, numeric/negation, no-evidence or cross-language probes.",
        "acceptance_gate": "Retain the materialized exact baseline only if all 34 frozen Chapter 11 ordered rankings match and the manifest rejects incompatible/corrupt payloads; diagnostic qrel results guide later routes, not a production model release.",
        "baseline": "Pinned Chapter 11 in-memory exact cosine for parity; V2 BM25 on the same eligible corpus for relevance comparison",
        "primary_variable": "Persist and reload frozen passage vectors under a checked model/text/source manifest; diagnostic query slice is a separate fixed workload axis",
        "controls": ["Unchanged V0 segment snapshot and support-team scope", "same pinned model, title/body text, normalization and cosine", "same top-k, 120-word context builder and complete 12-segment qrel roster"],
        "procedure": "Freeze Chapter 11 and Chapter 13 qrels; benchmark batch encoding; build and reload float32 snapshot; compare 17 Chapter 11 rankings at k=2,8; compare dense and BM25 on 14 new reviewed probes at k=2,8; warm and time query stages.",
        "corpus_snapshot": corpus["snapshot"], "eligible_segments": 12,
        "all_indexed_segments": len(base.segments),
        "ch11_qrel_version": old_data["version"], "ch13_qrel_version": data["version"],
        "ch13_query_count": len(queries), "ch13_judged_pairs": len(queries) * 12,
        "judgment_policy": data["review_method"], "zero_policy": data["zero_policy"],
        "model": model_info, "index_manifest": manifest,
        "index_build_ms": build_ms, "index_load_ms": load_ms,
        "batch_encoding": batch_results, "materialization_parity": parity,
        "parity_summary": {"comparisons": len(parity),
                           "rank_agreements": sum(p["rank_equal"] for p in parity),
                           "largest_raw_score_delta": max(p["max_score_delta"] for p in parity)},
        "cases": cases, "summaries": summaries, "timings": timings,
        "timing_policy": "Model load after imports is separate; batch timings are three warmed encode-only trials per batch size in fixed 1,4,16 order; five warmed randomized-method-order samples per stress query for BM25 search or dense query encoding plus exact scan. No context/generation time in request samples. Nearest-rank p50/p95 are local diagnostics, not production tails.",
        "candidate_context_answer_policy": "Candidate IDs/scores, selected context IDs/direct coverage, and absent generation labels are separate; no generator runs on Chapter 13 probes.",
        "failure_examples": ["acronym-sla: both routes omit the current signed amendment at top two", "code-segment: literal metadata ID absent from title/body; BM25 returns none and dense returns unrelated runbook windows", "num-basic: both routes rank other Sev-1 passages above the signed Basic eight-hour agreement", "none-orion and none-private: both routes return candidates without eligible positive evidence"],
        "conclusion": "Materialization preserves all 34 frozen exact rankings. Dense improves the two-query colloquial slice in this fixture but does not solve metadata IDs, current-version selection, the Basic numeric case or no-evidence returns.",
        "decision": "Retain the versioned exact dense snapshot as the V3 candidate baseline and keep BM25 as a separate baseline; do not infer a production model replacement, ANN need, or universal score threshold.",
        "hash_policy": "SHA256 of UTF-8 bytes with CRLF canonicalized to LF for text source files; binary vector hash is over exact bytes",
        "corpus_sha256": sha256(HERE.parent / "V0" / "corpus.json"),
        "ch11_qrels_sha256": sha256(HERE / "judgments_ch11.json"),
        "ch13_qrels_sha256": sha256(QRELS),
        "snapshot_code_sha256": sha256(HERE / "dense_snapshot.py"),
        "experiment_code_sha256": sha256(HERE / "experiment_ch13.py"),
        "environment": {"python": platform.python_version(), "platform": platform.platform()},
        "seed": SEED,
        "limitations": ["One author wrote and judged fictional stress questions while knowing the corpus; no independent assessment or workload prevalence.", "The two Spanish-to-English probes are exploratory author translations, not a native-speaker multilingual benchmark.", "The same fixed model is used for parity and diagnostic comparisons; no new model gain or train/test claim is made.", "Only 13 short segments on one local CPU; batch throughput and p95 cannot size a production service, and fixed batch-size order may confound the throughput comparison.", "A static support-team scope fixture is not authentication; live ACL and deletion behavior are not implemented.", "No answer generator, answer correctness, citation support or calibrated no-result threshold is evaluated.", "The snapshot stores fictional vectors and a restricted-source fixture; real derived vectors need source-aligned retention and access control."],
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--allow-download", action="store_true")
    parser.add_argument("--trials", type=int, default=5)
    parser.add_argument("--index-dir", type=Path, default=INDEX_DIR)
    parser.add_argument("--output", type=Path, default=HERE / "chapter-13-experiment-local.json")
    args = parser.parse_args()
    record = run(index_dir=args.index_dir, allow_download=args.allow_download, trials=args.trials)
    args.output.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "parity": record["parity_summary"],
                      "top2_recall": {name: result["macro_positive_query_mean"]["recall_at_k"]
                                      for name, result in record["summaries"]["2"].items()}},
                     ensure_ascii=False))
