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

## Chapter 11 — verified 2026-09-30

| Source | Used for | Scope and caution |
|---|---|---|
| Devlin et al., [BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding](https://arxiv.org/abs/1810.04805), 2018 | Contextual token representations in an encoder | BERT itself is not automatically a calibrated passage retriever; pooling and retrieval training matter. |
| Reimers and Gurevych, [Sentence-BERT](https://arxiv.org/abs/1908.10084), 2019 | Independent sentence encoding versus pairwise cross-encoding | Chapter 11 uses one later frozen sentence model, not the paper's benchmark conditions. |
| Karpukhin et al., [Dense Passage Retrieval](https://arxiv.org/abs/2004.04906), 2020 | Query/passage dual encoders and positive/negative passage training | Reported open-domain QA gains do not transfer automatically to the tiny fictional Helios corpus. |
| Sentence Transformers, [all-MiniLM-L6-v2 model card](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2/blob/8b3219a92973c328a8e22fadcfa821b5dc75636a/README.md), accessed 2026-09-30 | Public Apache-2.0 model, 384 dimensions, mean pooling, 256-word-piece default truncation, contrastive training description | Experiment pins revision `8b3219a92973c328a8e22fadcfa821b5dc75636a`; weights are external, frozen and not committed. Model-card intended use does not certify a domain retrieval gain. |
| Sentence Transformers, [query/document encoding usage](https://www.sbert.net/docs/sentence_transformer/usage/usage.html), accessed 2026-09-30 | Current API distinction for models with separate prompts/routes | The pinned symmetric model's experiment uses one shared `encode` path without prefixes; changing input format requires new index/version and measurement. |
| Kusupati et al., [Matryoshka Representation Learning](https://arxiv.org/abs/2205.13147), 2022 | Training nested useful vector prefixes | The Chapter 11 checkpoint is not asserted to support arbitrary prefix truncation; each prefix needs its own held-out retrieval test. |

## Chapter 12 — verified 2026-09-30

| Source | Used for | Scope and caution |
|---|---|---|
| Karpukhin et al., [Dense Passage Retrieval](https://arxiv.org/abs/2004.04906), 2020 | Dual-encoder question/passage training with negatives | Its open-domain QA results are not a claim for the fictional support corpus or this query-only adapter. |
| Xiong et al., [ANCE](https://arxiv.org/abs/2007.00808), 2020 | Iterative ANN-based negative mining | Chapter 12 explains its mining mechanism; the local runner does not build an ANN index. |
| Wang et al., [GPL](https://arxiv.org/abs/2112.07577), 2021 | Synthetic questions and cross-encoder pseudo-labels for unsupervised domain adaptation | The V3 training questions are human-authored; no GPL teacher or reported gain is reproduced. |
| Microsoft, [MS MARCO ranking datasets](https://github.com/microsoft/msmarco/blob/master/Datasets.md), accessed 2026-09-30 | Passage ranking, sparse labels, query/passage data and task boundaries | A leaderboard rank does not guarantee complete evidence or corpus transfer. |
| Thakur et al., [BEIR](https://arxiv.org/abs/2104.08663), 2021 | Heterogeneous zero-shot retrieval and BM25 comparator | Heterogeneous average can hide a support-domain failure; V3 does not run BEIR. |
| Muennighoff et al., [MTEB](https://arxiv.org/abs/2210.07316), 2022 | Embedding evaluation across tasks and languages | Overall embedding ranking is not a domain-specific retrieval test. |
| Zhang et al., [MIRACL](https://arxiv.org/abs/2210.09984), 2022 | Monolingual ad hoc retrieval across 18 languages | Does not by itself measure cross-lingual query-to-document search; V3 English-only results imply no multilingual gain. |
| Sentence Transformers, [all-MiniLM-L6-v2 pinned model card](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2/blob/8b3219a92973c328a8e22fadcfa821b5dc75636a/README.md), accessed 2026-09-30 | License and base model configuration reused from Chapter 11 | The Chapter 12 adapter is trained locally; base weights remain external and frozen. |

## Chapter 13 — verified 2026-09-30

| Source | Used for | Scope and caution |
|---|---|---|
| Sentence Transformers, [query/document encoding usage](https://www.sbert.net/docs/sentence_transformer/usage/usage.html), accessed 2026-09-30 | Query/document prompt and task routes, batch encoding interface | The pinned Chapter 11 model has no specialized prompt; V3 retains one shared `encode()` path. A different model needs a new checked contract. |
| Sentence Transformers, [semantic-search guide](https://www.sbert.net/examples/sentence_transformer/applications/semantic-search/README.html), accessed 2026-09-30 | Independent corpus/query embedding and exact scoring for smaller corpora | The guide's scale advice is not a benchmark of V3's Python CPU implementation. |
| Faiss maintainers, [MetricType and distances](https://github.com/facebookresearch/faiss/wiki/MetricType-and-distances), accessed 2026-09-30 | Cosine versus inner product and the normalization requirement | Chapter 13 implements its own exact scorer, not Faiss; actual service performance is not inferred. |
| Faiss maintainers, [Faiss indexes](https://github.com/facebookresearch/faiss/wiki/Faiss-indexes), accessed 2026-09-30 | Flat exact index representation and raw vector storage analogue | V3's manifest/ID map and scope gate are explicit teaching code, not a Faiss feature test. |
| Sentence Transformers, [all-MiniLM-L6-v2 pinned model card](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2/blob/8b3219a92973c328a8e22fadcfa821b5dc75636a/README.md), accessed 2026-09-30 | Model revision, short-text input limit, 384 dimensions and Apache-2.0 license | The 14-query diagnostic probe is fictional and gives no broader model-selection or multilingual claim. |

## Chapter 14 — verified 2026-10-01

| Source | Used for | Scope and caution |
|---|---|---|
| Formal, Piwowarski & Clinchant, [SPLADE](https://arxiv.org/abs/2107.05720), 2021 | Learned sparse first-stage retrieval, expansion, log saturation and regularization | The original formulation uses sum pooling; V3's hand-authored logits do not reproduce its trained model or benchmark results. |
| Formal et al., [SPLADE v2](https://arxiv.org/html/2109.10086v1), 2021 | Max-pooling equation, separate query/document sparsity penalties, FLOPS surrogate and document-only variant | The V3 code implements only the fixed-logit max pool and exact posting accumulation, without training or latency claims for a neural encoder. |
| Khattab & Zaharia, [ColBERT](https://arxiv.org/html/2004.12832v2), 2020 | Independent contextual query/document token encoders, MaxSim, reranking and end-to-end token-index search | V3 computes MaxSim on hand-authored unit vectors; no ColBERT checkpoint, token ANN or paper-reported speedup is reproduced. |
| Santhanam et al., [ColBERTv2](https://arxiv.org/abs/2112.01488), 2021 | Residual compression and denoised supervision as a storage/quality research direction | Its reported compression or benchmark quality does not transfer to the uncompressed V3 toy. |

## Chapter 15 — verified 2026-10-01

| Source | Used for | Scope and caution |
|---|---|---|
| Bentley, [Multidimensional Binary Search Trees Used for Associative Searching](https://cs.wmich.edu/gupta/teaching/cs6310/lectureNotes_cs6310/kdtree-bentley.pdf), 1975 | Original axis-partitioned KD-tree construction and nearest-neighbor context | The paper's efficiency discussion is tied to its analysis/empirical setting; V4 proves exactness by its own box bound and tests, and does not claim universal logarithmic query time. |
| Omohundro, [Five Balltree Construction Algorithms](https://steveomohundro.com/wp-content/uploads/2009/03/omohundro89_five_balltree_construction_algorithms.pdf), 1989 | Ball-tree center/radius construction, overlap and metric-bound comparison | V4 derives the ball lower bound but implements only KD; no ball-tree timing result is claimed. |
| Charikar, [Similarity Estimation Techniques from Rounding Algorithms](https://www.cs.princeton.edu/courses/archive/spr04/cos598B/bib/CharikarEstim.pdf), 2002 | Random Gaussian hyperplane sign hash and `1−θ/π` pairwise collision probability | Independence-based table/bit formulas do not predict full-corpus top-K or qrel recall; V4 measures those separately. |
| Beyer et al., [When Is “Nearest Neighbor” Meaningful?](https://research.cs.wisc.edu/techreports/1998/TR1377.pdf), 1999 | Conditional high-dimensional distance-concentration warning | Synthetic Gaussian behavior does not imply all trained embeddings or intrinsic structures have the same difficulty. |
| scikit-learn maintainers, [Nearest Neighbors guide](https://scikit-learn.org/stable/modules/neighbors.html), accessed 2026-10-01 | Current maintained comparison of brute force, KD and ball-tree strategies and dimension/leaf-size caveats | V4 uses independent standard-library teaching code; no library performance numbers are copied into its results. |

## Chapter 16 — verified 2026-10-01

| Source | Used for | Scope and caution |
|---|---|---|
| Jégou, Douze & Schmid, [Product Quantization for Nearest Neighbor Search](https://doi.org/10.1109/TPAMI.2010.57), 2011 | Subvector codebooks, compact indices, approximate distance computation and IVF/PQ lineage | V4 uses tiny two-bit residual codebooks and no optimized kernels; paper benchmark performance does not transfer. |
| Faiss maintainers, [Faiss indexes](https://github.com/facebookresearch/faiss/wiki/Faiss-indexes), accessed 2026-10-01 | Maintained IVF-Flat and IVF-PQ definitions, `nlist/nprobe`, residual codes and code/ID byte formulas | V4 implements its own pure-Python version; Faiss byte formulas are payload intuition, not measured Python RSS or V4 speed. |
| Faiss maintainers, [FAQ](https://github.com/facebookresearch/faiss/wiki/FAQ), accessed 2026-10-01 | All-list probe as a coarse-error diagnostic, training-sample cautions and underfilled-result behavior | All-list exactness applies to IVF-Flat with original vectors and compatible filtering/metric, not to PQ ADC. |
| Johnson, Douze & Jégou, [Billion-scale similarity search with GPUs](https://arxiv.org/abs/1702.08734), 2017 | Hardware-aware compressed-domain search and top-k selection context | GPU results and scale are not extrapolated from the V4 local CPU/Python fixture. |
