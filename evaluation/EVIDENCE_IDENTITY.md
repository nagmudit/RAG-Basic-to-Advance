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
