# Chapter 3 lab — Worked solutions and expected observations

Use this after attempting the [lab](../labs/chapter-03/LAB.md). Local timing values will differ; correctness, units and causal explanations should not. The code in [measurements.py](../projects/V0/measurements.py) is a complete reference implementation of the controlled benchmark.

## A. V0 path and units

`load_corpus()` and `segment_corpus()` prepare the list once for an `Engine`; `search()` filters scope, tokenizes and scores each eligible segment, then sorts; `build_context()` chooses prompt excerpts; `build_prompt()` labels them; and `stub_answer()` checks only selected context. An ID map added beside `segments` would not skip any of `search()`'s repeated term work unless the query task and algorithm changed.

| Query | Whitespace words | Regex terms | Distinct regex terms |
|---|---:|---:|---:|
| `q-contract-change` | 14 | 14 | 14 |
| `q-termination` | 9 | 9 | 8 |

`the` occurs twice in the termination question. The distinct-term score uses it once. These counts do not predict a model's subword/token budget.

| Text | Code points (`len`) | UTF-8 bytes | V0 regex terms |
|---|---:|---:|---|
| `§` | 1 | 2 | `[]` |
| composed `é` | 1 | 2 | `[]` |
| decomposed `e\u0301` | 2 | 3 | `["e"]` |
| `Sev-1` | 5 | 5 | `["sev-1"]` |

Composed and decomposed accented `e` may render similarly. V0's ASCII-oriented tokenizer handles them differently, a concrete normalization failure. `projects/V0/corpus.json` was **4,528 bytes in the authoring checkout**; line-ending conversion can change the byte count in another checkout. Either way, the file's UTF-8 encoding and JSON syntax make its size different from Python's live heap or a model's prompt tokens.

## B. Growth and break-even

| Operation | `n=16` | Growth | Build/update caveat |
|---|---|---|---|
| Unsorted list, absent ID | 16 comparisons | `O(n)` worst case | No extra lookup structure; list changes are simple |
| Unsorted list, uniformly placed present ID | `(16+1)/2 = 8.5` comparisons on average | `O(n)` average under stated position distribution | Same list; early hits can be faster |
| Prepared dictionary | Average near one key lookup; collision path can check more | Average `O(1)`, worst `O(n)` | Build `O(n)` expected, extra memory, maintenance on changes |
| Binary search on sorted IDs | About four halvings to reduce 16 to 1 | `O(log₂ n)` comparisons | Sort `O(n log n)`; middle insertions can shift `O(n)` elements |
| Sort scored candidates | No fixed comparison count promised by `O` | `O(n log n)` upper growth for a comparison sort | Must first compute the scores; sorting does not reduce scoring work |

`log₂ 1024 = 10` because `2¹⁰=1024`; it is a count of halvings/comparison levels in the binary-search intuition, not milliseconds. Break-even requires `120+0.2q < 30q`, or `q > 120/29.8 ≈ 4.027`; the smallest integer is **5 lookups**. This omits map memory, updates, misses, distribution changes, disk/network work and the uncertainty of measured constants.

## C. Benchmark behavior

A minimal pair of equivalent lookup paths is:

```python
def linear_find(records, key):
    for record in records:
        if record["id"] == key:
            return record
    return None

by_id = {record["id"]: record for record in records}
# For each frozen key, verify linear_find(records, key) == by_id.get(key)
```

The [retained 50% hit record](../projects/V0/chapter-03-measurements.json) is one Windows 11 / CPython 3.14.2 run with seed `20260929`, 256 lookups per trial and seven trials. Medians of batched per-lookup times are:

| Records | List scan (µs) | Dictionary (µs) | One map build (µs) |
|---:|---:|---:|---:|
| 64 | 1.252 | 0.059 | 7.3 |
| 256 | 11.331 | 0.143 | 21.5 |
| 1,024 | 30.482 | 0.124 | 145.2 |
| 4,096 | 138.330 | 0.177 | 457.8 |
| 16,384 | 528.284 | 0.259 | 2349.3 |

