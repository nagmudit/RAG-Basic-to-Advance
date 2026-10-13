# Chapter 20 solutions — chunking as a retrieval decision

Attempt [the lab](../labs/chapter-20/LAB.md) before reading these answers. The separately written [chunker](code/chapter_20_mechanisms.py) imports neither learner nor project code. Running it is a feedback step, not your independent construction. Delayed tasks remain learner assignments.

## 1. Window construction and coordinates

For ` A  BB\nCCC D E `, word spans are `[1,2)`, `[4,6)`, `[7,10)`, `[11,12)` and `[13,14)`. Length3/overlap1 emits `[1,10)`, `[7,14)`; length2/overlap0 emits `[1,6)`, `[7,12)`, `[13,14)`. Original repeated spaces/newlines survive in the copied substrings. Split-and-rejoin would create a new coordinate space.

Validate positive integer size and integer `0<=overlap<size`, excluding booleans. Advance `size-overlap`; emit the first final shortened window and stop. For five words with length3/overlap1, two windows suffice; do not emit another copy of the last word. Whitespace-only input emits nothing. O(T) matching plus O(C) interval output does not include the additional cost of copying/encoding repeated text.

For19 words, length8, overlap3, stride5: starts0/5/10/15; intervals `[0,8)`,`[5,13)`,`[10,18)`,`[15,19)`. The tail has four words. `1+ceil((19-8)/5)=4` windows emit28 word assignments, cover19 unique words and repeat9: duplicate-assignment fraction9/28. This is not the code-point redundancy metric or a model-token count.

## 2. Overlap arithmetic and span coverage

Large-source assignment factor `1/(1-O/L)` gives4/3 at25% and2 at50%. Tails, source structure and copied prefixes alter exact counts. Larger overlap approaches zero progress; equality with length is invalid. Even a beneficial boundary rescue has a vector/input/context cost.

For `[0,6)`,`[4,10)` over ten nonwhitespace characters, emitted count12 and union10 give duplicate fraction2/12. Requirement `[3,8)` is covered jointly; either single interval misses part. The implementation unions positions before determining full atoms. Whitespace-only gaps are ignored by the declared evidence metric. Overlap or equal governed aliases cannot inflate coverage by counting the same position twice.

## 3. Units, tokens and encoding limits

The independent chunker counts whitespace words and returns canonical code-point offsets. Character windows count code points. The pinned tokenizer counts WordPieces; rare identifiers can expand into several. Actual indexed inputs include two special tokens and have maximum123, below the encoder's256 limit. The full operations parent has517 without specials: counting is not a transformer forward pass, and the parent is not encoded.

The packing proxy sums encoder WordPieces without each item's specials and allows80. It is not a generator prompt budget. A generator would need its own full prompt/token/output accounting. Correct boundary offsets, actual model visibility and selected context capacity are separate gates.

## 4. Same judged questions, distinct measurement layers

For **`ch20-chunked-evidence-v1`**, twelve questions have ten positives/eighteen required atoms and two no-evidence cases. Source-span judgments bind actual source/record/policy identities and original anchors. They are independent of the chunk roster. Atom recall is fully covered required atoms divided by that question's atoms; the headline averages ten per-question values, not all eighteen atoms as one micro fraction. Complete context evidence requires every atom for a question.

Candidate top3 versus packed-context recall is .800/.7667 for word24, .8667/.7833 for overlap, .900/.8667 for word48,1/.400 for word96 and1/.900 for structure48. Whole-parent expansion shares word24 child rankings and falls to .400 context recall. Char128 gives .700/.700. The inspected winner remains provisional.

Mean context duplication averages all twelve queries: overlap .0914 versus .0417 for ordinary windows, structure .0362. Exact-copy alias equality includes body and scope/license/retention; other similar sources cannot be merged casually. Both no-evidence questions return candidates in every mode,2/2. No answer, citation-support, faithfulness or abstention result follows.

No train/dev/test split exists here. The corpus includes known fictional procedures and inspected questions. Selecting structure48 is a development decision, not held-out validation or a claim of improvement over Chapter19/V3/V4 metrics with incompatible denominators/input policies.

## 5. Trace the first losses

- `green-fail`, overlap: all atoms reach candidates; selected units cost29/28, but the next27 would total84. The budget rejects it, leaving one of two atoms. Inspect the saved packing reason, not an imagined search miss.
- `drill`, word24: three candidate atoms are covered; units31/27 fit, next31 fails, leaving2/3 in context. The needed span is identifiable through contributing chunk IDs, source range and original Markdown lines.
- `green-wait`, structure48: all atoms reach top3, but the selected58-WordPiece unit lacks both required atoms;61/55 do not fit afterward. This case's context recall0 remains in the .900 average.
- `word24-parent`: the child IDs/scores are unchanged. A517-WordPiece S-ops parent is rejected; later children point to the same attempted parent and receive duplicate-parent dispositions. Expansion is not a new relevance score or parent embedding.

