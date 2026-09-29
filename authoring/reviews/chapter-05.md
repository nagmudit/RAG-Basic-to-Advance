# Chapter 5 authoring review and completion checklist

**Reviewed:** 2026-09-29. **Artifacts:** [chapter](../../chapters/chapter-05-text-normalization-and-inverted-indexes.md), [lab](../../labs/chapter-05/LAB.md), [solutions](../../solutions/chapter-05-solutions.md), [V1 project snapshot](../../projects/V1/README.md), [index code](../../projects/V1/lexical_index.py), [experiment record](../../projects/V1/chapter-05-experiment.json), and [visual sources](../../visuals/chapter-05/figure-05-01-from-documents-to-postings.mmd). **Decision:** ready as the indexed lexical prerequisite for Chapter 6. Chapter 6's TF-IDF and Chapter 9's judged retrieval are intentionally not implemented here.

## Technical review

- The V0 corpus, `Engine.run()`, frozen questions, expected source clauses and answer stub are unmodified. The V1 default analyzer calls V0's tokenizer, and V1 keeps the distinct-term overlap score and V0's numeric document/section/segment tie break. Tests compare exact top-k `(segment ID, score)` and complete two-task answers at depths 1, 2 and 8.
- The index retains original segment dictionaries as its forward store, field-local positional postings, analyzed title/body lengths, snapshot/analyzer versions, and static scope membership. The five-record hand table was checked against executable postings: `hx-7a` at S1:2, S2:2, S3:1, S5:0; `guide` at S1:4, S3:3, S4:5. Term frequency is occurrence count; `df=4` uses segments as the unit, not four relevant whole documents.
- Boolean AND/OR/anchored NOT and phrase queries are verified, including a repeated-term phrase and a title/body non-crossing case. The diagram says “intersect eligible IDs” because the teaching code uses sets; sorted two-cursor merge is explained as the next implementation mechanism. A phrase means adjacent analyzed terms, not an exact byte substring.
- `unicode_nfc` composes canonical forms and applies Python case folding; the version includes the runtime Unicode-data version. It still lacks language-specific segmentation. `HX-7C` and `resett` return no exact match. The chapter treats stop words, stems, lemmas, n-grams and fuzzy matching as choices with possible information loss, not implemented magic. Unicode NFC/NFKC, case folding, Boolean intersection and positional matching claims were checked against primary Unicode, Python and Stanford IR sources in [REFERENCES.md](../../REFERENCES.md). Versioned Lucene API pages support only the production mapping, not an equivalence of internal implementations.
- Eligibility is checked before candidate score accumulation or forward-text fetch. A legal-only `S5`/`D10` posting can exist inside the service, but support-facing candidates, prompts and normal traces exclude it. Tests cover `D10` and missing `D2`. The code's caller-provided scope is explicitly a local fixture, not authentication; static scope membership would need immediate policy/cache invalidation on a revocation.
- The experiment changes only the search algorithm under the V0 analyzer and checks exact candidate/score equality before timing. Its JSON retains source and code hashes, query-set version, seed, runtime/platform, raw samples, nearest-rank p95, work counts and separate one-run build cost. The 13/130/1,300 segment corpora are deterministic source copies, not new judgments. The common contract query scores every eligible segment; this counterexample is preserved in the manuscript and solutions. Nine sequential local timings do not support a production p95, speed guarantee or end-to-end answer-quality claim.
- The two Mermaid figures were rendered to SVG and PNG and inspected at normal reading size. Figure 5.01 separates index-time postings, forward and scope stores; Figure 5.02 shows a query-time scoped Boolean example. Exact positions and computed work counts use tables. No quantitative plot is warranted by this small, noisy timing experiment: the raw samples are preserved for readers to plot if useful, while a smooth growth curve would overstate precision.

## Pedagogical review

- The chapter starts from V0's repeated full scan, then builds analyzer → term → posting → Boolean/phrase search before introducing query-time complexity. It distinguishes a term from raw text and a model token, a posting from an eligible candidate, and a candidate from evidence.
- The five-record fixture allows every posting, phrase and access decision to be checked by hand. The rare code, genuinely misspelled word, canonically equivalent accent, common term, restricted record and missing amendment expose different failure mechanisms. `S5` is a deliberate trust test rather than a final-answer-only filter.
- The implementation demonstrates the actual V1 preview; TF-IDF, compression, mutable indexes and formal qrels are reserved for their prerequisite positions. The lab asks for predictions before running code, a hand cursor trace, an analyzer collision policy, a reproducible experiment card, and two stage-local debugging arguments. Solutions give calculations and uncertainty rather than a blanket “index faster” conclusion.
- The project continues the same source/answer contract. Search work, candidate IDs, context IDs and supporting evidence IDs remain separate in the request record; index build time is not silently added to per-request latency.

## Completion checklist

### Learning and mechanism

- [x] V0 full-scan failure, simpler baseline and Chapters 2–4 prerequisites are explicit.
- [x] Analyzer, normalization, vocabulary, posting, position, Boolean/phrase, forward store and length terms are defined in chapter and glossary with limits.
- [x] Index time and query time, field and source provenance, candidate and evidence are traced separately.
- [x] Hand positions, `df=4`, AND intersection and `O(p+q)` cursor bound state units/assumptions; no unsupported O(1) search claim.
- [x] Pseudocode and standard-library from-scratch index/query implementation precede production internals.
- [x] Build, posting visits, scored segments, timing, storage growth and permission-update cost are bounded or measured at the chapter's maturity.
- [x] Analyzer alternatives, failure cases, security trade-offs and Chapter 6/8/9 dependencies are explicit.

### Evidence and operation

- [x] Experiment records question, hypothesis, V0 baseline, algorithm variable, controls, synthetic corpus, four frozen query IDs, exact-agreement invariant, timing/work metrics, raw samples, error analysis and limits.
- [x] Candidate parity is checked separately from context and deterministic answer parity; no general generation or end-to-end quality is claimed.
- [x] Index/analyzer/snapshot versions and redacted request work/latency fields are present; ingestion events, model tokens, cost ledger and production dashboards are **N/A** because this is a local static index without ingestion service or model.
- [x] Rare/common/no-result, misspelling, Unicode, missing-amendment and restricted-source probes are retained.
- [x] Authorization, source trust, private index access and revocation risk are discussed; the fixture contains no real private text.

### Visual and practice

- [x] Visual audit chooses two small flow diagrams for the index/query boundary and Markdown tables for exact postings and measurements; a plot is **N/A** because this local timing sample does not establish a stable curve.
- [x] Each figure has number, title, takeaway, alt text, chapter association, editable `.mmd`, SVG and PNG. Plot source and illustration specification are **N/A** because those media are unused.
- [x] Diagram arrows, S1–S5 postings, S5 scope exclusion and query operation match the code/prose; PNGs were visually inspected and labels survive grayscale.
- [x] Worked trace, debugging/design exercise, V1 preview and separate solutions are present.
- [x] Active recall, observable mastery abilities and primary further reading are present.

### Release hygiene

- [x] Local links, syllabus number, project version and prerequisite references resolve; Chapter 6 content was not authored.
- [x] Primary sources and time-sensitive runtime/data claims were checked on the review date; vendor claims and frontier papers are **N/A**.
- [x] V1 and V0 behavior tests, exact experiment agreement, manifest hashes, raw samples and diagram renders reproduce; noisy and limited outcomes remain explicit.
- [x] Chapter, lab, solutions, code, tests, fixture, experiment, diagrams, glossary, references, roadmap links and this review form one Chapter 5 change.
