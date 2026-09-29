"""Canonical, deduplicated bibliography built from the manuscript's own registers.

Sources of metadata, in priority order:
  1. book/bibliography.toml overrides (grouping, fuller names, venues, DOIs);
  2. reference registers (REFERENCES.md): "Authors, [Title](url), Year";
  3. reading/frontier registers: "[Title](url), Authors, Year".
Works are keyed by DOI, then arXiv identifier, then canonical URL.
Citations are recorded while documents render, with the context in which
they occur, so the bibliography can separate References, Further reading
and Frontier sources.
"""

from __future__ import annotations

import html
import re
import tomllib
from dataclasses import dataclass, field

from .common import ROOT, Issues, id_slug, short_id

LINK = re.compile(r"\[((?:[^\[\]]|\[[^\]]*\])+)\]\((https?://[^)\s]+)\)")
YEAR = re.compile(r"\b(1[89]\d\d|20\d\d)\b")


def canon_url(u: str) -> str:
    u = u.strip().replace("http://", "https://", 1)
    u = u.split("#", 1)[0]
    if m := re.match(r"https://(?:www\.)?arxiv\.org/(?:abs|pdf)/(\d{4}\.\d{4,5})(?:v\d+)?", u):
        return f"arxiv:{m[1]}"
    if m := re.match(r"https://(?:dx\.)?doi\.org/(10\..+)$", u):
        return "doi:" + m[1].lower()
    m = re.match(r"(https://)([^/]+)(.*)$", u)
    if m:
        u = m[1] + m[2].lower() + m[3]
    return u.rstrip("/")


def clean_title(t: str) -> str:
    t = re.sub(r"[*_`]", "", t).strip()
    return re.sub(r"\s+", " ", t)


def cite_label(authors: str) -> str:
    a = re.sub(r"\(.*?\)", "", authors)
    a = re.sub(r"\s+and\s+", " & ", a).strip(" ,;")
    return re.sub(r"\s+", " ", a)


@dataclass
class Work:
    key: str
    authors: str
    cite: str
    year: str
    title: str
    venue: str = ""
    url: str = ""
    doi: str = ""
    cite_text: str = ""
    suffix: str = ""
    urls: set[str] = field(default_factory=set)
    contexts: set[str] = field(default_factory=set)
    chapters: set[int] = field(default_factory=set)

    @property
    def anchor(self) -> str:
        return short_id("bib-" + id_slug(f"{self.cite}-{self.year}{self.suffix}-{self.title}"), 60)

    @property
    def arxiv(self) -> str:
        return self.key[6:] if self.key.startswith("arxiv:") else ""

    def in_text(self) -> str:
        if self.cite_text:
            return self.cite_text
        return f"{self.cite}, {self.year}{self.suffix}"


