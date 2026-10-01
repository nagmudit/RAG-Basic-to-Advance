# Quarter-book remediation verification - Chapters 1-16

## Disposition and scope

**Seven P1 findings closed; zero partial; zero remaining in this backlog.** The three P2-02 factual corrections, clipped Figure 16.01 correction, workload registry and future completion checks are complete. This is a targeted verification, not another quarter-book audit or a new curriculum plan.

The complete [independent audit](QUARTER_BOOK_AUDIT_CH01_16.md) was read before implementation. Its seven P1 findings were handled in the requested order: P1-02, P1-03, P1-01, P1-07, P1-06, P1-04, P1-05. Verification then covered the explicitly authorized factual/figure fixes, workload identities and checklist. No Chapter 17 was created and no changes were committed.

Baseline: commit `6202e5ec067119991722c99c3a2a15c42266c902`; verification date 2026-10-01. The original audit was already untracked when work began and remains byte-identical; it is not a newly authored remediation file. Existing source files were hashed before editing. Tests/runs used the existing Windows Python 3.14.2 environment, CPU PyTorch 2.10.0, sentence-transformers 5.2.2 and the already cached pinned MiniLM revision. No dependencies or new model weights were installed/downloaded. Temporary replay/build files are outside canonical source paths, under `C:/Users/mudit/AppData/Local/Temp/rag-remediation-ch01-16-x65ck8pa`.

Observed results below come from executed tests, fresh offline experiments, comparisons with historical cases, and rendered images/PDF pages. A PASS means the specified remediation and its verification succeeded; it does not establish population-level retrieval quality or empirical learner mastery.

## P1-02 - Mathematics and gradient bridge

**Finding:** Executable retriever adaptation relied on matrix/gradient/update operations without the bounded prerequisite bridge needed for a self-contained book.

**Files changed:** `chapters/chapter-10-vectors-distance-and-exact-similarity.md`; `chapters/chapter-11-how-embedding-models-learn-retrieval-spaces.md`; `chapters/chapter-12-retriever-training-and-domain-adaptation.md`; `labs/chapter-12/LAB.md`; `solutions/chapter-12-solutions.md`; `projects/V3/training_bridge.py`; `projects/V3/test_training_bridge.py`.

**What changed:** Chapter 12's “From a vector to one parameter update” teaches matrix dimensions, row dot products, transpose, logits, stable row loss, local derivative, chain rule, outer-product gradient and one actual update. A 2x2 identity matrix acting on `(1,2)` is completely calculated, including the changed scores/probability/loss. The positive passage remains second despite lower loss. The subsequent bridge maps the hand calculation to the real rank-16 residual adapter, normalization derivative, A/B gradient shapes, frozen passages, initial zero-B behavior, `zero_grad()`, `loss.backward()` and Adam `optimizer.step()`. It distinguishes the simple hand SGD update from the actual cosine/Adam training run. Chapters 10/11 provide concise prerequisite links rather than generic neural-network material.

“Stable probabilities compute the same objective” explains the common exponential factor cancellation in `softmax(z-max(z))`, computes `[4,3,1] -> [0,-1,-3]`, and connects subtract-max to log-sum-exp. Large logits `[1004,1003,1001]` produce the same probabilities without direct exponential overflow. The lab requires a hand attempt before checking the companion script; the separate solution explains intermediate steps.

**Independent verification:** `test_training_bridge.py` passed all three tests, including analytic versus central finite differences for two matrices, normalized/unnormalized vectors, and nonunit temperature. The worked example's maximum derivative discrepancy was `4.35e-11` at epsilon `1e-6`. With learning rate .1, scores changed from `(1,2)` to `(1.365529,1.634471)`, positive probability from `.268941` to `.433167`, and loss from `1.313262` to `.836632` nats. Stable shift equivalence passed; direct `exp(1004)` overflow was confirmed. The actual Chapter 12 offline replay retained epoch 1, the exact historical adapter digest and the failed held-out improvement. Reader pages containing the worked matrix/update were rendered and inspected, with no clipped equations or code.

**PASS / PARTIAL / FAIL:** **PASS**.

**Remaining concern:** This intentionally teaches the operations used by this adapter, not a generic deep-learning curriculum. Lower training loss is explicitly separated from changed top-k and held-out relevance.

## P1-03 - Common correlated request/sample envelope

**Finding:** V3/V4 timed samples lost correlation and some lossy candidate stages, preventing diagnosis from the actual execution.

**Files changed:** `projects/common/experiment_trace.py`; `projects/common/test_experiment_trace.py`; V3 `experiment_ch10.py` through `experiment_ch14.py`; V4 `experiment_ch15.py`, `experiment_ch16.py`, `ann_ch15.py`, `ivf_pq_ch16.py`; `projects/V3/test_trace_pipeline.py`; `projects/V4/test_trace_shortlists.py`; `observability/SAMPLE_ENVELOPE.md`; V2/V3/V4 READMEs; historical-result helper/manifest and affected historical-hash tests.

