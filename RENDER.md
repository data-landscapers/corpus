---
type: runbook
title: Render the site — instruction for Claude Code
last_reviewed: 2026-09-20
---

# Render the site — runbook for Claude Code

*(Job 2. Renders every site page from Corpus-owned `outputs/`, already in the repo and committed — no pull, no second tree. Read `documentation/design.md` §8 and §9 first. **`documentation/render.md` is why each step is where it is and what each check catches**; this file is what to run. OSINT is read-only and is not touched by any step here. To run this straight after `BUILD.md` as one job, use `CYCLE.md`; this file runs alone exactly as written, Step 0 included.)*

## Prerequisites

- Python 3 with WeasyPrint. `C:\msys64\mingw64\bin` must sit on PATH **after** the Python entries and **before** `C:\Program Files\Tesseract-OCR`; a shared-library error means check that ordering first.
- Run every command from the repo root. Commit after each coherent step.

## Running unattended — a run never stops to ask

**RENDER puts no question mid-stream.** A run finishes or fails; a failure is an error it cannot get past, never a decision it would rather Bill made. Where it wants his attention it finishes the job and writes a block in `logs/messages-for-bill.md`. **RENDER judges nothing about its input** — fitness to publish is BUILD's — and its one hard stop is Step 0.

## Step 0 — a finished build behind you, then a clean tree

Stamp the clock first, before the gate, so a Step 0 stop logs a duration too:

```bash
python scripts/log-line.py --start render
```

**Check the build finished before rendering a line of it.** A build that died mid-stage-4 renders perfectly and is silently a cycle out of date:

```bash
# 1. a build that started and never reported itself leaves its sentinel behind
if [ -e logs/.build-in-progress ]; then
  echo "RENDER STOP: $(cat logs/.build-in-progress) — that build never finished"; exit 1
fi
# 2. the newest build line must exist and must not be an error line
build_line=$(grep -m1 -i -E ' · (\*\*)?build(\*\*)? · ' logs/log.md)
[ -n "$build_line" ] || { echo "RENDER STOP: no build line in logs/log.md"; exit 1; }
case "$build_line" in *errored*) echo "RENDER STOP: last build errored — $build_line"; exit 1 ;; esac
# 3. outputs/ must be committed — a finished build leaves nothing outstanding
if [ -n "$(git status --porcelain outputs)" ]; then
  echo "RENDER STOP: outputs/ has uncommitted changes"; exit 1
fi
echo "build ok: ${build_line%% · *}"
```

**All three log and stop** — `python scripts/log-line.py render "stopped at step 0: <which> — not rendered"` — and write a message. **The repair is to run BUILD**, which resumes where it stopped. **Never delete the sentinel or hand-write a log line to get past this**: forging either publishes the half-built tree the check exists to catch.

Then commit anything else outstanding, **after the gate, not before**:

```bash
git add -A && git diff --cached --quiet || git commit -m "Commit outstanding work before render"
```

## Step 1 — stamp the commit the site is built from

```bash
git rev-parse HEAD > BUILT-FROM
```

## Step 2 — render every report to HTML + PDF

`render.py` writes HTML + PDF into `site/…`, the output tree taken from the source path. **Render everything.** An unchanged document keeps its edition and is not re-cut; `--force` cuts every edition and is a decision, not a habit.

```bash
rendered=0; failed=0
for md in outputs/reports/*/*-status.md outputs/reports/*/*-progress.md outputs/reports/*/*-monthly.md \
          outputs/topics/*/*-progress.md outputs/topics/*/*-monthly.md; do
  [ -e "$md" ] || continue
  if python scripts/render.py "$md"; then rendered=$((rendered+1)); else echo "RENDER FAIL: $md"; failed=$((failed+1)); fi
done

# The bulletin — see The bulletin below.
for md in outputs/bulletins/*-bulletin.md; do
  [ -e "$md" ] || continue
  if python scripts/render.py "$md"; then rendered=$((rendered+1)); else echo "RENDER FAIL: $md"; failed=$((failed+1)); fi
done

# Coverage assertion: the patterns above must have reached every report document.
present=$(find outputs/reports outputs/topics outputs/bulletins -name '*.md'           ! -name 'progress-narrative-archive.md' | wc -l)
missed=$((present - rendered - failed))
echo "rendered $rendered of $present report documents ($failed failed, $missed never listed)"
if [ "$missed" -gt 0 ]; then
  echo "RENDER STOP: $missed document(s) matched no pattern in the loop — do not deploy:"
  find outputs/reports outputs/topics outputs/bulletins -name '*.md'        ! -name 'progress-narrative-archive.md' | grep -Ev -- '-(status|progress|monthly|bulletin)\.md$'
  exit 1
fi
if [ "$failed" -gt 0 ]; then
  echo "$failed document(s) failed in render.py (see RENDER FAIL above) — deploying the rest; message Bill"
fi
```

