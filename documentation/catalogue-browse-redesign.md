# The catalogue browse surface, second cut

*(Design record, 2026-08-24. `prep/catalogue.md` is Bill's ten-point brief; this is what each point turned into and the two places where following it exposed something else that was wrong. The download box is §10 of the brief and has its own record in `catalogue-filtered-download.md`; the entity facet's removal is §7 and is noted in `catalogue-search.md` beside the stage it was built in.)*

## What changed

The sidebar is three facets — **Country, Topic, Year published** — where it was five, and none of the three is ordered by record count any more. Lens and Named actor are gone from it. The lede is body text at body size taking the width the download box leaves it, instead of a 14px grey caption capped at 74 characters. Everything downloadable is one box beside the lede.

## Sorting by count was the actual complaint

Four of the brief's ten points are about ordering, and they are one problem seen from four angles. Every facet sorted by count, descending, and recomputed that sort on every redraw — so **the list reordered itself under the reader every time a box was ticked**. Kenya was ninth, then fourth, then somewhere below the fold, and a reader who wanted Kenya had no way to know where to look for it except to read the whole list each time.

Count-sorting is right for a vocabulary with no order of its own. It is wrong for these three, because all three have one:

- **Places** have a place order: region, then name. The vocabulary carries the region on every row already; nothing had to be built, only used.
- **Topics** have `lookups/taxonomy.csv`'s `Sort order` column, which is the sequence the taxonomy was written in and the sequence every other surface on the site shows it in. `taxonomy_lib.keys()` returns it. The Level 1 grouping falls out of the same list for free — Governance, Finance, ICT Infrastructure, DPI, and so on — so there is no second list to keep in step.
- **Years** are years.

`facetBlock` now takes an optional `order` argument: an explicit key sequence when the vocabulary has one, count-descending when it does not. The entity facet was the only caller that wanted the old behaviour, and it has gone.

## Two things the brief flushed out

**The region-name map had drifted, and it was a copy.** The page carried a hardcoded `REGION_NAME` mapping eight codes to labels. It wrote `XAF` as *Africa-wide* and `XSS` as *Sub-Saharan* where the vocabulary calls them *Africa* and *Sub-Saharan Africa*, and it carried `XHA` — *Horn of Africa* — which is not in the vocabulary at all and had presumably been true once. Every one of those codes is a **row in `countries.csv` with its own name**, so the map was a copy of data the page already had loaded. It is deleted; region headers read their labels from the place vocabulary like everything else does.

Grouping the regions was the second half of it. The old code grouped each place by its parent — which put *Central Africa* under *Africa*, and *Africa* under *Global* — so the region codes were scattered down the list under headers of their own. They are places a source can be tagged to in their own right, and the brief asks for them together and first: **REGIONS**, then the country groups alphabetically, countries alphabetical inside each.

**The pre-2020 bucket needed a key, and the key needed escaping.** Grouping every year before 2020 as `< 2020` means the facet filters on a *bucket* rather than on the row's year, which is a one-line change (`r._y` holds the bucket). What is not one line is that the bucket's key is `<2020`, and that key travels into a checkbox `value` attribute and into the URL fragment. Both are now escaped — `att()` on the attribute, `encodeURIComponent` on the fragment — and neither was, because until now every facet key was an ISO code or a dotted slug and the question had never come up. A facet vocabulary that is no longer entirely machine-generated is a facet vocabulary that has to be escaped.

## A stale filter in a shared URL is now ignored

Filter state lives in the URL hash, which is the whole point of it — a filtered view is citable. The consequence of removing a facet is that URLs naming it are still in circulation. `readHash` used to set any key it found that existed on the state object; it now sets only keys in the current facet list, so `#lens=sovereignty` from an old link opens the unfiltered catalogue rather than a filtered one with no control anywhere on the page to unfilter it.

## Checked

`scripts/test_catalogue_export.py` still passes — the CSV serialiser reproduces `raw-catalogue.csv` byte for byte over all 10,747 rows. Beyond that, a jsdom pass over the built page confirmed on the day: the three facets and their orders, the eight year options with `< 2020` last at 441 records, the pre-2020 filter cutting to 441 rows all dated before 2020, the download buttons disabled unfiltered and live filtered, `#years=%3C2020&places=KEN` reloading to 29 records, a stale `#lens=` URL reloading to the full catalogue, and no lens tags left on any row. That pass is not in the repo — it needs an npm install this tree does not otherwise want, and `catalogue-filtered-download.md` records the same reasoning for the same reason.
