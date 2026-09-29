"""Chapter 9: judged V2 lexical baseline and execution-equivalence experiment.

The primary quality comparison changes only overlap versus BM25 scoring on
the same eligible V1 postings. WAND is an exact-execution control for BM25.
Search timing is local and excludes context construction and the V0 stub.
"""

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

from bm25 import build_bm25_index, search as bm25_search
from eval_ch09 import evaluate_ranking, load_judgments, nearest_rank, summarize
from lexical_index import (FROZEN_QUESTIONS, build_context, build_index,
                           load_corpus, search as overlap_search,
                           stub_answer)
from wand import build_wand_index, search as wand_search


HERE = Path(__file__).resolve().parent
MODES = ("overlap", "bm25_exhaustive", "bm25_wand")
DEPTHS = (1, 2, 5, 8)
SEED = 9092026
CONTEXT_BUDGET_WORDS = 120


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def signature(rows):
    return [(row["segment_id"], row["score"]) for row in rows]


def run(trials=11):
    if trials < 1:
        raise ValueError("trials must be positive")
    began = datetime.now(timezone.utc).isoformat()
    corpus = load_corpus()
    base = build_index(corpus)
    bm25 = build_bm25_index(base)
    wand = build_wand_index(bm25)
    dataset, queries = load_judgments(base)
    rng = random.Random(SEED)

    def call(mode, question, k):
        if mode == "overlap":
            return overlap_search(base, question, scope="support-team", top_k=k)
        if mode == "bm25_exhaustive":
            return bm25_search(bm25, question, scope="support-team", top_k=k)
        candidates, work, _ = wand_search(wand, question, scope="support-team", top_k=k)
        return candidates, work

    cases = []
    for qid, item in queries.items():
        for k in DEPTHS:
            modes = {}
            for mode in MODES:
                candidates, work = call(mode, item["question"], k)
                candidate_ids = [row["segment_id"] for row in candidates]
                judgment = evaluate_ranking(candidate_ids, item["grades"], k)
                context, context_words = build_context(candidates, CONTEXT_BUDGET_WORDS)
                context_ids = [row["segment_id"] for row in context]
                required_direct = set(item["grade_2"])
                context_direct_hits = len(required_direct & set(context_ids))
                if qid in FROZEN_QUESTIONS:
                    _, status, reason, supporting_ids = stub_answer(qid, context)
                else:
                    status, reason, supporting_ids = None, None, []
                modes[mode] = {
                    "candidate_ids": candidate_ids,
                    "candidate_scores_raw": [row["score"] for row in candidates],
                    "ranking_metrics": judgment,
                    "context_ids": context_ids,
                    "context_source_words": context_words,
                    "context_direct_hits": context_direct_hits,
                    "context_direct_recall": (context_direct_hits / len(required_direct)
                                              if required_direct else None),
                    "stub_status": status,
                    "stub_reason": reason,
                    "stub_supporting_ids": supporting_ids,
                    "scored_segments": work.get("scored_segments",
                                                work.get("fully_scored_segments")),
                    "work": work,
                }
            if (modes["bm25_exhaustive"]["candidate_ids"]
                    != modes["bm25_wand"]["candidate_ids"] or
                    modes["bm25_exhaustive"]["candidate_scores_raw"]
                    != modes["bm25_wand"]["candidate_scores_raw"] or
                    modes["bm25_exhaustive"]["context_ids"]
                    != modes["bm25_wand"]["context_ids"]):
                raise AssertionError(f"WAND and exhaustive BM25 disagree: {qid} k={k}")
            # One warm call per mode; then rotate method order for each trial.
            for mode in MODES:
                call(mode, item["question"], k)
            samples = {mode: [] for mode in MODES}
            for _ in range(trials):
                order = list(MODES)
                rng.shuffle(order)
                for mode in order:
                    start = perf_counter_ns()
                    call(mode, item["question"], k)
                    samples[mode].append(round((perf_counter_ns() - start) / 1000, 3))
            for mode in MODES:
                modes[mode]["search_latency_us"] = {
                    "raw": samples[mode],
                    "p50_nearest_rank": nearest_rank(samples[mode], .5),
                    "p95_nearest_rank": nearest_rank(samples[mode], .95),
                }
            cases.append({"query_id": qid, "slice": item["slice"],
                          "origin": item["origin"], "top_k": k,
                          "modes": modes, "wand_exact_agreement": True})

    summaries = {}
    for k in DEPTHS:
        summaries[str(k)] = {}
        for mode in MODES:
            rows = [case["modes"][mode]["ranking_metrics"]
                    for case in cases if case["top_k"] == k]
            timings = [sample for case in cases if case["top_k"] == k
                       for sample in case["modes"][mode]["search_latency_us"]["raw"]]
            quality = summarize(rows)
            summaries[str(k)][mode] = {
                **quality,
                "search_latency_us_equal_query_mix": {
                    "samples": len(timings),
                    "p50_nearest_rank": nearest_rank(timings, .5),
                    "p95_nearest_rank": nearest_rank(timings, .95),
                },
                "mean_fully_scored_segments": statistics.mean(
                    case["modes"][mode]["scored_segments"]
                    for case in cases if case["top_k"] == k),
            }

    failures = {}
    for qid in ("q-contract-change", "q-unknown-renewal", "q-private-target"):
        case = next(x for x in cases if x["query_id"] == qid and x["top_k"] == 2)
        failures[qid] = {
            "qrel_grade_2_ids": queries[qid]["grade_2"],
            "bm25_candidate_ids": case["modes"]["bm25_exhaustive"]["candidate_ids"],
            "bm25_context_ids": case["modes"]["bm25_exhaustive"]["context_ids"],
            "bm25_metrics": case["modes"]["bm25_exhaustive"]["ranking_metrics"],
            "stub_status": case["modes"]["bm25_exhaustive"]["stub_status"],
        }
    return {
        "experiment_id": "ch09-v2-judged-lexical-baseline-v1",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "measurement_window_utc": {"start": began,
                                   "end": datetime.now(timezone.utc).isoformat()},
        "question": "Does BM25 improve judged segment ranking over overlap on the declared small query set, and does exact WAND preserve BM25 quality?",
        "hypothesis": "BM25 macro NDCG@2 exceeds overlap on positive queries; WAND preserves every BM25 ranking and context. No latency gain is assumed.",
        "primary_variable": "overlap versus BM25 scoring; WAND is a same-score execution-equivalence control",
        "controls": ["V0 source snapshot and segmenter", "V1 analyzer and postings",
                     "support-team eligibility fixture", "frozen questions/qrels",
                     "top-k", "120 source-word context budget", "V0 stub for two original tasks"],
        "qrel_policy": "All twelve eligible segments inspected for each query; omitted nonzero entries are explicitly reviewed grade 0. Binary relevant grade >=1; direct evidence grade 2.",
        "zero_positive_policy": "Recall, Hit, F1, RR, AP, NDCG and direct recall are null and excluded from positive-query macro means; no-positive candidate rate is reported separately. P@k is zero by the fixed-k denominator.",
        "metric_conventions": {
            "precision_at_k": "binary hits/k; missing result slots are nonrelevant",
            "recall_at_k": "binary hits/all known grade>=1 eligible segments",
            "ap_at_k": "sum precision at hit ranks <=k / all known grade>=1 eligible segments",
            "rr_at_k": "reciprocal first grade>=1 rank <=k; zero when missed",
            "dcg_at_k": "sum (2^grade-1)/log2(rank+1); rank is 1-based",
            "ndcg_at_k": "DCG@k / ideal DCG@k over the judged eligible roster",
            "macro": "arithmetic mean over queries with positive qrels",
            "micro_recall": "sum binary hits / sum known relevant segments on positive queries",
            "percentile": "nearest rank ceil(p*n) on measured search-call durations",
        },
        "corpus_snapshot": corpus["snapshot"],
        "hash_policy": "SHA256 of UTF-8 bytes with CRLF canonicalized to LF",
        "corpus_sha256": sha256(HERE.parent / "V0" / "corpus.json"),
        "qrels_sha256": sha256(HERE / "judgments_ch09.json"),
        "index_code_sha256": sha256(HERE.parent / "V1" / "lexical_index.py"),
        "bm25_code_sha256": sha256(HERE / "bm25.py"),
        "wand_code_sha256": sha256(HERE / "wand.py"),
        "metric_code_sha256": sha256(HERE / "eval_ch09.py"),
        "experiment_code_sha256": sha256(HERE / "experiment_ch09.py"),
        "python": sys.version.split()[0], "platform": platform.platform(),
        "analyzer_version": base.analyzer.version, "index_version": base.version,
        "scoring_version": bm25.version, "execution_version": wand.version,
        "qrel_version": dataset["version"],
        "query_count": len(queries), "positive_query_count": sum(
            any(value >= 1 for value in item["grades"].values())
            for item in queries.values()),
        "judged_eligible_segments_per_query": len(dataset["eligible_segment_ids"]),
        "judged_pairs": len(queries) * len(dataset["eligible_segment_ids"]),
        "query_ids": list(queries), "depths": list(DEPTHS), "modes": list(MODES),
        "seed": SEED, "trials_per_method_query_depth": trials,
        "timing_scope": "candidate search only; excludes build, context, V0 stub and JSON writing",
        "latency_unit": "microseconds_per_search_call",
        "build_ms_one_run": {
            "postings": round(base.build_ms, 3),
            "bm25_statistics": round(bm25.statistics_build_ms, 3),
            "wand_impacts_bounds": round(wand.impact_build_ms, 3),
        },
        "context_budget_source_words": CONTEXT_BUDGET_WORDS,
        "limitations": ["13 indexed segments, twelve support-team eligible",
                        "fourteen authored/fixture queries, eleven with positive qrels",
                        "single author and no independent assessor/adjudication",
                        "V0 questions were known failures before Chapter 9 labels",
                        "only one static corpus/scope/analyzer and one timing machine",
                        "11 local samples per mode/query/depth; no service p95 estimate",
                        "no model-generated answer correctness or faithfulness judgment"],
        "summaries": summaries, "failure_examples_at_k2": failures,
        "cases": cases,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=HERE / "chapter-09-experiment.json")
    parser.add_argument("--trials", type=int, default=11)
    args = parser.parse_args()
    result = run(args.trials)
    args.output.write_text(json.dumps(result, ensure_ascii=True, allow_nan=False,
                                      indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {args.output}")
    for mode in MODES:
        score = result["summaries"]["2"][mode]
        print(mode, "macro NDCG@2=",
              round(score["macro_positive_query_mean"]["ndcg_at_k"], 4),
              "P@2=", round(score["macro_positive_query_mean"]["precision_at_k"], 4),
              "p50/p95 us=", score["search_latency_us_equal_query_mix"]["p50_nearest_rank"],
              score["search_latency_us_equal_query_mix"]["p95_nearest_rank"])


if __name__ == "__main__":
    main()
