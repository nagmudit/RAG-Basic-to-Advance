# Chapter 7 authoring review and completion checklist

**Reviewed:** 2026-09-29. **Artifacts:** [chapter](../../chapters/chapter-07-bm25-and-other-lexical-ranking-models.md), [lab](../../labs/chapter-07/LAB.md), [solutions](../../solutions/chapter-07-solutions.md), [V2 stage](../../projects/V2/README.md), [scorer](../../projects/V2/bm25.py), [fixture](../../projects/V2/toy_length_corpus.json), [paired experiment](../../projects/V2/chapter-07-experiment.json) and [figure source](../../visuals/chapter-07/plot-07-01-bm25-controls.py). **Decision:** Chapter 7 begins V2 with an exhaustive BM25 comparator. Chapter 8's exact top-*k* pruning and Chapter 9's judged qrels remain future dependencies.

## Technical accuracy review

- The scorer reuses the Chapter 5 positional index and V0 context/answer stub. The default eligible corpus unit is a segment. `N`, `df`, analyzed title-plus-body `L_d` and `avgdl` are computed per static scope; legal-only S5 never changes support-team statistics or candidates. Eligibility is checked before contribution accumulation and record fetch. The caller-supplied scope is explicitly a fictional teaching fixture, not authentication.
- The implemented IDF is exactly `ln(1+(N−df+0.5)/(df+0.5))` for `df>0`; it is positive even at `df=N`. The chapter distinguishes it from Chapter 6 `ln(N/df)` and the potentially negative RSJ no-feedback form. Query terms are deduplicated. Missing postings produce no candidates, while common-term postings still produce scored candidates. `k1>0`, `0≤b≤1` and positive finite title boost are validated. `avgdl=0` cannot arise for a positive posting from a consistent index; the factor raises if it does.
- The toy arithmetic was recomputed from the scorer: support `N=4`, `df(amber)=2`, `avgdl=4`; S1 `K=.75`, factor 1.6, score 1.109035; S2 `K=2.55`, factor .967033, score .670296. At `b=0` they tie at .953077; raw TF-IDF ties at 1.386294. S2 `amber filler` contributions .670296 and 1.156340 sum to 1.826636. Figure 7.01 plots the imported `saturation()` function, with the left asymptotes `1+k1` and the right `b=0` flat control.
- The paired experiment holds source snapshot, analyzer, eligibility scope, four query IDs, depth, context budget and stub fixed while comparing five declared score modes. The experiment record includes code/corpus SHA256 with CRLF normalized to LF for cross-platform checkouts, seven raw randomized-order search-only timings per mode/case, one-time build costs, candidate IDs/scores, selected-context IDs, fixture-required span coverage, work counts and stub status. At top two both BM25 variants gain the termination span and lose one dated-contract span; `D1 §3` ranks fourth under `b=.75`. At top eight every compared mode covers the two fixture tasks. These are narrow checks; no judged retrieval or LLM correctness metric is claimed.
- Historical and algorithmic claims were checked against the primary Stanford IR BM25 and language-model accounts, Robertson–Zaragoza's survey, Lv–Zhai's original BM25+ work, and the versioned Apache Lucene 10.4.0 BM25 API in [REFERENCES.md](../../REFERENCES.md). The chapter labels the combined-field title boost as a toy policy, not BM25F or Lucene numerical parity. It states BM25 scores are uncalibrated ranking signals.
- The query path visits eligible posting matches and sorts all scored segments. Complexity is bounded by matching postings plus sorting; no Chapter 8 pruning is implied. Per-scope precomputation and permission-change consistency costs are stated. The normal trace separates candidate, context and evidence IDs, versions, stage timings and approximate prompt-token proxy; the local term explainer is access-sensitive. No model calls or paid costs exist at this stage.

## Pedagogical review

