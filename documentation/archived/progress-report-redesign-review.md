---
type: review
title: progress-report-redesign-review.md — CC's operational review of the indicator frame
last_reviewed: 2026-08-26
status: closed 2026-08-26 — all ten items accepted into progress-report-redesign.md. The three blocking items were resolved in Bill's favour of the baked table; items 4 and 9 are actioned (see the closing note).
---

# Operational review — the indicator-framed progress report

*(CC, 2026-08-26, against `documentation/progress-report-redesign.md` as agreed with Bill the same
day. The design holds: the frame is right, the vocabulary is right, and §4's decision to print
every row and count nothing is the best thing in the note. What follows is what the note assumes
about the machinery that is not true of the machinery.)*

**The wireframe checks out.** 121 indicators, 38 Level-2 subjects, and every one of them is a key
in `lookups/taxonomy.csv` — no orphans in either direction. Slugging the indicator text under its
subject yields 121 distinct ids with no collisions. There is nothing wrong with the frame itself.

## 1. Blocking — the datatable cannot hyperlink inside prose

§5 says *"The component already does everything needed; no upstream change is currently
required."* It is not so, and the thing it cannot do is the design's evidence rule.

`site/assets/js/datatable.js` escapes every cell it draws — `cellHtml()` at line 583 returns
`esc(display(ci, v))`, and the detail panel does the same at line 633. The one escape hatch,
`data-links`, treats the **whole cell as a single URL** and prints the URL as its own label
(`linkCell()`, line 142). So *"a clause or two, hyperlinked on the claim"* (§5) and *"every
hyperlink in a Developments cell resolves through a ledger row's `sources`"* (§2) both render as
literal `[text](url)` on the page. A second obstacle behind the first: `sources` on the ledger
holds **slugs**, not URLs — `cite()`/`row_url()` resolve them through `slug_urls()` at render
time — so the CSV would have to carry resolved URLs whatever else changes.

**Recommendation: don't use the datatable here — bake the table into the page.** §7's argument for
the component is borrowed from finance, and it is an argument about arithmetic that does not
transfer. The finance table is 1,257 rows by 20 columns, several megabytes of HTML against a 1.1 MB
CSV (`RENDER.md` → *The finance tables*). A progress report is **121 rows, fixed, per country**,
and `site/reports/ZAF/ZAF-progress.html` is already 86 KB baked-in today. A written table costs
nothing at that size and buys back everything §7 gives up: inline citations work as they do now,
the page works with JavaScript off, and §3 below stops being a problem. Put the full text in a
`<details>` expander per row — the same terse/full split, without the component.

If Bill would rather keep the datatable for the sorting and filtering, then the shared-asset path
is unavoidable and §5's paragraph is wrong rather than optional: add a `data-rich="developments"`
attribute upstream in `data-landscapers/assets/shared/datatable.js`, rendering a restricted inline
subset (`[text](url)` → anchor, and nothing else — no raw HTML through), then copy down and update
`site/assets/DATATABLE-FROM`. Sorting and filtering across 121 rows a reader reads in taxonomy
order is a thin prize for that.

## 2. Blocking — the three region units issue the progress report and nothing else

`scripts/report-register-check.py:78` states it plainly: *"a region, which issues the progress
report only"*. XAF, XSA and XWA have no status and no monthly. And the region document is not a
view of the taxonomy — `sections()` in `report-render.py` is explicit that a region reads
`report-region-sections.csv` because *"its sections run from the region's institutions outwards to
what funds them … not a view of the taxonomy at all"*. The redesign's shape — one table per
Level-1 chapter, in taxonomy order — is country-shaped, and §8's *"a model pass over 57 ledgers"*
sweeps the three regions in without deciding anything.

**Recommendation: regions keep the current renderer.** The redesign covers the 54 countries; the
note should say so in §1 rather than leave it to be discovered at the migration. The regions'
ledgers do use taxonomy subjects, so extending the frame later is possible — but their document
answers a different question and the indicator list was not drawn for it.

## 3. Blocking — a datatable page has no PDF, and progress is a PDF edition today

Not mentioned anywhere in the note. `scripts/country.py`'s `report_cards()` builds each country
page's report list by globbing `site/reports/{iso}/{iso}-progress-{edition}.pdf`; no PDF means
progress drops off the country page silently, without an error. `RENDER.md` → *The finance tables*
records the same cost from the other side: *"neither table appears with JavaScript off"*.

