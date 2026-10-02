# Visual teaching and asset contract

Each chapter audits its significant concepts: would a diagram, plot, table, annotated algorithm, timeline, or illustration materially improve understanding? Make the smallest visual that answers a specific learner question. A dense chapter may need many figures; a simple one may need few. Visuals progress from `question → search → evidence → answer`, through multi-stage ranking, to production services and telemetry. Never use a generated image as the authority for an exact algorithm, formula or number.

## Choose the medium by teaching purpose

| Medium | Use for | Source to retain |
|---|---|---|
| Mermaid | Exact flow, dependencies, architecture, sequence, state machines, graph traversal, query/ingest path | Editable `.mmd` or fenced block |
| Reproducible programmatic plot | Numerical geometry, TF/IDF/BM25, score distributions, ANN quality/latency, chunking, candidate depth, latency histograms, cost and drift | Script, inputs or generation recipe, units and environment |
| Table | Exact metric definitions, parameter comparisons, failure matrices and decisions | Editable Markdown/source data |
| ASCII or annotated code | Tiny posting lists, memory layout, traversal trace and line-by-line mechanism | Chapter source |
| Generated conceptual illustration | Intuition that precise media cannot convey as well, such as HNSW roads/highways or embedding neighborhoods | Prompt, model/date if known, output, purpose and revision note |

Use image generation only if it teaches something Mermaid, code, a table or a plot cannot communicate better. If unavailable, retain an illustration specification; do not add a decorative placeholder. Split unreadable Mermaid into smaller figures. Prefer a plot computed from explicit data over an image that merely looks quantitative.

## Figure register and directory convention

Assets live under `visuals/chapter-NN/` **when that chapter is authored**; create no empty chapter directories now. Use `figure-NN-SS-slug.mmd`, `plot-NN-SS-slug.py` plus small data as needed, or `illustration-NN-SS-slug.png` with matching prompt/specification. `NN` is the current two-digit chapter number and `SS` is sequence within that chapter. Reference assets by relative links in chapter text. Every substantial visual has **Figure NN.SS — title**, a caption that states the takeaway and boundary/assumption, alt text describing the essential relationship, editable source path, and chapter association. Plots also state axes, units, dataset, seed and uncertainty where relevant. If the file changes, update the figure record and chapter citation together. Screenshots of tools should include version/date and should not replace editable source.

## One diagram language

- User/input: rounded entry node; sources/indexes: cylinder or clearly labeled store; processing/retriever/ranker/context/generator: rectangular action nodes; decision/policy: diamond; evaluation/telemetry: sidecar or separate control-plane lane; external tools: bordered external lane.
- Solid arrows show data or execution direction and have labels when ambiguity is possible. Dashed arrows show feedback, monitoring or optional control. Separate **INDEX TIME** and **QUERY TIME** lanes and mark when a live source crosses them. Preserve candidate → selected evidence → answer as distinct node types and labels.
- Use consistent stage names: query processing, eligibility, lexical/vector/source retrieval, fusion, reranking, context construction, generation, verification, response. Authorization is a gate. Accessible colors may reinforce these types but meaning must survive grayscale and screen readers.
- Never invent a new shape meaning silently. Put a legend on nontrivial figures. Avoid a single unreadable everything diagram.

## Technical accuracy and chapter visual audit

Before acceptance, compare every arrow, ordering, label, layer, formula, number, parameter name and index/query distinction against the prose, pseudocode and executable trace. Verify diagram examples with the same toy data used by the chapter. Check alt text, caption, legibility at normal reading size, source reproducibility, contrast and chapter/figure numbering. Generated illustrations may use analogy, but their captions must say where the analogy stops. An algorithmic diagram is reviewed as carefully as code. Record the visual audit in [the chapter checklist](../CHAPTER_COMPLETION_CHECKLIST.md).

## Chapter 17 authored visual audit

The optional Phase 1.6 visual plan has become four focused assets: [17.01 frontier/local minimum](chapter-17/figure-17-01-frontier.svg), [17.02 actual hierarchy/descent](chapter-17/figure-17-02-hierarchy.svg), [17.03 exact diverse-neighbor geometry](chapter-17/figure-17-03-diversity.svg), and [17.04 measured recall/work/p95/payload](chapter-17/figure-17-04-quality-cost.svg). The chapter retains captions, alt text, SVG/PNG, editable sources, hand coordinates/actual adjacency and registered plot data. Exact scan and partition/compression mechanisms are already visible in prerequisite chapters; the new diagrams teach the new graph state. A roads/highways generated illustration is N/A because explicit layered adjacency communicates the same intuition while preserving exact traversal. Three parameter roles, memory arithmetic and a missed-neighbor trace also have editable chapter tables. No empty assets or decorative placeholders are required.
