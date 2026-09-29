# Source register

This register records primary sources used in written chapters. Concept explanations are original textbook prose; fictional examples are identified in their chapters. A source's existence does not make a chapter's claims automatically correct. Authors verify the relevant passage when writing and review time-sensitive claims again when revising.

## Chapter 1 — verified 2026-09-29

| Source | Used for | Scope and caution |
|---|---|---|
| Manning, Raghavan and Schütze, [*Introduction to Information Retrieval*: An Example Information Retrieval Problem](https://nlp.stanford.edu/IR-book/html/htmledition/an-example-information-retrieval-problem-1.html) and [Information Retrieval System Evaluation](https://nlp.stanford.edu/IR-book/html/htmledition/information-retrieval-system-evaluation-1.html), 2008 | Query versus information need; relevance relative to that need | A foundational IR account, not a model of every modern RAG workload. |
| Lewis et al., [*Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks*](https://arxiv.org/abs/2005.11401), 2020 | Historical parametric/non-parametric framing and the paper's specific RAG architecture | The chapter uses RAG more broadly for application retrieval; Chapter 55 teaches the trained architectures. |
| NIST TREC, [English relevance judgments](https://trec.nist.gov/data/reljudge_eng.html) | Example of tying questions, documents and judgments to a specific collection | Full evaluation and qrels are taught in Chapter 9; do not infer complete judgments for an arbitrary corpus. |

## Chapter 2 — verified 2026-09-29

| Source | Used for | Scope and caution |
|---|---|---|
| Manning, Raghavan and Schütze, [*Introduction to Information Retrieval*: An Example Information Retrieval Problem](https://nlp.stanford.edu/IR-book/html/htmledition/an-example-information-retrieval-problem-1.html) and [A First Take at Building an Inverted Index](https://nlp.stanford.edu/IR-book/html/htmledition/a-first-take-at-building-an-inverted-index-1.html), 2008 | Linear scan as an instructive baseline; index motivation | V0 deliberately stops before implementing an inverted index, which begins in Chapter 5. |
| Python Software Foundation, [regular-expression operations](https://docs.python.org/3/library/re.html) | V0's small lexical tokenizer uses `re.compile(...).findall(...)` | The expression chosen by the book is ASCII-oriented and not a general analyzer. |
| Python Software Foundation, [`time.perf_counter()`](https://docs.python.org/3/library/time.html#time.perf_counter) | Measuring elapsed stage and request durations by differences between calls | One tiny-corpus timing sample does not establish a latency distribution or benchmark result. |
