# Chapter 1 lab — Choose the evidence path

**Purpose.** Decide whether an answer needs external knowledge, which source is authoritative, what operation is needed, and what the assistant should return. This is a design and hand-tracing lab. It does not require a search engine or model account.

**Prerequisite:** [Chapter 1](../../chapters/chapter-01-a-question-a-model-and-missing-evidence.md). **Estimated time:** 60–90 minutes. Attempt all cases before opening the [solutions](../../solutions/chapter-01-solutions.md).

## A. Classify 15 requests

For each request, write five fields:

1. **Information need:** what would actually satisfy the user?
2. **Authoritative source and eligibility:** model/prompt, local document, structured system, live source, or unknown; who may access it?
3. **Operation:** direct transformation, deterministic computation, document retrieval, structured query/API, live retrieval, or combination.
4. **Output:** direct answer, source list, cited synthesis, clarification, or abstention.
5. **Tempting failure:** one plausible path that would be less reliable and why.

Some cases have more than one defensible design. State the assumption that makes your route appropriate. A source you cannot access is not eligible evidence.

| # | User request and constraints |
|---:|---|
| 1 | “Rewrite this supplied paragraph in a warmer tone. Keep every number unchanged.” |
| 2 | “What is 17 + 25?” |
| 3 | “Show me the termination clause in the Helios Pro agreement; I want to read the wording myself.” The requester has contract access. |
| 4 | “As of 20 May 2026, how did the Helios Pro Sev-1 response target change?” The requester has access to the agreement and amendment. |
| 5 | “How many Sev-1 tickets for customer C-17 are open right now?” The ticket database has status and customer fields. |
| 6 | “Where is shipment 92817 right now?” A shipment-status API is available and authorized. |
| 7 | “Summarize the newest public safety notice for device P-8.” The local corpus was last refreshed a month ago; an official live notice site exists. |
| 8 | “In one sentence, what does HTTP stand for?” No special source or audit requirement is stated. |
| 9 | “What are our current new-hire laptop setup steps?” The maintained internal handbook is accessible to this employee. |
| 10 | “What dose should this patient take today?” The assistant has no verified medication order or clinician-approved source for this patient. |
| 11 | “What was the total on my latest paid invoice?” The authenticated billing system has invoice totals and payment status. |
| 12 | “Summarize the paragraph I pasted above in 20 words.” The entire paragraph is present in the current prompt. |
| 13 | “Do the three project proposals agree on who owns the migration?” Three accessible proposals name different owners and dates. |
| 14 | “List all currently active services owned by Team Blue.” A service registry has owner and active-state fields; design notes mention some old owners. |
| 15 | “What was the Helios Pro Sev-1 target on 1 February 2025?” The original agreement and later amendment are both accessible. |

## B. Hand-trace a change and an access boundary

Use the fictional `D1`, `D2`, and `D3` records in Chapter 1.

1. For case 4, list candidates, selected evidence and each answer claim. Compute the absolute and percentage reduction. Cite the old and new targets separately.
2. Repeat with `D2` removed from the corpus snapshot. Say exactly which claim is now unsupported.
3. Repeat with `D2` present in the store but inaccessible to the requester. Explain what must be excluded from candidates, context, answer and ordinary logs. State a safe user-facing response.
4. A model cites `D3 FAQ-7` for “the target is one hour.” Explain two independent problems with that citation.

## C. A tiny controlled comparison

Complete the experiment card below on paper. The required facts are the old and new target. Hold the question, date and selection rule fixed; vary only whether `D2` is available. Report fact coverage as `supported required facts / 2` and identify the permitted outcome. Then state one conclusion the experiment **cannot** support.

```text
Question:
Hypothesis:
Baseline corpus:
Changed corpus:
Controlled variables:
Required facts and source locations:
Result for each corpus:
Error analysis:
Conclusion and limitation:
```

## D. Optional executable trace

Run `python labs/chapter-01/source_trace.py` from the repository root. Read its output and find the exact fields that distinguish candidates from selected evidence. Change one selected span to a non-existent span; observe the error. Then restore it and remove the user’s permitted scope from `D2`; observe the authorization check. The code validates locators and scope only. Explain in two sentences why those checks do not establish that a natural-language answer is correct.

## Review rubric

An excellent submission identifies the source of truth and access scope before choosing search, separates search from generation, dates the evidence, declines unsupported claims, computes the change with units, and names a concrete failure of an alternative route. Do not award full credit for merely labeling a row “RAG” or “no RAG.”
