# Chapter 2 lab — Worked solutions and expected observations

Attempt the [lab](../labs/chapter-02/LAB.md) before reading this file. The full [V0 reference engine](../projects/V0/engine.py) is one implementation of the mechanism, not a framework or a general QA system. Values below assume the checked-in [corpus](../projects/V0/corpus.json) and default 24-word windows; wall-clock timings vary by run.

## A. Corpus and segmentation

There are **10 document IDs** and **11 named source sections**: `D1` contributes two sections, while every other document contributes one. With 24-word non-overlapping windows, the longer `D4 step-4` section contributes three segments, so the prepared list contains **13 segments**. `D1 §3` and `D1 §8` share an ID because they are locations in the same agreement version. Giving them separate document IDs would break document-level provenance and make update/delete behavior ambiguous.

Version and span are required to distinguish amended text and to check that an answer citation points to the text actually seen. The snapshot identifies the frozen set served by a request. The `D4` boundary splits **“service configuration”**: window 0 ends with `service`, window 1 begins with `configuration,`. A single retrieved window may lose the intended phrase or a condition that crosses the boundary. Increasing overlap or using sentence-aware boundaries is a later design choice, not a silent fix in V0.

## B. Term overlap and ordering

`Helios Pro Sev-1 target` becomes `{helios, pro, sev-1, target}`. With one point per distinct shared term in title plus segment text:

| Segment | Score | Explanation |
|---|---:|---|
| `D1:§3:0` | 4 | Title provides `helios`, `pro`; clause provides `sev-1`, `target`. |
| `D2:§2:0` | 4 | Same four terms; signed amendment. |
| `D3:FAQ-7:0` | 4 | Same four terms; stale FAQ. |
| `D5:§3:0` | 3 | `helios`, `sev-1`, `target`, but **Basic** rather than Pro. |
| `D7:timeline:0` | 4 | Same four terms; describes an observed incident, not the contractual target. |
| `D9:proposal-2:0` | 4 | Same four terms; unsigned proposal. |

The ties prove only that this scoring function cannot discriminate authority. Sorting by numeric document ID puts `D1`, `D2`, `D3`, `D7`, `D9` in that order for this four-term query. It makes repeated runs comparable; it does not decide which clause governs.

For the full frozen `q-contract-change`, the default reference top eight are `D2:§2:0` (7), `D1:§3:0` (6), `D3:FAQ-7:0` (6), `D7:timeline:0` (6), `D9:proposal-2:0` (6), `D5:§3:0` (5), `D8:§3:0` (5), and `D4:step-4:1` (4). This list is tied to the exact tokenizer, title inclusion and snapshot. `zymurgy` gives zero positive-score candidates; the result means no literal match under this program, not that no relevant source exists.

## C. Context, stub and telemetry

With `top_k=2` and the default 120-word budget, the context contains `D2:§2:0` and `D1:§3:0`. The stub checks both complete quotes **in context**, returns the four-to-one-hour change, and sets `evidence_ids` to those two segments. The percentage is `(4 − 1)/4 = 3/4 = 75%`; the absolute reduction is three hours. With `D2` absent, the stub abstains even though `D1` and the stale `D3` may be present.

The default `top_k=8` context also contains the FAQ, incident and draft. They are **context candidates**, not automatically evidence for the dated answer. The narrow stub ignores them. A real generator might not, so their presence is a quality risk requiring later evaluation.

A correct trace records IDs, a UTC timestamp, scores, snapshot, stage durations, status and reason. It excludes the raw question and excerpt text; `--show-prompt` displays those only as a local inspection action. `estimated_prompt_tokens` is a character-based proxy and cannot be used to enforce a provider limit. The `--scope` flag exercises the local filter but does not authenticate a person.

## D. Failure probes

| Probe | Expected result | First responsible boundary |
|---|---|---|
| `top_k=1` contract question | Only `D2 §2` survives; context coverage 1/2; abstention | Candidate depth/ranking |
| `top_k=2` contract question | `D2 §2` and `D1 §3` survive; coverage 2/2; cited answer | Both required spans supplied |
| Drop `D2` | Snapshot gets `-without-D2`; no `D2` candidate; abstention | Source preparation/availability |
| Word budget 5 | Candidates remain but no full source segment fits; empty context; abstention | Context packing |
| Window 8, depth 20 | `D2` fragments are candidates; no fragment contains the complete clause; abstention | Segmentation/context sufficiency |
| Termination depth 2 | `D1 §8` is below cutoff; abstention | Ranking depth |
| Termination depth 3 | `D1 §8` enters context; exact clause and locator returned | Supported source-only response |
| “urgent incident pledge” | Runbook/incident vocabulary dominates; no required amendment support; abstention | Lexical mismatch |
| `support-team` and `D10` | `D10` is absent from eligible candidates, context and trace | Pre-scoring eligibility gate works for the fixture |

The 8-word-window probe shows why candidate presence is weaker than answerability: a `D2` ID can be present while the required complete source text is unavailable to the stub. It does **not** prove that every real generator would abstain on the same fragments.

## E. Experiment card

**Question:** Does retaining more than one lexical candidate expose both facts needed for the dated comparison? **Hypothesis:** depth one omits `D1 §3`, while depth two includes it. **Baseline:** `top_k=1`. **Independent variable:** `top_k ∈ {1,2,8}`. **Controls:** snapshot `support-corpus-2026-05-20`, query `q-contract-change`, `support-team` scope, 24-word windows, 120-word context budget, tokenizer, score and stub. **Hand-labeled evidence:** `D1 §3` and `D2 §2`. **Metric:** required-evidence coverage in context, denominator 2, plus status. **Procedure:** run each setting and inspect trace lists.

| Depth | Coverage | Status | Error analysis |
|---:|---:|---|---|
| 1 | 1/2 | Abstained | `D1` old target absent from context. |
| 2 | 2/2 | Answered | Both contractual spans present. |
| 8 | 2/2 | Answered | Extra stale/irrelevant context adds no required fact under this stub. |

**Conclusion:** depth two is sufficient for this one frozen task. **Limits:** one query, manually complete evidence labels, a task-specific stub, and noisy tiny-corpus latency. The termination query is a counterexample to a universal depth-two rule. A separate 24-versus-8-word-window comparison changes only the window size; at eight, the exact quote splits and the stub abstains despite `D2` fragments appearing. That is a meaningful negative result.

## F. Design answers

There is no universal safe corpus size for a full scan. Estimate `eligible_segments × terms processed per segment × request rate` on target hardware, then measure against a declared latency objective. If the scan misses that objective, an index is motivated; if it meets it at the required quality and update rate, the simple path may be adequate.

A citation test can require every cited `(document ID, version, span)` to appear in the selected context and require the cited quote to match the source snapshot. That catches missing or mismatched locators, but not an incorrect paraphrase, a wrong calculation or a source that is itself stale or false.

An optional LLM integration should receive only eligible excerpts with source labels, and the application should preserve its prompt/model version and inspect claims. A model-produced sentence cannot replace the manual source judgments used for the frozen tasks; compare both systems on the same questions and failure cases.
