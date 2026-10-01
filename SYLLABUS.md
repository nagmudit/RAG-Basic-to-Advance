# Detailed syllabus

**Architecture:** 12 parts → 28 modules → 57 chapters. Chapters are numbered globally so every prerequisite and case study can cite an unambiguous target. Each chapter has an objective, prerequisites, a lab, a planned visual, a trade-off, a misconception, and the capability it unlocks. The nested `Section → Topic → micro-concepts` lines define minimum teaching depth; chapter writing may add sections but cannot quietly replace mechanisms with labels.

The core question evolves throughout: **Which evidence enters the LLM's context, through what algorithm and authorization path, and with what measured risk of omission or error?** Every part ends with a cumulative quiz, an architecture sketch from memory, and a comparison against the prior engine version. Depth labels follow [TEACHING_PHILOSOPHY.md](TEACHING_PHILOSOPHY.md). The first judged retriever appears in Chapter 09; Core RAG Evaluation is taught in Chapters 30–33 before specialized and adaptive architectures. Every written chapter follows the [completion checklist](CHAPTER_COMPLETION_CHECKLIST.md), [visual system](visuals/VISUAL_ASSET_CONTRACT.md), [evaluation/experiment contract](evaluation/EVALUATION_EXPERIMENT_CONTRACT.md) and evolving [observability contract](observability/OBSERVABILITY_CONTRACT.md).

## Part I — Orientation and prerequisites [FOUNDATIONAL]

### Module 01 — Why external knowledge?

#### Chapter 01 — A question, a model, and missing evidence

- **Authored materials:** [Chapter](chapters/chapter-01-a-question-a-model-and-missing-evidence.md) · [Lab](labs/chapter-01/LAB.md) · [Solutions](solutions/chapter-01-solutions.md) · [V0 brief](projects/V0/README.md).
- **Objective:** Decide whether a task needs retrieval and trace the simplest evidence path.
- **Prerequisites:** None.
- **Section 1 — Knowledge boundaries.** Topic: model knowledge; micro-concepts: training cutoffs, weights as parametric memory, private facts, stale facts, hallucination, context windows, source provenance. Topic: alternatives; micro-concepts: direct answering, prompt-only context, fine-tuning, tool calls, search without generation.
- **Section 2 — The RAG contract.** Topic: grounding; micro-concepts: question, corpus, candidate, evidence, answer, citation, abstention. Topic: suitability; micro-concepts: stable vs changing facts, exact lookup vs synthesis, when retrieval costs more than it helps.
- **Lab:** Sort 15 realistic requests by knowledge source and justify RAG or an alternative.
- **Visual:** One question through model-only and evidence-backed paths.
- **Trade-off / misconception:** Retrieval improves access to evidence but adds latency and cannot guarantee truth; RAG is not synonymous with vector search.
- **Unlocks:** The hand-built pipeline in Chapter 02.

#### Chapter 02 — Build the first RAG loop without a framework

- **Authored materials:** [Chapter](chapters/chapter-02-build-the-first-rag-loop.md) · [Lab](labs/chapter-02/LAB.md) · [Solutions](solutions/chapter-02-solutions.md) · [V0 implementation and results](projects/V0/README.md).
- **Objective:** Implement `documents → segment → search → prompt → answer` and observe a failure at each boundary.
- **Prerequisites:** Chapter 01; a short in-lab primer teaches the Python lists and dictionaries used here.
- **Section 1 — Index and query time.** Topic: source representation; micro-concepts: document IDs, text spans, crude splitting, token overlap score. Topic: retrieval; micro-concepts: scoring every span, top-k selection, deterministic tie breaking.
- **Section 2 — Evidence in the prompt.** Topic: context assembly; micro-concepts: source labels, token budget estimate, quoted evidence, explicit unsupported-answer behavior. Topic: minimal telemetry; micro-concepts: request/query IDs, source snapshot, candidate IDs and scores, selected context IDs, wall-clock latency, status, redacted structured log.
- **Lab:** Implement a 10-document local engine with a stub generator and one structured request record, then optionally connect an LLM.
- **Visual:** Separate index-time and query-time sequence diagrams.
- **Trade-off / misconception:** A prompt containing a retrieved passage may still yield an unsupported answer.
- **Unlocks:** Concrete failures that motivate indexing, ranking, and evaluation.

### Module 02 — Computing and language-model tools

#### Chapter 03 — Data, algorithms, and measurements needed for search

- **Authored materials:** [Chapter](chapters/chapter-03-data-algorithms-and-measurements-needed-for-search.md) · [Lab](labs/chapter-03/LAB.md) · [Solutions](solutions/chapter-03-solutions.md) · [V0 characterization](projects/V0/CHAPTER_03_MEASUREMENT.md).
- **Objective:** Acquire the minimum programming and mathematical vocabulary used by later chapters.
- **Prerequisites:** Chapter 02.
- **Section 1 — Data structures and costs.** Topic: storage; micro-concepts: arrays, maps, sets, sorting, hash lookup, bytes vs characters, memory vs disk. Topic: complexity; micro-concepts: input size, linear scan, logarithmic lookup, upper bounds vs measured latency.
- **Section 2 — Mathematical tools.** Topic: algebra and statistics; micro-concepts: sums, logs, probability, distributions, vectors, norms, averages, percentiles, uncertainty. Topic: experiments; micro-concepts: controls, reproducibility, train/validation/test leakage.
- **Lab:** Count tokens and benchmark scan vs dictionary lookup at several corpus sizes.
- **Visual:** Growth curves with axes and units.
- **Trade-off / misconception:** Big-O alone does not predict wall-clock latency or I/O.
- **Unlocks:** Index construction and quantitative ranking.

#### Chapter 04 — What an LLM does with supplied context

- **Authored materials:** [Chapter](chapters/chapter-04-what-an-llm-does-with-supplied-context.md) · [Lab](labs/chapter-04/LAB.md) · [Solutions](solutions/chapter-04-solutions.md) · [V0 context probes](projects/V0/CHAPTER_04_CONTEXT_PROBES.md).
- **Objective:** Explain why retrieving relevant text is necessary but insufficient for grounded answers.
- **Prerequisites:** Chapters 01–03.
- **Section 1 — Minimal language-model mechanics.** Topic: tokens and generation; micro-concepts: tokenization, next-token prediction, attention intuition, context position, instructions vs untrusted data. Topic: context limitations; micro-concepts: truncation, distraction, conflicting passages, answerability.
- **Section 2 — Knowledge access choices.** Topic: model adaptation; micro-concepts: in-context examples, continued pretraining, fine-tuning, external memory, tool calls, freshness and provenance differences.
- **Lab:** Hold the evidence fixed and vary its position, conflicts, and response instructions.
- **Visual:** Prompt slots and evidence-to-claim arrows.
- **Trade-off / misconception:** A larger context window changes the budget; it does not select evidence or validate claims.
- **Unlocks:** Retrieval quality as a distinct engineering problem.

## Part II — Information retrieval foundations [FOUNDATIONAL]

### Module 03 — Lexical search machinery

#### Chapter 05 — Text normalization and inverted indexes

- **Authored materials:** [Chapter](chapters/chapter-05-text-normalization-and-inverted-indexes.md) · [Lab](labs/chapter-05/LAB.md) · [Solutions](solutions/chapter-05-solutions.md) · [V1 index preview](projects/V1/README.md).
- **Objective:** Build an index that avoids scanning every document for every query.
- **Prerequisites:** Chapters 02–03.
- **Section 1 — From text to terms.** Topic: lexical processing; micro-concepts: corpus, document, field, term, token, vocabulary, case and Unicode normalization, stop words, stemming, lemmatization, n-grams, fuzzy matching and their loss of information.
- **Section 2 — Index structures.** Topic: inverted index; micro-concepts: posting list, document ID, term frequency, positions, skip pointers, Boolean AND/OR/NOT, phrase search. Topic: forward index; micro-concepts: stored fields, document length, reconstruction and highlighting.
- **Lab:** Implement postings and phrase queries; inspect a rare product code and a misspelling.
- **Visual:** Five documents transformed into a term-to-postings table.
- **Trade-off / misconception:** Aggressive normalization may merge distinctions needed for exact identifiers.
- **Unlocks:** Weighted ranking without full scans.

#### Chapter 06 — TF-IDF, vector-space ranking, and lexical limits

- **Authored materials:** [Chapter](chapters/chapter-06-tf-idf-vector-space-ranking-and-lexical-limits.md) · [Lab](labs/chapter-06/LAB.md) · [Solutions](solutions/chapter-06-solutions.md) · [V1 ranking implementation](projects/V1/README.md).
- **Objective:** Rank documents by term evidence and derive every factor in a sample score.
- **Prerequisites:** Chapter 05 and logarithms from Chapter 03.
- **Section 1 — Weighted terms.** Topic: frequency statistics; micro-concepts: TF, DF, corpus size, IDF, term saturation intuition, field length, zero and rare term handling. Topic: TF-IDF; micro-concepts: weighting variants, sparse document vectors, cosine normalization.
- **Section 2 — Ranking behavior.** Topic: worked calculation; micro-concepts: two-query-term scores, document length effects, synonym mismatch, query term absence, field weighting and language-specific tokenization.
- **Lab:** Implement TF-IDF and explain a ranking reversal after adding a document.
- **Visual:** Sparse term-document matrix with nonzero entries.
- **Trade-off / misconception:** TF-IDF is a family of choices, not one universal formula.
- **Unlocks:** BM25 and sparse neural retrieval comparisons.

### Module 04 — Probabilistic ranking and query execution

#### Chapter 07 — BM25 and other lexical ranking models

