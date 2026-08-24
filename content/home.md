# The home page

Section intros and caveats for `site/index.html`, read by `scripts/home.py`.

The `section-intro` blocks are what a reader meets first; the `caveat` blocks sit under the boxes and explain why the numbers do not add up the way an unwary reader would expect them to. Both matter more than their length suggests — this page is the one most people see and the only one that has to explain the shape of the whole corpus.

Finance, Catalogue and Method left this page on 2026-08-19 and became top-level pages of their own; their intros went with them. What is left here is the three sections home still owns, plus the two-line Bulletin section at the top.

The Bulletin section is heading, this paragraph and nothing else *(Bill, 2026-08-21)*: the two boxes and the caveat under them went, along with the second bulletin they counted. `bulletin-intro` was a string constant in `home.py` until then, which is why the instruction to leave the editable text and remove the rest did not describe what was there — it is editable here now.

## hero

Corpus is a repository of public documents covering digital transformation, digital public infrastructures and data governance across Africa. It is updated daily. 

## countries-intro

The repository covers all 54 countries For each country four reports have been built and are modified whenever newly arrived content merits an update. The ***Status Report*** attempts to summarise the current state of all components of the digital transformation landscape, The ***Monthly Update*** reference all new content published since the beginning of the last calendar month. The ***Progress Report*** attempts to track whether the tracked components have advanced, stalled or regressed over the past 12 months. ***Non-state Finance*** list all known financial commitments made since 2015. A fifth report on state budgeting and expenditure is outstanding.

## countries-caveat

Sources held per country. A source tagged to several countries is counted under each, so these sum to more than the country total above: they measure coverage, not documents.

## regions-intro

Sources tagged to a region, a bloc or the continent as a whole, rather than to a single named country — the African Union, ECOWAS, SADC and the other regional bodies, plus the broader continental and cross-regional tags. A source is filed under a country whenever it names one; these are what is left. Eight groupings are tracked here, from the four sub-regions to the continental and global tags.

## topics-intro

A controlled vocabulary in a strict single-parent tree, so a category rolls up to every topic beneath it. A source carries as many topics as it evidences, and is counted under each of them. Data protection, digital identity, cross-border data flows, connectivity, artificial intelligence and the rest. Each topic resolves to the documents that evidence it, not to a summary of them.

## bulletin-intro

The bulletin lists all new content published today and yesterday. The first build takes place overnight and is refreshed in the middle of the day to catch this morning's publications. The bulletin can be filtered by country and topic.
