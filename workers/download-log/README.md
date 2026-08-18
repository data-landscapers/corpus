---
type: runbook
title: The download-log Worker — what it does and how to deploy it
last_reviewed: 2026-08-18
status: not yet deployed
---

# download-log

*(Set up 2026-08-18, straight after the `.io` move. It answers one question — **which dated editions do readers actually take?** — and it does nothing else yet. The rule that would eventually act on the answer is `documentation/delete-unless-downloaded.md`, and it is **not** switched on: nothing deletes anything, and nothing will until there is a month of evidence to decide on.)*

## What it does

Sees a request for a `.pdf` or `.csv` on `corpus.data-landscapers.io`, writes the file's path into a Cloudflare KV store with a first-seen date, a last-seen date and a count, and passes the request through untouched.

**It does not serve the file.** The response is fetched and returned whatever happens in the logging, so a Worker that breaks costs a missing log entry rather than a broken download. That asymmetry is the point: the record can be incomplete, never wrong in the direction that would one day delete a file somebody is holding.

**It logs no reader.** No IP address, no user-agent, no referrer, no session. The key is the path of the file; the value is when it was taken and how often. The user-agent is read once, in memory, to decide whether a hit was a crawler, and is not stored.

**Crawlers are counted separately, not excluded.** A bot causing a file to be kept costs storage; a real reader's download going unrecorded would eventually cost the file. So the two are split and whoever reads the numbers later can decide what to believe.

## Deploying it

*(Cloudflare's dashboard is reorganised often, so these are the things that have to be true rather than a promise about what the buttons are called. Screens moved twice during the `.io` move on the same day. **Bindings** and **Domains & Routes** sit alongside *Settings* on a Worker's page rather than inside it, and in older dashboards they are under it.)*

**Two deep links that skip the menus entirely**, and resolve to the right account on their own:

- KV namespaces — `https://dash.cloudflare.com/?to=/:account/workers/kv/namespaces`
- Workers — `https://dash.cloudflare.com/?to=/:account/workers`

**Both KV and Workers are account-level, not inside a domain.** If the left sidebar is showing `data-landscapers.io`, click the Cloudflare logo or the account name in the breadcrumb to come up a level; the zone sidebar does not carry either of them. The dashboard search box is quicker than hunting for the label, which is *Workers & Pages* in the older dashboard and *Compute (Workers)* in the newer one. The first Worker you create will also ask you to choose a `workers.dev` subdomain — pick anything, it is never used, since this Worker is bound to a route on your own domain.

**1. Create the KV namespace.** *Storage & Databases* → *KV* → *Create a namespace* → name it `downloads`.

**2. Create the Worker.** *Compute (Workers)* → *Create* → *Start from Hello World* → name it `download-log` → *Deploy*. Do not worry about what it does yet.

**3. Paste the code.** Open the Worker → *Edit code* → select everything in the editor and replace it with the contents of `worker.js` beside this file → *Deploy*.

**4. Bind the namespace.** Worker → *Bindings* → *Add* → **KV namespace** → **Variable name `DOWNLOADS`** (exactly that, in capitals — the code looks for `env.DOWNLOADS`) → namespace `downloads` → *Deploy*.

**5. Put it on the route.** Worker → *Domains & Routes* → *Add* → *Route* → zone `data-landscapers.io`, route `corpus.data-landscapers.io/*`.

**The route covers everything rather than just the download directories**, and the Worker filters by file extension instead. One route cannot miss a directory added later, and the free allowance is 100,000 requests a day against a site that will not approach it. The cost is that the Worker runs on page views too and returns them untouched.

**6. Check it.** Download any PDF from the site, wait a few seconds, then open *KV* → `downloads` → the key should be there, named for the path — `reports/KEN/KEN-status-2026-08-18.pdf` — with a value like `{"first":"2026-08-18","last":"2026-08-18","n":1,"bots":0}`.

### If the Bindings screen offers no fields

*(2026-08-18: it showed Cloudflare's KV sample code and nothing to fill in.)* **Declare the binding in the Worker's configuration file instead**, which is where the dashboard would have put it anyway.

Get the namespace's ID first: *KV* → the `downloads` namespace → it is the 32-character hex string shown as **Namespace ID** (also the last part of the page's URL).

Then open the Worker → *Edit code* → in the file list find **`wrangler.jsonc`** (or `wrangler.toml`). Leave `name`, `main` and `compatibility_date` alone and add one block:

```jsonc
  "kv_namespaces": [
    { "binding": "DOWNLOADS", "id": "<the 32-character namespace id>" }
  ]
```

In `wrangler.toml` the same thing is written:

```toml
[[kv_namespaces]]
binding = "DOWNLOADS"
id = "<the 32-character namespace id>"
```

Deploy. `binding` is the variable name the code reads, so it must stay `DOWNLOADS`; `id` says which namespace it points at. Mind the comma placement in the JSON — a block added after an existing entry needs a comma before it.

**If nothing appears**, the binding name is the thing to check first: the code reads `env.DOWNLOADS` and does nothing at all if that binding is absent, by design, so a mistyped variable name fails silently and safely.

## Reading it

For now, in the dashboard: *KV* → `downloads` → the key list is the answer to *what has been taken*.

Nothing on this machine reads it yet, and nothing should until the deletion rule is decided. When that happens the reader needs a Cloudflare API token with KV read scope, which is a secret and must live outside git — an environment variable or a gitignored file, never a constant in a script.

## What it deliberately does not do

- **It does not delete anything.** `documentation/delete-unless-downloaded.md` describes the rule; this is the evidence-gathering that comes first.
- **It does not mint, copy or move files.** Nothing is archived on download; the archive, if it ever exists, is `site/` continuing to hold what it already holds.
- **It does not log HTML page views.** Those are the browsable surface, not editions, and counting them is a different question with a different tool.
- **It does not run on `data-landscapers.com`.** Requests there are redirected at the edge before any origin is reached, so a download that begins on the old domain is logged when it lands on the new one.
