# think-framework — project memory

Claude loads this via `CLAUDE.md`. Keep this file short.

## Session memory

The conversation is disposable. Durable state lives on disk:

- `.claude/state/current-focus.md` — sprint snapshot (SessionStart injects up to 4000 chars on startup, resume, `/clear`, and compact).
- Artifact `Handoff:` blocks — what the next session should read and do.

`current-focus.md` is a map, not a work order. Do not execute the backlog unless the user says 继续 / resume / 进度, or the request matches a listed item.

When context is around 70%, or a milestone is done: update `current-focus.md`, end with `Handoff:`, then `/clear` or start a new session. Prefer `/clear` over waiting for compact.

Do not read either whole book into a session. Use the derived handbooks, and only the sections the current stage needs.

## Agents

- `_vincent` / `vincent` — *Beyond Feelings*. Method: `beyond-feelings/derived/actionable-principles.md`.
- `_williams` / `williams` — *The Craft of Research*. Method: `the-craft-of-research/derived/actionable-principles.md`.

Do not mix the two methods.

## Substantial output footer

```text
Owner:
Purpose:
Assumptions:
Open questions:
Handoff:
```
