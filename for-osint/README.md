---
type: doc
title: for-osint — material written in Corpus, destined for the OSINT repo
last_reviewed: 2026-08-14
---

# for-osint

**Files here are written in Corpus and belong in OSINT.** Corpus never writes to OSINT (`CLAUDE.md`), so anything it authors for that repo lands here, under git, and **Bill installs it in an OSINT session**. Nothing in this folder is run from here, and nothing in Corpus reads it.

The pairing is `logs/notes-for-osint.md`: that file carries the numbered instruction to install these, and it is where the note is struck once done. A file that has been installed in OSINT is deleted from here — OSINT's git holds it from then on, and two copies of a live process file is the failure this whole boundary exists to prevent.

## Currently held

| File | Destination in OSINT | Note |
|---|---|---|
| `STATUS-INIT.md` | repo root, as a standalone procedure file; `wiki/index.md` → *Processes* takes its trigger | Every path inside it is relative to the **OSINT** root and reads correctly only after the move. |
| `status-outline.md` | `lookups/status-outline.md` | The drafting outline `STATUS-INIT.md` works to — 37 sub-sections, one per taxonomy Level-2 slug. |
| `status-wireframe.md` | — | Superseded by `status-outline.md`, kept only until Bill confirms it can go. |

Two data files that move with `STATUS-INIT.md` are **not** here: `africa-dpi-data.csv` (17 MB) and `status-indicators-africa-dpi.csv` are in Corpus's gitignored `prep/`, awaiting Bill's decision on how they reach OSINT's `lookups/`. Routing 17 MB of third-party data through a public repo to get it into a private one is not obviously the right way to move a file (`logs/notes-for-osint.md` note 8).
