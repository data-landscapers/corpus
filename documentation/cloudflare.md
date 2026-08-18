---
type: reference
title: The Cloudflare layer — how it is configured, and what Corpus does with it
last_reviewed: 2026-08-18
status: current — describes the live configuration
---

# The Cloudflare layer

*(Written 2026-08-18, from three files that between them built this: `archived/domain-move.md`, `archived/delete-unless-downloaded.md` and the Worker's own README. Those recorded how the thing was arrived at — the options weighed, the dead ends, the dashboard screens that had moved. This one records only what is true now, and what depends on it. If you are picking this up cold, this file is the whole picture and you do not need the archived three.)*

## The shape of it

**Two sites, one Cloudflare account, two zones.** `data-landscapers.io` is where both sites live; `data-landscapers.com` exists now only to redirect every old URL to its `.io` twin, path intact, and will go on existing for that purpose indefinitely.

**Cloudflare sits in front of GitHub Pages, which is still the origin and still holds the files.** Nothing about publishing changed when Cloudflare arrived: RENDER commits `site/`, a push triggers the Pages workflow, and Pages serves. Cloudflare terminates TLS at its edge, forwards to Pages, and does two jobs of its own — the redirects from `.com`, and the download log.

**The download log is the part Corpus reads back.** A Worker notes the path of every `.pdf` and `.csv` a reader takes and writes it to a KV store. On Bill's machine, RENDER reads that store and deletes superseded editions nobody ever took. Nothing online ever writes to the repo; the record travels one way, and the only thing that acts on it runs where the repo is.

```
reader ──► Cloudflare edge ──► GitHub Pages (origin, holds site/)
              │
              ├─ .com hostnames: 301 to .io, path preserved
              ├─ http: 301 to https, except /.well-known/acme-challenge/
              └─ Worker `download-log`: notes the path of a .pdf/.csv ──► KV `downloads`
                                                                              │
                    Bill's machine:  RENDER Step 6a ── prune-editions.py ◄────┘
```

## Zones and DNS

**`data-landscapers.io` — the live zone.** Six records serve the sites, and the four apex `A` rows are GitHub Pages' own addresses. All three hostnames are **proxied (orange)**.

| Type  | Name     | Content                      | Proxy    |
| ----- | -------- | ---------------------------- | -------- |
| A     | `@`      | `185.199.108.153`            | Proxied  |
| A     | `@`      | `185.199.109.153`            | Proxied  |
| A     | `@`      | `185.199.110.153`            | Proxied  |
| A     | `@`      | `185.199.111.153`            | Proxied  |
| CNAME | `www`    | `data-landscapers.github.io` | Proxied  |
| CNAME | `corpus` | `data-landscapers.github.io` | Proxied  |

**The four `A` rows share the name `@` and must share the proxy status**; the dashboard lists them by full hostname rather than by the `@` shorthand used to enter them. GitHub's own documentation is the authority on those four addresses, not this file.

**Both `CNAME`s point at `data-landscapers.github.io` although they serve different repositories.** GitHub routes on the hostname the browser asked for, and the repository that claims a hostname is whichever one has it set as its custom domain — which is also why two repositories cannot claim the same one.

**`data-landscapers.com` — the redirect zone.** It serves no content. Two records exist so that requests reach Cloudflare's edge at all, where the redirect rules answer them.

| Type | Name     | Content | Proxy   |
| ---- | -------- | ------- | ------- |
| AAAA | `@`      | `100::` | Proxied |
| AAAA | `corpus` | `100::` | Proxied |

**`100::` is the IPv6 discard address and nothing is behind it.** A redirect rule runs at the edge before any origin is contacted, but a *proxied* record must exist for the request to reach the edge — so the record's only job is to exist. There is no `www` record on either zone's `.com` side, because `www.data-landscapers.com` never existed and nothing published references it.

**Any `MX` and `TXT` records on the `.com` are email and domain verification and are unrelated to the above.** Leave them alone.

## TLS

**SSL/TLS mode is Full (strict), on both zones.** Cloudflare talks to GitHub over HTTPS and validates the certificate. Flexible would put plain HTTP on that leg, GitHub would redirect it to HTTPS, and the redirect would arrive back at Cloudflare to be stripped again — a loop.

**Certificates are GitHub's, issued to the origin, and *Enforce HTTPS* is on for both repositories.** The current pair was issued on 2026-08-18 and expires on **16 November 2026**.

**Zone-wide *Always Use HTTPS* is deliberately OFF, and a Redirect Rule does that job instead.** GitHub renews a certificate by re-running a plaintext HTTP challenge against the hostname; with the clouds orange that challenge reaches Cloudflare, and with *Always Use HTTPS* on it is redirected to HTTPS and never answered. Issuance and renewal both fail that way, silently, and sit at *"TLS certificate is being provisioned … 1 of 3"* for ever.

**So the `.io` zone carries a rule named `force https except acme`** — match `not ssl and not starts_with(http.request.uri.path, "/.well-known/acme-challenge/")`, then *URL redirect* → Dynamic → `concat("https://", http.host, http.request.uri.path)` → `301`, preserve query string on. `http.host` rather than a literal hostname is what makes one rule serve the apex, `www` and `corpus` together.

**That exclusion is what will let November's renewal complete unattended.** It is the single most load-bearing piece of configuration in this file, and the way to confirm it still works is below.

## Redirect rules

**Three rules, all `301`, all preserving the query string.** Two live in the `.com` zone and one in the `.io` zone.

| Zone   | Name                     | Matches                                     | Redirects to                                              |
| ------ | ------------------------ | ------------------------------------------- | --------------------------------------------------------- |
| `.com` | `corpus com to io`       | hostname equals `corpus.data-landscapers.com` | `concat("https://corpus.data-landscapers.io", http.request.uri.path)` |
| `.com` | `main com to io`         | hostname equals `data-landscapers.com`        | `concat("https://data-landscapers.io", http.request.uri.path)` |
| `.io`  | `force https except acme` | `not ssl` and not an acme-challenge path      | `concat("https://", http.host, http.request.uri.path)` |

**The path must survive the redirect, and that is the whole point of the first two.** 1,053 published PDFs carry absolute `corpus.data-landscapers.com` URLs printed inside them and cannot be corrected, because a retained edition is not revised after publication. `…/KEN-status-2026-08-06.pdf` reaching that exact file is what these rules are for; a redirect that landed everyone on the front page would be worse than none.

## The download log

**`workers/download-log/worker.js` is the code, deployed as a Worker named `download-log`, on the route `corpus.data-landscapers.io/*`.**

**It sees a request for a `.pdf` or `.csv`, writes the file's path into KV, and passes the request through untouched.** The response is fetched and returned whatever happens in the logging, so a Worker that breaks costs a missing log entry rather than a broken download. That asymmetry is what makes it safe to hang a deletion rule off: the record can be incomplete, never wrong in the direction that would delete a file somebody is holding.

**The route covers the whole site and the Worker filters by file extension.** One route cannot miss a directory added later, and the free allowance is 100,000 requests a day against a site that will not approach it. The cost is that the Worker runs on page views too and returns them untouched.

**The KV namespace is `downloads`, bound to the Worker as the variable `DOWNLOADS`** — capitals, because the code reads `env.DOWNLOADS` and does nothing at all if that binding is absent. A mistyped binding name therefore fails silently and safely.

**The key is the file's path as published, without its leading slash**, which is exactly its path under `site/` — so whatever reads the record can match a key against a file on disk with no translation between two naming schemes. The value records when it was taken and how often:

```
reports/KEN/KEN-status-2026-08-18.pdf     {"first":"2026-08-18","last":"2026-08-18","n":1,"bots":0}
```

**It logs no reader.** No IP address, no user-agent, no referrer, no session. The user-agent is read once, in memory, to decide whether a hit came from a crawler, and is not stored.

**Crawlers are counted separately rather than excluded** — `n` for readers, `bots` for the rest. Both protect a file from deletion; the split exists so that whoever reads the numbers later can tell them apart.

**HTML pages are not logged.** They are the browsable surface, not editions. Neither is anything on `data-landscapers.com`, where requests are redirected at the edge before an origin is reached — a download that begins on the old domain is logged when it lands on the new one.

## What Corpus does with the record

**A superseded edition is deleted unless somebody downloaded it.** `scripts/prune-editions.py` is the rule; `RENDER.md` Step 6a runs it with `--apply`, after the site is written and before the leak gate and the commit — so the deletions are carried by the same commit as the render that superseded them, and the gate reads the tree as it will be published.

**Retention exists for readers rather than for artefacts.** A citation only exists if somebody actually took the file, so an edition nobody ever fetched has nothing resting on it. Storage then tracks demand rather than catalogue size, and the catalogue is the half that grows without limit.

**The file never moves.** A downloaded edition stays at the URL it was cited at; an undownloaded one is deleted. There is no archive folder, no copy step and no redirect, so no link this rule keeps ever changes address.

**Five conditions, all of which must hold before a file is deleted.**

1. **It is not the current edition.** The newest edition of any document is never touched.
2. **It was published after 2026-08-18**, the day the Worker went live. The rule applies **forward only**: the ~1,053 editions already published have no record for the period before the Worker existed, so every one of them would be deleted for want of evidence.
3. **It was superseded more than seven days ago** — long enough that a late log entry still arrives before the deletion, and it covers the reader who browses on Monday and downloads on Friday from a link they kept.
4. **The download record is healthy** — see the two checks below.
5. **Nothing ever fetched it.** Any hit at all protects, in any casing, a crawler's included.

**Any fetch protects, including a crawler's, and one consequence is that the values are never read.** Presence of the key is the whole test, so the pruner asks Cloudflare for the key list alone. A bot causing a keep costs storage, where dropping a real reader's download would eventually cost the file — and the crawler pattern matches `curl`, `wget` and `python-requests`, which is how a technical reader takes a file they mean to cite.

**Two health checks, because an empty answer and a quiet week look identical.** `--min-keys` refuses to act on an empty listing, which is what an unbound namespace, a wrong namespace ID and a Worker knocked off its route all look like. `--liveness-days` requires that some key names an edition minted in the last fortnight — a key can only exist after the file it names was minted, so the newest edition date across the keys is a lower bound on when the Worker last recorded anything.

**Every uncertainty resolves towards keeping the file.** A missing credential, an API error, an unparseable answer, an empty listing or a stale-looking record stops the whole run and deletes nothing — not file by file. The script exits 0 either way and prints `PRUNE: declined` with the reason, so a refusal never fails a render. A refusal that persists across runs means the rule is silently not in effect and wants acting on.

**Deletions are recorded in `logs/deleted-editions.csv`**, committed with the render. Git keeps the blob for ever regardless; the ledger is the part a person can read. `--ledger` points that elsewhere, which is what a rehearsal against a scratch tree should use.

**What this does not do is shrink the repository.** Deleting a PDF from `site/` removes it from the published site and leaves the blob in `.git`. The saving is against GitHub Pages' soft ceiling of about 1 GB; getting repository weight back is a different operation entirely.

## Credentials

**The pruner needs a Cloudflare API token with `Account · Workers KV Storage · Read`, and nothing more.** Read scope is deliberate: nothing on this side ever writes to KV, and a token that cannot write cannot corrupt the record the deletion rule reads.

**Supply it as the environment variables `CF_ACCOUNT_ID`, `CF_KV_NAMESPACE_ID` and `CF_API_TOKEN`, or as those three keys in `logs/.cloudflare-kv.json`**, which `.gitignore` excludes. Environment variables take precedence. The token is a secret and must never be committed.

**Both IDs appear in one place.** Open the `downloads` namespace in the dashboard and the address reads `dash.cloudflare.com/<ACCOUNT_ID>/workers/kv/namespaces/<NAMESPACE_ID>`.

## Confirming it all still works

**Test results, not screens.** The dashboard is reorganised often; every one of these checks describes an answer rather than a button, and they are what to trust.

**The sites serve, and the old addresses still forward with their paths:**

```
curl -sS -o NUL -D - https://corpus.data-landscapers.io/
curl -sS -o NUL -D - https://corpus.data-landscapers.com/reports/KEN/KEN-status.html
```

The second must answer `301` with `Server: cloudflare` and a `Location:` carrying the **full path**. A stale local DNS answer can make a working redirect look broken for up to an hour, and it looks exactly like a broken configuration — `curl --resolve`, or a phone on mobile data, settles it in seconds where a browser cannot.

**The acme exclusion, which is what November's renewal depends on:**

```
curl -sS -o NUL -D - http://data-landscapers.io/                              # must 301 to https
curl -sS -o NUL -D - http://data-landscapers.io/.well-known/acme-challenge/x  # must 404, not 301
```

The second must also carry an `X-GitHub-Request-Id` header, which is how you know the request reached GitHub rather than being answered at Cloudflare's edge. A `301` there means renewal will fail in November the same silent way issuance failed in August.

**The download log records, and the pruner can read it:**

```
python scripts/prune-editions.py
```

Expect `PRUNE: N editions on disk, M paths in the download record, N kept, 0 deletable`. Anything beginning `PRUNE: declined` names its own reason: no credential, an HTTP 403 (permission on the wrong scope), an HTTP 404 (wrong account or namespace ID), or a listing of 0 keys (pointed at an empty namespace).

## What must not change

**The `.com` stays registered indefinitely.** 1,053 published PDFs carry absolute `.com` URLs inside them, 401 published pages link to it, and §9 promises that a dated URL resolves for ever. The redirect rules are what keep every one of those alive, and there is no date at which removing them becomes safe. Letting the registration lapse is the one thing here with no undo.

**A hostname whose certificate is being issued or renewed must be grey (DNS only) for the duration.** GitHub validates by fetching a plaintext challenge from the hostname; with the proxy on it reaches Cloudflare instead, and validation never completes. Nothing is dark while the clouds are grey — the site serves straight from GitHub Pages, which is where it lived before Cloudflare. The `force https except acme` rule exists so that this is not needed for a routine renewal.

**Full (strict), never Flexible.**

**The KV binding stays `DOWNLOADS` and the key stays the path under `site/`.** The Worker writes both and the pruner reads both; they are one agreement with two ends, and either end changing alone breaks the rule silently.

**Nothing online ever writes to the repository.** The Worker records and cannot delete; the pruner deletes and runs where the repo is. That separation is what makes it safe for something irreversible to act on a record gathered elsewhere.

## What §9 now promises

**A dated URL resolves for ever *if anybody ever took it*.** That is the amendment this layer made to `documentation/design.md` §9, and the reasoning is recorded there.

**The residue, stated rather than hidden:** someone may hold a URL they never downloaded from — a link pasted into a message, an address copied off a page — and for them the file eventually goes. The seven-day lag covers most of that and not all of it, and it is the price of the rule.

## Dates

- **2026-08-18** — both sites moved to `.io` behind Cloudflare; redirects, Full (strict) and the acme exclusion built and verified. The `download-log` Worker deployed and verified. `prune-editions.py` written, the KV read token created, and Step 6a run end to end inside a full render.
- **16 November 2026** — the current TLS certificates expire. Renewal should be automatic; the acme check above is what says whether it will be.
