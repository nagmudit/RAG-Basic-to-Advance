"""Render the fixed Chapter 14 MaxSim grid from the checked experiment record."""

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).resolve().parent
record = json.loads((HERE.parents[1] / "projects" / "V3" /
                     "chapter-14-experiment.json").read_text(encoding="utf-8"))
fig, axes = plt.subplots(1, 2, figsize=(10.2, 3.8), constrained_layout=True,
                         gridspec_kw={"width_ratios": [2.5, 1]})
for ax, item_id, title in zip(axes, ("A_both_with_noise", "B_generic"),
                              ("A: two matches plus distractors", "B: one generic token")):
    item = record["token"][item_id]
    grid = np.array(item["grid"])
    ax.imshow(grid, cmap="BrBG", vmin=-1, vmax=1, aspect="auto")
    ax.set_xticks(range(grid.shape[1]), [f"d{j}" for j in range(grid.shape[1])])
    ax.set_yticks(range(2), ["q0", "q1"])
    ax.set_xlabel("Document token position")
    ax.set_ylabel("Query token position")
    ax.set_title(f"{title}\nMaxSim = {item['maxsim']:.3f}", fontsize=11)
    for i in range(grid.shape[0]):
        for j in range(grid.shape[1]):
            chosen = j == item["winner_indices"][i]
            ax.text(j, i, f"{grid[i,j]:+.3f}", ha="center", va="center",
                    fontsize=10, color="black", fontweight="bold" if chosen else "normal",
                    bbox={"boxstyle": "round,pad=.15", "facecolor": "white",
                          "edgecolor": "black" if chosen else "none", "alpha": .9})
    ax.set_xticks(np.arange(-.5, grid.shape[1], 1), minor=True)
    ax.set_yticks(np.arange(-.5, 2, 1), minor=True)
    ax.grid(which="minor", color="#333333", linewidth=.6)
    ax.tick_params(which="minor", bottom=False, left=False)
fig.suptitle("Each query token chooses its best document token; winners are boxed", fontsize=12)
for extension in ("svg", "png"):
    path = HERE / f"figure-14-01-maxsim-grid.{extension}"
    fig.savefig(path, dpi=180, facecolor="white")
    if extension == "svg":
        path.write_text("\n".join(line.rstrip() for line in path.read_text(encoding="utf-8").splitlines()) + "\n", encoding="utf-8")
plt.close(fig)
