# Current Focus

**Sprint:** Session memory — disk is memory, sessions are disposable. As of 2026-08-14, `_vincent` and `_williams` exist; this sprint installs the no-one-did-it context pattern so `/clear` can replace slow auto-compact.

This file is orientation only. Do not start unfinished items unless the user says 继续 / resume / 进度, or the request matches a listed item.

## Outstanding work

1. **Use the new session memory.** After `/clear` or a new window, read this file (already injected) and the latest `Handoff:` if any. Do not re-read either whole book.
2. **`_williams` is ready to use.** Canonical method: `the-craft-of-research/derived/actionable-principles.md`. Claude agent: `.claude/agents/williams.md` (invoke as `_williams` or `williams`). Load only the AP sections for the current stage.
3. **`_vincent` is ready to use.** Canonical method: `beyond-feelings/derived/actionable-principles.md`. Claude agent: `.claude/agents/vincent.md`. Same rule: no full-handbook dump unless a full audit is requested.

## How this sprint resumes

- Unrelated small questions: answer them. Do not open the backlog.
- Continue research or judgment work: pick the matching agent and the smallest AP set.
- At a milestone or ~70% context: update this file, end with `Handoff:`, then `/clear`.
- Keep this file short. The SessionStart hook injects it (max 4000 chars) on startup, resume, clear, and compact.

## Chinese translation — 2026-10-05 · completed

- Full translations are in `beyond-feelings-zh-CN/` and `the-craft-of-research-zh-CN/`; originals are unchanged. All 63 numbered files and 5 derived notes are complete.
- Each directory has `README.md`, `阅读版.html`, combined Markdown, `notes.html`, image explanations, `translation-review.md` and durable `review/` records.
- Chapter self-review, independent reviews of selected chapters, and independent review of all derived notes are complete; discovered issues were corrected. Source gaps and internal conflicts remain explicitly marked.
- Final structural validation passed: 101 source-file counterparts, 31 image copies, 134 footnotes and 178 principle IDs. Reading layout, tables, chapter filtering and jumps were checked in Safari.
- Rebuild: `python3 scripts/build-chinese-editions.py`; verify: `python3 scripts/validate-chinese-editions.py`. Build requires Pandoc. Checks report structure, not semantic correctness.

Handoff: Translation request is complete. Start from either Chinese README. For source defects, read its `translation-review.md`; do not invent missing text or load either whole original book. No translation backlog remains.
