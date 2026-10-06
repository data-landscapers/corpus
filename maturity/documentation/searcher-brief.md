---
type: brief
reader: cc
title: searcher-brief.md — what one searcher does for one country of a maturity study
last_reviewed: 2026-10-06
status: first used for maturity study health, task H5
---

# Searcher brief: find what the study lacks

*(Method §5 as instructions. The parent stages what you select; you write decisions, never documents.)*

## What you are given

A study id `{id}` and a country `{ISO3}`, under `C:\CORPUS`.

1. Read `maturity/{id}/study.json` and the study file it names: the typology, the aspects, the ladders.
2. Read `maturity/{id}/evidence/{ISO3}/profile.csv`. **A row with text in `gap` is what you search for**; rows with a value are what is already held. Read `evidence.csv` beside it for the held facts.

## Search

**One Exa Agent run per sub-indicator that has a gap** (`agent_run`, `effort: "medium"`). Load the Exa tools with ToolSearch if they are not listed. In the query: name the country and the sub-indicator in plain words, list the gaps as questions, give the held facts in a line so they are not returned again, and ask for **at most eight documents, ranked**, each with URL, title, publisher, date and one line on which gap it answers. Ask in the country's working language as well as English. Ask for the study file's source types in its order, primary and official first, and for nothing dated before 2019 except a stated absence.

Do not search further by hand unless a run returns nothing. Leave out a return that is plainly another country's or not a document.

## Fetch

Write the leads to `maturity/{id}/search/{ISO3}/leads.json`:

```json
[{"url": "", "title": "", "publisher": "", "published": "", "sub_indicator": "", "why": ""}]
```

Then run, from `C:\CORPUS`: `python scripts/study-stage.py {id} fetch {ISO3}`. It screens out what is already held or rejected, fetches the rest once and writes `fetched.csv` beside the leads. The text of each fetched lead is at the `cache` path it prints. Run it once; do not add leads afterwards.

## Decide

Read each fetched text. Over 20,000 words, search it for the study's terms and the country's name and read around them. Then write `maturity/{id}/search/{ISO3}/decisions/{k}.json`, `k` being the lead's number in `fetched.csv`, **one file per fetched lead, as soon as it is read**:

```json
{"select": true, "sub_indicator": "", "aspect": "", "fact": "", "title": "", "publisher": "",
 "published": "", "date_source": "source", "why_not": ""}
```

**Select a document only when its text states a dated fact, on an aspect with a gap, that nothing held states.** One such fact is enough. A document about the right system that states no such fact is not selected. Nor is one about another country, an Exa summary, or a page that only links to the document.

- `aspect`: the gap aspects the text answers, joined by `;`.
- `fact`: the dated fact, in one sentence, as the text states it.
- `title`, `publisher`: the document's own, in its own language and spelling.
- `published`: **the document's own date** from its byline, imprint or metadata, as `YYYY-MM-DD`, `YYYY-MM` or `YYYY`. Never the date you fetched it. `date_source` is `source` where the document states it, `proxy` where you inferred it.
- `why_not`: where `select` is false, one line.

## Rules

**`C:\OSINT` and `C:\corpus-osint-xfer` are not yours to write to.** Write only `leads.json` and the `decisions` files, with the Write tool. Create, edit, move or delete nothing else. Start no agents. Do not run git, and run no script but the one above.

## When you finish

Reply in five lines at most: runs made, leads returned, fetched, selected, and anything the parent must know.