Recommendation 1 above dissolves this — a baked table keeps the PDF. If the datatable is chosen
anyway, then §7 needs to say outright that progress stops being a PDF edition, and what the
citable artefact becomes: a dated CSV is a **dataset**, not the document, and the editions rule in
`RENDER.md` §9 has been protecting a document.

## 4. 636,000 characters of drafted narrative have no stated fate

*"No per-L1 narrative blocks"* (§1) deletes their container. Across the 57 `*-progress.md` files
there are 619 narrative blocks, **469 of them written**, totalling 636,277 characters — call it a
hundred thousand words of drafted, register-checked, cited prose. §8's migration item covers
mapping ledger rows to indicators and says nothing about this.

**CC's call, recorded here rather than asked:** archive every unit's written blocks to
`outputs/reports/{unit}/progress-narrative-archive.md` **before** the first re-render, and feed
them to the indicator drafting pass as source material. They are the best input that pass will
ever get — the same evidence, already judged and already cited. A rebuild that drops them costs
more than the redesign saves. This is reversible and cheap, so it does not need Bill.

## 5. The prose stops being register-checked

`report-register-check.py` reads prose out of `<!-- narrative: key -->` markers in the `.md` files
(`MARKER`, `prose_spans()`, and the glob at line 224). Cliché and jargon registers, the
first-person test, citation density, and the word budgets read out of the skeletons — all of it
sees narrative blocks and only narrative blocks. Developments prose living in
`outputs/reports/{unit}/indicators.csv` is invisible to every one of those checks, and it would be
the longest body of prose the site publishes.

