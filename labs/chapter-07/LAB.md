# Chapter 7 lab — Make BM25's length decision visible

**Prerequisites:** Chapters 3, 5 and 6; V1's fixed positional index and ranking experiment. **Deliverables:** one hand-worked BM25 trace, a parameter-control table and plot explanation, an executable V2 comparison card, three failure diagnoses, and a short oral defense. The fixture is fictional. Its two required-evidence sets are not complete qrels; the answer stub is deterministic, not an LLM.

## A. Calculate before running the scorer

Read [toy_length_corpus.json](../../projects/V2/toy_length_corpus.json). Under `support-team`, query `amber` with `k1=1.2`, `b=.75`, title boost 1. Treat one indexed **segment** as the corpus unit. Write down every eligible segment length, `N`, `df(amber)`, `avgdl`, `idf_B(amber)`, `tf` for S1 and S2, both `K_d` values, both term factors and both scores. State the rank and the candidate count. Keep at least six decimal places internally.

Compute the same two scores with `b=0`. Then compute their Chapter 6 raw TF-IDF scores. Explain precisely what changed in each comparison. Why is legal-only S5 excluded even though it has four `amber` occurrences? If S5 is added or removed from the *legal* scope, which support-team quantities may change under this lab policy?

## B. Probe the controls and figure

At `L_d=avgdl=4`, calculate the BM25 factor for `tf=1,2,4` with `k1=1.2`. Identify the upper limit as `tf` grows; explain why the factor at four occurrences is below four times the factor at one. Now keep `tf=2` and compare lengths 2 and 10 for `b=0` and `b=.75`. Predict the direction of the curves before opening [Figure 7.01](../../visuals/chapter-07/figure-07-01-bm25-controls.svg).

Regenerate the plot with `python -X utf8 visuals/chapter-07/plot-07-01-bm25-controls.py`. Identify its horizontal and vertical units, fixed assumptions, where the panels meet, and why there are no error bars. Explain one real workload in which stronger length normalization might hurt.

## C. Inspect and extend the implementation

Run from the repository root:

```powershell
python -X utf8 -m unittest discover -s projects/V2 -p 'test_*.py' -v
python -X utf8 projects/V2/bm25.py --query-id q-contract-change --top-k 2
python -X utf8 projects/V2/bm25.py --query-id q-termination --top-k 2 --b 0
```

In a small scratch file, implement the term factor from the chapter without importing `saturation()`, then compare your values for the cases above to `bm25.saturation()`. Use the local `explain()` helper on fictional S2 for `amber filler`; show that its two contributions sum to S2's search score. Do not turn that term-level output into a general query log. Inspect where `df`, `lengths` and `avgdl` are built and where eligibility is applied in the query loop. Explain why Chapter 8 can change execution without changing the score.

Probe `amber` under a missing scope, a term absent from all eligible postings, and a term present in **every** segment of a two-segment scope. State candidate count and whether `idf_B` is zero. Compare these outcomes with Chapter 6's IDF convention. Try invalid `k1`, `b` and title boost; state the bounds the code enforces. Explain why the optional title boost does not make this BM25F.

## D. Keep the controlled comparison honest

Run `python -X utf8 projects/V2/experiment_ch07.py --output projects/V2/chapter-07-experiment-local.json`, then inspect the checked-in [raw result](../../projects/V2/chapter-07-experiment.json). Hold source snapshot, V0 analyzer, eligibility scope, query text, context budget, top-*k* and stub fixed. Compare overlap, raw TF-IDF, cosine, BM25 `b=0` and BM25 `b=.75` at depths 2 and 8. For each V0 task, record candidate IDs and rank of required spans, required spans in selected context, stub status, scored-segment count and search-only median/p95 from the seven raw samples. Keep build times separate. Record the rare numeric and no-result probes without inventing answer labels for them.

Write an [experiment card](../../evaluation/EVALUATION_EXPERIMENT_CONTRACT.md): question and falsifiable hypothesis; baseline and variable; controls, data/code/index versions and frozen query set; required evidence IDs and denominators; per-task results; at least two failures or limitations; latency/build observations; and a decision for what Chapter 9 must measure before tuning `k1` or `b`. Do not compare raw score magnitudes across different methods. Do not call the fixture stub status answer correctness.

## E. Diagnose and defend

1. BM25 `b=.75` ranks `D2 §2` first for the dated change but the stub abstains at top two. Find the first stage where `D1 §3` is lost. Would changing the prompt or the title boost be a justified repair from this evidence alone?
2. BM25 retrieves `D1 §8` at rank two for termination; overlap does not. What does this show, and what does the dated-change failure prevent you from concluding?
3. A colleague says a BM25 score of 5.6 means a 56% chance of a supported answer. Locate every category error: score interpretation, candidate/context distinction, source authority, answer verification and calibration.

Orally contrast BM25 with BM25+ (long-document lower bound), BM25F (field-specific normalization), smoothed query likelihood (estimated query-generation probability), and exact/fuzzy candidate matching. State where each may help and what it cannot solve. Explain why source authorization must precede ranking. End with the question Chapter 8 answers about scoring work and the new judgments Chapter 9 must provide.

**Passing submission:** numerical values match the scorer; the fixture's length effect and `b=0` control are isolated; both the termination gain and contract loss are reported; scope statistics do not leak legal-only S5 into support ranking; search timing is separate from build and answer status; and no BM25 score is called a calibrated relevance probability. Consult the [separate solutions](../../solutions/chapter-07-solutions.md) only after completing your own calculations.
