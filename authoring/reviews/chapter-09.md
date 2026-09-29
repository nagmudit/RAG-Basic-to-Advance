# Chapter 9 authoring review and completion checklist

**Reviewed:** 2026-09-30. **Artifacts:** [chapter](../../chapters/chapter-09-relevance-judgments-and-ranking-metrics.md), [lab](../../labs/chapter-09/LAB.md), [solutions](../../solutions/chapter-09-solutions.md), [V2 project](../../projects/V2/README.md), [qrels](../../projects/V2/judgments_ch09.json), [metric code](../../projects/V2/eval_ch09.py), [tests](../../projects/V2/test_eval_ch09.py), [paired experiment](../../projects/V2/chapter-09-experiment.json), [figure source](../../visuals/chapter-09/plot-09-01-ranked-gain.py) and [SVG](../../visuals/chapter-09/figure-09-01-ranked-gain.svg). **Decision:** Chapter 9 completes the first judged V2 retrieval baseline and Part II. Chapter 10 remains untouched.

## Technical accuracy review

- The judgment universe is the twelve indexed support-team **segments** from source snapshot `support-corpus-2026-05-20`, not whole documents or all ten source records. Fourteen questions generate 168 reviewed pairs. All omitted nonzero entries are declared and inspected grade 0; the loader expands these and rejects source, scope, unit or ordered eligible-roster mismatch. D10 is legal-only and never a support-team qrel, score or context item. The scope is a fixture, not authentication.
- Grades 0/1/2 have query-specific written rationales, including signed current versus old FAQ, draft when explicitly requested, observation versus contract, multi-window runbook evidence and three zero-positive questions. Two V0 questions are identical to their frozen originals. This single-author set is not held out, not independently adjudicated and not representative of a production workload; those limitations are stated beside every claim.
- The pure evaluator uses binary threshold grade ≥1; fixed-*k* Precision treats absent slots as nonrelevant; Recall and AP denominators include all known positives; MRR stops at the first positive; DCG gain is `2^grade−1`, discount is `log₂(rank+1)`, and IDCG comes from the full eligible roster. Zero-positive queries have `null` for undefined measures and a separate any-candidate flag. Duplicate, unjudged or ineligible IDs raise. Macro averages include positive queries only; micro recall pools positive hits/denominators. Hand arithmetic and edge tests check these choices.
- The experiment changes overlap versus BM25 scoring on the same V1 postings; WAND is a same-score execution control, not an independent relevance model. For fourteen queries at four depths, it records raw ordered IDs/scores, judged metrics, selected context, direct-evidence coverage, limited V0 stub status, scored counts and eleven randomized-order search-only timing samples per mode/case. The record pins source/qrel/code hashes, versions, seed, query mix, measurement window, one-time build cost, p50/p95 and failure examples. No LLM was called.
- The BM25 macro NDCG@2 gain hypothesis is falsified: overlap 0.9091; BM25/WAND 0.8997. BM25 direct recall improves 0.9091→0.9545 while binary recall falls 0.9091→0.8636. Dated-contract grade-2 coverage falls to one of two at top two; termination grade-2 coverage improves. WAND matches exhaustive BM25 IDs, raw scores, qrel metrics and context but is slower locally. Two of three zero-positive queries return irrelevant candidates; private D10 remains excluded. All numeric statements were checked against the checked-in JSON, not recomputed from rounded table values.
- Query-set/rubric versions, source/index/scorer/executor hashes, candidate/context/stub separation and redaction boundaries are documented. The evaluation record is an offline quality observation rather than a production metric stream or a full request trace. Human assessment expense and report size are bounded conceptually; no billed model/token cost is claimed. Legal/privacy retention implications of stored qrels and traces are discussed.
- Historical/benchmark statements were checked against primary Stanford IR evaluation and relevance-assessment chapters, NIST's TREC overview and qrel guidance, and official `trec_eval` documentation, recorded in [REFERENCES.md](../../REFERENCES.md). Tool conventions are compared, not claimed numerically identical.

## Pedagogical review

