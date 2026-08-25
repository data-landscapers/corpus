# CC: rebuilding after the 2026-08-25 country-page and report changes

*(**Addressed to Claude Code, not to Bill.** Every instruction in this file is an instruction to the session that runs the rebuild; nothing in it asks Bill for anything, and nothing in it needs his agreement. It exists because the work was done in Cowork, which cannot run the build — the workroot junctions to OSINT do not resolve in its sandbox, so `raw/` reads as absent and every renderer that checks the catalogue against the base refuses to start. The design reasoning is elsewhere: `design.md` → §3 and §9, `report-layer.md` → §1 and §5, `report-country-skeleton.md` → Sections. This file is only what to run, in what order, and what the run will find.)*

## Run 2026-08-25 19:16-19:35, on Windows — done, and what it found

*(Added by the session that ran it. This section is the outcome; everything from *What changed, in one list* onwards is the original instruction, left exactly as written so the two can be compared.)*

The sequence ran as prescribed and nothing had to be forced. `build-catalogue.py` from `scripts/.workroot/` (10,959 sources, no diff — `raw/` had not moved since the 17:03 build), then `rebuild.py --reports all` over 57 units, then `--check`, then the render loop, `home.py`, `topic-page.py`, `country.py`, `finance.py`. **Checks G, I, J and M pass on all 57 units.** 242 of 242 documents rendered, none failed, none unlisted. Every country-page change verified in the output. Deployed and mirrored.

**Six things the instruction did not predict, in the order they came up.**

**Run `rebuild.py` from the repo root, not from the workroot.** It builds the workroot itself, so from inside one it tries to junction `.workroot/scripts/.workroot/scripts` and dies. `build-catalogue.py` is the opposite — it derives its base from `__file__`, so it wants `python scripts/build-catalogue.py` **from** `scripts/.workroot/`, where that path resolves through the junction. `build-finance-page.py` is the same. Worth knowing before the first traceback rather than after it.

**229 unwritten blocks, not 206**, in exactly the four predicted chapters: capacity 67, data 62, geopolitics 54, digitalisation 46. The shape of the prediction was right and the count was low, because the monthlies carry these blocks too. **No reader-visible defect**: the sections carry their tables and sub-headings, and what is missing is the editorial paragraph. Check L fails on 54 units and gates nothing.

**Check M failed once, on DZA**, which the instruction did not anticipate. `DZA-dpi.govtech-dzair-services` cited `2026-08-20-aps-hcn-six-energy-digital-services`, which the base does not hold — and holds no APS record of that story at all, one APS record in the whole base and it is from last December. The Algérie Eco record that does carry it, `2026-08-21-algerie-eco-hcn-six-energy-digital-services`, already sat **first** in the row's `sources`, so the claim's evidence was never in doubt and the dead slug was simply dropped.

**The 76 topic documents and the bulletin held their editions off, and were repaged.** Their markdown had not moved, so §9's gate correctly left their PDFs alone — which would have left 77 report pages on the site without the contents bar their siblings had just gained. `render.py --repage` exists for exactly this: it rewrote the served pages under the held editions, no PDF and no new edition. Verified afterwards that the held PDFs' mtimes did not move.

**The finance compile was run**, because the instruction anticipates the `gov.policy` relabel reaching the finance tables *once it reruns*. It did — 28 exports, `Strategies plans and policies` → `"Strategies, plans and policies"` — and it brought in one deal the base had gained since it last ran (CDC-CI Capital's seed grants, Côte d'Ivoire). `finance.py` then minted `all-nonstate-2026-08-25.csv`, a correctly-dated edition.

**Two stale statements were found and fixed rather than reported.** `RENDER.md` Step 6 still described an `all.html` that `finance.py` has deleted on sight since 2026-08-19, in three places. `report-render.py`'s module docstring still said a country unit reads `report-country-sections.csv`, while its country profile has carried `"sections": None` since this change. Both are Corpus's own files.

**And the two things the instruction left for whoever could reach them are done.** `scripts/test_bulletin.py`'s one-word fix is made and **all ten test files now pass** (`test_render_gate.py` included — it wanted WeasyPrint, which is present here; `test_catalogue_export.py` skips for want of `node`). The `[FYI]` is written to the share as **`notes-for-osint.md` note 43**, committed and pushed.

