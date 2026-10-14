# Chapter 24 — Separate solutions and reasoning

Attempt the [lab](../labs/chapter-24/LAB.md), especially A0, before reading this file. The reference is a comparison aid, not a substitute for learner construction.

## A0 — Admission and readiness

The [bounded construction answer](chapter-24/reference_construction.py) implements the starter's exact contract. The original spends the first two words in the checker's fixture. The first certificate proposal is accepted; its whitespace variant is a duplicate. A18 changes a protected atom, the wrong anchor rejects before any budget decision, a second distinct valid representation is accepted, and the final proposal exceeds the branch limit. With a four-word total allowance, the first three-word proposal fails because the two-word original already consumed part of the budget.

```powershell
python -X utf8 labs/chapter-24/check_construction.py solutions/chapter-24/reference_construction.py
```

This verifies the supplied answer only. Credit requires the learner's pre-reference attempt and additional fixture. An implementation that independently extracts richer domain atoms can be useful, but its extraction needs a separate contract; it must not accidentally change the toy checker's stated input semantics.

The scheduler first validates dependency membership and cycles over the entire graph. Repeated ready layers validate an ordering. Only then does it use the caller's completed set to return pending tasks whose prerequisites are satisfied. A disconnected cycle is an error rather than a reason to execute unrelated work and ignore the invalid plan. The project [reference](../projects/V7/reformulate_ch24.py) additionally propagates failed prerequisites through descendants.

Atom checks are not semantic proofs. “Orion certificate renewal” and “Orion invoice payment” use the same recognized entity and no conflicting digits. Both can pass a narrow guard while seeking different evidence. Likewise, adding or removing negation can reverse a need without introducing a new protected atom. Stronger inference or clarification may be needed; it must itself be evaluated rather than assumed reliable.

## A1 — Arithmetic and loss boundaries

The feedback sum is (1, .5). Its norm is √1.25 ≈ 1.1180, so the normalized result is approximately (.8944, .4472). Wrong-topic feedback moves the vector toward the wrong topic using the same update. A zero update has no cosine direction; the reference raises. A production policy could instead record an explicit original fallback.

The full interleaved admission is `x from original`, `y from rewrite`, `z from original`; the second occurrence of x is skipped. Cap two retains x and y. If z is the sole requirement, original recall is 1, union recall is 1, and capped recall is 0. The retained x score is .70 because its first occurrence owns it. Sorting by the displayed .95/.70/.60 values would be a different cross-list ranking policy, unsupported by this interleaver's contract.

Initially retry and trust are ready. After completing retry, only trust is ready. After completing both, combine is ready. With budget two, combine remains unexecuted. If retry fails, combine is blocked; trust can still complete. Partial success is a statement about fulfilled requirements, not permission to invent the missing conclusion.

## A2 — Predictions

- **q01:** the HTTP 429 proposal conflicts with original 503 and rejects, even though it is also surplus. The declared rejection precedence matters. Both admitted paraphrases happen to retrieve the same source shortlist as the original.
- **q06:** the waiting-period hypothetical passage passes the limited atom checks. It omits the authority relationship central to the need and loses A16.
- **q07:** same-entity billing language passes the guard. It steers the hypothetical search away from A17. An admitted proposal can be safe with respect to fields and still be irrelevant.
- **q09:** both the A12 multi-query proposal and the 429 hypothetical passage reject. Hypothetical mode falls back to the original A11 query. Its hard ID remains fixed before scoring.
- **q10:** the publication interval is retained outside the text. Date-free variants still score only A01 and A02 under the original half-open interval.
- **q16:** the inherited count rule classifies the answerable duration need as unsupported. No query encode/search/context stage runs for this question. Its A09 source requirement remains judged and missed.

These are the checked fixture outcomes; they are not universal properties of query reformulation.

## A3 — The paired result

For **`ch24-frozen-reformulations-v1`**, original/multi/hypothetical required union, Recall@2 and context recall are respectively .9091/.9091/.7273. Each value is macro recall over eleven positive questions, not over source–query pairs or 33 independent samples. The one two-source question finds both publications; the duration question finds none. Hypothetical mode also loses q06 and q07.

Mean branches over all sixteen tasks are .6250/1.8125/.6250, scored pairs 6.4375/19.25/6.4375, charged encoder WordPieces 7.3125/18.8750/11.6250. Multi-query expends about 2.99 times the scoring work while tying measured required recall. All methods correctly retain empty evidence for three required-empty tasks and satisfy two labeled guard decisions; intended outcome accuracy over all sixteen is 15/16.

