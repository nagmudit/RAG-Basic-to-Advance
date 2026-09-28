# Case-study plan

Every study uses the same review sheet: **requirements → dataset → ingestion → segmentation/metadata → indexes → candidate retrieval → reranking/context → generation → evaluation → operations → failure probes → architectural alternatives**. The expected design is a hypothesis to test, not a vendor prescription. All studies include provenance and answerability; domain-specific safety and permissions are explicit.

## 01. Company documentation assistant — enabled by Chapters 01–33, 49

- **Requirements and data:** Answer policy and product questions from Markdown, wiki, PDF, and change logs; source version and user permission matter.
- **Pipeline:** Parse headings/tables, chunk by section with parent expansion, index BM25+dense, prefilter ACL/version, rerank, cite section and effective date.
- **Evaluation and operations:** Query slices for exact policy IDs, paraphrases, conflicts, and unanswerable questions; measure citation support, update delay, and access leakage.
- **Failure/trade-off:** A superseded policy ranks highly. Compare temporal filtering with recency boost; only the former can enforce an as-of constraint.

## 02. Customer support assistant — enabled by Chapters 19–34, 49–50

- **Requirements and data:** Use knowledge articles and ticket resolutions; avoid exposing private customer tickets across accounts.
- **Pipeline:** Deduplicate templates, separate public and tenant-specific records, hybrid retrieval for error codes and symptom descriptions, rerank by product/version, escalate when no supported fix exists.
- **Evaluation and operations:** Resolution rate, unsupported suggestion rate, p95 latency, per-tenant ACL tests, feedback and article freshness.
- **Failure/trade-off:** Frequent but outdated ticket fixes dominate similarity; compare version constraints and freshness with broad recall.

## 03. Legal-document research — enabled by Chapters 05–09, 19–33, 40, 49

- **Requirements and data:** Find exact clauses and related authorities in versioned contracts, statutes, or judgments; human legal review remains required.
- **Pipeline:** Preserve section/page/footnote boundaries, exact lexical search plus dense expansion, jurisdiction/date filters, citation-chain retrieval where needed, show quoted source spans.
- **Evaluation and operations:** Clause recall, citation accuracy, currentness, redaction and privileged-document access tests.
- **Failure/trade-off:** A semantic match from a different jurisdiction looks persuasive; enforce jurisdiction as an eligibility rule, not a soft rank feature.

## 04. Medical and scientific literature — enabled by Chapters 09, 19–33, 40, 48–49

- **Requirements and data:** Synthesize from papers, abstracts, trial registries, and updates; distinguish evidence strength and publication date.
- **Pipeline:** Parse tables, study sections and citations, use controlled vocabulary plus semantic retrieval, filter study type/date, group conflicting results, include source and limitation in the answer.
- **Evaluation and operations:** Expert-labeled evidence recall, claim support, date of last search, harmful omission and uncertainty tests; domain expert review is a gate.
- **Failure/trade-off:** A preprint or retracted result outranks stronger evidence; source status and study quality require explicit handling.

## 05. Financial research assistant — enabled by Chapters 19–33, 40–41, 48–52

- **Requirements and data:** Answer questions from filings, earnings calls, and time-series tables with as-of dates and exact numeric calculations.
- **Pipeline:** Extract table structure and units, search filings lexically/semantically, route totals and comparisons to typed data/SQL, cite filing page and period.
- **Evaluation and operations:** Numeric exactness, unit conversion, temporal leakage, source lineage, reporting delay, access control and review workflow.
- **Failure/trade-off:** A text embedding retrieves a similar quarter but the wrong period; structured period filters and arithmetic checks are essential.

## 06. Codebase assistant — enabled by Chapters 05–14, 19–33, 44, 48

- **Requirements and data:** Explain implementation behavior across repository versions; follow definitions, references, tests, and call sites.
- **Pipeline:** Parse symbols and file paths, index exact names and code embeddings, use repository graph for dependencies, expand to relevant function/module context, cite file and commit.
- **Evaluation and operations:** Symbol recall, correct-version answers, cited line support, latency after commit ingestion.
- **Failure/trade-off:** A generated answer relies on an old signature; revision identity belongs in every indexed record and result.

## 07. E-commerce/product search — enabled by Chapters 05–14, 21–27, 30–33, 41, 48

