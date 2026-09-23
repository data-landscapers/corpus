---
type: design-note
title: site-analytics.md — daily views (Google Analytics) and search clicks (Search Console), collected by the cycle
last_reviewed: 2026-09-23
status: built 2026-09-23 (CC); runs as CYCLE.md step 1a
---

# Site analytics

**Every cycle collects the daily page views for both sites from Google Analytics and the daily search clicks from Google Search Console, and keeps them in one table.** Bill asked for it on 2026-09-23. It is private: nothing here is published, and nothing a reader sees changes, so there is no change-log entry.

## What is already set up (Bill, 2026-09-23)

- **Google Cloud project** `data-landscapers` (no organisation), with the **Google Analytics Data API** and the **Google Search Console API** both enabled.
- **Service account** `dl-stats@data-landscapers.iam.gserviceaccount.com`, with no Cloud roles — it needs none. Added as **Viewer** on the GA4 property and **Restricted** on the Search Console property.
- **Key** at `C:\Users\bill\.api-keys\google-analytics.json`. **It is a credential: never copy it into a repo, never print its contents, never commit its path's contents.** The script reads the path from `CORPUS_GOOGLE_KEY` and falls back to that default.
- **GA4 property ID** `539744459` (the measurement ID `G-BF3X4N6YML` is the tag, not the property — the API wants the number). Both sites load the same tag, so one property carries both, split by hostname.
- **Search Console property** `sc-domain:data-landscapers.io` — a domain property, so it covers `corpus.data-landscapers.io` too. The separate corpus property also exists in Search Console; it is not needed and dl-stats has not been added to it.

**Not yet proved.** A read-only test from Cowork on 2026-09-23 found and read the key but never reached Google — the Cowork shell's network allowlist blocks `googleapis.com`, which says nothing about the permissions. Claude Code on the machine has normal network access, so the first task below is that test.

## The table — `logs/site-analytics.csv`

One row per **date × host**: `date,host,views,users,sessions,clicks,impressions,fetched_at`.

- `host` is `data-landscapers.io` or `corpus.data-landscapers.io`. A local preview (`localhost`, `127.0.0.1`) is dropped — the site being checked on this machine, not readers (Bill, 2026-09-23). Anything else GA reports (`www.`, a preview host) is summed into one row with host `other`, so the day's public total reconciles with the GA interface less those local views.
- `views` is GA4 `screenPageViews`; `users` is `totalUsers`; `sessions` is `sessions`. `clicks` and `impressions` are Search Console's.
- `fetched_at` is when the row was last written, UTC, ISO 8601.
- Sorted by date then host. **Written with `\n` line endings** (`lineterminator="\n"`), because a Windows `csv.writer` default of `\r\n` churns the whole file on every run.
- A value the API did not return is **blank, never 0**. Zero is a real answer. A source *answers* a date on or before the newest date it returned any row for: there a host it said nothing about is 0; past it (Search Console not yet published, or the fetch failed) the old value stands, blank if there was none.
- `other` sums `users` across hosts, which over-counts anyone on two of them. It is there so the day's views reconcile, not as a headcount.

## How a run works — `scripts/site-analytics.py`

**It updates rows, it never appends blindly.** Each run reads the table, works out the date range, fetches, and replaces the rows for every date it fetched.

- **Neither source is final the next morning.** GA4 can take 24–48 hours to settle a day; Search Console trails by two to three days. So every run re-fetches **the last 3 days of GA** and **the last 4 days of Search Console** up to yesterday, and overwrites them. Older rows are settled and are not touched again.
- **The cycle is not strictly nightly** (it fires on an OSINT close, and can be skipped or held), so the range starts at the **earlier of the newest row minus the re-fetch window, and the first missing date** — a skipped night fills itself in on the next run and the table has no gaps.
- **The table starts on 2026-09-13** (`FLOOR`, Bill 2026-09-23) — the first day Search Console has data. The first run backfills from there.
- **GA:** `runReport` on `properties/539744459`, dimensions `date` and `hostName`, the three metrics above, `limit` high enough for the range (paginate with `offset` if not).
- **Search Console:** `searchanalytics.query` on `sc-domain:data-landscapers.io` with `dataState: "all"` (the re-fetch window replaces the provisional days). Dimensions `date` and `page`, paginating with `startRow` at 25,000 rows, then summing `clicks` and `impressions` per date per page hostname. **Grouping by page can total slightly differently from grouping by date alone** — Google aggregates differently per dimension. Take the per-host split from the page query; check its per-date totals against a `date`-only query on the first run and note the difference in the commit body if it is material.
- **The two sources count days in different timezones** — Search Console in US Pacific time, GA in the property's own timezone. A date's clicks and views are not the same visitors. Fine for trends; do not divide one by the other.
- **One source failing does not fail the other.** Its columns stay as they were for that run, and the next run's window picks them up.
- **Exit codes**: 0 both fetched; 1 one or both failed (the table still holds whatever succeeded); 2 misconfiguration — no key, unreadable key, permission denied.
- Dependencies: `google-analytics-data`, `google-api-python-client`, `google-auth`. Import them inside the fetch functions so the tests run without them.
- `--dry-run` prints the rows it would write and writes nothing. `--since YYYY-MM-DD` forces a re-fetch from that date.

## Where it runs in the cycle

**Step 1a of `CYCLE.md`, straight after the notes drain and before the build.** It depends on nothing the build or the render produces, and running first means its commit is in the tree before BUILD stage 0 asks for a clean one, and in the mirror at the end. `CYCLE.md` gets one line of ordering and nothing else; everything about the job is here.

**It never holds the cycle.** On exit 1 or 2 it writes its log line and the cycle goes on to the build. On exit 2 it also writes one block in `logs/messages-for-bill.md` — a revoked key or a lost permission needs Bill — unless a block on the same subject is already open.

**Log line**, through `scripts/log-line.py` — the script's last line of output is the message: `· **ANALYTICS** ·` naming the dates written and yesterday's totals per host, e.g. `2026-09-20..2026-09-22 written; 22 Sep: dl.io 312 views / 41 clicks, corpus 88 views / 9 clicks`. On a failure, which source and the error.

**Commit**: the CSV alone, subject `Analytics: <dates>`. A run that changed no values commits nothing — a row's `fetched_at` moves only when one of its values does, so the file is byte-identical.

## Tasks for Claude Code

1. **Test access, read-only.** In a temp folder outside every repo, install the three libraries and, with the key above, fetch GA views/users/sessions by date and hostName for `7daysAgo`..`yesterday`, list the Search Console sites the account can see, and fetch 10 days of clicks by date on `sc-domain:data-landscapers.io`. If either is refused with a permission error, wait ten minutes and retry once (new users take time to propagate); if it still fails, write one block in `messages-for-bill.md` naming the exact error and stop here.
2. **Write `scripts/site-analytics.py`** to the section above, and `scripts/test_site_analytics.py` in the style of the other `test_*.py`: range calculation (empty table, gap, skipped nights, re-fetch windows), upsert replacing rather than duplicating, `other` host folding, blank-not-zero, `\n` endings. No network in the tests.
3. **Backfill**: run it once for real. Check yesterday's views per host against the GA interface and the Search Console total against its Performance report; say in the commit body how close they were. The log should start from 2026-09-13.
4. **Add step 1a to `CYCLE.md`** — one line pointing here. Add `ANALYTICS` wherever job names are defined for `log-line.py`.
5. **Commit and push** each of 2–4 as its own commit. Then set this note's `status:` to built, with the date.
