---
type: pointer
title: corpus-alerts — see documentation/catalogue-alerts.md
last_reviewed: 2026-09-16
---

# corpus-alerts

**`worker.js` beside this file is deployed to Cloudflare as the Worker `corpus-alerts`, on the route `corpus.data-landscapers.io/api/alerts/*`.** It takes sign-ups, serves a plain Atom feed for a selection, lets a reader edit what they hold, and on a Monday cron builds one weekly digest and hands it to Buttondown.

**The route is more specific than `download-log`'s `/*`**, so it wins for those paths and nothing else about the site's serving changes.

**Bindings, and the names are load-bearing.** KV `ALERTS` → namespace `alerts`; secrets `BUTTONDOWN_API_KEY`, `TURNSTILE_SECRET` and `RUN_TOKEN` (the last optional: it enables `POST /api/alerts/run`, the Monday job on demand, and its twin is the gitignored `logs/.alerts-run-token`); variables `SITE`, `MAIN_SITE` and `SEND_MODE`. One cron trigger, `0 7 * * MON` — the day by name, because Cloudflare counts `1` as Sunday. `documentation/catalogue-alerts.md` → *What is deployed* is the standing account of this, and `documentation/archived/catalogue-alerts-build.md` Part 1 C is how it was set up, step by step.

**Everything else is in that design record** — what an alert is, why there is one email rather than one per alert, why the archive is off, and what is still open. This file is a pointer so the code does not sit in a directory with nothing next to it.

**The first half of `worker.js` is pure** — no `fetch`, no KV, no `Response` — and `scripts/test_alerts_worker.py` loads it on its own to test the rules. The marker line in the file is where that half ends. Keep new decisions above it.
