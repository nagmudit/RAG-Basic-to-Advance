"""Editable taxonomy and logical page/cache diagrams; no measured SSD claim."""
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch,Rectangle,Ellipse

HERE=Path(__file__).resolve().parent
plt.rcParams.update({"font.size":13,"svg.fonttype":"none"})


def save(fig,slug):
    fig.savefig(HERE/f"{slug}.png",dpi=160,bbox_inches="tight")
    p=HERE/f"{slug}.svg"
    fig.savefig(p,bbox_inches="tight")
    p.write_text("\n".join(s.rstrip() for s in p.read_text(encoding="utf-8").splitlines())+"\n",encoding="utf-8")
    plt.close(fig)


fig,ax=plt.subplots(figsize=(9,6))
ax.set(xlim=(0,10),ylim=(0,7))
layers=[(5.6,"SERVICE","Identity, routing, write visibility, recovery, monitoring"),
        (4.2,"ENGINE","Fields, predicates, lexical/vector plans, query execution"),
        (2.8,"LIBRARY","Native operations and index data structures in a process"),
        (1.4,"ALGORITHM","Scan, IVF/PQ, HNSW, Vamana: rules for finding candidates")]
for y,title,body in layers:
    ax.add_patch(Rectangle((.6,y),8.8,.95,facecolor="#edf3f8",edgecolor="#005a83"))
    ax.text(.9,y+.67,title,weight="bold")
    ax.text(.9,y+.25,body,fontsize=13)
for upper,lower,label in ((5.6,5.15,"delegates query execution"),(4.2,3.75,"may call native library"),(2.8,2.35,"implements the mechanism")):
    ax.annotate("",(5,lower),(5,upper),arrowprops={"arrowstyle":"->","color":"black"})
    ax.text(5.3,(upper+lower)/2,label,va="center",fontsize=13)
ax.text(.65,.55,"An algorithm cannot provide the service contracts above it.",weight="bold")
ax.axis("off")
ax.set_title("Figure 18.02 — Four responsibilities behind one search endpoint",weight="bold",fontsize=15)
fig.tight_layout()
save(fig,"figure-18-02-responsibilities")

data=json.loads((HERE.parents[1]/"projects/V4/chapter-18-experiment.json").read_text())['logical_storage']
fig,axes=plt.subplots(1,2,figsize=(10,5))
ax=axes[0]
ax.set(xlim=(0,5),ylim=(0,6))
for x,y,label in ((.3,4.6,"RAM: codes + hot-node cache"),(.3,1.0,"SSD: vectors + adjacency pages")):
    ax.add_patch(Rectangle((x,y),4.4,.8,facecolor="#edf3f8",edgecolor="#005a83"))
    ax.add_patch(Ellipse((x+2.2,y+.8),4.4,.3,facecolor="white",edgecolor="#005a83"))
    ax.text(x+2.2,y+.35,label,ha="center",fontsize=13)
ax.add_patch(Rectangle((.7,2.9),3.6,.85,facecolor="white",edgecolor="black"))
ax.text(2.5,3.32,"Select beam;\ncoalesce misses",ha="center",va="center",fontsize=13)
ax.annotate("",(2.5,3.8),(2.5,4.4),arrowprops={"arrowstyle":"->"})
ax.annotate("",(2.5,1.9),(2.5,2.85),arrowprops={"arrowstyle":"->"})
ax.text(2.65,2.35,"read missing pages",fontsize=13)
ax.annotate("",(.45,4.4),(.45,2.),arrowprops={"arrowstyle":"->","linestyle":"--"})
ax.text(.13,3.2,"update frontier",fontsize=13,rotation=90,ha="center",va="center",bbox={"facecolor":"white","edgecolor":"none"})
ax.text(.3,.35,"Conceptual disk graph path;\nDiskANN is not implemented here.",fontsize=13)
ax.set_title("QUERY TIME: separate RAM and SSD roles",fontsize=13)
ax.axis("off")
ax=axes[1]
ax.set(xlim=(0,5),ylim=(0,6))
ax.text(.1,5.4,"A,B → page 0; C → page 1; D → page 2",fontsize=13)
for number,case in enumerate(data['cases']):
    y=4.0-number*2
    ax.add_patch(FancyBboxPatch((.1,y-.6),4.6,1.5,boxstyle="round,pad=.12",facecolor="#f2f2f2",edgecolor="black"))
    ax.text(.3,y+.5,"Beam: "+", ".join(case['beam']),fontsize=13,weight="bold")
    ax.text(.3,y+.05,f"Cache {case['cache_before']} → {case['cache_after']}",fontsize=13)
    ax.text(.3,y-.4,f"Page requests: {case['requested_pages']}",fontsize=13)
ax.text(.1,.5,"Capacity: 2 pages; cache order: oldest → newest",fontsize=13)
ax.axis("off")
ax.set_title("Actual logical cache decisions",fontsize=13)
fig.suptitle("Figure 18.01 — A beam can share pages and reuse cached records",weight="bold",fontsize=15)
fig.text(.5,.015,"ch18-logical-page-cache-v1 · logical requests, not SSD latency or OS cache measurements",ha="center",fontsize=13)
fig.tight_layout(rect=(0,.05,1,.93))
save(fig,"figure-18-01-pages-and-cache")
