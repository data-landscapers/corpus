---
type: design-note
title: catalogue-alerts-digest.md — alternative to catalogue-alerts.md: one weekly email per reader, built by the Worker
last_reviewed: 2026-09-15
status: proposed by Cowork 2026-09-15 for CC to weigh against catalogue-alerts.md; not decided
---

# Catalogue alerts — the digest alternative

`catalogue-alerts.md` gives each alert its own Buttondown RSS feed. That design has three limits Bill has asked about: an alert covers **one** country and **one** topic; a reader with five alerts gets **five** emails every Monday; and an alert **cannot be edited**, only dropped in Buttondown's portal and set up again. This note is the alternative that removes all three. Everything in `catalogue-alerts.md` not named here stands: `recent.json`, `vocab.json`, the backfill rule, the feed endpoint for feed readers, Turnstile, the no-logging rule, one `data-landscapers` newsletter, and the site storing no addresses.

**The change in one line.** The Worker builds one weekly email and hands it to Buttondown to send. Each alert is a section of that email, shown only to subscribers who carry the alert's tag. Buttondown stops needing a feed per alert, and each reader gets one email covering everything they follow.

CC: weigh this against `catalogue-alerts.md`, write the verdict at the top of whichever note loses, and fold the winner into `design.md` §6. The open questions that decide it are in *What must be proved first*.

---

## How it works

**An alert is a catalogue selection.** A set of countries (1–5, or Any) and a set of topics (1–5, or Any), matched the way the catalogue matches: a document matches if it carries **any** of the alert's countries **and any** of its topics. The main-site alert is a fixed alert with the id `site`. A reader may hold up to **10** alerts.

**Each alert has an id and a tag.** The id is the first 10 hex characters of the SHA-256 of the canonical definition, `P=<places sorted, comma-joined or any>|T=<topics sorted, comma-joined or any>`. The same selection always gets the same id, so two readers who want "Kenya, Nigeria · AI" share one tag. The tag is named `alert <id>`, with the alert's label as its public description. KV `ALERT_DEFS` maps id → `{places, topics, label, created}`. **KV holds definitions only, never an address**; a definition is no more personal than a catalogue URL.

**Which alerts a reader has lives in Buttondown**, as their tags, exactly as in `catalogue-alerts.md`. Tags are **not** subscriber-editable any more: their names are opaque ids, and editing happens on the site's own page (below). Buttondown's portal is left on for unsubscribing.

**The weekly send** is a Cloudflare Cron Trigger on the same Worker, `0 7 * * 1` (Monday 07:00 UTC):

1. Read KV `last_sent_through` (a date). The window is the day after it to yesterday, capped at 21 days. First run: the last 7 days.
2. Fetch `recent.json` (now **28** days, up from 14, so a missed week or two is caught up rather than lost) and the main site's `feed.json` (B-new-2).
3. List the alert tags that have at least one active subscriber (`GET /v1/tags`, then a subscriber count per tag; if the API gives no per-tag count, `GET /v1/subscribers?tag=<name>&page_size=1` and read `count`).
4. For each such alert, select the window's records that match its definition, newest `ingested` first. Drop alerts with no match.
5. Build one Markdown body: a short opening line, then for each non-empty alert a section wrapped in `{% if "alert <id>" in subscriber.tags %}` … `{% endif %}` with the alert's label as a heading, up to **25** items, and when there are more, *and N more in the catalogue* linking to `SITE/catalogue/#places=<…>&topics=<…>` (the catalogue's own fragment, comma-joined). The main-site section uses `alert site` and the posts in `feed.json` dated inside the window. The footer carries the manage link (below) and Buttondown's own unsubscribe footer.
6. `POST /v1/emails` with the subject **Data Landscapers alerts — week of <Monday's date>**, the body, `status` from the variable `SEND_MODE` (`draft` or `about_to_send`), and `filters` = `{"predicate": "or", "groups": [], "filters": [one {"field": "subscriber.tags", "operator": "contains", "value": "<tag id>"} per non-empty alert]}`. A reader none of whose alerts matched is outside the filter and gets **no email**, which keeps *No new documents, no email*.
7. Write `last_sent_through` = yesterday and `sent:<date>` = the email's id. If `sent:<date>` already exists the run stops at step 1, so a retried cron cannot send twice.
8. If nothing matched at all, write `last_sent_through` and send nothing.

