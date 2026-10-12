# Chapter 18 solutions — An index benchmark is a bounded claim

Consult after attempting [the lab](../labs/chapter-18/LAB.md). Correct reasoning, construction and named limits matter as much as matching the checked record. Timing replays need not match; frozen identities, raw outcomes and logical arithmetic should.

## A0. Independent construction

[The independent answer](code/chapter_18_mechanisms.py) imports no storage/index engine. It snapshots initial residency, updates hits in encounter order, gathers unique misses and completes them in specified order. It keeps both node-level misses when two nodes share a missing page, while making one page request. Its list-based updates are intentionally bounded and visible; production planning can use hash-based deduplication and an efficient LRU structure.

```powershell
python -X utf8 labs/chapter-18/check_implementation.py --implementation solutions/code/chapter_18_mechanisms.py
```

The fresh checker starts with page20 resident. First requests10/30, evicts20 and retains10/30; second requests20, evicts10 and retains30/20. An empty beam preserves state. A solution that marks the second node on a missed page as a hit at beam entry has changed the contract. Running this code gives no measured SSD result.

## A. Hand mechanisms

**1. Logical cache — `ch18-logical-page-cache-v1`.** A/B map to0 and miss at entry; C maps to1 and hits; D maps to2 and misses. Unique requests `[0,2]` complete after hit touches, leaving `[0,2]` and evicting1. Next B and D hit while C misses; request `[1]`, evict0 and retain `[2,1]`. Completion order is controlled here; a real asynchronous scheduler must expose/define its actual state transitions.

**2. Record/page arithmetic.** Coordinates `128·4=512` bytes; adjacency `64·4=256`; header16. Total784 bytes. `floor(4096/784)=5` whole records/page; `4096−5·784=176` unused bytes. Header, degree, alignment and spanning choices are declared assumptions, not an implementation inspection.

**3. Hypothetical I/O.** 100 serial reads at .15ms contribute15ms. With eight independent known-address reads per batch, `ceil(100/8)=13` rounds give an ideal1.95ms. A dependent graph walk may reveal one next address at a time, yielding many more rounds. Storage queueing, contention and residency also differ. Neither number is a DiskANN benchmark on this machine.

**4. Robust pruning.** At x0,s1,c3, distances are2 and3. Alpha1 prunes because2<=3; alpha2 retains because4>3. Squared arithmetic must use alpha squared: at alpha2 compare `4·4=16` with9, not `2·4=8`. The alpha/degree/candidate-pool policy is construction-time graph design; efSearch controls retained query exploration, and disk beam width controls grouped expansions/I/O. They are not interchangeable.

**5. Scoring-aware reconstruction.** Both reconstructions have squared error .04. For q=(1,0), q·x=1; q·(1,.2)=1; q·(.8,0)=.8. Score errors are0 and.2. Quantization error direction matters. A better compressed score cannot recover an unsearched partition or an item excluded below the rescoring depth. No ScaNN experiment has run here.

## B. Native benchmark interpretation

**6. Card.** Name `ch16-synthetic-n1024-d32-v1` or `ch13-stress-probes-v1`, not simply “the benchmark.” Freeze actual rows/queries/qrels, IDs, float32 input/canonical refinement policy, k2, native depth8, M8/c64/seed18012026, sorted insertion, one OpenMP thread and five repeats/query. The synthetic distribution is the preserved coordinate-resampled/noisy generator with no human labels. The fourteen judged questions were previously inspected. No untouched test or multilingual transfer is claimed.

**7. Quality gate — `ch16-synthetic-n1024-d32-v1`.** Flat has geometric recall1; graph e8/e32/e64 have `.78125/.96875/1`. The teaching .95 gate rejects e8 and admits e32/e64. In the checked native-call table Flat is faster than the two admitted graph settings, builds faster and has fewer serialized bytes. This is an observed small-workload decision, not a universal dominance theorem. Adapter p95 has noisy ordering and a different boundary. No confidence interval or service gate was measured.

Flat/HNSW native file bytes are131,117/214,130, plus16,055-byte manifests each. Native add/build costs are in the record; neither class learns centroids/codebooks. NumPy originals, Python rows, serialized copies, buffers/replicas and source stores are not included in those file counts. On the judged workload, native files are18,477/19,714 plus998-byte manifests, and all routes retain judged macro Recall@2 `.791667`.

**8. Precision/pools.** The current oracle IDs match Chapter17 history on every frozen question. Native distance computation and float64 accumulation over float32 coordinates are not bit-identical. Native-return R8 is the actual bounded pool; refining those IDs preserves its membership. If a globally tied boundary item is excluded before refinement, stable sorting inside the pool cannot recover it. The observed probes avoid that global ambiguity; the fixture tie test requests all four items.