**What changed:** Fresh measured requests have request/query/mode/trial IDs, workload ID, corpus/query/qrel/index/model identities, status/reason, stage timings, raw candidate IDs/scores, intermediate stages, final candidates and context/evidence IDs where run. Not-run stages use null. Timers finish before context/trace serialization; existing separately measured encoding/scan stages remain separate. Route-specific index identities are retained where lexical and dense routes differ. The Chapter 12 trace retains the full scored pool but identifies only the returned top two as final candidates.

LSH retains the actual eligible bucket union. IVF/PQ now saves eligible scanned candidates, selected IVF lists, the actual ADC top-R before exact reordering, all exact-refinement candidates and scores, final top-k and the packed context subset. This is instrumentation of the existing route, not a recreated shortlist or new ANN algorithm. Ordinary records contain no source/query text, prompts or exception messages. Eligibility is checked before diagnostic context callbacks/forward fetch; failed or invalid operations record generic redacted reasons and re-raise. Multi-stage manually timed paths use a failure guard. Standalone timing helpers preserve their prior calling interfaces.

**Independent verification:** The helper tests passed field/alignment, invalid/failed status, exception redaction, protected-ID rejection, eligibility-before-context-callback and multi-stage failure cases. The Chapter 13 pipeline test forces an invalid dense scan and observes a correlated redacted `invalid` record for that query/mode, not only a helper-only simulation. Chapter 16 tests verify actual four-item ADC/refinement pools, final two candidates, a one-item context subset and list selection; invalid ANN queries emit status. The LSH test verifies its retained eligible union omits the private decoy.

Fresh offline Chapter 10-16 records supplied **2,963** measured samples: 56/68/33/28/124/1,542/1,112 respectively. Independent record inspection checked required keys, registered workload identities, candidate/score alignment, context membership and absence of D10/source text. Candidate IDs and quality outcomes matched the original cases. On `spanish-fee`, one-probe list omission is distinguishable from full-probe ADC shortlist loss; refinement recovers the exact pair only when it entered top-R. On `code-segment`, the missing exact second neighbor lies outside the retained approximate top-four pool, so refinement cannot recover it. The context-subset unit test separately localizes a later packing loss.

**PASS / PARTIAL / FAIL:** **PASS**.

**Remaining concern:** This is a minimal in-process teaching envelope, not distributed OpenTelemetry or a durable telemetry service. Preflight/model/corpus setup failure before query identity exists remains a setup error; nonrequest batch/build measurements keep their aggregate provenance. Historical records retain their historical schema. Fresh diagnostic candidate retention adds local allocation work; fresh timings do not replace historical performance observations.

## P1-01 - Independent bounded mechanism construction

**Finding:** Several implementation/mastery promises were satisfied by inspecting supplied engines rather than writing a bounded mechanism independently.

**Files changed:** Chapters/labs/solutions 05/06/07/08/14/15/16; each lab's new `implement.py` and `check_implementation.py`; `solutions/code/chapter_05_mechanisms.py` through the corresponding 06/07/08/14/15/16 files; `projects/common/learner_checks.py`; `projects/common/test_learner_mechanisms.py`.

**What changed:** Each chapter has an early construction gate, an unsolved starter, a precise input/output/edge-case contract, hand prediction, own-fixture work, fresh assessment fixtures and a separate reasoned answer/rubric. Starters intentionally raise `NotImplementedError`; they are learner deliverables, not broken running engines. Existing calculation, debugging, experiment and full-project tasks remain.

| Chapter | Independent mechanism | Verified outcome |
|---|---|---|
| 05 | `build_postings`, `phrase_match` | Zero-based positions, consecutive/repeated terms, sorted output, absent/empty phrase cases |
| 06 | `tfidf_score` | Raw TF, eligible DF, unsmoothed ln(N/DF), distinct query weights, complete norms/dot/cosine, zero/OOV policy |
| 07 | `bm25_score` | Complete multi-term IDF/TF/length/average-length score at three k1/b settings; absent term, query repetition and parameter validation |
| 08 | `safe_top_k` | Supplied conservative bound -> threshold -> strict safe skip; callback counts; exact ordered exhaustive parity in 73 fresh/tie cases |
| 14 | `weighted_sparse_score`, `maxsim` | Eligibility before accumulation; hand-checked 2x3 dot grid, row winners, sum and deterministic tie |
| 15 | Seeded planes, signatures, buckets and `lsh_search` | Reproducible plane/bucket construction; actual candidates; exact-oracle comparison with a boundary miss and Recall@1=.5 |
| 16 | `nearest_centroid`, `encode_subvectors`, `adc_distance` | Tiny 2D/4D codebook arithmetic; ADC=.15 equals decoded-vector distance; original-distance error and an actual compressed ranking miss |

**Independent verification:** All seven separately implemented answers passed their new fixtures. The two construction assessment tests also confirmed all seven starter attempts remain unsolved and that answer files import neither project engines nor learner implementations. Checker expectations use hand calculations or an exhaustive oracle, not hidden reference imports. The safe-pruning tie test scores a bound equal to the threshold; it skips only a strictly lower bound. LSH/PQ approximation misses are measured and retained rather than forced into exact parity.

**PASS / PARTIAL / FAIL:** **PASS**.

**Remaining concern:** Assessment fixtures are publicly reviewable and “unseen” relative to the worked prose, not secret grading infrastructure. Independence and explanation need the instructor/learner rubric; passing output alone is insufficient. Pruning correctness assumes a genuinely conservative supplied bound, whose failure case is explicitly taught.

