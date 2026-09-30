# Chapter 11 lab — Explain and test a frozen sentence encoder

**Prerequisites:** Chapters 4, 9 and 10, the V2 BM25/qrel baseline, and V3's exact vector oracle. **Time:** about 110–145 minutes. Read [Chapter 11](../../chapters/chapter-11-how-embedding-models-learn-retrieval-spaces.md) first. Work from the repository root with Python 3.14 or a compatible environment. The experiment uses a public ~92 MB pinned model, `sentence-transformers` and CPU PyTorch; the model weights are **not** in this repository. Attempt each task before opening the [solutions](../../solutions/chapter-11-solutions.md).

## Deliverables

Submit a pooling and contrastive-arithmetic sheet, a small independent implementation, a qrel/experiment card with per-slice failures, and a version-safe design defense. Do not fine-tune on the 17 probe questions. Keep model load, passage encoding/index build, query encoding, exact scan, context selection and generation as different stages.

## 1. Derive the representation and loss

For token vectors `(2,0)`, `(0,4)`, `(99,99)` and attention mask `1,1,0`, calculate the masked mean. Explain why including padding would change a sentence vector. Name two other pooling choices and what must be versioned if pooling changes.

Use the hand-authored query vectors `q₁=(1,0)`, `q₂=(0,1)` and passage vectors `p₁=(3,0)`, `p₂=(1,2)`. Calculate all four dot scores and write the `2×2` score matrix. At temperature `τ=1`, calculate the row-softmax probability of the diagonal pair for each query and the mean negative log probability in nats. Repeat for an all-ones score matrix. Describe a case where `p₂` is also valid evidence for `q₁`: which training assumption fails? What happens to the preference strength when `τ` becomes smaller *if the diagonal is already larger*?

Before inspecting the project code, independently implement masked mean pooling and a numerically stable row-softmax contrastive loss in a scratch file. Reject an all-zero mask, a non-square score matrix, nonfinite values and nonpositive temperature. Check your values against:

```powershell
python -X utf8 projects/V3/contrastive_math.py
python -X utf8 -m unittest discover -s projects/V3 -p 'test_*.py' -v
python -X utf8 visuals/chapter-11/plot-11-01-encoders-and-batch.py
```

## 2. Audit the frozen model and judgment set

Open [the model card](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2/blob/8b3219a92973c328a8e22fadcfa821b5dc75636a/README.md), [the 17-query qrels](../../projects/V3/judgments_ch11.json) and [the experiment code](../../projects/V3/experiment_ch11.py). Record the pinned model ID/revision, license, embedding dimension, sequence limit, pooling/normalization, input fields, query/document symmetry and package versions. Why is `title + segment text` a meaningful but incomplete input? Which metadata fields are unavailable to both BM25 and dense text search? State what would happen to a citation if its source locator were lost even when the retrieved vector had high cosine.

Verify the qrel roster has 12 support-team segments, 17 questions and 204 judged pairs; count the eight paraphrases, six exact-identifier probes and three no-evidence probes. Explain why D10 is outside the roster and why an unlisted eligible segment has grade zero in **this complete tiny set**, unlike an unjudged item in a large pooled benchmark. Check that the model weights were not tuned on these questions. Name two reasons the new probe is still not a general benchmark.

## 3. Reproduce the comparison and diagnose failures

The default runner uses a locally cached pinned model. If it is unavailable, install the dependency in an isolated environment and rerun once with `--allow-download`; that flag fetches **only the pinned revision**. Do not commit downloaded weights or your local timing record.

```powershell
python -X utf8 projects/V3/experiment_ch11.py --output projects/V3/chapter-11-experiment-local.json
```

Fill in this experiment card using the checked-in [raw record](../../projects/V3/chapter-11-experiment.json) and your local run:

```text
Question, falsifiable paraphrase Recall@2 hypothesis, decision rule:
BM25 baseline and changed encoder/score/execution system:
Fixed source, segment, scope, query/qrel, context and metric contracts:
Model ID/revision, tokenizer/input/pooling/normalization/dimension:
Index-time and query-time work; model load and build costs:
Positive and zero-positive query counts; per-slice Recall/NDCG:
Raw timing population, units, randomized order, samples and exclusions:
Four query-level trace diagnoses; conclusion and limits:
```

Calculate the paraphrase Recall@2 difference and all-positive-query NDCG@2 difference. Inspect `p-shared`, `p-change-log`, `p-basic`, `i-segment`, `i-price-id` and `n-private`. For each, report BM25 versus dense candidate IDs and qrel grades at top two, context IDs and whether the source is eligible. Why are the two literal metadata IDs missed? Why is `p-basic` a warning even though dense Recall@2 counts a hit? What does returning candidates on every no-evidence query tell you about nearest-neighbor search without calibrated abstention?

Compare local timing with the checked-in record **without** expecting exact microseconds. Report model load, document encoding/index build, query encoding and exact scoring separately where the record permits. State what was excluded from the search-only and encode-plus-scan samples. Never describe these tiny local p95s as service tail latency or the encoder's cosine as an answer-confidence probability.

## 4. Design and oral defense

Draw index time and query time lanes. Include tokenizer, model/prompt and pooling versions; passage vector IDs; eligibility; exact similarity; candidate ranking; context construction; and the future answer boundary. Explain what a cross-encoder would change in this drawing and why it belongs after a first-stage candidate set. Suppose a model requires `query:` and `passage:` instructions. Specify how you would migrate its index without comparing old passage vectors to new query vectors.

Estimate raw float32 coordinate bytes for 13 vectors of dimension 384, then for one million vectors. State what those estimates exclude. Give a migration plan for a purported 128-coordinate Matryoshka prefix: required model evidence, query/passage truncation, renormalization, index version, judged Recall@K by slice and latency/storage measurements. Explain why arbitrary truncation of this model is not supported by its card. Add a multilingual and a cross-lingual test slice that would need independent labels. Conclude with an oral answer to: “The nearest passage has cosine 0.9. Can the assistant cite it?”

**Cumulative recall:** compare Chapter 10's *exact-neighbor correctness* with Chapter 11's *judged-evidence recall*. A later ANN system can lose the former; a poor representation can lose the latter even with exact search.
