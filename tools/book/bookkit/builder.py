"""Markdown -> one HTML document for a given build profile."""

from __future__ import annotations

import datetime as dt
import hashlib
import html
import json
import re
import shutil
import subprocess
from pathlib import Path, PurePosixPath
from urllib.parse import unquote

from markdown_it import MarkdownIt
from markdown_it.token import Token
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import TextLexer, get_lexer_by_name, get_lexer_for_filename
from pygments.util import ClassNotFound

from . import BUILDER_VERSION
from .biblio import Bibliography
from .common import (CSS, PYGMENTS_STYLE, ROOT, Block, Caption, Chapter, Heading, Issues,
                     doc_anchor, first_h1, gh_slug, git, glob_files, heading_anchor, id_slug,
                     natural_key, rel, roman, strip_tags)
from .config import Paper, parse_paper
from .figures import (LANDSCAPE_MARGIN_V_PT, LAYOUTS, MARGIN_PT, PAGE_SIDE_PT, Measure, choose_layout, layout_boxes, measure_svg,
                      mermaid_nodes)

CAPTION_KINDS = ("Figure", "Table", "Plot", "Trace", "Illustration", "Listing")
FIGURE_KINDS = ("Figure", "Plot", "Illustration")
LAYOUT_DIRECTIVE = re.compile(r"<!--\s*(?:figure-|table-|code-)?layout:\s*([a-z-]+)\s*-->")
INDEX_MARK = re.compile(r"@index\{([^{}]+)\}")
MMDC_CACHE = ROOT / "build" / ".cache" / "mermaid"


# ------------------------------------------------------------------ syllabus

def parse_syllabus(path: Path):
    """[{roman, title, level, modules: [{num, title, chapters: [(n, title)]}]}]"""
    parts = []
    if not path.exists():
        return parts
    for line in path.read_text(encoding="utf-8").splitlines():
        if m := re.match(r"^## Part ([IVXLC]+) — (.+?)(?:\s+\[(.+)\])?\s*$", line):
            parts.append({"roman": m[1], "title": m[2], "level": m[3], "modules": []})
        elif (m := re.match(r"^### Module (\d+) — (.+)$", line)) and parts:
            parts[-1]["modules"].append({"num": int(m[1]), "title": m[2], "chapters": []})
        elif (m := re.match(r"^#### Chapter (\d+) — (.+)$", line)) and parts:
            if not parts[-1]["modules"]:
                parts[-1]["modules"].append({"num": 0, "title": "", "chapters": []})
            parts[-1]["modules"][-1]["chapters"].append((int(m[1]), m[2].strip()))
    return parts


def discover_chapters(sources: dict) -> list[Chapter]:
    out = []
    for p in glob_files([sources["chapters"]]):
        m = re.search(r"chapter-(\d+)", p.name)
        if m:
            out.append(Chapter(m[1], p, int(m[1]), first_h1(p)))
    return sorted(out, key=lambda c: c.number)


def mermaid_to_svg(src: str, issues: Issues) -> Path | None:
    """Render a Mermaid block with mmdc once; cached by content hash."""
    mmdc = shutil.which("mmdc")
    if not mmdc:
        return None
    MMDC_CACHE.mkdir(parents=True, exist_ok=True)
    out = MMDC_CACHE / f"{hashlib.sha1(src.encode()).hexdigest()[:16]}.svg"
    if out.exists():
        return out
    tmp = out.with_suffix(".mmd")
    tmp.write_text(src, encoding="utf-8")
    try:
        subprocess.run([mmdc, "-i", str(tmp), "-o", str(out), "-b", "white", "-q"],
                       cwd=ROOT, capture_output=True, timeout=180, check=False)
    except (OSError, subprocess.TimeoutExpired) as e:
        issues.warn(f"mmdc failed ({e}); falling back to in-browser Mermaid")
    tmp.unlink(missing_ok=True)
    return out if out.exists() else None


# -------------------------------------------------------------------- builder

