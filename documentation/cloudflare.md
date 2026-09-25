---
type: reference
reader: cc
title: The Cloudflare layer — how it is configured, and what Corpus does with it
last_reviewed: 2026-08-18
status: current — describes the live configuration
---

# The Cloudflare layer

> **If you are picking this up cold, read `documentation/how-the-site-is-served.md` first.** This
> file is the operational reference — what is configured, and how to check it still works. It
> records only what is true now; how it was arrived at is in `archived/domain-move.md`,
> `archived/delete-unless-downloaded.md` and git.

## The shape of it

**Two sites, one Cloudflare account, two zones.** `data-landscapers.io` is where both sites live; `data-landscapers.com` exists only to redirect every old URL to its `.io` twin, path intact, indefinitely.

**Cloudflare sits in front of GitHub Pages and holds the editions.** RENDER commits `site/`, a push triggers the Pages workflow, and Pages serves the pages. The dated `.pdf`/`.csv` editions and the `catalogue/names/` shards live in the R2 bucket `editions`, served through the Worker at their existing URLs — **`documentation/editions-serving-shape.md` is the reference for that half.** Cloudflare terminates TLS and does three jobs: the `.com` redirects, the download log, and serving the editions.

**The download log is the part Corpus reads back**: RENDER, on Bill's machine, reads the KV record and deletes superseded editions nobody took.

```
reader ──► Cloudflare edge ──► Worker `download-log` ──┬─► R2 `editions`  dated .pdf/.csv,
              │                                        │                  catalogue/names/
              ├─ .com hostnames: 301 to .io, path preserved
              ├─ http: 301 to https, except /.well-known/acme-challenge/
              │                                        └─► GitHub Pages   pages, assets, the
              │                                                           catalogue, the bulletin
              └─ the Worker also notes the path of a .pdf/.csv ──► KV `downloads`
                                                                       │
        Bill's machine:  RENDER Step 6a ── prune-editions.py ◄─────────┘
                         RENDER Step 6b ── r2-sync.py ──► R2
```

## Zones and DNS

**`data-landscapers.io` — the live zone.** Six records serve the sites over HTTP, and the four apex `A` rows are GitHub Pages' own addresses. All three hostnames are **proxied (orange)**.

| Type  | Name     | Content                      | Proxy    |
| ----- | -------- | ---------------------------- | -------- |
| A     | `@`      | `185.199.108.153`            | Proxied  |
| A     | `@`      | `185.199.109.153`            | Proxied  |
| A     | `@`      | `185.199.110.153`            | Proxied  |
| A     | `@`      | `185.199.111.153`            | Proxied  |
| CNAME | `www`    | `data-landscapers.github.io` | Proxied  |
| CNAME | `corpus` | `data-landscapers.github.io` | Proxied  |

**The four `A` rows share the name `@` and must share the proxy status.** GitHub's documentation is the authority on the addresses.

**Both `CNAME`s point at `data-landscapers.github.io` although they serve different repositories** — GitHub routes on the requested hostname to the repository whose custom domain it is.

**`data-landscapers.com` — the redirect zone.** It serves no content. Two records exist so that requests reach Cloudflare's edge, where the redirect rules answer them.

| Type | Name     | Content | Proxy   |
| ---- | -------- | ------- | ------- |
| AAAA | `@`      | `100::` | Proxied |
| AAAA | `corpus` | `100::` | Proxied |

**`100::` is the IPv6 discard address**; a *proxied* record must exist for a request to reach the edge, where the redirect answers it before any origin. No `www` record: `www.data-landscapers.com` never existed.

**Any `MX` and `TXT` records on either zone are email and domain verification, unrelated to the above.** Leave them alone. Both zones have them; the `.io`'s are listed below.

### The sending domain — mail records on the `.io`

| Type | Name     | Content                                                   | Purpose                        |
| ---- | -------- | --------------------------------------------------------- | ------------------------------ |
| MX   | `@`      | `datalandscapers-io01b.mail.protection.outlook.com` (0)   | Microsoft 365 receives mail    |
| TXT  | `@`      | `v=spf1 include:secureserver.net -all`                    | SPF — GoDaddy, **hard fail**   |
| TXT  | `@`      | `MS=ms66509802`                                           | Microsoft 365 domain proof     |
| TXT  | `@`      | `google-site-verification=WCxwyKIHqVh-SmHZZjmrkYBcRz8IrRncrw0TdE9Q1Ds` | Google domain proof |

There is **no `DMARC` record at the root**, `_dmarc.data-landscapers.io`, and none is needed to send; `p=none` with a reporting address is the cheap first step if one is ever wanted. The `.com` mirrors the arrangement: same M365 MX, its own `TXT` rows.

