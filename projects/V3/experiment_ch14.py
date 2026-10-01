"""Deterministic Chapter 14 toy mechanism record, not a model benchmark."""

import argparse
import hashlib
import json
import math
import platform
import random
import sys
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter_ns

from sparse_late_ch14 import SparseIndex, SparseRow, maxsim, pooled_cosine, sparse_pool

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "common"))
from experiment_trace import TraceCollector, versions, eligible, context_ids as trace_context_ids
SEED = 14092026
R = 2**-0.5
Q = [(1.0, 0.0), (0.0, 1.0)]
DOCUMENTS = {
    "A_both_with_noise": [(1.0, 0.0), (0.0, 1.0), (-R, -R), (-R, -R)],
    "B_generic": [(R, R)],
    "C_one_signal": [(1.0, 0.0)],
}
TOKEN_QRELS = {"A_both_with_noise": 2, "B_generic": 0, "C_one_signal": 1}
SPARSE_QRELS = {"incident": 2, "ticket_sale": 0, "reply_template": 0}


def source_sha256(path):
    """Match V3's source hash policy across LF/CRLF working trees."""
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def sparse_fixture():
    # These are hand-authored vocabulary logits. They did not come from an MLM.
    q = sparse_pool([{"ticket": 2.0, "incident": 1.8},
                     {"reply": 2.0, "response": 1.8}])
    lexical_q = {term: q[term] for term in ("ticket", "reply")}
    rows = [SparseRow("incident", "support-team", sparse_pool([{"incident": 2.0,
                                                                   "response": 2.0}])),
            SparseRow("ticket_sale", "support-team", sparse_pool([{"ticket": 2.0,
                                                                      "sale": 2.0}])),
            SparseRow("reply_template", "support-team", sparse_pool([{"reply": 2.0,
                                                                         "template": 2.0}])),
            SparseRow("private", "legal-team", sparse_pool([{"incident": 100.0,
                                                               "response": 100.0}]))]
    return q, lexical_q, SparseIndex(rows)


def timed(call, samples=31, *, trace=None, query_id=None, mode=None):
    call()  # warm Python path
    values = []
    for trial in range(samples):
        if trace is None:  # Preserve the original standalone timing helper API.
            start = perf_counter_ns()
            call()
            values.append((perf_counter_ns()-start)/1000)
        else:
            _, rec = trace.execute(query_id, mode, trial, call)
            values.append(rec["stage_timings_ms"]["search"]*1000)
    ordered = sorted(values)
    return {"unit": "microseconds", "samples": values,
            "p50_nearest_rank": ordered[math.ceil(.50*samples)-1],
            "p95_nearest_rank": ordered[math.ceil(.95*samples)-1]}


def elapsed_ms(call):
    start = perf_counter_ns()
    call()
    return (perf_counter_ns() - start)/1_000_000


