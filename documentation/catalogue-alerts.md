---
type: design-note
title: catalogue-alerts.md — one weekly email per reader, built by a Cloudflare Worker and sent by Buttondown
last_reviewed: 2026-09-21
status: built and deployed 2026-09-16; E3 outstanding — Monday 2026-09-21, check `cron_status` first, then release the draft by hand
---

# Catalogue alerts

A reader picks up to five countries and five topics and gets one email a week listing the new documents that match. The **Get alerts** button on the catalogue page opens it. The same email carries the main site's weekly alert of new writing on data-landscapers.io as one more section, and a reader can take any combination from one form and edit it later.

**This note is the live reference: what an alert is, how the thing is configured, and which rules must not change.** The build — the step-by-step setup, the copy as it was drafted, the decisions with the evidence they were taken on — is archived at `archived/catalogue-alerts-build.md`, and the design it displaced at `archived/catalogue-alerts-digest.md`.

## What an alert is

**A catalogue selection.** A set of countries (1–5, or Any) and a set of topics (1–5, or Any), matched the way the catalogue matches: a document matches if it carries **any** of the alert's countries **and any** of its topics. A reader may hold up to **10** alerts and edits them on the site's own manage page. The main-site alert is a fixed alert with the id `site`.

**The site stores no addresses.** Buttondown holds them, in the `data-landscapers` newsletter that already holds the main site's subscribers, which is what keeps `design.md` §1 (no user record) true. KV holds alert *definitions* and dates, never an address.

**One newsletter, and everything it sends is an alert.** There is no hand-written newsletter and no Buttondown RSS-to-email feed. Buttondown is a list and a sender; every rule about what a reader receives lives in this repo, under its tests.

## How it works

`scripts/alerts.py` runs in RENDER Step 5, straight after `catalogue.py`, and writes four files into `site/alerts/`:

