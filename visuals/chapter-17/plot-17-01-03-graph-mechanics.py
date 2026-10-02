"""Exact fixture/algorithm-derived diagrams, not an ANN performance illustration."""
import json
import sys
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]/"projects/V4"))
from hnsw_ch17 import HNSW, search_layer, squared_l2, select_neighbors
plt.rcParams.update({"font.size": 11, "svg.fonttype": "none"})


def save(fig, slug):
    fig.savefig(HERE/f"{slug}.png", dpi=160, bbox_inches="tight")
    path = HERE/f"{slug}.svg"
    fig.savefig(path, bbox_inches="tight")
    path.write_text("\n".join(line.rstrip() for line in path.read_text(encoding="utf-8").splitlines())+"\n", encoding="utf-8")
    plt.close(fig)


fixture = json.loads((HERE.parents[1]/"projects/V4/graph_fixture_ch17.json").read_text())
fig, axes = plt.subplots(2, 1, figsize=(9, 5.2))
for ax, ef in zip(axes, (1, 2)):
    ranking, detail = search_layer(fixture["query"], fixture["vectors"], fixture["adjacency"], ["A"], ef, capture="full")
    for i, name in enumerate("ABCD"):
        ax.scatter(i, 0, s=900, facecolors="white", edgecolors="black", zorder=3)
        ax.text(i, 0, name, ha="center", va="center", zorder=4, weight="bold")
        ax.text(i, -.28, f"x={fixture['vectors'][name][0]:g}; d²={squared_l2(fixture['query'], fixture['vectors'][name]):g}", ha="center")
        if i < 3:
            ax.plot([i, i+1], [0, 0], color="gray", zorder=1)
    scored = detail["scored_ids"]
    ax.text(-.05, .47, f"ef={ef}: scored {', '.join(scored)}; returned {ranking[0][0]}", weight="bold")
    expansions = [e["current_id"] for e in detail["events"] if e["action"] == "expand"]
    ax.text(-.05, .26, "Expansion order: "+" → ".join(expansions), color="#005a83")
    if ef == 1:
        ax.text(2.65, .25, "D not discovered", ha="center", color="#9c300c")
    ax.set(xlim=(-.35, 3.5), ylim=(-.55, .65))
    ax.axis("off")
fig.suptitle("Figure 17.01 — A frontier can cross a greedy local minimum", weight="bold")
fig.text(.5, .015, "ch17-frontier-fixture-v1 · q=0 · diagram spacing is topology, not vector distance", ha="center", fontsize=11)
fig.tight_layout(rect=(0,.04,1,.94))
save(fig, "figure-17-01-frontier")

graph = HNSW(scope="demo", M=2, ef_construction=12, seed=17022026)
points = {"A": (0., 0.), "B": (1., 0.), "C": (2., 0.), "D": (3., 0.),
          "E": (4., 1.), "F": (5., 0.), "G": (6., 0.), "H": (7., 0.)}
levels = {"A": 2, "C": 1, "F": 1}
for name, point in points.items():
    graph.add({"item_id": name, "vector": point, "allowed_scopes": ["demo"]}, level=levels.get(name, 0))
ranked, work = graph.search((6.7,.2), scope="demo", k=2, ef_search=4, capture="full")
(HERE/"hierarchy-example.json").write_text(json.dumps({"points": points, "levels": graph.levels,
    "layers": graph.layers, "query": [6.7,.2], "result": ranked, "trace": work["graph_trace"]}, indent=2)+"\n")
fig, ax = plt.subplots(figsize=(10, 5))
for layer in range(3):
    y = layer*1.5
    for name, links in graph.layers[layer].items():
        x = ord(name)-65
        for target in links:
            ax.annotate("", (ord(target)-65, y), (x, y), arrowprops={"arrowstyle": "->", "color": "#aaa", "lw": 1.1, "connectionstyle": "arc3,rad=.13"})
        ax.scatter(x, y, s=380, facecolors="white", edgecolors="black", zorder=3)
        ax.text(x,y,name,ha="center",va="center",zorder=4)
    detail = next(t for t in work["graph_trace"] if t["layer"] == layer)
    expands = [e["current_id"] for e in detail["events"] if e["action"] == "expand"]
    ax.text(.7,y+.55,f"Layer {layer}: enter {detail['entry_id']}; expand "+" → ".join(expands), color="#005a83", ha="left",
            bbox={"facecolor": "white", "edgecolor": "none", "pad": 2}, zorder=6)
    if layer:
        destination = work["candidate_stages"][f"layer_{layer}_retained"][0][0]
        x = ord(destination)-65
        ax.annotate("",(x,y-1.08),(x,y-.24),arrowprops={"arrowstyle":"->","color":"#9c300c","lw":2})
ax.set(xlim=(-.9,7.9), ylim=(-.7,4.05))
ax.axis("off")
ax.set_title("Figure 17.02 — Same vertices, nested layers, carried entry point", weight="bold")
fig.text(.5,.015,"Forced levels for traceability · q=(6.7,.2), M=2, efConstruction=12, efSearch=4\nGray arrows: actual outgoing links; dark vertical arrows: query descent; layout is schematic",ha="center",fontsize=10)
fig.tight_layout(rect=(0,.07,1,1))
save(fig,"figure-17-02-hierarchy")

vs={"P":(1.,0.),"Q":(1.2,.1),"R":(0.,2.)}
assert select_neighbors((0.,0.),vs,vs,2)==["P","R"]
fig, ax=plt.subplots(figsize=(6.5,5))
ax.scatter([0],[0],marker="*",s=240,color="black")
ax.annotate("new vertex x",(0,0),xytext=(-.05,-.3))
for name,(x,y) in vs.items():
    ax.scatter([x],[y],s=180,facecolors="white",edgecolors="black",zorder=3)
    ax.annotate(name,(x,y),xytext=(x+.1,y+.12))
    ax.plot([0,x],[0,y],ls="--" if name=="Q" else "-",lw=2,
            color="#9c300c" if name=="Q" else "#005a83")
ax.text(.25,1.7,"R accepted: d²(R,P)=5 ≥ d²(R,x)=4",fontsize=10)
ax.text(.1,.8,"Q rejected: d²(Q,P)=.05 < d²(Q,x)=1.45",fontsize=10)
ax.set(xlim=(-.4,2.8),ylim=(-.5,2.5),xlabel="coordinate 1",ylabel="coordinate 2")
ax.set_aspect("equal")
ax.grid(alpha=.2)
ax.set_title("Figure 17.03 — Select directions, not only closest points",fontsize=12,weight="bold")
fig.tight_layout()
save(fig,"figure-17-03-diversity")
