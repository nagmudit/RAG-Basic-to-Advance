"""Plot one fixed two-dimensional exact, KD and LSH teaching trace."""

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "projects" / "V4"))
from ann_ch15 import KDTree, HyperplaneLSH, exact_cosine  # noqa: E402
from experiment_ch15 import synthetic_rows  # noqa: E402

SEED = 1
rows, queries = synthetic_rows(12, 2, SEED)
q = queries[0]
exact, _ = exact_cosine(rows, q, scope="benchmark", k=2)
kd = KDTree(rows, leaf_size=2)
lsh = HyperplaneLSH(rows, tables=2, bits=4, seed=SEED,
                    source_version="figure-15-01-fixed-toy")
approx, _ = lsh.search(q, scope="benchmark", k=2)
oracle_ids = {item_id for item_id, _ in exact}
bucket_ids = set()
for table, planes in zip(lsh.buckets, lsh.planes):
    bucket_ids.update(table.get(lsh._signature(q, planes), []))

fig, axes = plt.subplots(1, 3, figsize=(12.4, 4.5), sharex=True, sharey=True,
                         constrained_layout=True)


def draw_tree(node, ax, box, depth=0):
    if node.indices is not None:
        return
    xmin, xmax, ymin, ymax = box
    if node.axis == 0:
        ax.plot([node.pivot, node.pivot], [ymin, ymax], color="#355c7d",
                linewidth=1.8/(1+.18*depth), alpha=.8)
        draw_tree(node.left, ax, (xmin, node.pivot, ymin, ymax), depth+1)
        draw_tree(node.right, ax, (node.pivot, xmax, ymin, ymax), depth+1)
    else:
        ax.plot([xmin, xmax], [node.pivot, node.pivot], color="#355c7d",
                linewidth=1.8/(1+.18*depth), alpha=.8)
        draw_tree(node.left, ax, (xmin, xmax, ymin, node.pivot), depth+1)
        draw_tree(node.right, ax, (xmin, xmax, node.pivot, ymax), depth+1)


for ax, title in zip(axes, ("Exact scan: all 12 scored", "KD tree: bounded regions", "LSH: matching buckets only")):
    ax.set_title(title, fontsize=10.5)
    ax.axhline(0, color="#dddddd", linewidth=.6)
    ax.axvline(0, color="#dddddd", linewidth=.6)
    ax.set_xlim(-1.25, 1.25)
    ax.set_ylim(-1.25, 1.25)
    ax.set_aspect("equal")
    ax.set_xlabel("Unit-vector coordinate x")
axes[0].set_ylabel("Unit-vector coordinate y")
draw_tree(kd.root, axes[1], (-1.25, 1.25, -1.25, 1.25))

# Show the first hyperplane as one orientation cue; the bucket signature uses
# four planes per table, not only the drawn boundary.
plane = lsh.planes[0][0]
if abs(plane[1]) > 1e-8:
    xx = [-1.25, 1.25]
    axes[2].plot(xx, [-plane[0]*x/plane[1] for x in xx],
                 linestyle="--", color="#7353a6", linewidth=1, label="one of eight planes")

for ax in axes:
    for row in rows:
        x, y = row["vector"]
        item_id = row["item_id"]
        candidate = item_id in bucket_ids
        color = "#db7c22" if ax is axes[2] and candidate else "#7b8490"
        ax.scatter(x, y, s=42, color=color, zorder=3)
        if item_id in oracle_ids:
            ax.scatter(x, y, s=116, facecolors="none", edgecolors="#176b45",
                       linewidths=2, zorder=4)
        if item_id in oracle_ids:
            ax.annotate(item_id[-2:], (x, y), xytext=(5, 5),
                        textcoords="offset points", fontsize=9, fontweight="bold")
    ax.scatter(*q, marker="*", s=200, color="#a72e47", edgecolors="black", zorder=5)

axes[2].legend(loc="lower left", fontsize=8, framealpha=.9)
fig.suptitle("One fixed query: green rings are exact top-2; orange points enter the LSH candidate union", fontsize=12)
for extension in ("svg", "png"):
    path = HERE / f"figure-15-01-partitions-and-buckets.{extension}"
    fig.savefig(path, dpi=180, facecolor="white")
    if extension == "svg":
        path.write_text("\n".join(line.rstrip() for line in path.read_text(encoding="utf-8").splitlines()) + "\n", encoding="utf-8")
plt.close(fig)
