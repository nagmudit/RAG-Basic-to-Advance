"""Chapter 6 paired overlap-versus-TF-IDF ranking comparison.

Only the scoring rule changes; corpus, analyzer, postings, eligibility,
candidate depth and context budget stay fixed. The two V0 evidence sets are
narrow fixture checks, not a general relevance-judgment collection.
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

from lexical_index import (
    FROZEN_QUESTIONS, build_context, build_index, load_corpus,
    search as overlap_search, stub_answer,
)
from tfidf import build_weighted_index, search as weighted_search


HERE = Path(__file__).resolve().parent
SEED = 6062026
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
MODES = ("overlap", "raw", "sublinear", "cosine")


def nearest_rank(values, fraction):
    ordered = sorted(values)
    return ordered[max(1, math.ceil(fraction * len(ordered))) - 1]


def run(trials=7):
    if trials < 1:
        raise ValueError("trials must be positive")
    corpus = load_corpus()
    base = build_index(corpus)
    weighted = build_weighted_index(base)
    rng = random.Random(SEED)
    cases = []
    for query_id, question in QUERIES.items():
        for top_k in DEPTHS:
            def call(mode):
                if mode == "overlap":
                    return overlap_search(base, question, scope="support-team", top_k=top_k)
                return weighted_search(
                    weighted, question, scope="support-team", top_k=top_k, mode=mode
                )

            observed = {}
            for mode in MODES:
                candidates, work = call(mode)
                context, context_words = build_context(candidates, 120)
                required = REQUIRED.get(query_id, [])
                if required:
                    _, answer_status, reason, evidence_ids = stub_answer(query_id, context)
                else:
                    answer_status, reason, evidence_ids = None, None, []
                observed[mode] = {
                    "candidate_scores": [
                        {"segment_id": part["segment_id"], "score": round(part["score"], 6)}
                        for part in candidates
                    ],
                    "required_evidence_ids": required,
                    "required_in_candidates": [
                        item for item in required
                        if item in {part["segment_id"] for part in candidates}
                    ],
                    "context_ids": [part["segment_id"] for part in context],
                    "required_in_context": [
                        item for item in required
                        if item in {part["segment_id"] for part in context}
                    ],
                    "context_source_words": context_words,
                    "fixture_answer_status": answer_status,
                    "fixture_answer_reason": reason,
                    "fixture_evidence_ids": evidence_ids,
                    "work": work,
                }
            for mode in MODES:
                call(mode)  # warm path outside timing
            samples = {mode: [] for mode in MODES}
            for _ in range(trials):
                order = list(MODES)
                rng.shuffle(order)
                for mode in order:
                    started = perf_counter_ns()
                    call(mode)
                    samples[mode].append(round((perf_counter_ns() - started) / 1000, 3))
            for mode in MODES:
                observed[mode]["search_latency_us"] = {
                    "raw": samples[mode],
                    "median": round(statistics.median(samples[mode]), 3),
                    "p95_nearest_rank": round(nearest_rank(samples[mode], .95), 3),
                }
            cases.append({"query_id": query_id, "top_k": top_k, "modes": observed})
    return {
        "experiment_id": "ch06-v1-overlap-tfidf-variants-v1",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "corpus_snapshot": corpus["snapshot"],
        "corpus_sha256": hashlib.sha256((HERE.parent / "V0" / "corpus.json").read_bytes()).hexdigest(),
        "index_code_sha256": hashlib.sha256((HERE / "lexical_index.py").read_bytes()).hexdigest(),
        "ranker_code_sha256": hashlib.sha256((HERE / "tfidf.py").read_bytes()).hexdigest(),
        "experiment_code_sha256": hashlib.sha256((HERE / "experiment_ch06.py").read_bytes()).hexdigest(),
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "seed": SEED,
        "query_set_version": "ch06-four-query-v1",
        "query_ids": list(QUERIES),
        "depths": list(DEPTHS),
        "modes": list(MODES),
        "analyzer_version": base.analyzer.version,
        "index_version": base.version,
        "scoring_version": weighted.version,
        "scope_fixture": "support-team",
        "context_budget_source_words": 120,
        "postings_build_ms_one_run": round(base.build_ms, 3),
        "scope_statistics_build_ms_one_run": round(weighted.statistics_build_ms, 3),
        "trials_per_method_case": trials,
        "latency_unit": "microseconds_per_search_call",
        "timing_scope": "candidate search only, excluding build/context/stub",
        "cases": cases,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=HERE / "chapter-06-experiment.json")
    parser.add_argument("--trials", type=int, default=7)
    args = parser.parse_args()
    if args.trials < 1:
        parser.error("trials must be positive")
    result = run(trials=args.trials)
    args.output.write_text(json.dumps(result, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {args.output}")
    for case in result["cases"]:
        if case["query_id"] not in REQUIRED or case["top_k"] != 2:
            continue
        print(case["query_id"], "top_k=2")
        for mode, row in case["modes"].items():
            print(f"  {mode:9s} required={len(row['required_in_candidates'])}/"
                  f"{len(row['required_evidence_ids'])} "
                  f"status={row['fixture_answer_status']} "
                  f"median_search={row['search_latency_us']['median']:.3f} us")


if __name__ == "__main__":
    main()
