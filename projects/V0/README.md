# Build Your Own RAG Engine — V0 evidence contract

**Introduced in Chapters 1–2.** Chapter 1 fixes the source and answer contract. Chapter 2 builds the first literal-search implementation and emits a minimal request record. This file is the initial version specification; it does not claim that an engine already exists.

## Tiny corpus and source identity

The fictional snapshot is `support-corpus-2026-05-20`. Start with these records and expand toward ten short documents in Chapter 2. Keep IDs, versions, dates and location markers rather than anonymous strings.

| ID | Version and location | Role |
|---|---|---|
| `D1` | Support Agreement v1, effective 2025-01-01, §3 and §8 | Four-hour original Sev-1 target; §8 says “Either party may terminate this agreement with 30 days' written notice.” |
| `D2` | Amendment A, signed 2026-05-12, effective 2026-05-15, §2 | One-hour replacement target |
| `D3` | FAQ captured 2026-05-10, FAQ-7 | Stale four-hour summary |

Use the exact sample clauses in [Chapter 1](../../chapters/chapter-01-a-question-a-model-and-missing-evidence.md). Source content and user scope are teaching fixtures, not real private data.

## Frozen initial questions and expected evidence

| Query ID | Question | Eligible evidence | Expected behavior |
|---|---|---|---|
| `q-contract-change` | As of 20 May 2026, how did the Helios Pro Sev-1 target change? | `D1 §3`, `D2 §2` | Four to one hour, three-hour/75% reduction, both cited; abstain on current change if `D2` is unavailable. |
| `q-termination` | Show the termination clause in the Helios Pro agreement. | `D1 §8` | Return the clause and locator; generation is optional. |

## Minimal trace and acceptance criteria

Record `request_id`, `query_id`, `corpus_snapshot`, eligible candidate IDs and any raw scores, selected evidence IDs/spans, status, failure/abstention reason and wall-clock latency in milliseconds. Keep raw confidential content out of a broadly accessible trace. A candidate must not be labeled evidence merely because search returned it.

V0 passes when a reader can inspect one request and identify the source snapshot, candidates, evidence and answer status; when the system does not assert the current target from `D1`/`D3` alone; and when an inaccessible `D2` is excluded before prompt construction. The literal search built in Chapter 2 is expected to fail some paraphrases and longer documents. Preserve those failures as the reason for later upgrades.
