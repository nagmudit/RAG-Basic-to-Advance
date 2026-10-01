"""Figure 16.01: computed 2D IVF cells plus a hand-worked residual PQ code."""

from pathlib import Path
import math
import sys

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "projects" / "V4"))
from ann_ch15 import exact_cosine, unit  # noqa: E402
from ivf_pq_ch16 import IVFPQ  # noqa: E402

HERE = Path(__file__).resolve().parent
angles = (15, 30, 60, 75, 105, 120, 150, 165, 195, 210, 240, 255, 285, 300, 330, 345)
rows = [{"item_id": f"{i:02d}",
         "vector": (math.cos(math.radians(a)), math.sin(math.radians(a))),
         "allowed_scopes": ["demo"]} for i, a in enumerate(angles)]
index = IVFPQ(rows, nlist=4, subspaces=2, bits=1, seed=16)
chosen = None
for angle in range(360):
    q = unit((math.cos(math.radians(angle)), math.sin(math.radians(angle))))
    exact, _ = exact_cosine(rows, q, scope="demo", k=2)
    one, work1 = index.search(q, scope="demo", k=2, nprobe=1)
    two, _ = index.search(q, scope="demo", k=2, nprobe=2)
    if len(set(i for i, _ in one) & set(i for i, _ in exact)) == 1 and \
            [i for i, _ in two] == [i for i, _ in exact]:
        chosen = (angle, q, exact, one, work1)
        break
if chosen is None:
    raise AssertionError("Expected one-list miss and two-list recovery")
angle, q, exact, one, work1 = chosen

fig, (ax, bx) = plt.subplots(1, 2, figsize=(13, 5.2),
                              gridspec_kw={"width_ratios": [1.06, 1]})
fig.suptitle("IVF can omit a cell; PQ can perturb order inside a cell", fontsize=16)
palette = ("#267b9a", "#cf6f32", "#7456a4", "#409263")
gx, gy = np.meshgrid(np.linspace(-1.15, 1.15, 240), np.linspace(-1.15, 1.15, 240))
assignment = np.array([index._assign(unit((x, y))) if x*x+y*y > .0001 else 0
                       for x, y in zip(gx.ravel(), gy.ravel())]).reshape(gx.shape)
from matplotlib.colors import ListedColormap
ax.contourf(gx, gy, assignment, levels=np.arange(5)-.5,
            cmap=ListedColormap(("#d8ebf0", "#f8e4d5", "#e8def2", "#dcefe4")), alpha=.8)
ax.contour(gx, gy, assignment, levels=[.5, 1.5, 2.5], colors="#8b929b", linewidths=.6)
for row in rows:
    i = index.rows[row["item_id"]]["list_id"]
    x, y = row["vector"]
    ax.scatter(x, y, color=palette[i], s=36, edgecolor="white", linewidth=.6, zorder=4)
    ax.annotate(row["item_id"], (x, y), xytext=(4, 3), textcoords="offset points", fontsize=8)
for i, (x, y) in enumerate(index.centroids):
    ax.scatter(x, y, marker="X", color=palette[i], s=150, edgecolor="black", linewidth=.6, zorder=5)
    ax.annotate(f"C{i}", (x, y), xytext=(-13, -18), textcoords="offset points", fontsize=9)
ax.scatter(*q, marker="*", s=230, color="#111820", zorder=7)
ax.annotate(f"q ({angle}°)", q, xytext=(8, -19), textcoords="offset points", fontsize=9)
for item_id, _ in exact:
    x, y = next(r["vector"] for r in rows if r["item_id"] == item_id)
    ax.scatter(x, y, s=210, facecolors="none", edgecolors="#214d32", linewidths=2.1, zorder=6)
ax.set(xlim=(-1.22, 1.22), ylim=(-1.22, 1.22), xlabel="Unit-vector coordinate 1",
       ylabel="Unit-vector coordinate 2", title="A. Probe a centroid, then its assigned list")
ax.set_aspect("equal")
ax.grid(alpha=.12)
ax.text(.02, -.18, f"Exact top-2: {exact[0][0]}, {exact[1][0]}  |  nprobe=1: "
        f"{one[0][0]}, {one[1][0]}  |  nprobe=2 restores both",
        transform=ax.transAxes, fontsize=9, color="#223b46")

bx.axis("off")
bx.set_title("B. Encode a residual as two short codewords")
lines = [
    ("Stored vector x", "(1.4, 1.7)"),
    ("Coarse centroid c", "(1.0, 0.0)"),
    ("Residual r = x − c", "(0.4, 1.7)"),
    ("Subspace 1 codebook", "[0.0, 0.5] → code 1"),
    ("Subspace 2 codebook", "[0.0, 2.0] → code 1"),
    ("Stored PQ code", "(1, 1), two 1-bit indices"),
    ("Reconstruction c + r̂", "(1.5, 2.0)"),
    ("Squared reconstruction error", "0.10")]
for idx, (label, value) in enumerate(lines):
    y = .91-idx*.105
    bx.add_patch(plt.Rectangle((.02, y-.038), .96, .086,
                               transform=bx.transAxes, facecolor="#edf2f5" if idx % 2 == 0 else "white",
                               edgecolor="none"))
    bx.text(.04, y, label, transform=bx.transAxes, va="center", fontsize=10, color="#263941")
    bx.text(.98, y, value, transform=bx.transAxes, ha="right", va="center", fontsize=10,
            color="#174f75" if idx in (5, 6, 7) else "#263941")
bx.text(.03, -.08, "The right-hand arithmetic is an unnormalized L2 toy; V4 trains\n"
        "codebooks on residuals of normalized passage vectors.", transform=bx.transAxes, fontsize=9)
fig.tight_layout(rect=(0, .045, 1, .94), w_pad=2.6)
fig.savefig(HERE / "figure-16-01-cells-and-codes.svg", bbox_inches="tight")
fig.savefig(HERE / "figure-16-01-cells-and-codes.png", dpi=170, bbox_inches="tight")
svg = HERE / "figure-16-01-cells-and-codes.svg"
svg.write_text("\n".join(line.rstrip() for line in svg.read_text(encoding="utf-8").splitlines()) + "\n",
               encoding="utf-8")
print(f"angle={angle}; exact={[i for i,_ in exact]}; probe1={[i for i,_ in one]}; list={work1['probed_lists']}")