class BookBuilder:
    def __init__(self, cfg: dict, profile: dict, issues: Issues, mode: str | None = None):
        self.cfg = cfg
        self.p = profile
        self.issues = issues
        self.book = cfg["book"]
        self.sources = cfg["sources"]
        self.layout = cfg.get("layout", {})
        self.mode = mode or self.book.get("mode", "draft")
        self.paper: Paper = parse_paper(self.book.get("paper", "A4"))
        self.boxes = layout_boxes(self.paper)
        self.repo_url = self.book.get("repo_url", "").rstrip("/")
        self.branch = self.book.get("branch", "master")
        self.bib = Bibliography(self.sources, issues)
        self.md = (MarkdownIt("commonmark", {"html": True, "typographer": False})
                   .enable("table").enable("strikethrough"))
        self.md.add_render_rule("fence", self._render_fence)
        self.chapters = discover_chapters(self.sources)
        self.parts = parse_syllabus(ROOT / self.sources.get("syllabus", "SYLLABUS.md"))
        self.planned = {n: t for part in self.parts for m in part["modules"] for n, t in m["chapters"]}
        self.commit = git("rev-parse", "--short", "HEAD") or "unknown"
        self.dirty = bool(git("status", "--porcelain", "--untracked-files=no"))
        self.built = dt.date.today().isoformat()
        self._reset()
        self._plan()

    # ---------------------------------------------------------------- state
    def _reset(self):
        self.captions: list[Caption] = []
        self.figures: list[dict] = []           # layout decisions for the report
        self.index_marks: list[dict] = []
        self.used_images: set[str] = set()
        self.used_anchor_ids: set[str] = set()
        self.appendix_letters: dict[str, str] = {}   # section id -> letter
        self.code_blocks: list[dict] = []
        self.external_links = 0
        self.citations = 0
        self.bib.reset_usage()
        self._pending_layout: str | None = None
        self._ctx = {"doc": None, "chapter": None, "src": ROOT, "further": False, "register": None}

    def chapter_file(self, key: str, ch: Chapter) -> Path | None:
        pat = self.sources.get(key)
        if not pat:
            return None
        p = ROOT / pat.format(nn=ch.nn, n=ch.number)
        return p if p.exists() else None

    def _plan(self):
        """Decide which files this edition contains and assign every anchor up front."""
        secs = self.cfg.get("sections", {})
        appendices = list(self.p["appendices"])
        if self.p["solutions"] == "appendix" and "solutions" not in appendices:
            appendices.insert(0, "solutions")
        self.front_ids, self.appendix_ids, self.back_ids = self.p["front"], appendices, self.p["back"]
        chapter_owned = set()
        for ch in self.chapters:
            chapter_owned.add(rel(ch.path))
            for k in ("lab", "solution", "review"):
                if f := self.chapter_file(k, ch):
                    chapter_owned.add(rel(f))
        placed: set[str] = set()
        self.section_paths: dict[str, list[Path]] = {}
        for sid in self.front_ids + self.appendix_ids + self.back_ids:
            sec = secs[sid]
            if sec.get("auto"):
                self.section_paths[sid] = []
                continue
            paths = []
            for pat in sec.get("files", []):
                if not any(True for _ in ROOT.glob(pat)):
                    self.issues.error(f"section {sid!r}: no file matches {pat}")
            for f in glob_files(sec.get("files", [])):
                r = rel(f)
                if f.suffix == ".md" and r not in placed and r not in chapter_owned:
                    placed.add(r)
                    paths.append(f)
            self.section_paths[sid] = paths
        # Documents printed in this edition (links to anything else go to the repository).
        self.doc_ids: dict[str, str] = {}
        for paths in self.section_paths.values():
            for f in paths:
                self.doc_ids[rel(f)] = doc_anchor(rel(f))
        body = self.p["body"]
        for ch in self.chapters:
            if body == "chapters":
                self.doc_ids[rel(ch.path)] = doc_anchor(rel(ch.path))
            if (body == "labs" or (body == "chapters" and self.p["labs"] == "inline")) and \
                    (f := self.chapter_file("lab", ch)):
                self.doc_ids[rel(f)] = doc_anchor(rel(f))
            if (body == "solutions" or "solutions" in self.appendix_ids) and \
                    (f := self.chapter_file("solution", ch)):
                self.doc_ids[rel(f)] = doc_anchor(rel(f))
            if "reviews" in self.appendix_ids and (f := self.chapter_file("review", ch)):
                self.doc_ids[rel(f)] = doc_anchor(rel(f))
        self.code_ids: dict[str, str] = {}
        if "code" in self.appendix_ids + self.back_ids:
            for f in glob_files(secs["code"].get("files", [])):
                self.code_ids[rel(f)] = "code-" + id_slug(rel(f))
        self.visual_ids: dict[str, str] = {}
        if "visuals" in self.appendix_ids + self.back_ids:
            for f in glob_files(["visuals/**/*"]):
                if f.suffix.lower() in (".svg", ".png", ".jpg", ".jpeg", ".mmd", ".gif", ".webp"):
                    self.visual_ids[rel(f)] = "vis-" + id_slug(rel(f))
        letter = 0
        for sid in self.appendix_ids:
            if secs[sid].get("auto") or self.section_paths[sid]:
                letter += 1
                self.appendix_letters[sid] = chr(64 + letter)
        # Unit anchor per chapter number: where "Chapter N" points in this edition.
        self.unit_ids: dict[int, str] = {}
        for ch in self.chapters:
            if body == "chapters":
                self.unit_ids[ch.number] = f"unit-ch{ch.number:02d}"
            elif body == "labs" and self.chapter_file("lab", ch):
                self.unit_ids[ch.number] = f"unit-ch{ch.number:02d}"
            elif body == "solutions" and self.chapter_file("solution", ch):
                self.unit_ids[ch.number] = f"unit-ch{ch.number:02d}"

    # ------------------------------------------------------------ links
    def github(self, path: str, is_dir: bool = False) -> str:
        if not self.repo_url:
            return path
        return f"{self.repo_url}/{'tree' if is_dir else 'blob'}/{self.branch}/{path}"

    def resolve_href(self, href: str, src: Path) -> str:
        if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", href) or href.startswith("//"):
            return href
        src_rel = rel(src)
        if href.startswith("#"):
            base = self.doc_ids.get(src_rel)
            return "#" + heading_anchor(base, href[1:]) if base else self.github(src_rel) + href
        path, _, frag = href.partition("#")
        target = (src.parent / unquote(path)).resolve()
        try:
            t = rel(target)
        except ValueError:
            self.issues.error(f"{src_rel}: link leaves the repository: {href}")
            return href
        if not target.exists():
            self.issues.error(f"{src_rel}: broken relative link -> {href}")
            return self.github(t)
        if target.is_dir():
            readme = target / "README.md"
            if readme.exists() and rel(readme) in self.doc_ids:
                return "#" + self.doc_ids[rel(readme)]
            return self.github(t, is_dir=True)
        if t in self.doc_ids:
            return "#" + (heading_anchor(self.doc_ids[t], frag) if frag else self.doc_ids[t])
        if target.suffix.lower() in (".svg", ".png", ".jpg", ".jpeg", ".mmd"):
            return f"#asset:{t}"          # resolved to the figure, gallery or repository later
        if t in self.code_ids:
            return "#" + self.code_ids[t]
        return self.github(t)

    # --------------------------------------------------------- code blocks
    def _render_fence(self, tokens, idx, options, env):
        tok = tokens[idx]
        lang = (tok.info or "").strip().split()[0] if tok.info else ""
        if lang == "mermaid":
            return self._mermaid_html(tok.content)
        layout = self._pending_layout if self._pending_layout == "landscape" else None
        self._pending_layout = None
        return self.highlight(tok.content, lang=lang, layout=layout)

    def highlight(self, code: str, lang: str = "", filename: str = "", linenos=False,
                  layout: str | None = None, check: bool = True) -> str:
        lexer = None
        try:
            if lang and lang not in ("text", "plain", "txt"):
                lexer = get_lexer_by_name(lang)
            elif filename:
                lexer = get_lexer_for_filename(filename)
        except ClassNotFound:
            pass
        fmt = HtmlFormatter(style=PYGMENTS_STYLE, cssclass="hl", linespans="cl",
                            linenos="inline" if linenos else False)
        out = highlight(code, lexer or TextLexer(), fmt)
        out = re.sub(r'<span id="cl-\d+">', '<span class="cl">', out)
        lines = code.rstrip("\n").split("\n")
        widths = [len(l.expandtabs(4)) for l in lines]
        if layout is None and not linenos and max(widths, default=0) > self.code_columns():
            if max(widths) <= self.code_columns("wide"):
                layout = "wide"               # extend into the margins rather than wrap
        cols = self.code_columns(layout)
        long = [w for w in widths if w > cols]
        if check:
            first = next((re.sub(r"\s+", " ", l.strip()) for l in lines if len(l.strip()) >= 20), "")
            self.code_blocks.append({"doc": rel(self._ctx["src"]), "lines": len(lines),
                                     "long": len(long), "max": max(long, default=0), "listing": linenos,
                                     "first": first, "chapter": self._ctx["chapter"]})
        cls = ["code"]
        if linenos:
            cls.append("listing")
        if len(lines) <= int(self.layout.get("short_code_lines", 25)):
            cls.append("short")
        if layout in ("landscape", "wide"):
            cls.append(f"layout-{layout}")
        return f'<div class="{" ".join(cls)}" data-lang="{html.escape(lang)}">{out}</div>\n'

    def code_samples(self) -> list[str]:
        """First substantial line of each chapter code block (for the text-extraction test)."""
        return [c["first"] for c in self.code_blocks
                if c["first"] and not c["listing"] and c["chapter"] is not None]

    def code_columns(self, layout: str | None = None) -> int:
        """Characters per code line before wrapping (padding, border and hanging indent removed)."""
        width = {"landscape": self.boxes["landscape"].width,
                 "wide": self.boxes["wide"].width}.get(layout, self.paper.width_pt - 2 * MARGIN_PT)
        char = 0.55 * float(self.layout.get("code_pt", 8.5))      # Consolas/Cascadia advance
        return int((width - 20 - 1.7 * char) / char)

    # ------------------------------------------------------------- figures
    def _figure_img(self, src_uri: str, path: Path | None, alt: str, forced: str | None,
                    measure: Measure | None) -> str:
        layout, style = "normal", ""
        if measure:
            layout, scale, label = choose_layout(
                measure, self.boxes, float(self.layout.get("min_label_pt", 6.5)),
                float(self.layout.get("max_label_pt", 11.0)), forced)
            style = f' style="width:{measure.width_pt * scale:.1f}pt"'
            rec = {"src": rel(path) if path else "", "layout": layout, "scale": round(scale, 3),
                   "label_pt": round(label, 2), "doc": rel(self._ctx["src"])}
            self.figures.append(rec)
            if label < float(self.layout.get("min_label_pt", 6.5)) - 1e-6:
                self.issues.warn(f"{rec['doc']}: {rec['src'] or 'diagram'} labels render at {label:.1f}pt "
                                 f"even on a {layout} page (minimum "
                                 f"{self.layout.get('min_label_pt', 6.5)}pt); consider splitting it")
        elif forced in LAYOUTS:
            layout = forced
        return (f'<img class="fig" data-layout="{layout}" src="{src_uri}" alt="{html.escape(alt)}"'
                f'{style}>')

    def _mermaid_html(self, src: str) -> str:
        forced, self._pending_layout = self._pending_layout, None
        nodes = mermaid_nodes(src)
        if nodes > int(self.layout.get("dense_diagram_nodes", 28)):
            self.issues.warn(f"{rel(self._ctx['src'])}: Mermaid diagram has ~{nodes} nodes; "
                             f"consider splitting it into smaller figures")
        svg = mermaid_to_svg(src, self.issues)
        if svg:
            m = measure_svg(svg)
            img = self._figure_img(svg.as_uri(), None, "Diagram", forced, m)
            return f'<figure class="img">{img}</figure>\n'
        return f'<div class="mermaid-wrap"><pre class="mermaid">{html.escape(src)}</pre></div>\n'

    # ------------------------------------------------------------ markdown
    @staticmethod
    def protect(text: str):
        """Pull math and @index markers out before Markdown parsing; skip code."""
        maths: list[tuple[bool, str]] = []
        marks: list[str] = []
        out_parts, chunk = [], []
        fence = None

        def flush():
            if not chunk:
                return
            seg = "".join(chunk)
            codes: list[str] = []

            def keep_code(m):
                codes.append(m[0])
                return f"CODESPAN{len(codes) - 1}X"
            seg = re.sub(r"(`+)(?:.|\n)+?\1", keep_code, seg)

            def disp(m):
                maths.append((True, m[1].strip()))
                return f"\n\nMATHBLOCK{len(maths) - 1}X\n\n"

            def inl(m):
                maths.append((False, m[1].strip()))
                return f"MATHINLINE{len(maths) - 1}X"

            def mark(m):
                marks.append(m[1].strip())
                return f"IDXMARK{len(marks) - 1}X"
            seg = re.sub(r"\\\[(.+?)\\\]", disp, seg, flags=re.S)
            seg = re.sub(r"\\\((.+?)\\\)", inl, seg, flags=re.S)
            seg = INDEX_MARK.sub(mark, seg)
            seg = re.sub(r"CODESPAN(\d+)X", lambda m: codes[int(m[1])], seg)
            out_parts.append(seg)
            chunk.clear()

        for line in text.splitlines(keepends=True):
            m = re.match(r"^\s*(```+|~~~+)", line)
            if fence is None and m:
                flush()
                fence = m[1]
                out_parts.append(line)
            elif fence is not None:
                out_parts.append(line)
                s = line.strip()
                if s.startswith(fence[0] * len(fence)) and s.strip(fence[0]) == "":
                    fence = None
            else:
                chunk.append(line)
        flush()
        return "".join(out_parts), maths, marks

    def template(self, text: str) -> str:
        written = [c.number for c in self.chapters]
        span = (f"Chapters {written[0]}–{written[-1]}" if len(written) > 1
                else f"Chapter {written[0]}" if written else "no chapters")
        note = {"companion": ", which are published separately in the solutions companion",
                "appendix": ", which are collected in an appendix at the back of the book",
                "none": ""}[self.p["solutions"]]
        values = {"written_span": span, "planned_total": str(len(self.planned) or len(written)),
                  "planned_parts": str(len(self.parts)), "solutions_note": note,
                  "edition": self.p["edition"], "version": str(self.book.get("version", ""))}
        return re.sub(r"\{\{\s*(\w+)\s*\}\}", lambda m: values.get(m[1], m[0]), text)

    def render_doc(self, path: Path, shift: int = 0, title_override: str | None = None,
                   chapter: int | None = None, heading_hook=None, text: str | None = None,
                   doc_id: str | None = None) -> Block:
        """Render one Markdown file (or `text` attributed to it). `shift` demotes headings."""
        src_rel = rel(path)
        doc_id = doc_id or self.doc_ids.get(src_rel) or doc_anchor(src_rel)
        register = next((k for k, key in (("reference", "reference_registers"),
                                          ("further", "reading_registers"),
                                          ("frontier", "frontier_registers"))
                         if src_rel in self.sources.get(key, [])), None)
        self._ctx = {"doc": doc_id, "chapter": chapter, "src": path, "further": False,
                     "register": register}
        raw = text if text is not None else path.read_text(encoding="utf-8")
        if src_rel.startswith("book/"):
            raw = self.template(raw)
        raw, maths, marks = self.protect(raw)
        tokens = self.md.parse(raw)
        headings: list[Heading] = []
        slugs: dict[str, int] = {}
        for i, tok in enumerate(tokens):
            if tok.type == "html_block" and (m := LAYOUT_DIRECTIVE.search(tok.content)):
                self._pending_layout = m[1]
            elif tok.type == "heading_open":
                lvl = int(tok.tag[1])
                inline = tokens[i + 1]
                if lvl == 1 and title_override and not headings:
                    inline.children = self.md.parse(title_override)[1].children
                plain = "".join(c.content for c in (inline.children or [])
                                if c.type in ("text", "code_inline", "html_inline")).strip()
                slug = gh_slug(plain)
                n = slugs.get(slug, 0)
                slugs[slug] = n + 1
                hid = heading_anchor(doc_id, f"{slug}-{n}" if n else slug)
                new_lvl = min(lvl + shift, 6)
                tok.tag = f"h{new_lvl}"
                close = next(j for j in range(i, len(tokens)) if tokens[j].type == "heading_close")
                tokens[close].tag = f"h{new_lvl}"
                tok.attrSet("id", hid)
                h = Heading(hid, plain, new_lvl)
                self._ctx["further"] = bool(re.search(r"further reading", plain, re.I))
                if heading_hook:
                    heading_hook(h, lvl, tok)
                else:
                    h.toc = self.toc_ok("doc", h.level)
                headings.append(h)
            elif tok.type == "table_open" and self._pending_layout:
                tok.attrSet("data-layout", self._pending_layout)
                self._pending_layout = None
            elif tok.type == "inline" and tok.children:
                self._inline(tok, path)
        body = self.md.renderer.render(tokens, self.md.options, {})
        body = self._postprocess(body, maths, marks, doc_id, chapter, src_rel)
        return Block(f'<section class="doc" id="{doc_id}" data-src="{src_rel}">\n{body}</section>\n',
                     headings)

    def _inline(self, tok: Token, path: Path):
        children, out, cited = tok.children, [], set()
        for c in children:
            out.append(c)
            if c.type == "link_open":
                href = c.attrGet("href") or ""
                if re.match(r"https?://", href):
                    self.external_links += 1
                    work = self.bib.lookup(href)
                    ctx = self._ctx
                    context = ctx["register"] or ("further" if ctx["further"] else "reference")
                    if work:
                        self.bib.record(work, context, ctx["chapter"])
                        c.meta["cite"] = None if work.key in cited else work
                        cited.add(work.key)
                    elif ctx["chapter"] is not None or ctx["register"]:
                        self.issues.warn(f"{rel(path)}: external source not in the provenance registers "
                                         f"or bibliography: {href}")
                c.attrSet("href", self.resolve_href(href, path))
            elif c.type == "link_close":
                opener = next((o for o in reversed(out[:-1]) if o.type == "link_open"), None)
                work = opener.meta.get("cite") if opener is not None else None
                if work is not None:
                    t = Token("html_inline", "", 0)
                    t.content = " " + self.bib.citation_html(work)
                    out.append(t)
                    self.citations += 1
                    opener.meta["cite"] = None
            elif c.type == "image":
                self._image(c, path)
        tok.children = out

    def _image(self, c: Token, path: Path):
        src = c.attrGet("src") or ""
        forced, self._pending_layout = self._pending_layout, None
        if re.match(r"^[a-z]+:", src):
            return
        target = (path.parent / unquote(src)).resolve()
        if not target.exists():
            self.issues.error(f"{rel(path)}: missing image {src}")
            return
        self.used_images.add(rel(target))
        alt = "".join(ch.content for ch in (c.children or [])) or c.content
        measure = measure_svg(target) if target.suffix.lower() == ".svg" else None
        c.type = "html_inline"
        c.content = self._figure_img(target.as_uri(), target, alt, forced, measure)
        c.children = None

    def _postprocess(self, body: str, maths, marks, doc_id: str, chapter: int | None,
                     src_rel: str) -> str:
        def math_html(i: int) -> str:
            display, tex = maths[i]
            tag = "div" if display else "span"
            return f'<{tag} class="math{" display" if display else ""}">{html.escape(tex)}</{tag}>'
        body = re.sub(r"<p>MATHBLOCK(\d+)X</p>", lambda m: math_html(int(m[1])), body)
        body = re.sub(r"MATH(?:BLOCK|INLINE)(\d+)X", lambda m: math_html(int(m[1])), body)

        def mark_html(m):
            term = marks[int(m[1])]
            anchor = f"ix-{len(self.index_marks) + 1}"
            self.index_marks.append({"term": term, "anchor": anchor, "doc": doc_id, "chapter": chapter})
            return f'<a class="ix" id="{anchor}"></a>'
        body = re.sub(r"IDXMARK(\d+)X", mark_html, body)
        # A paragraph holding only an image becomes a figure; its layout comes from the image.
        body = re.sub(r'<p>\s*(<img class="fig" data-layout="(\w+)"[^>]*>)\s*</p>',
                      r'<figure class="img layout-\2">\1</figure>', body)
        body = re.sub(r'<figure class="img">(<img class="fig" data-layout="(\w+)")',
                      r'<figure class="img layout-\2">\1', body)
        # Numbered captions: **Figure 7.01 — Title.** ...
        new_caps: list[Caption] = []

        def cap(m):
            kind, num, title = m[1], m[2], strip_tags(m[3]).strip().rstrip(".")
            anchor = f"cap-{kind.lower()}-{num.replace('.', '-')}"
            if anchor in self.used_anchor_ids:
                self.issues.error(f"{src_rel}: duplicate {kind} {num}")
                anchor = f"{anchor}-{len(self.captions)}"
            self.used_anchor_ids.add(anchor)
            c = Caption(kind, num, title, anchor, chapter, doc_id, src_rel, len(self.captions))
            self.captions.append(c)
            new_caps.append(c)
            return f'<p class="caption caption-{kind.lower()}" id="{anchor}"><strong>{kind} {num} — {m[3]}'
        body = re.sub(rf"<p><strong>({'|'.join(CAPTION_KINDS)}) (\d+\.\d+) — (.*?)(?=</strong>)", cap, body)
        # Tables: wrap (layout classes are applied here or by in-browser measurement).
        body = re.sub(r'<table( data-layout="(\w+)")?>',
                      lambda m: f'<div class="table-wrap{" layout-" + m[2] if m[2] else ""}"><table>', body)
        body = body.replace("</table>", "</table></div>")
        # Group each figure caption with the figure that follows it (and its metadata note).
        body = self._group_figures(body, new_caps)
        for c in new_caps:
            if not c.attached:
                what = "table" if c.kind == "Table" else "figure"
                self.issues.warn(f"{src_rel}: {c.kind} {c.number} caption is not followed by its {what}")
        return body

    def _group_figures(self, body: str, caps: list[Caption]) -> str:
        note_re = r'(?:\s*(<p><em>Alt text:</em>.*?</p>))?'
        for c in caps:
            if c.kind == "Table":
                m = re.search(rf'(<p class="caption caption-table" id="{c.anchor}">.*?</p>)\s*'
                              rf'(<div class="table-wrap[^"]*">)', body, re.S)
                if m:
                    c.attached = True
                    body = body.replace(m[1], m[1].replace('class="caption', 'class="caption keep-next', 1), 1)
                continue
            m = re.search(rf'<p class="(caption[^"]*)" id="{c.anchor}">(.*?)</p>\s*'
                          rf'(<figure class="img layout-(\w+)">(.*?)</figure>){note_re}', body, re.S)
            if not m:
                continue
            c.attached = True
            layout, inner, note = m[4], m[5], m[6]
            if (src := re.search(r'src="file:///([^"]+)"', inner)):
                try:
                    c.asset = rel(Path(unquote(src[1])))
                except ValueError:
                    c.asset = None
            alt = ""
            if note:
                alt_m = re.match(r"<p><em>Alt text:</em>\s*(.*?)(?:<em>|</p>)", note, re.S)
                alt = strip_tags(alt_m[1]).strip() if alt_m else ""
            if alt:
                inner = re.sub(r'alt="[^"]*"', f'alt="{html.escape(alt)}"', inner, count=1)
            elif 'alt="Diagram"' in inner:
                inner = inner.replace('alt="Diagram"', f'alt="{html.escape(c.title)}"', 1)
            meta = (f'<div class="figure-meta">{note.replace("<p>", "<p class=\"figure-note\">", 1)}</div>'
                    if note and self.p["figure_metadata"] else "")
            fig = (f'<figure class="numbered layout-{layout}" data-caption="{c.anchor}">'
                   f'<figcaption class="{m[1]}" id="{c.anchor}">{m[2]}</figcaption>{inner}{meta}</figure>')
            body = body.replace(m[0], fig, 1)
        return body

    # --------------------------------------------------------- TOC policy
    def toc_ok(self, kind: str, level: int) -> bool:
        if kind in ("front", "part", "appendix", "back", "chapter", "unit"):
            return True
        if kind == "lab":
            return self.p["toc_labs"] or self.p["toc_depth"] >= level
        return level <= self.p["toc_depth"]

    # ------------------------------------------------------ book sections
    def section_block(self, sid: str, kind: str) -> Block | None:
        sec = self.cfg["sections"][sid]
        if sec.get("auto"):
            return self.auto_block(sid, kind)
        paths = self.section_paths.get(sid, [])
        if not paths:
            return None
        letter = self.appendix_letters.get(sid) if kind == "appendix" else None
        title = sec.get("title")
        book_title = self.book["title"]
        if len(paths) == 1:
            name = title or first_h1(paths[0])
            full = f"Appendix {letter} — {name}" if letter else name

            def hook(h, lvl, tok):
                if lvl == 1:
                    h.level, h.kind, h.toc, h.opener = 1, kind, True, True
                    h.running = full if kind != "appendix" else f"Appendix {letter} · {name}"
                    h.verso = book_title
                    tok.attrSet("class", f"{kind}-title")
                else:
                    h.toc = kind == "appendix" and h.level == 2 and self.p["toc_depth"] >= 3
            b = self.render_doc(paths[0], title_override=full, heading_hook=hook)
            return Block(f'<div class="{kind} section-start"{self._appendix_id(letter)}>{b.html}</div>',
                         b.headings)
        name = title or first_h1(paths[0])
        full = f"Appendix {letter} — {name}" if letter else name
        sid_anchor = f"sec-{id_slug(full)}"
        head = Heading(sid_anchor, full, 1, kind=kind, toc=True, opener=True, verso=book_title,
                       running=f"Appendix {letter} · {name}" if letter else full)
        parts = [f'<h1 class="{kind}-title" id="{sid_anchor}">{html.escape(full)}</h1>']
        heads = [head]
        for f in paths:
            def hook(h, lvl, tok):
                h.level = lvl + 1
                h.toc = self.toc_ok("doc", h.level)
            b = self.render_doc(f, shift=1, heading_hook=hook)
            parts.append(b.html)
            heads += b.headings
        return Block(f'<div class="{kind} section-start"{self._appendix_id(letter)}>{"".join(parts)}</div>',
                     heads)

    @staticmethod
    def _appendix_id(letter: str | None) -> str:
        return f' id="appendix-{letter.lower()}"' if letter else ""

    def part_block(self, part: dict) -> Block:
        pid = f"part-{part['roman'].lower()}"
        title = f"Part {part['roman']} — {part['title']}"
        written = {c.number for c in self.chapters}
        rows = []
        for mod in part["modules"]:
            if mod["title"]:
                rows.append(f'<li class="module">Module {mod["num"]:02d} — {html.escape(mod["title"])}</li>')
            for n, t in mod["chapters"]:
                if n in self.unit_ids:
                    rows.append(f'<li class="ch written"><a href="#{self.unit_ids[n]}">'
                                f'<span class="n">{n}</span>{html.escape(t)}</a></li>')
                else:
                    tag = "planned" if n not in written else "not in this edition"
                    rows.append(f'<li class="ch planned"><span class="n">{n}</span>{html.escape(t)}'
                                f'<span class="tag">{tag}</span></li>')
        level = f'<div class="part-level">{html.escape(part["level"])}</div>' if part.get("level") else ""
        out = (f'<section class="part-page" id="{pid}"><h1 class="part-title" id="{pid}-title">'
               f'<span class="part-label">Part {part["roman"]}</span>'
               f'<span class="part-name">{html.escape(part["title"])}</span></h1>{level}'
               f'<ul class="part-chapters">{"".join(rows)}</ul></section>')
        verso = f"Part {part['roman']} · {part['title']}"
        return Block(out, [Heading(f"{pid}-title", title, 1, kind="part", toc=True, opener=True,
                                   running="", verso=verso)])

    def _unit_heading_hook(self, ch: Chapter, label: str):
        def hook(h: Heading, src_lvl: int, tok):
            h.level = src_lvl + 1
            if src_lvl == 1:
                h.kind, h.toc, h.opener = "chapter", True, True
                h.running = label
                tok.attrSet("class", "chapter-title")
            else:
                h.toc = self.toc_ok("section", h.level)
        return hook

    def chapter_block(self, ch: Chapter, pages=None) -> Block:
        label = f"Chapter {ch.number} · {ch.short_title}"
        b = self.render_doc(ch.path, chapter=ch.number, heading_hook=self._unit_heading_hook(ch, label))
        b.html = re.sub(r'(<h1 id="[^"]+" class="chapter-title">)Chapter (\d+) — (.*?)</h1>',
                        r'\1<span class="ch-label">Chapter \2</span><span class="ch-name">\3</span></h1>',
                        b.html, count=1)
        heads = list(b.headings)
        parts = [f'<span class="unit-anchor" id="{self.unit_ids[ch.number]}"></span>', b.html]
        if self.p["local_toc"]:
            parts[1] = self._insert_local_toc(parts[1], b.headings, pages)
        if self.p["labs"] == "inline" and (lab := self.chapter_file("lab", ch)):
            lb = self._lab(lab, ch, shift=1)
            parts.append(f'<div class="lab">{lb.html}</div>')
            heads += lb.headings
        return Block(f'<article class="chapter" data-chapter="{ch.number}">{"".join(parts)}</article>', heads)

    def _lab(self, lab: Path, ch: Chapter, shift: int) -> Block:
        def hook(h: Heading, src_lvl: int, tok):
            h.level = src_lvl + shift + 1
            if src_lvl == 1:
                h.kind = "lab"
                h.toc = self.toc_ok("lab", h.level)
                tok.attrSet("class", "lab-title")
            else:
                h.toc = self.toc_ok("section", h.level)
        return self.render_doc(lab, shift=shift, chapter=ch.number, heading_hook=hook)

    def _insert_local_toc(self, body: str, heads: list[Heading], pages) -> str:
        items = [h for h in heads if h.level == 3]
        if len(items) < 4:
            return body
        rows = "".join(f'<li><a href="#{h.id}"><span class="t">{html.escape(h.text)}</span>'
                       f'<span class="pg">{self.page_label(pages, h.id)}</span></a></li>' for h in items)
        box = f'<nav class="local-toc" aria-label="In this chapter"><div class="lt-title">In this chapter</div><ol>{rows}</ol></nav>'
        m = re.search(r"</blockquote>", body)
        first_h2 = body.find("<h2")
        if m and (first_h2 < 0 or m.end() < first_h2):
            return body[:m.end()] + box + body[m.end():]
        end_h1 = body.find("</h1>")
        return body[:end_h1 + 5] + box + body[end_h1 + 5:] if end_h1 >= 0 else body

    def workbook_unit(self, ch: Chapter) -> Block | None:
        lab = self.chapter_file("lab", ch)
        if not lab:
            return None
        uid = self.unit_ids[ch.number]
        title = f"Chapter {ch.number} — {ch.short_title}"
        head = Heading(uid + "-h", title, 2, kind="chapter", toc=True, opener=True,
                       running=f"Chapter {ch.number} · {ch.short_title}")
        parts = [f'<h1 class="chapter-title" id="{uid}-h"><span class="ch-label">Chapter {ch.number}</span>'
                 f'<span class="ch-name">{html.escape(ch.short_title)}</span></h1>']
        heads = [head]
        practice = self._extract_sections(ch.path, self.p["practice_sections"])
        if practice:
            b = self.render_doc(ch.path, text=practice, chapter=ch.number, doc_id=f"{uid}-practice",
                                heading_hook=lambda h, lvl, tok: setattr(h, "toc", False))
            parts.append(f'<div class="practice"><h2 class="practice-title" id="{uid}-practice-h">'
                         f'Practice from the chapter</h2>{b.html}</div>')
            heads.append(Heading(f"{uid}-practice-h", "Practice from the chapter", 3,
                                 toc=self.p["toc_depth"] >= 3))
            heads += [h for h in b.headings]
        lb = self._lab(lab, ch, shift=1)
        parts.append(f'<div class="lab">{lb.html}</div>')
        heads += lb.headings
        if self.p["answer_space"]:
            parts.append('<section class="answer-space"><div class="as-title">Notes and answers</div>'
                         '<div class="as-lines"></div></section>')
        return Block(f'<article class="chapter workbook" id="{uid}">{"".join(parts)}</article>', heads)

    def solution_unit(self, ch: Chapter) -> Block | None:
        sol = self.chapter_file("solution", ch)
        if not sol:
            return None
        uid = self.unit_ids[ch.number]
        label = f"Chapter {ch.number} · Solutions"
        b = self.render_doc(sol, chapter=ch.number, heading_hook=self._unit_heading_hook(ch, label))
        return Block(f'<article class="chapter solutions" id="{uid}">{b.html}</article>', b.headings)

    @staticmethod
    def _extract_sections(path: Path, patterns: list[str]) -> str:
        if not patterns:
            return ""
        lines = path.read_text(encoding="utf-8").splitlines()
        pat = re.compile(rf"^(#{{2,6}})\s+(?:\d+\.\s*)?(?:{'|'.join(map(re.escape, patterns))})", re.I)
        out, i = [], 0
        while i < len(lines):
            m = pat.match(lines[i])
            if not m:
                i += 1
                continue
            depth = len(m[1])
            chunk = ["#" * 3 + lines[i][depth:]]
            i += 1
            while i < len(lines):
                h = re.match(r"^(#{1,6})\s", lines[i])
                if h and len(h[1]) <= depth:
                    break
                chunk.append(re.sub(r"^(#{4,6})", lambda mm: "#" * min(6, len(mm[1]) - depth + 3), lines[i])
                             if h else lines[i])
                i += 1
            out.append("\n".join(chunk))
        return "\n\n".join(out)

    # ---------------------------------------------------------- auto sections
    def auto_block(self, sid: str, kind: str) -> Block | None:
        sec = self.cfg["sections"][sid]
        auto = sec["auto"]
        letter = self.appendix_letters.get(sid) if kind == "appendix" else None
        name = sec.get("title", auto.title())
        title = f"Appendix {letter} — {name}" if letter else name
        anchor = f"sec-{id_slug(title)}"
        head = Heading(anchor, title, 1, kind=kind, toc=True, opener=True, verso=self.book["title"],
                       running=f"Appendix {letter} · {name}" if letter else name)
        builder = {"solutions": lambda: self._docs_by_chapter("solution"),
                   "reviews": lambda: self._docs_by_chapter("review"),
                   "visuals": self.visuals_gallery, "code": lambda: self.code_listings(sec),
                   "bibliography": self.bibliography_block, "index": self.index_block,
                   "build-info": self.build_info_block}.get(auto)
        if builder is None:
            self.issues.error(f"section {sid!r}: unknown auto type {auto!r}")
            return None
        inner = builder()
        if inner is None:
            return None
        return Block(f'<div class="{kind} section-start"{self._appendix_id(letter)}>'
                     f'<h1 class="{kind}-title" id="{anchor}">{html.escape(title)}</h1>{inner.html}</div>',
                     [head] + inner.headings)

    def _docs_by_chapter(self, key: str) -> Block | None:
        parts, heads = [], []
        for ch in self.chapters:
            if f := self.chapter_file(key, ch):
                def hook(h, lvl, tok):
                    h.level = lvl + 1
                    h.toc = lvl == 1 or self.toc_ok("doc", h.level)
                b = self.render_doc(f, shift=1, chapter=ch.number, heading_hook=hook)
                parts.append(b.html)
                heads += b.headings
        return Block("".join(parts), heads) if parts else None

    def visuals_gallery(self) -> Block:
        groups: dict[tuple[int, int], list[Path]] = {}
        for f in glob_files(["visuals/chapter-*/*"]):
            m = re.search(r"-(\d{2})-(\d{2})-", f.name)
            if m:
                groups.setdefault((int(m[1]), int(m[2])), []).append(f)
            elif f.suffix.lower() in (".svg", ".png"):
                self.issues.warn(f"visual without figure-NN-SS naming: {rel(f)}")
        by_key = {c.key: c for c in self.captions if c.kind in FIGURE_KINDS and c.chapter is not None}
        out = ['<p class="lead">Every visual asset in <code>visuals/</code>, grouped by chapter and figure '
               'number, with its editable source and where it appears. Diagrams are Mermaid '
               '(<code>.mmd</code>); plots are reproducible Python programs listed in the code appendix.</p>']
        heads, current = [], None
        for (chn, seq), files in sorted(groups.items()):
            if chn != current:
                current = chn
                ch = next((c for c in self.chapters if c.number == chn), None)
                hid = f"vis-chapter-{chn:02d}"
                name = f"Chapter {chn} figures" + (f" — {ch.short_title}" if ch else "")
                out.append(f'<h2 id="{hid}">{html.escape(name)}</h2>')
                heads.append(Heading(hid, name, 2, toc=self.toc_ok("doc", 2)))
            cap = by_key.get((chn, seq))
            stem = re.sub(r"^(figure|plot|illustration)-\d{2}-\d{2}-", "", files[0].stem)
            title = cap.title if cap else stem.replace("-", " ").capitalize()
            kind = cap.kind if cap else "Figure"
            gid = f"gallery-{chn:02d}-{seq:02d}"
            out.append(f'<div class="gallery-item"><h3 id="{gid}">{kind} {chn}.{seq:02d} — {html.escape(title)}</h3>')
            heads.append(Heading(gid, f"{kind} {chn}.{seq:02d} — {title}", 3, toc=self.toc_ok("doc", 3)))
            by_ext = {f.suffix.lower(): f for f in files}
            img = by_ext.get(".svg") or by_ext.get(".png")
            anchors = "".join(f'<span id="{self.visual_ids[rel(f)]}"></span>'
                              for f in files if rel(f) in self.visual_ids)
            out.append(anchors)
            if img:
                m = measure_svg(img) if img.suffix == ".svg" else None
                style = ""
                if m:
                    s = min(self.boxes["normal"].width / m.width_pt, 420 / m.height_pt,
                            1.0 if not m.fluid else 9e9)
                    style = f' style="width:{m.width_pt * s:.1f}pt"'
                out.append(f'<figure class="img gallery"><img src="{img.as_uri()}" alt="{html.escape(title)}"{style}></figure>')
            rows = []
            for f in sorted(files, key=lambda f: f.suffix):
                r = rel(f)
                role = {".svg": "Rendered (vector)", ".png": "Rendered (raster)", ".mmd": "Mermaid source",
                        ".py": "Plot program"}.get(f.suffix.lower(), "Asset")
                link = f"#{self.code_ids[r]}" if r in self.code_ids else self.github(r)
                rows.append(f'<tr><td>{role}</td><td><a href="{link}"><code>{html.escape(r)}</code></a></td></tr>')
            if cap:
                rows.append(f'<tr><td>Appears in</td><td><a href="#{cap.anchor}">{cap.kind} {cap.number}</a> '
                            f'in Chapter {chn}</td></tr>')
            elif img and rel(img) not in self.used_images:
                self.issues.warn(f"visual not used by any printed chapter: {rel(img)}")
            out.append(f'<div class="table-wrap"><table class="assets"><tbody>{"".join(rows)}</tbody></table></div>')
            if mmd := by_ext.get(".mmd"):
                out.append('<p class="figure-note"><em>Mermaid source:</em></p>')
                out.append(self.highlight(mmd.read_text(encoding="utf-8"), filename="x.txt", check=False))
            out.append("</div>")
        return Block("".join(out), heads)

    def code_listings(self, sec: dict) -> Block:
        max_bytes = int(sec.get("max_bytes", 12000))
        out = ['<p class="lead">Complete listings of the running project, lab helpers and figure programs '
               'as they stand in this build. Run commands from the repository root.</p>']
        heads = []
        by_dir: dict[str, list[Path]] = {}
        for f in glob_files(sec.get("files", [])):
            by_dir.setdefault(PurePosixPath(rel(f)).parent.as_posix(), []).append(f)
        for d in sorted(by_dir, key=natural_key):
            did = f"code-dir-{id_slug(d)}"
            out.append(f'<h2 id="{did}"><code>{html.escape(d)}/</code></h2>')
            heads.append(Heading(did, f"{d}/", 2, toc=self.toc_ok("doc", 2)))
            for f in sorted(by_dir[d], key=lambda f: (f.name.startswith("test_"), natural_key(f.name))):
                r = rel(f)
                size = f.stat().st_size
                if size > max_bytes:
                    out.append(f'<p class="listing-skip" id="{self.code_ids[r]}"><code>{html.escape(f.name)}</code> '
                               f'— {size / 1024:.1f} KB data file, not reproduced. '
                               f'<a href="{self.github(r)}">View it in the repository</a>.</p>')
                    continue
                out.append(f'<h3 class="listing-title" id="{self.code_ids[r]}"><code>{html.escape(r)}</code></h3>')
                heads.append(Heading(self.code_ids[r], r, 3, toc=self.toc_ok("doc", 3)))
                self._ctx["src"] = f
                out.append(self.highlight(f.read_text(encoding="utf-8"), filename=f.name, linenos=True))
        return Block("".join(out), heads)

    def chapter_anchor(self, n: int) -> str | None:
        return self.unit_ids.get(n)

    def bibliography_block(self) -> Block | None:
        used = self.bib.used()
        if not used:
            return None
        groups = [("reference", "References",
                   "Sources relied on for factual and technical claims in the chapters. Scope, caution "
                   "and verification dates for each are recorded in the source notes."),
                  ("further", "Further reading",
                   "Recommended reading that does not support a specific claim in the text."),
                  ("frontier", "Frontier sources",
                   "Time-sensitive research tracked for later chapters; not yet core instruction.")]
        out, heads = [], []
        for cat, name, lead in groups:
            ws = [w for w in used if self.bib.category(w) == cat]
            if not ws:
                continue
            hid = f"bib-{cat}"
            out.append(f'<h2 id="{hid}">{name}</h2><p class="lead">{lead}</p>')
            heads.append(Heading(hid, name, 2, toc=self.toc_ok("doc", 2)))
            out += [self.bib.entry_html(w, self.chapter_anchor) for w in ws]
        return Block("".join(out), heads)

    def index_block(self) -> Block | None:
        # Markers are collected while the body renders (back matter comes last);
        # compose() fills in the entries once page numbers are known.
        if not self.index_marks:
            self.issues.note("no @index{...} markers in the manuscript; index section omitted")
            return None
        return Block("<!--INDEX-->", [])

    def build_info_block(self) -> Block:
        rows = [("Profile", self.p["name"]), ("Edition", self.p["edition"]),
                ("Version", str(self.book.get("version", ""))), ("Mode", self.mode),
                ("Build date", self.built), ("Git commit", self.commit + (" (dirty)" if self.dirty else "")),
                ("Builder", f"bookkit {BUILDER_VERSION}"), ("Paper", self.paper.css),
                ("Figure minimum label", f"{self.layout.get('min_label_pt', 6.5)} pt")]
        table = "".join(f"<tr><th>{html.escape(k)}</th><td>{html.escape(v)}</td></tr>" for k, v in rows)
        figs = "".join(f"<tr><td><code>{html.escape(f['src'] or f['doc'])}</code></td><td>{f['layout']}</td>"
                       f"<td>{f['scale']:.2f}</td><td>{f['label_pt']:.1f} pt</td></tr>" for f in self.figures)
        issues = "".join(f"<li><strong>{lv}</strong> {html.escape(m)}</li>"
                         for (lv, m) in self.issues.items if lv != "note") or "<li>None.</li>"
        return Block(f'<div class="table-wrap"><table><tbody>{table}</tbody></table></div>'
                     f'<h2 id="build-figures">Figure layout decisions</h2><div class="table-wrap"><table>'
                     f'<thead><tr><th>Figure</th><th>Layout</th><th>Scale</th><th>Label size</th></tr></thead>'
                     f'<tbody>{figs}</tbody></table></div>'
                     f'<h2 id="build-issues">Preflight findings at render time</h2><ul>{issues}</ul>',
                     [Heading("build-figures", "Figure layout decisions", 2, toc=False),
                      Heading("build-issues", "Preflight findings at render time", 2, toc=False)])

    # ------------------------------------------------------------ front pages
    def written_span(self) -> str:
        nums = [c.number for c in self.chapters]
        if not nums:
            return "No chapters"
        return f"Chapters {nums[0]}–{nums[-1]}" if len(nums) > 1 else f"Chapter {nums[0]}"

    def cover_html(self) -> str:
        b, e = self.book, html.escape
        edition = f'<div class="cover-edition">{e(self.p["edition"])}</div>' if self.p["edition"] else ""
        if self.mode == "release":
            year = b.get("publication_date") or self.built[:4]
            foot = f'<div class="cover-release">Version {e(str(b.get("version", "")))} · {e(str(year))}</div>'
        else:
            status = f"{self.written_span()} of {len(self.planned)} written" if self.planned else self.written_span()
            foot = (f'<div class="cover-draft">Working draft · {status}<br>Version {e(str(b.get("version", "")))}'
                    f' · built {self.built} · {self.commit}{" (uncommitted changes)" if self.dirty else ""}</div>')
        return (f'<section class="cover"><div class="cover-band"></div>'
                f'<div class="cover-title">{e(b["title"])}</div>'
                f'<div class="cover-subtitle">{e(b.get("subtitle", ""))}</div>{edition}'
                f'<div class="cover-author">{e(b.get("author", ""))}</div>{foot}</section>')

    def colophon_html(self) -> str:
        b, e = self.book, html.escape
        repo = (f'<p>Source repository and runnable code: <a href="{self.repo_url}">{e(self.repo_url)}</a></p>'
                if self.repo_url else "")
        status = ("This is a working draft generated from the book's Markdown sources; later chapters are "
                  "written in syllabus order and appear in later builds." if self.mode == "draft" else
                  "Generated from the book's Markdown sources.")
        companions = {"companion": "Worked solutions are published in the separate solutions companion. ",
                      "appendix": "", "none": ""}[self.p["solutions"]]
        return (f'<section class="colophon"><p><strong>{e(b["title"])}</strong><br>{e(b.get("subtitle", ""))}</p>'
                f'<p>{e(b.get("author", ""))}</p>'
                f'<p>{e(self.p["edition"])}, version {e(str(b.get("version", "")))}. {status} {companions}'
                f'Links to files that are not printed in this edition open the source repository.</p>'
                f'<table class="build-info"><tbody>'
                f'<tr><th>Build date</th><td>{self.built}</td></tr>'
                f'<tr><th>Edition / profile</th><td>{e(self.p["edition"])} ({e(self.p["name"])})</td></tr>'
                f'<tr><th>Version</th><td>{e(str(b.get("version", "")))} ({self.mode})</td></tr>'
                f'<tr><th>Git commit</th><td><code>{self.commit}</code>{" with uncommitted changes" if self.dirty else ""}</td></tr>'
                f'<tr><th>Chapters written</th><td>{len(self.chapters)}'
                f'{f" of {len(self.planned)} planned" if self.planned else ""}</td></tr>'
                f'<tr><th>Builder</th><td>bookkit {BUILDER_VERSION}</td></tr></tbody></table>{repo}</section>')

    def page_label(self, pages, anchor: str) -> str:
        if not pages or anchor not in pages.get("pages", {}):
            return ""
        return self.label_for(pages["pages"][anchor], pages.get("body_start"))

    def label_for(self, page: int, body_start: int | None) -> str:
        if self.p["page_numbers"] == "roman-front" and body_start:
            return roman(page) if page < body_start else str(page - body_start + 1)
        return str(page)

    def contents_block(self, heads: list[Heading], pages) -> Block:
        rows = []
        for h in heads:
            if not h.toc:
                continue
            depth = max(1, min(h.level, 4))
            cls = f"toc-l{depth}" + (" toc-part" if h.kind == "part" else "") + \
                  (" toc-lab" if h.kind == "lab" else "")
            rows.append(f'<li class="{cls}"><a href="#{h.id}"><span class="t">{html.escape(h.text)}</span>'
                        f'<span class="dots"></span><span class="pg">{self.page_label(pages, h.id)}</span></a></li>')
        return Block(f'<section class="toc-page"><h1 id="contents" class="front-title">Contents</h1>'
                     f'<nav aria-label="Contents"><ul class="toc">{"".join(rows)}</ul></nav></section>',
                     [Heading("contents", "Contents", 1, kind="front", opener=True, running="Contents",
                              verso=self.book["title"])])

    def list_block(self, kinds: tuple[str, ...], title: str, hid: str, pages) -> Block | None:
        caps = sorted((c for c in self.captions if c.kind in kinds), key=lambda c: (c.key, c.order))
        if not caps:
            return None
        rows = "".join(
            f'<li class="toc-l2"><a href="#{c.anchor}"><span class="t"><span class="num">{c.number}</span>'
            f'{html.escape(c.title)}</span><span class="dots"></span>'
            f'<span class="pg">{self.page_label(pages, c.anchor)}</span></a></li>' for c in caps)
        return Block(f'<section class="toc-page list-of"><h1 id="{hid}" class="front-title">{title}</h1>'
                     f'<ul class="toc">{rows}</ul></section>',
                     [Heading(hid, title, 1, kind="front", toc=True, opener=True, running=title,
                              verso=self.book["title"])])

    # --------------------------------------------------------------- assembly
    def build_body(self, pages) -> list[Block]:
        self._reset()
        blocks = [b for sid in self.front_ids if (b := self.section_block(sid, "front"))]
        placed = set()
        for part in self.parts:
            nums = [n for m in part["modules"] for n, _ in m["chapters"]]
            units = [self._unit(c, pages) for c in self.chapters if c.number in nums]
            units = [u for u in units if u]
            if not units:
                continue
            blocks.append(self.part_block(part))
            blocks += units
            placed |= set(nums)
        for ch in self.chapters:
            if ch.number not in placed:
                self.issues.warn(f"Chapter {ch.number} is not listed in the syllabus; placed after the Parts")
                if u := self._unit(ch, pages):
                    blocks.append(u)
        # The bibliography and index summarise every other document (citation contexts,
        # index markers), so they render last and are then put back in their places.
        deferred: list[tuple[int, str, str]] = []
        for kind, ids in (("appendix", self.appendix_ids), ("back", self.back_ids)):
            for sid in ids:
                if self.cfg["sections"][sid].get("auto") in ("bibliography", "index"):
                    deferred.append((len(blocks), sid, kind))
                    blocks.append(None)
                elif b := self.section_block(sid, kind):
                    blocks.append(b)
        for pos, sid, kind in deferred:
            blocks[pos] = self.section_block(sid, kind)
        return [b for b in blocks if b]

    def _unit(self, ch: Chapter, pages) -> Block | None:
        body = self.p["body"]
        if body == "chapters":
            return self.chapter_block(ch, pages)
        if body == "labs":
            return self.workbook_unit(ch)
        return self.solution_unit(ch)

    def compose(self, pages, vendor: dict[str, str]) -> tuple[str, list[Heading]]:
        body = self.build_body(pages)
        lof = self.list_block(FIGURE_KINDS, "List of figures", "list-of-figures", pages)
        lot = self.list_block(("Table",), "List of tables", "list-of-tables", pages)
        extra = [b for b in (lof, lot) if b]
        body_heads = [h for b in body for h in b.headings]
        toc = self.contents_block([h for b in extra for h in b.headings] + body_heads, pages)
        ordered = [toc] + extra + body
        headings = [h for b in ordered for h in b.headings]
        doc_html = "".join(b.html for b in ordered)
        if "<!--INDEX-->" in doc_html:
            doc_html, idx_heads = self._fill_index(doc_html, pages)
            headings += idx_heads
        doc_html = self._resolve_assets(doc_html)
        doc_html = self.crossref(doc_html, pages)
        doc_html = self._check_links(doc_html)
        # Headings link to themselves so Chromium emits a named destination for each;
        # those give exact page positions for the Contents, bookmarks and running heads.
        doc_html = re.sub(r'<(h[1-6])\b([^>]*?\bid="([^"]+)"[^>]*)>(.*?)</\1>',
                          lambda m: m[0] if "<a " in m[4] else
                          f'<{m[1]}{m[2]}><a class="hlink" href="#{m[3]}">{m[4]}</a></{m[1]}>',
                          doc_html, flags=re.S)
        pyg = HtmlFormatter(style=PYGMENTS_STYLE).get_style_defs(".hl")
        mermaid = (f'<script src="{vendor["mermaid_js"]}"></script>'
                   if 'class="mermaid"' in doc_html else "")
        page = (f"{self.html_head(vendor)}<style>{pyg}</style></head><body class=\"profile-{self.p['name']}\">"
                f"{self.colophon_html()}{doc_html}"
                f'<script>window.BOOK_LAYOUT = {json.dumps(self.js_layout())};</script>'
                f'<script src="{vendor["katex_js"]}"></script>{mermaid}'
                f"<script>{READY_JS}</script></body></html>")
        return page, headings

    def _fill_index(self, doc_html: str, pages) -> tuple[str, list[Heading]]:
        terms: dict[str, list[dict]] = {}
        for m in self.index_marks:
            terms.setdefault(m["term"], []).append(m)
        rows = []
        for term in sorted(terms, key=str.casefold):
            refs = ", ".join(f'<a href="#{m["anchor"]}">{self.page_label(pages, m["anchor"]) or "•"}</a>'
                             for m in terms[term])
            main, _, sub = term.partition("|")
            label = f'{html.escape(main)}{", " + html.escape(sub) if sub else ""}'
            rows.append(f'<li><span class="ix-term">{label}</span> {refs}</li>')
        return doc_html.replace("<!--INDEX-->", f'<ul class="index">{"".join(rows)}</ul>'), []

    def _resolve_assets(self, doc_html: str) -> str:
        by_asset = {c.asset: c.anchor for c in self.captions if c.asset}

        def fix(m):
            path = m[1]
            if path in by_asset:
                return f'href="#{by_asset[path]}"'
            if path in self.visual_ids:
                return f'href="#{self.visual_ids[path]}"'
            return f'href="{self.github(path)}"'
        return re.sub(r'href="#asset:([^"]+)"', fix, doc_html)

    def _check_links(self, doc_html: str) -> str:
        ids = set(re.findall(r'\bid="([^"]+)"', doc_html))

        def fix(m):
            target = m[1]
            if target in ids:
                return m[0]
            base = target.split("--")[0]
            if base in ids:
                self.issues.warn(f"missing heading anchor #{target.split('--', 1)[1]} in {base}; "
                                 f"linking to the document instead")
                return f'href="#{base}"'
            self.issues.error(f"unresolved internal link #{target}")
            return m[0]
        return re.sub(r'href="#([^"]+)"', fix, doc_html)

    # ---------------------------------------------------------- cross-refs
    XREF = re.compile(r"(?<![\w.])(Chapter|Figure|Table|Appendix)\s+(\d+(?:\.\d+)?|[A-Z])\b(?![.\d]\d)")

    def crossref(self, doc_html: str, pages) -> str:
        """Link plain-text Chapter/Figure/Table/Appendix references; add page numbers across documents."""
        caps = {}
        for c in self.captions:
            caps.setdefault(("Table" if c.kind == "Table" else "Figure", c.key), c)
        letters = {v: f"appendix-{v.lower()}" for v in self.appendix_letters.values()}
        written = {c.number for c in self.chapters}
        mode = self.p["xref_pages"]
        out, skip, doc_stack, cap_link = [], [], [], None
        skip_tags = {"a", "code", "pre", "h1", "h2", "h3", "h4", "h5", "h6", "figcaption", "script",
                     "style", "nav", "title"}
        for part in re.split(r"(<[^>]+>)", doc_html):
            if part.startswith("<"):
                m = re.match(r"<(/?)([a-zA-Z0-9]+)([^>]*)>", part)
                if m:
                    closing, tag, attrs = m[1] == "/", m[2].lower(), m[3]
                    if tag == "section":
                        if closing:
                            doc_stack and doc_stack.pop()
                        else:
                            dm = re.search(r'class="doc" id="([^"]+)"', attrs)
                            doc_stack.append(dm[1] if dm else None)
                    key = tag
                    if tag == "p" and 'class="caption' in attrs:
                        key = "p.caption"
                    if not closing and (key in skip_tags or key == "p.caption"):
                        skip.append(key)
                        if tag == "a" and (hm := re.search(r'href="#(cap-[^"]+)"', attrs)):
                            cap_link = hm[1]
                    elif closing and skip and skip[-1] in (tag, "p.caption" if tag == "p" else None):
                        popped = skip.pop()
                        if popped == "a" and cap_link:
                            out.append(part)
                            out.append(self._page_suffix(cap_link, doc_stack, pages, mode))
                            cap_link = None
                            continue
                out.append(part)
                continue
            if skip or not part.strip():
                out.append(part)
                continue

            def link(m):
                kind, ref = m[1], m[2]
                target = None
                if kind == "Chapter" and ref.isdigit():
                    n = int(ref)
                    if self.planned and n > max(self.planned):
                        self.issues.error(f"reference to nonexistent Chapter {n}")
                    target = self.unit_ids.get(n)
                elif kind in ("Figure", "Table") and "." in ref:
                    a, b = ref.split(".")
                    c = caps.get((kind, (int(a), int(b))))
                    if c:
                        return (f'<a class="xref" href="#{c.anchor}">{m[0]}</a>'
                                + self._page_suffix(c.anchor, doc_stack, pages, mode))
                    if int(a) in written and self.p["body"] == "chapters":
                        self.issues.warn(f"reference to missing {kind} {ref} "
                                         f"(in {doc_stack[-1] if doc_stack else 'front matter'})")
                elif kind == "Appendix" and ref in letters:
                    target = letters[ref]
                return f'<a class="xref" href="#{target}">{m[0]}</a>' if target else m[0]
            out.append(self.XREF.sub(link, part))
        return "".join(out)


    def _page_suffix(self, anchor: str, doc_stack, pages, mode) -> str:
        if mode == "none" or not pages:
            return ""
        cap = next((c for c in self.captions if c.anchor == anchor), None)
        here = doc_stack[-1] if doc_stack else None
        if here is None:                     # Contents, lists, gallery: pages shown elsewhere
            return ""
        if mode == "cross-document" and cap and cap.doc_id == here:
            return ""
        label = self.page_label(pages, anchor)
        return f'<span class="pref"> (p.&#8239;{label})</span>' if label else ""

    # ------------------------------------------------------------------ misc
    def js_layout(self) -> dict:
        return {"contentWidthPt": self.paper.width_pt - 2 * MARGIN_PT,
                "viewportWidthPt": self.paper.width_pt - 2 * PAGE_SIDE_PT,
                "contentHeightPt": self.paper.height_pt - 2 * MARGIN_PT,
                "landscapeWidthPt": self.boxes["landscape"].width}

    def html_head(self, vendor: dict[str, str], extra_css: str = "") -> str:
        p = self.paper
        size = f"{p.width_pt:.2f}pt {p.height_pt:.2f}pt"
        return (f"<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\">"
                f"<title>{html.escape(self.book['title'])} — {html.escape(self.p['edition'])}</title>"
                f'<link rel="stylesheet" href="{vendor["katex_css"]}">'
                f'<link rel="stylesheet" href="{CSS.as_uri()}">'
                f"<style>@page {{ size: {size}; }} @page landscape {{ size: {size.split()[1]} {size.split()[0]}; }}"
                f":root {{ --landscape-w: {self.boxes['landscape'].width:.1f}pt;"
                f" --content-h: {self.paper.height_pt - 2 * MARGIN_PT:.1f}pt;"
                f" --landscape-h: {self.paper.width_pt - 2 * LANDSCAPE_MARGIN_V_PT:.1f}pt; }}{extra_css}</style>")

    def cover_document(self, vendor: dict[str, str]) -> str:
        return (f"{self.html_head(vendor, '@page { margin: 0; }')}</head><body class=\"cover-doc\">"
                f"{self.cover_html()}<script>window.__BOOK_READY = true;</script></body></html>")


