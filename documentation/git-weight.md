---
type: decision
reader: cc
title: git-weight.md — what leaves git so a cloud run clones less (R173)
date: 2026-11-26
status: decided by CC; the move is housekeeping job 91
---

# Git weight

## Measured, 26 November 2026

- **260,267 tracked files, 1,130 MB of them in the working tree.** `maturity/` holds 249,796 files and 540 MB; `site/` 1,164 files and 267 MB; `outputs/` 7,821 files and 144 MB.
- **`.git` is 6.7 GB on this laptop**: 1.80 GB packed and 4.89 GB in 455,502 loose objects, 10,631 commits.
- **A clean clone from GitHub takes five minutes**: 141 seconds to fetch a 2.67 GB pack, then 159 to check out 260,267 files (about 1.1 GB). A cloud run that starts fresh pays the fetch every time.

## Where the files are

Inside `maturity/`, by kind:

| Kind | Files | MB | Read by |
|---|---|---|---|
| `evidence/{ISO3}/facts/{n}.json`, one per drafted part | 145,745 | 62 | `study-stage.py` when it compiles a country, and the arrivals fan |
| `search/` and the dated `search-YYYY-MM-DD/` snapshots: leads, decisions, fetched | 51,398 | 59 | the rebuild's searcher, that night only |
| `_batch/`, chiefly the night's arrivals | 15,344 | 32 | the night's arrivals pass |
| `evidence/{ISO3}/readlist.csv` | 6,210 | 296 | `study-select.py` and the drafters, at a rebuild |
| `evidence.csv`, `profile.csv`, `systems.csv`, `stage.json`, `short.json` per cell | 30,011 | 37 | the ladders, `maturity-site.py`, the paragraph writer |

The published product is `outputs/maturity/` and the compiled cell files. Everything above the last row is working material that a study writes, reads within a night or a rebuild, and keeps for the record.

## Decision

**Facts fold into one file a cell; the rest of the working files leave git for a private R2 bucket; the cell files stay.**

- **Facts stay in git, folded.** A night's arrivals restage a country from all its facts, in any study, so they must be on hand every night. The 145,745 part files become one `facts.jsonl` per cell, 6,210 files and the same 62 MB, appended to rather than added to.
- `search*/`, `_batch/` and `readlist.csv` go to `corpus-maturity-work` on R2, one archive per study per night under `{study}/{date}.tar.gz`, written by the run that made them. Only a rebuild reads them, and it pulls its own study's archive.
- Git keeps `study.json`, the study's markdown, its evidence summaries, the folded facts and the five compiled files per cell: about 38,000 files and 155 MB, so `maturity/` falls from 249,796 files to about 38,000 and the tree from 260,267 to about 48,000.
- **History is not rewritten.** The pack keeps the old files; a shallow clone (`--depth 1`) is what a cloud run takes, and it gets the slim tree. A history rewrite would break every published commit link and is not worth 1.8 GB.
- `git gc` runs once now and monthly in the cycle's upkeep: 455,502 loose objects are 4.9 GB that a pack would hold in a fraction, and every `git status` walks them.

## What a cloud run clones

`git clone --depth 1` of about 48,000 files, `site/` and `outputs/` included, which the render needs; then, for the night's two rebuilt studies only, their archives from R2. OSINT's side is a clone plus its 27 GB from `osint-backup` (R196, R180).
