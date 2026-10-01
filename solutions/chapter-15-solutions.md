# Chapter 15 lab — worked solutions

Use these after the [lab](../labs/chapter-15/LAB.md). Rankings and work come from the [checked V4 record](../projects/V4/chapter-15-experiment.json); machine timings are illustrative of that run and may move on replay.

## A. Exact pruning

The four distances from `(.9,.1)` are: `(0,0)` `√.82≈.906`; `(0,2)` `√4.42≈2.102`; `(2,0)` `√1.22≈1.105`; `(2,2)` `√4.82≈2.195`. The left child's two results give `k=1` radius `.906` or `k=2` radius `2.102`. The right region begins at `x=2`, so its lower bound is `1.1`. At `k=1`, `1.1>.906` permits pruning. At `k=2`, `1.1<2.102` requires backtracking; it discovers `(2,0)` as the second result. Equal distances resolve by ascending stable item ID, so equality cannot be pruned without examining a possible better tie.

`KDTree._build` chooses the coordinate with largest current spread and splits the sorted IDs at the median; each node stores coordinate minima/maxima. `search` orders children by their box lower bounds and calls `visit` on both unless the bound proves a branch cannot improve the current top-*k*. The test compares exact ID order for twelve queries each in dimensions 2, 8 and 32; it also checks a stable tie. The ball's lower bound is `max(0,2−.5)=1.5`. A worst distance of `1.4` permits pruning; `1.6` does not. Ball bounds follow `||q−x|| ≥ ||q−c||−||x−c||` for every contained point `x`.

At `N=2048,d=2`, exact scores 2048 vectors per query, KD averages about 8.4, and all 20 ordered top-two rankings agree. The checked local p50 is roughly `1.65 ms` exact and `.059 ms` KD. At `N=2048,d=32`, KD scores about 2047.6 of 2048 vectors and still agrees on all 20 rankings; it takes about `18.44 ms` versus `7.45 ms` for the Python scan. It is an exactness success and an efficiency loss on this particular synthetic distribution, not a universal verdict on trees or trained embeddings.

## B. Hash collision and measured loss

At `θ=60°=π/3`, one bit collides with probability `1−1/3=2/3`. Four independent bits in one table collide with `(2/3)^4=16/81≈.1975`. Four independent tables yield `1−(1−16/81)^4≈.586`. The calculation assumes independently sampled planes within and across tables. It concerns one pair; nearest-neighbor recall also depends on competing vectors, bucket sizes, a fixed random draw and top-*k* refinement.

The code seeds Gaussian planes and creates fixed sign signatures at index build. A query probes one exact-match bucket in each table, unions IDs, checks the static scope, then uses original cosine to rerank the union. It has no multiprobe and no arbitrary fallback. Figure 15.01's exact top two are IDs `08` and `07`; the union contains `08`, so `07` is unavailable to the refinement step.

The V0 four-bit table axis reads as follows (all at top two):

| Tables | Mean scored | Exact-neighbor Recall | Judged macro Recall | Search p50 ms |
|---:|---:|---:|---:|---:|
| 2 | 3.86 | .357 | .292 | .587 |
| 4 | 5.71 | .464 | .542 | 1.058 |
| 8 | 7.93 | .786 | .792 | 1.830 |

At four tables, increasing bits changes the result this way:

| Bits | Mean scored | Exact-neighbor Recall | Judged macro Recall | Search p50 ms |
|---:|---:|---:|---:|---:|
| 4 | 5.71 | .464 | .542 | 1.058 |
| 6 | 1.71 | .250 | .292 | 1.276 |
| 8 | .50 | .036 | .000 | 1.569 |

More tables recover more candidates but spend more search work. More bits shrink buckets and worsen recall here; projection cost rises enough that p50 also rises despite fewer scored vectors. The eight-table/four-bit setting matches exact aggregate judged Recall@2 (`.792`) but misses about 21% of exact top-two neighbors and takes roughly `1.83 ms` search-only versus `.61 ms` for the scan. The pinned model's query encoding adds about `17.45 ms` median, and index build is a separate cost. No measured V0 configuration merits replacement from these inspected questions.

## C. Failure localization

For `style-ticket`, exact top two include direct incident `D7:timeline:0`, but two-table/four-bit LSH has an empty candidate/context list. This is a genuine ANN candidate miss. For `acronym-sla`, exact dense itself ranks the old clause and Basic agreement rather than direct current amendment `D2:§2:0`; LSH cannot repair a missing exact-oracle target merely by matching neighbors. For `code-segment`, literal `D6:row-2:0` is a metadata identifier absent from title/body embeddings; an authorized exact-ID route is the narrow fix. For `none-private`, there is no eligible positive qrel; D10 is legal-only and never a candidate/context ID. An empty LSH bucket is not proven abstention. Each diagnostic case has `generation_status=null`, so answer correctness and citations are unmeasured.

A larger experiment must freeze source/model/index revisions and an independent reviewed question set before tuning; stratify by source, scope, query type and language; evaluate complete qrels plus exact top-*k* oracle at fixed depths; repeat randomized-index seeds; measure build/refresh and bytes, warm/cold encoder/search/refine and end-to-end latency with p50/p95 sample counts; include empty-bucket and permission tests; and set explicit recall/latency acceptance gates. Chapter 13's fourteen questions are already inspected regressions. The counterexamples to the teammate are KD's V0 mean 8.36 scored vectors versus exact 12 but search p50 `3.27 ms` versus `.61 ms`, and LSH eight-table/four-bit judged macro Recall matching exact while exact-neighbor recall is only `.786` with slower search. Stage traces, candidate IDs, qrel denominators and scoped latency distributions are needed before a route change.

## Independent bounded mechanism: reasoning and answer

A seeded local RNG creates a reproducible projection family. Signatures select a candidate bucket; cosine orders that bucket. The boundary-miss fixture has an exact neighbor outside the only bucket: its measured Recall@1 is 0.5, not 1.

The separate [worked implementation](code/chapter_15_mechanisms.py) uses standard-library code and imports no supplied project engine or learner scaffold. After comparing your reasoning, verify it on the new fixtures:

```powershell
python -X utf8 labs/chapter-15/check_implementation.py --implementation solutions/code/chapter_15_mechanisms.py
```

Rubric: correct intermediate mechanism (40%), deterministic and edge-case behavior (20%), independently written code (20%), and explanation of exact parity or measured approximation failure (20%). Passing output alone is insufficient. A loop-based implementation is appropriate; premature abstraction is unnecessary.
