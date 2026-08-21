# The home page

Section intros and caveats for `site/index.html`, read by `scripts/home.py`.

The `section-intro` blocks are what a reader meets first; the `caveat` blocks sit under the boxes and explain why the numbers do not add up the way an unwary reader would expect them to. Both matter more than their length suggests — this page is the one most people see and the only one that has to explain the shape of the whole corpus.

Finance, Catalogue and Method left this page on 2026-08-19 and became top-level pages of their own; their intros went with them. What is left here is the three sections home still owns, plus the two-line Bulletin section at the top.

The Bulletin section is heading, this paragraph and nothing else *(Bill, 2026-08-21)*: the two boxes and the caveat under them went, along with the second bulletin they counted. `bulletin-intro` was a string constant in `home.py` until then, which is why the instruction to leave the editable text and remove the rest did not describe what was there — it is editable here now.

## hero

A living record of digital transformation and data governance across Africa. Compiled from primary sources. Updated daily.

## countries-intro

Each country page contains four reports: A status summary; A breakdown of progress recorded over the past twelve months; a summary of news reported in the last month; and a financial record of investments or commitments made by non-state institutions since 2015.

## countries-caveat

Sources held per country. A source tagged to several countries is counted under each, so these sum to more than the country total above: they measure coverage, not documents.

## regions-intro

Sources tagged to a region, a bloc or the continent as a whole, rather than to a single named country — the African Union, ECOWAS, SADC and the other regional bodies, plus the broader continental and cross-regional tags. A source is filed under a country whenever it names one; these are what is left. Eight groupings are tracked here, from the four sub-regions to the continental and global tags.

## topics-intro

A controlled vocabulary in a strict single-parent tree, so a category rolls up to every topic beneath it. A source carries as many topics as it evidences, and is counted under each of them. Data protection, digital identity, cross-border data flows, connectivity, artificial intelligence and the rest. Each topic resolves to the documents that evidence it, not to a summary of them.

## bulletin-intro

Everything published in the last two days, by topic, with the countries each item touches. Compiled at the end of each collection sweep; a quiet bulletin means nothing was published on those two days, not that nothing arrived.
