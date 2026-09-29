# Chapter 3 lab — Measure the operation you actually need

**Prerequisites:** [Chapters 1–2](../../chapters/chapter-02-build-the-first-rag-loop.md), the frozen [V0 source and question contract](../../projects/V0/README.md), and [Chapter 3](../../chapters/chapter-03-data-algorithms-and-measurements-needed-for-search.md). **Estimated time:** 3–4 hours. Use the Python standard library for the benchmark; matplotlib is needed only to regenerate the supplied plot. Attempt the tasks before opening the [worked solutions](../../solutions/chapter-03-solutions.md).

The deliverable is a small experiment report, not a claim that a dictionary solves RAG search. Keep the original V0 corpus, answer path, scope behavior and two frozen evidence questions intact. Your benchmark compares **two implementations of exact-ID lookup** on the same synthetic records and keys. It may extend the V0 project with a measurement sidecar, but V1's term index waits for Chapter 5.

## A. Read the V0 path and count its units

1. In [engine.py](../../projects/V0/engine.py), point to the line or function for each operation: one-time source segmentation, per-request eligibility, per-request term scoring, candidate sorting, context selection and answer stub. Which work would still happen if you added `{segment_id: segment}` but kept `search()` unchanged?
2. Run `tokenize()` on the two strings in `FROZEN_QUESTIONS`. Record whitespace-word count, regex-term count and distinct regex-term count. Explain the repeated term in the termination question. Do not label any of these a model-token count.
3. For `"§"`, `"é"`, `"e\u0301"` and `"Sev-1"`, report `len(text)`, `len(text.encode("utf-8"))` and `tokenize(text)`. State which two strings may display similarly while differing in code points. Use Unicode escapes if your terminal changes non-ASCII input.
4. Find the size of the checked-in `corpus.json` file in bytes. Why is that size neither V0's Python heap usage nor its prompt-token count?

## B. Derive before timing

For a list of `n` records, fill in the number or bound requested below. State whether the bound is average or worst case and what distribution, if any, it assumes.

| Operation | `n=16` hand trace or bound | Growth with `n` | Build/update cost to remember |
|---|---|---|---|
| Unsorted list, absent exact ID |  |  |  |
| Unsorted list, uniformly located present ID |  |  |  |
| Prepared dictionary, exact ID |  |  |  |
| Binary search on sorted IDs |  |  |  |
| Sort `n` scored candidates |  |  |  |

Calculate `log₂ 1024` and explain its unit. For `B=120 µs`, `Tₛ=30 µs/lookup` and `Tₘ=0.2 µs/lookup`, find the smallest integer number of lookups for which `B+qTₘ < qTₛ`. Say which real costs this simple break-even equation omits.

## C. Implement and reproduce a controlled comparison

1. Independently implement `linear_find(records, key)` and a `{record["id"]: record}` map. For four records, check the first, last and absent IDs. The returned record **and missing-result behavior** must agree.
2. Create five sizes—64, 256, 1,024, 4,096 and 16,384 synthetic records—with stable unique IDs. At each size create 256 deterministic shuffled lookup keys: 128 present and 128 absent. Time seven batches of each method with `time.perf_counter_ns()`. Divide each elapsed nanosecond count by 256 and by 1,000 to obtain **microseconds per lookup**. Build the dictionary outside the timed lookup batches and record its build time separately. Warm both paths, alternate method order, consume results and check equality outside timing.
3. Compare your procedure to the [reference measurement sidecar](../../projects/V0/measurements.py). Run:

   ```powershell
   python -X utf8 projects/V0/measurements.py
   python visuals/chapter-03/plot-03-01-id-lookup.py
   ```

   Inspect the [JSON record](../../projects/V0/chapter-03-measurements.json) and [plot source](../../visuals/chapter-03/plot-03-01-id-lookup.py). The second command requires matplotlib. Explain both axes, their units and log scales, what a point represents, and what an error bar does **not** establish.
4. Rerun with only the hit/miss mix changed:

   ```powershell
   python -X utf8 projects/V0/measurements.py --hit-fraction 0 --output chapter-03-all-miss-local.json
   ```

   Compare this with the [retained all-miss record](../../projects/V0/chapter-03-all-miss-measurements.json). Why should the list-scan curve change? Why is “same `n`” an insufficient workload description?

## D. Write an experiment card and debug a misleading claim

Use the [experiment contract](../../evaluation/EVALUATION_EXPERIMENT_CONTRACT.md) to write a card with question, falsifiable hypothesis, baseline, changed variable, controls, synthetic corpus and code version, frozen keys/seed, hit and miss counts, timing unit, number of trials, per-size results, error analysis, conclusion and limitations. Include the observed build and shallow-container byte costs. Name at least two sources of timing noise. Preserve a negative or inconclusive observation if your run differs from the supplied one.

A colleague says: “The dictionary makes RAG retrieval 2,000 times faster, so we can replace V0's `search()` with `by_id.get(question)`.” Identify **three separate errors** in this claim: task/semantics, measurement, and eligibility. State the first V0 trace fields you would inspect if the contract-change answer then omitted `D2`.

## E. Calculate and defend the small mathematics

1. For candidate counts `[2,0,3]`, calculate the sum and mean across all requests. What happens to the reported mean if the zero-result request is silently excluded?
2. For latencies `[2,3,4,6,20]` milliseconds, calculate mean, median and p95 using nearest rank `ceil(p×n)`. Explain why five observations cannot establish a stable production p95. Do **not** add stage p95s to estimate wall p95.
3. For vectors `a=(1,2)` and `b=(2,1)`, calculate `a·b`, `||a||₂`, `||b||₂` and cosine. What special case makes cosine undefined? Why is the result not a permission score?
4. Propose a train/validation/test split for future queries over **unseen agreements**. Specify how you group `D1`, `D2`, related FAQs and synthetic questions. Contrast it with a test of new questions over a fixed known corpus. State which deployment claim each split can support.

## F. Running-project check and oral defense

Run the V0 behavioral tests after your measurement work:

```powershell
python -m unittest discover -s projects/V0 -p 'test_*.py' -v
```

Show that `D10` is still absent for `support-team`, `D2` is still required for the dated change, and the termination clause still comes from `D1 §8`. Explain aloud why the exact-ID benchmark cannot justify a claim about answer correctness, faithfulness or lexical retrieval quality. Keep your code, JSON manifest, raw samples, one annotated plot and experiment card together; place the [separate solutions](../../solutions/chapter-03-solutions.md) aside until your first attempt is complete.

**Passing submission:** both lookup methods agree on present and absent IDs; timings have explicit per-lookup units and build cost outside the loop; the workload and seed are frozen; the all-miss probe is explained; the chapter's four hand calculations are correct; V0's evidence and scope tests still pass; and the conclusion does not confuse exact-ID lookup with text search.