- The chapter begins from Chapter 6's observed repetition/length limitations and the contract-clause regression, then derives the BM25 terms, works a short/long example, shows index/query pseudocode, introduces the from-scratch scorer and only then maps to Lucene and variants. It uses probabilistic odds as motivation without mislabeling BM25 as a calibrated probability.
- Figure 7.01 answers two specific questions: how repeated occurrences saturate and how a fixed `tf` changes with length. The axes, units, fixed parameters, source, formula-derived status, exact asymptotes, alt text and rendered alternatives are stated. The SVG/PNG were rendered and inspected at reading size. Exact experiment outcomes use a table rather than a misleading smooth plot.
- The lab requires calculation before code, isolates `b=0` as a control, checks legal-scope and no-result boundaries, reproduces a negative contract outcome, asks for a controlled experiment card and gives an oral defense. Solutions contain both arithmetic and failure localization. Parameter tuning is deferred until Chapter 9 supplies a development/test judgment split; this preserves the syllabus dependency.
- BM25+, BM25F, smoothed query likelihood and exact/fuzzy candidate matching are separated by mechanism. Their inclusion is conceptual, without making this chapter a second full search textbook or claiming those variants were implemented in V2.

## Chapter completion checklist

### Learning and mechanism

- [x] A concrete V1 ranking limitation, its measured counterexample and already-taught postings/TF-IDF motivate the chapter.
- [x] BM25, IDF conventions, `k1`, `b`, `avgdl`, BM25+, BM25F, query likelihood and smoothing have explicit definitions and glossary entries or chapter formulas.
- [x] Index-time per-scope statistics and query-time eligibility, posting accumulation, sort, context and answer stages are distinct.
- [x] Formula assumptions, units, `df=0`, `df=N`, empty scope, positive match length and invalid parameter cases are stated; S1/S2 arithmetic is hand-worked.
- [x] Pseudocode and a standard-library implementation expose the mechanism before Lucene is introduced.
- [x] Posting/sort complexity, per-scope storage/update cost and search-only/build time boundaries are stated.
- [x] Alternatives, scoring conventions, lexical mismatch, field policy, next dependency and non-probability misconception are explicit.

### Evidence and operation

- [x] Experiment question, baseline, one primary scoring-configuration variable, controlled corpus/questions/depth/budget/scope, narrow required evidence IDs, raw samples, opposing results, latency, hashes and limitations are preserved.
- [x] Candidate ranking, selected context, deterministic stub and later LLM/answer judgment are never collapsed into one measure.
- [x] Versioned redacted request trace and build/search timings are present. Production metrics/events, token billing and cost ledger are **N/A** because no service or model runs in Chapter 7.
- [x] Dated-contract and termination disagreements, no-result/common-term distinction, title-boost caveat and restricted S5 are explicit probes.
- [x] Eligibility, access-sensitive term explanation, static-scope revocation and tenant-cache risk are reviewed; sources are fictional.

### Visual and practice

- [x] Visual audit chose one reproducible two-panel formula plot; tables, prose and pseudocode cover exact experiment outcomes and process steps without duplicating Chapter 5's workflow diagrams.
- [x] Figure 7.01 has title, number, takeaway, alt text, editable Python source, parameters/data, axes/units, no-randomness note, SVG/PNG and chapter association; generated illustration is **N/A** because exact formula plots teach the mechanism better.
- [x] Plot values, limits, labels, color/marker distinction and legibility were compared with the scorer and inspected at reading size.
- [x] Worked calculation, controlled lab experiment, debugging/design/oral defense and separate solutions are present.
- [x] Active-recall prompts, observable mastery abilities and primary further reading are present.

### Release hygiene

- [x] Chapter/project links resolve, syllabus numbering is sequential, and Chapter 8 material is only a dependency preview.
- [x] Primary references and Lucene documentation were checked for 2026-09-29; no evolving research acronym is promoted into a core claim without mechanism.
- [x] V0/V1/V2 tests, experiment hashes/raw samples, toy arithmetic, plot rendering and SVG syntax reproduce; the negative contract result is retained.
- [x] Chapter, lab, solutions, code, tests, fixture, experiment record, figure source/renderings, glossary, references, project note and this review are included in one Chapter 7 change.
