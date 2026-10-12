# Chapter 18 lab — Benchmark the index and defend the system boundary

Read [Chapter 18](../../chapters/chapter-18-disk-ann-benchmarks-and-vector-databases.md), with Chapters 3 and 15–17 as prerequisites. This lab closes Part IV. Submit the independent mechanism, measurement card and cumulative assessment; running the supplied benchmark alone is insufficient.

## A0. Construct page coalescing and cache state

Before opening [storage_ch18.py](../../projects/V4/storage_ch18.py) or the solution, implement `read_beam` in [implement.py](implement.py). Inputs are an ordered beam, node/page map, oldest-first cache and positive capacity. Classify hits using residency **at beam entry**. Touch existing hits in encounter order; coalesce unique missed pages in encounter order; then complete those reads in that order, appending them and evicting the oldest page when capacity is exceeded. Two nodes on one missing page produce one page request, while both node decisions remain misses at entry.

Draw your own fixture, hand-predict decisions/request order/evictions/final cache, implement it, and run:

```powershell
python -X utf8 labs/chapter-18/check_implementation.py
```

The unsolved starter intentionally raises `NotImplementedError`. The fresh checker uses nodes on pages10/20/30, a two-page cache and two beams; it tests coalescing, reuse, eviction and an empty beam. Submit your first attempt, predictions, checker feedback and any correction. Only then inspect the [independent answer](../../solutions/code/chapter_18_mechanisms.py). These are logical page/cache operations; neither the code nor its run time measures an SSD or implements DiskANN.

## A. Hand mechanisms and budgets

1. Trace `ch18-logical-page-cache-v1` from cache `[1]` through `[A,B,C,D]`, then `[B,D,C]`. Write every node/page decision, unique page request and LRU eviction. Explain why simultaneous completion in another order could change cache state.
2. For a hypothetical record with d=128 float32 coordinates, 64 four-byte outgoing IDs and a 16-byte header, compute record bytes and the number of whole records in a 4,096-byte page without splitting records. Calculate unused bytes. This is a declared packing example, not the layout of every DiskANN implementation.
3. With assumed random-read latency .15ms, compare 100 serial reads with an ideal eight-read beam when every address is known initially. Explain why graph dependencies, queueing and cache state can invalidate that ideal calculation.
4. Hand-check Vamana's pruning comparison for x=0,s=1,c=3 at alpha1 and2. Convert it to squared-distance arithmetic correctly. Contrast its construction role with efSearch and a disk beam width.
5. For q=x=(1,0), calculate reconstruction error and inner-product error for `(1,.2)` and `(.8,0)`. Explain why equal reconstruction error need not give equal scoring error. Identify partition, compressed-score and rescoring losses in a ScaNN-style pipeline.

## B. Run matched native indexes

Use the existing Python environment if it has the pinned native packages. Otherwise install [requirements-ch18.txt](../../projects/V4/requirements-ch18.txt) in an isolated environment. The judged run also needs V3's cached pinned sentence encoder; follow [V3 setup](../../projects/V3/README.md). No vector database account or service is required.

```powershell
python -m pip install -r projects/V4/requirements-ch18.txt
python -X utf8 -m unittest discover -s projects/V4 -p test_ch18.py -v
$ch18Run = "projects/V4/experiment_ch18.py"
$ch18Output = "projects/V4/chapter-18-experiment-local.json"
$ch18Indexes = "build/ch18-local-indexes"
python -X utf8 $ch18Run --output $ch18Output --artifact-dir $ch18Indexes
python -X utf8 visuals/chapter-18/plot-18-01-02-boundaries-and-pages.py
python -X utf8 visuals/chapter-18/plot-18-03-04-native-and-filters.py
```

The first command is unnecessary when those exact packages are already installed. The runner does not download weights by default. Use `--allow-download` only if you intend to fetch the same pinned V3 revision. Plots require matplotlib and read the **checked** observation; your replay uses a separate output/artifact directory. Never overwrite historical records or canonical native bundles to align a new timestamp.

