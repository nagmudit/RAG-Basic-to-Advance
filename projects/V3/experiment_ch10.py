"""Chapter 10: compare exact binary lexical vectors with the judged V2 BM25.

This deliberately re-encodes known lexical features in a dense array. It is
not an embedding model and makes no claim of semantic generalization.
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

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "V1"))
sys.path.insert(0, str(HERE.parent / "V2"))
from lexical_index import FROZEN_QUESTIONS, build_context, build_index, load_corpus, stub_answer  # noqa: E402
from bm25 import build_bm25_index, search as bm25_search  # noqa: E402
from eval_ch09 import evaluate_ranking, load_judgments, nearest_rank, summarize  # noqa: E402
from exact_vectors import ExactIndex  # noqa: E402

SEED = 10102026
DEPTHS = (2, 8)
MODES = ("bm25", "binary_cosine")


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def build_binary_index(base):
    """Make a dense, binary vocabulary vector at index time, without learning."""
    vocab = tuple(sorted(base.postings))
    terms_by_ordinal = [set() for _ in base.segments]
    for term, postings in base.postings.items():
        for posting in postings:
            terms_by_ordinal[posting.ordinal].add(term)
    records = [
        {"item_id": segment["segment_id"],
         "vector": [float(term in terms_by_ordinal[i]) for term in vocab],
         "allowed_scopes": segment["allowed_scopes"]}
        for i, segment in enumerate(base.segments)
    ]
    return ExactIndex(records, version=f"ch10-binary-vocab-{base.version}"), vocab


def query_vector(base, vocab, question):
    terms = set(base.analyzer.terms(question))
    return tuple(float(term in terms) for term in vocab)


def vector_search(vector_index, base, vocab, question, k):
    q = query_vector(base, vocab, question)
    if not any(q):
        return [], {"indexed_vectors": len(vector_index.entries),
                    "eligible_vectors": len(base.scope_ordinals["support-team"]),
                    "scored_vectors": 0, "dimension": len(vocab),
                    "coordinate_comparisons": 0, "reason": "zero_in_vocabulary_query"}
    rows, work = vector_index.search(q, scope="support-team", metric="cosine",
                                     top_k=k, plan="heap")
    segments = {part["segment_id"]: part for part in base.segments}
    return [{**segments[row["item_id"]], "score": row["value"]}
            for row in rows], work


def run(trials=11):
    if trials < 1:
        raise ValueError("trials must be positive")
    began = datetime.now(timezone.utc).isoformat()
    corpus = load_corpus()
    base = build_index(corpus)
    bm25 = build_bm25_index(base)
    vectors, vocab = build_binary_index(base)
    dataset, queries = load_judgments(base)
    rng = random.Random(SEED)

    def call(mode, question, k):
        return (bm25_search(bm25, question, scope="support-team", top_k=k)
                if mode == "bm25" else
                vector_search(vectors, base, vocab, question, k))

    cases = []
    for qid, query in queries.items():
        for k in DEPTHS:
            modes = {}
            for mode in MODES:
                candidates, work = call(mode, query["question"], k)
                ids = [row["segment_id"] for row in candidates]
                context, source_words = build_context(candidates, 120)
                context_ids = [row["segment_id"] for row in context]
                direct = set(query["grade_2"])
                if qid in FROZEN_QUESTIONS:
                    _, status, reason, cited = stub_answer(qid, context)
                else:
                    status, reason, cited = None, None, []
                modes[mode] = {
                    "candidate_ids": ids,
                    "candidate_scores_raw": [row["score"] for row in candidates],
                    "ranking_metrics": evaluate_ranking(ids, query["grades"], k),
                    "context_ids": context_ids,
                    "context_source_words": source_words,
                    "context_direct_recall": (len(direct & set(context_ids)) / len(direct)
                                              if direct else None),
                    "stub_status": status, "stub_reason": reason,
                    "stub_supporting_ids": cited,
                    "work": work,
                }
                if any(id_.startswith("D10:") for id_ in ids + context_ids):
                    raise AssertionError("Legal-only source leaked into support-team result")
            for mode in MODES:
                call(mode, query["question"], k)  # warm call, outside timing
            samples = {mode: [] for mode in MODES}
            for _ in range(trials):
                order = list(MODES)
                rng.shuffle(order)
                for mode in order:
                    start = perf_counter_ns()
                    call(mode, query["question"], k)
                    samples[mode].append(round((perf_counter_ns() - start) / 1000, 3))
            for mode in MODES:
                modes[mode]["search_latency_us"] = {
                    "raw": samples[mode],
                    "p50_nearest_rank": nearest_rank(samples[mode], .5),
                    "p95_nearest_rank": nearest_rank(samples[mode], .95),
                }
            cases.append({"query_id": qid, "slice": query["slice"],
                          "origin": query["origin"], "top_k": k, "modes": modes})
    summaries = {}
    for k in DEPTHS:
        summaries[str(k)] = {}
        for mode in MODES:
            selected = [case for case in cases if case["top_k"] == k]
            timing = [sample for case in selected
                      for sample in case["modes"][mode]["search_latency_us"]["raw"]]
            rows = [case["modes"][mode]["ranking_metrics"] for case in selected]
            summaries[str(k)][mode] = {
                **summarize(rows),
                "search_latency_us_equal_query_mix": {
                    "samples": len(timing), "p50_nearest_rank": nearest_rank(timing, .5),
                    "p95_nearest_rank": nearest_rank(timing, .95)},
                "mean_scored_segments": statistics.mean(
                    case["modes"][mode]["work"].get("scored_segments",
                                                          case["modes"][mode]["work"].get("scored_vectors"))
                    for case in selected),
            }
    return {
        "experiment_id": "ch10-v3-exact-binary-vector-v1",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "measurement_window_utc": {"start": began,
                                   "end": datetime.now(timezone.utc).isoformat()},
        "question": "Does changing from V2 BM25 to cosine over exact dense binary lexical features improve judged ranking?",
        "hypothesis": "It improves macro positive-query NDCG@2; exact search scores every eligible vector. This is falsifiable and no speed gain is predicted.",
        "baseline": "V2 exhaustive BM25; k1=1.2, b=0.75",
        "primary_variable": "BM25 term scoring/posting-union execution versus exact cosine of binary title-plus-body term presence",
        "controls": ["V0 source/segment snapshot", "V1 analyzer and fixed vocabulary",
                     "support-team static eligibility", "V2 Chapter 9 frozen qrels/questions",
                     "same top-k and 120-source-word context selection"],
        "representation": "One dense coordinate per sorted V1 vocabulary term, 1 iff title or body contains it; query uses the same analyzer and binary coordinates; no learned model, IDF, or domain adaptation.",
        "zero_query_policy": "If no analyzed query term is in the frozen vocabulary, return no candidates; cosine of the zero vector is undefined.",
        "zero_positive_policy": "Recall, Hit, F1, RR, AP, NDCG and direct recall null/excluded from positive macro; zero-positive candidate rate separate.",
        "metric_policy": "V2 Chapter 9 graded qrels and formulas unchanged; exact cosine is a geometric score, not relevance probability.",
        "corpus_snapshot": corpus["snapshot"], "qrel_version": dataset["version"],
        "query_count": len(queries), "eligible_segments": len(base.scope_ordinals["support-team"]),
        "judged_pairs": len(queries) * len(base.scope_ordinals["support-team"]),
        "vocabulary_dimension": len(vocab), "vector_index_version": vectors.version,
        "hash_policy": "SHA256 of UTF-8 bytes with CRLF canonicalized to LF",
        "corpus_sha256": sha256(HERE.parent / "V0" / "corpus.json"),
        "qrels_sha256": sha256(HERE.parent / "V2" / "judgments_ch09.json"),
        "vector_code_sha256": sha256(HERE / "exact_vectors.py"),
        "experiment_code_sha256": sha256(HERE / "experiment_ch10.py"),
        "seed": SEED, "warm_calls_per_mode_case": 1,
        "trials_per_mode_case": trials,
        "timing": "Search call only; randomized pair order; microseconds from perf_counter_ns; no build, context or stub time. Samples are local, not service tails.",
        "environment": {"python": platform.python_version(),
                        "platform": platform.platform(),
                        "processor": platform.processor()},
        "cases": cases, "summaries": summaries,
        "limitations": ["Single-author tiny qrel set, partly known V0 failures; not held out.",
                        "Binary lexical coordinates do not encode semantic paraphrase.",
                        "Dense Python tuples are intentionally unoptimized; no production latency conclusion.",
                        "Static scope fixture is not authentication or a live ACL service.",
                        "No general generator or answer judgment; V0 stub only for two tasks."],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=HERE / "chapter-10-experiment.json")
    parser.add_argument("--trials", type=int, default=11)
    args = parser.parse_args()
    record = run(args.trials)
    args.output.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "query_count": record["query_count"],
                      "dimension": record["vocabulary_dimension"],
                      "top2": record["summaries"]["2"]}, indent=2))


if __name__ == "__main__":
    main()
