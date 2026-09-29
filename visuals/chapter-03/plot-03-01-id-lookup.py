"""Render Figure 3.01 from the checked-in Chapter 3 measurement record.

From the repository root:
    python visuals/chapter-03/plot-03-01-id-lookup.py

Requires matplotlib for rendering. The benchmark itself uses only the Python
standard library. This plot reports observed timings, not a universal speedup.
"""

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

matplotlib.rcParams["svg.hashsalt"] = "chapter-03-figure-01"


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DATA = ROOT / "projects" / "V0" / "chapter-03-measurements.json"


def main():
    report = json.loads(DATA.read_text(encoding="utf-8"))
    rows = report["results"]
    sizes = [row["records"] for row in rows]
    figure, axis = plt.subplots(figsize=(9, 5.5), layout="constrained")
    for label, center, samples, color, marker, line in (
        ("List scan", "scan_median_us_per_lookup", "scan_us_per_lookup_samples", "#1b5e87", "o", "-"),
        ("Dictionary by ID", "dict_median_us_per_lookup", "dict_us_per_lookup_samples", "#a34216", "s", "--"),
    ):
        medians = [row[center] for row in rows]
        low = [row[center] - min(row[samples]) for row in rows]
        high = [max(row[samples]) - row[center] for row in rows]
        axis.errorbar(
            sizes,
            medians,
            yerr=[low, high],
            label=label,
            color=color,
            marker=marker,
            linestyle=line,
            linewidth=2,
            markersize=6,
            capsize=3,
        )
    axis.set_xscale("log", base=2)
    axis.set_yscale("log")
    axis.set_xticks(sizes, [f"{size:,}" for size in sizes])
    axis.set_xlabel("Synthetic records (count; log₂ axis)")
    axis.set_ylabel("Median time per exact-ID lookup (µs; log axis)")
    axis.set_title("Figure 3.01  |  Same exact-ID task, different data structures")
    axis.grid(True, which="major", alpha=0.27)
    axis.legend(loc="upper left", frameon=True)
    figure.text(
        0.5,
        -0.015,
        f"{report['python_implementation']} {report['python']} · {rows[0]['queries_per_trial']} lookups/trial "
        f"(50% hits) · {rows[0]['trials']} trials · one local run; bars show min–max trial means",
        ha="center",
        va="bottom",
        fontsize=8,
    )
    for suffix in ("svg", "png"):
        destination = HERE / f"plot-03-01-id-lookup.{suffix}"
        figure.savefig(destination, dpi=180, bbox_inches="tight", metadata={"Date": None})
        if suffix == "svg":
            # Matplotlib leaves spaces at the ends of multi-line path commands.
            # The SVG parser treats a newline as whitespace, so trim those
            # spaces to keep the editable/rendered artifact diff-clean.
            source = destination.read_text(encoding="utf-8")
            destination.write_text(
                "\n".join(line.rstrip() for line in source.splitlines()) + "\n",
                encoding="utf-8",
            )
        print(destination)
    plt.close(figure)


if __name__ == "__main__":
    main()
