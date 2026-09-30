# Chapter 11 lab — Worked solutions

Try the [lab](../labs/chapter-11/LAB.md) before reading these. Numeric retrieval findings follow the checked-in [Chapter 11 experiment](../projects/V3/chapter-11-experiment.json); model load and timing vary by environment.

## 1. Representation and contrastive arithmetic

The masked token sum is `(2,0)+(0,4)=(2,4)` and the mask count is `2`, so the pooled vector is `(1,2)`. Counting the padding vector would instead give `(101/3,103/3)≈(33.67,34.33)`, whose direction has little to do with the two real tokens. Special-token/CLS pooling and max pooling are alternatives; tokenizer, model, text format, pooling, projection, normalization and dimension must be versioned together.

The four dot products are `q₁·p₁=3`, `q₁·p₂=1`, `q₂·p₁=0`, `q₂·p₂=2`, giving `[[3,1],[0,2]]`. At `τ=1`, each diagonal probability is `1/(1+e⁻²)≈0.880797`; the mean negative log probability is `ln(1+e⁻²)≈0.126928` nats. All-ones scores yield `P=.5` and loss `ln 2≈.693147`. With `τ=.5`, the logit gap grows from 2 to 4, so the first example's positive probability rises to about `.982014` and loss falls to about `.018150`. If `p₂` also answers `q₁`, treating it as a negative pushes a valid passage away: the one-positive-per-row batch contract is wrong for that pair.

A small independent implementation can follow this shape:

```python
import math

def pool(rows, mask):
    if not rows or len(rows) != len(mask) or sum(mask) == 0:
        raise ValueError("invalid rows or mask")
    if any(m not in (0, 1) for m in mask):
        raise ValueError("mask must be binary")
    d = len(rows[0])
    if d == 0 or any(len(row) != d for row in rows):
        raise ValueError("dimension mismatch")
    if any(not math.isfinite(float(x)) for row in rows for x in row):
        raise ValueError("nonfinite coordinate")
    return tuple(math.fsum(row[j] for row, m in zip(rows, mask) if m)
                 / sum(mask) for j in range(d))

def batch_loss(scores, temperature):
    n = len(scores)
    if not n or any(len(row) != n for row in scores):
        raise ValueError("square nonempty score matrix required")
    if not math.isfinite(temperature) or temperature <= 0:
        raise ValueError("invalid temperature")
    if any(not math.isfinite(float(x)) for row in scores for x in row):
        raise ValueError("nonfinite score")
    losses = []
    for i, row in enumerate(scores):
        z = [x / temperature for x in row]
        m = max(z)
        log_denom = m + math.log(math.fsum(math.exp(x-m) for x in z))
        losses.append(log_denom - z[i])
    return math.fsum(losses) / n
```

The project [contrastive module](../projects/V3/contrastive_math.py) additionally returns each diagonal probability and checks an all-zero mask. It computes a training **signal** only; Chapter 11 does not update model weights.

## 2. Model and qrel audit

The public model is `sentence-transformers/all-MiniLM-L6-v2` at revision `8b3219a92973c328a8e22fadcfa821b5dc75636a`, licensed Apache-2.0 on its [model card](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2/blob/8b3219a92973c328a8e22fadcfa821b5dc75636a/README.md). The card describes 384-dimensional sentence/paragraph embeddings, masked mean pooling, normalization and a default 256-word-piece truncation. The checked-in run used sentence-transformers `5.2.2`, transformers `4.57.3`, CPU PyTorch `2.10.0+cpu`, two torch threads and one shared encoder with no query/passage instruction prefixes. Both search methods see the V0 segment title and body. They do not separately index literal segment ID, source status or effective-date metadata; titles can still contain words such as “Draft” or “Amendment.” A high cosine without the source ID/version/span cannot support a resolvable citation.

The query set has `8+6+3=17` questions and `17×12=204` reviewed eligible query–segment pairs. Each eligible ID absent from a query's grade-1/2 list is expressly grade zero. D10 is legal-only and has **no** support-team judgment or candidate score. The model weights were frozen before evaluation and not adapted to these qrels. The probe is still small, fictional, written and judged by one person who knew the corpus and earlier failures, and contains no external workload sampling or independent assessor. Its results do not establish cross-domain or production quality.

## 3. Reproduced comparison and trace diagnoses

