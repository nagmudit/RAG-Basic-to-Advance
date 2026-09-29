# Chapter 1 lab — Worked solutions

Read the [lab](../labs/chapter-01/LAB.md) and attempt it first. These are **defensible first routes**, not universal architectures. A different route earns credit if its source, authorization, operation and failure analysis are explicit.

## A. The 15 requests

| # | Need, first route and output | Tempting failure and qualification |
|---:|---|---|
| 1 | Transform the supplied words directly; preserve numbers and check them against input. | External retrieval could add unrelated facts or alter numbers. No outside source is needed. |
| 2 | Compute `17 + 25 = 42` deterministically; return 42. | Search may find a page containing both numbers but cannot establish this arithmetic result. |
| 3 | Search only authorized contract versions and return the exact termination clause with document, version and section. | A generated paraphrase may omit a legal qualifier; the user asked for wording. |
| 4 | Retrieve `D1 §3` and effective `D2 §2`, compare targets, and give a cited answer: 4 h → 1 h, down 3 h or 75%. | `D3` alone is stale; a model-only guess cannot establish the private amendment. |
| 5 | Query the ticket database with `customer=C-17` and `status=open`, using the relevant Sev-1 field and an authorized account; return the count and as-of time. | Embedding search over ticket descriptions cannot reliably count all and only open tickets. |
| 6 | Call the authorized live shipment API and return status/time, perhaps with a direct link. | A copied shipping email or old document may be stale. |
| 7 | Fetch the official live notice, verify device identifier, publication/effective time and source, then cite a summary; ask or abstain if no verified notice appears. | The month-old local corpus cannot establish the newest notice. |
| 8 | A direct, concise answer is reasonable: “Hypertext Transfer Protocol.” | Retrieval has overhead here. If the context demands a textbook citation, add one; the request itself does not. |
| 9 | Search the authorized, maintained handbook; cite the current steps and version. | Model training data cannot know this organization’s current process. A stale employee blog may be a poor source. |
| 10 | Do not guess a dose. Ask for the verified order and route to an appropriate clinician or approved clinical workflow. | General medical text is not patient-specific authority. Access to some medical article would still be insufficient. |
| 11 | Use the authenticated billing API/database to find the latest **paid** invoice, then return its total, currency and invoice date/ID. | Document search can confuse “latest,” “paid,” drafts and currency; permissions must be checked. |
| 12 | Summarize the supplied paragraph directly and count words; do not retrieve unrelated material. | External search would change the source set without the user asking for it. |
| 13 | Retrieve all three authorized proposals, identify owner claims with dates, and report agreement or conflict with citations. | Choosing the highest-ranked proposal silently would hide contradiction. If authority is unclear, say so. |
| 14 | Query the service registry for `owner=Team Blue` and `active=true`; return the list with snapshot time. | Old design notes may mention retired services or former owners. Document search may aid explanation but is not the source of truth for the exact list. |
| 15 | Retrieve the original agreement with **historical** effective-time filtering; answer four hours from `D1 §3`. | Applying the 15 May 2026 amendment to a February 2025 question would be a temporal error. |

## B. Hand trace

For case 4, one possible candidate order is `[D3, D1, D2]`. The selected evidence is `[D1 §3, D2 §2]`. The supported claims are: old target = 4 hours from `D1 §3`; new target = 1 hour effective 15 May 2026 from `D2 §2`; change = `4 − 1 = 3` hours and `3 / 4 = 0.75 = 75%` reduction. `D3` is a candidate but stale for the current target.

Without `D2`, the current target and magnitude of change are unsupported. The old four-hour target remains supported. A safe answer states the old value and cannot verify a subsequent change from this snapshot. If `D2` is inaccessible, it must be outside the request’s eligible candidates and supplied context; the response and ordinary logs must not expose its content or reveal protected identifiers. The user can be referred to an authorized channel without confirming a confidential amendment.

`D3 FAQ-7` is a bad citation for “one hour” because the quoted FAQ says **four** hours, so it does not support the claim. It also predates the effective amendment and is a stale summary for the dated contractual question.

## C. Controlled comparison

Question: does adding the effective amendment make the dated change answerable under the explicit evidence rule? Hypothesis: `D1` supports only the old target, while `D1` plus `D2` supports both required facts. Baseline `{D1}` has fact coverage `1/2` and permits only a partial statement plus abstention about the change. Changed corpus `{D1,D2}` has coverage `2/2` and permits the cited comparison. The controlled variables are question, date, user access, selection rule and required facts. A claim of a new target from the baseline suggests untracked information or invention. The result does **not** prove that an automatic retriever will find `D2` or that a generator will use it faithfully.

## D. Executable trace

The script reports candidate IDs separately from evidence locators. A non-existent span fails the locator check; removing the requester’s scope fails the authorization check. Neither check proves that the final sentence expresses the legal meaning of the quoted clause, uses the right effective date, or performs the percentage calculation correctly. Those require separate source interpretation, arithmetic and claim review.
