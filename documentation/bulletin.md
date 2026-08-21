# The bulletin — design note

*(Built 2026-08-17 from Bill's brief and four decisions taken against it; rewritten 2026-08-21 against `prep/bulletin.md`, a seventeen-point revision that retired half of it, and revised again the same day after he read the built page. The live procedure is `BUILD.md` stage 7 and `RENDER.md` → The bulletin; this note is the reasoning behind them and the record of what was chosen over what.)*

## What it is

One document, rewritten whenever its content moves, covering the sources **published** on the day of the build and the day before it. It is `outputs/bulletins/corpus-bulletin.md`, and it is served at `https://corpus.data-landscapers.io/bulletin/`.

The taxonomy's Level-1 categories are its sections, each opening onto the Level-2 topics beneath it, both ordered by `lookups/taxonomy.csv`. Each item is summarised **once**, in the first section it appears in; every other topic it carries holds a cross-reference to that summary. Beside each headline sit the countries the item touches, as boxes linking to those countries' pages.

`scripts/bulletin.py` selects the window, decides where each summary lands and writes the file; the summaries themselves are written by BUILD, one to three sentences each.

## The 2026-08-21 revision

**The country bulletin is retired, and this is the whole of what changed.** Everything else in Bill's list follows from it or from the page's furniture being wrong.

There were two documents. They covered the same items over the same window and differed only in how they grouped them — one by place, one by topic — so a reader who opened both read every summary twice, and a run that assembled both wrote every summary twice into git. The design note of 2026-08-17 treated that as the point (*"Both cover the same set of items"*) and it was the flaw: the two documents were one document rendered under two indexes, and an index is not a document.

**What the place grouping was actually for survives, on the item.** Each headline now carries a box per African country the record is tagged to, linking to that country's page. A reader who wants Kenya's items no longer reads a second document to find them; they scan for the box, or they go to Kenya's page, which holds a month rather than two days. The boxes are the website's own `.wip-item-card__status--active` component — the green category box on the Lab index — so this is shared markup rather than a Corpus invention, which is what `CLAUDE.md`'s *share style and functionality wherever possible* means in practice.

**Regions get no box, and that is not an oversight.** The `X`-prefixed places are regions, blocs and the global tag, and none of them has a country page to open. A box that 404s is worse than no box, and the region's items are reachable through the catalogue's place filter, which is where the home page's region boxes already send a reader.

**The order is `lookups/taxonomy.csv`'s, and so are the labels.** `taxonomy_lib`'s own note said the ordering waited on Bill reviewing the pages; for the bulletin he has reviewed them. The bulletin previously took both from `home.SUBTOPIC_NAMES`, which is a hand-ordered working copy that predates the CSV — two vocabularies, and the one the site calls canonical was not the one this document used. One consequence is worth stating: the nav bar at the head of the document and the headings it jumps to are generated from the same list, so they cannot disagree.

**The nav bar names only the categories this edition holds.** A two-day window reaches four or five of the ten categories on a quiet day. A fixed bar of ten would be mostly dead jumps, so the bar is built from the sections that exist.

**A record carrying no topic at all now appears, under *Not topic-specific*.** The topic bulletin dropped those records silently while counting them in its own headline figure, so the document could say fifty and show forty-seven. The same applies to a slug the taxonomy does not carry: it gets a section under *Other* rather than vanishing.

**The PDF came back** *(point 17)*, four days after being ruled out. The 2026-08-17 argument was that a bulletin is superseded the next morning and its content is kept by the reports, so a dated PDF archives the same news twice under a worse name. What it missed is that being superseded tomorrow is the reason to want a copy today: every other document on the site can be re-read at its own URL, and this one cannot.

**The compile timestamp is a claim about the material, not about the build** — and looking counts as an update *(Bill, 2026-08-21, fourth pass, overturning the first ruling below)*. The stamp was first suppressed whenever the body had not moved, on the reasoning that a page saying *last updated* should not say so when nothing had been. Bill's objection: *"if we ran sweep cycle now and the resulting bulletin remained unchanged — the information that it was last updated on this sweep is correct. We did update — by looking for new material and found none."* And the case he means is not a sweep that found nothing at all but **a sweep that found nothing dated for the bulletin** — fifty sources admitted, none of them published inside the two-day window. That is a night's work, and the page reported it as neglect.

So `--assemble` writes the stamp whenever it moves, and calls it `checked` rather than `written` when nothing else did. The comparison survives for what it is now for: telling *we looked and nothing was published* from *here is what was published*, and refusing a write when not even the clock has moved.

**And the stamp is OSINT's clock, not ours** *(Bill, 2026-08-21, second pass)*. His question was whether the last-updated time could be *the point at which OSINT's last sweep-cycle ran INGEST*, and it can: `logs/ingested_log.md` on the mirror is newest-first and every batch writes a `## YYYY-MM-DD HH:MM (ingest …)` heading. `scripts/osint_lib.py` reads it. The build clock answers *when did we last run*, which on a day when nothing came in is a different claim from *when did your material last move*, and only the second is about the reader.

The rotation table's `End` was the other candidate and is the cruder of the two — 00:14 against ingest's 00:05 on 2026-08-21, because the close comes after. `osint_lib.last_cycle_close()` exists and nothing calls it; it is there so that the comparison can be made again rather than re-derived.

**The byline states the days it covers, not the days it looked at** *(Bill, 2026-08-21, third pass)*. The window is the run's date and the day before it, and the run happens in the small hours — on 2026-08-21 the sweep closed at 00:14 and not one of the fifty items it caught carried a publication date of the 21st. The byline said *published on 20 and 21 August 2026* anyway, which reads as *the 21st was covered and found empty* when the day had barely started. `covered_phrase()` builds the phrase from the publication dates actually in hand. The nominal window still governs selection, and still appears where the document states an absence: *nothing was published on the 20th **or** the 21st* is a claim about the window and needs both days named.

**Which exposed the comparison rule as excluding too much.** `--assemble` compared the body below the frontmatter, on the reasoning that the stamp is in the frontmatter and must be excluded — but that excluded the *whole* frontmatter, and the subtitle is in it. So the byline fix ran, reported `unchanged`, and left the wrong subtitle on disk. The test is now: rebuild the document with the stamp already on the file and compare the whole thing. If that reproduces it, only the clock moved. Normalising the one field that moves on its own is the narrow version of what the old rule was reaching for, and the wide version had made a whole region of the document unreachable to its own generator.

**Which forced the question of what `render.py` should do with a moved stamp** *(2026-08-21, fourth pass)*. Its edition gate hashes the body below the frontmatter and holds off when that has not changed — leaving the document entirely alone, page as well as PDF, so that a page cannot print today while the artefact beside it says August. With the stamp now moving on every sweep, that rule would have thrown away the very thing Bill asked for: the source would carry the new time and the served page would not.

The two obvious answers were both wrong. Widening the digest to cover the byline mints a dated PDF every sweep, so two consecutive editions carry the same news under different names, which is what §9 exists to stop. Leaving the page alone keeps the stale byline. **The answer is that the page and the PDF are answering different questions**, so for `type: bulletin` a held-off render rewrites the page under the edition it is already holding and does not touch the PDF. The byline says when we last looked; the colophon names the dated file it is offering; a snapshot is entitled to the stamp it was cut with. The colophon's *Edition* row went back to the plain edition at the same time — it had been showing `compiled:` to the minute, which after this change would have named an edition that is not the file on offer, and `editions.py`'s same-day `-2` suffix already tells two cuts of one day apart.

**Where the mirror cannot be read the build clock stands in and the run says so.** A file read from a mirror reads as whatever the last sync left, which is why every reader in `osint_lib` returns `None` rather than guessing, and why `--assemble` prints `— from OSINT ingest` or `— from build clock (mirror unreadable)`. A fallback nobody is told about is a fallback that quietly becomes the normal case.

**The mirror path is now one constant.** `osint-cycle-ready.py` held its own `MIRROR` and this was about to be the second copy; both take it from `osint_lib` now, `CORPUS_OSINT_MIRROR` overriding, which is the arrangement `status_lib.EXCHANGE` already uses for the transfer folder. Reading OSINT is unrestricted (`CLAUDE.md`); writing to it is not, and nothing here writes.

**The shown edition and the filed edition are different strings.** The colophon says `2026-08-21 at 16:31`; the PDF is `corpus-bulletin-2026-08-21.pdf`, with `editions.py`'s same-day sequence if a second is cut. A time in a filename is a space and a colon, which is not a filename on Windows, and changing the edition grammar to carry one would reach every dated artefact the site publishes for the sake of one document's byline.

## The furniture, and why it was wrong

Four of Bill's seventeen points are about the page's chrome, and each was a piece of a report's apparatus that a bulletin had inherited without earning.

**The kicker said DAILY BULLETIN above a title saying Bulletin** — the same word twice, plus a claim about cadence the document does not make. It is written at the end of a collection sweep, not at a time of day. `KIND_LABEL["bulletin"]` is now empty and the element comes out entirely rather than rendering blank.

**The byline said *Edition of 2026-08-21 · sources published 20 and 21 August 2026*.** The subtitle now carries the whole of it and says more: when it was last updated, to the minute, and what window it covers. The edition is still on the page, in the colophon, which is where an edition belongs.

**The standfirst — *Compiled … · 50 sources published …, across 25 topics* — is gone.** It restated the byline with a count of sections attached, and the count of sections is visible in the nav bar directly beneath it.

**The download button says `↓ PDF` and sits level with the byline** *(second pass)*. *Download* is what the arrow already says, and a button on its own line below the byline ended the header on a call to action rather than on what the document is. The row is `flex-wrap: nowrap`: the first attempt let it wrap, which put the button straight back under the byline at every width the byline ran long — and the bulletin's byline always does, since it states both a timestamp and a window. The byline shrinks and wraps inside its own box instead, which is what `min-width: 0` on a flex item is for. It is `align-items: flex-end` *(third pass)*, so the button's foot sits on the byline's last line rather than its head on the first.

**The header carries no closing rule on this page** *(third pass)*. `main.css` gives every `.article-header` a bottom border and the category bar had a top border of its own, so the page opened on two horizontal lines a few millimetres apart with nothing between them. `main.css` is vendored from the website repo and is not ours to edit, so the header takes an `.article-header--bulletin` modifier and `report.css` turns the border off for it — one rule now, under the bar, closing it before the first category.

**The category bar is terracotta small caps with middot separators** *(second pass)*. `--accent`, the site's own #c84b2f, because these are the page's own contents rather than site chrome — `.corpus-nav` above it is grey until hovered, which is right for a nav that is the same on every page and wrong for one that describes this document. The middot is the site's separator already, in every report byline and in the footer, so the bar is punctuated the way the rest of the site is rather than in a third style. It is written into the markup as a `<span aria-hidden>` rather than drawn with a CSS `::after`, because an `::after` on the anchor sits *inside* the link: it would underline on hover and be part of the click target.

**The closing italic note is gone**, and with it `content/bulletin.md`, whose only two blocks were the two bulletins' closing notes. It explained the summarise-once discipline and then pointed at the country bulletin, which no longer exists; the discipline is legible from the cross-references themselves.

**`Current edition` came off the colophon.** On a report it points a reader holding a dated PDF back at the live page, which is the entire reason for the row. The bulletin has one page; the row printed its own address back at whoever was already reading it.

**The two standing paragraphs under *About this document* are one paragraph, Bill's**, in `content/document.md` → `bulletin-notes`. They had explained that the corpus acquires in batches and that the page is not an archive; his replacement says what a reader actually needs, which is where to look for anything older — the country pages for the last month, the catalogue for everything.

## What was found on the way

**The bulletin pages had been served unstyled since 2026-08-17.** `render.py` wrote `../../assets/css/main.css` as a constant, which is right for `site/reports/{unit}/` and `site/topics/{slug}/` — the only two trees that existed when the line was written — and one level too high for `site/bulletins/`. Both stylesheets and the logo resolved above `site/` and 404'd. Nothing caught it: a page with no CSS is still a page, and `--no-pdf` meant no PDF was ever cut, which is where the breakage would have been unmissable. The path is now counted from the directory the page lands in.

## The four original decisions, and what is left of them

**1. The window is publication, not acquisition.** *(Bill, 2026-08-17, chosen over *everything ingested since the last build* and over a seven-day window.)* Unchanged, and it is still the choice with the largest consequence. The corpus does not acquire continuously: the 2026-08-16 run ingested 184 records carrying publication dates spread across the ten days before it, of which eleven fell inside a two-day window. So most bulletins are short, some are empty, and a large batch of genuinely new-to-us material goes unreported by them. What the bulletin reports is *what the world published*, not *what we happened to fetch*.

**Which makes the empty bulletin a first-class outcome.** It renders, it says the window was empty, and it says why — that nothing was *published* on those two days, not that nothing arrived. A bulletin simply absent on a quiet day would be indistinguishable from a build that did not run.

**2. The summaries are model-authored.** *(Bill, 2026-08-17, over a scripted listing of titles and links.)* Unchanged. Bounded by keeping what it writes: the window is two days wide and the build runs daily, so nearly every item is selected on two consecutive mornings. `outputs/bulletins/summaries.json` is the store, `--write` is the only way in, and `--scan` asks only where there is none. Without it every item would be summarised twice and worded differently on the two days — worse than the wasted tokens, because both wordings would be published.

**3. Detail sits in one place and everything else points at it.** *(Bill, 2026-08-17.)* Half retired with the country bulletin, and the surviving half re-cut on 2026-08-21.

The anchor was *the first topic the record lists* — first in the record's own facet list, which `build-catalogue.py` carries across from the source frontmatter unchanged. That was chosen over alphabetical order, because alphabetical order is a property of the code rather than of the item, and it worked while the sections were in facet order too: the item's first topic was the first section it appeared in, so every cross-reference pointed backwards.

**Ordering the sections by the taxonomy broke that silently, and the built page showed it immediately.** Governance is the taxonomy's first category and so the first thing a reader meets, and on the first build every item under it opened *Summarised under …* and sent the reader further down the page for the text. The document would not start. So the anchor is now the item's earliest topic **in document order** — `min` over `taxonomy_lib.sort_key` — which restores the property the old rule had by accident and states it as the rule it always was: **the summary goes where the item first appears.**

This is worth keeping in view because it is a class of fault rather than an incident. Two rules agreed for a reason neither of them stated, one changed, and nothing failed — the page rendered, every anchor resolved, the counts were right. The only detector was reading it.

**4. HTML only, no PDF.** Reversed 2026-08-21, above.

## What it is not

**It is not an archive and does not accumulate.** The document is rewritten in place and holds only the current window; git history holds every prior version, and now so does the dated PDF. The summaries store is pruned 30 days after an item's publication date — 28 days after the last window that could have cited it.

**It is not a record layer.** Nothing here is a position that can move, nothing is checked against a ledger, and nothing downstream derives from it.

**It does not judge relevance.** Every catalogue record published in the window and inside the geographic remit appears. The remit filter (`scope_lib.in_remit`, added 2026-08-20) is not a relevance judgement but a scope one, and the records it turns away are named on the run rather than dropped in silence.
