"""Figure 11.01: independent query/passage encoders and a dot-score matrix.

Vectors are hand-authored in arbitrary feature units. The script checks every
matrix value and the mean InfoNCE loss against Chapter 11's arithmetic code.
"""

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "projects" / "V3"))
from contrastive_math import in_batch_loss  # noqa: E402
from exact_vectors import dot  # noqa: E402

QUERIES = ((1, 0), (0, 1))
PASSAGES = ((3, 0), (1, 2))
SCORES = tuple(tuple(dot(q, p) for p in PASSAGES) for q in QUERIES)
assert SCORES == ((3, 1), (0, 2))
LOSS, PROBABILITIES = in_batch_loss(SCORES)


def box(ax, xy, width, height, label, *, color):
    patch = FancyBboxPatch(xy, width, height, boxstyle="round,pad=0.02",
                           linewidth=1.2, edgecolor="#334155", facecolor=color)
    ax.add_patch(patch)
    ax.text(xy[0] + width / 2, xy[1] + height / 2, label,
            ha="center", va="center", fontsize=9)


def arrow(ax, start, end, label=None):
    ax.add_patch(FancyArrowPatch(start, end, arrowstyle="-|>", mutation_scale=12,
                                 linewidth=1.3, color="#475569"))
    if label:
        ax.text((start[0] + end[0]) / 2, (start[1] + end[1]) / 2 + .1,
                label, ha="center", fontsize=8, color="#334155")


def main():
    plt.rcParams["svg.hashsalt"] = "rag-ch11-encoders"
    plt.rcParams["font.family"] = "DejaVu Sans"
    fig, (left, right) = plt.subplots(1, 2, figsize=(11.5, 5.1),
                                      gridspec_kw={"width_ratios": [1.2, 1]},
                                      layout="constrained")
    fig.suptitle("Independent encoding makes a reusable similarity matrix", fontsize=13)
    left.set(xlim=(0, 10), ylim=(0, 6))
    left.axis("off")
    left.set_title("A · encode each side before pairwise comparison")
    box(left, (.15, 4.35), 2.2, .8, "queries\nq₁, q₂", color="#e9f0fb")
    box(left, (3.0, 4.35), 2.15, .8, "query encoder\nE_q", color="#d3e4fa")
    box(left, (5.85, 4.35), 3.55, .8, "q₁=(1,0), q₂=(0,1)", color="#e9f0fb")
    box(left, (.15, 1.35), 2.2, .8, "passages\np₁, p₂", color="#ecf7f1")
    box(left, (3.0, 1.35), 2.15, .8, "passage encoder\nE_p", color="#cfeadb")
    box(left, (5.85, 1.35), 3.55, .8, "p₁=(3,0), p₂=(1,2)", color="#ecf7f1")
    for y in (4.75, 1.75):
        arrow(left, (2.38, y), (2.95, y))
        arrow(left, (5.18, y), (5.80, y))
    left.text(.2, .62, "Index time: encode passages once. Query time: encode q, then score.",
              fontsize=9, color="#243244")
    left.text(.2, .19, "Encoders may share weights; this toy specifies only their outputs.",
              fontsize=8, color="#475569")
    right.set(xlim=(-.65, 2.35), ylim=(-.75, 2.7))
    right.set_xticks((.5, 1.5), labels=("p₁", "p₂"))
    right.set_yticks((1.5, .5), labels=("q₁", "q₂"))
    right.xaxis.tick_top()
    right.set_title("B · dot scores, row softmax, diagonal positives", pad=22)
    colors = {True: "#d7ebdf", False: "#edf0f3"}
    for i in range(2):
        for j in range(2):
            right.add_patch(Rectangle((j, 1 - i), 1, 1,
                                      facecolor=colors[i == j], edgecolor="white",
                                      linewidth=3))
            right.text(j + .5, 1.5 - i, str(SCORES[i][j]),
                       ha="center", va="center", fontsize=19,
                       weight="bold" if i == j else "normal")
    right.text(-.58, -.13, f"P(positive | q₁) = {PROBABILITIES[0]:.3f}", fontsize=9)
    right.text(-.58, -.39, f"Mean in-batch loss = {LOSS:.3f} nats, temperature = 1",
               fontsize=9)
    right.text(-.58, -.67, "Off-diagonal items are assumed negatives; check for false negatives.",
               fontsize=8, color="#475569")
    right.spines[:].set_visible(False)
    svg = HERE / "figure-11-01-encoders-and-batch.svg"
    png = HERE / "figure-11-01-encoders-and-batch.png"
    fig.savefig(svg, metadata={"Date": None, "Creator": "Chapter 11 plot source"})
    fig.savefig(png, dpi=180, metadata={"Software": "Chapter 11 plot source"})
    plt.close(fig)
    svg.write_text("\n".join(line.rstrip() for line in
                             svg.read_text(encoding="utf-8").splitlines()) + "\n",
                   encoding="utf-8")
    print(f"Wrote {svg} and {png}")


if __name__ == "__main__":
    main()
