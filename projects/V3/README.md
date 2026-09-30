# Build Your Own RAG Engine — V3, Chapter 10 exact-vector foundation

V3 spans Chapters 10–14 in the [project roadmap](../../PROJECT_ROADMAP.md). **Only its Chapter 10 stage is implemented.** This stage supplies an [exact vector oracle](exact_vectors.py), not a learned retriever. Chapter 11 will introduce embedding models; Chapter 12 will address training and domain adaptation. V0's fictional source snapshot, V1's analyzer/postings, V2's BM25/qrels and the two-question answer stub remain the binding baseline. No Chapter 11 implementation is present here.

## Artifacts and boundaries

- [Exact vector code](exact_vectors.py): numeric validation, dot/cosine/L2/L1, index-time unit vectors, scoped exhaustive scoring, full sort or bounded-heap selection, raw scores, deterministic ID ties and work counters. `allowed_scopes` is a static fixture; a caller-supplied scope is **not authentication**.
- [Behavioral tests](test_exact_vectors.py): hand geometry, plan equivalence, full eligible scan, tie order, zero/dimension/nonfinite handling, duplicate IDs and support-team isolation.
- [Paired judged experiment](experiment_ch10.py) and [checked-in record](chapter-10-experiment.json): V2 BM25 versus exact cosine on dense **binary lexical term-presence** coordinates. There are 119 fixed vocabulary dimensions; no learned encoder and no semantic claim. It reuses Chapter 9's 14 frozen queries and 168 reviewed support-team query–segment pairs. The record retains candidate IDs/raw scores, qrel ranking metrics, selected context IDs/direct coverage, the limited V0 stub status, work, raw search-only timings, versions, hashes, environment and limitations.
- [Figure 10.01 source](../../visuals/chapter-10/plot-10-01-metric-geometry.py), [SVG](../../visuals/chapter-10/figure-10-01-metric-geometry.svg) and [PNG](../../visuals/chapter-10/figure-10-01-metric-geometry.png): hand-authored geometry, exact metric ranking and explicit tie rule.

The vector index contains all 13 V0 indexed segments, but the `support-team` search scores only 12. Legal-only D10 is excluded **before** similarity calculations and is absent from context. Real permission checks must derive scope from a trusted identity and handle live updates. The 119-coordinate vocabulary and segment representations are built at index time from V1's analyzed title/body term presence. The query gets the same coordinate map at query time. A query with no vocabulary terms has a zero vector; the wrapper returns no candidates and records the reason because cosine is undefined there. Other cosine queries score every eligible nonzero vector, including zero-similarity items. The exact index is the oracle for its declared representation/metric, not for human relevance.

## Reproduce

From the repository root:

```powershell
python -X utf8 -m unittest discover -s projects/V3 -p 'test_*.py' -v
python -X utf8 projects/V3/experiment_ch10.py --output projects/V3/chapter-10-experiment-local.json
python -X utf8 visuals/chapter-10/plot-10-01-metric-geometry.py
```

Use a local experiment output path to preserve the checked-in observation. The code/tests use the Python standard library; the figure requires matplotlib. The record's hash policy normalizes CRLF to LF. Search timing excludes index build, context selection and stub; one warm call per method/case precedes 11 timed calls, with randomized method order. Local timing varies. Raw IDs/scores are useful in this fictional fixture but need access-controlled handling in a real trace.

## Measured result and next gate

The top-two macro positive-query NDCG hypothesis fails: BM25 `0.8997`, exact binary cosine `0.7724`. Binary cosine misses the governing termination clause at top two; BM25 includes it. Both still omit one required signed contract-change clause at top two. All ranked/cited content stays under the support-team fixture, but two of three zero-positive questions still return irrelevant eligible candidates. At top two the checked-in local p50/p95 search-only timing is 44.5/103.0 µs for BM25 and 140.7/398.1 µs for binary cosine; this tiny Python run cannot size a production vector service. The negative result is expected to be instructive: dense storage of term presence does not add semantic information and gives up sparse candidate generation. Chapter 11 must evaluate an actual frozen encoder on an independently judged paraphrase/identifier split before treating vector proximity as a retrieval gain. Later ANN comparisons must keep the exact vector oracle and judged-evidence metrics separate.