## P1-07 - Content-bound qrels

**Finding:** Unchanged snapshot strings and IDs could let stale judgments survive changed source evidence.

**Files changed:** `projects/common/qrel_identity.py`; `projects/common/test_qrel_identity.py`; `projects/V1/lexical_index.py`; V2 `eval_ch09.py`, `judgments_ch09.json`; V3 `experiment_ch11.py`, `experiment_ch12.py`, `judgments_ch11.json`, `judgments_ch12.json`, `judgments_ch13.json` (13 uses the common Chapter 09 loader); `evaluation/EVIDENCE_IDENTITY.md`; relevant historical-result tests.

**What changed:** All reviewed eligible items, including zero-grade items, are bound to document/source version, normalized title/body and whole-source digests, locator/word range/order, sorted permissions, and authority/effective-date metadata. A canonical eligible corpus manifest records those identities and its SHA-256. The index carries additive source identities without changing analyzer, segmentation, ranking or index version. All four loaders validate the same contract before metrics/training.

The declared normalization collapses Unicode whitespace runs and trims ends; CRLF/LF, tabs and incidental spaces remain compatible. Case, punctuation, numbers, spelling and Unicode code points remain significant. Locator/version/status/date/permission changes require review. Permission list order is insignificant; membership is significant. Whole-source edits conservatively invalidate that source's judgments. The manifest contains hashes/identity metadata, not protected raw source text. `binding_revision` distinguishes the added contract while preserving the existing judgment versions and every old query/grade/split field.

**Independent verification:** All four loaders rejected D1's `four hours` -> `nine hours` edit while D1 and the snapshot string stayed fixed. All loaded unchanged evidence and whitespace-only source/title changes. Additional probes rejected locator, permission membership, signed/draft status and effective-date changes. Independent Git-baseline comparisons confirmed every preexisting field of all four qrel JSON files stayed semantically identical. Fresh 10-13 experiments still reproduced their original quality outcomes; original result-file hashes are preserved as historical provenance rather than rewritten to the new metadata hash.

**PASS / PARTIAL / FAIL:** **PASS**.

**Remaining concern:** Evidence identity detects incompatibility; it does not reassess relevance. A future source change must trigger human judgment review, not automatic digest replacement. Protected sources outside the eligible roster are not support-team judgments.

## P1-06 - Generalization unit and source-family semantics

**Finding:** Document-disjoint targets were more narrowly independent than the family-grouping advice and some source-disjoint wording suggested.

**Files changed:** Chapter 12/lab/solution; `projects/V3/judgments_ch12.json`, `experiment_ch12.py`, V3 README; `projects/common/split_semantics.py`, `test_split_semantics.py`; Figure 12.02 plot/SVG/PNG.

**What changed:** Chose the authorized narrower protocol: **new-query/document-target holdout with source-family overlap**. Explicit family metadata groups D1-D7/D9 as `helios-support` and D8 as `atlas-support`. Train/validation/test document IDs are disjoint, while Helios appears in all three. Text, diagram, manifest, experiment controls, lab and solution agree that this does not establish unseen-family/domain transfer. Atlas's incidental test-only occurrence is not presented as a separately powered transfer result. The solution reserves “keep all revisions/translations together” for a future family-holdout claim.

`validate_generalization()` reports overlaps and requires disjoint declared families if a workload claims `source-family-holdout`. No existing question, label, train pair, negative policy, split, seed, checkpoint or model/index identity changed.

**Independent verification:** Three focused tests passed: current overlap is reported; relabeling the same data as family holdout is rejected; a synthetic disjoint-family declaration validates and an incomplete family map fails. Fresh actual adaptation selected epoch 1, reproduced the exact adapter digest, and retained frozen/adapted test Recall@2=.888889 versus BM25=.666667. Later checkpoints still drive validation Recall@2 to zero. Figure 12.02 was regenerated and inspected as SVG, PNG and reader PDF; it states family overlap and shows the unchanged label ownership paths.

**PASS / PARTIAL / FAIL:** **PASS**.

**Remaining concern:** Family metadata is an authored grouping requiring semantic review; a validator cannot infer semantic independence from a name. This experiment remains small, author judged, and deliberately narrower than domain transfer.

## P1-04 - Complete BM25 development selection

**Finding:** Chapter 07 deferred parameter fitting, but Chapter 09 did not deliver a legitimate select/freeze/test exercise.

**Files changed:** Chapters 07/09; `labs/chapter-09/LAB.md`; `solutions/chapter-09-solutions.md`; `projects/V2/tune_bm25_ch09.py`, `judgments_bm25_tuning.json`, `chapter-09-tuning-experiment.json`, `test_bm25_tuning.py`; registry/README references.

**What changed:** A separate authored workload `ch09-bm25-devtest-v1` has six development and six test questions, each completely judged against twelve eligible segments (144 pairs). Existing fourteen-query Chapter 09 cases remain inspected diagnostics. The learner writes a small grid driver, predeclares metric/ties, saves a frozen decision, then evaluates test. The reference selection function receives development data only. It evaluates k1 [.8,1.2,1.6,2] and b [0,.25,.5,.75,1] at fixed analyzer/title policy/scope/top-k, selects macro positive-query NDCG@2, freezes controls/digest, then reports selected/default test cases and slices, work, redacted samples and warmed local timings.

