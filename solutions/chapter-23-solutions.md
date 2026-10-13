# Chapter 23 solutions — Interpretation before evidence access

Attempt the [lab](../labs/chapter-23/LAB.md) and hand predictions before reading this file or the [separate bounded policy](code/chapter_23_mechanisms.py).

## A0. Policy reasoning

With only lexical/dense available, exact IDs select lexical, paraphrases/dates select dense, relationships select marked partial lexical evidence, and counts stop as unsupported. A count with only dense must not estimate a total from retrieved passages. A relationship with graph available selects graph as ready; the construction fixture does not implement that graph backend.

Ambiguity precedes language and capability checks because selecting a backend cannot resolve what was asked. Non-English is unsupported under the declared English grammar; this is not an evaluation of multilingual embeddings. Missing dense/lexical can use the other mechanism under the same constraints. Missing graph can return evidence-only partial results, while missing SQL stops. Invalid kind/registry/ambiguity types reject; inputs remain unchanged. A fresh fixture and oral defense are still required even if checker outputs pass.

## A1. Original, slot and clock

r01 preserves the actual tab/spacing original and derives surface `A06 waiting period?`. Its exact slot is A06, not a lowercased token treated as a new identifier. r05 means publication in `[2026-10-06T00:00:00Z,2026-10-07T00:00:00Z)`. A06's publication metadata remains October 6 through its revisions, so that interval does not identify the nine-minute historical body.

r07 resolves one prior A06 slot only after matching the trusted principal/session and checking expiration. Slot provenance names the prior turn. The lexical field input carries the locked ID without an LLM paraphrase. Current authorization remains mandatory. r08 explicitly requests source time 1500: A06 revision 2 supplies nine-minute evidence, and current/revision grants still intersect.

r13 has two prior record IDs and must clarify. Choosing one by recency would invent a referent. Invalid dates reject their calendar interpretation. Relative times without an axis/reference policy remain unresolved. Lowercase/full-width ID-like strings require confirmation in this narrow grammar; unsupported control characters raise a redacted invalid request. These are domain policies, not universal Unicode/language restrictions.

r21 asks for an attribute: Green's waiting duration. The coarse `how many` cue calls it a count and selects unavailable SQL. This is a false positive retrieval trigger before any backend search. Similarity tuning cannot repair that branch. The expected semantic/attribute plan and relevant Green span stay frozen; the miss remains in the positive denominator.

## A2. Matched metric arithmetic

Read actual values from [the checked record](../projects/V7/chapter-23-experiment.json). **`ch23-query-plans-v1`** has ten positive questions with eleven source requirements. If a two-source question finds one record, its recall is .5 and it contributes one .5 to the ten-question macro average. Do not divide all successes by eleven and call that the same metric.

Required-empty correctness uses four distinct no-result tasks. Seven guard decisions have their own denominator, including one marked partial relationship fallback. Guard correctness is not generated abstention quality. Full rule-plan accuracy also checks intent, predicate/time, selected route and declared planning outcome on all twenty-one queries. A correct plan can still produce a retrieval miss.

`dense_all` searches authorized current sources, so its wrong neighboring procedure can obey ACLs while failing an exact ID. `constraint_dense` applies the same interpreted predicates/history/guards as `rule_route`; ties between them show that on small selected sets lexical route choice adds no quality gain. Any improvement against all-dense is a policy-bundle result, not an isolated BM25 effect. A narrower candidate set can also hide weak ranking: representative unconstrained paraphrases are still needed.

The publication interval includes A01 and A02. Both are required publication identities despite identical body claims. Both actual units are 34 WordPieces: 68 fits budget 80, so both enter context and candidate/context recall match here. Under a hypothetical budget 60, only one whole unit could fit; do not present that hand prediction as measured quality on the registered workload. Source availability does not certify answer correctness, faithfulness or citation support.

Three randomized warm repeats produce sixty-three parent timing observations per policy, not sixty-three independent judged questions. Search totals mix actual backend attempts with zero-search guard/empty parents. Prepared encoding, eligibility, packing, quality evaluation and diagnostic serialization are separate. Report the declared estimator/population; do not infer service p95 or sum stage percentiles. Earlier V6 metrics have different workloads and denominators.

## A3. Failure and fallback

On **`ch23-bounded-route-fallback-v1`**, an immediate injected dense timeout permits lexical under the same task; an injected exact-ID lexical timeout permits dense under the same record constraint. Each actual attempt has a child request ID. Two injected timeouts stop after two attempts with `retry_budget_exhausted`. An empty A99 task has zero attempts and does not drop its ID.

The graph route is unavailable in the local capability registry. Its lexical fallback is partial evidence, not a failed actual graph call and not graph-path completeness. Count/web requests remain unsupported; local current metadata cannot prove latest public information. Permission/integrity failures are not retryable backend timeouts. Current deletion/revocation blocks historical and remembered reads before body/vector scoring.

## A4. Repair design and limits

A possible repair distinguishes a numeric attribute with an explicit unit (`minutes`) from counting records. A pattern alone is not enough: “How many records mention minutes?” remains a corpus count, and “What is the average waiting time?” is aggregation despite a duration unit. A schema-aware classifier should determine the operation and scope; ambiguous input may need clarification. Keep the original query and record which feature changed the decision.

Assess new examples under a reviewed new workload if reporting quality. Splitting variants of the same authored question does not establish unseen-domain transfer. A proposed rule passing two examples is mechanism evidence, not production calibration. Preserve the original reference's negative result and label identity.

## Hand score, misconceptions and rubric

With three equal-length records, a once-occurring term in one record has IDF `ln(1+2.5/1.5)=ln(8/3)=.980829`. For TF1 and average length, BM25 saturation is one at `k1=1.2,b=.75`. Exact field selection changes the scored set; current permission decides whether the term/body can be accessed at all. Neither the contribution nor a normalized dot score is route or answer confidence.

Suggested pass is 80%, with mandatory gates for original-query retention, current authority before scoring/fetch, no hard-constraint relaxation and no fabricated SQL/graph/web/generator result. Allocate independent router/fresh fixture 25%, interpretation/time/reference hand work 20%, source-bound paired metrics and failures 25%, actual traces/fallback/packing diagnosis 20%, and repair/design defense 10%. Keep first-attempt and delayed-teach-back evidence. The author review certifies supplied artifacts, not learner independence or delayed mastery. Chapter 24 remains unstarted.
