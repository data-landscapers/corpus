---
type: design-note
reader: cc
title: external-datasets.md — global databases as claims, not scores
last_reviewed: 2026-11-10
status: built for aftech, gtmi, unctad, odin, itu, spi and wdi; maturity pass not yet built
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

**Index values are skipped, unless real data sits behind them** *(Bill, 2026-11-10)*. Kept: an answer in words, a named system or law, a year, a link, an observed yes or no, and ODIN's element scores, each of which records one observed fact about a data category. Dropped:
- GTMI's composites, and the five UN and ITU indices it carries;
- the points ITU gives each answer;
- SPI's own composites (only the codes the lookup maps are kept);
- the UN e-government indices. With those gone, the UN E-Government Survey left only portal URLs and a few questionnaires, so it was dropped the same day.

A figure we want goes through `reference/measures.csv` like any other.

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
- **First run, 2026-11-10.**
  - Carnegie: 238 staged, 41 held, 41 too thin, 247 unfetchable.
  - GTMI: 499 staged, 75 held, 12 undated, 77 thin, 369 unfetchable, plus 23 listings or error pages.
  - UNCTAD's Global Cyberlaw Tracker (added the same day): 303 claims, one per law or per area with none. 72 staged, 26 held, 10 already staged by another source, 72 unfetchable, 6 thin. Its status is in `data.csv` and its laws in `document_links.json`, both on `storage.unctad.org`; unctad.org itself refuses scripted fetches.
  - ODIN (Open Data Watch's Open Data Inventory, the same day): no file, so `fetch_odin` reads the site's own API, one profile per country and round (2016-2024, 324 calls, about 15 minutes), and keeps the parts a claim is made from as one gzip. 6,393 claims, one per country, round and data category. Each carries the ten element scores (`-1` is ODIN's "not scored"), the series found, the latest year of data and where the assessor found it. Its `shape` is `index`: the links are statistics offices' data tables, so none is staged, only the latest round's record. It maps every category to `opendatapolicy` as `theirs-broader`, since ODIN tests what is published openly and ours asks for a policy.
  - ITU's ICT Regulatory Tracker (the same day): its site, `app.gen5.digital`, reads ITU's metrics API, which `fetch_itu` calls once per country and year, 2007-2024 (864 calls). That gives 42,017 claims: the 50 answers in words, in four pillars (regulator, mandates, regime, competition). Only a few map: the broadband plan, the consultation duty, the telecom consumer mandate, international-gateway competition and foreign-ownership limits (to `digitalsovereignty`). The rest is the telecom-regulation layer we have no indicator for, the same gap as Carnegie's unmapped rows. Licence CC BY-NC-SA 4.0, as the tracker states.
  - World Bank SPI (the same day), from its GitHub repository: 11,206 claims, the factual indicator values for 2004-2024. SPI mostly compiles other databases (the UN SDG statistics indicators, ODIN, the IMF). Its own work, the census years (Kenya "1999, 2009, 2019"), rides on the census claims. Mapped: censuses and surveys, CRVS completeness, the statistics law's UN compliance, the statistics plan's funding (`theirs-broader`: ours stops at the plan) and the microdata catalogue.
  - World Bank WDI (the same day), from the World Bank API rather than the `datasets/` GitHub scrape of it, which is stale. 1,548 claims from 21 series and 12 country facts, listed in `lookups/external-items.csv`, from which the fetch reads its selection. The facts include the latest census and survey and the IMF dissemination standard. Infrastructure: mobile, fixed broadband and fixed-line subscriptions, secure servers, urban and total electricity access, grid losses, consumption, renewable share and firms' outages. WDI carries no network coverage, and its bandwidth series ended in 2011.
    - **Values from 2024 on, unless one is a baseline** *(Bill, 2026-11-10)*. Where a country has none from 2024 on, its latest earlier value stays, and the fetch keeps 2010 on so the cut-off can move. Its `shape` is `series`: the record is each country's latest value of each item.
    - Not selected: the series a measure already reads (internet use and its sex split, rural electricity, account ownership, ICT service exports, GDP, population, GNI), which go through `reference/measures.csv`. Also left out: indices such as CPIA, SPI and liner connectivity, and Doing Business, discontinued in 2021.
  - A register's year is the instrument's own and dates it first; an upload path or a PDF's metadata dated Ghana's 2008 Act 2026. Carnegie's batches went out before this rule, so 91 of them carry their path date, marked `proxy`.
  - A GTMI year answer dates the system, never a page: a treasury's founding year once dated its 2025 newsletter 1990. A GTMI document is dated by its path or its own metadata; a Carnegie row's year is the instrument's own.
  - Most unfetchable links are 404s with no Wayback capture. They stay as claims. `stage --retry` fetches the transient failures again.
  - Titles: GTMI gives no document titles, so `best_title` builds one from the page title, the file name, the body's first line or the claim's name, skipping letterheads.
- **The database itself is one raw record per edition**, its African rows rendered by country. This is the fallback a claim cites when it has no primary. The prose names the basis: "the government told the World Bank's GovTech survey…", or "Carnegie's tracker lists…".

## 5. Not yet built

**The maturity pass.** Claims reach a study as evidence through a drafter reading them beside the held primary, under the citing rule above. It waits on the primaries landing, and on `study-update.py` → `HELD`. Registered as a CORPUS housekeeping job.

**More sources.** Each source needs one adapter, one register row and a block of mappings.
