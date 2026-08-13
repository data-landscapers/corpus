---
type: doc
title: Handover — Corpus, for a new maintainer's Claude
last_reviewed: 2026-08-12
---

# Handover: Corpus

*(Written 2026-08-12 for a colleague taking over this repo, to brief a fresh Claude session with no prior context. Read `CLAUDE.md` and `documentation/design.md` in full before touching anything — this is a summary, not a replacement.)*

## What this is

Corpus is the public-site repo for **data-landscapers.com**'s Africa data-governance research. It builds and serves **corpus.data-landscapers.com**: a browsable, downloadable public surface — country reports, regional reports, a source catalogue, budget and non-state-finance data — over a private research base called **OSINT** (`C:\Users\bill\OSINT`, a separate repo Bill maintains).

Corpus is a **derived view**. It holds no state of its own and nothing on it is authored by hand except the build code itself. Everything served is generated from a folder called `outputs/` inside OSINT.

Status as of 2026-08-12: build code exists and works (pull, render, country pages, home page), and the site is deployed via GitHub Pages. Several launch preconditions are still open — see below.

## The one hard boundary

**OSINT is read-only from this repo, absolutely.** No edits, no new files, no moves, no deletes, no git operations, no running OSINT's own procedure files — not even its log or review-queue files. OSINT is the store of record; a mistake there is data loss, whereas a mistake in Corpus is a rebuild.

If something needs to change *in* OSINT — a stale note, a broken path, a request for a new machine-readable export — write it as a numbered finding in `logs/notes-for-osint.md` and tell Bill (or whoever owns OSINT now). Don't make the change yourself. This is stated in `CLAUDE.md` and is the single most important rule in this repo.

Corpus *reads* OSINT freely: grep the tree, read any file, run read-only git commands. It just never writes.

## How data actually moves

**Corpus pulls; OSINT never pushes.** `scripts/pull.py` reads OSINT's committed `HEAD` (never its working tree — a run in progress is simply uncommitted, so this is safe), diffs `outputs/` against the last SHA it built, checks the diff for leaked source bodies, and replaces `upstream/` wholesale. The OSINT path defaults to `C:\Users\bill\OSINT` and can be overridden with `$OSINT_PATH`.

Then the renderers run over `upstream/` and write `site/`:
- `scripts/render.py` — one report (status / monthly / progress) → HTML + PDF, both from one template and one stylesheet, via WeasyPrint.
- `scripts/home.py` — the home page, from catalogue counts.
- `scripts/country.py` — one country page (or all 54), from report frontmatter, the PDFs already rendered, and the non-state-finance CSVs.

`site/` is what GitHub Pages serves. The deploy workflow (`.github/workflows/deploy.yml`) does **not** build anything — it only publishes whatever is already committed in `site/`, triggered by a push touching `site/**`. The render happens locally (WeasyPrint's system deps and the OSINT checkout aren't available to a CI runner), so **the build has to be run and its output committed by hand** each time it should update.

## Repo layout — one rule per folder, and the folder is the rule

```
upstream/    pulled from OSINT outputs/, 1:1 — never hand-edited, overwritten wholesale by every pull
build/       the pull, the renderer, the templates — the ONLY place anything is authored
site/        rendered artefacts, what is served — generated, overwritten by the next build
prototypes/  disposable scaffolding, deleted once the real build fully replaces it
documentation/design.md · logs/notes-for-osint.md · CLAUDE.md · documentation/workflow.md
```

`upstream/` mirrors OSINT's `outputs/` exactly — no renaming, no reshaping. Any divergence would be a mapping that has to be kept in step by hand, which is exactly the kind of thing that silently rots.

## Design decisions already settled (don't relitigate without reason)

Full reasoning is in `documentation/design.md` §1; the highlights:

- Site name is `corpus.data-landscapers.com`, same visual family as the main site.
- Everything is open — no login, no registration, no gate.
- OSINT stays private; only what's in `outputs/` (metadata and compiled prose, never verbatim source bodies) is ever published.
- PDFs are tracked in git, in this repo — the served artefact and its history are one object.
- Every published file carries its build date in the filename; earlier editions are retained silently (a quiet "earlier editions" link, no version picker). A new edition is only minted when the *content* changes (hash below frontmatter), not on every nightly render — otherwise a stable report would mint hundreds of near-identical editions a year.
- No undated download URL ever exists — a citation must never change under the person who made it.
- A published manifest CSV (not yet built) will let anyone verify integrity (hash), currency (dated), and provenance (OSINT commit SHA) for any file they downloaded. Full spec in `documentation/design.md` §9.

