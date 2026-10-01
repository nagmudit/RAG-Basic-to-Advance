# Chapter 11 — How embedding models learn retrieval spaces [INTERMEDIATE]

Chapter 10 gave us an exact answer to a geometric question: *which eligible item is closest to this query vector under this metric?* It did not answer where useful coordinates come from. Its 119-dimensional binary term vectors fell below BM25 on Chapter 9's judged questions, and a query that uses different words can still have little or no overlap with its evidence. The next change is to learn a mapping from text to numbers so that some differently worded query–passage pairs become close. The new risk is equally important: a learned mapping can place a wrong product, outdated clause, or plausible but unanswerable passage nearby. An embedding is a model output, not an evidence certificate.

This chapter explains the mechanism and evaluates **one frozen encoder**. It does not train on the Helios corpus or choose a winning model. Chapter 12 will cover retriever training and domain adaptation; Chapter 13 will treat dense candidate retrieval operations. The running engine still keeps authorization before scoring and candidate, selected context and answer as separate stages.

**Prerequisites.** Chapter 4 introduced token representations and attention inside a language model. Chapter 10 supplied norms, cosine, exact top-*k* and the zero-vector policy. Chapter 9 supplied qrels and ranking metrics; V2 BM25 is the judged baseline. Read the [Chapter 11 lab](../labs/chapter-11/LAB.md) after the mechanism and try it before the [solutions](../solutions/chapter-11-solutions.md).

**Workload identity:** `ch11-embedding-probes-v1`; see the [comparison registry](../evaluation/WORKLOAD_REGISTRY.md). Metrics across different workloads do not form an improvement sequence.

## 1. What is actually encoded?

An **encoder** maps an input sequence of model tokens to numerical representations. A noncontextual word lookup assigns a token a learned vector regardless of surrounding words. A contextual text encoder changes a token's representation using other visible tokens, so the same surface token can contribute differently in different sentences. A transformer encoder does this through layers of attention and feed-forward transformations; Chapter 4's query/key/value picture applies here, but the encoder's output is not a generated answer. It is a set of token vectors. A retrieval application needs a declared way to turn them into a passage vector.

The pipeline has several contracts:

```text
source record + section/version/allowed scopes
    → choose the exact searchable text (e.g. title + segment body)
    → model tokenizer, token limit and truncation rule
    → contextual token vectors h₁ ... hₜ
    → pooling (for example, masked mean) → one d-coordinate vector
    → optional projection and L2 normalization
    → store vector with source ID, scope and encoder/format version

question → compatible query tokenizer/encoder/prefix → query vector
         → eligibility gate → exact similarity → candidate IDs
         → selected context → later answer and citation checks
```

**Pooling** compresses token vectors to one vector. With attention mask `mᵢ∈{0,1}`, masked mean pooling is `z = (Σᵢ mᵢ hᵢ)/(Σᵢ mᵢ)` for a nonempty unmasked input. Padding tokens do not count. In a two-coordinate toy, token vectors `(2,0)`, `(0,4)` and padding `(99,99)` with mask `1,1,0` yield `(1,2)`, not `(33.67,34.33)`. A special-token representation or max pooling is another design, but changing pooling changes every vector and may change rank. A “sentence embedding” is therefore **tokenizer + model weights + input format + pooling + normalization + dimension**, not merely a checkpoint name. [The local arithmetic implementation](../projects/V3/contrastive_math.py) exposes masked mean before the project uses a library encoder.

The chosen [model card](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2/blob/8b3219a92973c328a8e22fadcfa821b5dc75636a/README.md) describes a 384-coordinate sentence/short-paragraph encoder with attention-mask-aware mean pooling and normalization, and says inputs beyond 256 word pieces are truncated by default. V3 pins the public Apache-2.0 checkpoint revision `8b3219a92973c328a8e22fadcfa821b5dc75636a`. Those are **this model's** properties, not universal embedding defaults. The project source segments are short, yet a real page or code file may exceed a model's input limit. If the answer-bearing span is beyond truncation, an excellent encoder cannot embed it. Chunking and lineage in Chapters 19–20 will make this failure explicit.

### Word, token, sentence and document are different units

