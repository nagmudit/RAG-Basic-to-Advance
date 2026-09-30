# Lab 13 — Build, reload and diagnose an exact dense candidate index

**Prerequisites:** Chapters 9–12, the pinned V3 encoder in [V3 README](../../projects/V3/README.md), Python with Sentence Transformers, CPU PyTorch and matplotlib. Work from the repository root. Record your answers before reading the [solutions](../../solutions/chapter-13-solutions.md).

## Goal and baseline

Build a materialized exact dense index with source/model/text validation. First compare its rankings with Chapter 11's in-memory exact index. Then compare unchanged frozen dense and V2 BM25 on the new Chapter 13 judged stress set. Hypothesize that the persisted index preserves all top-two/top-eight IDs and that dense gains the colloquial slice without solving exact metadata IDs or no-evidence detection. Keep corpus, eligibility, encoder, text format, cosine, top-*k*, qrels and context budget fixed.

## A. Audit source and representation before running

1. Read [the snapshot code](../../projects/V3/dense_snapshot.py) and [new qrels](../../projects/V3/judgments_ch13.json). Count indexed and support-team eligible segments, dimension, float32 bytes, 14 diagnostic questions and reviewed pairs. Which manifest fields prevent a stale or mismatched query encoder from using this file? Which checks protect the source-to-row map?
2. Calculate cosine and raw dot for `q=(1,0)`, `a=(0.8,0.6)` and `b=(7,7)`. Rank both passages by each score. State what the loader enforces for the real vectors.
3. Inspect `acronym-sla`, `code-segment`, `style-ticket` and `none-private` qrels. Identify direct evidence and any grade-1 partial source. Explain why D10 has no grade, even for the private-addendum question.

## B. Reproduce the index and experiment

The runner uses the pinned locally cached model unless you explicitly allow a download. Use local output paths so the checked-in record and artifact remain fixed.

```powershell
$env:HF_HUB_OFFLINE='1'
$env:TRANSFORMERS_OFFLINE='1'
python -X utf8 -m unittest discover -s projects/V3 -p 'test_*.py' -v
python -X utf8 projects/V3/experiment_ch13.py --index-dir projects/V3/index_ch13-local --output projects/V3/chapter-13-experiment-local.json
python -X utf8 visuals/chapter-13/plot-13-01-dense-flow.py
python -X utf8 visuals/chapter-13/plot-13-02-score-trace.py
```

Compare `parity_summary`, `index_manifest`, `batch_encoding`, `summaries`, `cases` and `timings` with the [checked-in record](../../projects/V3/chapter-13-experiment.json). Repeated CPU timing will vary. Check that the materialized and in-memory IDs agree for all 17 Chapter 11 queries at both depths; do not assume score parity implies relevance parity. Verify that every dense stress query scores 12 eligible vectors and that D10 never reaches candidates or context.

## C. Test a mismatch safely

Use a *temporary copy* of the index so the checked-in artifact is not altered. The following code uses the manifest's expected vector hash to reject a one-byte corruption:

```powershell
@'
from pathlib import Path
from tempfile import TemporaryDirectory
from shutil import copytree
import sys
sys.path.insert(0, 'projects/V3')
sys.path.insert(0, 'projects/V1')
from dense_snapshot import load_snapshot
from lexical_index import build_index, load_corpus
base = build_index(load_corpus())
with TemporaryDirectory() as temp:
    target = Path(temp) / 'index'
    copytree('projects/V3/index_ch13', target)
    path = target / 'vectors.f32'
    data = bytearray(path.read_bytes())
    data[0] ^= 1
    path.write_bytes(data)
    try:
        load_snapshot(base, target)
    except ValueError as error:
        print(type(error).__name__, str(error))
    else:
        raise AssertionError('corrupted vector file was accepted')
'@ | python -X utf8 -
```

Also use `load_snapshot(base, 'projects/V3/index_ch13', expected_model_revision='wrong')` in a short Python probe. Explain why model dimension alone would be an insufficient compatibility check.

## D. Diagnose quality and cost

1. Make a top-two table for macro Recall, NDCG, each two-query stress slice and no-evidence candidate return. Identify a dense gain and at least two shared misses. Report denominator and the one-author limitations.
2. Trace `style-ticket` and `acronym-sla`: expected segment, BM25 IDs/scores, dense IDs/scores, selected context IDs and direct-evidence coverage. Explain why BM25 and cosine raw scores cannot be compared across methods.
3. Compare batch sizes 1, 4 and 16 in texts/second; identify the fastest **in your local run** and explain why it is not a universal batch-size recommendation. Separate model construction, snapshot build, snapshot load, warm query encode and exact scan.
4. Calculate raw vector storage for 13 and one million rows. A teammate says the 20 ms dense request proves ANN is needed. Explain which measured stage ANN could affect, the exact-neighbor oracle needed to evaluate it, and which work remains unchanged.
5. Propose an authorized exact-ID route for `D6:row-2:0` and a separate no-evidence/abstention evaluation. Preserve source identity and permission checks.

## Submission

Provide the arithmetic, a manifest-integrity explanation, one comparison table, three failure traces, an annotated latency boundary, and a narrow next-step proposal. Preserve any negative result. Do not tune model or thresholds on these 14 diagnostic questions and call the same set held out.
