---
title: Who hosts the state's front door — methodology
date: 2026-09-29
author: Bill Anderson
source: R&D/Hyperscaler-dependence/ (HYPERSCALER-SCAN.md, HYPERSCALER-DRAIN.md, scripts/hyperscaler-scan.py, scripts/hyperscaler-report.py)
---

# Who hosts the state's front door: methodology

29 September 2026 · Bill Anderson

This note describes how the 54 country fact sheets were made: which institutions were chosen, how their internet names were found and looked up, how each address was assigned to a host, and what the figures do and do not show. It is written for readers who want to check the work or doubt it. Every file and script named here is in the Corpus repository, and every figure in the fact sheets can be recomputed from them.

## 1. What is measured

For each strategic institution in a country, the scan asks one question: **which organisation runs the servers that the institution's public internet names point to?** A public name is a website, a mail server, a login portal or anything else the institution has published in the domain name system (DNS).

The unit of measurement is a **working address record**: one DNS record (A, AAAA, MX or NS) under an institution's domain that resolved to a server. Each record is assigned to a host and a category. A country's figures are shares of its working address records.

This measures the public edge of the state. It does not measure where databases, core banking systems, ID registers or payroll run. Those sit behind the edge and leave no trace in public DNS.

## 2. Why this approach

The method follows Computer Weekly's September 2026 study of UK police forces. It needs no cooperation from anyone, no freedom-of-information requests and no procurement records. It uses only four public sources:

- the domain name system itself, queried through a public resolver;
- Certificate Transparency logs, which record every publicly trusted website certificate;
- the internet registries (AFRINIC, RIPE, ARIN, APNIC, LACNIC), which record who holds each block of addresses;
- the address lists that Amazon, Microsoft, Google, Oracle and Cloudflare publish for their own networks.

These sources are global and the same for every country. That makes the method repeatable, and it makes one country comparable with another. It also means the results depend on the quality of those sources, which section 10 covers.

## 3. Choosing the institutions

**The list of types.** `strategic-institutions.csv` defines 36 types of institution in five tiers:

| Tier | Types | The types |
| --- | --- | --- |
| 1 Sovereign spine | 14 | Presidency, Parliament, Foreign Affairs, Defence, Armed Forces, Police, Justice, Treasury, Revenue, Customs, Intelligence, Interior, Central Bank, Commercial Banks |
| 2 Citizen data | 8 | Civil registry and ID, Data protection, Electoral commission, Statistics, Immigration, Health, Social protection, Land registry |
| 3 Money and critical services | 8 | Payment switch, Stock exchange, Securities regulator, Pension or wealth fund, Procurement, Energy utility, Ports, State-owned telco |
| 4 Digital state | 4 | E-government agency, National data centre, Cybersecurity agency, Communications regulator |
| 5 Oversight | 2 | Audit office, Anti-corruption commission |

The same list was used in every country. Commercial Banks means the ten largest banks by assets, from the central bank's list of licensed banks or the most recent published ranking. Where a sector has fewer than ten banks, all are included.

**Finding each institution's domain.** For each country and type, the institution and its main domain were identified by knowledge and web search. Each domain was confirmed by fetching its homepage once. This is the only time any request went to an institution's own server, and it happened before the scan. The scan itself made none (section 11).

**Coverage is recorded, not assumed.** A type with no institution in a country, or whose domain could not be found, has a row marked `absent` with the reason. Where one institution covers two types (a revenue authority that also runs customs), the second type is marked `absent` with a note naming the row that covers it. A domain that no longer resolves is marked `dead`.

Across the 54 countries there are 2,425 seed rows: 1,830 scanned, 568 absent and 27 dead. 1,857 domains were scanned. The lists are in `scan/{ISO3}/institutions-{ISO3}.csv`.

**What a sceptic should know.** The lists were drawn up for this scan. A domain was checked to exist and to belong to the institution, not confirmed with the institution as its main one. Some institutions use several domains and only one or two were seeded. A missing domain lowers the count for that institution. It does not move it into another category.

## 4. Finding the names

For each seeded domain the scan collects names from three sources. Each name records which sources found it.