- **Requirements and data:** Find products by exact SKU, compatibility, attributes, and vague natural-language needs; stock and price are structured live fields.
- **Pipeline:** BM25 for identifiers, metadata filters for brand/size/availability, dense retrieval for descriptions, hybrid fusion and learned/business-aware reranking; fetch current price from a trusted API.
- **Evaluation and operations:** Exact-SKU hit rate, attribute constraint satisfaction, conversion and latency by query slice.
- **Failure/trade-off:** Dense similarity suggests an incompatible item; hard compatibility filters must precede display.

## 08. News and current-events RAG — enabled by Chapters 22–33, 40, 48–49

- **Requirements and data:** Answer current questions using source pages with publication and event dates, corrections, and conflicting reports.
- **Pipeline:** Search and fetch live pages, canonicalize duplicates, prefer primary reporting where possible, separate event time from page update time, cross-check claims, timestamp citations.
- **Evaluation and operations:** Freshness lag, source diversity, claim support, correction propagation and source availability.
- **Failure/trade-off:** Many syndicated pages create false consensus; deduplicate by origin and claim lineage.

## 09. Enterprise multi-tenant RAG — enabled by Chapters 21–22, 30–33, 48–52

- **Requirements and data:** Millions of mixed documents, many users, document-level ACLs, hourly freshness, deletion and audits.
- **Pipeline:** Canonical permission metadata, tenant-aware partitioning, permission prefilter/ANN-aware filter, shard routing, hybrid retrieval, safe caches, versioned index cutover.
- **Evaluation and operations:** Cross-tenant probes, recall under selective ACLs, p95 latency, delete SLA, reindex recovery and per-tenant cost.
- **Failure/trade-off:** Postfiltering top-k after ANN underfills results and may leak into logs; compare filtered index strategies.

## 10. Graph-based organizational knowledge — enabled by Chapters 30–35, 38–39, 49

- **Requirements and data:** Answer “who owns what,” dependency chains, and organization-wide themes from docs, tickets, and directory records.
- **Pipeline:** Resolve entities, extract cited edges with valid time, graph traversal for local relationships, optional community summaries for global questions, retrieve original text before answering.
- **Evaluation and operations:** Edge precision/recall, path validity, global-summary coverage, extraction cost and update lag.
- **Failure/trade-off:** Homonyms merge two people; entity resolution and edge provenance matter more than graph traversal speed.

## 11. Multimodal PDF intelligence — enabled by Chapters 19–20, 28–33, 42–43, 49

- **Requirements and data:** Answer from text, scanned pages, diagrams, charts and tables in reports/manuals.
- **Pipeline:** OCR plus layout, table-cell and figure regions, page/coordinate IDs, text and visual retrieval, context that preserves axes and units, cited page regions.
- **Evaluation and operations:** Field extraction accuracy, region recall, chart-value fidelity, OCR quality, human review on low-confidence pages.
- **Failure/trade-off:** Flattening a table into reading-order text scrambles row-column relationships; preserve structure or use an image-aware path.

## 12. Billion-vector retrieval platform — enabled by Chapters 15–18, 21, 30, 48, 51–52

- **Requirements and data:** Very large vector corpus with metadata filters, high query rate, bounded p95 latency and continuous updates.
- **Pipeline:** Benchmark exact samples, compare compressed IVF/PQ, graph, and disk-resident ANN, route/shard with replicas, merge candidates, rerank, version and monitor index builds.
- **Evaluation and operations:** ANN recall vs exact neighbors, task relevance recall, bytes/vector, build/update throughput, p95/p99, filter selectivity and recovery time.
- **Failure/trade-off:** Index family wins unfiltered benchmarks but degrades under selective ACLs; workload-specific filtered benchmarks govern the decision.

## Cross-case design exercise

After Chapter 54, choose two cases with opposite constraints (for example, product search and legal research). Produce one architecture diagram, one versioned evaluation sheet and one incident trace per case. Set workload-specific retrieval, answer, latency, freshness, security and cost gates; identify the dashboard panels and alerts that would reveal the case's likely failure. Explain which components transfer, which do not, and where a simpler exact or structured operation is preferable to dense retrieval. Follow the [experiment](evaluation/EVALUATION_EXPERIMENT_CONTRACT.md), [observability](observability/OBSERVABILITY_CONTRACT.md) and [visual](visuals/VISUAL_ASSET_CONTRACT.md) contracts.
