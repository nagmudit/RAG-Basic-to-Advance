# Production RAG observability contract

This is the authoritative engineering contract for request and ingestion telemetry. Chapters 02, 09–13, 30–32, 48, 50–52, and 56 implement it progressively. The question is: **what did the system do, what evidence did it use, where did time and money go, why did it fail, and is it degrading?** See [the evaluation contract](../evaluation/EVALUATION_EXPERIMENT_CONTRACT.md) for judgments and experiment design. Telemetry never substitutes for relevance judgments.

## Five records with different purposes

| Record | Unit | Purpose | Example |
|---|---|---|---|
| Structured log | One discrete diagnostic record | Search details and failures by correlation ID | `retrieval_failed` with redacted reason and `request_id` |
| Metric | Aggregated numeric time series | Trends, SLI calculations, alerts | `rag_request_latency_ms` histogram by route |
| Trace | Causally linked spans for one execution | Locate slow or failed stages | request → lexical/vector → rerank → generation |
| Evaluation | Judged quality observation on a defined sample | Determine relevance, support and user outcome | Recall@10 on frozen qrels; citation accuracy on reviewed answers |
| Event | Durable business or lifecycle transition | Trigger/replay/audit a state change | `document_deleted`, `index_alias_switched`, `deployment_rolled_back` |

A transition event may cause a log and increment a metric; they are not interchangeable. A quality score is an evaluation tied to a dataset/rubric version, not an unlabeled service-health metric. Use structured, searchable logs with levels, bounded retention, redaction and sampling; keep error/security events at appropriate retention. Do not put raw queries, source text, credentials, user IDs, or tenant IDs in low-cardinality metric labels. A trace may carry restricted identifiers only under access control and retention rules. Sample ordinary traces predictably, but retain failures and suspected security incidents under policy.

## Canonical query trace

The minimal V0 record has `request_id`, `query_id`, timestamp, corpus snapshot, retrieved IDs, raw scores, elapsed milliseconds, status, and failure reason. Add fields when the associated stage exists. At maturity, a root span owns `trace_id`, `request_id`, route, status, tenant scope (protected), source/index/prompt/model versions, wall-clock time, token totals, and cost total. Child spans form this tree:

```json
{
  "trace_id": "t-98127", "request_id": "r-98127", "query_id": "q-17",
  "tenant_scope_ref": "restricted-ref", "index_version": "idx-4",
  "retrieved_document_ids": ["d2", "d9"],
  "reranked_document_ids": ["d9", "d2"],
  "context_document_ids": ["d9"],
  "latency_ms": {"wall": 1119, "retrieval": 103, "rerank": 184, "generation": 742},
  "token_usage": {"input": 4692, "output": 311},
  "cost": {"estimated_total": null, "currency": "USD", "price_version": "example-only"},
  "status": "success"
}
```

The durations are **illustrative schema values**, not measured performance. `null` means cost is not yet calculated; a real ledger must fill it and preserve measured versus estimated status.

```text
rag.request
  query.process (intent, rewrite)
  retrieval (eligibility/filter)
    lexical.search (candidate IDs, scores, depth)
    vector.search (candidate IDs, scores, depth, ANN settings)
    source.search (source, partial/timeout status)
    fusion (input and merged counts)
  rerank (input/output IDs, model version)
  context.build (evidence IDs, source version and span, tokens)
  generation (model, input/output tokens, finish reason)
  verification (claim IDs, cited spans, outcome)
  response (answer/abstain/partial, status)
```

Each span has `span_id`, `parent_span_id`, start/end or duration, stage status, retry count, and redacted diagnostic attributes. Candidate IDs remain distinct from evidence IDs and answer claims. Capture exclusion reasons without exposing unauthorized content. Record the latency critical path: parallel child durations must not be added to infer root latency. For asynchronous work, propagate trace context through queues and use links when there is no single parent; explain trace IDs, span IDs, context propagation and baggage without putting sensitive values in baggage. Version attributes include `application_version`, `prompt_version`, `retriever_version`, `embedding_model_version`, `reranker_model_version`, `generator_model_version`, `index_version`, `chunking_version`, `metadata_schema_version`, and `evaluation_dataset_version` where applicable. Record source-specific partial results and stop/budget reasons for adaptive or agentic routes.

## Canonical ingestion trace

An ingest root identifies `source_id`, `source_version`, event/change ID, tenant policy, ingest run and target index version. Spans follow **source change → connector → queue → parse/OCR → normalize/dedupe → chunk → embed → index write → validation → visible alias**. Updates and deletes require idempotency key, tombstone/deletion time, retry/dead-letter disposition and visibility time. Emit lifecycle events for `document_ingested`, `document_updated`, `document_deleted`, `embedding_generated`, `index_rebuilt`, `index_alias_switched`, `cache_invalidated`, `model_changed`, `drift_detected`, `evaluation_regressed`, deployment and rollback. The ingestion dashboard includes processed/failed documents, parse and OCR error rates, embedding/indexing throughput and failures, queue depth/lag, duplicate rate, reindex progress, source-update-to-searchable lag, and deletion propagation delay.

## Latency and capacity

Measure service time, queue time, network time, cold-start and warm paths separately. Record end-to-end **wall-clock** latency and stage histograms in consistent units. Compute p50/p90/p95/p99 from request samples or histogram buckets over a declared window and sample count; never sum per-stage p95 values. Inspect the critical path for sequential work, parallel lexical/vector search, fan-out, head-of-line blocking, retries, cache-hit mixtures and timeouts. Compare against a workload-specific latency budget with explicit stage allowances and deadline propagation. Display both success and timeout populations so slow failures do not disappear from a success-only percentile. For distributed search, show shard latency, oversampling, merge time and partial-result rate.

