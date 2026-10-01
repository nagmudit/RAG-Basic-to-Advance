# Quarter-book audit — Chapters 1–16

**Independent review date:** 2026-10-01  
**Audited commit:** `6202e5ec067119991722c99c3a2a15c42266c902`  
**Disposition:** **YES — proceed after targeted fixes**  
**Remediation inventory:** **0 P0, 7 P1, 8 P2 findings**. IDs in the remediation plan identify distinct findings; appearances elsewhere are not additional findings.

## Executive summary

The first sixteen chapters provide a technically credible foundation for the intended book. This conclusion rests on executed code, independently checked calculations and algorithms, inspected rendered figures, a rebuilt reader PDF, and comparison with the repository's own contracts. It does not rest on the authoring reviews' declarations of completion.

The strongest pattern is mechanism → observable failure → measured decision. V0 exposes segmentation, ranking and evidence-budget failures. V1 separates postings from scoring. V2 supplies a functioning BM25 baseline, exact WAND pruning and reviewed relevance judgments. V3 deliberately distinguishes lexical coordinates from learned embeddings, rejects an adapter that fails to improve held-out results, and persists a versioned exact dense oracle. V4 preserves that oracle while separating geometric ANN recall from judged evidence recall and coarse-list loss from quantization loss. These are substantial textbook strengths.

The principal weakness is the difference between **a working reference implementation** and **a learner who can implement its mechanism**. The syllabus explicitly requires implementation in the Chapter 05, 06, 08, 15 and 16 labs, but the authored labs chiefly ask learners to calculate, trace, execute and diagnose the supplied implementations. Chapter 07 independently implements a term factor, but not a complete scorer; Chapter 14's numerical lab meets its syllabus while its stronger implement-MaxSim mastery gate is untested. These tasks require thought; they are not empty labs. Nevertheless, they do not establish all the construction capabilities claimed. Mathematics has a related discontinuity: scalar vectors, small softmax and loss arithmetic are worked, but matrix shapes and the gradient update behind Chapter 12 receive less decomposition.

The main engineering continuity problem is telemetry. Early engine facades produce a coherent redacted request record. Later experiment runners preserve valuable IDs, scores, work and aggregate timings but do not consistently preserve request correlation, per-execution timing/status and intermediate candidate stages. Chapter 15's V0 cases include request IDs; Chapter 16's corresponding cases drop them. Chapter 16 also recommends logging the approximate top-R shortlist but does not save that shortlist's IDs/scores before exact refinement.

Other consequential gaps are an unfinished BM25 tuning exercise, missing explicit cumulative checkpoints for completed Parts I and III, document-ID rather than source-family enforcement in the adaptation split, and qrel loaders that do not bind judgments to source content. The latter is a demonstrated future-change hazard, **not evidence that the current checked results are invalid**.

Independent execution found **105 passing repository tests**, all **16 selected executable entry points** running successfully, and **1,140 additional seeded algorithm/security probes** with no parity or eligibility failures. Checked deterministic results agreed in the fields compared; CPU timings changed, as the manuscript says they may. The reader build succeeded at **241 pages**, with working destination checks, embedded fonts and no build errors. Publication defects include several near-empty pages, two duplicated bibliography works, one clipped figure label, and a stale existing reader PDF.

**Answer to the longitudinal question:** continuing the technical mechanisms and experimental caution at their present quality could produce the intended book. Continuing the present lab, prerequisite and telemetry patterns unchanged would produce a strong explanatory survey with runnable demonstrations, but would not reliably deliver the promised self-contained implementation, debugging and production mastery. Address the seven P1 findings within the next five chapters, giving the mathematics, implementation and trace continuity fixes priority as Chapter 17 is prepared. There is no observed structural blocker requiring the book to be restarted.

The repository plans **57** chapters. Sixteen authored chapters are **28.1%**, leaving **41**, rather than 42, remaining chapters. “Quarter-book” remains a reasonable name for this review.

## Audit scope and method

### Specification used

The following were treated as the book's specification, not optional promotional material:

| Contract / architectural source | Requirement used in this audit |
|---|---|
| `README.md`, `SYLLABUS.md` | Twelve parts, 28 modules, 57 chapters; objectives, prerequisites, minimum micro-concept depth, labs, visuals, misconceptions and unlocks. |
| `TEACHING_PHILOSOPHY.md`, `KNOWLEDGE_MAP.md`, `ROADMAP.md` | Motivation before abstraction, first-principles mechanisms, failure-driven progression, active recall and capability gates. |
| `PROJECT_ROADMAP.md`, `REFERENCE_ARCHITECTURE.md` | One evolving “Build Your Own RAG Engine,” retained baselines and telemetry, explicit evidence and authorization paths. |
| `CHAPTER_COMPLETION_CHECKLIST.md` | Chapter authoring/completion contract: mechanism depth, code, worked examples, exercises, solutions, experiments, visuals, references and continuity. No separate chapter-authoring contract file was found. |
| `visuals/VISUAL_ASSET_CONTRACT.md` | Numbered instructional figures, captions, editable source, rendered alternatives, legibility and reproducible plots. |
| `evaluation/EVALUATION_EXPERIMENT_CONTRACT.md` | Questions, hypotheses, baselines, controlled variables, versioned workloads, judgments, metrics, raw results, uncertainty, failure analysis and scoped conclusions. |
| `observability/OBSERVABILITY_CONTRACT.md` | Progressive request and ingest observability; logs, metrics, traces, evaluation and events are distinct; redaction and authorization apply throughout. |
| `GLOSSARY.md`, `REFERENCES.md`, `PAPER_READING_PATH.md`, `FRONTIER_RESEARCH.md`, `CASE_STUDIES.md` | Stable terminology, source provenance, research literacy, distinction between established mechanisms and frontier results, and planned cumulative case studies. |
| `book/book.toml`, `tools/book/README.md`, build implementation/tests | Edition profiles, inclusion rules, layout, links, figures, bibliography, PDF extraction checks and publication provenance. |

`PROJECT_ROADMAP.md` is present; no separate `PROJECT_ROADMAP` substitute was invented. The authoring checklist itself supplies the requested chapter contract. There are no top-level `datasets/` or `experiments/` directories in this state; actual datasets and result records live under `projects/`.

### Inspection and execution

All sixteen chapter manuscripts, labs, solution files and chapter review files were inspected, together with their project briefs, core implementations, data, checked results and visual assets. The review files were used as claims to verify, not as proof. Core algorithm implementations received source inspection and execution; existing behavioral tests were run. This is an empirical/source audit, not a formal proof or exhaustive test of every possible numeric input.

An initial inventory and SHA256 baseline covered all **242 tracked files**. The working tree was clean. A byte-copy of those tracked files was made outside the repository:

`C:/Users/mudit/AppData/Local/Temp/rag-quarter-audit-20261001-dtdwd_dn/repo`

Tests, experiment replays, plot regeneration and the reader build ran there. This avoids overwriting canonical experiment records, figures or distribution files. Scratch logs and probe results are under the parent temporary directory; substantive outcomes are recorded here so that the report remains useful without those temporary files. No dependency installation or model download was needed. The pinned encoder was already cached, and offline loading succeeded.

Representative reproduction commands, run in a disposable copy:

```powershell
python -B -X utf8 -m unittest discover -s projects/V0 -v
python -B -X utf8 -m unittest discover -s projects/V1 -v
python -B -X utf8 -m unittest discover -s projects/V2 -v
python -B -X utf8 -m unittest discover -s projects/V3 -v
python -B -X utf8 -m unittest discover -s projects/V4 -v
python -B -X utf8 -m unittest discover -s tools/book -v
python -B -X utf8 tools/book/build_book.py --profile reader
```

Suites were discovered separately: combining all project directories under one discovery root risks collisions between similarly named local modules. Experiments were run separately, with local output paths where supported. Original scripts with canonical defaults were safe because execution was confined to the copy.

**Environment observed:** Windows, Python 3.14.2, sentence-transformers 5.2.2, transformers 4.57.3, PyTorch 2.10.0 on CPU. NumPy, matplotlib, Pillow, PyMuPDF, markdown-it and Playwright/Chromium were available. Mermaid CLI was available. Poppler was absent; PDF pages were rendered with PyMuPDF for inspection. No claim is made that these local latency numbers represent another machine or a service workload.

Six contact sheets covered all **23 rendered figures**. Individual PDF pages were additionally inspected at readable resolution, including landscape diagrams, training figures, IVF/PQ plots, equations, tables, code, labs and references. All sixteen matplotlib plot programs were run; regenerated PNG hashes matched their checked counterparts. Mermaid renderings and SVG references were inspected and exercised by the book pipeline; a separate bit-identical regeneration of every checked Mermaid SVG was not performed.

Representative external citations were checked against original papers, canonical IR material and official implementation/model documentation. The reference-health table identifies the extent of verification. Network fetch failures are reported as unverified fetches, not automatically as broken or false citations.

### Interpretation rules

Coverage levels used below:

- **Mentioned:** named or situated without a mechanism.
- **Explained:** mechanism, assumptions and failure boundary taught in prose/math.
- **Demonstrated:** reproducible worked example or traced result.
- **Implemented:** working reference code supplied and independently exercised.
- **Practised:** learner must calculate, diagnose, design or implement it.
- **Mastery supported:** the required learner artifact tests the actual claimed capability. Supplying reference code alone does not establish this level.

“Partial” is not always a defect. The syllabus intentionally defers HNSW to Chapter 17, ingestion/chunking to 19–20, live metadata/ACL systems to 21, durable updates to 22, fusion to 25, generation/context machinery to 28–29, and full RAG evaluation to 30–33. Their absence in Chapters 1–16 is appropriate. A null generation result on new retrieval questions is honest, not an unfinished LLM integration.

Severity is separate from scheduling. **P0** means continuing would compound a genuine blocking problem. **P1** means consequential teaching/engineering debt to correct within the next five chapters. **P2** means non-blocking publication or reproducibility improvement. None of the observed cosmetic defects determines the proceed verdict.

## Repository state audited

| Item | Observed state |
|---|---|
| Git commit | `6202e5ec067119991722c99c3a2a15c42266c902`, “Author Chapter 16 IVF and PQ.” |
| Source tree | Initially clean; 242 tracked files. |
| Authored chapters | 01–16; Parts I, II and III complete; Part IV contains Chapters 15–16 of planned 15–18. |
| Associated teaching material | 16 labs, 16 solution files, 16 authoring reviews; Chapter 01 also has `labs/chapter-01/source_trace.py`. |
| Running project | V0–V4; 42 project Python files, 25 project JSON files and a checked float32 dense snapshot. |
| Visuals | 23 substantive figures with SVG and PNG assets; seven Mermaid sources and sixteen plot programs. |
| Current reader rebuilt by audit | 241 pages; 343 outline entries; 2,085 link annotations; 26 embedded fonts. |
| Existing local reader distribution | `dist/rag-book-reader.pdf` is an older 198-page, 13-chapter build, dated 2026-09-30, with different commit/dirty-state metadata. It is not the PDF used to judge the current manuscript. |
| Changes made by audit | This Markdown report only. All generated execution/build outputs remained outside canonical source paths. |

The copy has no `.git` directory, so its build provenance reports an unknown commit. That is a consequence of isolation, not a source-builder defect. The source commit being audited is recorded above.

## Book-level scorecard

Scale: 5 = publication/expert-teaching quality; 4 = strong with targeted improvements; 3 = adequate with meaningful revision; 2 = substantial weakness; 1 = structural failure. Scores concern the present quarter's intended scope, not unimplemented future chapters.

| Dimension | Score | Evidence / reason |
|---|---:|---|
| Technical accuracy | 4 | BM25, WAND, metric arithmetic, MaxSim and IVF/PQ survived source/calculation/probe checks. Chapter 12's 49 KiB estimate should be 48 KiB; Chapter 14's unqualified “log1p saturates” obscures its unboundedness. |
| Syllabus coverage | 4 | Core mechanisms are present and runnable. BM25 tuning is deferred but never completed; five implementation labs do not require the promised implementation. |
| Prerequisite discipline | 3 | Exact KNN precedes ANN and qrels precede ranking measures. Matrix notation remains intuitive in 04; actual gradient adaptation in 12 assumes missing update/shape steps. |
| Conceptual depth | 3 | Excellent BM25 factor decomposition and ANN error separation; weaker loss-to-update decomposition and learner construction of indexing/pruning mechanisms. |
| Pedagogy | 4 | Concrete Helios failures motivate progression; missing Part I/III cumulative checkpoints and mathematics bridges prevent a full 5. |
| Examples | 5 | Reused source clauses, rank reversals, negative results and hand-calculable geometry illuminate mechanisms and explicitly delimit generalization. |
| Mathematics | 3 | Worked softmax/loss arithmetic and most edge policies are correct; matrix dimensions and an actual parameter-update step are not taught with the care given to scalar ranking arithmetic. |
| Code | 4 | 86 project tests pass, readable mechanisms and 1,140 independent probes agree. Environment pinning and a common later-stage request wrapper remain incomplete. |
| Labs | 3 | Strong calculation/debug/design tasks; reference execution substitutes for required implementation in 05/06/08/15/16. |
| Solutions | 4 | Reasoned diagnoses and alternatives, rather than answer keys alone. Missing independent implementation tasks also mean corresponding implementation reasoning is not assessed. |
| Experimentation | 4 | Controlled comparisons, raw results and negative decisions are unusually strong. Source-family splitting and content-bound qrels need strengthening. |
| Evaluation | 4 | Complete small judgment rosters, binary/graded distinctions and zero-positive policies. Deferred tuning and mutable-content binding remain gaps. |
| Observability progression | 3 | Redacted V0–V2 request records are strong; later per-query records/timing arrays are not consistently one correlated execution trace. |
| Visuals | 4 | All 23 teach mechanisms; 16.01 has a clipped query label, 13.01 has a flow/convention ambiguity, and wide-diagram print labels approach the minimum size. |
| Citations | 4 | Representative primary-source claims checked correctly. PDF duplicates ColBERT/SPLADE v2 works; not every factual claim has a precise evidence hook. |
| Terminology consistency | 4 | Candidate/evidence, relevance/similarity and correctness/faithfulness stay distinct. Corpus eligibility and duplicate training glossary entries need cleanup. |
| Project continuity | 4 | V0 corpus and lexical/exact baselines persist; dense snapshot parity is checked. Telemetry preservation and comparison-workload identity need a clearer shared contract. |
| Production relevance | 4 | Access, versioning, payload limits and refusal to deploy toy wins are taught early. Production failure records are described more fully than implemented in later runners. |
| Research discipline | 4 | Trained-model claims, manual operators and frontier hypotheses are distinguished. Family-level independence and bibliographic identity need targeted fixes. |
| Overall coherence | 4 | One accumulated evidence-search story is visible. Practice, mathematics and observability gaps could become recurring debt if copied forward. |

## Syllabus coverage matrix

Entries summarize inspected material rather than restating the syllabus. “Reference only” means implemented in the repository but not independently constructed by the learner.

| Chapter | Syllabus objective | Required topics | Fully covered | Partially covered | Missing | Unexpected additions | Lab aligned? | Project aligned? | Visual aligned? | Mastery gate supported? |
|---|---|---|---|---|---|---|---|---|---|---|
| 01 | Decide when retrieval is needed; trace evidence | Knowledge boundaries, alternatives, grounding, provenance, abstention | Manual dated-source comparison; task routing; evidence/citation distinction | Fine-tuning and tool alternatives appropriately introductory | No material objective omission | Authorization and incident-vs-contract evidence distinctions | Yes: 15 justified routes | Yes: V0 contract | Yes: two evidence paths | Yes, at conceptual/manual level |
| 02 | Implement the first loop; fail each boundary | IDs, segmentation, overlap, top-k, prompt, budget, structured log | Independent loop, deterministic ties, two-task stub, boundary failures, safe trace | Optional real model deliberately not used | No core omission | Detailed scope isolation and exact quoted-clause guard | Yes: actual independent build | Yes: executable V0 | Yes: preparation/query separation | Yes within stated stub limits |
| 03 | Acquire minimum computing/math vocabulary | Structures, Big-O, units, logs/probability/vectors, percentiles, controls/leakage | Exact-ID benchmark, complexity distinction, scalar calculations and split principles | Matrix algebra/natural exp needed later are not bridged | No worked matrix/exp bridge for later use | Amortization and miss-mixture comparison | Yes; unsafe canonical output default is workflow debt | Yes: V0 characterization | Yes: same-task growth curves | Mostly; later math readiness overstated |
| 04 | Explain relevant context's insufficiency | Token prediction, attention, position, conflict, instructions, adaptation choices | Prompt fixtures, small softmax, token budget, claim support/faithfulness distinction | Matrix formula explicitly intuitive; position experiment has no model outputs by design | No core stated-gate omission; formal shape walkthrough would help | Detailed prompt-injection fixture | Yes as prompt/claim diagnosis; not an empirical LLM study | Yes: V0 context probes | Yes: autoregression and claim checks | Yes for stated small-softmax/conceptual gate |
| 05 | Build an inverted index | Analyzer, postings/positions, Boolean/phrase, forward index, costs | Runnable positional index, phrase failures, Unicode/code trade-offs, scope filtering | Stem/lemma/fuzzy/ngram options explained, not implemented | Required learner implementation of postings/phrase | Analyzer failure and safe Boolean NOT | Partial: hand work + reference execution | Yes: V1 retains V0 | Yes: postings + scoped intersection | Explain/trace yes; implement not established |
| 06 | Derive factors and rank with TF-IDF | TF/DF/IDF, variants, sparse vectors, cosine, field effects, rank reversal | Full worked rank reversal, weighting policies, missing/zero distinctions | Learner construction of scorer | Required independent TF-IDF implementation | Explicit matched-zero-cosine policy | Partial: calculations/variants strong | Yes: V1 scorer shares index | Yes: sparse weighted matrix | Calculation yes; implementation not established |
| 07 | Calculate and tune BM25 | IDF/odds, saturation, length, k1/b, variants, fitting, lexical failures | Worked BM25, curves, limits, runnable scorer and parameter controls | Independent coding covers term factor; fitting deferred to 09; alternatives conceptual | Completed judged tuning/selection and learner complete scorer | Nonnegative-IDF and field-boost distinctions | Mostly: implements saturation/calculates; full scorer/tuning incomplete | Yes: V2 baseline | Yes: controls and asymptotes | Calculate/debug yes; tune/full construction not established |
| 08 | Return exact top-k with safe pruning | Codec, execution plans, bounds, heap, WAND/BMW, impacts, exact vs approximate | Executable exact WAND, cursor trace, codec, work/latency comparison | BMW/MaxScore/segments explained, appropriately not all implemented | Required learner-built toy pruner | Floating-point/tie-safe conservative bounds | Partial: predicts/traces/debugs reference | Yes: V2 score parity | Yes: global trace + labeled conceptual blocks | Trace/defend yes; implement not established |
| 09 | Measure evidence relevance and ordering | Qrels, assessment, incomplete labels, P/R/MRR/MAP/NDCG, latency | Complete reviewed roster, worked metrics, harness, Part II quiz | Multiple assessors hypothetical, not fabricated as real | Earlier promised BM25 tuning still absent | Strong zero-positive/unjudged policies | Yes: independent metric functions | Yes: judged V2 | Yes: ranked gain | Yes for ranking evaluation; not tuning |
| 10 | Calculate metric-dependent neighbors | Norms, metrics, unit relation, exact scan/heap, batching/memory | Hand geometry, executable scoped exact oracle, deterministic ties | Anisotropy introductory, matrix notation terse | No required exact-search omission | Binary lexical vectors explicitly precede learned ones | Yes: independent top-k implementation | Yes: V3 oracle on same V0 | Yes: metric geometry | Yes, except broader matrix fluency |
| 11 | Explain encoder pipeline and learning signal | Pooling, towers/asymmetry, contrastive pairs, negatives, temperature, prefixes | Pinned real encoder, masked mean, worked softmax/loss, slice comparison, ID failures | Connecting stable implementation to the worked probability; multilingual/Matryoshka conceptual | No core loss-arithmetic omission; update belongs to 12 | Model-role and arbitrary-prefix guard | Yes: hand math + independent pooling/loss + model comparison | Yes: V3 frozen encoder | Yes: independent encoders/batch | Pipeline/calculation yes; update deliberately not yet taught |
| 12 | Adapt then test generalization | Signals/loss families, mining, masks, distillation, splits, shifts | Actual query adapter, validation selection, rejected test gain, failure history | Gradient/update mechanism; domain/language transfer conceptual | Source-family split enforcement; hand update | Negative adaptation result retained | Aligned experiment; implementation depth limited | Yes: base passage space frozen | Mostly: split/score visuals; update-motion example missing | Experiment defense yes; first-principles training partial |
| 13 | Materialize dense index and diagnose | Batch/version/vector IDs, paired encoders, exact scores, sliced quality, cold/warm costs | Manifest, float32 reload, corruption gates, parity, stress slices and timings | Runtime/environment portability; correlated request timing | No core index omission | Strong searchable-text digest validation | Yes: build/reload/corrupt/diagnose | Yes: V3 checked exact oracle | Mostly: flow convention ambiguity | Yes for local exact index |
| 14 | Place sparse/late interaction models | Vocabulary expansion, sparsity, token storage, MaxSim, retrieval/rerank roles | Manual operator code, MaxSim reversal, failure/context limits | Learned training/index optimization conceptual and labeled | Learner implementation required by chapter's stronger mastery gate | Clear separation from trained SPLADE/ColBERT benchmark | Yes for syllabus's numerical task; stronger gate partial | Yes: sandbox preserves frozen baseline | Yes: token score grid | Compute/role yes; independently implement not assessed |
| 15 | Explain early exact/approximate families | Exact costs, KD/ball bounds, backtracking, dimension, LSH probabilities | Correct exact KD, lossy LSH, probabilities, oracle/judged recall, negative timings | Formal space accounting and broader scale evidence | Required learner LSH implementation | Eligibility and representation-vs-ANN diagnosis | Partial: trace/measure rather than build LSH | Yes: V4 reuses dense snapshot | Yes: partitions/buckets + cost/quality | Explain/diagnose yes; implement not established |
| 16 | Trace assignment/probing/compression | Centroids, residual PQ, ADC, nlist/nprobe, bytes, refinement, updates | Runnable Lloyd/IVF/PQ, hand residual/ADC/storage, separated losses, tombstones | Hand training update; durable lifecycle intentionally later | Required learner toy coarse/PQ implementation | Sensitive-training-artifact warning and negative deployment gate | Partial: detailed hand work + supplied index calls | Yes, except trace-field regression | Yes, with clipped 38° query label | Trace/error/bytes yes; construction not established |

