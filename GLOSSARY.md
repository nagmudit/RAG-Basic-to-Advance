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
| Vector dimension / coordinate schema | Number and ordered meaning of numeric features shared by query and indexed items; a matching dimension alone does not prove the same schema or encoder version | 10 | Searchable source text or an interchangeable embedding model |
| Dense vector / binary lexical vector | Explicit coordinate array, including zero positions / Chapter 10's one-or-zero term-presence array over a frozen vocabulary | 10 | Learned semantic embedding; “dense” does not mean semantically trained |
| Unit vector / L2 normalization | Nonzero vector divided by its Euclidean norm, producing magnitude one | 10 | Zero-vector operation or proof of semantic relevance |
| Inner product / dot similarity | Sum of corresponding coordinate products; for nonzero vectors equals product of norms times cosine and therefore may use magnitude | 10 | Cosine unless both sides have unit norm |
| Euclidean / L2 distance | Square root of sum of squared coordinate differences; lower means closer in the declared coordinate system | 10 | Cosine order for unnormalized vectors |
| Manhattan / L1 distance | Sum of absolute coordinate differences; lower means closer under coordinate-wise deviations | 10 | Euclidean or angular distance |
| Exact vector KNN / oracle | Scoring every eligible vector under one fixed metric, schema, snapshot and tie rule to return the true top-k by that score | 10 | Judged relevance, evidence correctness or later approximate ANN results |
| Anisotropy (vector population) | Uneven spread of representation vectors across directions; a geometric property to inspect on a specified population | 10 | A universal failure diagnosis from a two-dimensional drawing |
| Zero-vector cosine policy | Explicit handling of a query or item with zero norm, for which cosine has no defined value | 10 | Automatically assigning similarity zero or declaring the information need unanswerable |
| Text encoder / embedding model | Versioned tokenizer, weights, input format, pooling and normalization that map text to fixed-coordinate representations | 11 | A relevance judge, answer generator or vector metric alone |
| Contextual token vector | Representation of a token position conditioned on surrounding visible tokens in the encoded sequence | 04; retrieval application 11 | A fixed word lookup or whole-passage embedding |
| Pooling / masked mean pooling | Reduction of token vectors to one sequence vector; masked mean averages only nonpadding positions | 11 | Averaging padding or retaining every token vector for late interaction |
| Sentence / passage embedding | Fixed-size vector for one declared text span and encoder contract, used as a retrieval representation | 11 | The original source, proof of semantics or citation locator |
| Bi-encoder / dual encoder | Query and passage are encoded independently (with shared or separate weights) and compared by a vector score | 11 | Cross-encoder pairwise attention or guaranteed relevance |
| Cross-encoder | Model that jointly reads a query and candidate passage to score their pair; Chapter 26 treats its ranking use | 11; deep treatment 26 | One reusable query-independent passage vector |
| Query/document instruction or prefix | Model-specified text/task marker or route applied separately to question and passage inputs | 11 | Arbitrary prompt text safe to add to an existing index |
| Contrastive in-batch objective / InfoNCE intuition | Row-softmax loss favoring a declared positive query–passage pair over other batch passages under a score and temperature | 11; training depth 12 | Calibrated relevance probability or guarantee that other passages are irrelevant |
| Positive / in-batch negative / false negative | Declared relevant training passage / another batch passage assumed irrelevant / an assumed negative that is actually relevant | 11; deep treatment 12 | Complete human qrels or a trustworthy hard negative by default |
| Hard negative | A close or superficially plausible nonrelevant candidate used to teach a finer ranking boundary after its label is checked | 11; mining depth 12 | Any top result, partial evidence or automatically safe negative |
| Contrastive temperature | Positive scale `τ` dividing pair scores before batch softmax, changing sharpness and gradients | 11 | A relevance threshold or answer confidence |
| Matryoshka embedding prefix | First `m` coordinates of a model explicitly trained/evaluated for useful nested prefixes | 11 | Arbitrarily truncating an unrelated embedding model |
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
| Term frequency (TF) / document frequency (DF) | TF counts occurrences in one indexed unit or field; DF counts eligible indexed units containing a term, which are segments in V1 | 05; formal weighting 06 | Relevance probability or distinct source-document count when segments are indexed |
| Inverse document frequency (IDF) | Corpus-level rarity weight; V1 uses `ln(N/df)` for a term present in at least one eligible segment | 06 | A universal or calibrated relevance probability; smoothing conventions differ |
| TF-IDF | Family of lexical weights combining a declared TF transformation and IDF, with optional query/field/length choices | 06 | One universal ranking formula or semantic similarity |
| Sublinear term-frequency weight | Diminishing repetition weight such as `1+ln(tf)` for positive integer field counts | 06 | Bounded BM25 saturation or raw occurrence count |
| Sparse term vector | Vocabulary-coordinate vector with mostly zero weights; classical lexical weights are zero for absent terms, while learned sparse expansion may activate an absent term | 06; extension 14 | Learned dense embedding, original word sequence, or a guarantee of literal presence |
| Learned sparse retrieval / SPLADE-style representation | A trained encoder assigns a small number of nonzero vocabulary-coordinate weights to a query or passage, possibly including terms absent from its surface text | 14 | BM25 weights or a hand-authored synonym map; Chapter 14's fixture is illustrative, not trained |
| Vocabulary expansion coordinate | Positive sparse weight for a vocabulary term not literally present in the encoded text | 14 | Proof that the added term is relevant or licensed source text |
| Weighted posting | Term-to-passage entry carrying a sparse model's positive document weight for weighted-overlap scoring | 14 | BM25 term frequency or an access permission |
| Sparse FLOPS regularizer | Training penalty on squared mean coordinate weights/activations that discourages costly broad posting use | 14 | Measured floating-point operations or a latency guarantee |
| Late interaction | Query and passage encoded independently into multiple token vectors, then compared by a lightweight token-level operator at ranking time | 14 | Joint query–document cross-attention or one pooled vector |
| MaxSim | Sum over query tokens of their maximum similarity to any stored document token vector | 14 | One-to-one alignment, fact verification or calibrated relevance probability |
| Token-vector index | Store and optional candidate-search structure for passage token vectors with passage ID and version mapping | 14 | A single-vector index or the original citeable source span |
| Vector norm / cosine normalization | Euclidean magnitude of all weighted coordinates / dot product divided by nonzero query and document norms | 03; lexical application 06 | Document word count, relevance probability or source authority |
| Scope-local corpus statistic | `N`, `df` or norm calculated over the declared eligible search population | 06 | Authentication or a statistic safe to reuse across changing tenants/policies |
| BM25 | Lexical ranking family that combines query-term IDF with saturating term frequency and adjustable segment-length normalization; this book's Chapter 7 formula uses `idf_B=ln(1+(N−df+.5)/(df+.5))` | 07 | Calibrated probability of relevance, answer confidence, or top-k execution algorithm |
| Robertson–Sparck Jones IDF | Probabilistic no-feedback rarity approximation `ln((N−df+.5)/(df+.5))`, which may be negative for common terms | 07 | The nonnegative `log1p` IDF convention chosen for V2 |
| BM25 term saturation / `k1` | Diminishing gain from repeated matched terms; positive `k1` sets the curve and its limiting factor `1+k1` at average length | 07 | Raw or unbounded logarithmic TF; a maximum allowed occurrence count |
| BM25 length normalization / `b` | Adjustment through `1−b+b L_d/avgdl` for analyzed segment length relative to eligible-scope average; `0≤b≤1` | 07 | Cosine vector norm, context token budget, or a guarantee long text is irrelevant |
| BM25+ | BM25-family variant adding a positive lower-bound offset to a **matched** term's contribution to mitigate excessive long-document penalty | 07 | Adding evidence for an absent query term |
| BM25F / fielded BM25 | Field-aware BM25 family combining weighted fields with separate field-length treatment | 07 | Multiplying a title count in a single combined field |
| Query-likelihood retrieval model | Ranking by an estimated probability of generating query terms from each document language model, usually with collection smoothing | 07 | Calibrated probability that a document answers the user's information need |
| Smoothing (lexical language model) | Mixing document and collection term evidence so absent terms need not have zero estimated query probability | 07 | BM25 term saturation or relaxed authorization |
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
| Gap / delta encoding | Writing a sorted posting list as positive differences between successive document IDs | 08 | A query-time score or document-length normalization |
| Variable-byte code | Integer byte encoding using seven payload bits and a continuation/end convention; Chapter 8 uses high bit 1 on the final byte | 08 | A universal posting codec or compression of positions by itself |
| Skip data | Posting-list jump targets that let a cursor bypass entries when the query plan proves they cannot be needed | 05; deep treatment 08 | Dropping relevance evidence without a proof |
| Term-at-a-time (TAAT) | Visiting all postings for one query term before the next and accumulating document scores | 08 | Document-at-a-time cursor merging |
| Document-at-a-time (DAAT) | Moving term cursors in document-ID order and completing each candidate score at their meeting point | 08 | Scoring every corpus document |
| Top-k heap threshold | Score of the weakest retained result once a size-k heap is full; ties require the declared rank rule | 08 | A calibrated relevance or answerability threshold |
| Term impact / upper bound | A term's score contribution and a safe maximum over the declared eligible snapshot and scoring version | 08 | An arbitrary historical maximum valid after all updates |
| MaxScore | Exact top-k plan that distinguishes essential from nonessential term lists using remaining score bounds | 08 | A BM25 variant or LLM confidence score |
| WAND | Pivot-based posting-cursor plan that uses term-score upper bounds to avoid scoring provably losing candidates | 08 | Every possible WAND efficiency/effectiveness setting being exact |
| Block-Max WAND | WAND-style execution with tighter upper bounds for document-ID blocks | 08 | The global-bound toy searcher implemented in V2 |
| Impact ordering | Organizing postings by possible score contribution to encounter strong candidates early | 08 | Proof that a fixed posting budget returns exact top-k |
| Immutable index segment | Read-only indexed batch whose postings may later be rewritten by a background merge | 08 | An unchanging source corpus or permanent local document IDs |
| Inverted index | Analyzer-versioned term-to-postings lookup structure over a declared source snapshot | 05 | Forward store, vector index or access grant |
| Embedding | Learned numeric representation of an input | 11 | Any vector |
| Retriever adaptation | Updating a retriever using domain examples while testing generalization | 12 | Choosing a pretrained encoder unchanged |
| Embedding/index contract | Declared source, text formatting, encoder roles and revision, pooling, dimension, normalization, metric and ID mapping required for compatible search | 11; operational form 13 | A checkpoint name or vector dimension alone |
| Materialized dense index | Persisted vector rows plus an ordered ID/scope map and checked manifest for later similarity search | 13 | A judged evidence set or ANN by default |
| Batch encoding throughput | Indexed texts encoded per second under declared corpus, batch size, model, device and timing boundary | 13 | Single-query search latency or universal hardware capacity |
| Query encoding latency | Time to map one question to a vector under a declared model/input contract | 13 | Vector scan time or end-to-end answer latency |
| Exact dense scan | Scoring every eligible stored vector under a declared metric before deterministic top-k selection | 10; materialized form 13 | ANN, human relevance or permission grant |
| Index manifest / payload checksum | Versioned description of vector rows and their source/model contract / digest detecting changed stored bytes | 13 | Live authorization or semantic correctness of the model |
| Exact-neighbor parity | Agreement of ordered nearest-neighbor IDs under the same representation, metric, scope and tie rule | 13 | Agreement with human qrels or answer faithfulness |
| Hard negative | Nonrelevant candidate difficult for a retriever to distinguish from a positive | 12 | False negative, which is actually relevant |
| Positive pair / explicit negative | Query–passage pair reviewed as useful / reviewed as unsuitable for that query | 12 | A passage's universal relevance or an access grant |
| In-batch negative | Another training query's positive passage provisionally used as a negative for this query | 12 | A verified negative; duplicates and alternate answers can invalidate it |
| Mined negative | Candidate supplied by a retriever or teacher for negative review and possible training | 12 | Guaranteed irrelevance because it ranked highly |
| False negative | Useful or partially useful passage wrongly labeled as a training negative | 12 | A hard but genuinely irrelevant candidate |
| Weak supervision / synthetic query | Imperfect proxy label / generated question paired with a passage under a declared origin and review rule | 12 | Human-judged relevance or proof that other passages do not answer |
| Contrastive row-softmax / InfoNCE | Training objective raising positive score relative to declared row candidates at a temperature | 11; deep treatment 12 | Calibrated live relevance or answer probability |
| Temperature (retriever loss) | Positive divisor of training logits that changes softmax sharpness and gradients | 11; deep treatment 12 | A relevance threshold or model certainty |
| Triplet margin loss | Hinge penalty when a positive fails to beat a negative by a chosen score margin | 12 | A corpus-wide ranking metric |
| Hard-negative mining | Retrieving high-scoring candidate mistakes, verifying labels, and adding them to training | 12 | Automatically labeling all top nonpositives irrelevant |
| Score / ranking distillation | Teaching a student from teacher score relationships / candidate order preferences | 12 | Ground-truth relevance or teacher authorization |
| Query-side adapter | Trainable transformation of query embeddings while base query encoder and passage encoder remain frozen | 12 | Full transformer or two-tower fine-tuning |
| Domain adaptation / over-specialization | Updating representations for a target distribution / fitting sampled pairs while losing held-out behavior | 12 | Guaranteed improvement from lower training loss |
| Source-disjoint split | Training, validation and test labels assigned to different source-document identities | 12 | Complete independence when revisions, translations or authors' prior knowledge overlap |
| Multilingual / cross-lingual retrieval | Query and corpus within each of several languages / query and evidence in different languages | 12 | One benchmark or translated query proving all language directions |
| Vector index | Data structure for vector similarity lookup | 15 | Vector database/service |
| Exact KNN | Top-k closest items under a chosen metric, found without approximation | 10 | ANN |
| ANN | Search that trades exact-neighbor recall for speed, memory, or I/O | 15 | Relevance ranking quality |
| Hybrid retrieval | Combining more than one retrieval signal, often lexical and dense | 25 | A specific fusion formula |
| RRF | Reciprocal rank fusion, combining ranks rather than raw scores | 25 | Weighted score sum |
| Learning to rank | Estimating ranking order from labeled query-candidate examples and features | 27 | Hand-tuned heuristic or candidate retrieval |
| ACL | Access-control list or equivalent document eligibility policy | 21 | A soft relevance signal |
| Qrels | Versioned query-to-eligible-item relevance judgments under a declared corpus, unit, scope and rubric | 09 | Generated answers or permission grants |
| Relevance grade / rubric | Ordinal judgment and written rule for how useful one eligible segment is for one information need | 09 | BM25 score or universal authority label |
| Judgment universe | Source snapshot, indexed unit and eligible item roster over which qrels and metric denominators are defined | 09 | All documents a system might ever access |
| Unjudged item | Candidate whose relevance has not been assessed for a query, often because it was outside a pool | 09 | Reviewed grade-0 item |
| Judgment pool | Union of candidate items selected from diverse retrieval runs or expert search for human assessment | 09 | Complete corpus by default |
| Precision@K | Number of binary-relevant results in first K positions divided by K under a declared missing-slot policy | 09 | Recall@K or answer correctness |
| Recall@K | Number of known eligible binary-relevant items in first K positions divided by all known eligible binary-relevant items | 09 | ANN exact-neighbor recall or context recall |
| Hit Rate@K | Fraction of positive queries with at least one relevant result in first K positions | 09 | Coverage of every required evidence span |
| F1@K | Harmonic mean of Precision@K and Recall@K for a positive query when defined | 09 | Either component or answer quality by itself |
| Reciprocal rank / MRR@K | Inverse rank of the first binary-relevant result within K / mean over positive queries | 09 | Reward for finding every relevant item |
| Average precision / MAP@K | Mean of precision at relevant ranks through K divided by all known positives / mean over positive queries | 09 | Precision@K or a score normalized only by retrieved positives |
| DCG / NDCG@K | Sum of graded gains discounted by rank / ratio to ideal gain from the whole judged eligible set | 09 | Calibrated utility or proof of multi-evidence completeness |
| Macro / micro averaging | Equal weight per positive query / pooling relevant-item hits and denominators across positive queries | 09 | Interchangeable workload summaries |
| Zero-positive query | Information need with no relevant item in the declared eligible corpus; some ranking measures are undefined and candidate-return behavior is reported separately | 09 | Query that simply returned zero candidates |
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
| Metric | Quantified measure with a declared unit, denominator and aggregation; a production metric is an aggregated time series | 09; deep treatment 52 | One request log or an unlabeled quality claim |
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
- **Judged retrieval and core evaluation (09, 30–33):** qrels, relevance grades, pooling/unjudged policy, P/Recall/Hit/F1/MRR/MAP/NDCG, context recall/precision, answer correctness, faithfulness, citation support, benchmark transfer, LLM-as-judge and failure localization.
- **Specialized retrieval (34–47):** dialogue state, multi-hop, adaptive/active/corrective, Self-RAG, agentic policy, graph/community, web, SQL, document layout, multimodal embedding, code symbol graph, federation.
- **Production and research (48–57):** p95/SLO, corpus/retriever drift, prompt injection, poisoning, cross-tenant leak, tenant-safe/semantic caches, distributed top-k, cost per query, REALM, FiD, RETRO, Atlas.
- **Telemetry and operations (02, 09, 30–32, 48, 50–52):** correlation/trace/span ID, event, counter, gauge, histogram, log level, redaction, label cardinality, trace sampling, critical path, SLI/SLO/SLA, error budget, cost ledger, alert and incident.

## Naming notes

“RAG” is used broadly here for retrieving external knowledge to inform generation, while the original 2020 RAG paper describes particular model architectures. “GraphRAG” can mean any graph-enabled retrieval system or a named implementation with community summaries; chapters will say which. “Contextual retrieval,” “late chunking,” “adaptive RAG,” and “agentic RAG” overlap, so mechanism and source are always stated. “Recall” is qualified as relevance recall, context recall, or exact-neighbor ANN recall, each with its own denominator. “Confidence” specifies whose estimate it is: retriever score, trigger probability, answer confidence, or calibrated correctness. “Memory” identifies session state, durable user preference, model weights, or external corpus explicitly.
