# Chapter 11 technical and pedagogical review

**Reviewed:** 2026-09-30. **Artifacts:** [chapter](../../chapters/chapter-11-how-embedding-models-learn-retrieval-spaces.md), [lab](../../labs/chapter-11/LAB.md), [solutions](../../solutions/chapter-11-solutions.md), [V3 project](../../projects/V3/README.md), [contrastive arithmetic](../../projects/V3/contrastive_math.py), [frozen qrels](../../projects/V3/judgments_ch11.json), [experiment and raw record](../../projects/V3/experiment_ch11.py), [tests](../../projects/V3/test_ch11.py), [figure source](../../visuals/chapter-11/plot-11-01-encoders-and-batch.py).

## Technical review

- **Mechanism and arithmetic:** The text separates model-token vectors, masked pooling, a fixed-size embedding, normalization, exact similarity and evidence. Pooling `(2,0),(0,4),(99,99)` under `1,1,0` yields `(1,2)`. Figure 11.01 uses query vectors `(1,0),(0,1)` and passage vectors `(3,0),(1,2)` to generate exactly `[[3,1],[0,2]]`; diagonal row probabilities are `.880797` and mean natural-log loss `.126928`. The stable implementation passes its extreme-logit check. The softmax probability is identified as conditional on batch labels, never answer/relevance confidence. A wrong off-diagonal assumption is named a false negative.
- **Model and version:** The public pinned [model-card revision](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2/blob/8b3219a92973c328a8e22fadcfa821b5dc75636a/README.md) confirms Apache-2.0, 384 dimensions, masked-mean example, contrastive training and default 256-word-piece truncation. The local cached checkpoint revision matches the code. The recorded environment used sentence-transformers 5.2.2, transformers 4.57.3 and PyTorch 2.10.0+cpu. The symmetric shared `encode` path, `title + segment text`, normalized vectors, exact cosine and no prefixes are explicit. No trained weights or downloaded artifacts are committed. No arbitrary prefix is claimed to be Matryoshka.
- **Evaluation integrity:** The new 17-query qrel file was written before model execution; the loader checks source snapshot, all 12 eligible segment IDs, grades, no-evidence slice and duplicate IDs. It yields 204 completely reviewed pairs, with 8 paraphrase, 6 identifier and 3 no-evidence questions. The same source segments, scope, top-*k*, context builder and Chapter 9 metric definitions are used for BM25 and dense. The comparison changes representation, scoring and execution jointly, so it is a system comparison, not an ablation. The frozen model improves paraphrase Recall@2 `.8125→1.0000`; exact-identifier Recall@2 ties `.6667`; all three no-evidence questions return candidates. `p-basic` wrong-product rank one and the two literal metadata-ID misses are kept. All new generation statuses are null; no answer-quality inference is made. One author knew the corpus and prior failures, so neither independence nor production generalization is claimed.
- **Cost and observation:** Model load (after imports), document encode/index build, query encode, exact scan, BM25 search and context selection have distinct recorded boundaries. Seven randomized-order warmed samples per question/depth yield 119 samples per method/depth; p50/p95 are labeled local nearest-rank values, not service tails. Exact search scores all 12 eligible vectors for every question. Raw float32 coordinate storage calculations exclude object/index/model overhead. Source/index/model/qrel/code hashes match the checked-in record. Protected trace fields, source/vector retention, and lack of live authentication are acknowledged.
- **Primary-source check:** BERT, Sentence-BERT, DPR and Matryoshka primary papers plus official Sentence Transformers documentation/model card are listed in [REFERENCES.md](../../REFERENCES.md). Their historical mechanisms are separated from this model's measured Helios result. No leaderboard or multilingual performance is asserted from the English probe.

## Pedagogical review

