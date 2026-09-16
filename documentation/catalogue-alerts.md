---
type: design-note
title: catalogue-alerts.md — one weekly email per reader, built by a Cloudflare Worker and sent by Buttondown
last_reviewed: 2026-09-16
status: A, B, C done 2026-09-16 except A10 (existing subscribers not yet tagged `alert site`, found in D11) and Buttondown still bannering the sending domain as unfinished; D1-D11 and D17 passed; D12-D16 next, then E
---

# Catalogue alerts

A reader picks up to five countries and five topics, and gets one email a week listing the new documents that match. The **Get alerts** button on the catalogue page opens it. The same email carries the main site's weekly alert of new writing on data-landscapers.io as one more section, and a reader can take any combination from one form and edit it later.

**How it works.** The site publishes a small file of recent records. A Cloudflare Worker, on a Monday cron trigger, reads that file, builds **one** email body with a section per alert, and hands it to Buttondown to send. Each section is wrapped in a template test on the reader's tags, so a reader sees only the alerts they hold. **The site stores no addresses.** Buttondown holds them, in the `data-landscapers` newsletter that already holds the main site's subscribers. That keeps `design.md` §1 (no user record) true.

**One newsletter, and everything it sends is an alert.** There is no hand-written newsletter and, from this design on, no Buttondown RSS-to-email feed either. Buttondown is a list and a sender; every rule about what a reader receives lives in this repo, under its tests.

**An alert is a catalogue selection.** A set of countries (1–5, or Any) and a set of topics (1–5, or Any), matched the way the catalogue matches: a document matches if it carries **any** of the alert's countries **and any** of its topics. The main-site alert is a fixed alert with the id `site`. A reader may hold up to **10** alerts and can edit them on the site's own manage page.

Part 1 is the build, in order. Part 2 is the reader-facing text, ready to paste. Part 3 records the decisions, so nobody reopens them during the build. Part 4 is the one thing still to prove.

---

## Part 1 — Implementation

Parts A, C, D and E are Bill's. Part B is code, for a CC session given the brief in B1; B8 and B9 are in the `data-landscapers` repo. Every Buttondown API detail below was checked against Buttondown's own schema (`https://docs.buttondown.com/openapi.json`) and its template-variable documentation on **2026-09-16**. If a call fails, check that schema first.

### A. Buttondown setup (Bill, about 30 minutes)

Menu names are Buttondown's as documented on 2026-09-16; if a screen has moved, search its docs for the setting. Everything here is in the existing **data-landscapers** newsletter; no second newsletter is created.

1. Log in to Buttondown and open the **data-landscapers** newsletter.
2. Open **Settings → Billing**. The account is on Buttondown's **Standard** plan (Bill, 2026-09-15), which covers **Tagging & segmentation** through Basic (Bill, 2026-09-15) and API sending. Nothing needs adding. This design uses neither automations nor RSS-to-email, so once it has sent twice, check whether Standard is still the right plan.
3. Open **Settings → Basic**. Confirm the sender name is **Data Landscapers**, and under **Settings → Domains** that the newsletter sends from a **`newsletter.data-landscapers.io`** address. **Done, 2026-09-16**; the rest of this step is the record of how, and the one thing left to check.

    **The sending domain is `newsletter.data-landscapers.io`, and Buttondown sends through Postmark.** Four rows went into the `.io` zone by hand and all four verify: a DKIM `TXT`, a `CNAME` for the return path onto `pm.mtasv.net`, a `CNAME` for click tracking onto `webhook-consumer.buttondown.email`, and a DMARC `TXT` scoped to the subdomain. `cloudflare.md` → *Alerts send from `newsletter.data-landscapers.io`* holds them and the consequences.

    **Buttondown's managed DNS and its Cloudflare integration were both declined.** *Managed DNS* delegates a subdomain to Buttondown with two `NS` records, which is a part of the zone `cloudflare.md` could no longer describe; the *integration* wants a DNS-edit grant over the zone that serves both sites, the Workers routes and every edition URL, in exchange for saving four rows of typing. Manual rows cost ten minutes and leave the zone knowable.

    **This note had chosen the root domain, and the subdomain is better.** The root was picked on a reading of `cloudflare.md` that said the `.io` carried no `MX` and no `TXT` — wrong, as a resolver showed: Microsoft 365 receives mail there and `v=spf1 include:secureserver.net -all` was already present. Buttondown's flow put the records on `newsletter.` regardless, which answers the objection the correction raised: **newsletter reputation now sits on its own name** rather than on the domain carrying Bill's correspondence. The cost is a `From` address that reads `newsletter.data-landscapers.io`.

    **The SPF worry this raised is closed, and the answer was that there is nothing to do.** No `v=spf1` row was asked for. The return path is `pm-bounces.newsletter.data-landscapers.io` pointed at Postmark, so SPF is evaluated against **Postmark's** record and the root's hard-fail row never enters into it. **Do not add Buttondown to the root's SPF row** — it would be a change with no sender behind it.

    **Every `CNAME` goes in as DNS only — grey cloud**, and both did. This is the row that fails silently: `cloudflare.md` records that all three site hostnames are proxied, so the habit and the dashboard default are both wrong here, and a proxied row answers with Cloudflare's addresses instead of Postmark's. The check is from outside — a resolver that returns `pm.mtasv.net` rather than a Cloudflare address is looking at an unproxied row. **Do not orange these while tidying the zone.**

    **The one thing left: confirm the `From` address is the one you want** before any send, since it is now on the subdomain rather than the root. `newsletter.data-landscapers.io` mail that fails authentication is **quarantined, not bounced** (`p=quarantine`), and the reports go to Postmark rather than to Bill — so D's test send is where a delivery is verified rather than assumed.
