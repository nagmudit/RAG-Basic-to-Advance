# Chapter 22 lab — Publish the intended evidence version

Read [Chapter 22](../../chapters/chapter-22-freshness-versions-and-incremental-indexes.md) through Section 22.4. Chapters 19–21's source, chunk, permission and evaluation contracts are binding. This lab completes V6 and Part V; do not begin Chapter 23.

## A0. Construct the revision reducer

Before opening [the reference](../../projects/V6/lifecycle_ch22.py) or [separate answers](../../solutions/chapter-22-solutions.md), implement [implement.py](implement.py). Keep your initial hand states and first failing run. Do not import the reference/solution.

The small head/event schema has positive integer `revision` (booleans invalid), nonempty string `digest` and explicit Boolean `tombstone`. Return `(copied_head,status)`: older is unchanged/stale; equal identical is unchanged/duplicate; equal conflicting raises; newer is accepted. Never mutate inputs or erase the revision when deleting. This schema is smaller than the full event/source system.

```powershell
python -X utf8 labs/chapter-22/check_implementation.py
```

The starter intentionally fails. Add an independent six-event fixture using your own source/digests, a duplicate, delete, late upsert and explicit newer recreation. Predict each head before running it. Explain why a new event ID does not make an old source revision current. Only then inspect the reference.

## A1. Edit and delete actual source evidence

Inspect Chapter 21's unchanged [A06 source](../../projects/V6/fixtures_ch21/A06.md), then [revision 2](../../projects/V6/fixtures_ch22/A06-v2.md) and [revision 3](../../projects/V6/fixtures_ch22/A06-v3.md). Record actual raw/record/body/metadata digests, source version, chunk ID and line anchor. Explain the 90→9→12 minute edit and why versioned copies preserve the historical baseline.

Reproduce the actual event lifecycle using the separately prepared [pinned stack](../../projects/V6/requirements-ch21.txt) and cached model. Write outputs under `build`; keep the committed record immutable.

```powershell
$ch22Runner = "projects/V6/experiment_ch22.py"
$ch22Output = "build/ch22-local-results.json"
$ch22Index = "build/ch22-local-index"
python -X utf8 $ch22Runner --output $ch22Output --artifacts $ch22Index
python -X utf8 -m unittest discover -s projects/V6 -p 'test*.py' -v
```

Prove with actual candidate/context IDs and current source-span bindings:

1. `updated-current` at 1500 retrieves A06 revision 2's9-minute source, not revision 1.
2. `known-pending` at 4200 scores revision 2 but drops it before context because revision 3 is known and not yet projected. Preserve this miss.
3. `final-current` at 5300 retrieves revision 3's 12-minute source under ordered processing; no old A06 unit appears in its final/context output.
4. A03's revision 2 deletion prevents retrieval through both `deleted-current` and `deleted-history`, even though the arrival-control projection has resurrected its old internal head.
5. `revoked-history` returns no A08 evidence after its admin-only revision; historical access is not an old grant.

Attach two actual request IDs, their version/authority identity and first-loss stages. Physical raw/history files remain in this fictional audit artifact; this is serving deletion, not a physical-erasure proof.

## A2. Perform your own bounded edit safely

Copy the three Chapter 22 update files/descriptors into `build/ch22-own-updates`; edit the revision 2 source to a different waiting period. Run with `--updates` pointing there and the old labels. It must reject changed evidence identity. Keep that failure as evidence of the qrel boundary.

Then create a reviewed local workload: independently inspect the changed source requirement, update its text/span/hash/anchor, capsule manifest, descriptor hash and schedule digest, and assign new corpus/qrel/workload identities. Copy the registry locally and register all three related workload IDs with their new manifest and valid/invalid comparison rules. The supplied [manifest/loader helpers](../../projects/V6/experiment_ch22.py) may display actual canonical identities; do not use an automatic hash refresh as a substitute for review. Questions may retain a query-set identity only if their definitions are unchanged.

```powershell
$ch22OwnSources = "build/ch22-own-updates"
$ch22OwnLabels = "build/ch22-own-labels.json"
$ch22OwnRegistry = "build/ch22-own-registry.json"
python -X utf8 $ch22Runner `
  --updates $ch22OwnSources --labels $ch22OwnLabels `
  --registry $ch22OwnRegistry --output "build/ch22-own-results.json" `
  --artifacts "build/ch22-own-index"
```

After reassessment, show your new text is retrieved at its matching current/as-of checkpoints and the delete still blocks all A03 serving versions. Report your workload IDs; do not claim a gain over the book fixture's different evidence. The canonical source files/judgments outside `build` remain unchanged.

## A3. Compare ordering and diagnose partial publication

On **`ch22-versioned-evidence-v1`**, report positive Recall@1/context recall over six questions, correct-empty fraction over four, stale scored fraction over ten, search p50/p95 over thirty requests/mode and separate packing time. Explain fixed mode order, tiny repeat count and why logical event lag is not CPU or service latency.

On **`ch22-controlled-event-delivery-v1`**, draw seven deliveries and each before/incoming/after revision. Identify duplicate-event and stale-revision cases. Compute 200/600/900/500 controlled lag and state which reader/publication boundary it represents. Explain the test where a receipt commits, index publication fails, and a duplicate retry reconciles the pending index.

Write a fresh same-revision conflict and a backdated effective-time case. Explain why this bounded temporal policy rejects them rather than silently choosing a source truth.

## A4. Migrate, reject and roll back

Inspect **`ch22-compatible-generation-cutover-v1`**. Show backfill's 3500 source state, missing tail changes, rejected cutover, successful caught-up flip and valid rollback. Use actual contract identities and query outputs. Explain why 384 dimensions does not authorize old-contract query vectors on the new index. Both contracts use the same frozen backbone; do not call this a new trained-model comparison.

Inspect cache population/hit origin, generation/tenant/source-policy misses and their actual request envelopes. Explain why a cache hit has no freshly scored raw pool. Propose one delete/revocation cache regression and the restricted fields an ordinary reader must never see.

## A5. Complete the Part V cumulative checkpoint

Attempt Chapter 22 Section 22.12 without notes: architecture from memory, eight cross-chapter reasoning tasks, V0/V5/V6 comparison and delayed recall/teach-back on days 1/3/7/21. Submit the initial sketch, corrections, actual trace references, compatible workload cards and successful reattempt evidence. Use [the separate cumulative rubric](../../solutions/chapter-22-solutions.md#part-v-cumulative-assessment-rubric) only after your first attempt.

## Acceptance

| Area | Required evidence |
|---|---|
| Independent mechanism | First attempt, own reducer/fixture; duplicates/conflicts/tombstone/order correct |
| Source/version proof | Actual edited source bytes/locators and current/as-of outputs; old current/deleted evidence excluded |
| Evaluation | Registered identities, correct denominators, actual pending/replay failures and timing boundaries |
| Publication/recovery | Desired versus searchable state, duplicate retry after partial failure and persisted replay |
| Migration/cache | Tail gate, contract mismatch, compatible rollback and per-context cache validation |
| Part V mastery | Independent architecture/reasoning/project cards and delayed teach-back; no authorization or fabricated-generation claim |

Reference execution alone receives no independent-construction credit. The author review certifies supplied artifacts, not a learner's delayed performance.