1. **The root.** The domain itself and `www`.
2. **A dictionary.** 500 common names (such as `mail`, `vpn`, `portal`, `webmail`, `api`), including names common in African government and banking (`ecitizen`, `ifmis`, `ussd`, `etender`, `ibank`). A dictionary name is kept only if it resolves to an address.
3. **Certificate Transparency.** One query per domain to crt.sh, which lists every name that has appeared on a public certificate under the domain. Names found only here are kept even if they no longer resolve, so that expired names are visible.

**Wildcards.** Some domains answer for any name, real or not. Before using the dictionary, the scan looks up a random 16-letter name under the domain. If it resolves, the domain is a wildcard, and dictionary names are kept only where Certificate Transparency also lists them. 71 of the 1,857 domains were wildcards.

**Parent zones.** Where a seeded domain is the parent of other seeded domains (for example `gov.za` above `treasury.gov.za`), it is scanned at the root only. Otherwise its dictionary and certificate names would count every other institution's estate as its own.

**Certificate Transparency failures.** crt.sh is a free public service and it often fails under load. Each call is retried once after 30 seconds. On a second failure the domain is scanned without it and `ct_status: failed` is recorded in the country's `run.json`. This happened for 97 of the 1,857 domains. Those institutions are under-counted, mostly by the loss of old or rarely used names.

The scan found 61,106 distinct names. 33,939 of them resolved to a working server.

## 5. Looking up the names

Each name is looked up for A (IPv4 address), AAAA (IPv6 address) and CNAME (alias) records, with the full alias chain followed. The root of each domain is also looked up for MX (mail server), NS (name server) and TXT records. Only TXT records that begin `v=spf1` or `v=DMARC1` are kept; they show which services may send mail for the domain. All other TXT records are discarded unread.

Queries go to Cloudflare's public resolver (1.1.1.1), with Google's (8.8.8.8) as a fallback. Each query has a five-second timeout and one retry. No more than 20 queries are in flight at once. A failed lookup is recorded as a row with its result (`nxdomain`, `noanswer`, `servfail`, `timeout`), not dropped.

## 6. Assigning each address to a host

Each working record is assigned in this order. The first rule that matches is used.

1. **The alias chain against known services.** If a name's alias chain ends at a known service, the record is assigned to it: for example `mail.protection.outlook.com` (Microsoft 365), `ghs.googlehosted.com` (Google), `cloudflare.net` (Cloudflare), `mimecast.com` (Mimecast). The 44 suffixes are in `saas-targets.csv`. Some suffixes name a cloud platform (`azurewebsites.net`, `cloudfront.net`) but not a region; for these the address decides the region in step 2.
2. **The address against the cloud companies' published ranges.** Amazon, Microsoft (Azure Service Tags), Google Cloud, Google's other services, Oracle and Cloudflare each publish the address blocks they use, most with the region each block serves. An address inside one of these blocks is assigned to that company and region. The range files were fetched on 28 and 29 September 2026, and each country's `run.json` records the dates it used.
3. **The address against the internet registries.** Otherwise the scan asks the registries, through RDAP and RIPEstat, who holds the address and which network (ASN) announces it. Answers are cached for 30 days.
4. **The network against a hand-kept table.** The network number is looked up in `asn-owners.csv`, which assigns each network a category. When the scan meets a network not yet in the table, it adds it with the category blank.

**The hand-kept table.** `asn-owners.csv` holds 725 networks. Each was classified from its registered owner name, with at most one further lookup. The conventions were fixed before classification: a telecoms company is `telco-isp`; a bank's or company's own network is `african-colo`; a state body's own network is `national-dc`; a research network is `telco-isp`; a non-US software company is `commercial-host`. 39 networks could not be placed with confidence. They were given the most neutral nearby category, usually `commercial-host`, and are marked `unverified` in the table. The table is open, and anyone who disagrees with a line can change it and re-run the attribution without new lookups (section 12).

**Self-hosting.** A record is `self-hosted` when the registered owner of the address or the network matches the institution: two or more shared distinctive words in the names, or the domain's own label (such as `kra`) appearing in the owner's name. This rule is simple, and it can miss an institution that registered its addresses under another name. A miss moves the record into `national-dc` or `african-colo`, which are also counted as national or African, so the national share is little affected.

