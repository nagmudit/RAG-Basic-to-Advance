# Chapter 18 technical, pedagogical and completion review — 2026-10-12

This author-performed review continues from the [quarter-book remediation verification](../../audits/QUARTER_BOOK_REMEDIATION_VERIFY_CH01_16.md) and [Chapter17 review](chapter-17.md). It is not a new independent audit. Chapters1–17 and their experiment records remain unchanged. Existing publishing residuals are not reopened; new Chapter18 issues are fixed before completion.

## Prerequisites and architecture continuity

Chapter3 supplies numeric/data/measurement/database vocabulary. Chapters10/13 supply metric, checked vector/source/model/scope identity and content-bound judgments. Chapters15–17 supply exact/tree/hash/list/code/graph mechanisms, approximation boundaries, independent construction and correlated traces. Chapter18 teaches SSD/page/residency/beam, native precision/measurement boundaries and service responsibilities locally. No database or framework implementation precedes its mechanism explanation. No mathematical gradient/update prerequisite is missing: the encoder is frozen and the native indexes do not train it.

Part IV ends here. The manuscript/lab/separate rubric contain architecture from memory, eight cross-chapter reasoning questions, V0/V3/V4 capability/failure comparison followed by compatible same-workload comparisons, and day1/3/7/21 recall with day3/day7 novice teach-back. These are learner tasks, not fabricated completion observations. The architecture counts remain12 Parts,28 Modules,57 planned chapters;18 are authored. Chapter19 is not begun.

## Technical review

- **Mechanisms:** The chapter motivates disk/responsibility budgets from Chapter17. It teaches contiguous native exact execution, SIMD/bandwidth, RAM codes versus SSD full records, dependent I/O rounds, beams, cache coalescing/residency, Vamana robust pruning and partition/quantize/rescore. Alpha is squared if squared distances implement its ordinary-distance rule. Equal reconstruction errors with different inner-product errors are hand-calculated. DiskANN/Vamana source algorithms and layout were inspected; no logical cache example is mislabeled a DiskANN/SSD run.
- **Native implementation:** [Native code](../../projects/V4/native_ch18.py) pins the experimental Faiss/NumPy versions in the runner, builds Flat/HNSW from already authorized static rows, maps native ordinals to sorted external IDs, stores float32 vectors and refines only the actual returned pool with float64 accumulation/stable ID ties. Native global tie completeness is not claimed. Original unit/cosine oracle IDs and all prior cases remain historical; current frozen top-two ordering matches them. M8/c64/seed18012026 and one native OpenMP thread are explicit. The inspectable Chapter17 source is unchanged.
- **Snapshot integrity:** Four actual native binary/ID-manifest bundles are saved. Reload checks independently expected manifest/source/model/scope, current vector/eligible roster, payload/software/shape before native decoding. Changed vectors under unchanged IDs and corrupted bytes fail, with a test asserting no native reader call on roster mismatch. Local persistence/compatible query replay is distinguished from durable acknowledgment, write visibility, live mutation, replicated consistency, backup/crash recovery and physical erasure. Pinned Faiss HNSW removal is explicitly unsupported/tested; the frozen adapter does not pretend to be a live database.
- **Experiment design:** [The record](../../projects/V4/chapter-18-experiment.json) states question/hypothesis/baseline/controls/procedure/acceptance/uncertainty/decision. It reuses `ch16-synthetic-n1024-d32-v1` and content-bound `ch13-stress-probes-v1`, and registers both public-tag predicate workloads plus logical cache. Five randomized repeats/query produce80/70 adapter/native timing samples per unfiltered mode; five batch calls/mode are separate. Public-filter modes use48 timed samples each. Native binding-call timing, adapter work, batch throughput, query encoding and historical Python boundaries are distinct. No train/dev/test, unseen-family or multilingual claim is made.
- **Negative evidence:** Native graph e8/e32/e64 geometric recall on the synthetic set is .78125/.96875/1. At observed parity native Flat is faster at the call boundary and has lower build/file cost. Judged macro recall remains .791667; direct metadata-ID/current-amendment misses and two no-evidence candidate returns survive. Public-tag Flat R8 loses eligible neighbors despite exhaustive unfiltered scoring; underfill persists at bounded depths. These are actual retained failures, not forced wins. Exact dense/BM25 remain the operating baselines; all new answer/abstention outcomes are null.
- **Telemetry continuity:** Every measured search retains the common request/query/mode/trial/workload/version/status/timing envelope and actual native-return/predicate-survivor/refinement/final ID/score pools. Native scored IDs/frontiers are unavailable and explicitly marked null with `raw_pool_semantics=native_returned_shortlist_only`. Separate actual Chapter17 reference traces retain diagnostic capability, with distinct construction/request identity and an explicit warning against native attribution. Aggregate native counters are isolated in this serial one-thread experiment. Batch parent samples contain query-ID/output maps, not fabricated individual latencies. Logical cache samples record transitions and Python planning time without storage-I/O claims. D10 is absent before indexing/scoring/context; public task predicates are not ACLs.
- **System concepts:** Algorithm/library/engine/service ownership, namespaces, predicates, query/ingest throughput, write/search/delete visibility, consistency, ID portability, routing/shards/replicas, partial results, backup and cache responsibilities are mapped to current primary examples. Logical SQL syntax is not a physical authorization proof. Exact distributed top-k has stated assumptions; ANN oversampling is not guaranteed exactness. Actual service/distributed operation is left for later prerequisites.
- **Costs/math:** Vector/adjacency/replica payloads, record/page packing, hypothetical serial/parallel reads, alpha pruning, score-error direction, selectivity expectations and throughput/p95 formulas precede executable reliance. Actual native and manifest file bytes are separated from RSS, retained NumPy/serialized copies, source stores and replicas. No pricing or storage-latency number is imported as a local fact.