- **Authored materials:** [Chapter](chapters/chapter-07-bm25-and-other-lexical-ranking-models.md) · [Lab](labs/chapter-07/LAB.md) · [Solutions](solutions/chapter-07-solutions.md) · [V2 BM25 stage](projects/V2/README.md).
- **Objective:** Calculate and tune BM25, then identify where lexical scoring wins and fails.
- **Prerequisites:** Chapters 05–06.
- **Section 1 — Probabilistic ranking intuition.** Topic: relevance evidence; micro-concepts: odds, IDF motivation, term-frequency saturation, document-length normalization, query term summation, `k1` and `b`, nonnegative IDF conventions.
- **Section 2 — Variants and alternatives.** Topic: BM25 family; micro-concepts: BM25+, fielded BM25, parameter fitting, query likelihood language models, smoothing, exact and fuzzy matching. Topic: limits; micro-concepts: paraphrases, rare identifiers, short fields, domain tokenization.
- **Lab:** Implement BM25 and compare with TF-IDF on long and short documents.
- **Visual:** Saturation and length-normalization curves.
- **Trade-off / misconception:** BM25's strength depends on corpus, query type, analyzer, and tuning; it is not automatically inferior to dense search.
- **Unlocks:** A serious lexical baseline for every later experiment.

#### Chapter 08 — Production lexical query execution

- **Authored materials:** [Chapter](chapters/chapter-08-production-lexical-query-execution.md) · [Lab](labs/chapter-08/LAB.md) · [Solutions](solutions/chapter-08-solutions.md) · [V2 exact-pruning stage](projects/V2/README.md).
- **Objective:** Explain how a search engine returns exact top-k BM25 results without scoring every matching document.
- **Prerequisites:** Chapters 05–07; a top-k heap is introduced here before use.
- **Section 1 — Postings on disk.** Topic: execution structures; micro-concepts: gap/delta encoding, variable-byte codes, compressed postings, positions and skip data, fielded indexes, immutable segments, segment merging, index-time impacts
- **Section 2 — Top-k execution.** Topic: query plans; micro-concepts: term-at-a-time vs document-at-a-time, posting intersection, score upper bounds, MaxScore, WAND, Block-Max WAND, impact ordering, safe vs approximate early termination, heap threshold and query latency
- **Lab:** Implement a toy upper-bound pruning searcher; compare scored-document count, exact top-k agreement and latency with exhaustive BM25.
- **Visual:** Posting cursors, block upper bounds, and the moving top-k threshold on the same query.
- **Trade-off / misconception:** BM25 defines scores; pruning is correct only when upper bounds and update rules are valid.
- **Unlocks:** Production search internals and staged retrieval cost analysis.

#### Chapter 09 — Relevance judgments and ranking metrics

- **Authored materials:** [Chapter](chapters/chapter-09-relevance-judgments-and-ranking-metrics.md) · [Lab](labs/chapter-09/LAB.md) · [Solutions](solutions/chapter-09-solutions.md) · [V2 judged evaluation stage](projects/V2/README.md).
- **Objective:** Measure whether the right documents appear and in what order.
- **Prerequisites:** Chapters 05–07; basic averages from Chapter 03.
- **Section 1 — Defining relevance.** Topic: qrels; micro-concepts: query sets, document vs passage relevance, binary and graded labels, pooling, assessor disagreement, incomplete judgments, leakage.
- **Section 2 — Ranking measures.** Topic: set and rank measures; micro-concepts: Precision@K, Recall@K, Hit Rate, F1, reciprocal rank and MRR, average precision and MAP, DCG and NDCG, cutoffs, ties, macro vs micro averaging; report query-set version, measurement window and p50/p95 retrieval latency alongside judged quality.
- **Lab:** Hand-calculate metrics for three rankings and implement a small evaluation harness.
- **Visual:** Ranked lists with relevance labels and cumulative gain.
- **Trade-off / misconception:** A high retrieval score does not establish answer faithfulness; unjudged documents are not necessarily irrelevant.
- **Unlocks:** Experimental comparison of dense and ANN retrieval.

## Part III — Embeddings and retriever learning [INTERMEDIATE]

### Module 05 — Vector representations and training

#### Chapter 10 — Vectors, distance, and exact similarity

- **Authored materials:** [Chapter](chapters/chapter-10-vectors-distance-and-exact-similarity.md) · [Lab](labs/chapter-10/LAB.md) · [Solutions](solutions/chapter-10-solutions.md) · [V3 exact-vector foundation](projects/V3/README.md).
- **Objective:** Calculate similarities and explain how metric choice changes nearest neighbors.
- **Prerequisites:** Chapter 03 and lexical sparse vectors from Chapter 06.
- **Section 1 — Geometry.** Topic: representation; micro-concepts: dimensions, coordinates, sparse vs dense, norm, normalization, anisotropy intuition. Topic: comparisons; micro-concepts: dot product, inner product, cosine, Euclidean and Manhattan distance, unit-vector relationships.
- **Section 2 — Retrieval computation.** Topic: exact KNN; micro-concepts: score every vector, sort or heap top-k, matrix multiplication, `O(Nd)` work per query, memory layout, batching.
- **Lab:** Calculate three distances by hand and implement brute-force top-k with deterministic ties.
- **Visual:** Two-dimensional vectors plus a warning about high-dimensional intuition.
- **Trade-off / misconception:** Cosine is not inherently semantic; the embedding model and normalization define what it measures.
- **Unlocks:** Learned text embeddings and ANN.

#### Chapter 11 — How embedding models learn retrieval spaces

- **Authored materials:** [Chapter](chapters/chapter-11-how-embedding-models-learn-retrieval-spaces.md) · [Lab](labs/chapter-11/LAB.md) · [Solutions](solutions/chapter-11-solutions.md) · [V3 frozen-encoder stage](projects/V3/README.md).
- **Objective:** Explain what an encoder maps into a vector and how training makes proximity useful.
- **Prerequisites:** Chapters 04 and 10.
- **Section 1 — Representations.** Topic: embedding pipeline; micro-concepts: word vs contextual token vs sentence/document vectors, pooling, bi-encoder/dual-encoder, query/document asymmetry, instruction prefixes, multilingual and domain shift.
- **Section 2 — Learning relevance.** Topic: contrastive training; micro-concepts: positive pairs, hard negatives, in-batch negatives, temperature, score function, false negatives, dimensionality, Matryoshka prefixes and their evaluation.
- **Lab:** Compare a tiny trained or pretrained encoder against lexical search on paraphrases and IDs.
- **Visual:** Query and passage encoders feeding a similarity matrix.
- **Trade-off / misconception:** “Embeddings understand meaning” hides the training objective, domain limits, and exact-match failures.
- **Unlocks:** Dense retrieval and embedding model selection.

#### Chapter 12 — Retriever training and domain adaptation

- **Authored materials:** [Chapter](chapters/chapter-12-retriever-training-and-domain-adaptation.md) · [Lab](labs/chapter-12/LAB.md) · [Solutions](solutions/chapter-12-solutions.md) · [V3 adaptation stage](projects/V3/README.md).
- **Objective:** Train or adapt a dual encoder, then test whether the gain survives domain and language shifts.
- **Prerequisites:** Chapters 09–11 and relevance judgments in Chapter 09.
- **Section 1 — Training signal.** Topic: pairs and objectives; micro-concepts: queries and passages, positives, explicit/in-batch/mined/hard negatives, false negatives, weak supervision, teacher labels, synthetic query generation, softmax/InfoNCE, temperature, triplet/margin losses, pairwise/listwise variants and score distributions
- **Section 2 — Adaptation and validation.** Topic: mining and distillation; micro-concepts: BM25/dense/reranker hard negatives, iterative mining, false-negative detection, cross-encoder teacher to bi-encoder student, score vs ranking distillation, zero-shot vs fine-tuning, multilingual and cross-lingual transfer, catastrophic over-specialization, train/test leakage and corpus sampling
- **Lab:** Evaluate a baseline model on a small domain test set; adapt on separate training pairs; compare per-slice quality and latency against the frozen baseline, including multilingual queries where available.
- **Visual:** Training pairs and a contrastive score matrix, then separate train/test corpora.
- **Trade-off / misconception:** Leaderboard gains on MS MARCO, BEIR, MTEB or MIRACL do not establish a gain on the learner's domain; monitor generalization.
- **Unlocks:** Informed dense-model selection, sparse/late-interaction comparisons, and benchmark literacy.

### Module 06 — Dense and learned retrieval

#### Chapter 13 — Dense candidate retrieval in practice

- **Authored materials:** [Chapter](chapters/chapter-13-dense-candidate-retrieval-in-practice.md) · [Lab](labs/chapter-13/LAB.md) · [Solutions](solutions/chapter-13-solutions.md) · [V3 materialized exact-dense stage](projects/V3/README.md).
- **Objective:** Build a dense index and diagnose representation, metric, and domain failures.
- **Prerequisites:** Chapters 09–11.
- **Section 1 — Indexing and querying.** Topic: pipeline; micro-concepts: batching, embedding versions, vector IDs, normalization, exact score, top-k, query and document encoder pairing. Topic: benchmarks; micro-concepts: quality by query slice, cold vs warm latency, embeddings per second.
- **Section 2 — Failure analysis.** Topic: mismatch; micro-concepts: acronyms, exact codes, negation, numeric constraints, out-of-domain language, multilingual transfer, changing model versions.
- **Lab:** Build exact dense retrieval and compare BM25 and dense on labeled query slices.
- **Visual:** Paired indexing and query flows with score traces.
- **Trade-off / misconception:** Dense retrieval is a candidate generator, not proof of relevance.
- **Unlocks:** ANN and hybrid search.

