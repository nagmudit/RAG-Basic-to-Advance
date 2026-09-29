# Build Your Own RAG Engine — V0 evidence contract

**Implemented in Chapters 1–2.** Chapter 1 fixes the source and answer contract. [Chapter 2](../../chapters/chapter-02-build-the-first-rag-loop.md) implements a literal-search loop and a minimal request record. The checked-in [ten-document corpus](corpus.json), [engine](engine.py), [behavioral tests](test_engine.py), and [first result record](RESULTS.md) are the reproducible V0 snapshot.

[Chapter 3 characterizes V0's computing costs](CHAPTER_03_MEASUREMENT.md) with a separate exact-ID measurement sidecar. It leaves this engine and its evidence behavior intact; V1's term index is taught later.

## Tiny corpus and source identity

The fictional snapshot is `support-corpus-2026-05-20`. The implementation contains ten short documents. The three records below bind the Chapter 1 example; the other seven create realistic decoys, a long-section boundary and a restricted source. Keep IDs, versions, dates and location markers rather than anonymous strings.

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

Record `request_id`, `query_id`, UTC timestamp, `corpus_snapshot`, eligible candidate IDs and any raw scores, selected evidence IDs/spans, status, failure/abstention reason and wall-clock latency in milliseconds. Keep raw confidential content out of a broadly accessible trace. A candidate must not be labeled evidence merely because search returned it.

V0 passes when a reader can inspect one request and identify the source snapshot, candidates, evidence and answer status; when the system does not assert the current target from `D1`/`D3` alone; and when an inaccessible `D2` is excluded before prompt construction. The literal search built in Chapter 2 is expected to fail some paraphrases and longer documents. Preserve those failures as the reason for later upgrades.

## Run and inspect

From the repository root:

```powershell
python -X utf8 projects/V0/engine.py --top-k 2
python -X utf8 projects/V0/engine.py --query-id q-termination --top-k 3
python -X utf8 projects/V0/engine.py --drop-document D2
python -m unittest discover -s projects/V0 -p 'test_*.py' -v
```

Preparation validates and splits source sections into 13 segments once. Each request filters scope before scoring, scans every eligible segment, counts distinct literal term overlap, sorts reproducibly, packs source-labeled context, applies the two-task deterministic stub and emits a redacted structured trace. `--scope` is caller-controlled only in this local teaching program; it is not authentication. `--show-prompt` reveals fictional source text locally and is excluded from normal trace output. Word budgets and the character-based token estimate are illustrative, not a real model tokenizer or production control.
