# Chapter 16 lab — Separate list loss from code loss

Read [Chapter 16](../../chapters/chapter-16-ivf-quantization-and-compressed-vectors.md) and [Chapter 15](../../chapters/chapter-15-exact-knn-to-trees-and-hashing.md) first. Keep one exact oracle and the same scope/metric while changing the candidate index. The [checked record](../../projects/V4/chapter-16-experiment.json) is one local run: IDs, work and quality should reproduce under the pinned inputs, but CPU timings need not.

## A0. Independent bounded mechanism

Implement `nearest_centroid(vector, centroids)`, `encode_subvectors(vector, codebooks)`, and `adc_distance(query, code, codebooks)` in [implement.py](implement.py). Work on equal-dimensional finite vectors with squared L2 distance. Centroid/codeword ties choose the lowest index. Equal-width codebooks partition the vector into consecutive subvectors; encode each against its own book. ADC splits the uncompressed query and sums distances to selected codewords. This fixed-codebook fixture does not train k-means or duplicate the IVF engine.

Use two 2D coarse centroids and a 4D vector with two 2D codebooks. Show coarse assignment, residual `x-centroid`, every subvector/codeword distance, code, decoded residual and reconstruction `centroid+decoded residual`. For residual PQ, pass `q-centroid` to ADC. Verify ADC equals squared distance to the decoded vector, then measure error versus the original and compare a two-item approximate ranking with exact neighbors. The checker uses a fresh 4D fixture and a compression-induced top-1 miss. Approximation error is an outcome to measure, not a failed exactness promise. Keep the existing IVF/PQ error decomposition and negative results.

After your first attempt, run from the repository root:

```powershell
python -X utf8 labs/chapter-16/check_implementation.py
```

The starter intentionally raises `NotImplementedError`. Tests are feedback fixtures, not a concealed grading service. Submit your implementation, hand predictions, checker output and one diagnosis of a failing case. Open the separate chapter solutions only after attempting this task. Existing calculation, experiment and debugging tasks below still apply.

## Run the fixed stage

From the repository root:

```powershell
python -X utf8 -m unittest discover -s projects/V4 -p 'test_ch16.py' -v
python -X utf8 projects/V4/experiment_ch16.py --output projects/V4/chapter-16-experiment-local.json
python -X utf8 visuals/chapter-16/plot-16-01-cells-and-codes.py
python -X utf8 visuals/chapter-16/plot-16-02-quality-cost.py
```

The runner loads the checked Chapter 13 vector snapshot and pinned Chapter 11 query encoder. If the model is not cached, follow [V3 setup](../../projects/V3/README.md) and use `--allow-download` for that pinned public revision. The plotted Figure 16.02 deliberately reads the checked record, not your timing replay. Do not select a replacement index from the inspected Chapter 13 qrels.

## A. Build and probe coarse cells

1. In [Figure 16.01](../../visuals/chapter-16/figure-16-01-cells-and-codes.svg), identify the exact top two for the 38° query, the one-probe result and the missing ID. Name the training-time operation, index-time assignment and query-time probe. Explain why the two nearest points can live in different centroid cells.
2. Trace [the code](../../projects/V4/ivf_pq_ch16.py): `train_kmeans`, `_assign`, `lists`, `search`. For `nprobe=1` and `nprobe=nlist`, count centroid comparisons and explain why all-list IVF-Flat must match the exact oracle. What conditions would break that claim?
3. In the `N=1024,d=32` record, make a table at `nprobe=1,2,4,16` of mean list coverage, IVF-Flat exact-neighbor Recall@2, mean eligible vectors scored and local search p50. Check whether list coverage and Flat recall coincide on every row. Do not infer a production latency curve from these local Python samples.

## B. Quantize residuals, then measure the rank error

4. In Figure 16.01's right-hand example, compute `r=x−c`, its nearest codewords, two-bit payload, reconstruction `x̂`, squared reconstruction error, exact `||q−x||²` and approximate `||q−x̂||²` for `q=(1.2,1.8)`. Explain why those two distances can reorder two passages.
5. For the synthetic `N=1024,d=32,M=8,b=2` case, calculate the packed code bytes/vector, total code bytes, numeric ID bytes, coarse-centroid bytes and codebook bytes. Calculate theoretical payload totals for IVF-Flat, PQ without originals, and PQ plus originals. State at least four costs not included in the bars.
6. Compare full-probe Flat, ADC and top-eight refinement exact-neighbor recall and search p50. Explain which gate prevents the top-eight refinement from reaching one even though all lists were probed. Find one per-query record with an ADC miss and inspect its IDs and work.
7. Hold `nprobe=4` and compare Flat, ADC and refinement with `nprobe=16`. Does more probing monotonically improve ADC recall on these fixed sixteen queries? Why can new approximate competitors change the top two even while oracle-list coverage rises?

## C. Localize V0 regressions and decide

8. In V0, trace `spanish-fee` through exact, one-probe Flat, all-probe Flat, all-probe ADC and top-four refinement. For each, list candidate/context IDs, oracle-list coverage and judged Recall@2. Identify the first losing stage at each miss. Repeat for `code-segment` and explain why its qrel outcome differs even when Flat matches geometric exactness.
9. Report V0 macro judged Recall@2 and geometric Recall@2 for exact, one-probe Flat, all-probe ADC and all-probe refinement. Why is the refinement's `.875` judged score not a validated gain over `.792` exact? Include the twelve-vector training set, question inspection, the median encoder cost and full-scan search time.
10. Use `add` and `delete` on a toy index. State which query result changes immediately, what the tombstone leaves physically present, and what a durable production system would need to rebuild or invalidate. Propose a separate-scope test that prevents a restricted ID entering candidate and context lists. Explain why a caller-provided scope string is not authentication.

## Interview challenge

A colleague says: “We probed every cell, so recall must be exact; the two-byte PQ code proves a 64-fold end-to-end storage saving.” Reply with the all-list ADC quality, the role of original vectors in reranking, the codebook/centroid/ID costs and one qrel failure. Give an experiment gate for a real replacement.

Compare with the [separate worked solutions](../../solutions/chapter-16-solutions.md) only after you have traced the record. A negative deployment decision is a valid result.
