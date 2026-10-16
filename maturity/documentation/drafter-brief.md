---
type: brief
reader: cc
title: drafter-brief.md — what one drafter does with one call of a maturity study's reading list
last_reviewed: 2026-10-14
status: first used for maturity study health, task H3
---

# Drafter brief: read one call, write its facts

## What you are given

A study id `{id}` under `C:\CORPUS`, and either a country `{ISO3}` with the `n` of each of its documents, or regional stories (below). Sometimes also aspects: record only those.

1. Read `maturity/{id}/study.json`: the sub-indicators, the classes, and each aspect's closed list of values.
2. Read the study file it names, in `maturity/{id}/`: the typology, the aspects and the ladders.
3. Open `maturity/{id}/evidence/{ISO3}/readlist.csv`. Your documents are the rows your call names. A `status` row is orientation only; no fact is taken from it.

## Reading

**Read your documents and no others. Open them all in one turn.** Where `read` is `whole`, the file is `C:\OSINT\` followed by `path`. Where it is `passages`, the file is `C:\CORPUS\` followed by `path`. Read every file to its end, in several reads if need be.

**`C:\OSINT` is read-only. Never write, move or delete anything there.**

## What a fact is

**A fact is one thing the document states about one aspect of one sub-indicator, in this country.** Record only what this document itself states: nothing from another document, the status report or what you know.

- `sub_indicator` and `aspect`: keys from `study.json`.
- `value`: from that aspect's closed list, exactly as spelt. A facet aspect takes one `facet:value`; a `multi` aspect takes its values joined by `;`.
- `fact`: one sentence, in English, giving what the document states with its figures: numerator, denominator and who says so, where it gives them. No quotation of more than a few words.
- `as_of`: when the stated thing was true, as `YYYY`, `YYYY-MM` or `YYYY-MM-DD`. **The event's date, not the document's.** Where it gives none, use its `published` date and say so.
- `date_precision`: `year`, `month` or `day`.
- `system`: the system's name as the document gives it.
- `class`: the class the typology gives the system. **A fact is recorded only for a system of the sub-indicator's own class.** A system of any other class is a `systems` entry and gives no fact.

**Classify the deployment by what the document says it does, never by its product name.** A system named with no description of what it does is a `systems` entry with an empty `class`.

**A dated statement that something is absent is a fact**, such as a system withdrawn; so is a dated event in the last twelve months, and a dated report that a strategy was adopted, launched or lapsed.

**Do not stage, summarise or judge.**

## What you write

**One file per document, all written in one turn**: `maturity/{id}/evidence/{ISO3}/facts/{n}.json`, `n` being the document's number in the list.

```json
{
  "slug": "the slug column of the row, copied exactly",
  "facts": [
    {"sub_indicator": "", "aspect": "", "value": "", "fact": "", "as_of": "",
     "date_precision": "", "system": "", "class": ""}
  ],
  "systems": [
    {"system": "", "country_label": "", "class": "", "platform": "", "owner": "", "tiers": ""}
  ],
  "note": "one line: why there is no fact, where there is none"
}
```

`systems` takes every system in the study's field the document names for this country, of any class. A document that states nothing usable still gets its file, with empty lists and the `note`.

**Write with the Write tool. Create no other file, edit none, delete none, and start no agent of your own.**

## A regional call

**A regional call names stories, each with the countries it is listed for.** Read each once, from `C:\OSINT\` followed by its `path`, and answer for every country listed, from what the story states about that country by name. Write one file per story, `maturity/{id}/regional/{key}.json`:

```json
{"slug": "the story's slug", "countries": {"KEN": {"facts": [], "systems": [], "note": ""}}}
```

Each listed country gets an entry, shaped as a country file's lists and `note`.

## A shared call

**A shared call** (`first-pass-batch.md`) is a regional call over several studies. Answer each study from its aspects, into `maturity/_batch/shared/{key}.json`: `{"slug", "studies": {id: {"countries": {ISO3: {...}}}}}`.

## When you finish

Reply in three lines at most: documents read, facts written, anything the parent needs.
