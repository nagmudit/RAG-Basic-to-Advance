# Chapter 3 — Data, algorithms, and measurements needed for search

*Part I: Orientation and prerequisites · [FOUNDATIONAL]*

> **The question for this chapter:** When the V0 corpus grows, how can we predict which work repeats for every question, measure it honestly, and avoid improving the wrong operation?

In [Chapter 2](chapter-02-build-the-first-rag-loop.md), V0 prepared thirteen source-labeled segments and searched them by inspecting every eligible segment. That is an excellent first system because we can account for every candidate. It is also a useful failure case: a request repeats term extraction and overlap scoring on each eligible segment, even when most segments have nothing to do with the query. The two frozen questions still require the Chapter 1 evidence contract. No faster data structure may turn `D3`'s stale FAQ into the governing amendment, expose restricted `D10`, or let an answer cite a span that never reached context.

Before building an inverted index in Chapter 5, we need a small vocabulary for data structures, work, space and measurement. The goal here is not to make V0's answer path faster. We will compare two ways to solve **the same exact-ID lookup task**, then explain why that result cannot be pasted onto term retrieval. We will also acquire the algebra, statistics and vector notation needed to read later ranking chapters without treating a measured number as a universal law.

## 1. Follow the data before choosing a structure

V0 holds prepared segments in a Python **list**. A list is an ordered sequence: `segments[0]` finds one position, and a `for` loop visits positions in order. Each segment is a **dictionary**, or map, from field names such as `segment_id` and `text` to values. `tokenize()` produces terms; a **set** removes duplicates and makes membership/intersection convenient. Finally, `search()` sorts positively scored candidates. These choices serve different operations.

| Operation in V0 | Structure | What it buys | What it does not buy |
|---|---|---|---|
| Visit every eligible segment | List of segment dictionaries | Simple sequential scan; stable order | Skip segments that lack query terms |
| Read `part["source_span"]` | Dictionary record | Named field access | Search all records by content |
| Compute `query_terms & part_terms` | Sets | Distinct shared-term count | Term frequency, authority or semantic match |
| Sort candidate score tuples | List sort | Deterministic top `k` after scoring | Avoid scoring all eligible segments |

The distinction between **position lookup** and **content lookup** is easy to miss. `segments[7]` is direct because we already know position seven. “Find the segment about the amended Sev-1 target” supplies no position. An ID map, `{id: record}`, helps when the caller already has an exact ID. It does not answer a natural-language information need. Chapter 5 builds the missing term-to-record structure only after we understand this difference.

At **preparation time**, V0 reads a frozen snapshot and makes windows. An auxiliary map could also be built once at this stage. At **query time**, V0 receives a question and scope, filters eligibility, scores candidates, selects context and invokes the narrow stub. A preparation cost and a per-question cost have different denominators: building a map once for a thousand requests is not a thousand map builds. Conversely, an update or deletion must change every structure that claims to represent the current snapshot. The stable source ID, version and span continue to identify what a result means.

### Exact ID lookup as a controlled example

Suppose four prepared records have IDs `S0`, `S1`, `S2`, `S3`, in that list order. To find `S2`, a linear scan checks `S0`, `S1`, then `S2`: three comparisons. To find absent `X`, it checks all four. A map made with `{record["id"]: record for record in records}` stores the same four records under keys and can ask `by_id.get("S2")`. Building the map still visits all four once, and the map occupies additional memory. It does not establish whether `S2` is eligible, relevant, current or sufficient evidence.

The small reference implementation is ordinary Python:

```python
def linear_find(records, key):
    for record in records:
        if record["id"] == key:
            return record
    return None

by_id = {record["id"]: record for record in records}
same_answer = linear_find(records, "S2") == by_id.get("S2")
```

The [measurement sidecar](../projects/V0/measurements.py) uses this exact pair. It verifies equal answers for every measured key **outside** the timed region. It never plugs the ID map into V0's lexical search or prompt construction. In a real application, an ID lookup must still enforce the caller's source eligibility; knowing an ID is not authorization.

## 2. Count work before measuring seconds

**Time complexity** describes how an operation's work can grow with an input size. Let `n` be the number of records and `q` the number of exact-ID lookups. A list scan makes at most `n` ID comparisons for one lookup, so its worst-case work is `O(n)` and `q` lookups cost `O(qn)`. If the key is uniformly distributed among present IDs, it finds a record after about `(n+1)/2` comparisons on average. Absent IDs require `n` comparisons. The position and hit/miss distribution therefore matter even when `n` is fixed.

