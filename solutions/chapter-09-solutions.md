# Chapter 09 lab — Worked solutions

Attempt the [lab](../labs/chapter-09/LAB.md) before using these calculations. The checked-in timing values are one local run on 30 September 2026; reruns may differ.

## 1. Judgment universe

The unit is an indexed **segment** from `support-corpus-2026-05-20` under the `support-team` fixture. Fourteen queries times twelve eligible segments give 168 fully reviewed pairs. Binary relevance is grade `≥1`; grade 2 is direct evidence, grade 1 partial context, grade 0 reviewed nonrelevant or misleading for the question. The loader compares the exact ordered eligible segment roster and snapshot with the current index and rejects mismatches. A new chunker can change segment IDs and boundaries, so old segment qrels cannot be used without explicit mapping/review.

`q-contract-change` requires `D1:§3:0` and `D2:§2:0`, both grade 2. `D3:FAQ-7:0` is grade 0 because the older FAQ is superseded for the dated change. One relevant hit makes Hit@2 equal 1, even if the other signed clause is missing. `D9:proposal-2:0` is grade 2 when asking what the unsigned draft proposed, but grade 0 for the target currently in force. D10 is legal-only, outside the eligible roster: authorization determines membership before relevance is scored. An item outside a larger pool is **unjudged** until assessed; treating it as grade 0 would invent a negative label. Add it to a versioned pool, judge it under the same rubric, retain assessor IDs/rationales and reevaluate all systems on the revised qrels.

## 2. Hand metrics

There are `R=2` binary-relevant items. The ideal top two are A then B, with `IDCG@2=3+1/log₂3≈3.630930`; C contributes zero. The ideal at three is the same because the third item has grade 0. All values below use AP's denominator **two**, the total known positives.

| Ranking | P@2 | Recall@2 | Hit@2 | F₁@2 | RR@2 | AP@2 | DCG@2 | NDCG@2 | AP@3 | NDCG@3 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| R1 `[A,B,C]` | 1 | 1 | 1 | 1 | 1 | 1 | 3.630930 | 1 | 1 | 1 |
| R2 `[C,B,A]` | 0.5 | 0.5 | 1 | 0.5 | 0.5 | 0.25 | 0.630930 | 0.173765 | 0.583333 | 0.586883 |
| R3 `[B,C,A]` | 0.5 | 0.5 | 1 | 0.5 | 1 | 0.5 | 1.000000 | 0.275412 | 0.833333 | 0.688529 |

For R2 at three, precision at relevant ranks is `P@2=1/2` and `P@3=2/3`, hence `AP@3=(1/2+2/3)/2=7/12`. Its DCG is `1/log₂3+3/log₂4≈2.130930`. R3 has `P@1=1`, `P@3=2/3`, so `AP@3=(1+2/3)/2=5/6`; its DCG is `1+3/log₂4=2.5`. **Hit@2** is 1 for all three despite R2 and R3 lacking grade-2 A by rank two. Binary RR also does not distinguish grade 1 from grade 2 under this threshold; direct recall and NDCG do.

For all-zero qrels and an empty list, `P@2=0`; Recall, Hit, F₁, RR, AP, NDCG and direct recall are `null` by declared policy. The no-positive candidate flag is false. Returning B flips that flag to true while leaving `P@2=0`; it does not add evidence. For this miniature corpus, duplicate or ineligible IDs should raise. If AP divided by **retrieved** positives, R2 at *k*=2 would incorrectly receive `0.5` instead of `0.25`, hiding the missing A. If IDCG sorted only returned items, a run that never found A could receive a falsely perfect normalized gain.

## 3. Metric implementation notes

An independent implementation can loop over ranks up to *k*, accumulate binary hit count, precision at each hit and graded DCG, then compute ideal DCG from **all eligible grades**. It should use an explicit `None`/undefined result for measures without positives, fixed *k* as precision denominator and a deterministic result ordering supplied by the retriever. Compare with [the project tests](../projects/V2/test_eval_ch09.py); they include hand arithmetic, missing result slots, zero-positive queries, duplicate rejection, macro versus micro and qrel-roster version failures.

## 4. The checked-in comparison

