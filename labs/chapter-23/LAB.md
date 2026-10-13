# Chapter 23 lab — Preserve intent through a bounded query plan

Read [Chapter 23](../../chapters/chapter-23-normalize-classify-route-and-contextualize-queries.md) through Section 23.5 first. V6's source/version/current-grant and eighty-encoder-WordPiece packing contracts remain binding. This lab begins V7. Do not start Chapter 24.

## A0. Construct the five-kind policy

Before opening the [reference](../../projects/V7/query_ch23.py) or [separate answer](../../solutions/code/chapter_23_mechanisms.py), implement [implement.py](implement.py). Retain a handwritten decision table, your first failing run and corrections.

`route(kind, available, ambiguous=False, language='en')` returns exactly `primary`, `selected`, `outcome`, `fallback`, `reason`:

- `identifier → lexical`; `paraphrase → dense`; `date → dense`; `relationship → graph`; `count → sql`.
- `available` is a `frozenset` of known route names: lexical, dense, SQL, graph and web, written in lowercase. Reject unknown kinds, unknown capabilities, a non-frozenset registry or non-Boolean ambiguity with `ValueError`.
- Ambiguity takes priority: select nothing, outcome `clarify`, reason `ambiguous_intent`, fallback false.
- A non-English declared language next selects nothing, outcome `unsupported`, reason `unsupported_language`.
- An available primary selects itself, outcome `ready`, fallback false, reason null.
- Missing dense may fall back to lexical; missing lexical may fall back to dense. These keep outcome `ready`, reason `capability_fallback` and fallback true. The executor must retain constraints.
- Missing graph may select lexical only as outcome `partial`, reason `evidence_only`, fallback true.
- No compatible alternative selects nothing, outcome `unsupported`, reason `route_unavailable`, fallback false. Missing SQL must not turn into counting passages.

Do not mutate inputs or import the reference/answer. Predict what happens with `count` and only dense available, and with `relationship` and only graph available. Explain why availability does not grant authorization.

```powershell
python -X utf8 labs/chapter-23/check_implementation.py
```

The starter intentionally fails until you implement it. The checker is public assessment, not secret proof of independence. Create a fresh three-request fixture of your own, including a partial relationship fallback and an ambiguous date. Write the expected outputs before running. Add one own invalid-input case and explain why it rejects.

## A1. Trace actual interpretation

Now inspect the [larger interpreter](../../projects/V7/query_ch23.py). Use five requests of your own, one each for exact ID, paraphrase, publication date, relationship and count. Record original text, normalized surface, cue, typed predicate, requested time axis, primary/selected route and terminal reason. These mechanism probes make no new quality claim.

For the frozen workload, hand-predict r01, r05, r07, r08, r13 and r21 before opening the checked results:

1. Preserve the tab/spacing original for r01 while identifying the exact A06 field.
2. Derive r05's UTC half-open publication interval. Explain why it does not select a historical body.
3. Validate r07's prior-turn capsule: session, principal, expiration, one referent and source of the slot.
4. Select r08's source-effective version and still apply current permissions.
5. Explain why r13 cannot choose one of its two prior record IDs.
6. Determine whether r21 asks for an attribute or an aggregation. Record the reference rule's error honestly.

Also try a lowercase ID, a full-width ID, a control character, an invalid calendar date, an expired capsule and a capsule copied across principals. Do not describe an ID digest as authentication. Keep these strings in an appropriate local evaluation plane, not ordinary shared logs.

## A2. Reproduce the matched evidence experiment

Use the existing cached/pinned stack from [V6](../../projects/V6/README.md). No new dependency or model download is needed. Leave committed historical records unchanged and write your run under `build`:

```powershell
$ch23Runner = "projects/V7/experiment_ch23.py"
$ch23Output = "build/ch23-local-results.json"
$ch23Index = "build/ch23-local-index"
python -X utf8 $ch23Runner --output $ch23Output --artifacts $ch23Index
python -X utf8 -m unittest discover -s projects/V7 -p 'test*.py' -v
```

On **`ch23-query-plans-v1`**, report ten-question positive Recall@2, eleven source requirements, context evidence recall, four-task required-empty correctness and seven-task guard decision accuracy. Use per-question macro averages: the two-publication question contributes one fraction, not two independent queries. Report twenty-one-query full rule-plan accuracy and distinguish it from passage retrieval.

Compare `dense_all`, `constraint_dense` and `rule_route`. The all-dense comparison changes interpretation and dispatch together. Use the latter two to discuss route choice under shared interpreted plans. Preserve ties and worse results; do not claim the lexical route caused gains produced by metadata/reference constraints.

Report the workload ID, source/query/qrel/model/index identities, three warm repeats, shuffle seed, per-slice failures, query-processing p50/p95, route-search p50/p95 and separate eligibility/packing timings. State that zero-search guard/empty requests are in the parent timing population; these are not backend-only or service percentiles.

Attach one root/child trace for an exact ID and one for a date/follow-up case. Show actual task IDs, raw scored pool, shortlist, final candidates, packing attempts and actual source version in context. Do not reconstruct intermediate scores from final winners. Show why both 34-WordPiece publication units fit budget 80. Hand-predict the loss under a hypothetical budget 60 without reporting it as a result of the registered run.

## A3. Diagnose fallback and authority

On **`ch23-bounded-route-fallback-v1`**, trace the four controlled cases:

- a dense timeout followed by one lexical attempt;
- a lexical timeout followed by one dense attempt with the same exact ID;
- two failed attempts followed by a budget stop;
- an unknown exact ID with no backend attempt and no broadening.

For each, attach the parent request and actual child IDs/status/reasons. Compare the fixed constraint digest. Immediate exception injection is not a real deadline measurement. A failed backend is not a no-answer judgment. A deleted/revoked/other-tenant exact task must remain empty before vector/body scoring even if a remembered ID or another route is available.

Check the relationship guard's `partial` result: lexical passages may be returned, but no graph traversal or relationship answer ran. Check the count/web guards: no SQL/API/live source was executed. Explain what would have to be added before those routes could claim complete results.

## A4. Propose and assess a repair

Design a better distinction between “How many records?” and “How many minutes?” Add at least one counterexample to your own bounded policy fixture, including an ambiguous phrase. Write the expected interpretation independently before running. Do not patch the frozen reference or update its labels to make the existing miss disappear.

If you turn the repair into a measured retrieval benchmark, create a reviewed new workload/query/judgment identity and register its purpose, slices and valid/invalid comparisons first. Bind actual source/version/content/locator/current grants and the original query/context. A local mechanism probe is not a held-out generalization experiment. An automatically refreshed digest is not a new judgment review.

## Acceptance and recall

Submit your own implementation and first attempt; hand calculations; fresh policy fixture; reproduced version-bound metrics; actual parent/child/packing traces; timeout/empty/partial defense; and a proposed quantity-trigger repair with a counterexample. Use [separate solutions and rubric](../../solutions/chapter-23-solutions.md) afterward.

On days 1/3/7/21, draw original → slots → capability → authorization/version → route attempts → actual context from memory. Teach why slot, permission, similarity, relevance, evidence and answer remain different. Reference execution alone earns no construction credit. Passing this lab begins V7; Chapters 24–25 remain unstarted.
