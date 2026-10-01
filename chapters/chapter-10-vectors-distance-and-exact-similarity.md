# Chapter 10 — Vectors, distance, and exact similarity [INTERMEDIATE]

The [Chapter 12 update bridge](chapter-12-retriever-training-and-domain-adaptation.md#from-a-vector-to-one-parameter-update) later extends these dot products to shaped matrix multiplication, transpose and a checked parameter update; this chapter's exact search requires no training calculus.

Chapter 9 made the V2 lexical system measurable. Its BM25 search finds the termination clause at rank two, yet loses one governing clause for the dated contract question at that same cutoff. A lexical scorer sees the words its analyzer produced; it cannot, by itself, establish that a differently worded passage means the same thing. Before trying a learned representation, we need to know precisely what a vector searcher does with *any* representation. Otherwise a change in coordinates, distance, normalization, or search algorithm can be mistaken for a gain in understanding.

This chapter builds an **exact** vector oracle. It scores every eligible vector and returns the mathematically best *k* under a declared metric and tie rule. The vectors here are supplied numbers or a dense encoding of known lexical features. **They are not learned semantic embeddings.** Chapter 11 will ask how a model learns coordinates useful for retrieval. Later ANN chapters may skip some comparisons and must be checked against the exact oracle built here.

**Prerequisites.** Chapter 3 introduced arrays, norms, operations and complexity; Chapter 6 introduced sparse term vectors and cosine; Chapters 7–9 supply the judged BM25 comparison. Keep Chapter 2's candidate → selected context → answer boundary and Chapter 5's eligibility gate. A close neighbor is still only a candidate.

**Workload identity:** `ch09-lexical-judged-v1`; see the [comparison registry](../evaluation/WORKLOAD_REGISTRY.md). Metrics across different workloads do not form an improvement sequence.

## 1. The coordinates come before the distance

A vector is an ordered tuple of numbers, such as `x=(0.8, 0.6)`. Its **dimension** is the number of coordinates, here two. Coordinate one of a query must represent the same feature, in the same units and version, as coordinate one of every indexed item. Swapping axes or comparing vectors from different encoders invalidates a search even when dimensions happen to match. A title/body term presence vector from Chapter 6 has one coordinate per vocabulary term; most coordinates are zero, so a sparse map or postings representation is efficient. A dense array stores a position for every dimension, including zero positions. “Dense” describes storage/representation, not semantic intelligence.

The **Euclidean norm** `||x||₂ = sqrt(Σᵢ xᵢ²)` measures magnitude. A **unit vector** is `x/||x||₂` for `x ≠ 0`, and has norm one. In a term-count representation, magnitude can partly reflect how many or how often terms occur; whether that signal is useful is an evaluation question. Unit normalization removes magnitude from cosine comparison, which can help with one length effect while discarding potentially useful information. It cannot be applied to a zero vector: there is no direction to normalize.

Coordinates also have *population geometry*. If most vectors point near one direction, scores can bunch together; if one coordinate has a much larger scale than another, it may dominate an unnormalized distance. This is the intuition behind **anisotropy**: the population is not spread equally in all directions. It is not a diagnosis of a model until we inspect its actual vector and score distributions. A two-dimensional drawing cannot show the number of nearly comparable directions, concentration, or training effects in hundreds of dimensions. Use the drawing to verify formulas, not to infer high-dimensional retrieval quality.

### Four ways to compare the same points

Let the query be `q=(1,0)` and the candidate vectors be `A=(1,0)`, `B=(2,0)`, `C=(0.8,0.6)`, and `D=(0,1)`. These are hand-authored coordinates; no source text or relevance judgment is attached.

| Measure | Formula | Best direction | A | B | C | D |
|---|---|---|---:|---:|---:|---:|
| Inner/dot product | `Σᵢ qᵢxᵢ` | Larger | 1 | 2 | 0.8 | 0 |
| Cosine similarity | `(q·x)/(||q||₂ ||x||₂)` | Larger | 1 | 1 | 0.8 | 0 |
| Euclidean distance, L2 | `sqrt(Σᵢ(qᵢ−xᵢ)²)` | Smaller | 0 | 1 | `sqrt(0.4)≈0.632` | `sqrt(2)≈1.414` |
| Manhattan distance, L1 | `Σᵢ|qᵢ−xᵢ|` | Smaller | 0 | 1 | 0.8 | 2 |

Calculate C by hand: `q·C = 1×0.8+0×0.6=0.8`; `||C||₂=sqrt(0.8²+0.6²)=1`, so cosine is `0.8`. Its L2 distance is `sqrt((1−0.8)²+(0−0.6)²)=sqrt(0.4)`. Its L1 distance is `|0.2|+|−0.6|=0.8`. For B, the dot product is `2`, cosine is `2/(1×2)=1`, and L2 distance is `1`. Dot therefore puts B first because its magnitude is larger; cosine ties A and B because they point in the same direction; L2 puts A first because A equals the query. With an alphabetical ID tie rule, cosine orders `A, B, C, D`. Dot orders `B, A, C, D`; L2 orders `A, C, B, D`.

**Figure 10.01 — One coordinate set, three ranking rules.** Panel A plots the hand-authored points and `q` in feature units; panel B is computed by the exact search implementation. B's large norm helps its dot score but does not help its cosine. The plane is an arithmetic aid, not evidence about the shape of a real embedding space.

![A query at (1,0) and four labeled points appear in a two-dimensional plane. A is at the query, B lies farther on the same ray, C is above and left of A, and D is on the vertical axis. A table shows dot order B A C D, cosine order A B C D after the ID tie, and L2 order A C B D.](../visuals/chapter-10/figure-10-01-metric-geometry.svg)

*Alt text:* A and B have the same direction but different magnitudes. Exact ranking puts B ahead under dot, ties A and B under cosine, and puts A ahead under L2. *Editable source:* [plot program](../visuals/chapter-10/plot-10-01-metric-geometry.py); [PNG](../visuals/chapter-10/figure-10-01-metric-geometry.png). Chapter 10; Python and matplotlib; plotted coordinates and metric values are fixed, with no sampling, seed or uncertainty. Both axes are hand-authored feature units.

Two identities explain when metrics agree. For nonzero vectors, `q·x = ||q||₂ ||x||₂ cos(q,x)`. On **unit-normalized** query and item vectors, dot equals cosine, and

```text
||q̂ − x̂||₂² = ||q̂||₂² + ||x̂||₂² − 2(q̂·x̂)
                 = 2 − 2 cos(q,x).
```

Thus normalized L2 and cosine give opposite but equivalent *orderings* in exact arithmetic, because square root is increasing. This equivalence does **not** make their numeric scores interchangeable, and it does not hold for unnormalized L2. It also says nothing about L1. Negative coordinates are allowed: cosine can be negative, L2/L1 cannot. If a feature has physical units, scaling one axis changes L1/L2 and often dot/cosine; choose and version the representation with the metric.

> **Misconception check.** Cosine similarity measures angle between *given* vectors. It cannot manufacture semantic similarity from weak coordinates. A one-hot or binary term vector can still miss a paraphrase. Nor is a cosine score of `0.8` an 80% probability of relevance or answer correctness. Score thresholds and comparisons across encoders, metrics, scopes or corpus snapshots require labeled calibration; Chapter 23 revisits threshold policy.

## 2. Exact top-*k* is the oracle

For `N` eligible vectors of dimension `d`, one exact query must compare the query with every eligible item under the chosen metric. A straightforward dot or L1/L2 comparison takes `O(d)` arithmetic, so scoring takes `O(Nd)`. Sorting all scores adds `O(N log N)` time and `O(N)` result storage. A size-*k* heap keeps only the best `k` while scanning, taking `O(N log k)` selection time and `O(k)` heap storage, **but still scores all N**. The teaching code retains an `O(N)` eligible-entry list for clarity; an iterator could avoid that auxiliary list without changing the score count. For `k>N`, return all eligible vectors. An empty eligible set yields no result. Exactness here means exact exhaustive scoring under the chosen floating-point implementation, metric, snapshot, scope and tie policy—not proof that nearest vectors are relevant.

```text
INDEX TIME
  fix coordinate schema + source/index version
  validate dimension and finite numbers
  store vectors with source IDs and permitted scopes
  optionally store unit vectors for cosine

QUERY TIME
  derive trusted eligibility scope; validate and transform query
  for each eligible item: compute one full metric value
  keep best k by (metric value, deterministic ID tie)
  return candidate IDs, raw values and work counts
  select context and generate later, in distinct stages
```

The [standard-library implementation](../projects/V3/exact_vectors.py) exposes `dot`, `norm`, `unit`, `measure`, and `ExactIndex.search`. `sort` and `heap` plans use the same score and tie key; behavioral tests compare their IDs **and raw values** across metrics and cutoffs. For a similarity, higher values win; for a distance, lower values win. A deterministic item ID breaks exact score ties. This matters because `A` and `B` tie under cosine, and a different tie rule could alter the top-one result and downstream context. Floating-point scores that differ by tiny amounts are not declared tied by an arbitrary epsilon; this implementation compares computed values as they are. A production system must pin numerical kernels and check near-tie behavior across platforms.

The index caches unit item vectors for cosine at **index time** and normalizes the query once at **query time**. It rejects a zero query or an eligible zero item for cosine instead of silently assigning a score. The project wrapper has a separate policy for a lexical query whose fixed vocabulary coordinates are all zero: it returns **no candidates** and records `zero_in_vocabulary_query`. That is a no-result policy, not a numeric definition of cosine. For L1/L2/dot a zero vector can be scored. NaN, infinity, dimension mismatch, duplicate IDs, and invalid *k* are errors; silently ranking malformed data would make a false “exact” oracle.

### Physical execution and batching

A practical dense exact search lays the item vectors out as an `N×d` numeric matrix `X` and a batch of `Q` queries as `Q×d` matrix `Y`. Dot scores come from `Y Xᵀ`, a matrix multiplication costing about `O(QNd)` scalar multiply/add work, with optimized contiguous buffers and kernels. Batching can amortize dispatch and use hardware better, but also consumes `O(QN)` score memory if the full score matrix is materialized. Streaming blocks can reduce peak memory while retaining a per-query heap. For 32-bit floats, the raw vector matrix alone is approximately `4Nd` bytes, excluding IDs, metadata, alignment, index structures, replicas and cache. A million 768-dimensional vectors would be about **3.072 billion bytes** (roughly **2.86 GiB**) before those extras. This is a size calculation, not a service cost or latency promise.

Memory layout matters: row-contiguous vectors make each query–item dot a sequential read; Python tuples and object headers in this teaching index are much larger and slower than packed numeric arrays. The index build must be counted separately from query latency. Multiple queries can reuse the prepared matrix or unit vectors, but new or deleted documents and model version changes require a consistent index snapshot. Chapter 14 will treat exact dense retrieval as a baseline and later ANN chapters will trade some exact-neighbor recall for lower query work under measured conditions. The classical IR text and current nearest-neighbor library documentation both distinguish brute-force scoring from indexing structures; [the relevant primary sources](../REFERENCES.md#chapter-10--verified-2026-09-30) are listed in the reference register.

## 3. The V3 project begins with a deliberately weak representation

To keep the judged baseline alive, [V3's Chapter 10 experiment](../projects/V3/experiment_ch10.py) turns each V1 title/body segment into a **119-dimensional binary term vector**. The coordinate names are the sorted V1 vocabulary on the same V0 snapshot; a one means the analyzed term occurs, without TF, IDF, field boost or position. Query text passes through the same analyzer. This is a dense storage form of sparse lexical information. It **cannot** solve synonymy or paraphrase merely by using cosine. The comparator is V2 exhaustive BM25, with the same 14 frozen Chapter 9 questions, 12 support-team eligible segments, 168 reviewed query–segment pairs, *k*=2 and 8, and the same 120-source-word context builder. Legal-only D10 is outside both scoring and qrels. There is no encoder, model training, general generator or new answer judgment.

**Experiment card.** Question: does switching from BM25 to exact binary lexical cosine improve judged ranking? Falsifiable hypothesis: macro positive-query NDCG@2 rises. Primary change: scoring and representation; the V0 source/segment snapshot, V1 analyzer, scope fixture, questions, qrels and context budget remain fixed. Because the change bundles TF/IDF and cosine representation, this experiment demonstrates a *system-level alternative*, not which of those components caused a difference. The measured [raw record](../projects/V3/chapter-10-experiment.json) pins source/qrel/code hashes, vector dimension, environment, per-query IDs/scores/context, stub status for the two V0 questions, work counts, randomized method order and 11 warmed search-only samples per method/query/depth. It uses the Chapter 9 metric definitions, including separate no-positive behavior.

| Frozen support-team result | V2 BM25 | Exact binary cosine |
|---|---:|---:|
| Macro NDCG@2, 11 positive queries | 0.8997 | 0.7724 |
| Macro binary Recall@2 | 0.8636 | 0.7273 |
| Macro direct-evidence Recall@2 | 0.9545 | 0.8636 |
| Macro NDCG@8 | 0.9453 | 0.8713 |
| No-positive candidate rate at 2, 3 questions | 2/3 | 2/3 |
| Mean fully scored eligible segments per query | 10.71 | 11.14 |
| Search-only p50 / p95 at 2, local microseconds | 44.5 / 103.0 | 140.7 / 398.1 |

The NDCG hypothesis is **false on this fixture**. On `q-termination`, BM25's top two include `D1:§8:0`, the governing termination clause; binary cosine returns `D1:§3:0` and `D4:step-4:2`, so it misses that clause. Its title-term alignment can make the wrong section look geometrically close. On `q-contract-change`, both top-two lists omit `D1:§3:0`, the signed original needed with the amendment; the reranked decoys differ, but neither system assembles the complete dated evidence. The V0 stub therefore still abstains for that question. On `q-no-result`, both yield no candidates; the vector wrapper detects a query with zero in-vocabulary coordinates before attempting cosine. Two other zero-positive questions can still return plausible-looking but irrelevant eligible candidates. The static scope test checks that no `D10` ID enters either candidate or context list. This is a fixture security regression, **not** live authentication.

At the selected depth, a *candidate* may be relevant while the 120-word *context* drops it; the record retains both ID lists and direct-evidence context recall. Only two V0 questions run the deterministic stub. The stub's answer/abstention status is not an answer-correctness score for all 14 questions. The single-author, partly known-failure qrels, one tiny fictional corpus and Python-list implementation cannot establish population quality, production p95, or whether a learned encoder helps. A later, separately judged domain split is needed before claiming that. The measured latency gap describes these local search calls; it does not isolate the effect of SIMD matrix kernels or vector hardware.

**Observation and diagnosis.** A private trace may record query ID, source/index/vectorizer versions, scope identifier, metric, candidate IDs and raw scores, selected context IDs, score count, zero-vector/no-result reason, and search/context latency. It should not log arbitrary private query text or candidate payloads. Check in order: source snapshot → coordinate schema/encoder version → query norm → eligible count → candidate scores/tie order → qrel grades → context coverage → answer support. If `scored_vectors < eligible_vectors` in a nonzero exact search, investigate the implementation; if a legal-only ID appears, treat it as an eligibility failure, not a ranking error. Monitor distributions by scope and representation version before calibrating a similarity cutoff. Neither a high cosine nor a low distance should authorize a source.

## 4. What exact similarity does and does not buy

The advantage of brute-force search is a clear oracle: for its input vectors and metric, it does not miss a better eligible neighbor through an approximate index. It is simple to test, works well enough for small corpora, and gives a reference for future ANN recall. Its cost grows with eligible corpus size and dimension; a heap improves selection memory and work but does not remove comparisons. An inverted index can avoid work for sparse lexical features, as Chapters 5–8 showed. Thus converting sparse terms to a dense array may increase scan cost without adding information, as V3 demonstrates.

Choosing a metric is part of model design. Dot can intentionally use magnitude if training makes magnitude informative; cosine removes that factor; L2 responds to both direction and magnitude unless normalized; L1 sums coordinate deviations and has a different geometry. None is universally best. Scores from different metrics, model versions, vocabulary maps or scopes are not directly comparable. A fixed top-*k* may return irrelevant candidates even when no positive evidence exists; Chapter 23 will address no-result thresholds, dynamic *k* and calibration. A zero or low score alone does not prove unanswerability, and retriever confidence must remain separate from answer confidence.

### Practice and recall

The [lab](../labs/chapter-10/LAB.md) asks you to calculate all four measures for three candidates, implement and test both exact selection plans, inspect the judged negative result, and defend a design for a larger corpus. Attempt it before opening the [separate solutions](../solutions/chapter-10-solutions.md).

1. Explain why unit-normalized cosine and L2 rank identically, and give a counterexample without normalization.
2. If a heap makes top-*k* selection `O(N log k)`, why is exact scoring still `O(Nd)`?
3. What does `cosine=1` tell you about `A=(1,0)` and `B=(2,0)`? What does it *not* tell you about evidence quality?
4. Which version fields must match before an indexed vector can be compared with a query vector?
5. Why is `q-no-result` a different event from a search that scores 12 eligible vectors and returns the best two despite zero relevance?

**Interview defense.** A teammate says, “Cosine found the nearest section, so the model may cite it.” Walk through eligibility, representation, exact ranking, qrels, context selection, and claim support to show the additional checks needed. Explain how you would use exact search as an oracle for an ANN benchmark without confusing oracle-neighbor recall with judged evidence recall.

At the end of Part III, revisit these formulas after one, three, seven and 21 days, sketch the index/query boundary from memory, and compare V3's result against V2 rather than memorizing the table. For further reading, see [Manning, Raghavan and Schütze on vector-space scoring](https://nlp.stanford.edu/IR-book/html/htmledition/dot-products-1.html), their [discussion of computing vector scores](https://nlp.stanford.edu/IR-book/html/htmledition/computing-vector-scores-1.html), and [scikit-learn's nearest-neighbor algorithm documentation](https://scikit-learn.org/stable/modules/neighbors.html). Read the specific implementation assumptions; no library replaces the representation and judgment audit.

**You understand this chapter if you can…** compute dot, cosine, L2 and L1 by hand; predict a ranking change caused by magnitude or normalization; implement an exact scoped top-*k* search with deterministic ties and zero-vector policy; distinguish its `O(Nd)` scoring from heap selection and matrix batching; reproduce the V3 judged comparison without calling its binary features semantic; and locate a missing answer at the candidate, context or answer stage rather than equating nearest neighbor with evidence.
