"""Reproduce Chapter 5's scan-versus-postings comparison.

Synthetic copies increase corpus size; they are workload fixtures, not new
relevance judgments. The result retains raw timings and negative outcomes.
"""

import argparse
import hashlib
import json
import math
import platform
import random
import statistics
import sys
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter_ns

from lexical_index import Analyzer, build_index, load_corpus, search, segment_corpus
from engine import FROZEN_QUESTIONS, search as v0_search


HERE = Path(__file__).resolve().parent
QUERIES = {
    **FROZEN_QUESTIONS,
    "q-rare-numeric": "12000 credits",
    "q-no-result": "zzzx-missing",
}
SEED = 5042026


def clone_corpus(base, copies):
    if copies < 1:
        raise ValueError("copies must be positive")
    result = {"snapshot": f"{base['snapshot']}-synthetic-copies-{copies}", "documents": []}
    for copy_number in range(copies):
        for document in base["documents"]:
            clone = deepcopy(document)
            clone["id"] = f"D{copy_number * 10 + int(document['id'][1:])}"
            result["documents"].append(clone)
    return result


def nearest_rank(samples, fraction):
    ordered = sorted(samples)
    rank = max(1, math.ceil(fraction * len(ordered)))
    return ordered[rank - 1]


def timed_call(function):
    start = perf_counter_ns()
    result = function()
    return result, (perf_counter_ns() - start) / 1000  # microseconds


def run(copies=(1, 10, 100), trials=9):
    base = load_corpus()
    rng = random.Random(SEED)
    results = []
    for count in copies:
        corpus = clone_corpus(base, count)
        segments = segment_corpus(corpus)
        index = build_index(corpus, Analyzer("v0"))
        rows = []
        for query_id, question in QUERIES.items():
            def scan():
                return v0_search(segments, question, "support-team", 8)[0]

            def indexed():
                return search(index, question, "support-team", 8)[0]

            old = scan()
            new, work = search(index, question, "support-team", 8)
            old_signature = [(item["segment_id"], item["score"]) for item in old]
            new_signature = [(item["segment_id"], item["score"]) for item in new]
            if old_signature != new_signature:
                raise AssertionError(f"Candidate/score disagreement for {count=} {query_id=}")
            # Warm both paths. Alternate randomized method order for each pair.
            scan()
            indexed()
            samples = {"full_scan": [], "postings": []}
            for _ in range(trials):
                methods = [("full_scan", scan), ("postings", indexed)]
                rng.shuffle(methods)
                for name, function in methods:
                    _, elapsed_us = timed_call(function)
                    samples[name].append(round(elapsed_us, 3))
            rows.append({
                "query_id": query_id,
                "top8_candidate_scores": new_signature,
                "top8_exact_agreement": True,
                "full_scan_eligible_segments_scanned": work["eligible_segments"],
                "postings_eligible_posting_visits": work["eligible_posting_visits"],
                "postings_segments_scored": work["scored_segments"],
                "latency_us_per_query": {
                    name: {
                        "raw": values,
                        "median": round(statistics.median(values), 3),
                        "p95_nearest_rank": round(nearest_rank(values, .95), 3),
                    }
                    for name, values in samples.items()
                },
            })
        results.append({
            "copies": count,
            "segments": len(segments),
            "scope_eligible_segments": len(index.scope_ordinals["support-team"]),
            "index_version": index.version,
            "index_build_ms_one_run": round(index.build_ms, 3),
            "vocabulary_terms": len(index.postings),
            "term_document_pairs": index.term_document_pairs,
            "position_count": index.position_count,
            "queries": rows,
        })
    return {
        "experiment_id": "ch05-v0-scan-v1-postings-v1",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "base_corpus_snapshot": base["snapshot"],
        "base_corpus_sha256": hashlib.sha256(
            (HERE.parent / "V0" / "corpus.json").read_bytes()
        ).hexdigest(),
        "code_sha256": hashlib.sha256((HERE / "lexical_index.py").read_bytes()).hexdigest(),
        "experiment_code_sha256": hashlib.sha256((HERE / "experiment.py").read_bytes()).hexdigest(),
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "seed": SEED,
        "trials_per_method_per_query": trials,
        "query_ids": list(QUERIES),
        "query_set_version": "ch05-four-query-v1",
        "top_k": 8,
        "analyzer": "v0",
        "scope_fixture": "support-team",
        "latency_unit": "microseconds_per_query",
        "timing_scope": "search only; index build reported separately",
        "results": results,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=HERE / "chapter-05-experiment.json")
    parser.add_argument("--trials", type=int, default=9)
    args = parser.parse_args()
    if args.trials < 1:
        parser.error("trials must be positive")
    result = run(trials=args.trials)
    args.output.write_text(json.dumps(result, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {args.output}")
    for size in result["results"]:
        print(f"{size['segments']} segments; build {size['index_build_ms_one_run']:.3f} ms")
        for row in size["queries"]:
            latency = row["latency_us_per_query"]
            print(f"  {row['query_id']:18s} scan={latency['full_scan']['median']:8.3f} us "
                  f"index={latency['postings']['median']:8.3f} us "
                  f"scored={row['postings_segments_scored']}")


if __name__ == "__main__":
    main()