**9. Batch throughput.** For a saved batch, `queries_per_second = query_count/(native_batch_ms/1000)`. The checked synthetic mean per-batch rates are about81,078 Flat and48,252 graph e32 queries/s. All sixteen vectors enter one matrix call; there are five repeated batch calls/mode. These are not sixteen request-latency samples, endpoint throughput or embedding throughput. Do not derive per-request p95 from the batch rate.

## C. First losing boundaries

**10. Public predicate populations.** `ch18-public-tag-stride8-v1` has128 predicate-eligible rows of1,024 authorized; `ch18-public-tag-stride64-v1` has16. Their oracles are different `Top2(A intersect P)` populations. There are32 geometric memberships/workload and zero human judgments. Static predicate-specific Flat recall is1 with no underfill in both. Flat R8 postfilter recall/underfill is `.5625/75%` versus `.09375/100%` on the two separately named workloads; Flat R32 is `.96875/6.25%` versus `.5/68.75%`. Report each within its workload, without a cross-stride gain inference.

**11. Trace diagnosis.** Use the case's request ID, not another timing trial's UUID. An eligible oracle ID missing from `native_returned` was lost before metadata filtering. An ID in native return but not `metadata_survivors` failed the public predicate. A surviving/refined ID below final k lost at the final cutoff. An empty survivor list is `no_metadata_survivor_in_shortlist`, not proof of no eligible evidence. Native Flat's unfiltered exhaustive scoring cannot prevent a bounded return pool from excluding constrained neighbors. Every raw candidate remains authorized public data; this is not postfilter authorization.

**12. Judged failures — `ch13-stress-probes-v1`.** The direct target for `code-segment` is `D6:row-2:0`; the literal ID is absent from searchable title/body text. The directly governing current signed amendment for `acronym-sla` is `D2:§2:0`. The exact and native candidate routes omit those direct targets at k2. The two no-positive needs return candidates; recall is undefined for them and their candidate-return rate is1. D10 stays outside native membership. Answer correctness, faithfulness, citations and abstention remain null, not successful.

**13. Visibility limits.** Native records expose raw returned IDs/scores, survivors, exact refinement, final candidates and aggregate work. They do not expose the complete native scored-ID set/frontier. `inspectable_reference_e24` is the real Chapter17 teaching route on a separately built graph, with its own index digest and request ID. It supports mechanism diagnosis, but its path is not evidence of how Faiss searched. A replacement requiring full internals fails that gate until adequate instrumentation exists.

**14. Trusted reload.** Verify independent expected manifest/source/model/scope/roster and native payload hash before deserialization. The tests change an original vector with the same ID and assert that the native reader was never called. A corrupted payload is also rejected. Successful reloading/queries demonstrate compatible local persistence, not durable acknowledgment, crash recovery, replicated visibility or deletion propagation.

**15. Delete scope.** Pinned Faiss HNSW remove raises an unsupported-operation error. An enclosing database can provide a logical delete using other lifecycle state, but must prove result exclusion, cache/replica visibility and retention/erasure semantics. Flat removal can renumber ordinals; external-ID map identity must follow. The frozen adapter chooses new snapshots rather than pretending to be a live mutation service.

## D. Responsibility and selection defense

**16. Categories.** Faiss supplies numerical index implementations in a process. pgvector supplies vector functionality inside PostgreSQL's query/storage context. Elasticsearch/OpenSearch/Vespa add search/serving-engine responsibilities. Qdrant/Milvus/Weaviate/Pinecone offer systems centered on vector/data search in particular deployments; Chroma/LanceDB include local/embedded options and other modes. Product categories overlap. State the chosen mode/version and consult its primary contract; a namespace or client package does not establish authorization/durability.

**17. Service card.** A defensible card specifies which acknowledged writes survive what failure; when reads/searches/replicas must observe updates/deletes; how eligibility precedes scoring; how metadata plans affect recall; what source/model/ID versions are compatible; how caches are tenant/version safe; what partial responses mean; and how restores/exports retain identity and deletion state. Query throughput and accepted/searchable ingest throughput are different measures. Names without tests/owners are insufficient.

**18. V4 decision.** Keep the exact dense route and lexical comparator. Current native results are useful experiments with real snapshots and narrower telemetry. The small inspected workloads supply no independent domain/answer gain or database-service evidence. Require representative independently judged data, eligible/predicate slices, service load/latency, resident/storage accounting, update/delete/restore and observability gates before changing the operational route. A negative decision is the expected evidence-based result of this run.

## Part IV cumulative answers

### Architecture from memory

