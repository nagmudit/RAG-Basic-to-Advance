# Retrieval-Augmented Generation: a curriculum architecture

This repository contains the architecture and the beginning of a textbook and laboratory course on retrieval-augmented generation (RAG). The central engineering question is: **when a user asks a question, which evidence should enter the model's context, and why?**

The intended reader can program at a basic level but may know no information retrieval, vector search, language-model internals, or distributed systems. The path begins with a tiny searchable corpus and ends with the ability to design, evaluate, secure, and scale a multi-source retrieval platform. The book treats RAG as a knowledge-access system: lexical search, structured queries, graph traversal, web retrieval, multimodal retrieval, and dense vectors all have distinct roles.

## What completion means

You should be able to build key algorithms from scratch, trace a query through each stage, measure retrieval separately from answer quality, diagnose failures with evidence, instrument and operate the service, justify architecture choices under latency, cost and permission constraints, and read major research papers critically. Completion is demonstrated by a capstone and a final assessment, not by finishing a framework tutorial. The book uses precise diagrams, reproducible plots and selective conceptual illustrations as teaching tools.

## How to use this repository

1. Read [TEACHING_PHILOSOPHY.md](TEACHING_PHILOSOPHY.md) for the learning contract and [KNOWLEDGE_MAP.md](KNOWLEDGE_MAP.md) for prerequisites.
2. Follow the numbered chapters in [SYLLABUS.md](SYLLABUS.md), beginning with [Chapter 1 — A question, a model, and missing evidence](chapters/chapter-01-a-question-a-model-and-missing-evidence.md), [Chapter 2 — Build the first RAG loop](chapters/chapter-02-build-the-first-rag-loop.md), [Chapter 3 — Data, algorithms, and measurements](chapters/chapter-03-data-algorithms-and-measurements-needed-for-search.md), [Chapter 4 — What an LLM does with supplied context](chapters/chapter-04-what-an-llm-does-with-supplied-context.md), [Chapter 5 — Text normalization and inverted indexes](chapters/chapter-05-text-normalization-and-inverted-indexes.md), [Chapter 6 — TF-IDF and vector-space ranking](chapters/chapter-06-tf-idf-vector-space-ranking-and-lexical-limits.md), [Chapter 7 — BM25 and other lexical ranking models](chapters/chapter-07-bm25-and-other-lexical-ranking-models.md), [Chapter 8 — Production lexical query execution](chapters/chapter-08-production-lexical-query-execution.md), [Chapter 9 — Relevance judgments and ranking metrics](chapters/chapter-09-relevance-judgments-and-ranking-metrics.md), [Chapter 10 — Vectors, distance, and exact similarity](chapters/chapter-10-vectors-distance-and-exact-similarity.md), [Chapter 11 — How embedding models learn retrieval spaces](chapters/chapter-11-how-embedding-models-learn-retrieval-spaces.md), [Chapter 12 — Retriever training and domain adaptation](chapters/chapter-12-retriever-training-and-domain-adaptation.md), and [Chapter 13 — Dense candidate retrieval in practice](chapters/chapter-13-dense-candidate-retrieval-in-practice.md). Chapter entries specify the lab and mastery target that later writing must satisfy.
3. Use [ROADMAP.md](ROADMAP.md) to choose a pace. Every pace covers the same material.
4. Evolve one engine using [PROJECT_ROADMAP.md](PROJECT_ROADMAP.md). Record each version's retrieval and answer metrics before replacing a component.
5. Build the core evaluation harness in Chapters 30–33, then apply it to [CASE_STUDIES.md](CASE_STUDIES.md). Enter the tracks in [PAPER_READING_PATH.md](PAPER_READING_PATH.md) only after their prerequisites.
6. Use [GLOSSARY.md](GLOSSARY.md) for controlled terminology, [REFERENCE_ARCHITECTURE.md](REFERENCE_ARCHITECTURE.md) as the system map, and [FRONTIER_RESEARCH.md](FRONTIER_RESEARCH.md) for changing research that is not yet core instruction.
7. Apply the [chapter completion checklist](CHAPTER_COMPLETION_CHECKLIST.md) and the authoritative [observability](observability/OBSERVABILITY_CONTRACT.md), [evaluation/experiment](evaluation/EVALUATION_EXPERIMENT_CONTRACT.md), and [visual asset](visuals/VISUAL_ASSET_CONTRACT.md) contracts while authoring.

