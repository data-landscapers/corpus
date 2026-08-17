# The daily bulletin — design note (2026-08-17)

*(Built 2026-08-17, from Bill's brief and four decisions taken against it. The live procedure is `BUILD.md` stage 7 and `RENDER.md` → Bulletins; this note is the reasoning behind them and the record of what was chosen over what.)*

## What it is

Two documents, rewritten at every build, covering the sources **published** on the day of the build and the day before it:

- `outputs/bulletins/country-bulletin.md` — regions first, then countries, then the items tagged to no place at all;
- `outputs/bulletins/topic-bulletin.md` — the taxonomy's ten Level-1 categories, each opening onto the Level-2 topics beneath it, and **no subdivision by country**.

Both cover the same set of items, and each item is summarised **once**: the other sections it belongs to carry a cross-reference to the section that holds the detail. `scripts/bulletin.py` selects the window, decides where each summary lands and writes both files; the summaries themselves are written by BUILD, one to three sentences each.

## The four decisions

**1. The window is publication, not acquisition.** *(Bill, 2026-08-17, chosen over the alternative and over a seven-day window.)* This was the one choice with a large consequence, and it was put to him with the consequence stated: the corpus does not acquire continuously. The 2026-08-16 run ingested 184 records carrying publication dates spread across the ten days before it, of which eleven fell inside a two-day window and one inside the window the following morning. So most bulletins are short and some are empty, while a large batch of genuinely new-to-us material goes unreported by them. The alternative offered — *everything ingested since the last build* — would have caught the batch and never produced an empty document; it was declined, and what the bulletin therefore reports is *what the world published*, not *what we happened to fetch*. Those are different questions and only one of them is what a reader means by a daily bulletin.

**Which makes the empty bulletin a first-class outcome rather than an edge case.** It renders, it says the window was empty, and it says why — that nothing was *published* on those two days, not that nothing arrived. A bulletin that were simply absent on a quiet day would be indistinguishable from a build that did not run, which is the same failure `BUILD.md` stage 0 exists to make visible in the large.

**2. The summaries are model-authored.** *(Bill, 2026-08-17, over a scripted listing of titles and links.)* A listing is free and would have been a list, not a summary. So stage 7 is a model stage — the third in the build, after the report update and the status baseline — and its cost is bounded by the window rather than by the corpus: one day's publication per run.

**It is bounded further by keeping what it writes.** The window is two days wide and the build runs daily, so nearly every item is selected on two consecutive mornings. `outputs/bulletins/summaries.json` is the store, `--write` is the only way into it, and `--scan` asks for a summary only where there is none. Without that, every item would be summarised twice and worded differently on the two days — which is worse than the wasted tokens, because the two wordings would both be published.

**3. Detail sits in one place and everything else points at it.** *(Bill, 2026-08-17.)* An item tagged five countries is written out under one of them and cross-referenced from the other four. The anchor is **a region where the item carries one, otherwise the first place its record lists** — and in the topic bulletin, the first topic it lists. *First* means first in the record's own facet list, which `build-catalogue.py` carries across from the source frontmatter unchanged.

The alternative was alphabetical, and it was rejected because alphabetical order is a property of the code rather than of the item: a nine-country regional story would be written up under Benin. Anchoring on a region where there is one also puts the widest account of an item at the top of the document, where Bill asked for the regions to be.

**Regions and not "places".** *(Bill's brief, explicitly: "I know regions aren't countries but I don't want it called places".)* So the country bulletin's first group is `## Regions` — the eight `X`-prefixed codes, the same set the home page already calls regions — and the group heading is never *Places*. Items carrying no place code at all get a final group, `## Not place-specific`, rather than being dropped: on the first window built, three of eleven items had no place, and they included a US–China AI story and an Indian KYC proposal that are in the corpus deliberately.

**4. HTML only, no PDF.** *(Bill, 2026-08-17, sent mid-build.)* Every other rendered document cuts a dated PDF because it is a retained edition someone may cite away from the site. A bulletin is superseded the next morning, and what it reports is kept by the country, region and topic reports, so a dated PDF of one archives the same news a second time under a worse name. `render.py --no-pdf` is the flag; a page rendered without a PDF also drops the download button and the hash-and-verify colophon line, because a document that advertises a file nobody cut is worse than one that says nothing.

## What had to change around it

**`render.py` runs Markdown's `toc` extension.** Not for a table of contents — for the ids. A cross-reference is an in-document link, and without ids on the headings every one of them lands nowhere. `bulletin.py` imports the same `slugify` to build the link targets, so there is one implementation of the slug rather than two that can drift. For every other document the change is additive: an `id` attribute on each heading and nothing else.

**`render.py` takes the site directory from one function.** `site_rel()` returns `reports/KEN`, `topics/dpi-pay` or `bulletins`, and both the permalink written into the page and the directory the file is written to come from it. The bulletins are the only tree with no unit beneath them, and a second place deciding that is a second place for the two to disagree — silently, since a page whose canonical URL points somewhere it is not still renders perfectly.

**A document may state its own byline.** `subtitle:` in frontmatter overrides the ledger-count line, because no count of systems and instruments describes a bulletin; what a reader needs from the header is the window.

## What it is not

**It is not an archive and does not accumulate.** Both files are rewritten in place at every build and hold only the current window; git history holds every prior version, which is the right place for it. The summaries store is pruned 30 days after an item's publication date — 28 days after the last window that could have cited it.

**It is not a record layer.** Nothing here is a position that can move, nothing is checked against a ledger, and nothing downstream derives from it. A development that matters is in the country and topic reports; the bulletin is a view of two days of publication and is allowed to be exactly that.

**It does not judge relevance.** Every catalogue record published in the window appears. The corpus's selectivity is exercised at acquisition, not here.