- **`recent.json`** — the records ingested in the last **28 days** that pass the **backfill rule**: a record is in only if the end of its publication period is no more than **90 days** before its `ingested` date. Each row carries `id`, `title`, `publisher`, `published`, `ingested`, `places`, `topics`, `url` and `hero` (the record's `catalogue_hero`, or empty); `id` is the first 16 hex characters of the SHA-256 of `url`, or of `title|publisher|published` when there is no URL.
- **`vocab.json`** — `{places, topics}` labels, taken from `catalogue.py` → `vocab()` so they match the catalogue's own menus.
- **`index.html`** — the sign-up page: two capped multi-selects, an email field, a Turnstile widget, the main-site checkbox, and a feed box giving the Atom URL for the current selection. It reads the catalogue's own fragment (`#places=KEN,NGA&topics=tech.ai`, `#site=1`) and preselects from it.
- **`manage/index.html`** — the manage page. It reads `#s=<subscriber id>` from the fragment and **sends it in a POST body**, so the id reaches no server log and no `Referer`.

The Worker `corpus-alerts` (`workers/alerts/worker.js`) serves four routes and a cron handler. On Monday it reads `recent.json` and the main site's `feed.json`, tallies the alert tags in one paginated pass over `/v1/subscribers`, builds **one** Markdown body with a section per alert wrapped in `{% if "alert <id>" in subscriber.tags %}`, and posts it to Buttondown with an audience filter naming only the alerts that matched. A reader whose alerts all came up empty is outside the filter and gets **no email**.

## What is deployed

| | |
|---|---|
| Worker | `corpus-alerts`, route `corpus.data-landscapers.io/api/alerts/*` on zone `data-landscapers.io` — more specific than `download-log`'s `/*`, so it wins for those paths |
| Cron | `0 7 * * MON` — **the day written as a name**, because Cloudflare numbers days 1–7 from Sunday where standard cron makes `1` Monday |
| KV | namespace `alerts`, bound as `ALERTS` |
| Secrets | `BUTTONDOWN_API_KEY`, `TURNSTILE_SECRET`, and optionally `RUN_TOKEN` |
| Variables | `SITE`, `MAIN_SITE`, `SEND_MODE` |
| Turnstile | widget `corpus-alerts`, Managed, hostname `corpus.data-landscapers.io` |

**Routes.** `GET /api/alerts/feed?places=…&topics=…` returns Atom for a selection (400 on an unknown code or more than five of either). `POST /api/alerts/subscribe` verifies Turnstile, validates against `vocab.json`, creates the tag and its KV definition if new, and posts the subscriber. `POST /api/alerts/manage/list` and `/manage/save` both verify Turnstile — without it `list` is an oracle for anyone holding a forwarded link. `POST /api/alerts/run` runs exactly what the cron runs and needs `RUN_TOKEN`; with no token bound it is a 404, and its twin is the gitignored `logs/.alerts-run-token`.

**KV keys.** `def:<alert id>` → `{places, topics, label, tag_name, tag_id, created}`; `last_sent_through` → a date; `sent:<YYYY-MM-DD>` → an email id; `orphan:<tag name>` → a date first seen; `cron_status` → `{at, stage, …}`, overwritten each run, which is how *did Monday run, and where did it stop* is answered from the KV screen.

**Alert ids.** The first 10 hex characters of the SHA-256 of `P=<places sorted, comma-joined, or any>|T=<topics sorted, comma-joined, or any>`. The same selection always gets the same id, so two readers wanting *Kenya, Nigeria · AI* share one tag and one section. The tag is `alert <id>`, with the label as its public description and `subscriber_editable` off.

**The window.** Day after `last_sent_through` to yesterday, capped at 21 days; the last 7 on a first run. **Every date in the handler is UTC**, and so are the `ingested` dates `alerts.py` writes — Buttondown's own timezone is London and nothing here reads it.

## The rules that must not change

- **The subscribe body must never carry a `type` field.** `type: "regular"` is exactly how Buttondown documents bypassing double opt-in for a single subscriber; sent from here it would confirm an address nobody confirmed. It is also the plausible wrong fix — a test address sitting at `unactivated` looks like a bug — so `scripts/test_alerts_worker.py` tests for the field's absence.
- **`archival_mode: "disabled"` on every send.** One body holds every reader's sections, and a web render has no subscriber to test against, so the archive would publish all of them at a permanent URL.
- **The Worker never logs, stores or echoes an email address.** `manage/list` and the cron tally both receive addresses from Buttondown and discard them in the same expression that reads the tags. No `console.log` of a request or response body.
- **`recent.json` publishes nothing the catalogue page does not show.** Its columns are a subset of `build-catalogue.py` → `CSV_COLS`, plus `hero` — not in the download, but drawn under every row of the public catalogue (`catalogue.py`, the chunk field `hero`) — plus the hash. `scripts/test_alerts.py` asserts that allowlist rather than trusting the loop; widening it to anything the page does not show breaks the rule.
- **Every Buttondown `CNAME` goes in as DNS only — grey cloud.** All three site hostnames are proxied, so the habit and the dashboard default are both wrong here, and a proxied row answers with Cloudflare's addresses instead of Postmark's. The check is from outside: a resolver returning `pm.mtasv.net` is looking at an unproxied row.
- **Do not add Buttondown to the root's SPF row.** The return path is `pm-bounces.newsletter.data-landscapers.io` pointed at Postmark, so SPF is evaluated against Postmark's record and the root's hard-fail never enters into it.
- **New decisions go above the marker line in `worker.js`**, or they leave the test suite: everything above it is pure and is what `test_alerts_worker.py` loads.

## The knobs

- **`SEND_MODE`** — `draft` leaves the digest in **Emails → Drafts** for Bill to release; `about_to_send` sends it unattended. Nothing downstream reads the difference, so switching is one variable and no redeploy. **`draft` is a settled end state, not a probation**: it is the workflow Bill already has for the main site, applied to a body he no longer writes.
- **The caps** — five countries and five topics an alert, ten alerts a reader, **25 items a section** (beyond that, *and N more in the catalogue* linking to the catalogue's own fragment). The 25 is the lever if a body ever approaches a size Buttondown refuses.
- **The windows** — 28 days in `recent.json`, 21 days of catch-up, 90 days of backfill. The first two are paired: the send window can only catch up over records the file still carries.

## How the Buttondown account is configured

Set up once on 2026-09-16; `archived/catalogue-alerts-build.md` Part 1 A is the step-by-step and why each was chosen.

- **Sending domain `newsletter.data-landscapers.io`**, through Postmark, on four hand-entered rows in the `.io` zone — DKIM `TXT`, return-path `CNAME` onto `pm.mtasv.net`, click-tracking `CNAME` onto `webhook-consumer.buttondown.email`, and a DMARC `TXT` scoped to the subdomain. `cloudflare.md` → *Alerts send from `newsletter.data-landscapers.io`* holds them. Mail that fails authentication is **quarantined, not bounced**, and the reports go to Postmark rather than to Bill.
- **Double opt-in is on and cannot be turned off.** The confirmation email body is Buttondown's only editable part of it and must contain `{{ confirmation_url }}` **as a link** — a bare variable renders as literal braces, sends happily, and leaves every new subscriber unable to confirm.
- **Firewall: Filtering on Default, not Aggressive**; blocked subscribers on **Reject**, so a turned-away reader sees an error rather than *check your inbox*, and the Worker shows them `## e-blocked`. Aggressive rejected a repeat sign-up of a confirmed address, and the Corpus form has already passed Turnstile before Buttondown sees it.
- **Portal on**, as the unsubscribe path that does not depend on Corpus. The alert tags are `subscriber_editable: false`, so the portal shows a reader nothing about their alerts; it is a second route out, not the only one.
- **Email design is carried by the body, not by Buttondown's chrome.** Every alert and the confirmation email open with `site/assets/email-banner.png`; the newsletter icon is a transparent placeholder, the Header toggle is off, and **Settings → Email → Custom CSS** hides the masthead subject and colophon and supplies the site's type. The settings preview misleads on all of it — **test a design change by sending a draft to yourself, never by the preview**.
- **API key `corpus-alerts-worker`**, scoped to subscribers and emails, read and write. There is no tags scope; if `/v1/tags` ever 403s, `SubscriberInput.tags` creates a missing tag on the subscribe call, so what is lost is the description and the id, not the tag.
- **The post-confirmation redirect** points at `/alerts/manage/#s={{ subscriber.id }}&confirmed=1`. Whether Buttondown fills the variable in a redirect is undocumented; if it does not, the manage page says *Confirmed* and points at the link in the email, which the confirmation email carries for that reason.

## Reader-facing text

**`content/alerts.md` is the copy**, read through `copy_lib`, and it is the only place it lives. The digest body is built by the Worker. Text typed into Buttondown's own settings screens is recorded at the step that types it, in the archived build note.

## The decisions, so nobody reopens them

- **Buttondown, not a mail system of our own** — an address list is a user record, and `design.md` §1 rules one out. Kept over MailerLite, Mailchimp, Kit and EmailOctopus (2026-09-15): moving would move the main list for no gain in the part Bill touches.
- **One newsletter, alerts only** *(Bill, 2026-09-15)*. The cost is that every main-site sign-up must carry `alert site`.
- **One email per reader, not one per alert** *(2026-09-16)*. The rejected per-feed design allowed one country and one topic an alert, sent five emails to a reader with five alerts, and could not edit an alert at all.
- **Existing subscribers got a cadence change and were not told** *(Bill, 2026-09-16)*. The content is what they subscribed for; the rhythm is the only thing that moved. The main site's news is now up to six days late, which is the price of one email per reader.
- **Weekly, Monday 07:00 UTC — and UTC is the choice, not the default.** African timezones do not observe daylight saving, so a UTC-fixed send is the one that never moves for the readers this is for; London is what drifts.
- **The backfill rule is 90 days and it is needed.** Without it an alert would be mostly archive material, because most of what is ingested in a week was published long before it.
- **The Worker owns the send window**, which is what makes a missed Monday catch up, a retried cron harmless, and an ingest date mean what it says. Buttondown's RSS polling gave none of the three.
- **The subscriber id is the edit key.** Buttondown's own magic link exists but lands in its portal, which cannot edit a definition Corpus holds. A forwarded email lets the recipient edit the sender's alerts — already true of Buttondown's manage link, and the same harm as an unconfirmed tag-add, which is likewise accepted.
- **More Worker code, and that is the trade.** Every rule about what a reader receives is in this repo under tests, instead of in a feed's settings screen.

## What is still open

**E3 — Monday 2026-09-21.** Cloudflare's schedule has never been seen to fire: a five-minute test schedule left no trace, so the cron is unproven until a `cron_status` key appears dated that morning. If it is missing, run `POST /api/alerts/run` with the token in `logs/.alerts-run-token` — which builds the same draft — and then find out why the schedule did not fire. Release the first two Mondays as drafts by hand, and after the first, confirm the issue is **not** listed at `https://buttondown.com/data-landscapers/archive/`: that is the outcome check for `archival_mode`, which the draft screen does not expose.

**The hero line — built 2026-09-21, specified by Cowork the same day.** Each digest item shows the record's hero on its own line between the linked title and the publisher line, escaped as the title is, and omitted when empty; the Atom `<summary>` is `<hero> — <publisher> · published <date>`. It matters most where the title is not in English. On that day 4,791 of the 4,803 rows in `recent.json` carried one. **Live once `worker.js` is pasted into the Worker again**; the Worker treats a `recent.json` without `hero` as having none, so the order of render and deploy does not matter. Check the first draft with heroes for size before releasing it — about 120 characters an item, and the 25-item cap is still the lever.

**Not in this version**: report editions as alert items; a monthly pass pruning `def:` entries whose tag has no active subscriber and clearing stale `orphan:` keys; a monthly cadence if readers ask for one.