## Chapter-by-chapter audit

The A–P labels correspond to the requested review dimensions. Evidence paths refer to the audited source tree. A “not applicable” entry identifies an intentional scope boundary rather than excusing a missing present obligation.

### Chapter 01

**Evidence:** `chapters/chapter-01-a-question-a-model-and-missing-evidence.md`; `labs/chapter-01/LAB.md`; `solutions/chapter-01-solutions.md`; `labs/chapter-01/source_trace.py`; Figure 01.01.

- **A — Purpose:** Choose a knowledge-access route and trace an answer to eligible, dated source evidence. The learner should distinguish private/stale knowledge access from general language capability.
- **B — Coverage:** “A question is a message; an information need is a task,” “Where could an answer come from?” and the routing table explain the syllabus concepts rather than merely naming them. Fine-tuning and tools are comparisons, not promised implementations.
- **C — Technical correctness:** The amendment is signed May 12, effective May 15, and the question is as of May 20. Using the older four-hour clause alone is wrong for that date. The distinction between an incident observation and a contractual commitment is correct. No LLM accuracy experiment is falsely claimed.
- **D — Pedagogy:** A concrete missing amendment precedes abstraction. Candidate, evidence, answer and citation receive separate roles. The author does not begin by equating RAG with an embedding database.
- **E — Depth:** Sufficient for an orientation chapter: it decomposes source authority, time, scope and task rather than teaching a retrieval algorithm prematurely.
- **F — Worked examples:** “Work the Helios Pro question by hand” exposes the old/new clauses and authority decision. Four hours to one is a three-hour reduction and 75% reduction; arithmetic agrees. Unsupported follow-up facts remain unsupported.
- **G — Code:** `source_trace.py` validates source locators/scope in a manually chosen trace. It does not determine semantic support; the chapter's human-review boundary is essential and accurate. The script ran.
- **H — Lab:** Fifteen requests require choosing and justifying RAG or an alternative, plus evidence/permission reasoning. This is a substantive design/classification lab appropriate before implementation.
- **I — Solutions:** Explain why routes differ and allow justified alternatives. They preserve the decision task instead of treating one product architecture as the answer.
- **J — Visuals:** Figure 01.01 teaches model-only versus evidence-backed paths and claim checks. Rendered content is correct. Its tall PDF placement is preferable to shrinking it into a decorative thumbnail.
- **K — Experiments:** The manual evidence exercise states its comparison and limits. It is an evidence-access demonstration, not measured model improvement.
- **L — Evaluation:** Support is checked against clauses and dates. No retrieval metric or answer-performance claim requires premature qrels.
- **M — Observability:** “Your first audit trail” introduces traceable IDs, source versions and selected evidence before instrumentation becomes complex. Optional trace validation is a useful bridge.
- **N — Security:** Eligibility is a hard condition on using sources. Missing access does not become a negative relevance label or permission to answer from protected text.
- **O — Production connection:** Private sources, source authority, freshness, alternatives and abstention connect immediately to real task design without vendor instructions.
- **P — Mastery gate:** Supported by routing, hand evidence selection and explanations. No material blocking gap observed.

### Chapter 02

**Evidence:** `chapters/chapter-02-build-the-first-rag-loop.md`; `labs/chapter-02/LAB.md`; `solutions/chapter-02-solutions.md`; `projects/V0/engine.py`, `corpus.json`, `RESULTS.md`, `test_engine.py`; Figures 02.01–02.02.

- **A — Purpose:** Independently implement preparation, segmentation, overlap retrieval, top-k, context, a limited answer stub and a structured request record.
- **B — Coverage:** Index/query time, stable IDs/spans, deterministic ranking, budgeting and unsupported-answer behavior are implemented and practised. Optional LLM hookup is appropriately optional; the answer stub is explicitly two-task, not a simulated general model.
- **C — Technical correctness:** Ten documents become eleven structural sections, thirteen indexed segments and twenty-four segments under the smaller non-overlapping windows. The worked overlap decision gives D2 seven distinct matched terms versus D1 six. All eligible-scoring/context tests passed.
- **D — Pedagogy:** The Python primer and plain functions expose the mechanism. Failures are attached to stage boundaries. A learner can trace this chapter with Chapter 01 and its local primer.
- **E — Depth:** The crude mechanism has explicit assumptions: ASCII lexical tokens, distinct-term overlap, title/body choices, source-word budget and deterministic ID ties. It is not prematurely hidden behind a framework.
- **F — Worked examples:** Top-one loses the old clause needed for comparison; top-two can recover both. Other information needs need more context. Eight-word windows split required evidence; a five-word context budget drops it. Removing D2 leads to abstention. Success and failure are reproducible.
- **G — Code:** `Engine.run` keeps eligible candidates separate from selected context and verifies literal supported clauses in the stub. That narrow check teaches support boundaries but cannot validate arbitrary claims. Code and experiment execution succeeded.
- **H — Lab:** Requires an independent local engine and trace, followed by failure diagnosis. This is one of the strongest implementation labs and the appropriate pattern for later chapters.
- **I — Solutions:** Explain missing-evidence versus stub limitations and alternative context choices. They do not infer general answer correctness from the two supported tasks.
- **J — Visuals:** Preparation and request sequence are technically consistent. Figure 02.02's seven-lane landscape layout is useful but printed labels are near the contract minimum, around 6.52 pt; zoom is needed for comfortable reading.
- **K — Experiments:** Controlled changes to depth, window and budget isolate boundary failures on one frozen corpus. These are diagnostic comparisons, not general optimization results.
- **L — Evaluation:** Exact supported-clause availability and stub outcomes are appropriate before judged ranking metrics. The small task count is stated.
- **M — Observability:** Request/query IDs, timestamp, source snapshot, candidate IDs/raw scores, context/evidence IDs, wall/stage timing, status/reason and redacted logs form a strong initial contract.
- **N — Security:** Legal-only D10 is excluded before candidate scoring and prompt assembly. Tests verify omission from ordinary traces and context. Scope strings are fixture data, not authentication.
- **O — Production connection:** Identity, permissions, budgeting, diagnostics and reproducible failure matter more than the simple score. The connection is credible without framework dependence.
- **P — Mastery gate:** The lab genuinely enables building and explaining the stated local loop. It does not imply that a production generator has been evaluated.

### Chapter 03

**Evidence:** `chapters/chapter-03-data-algorithms-and-measurements-needed-for-search.md`, especially §§2, 4–6; `labs/chapter-03/LAB.md` C.3; `solutions/chapter-03-solutions.md`; `projects/V0/measurements.py`, `CHAPTER_03_MEASUREMENT.md`, both measurement JSON files; Figure 03.01.

- **A — Purpose:** Give later search chapters the minimum data-structure, complexity, unit, statistical and experiment vocabulary.
- **B — Coverage:** Lists/maps/sets, sorting, average hash lookup, linear/logarithmic growth, bytes/characters/lexical terms/model tokens, scalar vector/norm examples, probabilities, percentiles and leakage are explained and practised. Matrix notation needed for later actual training remains an incomplete bridge (P1-02); 04/11 do supply small softmax/loss arithmetic.
- **C — Technical correctness:** Expected successful linear-search comparisons at N=16 are 8.5; log2(1024)=10. The amortization example 120/(30−0.2) requires five queries. The nearest-rank p95 of [2,3,4,6,20] is 20; the mean is seven. No incorrect Big-O-to-latency conversion was found.
- **D — Pedagogy:** The same exact-ID task makes the structure comparison accessible. “A failure of the tempting interpretation” explicitly prevents treating an ID-lookup speedup as an IR/RAG speedup.
- **E — Depth:** Strong on separating cost models from measured work and seconds. The “small mathematics” section is too compact to serve as the full prerequisite for matrix attention and neural updates; this is a continuity problem, not wrong scalar arithmetic.
- **F — Worked examples:** The cosine example has dot product four and norms sqrt(5), giving .8. Units and intermediate arithmetic are present. The balanced hit/miss workload differs deliberately from the all-miss experiment and is labeled.
- **G — Code:** Seeded queries, consumed results, prebuilt maps, timed batches, warmup and alternating order are sensible. Seven trial batches of 256 queries estimate batch-average lookup time. Map build cost is one sample, accurately labeled.
- **H — Lab:** Independent scan/map functions, measured repeats and explaining amortization require implementation and experiment reasoning. However C.3 runs `measurements.py` without `--output`; its default overwrites `chapter-03-measurements.json` (P2-01).
- **I — Solutions:** Explain workload, units, build amortization and why two differently mixed workloads are not directly comparable.
- **J — Visuals:** Figure 03.01 uses corpus size, microseconds and growth axes correctly. Its interval depicts variation in batch means, not service latency tails.
- **K — Experiments:** The replay reproduced workload construction and mechanisms. Local N=16,384 scan/map medians were about 419.76/.248 µs versus saved 528.28/.259 µs; timing differences are expected, not failed reproduction.
- **L — Evaluation:** Exact ID parity is the task's correctness measure. No relevance metric is appropriate here. The chapter keeps measurement noise and algorithmic work separate.
- **M — Observability:** Raw timing samples, environment, sizes, mixture, seed and units are retained as experiment provenance. This characterization is not pretending to be a service request trace.
- **N — Security:** No new authorization mechanism is required. The experiment uses synthetic IDs and does not expose source text.
- **O — Production connection:** Build cost, input distributions, memory/disk and misleading benchmarks are directly relevant. Database-service vocabulary is introductory; durability/transactions belong to Chapter 18.
- **P — Mastery gate:** The programming/measurement gate is supported. Readiness for later matrix/gradient notation needs P1-02. Its conditional distinction between unseen-family transfer and new queries over a known corpus should be made explicit in Chapter 12's chosen split; the Chapter 12 solution also gives stronger family-grouping advice (P1-06).

### Chapter 04

**Evidence:** `chapters/chapter-04-what-an-llm-does-with-supplied-context.md`, “What attention can and cannot do” and context-budget/probe sections; `labs/chapter-04/LAB.md`; `solutions/chapter-04-solutions.md`; `projects/V0/context_probes.py`, `chapter-04-case-manifest.json`, `CHAPTER_04_CONTEXT_PROBES.md`; Figures 04.01–04.02.

- **A — Purpose:** Explain why supplying relevant text does not establish a correct, faithful answer; distinguish selection, visibility, interpretation and supported claims.
- **B — Coverage:** Token prediction, context positions, truncation, distraction, conflicts, instructions versus untrusted data and model-adaptation alternatives are explained. Attention is explained intuitively but its matrix expression is introduced beyond the taught mathematics.
- **C — Technical correctness:** The next-token product .7×.8=.56, scaled masked attention and logits [0,ln(3)] → unnormalized weights [1,3] → softmax [.25,.75] are correct. The budget 4096−512−240−40−64=3240 leaves 3,500 planned evidence tokens 260 over budget. These are token quantities, not source-word counts.
- **D — Pedagogy:** Prompt slots and claim cards are concrete. The matrix expression assumes shapes/transpose not established in Chapter 03, but the prose explicitly presents it as intuition and supplies a valid scalar softmax example. A dimensions/value-weighted-sum bridge would improve formal fluency; its absence does not defeat the stated small-softmax gate.
- **E — Depth:** Sufficient on supplied-context failures, small normalization and adaptation choices. A full Transformer derivation is not owed here. The matrix formula is not a fully implementable lesson, and is accurately labeled an intuition.
- **F — Worked examples:** Five positions use the same evidence and preserve the intended comparison; conflict/injection fixtures expose different mechanisms. The conflict prompt's character counts differ slightly, and the notes acknowledge confounding. No position-dependent model result is fabricated.
- **G — Code:** `context_probes.py` builds ten deterministic prompt cases and records measurements/inputs. Model outputs are null. Its literal support/claim fixtures teach review, not automated general entailment.
- **H — Lab:** Holding evidence fixed, identifying visibility/support and explaining conflict/prompt-injection behavior require judgment. Without an optional model run, this is a prompt-design and diagnosis exercise, not evidence for a particular model's lost-in-the-middle behavior.
- **I — Solutions:** Correctly distinguish faithful-to-a-wrong-source from world-correct and missing evidence from bad generation. They preserve caveats about unrun model outcomes.
- **J — Visuals:** The autoregressive feedback loop and prompt-to-claims diagram teach distinct processes and agree with the prose. Rendered attention formula and budget example were inspected without clipping.
- **K — Experiments:** Question/variables/controls and null outcomes are honestly scoped. A supplied prompt manifest is a reproducible experiment setup, not a completed model experiment.
- **L — Evaluation:** Claim-to-source inspection is appropriate; retrieval score is not answer confidence. Empirical model accuracy remains explicitly unmeasured.
- **M — Observability:** Case IDs, prompt versions/measurements and absent outputs are retained. This extends V0 characterization without falsely filling generation telemetry.
- **N — Security:** Retrieved instruction text is treated as untrusted data. Relevant text does not gain authority to override the application's policy.
- **O — Production connection:** Context budgets, changing information, provenance and instruction boundaries are relevant without framework documentation.
- **P — Mastery gate:** Conceptual, small-softmax and claim-review capability is supported. As the end of Part I, this chapter lacks the explicit cumulative part quiz/prior-version checkpoint promised in `SYLLABUS.md` (P1-05); its from-memory figure tasks are meaningful but narrower.

### Chapter 05

**Evidence:** `chapters/chapter-05-text-normalization-and-inverted-indexes.md`, §§1–5; `labs/chapter-05/LAB.md`, “Build and inspect” and “Explain and defend”; `solutions/chapter-05-solutions.md`; `projects/V1/lexical_index.py`, `experiment.py`, `test_lexical_index.py`, `toy_corpus.json`; Figures 05.01–05.02.

- **A — Purpose:** Build a positional inverted index, avoid scanning all source text and explain analyzer/phrase behavior.
- **B — Coverage:** Field/term/position/vocabulary, forward versus inverted data, AND/OR/anchored NOT, phrase offsets and skip ideas are explained. Reference postings and phrases are implemented. Stemming/lemmatization/ngrams/fuzzy search are trade-offs, not quietly substituted for this chapter's actual analyzer.
- **C — Technical correctness:** Unicode normalization/casefold followed by the declared ASCII token rule has explicitly shown losses. Field-local positions prevent matching across title/body. The V0 index has 119 terms, 222 term–segment pairs and 247 positions, consistent with the recorded build.
- **D — Pedagogy:** A hand postings table precedes index abstractions. Rare codes, repeated terms and false phrase matches make the reason for positions clear. New analyzer options are situated rather than used as unexplained magic.
- **E — Depth:** Strong build/query/storage decomposition. Phrase matching, scoped Boolean NOT and forward reconstruction are concrete; alternatives need not all be implemented to meet the core objective.
- **F — Worked examples:** Learners predict postings/positions and inspect rare codes/misspellings. A repeated-term phrase test exposes why membership alone is insufficient.
- **G — Code:** `lexical_index.py` uses explicit postings/forward records and readable query functions. Index statistics and protected-scope work are inspectable. Tests and runner passed.
- **H — Lab:** Hand construction, analyzer changes and unsafe-query diagnosis require thought. However “Build and inspect” executes supplied code; deliverables do not require an independently written postings builder and positional phrase matcher as the syllabus does (P1-01).
- **I — Solutions:** Explain term losses and phrase/permission mistakes. They cannot establish learner implementation mastery when the lab does not ask for that implementation.
- **J — Visuals:** Figure 05.01 connects stored source fields to postings. Figure 05.02 shows scope filtering and posting intersection. Both are necessary and readable.
- **K — Experiments:** V0 comparison states unchanged corpus and question behavior. Fewer text scans are measured separately from local Python latency; the index need not win every tiny case.
- **L — Evaluation:** Exact candidate/phrase behavior and workload counters suit the mechanism. Judged quality is appropriately deferred to Chapter 09.
- **M — Observability:** V1 retains the redacted request path and adds analyzer/index versions and posting/work details. This is a good example of progressive instrumentation.
- **N — Security:** Scope eligibility precedes accumulating/scoring candidates; NOT is anchored in an eligible universe. A restricted source is not recovered through a Boolean complement.
- **O — Production connection:** Immutable index/forward-source separation and normalization failures connect to real search without presenting a vendor's analyzer as the concept.
- **P — Mastery gate:** Explain/trace/debug is supported. “Build an index” needs an independently constructed artifact, not only reference execution.

### Chapter 06

**Evidence:** `chapters/chapter-06-tf-idf-vector-space-ranking-and-lexical-limits.md`, §§1–5; `labs/chapter-06/LAB.md` A–F; `solutions/chapter-06-solutions.md`; `projects/V1/tfidf.py`, `experiment_ch06.py`, `toy_ranking_corpus.json`, `test_tfidf.py`; Figure 06.01.

- **A — Purpose:** Derive term weights, compute a lexical score and explain why rankings reverse after a corpus change.
- **B — Coverage:** TF/DF/N/IDF, missing/ubiquitous terms, sparse vectors, raw/sublinear variants, cosine and field boosts are explained, demonstrated and implemented. Independent scorer construction is not required by the lab despite its syllabus requirement.
- **C — Technical correctness:** The chosen IDF is ln(N/df), not a universal TF-IDF law. Sublinear TF is applied to positive raw counts before field boosts. Cosine uses all vocabulary contributions in document norms. A matched zero-IDF vector and an absent query have distinct, explicitly declared policies.
- **D — Pedagogy:** Count statistics precede the equation and sparse representation. The corpus mutation isolates why an unchanged document's weight can change.
- **E — Depth:** Strong factor decomposition and boundary behavior; length effects are not confused with BM25 length normalization. There is enough material to build a scorer, but the assessment does not require doing so.
- **F — Worked examples:** Raw scoring reverses T2>T1 to T1>T2 after the added document; the sublinear alternative behaves differently. This is a reproducible corpus-statistics example rather than a vague IDF explanation.
- **G — Code:** `tfidf.py` exposes statistics, contributions, norms and declared weighting modes. Tests cover rank reversal, zero/missing terms, scope-local statistics and small positive title boosts. All passed.
- **H — Lab:** Predict-before-run arithmetic, one-choice weighting changes and three diagnoses are substantial. No explicit independently implemented TF-IDF deliverable exists (P1-01).
- **I — Solutions:** Derive the ranking and explain policy alternatives. Their reasoning is strong, though an implementation task and matching explained solution are needed to support the promised skill.
- **J — Visuals:** Figure 06.01's annotated sparse matrix and before/after weights teach why corpus changes affect ranking. Its zeros and nonzeros agree with calculations.
- **K — Experiments:** The one-document addition and weighting comparisons hold other choices fixed. V0 comparisons retain the same candidate/context path, including a loss rather than only a win.
- **L — Evaluation:** Rank/required-evidence behavior is diagnostic, not a judged universal gain. Explicitly postponing broad evaluation until qrels is appropriate.
- **M — Observability:** V1's scorer adds weighting and corpus-statistic identity while retaining candidate/context IDs and redacted trace behavior.
- **N — Security:** Statistics are scoped for the query's eligible corpus; restricted records do not contribute to this fixture's ranking or ordinary trace.
- **O — Production connection:** Analyzer choice, corpus drift and score incompatibility have clear system implications. Synonym mismatch motivates learned representations later.
- **P — Mastery gate:** Derivation and failure explanation are supported. Implementation mastery remains reference-only.

