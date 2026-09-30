# Chapter 12 lab — worked solutions

Try the [lab](../labs/chapter-12/LAB.md) before reading this page. The numerical measurements below are from the checked-in 2026-09-30 CPU run; small timing differences are expected.

## A. Split and label audit

Train source documents are D1, D2, D4, D6; validation D3, D7; test D5, D8, D9. These sets are disjoint. The indexed support-team roster contains 12 segments. Ten authored training pairs target five train segments. Four validation and 11 test questions each have all 12 eligible segments reviewed, giving `(4+11)×12=180` reviewed pairs. D10 is legal-only, so its eligibility is false before scoring; treating it as a grade-zero support-team negative would confuse authorization with relevance.

The runbook windows overlap in subject and sometimes in source text: `D4:step-4:0` ends near the configuration instruction and `D4:step-4:2` continues the incident procedure. They require review before being repelled from `tr-change-a`. The older signed D1 response clause can explain what the D2 amendment replaces; it is potentially useful history, even if D2 is the direct answer. D6's price row is a safe irrelevant example for a runbook or amendment query; D1's termination clause is an irrelevant example for a price query. A BM25 hit could be the exact current clause, a useful historical clause, or a wrong product. Rank alone cannot label it.

Keep all revisions of one agreement and translated copies of the same source family on one side of a split. Chapter 11's questions and failures were already inspected, so they are regression probes, not a clean test for selecting Chapter 12 settings.

## B. Objective arithmetic

The logits are `0.8/0.2=4`, `0.6/0.2=3`, `0.2/0.2=1`. The positive probability is `e^4/(e^4+e^3+e^1)≈0.705`, and `−ln(0.705)≈0.349` nats. The triplet violation is `max(0,0.3−0.8+0.6)=0.1`. If `0.6` belongs to a relevant passage, masking it or using a multi-positive objective avoids training against a valid result.

## C. Reproduction and selection

The runner first validates source IDs, the qrel roster and split ownership. It embeds all eligible passages because the retrieval index must contain test sources to retrieve them. It trains on query labels and seven passage vectors from train documents only. Validation labels choose epoch 1; only then does it encode test questions and read their labels for final metrics. The checked-in manifest and experiment hashes make changes detectable.

## D. Result and failure trace

| Method | Positive-query Recall@2 | NDCG@2 | No-evidence candidate rate |
|---|---:|---:|---:|
| BM25 | 0.667 | 0.667 | 2/2 |
| Frozen encoder | 0.889 | 0.807 | 2/2 |
| Selected adapter | 0.889 | 0.807 | 2/2 |

The held-out gain hypothesis fails. Epoch 1 training loss is about `0.249` with validation Recall@2 `1.0` and NDCG@2 `0.723`; epoch 5 training loss is about `0.013` while both validation metrics are `0`. Training loss alone would favor the harmful checkpoint. This is enough to reject a claim of improvement, though the tiny validation and test cannot establish a general performance difference.

The three positive-query slices each have only three questions. BM25 Basic/Atlas/draft Recall@2 is `2/3`, `2/3`, `2/3`; both frozen and selected adapted are `3/3`, `2/3`, `3/3`. The record has p50/p95 request-boundary timing for each slice, with 15 warm samples for a three-question slice and ten for the two-question no-evidence slice. Those sample sizes are for debugging only.

`te-atlas-b` asks which **signed** contract sets a two-hour Sev-1 first response. Its direct qrel is `D8:§3:0` (Atlas signed agreement). BM25 returns `D9:proposal-2:0`, `D2:§2:0`; frozen and adapted return `D7:timeline:0`, `D9:proposal-2:0`. D7 is an observed response, D9 is unsigned, and D2 is a signed Helios amendment for one hour. None of these top-two sets contains D8. Selected context IDs are logged separately and cannot repair a missing candidate. No answer is generated on these Chapter 12 queries, so no answer-quality claim follows. D10 is absent before similarity scoring.

The adapter has `2×384×16=12,288` float32 parameters, or `49,152` bytes (`48 KiB`) without optimizer state. The checked-in p50 request-boundary measurements are approximately 22.1 µs for BM25 search, 7,902 µs for frozen model query encoding plus exact scoring, and 8,154 µs for adapted encoding plus scoring. They exclude model load, passage build, training and context; five warm local samples per test query cannot estimate deployed p95 or cross-machine cost.

The next experiment should group revisions and translations by source family, collect more independently written queries, judge a pooled BM25/dense/reranker candidate set, and include wrong-entity, exact-ID, negative-evidence and no-result slices. Use train labels for gradients, validation labels for hyperparameters and threshold calibration, and one sealed test for release comparison. A multilingual claim requires a multilingual model plus native-language qrels; cross-lingual claims need explicit source/target language directions and reviewed answers. Until a relevant improvement survives that design, keep the frozen encoder and BM25 route rather than ship this adapter.
