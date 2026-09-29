"""Render Figure 8.01 from Chapter 8's checked-in fictional WAND trace.

Panel A shows the implemented global-bound WAND cursor movement. Panel B
shows *conceptual* two-docID block maxima computed from the same impacts;
the project does not implement Block-Max WAND. No randomness or uncertainty.
"""

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
DATA = HERE.parents[1] / "projects" / "V2" / "chapter-08-experiment.json"


def main():
    record = json.loads(DATA.read_text(encoding="utf-8"))["toy"]
    steps = record["local_fictional_cursor_steps"]
    assert [step["action"] for step in steps] == ["score", "seek", "score"]
    theta = steps[0]["threshold_after"]
    assert steps[1]["from"] == 1 and steps[1]["to"] == 5
    colors = {"rare": "#355ca8", "common": "#c45a28"}
    plt.rcParams["svg.hashsalt"] = "rag-ch08-wand-figure"
    plt.rcParams["font.family"] = "DejaVu Sans"
    fig, (top, bottom) = plt.subplots(2, 1, figsize=(11.4, 7.2),
                                     gridspec_kw={"height_ratios": [1, 1.1]},
                                     layout="constrained")
    fig.suptitle("One exact query: cursors, bounds, and the top-1 threshold", fontsize=14)

    for term, y in (("rare", 1), ("common", 0)):
        for row in record["postings"][term]:
            ordinal = row["ordinal"]
            top.scatter(ordinal, y, color=colors[term], s=100, zorder=3)
            top.annotate(f"{row['impact']:.3f}", (ordinal, y),
                         xytext=(0, 11 if y else -19), textcoords="offset points",
                         ha="center", fontsize=9)
    top.axvspan(.65, 4.35, color="#ece9e2", alpha=.85,
                label="P2–P5: common postings jumped")
    top.annotate("common cursor seeks P2 → P6",
                 xy=(5, -.09), xytext=(1, -.43),
                 arrowprops={"arrowstyle": "->", "lw": 1.7, "color": "#333333"},
                 fontsize=10, color="#333333")
    top.annotate(f"after P1: θ = {theta:.3f}", xy=(0, 1),
                 xytext=(.45, 1.31), fontsize=10,
                 arrowprops={"arrowstyle": "->", "lw": 1.1})
    top.set(xlim=(-.45, 5.5), ylim=(-.58, 1.48),
            xticks=range(6), xticklabels=[f"P{i}" for i in range(1, 7)],
            yticks=[0, 1], yticklabels=["common", "rare"],
            xlabel="Eligible segment ID (ascending cursor order)",
            ylabel="Query term / posting list",
            title="A · Global-bound WAND scores P1 and P6; it seeks over four postings")
    top.grid(axis="x", alpha=.18)
    top.legend(loc="upper right", frameon=False)

    blocks = record["docid_block_bounds_conceptual_only"]
    xs = [0, 1, 2]
    common = [block["upper_bound"] for block in blocks["common"]]
    rare = [block["upper_bound"] for block in blocks["rare"]]
    bottom.bar(xs, common, color=colors["common"], label="common max impact")
    bottom.bar(xs, rare, bottom=common, color=colors["rare"],
               label="rare max impact")
    bottom.axhline(theta, color="#1d252b", linestyle="--", linewidth=1.7,
                   label=f"heap threshold θ = {theta:.3f}")
    for x, a, b in zip(xs, common, rare):
        near_threshold = abs(a + b - theta) < .09
        bottom.annotate(f"{a+b:.3f}", (x, a+b),
                        xytext=(0, -8 if near_threshold else 5),
                        textcoords="offset points", ha="center",
                        va="top" if near_threshold else "bottom",
                        color="white" if near_threshold else "#222222", fontsize=9)
    bottom.set(xlim=(-.55, 2.55), ylim=(0, 1.55),
               xticks=xs, xticklabels=["B1: P1–P2", "B2: P3–P4", "B3: P5–P6"],
               xlabel="Conceptual two-docID range (P7 legal-only excluded)",
               ylabel="Sum of per-term block maxima (BM25 score units)",
               title="B · Block bounds are tighter; B2 and B3 fall below θ")
    bottom.grid(axis="y", alpha=.18)
    bottom.legend(loc="upper right", frameon=False, ncol=2)

    stem = HERE / "figure-08-01-cursors-bounds-threshold"
    fig.savefig(stem.with_suffix(".svg"), metadata={
        "Date": "2026-09-29", "Creator": "Chapter 8 toy WAND trace",
    })
    fig.savefig(stem.with_suffix(".png"), dpi=180,
                metadata={"Software": "matplotlib"})
    plt.close(fig)
    svg = stem.with_suffix(".svg")
    svg.write_text("\n".join(line.rstrip() for line in
                             svg.read_text(encoding="utf-8").splitlines()) + "\n",
                   encoding="utf-8")
    print(f"Wrote {stem.with_suffix('.svg')} and {stem.with_suffix('.png')}")


if __name__ == "__main__":
    main()
