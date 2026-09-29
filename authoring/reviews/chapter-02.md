# Chapter 2 authoring review and completion checklist

**Reviewed:** 2026-09-29. **Artifacts:** [chapter](../../chapters/chapter-02-build-the-first-rag-loop.md), [lab](../../labs/chapter-02/LAB.md), [solutions](../../solutions/chapter-02-solutions.md), [V0 code and corpus](../../projects/V0/README.md), [result record](../../projects/V0/RESULTS.md), and [visual sources](../../visuals/chapter-02/figure-02-01-preparation.mmd). **Decision:** ready as a foundational, model-free retrieval-loop chapter. Chapter 3 has not been authored.

## Technical review

- The Chapter 1 source contract is preserved: `D1` contains both `§3` and `§8`; `D2 §2` is the signed, effective replacement; `D3` is stale. Ten documents contain eleven named sections. The default 24-word preparation yields thirteen segments, including three non-overlapping windows from `D4`. The `D4` first boundary divides “service configuration.”
- The tokenizer and score in prose match the code: lowercase ASCII-oriented terms, an internal hyphen retained, distinct-term intersection of query and title-plus-window text. The four-term hand calculation gives 4 for `D1`, `D2`, `D3`, `D7` and `D9`, and 3 for `D5`. On the full frozen contract question, the first two scores are `D2=7` and `D1=6`. The tie rule is deterministic and is not represented as relevance or authority.
- Eligibility precedes scoring and the ordinary trace. The `support-team` scope excludes `D10`; making `D2` inaccessible also removes it before the prompt and forces abstention. This is a local simulation with caller-supplied scope, not authentication.
- The stub checks exact clauses **inside selected context**. For the frozen contract question, depth one gives 1/2 required spans and abstains; depth two gives 2/2 and answers with both citations. For the termination question, depth two omits `D1 §8`, while depth three returns the clause. Removing `D2`, using an empty context budget, and breaking the amendment into eight-word windows each lead to the diagnosed abstention. The calculation `4 − 1 = 3` hours and `3/4 = 75%` is correct.
- The request record contains request/query IDs, UTC timestamp, source snapshot, raw candidate scores, context and evidence IDs, eligible scan count, stage and wall milliseconds, status and reason. It omits raw question and excerpt text. The fixed request ID, approximate character-based token estimate, no-result code and local prompt preview are identified as teaching limits. The result record retains five failure examples and labels single-sample latency as non-generalizable.
- Complexity describes the implemented scan, repeated tokenization, sort and retained candidates. The text does not claim benchmark latency, provider token accuracy, general temporal resolution, legal interpretation, LLM answer quality or a production authorization policy.
- Two Mermaid diagrams were rendered to SVG and PNG and visually inspected. Figure 2.01 matches preparation before requests; Figure 2.02 shows eligibility before scoring and separates `build_context()` from `build_prompt()`. Both keep candidates, selected context and evidence conceptually separate. Tables carry exact numerical comparisons more clearly than a plot would.
- The official Stanford IR and Python standard-library sources were checked for the limited claims recorded in [REFERENCES.md](../../REFERENCES.md). No unstable frontier or product-performance claim was promoted into the chapter.

## Pedagogical review

- The opening inherits Chapter 1's missing-evidence failure and turns its manual trace into an executable path. The brief Python primer gives only the data structures required here. Terms, index/preparation time, query time, source identity, score, ranking, context, stub and trace appear before they are used in harder explanations.
- A worked score, executable pseudocode, code, a source-boundary failure, a candidate-depth experiment and a trace-led failure table teach distinct steps. The text states what the simple mental model cannot decide: semantic relevance, governing authority, model faithfulness, real token count and production permissions.
- The lab requires an independent ten-document implementation and hand calculation before looking at the reference. Separate solutions report exact rankings and negative outcomes. Recall prompts, design and debugging questions, a project upgrade and observable mastery abilities are included.
- The first evaluation record distinguishes candidates, supplied context, cited evidence and answer status. The one-question depth comparison is explicitly a hand audit; general qrels and retrieval metrics remain a later prerequisite. The preserved termination counterexample prevents a universal “top two is enough” inference.
- The visual-teaching audit chose sequence diagrams for stage order and source lineage, and Markdown tables for scores and experiment outcomes. A plotted latency curve would imply precision unsupported by the tiny single-sample measurements; a generated illustration would be less exact than the diagrams.

## Chapter completion checklist

### Learning and mechanism

- [x] The Chapter 1 missing-amendment and source-only tasks motivate V0; the simpler manual trace and prerequisites are explicit.
- [x] New terms are defined in the chapter and [glossary](../../GLOSSARY.md); the overlap and stub mental models include their limits.
- [x] Preparation and request data movement, including source labels and eligibility, are traced separately.
- [x] The score equation, assumptions, units and edge cases have a hand-worked six-source example; the dated target reduction is checked.
- [x] Pseudocode and a standard-library implementation expose the complete local mechanism before service abstractions.
- [x] Scan, sort and memory growth are bounded; latency is measured but the tiny sample is not over-interpreted; prompt and model-cost limits are explicit.
- [x] Alternatives, future prerequisites, trade-offs and common misconceptions are stated without requiring later methods to understand V0.

### Evidence and operation

- [x] The depth experiment identifies hypothesis, baseline, independent variable, controls, frozen snapshot/question/required spans, context-coverage denominator, procedure, results, failure, conclusion and limits.
- [x] Candidate, context, evidence and answer observations are separated, with preserved negative probes.
- [x] A UTC timestamp, snapshot, IDs, scores, stage and wall timings, status and reason provide V0-level observability; no unsupported cost estimate is presented.
- [x] Missing-source, no-result, lexical mismatch, segmentation, budget, ranking and access probes localize failures; later production implications are correctly bounded.
- [x] Scope filtering, source authority, prompt/source trust and trace privacy are checked; caller-supplied scope is explicitly identified as a simulation.

### Visual and practice

- [x] The visual audit records why two sequence diagrams and exact tables are used; no plot or generated illustration serves this tiny deterministic example better.
- [x] Both figures have numbers, titles, takeaway captions, alt text, chapter association, editable `.mmd` sources and rendered SVG/PNG alternatives. Plot code/data and illustration prompts are **N/A** because neither medium is used.
- [x] Diagram ordering, labels, source count, segment count and index/query boundaries were compared with code and prose; PNGs were visually inspected for legibility.
- [x] The lab, separate solutions, design/debugging questions and V0 project update are present.
- [x] Active recall, observable “You understand this chapter if you can…” abilities and verified further reading are present.

### Release hygiene

- [x] Local Markdown links, chapter references, prerequisites and project-version references were checked; no Chapter 3 manuscript or V1 implementation was started.
- [x] Primary-source scope and writing date are registered; the corpus and query labels are explicitly fictional and frozen.
- [x] Ten V0 behavioral tests passed; diagrams rendered; deterministic results and negative cases are retained with measurement limits.
- [x] Chapter source, visual source and renders, lab, solutions, corpus, tests, result record and this review are committed in the same Chapter 2 change.
