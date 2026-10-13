# V6 — Governed metadata and eligibility

[Chapter 21](../../chapters/chapter-21-metadata-schemas-and-filtered-retrieval.md) begins V6 from completed [V5](../V5/README.md). V0–V5 corpus/code/results remain historical and unchanged. This snapshot implements Chapter 21 only; Chapter 22's incremental/freshness lifecycle is not started.

## Construction before reference

Complete [lab A0](../../labs/chapter-21/LAB.md#a0-construct-the-metadata-selector) independently: authorization/predicate intersection, language null and half-open aware dates on a fresh metadata-only fixture. Keep a first attempt and own counterexample before opening [metadata_ch21.py](metadata_ch21.py) or [separate answers](../../solutions/chapter-21-solutions.md). Running this snapshot alone does not meet that construction requirement.

## Implemented boundary

- Governed schema/policy, trusted fixture principal, tenant AND role eligibility, missing/invalid ACL deny, approved-use gate and exact typed predicates.
- Unchanged Chapter 19 adapters and Chapter 20 structure48 chunks over seventeen new fictional descriptors; fifteen accepted one-unit records, two blocked before source read. Ten A-reader, four B-reader and one admin-only accepted source.
- Metadata digest alongside raw/canonical/record/source/chunk/locator/model identity. Actual body-only normalized384 vectors, audited inputs, exact dot/stable ties and trusted JSON snapshot/reload.
- Per-principal exact postings and sorted UTC-date index. A frozen view detects local metadata mutation; it is not a live revocation service.
- Authorized semantic, exact task prefilter, task post3 and task post9. Every plan authorizes before vector scoring; postfilters operate only on task attributes inside that authorized roster.
- Chapter 20's actual whole-unit context selector, permission recheck before forward fetch, budget80 encoder WordPieces without special tokens and packing attempts/context IDs. No reranker/generator/citation verification.
- Four-node authorized task-transit/pruning demonstration with actual frontier events, separate registered workload and preassigned scores. Not HNSW or ANN timing.

Principals are fixtures, not authentication. Metadata is curated/checksum-bound, not signed. Services, query compilation, caches and live revocation/updates remain unrun.

## Workload and evidence identity

**`ch21-metadata-predicates-v1`** uses [qrels_ch21.json](qrels_ch21.json): twelve inspected single-author questions, nine positives/three empty, eleven relevant memberships among 108 fully reviewed authorized query–unit pairs. All nonlisted authorized pairs are binary0 under this narrow waiting-period task. Unreadable sources are not relevance negatives. The source manifest binds raw/canonical/record/policy/use/retention identity and metadata digests; requirements bind actual original-source spans/line anchors. A changed byte, locator, metadata/policy or descriptor roster fails rather than refreshing judgments.

[The checked record](chapter-21-experiment.json) retains156 correlated envelopes (12 query encodes,144 search/context requests), actual scored/shortlist/task-survivor/final IDs and scores, permitted task IDs/counts, packing attempts/context IDs, three randomized warm repeats and 144 ordered reload checks. A collector validates each request against its own principal-authorized roster. No B/admin ID can enter an A-reader sample. Ordinary samples contain no query/source text, raw predicates, exception strings or excluded private IDs. The combined fictional instructor artifact is not a tenant-visible log.

[index_ch21](index_ch21) stores actual vectors/queries, lengths and source/metadata/model bindings. The independently expected digest precedes snapshot validation; it detects mismatch, not remote authenticity. Longest indexed input64 including two specials is below 256; no truncation or model download occurs.

## Checked decision

On **`ch21-metadata-predicates-v1`**, semantic/prefilter/post3/post9 macro Recall@2 is .2963/.9630/.5185/.9630 over nine positives. Eligible-oracle recall is .3333/1/.5556/1. Context source recall happens to match candidate recall here. The relevance ceiling is .963 because one query has three positives at k2. Precision@2 over all twelve is .1667/.4167/.2500/.4167. Semantic returns candidates on all three empty tasks and 20 predicate violations/pass; filtered plans have 3/3 correct empty tasks and zero violations. Post3 still misses positive tasks. This is candidate emptiness, not generated abstention.

Prefilter scores .9167 units/question on average; other plans9. Retain exact prefilter for this small frozen fixture. Post9 ties quality with more scored work, but can fail on a rank 10 counterexample. Keep post3's A08 rank 7 and B03 rank 4 losses, and the range-query k2 ceiling. No universal ANN/production or cross-language/held-out claim follows. V5's different .900 context recall is not a prior point in an improvement curve.

The record reports nearest-rank filter/search p50/p95 over 36 requests/plan and separate view/packing times. The filter/search timer includes selection, policy checks, score accumulation and sorting; excludes view construction, context, encoding, quality and serialization. The context selector uses an encoder-token proxy rather than a generation budget. Coordinate payload23,040 bytes is not JSON/RSS; these tiny local trials cannot establish service latency.

## Reproduce without changing the checked baseline

Use the separately prepared [pinned environment](requirements-ch21.txt), Python3.14.2 and the cached V3 model revision. The runner disables downloads and fails if the model is unavailable.

```powershell
$ch21Runner = "projects/V6/experiment_ch21.py"
$ch21Output = "build/ch21-local-results.json"
$ch21Artifacts = "build/ch21-local-index"
python -X utf8 $ch21Runner --output $ch21Output --artifacts $ch21Artifacts
python -X utf8 -m unittest discover -s projects/V6 -p 'test*.py' -v
python -X utf8 visuals/chapter-21/render_visuals.py
```

[make_fixture_ch21.py](make_fixture_ch21.py) reproduces source bytes/metadata only; it never regenerates judgments. The committed sources/labels are the checked identities. Fixture changes need a reviewed new version, not an automatic checksum update. Protect equivalent real source/index/trace data by tenant policy.

See [lab](../../labs/chapter-21/LAB.md), [solutions](../../solutions/chapter-21-solutions.md), [figures](../../visuals/chapter-21/render_visuals.py) and [review](../../authoring/reviews/chapter-21.md). Stop before Chapter 22.
