# V5 — canonical corpus and source quality

Chapter19 starts V5 with [source ingestion](../../chapters/chapter-19-source-ingestion-and-document-quality.md), after [V4's completed index laboratory](../V4/README.md). Its three bounded adapters produce auditable canonical documents. Chapter20 now completes V5's source/segmentation stage below. V0–V4 and Chapter19 source/result files remain unchanged; Chapter21 is not started.

## What runs

- [ingestion_ch19.py](ingestion_ch19.py): policy-before-read, exact source hashing, Markdown heading/prose/fenced-code units, strict HTML blocks/simple header-linked tables, native PDF page/bbox units, normalization, validation, quarantine and policy-partitioned exact duplicate grouping.
- [experiment_ch19.py](experiment_ch19.py): frozen source-bound span requirements, three randomized ingestion attempts/descriptor/mode and an unchanged lexical source diagnostic. No OCR, learned model, ANN, answer/context stage or live index service.
- [span_requirements.json](span_requirements.json): eight authored inspected requirements bound to seven licensed eligible sources' bytes/version/path/scope/license/retention. Not complete graded block qrels.
- [canonical_ch19](canonical_ch19): protected-in-production accepted records with normalized and raw extracted text, source hashes, locators, block maps, exclusions and record digests. The fixtures contain only fictional book-authored content.
- [chapter-19-experiment.json](chapter-19-experiment.json): the checked result and70 correlated samples, including54 ingestion attempts and16 source searches. No source/query text enters the ordinary sample envelopes.

## Reproduce

Installed checked versions are pinned in [requirements-ch19.txt](requirements-ch19.txt). The runner requires PyMuPDF and the standard library; ReportLab/Pillow generate fixtures. No dependency/model download happened during authoring. In a separately prepared environment, install these pins before reproducing.

```powershell
$ch19Runner = "projects/V5/experiment_ch19.py"
$ch19Output = "projects/V5/chapter-19-experiment-local.json"
$ch19Canonical = "build/ch19-local-canonical"
python -X utf8 $ch19Runner --output $ch19Output --canonical $ch19Canonical
python -X utf8 -m unittest discover -s projects/V5 -p 'test*.py' -v
```

The [fixture generator](make_fixture_ch19.py) uses invariant PDF creation and exact UTF-8 writes. The committed snapshots are authoritative for the checked requirements; generating with a different dependency/font stack can change PDF bytes. Review changed snapshots and requirements together rather than refreshing checksums automatically. The fixture-local `.gitattributes` prevents Git line-ending conversion of source bytes.

Complete [lab A0](../../labs/chapter-19/LAB.md#a0-construct-a-source-span-mapper) independently before reading the span mapper/reference answer. The intentionally unsolved starter is not part of the running engine.

## Checked decision

On **`ch19-source-quality-v1`**, structured preservation/traceable preservation is7/8; flat preservation is5/8 and traceable preservation0/8. Source Hit@1 remains6/8 in both. Structured accepts4/quarantines3/blocks2; flat accepts5/quarantines2/blocks2, from nine descriptors. All accepted required spans have region-level provenance. The image-only amendment remains missing; the merged-cell/encoding failures remain explicit. Both exact-copy aliases are retained.

Use structured canonical records for V5 development with these unresolved losses. This .875 is a new extraction metric/workload, not improvement over V3/V4 recall. Timings include mixed accepted/blocked/quarantined ingestion attempts and have tiny sample counts; no service performance verdict. See [the separate solutions](../../solutions/chapter-19-solutions.md) and [author review](../../authoring/reviews/chapter-19.md) for evidence and limits.

## Chapter 20: source-preserving chunk comparison

[Chapter20](../../chapters/chapter-20-chunking-as-a-retrieval-design-decision.md) uses the four unchanged accepted records plus a new fictional operations source parsed by the Chapter19 adapter. [chunking_ch20.py](chunking_ch20.py) implements char128, word24, word24-o8, word48, word96 and structure48; word24-parent reuses child vectors and expands original parents. Construct [lab A0](../../labs/chapter-20/LAB.md#a0-build-the-window-chunker) independently before reading references.

[evidence_spans_ch20.json](evidence_spans_ch20.json) binds five source/record/policy identities and original anchors to twelve inspected questions, eighteen required atoms on ten positives and two no-evidence cases. These are new source-span qrels, not Chapter19's extraction requirements or complete graded chunk-pair labels. Actual chunks carry text/range/source/record/chunker/policy identity and original block anchors. Normalized frozen384-vector exact search is body-only, with no new heading/summary prefix, reranker or generator.

[The checked record](chapter-20-experiment.json) retains264 correlated samples (12 query encodes +252 search/packing requests), all scored/top3 units and actual child/parent packing attempts. [index_ch20](index_ch20) holds canonical documents, actual vectors/token counts/query vectors and a trusted manifest. Reload validates source/model/chunk roster/map/vector identity and reproduces84 candidate rankings. No model downloads were enabled. The [requirements](requirements-ch20.txt) pin the observed stack and cached V3 revision.

```powershell
$ch20Runner = "projects/V5/experiment_ch20.py"
$ch20Output = "projects/V5/chapter-20-experiment-local.json"
$ch20Artifacts = "build/ch20-local-index"
python -X utf8 $ch20Runner --output $ch20Output --artifacts $ch20Artifacts
python -X utf8 -m unittest discover -s projects/V5 -p 'test*.py' -v
```

On **`ch20-chunked-evidence-v1`**, word24 candidate/context atom recall is .800/.7667; overlap .8667/.7833 with increased duplication; word48 .900/.8667; word96 1/.400; structure48 1/.900; whole-parent expansion .800/.400. Atom recall averages ten positives; duplication averages all twelve. Both no-evidence questions still return candidates. Structure48 is a provisional development choice and retains the green-wait packing miss. Generation/citation/abstention outcomes remain null. Parent517 WordPieces is counted but never encoded; whole-unit packing uses an80 encoder-token proxy, not generator accounting. Index/build/search/packing times and packed-coordinate payload are separate from JSON/RSS/service cost.

Stop before Chapter21. The separate [solutions](../../solutions/chapter-20-solutions.md) and [author review](../../authoring/reviews/chapter-20.md) document failures and limits. Historical corpora/results and extraction losses are preserved.
