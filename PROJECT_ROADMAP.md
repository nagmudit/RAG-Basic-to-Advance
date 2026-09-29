# Running project: Build Your Own RAG Engine

Each version is motivated by an observed limitation. Snapshots preserve its code, source manifest, fixed queries, relevance judgments, retrieval trace, latency, and representative failures. Minimal correlated telemetry starts in V0 and gains spans and stage metrics as stages appear. After V2, **every version** reports the frozen query set, relevant evidence IDs, at least one retrieval metric, p50/p95 latency, and two failure examples. After generation begins in V9, every version also reports answer correctness, faithfulness, citation support, and abstention behavior. Production versions add an ingestion trace, version manifest, cost ledger, SLIs/SLOs and a working dashboard under [the observability contract](observability/OBSERVABILITY_CONTRACT.md). A new feature is retained only when its target slice improves without violating authorization or service constraints.

The [V0 project snapshot](projects/V0/README.md) now includes the Chapter 1 evidence contract, Chapter 2 [full-scan engine](projects/V0/engine.py), ten-document corpus, behavioral tests and [baseline result record](projects/V0/RESULTS.md). Its two frozen questions preserve the first search path and failure cases.

Chapter 3 adds a [read-only V0 measurement sidecar](projects/V0/CHAPTER_03_MEASUREMENT.md) for exact-ID lookup, raw timing data and a reproducible plot. It measures computing primitives before V1 changes the retrieval algorithm. The V0 answer path and frozen evidence tests remain the baseline.

Chapter 4 adds [controlled context and prompt probes](projects/V0/CHAPTER_04_CONTEXT_PROBES.md) before any generator is integrated. The probes preserve source identity, eligibility and the two frozen evidence questions; their manifest explicitly records no model results. Generation enters the running engine at V9 after retrieval, ranking and context construction have measurable baselines.

