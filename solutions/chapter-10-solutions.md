# Chapter 10 lab — Worked solutions

Use these after attempting [the lab](../labs/chapter-10/LAB.md). Numeric values below follow its hand-authored example and the checked-in [experiment record](../projects/V3/chapter-10-experiment.json); local timings may vary.

## 1. Geometry

`||q||₂=1`, `||A||₂=1`, `||B||₂=2`, `||C||₂=sqrt(.8²+.6²)=1`, `||D||₂=1`.

| Item | Dot | Cosine | L2 | L1 |
|---|---:|---:|---:|---:|
| A | 1 | 1 | 0 | 0 |
| B | 2 | 1 | 1 | 1 |
| C | 0.8 | 0.8 | `sqrt(.4)≈.63246` | 0.8 |
| D | 0 | 0 | `sqrt(2)≈1.41421` | 2 |

For C, `q·C=(1)(.8)+(0)(.6)=.8`; `||C||=sqrt(.64+.36)=1`; L2 is `sqrt((.2)²+(-.6)²)=sqrt(.4)` and L1 is `.2+.6=.8`. Top three: dot `B,A,C`; cosine `A,B,C` after the ID tie; L2 `A,C,B`; L1 `A,C,B`. B's magnitude doubles its dot while its direction remains identical to A's. Expansion gives `||u−v||²=(u−v)·(u−v)=||u||²+||v||²−2u·v=2−2cos(q,x)` **when both u and v are unit-normalized nonzero vectors**. The monotonic square root and fixed tie rule then preserve rankings. Without normalization, q=A=(1,0), B=(2,0) are tied by cosine but L2 prefers A. For a zero query or item, cosine has a zero denominator and is undefined. The picture verifies the two-coordinate arithmetic and relative positions, not learned high-dimensional semantic quality or score calibration.

## 2. Exact search implementation and checks

This minimal independent reference follows the lab's contract. A real API should additionally validate scope provenance, upper coordinate bounds, numeric overflow and source/index version consistency. [V3's implementation](../projects/V3/exact_vectors.py) includes these core numeric and ID checks and retains index-time unit vectors.

```python
import heapq
import math

def exact(records, query, scope, metric, k, plan="sort"):
    if metric not in {"dot", "cosine", "l2", "l1"} or plan not in {"sort", "heap"}:
        raise ValueError("unknown metric or plan")
    if not isinstance(k, int) or k < 1:
        raise ValueError("positive k required")
    q = tuple(float(x) for x in query)
    if not q or not all(math.isfinite(x) for x in q):
        raise ValueError("invalid query")
    ids = [r["id"] for r in records]
    if len(set(ids)) != len(ids):
        raise ValueError("duplicate ID")
    eligible = [r for r in records if scope in r["scopes"]]
    rows = []
    for r in eligible:
        v = tuple(float(x) for x in r["vector"])
        if len(v) != len(q) or not all(math.isfinite(x) for x in v):
            raise ValueError("invalid item vector")
        dot = math.fsum(a*b for a, b in zip(q, v))
        if metric == "dot":
            value = dot
        elif metric == "cosine":
            qn, vn = math.hypot(*q), math.hypot(*v)
            if qn == 0 or vn == 0:
                raise ValueError("zero-vector cosine")
            value = dot / (qn*vn)
        elif metric == "l2":
            value = math.sqrt(math.fsum((a-b)**2 for a, b in zip(q, v)))
        else:
            value = math.fsum(abs(a-b) for a, b in zip(q, v))
        if not math.isfinite(value):
            raise ValueError("overflow")
        rows.append((r["id"], value))
    key = (lambda row: (-row[1], row[0])) if metric in {"dot", "cosine"} else (lambda row: (row[1], row[0]))
    chosen = sorted(rows, key=key)[:k] if plan == "sort" else heapq.nsmallest(k, rows, key=key)
    return chosen, len(rows)
```

For the lab's `P=(100,0)` restricted to `private`, public search scores four records, never P. Both plans return the same raw values and IDs at *k*=1,3,10; k=10 returns the four eligible items. A zero query or item raises for cosine but is valid for dot/L1/L2. Here the eligible list and `rows` use `O(N)` memory even when `heapq.nsmallest` uses an `O(k)` selection heap. A streaming implementation can avoid retaining `rows`; either version still performs `N` distance/similarity calculations of `d` coordinates each, `O(Nd)` scoring.

## 3. Judged experiment

