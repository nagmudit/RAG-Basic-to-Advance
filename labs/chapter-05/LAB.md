# Chapter 5 lab — Build and interrogate a positional index

**Prerequisites:** Chapters 2–4; Python standard library; the V0 corpus. **Deliverables:** one hand-built postings sheet, a Boolean/phrase trace, two analyzer failure notes, a reproducible experiment card, and a V1/V0 regression report. This lab uses fictional source records and makes no model call.

## A. Predict before running

Read the five records in [toy_corpus.json](../../projects/V1/toy_corpus.json). Under the `v0` analyzer, write the body term positions for `S1` and `S3`. Make a term-to-postings table for `hx-7a`, `guide`, `reset`, and `legacy`. For each posting record segment ID, body positions and term frequency. Keep title positions separate. Predict the body phrase matches for `reset guide`, `guide reset`, `hx-7a reset`, and `manual helios` at `support-team` scope. Explain why `S5` can be in an internal posting but not in a support result.

Compute by hand: `hx-7a AND guide`; `checklist OR legacy`; `(checklist OR legacy) NOT legacy`; and `hx-7a AND NOT legacy`. Name the positive set used for each NOT query. Write the two-cursor sorted-list intersection for `[S1,S2,S3,S5]` and `[S1,S3,S4]`, counting comparisons until one list ends. What changes when the legal-only `S5` is removed before intersection?

## B. Build and inspect

Run from the repository root:

```powershell
python -X utf8 projects/V1/lexical_index.py --phrase "initial response target"
python -X utf8 -m unittest discover -s projects/V1 -p 'test_*.py' -v
```

Read [lexical_index.py](../../projects/V1/lexical_index.py). Trace `build_index()` from source segment through analyzer, field-local position, posting tuple, forward segment and scope membership. Trace one `search()` from query term to eligible candidate, unweighted score, context and V0 stub. Find the code that prevents a title/body phrase crossing and the code that prevents an unauthorized forward fetch. Record the vocabulary size, term–segment pair count, position count and one index-build time on your machine; do not treat that single build time as a stable benchmark.

Use a short scratch script or Python REPL to call `boolean_ids()` and `phrase_ids()` on `load_corpus("projects/V1/toy_corpus.json")`. Compare results with A. Add a unit test for repeated-term phrase behavior (for example a temporary section `"go go now"`): `go go` should match, `go now` should match, and `go go go` should not. Keep the test after the lab if it catches a real regression.

## C. Break an analyzer on purpose

With the toy records, query `HX-7A`, the different code `HX-7C`, the misspelling `resett`, `café`, and the decomposed spelling `cafe` + U+0301 under both analyzers. State the exact match/miss outcome, and explain *which transformation* caused it. Then propose an analyzer or a separate exact field for a corpus where `HX-7A` and `HX-7B` are distinct product codes. Do not silently enable fuzzy matching. Explain how dropping `not`, applying a stemmer, or applying NFKC could create an unwanted equivalence on a different workload. Give a test query for each proposed policy.

## D. Compare work and behavior with V0

Run:

```powershell
python -X utf8 projects/V1/experiment.py --output projects/V1/chapter-05-experiment-local.json
python -X utf8 -m unittest discover -s projects/V0 -p 'test_*.py' -v
```

Inspect the checked-in [reference result](../../projects/V1/chapter-05-experiment.json) before comparing local medians. The frozen query set is the two V0 questions plus `q-rare-numeric` and `q-no-result`. The script uses synthetic copies at 13, 130 and 1,300 segments, `support-team`, V0 analyzer and top eight. On each size and query, confirm exact candidate ID/score agreement; report eligible segments, eligible posting visits, scored segments, raw timing samples, median and nearest-rank p95. State the index-build cost separately. The 130 and 1,300 segment corpora repeat source wording; explain why this is not a relevance benchmark.

Write an [experiment card](../../evaluation/EVALUATION_EXPERIMENT_CONTRACT.md) with question, falsifiable hypothesis, baseline, changed variable, controls, snapshot and code versions, query IDs, metric and denominator, procedure/seed, per-slice results, a negative or weak result, limitations, and decision. Candidate exact agreement is a *correctness invariant*, while latency and work counts describe cost. The first judged retriever and qrels appear in Chapter 9. Do not claim answer correctness from search timing.

## E. Debug an unsafe and a misleading result

1. A support trace contains `S5` after someone moves the scope filter to *after* ranking. Where is the first broken boundary? What tests and protected artifacts would you inspect? Why is removing `S5` from the final answer insufficient?
2. The dated Helios question returns `D3` but no `D2`, while the index contains `D2`. Distinguish: source/index omission, analyzer mismatch, scope exclusion, top-k loss, context-budget loss and answer-stage misuse. Name one trace or direct probe for each. Which later chapter will introduce a formal relevance judgment?
3. A colleague says, “The absent-query row is 800 times faster, so this index makes all RAG answers 800 times faster.” Identify the query-mix, stage-scope and sample-size errors. Which case in the result scored every eligible segment?

## F. Explain and defend

Sketch Figure 5.01 and Figure 5.02 from memory. Explain why a posting's positional `3` cannot by itself identify a quote in the original bytes. State what must be rebuilt when an analyzer changes and why an ACL change cannot wait for an eventual offline rebuild. Show the V0 and V1 frozen question answers and explain why they remain a *baseline*, not an LLM evaluation.

**Passing submission:** your hand postings and phrase answers match the executable fixture; no restricted ID reaches a support candidate, prompt or ordinary trace; exact V0 candidate order and scores hold under the V0 analyzer; the experiment separates index build from query time, records raw timing and a common-term counterexample, and preserves the distinction among candidate, context, evidence and answer. Check the [separate solutions](../../solutions/chapter-05-solutions.md) only after writing your own trace.