### Chapter 07

**Evidence:** `chapters/chapter-07-bm25-and-other-lexical-ranking-models.md`, especially “Saturate repetition and expose length,” “The family” and “Debug and tune”; `labs/chapter-07/LAB.md`; `solutions/chapter-07-solutions.md`; `projects/V2/bm25.py`, `experiment_ch07.py`, `toy_length_corpus.json`; Figure 07.01.

- **A — Purpose:** Calculate and tune BM25; understand why lexical scoring remains a serious baseline.
- **B — Coverage:** Nonnegative IDF, relevance/odds intuition, TF saturation, k1, b, average length and worked summation are genuinely decomposed. BM25+, fielded scoring and smoothed query likelihood are explained at a comparison level. Actual judged parameter fitting is missing.
- **C — Technical correctness:** The log1p IDF convention is correctly separated from potentially negative Robertson-style variants. The TF factor approaches k1+1; b=0 disables the length factor. Average length is over the declared corpus, not only current matches. Ad-hoc field boosts are not called full BM25F.
- **D — Pedagogy:** Failure of repetition/length handling precedes the formula. Parameter curves and a complete score calculation make the notation usable.
- **E — Depth:** Meets the requested BM25 decomposition for factors, calculation, limits and failure. “Calculate and tune” is only partly met: explanations of fitting are not a performed tuning/validation decision.
- **F — Worked examples:** Long versus short texts isolate TF and normalization; parameter extremes are interpretable. Figure functions are mathematical factors, not a claim that every plotted TF/length combination is a realizable document.
- **G — Code:** `bm25.py` splits build statistics from query contributions; parameters and tie behavior are inspectable. Baseline and invalid-parameter tests passed.
- **H — Lab:** Includes independent saturation calculation/function work and long/short comparison, but not a complete independently written scorer (P1-01). It explicitly waits for Chapter 09 before judged tuning; Chapter 09 never supplies that activity (P1-04).
- **I — Solutions:** Explain factor behavior and why a higher raw score does not prove better evidence. They do not provide a completed parameter-selection example.
- **J — Visuals:** Figure 07.01's saturation and length panels are accurate and instructionally necessary. Labels, parameter settings and units agree with the prose.
- **K — Experiments:** Baselines and variants are controlled, with lexical failure retained. Changing k1/b is a mechanism experiment, not held-out optimization.
- **L — Evaluation:** At this stage judgments are legitimately deferred. The debt becomes real after Chapter 09 is complete and tuning is still only advice.
- **M — Observability:** V2 adds scorer/parameter identity, IDF/statistics and work while keeping earlier redacted request data.
- **N — Security:** Eligibility and corpus-statistic scope remain hard constraints; increasing score cannot authorize a source.
- **O — Production connection:** Lucene's documented implementation choices are cited as choices; corpus/analyzer workload matters more than claiming BM25 always wins or loses.
- **P — Mastery gate:** Learners can derive, calculate and debug BM25. A measured tune/select/holdout task is needed to substantiate the tuning objective.

### Chapter 08

**Evidence:** `chapters/chapter-08-production-lexical-query-execution.md`; `labs/chapter-08/LAB.md` §§1–5; `solutions/chapter-08-solutions.md`; `projects/V2/wand.py`, `postings_codec.py`, `experiment_ch08.py`, `toy_pruning_corpus.json`, `test_wand.py`; Figure 08.01.

- **A — Purpose:** Return the same top-k BM25 ranking while scoring fewer matching documents; explain when a pruning bound is safe.
- **B — Coverage:** TAAT/DAAT, gaps/variable bytes, heap threshold, cursor movement and global WAND are explained, demonstrated and implemented. MaxScore, impact ordering, segments and Block-Max WAND are explanatory comparisons, not mislabeled as implemented BMW.
- **C — Technical correctness:** IDs [3,8,138] become gaps [3,5,130] and bytes 83 85 01 82 in hexadecimal under the declared codec. Nonnegative score bounds, outward rounding and tie conservatism are explicit. Independently checked WAND rankings/raw scores agree with exhaustive BM25.
- **D — Pedagogy:** A top-k heap is introduced locally before it is relied upon. A concrete threshold/cursor decision precedes optimization terminology.
- **E — Depth:** Particularly strong: it explains what is skipped, the score bound, why ties need care and why fewer scores may still be slower. No universal speedup is implied.
- **F — Worked examples:** P1 sets a threshold about 1.093526; common-term bound about .256 cannot beat it. A seek skips P2–P5 and scores P6, reducing six full scores to two; P6 about .983 still loses. The figure agrees.
- **G — Code:** `wand.py` exposes advancement/bounds/heap rather than delegating to a library. Existing tests and 600 additional seeded parity cases passed. This is empirical support, not a proof for arbitrary floating-point extremes.
- **H — Lab:** Byte work, cursor prediction, optimizer debugging, exactness/work/time comparison and oral defense are excellent. The required toy pruning implementation is not a deliverable: §2 traces supplied code, §3 runs it (P1-01).
- **I — Solutions:** Explain threshold safety, conservative equal-score handling and why latency can lose. Add a worked learner implementation solution when the task is added.
- **J — Visuals:** Figure 08.01 clearly separates executable global WAND from conceptual block bounds. It teaches advancement and the moving threshold without pretending the implementation is block-max.
- **K — Experiments:** Exhaustive BM25 remains the oracle; exact top-k agreement is distinct from scored-document reduction and latency. Negative speed results are preserved.
- **L — Evaluation:** Exact rank parity is the optimizer's correctness criterion, not judged relevance. This distinction prepares Chapter 09 correctly.
- **M — Observability:** Execution counters, posting movement, scorer identity and candidate/context trace remain available. The optimized route does not erase its baseline.
- **N — Security:** Eligible posting work is gated; pruning is about relevance cost, not authorization. Tests cover scope parity.
- **O — Production connection:** Disk postings and segments are situated correctly; the small in-memory Python implementation teaches a mechanism without masquerading as production throughput.
- **P — Mastery gate:** Learners can trace/defend safe pruning. The implement-from-principles part of the contract is untested.

### Chapter 09

**Evidence:** `chapters/chapter-09-relevance-judgments-and-ranking-metrics.md`; `labs/chapter-09/LAB.md`; `solutions/chapter-09-solutions.md`; `projects/V2/eval_ch09.py`, `judgments_ch09.json`, `experiment_ch09.py`, `test_eval_ch09.py`; Figure 09.01.

- **A — Purpose:** Define relevance on a declared universe, calculate set/rank measures and compare retrieval without confusing scores with truth.
- **B — Coverage:** Qrels, units, assessor disagreement, pooling/incomplete judgments, binary versus graded labels, P/R/F1/hit/MRR/AP/MAP/DCG/NDCG, macro/micro, ties and cutoffs are taught. The delayed Chapter 07 tuning exercise remains absent.
- **C — Technical correctness:** Fourteen queries have all 168 eligible query–segment pairs reviewed with grades 0/1/2. Binary relevance is grade ≥1; direct evidence is grade 2. AP's denominator is all relevant items, not just those retrieved. Exponential-gain NDCG is a declared convention, not the only possible DCG.
- **D — Pedagogy:** Ranked lists and judgments precede metric equations. Zero-positive and unjudged cases prevent misleading denominator shortcuts.
- **E — Depth:** Strong decomposition of metrics and their failure modes. Assessor agreement is an illustrative calculation rather than a fabricated multiple-assessor study.
- **F — Worked examples:** Three rankings expose precision/order/gain differences with intermediate calculations. Missing slots, no-positive queries and macro/micro differences are directly tested.
- **G — Code:** `evaluate_ranking` and loaders reject malformed rosters/grades and preserve null undefined metrics. Tests passed. **Observed gap:** `load_judgments` checks snapshot string and IDs, not source-content identity; a changed clause with unchanged IDs/snapshot was accepted (P1-07).
- **H — Lab:** Independent metric functions, hand calculations, rubric critique and cumulative Part II recall satisfy the main evaluation objective. Add a small development/held-out tuning exercise to close P1-04.
- **I — Solutions:** Explain denominator/convention choices and consequences, rather than reporting numbers alone. They do not pretend unjudged records are proven irrelevant.
- **J — Visuals:** Figure 09.01 pairs relevance labels, rank and cumulative discounted gain correctly. Smaller annotations need zoom at reduced sizes, but the teaching point remains legible.
- **K — Experiments:** Same corpus/workload/labels compare overlap, BM25 and WAND. Saved mean NDCG@2 is about .9091 for overlap versus .899686 for BM25; WAND equals BM25. A more sophisticated score is allowed to lose.
- **L — Evaluation:** Appropriate retrieval metrics, complete tiny qrels and honest one-author limits. No general quality winner is claimed from fourteen fictional requests.
- **M — Observability:** Query-set/version, sample window, raw timings, ranking IDs/scores and context/stub boundaries are retained; quality and service timing are distinct records.
- **N — Security:** D10 lies outside the support-team eligible judgment universe, not among “irrelevant negatives.” This avoids teaching authorization as a soft relevance feature.
- **O — Production connection:** Assessment cost, pooling, biased workloads and failure slices prepare engineering evaluation. Formal full-RAG evaluation is appropriately later.
- **P — Mastery gate:** Ranking-metric mastery is supported. Complete Part II checkpoint is present; BM25 tuning and content-bound judgment integrity are targeted additions.

### Chapter 10

**Evidence:** `chapters/chapter-10-vectors-distance-and-exact-similarity.md`; `labs/chapter-10/LAB.md`; `solutions/chapter-10-solutions.md`; `projects/V3/exact_vectors.py`, `experiment_ch10.py`, `test_exact_vectors.py`; Figure 10.01.

- **A — Purpose:** Calculate vector similarities and implement a trustworthy exact-neighbor oracle before learning or approximation.
- **B — Coverage:** Dense/sparse representation, norms, dot/cosine/L1/L2, unit relationships, exhaustive score work, sort/heap, batching and memory are demonstrated and implemented. Anisotropy is introduced as an intuition, not claimed mastered.
- **C — Technical correctness:** For unit vectors squared L2 = 2−2 cosine, so order equivalence needs normalization and deterministic ties. Raw dot and cosine differ when norms differ. Zero, nonfinite, dimension and duplicate-ID cases have explicit policies.
- **D — Pedagogy:** Small coordinates precede corpus vectors. The chapter explicitly uses 119-dimensional binary lexical coordinates before a learned model; “dense array” does not become “semantic embedding.”
- **E — Depth:** Excellent oracle-first discipline, score direction and tie explanation. Matrix batching is present but dimension mechanics remain terse (P1-02).
- **F — Worked examples:** Metric-dependent ranks and unit normalization expose why “nearest” needs a specified metric. Figure 10.01's A/B order uses declared ID tie-breaking where scores tie.
- **G — Code:** `ExactIndex` provides full-sort and bounded-heap plans, work counters and scope gates. Additional 360 seeded metric/plan comparisons agreed. The materialized eligible roster means auxiliary memory is not magically only O(k).
- **H — Lab:** Independent brute-force top-k, hand distances and edge tests satisfy the actual implementation objective.
- **I — Solutions:** Explain metric choices, ties, zero-vector policy and exact-work cost. They establish why an oracle is needed for later ANN.
- **J — Visuals:** Figure 10.01 is accurate and useful. The warning that two-dimensional geometry does not establish high-dimensional performance is appropriate.
- **K — Experiments:** Same Chapter 09 qrels compare binary cosine with BM25. Cosine mean NDCG@2 about .772408 loses to BM25; this is an honest representation negative result.
- **L — Evaluation:** Judged relevance and vector similarity remain distinct. No ANN recall is measured before approximation exists.
- **M — Observability:** Candidate scores, work, context IDs and declared coordinate/model absence are retained. Later common request correlation is incomplete at the V3 runner layer (P1-03).
- **N — Security:** Eligible vectors are selected before similarity scoring. Scope is explicitly static fixture policy; invalid numeric inputs are rejected.
- **O — Production connection:** Raw coordinate storage, memory layout, exact work and batching motivate later index decisions.
- **P — Mastery gate:** Hand metrics and independent exact top-k are supported. No missing ANN mechanism is owed at this point.

### Chapter 11

**Evidence:** `chapters/chapter-11-how-embedding-models-learn-retrieval-spaces.md`, especially §§2–3 and experiment discussion; `labs/chapter-11/LAB.md`; `solutions/chapter-11-solutions.md`; `projects/V3/contrastive_math.py`, `experiment_ch11.py`, `judgments_ch11.json`, `test_ch11.py`; Figure 11.01.

- **A — Purpose:** Explain a text encoder, independently calculate pooling/loss, and compare a real frozen encoder with lexical retrieval.
- **B — Coverage:** Token/contextual/sentence representations, masks, pooling, tower roles/asymmetry, prefixes, positives/negatives, temperature and model limits are explained. Multilingual and Matryoshka choices are properly conditional, not demonstrated capabilities of the chosen model.
- **C — Technical correctness:** The pinned MiniLM model produces 384-dimensional vectors with a 256-word-piece maximum in its card. Shared encoding is appropriate for this selected model, not a universal dual-encoder rule. The [[3,1],[0,2]] score fixture gives loss .126928 at temperature one.
- **D — Pedagogy:** Pooling and a small matrix precede the actual model experiment. The two rows work exponential normalization and log loss explicitly, building on 04's softmax. Connecting this arithmetic to the code's general subtract-max/log-sum-exp stability would improve the implementation bridge.
- **E — Depth:** Good distinction between contrastive evidence and “embeddings understand meaning.” False negatives, temperature and arbitrary truncation of non-Matryoshka vectors are substantive. Loss is computed, but how parameters move is deferred to 12 and still needs a bridge there.
- **F — Worked examples:** Masked mean excludes padding; a positive diagonal is a declared label, not truth. Constant scores yield ln(2)≈.693147 versus .126928 for the separated fixture. The hand example is reproducible.
- **G — Code:** `contrastive_math.py` exposes masked mean and numerically stable row loss. Encoder revision `8b3219a92973c328a8e22fadcfa821b5dc75636a` is pinned; uncached download requires the explicit flag. Cached offline replay succeeded.
- **H — Lab:** Independent pooling/loss plus paired retrieval analysis satisfy the comparison task. The worked row already simplifies exponentials by a common factor; explicitly relating that cancellation to subtracting the maximum would help learners generalize numerical stability.
- **I — Solutions:** Explain paraphrase wins, Basic/Pro confusion, metadata-ID failures and no-evidence candidates. They refuse to read a high cosine as supported answer confidence.
- **J — Visuals:** Figure 11.01 shows independent encoders and all pair scores. The diagonal label assumption and units/nats are clear and correct.
- **K — Experiments:** Seventeen authored questions give 204 reviewed pairs: eight paraphrase, six exact-ID and three no-eligible-evidence. Paraphrase Recall@2 rises .8125→1; identifier recall stays .6667; positive-query NDCG@2 rises .707596→.830781. These are slice results, not a universal dense win.
- **L — Evaluation:** Separate query set from 09; explicit no-positive behavior and absent generation. Comparison within this paired experiment is valid; comparing its headline score to 09's different workload as progress would not be.
- **M — Observability:** Model/input/index identity, candidate/context IDs and encode/scan timing samples are valuable. Per-execution correlation and status are less consistent than the V0 facade (P1-03).
- **N — Security:** D10 is excluded before support-team similarity/context work; ordinary records use IDs rather than source/question content.
- **O — Production connection:** Passage/query format compatibility, storage, domain shifts and literal IDs are practical. The selected model is not marketed as the right universal embedding.
- **P — Mastery gate:** Pooling, contrastive arithmetic and model-selection defense are supported. First-principles parameter learning is not yet supported by this chapter alone, as appropriately intended.

### Chapter 12

**Evidence:** `chapters/chapter-12-retriever-training-and-domain-adaptation.md`, split discussion and adaptation section; `labs/chapter-12/LAB.md` A–D; `solutions/chapter-12-solutions.md`; `projects/V3/experiment_ch12.py` (`load_split`, `train_adapter`), `judgments_ch12.json`, `chapter-12-experiment.json`, `test_ch12.py`; Figures 12.01–12.02.

- **A — Purpose:** Adapt a query tower, select using validation and test whether the adaptation generalizes rather than merely lowering training loss.
- **B — Coverage:** Actual training, reviewed positives/negative masks, hard-negative/mining/distillation alternatives, loss families, validation selection and over-specialization are present. Broader language/domain transfer is explained/proposed, not a measured multilingual training gain. How a loss induces a parameter update is insufficiently taught.
- **C — Technical correctness:** Rank-16 query projection `normalize(u+B A u)` with A 16×384 and B 384×16 has 12,288 parameters. Four-byte parameters total 49,152 bytes, **48 KiB**, not “about 49 KiB” (line 69); the solution file already gives the correct 48 KiB. “Chapter 41 will address experiment design” (line 63) points to the wrong chapter; experiment design is Chapter 48 (P2-02).
- **D — Pedagogy:** The loss/mask motivation is good. First use of autodiff, Adam, matrix transpose/multiplication and backpropagation requires a small explicit update explanation; the code's `.backward()`/`.step()` is not that explanation (P1-02).
- **E — Depth:** Strong experimental decomposition and honest adaptation boundary: transformer/passage vectors remain frozen. Weak first-principles optimization decomposition. A scalar or two-coordinate loss-gradient-update example would close the gap without teaching full Transformer training.
- **F — Worked examples:** The label matrix identifies same-source/valid-alternative false negatives. Training loss falls about .249→.013 by epoch five while validation Recall@2 collapses 1→0. Selected epoch one yields test Recall@2 .889, equal to frozen .889; BM25 is .667. No gain is the correct decision.
- **G — Code:** Actual gradient training is implemented, seeds and model are fixed, training negatives are restricted to train documents, and selection precedes test scoring. The selected epoch and adapter hash reproduced. Test label structures are validated early but are not used for optimization; early parsing is not itself test-score leakage.
- **H — Lab:** Freeze/audit labels, work loss, run actual adaptation, diagnose and reject a tempting training-loss interpretation. This aligns with the experiment task, but mostly exercising the full supplied trainer limits independent update mastery.
- **I — Solutions:** Strong explanation of masks, loss-versus-generalization and alternatives. The advice to keep revisions together is stronger than the actual fixture's document-ID split (P1-06).
- **J — Visuals:** Figures 12.01–12.02 correctly show reviewed labels and train/validation/test paths. The split visual marks different IDs; it does not prove source-family independence. A learning-history/update-motion visual would teach a currently missing mechanism rather than add decoration.
- **K — Experiments:** Ten authored training pairs, frozen passages, validation-selected checkpoint and held-out test provide a real small experiment with a retained negative outcome. However train D1/D2 and validation D3 concern the same Helios agreement family. Document-disjoint is not family-disjoint.
- **L — Evaluation:** Per-slice judgments and retrospective earlier probes are distinguished. One author, small authored split and related wording limit independence. Do not turn this into a broad domain/language-shift claim; the current text largely respects that limit.
- **M — Observability:** Training history, masks, code/corpus/split/model hashes, selected checkpoint, candidates/context and timings are retained. Correlation/status consistency remains P1-03.
- **N — Security:** The training/retrieval universe is eligible and protected D10 does not become a negative. False-negative masks address relevance, not authentication.
- **O — Production connection:** Teacher bias, source families, model/index compatibility, over-specialization and memory are relevant. Rejected adaptation is a useful production decision.
- **P — Mastery gate:** Learners can defend experimental selection and diagnose failure. The intended “train from understanding” capability requires P1-02, and the split discipline needs P1-06; current data do not establish family-level holdout generalization.

### Chapter 13

**Evidence:** `chapters/chapter-13-dense-candidate-retrieval-in-practice.md`; `labs/chapter-13/LAB.md`; `solutions/chapter-13-solutions.md`; `projects/V3/dense_snapshot.py`, `experiment_ch13.py`, `judgments_ch13.json`, `index_ch13/manifest.json`, `index_ch13/vectors.f32`, `test_ch13.py`; Figures 13.01–13.02.

