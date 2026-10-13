# Evidence identity for judgments

Judgments describe evidence under a particular information need and eligibility policy. A snapshot name and stable document ID are insufficient when their contents can change.

`projects/common/qrel_identity.py` binds every reviewed eligible segment, including grade-zero items, to its document ID/version, source locator and word range, sorted scope membership, normalized title/body digest, and whole-source digest. Signed/draft status and effective date are also bound because they can change relevance without changing text. The eligible corpus manifest contains these item identities, the snapshot, retrieval unit and scope, with a canonical JSON SHA-256 digest.

The `evidence-identity-v1` normalization policy collapses Unicode whitespace runs to one ordinary space and trims the ends. LF/CRLF, tabs, and incidental spaces therefore do not invalidate judgments. Case, punctuation, spelling, numbers and Unicode code points remain significant; no lowercasing, stemming or compatibility folding is performed. Changing source text, source title, version, authority/date metadata, locator/order, word range or permission membership requires judgment review. Sorting permission lists avoids treating their order as a permission change. Whole-source changes invalidate that source's judgments even if a particular short window stays identical. Eligible-roster changes also fail validation. Restricted content is represented by no eligible item and is not copied into the qrel manifest.

Chapter 09 and V3 Chapter 11/12/13 loaders call the same validation. The four existing judgment versions and all grades/questions are preserved; `binding_revision` records the additive identity contract. The immutable pre-remediation experiment records retain their historical qrel/code hashes in `projects/common/HISTORICAL_RESULTS.json`; new replay files record current hashes. A changed hash from added metadata is not a new relevance result.

To reproduce the integrity probes:

```powershell
python -X utf8 -m unittest discover -s projects/common -p 'test_qrel_identity.py' -v
```

The same-ID/snapshot `four hours` to `nine hours` change is rejected by all four loaders, while unchanged evidence and whitespace-only formatting changes still load. Updating a digest automatically to silence a failure is not a review: inspect the changed source and reassess affected judgments first.

## Chapter 19 extraction requirements

[V5 source-span requirements](../projects/V5/span_requirements.json) use a separate declared binding: exact raw file bytes plus source ID/version/path, sorted scopes, approved indexing use and license/retention policy for seven eligible licensed inputs. Canonical spans retain parser/normalization version, content/record digest and source locator. This byte-strict extraction policy does not replace `evidence-identity-v1` for historical qrels. The eight requirements are a preservation/traceability test, not complete graded block qrels. A scanned-page requirement remains in the denominator despite quarantine; automatic digest refresh is not source re-review.

## Chapter 20 independent source-span qrels

[evidence_spans_ch20.json](../projects/V5/evidence_spans_ch20.json) binds five canonical source/version/raw/body/record/policy identities and exact required text/ranges/original anchors. Ten positive questions have eighteen required atoms; two have no eligible published evidence. Query-specific spans are independent of chunk IDs/configurations, enabling matched candidate/context atom coverage. Required nonwhitespace positions must be covered by actual unit unions. Equal copy aliases are mapped only after body/scope/license/retention checks, with both origins retained. This is a declared source-span recall policy, not complete graded chunk-pair relevance, citation correctness or a change to historical qrels. Loaders reject changed content/locators/policy; actual index snapshots bind generated chunk maps/vectors and independently expected model/source digest.
# Chapter 21 metadata extension

V6's new workload binds every accepted source's raw bytes/version, canonical body/record digest, original span/line anchors and approved scope/use/license/retention. Its metadata digest additionally binds field values, schema and authorization-policy versions. Complete binary relevance is declared over each question's principal-authorized roster:108 reviewed pairs/11 positive memberships,9 positive/3 empty questions. Relevance is not inferred from arbitrary metadata matches; the narrow authored waiting-period fixture's matching records were inspected. Unreadable/admin-only rows are outside a reader's judgment universe, not grade0 negatives.

Current source/record/map/metadata mutations reject labels; the runner checks canonical-record/body and metadata digests before requirements. No automatic digest refresh preserves stale qrels. Actual normalized vectors/queries/chunks/fields and a trusted independently expected snapshot digest preserve reload identity. The four-node bridge instead uses a separately registered preassigned-score oracle/graph fixture, not human qrels. Static policy identity/local mutation detection is not a live revocation or freshness proof. Historical V0–V5 bindings/results remain unchanged.
