"""Figure 12.02. Fixed V0 document IDs and label paths; no sampled data."""

from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

HERE = Path(__file__).resolve().parent
fig, ax = plt.subplots(figsize=(10, 4.2), layout="constrained")
ax.set_xlim(0, 10)
ax.set_ylim(0, 4.2)
ax.axis("off")

def box(x, y, w, h, title, body, fill):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=.08",
                                facecolor=fill, edgecolor="#334155", linewidth=1.2))
    ax.text(x+w/2, y+h*.66, title, ha="center", va="center", weight="bold", fontsize=11)
    ax.text(x+w/2, y+h*.30, body, ha="center", va="center", fontsize=10)

box(.25, 2.65, 2.8, 1.0, "Train labels", "D1, D2, D4, D6", "#d5eddd")
box(3.6, 2.65, 2.8, 1.0, "Validation labels", "D3, D7", "#ffe6af")
box(6.95, 2.65, 2.8, 1.0, "Test labels", "D5, D8, D9", "#dce9f4")
box(.25, .55, 2.8, .95, "Gradient updates", "train pairs only", "#d5eddd")
box(3.6, .55, 2.8, .95, "Checkpoint choice", "validation only", "#ffe6af")
box(6.95, .55, 2.8, .95, "Final evaluation", "test once", "#dce9f4")
for x in (1.65, 5.0, 8.35):
    ax.add_patch(FancyArrowPatch((x, 2.56), (x, 1.55), arrowstyle="-|>",
                                 mutation_scale=17, color="#334155", linewidth=1.5))
ax.text(5, .05, "Shared eligible search index: D1–D9; legal-only D10 excluded before scoring",
        ha="center", va="center", fontsize=10, color="#17324d")
ax.set_title("Source documents are disjoint across label splits", fontsize=13)
for ext in ("svg", "png"):
    fig.savefig(HERE / f"figure-12-02-document-split.{ext}", dpi=180)
svg = HERE / "figure-12-02-document-split.svg"
svg.write_text("\n".join(line.rstrip() for line in svg.read_text(encoding="utf-8").splitlines()) + "\n",
               encoding="utf-8")
plt.close(fig)
