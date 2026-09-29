# Retrieval-Augmented Generation: a curriculum architecture

This repository contains the architecture and the beginning of a textbook and laboratory course on retrieval-augmented generation (RAG). The central engineering question is: **when a user asks a question, which evidence should enter the model's context, and why?**

The intended reader can program at a basic level but may know no information retrieval, vector search, language-model internals, or distributed systems. The path begins with a tiny searchable corpus and ends with the ability to design, evaluate, secure, and scale a multi-source retrieval platform. The book treats RAG as a knowledge-access system: lexical search, structured queries, graph traversal, web retrieval, multimodal retrieval, and dense vectors all have distinct roles.

## What completion means

You should be able to build key algorithms from scratch, trace a query through each stage, measure retrieval separately from answer quality, diagnose failures with evidence, instrument and operate the service, justify architecture choices under latency, cost and permission constraints, and read major research papers critically. Completion is demonstrated by a capstone and a final assessment, not by finishing a framework tutorial. The book uses precise diagrams, reproducible plots and selective conceptual illustrations as teaching tools.

## How to use this repository

1. Read [TEACHING_PHILOSOPHY.md](TEACHING_PHILOSOPHY.md) for the learning contract and [KNOWLEDGE_MAP.md](KNOWLEDGE_MAP.md) for prerequisites.
2. Follow the numbered chapters in [SYLLABUS.md](SYLLABUS.md), beginning with [Chapter 1 — A question, a model, and missing evidence](chapters/chapter-01-a-question-a-model-and-missing-evidence.md), [Chapter 2 — Build the first RAG loop](chapters/chapter-02-build-the-first-rag-loop.md), [Chapter 3 — Data, algorithms, and measurements](chapters/chapter-03-data-algorithms-and-measurements-needed-for-search.md), [Chapter 4 — What an LLM does with supplied context](chapters/chapter-04-what-an-llm-does-with-supplied-context.md), [Chapter 5 — Text normalization and inverted indexes](chapters/chapter-05-text-normalization-and-inverted-indexes.md), [Chapter 6 — TF-IDF and vector-space ranking](chapters/chapter-06-tf-idf-vector-space-ranking-and-lexical-limits.md), and [Chapter 7 — BM25 and other lexical ranking models](chapters/chapter-07-bm25-and-other-lexical-ranking-models.md). Chapter entries specify the lab and mastery target that later writing must satisfy.
3. Use [ROADMAP.md](ROADMAP.md) to choose a pace. Every pace covers the same material.
4. Evolve one engine using [PROJECT_ROADMAP.md](PROJECT_ROADMAP.md). Record each version's retrieval and answer metrics before replacing a component.
5. Build the core evaluation harness in Chapters 30–33, then apply it to [CASE_STUDIES.md](CASE_STUDIES.md). Enter the tracks in [PAPER_READING_PATH.md](PAPER_READING_PATH.md) only after their prerequisites.
6. Use [GLOSSARY.md](GLOSSARY.md) for controlled terminology, [REFERENCE_ARCHITECTURE.md](REFERENCE_ARCHITECTURE.md) as the system map, and [FRONTIER_RESEARCH.md](FRONTIER_RESEARCH.md) for changing research that is not yet core instruction.
7. Apply the [chapter completion checklist](CHAPTER_COMPLETION_CHECKLIST.md) and the authoritative [observability](observability/OBSERVABILITY_CONTRACT.md), [evaluation/experiment](evaluation/EVALUATION_EXPERIMENT_CONTRACT.md), and [visual asset](visuals/VISUAL_ASSET_CONTRACT.md) contracts while authoring.

## Running project

**Build Your Own RAG Engine** starts with a handful of plain-text documents, explicit IDs, a hand-written search function, and no model. It gains ranking, embeddings, indexing, ingestion, hybrid retrieval, reranking, context packing, generation, specialized sources, security, and operations. Minimal request telemetry begins at V0; judged retrieval metrics begin at V2; a full baseline RAG evaluation harness is built at V10 before advanced architectures. Production versions add ingestion traces, a cost ledger, SLIs/SLOs, a working dashboard and incident diagnosis. Each upgrade begins with a failure case and keeps the old version as a baseline. Python is the default language; production libraries enter after the mechanism is visible.

## Status and scope

Phase 2 now includes Chapters 1–7, their labs, separate solutions and visual sources, plus a runnable [V0 engine](projects/V0/README.md), a [Chapter 3 measurement record](projects/V0/CHAPTER_03_MEASUREMENT.md), [Chapter 4 context probes](projects/V0/CHAPTER_04_CONTEXT_PROBES.md), the [V1 lexical index and ranking experiments](projects/V1/README.md), and [V2's Chapter 7 BM25 stage](projects/V2/README.md). V0's answer path remains the baseline for later project versions. Later chapters and production implementation remain to be written in syllabus order. Algorithmic principles are separated from changing product details. The paper path and frontier register were checked on **2026-09-29**; each written chapter verifies its own time-sensitive claims and maintains references in [REFERENCES.md](REFERENCES.md).

The planned course has **12 parts, 28 modules, and 57 chapters**. These counts describe the current architecture, not a promise to compress topics that need more room during writing.
