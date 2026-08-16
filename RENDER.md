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
The renderers read `outputs/` directly *(2026-08-16)*. They were written against `upstream/`, a mirror of `outputs/` that RENDER refreshed on every run; the repoint this file used to defer has been done and `upstream/` is deleted. There is no copy step and no second tree that can go stale.

## Prerequisites

- Python 3 with WeasyPrint and its system libraries installed. On this machine (2026-08-13): MSYS2 at `C:\msys64` provides Pango/Cairo/HarfBuzz, and `C:\msys64\mingw64\bin` sits on the user PATH **after** the Python entries but **before** `C:\Program Files\Tesseract-OCR`. Both halves of that ordering matter: MSYS2 ships its own `python.exe`, so putting it earlier shadows the real interpreter, while Tesseract ships an older copy of the same Pango DLLs, so putting it later makes WeasyPrint fail with `cannot load library … error 0x7f`. If a render errors on a missing or unloadable shared library, check that ordering first.
- `pypdf`, for the leak gate's PDF text scan (`pip install pypdf`). Without it the gate fails closed on the first PDF rather than skipping it.
- Run every command from the repo root (`C:\CORPUS`).
- Commit after each coherent step (repo convention).

## Step 0 — start from a clean tree

Commit anything outstanding first, so the render's own commits are isolated and no uncommitted work is at risk:

```bash
git add -A && git diff --cached --quiet || git commit -m "Commit outstanding work before render"
```

A no-op if the tree is already clean.

## Step 1 — stamp the commit the site is built from

```bash
git rev-parse HEAD > BUILT-FROM
```

`BUILT-FROM` sits at the repo root and records the Corpus commit this render was cut at; `render.py`, `home.py` and `country.py` read it and print it as the site's provenance stamp (`documentation/design.md` §8). One line, and it is the whole of what Step 1 used to do.

*(Until 2026-08-16 this step mirrored `outputs/` into `upstream/` with `robocopy /MIR` and wrote `BUILT-FROM` there, because the renderers read that path. The repoint the old text deferred is done: every renderer reads `outputs/` directly and `upstream/` is gone. `scripts/pull.py` still writes an `upstream/` and is now orphaned — it belongs to the retired OSINT `outputs/` pull, not to this build.)*

## Step 2 — render every report to HTML + PDF

`render.py` takes one markdown file and writes HTML + PDF into `site/reports/…`. Loop it over every report document. *(2026-08-14: the output tree is now taken from the source path, not hardcoded — a document under `outputs/topics/` renders to `site/topics/`. Nothing changes for the unit reports.)*

**Render everything. RENDER does not judge its input** *(Bill, 2026-08-13)*. Whether a document is fit to publish is BUILD's responsibility — BUILD.md § Narrative integrity — and a render that second-guesses it is a second, weaker copy of that judgement in the wrong place.

```bash
rendered=0; failed=0
for md in outputs/reports/*/*-status.md outputs/reports/*/*-progress.md outputs/reports/*/*-monthly.md \
          outputs/topics/*/*-progress.md outputs/topics/*/*-monthly.md; do
  [ -e "$md" ] || continue
  if python scripts/render.py "$md"; then rendered=$((rendered+1)); else echo "RENDER FAIL: $md"; failed=$((failed+1)); fi
done

# Coverage assertion: the patterns above must have reached every report document.
present=$(find outputs/reports outputs/topics -name '*.md' | wc -l)
echo "rendered $rendered of $present report documents ($failed failed)"
if [ "$rendered" -ne "$present" ]; then
  echo "RENDER ABORT: $((present - rendered)) document(s) did not render — do not deploy"
  [ "$failed" -gt 0 ] && echo "  $failed failed in render.py (see RENDER FAIL above)"
  echo "  and any listed below matched no pattern in the loop:"
  find outputs/reports outputs/topics -name '*.md' | grep -Ev -- '-(status|progress|monthly)\.md$'
fi
```

Today that is 54 status + 57 progress + 54 monthly = 165 place documents, plus 76 topic documents (*Topics* below) = **241**, each as HTML and PDF — but **the assertion is what to trust, not the number**, which moves as units are initialised and as the taxonomy grows.

