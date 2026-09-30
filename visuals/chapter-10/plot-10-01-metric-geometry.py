"""Figure 10.01: explicit 2D vectors and three exact ranking orders.

The points are hand-authored unit/magnitude examples, not text embeddings.
No sampling, fitted model or statistical uncertainty is involved.
"""

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Arc

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "projects" / "V3"))
from exact_vectors import ExactIndex  # noqa: E402

POINTS = {"A": (1, 0), "B": (2, 0), "C": (.8, .6), "D": (0, 1)}
INDEX = ExactIndex([{"item_id": name, "vector": value,
                     "allowed_scopes": ["toy"]}
                    for name, value in POINTS.items()], version="ch10-figure-v1")


def main():
    plt.rcParams["svg.hashsalt"] = "rag-ch10-geometry"
    plt.rcParams["font.family"] = "DejaVu Sans"
    fig, (left, right) = plt.subplots(1, 2, figsize=(11.4, 5.1),
                                      gridspec_kw={"width_ratios": [1.35, 1]},
                                      layout="constrained")
    fig.suptitle("The metric changes the nearest neighbor of the same vectors", fontsize=13)
    left.arrow(0, 0, 1, 0, width=.014, length_includes_head=True,
               color="#111827", zorder=4)
    left.text(.44, -.17, "query q=(1,0)", fontsize=10)
    colors = {"A": "#2563a6", "B": "#a85521", "C": "#138064", "D": "#7754a5"}
    for name, (x, y) in POINTS.items():
        left.scatter(x, y, s=105, color=colors[name], zorder=5)
        left.text(x + .045, y + (.05 if name != "A" else .08),
                  f"{name}=({x:g},{y:g})", color=colors[name], fontsize=9)
    left.add_patch(Arc((0, 0), 1.3, 1.3, theta1=0, theta2=36.87,
                       linestyle="--", color="#697386", linewidth=1.2))
    left.text(.52, .26, "angle to C", fontsize=8, color="#4b5563")
    left.plot([1, .8], [0, .6], linestyle=":", color="#138064")
    left.text(1.03, .30, "L2(q,C)=0.632", fontsize=8, color="#138064")
    left.set(xlim=(-.15, 2.4), ylim=(-.3, 1.35), xlabel="coordinate 1 (feature units)",
             ylabel="coordinate 2 (feature units)",
             title="A · hand-authored coordinate plane")
    left.axhline(0, color="#aeb4bd", linewidth=.8)
    left.axvline(0, color="#aeb4bd", linewidth=.8)
    left.set_aspect("equal", adjustable="box")
    left.grid(alpha=.15)
    rows = []
    for metric in ("dot", "cosine", "l2"):
        ranked, _ = INDEX.search((1, 0), scope="toy", metric=metric,
                                 top_k=4, plan="sort")
        rows.append([metric, "  >  ".join(row["item_id"] for row in ranked),
                     "higher" if metric in ("dot", "cosine") else "lower"])
    right.axis("off")
    table = right.table(cellText=rows, colLabels=["Measure", "Exact order", "Best value"],
                        colWidths=[.20, .57, .23], bbox=[.01, .31, .98, .43])
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    for (row, col), cell in table.get_celld().items():
        cell.set_edgecolor("#c8ced8")
        if row == 0:
            cell.set_facecolor("#eaf0f6")
            cell.set_text_props(weight="bold")
    right.text(.03, .23, "Equal cosine values for A and B use ID order.", fontsize=9)
    right.text(.03, .15, "All four vectors are scored for every exact query.", fontsize=9)
    right.set_title("B · top-k order under a declared tie rule")
    svg = HERE / "figure-10-01-metric-geometry.svg"
    png = HERE / "figure-10-01-metric-geometry.png"
    fig.savefig(svg, metadata={"Date": None, "Creator": "Chapter 10 plot source"})
    fig.savefig(png, dpi=180, metadata={"Software": "Chapter 10 plot source"})
    plt.close(fig)
    svg.write_text("\n".join(line.rstrip() for line in
                             svg.read_text(encoding="utf-8").splitlines()) + "\n",
                   encoding="utf-8")
    print(f"Wrote {svg} and {png}")


if __name__ == "__main__":
    main()