A hash map computes a key's hash and uses it to find a likely storage location. Under ordinary hash-distribution assumptions, Python dictionary lookup is **average-case `O(1)`** with respect to the number of records. That is not an absolute time guarantee: hashing a long key has a cost, collisions can make the worst case `O(n)`, and the map must first be built in `O(n)` expected work. The [Python project's complexity reference](https://wiki.python.org/moin/TimeComplexity) states the assumptions and distinguishes average from worst case. A sorted array offers another option: binary search halves the candidate range repeatedly, giving `O(log₂ n)` comparisons for an exact key after an `O(n log n)` sort. Inserting into the middle of that array may shift many entries. Each structure pays for a different set of operations.

Here `O` gives a growth bound, not a stopwatch reading. If `n` doubles, an `O(n)` operation's leading work often roughly doubles, while `O(log₂ n)` adds roughly one halving step. `log₂ 16 = 4` because four halvings take 16 to 1: `16 → 8 → 4 → 2 → 1`. Constant factors, cache behavior, object allocation, interpreter overhead and storage I/O still determine elapsed time. For a collection on disk or behind a network, “one map lookup” may incur a cache miss, page read or remote call. A vector of source IDs in memory is not a distributed document store.

V0's **actual** retrieval task is different. Let `N` be prepared segments, `S≤N` eligible segments, `L` their average title-plus-text term count, `Q` distinct query terms, and `M` positive-score segments. Filtering scans all `N`; V0 then tokenizes every eligible segment for every request. Its approximate query work is `O(N + S(L + Q) + M log M)`; the last term sorts candidates. A map keyed by document ID changes neither the repeated term processing nor the score's meaning. An inverted index will address the first problem. Even then, index build, postings storage, permission checks and updates remain part of the total system cost.

### Build cost can be amortized, but not erased

If an auxiliary structure takes `B` microseconds to build, a scan takes `Tₛ` microseconds per exact lookup, and a map lookup takes `Tₘ`, the idealized break-even count is

\[
q > \frac{B}{T_s-T_m}, \qquad T_s>T_m.
\]

This algebra compares `qTₛ` with `B+qTₘ`. It assumes one unchanged collection, one workload and no memory or update cost. In the local 16,384-record sample below, `B≈2349 µs`, `Tₛ≈528.3 µs`, and `Tₘ≈0.259 µs`, suggesting roughly **five** lookups to repay that one measured build. It is a calculation on one machine, not a recommendation for a production threshold. The dictionary consumes extra memory; a deletion, new version or permission change may require additional maintenance; a disk-backed implementation has different constants.

## 3. Characters, bytes, words and tokens are different units

V0's context budget counts whitespace-separated **source words**. Its lexical score uses distinct lowercase **terms** from a regular expression. Its prompt-size estimate uses `ceil(characters/4)`. None of those is a real model-token count. A unit must be named before a number can be interpreted.

Python `str` length counts Unicode code points, not UTF-8 bytes and not necessarily visible characters. For example, `len("§")` is 1 while `len("§".encode("utf-8"))` is 2. The composed character `"é"` is one code point and two UTF-8 bytes; `"e\u0301"` displays similarly but has two code points and three UTF-8 bytes. Neither is guaranteed to be one model token. The [Python Unicode HOWTO](https://docs.python.org/3/howto/unicode.html) explains code points and encodings; Chapter 4 will explain why a model's tokenizer defines yet another unit.

For the frozen V0 questions, the exact current program returns:

| Query | Whitespace words | Regex terms | Distinct regex terms |
|---|---:|---:|---:|
| `q-contract-change` | 14 | 14 | 14 |
| `q-termination` | 9 | 9 | 8 |

The repeated `the` in the second question is why its distinct-term count is eight. These figures describe **this tokenizer and text**, not language-independent word counts. The lab recomputes them instead of trusting the table.

Storage units need the same care. The experiment records `sys.getsizeof(records)` and `sys.getsizeof(by_id)` as **shallow container bytes**. Those numbers omit the memory of the record dictionaries, strings and other referenced objects; adding them blindly can double-count shared values. It also records the number of UTF-8 bytes in a JSON serialization of synthetic records, which is a different representation from Python's live objects. Disk files may be compressed, indexed or replicated. For a real cost decision, specify what bytes are counted, where they live and how long they are retained. The [Python `sys.getsizeof` documentation](https://docs.python.org/3/library/sys.html#sys.getsizeof) explicitly limits the direct measurement to the object itself.

## 4. Measure one task with one frozen workload

The diagnostic asks: **How does exact-ID lookup time change with record count when the lookup semantics stay fixed?** The falsifiable hypothesis is that list scans will grow with `n`, while a prepared dictionary will have much flatter average lookup time in this in-memory Python workload. The baseline is a list scan. The only algorithmic change is the use of an ID map. We hold the record schema, key strings, Python process, query workload rule, hit/miss mix and answer semantics fixed.

The [frozen measurement file](../projects/V0/chapter-03-measurements.json) records five synthetic sizes: 64, 256, 1,024, 4,096 and 16,384 records. For each size, a fixed seed creates 256 keys, half present and half absent, shuffles them, and reuses them for seven timed trials. Both paths warm up; trial order alternates; every result is consumed; all individual lookups are checked for equality outside timing. Each batch's elapsed nanoseconds are divided by 256 and converted to **microseconds per lookup**. A single map-build sample, shallow container sizes, Python version, platform and raw timing samples are also retained. Python's [`perf_counter_ns()`](https://docs.python.org/3/library/time.html#time.perf_counter_ns) measures an elapsed interval; it does not label CPU time or explain why a trial was slow.

**Figure 3.01 — Exact-ID lookup growth in one local run.** The solid line is a list scan and the dashed line is an already-built dictionary. Both axes are logarithmic and labeled. Points are medians of seven *batch averages*; bars span the minimum and maximum batch averages. The plot demonstrates this workload's shape, not an end-to-end RAG latency or a universal speed ratio.

![Log-scale plot of median microseconds per exact-ID lookup against 64 through 16,384 synthetic records. The list-scan line rises from about 1.3 to 528 microseconds while the dictionary line stays below 0.26 microseconds; error bars show seven-trial batch ranges.](../visuals/chapter-03/plot-03-01-id-lookup.svg)

*Alt text:* Two labeled lines compare the same ID lookup task. Across five increasing synthetic corpus sizes, the list scan rises steeply and the already-built dictionary rises slightly. Both axes use log scales; bars are the range of seven batch-average trials. *Editable source:* [plot script](../visuals/chapter-03/plot-03-01-id-lookup.py). *Data:* [JSON measurements](../projects/V0/chapter-03-measurements.json). *Rendered alternative:* [PNG](../visuals/chapter-03/plot-03-01-id-lookup.png). *Chapter association:* 03.

**Table 3.1 — Recorded medians from this Windows 11 / CPython 3.14.2 run, 2026-09-29.** The build column is one sample, outside the lookup timing; it has no uncertainty estimate.

| Records (`n`) | Scan (µs/lookup) | Prepared map (µs/lookup) | Map build (µs, one sample) |
|---:|---:|---:|---:|
| 64 | 1.252 | 0.059 | 7.3 |
| 256 | 11.331 | 0.143 | 21.5 |
| 1,024 | 30.482 | 0.124 | 145.2 |
| 4,096 | 138.330 | 0.177 | 457.8 |
| 16,384 | 528.284 | 0.259 | 2349.3 |

The result supports the narrow hypothesis for exact-ID lookup on this machine. It does **not** show that V0's natural-language search becomes a dictionary lookup, that a map is always faster after construction, or that a single lookup time predicts request p95. At small sizes, fixed overhead, cache state and measurement noise can dominate. Python's [`timeit` guidance](https://docs.python.org/3/library/timeit.html) recommends repeated timing and examining the vector rather than treating a lone number as truth. The raw samples allow the learner to inspect variation and rerun the script. This is a controlled local experiment, not a hardware-independent benchmark.

### A failure of the tempting interpretation

Imagine placing `D2` into a map keyed by `D2`. The natural-language question does not contain `D2`; the program still needs a way to find it. Worse, a user might know `D2` but lack permission to read it. An ID map can accelerate an already-authorized source fetch **after** the relevant ID is known; it does not supply relevance, scope, temporal authority, or answer support. To test this boundary, compare the V0 trace for an inaccessible `D2`: candidates and context omit it before scoring, regardless of whether a source store could look up its ID. A speed measurement cannot override the evidence contract.

## 5. The small mathematics later chapters will reuse

We need mathematical notation because ranking models combine quantities, and evaluation summarizes repeated observations. The following tools are deliberately small enough to calculate by hand.

**Sums and averages.** The symbol `Σ` means “add the indicated values.” If three per-query candidate counts are `2, 0, 3`, then `Σᵢ cᵢ = 2+0+3 = 5`, and the arithmetic mean is `5/3 ≈ 1.67 candidates per query`. A zero-result query must remain in the denominator if the question is “average across all three requests.” Leaving it out silently changes the population.

**Logarithms.** `log₂ n` asks how many factors of two make `n`. Thus `log₂ 1,024 = 10`. A binary search over 1,024 sorted IDs needs on the order of ten halvings, subject to exact comparison convention. Later, logarithms appear inside term weighting; they compress a wide range of frequencies. A logarithm is undefined at zero, so a formula using `log(x)` must say how it handles `x=0`.

**Probability and distributions.** A probability is a statement about a specified experiment or model, not a synonym for a retrieval score. If a labeled set contains 8 answerable questions among 10, its observed answerable fraction is `8/10 = 0.8` on that set. It is not automatically an 80% chance for the next production query; the query distribution may differ. A **distribution** describes how values are spread, not merely their average. A workload with many short requests and a few expensive long ones can have a low mean and a damaging slow tail.

**Vectors and norms.** A vector is an ordered tuple of numbers, such as `a=(1,2)` and `b=(2,1)`. Their dot product is `a·b = 1×2 + 2×1 = 4`. Each Euclidean norm is `√(1²+2²)=√5`; the cosine between them is `4/(√5√5)=0.8`. The coordinates have no meaning here. Later chapters define term-weight and learned embedding coordinates before using these operations for retrieval. A zero vector has norm zero, so cosine needs an explicit zero-vector policy. A large cosine is a geometric relationship under a representation, not permission or proof of an answer.

**Percentiles and uncertainty.** Suppose five measured request latencies, in milliseconds, are `[2,3,4,6,20]`. Their mean is `35/5 = 7 ms`; their median is `4 ms`. Under the **nearest-rank** rule, the p95 position is `ceil(0.95×5)=5`, so p95 is `20 ms`. This p95 is just the maximum of five samples; it is a poor estimate of a service's long-run tail. Different percentile estimators can disagree on small samples. The plot above does not report request p95 at all: it shows medians and ranges of seven batch-average times. A wider or representative sample, stated window, denominator, workload slices and uncertainty analysis are needed for production claims. Chapter 48 develops formal experiment and interval methods.

Do not add stage p95s to obtain end-to-end p95. The slowest retrieval request need not be the slowest generation request, and stages may overlap. V0 reports one request's wall time and stage durations; a distribution needs many separately labeled requests. The [observability contract](../observability/OBSERVABILITY_CONTRACT.md) gives the later trace and dashboard shape.

## 6. Control experiments and prevent leakage

An experiment needs a **question**, a prediction that could be wrong, a baseline, a changed variable, controls, a frozen workload and declared measures. The exact-ID experiment meets those requirements for a computing claim. It does not have relevance judgments because the task is exact equality: the expected record for each key is known. A retrieval-quality experiment is different. It needs frozen questions, eligible relevant spans and a denominator that distinguishes candidate retrieval from selected context and final answer. V0 has only two hand-audited tasks; Chapter 9 introduces judged retrieval metrics, and Chapters 30–33 evaluate a full RAG baseline.

When we later train a retriever, split data before choosing settings. A **training set** changes model parameters; a **validation set** guides choices; a **test set** estimates performance after choices are frozen. Reusing the test set for repeated design decisions leaks information from evaluation into development. The split unit matters: if one version of a Helios agreement is in training and a near-duplicate amendment or synthetic paraphrase of it is in test, the test may measure recognition of a familiar source rather than generalization. Group related document versions and generated questions when the intended claim is transfer to unseen agreements. If the real task is new questions over the **same known corpus**, say that instead and build a matching split. Neither split is universally correct; it must match the deployment question.

Keep a versioned manifest of corpus, query set, scope policy, code, tokenizer, parameters and judgments. An improvement without those identities cannot be replayed. The Chapter 3 measurement JSON stores its deterministic synthetic workload and raw samples; V0's [baseline result record](../projects/V0/RESULTS.md) stores the separate evidence questions and failures. Neither should be mislabeled as a broad relevance benchmark.

## 7. Debug the first wrong number, not the most visible answer

If a timing curve changes unexpectedly, first verify that both programs returned the same records. Then inspect workload and units: were misses included, was the map built inside the timed loop, did the corpus size actually change, and is the y-axis a batch average or per-request percentile? Check process version, competing load, memory pressure and whether a cold path was compared with a warm path. If the dictionary appears slower for a tiny `n`, repeat the fixed workload and examine raw samples before editing the algorithm. A negative or inconclusive result belongs in the record.

For V0's RAG path, the diagnostic order remains **source and eligibility → candidate search → context selection → stub answer**. A data-structure timing improvement says nothing about a `D2` omission, a stale `D3` claim or a restricted `D10` leak. An ordinary measurement record needs configuration, counts, units, timestamp and environment; a request trace needs source snapshot, stage observations and redacted identifiers. Both should avoid raw private questions and source text in broadly accessible logs. Synthetic IDs here are safe fixtures; a production ID map or cache must retain the same permission boundary as the source it addresses. Retention and licensing of a real corpus also apply to benchmark copies, not only to the serving index.

The practical choice is therefore conditional. A list is easy to inspect and can be good enough for a small local corpus. A map helps exact lookup once an ID is known, at a build and memory cost. A sorted structure helps ordered lookup and ranges but complicates updates. A term index helps skip irrelevant documents for text queries; Chapter 5 will implement it and compare **the same term-search task** against V0's full scan. Chapter 4 first explains how an LLM uses supplied context, so that a faster search does not get confused with a better answer.

## 8. Practice and continuity

The [Chapter 3 lab](../labs/chapter-03/LAB.md) asks you to count V0's three text units, implement both exact-ID paths, reproduce the plot, test a cold/warm and hit/miss counterexample, compute growth and percentile examples, and diagnose one misleading performance claim. Compare with the [separate solutions](../solutions/chapter-03-solutions.md) after attempting the tasks. The running project gains only the [measurement sidecar and raw report](../projects/V0/measurements.py); V0's answer and eligibility code remain the Chapter 2 baseline. This is the first characterization step toward V1, whose actual tokenizer and index arrive in Chapters 5–6.

For an interview-style defense, explain why a dictionary can answer `by_id["D2"]` quickly but cannot discover `D2` from the frozen contract question. Then estimate when its build cost could be worthwhile and identify the security check that must remain outside the lookup's speed claim.

Close the chapter and answer from memory. Revisit after one, three, seven and twenty-one days:

- Which V0 operations occur once per snapshot, and which repeat per question?
- What input size and operation does each `O(·)` bound describe?
- Why is average-case dictionary lookup not a worst-case latency SLO?
- How can two strings look alike but differ in code points and UTF-8 bytes?
- Why are lexical terms, whitespace words and model tokens separate units?
- What do the axes and error bars of Figure 3.01 measure?
- Why is p95 from five requests unstable, and why is it not the sum of stage p95s?
- How can a train/test split leak through related source versions or synthetic queries?

### You understand this chapter if you can…

- Trace V0's list, dictionary, set and sort operations without calling an ID map a text-search index.
- Derive scan, hash-lookup, binary-search, build and sort growth with stated average/worst-case assumptions.
- Reproduce the exact-ID experiment from the checked-in code and data, state its workload and units, and refuse an unsupported RAG speed or quality conclusion.
- Count code points, UTF-8 bytes, whitespace words and V0 lexical terms in a small example, while reserving model tokens for a model tokenizer.
- Compute a mean, nearest-rank percentile, logarithm, dot product, norm and cosine by hand, including their edge cases.
- Propose a versioned, leakage-aware evaluation split that matches a named deployment question.
- Diagnose whether a surprising result comes from source eligibility, retrieval, context, answer behavior, timing setup or a mislabeled measurement.

## Further reading

- Python Software Foundation, [Time Complexity](https://wiki.python.org/moin/TimeComplexity): implementation-specific average and worst-case costs for common containers; it does not substitute for measuring your workload.
- Python Software Foundation, [`time.perf_counter_ns()`](https://docs.python.org/3/library/time.html#time.perf_counter_ns), [`timeit`](https://docs.python.org/3/library/timeit.html), [Unicode HOWTO](https://docs.python.org/3/howto/unicode.html), and [`sys.getsizeof`](https://docs.python.org/3/library/sys.html#sys.getsizeof): exact API and unit boundaries used above.
- [V0 measurement source](../projects/V0/measurements.py) and [raw record](../projects/V0/chapter-03-measurements.json): a reproducible local observation, not a general search benchmark.
