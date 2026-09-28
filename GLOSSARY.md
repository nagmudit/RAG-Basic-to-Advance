# Terminology register (Phase 1.6)

The glossary will grow with chapter writing. Each future entry will include: **preferred term**, plain-language definition, formal definition or formula if useful, first teaching chapter, related/contrasted terms, implementation examples, and naming caveats. This initial register fixes high-risk distinctions and assigns the remaining terms to families.

| Preferred term | Initial meaning | First chapter | Distinguish from |
|---|---|---|---|
| Information need | The underlying fact or task a user wants resolved | 01 | Literal query text |
| Corpus | The collection eligible for search | 02 | A retrieved candidate set |
| Document | Source record with stable identity and version | 02 | Chunk or model context |
| Chunk / passage | Searchable span derived from a document | 02; deep treatment 20 | Whole document |
| Candidate | Item returned for further selection | 02 | Verified evidence |
| Evidence | Authorized source content used to support a claim | 01 | Mere topical relevance |
| Grounding | Relating generated claims to supplied evidence | 01; deep treatment 29 | Guaranteed correctness |
| Provenance | Trace from answer claim to source, version, and span | 01 | Citation text alone |
| Retrieval | Finding eligible candidates from a corpus | 02 | Reranking or generation |
| Ranking | Ordering candidates by a relevance function | 06 | Candidate generation |
| Reranking | Reordering a preselected candidate set, often with a stronger model | 26 | First-stage retrieval |
| Dynamic pruning | Safely skipping candidate scoring using upper score bounds during top-k search | 08 | Approximate index search |
| Inverted index | Term-to-postings lookup structure | 05 | Vector index |
| Embedding | Learned numeric representation of an input | 11 | Any vector |
| Retriever adaptation | Updating a retriever using domain examples while testing generalization | 12 | Choosing a pretrained encoder unchanged |
| Hard negative | Nonrelevant candidate difficult for a retriever to distinguish from a positive | 12 | False negative, which is actually relevant |
| Vector index | Data structure for vector similarity lookup | 15 | Vector database/service |
| Exact KNN | Top-k closest items under a chosen metric, found without approximation | 10 | ANN |
| ANN | Search that trades exact-neighbor recall for speed, memory, or I/O | 15 | Relevance ranking quality |
| Hybrid retrieval | Combining more than one retrieval signal, often lexical and dense | 25 | A specific fusion formula |
| RRF | Reciprocal rank fusion, combining ranks rather than raw scores | 25 | Weighted score sum |
| Learning to rank | Estimating ranking order from labeled query-candidate examples and features | 27 | Hand-tuned heuristic or candidate retrieval |
| ACL | Access-control list or equivalent document eligibility policy | 21 | A soft relevance signal |
| Qrels | Query-to-item relevance judgments | 09 | Generated answers |
| Context recall | Share of answer-required evidence represented in the supplied context | 30 | Candidate retrieval recall |
| Faithfulness | Degree to which answer claims are supported by supplied evidence | 29 | Factual correctness in the world |
| Freshness | Whether an index/answer reflects the required time and version | 22 | Mere recency preference |
| Adaptive retrieval | Policy that changes whether or how to retrieve based on estimated need/evidence | 36 | Fixed retrieve-always pipeline |
| Agentic retrieval | A bounded policy that observes evidence and chooses subsequent actions dynamically | 37 | Fixed multi-step tool chain |
| Document intelligence | Extracting and indexing layout and structure from document pages | 42 | OCR text alone |
| Federated retrieval | Coordinating retrieval across distinct corpora or engines | 45 | Sharding one homogeneous index |
| Telemetry | Recorded signals about a system's execution and state | 02; deep treatment 52 | Quality judgment alone |
| Observability | Ability to infer behavior and failure causes from emitted evidence | 32; deep treatment 52 | A dashboard screenshot |
| Structured log | Searchable discrete diagnostic record with named fields and correlation ID | 02; deep treatment 52 | Aggregated metric |
| Metric | Aggregated numeric measurement over a defined interval and labels | 09; deep treatment 52 | One request log or judged case |
| Trace | Causally linked record of one request or ingest operation | 02; deep treatment 32, 52 | Aggregate metric |
| Span | Timed operation within a trace with parent/link, attributes and status | 32; deep treatment 52 | Whole trace |
| Event | Durable named state transition, such as a delete or index cutover | 22; deep treatment 50 | Routine diagnostic log |
| SLI | Service-level indicator: a defined measured reliability quantity | 48; deep treatment 52 | Its target, the SLO |
| SLO | Service-level objective: target for an SLI over a window | 48; deep treatment 52 | Contractual SLA |
| SLA | Service-level agreement: external service commitment and consequences | 52 | Internal SLO |
| Error budget | Allowed number or fraction of SLO misses within its window | 48; deep treatment 52 | Error count without denominator |
| Drift | Sustained change in data, query mix, system behavior or quality relative to a specified baseline | 48 | Sampling noise or a single regression |
| p50 / p95 / p99 | 50th/95th/99th percentile of a declared latency sample and window | 09; deep treatment 52 | Mean latency or sum of stage percentiles |
| Tail latency | Slow end of a latency distribution, often examined at p95 or p99 | 48; deep treatment 52 | Typical request latency |
| Metric cardinality | Number of distinct label combinations in a time series family | 52 | Number of requests |
| Sampling | Selection of a subset of traces, requests or judgments under a stated rule | 30; deep treatment 48, 52 | Random missing data with unknown bias |
| Cost ledger | Versioned record and allocation of request, ingestion, storage and network cost | 52 | Token count alone |

