---
type: runbook
reader: cc
title: The dataset update — BUILD stage 4b — instruction for Claude Code
last_reviewed: 2026-10-03
---

# The dataset update — BUILD stage 4b — runbook for Claude Code

*(Stage 4b of `BUILD.md`, moved here word for word on 2026-10-03 so that file fits its cap. `documentation/datasets.md` is the design.)*

**The same set difference as stage 4, over a dataset instead of a ledger** (`documentation/datasets.md`, T7). A raw record is a candidate for Data Centres if it carries `infra.store` or its title or `hub_line` names a data centre; it stays unconsidered until its slug is in `outputs/datasets/data-centres/considered.txt`. From `scripts/.workroot/`:

```bash
python scripts/dataset-scan.py                                   # the work order, by place
python scripts/dataset-scan.py --packet data-centres {PLACE}     # --parts N past ~30 records
```

1. **Read the packet** — each record beside the current rows of every country it names — and **write `prep/dc-evidence/t7/{PLACE}/decisions.json`**: an outcome for every slug under `considered`, and under `rows` the edits, new facilities and sources they rest on, each with a plain-English `summary` for the page's Recent changes. The format and the rules are in `scripts/dataset-scan.py`'s docstring; the reading rules are T6's (`scripts/dataset-evidence.py`).
2. **Decide per record** — *modifies a row* (something newer or more specific than the row holds), *adds a facility* (one the dataset lacks, checked against every row, not only the country's), or *nothing* (the default: most records restate what a row already says). A record that confirms a row joins it through `add_slugs`, so the row cites the catalogue.
3. **Apply**: `python scripts/dataset-scan.py --apply data-centres {PLACE} --dry-run` until clean, then without `--dry-run`. It writes the master, logs each change at the top of `logs/dataset-updates.csv` with its sources, and marks every accounted slug considered.

**A night's arrivals are one packet**: `--packet data-centres ALL`, applied as `--apply data-centres ALL`. The backlog was read place by place. Commit the master, `considered.txt`, `url-audit.csv`, `claims-to-source.csv` and the log. RENDER mints the dated edition.