## Pedagogical and visual review

The progression is simple measured mechanism → RAM/system limitation → local definitions/arithmetic → independent page/cache construction → native abstraction with declared visibility → controlled comparison → failure localization → ownership/selection defense. The [lab](../../labs/chapter-18/LAB.md) has a deliberately unsolved starter and fresh hand-expected coalescing/LRU fixtures. [The independent answer](../../solutions/code/chapter_18_mechanisms.py) imports neither native/storage engine nor learner code. Native benchmark execution complements the already learned ANN mechanisms; it does not replace this chapter's construction gate.

Four [editable figures](../../visuals/chapter-18/plot-18-01-02-boundaries-and-pages.py) and [measured plots](../../visuals/chapter-18/plot-18-03-04-native-and-filters.py) show page/cache state, responsibility delegation, public-predicate recall and native quality/latency/file size. Each has numbered caption-before-image, alt text, SVG/PNG, source, units/data/workload/sample and limits. Responsibilities are not drawn as a newly implemented service. Generated illustration is N/A: exact state/layout and measured plots answer these learner questions. Final print/readability observations are recorded below.

## Chapter completion checklist

### Learning and mechanism

- [x] Chapter17 limitations and current audited prerequisites motivate the new scope.
- [x] Intuition/terms, precise data movement and index/query/system boundaries are explained and registered in the glossary/map.
- [x] Mathematics, units, hand arithmetic, edge cases and precision/tie limits precede code.
- [x] Independent bounded page/cache construction precedes reference; native classes follow established mechanisms.
- [x] Cost/work/memory/storage/I/O/throughput and selection limits are quantified without universal guarantees.
- [x] Alternatives, misconceptions, next prerequisite and V4 decision are explicit; no Chapter19 work.

### Evidence and operation

- [x] Common correlated envelope preserved; actual accessible lossy stages saved and unavailable native internals marked truthfully.
- [x] Source/content/locator/scope-bound qrels checked; historical oracles/negative observations preserved.
- [x] Canonical workload IDs identify all headline measurements; incompatible workloads and timing boundaries remain separate.
- [x] Question/hypothesis/baseline/variables/controls/procedure/cases/results/uncertainty/limitations/decision saved.
- [x] Geometry, judged evidence, context and absent answer/citation/abstention outcomes are separate.
- [x] Failures/debugging, privacy/licensing/retention, eligibility, cache and persistence/serving limits reviewed.
- [x] Native counters/visibility limits cannot silently replace inspectable project telemetry.

### Visual and practice

- [x] Own bounded implementation, fresh checker, hand/design/interview work, native lab and separate reasoned solutions/rubrics present.
- [x] Training gradients: **N/A**, no parameter updates or retriever learning in this chapter.
- [x] Required cumulative end-of-Part architecture/reasoning/project/delayed recall and separate rubric delivered.
- [x] Four chosen figures have complete source/caption/alt/units/workload/uncertainty metadata.
- [x] Recall/mastery and paper/prerequisite/source path updates complete.

### Release hygiene

- [x] Final behavioral/record/registry/historical tests and independent learner-construction checker pass.
- [x] Visual renderings and Chapter18 printed pages inspected; label-size/overlap issues fixed.
- [x] Source/link/figure/numbering preflight and whitespace checks pass.
- [x] Chapter/lab/solutions/code/bundles/record/visuals/docs/review included together in the Chapter18 completion commit.

## Final verification

- **Tests:** 167 pass: V0 17, V1 17, V2 24, V3 26, V4 47, common 17 and book tooling 19. V4 includes 19 new Chapter18 tests. Historical-byte checks and frozen exact-neighbor comparisons pass. The untouched learner starter raises its intended `NotImplementedError`; the separately written solution passes the fresh hand-expected checker.
- **Recorded samples:** 410 synthetic, 374 judged-diagnostic, 320 in each public-tag workload and two logical-cache samples: 1,426 correlated envelopes. Each native workload's ten batch parents are included in its envelope count, not added again or converted into individual latency samples. The frozen synthetic Float32 global shortlist boundaries have no ties at depths 8/32; the judged boundary has none at depth 8. This observation is confined to the checked questions and depths, not a general tie guarantee.
- **Source and print checks:** Preflight reports 18 chapters, 36 numbered captions, zero errors and zero warnings. The final reader build has 303 pages, 31 figures, five numbered tables and 23/23 text-layer sample checks, with zero errors. Its eight warnings are inherited from prior material: six nearly empty pages and existing wrapped code in the Chapter13 lab/V3 README. No Chapter18 warning remains. Chapter18 and its lab occupy physical pages 228–248; all 21 pages were inspected in contact sheets, and all four figure pages were inspected at full size. Labels, arrows, plots and caption-before-image ordering are readable without overlaps. The four figures' minimum printed explicit label sizes are 7.12, 7.41, 6.57 and 6.72 points, exceeding the 6.5-point floor.
- **Review scope:** Technical and pedagogical review are author-performed. No independent human/sub-agent review or learner mastery outcome is claimed. The cumulative assessment and delayed recall schedule are delivered with separate answers/rubric; delayed outcomes remain for the learner to produce.
- **Remaining limits:** One graph seed/insertion order, small inspected question sets, warm serial native calls and no confidence intervals limit generalization. Native internal frontiers remain unavailable; the separate inspectable reference route is preserved and never attributed to Faiss. Logical page requests are not physical SSD measurements. DiskANN, ScaNN, live database/distributed service behavior, RSS, generation, abstention and held-out generalization are not measured here. These limits leave the exact dense/BM25 baselines and the historical negative results intact.
