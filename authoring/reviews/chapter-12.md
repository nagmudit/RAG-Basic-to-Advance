# Chapter 12 technical and pedagogical review — 2026-09-30

## Technical review

- **Mechanism:** The chapter defines query/passage labels, in-batch/explicit/mined/hard/false negatives, weak supervision, synthetic queries, temperature-scaled row softmax, triplet margin, pairwise/listwise objectives, mining and distillation. The `0.8/0.6/0.2` example yields logits `4/3/1`, positive probability about `.705`, loss about `.349` nats and triplet violation `.1`. The code's loss masks potentially relevant runbook neighbors and old contract context; it never treats D10 as a train negative.
- **Implementation boundary:** V3 trains a `384→16→384` residual query projection with 12,288 parameters. The pinned Chapter 11 transformer, passage vectors, exact cosine scorer and source text are frozen. This is query-tower adaptation, clearly narrower than full dual-encoder fine-tuning. All 12 eligible passage vectors are searchable; only seven train-document passage vectors enter the training loss. D10 is gated out before scoring. Training changes no source authority or answer policy.
- **Evaluation integrity:** The Chapter 12 manifest was authored before running adaptation. Train, validation and test source IDs are disjoint; the loader checks roster, split ownership, duplicate/empty queries, legal-only exclusion and unsafe negative IDs. Four validation and 11 test questions have a complete 12-segment roster (180 reviewed pairs), including 132 held-out test pairs. Chapter 9/11 questions are already inspected and excluded from checkpoint choice. The runner chooses epoch 1 by validation NDCG@2/Recall@2 before encoding test questions or using test labels. One author knew the fictional corpus, so this is a source-disjoint teaching test, not an independently assessed benchmark. Related wording across sources and only three test source documents remain limitations.
- **Observed result:** Held-out macro Recall@2 is BM25 `.667`, frozen `.889`, selected adapter `.889`; NDCG@2 is `.667`, `.807`, `.807`. Later checkpoints reduce train loss while validation Recall@2 and NDCG@2 fall to zero. All methods return candidates for both zero-positive questions. `te-atlas-b` lacks the signed Atlas source in all top-two lists. No answer generator runs, so answer claims are absent. The record retains raw candidate scores/IDs, selected context IDs, by-slice metrics, frozen qrel/model/code hashes, training history, adapter hash, timings, environment, failure examples, conclusion and rejection decision.
- **Cost and observation:** The projection is 48 KiB float32 before optimizer state. Timings include five warmed query samples per test case and method with nearest-rank p50/p95, plus by-slice timing. BM25 search and dense query-encode-plus-exact-score boundaries are named; model load, passage build, training and context are separate/excluded. Tiny CPU samples do not estimate service tails. The training and search index formats/version need a coordinated rollout if the encoder changes. Trace identifiers and learned vectors require access-controlled retention in a real deployment.
- **Primary sources:** DPR, ANCE, GPL, MS MARCO official dataset notes, BEIR, MTEB, MIRACL and the pinned model card were verified on 2026-09-30 and entered in [REFERENCES.md](../../REFERENCES.md). MIRACL is described as multilingual *monolingual* ad hoc retrieval; the English V3 test makes no language-transfer claim.

## Pedagogical review

- The observed Chapter 11 paraphrase improvement and no-evidence/wrong-entity failures motivate adaptation. Labels and loss precede named mining systems. The chapter explains where a high-scoring candidate becomes a false negative and why a lower train loss cannot replace a held-out retrieval metric.
- Figure 12.01 makes the contrastive-label assumption inspectable; Figure 12.02 separates the gradient, checkpoint and final-test paths while showing the shared eligible index. Both editable scripts, SVG and PNG were rendered; values, colors, arrows, captions and alt text were visually checked. The figures use fixed illustrative/factual inputs, with no statistical uncertainty to estimate.
- The lab requires independent loss arithmetic, source split and false-negative audits, reproduction, per-slice quality/latency inspection, a signed-contract failure trace and a next experiment. Separate solutions expose the negative result without revising the frozen manifest. The syllabus asks for baseline evaluation on a domain test; this implementation evaluates baseline and adapter together **after** checkpoint choice to preserve the test's role.
- The chapter distinguishes candidate, context and absent answer labels; retriever score from answer confidence; relevance from eligibility; and zero-shot, adapter and full fine-tuning. It closes with active recall, an interview/design prompt, mastery abilities and primary further reading. Chapter 13 remains unstarted.

## Chapter completion checklist

### Learning and mechanism

- [x] Chapter 11's measured limits motivate the change; Chapters 9–11 and BM25 are binding prerequisites.
- [x] Key training, adaptation, transfer and benchmark terms are defined and registered in the glossary.
- [x] Index-time passage encoding, train/validation/test label flow, query-time encoding, eligibility and candidate/context boundaries are distinct.
- [x] Softmax and margin mathematics, units, false-negative and numerical-stability assumptions are worked through.
- [x] A small inspectable PyTorch adapter implements actual gradient updates before discussion of scaled frameworks.
- [x] Parameter storage, objective/search work, local latency boundaries and full-reindex consequence are bounded.
- [x] Alternatives, trade-offs, regressions, model-selection decision and Chapter 13 dependency are explicit.

### Evidence and operation

- [x] The checked-in record has question, falsifiable hypothesis, baseline, variable/controls, frozen corpus/split/qrels, metrics, procedure, slices, result, failure, conclusion and limitations.
- [x] Candidate ranking, selected context and absent generation outcome are not conflated.
- [x] Model/adapter/index/split versions, hashes, raw scores, latency samples and by-slice diagnostics are retained; production logging cautions are stated.
- [x] Wrong signed source, false-negative runbook neighbors, no-evidence returns and later-checkpoint collapse serve as debugging probes.
- [x] D10 authorization, source licensing/retention, model license and derived-vector privacy are addressed.

### Visual and practice

- [x] Visual audit selected a score matrix and source-split flow; the numerical result uses a table.
- [x] Both figures have numbers, takeaway captions, alt text, editable scripts, SVG/PNG and fixed-input/no-uncertainty notes.
- [x] Rendered PNGs were inspected; labels and example values agree with code/prose.
- [x] Lab, worked solutions, design question, project upgrade, active recall and mastery target are present.

### Release hygiene

- [x] Chapter, lab, solutions, project, glossary, syllabus, architecture and references have updated links and numbering.
- [x] Primary benchmark and model sources were checked for the writing date; frontier claims are not promoted from a leaderboard.
- [x] V0–V3 tests, pinned experiment replay, figure rendering, record hashes and twelve-chapter manuscript preflight pass; negative results are retained.
- [x] Chapter source, qrels, experiment, tests, figure sources/renderings, project and review are staged together for one commit.
