# V7 — Query interpretation and bounded reformulation

[Chapter 23](../../chapters/chapter-23-normalize-classify-route-and-contextualize-queries.md) begins V7 from completed [V6](../V6/README.md). V0–V6 code, source capsules, judgments, vectors and result files remain historical and unchanged. Its routing checkpoint below is frozen. Chapter 24's separate reformulation checkpoint follows it; Chapter 25 fusion remains unstarted, so V7 is not yet complete.

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

A measured new query policy/dataset needs reviewed source/query/permission/judgment identities and a registered comparison. Digest replacement is not reassessment. See [lab](../../labs/chapter-23/LAB.md), [solutions](../../solutions/chapter-23-solutions.md), [figures](../../visuals/chapter-23/render_visuals.py) and [author review](../../authoring/reviews/chapter-23.md). Chapter 24 follows.

## Chapter 24 — Bounded reformulation checkpoint

Complete [Chapter 24](../../chapters/chapter-24-rewrite-expand-and-decompose-queries.md) and independently implement admission and dependency readiness in [A0](../../labs/chapter-24/LAB.md#a0--construct-before-opening-the-reference) before opening [reformulate_ch24.py](reformulate_ch24.py). The fresh checker imports only the learner's implementation. [Separate solutions](../../solutions/chapter-24-solutions.md) explain the reference; running it earns no construction credit.

### Implemented data path

[retrieval_ch24.py](retrieval_ch24.py) extends a copy of the frozen source capsule roster with ten governed fixtures. Eighteen historical body vectors remain unchanged; ten new bodies use the same pinned MiniLM body-only contract. Current authority, task fields and as-of selection still precede scoring. Each proposal binds the original request, principal, typed constraints, source authority, model contract and admission-policy version. Cheap atom checks reject changed IDs/numbers/known entities; they do not prove semantic equivalence.

The original/multi/hypothetical modes hold exact dense retrieval fixed, including for IDs, to isolate representation. Multi retains original plus at most two paraphrases. Hypothetical uses one admitted **author-written**, source-aware passage, with original fallback on rejection. No language model generates queries. Both methods keep the original interpreter and constraints; the duration/count false trigger remains untouched. At most three branches, 128 admitted whitespace words, 192 executed-input encoder WordPieces, branch depth two, global candidate cap two and inherited context budget eighty are explicit. Encoder inputs over 256 WordPieces reject without truncation.

Branch shortlists are interleaved by rank, deduplicated by immutable unit identity and capped. First occurrence owns its actual branch score; the merge never compares those scores or invents fused relevance. Raw pools, shortlists, full admission, capped IDs, origin branches and real packing outcomes survive in correlated frames. Current grants are checked again before source-version forward fetch. Hypothetical text cannot become context. Generator/token/monetary fields stay null when unrun.

### Checked comparison

**`ch24-frozen-reformulations-v1`** binds 28 source-version capsules, 25 logical heads, 16 original questions and frozen source-aware drafts. Eleven positive questions have twelve inspected source requirements; three required-empty tasks and two guards have separate denominators. The known answerable duration query remains a positive miss. No train/dev/test or zero-shot/generalization claim is made.

Original/multi/hypothetical union, Recall@2 and context recall are **.9091/.9091/.7273**. Multi scores 19.25 versus 6.4375 query-unit pairs per original task, about 2.99 times the work, with no required-recall gain. Hypothetical q06/q07 lose authority/certificate evidence through topic drift. Guard and required-empty decisions are correct, but intended outcome accuracy over all 16 is 15/16. No additional **required** evidence is lost at cap/packing; other candidates can still be lost, as original q07's rejected A12 shows. Both q10 publications fit in 68 WordPieces.

All ten positive questions that reach retrieval already have full original recall; the fixed interpreter blocks the eleventh. The feasible ceiling is therefore 10/11. This workload cannot establish whether reformulation recovers a correctly interpreted baseline retrieval miss. A follow-up needs independently frozen questions with that headroom. Deliberately faulty hypothetical drafts illustrate possible failures, not a live generator's error frequency.

[chapter-24-experiment.json](chapter-24-experiment.json) retains 291 parent/child envelopes (144 parents/147 branches), 38 separately measured prepared-input encodes and one privileged document-build sample. Three shuffled warm repeats use seed 24014 and prepared vectors. Search percentiles exclude proposal generation, request-time encoding, packing and serving overhead; they are not end-to-end service latency. The snapshot stores actual body/query vectors and token counts under an independently expected digest. Forty-eight query/method outcomes replay through all raw/intermediate/final scores, branch provenance and ordered context.

**`ch24-decomposition-budget-v1`** has four scheduler-only controls: shared step exhaustion, failed prerequisites, cycle and missing task. It records readiness/completion/blocking with null retrieval/context/model stages. No evidence-dependent multi-hop execution or answer is implied. Fault injection in tests checks partial branch failure and redacted errors; it is not a deadline experiment.

### Reproduce Chapter 24

```powershell
$ch24Runner = 'projects/V7/experiment_ch24.py'
$ch24Output = 'build/ch24-local-results.json'
$ch24Artifacts = 'build/ch24-local-index'
python -u -X utf8 $ch24Runner --output $ch24Output --artifacts $ch24Artifacts
python -X utf8 -m unittest discover -s projects/V7 -p 'test*.py' -v
python -X utf8 visuals/chapter-24/render_visuals.py
```

Use the existing pinned stack; model downloads remain disabled. The [labels](qrels_ch24.json), [drafts/prompt specification](reformulations_ch24.json), [sources](fixtures_ch24/sources.json), [runner](experiment_ch24.py), [snapshot](index_ch24/snapshot.json), [lab](../../labs/chapter-24/LAB.md), [solutions](../../solutions/chapter-24-solutions.md), [visual source](../../visuals/chapter-24/render_visuals.py) and [author review](../../authoring/reviews/chapter-24.md) form one checkpoint. Changed sources/questions/drafts require reviewed identities and a registered comparison. Do not refresh expected hashes to hide changed judgments. No Chapter 23 longitudinal gain, learned/live query generator, score fusion, production service or generated-answer metric is claimed. Chapter 25 remains unstarted.