All twenty settings tie on development. The preregistered default-first tie rule retains k1=1.2, b=.75. Both selected and default test Recall@2=1.0 and NDCG@2=.9261859507. There is no tuning gain. This is a query-wording holdout on already known sources, not an independent corpus/family study; the score is not a new point on the original Chapter 09 progress curve.

**Independent verification:** All three tuning tests passed, including mutated test text/labels leaving selection unchanged, cross-split duplicate-ID rejection, frozen selection metadata, test slices and correctly identified trace queries. The actual seven-trial reference run generated a separate new record; its 84 test request samples preserve query/mode/trial identity. The original diagnostic record and overlap-over-BM25 result were not overwritten. Existing BM25/WAND exact parity tests still pass.

**PASS / PARTIAL / FAIL:** **PASS**.

**Remaining concern:** Six questions per split and one assessor teach methodology, not release-quality parameter selection. Returning candidates for the zero-evidence test is retained as a failure, not interpreted as abstention.

## P1-05 - Completed Part I/III cumulative checkpoints

**Finding:** Part-level retention was promised but incomplete at the actual Part ends.

**Files changed:** Chapters/labs/solutions 04 and 14.

**What changed:** Part I reconstructs information need -> eligible source -> candidate -> evidence -> context -> claim -> citation/abstention from memory; six cumulative questions require boundary failures, model-only versus evidence-backed reasoning, V0 comparison and measured/unmeasured distinctions. Existing fictional response cards are reused without inventing a real-model experiment. Part III reconstructs representation/training/index/query/evaluation, distinguishes BM25 score/similarity/exact neighbor/judged relevance, compares lexical/dense failures on the same stress workload, traces V2 -> V3 with retained negative results, and explains which ANN/PQ approximation is not yet in the exact baseline. Both require teach-back and delayed day-3/day-7 recall with separate answer/rubric gates.

**Independent verification:** Manuscript/lab/solution inspection confirmed one aligned checkpoint at each completed Part end, six cumulative questions each, first drawing before reference access, boundary/failure comparisons and a ten-point rubric with required eligibility/exactness/support conditions. The Part III failure comparison uses the unchanged Chapter 13 stress cases, whose IDs/metrics were independently replayed. Book preflight resolved the new links and the reader build includes these end-of-Part tasks. No full extra chapter or future-Part content was created.

**PASS / PARTIAL / FAIL:** **PASS**.

**Remaining concern:** A textual rubric cannot establish learner retention experimentally; its evidence is an actionable assessment sequence rather than a claim about learning outcomes.

## P2-02 - Three small factual corrections

**Finding:** Wrong binary size, wrong experiment-design chapter pointer, and bounded-saturation wording for unbounded log compression.

**Files changed:** Chapter 12 and Chapter 14; Chapter 12's existing solution already used the correct binary unit.

**What changed:** Chapter 12 now gives `12,288 x 4 = 49,152 bytes = 48 KiB`; the experiment-design pointer is Chapter 48, matching the canonical “Experiments, ablations, and regression gates” syllabus entry rather than Chapter 41's SQL/API material. Chapter 14 says `log1p` growth continues without a finite ceiling, increasingly slowly, and contrasts finite BM25 TF saturation toward k1+1. Repeated affected source wording was searched.

**Independent verification:** Arithmetic was recomputed; syllabus headings were inspected; updated manuscript/solution wording was checked. The stable calculation scripts and existing BM25 tests pass. No remaining `49 KiB` or affected `Chapter 41` pointer was found in the relevant manuscript/lab/solution material. The actual Chapter 12 reader page shows 48 KiB and Chapter 48.

**PASS / PARTIAL / FAIL:** **PASS**.

**Remaining concern:** Other P2 findings were not expanded into this pass.

## Figure 16.01 - Query annotation clipping

**Finding:** The 38-degree query annotation ran into the right edge of the coarse-cell panel.

**Files changed:** `visuals/chapter-16/plot-16-01-cells-and-codes.py`; its SVG and PNG.

**What changed:** Repositioned the annotation inward, below/left of the query, with a light label backing and short leader. Canvas size, axis limits, circle points, centroids, query angle, list geometry and PQ arithmetic were preserved; no blind canvas expansion.

**Independent verification:** Regeneration again found angle 38, exact IDs `[01,02]`, one-probe `[01,00]` and two-probe recovery. The focused render test measures the label's actual bounding box inside the axes and checks geometry and both exports. Standalone PNG, independently browser-rendered SVG, and the final reader figure page at print scale were visually inspected: the full `q (38°)` annotation is visible and unambiguous. Chapter 12's clarified split figure was also inspected in all three formats.

**PASS / PARTIAL / FAIL:** **PASS**.

**Remaining concern:** Other visual/publishing findings from P2-05/P2-06 remain outside this authorization. Figure 16.01's explanatory layout and arithmetic are unchanged.

## Workload registry

**Finding:** Different chapter workloads could be mistaken for a longitudinal quality-improvement sequence.

