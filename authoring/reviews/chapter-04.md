# Chapter 4 authoring review and completion checklist

**Reviewed:** 2026-09-29. **Artifacts:** [chapter](../../chapters/chapter-04-what-an-llm-does-with-supplied-context.md), [lab](../../labs/chapter-04/LAB.md), [solutions](../../solutions/chapter-04-solutions.md), [V0 context-probe note](../../projects/V0/CHAPTER_04_CONTEXT_PROBES.md), [probe code](../../projects/V0/context_probes.py), [manifest](../../projects/V0/chapter-04-case-manifest.json), and [visual sources](../../visuals/chapter-04/figure-04-01-prompt-to-claims.mmd). **Decision:** ready as the model-context prerequisite before lexical indexing and later grounded generation. No model output was fabricated or presented as a measured result.

## Technical accuracy review

- The V0 [engine](../../projects/V0/engine.py) and Chapter 1 evidence contract remain unchanged. The sidecar checks `support-team` eligibility before selecting source IDs, preserves `D1 §3` and `D2 §2` in the controlled prompt families, excludes `D10`, and labels `P1` as a new lab-only snapshot. The default prompt renderer is checked against V0's `build_prompt()` format.
- The ten-case manifest contains three position, two conflict, two trusted-instruction, two untrusted-instruction and one missing-amendment case. The position cases contain the identical five IDs, 67 source words and 809 prompt characters; only order and prompt hash change. `conflict-neutral` and `conflict-stale` each contain 67 source words but 813 versus 809 characters, and the manuscript states that actual model-token counts remain unknown. The negative control has only `D1` from the two required spans.
- The manifest carries snapshot, scope fixture, context and required-evidence IDs, instruction version, word/character counts and prompt hash. It excludes raw question/excerpt/prompt text and records `model_name`, `model_token_count` and `model_result` as `null`. Explicit local preview is restricted to fictional sources. A hash detects changed bytes; it is not evidence support or a security guarantee.
- The generation factorization is valid for a fixed output-token sequence: `0.8×0.7=0.56` is a toy path probability, not correctness. The simplified attention equation includes scaling, softmax and a causal mask; logits `0, ln 3` produce `1/4,3/4`. The hypothetical budget gives `4096−512−240−40−64=3240`, and 3,500 excerpt tokens exceed it by 260. The fictional contract calculation remains `4−1=3` hours and `3/4=75%`.
- Figure 4.01 is a **conceptual source-to-claim path**: V0's actual stub uses two narrow pre-answer quote checks rather than a general post-generation verifier, as the caption states. Eligibility precedes search and content exposure; candidates, selected excerpts, proposed claims and supporting spans are separate. Figure 4.02 shows an application, tokenizer, autoregressive decoder and decoding rule in the correct causal order. Both Mermaid sources were rendered to SVG and PNG and visually inspected; the first was changed from a too-wide layout to a readable vertical flow.
- Primary papers were checked for the limited architecture, in-context learning, instruction-following, long-context position and indirect-injection claims recorded in [REFERENCES.md](../../REFERENCES.md). The chapter explicitly limits transfer from a paper's tested models to any chosen production model. It contains no current vendor capacity, pricing or quality claim.

## Pedagogical review

- The chapter begins with V0's realistic failure: correct `D1`/`D2` excerpts can coexist with stale FAQ, observed incident and unsigned draft, while a general generator can still misuse them. It explains tokenization, conditional generation, attention and decoding before discussing model behavior and operational choices.
- The attention example, token-budget ledger, ordered context table and claim-support table each answer a distinct learner question. The text repeatedly distinguishes prompt capacity from use, attention from authority, citation string from support, faithfulness from dated correctness, and source data from trusted instructions.
- The lab is complete without model access: code produces controlled stimuli, learners calculate mechanisms and grade explicitly fictional response cards. A real-model extension specifies versions, actual token counts, controls, repeated runs, protected outputs and uncertainty. The solutions do not invent position-effect or injection-success rates.
- The visual audit chose one bounded source/claim flow and one generation-loop diagram. Exact comparisons remain Markdown tables. A numerical plot is **N/A** because there are no measured LLM outcomes; plotting imagined quality curves would mislead. An illustration is unnecessary for exact roles and arrows.
- The project update is a diagnostic sidecar. It preserves V0's deterministic answer baseline and the roadmap's later generator introduction, while making candidate, context and claim failures inspectable now.

## Chapter completion checklist

### Learning and mechanism

- [x] A possible stale answer despite retrieved governing clauses motivates the chapter; Chapters 1–3 and V0 are explicit prerequisites.
- [x] Token, prompt, attention, decoding, context window, trust and adaptation terms are defined in the manuscript and [glossary](../../GLOSSARY.md), with mental-model limits.
- [x] Source preparation, query-time eligibility, retrieval, context, model input and claim review are separated in prose and Figure 4.01.
- [x] Conditional-token, attention, capacity and dated-contract calculations state assumptions, units and edge cases.
- [x] The token loop and sidecar prompt generator are transparent from-scratch mechanisms before any production framework or provider interface.
- [x] Model-token budget and possible input/output costs are bounded; no character proxy is passed off as a real bill or capacity limit. Real-model latency and cost are **N/A** until a model is actually run.
- [x] In-context examples, fine-tuning, continued pretraining, retrieval and tools are compared by their mechanism, freshness, provenance and permission trade-offs; misconceptions and later dependencies are explicit.

### Evidence and operation

- [x] The optional model experiment specifies question, hypothesis, baseline, independent variable, frozen source/question/required spans, controls, metrics, procedure, error analysis and limits. Results are correctly recorded as **unmeasured**; fictional response cards provide a complete no-model exercise.
- [x] Candidate, context, generated claims, claim support and end-to-end answer status remain separate; stale, missing and injected cases are inspected.
- [x] V0-level safe manifest fields, version/hash controls, stage diagnosis and required future model usage fields are taught. Production events and cost ledger are **N/A** because this sidecar runs no service, ingestion or paid model.
- [x] Position, conflict, trusted/untrusted instruction and missing-amendment probes expose distinct failures; no general model-quality claim is made.
- [x] Eligibility and source trust are enforced outside prompt wording; fictional raw previews are explicit and real prompt/output retention needs access controls.

### Visual and practice

- [x] The visual audit records why two diagrams and exact tables teach this chapter; no unmeasured plot or decorative illustration is used.
- [x] Both figures have number, title, takeaway caption, alt text, chapter association, editable `.mmd` and rendered SVG/PNG. Plot code/data and illustration prompt are **N/A** because those media are unused.
- [x] Diagram arrows, gate order, role labels and causal loop were compared with code and prose; PNGs were inspected for legibility and grayscale-independent labels.
- [x] Mechanism arithmetic, claim-review and design/debugging exercises, project sidecar and separate solutions are present.
- [x] Active recall, observable “You understand this chapter if you can…” abilities and primary further reading are present.

### Release hygiene

- [x] Local links, 57-chapter numbering and prerequisites were audited; Chapter 5 content was not authored.
- [x] Primary references and date were verified; no unstable frontier result was promoted into a universal claim.
- [x] Seventeen V0/probe behavior tests passed; ten-case manifest invariants and both diagram renders were checked. Negative and unmeasured outcomes remain explicit.
- [x] Chapter, lab, solutions, code, tests, manifest, figures, glossary, references, project note and this review are committed in one Chapter 4 change.
