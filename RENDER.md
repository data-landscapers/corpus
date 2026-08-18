---
type: runbook
title: Render the site — instruction for Claude Code
last_reviewed: 2026-08-16
---

# Render the site — runbook for Claude Code

*(Hand this to Claude Code running in the Corpus repo on Bill's machine. It renders every site page from Corpus-owned `outputs/`. Read `documentation/handover.md` and `documentation/design.md` §8 first. OSINT is read-only and is not touched by any step here. **To run this straight after `BUILD.md` as one job, use `CYCLE.md`**, which orders the two and changes nothing here; this file is unaffected by it and runs alone exactly as written, Step 0 included.)*

## What changed, and why this runbook exists

Corpus now **authors** its report and compile layer itself, in `outputs/` (see `documentation/migration-report-layer.md`). It is no longer a mirror pulled from OSINT.
So the build no longer starts with a pull. It starts from `outputs/`, which is already in the repo and committed. *(`scripts/pull.py` and its test were deleted on 2026-08-16; the leak gate they carried lives in `scripts/leak-check.py`, tested by `scripts/test_leak_check.py`.)*
The renderers read `outputs/` directly *(2026-08-16)*. They were written against `upstream/`, a mirror of `outputs/` that RENDER refreshed on every run; the repoint this file used to defer has been done and `upstream/` is deleted. There is no copy step and no second tree that can go stale.

## Prerequisites

- Python 3 with WeasyPrint and its system libraries installed. On this machine (2026-08-13): MSYS2 at `C:\msys64` provides Pango/Cairo/HarfBuzz, and `C:\msys64\mingw64\bin` sits on the user PATH **after** the Python entries but **before** `C:\Program Files\Tesseract-OCR`. Both halves of that ordering matter: MSYS2 ships its own `python.exe`, so putting it earlier shadows the real interpreter, while Tesseract ships an older copy of the same Pango DLLs, so putting it later makes WeasyPrint fail with `cannot load library … error 0x7f`. If a render errors on a missing or unloadable shared library, check that ordering first.
- `pypdf`, for the leak gate's PDF text scan (`pip install pypdf`). Without it the gate fails closed on the first PDF rather than skipping it.
- Run every command from the repo root (`C:\CORPUS`).
- Commit after each coherent step (repo convention).

## Running unattended — a run never stops to ask

**RENDER puts no question mid-stream** *(Bill, 2026-08-16)*. It is run straight after `BUILD.md` with nobody watching. A run ends two ways — it **finishes** or it **fails** — and a failure is an error it cannot get past, never a decision it would rather Bill made. Where it wants his attention, it finishes the job and writes a block under the marker in `logs/messages-for-bill.md`: what it would have asked, what it did instead, what his options are.

This is easier to hold to here than in BUILD, because RENDER judges nothing about its input by design. Its two hard stops are named and both are mechanical: **Step 0**, a build that did not finish, and **Step 7**, the leak gate. Everything else is rendered, committed and deployed.

## Step 0 — a finished build behind you, then a clean tree

**Stamp the clock first, before the gate** *(Bill, 2026-08-17)*, so the run's log line can say how long it took:

```bash
python scripts/log-line.py --start render
```

Before the gate rather than after it, because a Step 0 stop logs a line too and a stop that took twenty minutes to reach is worth being able to see. The stamp lives in the gitignored `logs/.run-start-render`; the closing call in **Log** reads it back and clears it, and a run that skipped this writes `unclocked` rather than dropping the field.

**Check the build finished before rendering a line of it** *(2026-08-16)*. A build that ran out of road mid-stage-4 leaves a tree that renders perfectly: every document is well-formed, every link resolves, every check passes, and the units that never got their new sources are silently a cycle out of date. Nothing downstream can see that, which is why the test is here and why it fails the run rather than warning.

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

**Check 1 is the mechanism and the other two are cheap corroboration** *(2026-08-16)*. `BUILD.md` stage 0 writes `logs/.build-in-progress` and its ending sequence removes it — on a clean finish and on a logged error alike, because both are runs that accounted for themselves. The file therefore survives exactly one thing: a session that died without saying so. That is a direct statement of the condition rather than an inference from timestamps, and the distinction is the reason this check is shaped the way it is.

**The timestamp test was tried first and does not work** *(2026-08-16)*. *Refuse when `outputs/` carries commits newer than the newest `· build ·` line* reads like the obvious implementation and fails on the live repo, because BUILD is not the only job that writes `outputs/`: `STATUS-INIT` rewrites a country's baseline and commits it, which puts fresh `outputs/` commits above the last build line as a matter of course. Every render following a baseline session would have stopped.
**Nor is it rescued by having STATUS-INIT log**, which it now does (`STATUS-INIT.md` stage 3 step 14, added the same day). Generalise the test to the newest line of *any* job and it inverts into a false negative: a BUILD that dies at unit 20 of 45 commits those twenty and writes nothing, and the next baseline session's line then sits above them and clears the half-finished build through a gate built to catch exactly it. The sentinel asserts the thing itself — a run started and never accounted for — and has neither failure mode.

**All three log and stop** — `python scripts/log-line.py render "stopped at step 0: <which> — not rendered"` — and write a message. None of them is repaired here. **The repair is to run BUILD**, which resumes exactly where it stopped, because stage 4 reads a set difference over slugs and every unit it finished is already marked. Do not delete the sentinel or hand-write a log line to get past this: both are assertions that a build finished, and forging one publishes the half-built tree the check exists to catch.

Then commit anything else outstanding, so the render's own commits are isolated and no uncommitted work is at risk:

```bash
git add -A && git diff --cached --quiet || git commit -m "Commit outstanding work before render"
```

A no-op if the tree is already clean. **It runs after the gate, not before, and the order is load-bearing** — this commit sweeps up everything, `outputs/` included, so running it first would quietly satisfy check 3 by committing the very work whose being uncommitted is the evidence. The gate reads the tree as the build left it; this then tidies what the gate has already ruled on.

## Step 1 — stamp the commit the site is built from

```bash
git rev-parse HEAD > BUILT-FROM
```

`BUILT-FROM` sits at the repo root and records the Corpus commit this render was cut at; `render.py`, `home.py` and `country.py` read it and print it as the site's provenance stamp (`documentation/design.md` §8). One line, and it is the whole of what Step 1 used to do.

*(Until 2026-08-16 this step mirrored `outputs/` into `upstream/` with `robocopy /MIR` and wrote `BUILT-FROM` there, because the renderers read that path. The repoint the old text deferred is done: every renderer reads `outputs/` directly and `upstream/` is gone. `scripts/pull.py`, which was the only thing that would have recreated an `upstream/`, was deleted the same day along with `scripts/test_pull.py`.)*

## Step 2 — render every report to HTML + PDF

`render.py` takes one markdown file and writes HTML + PDF into `site/reports/…`. Loop it over every report document. *(2026-08-14: the output tree is now taken from the source path, not hardcoded — a document under `outputs/topics/` renders to `site/topics/`. Nothing changes for the unit reports.)*

**Render everything. RENDER does not judge its input** *(Bill, 2026-08-13)*. Whether a document is fit to publish is BUILD's responsibility — BUILD.md § Narrative integrity — and a render that second-guesses it is a second, weaker copy of that judgement in the wrong place.

**The loop still hands over every document; `render.py` decides whether any of them has moved** *(2026-08-18)*. That is not a judgement about fitness — it is the rule `documentation/design.md` §9 already states: *an edition is cut when the content changes, not when a build runs*. It had never been implemented on this side. The edition is the render date, so the loop above cut a new dated PDF for all 241 documents on every render day and kept it for ever, which is how 1,053 PDFs and 314 MB accumulated in the fortnight from 2026-08-05. `render.py` now digests each source's body below its frontmatter, reads the digest back off the page it wrote last time, and leaves an unchanged document alone — page and PDF both. Expect most documents to report `edition unchanged` on most runs, and the count above to be unaffected: a document that was held off was handled, exits zero, and counts as rendered.

**A document that moves twice in a day gets a second edition, not an overwritten one** *(2026-08-18)*. §9's `-2` suffix is implemented alongside the gate: an in-day session run to force an update on a live issue now cuts `KEN-status-2026-08-18-2.pdf` and leaves the morning's file exactly as it was published. `country.py` and `topic-page.py` read editions through `render.py` rather than parsing filenames themselves, so the country and topic pages offer the newer of the two.

**A held-off document is not restyled, and that is the point.** The PDF embeds the stylesheet, so a change to `report.css` or to the template in `render.py` reaches new editions only. A retained edition is not revised after publication (§9), so the alternative — restyling what is already published — would change the bytes under a citation. To push a presentation change through the whole set deliberately, pass `--force` in the loop; it cuts 241 editions, so it is a decision, not a habit.

**The first run after 2026-08-18 cuts an edition for every document**, because no page yet carries the record the gate compares against. That is the same call `report-render.py` makes for a document with no stored digest: wrong only in the safe direction, and once.

```bash
rendered=0; failed=0
for md in outputs/reports/*/*-status.md outputs/reports/*/*-progress.md outputs/reports/*/*-monthly.md \
          outputs/topics/*/*-progress.md outputs/topics/*/*-monthly.md; do
  [ -e "$md" ] || continue
  if python scripts/render.py "$md"; then rendered=$((rendered+1)); else echo "RENDER FAIL: $md"; failed=$((failed+1)); fi
done

# The two bulletins, HTML only — see Bulletins below.
for md in outputs/bulletins/*-bulletin.md; do
  [ -e "$md" ] || continue
  if python scripts/render.py "$md" --no-pdf; then rendered=$((rendered+1)); else echo "RENDER FAIL: $md"; failed=$((failed+1)); fi
done

# Coverage assertion: the patterns above must have reached every report document.
present=$(find outputs/reports outputs/topics outputs/bulletins -name '*.md' | wc -l)
missed=$((present - rendered - failed))
echo "rendered $rendered of $present report documents ($failed failed, $missed never listed)"
if [ "$missed" -gt 0 ]; then
  echo "RENDER STOP: $missed document(s) matched no pattern in the loop — do not deploy:"
  find outputs/reports outputs/topics outputs/bulletins -name '*.md' | grep -Ev -- '-(status|progress|monthly|bulletin)\.md$'
  exit 1
fi
if [ "$failed" -gt 0 ]; then
  echo "$failed document(s) failed in render.py (see RENDER FAIL above) — deploying the rest; message Bill"
fi
```

**The two ways of coming up short are not the same failure and no longer share an outcome** *(2026-08-16)*. The old assertion fired on `rendered -ne present`, which lumped them together, printed *do not deploy*, and then let the runbook walk straight on into Steps 3 to 7 and deploy — advice with nothing behind it, and the sort of thing an unattended run either obeys too much or ignores.

- **A document the loop never listed stops the run.** That is the silent-shrink failure this assertion was built for: a rename moves a filename out of the glob and the loop quietly renders a subset with a zero exit, while `site/` keeps serving the old pages indefinitely because it is never purged. Nobody can see it from the output, so it fails the run — log, message, no deploy.
- **A document that was tried and failed does not.** One report that will not typeset is a known, visible, single-page fault, and withholding the other 240 pages to punish it is a worse outcome by every measure — the failed page keeps its previous render either way, exactly as the stale-page paragraph below describes, so stopping protects nothing and costs the whole cycle. Note it, render on, deploy, and put the list in `logs/messages-for-bill.md`.

Today that is 54 status + 57 progress + 54 monthly = 165 place documents, plus 76 topic documents (*Topics* below) = 241 as HTML and PDF, plus the 2 bulletins as HTML alone = **243** — but **the assertion is what to trust, not the number**, which moves as units are initialised and as the taxonomy grows.

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
git push
```

**The leak gate is the only STOP here, and that is deliberate** *(Bill, 2026-08-13)*. It guards a boundary RENDER alone can see — the moment artefacts enter a public repo — which is why it belongs at this step and fails the run.

RENDER does **not** judge whether a document is fit to publish. An earlier version of this step grepped `site/` for an unwritten-narrative marker and stopped the render on a hit; it has been removed. Fitness is BUILD's responsibility (BUILD.md § Narrative integrity), and a check here could only ever be a second, weaker copy of a judgement made better upstream — one that halted every render while narratives were still being authored, protecting nothing.

Deploy is unchanged (`documentation/handover.md`): the GitHub Pages workflow publishes whatever is committed in `site/` on a push touching `site/**`. It does not build — the render above is the build. The push above is what triggers it.

**The push is authorised by this runbook and is not a question to put** *(2026-08-16)*. It publishes to the open web, which is the kind of step that would ordinarily be worth confirming — but a render that stops to ask permission to deploy is a render that has done all of its work and shipped none of it, and running RENDER *is* the instruction to publish. It used to sit in this file as a bare sentence of prose rather than a command, which is how it came to look optional; the log shows every completed render pushing. The gate on publishing is the leak gate immediately above, and it has already run by this point.

## Bulletins

The two daily bulletins are authored by BUILD (`BUILD.md` stage 7) and arrive in `outputs/bulletins/`, covering what was published on the day of the build and the day before it. `render.py` puts them at `site/bulletins/{country,topic}-bulletin.html`, with no unit directory between — there are two documents and they are the whole tree.

**They are rendered as HTML and no PDF** *(Bill, 2026-08-17)*. Every other document here cuts a dated PDF because it is a retained edition worth citing away from the site; a bulletin is superseded the next morning and what it reports is kept by the reports, so a dated PDF of one would archive the same news a second time under a worse name. `--no-pdf` is what the loop passes, and the page it writes carries no download button and no hash-and-verify line — a document rendered without a PDF must not advertise one.

**The window is often empty and the documents still render.** A bulletin covering two days on which nothing was published says so in its own prose; there is nothing here for RENDER to judge, and no case in which it skips them.

The home page's Bulletin section (Step 3) is built from these two files' frontmatter and is omitted entirely when they do not exist, so a first render before BUILD has ever written one is not a broken link.

## Topics

Topic documents are authored by BUILD (`BUILD.md` stage 6) and arrive in `outputs/topics/{slug}/`, two per Level-2 taxonomy slug, 76 of them. They render exactly like the place reports and RENDER judges them no more than it judges anything else. `render.py` takes its output tree from the source path, so they land in `site/topics/{slug}/` with permalinks that agree; nothing needs passing on the command line.

**Step 2's loop and its coverage assertion already reach them** — both trees, one assertion, one number to trust. There is nothing extra to run here. Step 1's mirror carries the tree across for free, since it mirrors `outputs/` whole.

**The home page's Topics boxes are wired to these** *(2026-08-14)*. Each Level-2 box opens `/topics/{slug}/`, written by `scripts/topic-page.py` in Step 4; the box hrefs use the hyphenated slug, as the tree does. Until that day they pointed at `/topics/{dotted.slug}/` and would have 404'd — nothing caught it because nothing was published under either name, so **if the taxonomy grows a slug, check the link, not just the box**: `python - <<'EOF'` over `site/index.html` comparing every `/topics/…` href against `site/topics/…/index.html` is the whole test, and it is worth re-running after any change to either script.

## Log

On completion or error, write **one terse line** to `logs/log.md`, in the form `YYYY-MM-DD HH:MM · render · took · what happened`:

```bash
python scripts/log-line.py render "reports+home+countries+catalogue rendered, deployed — ok"
```

On failure, log the stage and error instead (`… errored rendering KEN-status: <message>`). One line per run.

**The duration writes itself** *(Bill, 2026-08-17)*, from the `--start render` stamp taken at Step 0 — the call above is unchanged. It reports the gap between that stamp and now, then clears it, so an error line carries how long the run got before it failed. Where Step 0's stamp was never taken, state it rather than leaving the field empty: `--since "2026-08-17 08:55"` or `--took 21m`.

**And message Bill where the run needed him** *(2026-08-16)*. A block under the marker in `logs/messages-for-bill.md`, written before the commit below so it is carried by it: documents that failed to typeset, a Step 0 stop and what has to be re-run, anything the run decided that he would otherwise have been asked. A clean render writes nothing there.

**The log reads newest first** *(2026-08-16)*, so the line is inserted at the top, under the marker comment — `>> logs/log.md` is no longer the recipe. It would still write a correct line, in the wrong place, which is the version of this that nobody notices. `scripts/log-line.py` does the insert and takes the message as an argument, so `·`, em-dashes, slashes and backticks in it are content rather than syntax; it exits 1 rather than guessing if the marker is missing.

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

**Run it from PowerShell, not from bash, and check the log line rather than the exit code** *(2026-08-14)*. In Git Bash the backslashes in an unquoted `C:\CORPUS\mirror.bat` are escape characters, so the word reaches `cmd` as `C:CORPUSmirror.bat`; `cmd` consumed no command, opened an interactive shell, and exited **0** having backed up nothing. That is the silent version of the failure above — a green exit and no mirror — and it is why the exit code alone cannot be trusted here. Use `& cmd /c "C:\CORPUS\mirror.bat"` from PowerShell, then confirm the **top** line of `logs\mirror_log.md` is dated within the last few minutes — that log reads newest first too. The absence of a fresh line is the real failure signal.

It backs up **both repos** — OSINT and Corpus — mirroring each one's working tree and full git history to Dropbox, plus one FreeFileSync pass to `D:` (which carries both repos and Bill's `Dropbox\Github`), and writes a dated line at the top of `logs\mirror_log.md`. OSINT is read-only here: the backup reads it and writes elsewhere, never into OSINT. Because RENDER is the last job in the pipeline, this one call captures everything the run produced, `outputs/` and `site/` included. A non-zero exit means a leg failed — see `logs\mirror_log.md` and the FreeFileSync log.

**The freshness check is built** *(2026-08-16)*. `scripts/lint-mirror-freshness.py` reads the newest line of `logs/mirror_log.md` and rules on three things: whether that run recorded `FAIL`, whether it predates the newest `· render ·` line in `logs/log.md`, and whether it is simply old (`--max-age-hours`, default 72). The third is not decoration — the first two both compare against *something having happened*, so a quiet fortnight with no render passes them both while the backup ages, which is the week-of-silence that made OSINT's `LINT` #19 necessary in the first place. Commits landed since the mirror are **reported, not gated**: they are the true measure of exposure, but a check that fails all the way through an ordinary working session is one that gets ignored.

```bash
python scripts/lint-mirror-freshness.py     # 0 clean · 1 stale or failed · 2 nothing recorded
```

**It reports and never fixes**: `mirror.bat` mirrors *onto* the Dropbox copies, so a `/MIR` is a destructive write on the destination and a lint check does not get to fire one off the back of its own opinion that a backup is overdue. Run it before the mirror to see whether one is owed, and after it to confirm the line landed.

**That is a rule about the check, not about the run** *(Bill, 2026-08-16, asked directly: "keep RENDER running the mirror")*. This paragraph used to end *"and firing a `/MIR` is Bill's"*, eight lines under a section that instructs the run to fire exactly one — read cold by an unattended session, a flat contradiction on the single destructive step in the job, and the likeliest place in either runbook for one to stop and ask. **RENDER runs the mirror**: it is the last step of the last job in the pipeline, the runbook is the authorisation, and the destination is a backup whose whole purpose is to be overwritten by the current state. What stays Bill's is firing one *outside* a run — which is what `lint-mirror-freshness.py` declines to do on its own. `scripts/test_mirror_freshness.py` proves all three fault paths fire, on the same principle as the leak-gate test: this check will read `ok` for weeks at a time, which is exactly when a broken one goes unnoticed.

*(Why it reads a log rather than trusting `mirror.bat`'s exit code is the paragraph above: a bare or bash-mangled invocation exits 0 having backed up nothing. Only a run that reached the end writes a dated line. This is what replaces `LINT` #19, which retires with OSINT's own mirror — `documentation/archived/osint-migration.md` R8 — and it now covers both repos, since one mirror does.)*

## If something fails

- A single report failing to render should not stop the loop, or the run — note it, continue, deploy the rest, and put the list in `logs/messages-for-bill.md`. Step 2 has the reasoning.
- A WeasyPrint/system-library error is environmental, not a repo bug — surface it rather than working around it. If it takes down every document rather than one, that is the whole run failing: log it and stop, since a deploy of nothing is not worth committing.
- **Nothing here is a question for Bill.** The two hard stops are Step 0 and the leak gate, and both are mechanical tests with a stated repair. Everything else finishes, logs, and leaves a message.
- Do not write anything to OSINT (`C:\OSINT`) under any circumstance; nothing in this runbook needs to.
