---
type: runbook
reader: cc
title: Scan one country's institutions for hyperscaler dependence — instruction for Claude Code
last_reviewed: 2026-09-28
status: R&D; ZAF scanned 2026-09-28, pilot countries not yet run
---

# Hyperscaler scan — runbook for Claude Code

*(Step Three of the hyperscaler-dependence R&D. The input is one file, `R&D/Hyperscaler-dependence/scan/{ISO3}/institutions-{ISO3}.csv`, built by hand in Step Two; the output is the DNS footprint of every institution in it, attributed and classified, under `R&D/Hyperscaler-dependence/scan/{ISO3}/`. Read `R&D/Hyperscaler-dependence/hyperscaler-dependence.md` first — §3 is the classification, §5 the pilot and what it has to decide. This runs on the laptop, not in Cowork, because Cowork's shell has no resolver. OSINT is not read or written by any step here. Everything here is passive: DNS queries through a public resolver, reads of public logs and registries, and the hyperscalers' own published range files. Nothing connects to an institution's own hosts.)*

## Prerequisites

- Python 3 with `dnspython` and `requests`. Run every command from the repo root.
- `scripts/hyperscaler-scan.py` — **built on the first run per §A below if it does not exist, and committed before any country is scanned.** Once it exists, §A is the spec it is held to, not a step.
- `R&D/Hyperscaler-dependence/asn-owners.csv` (`asn,owner,category,note`), `R&D/Hyperscaler-dependence/saas-targets.csv` (`suffix,provider,category`) and `R&D/Hyperscaler-dependence/subdomains.txt`. If any is missing, create it from §A.4 and §A.2 and commit; they grow with every run.
- `R&D/Hyperscaler-dependence/ranges/` and `R&D/Hyperscaler-dependence/cache/` are gitignored. Add the two lines to `.gitignore` on the first run.

## Running unattended — a run never stops to ask

A domain that does not resolve, a crt.sh call that times out, an IP no source will attribute: each is a row with a status, never a stop. The run's only hard stop is Step 0. Where a run wants Bill's attention it finishes the country and writes a block in `logs/messages-for-bill.md`, within the cap.

## A. The script — what `scripts/hyperscaler-scan.py` does

`python scripts/hyperscaler-scan.py R&D/Hyperscaler-dependence/scan/{ISO3}/institutions-{ISO3}.csv` reads the file, takes ISO3 from the filename, and writes `R&D/Hyperscaler-dependence/scan/{ISO3}/nodes.csv`, `organisations.csv` and `run.json`. It resumes: a name already in `nodes.csv` with today's `scan_date` is not queried again.

**A.1 Input.** Columns `type,institution,domain,email_domain,status,note`. One row per domain; an institution with two domains has two rows. A row whose `status` is `dead` is skipped. Anything else is scanned whatever its status says.

**A.2 Enumeration.** For each domain, three sources, each recorded in the node's `source` column. (1) The root: the domain itself and `www`. (2) The dictionary, `R&D/Hyperscaler-dependence/subdomains.txt`: a standard list of roughly 500 names plus the African-service list from the design note §5.3 (`ecitizen`, `ifmis`, `portal`, `webmail`, `zimbra`, `owa`, `autodiscover`, `vpn`, `citrix`, `remote`, `ibank`, `internetbanking`, `mobile`, `api`, `ussd`, `sip`, `egov`, `etender`, `eprocurement`, `efiling`, `tax`, `customs`, `visa`, `passport`, `id`, `nid`, `payroll`, `hr`, `intranet`, `mail2`, `smtp`, `mx`, `ns1`, `ns2`, `test`, `dev`, `staging`, `old`, `backup`). (3) Certificate Transparency: `https://crt.sh/?q=%25.{domain}&output=json`, one call per domain, one retry after 30 s, and on a second failure `ct_status: failed` in `run.json` and carry on. Names are deduplicated; a name found by two sources keeps both in `source`, joined by `;`.

**Wildcards.** Before the dictionary, resolve a random 16-character label under the domain. If it resolves, the domain is wildcarded: dictionary hits are not evidence of a real host and are kept only where CT also returned the name. Record `wildcard: true` for the domain in `run.json`.

**A.3 Resolution.** For every name: A, AAAA, CNAME (the full chain), and for the root only MX, NS and TXT — TXT kept only where it begins `v=spf1` or `v=DMARC1`, everything else discarded unread. Query a public recursive resolver (1.1.1.1, fall back 8.8.8.8), 5 s timeout, one retry, at most 20 in flight. NXDOMAIN and SERVFAIL are rows with `rr_status` set; nothing is retried a third time.

**A.4 Attribution, in this order, stopping at the first hit.** (1) The CNAME chain against `R&D/Hyperscaler-dependence/saas-targets.csv` — a suffix table (`outlook.com`, `mail.protection.outlook.com`, `googlehosted.com`, `ghs.googlehosted.com`, `azurewebsites.net`, `cloudapp.azure.com`, `trafficmanager.net`, `cloudfront.net`, `elb.amazonaws.com`, `amazonaws.com`, `salesforce.com`, `force.com`, `zendesk.com`, `cloudflare.net`, `akamaiedge.net`, `edgekey.net`, `fastly.net`, `incapdns.net`, `wixdns.net`, `github.io`, `netlify.app`, `vercel.app`, plus MX targets `protection.outlook.com`, `aspmx.l.google.com`, `pphosted.com`, `mimecast.com`, `mimecast.co.za`, `messagelabs.com`, `barracudanetworks.com`). (2) Every A/AAAA address against the range files: AWS `https://ip-ranges.amazonaws.com/ip-ranges.json` (region per prefix), Google `https://www.gstatic.com/ipranges/cloud.json` (scope per prefix) and `goog.json`, Cloudflare `https://www.cloudflare.com/ips-v4` and `ips-v6`, Oracle `https://docs.oracle.com/iaas/tools/public_ip_ranges.json`, and Azure's Service Tags Public JSON, whose download link changes weekly and is taken from `https://www.microsoft.com/en-us/download/details.aspx?id=56519` — the one awkward fetch; if it fails, run with the last cached copy and record its date. (3) RDAP for the address's registered owner and ASN, through `https://rdap.org/ip/{ip}` (which bootstraps to AFRINIC, RIPE, ARIN, APNIC or LACNIC), with `https://stat.ripe.net/data/network-info/data.json?resource={ip}` as the ASN fallback; every answer cached under `R&D/Hyperscaler-dependence/cache/` and never re-fetched inside 30 days. (4) The ASN against `R&D/Hyperscaler-dependence/asn-owners.csv`. An ASN not in the file gets `category: unattributed`, and the run appends it to `asn-owners.csv` with the RDAP owner name and an empty category for hand classification — so the file grows, and the next run attributes what this one could not.

**A.5 Categories.** Exactly the eleven of the design note §3, as slugs: `us-hyperscaler-africa`, `us-hyperscaler-offshore`, `us-saas`, `chinese-cloud`, `commercial-host`, `cdn-origin-unknown`, `african-colo`, `national-dc`, `telco-isp`, `self-hosted`, `unresolved` — plus `unattributed` for A.4(4), which is a working state and not a finding. `self-hosted` is set when the RDAP owner name matches the institution (normalised, token overlap ≥ 2) or the ASN is listed against it in `asn-owners.csv`. Region is recorded wherever a range file gives one; an Azure tag, an AWS `region` and a Google `scope` all map to the provider's region name as published, and the African regions are `af-south-1`, `southafricanorth`, `southafricawest`, `africa-south1`, and any Local Zone whose name contains `los` (Lagos) or `cpt` (Cape Town).

**A.6 Outputs.** `nodes.csv`: `iso3,type,institution,domain,name,source,rr_type,rr_status,target,ip,cname_chain,asn,owner,category,region,provider,scan_date`. `organisations.csv`: one row per institution — `iso3,type,institution,domains,names,routable,us_hyperscaler_share,african_region_share,us_saas_share,cdn_share,national_or_self_share,unattributed,mail_provider,mail_security,tangled_hybrid,scan_date` — where `mail_provider` is read from the root MX (`m365`, `google`, `self`, `other:<owner>`, `none`), `mail_security` from an MX or SPF include naming Mimecast, Proofpoint or similar, and `tangled_hybrid` is true when the institution has at least one `national-dc` or `self-hosted` record and at least one `us-hyperscaler-*` record. `run.json`: the ISO3, the scan date, each range file's fetched date, per-domain `wildcard` and `ct_status`, the counts, and the country roll-up. Every figure carries `scan_date`; nothing is undated.

**A.7 Limits.** At most 20 queries in flight; one crt.sh call per domain; RDAP at most 2 a second, cached. No HTTP request to any name under an institution's domain, ever — that is what keeps this passive. No port scans, no banner grabs, no probing of anything that resolves.

## Step 0 — the input exists and is well-formed

```bash
f="R&D/Hyperscaler-dependence/scan/${ISO3}/institutions-${ISO3}.csv"
[ -e "$f" ] || { echo "SCAN STOP: $f not found"; exit 1; }
head -1 "$f" | grep -q '^type,institution,domain,email_domain,status,note$' || { echo "SCAN STOP: $f has the wrong columns"; exit 1; }
grep -q "^${ISO3}," lookups/countries.csv || { echo "SCAN STOP: ${ISO3} not in lookups/countries.csv"; exit 1; }
```

Then commit anything outstanding in `R&D/Hyperscaler-dependence/` and the scan's own files, by explicit path — never `git add -A`, which sweeps in whatever else is in the tree: `git add R\&D scripts/hyperscaler-scan.py && git diff --cached --quiet || git commit -m "Commit outstanding work before scan"`.

## Step 1 — refresh the reference data

The script does this itself on start: it fetches the range files of A.4(2) into `R&D/Hyperscaler-dependence/ranges/` (a copy under a day old is reused), each saved with the date in `run.json`. A file that will not fetch is used from cache with its old date recorded; a file with no cache either is a stop for that provider only — its category is not assigned this run and `run.json` says so.

## Step 2 — scan

```bash
python scripts/hyperscaler-scan.py "R&D/Hyperscaler-dependence/scan/${ISO3}/institutions-${ISO3}.csv"
```

Announce the country by name as it starts. A domain whose root returns NXDOMAIN on A, AAAA and MX alike is written to `nodes.csv` with `rr_status: nxdomain` and its `status` in the input file set to `dead` in Step 4.

## Step 3 — read what came out

Before writing anything, read `organisations.csv` end to end and `nodes.csv` for every institution with `unattributed > 0`. Three things to look for, none of which changes the data: an institution whose every record is `unattributed`, which usually means its ASN is missing from `asn-owners.csv` and is the first thing to fill — classify the rows the run appended there, then `python scripts/hyperscaler-scan.py "R&D/Hyperscaler-dependence/scan/${ISO3}/institutions-${ISO3}.csv" --reattribute`, which re-runs attribution over today's `nodes.csv` without touching DNS; a domain whose records point somewhere no institution of that type should be — a gambling host, a parked page, a country it has no business in — which is a finding and goes in the note under Step 5; and a category share that looks wrong for the country, which is a reason to re-read the rows, not to adjust them.

## Step 4 — write back to the input file

The script does this at the end of the scan; check the diff. For each domain scanned: `status` becomes `scanned YYYY-MM-DD` (or `dead`); `email_domain`, where blank, becomes the domain the root MX serves, or stays blank if there is no MX. Nothing else in the input file is touched — the institution names and notes are Bill's.

## Step 5 — log, message, commit

One log line: `python scripts/log-line.py scan "{ISO3}: NN institutions, NN names, NN routable, NN% US hyperscaler, NN unattributed"`.

A message in `logs/messages-for-bill.md` only for a finding under Step 3 that is irreversible or already public — a site serving someone else's content is public; a high hyperscaler share is not. Within the cap; at the cap, the finding goes in `run.json` under `findings` instead.

Commit `R&D/Hyperscaler-dependence/scan/{ISO3}/`, the input file, `R&D/Hyperscaler-dependence/asn-owners.csv` and `R&D/Hyperscaler-dependence/saas-targets.csv`, never `ranges/` or `cache/`: `git add "R&D/Hyperscaler-dependence/scan/${ISO3}" "R&D/Hyperscaler-dependence/scan/${ISO3}/institutions-${ISO3}.csv" "R&D/Hyperscaler-dependence/asn-owners.csv" "R&D/Hyperscaler-dependence/saas-targets.csv" && git commit -m "Scan ${ISO3}: NN institutions, NN% US hyperscaler"`. The commit body carries every judgement the run made — an ASN classified by hand, a wildcard domain, a range file used from cache.

## On screen — one line and nothing else

`{ISO3} · institutions NN · names NN · routable NN · us-hyperscaler NN% (african region NN%) · m365 NN · google NN · cdn-fronted NN% · national/self NN% · unattributed NN`

## After the two pilot countries

Once KEN and NGA (or whichever two Bill names) have run, write `R&D/Hyperscaler-dependence/pilot-note.md`: the five questions of the design note §5.7, each answered with the figure that answered it, and a recommendation on whether the roll-up is a measure for the digital sovereignty indicator or evidence for it. That note is written once, after the pilot, and is the only narrative this runbook produces.
