# Chapter 19 solutions — source ingestion and document quality

Attempt [the lab](../labs/chapter-19/LAB.md) before consulting this file. These answers explain the mechanism; they do not substitute for your independently written mapper or prove delayed mastery.

## 1. The independent mapper

The separate [implementation](code/chapter_19_mechanisms.py) validates the complete ordered map before processing a request. For each block it computes `max(start,block_start)` and `min(end,block_end)`, emitting only a positive intersection. It returns whole source locators. Overlapping maps are invalid even when the requested span would miss the overlapping region; otherwise behavior would depend on what happened to be requested first.

For `[2,7)`, output a/page 1 `[2,3)` and b/page 2 `[5,7)`. For `[3,5)`, output nothing: both code points are canonical separators. For chapter exercise `[1,6)`, output `[1,3)` and `[5,6)`. A zero-width span is invalid rather than a successful empty result. The scan is O(B), and its output uses O(H) space. Returning a box narrower than the supplied source locator would invent precision that the map does not contain.

## 2. Normalization arithmetic

Decomposed `cafe` plus combining acute has five code points and six UTF-8 bytes: four ASCII bytes plus two for the combining mark. NFC `café` has four code points and five bytes: three ASCII bytes plus two for é. NFC preserves canonical equivalence; it does not preserve offset identity. Neither count is a model-token count or a count of grapheme clusters.

The code block remains `if approved:\n    restart()`, with its internal newline and four indentation spaces. A prose whitespace collapse would lose this relationship. Roman numeral IV is not compatibility-folded by the declared NFC policy. Identifiers, numbers, punctuation and negation remain significant source evidence.

## 3. Source inspection and extraction failure

The Markdown runbook contains the release heading, restart negation, accented ownership statement and indented code. The HTML table attaches East to 2 and West to 4, with a separate HTTP 403 exception. The born-digital contract has two body statements on pages1/2. The scanned amendment visually supplies 15 days while having no native text layer.

Five baseline failures are table association loss, navigation/script contamination, code indentation collapse, canonical-accent mismatch and file-only provenance. A correct source-ID hit on an accented or table question does not repair the evidence. Nonempty native text on a page with a chart image likewise does not establish chart coverage: the lab's native-text gate is limited.

## 4. The experiment's denominators and decision

For **`ch19-source-quality-v1`**, eight inspected source-span requirements give flat preservation 5/8 and structured 7/8. Traceable preservation is 0/8 and 7/8 because flat locators are file-only. Alias-aware source Hit@1 stays 6/8 in both. These span requirements are not complete graded block qrels; the lexical source diagnostic is deliberately weak. No held-out, production or cross-workload improvement claim follows.

There are nine descriptors, seven licensed scope-eligible inputs and two policy blocks. Flat accepts 5/quarantines 2; structured accepts 4/quarantines 3. The stricter merged-cell rejection reduces acceptance while preventing an unvalidated relationship from becoming published evidence. Keeping the scan's requirement in the denominator makes its missing evidence visible.

The checked mixed-attempt p95 values are 8.5449 ms/9.0036 ms flat/structured; each mode has 27 observations including blocks/quarantines. Nearest-rank p95 selects `ceil(.95*27)=26`. These attempts mix source sizes/statuses and have only three repeats/descriptor, so they cannot establish a general speed comparison. The eight lexical timings/mode are separate. Preserve your local durations with their own environment/window rather than replacing the checked record.

## 5. Localize the four requested failures

- `table`: the flat route retrieves S-html, but lacks the specified header/value relationship. Structured serialization repairs the preservation requirement, not source Hit@1.
- `unicode`: both retrieve S-copy; flat has the decomposed raw accent and fails the declared NFC canonical-span requirement. This is a representation-policy mismatch, not loss of all accent-related source meaning. Structured NFC satisfies the requirement.
- `clock`: the statement survives in S-pdf, but final lexical top 1 is S-copy. Inspect all scored sources, the positive pool and the ID tie rule; this is ranking loss after successful extraction.
- `retention`: the image-only S-scan is quarantined in both routes. The diagnostic returns S-pdf through lexical overlap. It is an unsupported candidate for this requirement. No generation or abstention occurred.

