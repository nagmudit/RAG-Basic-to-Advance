# Chapter 6 authoring review and completion checklist

**Reviewed:** 2026-09-29. **Artifacts:** [chapter](../../chapters/chapter-06-tf-idf-vector-space-ranking-and-lexical-limits.md), [lab](../../labs/chapter-06/LAB.md), [solutions](../../solutions/chapter-06-solutions.md), [V1 project](../../projects/V1/README.md), [scorer](../../projects/V1/tfidf.py), [paired experiment](../../projects/V1/chapter-06-experiment.json), [plot source](../../visuals/chapter-06/plot-06-01-sparse-tfidf-matrix.py) and [ranking fixture](../../projects/V1/toy_ranking_corpus.json). **Decision:** Chapter 6 completes V1's first lexical-ranking comparison; Chapter 7's BM25 and Chapter 9's judged ranking evaluation remain future work.

## Technical accuracy review

- The index, analyzer and V0 answer stub are unchanged. The new scorer reuses Chapter 5 postings, scopes, field positions and source records. It declares a segment as the DF unit and uses scope-local `N` and `df`; legal-only D10 does not affect support-team weights. Statistics and cosine document norms are prepared outside request timing. Title boost is positive, finite and part of the scoring version.
- Raw scoring is `sum(tf_w × ln(N/df))` over distinct query terms. Sublinear scoring transforms positive *integer field counts* with `1+ln(tf)` before applying the title boost, avoiding negative transformed counts for small boosts. Cosine uses document coordinates `tf_w×idf` over the full eligible vocabulary, query coordinates `idf` for distinct query terms, and both complete vector norms. Zero `df` is skipped, zero `N` yields no candidates, and a zero cosine denominator yields score zero for a posting match. Scores are not probabilities.
- The four-record fixture was checked against code and hand arithmetic. Before T4: `N=3`, both `df=2`, both `idf=0.405465`, rank T2>T1. After one blue-only T4: `N=4`, `df(amber)=2`, `df(blue)=3`, IDFs `0.693147`/`0.287682`, raw rank T1>T2. Sublinear and cosine keep T2 first. Solution norms and dot products were independently recomputed before release. The plot computes its cell values from the same scorer and fixture.
- The V1 paired experiment changes only the score mode at fixed V0 corpus, analyzer, scope, query, candidate depth and context budget. It retains source/index/ranker/experiment hashes, query-set version, seven raw timed search samples per mode/case, separate build times, candidate IDs/scores, context IDs, fixture-required-span coverage, and deterministic stub status. At k=2, raw/sublinear gain the termination span but lose the old dated-contract span; cosine gains neither termination at that depth nor contract coverage. At k=8 all modes cover the two fixture tasks. These are narrow evidence checks, not broad qrels or LLM correctness results.
- Source claims about TF, IDF, sublinear weighting, cosine, length effects and Lucene's different classic implementation were checked against the primary Stanford IR text and versioned Apache Lucene API documentation in [REFERENCES.md](../../REFERENCES.md). No claim that a particular mode wins a production workload is made.
- Eligibility precedes contribution accumulation and source-text fetch. The ordinary trace contains candidate/context/evidence IDs and scores, but no raw question or source text. The local `explain()` helper can reveal query terms and is explicitly restricted to fictional/protected use. Static scope statistics and membership are educational; the chapter states revocation and tenant-safe cache implications.

## Pedagogical review

- The chapter starts from Chapter 5's unweighted ties, introduces TF/DF/IDF with an explicit corpus unit, then derives a sparse matrix and one-document rank reversal before offering variants. It explains why a common-term zero score differs from no posting and why a missing query term does not impose AND semantics.
- The matrix figure answers a specific question: how a corpus change alters old document weights. Axes, units, exact values, source fixture, code and no-randomness/no-uncertainty condition are stated. It was rendered to SVG/PNG and inspected for annotation contrast and legibility. Exact workload outcomes use a table rather than a misleading smooth latency plot.
- The lab asks learners to calculate before running code, name every weighting choice, inspect edge cases, reproduce both favorable and unfavorable top-two results, defend the scope boundary, and localize a lost governing clause. The solutions report the same negative result. This prevents treating TF-IDF as a universally superior replacement for overlap.
- V0 remains the control; V1 now has both unweighted and weighted paths. The next dependency is BM25's treatment of repetition and length, followed by Chapter 9's broader qrels, so no future formula or judged metric is silently assumed.

## Chapter completion checklist

### Learning and mechanism

- [x] A concrete V1 overlap-ranking limitation and Chapters 3/5 prerequisites motivate the change; Chapter 4's evidence/answer boundary remains in force.
- [x] TF, DF, IDF, sparse vectors, sublinear TF, cosine and scope-local statistics have definitions and glossary entries with limits.
- [x] Index-time corpus statistics/norms and query-time posting accumulation, ranking, context and answer stages are separated.
- [x] Every formula declares its unit, transform and edge cases; the T1–T4 two-term numerical example and cosine norms are hand-worked.
- [x] Pseudocode in prose and a standard-library scorer expose the mechanism before the production Lucene analogue.
- [x] Posting traversal, per-scope statistics storage/update cost, build timings and search-only latency are bounded or measured at the correct scope.
- [x] Raw, sublinear and cosine trade-offs, exact-identifier/synonym limits, BM25 dependency and non-comparable score scales are explicit.

### Evidence and operation

- [x] Experiment records a falsifiable ranking question, overlap baseline, one score-mode variable, fixed corpus/analyzer/scope/query/depth/budget, two fixture evidence sets, work/latency/coverage measures, samples, opposing outcomes and limitations.
- [x] Candidate required-span coverage, selected-context coverage and deterministic stub status are separate; no answer correctness or general relevance claim is inferred.
- [x] Corpus/index/analyzer/scorer/query-set hashes and versions, rounded redacted candidate scores, search work, stage timing and build costs support reproduction. Model tokens, paid cost ledger and production dashboard are **N/A** because no model or service runs.
- [x] Added-document reversal, zero IDF, unseen term, small title boost, missing D1 at k=2 and D10 scope are explicit probes and tests.
- [x] Permission gating, scope-local statistic policy, revocation/cache risk and local explainer disclosure are reviewed; fixture content is fictional.

### Visual and practice

- [x] Visual audit selects one exact programmatic sparse-matrix plot; prose/tables handle formulas and controlled result counts. A workflow diagram would repeat Chapter 5's already-taught index path.
- [x] Figure 6.01 has number, title, takeaway, alt text, chapter association, editable Python source, versioned data, axes, dimensionless units, no-randomness note, SVG and PNG. Generated illustration and additional plot are **N/A**.
- [x] Plot values, labels, T4 perturbation, color annotations and rank claims were compared with code and visually inspected at reading size.
- [x] Worked calculation, diagnosis/design questions, V1 upgrade and separate solutions are present.
- [x] Active recall, observable mastery abilities and primary further reading are present.

### Release hygiene

- [x] Chapter/project links, sequential syllabus numbering and prerequisites resolve; no Chapter 7 content was authored.
- [x] Primary references and local runtime/plot versions were checked for 2026-09-29; no unstable frontier result is asserted.
- [x] V0/V1 behavior tests, experiment hashes/samples and plot rendering reproduce; weak and negative outcomes are retained.
- [x] Chapter, lab, solutions, code, tests, fixture, experiment data, plot source/renderings, glossary, references, project note and this review form one Chapter 6 change.
