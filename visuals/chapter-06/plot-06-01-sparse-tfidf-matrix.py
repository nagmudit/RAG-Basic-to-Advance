"""Render Figure 6.01 from the versioned four-record toy corpus.

Requires matplotlib. Run from the repository root:
    python visuals/chapter-06/plot-06-01-sparse-tfidf-matrix.py
The heatmap contains exact computed TF-IDF values, not sampled observations.
"""

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize

matplotlib.rcParams["svg.hashsalt"] = "chapter-06-sparse-tfidf-v1"

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "projects" / "V1"))
from tfidf import build_weighted_index, load_corpus  # noqa: E402


def matrix(corpus):
    index = build_weighted_index(corpus)
    stats = index.by_scope["support-team"]
    terms = ("amber", "blue")
    ids = [segment["document_id"] for segment in index.base.segments]
    values = []
    for term in terms:
        by_ordinal = {row.ordinal: row for row in index.base.posting(term)}
        values.append([
            by_ordinal[ordinal].term_frequency * stats.idf(term)
            if ordinal in by_ordinal else 0.0
            for ordinal in range(len(ids))
        ])
    return ids, terms, values, stats


def main():
    full = load_corpus(ROOT / "projects" / "V1" / "toy_ranking_corpus.json")
    before = {
        **full,
        "snapshot": full["snapshot"] + "-before-T4",
        "documents": full["documents"][:3],
    }
    panels = [matrix(before), matrix(full)]
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2), constrained_layout=True)
    norm = Normalize(vmin=0, vmax=max(max(row) for _, _, values, _ in panels for row in values))
    for ax, (ids, terms, values, stats), label in zip(axes, panels, ("Before T4", "After adding T4")):
        image = ax.imshow(values, cmap="Blues", norm=norm, aspect="auto")
        ax.set_xticks(range(len(ids)), ids)
        ax.set_yticks(range(len(terms)), terms)
        ax.set_xlabel("Eligible segment ID")
        ax.set_ylabel("Analyzed term")
        ax.set_title(f"{label}: N={stats.n_segments}, df(amber)={stats.df['amber']}, df(blue)={stats.df['blue']}")
        for row_index, row in enumerate(values):
            for col_index, value in enumerate(row):
                ax.text(col_index, row_index, f"{value:.3f}" if value else "0",
                        ha="center", va="center", fontsize=10,
                        color="white" if value > norm.vmax * .55 else "black")
        ax.set_xticks([x - .5 for x in range(1, len(ids))], minor=True)
        ax.set_yticks([.5], minor=True)
        ax.grid(which="minor", color="#888888", linewidth=.6)
        ax.tick_params(which="minor", bottom=False, left=False)
    fig.colorbar(image, ax=axes, label="Raw TF-IDF weight: tf × ln(N/df), dimensionless", shrink=.8)
    fig.suptitle("Figure 6.01 — One added segment changes global term weights", fontsize=13)
    svg_path = HERE / "figure-06-01-sparse-tfidf-matrix.svg"
    fig.savefig(svg_path, metadata={"Date": "2026-09-29"})
    fig.savefig(HERE / "figure-06-01-sparse-tfidf-matrix.png", dpi=170)
    plt.close(fig)
    # Matplotlib puts insignificant spaces at ends of multiline SVG path data.
    # Normalize them so the generated asset passes the repository diff check.
    svg_path.write_text(
        "\n".join(line.rstrip() for line in svg_path.read_text(encoding="utf-8").splitlines()) + "\n",
        encoding="utf-8",
    )
    print("Rendered Figure 6.01 SVG and PNG")


if __name__ == "__main__":
    main()
