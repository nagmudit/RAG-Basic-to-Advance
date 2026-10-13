# V7 — Query interpretation and routing checkpoint

[Chapter 23](../../chapters/chapter-23-normalize-classify-route-and-contextualize-queries.md) begins V7 from completed [V6](../V6/README.md). V0–V6 code, source capsules, judgments, vectors and result files remain historical and unchanged. Chapter 24 rewriting and Chapter 25 fusion are unstarted; this is the query-routing stage, not completed V7.

## Construct, then inspect

Complete [lab A0](../../labs/chapter-23/LAB.md#a0-construct-the-five-kind-policy) before viewing [query_ch23.py](query_ch23.py). Independently implement a five-kind capability/ambiguity/partial-stop policy and predict a fresh fixture. [Separate answers](../../solutions/chapter-23-solutions.md) follow; running this project earns no construction credit.

## Actual mechanisms and boundaries

- Preserve original text; derive NFC/whitespace surface without changing exact ID case. Cue matching, slots and their origins remain distinct.
- Closed English grammar: exact record, two entity names, UTC publication day/range, controlled source-effective as-of and one bound prior-turn record capsule.
- Session/principal/expiration/reference checks precede contextualization. These trusted fixture bindings are not authentication/signatures.
- Current authorization intersects historical grants before body/vector scoring. Existing V6 authority/capsules/checkpoint and body vectors are reused under their independently expected digest.
- Lexical BM25 over record ID plus body uses authorized-view statistics; exact task fields survive lexical/dense dispatch. Dense uses compatible normalized surface-query vectors. Explicit model/input contracts are checked; invented SQL/graph/web executor capabilities reject.
- One compatible lexical/dense retry on timeout, at most two actual attempts. Successful empty hard IDs do not broaden; integrity/permission errors are not timeout fallbacks.
- Unavailable graph permits marked partial lexical evidence; count/live-web routes remain unsupported. No SQL/graph/web, learned router, generated reformulation, fusion, reranker or generator ran.
- Current permission is rechecked before actual-version forward fetch. Inherited whole-unit context uses each unit's permitted role scope and shared eighty-encoder-WordPiece budget, not generator accounting.

## Bound workloads and checked results

**`ch23-query-plans-v1`** binds eighteen unchanged V6 source capsules, final ordered authority, twenty-one original query/context/principal definitions and independent expected plans. Ten positive questions have eleven inspected spans; four tasks require empty evidence; seven guards have operation/outcome labels. These are not complete graded pairs or train/dev/test splits.

All-dense / interpreted dense / rule routing Recall@2 and context recall are **.400/.900/.900**. Required-empty correctness is **0/1/1** over four tasks; guard decision accuracy **0/1/1** over seven. Full rule-plan accuracy is **20/21**. The answerable quantity query remains a false aggregation trigger; lexical selection ties interpreted dense. Gains over all-dense cannot be attributed solely to lexical retrieval. Both required publication units fit: 34 + 34 = 68 WordPieces under budget 80, with no additional context recall loss.

[The checked record](chapter-23-experiment.json) retains 333 main envelopes: 21 actual query encodes, 189 parents and 123 actual route attempts. Query-process, eligibility, sequential attempt totals and packing timings are separate. Three warm repeats shuffle query/policy order with seed 23014. Zero-search guard/empty parents contribute to route-search percentiles, so these are not backend-only or service latency results.

**`ch23-bounded-route-fallback-v1`** supplies four controls and ten envelopes: two successful single-alternative fallbacks, a two-timeout budget stop and an empty exact-ID task with zero attempts. Immediate exception injection is not measured deadline behavior; these controls have no relevance labels.

Parent/child IDs, common versions/status/reasons, actual scored/positive-score/shortlist/final pools, task IDs, fixed constraint digests and packing/context persist. Ordinary frames omit query/source/principal/context-capsule/raw-predicate/exception text. IDs and digests still require restricted access. The combined fictional instructor record is not tenant-visible logging.

[index_ch23/queries.json](index_ch23/queries.json) stores actual query vectors/token counts, bound to source/authority/generation/query/model contracts under an independently expected digest. Sixty-three raw/final-score/context outcomes replay. Documents remain in the historical V6 bank; no new document model or ANN geometry is claimed.

## Reproduce

Use the existing [pinned V6 stack](../V6/requirements-ch21.txt) and cached model; downloads are disabled. Write replay outputs under `build`:

```powershell
$ch23Runner = "projects/V7/experiment_ch23.py"
$ch23Output = "build/ch23-local-results.json"
$ch23Artifacts = "build/ch23-local-index"
python -X utf8 $ch23Runner --output $ch23Output --artifacts $ch23Artifacts
python -X utf8 -m unittest discover -s projects/V7 -p 'test*.py' -v
python -X utf8 visuals/chapter-23/render_visuals.py
```

A measured new query policy/dataset needs reviewed source/query/permission/judgment identities and a registered comparison. Digest replacement is not reassessment. See [lab](../../labs/chapter-23/LAB.md), [solutions](../../solutions/chapter-23-solutions.md), [figures](../../visuals/chapter-23/render_visuals.py) and [author review](../../authoring/reviews/chapter-23.md). Chapter 24 remains unstarted.
