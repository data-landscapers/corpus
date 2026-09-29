---
type: runbook
reader: cc
title: Drain one step of the hyperscaler scan across all 54 countries — instruction for Claude Code
last_reviewed: 2026-09-28
status: R&D; in use from 2026-09-29
---

# Hyperscaler drain — runbook for Claude Code

*(Bill's prompt is **"Continue draining HYPERSCALER step NN for all countries until I request you to stop cleanly."** This file says what that means: which country is next, what one unit of work is at each step, what "done" is, and how to stop. The state is one file, `R&D/Hyperscaler-dependence/progress.csv`, and nothing else — not memory, not the log, not a scratch list. `HYPERSCALER-SCAN.md` is the scan itself and `hyperscaler-dependence.md` the design; read both once per session. The whole exercise is step-wise on purpose: every country finishes step NN before any country starts step NN+1, because attribution improves with coverage and a report written early is a report written against a thinner lookup than the ones after it.)*

## The checklist

`progress.csv`: `seq,iso3,country,group,s01_seeds,s02_scan,s03_classify,s04_report,note`. A step cell is blank (not started), a date `YYYY-MM-DD` (done), `blocked: <reason>` (tried twice, moved on) or `skip: <reason>` (Bill's call, never CC's). `group` orders the work by domain convention — anglophone, francophone, North Africa, lusophone and hispanophone — because what a session learns on Senegal transfers to Côte d'Ivoire and not to Mozambique. **Re-read the file at the start of every session and before every unit**: Bill edits it too.

**The next job is the first row in `seq` order whose step NN cell is blank and whose step NN−1 cell is a date.** For step 01 every blank row is eligible. A `blocked:` row is not eligible until Bill clears it. When no row is eligible, say so in the closing line and stop — do not start step NN+1.

## One unit of work, and what done means

Every unit is one country. It ends with the cell written, the artefacts committed in one commit named `HYPERSCALER NN {ISO3}: <what>`, and one log line `python scripts/log-line.py hyperscaler "{NN} {ISO3}: <counts>"`. A unit that fails is retried once in the same session; a second failure writes `blocked: <one line>` in the cell, commits that, and the drain moves to the next row. Nothing is ever left half-written: a cell is blank or it is final.

### Step 01 — seeds: `institutions-{ISO3}.csv`

Build the file from `strategic-institutions.csv`, columns `type,institution,domain,email_domain,status,note` exactly as `HYPERSCALER-SCAN.md` A.1 states them. One row per domain; an institution with two domains has two rows; a type with no institution in this country, or one whose domain cannot be found, gets one row with `domain` blank and `status: absent` and the reason in `note`, so coverage is visible and a blank is never ambiguous. Banks: the ten largest by assets from the central bank's licensed-institution list or the most recent published ranking, cited in `note` on the first bank row; fewer than ten where the sector has fewer. Search effort by group: anglophone and North Africa, knowledge first and a search only where a guess fails; francophone, one search per institution is normal; lusophone and hispanophone and the fragile states, an agent run per country is warranted, and gaps are recorded as `absent`, not chased. Every domain with a value is confirmed by fetching its homepage — `status: confirmed YYYY-MM-DD` — and **no DNS lookup of any kind**, which is step 02's. `email_domain` is filled only where it is known to differ from `domain`; otherwise blank for step 02 to fill. Lint before the cell is written: exact header; no duplicate `domain`; at least one row per type in `strategic-institutions.csv`; no more than twelve bank rows. Done = the file lints and is committed.

### Step 02 — scan

`python scripts/hyperscaler-scan.py "R&D/Hyperscaler-dependence/institutions-{ISO3}.csv"`, exactly per `HYPERSCALER-SCAN.md` Steps 0–5, including its read-back and its write-back to the input file. Done = `scan/{ISO3}/run.json` exists with counts and `organisations.csv` has a row per institution scanned. The screen line is the scan's own. Several countries can run in parallel where crt.sh tolerates it; three at once is the ceiling, and a country whose crt.sh calls fail twice is `blocked: ct`, not retried a third time.

### Step 03 — classify, then re-attribute

This step has a gate that is not per country. **Before the first country**: open `asn-owners.csv`, classify every row whose `category` is blank — RDAP owner name, the ASN's own site if needed, one search at most — into one of the eleven categories, and commit that file alone as `HYPERSCALER 03: classify NN ASNs`. A row that cannot be classified in one move gets `category: commercial-host` and `note: unverified`, which is the conservative option, and is never left blank. Then, per country: `python scripts/hyperscaler-scan.py --reattribute "R&D/Hyperscaler-dependence/institutions-{ISO3}.csv"`, which recomputes `category`, `region` and `provider` in `nodes.csv` and every share in `organisations.csv` from the lookups alone — no DNS, no network, `scan_date` untouched. **If the flag does not exist, build it first**, to that spec, as its own commit, and hold it to `HYPERSCALER-SCAN.md` A.4–A.6. Done = `organisations.csv` shows `unattributed` at 2% of routable or less for the country; above that, `blocked: unattributed NN%` and move on, because the fix is more classification, not another run. When every country with a step 02 date has a step 03 date, the lookup is stable and step 04 may begin.

### Step 04 — report

Write `scan/{ISO3}/report.md` and `report-chart.png` in the exact shape of the three pilot reports — the same sections in the same order: the standfirst, *Where it lives*, *Banks against government*, *Email*, *Institution by institution*, *What stood out*, *What this can and cannot tell you*, the closing path line — with *Institution by institution* always in the type order of `institutions-{ISO3}.csv`, which is the order of `strategic-institutions.csv`; in their voice, for a reader who is not technical, with every figure dated. **Each report is a fact sheet that the continental report cites**: plain, short sentences that state facts. No AI-speak: no scene-setting, no "notably" or "it is worth noting", no rhetorical contrasts, no summing-up line. Keep the explanation of a technical term to a clause, and only where the reader needs it. Comparisons cite only countries whose step 03 cell is a date, and the report says how many that is ("of the 31 countries scanned so far"). A finding under *What stood out* that is irreversible or already public — a hijackable name, a site serving someone else's content — is also a block in `logs/messages-for-bill.md`, within the cap, and the report does not name the address. Done = both files committed. The three pilot reports are refreshed at step 04 like any other country, because they were written before the classification pass.

## Stopping cleanly

When Bill asks to stop: finish the unit in hand — the current country through to its cell, commit and log line — and start no other. At step 02 a scan in progress is left to finish, because it is resumable and a killed scan leaves a half-written `nodes.csv`; if it will run more than ten minutes, say so and let it. Then re-read `progress.csv`, print the closing line, and stop. A session that ends for any other reason — context, an error, the day — stops the same way: the checklist is always true at the moment CC leaves it.

## On screen

At the close of every unit, one line: `HYPERSCALER {NN} · {ISO3} done · {counts}`. At the close of the session, one line and nothing else: `HYPERSCALER step {NN} · done NN/54 · this session NN · blocked NN · next {ISO3 or none}`.

## What the drain never does

Never starts step NN+1 for any country, whatever is eligible. Never edits a `skip:` cell or clears a `blocked:` one. Never re-runs a dated step without Bill's word, except step 03 and 04 for the pilot three, which the checklist says to. Never writes a country's file from another country's — a seed list is built from the country's own institutions, not by editing the neighbour's. Never touches OSINT.