- **A — Purpose:** Build/reload a dense index with an explicit compatibility contract and diagnose why exact dense retrieval still misses relevant evidence.
- **B — Coverage:** Batches, float32 vectors/IDs, normalization, model/input pairing, versioning, exact top-k, throughput and failure slices are implemented and demonstrated. ANN and durable migrations are correctly deferred.
- **C — Technical correctness:** Thirteen ×384×4 =19,968 coordinate bytes. All 34 comparisons of in-memory/materialized IDs matched; selected raw-score differences were zero. Text digests, scopes, row order, model revision, metric, checksum and unit-vector checks prevent incompatible serving.
- **D — Pedagogy:** Materialization solves a concrete recomputation/compatibility problem. The learner sees what is persisted and what a request still computes.
- **E — Depth:** Strong index/build/query split and version invariants. The manifest teaches an operational concept that later ANN implementations inherit.
- **F — Worked examples:** Wrong revision, corrupted bytes and changed source rows are explicit failure probes. Fourteen new stress questions span seven two-query slices, including metadata IDs and Spanish-to-English probes.
- **G — Code:** `write_snapshot`/`load_snapshot` expose format validation; scoped exact scoring is retained. Corruption/version/security tests and the full runner passed. A local two-file writer is not an atomic production migration, and the manuscript does not claim otherwise.
- **H — Lab:** Build/reload, corrupt a temporary copy, inspect parity and diagnose candidate/context failures. This requires active debugging, not only accepting a saved plot.
- **I — Solutions:** Explain whether failure is source, representation, metadata route, eligibility or selected context. They preserve the fact that a missing answer experiment stays unrun.
- **J — Visuals:** Figure 13.02's score traces teach incompatible raw scores and candidate diagnosis. In 13.01, startup verification is visually connected into the request flow after query encoding and the eligibility box departs from the decision-shape convention; clarify startup-versus-request placement (P2-05).
- **K — Experiments:** Saved positive-query Recall@2 is about .708 BM25/.792 dense on this new workload. Batch sizes 1/4/16 have three trials, fixed order and reported throughput about 52.6/67.8/57.8 texts/s. Fixed-order confounding is explicitly acknowledged.
- **L — Evaluation:** Corpus, questions, complete 168 judgments, depths and absent answer labels are declared. Two translated Spanish questions do not establish multilingual model quality.
- **M — Observability:** Manifest and model versioning are excellent. `evaluate_queries` saves per-query modes while `timed_queries` saves pooled timing arrays; without a sample/request join, a slow query cannot reliably be connected to its candidate trace (P1-03).
- **N — Security:** The binary file contains the legal-only fixture row, but support-team similarity/context exclude it. Persisted derived vectors remain protected artifacts; static scopes do not implement live authentication.
- **O — Production connection:** Startup rejection, paired formats, stale versions, input digests and lifecycle warnings are substantive. Framework-independent index semantics are preserved.
- **P — Mastery gate:** Supported for this local exact index and failure diagnosis. Add common correlated records; do not prematurely demand a distributed vector service.

### Chapter 14

**Evidence:** `chapters/chapter-14-sparse-neural-search-and-late-interaction.md`; `labs/chapter-14/LAB.md`; `solutions/chapter-14-solutions.md`; `projects/V3/sparse_late_ch14.py`, `experiment_ch14.py`, `test_ch14.py`; Figure 14.01.

- **A — Purpose:** Position learned sparse and token-level late interaction between literal lexical retrieval and pooled single-vector retrieval.
- **B — Coverage:** Vocabulary logits/expansion, sparse pooling/regularization, weighted postings, separate token encoding/storage, MaxSim and retrieval/reranking roles are explained. Manual operators are implemented. Full trained SPLADE/ColBERT retrieval is neither implemented nor claimed.
- **C — Technical correctness:** The maximum pooling variant is correctly distinguished from original sum-pooled SPLADE. MaxSim is sum over query tokens of maximum passage-token similarities. “log1p saturates large positive ones” (line 29) needs precision: logarithmic compression is unbounded, unlike the bounded BM25 saturation taught earlier (P2-02).
- **D — Pedagogy:** Failures of literal terms and mean pooling motivate each operator. Manual logits/vectors are explicitly fixtures, preventing a false learned-model story.
- **E — Depth:** Operator, input/storage cost, role and failure are taught. Sparsity/optimized search/training are conceptual boundaries appropriate to the syllabus's compare-and-compute task.
- **F — Worked examples:** Exact MaxSim gives 2 versus sqrt(2) while pooled cosine reverses the ordering, −1 versus +1. Reusing a passage token for multiple query-token maxima is allowed by the operator, not a one-to-one alignment.
- **G — Code:** Weighted-posting accumulation, pooling and exact MaxSim expose the mechanism. Tests and replays agree. Hand-authored expansion is not asserted to be a trained neural model.
- **H — Lab:** Hand sparse weights, independently recomputed token grid, failure/time audit and design challenge align with the syllabus's tiny MaxSim computation. The chapter's stronger “implement weighted sparse posting accumulation and exact MaxSim” gate nevertheless needs an explicit small coding task (P1-01).
- **I — Solutions:** Explain token reuse, expansion errors, storage and first-stage/rerank limitations. They do not turn fixture success into production-model evidence.
- **J — Visuals:** Figure 14.01 annotates every similarity and winning token, making the reversal easy to reproduce. It is a necessary instructional figure.
- **K — Experiments:** Two separate one-query/three-row judged fixtures answer operator questions. Thirty-one warmed scoring-only samples are tiny diagnostic measurements. The record explicitly excludes comparison with Chapter 13 performance.
- **L — Evaluation:** Complete toy labels and stage distinctions are correct; aggregate toy quality cannot establish learned-model gain.
- **M — Observability:** Four `request_trace_examples` include request/query IDs, raw scores, work, null context and `answer_status=not_run`. They show a feasible common-record pattern, but do not restore it across V3/V4.
- **N — Security:** Weighted postings are eligibility-gated; no unsafe architecture is taught. Authorization limits remain distinct from false expansion.
- **O — Production connection:** Token storage, postings reuse, candidate depth and inability to recover missing first-stage candidates prepare later ranking choices.
- **P — Mastery gate:** Operator/role/computation is supported; its independently implement-sparse/MaxSim claim is not assessed (P1-01). As Part III's final chapter, it lacks the explicit cumulative quiz and V2→V3 architecture comparison promised by the syllabus (P1-05).

### Chapter 15

**Evidence:** `chapters/chapter-15-exact-knn-to-trees-and-hashing.md`; `labs/chapter-15/LAB.md` A–C; `solutions/chapter-15-solutions.md`; `projects/V4/ann_ch15.py`, `experiment_ch15.py`, `test_ch15.py`; Figures 15.01–15.02.

- **A — Purpose:** Explain exact pruning and early approximate families, measure them against the exact oracle and diagnose approximation separately from representation failure.
- **B — Coverage:** KD build/backtracking/boxes, ball bounds, dimensional degradation, angular LSH/probabilities/buckets and both recall definitions are explained and implemented where promised. Learner LSH implementation is absent. Ball-tree code is not necessary for this syllabus lab.
- **C — Technical correctness:** KD bounding-box lower bounds safely prune only when unable to beat the current worst result with tie rules. Ball lower bound max(0,dist(q,c)−r) follows triangle inequality. Random Gaussian hyperplanes yield collision 1−theta/pi; independence assumptions are stated.
- **D — Pedagogy:** Exact scan is the known baseline; two-dimensional success and higher-dimensional failure prevent an unjustified “trees are logarithmic” claim.
- **E — Depth:** Build/query/parameters/failure/debug are substantial. Space cost is discussed qualitatively rather than fully derived for boxes/buckets; useful to tighten before graph memory claims, but not a current blocker.
- **F — Worked examples:** At 60°, one bit collides with probability 2/3; four bits in one table 16/81; four independent tables give about .5864. The two-dimensional partition/bucket fixture exposes an ID no refinement can recover.
- **G — Code:** KD parity and scoped deterministic LSH were exercised. Ninety additional random KD/full-scan cases agreed. LSH checks scope before cosine; empty buckets stay empty rather than silently falling back to exact search.
- **H — Lab:** Hand bounds/probabilities, code trace, workload comparisons and localizing misses are demanding. “Construct a lossy hash” asks tracing supplied code; no independent LSH build is required despite the syllabus's explicit implementation task (P1-01).
- **I — Solutions:** Explain fewer visits versus lower latency, geometric versus judged recall, and reasons to retain exact search. They do not equate a qrel tie with safe deployment.
- **J — Visuals:** Figure 15.01 shows different candidate sets on the same coordinates. Figure 15.02 separates cost and recall and correctly contrasts low/high dimensions.
- **K — Experiments:** At N=2048,d=2 KD scores about 8.4 rather than 2048 and is faster; at d=32 it scores about 2047.6 and is slower. On V0, L=8,h=4 matches judged recall .792 but has geometric recall .786 and is slower than exact. These negative outcomes are retained.
- **L — Evaluation:** Synthetic geometric labels and V0 human-authored qrels are separate. Fixed seed/workloads and small warmed local samples are disclosed.
- **M — Observability:** V0 cases include `request_id=ch15-{qid}`, query ID, modes, candidate/raw scores and context IDs. Aggregate timing still lacks a complete correlated execution record (P1-03).
- **N — Security:** Trusted prefiltered KD fixture rosters and scope-gated LSH are explicitly limited. The caller's string is not authentication; no protected D10 context was observed.
- **O — Production connection:** Exact-oracle gates, filtered workloads, build/encoding cost and memory prevent premature ANN adoption.
- **P — Mastery gate:** Explain/trace/measure is supported. Implement-LSH mastery is not assessed; formal graph vocabulary belongs locally in 17, so its absence here is not a violation.

### Chapter 16

**Evidence:** `chapters/chapter-16-ivf-quantization-and-compressed-vectors.md`, §§1–6; `labs/chapter-16/LAB.md` A–C; `solutions/chapter-16-solutions.md`; `projects/V4/ivf_pq_ch16.py` (`train_kmeans`, `IVFPQ.search`, `add`, `delete`), `experiment_ch16.py` (`measure`, `v0_case`), `test_ch16.py`; Figures 16.01–16.02.

- **A — Purpose:** Trace coarse assignment/probing, residual product quantization, ADC, storage and exact refinement while separating their error gates.
- **B — Coverage:** nlist/nprobe, centroid training, lists, residual/codebook training, scalar/PQ comparison, reconstruction, ADC tables, reranking, imbalance and lifecycle are explained and implemented. Durable updates/sharding are appropriately future work. Learner coarse/PQ construction is absent.
- **C — Technical correctness:** All-probe IVF-Flat equals exact given the stated matching metric/roster/ties and no scan cap; all-probe PQ does not. Code implements deterministic farthest-first Lloyd training and residual codebooks. Thirty additional full-probe parity and sixty scope/delete probes passed.
- **D — Pedagogy:** List misses are separated before compression is added. The hand codebook is concrete. The training loop is explained in steps but a hand centroid-update example would better support the “implement toy cells/PQ” lab.
- **E — Depth:** Strong error and bytes decomposition: adding more lists cannot guarantee exactness after ADC, and exact reranking cannot recover an item absent from the shortlist. The missing learner construction is the consequential depth gap (P1-01).
- **F — Worked examples:** x=(1.4,1.7), c=(1,0) gives residual (.4,1.7), codeword (.5,2), reconstruction (1.5,2), squared reconstruction error .1. For q=(1.2,1.8), exact squared distance .05 versus reconstructed .13. Storage arithmetic agrees.
- **G — Code:** Training, assignment, lookup distances, eligibility and tombstones are visible. Existing tests and runner pass. Top-R refinement counts are logged, but its pre-refinement shortlist IDs/scores are not retained despite the chapter's diagnostic prescription (P1-03).
- **H — Lab:** Detailed hand residual/storage work, first-losing-stage diagnosis and add/delete probes require thinking. It calls/traces the supplied `IVFPQ`; it does not require the two-dimensional coarse cells and toy quantizer implementation promised by the syllabus.
- **I — Solutions:** Explain separate error gates, why approximate competitors can change rank, and payload versus real memory. Their negative replacement decision is evidence-backed.
- **J — Visuals:** Figure 16.02 clearly separates coarse coverage, recall, latency and theoretical storage. In Figure 16.01 the 38° query annotation is clipped at the right edge in PNG/PDF; repair plot limits/annotation placement (P2-05).
- **K — Experiments:** Two synthetic workloads, sixteen fixed queries each, fixed codebooks/seeds and one-variable probe/mode comparisons are explicit. At N=1024,d=32 all-probe Flat recall is 1, ADC .125, top-eight refinement .375. No confidence interval or production advantage is claimed.
- **L — Evaluation:** Reused V0 inspected qrels give exact judged recall .792, one-probe Flat .708, full-probe ADC .792 and refinement .875. The .875 is explicitly a small inspected-set accident, not validated improvement. Quality and geometric parity remain distinct.
- **M — Observability:** `measure` case records at line 57 contain query ID/exact IDs/modes, dropping Chapter 15's request ID. Search samples are warmed/repeated; `v0_case` encodes fourteen distinct queries once each, with no explicit untimed warm call. Its encoding median is a different sample population (P1-03, P2-08).
- **N — Security:** V0 training uses twelve already eligible support-team rows, excluding D10 before codebook learning. The chapter explicitly recognizes that shared training artifacts can leak protected data; it does not present static fixture checks as live ACLs.
- **O — Production connection:** Raw refinement copies, licensing/retention, stale codebooks, deletion/rebuild and replacement gates are substantive. Production migration remains Chapter 22's job.
- **P — Mastery gate:** Trace, error-localization and storage gates are supported. Independent construction and preserved correlated telemetry need correction before copying this authoring pattern into graph ANN.

## Cross-chapter dependency audit

### Dependency-violation table

This table separates actual prerequisite gaps from appropriate local introductions.

| Use / location | Prerequisite actually supplied | Observed issue | Audit judgment / action |
|---|---|---|---|
| 04, “What attention can and cannot do”: matrix attention/transpose | 03 gives scalar vectors/dot/norm; 04 itself works logits [0,ln(3)] through softmax | Full matrix shapes are not taught, but the equation is explicitly intuitive and the scalar gate is covered | Formal-shape improvement, not a failed stated gate. A local dimensions/weighted-value example is optional. |
| 11, “How a training signal shapes the space”: exp, ln, row sum and temperature | 04 works normalized exponential weights; 11 works [.8808,.8808] and .1269 loss | Arithmetic prerequisite is actually supplied | No fundamental softmax/loss coverage violation. Preserve these worked examples. |
| 11 lab / `contrastive_math.py`: stable subtract-max loss | Worked row simplifies exponentials by a common factor | General connection to code's max shift/log-sum-exp could be made explicit | Small implementation bridge within P1-02; not an assertion that loss arithmetic is absent. |
| 12 adaptation / `train_adapter`: A/B shapes, transpose, autodiff, Adam, gradient step | 10 supplies vector operations; 11 computes loss, not parameter updates | Loss-to-update mechanism is assumed at its first implemented training use | P1-02: compact parameter/gradient/update example; distinguish optimizer convenience from mechanism. |
| 07 tuning deferred to 09 | 09 does teach qrels/metrics | Dependency deferral is reasonable, but promised downstream activity never arrives | Unresolved teaching dependency, P1-04; do not tune on an inspected test set. |
| 12 train D1/D2, validation D3 | 03 §6 conditionally groups families for unseen-agreement transfer; solution 12 says keep all revisions together | IDs are disjoint while an agreement family crosses train/validation; text does acknowledge related-wording limits | Fixture/solution and generalization-unit mismatch, P1-06. Explicit family policy or a clearly bounded known-corpus record-holdout task. Current result is not proven invalid. |
| 08 heap | Introduced locally before WAND use | No violation found | Correct local prerequisite handling. |
| 09 metrics and qrels | Qrels/rubric precede metric calculations | No violation found | Correct ordering; corpus scoring examples before 09 do not pretend to be judged metrics. |
| 15 ANN / 16 quantization | Exact scan/metric relationship taught in 10 and reused in 13 | No ANN-before-exact violation found | Strong dependency chain. |
| Planned 17 graph traversal | Syllabus explicitly says graph vocabulary is introduced locally | Graph vocabulary is not yet taught | Not a missing prerequisite in 01–16. Require local graph/queue explanation in 17 as planned. |
| Planned 18 database service vocabulary | 03 gives memory/disk/lookup basics, not replication/durability semantics | “Database vocabulary from Chapter 03” is a thin prerequisite description | Introduce namespace/transaction/durability/consistency locally in 18 before comparison; do not retroactively turn 03 into a database course. |

No evidence was found of ranking metrics secretly requiring future qrels, ANN appearing before exact KNN, or an index structure used as a black box before Chapter 05 explains it. The dominant violations are mathematical granularity and unresolved deferred capabilities.

### Failure-first chain

| Chapter / mechanism | Failure actually exposed | Next capability motivated | Continuity judgment |
|---|---|---|---|
| 01: manually selected current evidence | Model cannot know private/new amendment; old source can mislead | Execute an evidence path in 02 | Strong and necessary. |
| 02: overlap loop, crude windows, bounded context | Split clause, wrong first candidate, missing comparison evidence | Cost/measurement discipline in 03; context limits in 04; index/rank improvements in 05+ | Strong; prerequisites solve observed questions rather than interrupting arbitrarily. |
| 03: scan/map and cost models | Big-O or an ID speedup alone does not measure IR quality | Controlled measurement throughout; context units in 04 | Legitimate prerequisite chapter, not a new retrieval feature. |
| 04: supplied prompt/evidence | Visibility, conflict and instruction boundaries still block support | Separate evidence selection/quality from generation | Strong conceptual bridge. |
| 05: positional inverted index | Fast literal match still treats different term evidence crudely | Weighted terms in 06 | Strong. |
| 06: TF-IDF | Repetition/length choices change rankings; lexical mismatch remains | BM25 in 07; learned representations later | Strong. |
| 07: BM25 | Accurate scores do not ensure efficient execution or judged evidence | Safe pruning in 08; judgments in 09 | Strong; the tune objective remains deferred debt. |
| 08: exact WAND | Fewer full scores can still cost more CPU; exactness is not relevance | Evaluate actual ranking in 09 | Particularly good separation of correctness, work and quality. |
| 09: judged lexical ranking | More sophisticated ranking may lose; paraphrases remain hard | Exact vector representations in 10 and learned encoder in 11 | Strong. |
| 10: exact binary lexical vectors | Geometry is exact but not intrinsically semantic | Learned encoder/training objective in 11 | Strong negative result. |
| 11: frozen encoder | Paraphrase gains coexist with ID/Basic-Pro/no-evidence failures | Adaptation experiment in 12; operational index in 13 | Adaptation is motivated; does not promise every ID failure is trainable. |
| 12: query adapter | Training loss improves while validation collapses; selected adapter gains nothing on test | Retain frozen baseline; materialize it in 13 | Strong scientific transition, despite missing update bridge. |
| 13: persisted exact dense | Encoding/search cost and pooled representation/source-route failures remain | Alternative representations in 14; approximation costs in 15 | Strong; different failures motivate different branches. |
| 14: sparse/MaxSim operator sandbox | Expansion can be wrong; pooled vector can lose token detail; storage/cost rises | Index/cost decisions in Part IV and later staged ranking | Useful branch, not a fake prerequisite for all ANN. Part III synthesis is missing. |
| 15: KD/LSH | High dimensions erase KD savings; LSH misses candidates and may be slower | Partition/compression/refinement in 16 | Strong. |
| 16: IVF/PQ | Coarse misses, ADC rank loss and top-R limits; raw refinement removes nominal memory saving | Graph ANN frontier in 17 and service boundaries in 18 | Strong; the new graph is a motivated alternative, not assumed universally better. |

## Terminology and conceptual continuity

### Duplication / drift table

