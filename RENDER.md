---
type: runbook
title: Render the site — instruction for Claude Code
last_reviewed: 2026-08-13
---

# Render the site — runbook for Claude Code

*(Hand this to Claude Code running in the Corpus repo on Bill's machine. It renders every site page from Corpus-owned `outputs/`. Read `documentation/handover.md` and `documentation/design.md` §8 first. OSINT is read-only and is not touched by any step here.)*

## What changed, and why this runbook exists

Corpus now **authors** its report and compile layer itself, in `outputs/` (see `documentation/migration-report-layer.md`). It is no longer a mirror pulled from OSINT.
So the build no longer starts with `scripts/pull.py`. It starts from `outputs/`, which is already in the repo and committed.
The existing renderers (`render.py`, `home.py`, `country.py`) were written to read `upstream/`. The quickest correct path is to make `upstream/` a copy of `outputs/` and run them unchanged; the durable path is to point them at `outputs/` directly. Step 1 gives both — do the copy now, do the repoint when there's time.

## Prerequisites

- Python 3 with WeasyPrint and its system libraries installed (already set up on this machine — the site has deployed before). If a render errors on a missing shared library, that is the WeasyPrint system dependency, not this repo.
- Run every command from the repo root (`C:\Users\bill\Dropbox\Github\Corpus`).
- Commit after each coherent step (repo convention).

## Step 0 — start from a clean tree

Commit anything outstanding first, so the render's own commits are isolated and no uncommitted work is at risk:

```bash
git add -A && git diff --cached --quiet || git commit -m "Commit outstanding work before render"
```

A no-op if the tree is already clean.

## Step 1 — point the build at Corpus-owned outputs

Quick path (zero code change): mirror `outputs/` into `upstream/`.

```bash
rsync -a --delete outputs/ upstream/          # Windows: robocopy outputs upstream /MIR
printf 'Corpus-authored outputs/ at %s\n' "$(git rev-parse HEAD)" > upstream/BUILT-FROM
git add upstream && git commit -m "Point build at Corpus-owned outputs (mirror into upstream)"
```

Durable path (do later): in `scripts/render.py`, `scripts/home.py`, `scripts/country.py`, change the input constant from `upstream` to `outputs`, retire `scripts/pull.py` for the report/finance/catalogue layers, then delete `upstream/`. One repoint, no ongoing copy.

## Step 2 — render every report to HTML + PDF

`render.py` takes one markdown file and writes HTML + PDF into `site/reports/…`. Loop it over every report document.

**Skip any monthly that still contains an unwritten-narrative marker** — a few monthlies have empty narrative blocks pending authoring (tracked in Corpus; do not publish a placeholder). Status and progress documents are complete and all render.

```bash
for md in upstream/reports/*/*-status.md upstream/reports/*/*-progress-*.md; do
  python scripts/render.py "$md" || echo "RENDER FAIL: $md"
done
for md in upstream/reports/*/*-monthly-*.md; do
  grep -q 'narrative not yet written' "$md" && { echo "SKIP (empty narrative): $md"; continue; }
  python scripts/render.py "$md" || echo "RENDER FAIL: $md"
done
```

Expect ~54 status + 57 progress + ~20 monthly documents rendered (each as HTML and PDF).

## Step 3 — build the home page

```bash
python scripts/home.py            # -> site/index.html
```

It reads catalogue counts from `upstream/catalogue/`. If `outputs/catalogue/stats.json` does not yet exist it falls back to counting `raw-catalogue.csv` — either is fine.

## Step 4 — build the country and region pages

```bash
python scripts/country.py         # every country -> site/countries/{ISO}/index.html (+ finance.html)
```

`country.py` builds the 54 country pages (those in `FULL_NAMES`). The 3 regions (XAF, XSA, XWA) publish as their rendered **progress** report sets from Step 2, linked under the home page's Regions section — they do not currently get a country-style page. If regions should get their own landing pages, that is a small extension to `country.py`, not a blocker for this render.

## Step 5 — build the catalogue page

`scripts/catalogue.py` (promoted from the prototype) writes the browse-and-filter surface and publishes the full downloads. It reads `upstream/catalogue/raw-catalogue.json` (synced in Step 1) and the vocabularies snapshotted in `outputs/vocab/`.

```bash
python scripts/catalogue.py       # -> site/catalogue/index.html, catalogue-data.js, raw-catalogue.{csv,json}
```

Expect ~9,400 records. The page carries metadata only; each record links to its publisher. If the place/topic labels look stale, refresh `outputs/vocab/countries.csv` and `outputs/vocab/taxonomy.md` from OSINT's `lookups/` and re-run.

## Non-state finance — what renders and what is still missing

Per-country non-state finance already renders: `scripts/country.py` writes a `finance.html` beside each country's `index.html` from `{ISO3}-nonstate.csv`, and the country page carries a Non-state finance section. Running Step 4 covers it.

**Gap:** the top-level `/finance/` landing page that the site nav links to has **no builder yet** — the link currently 404s. Building it (an aggregate view over `all-nonstate.csv`) is a small `scripts/finance.py`, not written. Flagging rather than assuming: say if you want that builder and I'll write it.

## Step 6 — verify, commit, deploy

```bash
# sanity: no unwritten-narrative placeholder reached the site
grep -rl 'narrative not yet written' site/ && echo "STOP: a placeholder was published" || echo "clean"
# every report links only to held sources — spot check a few if desired:
#   python scripts/report-render.py --unit KEN --check   (needs the workroot; optional)
git add site && git commit -m "Render site from Corpus-owned outputs: reports, home, country pages"
```

Deploy is unchanged (`documentation/handover.md`): the GitHub Pages workflow publishes whatever is committed in `site/` on a push touching `site/**`. It does not build — the render above is the build. Push to trigger it.

## Not in this runbook — Topics

The site's **Topics** section cannot render yet: there is no topic-report layer upstream (`REPORT-TOPIC` does not exist). Building it — a ledger sliced by taxonomy Level-1/Level-2 across places, rendered like the country reports — is a Corpus authoring job, owned here, not something Claude Code can render today. It is tracked separately. Home page Topics boxes should link to a "coming soon" state until then.

## Log

On completion or error, append **one terse line** to `logs/log.md`, in the form `YYYY-MM-DD HH:MM · render · what happened`:

```bash
printf '%s · render · %s\n' "$(date '+%Y-%m-%d %H:%M')" \
  "reports+home+countries+catalogue rendered, deployed — ok" >> logs/log.md
```

On failure, log the stage and error instead (`… errored rendering KEN-status: <message>`). One line per run.

## Mirror — back up the repo (final step)

First make sure **all** work is committed — including the log line just written — so the mirror backs up a clean, fully-committed tree:

```bash
git add -A && git diff --cached --quiet || git commit -m "Render run: reports, site, log"
```

Then run the repo backup from the root:

```bat
mirror.bat
```

It mirrors the working tree and full git history to Dropbox and to `D:\CORPUS` (three legs — robocopy, `git bundle`, FreeFileSync), and appends its own dated line to `logs\mirror_log.md`. Because RENDER is the last job in the pipeline, this one call backs up everything the run produced, `outputs/` and `site/` included. A non-zero exit means a leg failed — see `logs\mirror_log.md` and `logs\mirror-ffs\`.

## If something fails

- A single report failing to render should not stop the loop — note it and continue; report the list of failures.
- A WeasyPrint/system-library error is environmental, not a repo bug — surface it rather than working around it.
- Do not write anything to OSINT (`C:\OSINT`) under any circumstance; nothing in this runbook needs to.