**Action (CC's):** extend `report-register-check.py` to read the indicator file's `summary` and
`developments` columns as prose spans, with the word budget expressed per indicator rather than
per chapter. Without it the redesign trades a checked document for an unchecked one.

## 6. Check J asserts the shape check, not only check I

§8 retires the shape check for this document and names check I and the vocabulary. It also has to
name **check J**: `check_asof()` fails any `-progress.md` that does not contain the string `"Shape
check"`, and separately parses `period: {start} to {end}` out of the front matter to compute the
window-lag note. Both halves break on a document that no longer carries either. `shape_line()`,
the `CLOSE` sentinel and `front(..., period=)` all need to follow. Small, but it is a check that
fails the build, not a cosmetic one.

## 7. §3 claims more testability than exists

*"so a script can propose it and check I can test it"* is true of exactly one boundary:
**No evidence ⟺ zero mapped rows**. That one is decidable and worth checking. *No change* is not —
§3 defines it as "mapped rows with nothing published in the window", but a row published **inside**
the window that merely restates a standing position is also No change, and a script cannot tell
that from an Advanced. Advanced, Stalled, Regressed and Mixed are drafter's judgements throughout.

This matters because §5's check-L equivalent rests on it. State the checkable set precisely:

- No evidence ⇒ zero mapped rows, and Developments empty, and no link. *(testable, both ways)*
- Progress ≠ No evidence ⇒ Developments non-empty. *(testable — this is §5's rule, keep it)*
- Mixed ⇒ a qualifying clause is present. *(testable, and §3 makes it mandatory)*
- Everything else ⇒ vocabulary closure only.

## 8. Two near-identical vocabularies, one drift

The ledger keeps `movement` for the monthly — `MOVEMENTS = (Advanced, Stalled, Regressed, Closed,
No change, Baseline not held)` at `report-render.py:153`. The indicator layer gets Advanced,
Stalled, Regressed, **Mixed**, No change, **No evidence**. Four shared words, two closed sets, and
the pair at the end differs in both membership and meaning. §8 already anticipates a sibling
constant, which is right. Add one sentence to §2 saying that `movement` stays on the ledger for the
monthly and is **not read by the progress layer** — otherwise the next reader will assume one
derives from the other, and a well-meant "tidy-up" will merge them.

## 9. Indicator ids — the rule needs one more line

`{subject-slug}--{short-slug}` is sound: slugging the full indicator text gives 121 distinct ids
with no collisions and no duplicate indicator names anywhere in the wireframe. But "short-slug" is
undefined, and full-text slugs run long — the worst is 81 characters
(`capacity.research--think-tanks-and-academic-departments-contributing-to-dt-policy`).

**CC's call:** mint from the full indicator text, mechanically, no hand-shortening. An id nobody
composes by hand cannot be composed inconsistently, and 81 characters is a `row_id`-shaped cost the
repo already pays.

And say in §8 that once `lookups/indicators.csv` is minted, `prep/progress-report-wireframe-v2.csv`
is **retired**, not kept as a drafting copy. Two copies of one list with nothing comparing them is
the drift pattern `scripts/lint-shared-assets.py` exists to catch, and there would be no lint here.
An indicator is added by editing the lookup.

## 10. Arithmetic to refresh

The note is a decision record, so its numbers should be true as at its date:

| Note says | Measured 2026-08-26 |
|---|---|
| §1 "~118 indicators" | 121 — as the frontmatter and §8 both say. Pick one |
| §2 "6,083 rows" | 6,194 across the 57 ledgers |
| §4 ZAF "zero rows in 12 of 38" | **17** of 38 — ZAF holds rows in 21 subjects |
| §8 "309 of 2,052 cells" | 361 of 2,166. 2,052 is 54 × 38 — it counted countries only |

The 54-unit count in §8 is not wrong so much as unstated, and it is the same question as §2 above:
if the regions are out of the frame, say it there and the arithmetic follows.

## What CC will do without asking

Items 4, 5, 7, 8 and 9 are reversible and are CC's to action at implementation. Items 1, 2 and 3
change what the reader gets and what the citable artefact is, so they go to Bill as three
recommendations: **bake the table rather than draw it**, **leave the regions on the current
renderer**, and — following from the first — **keep the PDF**.

## Closing note — 2026-08-26

Bill's edit takes all ten items into the design note. The three that needed his call went the way
this review recommended: the table is **baked, not datatable-drawn**, the **regions stay on the
current renderer**, and the **PDF survives** as a consequence of the first. §7 adds the one thing
the recommendation implied but did not say — the PDF prints every row's detail expanded, because a
PDF has no expander and the full text is the document.

**One correction to the edited note, made rather than raised.** §4 carried a forecast from the
first draft — *"a median country's tables will show No evidence on a majority of indicators"* — that
the numbers do not support as stated. Under the most generous mapping available (every ledger row
landing on a distinct indicator inside its own subject) the median country still shows **42 of 121**
No evidence, a third rather than a majority, and only 12 of the 54 countries have a floor above a
majority. The real figure will run well above the floor, because rows cluster on the same
indicator — but that is a reasonable expectation, not a consequence of the ZAF sentence it hung
off. §4 now states the floor and says which way the error runs.

Everything else in the edited note verifies. §8's arithmetic is exact: 309 of 2,052 country×subject
cells empty over the 54 countries, ≥635 of 6,534 country×indicator slots guaranteed No evidence.
ZAF is empty in 17 of 38 subjects and is 11th-largest of the 57 ledgers, so "one of the largest" is
fair.

**Two items actioned, both prerequisites under any reading of the note.**

- **Item 9 — `lookups/indicators.csv` minted.** 121 rows, `indicator_id` plus the wireframe's six
  columns. Ids are `{Topic L2}--{slug of the full indicator text}` under the repo's own slug rule
  (`re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")`, as `report-render.py` uses), applied
  mechanically with no hand-shortening. The indicator text is ASCII throughout, so nothing was lost
  in transliteration, and all 121 ids are distinct. `prep/progress-report-wireframe-v2.csv` is now
  superseded and should be deleted at the first implementation commit, per §8.
- **Item 4 — the narrative archived, before anything can re-render over it.** 446 written blocks,
  590,966 characters, written to `outputs/reports/{unit}/progress-narrative-archive.md` across the
  54 country units. The three regions were deliberately skipped: their 23 remaining blocks are live
  prose in a document that keeps the current renderer, and archiving those would have been the
  first mistake §1's carve-out exists to prevent.

**What is not done, and is the implementation proper:** the `render_progress()` rewrite and its
baked table, the check I / check J / `shape_line` / `period:` rework (items 6 and 7), the register
check's extension to the indicator prose columns (item 5), the mapping decision in §8, and the
model pass mapping 54 ledgers onto the frame.