**What was left unassigned.** After classification, 76 of 65,534 working records (0.1%) could not be assigned, mostly addresses the registries returned no network for. The drain required 2% or less in every country. The highest was 0.9%.

## 7. The categories

| Category | Meaning | How it is assigned |
| --- | --- | --- |
| US cloud, in Africa | Amazon, Microsoft, Google or Oracle cloud in an African region (Cape Town, Johannesburg, Lagos) | published ranges and region |
| US cloud, outside Africa | the same companies anywhere else, including their worldwide delivery networks and addresses whose region is not published | published ranges, or the company's own network number |
| US online services | Microsoft 365, Google Workspace, Salesforce and similar | alias chain and mail records |
| Chinese cloud | Huawei, Alibaba, Tencent | network number |
| Other foreign hosting firms | commercial hosts such as OVH, Hetzner, DigitalOcean, GoDaddy | network number |
| Behind a shield | Cloudflare, Akamai, Imperva, Fastly and similar, which hide the real host | published ranges or network number |
| African data centres and IT firms | African colocation, cloud and IT service companies, and banks' own networks | network number |
| Government data centres | national data centres and state IT agencies | network number |
| Telecoms companies | telecoms operators and internet providers | network number |
| The institution's own systems | the institution's own address block or network | owner name match |
| Private or unusable | an address that cannot be reached from the internet | the address itself |

Three choices affect the headline figures and are stated here so they can be challenged:

- **Worldwide delivery networks count as outside Africa.** Amazon CloudFront, Azure Front Door and Google's global front ends serve each visitor from a nearby copy. They have no single location, and they are never counted as African.
- **Microsoft 365 is counted as a US online service, not as US cloud,** where its alias chain identifies it. Microsoft addresses outside the published Azure ranges, which are often Microsoft 365 too, are counted as US cloud with the region unknown. The US cloud share and the US online services share should be read together.
- **IBM, Rackspace and other US hosts count as other foreign hosting firms,** not US cloud. Only Amazon, Microsoft, Google and Oracle are counted as US cloud.

## 8. The measures

**Working addresses.** A, AAAA, MX and NS records that resolved. A name with both an IPv4 and an IPv6 address, or with several addresses, counts once per address. Most shields and delivery networks return several addresses for each name. This gives more weight to names behind them than a count of names would. The choice keeps the unit the same for every country. The per-name view can be computed from `institution-hosting-nodes.csv`.

**Shares.** Each share is a category's working addresses divided by all working addresses, for an institution, a sector or a country. US cloud in Africa is part of the US cloud share, not added to it.

**Email provider.** Read from the MX records of the seeded domain. If they point at Microsoft 365 or Google, that is the provider. If the mail passes through a filtering service (Mimecast, Proofpoint, Cisco and others), the SPF record is read to find the provider behind it; where it names none, the provider is reported as not visible. Otherwise the provider is the host the mail servers resolve to.

**Mixed home and US cloud.** An institution with at least one record on a government data centre or its own network and at least one on US cloud.

**Banks against government.** Commercial Banks are the bank sector. Every other type counts as government, including central banks, payment switches, stock exchanges and state-owned companies.

**Rankings.** Each fact sheet ranks its country among all countries whose attribution was complete when it was written. All 54 were. A country with few institutions or few addresses can rank high or low on very little. Eritrea, with five institutions and 47 working addresses, ranks first on US cloud share.

## 9. How the work was checked

- **Stepwise order.** All 54 countries finished each step before any country started the next. The table of network owners was completed before any country's attribution was finalised, so every country was assigned with the same table.
- **Attribution threshold.** A country passed only with unattributed records at 2% or less of its working addresses. All 54 passed.
- **Rescans where coverage failed.** Kenya and Nigeria were scanned again on 29 September after two missing institutions were added. Where Certificate Transparency failed on a large estate, the domain was re-run until it returned, because one failure removed a fifth of Kenya's addresses.
- **Nothing edited by hand.** No figure in a fact sheet was typed. The fact sheets are generated from the scan files by `scripts/hyperscaler-report.py`.

## 10. Limits, and which way they push the figures

