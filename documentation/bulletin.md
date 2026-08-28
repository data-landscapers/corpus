# The bulletin — design note

*(The live procedure is `BUILD.md` stage 7 and `RENDER.md` → *The bulletin*; this note is the reasoning behind them.)*

## What it is

One document, rewritten whenever its content moves, covering the sources **published** on the day of the build and the day before it: `outputs/bulletins/corpus-bulletin.md`, served at `/bulletin/`.

The taxonomy's Level-1 categories are its sections, each opening onto the Level-2 topics beneath it, both ordered by `lookups/taxonomy.csv` — order and labels alike, so the nav bar and the headings it jumps to are generated from one list and cannot disagree. Each item is summarised **once**, in the first section it appears in; every other topic it carries holds a cross-reference. Beside each headline sit the countries the item touches, as boxes linking to those countries' pages. `scripts/bulletin.py` selects the window, decides where each summary lands and writes the file; the summaries are written by BUILD, one to three sentences each.

## The shape

**One bulletin, not two.** There was a country bulletin and a topic bulletin covering the same items over the same window, differing only in grouping — one document rendered under two indexes, and an index is not a document. The country bulletin is retired; what the place grouping was for survives **on the item**, as the country boxes (the website's own `.wip-item-card__status--active` component — shared markup, per the share-style rule).

**The boxes carry a filter** (`site/assets/js/bulletin-filter.js`), the Lab index's category filter adapted for two differences: this list is nested two deep, so a section goes when its last item goes, a category when its last section goes, and the category bar re-punctuates rather than merely hides; and an item has zero to many countries (`data-places`, space-separated, written even when empty — a regional item is hidden by any country selection, which is right). The structure is read off the document at load; the item wrapper `<div class="bulletin-item" data-places="…" markdown="1">` is the only markup the filter needed.

- **A selection shows summaries only** — cross-reference stubs (`bulletin-item--xref`) are dropped, so the count is items, not mentions. The count is checked against the catalogue: for each country, the filter's figure equals the records in `raw-catalogue.csv` carrying that place.
- **The filter offers only the countries in this edition**, and is omitted below two.
- **Regions get no box** — an `X__` place has no country page, and a box that 404s is worse than no box; the catalogue's place filter covers them.
- A summary's *Also under X and Y* trailer is a `.bulletin-item__also` span the filter hides with the item **shown** — under a selection its targets are hidden and its claim false.

**The nav bar names only the categories this edition holds** — a fixed bar of ten is mostly dead jumps on a quiet day.

**A record carrying no topic appears under *Not topic-specific*; a slug the taxonomy does not carry gets a section under *Other*.** Nothing is dropped silently while being counted in the headline figure.

**The anchor rule: the summary goes where the item first appears** — the item's earliest topic **in document order** (`min` over `taxonomy_lib.sort_key`), so every cross-reference points backwards to text the reader has passed. (An earlier rule — the record's first-listed topic — agreed with this only while the sections were in facet order; reordering the sections broke it silently, and the only detector was reading the built page. Two rules that agree for a reason neither states are a standing class of fault here, and reading the built page is the check.)

## The stamps

**The compile timestamp is a claim about the material, not about the build — and looking counts as an update.** A sweep that admitted fifty sources none of them dated inside the window has still updated the bulletin: `--assemble` writes the stamp whenever it moves and reports `checked` rather than `written`. It refuses a write only when not even the clock has moved; the comparison is the whole file, rebuilt with the stamp already on it, so nothing but the clock is unreachable to its own generator.

**The stamp is OSINT's clock, not ours** — *when did your material last move*, not *when did we last run*. Two frontmatter stamps answer different questions: **`collected_to:`** is the byline's — the moment collection stopped, after which nothing more could have been caught; **`compiled:`** is the newest ingest — what the edition picker shows beside a dated PDF, where the question is how late the newest thing in the cut is.

**`collected_to:` is read from stated facts, never derived.** OSINT stamps `sweep_closed` on its ingest-log headings (`osint_lib.sweep_closed()`); the nightly cycle path instead writes its rotation row's `End` (`osint_lib.last_cycle_close()`); the byline takes **whichever is later**, since each artefact is silent about exactly what the other records. A derivation from heading-cluster gaps was tried and failed in both directions — the constant was a guess about the shape of OSINT's working day, which is not a shape Corpus gets to assume. A stated fact retires a derivation outright rather than joining it as a fallback.

**Where the mirror cannot be read, the build clock stands in and the run says so** — `— from build clock (mirror unreadable)`. Every reader in `osint_lib` returns `None` rather than guessing; a fallback nobody is told about quietly becomes the normal case. The mirror path is one constant, in `osint_lib`, `CORPUS_OSINT_MIRROR` overriding.

**The byline states the days it covers, not the days it looked at.** The run happens in the small hours, so *published on 20 and 21 August* over a catch entirely from the 20th reads as *the 21st was covered and found empty*. `covered_phrase()` builds the phrase from the publication dates actually in hand; the nominal window still governs selection, and still appears where the document states an absence — *nothing was published on the 20th or the 21st* is a claim about the window and needs both days named.

**The page refreshes on a held-off render; the PDF does not** — the byline says when we last looked, the colophon names the dated file, and a snapshot is entitled to the stamp it was cut with (`design.md` §9 has the rule). The colophon shows the plain edition, not `compiled:` to the minute — a time is not a filename, and the shown edition must name the file on offer.

## The furniture

The page dropped the report apparatus it had inherited without earning: no kicker (`KIND_LABEL["bulletin"]` is empty and the element comes out entirely), no standfirst, the subtitle carries the update time and window, the edition lives in the colophon only, and *Current edition* is off the colophon — the bulletin has one page, and the row printed its own address at whoever was already reading it. The download button is `↓ PDF`, level with the byline (`flex-wrap: nowrap`, byline `min-width: 0`, `align-items: flex-end`). The header takes `.article-header--bulletin` and `report.css` removes its bottom border — `main.css` is vendored and not ours to edit — so one rule closes the header, under the category bar. The bar is terracotta small caps with middot separators written as `aria-hidden` spans (an `::after` on the anchor would underline on hover and join the click target). The standing *About this document* paragraph is Bill's, in `content/document.md` → `bulletin-notes`.

## The decisions

1. **The window is publication, not acquisition** — the choice with the largest consequence. The corpus acquires in batches, so most bulletins are short and some are empty, and a large batch of new-to-us material goes unreported: the bulletin reports *what the world published*, not *what we happened to fetch*. **The empty bulletin is a first-class outcome**: it renders, says the window was empty, and says why — an absent bulletin is indistinguishable from a build that did not run.
2. **The summaries are model-authored**, bounded by keeping what it writes: `outputs/bulletins/summaries.json` is the store, `--write` the only way in, `--scan` asks only where there is none. Without it every item would be summarised twice, worded differently, and both published.
3. **Detail sits in one place** — the summarise-once discipline and the anchor rule above.
4. **A dated PDF is cut like everything else.** Being superseded tomorrow is the reason to want a copy today: every other document can be re-read at its own URL, and this one cannot.

## What it is not

**Not an archive** — one bounded exception: the last week of dated PDFs, listed in the colophon (`documentation/bulletin-archive.md`). The document is rewritten in place and holds only the current window; git holds every prior version; the summaries store is pruned 30 days after an item's publication date.

**Not a record layer.** Nothing here is a position that can move, nothing is checked against a ledger, nothing downstream derives from it.

**It does not judge relevance.** Every catalogue record published in the window and inside the geographic remit appears; the remit filter (`scope_lib.in_remit`) is a scope judgement, and the records it turns away are named on the run rather than dropped in silence.
