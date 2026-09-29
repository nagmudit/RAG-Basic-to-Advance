# V0 context and generation-boundary probes

Chapter 4 adds a [prompt intervention sidecar](context_probes.py), [behavioral checks](test_context_probes.py), and a [redacted ten-case manifest](chapter-04-case-manifest.json). It holds the [V0 corpus and evidence contract](README.md) as the reference source. `Engine.run()` is unchanged, and **no language model has been called**. The manifest's `model_name`, `model_token_count` and `model_result` are `null` by design. The V0 stub remains the deterministic answer baseline for its two frozen questions.

The sidecar selects only `support-team`-eligible excerpts before prompt construction. It fixes `q-contract-change` and the required `D1 §3`/`D2 §2` spans. The position family shuffles the same five excerpts (`D1,D2,D3,D7,D9`), giving 67 source words and 809 prompt characters in each case. The conflict family replaces one eight-word neutral lab note with stale `D3` while keeping the governing evidence. The trusted-instruction family varies application wording with sources fixed. The untrusted-instruction family gives a lab-only `P1` note text that *pretends* to be a system command; its snapshot is suffixed. The missing-amendment case deliberately omits `D2` and should not support the current change.

The manifest records case IDs, source snapshot, scope fixture, ordered context IDs, required IDs present, instruction version, word/character counts and a SHA-256 hash of the local prompt. It contains no raw question or source text. `--show-prompt` is an explicit **local fictional-source preview**. Hashes help detect prompt changes; they do not prove that a claim is supported. The `support-team` string is a teaching scope, not authentication. A real integration must derive permissions from verified identity before any source is exposed.

The intervention families are **stimuli**, not measured answer-quality results. A later model experiment must pin model/tokenizer/prompt versions, role formatting, decoding settings, actual token counts and output budgets; store outputs under appropriate access; and grade values, calculations, faithfulness, citations and abstention separately. The [Chapter 4 lab](../../labs/chapter-04/LAB.md) supplies a complete no-model learning path and an optional real-model experiment card. The project still reaches its first full generator in V9 / Chapters 28–29 according to the [project roadmap](../../PROJECT_ROADMAP.md).

Run from the repository root:

```powershell
python -X utf8 projects/V0/context_probes.py
python -X utf8 projects/V0/context_probes.py --show-prompt position-middle
python -m unittest discover -s projects/V0 -p 'test_*.py' -v
```

Regenerating the manifest changes its UTC creation timestamp but not the source IDs or prompt hashes if code and source snapshot are unchanged. Keep the original V0 [result record](RESULTS.md) and Chapter 3 [computing measurements](CHAPTER_03_MEASUREMENT.md) as separate baselines.
