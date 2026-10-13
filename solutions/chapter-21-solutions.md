# Chapter 21 — Worked solutions and reasoning rubric

Attempt [lab A0](../labs/chapter-21/LAB.md#a0-construct-the-metadata-selector) before reading this file or [the code answer](code/chapter_21_mechanisms.py). These are reasoned references, not a substitute for independent learner construction.

## 1. Metadata-only selection

The checker authorizes north/analyst rows r1,r2,r6. r3 has the wrong tenant, r4 the wrong role, r5 no grant. The requested English interval includes r1. r2 is exactly the excluded upper endpoint; r6 has unknown language and fails requested equality. North/admin selects r4. An absent tenant selects none. With no task predicates, r1,r2,r6 remain; a missing language tag is not a missing permission grant.

Normalize `2026-02-03T05:30:00+05:30` to `2026-02-03T00:00:00Z`. Reject a naive date because no instant can be inferred without a clock policy. Validate the whole task dictionary before iterating rows, so a malformed query cannot return an arbitrary partial prefix. Unknown fields raise; a requested tenant is not an allowed field in this smaller exercise. V6's larger task grammar permits tenant equality only as an intersection with the fixed trusted principal.

The separate code uses explicit conditional membership and aware datetime comparisons, imports neither the running engine nor the learner module, and never touches content/vector fields. Its date parser and rules are bounded. Production query builders need their own engine-specific null, array, Boolean and date grammar checks.

## 2. Identity and schema

V6's accepted sources are A01–A10, B01–B04 and A-admin. A-unknown fails the explicit ACL schema; A-unlicensed fails approved indexing use. Both stop before source path/read. The indexer's privileges do not imply a reader grant. The query principal A/reader gets ten rows; B/reader gets four; A-admin remains unscored in both reader experiments.

A01/A02 have the same text and potentially shared coordinates but different dates, IDs and original origins. A date question treats them differently. Preserve query-visible records and policy even if physical content storage is deduplicated. Chunk IDs remain tied to actual canonical content/ranges; metadata digests bind the governed sidecar and its schema/policy versions. Source bytes/locators and approved scope/use/retention remain in the qrel manifest. Recomputing a hash after a change does not constitute judgment review.

Metadata is curated here, not cryptographically signed. Policy authority must own tenant/ACL. An extraction-confidence number can motivate a quality review but cannot grant access or measure faithfulness. Owner identity also does not create a permission grant.

## 3. Hand ranking and mathematical denominators

For the six-row example, E is `{r3,r5}`, σ=2/6 and exact k2 is `[r3,r5]`. Depth2 postfilter returns none and oracle recall0. Depth3 returns r3 and recall1/2. Depth5 returns both and recall1. The expectation heuristic `L≈k/σ=6` assumes rank-independent match probability; it is not an ANN recall guarantee. Under that artificial model no-survivor probability at depth 3 is `(2/3)^3≈.2963`. That probability is unrelated to the experiment's coincidentally equal .2963 semantic macro recall.

A known eligible singleton at k2 is complete: oracle recall1 and judged recall1 for its one positive. Fixed-cutoff Precision@2 is 1/2. Underfill means fewer than `min(k,|E|)` candidates, not fewer than k under every predicate. A wrong-date semantic result can be authorized yet nonrelevant.

For the nine positive experiment questions, eight have one positive and one has three. Even perfect k2 retrieval gets macro recall `(8+2/3)/9=.962963`. The oracle denominator is its exact top2 set for the three-positive query and one for the others, so oracle recall can be1 while judged recall is below 1. Positive memberships total11, not nine or108; 108 is the complete binary authorized query–unit pair count: ten A queries×ten authorized rows plus two B queries×four rows.

## 4. Checked experiment and context

On **`ch21-metadata-predicates-v1`**, semantic/prefilter/post3/post9 relevance recall is .2963/.9630/.5185/.9630; eligible-oracle recall .3333/1/.5556/1. Context source recall is the same in this fixture. That equality is an observed result, not a general guarantee: the inherited selector can reject units under its whole-unit80 encoder-WordPiece proxy. Actual packing attempts remain available, including rejected wrong-task context units in the semantic route. No answer correctness, faithfulness, citation support or generated abstention is measured.

Precision@2 averaged over all twelve is .1667/.4167/.2500/.4167. The semantic baseline returns candidates on all three empty tasks and produces 20 task violations per pass. The filtered plans produce zero task violations and empty lists on3/3 empty tasks. Post3 also produces empty lists on positive tasks, so empty behavior alone is an inadequate quality measure. No running plan scores an unauthorized vector.

Prefilter scores11/12 units on average, while the other plans average9. View construction, task selection/scoring/sort and context packing have explicit separate boundaries; search percentiles do not include model load/query encode/serialization/evaluation. Three warm repetitions over small repeated templates do not give36 independent quality questions or service p95 confidence.

Post9 happens to recover the oracle. For a counterexample, place the only task match at exact authorized rank 10. Top9 excludes it even with perfect scoring; choose your own IDs/scores to demonstrate this in the lab. A full exact authorized enumeration with the same tie rule contains every task match; an ANN budget of the same numeric size need not be enumeration.

## 5. First-loss diagnoses

`a-day8` requires A08. Actual raw cosine rank 7 is .60323 rounded; top3 contains A07,A05,A06, none matching the day. The first loss is shortlist truncation. The trace has task_count1, empty task survivors/final/context and reason `shortlist_underfill`. Prefilter returns A08. A retrieval score close to another date's score is not confidence in date equality.

`b-day8` requires B03 but it is below B's top3. A small pool can still lose a rare match. `a-range` returns A07,A05 under prefilter and omits A06 at k2; it matches the top2 oracle while task evidence completeness remains2/3. Increasing shortlist depth cannot overcome the final k2 ceiling without changing k.

`a-request-b` has principal A and requested tenant B. E is empty. Filtered plans correctly return none; the semantic baseline returns authorized A units that fail the task. It neither switches the principal nor retrieves B. This is a wrong-task baseline result, distinct from a privacy breach.

Look up request IDs in your current record; UUIDs are correlated run identities, not stable fixture labels. Do not copy a different run's UUID and pretend it identifies your sample.

## 6. Connectivity and physical plans

On **`ch21-authorized-task-bridge-v1`**, task-transit expands u,x,y,v and accepts v at preassigned score .9. Task-pruned expands u then discards x, ending with no result. x/y are task-ineligible and authorized. This is exhaustive traversal of one chain with fixed scores, not HNSW or ANN latency. Private transit is not authorized by this demonstration.

A correct production design might select a small authorized exact subset, use a tenant/policy partition, or combine task acceptance with authorized transit and bounded iterative expansion. Each needs an eligible exact oracle, measured negative cases and a stated visibility boundary. A filter syntax name does not determine physical placement or establish before-scoring ACL safety.

## 7. Design defense and security diagnosis

A defensible card states field ownership/types/null semantics, clock meanings, trusted identity source, policy/schema/index/content bindings and revalidation boundaries. It compares physical plans at the same task/cutoff/score/eligibility, names workload denominators and shows work/latency/cost limits. It preserves negative traces and rejects universal conclusions from singleton/template success.

For caching, bind trusted authorization context/policy, corpus/index/model and task/query identity. Near semantic matches can differ in exact date/tenant/ID; validate those constraints before reuse. Policy revocation needs invalidation or revalidation against a current authority. A local metadata-mutation check is not a distributed revocation protocol. Updates, deletes and searchable visibility are Chapter 22 work.

Private IDs in ordinary A traces are already a boundary failure. Investigate eligibility before scoring, shared caches, ID mappings, tracing permissions and the forward fetch path; protect audit evidence and add a regression that detects first access, not only final output. Do not call it safe because an answer omitted the private text.

## 8. Retention rubric

Without notes, the learner should draw authorized universe, task membership, score pool, lossy shortlist, survivors, final k and context; place the four plans accurately; compute half-open and cutoff examples; and defend V0→V5→V6's conceptual progression. Strong reasoning states why workload scores are incompatible, why accurate metadata predicates do not establish semantic relevance in arbitrary corpora, and what a future lifecycle/authentication service must prove. The author review cannot certify independent construction or delayed recall.
