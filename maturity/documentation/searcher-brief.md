---
type: brief
reader: cc
title: searcher-brief.md — what one searcher does for one country of a maturity study
last_reviewed: 2026-10-19
status: first used for maturity study health, task H5
---

# Searcher brief: search one country afresh

*(Method §5. You write decisions, never documents.)*

## What you are given

A study id `{id}` and a country `{ISO3}`, under `C:\CORPUS`.

1. Read `maturity/{id}/study.json` and the study file it names: the typology, the aspects, the ladders.
2. **Every question of the ladder is searched, whatever is held** *(Bill, 2026-10-19)*: what `maturity/{id}/evidence/{ISO3}/` holds does not narrow the search.
3. **A sub-indicator named by the parent** is the only one searched.

## Search

**Standard Exa searches, never an Agent run** *(Bill, 2026-10-19)*: `web_search_exa`, one search per question of the ladder, in English and again in the country's working language (load the tools with ToolSearch if unlisted). Each query describes the document wanted: the country, the sub-indicator in plain words and what a yes would be, primary and official sources first.

Keep **at most eight documents, ranked**, newest first, each with URL, title, publisher, date and one line on which question it answers. Nothing dated before 2019 except a stated absence. Leave out a return that is plainly another country's or not a document.

## Fetch

Write the leads to `maturity/{id}/search/{ISO3}/leads.json`:

```json
[{"url": "", "title": "", "publisher": "", "published": "", "sub_indicator": "", "why": ""}]
```

Then run, from `C:\CORPUS`: `python scripts/study-stage.py {id} fetch {ISO3}`. It skips held or rejected URLs, fetches the rest once and writes `fetched.csv`, each text at its `cache` path. Run it once; add no leads afterwards.

## Decide

Read each fetched text. Over 20,000 words, search it for the study's terms and the country's name and read around them. Then write `maturity/{id}/search/{ISO3}/decisions/{k}.json`, `k` being the lead's number in `fetched.csv`, **one file per fetched lead, as soon as it is read**:

```json
{"select": true, "sub_indicator": "", "aspect": "", "fact": "", "title": "", "publisher": "",
 "published": "", "date_source": "source", "why_not": ""}
```

**Select a document when its text states a dated fact on one of the sub-indicator's aspects**; one is enough. Not one that states no such fact, is about another country, is an Exa summary, or only links to the document.

- `aspect`: the aspects the text answers, joined by `;`.
- `fact`: the dated fact, in one sentence, as the text states it.
- `title`, `publisher`: the document's own, in its own language and spelling.
- `published`: **the document's own date** from its byline, imprint or metadata, as `YYYY-MM-DD`, `YYYY-MM` or `YYYY`. Never the date you fetched it, a file stamp, a date in the URL or folder, the date of the event or meeting it reports, or the end of the financial year it covers. **Give only the precision the imprint gives**: a year is `YYYY`, never padded to `-01-01`. `date_source` is `source` where the document states it, `proxy` where you inferred it.
- `why_not`: where `select` is false, one line.

## Screen

**Ingest drops a quarter to a half of what studies select** *(R139)*, under the drop table in `scripts/.workroot/wiki/intake.md`. Do not select a document that is:

- `already-held`: the story is in `evidence.csv` already, from another address or outlet;
- `no-development`: a digest, PR, vendor thought-leadership, or a second-hand summary such as a law tracker or aggregator;
- `headline-only-stub`: the text adds nothing to its headline;
- `off-topic`, or `inadmissible-origin` under `scripts/.workroot/wiki/origin-screen.md`, including a page that says it was machine-written.

Start `why_not` with the code: `no-development: an awards press release`.

## Rules

**`C:\OSINT` and `C:\corpus-osint-xfer` are not yours to write to.** Write only `leads.json` and the `decisions` files, with the Write tool, and touch nothing else. Start no agents. Do not run git, and run no script but the one above.

**You run unattended.** Never ask or wait: where unsure, take the conservative option and say so.

## When you finish

Reply in five lines at most: runs, leads, fetched, selected, and anything else the parent needs.
