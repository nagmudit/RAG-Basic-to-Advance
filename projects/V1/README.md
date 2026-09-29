# Build Your Own RAG Engine — V1, Chapter 5 index preview

V1 spans Chapters 3–6 in the [project roadmap](../../PROJECT_ROADMAP.md). Chapter 3 measured the V0 full-scan primitive; Chapter 4 isolated prompt behavior; **Chapter 5 now replaces candidate generation with a positional inverted index** while retaining V0's analyzer, unweighted overlap score, context packing and two-task answer stub by default. Chapter 6 will add TF-IDF and complete V1's weighted ranking comparison. The V0 source and tests remain a frozen baseline.

## Artifacts and boundary

- [Index/search implementation](lexical_index.py): forward segments, analyzed field lengths, title/body positions, term postings, scope membership, Boolean and phrase search, unweighted OR ranking, redacted request trace.
- [Five-record fixture](toy_corpus.json): exact product code, phrase order, accent and legal-only counterexample. It is fictional and separate from V0's ten-document corpus.
- [Behavioral tests](test_lexical_index.py): V0 order/score/answer parity under `v0`, field-local phrases, Boolean operations, Unicode canonical matching, missing amendment and restricted-source exclusion.
- [Experiment program](experiment.py) and [raw record](chapter-05-experiment.json): scan-versus-index comparison with source/code hashes, all raw timing samples, work counts and synthetic copy sizes.

V1 builds the index before requests. An analyzer choice is an index version; the default `v0` mode makes a clean algorithm comparison. `unicode_nfc` deliberately changes matching semantics and is evaluated separately. The `support-team` scope is a **caller-controlled teaching fixture**, not authentication. Indexing the legal-only `D10` internally does not authorize its candidate, prompt or normal trace exposure. Scope membership is static here; permission updates need live enforcement and invalidation in a real service. No model or retrieval-quality judge is present yet.

## Run

```powershell
python -X utf8 projects/V1/lexical_index.py
python -X utf8 projects/V1/lexical_index.py --phrase "initial response target"
python -X utf8 projects/V1/experiment.py --output projects/V1/chapter-05-experiment-local.json
python -X utf8 -m unittest discover -s projects/V1 -p 'test_*.py' -v
python -X utf8 -m unittest discover -s projects/V0 -p 'test_*.py' -v
```

Running `experiment.py` without `--output` overwrites the checked-in observation. Local timing may differ. The Python standard library suffices for code and tests; Mermaid CLI renders the chapter's visual sources. `--show-prompt` prints fictional source text locally and must not be used as a general telemetry setting.

## What the checked-in experiment establishes

The four query IDs, V0 analyzer, top eight, support scope and synthetic copy counts are fixed. For every recorded size and query, the V0 and indexed top-eight `(segment ID, score)` sequences agree exactly. The original 13-segment index has 119 terms, 222 term–segment pairs and 247 positions. In the checked-in run, a rare numeric query scored one of twelve eligible segments; the common contract question scored all twelve. The 1,300-segment synthetic version showed the same pattern: 100/1,200 versus 1,200/1,200. Build time is reported separately. Nine local timing samples per query/method are too few for reliable production tails; copied documents do not simulate a diverse corpus. There are no qrels or generated answers in this experiment. The V0 deterministic two-task answers are checked independently for regression, not treated as model-quality evidence.

## Trace growth and next step

The V1 request record adds `index_version`, `analyzer_version`, `eligible_posting_visits`, `scored_segments`, and `query_term_count` to the existing V0 candidate, context, evidence, status and latency fields. It contains no raw question or source text. Candidate IDs, selected context IDs and supporting evidence IDs remain separate. Chapter 6 will preserve this indexed baseline while adding term weights and measured ranking comparisons; formal relevance labels begin in Chapter 9.