## Taxonomy for future entries

- **Data and lifecycle (02, 19–22, 42, 50):** source, connector, canonical record, checksum, parser, OCR, layout, duplicate, lineage, version, tombstone, CDC, idempotency, backfill, licensing, retention, migration.
- **Lexical IR and execution (05–09):** analyzer, posting, position, TF, DF, IDF, TF-IDF, BM25, BM25F, Boolean query, gap encoding, skip data, term-at-a-time, document-at-a-time, MaxScore, WAND, Block-Max WAND.
- **Geometry and retriever learning (10–14):** norm, dot product, cosine, dense/sparse, dual encoder, InfoNCE, in-batch/hard/false negatives, mining, distillation, domain shift, SPLADE, MaxSim, ColBERT.
- **ANN and storage (15–18):** KNN, exact-neighbor recall, KD-tree, LSH, IVF, `nlist`, `nprobe`, PQ, HNSW, `M`, `efConstruction`, `efSearch`, DiskANN, shard, replica.
- **Query, ranking and evidence (23–29):** intent, route, rewrite, HyDE, fusion, RRF, learning to rank, LambdaMART, cross-encoder, MMR, dynamic top-k, threshold calibration, context packing, abstention, citation span.
- **Core evaluation (30–33):** qrels, retrieval/context recall, context precision, answer correctness, faithfulness, citation support, benchmark transfer, LLM-as-judge and failure localization.
- **Specialized retrieval (34–47):** dialogue state, multi-hop, adaptive/active/corrective, Self-RAG, agentic policy, graph/community, web, SQL, document layout, multimodal embedding, code symbol graph, federation.
- **Production and research (48–57):** p95/SLO, corpus/retriever drift, prompt injection, poisoning, cross-tenant leak, tenant-safe/semantic caches, distributed top-k, cost per query, REALM, FiD, RETRO, Atlas.
- **Telemetry and operations (02, 09, 30–32, 48, 50–52):** correlation/trace/span ID, event, counter, gauge, histogram, log level, redaction, label cardinality, trace sampling, critical path, SLI/SLO/SLA, error budget, cost ledger, alert and incident.

## Naming notes

“RAG” is used broadly here for retrieving external knowledge to inform generation, while the original 2020 RAG paper describes particular model architectures. “GraphRAG” can mean any graph-enabled retrieval system or a named implementation with community summaries; chapters will say which. “Contextual retrieval,” “late chunking,” “adaptive RAG,” and “agentic RAG” overlap, so mechanism and source are always stated. “Recall” is qualified as relevance recall, context recall, or exact-neighbor ANN recall, each with its own denominator. “Confidence” specifies whose estimate it is: retriever score, trigger probability, answer confidence, or calibrated correctness. “Memory” identifies session state, durable user preference, model weights, or external corpus explicitly.