#### Chapter 14 — Sparse neural search and late interaction

- **Authored materials:** [Chapter](chapters/chapter-14-sparse-neural-search-and-late-interaction.md) · [Lab](labs/chapter-14/LAB.md) · [Solutions](solutions/chapter-14-solutions.md) · [V3 mechanism sandbox](projects/V3/README.md).
- **Objective:** Place learned sparse and token-level interaction models between lexical and single-vector retrieval.
- **Prerequisites:** Chapters 06–13.
- **Section 1 — Learned sparse retrieval.** Topic: SPLADE-style methods; micro-concepts: vocabulary-space weights, expansion terms, sparsity regularization, inverted-index compatibility, index size and latency.
- **Section 2 — Fine-grained interaction.** Topic: ColBERT-style methods; micro-concepts: separate token encoders, document token storage, MaxSim, late interaction, pruning, candidate retrieval vs reranking roles.
- **Lab:** Compute a tiny MaxSim matrix and compare it with a single-vector score.
- **Visual:** Token-to-token score grid.
- **Trade-off / misconception:** Late interaction is neither ordinary single-vector ANN nor a full cross-encoder.
- **Unlocks:** More precise retrieval choices and staged ranking.

## Part IV — Approximate search and storage [ADVANCED]

### Module 07 — Why approximation works

#### Chapter 15 — Exact KNN to trees and hashing

- **Authored materials:** [Chapter](chapters/chapter-15-exact-knn-to-trees-and-hashing.md) · [Lab](labs/chapter-15/LAB.md) · [Solutions](solutions/chapter-15-solutions.md) · [V4 exact/KD/LSH stage](projects/V4/README.md).
- **Objective:** Explain when exact search becomes expensive and how early ANN families prune work.
- **Prerequisites:** Chapters 10–13.
- **Section 1 — Baseline and scale.** Topic: exhaustive search; micro-concepts: `N × d` comparisons, cache behavior, memory bandwidth, top-k selection, recall relative to exact results, high-dimensional distance concentration.
- **Section 2 — Partition methods.** Topic: trees and hashes; micro-concepts: KD-tree split axes, ball-tree bounds, backtracking, dimensional degradation, locality-sensitive hashing collision probability, random projections and candidate buckets.
- **Lab:** Plot exact latency with corpus size; implement a toy random-hyperplane LSH and measure recall.
- **Visual:** Tree partitions and hash buckets beside the full scan.
- **Trade-off / misconception:** ANN speedups are workload-dependent and must be reported with recall against exact KNN.
- **Unlocks:** Quantization, graph indexes, and index benchmarking.

#### Chapter 16 — IVF, quantization, and compressed vectors

- **Objective:** Trace coarse assignment, candidate probing, and approximate distance reconstruction.
- **Prerequisites:** Chapters 10 and 15; clustering intuition is introduced here.
- **Section 1 — Coarse partitions.** Topic: IVF; micro-concepts: centroids, training sample, assign vectors to lists, residuals, `nlist`, `nprobe`, IVF-Flat, unbalanced lists, update costs.
- **Section 2 — Compression.** Topic: quantization; micro-concepts: scalar quantization, product subspaces, codebooks, byte codes, lookup-table distance, IVF-PQ, reconstruction error, reranking exact originals. Topic: lifecycle; micro-concepts: training sample bias, rebuilding centroids/codebooks, inserts, deleted IDs and distributed list ownership.
- **Lab:** Implement two-dimensional coarse cells and a toy product quantizer; chart recall, bytes, and latency.
- **Visual:** Centroid cells plus subvector-to-codebook lookup.
- **Trade-off / misconception:** Compression and coarse pruning produce distinct errors; tune and measure each.
- **Unlocks:** Memory-aware vector index design.

### Module 08 — Graph ANN and vector systems

#### Chapter 17 — Proximity graphs, NSW, and HNSW

- **Objective:** Explain and trace HNSW insertion and search with its main tuning knobs.
- **Prerequisites:** Chapters 10, 15–16; graph vocabulary is introduced locally before traversal.
- **Section 1 — Navigable graphs.** Topic: NSW; micro-concepts: vertices as vectors, proximity edges, greedy descent, local minima, long-range links, candidate queues, visited sets. Topic: HNSW hierarchy; micro-concepts: random level assignment, upper-layer entry point, layer descent, base layer.
- **Section 2 — Construction and query.** Topic: insertion; micro-concepts: neighbor search, diversity heuristic, reciprocal links, degree limit `M`, `efConstruction`, deletions and tombstones. Topic: query; micro-concepts: `efSearch`, bounded candidate expansion, recall/latency curve, memory per edge, serialization and concurrency.
- **Lab:** Step through a tiny layered graph on paper, then sweep `M` and `efSearch` in an implementation.
- **Visual:** Layered graph with entry point, traversed path, and candidate frontier.
- **Trade-off / misconception:** HNSW performance and complexity are empirical and workload-sensitive; it is not a universal logarithmic guarantee.
- **Unlocks:** Graph ANN benchmarking and vector-store architecture.

#### Chapter 18 — Disk ANN, benchmarks, and vector databases

- **Objective:** Distinguish an index algorithm, a library, a search engine, and a database service.
- **Prerequisites:** Chapters 15–17 and database vocabulary from Chapter 03.
- **Section 1 — Index portfolios.** Topic: families; micro-concepts: disk-resident graph search such as DiskANN, SSD random reads, caches, ScaNN-style partition/quantize/rerank, FAISS index families, training vs build time, inserts/deletes, benchmark recall/latency/throughput.
- **Section 2 — System boundary.** Topic: vector services; micro-concepts: FAISS library vs pgvector in PostgreSQL vs search engines (Elasticsearch, OpenSearch, Vespa) vs purpose-built stores (Qdrant, Milvus, Weaviate, Pinecone) vs local/embedded choices (Chroma, LanceDB); persistence, namespaces, metadata, filter execution, partition/shard routing, replication, write durability, consistency, backup, multi-tenancy and observability. Topic: selection; micro-concepts: ingest throughput, query throughput, filtered recall, operational ownership and portability.
- **Lab:** Run one exact and one approximate index under identical queries; record index size, build time, p95 latency, and recall.
- **Visual:** Layer diagram from vector to ANN index to storage service.
- **Trade-off / misconception:** Product features and index defaults change; architectural category and measured workload matter more than vendor labels.
- **Unlocks:** Designing an ingestion and serving stack.

## Part V — Building a trustworthy corpus [INTERMEDIATE / PRODUCTION]

### Module 09 — Data extraction and segmentation

#### Chapter 19 — Source ingestion and document quality

- **Objective:** Turn heterogeneous sources into normalized, auditable documents before embedding them.
- **Prerequisites:** Chapters 02, 05, and 18.
- **Section 1 — Source adapters.** Topic: formats; micro-concepts: plain text, Markdown, HTML/websites, PDF vs scanned PDF and OCR, Word, spreadsheets, slides, JSON/API, SQL rows, email/tickets/wiki, code, image, audio/video transcript. Topic: extraction; micro-concepts: tables, reading order, headers, footnotes, page coordinates and source anchors.
- **Section 2 — Quality pipeline.** Topic: records; micro-concepts: stable source IDs, parse errors, cleaning, Unicode normalization, deduplication, boilerplate removal, enrichment, version and checksum, quarantine, validation and provenance. Topic: governance; micro-concepts: source licensing, retention requirements, deletion obligations and allowed indexing uses.
- **Lab:** Ingest three formats; report dropped or ambiguous content and trace a chunk to its original page.
- **Visual:** Source-to-canonical-document lineage with rejection points.
- **Trade-off / misconception:** A more sophisticated retriever cannot recover text lost or scrambled during parsing.
- **Unlocks:** Meaningful chunk design and source-specific evaluation.

#### Chapter 20 — Chunking as a retrieval design decision

- **Objective:** Select segmentation by document structure, question granularity, and measured answer coverage.
- **Prerequisites:** Chapters 09, 11–13, and 19.
- **Section 1 — Boundaries.** Topic: strategies; micro-concepts: fixed characters/tokens, sentences, paragraphs, recursive splits, overlap, Markdown/HTML/layout/code/conversation boundaries, semantic and proposition segmentation, query-aware/adaptive proposals. Topic: parameters; micro-concepts: token count, overlap ratio, heading context, section continuity.
- **Section 2 — Multi-scale retrieval.** Topic: parent-child; micro-concepts: child match vs parent expansion, small-to-big, hierarchical summaries, RAPTOR-style trees, late chunking, contextual retrieval (adding document context before indexing), chunk-to-document mapping. Topic: measurement; micro-concepts: boundary quality, recall, redundancy, embedding cost, context dilution and citation span accuracy.
- **Lab:** Compare at least three chunkers on the same judged questions and report recall, duplicate context, and answer evidence span.
- **Visual:** One document with competing boundaries and retrieved spans.
- **Trade-off / misconception:** Larger or overlapping chunks do not monotonically improve answer quality.
- **Unlocks:** Controlled index metadata and hierarchical retrieval.

### Module 10 — Metadata, authorization, and updates

#### Chapter 21 — Metadata schemas and filtered retrieval

- **Objective:** Use structured attributes and permissions to reduce the eligible search space correctly.
- **Prerequisites:** Chapters 05, 13, 18–20.
- **Section 1 — Metadata design.** Topic: schema; micro-concepts: source, tenant, owner, ACL, timestamps, version, entity, language, hierarchy, stable IDs, extraction confidence and missing values. Topic: constraints; micro-concepts: exact IDs, date ranges, field filters and SQL-like predicates.
- **Section 2 — Filter execution.** Topic: placement; micro-concepts: prefilter, ANN-aware filtering, postfilter, filter selectivity, empty result behavior, oversampling, authorization before evidence leaves the service.
- **Lab:** Compare metadata filtering with semantic scoring on an exact-date and exact-tenant query.
- **Visual:** Candidate sets before and after each filter placement.
- **Trade-off / misconception:** Postfiltering an unauthorized top-k can leak information and underfill results.
- **Unlocks:** Secure hybrid retrieval and production ACL design.

