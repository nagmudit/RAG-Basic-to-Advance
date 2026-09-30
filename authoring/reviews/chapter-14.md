# Chapter 14 technical and pedagogical review — 2026-10-01

## Technical review

- **Mechanism:** The chapter distinguishes a model's representation from its search execution. It gives original SPLADE sum pooling versus SPLADE-v2 max pooling accurately, implements only the latter on fixed logits, and traces nonnegative weighted posting accumulation with eligibility before score accumulation. It gives the ColBERT-style MaxSim operator over independently supplied unit token vectors, not a cross-encoder or single-vector score. The toy code does not claim trained SPLADE/ColBERT inference.
- **Arithmetic:** `log1p(ReLU(2))=log(3)=1.098612`; `log1p(ReLU(1.8))=log(2.8)=1.029619`; incident weighted dot `2.262305`; literal distractor score `1.206949`. MaxSim scores are A=`2`, B=`√2`, C=`1`; mean-pooled cosines are A=`−1`, B=`1`, C=`1/√2`. The A/B grids and winner indices match Figure 14.01 and the record. The idealized 13×100×128×4 storage example is 665,600 bytes versus 6,656 bytes for one vector per passage.
- **Execution and limits:** The sparse fixture has three eligible support-team rows and one legal-only row. Surface and expanded routes score two and four eligible posting entries; the legal row is present in postings but never scored. MaxSim evaluates all three toy documents exactly. Model forward pass, token ANN, compression, context, generation and real authentication are absent. Fixed in-process microsecond samples are separated from Chapter 13's encoder/request timings and are not service claims.
- **Evaluation:** Both fixtures have one query and complete three-row 0/1/2 grades. The record states hypothesis, baseline, variables, controls, source/code/runner/fixture identity, procedure, seeded timing order, raw weights/scores/grids, ranked IDs, four request-trace examples, work, 31 raw warmed samples, failure examples and limitations. The toy reversals do not establish a trained-model gain or replace Chapter 13's V0 BM25/frozen-dense baseline. Grade-2 direct Recall@1 is identified explicitly. No answer correctness, faithfulness, citation or abstention label exists for these tasks.
- **Primary-source verification:** [SPLADE](https://arxiv.org/abs/2107.05720), [SPLADE v2's equation and FLOPS penalty](https://arxiv.org/html/2109.10086v1), [ColBERT's MaxSim and two search roles](https://arxiv.org/html/2004.12832v2), and [ColBERTv2's compression direction](https://arxiv.org/abs/2112.01488) were checked on 2026-10-01. Their claims are bounded in [REFERENCES.md](../../REFERENCES.md); no model leaderboard result is transferred to V3.

## Pedagogical review

- The motivation is Chapter 13's lexical mismatch and pooled-detail loss; BM25 and frozen dense remain visible baselines. Model names follow mechanisms, and a false expansion and no-evidence warning temper the constructed positive examples.
- The chapter separates index and query time, candidate and evidence/answer, scope and relevance, exact MaxSim and token ANN, reranking and first-stage retrieval. It explains storage, posting visits, query-length score dependence, pruning and compression without beginning Chapter 15.
- Figure 14.01 answers one question: where does each query token find its best document token? The script reads the checked record, labels axes and units, boxes argmax cells, and emits SVG/PNG. The PNG was inspected for cell values, winner boxes, contrast and legibility. The table carries exact sparse arithmetic; an extra decorative diagram was unnecessary.
- The lab requires hand computation, scope/work audit, a false-expansion probe, a full MaxSim/pooling reversal, a candidate-role explanation and a future held-out experiment design. Separate solutions show intermediate arithmetic. Active recall, interview prompt and mastery abilities are in the chapter.

## Chapter completion checklist

### Learning and mechanism

- [x] Chapter 13 failures motivate Chapter 14; Chapters 6–13 are named prerequisites.
- [x] Learned sparse, expansion, weighted posting, FLOPS regularization, late interaction, MaxSim and token-vector index are defined in the glossary.
- [x] Index/query paths, scoring, eligibility, candidates, selected evidence and absent generation are kept distinct.
- [x] Equations, units, assumptions, tie rule, edge cases and hand-worked scores are explicit.
- [x] Pseudocode and from-scratch Python precede paper/model implementation details.
- [x] Posting work, token comparison work, idealized raw bytes and excluded costs are bounded.
- [x] Alternatives, failures, retrieval roles, score calibration and next dependencies are explicit.

### Evidence and operation

- [x] Fixed experiment records question, hypothesis, baselines, variables/controls, full toy qrels, versions, procedure, rankings, raw scores, timing samples, work, failure examples, conclusion and limits.
- [x] Candidate scores are not mistaken for context, answer, evidence support or trained-model quality.
- [x] Code/fixture identity, scope, model absence, raw traces and scoring-only timing boundary are retained.
- [x] Vocabulary mismatch, false expansion, pooled dilution, no-result and candidate-set misses have probes or explicit next tests.
- [x] Static scope is named as a fixture; derived-index licensing, retention and source deletion obligations are checked.

### Visual and practice

- [x] Visual audit chose the token score grid; exact formulas and stage distinctions use tables/text/pseudocode.
- [x] Figure 14.01 has number, title, takeaway, alt text, chapter, editable script and rendered SVG/PNG with axes/units.
- [x] Rendered grid was inspected against exact code/record values; score labels and winner boxes are legible.
- [x] Worked lab, solutions, false-expansion debugging, design/interview question, V3 update, active recall and mastery target are present.

### Release hygiene

- [x] Chapter/lab/solutions/V3/figure, syllabus, README, project roadmap, knowledge map, architecture, glossary, paper path and references resolve in manuscript preflight.
- [x] Primary research sources and paper distinctions were verified on 2026-10-01; no frontier claim enters stable fundamentals.
- [x] V0–V3 tests, fixed experiment replay, image render, record hash, reference scan and fourteen-chapter preflight pass.
- [x] Chapter, lab, solutions, code/tests/experiment, visual source/renderings, cross-file updates and review are committed together.
