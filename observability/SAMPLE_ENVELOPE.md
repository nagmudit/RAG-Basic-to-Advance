# Minimal correlated experiment sample

The V0 request lineage continues through V3/V4 experiments via [the shared helper](../projects/common/experiment_trace.py). This is a small JSON teaching envelope, with no tracing service dependency. Fresh measured calls carry unique request ID, query ID, mode and trial ID; workload and corpus/query/qrel/index/model identities; status/reason; stage timings in milliseconds; raw scores/IDs; intermediate stages; final candidates; and context/evidence IDs where those stages ran. `None` means a stage was not run, rather than an empty successful answer. No new generator is inferred.

The timer ends before context selection and diagnostic serialization. Query encoding and exact scan retain separate timings where already measured; search-only ANN trials reuse the independently encoded query. Candidate data comes from that actual operation's result. Ordinary records contain no query/source text, prompts or exception messages. The caller supplies an already eligible roster; the helper rejects IDs outside it and emits a redacted failure record. This fixture gate is not authentication or a replacement for the retriever's authorization check.

For simple exact routes, raw candidates mean the returned scored candidate list; additional full scoring pools appear only when the mechanism exposes them. LSH retains the scored eligible bucket union. Chapter 16 retains eligible probed-list candidates (`scored`), actual `approximate_top_r`, all `exact_refinement_candidates` with exact scores, final top-k, and the context subset when packed. `ivf_probed_lists` records coarse selection. Compare the relevant item against those boundaries: absent from scanned IDs means a list/eligibility miss; present but below ADC top-R means compression/shortlist loss; present after refinement but outside top-k means exact rerank loss; final but absent from context means packing loss. Do not invent a context stage for synthetic geometry.

All measured request samples in fresh Chapters 10-16 replays use the envelope, alongside their existing quality cases and aggregate timing arrays. The historical result files are unchanged and explicitly retain their historical schema/hashes; [the sealed registry](../projects/common/HISTORICAL_RESULTS.json) checks that preservation. New runs use explicit local output paths. Corpus/model loading and batch index-build experiments precede request identity and keep their existing aggregate provenance; they are not claimed as request traces.

```powershell
python -X utf8 -m unittest discover -s projects/common -p 'test_experiment_trace.py' -v
python -X utf8 -m unittest discover -s projects/V4 -p 'test_trace_shortlists.py' -v
```

Invalid/failed operations emit generic reason codes before re-raising. Preflight failure before a query is identified remains an experiment setup error. Never copy protected D10 source content into ordinary diagnostics; tests exercise both exception redaction and candidate-ID isolation.
