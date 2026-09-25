---
type: doc
reader: cc
title: The render — why each step is where it is
last_reviewed: 2026-09-20
---

# The render — why each step is where it is

*(Spec for `RENDER.md`. The runbook says what to run and in what order; this says why, and what each check exists to catch. **Where another file already owns an argument this points at it.**)*

## The shape of the job

RENDER turns Corpus-owned `outputs/` — already built, already committed — into `site/`, and pushes. No pull, no second tree. `design.md` §8 and §9 are the frame; most of what follows protects §9, *a published file is never revised*.

**RENDER judges nothing about its input.** Fitness to publish is BUILD's (`BUILD.md` → *Narrative integrity*); a check here would be a weaker copy in the wrong place. That is why Step 0 is the only stop, and why a render never puts a question mid-stream: where it wants Bill's attention it finishes the job and writes a block.

**No count, size or total is written into the runbook**: a stale number in a procedure drifts with nothing catching it. The build prints its own figures on the run that wrote them.

## Prerequisites — why the PATH ordering matters

MSYS2 ships its own `python.exe` and Tesseract ships older Pango DLLs, so `C:\msys64\mingw64\bin` has to sit between them. A missing or unloadable shared library (`cannot load library … error 0x7f`) is environmental, not a repo bug.

## Step 0 — why the gate is a sentinel

A build that died mid-stage-4 leaves a tree that renders perfectly: every check passes, and the units that never got their sources are silently a cycle out of date. Nothing downstream can see it, so the test is here and it fails the run.

**Check 1 is the mechanism; the other two are cheap corroboration.** `logs/.build-in-progress` survives exactly one thing — a session that died without saying so. A timestamp test cannot assert that: other jobs legitimately commit `outputs/`, and a died build commits its finished units and writes nothing.

**Never delete the sentinel or hand-write a log line to get past it** — either forges the claim that a build finished. The repair is to run BUILD, which resumes where it stopped.

The "commit anything outstanding" line runs **after** the gate: running it first would satisfy check 3 by committing the very work whose being uncommitted is the evidence. In a cycle there is no repair at the seam at all — `CYCLE.md` owns that.

## Step 2 — the edition gate and the coverage assertion

**`render.py` decides whether a document has moved**, on §9's rule: an edition is cut when the content changes, not when a build runs. It digests each source's body below the frontmatter, reads the digest back off the page it wrote last time, and leaves an unchanged document alone — page and PDF both — counting it as rendered. A document that moves twice in a day gets a `-2` suffix, never an overwrite.

**A held-off document is not restyled**, because the PDF embeds the stylesheet: a CSS change reaches new editions only. `--force` cuts every edition and is a decision, not a habit. Assets are stamped with a digest of their own bytes (`main.css?v=22ef527a`), so the query string changes exactly when the file does.

**The count is asserted because a shrinking loop is silent**: a rename moves filenames out of the glob, the loop renders a subset with a zero exit, and `site/` — never purged — serves the old pages indefinitely. The assertion enumerates without a pattern. `progress-narrative-archive.md` is excluded **by exact filename**, and nothing else is forgiven.

**The two ways of coming up short are different failures.** A document the loop **never listed** stops the run. A document **tried and failed** does not: it keeps its previous render either way, so withholding the other pages protects nothing.

## Steps 3, 4 and 4a — what reads what, and the ordering that follows

`home.py` writes three pages from one set of catalogue counts — home, the country matrix, the taxonomy matrix. The topics page prints `lookups/taxonomy.csv` in its order and wording, so it goes stale when a subject is added there.

**`topic-page.py`, `region.py` and `progress.py` run after Step 2** because each reads what Step 2 actually rendered: the landing page a topic box opens, a region's Reports section, an indicator row's bookmark inside a topic progress report.

**`region.py` reuses `country.py`'s machinery** — report rows, the finance pivot, the catalogue cut. Regions differ in one thing: a region issues a monthly update and a progress report, never a status (`REPORT-REGION.md`). **`site/metadata/non-state-finance-metadata.csv` is one field dictionary for the whole site**, hand-maintained and undated because it describes a shape, not a finding; both builders refuse to build without it.

**Progress is one builder and two readings of one grid**: a 54 × 121 frame with a value in every cell, counted down the columns for `/progress/` and down the rows for `/progress/countries/`. The row sums are asserted — a build where one does not has misread a report. **It reads the published reports, not `indicators.csv`**, whose per-country CSV holds only the rows carrying evidence, so *No evidence* stays a number a report states rather than a subtraction. `check_links()` refuses to build on a missing report or a lost `id`: a dead anchor on the most linked-to page is a defect.

## Step 5 — the catalogue

`catalogue-serving-shape.md` decided the serving shape. What belongs here is what a render has to know.

