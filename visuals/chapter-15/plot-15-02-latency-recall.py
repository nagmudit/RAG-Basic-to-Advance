"""Plot measured Chapter 15 synthetic timing and exact-neighbor recall."""

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import NullLocator

HERE = Path(__file__).resolve().parent
record = json.loads((HERE.parents[1] / "projects" / "V4" /
                     "chapter-15-experiment.json").read_text(encoding="utf-8"))
fig, axes = plt.subplots(1, 2, figsize=(10.8, 4.25), constrained_layout=True)
colors = {"exact": "#294d6b", "kd": "#1f7a55", "lsh": "#bb682c"}
for dimension, marker in ((2, "o"), (32, "s")):
    rows = sorted((item for item in record["synthetic"] if item["dimension"] == dimension),
                  key=lambda item: item["n"])
    for method in ("exact", "kd", "lsh"):
        axes[0].plot([item["n"] for item in rows],
                     [item["timings"][method]["p50_nearest_rank"] for item in rows],
                     marker=marker, color=colors[method],
                     linestyle="-" if dimension == 2 else "--",
                     label=f"{method}, d={dimension}")
    axes[1].plot([item["n"] for item in rows],
                 [item["quality"]["lsh_mean_exact_neighbor_recall_at_2"] for item in rows],
                 marker=marker, color="#bb682c",
                 linestyle="-" if dimension == 2 else "--", label=f"LSH d={dimension}")
axes[0].set(xlabel="Corpus vectors N", ylabel="Search-only p50 (ms)",
            title="Local Python search time", xscale="log", yscale="log")
axes[0].legend(fontsize=8, ncol=2)
axes[1].axhline(1, color="#1f7a55", linestyle=":", label="exact/KD oracle")
axes[1].set(xlabel="Corpus vectors N", ylabel="Mean exact-neighbor Recall@2",
            title="LSH approximation loss", xscale="log", ylim=(0, 1.05))
axes[1].legend(fontsize=8)
for ax in axes:
    ax.set_xticks([128, 512, 2048], ["128", "512", "2048"])
    ax.xaxis.set_minor_locator(NullLocator())
    ax.set_xlim(105, 2500)
    ax.grid(alpha=.25)
fig.suptitle("Fixed LSH: 4 tables × 6 bits; 20 queries per N and dimension", fontsize=12)
for extension in ("svg", "png"):
    path = HERE / f"figure-15-02-latency-recall.{extension}"
    fig.savefig(path, dpi=180, facecolor="white")
    if extension == "svg":
        path.write_text("\n".join(line.rstrip() for line in path.read_text(encoding="utf-8").splitlines()) + "\n", encoding="utf-8")
plt.close(fig)
