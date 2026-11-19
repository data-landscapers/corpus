---
type: design-note
reader: cc
title: whos-who.md — a Who's Who index of officeholders, built in Corpus
last_reviewed: 2026-11-19
status: design for CC's operational review; nothing built
---

# Who's Who index

*(Written 2026-11-19 in Cowork from Bill's brief. The counts in §2 were measured against the mirror and this repo that morning; the extraction yield in §5 is a rough sample, not a measurement, and stage 1 exists to replace it. CC reviews this operationally before anything is built — §11 lists what the review should settle.)*

## 1. What it is, and the one rule

**A public index of who held which position in which organisation, in which year, with the source that says so.** One row is one attestation: a named source, published in a given year, states that a person held a position at an organisation.

**For legal reasons a published row carries five fields and no others** *(Bill, 2026-11-19)*: `name`, `year`, `position`, `organisation`, `source_url`. No biography, nationality, gender, age, photograph, summary or quotation. The rule is on the output; §3 extends it to everything this repo commits, because the repo is public.

**The build belongs in Corpus and asks nothing of OSINT.** OSINT collects and classifies; a Who's Who is a derived view. OSINT tags institutions and not officeholders, and holds no entity registry, so there is nothing over there to extend. The precedent is `build-entity-names.py`: the slugs are OSINT's, and how they are written is decided here.

## 2. What exists already

| Thing | Where | State |
|---|---|---|
| Sources | mirror `raw/` | about 46,600, each with `url`, `published`, `date_precision`, `places`, `entities` in frontmatter |
| Organisation display names | `lookups/entity-names.csv` | 10,935 slugs; basis `full` 9,529, `partial` 737, `acronym` 669; `hand` rows survive a rebuild |
| Organisation variants | `scripts/entity-variants.py` | groups split slugs by country suffix, French and English stems, and initialisms; rules nothing |
| Name extraction | `scripts/names_lib.py` | capitalised runs from prose, built for search recall; does not tell a person from an organisation |
| People | nowhere | no table, no ids, no deduping |

**The organisations half is mostly a matter of tightening what is here. The people half is new.**

## 3. The boundary this adds

**Everything committed to this repo about a person is one of the five fields or an opaque key.** The repo is public and its history is permanent, so a working file is as published as a page. Three consequences:

- **No evidence sentence is ever written to a tracked file.** The extractor reads the body, emits the fields and the source's path, and discards the text. A reviewer who wants the sentence re-reads the mirror.
- **No attribute is stored on a person.** Not a country, not a type, not a note. A person's place is derived at build time from the organisations of their positions and is never written down.
- **Scratch that holds bodies or sentences lives outside the repo**, as `osint-patch.py`'s clone does.

`scripts/lint-whos-who.py` (§8) holds the committed files to their declared columns.

## 4. The model

Three tables and two supports, all CSV. Lookups are hand-correctable and a deriver never overwrites a `hand` row.

**`lookups/organisations.csv`** — one row per organisation the index names. A sidecar keyed on OSINT's slug, so `entity-names.csv` and its four readers are untouched.

| column | holds |
|---|---|
| `slug` | OSINT entity slug |
| `canonical_slug` | the slug this one publishes under; itself unless two slugs are one body |
| `name` | published name; defaults to `entity-names.csv` → `display` |
| `place` | ISO-3 or `X__` code, from the dominant place of the sources tagging it |
| `kind` | `government` or `other` |
| `basis` | `auto` or `hand` |

**`lookups/org-lineage.csv`** — `slug`, `successor_slug`, `year`, `basis`. Government only (§6).

**`lookups/people.csv`** — `person_id`, `name`, `basis`. The id is opaque and issued once; it is never derived from the name, so a corrected spelling does not move it.

**`lookups/person-aliases.csv`** — `alias`, `person_id`, `basis`. Every written form of a name that resolves to a person. An alias is a name and nothing else.

**`lookups/person-rulings.csv`** — `person_id_a`, `person_id_b`, `ruling` (`same` or `different`), `ruled`. Hand rulings on candidate merges, so a question is asked once.

**`build/whos-who/positions.csv`** — the derived fact table: `person_id`, `slug`, `position`, `year`, `source_url`, `source_file`. Rebuilt whole; never edited by hand. A wrong row is fixed in a lookup or in the suppression list (§7), then rebuilt.

The published table is the join: `people.name`, `year`, `position`, `organisations.name` through `canonical_slug`, `source_url`.

## 5. Extraction

**A row needs a person, a position and an organisation in the same statement.** That is the scope test as well as the extraction rule: a private individual named in a story has no position at an organisation and cannot produce a row. Bylines are excluded by construction — the `Author:` line is stripped with the frontmatter.

**Two passes, because the corpus is large and the statement is small.**

1. **Candidate pass, deterministic.** Find sentences where a name-shaped run sits beside a role word (`Minister`, `Ministre`, `Director-General`, `Commissioner`, `Governor`, `Chief Executive`, `Chair`, `Permanent Secretary` and their French and Portuguese forms; the list is a lookup). In a rough sample of 3,000 files from `raw/2026`, 952 contained a role word at all, so expect candidates in something like a third of sources.
2. **Reading pass, by model, over the candidate sentence only.** Returns zero or more `(name, position, organisation-as-written)` triples, or nothing. It is told to return nothing where the sentence reports a former, acting-elsewhere, nominated or hypothetical holder unless the position text says so (`former Minister of…` is a different statement about a different year and is dropped in version one).

**The organisation is resolved against the source's own `entities:` tags first.** The tagged slugs are the short list; the organisation-as-written is matched to one of them through `entity-names.csv` and the variant rules. No match means the row is dropped and counted, not invented. This is what keeps the organisations table inside OSINT's vocabulary.

**`year` is the year the source attests, and claims nothing about a term of office.** It is the year of `published`, unless the sentence carries its own date. A source with `date_precision` coarser than a year yields no row. Two sources in two years are two rows; the index never infers a start, an end or the years between.

**`position` is the title as the source gives it, normalised only for case and whitespace.** A French title stays French. No controlled vocabulary of titles in version one.

**`source_url` is the source's `url` — the publisher's own page.**

## 6. Organisations, and why government is the special case

**For most organisations the existing display name is the canonical name**, and the work is the 737 `partial` rows that reach the index, corrected by hand as `hand` rows in `entity-names.csv`.

**A government department differs in three ways.**

- **The published name carries the country.** `angola-ministry-of-interior` displays as *Ministry of Interior*, which is one of dozens. Where `kind` is `government` and the name does not already contain its place, the published form is `{name}, {country}`. About 500 slugs contain `ministry`.
- **A ministry's name is true for a period.** Reshuffles rename, merge and split portfolios. **Each named incarnation keeps its own row and its own slug**, because a 2019 attestation should publish under the 2019 name, and `org-lineage.csv` links an incarnation to its successor. Nothing is collapsed. Lineage is filled by hand where a reader would otherwise be misled, and is not a completeness target.
- **One body, two languages.** `ministere-justice-djibouti` and an English slug for the same ministry are one organisation; `entity-variants.py` already finds these. A confirmed pair sets `canonical_slug` here and is sent to OSINT as an `[ACT]` note so the tags converge; the index does not wait for that.

**The government itself is not a position-holding organisation.** A row resolving only to `government-of-{country}` is kept for heads of state and government and dropped otherwise, since *Minister, Government of Ghana* tells a reader nothing the ministry row would not.

## 7. People: deduping, and removal

**A wrong merge credits one person with another's office, which is the worst error this index can make. A missed merge shows one person twice, which is mild.** Every rule resolves towards keeping people apart.

**Normalisation, for comparison only** — the published name is never the normalised one. Strip honorifics and post-nominals (`Dr`, `Hon.`, `Eng.`, `Prof`, `S.E.`, `MP`), fold case, accents and punctuation, and treat token order as free, because the corpus writes family names first and last.

**Merge automatically only when** the normalised names match in full **and** the two attestations share an organisation (by `canonical_slug` or lineage) or a country. Same name in two countries stays two people. An initial against a full given name (`A. Mensah`, `Ama Mensah`) is never merged automatically, even inside one ministry.

**Everything else that looks alike is a candidate, written to `build/whos-who/merge-candidates.csv` and left separate** until a row in `person-rulings.csv` settles it. The file is a report, not a queue anything must drain; unresolved candidates are the correct resting state.

**The canonical name is the fullest form the sources give, most frequent first on a tie**, and a `hand` row overrides it.

**Removal is one row.** `lookups/whos-who-suppress.csv` holds `person_id` or a `(person_id, slug)` pair with the date; the build drops matching rows before anything is written to `outputs/`. It carries no reason column — a reason is a statement about a person.

## 8. Publication

- **Page:** `/whos-who/`, one table on the shared datatable, columns as the five fields, filter by organisation and country (country derived from the organisation, shown as part of its name). No per-person page in version one, so no person URL becomes a permanent identifier.
- **Download:** see §10 decision 1. This note assumes an **undated, current-only CSV**, on the catalogue's precedent.
- **Output:** `outputs/whos-who/whos-who.csv`, exactly five columns.
- **Method page:** a section under `/methodology/` saying what a row is and is not — an attestation in a year, not a term — and how to ask for a correction or removal.
- **Change log:** one entry at launch.

**Lints, all in `scripts/lint-whos-who.py`, failing the build:**

1. `outputs/whos-who/*.csv` has exactly the five columns, in order.
2. Each tracked lookup has exactly its declared columns from §4.
3. Every `source_url` is a catalogue URL; every `slug` exists in `entity-names.csv`.
4. No suppressed person or pair appears in `outputs/`.
5. No published name appears under two `person_id`s within one organisation — the visible symptom of a missed safe merge.

`lint-interface.py` should need no exception: the build reads `raw/` and `lookups/` and nothing of OSINT's process material.

## 9. Build stages

Each fits a session and has a finish line.

1. **Pilot, one country.** Both extraction passes over one well-covered country, into scratch. *Finish:* a hand check of 200 rows giving precision for person, position and organisation separately, and the drop counts. This decides whether the reading pass is needed everywhere or patterns suffice for some sources.
2. **Organisations sidecar.** `organisations.csv` built for every slug the pilot reached; government naming rule applied. *Finish:* no published government name ambiguous across countries.
3. **People.** Ids, aliases, the merge rule, the candidates report. *Finish:* lint 5 clean on the pilot country; a sample of 100 automatic merges checked by hand with none wrong.
4. **Full run and incremental.** Whole corpus once, then only sources new since the last run, as a stage in `rebuild.py` after 2c. *Finish:* a nightly run adds rows without reissuing an id.
5. **Publish.** Page, download, method section, lints in the render gate, change-log entry. Not before Bill has ruled on §10.

## 10. Decisions that are Bill's

Both are about what is public and hard to take back.

1. **Is the download a dated edition?** `design.md` §9 says a published file is never revised and a taken URL resolves for ever. A removal request cannot be honoured against that. **Recommended: no editions — one undated current file, as the catalogue has**, so a removal is complete at the next build. Git history of `outputs/` would still hold the old row; whether that matters is part of the same legal question.
2. **Does the five-field limit bind the repo's lookups as designed in §4?** They add opaque ids, aliases (names) and rulings (pairs of ids) to the five fields. If that is too much, the people tables move outside the repo and only `outputs/` is committed.

## 11. What CC's review should settle

- Whether the reading pass runs as agents inside the nightly cycle or as its own job, and what a full first run costs.
- Whether `organisations.csv` as a sidecar is right, or `entity-names.csv` should grow the columns.
- Where scratch lives, and whether `build/whos-who/` is tracked or ignored — `positions.csv` holds only fields and keys, but nothing requires it in history.
- How ids stay stable when the mirror re-files a source or OSINT merges two slugs.
- Whether stage 1's country should be one with heavy French-language coverage, since that is where name order and ministry naming are hardest.
