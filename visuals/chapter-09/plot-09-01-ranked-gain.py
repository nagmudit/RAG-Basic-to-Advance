"""Figure 9.01: three toy rankings, explicit grades, and cumulative DCG.

Input is the four-item fictional hand example in Chapter 9. No sampling or
uncertainty is involved; the plot validates its final gain against V2 metrics.
"""

import math
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "projects" / "V2"))
from eval_ch09 import evaluate_ranking  # noqa: E402


GRADES = {"A": 2, "B": 1, "C": 0, "D": 0}
RUNS = {
    "Ideal: A B C": ["A", "B", "C"],
    "Late evidence: C B A": ["C", "B", "A"],
    "Partial first: B C A": ["B", "C", "A"],
}
COLORS = {2: "#315fa7", 1: "#b85c28", 0: "#8d939c"}


def cumulative_dcg(ids):
    total = 0.0
    out = []
    for rank, item in enumerate(ids, 1):
        total += (2 ** GRADES[item] - 1) / math.log2(rank + 1)
        out.append(total)
    return out


def main():
    plt.rcParams["svg.hashsalt"] = "rag-ch09-gain-figure"
    plt.rcParams["font.family"] = "DejaVu Sans"
    fig, (left, right) = plt.subplots(1, 2, figsize=(11.4, 5.5),
                                      gridspec_kw={"width_ratios": [1, 1.15]},
                                      layout="constrained")
    fig.suptitle("The same relevant items can earn different rank-sensitive gain",
                 fontsize=13)
    names = list(RUNS)
    for row, (name, ids) in enumerate(RUNS.items()):
        y = len(names) - row
        for rank, item in enumerate(ids, 1):
            grade = GRADES[item]
            left.scatter(rank, y, s=1750, marker="s", color=COLORS[grade],
                         edgecolor="white", linewidth=1.2, zorder=3)
            left.text(rank, y, f"{item}\ng={grade}", va="center", ha="center",
                      color="white", fontsize=10, weight="bold", zorder=4)
        gains = cumulative_dcg(ids)
        measured = evaluate_ranking(ids, GRADES, 3)
        assert math.isclose(gains[-1], measured["dcg_at_k"])
        right.plot((1, 2, 3), gains, marker="o", linewidth=2.2,
                   label=f"{name} · NDCG@3={measured['ndcg_at_k']:.3f}")
    left.set(xlim=(.55, 3.45), ylim=(.45, 3.55), xticks=(1, 2, 3),
             xlabel="Rank (1 is first result)",
             yticks=(3, 2, 1), yticklabels=names,
             title="A · Ranked IDs and qrel grades")
    left.grid(axis="x", alpha=.2)
    right.set(xlim=(1, 3), ylim=(0, 3.95), xticks=(1, 2, 3),
              xlabel="Rank cutoff k", ylabel="Cumulative DCG@k (gain units)",
              title="B · Discounted gain accumulates by rank")
    right.grid(alpha=.25)
    right.legend(loc="lower right", fontsize=8)
    svg = HERE / "figure-09-01-ranked-gain.svg"
    png = HERE / "figure-09-01-ranked-gain.png"
    fig.savefig(svg, metadata={"Date": None, "Creator": "Chapter 9 plot source"})
    fig.savefig(png, dpi=180, metadata={"Software": "Chapter 9 plot source"})
    plt.close(fig)
    svg.write_text("\n".join(line.rstrip() for line in
                             svg.read_text(encoding="utf-8").splitlines()) + "\n",
                   encoding="utf-8")
    print(f"Wrote {svg} and {png}")


if __name__ == "__main__":
    main()
