---
type: design-note
reader: cc
title: whos-who.md — a Who's Who index of officeholders, built in Corpus
last_reviewed: 2026-11-20
status: design, owned by CC; stages 1–4 done, stage 5 live unlinked, launch owed (§15); Bill's rulings are §10, results §11–§15
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

**`build/whos-who/extract.csv`** — tracked; the model's output, one row per tuple: `source_url`, `name_as_written`, `position`, `org_as_written`, `slug_hint`, `tense`, `year`, `year_to`. `slug_hint` is the model's pick from the source's own tags, kept only if it is one of them; the build prefers it and falls back to matching. **Keyed by `source_url`, not file path**, so a source the mirror re-files is not read again and its rows keep their ids. A source is read once; a source with no tuples gets one row with the rest blank, so it is not read again either. Organisation and person are resolved from it at every build, so a slug merge or an alias ruling takes effect without the model.

**`lookups/organisations.csv`** — one row per organisation the index names. A sidecar keyed on OSINT's slug, so `entity-names.csv`, which is rebuilt nightly and has four readers, is untouched.

| column | holds |
|---|---|
| `slug` | OSINT entity slug |
| `canonical_slug` | the slug this one publishes under; itself unless two slugs are one body |
| `name` | published name; `entity-names.csv` → `display` where derived whole, else the sources' own wording (§12) |
| `place` | ISO-3 or `X__` code, from the dominant place of the sources tagging it |
| `kind` | `government` or `other`, from `lookups/whos-who-gov-stems.csv` (§6) unless `hand` |
| `basis` | `auto` or `hand` |

**`lookups/org-lineage.csv`** — `slug`, `successor_slug`, `year`, `basis`. Government only (§6).

**`lookups/people.csv`** — `person_id`, `name`, `basis`, `anchor`. The id is opaque and issued once; it is never derived from the name, so a corrected spelling does not move it. `anchor` is a 12-character hash of the person's first cache row, which is how a rebuild finds the id again (§13); `basis` `retired` marks an id a ruling joined to another, kept so it is never reissued.

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

**The organisation is resolved against the source's own `entities:` tags first.** The tagged slugs are the short list; the organisation-as-written is matched to one of them through `entity-names.csv` and the variant rules. When none matches, any tagged slug in the catalogue may, by name or stem and in the source's own country (`whos_who_lib.py` states the narrowing). No match means the row is dropped and counted, not invented.

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

**Merge automatically only when** the normalised names match in full **and** the two attestations share an organisation, by `canonical_slug` or lineage. A shared country is not enough: common names recur within one country, so a same-name, same-country pair is a candidate. An initial against a full given name (`A. Mensah`, `Ama Mensah`) is never merged automatically, even inside one ministry. **One exception** *(Bill, 2026-11-20)*: a shorter name whose words are all in a fuller one at the same organisation, holding the same position, joins it, when it fits exactly one fuller name; different positions stay two people. Where `lookups/naming-conventions.csv` marks names patronymic, the shorter must also be the start of the fuller.

**Everything else that looks alike is a candidate, written to `merge-candidates.csv` and left separate** until a row in `person-rulings.csv` settles it. It is a report, not a queue; unresolved candidates are a correct resting state.

**The canonical name is the shortest form that keeps the first and last words of the fullest** *(Bill, 2026-11-20)*, so *Alassane Ouattara* but not *Oligui Nguema*; a surname in capitals is written in normal case, and a `hand` row overrides it.

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
3. Every `source_url` is a catalogue URL; every `slug` is a catalogue tag. (Not `entity-names.csv`: a fifth of resolved rows reach a slug it could not name, §12.)
4. No suppressed person or pair appears in `outputs/`; no suppressed person has a name, alias or cached name anywhere tracked.
5. No published name appears under two `person_id`s within one organisation, unless `person-rulings.csv` rules the pair `different` — the visible symptom of a missed safe merge.
6. Every published position passes §5's role-word, deny-list and length test.

## 8a. Searching, browsing and viewing

**A view is the one table, filtered** *(Bill)*. Selecting a name in any row filters to that person's rows; selecting an organisation filters to its rows, following `org-lineage.csv` through a ministry's earlier names, each shown under the name it had. Every row in one view opens the other. The filtered table is the shared datatable and nothing more: **the reader sorts by person, position or year**, and the page imposes no grouping and no sequence of its own.

**The filtered rows download as a CSV, cut in the browser** *(Bill)*: one person's positions or one organisation's, the five columns, the rows on screen. It is the catalogue's filtered download (`documentation/archived/catalogue-filtered-download.md`) and has no URL of its own.