`documentation/progress-report-scope.md` is untouched, as instructed. Its own recommendation — write the admission test, apply it to the view, reclassify only if the test needs types stated crisply — is Bill's to take.

## What changed, in one list

Code, all in `scripts/`:

- **`country.py`** — subtitle and colophon say *last updated*; report rows drop the period and the not-held count and read *N sources tracked*; *Twelve-month progress report* is now *Progress report*; *Sources* is now *Catalogue*, with new copy, without the most-frequent-publishers line, and with a per-country CSV cut published beside the page; the finance pivot's first column is *Topic*; the finance lede says *Figures are in US Dollars*; a *Public budgeting and expenditure* heading is added; the vault-access callout is removed.
- **`home.py`** — the countries index colophon says *last updated*.
- **`report-render.py`** — country reports take their sections from the taxonomy's ten Level-1 chapters in `lookups/taxonomy.csv` order; the section is derived from each row's subject rather than read off `ledger.csv`; `normalise_ledger()` writes the derived value back; narrative blocks are migrated onto the new keys; the monthly's title spans both months and its opener is one sentence; the country progress report's title is a month span and its *Compiled…* opener is gone; check I now tests `subject` rather than `section`.
- **`render.py`** — the byline reads *compiled by Claude Opus from the documents in the Corpus repository* and no longer counts not-held; a contents bar over the `<h2>`s is added to all three report kinds; the standfirst is matched by position rather than by the word *Compiled*; the kicker is *Progress report*.
- **`status_lib.py`** — `outline()` returns the 37 sub-sections in `taxonomy.csv` order.
- **`report-country-init.py`** — scaffolds `section` from the taxonomy.
- **`status-reorder.py`** — **new**, and already run over all 40 baselines (see below).
- **`taxonomy_lib.py`** — docstring only; the "ordering not yet" reservation is closed.

Data, already written by this session:

- **`outputs/reports/*/{ISO3}-status.md`** — 40 `STATUS-INIT` baselines physically reordered into taxonomy order by `scripts/status-reorder.py`. A permutation only: every sub-section's prose, heading and `<!-- slug -->` marker crossed over unchanged, verified by round-tripping all 40 through the parser. The 14 ledger-rendered status reports were not touched; the renderer reorders those.
- **`lookups/taxonomy.csv`** — `gov.policy`'s label gains its commas: *Strategies, plans and policies*. It is the label every other statement of that subject in either repo uses, and it now prints on 54 × 3 reports.

## The order to run it in

The section change is in the renderer, and the ledgers have to be normalised before anything reads them, which `load()` does on every render. So the ordinary sequence is right and nothing needs forcing:

1. `python scripts/build-catalogue.py` — the report layer refuses to resolve citations against a catalogue `raw/` has moved past, and this is stage 2's job, not the renderer's.
2. `python scripts/report-render.py --unit {UNIT} --render --doc all` over every unit, or the usual driver. First run per unit rewrites `ledger.csv` (row order, and `section` for rows whose stored value disagreed with their subject) and re-renders the markdown.
3. `python scripts/report-render.py --unit {UNIT} --check` — see *What the checks will say* below before reading the output as breakage.
4. `python scripts/render.py …` for the HTML and PDFs, then `python scripts/country.py`, `python scripts/home.py`.

`country.py` last, because it reads the report editions off the PDF filenames that step 4 mints.

## What the run will produce that looks alarming and is not

**Every report is a new edition.** The section order moved, the bylines moved and a contents bar arrived, so no document's digest survives. That is a genuine content change and `RENDER.md` §9 is satisfied by it — this is not the line-endings churn of 2026-08-24.

**206 unwritten narrative blocks appear across 54 progress reports, and check L fails on all of them.** Four Level-1 chapters — *Data*, *Digitalisation*, *Capacity*, *Geopolitics* — had no section of their own under the old six-section map, so there is no prose to carry into them. `LEGACY_SECTION_KEY` moves the prose that does exist (`infrastructure` → `ict-infrastructure`, `ai-tech` → `technology`; `dpi`, `governance`, `inclusion` and `finance` keep their keys), and the monthly's subject-keyed blocks migrate exactly, by the subject in the key — ZAF's monthly carried all 22 across with none left empty. What is left is drafting work for BUILD, which is what check L is for. **A document failing L is not finished; it is still published** (`report-render.py` → `--check`), so this does not gate the rebuild.

