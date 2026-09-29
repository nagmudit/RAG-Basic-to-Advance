# Chapter 4 lab — Worked solutions and review rubric

Attempt the [lab](../labs/chapter-04/LAB.md) before reading this file. The checked-in [manifest](../projects/V0/chapter-04-case-manifest.json) records **inputs**, not language-model behavior. The response cards are fictional examples created for claim review.

## A. Mechanism and units

`P(y₁,y₂|x)=P(y₁|x)P(y₂|x,y₁)=0.8×0.7=0.56`. This is a probability assigned to one two-token path under the toy conditionals, not correctness, faithfulness, citation support or a calibrated answer confidence. For toy attention logits `0` and `ln 3`, `exp(0)=1` and `exp(ln 3)=3`; normalized weights are `1/4=0.25` and `3/4=0.75`. A causal output position cannot see later output tokens. Neither weight establishes the truth or governing status of a source.

The excerpt allowance is `4096−512−240−40−64=3240` actual model tokens. A 3,500-token excerpt proposal exceeds it by **260 tokens**. V0's `tokenize()` makes lexical regex terms; `build_context()` counts whitespace-separated source words; `Engine.run()` records `ceil(prompt characters/4)` as an approximation. A model experiment needs the **chosen model's tokenizer** plus its wrapper and output accounting. The example budget is fictional and not a provider specification.

## B. Position cases and first failing stage

All three position cases use the five IDs `{D1:§3:0, D2:§2:0, D3:FAQ-7:0, D7:timeline:0, D9:proposal-2:0}`. Their order differs: front begins `D1,D2`; middle is `D3,D1,D2,D7,D9`; end is `D3,D7,D9,D1,D2`. Each manifest row reports **67 source words, 809 prompt characters and 2/2 required spans**; the SHA-256 hashes differ because order differs. Source strings and labels may be tokenized differently at boundaries, so one must measure actual model-token counts before claiming equal token budgets.

If a required `D2` candidate is absent from `context_ids`, the first failure is **context selection/packing**. If it is in the actual prompt and an answer still reports stale four hours, the first remaining failure is **generation or claim use**; inspect the source-version reasoning and citation. V0's narrow stub checks complete required strings in context and returns the same fixed answer for all three. It cannot reveal a model's position sensitivity.

## C. Controlled variants and their limits

`conflict-neutral` and `conflict-stale` both retain `D1 §3` and `D2 §2`. A lab-only eight-word `P1` note is replaced by the eight-word stale `D3` FAQ in the third slot. Both have 67 source words, but prompt characters are **813** and **809** because labels and text differ. Model-token counts, source identity and content also differ; the treatment tests a conflicting source slot, not a perfect length-matched token intervention.

`instruction-base` and `instruction-explicit` keep the same five IDs and order. Only the application's trusted response instructions change; prompt characters are 809 and 907. Grade the old/current values and calculations, citations to `D1`/`D2`, and abstention when evidence is missing. More words in an instruction may help, harm or do nothing on a chosen model; only a controlled run can tell.

The `untrusted-injected` case appends a `P1` excerpt that begins `SYSTEM:` and tells the model to ignore the question and report the stale value. The label is **data**, not a real system role. `D1` and `D2` remain in context. The manifest identifies a separate `-ch04-injected-probe` snapshot. Application-side eligibility filtering must still bar `D10`; a prompt instruction cannot enforce permissions. `missing-amendment` contains only `D1 §3` from the two required spans. It can support the original four-hour target but not a signed one-hour replacement or a dated reduction.

## D. Fictional response-card judgments

| Card | Correctness for dated task | Faithfulness and citation support | Abstention behavior / first failure |
|---|---|---|---|
| A | Correct under the fictional signed sources and arithmetic | `D1 §3` supports four; `D2 §2` supports one/effective date; `3/4=75%` follows | Answerable; no abstention needed. Preserve as positive regression case. |
| B | Incorrect current value | `D3` states four hours, so the words echo one supplied excerpt, but FAQ is stale; its citation does not support the *current* claim given `D2` | Failure at source-authority use in generation/verification; preserve stale-FAQ case. |
| C | Claim could match the full corpus but is **unsupported in this selected context** | `D2` is absent from `missing-amendment`; printed `[D2 §2]` is a fabricated context citation | Failure at answerability/verification after missing context; preserve omission and false-citation case. |
| D | Correct partial response | `D1 §3` supports the original value; no claim about an unseen amendment | Appropriate abstention on the change; preserve positive missing-evidence case. |
| E | Incorrect current value | `P1` is a lab-only instruction, not governing contract evidence; the response obeys untrusted text | Trust-boundary and claim-support failure; preserve injected-source case. |

Card B shows why merely repeating a source can be faithful to that **piece of text** yet wrong for the dated task. Card C shows why a source may exist in the broader corpus while being unavailable to the generator for this request. A strong review states both distinctions rather than marking every flawed answer simply “hallucinated.”

## E. Optional model experiment card

**Question:** On this frozen prompt set, does moving the same required source excerpts change claim support? **Hypothesis:** a chosen model may have different error rates when `D1`/`D2` are first, middle or last. **Baseline:** `position-front`. **Independent variable:** excerpt order. **Controls:** five IDs, signed source versions, question, trusted instructions, model/tokenizer versions, output cap and decoding settings. **Dataset:** fictional V0 `support-corpus-2026-05-20`; one frozen dated question; required spans `{D1 §3,D2 §2}`. **Procedure:** verify exact prompt hashes, count actual model tokens, randomize case order, run repeated trials if stochastic, save protected outputs and usage. **Measures:** each old/current value correct, arithmetic correct, citation supported, answer/abstain correct, output tokens, wall time and cost with denominators. **Error analysis:** inspect the earliest missing or misused source boundary. **Limitations:** one fictional question, small sample, position may change tokenizer counts, model/prompt versions matter. **Current checked-in result:** model behavior **unmeasured**. A real run must fill results and conclusions; the manifest's `null` fields are deliberate.

## F. Knowledge-access choices

Citation **format** can be taught with in-context examples or fine-tuning if repeated behavior warrants it, but those mechanisms do not supply the current private amendment. The current target needs eligible retrieval of signed `D2` (and `D1` for comparison) with version and span. The termination task can return `D1 §8` directly from source search without free-form synthesis. Arithmetic can use checked values and deterministic code, with a model explaining only the verified calculation if helpful. A live database status belongs in a permissioned structured query/tool path with a timestamp and schema validation. Continued pretraining may adapt broad domain language, but it is too indirect for an individually changing contract clause and source citation.

All V0 behavior tests and the prompt-probe tests should pass. The tests establish input-path and deterministic stub behavior, not language-model answer quality.
