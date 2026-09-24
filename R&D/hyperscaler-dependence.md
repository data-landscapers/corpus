---
type: design-note
title: hyperscaler-dependence.md — mapping African governments' and banks' hyperscaler dependence from DNS
last_reviewed: 2026-09-24
status: proposal; pilot not yet run
---

# Hyperscaler dependence — a DNS-based measure, and a pilot

*(Written 2026-09-24 in Cowork after Bill flagged Computer Weekly's data dive on UK police forces' hyperscaler dependence and asked whether the method transfers to African governments and banks. It does. This note records the method, what has to change for Africa, where the result fits Corpus, and a two-country pilot. Nothing here is built.)*

## 1. What Computer Weekly did

The piece (Computer Weekly, September 2026, "Data dive: Mapping UK police forces' hyperscale dependence") used no FOI requests, procurement registers or spending data. It took the 48 UK police forces and enumerated each one's DNS footprint three ways: the root records, a dictionary sweep of likely subdomains (`mail.`, `vpn.`, `citrix.`, `crm.` and so on), and passive Certificate Transparency logs. That produced 3,822 records. Each resolvable record was mapped to the registered owner of its IP address through RDAP against the regional internet registries, then classified into four buckets: US hyperscaler (Microsoft, Amazon, Google), other cloud, CDN or SaaS, third-party host or ISP, and force-owned infrastructure. TXT records (1,234 of them) were excluded as non-routable.

Dependence was reported as plain shares: 47 of 48 forces connect to at least one US hyperscaler; 46 of 48 route mail through Microsoft 365; 36.2 % of routable records point at Microsoft, Amazon or Google; Microsoft accounts for 773 routable records against Amazon's 161 and Google's 2; and 46 of 48 sit in a "tangled hybrid" of UK-sovereign and US-Cloud-Act-exposed infrastructure. The two outliers were the Ministry of Defence Police (no hyperscaler at all) and Derbyshire (fully US-dependent). The authors called the figures a lower bound, since an unresolved record can only add, and made no causal claims.

## 2. Why it transfers

Everything the method consumes is global public infrastructure that no African organisation has to cooperate with: DNS itself, Certificate Transparency logs (crt.sh), RDAP (AFRINIC for African address space, the other four registries for everything else) and the hyperscalers' own published IP-range files. That last input matters more here than it did for the UK: the range files are more reliable than RDAP for attribution, and they carry the **region** — so `af-south-1`, Azure South Africa North and West, and `africa-south1` can be told apart from an EU or US region. For a state with a residency rule (Nigeria's NDPA, Kenya's DPA, POPIA) that distinction is most of the story, and the UK study did not need it because for the UK everything is offshore anyway.

The method is also cheap, scriptable and repeatable, and every input is passive: DNS queries, log reads and published files. No port scanning, no probing, nothing that touches a login. A re-run a year later gives a trajectory, which is the thing nobody else will hold.

## 3. What changes for Africa

**The classification is richer.** US hyperscaler is one bucket among several, and *where* the state's edge actually lives is a more interesting finding than *whether* it touches Microsoft. The scheme for the pilot:

| category | examples | how attributed |
|---|---|---|
| US hyperscaler, African region | AWS af-south-1, Azure South Africa North/West, Google africa-south1 | range file, region field |
| US hyperscaler, offshore region | AWS eu-west-1, Azure West Europe, Google europe-west | range file, region field |
| US SaaS and platform | Microsoft 365, Google Workspace, Salesforce, Zendesk | MX, SPF, CNAME targets |
| Chinese cloud | Huawei Cloud (Johannesburg, Cairo), Alibaba Cloud | RDAP and ASN (no published range file) |
| European and other commercial host | OVH, Hetzner, Contabo, DigitalOcean | RDAP and ASN |
| CDN or edge, origin unknown | Cloudflare, Akamai, Fastly, Imperva | range file, then stop — the origin is hidden |
| African colocation and regional cloud | Teraco, Africa Data Centres, Rack Centre, Raxio, iXAfrica, Liquid | ASN lookup table, hand-kept |
| National government data centre or cloud | Galaxy Backbone, Konza, Rwanda NDC, Diamniadio, SITA | ASN lookup table, hand-kept |
| Telco and ISP hosting | MTN, Safaricom, Airtel, Orange, Seacom | ASN lookup table, hand-kept |
| Self-hosted | the organisation's own AFRINIC allocation or ASN | RDAP owner matches the organisation |
| Unresolved or dead | NXDOMAIN, no A record, RFC 1918 | resolver result |

**Use MX and SPF, not only A records.** Computer Weekly dropped TXT records. For Africa the SPF `include:` lines are one of the cleanest signals of Microsoft 365 against Google Workspace against a self-hosted Zimbra or Exchange, and the mail estate is itself a fair proxy for the office estate. Read TXT for SPF and DMARC; ignore the rest of it.

**Cloudflare hides origins.** A large share of African government and bank front doors sit behind it, so the hyperscaler share will be a harder lower bound than in the UK study. Report *CDN-fronted, origin unknown* as its own category and never fold it into anything else.

**Seed lists have to be built.** Government domain conventions are inconsistent (`.gov.ng`, `.go.ke`, `.gov.za`, `.gouv.sn`, `.gouv.ci`, and plenty on `.org` and `.com`), and no registry of them exists. Banks come from the central bank's licensed-institution list. That is a one-off lookup per country, kept as a dataset input, and it is where most of the hand work is.