**The `MX` row is not part of the alerts setup and must not be changed for it** — Buttondown requires no `MX`.

#### Alerts send from `newsletter.data-landscapers.io`, not the root

**All rows verified by Buttondown and confirmed resolving (2026-09-16).** Buttondown sends through **Postmark**, which is what `pm.mtasv.net` and `mtasv` are.

| Type  | Name                                          | Content                                | Proxy      | Purpose                    |
| ----- | --------------------------------------------- | -------------------------------------- | ---------- | -------------------------- |
| TXT   | `20260916144548pm._domainkey.newsletter`      | `k=rsa; p=MIGfMA0…`                    | n/a        | DKIM public key (current)  |
| TXT   | `20260529084906pm._domainkey.newsletter`      | `k=rsa; p=MIGfMA0…IDAQAB`              | n/a        | DKIM, **superseded — safe to delete** |
| CNAME | `pm-bounces.newsletter`                       | `pm.mtasv.net`                         | **DNS only** | Return-path / bounces    |
| CNAME | `track.newsletter`                            | `webhook-consumer.buttondown.email`    | **DNS only** | Click and open tracking  |
| TXT   | `_dmarc.newsletter`                           | `v=DMARC1; p=quarantine; rua=mailto:…@inbound.postmarkapp.com; aspf=r; pct=100` | n/a | DMARC, subdomain only |

The DKIM key is truncated above; the full row is whatever the zone holds.

**Changing the sending domain in Buttondown, in either direction, reissues DKIM** under a new selector — expect one new `TXT` row every time, and the domain shown unverified until it is added.

**Never add Buttondown's rows at the root**: its `_dmarc` is `p=quarantine` and the root's SPF already fails M365, so Bill's own mail would be quarantined. The subdomain also keeps newsletter reputation off Bill's M365 domain; the `From` address reads `newsletter.data-landscapers.io`. `documentation/catalogue-alerts.md` → *How the Buttondown account is configured* holds what is in force, `archived/catalogue-alerts-build.md` A3 the reasoning.

**Buttondown's manual records, not its managed DNS and not its Cloudflare integration** — managed DNS would delegate a subdomain this file could no longer describe, and the integration wants a DNS-edit grant over the zone that serves both sites, the Workers routes and every edition URL.

**No SPF row is needed for alerts; do not add Buttondown to the root's SPF.** The return path `pm-bounces.newsletter` is a `CNAME` onto `pm.mtasv.net`, so SPF is evaluated against **Postmark's** record. The root row lists GoDaddy, not `spf.protection.outlook.com`, so M365 mail from this domain already hard-fails SPF — Bill's arrangement, outside Corpus, not caused by alerts. **If a domain ever gains a second sender, merge into one `v=spf1` record rather than adding a second** — two records are a permanent failure.

**The mail `CNAME`s are DNS only — grey cloud. Do not orange them while tidying the zone**: proxied, they answer with Cloudflare's addresses and verification quietly stops passing. The check: a resolver returns `pm.mtasv.net` and `webhook-consumer.buttondown.email`, not Cloudflare addresses.

**`p=quarantine` makes an authentication failure silent** — no bounce, and reports go to Postmark's `rua`. So authentication is verified, not assumed (`catalogue-alerts.md` D); Bill's address as a second `rua` is the cheap way to see failures.

## TLS

**SSL/TLS mode is Full (strict), on both zones.** Flexible would send plain HTTP to GitHub, which redirects to HTTPS — a loop.

**Certificates are GitHub's, issued to the origin, and *Enforce HTTPS* is on for both repositories.** The current pair was issued on 2026-08-18 and expires on **16 November 2026**.

**Zone-wide *Always Use HTTPS* is deliberately OFF, and a Redirect Rule does that job instead.** GitHub issues and renews by a plaintext HTTP challenge; redirected, it is never answered and the certificate sits at *"TLS certificate is being provisioned … 1 of 3"* for ever.

**So the `.io` zone carries a rule named `force https except acme`** — match `not ssl and not starts_with(http.request.uri.path, "/.well-known/acme-challenge/")`, then *URL redirect* → Dynamic → `concat("https://", http.host, http.request.uri.path)` → `301`, preserve query string on. `http.host` rather than a literal hostname lets one rule serve the apex, `www` and `corpus` together.

**That exclusion is what lets November's renewal complete unattended** — the most load-bearing setting in this file. The check is below.

## Redirect rules

**Three rules, all `301`, all preserving the query string.** Two in the `.com` zone, one in the `.io`.