For actual request IDs, use the checked or local record; IDs are unique per run. Do not copy IDs from an unrelated run into your failure card.

## 6. Trace the PDF unit

`[24,53)` is S-pdf:b1, `First response is four hours.` Its saved locator is page 1 and approximately `[54.0,129.10,202.72,145.59]` in unrotated PyMuPDF top-left points. Retain full precision from the artifact and the source/version/digests. The source generator's bottom-left coordinates are not the parser coordinates. The native block bbox encloses a region; it does not provide a per-character inverse normalization map.

`[50,80)` intersects b1 `[50,53)` on page 1, b2 `[55,72)` on page 2 and b3 `[74,80)` on page 2. Gaps `[53,55)` and `[72,74)` are inserted separators. A single-page citation would omit part of this fixed unit. This exercise uses existing parser blocks; it does not optimize chunk sizes or overlap.

## 7. Quarantine and repair

`native_text_absent_requires_ocr_review`: inspect the page image, select a reviewed OCR route or a manually transcribed governed source, preserve derived-text provenance, and rejudge affected requirements. `invalid_utf8`: check original encoding/capture integrity; do not silently substitute a replacement character. `ambiguous_table_geometry`: recover a cell grid with row/column spans and header associations, or retain quarantine. None is a relevance judgment.

A real partial-publication route must identify known missing regions and constrain downstream claims. The current PDF adapter chooses all-or-quarantine when a page lacks native text; it has no reviewed blank-page exception and cannot certify all image content when some text exists.

## 8. Boilerplate counterexample

Place `Cancellation within 24 hours is excluded from refunds.` in the only footer. A blanket footer removal erases the exception. A useful new requirement asks about that exclusion and binds its original locator/content before modifying the policy. Review whether the footer contains repeated navigation, evidence or both. Recurrence and position alone do not establish irrelevance.

## 9. Exact duplicate and deletion defense

S-copy/S-md have equal canonical bodies and matching policy fields, so they form an exact duplicate group. Their record digests differ because source IDs/lineage differ. Both records remain. With different scope/license/retention, the key differs; the current code does not group them. A production shared-vector representation still requires policy-gated alias lookup and source-specific lifecycle state.

Deleting one alias must invalidate derived objects owned only by it while preserving independently authorized aliases. Expiration, index/cache propagation and backups need a later lifecycle mechanism. Identical text is not permission to union tenants' scope lists or overwrite the shorter retention policy. Near duplicates containing changed numbers/dates/signatures need separate evidence review.

## 10. Cost arithmetic and sampling

At 10,000 pages, .02 seconds/page gives 200 seconds native serial work; .8 seconds/page gives 8,000 seconds OCR, a factor 40 under those hypothetical assumptions. Excluded costs include setup, I/O, queueing, concurrency contention, retry, manual review and retained storage. These invented values are not local measurements.

A possible 60-source sample allocates15 each to Markdown/HTML/born-digital PDF/mixed-or-scanned PDF. Within each stratum include successful and failed/quarantined cases, larger and smaller sources and relevant languages. Randomly select within declared strata, record the actual roster and compare rendered source→raw extraction→canonical output. Equal allocation supports slice inspection; it does not estimate corpus-wide averages without accounting for actual population proportions. The small sample and single-reviewer judgments leave uncertainty. Do not select only files that parsed successfully.

## 11. Publication card and learning rubric

Publish the four structured accepted canonical records for V5 development; preserve duplicate aliases and dropped-region reports. Keep scan, broken UTF-8 and merged cells quarantined; block unapproved indexing use/ineligible scope before reads. Required-span traceability passes for all retained requirements, but extraction coverage remains 7/8. No queue, OCR, chunk-design comparison, embedding/index write, visibility or generator was run. The source hashes and parser/normalization record identities are the new upstream contract for later chapters.

Use the lab's 25/25/30/20 weighting for construction, source reasoning, evaluation/telemetry and governance. An 80% suggestion does not override the eligibility, stale-label, fabricated-OCR or invented-offset correction gates. Day1/3/7/21 recall tasks remain learner assignments. Chapter20 is not part of this completion.