The V1 analyzer's term `Sev-1` and the model tokenizer's word pieces need not coincide. A token vector describes a position in one encoded sequence; a pooled vector describes the whole input under the pooling rule. A source *document* can contain many indexed *segments*, each with its own vector and source locator. If one vector represents an entire long document, it may blur several unrelated facts; if each segment gets a vector, retrieval can find a local span but can also split a needed clause. The project keeps V0's existing segments so the representation change is inspectable. It encodes `title + newline + segment text`, without inserting segment ID, source status or effective date into either method's searchable text. That decision is visible in the experiment; changing it would be a separate comparison.

## 2. Why two encoders can retrieve without reading every pair

A **bi-encoder**, also called a dual encoder, computes `u = E_q(q)` and `v = E_p(p)` independently, then scores `s(q,p)=u·v` or a declared alternative such as cosine. `E_q` and `E_p` may share weights, use separate weights, or be one model with different query/document prompts. Independence permits passage vectors to be cached at index time. A query then requires one query encoding plus vector search. With `N` items and dimension `d`, the exact scorer still needs `O(Nd)` coordinate work; later ANN can reduce comparisons but must be evaluated against Chapter 10's oracle. Scoring does not check whether a passage is signed, fresh, permitted, complete or factually correct.

A **cross-encoder** instead processes `(q,p)` together and can attend across their tokens, but it must run separately for candidate pairs. Its interaction can improve ranking within a small candidate set; it cannot cheaply precompute one passage vector independent of the query. Chapter 26 will use that cost/quality distinction for reranking. A late-interaction model stores multiple token vectors per passage and compares them later; it sits between one-vector independence and full pairwise cross-encoding, and Chapter 14 will treat it. These architecture names describe *when* information crosses between query and passage, not a promise of better evidence.

