# Chapter 09 lab — Judge first, then score the ranking

**Prerequisites:** Chapters 3 and 5–8, including the V2 BM25 and WAND stage. **Time:** about 100–130 minutes. Read [Chapter 9](../../chapters/chapter-09-relevance-judgments-and-ranking-metrics.md) before starting. Work from the repository root with Python 3. Keep your own calculations separate until you have attempted the [solutions](../../solutions/chapter-09-solutions.md).

## Deliverables

Submit a three-ranking calculation sheet, a short qrel/rubric audit, a small metric function written independently from the project implementation, a reproducible experiment card and a one-page failure diagnosis. Include the source snapshot, query-set and rubric versions whenever you report a score. Do not tune the retrievers on this tiny judged set and then present the same run as held-out evidence.

## 1. Fix the judgment universe

Open [the frozen judgments](../../projects/V2/judgments_ch09.json) and [V0 corpus](../../projects/V0/corpus.json). Answer before running any ranker:

1. What is the retrieval unit, source snapshot, eligibility scope, number of judged pairs and grade threshold for binary relevance? How does the loader know a new chunking/index snapshot would invalidate the qrels?
2. For `q-contract-change`, name all grade-2 segments and one grade-0 decoy. Explain why Hit@2 can be 1 while the dated comparison is missing necessary evidence.
3. Explain the different grades of `D9:proposal-2:0` for `q-unsigned-proposal` and `q-current-target`. Explain why the legal-only D10 is outside the support-team judgment roster instead of a grade-0 support-team item.
4. In a hypothetical large corpus, pool the top three results from overlap and BM25 plus an expert Boolean search. If a new dense retriever returns an item outside the pool, is it grade 0, grade 1, grade 2 or unjudged? Specify how you would update the pool and assessors' record.

## 2. Calculate three rankings by hand

Use four fictional items with qrels `A=2`, `B=1`, `C=0`, `D=0`. Binary relevance means grade at least 1. Evaluate three top-three rankings:

- `R1 = [A,B,C]`
- `R2 = [C,B,A]`
- `R3 = [B,C,A]`

For each, calculate `P@2`, `Recall@2`, `Hit@2`, `F₁@2`, `RR@2`, `AP@2`, `DCG@2`, `NDCG@2`, then `AP@3` and `NDCG@3`. Show intermediate precision at each relevant rank and the ideal DCG. Use `gain(g)=2^g−1` and `discount(i)=log₂(i+1)` for rank *i*. Identify one metric that cannot tell whether a grade-2 item was found by rank two.

Now consider `R4=[]` and qrels `A=0,B=0`. State which measures are undefined under this chapter's policy and what no-positive behavior is reported. Explain why returning B would not improve a retrieval quality score.

## 3. Implement and check your own metric core

In a temporary Python file, implement `precision_at_k`, `recall_at_k`, `ap_at_k` and `ndcg_at_k` from the definitions above. Use the complete grade dictionary, not only retrieved items, for recall, AP and ideal DCG. Explicitly reject duplicate returned IDs. Decide how your functions express `R=0`; document it. Test your output on R1–R3 before comparing it with [the project implementation](../../projects/V2/eval_ch09.py):

```powershell
python -X utf8 projects/V2/eval_ch09.py
python -X utf8 -m unittest discover -s projects/V2 -p 'test_*.py' -v
```

What would go wrong if AP@2 divided by the number of **retrieved** relevant items? What would go wrong if IDCG sorted only the returned list?

## 4. Run the paired V2 baseline

Write to a **new** path to preserve the checked-in observation:

```powershell
python -X utf8 projects/V2/experiment_ch09.py --output projects/V2/chapter-09-experiment-local.json
python -X utf8 visuals/chapter-09/plot-09-01-ranked-gain.py
```

