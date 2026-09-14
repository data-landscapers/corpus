---
type: design-note
title: catalogue-alerts.md — email alerts for one country and one topic, through Buttondown
last_reviewed: 2026-09-14
status: specified, not built; Bill implements the week of 2026-09-21
---

# Catalogue alerts

A reader picks a country, a topic, or both, and gets a weekly email listing the new documents that match. The **Get alerts** button on the catalogue page opens it.

**How it works.** The site publishes a small file of recent records. A Cloudflare Worker turns that file into a filtered Atom feed for each place-and-topic pair. When a reader subscribes to a pair, the Worker tags them in Buttondown and creates a Buttondown RSS-to-email feed for that pair if none exists yet. From then on Buttondown sends the email. **The site stores no addresses.** Buttondown holds them, as it already does for the main site. That keeps `design.md` §1 (no user record) true.

Part 1 is the build, in order. Part 2 is the reader-facing text, ready to paste. Part 3 records the decisions, so nobody reopens them during the build.

---

## Part 1 — Implementation

Parts A, C, D and E are Bill's. Part B is code, for a CC session given the brief in B1. Every Buttondown API detail below was checked against Buttondown's own schema (`https://docs.buttondown.com/openapi.json`) on 2026-09-14. If a call fails, check that schema first.

### A. Buttondown setup (Bill, about 30 minutes)

Menu names are Buttondown's as documented on 2026-09-14; if a screen has moved, search its docs for the setting.

1. Log in to Buttondown.
2. Open **Settings → Billing**.
3. Confirm the account has **Tagging & segmentation** and **RSS-to-email**. Add either one that is missing.
4. Create a new newsletter named **Corpus alerts**.
5. In the new newsletter, open **Settings → Basic**.
6. Set the sender name to **Corpus**.
7. Set the timezone to **UTC**.
8. Set the description to: *Weekly alerts of new documents in the Corpus catalogue.*
9. If the main newsletter sends from a custom domain, set up the same sending domain here.
10. Open **Settings → Subscribing** and confirm double opt-in is on.
11. Replace the confirmation email text with the text in Part 2, *Confirmation email*.
12. Open **Settings → Portal** and confirm the subscriber portal is on.
13. Open **API → Keys**.
14. Create a key labelled **corpus-alerts-worker**.
15. Give it **write** for `subscriber_access` and `automations_access`, and **none** for everything else. If D6 fails and the Worker's log shows a 403 from `/external_feeds`, add write for `administrivia_access`.
16. Copy the key into your password manager. It is used in C6.

### B. Build (CC session)

