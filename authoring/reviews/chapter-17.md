# Chapter 17 technical, pedagogical and completion review — 2026-10-03

This author-performed review continues from [the remediation verification](../../audits/QUARTER_BOOK_REMEDIATION_VERIFY_CH01_16.md), disposition **READY FOR CHAPTER 17 WITH NON-BLOCKING RESIDUALS**. It is not a new independent audit. Chapters 1–16 and sealed historical result files are preserved. Publishing residuals identified by the audit remain outside this chapter's scope unless the new material exposes a contradiction.

## Prerequisite and continuity review

The remediated Chapters 10, 13, 15 and 16 supply finite vector arithmetic, metric/normalization, exact top-k and deterministic ties, a checked source/model/index snapshot, eligibility before scoring, content-bound judgments, geometric versus judged recall, baseline timing and independent construction gates. Graph vocabulary, priority queues, squared L2 comparisons, logarithms/floor, geometric level probability and memory arithmetic are taught locally before executable reliance. There is no missing model-training mathematics because graph construction does not update the encoder.

An actual source discrepancy was found while preserving the Chapter 16 workload: the historical generator picks its stored row separately for each coordinate, rather than perturbing one whole stored vector. The Chapter 17 text/record and registry describe the actual distribution. Legacy version IDs, source code, vectors, exact oracles and all historical observations are unchanged; no remediation item or old chapter has been reopened. The new record's exact IDs are checked against Chapter 16 history.

## Technical review

- **Mechanism:** [The engine](../../projects/V4/hnsw_ch17.py) implements nearest-first frontier and worst-first retained heaps, visited sets, stable distance/ID ties, geometric random maximum levels, nested membership, highest entry, upper width-one descent, base width, diverse neighbor selection, reciprocal insertion and capacity pruning. New vertices select at most M; outgoing capacities are M above the base and 2M at the base. Individual pruning may leave asymmetric links; outgoing reachability is explained. No candidate extension/refill is used in the measured configuration. `efSearch` bounds retained neighbors, not distances, visits or all pending entries.
- **Math and costs:** The chapter derives unit-vector L2/cosine order, `P(L≥l)=M^(-l)`, geometric upper memberships and an expected capacity bound; logarithms and floor precede the sampler. The four-vertex trace has distances 4,1,1.21,.01; width-one misses D, width-two recovers it. Diverse selection rejects Q using `.05<1.45` and accepts R using `5≥4`. Forced hierarchy distances/expansion and the lab's level-zero insertion are computed from actual coordinates/code. Query complexity is stated by scored vectors, examined edges and heap work, with no universal logarithmic claim. Build counter excludes diversity comparisons; wall time includes them. M=4 large-workload payload is 131,072 vector + 30,632 adjacency + 4,096 level bytes = 165,800, a lower bound rather than RSS.
- **Scope/lifecycle:** Graph construction admits only twelve already eligible support-team vectors. D10 never enters graph training/navigation/scoring/context. The scope label is not authentication, and a different scope is rejected. Tombstones block traversal/scoring but retain physical data and may break routes. Trusted expected source/digest checks demonstrate query-only persistence; durable mutation/RNG continuation, live policy, concurrency, service storage and erasure are explicitly unimplemented. Retention/licensing and tenant-safe cache invalidation are discussed.
- **Experiment:** [The runner/record](../../projects/V4/chapter-17-experiment.json) use the registered four-vertex fixture, identical historical Chapter 16 synthetic rows/queries and `ch13-stress-probes-v1` with verified evidence manifest. Exact squared L2 ordered results are checked against cosine and historical oracles. M=2/4/8, construction width32, query widths2/8/24 form declared controlled configurations; M=4 construction width8 is ablated at query width24 with identical levels. M also changes hierarchy density, so degree isolation is not claimed. Fresh one/all-probe IVF-Flat controls use this chapter's coarse seed, not the historical centroids.
- **Negative results:** The large synthetic best tested graph recovers 31/32 memberships; `s00352` remains undiscovered on `synth-07`. The tiny judged low-degree graph plateaus despite wider search; geometric parity at M=4 leaves macro judged recall `.791667`, with local search overhead. `code-segment` and `acronym-sla` remain exact representation/authority failures. Both zero-positive questions return candidates. Generation correctness/faithfulness/citation/abstention are null. The decision retains exact dense and BM25; no inspected diagnostic is mislabeled held-out or multilingual generalization.
- **Telemetry:** Every quality/timed search preserves common request/query/mode/trial/workload/version/status/timing identity and actual raw/layer/base/final ID/score pools. Query encoding has its own correlated record. Initial queue states and real admissions/evictions replay intermediate frontiers, checked against saved retained pools. Graph adjacency/levels/digests support connectivity diagnosis. Score kind is negative squared L2; trace distances are positive squared L2. Context is outside search timing; in-operation trace allocation is inside it. No raw private text/exception string is emitted. Historical timing/schema boundaries remain separate.
- **Sources:** Original HNSW algorithms and current hnswlib parameter/API documentation were checked on 2026-10-02. Vendor defaults, benchmark speed and memory formulas are not adopted as local measured facts. The reference register records the implementation-specific limits.

## Pedagogical and visual review

The chapter preserves failure-first order: exact/tree/hash/coarse/compression limitations → greedy local minimum → bounded frontier → hierarchy → useful connection selection → construction/query parameters → work and memory → learner attempt → complete reference → controlled experiment → trace-led debugging and a project decision. Similarity, candidate, relevance, evidence, context and absent answer metrics remain distinct. An HNSW navigation graph is distinguished from an evidence/knowledge graph.

