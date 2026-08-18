---
type: runbook
title: The download-log Worker — what it does and how to deploy it
last_reviewed: 2026-08-18
status: deployed and verified 2026-08-18 — archived, superseded by documentation/cloudflare.md
---

> **Archived 2026-08-18.** What the Worker does, where it is bound and what it stores is in **`documentation/cloudflare.md`**, which is the file to read and to keep current. This one is kept for the deployment account: the dashboard path taken, the binding screen that offers no fields, the `wrangler.jsonc` fallback, and the first verification. Cloudflare moves those screens often, so treat the button names here as a record of one afternoon rather than as instructions.

# download-log

*(Set up 2026-08-18, straight after the `.io` move. It answers one question — **which dated editions do readers actually take?** — and it does nothing else. The rule that acts on the answer is `documentation/archived/delete-unless-downloaded.md`, implemented the same day in `scripts/prune-editions.py` and run by RENDER Step 6a: a superseded edition is deleted unless somebody downloaded it, PDFs and CSVs, **forward only**. The month of evidence this file first said to wait for is not owed, because forward-only makes the waiting automatic — the rule can touch nothing published before the Worker existed, so its first candidate is an edition the Worker itself watched from the day it was minted.)*

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

**3. Paste the code.** Open the Worker → *Edit code* → select everything in the editor and replace it with the contents of `workers/download-log/worker.js` → *Deploy*.

**4. Bind the namespace.** Worker → *Bindings* → *Add binding*. **This is a two-step wizard and the first step has no fields** — it shows a list of binding types on the left and a description of the highlighted one on the right, sample code included. That sample says `env.KV` because it documents KV in general, not this Worker. Select **KV namespace**, then press the blue **Add Binding** button; the form appears on the *next* screen. On it: **Variable name `DOWNLOADS`** (capitals — the code looks for `env.DOWNLOADS`) and namespace `downloads`. *(This cost half an hour on 2026-08-18: the first screen reads as a dead end.)* The old path was: Worker → *Settings* → *Bindings* → *Add* → **KV namespace** → **Variable name `DOWNLOADS`** (exactly that, in capitals — the code looks for `env.DOWNLOADS`) → namespace `downloads` → *Deploy*.

**5. Put it on the route.** Worker → *Domains* → *Add Route* → pick the zone `data-landscapers.io` → route pattern `corpus.data-landscapers.io/*`.

**Correct the pattern it offers.** It pre-fills `*.data-landscapers.io/*`, which puts the Worker in front of *every* subdomain including any added later. Replace it with the corpus hostname.

**Check the deployed code before adding the route, not after.** The route is the moment the Worker starts answering for the whole site: if the Hello World template is still deployed, every page becomes the words *Hello World*. Worker → *Edit code* → confirm `record(` and `env.DOWNLOADS` are there and the editor reports 0 errors.

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

**Verified working on 2026-08-18**, first try: the two test fetches produced

```
countries/KEN/KEN-nonstate-2026-08-18.csv   {"first":"2026-08-18","last":"2026-08-18","n":0,"bots":1}
reports/KEN/KEN-status-2026-08-18.pdf       {"first":"2026-08-18","last":"2026-08-18","n":0,"bots":1}
```

**`n:0, bots:1` is the crawler split doing its job** — the tests were made with `curl`, which the user-agent check catches. A browser download lands in `n`. The two HTML pages fetched in the same run produced no keys at all, which is the extension filter doing its job.

**If nothing appears**, the binding name is the thing to check first: the code reads `env.DOWNLOADS` and does nothing at all if that binding is absent, by design, so a mistyped variable name fails silently and safely.

## Reading it

In the dashboard: *KV* → `downloads` → the key list is the answer to *what has been taken*.

**`scripts/prune-editions.py` reads it too, and acts on it** *(2026-08-18, the same day: Bill's call to implement the rule for PDFs and CSVs, forward only)*. It asks for the **key list alone** and never for the values — presence of a key is the whole test, because any fetch at all protects a file, a crawler's included. That is `documentation/archived/delete-unless-downloaded.md` in force; RENDER Step 6a runs it.

**It needs a Cloudflare API token with KV read scope**, which is a secret and must live outside git — never a constant in a script. Create it at *My Profile* → *API Tokens* → *Create Token* → *Custom token*, with the single permission **Account · Workers KV Storage · Read** on this account. Then supply it, with the account ID and the `downloads` namespace ID, either as the environment variables `CF_ACCOUNT_ID`, `CF_KV_NAMESPACE_ID`, `CF_API_TOKEN`, or in `logs/.cloudflare-kv.json` under those same three names — a file `.gitignore` excludes for this reason. **Read scope is deliberate**: nothing on this side ever needs to write to KV, and a token that cannot write cannot corrupt the record the deletion rule reads.

**With no token on the machine the pruner declines and deletes nothing**, printing why. That is the correct behaviour rather than a fault — but it also means the rule silently is not in effect, so a `PRUNE: declined` line that persists across runs is worth acting on.

**The token was created and verified on 2026-08-18**, first try: `python scripts/prune-editions.py` read the record and reported `1401 editions on disk, 2 paths in the download record, 1401 kept, 0 deletable`. The two paths are that day's `curl` tests, and *0 deletable* against 1,401 files is forward-only doing its job — the whole published set predates the rule, so the first real candidate is still weeks away.

## What it deliberately does not do

- **It does not delete anything.** The Worker only records. The deletion is `scripts/prune-editions.py`, on Bill's machine, in RENDER Step 6a — nothing online ever writes to the repo, and nothing here can remove a file. *(That separation is the point: this half runs on Cloudflare where it cannot be trusted with anything irreversible, and the half that deletes runs where the repo is, reads this record, and refuses to act whenever the record looks less than sound.)*
- **It does not mint, copy or move files.** Nothing is archived on download; the archive, if it ever exists, is `site/` continuing to hold what it already holds.
- **It does not log HTML page views.** Those are the browsable surface, not editions, and counting them is a different question with a different tool.
- **It does not run on `data-landscapers.com`.** Requests there are redirected at the edge before any origin is reached, so a download that begins on the old domain is logged when it lands on the new one.