| Concept | First definition | Later usage | Consistent? | Action |
|---|---|---|---|---|
| Information need / question | 01 §2: task versus its verbal message | 09 qrels, 13 stress slices, 15/16 failure diagnosis | Yes | Preserve task/authority/date distinctions when routing appears. |
| Corpus | Glossary: collection “eligible for a particular search task or snapshot” | V0/V3 index stores thirteen segments including D10; support-team eligible roster has twelve | Partly ambiguous | Name indexed corpus, eligible query corpus and candidate set separately (P2-03). Current code is clear about twelve versus thirteen. |
| Document / record | 01/02: stable source identity/version | 05 index ordinals represent segments; 09 judges indexed segments | Yes when unit is stated | Keep `retrieval_unit=indexed_segment`; avoid calling a segment score a document judgment without explanation. |
| Passage / chunk / segment | 01/02: derived searchable span; V0 uses segment IDs | 11 paper “passage” maps to indexed segment; 20 will teach richer chunking | Yes, declared synonyms at current granularity | Provide alias mapping rather than inventing different mechanisms. |
| Candidate / evidence | 01: returned item versus support accepted for a claim | 02 candidates/context/stub checks; 13 direct-context coverage; 16 candidate/context IDs | Yes | Continue preserving stage sets; fill refinement shortlist observability gap (P1-03). |
| Context / evidence | 02: selected prompt material may not support all claims | 04 support cards, 13 context direct recall, null generation | Yes | Do not relabel all selected context as verified evidence. |
| Relevance / similarity | 06 lexical score; 09 judged task relation | 10/11 geometric scores; 15/16 two recalls | Yes | Particularly strong distinction; keep raw scores uncalibrated. |
| Score / ranking | 02 deterministic overlap order | 07 BM25, 10 dot/cosine/negative distances, 14 MaxSim, 16 negative squared ADC distance | Yes, conventions explicit | Continue declaring score direction and tie rule. Numeric scores from these systems cannot be fused directly. |
| Retrieval / search | 01 retrieval includes external information access; 05 search yields candidates | Later local lexical/vector candidate generation | Compatible | Preserve retrieval's broader scope when SQL/tools arrive; no observed contradiction. |
| Grounding / faithfulness / correctness | 01/04 distinguish source support from world correctness | Later retrieval-only experiments leave answer labels null | Yes | Retain this distinction when full RAG metrics arrive in 30–33. |
| Recall | 09 judged relevant-item fraction | 15/16 exact-neighbor recall, oracle-list coverage and judged evidence recall | Yes, with qualifiers | Never publish an unqualified “recall” curve when multiple denominators are possible. |
| Index time / query time | 02 preparation versus request work | 05 postings, 13 persistence, 16 centroid/codebook training and assignment | Yes | Keep training/build/query stages distinct in graph and database chapters. |
| Zero-vector cosine | 06 matched zero-IDF vector gets declared score zero | 10 invalid cosine vector raises; wrappers can return explicit no-result | Different policies, explicitly named | Not a hidden math contradiction. Explain domain-specific policy rather than forcing one behavior on every stage. |
| Saturation | 07 bounded TF factor approaches k1+1 | 14 calls unbounded log1p “saturation” | Terminology can mislead | Explain sublinear compression versus finite asymptote (P2-02). SPLADE literature's terminology alone does not teach this distinction. |
| Hard negative | Glossary row taught in 11 with label-check requirement | Second same-name row taught in 12 with shorter definition | Duplicate, broadly compatible | Canonical entry with chapter-depth progression; retain checked-label caveat (P2-03). |
| InfoNCE / in-batch loss / temperature | Glossary contrastive entries in 11 | Additional overlapping entries near training terms in 12 | Compatible duplication | Merge/alias entries and keep one first-introduction/deep-treatment map (P2-03). |
| Request trace | 02 one correlated redacted execution | 13 pooled timings + case records; 14 examples; 15 request IDs; 16 drops them | Interface drift | Preserve a small common envelope without requiring distributed spans prematurely (P1-03). |
| Source-disjoint / held-out | 03 requires the split to match deployment: families for unseen agreements, or new questions over known corpus | 12 uses disjoint document IDs; D1/D2/D3 share family; solution 12 gives unconditional family-grouping advice | Document claim is valid but fixture/solution boundary is uneven | State intended generalization and audit family overlap; distinguish record holdout from family holdout (P1-06). |

Capitalization and IR abbreviations are generally consistent. Undefined-term risk is concentrated in matrix/optimization language, not a large uncontrolled vocabulary. Several architecture documents intentionally list future terms; these do not count as taught concepts. Paper names and product names are normally identified as such.

### Running-example continuity

The Helios Pro contractual change persists from manual evidence through V0, positional indexing, lexical ranking, judgments, encoder comparisons, materialization and ANN diagnosis. D4's split runbook instruction, D6's metadata-ID failure and D10's legal-only scope become reusable failure probes. This is genuine accumulation rather than sixteen unrelated blog examples.

Small new fixtures are usually justified: V1's ranking corpus isolates a DF-induced reversal; V2's length/pruning corpora isolate saturation and cursor skipping; Chapter 14's token vectors isolate pooling versus MaxSim. They are labeled separate tasks and return to the V0 baseline. Their creation is not evidence of an abandoned project.

The query sets do change. Chapter 09/10 use one fourteen-query judgment set; 11 uses seventeen new questions; 12 introduces training/validation/test labels; 13 adds fourteen stress questions; 15/16 reuse the latter. The book does not claim these headline metrics form a single improvement curve. Nevertheless, a maintained comparison ledger would make this constraint harder to forget when hybrid/reranking experiments arrive. Do not compare .899686 from 09 with .830781 from 11 as if only the retriever changed.

## Running project audit

### Project-evolution table

| Version / stage | New capability | Previous failure motivating it | Dataset continuity | Telemetry continuity | Reproducible? |
|---|---|---|---|---|---|
| V0 / 01–02 | Manual evidence → segmented overlap/context/stub engine | Missing/private/current evidence and ungrounded answers | Same ten fictional source documents; thirteen default segments | Full redacted request envelope established | Yes: source trace, engine, tests and outcomes executed. |
| V0 / 03 | Exact-ID characterization and measurement sidecar | Complexity/work/seconds and workload mixtures get confused | Synthetic ID task explicitly separate from IR corpus | Experiment provenance/raw samples, not a replacement request API | Yes; CPU timings vary. |
| V0 / 04 | Fixed prompt/context probes | Retrieved text can be invisible/conflicting/untrusted | Same source evidence; ten controlled prompt cases | Case IDs and null model outputs | Yes; no real model experiment claimed. |
| V1 / 05 | Positional inverted/forward index and Boolean/phrase retrieval | Repeated full-text scans and unordered term overlap | V0 retained; additional analyzer fixture | Request fields retained; analyzer/index/work added | Yes. |
| V1 / 06 | TF-IDF variants/field effects | Equal overlap ignores term rarity and frequency choices | V0 retained; rank-reversal toy declared | Weighting/statistics/version data retained | Yes. |
| V2 / 07 | BM25 | TF-IDF repetition/length behavior | Same V0 plus explicit length fixture | Scorer/parameter/work identity extends trace | Yes. |
| V2 / 08 | Exact WAND and postings codec | Exhaustively scoring matches costs work | Same scores/corpus; separate cursor fixture | Execution counters and rank parity retained | Yes, including independent randomized parity. |
| V2 / 09 | Judged retrieval harness | Scores/work do not establish relevance | Fourteen questions × twelve eligible segments, complete 168 pairs | Workload/window/quality/timing records added | Yes; content binding remains weak. |
| V3 / 10 | Exact vector oracle on binary lexical coordinates | Need metric/representation baseline before learned/ANN claims | Reuses 09 qrels and V0 IDs | Candidate/context/work retained; common facade not maintained | Yes. |
| V3 / 11 | Pinned frozen text encoder | Literal/binary geometry misses paraphrases | Same corpus; new 17-query/204-pair workload | Model versions and encode/scan timing, less consistent correlation | Yes, cached offline. |
| V3 / 12 | Gradient-trained query adapter, rejected as replacement | Domain adaptation may help or over-specialize | Same corpus; new document-split labels; family overlap disclosed but not enforced | Training/checkpoint provenance strong; no uniform request envelope | Yes; selected epoch/hash matched. |
| V3 / 13 | Checked materialized float32 exact index | Recompute cost and format/version mismatch | Same model/corpus/IDs; 34 parity checks; new 14-query stress qrels | Manifest excellent; request sample joins incomplete | Yes, including reload/corruption gates. |
| V3 / 14 | Manual sparse/MaxSim sandbox | Literal/pooled representations lose distinct evidence | Separate labeled fixtures; frozen exact baseline retained | Four illustrative trace records restore some fields | Yes; not a trained retrieval model. |
| V4 / 15 | Exact KD and approximate LSH | Full scan scaling; higher-dimensional pruning loss | Ch13 model/index/qrels retained; synthetic sizes/dimensions declared | V0 cases have request/query IDs, scores/context; timing joins incomplete | Yes. |
| V4 / 16 | IVF-Flat, residual PQ ADC, top-R refinement | Need separate probe/compression/memory trade-offs | Ch13 snapshot/qrels retained; seeded synthetic fixtures | Drops case request ID; no saved pre-refinement shortlist IDs | Yes; full-probe exact parity holds. |

**Observed:** later versions import/reuse the prior analyzer, corpus, context builder, BM25, judgments and dense snapshot rather than silently replacing them. V3's geometry has an `item_id` interface distinct from source `segment_id`; wrappers translate explicitly. V4 evolves the candidate-index layer, not the full answer service. The rejected adapter does not contaminate Chapter 13's frozen passage space.

**Audit judgment:** this is a coherent staged project, with intentionally bounded mechanism modules. It is not yet one uniformly callable end-to-end engine facade. That is acceptable at the candidate-index stage **provided** common request observability and comparison contracts survive. P1-03 concerns lost information, not a demand to rewrite all modules into a framework.

Keep the exact oracle, corpus/model identity and scoring tie rules stable while adding graph ANN. A version is not a new product merely because an experiment runner is new. Conversely, saving an experiment JSON is not enough to claim earlier telemetry has been preserved.

## Code and reproducibility audit

### Execution outcomes

| Suite | Tests | Result |
|---|---:|---|
| `projects/V0` | 17 | Pass |
| `projects/V1` | 17 | Pass |
| `projects/V2` | 21 | Pass |
| `projects/V3` | 22 | Pass |
| `projects/V4` | 9 | Pass |
| `tools/book` | 19 | Pass |
| **Total** | **105** | **No failures** |

All sixteen selected script entry points ran; the artifact-health appendix identifies them. Relevant tests check behavior rather than simply snapshotting prose: protected-source exclusion, split clauses/budgets, phrase positions, zero/missing terms, ties, WAND parity, malformed metrics, encoder masks, snapshot corruption and approximate-index error gates.

Additional probes used seed **1601**:

| Independent probe | Checks | Criterion | Result |
|---|---:|---|---|
| WAND versus direct BM25 | 600 | Forty generated small corpora, fifteen queries each; varied scopes, k1/b and k; ordered IDs and raw scores agree | Pass |
| KD versus full L2 scan | 90 | Generated finite vectors/queries; exact ranked IDs agree | Pass |
| Exact sort versus bounded heap | 360 | Dot/cosine/L1/L2; same eligible roster, depth and ties | Pass |
| IVF-Flat with all lists | 30 | Full-probe ordered top-k equals exact scan | Pass |
| IVF scope/delete gates | 60 | Returned IDs satisfy scope and exclude tombstones | Pass |
| **Total** | **1,140** | Empirical checks, not exhaustive proofs | **No failures** |

The audit compared **3,898 selected nested fields** in replayed Chapter 06–16 results with checked records: IDs, context IDs, quality metrics, work/summary fields, training history/selection and adapter identity where present. No differences occurred under the declared float tolerances. This was not an exhaustive byte comparison of every JSON field: timestamps/timings differ, and Chapter 14's automated comparison covered only two selected fields, supplemented by direct operator arithmetic and tests.

### Demonstrated integrity gap

In a disposable copy, the D1 clause was changed from four hours to nine hours while retaining source IDs and the snapshot string. The index was rebuilt and passed to `projects/V2/eval_ch09.py:load_judgments`. **The qrels were accepted.** The loader checks snapshot, eligible segment roster and label validity; it does not compare the text against a frozen corpus digest.

This probe is intentionally a violation of the fixture's intended version discipline. A robust validation gate should detect that violation. Recording a new corpus hash in the output is useful provenance, but it does not prove that existing judgments apply to the new content. The Chapter 11 loader has the same snapshot/roster pattern; Chapter 13 diagnostic loading delegates to it. Chapter 13's vector manifest already demonstrates how searchable-text identity can be validated. See P1-07.

### Code-quality judgment

The implementations are generally readable, deterministic where expected, and deliberately small enough to expose the mechanism. Finite/dimension checks, scope gates, tie rules, invalid parameters and corrupted-index errors are appropriate. Python object/payload costs are usually acknowledged rather than hidden behind a raw-byte formula.

No observed code defect invalidates the current experiments. This is not certification for unbounded numeric extremes, concurrent updates, untrusted service inputs or live authorization. Those are later system obligations. Existing exceptions teach rejection, but later runners lack a consistent redacted failure/status record on that rejection (P1-03).

The major reproducibility limitations are:

- Mutable reference-output defaults, most concretely Chapter 03 lab C.3 (P2-01).
- Model revision pinning is strong; a reproducible tested package environment is weaker. V3 setup installs libraries, while V0/V4 environment records mostly identify Python/platform rather than all numeric/runtime versions and thread settings (P2-07).
- CPU timings are reproducible as a protocol, not bit-identical numbers. No universal performance claim should be inferred from replay success.
- The adapter hash is retained but the rejected adapter is not a separately published weight artifact. This is a reasonable current boundary; if future accepted adaptations must be served, serialization/reload parity will be necessary.

## Experiment and measurement audit

### Experimental-science assessment

The first quarter is substantially teaching engineering science rather than anecdotal tinkering. Most checked experiment records include a question, hypothesis, baseline, controlled inputs, procedure, dataset/workload, metrics, raw results, failures, conclusion, decision and limitations. Negative outcomes are central: overlap can beat BM25 on this toy set; binary cosine loses; adapted loss falls while validation fails; high-dimensional KD and tiny-corpus ANN can be slower; all-probe PQ remains lossy.

The important caveats are not hidden: author-written judgments are not independent public benchmarks; two translated questions do not establish multilingual quality; model/corpus inspection creates selection bias; geometric recall is not judged relevance; no generation means no answer-quality result.

One experiment can have several declared variables, but controlled comparisons need pairwise interpretation. Chapter 16 holds trained centroids/codebooks fixed while changing nprobe or scoring mode. Comparisons across its two sizes/dimensions do not isolate size alone; the text does not claim they do.

| Experiment | Contract coverage | Main limitation / open issue |
|---|---|---|
| 01 manual source access | Task, evidence comparison, support outcome and boundary | Not an empirical model study; correctly scoped. |
| 02 depth/window/budget failures | Same source corpus, explicit changed mechanism and outcomes | Two-task stub, no general entailment evaluator. |
| 03 scan/map | Frozen seeded workload, baseline, controls, repeated raw samples, units and failure interpretation | Single-sample build timing; canonical output overwrite risk. |
| 04 prompt manifest | Fixed evidence, case variables and measured input sizes | No model outputs; setup/diagnosis rather than completed position-effect experiment. |
| 05–08 lexical mechanisms | Same baseline paths, isolated toys, exactness/work/time distinguished | Required independent lab implementations absent; BM25 judged fitting deferred. |
| 09 judged ranking | Fourteen queries, full 168-pair qrels, rubric/metrics/latency/error cases | Single author and no completed development/test parameter selection; no source-content validation. |
| 10 representation baseline | Same 09 qrels, exact cosine versus BM25 | Binary term coordinates, correctly not a learned-semantic test. |
| 11 frozen model | Pinned encoder, new 17-query/204-pair set, slices, raw timings and failures | Known fictional corpus; not an untouched workload. |
| 12 adaptation | Frozen base, train-only candidates/masks, validation selection, final test and negative outcome | Family overlap across train/validation; missing update derivation. |
| 13 materialization/stress | Manifest/parity, new slices, split costs and qrels | Fixed batch-size ordering; two queries per slice; pooled timing correlation. |
| 14 operators | Labeled manual inputs, complete tiny labels, exact operator comparison | No trained-model gain; cannot compare to 13's task/performance. |
| 15 KD/LSH | Exact oracle, fixed workload/seed, parameter comparisons and dual recall | One corpus/seed/local Python; no production recommendation. |
| 16 IVF/PQ | Frozen codebooks, probe/mode comparisons, oracle coverage, dual recall/storage and rejection gate | Same twelve V0 vectors train codebooks; inspected qrels; one training sample/seed. |

### Performance measurement

| Location | Timer / samples / warmup | Interpretation supported | What is not supported |
|---|---|---|---|
| V0 measurement sidecar / 03 | High-resolution counter; seven warmed, alternating trial batches of 256 seeded lookups per size | Median and variation of batch-average lookup cost; growth on this task | Per-request service p95; production speedup; precise build distribution from one sample |
| Lexical paired runners / 05–09 | Raw search samples and declared workload/window; plan parity/work tracked | Local implementation cost versus candidate correctness/relevance | Optimized search-engine throughput |
| 11 frozen encoder | Warm call per method/query/depth, seven randomized-order samples; 119 samples per method/depth | Query encoding + scan versus BM25, separate stage samples | Service tails or universal embedding latency |
| 12 adapter runner | Load/train/request timing separated; frozen inputs and selected checkpoint | Cost of this small query adaptation and local search | Full-transformer training cost or scalable adaptation benchmark |
| 13 batch encoding | Three trials for sizes 1/4/16 in fixed order | Exploratory local throughput; author explicitly names ordering confound | A robust optimal batch size |
| 13 requests | Warm encode/scan separated from load/build; raw arrays | Local stage distributions over declared query set | Slow-query-to-candidate diagnosis without joins |
| 14 operator sandbox | Thirty-one warmed scoring-only samples | Relative operator cost on manual tiny inputs | SPLADE/ColBERT system latency |
| 15 exact/KD/LSH | Warmed local search, repeated method comparison; encoding/build separated | Dimensional degradation and local work/time counterexamples | Universal asymptotic timing or independent-workload confidence interval |
| 16 search | Untimed warm call per method/query, two randomized-order passes; nearest-rank percentiles | Pedagogical search-only distribution on sixteen/fourteen fixed queries | Reliable service p95 or hardware-optimized PQ advantage |
| 16 query encoding | Fourteen distinct questions encoded once each after load; no explicit encoder warm call in `v0_case` | Median of those one-pass encode observations | Same warmed/repeated population as search; cold/warm encoder distribution |

**Observed:** no reviewed chapter presents one local run as a universal performance result. Timing captions generally state workload, units, boundary and limitations. Chapter 03 labels its build measurement one sample; Chapters 13/15/16 explicitly reject production sizing from the toy runs.

**Audit judgment:** performance discipline is strong for pedagogical measurements. P2-08 asks for clearer sample-population labels and stronger repeat/order protocols when a result is intended to select a configuration. It does not ask for large noisy benchmarks merely to make a foundations chapter look scientific.

Record CPU identity, numerical library/runtime versions, thread count and timed exclusions consistently (P2-07). Do not sum stage p95 values into a root p95. Distinguish service time, query encoding, search, build, model import/load and context/generation. Several later chapters already explain these distinctions better than their common trace interfaces implement them.

## Evaluation and observability audit

### Evaluation progression

| Stage | Evaluation capability present | Assessment |
|---|---|---|
| 01–04 | Human source/claim reasoning, deterministic stub evidence checks, null unrun model outcomes | Appropriate foundational progression. |
| 05–08 | Candidate behavior, exact score/rank parity, optimizer work and timing | Correctly does not label optimizer parity as relevance. |
| 09 | Complete eligible qrels, binary/graded metrics, cutoff/zero/incomplete policies | Strong and usable; add fitting exercise and content binding. |
| 10–13 | Same-task paired baselines, new declared query sets, sliced encoder/adaptation quality, selected context coverage | Strong; family holdout and metadata identity need enforcement. |
| 14 | Manual learned-operator fixtures, separate quality/cost | Honest operator demonstration. |
| 15–16 | Exact-neighbor recall, list coverage and judged evidence recall separately; context and unrun generation | Excellent distinction; add recorded intermediate shortlist for diagnosis. |
| Later contract | Context/generation/faithfulness/citation/abstention harness in 30–33 | Correctly deferred; no present penalty for absence. |

### Observability conformance

| Signal | V0–V2 | V3–V4 observed state | Required correction |
|---|---|---|---|
| Request ID / query ID | Correlated engine record | Query IDs common; 14 has trace examples; 15 has V0 request IDs; 16 drops them | Stable request/sample envelope, P1-03 |
| Source/index/model identity | Snapshot/analyzer/scorer versions | Strong corpus/model/code hashes and dense manifest | Carry identity on or unambiguously link each execution |
| Candidates/raw scores | Explicit engine trace | Generally retained per mode | Preserve metric/score direction; include pre-refinement top-R |
| Selected context / evidence | Distinct context and stub evidence IDs | Context IDs retained; new generation labels null | Continue distinguishing selection from verified support |
| Latency/stage timing | Root and stages together | Separate pooled arrays; no consistent join to cases | Key raw samples by request/query/mode/trial |
| Status / failure / reason | Stub and retrieval statuses/reasons | Successful experiment cases dominate; validation raises exceptions | Emit redacted failed execution record, preserving not-run/null stages |
| Privacy / redaction | No ordinary raw query/source text | Mostly IDs/hashes/work; judgments themselves contain controlled fictional text | Keep protected trace access distinct from datasets and aggregate labels |
| Index/codebook settings | Not yet applicable | nlist/nprobe/M/b, list IDs, work counters | Strong; attach shortlist and timing lineage |
| Ingestion events, distributed spans, cost ledger | Later obligation | Deliberately absent | Do not demand production completeness before 19+/30+/48+ |

