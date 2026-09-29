# Chapter 7 lab — worked solutions

All scores below use the [fictional fixture](../projects/V2/toy_length_corpus.json), natural logarithms, segment-level statistics and full precision in the [V2 scorer](../projects/V2/bm25.py). Display values are rounded. A different IDF or field policy gives different numbers.

## A. Scope, arithmetic and rank

The support-team segments S1–S4 have analyzed lengths 2, 10, 2 and 2 terms. `N=4`, `avgdl=4`, `df(amber)=2`, and `idf_B(amber)=ln(1+(4−2+0.5)/(2+0.5))=ln(2)=0.693147`. S1 and S2 each have `tf=2`. At `k1=1.2,b=.75`, S1 has `K=1.2(.25+.75×2/4)=.75`, factor `4.4/2.75=1.6`, score **1.109035**. S2 has `K=1.2(.25+.75×10/4)=2.55`, factor `4.4/4.55≈.967033`, score **0.670296**. The only matching eligible candidates are S1 and S2, in that order.

For `b=0`, both have `K=1.2` and score `ln(2)×4.4/3.2≈0.953077`; S1 wins only by the fixed tie rule. Raw TF-IDF uses `ln(N/df)=ln(2)` multiplied by raw `tf=2`, so both score **1.386294**. The BM25 length difference comes solely from `b`; the TF-IDF/BM25 comparison also changes the term-frequency formula and therefore cannot isolate length on its own. S5 belongs only to `legal-team`: it does not enter support `N`, `df`, `avgdl`, candidates or ordinary trace. A legal-only change must not change support statistics under this static scope-local policy.

## B. Controls and plot

At `L_d=avgdl=4`, `K=1.2`. For `tf=1,2,4`, the factors are `2.2/2.2=1`, `4.4/3.2=1.375`, and `8.8/5.2≈1.692308`. The factor approaches `1+k1=2.2` as `tf→∞`. Repetition helps but each additional occurrence contributes less. For `tf=2`, `b=0` gives the same factor 1.375 at lengths 2 and 10. For `b=.75`, length 2 gives 1.6 and length 10 gives about .967033. In the plot, panel A's horizontal axis is term occurrences; panel B's is analyzed segment length in terms; both vertical axes are dimensionless **pre-IDF term factors**. The curves are exact outputs of the code, so sampling error bars and a random seed would misdescribe them. A long policy containing several governing clauses may be unfairly penalized by a large `b`.

## C. Code and edge cases

For fictional S2 and query `amber filler`, `explain()` returns `tf=2` for amber and `tf=8` for filler, with `df=2`, `idf=ln(2)`, `L_d=10` and `avgdl=4` for both. The contributions are approximately **0.670296** and **1.156340**, summing to S2's search score **1.826636**. `build_bm25_index()` prepares eligible lengths, `N`, `df` and `avgdl`; `search()` checks eligible ordinals before adding contributions or fetching candidate records. The exact sort follows accumulation. An absent posting or missing scope yields zero candidates. For two eligible `blue`-only segments, `N=df=2`, `idf_B=ln(1+0.5/2.5)=ln(1.2)>0`, so both remain scored candidates. Chapter 6's `ln(N/df)` would give them **zero score but still two candidates**. Invalid `k1≤0`, nonfinite `k1`, `b` outside `[0,1]`, nonfinite `b`, and nonpositive/nonfinite title boosts raise `ValueError`. The combined-field title multiplier has no separate per-field `avgdl` or saturation and is not BM25F.

## D. Controlled V0 comparison

The checked-in [experiment](../projects/V2/chapter-07-experiment.json) fixes the source, analyzer, scope, queries, depth, context budget and stub. At top two:

| Task | Overlap | Raw TF-IDF | Cosine | BM25 `b=0` | BM25 `b=.75` |
|---|---|---|---|---|---|
| Dated change: 2 required spans | 2/2 in context; answered | 1/2; abstained | 1/2; abstained | 1/2; abstained | 1/2; abstained |
| Termination: 1 required span | 0/1; abstained | 1/1; answered | 0/1; abstained | 1/1; answered | 1/1; answered |

For the dated change, BM25 `b=.75` ranks `D2 §2` first, `D3 FAQ-7` second and `D1 §3` **fourth**. Its `b=0` variant ranks `D1 §3` fifth. For termination, both BM25 variants rank `D1 §8` second. At top eight, every method places required spans in context for both tasks and the unchanged stub answers. The rare numeric and no-result cases have no required-evidence label and therefore no correctness denominator. The recorded search-only median for dated-change/top-two is 23.7 µs overlap, 32.6 µs raw TF-IDF, 35.0 µs cosine, 46.8 µs BM25 `b=0`, and 47.4 µs BM25 `b=.75` in that single local run; consult the record for raw samples and nearest-rank p95. There are only seven samples and 13 indexed segments. Build timings are separate, and this is not a production latency result. The experiment's top-two hypothesis is falsified by the missing contract span.

An appropriate decision is to **retain BM25 as a transparent V2 comparator**, not to claim a winning setting. Chapter 9 must add reviewed qrels, rank-sensitive metrics, a larger query set and development/test separation. The present fixture exposes two opposite outcomes and a missing governing clause worth preserving as a regression. It cannot establish overall relevance or LLM answer quality.

## E. Failure localization and oral defense

The dated-change failure first occurs at **candidate ranking/depth**: `D1 §3` is indexed and eligible, but sits below the top-two cutoff; it never reaches context. Prompt wording cannot restore missing evidence. A title boost could be tested as a new independent variable on labeled data, but this result alone does not justify tuning it. For termination, BM25 moves `D1 §8` into top two, which is a specific evidence-coverage gain. The simultaneous dated-change loss prevents a general superiority claim.

A BM25 score of 5.6 is an uncalibrated sum of formula contributions, not 56% or any other answer probability. A candidate may be out of context; a context passage may be stale, in conflict, or insufficient; the stub's output is not a model-quality judgment. Calibration would need labels, a declared score population and validation of the intended event. BM25+ guards a matched-term lower bound in very long documents; BM25F models separate fields; a smoothed query-likelihood model estimates query generation from document and collection frequencies; exact/fuzzy matching changes which candidates can enter scoring. None grants authorization or verifies a final claim. Chapter 8 asks how to return the **same exact top-k** with less scoring work. Chapter 9 asks which ranks are actually relevant across a defensible judged query set.
