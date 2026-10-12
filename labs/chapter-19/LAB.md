# Chapter 19 lab — inspect, preserve and trace source evidence

Use [the chapter](../../chapters/chapter-19-source-ingestion-and-document-quality.md) after Chapters 02/05/18. Workload: **`ch19-source-quality-v1`**. Preserve V0–V4; this lab starts V5 with canonical records before Chapter20's chunking comparisons.

## A0. Construct a source-span mapper

Before opening the reference or answer, edit [implement.py](implement.py). Its ordered block map uses half-open Unicode-code-point ranges. Validate every block, require positive widths and no overlaps, then validate the request `0 <= start < end <= last_end`. For each block return `block_id`, its positive `canonical_overlap` and its unchanged whole `locator`. Separator-only spans return `[]`. Empty maps contain no valid span. Booleans are not integer offsets under this contract.

Hand-predict `[2,7)` and `[3,5)` for blocks `[0,3)` on page1 and `[5,9)` on page2. Use interval intersection. Create your own three-block fixture with gaps/cross-block span before running [the fresh checker](check_implementation.py):

```powershell
python -X utf8 labs/chapter-19/check_implementation.py
```

Keep your first attempt and validation reasoning; running reference code does not satisfy construction. After your attempt, compare with the separate answer:

```powershell
$ch19Answer = "solutions/code/chapter_19_mechanisms.py"
python -X utf8 labs/chapter-19/check_implementation.py --implementation $ch19Answer
```

## A. Inspect original snapshots before reading extracted output

Inspect [the runbook](../../projects/V5/fixtures/runbook.md), [HTML policy](../../projects/V5/fixtures/retry.html), [contract PDF](../../projects/V5/fixtures/contract.pdf) and [scanned amendment](../../projects/V5/fixtures/scanned.pdf). These are fictional book-authored snapshots; render PDFs if needed.

Write a source inventory with format, expected content regions, consequential facts/relationships and proposed anchors. Include East's retry limit, the HTTP403 exception, code indentation, the decomposed accent and both PDF body statements. Inspect the image-only amendment visually; do not infer its absence from native text extraction. Record five ways a flat extraction could fail.

Read [sources.json](../../projects/V5/fixtures/sources.json) and the [frozen requirements](../../projects/V5/span_requirements.json). Explain why one source is scope-blocked and another rights-blocked before reading their bytes. Inspect the UTF-8 and merged-cell failure fixtures through the authorized review route. Do not place their raw content or exception strings into ordinary telemetry.

## B. Reproduce the controlled comparison

Checked versions: PyMuPDF1.27.2, ReportLab4.4.10, Pillow12.1.1. ReportLab/Pillow recreate fixtures; ingestion needs PyMuPDF/standard library. Prepare dependencies from the pinned [requirements](../../projects/V5/requirements-ch19.txt). No OCR, encoder, database or model download is needed.

```powershell
$ch19Runner = "projects/V5/experiment_ch19.py"
$ch19Local = "projects/V5/chapter-19-experiment-local.json"
$ch19Canonical = "build/ch19-local-canonical"
python -X utf8 $ch19Runner --output $ch19Local --canonical $ch19Canonical
python -X utf8 -m unittest discover -s projects/V5 -p 'test*.py' -v
```

Quality uses eight inspected probes; timing uses three randomized attempts/descriptor/mode. Preserve the checked record. Source/policy changes require reviewed requirements and a new corpus/workload version; automatic checksum refresh is not review.

Report preservation, traceable preservation and alias-aware source Hit@1 with denominator8 and workload ID. Report accepted/quarantined/blocked counts with denominator9 and license-eligible source count7. Separate mixed ingestion-attempt latency from lexical search, and label your run's sample counts/boundaries. Inspect `table`, `unicode`, `clock` and `retention`; include actual failing request IDs and outcomes. No answer/faithfulness/abstention measurement is implied.

## C. Trace a fixed retrieval unit to its original page

Use structured canonical `S-pdf`, range `[24,53)`. Apply your mapper. Save a lineage card with source/version/raw digest, record/parser/normalization identity, canonical substring/range and source page/bbox/coordinate system. Open page1 and verify that the rectangle encloses the first-response statement. This manually selected fixed unit satisfies the provenance exercise; it is not a chunk-strategy implementation.

Repeat with `[50,80)`. Predict which three native blocks and two source pages it intersects, and distinguish inserted separators. Explain why the returned boxes cover full blocks and cannot certify exact inverse raw character positions. Repeat one accent example and calculate raw/canonical code-point and UTF-8 byte counts.

## D. Repair policy without hiding losses

1. Defend quarantine for the scan, invalid bytes and merged table. Identify a safe reason code and a next review action for each. No OCR or repair is required to pass this bounded lab.
2. Construct a footer containing the only exception and show how a broad removal rule would fail. Write a new proposed source-span requirement before changing the adapter.
3. Describe how identical text under two scopes/different retention policies should be grouped and deleted. Keep all source aliases and state who owns actual deletion propagation.
4. Design a 60-source review sample across four source types; cover accepted and failed inputs, sizes and languages. State sampling bias and the evidence needed before extrapolating.
5. Produce a publication decision card: accepted artifacts, unresolved losses, quality gates, timing uncertainty and stages not run.

## Submission and rubric

Submit your first mapper/own fixture, source inventory, local experiment, lineage card, four failure traces and publication defense. Suggested rubric: construction25%, source reasoning25%, evidence/telemetry30%, governance20%; threshold80%. Unauthorized reads, invented offsets, silently refreshed bindings or fabricated OCR/generation require correction regardless of score. This is a teaching rubric.

Consult [separate solutions](../../solutions/chapter-19-solutions.md) after attempting the work; revisit day1/3/7/21 recall. Part V's cumulative assessment belongs after Chapter22. Stop here.