def build_record():
    q, lexical_q, index = sparse_fixture()
    sparse = {}
    for name, representation in (("surface_only", lexical_q), ("expanded", q)):
        ranked, work = index.search(representation, "support-team", 3)
        sparse[name] = {"query_weights": representation, "ranking": ranked, "work": work,
                        "recall_at_1": int(bool(ranked) and ranked[0][0] == "incident")}
    token = {}
    for item_id, vectors in DOCUMENTS.items():
        score, grid, winners = maxsim(Q, vectors)
        token[item_id] = {"maxsim": score, "pooled_cosine": pooled_cosine(Q, vectors),
                          "grid": grid, "winner_indices": winners, "grade": TOKEN_QRELS[item_id]}
    maxsim_order = sorted(token, key=lambda key: (-token[key]["maxsim"], key))
    pooled_order = sorted(token, key=lambda key: (-token[key]["pooled_cosine"], key))
    methods = {
        "surface_postings": lambda: index.search(lexical_q, "support-team", 3),
        "expanded_postings": lambda: index.search(q, "support-team", 3),
        "exact_maxsim_three": lambda: sorted([(i, maxsim(Q, v)[0]) for i, v in DOCUMENTS.items()], key=lambda p: (-p[1], p[0])),
        "pooled_cosine_three": lambda: sorted([(i, pooled_cosine(Q, v)) for i, v in DOCUMENTS.items()], key=lambda p: (-p[1], p[0])),
    }
    random.seed(SEED)
    order = list(methods)
    random.shuffle(order)
    traces = {family: TraceCollector(f"ch14-{family}-fixture-v1",
        versions("ch14-toy-1", f"toy-{family}-1", "ch14-toy-1", "fixed-weights-or-vectors-1", None),
        SPARSE_QRELS if family == "sparse" else TOKEN_QRELS) for family in ("sparse", "token")}
    timings = {name: timed(methods[name], trace=traces["sparse" if "postings" in name else "token"],
        query_id="toy-sparse-1" if "postings" in name else "toy-token-1", mode=name) for name in order}
    code = HERE / "sparse_late_ch14.py"
    runner = HERE / "experiment_ch14.py"
    recorded_at = datetime.now(timezone.utc).isoformat()
    request_trace_examples = []
    for name, result in sparse.items():
        request_trace_examples.append({
            "request_id": f"toy-sparse-{name}", "query_id": "toy-sparse-1",
            "timestamp_utc": recorded_at, "corpus_snapshot": "ch14-toy-1",
            "index_version": "in-memory-fixed-weights-1", "scope_fixture": "support-team",
            "eligible_rows": result["work"]["eligible_rows"],
            "retrieved_ids": [item_id for item_id, _ in result["ranking"]],
            "raw_scores": [value for _, value in result["ranking"]],
            "elapsed_ms": elapsed_ms(lambda: index.search(
                lexical_q if name == "surface_only" else q, "support-team", 3)),
            "selected_context_ids": None, "answer_status": "not_run",
            "latency_summary_ref": "latency.methods." + ("surface_postings" if name == "surface_only" else "expanded_postings"),
            "status": "scored", "failure_reason": None})
    for name, order in (("exact_maxsim", maxsim_order), ("pooled_cosine", pooled_order)):
        request_trace_examples.append({
            "request_id": f"toy-token-{name}", "query_id": "toy-token-1",
            "timestamp_utc": recorded_at, "corpus_snapshot": "ch14-toy-1",
            "index_version": "in-memory-fixed-vectors-1", "scope_fixture": "all-three-public",
            "eligible_rows": 3, "retrieved_ids": order,
            "raw_scores": [token[item_id]["maxsim" if name == "exact_maxsim" else "pooled_cosine"] for item_id in order],
            "elapsed_ms": elapsed_ms(methods["exact_maxsim_three" if name == "exact_maxsim" else "pooled_cosine_three"]),
            "selected_context_ids": None, "answer_status": "not_run",
            "latency_summary_ref": "latency.methods." + ("exact_maxsim_three" if name == "exact_maxsim" else "pooled_cosine_three"),
            "status": "scored", "failure_reason": None})
    return {
        "experiment_id": "ch14-fixed-mechanism-probe", "date_utc": recorded_at,
        "question": "Can vocabulary expansion and token-level MaxSim change rankings on fully judged toy cases?",
        "hypothesis": "Expansion retrieves the incident at rank one where surface matching does not; MaxSim ranks the two-signal document above a generic one where pooled cosine does not.",
        "baseline": "Exact surface-term weighted postings and cosine of hand-authored mean-pooled unit token vectors",
        "independent_variables": ["add two manually authored query expansion terms", "replace pooled cosine with exact MaxSim"],
        "controls": "Fixed toy documents, qrels, vectors, scope, top-k and deterministic tie rule; no trained weights or generator",
        "procedure": "Freeze hand-authored fixtures and complete three-row judgments; run surface/expanded weighted postings and pooled/MaxSim exact scoring at k=3; warm each Python path once, then time 31 samples in a seeded shuffled method order; inspect rankings, work and failures.",
        "workload_slices": {"sparse_vocabulary_mismatch": {"question": "ticket reply latency",
                                                     "documents": {"incident": "incident response took 120 minutes", "ticket_sale": "ticket sale", "reply_template": "reply template"}},
                            "token_pooling_dilution": {"question": "match both abstract token needs",
                                                       "documents": {"A_both_with_noise": "two exact directions plus two distractors", "B_generic": "one generic direction", "C_one_signal": "one exact direction"}}},
        "frozen_judgments": {"sparse": SPARSE_QRELS, "token": TOKEN_QRELS,
                             "eligible_sparse_rows": 3, "assessor": "author", "rubric": "2 complete direct match; 1 partial; 0 irrelevant"},
        "source": {"chapter_13_baseline": "projects/V3/chapter-13-experiment.json",
                   "code_sha256": source_sha256(code),
                   "runner_sha256": source_sha256(runner),
                   "fixture_version": "ch14-toy-1", "model_version": None,
                   "index_version": "in-memory-fixed-weights-1", "seed": SEED},
        "sparse": sparse, "token": token,
        "token_rankings": {"exact_maxsim": maxsim_order, "pooled_cosine": pooled_order},
        "request_trace_examples": request_trace_examples,
        "workload_ids": [t.workload_id for t in traces.values()],
        "request_samples": [r for t in traces.values() for r in t.records],
        "latency": {"environment": {"python": platform.python_version(), "platform": platform.platform()},
                    "boundary": "warm in-process scoring only; excludes neural encoding, building, I/O, context and generation",
                    "method_order": order, "methods": timings},
        "failure_examples": ["Surface-only postings miss incident at every depth because there is no shared term.",
                             "Pooled cosine favors B_generic; it dilutes A_both_with_noise's two exact matches.",
                             "Expanded query also scores unrelated literal matches; no-result or precision is not solved.",
                             "The legal-team private row is not scored for support-team."],
        "decision": "keep as a mechanism fixture; no production retriever selected",
        "limitations": ["Fixed logits and token vectors are hand-authored, not trained SPLADE or ColBERT.",
                        "The sparse and token tasks are separate, tiny, one-author judged fixtures; their scores and latencies are not comparable to Chapter 13 BM25/dense measurements.",
                        "No confidence interval or transfer claim is possible from one query per task.",
                        "Fixed timing method order and tiny in-process Python loops make the microsecond percentiles sensitive to measurement overhead and cache state.",
                        "Exact MaxSim scans all toy token vectors; no ANN, compression, model forward pass or production latency is measured.",
                        "Static scope is an eligibility demonstration, not authenticated authorization.",
                        "No selected context, answer, citation, faithfulness or abstention outcome is measured."],
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=HERE / "chapter-14-experiment-local.json")
    args = parser.parse_args()
    record = build_record()
    args.output.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {args.output}")