The falsifiable paraphrase hypothesis holds on this probe: macro binary Recall@2 rises from BM25 `.8125` to frozen encoder `1.0000`, an absolute gain of `.1875`. Across the fourteen positive questions, macro NDCG@2 rises from `.707596` to `.830781`, an absolute gain of `.123185`. The six-query exact-identifier slice has equal Recall@2, `.6667`, for both. All three zero-positive queries return candidates for both methods. These are separate slice observations, not a universal model win.

| Query | BM25 top two | Frozen encoder top two | Diagnosis |
|---|---|---|---|
| `p-shared` | `D4:step-4:0`, `D2:§2:0` | `D4:step-4:1`, `D4:step-4:0` | Only second runbook window is grade 2 for notifying the commander. Dense puts it first; BM25 misses it at two. |
| `p-change-log` | `D4:step-4:0`, `D6:row-2:0` | `D4:step-4:1`, `D4:step-4:0` | First runbook window is grade 1 partial; second is grade 2 complete. Dense recovers complete evidence. |
| `p-basic` | `D5:§3:0`, `D4:step-4:1` | `D1:§3:0`, `D5:§3:0` | BM25 puts Basic first. Dense confuses Pro/Basic at rank one, although grade-2 Basic survives at rank two. |
| `i-segment` | none | `D2:§2:0`, `D1:§3:0` | Both miss requested `D1:§8:0`; ID metadata is absent from searchable text. Dense returns wrong nearby content. |
| `i-price-id` | none | `D1:§3:0`, `D4:step-4:2` | Both miss requested `D6:row-2:0` for the same mechanism. |
| `n-private` | `D4:step-4:2`, `D3:FAQ-7:0` | `D1:§3:0`, `D5:§3:0` | All returned IDs are eligible but grade 0. D10 is excluded before scoring; the remaining evidence cannot answer the private question. |

At top two the selected context IDs for these cases match the listed candidate IDs under the 120-source-word budget; the [raw record](../projects/V3/chapter-11-experiment.json) keeps both fields because other contexts or budgets could differ. `generation_status` is null for every new question: no answer correctness, faithfulness or citation support was measured. The literal-ID failure calls for a metadata/ID lookup path or indexed ID field with a trusted parser, not a larger cosine score. A calibrated no-result/abstention policy needs reviewed negative cases; neither method has one yet.

The checked-in local run had one warm call per method/query/depth, seven randomized-order samples, and 119 samples per method at each cutoff (`17×7`). BM25 search-only p50/p95 at two was `76.4/114.3 µs`; dense **query encoding plus exact scan** was `17,081.2/19,993.3 µs`. The record also separates each dense encoding sample from its exact scan sample. Model load was about `275 ms` *after imports* and encoding/building thirteen indexed vectors about `574 ms`; those costs and context selection are outside request samples. Machine, cache, batch size and model runtime can change timings greatly. These samples are not service p95 estimates.

## 4. Design defense

At index time, store `source ID/version/span → title+body text → tokenizer/model/pooling/normalization → vector`, plus allowed scope and exact encoder/input-format version. At query time, derive trusted scope, encode a compatible query, gate eligibility, score/rank the vectors, select context with locators, and only then generate and check claims. A cross-encoder would read `(query, candidate)` together after first-stage retrieval; it cannot reuse a single query-independent passage vector for all comparisons. When a model requires different query/passage prefixes, build a new versioned passage index with the prescribed passage prefix and switch only after the compatible query path, qrels, security tests and rollback route are ready. Do not mix old and new vectors or compare raw scores without calibration.

Raw float32 coordinates take `13×384×4=19,968` bytes for this corpus; one million take `1,536,000,000` bytes, about `1.43 GiB`. Both exclude tokenizer/model weights, object headers, IDs, metadata, permissions, replicas, ANN structures, deleted versions and working memory. A Matryoshka prefix needs an explicit model training/validation claim, the same approved prefix on query and passage, renormalization for cosine, a rebuilt versioned index, exact-neighbor and judged-evidence Recall@K by slice, and storage/latency measurements. This MiniLM model card does not state that it was trained for nested prefixes, so choosing its first 128 coordinates arbitrarily is not justified. A multilingual test might pair native Hindi questions with Hindi source passages; a cross-lingual test might pair Hindi questions with English passages. Each needs its own judged questions and corpus. A `0.9` cosine identifies a nearby **candidate**, not an authorized, current, complete, claim-supporting citation.
