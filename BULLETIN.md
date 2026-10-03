---
type: runbook
reader: cc
title: The bulletin — BUILD stage 7 — instruction for Claude Code
last_reviewed: 2026-10-03
---

# The bulletin — BUILD stage 7 — runbook for Claude Code

*(Stage 7 of `BUILD.md`, moved here word for word on 2026-10-03 so that file fits its cap. `BULLETIN-TOPUP.md` is the same stage run alone at midday; `RENDER.md` → *The bulletin* publishes it.)*

One document over the newest day or two of publication: `outputs/bulletins/corpus-bulletin.md`, published at `/bulletin/`. Design note: `documentation/bulletin.md`. **This stage can also run on its own at midday** — `BULLETIN-TOPUP.md` is that run. Its only precondition is stage 2.

```bash
python scripts/bulletin.py --scan          # the window, and which items still need a summary
```

For **each** item in the work order, read it — `raw/{year}/{slug}.md` from `scripts/.workroot/`, `hub_line` first, body only where the line is not enough — and write one to three sentences:

```bash
python scripts/bulletin.py --write {slug} --text "…"
python scripts/bulletin.py --assemble      # then commit outputs/bulletins/
```

- **The window is publication, not acquisition**: an item is in when its `published` date is today or yesterday — **today alone from 18:00**. **An empty window is a finished bulletin**; `--assemble` writes the document saying the window was empty and why.
- **A summary is written once and kept** in `summaries.json`; `--scan` asks only for what is not in it.
- **`--assemble` stops rather than publishing a gap**: an item in the window with no summary fails the command and names the slugs.
- **Everything in a summary is sourced by construction** — each entry opens with the item's title linked to the publisher's record. That does not license a fact the item does not carry, and **a verbatim sentence lifted from the body is a register failure**.
- **Detail sits in one place**: an item carrying five topics is summarised once and cross-referenced from the other four.
- **The sections are `lookups/taxonomy.csv`'s order and labels**, Level-1 groups with Level-2 sections.
- **A sweep that published nothing into the window has still updated the bulletin**; the run reports `checked` rather than `written`.