**Query/document asymmetry.** A question is short and asks for a fact; a passage states one. Some retrievers train separate towers or require distinct prefixes such as a query instruction and a passage instruction. The current Sentence Transformers API offers `encode_query()` and `encode_document()` for models with such prompts or tasks; [its documentation](https://www.sbert.net/docs/sentence_transformer/usage/usage.html) says that for models without specialized prompts these behave like ordinary encoding. V3 deliberately uses the pinned symmetric MiniLM sentence model with one shared `encode()` path and no prefixes. Adding an arbitrary prefix to only queries would change the input distribution and make stored passage vectors incompatible with the intended format. Always inspect the model card and preserve the exact query/passage preprocessing version. “Same 384 dimensions” does not make embeddings from two model revisions compatible.

**Figure 11.01 — Independent encoding and one contrastive batch.** Query vectors `q₁=(1,0)`, `q₂=(0,1)` and passage vectors `p₁=(3,0)`, `p₂=(1,2)` are hand-authored in arbitrary feature units. The matrix displays every dot product. Its diagonal denotes the *declared training pairs*, not proven relevance. The off-diagonal items are assumed negatives; a second valid passage would violate that assumption.

![Queries q1 and q2 enter a query encoder, while passages p1 and p2 enter a passage encoder. Their two-coordinate outputs form a two-by-two dot-score matrix with rows 3,1 and 0,2. The diagonal positive cells are highlighted; the row-softmax positive probability is about 0.881 and mean loss about 0.127.](../visuals/chapter-11/figure-11-01-encoders-and-batch.svg)

*Alt text:* Independently encoded query and passage vectors produce all four pair scores, with higher diagonal scores and an explicit warning that an off-diagonal pair could also be relevant. *Editable source:* [plot program](../visuals/chapter-11/plot-11-01-encoders-and-batch.py); [PNG](../visuals/chapter-11/figure-11-01-encoders-and-batch.png). Chapter 11; Python and matplotlib; coordinates are fixed arbitrary feature units, no sampling, seed or uncertainty. The matrix score is a dot-product unit; loss is in natural-log units (nats).

## 3. How a training signal shapes the space

For the loss-to-parameter step, continue to [Chapter 12's worked update](chapter-12-retriever-training-and-domain-adaptation.md#from-a-vector-to-one-parameter-update). Its [stability bridge](chapter-12-retriever-training-and-domain-adaptation.md#stable-probabilities-compute-the-same-objective) connects the common-factor cancellation below to this module's subtract-max/log-sum-exp code.

A useful retriever cannot infer relevance from geometry alone. It needs examples saying that query `qᵢ` should be close to positive passage `pᵢ⁺` and separated from alternatives. For a batch of `B` aligned query–positive pairs, form a `B×B` score matrix `Sᵢⱼ = s(E_q(qᵢ), E_p(pⱼ))`. The simplest **in-batch contrastive** rule treats column `i` as the one positive for row `i` and every other column as negative:

```text
P(pᵢ | qᵢ, batch) = exp(Sᵢᵢ / τ) / Σⱼ exp(Sᵢⱼ / τ)
L = −(1/B) Σᵢ log P(pᵢ | qᵢ, batch)
```

`τ>0` is a **temperature** that scales score differences before the row softmax. It does not make a raw cosine into a calibrated probability that a passage is relevant; `P` is conditional on the chosen batch and its assumed one-positive labels. The model weights are adjusted by gradients of this loss during training. Our project **does not adjust weights** in Chapter 11. [The from-scratch function](../projects/V3/contrastive_math.py) computes a numerically stable log-sum-exp and the batch loss to expose the mechanism before Chapter 12 teaches actual fitting.

For Figure 11.01, `S=[[3,1],[0,2]]` and `τ=1`. Row one assigns its diagonal `e³/(e³+e¹)=1/(1+e⁻²)≈0.8808`; row two gives the same probability `e²/(e⁰+e²)≈0.8808`. The mean loss is `−ln(0.8808)≈0.1269` nats. If every score were `1`, each row would have probability `0.5` and loss `ln 2≈0.6931`. A smaller temperature sharpens the first example's preference, but when a mislabeled alternative is actually relevant it can amplify the wrong training pressure.

The batch rule creates **in-batch negatives** almost for free, but a different passage in the batch may also answer the query. That is a **false negative**. A **hard negative** looks similar to the query yet lacks the required fact, perhaps the Helios Pro FAQ when the signed effective amendment is requested. It teaches a finer boundary only if the label is correct. A stale passage, wrong entity, partially relevant span and genuinely irrelevant item should not be silently collapsed into one universal class. Chapter 12 will examine explicit labels, mining, weak supervision, teacher-generated signals, false-negative detection, and domain adaptation. Here the essential point is that **training data and objective decide what “near” means**; neither cosine nor a transformer automatically enforces source authority or exact identity.

### Dimensions and Matryoshka prefixes

A `d`-coordinate vector costs `O(d)` to compare and roughly `4d` raw bytes at float32 before IDs and index overhead. More dimensions can express more distinctions but also raise storage, transfer and exact-scan work; fewer dimensions can discard a critical entity or numeric feature. **Matryoshka representation learning** trains multiple nested prefixes of one vector to remain useful at specified dimensions. For an approved prefix length `m`, truncate **both** query and passage vectors, renormalize if cosine is the metric, rebuild the index under a new version, and measure quality and exact-neighbor agreement by slice. Arbitrarily taking the first 128 coordinates of this Chapter 11 model is *not* a Matryoshka experiment: its [model card](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2/blob/8b3219a92973c328a8e22fadcfa821b5dc75636a/README.md) does not claim that training objective. The [original research paper](https://arxiv.org/abs/2205.13147) motivates nested-prefix learning, but every candidate model and prefix still needs testing on the target corpus.

## 4. Frozen model experiment on newly judged questions

The [V3 Chapter 11 probe](../projects/V3/judgments_ch11.json) was written and reviewed before querying the model. It contains 17 fictional questions: eight paraphrases, six exact-identifier/entity/numeric probes, and three no-eligible-evidence probes. Every one of the twelve support-team segments has a 0/1/2 judgment for each question: **204 reviewed query–segment pairs**. One author knew the corpus and earlier failure patterns, so this is not a blinded, independent or production-representative benchmark. No query was used to fit or tune this frozen model. The qrels loader rejects a changed source snapshot, segment roster, illegal ID or contradicted no-evidence slice. Legal-only D10 is outside the judgment universe and search eligibility.

**Experiment contract.** Question: does a frozen sentence encoder improve paraphrase retrieval over V2 exhaustive BM25, and how does it behave on identifiers and no-evidence questions? Falsifiable hypothesis: mean paraphrase Recall@2 rises. Primary system change: BM25's analyzed-term/posting score versus normalized 384-coordinate MiniLM sentence vectors and Chapter 10's exact cosine scan. The source snapshot, V0 segment boundaries, support-team eligibility, frozen questions/qrels, top-*k* values, 120-source-word context builder and Chapter 9 metric formulas stay fixed. The representation, score and execution plan change together, so the experiment cannot attribute any gain to one alone. No generation is run for these new questions; candidate rankings and selected-context IDs are recorded separately.

The [reproducible runner](../projects/V3/experiment_ch11.py) pins model revision and library versions, stores normalized passage vectors at index time, encodes one question at query time, filters scope before exact scoring, and retains raw scores/work. Seven randomized-order warmed timings per query/depth compare BM25 search with *query encoding plus exact scan*; model load, document encoding/index build and context selection are separate. The [checked-in record](../projects/V3/chapter-11-experiment.json) includes per-query results, input/code hashes, versions, measurement window and local raw samples.

| Top-two result on the 17-query probe | V2 BM25 | Frozen encoder + exact cosine |
|---|---:|---:|
| Paraphrase macro binary Recall@2, 8 queries | 0.8125 | **1.0000** |
| Paraphrase macro NDCG@2 | 0.7383 | **0.9539** |
| Exact-identifier slice macro Recall@2, 6 queries | 0.6667 | 0.6667 |
| All positive-query macro NDCG@2, 14 queries | 0.7076 | **0.8308** |
| No-evidence questions returning candidates, 3 queries | 3/3 | 3/3 |
| Mean fully scored eligible segments per query | 8.41 | 12.00 |
| Local search / encode-plus-scan p50, 119 samples, µs | 76.4 | 17,081.2 |
| Local search / encode-plus-scan p95, 119 samples, µs | 114.3 | 19,993.3 |

The hypothesis holds **on this authored probe**. For `p-shared`, BM25 top two miss the second runbook segment that names the incident commander; the frozen encoder puts it first. For `p-change-log`, BM25 puts a partial first runbook window first and misses the complete second window at top two; the encoder ranks the complete window first. On `p-observed`, both find the historical incident report by rank two, while the encoder moves it to rank one. Yet the result is not one-way: for `p-basic`, BM25 places the signed Basic agreement first and the encoder places a wrong-product Helios Pro agreement ahead of it, leaving the correct item second. A top-two recall gain does not eliminate an entity error at rank one.

The literal metadata requests `i-segment` (`D1:§8:0`) and `i-price-id` (`D6:row-2:0`) expose another boundary. Neither method indexes those IDs as searchable text. BM25 returns no candidates; the sentence encoder returns geometrically plausible **wrong** candidates. Both have zero judged hits for these two questions. The no-evidence SKU, private-target and renewal questions each return candidates under both methods. For the private request, D10 is correctly excluded before scoring, but the remaining candidates do not answer it. A similarity threshold is not yet calibrated, and a model's nearest neighbor is not a reason to cite. Later query routing and abstention policy must handle these cases with judged calibration.

The checked-in CPU run spent about `574 ms` preparing all thirteen passage vectors and the exact index after model load; model load took about `275 ms` in that warm local process, with Python library import/cache state outside the figure. Its 384 float32 coordinates for 13 vectors need only `19,968` raw bytes before Python object and index overhead. The **17 ms versus 0.076 ms** local median request comparison reflects this particular CPU model, Python implementation, tiny corpus and unbatched query encoder. It is not a production p95 or a general dense-vs-lexical cost ratio. At larger scale, encoder throughput, batching, vector storage, search, network, cache, filtering and candidate depth all need separate measurements. The result has no answer-correctness, faithfulness or citation judgment.

## 5. Diagnose what proximity has learned

When dense retrieval looks good or bad, inspect the following chain rather than treating the score as an explanation:

1. **Input and version.** Did query and passage use compatible tokenizer, prompts, model revision, pooling, normalization and dimension? Was an answer span truncated? Was the indexed source version current?
2. **Eligibility.** Was the source permitted under the request's trusted scope? D10's absence is a policy requirement regardless of its score. Static `support-team` here is a fixture, not authentication.
3. **Candidate representation and rank.** Which eligible IDs, raw similarities and qrel grades appear at each depth? Does a wrong entity, number, negation or unsigned proposal rank above the correct segment? Are score distributions changing across domain, language or model versions? Scores from different models are not calibrated against one another.
4. **Selected context.** Did a relevant candidate survive the source-word budget with locator and version? A top-*k* hit can still be omitted before generation.
5. **Answer.** No new answer generator is used in this chapter. When one is added, judge correctness, faithfulness, citations and abstention separately; retriever confidence is not answer confidence.

A protected trace can record query ID, source/model/index versions, query encoding and exact-scan durations, vector dimension/norm summary, eligible/scored count, candidate IDs/scores, context IDs and no-result reason. Ordinary metrics should aggregate bounded labels, not raw query text, source content, tenant IDs or high-cardinality document IDs. A checkpoint download is a model artifact with license and retention obligations; V3 pins a public Apache-2.0 model and does not commit its weights. If an index retains embeddings derived from private text, treat the embeddings, IDs and caches as governed data and delete/rebuild on policy and source changes. **Corpus drift** or a model revision can invalidate a past score distribution; later evaluation chapters will formalize monitoring.

Multilingual retrieval illustrates the same caution. A model trained primarily for English sentence similarity may behave differently for a Japanese query over English passages or for native-language query and corpus pairs. **Multilingual** and **cross-lingual** tasks need distinct labeled slices; neither the model card nor this English fiction probe proves performance in another language. Domain-specific acronyms, code symbols, legal dates and negative evidence also deserve dedicated tests. Chapter 12 will make adaptation choices and leakage controls explicit. The [primary reading path](../PAPER_READING_PATH.md) begins with Sentence-BERT and DPR after these mechanisms, not with a model leaderboard.

### Practice and recall

The [lab](../labs/chapter-11/LAB.md) asks you to compute the score matrix and loss by hand, implement masked pooling and row-softmax independently, reproduce the frozen comparison, inspect failures by slice, and design a version-safe encoder rollout. Keep the Chapter 10 exact oracle alongside judged evidence recall.

1. Which parts of the tokenizer → token vectors → pooling → normalization path must be versioned together?
2. Why does a bi-encoder allow stored passage vectors while a cross-encoder cannot score an arbitrary new query from one stored passage vector?
3. In Figure 11.01, what happens to the loss if `p₂` also correctly answers `q₁`?
4. Why does `p-basic` reveal a rank-one entity failure even though top-two recall is one?
5. Why do both retrievers fail literal segment-ID requests, and what additional indexed field or route would fix the *mechanism*?
6. What would have to be true before a 128-coordinate prefix could replace the full 384-coordinate vector?

**Interview defense.** A team reports that a “semantic model” improves aggregate NDCG and proposes turning off BM25. Ask for query-slice qrels, exact-ID and wrong-entity cases, source/version and permission behavior, model/prompt/pooling versions, top-*k* and context coverage, no-evidence return rate, search and encode latency, and independent test data. State which findings would justify a staged retriever and which would require more data.

Revisit the loss and encoder boundary after one, three, seven and 21 days; redraw Figure 11.01 from memory, then compare V3's frozen-model result with V2 and the Chapter 10 binary-vector result. Further reading: [BERT on contextual representations](https://arxiv.org/abs/1810.04805), [Sentence-BERT on independently comparable sentence embeddings](https://arxiv.org/abs/1908.10084), [DPR on dual-encoder open-domain retrieval](https://arxiv.org/abs/2004.04906), the [pinned model card](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2/blob/8b3219a92973c328a8e22fadcfa821b5dc75636a/README.md), and [Matryoshka representation learning](https://arxiv.org/abs/2205.13147). Read their task, data and metric before transferring a result to this corpus.

**You understand this chapter if you can…** trace text through tokenizer, contextual token vectors, masked pooling and normalization; calculate a two-pair contrastive loss and identify a false negative; explain shared versus asymmetric bi-encoders and their cost relative to cross-encoding; reproduce the pinned exact-search experiment with versioned qrels; name both its paraphrase gains and identifier/no-evidence failures; and separate candidate proximity, selected evidence and supported answers.
