# Chapter 8 authoring review and completion checklist

**Reviewed:** 2026-09-29. **Artifacts:** [chapter](../../chapters/chapter-08-production-lexical-query-execution.md), [lab](../../labs/chapter-08/LAB.md), [solutions](../../solutions/chapter-08-solutions.md), [V2 stage](../../projects/V2/README.md), [searcher](../../projects/V2/wand.py), [codec](../../projects/V2/postings_codec.py), [fictional fixture](../../projects/V2/toy_pruning_corpus.json), [experiment record](../../projects/V2/chapter-08-experiment.json), [figure source](../../visuals/chapter-08/plot-08-01-cursors-bounds-threshold.py) and [SVG](../../visuals/chapter-08/figure-08-01-cursors-bounds-threshold.svg). **Decision:** Chapter 8 teaches exact lexical query execution; Chapter 9 remains the first judged retrieval-metric chapter.

## Technical accuracy review

- The Chapter 7 score, positive title boost, analyzer, scope statistics, source snapshot, V0 tie order, context budget and deterministic stub are held fixed. The new index-time cache stores per-scope per-posting impacts and outward-rounded global maxima. Query time uses sorted cursors, a min-heap and a conservative WAND pivot. Its invariant is `S(q,d)≤Σ U_t` over terms that can still match, conditional on valid nonnegative bounds and the same eligibility/scoring snapshot. Equal-threshold candidates remain eligible because the stable tie key can decide rank. This is a tested finite Python implementation, not a proof for arbitrary floating-point configurations.
- The toy support scope has six eligible posting-union matches. P7 is legal-only and excluded from score statistics, impacts, bounds, candidate IDs and context. After P1 scores `1.093526829`, a `common` cursor seeks P2→P6 over four postings; P6 scores `0.983418829` and loses. Cached exhaustive fully scores six; WAND scores two. The plotted conceptual B2/B3 maxima are lower than the threshold, but the code does **not** implement Block-Max WAND. Plot labels and the actual cursor trace were compared to the experiment JSON and visually inspected.
- The codec encodes `[3,8,138]` as gaps `[3,5,130]` and bytes `83 85 01 82` under the stated final-byte high-bit convention. It is separate from V2's RAM search and does not claim compressed on-disk postings, skip-address layout or segment merge. Fielded/positional data, immutable segments, merging and production query latency are taught conceptually with primary sources.
- The paired experiment has a five-query frozen set, depths 1/2/8, one plan variable, cached exhaustive control and untimed direct-BM25 oracle. It retains line-ending-canonical hashes, versions, seed, eleven raw randomized-order search-only times per mode/case, exact candidate IDs and unrounded scores, work counters, selected context, required-span checks and stub outcomes. All fifteen cases agree with the oracle; score work falls on some queries but the checked-in tiny Python run is slower. The dated-contract top-two omission and abstention persist. These fixture-required spans are **not** exhaustive qrels or answer-quality labels.
- Indexing/build cost, search-only latency and context/stub work are separated. Normal output avoids query/source text; fictional cursor traces are opt-in. Static scope is not authentication. Bound invalidation, deletions, licensing/retention, protected trace access and tenant-safe cache implications are explicit. No model API call, billed token amount or deployed service exists in this chapter.
- Claims were checked against the primary Stanford IR compression/execution chapters, Broder et al.'s WAND paper, Ding and Suel's BMW paper and versioned Lucene segment documentation, recorded in [REFERENCES.md](../../REFERENCES.md). No measured production speedup or BMW implementation is claimed.

## Pedagogical review

- The chapter begins with the observed Chapter 7 exhaustive-score cost, then separates disk postings from scoring plans, derives the upper-bound inequality, hand-traces the pivot, compares execution families and finally tests the implementation. The learner sees precisely what makes a skip safe before meeting algorithm names.
- Figure 8.01 answers why a cursor may seek and how block bounds could tighten the same query. Its two panels distinguish actual WAND movement from conceptual BMW bounds; colors, caption, alt text, axes, units, data/source, and no-randomness status are stated. A compact table handles plan comparisons, and pseudocode handles program order. A generated illustration is **N/A** because an exact data-driven plot is clearer for this proof.
- The lab asks for bytes, intersection, an inequality, cursor trace, controlled experiment and broken-bound diagnosis before reading separate solutions. The oral defense tests exactness, cost and invalidation. Active recall and observable mastery targets are present. Chapter 9's qrels are previewed but not used as a prerequisite.

## Chapter completion checklist

### Learning and mechanism

- [x] Chapter 7's observed exhaustive work motivates the change; prerequisites 5–7 remain binding.
- [x] Gap/variable-byte, skip, TAAT, DAAT, heap threshold, impact, WAND, MaxScore, BMW and segments have definitions or linked glossary entries.
- [x] Index-time compression/cache/bounds and query-time cursor/heap/context paths are distinct.
- [x] BM25 contribution and bound inequality, score units, tie equality, missing-list and finite-precision limits are explicit; toy scores and bytes are worked by hand.
- [x] Pseudocode and standard-library cursor/heap search precede production analogues.
- [x] Work bounds, cached-impact storage/build cost, compressed-I/O trade-off, local latency and worst-case lack of pruning are stated.
- [x] Execution alternatives, exact/approximate boundary, prior baseline and Chapter 9 dependency are explicit.

### Evidence and operation

- [x] Experiment question/hypothesis, baseline, single variable, frozen corpus/query/depth/scope, relevant fixture spans, seed, hashes, raw samples, results, failure and limits are retained.
- [x] Candidate agreement, selected context, stub status and absent judged generation quality are separate.
- [x] Version/work/latency trace fields, aggregated metrics and protected diagnostic details are explained. Paid-model cost is **N/A** because no model runs; query CPU and index build remain relevant costs.
- [x] No-result, rare numeric, common broad, equal ties, corrupted bounds and legal-only source are probed.
- [x] Eligibility before scoring/fetch, cache invalidation and source retention/licensing implications are checked.

### Visual and practice

- [x] Visual audit chose one data-driven two-panel plot for cursor/bound movement; exact lists, tables and code cover the remaining micro-concepts.
- [x] Figure 8.01 has number, title, takeaway, alt text, editable code, checked-in data, units, no-randomness note, SVG/PNG and chapter association.
- [x] Plot trace, block sums, threshold, labels, colors and normal-reading-size legibility were checked against code and rendered output.
- [x] Hand exercise, debugging/design/oral defense, V2 upgrade and separate solutions are present.
- [x] Recall prompts, observable mastery abilities and primary further reading are present.

### Release hygiene

- [x] Chapter/project links, syllabus numbering and figure number were checked; Chapter 9 is not authored.
- [x] Primary references are recorded for the writing date and algorithm names are subordinate to mechanisms.
- [x] V0/V1/V2 tests, code compilation, checked-in experiment hashes/results, plot rendering and manuscript preflight pass; negative latency and contract findings are retained.
- [x] Chapter, lab, solutions, code, tests, fixture, record, plot, glossary, references, project snapshot and this review are included in the Chapter 8 change.
