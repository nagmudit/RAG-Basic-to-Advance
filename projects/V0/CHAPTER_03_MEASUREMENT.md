# V0 characterization before V1 indexing

Chapter 3 adds a read-only [measurement sidecar](measurements.py), its [behavioral checks](test_measurements.py), a [frozen 50% hit record](chapter-03-measurements.json), and an [all-miss record](chapter-03-all-miss-measurements.json). It does **not** change [V0's lexical search and answer code](engine.py) or create a V1 term index. The exact-ID task is deliberately narrower than retrieval from a natural-language question.

**Question:** On deterministic in-memory synthetic records, how do list scan and a prepared dictionary compare for the same exact-ID lookup as record count grows? **Hypothesis:** scan time rises with `n`, while average prepared-map lookup is much flatter. **Baseline:** `linear_find`. **Changed variable:** list versus dictionary; the separate all-miss probe changes the hit mix while keeping the method comparison. **Controls:** ID schema, seed `20260929`, record sizes 64–16,384, 256 shuffled keys per trial, seven trials, Python process and method semantics within a run. **Correctness:** both implementations are checked against the same expected record or `None` for each key outside timing. **Metric:** median of seven batched wall-time averages, in microseconds **per exact-ID lookup**; retain raw samples and one dictionary-build time. **Memory observation:** `sys.getsizeof` shallow container bytes and UTF-8 JSON bytes, not total resident memory.

For the checked-in half-hit Windows 11 / CPython 3.14.2 run, the 16,384-record median was 528.284 µs/lookup for scan and 0.259 µs/lookup for the prepared dictionary; one build took 2349.3 µs. In the sequentially collected all-miss run, scan median at that size was 671.752 µs/lookup. A missing ID traverses the whole list. These observations are local and noisy; the two runs were not randomized as a paired experiment. The [reproducible plot and source](../../visuals/chapter-03/plot-03-01-id-lookup.py) show all sizes and raw-sample ranges.

The measurement is a computing prerequisite for V1, not a relevance, authorization, answer-quality or end-to-end latency result. It cannot replace V0 `search()` with `by_id.get(question)`: the frozen question is not an ID, and an ID lookup still requires a verified eligibility policy. V0's [baseline results and failures](RESULTS.md) remain the source for its two evidence tasks. The benchmark stores no private text or real user identifiers.

Reproduce from the repository root:

```powershell
python -X utf8 projects/V0/measurements.py
python -X utf8 projects/V0/measurements.py --hit-fraction 0 --output projects/V0/chapter-03-all-miss-measurements.json
python visuals/chapter-03/plot-03-01-id-lookup.py
python -m unittest discover -s projects/V0 -p 'test_*.py' -v
```

The plot was rendered with matplotlib 3.11.0 in the authoring environment; the measurement sidecar and V0 engine use only the Python standard library. Rerunning overwrites the recorded measurements with **new local observations**; preserve the committed JSON when comparing runs.