The plot's x-axis is synthetic **record count**, y-axis **microseconds per exact-ID lookup**, and both axes are logarithmic. Each point is the median of seven **batch-average** times, not request p50. Bars show the min-to-max batch-average range; they are not confidence intervals. The time excludes map construction and record generation. At 16,384, the saved shallow list container is 136,632 bytes and the shallow dictionary container is 415,152 bytes. Neither includes the shared records or strings, so subtracting them is not a total-memory bill.

In the [retained all-miss record](../projects/V0/chapter-03-all-miss-measurements.json), the 16,384-record scan median was about **671.752 µs** per lookup, versus **528.284 µs** in the half-hit run; all misses must traverse the full list. The dictionary's measured values remain small but are not guaranteed constant on every run. These two records were collected sequentially as separate local runs, so environmental noise also differs. Repeating both conditions in randomized order would strengthen the comparison.

## D. Experiment card and claim diagnosis

**Question:** How does exact-ID lookup time grow with synthetic record count? **Hypothesis:** list scan rises much more than prepared dictionary lookup. **Baseline:** linear scan. **Changed variable:** lookup implementation; a second controlled probe changes only hit fraction. **Controls:** ID schema, seed, present/absent keys, size sequence, process, batch size and trial count within a run. **Versions:** `measurements-v1`, Python/platform fields and timestamp in each JSON. **Measures:** correctness equality, median and raw batch-average µs/lookup, one map-build sample, shallow bytes. **Result:** the recorded list-scan curve rises strongly; the map curve is much flatter for this exact-ID task. **Error analysis:** misses increase scan work; warm-up, scheduling, caches, interpreter overhead and different run times affect wall time. **Limit:** synthetic in-memory lookup, small number of trials, no relevance judgments, no authorization in the benchmark, no full RAG path. **Decision:** keep the measurement sidecar as a prerequisite; do not replace V0 `search()` with an ID map.

The colleague's claim fails at three boundaries. (1) `by_id.get(question)` expects an **ID**, but the contract question is natural language and has no `D2` key. (2) The measured ratio concerns a synthetic exact-ID operation with an already-built map, not end-to-end request latency or lexical candidate quality; even the numeric ratio varies by size and run. (3) Direct ID access could expose ineligible `D2` or `D10` unless scope is checked before content leaves the store. For a missing amendment answer, inspect source snapshot and eligible scan count, then `candidate_scores`, `context_ids`, `evidence_ids`, status and reason in the V0 trace. The earliest missing boundary drives the diagnosis.

## E. Arithmetic, tail behavior and split design

For `[2,0,3]`, `Σ cᵢ=5` and the mean across **three** requests is `5/3≈1.67`. Excluding the zero-result request yields `5/2=2.5`, a different question and misleadingly better-looking coverage. For `[2,3,4,6,20]` ms, mean `=35/5=7 ms`, median `=4 ms`, nearest-rank p95 position `ceil(0.95×5)=5`, so p95 `=20 ms`. Five requests provide almost no stable tail estimate; stage p95s are not additive.

For `a=(1,2)` and `b=(2,1)`, dot product `=4`; both Euclidean norms are `√5`; cosine `=4/5=0.8`. A zero vector makes the cosine denominator zero. The coordinate calculation cannot decide source authorization or factual support.

For **unseen-agreement** transfer, group all versions and derived artifacts of one agreement—including `D1`, `D2`, `D3` and synthetic paraphrases—into a single train, validation or test partition. Tune only on training/validation groups and open test once the design is frozen. For **new questions over a known corpus**, the document collection may remain fixed while questions are separated and deduplicated; that supports a narrower deployment claim. A test question copied from a training synthetic template can still leak, even if its wording differs slightly. State corpus and query versions with each result.

## F. Project guardrail

The measurement code has no call path into V0 `Engine.run()`. The existing behavioral suite still checks the `D10` scope exclusion, `D2` evidence requirement and `D1 §8` termination response. Passing that suite is necessary for preserving V0 behavior; it does not turn the synthetic benchmark into an answer-quality study.
