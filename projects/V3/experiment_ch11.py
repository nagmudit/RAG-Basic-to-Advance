"""Chapter 11: frozen sentence encoder versus V2 BM25 on new judged probes.

No weights are trained or changed. Load a pinned public model from the local
cache by default; pass --allow-download explicitly to fetch the pinned revision.
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

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "V1"))
sys.path.insert(0, str(HERE.parent / "V2"))
from lexical_index import build_context, build_index, load_corpus  # noqa: E402
from bm25 import build_bm25_index, search as bm25_search  # noqa: E402
from eval_ch09 import evaluate_ranking, nearest_rank, summarize  # noqa: E402
from exact_vectors import ExactIndex  # noqa: E402

MODEL_ID = "sentence-transformers/all-MiniLM-L6-v2"
MODEL_REVISION = "8b3219a92973c328a8e22fadcfa821b5dc75636a"
DATASET_PATH = HERE / "judgments_ch11.json"
SEED = 11092026
DEPTHS = (2, 8)
MODES = ("bm25", "frozen_encoder")


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def load_judgments(base, path=DATASET_PATH):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if (data["corpus_snapshot"] != base.snapshot or
            data["scope_fixture"] != "support-team" or
            data["retrieval_unit"] != "indexed_segment" or
            data["binary_relevant_at_or_above"] != 1):
        raise ValueError("Judgment snapshot, scope, unit or threshold mismatch")
    roster = [base.segments[i]["segment_id"]
              for i in sorted(base.scope_ordinals["support-team"])]
    if data["eligible_segment_ids"] != roster or len(roster) != len(set(roster)):
        raise ValueError("Judgment roster differs from eligible index")
    queries = {}
    for item in data["queries"]:
        qid = item["query_id"]
        if qid in queries or not item.get("question") or not item.get("rationale"):
            raise ValueError("Duplicate or incomplete query")
        if item["slice"] not in ("paraphrase", "exact_identifier", "no_eligible_evidence"):
            raise ValueError("Unknown query slice")
        strong, partial = item["grade_2"], item["grade_1"]
        if (len(strong) != len(set(strong)) or len(partial) != len(set(partial)) or
                not set(strong).isdisjoint(partial) or
                not (set(strong) | set(partial)) <= set(roster)):
            raise ValueError("Duplicate, overlapping or ineligible qrel")
        if (item["slice"] == "no_eligible_evidence") != (not strong and not partial):
            raise ValueError("No-evidence slice contradicts qrels")
        grades = {segment_id: 0 for segment_id in roster}
        grades.update({segment_id: 1 for segment_id in partial})
        grades.update({segment_id: 2 for segment_id in strong})
        queries[qid] = {**item, "grades": grades}
    if len(queries) != 17:
        raise ValueError("Frozen Chapter 11 probe must have seventeen queries")
    return data, queries


def load_encoder(*, allow_download=False):
    import sentence_transformers
    import torch
    import transformers
    from sentence_transformers import SentenceTransformer

    torch.set_num_threads(2)
    started = perf_counter_ns()
    try:
        model = SentenceTransformer(MODEL_ID, revision=MODEL_REVISION, device="cpu",
                                    local_files_only=not allow_download)
    except Exception as exc:
        raise RuntimeError(
            "Pinned model unavailable. Install sentence-transformers and rerun "
            "with --allow-download once, or place the pinned revision in the "
            "local Hugging Face cache."
        ) from exc
    model.eval()
    if model.get_sentence_embedding_dimension() != 384:
        raise ValueError("Unexpected embedding dimension for pinned checkpoint")
    return model, {
        "model_id": MODEL_ID, "model_revision": MODEL_REVISION,
        "dimension": 384, "max_sequence_length_wordpieces": model.max_seq_length,
        "device": "cpu", "torch_threads": torch.get_num_threads(),
        "sentence_transformers_version": sentence_transformers.__version__,
        "transformers_version": transformers.__version__,
        "torch_version": torch.__version__,
        "load_ms": round((perf_counter_ns() - started) / 1e6, 3),
        "encode_policy": "title newline segment text; one shared frozen encoder for questions and passages; normalized float32 sentence embeddings; no instruction prefixes",
    }


def embed(model, texts, *, batch_size):
    vectors = model.encode(texts, batch_size=batch_size, show_progress_bar=False,
                           convert_to_numpy=True, normalize_embeddings=True)
    if len(vectors) != len(texts) or vectors.shape[1] != 384:
        raise ValueError("Unexpected encoded shape")
    out = [tuple(float(value) for value in row) for row in vectors]
    if any(not all(math.isfinite(value) for value in row) for row in out):
        raise ValueError("Nonfinite embedding")
    return out


def build_dense_index(base, model):
    started = perf_counter_ns()
    texts = [segment["title"] + "\n" + segment["text"] for segment in base.segments]
    vectors = embed(model, texts, batch_size=16)
    records = [
        {"item_id": segment["segment_id"], "vector": vector,
         "allowed_scopes": segment["allowed_scopes"]}
        for segment, vector in zip(base.segments, vectors)
    ]
    index = ExactIndex(records, version=f"ch11-{MODEL_REVISION[:12]}-{base.version}")
    return index, round((perf_counter_ns() - started) / 1e6, 3)


def dense_search(index, base, query_vector, k):
    rows, work = index.search(query_vector, scope="support-team",
                              metric="cosine", top_k=k, plan="heap")
    segments = {part["segment_id"]: part for part in base.segments}
    return [{**segments[row["item_id"]], "score": row["value"]}
            for row in rows], work


def run(*, trials=7, allow_download=False):
    if not isinstance(trials, int) or trials < 1:
        raise ValueError("trials must be positive")
    began = datetime.now(timezone.utc).isoformat()
    corpus = load_corpus()
    base = build_index(corpus)
    bm25 = build_bm25_index(base)
    dataset, queries = load_judgments(base)  # freeze judgments before model load
    model, model_info = load_encoder(allow_download=allow_download)
    dense, dense_build_ms = build_dense_index(base, model)
    rng = random.Random(SEED)
    cases = []
    for qid, item in queries.items():
        question = item["question"]
        query_vector = embed(model, [question], batch_size=1)[0]
        for k in DEPTHS:
            modes = {}
            for mode in MODES:
                candidates, work = (bm25_search(bm25, question, scope="support-team", top_k=k)
                                    if mode == "bm25" else
                                    dense_search(dense, base, query_vector, k))
                ids = [row["segment_id"] for row in candidates]
                context, source_words = build_context(candidates, 120)
                context_ids = [row["segment_id"] for row in context]
                direct = set(item["grade_2"])
                if any(id_.startswith("D10:") for id_ in ids + context_ids):
                    raise AssertionError("Legal-only candidate entered support-team result")
                modes[mode] = {
                    "candidate_ids": ids,
                    "candidate_scores_raw": [row["score"] for row in candidates],
                    "ranking_metrics": evaluate_ranking(ids, item["grades"], k),
                    "context_ids": context_ids,
                    "context_source_words": source_words,
                    "context_direct_recall": (len(direct & set(context_ids)) / len(direct)
                                              if direct else None),
                    "generation_status": None,
                    "work": work,
                }
            # One untimed warm call per method/case. Dense query encoding is
            # measured independently from exact vector scan in later trials.
            bm25_search(bm25, question, scope="support-team", top_k=k)
            dense_search(dense, base, embed(model, [question], batch_size=1)[0], k)
            samples = {"bm25_search_us": [], "dense_encode_us": [],
                       "dense_scan_us": [], "dense_total_us": []}
            for _ in range(trials):
                order = list(MODES)
                rng.shuffle(order)
                for mode in order:
                    if mode == "bm25":
                        start = perf_counter_ns()
                        bm25_search(bm25, question, scope="support-team", top_k=k)
                        samples["bm25_search_us"].append(
                            round((perf_counter_ns() - start) / 1000, 3))
                    else:
                        start = perf_counter_ns()
                        vector = embed(model, [question], batch_size=1)[0]
                        encoded = perf_counter_ns()
                        dense_search(dense, base, vector, k)
                        finished = perf_counter_ns()
                        samples["dense_encode_us"].append(round((encoded - start) / 1000, 3))
                        samples["dense_scan_us"].append(round((finished - encoded) / 1000, 3))
                        samples["dense_total_us"].append(round((finished - start) / 1000, 3))
            modes["bm25"]["search_latency_us"] = samples["bm25_search_us"]
            modes["frozen_encoder"]["query_encode_latency_us"] = samples["dense_encode_us"]
            modes["frozen_encoder"]["exact_scan_latency_us"] = samples["dense_scan_us"]
            modes["frozen_encoder"]["encode_plus_scan_latency_us"] = samples["dense_total_us"]
            cases.append({"query_id": qid, "slice": item["slice"],
                          "top_k": k, "modes": modes})

    summaries = {}
    for k in DEPTHS:
        selected = [case for case in cases if case["top_k"] == k]
        summaries[str(k)] = {}
        for mode in MODES:
            rows = [case["modes"][mode]["ranking_metrics"] for case in selected]
            timing_key = ("search_latency_us" if mode == "bm25" else
                          "encode_plus_scan_latency_us")
            times = [sample for case in selected for sample in case["modes"][mode][timing_key]]
            by_slice = {}
            for slice_name in ("paraphrase", "exact_identifier"):
                subset = [case["modes"][mode]["ranking_metrics"] for case in selected
                          if case["slice"] == slice_name]
                by_slice[slice_name] = summarize(subset)
            no_answer = [case for case in selected if case["slice"] == "no_eligible_evidence"]
            by_slice["no_eligible_evidence"] = {
                "queries": len(no_answer),
                "candidate_return_rate": statistics.mean(
                    bool(case["modes"][mode]["candidate_ids"]) for case in no_answer),
            }
            summaries[str(k)][mode] = {
                **summarize(rows), "by_slice": by_slice,
                "timed_search_or_encode_plus_scan_us": {
                    "samples": len(times), "p50_nearest_rank": nearest_rank(times, .5),
                    "p95_nearest_rank": nearest_rank(times, .95)},
                "mean_fully_scored_eligible_segments": statistics.mean(
                    case["modes"][mode]["work"].get("scored_segments",
                                                          case["modes"][mode]["work"].get("scored_vectors"))
                    for case in selected),
            }
    return {
        "experiment_id": "ch11-v3-frozen-encoder-v1",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "measurement_window_utc": {"start": began,
                                   "end": datetime.now(timezone.utc).isoformat()},
        "question": "Does one frozen sentence encoder retrieve newly worded paraphrases better than V2 BM25, and what happens to exact identifiers and no-answer probes?",
        "hypothesis": "Macro Recall@2 on the paraphrase slice improves over BM25; exact-identifier performance may regress. No universal gain is predicted.",
        "baseline": "V2 exhaustive BM25 with k1=1.2, b=0.75 on the unchanged V1 title/body index",
        "primary_variable": "BM25 lexical scoring/posting-union versus frozen shared sentence encoder + exact cosine scan of title and segment text",
        "controls": ["V0 corpus and segment IDs", "support-team static eligibility",
                     "17 newly judged questions and complete 12-segment roster",
                     "same top-k, 120-source-word context builder and graded qrel metric formulas",
                     "no trained or adapted weights in this repository"],
        "judgment_policy": dataset["review_method"],
        "qrel_policy": dataset["zero_policy"],
        "zero_positive_policy": "Recall, Hit, F1, RR, AP, NDCG and direct recall are undefined on zero-positive queries; report candidate-return rate separately.",
        "candidate_context_answer_policy": "Ranked candidates and selected context are logged separately. No generator runs for these 17 new questions; answer-quality labels are absent.",
        "corpus_snapshot": corpus["snapshot"], "qrel_version": dataset["version"],
        "query_count": len(queries), "eligible_segments": len(base.scope_ordinals["support-team"]),
        "judged_pairs": len(queries) * len(base.scope_ordinals["support-team"]),
        "model": model_info, "vector_index_version": dense.version,
        "dense_index_encode_and_build_ms": dense_build_ms,
        "bm25_postings_build_ms": round(base.build_ms, 3),
        "bm25_statistics_build_ms": round(bm25.statistics_build_ms, 3),
        "source_text_policy": "Both retrievers use title and the same V0 segment body; neither indexes segment ID, source status, or effective date as a separate field.",
        "hash_policy": "SHA256 of UTF-8 bytes with CRLF canonicalized to LF",
        "corpus_sha256": sha256(HERE.parent / "V0" / "corpus.json"),
        "qrels_sha256": sha256(DATASET_PATH),
        "vector_code_sha256": sha256(HERE / "exact_vectors.py"),
        "experiment_code_sha256": sha256(HERE / "experiment_ch11.py"),
        "seed": SEED, "warm_calls_per_mode_case": 1,
        "trials_per_mode_case": trials,
        "timing": "CPU, one query per model encode, randomized method order, search-only BM25 versus dense query encode plus exact scan; model load, index build and context outside request timing; microseconds and nearest-rank percentiles. Small local samples are not production tails.",
        "environment": {"python": platform.python_version(),
                        "platform": platform.platform(), "processor": platform.processor()},
        "cases": cases, "summaries": summaries,
        "limitations": ["One author judged and wrote new fictional questions while knowing the corpus; no independent assessor or external validity.",
                        "Frozen pretrained model is a general sentence encoder, not a domain-trained query/passage pair.",
                        "The two methods use different scoring and representation together; causal attribution is limited.",
                        "Literal segment IDs are absent from both searchable text representations; neither tests a dedicated ID route.",
                        "No answer generator, human answer labels or claim-support evaluation for the new questions.",
                        "Static support-team scope is a fixture, not authentication; no live ACL changes.",
                        "The tiny Python exact scan and one CPU/model version do not predict production p95 or scaled ANN behavior."],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=HERE / "chapter-11-experiment.json")
    parser.add_argument("--trials", type=int, default=7)
    parser.add_argument("--allow-download", action="store_true")
    args = parser.parse_args()
    record = run(trials=args.trials, allow_download=args.allow_download)
    args.output.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    summary = record["summaries"]["2"]
    print(json.dumps({"output": str(args.output), "model_revision": MODEL_REVISION,
                      "judged_pairs": record["judged_pairs"],
                      "top2": {name: {
                          "macro_ndcg": row["macro_positive_query_mean"]["ndcg_at_k"],
                          "paraphrase_recall": row["by_slice"]["paraphrase"]
                          ["macro_positive_query_mean"]["recall_at_k"],
                          "identifier_recall": row["by_slice"]["exact_identifier"]
                          ["macro_positive_query_mean"]["recall_at_k"],
                          "p50_us": row["timed_search_or_encode_plus_scan_us"]
                          ["p50_nearest_rank"]} for name, row in summary.items()}},
                     indent=2))


if __name__ == "__main__":
    main()