#### Chapter 22 — Freshness, versions, and incremental indexes

- **Objective:** Keep answers tied to the correct version of changing sources.
- **Prerequisites:** Chapters 19–21.
- **Section 1 — Change detection.** Topic: ingestion lifecycle; micro-concepts: polling vs events vs CDC, content hashes, idempotent upserts, out-of-order events, document lineage, tombstones, deletions, replay.
- **Section 2 — Reindexing and time.** Topic: migration; micro-concepts: embedding model/version compatibility, dual indexes, backfill, cutover, rollback, stale cache invalidation, temporal filters vs freshness boosting, as-of queries.
- **Lab:** Edit and delete a document; prove the new version appears and the old one cannot be retrieved.
- **Visual:** Version timeline and two-index migration.
- **Trade-off / misconception:** A recently updated source is not necessarily the relevant one; freshness and relevance must be measured separately.
- **Unlocks:** Reliable production ingestion and temporal retrieval.

## Part VI — Selecting and ranking evidence [INTERMEDIATE / ADVANCED]

### Module 11 — Query understanding

#### Chapter 23 — Normalize, classify, route, and contextualize queries

- **Objective:** Determine what kind of evidence a query requires before searching.
- **Prerequisites:** Chapters 05, 13, and 20–22.
- **Section 1 — Query interpretation.** Topic: parsing; micro-concepts: normalization, spelling, entities, identifiers, language, intent, temporal expressions, aggregation cues, ambiguity and follow-up references.
- **Section 2 — Routing.** Topic: source selection; micro-concepts: lexical/dense/SQL/graph/web/tool routes, deterministic rules vs learned router, confidence, fallback, authorization, query-plan logging.
- **Lab:** Build a rule-based router for exact ID, paraphrase, date, relationship, and count queries.
- **Visual:** Decision tree with abstain and fallback branches.
- **Trade-off / misconception:** Query rewriting can erase precise entities or temporal constraints; preserve the original query.
- **Unlocks:** Safe query expansion and multi-source plans.

#### Chapter 24 — Rewrite, expand, and decompose queries

- **Objective:** Increase candidate recall without creating unsupported intent.
- **Prerequisites:** Chapters 09, 11–13, and 23.
- **Section 1 — Lexical and semantic reformulation.** Topic: expansion; micro-concepts: synonyms, spelling variants, pseudo-relevance feedback, multiple paraphrases, HyDE hypothetical passage, step-back prompts and their failure modes.
- **Section 2 — Planning.** Topic: decomposition; micro-concepts: subqueries, dependency order, query fan-out, deduplication, budget, stopping, original-query anchor, per-branch evaluation.
- **Lab:** Compare original, multi-query, and HyDE-style retrieval on a fixed judgment set.
- **Visual:** Query fan-out and merge with branch costs.
- **Trade-off / misconception:** More generated queries may add false positives, latency, and cost.
- **Unlocks:** Hybrid candidate fusion and multi-hop retrieval.

### Module 12 — Hybrid retrieval and staged ranking

#### Chapter 25 — Hybrid candidate generation and fusion

- **Objective:** Combine complementary retrievers while keeping scores interpretable.
- **Prerequisites:** Chapters 07–14, 21, and 24.
- **Section 1 — Candidate sets.** Topic: union and intersection; micro-concepts: lexical wins on IDs/acronyms, dense wins on paraphrases, sparse-neural bridge, overlap, coverage, recall budgets and per-source quotas.
- **Section 2 — Fusion.** Topic: scoring; micro-concepts: raw-score incompatibility, query-document score calibration, min-max/z-score pitfalls, weighted fusion, reciprocal rank fusion with rank constant, RAG Fusion, learned fusion and leakage.
- **Lab:** Hand-calculate RRF for two rankings and test exact-ID and paraphrase cases.
- **Visual:** Two ranked streams merged into one candidate pool.
- **Trade-off / misconception:** Hybrid search cannot compensate for bad parsing or missing indexed content.
- **Unlocks:** Reranking on a wider candidate set.

#### Chapter 26 — Reranking, diversity, and deduplication

- **Objective:** Explain why selecting eight directly differs from retrieving 100, reranking 30, then packing eight.
- **Prerequisites:** Chapters 09, 11–14, and 25.
- **Section 1 — Relevance models.** Topic: stages; micro-concepts: first-stage retrieval vs second-stage ranking, bi-encoder vs cross-encoder, feature-based vs neural vs LLM ranking, score interpretation and batch costs. Chapter 27 derives learning objectives and training.
- **Section 2 — Selection beyond score.** Topic: coverage; micro-concepts: near-duplicate removal, Maximal Marginal Relevance, novelty, source balance, recency and business rules, hard ACL constraint vs soft ranking feature.
- **Lab:** Implement a 100→30→8 funnel and compare judged top-eight quality and latency.
- **Visual:** Retrieval funnel with cost at each stage.
- **Trade-off / misconception:** Reranking only reorders available candidates; it cannot recover a missed document.
- **Unlocks:** Deliberate context construction.

#### Chapter 27 — Learning to rank for staged retrieval

- **Objective:** Train and compare feature-based and neural rankers for an already retrieved candidate set.
- **Prerequisites:** Chapters 09, 13–14, and 25–26; labeled rankings are available from Chapter 09.
- **Section 1 — Feature-based ranking.** Topic: learning objectives; micro-concepts: lexical/dense/metadata features, feature normalization, leakage, pointwise regression/classification, pairwise preferences, listwise objectives, RankNet gradient intuition, LambdaRank metric weighting, LambdaMART boosted trees
- **Section 2 — Neural reranking.** Topic: production funnel; micro-concepts: cross-encoder and LLM rerankers, teacher-student distillation, score calibration, query-document score distributions, candidate depth vs cost, training data bias, latency budgets and fallbacks
- **Lab:** Fit a small feature-based ranker and compare it with BM25, a cross-encoder, and a fixed heuristic on the same qrels; plot quality against candidate depth and cost.
- **Visual:** Historical path: heuristic score → learned features → neural cross-encoder → LLM reranker, with per-stage cost.
- **Trade-off / misconception:** A stronger ranker cannot restore a missing candidate; ranker training can overfit candidate-generation bias.
- **Unlocks:** Evidence selection with calibrated scores and defensible ranking budgets.

## Part VII — Context, grounded generation, and core evaluation [INTERMEDIATE / ADVANCED]

### Module 13 — Turning candidates into answers

#### Chapter 28 — Context selection and packing

- **Objective:** Construct a bounded evidence packet that preserves answer-bearing spans and source identity.
- **Prerequisites:** Chapters 20, 25–27, and model context basics from Chapter 04.
- **Section 1 — Selection.** Topic: budgets; micro-concepts: tokenizer counts, model input/output reserve, dynamic top-k, similarity thresholds and their calibration, no-result detection, marginal evidence gain, parent expansion, contextual headers, contextual compression, diversity and source quotas.
- **Section 2 — Presentation.** Topic: packing; micro-concepts: ordering, chronology, contradictory evidence grouping, compression, deduplication, lost-in-the-middle effects, citations and span offsets, truncation audits.
- **Lab:** Compare answer quality as context grows; include a deliberately buried decisive passage.
- **Visual:** Token-budget rectangle with evidence blocks and claim links.
- **Trade-off / misconception:** The top-scoring chunks are not automatically the best final context set.
- **Unlocks:** Grounding and citation verification.

#### Chapter 29 — Grounded generation, verification, and abstention

- **Objective:** Separate answer correctness, faithfulness to evidence, and citation accuracy.
- **Prerequisites:** Chapters 04, 09, and 28.
- **Section 1 — Generation contract.** Topic: prompts; micro-concepts: task instruction, data delimiters, untrusted retrieved text, answerability threshold, conflicting evidence, temporal scope, response schema.
- **Section 2 — Verification.** Topic: claim-to-source checks; micro-concepts: atomic claims, entailment limits, citation span support, negative and contradictory evidence, unsupported additions, no-result behavior, uncertainty and abstention, post-generation repair and its cost.
- **Lab:** Generate answers to supported, conflicting, and unanswerable questions; annotate each claim.
- **Visual:** Evidence spans feeding claims, with unsupported claims highlighted.
- **Trade-off / misconception:** A cited answer may still misrepresent or contradict its source.
- **Unlocks:** Evaluation of generation and conversational evidence use.

### Module 14 — Core RAG evaluation

#### Chapter 30 — Retrieval evaluation at system depth

- **Objective:** Build a defensible relevance dataset and distinguish candidate coverage from final ranking quality.
- **Prerequisites:** Chapters 09, 20, and 25–29.
- **Section 1 — Dataset construction.** Topic: judgments; micro-concepts: qrels recap, golden sets, human vs synthetic questions, hard negatives, query slices, passage/document labels, graded relevance, pooled judgments, assessor agreement, temporal and ACL-specific cases.
- **Section 2 — Analysis.** Topic: metrics; micro-concepts: Recall@K at each retrieval stage, Precision@K, Hit Rate, MRR, MAP, NDCG, context recall, context precision, evidence coverage, diversity, per-slice failures, ANN recall vs relevance recall, dataset and rubric version in every reported quality series. Confidence intervals return in Chapter 48.
- **Lab:** Build a small golden set and implement a reproducible retrieval/context metric harness; report recall lost at parsing, first stage, filter, fusion, reranking and packing.
- **Visual:** Stage-wise recall waterfall.
- **Trade-off / misconception:** One aggregate metric can hide catastrophic exact-ID, rare-language, or permission failures.
- **Unlocks:** Answer evaluation and localization of faults.

