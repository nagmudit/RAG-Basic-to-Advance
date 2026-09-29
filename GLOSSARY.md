# Terminology register (Phase 1.6)

The glossary will grow with chapter writing. Each future entry will include: **preferred term**, plain-language definition, formal definition or formula if useful, first teaching chapter, related/contrasted terms, implementation examples, and naming caveats. This initial register fixes high-risk distinctions and assigns the remaining terms to families.

| Preferred term | Initial meaning | First chapter | Distinguish from |
|---|---|---|---|
| Information need | The underlying fact or task a user wants resolved | 01 | Literal query text |
| Query | The words or structured request sent to a system to express an information need | 01 | The full underlying need |
| Model parameters / parametric memory | Learned numerical weights that encode behavior and some knowledge between model updates | 01; deep treatment 04, 55 | Current prompt context or external records |
| Prompt context | Material supplied to the model for a particular request | 01; deep treatment 28–29 | Fixed model parameters |
| External source | Record outside model parameters and current prompt that an application can access | 01 | Verified evidence selected from it |
| Corpus | The collection eligible for a particular search task or snapshot | 01; deep treatment 02 | A retrieved candidate set |
| Document | Source record with stable identity and version | 01; deep treatment 02, 19 | Chunk or model context |
| Chunk / passage | Searchable span derived from a document | 01; deep treatment 02, 20 | Whole document |
| Candidate | Item returned for further selection | 01; deep treatment 02 | Verified evidence |
| Evidence | Authorized source content used to support a claim | 01 | Mere topical relevance |
| Grounding | Relating generated claims to supplied evidence | 01; deep treatment 29 | Guaranteed correctness |
| Provenance | Trace from answer claim to source, version, and span | 01 | Citation text alone |
| Citation | Pointer from an answer claim to a source version and supporting location | 01 | Proof that the cited source is correct |
| Abstention | Declining to assert a claim when eligible evidence is insufficient | 01; deep treatment 29 | Uninformative refusal |
| Answerability | Whether an information need can be resolved from the available eligible evidence under the task constraints | 01; deep treatment 31 | Model willingness to respond |
| Eligibility | Whether a source may enter search or context for a request under scope, time and authorization rules | 01; deep treatment 21, 49 | Relevance score |
| Source snapshot | Identified version of the material searchable for a request | 01; deep treatment 22 | The newest source anywhere |
| Unsupported claim | Answer statement that the supplied eligible evidence does not establish | 01; deep treatment 29, 31 | Necessarily false statement |
| Hallucination | Broad term for generated content presented as fact without adequate support; diagnose the narrower failure when possible | 01 | Every factual error or source error |
| Retrieval | Finding eligible candidates from a corpus | 01; implementation 02 | Reranking or generation |
| Index time / preparation time | Work done to prepare searchable source representations before a particular question | 02; deep treatment 05, 19 | Query-time work |
| Query time | Work done for a particular question using prepared sources | 02 | Index-time preparation |
| List / array | Ordered collection whose position can be accessed directly; searching unknown content may still require a scan | 03 | Map keyed by known identity |
| Map / dictionary | Key-to-value structure for lookup by a supplied key | 03 | Content search from an information need |
| Set | Collection of distinct values supporting membership and overlap operations | 03; first used 02 | Ordered list with repetitions |
| Hash lookup | Finding a value using a computed key hash; expected fast lookup depends on collision behavior | 03 | Worst-case guarantee or relevance retrieval |
| Binary search | Repeatedly halving a sorted key range to find an exact key | 03 | Hash lookup or unsorted content search |
| Time complexity / Big O | Bound on how operation count grows with a named input size under stated assumptions | 03 | Measured seconds or latency SLO |
| Average case / worst case | Expected work under a stated input distribution versus an upper bound for allowed inputs | 03 | Typical latency versus p99 without a workload |
| Build cost / amortization | One-time preparation work spread across a declared number of later operations | 03 | A cost that disappears entirely |
| Shallow container bytes | Memory size of the container object itself, excluding objects it references | 03 | Total resident or serialized bytes |
| Code point / UTF-8 byte | Abstract Unicode character value versus encoded storage unit | 03 | Visible glyph or model token |
| Model token | Unit emitted by a particular language-model tokenizer | 03; deep treatment 04 | V0 regex term, whitespace word or character proxy |
| Prompt | Model-facing input assembled from instructions, question and supplied data for one request | 04; V0 construction 02 | Model weights or source corpus itself |
| Autoregressive generation | Producing a sequence by conditioning each next-token prediction on visible input and earlier output | 04 | Evidence retrieval or verification |
| Next-token distribution | Model-assigned conditional probabilities over possible next tokens at one generation step | 04 | Probability that the final claim is true |
| Decoding rule | Procedure choosing an output token from the next-token distribution, such as greedy choice or sampling | 04 | Source relevance or factual support |
| Attention / query-key-value | Learned operation that weights visible token representations using query-key compatibility and combines values | 04 | Passage authority, citation or explanation of truth |
| Causal mask | Constraint preventing an autoregressive output position from reading later output tokens | 04 | Source access-control filter |
| Context window | Model-specific token capacity available to an inference step under its input/output accounting | 04 | Guarantee that every supplied fact is used |
| Context position effect | Change in model behavior associated with where otherwise fixed evidence appears in the input | 04 | Universal rule that middle evidence fails |
| Context distraction / contradiction | Irrelevant or opposing excerpts that can interfere with use of required evidence | 04; deep treatment 28–29 | Proof that a longer input is always worse |
| Prompt truncation | Omission of input caused by a capacity policy or limit | 04 | Retrieval failure when a candidate was already found |
| Trusted instruction / untrusted source data | Application-authorized direction versus external content supplied for inspection | 04; deep security 49 | Text that merely looks like a high-priority role label |
| Indirect prompt injection | Attempt to redirect model behavior using instructions embedded in retrieved or other lower-trust material | 04; deep treatment 49 | Ordinary quotation of an instruction as data |
| Claim-level support check | Review of each answer assertion against eligible source spans, versions and valid derivations | 04; deep treatment 29–31 | Presence of a citation string |
| In-context example | Example in the request input used to elicit a behavior without updating model weights | 04 | Source establishing a current private fact |
| Fine-tuning / continued pretraining | Updating model weights on task examples or broader domain text respectively | 04; deep treatment 12, 55 | Per-request retrieval of current evidence |
| Tool call | Invocation of an external function or source during a request | 04; deep treatment 37, 41 | Automatically agentic behavior or verified result |
| Workload | Defined distribution of operations, inputs, hit/miss mix and volume under test | 03 | Corpus size alone |
| Benchmark | Reproducible timed comparison with a declared task, implementation, environment and workload | 03 | Universal performance claim |
| Mean / median | Arithmetic average versus middle value of sorted observations | 03 | Tail percentile |
| Percentile estimator | Declared rule mapping a sample and probability to a quantile, such as nearest rank | 03; deep treatment 52 | A unique answer for very small samples |
| Uncertainty | Limits on what a finite, variable sample can establish about another workload or population | 03; deep treatment 48 | Mere rounding error |
| Training / validation / test split | Data partitions for fitting, choosing and finally estimating generalization | 03; deep treatment 12, 48 | Reusing one set for all decisions |
| Data leakage | Evaluation information entering model fitting or design choices and biasing the reported result | 03; deep treatment 12 | Legitimate use of known corpus at inference |
| Vector / norm / dot product | Ordered numeric coordinates, their magnitude and pairwise product sum | 03; deep treatment 10 | Evidence authority or access right |
| Cosine similarity | Dot product divided by nonzero vector norms, measuring geometric angle alignment | 03; deep treatment 10 | Calibrated answer correctness |
| Logarithm | Exponent needed to obtain a positive value from a chosen base; e.g., `log₂ 1024 = 10` | 03; deep treatment 06 | Defined operation at zero |
| Probability / distribution | Likelihood under a stated model and spread of outcomes across its population | 03; deep treatment 09, 48 | Raw retrieval score or one sample mean |
| Source locator | Document ID, version, section/span and where needed offset that identify cited source text | 02 | Citation text without a resolvable source |
| Segment / window | V0 searchable word span derived from one named document section | 02; deep treatment 20 | Whole source document |
| Tokenization | Converting text into matching units under explicit rules | 02; deep treatment 05 | Model-token counting or semantic understanding |
| Term | Unit compared by a lexical retrieval rule after tokenization/normalization | 02; deep treatment 05 | Original word or model token |
| Analyzer | Versioned rule sequence mapping document fields and queries to searchable terms | 05 | A model tokenizer or a harmless generic text cleaner |
| Unicode NFC / NFKC | Canonical composition versus compatibility composition after decomposition; NFKC may merge additional distinctions | 05 | Case folding, tokenization or proof that two identifiers are equivalent |
| Vocabulary | Distinct indexed terms produced by a specified analyzer on a specified snapshot | 05 | Every surface word or every possible query |
| Posting / posting list | One term's segment entry, optionally with field frequencies and positions / its ordered entries | 05 | The original source text or eligible result set |
| Positional index | Inverted index retaining term offsets within each indexed field | 05 | Original byte offsets or cross-field phrase matching |
| Boolean retrieval | Set combination of term matches using AND, OR and anchored NOT under eligibility | 05 | Ranked relevance or evidence verification |
| Phrase query | Match requiring analyzed terms at consecutive positions in one field | 05 | Exact character substring or arbitrary semantic paraphrase |
| Forward index / stored fields | Segment-ID lookup for original text, fields, version, locator and metadata | 05 | Term-to-postings lookup or reconstruction from terms |
| Analyzed field length | Count of emitted terms in one indexed field under its analyzer version | 05 | Source bytes, whitespace words or model tokens |
| Term frequency / segment frequency | Occurrence count of a term in a field or segment / count of indexed segments containing it | 05; weighting 06 | Relevance probability or count of distinct source documents when segments are indexed |
| Stop word / stem / lemma | Optional removal of selected common terms / rule-derived root / linguistically derived base form | 05 | Universally safe normalization; each can change match meaning |
| N-gram / fuzzy match | Contiguous sequence of n terms or characters / bounded approximate matching under a declared rule | 05; advanced query use 23 | Exact identifier equality or guaranteed typo correction |
| Literal term overlap | Number of distinct query terms shared with a candidate under V0's tokenizer | 02 | Calibrated relevance probability |
| Top-k | Retaining the k highest-scored candidates under a stated sorting and tie rule | 02; deep treatment 08 | Proof that those k suffice as evidence |
| Deterministic tie break | Fixed secondary sort rule used when primary scores are equal | 02 | A new relevance signal |
| Context construction | Selecting and labeling excerpts to supply to an answer process | 02; deep treatment 28 | Candidate retrieval itself |
| Context budget | Limit on material placed into the request context, measured in a stated unit | 02; deep treatment 28 | True model token limit when only words are counted |
| Stub generator | Small deterministic task-specific answer function used to expose a pipeline boundary | 02 | General language model or semantic verifier |
| No-result detection | Recognizing that a retrieval rule returned no candidates under the current query, scope and corpus | 02; deep treatment 23, 36 | Proof that no answer exists |
| Ranking | Ordering candidates by a score and tie rule | 02; deep treatment 06, 27 | Candidate generation or evidence verification |
| Reranking | Reordering a preselected candidate set, often with a stronger model | 26 | First-stage retrieval |
| Dynamic pruning | Safely skipping candidate scoring using upper score bounds during top-k search | 08 | Approximate index search |
| Inverted index | Analyzer-versioned term-to-postings lookup structure over a declared source snapshot | 05 | Forward store, vector index or access grant |
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
