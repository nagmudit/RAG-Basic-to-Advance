# Chapter 22 — Worked solutions and Part V rubric

Attempt [the lab](../labs/chapter-22/LAB.md) before consulting this file or [the separate reducer answer](code/chapter_22_mechanisms.py). Neither imports the learner or running engine.

## Revision reducer

The fresh checker accepts revision 2, treats an identical repeat as duplicate, rejects revision 1 as stale, accepts deletion 3 and retains its revision/digest. Old revision 2 remains stale even with a new delivery identity. Explicit recreation 4 is a new source action and is accepted under the stated policy. Booleans as revision, empty digests and non-Boolean tombstones are invalid. Equal revision 3 with a changed deletion digest is a conflict. Copies preserve the original input states.

Deduplication by event ID and ordering by source revision answer different questions. Source payload identity includes permission metadata; identical body text does not make an ACL change redundant. A content hash distinguishes states but cannot tell which is newer. Tombstone retirement needs replay/replica/restore/caching evidence, not an arbitrary age alone.

## Actual edits, deletion and source-bound judgments

A06 revision 1 says 90 minutes, revision 2 says 9, revision 3 says 12. Their actual raw source bytes, canonical record/metadata/locators and retrieval-unit identities differ; the old files/labels are preserved. At 1500 both projections return revision 2. At 4200 both still score revision 2, but the known-revision barrier removes it because the trusted source authority requires revision 3. At 5300 ordered returns revision 3; last-arrival has regressed to revision 1 and the barrier removes its stale candidate.

A03 is deleted at source time 2000 and its tombstone is projected 2600. A late revision 1 replay at 5100 leaves ordered deletion 2 intact but replaces the arrival projection's head. Both serving routes deny A03 before scoring under current source authority. Deleted-history is also empty. A08's admin-only revision 2 is effective 3000/projected 3900; current reader access to its earlier revision 1 is denied. This does not prove physical erasure or instantaneous real-world permission propagation; the fixture has a deliberately current trusted authority.

For an own edited workload, re-review actual spans/origins/policy and register new identities. The old requirement must fail. The CLI supports separate updates/labels/registry; it does not silently relabel the book baseline. A renamed raw path changes its descriptor binding even if its body remains equal.

## Timing and measured outcomes

On **`ch22-versioned-evidence-v1`**, six positives comprise initial-current, updated-current, known-pending, final-current and two historical questions. Ordered solves five, arrival four: .8333 versus .6667. Selected-context recall matches here because the correct single units fit the inherited 80 encoder-WordPiece proxy. It is not an answer-quality measure or a universal candidate/context equality.

The four empty tasks are deleted current, deleted history, revoked history and wrong tenant. Both have correct-empty fraction 1. Stale scored fraction over all ten is .1 ordered and .2 arrival. A correct empty privacy boundary can coexist with unhealthy internal source state, so inspect the privileged event projection separately.

Three repeats produce 30 CPU samples/projection, not 30 independently judged questions. The search timer includes version/policy selection, exact scoring and the known-revision barrier; encoding/build/publication/packing/serialization/evaluation are separate. Fixed chronological/mode order and tiny repeats limit latency interpretation. Use actual request IDs from your own run, not copied UUIDs.

On **`ch22-controlled-event-delivery-v1`**, source 1000→visible 1200 gives 200 logical milliseconds; delete 2000→2600 gives 600; revoke 3000→3900 gives 900; edit 4000→4500 gives 500. These are controlled scheduled positions, not actual worker or service latency. The known-pending query at 4200 sits 300 after source commit and 300 before publication. No amount of broader candidate search can find a representation that has not been published.

## Publication and persistence

Canonical acceptance can precede failed index publication. A duplicate receipt must not suppress reconciliation when generation state differs from desired store state. The regression leaves the store at revision 2/index at revision 1 after invalid prepared vectors, repairs them, and retries the same event. Receipt status is duplicate-event while publication completes. This illustrates separate checkpoints rather than an invented end-to-end transaction.

The local state snapshot retains heads/history/receipts; a trusted digest guards actual stored bank/query/state payload. Reload exactly reproduces 20 raw/final candidate sequences. Temporary-file write/flush/fsync/replace is a local primitive, not a universal distributed or power-loss durability proof. Backup restore must reconcile tombstones, grants and source positions before serving.

## Migration, compatibility and caches