| Zone   | Name                     | Matches                                     | Redirects to                                              |
| ------ | ------------------------ | ------------------------------------------- | --------------------------------------------------------- |
| `.com` | `corpus com to io`       | hostname equals `corpus.data-landscapers.com` | `concat("https://corpus.data-landscapers.io", http.request.uri.path)` |
| `.com` | `main com to io`         | hostname equals `data-landscapers.com`        | `concat("https://data-landscapers.io", http.request.uri.path)` |
| `.io`  | `force https except acme` | `not ssl` and not an acme-challenge path      | `concat("https://", http.host, http.request.uri.path)` |

**The path must survive the redirect**: 1,053 published PDFs carry absolute `corpus.data-landscapers.com` URLs that an unrevisable edition cannot correct.

## The download log

**`workers/download-log/worker.js` is the code, deployed as a Worker named `download-log`, on the route `corpus.data-landscapers.io/*`.**

**It sees a request for a `.pdf` or `.csv` and writes the file's path into KV.** The response is obtained first — from R2 where the bucket holds the object, from GitHub Pages otherwise — and returned whatever happens in the logging, which runs in `waitUntil` and whose failure is swallowed. A broken logger costs a missing entry, never a download, so the record can be incomplete but never wrong in the direction that would delete a file somebody holds.

**The Worker is in the serving path** — the only route to a bucket-only file (`editions-serving-shape.md` → *What this costs in safety*). **R2 is tried, never required**: a miss, a throw or an absent binding falls through to Pages.

**The route covers the whole site and the Worker filters by extension**, so no later directory is missed; the free allowance is 100,000 requests a day.

**The KV namespace is `downloads`, bound to the Worker as the variable `DOWNLOADS`** — the code reads `env.DOWNLOADS` and does nothing if the binding is absent, so a mistyped binding fails silently and safely.

**The key is the file's path as published, without its leading slash** — exactly its path under `site/`, so a key matches a file on disk with no translation. The value records when it was taken and how often:

```
reports/KEN/KEN-status-2026-08-18.pdf     {"first":"2026-08-18","last":"2026-08-18","n":1,"bots":0}
```

**It logs no reader** — no IP, user-agent, referrer or session. The user-agent is read in memory to classify a crawler, and not stored.

**Crawlers are counted separately rather than excluded** — `n` for readers, `bots` for the rest. Both protect a file from deletion.

**HTML pages are not logged**, nor anything on `data-landscapers.com`, which is redirected at the edge — a download begun on the old domain is logged when it lands on the new one.

## What Corpus does with the record

**A superseded edition is deleted unless somebody downloaded it.** `scripts/prune-editions.py` is the rule; `RENDER.md` Step 6a runs it with `--apply`, after the site is written and before the commit, so the deletions ride in the render commit that superseded them. Retention exists for readers: an edition nobody fetched has no citation resting on it, and storage tracks demand rather than catalogue size.

**The file never moves**: kept at its cited URL or deleted — no archive folder, copy or redirect.

**Five conditions, all of which must hold before a file is deleted.**

1. **It is not the current edition.** The newest edition of any document is never touched.
2. **It was published after 2026-08-18**, the day the Worker went live. The rule applies **forward only**: an edition from before the Worker has no record for its period and would be deleted for want of evidence. The pre-worker archive was cleared by hand on 2026-09-08 (`design.md` §9, `scripts/drop-pre-worker-editions.py`); the condition stays in the rule.
3. **It was superseded more than seven days ago** — so a late log entry still arrives first, and a reader who downloads on Friday from a link kept on Monday is covered.
4. **The download record is healthy** — the two checks below.
5. **Nothing ever fetched it.** Any hit at all protects, in any casing, a crawler's included.

**Presence of the key is the whole test** — the pruner lists keys only. A crawler causing a keep costs storage; the crawler pattern matches `curl`, `wget` and `python-requests`, which is how a technical reader takes a file to cite.

**Two health checks, because an empty answer and a quiet week look identical.** `--min-keys` refuses to act on an empty listing (an unbound namespace, a wrong namespace ID, a Worker off its route). `--liveness-days` requires that some key names an edition minted in the last fortnight — a key can only exist after its file was minted, so the newest edition date across the keys bounds when the Worker last recorded anything.

**Every uncertainty resolves towards keeping the file.** A missing credential, an API error, an unparseable answer, an empty listing or a stale-looking record stops the whole run and deletes nothing. The script exits 0 either way and prints `PRUNE: declined` with the reason, so a refusal never fails a render. A refusal that persists across runs means the rule is silently not in effect and wants acting on.

