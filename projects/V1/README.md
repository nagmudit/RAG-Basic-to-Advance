# Build Your Own RAG Engine — V1 lexical indexing and ranking

V1 spans Chapters 3–6 in the [project roadmap](../../PROJECT_ROADMAP.md). Chapter 3 measured the V0 full-scan primitive; Chapter 4 isolated prompt behavior; Chapter 5 replaced candidate generation with a positional inverted index while retaining V0's unweighted score. **Chapter 6 completes V1's first weighted lexical comparison** with raw TF-IDF, sublinear TF-IDF and cosine scoring over the same postings. The V0 source and tests remain a frozen baseline. Formal qrels and judged retrieval metrics begin at V2 / Chapter 9.

## Artifacts and boundary

- [Index/search implementation](lexical_index.py): forward segments, analyzed field lengths, title/body positions, term postings, scope membership, Boolean and phrase search, unweighted OR ranking, redacted request trace.
- [Five-record fixture](toy_corpus.json): exact product code, phrase order, accent and legal-only counterexample. It is fictional and separate from V0's ten-document corpus.
- [Behavioral tests](test_lexical_index.py): V0 order/score/answer parity under `v0`, field-local phrases, Boolean operations, Unicode canonical matching, missing amendment and restricted-source exclusion.
- [Experiment program](experiment.py) and [raw record](chapter-05-experiment.json): scan-versus-index comparison with source/code hashes, all raw timing samples, work counts and synthetic copy sizes.
- [TF-IDF scorer](tfidf.py), [four-record ranking fixture](toy_ranking_corpus.json), and [formula tests](test_tfidf.py): scope-local `N`/`df`, declared weight variants, a one-document rank reversal, zero-IDF handling and a small-title-boost edge case.
- [Chapter 6 paired experiment](experiment_ch06.py) and [raw record](chapter-06-experiment.json): overlap versus three weighting rules on the frozen V0 source/questions, top-k 2 and 8, with candidate/context required-span coverage and seven raw search-time samples per case.

V1 builds the index and scope-local ranking statistics before requests. An analyzer choice is an index version; the default `v0` mode makes a clean ranking comparison. `unicode_nfc` deliberately changes matching semantics and is evaluated separately. The `support-team` scope is a **caller-controlled teaching fixture**, not authentication. Indexing the legal-only `D10` internally does not authorize its candidate, prompt or normal trace exposure. Scope membership and statistics are static here; permission updates need live enforcement and invalidation in a real service. No model or general retrieval-quality judge is present yet.

## Run

```powershell
python -X utf8 projects/V1/lexical_index.py
python -X utf8 projects/V1/lexical_index.py --phrase "initial response target"
python -X utf8 projects/V1/experiment.py --output projects/V1/chapter-05-experiment-local.json
python -X utf8 projects/V1/tfidf.py --mode raw --top-k 2
python -X utf8 projects/V1/experiment_ch06.py --output projects/V1/chapter-06-experiment-local.json
python -X utf8 visuals/chapter-06/plot-06-01-sparse-tfidf-matrix.py
python -X utf8 -m unittest discover -s projects/V1 -p 'test_*.py' -v
python -X utf8 -m unittest discover -s projects/V0 -p 'test_*.py' -v
```

Running either experiment without `--output` overwrites its checked-in observation. Local timing may differ. The Python standard library suffices for project code and tests; Figure 6.01 requires matplotlib, and Mermaid CLI renders Chapter 5's diagrams. `--show-prompt` prints fictional source text locally and must not be used as a general telemetry setting.

## What the checked-in experiment establishes

The four query IDs, V0 analyzer, top eight, support scope and synthetic copy counts are fixed. For every recorded size and query, the V0 and indexed top-eight `(segment ID, score)` sequences agree exactly. The original 13-segment index has 119 terms, 222 term–segment pairs and 247 positions. In the checked-in run, a rare numeric query scored one of twelve eligible segments; the common contract question scored all twelve. The 1,300-segment synthetic version showed the same pattern: 100/1,200 versus 1,200/1,200. Build time is reported separately. Nine local timing samples per query/method are too few for reliable production tails; copied documents do not simulate a diverse corpus. There are no qrels or generated answers in this experiment. The V0 deterministic two-task answers are checked independently for regression, not treated as model-quality evidence.

## Chapter 6 ranking result and trace growth

At top two, Chapter 5 overlap places both contract-change clauses in candidates but misses the termination clause. Raw and sublinear TF-IDF retrieve the termination clause but lose the original contract clause; cosine does not repair termination. At top eight, all four rules place the frozen required spans in context, and the unchanged deterministic V0 stub answers both tasks. The Chapter 6 record preserves **both** the gain and the loss, plus source/code hashes, raw timings, build costs and work counts. It does not establish a general quality winner: two fixture evidence sets are not comprehensive qrels, and no LLM output is measured. Chapter 9 will judge retrieval on a broader frozen query set.

The V1 request record adds `index_version`, `analyzer_version`, `scoring_version`, `score_mode`, `eligible_posting_visits`, `scored_segments`, `query_term_count`, zero-score candidate count and stage latency to the existing V0 candidate, context, evidence and status fields. It contains no raw question or source text. Candidate IDs, selected context IDs and supporting evidence IDs remain separate. Chapter 7 uses this measured V1 baseline to examine BM25's saturation and length normalization.