#### Chapter 31 — Generation and end-to-end evaluation

- **Objective:** Evaluate answer correctness, evidence support and end-to-end utility separately from retrieval quality.
- **Prerequisites:** Chapters 28–30.
- **Section 1 — Answer criteria.** Topic: human and automated labels; micro-concepts: factual correctness, completeness, relevance, faithfulness, citation accuracy, abstention, unsupported-claim rate, contradictory sources.
- **Section 2 — Evaluation operations.** Topic: methods; micro-concepts: blind human review, LLM-as-judge basics and rubric, position and model bias, calibration against humans, basic regression suite, answerability tests and sampled online judgments. Online A/B and release gates return in Chapter 48; operational dashboards and SLIs/SLOs mature in Chapter 52. Tool examples (RAGAS, TruLens, DeepEval, LangSmith) are mapped to metrics, not used as definitions.
- **Lab:** Extend the Chapter 30 harness with answer correctness, faithfulness, citation support and abstention checks; grade 30 answers and inspect human vs model-judge disagreements.
- **Visual:** Three diagnostic scorecards: retrieval, answer, and request behavior; production dashboard construction returns in Chapter 52.
- **Trade-off / misconception:** LLM judge scores are measurements with bias, not ground truth.
- **Unlocks:** Systematic debugging and experiment design.

### Module 15 — Baseline debugging and benchmark literacy

#### Chapter 32 — Baseline RAG debugging and trace inspection

- **Objective:** Locate failures at the earliest responsible stage using a reproducible trace.
- **Prerequisites:** Chapters 19–31.
- **Section 1 — Trace anatomy.** Topic: stages; micro-concepts: request/trace/span IDs, parent-child and parallel spans, correlation with logs/events, candidate vs evidence IDs, source/index/prompt/model versions, missing source, parse loss, wrong boundary, embedding mismatch, ANN miss, faulty filter, fusion failure, reranker error, truncation, prompt noncompliance and unsupported answer.
- **Section 2 — Diagnostic procedure.** Topic: controlled probes; micro-concepts: exact-search oracle, authorization-safe filter probe, inspect candidates and scores, swap context with gold evidence, replay input, redaction/retention, minimal failure case, first failing stage. Production alert thresholds return in Chapter 48.
- **Lab:** Implement a minimal nested request trace and diagnose injected faults across at least five stages; provide minimal reproduction and a proposed fix.
- **Visual:** Decision tree from failed answer to first failing stage.
- **Trade-off / misconception:** Prompt edits cannot fix a document that was never ingested or authorized.
- **Unlocks:** Reliable regression and incident handling.

#### Chapter 33 — Benchmark literacy and dataset transfer

- **Objective:** Read a benchmark as a task distribution with labels and blind spots, not as a leaderboard number.
- **Prerequisites:** Chapters 09, 12–14, and 30–32.
- **Section 1 — Retrieval datasets.** Topic: task contracts; micro-concepts: MS MARCO, Natural Questions, BEIR, MTEB, MIRACL, LoTTE, HotpotQA, MuSiQue, BRIGHT; corpus, query source, relevance unit, label completeness, metric, shortcut risks and language coverage
- **Section 2 — RAG and multimodal benchmarks.** Topic: transfer checks; micro-concepts: TREC RAG, ViDoRe and domain-specific sets; answer/evidence labels, citation and support criteria, corpus drift, multilingual vs cross-lingual evaluation, contamination, licensing, sampling and production resemblance
- **Lab:** Create dataset cards for three benchmarks and one local corpus; identify what each rewards, what it misses, and which metric is comparable.
- **Visual:** Benchmark-task matrix: query distribution × corpus × labels × metric × deployment resemblance.
- **Trade-off / misconception:** A benchmark ranking is conditional on its corpus and judgments; leaderboard position is not a deployment decision.
- **Unlocks:** Critical evaluation of advanced retrieval papers and later architecture claims.

## Part VIII — Conversation and dynamic retrieval [ADVANCED]

### Module 16 — Conversation and evidence chains

#### Chapter 34 — Conversational retrieval and memory

- **Objective:** Resolve follow-up references while keeping session state separate from durable knowledge.
- **Prerequisites:** Chapters 22–24 and 29.
- **Section 1 — Dialogue state.** Topic: contextualization; micro-concepts: pronouns, ellipsis, entity history, topic shifts, original turn preservation, query rewriting with uncertainty.
- **Section 2 — Memory and personalization.** Topic: state storage; micro-concepts: recent turns, summaries, user preferences, durable source records, permission scope, retention, stale memory and contradiction.
- **Lab:** Make “What did he study?” retrieve the intended person after an earlier question; test an ambiguous follow-up.
- **Visual:** Session state and retrieval corpus as distinct stores.
- **Trade-off / misconception:** Conversation memory is neither an authorized knowledge base nor a reliable substitute for source retrieval.
- **Unlocks:** Multi-step retrieval with state.

#### Chapter 35 — Multi-hop and iterative retrieval

- **Objective:** Build evidence chains for questions whose answer needs linked facts, and measure each hop separately.
- **Prerequisites:** Chapters 23–24, 28–33, and conversational state in Chapter 34.
- **Section 1 — Question structure.** Topic: decomposition; micro-concepts: single-hop vs multi-hop, dependent vs independent subquestions, intermediate entity discovery, evidence chains/graphs, branch or beam-search intuition, provenance and error propagation
- **Section 2 — Iterative search.** Topic: retrieve–reason–retrieve; micro-concepts: new queries from intermediate evidence, IRCoT-style interleaving, stopping on sufficient evidence, hop-level recall vs final-answer correctness, shortcut baselines, HotpotQA and MuSiQue evaluation caveats
- **Lab:** Implement a two-hop search with traceable intermediate entity IDs; compare one-shot and iterative retrieval on labeled chains.
- **Visual:** Question dependency DAG with per-hop candidates, evidence edges, and stop condition.
- **Trade-off / misconception:** A correct final answer can hide a broken evidence chain; early hop errors propagate and branching raises cost.
- **Unlocks:** Adaptive decisions, agentic policies, and graph traversal.

### Module 17 — Adaptive and agentic control

#### Chapter 36 — Adaptive, active, and corrective retrieval

- **Objective:** Select when to retrieve, retry, or escalate based on measurable information gaps.
- **Prerequisites:** Chapters 29–33 and 35; bounded search state is introduced here.
- **Section 1 — Retrieval triggers.** Topic: policies; micro-concepts: retrieve-always vs if-needed, query difficulty, confidence-based retrieval, information-gap detection, dynamic top-k, similarity thresholds and calibration, no-result detection, retriever confidence vs answer confidence, false-positive and false-negative triggers
- **Section 2 — During and after generation.** Topic: active/corrective mechanisms; micro-concepts: FLARE-style forward-looking retrieval, evidence-quality grading, CRAG-specific correction, Self-RAG trained reflection tokens, retry/fallback, web escalation, negative or contradictory evidence, step/token/monetary cost and latency
- **Lab:** Compare fixed retrieval with a thresholded trigger and a corrective fallback; calibrate trigger errors on a held-out set and report costs.
- **Visual:** State machine for no retrieval, retrieve, grade, retry, escalate, answer, and abstain.
- **Trade-off / misconception:** A model's confidence is not a calibrated probability that the evidence is sufficient; corrective loops can amplify errors.
- **Unlocks:** Explicit retrieval policies for agentic systems.

#### Chapter 37 — Agentic retrieval and tool-orchestrated RAG

- **Objective:** Design a reproducible bounded policy that chooses the next evidence action from observations.
- **Prerequisites:** Chapters 23–24 and 29–36.
- **Later connection:** Tool APIs are introduced here; source-specific APIs are detailed in Chapters 40–41.
- **Section 1 — Control model.** Topic: policy and state; micro-concepts: deterministic pipeline vs dynamic policy, state, observations, actions, tools, source/tool selection, query planning, search loops, evidence inspection, information-gap detection, reflection and verification
- **Section 2 — Operational bounds.** Topic: termination and failure; micro-concepts: step/token/monetary budgets, loop detection, partial success, deterministic guardrails, failure recovery, state machines/graphs, trace replay, reproducibility and escalation to a human
- **Lab:** Implement a bounded tool-choice loop over two local retrievers, with explicit stop rules, loop detection, action trace and budget ledger.
- **Visual:** Policy state graph annotated with observations, actions, guards and terminal states.
- **Trade-off / misconception:** Using tools does not by itself make a workflow agentic; dynamic decisions must depend on observed evidence and remain auditable.
- **Unlocks:** Specialized source orchestration and production traces.

## Part IX — Graph, web, and structured knowledge [ADVANCED]

### Module 18 — Relationship retrieval

#### Chapter 38 — Graphs and knowledge representation

- **Objective:** Represent relationship questions as traversals and identify when text similarity loses a link.
- **Prerequisites:** Chapters 03, 19, and 35.
- **Section 1 — Graph foundations.** Topic: structures; micro-concepts: node, edge, property, directed/undirected, weighted edge, paths, connected components, BFS, DFS, centrality and communities.
- **Section 2 — Knowledge graphs.** Topic: extraction; micro-concepts: entity mentions vs canonical entities, disambiguation, typed relations, provenance, conflicting edges, temporal validity, graph schema and traversal query.
- **Lab:** Build an entity graph from a small corpus and answer two-hop questions with BFS.
- **Visual:** Source sentence → extracted edge → traversed path → cited sentence.
- **Trade-off / misconception:** An extracted relation is a claim with uncertainty, not a ground truth edge.
- **Unlocks:** Graph-based RAG and global corpus questions.

