---
type: decision
title: editions-serving-shape.md — where the dated editions are served from
last_reviewed: 2026-09-08
status: done — decided, built and cut over on 2026-09-08
---

# The serving shape of the editions

> **`documentation/how-the-site-is-served.md` is the plain-language version of what this note
> decided.** Read that if you want to understand the arrangement; read this if you want to know
> why it was chosen and what it cost.

*(This is the note `catalogue-serving-shape.md` → *The editions layer* said would be needed and
deferred. Written 2026-09-08 at Bill's instruction to build the move now rather than at the end
of the freeze. It resolves the ceiling problem that note called "the real one" and that the
prune rule was never going to solve on its own.)*

## What was decided

**The dated editions and the names index move to Cloudflare R2, served through the Worker that is
already in front of them, at the URLs they already have.** GitHub Pages keeps every HTML page,
the assets, the catalogue and the bulletin.

**The URL does not change, and that is the constraint everything else was fitted around.** §9
promises a dated URL resolves for ever. Moving a file between origins is an implementation
detail the reader must never be able to observe, so the R2 key is the path under `site/` — which
is also the KV key the download record already uses. One string addresses a file in three places
and nothing translates between naming schemes.

## Why the prune rule was not going to be enough

**Deletion tracks demand; the catalogue tracks the world.** `prune-editions.py` deletes a
superseded edition nobody downloaded, and it works — 2,019 editions and 625 MB since 2026-08-26.
But 251 documents cutting an edition whenever their content moves generate editions faster than
supersession plus a week plus *nobody took it* retires them, and the fraction that anybody
downloads only grows once the site is public. On 2026-09-08 `site/` stood at 1,316 MB against a
soft ceiling of about 1 GB, having been 924 MB four days earlier.

**Clearing the pre-worker archive bought three weeks, not a solution.** 1,237 editions and 374 MB
went on 2026-09-08 (`design.md` §9, and `scripts/drop-pre-worker-editions.py`). That took the
tree to 957 MB — under the ceiling, and back over it within the month. It was worth doing and it
was never the answer.

**The editions are 901 MB of the remaining 957 MB.** Nothing else on the site is large enough for
the arithmetic to work any other way: pages, assets, the catalogue and the bulletin together are
about 56 MB. Either the editions leave GitHub Pages or the ceiling is met again by October.

## The shape

```
reader ──► Cloudflare edge ──► Worker `download-log` ──┬─► R2 `editions`   dated .pdf/.csv,
              │                                        │                   catalogue/names/
              ├─ .com → .io, path preserved            │
              └─ http → https, except acme             └─► GitHub Pages    everything else,
                                                                           and the fallback
                        KV `downloads` ◄── the Worker records what was taken
                              │
      Bill's machine:  prune-editions.py ◄─┘  deletes from whichever store holds it
```

## What moves, and what does not

| | Where | Why |
| --- | --- | --- |
| Dated `.pdf`/`.csv` in `reports/`, `topics/`, `countries/`, `finance/` | **R2** | 2,501 files, 843 MB, the whole of the problem |
| `catalogue/names/` | **R2** | 5,638 shards, 73 MB of derived data: fetched by the catalogue's own JS, never cited, never linked, rebuilt from `outputs/` in one command |
| HTML pages, assets, `raw-catalogue.csv` | Pages | The browsable surface. `raw-catalogue.csv` is deliberately undated (§9) and republished wholesale, so it is not an edition and never matches |
| `bulletin/` | Pages | **A decision, not an oversight.** Bulletin editions are deleted on a stated seven-day window rather than on downloads, so they never accumulate — 20 files, 6 MB — and `prune-editions.py` rebuilds `bulletin/editions.json` by reading that directory off disk. Moving 6 MB would mean teaching the manifest rebuild to enumerate a bucket, for no headroom |

**8,139 objects, 901.3 MB.** `python scripts/r2-sync.py` prints the current count without
uploading anything.

## What this costs in safety, stated plainly

**The Worker was deliberately out of the serving path and no longer is.** Its original design
fetched from origin and returned the response whatever happened in the logging, so a broken
Worker cost a log entry rather than a download — and `cloudflare.md` names that asymmetry as
what made it safe to hang a deletion rule off. Serving editions from R2 gives that up: once a
file exists only in the bucket, this Worker is the only route to it.

**Three things hold the line instead.**

1. **R2 is tried, never required.** A miss, a throw, or an unbound namespace falls through to
   the origin fetch. Through the whole migration both copies exist and the fallback is a real
   file rather than a 404.
2. **Logging still cannot withhold a response.** It runs in `waitUntil`, after the body is in
   hand, and its failure is swallowed. The download record can be incomplete; it cannot be wrong
   in the direction that deletes a file somebody is holding.
3. **The local copy is deleted only against a verified bucket copy.** `r2-sync.py --prune-local`
   refuses to touch a file it has not just seen in R2 at the same byte count and the same MD5,
   and it refuses wholesale rather than file by file.

**The residue:** an outage at Cloudflare now takes the editions down, where before it would have
taken the whole site down anyway — the zone is already in front of Pages, proxied, and has been
since 2026-08-18. What is genuinely new is that a *Worker* fault, as opposed to an edge fault,
now reaches the editions. That is the price of the ceiling, and it is why the fallback exists.

## The selection rule exists twice

**`r2-sync.py` decides what to upload with `editions.py`'s grammar, which is canonical; the
Worker decides what to look for with a regex, because a Worker cannot import Python.** They must
agree. A file uploaded that the Worker does not recognise is served from Pages until the local
copy goes, and 404s after. `r2-sync.py --check-serving` is the check that does not trust them to
match: it asks the live site which origin answered, reading the immutable `Cache-Control` the
Worker sets and Pages does not.