READY_JS = r"""
(async () => {
  const errors = [], report = [];
  const L = window.BOOK_LAYOUT, PX = 96 / 72;
  try {
    if (window.katex) {
      document.querySelectorAll('.math').forEach(el => {
        try { katex.render(el.textContent, el, {displayMode: el.classList.contains('display'), throwOnError: false}); }
        catch (e) { errors.push('katex: ' + e); }
      });
    } else if (document.querySelector('.math')) errors.push('KaTeX did not load');
    if (window.mermaid) {
      mermaid.initialize({startOnLoad: false, theme: 'default', securityLevel: 'strict'});
      for (const n of document.querySelectorAll('pre.mermaid')) {
        try { await mermaid.run({nodes: [n]}); } catch (e) { errors.push('mermaid: ' + e); }
      }
    }
  } catch (e) { errors.push(String(e)); }
  await document.fonts.ready;
  await Promise.all([...document.images].map(img => img.complete ? null :
    new Promise(r => { img.onload = img.onerror = r; })));
  // Wide tables that overflow the text block move to a landscape page.
  const contentW = L.contentWidthPt * PX, contentH = L.contentHeightPt * PX;
  document.querySelectorAll('.table-wrap').forEach((w, i) => {
    const t = w.querySelector('table');
    if (!t) return;
    if (!w.classList.contains('layout-landscape') && t.scrollWidth > w.clientWidth + 2) {
      w.classList.add('layout-landscape');
    }
    if (t.scrollWidth > w.clientWidth + 2) {
      report.push('table overflows even on a landscape page: "' + (t.innerText || '').slice(0, 60).replace(/\s+/g, ' ') + '"');
    }
    for (const tr of t.rows) {
      if (tr.getBoundingClientRect().height > contentH * 0.6) {
        report.push('very tall table row (' + Math.round(tr.getBoundingClientRect().height / PX) + 'pt): "' +
                    (tr.innerText || '').slice(0, 60).replace(/\s+/g, ' ') + '"');
      }
    }
  });
  window.__BOOK_ERRORS = errors;
  window.__BOOK_REPORT = report;
  window.__BOOK_READY = true;
})();
"""
