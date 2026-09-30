"""Figure 12.01. Fixed illustrative scores; no sampled observations."""

from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).resolve().parent
scores = np.array([[.80, .60, .20], [.22, .83, .42]])
labels = np.array([["POSITIVE", "REVIEW", "NEGATIVE"],
                   ["NEGATIVE", "POSITIVE", "NEGATIVE"]])
colors = {"POSITIVE": "#d5eddd", "REVIEW": "#ffe6af", "NEGATIVE": "#dce9f4"}
fig, ax = plt.subplots(figsize=(8.0, 3.3), layout="constrained")
for row in range(2):
    for col in range(3):
        ax.add_patch(plt.Rectangle((col-.48, row-.43), .96, .86,
                                   facecolor=colors[labels[row, col]], edgecolor="#334155"))
        ax.text(col, row-.08, f"{scores[row,col]:.2f}", ha="center", va="center",
                fontsize=16, weight="bold", color="#17212b")
        ax.text(col, row+.23, labels[row,col], ha="center", va="center", fontsize=8,
                color="#17212b")
ax.set_xlim(-.55, 2.55)
ax.set_ylim(1.48, -.48)
ax.set_xticks(range(3), ["Passage A", "Passage B", "Passage C"])
ax.set_yticks(range(2), ["Query A", "Query B"])
ax.tick_params(length=0)
for spine in ax.spines.values():
    spine.set_visible(False)
ax.set_title("Cosine score alone does not determine a negative label", fontsize=12)
ax.set_xlabel("Passage candidate; score is unitless cosine")
for ext in ("svg", "png"):
    fig.savefig(HERE / f"figure-12-01-training-matrix.{ext}", dpi=180)
svg = HERE / "figure-12-01-training-matrix.svg"
svg.write_text("\n".join(line.rstrip() for line in svg.read_text(encoding="utf-8").splitlines()) + "\n",
               encoding="utf-8")
plt.close(fig)
