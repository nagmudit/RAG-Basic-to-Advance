# Evaluation and experiment contract

This file is the authoritative reusable plan for judged system changes and production release gates. [Core evaluation](../SYLLABUS.md) begins in Chapters 09 and 30–33; production experimentation follows in Chapter 48. [Observability](../observability/OBSERVABILITY_CONTRACT.md) supplies trace and dashboard evidence, but neither latency nor a judge score alone proves answer quality.

## Required experiment record

For each meaningful algorithm or architecture change, save: **question, falsifiable hypothesis, baseline, independent variable, controlled variables, corpus/dataset and versions, frozen query set, qrels or answer labels, workload slices, metrics and denominators, procedure, per-query and aggregate results, uncertainty where useful, error analysis, conclusion, limitations**. Pin code, model, prompt, index, chunker and judgment rubric versions; state randomized order/seeds and sample exclusions. Change one primary variable at a time or explicitly use a factorial design. A negative result is valid when the comparison is reproducible.

Example questions: Does chunk overlap improve evidence Recall@10? Does hybrid search improve exact identifiers without hurting paraphrases? Does increasing HNSW `efSearch` improve exact-neighbor recall enough to justify p95? Does a reranker improve Precision@5 at fixed candidate depth? Does context compression reduce tokens without reducing supported answers? Report both the target gain and its latency/cost/security regressions. Disaggregate by language, tenant policy, source type, query difficulty and freshness. An incomplete qrel set and LLM judge bias are named limitations, not ignored.

## Quality layers

| Layer | Evidence and measures | Typical failure |
|---|---|
| Candidate retrieval | Qrels; Precision/Recall@K, Hit Rate, MRR, MAP, NDCG, candidate coverage, ANN oracle recall, filter recall | Required span never appears |
| Context | Required evidence coverage/recall, precision or relevant-token ratio, redundancy/diversity, contradiction coverage | Good candidate is dropped or buried |
| Generation | Correctness, completeness, faithfulness/groundedness, citation support, unsupported claims, answerability/abstention | Fluent claim lacks support or follows stale evidence |
| End to end | Task completion, resolution or human preference on a declared workload | Component metrics improve without user outcome |

Judge methods require written rubric, representative human calibration, blind review where possible, disagreement inspection and rubric/version tracking. Synthetic questions help coverage but cannot replace human/production questions. Offline benchmark names are task descriptions, not guarantees of transfer. Online estimates need privacy-safe sampling, denominators and selection-bias notes.

## Production release and capstone gates

Before deployment, specify **workload-specific** thresholds and a fail/rollback policy for: retrieval recall/rank and exact-ID/multilingual/hard slices; correctness, faithfulness, citations, unsupported claims and abstention; p50/p95/p99 with timeouts and partial failures; availability/retry behavior; source-update-to-searchable lag, deletion propagation and migration; cross-tenant isolation, ACL, cache and prompt-injection tests; cost/query, /1,000 and by stage/tenant. Use paired comparisons/confidence intervals for noisy metrics, a canary and regression gates. Document any unmet gate as an explicit capstone failure or accepted limitation with owner and remediation; a service merely running is insufficient. Quality SLOs based on sparse/noisy labels require careful denominators and are generally release gates plus monitored estimates, not universal numeric promises.

| Gate | Minimum evidence |
|---|---|
| Retrieval | Recall/rank at declared K, exact-identifier, multilingual and hard-query slices against frozen qrels |
| Generation | Correctness, faithfulness, citation support, unsupported claims and abstention on a reviewed set |
| Latency | End-to-end and stage p50/p95/p99, timeout and partial-result populations under stated load |
| Reliability | Availability SLI, retry/fallback outcomes, error budget and recovery drill |
| Freshness | Source-update-to-searchable lag, delete propagation and index migration verification |
| Security | Cross-tenant/ACL and cache isolation tests, prompt-injection/tool-boundary probes and protected events |
| Cost | Request and ingest/storage ledger, cost/query and /1,000, plus stage and tenant breakdown where relevant |

## Ten trace-led debugging exercises

For each, preserve a failing request, trace, stage outputs, version manifest, relevant qrels and a proposed regression test.

| # | Observation | First checks and expected diagnosis |
|---|---|---|
| 1 | Wrong answer, perfect retrieval recall | Inspect selected context, claim support and generation/verification; recall does not prove correct use. |
| 2 | High faithfulness, low correctness | Check outdated or incorrect source/version and missing contradictory evidence. |
| 3 | Recall@100 high, Recall@5 poor | Inspect rank features, fusion, reranker depth and per-stage positions. |
| 4 | Offline quality improves, p95 doubles | Compare request distributions, critical path and declared quality/latency gate; decide canary/rollback. |
| 5 | Aggregate accuracy stable, Japanese queries regress | Stratify by language; inspect query/corpus mix, tokenizer and cross-lingual model version. |
| 6 | p50 healthy, p99 terrible | Inspect shard fan-out, queueing, cold starts, retries, timeout and cache-hit mixtures. |
| 7 | New embedding helps semantics, exact IDs degrade | Inspect exact-ID slice, lexical route and fusion; rollback or route identifiers. |
| 8 | Online quality falls, frozen benchmark stable | Check query/corpus/source/language drift, version changes and benchmark coverage; add reviewed fresh queries. |
| 9 | Deleted source appears in answer | Trace delete event through queue, tombstone, index alias, context and tenant-safe cache invalidation. |
| 10 | Tenant B document ID appears in Tenant A trace | Declare a security incident; inspect eligibility, logging and caches even if answer text is clean. |

## Reusable output card

```text
Experiment ID / date / owner:
Question and hypothesis:
Baseline and proposed change:
Independent variable; controlled variables:
Corpus, query-set, qrel/rubric and code/model/index versions:
Slices, metrics, denominators and acceptance gates:
Procedure, seeds, samples and exclusions:
Results (aggregate and per slice, latency/cost/security effects):
Failure examples and trace IDs:
Conclusion, uncertainty and limitations:
Decision (keep, revise, reject) and next regression case:
```