#### Chapter 39 — Knowledge-graph and GraphRAG-style systems

- **Objective:** Compare local path retrieval, community summarization, and passage retrieval by question type.
- **Prerequisites:** Chapters 20, 28–29, and 38.
- **Section 1 — Local graph retrieval.** Topic: query mapping; micro-concepts: entity linking, neighborhood expansion, path constraints, text evidence back-links, graph + vector candidate fusion and hop budgets.
- **Section 2 — Corpus-level synthesis.** Topic: GraphRAG-style workflow; micro-concepts: document extraction, entity/relation graph, community detection, summary construction, local vs global query, summary provenance and update cost. Microsoft GraphRAG is one implementation, not the definition of all graph RAG.
- **Lab:** Compare vector passages, graph paths, and community summaries on a local relationship question and a global-theme question.
- **Visual:** Graph neighborhoods vs hierarchical community summaries.
- **Trade-off / misconception:** Graph construction can be expensive and error-prone; relationship structure helps only when the query and data justify it.
- **Unlocks:** Graph case studies and multi-source architecture.

### Module 19 — Live and structured sources

#### Chapter 40 — Web retrieval and source credibility

- **Objective:** Use live sources while preserving freshness, attribution, and conflicting evidence.
- **Prerequisites:** Chapters 19, 22–29.
- **Section 1 — Live retrieval.** Topic: workflow; micro-concepts: search API, query fan-out, URL selection, robots constraints, fetch and dynamic-page rendering, parsing, canonicalization, duplicates, rate limits.
- **Section 2 — Evidence quality.** Topic: provenance; micro-concepts: publication vs event date, source authority, primary vs secondary, conflicting claims, link rot, citation URL and capture timestamp, web vs pre-indexed retrieval.
- **Lab:** Compare a local stale answer with a current web answer and document the source date and evidence chain.
- **Visual:** Search → fetch → parse → rank → cite, with failure branches.
- **Trade-off / misconception:** Freshness is not credibility; a live page may be incorrect or manipulated.
- **Unlocks:** Current-events case studies and controlled external tools.

#### Chapter 41 — SQL, APIs, and structured retrieval

- **Objective:** Route aggregations and exact records to structured systems with validated queries.
- **Prerequisites:** Chapters 21, 23, 29, and basic relational concepts taught here.
- **Section 1 — Relational foundation.** Topic: schema; micro-concepts: tables, keys, joins, filters, aggregation, snapshot isolation intuition, semantic layers, units and nulls.
- **Section 2 — Safe tool use.** Topic: text-to-SQL and API plans; micro-concepts: schema retrieval, query generation, AST validation, read-only execution, row-level permissions, limit and timeout, result provenance, graph query analogues and structured outputs.
- **Lab:** Answer an aggregate question with SQL and compare with embedding each row as text.
- **Visual:** Natural-language request → validated query → rows → answer.
- **Trade-off / misconception:** Similar rows in embedding space do not implement exact joins, totals, or permission rules.
- **Unlocks:** Multi-source platform design.

## Part X — Multimodal, code, and architecture choices [ADVANCED]

### Module 20 — Document and multimodal evidence

#### Chapter 42 — Document intelligence and layout-aware retrieval

- **Objective:** Extract and retrieve evidence from visually structured documents without losing reading order or coordinates.
- **Prerequisites:** Chapters 19–21, 28–33.
- **Section 1 — Document extraction.** Topic: page structure; micro-concepts: born-digital vs scanned PDF, OCR and error patterns, reading order, coordinate systems and bounding boxes, headers/footers, tables/cells/merged cells, diagrams, figures/captions and layout models
- **Section 2 — Structure-preserving indexing.** Topic: retrieval units; micro-concepts: page-level and region-level indexes, cell-to-table and figure-to-caption links, chunking by layout, coordinate provenance, confidence thresholds, query-time expansion and citation rendering
- **Lab:** Index a mixed PDF at text, page and region levels; retrieve a table cell and a figure caption with coordinate-level citations.
- **Visual:** Annotated page image showing boxes, reading order, cell graph and evidence anchors.
- **Trade-off / misconception:** Flattened OCR text may invert table meaning or detach a caption; extraction quality bounds retrieval quality.
- **Unlocks:** OCR-first baselines for multimodal retrieval.

#### Chapter 43 — Multimodal retrieval and grounding

- **Objective:** Compare text-only, multimodal, and visual-document retrieval on the same labeled tasks.
- **Prerequisites:** Chapters 10–14, 28–33, and 42.
- **Section 1 — Representations and search.** Topic: cross-modal retrieval; micro-concepts: text vs multimodal embeddings, text→image, image→text, image→image, page-image and screenshot retrieval, single-vector vs multi-vector representations, late interaction for visual documents, OCR-first vs OCR-free paths, ColPali/ViDoRe-style examples
- **Section 2 — Evidence across media.** Topic: temporal and visual grounding; micro-concepts: chart/table retrieval, audio segmentation and transcript alignment, video segment retrieval, timecodes, multimodal reranking, page/region/frame provenance and claim grounding
- **Lab:** Compare OCR-BM25, page-image embeddings and a multi-vector visual retriever on pages with tables and figures; report region recall and grounded-answer errors.
- **Visual:** Query and page/image token interactions linked to cited page regions and audio/video time anchors.
- **Trade-off / misconception:** Cross-modal similarity and visual grounding are different tasks; benchmark gains are not universal across document types.
- **Unlocks:** Multimodal case studies and source fusion.

### Module 21 — Code and multi-index retrieval

#### Chapter 44 — Code retrieval and repository evidence

- **Objective:** Find exact symbols and behavioral evidence across a versioned codebase.
- **Prerequisites:** Chapters 05–14, 19–25, and 28–33.
- **Section 1 — Repository structure.** Topic: index units; micro-concepts: files/paths, ASTs, definitions, references, imports, call and inheritance graphs, repository topology, generated files, commit identity, tests as evidence, code-specific chunking
- **Section 2 — Query and expansion.** Topic: hybrid code search; micro-concepts: lexical identifiers, code embeddings, path/symbol filters, graph expansion, function/module context expansion, version constraints, provenance to file/line/commit and evaluation by symbol/behavior task
- **Lab:** Answer a cross-file behavior question from symbol, lexical and dense candidates; cite source and test at a pinned commit.
- **Visual:** Repository graph connecting import, call, definition and test edges to retrieved code spans.
- **Trade-off / misconception:** A semantically similar snippet from another commit can be wrong; generated files may swamp useful results.
- **Unlocks:** Codebase assistant case study and multi-index routing.

#### Chapter 45 — Federated and multi-index retrieval

- **Objective:** Merge evidence from heterogeneous corpora and engines without losing permissions or provenance.
- **Prerequisites:** Chapters 21–26, 30–33, and specialized sources in Chapters 38–44.
- **Section 1 — Source planning.** Topic: federation; micro-concepts: multiple corpora/retrieval engines, source routing, heterogeneous freshness, per-source filters, candidate quotas, source health, timeouts, partial results, failure isolation and permission boundaries
- **Section 2 — Merging.** Topic: comparability; micro-concepts: source-specific scores, score incomparability, calibration vs rank fusion, shard/index score comparability, duplicate entities across sources, source/version provenance, overfetch and final top-k correctness
- **Lab:** Federate two retrievers with different score scales and one timed-out source; compare quota, RRF and calibrated fusion with ACL tests.
- **Visual:** Coordinator fan-out with per-source budgets, partial-result flags and merged provenance.
- **Trade-off / misconception:** Naive global sorting of raw scores can favor one engine and conceal a failed source.
- **Unlocks:** Multi-source architecture and distributed serving.

### Module 22 — Architecture taxonomy

#### Chapter 46 — RAG architecture families and their boundaries

- **Objective:** Classify architectures by retrieval control, source type, and evidence representation rather than slogans.
- **Prerequisites:** Chapters 01–45.
- **Section 1 — Pipeline families.** Topic: control; micro-concepts: naive, advanced/modular, hybrid, multi-query, conversational, parent-child, hierarchical, corrective/CRAG, Self-RAG, adaptive, agentic, multi-hop, long-context + retrieval and memory-augmented systems.
- **Section 2 — Source families.** Topic: knowledge access; micro-concepts: graph/knowledge-graph/GraphRAG-style, SQL, web, multimodal, code, temporal and federated RAG; orthogonal combinations and vendor naming overlap.
- **Lab:** Classify five real or hypothetical systems on independent axes and draw their query paths.
- **Visual:** Matrix of source, control policy, retrieval method, and evidence granularity.
- **Trade-off / misconception:** “Advanced RAG” and “GraphRAG” are not stable, mutually exclusive standards.
- **Unlocks:** Comparing RAG with alternatives and designing task-specific systems.

#### Chapter 47 — RAG versus and alongside related techniques

- **Objective:** Defend a knowledge-access design that may combine retrieval with adaptation, tools, and long context.
- **Prerequisites:** Chapters 04, 29, and 46.
- **Section 1 — Model-side choices.** Topic: alternatives; micro-concepts: fine-tuning, continued pretraining, prompts, long-context input, caching and semantic caching, costs of updating knowledge vs behavior.
- **Section 2 — System-side choices.** Topic: complements; micro-concepts: search without generation, function calling, agents, live web, SQL, knowledge graphs, user memory and their trust boundaries.
- **Lab:** Design two solutions to the same task under different freshness, audit, and latency constraints.
- **Visual:** Decision table with requirements, candidate technique, reason, and failure risk.
- **Trade-off / misconception:** Techniques are often composable; the right choice follows the information need.
- **Unlocks:** Formal evaluation and production architecture defense.

