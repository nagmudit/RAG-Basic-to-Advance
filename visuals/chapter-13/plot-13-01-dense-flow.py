"""Figure 13.01. Fixed local index/query mechanism; no measured values."""

from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

HERE = Path(__file__).resolve().parent
fig, ax = plt.subplots(figsize=(14, 5.2), layout="constrained")
ax.set_xlim(0, 14)
ax.set_ylim(0, 5.2)
ax.axis("off")


def box(x, y, w, title, sub, fill):
    ax.add_patch(FancyBboxPatch((x, y), w, .72, boxstyle="round,pad=.04",
                                edgecolor="#263747", facecolor=fill, linewidth=1.2))
    ax.text(x + w / 2, y + .46, title, ha="center", va="center",
            fontsize=10, weight="bold", color="#152536")
    ax.text(x + w / 2, y + .18, sub, ha="center", va="center", fontsize=8.2,
            color="#243949")


def arrow(x1, y1, x2, y2, dashed=False):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>",
                                 mutation_scale=12, linewidth=1.4,
                                 linestyle="--" if dashed else "-", color="#42566a"))


ax.text(.2, 4.8, "INDEX TIME", fontsize=11, weight="bold", color="#17324d")
top = [(.2, "Source segments", "IDs + scopes", "#e2ebf2"),
       (2.95, "Text format", "title + body", "#e2ebf2"),
       (5.7, "Pinned encoder", "batched", "#dcefdc"),
       (8.45, "L2 normalize", "384 floats / row", "#dcefdc"),
       (11.2, "Snapshot", "binary + manifest", "#e2ebf2")]
for x, title, sub, fill in top:
    box(x, 3.72, 2.55, title, sub, fill)
for x in (2.75, 5.50, 8.25, 11.0):
    arrow(x, 4.08, x + .18, 4.08)

ax.text(.2, 2.8, "QUERY TIME", fontsize=11, weight="bold", color="#17324d")
bottom = [(.2, "Question", "one input", "#e2ebf2"),
          (2.17, "Same encoder", "compatible query", "#dcefdc"),
          (4.14, "Verified index", "startup load", "#ffe6af"),
          (6.11, "Eligibility", "D10 excluded", "#ffe6af"),
          (8.08, "Exact cosine", "12 eligible rows", "#dcefdc"),
          (10.05, "Candidates", "score + top-k", "#e2ebf2"),
          (12.02, "Context", "selected spans", "#e2ebf2")]
for x, title, sub, fill in bottom:
    box(x, 1.72, 1.75, title, sub, fill)
for x in (1.95, 3.92, 5.89, 7.86, 9.83, 11.8):
    arrow(x, 2.08, x + .19, 2.08)
arrow(12.47, 3.65, 5.05, 2.54, dashed=True)
ax.text(10.4, 2.95, "validated at startup", fontsize=8.5, color="#42566a")
ax.text(.2, .55, "Solid arrows: data/execution     Dashed arrow: startup validation",
        fontsize=9.5, color="#42566a")
ax.text(.2, .2, "Scope is a local fixture; a real service derives permissions from trusted identity.",
        fontsize=9, color="#42566a")
ax.set_title("A durable dense index must match the query encoder and source snapshot",
             fontsize=14, pad=12)
for ext in ("svg", "png"):
    fig.savefig(HERE / f"figure-13-01-dense-flow.{ext}", dpi=180)
svg = HERE / "figure-13-01-dense-flow.svg"
svg.write_text("\n".join(line.rstrip() for line in svg.read_text(encoding="utf-8").splitlines()) + "\n",
               encoding="utf-8")
plt.close(fig)