class Bibliography:
    def __init__(self, sources: dict, issues: Issues):
        self.issues = issues
        self.works: dict[str, Work] = {}
        self.overrides: list[tuple[list[str], dict]] = []
        self.url_map: dict[str, str] = {}          # canonical url -> work key
        path = ROOT / sources.get("bibliography", "book/bibliography.toml")
        if path.exists():
            for w in tomllib.loads(path.read_text(encoding="utf-8")).get("work", []):
                self.overrides.append(([canon_url(m) for m in w.get("match", [])], w))
        registers = ([(p, "reference") for p in sources.get("reference_registers", [])]
                     + [(p, "further") for p in sources.get("reading_registers", [])]
                     + [(p, "frontier") for p in sources.get("frontier_registers", [])])
        for rpath, _kind in registers:
            p = ROOT / rpath
            if not p.exists():
                issues.error(f"bibliography register missing: {rpath}")
                continue
            for line in p.read_text(encoding="utf-8").splitlines():
                if line.startswith("|") and "](http" in line:
                    self._parse_row(line)
        self._disambiguate()

    # -------------------------------------------------------------- parsing
    def _override_for(self, canon: str) -> tuple[str, dict] | None:
        best = None
        for prefixes, data in self.overrides:
            for pre in prefixes:
                if canon == pre or canon.startswith(pre.rstrip("/") + "/") or (
                        pre.endswith("/") and canon.startswith(pre)):
                    if best is None or len(pre) > len(best[0]):
                        best = (pre, data)
        return best

    def _parse_row(self, line: str):
        cells = [c.strip() for c in re.split(r"(?<!\\)\|", line.strip().strip("|"))]
        cell = next((c for c in cells if LINK.search(c)), None)
        if not cell:
            return
        links = LINK.findall(cell)
        plain = LINK.sub("\x00", cell)
        years = YEAR.findall(plain)
        year = years[-1] if years else "n.d."
        if cell.lstrip().startswith("["):                 # [Title](url), Authors, Year
            tail = re.sub(r"\(.*?\)", "", plain.split("\x00")[-1])   # drop notes like "(first submitted 2016)"
            tail = YEAR.split(tail)[0] if YEAR.search(tail) else tail
            authors = tail.strip(" ,;")                                # keep the period of "et al."
            venue = ""
        else:                                            # Authors, [Title](url), Venue Year
            authors = plain.split("\x00")[0].strip(" ,;")
            tail = plain.split("\x00")[-1]
            venue = YEAR.sub("", tail).strip(" ,;.")
            if len(venue.split()) > 4 or not re.fullmatch(r"[A-Za-z][\w .&-]*", venue or "x"):
                venue = ""
        for text, url in links:
            self._add(url, authors=authors, year=year, title=clean_title(text), venue=venue)

    def _add(self, url: str, **meta) -> Work:
        canon = canon_url(url)
        ov = self._override_for(canon)
        if ov:
            pre, data = ov
            key = f"work:{canon_url(data['match'][0])}"      # one work per override entry
            if key not in self.works:
                authors = data.get("authors", meta.get("authors", ""))
                self.works[key] = Work(
                    key=key, authors=authors, cite=data.get("cite", cite_label(authors)),
                    year=str(data.get("year", meta.get("year", "n.d."))),
                    title=data.get("title", meta.get("title", "")), venue=data.get("venue", ""),
                    url=data.get("url", url), doi=data.get("doi", ""),
                    cite_text=data.get("cite_text", ""))
            if pre.startswith("doi:") and not self.works[key].doi:
                self.works[key].doi = pre[4:]
        else:
            key = canon
            if key not in self.works:
                authors = meta.get("authors", "") or "Anonymous"
                self.works[key] = Work(key=key, authors=authors, cite=cite_label(authors),
                                       year=meta.get("year", "n.d."), title=meta.get("title", url),
                                       venue=meta.get("venue", ""), url=url,
                                       doi=canon[4:] if canon.startswith("doi:") else "")
        self.works[key].urls.add(canon)
        self.url_map[canon] = key
        return self.works[key]

    def _disambiguate(self):
        groups: dict[tuple[str, str], list[Work]] = {}
        for w in self.works.values():
            if not w.cite_text:
                groups.setdefault((w.cite.casefold(), w.year), []).append(w)
        for ws in groups.values():
            if len(ws) > 1:
                for i, w in enumerate(sorted(ws, key=lambda w: w.title.casefold())):
                    w.suffix = "abcdefghijklmnopqrstuvwxyz"[i]

    # ------------------------------------------------------------- lookups
    def lookup(self, url: str) -> Work | None:
        canon = canon_url(url)
        if canon in self.url_map:
            return self.works[self.url_map[canon]]
        ov = self._override_for(canon)
        if ov:                          # a new page of a grouped work (e.g. another IR-book section)
            return self._add(url)
        return None

    def record(self, work: Work, context: str, chapter: int | None):
        work.contexts.add(context)
        if chapter is not None:
            work.chapters.add(chapter)

    def reset_usage(self):
        for w in self.works.values():
            w.contexts.clear()
            w.chapters.clear()

    def citation_html(self, work: Work) -> str:
        return f'<a class="cite" href="#{work.anchor}">({html.escape(work.in_text())})</a>'

    # --------------------------------------------------------------- output
    def used(self) -> list[Work]:
        return sorted((w for w in self.works.values() if w.contexts),
                      key=lambda w: (w.authors.casefold(), w.year, w.suffix, w.title.casefold()))

    @staticmethod
    def category(w: Work) -> str:
        if "reference" in w.contexts:
            return "reference"
        if "further" in w.contexts:
            return "further"
        return "frontier"

    def entry_html(self, w: Work, chapter_anchor) -> str:
        e = html.escape
        title = e(w.title)
        title_end = "" if title.endswith(("?", "!", ".")) else "."
        parts = [f'<span class="bib-authors">{e(w.authors)}</span> ({e(w.year)}{w.suffix}). '
                 f'<em>{title}</em>{title_end}']
        if w.venue:
            parts.append(f" {e(w.venue)}.")
        if w.doi:
            parts.append(f' <a href="https://doi.org/{e(w.doi)}">https://doi.org/{e(w.doi)}</a>')
        elif w.arxiv:
            parts.append(f' <a href="https://arxiv.org/abs/{w.arxiv}">arXiv:{w.arxiv}</a>')
        elif w.url:
            shown = re.sub(r"^https?://", "", w.url).rstrip("/")
            parts.append(f' <a href="{e(w.url)}">{e(shown)}</a>')
        if w.chapters:
            links = ", ".join(
                (f'<a href="#{chapter_anchor(n)}">{n}</a>' if chapter_anchor(n) else str(n))
                for n in sorted(w.chapters))
            word = "Chapter" if len(w.chapters) == 1 else "Chapters"
            parts.append(f' <span class="bib-cited">Cited in {word} {links}.</span>')
        return f'<p class="bib-entry" id="{w.anchor}">{"".join(parts)}</p>'