The hypothesis was “binary lexical cosine increases macro positive-query NDCG@2 over V2 BM25.” It is rejected on the checked-in 14-query, 12-eligible-segment, 168-reviewed-pair support-team fixture: BM25 is `0.899686`; binary cosine is `0.772408`, a **−0.127278** absolute NDCG difference. Macro binary Recall@2 falls from `0.863636` to `0.727273`, and direct-evidence recall from `0.954545` to `0.863636`. At *k*=8 both reach binary Recall 1 on positive queries, but BM25 NDCG remains higher (`.945258` versus `.871267`). There are 11 positive and 3 zero-positive questions. Both methods return candidates on two of the three zero-positive questions at *k*=2. With one zero-vocabulary query, exact cosine scores zero vectors; otherwise it scores all 12 eligible vectors. Its mean fully scored count is 11.14; BM25's posting-union mean is 10.71. In the checked-in local run, search-only p50/p95 at top two is 44.5/103.0 µs for BM25 and 140.7/398.1 µs for binary cosine. There are 154 samples per mode/depth: 14 queries × 11 timed trials, one warm call outside timing and randomized pair order. These are not service p95 estimates.

| Query, top two | BM25 candidates | Binary cosine candidates | Direct-evidence and context diagnosis |
|---|---|---|---|
| `q-termination` | `D4:step-4:2`, `D1:§8:0` | `D1:§3:0`, `D4:step-4:2` | Only `D1:§8:0` is grade 2. BM25 context contains it and the V0 stub answers; cosine context misses it and the stub abstains. |
| `q-contract-change` | `D2:§2:0`, `D3:FAQ-7:0` | `D3:FAQ-7:0`, `D2:§2:0` | Both need `D1:§3:0` **and** `D2:§2:0`; neither top-two context contains both. Both stubs abstain. |
| `q-no-result` | none | none | No positive qrels. Cosine wrapper sees zero in-vocabulary query coordinates and returns no result, rather than dividing by zero. |
| `q-private-target` | `D7:timeline:0`, `D3:FAQ-7:0` | same IDs | No support-team positive qrels. Legal-only D10 is outside eligibility and is absent from candidates and context; other eligible decoys still appear. |
| `q-unknown-renewal` | `D3:FAQ-7:0`, `D1:§3:0` | `D3:FAQ-7:0`, `D6:row-2:0` | No positive qrels, yet both return plausible eligible items. Nearest is not equivalent to answerable. |

The source snapshot is `support-corpus-2026-05-20`, the fixed analyzer is V1's `v0`, the representation has 119 sorted vocabulary coordinates, and qrels are `ch09-segment-qrels-v1`. Inspect the record for SHA256s and exact local environment. The representation and score change together; this comparison cannot attribute the loss to either binary weighting or cosine alone. The qrels are single-author and partly known failures, so there is no held-out generalization claim. Candidate rankings, selected context and the two-task stub status are different measurements. A score is geometric, not a probability of correct citation.

## 4. Scale and design defense

Raw coordinates: `1,000,000 × 768 × 4 = 3,072,000,000` bytes, or `3,072,000,000 / 2³⁰ ≈ 2.861 GiB`. IDs, versions, metadata, scope, copies and working memory add more. One exact query does `O(1,000,000×768)` coordinate work. Full sort adds `O(N log N)` selection and `O(N)` score storage. A streaming top-ten heap adds `O(N log 10)` selection and `O(10)` heap storage, after the same full scoring. A contiguous matrix improves locality/vectorized kernel use; a fully materialized batch of Q queries needs `Q×N` score cells, e.g. float32 gives `4QN` bytes before top-*k* extraction. Blocked scoring can bound this. Python tuple timings on 12 eligible items are a diagnostic, not a production sizing model.

For ANN, compare its returned neighbor IDs with **this exact vector oracle** at the same model, metric, source version and eligibility scope: exact-neighbor Recall@10 measures approximation loss. Separately compare candidate IDs with **judged evidence qrels**: evidence Recall@10 measures task utility. An ANN system can recover exact neighbors perfectly while the representation retrieves irrelevant passages; it can also miss an exact neighbor but return another judged-relevant passage. Include latency, work, source/version consistency and authorization checks. A `0.9` cosine result may be an eligible candidate; it can be cited only after source authority, selected span, date, and claim-level support are verified. If a forbidden result appears, investigate eligibility before ranker math. If a judged relevant candidate appears but not in context, inspect the context budget and ordering before blaming retrieval.
