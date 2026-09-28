# Teaching philosophy

## The recurring question

At each stage, answer: **How did these particular pieces of evidence become the model's context?** Start with `question → search → evidence → answer`. Add transformations, indexes, filtering, ranking, and verification only when the learner can explain the failure that motivates each addition.

## Progression

Each chapter starts with an observable problem. Introduce an intuitive model, define terms, trace data at index and query time, derive only the mathematics needed, calculate a tiny numerical example, implement the mechanism, and then inspect a production analogue. Compare alternatives using quality, latency, cost, memory, freshness, and operational complexity. An analogy is temporary scaffolding; state where it fails.

The dependency graph is binding. For example, postings precede BM25 and dynamic pruning; vectors and similarity precede embeddings and retriever training; exact KNN precedes ANN; graph traversal precedes graph-based RAG; relevance labels precede ranking metrics; authentication and authorization precede multi-tenant retrieval. The full baseline RAG evaluation harness is taught before advanced architectures are attempted. Chapters may preview future terms, but may not require them.

## Theory and implementation

Build tokenization, an inverted index, TF-IDF, BM25, one safe top-k pruning method, vector similarity, exact KNN, illustrative ANN, chunkers, RRF, a reranking funnel, metric functions, graph traversal, and a bounded retrieval loop in small Python programs. Then map each to library or service implementations and document what the abstraction hides. Frameworks arrive in Part XII. Numerical examples use small corpora and show intermediate values, assumptions, units, and edge cases. Complexity claims distinguish worst-case guarantees from empirical behavior.

## Visuals and experiments

Use a diagram when data movement or structure is hard to retain: posting lists, chunk boundaries, vector geometry, HNSW layers, IVF cells, retrieval funnels, evidence provenance, and distributed query paths. Use Mermaid for flows and ASCII or plotted figures for geometry. Every major diagram must identify index-time and query-time steps. Experiments change one variable at a time, save the query set and relevance judgments, compare a baseline, and report variance where appropriate. Counterexamples matter: exact identifiers, rare acronyms, stale pages, contradictory sources, and unauthorized hits.

## Chapter contract

A written chapter will include its motivation, prerequisite recap, mental model, mechanism, mathematics where useful, worked example, visualization, from-scratch implementation, production mapping, trade-offs, failure and debugging guide, exercises, project upgrade, recall prompts, and further reading. Do not force empty sections into chapters where a component does not apply. Every chapter ends with **“You understand this chapter if you can…”** and observable abilities: explain, calculate or implement, compare, and debug.

Labels mark depth, not reader status: `[FOUNDATIONAL]`, `[INTERMEDIATE]`, `[ADVANCED]`, `[PRODUCTION]`, and `[RESEARCH]`. Optional advanced boxes can be deferred without breaking prerequisites.

## Practice and retention

Each module mixes recall, explanation, reasoning, numerical, coding, debugging, design, and where appropriate research tasks. Solutions live separately after the learner has attempted the task. Revisit old concepts through cumulative quizzes at the end of every part, flashcards scheduled approximately after 1, 3, 7, and 21 days, architecture sketches from memory, and comparisons of the latest engine against V0. Interview questions are oral defenses of a design decision, not vocabulary tests.

## Evaluation of learning and systems

The learner is assessed on both a running implementation and its reasoning: unit-level calculations, retrieval judgments, error analysis, security tests, latency budgets, and a written architecture defense. The final exam includes theory, numerical ranking, code, diagnosis, system design, paper critique, and teaching a novice. System evaluations keep retrieval, answer, and end-to-end measures distinct; an answer that sounds plausible cannot rescue missing or unauthorized evidence.

## Revision policy

After each part, review knowledge continuity, code continuity, terminology, exercises, architecture, and new research. Historical papers explain ideas, while product and model claims are checked against current primary documentation when chapters are written. Report uncertainty and dataset-specific findings rather than universal winners.
