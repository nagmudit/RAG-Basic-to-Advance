"""Figure measurement and layout decisions.

A figure is placed in the smallest layout whose scale keeps its labels at or
above `min_label_pt`: normal (text width) -> wide (into the margins) ->
full-page (own page) or landscape (own rotated page), trying landscape first
for wide aspect ratios. Figures are never shrunk just to share a page with
prose; if no layout reaches the minimum, the most legible one is used and a
warning suggests splitting the figure.
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from .common import PT_PER_MM
from .config import Paper

MARGIN_PT = 20 * PT_PER_MM          # keep in sync with @page in book.css
WIDE_EXTRA_PT = 12 * PT_PER_MM      # a wide figure extends this far beyond the text column (body padding)
PAGE_SIDE_PT = 8 * PT_PER_MM        # @page side margin (keep in sync with book.css)
LANDSCAPE_MARGIN_V_PT = 18 * PT_PER_MM   # keep in sync with @page landscape
LANDSCAPE_MARGIN_H_PT = 15 * PT_PER_MM   # keep in sync with @page landscape
CAPTION_ALLOWANCE_PT = 60           # room for the caption above a figure on its own page
LAYOUTS = ("normal", "wide", "fullpage", "landscape")


@dataclass
class Box:
    width: float
    height: float


def layout_boxes(paper: Paper) -> dict[str, Box]:
    content_w = paper.width_pt - 2 * MARGIN_PT
    content_h = paper.height_pt - 2 * MARGIN_PT
    return {
        "normal": Box(content_w, content_h * 0.55),
        "wide": Box(content_w + 2 * WIDE_EXTRA_PT, content_h * 0.62),
        "fullpage": Box(content_w + 2 * WIDE_EXTRA_PT, content_h - CAPTION_ALLOWANCE_PT),
        "landscape": Box(paper.height_pt - 2 * LANDSCAPE_MARGIN_H_PT,
                         paper.width_pt - 2 * LANDSCAPE_MARGIN_V_PT - CAPTION_ALLOWANCE_PT),
    }


@dataclass
class Measure:
    width_pt: float
    height_pt: float
    label_pt: float        # nominal label size at scale 1
    fluid: bool            # SVG declares width=100% (may be enlarged)


def _len_pt(v: str | None) -> float | None:
    if not v:
        return None
    m = re.fullmatch(r"\s*([\d.]+)\s*(pt|px|mm|cm|in)?\s*", v)
    if not m:
        return None
    n, unit = float(m[1]), (m[2] or "px")
    return n * {"pt": 1, "px": 0.75, "mm": PT_PER_MM, "cm": 10 * PT_PER_MM, "in": 72}[unit]


def measure_svg(path: Path) -> Measure | None:
    try:
        head = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    tag = re.search(r"<svg\b[^>]*>", head, re.S)
    if not tag:
        return None
    t = tag[0]
    attr = lambda name: (m[1] if (m := re.search(rf'\s{name}="([^"]*)"', t)) else None)
    vb = attr("viewBox")
    vbw = vbh = None
    if vb:
        nums = [float(x) for x in re.split(r"[\s,]+", vb.strip()) if x]
        if len(nums) == 4:
            vbw, vbh = nums[2], nums[3]
    w, h = _len_pt(attr("width")), _len_pt(attr("height"))
    fluid = (attr("width") or "").strip().endswith("%")
    if fluid or w is None:
        if vbw is None:
            return None
        w, h = vbw * 0.75, vbh * 0.75          # Mermaid: viewBox in CSS px
    elif h is None and vbw:
        h = w * vbh / vbw
    if not w or not h:
        return None
    # Nominal label size: the most common explicit font size, else a type default.
    sizes = Counter(float(s) for s in re.findall(r"font-size:\s*([\d.]+)px", head))
    if sizes:
        label = sizes.most_common(1)[0][0] * 0.75
    elif "matplotlib" in head[:2000] or "Created with matplotlib" in head:
        label = 10.0                             # matplotlib default text size (glyphs are paths)
    else:
        label = 10.0
    return Measure(w, h, label, fluid)


def mermaid_nodes(src: str) -> int:
    """Rough node count for density warnings (flowchart ids and sequence participants)."""
    ids = set(re.findall(r"(?:^|[\s>|-])([A-Za-z_][\w]*)\s*[\[\(\{]", src, re.M))
    ids |= set(re.findall(r"^\s*participant\s+(\w+)", src, re.M))
    return len(ids)


def choose_layout(m: Measure, boxes: dict[str, Box], min_label: float, max_label: float,
                  forced: str | None = None) -> tuple[str, float, float]:
    """Return (layout, scale, label_pt)."""
    cap = max_label / m.label_pt if m.label_pt else 1.0
    cap = min(cap, 1.0) if not m.fluid else cap

    def fit(name):
        b = boxes[name]
        s = min(cap, b.width / m.width_pt, b.height / m.height_pt)
        return s, s * m.label_pt

    if forced in LAYOUTS:
        s, lbl = fit(forced)
        return forced, s, lbl
    order = ["normal", "wide"] + (["landscape", "fullpage"] if m.width_pt / m.height_pt > 1.3
                                  else ["fullpage", "landscape"])
    best = None
    for name in order:
        s, lbl = fit(name)
        if lbl >= min_label - 1e-6:
            return name, s, lbl
        if best is None or lbl > best[2] + 0.05:
            best = (name, s, lbl)
    return best
