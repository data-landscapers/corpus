---
type: design-note
reader: cc
title: whos-who.md — a Who's Who index of officeholders, built in Corpus
last_reviewed: 2026-11-19
status: design, owned by CC; nothing built; Bill's rulings are §10, what stage 1 measures §11
---

# Who's Who index

*(Drafted 2026-11-19 in Cowork from Bill's brief and rulings; reviewed and taken over by CC the same day, with Bill agreeing every review point. The counts were measured that day; the extraction yield in §5 is a rough sample that stage 1 replaces.)*

## 1. What it is, and the one rule

**A public index of who held which position in which organisation, in which year, with the source that says so.** One row is one attestation: a named source, published in a given year, states that a person holds or held a position at an organisation.

**History is the point, not a by-product** *(Bill, 2026-11-19)*. The reader has seen a name in the news and wants the rest: where this person has been, and who else has passed through this organisation. A person's past positions and an organisation's past holders are worth more than a list of who is in post, so a statement about a former holder is kept and the views in §8a let the reader follow both.

**For legal reasons a published row carries five fields and no others** *(Bill, 2026-11-19)*: `name`, `year`, `position`, `organisation`, `source_url`. No biography, nationality, gender, age, photograph, summary or quotation. The rule is on the output; §3 extends it to everything this repo commits, because the repo is public.

**The build belongs in Corpus and asks nothing of OSINT.** OSINT tags institutions and not officeholders, and holds no entity registry to extend. The precedent is `build-entity-names.py`: the slugs are OSINT's, and how they are written is decided here.

## 2. What exists already

| Thing | Where | State |
|---|---|---|
| Sources | mirror `raw/` | about 46,600, each with `url`, `published`, `date_precision`, `places`, `entities` in frontmatter; the catalogue holds 45,288 of them |
| Organisation display names | `lookups/entity-names.csv` | 10,935 slugs; basis `full` 9,529, `partial` 737, `acronym` 669; `hand` rows survive a rebuild; four readers |
| Organisation variants | `scripts/entity-variants.py` | groups split slugs by country suffix, French and English stems, and initialisms; rules nothing |
| Name extraction | `scripts/names_lib.py` | capitalised runs from prose, built for search recall; does not tell a person from an organisation; four readers (`build-entity-names`, `build-names-index`, `catalogue`, `shard_lib`) |
| People | nowhere | no table, no ids, no deduping |

## 3. The boundary this adds

**Everything committed to this repo about a person is one of the five fields or an opaque key.** The repo is public and its history is permanent, so a working file is as published as a page. Four consequences:

- **No evidence sentence is ever written to a tracked file.** The extractor reads the body, emits the fields and the source's URL, and discards the text.
- **No attribute is stored on a person.** Not a country, not a type, not a note. A person's place is derived at build time from the organisations of their positions and is never written down.
- **Scratch that holds bodies or sentences lives outside the repo**, as `osint-patch.py`'s clone does.
- **The extraction cache is tracked** (§4): it holds only a name as written, a title, an organisation as written, years and a URL, so it is inside the rule, and it is the one artefact a rebuild cannot cheaply remake.

## 4. The model

Lookups and the cache are CSV. Lookups are hand-correctable and a deriver never overwrites a `hand` row.

**`build/whos-who/extract.csv`** — tracked; the model's output, one row per tuple: `source_url`, `name_as_written`, `position`, `org_as_written`, `tense`, `year`, `year_to`. **Keyed by `source_url`, not file path**, so a source the mirror re-files is not read again and its rows keep their ids. A source is read once; a source with no tuples gets one row with the rest blank, so it is not read again either. Organisation and person are resolved from it at every build, so a slug merge or an alias ruling takes effect without the model.

**`lookups/organisations.csv`** — one row per organisation the index names. A sidecar keyed on OSINT's slug, so `entity-names.csv`, which is rebuilt nightly and has four readers, is untouched.

| column | holds |
|---|---|
| `slug` | OSINT entity slug |
| `canonical_slug` | the slug this one publishes under; itself unless two slugs are one body |
| `name` | published name; defaults to `entity-names.csv` → `display` |
| `place` | ISO-3 or `X__` code, from the dominant place of the sources tagging it |
| `kind` | `government` or `other`, from `lookups/whos-who-gov-stems.csv` (§6) unless `hand` |
| `basis` | `auto` or `hand` |

**`lookups/org-lineage.csv`** — `slug`, `successor_slug`, `year`, `basis`. Government only (§6).

**`lookups/people.csv`** — `person_id`, `name`, `basis`. The id is opaque and issued once; it is never derived from the name, so a corrected spelling does not move it.

**`lookups/person-aliases.csv`** — `alias`, `person_id`, `basis`. Every written form of a name that resolves to a person. An alias is a name and nothing else.

**`lookups/person-rulings.csv`** — `person_id_a`, `person_id_b`, `ruling` (`same` or `different`), `ruled`. Hand rulings on candidate merges, so a question is asked once.

**Word lists, all lookups:** `whos-who-roles.csv` (role words, §5), `whos-who-deny.csv` (words a position may never carry, §5), `whos-who-gov-stems.csv` (§6).

**`build/whos-who/positions.csv`** — untracked; the derived fact table: `person_id`, `slug`, `position`, `tense`, `year`, `year_to`, `source_url`. Rebuilt whole from the cache and the lookups; never edited by hand. A wrong row is fixed in a lookup or the suppression list (§7), or by deleting its source's cache rows so the source is read again. `merge-candidates.csv` sits beside it, also untracked.

The published table is the join: `people.name`, `year`, `position`, `organisations.name` through `canonical_slug`, `source_url`. `tense` and `year_to` publish inside the five fields and add none: a `held` row's position reads `{position} (former)`, and a span reads `2015–2019` in the year column.

## 5. Extraction

**A row needs a person, a position and an organisation in the same statement.** That is the scope test as well as the extraction rule: a private individual named in a story has no position at an organisation and cannot produce a row.

**Only catalogue sources are read, and only their body.** A source outside the catalogue would fail lint 3. The frontmatter is stripped whole — including `note:` and `catalogue_hero`, which name people and posts in OSINT's words rather than the source's — and so is the `Author:` byline.

1. **Candidate pass, deterministic.** Find sentences where a name-shaped run sits beside a role word (`Minister`, `Ministre`, `Ministro`, `Director-General`, `Commissioner`, `Governor`, `Chief Executive`, `Chair`, `Permanent Secretary` and their French, Portuguese and Spanish forms — Equatorial Guinea's sources are Spanish). In a rough sample of 3,000 files from `raw/2026`, 952 contained a role word, so about 15,000 files reach the model.
2. **Reading pass, by model, over the candidate sentence only.** Returns zero or more `(name, position, organisation-as-written, tense, years-if-stated)` tuples, or nothing. `position` is the title alone, with no adjective the title does not carry. It returns nothing for a nominated, rumoured or hypothetical holder: a person who has not held the post has no row.

**A former holder is a row, with `tense` `held`.** Three kinds of statement produce one, and the extractor tells them apart only to set the year:

- **Described as former** (`former Minister of Finance`, `ex-PDG`, `ancien ministre`): `held`, and the year is the source's own, which says only that by then the person had left. The published row reads *Minister of Finance (former)* against that year.
- **A stated term** (`who served as governor from 2015 to 2019`): `held`, `year` and `year_to` as the source gives them. This is the one case where a row carries a span, because the source states it.
- **A departure reported** (`stepped down`, `was replaced as`, `a quitté ses fonctions`): `held`, in the year of the event. **How or why the person left is never recorded** — not in the position text and not anywhere else. Resignation, dismissal and removal all publish as the same word.

**An appointment reported is a `holds` row in the year of the event.** An acting or interim holder is a `holds` row whose position keeps the source's own qualifier.

**The organisation is resolved against the source's own `entities:` tags first.** The tagged slugs are the short list; the organisation-as-written is matched to one of them through `entity-names.csv` and the variant rules. No match means the row is dropped and counted, not invented.

**`year` is the year the source attests, and claims nothing about a term of office.** It is the year of `published`, unless the sentence carries its own date. A source with `date_precision` coarser than a year yields no row. Two sources in two years are two rows; the index never infers a start, an end or the years between, and never turns a `holds` row into a `held` one because time has passed or a successor has appeared. **Nothing in the index says who is in post today**; the latest attested year is the most it claims.

**`position` is the title as the source gives it, normalised only for case and whitespace, and it is the field the legal rule leans on hardest**, because it is free text written by a model. A position must contain a word from `whos-who-roles.csv` and none from `whos-who-deny.csv` — manner-of-departure and evaluative words in every language read (`sacked`, `disgraced`, `limogé`, `embattled`, `corrupt`, `controversial`, …) — and runs to at most twelve words. A tuple that fails is dropped and counted, not repaired. A French title stays French. No controlled vocabulary of titles in version one.

**`source_url` is the source's `url` — the publisher's own page.**

## 6. Organisations, and why government is the special case

**For most organisations the existing display name is the canonical name**, and the work is the 737 `partial` rows that reach the index, corrected by hand as `hand` rows in `entity-names.csv`.

**`kind` is `government` when the slug or display name carries a stem from `whos-who-gov-stems.csv`** — `ministry`, `ministere`, `ministerio`, `ministério`, `department-of`, `office-of-the-president`, `presidency`, `primature` and the like — and `hand` rows correct it. There are 499 slugs containing `ministry` and 46 more starting `ministere` or `ministerio`.

**A government department differs in three ways.**

- **The published name carries the country.** `angola-ministry-of-interior` displays as *Ministry of Interior*, which is one of dozens. Where `kind` is `government` and the name does not already contain its place, the published form is `{name}, {country}`.
- **A ministry's name is true for a period.** Reshuffles rename, merge and split portfolios. **Each named incarnation keeps its own row and its own slug**, because a 2019 attestation should publish under the 2019 name, and `org-lineage.csv` links an incarnation to its successor. Nothing is collapsed. Lineage is filled by hand where a reader would be misled; it is not a completeness target.
- **One body, two languages.** `ministere-justice-djibouti` and an English slug for the same ministry are one organisation; `entity-variants.py` already finds these. A confirmed pair sets `canonical_slug` here and is sent to OSINT as an `[ACT]` note so the tags converge; the index does not wait for that. When OSINT merges two slugs, the dropped one's `organisations.csv` row goes in the same commit as the rebuild that stops resolving to it.

**The government itself is not a position-holding organisation.** A row resolving only to `government-of-{country}` is kept for heads of state and government and dropped otherwise, since *Minister, Government of Ghana* tells a reader nothing the ministry row would not.

## 7. People: deduping, and removal

**A wrong merge credits one person with another's office, which is the worst error this index can make. A missed merge shows one person twice, which is mild.** Every rule resolves towards keeping people apart.

**Normalisation, for comparison only** — the published name is never the normalised one. Strip honorifics and post-nominals (`Dr`, `Hon.`, `Eng.`, `Prof`, `S.E.`, `MP`), fold case, accents and punctuation, and treat token order as free, because the corpus writes family names first and last.

**Merge automatically only when** the normalised names match in full **and** the two attestations share an organisation, by `canonical_slug` or lineage. A shared country is not enough: common names recur within one country, so a same-name, same-country pair is a candidate. An initial against a full given name (`A. Mensah`, `Ama Mensah`) is never merged automatically, even inside one ministry.

**Everything else that looks alike is a candidate, written to `merge-candidates.csv` and left separate** until a row in `person-rulings.csv` settles it. It is a report, not a queue; unresolved candidates are a correct resting state.

**The canonical name is the fullest form the sources give, most frequent first on a tie**, and a `hand` row overrides it.

**Removal takes the name out of every tracked file, not only the output.** `lookups/whos-who-suppress.csv` holds `person_id` or a `(person_id, slug)` pair with the date; the build drops matching rows before anything is written to `outputs/`. A whole-person removal also blanks the person's `name` in `people.csv` (the id stays, so it is never reissued), deletes their aliases, and blanks `name_as_written` on their cache rows, in the same commit. It carries no reason column — a reason is a statement about a person. **Git history still holds the name**, which ruling 2 accepts; the method page promises removal from the site and the download, and no more.

## 8. Publication

- **Page:** `/whos-who/`, one page (§8a).
- **Download:** one **undated, current-only CSV** *(Bill)*, so a removal is complete at the next build. It joins the catalogue as a named exception to `design.md` §9, amended in the commit that publishes.
- **Output:** `outputs/whos-who/whos-who.csv`, exactly five columns.
- **Method page:** a section under `/methodology/` saying what a row is and is not — an attestation in a year, not a term — and how to ask for a correction or removal.
- **Change log:** one entry at launch.

**Lints, all in `scripts/lint-whos-who.py`, failing the build:**

1. `outputs/whos-who/*.csv` has exactly the five columns, in order.
2. Each tracked lookup and the cache have exactly their declared columns from §4.
3. Every `source_url` is a catalogue URL; every `slug` exists in `entity-names.csv`.
4. No suppressed person or pair appears in `outputs/`; no suppressed person has a name, alias or cached name anywhere tracked.
5. No published name appears under two `person_id`s within one organisation, unless `person-rulings.csv` rules the pair `different` — the visible symptom of a missed safe merge.
6. Every published position passes §5's role-word, deny-list and length test.

## 8a. Searching, browsing and viewing

**A view is the one table, filtered** *(Bill)*. Selecting a name in any row filters to that person's rows; selecting an organisation filters to its rows, following `org-lineage.csv` through a ministry's earlier names, each shown under the name it had. Every row in one view opens the other. The filtered table is the shared datatable and nothing more: **the reader sorts by person, position or year**, and the page imposes no grouping and no sequence of its own.

**The filtered rows download as a CSV, cut in the browser** *(Bill)*: one person's positions or one organisation's, the five columns, the rows on screen. It is the catalogue's filtered download (`documentation/archived/catalogue-filtered-download.md`) and has no URL of its own.

**No link opens a person's view** *(Bill)*. No `person_id` appears in a URL, a fragment, the page source a reader would copy, or the download. The page may keep a search term in the fragment as the catalogue does; a name there is a search, and it finds everyone of that name.

**Nothing else on the site links in, in version one** *(Bill; to be reconsidered)*. Reports and catalogue rows do not link names to the index.

**A person's view links out to the catalogue's name search** *(Bill)*, so "more" is every held document that mentions the name. The names index needs no rebuild: it holds 2,296,073 names over all 45,288 catalogue documents with no frequency cut-off. But the link is not exact. The index keys each spelling separately, so the link searches every alias and not the canonical name alone; and `names_lib.NAME` starts a name only at an ASCII capital and joins only its listed particles, so *Élisabeth* loses its first token and a lower-case *ould* splits a name in two. An alias absent from the index is left out of the search. A change to `names_lib.NAME` is its own job, since it moves `entity-names.csv` and three other readers.

**Search on the page is over names and aliases**, on `shard_lib.py`'s client-side pattern, so a variant spelling finds the person. **Browse is by country, then organisation.** No A to Z of people: the corpus writes family names first and last, and the index does not know which token to file under.

**Two people with one name are two sets of rows**, told apart only by their organisations and years. The index never adds a distinguishing label.

**The page says what the rows are, above every view and in the download's metadata file** *(Bill)*: each row is one source's statement in one year; the list is what the held sources happen to attest, with gaps; a missing row is not a vacant post; and **an organisation's rows are not a line of succession** and should not be cited as one. The same words head the method section.

## 9. Build stages

1. **Pilot, one French-language country** — the best-covered one, where name order and ministry naming are hardest. Both extraction passes into scratch and the cache. *Finish:* a hand check of 200 rows giving precision for person, position, organisation and `tense` separately; the drop counts by cause; and the §11 measurements.
2. **Organisations sidecar.** `organisations.csv` built for every slug the pilot reached; `kind` and the government naming rule applied. *Finish:* no published government name ambiguous across countries.
3. **People.** Ids, aliases, the merge rule, the candidates report. *Finish:* lint 5 clean on the pilot country; a sample of 100 automatic merges checked by hand with none wrong.
4. **Full run and incremental.** The model pass is never inside `rebuild.py`, which runs no model stages. `rebuild.py` gains a deterministic stage after 2c that runs the candidate pass and builds `positions.csv` from the cache; the reading pass is a model step after the rebuild, over candidate sources not yet in the cache, as report authoring follows stage 4. The full first run is its own job. *Finish:* a nightly run adds rows without reissuing an id, and the page-weight lint passes at the full row count.
5. **Publish.** Page, views, filtered download, method section, lints in the render gate, change-log entry.

## 10. Bill's rulings, 2026-11-19

1. No dated editions (§8).
2. The people tables may live in the repo (§4).
3. Former holders are kept; history is the purpose (§1, §5).
4. No page per person and no link to a person's view; a filtered CSV instead (§8a). A `#` person link stays closed.
5. No links in from the rest of the site in version one.
6. A link out to the catalogue's name search, if the names index serves it (§8a).
7. Views are sortable filtered tables, with a plain statement that no line of succession is suggested (§8a).
8. CC's review points agreed whole, and the module is CC's from here.
9. A design note is uncapped until built; `lint-docs.py` exempts `type: design-note` while `status:` begins "design".

Nothing is open with Bill.

## 11. What stage 1 measures

- **Cost:** tokens per file through the reading pass, scaled to about 15,000 files. A rough expectation is in the range of a first-pass maturity batch, about 2% of the week; a pilot that implies much more is reported before the full run.
- **The catalogue link:** the share of aliases that are exact entries in `outputs/names/`, and of people with none; whether the catalogue's search takes several names in one query and can match a whole name.
- **Page weight:** rows per source, scaled. The table's data file must stay under 2 MB compressed (`lint-page-weight.py`); past it, the catalogue's split applies. 100,000 rows is the query-service line, and a plausible yield is well under it.