The local JSON is a scratch artifact and need not be committed. Compare overlap, exhaustive BM25 and exact WAND at *k*=2 and 8. Extract macro NDCG, binary Recall, direct recall, MAP, zero-positive candidate rate, p50/p95 search-only microseconds and scored-segment count. Inspect `q-contract-change`, `q-termination`, `q-urgent-arrival`, `q-unknown-renewal` and `q-private-target` individually. Verify that BM25 and WAND have identical ordered IDs and raw scores at every recorded depth. Your measured latency may differ from the checked-in run.

Use this experiment card:

```text
Question, hypothesis and decision rule:
Primary baseline and changed variable; exact-execution control:
Source, analyzer, scorer, qrel/rubric and query-set versions:
Eligible unit and scope; query counts and workload slices:
Metric formulas, cutoff, zero-positive and unjudged policy:
Timing window, units, sample count, order/seed and exclusions:
Per-query and aggregate results, including negative cases:
Candidate → selected context → stub/answer distinction:
Assessor limitations, uncertainty, conclusion and next action:
```

## 5. Debugging and oral defense

- If a report says “MRR@2 is high, so the contract question is solved,” identify the denominator or missing requirement that makes the claim false.
- If a new vector retriever finds a truly relevant but unpooled document, describe the likely evaluation bias when unjudged is treated as nonrelevant.
- If a source update changes `D2 §2`, list the qrel, index and trace versions that must be checked before comparing scores.
- Suppose the top two include both grade-2 segments but context packing drops one. Which stage failed? Which Chapter 9 metric stays unchanged? What must later core RAG evaluation add?
- Defend why the current negative BM25 aggregate result should be retained, and what larger split/assessor design would be needed before a tuning or deployment claim.

End with a from-memory sketch: `frozen corpus + information needs + judgments → ranked candidate IDs → metrics`, with authorization as a gate and context/answer as separate downstream stages.

As the **Part II checkpoint**, extend the sketch backward through V0 scan, V1 analyzer/postings/TF-IDF and V2 BM25/WAND. Answer the chapter's five cumulative questions and compare one measured gain and one retained failure across versions.

## 6. Complete the BM25 parameter selection

Use workload `ch09-bm25-devtest-v1`, not the already inspected fourteen-query Chapter 09 diagnostic set. The [new manifest](../../projects/V2/judgments_bm25_tuning.json) has six development and six test queries; each group has five positives and one no-eligible-evidence query over the same twelve eligible segments. Only new question wording/IDs are held out; the author already knows the sources. Read the development group first. Do not inspect test grades or the reference runner/solution until you have frozen your choice. The files are public, so this is a procedural learning gate, not a secret grading service.

1. Write your own small grid driver using the existing BM25 scorer and your Chapter 09 metrics. Evaluate twenty parameter pairs: k1 in [.8,1.2,1.6,2] and b in [0,.25,.5,.75,1]. Keep analyzer, scope, title boost 1, top-k=2 and corpus fixed. Select by macro positive-query NDCG@2; report no-evidence behavior separately.
2. Before evaluating test, save a JSON decision record with workload/corpus/query/qrel/evidence-manifest identities, analyzer, grid, development scores, selection metric, parameters and tie rule. Predeclare ties: default first, then closest L1 distance to (1.2,.75), then numeric order. A tie is a legitimate result.
3. Freeze that file. Evaluate only its selected setting and the unchanged default on the test group. Report agreement, operations, price, other-product and no-evidence slices, raw candidate IDs/scores, scoring work, and a warmed paired local latency diagnostic. State what this six-query test cannot establish. Never return to development selection after seeing test.
4. Compare with the [reference runner](../../projects/V2/tune_bm25_ch09.py) after your attempt. Explain how `select_parameters(base, development)` excludes test inputs; alter test labels in a scratch copy and confirm the selected parameters stay the same. Retain the original Chapter 09 overlap/BM25/WAND results as inspected diagnostics.

```powershell
python -X utf8 projects/V2/tune_bm25_ch09.py --output projects/V2/chapter-09-tuning-local.json
python -X utf8 -m unittest discover -s projects/V2 -p 'test_bm25_tuning.py' -v
```

Submit your grid driver, frozen choice, held-out report and a short explanation of why changing the workload can change a score without improving the engine.
