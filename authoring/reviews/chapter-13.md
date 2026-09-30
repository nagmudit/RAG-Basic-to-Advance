# Chapter 13 technical and pedagogical review — 2026-09-30

## Technical review

- **Mechanism and versioning:** V1 segments are formatted as title/newline/body; the pinned Chapter 11 shared encoder produces normalized 384-coordinate vectors. Chapter 13 writes ordered little-endian float32 rows with source IDs, scopes, searchable-text hashes, model revision, 256-word-piece limit, pooling, metric, tie rule, payload digest and derived index version. The loader checks every row and vector before constructing the exact scorer. Index load is a startup gate; a request does not repeatedly rebuild the snapshot. A model/text/version mismatch fails closed. D10 remains stored but is excluded before support-team scoring.
- **Arithmetic and cost:** The chapter works raw dot versus cosine for `q=(1,0)`, unit `a=(.8,.6)` and longer `b=(7,7)`, with opposite rankings. A 13×384×4 float32 file is 19,968 bytes; a million rows are 1,536,000,000 raw bytes. The local exact scan scores 12×384=4,608 coordinates per support-team query, then retains top-*k*; source/model/index memory and build cost are excluded. ANN can only change the scan work, not the query encoding boundary.
- **Evidence:** The Chapter 11 in-memory and Chapter 13 reloaded indexes agree on 34/34 ordered rankings and raw scores at k=2,8. The separate 14-question Chapter 13 diagnostic set has 168 complete eligible judgments across seven two-question slices. Positive-query top-two Recall is BM25 `.708`, dense `.792`; the colloquial slice is `.5` versus `1.0`. Both routes miss the literal metadata ID, current signed SLA target, Basic numeric constraint and no-evidence rejection. The two author-translated Spanish queries are expressly exploratory, without native assessment. No answer generator runs. Candidate IDs/scores, context IDs/direct recall and absent answer labels remain separate.
- **Operation and observability:** The record separates cached-model construction after imports, batch encode throughput, snapshot build/load, warm query encoding, exact scan and BM25 search. Five warmed request samples per query/method and three fixed-order batch passes are local CPU diagnostics, with sample counts, p50/p95 and by-slice quality. Fixed batch order and tiny corpus limit throughput interpretation. Versions, raw scores, work counts, hashes, eligibility, failure examples, conclusion and decision are captured. Real authorization, atomic publication, live update/deletion and service tails remain later work; a derived restricted-source vector requires source-aligned access and retention.
- **Primary-source check:** Current official Sentence Transformers usage/semantic-search documentation, Faiss metric/flat-index documentation, and the pinned model card were checked on 2026-09-30 and recorded in [REFERENCES.md](../../REFERENCES.md). The chapter uses Faiss only as an analogue and makes no benchmark claim about it.

## Pedagogical review

- Chapter 10's exact oracle, Chapter 11's frozen model and Chapter 12's rejected adapter are explicit prerequisites. The new failure is operational ambiguity of an in-memory retriever: stale vectors, lost IDs and conflated timings. The chapter resolves that through a checked materialized index before naming later ANN or vector services.
- Figure 13.01 separates index time, startup validation and request time; Figure 13.02 uses actual qrel/candidate scores from one query and separate scales for BM25 and cosine. Both have editable scripts, SVG/PNG, alt text, takeaways and fixed-input notes; rendered PNGs were inspected for arrow order, ID labels and legibility. A table carries aggregate/slice results without suggesting statistical certainty.
- The lab requires a temporary corruption probe, metric arithmetic, complete qrel and scope audit, exact-rank parity, per-slice quality and stage timing, and narrow failure fixes. Solutions show intermediate IDs/scores and denominators. Active recall and mastery abilities connect the exact baseline to Chapters 14–15 without beginning either.

## Chapter completion checklist

### Learning and mechanism

- [x] An in-memory frozen retriever's version/ID/cost ambiguity motivates the materialized index; Chapters 9–12 are explicit prerequisites.
- [x] Materialized index, embedding contract, batch throughput, exact scan and parity are defined and registered in the glossary.
- [x] Source formatting, batch build, normalization, storage, startup validation, query encoding, eligibility, exact score, candidates and context are traced separately.
- [x] Dot/cosine arithmetic, storage/coordinate units, invalid-vector and stale-version cases are explicit.
- [x] From-scratch binary/manifest code and Chapter 10 exact scorer precede library analogues.
- [x] Index bytes, O(Nd) scan, model/build/load/query-stage timing and their excluded costs are bounded.
- [x] Failure-driven alternatives, representation/metric limits and ANN/hybrid dependencies are clear.

### Evidence and operation

- [x] The record has question, hypothesis, baseline, variable/controls, frozen corpus/qrels, slices, metrics, procedure, results, errors, conclusion, decision and limitations.
- [x] Candidate retrieval, selected context and absent new generation outcome remain distinct.
- [x] Source/model/index/qrel/code hashes, raw scores, stages, work counts, timings and version/eligibility outcomes are logged at local maturity.
- [x] Acronym/version, metadata ID, numeric entity, colloquial paraphrase, no-evidence and restricted-source probes are inspected.
- [x] D10 scope, fictional vector retention and model license/representation limits are stated.

### Visual and practice

- [x] Visual audit selected paired execution lanes and one real score trace; aggregate results use a table.
- [x] Both figures have number, caption, alt text, editable source, SVG/PNG and fixed-input/measurement notes.
- [x] The rendered PNGs were inspected; Figure 13.01's startup gate and Figure 13.02's score values agree with code and prose.
- [x] Lab, worked solutions, design/interview questions, project upgrade, active recall and mastery target are present.

### Release hygiene

- [x] Chapter, lab, solutions, V3, syllabus, README, glossary, map, architecture, observability and references are linked and numbered.
- [x] Pinned model/library guidance and primary technical sources were verified for the writing date; exploratory Spanish probes are not promoted to a multilingual claim.
- [x] V0–V3 tests, snapshot integrity/record hashes, experiment replay, figure rendering and thirteen-chapter manuscript preflight pass; shared failures remain visible.
- [x] Chapter source, lab, solutions, code/tests, qrels, binary/manifest, experiment, visual source/renderings, documentation and review are committed together.
