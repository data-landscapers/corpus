---
type: design-note
reader: cc
title: external-datasets.md — global databases as claims, not scores
last_reviewed: 2026-11-10
status: built for aftech and gtmi; maturity pass not yet built
---

# External datasets

*(Bill, 2026-11-10: import Carnegie's Africa Technology Policy Tracker, then the World Bank's GTMI and the other global databases, by one method.)*

## 1. What is kept

**The evidence behind a database, not its score** *(Bill)*. A score is someone else's judgement on someone else's ladder. What we can use is what they recorded to reach it: that a law exists and its name, when a system launched, a link to the strategy. GTMI's file holds every country's survey answers for 2020, 2022 and 2025. Carnegie's is a list of laws, policies and regulations, each with a link.

Both come down to the same thing, a **claim**: one statement about one country, with its evidence. `scripts/external-claims.py` turns each source into the same table, with one adapter per source:

| Column | What it holds |
|---|---|
| `source`, `edition` | The `lookups/external-sources.csv` id and the fetch date the edition was filed under |
| `survey_year` | GTMI's round (2020, 2022, 2025); blank for a register |
| `iso3`, `item`, `question` | The country, the source's own question id (or Carnegie's tags) and its wording |
| `status`, `name`, `year` | The coded answer decoded (`2 Yes (Effective)`) or Carnegie's law/policy/regulation; the system's or instrument's name; the year given |
| `url`, `documents` | A link to a system (portal, home page); links to documents, space-separated |
| `basis` | `self-reported` (a government answered GTMI's survey), `publisher-assessed` (the World Bank filled it in remotely) or `publisher-compiled` (Carnegie) |
| `studies`, `fit` | The maturity studies the question maps to, and how well |

**Scores are not converted.** GTMI's composite scores and the five indices it carries from the UN and ITU are formulas in the workbook. A score we want goes through `reference/measures.csv` like any other.

## 2. Files

- `lookups/external-sources.csv`: the register, one row per database. It holds the download URL, the shape, the publisher's release date, the refresh cadence and the licence position. A new edition is a new `download_url`.
- `reference/external/{source}/{edition}/`: `original.xlsx` as fetched and never rewritten, plus its `sha256`, `release`, `claims.csv` and `staging.csv`. `fetch` writes nothing if the bytes are unchanged.
- `reference/external/claims.csv`: every source's latest edition together, which is what a study reads.
- `lookups/external-items.csv`: question to study, with `fit` and `note`.

## 3. Mapping keeps an open mind

**Their indicator may be better conceived than ours** *(Bill)*. So the mapping does not just translate. Each row says how well the question fits:

- `same`
- `partial`
- `theirs-broader`
- `theirs-narrower`
- `none`, for a question with no study of ours

The `note` says what differs. Read together, those rows are the case for changing our framework. They are reported to Bill as a comparison and are never acted on silently.

The first reading, on 2026-11-10, found three patterns:

- **GTMI tests delivery where we test intent.** Examples: a shared cloud that is operating, not a cloud strategy (I-1); an open-data portal, not a policy (I-29); a data-governance institution, not a policy (I-34).
- **GTMI asks about enforcement where we stop at enactment.** Examples: access to information (I-37.4) and a data-protection enforcement rating (I-38.5.1).
- **Two families have no indicator of ours.**
  - Core public-finance and civil-service systems: FMIS, treasury single account, HRMIS, payroll, debt and public investment management, e-procurement.
  - Telecom sector regulation: spectrum, licensing, quality of service. Most of the 161 of Carnegie's 595 rows that map to no study are this.

## 4. Citing

**Cite the primary wherever one exists; the database only for what nothing else states, and say whose statement it is** *(Bill, 2026-11-10)*. `lint-study.py` holds every evidence row to a record held in raw/. So:

- **Primaries are acquired.** `stage` sends a claim's document links that are not already held to `new-queue/dataset-external-{source}-NN/`, 40 to a batch, in `status-stage.py`'s file format. Portal and home-page links are not sent: they show a system exists and stay as claims. A link is held when OSINT's URL index or the catalogue (same title, same country) has it. A document is staged only when a date can be read from its path or the source's year. `staging.csv` records each link's outcome, so a rerun fetches only what is new.
- **The database itself is one raw record per edition**, its African rows rendered by country. This is the fallback a claim cites when it has no primary. The prose names the basis: "the government told the World Bank's GovTech survey…", or "Carnegie's tracker lists…".

## 5. Not yet built

**The maturity pass.** Claims reach a study as evidence through a drafter reading them beside the held primary, under the citing rule above. It waits on the primaries landing, and on `study-update.py` → `HELD`. Registered as a CORPUS housekeeping job.

**More sources.** These include UNCTAD's cyberlaw tracker, the ITU ICT regulatory tracker, the UN e-government survey's country data and the IIAG's indicator data. Each needs one adapter, one register row and a block of mappings.
