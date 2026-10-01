# Chapter 15 lab — Prove a prune, then measure a miss

Read [Chapter 15](../../chapters/chapter-15-exact-knn-to-trees-and-hashing.md) before starting. The goal is to keep **safe exact pruning** separate from **approximate candidate loss**. The [checked record](../../projects/V4/chapter-15-experiment.json) is one local run; replay timings can differ. The V0 qrels were inspected in Chapter 13 and serve as regressions, not a new held-out model-selection set.

## A0. Independent bounded mechanism

Implement one-table random-hyperplane LSH in [implement.py](implement.py): `signature(vector, planes)`, `build_lsh(documents, seed=15, bits=3, planes=None)`, and `lsh_search(index, documents, query, k=2)`. Documents are an already eligible ID-to-vector dictionary. Sample each plane's coordinates with a local seeded `random.Random(seed).gauss(0,1)`; a nonnegative dot product is bit 1. Store planes and signature-to-sorted-ID buckets. Optional supplied planes allow hand checking. Query only its exact-signature bucket, score those candidates by cosine, then rank descending score/ascending ID. Return actual `candidate_ids` and `ranking`; an empty bucket returns both empty. Reject a zero or dimension-mismatched query.

Show planes, document signatures, bucket contents and the query signature on your own 2D fixture. Compare top-1 with an exhaustive cosine oracle for at least two queries, including a boundary miss; report geometric recall and scored candidates. The unseen-in-the-prose fixture deliberately has Recall@1=0.5. Explain why changing bits may trade work for recall. Do not claim exact parity, relevance recall, or multi-table production LSH from this one-table exercise.

After your first attempt, run from the repository root:

```powershell
python -X utf8 labs/chapter-15/check_implementation.py
```

The starter intentionally raises `NotImplementedError`. Tests are feedback fixtures, not a concealed grading service. Submit your implementation, hand predictions, checker output and one diagnosis of a failing case. Open the separate chapter solutions only after attempting this task. Existing calculation, experiment and debugging tasks below still apply.

## Run the fixed stage

From the repository root:

```powershell
python -X utf8 -m unittest discover -s projects/V4 -p 'test_*.py' -v
python -X utf8 projects/V4/experiment_ch15.py --output projects/V4/chapter-15-experiment-local.json
python -X utf8 visuals/chapter-15/plot-15-01-partitions-and-buckets.py
python -X utf8 visuals/chapter-15/plot-15-02-latency-recall.py
```

The runner loads the pinned Chapter 13 snapshot and the cached Chapter 11 model. If the model is not cached, use the [V3 setup instructions](../../projects/V3/README.md) and pass `--allow-download` once; the experiment does not silently change model revision. Compare IDs, recall and work before comparing replay timing. Figure 15.02 reads the checked record, so it does not change when the local replay differs.

## A. Audit exactness and pruning

1. For passage vectors `(0,0)`, `(0,2)`, `(2,0)`, `(2,2)` and query `q=(.9,.1)`, calculate all four Euclidean distances. Draw a median split at `x=1`. After searching the left child, write the current worst distance for `k=1` and `k=2`. Compute the right-box lower bound and decide whether pruning is legal in each case. State the stable tie rule.
2. In [the KD implementation](../../projects/V4/ann_ch15.py), identify where the axis and median are chosen, the bounding box is formed, a nearer child is visited, and a branch is pruned. Explain why backtracking matters. Run `test_ch15.py` and identify what it checks across 2, 8 and 32 dimensions.
3. A ball has center `c`, radius `.5`, and the query is distance `2` from `c`. Derive its lower bound. May the ball be pruned when the current worst top-*k* distance is `1.4`? What if it is `1.6`? Explain why this bound uses the triangle inequality rather than coordinate ranges.
4. Inspect synthetic cases `N=2048,d=2` and `N=2048,d=32` in the record. State the mean vectors scored by exact and KD, ordered-rank parity, and search p50. Explain why one case is a success for KD and the other a failure **of efficiency**, not correctness.

## B. Construct a lossy hash

5. Derive `p=1−θ/π` for one hyperplane as the probability supplied by the angular hash model. For `θ=60°`, calculate one-bit, four-bit one-table, and four-bit/four-table collision probabilities. Name the independence assumption. Say why a pairwise collision probability is not exact-neighbor Recall@2 on a full corpus.
6. Trace [the LSH code](../../projects/V4/ann_ch15.py): seed, planes, signatures, bucket union, eligibility check, cosine refinement and empty-bucket behavior. Figure [15.01](../../visuals/chapter-15/figure-15-01-partitions-and-buckets.svg) uses twelve two-dimensional points. Identify the exact top two and the LSH candidate union. Explain why no later scoring step can restore the missing ID.
7. In the V0 record, hold bits at four while comparing `L=2,4,8`; then hold tables at four while comparing bits `h=4,6,8`. Report scored-vector mean, exact-neighbor Recall@2, judged macro evidence Recall@2 and search-only p50 for each. Do the observed directions fit the usual table/bit trade-off? Is any V0 LSH configuration justified as a replacement? Include query encoding and build cost in your answer.

## C. Localize a candidate failure

8. Inspect `style-ticket`, `acronym-sla`, `code-segment` and `none-private`. For each, separate: eligible source, exact geometric top-two, LSH two-table/four-bit candidates, direct qrel, selected context IDs and unrun answer. Identify one **approximation miss**, one **representation/metadata failure**, and one **no-evidence or authorization boundary**. D10 is outside the support-team judgment universe, not a negative example.
9. Design a next experiment on a larger held-out workload. Specify snapshot/model/index pins, questions and complete qrels, scope/filtered queries, multiple LSH seeds, exact-neighbor and judged evidence metrics, build and refresh time, raw/index bytes, warm/cold p50/p95, query encode/search/refine boundaries, no-result policy and acceptance gate. Explain how you would prevent repeated tuning on Chapter 13's inspected cases.

## Interview challenge

A teammate says, “Our KD tree visited fewer points, so it must be faster; our LSH matched qrel recall, so it must be safe.” Give two counterexamples from the checked V0 record. Then say which traces and denominators are required before changing the candidate route.

Compare with the [separate worked solutions](../../solutions/chapter-15-solutions.md) after completing your trace. A negative decision is acceptable when the saved evidence supports it.