On **`ch22-compatible-generation-cutover-v1`**, backfill at 3500 misses A08's projection 3900 and A06 revision 3 at 4500. A stale target fails comparison to current source head/history. Tail replay after 3500 catches those changes and ignores stale/duplicate deliveries; the switch succeeds. The old body generation also stayed current, so validated rollback succeeds. A frozen obsolete rollback target would fail.

The old body/new entity-prefix contracts share one cached backbone and 384 coordinates but have different input identities. An old-contract query on the new generation is rejected before vector access. All seven final source/version tasks pass on each compatible generation: three positives/four empty. This is migration protocol parity on exact-ID tasks, not better embeddings or a production throughput benchmark.

The cache hit inherits the actual scoring-origin request ID and retains an observed cached-payload stage with empty raw scores. Changes in generation, tenant or source/policy epoch miss. A forged deleted-source payload under a current key is rejected before returning evidence. A source-authority digest invalidates conservatively; a production system needs bounded invalidation/revalidation and a current authority rather than trusting old cached grants.

## Part V cross-chapter reasoning answers

1. Missing scanned amendment is an ingestion/extraction failure. A correct source hit is not preserved evidence; unchanged canonical text cannot gain missing pixels through reindexing.
2. Whole-parent budget rejection is context selection/representation granularity. Smaller focused units, overlap and parent expansion have distinct costs and must be evaluated on the same independent source spans.
3. Top 3 filtering can miss a rank 7 eligible result. The oracle is exact top min(k,eligible count) within authorization and the task predicate, not the unfiltered top 3.
4. ACL change requires new source/metadata/policy/eligibility identities and publication/cache checks. Coordinates may be reused only when actual input/model/metric identity is unchanged; grants are still republished.
5. Tombstone revision dominates stale upsert. Current permission/deletion blocks serving independently of whether the projection is healthy. Physical purge/tombstone retirement require broader lifecycle reasoning.
6. Source revision 3 is known but not yet projected; raw revision 2 is observed and barred. The positive requirement remains in recall's denominator; it is not a reviewed negative pair or ANN error.
7. Snapshot completion lacks tail coverage. Validate heads/history/rosters/model/grants and actual query gates at a defined source position before cutover; rollback must be current too.
8. Extraction preservation counts required source spans retained by parsing; chunk recall counts independent evidence covered by retrieval; predicate oracle recall counts eligible exact neighbors; version/context recall counts the intended version's evidence. Their workloads/units/denominators differ. Correctness, faithfulness and citations require generation and labels later.

## Architecture from memory and running-project comparison

A correct sketch separates approved original capture, parsing/normalization/quality disposition, canonical source/anchors, chunks/metadata, compatible representations, source revision/tombstone projection, generation publication and query-time current/history/authorization/scoring/packing. It places source-bound judgments and correlated telemetry beside the actual stages. The source change log/watermark, backfill/tail and serving pointer remain visible. Mark queues, live IAM, distributed publication/durability, physical purge, generator and service dashboard as unrun.

V0 provides literal source/context/stub behavior. V5 adds extraction fidelity and segmentation/packing choices; V6 adds governed eligibility and evidence lifecycle. Their conceptual responsibilities grow; incompatible numeric scores do not form a learning curve. Preserve scan/table/encoding losses, oversized-parent/packing loss, predicate-shortlist underfill and source-known/index-pending/replay loss. Each result card names corpus/query/qrel/model/index/eligibility/cutoff and timing boundaries.

## Part V cumulative assessment rubric

| Component | Weight | Evidence required |
|---|---:|---|
| Architecture from memory | 25% | Separate source/index/query/evaluation lanes; actual identities/maps, authorization and all lossy/publication boundaries |
| Cross-chapter reasoning | 30% | Eight mechanism diagnoses; correct set/time/version/cost arithmetic and no source-hit/recall/answer conflation |
| Running-project comparison | 25% | Compatible workload cards, preserved negative results and actual request/version traces; measured/unrun limits |
| Delayed recall/teach-back | 20% | Independent scheduled redraw/prediction, correction log and successful reattempt; no fabricated learner outcome |

Suggested pass 80% with mandatory gates: authorization before scoring/fetch/cache reuse, version/content-bound judgments, no invented generation/native/production/generalization result. Chapter-local rubric: own reducer 25%, edited/deleted source proof 25%, measured timeline/trace diagnosis 20%, migration/cache/recovery defense 20%, own reviewed workload 10%. Reference execution earns no construction credit.