**A document the loop never listed stops the run; a document tried and failed does not** — note it, render on, deploy, list it in the message. Topic documents land in `site/topics/{slug}/` and the loop already reaches them; **if the taxonomy grows a slug, check the link, not just the box** — every `/topics/…` href in `site/index.html` against `site/topics/…/index.html`.

## Step 3 — build the home page

```bash
python scripts/home.py            # -> site/index.html, site/countries/, site/topics/
```

Stale place or topic labels mean `outputs/vocab/` wants refreshing from OSINT's `lookups/`.

## Step 4 — build the country, region and topic pages

```bash
python scripts/country.py         # every country -> site/countries/{ISO}/index.html (+ finance.html)
python scripts/region.py          # every region  -> site/countries/{X__}/index.html (+ finance.html)
python scripts/topic-page.py      # every topic   -> site/topics/{slug}/index.html
```

**`topic-page.py` and `region.py` run after Step 2** — both read what Step 2 rendered. The finance CSVs are dated editions, written before the pages that link them by name.

## Step 4a — build the two progress tables

```bash
python scripts/progress.py        # -> site/progress/ and site/progress/countries/
```

Also after Step 2. It writes no edition, so it is safe to run alone after an edit to `content/progress-topics.md` or `content/progress-countries.md`.

## Step 5 — build the catalogue page

```bash
python scripts/catalogue.py       # -> site/catalogue/index.html, data/, raw-catalogue.csv
python scripts/alerts.py          # -> site/alerts/ — the two pages and the two files the Worker reads
```

**`alerts.py` runs after `catalogue.py`**, from the same `raw-catalogue.json`. Then the tests:

```bash
python scripts/test_catalogue_rowshape.py     # the four readings of a row agree on its fields
python scripts/test_catalogue_index.py        # the split payload holds the whole catalogue
python scripts/test_catalogue_firstscreen.py  # baked markup == what the page draws (needs node)
python scripts/test_catalogue_export.py       # every record rebuilt == raw-catalogue.csv (needs node)
python scripts/test_alerts.py                 # the backfill rule, the record id, the published columns
python scripts/test_alerts_worker.py          # the Worker's pure core (needs node, or `pip install dukpy`)
```

### The search indexes — built before the page

```bash
python scripts/rebuild.py --catalogue                 # BUILD stage 2 + 2b: catalogue, then names
python scripts/build-title-index.py                   # -> outputs/titles/  (no vault needed)
python scripts/test_title_index.py                    # word-aligned queries find their records
python scripts/build-names-index.py --stats           # size profile, writes nothing (from .workroot)
python scripts/build-title-index.py --stats           # the same for the title shards
```

**Do not `git add` `site/catalogue/names/` or `site/catalogue/titles/`** — the shards are served from R2 and tracked in neither tree. `outputs/catalogue/doc-ids.csv` **is tracked and must stay so**: rebuilding it renumbers every id and rewrites every shard.

## Step 6 — build the non-state finance landing

```bash
python scripts/finance.py         # -> site/finance/index.html + all-nonstate-{edition}.csv
```

## The prose

Every explanatory paragraph the site shows a reader lives in `content/`, read by `scripts/copy_lib.py`. **A missing key stops the build.**

```bash
python scripts/copy_lib.py            # what is where: file, key, word count, placeholders
python scripts/copy_lib.py home       # one file
```

## The finance tables

Drawn in the browser by `site/assets/js/datatable.js` from the published CSV the page already offers.

```bash
cd /tmp && npm install jsdom && node prototypes/datatable-test.mjs   # from a copy in that dir
```

> **Line endings, when building from a Cowork session.** `csv.writer` emits `\r\n`; Windows git normalises to LF on commit and Linux git does not, so a rebuild in the Cowork sandbox rewrites every published CSV with CRLF and git reports the whole file changed. A published edition must not be revised (§9), so **check for CR-only churn before committing a rebuild** and restore those files: `for f in $(git diff --name-only); do [ -z "$(git diff --ignore-cr-at-eol -- "$f")" ] && git checkout HEAD -- "$f"; done`. A `.gitattributes` would settle it permanently, but 186 tracked files already hold CRLF, so adding one renormalises them all at once — a decision for a session doing only that.

## Step 6a — prune superseded editions nobody took

```bash
python scripts/prune-editions.py --apply
```

