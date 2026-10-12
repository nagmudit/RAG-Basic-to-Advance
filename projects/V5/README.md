# V5 — canonical corpus and source quality

Chapter19 starts V5 with [source ingestion](../../chapters/chapter-19-source-ingestion-and-document-quality.md), after [V4's completed index laboratory](../V4/README.md). Its three bounded adapters produce auditable canonical documents. Chapter20's chunking comparison is not authored here. V0–V4 source/result files remain unchanged.

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