Chapter 5 starts [V1's positional lexical index](projects/V1/README.md). Its default analyzer and unweighted score reproduce V0 candidate order and frozen answer behavior; Boolean, phrase and Unicode diagnostics expose new analyzer choices separately. A raw scan-versus-postings experiment records index build cost, query work and latency. Chapter 6 adds TF-IDF before V1 is considered complete; judged qrels still begin at V2 / Chapter 9.

Chapter 6 completes [V1's first ranking comparison](projects/V1/README.md) with raw, sublinear and cosine TF-IDF on the same indexed source. The paired experiment keeps the required-span gain for termination and loss for the dated contract change at top two; build cost, search timing, candidate IDs, context IDs and stub status remain separate. This is a transparent fixture check before Chapter 9's broader qrels and metrics, not a declaration of a winning ranker.

Chapter 7 starts [V2's BM25 stage](projects/V2/README.md). It adds scope-local segment lengths and `avgdl`, nonnegative IDF and saturating term contributions over the same V1 postings. A short/long fixture isolates `b`; a paired frozen-query run preserves both the top-two termination gain and dated-contract evidence loss. It records candidate/context separation, build cost, search timing and version hashes. The judged V2 metric baseline is still scheduled for Chapter 9, after Chapter 8's exact top-*k* pruning method.

Chapter 8 adds [V2's global-bound WAND stage](projects/V2/README.md): scope-specific cached BM25 term impacts and conservative upper bounds, DAAT posting cursors, a top-*k* heap and exact tie handling. A paired five-query, three-depth record checks ordered IDs, raw scores, selected context and stub status against exhaustive BM25. It reduces full scores on some cases but is slower than cached exhaustive search on the tiny Python corpus. Gap/variable-byte coding is a separate teaching codec; compressed-disk and Block-Max WAND execution remain conceptual. Chapter 9 still supplies reviewed qrels and ranking metrics.

| Version / chapters | Previous limitation | Feature and concept | Implementation task | Observation to test |
|---|---|---|---|---|
| V0 / 01–02 | No external evidence | Literal search, explicit context, minimal telemetry | Score text matches; label sources; log request/query ID, source snapshot, retrieved IDs/scores, chosen evidence IDs, status and wall-clock latency | Exact words work; paraphrases and long documents fail; one request is replayable |
| V1 / 03–06 | Full scans and unweighted terms | Tokenizer, postings, TF-IDF | Build inverted and forward indexes; record index build time and search-stage duration | Rare terms affect rank; scans are avoidable |
| V2 / 07–09 | Repetition/length bias and unmeasured ranking | BM25, lexical top-k pruning, qrels | Implement BM25, one safe pruning method, judged retrieval metrics and a p50/p95 latency summary with query-set version | Same exact top-k with fewer scored documents; metric baseline established |
| V3 / 10–14 | Paraphrase gaps and domain mismatch | Vectors, embeddings, retriever adaptation, exact dense and learned sparse | Evaluate frozen encoder, train/adapt on held-out domain split, compare BM25 | Some paraphrases improve; IDs and out-of-domain queries may regress |
| V4 / 15–18 | Exact KNN cost | Trees/LSH demonstration, IVF/PQ or HNSW, vector service comparison | Benchmark against exact oracle, including filtered queries; record ANN settings, index version and stage latency | Recall/latency/memory frontier appears |
| V5 / 19–20 | Whole documents dilute evidence | Parsing, lineage and chunking | Preserve page/section anchors; compare three chunkers | Boundary quality changes recall and citation precision |
| V6 / 21–22 | Wrong tenant, date or version | Metadata/ACL and freshness lifecycle | Prefilter permissions; upsert, tombstone and reindex; record change/visibility times and protected authorization events | Unauthorized and stale hits disappear; update lag is measurable |
| V7 / 23–25 | One query form or signal misses evidence | Routing, rewriting, BM25+dense, RRF | Preserve original query; fuse eligible candidates | Exact IDs and paraphrases improve on separate slices |
| V8 / 26–27 | Top candidates misordered | Reranking and learned ranking | Compare 8 direct with 100→30→8; train simple feature ranker; record per-stage IDs, counts and durations | Quality/cost curve varies with candidate depth |
| V9 / 28–29 | Good hits become weak answers | Context packing, grounded generation, citations and abstention | Pack diverse evidence; mark claims and source spans; log context IDs, model/prompt version, tokens, generation duration, estimated stage cost and abstention reason | Answer support may peak before max context size |
| V10 / 30–33 | Anecdotes hide failure and benchmark mismatch | **Core RAG evaluation harness** | Implement retrieval/context/answer metrics, basic judge rubric, nested redacted request spans, versioned dataset cards and failure localization | Failures localize to first responsible stage; benchmark fit is explicit |
| V11 / 34 | Follow-ups lose references | Conversational state and rewrite | Resolve pronouns with source-preserving state | Follow-up recall improves; ambiguity remains visible |
| V12 / 35 | One pass misses linked facts | Multi-hop retrieval | Track intermediate entities, queries and evidence edges | Hop recall and final answer quality diverge |
| V13 / 36 | Fixed retrieval is wasteful or insufficient | Adaptive trigger and corrective fallback | Calibrate no-result/retry/escalation on held-out queries | Trigger false positives/negatives and costs are visible |
| V14 / 37 | Fixed plan fails mixed requests | Bounded agentic policy | Choose local tools from observations; stop on budget/loop | Dynamic routes help selected tasks; runaway loops are prevented |
| V15 / 38–39 | Similarity misses relations or themes | Graph paths and community summaries | Extract cited edges, traverse and summarize | Local/global graph benefits depend on query type and build cost |
| V16 / 40 | Corpus cannot answer fresh events | Web retrieval | Search/fetch/parse/date/dedupe/cite live pages | Freshness rises while source credibility becomes a risk |
| V17 / 41 | Exact aggregations fail in text retrieval | Validated SQL/API path | Add read-only schema-aware query route | Numeric exactness improves; tool permissions are tested |
| V18 / 42–43 | Text extraction loses visual evidence | Layout-aware and multimodal retrieval | Compare OCR-first, page-image and region paths | Chart/table/figure recall differs by representation |
| V19 / 44–45 | Generic chunks and one index miss structure | Code and federated retrieval | Add symbol graph, commit IDs, two-index fusion and timeout flags | Cross-file tasks improve; partial results stay explicit |
| V20 / 48 | Offline gains may not survive deployment | Production evaluation | Ablations, confidence intervals, slice-specific regression gates, canary/rollback rule and drift report from the existing trace/metric stream | Regression gates detect slice, latency and cost failures before rollout |
| V21 / 49–50 | Local scripts cannot safely serve users or updates | Secure API and ingestion workers | ACL tests, tenant-safe caches, queue, idempotency, deletion; correlate source-change-to-visibility spans, queue lag, parse/embedding failures, deletion delay and security events | Cross-tenant access is blocked; replay and deletes converge with measurable freshness |
| V22 / 51–52 | One node cannot meet service targets | Shards, replicas, production observability and economics | Overfetch shard top-k; propagate trace context; implement structured logs, counters/gauges/histograms, version manifest, request/ingest spans, stage cost ledger, SLIs/SLOs, alerts and a working local or deployable dashboard; diagnose an injected incident | Fan-out and p99, filter selectivity, freshness, quality and cost are visible by route and version |
| V23 / 56 | Components exist without system proof | Production platform capstone | Integrate UI, backup/restore, threat model, reproducible benchmarks, dashboard/runbook and design defense; test workload-specific retrieval, generation, latency, reliability, freshness, security and cost gates | Meets explicit gates or documents each failure and remediation |

## Invariant evaluation record

From V2 onward, freeze a query-set version and record `query_id`, relevance labels, source/version IDs, eligibility filters, raw candidates and scores, final rank, retrieval metric, p50/p95 timing, and at least two root-cause examples. Keep exact-ID, paraphrase, multilingual, stale, and permission slices. From V9 onward add answer claims, supporting spans, correctness/faithfulness labels, citation accuracy and abstention outcomes. Core evaluation is formalized in V10, but simple judgments and metrics begin in V2. Every version preserves its telemetry schema and versions so a regression can be compared fairly. The capstone adds a deployment manifest, incident runbook, backup/restore drill and architecture decision records. The reusable experiment card and ten trace-led debugging scenarios are in [EVALUATION_EXPERIMENT_CONTRACT.md](evaluation/EVALUATION_EXPERIMENT_CONTRACT.md).

## Telemetry progression between milestones

The row for each version records its **new** signals; previously learned signals continue. V3 adds encoder/training and corpus-split versions to retrieval comparisons. V5 traces source → parsed span → chunk → index ID. V7 records original versus rewritten query and each source's candidates before fusion. V11–V14 record conversation state reference, hop number, action/observation, retrieval trigger, budget and stop reason without logging private text. V15–V19 add graph-edge provenance, web capture time, SQL/API result status, page/region coordinates, code commit ID, source timeout and partial-result flags as each route appears. V20 turns these measurements into release decisions; V21 correlates source changes with visibility; V22 implements the dashboard and alerts. At every stage, candidate IDs, selected evidence IDs and answer citations remain separate and access-controlled.

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