**Files changed:** `evaluation/WORKLOAD_REGISTRY.json`, `WORKLOAD_REGISTRY.md`; headline-workload notes in affected Chapters 03 and 05-16; fresh V3/V4/tuning result identities; README/project README references; `projects/common/test_workload_registry.py`.

**What changed:** Sixteen canonical workload entries record chapters, corpus/query/qrel identities, query/judgment counts, slices, purpose, valid comparisons and invalid inferences. They cover V0 tasks; original Chapter 09/10; Chapter 11 and its Chapter 13 parity reuse; Chapter 12's separate train/dev/test counts; shared Chapter 13/15/16 stress data; two Chapter 14 fixtures; separate BM25 tuning; six Chapter 15 synthetic cases and two Chapter 16 synthetic cases. Geometric oracle memberships are separated from human relevance judgments. Chapter 12's 180 validation/test judgments are not falsely counted as 25x12. Existing record metrics are assigned identities without rewriting historical JSON.

**Independent verification:** Registry tests passed unique/required fields, source existence, exact qrel versions/manifests/counts/slice rosters, Markdown identity coverage, and all sealed historical results. Independent replay inspection found every fresh sample's workload ID in the register. Shared stress cases remain comparable under the same corpus/model/qrels/cutoff; synthetic N/d/seed/query definitions stay distinct. The new BM25 test is explicitly incomparable as an improvement over old Chapter 09.

**PASS / PARTIAL / FAIL:** **PASS**.

**Remaining concern:** Future authors must register definition changes and keep cutoff/eligibility/model/metric/timing boundaries compatible; matching an ID alone cannot justify incompatible comparisons.

## Future completion checklist

**Finding:** Repairs needed to prevent the observed patterns from recurring during Chapters 17-57.

**Files changed:** `CHAPTER_COMPLETION_CHECKLIST.md`.

**What changed:** Added nine checks for independent bounded implementation, first attempt before reference code, prerequisite training mathematics, correlated sample lineage, actual intermediate lossy stages, evidence-bound qrels, headline workload identities, invalid cross-workload improvement claims, and cumulative Part-ending recall/architecture/project checkpoints. Existing curriculum structure and contracts remain.

**Independent verification:** Each requested check is present under the existing evidence/practice categories. Its registry link resolves in book preflight. No syllabus, knowledge-map, project roadmap, teaching philosophy, reference architecture, glossary or reference-register rewrite was made.

**PASS / PARTIAL / FAIL:** **PASS**.

**Remaining concern:** Checklist enforcement is an authoring/review responsibility; the addition is not represented as automatic validation of pedagogical quality.

## Executed tests and reproducibility evidence

All existing test suites were run along with focused additions. Final aggregate: **132 passed, 0 failed**, comprising the prior 105 tests plus 27 added tests. Some historical-hash assertions now validate sealed historical records rather than falsely require old executions to have used current code/qrel metadata; their ranking/failure/version assertions remain. Fresh replay comparisons independently cover current execution behavior.

| Suite | Command suffix after `python -X utf8 -m unittest discover` | Passed |
|---|---|---:|
| V0 | `-s projects/V0 -p 'test_*.py'` | 17 |
| V1 | `-s projects/V1 -p 'test_*.py'` | 17 |
| V2 | `-s projects/V2 -p 'test_*.py'` | 24 |
| V3 | `-s projects/V3 -p 'test_*.py'` | 26 |
| V4 | `-s projects/V4 -p 'test_*.py'` | 12 |
| Common remediation contracts | `-s projects/common -p 'test_*.py'` | 17 |
| Book builder | `-s tools/book -p 'test_*.py'` | 19 |

Representative replay commands, from the repository root, with `<scratch>` replaced by a directory outside canonical sources:

```powershell
python -X utf8 projects/V3/training_bridge.py
python -X utf8 projects/V3/experiment_ch10.py --trials 1 --output <scratch>/ch10.json
python -X utf8 projects/V3/experiment_ch11.py --trials 1 --output <scratch>/ch11.json
python -X utf8 projects/V3/experiment_ch12.py --trials 1 --output <scratch>/ch12.json
python -X utf8 projects/V3/experiment_ch13.py --trials 1 --index-dir <scratch>/index_ch13 --output <scratch>/ch13.json
python -X utf8 projects/V3/experiment_ch14.py --output <scratch>/ch14.json
python -X utf8 projects/V4/experiment_ch15.py --output <scratch>/ch15.json
python -X utf8 projects/V4/experiment_ch16.py --output <scratch>/ch16.json
python -X utf8 projects/V2/tune_bm25_ch09.py --output <scratch>/tuning.json
python -X utf8 tools/book/build_book.py --check
```

The one-trial 10-13 replays verify deterministic IDs/metrics and envelope wiring, not a credible new latency distribution. Chapters 14/15/16 retain their configured repeated diagnostic timings. Their original benchmark samples remain historical results. No new production latency or universal quality claim was inferred.

### Preserved baseline gates

