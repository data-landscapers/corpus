---
type: runbook
title: Render the site — instruction for Claude Code
last_reviewed: 2026-08-28
---

# Render the site — runbook for Claude Code

*(Job 2. Renders every site page from Corpus-owned `outputs/`, which is already in the repo and committed — there is no pull and no second tree. Read `documentation/design.md` §8 and §9 first. OSINT is read-only and is not touched by any step here. To run this straight after `BUILD.md` as one job, use `CYCLE.md`; this file runs alone exactly as written, Step 0 included.)*

## Prerequisites

- Python 3 with WeasyPrint and its system libraries. On this machine, MSYS2 at `C:\msys64` provides Pango/Cairo/HarfBuzz, and `C:\msys64\mingw64\bin` sits on the user PATH **after** the Python entries but **before** `C:\Program Files\Tesseract-OCR` — MSYS2 ships its own `python.exe`, and Tesseract ships older Pango DLLs (`cannot load library … error 0x7f`). A missing/unloadable shared library means check that ordering first.
- Run every command from the repo root. Commit after each coherent step.

## Running unattended — a run never stops to ask

**RENDER puts no question mid-stream.** A run finishes or fails; a failure is an error it cannot get past, never a decision it would rather Bill made. Where it wants his attention, it finishes the job and writes a block in `logs/messages-for-bill.md`. RENDER judges nothing about its input by design; its one hard stop is Step 0.

## Step 0 — a finished build behind you, then a clean tree

Stamp the clock first, before the gate, so a Step 0 stop logs a duration too:

```bash
python scripts/log-line.py --start render
```

**Check the build finished before rendering a line of it.** A build that died mid-stage-4 leaves a tree that renders perfectly — every check passes, and the units that never got their sources are silently a cycle out of date. Nothing downstream can see that, so the test is here and it fails the run:

```bash
# 1. a build that started and never reported itself leaves its sentinel behind
if [ -e logs/.build-in-progress ]; then
  echo "RENDER STOP: $(cat logs/.build-in-progress) — that build never finished"; exit 1
fi
# 2. the newest build line must exist and must not be an error line
build_line=$(grep -m1 ' · build · ' logs/log.md)
[ -n "$build_line" ] || { echo "RENDER STOP: no build line in logs/log.md"; exit 1; }
case "$build_line" in *errored*) echo "RENDER STOP: last build errored — $build_line"; exit 1 ;; esac
# 3. outputs/ must be committed — a finished build leaves nothing outstanding
if [ -n "$(git status --porcelain outputs)" ]; then
  echo "RENDER STOP: outputs/ has uncommitted changes"; exit 1
fi
echo "build ok: ${build_line%% · build · *}"
```

**Check 1 is the mechanism; the other two are cheap corroboration.** The sentinel survives exactly one thing — a session that died without saying so — and asserts the condition directly. (A timestamp test cannot: other jobs legitimately commit `outputs/`, and a died build commits its finished units and writes nothing, so timestamp logic fails in both directions.)

**All three log and stop** — `python scripts/log-line.py render "stopped at step 0: <which> — not rendered"` — and write a message. **The repair is to run BUILD**, which resumes where it stopped. Never delete the sentinel or hand-write a log line to get past this: both are assertions that a build finished, and forging one publishes the half-built tree the check exists to catch.

Then commit anything else outstanding, **after the gate, not before** — running it first would satisfy check 3 by committing the very work whose being uncommitted is the evidence:

```bash
git add -A && git diff --cached --quiet || git commit -m "Commit outstanding work before render"
```

## Step 1 — stamp the commit the site is built from

```bash
git rev-parse HEAD > BUILT-FROM
```

Records the Corpus commit this render was cut at. No page prints it any more; it is the build's own record, kept because it costs one line.

## Step 2 — render every report to HTML + PDF

`render.py` takes one markdown file and writes HTML + PDF into `site/…`, the output tree taken from the source path.

**Render everything. RENDER does not judge its input.** Fitness to publish is BUILD's (BUILD.md → *Narrative integrity*); a render that second-guesses it is a weaker copy of that judgement in the wrong place.

