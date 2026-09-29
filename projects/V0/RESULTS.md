# V0 baseline result record

**Run date:** 2026-09-29. **Environment:** Python 3.14.2, local Windows workspace; source snapshot `support-corpus-2026-05-20`, 10 documents, 13 segments, 24-word windows, `support-team` scope, 120-source-word context budget. **Answer system:** deterministic two-task stub, with no LLM call. Reproduce the run with the commands in [V0 README](README.md). The corpus, query set and expected spans are fictional teaching data.

## Frozen questions and required evidence

| Query ID | Frozen task | Required evidence | Success condition |
|---|---|---|---|
| `q-contract-change` | Compare the Helios Pro Sev-1 target as of 20 May 2026 | `D1 §3` and `D2 §2` | Both spans in context; answer four to one hour with both citations and three-hour/75% reduction. |
| `q-termination` | Show the Helios Pro termination clause | `D1 §8` | Exact clause and locator returned. |

The early quality measure is **required-evidence coverage in selected context**, the count of required spans present divided by one or two as shown. This is a transparent hand-audit for two questions, not a formal or general relevance metric. Chapter 9 introduces judged retrieval metrics; V2 freezes a larger judged query set.

## Observed depth experiment

All rows use the same corpus, tokenizer, scope, context budget and stub; only `top_k` changes within each question. Latencies are **single measured wall-clock samples** in milliseconds from this run and are too small and noisy to compare as performance claims.

| Query | `top_k` | Context coverage | Stub outcome | One wall sample (ms) |
|---|---:|---:|---|---:|
| `q-contract-change` | 1 | 1/2 | Abstained | 0.136 |
| `q-contract-change` | 2 | 2/2 | Answered | 0.111 |
| `q-contract-change` | 8 | 2/2 | Answered; more distracting context | 0.110 |
| `q-termination` | 2 | 0/1 | Abstained | 0.095 |
| `q-termination` | 3 | 1/1 | Returned exact clause | 0.095 |
| `q-termination` | 8 | 1/1 | Returned exact clause | 0.100 |

Stage durations, raw candidate scores, context IDs, evidence IDs, request ID, UTC timestamp, snapshot, status and reason are present in each CLI JSON trace. A separate preparation time is printed outside request timing. No raw question or source text is copied into the ordinary trace.

## Preserved failure examples

1. **Candidate depth:** `top_k=1` finds `D2` but not `D1 §3` in context, so the dated comparison abstains. The termination span appears only at rank three for its frozen query.
2. **Source availability:** `--drop-document D2` labels a new snapshot and abstains rather than using `D3`’s stale four-hour FAQ as current evidence.
3. **Segmentation:** `--window-words 8 --top-k 20` can retrieve `D2` fragments while no single supplied segment contains the exact amendment clause, so the stub abstains.
4. **Lexical mismatch:** “What became of the urgent incident pledge?” ranks runbook/incident text and fails to supply the required amendment. This negative result motivates better query handling or retrieval later.
5. **Eligibility:** For `support-team`, restricted `D10` is removed before scoring; it does not enter candidates, context or ordinary trace. This local scope flag does not implement real authentication.

No claim about real-world answer correctness, faithfulness, p95 latency or cost is made from this two-query, model-free baseline. The retained traces and failures are the comparison point for later project versions.
