# Downloading a filtered selection of the catalogue

*(Design record, 2026-08-24. Bill asked whether the catalogue could offer "a CSV download of a filtered selection as well as the whole catalogue". It can, and it now does. This is what the choice was between, why the expensive-looking option was the cheap one, and what the resulting file is and is not.)*

## The question was never whether, it was which columns

The filtering already existed and so did the selection. `drawResults()` computes `out` on every redraw, and `writeHash()` has been putting the filter state in the URL since the prototype. Adding a button that turns `out` into a Blob is about twenty-five lines and no new data.

What made it a decision rather than a chore is that **the page does not hold a whole catalogue record.** `pack_rows()` packs eleven fields because eleven fields are what a row on the page renders: title, publisher, date, places, topics, lens, url, slug, artefact-held, body-completeness, entities. The published download carries sixteen. The five it does not pack — `author`, `date_precision`, `finance`, `words`, `ingested` — were never dropped on purpose; they were simply never needed to draw anything, and `pack_rows` packs what draws.

So the naive version of this feature ships a file called CSV whose columns are *whatever the browse surface happened to need*, sitting one paragraph away from another file called CSV with a different set. That is not a defect anyone notices on the day. It is the kind of thing that surfaces six months later in somebody's script, and by then both files are in circulation.

## Three ways to close the gap, and what each costs

| | payload cost to every visitor | fetch on export | schema |
|---|---|---|---|
| serialise the eleven packed fields | none | none | **differs from the published file** |
| pack the missing five | **~600 KB on 4.0 MB, on every visit** | none | parity |
| fetch the full catalogue on first export click | ~700 bytes (the column spec) | 8.4 MB / 1.7 MB gzipped, **once, only if you export** | parity |

The second option is the one that looks obvious and is wrong. `design.md` §6 has the catalogue payload on the open list precisely because it is already heavy — "a single fetch stops being defensible around 15–20k rows" — and paying six hundred kilobytes on every visit to buy a feature most visitors never touch is spending the scarce resource on the rare case.

The third is the same lazy-fetch shape the names index (`catalogue-search.md` stage 3) already uses on the same page, arrived at from the other direction: **the export payload, like the search payload, is the kind that can be fetched on demand, because nobody who came to browse by country and year needs it.** A reader who never clicks export fetches nothing at all. A reader who does pays one round trip and gets a file with the right columns in it.

**It also removes the join entirely from the build.** The selection is cut from `raw-catalogue.json` by slug, so what comes out is the published record itself rather than a reconstruction of one, and there is no second code path that can drift from `build-catalogue.py`.

## One source of truth for the column spec, checked by byte comparison

`catalogue.py` → `csv_cols()` reads `CSV_COLS` out of `build-catalogue.py` **by syntax tree rather than by import** — importing it would open the vault at module scope, which a page build has no business doing, and the filename is hyphenated besides. A column added upstream reaches the export on the next build with nothing to change here.

The JS then reproduces `csv.DictWriter`'s output: `QUOTE_MINIMAL` quoting, `; ` between list values, Python's `True`/`False` for the `finance` boolean, **CRLF line endings and no BOM**. That last pair is the one worth stating, because `RENDER.md` → *The finance tables* is the standing record of what line endings do under a Cowork build when two sides disagree about them.

**The claim is checked rather than asserted, and the check is in the repo.** `scripts/test_catalogue_export.py` lifts `csvCell` and `toCSV` out of the *built* `index.html` — testing a copy of the logic would only prove the copy right — runs them over all 10,731 items of `raw-catalogue.json`, and compares the result to `raw-catalogue.csv` byte for byte. It matches at 4,560,196 bytes. A filtered export is therefore the published file with rows removed, and nothing else.

It is a repo test rather than a one-off because **this is exactly the kind of agreement that breaks quietly.** A changed quoting rule, a lost CRLF, a boolean that starts rendering `false` instead of `False`: the page still works, the file still downloads, and nothing else in the build has any reason to look. Run it after anything touches the serialiser or `build-catalogue.py`'s `CSV_COLS`. It needs node on PATH and a built catalogue, and skips rather than fails without either.

Beyond that, a jsdom pass over the built page covered the behaviour once, on the day: that the control stays hidden when nothing is filtered and when nothing matches, that a text search pulling rows in through the names index exports all of them, that the file follows the sort the reader was looking at, and that a failed fetch leaves a message and the buttons rather than a broken page. That one is **not** in the repo — it needs an npm install to run, which is a dependency this tree does not otherwise have and should not acquire for one test. The behaviour it covers also fails visibly, in a way the byte-level agreement above does not, which is the reason to keep only the second one standing.

## What the file is, and what it is not

**It is not an edition, and neither is the whole-catalogue file.** `design.md` §9 settled that deliberately — the catalogue is an index over other people's records rather than a compiled finding of ours, so it lives at an undated URL and is republished wholesale on every build. It would have been easy, and wrong, to write a note on the export implying the reader should cite the full CSV instead as though *that* were the stable thing.

So the provenance the export carries points at the reproducible object rather than the file:

- **the filename** carries the catalogue's build date — `catalogue-selection-2026-08-24.csv` — which is the one thing a CSV can hold without a comment row, and comment rows were rejected because they break a naive parser;
- **the JSON** carries a `selection` block: the view's URL, the filters in structured form, the record count against the catalogue total, the moment it was cut, and a note saying to cite the URL rather than the file;
- **the page** says the same in the note under the results, whenever a selection is downloadable.

The URL is the citable object because it re-cuts against whatever the catalogue holds when it is opened. That is a better guarantee than a file, and it is the guarantee the filter-state-in-the-URL design was already making.

## Where it sits on the page

**Every download is now one box beside the lede** *(Bill, 2026-08-24, `prep/catalogue.md` §10)*, in the site's ordinary `.btn` down-arrow style — three rows, *Whole catalogue* / *This selection* / *Metadata*, CSV and JSON where both exist. That replaces the two arrangements this section previously described: a prose paragraph of links under the lede for the whole file, and a separate control beside the result count for the selection. A reader looking for a download was being asked to know which of the two they wanted before they knew where to look for it.

The one thing the move costs is the *appear when there is something to cut* behaviour, and it is traded rather than lost. The selection buttons are always drawn and are **disabled until a filter or a search narrows the view** — unfiltered, the selection *is* the catalogue and the row above already offers the published, citable files, so a live button there would only duplicate them. A disabled button in a labelled row says the feature exists and what turns it on; a control that renders nothing says neither, which was fine beside a result count and is not fine in a box headed *Downloads*. The hover title carries the reason either way.

*Metadata* is the third row, `site/metadata/catalogue-metadata.csv` — the field list for both the whole-catalogue and the selection downloads, and the same file the reader would otherwise have to guess at.

## What this does not do

It does not touch the metadata-only commitment. The export is a row subset of a file that already carries no bodies, and `leak-check.py` is unchanged and still clean.

It does not shard the browse payload, which is still `design.md` §6's open question and still wants deciding before it breaks rather than when. What it does is add a second consumer of `raw-catalogue.json` at its published URL, which is one more reason the eventual split should keep that URL working.
