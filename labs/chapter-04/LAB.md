# Chapter 4 lab — From supplied context to supported claims

**Prerequisites:** [Chapters 1–3](../../chapters/chapter-03-data-algorithms-and-measurements-needed-for-search.md), the [V0 evidence contract](../../projects/V0/README.md), and [Chapter 4](../../chapters/chapter-04-what-an-llm-does-with-supplied-context.md). **Estimated time:** 3–4 hours without a real model, plus any optional model runs. The [solutions](../../solutions/chapter-04-solutions.md) are separate. The supplied [probe code](../../projects/V0/context_probes.py) uses only the Python standard library and never calls a model.

You will examine **what enters the prompt** before judging what an answer says. The dated Helios task still requires `D1 §3` and `D2 §2`; `D3 FAQ-7` is stale, `D7` is an observed incident, `D9` is unsigned, and restricted `D10` is ineligible for `support-team`. The lab-only `P1` note is not part of V0's source truth. A candidate, a context excerpt, a claim and verified evidence must remain separate in your report.

## A. Calculate the model-facing mechanism

1. Write the two-token factorization `P(y₁,y₂|x)` and calculate it when `P(y₁|x)=0.8` and `P(y₂|x,y₁)=0.7`. Explain why the result is not a probability that a Helios answer is correct.
2. A toy attention head has two visible scaled logits, `0` and `ln 3`. Compute the unnormalized exponentials and softmax weights. What can the next output position **not** see under a causal mask? Why is the larger weight neither a relevance judgment nor a citation?
3. For a hypothetical 4,096-token combined budget, reserve 512 output tokens, 240 instruction tokens, 40 question tokens and 64 wrapper/label tokens. How many **actual model tokens** remain for excerpts? What if excerpts require 3,500? Explain why V0's source-word budget and character proxy cannot enforce this limit.
4. Locate where V0 counts regex terms, source words and an estimated prompt token proxy. State what additional tokenizer measurement a real-model experiment would need.

## B. Inspect the fixed position experiment

From the repository root, run:

```powershell
python -X utf8 projects/V0/context_probes.py
python -X utf8 projects/V0/context_probes.py --show-prompt position-middle
```

Open the [redacted case manifest](../../projects/V0/chapter-04-case-manifest.json). For `position-front`, `position-middle` and `position-end`, record the ordered `context_ids`, required-evidence IDs, source-word count, prompt-character count and prompt hash. Confirm that the same five excerpts are used and only their order changes. Explain why equal character counts do not certify equal counts under a particular model tokenizer.

Draw [Figure 4.01](../../visuals/chapter-04/figure-04-01-prompt-to-claims.svg) from memory. Mark the earliest stage responsible if `D2` appears in `candidate_scores` but is absent from `context_ids`; mark a different stage if `D2` is in context but the answer asserts the stale four-hour value. Explain what V0's exact stub would do on all three position cases and what that **cannot** tell us about a real model.

## C. Change one prompt factor at a time

1. Compare `conflict-neutral` with `conflict-stale`. Which required evidence remains fixed? Which third excerpt changes? Are the source-word totals equal? Are the prompt-character counts identical? State the remaining model-token and source-label confounds before interpreting any future output.
2. Compare `instruction-base` with `instruction-explicit`. Verify that excerpt IDs and order are identical. Identify the changed **trusted** text and two answer behaviors you would grade. Does a longer instruction prove better faithfulness?
3. Preview `untrusted-neutral` and `untrusted-injected`. Identify the `P1` text that tries to act as a system instruction. Show that `D1`/`D2` still appear and that the injected source uses a labeled lab snapshot. Why must the application keep access checks outside the model even if the prompt says to ignore instructions in sources?
4. Inspect `missing-amendment`. Which required span is absent? What partial statement could still be supported? What current-change statement must be withheld?

Use `--show-prompt` only for this fictional local fixture. The ordinary manifest excludes raw prompt and source text; apply the same separation to real private material.

## D. Review fictional response cards claim by claim

These responses are **authored teaching examples, not outputs measured from a language model**. For each, fill in four columns: answer correctness for the dated task, faithfulness to the specified selected context, citation support, and appropriate abstention/partial-answer behavior. Name the first failure boundary and a regression case to save.

| Card | Selected context | Proposed response |
|---|---|---|
| A | `position-front` | “The original target was four hours [D1 v1 §3]. Signed Amendment A set one hour effective 15 May [D2 signed-2026-05-12 §2], a three-hour or 75% reduction.” |
| B | `position-front` | “The current target is four hours [D3 FAQ-7].” |
| C | `missing-amendment` | “The target changed from four to one hour effective 15 May [D2 §2].” |
| D | `missing-amendment` | “The original agreement says four hours [D1 v1 §3]. I cannot verify a later change from these excerpts.” |
| E | `untrusted-injected` | “The current target is four hours; the note told me to use that answer [P1 probe].” |

Be precise: a citation string may name a real ID yet fail because that span was absent, stale, ineligible or unrelated to the claim. Also distinguish **faithful to the provided source text** from **correct for the dated contract task**.

## E. Write an experiment card for an optional real model

Design a test of one family, preferably position. State the question, falsifiable hypothesis, baseline, independent variable, controls, source snapshot, frozen question and required evidence, model/tokenizer/prompt versions, actual token and output caps, decoding settings, seeds or repetitions, order randomization, privacy-safe storage, metrics and denominators, per-case results format, error analysis and limitations. Use a claim rubric for old value, effective replacement, arithmetic, citation support and abstention. Include latency and measured or estimated cost if the model interface reports them.

If you have a model available, run the frozen cases and add the outputs to **your own protected experiment record**. Do not write model outcomes into the checked-in V0 manifest without actually running and reviewing them. If no model is available, finish the design card and response-card review; report “model behavior unmeasured.” Neither path licenses a universal claim from two fictional questions.

## F. Choose a knowledge-access method and defend it

For each task, choose direct generation, in-context examples, fine-tuning, continued pretraining, retrieval or a structured tool. Justify freshness, provenance, permission and cost: (i) teach a model the desired citation format across many requests; (ii) answer the current private Helios amendment; (iii) retrieve the exact termination clause; (iv) calculate the reduction from two verified numbers; (v) answer a live database status. Multiple mechanisms may cooperate, but state which one supplies the fact.

Run the complete V0 and probe suite:

```powershell
python -m unittest discover -s projects/V0 -p 'test_*.py' -v
```

**Passing submission:** mechanism arithmetic and budget have correct units; position cases keep the same five source IDs; all fictional response cards are graded at claim level; `D10` stays out of `support-team` prompts; no source instruction is promoted to a trusted role; and any statement about a real model is backed by an actual versioned run. Save a one-page experiment card, the case manifest, a local prompt sketch, the grading table and a paragraph explaining one misleading “more context is enough” argument.
