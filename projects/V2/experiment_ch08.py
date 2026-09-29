"""Chapter 8: exact WAND versus cached exhaustive BM25 query execution.

The primary variable is the execution plan. Both timed plans read the same
prepared eligible term impacts. Chapter 7 BM25 is checked as an untimed
independent oracle. Required V0 spans are narrow fixture checks, not qrels.
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
from lexical_index import FROZEN_QUESTIONS, build_context, build_index, load_corpus, stub_answer
from wand import build_wand_index, exhaustive_cached_search, search as wand_search


HERE = Path(__file__).resolve().parent
SEED = 8082026
QUERIES = {
    **FROZEN_QUESTIONS,
    "q-rare-numeric": "12000 credits",
    "q-no-result": "zzzx-missing",
    "q-common-mix": "the support",
}
REQUIRED = {
    "q-contract-change": ["D1:§3:0", "D2:§2:0"],
    "q-termination": ["D1:§8:0"],
}
DEPTHS = (1, 2, 8)
MODES = ("cached_exhaustive", "wand")


def sha256(path):
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def nearest_rank(values, p):
    ordered = sorted(values)
    return ordered[max(1, math.ceil(p * len(ordered))) - 1]


def signature(rows):
    return [(row["segment_id"], row["score"]) for row in rows]


def observe(candidates, work, query_id):
    context, context_words = build_context(candidates, 120)
    required = REQUIRED.get(query_id, [])
    if required:
        _, status, reason, evidence_ids = stub_answer(query_id, context)
    else:
        status, reason, evidence_ids = None, None, []
    candidate_ids = [row["segment_id"] for row in candidates]
    context_ids = [row["segment_id"] for row in context]
    return {
        "candidate_scores": [
            {"segment_id": row["segment_id"], "score": round(row["score"], 6)}
            for row in candidates
        ],
        "required_evidence_ids": required,
        "required_in_candidates": [x for x in required if x in candidate_ids],
        "context_ids": context_ids,
        "required_in_context": [x for x in required if x in context_ids],
        "context_source_words": context_words,
        "fixture_answer_status": status,
        "fixture_answer_reason": reason,
        "fixture_evidence_ids": evidence_ids,
        "work": work,
    }


def toy_record():
    toy_path = HERE / "toy_pruning_corpus.json"
    toy = json.loads(toy_path.read_text(encoding="utf-8"))
    bm25 = build_bm25_index(toy)
    wand = build_wand_index(bm25)
    reference, reference_work = bm25_search(bm25, "rare common", top_k=1)
    cached, cached_work = exhaustive_cached_search(wand, "rare common", top_k=1)
    pruned, pruned_work, steps = wand_search(
        wand, "rare common", top_k=1, capture_steps=True
    )
    if not signature(reference) == signature(cached) == signature(pruned):
        raise AssertionError("Toy exact top-one disagreement")
    term_columns = wand.by_scope["support-team"]
    postings = {}
    blocks = {}
    block_width = 2  # docID ranges; toy WAND still uses GLOBAL term bounds
    last_eligible = max(bm25.base.scope_ordinals["support-team"])
    for term in ("common", "rare"):
        column = term_columns[term]
        postings[term] = [
            {"ordinal": ordinal, "segment_id": bm25.base.segments[ordinal]["segment_id"],
             "impact": round(impact, 9)}
            for ordinal, impact in zip(column.ordinals, column.impacts)
        ]
        blocks[term] = []
        for start in range(0, last_eligible + 1, block_width):
            impacts = [impact for ordinal, impact in zip(column.ordinals, column.impacts)
                       if start <= ordinal < start + block_width]
            blocks[term].append({
                "first_ordinal": start,
                "last_ordinal": min(start + block_width - 1, last_eligible),
                "upper_bound": round(max(impacts, default=0.0), 9),
            })
    return {
        "corpus_snapshot": toy["snapshot"], "corpus_sha256": sha256(toy_path),
        "query_id": "toy-rare-common", "scope_fixture": "support-team", "top_k": 1,
        "candidate_scores": observe(pruned, pruned_work, "toy-rare-common")["candidate_scores"],
        "reference_fully_scored_segments": reference_work["scored_segments"],
        "cached_exhaustive_work": cached_work,
        "wand_work": pruned_work,
        "global_term_upper_bounds": {
            term: term_columns[term].upper_bound for term in ("common", "rare")
        },
        "docid_block_width": block_width,
        "docid_block_bounds_conceptual_only": blocks,
        "postings": postings,
        "local_fictional_cursor_steps": steps,
    }


def run(trials=11):
    if trials < 1:
        raise ValueError("trials must be positive")
    corpus = load_corpus()
    base = build_index(corpus)
    bm25 = build_bm25_index(base)
    wand = build_wand_index(bm25)
    rng = random.Random(SEED)
    cases = []

    def call(mode, question, top_k):
        if mode == "cached_exhaustive":
            return exhaustive_cached_search(wand, question, top_k=top_k)
        rows, work, _ = wand_search(wand, question, top_k=top_k)
        return rows, work

    for query_id, question in QUERIES.items():
        for top_k in DEPTHS:
            oracle, _ = bm25_search(bm25, question, top_k=top_k)
            observed = {}
            raw_rows = {}
            for mode in MODES:
                candidates, work = call(mode, question, top_k)
                raw_rows[mode] = candidates
                if signature(candidates) != signature(oracle):
                    raise AssertionError(f"Exact top-k disagreement: {query_id} k={top_k} {mode}")
                observed[mode] = observe(candidates, work, query_id)
            if observed["cached_exhaustive"]["context_ids"] != observed["wand"]["context_ids"]:
                raise AssertionError("Context changed under execution-only comparison")
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
                observed[mode]["search_latency_us"] = {
                    "raw": samples[mode],
                    "median": round(statistics.median(samples[mode]), 3),
                    "p95_nearest_rank": round(nearest_rank(samples[mode], .95), 3),
                }
            cases.append({
                "query_id": query_id, "top_k": top_k,
                "exact_top_k_agreement": True, "modes": observed,
            })
    return {
        "experiment_id": "ch08-v2-exact-wand-v1",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "question": "Can bound-based execution score fewer segments while preserving exact BM25 top-k?",
        "hypothesis": "At least one frozen or toy case has fewer fully scored segments, and every tested case preserves exact IDs, float scores and selected context; median latency improvement is not assumed.",
        "baseline": "exhaustive accumulation over the same cached eligible term impacts",
        "independent_variable": "query execution plan: cached exhaustive sort or global-bound WAND with heap",
        "controlled_variables": ["V0 corpus snapshot", "V0 analyzer", "support-team scope fixture",
                                 "BM25 k1=1.2 b=.75 title boost=1", "term-impact cache",
                                 "query text", "top-k", "120 source-word context budget",
                                 "deterministic answer stub"],
        "evidence_measure": "fixture-required span coverage in candidates/context; no general qrels",
        "limitations": ["13-segment static V0 index", "one scope fixture",
                        "11 local search-only samples per mode/case", "Python RAM tuple/bisect implementation",
                        "no compressed-disk execution or BM25 block pruning",
                        "no human qrels or LLM answer judgment"],
        "hash_policy": "SHA256 of UTF-8 bytes with CRLF canonicalized to LF",
        "corpus_snapshot": corpus["snapshot"],
        "corpus_sha256": sha256(HERE.parent / "V0" / "corpus.json"),
        "index_code_sha256": sha256(HERE.parent / "V1" / "lexical_index.py"),
        "bm25_code_sha256": sha256(HERE / "bm25.py"),
        "wand_code_sha256": sha256(HERE / "wand.py"),
        "codec_code_sha256": sha256(HERE / "postings_codec.py"),
        "experiment_code_sha256": sha256(HERE / "experiment_ch08.py"),
        "python": sys.version.split()[0], "platform": platform.platform(),
        "seed": SEED, "query_set_version": "ch08-five-query-v1",
        "query_ids": list(QUERIES), "depths": list(DEPTHS), "modes": list(MODES),
        "analyzer_version": base.analyzer.version,
        "index_version": base.version,
        "scoring_version": bm25.version,
        "execution_version": wand.version,
        "scope_fixture": "support-team", "context_budget_source_words": 120,
        "postings_build_ms_one_run": round(base.build_ms, 3),
        "bm25_statistics_build_ms_one_run": round(bm25.statistics_build_ms, 3),
        "impact_bounds_build_ms_one_run": round(wand.impact_build_ms, 3),
        "stored_term_impacts_across_scopes": wand.stored_impacts,
        "trials_per_method_case": trials,
        "latency_unit": "microseconds_per_search_call",
        "timing_scope": "candidate search only; excludes all build, context and stub work",
        "cases": cases,
        "toy": toy_record(),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=HERE / "chapter-08-experiment.json")
    parser.add_argument("--trials", type=int, default=11)
    args = parser.parse_args()
    result = run(args.trials)
    args.output.write_text(json.dumps(result, ensure_ascii=True, allow_nan=False, indent=2) + "\n",
                           encoding="utf-8")
    print(f"Wrote {args.output}")
    toy = result["toy"]
    print("toy", toy["reference_fully_scored_segments"], "->",
          toy["wand_work"]["fully_scored_segments"], "fully scored;",
          toy["wand_work"]["postings_advanced_by_seek"], "postings advanced by seek")
    for case in result["cases"]:
        if case["top_k"] not in (1, 2):
            continue
        a, b = (case["modes"][mode]["work"]["fully_scored_segments"] for mode in MODES)
        if a > b:
            print(case["query_id"], f"k={case['top_k']}", f"{a}->{b} scored")


if __name__ == "__main__":
    main()