| Illustrative stage | p50 ms | p95 ms | p99 ms |
|---|---:|---:|---:|
| Query processing | 14 | 28 | 51 |
| Retrieval | 81 | 147 | 221 |
| Reranking | 153 | 284 | 391 |
| Generation | 612 | 1210 | 1742 |
| End to end | 901 | 1680 | 2310 |

For a sorted set of `n` measured durations, teach a declared percentile estimator (for example, nearest-rank `ceil(p*n)` with 1-based indexing), its small-sample limitations and histogram approximation error. The end-to-end row comes from root request durations; it is **not** the sum of stage percentiles.

## Metric catalog and dashboard assignment

Use counters for requests/errors/security events, gauges for queue depth/freshness and current version, and histograms for latency, tokens, candidate counts and cost. Label only by bounded dimensions such as route, stage, status, model/index *version class* and workload slice; explain cardinality, aggregation, dimensionality and sampling. Exact request, query, document and tenant IDs belong in access-controlled traces/logs. Quality series must show dataset/rubric version, sample size and uncertainty, not silently mix offline and sampled online scores.

| Dashboard | Required views and diagnostic question |
|---|---|
| Retrieval quality | Recall@5/10/20, MRR/NDCG, Hit Rate, candidate coverage, exact-neighbor ANN recall, filter recall; which stage loses relevant evidence? |
| Context quality | Context recall/precision, evidence redundancy/diversity, contradiction coverage, duplicate/relevant-token ratio, context tokens; was evidence selected and preserved? |
| Answer quality | Correctness, completeness, faithfulness, citation accuracy, unsupported-claim rate, answerability and abstention accuracy; did the answer use evidence correctly? |
| System health | Request rate, errors, timeouts, availability, p50/p95/p99 by stage/route, queue/freshness lag, partial results, cache hit rate; is the service meeting its budget? |
| Economics | Cost/query and /1,000 queries, stage cost, token usage, storage/indexing/network, cache savings, cost/successful task and by tenant under restricted access; where is money spent? |
| Security | Unauthorized attempts, ACL/filter and cross-tenant test failures, blocked tool actions, prompt-injection/PII/secret detections, deletion/caching incidents; did a trust boundary fail? |

The Chapter 52 / V22 assignment is a **working local or deployable dashboard** backed by instrumented requests and ingestion jobs. Include useful time windows, sample/denominator labels, metric version, at least one stage latency and quality panel, error/freshness/cost/security panels, an alert and a trace drill-down. Demonstrate one incident from alert to trace to source/judgment to fix and regression test. A screenshot alone does not satisfy the assignment. Teach the chart question, aggregation pitfall and label/cardinality cost for each panel. A small direct implementation (structured JSON logs, in-process histograms, trace IDs and local dashboard data) precedes an optional concrete stack. Chapters may then map to OpenTelemetry, Prometheus/Grafana, and RAG/LLM tools such as LangSmith, Phoenix, TruLens, DeepEval, RAGAS and OpenLLMetry; verify current official documentation when writing.

## Reliability targets and drift

An **SLI** is a measured proportion or distribution (for example, successful requests under 1.5 seconds, or source updates visible within 10 minutes). An **SLO** is a workload-specific target and window; an **SLA** is an external commitment with consequences. The **error budget** is the permitted miss fraction or count over the SLO window. Define numerator, denominator, exclusions, window and measurement source. Track availability, latency, freshness, and where justified durability. A quality gate such as Recall@10 or citation accuracy needs a fixed judgment population and uncertainty interval; noisy judge outputs and changing query mix make it unsuitable as an unqualified live SLO. Favor reviewable offline release gates plus stratified online samples.

Example teaching targets, **not universal defaults**: 95% of eligible requests complete within 1.5 seconds over seven days, or 99% of source updates become searchable within ten minutes over a week. The first allows 5% misses by definition; its operational error-budget count depends on the eligible request denominator. A source update deleted during the window needs an explicit counting policy.

Monitor corpus, query, user/source distribution, language, metadata, retriever/embedding-model and answer-quality drift. Compare matched windows and slices, quantify baseline variance, check version/deployment changes, inspect label coverage, and distinguish ordinary sampling noise from persistent movement. A stable offline benchmark with falling online quality is a prompt to sample fresh production questions safely and add reviewed cases to the next versioned offline set. Close the loop: **offline evaluation → regression gate → deployment/canary → online monitoring → drift diagnosis → new reviewed dataset**.

## Cost ledger and failure localization

For each request record model calls, input/output tokens, retrieval fan-out, candidates reranked, context size, cache hit/miss, query rewrite, embedding/search, reranking, generation and verification costs with a price/version timestamp. Amortize ingest parsing/OCR, embedding, index build/storage, network and compute utilization over a stated horizon. Derive cost/query, cost/1,000 and cost/successful task; support restricted tenant and strategy breakdowns. State whether costs are measured, estimated or allocated. Never present a token-only bill as total operating cost.

For a wrong answer, check in order: source present and licensed/eligible → parsed and current → relevant span indexed → eligible candidate retrieved → ranked into chosen depth → entered context → claim supported/cited → answer correct and current. Compare trace IDs and source versions at each boundary. A security boundary failure is an incident even if the final answer happened to omit the data. Chapters 32, 48, 50 and 52 use the ten concrete investigations in [the evaluation contract](../evaluation/EVALUATION_EXPERIMENT_CONTRACT.md).
