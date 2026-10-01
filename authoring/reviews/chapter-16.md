# Chapter 16 technical and pedagogical review — 2026-10-01

## Technical review

- **Mechanism and parity:** [Chapter 16](../../chapters/chapter-16-ivf-quantization-and-compressed-vectors.md) holds Chapter 13's normalized-vector, scope, snapshot, metric and top-two oracle fixed. [Pure-Python code](../../projects/V4/ivf_pq_ch16.py) trains coarse centroids from a declared indexed-vector sample, assigns each row once, trains residual subspace codebooks, probes nearest centroid lists, gates eligibility before scoring and compares IVF-Flat, per-list ADC and top-`R` exact refinement. All-list IVF-Flat matches ordered exact top two for every synthetic and V0 question in the [checked record](../../projects/V4/chapter-16-experiment.json). The proof in prose correctly makes IVF-Flat geometric recall equal to oracle-list coverage under the same exact metric and tie rule. No claim is made that a centroid is a relevance label or that all-list PQ is exact.
- **Arithmetic and bytes:** Figure 16.01's separate unnormalized example uses `x=(1.4,1.7)`, `c=(1,0)`, residual `(.4,1.7)`, codewords `(.5,2)`, reconstruction `(1.5,2)` and squared reconstruction error `.10`; query `(1.2,1.8)` has exact `.05` and reconstructed `.13` squared distance. The 1,024-by-32 synthetic example has 8 two-bit code indices (2 packed bytes/vector), 2,048 code bytes, 8,192 numeric-ID bytes, 2,048 coarse-centroid bytes and 512 codebook bytes. Payload lower bounds are 138.0 KiB IVF-Flat, 12.5 KiB compressed-only PQ and 140.5 KiB PQ retaining raw originals; these exclude Python object/layout overhead and are not measured RSS. The record also captures mean squared reconstruction error `.565` on the large synthetic set. Exact refinement requires originals and cannot recover an unprobed or below-`R` ID.
- **Experiment and error sites:** The [runner](../../projects/V4/experiment_ch16.py) freezes two planted synthetic workloads (16 questions each, no relevance labels) and the existing fourteen V0 diagnostic questions/168 complete judged pairs. The latter were inspected in Chapter 13 and all twelve eligible vectors train this toy V0 index; no held-out gain is claimed. Variable settings `nprobe=1/2/4/all` for synthetic and `1/2/3` for V0 keep centroids/codebooks fixed per workload. Two randomized-order warm search-only samples/query, build time, V0 query-encode time, per-query candidate/context IDs, approximate scores, list coverage, exact-neighbor and qrel recall, list sizes, payload bounds, version hashes, source/model/qrel manifests and null generation outcomes are saved. The record names `spanish-fee` coarse then compression loss, `code-segment` shortlist and exact-ID-route failures, `acronym-sla` source/representation failure and `none-private` eligibility/no-answer boundary. No LLM, answer judge or citation metric runs.
- **Measured decision:** On `N=1024,d=32`, all-list Flat recall is `1.000`, all-list ADC `.125`, top-eight refinement `.375`; one-list Flat `.313`. In inspected V0, one-list Flat judged macro Recall@2 falls `.792→.708`; all-list ADC matches `.792` aggregate qrel recall while geometric recall is `.500`, and top-four refinement reaches `.875` aggregate qrel recall while geometric recall is `.714`. Those small, already inspected qrels and inadequate V0 codebook sample do not support replacing the exact route. The local all-list Flat/ADC search medians exceed exact's `.405 ms`, with separate model query encode median `10.141 ms`. The negative decision is preserved in the chapter and [V4 README](../../projects/V4/README.md).
- **Operation and scope:** Source/model/index/codebook version compatibility, centroid training bias, list imbalance, insert/tombstone/rebuild limits, original-vector fetch cost, raw/codebook retention, derived-data licensing, trusted policy gating and tenant-safe caches are explicit. V0 excludes legal-only D10 before training and query scoring; a static scope string is never called authentication. The recommended protected trace distinguishes probed lists, eligible/scored counts, ADC shortlist, refined results and context, with no raw private questions in metric labels. Distributed list ownership and atomic cutover remain for later production chapters.
- **Primary evidence:** [Jégou, Douze & Schmid](https://doi.org/10.1109/TPAMI.2010.57), the maintained [Faiss index map](https://github.com/facebookresearch/faiss/wiki/Faiss-indexes) and [FAQ](https://github.com/facebookresearch/faiss/wiki/FAQ), and [Johnson, Douze & Jégou](https://arxiv.org/abs/1702.08734) were checked on 2026-10-01. Paper and library performance numbers are not imported into this local Python experiment. The chapter and [reference register](../../REFERENCES.md) state the transfer limits.

## Pedagogical and visual review

- The chapter starts with Chapter 15's unsolved exact-scan cost, teaches coarse assignment before PQ, then decomposes loss using exact → IVF-Flat → ADC → top-`R` refinement. A four-method comparison holds representation, scope and oracle fixed. The numerical PQ example exposes approximate-score error; the separate V0 failure trace shows why geometric recall, judged evidence, context and answer are different layers.
- [Figure 16.01](../../visuals/chapter-16/figure-16-01-cells-and-codes.svg) is computed from sixteen actual fixed unit-circle points, four trained centroids and the same query/one-probe/two-probe code used in the test: exact `01,02`, one-probe `01,00`. Its right side explicitly labels independent unnormalized hand arithmetic. [Figure 16.02](../../visuals/chapter-16/figure-16-02-quality-cost.svg) reads the final checked record, includes units, sample count, seed, settings and byte-accounting limits. Both PNGs were inspected at full size for labels, contrast, geometry and caption accuracy; editable scripts and alt text are retained. An image-generation illustration is **N/A** because programmatic geometry, arithmetic and measured plots answer the learner questions precisely.
- The [lab](../../labs/chapter-16/LAB.md) asks learners to prove the all-list parity, calculate residual code and byte costs, plot recall/latency/storage, distinguish coarse from compression/shortlist loss, trace V0 qrel examples and design a migration. [Separate solutions](../../solutions/chapter-16-solutions.md) include arithmetic, record values, IDs and a negative deployment decision. Practice, active recall, interview and mastery criteria close the chapter.

## Chapter completion checklist

### Learning and mechanism

- [x] Chapter 15 exact/LSH results motivate IVF and PQ; Chapters 10, 13 and 15 are binding prerequisites.
- [x] IVF, centroids, `nlist/nprobe`, scalar/PQ quantization, residual, codebooks, ADC, coverage, reconstruction and refinement are defined in text and [glossary](../../GLOSSARY.md).
- [x] Index-time training/assignment/encoding and query-time probing/ADC/refinement are separate in prose, pseudocode and figures.
- [x] Mathematical distance/byte formulas, a hand-calculated residual example, normalization limits, ties and missing-list/shortlist cases are explicit.
- [x] From-scratch k-means/IVF/PQ code precedes Faiss as a maintained implementation reference; query/build complexity and storage lower bounds are stated.
- [x] Simpler exact baseline, alternatives, negative result, update lifecycle and Chapter 17 dependency are explained.

### Evidence and operation

- [x] Checked experiment includes question/hypothesis, controlled variables, seeds, corpora, frozen questions/qrels, metrics/denominators, raw cases, timing samples, hashes, conclusion, failure examples, uncertainty and limitations.
- [x] Exact-neighbor/list coverage, judged evidence recall, context IDs and unrun generation are not conflated.
- [x] Training/build, query encode, search, list/bucket, compressed scoring, refinement, payload and version observability are taught.
- [x] Coarse, compression, shortlist, source/representation and no-evidence failures are independently diagnosed.
- [x] Scope and derived-data privacy/licensing/retention boundaries are checked; the fixture is not treated as live ACL enforcement.

### Visual and practice

- [x] Visual audit selected computed two-dimensional cells/PQ arithmetic and a measured three-panel quality/cost plot.
- [x] Both figures have number/title/takeaway caption, alt text, editable source, SVG/PNG, data/seed, units and uncertainty limits.
- [x] Cell IDs and centroid boundaries match the implementation/test; plot values and packed-byte arithmetic match the final checked record.
- [x] Lab, separate solutions, running V4 update, design/interview prompt, active recall and mastery target are complete.

### Release hygiene

- [x] Cross-file chapter/project/paper references and captions resolve in sixteen-chapter manuscript preflight.
- [x] Primary paper and maintained library claims were verified on 2026-10-01; no frontier acronym replaces the mechanism.
- [x] V0–V4 tests pass (86 total), both plot scripts rerender, checked hashes/parity and `git diff --check` pass.
- [x] Chapter, lab, solutions, code/tests/record, visual source/renderings, documentation and review are committed together.