6. Create a benchmark card before interpreting results: workload ID, corpus/query/qrel/index/model versions, N/d, scope, dtype/metric/ties, k, return depth, graph settings/seed/order, native threads, warmup, trials, failure population and timing exclusions. State which labels are geometric and which are human relevance judgments.
7. Run Flat and HNSW on identical frozen questions. Tabulate geometric recall, native p50/p95, adapter p95, add/build time and actual native/manifest bytes. For the synthetic workload, use a **teaching decision gate** of geometric Recall@2 at least .95; inspect which configurations pass and whether any measured graph point dominates Flat. This is an already inspected exercise, not untouched test selection.
8. Verify recorded oracle IDs against Chapter17's historical cases. Explain why observed parity under float32 coercion does not imply bit-identical scores or guaranteed global ties. Inspect the actual native depth8 pool and the float64-accumulated refinement pool.
9. Compare the two matrix-call batch modes. Calculate Q/T yourself for one saved sample. Explain why its mean queries/s is not a per-request latency distribution or endpoint capacity estimate. Keep the per-query adapter samples separate.

## C. Diagnose actual pools and snapshot boundaries

10. For `ch18-public-tag-stride8-v1` and `ch18-public-tag-stride64-v1`, list the authorized count, predicate-eligible count, k and oracle definition. Compare all five modes' eligible-neighbor recall and underfill rates. Do not treat stride8 and64 as a longitudinal improvement chart.
11. Find a query where Flat R8 followed by the public tag returns no result or misses an oracle ID. Join the case's request ID to the actual native-return, metadata-survivor, refinement and final fields. Repeat at R32. Classify the first losing boundary. Explain why this demonstration is not an ACL test.
12. On `ch13-stress-probes-v1`, inspect `code-segment`, `acronym-sla` and the two zero-positive questions. Identify the directly relevant source IDs, exact candidate failures and absent generation/abstention outcomes. Explain why all geometric oracle memberships can match while judged recall remains below one.
13. Compare native trace availability with `inspectable_reference_e24`. The reference graph has its own construction and request ID. State exactly what can be diagnosed from each route and why attributing the reference frontier to Faiss would falsify the trace.
14. Restore a local native snapshot using its expected trusted manifest digest, current row/source/model/scope identity and payload hash. Verify rankings. Change a vector while retaining its ID or corrupt native bytes, then confirm rejection **before** native deserialization. State what this proves and which durability/crash/backup guarantees remain untested.
15. Inspect the pinned HNSW delete test. Explain why a database delete API can exist even when its chosen index has no physical remove operation. Describe the ID-map, tombstone, cache, visibility and rebuild checks needed for a later real lifecycle, without claiming they are implemented here.

## D. Select by responsibilities

16. Classify Faiss, pgvector/PostgreSQL, one search engine, one system centered on vector search, and one embedded option. For each, use current primary documentation to locate algorithm, library, query-engine and service responsibilities. Do not copy marketing speed into your benchmark card.
17. Design a one-page service contract with write acknowledgment meaning, durability failure model, search visibility, predicate/authorization execution, tenant-safe caches, routing/replicas, timeout/partial behavior, backup/restore and exports. Include query throughput and accepted-versus-searchable ingest throughput. This is a design exercise; no real service is deployed.
18. Write the V4 decision: keep or change a route, identify compatible workload evidence and two failures, distinguish kernel/adapter/batch/endpoint boundaries, account for bytes/build cost and mark absent answer measures. An honest rejection or deferred adoption receives full credit.

## Part IV cumulative assessment

Complete [the chapter checkpoint](../../chapters/chapter-18-disk-ann-benchmarks-and-vector-databases.md#14-part-iv-cumulative-checkpoint--approximation-without-lost-accountability) without notes:

- Architecture from memory with separate index/query/evaluation lanes and all lossy stages.
- Eight cross-chapter reasoning/calculation questions, including exact bounds versus approximate stops.
- V0/V3/V4 capability/failure comparison, then compatible same-workload result comparisons.
- Day1/3/7/21 recall; day3/day7 teach-back with a hand example and recorded request.

Use [the separate Part IV rubric](../../solutions/chapter-18-solutions.md#part-iv-cumulative-assessment-rubric). Retention tasks are scheduled learner work, not experiments falsely marked as already performed by the author. Chapter19 is not part of this submission.
