# Chapter 14 lab — Weighted postings and exact MaxSim

Read [Chapter 14](../../chapters/chapter-14-sparse-neural-search-and-late-interaction.md) first. This lab has two **fixed mechanism tasks**. The sparse logits and token vectors are hand-authored; no SPLADE or ColBERT network is trained or benchmarked. Keep Chapter 13's BM25/frozen-dense results as the operational baseline, and do not present this toy's Recall@1 as a gain over that different corpus.

## A0. Independent bounded mechanism

Implement `weighted_sparse_score(query, postings, eligible_ids)` and `maxsim(query, document)` in [implement.py](implement.py) before opening the supplied mechanism or solution. This is scoring on fixed weights/vectors, not training SPLADE or ColBERT.

Weighted postings map each term to `(ID, positive document weight)` pairs. Query weights are finite/nonnegative. Filter eligibility **before** accumulating each product and return descending score/ascending ID pairs. Zero query weights contribute no candidates. MaxSim receives nonempty equal-dimension unit token vectors; form every dot product, choose the first document-token position on a tie in each query row, then sum row maxima. Return `(score, grid, winner_indices)`.

Use your own two-term postings fixture including one ineligible record, and a 2x3 token matrix with a tie. Show products, row maxima and winners by hand, then implement. The checker supplies different fixtures. Explain why sparse weighted accumulation and MaxSim have different storage/work, and preserve the existing pooling-failure calculations.

After your first attempt, run from the repository root:

```powershell
python -X utf8 labs/chapter-14/check_implementation.py
```

The starter intentionally raises `NotImplementedError`. Tests are feedback fixtures, not a concealed grading service. Submit your implementation, hand predictions, checker output and one diagnosis of a failing case. Open the separate chapter solutions only after attempting this task. Existing calculation, experiment and debugging tasks below still apply.

## Setup and release boundary

From the repository root, run:

```powershell
python -X utf8 -m unittest discover -s projects/V3 -p 'test_*.py' -v
python -X utf8 projects/V3/experiment_ch14.py --output projects/V3/chapter-14-experiment-local.json
python -X utf8 visuals/chapter-14/plot-14-01-maxsim-grid.py
```

The runner writes a local record; compare its rankings, score grids and work counts to the [checked record](../../projects/V3/chapter-14-experiment.json). The date and warmed microsecond samples can differ. The plot source reads the checked record so its numeric figure remains fixed. If matplotlib/numpy are absent, inspect the table and JSON first; the scoring code itself is standard-library Python.

## A. Trace the sparse index by hand

1. In [the mechanism code](../../projects/V3/sparse_late_ch14.py), locate `sparse_pool`, `SparseIndex.__init__` and `search`. For logits `a=2` at one token position and `a=1,c=3,b=-10` at another, calculate all retained weights. Explain why max pooling differs from summing the two `a` activations.
2. List the nonzero weights for the fixture's query and three eligible passages. Write the postings for `ticket`, `reply`, `incident` and `response`. Calculate the surface-only and expanded score of each passage to three decimals. Give the top-three order under ID ties, and Recall@1 for the grade-2 incident.
3. Inspect `posting_entries_scored`, `positive_score_candidates` and `eligible_rows` for each route. Explain why expanding the query increases work even on this tiny corpus. Show the legal-team `private` posting and explain why its high logit must not affect the support-team score or qrels. Which code line gates eligibility? Which real system component would have to supply it?
4. Probe a **false expansion** without changing the checked fixture: in a short Python REPL import `sparse_fixture`, copy its query map and set `sale` to `8.0`; run `index.search(modified, 'support-team', 3)`. Which passage ranks first? Why does the legitimate incident remain a candidate but cease to be top one? Keep this result as a failure example, not a tuned setting.

## B. Recompute the late-interaction grid

5. From [the runner](../../projects/V3/experiment_ch14.py), write the two query vectors and all A/B/C document vectors. Compute each dot-product cell for A and B, circle the maximum of each query row, and sum them. Compare A, B and C by MaxSim.
6. Compute mean-pooled vectors and their cosines for A/B/C. Explain the reversed first rank. Why is the toy's pooled cosine not a benchmark of the Chapter 11 encoder? Use the [figure](../../visuals/chapter-14/figure-14-01-maxsim-grid.svg) to check exact cells and argmax positions.
7. In one paragraph, distinguish: an exact scan of every eligible document's token grid; token ANN candidate generation followed by exact MaxSim refinement; and MaxSim reranking only BM25's top 100. Say which can recover a passage excluded by BM25's top 100 and which needs an exact-MaxSim oracle to quantify approximation loss.

## C. Audit evidence, time and transfer

8. Read the [experiment record](../../projects/V3/chapter-14-experiment.json). Identify the question, falsifiable hypothesis, baselines, independent variables, frozen qrels, code/model/index versions, scope, seed, raw scores, p50/p95 sample counts, work and failure examples. Inspect all four request-trace examples: distinguish ranked candidate IDs from the null context and unrun answer fields. Explain why the sparse and token scores **cannot** be compared numerically to each other or to Chapter 13 BM25/cosine. State which timing stages are absent and why no answer-quality claim is possible.
9. Propose a fair *future* experiment on the V0 corpus: model and snapshot pins, non-overlapping tuning/test query sets, support/legal scope test, BM25 and Chapter 13 dense baselines, retrieval metrics at fixed depths, exact-versus-approximate comparison, index bytes, warm encode/search/refine timings, and inspected failures. Include the old-current SLA, metadata ID and no-evidence cases as known regressions. Name a separate held-out source for a fresh gain claim.

## Design and interview challenge

A manager proposes replacing BM25 with a late-interaction model because its toy MaxSim score is `2.000`. Respond in five sentences: what that number means, what it does **not** mean, the candidate coverage test, the latency/storage test, and the authorization/answer path that still must be verified.

Check your work against the [separate solutions](../../solutions/chapter-14-solutions.md). An acceptable conclusion can be negative: the local fixture explains operator behavior but cannot select a production retriever.

## Part III cumulative checkpoint

Close Chapters 10-14 and their figures. Draw the full representation/training/index/query/evaluation path and answer Chapter 14's six cumulative questions. Include raw text/analyzer or tokenizer, dimensions, frozen versus trainable weights, exact index, eligibility, scores, candidate IDs and judged metrics. Keep context and answer evaluation downstream.

After drawing, use the unchanged Chapter 13 stress record (`ch13-stress-probes-v1`) to compare lexical and dense acronym, exact-code, numeric-constraint and no-evidence failures. State the query/slice denominator and metric. Explain the preserved V2 -> V3 project steps: no representation change in exact WAND; binary lexical vectors; pinned encoder; failed adaptation; checked materialized exact oracle; separate sparse and token scoring sandboxes. Show why workload definitions prohibit a cross-chapter improvement curve.

Identify approximation that has **not** yet been introduced: no lossy ANN bucket/list/graph omission or PQ code distortion in the current exact dense oracle; WAND's safe bounds preserve exact rankings. MaxSim/sparse toy inputs are authored fixtures, not trained production models. Submit your first diagram, answers, paired same-workload failure table, version comparison and teach-back. Repeat recall at day 3 and day 7 before consulting the rubric again.