| Preserved asset/result | Independent check |
|---|---|
| Original audit, corpus, dense snapshot and curricula | Pre-edit byte-hash comparisons; no Chapter 17 or commit |
| Twelve preexisting experiment JSON files | Byte/LF-normalized sealed checks; fresh records written separately |
| All four old judgment definitions | Every preexisting JSON field compared semantically with Git HEAD; only binding/family metadata added |
| Overlap beating BM25 on original Chapter 09 workload | Original record unchanged; existing metric/parity tests pass |
| BM25/WAND exactness | Existing exhaustive-parity/tie/filter tests pass |
| Chapter 11 embedding slices | Fresh paraphrase .8125 lexical versus 1.0 dense; identifier .666667 both; original cases/metrics agree |
| Failed Chapter 12 improvement | Epoch 1, exact adapter digest, later validation collapse, frozen/adapted .888889 test recall retained |
| Exact dense oracle/materialization | All 34 ordered comparisons match, max score difference zero; corruption/version tests pass |
| ANN geometric versus judged relevance | Original V0 candidate IDs and synthetic outcomes match; stress dense judged recall .791667 retained |
| PQ/IVF negative results | Full-probe Flat exact parity; large synthetic ADC .125/refinement .375 neighbor recall retained; original quality summaries/IDs agree |
| Authorization | Existing scope gates plus new trace/context tests pass; ordinary records omit D10 |

### Targeted publishing verification

A reader PDF was rebuilt in a refreshed temporary copy using the repository builder. No canonical `dist` release was replaced. Preflight found **16 chapters, 28 numbered captions, zero errors and zero warnings**. The 254-page reader build completed with zero errors and eight nonblocking warnings; all 21 text-extraction sample checks passed. SVGs were rendered independently in Chromium; target PDF pages were rendered with PyMuPDF because Poppler is absent. The worked matrix/update, clarified Figure 12.02 and Figure 16.01 were visually inspected at the intended reader layout. In the final temporary build, their physical PDF pages are 148-149, 152 and 195 respectively (front matter has ten pages).

The reader retains nonblocking near-empty-page and preexisting long-code wrapping warnings. Bibliography deduplication and broader publishing/layout cleanup remain the original audit's P2 work, deliberately not repaired here. This verification does not claim a full publishing audit or a publication-ready final release.

## Changed-file inventory

The inventory below excludes the preexisting unchanged independent audit and temporary build/test outputs. It includes the new verification report itself. Paths are relative to the repository root.

**112 files: 66 modified, 46 created.**

