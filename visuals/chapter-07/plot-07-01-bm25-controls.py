"""Render Figure 7.01 from Chapter 7's BM25 term-factor function.

Axes are dimensionless: tf and analyzed segment length in terms, and the
BM25 term factor before multiplication by IDF. No sampled data or randomness.
Requires matplotlib; project scorer and tests require only the stdlib.
"""

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "projects" / "V2"))
from bm25 import saturation  # noqa: E402


def main():
    plt.rcParams["svg.hashsalt"] = "rag-ch07-bm25-controls"
    plt.rcParams["font.family"] = "DejaVu Sans"
    fig, axes = plt.subplots(1, 2, figsize=(11.4, 4.4), layout="constrained")
    tf_values = list(range(1, 13))
    for k1, color in ((0.4, "#2b6d8a"), (1.2, "#ba542f"), (2.0, "#654398")):
        values = [saturation(tf, 4, 4, k1=k1, b=.75) for tf in tf_values]
        axes[0].plot(tf_values, values, marker="o", markersize=3.8,
                     color=color, label=f"k₁ = {k1:g}")
        axes[0].axhline(1 + k1, color=color, linestyle=":", linewidth=.7,
                        alpha=.6)
    axes[0].set(title="A · Repetition has diminishing returns",
                xlabel="Term frequency in segment (occurrences)",
                ylabel="BM25 term factor before IDF (unitless)",
                xlim=(1, 12), ylim=(0, 3.25))
    axes[0].legend(frameon=False)
    axes[0].grid(alpha=.22)

    lengths = list(range(1, 13))
    for b, color in ((0, "#2b6d8a"), (.75, "#ba542f"), (1, "#654398")):
        values = [saturation(2, length, 4, k1=1.2, b=b) for length in lengths]
        axes[1].plot(lengths, values, marker="o", markersize=3.8,
                     color=color, label=f"b = {b:g}")
    axes[1].axvline(4, color="#555555", linestyle="--", linewidth=.8)
    axes[1].set(title="B · Length changes a fixed two-hit score",
                xlabel="Analyzed segment length (terms); avgdl = 4",
                ylabel="BM25 term factor before IDF (unitless)",
                xlim=(1, 12), ylim=(.4, 2.1))
    axes[1].legend(frameon=False)
    axes[1].grid(alpha=.22)
    fig.suptitle("BM25 controls repetition and length separately", fontsize=13)
    metadata = {"Date": "2026-09-29", "Creator": "Chapter 7 BM25 plot source"}
    stem = HERE / "figure-07-01-bm25-controls"
    fig.savefig(stem.with_suffix(".svg"), metadata=metadata)
    fig.savefig(stem.with_suffix(".png"), dpi=180, metadata={"Software": "matplotlib"})
    plt.close(fig)
    # Matplotlib may emit indentation as trailing whitespace in SVG path data.
    svg = stem.with_suffix(".svg")
    svg.write_text("\n".join(line.rstrip() for line in
                             svg.read_text(encoding="utf-8").splitlines()) + "\n",
                   encoding="utf-8")
    print(f"Wrote {stem.with_suffix('.svg')} and {stem.with_suffix('.png')}")


if __name__ == "__main__":
    main()
