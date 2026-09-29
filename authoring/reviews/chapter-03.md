# Chapter 3 authoring review and completion checklist

**Reviewed:** 2026-09-29. **Artifacts:** [chapter](../../chapters/chapter-03-data-algorithms-and-measurements-needed-for-search.md), [lab](../../labs/chapter-03/LAB.md), [solutions](../../solutions/chapter-03-solutions.md), [V0 measurement note](../../projects/V0/CHAPTER_03_MEASUREMENT.md), [benchmark code](../../projects/V0/measurements.py), [frozen data](../../projects/V0/chapter-03-measurements.json), and [plot source](../../visuals/chapter-03/plot-03-01-id-lookup.py). **Decision:** ready as the computing and measurement prerequisite for Chapters 4–6. No Chapter 4 manuscript or term index was started.

## Technical accuracy review

- V0's original [engine](../../projects/V0/engine.py) is unchanged. The new sidecar compares **the same exact-ID operation** with a list scan and dictionary, verifies equal present/missing results outside timing, and does not route a natural-language question through `by_id.get`. The Chapter 1 `D1`/`D2`/`D3` evidence and `D10` eligibility contract remains covered by the existing tests.
- Complexity statements name their task and assumptions: worst-case `O(n)` list scan; average-case dictionary `O(1)` and possible worst-case `O(n)`; binary search only after sorting; preparation/build cost separate from query cost. V0's actual path includes scanning all prepared segments for eligibility, repeated tokenization of eligible segments and sorting positive-score candidates.
- Hand calculations were checked: uniformly located present ID at `n=16` averages 8.5 comparisons; `log₂1024=10`; `120/(30−0.2)≈4.027`, so five integer lookups satisfy the strict break-even inequality. The saved 16,384-record values give `2349.3/(528.284−0.259)≈4.45`, again five whole lookups under the idealized assumptions. Mean, nearest-rank p95, dot product, norms and cosine calculations agree with the solutions.
- V0 token counts were executed against the actual tokenizer: contract question 14 whitespace words / 14 regex terms / 14 distinct; termination question 9 / 9 / 8. Unicode examples were checked using escaped code points: `§` and composed `é` are one code point/two UTF-8 bytes; decomposed `e\u0301` is two/three and yields V0 term `e`. The solutions label the local JSON file-byte count as checkout-dependent because newline conversion can change it.
- The default and all-miss benchmark records were collected **sequentially**. Each records timestamp, Python/platform, seed, workload, 256 keys, seven raw trial samples per method, hit/miss counts, map-build time, shallow container bytes and serialized bytes. The chapter and solution tables were machine-checked against the frozen JSON. The all-miss result and measurement-noise limits are preserved. No p95, confidence interval or end-to-end speed claim is inferred from batched averages.
- Figure 3.01 was generated from the checked-in JSON by the editable plotting script. Both axes, units, log scales, lines, markers and min/max trial-range bars match the data and prose. SVG and PNG were visually inspected at normal reading size. The figure's information survives grayscale through solid/circle versus dashed/square encoding.
- The Python project's current container-complexity page and official `perf_counter_ns`, `timeit`, Unicode and `sys.getsizeof` documentation were checked on the review date. Claims stay within those sources' scope; tool version and local environment appear in the raw report. [Source register](../../REFERENCES.md).

## Pedagogical review

- The motivating failure is V0's repeated full scan. Chapter 2's list, dictionaries, sets, fixed snapshot, scope gate and trace are reused rather than retaught from scratch. The same-task ID comparison prevents a misleading “dictionary replaces retrieval” conclusion and keeps the actual inverted index as a later mechanism.
- Definitions precede the worked calculations. The chapter repeatedly distinguishes input size from elapsed time; average from worst case; preparation from query cost; shallow memory from total memory; code points, bytes, words, regex terms and model tokens; batch-average timing from request percentiles; and geometric similarity from evidence authority.
- Figure 3.01 answers the growth question. Exact tables show data-structure roles, word/term counts and measured values. A separate flow diagram would repeat Chapter 2's existing preparation/query diagrams, so it has no added teaching value here. The plot has source code, raw data, environment, axes and units; its caption explicitly limits the inference.
- The lab requires independent implementation, controlled measurement, a hit/miss counterexample, experiment card, misleading-claim diagnosis, hand arithmetic, leakage-aware split design and V0 regression checks. Separate solutions expose exact expected arithmetic while treating rerun timings as variable. Recall prompts and observable mastery abilities close the chapter.
- The project update is a diagnostic attached to V0, not a premature V1 index. Frozen evidence questions and trace-stage distinctions remain visible. No label or answer-quality improvement is claimed from the synthetic benchmark.

## Chapter completion checklist

### Learning and mechanism

- [x] V0's repeated scan motivates the chapter; Chapters 1–2 and their source contract are explicit prerequisites.
- [x] Lists, maps, sets, hashing, growth, units, measurement and split terms are defined and entered in the [glossary](../../GLOSSARY.md), with limits.
- [x] Preparation, exact-ID lookup and V0's separate query-time search path are traced without confusing ID fetch with retrieval.
- [x] Complexity assumptions, units, edge cases and hand calculations cover lookup, break-even, byte/term counts, logarithms, vectors and percentiles.
- [x] Pseudocode-like traces and small standard-library code precede service abstractions; a dictionary is not presented as a term index.
- [x] Build and query time, memory containers, serialized bytes and omitted storage/network costs are bounded; local latency is measured with uncertainty cautions.
- [x] Alternatives, update costs, misconceptions, Chapter 2 continuity and Chapter 5 index motivation are explicit.

### Evidence and operation

- [x] The exact-ID experiment states question, hypothesis, baseline, variable, controls, synthetic corpus, deterministic keys, measures/denominators, procedure, results, error analysis, conclusion and limitations. Formal relevance qrels are **N/A** to exact equality; the two V0 evidence questions remain separately frozen.
- [x] Candidate retrieval, selected context and answer outcomes are kept distinct from the synthetic lookup timing; V0 failure examples are retained.
- [x] The measurement manifest, raw samples, versions and units complement rather than replace V0 request traces. Ingestion events and a monetary ledger are **N/A** because this sidecar ingests no external source and calls no paid model or service.
- [x] All-miss, Unicode normalization, tiny-sample p95, test leakage and unauthorized-ID probes support diagnosis; production-scale claims are explicitly bounded.
- [x] Verified eligibility remains required for real ID access; real benchmark copies would inherit source privacy, licensing and retention policy.

### Visual and practice

- [x] The visual audit chose a measured growth plot and exact tables; Chapter 2 already supplies the stage-flow diagrams.
- [x] Figure 3.01 has number, title, takeaway caption, alt text, chapter association, editable script, JSON data, units, platform and rendered SVG/PNG. Generated illustration specification is **N/A** because no illustration is used.
- [x] Plot values, bars, labels, log axes and table values agree with the raw data; readability and shape-based distinction were visually checked.
- [x] Worked exercise, debugging/design/oral-defense questions, V0 characterization and separate solutions are present.
- [x] Active recall, observable “You understand this chapter if you can…” abilities and verified further reading are present.

### Release hygiene

- [x] Local links, numbering, prerequisites and project-version references were audited; no Chapter 4 content was authored.
- [x] Primary sources and runtime/plotting versions were verified for the writing date; no frontier claim was introduced.
- [x] Thirteen V0 and measurement behavior tests passed; the plot regenerated; table values match the frozen JSON; negative results and limits remain visible.
- [x] Chapter source, lab, solutions, code, tests, raw measurements, plot source/renders, terminology, reference register and this review are committed in one Chapter 3 change.