| File | Change |
|---|---|
| [CHAPTER_COMPLETION_CHECKLIST.md](../CHAPTER_COMPLETION_CHECKLIST.md) | Modified |
| [README.md](../README.md) | Modified |
| [audits/QUARTER_BOOK_REMEDIATION_VERIFY_CH01_16.md](../audits/QUARTER_BOOK_REMEDIATION_VERIFY_CH01_16.md) | Created |
| [chapters/chapter-03-data-algorithms-and-measurements-needed-for-search.md](../chapters/chapter-03-data-algorithms-and-measurements-needed-for-search.md) | Modified |
| [chapters/chapter-04-what-an-llm-does-with-supplied-context.md](../chapters/chapter-04-what-an-llm-does-with-supplied-context.md) | Modified |
| [chapters/chapter-05-text-normalization-and-inverted-indexes.md](../chapters/chapter-05-text-normalization-and-inverted-indexes.md) | Modified |
| [chapters/chapter-06-tf-idf-vector-space-ranking-and-lexical-limits.md](../chapters/chapter-06-tf-idf-vector-space-ranking-and-lexical-limits.md) | Modified |
| [chapters/chapter-07-bm25-and-other-lexical-ranking-models.md](../chapters/chapter-07-bm25-and-other-lexical-ranking-models.md) | Modified |
| [chapters/chapter-08-production-lexical-query-execution.md](../chapters/chapter-08-production-lexical-query-execution.md) | Modified |
| [chapters/chapter-09-relevance-judgments-and-ranking-metrics.md](../chapters/chapter-09-relevance-judgments-and-ranking-metrics.md) | Modified |
| [chapters/chapter-10-vectors-distance-and-exact-similarity.md](../chapters/chapter-10-vectors-distance-and-exact-similarity.md) | Modified |
| [chapters/chapter-11-how-embedding-models-learn-retrieval-spaces.md](../chapters/chapter-11-how-embedding-models-learn-retrieval-spaces.md) | Modified |
| [chapters/chapter-12-retriever-training-and-domain-adaptation.md](../chapters/chapter-12-retriever-training-and-domain-adaptation.md) | Modified |
| [chapters/chapter-13-dense-candidate-retrieval-in-practice.md](../chapters/chapter-13-dense-candidate-retrieval-in-practice.md) | Modified |
| [chapters/chapter-14-sparse-neural-search-and-late-interaction.md](../chapters/chapter-14-sparse-neural-search-and-late-interaction.md) | Modified |
| [chapters/chapter-15-exact-knn-to-trees-and-hashing.md](../chapters/chapter-15-exact-knn-to-trees-and-hashing.md) | Modified |
| [chapters/chapter-16-ivf-quantization-and-compressed-vectors.md](../chapters/chapter-16-ivf-quantization-and-compressed-vectors.md) | Modified |
| [evaluation/EVIDENCE_IDENTITY.md](../evaluation/EVIDENCE_IDENTITY.md) | Created |
| [evaluation/WORKLOAD_REGISTRY.json](../evaluation/WORKLOAD_REGISTRY.json) | Created |
| [evaluation/WORKLOAD_REGISTRY.md](../evaluation/WORKLOAD_REGISTRY.md) | Created |
| [labs/chapter-04/LAB.md](../labs/chapter-04/LAB.md) | Modified |
| [labs/chapter-05/LAB.md](../labs/chapter-05/LAB.md) | Modified |
| [labs/chapter-05/check_implementation.py](../labs/chapter-05/check_implementation.py) | Created |
| [labs/chapter-05/implement.py](../labs/chapter-05/implement.py) | Created |
| [labs/chapter-06/LAB.md](../labs/chapter-06/LAB.md) | Modified |
| [labs/chapter-06/check_implementation.py](../labs/chapter-06/check_implementation.py) | Created |
| [labs/chapter-06/implement.py](../labs/chapter-06/implement.py) | Created |
| [labs/chapter-07/LAB.md](../labs/chapter-07/LAB.md) | Modified |
| [labs/chapter-07/check_implementation.py](../labs/chapter-07/check_implementation.py) | Created |
| [labs/chapter-07/implement.py](../labs/chapter-07/implement.py) | Created |
| [labs/chapter-08/LAB.md](../labs/chapter-08/LAB.md) | Modified |
| [labs/chapter-08/check_implementation.py](../labs/chapter-08/check_implementation.py) | Created |
| [labs/chapter-08/implement.py](../labs/chapter-08/implement.py) | Created |
| [labs/chapter-09/LAB.md](../labs/chapter-09/LAB.md) | Modified |
| [labs/chapter-12/LAB.md](../labs/chapter-12/LAB.md) | Modified |
| [labs/chapter-14/LAB.md](../labs/chapter-14/LAB.md) | Modified |
| [labs/chapter-14/check_implementation.py](../labs/chapter-14/check_implementation.py) | Created |
| [labs/chapter-14/implement.py](../labs/chapter-14/implement.py) | Created |
| [labs/chapter-15/LAB.md](../labs/chapter-15/LAB.md) | Modified |
| [labs/chapter-15/check_implementation.py](../labs/chapter-15/check_implementation.py) | Created |
| [labs/chapter-15/implement.py](../labs/chapter-15/implement.py) | Created |
| [labs/chapter-16/LAB.md](../labs/chapter-16/LAB.md) | Modified |
| [labs/chapter-16/check_implementation.py](../labs/chapter-16/check_implementation.py) | Created |
| [labs/chapter-16/implement.py](../labs/chapter-16/implement.py) | Created |
| [observability/SAMPLE_ENVELOPE.md](../observability/SAMPLE_ENVELOPE.md) | Created |
| [projects/V1/lexical_index.py](../projects/V1/lexical_index.py) | Modified |
| [projects/V2/README.md](../projects/V2/README.md) | Modified |
| [projects/V2/chapter-09-tuning-experiment.json](../projects/V2/chapter-09-tuning-experiment.json) | Created |
| [projects/V2/eval_ch09.py](../projects/V2/eval_ch09.py) | Modified |
| [projects/V2/judgments_bm25_tuning.json](../projects/V2/judgments_bm25_tuning.json) | Created |
| [projects/V2/judgments_ch09.json](../projects/V2/judgments_ch09.json) | Modified |
| [projects/V2/test_bm25_tuning.py](../projects/V2/test_bm25_tuning.py) | Created |
| [projects/V2/tune_bm25_ch09.py](../projects/V2/tune_bm25_ch09.py) | Created |
| [projects/V3/README.md](../projects/V3/README.md) | Modified |
| [projects/V3/experiment_ch10.py](../projects/V3/experiment_ch10.py) | Modified |
| [projects/V3/experiment_ch11.py](../projects/V3/experiment_ch11.py) | Modified |
| [projects/V3/experiment_ch12.py](../projects/V3/experiment_ch12.py) | Modified |
| [projects/V3/experiment_ch13.py](../projects/V3/experiment_ch13.py) | Modified |
| [projects/V3/experiment_ch14.py](../projects/V3/experiment_ch14.py) | Modified |
| [projects/V3/judgments_ch11.json](../projects/V3/judgments_ch11.json) | Modified |
| [projects/V3/judgments_ch12.json](../projects/V3/judgments_ch12.json) | Modified |
| [projects/V3/judgments_ch13.json](../projects/V3/judgments_ch13.json) | Modified |
| [projects/V3/test_ch11.py](../projects/V3/test_ch11.py) | Modified |
| [projects/V3/test_ch12.py](../projects/V3/test_ch12.py) | Modified |
| [projects/V3/test_ch13.py](../projects/V3/test_ch13.py) | Modified |
| [projects/V3/test_ch14.py](../projects/V3/test_ch14.py) | Modified |
| [projects/V3/test_trace_pipeline.py](../projects/V3/test_trace_pipeline.py) | Created |
| [projects/V3/test_training_bridge.py](../projects/V3/test_training_bridge.py) | Created |
| [projects/V3/training_bridge.py](../projects/V3/training_bridge.py) | Created |
| [projects/V4/README.md](../projects/V4/README.md) | Modified |
| [projects/V4/ann_ch15.py](../projects/V4/ann_ch15.py) | Modified |
| [projects/V4/experiment_ch15.py](../projects/V4/experiment_ch15.py) | Modified |
| [projects/V4/experiment_ch16.py](../projects/V4/experiment_ch16.py) | Modified |
| [projects/V4/ivf_pq_ch16.py](../projects/V4/ivf_pq_ch16.py) | Modified |
| [projects/V4/test_ch15.py](../projects/V4/test_ch15.py) | Modified |
| [projects/V4/test_ch16.py](../projects/V4/test_ch16.py) | Modified |
| [projects/V4/test_trace_shortlists.py](../projects/V4/test_trace_shortlists.py) | Created |
| [projects/common/HISTORICAL_RESULTS.json](../projects/common/HISTORICAL_RESULTS.json) | Created |
| [projects/common/experiment_trace.py](../projects/common/experiment_trace.py) | Created |
| [projects/common/historical_results.py](../projects/common/historical_results.py) | Created |
| [projects/common/learner_checks.py](../projects/common/learner_checks.py) | Created |
| [projects/common/qrel_identity.py](../projects/common/qrel_identity.py) | Created |
| [projects/common/split_semantics.py](../projects/common/split_semantics.py) | Created |
| [projects/common/test_experiment_trace.py](../projects/common/test_experiment_trace.py) | Created |
| [projects/common/test_learner_mechanisms.py](../projects/common/test_learner_mechanisms.py) | Created |
| [projects/common/test_qrel_identity.py](../projects/common/test_qrel_identity.py) | Created |
| [projects/common/test_remediation_visuals.py](../projects/common/test_remediation_visuals.py) | Created |
| [projects/common/test_split_semantics.py](../projects/common/test_split_semantics.py) | Created |
| [projects/common/test_workload_registry.py](../projects/common/test_workload_registry.py) | Created |
| [solutions/chapter-04-solutions.md](../solutions/chapter-04-solutions.md) | Modified |
| [solutions/chapter-05-solutions.md](../solutions/chapter-05-solutions.md) | Modified |
| [solutions/chapter-06-solutions.md](../solutions/chapter-06-solutions.md) | Modified |
| [solutions/chapter-07-solutions.md](../solutions/chapter-07-solutions.md) | Modified |
| [solutions/chapter-08-solutions.md](../solutions/chapter-08-solutions.md) | Modified |
| [solutions/chapter-09-solutions.md](../solutions/chapter-09-solutions.md) | Modified |
| [solutions/chapter-12-solutions.md](../solutions/chapter-12-solutions.md) | Modified |
| [solutions/chapter-14-solutions.md](../solutions/chapter-14-solutions.md) | Modified |
| [solutions/chapter-15-solutions.md](../solutions/chapter-15-solutions.md) | Modified |
| [solutions/chapter-16-solutions.md](../solutions/chapter-16-solutions.md) | Modified |
| [solutions/code/chapter_05_mechanisms.py](../solutions/code/chapter_05_mechanisms.py) | Created |
| [solutions/code/chapter_06_mechanisms.py](../solutions/code/chapter_06_mechanisms.py) | Created |
| [solutions/code/chapter_07_mechanisms.py](../solutions/code/chapter_07_mechanisms.py) | Created |
| [solutions/code/chapter_08_mechanisms.py](../solutions/code/chapter_08_mechanisms.py) | Created |
| [solutions/code/chapter_14_mechanisms.py](../solutions/code/chapter_14_mechanisms.py) | Created |
| [solutions/code/chapter_15_mechanisms.py](../solutions/code/chapter_15_mechanisms.py) | Created |
| [solutions/code/chapter_16_mechanisms.py](../solutions/code/chapter_16_mechanisms.py) | Created |
| [visuals/chapter-12/figure-12-02-document-split.png](../visuals/chapter-12/figure-12-02-document-split.png) | Modified |
| [visuals/chapter-12/figure-12-02-document-split.svg](../visuals/chapter-12/figure-12-02-document-split.svg) | Modified |
| [visuals/chapter-12/plot-12-02-document-split.py](../visuals/chapter-12/plot-12-02-document-split.py) | Modified |
| [visuals/chapter-16/figure-16-01-cells-and-codes.png](../visuals/chapter-16/figure-16-01-cells-and-codes.png) | Modified |
| [visuals/chapter-16/figure-16-01-cells-and-codes.svg](../visuals/chapter-16/figure-16-01-cells-and-codes.svg) | Modified |
| [visuals/chapter-16/plot-16-01-cells-and-codes.py](../visuals/chapter-16/plot-16-01-cells-and-codes.py) | Modified |

## Chapter 17 readiness

All seven authorized P1 debts now have concrete teaching/code/contracts and executed verification. Continuing authoring will not compound the identified implementation, mathematics, lineage, qrel, split, tuning or cumulative-retention gaps. The original negative results and baselines remain available. Nonblocking publishing and other unrequested P2 work remains for the later publication pass; learner retention still requires actual learner assessment.

READY FOR CHAPTER 17 WITH NON-BLOCKING RESIDUALS
