---
type: spec
title: geopol.sovereignty — the status sub-section: what it says, what it reads, what Not established looks like
reader: cc
last_reviewed: 2026-09-25
---

# `geopol.sovereignty` — the status sub-section

*(Cowork, 2026-09-25, on Bill's framing, register R77. The drafting brief for the `### Digital sovereignty` sub-section of every country status report, written across the 54 units by R78, whose mechanics are the last section of `status-brief-finance-sustain.md`. Three questions — what the section says, what evidence it reads, what *Not established* looks like — under `STATUS-INIT.md`'s rules, which govern this sub-section as they govern the other 38. The indicator it pairs with is `indicator-digital-sovereignty.md`; the outline entry is `status-outline.md` → `geopol.sovereignty`.)*

## The question

**How much of its digital estate does the state control, and on what terms does it depend on the rest?** The sub-section tracks the move away from dependence on hyperscalers and other foreign providers across the whole stack — where state data sits and under whose law; who can run, change and switch off the core systems (identity, payments, the exchange layer, government hosting); the software and licences those systems run on; the compute and models behind the state's AI; and the skills to do any of that without the vendor — and it does so knowing that the destination is not self-sufficiency. Every serious statement of sovereignty on file says the same thing: Rwanda's prime minister puts it as where decisions are made and where value is recorded, not the exclusion of global firms; Sierra Leone's president as sovereignty travelling with the law rather than the building; South Africa's SITA as knowing how services continue when a supplier fails. The mature position is control with portability — a pragmatic, continuing relationship with big tech on terms the state has set and can enforce — and a wall of localisation with nothing behind it is not the top of the ladder. The section's job is to say which of those a country has, from what the state has actually kept and signed.

It is the Geopolitics chapter's one sub-section that names no power. The five actor sub-sections say what the US and its hyperscalers, China, the EU, India and the Gulf have done in the country and what was signed; this one reads the same agreements for their terms, and says what the state has kept for itself when those powers arrived. It is not `gov.protect`, which is the rights of data subjects; not `infra.store`, which is the physical capacity to host; not `gov.regional`, which asks about cross-border transfer rules — though it borrows one fact from each.

## What the section says

**The first sentence carries the news, and the news is a term, a decision or a dependency** — a hosting decree in force, a contract renegotiated to add exit rights, a state discovering that funding a system and owning it were different things, a data-embassy agreement, a national cloud taking the registers in. Never the number of memoranda, never a region announced, never a vendor's investment figure: those are the actor sub-sections' news and establish nothing here.

Then, in the order the evidence dictates, the section establishes five things, and says plainly which of them it cannot.

**Where state data sits and under whose law.** The instrument, if there is one — a data classification, a localisation rule by category or wholesale, a government-cloud or hosting policy — and whether it is in force or stated as a goal. Where the registers, the identity database, the payment switch and the exchange actually run: a national data centre, a domestic operator, a hyperscaler region in-country, a region abroad, an Outpost or local zone on state premises whose control terms are or are not published. Under whose jurisdiction that puts the data, where a source says.

**Who can run and change the core systems.** For identity, payments, the exchange layer and government hosting: whether source code, keys and administrative control are the state's; whether the operating contract carries exit and portability terms; whether the state has the staff to operate without the vendor; whether it has ever changed vendor or brought a system in-house, and what that cost. A licence fee paid to keep using a system the state financed is the finding in its plainest form.

**On what terms the state has bound itself.** For each agreement the actor sub-sections name that touches state data or core systems — a hyperscaler framework, a bilateral data-sharing clause, a vendor-financed data centre, an AI compute partnership — whether its published terms address data jurisdiction, portability, exit and audit, and what they say. Usually they are not published, and that is stated once, dated, not once per agreement.

**The AI layer.** Where the state's models and compute sit — a national compute facility, a hyperscaler sovereign-cloud arrangement with key custody, a foreign-hosted model behind a government service — and whether a national AI strategy or policy addresses hosting, model ownership and access terms, or is silent on them. A sovereign-cloud offer is stated as the vendor's offer, with its terms; the state's acceptance of it is a separate fact.

**The continental layer.** Whether the country takes part in a regional or continental cross-border data mechanism, a regional data-embassy arrangement or shared hosting, and whether its instruments take the AU Data Policy Framework's shape — localisation by category, with portability. `gov.regional` already asks about transfer rules and is not repeated; the one fact borrowed is participation.

One continuous narrative, up to 350 words, no sub-headings or tables, every claim hyperlinked, every time-varying figure dated, no opinion. A country that has a hosting decree and no exit clause is described as exactly that, and the reader draws the conclusion.

## What evidence it reads

