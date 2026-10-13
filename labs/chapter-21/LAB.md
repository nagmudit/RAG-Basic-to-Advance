# Chapter 21 lab — Keep constraints out of the similarity score

Read [Chapter 21](../../chapters/chapter-21-metadata-schemas-and-filtered-retrieval.md) through Section 21.6 first. Chapter 20's independent chunking, source-bound labels and context budget are binding prerequisites. This lab starts V6; it does not implement Chapter 22's freshness lifecycle.

## A0. Construct the metadata selector

Before inspecting [the reference](../../projects/V6/metadata_ch21.py) or the separate solutions, implement `select` in [implement.py](implement.py). Keep an initial hand prediction and first failing run in your lab notebook. Use only the standard library; do not import the V6 selector or final answer.

**Bounded contract:** metadata-only rows have `id`, `tenant`, role-list `roles`, optional `language` and publication string `published`. The trusted function arguments provide tenant and roles. Authorize with tenant equality AND nonempty role overlap. Missing tenant/roles denies. The task dictionary may contain only `language`, `start` and `end`; unknown/malformed fields raise `ValueError` before selecting anything. Optional language null does not match requested language. Dates must have a timezone; normalize instants and use `[start,end)`. An invalid row date excludes it when a date predicate is active. Return sorted IDs; never fetch a body/vector. This simplified exercise schema is intentionally smaller than V6's governed schema.

1. Draw separate permission and task sets for the checker fixture. Predict the selected IDs for a reader, an admin and an absent tenant.
2. Implement the intersection and date/null rules. Explain how an omitted predicate differs from a null requested value.
3. Run the checker; repair your implementation based on the invariant, not an ID-specific branch.
4. Add your own four-row fixture using a different tenant, a boundary timestamp and a missing role. Show a second aware timezone representation of the same instant and the excluded upper endpoint.

```powershell
python -X utf8 labs/chapter-21/check_implementation.py
```

The supplied starter intentionally raises `NotImplementedError`. Passing the checker alone is insufficient: submit the independent implementation, first attempt, own fixture and reasoning. Only then inspect the reference and [separate answers](../../solutions/chapter-21-solutions.md).

## A1. Inspect the trusted schema and evidence

Read [the descriptors](../../projects/V6/sources_ch21.json) and [source-bound labels](../../projects/V6/qrels_ch21.json). Choose one A-reader source, one B-reader source and the admin-only source. Record each original source/version/hash, chunk range and line locator, metadata digest and policy/schema version. Identify which fields can be suggested by extraction and which must come from policy authority.

Explain why A01 and A02 are distinct query-visible records despite identical bodies. Identify the two pre-read blocked descriptors. Do not treat them as relevance negatives. The fixture is fictional instructor data; an ordinary A request must never log B/admin IDs. No authentication or cryptographic signing service runs.

## A2. Reproduce matched plans

Use the already-prepared environment and cached model. [Requirements](../../projects/V6/requirements-ch21.txt) pin observed versions; the runner does not install/download dependencies. Keep the committed baseline record immutable and write local outputs under `build`.

```powershell
$ch21Runner = "projects/V6/experiment_ch21.py"
$ch21Local = "build/ch21-local-results.json"
$ch21Index = "build/ch21-local-index"
python -X utf8 $ch21Runner --output $ch21Local --artifacts $ch21Index
python -X utf8 -m unittest discover -s projects/V6 -p 'test*.py' -v
```

For `ch21-metadata-predicates-v1`, report all four plans at k2: macro relevance recall over nine positives, eligible-oracle recall, context source recall, Precision@2 over all twelve, correct-empty fraction over three, predicate violations, mean scored work, search p50/p95 and separate view/packing times. Identify timing exclusions. Compute why .963 is the relevance ceiling and why a correct singleton has Precision@2=.5.

Preserve the common envelope, trusted snapshot, actual shortlisted scores, context attempts and null answer/evidence-claim stages. Attach at least two actual request IDs from your run. Do not compare these metrics numerically with Chapter 20's different workload as an improvement sequence.

## A3. Diagnose actual negative results

1. Find `a-day8`/`post3`/trial0. Use raw candidates, shortlist, task-match IDs and final IDs to locate A08's first loss. Report rank, score, `task_count` and reason. Explain why the empty final list does not imply absence.
2. Find `b-day8`/`post3`/trial0. Show why a four-row authorized pool can still lose a task match.
3. Find `a-range`/`prefilter`/trial0. Explain the omitted third relevant source at k2. Separate cutoff completeness from eligible-oracle recall.
4. Find `a-request-b`. Distinguish the semantic baseline's wrong-task A candidates from unauthorized B access. Explain why a task predicate cannot alter the principal.

## A4. Reason about ANN placement and budgets

Reproduce `ch21-authorized-task-bridge-v1` from the checked record. Draw the actual frontier events under task transit and task pruning; explain why this is not HNSW or an ACL-filtering implementation. Add a hand graph with two alternative authorized routes and predict what pruning changes.

Calculate the six-row chapter example at shortlist depths2,3,5. Derive selectivity and the artificial `k/σ` expectation. Construct a ten-row ranking where post9 still fails. A test supplied by the author is a reference check; your counterexample must use your own IDs/scores/task pattern. Explain a bounded fallback and when it changes the task versus only the search effort.

## A5. Submit a design card and delayed defense

Your card includes: trusted identity source; governed field types/owners/null semantics; source/metadata/qrel identity; index/query plan; exact baseline and eligible oracle; quality/work/latency gates and denominators; two failure traces; tenant-safe cache requirements; snapshot mutation/revocation limits; decision and next regression case. Do not build live updates, caches or Chapter 22 mechanisms in this submission.

**Interview defense:** a system has zero unauthorized final responses but private IDs in A's traces. State the failed boundary and required investigation. Another system has zero task violations but low recall: explain why the first fix is not automatically a new embedding model.

**Delayed task:** after 1,3,7 and 21 days, sketch the authorization/task/scoring/shortlist/context stages without the chapter. Explain V0, V5 and V6's conceptual progress without comparing incompatible scores. The cumulative Part V checkpoint remains in Chapter 22.

## Acceptance rubric

| Area | Required evidence |
|---|---|
| Independent construction | First attempt, working bounded selector, own fixture; no reference import or hardcoded fixture IDs |
| Typed correctness | Timezone equivalence, half-open boundary, unknown/null distinction, malformed predicate rejection |
| Access boundary | Tenant AND role intersection before content/vector use; no private IDs in ordinary request traces |
| Identity | Actual content/locator/metadata/policy-bound judgments and independently expected snapshot digest |
| Measurement | Named workload, frozen questions/qrels, all denominators, exact oracle, stage boundaries and negative results |
| Diagnosis | Two actual first-loss traces, plus cutoff ceiling and bridge reasoning |
| Design and retention | Provisional plan, cache/revocation limits, cost/scale defense and delayed teach-back |

The author-performed review verifies supplied artifacts. It cannot certify that you independently constructed the mechanism or performed delayed recall. See [solutions and reasoning rubric](../../solutions/chapter-21-solutions.md) after your attempt.
