# Chapter 17 solutions — Bounded exploration and an honest graph decision

Use after attempting the [lab](../labs/chapter-17/LAB.md). The independent construction is required; reference execution alone does not earn its credit. Timings below are descriptive of the [checked observation](../projects/V4/chapter-17-experiment.json), not expected values for a replay.

## A0. Independent construction

The [bounded answer](code/chapter_17_mechanisms.py) imports no complete graph engine. It maintains a nearest-first frontier, visited set and sorted retained list. After a score is admitted, retain only the best `ef` pairs; after popping, stop only if the pool is full and the popped pair is worse than its worst pair. A distance tie uses the ID. The sorted list costs order `ef` insertion/copy work; the full engine's worst-first heap reduces this part to logarithmic heap updates. Both must retain the same search invariant.

```powershell
python -X utf8 labs/chapter-17/check_implementation.py --implementation solutions/code/chapter_17_mechanisms.py
```

Expected feedback includes local-minimum failure, frontier recovery, cycle/tie/disconnection behavior and diversity selection. In the fresh checker, width one returns `near`, width two returns `goal`, and all four vertices are scored at width two. Removing the bridge→goal edge leaves `near` first even at width ten. Returning a low score without reaching the missing vertex is not an exactness certificate.

For diversity, `p=(1,0)` is selected, `redundant=(1.2,.1)` rejected because `.05<1.45`, and `other=(0,2)` accepted because `5≥4`. A solution that simply selects the closest two passes neither the mechanism nor the fixture.

## A. Hand mechanics

**4. Four-vertex trace — `ch17-frontier-fixture-v1`.** At width one, expanding B scores C:1.21 and rejects it against retained B:1. D is undiscovered. At width two, expanding A retains B,A; expanding B admits C and evicts A; expanding C admits D and evicts C; expanding D discovers nothing new. Return D:.01 as top one. Both evaluated distance arithmetic and neighbor ID ordering remain exact, while the narrow exploration is approximate. Removing C→D makes D unreachable from A; width cannot create an edge.

**5. Random levels.** For `M=4`, the tail probabilities are `1,1/4,1/16`. At `N=1,024`, expected populations are `1,024,256,64`, then 16,4,1. Expected upper memberships per vertex are `1/(4−1)=1/3`. `U=.8,.2,.01` produces levels `0,1,3`: the last has `−ln(.01)/ln(4)≈3.322`. Actual populations fluctuate. Levels are random navigation roles, not relevance/authority labels. The seed, order and level distribution must be versioned.

**6. Hierarchy.** The forced example has A at layer two; A,C,F at layer one; A through H at layer zero. Upper expansion starts A then follows A,C,F at layer one. Carry F into the base, where expansion order is F,G,H,E. Squared query distances are F `2.93`, G `.53`, H `.13`, E `7.93`. Width four retains enough room for E; base expansion is not one strictly descending path. Output H,G. Compare against [the actual trace](../visuals/chapter-17/hierarchy-example.json), not an imagined fully connected upper layer.

**7. Insert I `(6.5,0)`, level zero.** Greedy upper routing enters the base at F. Construction width twelve discovers all eight old vertices; the pool in nearest order is `G,H,F,E,D,C,B,A`. G and H are tied at squared distance `.25`; stable ID order selects G first. H is accepted because `d²(H,G)=1≥d²(H,I)=.25`. With two links selected, stop selection. Add I→G,H; G's outgoing list becomes F,H,I and H's becomes G,I. No old list exceeds base capacity four, so no pruning occurs in this insertion. A valid answer records that no pruning was required rather than inventing a shrink event. I belongs only to layer zero, and A remains the highest entry.

**8. Diversity arithmetic.** From center zero, P,Q,R distances are `1,1.45,4`. P accepted; Q rejected by `.05<1.45`; R accepted by `5≥4`. Nearest-only selects P,Q. Preserving another direction can help navigation, but this three-point exercise does not measure a retrieval gain. Refill and candidate extension are separate policy choices.

## B. Controlled comparisons

**9. Width grid — `ch16-synthetic-n1024-d32-v1`.** All graphs below have construction width 32 and seed `17022026`; each row changes width on its fixed graph. Geometric Recall@2 is the mean of sixteen fractions with denominator two.

| M | Recall at e=2 / 8 / 24 | Mean scored vectors at e=2 / 8 / 24 |
|---|---|---|
| 2 | .094 / .125 / .250 | 15.4 / 32.1 / 74.0 |
| 4 | .188 / .406 / .781 | 31.9 / 76.8 / 158.3 |
| 8 | .344 / .594 / .969 | 56.9 / 129.3 / 256.0 |

Use saved `search_only_timing` for your p50/p95 table. Width improves this measured aggregate, not a universal theorem. M changes both capacities and `P(L≥l)` in this engine, so the across-M comparison does not isolate degree alone. The higher-dimensional synthetic geometry has no relevance or answer labels.

**10. Construction ablation — same workload.** At M=4 and query width 24, construction widths 8/32 produce Recall@2 `.625/.781`, adjacency entries `7,237/7,658`, and identical level populations `[1024,247,68,14,4]`. Saved build times are single local observations. The query-to-existing counter excludes neighbor-diversity distance work; total build wall time includes it. A new graph seed over unchanged queries/corpus is a new index/experiment identity on the same workload; changing query/corpus/judgment semantics requires a new registry entry. Do not call any of these inspected measurements an untouched test.

