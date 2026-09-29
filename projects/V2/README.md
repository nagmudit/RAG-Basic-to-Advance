# Build Your Own RAG Engine — V2, Chapter 7 BM25 stage

V2 spans Chapters 7–9 in the [project roadmap](../../PROJECT_ROADMAP.md). **This snapshot implements Chapter 7 only.** It reuses V1's source snapshot, analyzer, positional postings, source records, context construction and deterministic V0 answer stub. [BM25](bm25.py) adds scope-local segment lengths, average length, document frequencies, nonnegative IDF and saturating term scores. It exhaustively scores every eligible posting match. Chapter 8 adds a safe exact top-*k* execution strategy; Chapter 9 adds reviewed qrels, ranking metrics and p50/p95 reporting on a larger frozen query set. Those later components have not been implemented here.

## Artifacts and policy

- [BM25 implementation](bm25.py) with `k1=1.2`, `b=.75` defaults and a local per-term explainer; [behavioral tests](test_bm25.py).
- [Short/long fixture](toy_length_corpus.json) with one legal-only record. It isolates the length parameter without using private data.
- [Paired V0 comparison](experiment_ch07.py) and [checked-in raw result](chapter-07-experiment.json). The record retains line-ending-normalized source/index/ranker/experiment SHA256 hashes, query and scorer versions, build costs, seven search-only raw samples per method/case, candidate scores, selected-context IDs, required-evidence coverage, work counts and deterministic stub status.
- [Chapter 7 plot source](../../visuals/chapter-07/plot-07-01-bm25-controls.py) and [rendered SVG](../../visuals/chapter-07/figure-07-01-bm25-controls.svg).

The default corpus unit is an **eligible indexed segment**. `L_d` is the analyzed title-plus-body term count and `avgdl` includes all eligible segments in that scope, even those without the query term. `df` is counted once per eligible segment. Title boost applies to term count, not length; this is a simple combined-field choice, not BM25F. The caller-controlled `support-team` fixture is not authentication. Real permission changes need live enforcement plus statistics/cache invalidation. The normal trace records IDs, scores, versions, work and timings without query/source text; the local explainer may reveal terms and is suitable only for fictional or properly protected data.

## Run

```powershell
python -X utf8 projects/V2/bm25.py --query-id q-contract-change --top-k 2
python -X utf8 projects/V2/bm25.py --query-id q-termination --top-k 2 --b 0
python -X utf8 projects/V2/experiment_ch07.py --output projects/V2/chapter-07-experiment-local.json
python -X utf8 visuals/chapter-07/plot-07-01-bm25-controls.py
python -X utf8 -m unittest discover -s projects/V2 -p 'test_*.py' -v
python -X utf8 -m unittest discover -s projects/V1 -p 'test_*.py' -v
python -X utf8 -m unittest discover -s projects/V0 -p 'test_*.py' -v
```

Running the experiment **without** `--output` overwrites its checked-in observation. Project code and tests use the Python standard library; the figure requires matplotlib. Timing varies by machine and run. `--show-prompt` prints fictional source text for local inspection and is not a telemetry option for real content.

## Current finding and next gate

At top two, BM25 with either tested `b` retrieves the termination evidence `D1 §8`, while overlap misses it. Neither BM25 setting retains both governing contract-change clauses in the top-two context: `D1 §3` sits below the cutoff, and the stub abstains. At top eight all compared methods include the fixture-required evidence and the stub answers both tasks. This is a **small required-span check**, not judged retrieval quality or answer correctness. V2 should preserve the negative contract case for Chapter 9's qrels and not tune parameters on these two tests alone. Search-only timings and build costs live in the raw record; the seven local samples cannot establish production tail latency. Chapter 8 must preserve exact exhaustive BM25 ordering while reducing scored-document work.
