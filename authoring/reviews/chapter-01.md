# Chapter 1 authoring review

**Reviewed:** 2026-09-29. **Artifact:** [Chapter 1](../../chapters/chapter-01-a-question-a-model-and-missing-evidence.md). **Result:** technical and pedagogical reviews pass for a foundational orientation chapter.

## Technical accuracy review

- Fictional corpus uses `D1` agreement v1 (2025-01-01), `D2` amendment signed 2026-05-12 and effective 2026-05-15, and `D3` FAQ captured 2026-05-10. On the 2026-05-20 query date, `D1 §3` supports the old target and `D2 §2` the replacement; `D3` is stale for the current target. V0 keeps `D1 §8` under the same document ID.
- Arithmetic checked: `4 − 1 = 3` hours; `3 / 4 = 0.75 = 75%`. The text says **response target**, not observed response time.
- The source-backed answer cites both facts; candidate, evidence, claim and citation remain distinct. The inaccessible-amendment path excludes content before answer or ordinary-log exposure.
- The embedded Mermaid block exactly matches the editable `.mmd` source. SVG and PNG were rendered with the installed Mermaid CLI and visually inspected. Arrow direction, before-question/query-time lanes, eligibility before search, and candidate/evidence boundaries agree with the prose.
- `source_trace.py` executed successfully. A bad span raises `ValueError`; an ineligible candidate raises `PermissionError`. The code labels its result `locators_verified` and explicitly leaves semantic claim support to separate review.
- Primary source pages used for the query/information-need distinction, historical RAG framing and TREC judgments were checked on the review date. [Source register](../../REFERENCES.md).
- All local Markdown links resolved in the repository audit. No tool/vendor capability claims require a current implementation comparison in this chapter.

## Pedagogical review

- The motivating failure precedes terminology; every new term needed for the worked case is defined before use. Later concepts are previews with chapter pointers, not prerequisites.
- The chapter separates model parameters, prompt context and external sources; treats retrieval as knowledge access; and compares direct transformation, calculation, source-only search, structured lookup, live lookup and cited synthesis.
- The worked case shows a stale candidate, current amendment, arithmetic, an answerable path, missing evidence and an authorization boundary. The one-variable paper experiment states its metric and its narrow limitation.
- Figure 1.01, two exact comparison tables, the case trace, 15 classification problems, separate solutions, oral design questions, active recall and the observable mastery test each answer a distinct teaching need.
- The V0 brief preserves a frozen source snapshot, queries and expected evidence for Chapter 2. It states that no retriever has been implemented yet.

## Checklist items adapted for this chapter

- A numerical performance plot and generated conceptual illustration are **N/A**: Chapter 1 has no measured numerical curve, and the exact pipeline is clearer in Mermaid.
- A search algorithm, ranking formula and full from-scratch retriever are **N/A** here: Chapter 2 builds literal search, while Chapters 5–9 teach its internals and metrics. The optional executable artifact checks source locators and eligibility without pretending to retrieve or judge semantic correctness.
- Concrete production stack, distributed trace, cost ledger and SLO are **N/A** for this prerequisite-free opening chapter. It introduces the required identity, version, latency and privacy questions; implementation grows under the project and observability contracts.
- A model-quality result is **N/A**: the chapter’s controlled comparison is a hand-audit of evidence availability, not an LLM benchmark. It explicitly names this limitation.
