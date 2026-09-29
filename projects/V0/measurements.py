"""Chapter 3 diagnostic: compare two implementations of exact ID lookup.

This is not a term index and does not change V0's answer path. The list scan and
dictionary lookup perform the same exact-ID task on deterministic synthetic
records. Run from the repository root:

    python projects/V0/measurements.py
"""

import argparse
import json
import platform
import random
import sys
from datetime import datetime, timezone
from pathlib import Path
from statistics import median
from time import perf_counter_ns


DEFAULT_OUTPUT = Path(__file__).with_name("chapter-03-measurements.json")
SIZES = (64, 256, 1024, 4096, 16384)
SEED = 20260929
QUERY_COUNT = 256
TRIALS = 7


def make_records(count):
    if count < 1:
        raise ValueError("count must be positive")
    return [
        {"id": f"S{number:05d}", "payload": f"synthetic source {number}"}
        for number in range(count)
    ]


def make_queries(count, query_count=QUERY_COUNT, seed=SEED, hit_fraction=0.5):
    """Create a reproducible hit/miss workload for one size."""
    if query_count < 2 or query_count % 2:
        raise ValueError("query_count must be even and at least two")
    if hit_fraction not in (0.0, 0.5, 1.0):
        raise ValueError("hit_fraction must be 0, 0.5 or 1")
    rng = random.Random(seed + count)
    hit_count = int(query_count * hit_fraction)
    miss_count = query_count - hit_count
    hits = [f"S{rng.randrange(count):05d}" for _ in range(hit_count)]
    misses = [f"M{number:05d}" for number in range(miss_count)]
    keys = hits + misses
    rng.shuffle(keys)
    return keys


def linear_find(records, key):
    for record in records:
        if record["id"] == key:
            return record
    return None


def batch_hits(lookup, keys):
    """Consume every result so both timed methods do equivalent useful work."""
    return sum(lookup(key) is not None for key in keys)


def timed_batch(lookup, keys):
    started = perf_counter_ns()
    hits = batch_hits(lookup, keys)
    elapsed_ns = perf_counter_ns() - started
    return elapsed_ns / len(keys) / 1000, hits  # microseconds per lookup


def measure_size(count, query_count=QUERY_COUNT, trials=TRIALS, seed=SEED, hit_fraction=0.5):
    if trials < 1:
        raise ValueError("trials must be positive")
    records = make_records(count)
    keys = make_queries(count, query_count, seed, hit_fraction)
    expected_hits = int(query_count * hit_fraction)
    build_started = perf_counter_ns()
    by_id = {record["id"]: record for record in records}
    build_us = (perf_counter_ns() - build_started) / 1000
    if len(by_id) != len(records):
        raise AssertionError("duplicate synthetic source ID")

    # Correctness is verified outside timing. Both paths have exactly the same
    # observable answer, including misses; neither is a relevance retriever.
    for key in keys:
        if linear_find(records, key) != by_id.get(key):
            raise AssertionError(f"lookup disagreement on {key}")

    scan = lambda key: linear_find(records, key)
    hashed = by_id.get
    batch_hits(scan, keys)  # warm both paths before recording trials
    batch_hits(hashed, keys)
    scan_samples = []
    dict_samples = []
    for trial in range(trials):
        paths = (("scan", scan), ("dict", hashed))
        if trial % 2:
            paths = tuple(reversed(paths))
        for name, lookup in paths:
            per_lookup_us, hits = timed_batch(lookup, keys)
            if hits != expected_hits:
                raise AssertionError("incorrect hit count")
            (scan_samples if name == "scan" else dict_samples).append(per_lookup_us)

    return {
        "records": count,
        "queries_per_trial": query_count,
        "hits_per_trial": expected_hits,
        "misses_per_trial": query_count - expected_hits,
        "trials": trials,
        "scan_us_per_lookup_samples": scan_samples,
        "dict_us_per_lookup_samples": dict_samples,
        "scan_median_us_per_lookup": median(scan_samples),
        "dict_median_us_per_lookup": median(dict_samples),
        "dict_build_us_one_sample": build_us,
        "list_container_bytes_shallow": sys.getsizeof(records),
        "dict_container_bytes_shallow": sys.getsizeof(by_id),
        "json_utf8_bytes": len(json.dumps(records, ensure_ascii=False).encode("utf-8")),
    }


def run_experiment(sizes=SIZES, query_count=QUERY_COUNT, trials=TRIALS, seed=SEED, hit_fraction=0.5):
    return {
        "experiment_id": "chapter-03-exact-id-lookup-v1",
        "measured_at_utc": datetime.now(timezone.utc).isoformat(),
        "code_version": "measurements-v1",
        "source_context": "V0 teaching project; synthetic records, not V0 lexical retrieval",
        "python": sys.version.split()[0],
        "python_implementation": platform.python_implementation(),
        "platform": platform.platform(),
        "seed": seed,
        "size_order": list(sizes),
        "workload": (
            f"{hit_fraction:.0%} uniformly sampled present IDs, "
            f"{1-hit_fraction:.0%} absent IDs; fixed shuffled keys per size"
        ),
        "clock": "time.perf_counter_ns; batched wall time",
        "results": [measure_size(n, query_count, trials, seed, hit_fraction) for n in sizes],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--queries", type=int, default=QUERY_COUNT)
    parser.add_argument("--trials", type=int, default=TRIALS)
    parser.add_argument("--hit-fraction", type=float, choices=(0.0, 0.5, 1.0), default=0.5)
    args = parser.parse_args()
    report = run_experiment(query_count=args.queries, trials=args.trials, hit_fraction=args.hit_fraction)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {args.output}")
    for row in report["results"]:
        print(
            f"n={row['records']:5d}  scan={row['scan_median_us_per_lookup']:8.3f} us  "
            f"dict={row['dict_median_us_per_lookup']:8.3f} us  "
            f"build={row['dict_build_us_one_sample']:8.3f} us"
        )


if __name__ == "__main__":
    main()
