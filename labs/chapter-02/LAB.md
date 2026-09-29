# Chapter 2 lab — A complete first search-to-answer loop

**Prerequisite:** [Chapter 1](../../chapters/chapter-01-a-question-a-model-and-missing-evidence.md), its [V0 evidence contract](../../projects/V0/README.md), and [Chapter 2](../../chapters/chapter-02-build-the-first-rag-loop.md). **Estimated time:** 2–3 hours. Use only the Python standard library. The [reference engine](../../projects/V0/engine.py) and [separate solutions](../../solutions/chapter-02-solutions.md) are available for comparison after your first attempt.

The deliverable is a ten-document local search loop with source labels, an explicit abstention rule and one structured trace per request. It must preserve the Chapter 1 contract: `D1 §3` and `D2 §2` are both required for the dated change; `D1 §8` is the termination clause; `D10` is not eligible for a `support-team` request. A fluent sentence is not evidence that these boundaries were honored.

## A. Inspect and prepare the source snapshot

1. Open [corpus.json](../../projects/V0/corpus.json). Count documents and named sections. Explain why the original agreement’s `§3` and `§8` share document ID `D1`.
2. Give two reasons to retain `version` and `source_span` on every derived segment. What does `support-corpus-2026-05-20` identify?
3. Implement `load_corpus()` and `segment_corpus()` independently, or reimplement their behavior in a small scratch file. Split each named section into non-overlapping windows of at most 24 whitespace-separated words. Retain document ID, title, version, scope, section label, text and start/end word offsets. Count the resulting segments.
4. Inspect `D4:step-4:0` and `D4:step-4:1`. Record the two words split by their boundary and explain one answer or retrieval error this could cause.

**Python reminder:** a list preserves the source order; a dictionary gives each segment named fields; `for` visits each document and section; `words[start:start + 24]` takes a window. The segment ID must distinguish two windows from one section.

## B. Build and hand-check literal search

1. Implement the V0 tokenizer and score: lowercase ASCII letter/digit terms, keeping an internal hyphen such as `Sev-1`; one point for each **distinct** query term present in the segment title or text. Filter by allowed scope *before* scoring.
2. For `Helios Pro Sev-1 target`, write the set of four query terms. Fill in the score and justification for `D1 §3`, `D2 §2`, `D3 FAQ-7`, `D5 §3`, `D7 timeline` and `D9 proposal-2`. Which tied records would be unsafe to treat as governing evidence, and why?
3. Sort by descending score, then numeric `D` number, section order and window number. Keep positive-score top `k`. Compare your first eight candidate IDs for `q-contract-change` with the reference engine. State why deterministic tie-breaking improves reproducibility without improving relevance by itself.
4. Use a query with no shared terms (for example, `zymurgy`). Report candidates and the meaning of “no result” under this tokenizer.

## C. Build the prompt, answer stub and trace

1. Greedily pack ranked candidates under a 120-word **source-text** budget. Preserve `[document ID version span]` before each excerpt. Do not call every context excerpt “evidence.”
2. Write a narrow stub for the two frozen query IDs. The dated change must require exact `D1 §3` and `D2 §2` clauses **inside the packed context**. The termination query must return `D1 §8` from context. Missing required text leads to abstention. Compute `4 − 1` hours and `(4 − 1)/4` only after both contractual values are present.
3. Emit a structured request record containing request/query IDs, UTC timestamp, snapshot, candidate IDs and raw integer scores, context IDs, evidence IDs, eligible segments scanned, status, reason, search/context/stub/wall milliseconds and an explicitly approximate prompt-token estimate. Keep question and source text out of the ordinary record.
4. Inspect the prompt locally. Explain why the label `D3 FAQ-7` in context does not make its stale four-hour summary a governing source for the current target.

If you want to inspect the finished reference behavior without reading its code yet, run from the repository root:

```powershell
python -X utf8 projects/V0/engine.py --top-k 2
python -X utf8 projects/V0/engine.py --query-id q-termination --top-k 3
```

The CLI’s `--scope` is a teaching control, not authentication. Treat any custom scope in this lab as a simulation of already-verified permissions.

## D. Controlled probes and failure localization

Run or reproduce each change **one at a time**, keeping the other settings fixed. Record the first failing boundary: source preparation, eligibility, search/rank, context packing, stub, or answer verification.

| Probe | Command or change | Record |
|---|---|---|
| Candidate depth | `--top-k 1`, then `--top-k 2` on `q-contract-change` | Candidate, context, evidence IDs; answer status |
| Source absent | `--drop-document D2` | New snapshot ID; first stage where `D2` is absent |
| Tiny context | `--context-budget-words 5` | Candidate IDs versus context IDs |
| Small windows | `--window-words 8 --top-k 20` | Whether `D2` fragments are retrieved; whether full quote survives |
| Source-only search | `--query-id q-termination --top-k 2`, then `3` | Position of `D1 §8`; answer status |
| Lexical mismatch | `--question "What became of the urgent incident pledge?"` | Top candidates; whether the amendment appears |
| Eligibility | Search with `support-team` scope | Whether `D10` appears in candidates, context, prompt or ordinary trace |

Do **not** log the raw prompt from a real private corpus. This lab’s sources are fictional, and `--show-prompt` is a local inspection aid only.

## E. Report an experiment rather than an impression

Use the [experiment contract](../../evaluation/EVALUATION_EXPERIMENT_CONTRACT.md) to compare `top_k=1`, `2` and `8` on the unchanged contract question. State the question, hypothesis, baseline, independent and controlled variables, corpus/query IDs, hand-labeled required evidence, metric and denominator, procedure, results, error analysis, conclusion and limits. Your main quality observation is required-evidence coverage **in context** (`0/2`, `1/2` or `2/2`) plus answer/abstain status. Include measured wall time from your runs, but do not interpret one or two sub-millisecond measurements as a reliable performance difference.

Then compare 24-word and 8-word windows. Is a retrieved `D2` fragment enough for the exact stub? Explain the failure using candidate, context and evidence IDs separately.

## F. Design and explain

1. What is the largest source collection for which you would be comfortable scanning and re-tokenizing every segment on every request? Your answer should state a latency target and workload assumption, not a universal document count.
2. Propose one safe way to test whether the answer’s citations point to the versions and spans that reached context. What would the test still fail to prove?
3. If you optionally connect a real LLM, keep eligibility filtering and source labels outside the model. Save prompt/model version, review answer claims against the spans, and compare with the deterministic stub. Do not treat an attractive generated answer as a success metric without judgments.

## Submission and review rubric

Submit code, a frozen corpus/query manifest, two normal request traces, the probe table, the experiment card and a paragraph explaining one negative result. A passing submission filters `D10` before scoring, keeps `candidate_scores`, `context_ids` and `evidence_ids` distinct, abstains without `D2`, returns `D1 §8` at sufficient depth, and reports measured latency with its limits. The supplied [behavioral tests](../../projects/V0/test_engine.py) check the reference implementation; use them to understand expected boundaries, then inspect your own implementation’s trace rather than copying output blindly.