**The count is asserted because a shrinking loop is silent** *(2026-08-14)*. The `|| echo "RENDER FAIL"` above only fires for a document that was *tried* and failed; it says nothing about one the shell never listed. When the monthly and progress filenames dropped their month, the old `*-progress-*.md` and `*-monthly-*.md` patterns stopped matching anything, and the loop would have quietly rendered 54 documents instead of 165 with no error and a zero exit. Step 1's `/MIR` deletes the old filenames in the same run that breaks the match, so there is no second chance to notice. `site/` is not mirrored and not purged, so all 111 monthly and progress pages would have gone on being served at their last-rendered state indefinitely — the same stale-page failure described below, reached by a different route. The assertion enumerates without a pattern, so no future rename can shrink the set in silence.

This replaces an earlier rule that skipped any monthly carrying an unwritten-narrative marker. Skipping was worse than useless: it never retracted what an earlier render had already published, so a withheld document kept its stale page on the site indefinitely — on 2026-08-13, `TCD-monthly` and `TGO-monthly` were still serving pages rendered on 08-11 from markdown the run had deliberately declined to publish.

## Step 3 — build the home page

```bash
python scripts/home.py            # -> site/index.html
```

It reads catalogue counts from `outputs/catalogue/`. If `outputs/catalogue/stats.json` does not yet exist it falls back to counting `raw-catalogue.csv` — either is fine.

## Step 4 — build the country, region and topic pages

```bash
python scripts/country.py         # every country -> site/countries/{ISO}/index.html (+ finance.html)
python scripts/topic-page.py      # every topic   -> site/topics/{slug}/index.html (+ Level-1 index pages)
```

**`topic-page.py` runs after Step 2, not before it.** It writes the landing page each home-page topic box opens — the two documents, their periods and their dated PDFs — by reading what Step 2 actually rendered and what BUILD wrote into `outputs/topics/`. Run before the documents exist, it writes pages advertising nothing. It also writes an `index.html` for each of the ten Level-1 categories, which is what the *All {category}* box at the end of each sub-topic row opens; that page is an index of the topics beneath it and says plainly that it is not a report.

`country.py` builds the 54 country pages (those in `FULL_NAMES`). The 3 regions (XAF, XSA, XWA) publish as their rendered **progress** report sets from Step 2, linked under the home page's Regions section — they do not currently get a country-style page. If regions should get their own landing pages, that is a small extension to `country.py`, not a blocker for this render.

## Step 5 — build the catalogue page

`scripts/catalogue.py` (promoted from the prototype) writes the browse-and-filter surface and publishes the full downloads. It reads `outputs/catalogue/raw-catalogue.json` and the vocabularies snapshotted in `outputs/vocab/`.

```bash
python scripts/catalogue.py       # -> site/catalogue/index.html, catalogue-data.js, raw-catalogue.{csv,json}
```

Expect ~9,400 records. The page carries metadata only; each record links to its publisher. If the place/topic labels look stale, refresh `outputs/vocab/countries.csv` and `outputs/vocab/taxonomy.md` from OSINT's `lookups/` and re-run.

## Step 6 — build the non-state finance landing

```bash
python scripts/finance.py         # -> site/finance/index.html + all-nonstate.csv
```

This is the page the site nav's **Finance** link points at; without this step that link 404s. Expect ~1,230 deals and a headline total near US$91,000m.

Per-country finance is separate and already covered by Step 4: `scripts/country.py` writes a `finance.html` beside each country's `index.html` from `{ISO3}-nonstate.csv`.

**The page layout is a shell, deliberately.** `finance.py`'s aggregation is real and its numbers are correct; the presentation is a placeholder awaiting design — headline totals, top financiers, by-sector and by-place tables, links down to each country's finance page. It is wired in because a plain page beats a 404, not because it is finished.

## Step 7 — verify, commit, deploy

```bash
# leak gate — no verbatim source body may reach the public site or outputs
python scripts/leak-check.py site outputs || { echo "STOP: leak gate failed"; exit 1; }
# every report links only to held sources — spot check a few if desired:
#   python scripts/report-render.py --unit KEN --check   (needs the workroot; optional)
git add site && git commit -m "Render site from Corpus-owned outputs: reports, home, country pages"
```

**The leak gate is the only STOP here, and that is deliberate** *(Bill, 2026-08-13)*. It guards a boundary RENDER alone can see — the moment artefacts enter a public repo — which is why it belongs at this step and fails the run.

