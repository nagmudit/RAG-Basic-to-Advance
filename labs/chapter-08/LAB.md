# Chapter 08 lab — Prove a skip, then measure it

**Prerequisites:** Chapters 5–7 and the V2 BM25 stage. **Time:** about 90–120 minutes. Use Python 3 and the repository root as your working directory. Read [Chapter 8](../../chapters/chapter-08-production-lexical-query-execution.md) first. Keep your written answers separate from the [worked solutions](../../solutions/chapter-08-solutions.md) until you have attempted each task.

## Goal and evidence

Implement and explain a safe top-*k* pruning decision while keeping Chapter 7's score and eligibility rules fixed. Submit: your hand calculations; one annotated cursor trace; test output; an experiment card with exactness, work and latency; one failure diagnosis; and a short architecture sketch showing index-time bounds and query-time cursors. The [checked-in V2 searcher](../../projects/V2/wand.py) is a reference implementation, not a substitute for the reasoning.

## 1. Hand-work the bytes and the query plan

1. For sorted IDs `[3, 8, 138]`, compute positive gaps and encode them using seven payload bits per byte, with the high bit **1 on the last byte** of each integer. Show the bits or hexadecimal bytes. Decode them again. What changes if the convention instead puts the high bit on continuation bytes?
2. Intersect `A=[1,3,8,11]` and `B=[2,3,9,11]` by moving sorted cursors. Record each comparison and the emitted IDs. Then state what the OR candidate set would be. Explain why replacing Chapter 7's OR posting union with the intersection would change the ranked result set.
3. Sketch a posting for one term with document ID, field count, and positions. Mark which fields a simple BM25 evaluation needs and which a phrase query needs. Name one cost saved and one cost added by compression.

Check the codec without changing the search implementation:

```powershell
python -X utf8 projects/V2/postings_codec.py
python -X utf8 -m unittest discover -s projects/V2 -p 'test_*.py' -v
```

## 2. Trace a safe WAND decision

Open [the fictional corpus](../../projects/V2/toy_pruning_corpus.json). Its P7 record is legal-only; the caller's `support-team` scope is a fixture and must exclude P7 before building scores or bounds. Run:

```powershell
python -X utf8 projects/V2/wand.py --toy-trace
```

For query `rare common`, *k*=1:

1. Record P1's score and the resulting heap threshold `θ`. Record the global bound for `common` and explain why a `common`-only P2 cannot replace P1. Why must the comparison retain equality when the heap is full?
2. Identify the pivot at P6. Trace the `common` cursor's seek from P2 to P6. Count the postings advanced and the documents fully scored by WAND and cached exhaustive execution. Compute P6's two-term score to three decimal places and name the winner.
3. Use the two-document-ID ranges in [Figure 8.01](../../visuals/chapter-08/figure-08-01-cursors-bounds-threshold.svg). Explain why B2 and B3 **could** be skipped by a correct block-bound plan after P1, while the implemented global-bound WAND still scores P6. Explain why B1's summed bound can exceed every actual document score in B1.
4. Write the upper-bound inequality that justifies a skip. State the data and version assumptions hidden inside the phrase “valid bound.”

## 3. Run a controlled comparison

The first two query IDs in the [experiment script](../../projects/V2/experiment_ch08.py) are frozen V0 tasks. Do not tune on them. Run the experiment to a **new file** so the checked-in observation remains available for comparison:

```powershell
python -X utf8 projects/V2/experiment_ch08.py --output projects/V2/chapter-08-experiment-local.json
```

The local JSON is a scratch artifact; it need not be submitted to version control. For `q-contract-change` at *k*=1 and 2, and `q-no-result` at *k*=1, extract exact top-*k* agreement, candidate IDs, fully scored counts, median search-only microseconds, required evidence in selected context, and stub status. Compare the two execution plans **and** the untimed direct BM25 oracle. Write a one-paragraph decision: does this experiment support exactness, less scoring work, lower latency, better evidence selection, or any combination? Name the corpus size, timing sample count and absent judgments.

Use this card:

```text
Question / falsifiable hypothesis:
Baseline / one independent variable / fixed controls:
Source snapshot, query-set version, scorer and execution versions:
Query slices, k, metrics and denominators:
Procedure, seed, samples and timing scope:
Exactness and work results:
Latency and build results:
Candidate → context → answer observations:
Failure example, conclusion and limitations:
```

## 4. Debug a broken optimizer

Without editing the checked-in source, consider a faulty build that records `U_rare=0.20` even though a support-team posting contributes about `1.094`. After P1 has been seen, another cursor may use this false bound. Explain which inequality no longer holds and what kind of missed winner is possible. Then consider a different fault: P7's legal-only posting enters a cache shared with support-team. Explain the eligibility failure even if the returned support-team top-one ID happens to remain P1. Specify a protected regression test for each fault and the trace fields that would locate it. Raw query text and source text do not belong in routine metrics.

## 5. Oral defense and recall

- Defend keeping exhaustive DAAT or TAAT for a 13-segment index despite a WAND reduction in full scores.
- Compare MaxScore, WAND, Block-Max WAND and a fixed posting-budget cutoff by what each knows and what each can guarantee.
- Describe what a segment merge, BM25 parameter change or permission update does to a cached upper bound.
- Draw the V2 path from source snapshot to posting list to eligible candidate to selected context to answer. Mark which Chapter 8 change is at index time and which is at query time.

After completing the lab, revisit the four recall questions after roughly 1, 3, 7 and 21 days. The next chapter adds reviewed relevance labels and ranking metrics; do not use a saved score count as a substitute for those judgments.