## Part XI — Production evaluation, security, and scale [PRODUCTION]

### Module 23 — Experimentation and trust

#### Chapter 48 — Experiments, ablations, and regression gates

- **Objective:** Test whether a new technique actually improves the intended workload.
- **Prerequisites:** Chapters 09, 25–27, and 30–33.
- **Section 1 — Study design.** Topic: controls; micro-concepts: frozen corpus and qrels, one-variable ablations, paired queries, baselines, sampling, confidence intervals, multiple comparison caution.
- **Section 2 — Deployment evidence.** Topic: gates; micro-concepts: confidence intervals, slice-level quality/latency/cost/security acceptance criteria, canary, online A/B, rollback threshold, corpus/query/language vs retriever drift, offline regression gate → deployment → online monitoring → reviewed new cases, SLIs/SLOs and error-budget intuition. Separate offline judgments from online service metrics; dashboards are implemented in Chapter 52.
- **Lab:** Ablate chunk size, hybrid weight, reranking, and context budget on the same benchmark; build a versioned release-gate report with a canary/rollback rule and one drift investigation.
- **Visual:** Pareto frontier of quality, latency, and cost.
- **Trade-off / misconception:** A benchmark win under one corpus or model is not a universal architecture rule.
- **Unlocks:** Production decisions based on evidence.

#### Chapter 49 — Secure retrieval and untrusted evidence

- **Objective:** Prevent unauthorized retrieval and instruction execution from source content.
- **Prerequisites:** Chapters 04, 21–22, 29, 32, and 41.
- **Section 1 — Access boundaries.** Topic: identity and authorization; micro-concepts: tenant identity, document/row ACL, RBAC and attribute policies, permission-aware prefiltering, tenant-safe query/embedding/semantic cache keys, semantic-cache false matches, deletion and audit logs, least privilege.
- **Section 2 — Adversarial content.** Topic: threats; micro-concepts: indirect prompt injection, poisoned documents, forged citations, tool-output manipulation, PII and secrets, exfiltration paths, source trust tiers, sandboxed tool execution, protected security-event logs and trace redaction.
- **Lab:** Run cross-tenant and malicious-document tests; assert no unauthorized text reaches prompt, log, or cache.
- **Visual:** Trust boundaries around retrievers, tools, context, and model.
- **Trade-off / misconception:** Prompt instructions alone cannot enforce access control.
- **Unlocks:** Secure multi-tenant deployment.

### Module 24 — Ingestion and distributed serving

#### Chapter 50 — Production ingestion and index lifecycle

- **Objective:** Operate parsing, embedding, and indexing as recoverable services.
- **Prerequisites:** Chapters 18–22 and 49.
- **Section 1 — Data plane.** Topic: pipeline; micro-concepts: source connector, queue, worker, batching, retries, dead-letter queue, idempotency, checkpoint, validation, throughput and backpressure.
- **Section 2 — Lifecycle.** Topic: versioned indexes; micro-concepts: CDC, dual-write limits, snapshot + replay, model migration, alias cutover, consistency windows, backup, restore and deletion propagation. Topic: ingestion observability; micro-concepts: correlated change-to-visibility spans, queue depth/lag, parse/OCR/embedding failures, indexing throughput, duplicate rate, reindex progress, freshness lag and deletion delay.
- **Lab:** Simulate duplicate events and worker failure; verify exactly one visible current document version and trace the source change through the queue, parser, embedder and searchable index.
- **Visual:** Queue and worker pipeline with failure and recovery paths.
- **Trade-off / misconception:** “Exactly once” is usually an application-level outcome built from idempotency, not a free queue property.
- **Unlocks:** Distributed serving and scale estimates.

#### Chapter 51 — Retrieval from thousands to billions of vectors

- **Objective:** Plan memory, storage, routing, and latency for several corpus scales.
- **Prerequisites:** Chapters 15–18, 21, 48, and 50.
- **Section 1 — Capacity.** Topic: scale points; micro-concepts: 1k, 100k, 10m and 1b vectors, raw-vector bytes, graph overhead, PQ compression, index build time, RAM/SSD/GPU placement, CPU vs GPU search.
- **Section 2 — Distributed query.** Topic: serving; micro-concepts: partition and shard selection, fan-out, replicas, shard oversampling, distributed top-k correctness, score comparability across shards and indexes, filter locality, multi-tenancy, caching, consistency, correlated shard/merge spans, partial results, p99 tail latency, throughput and recovery.
- **Lab:** Write a capacity and p95 latency budget for 20m documents with ACLs and hourly freshness.
- **Visual:** Coordinator → routed shards → partial top-k → merge → rerank.
- **Trade-off / misconception:** More shards can reduce per-shard work while increasing fan-out and tail latency.
- **Unlocks:** A defensible production reference architecture.

### Module 25 — Reliability and economics

#### Chapter 52 — Reliability, cost, and deployment operations

- **Objective:** Keep the platform within quality, service, and cost targets through change.
- **Prerequisites:** Chapters 30–33 and 48–51.
- **Section 1 — Operations and telemetry implementation.** Topic: service design; micro-concepts: APIs, UI, rate limits, retries, circuit breakers, fallbacks, recovery. Topic: observability; micro-concepts: structured logs vs counters/gauges/histograms vs traces/spans vs quality evaluations vs lifecycle events, trace/context propagation, redaction, sampling/retention, label cardinality, stage histograms, p50/p90/p95/p99 and critical-path/fan-out latency, SLIs/SLOs/SLAs/error budgets, alert thresholds, version manifests, drift, dashboards and incident review. Implement minimal telemetry directly before mapping to current OpenTelemetry, Prometheus/Grafana and RAG tooling documentation.
- **Section 2 — Economics.** Topic: cost ledger; micro-concepts: request tokens/calls, rewrite, search, rerank, generation and verification cost; source parsing/OCR, embeddings, index/storage/network, utilization, cache savings, amortized refresh, per-tenant and per-strategy metering, cost/query and cost/successful task.
- **Lab:** Instrument query and ingest traces, stage metrics, lifecycle/security events and a cost ledger; build a working local or deployable dashboard with latency, quality, freshness, error, cost and security panels; fire an alert, trace one incident to cause, and show recovery. Produce a per-1,000-query cost sheet and runbook with rollback triggers.
- **Visual:** Cost and latency budget alongside service dependencies.
- **Trade-off / misconception:** The cheapest per-query component may increase total cost by lowering cacheability or answer quality.
- **Unlocks:** Capstone build and architecture critique.

## Part XII — Synthesis, ecosystem, and research [PRODUCTION / RESEARCH]

### Module 26 — Applying and comparing systems

#### Chapter 53 — Frameworks, models, and product evaluation

- **Objective:** Translate known concepts into current tools without losing mechanism-level understanding.
- **Prerequisites:** Chapters 01–52.
- **Section 1 — Abstraction mapping.** Topic: frameworks; micro-concepts: custom Python, LangChain, LlamaIndex, Haystack, DSPy, LangGraph; what each abstracts, hides, composes, and costs to operate.
- **Section 2 — Ecosystem due diligence.** Topic: providers and stores; micro-concepts: embedding/reranking/generation model categories, context and language coverage, evaluation on own corpus, privacy, version pinning, portability and migration. Examples may include OpenAI, Anthropic, Google, Cohere, Voyage, Jina AI, BGE, Sentence Transformers and ColBERT-style models; capabilities are time-stamped and checked against official docs in the written chapter.
- **Lab:** Reproduce one hand-built pipeline with a framework and compare intermediate traces and measurements.
- **Visual:** Concept → algorithm → library → service layers.
- **Trade-off / misconception:** Framework convenience does not remove data, evaluation, security, or scaling obligations.
- **Unlocks:** Case-study architecture comparisons.

#### Chapter 54 — Twelve case studies and architecture critiques

- **Objective:** Transfer principles across domains with different evidence and risk profiles.
- **Prerequisites:** Chapters 01–53; [CASE_STUDIES.md](CASE_STUDIES.md) gives the detailed plan.
- **Section 1 — Workload analysis.** Topic: cases; micro-concepts: company docs, customer support, legal, medical/scientific, financial, code, e-commerce, news, multi-tenant enterprise, organizational graph, multimodal PDF and billion-vector search.
- **Section 2 — Design reviews.** Topic: repeated template; micro-concepts: requirements → data → ingestion → chunks/indexes → retrieval/rank/context → generation → metrics → operations → failure probes → alternatives.
- **Lab:** Defend two contrasting architectures and critique a deliberately flawed design.
- **Visual:** Comparable system cards and decision matrix.
- **Trade-off / misconception:** Case-study outcomes are workload-specific and do not establish a universal “best RAG stack.”
- **Unlocks:** Capstone specification and final design defense.

### Module 27 — Research architecture history

#### Chapter 55 — History of retrieval-augmented language models

- **Objective:** Distinguish research architectures that train with retrieval from inference-time application RAG.
- **Prerequisites:** Chapters 01–14, 28–33, and 46–47.
- **Section 1 — Historical chain.** Topic: systems; micro-concepts: classic external search and open-domain QA, learned dense retrieval, REALM, RAG-Sequence/RAG-Token, Fusion-in-Decoder, retrieval-augmented pretraining, RETRO, Atlas and modern inference-time engineering RAG
- **Section 2 — Training and fusion axes.** Topic: architecture; micro-concepts: frozen vs learned vs differentiable retriever, jointly trained retriever/generator, retrieval during pretraining/fine-tuning/inference, retrieve-once vs repeated, passage fusion vs token/chunk retrieval, index update behavior and compute
- **Lab:** Draw an architecture matrix for REALM, RAG, FiD, RETRO and Atlas; identify training signal, retrieval timing and deployment cost.
- **Visual:** Timeline and two-axis matrix: retrieval timing × retriever/generator training coupling.
- **Trade-off / misconception:** A research model with retrieval during pretraining is not automatically an appropriate enterprise application design.
- **Unlocks:** Research-paper interpretation and the final expertise assessment.