- The Chapter 10 binary-vector failure motivates learned coordinates without promising they solve evidence authority. A source→token→pool→vector→candidate path precedes architecture names. The from-scratch pooling/loss exercise precedes the library experiment. The figure lets the learner verify the full score matrix and false-negative assumption, while the actual V3 record teaches a measured paraphrase gain alongside identifier, wrong-entity and no-answer limits.
- The lab forces independent arithmetic/code, qrel-roster review before the model run, paired per-slice diagnosis, timing-boundary analysis, and an architecture defense. Worked solutions supply intermediate values, IDs, grades and context interpretation. The chapter leaves actual weight updates, mining and domain adaptation to Chapter 12 as required by the syllabus. It ends with active recall, further reading and observable mastery abilities.
- Terminology and roadmap links now distinguish contextual token vectors from pooled embeddings, a frozen encoder from adapted retrieval, batch probability from relevance confidence, and exact vector neighbors from judged evidence. User-facing source and claim verification remain later generation work.

## Chapter completion checklist

### Learning and mechanism

- [x] Chapter 10's observed binary-vector and lexical paraphrase limitations motivate the new representation; Chapters 4, 9 and 10 are explicit prerequisites.
- [x] Contextual token vector, pooling, sentence embedding, bi-/cross-encoder, asymmetric input, contrastive loss, negatives, temperature and Matryoshka prefix are defined and registered.
- [x] Source/input/version/index-time embedding and query-time encoding/eligibility/exact score/context boundaries are traced.
- [x] Masked-mean and `2×2` loss mathematics include assumptions, units, intermediate scores, false-negative and numerical-stability cases.
- [x] Standard-library pooling and row-softmax code precede the pinned library/model implementation; no Chapter 12 training code is smuggled in.
- [x] `O(Nd)` exact search, embedding/index costs, float32 storage, measured local stage latency and excluded production costs are bounded.
- [x] Shared versus asymmetric encoders, cross-encoder/late-interaction trade-offs, identifier failures, model/version/prefix limits and Chapter 12–14 dependencies are explicit.

### Evidence and operation

- [x] Falsifiable paraphrase-recall hypothesis, V2 BM25 baseline, fixed corpus/scope/qrels/depth/context, primary system change, versions, seed, raw samples, slices, failures and limits are recorded.
- [x] Candidate IDs and scores, selected context IDs/direct coverage, absent new generator labels and future answer checks are kept distinct.
- [x] Trace/version/work/time fields, model/index build costs, protected identifiers and drift/retention implications are taught. Paid-model charge is N/A: all inference is local; GPU/service operating cost is not inferred from this fixture.
- [x] Wrong product, partial runbook, literal segment IDs, no-answer and restricted D10 provide concrete debugging probes.
- [x] Static scope/authentication boundary, protected embeddings/IDs, pinned model license and no committed weights are stated.

### Visual and practice

- [x] Visual audit chose a programmatic encoder→score-matrix figure; formulas and result table carry precise values without a decorative visual.
- [x] Figure 11.01 has number, caption, alt, editable script, SVG/PNG, fixed vectors, arbitrary score units, loss units and no-sampling note.
- [x] Every arrow and matrix cell was checked against the arithmetic code; the PNG was visually inspected for legibility and contrast.
- [x] Hand work, independent coding, judged experiment, design/interview defense, project update and separate solutions are present.
- [x] Active recall, spaced review, observable mastery statement and primary further reading are present.

### Release hygiene

- [x] Chapter, lab, solution, visual, project, syllabus, glossary and reference links resolve; Chapter 12 is not authored.
- [x] Pinned model-card revision and official API/paper sources were verified for 2026-09-30; frontier claims remain outside the core chapter.
- [x] V0–V3 tests, qrel/hash integrity, experiment replay, visual rendering/inspection and 11-chapter manuscript preflight pass; gains and failures remain in the record.
- [x] Chapter, lab, solutions, code/tests, qrels, experiment, visual source/renderings, roadmap, reference/glossary and this review are included in one Chapter 11 change.