**`render.py` decides whether a document has moved** — design.md §9: *an edition is cut when the content changes, not when a build runs*. It digests each source's body below its frontmatter, reads back the digest off the page it wrote last time, and leaves an unchanged document alone — page and PDF both. Most documents report `edition unchanged` on most runs; a held-off document was handled, exits zero, and counts as rendered. A document that moves twice in a day gets a `-2`-suffixed second edition, never an overwrite. **A held-off document is not restyled**: the PDF embeds the stylesheet, so a CSS or template change reaches new editions only — to push one through the whole set, pass `--force`, which cuts every edition and is a decision, not a habit.

```bash
rendered=0; failed=0
for md in outputs/reports/*/*-status.md outputs/reports/*/*-progress.md outputs/reports/*/*-monthly.md \
          outputs/topics/*/*-progress.md outputs/topics/*/*-monthly.md; do
  [ -e "$md" ] || continue
  if python scripts/render.py "$md"; then rendered=$((rendered+1)); else echo "RENDER FAIL: $md"; failed=$((failed+1)); fi
done

# The bulletin — see Bulletins below.
for md in outputs/bulletins/*-bulletin.md; do
  [ -e "$md" ] || continue
  if python scripts/render.py "$md"; then rendered=$((rendered+1)); else echo "RENDER FAIL: $md"; failed=$((failed+1)); fi
done

# Coverage assertion: the patterns above must have reached every report document.
# `progress-narrative-archive.md` is working material, not a document — see below.
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

**The count is asserted because a shrinking loop is silent**: a rename moves filenames out of the glob and the loop quietly renders a subset with a zero exit, while `site/` — never purged — serves the old pages indefinitely. The assertion enumerates without a pattern, so no rename can shrink the set in silence. `progress-narrative-archive.md` is excluded **by exact filename** — it is the per-chapter narrative the indicator frame archived as drafting material, published nowhere — so the property stands: nothing but that one name is forgiven.

**The two ways of coming up short are different failures.** A document the loop **never listed** stops the run — the silent-shrink case, invisible from the output: log, message, no deploy. A document **tried and failed** does not — one page that will not typeset keeps its previous render either way, so withholding the other pages protects nothing: note it, render on, deploy, list it in the message.

The set is currently ~242 documents (165 place + 76 topic + the bulletin), all HTML and PDF — but **the assertion is what to trust, not the number**.

## Step 3 — build the home page

```bash
python scripts/home.py            # -> site/index.html, site/countries/, site/topics/
```

Reads catalogue counts from `outputs/catalogue/` (`stats.json`, falling back to counting `raw-catalogue.csv`). **One command, three pages**: the country matrix and taxonomy matrix are pages of their own, and the home page keeps each section's heading, intro and link. All three are the same object built from the same counts. The topics page prints the whole taxonomy in `lookups/taxonomy.csv`'s order and wording, so it is the page that goes out of date when a subject is added there and nothing else changes.

## Step 4 — build the country, region and topic pages

```bash
python scripts/country.py         # every country -> site/countries/{ISO}/index.html (+ finance.html)
python scripts/topic-page.py      # every topic   -> site/topics/{slug}/index.html
```

**`topic-page.py` runs after Step 2** — it writes the landing page each topic box opens by reading what Step 2 actually rendered; run before the documents exist, it advertises nothing.

**One field dictionary, not one per country.** `site/metadata/non-state-finance-metadata.csv` describes the non-state finance schema for every table on the site: hand-maintained by Bill, generated by nothing. `country.py` links it and refuses to build if it is missing — an absence there is 54 broken links. It carries no edition date: it describes a shape, not a finding.

**The finance CSVs are dated editions** — `{ISO3}-nonstate-{edition}.csv` beside each country page, on §9's rule: a new edition only when the bytes move, retained edition over edition, `-2` for a second in a day. Pages are written after the CSVs because they link them by name. The catalogue CSV is deliberately outside the edition rule.

`country.py` builds the 54 country pages. The 3 regions (XAF, XSA, XWA) publish as their rendered progress reports from Step 2, linked under the home page's Regions section — no country-style page.

## Step 5 — build the catalogue page

```bash
python scripts/catalogue.py       # -> site/catalogue/index.html, catalogue-data.js, raw-catalogue.{csv,json}
```

Reads `outputs/catalogue/raw-catalogue.json` and the vocabularies in `outputs/vocab/`. Expect ~10,700 records, metadata only, each linking to its publisher. Stale place/topic labels mean `outputs/vocab/` wants refreshing from OSINT's `lookups/`.

### The names index — build it before the page

`scripts/build-names-index.py` (BUILD stage 2b, from the workroot) writes `outputs/names/`: ~208,000 names keyed to stable document ids, in ~1,900 shards the catalogue page fetches one at a time on search. `catalogue.py` packs the shard keys into the page and copies the shards to `site/catalogue/names/`.

```bash
python scripts/rebuild.py --catalogue                 # BUILD stage 2 + 2b: catalogue, then names
python scripts/build-names-index.py --stats           # size profile, writes nothing (from .workroot)
```

### Entity display names

`scripts/build-entity-names.py` (BUILD stage 2c) writes `lookups/entity-names.csv` — a display name per entity slug, derived from the slug's own sources; `catalogue.py` prettifies the unnamed rest. The name joins the search blob. **The file is meant to be corrected by hand**: `basis: hand` is never overwritten; `basis` (`acronym`/`full`/`partial`) and `sources` say how much to trust a row. It is Corpus's file: the slugs are OSINT's, how they are written is decided here.

**`outputs/names/` is gitignored; `site/catalogue/names/` is tracked** — same shards, and tracking both would carry 37 MB twice. `outputs/catalogue/doc-ids.csv` **is tracked and must stay so**: the append-only registry that keeps postings stable; rebuilding it renumbers every id and rewrites every shard.

**The shards are exempt from §9, deliberately.** Nothing cites a shard; it is a derived lookup that must track the corpus or it is wrong. Shards are rewritten in place and stale ones deleted, in both trees — the one place "never purged" does not apply. Ids are append-only, and both writers compare before writing, so expect a handful of changed shards per cycle. A rebuild that changes all of them means the id registry was rewritten rather than appended to — that is the bug to look for.

## Step 6 — build the non-state finance landing

```bash
python scripts/finance.py         # -> site/finance/index.html + all-nonstate-{edition}.csv
```

The site nav's **Finance** link points here. Expect ~1,230 deals and a headline total near US$91,000m. **The all-Africa table is on the landing page itself**, on the same component as each country's `finance.html`; `finance.py` deletes any legacy `all.html` it finds, printing a line. `recipient_country` is ISO-3 in the CSV and a country name in the table, mapped via a `data-labels` attribute from `outputs/vocab/countries.csv`. The cross-country CSV is a dated edition on the same rule as the per-country ones.

**The landing layout above the table is a placeholder awaiting design**; the table itself is finished and is what a reader came for.

## The prose

**Every explanatory paragraph the site shows a reader lives in `content/`**, one markdown file per page type, named blocks under `##` headings, read by `scripts/copy_lib.py`:

```bash
python scripts/copy_lib.py            # what is where: file, key, word count, placeholders
python scripts/copy_lib.py home       # one file
```

Three calls for three kinds of slot: `copy()` returns HTML; `copy_inline()` returns it without the wrapping `<p>` (raises if the block has grown to two paragraphs); `copy_md()` returns markdown untouched, for the emitters whose output `render.py` converts later.

**A missing key stops the build** — no fallback, no empty string: a page quietly rendering without its explanatory paragraph looks finished and is not. **Placeholder values arrive pre-formatted** — a format spec inside a content file puts presentation logic back where it was taken out of, and fails at build time in what the editor thinks is plain text. Blocks carrying `{placeholders}` or branch-selection are still string constants in the builders; they move when a slot or variant per branch exists.

## The finance tables

Both the per-country `finance.html` and the all-Africa table are drawn **in the browser** by `site/assets/js/datatable.js` reading the published CSV the page already offers — no `<tr>` per commitment. `site/assets/css/datatable.css` holds the styling, kept out of `main.css` because that file is a copy carrying its own provenance marker (`MAIN-CSS-FROM`). The cost is that neither table appears with JavaScript off, so both carry a `<noscript>` block naming the CSV: the data is never behind the script, only the table is.

The component is a port of the Lab's datatable (`data-landscapers/assets/shared/` is canonical), driven entirely by `data-*` attributes documented in the file's own header. Two finance-specific behaviours: it parses CSV by character scan (quoted fields carry newlines), and it sorts blank amounts last in both directions (a missing figure is not a small one).

```bash
cd /tmp && npm install jsdom && node prototypes/datatable-test.mjs   # from a copy in that dir
```