## What's built vs. what's still open

**Built and working:** the pull, the report renderer (HTML+PDF), the home page, and all 54 country pages plus 3 regional report sets — these are already generated into `site/`.

**Not built yet / explicitly deferred:**
- Topics section — `REPORT-TOPIC.md` doesn't exist upstream yet, so there's nothing to render.
- The edition manifest CSV (`documentation/design.md` §9) — designed, not implemented.
- Budget block on country pages — suspended; `{ISO3}-summary.csv` isn't read.
- Catalogue serving shape — flat JSON works today (7,770 records) but won't past ~15–20k rows; sharding is designed but not built.

**Launch preconditions (`documentation/design.md` §7) — the site cannot launch over these:**
1. OSINT's repo size (4.6 GB, growing ~150 MB/day) is against GitHub's soft 5 GB ceiling.
2. There's no single consolidated, versioned, methodology-documented cross-country dataset — 59 per-country CSVs aren't a citable dataset on their own.
3. `REPORT-LINT` (a verification pass) doesn't yet cover the reporting layer that the site would be publishing.

These are OSINT-side problems Corpus can't fix directly — they're tracked as unresolved notes 3, 4, 5 in `logs/notes-for-osint.md`.

## logs/notes-for-osint.md — what it is and why it matters

This file is the *only* channel for getting a change made in OSINT from a Corpus session. It's numbered, oldest-unresolved-first, and has a **Standing constraints** section at the top — properties of OSINT the site depends on that must never silently change:
- `outputs/` must stay git-tracked and committed (the build diffs against committed HEAD; a cycle that stops committing it breaks the site with no error).
- Nothing outside `outputs/` is ever read by the build.
- A catalogue slug is a permanent public identifier and must never be reissued once the site is live.

As of 2026-08-12 there are 9 open numbered notes (1–9) — worth reading in full, but two are worth flagging by name: **#6** is a live data-integrity discrepancy (Kenya's ledger count disagrees across three files — 171 rows in the CSV vs. 146/169 in different frontmatter) that has to be resolved before *Not held* counts go on a public page, since that's meant to be the site's signature honesty feature. **#9** is that the site currently hand-duplicates two OSINT vocabularies (country names, topic labels) because it isn't allowed to read outside `outputs/` — a maintenance risk if either vocabulary changes upstream.

## Working conventions

- **One line per paragraph, never hand-wrapped.** Applies to every file in this repo except frontmatter, code blocks, and tables. Reason: a hard-wrapped paragraph diffs badly — one changed word near the start reflows every following line, so the diff shows a rewritten paragraph instead of a changed word.
- **Commit after every change, not at the end of a session.** One commit per coherent change, terse subject line. An uncommitted tree is the one state that isn't reversible.
- **This repo lives on Dropbox.** Deletes need permission once per session — the sandbox blocks `unlink` on the Dropbox mount by default, which leaves a stale `.git/HEAD.lock` that then fails *every subsequent* commit with "cannot lock ref 'HEAD'". If commits start failing mid-session, check for stale `.lock` / `tmp_obj_*` files under `.git/` first.
- `documentation/design.md` is a living design record, revised in place rather than appended to — when a section of it gets built, the runnable part should move to a proper procedure file and the design doc keeps only the reasoning.
- `documentation/workflow.md` is a lightweight Obsidian kanban board (Backlog / Next / Processing / Complete) — currently near-empty, not a source of truth for project state; treat `documentation/design.md` §6/§7 and `logs/notes-for-osint.md` as the actual backlog.

## Recommended reading order for a first session

1. `CLAUDE.md` — the rules above, in full and in Bill's own words.
2. `documentation/design.md` — the full design record: what's settled, content model, the three design commitments, how data reaches the site, editions and verification.
3. `logs/notes-for-osint.md` — the standing constraints and the 9 open notes.
4. `build/*.py` docstrings — each script's header explains what it does and why, in the same voice as the design doc; they're worth reading before changing any of them.
