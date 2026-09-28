# Chapter completion checklist

Use this before declaring a chapter complete. Mark an item **N/A with one reason** when it has no pedagogical role; do not add empty sections. The authoritative policies are [teaching philosophy](TEACHING_PHILOSOPHY.md), [observability](observability/OBSERVABILITY_CONTRACT.md), [evaluation/experiments](evaluation/EVALUATION_EXPERIMENT_CONTRACT.md), and [visual assets](visuals/VISUAL_ASSET_CONTRACT.md).

## Learning and mechanism

- [ ] Failure or information need motivates the chapter; simpler baseline and prerequisites are explicit and already taught.
- [ ] Terms are defined and added to the glossary; intuition, mental model and its limits are clear.
- [ ] Internal mechanics and data movement are traced; index-time and query-time behavior are separated where applicable.
- [ ] Mathematics, assumptions, units, edge cases and a hand-worked numerical example are included where useful.
- [ ] Algorithm/pseudocode and a small from-scratch implementation are included where useful, before production abstractions.
- [ ] Complexity, latency, memory/storage and cost are quantified or bounded appropriately.
- [ ] Alternatives, trade-offs, connection to earlier chapters, next dependency and misconceptions are explicit.

## Evidence and operation

- [ ] Experiment states question, hypothesis, baseline, variable/controls, corpus, frozen questions/qrels, metrics, procedure, results, error analysis, conclusion and limitations where useful.
- [ ] Evaluation distinguishes candidate retrieval, selected context, generation and end-to-end outcome; failure examples are inspected.
- [ ] Logs, metrics, traces, events, versions, cost and failure localization are taught at the chapter's maturity level where applicable.
- [ ] Debugging probes and negative/contradictory examples are included; production implementation and scale implications are accurate.
- [ ] Authorization, source trust, privacy, retention and security implications are checked where relevant.

## Visual and practice

- [ ] Visual-teaching audit identifies concepts that need figures; chosen medium serves the learner question.
- [ ] Each substantial figure has number, title, takeaway caption, alt text, chapter and editable source; plots have code/data/units; generated illustrations have prompt/specification.
- [ ] Diagram arrows, ordering, labels, formulas, values, parameter names and index/query boundaries agree with code and prose; readability and accessibility checked.
- [ ] Worked exercise, debugging/design/interview question, running-project upgrade and separate solutions are present as appropriate.
- [ ] Active-recall prompts or flashcards, “You understand this chapter if you can…” abilities, and further reading are present.

## Release hygiene

- [ ] Chapter and project links resolve; numbering and prerequisites are current; no old terminology survives.
- [ ] Primary references, datasets, model/tool versions and time-sensitive claims are verified for the writing date; frontier claims stay in the frontier register until promoted.
- [ ] Code, plots, labs and judgments reproduce; negative results and limitations are retained.
- [ ] Chapter source, visual source, lab artifacts, evaluation data and project snapshot are committed together when they exist.
