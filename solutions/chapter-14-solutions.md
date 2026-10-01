# Chapter 14 lab — worked solutions

Attempt the [lab](../labs/chapter-14/LAB.md) before using this page. The fixed scores come from [the checked record](../projects/V3/chapter-14-experiment.json); warmed timing samples are machine-specific.

## A. Sparse trace

For the first pooling probe, `a=max(log(3),log(2))=log(3)≈1.099`; `c=log(4)≈1.386`; `b` is absent because `ReLU(−10)=0`. Sum pooling would give `log(3)+log(2)≈1.792` for `a`; this code implements the SPLADE-v2-style maximum, not the original sum.

The query has `ticket=reply=log(3)≈1.098612` and expansion terms `incident=response=log(2.8)≈1.029619`. Each eligible document has two positive weights of `log(3)`: incident (`incident`,`response`); ticket sale (`ticket`,`sale`); reply template (`reply`,`template`). The four queried posting lists each have one **eligible** entry. Surface-only scoring visits `ticket` and `reply`, yielding ticket sale and reply template at `log(3)²≈1.206949` each. ID tie-breaking places `reply_template` before `ticket_sale`. Incident has no shared term and is absent, so direct Recall@1 is 0.

Expanded scoring visits four eligible entries. The incident score is `2 log(2.8) log(3)≈2.262305`; the literal distractors remain at `≈1.206949`. Order: `incident`, `reply_template`, `ticket_sale`; direct Recall@1 is 1. Work changes from two to four scored posting entries and from two to three positive-score candidates. There are three eligible support-team rows. The `private` legal-team row also contains `incident` and `response` with high weights, but `search()` checks `self.rows[item_id].scope != scope` and continues **before** accumulating score or counting work. An authenticated policy service would have to establish eligibility in a real system; the demo accepts only a fixture string and therefore is not authentication.

With the copied query's `sale=8`, `ticket_sale` gains `8×log(3)≈8.789` on top of its `1.207`, for about `9.996`. It takes rank one even though it is grade 0. Incident remains at `2.262` and rank two. This is a false expansion example; a single observed failure does not justify a universal clipping threshold.

## B. Token matrix

The query is `q0=(1,0)`, `q1=(0,1)`. A is `(1,0)`, `(0,1)`, then twice `(−√½,−√½)`. Its grid is `[[1,0,−.707,−.707],[0,1,−.707,−.707]]`; winners are positions `0` and `1`, hence MaxSim `2`. B is one `(√½,√½)` vector. Its grid is `[[.707],[.707]]`; both maxima use document position `0`, hence MaxSim `√2≈1.414`. C has one `(1,0)`; its grid is `[[1],[0]]`, hence MaxSim `1`. Exact order is A, B, C. B can supply its one token as the best match to **both** query tokens; MaxSim is not one-to-one assignment.

The mean of the query is `(.5,.5)`. A's mean is `( (1−√2)/4, (1−√2)/4 )`, opposite to the query mean, so its cosine is `−1`; B's mean points in the same direction, so cosine is `+1`; C's cosine is `1/√2≈.707`. Pooled order is B, C, A. This is a geometric construction. The Chapter 11 sentence encoder has learned contextual vectors and a trained pooling path; these hand-authored two-dimensional vectors are not its output.

Exact full-set MaxSim evaluates every eligible token grid and is the score oracle for this fixed representation. A token ANN stage may miss a high exact-MaxSim document; compare its output with that oracle and with qrels. Reranking only BM25's top 100 can improve order **within that 100** but cannot recover a passage BM25 omitted. A full-collection token-index route can recover such a passage if its candidate-generation stage finds it; approximation recall must still be measured.

## C. Evidence audit

The record asks whether expansion and MaxSim change the intended rankings. It freezes one three-passage sparse query and one three-passage token query, complete grades under a 0/1/2 rubric, the exact surface-posting and pooled-cosine baselines, manual logits/vectors, `k=3`, ID ties, a static support-team gate, `seed=14092026`, fixture/code/runner/index identities, raw ranks/scores, work, 31 warmed microsecond samples for each method, and explicit failures/limits. Its four request-trace examples retain query/request ID, fixture/index, eligible count, candidate IDs and raw scores; `selected_context_ids=null` and `answer_status=not_run` mean those stages did not execute. `model_version=null` is deliberate: no model weights are trained or loaded. The timed boundary excludes neural encoding, index build, I/O, context, answer generation and network; it is also too small to estimate a service tail. A sparse weighted-dot score, token MaxSim score, BM25 score and dense cosine have different units/distributions. None is a calibrated probability of relevance or answer correctness. The code ranks candidates; it has no new context/answer outcome.