RENDER does **not** judge whether a document is fit to publish. An earlier version of this step grepped `site/` for an unwritten-narrative marker and stopped the render on a hit; it has been removed. Fitness is BUILD's responsibility (BUILD.md § Narrative integrity), and a check here could only ever be a second, weaker copy of a judgement made better upstream — one that halted every render while narratives were still being authored, protecting nothing.

Deploy is unchanged (`documentation/handover.md`): the GitHub Pages workflow publishes whatever is committed in `site/` on a push touching `site/**`. It does not build — the render above is the build. Push to trigger it.

## Topics

Topic documents are authored by BUILD (`BUILD.md` stage 6) and arrive in `outputs/topics/{slug}/`, two per Level-2 taxonomy slug, 76 of them. They render exactly like the place reports and RENDER judges them no more than it judges anything else. `render.py` takes its output tree from the source path, so they land in `site/topics/{slug}/` with permalinks that agree; nothing needs passing on the command line.

**Step 2's loop and its coverage assertion already reach them** — both trees, one assertion, one number to trust. There is nothing extra to run here. Step 1's mirror carries the tree across for free, since it mirrors `outputs/` whole.

**The home page's Topics boxes are wired to these** *(2026-08-14)*. Each Level-2 box opens `/topics/{slug}/`, written by `scripts/topic-page.py` in Step 4; the box hrefs use the hyphenated slug, as the tree does. Until that day they pointed at `/topics/{dotted.slug}/` and would have 404'd — nothing caught it because nothing was published under either name, so **if the taxonomy grows a slug, check the link, not just the box**: `python - <<'EOF'` over `site/index.html` comparing every `/topics/…` href against `site/topics/…/index.html` is the whole test, and it is worth re-running after any change to either script.

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

Then run the repo backup, by absolute path:

```bat
cmd /c C:\CORPUS\mirror.bat
```

**Name the path in full.** Bare `mirror.bat` resolves only if the shell happens to be sitting in the repo root — true when a person types it after working there, false for a shell a session spawns, which is where it failed on 2026-08-13 with *"'mirror.bat' is not recognized"*. That failure is at least loud; the script itself is safe to call from anywhere, since it uses `%~dp0` for the FreeFileSync batch and absolute paths for both repos.

**Run it from PowerShell, not from bash, and check the log line rather than the exit code** *(2026-08-14)*. In Git Bash the backslashes in an unquoted `C:\CORPUS\mirror.bat` are escape characters, so the word reaches `cmd` as `C:CORPUSmirror.bat`; `cmd` consumed no command, opened an interactive shell, and exited **0** having backed up nothing. That is the silent version of the failure above — a green exit and no mirror — and it is why the exit code alone cannot be trusted here. Use `& cmd /c "C:\CORPUS\mirror.bat"` from PowerShell, then confirm `logs\mirror_log.md` carries a line dated within the last few minutes. The absence of a fresh line is the real failure signal.

It backs up **both repos** — OSINT and Corpus — mirroring each one's working tree and full git history to Dropbox, plus one FreeFileSync pass to `D:` (which carries both repos and Bill's `Dropbox\Github`), and appends a dated line to `logs\mirror_log.md`. OSINT is read-only here: the backup reads it and writes elsewhere, never into OSINT. Because RENDER is the last job in the pipeline, this one call captures everything the run produced, `outputs/` and `site/` included. A non-zero exit means a leg failed — see `logs\mirror_log.md` and the FreeFileSync log.

**Owed: an automated freshness check over `logs\mirror_log.md`** *(2026-08-16, not yet built)*. All backups are Corpus's now — OSINT runs none and its own `LINT` #19 retires with its mirror (`documentation/osint-migration.md` R8). #19 existed because the mirror once went a week stale in silence, and it is the only automated guard either repo has ever had; the paragraph above replaces it with a human being asked to eyeball a timestamp, in the same breath as explaining that the exit code cannot be trusted. One mirror now covers both repos, so a silent lapse loses both. The check belongs here, on the same skeleton as OSINT's — newest line in `logs\mirror_log.md` against the newest render, plus a `FAIL` state — and reports rather than fixes, since firing a `/MIR` is Bill's.

## If something fails

- A single report failing to render should not stop the loop — note it and continue; report the list of failures.
- A WeasyPrint/system-library error is environmental, not a repo bug — surface it rather than working around it.
- Do not write anything to OSINT (`C:\OSINT`) under any circumstance; nothing in this runbook needs to.