There are 144 parent requests and 147 actual branch requests, producing 291 retrieval envelopes. Thirty-eight one-time prepared-input encodes and one privileged document-build envelope are separate. The four scheduler-control envelopes belong to **`ch24-decomposition-budget-v1`**, which has no qrels or retrieval metrics. Forty-eight query/method outcomes replay through all retained candidate stages, origin scores, provenance and ordered context under the expected snapshot digest.

Local search percentiles exclude proposal generation, request-time encoding, packing and serving overhead. Prepared-input WordPieces are charged as a resource proxy for the branches actually executed; they are not a claim that every repeat encoded those strings again. Null generator cost means unrun, not a free generator call.

## A4 — Follow the actual failure

In hypothetical q06, the branch shortlist is A06/A01, while the required authority source is A16. Inspect its raw scored pool to distinguish “scored below branch cutoff” from “excluded before scoring.” The original entity filter permits A16; the representation changes its rank. The loss has already happened at the branch shortlist, before interleaving or context. Source authenticity cannot repair relevance.

In hypothetical q07, the wrong billing passage returns A14/A05, missing required A17. In multi mode, original and the first rewrite lead with A17, while the second rewrite leads with A14. Interleaving deduplicates the repeated A17, then admits A14. The final A17/A14 set retains the requirement but changes the second context source.

In original q07, A17 uses forty encoder WordPieces; the other candidate A12 does not fit the remaining forty under whole-unit packing. The source requirement is A17, so required context recall remains one. This is an observed packing loss without observed loss of required recall. Do not erase the rejected A12 from the trace or infer that every omitted candidate is irrelevant.

The q10 publication units each use thirty-four encoder WordPieces. Their total sixty-eight fits eighty. All methods retain both. Source identity matters even when similarly worded publications resemble duplicates: the labels require both distinct publications.

For q11, A-reader cannot access admin-only A19; q12's B-reader cannot access A11; q15's A03 is deleted under current authority. Their successful empty tasks have no branch and an actually empty context list. Guarded q13/q14 and misclassified q16 have unrun context represented as null. Rewriting never widens any of these eligibility boundaries.

## A5 — A defensible decision

Keep the original representation as the default for this workload. Multi-query provides no measured required-recall benefit for nearly three times the scoring work. It may still help on another reviewed query distribution, but this experiment supplies no evidence for that transfer. The richer trace and admission mechanism can remain useful engineering infrastructure without promoting every proposed retrieval policy.

All ten retrieval-executed positives already have full original recall, while the fixed interpreter prevents the eleventh from searching. The available ceiling is therefore 10/11. This experiment cannot test recovery of a correctly interpreted baseline retrieval miss; it has none. A new, independently frozen workload needs such cases before making that claim. Deliberately faulty hypothetical drafts demonstrate possible failures rather than measure a live generator's error rate.

The hypothetical comparison establishes that a changed document-like representation can steer actual source retrieval and can fail through topic drift. It does not measure an instruction model's generation quality, stochastic variance, latency or zero-shot performance. A live comparison needs frozen original questions/qrels, reviewed data transfer, prompt/model/version/sampling identities, actual generated passages retained appropriately, actual resource accounting and paired relevance evaluation. It must preserve negative samples rather than select only successful drafts.

For the duration false trigger, first localize the interpretation error. Adding paraphrases after a terminal route decision cannot fix an unexecuted stage. If the grammar is changed, version that policy and rerun a compatible paired comparison without replacing the historical Chapter 23 result.

For a new experiment, register corpus, query, qrel and representation-policy identities, source/content/locator/policy bindings, slices, purpose, valid comparisons and invalid cross-workload conclusions. Freeze tuning and evaluation roles honestly. An author who sees every source and adjusts every draft has not produced an unseen-domain or held-out result.

## Recall and design answers

PRF assumes relevance; true feedback obtains judgments. Union monotonicity says nothing about capped ranking. Original hard fields can survive text omission because the executor carries them separately. A first-occurrence score explains one branch measurement, not a calibrated probability or fused ranking. Dependencies require observed prerequisite outputs; independent searches merely share the original task. Qrels cannot be runtime stop signals. Unknown generator cost remains null. No generated correctness, faithfulness, citation support or abstention outcome can be inferred from source retrieval alone.

A credible incident-service design uses original task constraints, tenant-scoped current authority, shared step/token/deadline limits, declared partial-result semantics, branch provenance and source-version evidence. It begins with the smallest measured policy. Names of orchestrators or frameworks do not supply those guarantees. Chapter 25 remains unstarted.
