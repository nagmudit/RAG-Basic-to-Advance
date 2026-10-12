"""Plots only the checked record. No substitution of historical/native timings."""
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE=Path(__file__).resolve().parent
data=json.loads((HERE.parents[1]/"projects/V4/chapter-18-experiment.json").read_text())
plt.rcParams.update({"font.size":13,"svg.fonttype":"none"})


def save(fig,slug):
    fig.savefig(HERE/f"{slug}.png",dpi=160,bbox_inches="tight")
    p=HERE/f"{slug}.svg"
    fig.savefig(p,bbox_inches="tight")
    p.write_text("\n".join(s.rstrip() for s in p.read_text(encoding="utf-8").splitlines())+"\n",encoding="utf-8")
    plt.close(fig)


w=data['synthetic']
fig,axes=plt.subplots(1,2,figsize=(10,4.8))
ax=axes[0]
names=[f'hnsw_e{ef}_r8' for ef in (8,32,64)]
vals=[w['summaries'][n] for n in names]
ax.plot([v['native_kernel_timing']['p95_nearest_rank'] for v in vals],
        [v['mean_exact_neighbor_recall_at_2'] for v in vals],marker='o',color='#005a83',label='HNSW M=8')
for ef,v in zip((8,32,64),vals):
    ax.annotate(f'ef={ef}',(v['native_kernel_timing']['p95_nearest_rank'],v['mean_exact_neighbor_recall_at_2']),xytext=(-8,-18) if ef==64 else (5,-18),ha='right' if ef==64 else 'left',textcoords='offset points',fontsize=13)
flat=w['summaries']['flat_r8']
ax.scatter([flat['native_kernel_timing']['p95_nearest_rank']],[1.],marker='s',s=70,color='#9c300c',label='Flat')
ax.set(xlabel='Native kernel p95 (ms)',ylabel='Exact-neighbor Recall@2',ylim=(.7,1.08))
ax.grid(alpha=.2)
ax.legend(fontsize=13,loc='lower right')
ax=axes[1]
b=w['builds']
ax.bar(['Flat','HNSW'],[b[n]['serialized_native_bytes']/1024 for n in ('flat','hnsw')],color='#005a83',label='Native file')
ax.bar(['Flat','HNSW'],[b[n]['id_manifest_bytes']/1024 for n in ('flat','hnsw')],
    bottom=[b[n]['serialized_native_bytes']/1024 for n in ('flat','hnsw')],color='#9c300c',label='ID/metadata manifest')
ax.set(ylabel='Measured serialized bytes (KiB)')
ax.grid(axis='y',alpha=.2)
ax.legend(fontsize=13,loc='lower left')
fig.suptitle('Figure 18.04 — Compare native quality, latency and actual files',fontsize=15,weight='bold')
fig.text(.5,.02,'ch16-synthetic-n1024-d32-v1 · 16 queries · 80 timed calls/mode\nFaiss 1.13.2, one thread, depth 8; one seed/order, no CI. Kernel excludes adapter. Files are not RSS.',ha='center',fontsize=13)
fig.tight_layout(rect=(0,.13,1,.93))
save(fig,'figure-18-04-native-quality-size')

fig,axes=plt.subplots(1,2,figsize=(10,5))
names=['prefilter_flat','post_flat_r8','post_flat_r32','post_hnsw_e32_r8','post_hnsw_e64_r32']
labels=['pre\nFlat','post\nFlat\nR8','post\nFlat\nR32','post\nHNSW\nR8','post\nHNSW\nR32']
for ax,w in zip(axes,data['public_tag_filters']):
    ax.bar(labels,[w['summaries'][n]['mean_filtered_exact_neighbor_recall_at_2'] for n in names],
           color=['#005a83','#999','#999','#9c300c','#9c300c'])
    ax.set(ylim=(0,1.08),ylabel='Eligible exact-neighbor Recall@2')
    ax.set_title(w['workload_id']+f"\n{w['predicate_eligible_count']} predicate-eligible / 1024 authorized",fontsize=13)
    ax.grid(axis='y',alpha=.2)
fig.suptitle('Figure 18.03 — A complete unfiltered search can lose filtered neighbors',fontsize=15,weight='bold')
fig.text(.5,.02,'Each panel: separate eligible oracle, 16 frozen queries, zero human judgments\nAll vectors already authorized. Public tags are not ACLs. HNSW: ef32/R8 and ef64/R32.',ha='center',fontsize=13)
fig.tight_layout(rect=(0,.12,1,.91))
save(fig,'figure-18-03-filtered-recall')
