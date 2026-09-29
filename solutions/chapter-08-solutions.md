# Chapter 08 lab — Worked solutions

Try the [lab](../labs/chapter-08/LAB.md) before reading this file. Numeric examples use the Chapter 7 BM25 settings and the fictional support-team fixture. Display rounding never defines a rank.

## 1. Bytes and cursor movement

The gaps are `[3,5,130]`. The first two each fit in seven payload bits and end with a high-bit-1 byte: hexadecimal `83` and `85`. `130=1×128+2`, so its payload groups are `01,02`; the first byte has high bit 0, the final byte high bit 1: `01 82`. The stream is `83 85 01 82`. Decode to gaps `3,5,130`, then prefix-sum to IDs `3,8,138`. A continuation-bit-1 convention would use different bytes; a decoder must know which convention was written. The toy codec rejects zero/descending IDs and unterminated integers.

For the intersection, compare `(1,2)` and advance A; `(3,2)` and advance B; `(3,3)` emit 3 and advance both; `(8,9)` advance A; `(11,9)` advance B; `(11,11)` emit 11. The OR union is `[1,2,3,8,9,11]`. BM25 on the posting union permits one-term matches; AND would exclude IDs 1, 2, 8 and 9 before scoring, so it is a different retrieval rule. A posting might contain `(docID=8, title_tf=1, body_tf=2, title_positions=[0], body_positions=[4,9])`. The Chapter 7 scorer needs field counts and analyzed length; a phrase check needs positions. Compression can reduce disk read/cache footprint and adds decode CPU.

## 2. WAND's proof on the toy

P1 scores about `1.093526829`, so a full top-one heap has `θ=1.093526829`. `U_common≈0.256130736`, less than `θ`; P2 cannot win on `common` alone. A candidate with score exactly `θ` may have a better stable tie key, so a score-only bound must keep `≥ θ` eligible. The `rare` cursor's next ID is P6, the pivot. The `common` cursor moves from P2 to P6, advancing four entries: P2 through P5. Cached exhaustive execution fully scores six support-team candidates; WAND fully scores P1 and P6. P6's contributions are about `0.796791+0.186628≈0.983419`, below P1. P7 is never eligible.

For conceptual two-ID blocks, B2 contains only common contributions, with upper bound `0.256`; B3's sum of per-term block maxima is about `0.256+0.797=1.053`; both are below `θ≈1.094`. A correct block-aware algorithm could skip those ranges after P1. Our global WAND has `U_rare≈1.094` and `U_common≈0.256` across the **whole** scope, so it cannot infer B3's tighter maximum and scores P6. B1's bound `≈1.350` adds `rare`'s P1 maximum and `common`'s P2 maximum, although no B1 document has both. A loose upper bound is still safe.

The invariant is `S(q,d)=Σ_{t∈q∩d}w(t,d)≤Σ_{t∈q∩d}U_t`, assuming nonnegative impacts and `U_t≥w(t,d)` for every still eligible candidate. To skip, the possible sum for all unseen IDs in the skipped range must be **strictly less** than the full heap's `θ`, unless a stronger proof also includes the exact tie key. Bounds and scores must use the same analyzer, corpus/segment snapshot, length and frequency statistics, BM25 parameters, field policy, scope and live-document set. Float handling must be conservative enough for the actual scorer.

## 3. Experiment interpretation

The [checked-in result](../projects/V2/chapter-08-experiment.json) recorded exact ordered top-*k* IDs and unrounded scores against direct Chapter 7 BM25 for every five-query, three-depth case. Your local microsecond medians may vary. On the checked-in run:

| Query | *k* | Cached full scores → WAND | Median search-only time | Selected required evidence / stub |
|---|---:|---:|---:|---|
| Dated contract | 1 | 12 → 2 | 16.3 → 39.0 µs | 1/2; abstained |
| Dated contract | 2 | 12 → 9 | 14.6 → 98.9 µs | 1/2; abstained |
| No result | 1 | 0 → 0 | 2.9 → 3.2 µs | No required-span label or stub verdict |

The contract top-one ID is `D2 §2`; the top-two list is `D2 §2`, `D3 FAQ-7` under both plans. `D1 §3` remains outside context, so the stub abstains. The no-result query returns no candidates and has no judged stub verdict. Candidate IDs, raw scores, context IDs and stub status are identical between plans. The experiment supports exactness for its tested cases and fewer fully scored candidates for some cases. It rejects a latency improvement on this tiny Python/RAM workload and shows no improvement in evidence coverage or answer behavior. The V0 corpus has 13 indexed segments, 12 eligible in support-team; eleven local timing samples per method/case are search-only; there are no general qrels or LLM answer labels. One run's build costs and p95-like sample statistics cannot establish service tail performance.

A suitable experiment card names cached exhaustive as baseline, execution plan as the single variable, the Chapter 7 direct scorer as untimed oracle, frozen V0 source and five-query set, seed `8082026`, depths 1/2/8, exact ID/raw-score agreement, full-score and seek counts, raw timing samples, context coverage and stub status. It records the missing `D1 §3` as a ranking failure that both plans preserve. The conclusion is to retain WAND as a teaching proof and not claim a deployment speed gain from this fixture.

## 4. Failure diagnosis and design defense

If `U_rare=0.20` while a true contribution is about `1.094`, `U_rare≥w(rare,d)` is false. A prefix sum can now appear below `θ` even though a still unseen document could beat the heap. An exactness regression should compare ranked IDs and **unrounded** scores with exhaustive BM25 on a fixture whose hidden rare document must win; it should fail when the bound is corrupted. Include scoring, bounds and index versions plus cursor/seek counters in a protected trace. A shared cache that admits P7 violates eligibility and may leak a legal-only ID, statistics or source text even if P1 still wins. Test that P7 is absent from support-team candidate, impact and context paths and that scope-specific counts/bounds change only through authorized rebuilds. A permission update requires cache invalidation or a proven safe live-filter design. A segment merge or `k1`/`b`/field-policy change invalidates previously computed impacts or their mappings unless the new reader/version recomputes them.

For 13 segments, exhaustive accumulation can be faster and simpler: cursor sorting, seeks, bound checks and a heap exceed saved arithmetic in the checked-in run. MaxScore selects essential lists using remaining score potential; WAND uses sorted cursor pivots; Block-Max WAND uses tighter local range bounds; each can be exact with valid bounds and tie handling. A fixed posting budget is approximate unless a separate proof covers omitted candidates. The source snapshot and analyzer produce postings at index time, while V2 also caches scope-specific impacts and bounds. Query time checks eligibility, moves posting cursors, scores selected candidates, ranks top *k*, packs context and invokes the unchanged answer stub. Only the execution plan changes in Chapter 8; Chapter 9 supplies judged ranking quality.