**Deletions are recorded in `logs/deleted-editions.csv`**, committed with the render. `--ledger` points that elsewhere, for a rehearsal against a scratch tree.

**Deleting does not shrink the repository** (the blob stays in `.git`); the saving is against Pages' ~1 GB soft ceiling. **Step 6b stops the growth**: an edition uploaded to R2 and removed before the commit never enters git.

## Credentials

**The pruner needs a Cloudflare API token with `Account · Workers KV Storage · Read`, and nothing more** — a token that cannot write cannot corrupt the record.

**Supply it as the environment variables `CF_ACCOUNT_ID`, `CF_KV_NAMESPACE_ID` and `CF_API_TOKEN`, or as those three keys in `logs/.cloudflare-kv.json`**, which `.gitignore` excludes. Environment variables take precedence. The token is a secret and must never be committed.

**Both IDs appear in one place.** Open the `downloads` namespace in the dashboard and the address reads `dash.cloudflare.com/<ACCOUNT_ID>/workers/kv/namespaces/<NAMESPACE_ID>`.

**R2 needs a second, separate and much stronger credential.** `scripts/r2-sync.py` writes the editions bucket over the S3-compatible endpoint with an *Object Read & Write* key pair — `CF_R2_ACCESS_KEY_ID` and `CF_R2_SECRET_ACCESS_KEY`, minted under *R2 · Manage API tokens* — in the environment or in `logs/.cloudflare-r2.json`, which `.gitignore` excludes. **It can overwrite and delete published editions**; it is the credential in this repo with the most behind it. `documentation/editions-serving-shape.md` → *Doing it* has the setup.

## Confirming it all still works

**Test results, not screens** — the dashboard is reorganised often.

**The sites serve, and the old addresses still forward with their paths:**

```
curl -sS -o NUL -D - https://corpus.data-landscapers.io/
curl -sS -o NUL -D - https://corpus.data-landscapers.com/reports/KEN/KEN-status.html
```

The second must answer `301` with `Server: cloudflare` and a `Location:` carrying the **full path**. A stale local DNS answer can make a working redirect look broken for up to an hour — `curl --resolve`, or a phone on mobile data, settles it.

**The acme exclusion, which November's renewal depends on:**

```
curl -sS -o NUL -D - http://data-landscapers.io/                              # must 301 to https
curl -sS -o NUL -D - http://data-landscapers.io/.well-known/acme-challenge/x  # must 404, not 301
```

The second must also carry an `X-GitHub-Request-Id` header, which shows the request reached GitHub rather than being answered at the edge. A `301` there means renewal will fail silently in November.

**The download log records, and the pruner can read it:**

```
python scripts/prune-editions.py
```

Expect `PRUNE: N editions on disk, M paths in the download record, N kept, 0 deletable`. Anything beginning `PRUNE: declined` names its reason: no credential, an HTTP 403 (permission on the wrong scope), an HTTP 404 (wrong account or namespace ID), or a listing of 0 keys (pointed at an empty namespace).

## What must not change

**The `.com` stays registered indefinitely.** 1,053 published PDFs carry absolute `.com` URLs, 401 published pages link to it, and §9 promises that a dated URL resolves for ever. There is no date at which removing the redirects becomes safe, and a lapsed registration has no undo.

**A hostname whose certificate is being issued or renewed must be grey (DNS only) for the duration** unless the acme rule is in place; with the proxy on otherwise, validation never completes. Nothing goes dark while grey — Pages serves directly. `force https except acme` makes this unnecessary for a routine renewal.

**Full (strict), never Flexible.**

**The KV binding stays `DOWNLOADS` and the key stays the path under `site/`** — Worker and pruner are two ends of one agreement; either changing alone breaks it silently.

**Nothing online ever writes to the repository.** The Worker records and cannot delete; the pruner deletes and runs where the repo is.

## What §9 now promises

**A dated URL resolves for ever *if anybody ever took it*** — the amendment this layer made to `documentation/design.md` §9, where the reasoning is. **The residue:** someone holding a URL they never downloaded from — a pasted link — eventually loses the file. The seven-day lag covers most of that, not all.

## Dates

- **2026-08-18** — both sites moved to `.io` behind Cloudflare; redirects, Full (strict), the acme exclusion, the `download-log` Worker, `prune-editions.py`, the KV read token and Step 6a built and verified.
- **2026-09-16** — alerts sending domain `newsletter.data-landscapers.io` verified; DKIM reissued under selector `20260916144548pm`.
- **16 November 2026** — the current TLS certificates expire. Renewal should be automatic; the acme check above says whether it will be.
