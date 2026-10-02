"""Measured plot from checked Chapter17 record; local timings, no CI."""
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE=Path(__file__).resolve().parent
data=json.loads((HERE.parents[1]/"projects/V4/chapter-17-experiment.json").read_text(encoding="utf-8"))
w=data["synthetic"][1]
plt.rcParams.update({"font.size":13,"svg.fonttype":"none"})
fig,axes=plt.subplots(2,2,figsize=(11,7.5))
colors={2:"#005a83",4:"#9c300c",8:"#5c3c91"}
for M in (2,4,8):
    names=[f"m{M}_c32_e{ef}" for ef in (2,8,24)]
    values=[w["summaries"][name] for name in names]
    for ax,key,label in ((axes[0,0],"mean_exact_neighbor_recall_at_2","Exact-neighbor Recall@2"),
                         (axes[0,1],"mean_scored_vectors","Distinct vectors scored/query")):
        ax.plot((2,8,24),[v[key] for v in values],marker="o",color=colors[M],label=f"M={M}")
        ax.set(xlabel="efSearch (retained neighbors)",ylabel=label)
    axes[1,0].plot((2,8,24),[v["search_only_timing"]["p95_nearest_rank"] for v in values],
                   marker="o",color=colors[M],label=f"M={M}")
axes[0,0].set(ylim=(0,1.05))
axes[1,0].set(xlabel="efSearch (retained neighbors)",ylabel="Search-only p95 (ms)")
axes[1,0].axhline(w["summaries"]["exact"]["search_only_timing"]["p95_nearest_rank"],color="black",ls="--",label="Exact scan")
names=[f"m{m}_c32" for m in (2,4,8)]
vectors=[w["graphs"][n]["payload_lower_bounds"]["vector_float32_bytes"]/1024 for n in names]
links=[w["graphs"][n]["payload_lower_bounds"]["adjacency_uint32_bytes"]/1024 for n in names]
levels=[w["graphs"][n]["payload_lower_bounds"]["level_uint32_bytes"]/1024 for n in names]
ax=axes[1,1]
ax.bar(["2","4","8"],vectors,label="Float32 vectors",color="#bbb")
ax.bar(["2","4","8"],links,bottom=vectors,label="32-bit adjacency",color="#005a83")
ax.bar(["2","4","8"],levels,bottom=[a+b for a,b in zip(vectors,links)],label="32-bit levels",color="#9c300c")
ax.set(xlabel="M (degree and level distribution change)",ylabel="Payload lower bound (KiB)")
for ax in axes.flat:
    ax.legend(fontsize=13)
    ax.grid(axis="y",alpha=.2)
fig.suptitle("Figure 17.04 — More exploration buys recall; graph edges consume memory",weight="bold")
fig.text(.5,.015,"ch16-synthetic-n1024-d32-v1 · 16 frozen queries\nGraph seed 17022026 · efConstruction=32 · 32 samples/mode · one process/seed, no CI\nTrace construction included; encode/context excluded. Payload bytes are not RSS.",ha="center",fontsize=13)
fig.tight_layout(rect=(0,.12,1,.94))
fig.savefig(HERE/"figure-17-04-quality-cost.png",dpi=160,bbox_inches="tight")
path=HERE/"figure-17-04-quality-cost.svg"
fig.savefig(path,bbox_inches="tight")
path.write_text("\n".join(line.rstrip() for line in path.read_text(encoding="utf-8").splitlines())+"\n",encoding="utf-8")