- The chapter begins with Chapter 8's exact but still wrong dated-contract top two, then fixes judgment unit, eligibility, rubric and full denominator before defining a metric. The same four-item A/B/C/D example supplies hand Precision/Recall/F₁/RR/AP/NDCG arithmetic; explicit zero-positive and missing-slot rules prevent divide-by-zero shortcuts.
- Figure 9.01 answers what order changes when the same items are returned. Its left panel displays IDs and grades; its right panel plots cumulative gain from the exact metric formula. Axes, units, toy data, absence of sampling, alt text, editable source, SVG/PNG and chapter association are stated. It was rendered and inspected at normal reading size; a decorative generated image is **N/A** because exact labels and formula curves teach this concept better.
- The lab requires qrel audit, three hand rankings, an independent metric core, a paired experiment, an experiment card, debugging and an oral defense before separate solutions. The Part II checkpoint tests V0 scan → V1 index/TF-IDF → V2 BM25/WAND/judgment continuity with an architecture sketch. High MRR, unjudged-pool bias and context-stage loss receive explicit counterexamples.
- The chapter distinguishes candidate metrics from selected context, stub output and future answer judgments, and keeps observed aggregate losses alongside gains. It defers broad benchmark transfer, assessor calibration at scale, statistical confidence intervals and answer-faithfulness evaluation to their syllabus positions while giving enough mechanism to interpret a first judged retriever.

## Chapter completion checklist

### Learning and mechanism

- [x] Chapter 8's unchanged but incomplete contract retrieval motivates labels; earlier analyzer/posting/BM25 concepts are prerequisites.
- [x] Qrels, grades, eligible universe, pooling/unjudged, binary/rank/graded metrics, macro/micro and zero-positive terms are defined and added to the glossary.
- [x] Source/index preparation, query retrieval, offline assessment, context packing and limited stub generation are separated.
- [x] Formula assumptions, fixed-*k* denominators, all-positive AP denominator, DCG gain/discount, no-result and duplicate/ineligible edges are explicit; A/B/C/D arithmetic is worked.
- [x] Pseudocode and standard-library metric implementation expose mechanics before `trec_eval` is mentioned as a production research analogue.
- [x] `O(QN)` qrel expansion, `O(k+N log N)` per-query metric work, judgment/report costs and measured local latency are bounded.
- [x] Different metrics' trade-offs, scorer baseline, Chapter 10 dependency, benchmark transfer and answer-quality misconceptions are explicit.

### Evidence and operation

- [x] Experiment question, falsifiable hypothesis, one primary quality variable, fixed corpus/questions/scope/rubric/depth, WAND control, 168 judgments, raw samples, per-query/aggregate results, seed, failures and limits are preserved.
- [x] Candidate ranking, selected context, two-task deterministic stub and absent general answer labels remain distinct.
- [x] Offline evaluation output, request-trace fields, aggregated latency/quality views, versions, protected diagnostics and lifecycle changes are explained; paid-model cost is **N/A** because there are no model calls.
- [x] Dated-contract, termination, generic-overlap no-answer, nonexistent identifier and restricted-source probes are inspected; pooling bias and assessor disagreements are covered.
- [x] D10 eligibility and private-question/qrel retention boundaries are reviewed; no rank score overrides permission.

### Visual and practice

- [x] Visual audit chose one data-driven rank/gain plot; tables and formulas handle exact metric comparisons without decorative charts.
- [x] Figure 9.01 has number, title, takeaway, alt text, editable source, exact input grades, axes/units, no-randomness note, SVG/PNG and chapter association.
- [x] Plot ranks, colors, labels, curves and final DCG/NDCG were checked against metric code and visually inspected.
- [x] Hand calculations, code exercise, failure diagnosis, project upgrade, oral defense, Part II checkpoint and separate solutions are present.
- [x] Active recall schedule, observable mastery abilities and primary further reading are present.

### Release hygiene

- [x] Chapter/project links, syllabus numbering and Figure 9.01 reference were checked; no Chapter 10 content was authored.
- [x] Primary references and tool conventions were verified for 2026-09-30; external benchmark names do not replace task descriptions.
- [x] V0/V1/V2 tests, direct metric CLI, qrel-roster integrity, experiment hashes, plot rendering and manuscript preflight pass; negative BM25 and WAND results remain visible.
- [x] Chapter, lab, solutions, code/tests, qrels, experiment record, visual source/renderings, glossary, references, V2 note and this review are included in one Chapter 9 change.
