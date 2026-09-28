# Running project: Build Your Own RAG Engine

Each version is motivated by an observed limitation. Snapshots preserve its code, source manifest, fixed queries, relevance judgments, retrieval trace, latency, and representative failures. After V2, **every version** reports the frozen query set, relevant evidence IDs, at least one retrieval metric, p50/p95 latency, and two failure examples. After generation begins in V9, every version also reports answer correctness, faithfulness, citation support, and abstention behavior. A new feature is retained only when its target slice improves without violating authorization or service constraints.

| Version / chapters | Previous limitation | Feature and concept | Implementation task | Observation to test |
|---|---|---|---|---|
| V0 / 01–02 | No external evidence | Literal search and explicit context | Score text matches; label sources; use stub generator | Exact words work; paraphrases and long documents fail |
| V1 / 03–06 | Full scans and unweighted terms | Tokenizer, postings, TF-IDF | Build inverted and forward indexes | Rare terms affect rank; scans are avoidable |
| V2 / 07–09 | Repetition/length bias and unmeasured ranking | BM25, lexical top-k pruning, qrels | Implement BM25, one safe pruning method and metrics | Same exact top-k with fewer scored documents; metric baseline established |
| V3 / 10–14 | Paraphrase gaps and domain mismatch | Vectors, embeddings, retriever adaptation, exact dense and learned sparse | Evaluate frozen encoder, train/adapt on held-out domain split, compare BM25 | Some paraphrases improve; IDs and out-of-domain queries may regress |
| V4 / 15–18 | Exact KNN cost | Trees/LSH demonstration, IVF/PQ or HNSW, vector service comparison | Benchmark against exact oracle, including filtered queries | Recall/latency/memory frontier appears |
| V5 / 19–20 | Whole documents dilute evidence | Parsing, lineage and chunking | Preserve page/section anchors; compare three chunkers | Boundary quality changes recall and citation precision |
| V6 / 21–22 | Wrong tenant, date or version | Metadata/ACL and freshness lifecycle | Prefilter permissions; upsert, tombstone and reindex | Unauthorized and stale hits disappear; update lag is measurable |
| V7 / 23–25 | One query form or signal misses evidence | Routing, rewriting, BM25+dense, RRF | Preserve original query; fuse eligible candidates | Exact IDs and paraphrases improve on separate slices |
| V8 / 26–27 | Top candidates misordered | Reranking and learned ranking | Compare 8 direct with 100→30→8; train simple feature ranker | Quality/cost curve varies with candidate depth |
| V9 / 28–29 | Good hits become weak answers | Context packing, grounded generation, citations and abstention | Pack diverse evidence; mark claims and source spans | Answer support may peak before max context size |
| V10 / 30–33 | Anecdotes hide failure and benchmark mismatch | **Core RAG evaluation harness** | Implement retrieval/context/answer metrics, basic judge rubric, traces and dataset cards | Failures localize to first responsible stage; benchmark fit is explicit |
| V11 / 34 | Follow-ups lose references | Conversational state and rewrite | Resolve pronouns with source-preserving state | Follow-up recall improves; ambiguity remains visible |
| V12 / 35 | One pass misses linked facts | Multi-hop retrieval | Track intermediate entities, queries and evidence edges | Hop recall and final answer quality diverge |
| V13 / 36 | Fixed retrieval is wasteful or insufficient | Adaptive trigger and corrective fallback | Calibrate no-result/retry/escalation on held-out queries | Trigger false positives/negatives and costs are visible |
| V14 / 37 | Fixed plan fails mixed requests | Bounded agentic policy | Choose local tools from observations; stop on budget/loop | Dynamic routes help selected tasks; runaway loops are prevented |
| V15 / 38–39 | Similarity misses relations or themes | Graph paths and community summaries | Extract cited edges, traverse and summarize | Local/global graph benefits depend on query type and build cost |
| V16 / 40 | Corpus cannot answer fresh events | Web retrieval | Search/fetch/parse/date/dedupe/cite live pages | Freshness rises while source credibility becomes a risk |
| V17 / 41 | Exact aggregations fail in text retrieval | Validated SQL/API path | Add read-only schema-aware query route | Numeric exactness improves; tool permissions are tested |
| V18 / 42–43 | Text extraction loses visual evidence | Layout-aware and multimodal retrieval | Compare OCR-first, page-image and region paths | Chart/table/figure recall differs by representation |
| V19 / 44–45 | Generic chunks and one index miss structure | Code and federated retrieval | Add symbol graph, commit IDs, two-index fusion and timeout flags | Cross-file tasks improve; partial results stay explicit |
| V20 / 48 | Offline gains may not survive deployment | Production evaluation | Ablations, confidence intervals, canary and drift dashboard | Regression gates detect slice and latency failures |
| V21 / 49–50 | Local scripts cannot safely serve users or updates | Secure API and ingestion workers | ACL tests, tenant-safe caches, queue, idempotency, deletion | Cross-tenant access is blocked; replay and deletes converge |
| V22 / 51–52 | One node cannot meet service targets | Shards, replicas, observability and cost | Overfetch shard top-k, merge, trace p95, model cost/recovery | Fan-out, filter selectivity and tail latency dominate choices |
| V23 / 56 | Components exist without system proof | Production platform capstone | Integrate UI, backup/restore, threat model, benchmarks, runbook and design defense | Meets explicit quality/safety/freshness/cost gates or documents why not |

## Invariant evaluation record

From V2 onward, freeze a query-set version and record `query_id`, relevance labels, source/version IDs, eligibility filters, raw candidates and scores, final rank, retrieval metric, timing, and root-cause examples. Keep exact-ID, paraphrase, multilingual, stale, and permission slices. From V9 onward add answer claims, supporting spans, correctness/faithfulness labels, citation accuracy and abstention outcomes. Core evaluation is formalized in V10, but simple judgments and metrics begin in V2. The capstone adds a deployment manifest, incident runbook, backup/restore drill and architecture decision records.

## Required experiments

- BM25 vs exact dense vs hybrid on SKU, acronym, paraphrase and multilingual slices.
- Baseline vs adapted retriever on an untouched domain test set; inspect false negatives and leakage.
- Safe lexical pruning and ANN against exact top-k oracles, with filtered recall and p95 latency.
- Chunk boundary/overlap vs evidence recall, duplicate tokens and citation precision.
- Reranker candidate depth and learned features vs quality, p95 and cost.
- Context size/order vs supported claims, contradictions and abstention.
- Adaptive trigger vs fixed retrieval: missed retrievals, needless retrievals and total cost.
- Edit/delete/reindex/cache invalidation timing, including tenant-scoped caches.
- Graph vs passage retrieval on relationship and global-theme questions.

Negative results are valid when the comparison is reproducible and its workload limits are clear.
