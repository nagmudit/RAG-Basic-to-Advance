# Chapter 10 technical and pedagogical review

**Reviewed:** 2026-09-30. **Artifacts:** [chapter](../../chapters/chapter-10-vectors-distance-and-exact-similarity.md), [lab](../../labs/chapter-10/LAB.md), [solutions](../../solutions/chapter-10-solutions.md), [V3 project](../../projects/V3/README.md), [exact code](../../projects/V3/exact_vectors.py), [judged experiment](../../projects/V3/chapter-10-experiment.json), [tests](../../projects/V3/test_exact_vectors.py), [visual source](../../visuals/chapter-10/plot-10-01-metric-geometry.py).

## Technical review

- **Arithmetic:** For `q=(1,0)`, `C=(.8,.6)`, dot `.8`, norm `1`, cosine `.8`, L2 `sqrt(.4)`, L1 `.8`. Dot `B>A>C>D`, cosine `A=B>C>D` resolved by ID, L2 `A<C<B<D`. Figure 10.01's table is computed from the same `ExactIndex`; the caption does not claim high-dimensional behavior. The normalized L2/cosine identity states its nonzero/unit assumptions. Raw vector size `10^6×768×4=3,072,000,000` bytes is checked against the GiB conversion.
- **Algorithm:** All four metrics score all eligible items; `sort` and `heap` have identical raw results on toy cases. The scope gate runs before scoring, so private P and V0 legal-only D10 do not enter support-team score work or context. The heap changes selection complexity, not `O(Nd)` scoring. The teaching implementation retains an `O(N)` eligible list, disclosed in the chapter and solution. It rejects zero cosine, nonfinite coordinates, wrong dimensions, duplicate IDs and invalid *k*; its lexical wrapper reports an explicit zero-in-vocabulary no-result policy. Real authentication and numeric-kernel parity are outside this fixture.
- **Experiment integrity:** V0 source and V1 analyzer/segment IDs remain fixed; V2 qrels loader checks snapshot and all 12 eligible IDs. The 14-query/168-pair record stores method order seed, raw search-only samples, candidate/raw score/context/stub fields, qrel metric conventions, hashes, scope and version. The hypothesis fails: top-two macro NDCG BM25 `.899686`, binary cosine `.772408`. Termination and dated-contract examples were inspected against grade-2 IDs and context/stub outcomes. The representation/scorer change is bundled, so the result is a system comparison and is **not** attributed to one feature or claimed to generalize to learned embeddings. Local p95 is labeled as local, not service tail evidence.
- **Reference audit:** Stanford IR text supports term vectors/cosine/exact score work; scikit-learn documentation supports the brute-force query-cost distinction; NumPy documentation supports matrix multiplication/norm as a production analogue. All are primary/official sources in [REFERENCES.md](../../REFERENCES.md). No new benchmark or model-performance claim appears.
- **Security and observation:** Static scopes are named as fixtures, never authenticated users. Experiment records IDs and numeric scores without private query/source text; a real trace requires protected IDs and bounded retention. The chapter keeps source/index version, candidates, selected context and stub status distinct. No external data, license, retention or model call is added; ingestion lifecycle events and monetary model-cost accounting are **N/A** for this static numeric stage.

## Pedagogical review

- The opening uses a measured lexical failure without suggesting that arbitrary coordinates fix paraphrase. It revisits Chapter 6 sparse lexical vectors and Chapter 9 qrels, teaches the numeric mechanism before naming a future encoder, and postpones ANN until the exact oracle exists. Figure 10.01 answers why magnitude and metric alter order. A hand calculation, table and executable plot agree; the two-dimensional analogy's limit is stated next to it.
- The project exercise carries V2's frozen judged comparison forward, retains a negative result, identifies which direct span disappeared, and separates exact-neighbor correctness from relevance, context coverage and answer support. The lab requires arithmetic, independent code, debugging, experiment interpretation and a scale/design defense. Solutions include intermediate values, query-level failure diagnoses and a working small reference implementation.
- The glossary distinguishes dense storage from learned embedding, exact neighbor from judged evidence, and cosine from probability. The roadmap and knowledge map now put exact KNN before encoder training. Chapter 11 is unlocked but not written.

## Chapter completion checklist

### Learning and mechanism

- [x] Observed V2 failure and binding Chapter 3/6/9 prerequisites motivate the vector oracle.
- [x] Coordinate schema, dimension, sparse/dense, norm, normalization, anisotropy, four metrics and zero policy are defined and registered.
- [x] Index-time storage/unit normalization and query-time validation, eligibility, scoring, selection, context boundary are traced.
- [x] Formulas, assumptions, score direction, hand example, numerical table, tie rule, zero/nonfinite/dimension cases are explicit.
- [x] Pseudocode and standard-library full-scan implementation precede matrix/BLAS and future ANN abstractions.
- [x] `O(Nd)` scoring, sort/heap selection, Python eligible-list memory, batch score-matrix memory and raw float32 storage are bounded.
- [x] Metric alternatives, sparse-postings comparison, misconception and Chapter 11/ANN dependencies are explicit.

### Evidence and operation

- [x] Falsifiable question/hypothesis, BM25 baseline, changed binary-vector system, fixed corpus/analyzer/qrels/scope, seeded procedure, samples, metrics, errors, conclusion and limits are recorded.
- [x] Candidate IDs, selected context IDs, grade-2 coverage, limited V0 stub status and absent general answer judgment are separate.
- [x] Version/hash fields, score/work counters, search-only latency distribution and protected trace guidance are included. Lifecycle events and paid-model costs are N/A for a frozen offline stage.
- [x] Termination, contract-change, zero-query, zero-positive plausible candidates and restricted D10 cases provide debugging and negative examples.
- [x] Eligibility precedes scoring; scope fixture/authentication distinction and safe trace/retention implications are stated.

### Visual and practice

- [x] Visual audit chose one programmatic geometry/order plot; the exact formulas and metric trade-offs remain in a table.
- [x] Figure 10.01 has number, caption/takeaway, alt, editable script, SVG/PNG, axes/units, fixed data and no-randomness note.
- [x] Plot values/order and ID tie were checked against implementation and PNG visually inspected for legibility and contrast.
- [x] Lab, independent implementation exercise, diagnosed experiment, design defense, cumulative sketch and separate worked solutions are linked.
- [x] Recall prompts, spaced-review instruction, observable mastery statement and further primary reading are present.

### Release hygiene

- [x] Chapter/lab/project/reference/glossary/roadmap links and numbering pass the book preflight; no Chapter 11 material was authored.
- [x] Primary sources verified for 2026-09-30; no frontier model claim is promoted into core instruction.
- [x] V0/V1/V2/V3 behavioral suites, experiment reproducibility, figure render/visual inspection, hash audit and preflight pass; negative quality/latency results are retained.
- [x] Chapter, lab, solutions, code, tests, experiment, visual source/renderings, glossary, references, roadmap, architecture and this review are part of one Chapter 10 change.