**11. Payload — same workload.** Vectors contribute 131,072 bytes; maximum levels contribute 4,096. M=2/4/8 gives `5,070/7,658/13,289` directed entries, or `20,280/30,632/53,156` adjacency bytes at four bytes/entry. Three-component totals are `155,448/165,800/188,324` bytes. Excluded costs include string-to-internal-ID maps, adjacency offsets/reserved capacity, Python objects, scopes, replicas and traces. The vectors are retained originals; no two-byte PQ code replaces them. Actual process memory needs measurement.

**12. Controls — same workload.** Fresh one-probe IVF-Flat reaches `.219` geometric recall and scores 68.9 vectors/query; all-probe Flat and exhaustive agree on every ordered top two. Both full scans score 1,024 vectors. The fresh IVF uses this chapter's seed and training choices, so its centroids differ from the historical Chapter 16 construction. Same-vector oracles can be compared; unmatched historical timings cannot establish an improvement. Registry labels preserve identity while the new record corrects the synthetic generator description: each query coordinate selects its stored row independently. No single planted neighbor is promised.

## C. Trace-led failure localization

**13. `synth-07` — `ch16-synthetic-n1024-d32-v1`.** Exact IDs are `s00001,s00352`; `m8_c32_e24` returns `s00001,s00931`. `s00352` does not occur in the actual raw scored IDs: it is undiscovered, not a final-cutoff or score-refinement error. Join the case's `request_id` to the sample with `trial_id="quality"`, initialize the recorded queues, and apply each pop/admission/eviction. The test suite performs this replay and checks final layer pools. The missing membership is preserved; 31 of 32 memberships produce `.96875`, reported `.969`.

**14. `code-sev` — `ch13-stress-probes-v1`.** Exact returns `D8:§3:0,D1:§3:0`; `m2_c32_e2` returns `D1:§3:0,D3:FAQ-7:0`, losing the direct D8 result. `m4_c32_e24` restores the exact pair. The M=2 graph's highest entry is `D9:proposal-2:0`; this request carries `D1:§3:0` into layer zero. Base outgoing traversal from that region reaches eight vertices and excludes the three D4 vertices and D8. The raw pool nevertheless includes `D4:step-4:0`, scored in an upper layer; raw scoring and base reachability are distinct diagnostics. D8 is never scored. Query-width growth cannot repair a missing outgoing route. Some questions can enter another region through upper layers, so global base reachability alone is not a universal per-query recall prediction.

**15. Exact representation failures — same workload.** `code-segment`'s direct target is `D6:row-2:0`; its identifier is metadata, absent from the searchable body/title route, and the exact top two are D4 segments. `acronym-sla`'s directly governing current signed amendment is `D2:§2:0`; exact returns D1/D5 instead. Geometric parity preserves these failures. Use exact identifier/metadata routing or appropriately evaluated representation/ranking changes; increasing graph width at the same top two cannot reorder the exhaustive oracle. Context selection and generation require their own evidence; null answer fields must stay null.

**16. No-evidence questions — same workload.** Both `none-private` and `none-orion` return candidates under every measured route. The zero-positive candidate-return rate is `1` over two questions; judged recall for those questions is undefined, not zero or one. D10 is absent from graph membership/scoring/context. Completion `ok` says the search operation ran correctly, not that it found evidence. A calibrated no-result threshold needs representative positive/no-evidence questions, frozen model/metric/eligibility and separate development/test semantics. No threshold or answer abstention was measured here.

## D. Operation and decision

**17. Delete/reload.** Tombstones block scoring/traversal immediately in this engine but retain vectors/edges in memory/snapshots. A bridge deletion can disconnect a required route; entry deletion invokes a surviving-highest-entry scan. Rebuild or repair is necessary before promising restored recall. The checked reload verifies caller-provided digest and source version; editing the file and its own hash cannot substitute for the trusted expected digest. Query-only reload avoids claiming a persisted RNG/mutation lifecycle. A physical-erasure/retention obligation requires more than a tombstone.

**18. Scope change.** Authenticate upstream, create a trusted eligible roster, build/routinely select a graph for that policy version, and invalidate incompatible tenant/index/model cache entries. Match its oracle to the same roster. Verify that all raw scored/intermediate/final/context IDs are eligible and measure recall after removing forbidden bridges. Retain protected diagnostics under access control. Postfiltering returned results fails to prove the stronger before-scoring boundary.

**19. Decision card.** Retain V3 exact dense and V2 BM25 as operational baselines. On `ch13-stress-probes-v1`, exact and `M=4,c=32,e=24` have judged macro Recall@2 `.792`; the graph reaches geometric parity while adding local overhead. Query encoding remains much larger than twelve-vector scoring. On `ch16-synthetic-n1024-d32-v1`, the best tested graph reduces work with `.969` geometric recall and a surviving miss, but has no human labels. Adoption needs representative independent judged questions, per-slice quality gates, matched service timing/load, measured resident/storage bytes, update/delete/eligibility tests and a recovery/fallback plan. No correctness, faithfulness, citations or abstention gain has been evaluated.

## Assessment rubric

Award construction credit for the learner's own mechanism and explanation of invariants; require trace-backed classification of misses. Accept any correctly bounded data structure with an honest complexity account. Deduct for treating `ef` as a visit limit, claiming universal logarithmic search, equating geometric with judged recall, cross-workload gain claims, or scoring restricted vertices. The final recommendation may reject the graph. Confidence about a recommendation must come from evidence and named limitations, not a preferred algorithm.