A fair future comparison would freeze model/tokenizer/query-document input contracts and source/index snapshots; build learned-sparse and token-vector indexes from V0; tune on one set and test once on a separately reviewed set; retain the support-team eligible roster and test D10 exclusion; compare with V2 BM25 and Chapter 13 frozen dense at equal depths; report binary/graded qrel metrics, no-evidence returns, index bytes/build time, encoder/search/refine p50/p95, and exact-neighbor versus approximate loss. The Chapter 13 SLA, metadata ID and no-evidence queries are **inspected regression cases**; they are not a fresh held-out set. A separate source-disjoint or independently reviewed future query sample is needed for a general gain statement. If candidate gain is real, context and generation evaluation still follow later.

The manager's `2.000` is a sum of two best token similarities in a constructed two-dimensional example. It is neither a relevance probability nor a BM25/dense comparable score. We would first measure judged candidate recall, including a case absent from the first-stage candidate set. We would then measure token-index bytes, build/refresh cost and complete warm query latency under a representative workload. We would still check trusted eligibility, selected evidence and grounded answer behavior before changing the deployed path.

## Independent bounded mechanism: reasoning and answer

Multiply shared term weights only after eligibility; MaxSim instead keeps a full token-pair grid and selects one maximum per query row. The answer exposes grid/winners so the mechanism remains inspectable.

The separate [worked implementation](code/chapter_14_mechanisms.py) uses standard-library code and imports no supplied project engine or learner scaffold. After comparing your reasoning, verify it on the new fixtures:

```powershell
python -X utf8 labs/chapter-14/check_implementation.py --implementation solutions/code/chapter_14_mechanisms.py
```

Rubric: correct intermediate mechanism (40%), deterministic and edge-case behavior (20%), independently written code (20%), and explanation of exact parity or measured approximation failure (20%). Passing output alone is insufficient. A loop-based implementation is appropriate; premature abstraction is unnecessary.

## Part III cumulative checkpoint: answer and rubric

At build time sources become lexical weights, pooled sentence vectors or token vectors under an explicit model/input contract; materialized exact vectors keep ID/scope/model/source manifests. A query follows the same representation contract, then eligibility gates scoring. Training pairs/loss/gradient/updates are a separate path; validation selects, test reports. Candidate scoring and qrels measure different things, and context/generation remain downstream.

Quiz answers: (1) BM25 estimates lexical matching with collection statistics, embedding similarity is geometry of a learned representation, exact neighbor is the mathematically highest allowed score under that geometry, and judged relevance is assessor evidence for the information need; (2) exact execution cannot repair missing metadata input, authority or version distinctions in the representation; (3) compare BM25/dense on the same Chapter 13 workload, such as `code-segment` or `num-basic`, and keep no-evidence return separate from recall; (4) loss derivatives update the query adapter while passages stay frozen; document targets are disjoint but Helios families overlap, so no transfer claim follows; (5) retain lexical baselines, the rejected epoch-1 adapter result and all 34 exact materialization parity checks; (6) no lossy ANN/PQ stage is in the exact dense baseline, and safe WAND pruning changes work without changing the result.

V3 adds capability beside V2, not a universally better score. Chapter 10 uses the Chapter 09 workload, Chapter 11 new embedding probes, Chapter 12 a train/dev/test adaptation workload, and Chapter 13 new stress probes. The Chapter 14 sparse/token fixtures each contain one authored query and three judged eligible items; they do not demonstrate a trained-model gain over the corpus. The workload registry makes valid comparisons explicit.

Rubric (10 points): complete build/query/training paths (2), four score/relevance distinctions (2), correct same-workload failure evidence (2), V2/V3 baseline/negative-result/version continuity (2), and exactness/approximation distinction plus teach-back (2). Pass at 8/10 with eligibility and exactness correct. Accept alternate layouts, but no score-comparison progression across unrelated workloads. Record omitted links on day-3/day-7 recall rather than copying the answer.
