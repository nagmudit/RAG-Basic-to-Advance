# Chapter 10 lab — Establish an exact vector oracle

**Prerequisites:** Chapters 3, 6 and 9; V0 source/answer path and V2 qrels are binding. **Time:** about 100–130 minutes. Read [Chapter 10](../../chapters/chapter-10-vectors-distance-and-exact-similarity.md) first. Work from the repository root with Python 3. Attempt each task before reading the [separate solutions](../../solutions/chapter-10-solutions.md).

## Deliverables

Submit a hand-calculation sheet, a short standalone exact-search implementation with tests, an experiment card with per-query error notes, and a design defense. Keep candidate IDs, selected context IDs and any stub behavior in distinct columns. Do not describe the binary term features as learned embeddings.

## 1. Compute and explain the geometry

Use `q=(1,0)` and `A=(1,0)`, `B=(2,0)`, `C=(0.8,0.6)`, `D=(0,1)`. Compute the norm of each, then dot, cosine, L2 and L1 from q to each item. Show the intermediate products for C. List top three under every measure, taking larger dot/cosine and smaller L1/L2. Break exact ties by alphabetical item ID. Explain why B wins dot but ties A under cosine. Derive `||q̂−x̂||₂²=2−2cos(q,x)` from the norm expansion, and state both conditions under which this yields identical rankings. Give a zero-vector counterexample to careless cosine calculation.

Sketch these points on paper before viewing [Figure 10.01](../../visuals/chapter-10/figure-10-01-metric-geometry.svg). Which relationships can the two-dimensional picture verify, and which claims about a learned 768-dimensional model would be unwarranted?

## 2. Implement exact scoped top-*k*

In a new scratch file, implement a function accepting records with unique ID, numeric coordinates and permitted scopes; query coordinates; a trusted scope; metric `dot`, `cosine`, `l2` or `l1`; and positive *k*. Score **every eligible** record. Return ordered `(ID, raw value)` pairs, with alphabetical ID ties, plus a scored count. Write one version using full sort and another using a bounded heap or `heapq.nsmallest`. Do not copy [the project implementation](../../projects/V3/exact_vectors.py) until your own version passes the hand example.

Test at least: four metric orders; both plans agree on IDs and raw values for *k*=1, 3 and 10; a private `P=(100,0)` is absent under the public scope; a zero query and zero document have an explicit cosine policy; dimension mismatch, NaN and duplicate IDs are rejected. Explain why a heap cannot avoid `N×d` coordinate work. State your extra-memory bound honestly, including any eligible-list allocation.

Afterward compare your decisions with the project implementation and run:

```powershell
python -X utf8 -m unittest discover -s projects/V3 -p 'test_*.py' -v
python -X utf8 visuals/chapter-10/plot-10-01-metric-geometry.py
```

## 3. Reproduce the judged V3 experiment

Run to a **new local path** so the checked-in observation stays intact:

```powershell
python -X utf8 projects/V3/experiment_ch10.py --output projects/V3/chapter-10-experiment-local.json
```

Read [the frozen V2 qrels](../../projects/V2/judgments_ch09.json), [V3 experiment code](../../projects/V3/experiment_ch10.py), and your output. Complete this experiment card:

```text
Question and falsifiable NDCG@2 hypothesis:
Baseline; representation/score/execution change; fixed controls:
Source, analyzer, vocabulary, query-set and qrel versions:
Eligibility scope, retrieval unit, dimension, query count, judged-pair count:
Metric/zero-positive conventions; candidate/context/stub distinctions:
Timing window, warmed calls, randomized order, sample count, units:
BM25 versus exact cosine at k=2 and 8; work and latency:
At least three per-query failures; conclusion and limitations:
```

Calculate the top-two macro NDCG difference yourself from the printed summaries. Inspect `q-termination`, `q-contract-change`, `q-no-result` and `q-private-target`: list candidate IDs and grades, whether all needed direct evidence enters context, and whether any legal-only D10 ID was eligible. Find a query where both rankers return plausible candidates although its qrels contain no positives. Explain why neither a nearest neighbor nor a high cosine guarantees an answer. Check your local source/qrel hashes against the checked-in record; timing is expected to vary by machine.

## 4. Defend the next design choice

Imagine 1,000,000 vectors of 768 float32 coordinates. Calculate the raw coordinate bytes and convert to GiB. At one query, compare full-sort and heap selection complexity at *k*=10; include the unavoidable score work. Explain what an `N×d` contiguous matrix changes, what a `Q×N` full batch score matrix costs, and why this simple corpus's measured Python timings cannot predict that hardware's p95. Specify the oracle metrics you would use when a later ANN method arrives: exact-neighbor Recall@10 **and** judged evidence Recall@10, plus latency and a fixed eligibility scope. Why are both recalls necessary?

**Cumulative recall.** Draw the source → index → eligibility → vector candidate → context → stub answer path and mark where Chapter 9's qrels attach. State how you would diagnose an unauthorized candidate versus a relevant candidate lost to context truncation. Write a short oral answer to: “Our cosine score is 0.9; can we cite the result?”