## Running project

**Build Your Own RAG Engine** starts with a handful of plain-text documents, explicit IDs, a hand-written search function, and no model. It gains ranking, embeddings, indexing, ingestion, hybrid retrieval, reranking, context packing, generation, specialized sources, security, and operations. Minimal request telemetry begins at V0; judged retrieval metrics begin at V2; a full baseline RAG evaluation harness is built at V10 before advanced architectures. Production versions add ingestion traces, a cost ledger, SLIs/SLOs, a working dashboard and incident diagnosis. Each upgrade begins with a failure case and keeps the old version as a baseline. Python is the default language; production libraries enter after the mechanism is visible.

## Status and scope

Phase 2 now includes Chapters 1–24, their labs, separate solutions and visual sources, plus a runnable [V0 engine](projects/V0/README.md), a [Chapter 3 measurement record](projects/V0/CHAPTER_03_MEASUREMENT.md), [Chapter 4 context probes](projects/V0/CHAPTER_04_CONTEXT_PROBES.md), the [V1 lexical index and ranking experiments](projects/V1/README.md), [V2's BM25, exact-pruning and judged-ranking stages](projects/V2/README.md), [V3's exact-vector, frozen-encoder, domain-adaptation, materialized dense and sparse/late-interaction mechanism stages](projects/V3/README.md), and [V4's Chapter 15 exact-KD/LSH, Chapter 16 IVF/PQ, Chapter 17 HNSW and Chapter 18 native/system-boundary comparisons](projects/V4/README.md). V0's answer path remains the baseline for later project versions. Later chapters and production implementation remain to be written in syllabus order. Algorithmic principles are separated from changing product details. The paper path and frontier register were checked on **2026-09-29**; each written chapter verifies its own time-sensitive claims and maintains references in [REFERENCES.md](REFERENCES.md).

The planned course has **12 parts, 28 modules, and 57 chapters**. These counts describe the current architecture, not a promise to compress topics that need more room during writing.

## Workload and remediation continuity

Headline results identify their [workload/comparison registry entry](evaluation/WORKLOAD_REGISTRY.md). Chapter 09/11/12/13 judgments use [content-bound evidence identities](evaluation/EVIDENCE_IDENTITY.md), and fresh V3/V4 runs preserve [correlated redacted request samples](observability/SAMPLE_ENVELOPE.md). Original result files and project negative results remain historical baselines. Bounded learner constructions live in the Chapter 05/06/07/08/14/15/16/17/18/19/20 labs; Chapter 12 contains the worked parameter-update bridge; completed Parts I/III/IV end with cumulative checkpoints. These are targeted repairs to the existing curriculum.

## Chapter 17

[Proximity graphs, NSW, and HNSW](chapters/chapter-17-proximity-graphs-nsw-and-hnsw.md) continues from the remediated audit checkpoint: independent frontier/diversity construction, hierarchy/insertion, exact-oracle and judged comparisons, correlated frontier replay, four reproducible figures, separate solutions and a reviewed V4 decision. The graph is experimental; exact dense and BM25 remain baselines. Chapter 18 now closes Part IV with the native/system-boundary stage below.

## Completed Part IV / Chapter 18

[Disk ANN, benchmarks, and vector databases](chapters/chapter-18-disk-ann-benchmarks-and-vector-databases.md) adds independent logical page/cache construction, matched pinned native exact/HNSW measurements, actual snapshots/bytes, predicate-specific oracle/underfill experiments and explicit native trace-availability limits. V4 preserves the inspectable Chapter17 route and all historical results. The chapter/lab includes the required cumulative architecture, cross-chapter reasoning, running-project comparison and delayed teach-back with a separate rubric. Native small-workload results retain exact/BM25; no database service or answer-quality gain is claimed. Chapter19 now starts V5 with the source-quality stage below.

## Chapter 19 / V5 source quality

[Source ingestion and document quality](chapters/chapter-19-source-ingestion-and-document-quality.md) adds three bounded format adapters, canonical source/version/content/locator identity, normalization inputs, policy-before-read, quality quarantine, exact duplicate aliases and an independently constructed source-span mapper. The registered eight-probe extraction experiment retains missing scan evidence and unchanged source Hit@1 alongside improved preservation/traceability. [V5](projects/V5/README.md) starts with canonical artifacts; V0-V4 and historical results remain intact. Lab, separate solutions, three reproducible figures and author review are complete. Chapter20 now completes V5 below.

## Chapter 20 / completed V5 source and segmentation

[Chunking as a retrieval design decision](chapters/chapter-20-chunking-as-a-retrieval-design-decision.md) adds independent window construction, source-bound evidence judgments, six exact-dense boundary configurations and shared-child parent expansion. The frozen workload distinguishes candidate coverage, packed evidence and duplicate positions; large units/parents retain negative budget outcomes. V5 preserves Chapter19's source artifacts/quarantines and all earlier results. Four figures, lab/solutions, trusted snapshots, tests and author review are included. Chapter21 now starts V6 below.

## Chapter 21 / V6 governed metadata

[Metadata schemas and filtered retrieval](chapters/chapter-21-metadata-schemas-and-filtered-retrieval.md) adds independent typed selection, trusted-principal authorization before scoring, exact date/ID/language/tenant task predicates, four measured exact filter plans and an authorized task-bridge demonstration. [V6](projects/V6/README.md) retains source/locator/metadata/policy-bound qrels, actual vectors, eligible oracles and inherited context/packing telemetry. Shortlist failures and cutoff ceilings remain explicit; no longitudinal V5 gain or live service/answer claim is made. Lab, separate solutions, four figures, tests and author review are included. Chapter 22 now completes V6 below.

## Chapter 22 / completed V6 and Part V

[Freshness, versions and incremental indexes](chapters/chapter-22-freshness-versions-and-incremental-indexes.md) adds independent revision/tombstone construction, source/version-bound current and historical evidence, actual event replay, known-pending publication gaps and tail-validated migration/rollback. [V6](projects/V6/README.md) preserves earlier snapshots and common query/ingestion/cache traces. A same-dimensional input-contract mismatch is rejected before scoring; caches bind tenant/policy/source/index/task identity. Lab, solutions, four visuals, tests and author review include the cumulative Part V architecture, cross-chapter reasoning, running-project comparison and delayed teach-back. Chapter 23 continues below.

## Chapter 23 / beginning V7

[Normalize, classify, route, and contextualize queries](chapters/chapter-23-normalize-classify-route-and-contextualize-queries.md) adds independent five-kind routing, original-query retention, typed time/ID/reference slots, current-grant gates and bounded actual lexical/dense fallback. [V7](projects/V7/README.md) compares all-dense, interpreted dense and rule routing on registered source-bound workloads, retains the quantity false trigger and route tie, and preserves parent/child/packing traces. Lab, solutions, four editable figures, tests and author review complete this frozen checkpoint. SQL/graph/web and generation remain unrun; Chapter 24 continues below.

## Chapter 24 / bounded reformulation

[Rewrite, expand, and decompose queries](chapters/chapter-24-rewrite-expand-and-decompose-queries.md) adds independently constructed admission/readiness, feedback geometry, frozen-intent paraphrase/hypothetical representations and visible fan-out/dedup/cap/packing boundaries. [V7](projects/V7/README.md#chapter-24--bounded-reformulation-checkpoint) preserves its Chapter 23 baseline and registers a richer source-bound workload. Multi-query ties original recall with about three times the scoring work; author-written hypothetical passages lose evidence through topic drift. Lab, separate solutions, five editable figures, tests and author review complete the checkpoint. No live query/answer generator or score fusion ran. Chapter 25 remains unstarted.
