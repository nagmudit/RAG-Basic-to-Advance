"""Paired Chapter 7 lexical-ranking experiment on unchanged V0 questions.

This is a fixture-required-evidence comparison. Chapter 9 adds broad qrels,
judged retrieval metrics and an expanded frozen query set to complete V2.
"""

import argparse
import hashlib
import json
import math
import platform
import random
import statistics
import sys
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter_ns

from bm25 import build_bm25_index, search as bm25_search
from lexical_index import (FROZEN_QUESTIONS, build_context, build_index,
                           load_corpus, search as overlap_search, stub_answer)
from tfidf import build_weighted_index, search as tfidf_search


HERE = Path(__file__).resolve().parent
SEED = 7072026
QUERIES = {
    **FROZEN_QUESTIONS,
    "q-rare-numeric": "12000 credits",
    "q-no-result": "zzzx-missing",
}
REQUIRED = {
    "q-contract-change": ["D1:§3:0", "D2:§2:0"],
    "q-termination": ["D1:§8:0"],
}
DEPTHS = (2, 8)
MODES = ("overlap", "tfidf_raw", "tfidf_cosine", "bm25_b0", "bm25_b075")


def sha256(path):
    # Canonicalize text line endings: Git may check out the same blob as CRLF.
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def nearest_rank(values, p):
    ordered = sorted(values)
    return ordered[max(1, math.ceil(p * len(ordered))) - 1]


def run(trials=7):
    if trials < 1:
        raise ValueError("trials must be positive")
    corpus = load_corpus()
    base = build_index(corpus)
    weighted = build_weighted_index(base)
    b0 = build_bm25_index(base, b=0)
    b075 = build_bm25_index(base, b=.75)

    def call(mode, question, top_k):
        if mode == "overlap":
            return overlap_search(base, question, scope="support-team", top_k=top_k)
        if mode.startswith("tfidf_"):
            return tfidf_search(weighted, question, scope="support-team", top_k=top_k,
                                mode=mode.removeprefix("tfidf_"))
        return bm25_search(b0 if mode == "bm25_b0" else b075, question,
                           scope="support-team", top_k=top_k)

    rng = random.Random(SEED)
    cases = []
    for query_id, question in QUERIES.items():
        for top_k in DEPTHS:
            modes = {}
            for mode in MODES:
                candidates, work = call(mode, question, top_k)
                context, context_words = build_context(candidates, 120)
                required = REQUIRED.get(query_id, [])
                if required:
                    _, status, reason, evidence_ids = stub_answer(query_id, context)
                else:
                    status, reason, evidence_ids = None, None, []
                candidate_ids = [item["segment_id"] for item in candidates]
                context_ids = [item["segment_id"] for item in context]
                modes[mode] = {
                    "candidate_scores": [
                        {"segment_id": item["segment_id"],
                         "score": round(item["score"], 6)}
                        for item in candidates
                    ],
                    "required_evidence_ids": required,
                    "required_in_candidates": [i for i in required if i in candidate_ids],
                    "context_ids": context_ids,
                    "required_in_context": [i for i in required if i in context_ids],
                    "context_source_words": context_words,
                    "fixture_answer_status": status,
                    "fixture_answer_reason": reason,
                    "fixture_evidence_ids": evidence_ids,
                    "work": work,
                }
            for mode in MODES:
                call(mode, question, top_k)
            samples = {mode: [] for mode in MODES}
            for _ in range(trials):
                order = list(MODES)
                rng.shuffle(order)
                for mode in order:
                    started = perf_counter_ns()
                    call(mode, question, top_k)
                    samples[mode].append(round((perf_counter_ns() - started) / 1000, 3))
            for mode in MODES:
                modes[mode]["search_latency_us"] = {
                    "raw": samples[mode],
                    "median": round(statistics.median(samples[mode]), 3),
                    "p95_nearest_rank": round(nearest_rank(samples[mode], .95), 3),
                }
            cases.append({"query_id": query_id, "top_k": top_k, "modes": modes})
    return {
        "experiment_id": "ch07-v2-bm25-versus-v1-v1",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_hash_policy": "SHA256 of UTF-8 bytes with CRLF canonicalized to LF",
        "question": "Does BM25 b=.75 improve both frozen required-evidence tasks at top two over raw TF-IDF?",
        "hypothesis": "BM25 b=.75 places all required spans in top-two context for both tasks; falsified if either task lacks a required span.",
        "baseline": "V1 raw TF-IDF; overlap and cosine are retained historical controls",
        "independent_variable": "declared scoring configuration; the BM25 b pair isolates b",
        "controlled_variables": ["source snapshot", "V0 analyzer", "support-team eligibility fixture",
                                 "question text", "candidate depth", "120 source-word context budget",
                                 "deterministic answer stub", "k1=1.2 and title boost=1 for BM25"],
        "evidence_measure": "required fixture spans in candidates/context divided by listed required spans; not general qrels",
        "limitations": ["two required-evidence tasks only", "no human relevance judgments",
                        "deterministic stub, no LLM", "tiny static corpus and scope",
                        "seven local timings per case, not production tails"],
        "corpus_snapshot": corpus["snapshot"],
        "corpus_sha256": sha256(HERE.parent / "V0" / "corpus.json"),
        "index_code_sha256": sha256(HERE.parent / "V1" / "lexical_index.py"),
        "tfidf_code_sha256": sha256(HERE.parent / "V1" / "tfidf.py"),
        "bm25_code_sha256": sha256(HERE / "bm25.py"),
        "experiment_code_sha256": sha256(HERE / "experiment_ch07.py"),
        "python": sys.version.split()[0], "platform": platform.platform(),
        "seed": SEED, "query_set_version": "ch06-four-query-v1",
        "query_ids": list(QUERIES), "depths": list(DEPTHS), "modes": list(MODES),
        "analyzer_version": base.analyzer.version,
        "index_version": base.version,
        "scoring_versions": {
            "overlap": "v1-ch05-distinct-term-overlap",
            "tfidf_raw": weighted.version + "-raw",
            "tfidf_cosine": weighted.version + "-cosine",
            "bm25_b0": b0.version, "bm25_b075": b075.version,
        },
        "scope_fixture": "support-team", "context_budget_source_words": 120,
        "postings_build_ms_one_run": round(base.build_ms, 3),
        "statistics_build_ms_one_run": {
            "tfidf": round(weighted.statistics_build_ms, 3),
            "bm25_b0": round(b0.statistics_build_ms, 3),
            "bm25_b075": round(b075.statistics_build_ms, 3),
        },
        "trials_per_method_case": trials,
        "latency_unit": "microseconds_per_search_call",
        "timing_scope": "candidate search only; excludes build/context/stub",
        "cases": cases,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=HERE / "chapter-07-experiment.json")
    parser.add_argument("--trials", type=int, default=7)
    args = parser.parse_args()
    result = run(args.trials)
    args.output.write_text(json.dumps(result, ensure_ascii=True, indent=2) + "\n",
                           encoding="utf-8")
    print(f"Wrote {args.output}")
    for case in result["cases"]:
        if case["query_id"] not in REQUIRED or case["top_k"] != 2:
            continue
        print(case["query_id"], "top_k=2")
        for mode, row in case["modes"].items():
            print(f"  {mode:13s} required={len(row['required_in_context'])}/"
                  f"{len(row['required_evidence_ids'])} "
                  f"status={row['fixture_answer_status']} "
                  f"median_search={row['search_latency_us']['median']:.3f} us")


if __name__ == "__main__":
    main()
