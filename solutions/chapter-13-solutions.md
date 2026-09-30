# Chapter 13 lab — worked solutions

Try the [lab](../labs/chapter-13/LAB.md) before reading this page. The measurements below are from the checked-in 2026-09-30 CPU run; timing can change on replay.

## A. Source, index and metric

The V0 snapshot has 13 indexed segments; the support-team fixture may score 12. The model emits 384 coordinates. Thirteen float32 rows use `13×384×4=19,968` raw bytes, excluding manifest, source text, Python objects, model weights, runtime and backups. Fourteen new questions times 12 eligible segments give 168 reviewed query–segment pairs. The manifest binds source snapshot, ordered IDs, source-text digests, scopes, model ID/revision, shared encoder roles, input format, normalization, dimension, metric, tie rule, vector length and SHA256. The loader rejects any changed row, text or revision before search. D10 is indexed with `legal-team` scope but absent from support-team scoring and qrels.

For `q=(1,0)`, `a=(.8,.6)` has norm 1 and `q·a=.8`, so cosine `.8`. `b=(7,7)` has norm `√98≈9.899`; `q·b=7`, cosine `7/√98≈.707`. Raw dot picks `b`; cosine picks `a`. The real snapshot requires near-unit passage vectors and normalized model query vectors. Dot and cosine are rank-equivalent only under that compatible normalization, aside from floating-point/tie effects.

`acronym-sla` asks for current target: D2's signed amendment is grade 2; D1's old signed clause is grade 1 historical context. `code-segment` targets D6's metadata ID, which is absent from title/body text. `style-ticket` targets D7's observed incident duration. `none-private` has zero eligible positives; legal-only D10 is outside the judgment universe, not a grade-0 support-team candidate.

## B. Integrity and measured quality

The checked-in snapshot reloads with all 13 row IDs and the pinned model/text contract. It agrees with the Chapter 11 in-memory exact index on all `17×2=34` ordered top-*k* rankings at depths 2 and 8; maximum raw-score delta is zero in the checked-in run. This validates persistence of **the same representation**, not human relevance. The corruption probe raises `ValueError` for the payload checksum; wrong expected model revision raises a compatibility `ValueError`. Equal dimensions do not imply aligned coordinate spaces, pooling or input prefixes.

| Top-two diagnostic | BM25 | Dense |
|---|---:|---:|
| Macro positive-query Recall@2 | .708 | .792 |
| Macro positive-query NDCG@2 | .681 | .742 |
| Acronym Recall@2 | .75 | .75 |
| Exact-code Recall@2 | .5 | .5 |
| Negation Recall@2 | 1.0 | 1.0 |
| Numeric-constraint Recall@2 | .5 | .5 |
| Colloquial Recall@2 | .5 | 1.0 |
| Exploratory cross-lingual Recall@2 | 1.0 | 1.0 |
| No-evidence candidate return | 2/2 | 2/2 |

The 12 positive questions and seven slices are too small for a general win claim. The Spanish questions are author translations without native assessment. Both methods miss the literal metadata ID and the direct current target under the SLA acronym; both return candidates for both no-evidence questions. The only slice advantage for dense at depth two is colloquial wording.

For `style-ticket`, BM25 returns `D2:§2:0` (`3.164`) and `D6:row-2:0` (`2.570`), with no D7 in selected context and direct coverage `0`. Dense returns `D7:timeline:0` (`.385`) then `D3:FAQ-7:0` (`.367`), with D7 in selected context and direct coverage `1`. No answer is generated. BM25 points and cosine are different scales and neither is calibrated answer probability.

For `acronym-sla`, BM25's top two are D3 FAQ and D1 old signed clause; dense's are D1 old clause and D5 Basic agreement. Both omit direct D2, so top-two direct-evidence coverage is zero. The grade-1 D1 result produces partial binary recall but cannot answer the current-target question alone. The likely fix is version/source-status handling and perhaps acronym expansion, each evaluated separately. For `code-segment`, BM25 returns none and dense returns unrelated D4 runbook windows; an authorized exact-ID lookup is the narrow fix.

## C. Throughput, latency and next step

The checked-in three-pass median is about 52.6 texts/s at batch 1, 67.8 at batch 4, and 57.8 at batch 16. Batch 4 is fastest **in this tiny run**, but text lengths, CPU/GPU, memory, fixed trial order and variation can reverse it. The record separates model construction after imports (`382.4 ms`), snapshot build (`239.6 ms`), snapshot load (`25.0 ms`), warm query encoding p50 (`16.9 ms`), and exact scan/selection p50 (`.620 ms`). BM25 search-only p50 is `.090 ms`. The dense combined p50 (`17.5 ms`) comes from measured combined samples and should not be reconstructed by adding stage percentiles. No context or generator time is included.

At one million rows the raw float32 coordinate file is `1,536,000,000` bytes, about `1.43 GiB`, before ID map, metadata, source, model, index overhead or replicas. ANN could reduce **vector comparisons in the exact-scan stage**; it cannot remove the measured query-encoding time. Chapter 15 must compare ANN top-*k* with the exact-neighbor oracle and qrel recall under the same scope, plus latency/memory at a representative corpus size. The present 13-row scan is far too small to justify ANN on latency grounds.

An exact-ID route should first authenticate scope, look up the requested segment ID in an authorized forward/metadata index, retain source version and span, then pass an eligible result to context. A no-evidence policy needs independently reviewed positive/negative questions and calibrated thresholds or answerability checks; two negatives cannot set a reliable cosine cutoff. Until those evaluations exist, a top-*k* candidate remains only a candidate.
