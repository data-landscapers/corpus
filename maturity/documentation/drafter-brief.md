---
type: brief
reader: cc
title: drafter-brief.md — what one drafter does with one slice of a maturity study's reading list
last_reviewed: 2026-10-06
status: first used for maturity study health, task H3
---

# Drafter brief: read a slice, write its facts

*(Method §4 as instructions. The parent merges and checks what you write.)*

## What you are given

A study id `{id}`, a country `{ISO3}` and a slice number, under `C:\CORPUS`.

1. Read `maturity/{id}/study.json`: the sub-indicators, the classes, and each aspect's closed list of values.
2. Read the study file it names, in `maturity/{id}/`: the typology, the aspects and the ladders. The typology decides the class of every system you meet.
3. Open `maturity/{id}/evidence/{ISO3}/readlist.csv`. Your documents are the rows whose `slice` is yours. Rows with `kind` of `status` are the country's status report on the subject: read those sections first as orientation, and take no fact from them.

## Reading

**Read every document in your slice, in order of `n`, whole.** Where `read` is `whole`, the file is `C:\OSINT\` followed by `path`. Where `read` is `passages`, the file is `C:\CORPUS\` followed by `path`, and holds the passages of a long document; read all of it. A file longer than one read takes several: continue until its end.

**`C:\OSINT` is read-only. Never write, move or delete anything there.**

## What a fact is

**A fact is one thing the document states about one aspect of one sub-indicator, in this country.** One row each. Record only what this document itself states; do not carry anything over from another document, the status report or what you know.

- `sub_indicator` and `aspect`: keys from `study.json`.
- `value`: from that aspect's closed list, exactly as spelt. A facet aspect takes one `facet:value`; a `multi` aspect takes its values joined by `;`.
- `fact`: one sentence, in English, giving what the document states with its figures: numerator, denominator and who says so, where it gives them. No quotation of more than a few words.
- `as_of`: when the stated thing was true, as `YYYY`, `YYYY-MM` or `YYYY-MM-DD`. **The event's date, not the document's.** Where the document gives none, use its `published` date and say so in `fact`.
- `date_precision`: `year`, `month` or `day`.
- `system`: the system's name as the document gives it.
- `class`: the class the typology gives the system. **A fact is recorded only for a system of the sub-indicator's own class.** A system of any other class is a `systems` entry and gives no fact.

**Classify the deployment by what the document says it does, never by its product name.** A system named with no description of what it does is a `systems` entry with an empty `class`.

**A dated statement that something is absent is a fact**: reporting on paper end to end, a system withdrawn. So is a dated event in the last twelve months: a rollout, an outage, a funding cut.

**Do not stage, summarise or judge.**

## What you write

**One file per document, written as soon as that document is read**, before opening the next: `maturity/{id}/evidence/{ISO3}/facts/{n}.json`, `n` being the document's number in the list.

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

`systems` takes every health information system the document names for this country, of any class: `country_label` is what the country calls it, `platform` the software, `owner` who runs it, `tiers` where it is used as the document states it. A document that states nothing usable still gets its file, with empty lists and the `note`.

**Write with the Write tool, one file at a time. Create no other file, edit none, delete none, and start no agent of your own.**

## When you finish

Reply in five lines at most: documents read, facts written, systems named, and anything the parent must know, such as a file that would not open.
