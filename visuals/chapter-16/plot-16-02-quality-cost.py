"""Figure 16.02 from the checked Chapter 16 1024-by-32 synthetic workload."""

from pathlib import Path
import json

import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
record = json.loads((HERE.parents[1] / "projects" / "V4" /
                     "chapter-16-experiment.json").read_text(encoding="utf-8"))
case = next(x for x in record["synthetic"] if x["n"] == 1024 and x["dimension"] == 32)
probes = case["nprobe_grid"]
colors = {"flat": "#215a77", "adc": "#c16c2f", "refine": "#41815e"}
labels = {"flat": "IVF-Flat", "adc": "IVF-PQ ADC", "refine": "IVF-PQ + exact top-8"}
fig, axes = plt.subplots(1, 3, figsize=(14, 4.6), gridspec_kw={"width_ratios": [1.15, 1.15, .86]})
fig.suptitle("Coarse probing and compression spend different quality budgets", fontsize=16)
ax, bx, cx = axes
for mode in colors:
    recall = [case["summaries"][f"{mode}_p{p}"]["mean_exact_neighbor_recall_at_2"]
              for p in probes]
    latency = [case["summaries"][f"{mode}_p{p}"]["search_only_timing"]["p50_nearest_rank"]
               for p in probes]
    ax.plot(probes, recall, marker="o", color=colors[mode], label=labels[mode])
    bx.plot(probes, latency, marker="o", color=colors[mode], label=labels[mode])
coverage = [case["summaries"][f"flat_p{p}"]["mean_oracle_list_coverage_at_2"]
            for p in probes]
ax.plot(probes, coverage, color="#66727d", linestyle=":", marker="x",
        label="Oracle IDs in probed lists")
ax.set(xlabel="nprobe (of 16 lists)", ylabel="Mean exact-neighbor Recall@2",
       ylim=(-.03, 1.05), title="A. Geometry, 16 planted queries")
ax.set_xticks(probes)
ax.grid(alpha=.2)
ax.legend(loc="lower right", fontsize=8)
bx.axhline(case["summaries"]["exact"]["search_only_timing"]["p50_nearest_rank"],
           linestyle="--", color="#353f49", label="Exact full scan")
bx.set(xlabel="nprobe (of 16 lists)", ylabel="Warm search-only p50 (ms)",
       title="B. Python CPU time, 32 dimensions")
bx.set_xticks(probes)
bx.grid(alpha=.2)
bx.legend(loc="upper left", fontsize=8)
b = case["storage_lower_bounds"]
flat = b["raw_float32_vectors_bytes"]+b["ids_uint64_bytes"]+b["coarse_float32_bytes"]
pq = b["ids_uint64_bytes"]+b["coarse_float32_bytes"]+b["pq_code_packed_bytes"]+b["pq_codebook_float32_bytes"]
refine = pq+b["raw_float32_vectors_bytes"]
names = ["IVF-Flat", "PQ packed\nno originals", "PQ + raw\nfor refine"]
values = [flat, pq, refine]
bars = cx.bar(names, [v/1024 for v in values], color=[colors["flat"], colors["adc"], colors["refine"]])
for bar, v in zip(bars, values):
    cx.annotate(f"{v/1024:.1f} KiB", (bar.get_x()+bar.get_width()/2, bar.get_height()),
                xytext=(0, 3), textcoords="offset points", ha="center", fontsize=9)
cx.set(ylabel="Theoretical payload lower bound (KiB)", ylim=(0, max(values)/1024*1.14),
       title="C. Stored index payload")
cx.grid(axis="y", alpha=.2)
fig.text(.5, .015,
         "Fixed Gaussian-unit N=1024, d=32, seed 16013082; nlist=16, 8 subspaces × 2 bits; "
         "16 queries, 2 warm passes/query. Bytes exclude Python objects, list offsets and scopes.",
         ha="center", fontsize=8.5)
fig.tight_layout(rect=(0, .055, 1, .93), w_pad=2.0)
fig.savefig(HERE / "figure-16-02-quality-cost.svg", bbox_inches="tight")
fig.savefig(HERE / "figure-16-02-quality-cost.png", dpi=170, bbox_inches="tight")
svg = HERE / "figure-16-02-quality-cost.svg"
svg.write_text("\n".join(line.rstrip() for line in svg.read_text(encoding="utf-8").splitlines()) + "\n",
               encoding="utf-8")