## Doing it

**The order is upload, deploy, verify, then delete locally, and it is not negotiable.** Every
step leaves the site serving throughout.

### Bill's steps, in the Cloudflare dashboard

There is no `wrangler` and no `node` on the render machine, and the existing API token is
`Workers KV Storage · Read` — deliberately read-only, and unable to do any of this. So these
four are account-side.

1. **R2 → Create bucket**, named `editions`, standard storage, automatic location.
2. **R2 → Manage API tokens → Create token**, *Object Read & Write*, scoped to that bucket.
   It hands back an **Access Key ID** and a **Secret Access Key**, shown once.
3. **Workers → `download-log` → Settings → Bindings → Add → R2 bucket**: variable name
   `EDITIONS` (capitals — the code reads `env.EDITIONS` and falls through to Pages if it is
   absent, so a mistyped name fails silently and safely), bucket `editions`.
4. **Deploy the Worker**: paste `workers/download-log/worker.js` into the dashboard editor and
   save. The KV binding `DOWNLOADS` stays exactly as it is.

Then, on the render machine, write the credentials to `logs/.cloudflare-r2.json`, which
`.gitignore` excludes:

```json
{
  "CF_ACCOUNT_ID": "abed2ae73725c64bd81060e0dcbcd4ef",
  "CF_R2_BUCKET": "editions",
  "CF_R2_ACCESS_KEY_ID": "…",
  "CF_R2_SECRET_ACCESS_KEY": "…"
}
```

### The cutover

```bash
python scripts/test_r2_client.py            # the canonical request and the move rule
python scripts/r2-sync.py                   # what would go up: expect ~8,139 objects, ~901 MB
python scripts/r2-sync.py --apply           # upload. Idempotent; safe to re-run after a failure
python scripts/r2-sync.py --verify          # every candidate in the bucket, size and MD5
python scripts/r2-sync.py --check-serving   # which origin the live site answers from
```

`--check-serving` must say `r2` for the sampled keys before the next line runs. It is the only
step that proves the Worker, the binding and the upload agree, and it is the whole reason the
local copies are still there at this point.

```bash
python scripts/r2-sync.py --prune-local --apply     # delete the verified local copies
git add -A site && git commit && git push           # the tree Pages serves loses 901 MB
```

**Rolling back, at any point before the last line:** remove the R2 binding in the dashboard. The
Worker falls through to Pages for everything and the site is exactly as it was. After the last
line, roll back with `git revert` of that commit, which restores the files to `site/`.

## After the move

**`prune-editions.py` prunes both stores as one.** It lists the bucket, merges it with the tree,
and treats a document as one document however its editions are distributed — a merge that gets
this wrong would read a disk edition as the newest of its own set, call it the current edition,
and keep it for ever. An edition that is in both stores is one row and leaves both.
`test_prune_editions.py` pins all three cases.

**A bucket that will not list is reported, not worked around.** The run falls back to the tree,
which cannot delete anything wrongly — an edition whose successor is only in R2 simply looks
current and is kept — but it does mean nothing in R2 is being retired, and it says so.

**RENDER gains Step 6b**, after the prune and before the commit: upload the editions this render
cut, verify, delete the local copies. New editions therefore never enter git at all, which also
stops the history growth `catalogue-serving-shape.md` costed at roughly 6 GB a year.

## What it costs in money

**R2 bills storage per GB-month and charges nothing for egress, which is the entire reason it is
R2 and not S3.** At ~0.9 GB the storage line is cents a month; the uploads are a one-off 8,139
class-A operations against an allowance far larger; reads are class-B and are mostly served from
Cloudflare's cache before they reach the bucket, because every edition is immutable by
construction and is returned with a one-year `immutable` cache header. **Confirm the current
rates and the free allowance when the bucket is created** — this note should not be the record
of somebody else's price list.

## What must not change

**The R2 key stays the path under `site/`**, which is also the KV key. The Worker writes one and
reads the other, `r2-sync.py` writes both, and `prune-editions.py` matches all three. Any one of
them changing alone breaks the rule silently.

**The binding stays `EDITIONS`**, and `DOWNLOADS` stays `DOWNLOADS`.

**The local copy is never deleted except against a verified bucket copy.** Not "it uploaded
without error" — verified, by a read back, on size and MD5.

**The bulletin stays on Pages** until somebody teaches `bulletin_editions.py` to enumerate a
bucket, and there is no reason to.

## Dates

- **2026-09-08** — decided, built and cut over, all in one session. The pre-worker archive
  cleared (1,237 editions, 374 MB); `r2_client.py`, `r2-sync.py` and the Worker's serving half
  written and tested; `prune-editions.py` taught to prune both stores. Bucket created, 8,139
  objects uploaded and verified twice, the Worker deployed with both bindings over the API, and
  the local copies deleted. **`site/` 1,316 MB → 82 MB.**

  **Four faults were found by probing the live site rather than by trusting the deploy**, and
  each is worth remembering because none of them would have announced itself. The 5,658 `.txt`
  name shards went up as `application/octet-stream` because `.txt` was missing from the type
  map, and matched on size and MD5 for ever after — fixed by making the content type part of
  what "already current" means. A single Cloudflare `503` two thirds of the way through a resync
  aborted the whole run, correctly but unhelpfully; the transient codes are now retried. Passing
  R2 the whole header set as `range` made it resolve the absent Range to the entire object, so
  every ordinary download answered `206 Partial Content`. And `--check-serving` was reading
  Cloudflare's edge cache rather than the Worker, reporting `pages` for files R2 was serving.
