# Reader layout repair — Chapters 1–24

**Date:** 2026-10-14. **Baseline:** Chapter 24 checkpoint `d0e4b9a`, 438-page reader build with zero errors and eight warnings. This is a print-layout repair, not a chapter-content or experiment remediation pass.

## Changes

- Added opt-in `layout.compact_documents` for six source documents: Chapter 1 lab, Chapter 2, Chapter 4, Chapter 11 lab, Chapter 13 lab and Chapter 14. The renderer adds a spacing class only to these documents. Paragraph, heading and list gaps are smaller; body/code font sizes, line heights, figure-label floors and chapter/lab page starts remain unchanged. Chapter 13's lab has a slightly tighter paragraph/heading override to keep its submission section on the preceding page.
- Reformatted Chapter 13 lab and V3 README PowerShell commands using task-specific output/index variables. Expanded command arguments, output locations and runner behavior are identical. No experiment was rerun or replaced to perform this repair.
- Kept nearly-empty-page and code-width checks enabled. Added two renderer regressions: compact documents must preserve complete HTML content, headings, link destinations and figure decisions; other documents must remain unaffected. Documented the spacing option in the book-build guide.

## Verification

- **Reader:** 432 pages, front matter i–xii, body 1–420; 24 of 57 chapters, 55 figures, 13 numbered tables, 95 works, 662 bookmarks. **Zero errors and zero warnings.** All 29 text-layer checks pass, and internal links/destinations resolve. The remaining no-index message is informational: no index-term markers have been authored.
- **Preflight:** 24 chapters, 68 numbered captions, zero errors/warnings.
- **Tests:** 24 book-tool tests and 17 common/evidence tests pass. Renderer comparisons preserve all text/markup except the spacing class, including the six affected documents' headings and figure decisions. Chapter 24 remains outside the spacing opt-in.
- **Commands:** Both affected documents' PowerShell fences parse without errors. Static argument expansion matches the original runner invocations exactly; no displayed line exceeds the widest 111-column measure.
- **Visual QA:** All six affected endings were rendered and inspected at physical pages 27, 39, 65, 143, 165 and 173. Chapter 13's submission section and long corruption probe fit legibly on page 165. V3's command block was inspected at page 377. Source text was retained; no font shrinking, clipping, hidden text or warning suppression was used.
- **Preservation:** Chapter manuscripts, executable project implementations, governed sources, labels, vector/model snapshots and historical experiment records remain unchanged. Only command presentation changes in the Chapter 13 lab and V3 README. The earlier author/audit reports remain historical reports of their own builds.

The six former one-to-five-line spill pages have been absorbed into preceding pages. Chapter 25 remains unstarted.
