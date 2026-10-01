# Build Your Own RAG Engine — V4, Chapter 15 exact and approximate search

V4 spans Chapters 15–18 in the [project roadmap](../../PROJECT_ROADMAP.md). **Only Chapter 15 is implemented here.** It starts from V3's [checked materialized exact dense index](../V3/README.md), pinned 384-coordinate model and Chapter 13 diagnostic qrels. [Chapter 15](../../chapters/chapter-15-exact-knn-to-trees-and-hashing.md) asks which comparisons can be skipped safely and what candidate quality is lost when skipping is approximate. V0–V3 stay as baselines; no approximate index replaces the exact candidate route.

## Artifacts and execution contracts

- [From-scratch code](ann_ch15.py): a full cosine scan over pre-normalized rows, materializing score pairs before bounded top-*k* heap selection; an exact median-split KD tree with coordinate bounding-box lower bounds and backtracking; and a seeded random-hyperplane LSH index with `L` independent tables, `h` sign bits/table, matching-bucket union, scope filtering and exact cosine refinement. The LSH route returns an empty list if no eligible bucket matches. No arbitrary fill or hidden full-scan fallback masks an ANN miss.
- [Behavioral tests](test_ch15.py): exact KD ordered parity against a scan across multiple dimensions and ties, LSH seed determinism, static-scope exclusion, empty-bucket behavior, invalid inputs, and checked-record/source-hash/eligibility invariants.
- [Experiment runner](experiment_ch15.py) and [checked record](chapter-15-experiment.json): six synthetic workloads (`N=128,512,2048`; `d=2,32`) with twenty fixed queries each, plus fourteen existing Chapter 13 V0 questions with 168 complete support-team qrels. The synthetic workload reports **exact-neighbor** Recall@2 only. V0 reports both exact-neighbor and **judged relevant-evidence** recall, ranked candidate/context IDs, per-query scores/work/status, no-evidence returns, build time, query-encode time and search-only p50/p95. The V0 LSH `L∈{2,4,8} × h∈{4,6,8}` grid was predeclared. Code, model, source, index, qrel, seed, tie and metric contracts are recorded.
- [Figure 15.01](../../visuals/chapter-15/figure-15-01-partitions-and-buckets.svg), its [editable source](../../visuals/chapter-15/plot-15-01-partitions-and-buckets.py) and PNG: one fixed two-dimensional scan/KD/LSH trace, with a missed exact neighbor visible. [Figure 15.02](../../visuals/chapter-15/figure-15-02-latency-recall.svg), its [editable source](../../visuals/chapter-15/plot-15-02-latency-recall.py) and PNG: search-only p50 and exact-neighbor recall from the checked synthetic record.

The indexed Chapter 13 binary snapshot includes thirteen passages; the support-team exact/KD query population has twelve. LSH bucket maps include the legal-only D10 vector but the query applies the support-team fixture **before scoring and context selection**. A caller-supplied scope is not authentication. The KD tree is built from the already eligible static roster, so a changed live policy would require a new or trusted eligibility path. Chapter 21 later treats real ACL filtering and deletion lifecycle. Derived vectors and bucket maps inherit source privacy, licensing and retention duties.

## Reproduce

From the repository root:

```powershell
python -X utf8 -m unittest discover -s projects/V4 -p 'test_*.py' -v
python -X utf8 projects/V4/experiment_ch15.py --output projects/V4/chapter-15-experiment-local.json
python -X utf8 visuals/chapter-15/plot-15-01-partitions-and-buckets.py
python -X utf8 visuals/chapter-15/plot-15-02-latency-recall.py
python -X utf8 tools/book/build_book.py --check
```

The experiment runner uses standard-library Python except for loading the pinned Chapter 11 sentence encoder; that path needs `sentence-transformers` and CPU PyTorch as in [V3 setup](../V3/README.md). It reads the checked Chapter 13 snapshot and cached exact model revision by default. Pass `--allow-download` only if the cache is absent and you intend to fetch that same pinned public revision. The plots require matplotlib; Figure 15.02 reads the **checked** experiment record and does not substitute a local replay. Use a local output filename to keep checked observations intact. Replaying timing changes the measured values and timestamp but should preserve frozen IDs, work, parity and qrel outcomes under the same environment and code.

## Measured decision and next gate

On the six synthetic sets, KD matches every exact ordered top two. At `N=2048,d=2`, it scores 8.4 vectors/query on average rather than 2048 and is faster in the checked Python run. At `N=2048,d=32`, it scores about 2047.6 and is slower. Four-table/six-bit LSH scores fewer vectors at `d=32` but has mean exact-neighbor Recall@2 only `.225` at the largest size. The synthetic Gaussian-unit construction has no human qrels and does not model production embeddings.

On the inspected V0 diagnostic questions, exact/KD macro relevant-evidence Recall@2 is `.792` and KD ordered rankings agree with exact on all 14 questions. KD scores 8.36 eligible vectors/query on average versus 12 for exact but takes about `3.27 ms` median search-only versus `.61 ms` exact. Two-table/four-bit LSH scores 3.86 vectors/query but has exact-neighbor Recall@2 `.357` and qrel Recall@2 `.292`; its `.59 ms` search-only median gives no credible quality/latency case. Eight-table/four-bit LSH restores aggregate qrel Recall@2 `.792` while exact-neighbor recall remains `.786` and search-only p50 rises to `1.83 ms`. Query encoding is about `17.45 ms` median on this run and is separate from all search timings. An empty bucket on `style-ticket` loses the direct incident evidence. All new generation outcomes are unmeasured.

**Decision:** retain Chapter 13's exact dense route as the V4 oracle and BM25 as the judged lexical comparator. Do not deploy toy LSH or infer a general tree/LSH speedup. The Chapter 13 questions were author-written and inspected; a later model/index selection needs fresh independent qrels, representative corpus scale, multiple hash seeds, filtered-query cases, full build/refresh/storage costs and end-to-end latency. Chapter 16 may add coarse partitions and compressed vectors against this exact oracle. It has not been started here.