**No link opens a person's view** *(Bill)*. No `person_id` appears in a URL, a fragment, the page source a reader would copy, or the download. The page may keep a search term in the fragment as the catalogue does; a name there is a search, and it finds everyone of that name.

**Nothing else on the site links in, in version one** *(Bill; to be reconsidered)*. Reports and catalogue rows do not link names to the index.

**A person's view links out to the catalogue's name search** *(Bill)*, so "more" is every held document that mentions the name. The names index needs no rebuild: it holds 2,296,073 names over all 45,288 catalogue documents with no frequency cut-off. But the link is not exact. The index keys each spelling separately, so the link searches every alias and not the canonical name alone; and `names_lib.NAME` starts a name only at an ASCII capital and joins only its listed particles, so *Élisabeth* loses its first token and a lower-case *ould* splits a name in two. An alias absent from the index is left out of the search. A change to `names_lib.NAME` is its own job, since it moves `entity-names.csv` and three other readers.

**Nothing shows until the reader searches** *(Bill, 2026-11-20)*: three letters, a country or an organisation. **Search is over names, aliases, positions and organisation names**, so a variant spelling finds the person and *minister of finance* finds the post across countries. **The organisation filter stands alone** *(Bill, 2026-11-20)*: a body with no country, or filed under the wrong one (the Gates Foundation's `place` is TZA), is one choice away; a country narrows the organisations offered and is never required. No A to Z of people: the corpus writes family names first and last, and the index does not know which token to file under. Stage 5 (§15) says how it was built.

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

## 11. Stage 1, Côte d'Ivoire, 2026-11-19

**Done.** `scripts/whos-who-candidates.py` and `scripts/whos-who-cache.py`; the reading pass is Sonnet agents on `C:\whos-who-work\brief.md`, one batch each.

- **Yield:** 1,210 catalogue sources; 847 with candidate sentences (4,081); 604 yielded 1,241 rows, 238 nothing. Lints dropped 55 tuples: 26 positions over 12 words, 22 with no role word, 2 names under 2 words, 2 the source's author.
- **Precision, 200 rows by hand:** person 200/200, position 198/200, organisation 197/200, tense 200/200 (few `held` rows in the sample, so tense is thinly tested).
- **Cost:** about 1.6M Sonnet tokens, of which about 50k a batch is fixed agent overhead; batches are now 150 sources. The full catalogue has 31,089 sources with candidates and 179,088 sentences, so roughly 55–70M tokens.
- **The role list was widened** after the check (board members, advisers, chefs de cabinet, secretaries): positions such as *Membre du Conseil* had failed the role-word lint.
- **Authors:** 2 of 835 rows were a source's own author named with a post in the text; the cache now drops a name that matches the catalogue's `author`.

**Full reading pass, done 2026-11-19** (paused once at the quota line, resumed at 19:13): 202 + 103 batches. The cache holds 42,357 attestations (1,377 `held`) from 30,923 sources; about 180–250k Sonnet tokens a 150-source batch. **14 sources an agent skipped remain uncached** and go to the next incremental pass. **To run a pass:** empty `C:\whos-who-work\candidates\all\` and `out\all\`, run `whos-who-candidates.py --all` (the cache excludes what is done), launch readers on the brief, and admit each finished batch with `whos-who-cache.py all --only N`. Stage 2 followed (§12).

**Measured since:** §13–§14. The pilot's rate, about 1.5 rows a candidate source, puts the full index near 45,000 rows, under the 100,000-row query-service line.

## 12. Stage 2, organisations, 2026-11-20

**Done.** `scripts/whos_who_lib.py` resolves a cached tuple to a slug; `scripts/whos-who-orgs.py` writes `lookups/organisations.csv` and exits 1 on the finish line; `scripts/test_whos_who_lib.py` pins each wrong match below. `org-lineage.csv` is header-only, filled by hand where needed.

- **Resolution:** 33,358 of 42,357 tuples (79%) reach a slug — 26,378 by the model's hint, 3,030 by a bare country to its government, about 3,950 by the untagged fallback. Dropped: 8,638 name a body no tagged slug matches (ManageEngine, AOS Ltd), 218 match two slugs, 141 name a country with no government slug.
- **Hints are trusted.** In a sample of 40 where the written form does not match the slug, all 40 were right (acronyms, translations); a hint is overridden only when the organisation names another country.
- **Organisations:** 6,384, 1,198 of them government; 24 government slugs fold into another (same country, same stem; a national government in any language). The finish line holds: no published government name stands for two countries or none.
- **Names:** 4,448 from `entity-names.csv`, 1,870 from the sources' wording, 63 *Government of {country}*. 148 slugs (217 rows) are left out because no written form is recognisably theirs — person-named slugs such as `joao-lourenco` among them — until a `hand` row names one.
- **Wrong matches found and fixed:** a named country ignored (*Burkina Faso Ministry of Health* to Eswatini's); the two Congos; regions stripped as countries (Somaliland and Puntland folded, Tshopo named DR Congo's government); a foreign ministry a story tagged (Sudan's foreign ministry to China's); folds on equal names (*Ministry of Health and Sanitation* is its own incarnation). Embassies and high commissions are `government`, so *Indian High Commission* carries its host.
- **Left for stage 3 or by hand:** 48 pairs of government slugs in one country with one published name (`bf-ministry-digital-transition`, `ministere-transition-digitale-burkina-faso`) are not folded; folding on a name is what merged two incarnations. 35 of the 48 were plainly one body written two ways and were folded by hand the same day (39 `hand` rows), which retired 48 person ids into their twins as §13 intends. The 13 left are probable incarnations (*Ministry of Education* against *Education, Science and Technology*) or have a guessed place. The `[ACT]` note asking OSINT to converge the folded tags goes at publication, per §6.


## 13. Stage 3, people, 2026-11-20

**Done.** `scripts/whos-who-people.py` writes `lookups/people.csv` and `person-aliases.csv` (tracked) and `build/whos-who/positions.csv` and `merge-candidates.csv` (untracked), with `person-rulings.csv` and `whos-who-suppress.csv` header-only.

- **Counts:** 33,090 positions for 17,112 people from 33,092 facts. Dropped before people: 8,908 with no organisation, 217 at an unnamed one, 133 at a national government held by someone who is not its head, and 7 names under two words once titles are off.
- **Merges:** 887 people carry more than one written form. **A hand check of 100 found none wrong**: the variants were case, accents, order, hyphens and apostrophes (*Denis Sassou-N'Guesso* in 16 spellings). The check found one risk, now closed: a middle *M.* was being stripped as *Monsieur*, so titles come off the ends of a name only.
- **Lint 5:** clean on Côte d'Ivoire and estate-wide.
- **Candidates:** 2,662: 1,157 same name in one country at two organisations, 927 one name inside the other at one organisation, 333 same name across countries, 53 an initial against a given name. They are left unresolved. A career across two ministries is two people until a `same` ruling joins it, which is what §7 trades for never crediting one person with another's office.
- **Ids:** `anchor` hashes the whole cache row (source, name, position, organisation as written). Hashing only the source and the name tied two organisations' groups to one id whenever a story named someone in two posts, and 76 ids retired on a second build. With the whole row, three successive builds issue and retire nothing.

## 14. Stage 4, full run and incremental, 2026-11-20

**Done.** `rebuild.py` stage 2e runs `whos-who-candidates.py --all`, `whos-who-orgs.py` and `whos-who-people.py`, all soft. The reading pass is BUILD stage 4d, `WHOS-WHO-UPDATE.md`, with the brief now `documentation/whos-who-reader-brief.md`. Old work batches are moved to `C:\whos-who-work\done-{date}\`, not deleted.

- **Incremental:** with the newest 3,000 cache rows withheld and then added, 902 people were new, no existing id moved, and nobody lost a row. The first real pass, on 2026-11-20, read one batch of 130 sources: the 14 skipped and the arrivals since. It admitted 171 rows from 97 sources, with 33 yielding nothing and 10 tuples dropped by the position lints, for about 160k Sonnet tokens. The rebuild issued 44 new ids and retired none.
- **Page weight:** at 33,090 rows the five-column CSV is 6.1 MB, **1.87 MB compressed against the 2 MB line**. It crosses at about 35,000 rows, weeks away. Packing people and organisations as lookups saves almost nothing (1.82 MB); the source URLs are 1.3 MB of it, and the table without them is 0.5 MB. **Stage 5 therefore ships the catalogue's split**: the four shown columns up front, the source URL fetched when a row is opened. The download stays the full five columns.
- **Still to measure at stage 5:** the share of aliases that are exact entries in `outputs/names/`, and whether the catalogue's search takes several names and matches a whole name.

## 15. Stage 5, publish, 2026-11-20

**Live at `/whos-who/`, `noindex`, out of the sitemap and the nav** *(Bill: work on it live before it is linked)*. `scripts/whos-who-publish.py` writes the page, `outputs/whos-who/whos-who.csv` and its site copy, the metadata file and the search data; `rebuild.py` stage 2e runs it after `whos-who-people.py`. `site/assets/js/whos-who.js` is the search; `whos-who.css` the layout.

- **The split, on demand.** `data/index.json` (people, aliases, organisations, positions, rows as offsets; 548 KB compressed at 33,229 rows) is fetched on the first search, not with the page. Source URLs are in `data/src-NNN.json`, keyed by the catalogue's append-only document id in blocks of 1,000, fetched for an opened row or a download. People are indexed by name order, never by `person_id`.
- **The shared table, driven.** Datatable v5 (data-landscapers `33df416`) added `data-defer`, `dt:render` and `dt:detail`; each search hands the table a CSV cut in memory, and the row panel carries the source and three ways out: this name, this organisation, this name in the catalogue. The table's own toolbar is hidden, so there is one search.
- **Lints:** `scripts/lint-whos-who.py`, RENDER Step 7, holds §8's six and two more: the index under 2 MB compressed, which `lint-page-weight.py` cannot see on a table built on demand, and no `person_id` on the site. A World Bank project id has the same shape, so URLs are not searched.
- **One published row per person, position, organisation and year** *(Bill, 2026-11-20)*, its sources joined with `; `. Collapsed in `whos-who-publish.py` only: the cache and `positions.csv` stay one row a source, because ids anchor there. Positions first grouped on case, accents, hyphens and spacing; the title rule below replaced that. 33,229 rows became 24,565. §1's "one row is one attestation" now reads "one row is one or more sources attesting the same thing in one year".
- **Same body, two tags.** `afcfta` folds into `afcfta-secretariat` by a `hand` row, as the ministry pairs did (§12); it joins the launch `[ACT]` note. Of the other name pairs where one is the other plus *Secretariat* or *Commission*, African Union and its Commission, and Public Service and its Commission, are different bodies and stay apart; the Commonwealth pair has 4 rows and waits for a sighting. *Wamkele Mene* and *Wamkele Keabetswe Mene* were one person behind a merge candidate (§13); a `same` ruling joined them. The contained-name join below now does this by rule.
- **Shorter names, and the contained-name join** *(Bill, 2026-11-20)*: §7 as amended. The join took 453 shorter names into fuller ones, 16,653 people from 17,105; 30 checked at random were all one person. Published rows fell to 24,176.
- **`lookups/naming-conventions.csv`**, one row a country, `basis` `draft`: name order (`given-first`, `family-first`, `either`, `patronymic`), whether official texts put the family name in capitals, the particles, a note. Its first use is the patronymic order rule; the particles wait for a use. Rows are corrected by hand as the index shows a case.
- **One title however written** *(Bill, 2026-11-20)*. `W.title_parts` reads a position as its titles after four folds: case, accents and punctuation; language and abbreviation through `lookups/position-glossary.csv` (*secrétaire général*, *DG*, *PCA*); words repeating the organisation, its initials or a country; word order. A person's positions at one organisation in one year are one row when any part matches, chained, so *DG* and *CEO* meet through *Director General and CEO*. Rank words survive every fold, so *Deputy Governor* is never *Governor*. The row shows an English form if any, then the fullest, then the shortest. 24,176 rows became 22,067; 45 merges checked at random were all one title. The contained-name join uses the same test (523 joined, 16,579 people). Four rows whose organisation was a person's tag (*Abdelmadjid Tebboune*) are dropped and counted.
- **`lookups/org-abbreviations.csv`** *(Bill, 2026-11-20)*: an organisation's abbreviations in any language (*AfDB*, *BAD*; *UEMOA*, *WAEMU*) and the full name it publishes under, which replaces a sources' scrap such as *La BEAC* or *GIZ Kenya*. `whos-who-orgs.py` folds a slug spelt as a listed abbreviation into its body, and two `other` slugs with one name into one when the list holds either or they share their one country; one name in two countries stays two (*Senate*). Governments keep the stem rule (§6). 56 slugs folded; the search finds a body by any abbreviation. Title matching now also reads a plural qualifier as its singular. 22,001 rows, 16,519 people. *Bank of the Republic of Burundi* was published as *World Bank*; a `hand` row in `entity-names.csv` corrects it.
- **Added on the way:** a correction or removal link under the results, the search kept in the fragment (`#q=`, `#country=`, `#org=`), and a row and source count over every result.
- **Launch, owed:** drop `ROBOTS` in `whos-who-publish.py`, add the nav item in `chrome_lib.py`, write the method section in `content/methodology.md` quoting `CAUTION`, add the change-log entry, and send the `[ACT]` note on the folded tags (§12). The two measurements left from §14 go with it.
