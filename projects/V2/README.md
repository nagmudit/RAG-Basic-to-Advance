# Build Your Own RAG Engine — V2, Chapters 7–8 lexical stages

V2 spans Chapters 7–9 in the [project roadmap](../../PROJECT_ROADMAP.md). **This snapshot implements Chapters 7 and 8.** It reuses V1's source snapshot, analyzer, positional postings, source records, context construction and deterministic V0 answer stub. [BM25](bm25.py) adds scope-local segment lengths, average length, document frequencies, nonnegative IDF and saturating term scores. Chapter 7 exhaustively scores every eligible posting match. Chapter 8 adds [global-bound WAND](wand.py): cached per-term impacts and bounds for the same scoring version, document-at-a-time cursors, a size-*k* heap and exact tie handling. Chapter 9 will add reviewed qrels, ranking metrics and p50/p95 reporting on a larger frozen query set; it is not implemented here.

## Artifacts and policy

- [BM25 implementation](bm25.py) with `k1=1.2`, `b=.75` defaults and a local per-term explainer; [behavioral tests](test_bm25.py).
- [Short/long fixture](toy_length_corpus.json) with one legal-only record. It isolates the length parameter without using private data.
- [Paired V0 comparison](experiment_ch07.py) and [checked-in raw result](chapter-07-experiment.json). The record retains line-ending-normalized source/index/ranker/experiment SHA256 hashes, query and scorer versions, build costs, seven search-only raw samples per method/case, candidate scores, selected-context IDs, required-evidence coverage, work counts and deterministic stub status.
- [Chapter 7 plot source](../../visuals/chapter-07/plot-07-01-bm25-controls.py) and [rendered SVG](../../visuals/chapter-07/figure-07-01-bm25-controls.svg).
- [Chapter 8 exact-pruning implementation](wand.py), [behavioral tests](test_wand.py) and [fictional pruning fixture](toy_pruning_corpus.json). `--toy-trace` exposes fictional cursor details only.
- [Variable-byte gap codec](postings_codec.py): a separate byte-level teaching exercise. The WAND searcher uses RAM postings and does not run on compressed disk data.
- [Chapter 8 paired experiment](experiment_ch08.py) and [checked-in raw result](chapter-08-experiment.json): cached exhaustive versus WAND, with direct BM25 as an untimed oracle; five fixed queries at *k*=1/2/8, eleven randomized-order search-only samples per method/case, exact IDs and raw scores, work, context, stub status, hashes and limitations.
- [Figure 8.01 plot source](../../visuals/chapter-08/plot-08-01-cursors-bounds-threshold.py), [SVG](../../visuals/chapter-08/figure-08-01-cursors-bounds-threshold.svg) and [PNG](../../visuals/chapter-08/figure-08-01-cursors-bounds-threshold.png). Its block maxima explain Block-Max WAND conceptually; they are not used by the implemented global WAND.

The default corpus unit is an **eligible indexed segment**. `L_d` is the analyzed title-plus-body term count and `avgdl` includes all eligible segments in that scope, even those without the query term. `df` is counted once per eligible segment. Title boost applies to term count, not length; this is a simple combined-field choice, not BM25F. The caller-controlled `support-team` fixture is not authentication. Real permission changes need live enforcement plus statistics/cache invalidation. The normal trace records IDs, scores, versions, work and timings without query/source text; the local explainer may reveal terms and is suitable only for fictional or properly protected data.

The WAND build caches impacts per scope/posting, so scorer parameters, source/analyzer snapshot and eligibility must match the bound version. A real live permission system must enforce eligibility independently and handle updates; the static fixture is only a controlled experiment. The Python implementation rounds bounds outward and retains equal-threshold candidates for tie correctness. Its exactness argument requires valid bounds and nonnegative contributions; arbitrary floating-point programs still require numerical validation. Never use the fictional `--toy-trace` mode as routine telemetry on private content.

## Run

```powershell
python -X utf8 projects/V2/bm25.py --query-id q-contract-change --top-k 2
python -X utf8 projects/V2/bm25.py --query-id q-termination --top-k 2 --b 0
python -X utf8 projects/V2/postings_codec.py
python -X utf8 projects/V2/wand.py --toy-trace
python -X utf8 projects/V2/wand.py --question '12000 credits' --top-k 2
python -X utf8 projects/V2/experiment_ch07.py --output projects/V2/chapter-07-experiment-local.json
python -X utf8 projects/V2/experiment_ch08.py --output projects/V2/chapter-08-experiment-local.json
python -X utf8 visuals/chapter-07/plot-07-01-bm25-controls.py
python -X utf8 visuals/chapter-08/plot-08-01-cursors-bounds-threshold.py
python -X utf8 -m unittest discover -s projects/V2 -p 'test_*.py' -v
python -X utf8 -m unittest discover -s projects/V1 -p 'test_*.py' -v
python -X utf8 -m unittest discover -s projects/V0 -p 'test_*.py' -v
```

Running an experiment **without** `--output` overwrites its checked-in observation. Project code and tests use the Python standard library; figures require matplotlib. Timing varies by machine and run. `--show-prompt` prints fictional source text for local inspection and is not a telemetry option for real content.

## Current findings and next gate

At top two, BM25 with either tested `b` retrieves the termination evidence `D1 §8`, while overlap misses it. Neither BM25 setting retains both governing contract-change clauses in the top-two context: `D1 §3` sits below the cutoff, and the stub abstains. At top eight all compared methods include the fixture-required evidence and the stub answers both tasks. This is a **small required-span check**, not judged retrieval quality or answer correctness. V2 preserves the negative contract case for Chapter 9's qrels rather than tuning on the two V0 questions.

Chapter 8's toy WAND plan scores 2 of 6 eligible matches and advances over four postings; the top-one candidate equals exhaustive BM25. On the V0 contract task at *k*=1, cached exhaustive scores 12 segments and WAND scores 2; the checked-in median search-only times are **16.3 versus 39.0 µs**. At *k*=2, it scores 12 versus 9 and takes **14.6 versus 98.9 µs**. The reduced work and slower query time coexist because cursor/bound/heap overhead dominates this small Python corpus. All 15 frozen query/depth comparisons preserve direct BM25's ordered IDs and raw scores as well as context and stub behavior between execution plans. The eleven local samples per case are not production tail-latency evidence; build costs and raw samples are in the record. Chapter 9 must add reviewed relevance judgments and a larger metric baseline before any ranking or release claim.