The contract explicitly says Chapters 02 and 09–16 implement observability progressively. The project roadmap also requires retention of earlier telemetry. A rich experiment JSON may explain aggregate behavior while still failing to answer “which candidates belonged to this slow or failed request?” That is the concrete gap.

Security checks passed for the examined paths and additional scope/delete probes. Eligibility precedes context, and ordinary logs do not leak protected source text. KD's prefiltered roster and IVF's eligible training roster are trusted fixture assumptions; LSH's internal candidate filtering precedes similarity refinement. The manuscript states that a caller-supplied scope string is not authentication. No observed example promotes live authorization to a soft ranking factor.

## Mathematics audit

### Checked numerical and notation ledger

| Location / mechanism | Check | Result / limitation |
|---|---|---|
| 01 contractual change | (4−1)/4 | .75, correct; source-date interpretation is separate from arithmetic. |
| 03 average scan/log/amortization | 8.5 at N=16; log2(1024)=10; 120/29.8 rounded up | Correct. |
| 03 vector/statistics | Dot four / norms sqrt(5); five-value nearest-rank percentile | Cosine .8; mean seven/p95 twenty, correct. |
| 04 next-token probability | Product of two conditional example probabilities | .56, correct; conditional notation is terse. |
| 04 attention | Softmax((QKᵀ/sqrt(dk))+M)V; logits [0,ln(3)] | Matrix formula is correct/intuitive; scalar weights [.25,.75] are worked. Full matrix dimensions not taught. |
| 04 context budget | 4096−512−240−40−64 | 3240 available; 260-token overage, correct. |
| 06 TF-IDF | ln(N/df), sublinear TF, full-vector cosine | Correct declared convention, corpus reversal and edge policies. |
| 07 BM25 | IDF, TF factor, length normalization and limits | Correct; k1/b and field convention scoped. |
| 08 codec/WAND | Delta/variable bytes and safe bound/threshold trace | Correct under declared codec, nonnegative bounds and ties. |
| 09 metrics | AP, reciprocal rank, exponential DCG, ideal ranking and denominators | Checked worked values/policies agree; convention differences are named. |
| 10 geometry | L1/L2/dot/cosine; unit-vector squared L2 relation | Correct; normalization/ties matter. |
| 11 contrastive loss | Two rows with positive score margin two, tau=1 | .126928 versus constant ln(2), correct and worked; connect factor cancellation to stable code. |
| 12 adaptation | A/B dimensions and parameter storage | 12,288 floats, 49,152 bytes =48 KiB; text estimate incorrect. |
| 13 dense payload | 13×384×4; million-vector example | 19,968 bytes and 1.536 billion bytes≈1.43 GiB, correct; excludes metadata/model/replicas. |
| 14 MaxSim | Sum of per-query-token maxima | 2 versus sqrt(2), pooled order reverses; correct. log1p unboundedness needs explanation. |
| 15 ball/LSH | Lower bound 2−.5; (2/3)^4; 1−(1−16/81)^4 | 1.5; .19753; about .5864, correct. |
| 16 reconstruction/ADC | Residual/code/reconstructed query distance | .1 reconstruction error; .05 exact/.13 reconstructed squared distance, correct. |
| 16 theoretical memory | N=1024,d=32,M=8,b=2, IDs/centroids/codebooks/originals | Flat 138 KiB, PQ 12.5 KiB, PQ+originals 140.5 KiB, correct lower bounds. |

Notation is mostly local and consistent: N/d identify corpus size/dimension; k is result depth; k1/b are BM25 parameters; M/b acquire explicitly scoped PQ meanings rather than being globally constant symbols. Distances use squared versus unsquared units deliberately; Chapter 16 scores are negative squared L2 values, not calibrated confidence.

The book teaches ranking mathematics and small softmax/loss arithmetic rather than merely decorating prose with equations. The weaker boundary is the move from these scalar calculations to an actual trainable matrix projection. P1-02 should teach shapes and one loss-driven update, connecting existing probability calculations to stable code; it need not derive all attention heads or Adam internals. The update example is the highest-value mathematical remediation.

### Algorithmic quality

| Mechanism | Problem/input/store and build/query distinction | Steps, parameters, costs | Failure/debug/alternative | Missing dimension |
|---|---|---|---|---|
| V0 overlap/context | Sources → segments; question/scopes → candidate/context/stub | Explicit scan/top-k/budget and deterministic ties | Split clause, missing source, budget; index later | No core omission within toy scope. |
| Exact ID lookup | ID list/map and query ID | Linear versus average hash lookup; build/amortization | Miss mixture, collision/worst-case caveats | Precise real resident memory intentionally not benchmarked. |
| Positional index | Analyzer → postings/forward fields; query lists/positions | Boolean/phrase steps and posting work | Unicode/code loss, phrase membership mistake; different analyzers | Learner implementation missing, not reference mechanism. |
| TF-IDF | Scoped statistics/sparse vectors; query weights | Variants/norms and corpus-dependent weights | Zero/absent, corpus reversal, lexical mismatch | Learner implementation missing. |
| BM25 | Length/DF/avgdl at build; summed term contributions at query | k1/b/factors/work, explicit convention | Length/repetition/IDs; variants/QL | Judged fitting and complete learner scorer missing; term factor is practised. |
| WAND/codec | Encoded gaps and posting cursors; bound-driven exact query | Heap threshold, advance/seek, bounds and work | Unsafe bound/tie, overhead; exhaustive/MaxScore/BMW | Learner pruner missing; full BMW intentionally conceptual. |
| Exact vector KNN | Vectors/IDs/scopes; exhaustive eligible scores | O(Nd), sort/heap selection, batch matrix/memory | Zero/mismatch/ties; ANN later | Matrix shape worked detail too terse. |
| Frozen encoder/InfoNCE | Tokenized input, masks, pooled vectors; pair-score batch | Model roles/temperature and loss formula | False negatives/domain/prefix/IDs; lexical alternatives | Loss-to-update is deferred, but not fully delivered in 12. |
| Query adapter | Frozen passage/query embeddings and A/B parameters | Low-rank projection, masked loss, train/validate/test loop | Over-specialization, rejected gain; retain frozen | Gradient mechanism and family grouping. |
| Dense persistence | Manifest + float32 rows | Build/reload/validate, exact serving, hashes | Corruption/revision/source changes; rebuild | Atomic live migration intentionally later. |
| Sparse/MaxSim | Vocabulary weights or token vectors | Posting accumulation / query-token maxima; storage costs | False expansion, pooled loss, missing candidate | Learner implementation gate untested; trained/optimized index is intentionally not implemented. |
| KD/ball/LSH | Coordinates/boxes or random planes/buckets | Build/query/backtrack, collision/table/bit parameters | Dimension/empty buckets/approximation; exact | Formal space bound could be tighter; LSH learner build absent. |
| IVF/PQ | Coarse lists/residual subspace books/codes | Training, assign, probe, ADC, refine; cost/bytes | List miss, quantization rank, top-R, drift/delete | Learner build, hand centroid update and recorded top-R shortlist. |

No algorithm in this scope is judged complete merely because its acronym appears. The reference mechanisms generally have inputs, state, index/query steps, parameters, costs and failures. The incomplete dimensions cluster around neural updates, learner implementations, judged fitting and diagnostic state preservation.

## Visual-system audit

All twenty-three figures were inspected as rendered assets, not only source. The reader PDF was used to check scale/layout in addition to standalone PNGs/SVGs. Each figure has a substantive instructional purpose; no figure was identified as purely decorative.

### Visual health table

Paths are under `visuals/chapter-NN/`; figure labels match manuscript numbering.

| Figure | Purpose | Correct? | Readable? | Necessary? | Issue / assessment |
|---|---|---|---|---|---|
| 01.01 evidence paths | Separate model-only and evidence-backed answers | Yes | Yes at full-page size | Yes | Tall layout preserves the branches; reduced thumbnail would lose detail. |
| 02.01 preparation | Source/segment/index-time path | Yes | Yes | Yes | Clearly separated from request work. |
| 02.02 query sequence | Scope, candidates, context, stub and trace | Yes | Borderline in print | Yes | Landscape avoids worse shrinkage, but smallest text about 6.52 pt. |
| 03.01 ID lookup | Same-task scan/map growth and variation | Yes | Yes | Yes | Axes/units present; variation is in batch means, not request tails. |
| 04.01 autoregressive loop | Token feedback and next-token selection | Yes | Yes | Yes | Does not imply every model is the original encoder-decoder Transformer. |
| 04.02 prompt to claims | Visibility, instruction/data and support checks | Yes | Yes at full-page size | Yes | Caption explains the role of source support. |
| 05.01 documents to postings | Fields/positions/forward and inverted views | Yes | Yes | Yes | Strong structural teaching visual. |
| 05.02 scoped intersection | Eligibility before Boolean work | Yes | Yes | Yes | Prevents a ranking-first permission interpretation. |
| 06.01 sparse TF-IDF matrix | DF/IDF and rank reversal after corpus change | Yes | Yes | Yes | Annotated values illuminate the mechanism rather than just show a matrix. |
| 07.01 BM25 controls | TF asymptote and length parameter effects | Yes | Yes | Yes | Mathematical factor plots; not every TF/length combination is a realizable text. |
| 08.01 cursors/bounds/threshold | Safe advance and conceptual block bounds | Yes | Yes | Yes | Executable WAND versus conceptual BMW distinction is visible. |
| 09.01 ranked gain | Graded order/discount/ideal comparison | Yes | Generally | Yes | Small labels require zoom at reduced size; no metric error observed. |
| 10.01 metric geometry | Different metrics and stable tie rules | Yes | Yes | Yes | Tie ranking is explicitly ID-based; no false geometric distinction. |
| 11.01 encoders and batch | Separate towers and contrastive score rows | Yes | Yes | Yes | Declared positives and possible false negatives are labeled. |
| 12.01 training matrix | Reviewed positives and masked unsafe negatives | Yes | Yes | Yes | Excellent connection between labels and loss candidates. |
| 12.02 document split | Optimization/selection/test data boundaries | Yes for IDs | Yes | Yes | Does not establish family independence; revise if P1-06 changes grouping. |
| 13.01 dense flow | Build/startup/request compatibility and eligibility | Mostly | Yes | Yes | Startup verification appears in request arrow chain; eligibility is a rectangle rather than decision diamond. P2-05. |
| 13.02 score trace | Candidate diagnosis without comparing incompatible raw scores | Yes | Yes | Yes | Highlighted intended evidence is useful; separate score scales are clear. |
| 14.01 MaxSim grid | Per-query-token maxima versus pooling | Yes | Yes | Yes | Grid and selected maxima directly reproduce the score reversal. |
| 15.01 partitions/buckets | Exact KD pruning versus LSH candidate miss | Yes | Yes | Yes | Shared coordinates make candidate-set difference inspectable. |
| 15.02 latency/recall | Work/time and dimension/recall trade-offs | Yes | Yes | Yes | Honest low/high-dimensional contrast and local units. |
| 16.01 cells/codes | Coarse boundary miss and residual quantization | Yes | One clipped annotation | Yes | Right-edge 38° query annotation clipped in the rendered asset/PDF. P2-05. |
| 16.02 quality/cost | Coarse coverage, ADC/refine recall, search time and bytes | Yes | Yes, landscape | Yes | Packed lower bounds explicitly exclude resident-object costs; originals erase apparent savings. |

Figure numbering, referenced asset existence and order passed the current builder checks. Captions generally identify the takeaway, workload, units and limits, and assets have editable sources. The plot scripts regenerated all checked plot PNGs exactly in the audit environment.

The early Mermaid set shares shapes/colors and stage conventions. Later matplotlib diagrams/plots use coherent local conventions but do not follow every Mermaid shape rule; Figure 13.01 is the clearest small inconsistency. Color carries reinforcement, not the only semantic signal: labels, arrows and maxima remain present. The visual system is recognizable and functional, though not completely standardized.

Layout-dependent language was specifically considered. Left/right references to TF-IDF panels and coarse/PQ panels agree with the inspected renderings. No observed prose relies on a box orientation that has actually reversed. Asset-source duplication with inline Mermaid is maintainability risk, but current preflight/rendering did not reveal divergent definitions.

**Missing instructional visual worth prioritizing:** Chapter 12's loss/validation history and a minimal update-vector example. The chapter's strongest empirical lesson is loss falling while validation fails, yet its two figures teach labels/splits, not that trajectory or parameter movement. This is part of P1-02 if used to teach the missing update; a separate historical chart is optional. Do not add figures merely to increase visual count.

## References and research-quality audit

### Direct verification

The following primary/official sources were opened and compared with representative claims. These links are evidence, not an assertion that every listed paper was read in full.