A possible repair is a bounded section/neighbor expansion or an explicit alternative packing policy. Freeze a regression case and measure the new mechanism before claiming that it works. The current result contains neither a repair nor a hidden deeper search fallback.

## 6. Source and citation lineage

For each chosen unit, retain source/version/raw digest, canonical-record/chunker/model/input identities, exact body range/text digest and every intersecting original anchor. A PDF chunk crossing pages has multiple page/bbox locators. Each bbox covers a native source block; normalization can prevent exact inverse character mapping. A Markdown range similarly maps to original line regions.

Position coverage establishes that source evidence is available; it does not establish that fragments were read coherently or that an answer cited the right claim. A claim-level citation audit compares the actual generated claim with its cited original region. That stage is not run. Do not label a correct chunk map citation accuracy.

## 7. Context mechanisms and source-support risk

Parent expansion matches a child then selects larger original text at query time, with source/version/eligibility and budget checks. A deterministic heading prefix changes encoded input at index time using source-derived heading ranges. A generated contextual description changes that input with derived text that needs support checks; retain it separately from evidence.

A summary tree indexes derived representations at multiple scales and must retain links to original leaves and summary-error provenance. Late chunking computes contextual token states over a suitable larger input, then pools states for each chunk. Independently encoding chunks with ordinary mean pooling is not late chunking. Neither a whole parent nor a copied title changes the timing of transformer contextualization.

The current code executes conventional body-only chunk embeddings and full-original-parent expansion. Other mechanisms are conceptual/research comparisons. Use the paper path's prerequisites for full research reading; do not import external benchmark gains into the local table.

## 8. Index and cost interpretation

Word24 has22 vectors/671 actual encoded WordPieces; overlap31/939. Float32 coordinate payload is `22*384*4=33,792` bytes versus47,616; the .333 overlap fraction does not guarantee a1.5 expansion on short heterogeneous documents. Actual vector-count ratio31/22 and input ratio939/671 are different measures. Structure48 also has31 vectors but689 encoded WordPieces, demonstrating uneven structural lengths.

Word96 has nine vectors/13,824 coordinate bytes and full candidate coverage, yet only .400 context recall. Smaller index/query work is not sufficient evidence of a better RAG pipeline. Recorded one-build embedding times and36 tiny search samples/mode are not general service capacity or monetary costs. Parent mode creates zero new vectors, but the teaching JSON serializes its shared rows again. JSON bytes and RSS are not the packed-coordinate payload.

The saved verifier compares the snapshot with independently expected digest/model/source identity, generated chunk roster/maps, vector shapes/norms and index versions. Eighty-four mode/query checks replay ordered candidates. Updating a digest from the file being checked would remove the independent trust condition.

## 9. A bounded expansion defense

An implementable later policy could expand each top child to its verified containing section, deduplicate repeated section IDs, cap section/neighbor size, recheck eligibility/version, and retain causes plus budget/stopping reasons. If the section is too large, select declared source-preserving neighboring units rather than silently truncating a condition. Test cross-section exceptions, stale parents, different scopes, duplicates and cases where no available evidence fits. This is a proposed mechanism, not a completed Chapter21/28 implementation.

Source, parser, chunker or input-policy changes can invalidate ranges, vectors and judgments. Retain versioned manifests, original snapshots and exact baselines. Cache keys need model/input/chunker/source/policy identity, with tenant-safe lookup and invalidation. Metadata/update lifecycle is the next dependency; no live propagation is claimed here.

## 10. Learning and evaluation defense

For a real corpus, create representative development questions for parameter selection, then freeze model/boundaries/cutoffs/budgets before reviewing a separate test set. Identify whether sources/families/time are disjoint and what generalization that split can support. Preserve hard slices, no-evidence cases and human disagreements. Do not silently move failed test questions into development and keep the same claim.

Suggested lab rubric: construction25%, math/units20%, experiment/trace diagnosis35%, design/continuity20%, with an80% teaching threshold. Correct authorization, stale-label, invented-offset and fabricated-model/answer failures regardless of total. Submit your independent first attempt and own fixture, not just reference output. Day1/3/7/21 tasks are delayed practice, not automatic mastery. Part V's cumulative checkpoint remains after Chapter22; Chapter21 is not started.