### Module 28 — Capstone and research literacy

#### Chapter 56 — Design and build a production RAG platform

- **Objective:** Integrate the complete course into an evaluated, permission-safe, multi-source service.
- **Prerequisites:** Chapters 01–55 and the project milestones.
- **Section 1 — Required platform.** Topic: implementation; micro-concepts: multiple source adapters, parsing/chunking/embeddings, BM25+dense+hybrid, filters/reranking, conversation/query rewriting, multi-hop, web and graph branch, citations, evaluation, caching, APIs/UI, deployment.
- **Section 2 — Engineering defense.** Topic: evidence; micro-concepts: ACL tests, incremental updates/deletions, correlated request and ingest traces, p50/p95/p99 budget, quality/system/economics/security dashboards, SLI/SLO and error-budget report, stage/tenant cost ledger, drift and regression gates, backup/restore, failure injection, ablation, architecture decision records.
- **Lab:** Deliver a working service and dashboard, reproducible benchmark, explicit workload-specific retrieval/generation/latency/reliability/freshness/security/cost gates, threat model, incident runbook, and design review; document any unmet gate.
- **Visual:** Full reference architecture annotated with actual deployed components.
- **Trade-off / misconception:** Feature completion without measured quality and safe operation does not satisfy the capstone.
- **Unlocks:** Research comparison and independent design work.

#### Chapter 57 — Research reading and final expertise test

- **Objective:** Critically read new retrieval work and demonstrate independent judgment across the field.
- **Prerequisites:** Chapters 01–56 and the staged [PAPER_READING_PATH.md](PAPER_READING_PATH.md).
- **Section 1 — Paper literacy.** Topic: critique; micro-concepts: problem formulation, baselines, datasets, relevance labels, ablations, latency/cost, reproducibility, generalization and failure analysis.
- **Section 2 — Expertise assessment.** Topic: tasks; micro-concepts: explain RAG from first principles; calculate BM25, cosine, RRF and NDCG; implement an index; diagnose a trace; design for 100m+ documents; critique a GraphRAG/agentic claim; teach one concept to a novice.
- **Lab:** Submit a paper replication or well-scoped negative result and defend the capstone orally.
- **Visual:** Claim → evidence → limitation map for a research paper.
- **Trade-off / misconception:** A new architecture name or reported benchmark gain is not enough to justify deployment.
- **Unlocks:** Independent research and system leadership.

## Assessment and content continuity

Every written chapter ends with “You understand this chapter if you can…” and observable abilities: explain the mechanism, draw index-time and query-time flow, calculate or implement a small instance, compare alternatives, and diagnose a failure. Separate solution files are written with chapters. Core evaluation in Chapters 30–33 supplies the harness for every later architecture; Chapters 48 and 52 add production experiments, an implemented dashboard, latency, cost, and incident response. Each chapter applies the visual audit and completion checklist; substantive figures retain editable source. The final exam mixes numerical work, code, debugging, design, paper interpretation, architecture critique, and teaching.

## Deep-decomposition checkpoints

| Mechanism | Trace the learner must draw | Counterexample or measurement |
|---|---|---|
| Lexical scoring/execution (07–08) | postings → BM25 upper bounds → pruning → top-k heap | Exact top-k agreement and scored-document count |
| Retriever training (11–12) | positive/negative pairs → objective → mining → distillation → domain test | False negatives and held-out domain/language slices |
| HNSW and IVF/PQ (16–17) | training/insertion → candidate frontier/list probes → approximate scores | Exact-neighbor recall, task relevance recall, latency, bytes |
| Chunking and metadata (20–21) | source layout → boundary → parent mapping → ACL filter → citation span | Recall, duplicate tokens, unauthorized and stale hits |
| Hybrid and ranking (25–27) | source candidates → fusion → trained/cross-encoder rank → selection | Exact SKU vs paraphrase; candidate-depth/cost curve |
| Context and answer (28–29) | selected evidence → packing → claims → citations/abstention | Buried, negative, and conflicting evidence |
| Evaluation (30–33, 48) | qrels → retrieval/context/answer metrics → local failure → controlled experiment | Incomplete qrels, judge bias, benchmark transfer |
| Dynamic retrieval (35–37) | information gap → action → observation → state update → stop | Trigger false positives/negatives, loop and budget exhaustion |
| Graph/web/SQL (38–41) | source semantics → query route → evidence/provenance → answer | False graph edge, stale web page, invalid aggregation |
| Multimodal and code (42–45) | page/region or symbol → candidate → expansion → grounded citation | OCR order error, chart units, wrong commit, partial source |
| Production (49–52) | identity → idempotent update → ingest trace → shard route → answer trace → dashboard/alert → recovery | Tenant leak, stale delete, filtered recall, p95/p99, freshness and cost budget |

## Phase 1.5 audit outcome

This revision preserved the first-principles spine and expanded only overloaded or missing mechanisms. Evaluation now has an early baseline harness before advanced architectures. Lexical query execution, retriever training, learned ranking, benchmark literacy, document intelligence, code and federation, and retrieval-augmented model history have dedicated homes. Temporal retrieval remains anchored in Chapter 22, while hierarchical retrieval remains anchored in Chapters 20 and 28. A separate frontier file holds unstable research claims. Each added method has a simpler baseline and a measurement specified in its lab.

## “Could this be the only resource?” coverage audit

The gate in each row is a **required explanation or artifact** when chapters are written. A heading alone does not pass. These checks drove the new chapters and revisions above.

| Major area | Chapter anchor | Required understanding or artifact |
|---|---|---|
| Classical IR | 05–09 | Explain the evolution from Boolean matching to weighted lexical ranking and judged top-k retrieval. |
| Lexical search | 05–08 | Build postings and BM25, then safely prune scoring with the same top-k result. |
| Dense retrieval | 10–14 | Derive similarity, explain encoder training, compare exact dense retrieval with BM25 and sparse/late-interaction alternatives. |
| Retriever training | 11–12 | Inspect positives, negatives, objective, mining, distillation and held-out domain/language failures. |
| ANN | 15–18 | Use exact KNN as oracle; trace IVF/PQ/HNSW search, bytes, build/update and recall/latency trade-offs. |
| Vector databases | 18, 21 | Distinguish index, library and service; test filtered recall, durability, deletion and multi-tenant behavior. |
| Ingestion | 19, 22, 50 | Preserve source lineage and layout; replay update/delete events and measure staleness. |
| Chunking | 20 | Compare boundaries, overlap, child/parent mapping and citation spans on judged questions. |
| Metadata | 21–22 | Treat ACL/time/version as eligibility; demonstrate prefilter vs postfilter behavior. |
| Query processing | 23–24 | Preserve original intent through routing, rewriting, expansion, decomposition and fallback. |
| Hybrid retrieval | 25 | Hand-calculate fusion and test exact-ID vs paraphrase slices. |
| Reranking / LTR | 26–27 | Compare heuristics, learned features, cross-encoders and LLM ranking under candidate-depth and latency budgets. |
| Context engineering | 28 | Account for tokens, order, compression, redundancy, dynamic top-k and evidence provenance. |
| Grounded generation | 29 | Label atomic claims, contradictory evidence, citation support, answerability and abstention. |
| Core evaluation | 09, 30–33 | Build qrels and a harness separating retrieval, context, answer and benchmark-transfer questions before advanced RAG. |
| Debugging | 32, 48 | Find the first failing stage with a trace; later connect regression, drift and incident diagnosis. |
| Conversational RAG | 34 | Resolve follow-up references without treating session memory as a trusted corpus. |
| Multi-hop | 35 | Trace each evidence hop and compare hop recall with final-answer accuracy. |
| Adaptive retrieval | 36 | Calibrate retrieve/skip/retry triggers and count false triggers and cost. |
| Agentic RAG | 37 | Specify state, action, observation, guardrails, budgets, stop and replay for a dynamic policy. |
| GraphRAG | 38–39 | Build a cited path and compare graph neighborhoods with community summaries on local/global questions. |
| Structured retrieval | 41 | Run validated read-only SQL/graph/API queries with exact permissions and numeric checks. |
| Web retrieval | 40 | Separate event/publication/fetch dates, credibility, duplication and conflicting claims. |
| Document and multimodal RAG | 42–43 | Compare OCR/layout, page image and multi-vector retrieval with coordinate/time grounding. |
| Code retrieval | 44 | Follow symbols, calls, tests and commit identity across files. |
| Federated retrieval | 45 | Handle score scales, quotas, partial results, duplicate entities and source-specific ACLs. |
| Security | 21, 41, 49 | Test unauthorized evidence and indirect instructions at source, retrieval, cache, tool and output boundaries. |
| Distributed serving | 18, 51 | Budget shard overfetch, merged top-k correctness, filtered recall and p95 tail latency. |
| Cost engineering | 36–37, 44, 52 | Quantify query fan-out, step/token budgets, indexing, reranking, generation and caching. |
| Retrieval-augmented model research | 55 | Compare REALM, RAG, FiD, RETRO and Atlas by retriever training, fusion and retrieval timing. |
| Research-paper literacy | 33, 55–57 | Produce a paper card with task, baseline, metric, result, ablation, limitation and replication proposal. |