`SEND_MODE` starts at `draft`: for the first two Mondays Bill opens **Emails → Drafts**, previews it as a few subscribers (Buttondown's *subscriber preview*), and sends it himself. Then it goes to `about_to_send`.

**Managing alerts.** Every email carries `https://corpus.data-landscapers.io/alerts/manage/#s={{ subscriber.id }}`. The subscriber id is Buttondown's UUID and works as the key, the same way Buttondown's own manage and unsubscribe links do. It travels in the fragment, so it never reaches a server log; the page's script sends it in a POST body.

- `POST /api/alerts/manage/list` `{s}`: the Worker fetches the subscriber from Buttondown, keeps its `alert …` tags, looks each up in `ALERT_DEFS`, and returns `[{id, places, topics, label}]` plus whether `site` is held. **It does not return the email address.**
- The page shows each alert as an editable row (the same country and topic pickers as the sign-up form), a delete button per row, an **Add alert** button up to 10, and the main-site checkbox.
- `POST /api/alerts/manage/save` `{s, alerts: [{places, topics}], site, cf-turnstile-response}`: Turnstile, validate against `vocab.json`, compute each id, create any missing tag and `ALERT_DEFS` entry, then `PATCH /v1/subscribers/<s>` with the subscriber's non-alert tags plus the new alert tags. Saving with no alerts leaves the address subscribed and sent nothing; the page says so and points to the unsubscribe link in any email to remove the address.

**Signing up** changes only in the pickers: country and topic become multi-selects of up to 5 each, and a catalogue link carrying several values preselects all of them (up to 5; beyond that the page shows the *several* note). The Worker computes the id, creates the tag and `ALERT_DEFS` entry if new, and adds the tag as before. Creating an external feed is gone. An existing address that signs up again gets the alert added, as before.

---

## What changes against catalogue-alerts.md

- **Part A.** No RSS feed for the main site (A13–A14 go; any existing main-site RSS automation is deleted once the digest has sent once, or readers get the main site twice). The account is on Buttondown's **Standard** plan (Bill, 2026-09-15), which covers automations and custom domains; this design needs neither automations nor RSS-to-email, but it does need **Tagging & segmentation**, which Standard includes through Basic (Bill, 2026-09-15), and API sending. The newsletter should send from a `data-landscapers.io` address, as in `catalogue-alerts.md` A5. `alert site` is created with subscriber-editable **off**. The API key needs write for `subscriber_access` and for sending emails (`emails_access` or whatever the key screen calls it; check against `openapi.json`); `automations_access` is no longer needed.
- **B3.** `recent.json` covers 28 days. The pickers are multi-selects. New file `site/alerts/manage/index.html`.
- **B5.** No `/external_feeds` call. Three new routes (`manage/list`, `manage/save`, the cron handler). New KV keys: `ALERT_DEFS` entries, `last_sent_through`, `sent:<date>`. New variable `SEND_MODE`. The cron trigger is set in the Worker's **Settings → Triggers**.
- **B-new-2 (data-landscapers).** Add `feed.json`, a Liquid-built JSON twin of `feed.xml` (`title`, `url`, `date`, `description` for the last 20 posts), so the Worker needs no XML parser. B8's hidden `tag` field stays.
- **Tests.** Add: the alert id is stable under reordering; matching with several places and topics; the body for a set of alerts matches a golden file; the `or` filter lists exactly the non-empty alerts; a retried cron sends nothing; `manage/list` never returns an email address; `manage/save` keeps non-alert tags.
- **Part D.** Replace the feed-poll steps with: run the cron by hand (`wrangler` or the dashboard's *Trigger* button) with `SEND_MODE=draft`; preview the draft as a subscriber with one alert, one with three, and one with only `alert site`; check each sees only their sections; edit an alert on the manage page and check the tags in Buttondown.
- **Part 2 text.** `## what` becomes: *Each alert can cover up to five countries and five topics; a document matches if it is about any of the countries and any of the topics. You can hold up to ten alerts. They all arrive together, in one email on Monday.* `## several` changes its threshold to five. New blocks for the manage page: `## manage-title`, `## manage-empty`, `## manage-saved`.
- **Later list.** *Portal clutter* goes: tags are no longer shown in the portal. *Removing unused feeds* becomes removing `ALERT_DEFS` entries whose tag has no subscriber, and the tag with it.

---

## What must be proved first

These are unverified against Buttondown's documentation as read on 2026-09-15, and each one decides the design. A one-hour spike with a test tag and two test subscribers settles them before any build.

1. **Tag test in the template.** The docs list `subscriber.tags` as a template variable and use Django templating, but give no example of `{% if "alert x" in subscriber.tags %}`. If `tags` is a list of names this works; if it is a list of objects the test has to be different. **If no form works, this design fails**, and `catalogue-alerts.md` stands.
2. **`subscriber.id`** in the template is the id that `GET /v1/subscribers/{id}` accepts.
3. **Filter size.** An `or` filter with many tag conditions (try 200) is accepted by `POST /v1/emails`. If there is a cap, the fallback is to send to every subscriber with any alert tag and add an `{% if %}` line reading *Nothing new for your alerts this week*, which breaks *No new documents, no email*.
4. **Body size.** A body with a few hundred conditional sections sends. Buttondown documents no limit. If there is one, lower the per-alert cap from 25.
5. **Plan.** The account is on Standard, which includes tagging. Confirm it allows API-created emails sent with `about_to_send`. If this design wins, check whether Standard's automations are still worth paying for, since nothing here uses them.

---

## Decisions

**One email per reader, not one per alert.** Five alerts meant five Monday emails. One email with sections is what a reader with several interests wants, and it matches Buttondown's pricing assumption of at most one email a day.

**Several countries and topics per alert, capped at five each and ten alerts.** The per-feed design could not allow them, because every combination needed its own Buttondown feed. Here a combination costs one KV entry and one tag. The caps keep the email readable and the tag count bounded; Turnstile and the vocabulary check still stop a bot inventing definitions in bulk, and unused definitions are pruned.

**The subscriber id is the edit key.** The alternatives were accounts, which `design.md` §1 rules out, or an emailed magic link, which needs a transactional send Buttondown does not offer per request. A forwarded email lets the recipient edit the sender's alerts; the same is already true of Buttondown's own manage link, and the harm is the same as in `catalogue-alerts.md`'s decision on unconfirmed tag-adds.

**The Worker owns the send window.** `last_sent_through` makes a missed Monday catch up rather than drop items, and `sent:<date>` makes a retry harmless. Buttondown's RSS polling gave neither.

**Drafts first.** The first two sends are drafts Bill releases by hand, because a template mistake here goes to everyone at once rather than to one feed's subscribers.

**Cost of the change.** More Worker code (a cron handler, a body builder, two manage routes) and more to test. In return Buttondown is only a list and a sender, and every rule about what a reader receives lives in this repo, under its tests.
