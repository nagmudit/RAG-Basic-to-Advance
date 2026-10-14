# Chapter 24 lab — Keep the need fixed while changing the search

**Prerequisites:** completed Chapter 23/V7, exact retrieval from Chapters 11–13 and the chapter's feedback, fan-out and dependency explanations. Read through §24.7 before beginning. This lab extends V7; Chapter 25 is unstarted.

**Deliverable:** your own bounded implementation, predictions, a source-bound paired result table, a correlated failure trace and a short decision memo. Use the existing pinned CPU stack and cached model. Do not edit historical artifacts or the committed Chapter 24 experiment to make a method win.

## A0 — Construct before opening the reference

Copy [starter.py](starter.py) to an ignored working directory such as `build/ch24-work/your_policy.py`. Independently implement both functions. Do not import the project reference or the separate answer.

For `admit_toy`, reserve the normalized original. Check each proposal's anchor, protected atoms, duplicate key, branch limit and cumulative word limit in that order. Accepted strings spend the shared budget; rejected strings do not. A casefolded duplicate key does not authorize changing an exact ID. Predict the selected strings and every rejection reason for a tiny fixture you write before running the checker.

For `ready_toy`, validate all named dependencies and the entire graph before returning sorted ready tasks. A disconnected cycle must reject even if an independent task exists. Derive readiness from completed predecessors, not from scheduled predecessors. Explain why three individually affordable tasks can still exceed a shared budget of two steps.

```powershell
python -X utf8 labs/chapter-24/check_construction.py build/ch24-work/your_policy.py
```

The checker supplies a fresh certificate/renewal fixture; it does not import the final solution. Save your initial prediction, implementation and checker result. Then add your own unseen duplicate/budget and dependency fixtures. Have a peer inspect the code if one is available; the supplied reference tests cannot certify independent construction.

Only after this attempt, inspect [separate solutions](../../solutions/chapter-24-solutions.md) and the [project reference](../../projects/V7/reformulate_ch24.py). Explain one meaningful difference between your implementation and the reference. A failed initial attempt followed by a reasoned correction is a valid learning outcome.

## A1 — Work the two loss mechanisms by hand

1. Compute the normalized centroid update for q = (1, 0), P = {(0, 1)}, α = 1, β = .5, γ = 0. Show the unnormalized vector, norm and final coordinates. What happens when the assumed positive is about the wrong topic? What should happen for a zero update?
2. Interleave original `[(x,.70),(z,.60)]` and rewrite `[(y,.95),(x,.80)]` with cap two. Preserve the origin of each score. If `z` alone is required, compute original recall, union recall and capped recall. Why must you avoid sorting the output by the displayed scores?
3. For independent tasks `retry` and `trust`, with `combine` depending on both, list ready/completed/blocked tasks after zero, one and two successful steps. Now fail `retry`. Distinguish a ready task left by budget exhaustion from a task blocked by a failed dependency.

These are numerical/control exercises, not new benchmark results. Do not report their toy recalls as corpus performance.

## A2 — Inspect the frozen experiment before running it

Read the [original questions and required spans](../../projects/V7/qrels_ch24.json) and [frozen drafts](../../projects/V7/reformulations_ch24.json). Record their workload, query, qrel, source and draft identities. Note the explicit author-written/source-aware origin. Predict the behavior of:

- `q01`: a changed HTTP code in a surplus proposal;
- `q06`: an authority question rewritten toward waiting procedures;
- `q07`: a certificate question with billing language;
- `q09`: a rejected HTTP-code change and original fallback;
- `q10`: date-free text under a locked publication interval;
- `q16`: the inherited duration/count false trigger.

For each, distinguish admission prediction, likely candidates and required evidence. Do not use a candidate's similarity as a relevance label. The full bodies are fictional instructor data, not tenant-facing telemetry.

## A3 — Reproduce without replacing the checked result

```powershell
$ch24Runner = 'projects/V7/experiment_ch24.py'
$ch24Result = 'build/ch24-local-results.json'
$ch24Snapshot = 'build/ch24-local-index'
python -u -X utf8 $ch24Runner --output $ch24Result --artifacts $ch24Snapshot
python -X utf8 -m unittest discover -s projects/V7 -p 'test*.py' -v
python -X utf8 visuals/chapter-24/render_visuals.py
```

The runner uses the cached pinned encoder; downloads are disabled. It reuses eighteen historical body vectors, encodes ten new source bodies, prepares actual admitted query inputs, executes three shuffled repeats, validates all source/query/draft identities and restores the snapshot. It checks 48 complete query/method outcomes through raw/intermediate/final scores and ordered context. Timings, UUIDs and snapshot digests containing UUIDs can differ between independent runs; source identities, representation inputs and deterministic rankings should agree.

Build a paired table for **`ch24-frozen-reformulations-v1`** with union recall, Recall@2, context recall, actual branches, scored pairs and charged encoder WordPieces. Use eleven positive original questions for macro recall; do not multiply that denominator by three timing repeats. Report required-empty decisions separately over three tasks, and guards over two. The positive duration miss stays in the positive denominator.

State which stages the timing excludes. Do not infer a live generator's latency, token cost, answer correctness, faithfulness, citation support or generated abstention from this run. No answer generator ran; those fields remain unavailable.

## A4 — Diagnose one loss without changing the labels

Select `q06` or `q07` in hypothetical mode. Follow the original question → frozen draft → admission decision → prepared-encoding sample → child full scores and shortlist → parent admission/cap → source-version context. Identify the first boundary where the required source disappears. Include actual request and child IDs from your run; omit raw principal values from ordinary diagnostic output.

Then inspect original `q07`. Explain why its second candidate is omitted by packing while required context recall stays one. The supplied labels are inspected positive requirements; the absent A12 is not automatically a globally irrelevant document. Finally inspect the two publication sources in `q10`; show that both fit in 68 encoder WordPieces under the shared context budget eighty.

For an additional safety check, inspect current authorization on `q11`, `q12` and `q15`. No reformulation should recover the admin-only, other-tenant or deleted hard-ID record. Explain why zero branches with empty context differ from a guard's null, unrun context.

## A5 — Decide and defend

Write a 300–500-word memo with these claims supported by your result file:

1. Does multi-query earn promotion on this workload? Compare benefit and work, including ties. Compute the recall ceiling imposed by the fixed interpreter and explain which retrieval-recovery claim this workload cannot test.
2. Does the hypothetical-passage result establish anything about a live HyDE system? Identify the missing experiment.
3. Which failure should be investigated first if an answerable duration question never reaches retrieval?
4. What source/query/qrel/prompt/model identities and comparisons would a new experiment need?

If you try new questions, drafts, source content or budgets as an experiment, register a new reviewed workload/comparison before reporting metrics. Preserve the original record. Use separately frozen evaluation questions when tuning; do not call a source-aware authored fixture held-out generalization.

## Submission rubric

| Evidence | Points |
|---|---:|
| Independent admission/readiness code, initial predictions and fresh fixtures | 30 |
| Correct geometry, interleaving, dependency and budget reasoning | 20 |
| Bound paired experiment with correct denominators and timing limits | 20 |
| Correlated failure/packing/permission diagnosis | 20 |
| Defensible negative-result memo and explicit untested claims | 10 |

A passing run without independent construction earns no construction points. A proposal that widens permissions, mutates the original hard fields, uses qrels as a stop signal or treats hypothetical text as evidence requires correction before the lab is complete. End at this V7 checkpoint; do not begin Chapter 25.
