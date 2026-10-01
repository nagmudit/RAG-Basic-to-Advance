# Chapter 6 lab — worked solutions

The arithmetic below uses the [four-record fictional fixture](../projects/V1/toy_ranking_corpus.json), natural logarithms and a **segment** as the DF unit. Scores are rounded for display; the implementation retains full floating-point values for ranking.

## A. Matrix and rank reversal

Before T4, the term-frequency rows are `amber: [2,1,0]` and `blue: [0,2,1]` for T1–T3. `N=3` and both `df=2`, hence each IDF is `ln(3/2)=0.405465`. Nonzero raw weights are `amber: [0.810930,0.405465,0]`, `blue: [0,0.810930,0.405465]`. Summed scores are `T1=0.810930`, `T2=1.216395`, `T3=0.405465`; rank **T2 > T1 > T3**.

After adding T4, the frequency rows become `amber: [2,1,0,0]`, `blue: [0,2,1,1]`. `N=4`, `df(amber)=2`, `df(blue)=3`; IDFs are `ln 2=0.693147` and `ln(4/3)=0.287682`. Weights are `amber: [1.386294,0.693147,0,0]`, `blue: [0,0.575364,0.287682,0.287682]`. Scores are `T1=1.386294`, `T2=1.268511`, `T3=T4=0.287682`; rank **T1 > T2 > T3 > T4**, with the T3/T4 tie resolved by numeric ID. The added blue segment changed both corpus statistics while T1/T2 TF remained fixed. Figure 6.01 visualizes these exact cells; axes are eligible segment and analyzed term, color represents a dimensionless weight, and no measurement uncertainty or random seed applies.

## B. Variants and norms

After T4, raw scores are `T1=1.386294` and `T2=1.268511`. Under sublinear TF, `tf=2` becomes `1+ln2=1.693147`. Thus `T1=(1+ln2)×ln2=1.173600`; `T2=ln2+(1+ln2)×ln(4/3)=1.180235`. T2 stays narrowly ahead. The field-boost code transforms each integer title/body count separately, then multiplies the title component by the chosen positive boost; taking `ln(0.1)` of a boosted title count would incorrectly turn a positive match negative.

For the declared cosine variant after T4, `q=(a,b)=(0.693147,0.287682)`, `T1=(2a,0)=(1.386294,0)` and `T2=(a,2b)=(0.693147,0.575364)`. `||q||=sqrt(a²+b²)≈0.750476`; `||T1||=1.386294`; `q·T1=2a²≈0.960906`; cosine `T1≈0.923610`. `||T2||=sqrt(a²+(2b)²)≈0.900831`; `q·T2=a²+2b²≈0.645975`; cosine `T2≈0.955511`. Values may vary in the last displayed digit if intermediate numbers are rounded early. The score describes angle in this sparse weighted space, not probability that the passage or answer is correct. The [local explainer](../projects/V1/tfidf.py) returns per-term `tf`, `df`, `N`, `idf` and contribution; its raw contributions sum to the ranked score within floating-point tolerance.

## C. Zero cases and scope

With two `blue`-only eligible segments, `N=df(blue)=2`, so `idf(blue)=ln1=0`. Both are posting matches and returned as zero-score candidates. `never-seen` has no posting and returns no candidates. A zero query or document vector makes cosine's denominator zero; this implementation assigns score zero to a matched candidate. `df=0` is skipped rather than divided by, and `N=0` means no eligible candidates. An `idf+1` convention would assign nonzero weight to a universal term and can alter ranking; it is a different, valid *declared* convention, not an algebraically invisible patch.

On V0, support has 12 eligible segments and no `thirty-minute` posting; legal has one eligible segment and one such posting. Support-side `df` excludes D10. The in-memory `support-team` parameter is only a lab fixture. A real revocation must update or override eligibility before serving and invalidate stale statistics/index views and tenant-safe caches; a postponed rebuild must not allow content exposure.