`prototypes/datatable-test.mjs` loads the two built pages into jsdom and asserts on what the component produced, then drives a filter, a no-hit search, and a numeric sort. jsdom has no layout, so the sticky header and column-width sync need a browser.

> **Line endings, when building from a Cowork session.** `csv.writer` emits `\r\n`; Windows git normalises to LF on commit and Linux git does not, so a rebuild in the Cowork sandbox rewrites every published CSV with CRLF and git reports the whole file changed. A published edition must not be revised (§9), so **check for CR-only churn before committing a rebuild** and restore those files: `for f in $(git diff --name-only); do [ -z "$(git diff --ignore-cr-at-eol -- "$f")" ] && git checkout HEAD -- "$f"; done`. A `.gitattributes` would settle it permanently, but 186 tracked files already hold CRLF, so adding one renormalises them all at once — a decision for a session doing only that.

## Step 6a — prune superseded editions nobody took

```bash
python scripts/prune-editions.py --apply
```

**A superseded edition is deleted unless somebody downloaded it** (`documentation/cloudflare.md`; forward-only from 2026-08-18). Retention exists for readers: a citation only exists if someone took the file. The current edition, anything ever fetched (crawlers included), anything superseded under a week, anything dated on or before 2026-08-18, and any undated download are never touched. It runs here, before Step 7's `git add site`, so deletions ride the same commit as the render that superseded them.

**A refusal is a normal outcome and never fails the run.** The script exits 0 either way and declines wholesale — on a missing credential (it needs a Cloudflare API token with KV read scope, `documentation/cloudflare.md` → *Credentials*), an API error, an empty key listing or a stale-looking download record — printing `PRUNE: declined` with the reason. Persistent refusal means the Worker or token wants looking at; until then the rule is simply not in effect. Deletions are appended to `logs/deleted-editions.csv`, committed with the render.

## Step 7 — verify, commit, deploy

```bash
git add site
[ -e logs/deleted-editions.csv ] && git add logs/deleted-editions.csv
git commit -m "Render site from Corpus-owned outputs: reports, home, country pages"
git push
```

**Step 0 is the only STOP in this runbook.** RENDER does not judge fitness to publish — that is BUILD's, and a check here would be a second, weaker copy of it that halts every render to protect nothing.

Deploy: the GitHub Pages workflow publishes whatever is committed in `site/` on a push touching `site/**`. It does not build — the render above is the build; the push triggers it. **The push is authorised by this runbook and is not a question to put**: running RENDER *is* the instruction to publish.

## The bulletin

Authored by BUILD (stage 7), arrives at `outputs/bulletins/corpus-bulletin.md`. **Published at `site/bulletin/index.html`, served as `/bulletin/`** — one bulletin, a singular URL, the one document served as a directory index. The retired country bulletin's pages under `site/bulletins/` are deleted, not left to rot.

- **It cuts a dated PDF like everything else** — the superseded document is precisely the one a reader wants a copy of, because tomorrow's page will not be showing it. The edition shown on the page carries a time (from `compiled:`); the filename carries the plain date and same-day sequence.
- **Its page is refreshed on a held-off render, which no other document's is.** Freshness is news for a bulletin: a sweep that brought in fifty sources none dated inside the window still updated it — *we looked, and nothing was published*. For `type: bulletin` the gate holds the edition and `render.py` rewrites the page under the edition it is holding, PDF untouched. The digest is still the body, so a moved clock cannot cut an edition; the byline answers *when did we last look*, the colophon *which dated file is this*.
- **It keeps a week of editions, and the page lists them.** `site/bulletin/editions.json` is the manifest (`documentation/bulletin-archive.md` is the design). `render.py` writes an entry at the moment it cuts a bulletin PDF — the only moment the picker's three facts are in hand. The colophon's `Retention` row names the date the file is kept until, and travels into the PDF: a file that will 404 in a week and does not say so fails §9 on its own terms.
- **The bulletin leaves the download rule**: `prune-editions.py` deletes a bulletin edition on the retention window, not on fetches, and rewrites the manifest — otherwise the one-week promise would hold for every bulletin except the ones a reader took. Bulletin retention therefore works with no Cloudflare token.
- **Assert that the listing and the directory agree**, after Step 6a and after the render: `python scripts/bulletin_editions.py` prints the listing and names any entry with no file behind it. The renderer and pruner both rebuild rather than append, so a mismatch means something outside them moved a file.
- **It is the one page here that carries a script**: `site/assets/js/bulletin-filter.js`, Corpus's own, referenced only from this page, written into the HTML pass and left out of the PDF pass. The control renders `hidden` and the script removes the attribute, so a page whose script fails is a page without a filter, not one with a dead control.
- **An empty window still renders** — the document says so in its own prose; RENDER never skips it. The home page's Bulletin section is omitted entirely when the document does not exist.