1. Start a fresh CC session in `C:\CORPUS` with this brief: *"Build catalogue alerts per `documentation/catalogue-alerts.md` Part 1 B, then stop for Bill's deploy."*
2. CC builds B3–B7, runs RENDER's catalogue step, and commits and pushes.
3. **`scripts/alerts.py`** writes three files, and RENDER runs it straight after `catalogue.py`, with a line added to `RENDER.md` Step 5:
   - **`site/alerts/recent.json`**: the records ingested in the last **14 days** that pass the **backfill rule**. A record passes if the end of its publication period is no more than **90 days** before its `ingested` date. The period is the day, the month or the year, according to `date_precision`. Records with no `published` date are excluded. Each row carries `id`, `title`, `publisher`, `published`, `ingested`, `places` (array), `topics` (array) and `url`. `id` is the first 16 hex characters of the SHA-256 of `url`, or of `title|publisher|published` when there is no URL. The source is `outputs/catalogue/raw-catalogue.json`, and only columns already in `CSV_COLS` are used, so nothing unpublished leaks.
   - **`site/alerts/vocab.json`**: `{places: {code: label}, topics: {slug: label}}`, taken from `catalogue.py` → `vocab()` so the labels match the catalogue's menus. Places include the region codes (`XWA`, `XAF`, `XGL` and so on), as the catalogue's place facet does.
   - **`site/alerts/index.html`**: the reader page, in the site's chrome, with its text drawn from **`content/alerts.md`** through `copy_lib` (Part 2 gives the blocks). The page has:
     - two `<select>`s, Country and Topic, filled from `vocab.json` at build time, each with an **Any** option;
     - an email field;
     - a Cloudflare Turnstile widget (site key from C3, written in as a constant);
     - a submit button that posts to `/api/alerts/subscribe`.

     A small script reads the fragment (`#places=KEN&topics=tech.ai`, the catalogue's own keys) and preselects the first value of each. If the fragment carries more than one value for either, it shows the *more than one* note. Submitting with both set to Any is refused in the page. A second, collapsed section gives the plain feed URL for the current selection, for readers who use a feed reader.
4. **Catalogue button.** In `catalogue.py`, add a row to the downloads box under *This selection*: **Get alerts**, a `.btn btn--sm` link to `../alerts/`. The page's script rewrites its `href` on every redraw to carry the current `places` and `topics` as a fragment. It stays enabled with nothing selected and then opens the alerts page blank.
5. **`workers/alerts/worker.js`** is a new Worker, separate from `download-log`. `workers/alerts/README.md` is a pointer to this file. Bindings: KV `ALERT_FEEDS`; secrets `BUTTONDOWN_API_KEY` and `TURNSTILE_SECRET`; variable `SITE` = `https://corpus.data-landscapers.io`. Two routes:
   - **`GET /api/alerts/feed?place=KEN&topic=tech.ai`** (either parameter may be omitted, not both):
     - reject a code not in `vocab.json` with 400;
     - fetch `recent.json` and `vocab.json` from `SITE`, cached 15 minutes;
     - keep the rows where `places` contains `place` (if given) and `topics` contains `topic` (if given);
     - sort newest `ingested` first and cap at 200;
     - return Atom 1.0 (`application/atom+xml`), cached 30 minutes in `caches.default`.

     The feed title is `Corpus: <place label> · <topic label>`, or just the one label. Each entry has:
     - `<id>`: `tag:corpus.data-landscapers.io,2026:<id>`;
     - `<title>`: the title;
     - `<link href>`: `url`, or `SITE/catalogue/#q=<encoded title>` when `url` is empty;
     - `<updated>` and `<published>`: `ingested` at `T00:00:00Z`;
     - `<summary>`: `<publisher> · published <published>`.

     An empty result is still a valid feed with no entries.
   - **`POST /api/alerts/subscribe`** (form-encoded: `email`, `place`, `topic`, `cf-turnstile-response`):
     1. Verify Turnstile at `https://challenges.cloudflare.com/turnstile/v0/siteverify`, passing the client IP. On failure, redirect 303 to `/alerts/?e=check`.
     2. Validate `place` and `topic` against `vocab.json` (at least one set) and the email's shape. On failure, redirect 303 to `/alerts/?e=input`.
     3. Pair key: `<place or any>|<topic or any>`. Tag name: `alert <place or any> <topic or any>`, e.g. `alert KEN tech.ai`.
     4. `POST https://api.buttondown.com/v1/tags` with header `X-Buttondown-Collision-Behavior: overwrite` and body `{name, color: "#1a5f7a", public_description: "<place label> · <topic label>", subscriber_editable: true}`. Take the tag's `id` from the response.
     5. Look up `ALERT_FEEDS` for the pair key. If it is absent, `POST /v1/external_feeds` with the body below, then store the returned feed `id` under the pair key.
     6. `POST /v1/subscribers` with header `X-Buttondown-Collision-Behavior: add` and body `{email_address, tags: [tag name], ip_address: <client IP>, referrer_url: SITE + "/alerts/"}`. A new address gets Buttondown's confirmation email. An existing one has the tag added.
     7. Redirect 303 to `/alerts/?ok=1`. On any Buttondown error, redirect 303 to `/alerts/?e=later` and do nothing else.

     All Buttondown calls send `Authorization: Token <BUTTONDOWN_API_KEY>`. **The Worker never logs, stores or echoes the email address.** No `console.log` of the request body.

   The external feed body:

   ```json
   {
     "url": "https://corpus.data-landscapers.io/api/alerts/feed?place=KEN&topic=tech.ai",
     "label": "KEN|tech.ai",
     "behavior": "emails",
     "cadence": "weekly",
     "cadence_metadata": {"weekday": "monday", "time": "7"},
     "skip_old_items": false,
     "filters": {"predicate": "and", "groups": [],
                 "filters": [{"field": "subscriber.tags", "operator": "contains", "value": "<tag id>"}]},
     "subject": "Corpus: new documents, Kenya · Artificial intelligence",
     "body": "<the digest template in Part 2>"
   }
   ```

   `skip_old_items` must stay **false**. Buttondown's version skips anything dated more than a day before it sees it, and the feed's dates are ingest dates, which a weekly poll would often miss. The backfill rule in `alerts.py` does that job.
6. **Tests** (in `scripts/`, the house pattern):
   - the backfill rule at each `date_precision`;
   - the `id` for a row with and without a URL;
   - the feed filter with place only, topic only and both;
   - Atom validity of an empty and a full feed;
   - that `recent.json` carries no key outside `CSV_COLS` plus `id`.
7. Commit the build. Push. Leave `workers/alerts/worker.js` for Bill to paste in C.

### C. Cloudflare setup and deploy (Bill, about 30 minutes)

1. Open the Cloudflare dashboard.
2. Go to **Turnstile → Add widget**.
3. Name it **corpus-alerts**, add hostname `corpus.data-landscapers.io`, mode **Managed**. Copy the site key and the secret key.
4. Give the site key to the CC session. It goes into `alerts.py`; re-render, commit and push.
5. Go to **Workers & Pages → Create → Worker**. Name it **corpus-alerts**. Deploy the placeholder.
6. Open the Worker's **Settings → Variables and Secrets**. Add secret `BUTTONDOWN_API_KEY` (from A16), secret `TURNSTILE_SECRET` (from C3) and text variable `SITE` = `https://corpus.data-landscapers.io`.
7. Go to **Storage & Databases → KV → Create namespace**. Name it `alert-feeds`.
8. In the Worker's **Settings → Bindings**, add a KV binding: variable name `ALERT_FEEDS`, namespace `alert-feeds`.
9. Open the Worker's **Edit code**. Paste `workers/alerts/worker.js`. Deploy.
10. In the Worker's **Settings → Domains & Routes**, add route `corpus.data-landscapers.io/api/alerts/*` on zone `data-landscapers.io`. It is more specific than `download-log`'s `/*`, so it wins for those paths and nothing else changes.

### D. Test before going live (Bill, with the CC session)

1. Open `https://corpus.data-landscapers.io/api/alerts/feed?place=KEN`. Expect an Atom feed with entries.
2. Open `https://corpus.data-landscapers.io/api/alerts/feed?place=ZZZ`. Expect a 400.
3. Open `https://corpus.data-landscapers.io/catalogue/#places=KEN&topics=tech.ai`.
4. Click **Get alerts**. Expect the alerts page with Kenya and the AI topic already selected.
5. Enter your own email address and submit.
6. Expect the page's *check your inbox* message.
7. Expect Buttondown's confirmation email. Click the confirm link.
8. In Buttondown (Corpus alerts), open **Subscribers**. Expect your address with the tag `alert KEN tech.ai`.
9. Open **Automations → RSS**. Expect one feed labelled `KEN|tech.ai`.
10. Change that feed's behaviour to **Draft**.
11. Force a poll: `curl -X POST -H "Authorization: Token <key>" https://api.buttondown.com/v1/external_feeds/<feed id>/items`.
12. Open **Emails → Drafts**. Expect a digest draft. Check the subject, the links and the footer.
13. Submit the form again with the same address and pair. Expect no second feed and no second tag.
14. Change the feed's behaviour back to **Emails**.
15. Check the Worker's **Logs** tab. Expect no email address anywhere.

### E. Go live (Bill)

1. Tell the CC session the tests passed.
2. The session updates `design.md` §6 to say alerts are built, and logs the run.
3. Optionally, announce it in the main Buttondown newsletter with a link to `https://corpus.data-landscapers.io/alerts/`.

### Later, not in this version

- **Report editions as alert items**: a new status or progress report for a country going into that country's alerts.
- **Removing unused feeds**: a monthly pass that deletes any external feed whose tag has no active subscriber, and its KV entry.
- **A monthly cadence**, if readers ask for one.
- **Portal clutter**: once there are more than about 50 alert tags, reconsider `subscriber_editable`, since every editable tag shows in every subscriber's portal.

---

## Part 2 — Reader-facing text

Blunt, per the site's copy rules. The page blocks go into `content/alerts.md` under these headings.

### `## title`

Alerts

### `## lede`

Get an email when new documents about your country or topic reach the catalogue. Free, weekly, and you can stop at any time.

### `## how`

1. Pick a country, a topic, or both.
2. Enter your email address.
3. Confirm from the email we send you.

You then get one email a week, on Monday, listing the new documents that match. No new documents, no email.

### `## what`

Each alert covers one country and one topic. Choose **Any** for either to widen it. To follow more than one, set up another alert with the same email address.

An alert lists documents published in roughly the last three months as they reach the catalogue. Older documents we add to the archive are not sent; find those in the catalogue.

A region, such as West Africa, covers documents about the region as a whole, not every document about each country in it.

### `## several`

Alerts follow one country and one topic. Your selection had more than one, so pick the ones you want below.

### `## manage`

Every alert email has a link to manage your subscription. Use it to drop one alert and keep the others, or to stop all of them.

### `## feed`

Use a feed reader? Copy this address instead. It shows the same documents and needs no email address.

### `## privacy`

Your email address is held by Buttondown, the service that sends the alerts, and used only to send them. This site does not store it. Buttondown's privacy policy: https://buttondown.com/legal/privacy

### `## ok`

Check your inbox. Click the link in the email from Corpus to start your alert.

### `## e-check`

The check that you are not a robot did not complete. Please try again.

### `## e-input`

Pick a country or a topic, and check the email address.

### `## e-later`

Something went wrong on our side. Please try again later.

### Confirmation email (Buttondown, A11)

Subject: **Confirm your Corpus alert**

> You asked for weekly emails about new documents in the Corpus catalogue.
>
> Confirm here: {{ confirmation_url }}
>
> If this wasn't you, ignore this email and nothing will be sent.

Keep whatever confirmation-link variable Buttondown's default template uses if it differs from `{{ confirmation_url }}`; copy it from the default before replacing the text.

### Digest template (the `body` in B5)

```
New in the Corpus catalogue this week, for **{PAIR LABEL}**:

{% for item in items %}
**[{{ item.title }}]({{ item.url }})**
{{ item.description }}

{% endfor %}
Browse everything: https://corpus.data-landscapers.io/catalogue/{FRAGMENT}
```

The Worker fills in `{PAIR LABEL}` (e.g. *Kenya · Artificial intelligence*) and `{FRAGMENT}` (e.g. `#places=KEN&topics=tech.ai`) when it creates the feed. Buttondown adds the unsubscribe and manage-subscription footer itself.

---

## Part 3 — Decisions

**Buttondown, not a mail system of our own.** An address list is a user record, and `design.md` §1 rules one out on this site. Buttondown already holds the main site's list and handles consent, confirmation, unsubscribe and bounces.

**A separate newsletter.** Alert subscribers and main-site readers are different lists with different expectations. Buttondown charges by total subscribers, not per newsletter.

**Feeds are created when someone asks for one.** 62 places and 38 topics, each with an Any option, make 2,456 possible alerts. Creating them all would fill the account with feeds nobody reads, and Buttondown cannot filter one feed per subscriber. The ceiling stays 2,456 whatever a bot submits, because codes are checked against the vocabulary; Turnstile covers the rest.

**Weekly, Monday 07:00 UTC.** Buttondown's pricing assumes at most one email a day to the whole list. Measured on 2026-09-14, the busiest country (Nigeria) had 125 documents ingested in a week and the busiest topic 278, before the backfill rule. Per-item sending would be unreadable.

**The backfill rule is 90 days, and it is needed.** Of the 12,472 records ingested in the 35 days to 2026-09-14, only 4,453 were published within 30 days of ingest, and 3,106 were over a year old. Without the rule an alert would be mostly archive material. Ninety days keeps late-found reports and drops the backfill.

**Tag-adds to an existing address are not reconfirmed.** Someone could add an alert to an address that already subscribes. The harm is one unwanted weekly email with a manage link in it. Guarding against it means a confirmation step per alert, which Buttondown does not offer without taking the subscriber out of their other alerts.

**`recent.json` is published data only.** Its columns are a subset of `CSV_COLS` plus a hash, so the alert layer publishes nothing the catalogue download does not.