## D. Paired V1 experiment

The [checked-in record](../projects/V1/chapter-06-experiment.json) fixes the V0 snapshot, V0 analyzer, support scope, 120 source-word context budget, query set `ch06-four-query-v1`, `k=2,8`, and seed `6062026`. The two V0 tasks have fixture-required IDs: `D1:§3:0` plus `D2:§2:0`, and `D1:§8:0`. At `k=2`, overlap covers 2/2 and answers the dated change, while raw/sublinear/cosine cover 1/2 and abstain. For termination, overlap and cosine cover 0/1 and abstain; raw and sublinear cover 1/1 and answer. At `k=8`, all four modes cover the required evidence and the deterministic stub answers both tasks. The rare-numeric and absent queries have no answer labels, so they are diagnostic work slices only.

One defensible experiment card says: **Question:** Does TF-IDF improve required-evidence coverage at a fixed small depth? **Hypothesis:** weighting helps at least one task but may hurt another; no universal improvement is assumed. **Baseline:** Chapter 5 distinct overlap. **Independent variable:** four score modes. **Controls:** index, analyzer, snapshot, scope, question IDs, top-k and context budget. **Metric:** required IDs in candidates and context with per-task denominator, stub status, search microseconds and build cost. **Result:** raw/sublinear repair termination but lose the old governing clause for the dated change at k=2; cosine does not repair termination. **Decision:** retain variants as experiments and failure fixtures; defer a quality winner until reviewed qrels and more tasks in Chapter 9. **Limits:** two known-answer labels, tiny static corpus, local seven-sample timings, no LLM, no online workload or human relevance judgments. In the checked-in run, `q-contract-change`, k=2, median search-only times were overlap 24.7 µs, raw 33.8 µs, sublinear 45.1 µs, cosine 36.5 µs. These are observations, not a production speed ratio.

## E. Failure localization

For the dated change, raw TF-IDF finds `D1 §3` but ranks it fifth; the first lost boundary at k=2 is **ranking/candidate depth**, before context or prompt. A stronger prompt cannot include a missing source. For termination, overlap ranks `D1 §8` third, while raw and sublinear move it to second; the term weights change selection even though the source and analyzer are fixed. One gain cannot erase the contract loss. A raw score of 6.1 and a cosine score of 0.3 have different scales/formulas, may use different scope-local `N`/`df` and different queries, and say nothing directly about authority, answer faithfulness or reliability. A permission gate remains independent of both.

## F. Continuity

Index time prepares postings, scope-local DF and cosine document norms. Query time analyzes once, accumulates contributions from eligible postings, optionally normalizes, sorts and selects. An analyzed field length counts terms in one field; a vector norm is the square root of summed squared **weighted coordinates across the whole vocabulary**. An absent query term adds zero and does not impose an AND condition; a universal term can yield a zero score while still matching. Updating the source collection can change all IDFs, so an experiment pins the corpus and scorer version. Chapter 7 asks whether BM25's term saturation and length normalization serve these workload slices better, with Chapter 5 overlap and Chapter 6 variants retained as baselines.

## Independent bounded mechanism: reasoning and answer

Count eligible-document DF once per document, compute unsmoothed IDF, form raw-TF document weights and distinct-term query weights, then normalize full vectors. The denominator explains why adding a nonquery rare term can lower cosine.

The separate [worked implementation](code/chapter_06_mechanisms.py) uses standard-library code and imports no supplied project engine or learner scaffold. After comparing your reasoning, verify it on the new fixtures:

```powershell
python -X utf8 labs/chapter-06/check_implementation.py --implementation solutions/code/chapter_06_mechanisms.py
```

Rubric: correct intermediate mechanism (40%), deterministic and edge-case behavior (20%), independently written code (20%), and explanation of exact parity or measured approximation failure (20%). Passing output alone is insufficient. A loop-based implementation is appropriate; premature abstraction is unnecessary.