At top two, the [record](../projects/V2/chapter-09-experiment.json) reports eleven positive queries and three zero-positive queries. Macro NDCG is `0.9091` for overlap versus `0.8997` for both BM25 plans. Macro binary Recall is `0.9091` versus `0.8636`; macro **direct** Recall is `0.9091` versus `0.9545`. MAP is `0.9091` versus `0.8182`. Search-only p50/p95 in microseconds is `21.5/30.2` for overlap, `43.1/62.0` for exhaustive BM25 and `128.5/195.7` for WAND in that local equal-query-mix run. BM25 and WAND have identical ordered IDs, raw scores, context IDs and judged quality at all recorded depths; WAND scores an average six segments at *k*=2 versus about 10.71 for exhaustive BM25. Fewer score calculations do not imply lower latency here.

At top eight, both ranking methods reach macro binary and direct recall 1 on this tiny collection, while macro `P@8≈0.1818` because most of eight slots are nonrelevant. Two of three zero-positive questions still return irrelevant candidates at top two; the nonexistent identifier returns none. The top-two dated-contract result is BM25 `[D2 §2, D3 FAQ-7]`, with direct recall `1/2`, `NDCG≈0.613` and stub **abstained**. Overlap has `[D2 §2, D1 §3]`. For termination, BM25 includes `D1 §8` and the stub answers, whereas overlap omits the clause at top two. BM25 loses grade-1 context on urgent-arrival and current-target queries. For the unknown renewal and private-target questions, public candidates are returned despite no eligible positive evidence. D10 never appears in support-team results or qrels. No LLM answer evaluation was performed on these newer queries.

The declared BM25 NDCG@2 improvement hypothesis is falsified on this fixture. The result does **not** establish a general winner: there are fourteen questions, one author, one small fictional corpus, and two inherited questions whose failures were already known. A credible next comparison would collect many representative human questions, label a diverse pool with independent assessors, define development and untouched test splits, version the corpus and rubric, and report per-slice quality with uncertainty alongside latency and authorization tests. This chapter does not tune parameters or start the Chapter 10 dense-retrieval work.

## 5. Failure localization

MRR@2 can be high after the first relevant segment even if a second mandatory clause is missing; check `all_direct@2`, Recall@2 and the actual evidence set. Treating a new relevant unpooled item as negative biases evaluation against methods that find outside the existing pool. When D2 changes, inspect source/version, segment boundary, index/analyzer/scorer, qrel/rubric and trace versions before computing a delta. If both grade-2 segments were candidates but one is absent from selected context, the failure is context construction; candidate Recall@2 remains 1, while a later context-recall measure must fall. The current negative BM25 comparison should remain in the record because it is a reproducible observed result under the declared data and metric, even though it is too small for a deployment claim.

## Part II checkpoint

V0 scans every eligible segment and makes candidate/context/answer boundaries explicit. V1 replaces the scan with analyzer-versioned postings and adds TF-IDF weights; the analyzer can destroy meaningful code or product distinctions if normalization is too aggressive. BM25 differs by a declared nonnegative IDF, saturating term frequency and length adjustment through `k1` and `b`; it is still lexical. WAND can skip only when its bound covers every still-possible nonnegative score contribution under the same eligible snapshot, scorer and tie policy. On this qrel rubric BM25 recovers direct termination evidence but displaces an original signed clause or useful partial context elsewhere, so direct recall and macro NDCG move in different directions. Draw offline qrels/evaluation beside, rather than inside, the request path. The private legal-only source is gated before candidate scoring, and the missing contract clause falls out at top-two candidate rank before context construction.

## BM25 dev/test selection: separate workload answer

On `ch09-bm25-devtest-v1`, the twenty development configurations tie at the primary metric. Apply the preregistered default-first rule: k1=1.2, b=.75. Freeze those controls before computing test. The separate [result record](../projects/V2/chapter-09-tuning-experiment.json) reports default and selected test Recall@2=1.0 and NDCG@2=0.9261859507; RR/AP=.9 indicate one relevant result is at rank two. Both methods return candidates on the no-evidence question, so candidate recall is not answer abstention. There is no tuning gain.

The [reference driver](../projects/V2/tune_bm25_ch09.py) stores development grid/slice results, a frozen selection digest, test cases/slices, timings/work, versions and redacted sample traces. Its selection function receives development data only. The test mutates final-test labels and wording while retaining the same selection, and rejects duplicate query IDs across groups. The original Chapter 09 fourteen-query record has a different workload and remains an inspected diagnostic; neither its scores nor Chapter 11's scores form an improvement sequence with this new fixture.

Rubric: independent grid driver and correctly declared metric/ties (30%), saved selection before test (25%), honest paired test/slice/error analysis (30%), and explicit source/assessor/generalization limits (15%). Copying the selected constants from this answer does not demonstrate parameter selection.