| Source | Verified claim / scope | Outcome |
|---|---|---|
| [Lewis et al., Retrieval-Augmented Generation (2020)](https://arxiv.org/abs/2005.11401) | Original model combines parametric generation and nonparametric retrieval; specific architecture is not the whole modern category | Supports the appropriately scoped history in 01/04. Abstract/record checked, not every experimental table. |
| [Vaswani et al., Attention Is All You Need](https://arxiv.org/html/1706.03762) | Scaled dot-product attention, masking and original encoder-decoder architecture | Formula/history correct; does not repair the chapter's prerequisite gap. |
| [Manning et al., inverse document frequency](https://nlp.stanford.edu/IR-book/html/htmledition/inverse-document-frequency-1.html) | Document frequency and rarity weighting | Consistent with 06's declared variant and motivation. |
| [Manning et al., ranked retrieval evaluation](https://nlp.stanford.edu/IR-book/html/htmledition/evaluation-of-ranked-retrieval-results-1.html) | AP/MAP/ranked measures and assessment constraints | 09 conventions and denominators are defensible; DCG gain conventions must remain explicit. |
| [Lucene 10.4.0 BM25Similarity](https://lucene.apache.org/core/10_4_0/core/org/apache/lucene/search/similarities/BM25Similarity.html) | log1p IDF and documented default k1=1.2, b=.75 | Accurate implementation-specific support; defaults are not universal optimum parameters. |
| [IBM WAND publication record](https://research.ibm.com/publications/efficient-query-evaluation-using-a-two-level-retrieval-process) | Name/history of the two-level query evaluation work | Metadata/abstract support; full paper proof was not obtained. Algorithm audit additionally relies on source, calculation and parity checks. |
| [Pinned all-MiniLM-L6-v2 card](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2/blob/8b3219a92973c328a8e22fadcfa821b5dc75636a/README.md) | 384-dimensional sentence vectors, English card, 256-word-piece default, mean pooling/contrastive use, Apache-2.0 | Supports selected-model claims. Does not support arbitrary Matryoshka truncation or multilingual guarantees. |
| [Karpukhin et al., Dense Passage Retrieval](https://arxiv.org/abs/2004.04906) | Learned dual-encoder retrieval and empirical gains on specific QA workloads | Properly used for architecture/training motivation, not universal dense superiority. |
| [SPLADE v2](https://arxiv.org/html/2109.10086) | Original sum pooling versus later max pooling; vocabulary log1p(ReLU) weights | 14 accurately distinguishes variants. “Log-saturation” is literature terminology; explain unbounded log compression for this book's learners. |
| [ColBERT](https://arxiv.org/html/2004.12832) | Separate token representations, normalized token interaction/MaxSim, reranking and end-to-end retrieval roles | Operator/role claims are correct; manual fixture is not paper performance. |
| [Charikar, similarity estimation (original PDF)](https://www.cs.princeton.edu/courses/archive/spr04/cos598B/bib/CharikarEstim.pdf) | Random-hyperplane angular collision probability | Supports 15's 1−theta/pi and subsequent independent-bit/table calculation. |
| [Faiss official index-family documentation](https://github.com/facebookresearch/faiss/wiki/Faiss-indexes) | IVF-Flat/IVF-PQ categories, packed code/raw-vector memory formulas and scan/probe caveats | Supports 16's implementation-specific comparisons and payload accounting. |

The Robertson–Zaragoza BM25 PDF and product-quantization DOI/HAL route could not be fully fetched in this session: tool fetch errors and a bot challenge prevented inspection. Python's `time` documentation fetch also failed. These are **verification limits**, not findings that the repository's citations are false. BM25/PQ correctness was independently examined in the source/calculations and official implementation documentation; the full historical papers still deserve a later source review.

### Reference-health table

| Chapter | Citation coverage | Primary sources | Current claims verified | Concerns |
|---|---|---|---|---|
| 01 | Evidence-access/history and further reading present | RAG paper, foundational references | RAG architecture/history scope checked | Manual fictional evidence is not externally factual; no invented citation requirement. |
| 02 | IR/Python support and separate reading | Canonical IR material | Mechanisms/code checked locally | General Python support is not evidence that the stub is a general model; text respects this. |
| 03 | Data/measurement/IR sources | Canonical texts and official runtime documentation | Calculations/protocol checked locally | Remote timing-doc fetch failed; package/machine provenance could improve. |
| 04 | Transformer/LLM/context sources linked | Original Transformer and language-model research | Attention/original-architecture scope checked | Not every model-family/context research claim independently re-read; keep claim-specific hooks. |
| 05 | Canonical IR/analyzer reading | IR textbook | Postings/positions/analyzer checked locally | Vendor/analyzer options are examples, not one universal language-processing rule. |
| 06 | Canonical TF-IDF/vector sources | IR textbook | IDF source checked | Variants are correctly declared; preserve equation convention near citations. |
| 07 | BM25 paper + implementation documentation | Robertson/Zaragoza; Lucene for its specific convention | Lucene IDF/defaults checked | Full foundational PDF fetch unavailable; no unsupported universal defaults observed. |
| 08 | WAND/BMW and codec reading | Original query-evaluation research | IBM record/history checked; algorithm empirically verified | Full WAND paper not checked in session; source cannot substitute for its whole proof. |
| 09 | Evaluation definitions/readings | Canonical IR evaluation, original metric work | Ranked-evaluation source checked | Single-author assessment is disclosed; no assessor independence fabricated. |
| 10 | Geometry/exact search sources | Foundational mathematical/IR sources | Arithmetic/implementation checked locally | No learned-semantics claim to source; matrix vocabulary still needs teaching. |
| 11 | Encoder, DPR, model card, prefix-training research | Original papers and pinned model card | Model dimensions/pooling/revision boundary and DPR scope checked | Current selected-model claims have strong specific support. |
| 12 | Training/mining/distillation/benchmark reading | Original retriever research/benchmark maintainers | Local actual experiment; DPR scope sampled | Domain/language claims are limits/plans, not demonstrated transfer; full paper claims not exhaustively verified. |
| 13 | Model/index/diagnostic references | Model card and original retriever material | Pinned-model facts and persisted index checked | Spanish probes do not substantiate general multilingual quality. |
| 14 | Closely placed SPLADE/ColBERT citations | Original papers | Pooling variant and MaxSim roles checked directly | Duplicate PDF bibliography entries; clarify logarithmic “saturation.” |
| 15 | KD/ball/LSH and benchmark reading | Original LSH; foundational algorithms | Collision formula checked in original PDF | One-seed Python experiment is not sourced as universal complexity evidence. |
| 16 | PQ paper and official IVF/index reading | Original PQ citation; Faiss official docs | Family/storage/probe behavior checked | Full PQ paper fetch unavailable; manual/synthetic results stay scoped. |

`REFERENCES.md`, `PAPER_READING_PATH.md` and `FRONTIER_RESEARCH.md` separate foundational reading, engineering implementation and frontier work. No observed chapter treats a vendor product as the definition of RAG or a recent benchmark result as universal truth. Matryoshka requires explicit model training support; SPLADE/ColBERT are named model families; multilingual and adaptive claims are conditional.

Further reading is usually labeled separately from evidence for equations or model behavior. There is no demonstrated systematic citation laundering in the sampled claims. A broad further-reading list still does not support every nearby sentence; precise source hooks should accompany unusual historical/formula claims.

**Observed publication defect:** the rebuilt bibliography lists ColBERT twice and SPLADE v2 twice, with abs/html routes treated as distinct works. `tools/book/bookkit/biblio.py:canon_url` normalizes arXiv `abs|pdf` but not `html`. This is a concrete identity/deduplication gap, P2-04. The existence of 51 bibliography records should not be reported as 51 necessarily distinct research works.

The register's dates and pinned revisions are helpful. Time-sensitive product capacities/prices are not central to these chapters. Future service/product chapters should continue to pin documentation versions rather than import current marketing claims into stable theory.

## Labs, exercises and retention audit

### Exercise-difficulty map

This is a qualitative map of required tasks, not a count of every question. R=recall, E=explanation, N=numerical, C=independent coding, D=debugging, S=system/design choice, X=experiment, P=paper/research critique.

| Chapter | Dominant required types | Difficulty / capability progression | Gap |
|---|---|---|---|
| 01 | R/E/S | Justify knowledge route and source authority | Appropriate pre-code tasks. |
| 02 | C/D/E/X | Build all simple stages, log, create failures | Strong construction gate. |
| 03 | C/N/X/E | Independent lookup/benchmark, interpret variation | Strong; later math breadth exceeds this foundation. |
| 04 | E/D/S/N | Prompt/claim cards, budget, instruction/conflict diagnosis | No mandatory model experiment; correctly labeled. |
| 05 | N/D/E/X | Predict postings, analyzer failures, trace Boolean/phrase | Explicit promised C missing. |
| 06 | N/E/D/X | Derive reversal and change weighting choices | Explicit promised C missing. |
| 07 | N/C/E/X | Implement factor arithmetic and diagnose BM25 behavior | Coding covers factor, not full scorer; judged tuning missing after deferral. |
| 08 | N/D/E/X | Byte/cursor/bound prediction and broken optimizer | Explicit promised C missing. |
| 09 | N/C/E/S | Implement metrics, critique labels, Part II synthesis | Strong numerical/evaluation gate. |
| 10 | N/C/D/E | Implement exact top-k and metric/edge policies | Strong construction gate. |
| 11 | N/C/X/E/S | Pooling/loss implementation and pinned model slices | Relate worked exponential cancellation to stable implementation. |
| 12 | N/X/D/S/P | Audit labels, run real trainer, diagnose selection/transfer | Complexity grows, but update construction is hidden. |
| 13 | D/X/S/E | Build/reload, corruption/version probes, sliced diagnosis | Good operational challenge. |
| 14 | N/E/D/S/P | Sparse/MaxSim hand operators and model-role critique | Numerical syllabus task aligned; stronger implement gate and Part III synthesis untested. |
| 15 | N/D/X/S/E | Bounds/hash probabilities, dual-recall diagnosis, next design | Promised learner LSH C missing. |
| 16 | N/D/X/S/E | Residual/ADC/bytes and first-losing-stage/update diagnosis | Promised learner coarse/PQ C missing. |

Challenge increases in analysis and design. The learner moves from choosing a knowledge source to distinguishing training, representation, approximation, codebook, context and authorization failures. Debugging and numerical work are well represented. Independent algorithm construction is **not** increasing consistently with that challenge; it retreats to tracing supplied code in several advanced mechanisms. Full research reproduction is reasonably reserved for later stages; reading/claim critique already appears without pretending a toy operator replicates a paper.

### Solution quality

Solutions usually preserve reasoning: why one clause is authoritative, why a phrase needs positions, why TF-IDF reverses, why a WAND bound is safe, why an undefined denominator remains null, why loss reduction is not gain, and why ANN parity/quality are different. Alternatives and rejection decisions are acceptable where justified. This is much stronger than printing expected output.

The solutions are separately linked and the reader/workbook/solutions profiles respect that separation. Their existence is not a reason to make lab deliverables merely execute the solved mechanism. Add the explicit construction tasks and reasoning-based solutions in P1-01; assess behavior on unseen tiny cases so copying the reference output is insufficient.

### Retention system

Active-recall questions and “You understand this chapter if…” gates are present. Later chapters revisit old mechanisms: positional terms support sparse neural search; Chapter 09 qrels constrain dense experiments; exact geometry constrains ANN; the D10 permission fixture persists. Oral explanation and teach-back tasks are real, not only promised.

The contracts promise every part a cumulative quiz, architecture-from-memory sketch and comparison with the preceding engine. Chapter 09 implements an explicit Part II synthesis. Chapter 04 has chapter-level recall, drawing both figures from memory and revisiting dated sources, but not the full explicit Part I checkpoint. Chapter 14 has local operator questions and memory sketches but no full Part III synthesis of exact vectors, encoder objective, adaptation, materialization and their retained lexical baseline.

**Audit judgment:** retention is substantially implemented, but completed-part retention is uneven (P1-05). Repeated security caveats do not replace retrieval practice. Add two bounded checkpoint artifacts using existing sources/results; do not require new chapters or datasets. Part IV's checkpoint is not due until Chapter 18.

## PDF / publishing audit

This section is separate from manuscript quality. A readable PDF cannot establish algorithm mastery, and a near-empty page cannot invalidate correct retrieval code.

### Independent build results

`python -B -X utf8 tools/book/build_book.py --profile reader` completed successfully in the disposable copy. The current build produced:

- **241 pages**, with roman front matter and Arabic body page labels.
- **343 outline/bookmark entries** and **2,085 links**: 1,422 internal, 663 external.
- **26 embedded fonts**.
- **21 extraction checks**, all passing.
- **23 figures**: two full-page, eleven wide, five landscape and five normal placements.
- Five captioned tables in the list-of-tables metadata; other uncaptioned manuscript tables also exist.
- **51 bibliography records**, with duplicate-work issue described above.
- **Zero generated index entries** because no term-index markers are authored.
- **Zero build errors; eight warnings**: six near-empty pages plus code-wrapping warnings in the Chapter 13 lab and V3 README.

### Representative rendered pages

Physical PDF page numbers below count from the cover, to make the evidence reproducible regardless of printed page labels.

| Element | Physical page(s) inspected / mapped | Finding |
|---|---|---|
| Cover | 1 | Title, edition/version and author are clear; no clipping. |
| Contents / navigation | 3–4; bookmarks/link structures checked | Part/chapter navigation works structurally; destinations are present. No interactive viewer clicking was performed. |
| Part opener | 11 and Part IV boundary at 171 | Distinct hierarchy and coherent progression; appropriate intentional whitespace. |
| Chapter openers | 12, 141, 182 | Clear chapter titles; 12's long heading leaves “[INTERMEDIATE]” on a visually awkward separate line. Publication polish. |
| Source diagram / landscape sequence | Chapter 01 figure and 02.02 placement | Flow correct; landscape preserves lanes, but small labels remain demanding in print. |
| Plot | 03 growth plot; 143 training matrix; 183 cells/codes; 188 quality/cost | No axis/unit errors; 16.01 query label clipped; 16.02 landscape readable. |
| Equations | 58; 145 | Attention/budget and training expressions fit; no observed clipping. Chapter 12 byte/reference text errors remain source errors. |
| Tables | Training result page; glossary table at 221 | Header repetition/wrapping generally good; no observed unreadable table split. |
| Code / lab | V0 pseudocode and Chapter 13 lab | Monospace distinguishable; line-wrap warnings remain for long lab/README lines. |
| References | 230; source register at 234 | Readable and linked; duplicate ColBERT/SPLADE entries need deduplication. |
| Near-empty pages | 26 and 39 viewed; warnings also at 90,109,140,160 | 26 leaves one dangling sentence; 39 one further-reading bullet. These are avoidable pagination artifacts, not intentional part openers. |

Reader profile includes chapters/labs and project briefs, with solutions available separately. It does **not** dump every raw code file or every JSON record into the reader PDF. The 241-page count is substantial but does not establish an uncontrolled appendix explosion. Complete/author profiles intentionally serve different audiences; they were not rebuilt in this audit.

Running headers, margins and hierarchy were coherent in inspected pages. No blank-page storm, equation clipping or broken local figure placement was observed. Internal destinations were validated programmatically; external URL presence is not a guarantee that every remote page remains available.

P2-06 should address orphan pages, long code/heading wrapping, a populated reader index if the publication contract intends one, and refreshed distribution/provenance. The existing 198-page `dist` reader is stale relative to Chapter 16. It may be an ignored local artifact rather than a release; label it accordingly and rebuild only during authorized publication work. This audit deliberately did not replace it.

## Redundancy and information-density audit

### Healthy reinforcement

| Repeated concept | Locations | Why repetition is useful |
|---|---|---|
| Candidate is not verified evidence | 01 vocabulary; 02 context/stub; 04 claim support; 13/16 candidate/context results | Same distinction acquires a new operational consequence at each stage. |
| Eligibility before relevance/context | 02,05,07,10,13,15,16; D10 fixture | Inverted, vector, bucket and trained-codebook paths introduce different risks. Repetition prevents transfer errors. |
| Work is not latency | 03 cost models; 08 WAND; 15 KD; 16 ADC | Later measured counterexamples test earlier knowledge rather than merely restating it. |
| Score is not confidence | 06 weighting; 09 relevance; 11 cosine; 14 MaxSim; 16 ADC | Prevents conflating multiple new score spaces with task truth. |
| Missing candidate cannot be recovered later | 02 top-k/context; 14 rerank role; 15 buckets; 16 top-R | Same invariant is applied to different first-losing-stage mechanisms. |
| Preserve exact/judged baselines | 09–16 | Repeated experiment controls are necessary, not disposable boilerplate. |

### Unnecessary repetition / editorial opportunities

| Location | Observed overlap | Judgment / minimal action |
|---|---|---|
| `projects/V3/README.md` included as reader appendix | Detailed inventories restate model/qrel/candidate/timing limitations already taught in 11–14 | Useful repository navigation, but reader PDF repeats technical setup/claims. Consider a concise reader-specific inventory while retaining the detailed source README. P2-06, low priority. |
| V3/V4 chapter prose + lab opening + solutions + project brief | Multiple nearby statements that CPU timings vary, scope strings are not authentication and no generator is run | Local lab safeguards are justified. Repetition across consecutive reader sections can be shortened by a common fixture/measurement note plus mechanism-specific limits. Optional, not a reason to remove safety context. |
| Glossary training entries | Hard-negative/contrastive objective entries are duplicated rather than referenced | This is register duplication, not useful spaced recall. Canonicalize with aliases/deep-treatment chapters (P2-03). |
| PDF bibliography | Same ColBERT/SPLADE works represented twice | Unnecessary duplication demonstrably caused by URL identity normalization (P2-04). |

No pervasive evidence was found of chapters simply repeating a RAG introduction or saying the same mechanism twice in different words while avoiding substance. The shortest later chapters are dense with calculations, interfaces and results. The solution to current gaps is better decomposition and practice, not indiscriminate shortening. The reviewer does not recommend making the book terse for its own sake.

## Missing prerequisite explanations

| Current book says / location | Understanding silently assumed | Explanation needed | Where it belongs |
|---|---|---|---|
| 04 displays an explicitly intuitive matrix equation and works scalar softmax | Full matrix axes/transpose and value-weighted multiplication are not developed | Optional token-count/vector-width and weighted-value example; do not replace the existing valid [.25,.75] row | 04 local formal-fluency improvement; not a failed stated gate |
| 11 works exponential probabilities/log loss; `contrastive_math.py` uses max shift | Generalizing the worked common-factor cancellation to log-sum-exp stability | Connect the existing arithmetic to row-max cancellation and one large-score overflow example | 11 implementation bridge within P1-02 |
| 12 uses `u+B A u` and tensor transpose | Shape-compatible matrix multiplication and row/column orientation | Trace 2D toy A/B shapes and each intermediate output; relate to actual 16×384/384×16 arrays | 12 before adapter code; P1-02 |
| 12 calls backward/Adam step | Loss derivative, gradient sign and parameter update | One scalar/two-coordinate update, before/after score/loss; label autodiff as computing that derivative | 12 training-mechanism section; P1-02 |
| 07 says tune with later judgments | Development selection versus final evaluation | Frozen dev/test subsets, predeclared small k1/b grid, selection, single held-out report and failure slice | 09 follow-through task; P1-04 |
| 12 calls split source-disjoint | Record identity versus source family/revision leakage | Map D1/D2/D3 family, explain target generalization and enforce chosen grouping | 12 split fixture/diagram/test; P1-06 |
| 16 verbally describes Lloyd training then uses trained codebooks | Centroid update versus point assignment as distinct operations | One assignment/update iteration on a few 2D points; use it in learner-built cells/codebooks | 16 construction lab; P1-01 |
| Later experiments save IDs plus timing arrays | An experiment case versus a timed request execution | Sample identity/join example, not full distributed tracing | V3/V4 common envelope; P1-03 |
| 18 expects “database vocabulary from Chapter 03” | Durability, consistency, namespace, replication and transaction boundary | Define terms locally before comparing library/index/service | Chapter 18 as planned; no source expansion now required |

These are bounded explanations. They do not justify adding advanced probability theory, full optimization courses or later graph/storage systems to the first quarter.

### Missing-concept table

| Missing concept / capability | Expected chapter | Why important | Severity | Minimal fix |
|---|---|---|---|---|
| Independently implemented postings/phrase matcher | 05 lab | Learner must construct the core index, not only inspect it | P1-01 | Small builder and positional-phrase function with unseen tiny cases |
| Independently implemented TF-IDF scorer | 06 lab | Tests ability to translate declared formula/norm into code | P1-01 | Minimal scoped scorer and rank-reversal check |
| Complete independently implemented BM25 scorer | 07 lab | Existing independent term factor is useful but narrower than the full implementation task | P1-01 | Sum factor/IDF contributions under declared statistics and scope |
| Independently implemented toy safe pruner | 08 lab | Cursor/bound correctness cannot be established from supplied output alone | P1-01 | Small exact bound-pruning task and exhaustive parity |
| Judged BM25 parameter selection | 07→09 | “Calculate and tune” and later serious lexical baseline require a completed decision | P1-04 | Small fixed dev/held-out exercise; accept no gain |
| Matrix/update bridge | 12, with links from 10/11 | First-principles learning requires loss-to-parameter mechanics; softmax arithmetic already exists | P1-02 | Small shape/gradient/update example and stable-code connection |
| Source-family split enforcement | 12 | Earlier leakage discipline must survive actual adaptation | P1-06 | Family metadata/check or explicit narrower holdout objective |
| Independent toy LSH | 15 lab | Explicit syllabus implementation requirement | P1-01 | Seeded planes/signatures/bucket union and exact recall |
| Independent weighted sparse/MaxSim operators | 14 mastery gate | Numerical lab does not establish the stronger chapter implementation gate | P1-01 | Small posting accumulator and MaxSim function using existing fixture |
| Independent toy coarse/PQ mechanism | 16 lab | Explicit syllabus implementation requirement | P1-01 | 2D assignment/codebook/ADC functions and reconstruction check |
| Correlated retained request/shortlist trace | 13–16 | Actual slow/missed/failed execution diagnosis | P1-03 | Common envelope plus query/mode/trial sample keys |
| Completed Part I/III cumulative checkpoint | 04/14 | Contract's retention and cumulative architecture gates | P1-05 | Quiz, from-memory sketch, prior-version comparison |
| Content-bound judgments | 09/11/12/13 loaders | Prevent valid IDs masking changed evidence | P1-07 | Validated eligible text/scope digest bound to qrels |

## Preparation for Chapters 17–25

| Upcoming chapter | Readiness established | Debt / local teaching needed | Timing category |
|---|---|---|---|
| 17 HNSW | Exact oracle, metric/normalization, heaps, candidate misses, dual recall and retained dense snapshot | Teach graphs/visited/frontier locally as syllabus says; avoid copying trace-only implementation labs; preserve candidate-frontier trace | **FIX BEFORE END OF CURRENT PART**: P1-01/P1-03; graph terms are planned local content |
| 18 vector services/benchmarks | Build versus query costs, ANN trade-offs, model/index identity | Define database semantics locally; strengthen machine/thread/sample metadata before comparative benchmarks | **FIX BEFORE END OF CURRENT PART**: P1-03; P2-07/08 before credible selection benchmarks |
| 19 ingestion | Stable source/segment IDs, forward records, digests and provenance | Preserve source-family/permission lineage in heterogeneous extraction; teach formats/OCR locally | **CAN FIX LATER**, by 19: P1-06/07 |
| 20 chunking | Boundary failure, budget dilution, qrels, exact retrieval and model constraints | Bind judgments to changed spans/content; do not reuse obsolete segment labels without review | **FIX BEFORE completing next five chapters**: P1-07 |
| 21 metadata/filtered retrieval | Eligibility-before-scoring discipline; ID routing failures | Static string scopes are not live authorization; add filter/selectivity/empty-result experiments and failure traces | **FIX BEFORE completing next five chapters**: P1-03 |
| 22 freshness | Manifest/compatibility and toy tombstones | Version content and qrels together; teach durable events/alias/delete/rebuild rather than treating local delete as durable removal | **CAN FIX LATER**, before 22: P1-07 already should be complete |
| 23 query routing | Information need, exact-ID versus paraphrase failures, eligibility | Preserve original query/route and trust boundary; correlate routing with candidate traces | **CAN FIX LATER** after P1-03 |
| 24 reformulation | Encoder limitations, false expansion, declared qrels | Prevent inspected-set repeated tuning and reformulation leakage | **CAN FIX LATER** after P1-04/06 |
| 25 hybrid fusion | Lexical/dense/MaxSim score incompatibility and complementary failure slices | Use same frozen workload for paired fusion; learner must implement the formula rather than run a finished fusion script | **CAN FIX LATER** after P1-01/04 |

**BLOCKER BEFORE CHAPTER 16:** none identified retrospectively. Chapter 16's current runnable mechanisms are not invalid.

**FIX BEFORE END OF CURRENT PART:** establish the common trace/construction-task pattern and locally teach graph/database vocabulary before it is used. Fill the earlier math/tuning/retention gaps within the next five chapters so later authoring does not assume they were completed.

**OPTIONAL IMPROVEMENT:** a comparison ledger, hand centroid-update panel and learning-history figure can make already valid controls easier to inspect. They do not require additional production systems in the first quarter.

## Top 10 strengths

1. **Chapter 02 actually requires construction.** `labs/chapter-02/LAB.md` asks for the ten-document engine and structured record; `projects/V0/engine.py` independently runs. It meets the first-principles contract through an inspectable pipeline rather than a framework call.
2. **Evidence failure is concrete and cumulative.** Chapters 01–02 use the dated Helios clauses, D4's split instruction and context-budget losses. The same sources recur in lexical, dense and ANN diagnosis rather than disappearing after orientation.
3. **Chapter 03 prevents a plausible benchmark mistake.** Its “failure of the tempting interpretation” and `measurements.py` hold the exact-ID task fixed and separate build/work/seconds. An ID dictionary win is explicitly not proof of RAG improvement.
4. **Chapter 06 demonstrates corpus-dependent ranking.** Its sparse matrix and `toy_ranking_corpus.json` derive the before/after DF/IDF contributions and rank reversal. This goes substantially beyond “TF-IDF favors rare terms.”
5. **Chapter 07 teaches the BM25 factors.** §§1–3, Figure 07.01 and `bm25.py` expose IDF convention, saturation, average length, k1/b, parameter limits and a worked score before variants. This satisfies the mechanism-depth contract apart from completed tuning.
6. **Chapter 08 treats safe pruning as a correctness problem.** The P1→threshold→P6 cursor example, conservative ties and `wand.py` retain exact scores/ranks while separating skipped work from latency. All 600 additional parity cases agreed.
7. **Chapter 09 refuses convenient evaluation shortcuts.** `judgments_ch09.json` reviews all 168 eligible pairs; `eval_ch09.py` handles zero-positive and unjudged cases explicitly. The overlap baseline can beat BM25; the result is not concealed.
8. **Chapter 12 retains a scientifically useful failure.** Training loss improves while validation deteriorates, and the selected adapter does not improve the test baseline. `chapter-12-experiment.json` preserves history/selection and rejects deployment rather than selling training loss.
9. **Chapter 13 has a real compatibility gate.** `dense_snapshot.py` validates source text, model/input contract, metric, row scopes and bytes before serving. The 34 materialization parity cases and corruption tests make versioning operational.
10. **Chapters 15–16 separate failure denominators and costs.** Exact-neighbor recall, judged relevance, list coverage, approximate shortlist and raw-refinement storage are distinct. All-probe PQ's loss and the 140.5 KiB originals-retaining payload are shown even when they undermine the proposed optimization.

## Top 10 weaknesses

| # | Location | Observed problem | Why it matters | Severity / correction |
|---|---|---|---|---|
| 1 | Labs 05/06/08/15/16; partial coding in 07; stronger mastery gate in 14 | Explicit construction tasks become calculations/traces/reference runs, or assess a narrower function | Completion does not establish construction ability; this pattern would weaken later “expert” gates | P1-01: bounded independent mechanism functions and unseen checks |
| 2 | 12 adaptation/`train_adapter`, with vector/loss foundations in 10/11 | Actual matrix/gradient-update mechanism assumed; scalar probability arithmetic is taught | First-principles chain weakens at the first implemented parameter-training step | P1-02: small worked shape/gradient/update bridge |
| 3 | `experiment_ch13.py` case/timing split; `experiment_ch15.py` request IDs versus `experiment_ch16.py:measure`; `IVFPQ.search` refinement | Correlation fields regress and pre-refinement top-R IDs are not saved | Cannot reliably locate a slow/failed request or prove the first losing shortlist gate from its trace | P1-03: common envelope and intermediate stage IDs/scores |
| 4 | 07 “Debug and tune”; 07 lab deferral; 09 lab/harness | Judged tuning is promised later but never performed | Serious lexical baseline remains an unselected parameter choice; future comparisons can inherit the omission | P1-04: frozen development/held-out selection task |
| 5 | Completed Part I ends at 04; Part III ends at 14 | Chapter recall exists, but full promised cumulative part checkpoints do not | Learners can pass local tasks without reconstructing the accumulated architecture | P1-05: two cumulative quiz/sketch/comparison checkpoints |
| 6 | `judgments_ch12.json:document_split`; `load_split`; solution 12's grouping advice; 03 §6 | Helios D1/D2/D3 crosses train/validation while the solution says keep revisions together; limitations acknowledge related wording | Valid document-ID holdout can be mistaken for stronger family transfer; instructional advice and fixture should agree | P1-06: group families or explicitly narrow/audit the holdout task |
| 7 | `eval_ch09.py:load_judgments`; related V3 loaders | Same IDs/snapshot with changed source text still accepts qrels | Upcoming chunk/update experiments can evaluate obsolete labels without noticing | P1-07: validated content/scope digest |
| 8 | `labs/chapter-03/LAB.md` C.3; `measurements.py:DEFAULT_OUTPUT` | Default command overwrites frozen reference measurement JSON | Running a lab can change canonical plots while chapter tables still describe the old run | P2-01: local outputs and explicit reference/regeneration distinction |
| 9 | `tools/book/bookkit/biblio.py:canon_url`; PDF bibliography p230 | arXiv abs/html routes duplicate ColBERT/SPLADE works | Citations become harder to maintain and apparent source counts inflate | P2-04: canonical paper identity across routes |
| 10 | Figure 16.01, Figure 13.01; PDF p26/39 and wrap warnings | One clipped query label, startup-flow ambiguity, orphan content and long wrapped lines | Reader loses visual/detail clarity; publication defects are independently visible | P2-05/06: asset/layout corrections and rebuilt-page verification |

These are observations plus review judgments; none imply the existing WAND, KD or IVF-Flat algorithms failed. Several weaker aspects, such as one-pass encoder timing and glossary aliases, are documented in the P2 plan rather than artificially promoted into blockers.

## Risks if current generation pattern continues

| # | Supported current pattern | Longitudinal risk | Preventive action |
|---|---|---|---|
| 1 | Five labs replace explicit construction with tracing a supplied implementation | Advanced chapters become demonstrations learners cannot recreate | P1-01: capability-specific learner artifacts |
| 2 | Correct neural formulas and worked scalar losses precede missing shape/update decomposition | Ranker, adaptive-policy and multimodal training chapters silently rely on untaught parameter-update mathematics | P1-02: close the existing bridge before adding more notation |
| 3 | V0 telemetry is richer as one request record than later pooled experiment records | Multi-source/fan-out systems have plentiful logs but no causal diagnosis | P1-03: retain sample/request/stage lineage |
| 4 | BM25 fitting deferred from 07 never lands in 09 | Future dense/hybrid “gains” compare against an inadequately selected baseline | P1-04: complete baseline selection with held-out limits |
| 5 | Document-disjoint split is called source-disjoint while agreement families overlap | Later adaptations/teacher-generated data inherit misleading independence claims | P1-06: grouping contract tied to intended generalization |
| 6 | Qrels rely on snapshot strings and roster IDs | Chunking, edits and incremental indexing silently invalidate labels | P1-07: bind reviewed content and scope to judgments |
| 7 | Completed Parts I/III lack promised cumulative checkpoints | Local mastery accumulates without architecture retention or cross-version reasoning | P1-05: enforce part-level artifacts |
| 8 | Different qrel workloads introduce new headline scores at each V3 stage | Later readers or summaries turn non-comparable metrics into an improvement narrative | Preserve workload ledger and same-set paired comparisons |
| 9 | Canonical-output defaults, unpinned package setup and heterogeneous timing samples | Reference figures/results drift during normal learner runs; replay is mistaken for numeric benchmark equality | P2-01/07/08: local output, environment/sample metadata |
| 10 | Bibliographic URL identity and pagination already produce duplicates/orphan pages | Growing source registers and reader appendices become harder to navigate and maintain | P2-03/04/06: canonical registers and recurring rendered QA |

No unsupported prediction of a multi-thousand-page book or universal performance failure is made. These risks follow specific observed patterns; they are not generic objections to AI-assisted authoring.

## P0 / P1 / P2 remediation plan

**Do not apply these changes as part of this audit.** The following is a reviewable work inventory. IDs are unique, and the totals are **P0: 0; P1: 7; P2: 8**.

### P0 — Before Chapter 17

**None.** No evidence warrants declaring the present technical baseline unusable or requiring structural revision. Exactness, current data consistency, executable experiments and eligibility gates held up. The targeted fixes below matter, but are not a demand to restart the book.

### P1 — Before completing the next five chapters

| ID | Files affected | What must change | Why | How to verify |
|---|---|---|---|---|
| **P1-01** | Labs/solutions 05/06/07/08/14/15/16; chapter mastery wording if needed | Require small independently written postings/phrase, TF-IDF, complete BM25 sum, safe bound pruner, weighted sparse/MaxSim, random-hyperplane LSH and coarse/PQ functions. Preserve current calculation/diagnosis tasks. Do not require wholesale duplicate engines. | Explicit syllabus construction outcomes or the stronger Chapter 14 gate are not tested by executing reference code; Chapter 07 coding covers only its term factor. | Learner implementation passes unseen tiny fixtures, exact parity where promised and lossy-recall checks where appropriate; learner explains the first failure without inspecting the reference implementation. Solutions explain steps/alternatives, not only code/output. |
| **P1-02** | Chapter 12 and its lab/solutions; Chapters 10/11 bridge links and stable-loss explanation; optional formal-shape example in 04 | Add bounded shape/transpose and loss→gradient→parameter-update examples. Connect existing softmax/loss arithmetic to subtract-max implementation. Preserve the valid worked examples in 04/11. | The self-contained chain currently jumps from scalar geometry/loss to actual matrix/autodiff training. | A reader knowing only preceding chapters can state each adapter intermediate's dimension, show stability cancellation, and perform one update that changes score/loss. Check arithmetic and derivative against finite differences. Optional attention dimensions remain separately labeled. |
| **P1-03** | V3 experiment runners 10–14; V4 runners 15–16; `projects/V4/ivf_pq_ch16.py` diagnostics; affected labs/briefs | Define/preserve a minimal request/sample envelope: request/query/mode/trial IDs, linked versions, root/timed-stage boundary, raw candidate and context IDs/scores, status/reason. Save approximate top-R before refinement. Emit redacted failure records. | Later records lose V0 correlation and cannot identify the first losing or slow execution stage. | Every timed sample joins one query/mode/trial; Chapter 16 retains request IDs; a known top-R miss is explained from saved IDs; invalid input yields a redacted failure/status record; D10/raw private content stays absent from ordinary logs. No need for full distributed tracing yet. |
| **P1-04** | Chapters 07/09; labs/solutions 07/09; `projects/V2/experiment_ch09.py` or a bounded fitting sidecar; declared judgments/fixture | Complete the promised BM25 tuning exercise with a small fixed parameter grid, development selection, fresh/explicit held-out judgments and one final comparison. Keep existing inspected cases as diagnostics, not newly “unseen” test data. | Later retrieval comparisons need a defensibly selected lexical baseline and actual fitting skill. | Selection uses development labels only; scorer/analyzer/workload identity is recorded; final test is not used to choose settings; report slices, costs and no gain if that is the result. Existing current baseline results remain distinguishable. |
| **P1-05** | Chapter 04/14 practice sections or labs; solutions 04/14; part-completion authoring review criteria | Add explicit completed-Part I/III cumulative quiz, architecture-from-memory sketch and comparison with the preceding engine capability. Reuse current artifacts. | Contracts promise part-level retention; chapter recall alone does not establish accumulated architecture knowledge. | A learner reconstructs source→candidate→context→claim boundaries for Part I and V2→V3 index/train/query/evaluation boundaries for Part III without viewing diagrams; answers cite failure evidence and retained baseline. |
| **P1-06** | `projects/V3/judgments_ch12.json`, `experiment_ch12.py:load_split`, split tests, Chapter 12/lab/solutions, Figure 12.02 if grouping changes | Define intended holdout/generalization unit. For unseen-family transfer, group families; for known-corpus new-query/record evaluation, explicitly teach that narrower task and audit family overlap. Align solution 12's “keep all revisions” advice with the actual fixture. | Train D1/D2 and validation D3 share a Helios agreement family. Document-disjoint is accurate, but weaker than the solution's advice; related-wording limitations are already acknowledged. | Explicit family map detects overlap. Family-held-out claims require disjoint families. If data change, rerun selection/results. If task stays narrow, wording/diagram/solution agree and no family-transfer gain is claimed. |
| **P1-07** | `projects/V2/judgments_ch09.json`, `eval_ch09.py`; V3 judgments/loaders 11–13 and split validation 12; applicable tests/briefs | Bind judgments to a normalized eligible source-text/locator/scope digest or immutable manifest and validate it, in addition to IDs/snapshot strings. Require review/reversion of labels when evidence changes. | Current loader accepts changed content under old IDs; chunking and updates will compound this hazard. | Same-ID/snapshot four→nine-hour probe is rejected. Whitespace policy is explicit. Scope/source changes fail validation. Unchanged data replay passes, and future chunk/update experiments record the applicable judgment version. |

Prioritize P1-01/02/03 while preparing Chapter 17: they affect how the next mechanism will be taught and traced. The other P1 items should be closed no later than Chapter 21, with content binding in place before any changed-chunk workload is evaluated.

### P2 — Before publication

| ID | Files affected | What must change | Why | How to verify |
|---|---|---|---|---|
| **P2-01** | `projects/V0/measurements.py`, `labs/chapter-03/LAB.md`; review analogous V1/V2 runner defaults/plot instructions | Use local output defaults or explicit local `--output`; separate reference-record regeneration from learner replay. | Normal Chapter 03 run overwrites frozen measurement data and can desynchronize plots/prose. | Execute documented learner commands in a copy; canonical checked JSON/figures remain byte-identical unless an explicitly designated regeneration command runs. |
| **P2-02** | Chapter 12 lines 63/69; Chapter 14 line 29; corresponding solutions/briefs where repeated | Correct 49 KiB→48 KiB; Chapter 41 experiment-design pointer→48; distinguish unbounded log compression from bounded BM25 saturation. | Small factual/navigation imprecision undermines otherwise careful mechanisms. | Recompute 12,288×4/1024; compare target syllabus heading; show log1p increasing without finite ceiling and BM25 TF approaching k1+1. |
| **P2-03** | `GLOSSARY.md`; affected terminology links / first-introduction map | Canonicalize duplicate hard-negative/InfoNCE entries with aliases/depth chapters. Clarify indexed corpus versus query-eligible corpus. | Register duplication and corpus wording can become semantic drift. | One canonical entry per concept/alias; twelve-eligible/thirteen-indexed examples remain unambiguous; chapter-first-use/deep-treatment references agree. |
| **P2-04** | `tools/book/bookkit/biblio.py`, `test_bookkit.py`, `REFERENCES.md` identities where needed | Normalize arXiv abs/pdf/html/version routes to one paper identity; retain precise implementation/source hooks and retrieval metadata. | Rebuilt bibliography duplicates ColBERT and SPLADE v2. | Abs/html/pdf variants resolve to one work; current reader bibliography lists each once; in-text links/citations still resolve. |
| **P2-05** | Chapter 13/16 plot sources and generated SVG/PNG; wide Mermaid placement if necessary; affected captions | Reposition unclipped 38° query annotation; clarify startup verification and decision shapes in dense flow; improve minimum print labels where practical. | Rendered defects/convention ambiguity are real, although not technical blockers. | Inspect standalone SVG/PNG and actual reader pages at intended scale; all labels fit; startup/request arrows and eligibility convention agree with caption/prose. |
| **P2-06** | `tools/book/book.css`, applicable layout rules in `tools/book/bookkit/`, title/code formatting; reader-specific project appendix selection; distribution procedure | Fix orphan sentence/bullet pages and wrapping warnings; improve long title placement; decide/index reader terms if required; publish a current, correctly provenanced reader build. Consider reducing repeated README inventories in reader profile only. | Independent PDF QA found pagination defects and a stale existing distribution; the current build is otherwise sound. | Rebuild all intended release profiles; inspect p26/39-equivalent boundaries, long code/titles, figures, tables and references; extraction/destination checks pass; distribution includes 16 chapters with current provenance. |
| **P2-07** | V3 setup in `README.md`; project environment metadata; optional tested dependency manifest | Document a tested package environment and model-cache procedure; record numeric library versions, CPU and thread settings consistently. | Pinned model bytes do not fully pin inference/training/plot behavior or timing. | Fresh expected environment runs the selected tests/experiments offline after one intentional cache setup; record versions/threads; deterministic outputs agree within declared tolerances. No large dependencies added merely for audit. |
| **P2-08** | V0 measurement notes; V3 batch/request measurement notes; `projects/V4/experiment_ch16.py` and Chapter 16 timing prose | Label one-pass encoder median separately from warmed repeated search; keep single-build and fixed-order batch limitations explicit. For configuration-selection benchmarks, add suitable warm/cold repeats/order randomization and sample metadata. | Timing populations differ; novice readers can overinterpret a shared p50/p95 vocabulary. | Record sample count/queries/repeats/warmup/timer/boundary for each reported distribution; no service-tail claim from tiny reused queries; expanded protocol only where the decision requires it. |

Optional items such as broader space-complexity tables and extra learning-history plots are not additional P1/P2 findings. They should be added only when they materially improve the specific mechanism.

## Appendix: artifact health tables

### Code / experiment health table

“Reproducible” refers to deterministic mechanism/results under the recorded inputs, not identical CPU latency. All executions below occurred in the disposable copy.

| Artifact | Runs? | Reproducible? | Result checked? | Main concern |
|---|---|---|---|---|
| `labs/chapter-01/source_trace.py` | Yes | Yes, manual source choices | Locator/scope behavior inspected | Does not semantically certify claims; correctly human-reviewed. |
| `projects/V0/engine.py` | Yes | Yes | Stub outcomes/context/security and tests | Two-task generator, intentionally limited. |
| `projects/V0/measurements.py` | Yes | Protocol/seed yes; timings vary | Balanced/all-miss records and calculations | Canonical default output; single build sample. |
| `projects/V0/context_probes.py` | Yes | Yes | Case manifest/input sizes/null outputs | No model behavior measured. |
| `projects/V1/experiment.py` | Yes | Yes | Index/phrase/scope results and tests | Lab does not independently build index. |
| `projects/V1/experiment_ch06.py` | Yes | Yes | Rank/statistic/contribution fields | Learner scorer task absent. |
| `projects/V2/experiment_ch07.py` | Yes | Yes | BM25 factors/rank/work | Tuning not completed. |
| `projects/V2/experiment_ch08.py` | Yes | Yes | WAND/direct parity, codec, cursor/work | Reference-only lab pruner. |
| `projects/V2/experiment_ch09.py` | Yes | Yes for current fixture | Qrel metrics/denominators/timings | Judgment content binding absent. |
| `projects/V3/experiment_ch10.py` | Yes | Yes | Binary-coordinate rankings/work/qrels | Not learned semantics; correctly labeled. |
| `projects/V3/experiment_ch11.py` | Yes, cached offline | Yes in tested environment | Pinned embeddings/ranks/slices; tests | Package environment and sample joins. |
| `projects/V3/experiment_ch12.py` | Yes, cached offline | Yes: epoch/hash matched | Training history, selection and test | Family overlap and update pedagogy. |
| `projects/V3/experiment_ch13.py` | Yes, cached offline | Yes | 34 parity cases, stress outcomes/build | Fixed-order throughput and timing correlation. |
| `projects/V3/experiment_ch14.py` | Yes | Yes | Manual operators/grid, tests and limited automated comparison | Not trained model or comparable workload. |
| `projects/V4/experiment_ch15.py` | Yes, cached offline | Yes | KD parity, LSH misses, dual recall | Learner LSH build and correlated timings. |
| `projects/V4/experiment_ch16.py` | Yes, cached offline | Yes | IVF/PQ/bytes/dual recall; tests/probes | Lost request ID/top-R trace; one-pass encode distribution. |
| V0/V1/V2/V3/V4 test suites | Yes | Yes | 17/17/21/22/9 tests pass | Not exhaustive service/concurrency certification. |
| `projects/V3/index_ch13/manifest.json` + `vectors.f32` | Loads | Yes | Bytes/model/text/scope/unit/parity gates | Local index, not durable multiwriter store. |
| V1/V2 toy JSON corpora | Loaded | Yes | Used in hand calculations and runners | Must remain labeled mechanism fixtures. |
| V2/V3 judgment JSON files | Loaded | Current IDs/labels yes | Reviewed roster/grades and arithmetic | Add content identity/family grouping safeguards. |
| Sixteen `visuals/chapter-NN/plot-*.py` programs | Yes | Yes in tested plotting environment | Regenerated PNG hashes matched | Local replay should not accidentally redefine reference timings. |
| Seven Mermaid sources and 23 rendered figure pairs | Book rendering passed | Current assets consistent with inspected source/prose | All PNGs inspected; SVG destinations/build checked | Not every Mermaid SVG regenerated bit-for-bit. |
| `tools/book` tests and reader build | Yes | Content/layout pipeline reproducible | 19 tests, extraction/link/font/render checks | Publication warnings/duplicates/stale dist remain. |

### Workload / comparison ledger

| Material | Questions / judgments | Valid comparisons | Invalid inference to avoid |
|---|---|---|---|
| V0 two-task answer fixture | Two deliberately supported task families | Boundary changes within V0 | General LLM correctness |
| Chapter 09, reused in 10 | 14 queries, 168 eligible pairs | Overlap/BM25/WAND; BM25/binary cosine on this set | “Dense semantic” gain from lexical coordinates |
| Chapter 11 | 17 queries, 204 pairs | BM25/frozen encoder by declared slices | Headline progress versus Chapter 09's different questions |
| Chapter 12 | 10 training pairs; 15 validation/test questions, 180 judged pairs | Frozen/selected adapter/BM25 under declared split | Family-held-out transfer from document IDs alone |
| Chapter 13, reused in 15/16 | 14 stress questions, 168 pairs | Exact/ANN/quantized candidate routes on same model/index | Validated model gain from inspected ANN qrels |
| Chapter 14 | Two separate one-query/three-row fixtures | Sparse/operator and MaxSim/pooled mechanism comparisons | SPLADE/ColBERT paper replication or cross-chapter latency gain |
| Chapter 15/16 synthetic | Declared seeds/sizes/dimensions/planted questions | Geometric oracle recall, work and local cost | Human relevance, answer quality or service tails |

### Publishing health summary

| Artifact / check | Outcome | Scope / concern |
|---|---|---|
| Current reader build | Pass, 241 pages | Generated in temporary copy only. |
| Local links/referenced assets/preflight | Pass in configured current build | Does not prove all remote URLs or every unbuilt profile. |
| PDF extraction checks | 21 pass | Complemented with rendered-page inspection. |
| PDF fonts/destinations | Embedded/resolvable in checked document | No live viewer interaction performed. |
| Visual assets | 23 rendered figures inspected | 16.01 annotation and 13.01 flow need targeted fixes. |
| Near-empty pages | Six warnings | Two visibly confirmed as orphan content. |
| Code wrap | Two source groups warned | Lab 13 and V3 README, longest reported lines around 140 columns. |
| Bibliography | Present and readable | Two duplicated paper identities. |
| Term index | No entries | Reader publication decision/authoring markers required if an index is expected. |
| Existing local `dist` reader | Stale 198-page/13-chapter artifact | Refresh during publication, not during independent source audit. |

## Should authoring proceed to Chapter 17?

**YES — proceed after targeted fixes**

The mechanisms, baselines, current data and experiments are sound enough to continue. The evidence does not justify a structural pause. Continuing the **authoring pattern unchanged**, however, would compound meaningful implementation-practice, mathematical-prerequisite and request-observability debt.

Correct the bounded construction/math/trace pattern first as Chapter 17 is prepared, and close the seven P1 items within the next five chapters. Preserve the existing exact oracle, corpus/model identities, negative experimental decisions and authorization boundaries. P2 publishing defects should not be used to block technical authoring.

No chapter, syllabus, code, figure, reference, checked result or existing distribution file was modified by this audit. Only `audits/QUARTER_BOOK_AUDIT_CH01_16.md` was created; execution and build artifacts stayed outside canonical source paths. No commit was made.