**Every country page gains a file.** `site/countries/{ISO3}/{ISO3}-catalogue.csv`, the catalogue cut. About 6.9 MB across all 54 including the finance CSVs already there; South Africa's is 326 KB for 779 records. It is not an edition — undated URL, republished wholesale, same rule as the catalogue it comes from.

**The finance CSVs may mint an edition on the `gov.policy` label.** Only for countries holding a commitment tagged to that subject, and only once the finance compile reruns. New content, correctly dated.

## Two things this session could not do, and one it broke and fixed

**No note was written to `C:\corpus-osint-xfer\`.** The share is not mounted in Cowork. `lookups/report-country-sections.csv` lives in OSINT's `lookups/` and Corpus no longer reads it — an `[FYI]` at most under the reversibility test, but it should be written so nobody maintains a file nothing consumes. `report-region-sections.csv` beside it **is** still read and must stay.

**`scripts/test_bulletin.py` fails, and it failed before this session.** `case_the_nav_bar_holds_only_the_categories_present` looks for `<nav class="bulletin-nav"`, and `bulletin.py` has emitted `<nav class="article-toc bulletin-nav"` since the class went up to `main.css` on 2026-08-24. One-word fix in the test. `test_render_gate.py` also fails in Cowork for want of WeasyPrint, which is an environment absence rather than a defect. The other seven test files pass.

**A `git stash` attempt left `.git/index.lock` behind**, because the Cowork sandbox cannot unlink files on the mount without permission. It was deleted before this session ended, along with a stray `.git/objects/cf/tmp_obj_*` and two probe files under `site/countries/ZAF/`. `git status` is clean of them. Worth knowing because the failure mode is a repository that refuses every git command afterwards, on Windows as much as here.

## Staging: read `git status` from Windows, not from here

Seen from the Cowork sandbox, `git status` reports **241 files modified**. Only **54** of them carry a real change, and those 54 are this session's work — seven scripts, three content and documentation files, `lookups/taxonomy.csv` and the 40 reordered baselines — plus one that is not this session's: `site/metadata/catalogue-metadata.csv`, which **Bill was editing by hand while this session ran** — a `Column,Definition` header row added, `date_precision` moved up beside `published`, and "The is of the metadata record" corrected to "The key of". It commits on its own terms; nothing here touched it. Two things worth knowing about it. Nothing in the build **parses** the file — `catalogue.py` only links it as the *Metadata* row of the Downloads box — so the new header row is safe. And `lens`, `body_completeness` and `artefact` are still blank, which are the three columns a reader is least likely to guess at.

The other **187** are `RENDER.md` line 242's known condition, counted there at 186: their committed blob is LF and their working copy is CRLF, because they were last written on Windows by a script using `Path.write_text()` — 108 country pages, 39 topic pages, the catalogue, finance and home pages, 17 scripts and the root runbooks. Git for Windows normalises them back on commit, so **`git status` on Bill's machine already shows them clean**; only a Linux git, which has no `core.autocrlf`, compares the raw bytes and calls them changed.

So the hazard runs the other way from how it first looks. A `git add -A` **on Windows** is safe and sweeps nothing in. A commit **from a Cowork session** would rewrite all 187, and — worse — a *rebuild* from one rewrites every published CSV with CRLF, which revises dated editions §9 says are never revised. `RENDER.md` carries the restore recipe for that case, and the reason a `.gitattributes` has not been added: it renormalises all 187 at once and wants a session doing only that.

To list what actually changed, from either side:

    git diff --ignore-cr-at-eol --numstat

## Left undone on purpose

Bill's sixth note on the progress report — *"too many random system or instruments… we need a structured list of what counts"* — is written up as a design question in `documentation/progress-report-scope.md` with the evidence and three options costed. Deciding it changes 6,083 rows across 57 ledgers, which is not a change to make in the same pass as a heading rename.
