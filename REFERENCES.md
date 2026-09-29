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

## Chapter 3 — verified 2026-09-29

| Source | Used for | Scope and caution |
|---|---|---|
| Python Software Foundation, [Time Complexity](https://wiki.python.org/moin/TimeComplexity) | CPython list, set and dict average/worst-case operation bounds | Implementation and workload assumptions are stated; bounds are not measured latency or universal across runtimes. |
| Python Software Foundation, [`time.perf_counter_ns()`](https://docs.python.org/3/library/time.html#time.perf_counter_ns) and [`timeit`](https://docs.python.org/3/library/timeit.html) | Elapsed timing, repetition, and interpretation of raw trial variation | The chapter's own sidecar is a local workload study, not a production latency benchmark. |
| Python Software Foundation, [Unicode HOWTO](https://docs.python.org/3/howto/unicode.html) | Code points versus UTF-8 bytes | A visible glyph, regex term and model token remain separate units. |
| Python Software Foundation, [`sys.getsizeof`](https://docs.python.org/3/library/sys.html#sys.getsizeof) | Shallow Python object size | It excludes the objects a container refers to; JSON bytes are another representation. |

## Chapter 4 — verified 2026-09-29

| Source | Used for | Scope and caution |
|---|---|---|
| Vaswani et al., [*Attention Is All You Need*](https://arxiv.org/abs/1706.03762), 2017 | Scaled dot-product attention, masking and the original Transformer | The original model is encoder–decoder; the chapter's autoregressive decoder sketch is a general teaching abstraction, not a claim that all LLMs share one architecture. |
| Brown et al., [*Language Models are Few-Shot Learners*](https://arxiv.org/abs/2005.14165), 2020 | Autoregressive generation and in-context examples in one large decoder-only family | Its results do not guarantee that examples supply current private facts or that every model responds alike. |
| Ouyang et al., [*Training language models to follow instructions with human feedback*](https://arxiv.org/abs/2203.02155), 2022 | Instruction-following model adaptation | Following instructions does not make a retrieved source true or enforce authorization. |
| Liu et al., [*Lost in the Middle: How Language Models Use Long Contexts*](https://aclanthology.org/2024.tacl-1.9/), 2024 | Empirical motivation for controlled evidence-position tests | Position effects are model/task/workload dependent; V0 has no measured LLM outputs. |
| Greshake et al., [*Not what you've signed up for*](https://arxiv.org/abs/2302.12173), 2023 | Indirect prompt injection through retrieved data | A lab-only fictional probe illustrates the mechanism; no defense guarantee is inferred from prompt wording. |
| Lewis et al., [*Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks*](https://arxiv.org/abs/2005.11401), 2020 | Distinction between learned retrieval–generation architectures and application engineering RAG | Detailed model-architecture history is reserved for Chapter 55. |

## Chapter 5 — verified 2026-09-29

| Source | Used for | Scope and caution |
|---|---|---|
| Manning, Raghavan and Schütze, [*Introduction to Information Retrieval*: The term vocabulary and postings lists](https://nlp.stanford.edu/IR-book/html/htmledition/the-term-vocabulary-and-postings-lists-1.html), [Tokenization](https://nlp.stanford.edu/IR-book/html/htmledition/tokenization-1.html), and [Processing Boolean queries](https://nlp.stanford.edu/IR-book/html/htmledition/processing-boolean-queries-1.html), 2008 | Analyzer symmetry, posting lists, AND/OR execution and sorted intersection | V1 uses Python sets for clarity and preserves V0's overlap scoring; compressed execution and weighted ranking are later chapters. |
| Manning, Raghavan and Schütze, [Positional indexes](https://nlp.stanford.edu/IR-book/html/htmledition/positional-indexes-1.html), 2008 | Same-field ordered positions for phrase matching | V1 stores term positions, not original character or byte offsets. |
| Unicode Consortium, [Unicode Standard Annex #15: Unicode Normalization Forms](https://www.unicode.org/reports/tr15/), revision current on 2026-09-29 | NFC versus compatibility normalization and the need to preserve meaningful distinctions | The lab's `unicode_nfc` analyzer is a limited Python teaching implementation, not a universal multilingual analyzer. |
| Python Software Foundation, [`str.casefold()`](https://docs.python.org/3/library/stdtypes.html#str.casefold), [`unicodedata.normalize()`](https://docs.python.org/3/library/unicodedata.html#unicodedata.normalize), and [regular expressions](https://docs.python.org/3/library/re.html) | Exact operations used in V1's optional analyzer | Python/Unicode versions can change details; pin and retest analyzer/index versions on production corpora. |
| Apache Lucene, [`TokenStream` 10.3.1](https://lucene.apache.org/core/10_3_1/core/org/apache/lucene/analysis/TokenStream.html), [`PostingsEnum` 10.4.0](https://lucene.apache.org/core/10_4_0/core/org/apache/lucene/index/PostingsEnum.html), and [`TextField` 10.3.1](https://lucene.apache.org/core/10_3_1/core/org/apache/lucene/document/TextField.html) API documentation | Production analogue for analysis streams, posting iteration and indexed-versus-stored fields | Versioned API examples only; V1 does not implement Lucene disk segments or claim Lucene supplies application authorization. |