| Limit | Effect |
| --- | --- |
| Shields hide the real host | US cloud share is a **minimum**. Anything behind a shield could be on US cloud. In some countries half the estate is behind a shield. |
| Mail filters hide the mail provider | Microsoft 365 and Google counts are **minimums**. |
| Only the public edge is visible | Says nothing about core systems. A body can run its website abroad and its database at home, or the reverse. |
| One lookup location | DNS answers can depend on where the question is asked. A resolver elsewhere may be sent to a different copy of a site behind a delivery network. Region shares for delivery networks are the least stable figure. |
| Addresses, not importance | An institution with many test, marketing or old names weighs more than one with few. |
| Certificate Transparency failures | 97 domains were scanned without certificate names, so their institutions are **under-counted**. The failures are listed in each `run.json`. |
| Seed lists | A missing domain lowers an institution's count. The choice of the ten largest banks favours large, often multinational, banks. |
| Hand-kept network table | 39 of 725 networks are marked unverified. A wrong line misplaces every address on that network, in every country. |
| Owner-name matching | Can miss self-hosting under another name. Such records mostly land in other national categories. |
| Snapshot | Every figure is as of the scan date: 28 September 2026 for South Africa, 29 September for the other 53 countries. |

Three objections come up often.

*"A share of addresses is not a share of dependence."* Agreed. The figure measures where an institution's public estate is hosted. It is evidence about dependence, not a measure of it. A ministry whose one website is on a US cloud may depend on it less than one whose mail runs there.

*"Cloudflare is American too."* It is, and so are Akamai, Imperva and Fastly. They are kept separate because they pass traffic on to an origin server they do not reveal. Folding them into US cloud would double the US figure in some countries on an assumption. They are shown as their own category so a reader can combine them if they choose.

*"The African cloud regions are new, so of course they are little used."* The scan records use on the scan date, not intentions. Where US cloud is used, the fact sheets report how much of it is in Africa.

## 11. What the scan did not do

The scan is passive. It sent DNS queries to public resolvers, one query per domain to crt.sh, lookups to the internet registries, and downloads of the cloud companies' published range files. It made no web request, port scan or login attempt against any host under an institution's domain, and it did not probe anything that resolved. The only direct contact with any institution was the single homepage fetch that confirmed each domain before the scan.

Some names point at a cloud name that has been deleted and that anyone could register. Whoever registered it could publish content under the institution's name. The scan found 13 such names in nine countries. The fact sheets count them but do not name them, and they were passed on for disclosure.

## 12. Reproducing it

Everything is in `R&D/Hyperscaler-dependence/` in the Corpus repository.

| File | What it is |
| --- | --- |
| `strategic-institutions.csv` | the 36 types |
| `scan/{ISO3}/institutions-{ISO3}.csv` | the seed list for each country, with status and notes |
| `subdomains.txt`, `saas-targets.csv`, `asn-owners.csv` | the dictionary, the service suffixes and the network table |
| `scan/{ISO3}/nodes.csv` | every record for the country, with its host and category |
| `scan/{ISO3}/organisations.csv` | the figures for each institution |
| `scan/{ISO3}/run.json` | range file dates, wildcards, Certificate Transparency failures, country totals and withheld findings |
| `institution-hosting.csv`, `institution-hosting-nodes.csv` | all 54 countries in one file each, one row per institution and one per record, with `-metadata.csv` files that explain every column |
| `HYPERSCALER-SCAN.md`, `HYPERSCALER-DRAIN.md` | the runbooks the scan was run from |

To scan a country: `python scripts/hyperscaler-scan.py "R&D/Hyperscaler-dependence/scan/KEN/institutions-KEN.csv"`. This needs Python 3 with `dnspython` and `requests`, and takes 10 to 60 minutes a country, mostly waiting on crt.sh.

To re-assign an existing scan after changing `asn-owners.csv` or `saas-targets.csv`, with no new lookups: add `--reattribute`. To rebuild a fact sheet: `python scripts/hyperscaler-report.py KEN`. To rebuild the combined files: `python scripts/hyperscaler-combine.py`.

A new scan will not give identical figures. DNS changes daily, certificates are issued and expire, and the cloud companies' ranges change weekly. The method is repeatable; a given day's results are not.
