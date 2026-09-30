"""Chapter 12: train a small query tower on frozen embeddings, then test once.

This is a pedagogical domain-adaptation experiment, not full encoder fine-tuning.
Training uses only train-document passages and train queries. Validation selects
one checkpoint. Held-out test-document questions are scored only afterward.
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
from lexical_index import build_context, build_index, load_corpus  # noqa: E402
from bm25 import build_bm25_index, search as bm25_search  # noqa: E402
from eval_ch09 import evaluate_ranking, nearest_rank, summarize  # noqa: E402
from experiment_ch11 import embed, load_encoder, sha256  # noqa: E402

JUDGMENTS = HERE / "judgments_ch12.json"
SEED = 12092026
TOP_K = 2
EPOCHS = 60
TEMPERATURE = 0.12
LEARNING_RATE = 0.04
RANK = 16


def load_split(base, path=JUDGMENTS):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    roster = [base.segments[i]["segment_id"] for i in sorted(base.scope_ordinals["support-team"])]
    if (data["corpus_snapshot"] != base.snapshot or data["scope_fixture"] != "support-team"
            or data["retrieval_unit"] != "indexed_segment"
            or data["eligible_segment_ids"] != roster
            or data["binary_relevant_at_or_above"] != 1):
        raise ValueError("Chapter 12 qrel roster or policy mismatch")
    split = data["document_split"]
    doc_ids = [doc for name in ("train", "validation", "test") for doc in split[name]]
    if len(doc_ids) != len(set(doc_ids)) or set(doc_ids) != {s.split(":")[0] for s in roster}:
        raise ValueError("Document splits must be disjoint and cover eligible documents")
    seen = set()
    for name in ("training_pairs", "validation_queries", "test_queries"):
        group = data[name]
        if not group:
            raise ValueError("Empty split")
        for item in group:
            qid = item["query_id"]
            if qid in seen or not item["question"]:
                raise ValueError("Duplicate or empty query")
            seen.add(qid)
            allowed_docs = set(split["train" if name == "training_pairs" else
                                     "validation" if name == "validation_queries" else "test"])
            if name == "training_pairs":
                if (item["positive_id"] not in roster or
                        item["positive_id"].split(":")[0] not in allowed_docs or
                        not set(item["unsafe_negative_ids"]) <= set(roster) or
                        any(s.split(":")[0] not in allowed_docs
                            for s in item["unsafe_negative_ids"]) or
                        item["positive_id"] in item["unsafe_negative_ids"]):
                    raise ValueError("Training pair crosses split or uses an invalid ID")
                continue
            strong, partial = item["grade_2"], item["grade_1"]
            if (len(strong) != len(set(strong)) or len(partial) != len(set(partial)) or
                    not set(strong).isdisjoint(partial) or
                    not set(strong + partial) <= set(roster) or
                    any(s.split(":")[0] not in allowed_docs for s in strong + partial) or
                    (item["slice"] == "no_eligible_evidence") != (not strong and not partial) or
                    not item["rationale"]):
                raise ValueError("Invalid or split-crossing qrel")
            item["grades"] = {sid: 2 if sid in strong else 1 if sid in partial else 0
                              for sid in roster}
    return data


def adapt_query(vector, a, b):
    import torch
    adjusted = vector + (vector @ a.T) @ b.T
    return torch.nn.functional.normalize(adjusted, dim=-1)


def rank_dense(query, passages, roster, a=None, b=None):
    import torch
    with torch.no_grad():
        q = adapt_query(query, a, b) if a is not None else query
        scores = (passages @ q).tolist()
    pairs = sorted(zip(roster, scores), key=lambda pair: (-pair[1], pair[0]))
    return pairs


def train_adapter(data, embeddings, roster):
    import torch
    torch.manual_seed(SEED)
    train_ids = [sid for sid in roster if sid.split(":")[0] in data["document_split"]["train"]]
    passage = torch.stack([embeddings["passages"][sid] for sid in train_ids])
    pairs = data["training_pairs"]
    queries = torch.stack([embeddings["queries"][item["query_id"]] for item in pairs])
    targets = torch.tensor([train_ids.index(item["positive_id"]) for item in pairs])
    mask = torch.zeros((len(pairs), len(train_ids)), dtype=torch.bool)
    for row, item in enumerate(pairs):
        for sid in item["unsafe_negative_ids"]:
            if sid in train_ids:
                mask[row, train_ids.index(sid)] = True
        assert not mask[row, targets[row]]
    a = torch.nn.Parameter(torch.randn(RANK, 384) * 0.01)
    b = torch.nn.Parameter(torch.zeros(384, RANK))
    optimizer = torch.optim.Adam([a, b], lr=LEARNING_RATE)
    best = None
    history = []
    for epoch in range(1, EPOCHS + 1):
        optimizer.zero_grad()
        q = adapt_query(queries, a, b)
        logits = q @ passage.T / TEMPERATURE
        loss = torch.nn.functional.cross_entropy(logits.masked_fill(mask, -1e9), targets)
        # A small norm cost resists unconstrained movement on only ten pairs.
        loss = loss + 0.01 * ((a.T @ b.T) ** 2).mean()
        loss.backward()
        optimizer.step()
        if epoch in (1, 5, 10, 20, 40, 60):
            metrics = score_group(data["validation_queries"], embeddings, roster, a, b)
            quality = metrics["summary"]["macro_positive_query_mean"]
            key = (quality["ndcg_at_k"], quality["recall_at_k"], -epoch)
            history.append({"epoch": epoch, "train_loss": round(float(loss.item()), 6),
                            "validation_ndcg_at_2": quality["ndcg_at_k"],
                            "validation_recall_at_2": quality["recall_at_k"]})
            if best is None or key > best[0]:
                best = (key, epoch, a.detach().clone(), b.detach().clone())
    _, epoch, best_a, best_b = best
    weights = best_a.numpy().tobytes() + best_b.numpy().tobytes()
    return best_a, best_b, epoch, history, hashlib.sha256(weights).hexdigest(), int((~mask).sum()) - len(pairs)


def score_group(items, embeddings, roster, a=None, b=None, bm25=None, base=None):
    passages = embeddings["passage_matrix"]
    cases = []
    for item in items:
        if bm25 is None:
            pairs = rank_dense(embeddings["queries"][item["query_id"]], passages, roster, a, b)
            candidate_ids = [sid for sid, _ in pairs[:TOP_K]]
            raw_scores = [score for _, score in pairs[:TOP_K]]
        else:
            rows, _ = bm25_search(bm25, item["question"], scope="support-team", top_k=TOP_K)
            candidate_ids = [row["segment_id"] for row in rows]
            raw_scores = [row["score"] for row in rows]
        if any(sid.startswith("D10:") for sid in candidate_ids):
            raise AssertionError("Ineligible segment entered candidates")
        segments = {segment["segment_id"]: segment for segment in base.segments} if base else None
        context_ids = None
        if segments is not None:
            candidates = [{**segments[sid], "score": score}
                          for sid, score in zip(candidate_ids, raw_scores)]
            context, _ = build_context(candidates, 120)
            context_ids = [row["segment_id"] for row in context]
        cases.append({"query_id": item["query_id"], "slice": item["slice"],
                      "candidate_ids": candidate_ids, "candidate_scores_raw": raw_scores,
                      "context_ids": context_ids,
                      "ranking_metrics": evaluate_ranking(candidate_ids, item["grades"], TOP_K),
                      "generation_status": None})
    slices = {}
    for slice_name in sorted({item["slice"] for item in items}):
        subset = [case for case in cases if case["slice"] == slice_name]
        if subset[0]["ranking_metrics"]["relevant_count"]:
            slices[slice_name] = summarize([case["ranking_metrics"] for case in subset])
        else:
            slices[slice_name] = {
                "queries": len(subset),
                "candidate_return_rate": sum(bool(case["candidate_ids"]) for case in subset) / len(subset),
            }
    return {"cases": cases, "summary": summarize([c["ranking_metrics"] for c in cases]),
            "by_slice": slices}


def run(*, allow_download=False, trials=5):
    if trials < 1:
        raise ValueError("trials must be positive")
    import torch
    started = datetime.now(timezone.utc).isoformat()
    corpus = load_corpus()
    base = build_index(corpus)
    data = load_split(base)  # validated before model execution
    roster = data["eligible_segment_ids"]
    bm25 = build_bm25_index(base)
    model, model_info = load_encoder(allow_download=allow_download)
    segments = {segment["segment_id"]: segment for segment in base.segments}
    build_start = perf_counter_ns()
    passage_vectors = embed(model, [segments[sid]["title"] + "\n" + segments[sid]["text"]
                                    for sid in roster], batch_size=16)
    passage_build_ms = (perf_counter_ns() - build_start) / 1e6
    selection_items = data["training_pairs"] + data["validation_queries"]
    query_vectors = embed(model, [item["question"] for item in selection_items], batch_size=16)
    embeddings = {"passages": {sid: torch.tensor(vector) for sid, vector in zip(roster, passage_vectors)},
                  "passage_matrix": torch.tensor(passage_vectors),
                  "queries": {item["query_id"]: torch.tensor(vector)
                              for item, vector in zip(selection_items, query_vectors)}}
    train_start = perf_counter_ns()
    a, b, selected_epoch, history, adapter_hash, usable_negatives = train_adapter(data, embeddings, roster)
    train_ms = (perf_counter_ns() - train_start) / 1e6
    validation = {name: score_group(data["validation_queries"], embeddings, roster, *weights,
                                    base=base)
                  for name, weights in {"frozen": (None, None), "adapted": (a, b)}.items()}
    # Even test query encoding waits until the checkpoint is chosen. Test passage
    # vectors are in the index throughout, as they must be for retrieval.
    test_vectors = embed(model, [item["question"] for item in data["test_queries"]],
                         batch_size=16)
    embeddings["queries"].update({item["query_id"]: torch.tensor(vector)
                                  for item, vector in zip(data["test_queries"], test_vectors)})
    # Only now evaluate the held-out test queries; no test labels enter training or checkpoint choice.
    test = {name: score_group(data["test_queries"], embeddings, roster, *weights,
                              bm25=bm25 if name == "bm25" else None, base=base)
            for name, weights in {"bm25": (None, None), "frozen": (None, None),
                                  "adapted": (a, b)}.items()}
    timings = {}
    rng = random.Random(SEED)
    for name in ("bm25", "frozen", "adapted"):
        samples = []
        slice_samples = {}
        items = list(data["test_queries"])
        for _ in range(trials):
            rng.shuffle(items)
            for item in items:
                # Inference boundary: model query encoding plus scoring for dense;
                # model load, passage build and context are excluded.
                if name == "bm25":
                    bm25_search(bm25, item["question"], scope="support-team", top_k=TOP_K)
                    tick = perf_counter_ns()
                    bm25_search(bm25, item["question"], scope="support-team", top_k=TOP_K)
                else:
                    embed(model, [item["question"]], batch_size=1)
                    tick = perf_counter_ns()
                    q = torch.tensor(embed(model, [item["question"]], batch_size=1)[0])
                    rank_dense(q, embeddings["passage_matrix"], roster,
                               a if name == "adapted" else None,
                               b if name == "adapted" else None)
                elapsed = round((perf_counter_ns() - tick) / 1000, 3)
                samples.append(elapsed)
                slice_samples.setdefault(item["slice"], []).append(elapsed)
        timings[name] = {"samples_us": samples, "p50_us": nearest_rank(samples, .5),
                         "p95_us": nearest_rank(samples, .95),
                         "by_slice": {slice_name: {"samples": len(values),
                                                   "p50_us": nearest_rank(values, .5),
                                                   "p95_us": nearest_rank(values, .95)}
                                      for slice_name, values in slice_samples.items()}}
    return {
        "experiment_id": "ch12-v3-query-adapter-v1", "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "measurement_window_utc": {"start": started, "end": datetime.now(timezone.utc).isoformat()},
        "question": "Does a small domain-trained query adapter improve retrieval of held-out source documents over the frozen encoder?",
        "hypothesis": "Macro held-out Recall@2 improves over frozen while no-evidence candidate behavior remains visible; a regression is acceptable.",
        "acceptance_gate": "Keep the adapter only if held-out positive-query Recall@2 exceeds frozen without a validation or no-evidence regression; this small set is diagnostic, not a production release gate.",
        "baseline": "Chapter 11 pinned frozen sentence encoder with exact cosine; V2 BM25 is a lexical reference",
        "primary_variable": "A trained rank-16 residual projection on query vectors; document encoder and exact scorer remain frozen",
        "controls": ["unchanged V0 corpus and support-team eligibility", "same 384d base encoder, title/body passage format, normalization, exact cosine and tie order", "source-disjoint train/validation/test query targets", "same complete 12-segment qrel roster, top-2, context word budget"],
        "judgment_policy": data["review_method"], "qrel_policy": data["zero_policy"],
        "procedure": "Validate frozen split/roster; encode eligible passages and train/validation queries; train only on train-document pairs with unsafe negatives masked; choose epoch by validation NDCG@2 then Recall@2; encode and score test queries once; compare BM25, frozen and adapted with fixed top-2/context policy; warm and time local queries.",
        "model": model_info, "corpus_snapshot": corpus["snapshot"], "qrel_version": data["version"],
        "index_version": base.version,
        "document_split": data["document_split"], "training_pairs": len(data["training_pairs"]),
        "validation_queries": len(data["validation_queries"]), "test_queries": len(data["test_queries"]),
        "test_judged_pairs": len(data["test_queries"]) * len(roster),
        "training": {"seed": SEED, "epochs": EPOCHS, "selected_epoch": selected_epoch,
                     "rank": RANK, "temperature": TEMPERATURE, "learning_rate": LEARNING_RATE,
                     "optimizer": "Adam", "loss": "masked row softmax cross entropy plus 0.01 mean squared residual projection",
                     "negative_policy": "All other train-document passages except listed potentially relevant neighbors; validation/test documents never mined or used as negatives",
                     "usable_query_negative_pairs": usable_negatives, "history": history,
                     "adapter_sha256": adapter_hash, "adapter_parameters": 2 * 384 * RANK,
                     "train_ms": round(train_ms, 3)},
        "passage_build_ms": round(passage_build_ms, 3),
        "validation": validation, "test": test, "test_timing": timings,
        "timing_policy": "5 warmed CPU samples per test query/method, method-specific query encode plus exact score or BM25 search; excludes model load, passage build, training and context. Local microbenchmarks are not production tails.",
        "candidate_context_answer_policy": "Candidate IDs/scores, selected context IDs and absent generation labels are separate. No answer generator was run on the new split.",
        "failure_examples": ["te-atlas-b: all three routes omit the signed Atlas contract from top two; dense routes choose observed incident and unsigned draft", "te-none-a and te-none-b: every route returns candidates despite no eligible evidence", "later adapter checkpoints fit train pairs while validation Recall@2 falls to zero"],
        "conclusion": "The selected adapter ties the frozen encoder on held-out Recall@2 and NDCG@2; the hypothesized gain is not observed.",
        "decision": "Reject the adapter as a replacement on this evidence; preserve it as a training and over-specialization demonstration.",
        "hash_policy": "SHA256 UTF-8 bytes with CRLF normalized to LF",
        "corpus_sha256": sha256(HERE.parent / "V0" / "corpus.json"),
        "qrels_sha256": sha256(JUDGMENTS), "experiment_code_sha256": sha256(HERE / "experiment_ch12.py"),
        "environment": {"python": platform.python_version(), "platform": platform.platform(),
                        "torch": torch.__version__},
        "limitations": ["One author created and graded all fictional questions while knowing the source facts and prior failures; no independent assessment.", "Ten authored training queries and nine positive held-out test queries span only three test documents; no statistical generalization claim.", "Source-disjoint targets prevent document-identity leakage but test documents are still embedded into the retrieval index as production would require; related Helios wording crosses documents.", "Only a query-side low-rank adapter is trained; the transformer and passage encoder are frozen, so this is not full dual-encoder fine-tuning.", "The English-only fixture cannot measure multilingual or cross-lingual transfer.", "No answer generator runs; answer quality, calibration, live authorization, ANN scale and production latency remain untested."]
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--allow-download", action="store_true")
    parser.add_argument("--trials", type=int, default=5)
    parser.add_argument("--output", type=Path, default=HERE / "chapter-12-experiment-local.json")
    args = parser.parse_args()
    result = run(allow_download=args.allow_download, trials=args.trials)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "selected_epoch": result["training"]["selected_epoch"],
                      "test": {name: group["summary"]["macro_positive_query_mean"]["recall_at_k"]
                               for name, group in result["test"].items()}}, ensure_ascii=False))
