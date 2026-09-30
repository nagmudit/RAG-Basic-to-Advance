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

## Chapter 6 — verified 2026-09-29

| Source | Used for | Scope and caution |
|---|---|---|
| Manning, Raghavan and Schütze, [Term frequency and weighting](https://nlp.stanford.edu/IR-book/html/htmledition/term-frequency-and-weighting-1.html), [Inverse document frequency](https://nlp.stanford.edu/IR-book/html/htmledition/inverse-document-frequency-1.html), and [Tf-idf weighting](https://nlp.stanford.edu/IR-book/html/htmledition/tf-idf-weighting-1.html), 2008 | TF, DF, IDF and sum of term weights | V1 declares `ln(N/df)` with an eligible-segment corpus; source books and engines may use other conventions and indexing units. |
| Manning, Raghavan and Schütze, [Sublinear tf scaling](https://nlp.stanford.edu/IR-book/html/htmledition/sublinear-tf-scaling-1.html), [Queries as vectors](https://nlp.stanford.edu/IR-book/html/htmledition/queries-as-vectors-1.html), and [Pivoted normalized document length](https://nlp.stanford.edu/IR-book/html/htmledition/pivoted-normalized-document-length-1.html), 2008 | Diminishing repetition weight, cosine query/document scoring and length-normalization limits | The chapter's query/document vector weighting is explicitly specified; cosine is not a relevance probability or a universal length correction. |
| Apache Lucene, [`TFIDFSimilarity` 10.1.0](https://lucene.apache.org/core/10_1_0/core/org/apache/lucene/search/similarities/TFIDFSimilarity.html) API documentation | Concrete production analogue showing configurable/implemented TF, IDF and norms | This version's classic transforms differ from V1's toy formulas; the API is not used in V1 code. |

## Chapter 7 — verified 2026-09-29

| Source | Used for | Scope and caution |
|---|---|---|
| Manning, Raghavan and Schütze, [*Introduction to Information Retrieval*: Okapi BM25](https://nlp.stanford.edu/IR-book/html/htmledition/okapi-bm25-a-non-binary-model-1.html), 2008 | Probabilistic relevance intuition, IDF variants, TF saturation and query term summation | V2 explicitly chooses a nonnegative Lucene-style IDF, segment corpus and binary query-term treatment; it does not implement every textbook form. |
| Robertson and Zaragoza, [*The Probabilistic Relevance Framework: BM25 and Beyond*](https://www.staff.city.ac.uk/~sbrp622/papers/foundations_bm25_review.pdf), 2009 | Framework, assumptions and BM25F context | Author-hosted paper; a BM25 score is an ordering signal, not a calibrated relevance or answer probability. |
| Apache Lucene, [`BM25Similarity` 10.4.0 API](https://lucene.apache.org/core/10_4_0/core/org/apache/lucene/search/similarities/BM25Similarity.html) | Versioned `k1`, `b`, nonnegative IDF and field-length production analogue | V2 uses one combined title/body field and unquantized Python lengths; numerical parity with Lucene is not claimed. |
| Lv and Zhai, [*Lower-Bounding Term Frequency Normalization*](https://timan.cs.illinois.edu/czhai/pub/cikm11-bm25.pdf), CIKM 2011 | Motivation for BM25+ and long-document lower-bound behavior | Author-hosted paper uses a different IDF from V2; the Chapter 7 code does not implement or benchmark it. |
| Manning, Raghavan and Schütze, [*Language Models for Information Retrieval*](https://nlp.stanford.edu/IR-book/pdf/12lmodel.pdf), 2008 | Query-likelihood model and collection smoothing | The comparison is conceptual; V2 only implements posting-union BM25 and does not score absent-term-only candidates under an LM. |

## Chapter 8 — verified 2026-09-29

| Source | Used for | Scope and caution |
|---|---|---|
| Manning, Raghavan and Schütze, [Variable byte codes](https://nlp.stanford.edu/IR-book/html/htmledition/variable-byte-codes-1.html), [Postings compression](https://nlp.stanford.edu/IR-book/html/htmledition/postings-file-compression-1.html), [Skip pointers](https://nlp.stanford.edu/IR-book/html/htmledition/faster-postings-list-intersection-via-skip-pointers-1.html), 2008 | Gap/byte worked example, compressed postings and sorted-cursor jumps | V2's codec uses the final-byte high-bit-1 convention; its WAND path remains RAM based. |
| Manning, Raghavan and Schütze, [Computing vector scores](https://nlp.stanford.edu/IR-book/html/htmledition/computing-vector-scores-1.html), [Impact ordering](https://nlp.stanford.edu/IR-book/html/htmledition/impact-ordering-1.html), [Inexact top-k retrieval](https://nlp.stanford.edu/IR-book/html/htmledition/inexact-top-k-document-retrieval-1.html), 2008 | TAAT/DAAT execution and exact versus budgeted approximate work | Textbook mechanisms are compared; V2 implements only cached exhaustive and one conservative global-bound WAND variant. |
| Broder et al., [*Efficient Query Evaluation Using a Two-Level Retrieval Process*](https://research.ibm.com/publications/efficient-query-evaluation-using-a-two-level-retrieval-process), 2003 | Original WAND pivot and bound idea | The original work discusses time/effectiveness trade-offs; V2's tested setting preserves exact BM25 top-k. |
| Ding and Suel, [*Faster Top-k Document Retrieval Using Block-Max Indexes*](https://research.engineering.nyu.edu/~suel/papers/bmw.pdf), 2011 | Block-local maxima and BMW | Figure 8.01 computes illustrative block bounds; BMW is not executed in V2. |
| Apache Lucene, [index package 10.1.0](https://lucene.apache.org/core/10_1_0/core/org/apache/lucene/index/package-summary.html) and [IndexWriter 10.4.0](https://lucene.apache.org/core/10_4_0/core/org/apache/lucene/index/IndexWriter.html) | Immutable segments, readers, writers and merge behavior | Versioned production analogue; V2 implements no disk segments, live deletes or segment merge. |
| Manning, Raghavan and Schütze, [Dynamic indexing](https://nlp.stanford.edu/IR-book/html/htmledition/dynamic-indexing-1.html), 2008 | Why new segments and merges affect query execution | The static V2 snapshot does not simulate ingestion or updates. |

## Chapter 9 — verified 2026-09-30

| Source | Used for | Scope and caution |
|---|---|---|
| Manning, Raghavan and Schütze, [IR system evaluation](https://nlp.stanford.edu/IR-book/html/htmledition/information-retrieval-system-evaluation-1.html), [unranked measures](https://nlp.stanford.edu/IR-book/html/htmledition/evaluation-of-unranked-retrieval-sets-1.html) and [ranked measures](https://nlp.stanford.edu/IR-book/html/htmledition/evaluation-of-ranked-retrieval-results-1.html), 2008 | Test-collection components and precision, recall, F, AP/MAP, DCG/NDCG intuition | V2 states its own grade, cutoff, zero-positive and missing-slot conventions; its miniature qrels are not a standard benchmark. |
| Manning, Raghavan and Schütze, [Assessing relevance](https://nlp.stanford.edu/IR-book/html/htmledition/assessing-relevance-1.html), 2008 | Pooling, assessor disagreement and Cohen's kappa example | Chapter 9's qrels have one author; no measured inter-assessor agreement is claimed. |
| NIST TREC, [TREC 2024 overview](https://trec.nist.gov/pubs/trec33/papers/overview_33.pdf) | Primary account of pooling assumptions, unjudged items and graded judgments in a modern TREC setting | Pooling can miss relevant items and bias novel systems; V2 instead reviews all twelve eligible items per question. |
| NIST TREC, [English relevance judgments](https://trec.nist.gov/data/reljudge_eng.html) | Official qrel/collection matching guidance | TREC's task-specific label definitions and collection permissions do not transfer automatically to the fictional Helios set. |
| NIST, [`trec_eval` README](https://github.com/usnistgov/trec_eval/blob/main/README) | Official evaluation-tool context and measure-name comparison | V2 implements declared educational metric conventions independently; numeric parity with every `trec_eval` option is not claimed. |

## Chapter 10 — verified 2026-09-30

| Source | Used for | Scope and caution |
|---|---|---|
| Manning, Raghavan and Schütze, [Dot products and cosine](https://nlp.stanford.edu/IR-book/html/htmledition/dot-products-1.html), [queries as vectors](https://nlp.stanford.edu/IR-book/html/htmledition/queries-as-vectors-1.html), [computing vector scores](https://nlp.stanford.edu/IR-book/html/htmledition/computing-vector-scores-1.html), 2008 | Vector-space representation, length normalization and the cost of scoring document vectors | Their sparse term-vector mechanics motivate Chapter 10's lexical comparison; no learned semantic meaning is inferred. |
| scikit-learn, [Nearest Neighbor Algorithms](https://scikit-learn.org/stable/modules/neighbors.html), accessed 2026-09-30 | Brute-force query work and the contrast with tree-based methods | Library implementation choices change by version and data; V3 uses a standard-library full scan, not scikit-learn or ANN. |
| NumPy, [`matmul`](https://numpy.org/doc/stable/reference/generated/numpy.matmul.html) and [`linalg.norm`](https://numpy.org/doc/stable/reference/generated/numpy.linalg.norm.html), accessed 2026-09-30 | Matrix multiplication and vector-norm production analogues | V3 does not depend on NumPy; packed matrices, kernel speed and floating-point parity were not benchmarked. |
