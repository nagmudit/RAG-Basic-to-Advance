"""Small redacted request/sample envelope; no source text or query text is stored.

The timer surrounds the operation only. Context selection and serialization are
outside that timer. IDs must come from the caller's already eligible roster.
"""
import math
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from time import perf_counter_ns

VERSION_FIELDS = ("corpus_version", "query_set_version", "qrels_version",
                  "index_version", "model_version")
REQUIRED_FIELDS = ("request_id", "query_id", "mode", "trial_id", "workload_id",
                   *VERSION_FIELDS, "status", "reason", "stage_timings_ms",
                   "raw_candidate_ids", "raw_candidate_scores",
                   "intermediate_candidate_ids", "intermediate_candidate_scores",
                   "final_candidate_ids", "final_candidate_scores",
                   "context_ids", "evidence_ids")


def versions(corpus, queries, qrels, index, model):
    return dict(zip(VERSION_FIELDS, (corpus, queries, qrels, index, model)))


def context_ids(base, result):
    from lexical_index import build_context
    ranked, _ = pairs(result)
    if not {i for i, _ in ranked} <= set(eligible(base)):
        raise ValueError("Ineligible candidate before forward/context fetch")
    sources = {s["segment_id"]: s for s in base.segments}
    context, _ = build_context([{**sources[i], "score": score} for i, score in ranked], 120)
    return [s["segment_id"] for s in context]


def eligible(base):
    return [base.segments[i]["segment_id"] for i in sorted(base.scope_ordinals["support-team"])]


def pairs(result):
    rows, work = result if isinstance(result, tuple) else (result, {})
    return [(r.get("segment_id", r.get("item_id")), r.get("score", r.get("value")))
            if isinstance(r, dict) else tuple(r) for r in rows], work


def validate(record, eligible_ids):
    if any(key not in record for key in REQUIRED_FIELDS):
        raise ValueError("Incomplete trace envelope")
    for ids, scores in ((record["raw_candidate_ids"], record["raw_candidate_scores"]),
                        (record["final_candidate_ids"], record["final_candidate_scores"]),
                        *((ids, record["intermediate_candidate_scores"][name])
                          for name, ids in record["intermediate_candidate_ids"].items())):
        if len(ids) != len(scores) or not set(ids) <= set(eligible_ids):
            raise ValueError("Ineligible or unaligned diagnostic candidates")
        if not all(math.isfinite(float(s)) for s in scores):
            raise ValueError("Nonfinite diagnostic score")
    for field in ("context_ids", "evidence_ids"):
        if record[field] is not None and not set(record[field]) <= set(eligible_ids):
            raise ValueError("Ineligible diagnostic context")
    if any(not math.isfinite(t) or t < 0 for t in record["stage_timings_ms"].values()):
        raise ValueError("Invalid diagnostic timing")


class TraceCollector:
    def __init__(self, workload_id, versions, eligible_ids):
        if any(key not in versions for key in VERSION_FIELDS):
            raise ValueError("Explicit version identities are required (None means not applicable)")
        self.workload_id, self.versions = workload_id, dict(versions)
        self.eligible_ids = set(eligible_ids)
        self.records = []

    def record(self, query_id, mode, trial_id, result, timings, *, context=None,
               status=None, reason=None):
        ranked, work = pairs(result)
        stages = work.get("candidate_stages", {})
        raw = stages.get("scored", ranked)
        if reason is None and not ranked and status is None:
            reason = work.get("reason") or ("empty_bucket" if work.get("no_bucket_match") else
                                            "empty_eligible_probe" if work.get("empty_eligible_probe") else "no_candidates")
        rec = {"schema_version": "rag-sample-1", "request_id": str(uuid.uuid4()),
               "query_id": query_id, "mode": mode, "trial_id": trial_id,
               "workload_id": self.workload_id, **self.versions,
               "timestamp_utc": datetime.now(timezone.utc).isoformat(),
               "status": status or ("ok" if ranked else "empty"), "reason": reason,
               "stage_timings_ms": dict(timings),
               "raw_candidate_ids": [i for i, _ in raw],
               "raw_candidate_scores": [s for _, s in raw],
               "intermediate_candidate_ids": {n: [i for i, _ in p] for n, p in stages.items() if n != "scored"},
               "intermediate_candidate_scores": {n: [s for _, s in p] for n, p in stages.items() if n != "scored"},
               "final_candidate_ids": [i for i, _ in ranked],
               "final_candidate_scores": [s for _, s in ranked],
               "context_ids": context, "evidence_ids": None,
               "ivf_probed_lists": work.get("probed_lists"),
               "timing_boundary": "operation only; context/trace serialization excluded"}
        index_identity = self.versions["index_version"]
        if isinstance(index_identity, dict) and mode in index_identity:
            rec["index_version"] = index_identity[mode]
        validate(rec, self.eligible_ids)
        self.records.append(rec)
        return rec

    @contextmanager
    def guard(self, query_id, mode, trial_id):
        """Emit a redacted error for a multi-stage operation with manual timers."""
        start, before = perf_counter_ns(), len(self.records)
        try:
            yield
        except Exception as exc:
            if len(self.records) == before:
                self.record(query_id, mode, trial_id, ([], {}),
                    {"failed_attempt": (perf_counter_ns()-start)/1e6},
                    status="invalid" if isinstance(exc, ValueError) else "failed",
                    reason="invalid_input" if isinstance(exc, ValueError) else "operation_failed")
            raise

    def execute(self, query_id, mode, trial_id, operation, *, stage="search", context_selector=None):
        start = perf_counter_ns()
        try:
            result = operation()
        except Exception as exc:
            elapsed = (perf_counter_ns() - start) / 1e6
            # Never serialize exception text: it may contain protected input.
            self.record(query_id, mode, trial_id, ([], {}), {stage: elapsed},
                        status="invalid" if isinstance(exc, ValueError) else "failed",
                        reason="invalid_input" if isinstance(exc, ValueError) else "operation_failed")
            raise
        elapsed = (perf_counter_ns() - start) / 1e6
        try:
            ranked, work = pairs(result)
            visible = [i for i, _ in ranked]
            visible.extend(i for stage in work.get("candidate_stages", {}).values() for i, _ in stage)
            if not set(visible) <= self.eligible_ids:
                raise ValueError("Ineligible candidate before context selection")
            context = context_selector(result) if context_selector else None
            rec = self.record(query_id, mode, trial_id, result, {stage: elapsed}, context=context)
        except Exception:
            self.record(query_id, mode, trial_id, ([], {}), {stage: elapsed},
                        status="failed", reason="diagnostic_or_eligibility_violation")
            raise
        return result, rec
