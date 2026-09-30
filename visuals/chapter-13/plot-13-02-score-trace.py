"""Figure 13.02. Reproduce one fixed score trace from the Chapter 13 record."""

import json
from pathlib import Path
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
record = json.loads((HERE.parent.parent / "projects" / "V3" /
                     "chapter-13-experiment.json").read_text(encoding="utf-8"))
case = next(row for row in record["cases"]
            if row["query_id"] == "style-ticket" and row["k"] == 2)
fig, axes = plt.subplots(1, 2, figsize=(11.4, 3.5), layout="constrained")
for ax, name, title, unit in zip(axes, ("bm25", "dense"),
                                 ("BM25 lexical", "Exact dense"),
                                 ("BM25 score (model-specific)", "Cosine (unitless)")):
    result = case["modes"][name]
    ids = result["candidate_ids"]
    scores = result["candidate_scores_raw"]
    bars = ax.barh([0, 1], scores, color=["#33865f" if sid == "D7:timeline:0"
                                       else "#6c88a2" for sid in ids], height=.48)
    ax.set_yticks([0, 1], ids)
    ax.invert_yaxis()
    ax.set_xlim(0, max(scores) * 1.26)
    ax.set_title(title, fontsize=12)
    ax.set_xlabel(unit)
    ax.grid(axis="x", alpha=.18)
    ax.set_axisbelow(True)
    for bar, value in zip(bars, scores):
        ax.text(value + max(scores) * .025, bar.get_y() + bar.get_height()/2,
                f"{value:.3f}", va="center", fontsize=9)
fig.suptitle("style-ticket: target D7 is green; score scales are not comparable", fontsize=13)
for ext in ("svg", "png"):
    fig.savefig(HERE / f"figure-13-02-score-trace.{ext}", dpi=180)
svg = HERE / "figure-13-02-score-trace.svg"
svg.write_text("\n".join(line.rstrip() for line in svg.read_text(encoding="utf-8").splitlines()) + "\n",
               encoding="utf-8")
plt.close(fig)
