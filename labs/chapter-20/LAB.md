# Chapter 20 lab — choose boundaries with source evidence

Continue from [Chapter 19](../chapter-19/LAB.md) and exact frozen retrieval from Chapters 11–13. Workload **`ch20-chunked-evidence-v1`** is new: five approved canonical sources, twelve inspected questions, eighteen required atoms on ten positives and two no-evidence cases. Preserve earlier data and quarantines. No generator or semantic/RAPTOR/late-chunking model runs.

## A0. Build the window chunker

Before opening the reference/answer, edit [implement.py](implement.py). Validate integer `size>0` and `0<=overlap<size`, excluding booleans. Find consecutive nonwhitespace words in original text and emit half-open code-point intervals from first-word start to last-word end. Advance `size-overlap` words; stop after the first window reaching the last word. Empty/whitespace-only text returns `[]`.

Hand-map ` A  BB\nCCC D E ` with length3/overlap1 and length2/overlap0. Explain why joining split words would invalidate offsets. Create your own longer fixture with Unicode, newlines and a shortened tail. Then run:

```powershell
python -X utf8 labs/chapter-20/check_implementation.py
```

Keep the first attempt and its validation reasoning. Reference execution alone does not satisfy construction. Compare afterward with the separate answer:

```powershell
$ch20Answer = "solutions/code/chapter_20_mechanisms.py"
python -X utf8 labs/chapter-20/check_implementation.py --implementation $ch20Answer
```

## A. Inspect source and judgments

Read the new [operations manual](../../projects/V5/fixtures_ch20/operations.md) and [source descriptor](../../projects/V5/source_descriptor_ch20.json), plus Chapter 19's unchanged accepted snapshots. Inspect Blue/Green ownership, approval/exception differences, billing boundary and complementary drill evidence. Read [source-span labels](../../projects/V5/evidence_spans_ch20.json): their intervals and original anchors are independent of chunk IDs. The scan/private-console questions have no eligible published evidence.

Calculate window count for19 words, length8, overlap3. Compute the approximate assignment expansion at25%/50% overlap and exact redundancy for intervals `[0,6)`,`[4,10)`. Distinguish word/token assignments from the experiment's nonwhitespace source-position redundancy.

## B. Reproduce at least three matched policies

The reference implements six base policies plus shared-child parent expansion. The frozen cached MiniLM revision/model dependencies are inherited from V3; new [requirements](../../projects/V5/requirements-ch20.txt) document the checked stack. No model download is enabled by this runner. If the pinned cache is absent, prepare the explicitly pinned V3 model through its documented setup first.

```powershell
$ch20Runner = "projects/V5/experiment_ch20.py"
$ch20Output = "projects/V5/chapter-20-experiment-local.json"
$ch20Artifacts = "build/ch20-local-index"
python -X utf8 $ch20Runner --output $ch20Output --artifacts $ch20Artifacts
python -X utf8 -m unittest discover -s projects/V5 -p 'test*.py' -v
```

Use `word24`, `word24-o8` and `structure48` for the minimum comparison; inspect `word48`, `word96`, `char128` and parent expansion as well. Keep the same twelve questions, labels, model/body input, exact top3 and80 encoder-WordPiece packing proxy. Report candidate/context atom recall, complete context evidence, duplicate positions, encoded input counts/vector payload and separate search/packing latency. Use ten positives for recall, all twelve for mean duplication and two negatives for candidate-return rate. Preserve local timings separately.

Explain the actual tokenizer audit and why a517-WordPiece parent can be counted but not encoded by this256-limit model. The parent is also too large for the80 budget. Do not call the proxy a generator-token budget or claim abstention/answer quality.

## C. Diagnose and trace

1. Inspect `green-fail` in overlap mode: complete candidate evidence becomes half after selecting29/28 WordPieces and rejecting27. Record actual request IDs, candidate ranks and packing reasons.
2. Inspect `drill` in `word24`: all three atoms reach candidates; a31-WordPiece unit is dropped after31/27 are selected. Identify its exact required span and original source lines.
3. Inspect `green-wait` in `structure48`: candidate recall1 becomes context recall0. Explain why the aggregate winner retains a failure.
4. Contrast `word24`/`word24-parent` using identical child candidates. Trace parent identity, scope/source check, deduplication and budget rejection.
5. Trace a PDF chunk crossing pages through canonical range and every intersecting original block locator. Save a source/record/model/chunker identity card. Correct source mapping does not prove claim-level citation support.

## D. Defend a provisional policy

Write a decision card with workload/denominators, simpler baseline, change, controls, failure examples, costs, limitations and a provisional choice. Explain why the inspected set supplies no held-out generalization. Propose one bounded section/neighbor repair and the regression case needed to test it; do not report an unrun improvement.

Compare parent expansion, source-heading prefixes, generated contextual descriptions, summary trees and late chunking by intervention stage, required data/model, cost and source-support risk. Design a real development/test split without using the test questions for parameter selection. Explain what must be reindexed and rejudged after a source/parser/chunker change.

## Submission and learning gate

Submit your independent chunker/own fixture, hand calculations, matched comparison, three failure traces, PDF lineage card and design defense. Suggested rubric: construction25%, math/units20%, evaluation/trace diagnosis35%, design/continuity20%; suggested threshold80%. Authorization leaks, stale-label suppression, invented offsets or fabricated model/generator results require correction regardless of score. These are learner gates, not observed mastery outcomes.

Use [separate solutions](../../solutions/chapter-20-solutions.md) after your attempt and revisit day1/3/7/21 recall. Part V's cumulative checkpoint remains after Chapter22. Stop before Chapter21.
