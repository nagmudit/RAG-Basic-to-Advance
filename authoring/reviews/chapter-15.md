# Chapter 15 technical and pedagogical review — 2026-10-01

## Technical review

- **Oracle and metric:** V4 loads Chapter 13's checksum-validated float32 snapshot, reuses its pinned model and support-team roster, then normalizes the stored vectors for KD L2 and LSH cosine. For unit vectors, `||q−d||²=2−2cos(q,d)` gives rank-equivalent L2/cosine. The KD tree preserves every checked ordered top two on the 14 V0 queries and all 120 synthetic queries; it is exact branch-and-bound, not ANN. Stable ID ties and a conservative strict prune condition are tested. The synthetic full scan materializes score pairs before bounded-heap top-*k*; its Python timing is not a vectorized production baseline.
- **Bounds and probabilities:** KD boxes compute the Euclidean distance from the query to the box as a lower bound; the four-point `k=1`/`k=2` example correctly distinguishes a legal prune from needed backtracking. Ball lower bound `max(0,||q−c||−r)` follows the triangle inequality and is derived, with no ball-tree code or benchmark claimed. Charikar's Gaussian sign hash has one-bit collision `1−θ/π`; concatenated bits/tables require independent planes. The Chapter 15 code uses seeded independent Gaussian planes and exact-match bucket probes, then original cosine scoring. Empty unions remain empty.
- **Measured evidence:** Six synthetic `N×d` cases each have 20 fixed planted queries and 60 warm randomized-order search samples/method. They measure exact-neighbor recall, not relevance. In `d=2`, KD scores roughly 8–9 vectors and is faster than Python scan; in `d=32`, KD scores nearly all vectors and is slower. Four-table/six-bit LSH at `N=2048,d=32` has `.225` mean exact-neighbor Recall@2. The V0 path keeps Chapter 13's 14 questions/168 complete qrels and evaluates a predeclared `3×3` table/bit grid. Exact/KD macro evidence Recall@2 is `.792`; two-table/four-bit LSH is `.292` with exact-neighbor recall `.357`. Eight-table/four-bit LSH reaches the same aggregate qrel recall but only `.786` exact-neighbor recall and slower search. The Chapter 13 questions are inspected regressions, not fresh held-out model-selection evidence.
- **Operation and observability:** Record includes source/model/index/qrel and code hashes, seeds/settings, build times, query-encode times, warm search-only samples with nearest-rank p50/p95, per-query raw candidate scores/IDs, context IDs, stage status, eligible/scored counts, bucket work, exact-neighbor overlap and qrel metrics. All generation fields remain null. D10 is stored but excluded before V0 candidate scoring/context; the KD roster is prefiltered. Static scope is not authentication; no live ACL, deletes, caches, shards or service tails are claimed. Derived vectors/hash buckets inherit source privacy, licensing and retention obligations.
- **Primary sources:** [Bentley](https://cs.wmich.edu/gupta/teaching/cs6310/lectureNotes_cs6310/kdtree-bentley.pdf), [Omohundro](https://steveomohundro.com/wp-content/uploads/2009/03/omohundro89_five_balltree_construction_algorithms.pdf), [Charikar](https://www.cs.princeton.edu/courses/archive/spr04/cos598B/bib/CharikarEstim.pdf), [Beyer et al.](https://research.cs.wisc.edu/techreports/1998/TR1377.pdf), and the [maintained scikit-learn neighbor guide](https://scikit-learn.org/stable/modules/neighbors.html) were checked on 2026-10-01. The paper path and [reference table](../../REFERENCES.md) state what is and is not transferred into the toy implementation.

## Pedagogical and visual review

- The chapter starts from Chapter 13's exact scan and asks which comparisons can safely be skipped. Exact KD, exact ball bounds and approximate LSH appear in dependency order. The same candidate/evidence/answer and index/query boundaries from previous chapters remain visible. The negative V0 result is retained instead of presenting fewer comparisons as automatic speed or relevance gain.
- Figure 15.01 is computed from the same fixed two-dimensional code fixture in all three panels: exact IDs `08,07`, KD split lines and an LSH candidate union containing only `08`. The dashed boundary is labeled as one of eight planes. The first rendering had colliding point labels and a bottom note; the corrected SVG/PNG was inspected for legibility, contrast and accurate arrows/geometry. Figure 15.02 reads the final checked experiment record; its first rendering had crowded log ticks, which were removed. The final plot labels axes, units, sample population and fixed LSH settings, and was visually inspected. Both have editable Python sources and alt text; no generated illustration was needed.
- The lab makes the learner prove a prune, derive the collision probability, read per-query candidate losses, compare table/bit axes, and propose an independent experiment. Separate solutions give arithmetic, IDs, measured denominators and an explicit negative deployment decision. Active recall and a mastery target close the chapter. Ball-tree coding is **N/A** here because the proof and comparison serve the conceptual role; a second tree implementation would not change the measured KD/LSH decision.

## Chapter completion checklist

### Learning and mechanism

- [x] Exact scan cost and Chapter 13 baseline motivate the chapter; Chapters 10–13 and Chapter 14's representation/execution distinction are explicit.
- [x] Exact-neighbor recall, KD/ball bounds, backtracking, random hyperplanes, table/bits and candidate union are defined and added to the glossary.
- [x] Index build, query encoding, bucket/probe/refinement, candidate/context/answer paths are distinguished.
- [x] KD and ball numerical bounds, LSH collision arithmetic, normalization, units, ties and empty bucket edge case are worked.
- [x] Pseudocode and from-scratch KD/LSH code precede library comparisons; ball implementation N/A for the reason above.
- [x] Scan, tree, LSH, raw vector/signature/plane costs and measured stage latency are bounded with implementation limitations.
- [x] Alternatives, high-dimensional caveats, negative results and Chapters 16–17 dependencies are explicit.

### Evidence and operation

- [x] The checked record states question, hypothesis, baseline, variables/controls, frozen data/qrels, factorial settings, procedures, versions, results, failures, conclusion and limitations.
- [x] Exact-neighbor and judged evidence recall are separate; context IDs and unrun generation are explicit.
- [x] Build/query timing, work, bucket reason, trace IDs/versions, raw ranks/scores and static-scope eligibility are captured.
- [x] `style-ticket`, acronym, metadata-ID and no-evidence failures localize approximation versus representation versus authorization/answerability.
- [x] D10, derived-index privacy/retention and absent real ACL lifecycle are named.

### Visual and practice

- [x] Visual audit selected a shared two-dimensional execution comparison and one measured work/quality plot.
- [x] Both figures have numbers, titles, takeaway captions, alt text, editable scripts, SVG/PNG, axes/units, fixed seeds/data and uncertainty limits.
- [x] Final PNGs were inspected against code/record after fixing label and tick overlap.
- [x] Worked lab, solutions, design/interview question, V4 update, active recall and mastery target are present.

### Release hygiene

- [x] Chapter/lab/solutions/V4/visual links and cross-file counts/numbering resolve in fifteen-chapter preflight.
- [x] Primary research, current library guidance, and time-sensitive citations were verified on 2026-10-01; frontier claims are excluded.
- [x] V0–V4 tests, checked record hashes/parity, plot reproduction, reference audit and manuscript preflight pass; negative result remains visible.
- [x] Chapter, lab, solutions, code/tests/experiment, visual source/renderings, documentation and review are committed together.