4. Set the timezone to **Europe/London**, or whatever the nearest option is. **Nothing depends on it** — Buttondown offers no UTC option (Bill, 2026-09-16), and this step is left over from the design where Buttondown owned the schedule and *weekly, Monday 07:00* was read in the newsletter's timezone. It does not any more: the Cloudflare cron fires and the Worker posts a finished email, which Buttondown sends on receipt. The setting now governs only how times read in Buttondown's own dashboard. Set it to London and move on.

    **The send time is fixed in UTC on purpose, and will not track London.** Cloudflare cron triggers are UTC-only, so `0 7 * * MON` means 07:00 UTC all year: 08:00 London in summer, 07:00 London in winter. Pinning it to London instead would mean editing the cron at both daylight-saving boundaries for ever, and it would be the wrong target anyway — **this readership is African, and African timezones do not observe daylight saving**, so a UTC-fixed send is the one that never moves for the people receiving it. London is the timezone that drifts here, not UTC.
5. Set the description to: *Weekly email alerts: new writing on data-landscapers.io and new documents in the Corpus catalogue.*
6. **Nothing to do: double opt-in cannot be turned off, so there is no toggle to find** (Buttondown's docs, read 2026-09-16; Bill looked for one and there is none). Buttondown requires it of every newsletter and states that it cannot be disabled globally. It can be waived only two ways, and knowing both is the point of this step: **per subscriber, by sending `type: "regular"` on the API call**, or newsletter-wide by asking Buttondown's support to set a hidden `should_require_double_optin` flag. Neither is wanted here. Open **Settings → Subscribing** only to find the **Confirmation** section, which is A7's screen.
7. Open **Settings → Subscribing → Confirmation** (`https://buttondown.com/settings/subscribing/confirmation`). **It is one block of text** (Bill, 2026-09-16). Paste this into it:

    ```
    You asked for weekly email alerts from Data Landscapers: new writing on data-landscapers.io, new documents in the Corpus catalogue, or both.

    [Confirm your alerts]({{ confirmation_url }})

    If this wasn't you, ignore this email and nothing will be sent.
    ```

    **The subject is not on that screen, and Buttondown's default stands.** The API carries `custom_subscription_confirmation_email_subject`, so a subject can be set by a call if it is ever wanted; it is not worth one. The body is the part a reader has to act on. (An earlier version of this step asked for a subject and a reminder as separate fields, inferred from the API schema. **The schema describes the API, and the screens expose a subset of it** — the same trap A14 warns about, so a step naming a field should say where the name came from. These two say: from Bill, looking at it.)

    **There is no default template to find.** The field is a custom override — schema default `""` — so the block is empty until something is typed into it, and Buttondown's built-in confirmation email is not exposed as editable text. Nothing is being replaced; something is being supplied for the first time.

    **The variable is `{{ confirmation_url }}`, and it must be a link.** Buttondown's own field description: *"Must contain `{{ confirmation_url }}` as an HTML or Markdown link."* A bare `{{ confirmation_url }}` on its own line is neither, which is why the text above wraps it in brackets — the wording around it can change, the brackets cannot go. A confirmation email whose link does not resolve renders as literal braces, sends happily, and leaves every new subscriber unable to confirm; nothing in Buttondown warns about it and the reader has no way to report it.

    **If a reminder field is on the screen, leave it empty.** Buttondown sends its own reminder to subscribers who never confirm, and a second piece of copy is a second thing to keep true.
    **Firewall: Filtering on Default, not Aggressive** (2026-09-16, found in D5). Buttondown scores every sign-up and rejects anything over a threshold, and on Aggressive it rejected a repeat sign-up of Bill's own confirmed address with `400 subscriber_blocked`. The Corpus form has already passed Turnstile before Buttondown sees it, so Aggressive adds little here beyond turning away borderline readers on shared carrier and institutional IPs; the main site's embed form has no Turnstile and Default still covers it. IP address filtering stays on, and a second fresh address went through with both tags under that combination. Handling of blocked subscribers stays on **Reject**, so a turned-away reader sees an error rather than *check your inbox*. The Worker shows such a reader `## e-blocked`, which tells them not to retry.
8. Open **Settings → Features → Portal** and turn the portal on. It is a **feature**, not a settings page — in the API it is an entry in the newsletter's `enabled_features` list alongside `archives`, `comments` and the rest — which is why *Settings → Portal* was not there to find (Bill, 2026-09-16).

    **Keep it on as the unsubscribe path that does not depend on Corpus.** Alerts are added and edited on the site's own manage page, and the alert tags are `subscriber_editable: false` (A9), so the portal shows a reader nothing about their alerts and is not where they are managed. What it gives is a Buttondown-hosted page for seeing and ending a subscription, reachable if the Worker or the site is down — the one reader-facing control in this design that should not have Corpus in its path. Buttondown's per-email unsubscribe link works regardless; this is the second route, not the only one.
9. Open **Tags** and create the tag **`alert site`**: colour `#1a5f7a`, public description *New writing on data-landscapers.io*, subscriber-editable **off**.
10. Open **Subscribers**, select every active subscriber, and add the tag `alert site`. Check that the tag's count equals the active subscriber count. There are a few of them (Bill, 2026-09-16), so this is a one-screen job. **It keeps the content they signed up for and changes when it arrives** — see *Existing subscribers get a cadence change, not a no-change* in Part 3.
11. Open **RSS-to-Email**, which is its own menu item and **not** part of *Automations* (Bill, 2026-09-16). The two are separate things in the API as well — `/external_feeds` for RSS-to-email, `/automations` for trigger-and-action workflows — and **this design uses neither**, so *Automations* needs no visit at all. What you are looking for here is an existing feed, and there are two cases; which one you are in decides nothing later, only what there is to switch off:
    - **A feed for `https://data-landscapers.io/feed.xml` exists**, whatever its behaviour. Set it to **Draft** now and note its settings. It is deleted in E, after the digest has sent once — delete it earlier and readers lose a week, leave it on Emails and they get the main site twice.
    - **No such feed exists**, because the main-site alert has been composed and sent by hand. Nothing to change here. What has to stop instead is the hand-send itself, and that is E4.
12. Open **API → Keys**.
13. Create a key labelled **corpus-alerts-worker**.
14. Grant **subscribers — read and write** and **emails — read and write**, and nothing else. **Done 2026-09-16, and those are the screen's own labels** (Bill): the scopes are named for the objects, not the `*_access` names the API schema suggested, and read/write is granted per object. *Automations* is not needed — nothing in this design uses one.

    **There is no tags scope, and that is the thing to watch.** The Worker calls `GET` and `POST /v1/tags` to create an alert's tag with its public description and to read back its id. No scope on the screen covers tags by name, so either `subscribers` carries them or those calls will **403**. If they do, the fallback is already in Buttondown's own contract: `SubscriberInput.tags` states that *"tags that don't already exist will be created"*, so the subscribe call alone is enough to attach a tag — what is lost is the description and the id, not the tag.

    **It surfaces at the first sign-up, not at the first cron**, which is the good version of this failure: D step 5 submits the form with Bill's own address and a 403 there names the endpoint in the Worker's log. Widen the one scope it names, and nothing else.

    **It also touches Part 4's open question.** If `/v1/tags` cannot be read, the Worker has no tag ids at all, and the email audience filter must take tag **names** — which is the answer Part 4 already thinks more likely. The two resolve together, and both resolve in D.
15. Copy the key into your password manager. It is used in C6.

### B. Build (CC session)

**Done 2026-09-16**, in Corpus and in `data-landscapers` as two commits. What follows is the
brief as it was written; the notes marked **Built** record where a step landed differently
from the way it reads here, and are the only part worth re-reading.

**Built: the Worker is written in two halves.** B6 asked for the Worker's tests "under the
same runner as `download-log`'s", and `download-log` has no tests and this machine has no
JavaScript runtime at all — so a Worker test written that way would never have run. Instead
`worker.js` carries a marker line: above it every rule is a pure function taking plain data
and returning plain data, below it the I/O that does no deciding.
`scripts/test_alerts_worker.py` loads the half above the marker into node where node exists
and into Duktape (`pip install dukpy`) where it does not, and runs all fourteen of B6's
cases. Three of them — the `/tags` call, the absent `type` key, the absent `console.log` —
are read off the source instead, because they are about which branch a call sits in rather
than about a value. **New decisions go above the marker**, or they leave the test suite.

**Built: `pip install dukpy` is a new dependency of the test suite**, and only of the test
suite. Nothing the site builds needs it and the suite skips cleanly without it.

1. Start a fresh CC session in `C:\CORPUS` with this brief: *"Build catalogue alerts per `documentation/catalogue-alerts.md` Part 1 B, then stop for Bill's deploy."*

    **Part A is done (2026-09-16) and B does not depend on any of it.** Two things the fresh session should not stop to ask about. **The Turnstile site key does not exist yet** — it is created in C3, after this — so B3 writes a named placeholder constant and C4 replaces it, re-renders and pushes; do not block on it and do not invent a key. And **the Buttondown API key is Bill's to paste in C6**, never committed and never needed by this session: B writes the Worker to read it from a secret binding and stops there.
2. CC builds B3–B7, runs RENDER's catalogue step, commits and pushes, then does B8–B9 in `data-landscapers` as their own commit.
3. **`scripts/alerts.py`** writes four files, and RENDER runs it straight after `catalogue.py`, with a line added to `RENDER.md` Step 5:
   - **`site/alerts/recent.json`**: the records ingested in the last **28 days** that pass the **backfill rule**. A record passes if the end of its publication period is no more than **90 days** before its `ingested` date. The period is the day, the month or the year, according to `date_precision`. Records with no `published` date are excluded. Each row carries `id`, `title`, `publisher`, `published`, `ingested`, `places` (array), `topics` (array) and `url`. `id` is the first 16 hex characters of the SHA-256 of `url`, or of `title|publisher|published` when there is no URL. The source is `outputs/catalogue/raw-catalogue.json`, and only columns already in `CSV_COLS` are used, so nothing unpublished leaks. **28 days, not 14**: the send window catches up after a missed Monday, and it can only catch up over records the file still carries.
   - **`site/alerts/vocab.json`**: `{places: {code: label}, topics: {slug: label}}`, taken from `catalogue.py` → `vocab()` so the labels match the catalogue's menus. Places include the region codes (`XWA`, `XAF`, `XGL` and so on), as the catalogue's place facet does.
   - **`site/alerts/index.html`**: the sign-up page, in the site's chrome, with its text drawn from **`content/alerts.md`** through `copy_lib` (Part 2 gives the blocks). The page has:
     - two multi-selects, Country and Topic, filled from `vocab.json` at build time, each with an **Any** option and a **cap of five** enforced in the page;
     - a checkbox, **New writing on data-landscapers.io** (`site`, value `1`), unticked by default, with the `## site` text as its label;
     - an email field;
     - a Cloudflare Turnstile widget (site key from C3, written in as a constant);
     - a submit button that posts to `/api/alerts/subscribe`.

     A small script reads the fragment (`#places=KEN,NGA&topics=tech.ai`, the catalogue's own keys) and preselects every value, up to five each. Beyond five it preselects the first five and shows the *several* note. The fragment `#site=1` ticks the checkbox. Submitting with both selects on Any and the checkbox unticked is refused in the page. A second, collapsed section gives the plain Atom feed URL for the current selection, and `https://data-landscapers.io/feed.xml` when the checkbox is ticked, for readers who use a feed reader.
   - **`site/alerts/manage/index.html`**: the manage page, same chrome, text from the same content file. It reads `#s=<subscriber id>` from the fragment, POSTs it to `manage/list`, and shows each alert as an editable row using the same pickers, with a delete button per row, an **Add alert** button up to ten, and the main-site checkbox. Saving posts to `manage/save`. **The subscriber id never leaves the fragment for a URL**: the page reads it from `location.hash` and sends it in a POST body, so it reaches no server log and no `Referer`.
4. **Catalogue button.** In `catalogue.py`, add a row to the downloads box under *This selection*: **Get alerts**, a `.btn btn--sm` link to `../alerts/`. The page's script rewrites its `href` on every redraw to carry the current `places` and `topics` as a fragment. It stays enabled with nothing selected and then opens the alerts page blank.
5. **`workers/alerts/worker.js`** is a new Worker, separate from `download-log`. `workers/alerts/README.md` is a pointer to this file. Bindings: KV `ALERTS`; secrets `BUTTONDOWN_API_KEY` and `TURNSTILE_SECRET`; variables `SITE` = `https://corpus.data-landscapers.io`, `MAIN_SITE` = `https://data-landscapers.io`, `SEND_MODE` = `draft`. One cron trigger, `0 7 * * MON`.

   **`SEND_MODE` has two settled values and either may be permanent.** On `draft` the Worker builds the digest every Monday and leaves it in **Emails → Drafts** for Bill to release; on `about_to_send` Buttondown sends it unattended. `draft` is how the first two Mondays go (E3), and it is also the end state if Bill wants to keep his hand on the send — it is the workflow he already has for the main site, applied to a body he no longer writes. Nothing downstream reads the difference: the audience filter, the sections, the window and `sent:<date>` are identical either way, so switching is one variable and no redeploy.

   **KV keys.** `def:<alert id>` → `{places, topics, label, tag_name, tag_id, created}`; `last_sent_through` → a date; `sent:<YYYY-MM-DD>` → an email id; `orphan:<tag name>` → a date first seen. **Built:** `cron_status` → `{at, stage, …counts or error}`, overwritten each run, so whether Monday ran and where it stopped can be read on the KV pairs screen (added after D9 left no trace, 2026-09-16). **KV holds definitions only, never an address**; a definition is no more personal than a catalogue URL. `tag_id` is stored because the body's section test uses the tag **name** while the email's audience filter uses whatever Part 4 settles — keeping both means the Worker needs no second round trip either way.

   **Alert ids.** The id is the first 10 hex characters of the SHA-256 of the canonical definition, `P=<places sorted, comma-joined, or any>|T=<topics sorted, comma-joined, or any>`. The same selection always gets the same id, so two readers who want *Kenya, Nigeria · AI* share one tag and one section. The tag is named `alert <id>` — 16 characters, inside Buttondown's 100-character limit and its name pattern — with the alert's label as its public description and `subscriber_editable` off.

   Four routes and a cron handler:

   - **`GET /api/alerts/feed?places=KEN,NGA&topics=tech.ai`** (either parameter may be omitted, not both), for feed readers:
     - reject a code not in `vocab.json`, or more than five of either, with 400;
     - fetch `recent.json` and `vocab.json` from `SITE`, cached 15 minutes;
     - keep the rows matching any given place **and** any given topic;
     - sort newest `ingested` first and cap at 200;
     - return Atom 1.0 (`application/atom+xml`), cached 30 minutes in `caches.default`.

     The feed title is the alert's label. Each entry has `<id>` `tag:corpus.data-landscapers.io,2026:<id>`; `<title>` the title; `<link href>` `url`, or `SITE/catalogue/#q=<encoded title>` when `url` is empty; `<updated>` and `<published>` `ingested` at `T00:00:00Z`; `<summary>` `<publisher> · published <published>`. An empty result is still a valid feed with no entries.

   - **`POST /api/alerts/subscribe`** (form-encoded: `email`, `places`, `topics`, `site`, `cf-turnstile-response`):
     1. Verify Turnstile at `https://challenges.cloudflare.com/turnstile/v0/siteverify`, passing the client IP. On failure, redirect 303 to `/alerts/?e=check`.
     2. Validate `places` and `topics` against `vocab.json` (at most five each), `site` as absent or `1`, and the email's shape. At least one of `places`, `topics` and `site` must be set. On failure, redirect 303 to `/alerts/?e=input`.
     3. Steps 3–4 run only when `places` or `topics` is set; a site-only request goes straight to step 5. Compute the alert id and read `def:<id>`.
     4. If the definition is absent: `POST /v1/tags` with header `X-Buttondown-Collision-Behavior: overwrite` and body `{name: "alert <id>", color: "#1a5f7a", public_description: "<label>", subscriber_editable: false}`, then write `def:<id>` with the returned tag `id`.
     5. `POST /v1/subscribers` with header `X-Buttondown-Collision-Behavior: add` and body `{email_address, tags: [...], ip_address: <client IP>, referrer_url: SITE + "/alerts/"}`. `tags` holds `alert <id>` if steps 3–4 ran, and `alert site` if `site` is set. A new address gets Buttondown's confirmation email. An existing one has the tags added. The Worker never creates the `alert site` tag; A9 did.

        **The body must never carry a `type` field.** `SubscriberInput` accepts one, and `type: "regular"` is precisely how Buttondown documents bypassing double opt-in for a single subscriber (A6). Sent from here it would confirm an address nobody confirmed — a consent failure, one word wide, in the one call that handles a stranger's email address. Absent, Buttondown creates the subscriber `unactivated` and sends the confirmation itself, which is the whole point. **It is also the plausible wrong fix**: a test address sitting at `unactivated` looks like a bug, and `type: "regular"` makes the symptom go away. B6 tests for the field's absence so that edit cannot survive.
     6. Redirect 303 to `/alerts/?ok=1`. On any Buttondown error, redirect 303 to `/alerts/?e=later` and do nothing else.

   - **`POST /api/alerts/manage/list`** (JSON: `s`, `cf-turnstile-response`): verify Turnstile, then `GET /v1/subscribers/<s>`, keep the tags matching `^alert (site|[0-9a-f]{10})$`, look each up in KV, and return `[{id, places, topics, label}]` plus whether `site` is held. **It does not return the email address**, and the response for an unknown `s` is indistinguishable from one with no alerts. Turnstile is on this route as well as `save`: without it the route is an oracle for anyone holding a forwarded link, and it costs the reader nothing they are not already passing on the same page.

   - **`POST /api/alerts/manage/save`** (JSON: `s`, `alerts: [{places, topics}]`, `site`, `cf-turnstile-response`): Turnstile, validate against `vocab.json` (at most ten alerts, five of each per alert), compute each id, create any missing tag and definition as in step 4, then `PATCH /v1/subscribers/<s>` with the subscriber's **non-alert tags** plus the new alert tags — read them back first, so a tag Buttondown holds for another reason survives the write. Saving with no alerts leaves the address subscribed and sent nothing; the page says so and points to the unsubscribe link in any email.

   - **The cron handler**, at Monday 07:00 UTC:
     1. Read `last_sent_through`. The window is the day after it to yesterday, capped at 21 days; on the first run, the last 7 days. **Every date in the handler is UTC** — the window, `last_sent_through`, `sent:<date>` and the Monday in the subject — and so are the `ingested` dates `alerts.py` writes. Buttondown's own timezone is London (A4) and is not UTC; nothing here reads it, and nothing here should start. If `sent:<this Monday>` already exists, stop — a retried cron cannot send twice.
     2. Fetch `recent.json` from `SITE` and `feed.json` from `MAIN_SITE` (B9).
     3. **Tally the alert tags in one pass**: page through `GET /v1/subscribers?type=regular` and count, for each tag name matching the alert pattern, how many subscribers carry it. `Subscriber.tags` is a list of tag **names**, so this needs no per-tag call. Buttondown carries no subscriber count on a tag, and `/v1/tags/{id}/analytics` reports `created_subscribers` — subscribers created *with* the tag, not those holding it now — so the single pass is the only correct count as well as the cheapest. Honour `Retry-After` and the `X-RateLimit-*` headers on 429 with a bounded backoff; abandon the run rather than half-send.
     4. For each tag with at least one subscriber, read `def:<id>` and select the window's records matching its definition, newest `ingested` first. A tag with no definition is skipped, its name written to `orphan:<name>`, and the run continues — `recent.json` carries 28 days and the window catches up to 21, so restoring the definition inside three weeks loses the reader nothing. Drop alerts with no match.
     5. Build one Markdown body: a short opening line, then for each non-empty alert a section wrapped in `{% if "alert <id>" in subscriber.tags %}` … `{% endif %}`, with the alert's label as a heading, up to **25** items, and when there are more, *and N more in the catalogue* linking to `SITE/catalogue/#places=<…>&topics=<…>` (the catalogue's own fragment, comma-joined). The main-site section uses `alert site` and the posts in `feed.json` dated inside the window. The footer carries the manage link and Buttondown's own unsubscribe footer.
     6. `POST /v1/emails` with the subject **Data Landscapers alerts — week of \<Monday's date\>**, the body, `status` from `SEND_MODE` (`draft` or `about_to_send`), **`archival_mode: "disabled"`**, and `filters` = `{"predicate": "or", "groups": [], "filters": [one {"field": "subscriber.tags", "operator": "contains", "value": "<tag>"} per non-empty alert]}`. A reader none of whose alerts matched is outside the filter and gets **no email**, which keeps *No new documents, no email*.

        **`archival_mode` must be `disabled`.** The body holds every reader's sections. Rendered for the web archive there is no subscriber, so every section shows at once, and the result is a permanent public URL carrying an unreadable page. Nothing private leaks — there are no addresses in it — but the archive is not where this belongs.
     7. Write `last_sent_through` = yesterday and `sent:<date>` = the email's id.
     8. If nothing matched at all, write `last_sent_through` and send nothing.

     All Buttondown calls send `Authorization: Token <BUTTONDOWN_API_KEY>`. **The Worker never logs, stores or echoes an email address.** `manage/list` and the cron's tally both receive addresses from Buttondown; both discard them in the same expression that reads the tags. No `console.log` of a request or response body.
6. **Tests** (in `scripts/`, the house pattern; the Worker's under the same runner as `download-log`'s):
   - the backfill rule at each `date_precision`;
   - the record `id` for a row with and without a URL;
   - the alert id is stable under reordering and under Any;
   - matching with several places and topics, place only, topic only, and both;
   - the digest body for a fixed set of alerts matches a golden file;
   - the `or` filter lists exactly the non-empty alerts, and the email carries `archival_mode: "disabled"`;
   - a site-only sign-up makes no `/tags` call;
   - the subscribe body carries no `type` key, so double opt-in cannot be bypassed;
   - a retried cron sends nothing;
   - a tag with no definition is skipped and recorded, and the rest of the email is built;
   - `manage/list` never returns an email address;
   - `manage/save` keeps non-alert tags;
   - Atom validity of an empty and a full feed;
   - that `recent.json` carries no key outside `CSV_COLS` plus `id`.
7. Commit the build. Push. Leave `workers/alerts/worker.js` for Bill to paste in C.
8. **Main-site form** (in `data-landscapers`, its own commit). In `newsletter/index.md`:
   - add `<input type="hidden" name="tag" value="alert site">` inside the form, so every new main-site subscriber carries the tag;
   - change the first *What to expect* line to *One email a week, on Monday, listing new articles, datasets and research*;
   - add a line under the form: *Want alerts for one country or topic from the Corpus catalogue? Set them up at https://corpus.data-landscapers.io/alerts/*.
9. **`feed.json`** (same repo, same commit): a Liquid-built JSON twin of `feed.xml` carrying `title`, `url`, `date` and `description` for the last 20 posts, so the Worker needs no XML parser. `feed.xml` stays for feed readers.

### C. Cloudflare setup and deploy (Bill, about 30 minutes)

1. Open the Cloudflare dashboard.
2. Go to **Turnstile → Add widget**.
3. Name it **corpus-alerts**, add hostname `corpus.data-landscapers.io`, mode **Managed**. Copy the site key and the secret key.
4. Give the site key to the CC session. It goes into `alerts.py`; re-render, commit and push.
5. Go to **Workers & Pages → Create → Worker**. Name it **corpus-alerts**. Deploy the placeholder.
6. Open the Worker's **Settings → Variables and Secrets**. Add secret `BUTTONDOWN_API_KEY` (from A15), secret `TURNSTILE_SECRET` (from C3), and text variables `SITE` = `https://corpus.data-landscapers.io`, `MAIN_SITE` = `https://data-landscapers.io`, `SEND_MODE` = `draft`.
7. Go to **Storage & Databases → KV → Create namespace**. Name it `alerts`.
8. In the Worker's **Settings → Bindings**, add a KV binding: variable name `ALERTS`, namespace `alerts`.
9. Open the Worker's **Edit code**. Paste `workers/alerts/worker.js`. Deploy.
10. In the Worker's **Settings → Triggers**, add a cron trigger `0 7 * * MON`, and check the dashboard reads it back as **07:00 on Monday**.

    **Write the day as a name, not a number.** Cloudflare numbers the days of the week 1–7 **from Sunday**, where standard cron counts 0–6 from Sunday and makes `1` Monday. This step read `0 7 * * 1` until 2026-09-16, and the dashboard showed *07:00 on Sunday* the moment Bill saved it — a digest built a day early would have sent with a window ending on Saturday and a subject naming a Sunday. `MON` means the same thing to both conventions.
11. In the Worker's **Settings → Domains & Routes**, add route `corpus.data-landscapers.io/api/alerts/*` on zone `data-landscapers.io`. It is more specific than `download-log`'s `/*`, so it wins for those paths and nothing else changes.

### D. Test before going live (Bill, with the CC session)

1. Open `https://corpus.data-landscapers.io/api/alerts/feed?places=KEN`. Expect an Atom feed with entries.
2. Open the same with `places=ZZZ`. Expect a 400.
3. Open `https://corpus.data-landscapers.io/catalogue/#places=KEN,NGA&topics=tech.ai`.
4. Click **Get alerts**. Expect the alerts page with Kenya, Nigeria and the AI topic already selected, and the main-site box unticked.
5. Tick the main-site box. Enter your own email address and submit.
6. Expect the page's *check your inbox* message, then Buttondown's confirmation email. Click the confirm link.

    **Where the confirm link lands is Buttondown's setting.** On 2026-09-16 it landed on the site's home page. Point Buttondown's post-confirmation redirect at `https://corpus.data-landscapers.io/alerts/?ok=confirmed`, which shows *Confirmed. Your alerts start with the next Monday email.* One confirmation email serves the catalogue and main-site sign-ups alike, and the alerts page covers both.
7. In Buttondown, open **Subscribers**. Expect your address with two tags: `alert site` and one `alert <id>`.
8. Sign up a second and third test address: one with a single country and no main-site box, one with three alerts set up in three submissions.
9. With `SEND_MODE` still `draft`, run the cron by hand — the dashboard's **Trigger** button, or `wrangler cron trigger --cron "0 7 * * MON"`.

    **Built: neither exists here.** The dashboard has no trigger button and this machine has no wrangler, and a five-minute schedule left no trace (2026-09-16). The Worker has `POST /api/alerts/run` instead, which runs exactly what the cron runs and answers with `cron_status`. It needs the Worker secret `RUN_TOKEN`, whose value is in the gitignored `logs/.alerts-run-token`; a CC session calls it from there. With no `RUN_TOKEN` bound the route is a 404.
10. Open **Emails → Drafts**. Expect one draft. Check the subject and that the audience filter names only the alerts with matches.
11. Use Buttondown's **subscriber preview** on that draft for each test address in turn. Expect each to see only its own sections: three sections for the third address, one for the second, and the main-site section only where the box was ticked.
12. Check the draft's archive setting is off, and that no address appears anywhere in the Worker's **Logs** tab.
13. Delete the draft. Run the cron again. Expect it to stop without sending — `sent:<date>` is set.
14. Open the manage link from the preview. Expect your alerts listed. Edit one to add a country, delete another, save.
15. In Buttondown, check the subscriber's tags match the edit, and that `alert site` survived it.
16. Save with no alerts. Expect the *nothing sent* message and the address still subscribed.
17. Submit the sign-up form again with an address and a selection it already holds. Expect no second tag and no error.

### E. Go live (Bill)

1. Tell the CC session the tests passed.
2. Clear `last_sent_through` and any `sent:<date>` keys left by the tests.
3. Release the first two Mondays as drafts, by hand. Only then consider `about_to_send`, and only if you want the send unattended — `draft` is a settled end state, not a probation. A template mistake here reaches everyone at once, which is the one way this design is worse than a feed per alert.
4. **Stop the old main-site alert, once the digest has sent once.** Delete the RSS-to-email feed held at Draft in A11 if there was one; if the main-site alert was sent by hand, stop sending it. **Both running is the failure this design exists to prevent** — a reader holding `alert site` would get the same post in a hand-sent mail and again in Monday's digest.
5. The session updates `design.md` §6 to say alerts are built, and logs the run.
6. **Nothing is announced, to anyone.** Existing subscribers move to the weekly rhythm without notice (Bill, 2026-09-16); the digest itself says what it is, and the first one a reader opens looks like the alert they signed up for. The link on the main site's newsletter page (B8) is the announcement to everyone who is not already subscribed.

### Later, not in this version

- **Report editions as alert items**: a new status or progress report for a country going into that country's alerts.
- **Pruning**: a monthly pass that deletes any `def:` entry whose tag has no active subscriber, and the tag with it, and clears `orphan:` keys older than a month.
- **A monthly cadence**, if readers ask for one.
- **Per-alert item caps**, if the body ever approaches a size Buttondown refuses. The lever is the 25 in B5 step 5.

---

## Part 2 — Reader-facing text

Blunt, per the site's copy rules. **Everything here is site copy: the page blocks go into `content/alerts.md` under these headings, and the digest body is built by the Worker.** Text that is typed into Buttondown's own settings screens sits inline at the step that types it — A5's description, A7's confirmation email, A9's tag description — because a step Bill performs once should not send him to another section to find its own words.

### `## title`

Alerts

### `## lede`

Get an email when new documents about your countries or topics reach the catalogue. Free, weekly, and you can stop at any time.

### `## how`

1. Pick countries, topics, or both.
2. Enter your email address.
3. Confirm from the email we send you.

You then get one email a week, on Monday, listing the new documents that match. No new documents, no email.

### `## what`

An alert can cover up to five countries and five topics. A document matches if it is about any of the countries and any of the topics. Choose **Any** to widen either side.

You can hold up to ten alerts. They all arrive together, in one email on Monday.

An alert lists documents published in roughly the last three months as they reach the catalogue. Older documents we add to the archive are not sent; find those in the catalogue.

A region, such as West Africa, covers documents about the region as a whole, not every document about each country in it.

### `## site`

Also send me new writing from data-landscapers.io: articles, working papers and datasets, once a week.

### `## several`

An alert covers up to five countries and five topics. Your selection had more, so pick the ones you want below.

### `## manage`

Every alert email has a link to change your alerts or stop them.

### `## manage-title`

Your alerts

### `## manage-lede`

Change the countries and topics you get alerts for, add another, or remove them all.

*(Added in the build, 2026-09-16. Every page here carries a lede under its `<h1>`, and
without one of its own the manage page was running the sign-up page's — an invitation to
subscribe, shown to somebody who already has. `## manage` stays on the sign-up page, where
saying that every email carries a manage link is news; on the manage page it is a sentence
telling the reader where they already are.)*

### `## manage-empty`

You have no alerts set up. Add one below.

### `## manage-saved`

Saved. Your next Monday email will use the alerts above.

### `## manage-none`

You have no alerts left, so we will send you nothing. Your address stays on the list. To remove it, use the unsubscribe link in any email from us.

### `## feed`

Use a feed reader? Copy this address instead. It shows the same documents and needs no email address.

### `## privacy`

Your email address is held by Buttondown, the service that sends the alerts, and used only to send them. This site does not store it. Buttondown's privacy policy: https://buttondown.com/legal/privacy

### `## ok`

Check your inbox. Click the link in the email from Data Landscapers to start your alert.

### `## e-check`

The check that you are not a robot did not complete. Please try again.

### `## e-input`

Pick a country, a topic or the main-site box, and check the email address.

### `## e-later`

Something went wrong on our side. Please try again later.

### The digest body (built by the Worker, B5 step 5)

```
New this week for your alerts.

{% if "alert site" in subscriber.tags %}
## New on data-landscapers.io

**[{title}]({url})**
{description}
{% endif %}

{% if "alert 4f1c8a20b3" in subscriber.tags %}
## Kenya, Nigeria · Artificial intelligence

**[{title}]({url})**
{publisher} · published {published}

…and 11 more in the catalogue: https://corpus.data-landscapers.io/catalogue/#places=KEN,NGA&topics=tech.ai
{% endif %}

---
Change or stop your alerts: https://corpus.data-landscapers.io/alerts/manage/#s={{ subscriber.id }}
```

One `{% if %}` block per non-empty alert, the main-site section first. The Worker writes the items in; only `subscriber.tags` and `subscriber.id` are left for Buttondown to render. Buttondown adds the unsubscribe footer itself.

---

## Part 3 — Decisions

**Buttondown, not a mail system of our own.** An address list is a user record, and `design.md` §1 rules one out on this site. Buttondown already holds the main site's list and handles consent, confirmation, unsubscribe and bounces.

**Buttondown kept, 2026-09-15.** Bill finds its interface confusing, so MailerLite, Mailchimp, Kit and EmailOctopus were compared. Under this design the comparison matters much less than it did — what is needed is a tagged list, a template that can test a tag, and an API send — but moving would still mean moving the main list for no gain in the part Bill touches, which here is A, D and two Monday drafts.

**One newsletter, alerts only (Bill, 2026-09-15).** Bill writes no newsletter; the main list only ever received automated alerts of new writing, so it is one more alert and belongs in the same list. One newsletter means one set of settings, one confirmation email and one place to unsubscribe. The cost is that existing subscribers must be tagged `alert site` once (A10) and every new main-site sign-up must carry the tag (B8).

**One email per reader, not one per alert (2026-09-16).** The rejected design gave every alert its own Buttondown RSS-to-email feed. It is recorded here because its three limits are what this design exists to remove: an alert could cover only **one** country and **one** topic, because every combination needed its own feed and 62 places by 38 topics is 2,456 of them; a reader with five alerts got **five** emails every Monday; and an alert could not be **edited**, only dropped in Buttondown's portal and set up again. Sections in one body cost one KV entry and one tag per combination instead, so several countries and topics per alert become free.

**Existing subscribers get a cadence change, not a no-change (Bill, 2026-09-16).** There are already a few subscribers on the list, set up to be alerted whenever new content is published, and Bill sends that alert himself. After this build they get the same content on a fixed weekly rhythm, bundled with any catalogue alerts they add, from a body the Worker wrote. Three things follow. **The main site's news is now up to six days late** — the price of one email per reader, and the reason a per-publication send is worth keeping in mind if that ever stings. **The old alert has to stop** (E4): both running means the same post twice. And **nobody is told** (Bill, 2026-09-16): the content is what they subscribed for, the rhythm is the only thing that moved, and a mail whose subject is *we are changing when we mail you* costs a reader more attention than the change does. Keeping the send in Bill's hands is a separate question from the cadence, and `SEND_MODE: draft` answers it without touching anything else.

**Five countries, five topics, ten alerts.** The caps keep the email readable and the tag count bounded. Turnstile and the vocabulary check stop a bot inventing definitions in bulk; unused definitions are pruned.

**Weekly, Monday 07:00 UTC — and UTC is the choice, not the default.** Cloudflare crons are UTC-only, so the alternative was editing the schedule at each daylight-saving boundary to hold 07:00 London. African timezones do not observe daylight saving, so for the readers this is for, a UTC-fixed send is the one that never moves; London is what drifts. Buttondown's own timezone setting (A4) is vestigial here and reads nothing.

Buttondown's pricing assumes at most one email a day to the whole list, and this design sends one. Measured on 2026-09-14, the busiest country (Nigeria) had 125 documents ingested in a week and the busiest topic 278, before the backfill rule. Per-item sending would be unreadable; so would an uncapped section, which is what the 25 is for.

**The backfill rule is 90 days, and it is needed.** Of the 12,472 records ingested in the 35 days to 2026-09-14, only 4,453 were published within 30 days of ingest, and 3,106 were over a year old. Without the rule an alert would be mostly archive material. Ninety days keeps late-found reports and drops the backfill.

**The Worker owns the send window.** `last_sent_through` makes a missed Monday catch up rather than drop items, `sent:<date>` makes a retried cron harmless, and `recent.json` carries 28 days so the catch-up has something to read. Buttondown's RSS polling gave none of the three, and its `skip_old_items` actively fought the ingest dates the feed carries.

**The subscriber id is the edit key.** The alternatives were accounts, which `design.md` §1 rules out, and Buttondown's own magic link, `POST /v1/subscribers/{id}/send-magic-link` — which does exist, so this is not a question of what Buttondown can send. It lands the reader in Buttondown's portal, which can unsubscribe them but cannot edit an alert definition, because the definition lives in Corpus's KV and the tag name is an opaque id. A forwarded email lets the recipient edit the sender's alerts; that is already true of Buttondown's own manage link, and it is the same harm as an unconfirmed tag-add.

**Tag-adds to an existing address are not reconfirmed.** Someone could add an alert to an address that already subscribes. The harm is one unwanted section in an email that carries a manage link. Guarding against it means a confirmation step per alert, which Buttondown does not offer without taking the subscriber out of their other alerts.

**Drafts for the first two Mondays, and `draft` is allowed to be permanent.** A template mistake reaches the whole list at once rather than one feed's subscribers. That is the real cost of one email per reader, and two hand-released drafts are what pays it. Bill already releases the main-site alert by hand, so `draft` is not a training mode for him — it is his current workflow over a body he no longer has to write, and `about_to_send` is an option he may simply never want.

**The archive is off.** `archival_mode: "disabled"` on every send. One body holds every reader's sections, and a web render has no subscriber to test, so the archive would publish all of them at a permanent URL.

**`recent.json` is published data only.** Its columns are a subset of `CSV_COLS` plus a hash, so the alert layer publishes nothing the catalogue download does not. KV holds alert definitions and dates, and no address ever.

**More Worker code, and that is the trade.** A cron handler, a body builder and two manage routes, against Buttondown reduced to a list and a sender. Every rule about what a reader receives is now in this repo, under the tests in B6, instead of in a feed's settings screen.

---

## Part 4 — What the spike must settle

Three of the five questions this design opened on 2026-09-15 are closed against Buttondown's own documentation, read 2026-09-16. They are recorded closed so nobody re-opens them mid-build:

- **The tag test in the template works, and it was the gate.** `subscriber.tags` is documented as "access to the tag **names** of a given subscriber", and the docs' own example is `{% if 'python' in subscriber.tags %}…{% elif 'html' in subscriber.tags %}…{% endif %}`. Names, not objects, so `{% if "alert <id>" in subscriber.tags %}` is the documented form.
- **`subscriber.id`** is documented as the subscriber's unique id, and `GET /v1/subscribers/{id_or_email}` takes an id, so the manage key needs no second lookup.
- **Neither the filter list nor the body has a documented cap.** `EmailFilterGroup.filters` is an unbounded array in the schema, and `EmailInput.body` carries no `maxLength` where `subject` carries 2000. The count is Corpus's to control in any case: at most one filter per alert with a subscriber, and at most 25 items per section.

**Settled in D9, 2026-09-16: ids.** Every filter carrying a tag name came back `422 Tag filters must be valid tag identifiers`. The Worker now reads `GET /v1/tags` at send time for the name-to-id map — so the key's scopes do cover tags — and refuses to build the email if any section's tag has no id. The question as it stood:

One question is left, and it is a single line of code either way:

- **Does an email filter on `subscriber.tags` take the tag's name or its id?** The schema types `value` as a plain string and gives no example. `Subscriber.tags` is a list of names, which makes the name the likely answer, but a 30-second check in D settles it: build one draft, look at the audience count Buttondown reports, and if it is zero, switch. The Worker stores both in `def:<id>`, so the switch is one constant.

**A14 may have answered it already.** The API key screen grants scopes per object and has no tags scope (Bill, 2026-09-16), so if `/v1/tags` returns 403 the Worker never holds a tag id and the filter must take names. Both resolve in D, and D's first sign-up is what decides them.

The key's scopes are no longer open: **subscribers read and write, emails read and write**, which is what A14 records.