A good sketch separates index time (source/content/locator/scope identity -> pinned input/encoder -> original vectors -> exact/tree/hash/list/code/graph structures) from query time (trusted eligibility -> compatible query vector -> candidate executor -> every lossy pool -> final rank -> context). Qrels/evidence identity and workload/version traces sit beside the stages evaluated. Show unchanged or unrun generation explicitly. A second service outline includes write/search/delete visibility, durable data, routing/replicas, backup/recovery and cache/telemetry duties still unimplemented. Candidate, evidence and answer remain different objects.

### Eight reasoning questions

1. KD uses a valid lower bound on all points in a box, so an excluded region cannot beat the exact heap under its assumptions. HNSW's stop compares discovered pending and retained vertices; it supplies no bound on the unseen vertices behind a discarded link.
2. Compare exact neighbors against bucket union, probed lists, compressed ranks, refinement pool, graph scored/frontier pools, predicate survivors and selected context in that order. The earliest absent stage identifies the responsible boundary. Use actual stages; hidden native internals remain unavailable.
3. Original vector payload `100000*384*4=153,600,000` bytes. Mean32 four-byte adjacency entries add12,800,000; two replicas of those two payloads total332,800,000 bytes. Levels/IDs/offsets/scopes/buffers/sources are extra. 48 eight-bit PQ codes need48 bytes/item or4,800,000 total; codebooks add `256*384*4=393,216`. These code-only numbers exclude originals/IDs/replicas. Retaining originals for refinement eliminates most of the claimed vector-storage saving; measure actual files/RSS and reconstruction/recall effects before adoption.
4. nprobe changes searched lists; efSearch changes retained exploration; returned depth changes the pool passed to filtering/refinement; disk beam changes grouped expansions/I/O. Query settings need not retrain a fixed structure, while changing centroids/codebooks, degree/hierarchy/construction rules requires an appropriately identified new build/training phase.
5. PQ M counts subspaces; HNSW M bounds connection selection/capacity and here affects hierarchy sampling. Exhaustive codes can misorder original distances. Namespace/SQL logical predicates do not by themselves prove a before-scoring authorization plan.
6. Geometric parity measures an index against its own metric oracle. Qrels assess relevant evidence under a content/eligibility contract. Context coverage is downstream; correctness/faithfulness/citations/abstention need generation and labels. V4 measures geometry, judged candidate quality and context IDs where packed, while preserving null new answer measures.
7. Separate same-workload/metric/cutoff/eligibility comparisons from changed workloads and kernel/batch/request boundaries. Collect a compatible representative service record with quality slices, arrival/load, failures, queue/encoding/search/context/generation timings, memory/cost and security gates. Do not average away a filtered regression.
8. Unchanged IDs and snapshot strings cannot bind changed content. Source/chunk/locator/scope/model/vector manifests must match the evidence judged and text fetched. A failed identity check requires source/judgment review, not updating the digest to silence it.

### Running-project comparison

V0 demonstrates a tiny source-to-context/stub evidence path. V3 adds lexical/learned representation comparisons, a rejected adapter and a checked exact dense snapshot. V4 adds candidate-execution alternatives, approximation diagnoses, native index measurements and persistence/system boundaries. Retain two-task V0 failures, inspected qrel failures and all negative results. Compare numerical outcomes only within named compatible workloads; historical Python and current native timings are not one speed curve. D10 exclusion is a boundary invariant, not relevance scoring. New answer outcomes remain unmeasured.

### Delayed teach-back

The author supplies tasks and rubric, not fabricated learner outcomes. On days1/3/7/21, reconstruct and correct missing boundaries. On days3/7, explain a hand miss and trace a recorded first-loss stage to a novice without jargon shortcuts. Reattempt any failed question after checking its actual mechanism and source identity.

## Part IV cumulative assessment rubric

| Component | Weight | Evidence required |
|---|---:|---|
| Architecture from memory | 25% | Index/query/evaluation separation, compatible identities, eligibility and all lossy stages; missing service duties visible |
| Cross-chapter reasoning and arithmetic | 30% | Safe bound versus approximate stop, list/code/graph/predicate distinctions, correct bytes and parameter roles |
| Running-project comparison | 25% | Workload-specific numbers, preserved negative/representation failures, trace IDs, measured/unmeasured boundaries and justified baseline |
| Delayed recall and teach-back | 20% | Scheduled independent redraw/explanation, predictions before trace inspection, correction log and successful reattempt |

Require a correct authorization boundary and no fabricated answer/native trace/generalization claim regardless of total score. Suggested pass threshold80% with all boundary gates satisfied. Chapter-local rubric: own page/cache mechanism25%, hand budgets15%, matched native/card work25%, actual trace/reload diagnosis20%, responsibility/decision defense15%. Reference execution alone earns no construction credit.
