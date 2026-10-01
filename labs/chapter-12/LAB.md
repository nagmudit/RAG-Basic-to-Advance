# Lab 12 — Adapt a retriever without reading the test during selection

**Prerequisites:** Chapters 9–11, the V2 BM25 and V3 frozen-encoder runs, Python with `sentence-transformers`, PyTorch and matplotlib. The pinned model revision is described in [V3](../../projects/V3/README.md). Work from the repository root. Finish the questions before opening the [solutions](../../solutions/chapter-12-solutions.md).

## Goal and hypothesis

The baseline is Chapter 11's frozen 384-dimensional encoder, with V2 BM25 as a lexical reference. The change is a rank-16 residual query projection trained on only the Chapter 12 training source documents. Predict whether held-out-document `Recall@2` rises; record a negative result if it does not. Keep support-team eligibility, corpus, title/body encoding, exact cosine, tie rule, top two, and context budget fixed.

## A. Freeze and audit labels before training

1. Open [the split manifest](../../projects/V3/judgments_ch12.json). List train, validation, and test source IDs. Verify that no source ID appears in two groups. Count the 12 eligible segments, 10 training pairs, four validation queries, and 11 test queries. How many validation/test query–segment pairs were reviewed? Why is D10 absent rather than assigned grade zero?
2. For `tr-change-a`, explain why two adjacent runbook spans are in `unsafe_negative_ids`. For `tr-amendment-a`, explain why the older signed clause is masked. Give one truly irrelevant explicit negative for each. Which labels would be unsafe to obtain by blindly treating a BM25 top result as negative?
3. Read `generalization_unit` and `source_family`. List family overlap across train/validation/test: disjoint document IDs do not imply disjoint semantic families. Explain the narrower new-query/document-target holdout being tested here, and why it does not establish unseen-family/domain transfer. For a future family-holdout experiment, write a leakage policy grouping translations and agreement revisions. State whether the inspected Chapter 11 probe is an untouched test.

## B. Work the loss by hand

For one query with positive cosine `0.8` and two reviewed negative cosines `0.6` and `0.2`, set temperature `0.2`. Calculate the three logits, positive softmax probability, and loss in natural-log units. Then calculate the triplet hinge loss for positive `0.8`, negative `0.6`, margin `0.3`. Explain what changes if the `0.6` passage is a second relevant result.

## C. Run the reproducible adaptation

Before opening the companion calculation, work the chapter's `u=(1,2)ᵀ`, `W=I` example independently. State each dimension; derive the four W derivatives; apply `η=.1`; recompute scores, positive probability and loss. Explain why rank can remain wrong while loss improves. Show why subtracting the maximum preserves all probabilities. Then run:

```powershell
python -B -X utf8 projects/V3/training_bridge.py
python -B -X utf8 -m unittest discover -s projects/V3 -p 'test_training_bridge.py' -v
```

Explain the central-difference tolerance, why the normalized derivative differs, and how the hand gradient relates to `loss.backward()` and Adam's `optimizer.step()`. Include this derivation in your submission.

The default runner uses the locally cached pinned model. It never downloads silently. If the model is absent, follow V3's pinned-revision setup before continuing.

```powershell
$env:HF_HUB_OFFLINE='1'
$env:TRANSFORMERS_OFFLINE='1'
python -X utf8 -m unittest discover -s projects/V3 -p 'test_*.py' -v
python -X utf8 projects/V3/experiment_ch12.py --output projects/V3/chapter-12-experiment-local.json
python -X utf8 visuals/chapter-12/plot-12-01-training-matrix.py
python -X utf8 visuals/chapter-12/plot-12-02-document-split.py
```

Compare your local record with [the checked-in run](../../projects/V3/chapter-12-experiment.json). Inspect `training.history`, `validation`, `test`, `test_timing`, `document_split`, hashes, and one raw `test.*.cases` entry. Repeated CPU timing varies; candidate IDs, selected epoch and metrics should reproduce with the pinned dependencies. Explain why the runner can encode test passages for the search index before training but must not use test labels to choose a checkpoint.

## D. Diagnose the result

1. Make a compact table of `Recall@2`, `NDCG@2`, and no-evidence candidate rate for BM25, frozen, and adapted. Then report Basic/Atlas/draft Recall@2 and inspect the by-slice timing samples. State whether the hypothesis survives. Compare epoch 1 with epoch 5 training loss and validation quality. Which value would mislead an engineer looking only at the optimizer log?
2. Trace `te-atlas-b`: target evidence, each method's top-two IDs, and why the incident and draft are wrong for *signed contract*. Distinguish retrieved candidates from context selected by the 120-word builder and from an answer. Check that D10 never appears.
3. Identify timing boundaries. Calculate the float32 adapter parameter bytes from two `384×16` matrices. Explain why these numbers do not determine production tail latency.
4. Design a next experiment with a larger source-family holdout, a reviewed hard-negative pool, an identifier slice, and a native-language or cross-lingual slice. Specify which labels may be used for checkpoint choice and which remain sealed.

## Submission

Provide your hand arithmetic, split audit, one-page comparison with a failure trace, a decision on whether to ship the adapter, and a next-experiment design. Preserve the negative result if observed. Do not edit the frozen manifest after viewing test outputs.