Before Step 7's `git add site`, so deletions ride the same commit. **A refusal is a normal outcome and never fails the run**: it prints `PRUNE: declined` with the reason and exits 0.

## Step 6b — put this render's editions in R2, and take them out of the tree

```bash
python scripts/r2-sync.py --apply
python scripts/r2-sync.py --prune-local --apply
```

After 6a, before Step 7. Without the R2 key pair both lines print `R2: declined` and exit 1; the render is still publishable, but a persistent refusal wants acting on. **After a change to what counts as an edition**, add `--check-serving` on the first run.

## Step 6c — build the methodology pages

```bash
python scripts/methodology.py     # -> site/methodology/ + its four annexes
```

Writes no edition; safe to run alone after an edit to `content/`.

## Step 6d — the sitemap

```bash
python scripts/sitemap.py         # -> site/sitemap.xml + site/robots.txt
```

Last of the writers, because it reads the tree the others left.

## Step 7 — verify, commit, deploy

```bash
python scripts/lint-external-links.py
python scripts/lint-structured-data.py
```

**A finding from either stops the push.** The repair is to fix the builder and re-run the step that wrote the page — `render.py --repage` for a report — neither of which cuts an edition.

```bash
git add site
[ -e logs/deleted-editions.csv ] && git add logs/deleted-editions.csv
git commit -m "Render site from Corpus-owned outputs: reports, home, country pages"
git push
```

**Step 0 is the only STOP in this runbook.** The GitHub Pages workflow publishes whatever is committed in `site/` on a push touching `site/**`. **The push is authorised by this runbook and is not a question to put**: running RENDER *is* the instruction to publish.

**The push is not the deploy, so check the run before the log says `deployed`** — before the mirror step, and again after it if it still reads `in_progress`:

```bash
curl -s "https://api.github.com/repos/data-landscapers/corpus/actions/runs?head_sha=$(git rev-parse HEAD)" | python -c "import json,sys; r=json.load(sys.stdin).get('workflow_runs',[]); print(r[0]['status'], r[0]['conclusion']) if r else print('no run')"
```

`completed success` is `deployed`. Anything else is logged as `pushed, deploy <status>`, and the fix is **Re-run failed jobs** on that run in GitHub Actions.

## The bulletin

From BUILD stage 7, at `outputs/bulletins/corpus-bulletin.md`, published at `site/bulletin/index.html` and served as `/bulletin/`. Step 2's loop renders it. Three things differ from every other document: **its page is refreshed on a held-off render**, PDF untouched; **it keeps a week of editions** and `prune-editions.py` deletes on that retention window rather than on fetches, so it needs no Cloudflare token; and **an empty window still renders** — never skip it.

**Assert that the listing and the directory agree**, after Step 6a and after the render:

```bash
python scripts/bulletin_editions.py
```

## Log

On completion or error, one terse line:

```bash
python scripts/log-line.py render "reports+home+countries+catalogue rendered, deployed — ok"
```

On failure, log the stage and error instead (`… errored rendering KEN-status: <message>`). The duration writes itself from the Step 0 stamp; where the stamp was never taken, use `--since` or `--took`.

**And message Bill where the run needed him** — before the commit below so it is carried by it: documents that failed to typeset, a Step 0 stop and what has to be re-run, anything the run decided he would otherwise have been asked. `python scripts/lint-messages.py` counts the caps. A clean render writes nothing.

## Mirror — back up the repo (final step)

First commit everything, including the log line just written:

```bash
git add -A && git diff --cached --quiet || git commit -m "Render run: reports, site, log"
```

Then run the backup, **by absolute path, from PowerShell**:

```powershell
& cmd /c "C:\CORPUS\mirror.bat"
```

**Check the log line rather than the exit code**: the top line of `logs\mirror_log.md` must be dated within the last few minutes. A bare `mirror.bat` exits 0 having backed up nothing, so the absence of a fresh line is the real failure signal.

```bash
python scripts/lint-mirror-freshness.py     # 0 clean · 1 stale or failed · 2 nothing recorded
```

Run it before the mirror to see whether one is owed, and after to confirm the line landed; **it reports and never fixes**. **RENDER runs the mirror** — what stays Bill's is firing one *outside* a run.

## If something fails

- A single report failing to render does not stop the loop or the run — note it, continue, deploy the rest, list it in `logs/messages-for-bill.md`.
- A WeasyPrint/system-library error is environmental, not a repo bug — surface it. If it takes down every document, that is the whole run failing: log it and stop.
- **Nothing here is a question for Bill.** The one hard stop is Step 0, a mechanical test with a stated repair.
- Do not write anything to OSINT (`C:\OSINT`) under any circumstance; nothing in this runbook needs to.
