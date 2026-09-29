# Chapter 6 lab — Make every lexical rank explainable

**Prerequisites:** Chapters 3 and 5, the V0 frozen questions, and the Chapter 5 V1 index. **Deliverables:** a hand-worked sparse matrix and rank reversal, three scoring-function traces, one controlled V1 comparison card, a failure diagnosis, and the V0/V1 regression output. This lab uses fictional sources, no model API, and no general qrels.

## A. Predict the ranking reversal before running code

Read [toy_ranking_corpus.json](../../projects/V1/toy_ranking_corpus.json). First use only T1–T3. For query `amber blue`, build a two-row term–segment table of raw term frequencies. Compute `N`, `df(amber)`, `df(blue)`, both values of `ln(N/df)`, every nonzero `tf×idf` cell, each document's **sum over distinct query terms**, and the ranking. Then add only T4 and recompute. Explain why old document text can keep the same TF but receive a new score. Write your calculations with six decimal places internally and round displayed answers to three decimals.

Check your hand matrix against [Figure 6.01](../../visuals/chapter-06/figure-06-01-sparse-tfidf-matrix.svg). Regenerate it with:

```powershell
python -X utf8 visuals/chapter-06/plot-06-01-sparse-tfidf-matrix.py
```

The plot requires matplotlib; the scorer and tests use only the Python standard library. Identify its axes, units, exact data source, and why no error bar or seed is appropriate.

## B. Change the weighting rule, one choice at a time

For the four-record fixture, use the formula in the chapter to calculate T1 and T2 under:

1. raw TF-IDF;
2. sublinear `1+ln(tf)` for positive term counts;
3. cosine with document coordinate `tf×idf` and binary-query-TF coordinate `idf`.

For cosine, show the full query and document norms and the dot product. Which rule keeps T2 ahead after T4 is added? Does a cosine score of about 0.956 mean 95.6% probability of relevance? Test your answers against [`tfidf.py`](../../projects/V1/tfidf.py):

```powershell
python -X utf8 -m unittest discover -s projects/V1 -p 'test_*.py' -v
python -X utf8 projects/V1/tfidf.py --mode raw --top-k 2
python -X utf8 projects/V1/tfidf.py --mode cosine --top-k 2
```

Write a short scratch script that calls `explain(index, "amber blue", "T2:body:0")`; verify that raw term contributions sum to its score. Keep such per-term explanation output local to this fictional corpus. Try `title_boost=0.1` on a title-only query and explain why the reference sublinear implementation transforms integer counts *before* applying the field boost.

## C. Make edge cases explicit

Construct two eligible segments both containing only `blue`. Under `idf=ln(N/df)`, calculate `idf(blue)` and the number of returned candidates for `blue`. Compare with the query `never-seen`. Then explain the no-result, zero-score, and zero-vector cases separately. State the rule for `df=0`, `N=0`, and a zero cosine denominator. Why would adding an arbitrary `+1` to the IDF formula change the implementation contract?

On the V0 snapshot, inspect the `support-team` and `legal-team` counts for `thirty-minute`. Explain why scope-local `df` protects the support score from the legal-only D10 record, and why the lab's caller-supplied scope still does not constitute authentication. What must happen to statistics and caches when source eligibility changes?

## D. Compare with the same V1 candidate path

Run:

```powershell
python -X utf8 projects/V1/experiment_ch06.py --output projects/V1/chapter-06-experiment-local.json
python -X utf8 -m unittest discover -s projects/V0 -p 'test_*.py' -v
```

Inspect the checked-in [raw result](../../projects/V1/chapter-06-experiment.json). The independent variable is overlap, raw TF-IDF, sublinear TF-IDF, or cosine. Hold source snapshot, analyzer, scope, `k`, context budget, query text and answer stub fixed. At `k=2` and `k=8`, record for each frozen task: candidate IDs/ranks, required evidence in candidates, required evidence in context, stub answer status, and search-only median latency. Use the record's seven raw samples and nearest-rank p95 without claiming a stable production tail. Keep postings and statistics build times separate.

Write an [experiment card](../../evaluation/EVALUATION_EXPERIMENT_CONTRACT.md) with a falsifiable hypothesis, baseline, controls, fixture-required evidence IDs, denominators, per-task results, weak or negative findings, latency and security implications, conclusion and limitations. Explain why the two known required-evidence sets are not a full qrel dataset. Do not collapse candidate coverage, context coverage and answer correctness into one number.

## E. Diagnose three disagreements

1. The raw scorer ranks `D2 §2` first for the dated change but the V0 stub abstains at `k=2`. Trace the first stage where the needed old clause disappears. Would changing the prompt fix that stage?
2. Overlap abstains on the termination request at `k=2`, while raw TF-IDF answers. Inspect title matches, rare terms and the `D1 §8` rank. Why is one success insufficient to claim TF-IDF is better overall?
3. A colleague compares a score of `6.1` from raw TF-IDF for one query with a cosine score of `0.3` for another tenant and says the first answer is twenty times more reliable. List the score-definition, scope-statistics, query and evidence/answer errors.

## F. Oral defense and project continuity

Explain from memory: index-time `df` and norm preparation; query-time posting accumulation; the difference between field length and vector norm; why a missing query term contributes zero without forcing an empty result; why `idf=0` is distinct from no posting; how source additions can change ranks; and which failure Chapter 7's BM25 is intended to examine. Show the Chapter 5 overlap engine and Chapter 6 scorer side by side. V0 remains unchanged, and the Chapter 6 scorer retains a regression where a governing clause falls to rank five.

**Passing submission:** all matrix weights and rankings match the fixture; each variant's definition is stated before its score; the ranking reversal is explained by changed `N` and `df`; authorization is a hard gate; both favorable and unfavorable top-two results are reported; raw timing and build cost are kept separate; and no deterministic stub status is presented as an LLM-quality result. Read the [separate solutions](../../solutions/chapter-06-solutions.md) after your own calculations.