**Say what DNS sees.** It measures the internet-facing edge — mail, web, VPN, citizen portals, internet banking. It does not see where core banking, the civil registry or IFMIS actually runs, and for banks that is mostly on-premise or in colocation. The published framing is *public-facing dependence*; claiming more would be the overreach the currency rules exist to catch.

## 4. Where it fits

**It is a dataset, not a source.** It follows `documentation/datasets.md`: a master in `outputs/datasets/hyperscaler-dependence/`, a `metadata.csv`, a `considered`-style resume file, dated editions under `site/`, every change logged with its source. Corpus owns it and maintains it. The scan script lives in `scripts/`. Once published it is Bill's own analysis and admissible into OSINT as such, under `geopol.usa`, `geopol.sovereignty` and `infra.store`, cited by author and tagged as analysis.

**It bears on the digital sovereignty indicator.** `indicator-digital-sovereignty.md` §3 considered a measure form — share of state data hosted under national jurisdiction — and set it aside because no country publishes it and the base cannot compute it. This is the computable proxy for the hosting part of that question: not the share of state *data*, which stays unknowable, but the share of the state's *public-facing estate* resolving to a US hyperscaler, and to an African region of one. It does not replace the instrument ladder — §5's "what is never evidence" still holds, and a hyperscaler region announced is still not evidence — but a state whose ministries all resolve to Azure West Europe has a fact on record that its hosting policy has to answer to, and the qualifier can say so. Whether it becomes a `measure` row in the frame or stays as evidence for the instrument is decided after the pilot, not before (§5.7).

**It is not a maturity-assessment task.** It is R&D, run when the assessment is not occupying the day.

## 5. The pilot

**5.1 Countries.** Kenya and Nigeria. Between them they exercise every category in §3: a hyperscaler presence at different depths (Nigeria has an AWS Local Zone in Lagos and Galaxy Backbone; Kenya has Konza and Safaricom hosting, with the nearest hyperscaler regions in South Africa), heavy Cloudflare use, active national data-centre programmes, two large banking sectors with published licence lists, and two residency regimes.

**5.2 Seeds.** Per country, about fifteen government organisations and the ten largest banks by assets. Government: presidency, finance, ICT, interior, health, education, the revenue authority, the central bank, the data protection authority, the ID authority, the e-government portal, the procurement portal, the police, parliament, the judiciary and the statistics office — taking whichever domains each actually uses, which is the lookup. Banks: from the central bank's licensed-institution list. Seeds go in `seeds.csv` with organisation, country, sector (`government` or `bank`), domain, and the source of the domain.

**5.3 Collection.** For each seed domain: the root records (A, AAAA, MX, NS, CNAME, TXT for SPF and DMARC only); a subdomain dictionary of roughly 500 names, the standard list plus an African-service list (`ecitizen`, `ifmis`, `portal`, `webmail`, `zimbra`, `owa`, `autodiscover`, `vpn`, `citrix`, `remote`, `ibank`, `internetbanking`, `mobile`, `api`, `ussd`, `sip`); and every name crt.sh returns for `%.domain`. Resolve everything. Rate-limit against each authoritative nameserver; this is a few thousand benign queries per organisation over an hour, not a flood.

**5.4 Attribution.** For each IP, in order: the published range files — AWS `ip-ranges.json` (region per prefix), Azure Service Tags (region per tag), Google `cloud.json` (scope per prefix), Cloudflare, Oracle; then RDAP for the owner; then the ASN against a hand-kept `asn-owners.csv` mapping ASN to owner and category, which grows as the pilot finds owners. A record whose CNAME chain ends in a known SaaS target is attributed to that SaaS before its IP is looked at.

**5.5 Measures.** Per organisation: records found, routable records, share by category, mail provider, CDN-fronted share, and the tangled-hybrid flag (any national or self-hosted record and any US-hyperscaler record). Per country: the same rolled up, split government against bank. Every figure carries the scan date.

**5.6 Outputs.** `nodes.csv` (one row per record: name, type, target, IP, ASN, owner, category, region, source of the name, scan date); `organisations.csv` (one row per organisation with §5.5); `seeds.csv`; `asn-owners.csv`; `metadata.csv`; and a pilot note in this folder recording what came out and what §5.7 decided. The script, `scripts/hyperscaler-scan.py`, takes a seeds file and writes the two CSVs; it resumes from `nodes.csv`.

**5.7 What the pilot decides.** Whether the §3 categories hold or need merging; how much Cloudflare hides and whether the residue is still a defensible share; whether the government-against-bank split shows anything; whether the subdomain dictionary earns its cost over Certificate Transparency alone; and whether the per-country roll-up is sound enough to sit in the frame as a measure or belongs as evidence for the instrument only. Each is answered in the pilot note with the figure that answered it.

**5.8 Effort.** Seed lists half a day, the script a day, the run a few hours on the laptop, review half a day. Three days spread across whichever days the assessment leaves free.

**5.9 Limitations, stated on the page.** Lower bound throughout; public-facing edge only; CDN-fronted origins unknown; a subdomain dictionary finds what it names; an organisation on shared hosting attributes to the host, not to any cloud; the scan date is the only date any of it carries.

## 6. After the pilot

If §5.7 holds up: all 54 states, the top ten banks in each, an annual re-run for trajectory, and the obvious extensions — data protection authorities and ID authorities as a sector of their own, stock exchanges, national payment switches. Each is a seed-list change, not a method change.
