# Chapter 5 lab — worked solutions and review notes

These answers refer to the frozen [five-record fixture](../projects/V1/toy_corpus.json) and the [V1 code](../projects/V1/lexical_index.py). Timing values are one recorded run; local timings may differ.

## A. Hand index and Boolean queries

`S1` body: `helios@0 pro@1 hx-7a@2 reset@3 guide@4`. `S3` body: `legacy@0 hx-7a@1 reset@2 guide@3`. `S1` also has `manual@0` in the *title*, independent of body position zero.

| Term | Body postings with positions (including internally indexed `S5`) |
|---|---|
| `hx-7a` | `S1:[2], S2:[2], S3:[1], S5:[0]` |
| `guide` | `S1:[4], S3:[3], S4:[5]` |
| `reset` | `S1:[3], S2:[3], S3:[2], S4:[4], S5:[1]` |
| `legacy` | `S3:[0]` |

Each listed term occurs once in each listed body, so its body term frequency there is one. `S5` is removed by `support-team` membership before a source-text fetch or score. Support-scope phrase matches: `reset guide` → `S1,S3,S4`; `guide reset` → none; `hx-7a reset` → `S1,S2,S3`; `manual helios` → none because the words are in different fields. The title/body boundary is as important as the arithmetic difference between positions.

Boolean results at support scope: `hx-7a AND guide` → `S1,S3`; `checklist OR legacy` → `S2,S3`; `(checklist OR legacy) NOT legacy` → `S2`; `hx-7a AND NOT legacy` → `S1,S2`. NOT subtracts from a declared positive and eligible set. An unanchored NOT is rejected.

For the unfiltered two-cursor example, compare `S1/S1` (emit), `S2/S3` (advance left), `S3/S3` (emit), `S5/S4` (advance right), then stop: four ID comparisons, result `S1,S3`. Filtering `S5` first leaves the same result and can remove one later cursor state; with these exact lists the process ends after comparing `S3/S3`, so three comparisons. A set implementation may use a different number of hash probes; this count describes the stated sorted-cursor algorithm.

## B. Program trace and repeated phrase

`build_index()` uses V0's 13 prepared segments, maps each title/body term occurrence to an ordinal and field position, then freezes ordered posting tuples and scope sets. It records `S1`'s analyzed lengths as title 1 and body 5. The V0-analyzer snapshot has **119 terms, 222 term–segment pairs and 247 positions**. The measured index-build time in the checked-in run was **0.561 ms**; a single value is not a distribution. `search()` checks `posting.ordinal in eligible` before adding that ordinal to `matched` and before reading its forward text. `phrase_ids()` chooses either `title_positions` or `body_positions`, never their concatenation. With a temporary `go go now` body, positions `go:[0,1]` and `now:[2]` make `go go` and `go now` match, while `go go go` lacks position 2 for `go`.

## C. Analyzer outcomes

`HX-7A` returns eligible `S1,S2,S3`; `HX-7C` and the misspelling `resett` return no exact match. The code is one hyphen-preserving term in this fixture. `S4` contains precomposed `café`; `unicode_nfc` matches both that query and decomposed `cafe` + U+0301 after normalization, while V0's ASCII regex produces different fragments for those two spellings. The best product-code policy here is an exact identifier field plus explicit, reviewed alias or fuzzy fallback; a broad edit-distance match can wrongly cross from `HX-7A` to `HX-7B`. A regression query must demand the right ID and reject the wrong one.

Dropping `not` can collapse `eligible` and `not eligible`; stemming can merge domain-distinct forms; NFKC can fold compatibility characters that the source uses as identifiers. These are potential collisions, not measured failures of this five-record fixture. Retain source text, test domain examples and version the analyzer.

## D. Experiment interpretation

The [raw experiment](../projects/V1/chapter-05-experiment.json) uses seed `5042026`, top eight, four fixed query IDs and nine timed samples per method/query. All checked top-eight ID/score lists agree exactly at 13, 130 and 1,300 segments. The two frozen V0 answer tests also agree at candidate depths 1, 2 and 8. In the 13-segment snapshot, the contract-change query visits 57 eligible postings and scores all 12 eligible segments; rare numeric visits two postings and scores one; no-result visits none and scores none. At 1,300 segments, those counts scale to 5,700/1,200; 200/100; and 0/0. The common query is the important counterexample to “the index always avoids scoring most documents.”

One possible experiment-card conclusion: **Question:** Can postings preserve V0 results while reducing term-processing work? **Hypothesis:** exact top-eight agreement and fewer scored segments for selective terms; no guarantee for common terms. **Baseline:** V0 scan. **Change:** posting lookup with the same analyzer and score. **Controls:** scope, snapshot wording, top eight, four queries, seed and copy counts. **Result:** exact candidate/score agreement on every checked row; selective-term work falls, common-term score count does not. In one run at 13 segments, rare-query median was 59.4 µs for scan versus 3.9 µs for postings; at 1,300, 6,216.1 versus 153.2 µs. Build time was 0.561 and 54.390 ms at those sizes. **Decision:** keep as a mechanistic V1 preview, then add judged quality and realistic workloads. **Limits:** synthetic duplicate content, single machine/process, nine timing samples, no production concurrency or storage bytes, no relevance qrels, no LLM outcome. A local slower result should be retained, not hidden.

## E. First broken boundary

If `S5` reaches a support candidate or ordinary trace, eligibility has already failed at candidate creation/logging; hiding it in the answer is too late. Inspect the scope source, scope membership version, posting filter, trace serializer and cached result, and rerun a negative authorization test. A leaked restricted ID is a security incident even without leaked source text.

If `D2` is absent, inspect source snapshot and `D2` segment ID; analyze the query and indexed fields using the same analyzer version; inspect eligibility membership; inspect candidate IDs and rank versus top-k; inspect selected context IDs versus budget; then inspect V0's exact-clause result. Chapter 9 introduces qrels and formal retrieval metrics. The absent-query timing is only one narrow search-stage slice; end-to-end RAG includes context and generation, and nine local samples cannot establish a production speed factor. The contract-change row scored every eligible segment.

## F. Boundaries

Figure 5.01 separates inverted, forward and scope stores at index time. Figure 5.02 filters term hits by scope before intersection output and source fetch. Position `3` means the fourth **analyzed term in one field**; it lacks original punctuation, byte offset, casing and version unless joined to the forward record. An analyzer change invalidates term keys and positions, so build a new version. A permission revocation must be enforced in the serving eligibility policy immediately, with index/cache invalidation or a live policy check; waiting for an offline rebuild risks exposure. V0 and V1 share a deterministic two-task stub, not a general LLM or claim verifier.
