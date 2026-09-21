---
type: design-note
title: datasets.md — the Datasets section, starting with Data Centres
last_reviewed: 2026-09-21
status: plan; not yet built
---

# Datasets

*(Written 2026-09-21 from Bill's fourteen-point brief. Where this departs from the brief it says so and gives the reason. The tasks at the end are the build order.)*

## 1. What it is

A new top-level nav item, **Datasets**, between Finance and Catalogue in `scripts/chrome_lib.py` → `NAV`. `/datasets/` lists the datasets. Each one gets a page with a table (the shared `datatable.js`), a dated CSV download, the metadata and a list of recent changes. **Data Centres** comes first, taken over from the main site's v2 post (`data-landscapers.io/lab/2026/06/10/africa-data-centres-v2/`).

**Corpus owns the dataset, and it is maintained, never rebuilt**, the same way a unit's ledger is. The master moves out of the gitignored `prep/` into `outputs/datasets/data-centres/`:

| File | What it holds |
|---|---|
| `data-centres.csv` | The master: one row per facility. |
| `metadata.csv` | The schema. It moves from `lookups/` because it describes this dataset and nothing else, and it is rewritten (T1). Published as `site/metadata/data-centres-metadata.csv` and shown at `/datasets/metadata/`, the one page holding every dataset's field dictionary (Bill, 2026-09-21; drawn from `content/datasets-metadata.md`). |
| `url-audit.csv` | One row per (facility, URL): the HTTP result, the final URL, the catalogue slug if there is one, the fields the URL supports, and the date checked. The validation passes resume from this file. |
| `considered.txt` | Every raw slug already read for this dataset. Works like `reports/{unit}/considered.txt`: a set difference, so a slug is never read twice. |

**The change log stays at `logs/dataset-updates.csv`**, as briefed, with the newest row first. Two changes to the brief: the column is named `action`, which takes `add`, `modify` or `retire` (and `import` for the one-off baseline row), and there is a sixth column, **`sources`**. A change with no source cannot be defended. Every change is logged, including those from the validation passes.

## 2. Changes to the brief

- **Publish first, then validate.** The v2 data is already public, so republishing it unchanged as Corpus's first edition carries no risk, and it gets the page live now instead of after a long validation. Each validation pass that changes the data then produces a new edition. This reverses the brief's order (step 5).
- **Validation 3 and step 10 become one pass, and that pass is the BUILD step (step 12) run over the backlog.** All three read raw/ and decide, per record, whether it changes an existing row, adds a facility or changes nothing. The only difference between them is which records they read. BUILD's step is built once: the first run reads all ~2,000 candidate records, and later runs read only what has arrived since.
- **The trigger is wider than `infra.store`.** 1,444 raw records carry `infra.store`, but data-centre news also arrives under `geopol.*`, `fin.*` and energy tags. A record is a candidate if it carries `infra.store` **or** its title or `hub_line` matches `data cent(re|er)|colocation|hyperscale|tier (III|IV)`.
- **Validation 1 splits in two.** A script checks all 1,316 URLs for existence: status, redirects and soft-404s. It costs nothing, and no model reads anything at this stage. The model's evidence check, "does this URL support what the row says?", then runs per country on the live URLs only. A dead URL does not delete a fact: the row keeps the fact, the audit records the death, and the Wayback Machine is tried before anything else.
- **Validation 4 (Exa) is targeted, not run on every row.** Running Exa on all 306 rows would use a large share of the week's quota and mostly confirm what the row already says. Exa runs only on:
  - the 38 low- or medium-confidence rows;
  - the 45 Planned or Under construction rows, whose status is the likeliest to have changed;
  - rows left with fewer than two live sources after V1;
  - the countries with no rows at all (next point).
- **Coverage gap: North Africa has no rows.** Egypt, Morocco, Algeria, Tunisia and Libya are in the remit (`lookups/countries.csv`, XNA), and so are Eritrea, São Tomé and Guinea-Bissau. None of the eight has a single row. Egypt and Morocco are major markets, so this is the biggest gap in the dataset, bigger than anything validation will find. They get a sourcing pass of their own (T8).
- **Every source a change rests on reaches the catalogue.** URLs that V1 finds live and Exa-found sources both go through V2's route into `new-queue/`, so the page can cite catalogue records.
- **Lane.** A `new-queue/` folder takes the backfill lane only if its name starts `status-acquire-` or `progress-filler-`. Any other name is priced as news, and ~1,000 URLs at news price is the wrong cost. Batches are named `dataset-data-centres-{ISO3}` and staged **without `READY`**, and an `[ACT]` note asks OSINT to add `dataset-` to the backfill whitelist. Staging happens now; READY is written once OSINT confirms. Batches stay under 200 items, the same cap as filler.

## 3. Tasks

Each task is one commit (or a few), and each one is resumable from the files in §1.

| # | Task | Output |
|---|---|---|
| **T1** | **Done 2026-09-21.** The metadata was rewritten by `scripts/datasets-metadata-dc.py` into `outputs/datasets/data-centres/metadata.csv`: 57 fields, each with a label, a type, its allowed values, the rule it is derived by where it is derived, and a `v2_name` giving its column in the v2 header. Snake_case throughout; `Microsoft`/`AWS`/`Google` become `hyperscaler_*`; `raw_slugs` and `last_verified` are new. Two columns are dropped because neither held information of its own: `ownership chain` equalled `ultimate_parent_company` in all 306 rows, and `chinese_role` was a lossy copy of `chinese_involvement`. | metadata.csv |
| **T2** | **Done 2026-09-21.** `scripts/datasets-import-dc.py` took the v2 file into `outputs/datasets/data-centres/data-centres.csv` (306 rows, 57 columns). The header was migrated through `v2_name`, and the values were normalised to `metadata.csv` in form only; the import row in `logs/dataset-updates.csv` counts each normalisation. Two fixes went further than the plan: **garbled accents were repaired in 70 cells** (`PÃºblica` → `Pública`; the same repair ran on `prep/`, with a `.pre-mojibake` backup kept), and **`source_urls` now lists all 1,316 URLs the row cites**, up from 648. The other 668 were cited only inside other cells, mostly comments and shareholders. `scripts/datasets_lib.py` holds read, write, `check()` against the metadata, `next_id()` and `log()`. `lint-mojibake.py` now treats `outputs/datasets/` as input. **Left for T6**, because each needs a source read to fix: 24 rows whose `hyperscaler_relationships` says *None* but which carry a `Yes` flag; 63 Operational rows with no `year_operational`; 17 rows with no `ultimate_parent_hq_country`. | master, lib, log |
| **T3** | **Built 2026-09-21; goes live on the next RENDER**, which bakes the nav into every page (`scripts/datasets.py`, RENDER Step 6). No map yet: it waits until T8 fills North Africa, because a map with an empty north misleads more than a table does. **Publish (edition 1, v2 unchanged).** Add the Datasets nav item; write `scripts/datasets.py` (a new RENDER step beside Step 6, so 6a/6b prune and sync the editions), the `/datasets/` index (Data Centres, plus links to the Finance and Catalogue downloads so the index does not have one entry), and `/datasets/data-centres/`: a table from a display-column CSV, the full dated CSV, the metadata CSV, a map if cheap (the data has `gps_coordinates`), a list of recent changes from the log, and `structured_data.dataset()`. Add `content/datasets.md` for the copy, an entry in `content/changelog.md`, and a methodology section. | live pages |
| **T4** | **Done 2026-09-21.** `scripts/dataset-urls.py` checked all 1,316 URLs (2,668 citations) into `url-audit.csv`: live 1,091, thin 61 (mostly LinkedIn and YouTube), blocked 54 (Bloomberg, Reuters, Simply Wall St: bot walls, not dead pages), dead 76, error 32, soft-404 2. The Wayback Machine holds a readable capture for 67 of the 110 that failed; 35 have none, and 5 went unanswered and will be asked again on the next `--wayback` run. Text for 1,170 URLs is cached in `prep/dc-url-cache/` for T5 and T6, so nothing is fetched twice. Only one row is left with fewer than two readable sources. **Fixed on the way:** the T2 import had cut six URLs short at a closing bracket (Wikipedia's `Unitel_(Angola)`); they are repaired in the master and in the log. Wayback answers 429 to parallel requests, so its lookups run one at a time with backoff. | `url-audit.csv` |
| **T5** | **V2: catalogue match and staging (script).** Look up each live URL in OSINT `lookups/raw-url-index.csv` using the normalisation `status-stage.py` already uses. Write the slug into `raw_slugs` on a match. On a miss, fetch the page and stage it in `status-stage.py`'s item format under `new-queue/dataset-data-centres-{ISO3}/`, passed through `lint-staged-queue.py`. Write `READY` only after OSINT's lane note (T5a) is answered. **T5a**: an `[ACT]` note to OSINT asking it to add the `dataset-` prefix to the backfill lane. The loose CTN edge data-centre item Bill dropped at the root is pulled as it stands (notes-for-osint 155). | slugs, staged batches, note |
| **T6** | **V1b: evidence check (model, one country per sitting, largest last).** For each live URL, fill in the fields it supports. Where a row claims something no URL supports, source it, soften it or clear it, and log the change. | `url-audit.csv`, edits, log rows |
| **T7** | **The BUILD dataset stage, then run it over the backlog** (V3 and step 10). Add a stage to `BUILD.md` after stage 4: `scripts/dataset-scan.py --slugs data-centres` lists the candidates not yet considered (§2's trigger). For each candidate the model modifies a row, adds a facility or does nothing, logs every change at the top of `dataset-updates.csv`, and marks the slug considered. The first run is the ~2,000-record backlog, taken one country at a time; after that it is part of the normal build. | BUILD stage, edits, log |
| **T8** | **Coverage: the eight countries with no rows** (EGY, MAR, DZA, TUN, LBY, ERI, STP, GNB). T7 covers what raw/ already holds for them. On top of that, one Exa brief per country: operational, planned and under construction facilities, with their operators. The sources go through T5's route. | new rows |
| **T9** | **V4: targeted Exa** on the rows §2 lists. Anything Exa finds is staged through T5, and changes are logged. | edits, log |
| **T10** | **Hand over from the main site.** The v2 post gets a line pointing to the live dataset on Corpus. That post is in `data-landscapers`, so the change is a one-line edit there, made upstream.  **Then empty `data-centres-status` in `content/datasets.md`**: the *still being finalised* notice on both pages goes, and a change-log entry says the dataset is complete. | link, notice off |

**Editions follow automatically:** each render after T6–T9 changes the master mints a dated CSV (`design.md` §9). The page shows the latest edition, and the log records what changed.

## 4. Sizing

T1–T5 and T10 are scripts and copy: about a sitting each, with no Exa use apart from T5's fetches. **T6, T7 and T8 are the heavy work**: ~1,300 URLs to read against rows, and ~2,000 raw records to triage. That is spread across sittings, one country at a time, and resumable from `url-audit.csv` and `considered.txt`. After the backlog is cleared, T7's ongoing cost is a few candidates a night. T9 is about 100 Exa briefs.