[The lab](../../labs/chapter-17/LAB.md) requires the learner to construct bounded layer search and diversity selection before reference inspection. Its unsolved starter fails intentionally; the independent answer imports no complete engine, and the checker tests fresh geometry, cycles/ties, a disconnection and retained bridge. Paper insertion, level arithmetic, matched workload sweeps, actual miss replay, deletion/reload and eligibility are separate tasks. The solutions provide reasoning, expected values and a rubric; a negative adoption decision receives full credit when justified.

The visual audit selects four figures: actual local-minimum frontier, actual forced hierarchy/descent, exact diverse-neighbor geometry, and checked recall/work/p95/payload. SVG/PNG and editable sources are retained, with caption-before-image, alt text, coordinates/adjacency, workload/seed/units/sample/uncertainty metadata. A generated highways illustration is N/A: explicit nested adjacency answers the learner question without introducing an analogy as algorithmic authority. Visual and manuscript validation results are recorded below after the final gates.

## Chapter completion checklist

### Learning and mechanism

- [x] Simpler exact/Chapter15–16 limitations motivate graph search; remediated prerequisites checked.
- [x] Intuition, vocabulary, precise state and glossary are complete; index/query time remain separate.
- [x] Distance, queue ordering, sampler mathematics, hand search/diversity/hierarchy and insertion are taught.
- [x] Independent bounded construction precedes reference; complete from-scratch engine precedes library mapping.
- [x] Work-dependent complexity, build cost, edge/vector/temporary memory and empirical scaling limits are explicit.
- [x] Alternatives, parameter roles, failure plateaus and the next dependency are clear; Chapter18 is not authored.

### Evidence and operation

- [x] Common correlated request/sample envelope and real intermediate lossy stages preserved.
- [x] Content-bound qrels and actual source/index/model identities are checked; historical results sealed.
- [x] Every headline table/plot names its canonical workload and compatible denominator/boundary.
- [x] Question/hypothesis/variables/controls/procedure/seeds, cases/aggregates, uncertainty and limitations saved.
- [x] Geometric/judged/context/generation distinctions and no train/dev/test/generalization overclaim verified.
- [x] Actual frontier replay, candidate pool and outgoing-connectivity debugging taught and tested.
- [x] Eligibility before membership/scoring/context, privacy, retention, deletion, cache and serving limits checked.
- [x] Negative experiments preserved; no forced winning ANN, hidden exact fallback or deployment claim.

### Visual and practice

- [x] Learner constructs bounded search/diversity on a fresh fixture; starter and reasoned answer separate.
- [x] Required arithmetic precedes executable code. Gradients/training updates: **N/A**, no model learning here.
- [x] Cumulative end-of-Part assessment: **N/A**, Part IV ends at Chapter18, not Chapter17.
- [x] Four focused figures, captions, alt text, editable sources and measurement metadata complete.
- [x] Paper exercise, debugging/design/interview challenge, lab, solutions, V4 update, recall and mastery included.

### Release hygiene

- [x] Final test totals, record integrity and sealed history checked.
- [x] Final diagram/plot renderings and Chapter17 reader layout inspected.
- [x] Manuscript/link/figure preflight and diff whitespace checks passed.
- [x] Chapter/lab/solutions/code/record/visuals/docs/review committed together.

## Final verification

- **148 passing tests:** V0 17, V1 17, V2 24, V3 26, V4 28 (including 16 Chapter17 tests), common 17 and book builder 19. The sealed historical observations remain byte-preserved. Chapter17 registry/version/count checks, source hashes, identical old geometric oracles, independent-solution fixtures and actual frontier replay pass.
- **Construction gate:** the untouched starter raises the expected NotImplementedError; the independent separate answer passes all fresh feedback fixtures. No solved code is placed in the learner starter.
- **Manuscript preflight:** 17 chapters, 32 numbered captions; zero errors and warnings after source renders.
- **Experiment continuity:** 624 request samples per synthetic workload, 560 on the judged workload (including 14 encoding samples), plus two registered hand searches. All saved samples preserve the common envelope and actual candidate/frontier stages; every headline result names its workload.
- **Reader layout:** the repository renderer and PyMuPDF page inspection are used because Poppler is unavailable. The Chapter17/lab pages and all four figures are inspected; a new plot-label issue was fixed by larger labels and a more compact four-panel layout. The final reader build has 278 pages, zero errors, 22/22 text samples, and no Chapter17 warnings. Physical pages 206-227 (chapter and lab) were visually inspected, including all four figures; minimum explicit rendered labels are 7.10, 7.50, 7.50 and 6.81pt, above the 6.5pt floor. Eight inherited warnings concern earlier pages and Chapter13/V3 wrapped code, matching the non-blocking publishing residuals; no earlier manuscript was rewritten.
- **Remaining scope limits:** one graph seed/insertion order, sixteen geometric queries/workload and fourteen previously inspected judged questions; no native HNSW, RSS/load benchmark, live ACL, durable/concurrent mutation, answer generator or calibrated abstention. These are named limits, not incomplete Chapter17 mechanisms. End-of-Part IV assessment remains for Chapter18.


- **Release:** final relative links/numbering/figure/source freshness and `git diff --check` pass. Chapter17 artifacts and affected shared registers are committed as one chapter update; Chapters1-16 and sealed result bytes remain untouched. No Chapter18 manuscript, lab or project stage was created.
