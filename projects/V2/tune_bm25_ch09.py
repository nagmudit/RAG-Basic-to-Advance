"""Bounded dev-select-freeze-test BM25 exercise; original Ch09 is diagnostic.

New authored questions hold out query wording, not corpus/source families. This
is methodology practice on twelve eligible segments, not a release benchmark.
"""
import argparse
import json
import platform
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "V1"))
sys.path.insert(0, str(HERE.parent / "common"))
from lexical_index import build_index, load_corpus
from bm25 import build_bm25_index, search
from eval_ch09 import evaluate_ranking, summarize, nearest_rank
from qrel_identity import validate_judgments, digest
from experiment_trace import TraceCollector, versions, eligible, context_ids

DATA = HERE / "judgments_bm25_tuning.json"
K1 = (.8, 1.2, 1.6, 2.)
B = (0., .25, .5, .75, 1.)
DEFAULT = (1.2, .75)
WORKLOAD = "ch09-bm25-devtest-v1"


def summarize_slice(rows):
    if any(row["relevant_count"] for row in rows):
        return summarize(rows)
    return {"positive_queries": 0, "zero_positive_queries": len(rows),
            "macro_positive_query_mean": None,
            "zero_positive_candidate_rate": sum(row["retrieved_count"] > 0 for row in rows)/len(rows)}


def load_workload(base, path=DATA):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    validate_judgments(data, base)
    roster = eligible(base)
    if data["eligible_segment_ids"] != roster:
        raise ValueError("Tuning roster mismatch")
    seen = set()
    for group in ("development", "test"):
        if not data[group]:
            raise ValueError("Empty tuning split")
        for item in data[group]:
            if item["query_id"] in seen or not item["question"] or not item["rationale"]:
                raise ValueError("Duplicate/incomplete query across dev/test")
            seen.add(item["query_id"])
            strong, partial = item["grade_2"], item["grade_1"]
            if not set(strong + partial) <= set(roster) or not set(strong).isdisjoint(partial):
                raise ValueError("Invalid tuning judgments")
            item["grades"] = {sid: 2 if sid in strong else 1 if sid in partial else 0 for sid in roster}
    return data


def evaluate(base, parameters, queries):
    index = build_bm25_index(base, k1=parameters[0], b=parameters[1])
    cases = []
    for item in queries:
        rows, work = search(index, item["question"], scope="support-team", top_k=2)
        ids = [r["segment_id"] for r in rows]
        cases.append({"query_id": item["query_id"], "slice": item["slice"],
                      "candidate_ids": ids, "candidate_scores": [r["score"] for r in rows],
                      "metrics": evaluate_ranking(ids, item["grades"], 2), "work": work})
    return {"cases": cases, "summary": summarize([c["metrics"] for c in cases]),
            "slices": {name: summarize_slice([c["metrics"] for c in cases if c["slice"] == name])
                       for name in sorted({c["slice"] for c in cases})}}


def select_parameters(base, development):
    # This function cannot access test queries or test labels.
    grid = []
    for k1 in K1:
        for b in B:
            result = evaluate(base, (k1, b), development)
            metric = result["summary"]["macro_positive_query_mean"]["ndcg_at_k"]
            grid.append({"k1": k1, "b": b, "development_ndcg_at_2": metric, "development": result})
    # Preregistered tie rule: keep default, then closest to it, then numeric order.
    winner = min(grid, key=lambda r: (-r["development_ndcg_at_2"],
        (r["k1"], r["b"]) != DEFAULT, abs(r["k1"]-1.2)+abs(r["b"]-.75), r["k1"], r["b"]))
    return (winner["k1"], winner["b"]), grid


def run(path=DATA, trials=7):
    if trials < 1:
        raise ValueError("Positive timing trials required")
    base = build_index(load_corpus())
    data = load_workload(base, path)
    chosen, grid = select_parameters(base, data["development"])
    frozen = {"selected_k1": chosen[0], "selected_b": chosen[1],
              "selection_metric": "macro positive-query NDCG@2", "cutoff": 2,
              "grid": {"k1": K1, "b": B}, "tie_rule": "default, nearest to default, numeric",
              "development_sha256": digest(data["development"]), "test_used_for_selection": False}
    frozen["selection_sha256"] = digest(frozen)
    # Test evaluation begins only after this parameter/selection record is frozen.
    tests = {name: evaluate(base, parameters, data["test"])
             for name, parameters in (("default", DEFAULT), ("selected", chosen))}
    collectors = {}
    for name, parameters in (("default", DEFAULT), ("selected", chosen)):
        index = build_bm25_index(base, k1=parameters[0], b=parameters[1])
        collectors[name] = TraceCollector(WORKLOAD, versions(base.snapshot, data["version"], data["version"], index.version, None), eligible(base))
    rng = random.Random(90917)
    for item in data["test"]:
        indexes = {name: build_bm25_index(base, k1=p[0], b=p[1])
                   for name, p in (("default", DEFAULT), ("selected", chosen))}
        for index in indexes.values():
            search(index, item["question"], scope="support-team", top_k=2)
        for trial in range(trials):
            for name in rng.sample(list(indexes), 2):
                collectors[name].execute(item["query_id"], name, trial,
                    lambda: search(indexes[name], item["question"], scope="support-team", top_k=2),
                    context_selector=lambda result: context_ids(base, result))
    timing = {}
    for name, collector in collectors.items():
        samples = [r["stage_timings_ms"]["search"]*1000 for r in collector.records]
        timing[name] = {"unit": "us", "samples": samples, "p50": nearest_rank(samples, .5), "p95": nearest_rank(samples, .95)}
    return {"experiment_id": "ch09-bm25-devtest-selection-v1", "workload_id": WORKLOAD,
            "corpus_version": base.snapshot, "query_set_version": data["version"], "qrels_version": data["version"],
            "evidence_manifest_sha256": data["evidence_identity"]["manifest_sha256"],
            "analyzer": base.analyzer.version, "scope": "support-team", "title_boost": 1.,
            "selection": frozen, "development_grid_results": grid, "test": tests,
            "request_samples": [r for c in collectors.values() for r in c.records], "timing": timing,
            "timing_policy": f"One warm call, {trials} randomized paired trials/query, perf_counter_ns search-only; local diagnostics, not service tails",
            "environment": {"python": platform.python_version(), "platform": platform.platform()},
            "limitations": ["Author-written new-query holdout on already known sources; not independent population validation",
                            "Original Chapter 09 cases remain inspected diagnostics and are not used as this test",
                            "Six questions per split, one assessor, no confidence interval; no universal parameter or quality-gain claim"]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=HERE / "chapter-09-tuning-local.json")
    parser.add_argument("--trials", type=int, default=7)
    args = parser.parse_args()
    args.output.write_text(json.dumps(run(trials=args.trials), ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(f"wrote {args.output}")