**Both halves of `site/catalogue/data/` are tracked**, unlike the search shards, because the page cannot draw a row without them, and a `git push` has to be enough to serve a working catalogue. **The chunk files inside are internal** and will change without notice; `raw-catalogue.csv` is the supported way to consume this data. `catalogue-internal.csv` (the same rows plus the slug and the note) is what the report layer and `status_lib` read; neither it nor `raw-catalogue.json` is copied into `site/`.

**The page reads its own column list from `build-catalogue.py` → `CSV_COLS` by syntax tree**, so a cut taken in a reader's browser and the published file cannot disagree.

**The first screen is written into the page**, so it shows results before anything is fetched and with JavaScript off. That markup is written by Python and redrawn by JavaScript, and the two have to agree. **The A–Z sort is decided at build time**: `coll()` ranks the titles and ships one integer per record, so a `#sort=az` link means the same thing for every reader, as `localeCompare` never did.

**Two of the four tests need node**, and a renumbering of the row's fields is what gets made on a machine without it. A catalogue row is a positional array read in four places — `pack_rows` packs it, `row_html` draws it, `split` projects four fields into the chunks, `rowOf` puts it back — and a slot that shifts in three of them silently draws another record's URL under this title. `test_catalogue_rowshape.py` reads all four out of `catalogue.py` and compares the positions: the part of the node pass that always runs.

## The alert pages

`alerts.py` runs after `catalogue.py` and from the same `raw-catalogue.json`, so the alert menus carry the vocabulary the catalogue's facets carry. `catalogue-alerts.md` is the design and owns the window, the backfill rule and the record shape; `workers/alerts/README.md` points at it from the code. Three things are the render's own:

- **`recent.json` is rewritten every render and is tracked**, like the catalogue's `data/` payload, because a `git push` has to be enough to make the alerts work.
- **Nothing in it is unpublished**: its columns are a subset of `CSV_COLS` plus a hash of the URL, and `test_alerts.py` asserts that rather than trusting the loop.
- **`test_alerts_worker.py` is the Worker's whole test suite and runs without Cloudflare.** `worker.js` is written in two halves with a marker line between them, and everything above it is pure and loads straight into a JavaScript engine. Node is preferred, Duktape (`dukpy`) is the fallback because node is not installed here; it skips with neither.

The Turnstile site key is a constant in `alerts.py`; until the widget exists the build prints a line saying the form will not submit.

## The search indexes

`build-names-index.py` (BUILD stage 2b, from the workroot) writes `outputs/names/`; `build-title-index.py` (stage 2d) writes `outputs/titles/`, on the same machinery (`shard_lib.py`). `catalogue.py` packs both sets of shard keys into the page.

**The title index *is* the page's title search** — the per-row search blob carries neither the title nor the hero. It reads only `outputs/`, so it can be rebuilt without the vault; it sits in stage 2 because that is when the catalogue it reads was written. **What a query can and cannot reach is in that script's own header.**

**`build-entity-names.py` (stage 2c) writes `lookups/entity-names.csv`**, a display name per entity slug derived from the slug's own sources; `catalogue.py` names the unnamed rest at build time, for the baked first screen. Only the derived names join the search blob. **The file is meant to be corrected by hand**: `basis: hand` is never overwritten. It is Corpus's file, the slugs are OSINT's.

**The shards are exempt from §9, deliberately.** Nothing cites a shard; it must track the corpus, so shards are rewritten in place and stale ones deleted. Ids are append-only and both writers compare before writing, so expect a handful of changed shards per cycle. **A rebuild that changes all of them means the id registry was rewritten rather than appended to**, which is why `outputs/catalogue/doc-ids.csv` is tracked and must stay so.

The shards are served from R2 and tracked in neither tree; `catalogue.py` still writes them into `site/` because that is what `r2-sync.py` uploads from.

## The prose, and the finance tables

**Every explanatory paragraph the site shows a reader lives in `content/`**, read by `copy_lib.py` — `copy()` for HTML, `copy_inline()` without the wrapping `<p>`, `copy_md()` for emitters whose output `render.py` converts later. `editing-content.md` is the fuller account. Two rules are the build's: **a missing key stops the build**, because a page without its paragraph looks finished and is not; and **placeholder values arrive pre-formatted**, because a format spec inside a content file puts presentation logic back in what the editor thinks is plain text.

**The finance tables are drawn in the browser** by `site/assets/js/datatable.js` from the published CSV the page already offers. With JavaScript off neither table appears, so both carry a `<noscript>` block naming the CSV: the data is never behind the script. `datatable.css` is kept out of `main.css` because that file is a copy with its own provenance marker (`MAIN-CSS-FROM`).