**Stylesheets and scripts are stamped with a digest of their own bytes** (`main.css?v=22ef527a`) — the query string changes exactly when the file does. So a change to `report.css` alone reaches a page only when that page next renders (the content gate reads the markdown): a stylesheet fix spreads as editions re-cut, or all at once behind `--force`. The bulletin, re-rendering whenever its window moves, picks it up the same day.

## Topics

Topic documents (BUILD stage 6) arrive in `outputs/topics/{slug}/`, two per Level-2 slug. They render exactly like the place reports — `render.py` takes its output tree from the source path, so they land in `site/topics/{slug}/`. Step 2's loop and coverage assertion already reach them. The home page's Topics boxes open `/topics/{slug}/` (hyphenated slug); **if the taxonomy grows a slug, check the link, not just the box** — compare every `/topics/…` href in `site/index.html` against `site/topics/…/index.html`.

## Log

On completion or error, one terse line:

```bash
python scripts/log-line.py render "reports+home+countries+catalogue rendered, deployed — ok"
```

On failure, log the stage and error instead (`… errored rendering KEN-status: <message>`). The duration writes itself from the Step 0 stamp, then clears it; where the stamp was never taken, state the truth with `--since` or `--took`. The script inserts at the top under the marker, refuses a message over 40 words, and exits 1 if the marker is missing.

**And message Bill where the run needed him** — before the commit below so it is carried by it: documents that failed to typeset, a Step 0 stop and what has to be re-run, anything the run decided he would otherwise have been asked. At most 80 words a block; `python scripts/lint-messages.py` counts both caps and `python scripts/lint-preambles.py` checks the preamble is still a pointer. A clean render writes nothing.

## Mirror — back up the repo (final step)

First commit everything, including the log line just written:

```bash
git add -A && git diff --cached --quiet || git commit -m "Render run: reports, site, log"
```

Then run the backup, **by absolute path, from PowerShell**:

```powershell
& cmd /c "C:\CORPUS\mirror.bat"
```

Bare `mirror.bat` resolves only if the shell is sitting in the repo root, and in Git Bash the unquoted backslashes are escape characters — `cmd` opens an interactive shell and exits **0 having backed up nothing**. So **check the log line rather than the exit code**: the top line of `logs\mirror_log.md` (newest first) must be dated within the last few minutes; the absence of a fresh line is the real failure signal.

It backs up **both repos** — OSINT and Corpus, working trees and full git history — to Dropbox, plus one FreeFileSync pass to `D:`, and writes a dated line at the top of `logs\mirror_log.md`. OSINT is read-only here: the backup reads it and writes elsewhere. RENDER is the last job in the pipeline, so this one call captures everything the run produced.

**The freshness check:**

```bash
python scripts/lint-mirror-freshness.py     # 0 clean · 1 stale or failed · 2 nothing recorded
```

It rules on three things: the newest mirror line recording `FAIL`; that line predating the newest `· render ·` line; and plain age (`--max-age-hours`, default 72 — the catch for a quiet fortnight in which nothing happened for the first two tests to compare against). Commits landed since the mirror are reported, not gated. **It reports and never fixes**: `mirror.bat` mirrors *onto* the backup copies, a destructive write a lint does not get to fire on its own opinion. Run it before the mirror to see whether one is owed, and after to confirm the line landed.

**RENDER runs the mirror.** The runbook is the authorisation and the destination is a backup whose purpose is to be overwritten by the current state. What stays Bill's is firing one *outside* a run.

## If something fails

- A single report failing to render does not stop the loop or the run — note it, continue, deploy the rest, list it in `logs/messages-for-bill.md`.
- A WeasyPrint/system-library error is environmental, not a repo bug — surface it. If it takes down every document, that is the whole run failing: log it and stop.
- **Nothing here is a question for Bill.** The one hard stop is Step 0, a mechanical test with a stated repair.
- Do not write anything to OSINT (`C:\OSINT`) under any circumstance; nothing in this runbook needs to.
