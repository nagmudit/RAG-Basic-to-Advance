"""Chapter 9: explicit, small-corpus segment judgments and ranking metrics.

Every eligible segment in the pinned support-team roster was reviewed. The
qrels file stores nonzero grades compactly and declares every other eligible
roster ID grade zero. The loader rejects a changed source/segment roster.
"""

import json
import math
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "V1"))
from lexical_index import FROZEN_QUESTIONS, build_index, load_corpus
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "common"))
from qrel_identity import validate_judgments


HERE = Path(__file__).resolve().parent
JUDGMENTS_PATH = HERE / "judgments_ch09.json"


def load_judgments(index=None, path=JUDGMENTS_PATH):
    index = index or build_index(load_corpus())
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    validate_judgments(data, index)
    if data["corpus_snapshot"] != index.snapshot:
        raise ValueError("Qrels and corpus snapshots differ")
    if data["scope_fixture"] != "support-team" or data["retrieval_unit"] != "indexed_segment":
        raise ValueError("Qrels use a different scope or unit")
    roster = [index.segments[i]["segment_id"]
              for i in sorted(index.scope_ordinals["support-team"])]
    if len(roster) != len(set(roster)) or data["eligible_segment_ids"] != roster:
        raise ValueError("Qrel roster differs from the indexed eligible segments")
    ids = set(roster)
    queries = {}
    for item in data["queries"]:
        qid = item["query_id"]
        if qid in queries:
            raise ValueError(f"Duplicate query ID: {qid}")
        if not item.get("question") or not item.get("slice") or not item.get("rationale"):
            raise ValueError(f"Missing query or judgment rationale: {qid}")
        if qid in FROZEN_QUESTIONS and item["question"] != FROZEN_QUESTIONS[qid]:
            raise ValueError(f"Frozen V0 question changed: {qid}")
        strong, partial = item["grade_2"], item["grade_1"]
        if len(strong) != len(set(strong)) or len(partial) != len(set(partial)):
            raise ValueError(f"Duplicate grade entry: {qid}")
        if not set(strong).isdisjoint(partial) or not (set(strong) | set(partial)) <= ids:
            raise ValueError(f"Overlapping or ineligible qrel: {qid}")
        grades = {segment_id: 0 for segment_id in roster}
        grades.update({segment_id: 1 for segment_id in partial})
        grades.update({segment_id: 2 for segment_id in strong})
        queries[qid] = {**item, "grades": grades}
    if not queries or data["binary_relevant_at_or_above"] != 1:
        raise ValueError("Empty query set or unexpected binary threshold")
    return data, queries


def evaluate_ranking(ranked_ids, grades, k):
    """Return declared top-k measures; missing slots count nonrelevant for P@k.

    AP@k divides by ALL known relevant segments, even if k is smaller than
    that count. A query with zero positives has undefined recall, F1, RR,
    AP, NDCG and grade-2 recall; it is reported in the no-answer slice.
    """
    if not isinstance(k, int) or k < 1:
        raise ValueError("k must be a positive integer")
    if len(ranked_ids) != len(set(ranked_ids)):
        raise ValueError("Duplicate ID in ranked results")
    if not set(ranked_ids) <= set(grades):
        raise ValueError("Ranking contains an ineligible or unjudged ID")
    top = ranked_ids[:k]
    n_rel = sum(grade >= 1 for grade in grades.values())
    n_direct = sum(grade == 2 for grade in grades.values())
    hits = direct_hits = 0
    rr = ap_numerator = dcg = 0.0
    for rank, segment_id in enumerate(top, 1):
        grade = grades[segment_id]
        dcg += (2 ** grade - 1) / math.log2(rank + 1)
        if grade >= 1:
            hits += 1
            if rr == 0:
                rr = 1 / rank
            ap_numerator += hits / rank
        if grade == 2:
            direct_hits += 1
    ideal = sorted(grades.values(), reverse=True)[:k]
    idcg = sum((2 ** grade - 1) / math.log2(rank + 1)
               for rank, grade in enumerate(ideal, 1))
    precision = hits / k
    recall = hits / n_rel if n_rel else None
    f1 = ((2 * precision * recall / (precision + recall))
          if recall is not None and precision + recall > 0 else
          (0.0 if recall is not None else None))
    return {
        "k": k,
        "retrieved_count": len(top),
        "relevant_count": n_rel,
        "direct_count": n_direct,
        "binary_hits": hits,
        "direct_hits": direct_hits,
        "precision_at_k": precision,
        "recall_at_k": recall,
        "hit_at_k": (int(hits > 0) if n_rel else None),
        "f1_at_k": f1,
        "rr_at_k": (rr if n_rel else None),
        "ap_at_k": (ap_numerator / n_rel if n_rel else None),
        "dcg_at_k": dcg,
        "idcg_at_k": idcg,
        "ndcg_at_k": (dcg / idcg if idcg else None),
        "direct_recall_at_k": (direct_hits / n_direct if n_direct else None),
        "all_direct_at_k": (direct_hits == n_direct if n_direct else None),
        "no_positive_candidate_returned": (bool(top) if n_rel == 0 else None),
    }


def nearest_rank(values, p):
    if not values or not 0 < p <= 1:
        raise ValueError("Nonempty values and p in (0,1] required")
    ordered = sorted(values)
    return ordered[math.ceil(p * len(ordered)) - 1]


def summarize(per_query):
    """Macro query means, micro recall and zero-positive false-candidate rate."""
    positive = [row for row in per_query if row["relevant_count"] > 0]
    zero = [row for row in per_query if row["relevant_count"] == 0]
    if not positive:
        raise ValueError("At least one positive query is required for a macro score")
    fields = ("precision_at_k", "recall_at_k", "hit_at_k", "f1_at_k",
              "rr_at_k", "ap_at_k", "ndcg_at_k", "direct_recall_at_k",
              "all_direct_at_k")
    macro = {}
    for field in fields:
        values = [row[field] for row in positive if row[field] is not None]
        macro[field] = statistics.mean(values) if values else None
    return {
        "positive_queries": len(positive),
        "zero_positive_queries": len(zero),
        "macro_positive_query_mean": macro,
        "micro_recall_at_k": (sum(row["binary_hits"] for row in positive)
                              / sum(row["relevant_count"] for row in positive)),
        "zero_positive_candidate_rate": (statistics.mean(
            int(row["no_positive_candidate_returned"]) for row in zero)
            if zero else None),
    }


if __name__ == "__main__":
    dataset, qs = load_judgments()
    print(json.dumps({"version": dataset["version"], "queries": len(qs),
                      "eligible_segments": len(dataset["eligible_segment_ids"]),
                      "judged_pairs": len(qs) * len(dataset["eligible_segment_ids"]),
                      "positive_queries": sum(any(g > 0 for g in q["grades"].values())
                                              for q in qs.values())}, indent=2))
