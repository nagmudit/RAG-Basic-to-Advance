# Learner roadmap

| Stage | Parts / chapters | Evidence of readiness | Milestone |
|---|---|---|---|
| Beginner | I–II / 01–09 | Explain RAG, build an inverted index, calculate BM25, and trace top-k execution | Judged lexical search with scores and a pruning trace |
| Competent | III–VII / 10–33 | Compare lexical and learned retrieval, build exact/ANN indexes, rank and pack evidence, evaluate a complete baseline RAG system | Reproducible engine with retrieval, context and answer metrics |
| Advanced | VIII–X / 34–47 | Evaluate conversation, multi-hop, adaptive/agentic, graph, web, SQL, multimodal, code and federated paths against the baseline | Evidence-backed multi-source assistant with bounded policies |
| Production engineer | XI / 48–52 | Measure, trace, debug and operate request and ingestion paths; run experiments, enforce permissions, manage updates, and design distributed retrieval under cost/latency targets | Service with tests, stage traces, versioned quality gates, working dashboard, alerts, cost ledger and recovery plan |
| Expert / research | XII / 53–57 plus paper/frontier paths | Critique research architectures, compare baselines, run ablations and defend novel designs | Capstone and final expertise assessment |

Stages are gates, not fixed durations. Complete a gate when its artifact and explanation pass review. At every gate, keep a failure log: query, expected evidence, actual candidates, scores, filters, context, answer, and root cause.

## Milestone projects

1. **Local search laboratory:** hand-built Boolean, TF-IDF, BM25, safe top-k pruning and relevance judgments over 20–100 documents.
2. **Hybrid corpus engine:** embeddings, a small domain adaptation experiment, exact KNN, ANN, metadata, RRF, reranking and a measured chunk-size comparison.
3. **Evaluated evidence-aware assistant:** source IDs, context budgets, citations and abstention; the Chapters 30–33 harness reports retrieval, context and answer quality before advanced architectures begin.
4. **Multi-source decision engine:** conversational, multi-hop, adaptive and bounded agentic paths across graph, live web, SQL, document images, code and multiple indexes. Every path is compared with the evaluated baseline.
5. **Production RAG platform:** multi-source ingestion; incremental updates; ACL-safe retrieval; tenant-safe caching, query/ingest tracing, SLIs/SLOs, a working dashboard and alerts, APIs, UI, deployment, backup and cost ledger. Diagnose a staged incident and demonstrate deletion propagation and cross-tenant isolation against explicit quality, latency, reliability, freshness, security and cost gates.

## Pacing options

All tracks follow the 57 chapters and the same gates. Durations are planning estimates, assuming 4–6 focused hours per chapter including practice and a larger capstone block; prior experience changes them.

| Study time | Approximate chapter pace | Approximate full path |
|---|---|---|
| 30 minutes/day | 1 chapter every 1–2 weeks | 18–28 months |
| 60 minutes/day | About 1 chapter per week | 12–17 months |
| 2 hours/day | About 2 chapters per week | 6–9 months |
| Intensive, 30–40 hours/week | 4–6 chapters per week | 3–5 months |

Capstone, review, and research time is included in the broad ranges. Do not advance just because a calendar says to; pass the milestone artifact first.