**The unit's own status report, first, because most of the evidence is already in it.** The five `geopol.*` sub-sections name the agreements; `infra.store` names where government data is hosted and who built the facility; `gov.policy` and `gov.legislate` carry the data classification, localisation and cloud-policy instruments; `dpi.id`, `dpi.pay` and `dpi.exchange` say who built and operates the core systems; `dpi.govtech` carries the government hosting; `tech.ai` the AI strategy and compute; `gov.regional` the cross-border mechanism. Nothing stated there is restated; each is re-read for the term, the jurisdiction, the operator and the exit.

**The DPI variables named in the outline, second**: `ict-storage-datalocalisation`, `govtech-cloud-1.6`, `reg-cyber-cloud` and `reg-egov-cloudpolicy` for the rule on where data sits; `exchange-uptake-sovereignty` for national control written into the exchange's rules; `ict-storage-govcloud` for where government data is hosted; `ict-storage-dcpresence` and `ict-storage-cloudadoption` as weak proxies that attribute no provider. Their comments and source URLs are the point; a sourceless negative is not evidence of absence and yields *Not held* with a `gaps.csv` line, as everywhere in the report.

**The catalogue, third**, filtered to the place on `geopol.sovereignty`, the five power slugs, `infra.store`, `gov.policy`, `gov.legislate`, `dpi.id`, `dpi.pay`, `dpi.exchange`, `dpi.govtech` and `tech.ai`, opened in `raw/`. `geopol.sovereignty` held nine sources on 2026-09-25, all ingested since 2026-09-21, and the back catalogue is not re-tagged, so the slug finds the newest material only; the read is a keyword pass over the place's sources under the other slugs — *sovereign, localis-, hosted, host, data centre, cloud, jurisdiction, source code, escrow, licence, exit, portab-, lock-in, migrate, in-house, key custody, sovereign cloud, data embassy, compute, GPU, national cloud, government cloud*. The concept page `wiki/concepts/geopol.sovereignty.md` is the fastest read of what the newest sources say and is an intermediary, never the link. The 260 ledger rows mapped to the five retired `geopol.*` indicators point at the same sources and may be used to find them, never cited in their own right — the status report does not read the ledger.

**Check A is set membership, and it binds.** A URL outside the four held bodies of evidence — the catalogue, the DPI source URLs, `all-nonstate.csv`, the IIAG profiles — is not cited, whatever the writer knows about a ministry's cloud policy or a vendor's contract. An instrument the section needs and none of them carries is a `gaps.csv` row, and an acquire line if it is dated 2024 or later; the section states the position at the grain the held evidence supports.

## What is never said

No agreement count, no total signed, no *strong ties with*. No hyperscaler region, Outpost, local zone or vendor-built data centre described as a gain or a loss of sovereignty — it is a facility, stated with its operator and whatever terms are published. No sovereignty *score*, *posture* or *stage*; the assessment reads the same facts against a rubric, and the status report lets the reader read them. No sentence that a state *is dependent on* a provider: the section states that the identity system is operated by a named vendor under a contract whose terms are unpublished, and stops. No vendor's taxonomy adopted as the state's — Microsoft's six dimensions are Microsoft's. No restatement of what the actor sub-sections already say, and no observation that two accounts of a contract differ.

## What *Not established* looks like

Each case is one dated sentence about the country, never about the evidence — not "the base holds nothing", not "no source could be found", not "terms are unclear". The common outcome across most of the 54 will be that the facts of hosting are established and the terms are not.

**No rule on where state data sits.** *"No instrument fixing where state data is held or under whose law it is processed was in force as at September 2026."* Stated only where the instruments the report has read — the data-protection law, the cybersecurity law, the cloud or e-government policy — are silent; a draft or a strategy goal is stated as a draft or a goal, dated, not as an absence.

**Where the data is hosted is not published.** *"Where the national identity database is hosted, and under whose jurisdiction, had not been published as at September 2026."* Named by system; the sentence never generalises to the estate when only one system is unknown.

**The terms are not published.** The usual case: *"The terms on which the [agreement] governs data jurisdiction, portability and exit had not been published as at September 2026."* One sentence for all the unit's unpublished agreements where there are several, naming them once. If a source says the terms exist and are confidential, that is a fact and is stated with its link.

**Whether the state can run its own systems is not on record.** *"Whether the state holds the source code and operating skills for the payment switch, or can exit its operating contract, was not on record as at September 2026."* Reserved for units where the operator is known and the dependency is not — where even the operator is unknown, the hosting sentence covers it.

A unit with nothing on any of the five — plausible for a handful — carries the first sentence alone, two sentences at most, no link, which check B accepts, and a `gaps.csv` row per named question. A unit with hosting facts and no terms carries the linked facts and one *not established* sentence, which is the expected shape and counts as written.
