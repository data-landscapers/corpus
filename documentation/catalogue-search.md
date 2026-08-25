# Catalogue search — widening it past title and publisher

*(Design note, 2026-08-24. The catalogue's search box matches `title + publisher` and nothing else. Bill asked whether it can draw on people and organisation names too, "or a broader index", and said a big backswing was acceptable. This is what the three available answers cost and which of them to build.)*

## What the search actually is today

One line in `scripts/catalogue.py`:

```js
ROWS.forEach(function(r){ r._s = (r[0] + ' ' + r[1]).toLowerCase(); });
```

A lowercased concatenation of title and publisher, scanned with `indexOf` on every keystroke over 10,711 rows. It works, it is fast enough, and it is the whole of it. Everything below is about what else could go into `_s` — or about replacing `_s` with something that is not a substring scan.

The constraint that shapes every option: **`build-catalogue.py` already carries `entities` and `pack_rows` throws them away.** The ten fields packed into `catalogue-data.js` are title, publisher, date, places, topics, lens, url, slug, artefact-held, body-completeness. Entities survive into `raw-catalogue.json` and `raw-catalogue.csv` — the downloads — and are dropped from the browse surface. So the first stage below is not new data. It is data the pipeline collects, publishes in the download, and declines to show.

## Stage 1 — put the entity tags into the browse surface

**This is the cheap and correct answer to the question as asked, and it should happen whatever is decided about the rest.**

`entities:` *is* the people-and-organisations facet. 24,891 tags across 10,510 of the 10,711 records, mean 2.32 per record, and by `CLAUDE.md` → *Entities* they are specifically the **actors** in each development rather than every name dropped in the text — which is the right density for a filter, not a defect.

**Dictionary-encode them rather than repeating the strings.** A vocabulary array of the 6,774 distinct slugs plus integer references costs **293 KB** against 524 KB for raw slug lists, on a payload that is currently 3,992 KB. That is a 7% increase, and the encoding is what makes stage 2 and the entity facet affordable rather than a second copy of the same strings.

**Expand hyphens into the search blob**: `r._s = (title + ' ' + publisher + ' ' + entitySlugs.join(' ').replace(/-/g, ' ')).toLowerCase()`. `institute-for-security-studies` then matches "security studies", `cassava-technologies` matches "cassava". Acronym slugs — `nira-uganda`, `odpc-kenya`, `ansie-djibouti` — match the acronym, which is usually what a specialist types anyway.

**While the data is there, add the entity facet and the entity chips.** The browse page renders place, topic and lens tags on every row and offers a facet for each; entities are the only classified facet with no presence on the page at all. The current 200-slug cap in `build-catalogue.py`'s `facets()` was set for a menu that has to be rendered as a list — a type-ahead facet, which the page already implements for the 62 places and 38 topics, does not need the cap and should read the full vocabulary.

**What stage 1 does not fix.** 4,068 of the 6,774 slugs are single-reference, so most of the vocabulary filters exactly one record; a slug is not a display name, so `ministerio-das-financas-ago` reads as itself on the page; and a reader searching "National Identification and Registration Authority" still gets nothing, because the slug is `nira-uganda`. Those are stage 2.

## Does stage 3 make stage 2 unnecessary? *(Bill asked, 2026-08-24)*

**No, but it changes what stage 2 is and when it should be done.** Stage 2 does two jobs and stage 3 retires exactly one of them.

**The search job: superseded.** Stage 2's alias search existed so that "National Identification and Registration Authority" would reach `nira-uganda`. Stage 3 finds that document by that string from the body directly, and does better — it also finds documents that *mention* the authority without carrying its tag.

**The label job: untouched.** Stage 3 maps text to documents; stage 2 maps a slug to its name. Those point in opposite directions, and no amount of names index makes the facet stop reading `bf-ministry-digital-transition`.

**But stage 3 makes stage 2 cheap, because it is the same extraction pass.** Measured: for 300 slugs carrying three or more sources, looking only at the bodies of the sources that tag them, a candidate name fell out for **99%**.

```
noa                      -> National Orientation Agency
central-bank-of-eswatini -> Central Bank of Eswatini
angola-cables            -> Angola Cables
civix                    -> CIVIX
```

`noa` is the argument in one line: stage 3 can say which documents mention that phrase, and only stage 2 can make the chip say it. About a third are wrong in a patterned way — country-suffixed slugs match on the country token alone, so `pura-gambia` gives "The Gambia" and `sec-nigeria` gives "Nigeria" — which scoring on the non-country tokens mostly fixes, leaving the hand pass stage 2 always involved.

**So the sequencing inverts rather than the stage disappearing**: stage 3 first, after which stage 2 shrinks from a derivation script plus a hand pass to a join on stage 3's output plus a hand pass.

**The entity facet stays either way.** A tag means *actor in the development* — three to six a source, institutions not officeholders, editorial judgement. A name in the index means *this string occurs in the text*. "The 623 sources where the World Bank is an actor" and "everything mentioning the World Bank" are different questions, and the tagging discipline is what buys the first one. Collapsing them would lose the more valuable half.

## Stage 2 — a display-name layer, owned here

**The precedent is already set and it settles the ownership question.** `scripts/catalogue.py` reads topic labels from Corpus's own `lookups/taxonomy.csv` rather than from the OSINT vocabulary snapshot, with the reasoning recorded in the script: *"The slugs are still OSINT's; only how they are written is decided here"* (Bill, 2026-08-19). Entity display names are the same object. Corpus derives them, Corpus owns them, and nothing is asked of OSINT.

That matters because **OSINT has no entity registry to ask for.** R11 (2026-08-16) retired `wiki/entities/`, its 1,891 pages and `ENTITY-PASS.md` on the reasoning that a tag is a terminal state; `lookups/region-membership.csv` is a frozen snapshot from before the pages went and nothing updates it. Asking OSINT to mint a name registry is asking it to reverse a decision it took deliberately — and Corpus cannot write to OSINT in any case.

**Derivation**: for each slug, take the most frequent capitalised surface form in the bodies of the sources that tag it, hold it in `lookups/entity-names.csv` as `slug,display,source` where `source` is `derived` or `hand`, and hand-correct downward from the top. Only 992 slugs carry five or more references, so the hand pass that matters is roughly a thousand rows, not seven thousand. Everything underived falls back to the hyphen-expanded slug, which is what the page shows today.

The file earns a second job immediately: **alias search**. A `display` of "National Identification and Registration Authority" indexed alongside `nira-uganda` closes the gap stage 1 leaves, at the cost of one more string per slug.

## Stage 3 — the broader index, and the question only Bill can answer

**"Or a broader index?" means searching the source bodies, and that runs straight into the metadata-only commitment.** `build-catalogue.py` carries no body text *deliberately* — "the bodies are other people's words held for the wiki's own use, and a catalogue is not a place to republish them" — and until 2026-08-25 `scripts/leak-check.py` failed the build if one appeared (`design.md` §8 — the commitment outlived the check).

> **Ruled, 2026-08-24 (Bill): "Publishing an index of names is not a licencing/copyright problem."** The question below is settled and stage 3 is admissible. What remains is engineering — the shard layout, the `RENDER.md` §9 exemption, and the lazy-fetch split — not permission. The argument is left standing because it is the reasoning the ruling was given on.

**The better reading is that a search index is not a republication, and the leak gate's own framing supports it**: `design.md` §8 says "the boundary that matters is bodies, not internal reasoning", and the gate's tests are for body-shaped *fields* — a column named `text`, a value over a length cap. A positionless inverted index delivers no expressive content and no prose can be reconstructed from it. But that is an argument, not a ruling, and **publishing it puts it in a public repo's history permanently**. By the reversibility test in `CLAUDE.md` → *Be decisive*, that makes it Bill's call rather than one to take and log.

**The recommendation, if he says yes: index names, not every word.** A read-only probe over a 900-document sample of `raw/` extrapolates to roughly **123,000 distinct proper-noun strings and 508,000 name→document postings** — about 3 MB raw, near 1 MB gzipped, against the 9.6 million words a full-text index would have to cover. It answers the question actually asked, it is an order of magnitude smaller, and "a list of the names occurring in a document" is a far easier thing to defend as an index term than a full concordance. **No snippets, in either case** — match-or-no-match is the line, because a snippet *is* the body, in fragments.

One finding from the probe worth carrying into any implementation: the naive extraction's most frequent "names" are `Value`, `Financier`, `Field`, `Amount`, `Deal ID` — the finance-record tables embedded in source pages. Tables and code blocks have to be stripped before extraction, or the index fills with column headers.

## The thing that makes this the right moment

**`design.md` §6 already lists the serving shape as open, and stage 3 forces it.**

> ~7.2 MB JSON at 9,407 records; ~23 MB at the 30,000 projected for spring 2027. A single fetch stops being defensible around 15–20k rows. […] Decide before launch, not when it breaks.

The page is at 3,992 KB of packed data on every visit and a linear scan on every keystroke. Stage 1 adds 7% and is fine. Stage 3 is not fine on that architecture at any size — but it does not have to be, because **a search index is the one payload that can be fetched lazily**: nobody who arrives to browse by country and year needs it, and it can load on first keypress. Splitting the browse payload from the search payload is the same split §6 is asking for, arrived at from the other direction, and it is cheaper to make once than to make twice.

## What stage 3 would cost a reader *(measured 2026-08-24, on Bill asking)*

The probe above was a 900-document sample and it was pessimistic. Built properly over all 10,711 documents — frontmatter, tables and code fences stripped before extraction, postings delta-encoded, gzipped — the index is smaller than the extrapolation suggested, and **sharding it makes what any one reader fetches almost too small to measure.**

| index | names | on the server | **what one search fetches** |
|---|---|---|---|
| one file, names in ≥2 documents | 34,496 | 0.68 MB | 0.68 MB |
| one file, all names | 207,998 | 2.54 MB | 2.54 MB |
| **2-char shards, ≥2 documents** | 34,496 | 1.44 MB / 586 files | **2.4 KB mean, 6.6 KB p90, 56 KB worst** |
| 2-char shards, all names | 207,998 | 7.76 MB / 809 files | 9.4 KB mean, 26 KB p90, 310 KB worst |

**Shard on the first two characters of every word in a name**, so "Cassava Technologies" is reachable from both `ca` and `te`. A reader typing `safaricom` issues **exactly one request** — the `sa` shard — because every character after the second filters what is already in memory. Median shard is 0.2 KB. Parsing the entire unsharded index takes 8 ms.

### Against the connections readers actually have

Sub-Saharan mobile sits at [15–20 Mbps on average](https://www.connectingafrica.com/4g-networks/the-state-of-mobile-broadband-affordability-in-africa), with [South Africa at 65.7 Mbps and Nigeria at 44.1 Mbps median](https://techcabal.com/2026/01/06/nigerias-average-4g-speeds-hit-33mbps/) and rural 2G/3G far below it.

| connection | today's page (1.14 MB) | a search shard (2.4 KB) |
|---|---|---|
| 2G / EDGE, ~0.1 Mbps | **~90 seconds** | under 1 second |
| 3G, ~2 Mbps | ~4.6 seconds | ~0.3 second |
| SSA average, ~20 Mbps | ~0.5 second | ~0.1 second |
| Nigeria median, 44 Mbps | ~0.2 second | latency only |

**So the answer to the question is that the thing being worried about is roughly 500 times cheaper than the thing already shipping.** `catalogue-data.js` is 3.99 MB raw and **1.14 MB gzipped, loaded by every reader on every visit whether they search or not**. A search shard is 2.4 KB — about **0.2%** of that. At Sub-Saharan data prices, where [1 GB runs about 2.4% of average monthly income and near 5% for the poorest 40%](https://www.ecofinagency.com/news/2407-47820-mobile-data-costs-still-too-high-in-sub-saharan-africa-says-world-bank), one gigabyte buys roughly 880 openings of the catalogue page — or about 437,000 searches.

**The resource problem is real, and it is not stage 3.** It is the browse payload, paid by everyone including the reader on EDGE who waits a minute and a half, and §6 projects it to roughly 3.2 MB gzipped at 30,000 records. Stage 3 is the occasion to fix that, not the cause of it.

### Three things that are genuinely costs

**Latency, not bytes.** On a poor mobile link a round trip is 300–800 ms, which dwarfs the transfer of a 2 KB file. Debounce at ~150 ms, cache every shard for the session, and never fetch on the first character.

**Word-prefix, not substring.** Typing `aricom` will not find Safaricom, where today's `indexOf` over titles would. This applies only to the names index — title, publisher and entity search stay in memory and stay substring — but it is a visible behaviour difference and the placeholder text has to say so.

**Bounded worst case, and a rule to settle.** The all-names variant has one 310 KB shard, which is 25 seconds on EDGE; split any shard over ~30 KB to three characters and the whole index fits with a bounded tail. Separately, 586–809 shard files are rebuilt on every run, so they are **not** edition-style artefacts and the immutability rule in `RENDER.md` §9 must exempt them or key them by content hash — otherwise the first rebuild trips it.

## Stage 1 — built 2026-08-24

`scripts/catalogue.py` packs the entity tags as field 10, dictionary-encoded against a vocabulary of all 6,774 slugs; `catalogue-data.js` went from 3,992 KB to 4,191 KB, **+199 KB**, under the 293 KB estimated. `scripts/build-catalogue.py`'s 200-slug facet cap is removed, so `raw-catalogue.json` now publishes the whole entity vocabulary rather than the head of it.

On the page: entity slugs join the search blob with hyphens expanded to spaces, a **Named actor** facet sits between Topic and Lens with the type-ahead the places and topics facets already use, rows carry up to three actor chips, and the facet, chips, URL hash and clear-all all behave as the existing facets do. The facet renders at most 150 options into the DOM at a time — the type-ahead searches the whole 6,774 either way — because rendering the full vocabulary on every redraw is what would otherwise make an uncapped list unaffordable.

> **The sidebar facet was removed on 2026-08-24** *(Bill, `prep/catalogue.md` §7; Lens went in the same pass, §6)*. **Nothing else in this document changes** — the search blob, the shards, the dictionary encoding and the row chips are all as described, and the entity filter itself still exists: clicking an actor chip on a row sets it, and the chip row above the results takes it off again. What went is the list of 6,774 checkboxes in the left column, and with it the 150-option DOM cap, which existed only to make that list affordable. The reason is that a search box which already reaches every one of those names by typing is a better front door to them than a scrolling list nobody can scan, and the sidebar's job is the three vocabularies a reader browses *by* — place, topic, year.



**Measured against the old title-and-publisher search, over the same 10,711 records:**

| search | before | after |
|---|---|---|
| `world bank` | 287 | **642** |
| `mtn` | 121 | **257** |
| `starlink` | 237 | **306** |
| `safaricom` | 50 | **112** |
| `huawei` | 65 | **127** |
| `nira` | 20 | **68** |

**Display names are still stage 2.** The facet label is the slug, mechanically prettified — title-cased, except short tokens, which in this vocabulary are overwhelmingly acronyms. The exception list for short tokens that are ordinary words was populated by measuring rather than guessing: 1,548 distinct tokens of four characters or fewer would be uppercased, and the frequent ones were read off and sorted, which is how `cote`, `faso` and `das` were caught. It gives `World Bank`, `ITU`, `UNDP`, `NIMC`, `Air Cote Divoire`, `ADCT Burkina Faso`, `Acacia Economics Pty Ltd`. It is provisional by construction and `lookups/entity-names.csv` replaces it.

Verified by driving the built page under jsdom: first paint and a full redraw including the entity recount both complete well inside a frame budget even in jsdom, which is far slower than a browser; the leak gate passes on `site/`.

## Stage 3 — built 2026-08-24

`scripts/build-names-index.py` extracts names from the source bodies and writes `outputs/names/`; `scripts/catalogue.py` packs the shard keys into the page and publishes the shards. **201,284 names over 430,929 postings across all 10,731 documents, in 1,896 shards.** *(Re-measured 2026-08-24 after stage 2 moved the extraction into `names_lib.py`; the first stage-3 build read 207,911 names over 1,889 shards, and the difference is the shared stopword sets, not the corpus.)*

**What a reader downloads, typing a whole query, measured by driving the built page:**

| query | requests | gzipped | records found |
|---|---|---|---|
| `bosun tijani` | 1 | 36.1 KB | 72 (was 1 on title and publisher) |
| `equity bank` | 1 | 7.7 KB | 7 (was 0) |
| `konza technopolis` | 1 | 13.0 KB | 46 |
| `flutterwave` | 1 | 6.4 KB | 44 |
| `vodacom` | 1 | 12.0 KB | 152 |
| `huawei` | 1 | 17.2 KB | 305 |

**One request per query, not one per character** — the debounce is 150 ms and every character after the shard key filters what is already in memory. Against the 1.25 MB gzipped that `catalogue-data.js` costs every reader on every visit, a search is 0.5–3% on top, and a reader who only browses pays nothing at all.

Four decisions worth keeping in view.

**Stable document ids, not row positions.** Postings key on `outputs/catalogue/doc-ids.csv`, which is append-only. Rows sort by date descending, so keying on row position would have shifted every id below each new source and rewritten all 1,896 shards every cycle. A second identical build now rewrites **zero** shards, which is the property that makes this affordable in git.

**Shard on every word, two characters deep, re-cut where fat.** "Cassava Technologies" is reachable from `ca` and from `te`. The first cut left a 248 KB shard, and one re-cut left 244 KB — English prefixes are not uniformly distributed, so the split had to become iterative. The remaining lever was that `of` and `the` were being used as shard keys, collecting every name containing them into a bucket too short to cut; excluding words nobody searches took the worst shard to **94.9 KB**, with a 0.5 KB median and a 10.7 KB p90.

**Word-prefix, not substring, and never under three characters.** `aricom` will not find Safaricom. Title, publisher and entity search stay in memory and stay substring; the placeholder and the note under the results say which is which, and a query too short to search names says so rather than silently returning less.

**It degrades to stage 1.** If the fetch fails or `fetch` is absent, the page keeps the in-memory results and loses only the extra matches — verified by stubbing the fetch to fail, which returns exactly the stage-1 count.

## Stage 2 — built 2026-08-24

`scripts/build-entity-names.py` writes `lookups/entity-names.csv`: **4,683 of 6,787 slugs named (68%)** — 4,045 `full`, 361 `acronym`, 277 `partial` — with the remaining 2,104 falling back to the page's prettifier. `catalogue.py` uses the derived name for the facet label, the row chips and the search blob, so `nira-uganda` now reads *National Identification and Registration Authority* and is reachable by typing it.

The extraction is shared with stage 3 rather than rebuilt: `names_lib.py` holds it, and the three readers import it. That module exists because a third reader appeared, which is the point at which duplication stops being cheaper.

**Three scoring lessons, each found by looking at what came out.**

**Strip the place before scoring.** Plain token overlap gave `pura-gambia` → "The Gambia" and `sec-nigeria` → "Nigeria": a country suffix is the least distinguishing part of a slug and was winning on its own. Scoring now runs on the slug's distinguishing tokens, with the place kept only as a tie-break so `bank-of-namibia` still prefers "Bank of Namibia" over "Bank". Those two now give *Public Utilities Regulatory Authority* and *Securities and Exchange Commission*.

**An acronym match must not expand to a place.** `bf` is the initials of "Burkina Faso", so the fix above simply moved the bug: `bf-ministry-digital-transition` derived the country and dropped the ministry. An expansion made entirely of place tokens is now rejected, and that slug falls back to the prettifier — which is straight with the reader, and better than a confident wrong answer.

**Thin evidence must be tight evidence — except for acronyms.** 4,074 slugs are tagged by exactly one source, so requiring two sources to agree is not a quality bar but a 78%→25% coverage cut on slugs that can never corroborate. What separates a good single-source derivation from a bad one is how much of the candidate the slug fails to explain: "Bank of Namibia" explains itself, "Draft ODPC Guidance" and "ID for All The Electoral Commission of Uganda" are extraction runs that crossed a heading. So the allowance for unexplained tokens grows with corroboration. Applying that to acronyms was then a mistake of its own — an expansion never contains its own initials, so *every* word is unexplained by construction, and the rule cost `undp` its "United Nations Development Programme" for being four words long while three-word `itu` survived. A threshold that fires on word count while claiming to measure fit is worth catching early.

**The file is meant to be corrected.** `basis` set to `hand` is never overwritten, and `basis` plus `sources` together say how far to trust a row, so a hand pass can start with the weakest. Ownership follows the `lookups/taxonomy.csv` precedent exactly: the slugs are OSINT's, how they are written is decided here.

## Recommendation

1. ~~**Build stage 1 now.**~~ Done.
2. ~~**Stage 3 is cleared to build.**~~ Done.
3. ~~**Stage 2.**~~ Done — and it did come out cheap, because stage 3's extraction was most of it.
4. **`design.md` §6 is still open and is now the live constraint.** The browse payload is 1.25 MB gzipped for every reader and heads for roughly 3.2 MB at the 30,000 records projected for spring 2027. The names index is the proof that lazy fetching works on this site; the browse rows are the thing that should use it next.