The component is a port of the Lab's datatable (`data-landscapers/assets/shared/` is canonical), documented in its own header. It parses CSV by character scan, because quoted fields carry newlines, and sorts blank amounts last in both directions, because a missing figure is not a small one. `prototypes/datatable-test.mjs` drives the built pages in jsdom, which has no layout — the sticky header and column-width sync need a browser.

**The line-endings trap keeps its statement in the runbook**, because it is a §9 rule and the runbook is where a session meets it.

## Steps 6a and 6b — retention, and where the editions live

`cloudflare.md` owns the delete-unless-downloaded rule and `editions-serving-shape.md` the move to R2. What the ordering buys: **6a runs before Step 7's `git add site`**, so a deletion rides the same commit as the render that superseded the file; **6b runs after 6a**, so an edition the pruner has just retired is never uploaded, **and before Step 7**, so the editions this render cut never enter git at all.

**The two refusals differ because the consequences do.** A declined prune suspends retention for a night, so it exits 0. A declined R2 sync leaves the tree growing against the 1 GB ceiling, so it exits 1 and wants acting on. Either way the site is serving, because the Worker falls through to Pages for anything the bucket does not hold. The two steps use **different credentials** — a KV token for 6a, an R2 key pair for 6b.

**`--check-serving`** asks the live site which origin answered for a sample of keys — the only check that the selection rule in `r2-sync.py` and in the Worker agree.

## Steps 6c and 6d

**The lookups annex reads data**: its tables are drawn at build time from the files they list — `lookups/`, the sweep lists BUILD stage 1 snapshots into `outputs/vocab/`, and `site/metadata/` — and each is offered as a CSV beside the page. `PAGES` in `methodology.py` is the list; adding a page means a row there and a content file, nothing else. Neither step writes an edition and nothing either produces is citable, which is why both are safe to run alone.

## Step 7 — the two page-wide checks

Both assert a property invisible in any diff.

**External links.** That every link leaving the site opens a new tab is asserted nowhere else, and a builder that stopped applying `target` looks exactly like a page nobody edited. `lint-external-links.py` checks the built tree *and* the builders, so a script that takes its chrome from `chrome_lib` and writes a page without `external_links()` is reported before it has rendered anything (`house-style.md` → *Links*).

**Structured data.** The `application/ld+json` block on every report, and the `Dataset` block on the catalogue, the finance table and every place's cut of both, has one consumer: a crawler that never reports back. Every assertion in `lint-structured-data.py` is *this page disagrees with itself* or *this value is not the type it claims* — its header says why each is there, and `test_lint_structured_data.py` proves it fails where it should. It also fails on a block that is neither shape: a builder not calling `structured_data.py`.

**The repair for either never cuts an edition** — fix the builder and re-run the step that wrote the page, or `render.py --repage` for a report — so a finding can stop the push at no cost.

**The push is not the deploy.** The Pages workflow publishes what is committed; it does not build, and its deploy step sometimes fails on GitHub's side — which is why the runbook reads the workflow run rather than trusting the push.

## The bulletin

`bulletin.md` is the design and `bulletin-archive.md` the archive's. The runbook names the three ways it differs from every other document; the reasons are here.

**Its page is refreshed on a held-off render** because freshness is itself news — *we looked, and nothing was published*. For `type: bulletin` the gate holds the edition and `render.py` rewrites the page under the edition it is holding, PDF untouched. The digest is still the body, so a moved clock cannot cut an edition.

**It leaves the download rule** so the one-week retention promise holds for every bulletin — which is also why bulletin retention needs no Cloudflare token.

**An empty window still renders** because the document says so in its own prose. The home page's Bulletin section is omitted entirely when the document does not exist.

It is also the one page carrying a script — `bulletin-filter.js`, in the HTML pass only. The control renders `hidden` and the script unhides it, so a failed script leaves no dead control.

## The mirror

`mirror.bat` backs up **both repos** — working trees and full git history — to Dropbox, plus a FreeFileSync pass to `D:`. OSINT is read-only here: the backup reads it and writes elsewhere. RENDER is the last job in the pipeline, so one call captures everything the run produced, and the runbook is the authorisation — the destination exists to be overwritten by the current state.

**The exit code cannot be trusted**: a bare `mirror.bat` resolves only from the repo root, and in Git Bash `cmd` can exit 0 having backed up nothing. Hence the log-line check.

`lint-mirror-freshness.py` rules on a `FAIL` line, a mirror line older than the newest RENDER line, and plain age — the catch for a quiet fortnight. **It reports and never fixes**: `mirror.bat` is a destructive write onto the backup copies, which a lint does not fire on its own opinion.

## The log line

The clock is stamped **before** the Step 0 gate, so a Step 0 stop logs a duration too. `CLAUDE.md` → *Be decisive* owns the message caps.
