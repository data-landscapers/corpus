---
type: reference
title: maturity-rubric.md — the five-stage anchors per indicator, drafted chapter by chapter for lookups/maturity-rubric.csv
last_reviewed: 2026-09-23
status: task C2 complete; task C3 — the 22 measures cut 2026-09-24, items 6–8 re-cut; items 9–10 acted on 2026-09-24, awaiting CC's re-cut
---

# The rubric

*(Task C2 of `maturity-assessment-tasks.md`: Cowork drafts one chapter and stops; CC reviews it against `indicator-mapping-conventions.md`, the generic scale in `maturity-assessment.md` §3 and the two worked rubrics in the indicator documents, and either cuts it to `lookups/maturity-rubric.csv` or sends it back. The order is instruments first, so this file opens with Governance and the one Finance instrument; systems follow, measures last (task C3, where each also needs its value definition and band). `maturity-assessment-norms.md` is the source of every norm named below and is not restated here beyond the short name.)*

## How to read an anchor

**An anchor is evidence a mapped row can satisfy.** Each stage names what the base has to hold — an instrument published, a body constituted, a decision taken, a figure cited — not a quality the assessor feels. The stage is the highest whose anchor's positive conditions are all met. Clauses saying what is still missing — *with no plan on record*, *regulations pending* — describe the typical case at that stage and are not conditions; a country with part of the next stage stays at this one, and the qualifier names what it has.

**"Aligned with" a continental instrument** means the national instrument says so, or the AU or a REC records the country as compliant; an assessor's own comparison is not alignment.

**Stage 1 needs a citation.** *Absent* is a dated statement that the thing does not exist — a tracker, a ministry's own admission, a *Not held* row with a source. Silence is *No evidence* (unassessed), never stage 1.

**The instrument ladder, applied everywhere below** unless a row says otherwise: 1 *Absent* — nothing of the kind, cited · 2 *Nascent* — drafted, tabled, announced, under consultation, or an expired instrument with a successor in preparation · 3 *Established* — adopted or enacted and published, but not yet operating: commencement, regulations, a body or a budget still pending, or in force in a limited form · 4 *Operating* — in force with the machinery to give it effect: implementing regulations or a plan, a body with a mandate and a budget, and at least one act of implementation on record (an enforcement decision, a progress report, a funded action) · 5 *Leading* — the continental instrument's own end state: aligned with or ratifying it, reviewed or reported against, and sustained.

**The system ladder, for rows whose kind is system**: 1 *Absent* — no system of the kind, cited · 2 *Nascent* — procured, under construction, piloted, or provided for with no platform running · 3 *Established* — in service, but limited in scope, coverage, connected systems or use · 4 *Operating* — in service at scale: national coverage or the main institutions connected, usage published, maintained, interoperable with at least one other system · 5 *Leading* — the continental instrument's end state: interoperable across the estate on open standards, linked to the base registers, sustained and reported.

**Vocabulary used in the anchors.** *Adopted*: approved by cabinet, council of ministers or the competent authority and published. *Enacted*: passed and promulgated. *In force*: commenced, with the commencement date passed. *Constituted*: members appointed and a first act on record. *On record*: cited in a mapped row. *In the window*: dated inside the snapshot's window, for a stage to change (`maturity-assessment.md` §6).

**`interpolated`** is `no` where the anchoring norm itself states the rung (the register's *fixes* column: a *rungs* row states several; a *top* row states only stage 5) and `yes` where the rung is Corpus's reading of the ladder between absence and the norm's end state. A reference that informs a rung does not make it the norm's: a rung drawn from ID4D, a REC model law, the Broadband Commission or ISO membership classes stays `yes`.

**What is never evidence for a higher stage:** the announcement of an instrument (that is stage 2); a foreign partner's programme to draft one; a global index score (a reference, not the record — `maturity-assessment-norms.md` §7); a strategy that names the thing among its actions without an instrument of its own.

---

## Governance — accepted and cut 2026-09-23

### `gov.policy--digital-transformation-strategy` — norm: DTS (top)

| stage | anchor | interpolated |
|---|---|---|
| 1 | A dated statement that no national digital strategy exists, or that the last one expired with no successor. | yes |
| 2 | A national digital transformation strategy in drafting, under consultation or announced with a horizon; or an expired strategy with a successor in preparation on record; or only a sectoral ICT strategy standing in for a national one. | yes |
| 3 | A national digital transformation strategy adopted and published, with a stated horizon, and no costed implementation plan, budget or M&E report on record. | yes |
| 4 | The adopted strategy with a costed implementation or action plan, an implementing body with a mandate, and at least one published progress, mid-term or M&E report; budget lines traceable to it. | yes |
| 5 | A current strategy that states its alignment with the DTS and covers its pillars, reviewed at mid-term or succeeded on schedule, with published results against its own targets. | no |

### `gov.policy--ict-strategy` — norm: DTS; Smart Africa Manifesto (top)

The DTS treats an ICT or telecoms strategy as subsumed in a digital transformation strategy, so the top of this ladder is integration, not a separate document. *Absent* is neither an ICT strategy nor a digital strategy covering the sector.

| stage | anchor | interpolated |
|---|---|---|
| 1 | A dated statement that no ICT or telecoms sector strategy or policy exists and no digital strategy covers the sector. | yes |
| 2 | An ICT or telecoms policy in drafting or consultation, or expired with a successor in preparation. | yes |
| 3 | An ICT or telecoms sector policy or strategy adopted and published, with no implementation plan or reporting on record. | yes |
| 4 | The adopted sector policy with an implementation plan, a ministry or regulator mandated to deliver it, and reported implementation (a regulator's annual report against it, a funded programme). | yes |
| 5 | The sector strategy integrated into, or superseded by, a national digital transformation strategy that puts ICT at the centre of the national development agenda (Manifesto principle 5), with the sector's targets carried in it. | no |

### `gov.policy--broadband-strategy` — norm: DTS (target); Broadband Commission Target 1 (rungs: plan exists → funded)

| stage | anchor | interpolated |
|---|---|---|
| 1 | A dated statement that no national broadband plan exists and broadband is outside the universal-service definition. | yes |
| 2 | A national broadband plan in drafting or consultation, or an expired plan with no successor adopted, or broadband added to the universal-access definition with no plan. | yes |
| 3 | A national broadband plan or strategy adopted and published with dated targets, and no funding source identified on record. | yes |
| 4 | The adopted plan funded — a budget line, a universal-service-fund allocation or a financed programme cited against it — with an implementing body and reported progress against its targets. | yes |
| 5 | A funded plan whose targets meet or exceed the DTS 2030 outcome (universal access at ≥ 6 Mb/s, affordability at or below the DTS or 2 %-of-GNI line) with published progress against them. | no |

### `gov.policy--data-storage-cloud-strategy` — norm: DPF; DTS (top)

| stage | anchor | interpolated |
|---|---|---|
| 1 | A dated statement that government has no policy on where its data is hosted or on the use of cloud. | yes |
| 2 | A government cloud or data-centre policy announced or in drafting; a cloud-first statement without an instrument; a national data centre planned or under construction with no hosting policy. | yes |
| 3 | A policy or strategy on government data hosting or cloud adopted and published (cloud-first policy, national data centre policy, government hosting rules), not yet applied through classification or procurement. | yes |
| 4 | The policy in force with a hosting classification for state data, a designated government cloud or data centre in service, and procurement or circular rules that require systems to conform; at least one migration or conformance act on record. | yes |
| 5 | The DPF and DTS end state: state data hosted per classification on national or continental infrastructure, portability and interoperability across providers required, and usage reported. | no |

### `gov.policy--data-interoperability-framework-roadmap` — norm: DTS; DPF; AU Interop. Framework (top)

| stage | anchor | interpolated |
|---|---|---|
| 1 | A dated statement that no interoperability framework or roadmap exists for government systems. | yes |
| 2 | A framework or roadmap in drafting or announced, or interoperability named as an action in a digital strategy with no instrument of its own. | yes |
| 3 | A national interoperability framework (e-GIF or equivalent) or roadmap adopted and published, voluntary or without a custodian. | yes |
| 4 | The framework made binding on government systems by an instrument (decree, circular, procurement rule), with a custodian body and a published standards catalogue; at least one system's conformance or a register-reuse decision on record. | yes |
| 5 | The DTS end state: a framework with implementing acts covering interoperability and levels of assurance, on open standards, with core registers reused across systems through a secure exchange environment. | no |

### `gov.policy--ai-strategy` — norm: Continental AI Strategy (rungs: national strategy in Phase 1; governance mechanisms)

| stage | anchor | interpolated |
|---|---|---|
| 1 | A dated statement that no national AI strategy or policy exists. | yes |
| 2 | An AI strategy in drafting or consultation, or AI addressed only as a section of a digital strategy, or a task force appointed to prepare one. | yes |
| 3 | A national AI strategy adopted and published. | no |
| 4 | The strategy with a governance mechanism constituted (a national AI council, office or designated authority), an implementation plan, and funding or a first funded action on record — Phase 1's "national strategies and governance structures". | no |
| 5 | The strategy stating its alignment with the Continental AI Strategy and covering its focus areas, with an ethics or risk framework adopted and implementation reported. | no |

### `gov.policy--data-localisation-policies` — norm: DPF; AfCFTA DTP Art. 22 (top)

The norm is category-based localisation with free flow otherwise; a blanket localisation requirement is not a higher stage than none. The sovereignty indicator (`indicator-digital-sovereignty.md`) reads the same evidence for control; this row reads it for the instrument's shape.

| stage | anchor | interpolated |
|---|---|---|
| 1 | A dated statement that no rule exists on where data may be held or processed. | yes |
| 2 | A localisation rule proposed or drafted; or a blanket localisation requirement in force with no categorisation of data. | yes |
| 3 | An instrument in force that classifies data and localises defined categories (state, critical, sensitive personal), with other categories free to flow. | yes |
| 4 | The category-based rules applied through hosting decisions and procurement with a supervising body, and transfer of non-localised categories permitted through a stated mechanism (adequacy, contract, consent); at least one application or exemption decision on record. | yes |
| 5 | The DPF and DTP end state: category-based localisation, no requirement to locate computing facilities beyond public-policy exceptions, free flow of non-personal data, and participation in a regional or continental data-flow mechanism. | no |

### `gov.policy--data-governance-policy` — norm: DPF (rungs: the DPF's own implementation sequence, formulation → domestication → monitoring and evaluation)

The register describes the DPF as having five implementation phases; a read of the document on 2026-09-23 found no numbered phases, only an implementation figure of *formulation → domestication → monitoring and evaluation* and a statement of progressive realisation. The rungs below follow the figure; the "five phases" is now an A2 item in the register's §6, and stage 4 stays `yes` until it is settled.

| stage | anchor | interpolated |
|---|---|---|
| 1 | A dated statement that no national data policy or strategy exists. | yes |
| 2 | A national data policy in drafting or consultation, or DPF adoption announced with no domestic instrument. | yes |
| 3 | A national data governance policy or strategy adopted and published — the DPF's *formulation* stage. | no |
| 4 | The policy in force with an institutional owner (a data governance authority, office or council) and implementing instruments on record in at least two of the DPF's areas — classification, sharing, open data, protection, cross-border flows — the DPF's *domestication* stage. | yes |
| 5 | The DPF end state: domestic instruments across the framework's areas, monitored and evaluated against it, and the country participating in intra-African data collaboration. | no |

### `gov.policy--open-data-policy` — norm: ACHPR Declaration Principle 29; DPF; DTS (top)

| stage | anchor | interpolated |
|---|---|---|
| 1 | A dated statement that no open data policy exists and no public body publishes open data. | yes |
| 2 | An open data policy in drafting or announced; or a portal or pilot publishing datasets with no policy behind it. | yes |
| 3 | An open data policy adopted and published, with no licence, portal or obligation on public bodies in force. | yes |
| 4 | The policy in force with an open licence, a portal publishing datasets under it, an obligation on public bodies to publish, and a custodian; publication activity in the 12 months to the as-at date on record. | yes |
| 5 | Principle 29's end state: proactive publication of information of public interest required by law, open by default and through digital means, with compliance monitored and reported. | no |

### `gov.legislate--data-protection-legislation` — norm: Malabo Arts 8, 13, 16–19 (top; ECOWAS/SADC/EAC as rungs)

| stage | anchor | interpolated |
|---|---|---|
| 1 | A dated statement that no data protection law exists (a tracker entry, a ministry's admission), with at most sectoral or constitutional provisions. | yes |
| 2 | A data protection bill drafted, tabled or under consultation; or a law passed but not promulgated. | yes |
| 3 | A comprehensive data protection law enacted and published, with commencement, implementing regulations or the authority still pending. | yes |
| 4 | The law in force with implementing regulations and an authority constituted under it (see the DPA row), and at least one enforcement or compliance act on record. | yes |
| 5 | A law aligned with Malabo's principles and data-subject rights, with Malabo ratified or the applicable REC instrument domesticated, a transfer regime in force, and enforcement reported. | no |

### `gov.legislate--cybersecurity-legislation` — norm: Malabo ch. III, Arts 24–31 (top; GCI tiers as reference)

| stage | anchor | interpolated |
|---|---|---|
| 1 | A dated statement that no cybercrime or cybersecurity law exists. | yes |
| 2 | A cybercrime or cybersecurity bill drafted or tabled; or offences addressed only by penal-code amendment; or a national cybersecurity policy adopted with no law. | yes |
| 3 | A cybercrime or cybersecurity law enacted and published, with regulations or the institutional mechanism pending. | yes |
| 4 | The law in force with implementing regulations, the institutional mechanism it provides for constituted (a cybersecurity agency, authority or CERT under the law), and prosecutions or incident-response acts on record. | yes |
| 5 | Malabo's chapter III met: national cybersecurity policy and strategy adopted, law in force, institutions operating, Malabo ratified, and harmonisation or mutual legal assistance arrangements on record. | no |

### `gov.legislate--legislation-covering-digital-id` — norm: DTS; AU Interop. Framework §4.1; DTP Art. 14 (target + top; ID4D governance principles as rungs)

| stage | anchor | interpolated |
|---|---|---|
| 1 | A dated statement that no law establishes a national ID system or authority. | yes |
| 2 | An identity bill drafted or tabled; or an ID system operating under executive instrument only, with legislation in preparation. | yes |
| 3 | A law enacted establishing the ID system or its authority, with regulations, commencement or the data-protection linkage pending. | yes |
| 4 | The law in force with regulations, an authority with a clear mandate, and provisions on the right to enrol, personal data protection, grievance and oversight, applied in practice on record. | yes |
| 5 | The Interop. Framework §4.1 end state: a harmonised enabling legal framework, a personal data law in force and applying to the ID system, Malabo ratified, and legal identity for all provided in law. | no |

### `gov.legislate--digital-payments-legislation` — norm: DTP Art. 15 and Annex; Malabo Art. 7 (top; G20 HLP 3, PAFI as rungs)

| stage | anchor | interpolated |
|---|---|---|
| 1 | A dated statement that no payment-systems law or e-money regulation exists. | yes |
| 2 | A payment-systems bill or e-money regulation drafted, tabled or under consultation. | yes |
| 3 | A payment-systems law or a central-bank e-money regulation in force, without a licensing regime for non-bank providers or interoperability rules. | yes |
| 4 | The framework in force with licensing of non-bank providers, interoperability rules or a mandate, and consumer-protection provisions, with licences or enforcement acts on record. | yes |
| 5 | The DTP end state: domestic interoperability mandated and in effect, cross-border participation (PAPSS or a regional system) provided for, AML/CFT and consumer protection embedded in the framework. | no |

### `gov.legislate--legislation-enabling-data-interoperability` — norm: DTS; DTP Art. 19; DPF (top)

| stage | anchor | interpolated |
|---|---|---|
| 1 | A dated statement that no instrument permits data sharing between public bodies. | yes |
| 2 | A data-sharing law, decree or e-government act in drafting or tabled. | yes |
| 3 | An instrument in force permitting public bodies to share data in general terms (an e-government law, a decree on the exchange platform), without obligations, standards or a custodian. | yes |
| 4 | The instrument with implementing acts: obligations to share through the exchange layer, register-reuse rules, levels of assurance, a custodian; conformance or a sharing agreement on record. | yes |
| 5 | The DTS end state: a framework with implementing acts for interoperability and levels of assurance on open standards, with mutual recognition of authentication and identities provided for (DTP Art. 19). | no |

### `gov.legislate--ai-legislation-regulations` — norm: Continental AI Strategy governance activities (rungs); DTP Annex on Emerging Technologies

| stage | anchor | interpolated |
|---|---|---|
| 1 | A dated statement that no law or regulation addresses AI, automated decision-making or algorithmic systems. | yes |
| 2 | A regulatory gap analysis or consultation on AI announced; AI addressed by guidance or ethics principles without legal effect. | no |
| 3 | Existing laws amended or sectoral rules adopted to cover AI — automated-decision provisions in data protection, sector guidance with legal effect, formally adopted AI ethics rules. | no |
| 4 | An enabling AI regulatory framework in force (act or decree) with assessment or evaluation tools and a designated regulator or oversight body. | no |
| 5 | The Continental AI Strategy end state: risk-based regulation in force, an independent oversight institution with enforcement and redress, and alignment with regional governance (the AI Ethics Board or REC frameworks). | no |

### `gov.legislate--e-commerce-legislation` — norm: Malabo ch. I; DTP Arts 12, 16, 27 (top; UNCTAD tracker areas as rungs)

| stage | anchor | interpolated |
|---|---|---|
| 1 | A dated statement that no electronic-transactions or e-commerce law exists. | yes |
| 2 | An e-transactions or e-commerce bill drafted or tabled. | yes |
| 3 | An electronic-transactions law enacted giving legal validity to electronic documents, contracts and signatures, with trust-service regulations or consumer provisions pending. | yes |
| 4 | The law in force with online consumer-protection provisions, e-signature or trust-service regulations and accredited providers, and enforcement or accreditation acts on record. | yes |
| 5 | The DTS "complete set" — e-transactions, consumer protection, privacy and cybercrime — all in force and mutually consistent, with mutual recognition of e-authentication provided for. | no |

### `gov.legislate--statistics-legislation` — norm: African Charter on Statistics; AU Model Statistics Law (top; Model Law clauses as rungs)

| stage | anchor | interpolated |
|---|---|---|
| 1 | A dated statement that no statistics act exists or that the act in force predates the national statistical system it governs. | yes |
| 2 | A statistics bill drafted or tabled to replace or create the act. | yes |
| 3 | A statistics act in force establishing the national statistics office, without the Charter's principles (independence, confidentiality, coordination) written into it. | yes |
| 4 | An act in force providing professional independence, a coordination mandate over the national statistical system, confidentiality of individual data and a funding basis, with the office operating under it. | yes |
| 5 | An act conforming to the Charter and the Model Law, with the Charter ratified. | no |

### `gov.legislate--access-to-information-legislation` — norm: ACHPR Declaration Principles 26, 29, 34; ACHPR Model Law (rungs)

| stage | anchor | interpolated |
|---|---|---|
| 1 | A dated statement that no access-to-information law exists, with at most a constitutional right. | yes |
| 2 | An access-to-information bill drafted, tabled or under consultation. | yes |
| 3 | An access-to-information law enacted, with the oversight mechanism, procedures or commencement pending. | yes |
| 4 | The law in force with procedures, proactive-disclosure obligations and an oversight mechanism established by law (Principle 34), with requests or decisions on record. | no |
| 5 | The Model Law met: proactive disclosure including through digital means, an independent oversight body operating with published decisions, and access that is expeditious and inexpensive. | no |

### `gov.protect--data-protection-authority` — norm: Malabo Arts 11–12; DPF checklist (rungs: established · independent · funded · effective · accountable)

| stage | anchor | interpolated |
|---|---|---|
| 1 | A dated statement that no authority exists and none is provided for in law. | yes |
| 2 | An authority provided for in law but not constituted; or data protection handled by a ministry unit or the regulator without a statutory authority. | yes |
| 3 | The authority constituted — members appointed — and beginning operations: registrations, guidance, a first report, with no enforcement decision on record. | yes |
| 4 | The authority independent by statute, funded in the budget, and enforcing — decisions, sanctions or orders on record — over public and private controllers. | no |
| 5 | Malabo Arts 11–12 met and the DPF checklist complete: independent, funded, enforcement decisions and sanctions published and complaints resolved on record, accountable (an annual report published), covering all controllers, and cooperating regionally (NADPA membership, cross-border cases). | no |

### `gov.protect--national-data-protection-readiness` — norm: DPF; AUC/ISOC Guidelines; Malabo (rungs: ratification · law in force · authority operating · Guidelines practices)

A composite of the four elements the register names, on the ordinary ladder.

| stage | anchor | interpolated |
|---|---|---|
| 1 | No law, no authority, no ratification, and a citation for the absence of the law. | yes |
| 2 | A data protection bill drafted or tabled, or a draft under consultation. | yes |
| 3 | A data protection law in force. | no |
| 4 | A law in force and an authority operating, with the Guidelines' practices on record — privacy-by-design guidance, codes of conduct, impact assessments, breach notification in use. | no |
| 5 | All four: Malabo ratified (or the REC instrument domesticated), law in force, authority enforcing, the Guidelines' practices in use, and participation in continental or regional cooperation. | no |

### `gov.regional--regional-policy-collaboration` — norm: DTS; PRIDA (top)

| stage | anchor | interpolated |
|---|---|---|
| 1 | A dated statement that the country takes no part in regional or continental digital policy processes. | yes |
| 2 | Membership only — of ATU, Smart Africa, a REC regulators' association — with no contribution on record. | yes |
| 3 | Active participation on record: hosting or contributing to a regional or continental policy process (PRIDA, a REC digital strategy, a harmonisation working group), or regional guidelines adopted domestically in one area. | yes |
| 4 | Regional guidelines or a REC digital strategy implemented through domestic instruments in more than one area (roaming, spectrum, cross-border data, digital ID recognition) with reporting to the regional body. | yes |
| 5 | The DTS end state: the national strategy stating its alignment with the regional and continental strategies, a standing coordination mechanism, and regional instruments carried in domestic law. | no |

### `gov.regional--regional-legal-harmonisation` — norm: Malabo Art. 28; DTS; DTP Art. 43 (top; REC instruments as rungs)

| stage | anchor | interpolated |
|---|---|---|
| 1 | A dated statement that no domestic instrument is harmonised with a REC or AU model or act. | yes |
| 2 | A REC model law or supplementary act referenced in a draft or bill. | yes |
| 3 | A REC instrument domesticated in one area of the cyberlaw set (data protection, cybercrime or e-transactions). | yes |
| 4 | REC instruments domesticated across the cyberlaw set, with mutual legal assistance or cross-border cooperation arrangements on record. | yes |
| 5 | Malabo and the AfCFTA Digital Trade Protocol ratified, the full set harmonised, and harmonisation reported to the REC or AU. | no |

### `gov.regional--shared-regional-infrastructure` — norm: PIDA PAP 2; DTS; Smart Africa One Africa Network (top) — kind: system

| stage | anchor | interpolated |
|---|---|---|
| 1 | A dated statement that the country is party to no regional ICT infrastructure project or network. | yes |
| 2 | Signatory or participant in a planned regional project (a PIDA PAP 2 ICT project, a cable consortium, a regional backbone) not yet in service. | yes |
| 3 | One shared regional asset in service touching the country: a cross-border fibre link, a cable landing shared through a consortium, a regional IXP peering, One Africa Network roaming. | yes |
| 4 | Several shared assets in service with operational agreements — cross-border capacity, regional traffic exchange, roaming — and usage or traffic reported. | yes |
| 5 | The DTS end state: regional or continental licensing of operators recognised, participation in regional networks and data infrastructure, and traffic kept regional on record. | no |

### `gov.regional--cross-border-data-transfers` — norm: Malabo Art. 14; DPF; DTP Art. 20 and Annex (top)

| stage | anchor | interpolated |
|---|---|---|
| 1 | A dated statement that no rule governs the transfer of personal data abroad. | yes |
| 2 | Transfer rules drafted, or in a bill. | yes |
| 3 | Transfer provisions in force in the data protection law (adequacy, consent, authorisation) with no mechanism issued by the authority. | yes |
| 4 | Transfer mechanisms operating — adequacy decisions, standard clauses, binding corporate rules or authorisations issued by the authority — with decisions on record. | yes |
| 5 | The DPF and DTP end state: an adequacy-based regime aligned with Malabo Art. 14 and the DTP annex, and participation in a regional or continental data-flow mechanism. | no |

### `gov.standards--national-interoperability-standards` — norm: DTS; AU Interop. Framework (top)

| stage | anchor | interpolated |
|---|---|---|
| 1 | A dated statement that no national standards exist for government systems' interoperability. | yes |
| 2 | A standards catalogue or e-GIF technical annex in drafting. | yes |
| 3 | Interoperability standards published for government systems, voluntary. | yes |
| 4 | The standards mandated for government procurement and systems by an instrument, with a custodian and conformance testing or certification on record. | yes |
| 5 | The DTS end state: open standards mandated, verification standards for identity in G2G, G2B and G2C transactions, referencing international standards (W3C, ISO/IEC), and ready for mutual recognition. | no |

### `gov.standards--national-quality-standards` — norm: PAQI / CAMI-20 (top, weak); UNIDO Quality Policy principles as reference

| stage | anchor | interpolated |
|---|---|---|
| 1 | A dated statement that no national standards body is active, or that none addresses ICT or data. | yes |
| 2 | A national standards body exists with no ICT or data quality standards adopted and no national quality policy. | yes |
| 3 | A national quality policy adopted, or the standards body adopting ICT or data quality standards (ISO 9001, ISO/IEC 27001, ISO 8000) as national standards, voluntary. | yes |
| 4 | A quality policy in force with accreditation and certification infrastructure operating for ICT — accredited certification bodies, certified government systems or bodies on record. | yes |
| 5 | The PAQI end state: the standards body participating in ARSO and AFRAC, harmonised African standards adopted, and a national quality policy on UNIDO's principles. | no |

### `gov.standards--adoption-of-international-standards` — norm: DTS; AU Interop. Framework; ARSO (top; ISO membership class as rungs)

| stage | anchor | interpolated |
|---|---|---|
| 1 | A dated statement that the country is outside ISO membership and adopts no international ICT standards. | yes |
| 2 | ISO correspondent or subscriber membership, with sporadic adoption of international standards. | yes |
| 3 | ISO member body; international ICT and data standards adopted as national standards on record. | yes |
| 4 | Systematic adoption through a published catalogue, participation in technical committees, and government systems required to conform to named international standards (security, records, identity). | yes |
| 5 | The DTS and Framework end state: technology neutrality and open standards mandated, participation in ARSO harmonisation and in international standard-setting. | no |

### `gov.discourse--non-governmental-contribution-to-national-policy` — norm: ACDEG; Public Service Charter; DPF; ACHPR Principle 17 (top; OECD Open Government Rec., OGP as reference)

| stage | anchor | interpolated |
|---|---|---|
| 1 | A dated statement that digital instruments are made without consultation, or that civil society is excluded from the process. | yes |
| 2 | Ad hoc consultation on a digital instrument on record, with no requirement or standing mechanism. | yes |
| 3 | Consultation required by law or standing practice for digital policy, with published consultations and responses on record. | yes |
| 4 | Standing multi-stakeholder bodies (a national IGF, an advisory council, a regulator's consultative committee) with a role in policy, and non-governmental input traceable in adopted instruments. | yes |
| 5 | The ACDEG and Declaration end state: a multi-stakeholder model of regulation, an enabling environment for civil society in law, and co-created commitments (an OGP action plan or equivalent) reported against. | no |

### `gov.discourse--open-discussion-of-government-policy` — norm: ACHPR Declaration Principles 26, 29, 34, 37, 41; ACDEG; Public Service Charter (top)

| stage | anchor | interpolated |
|---|---|---|
| 1 | Restrictions on discussion on record — an internet shutdown, blocking, or prosecution for online expression in the 12 months to the as-at date — and no access-to-information law. | yes |
| 2 | Discussion occurs but restrictions are on record in the 12 months to the as-at date (a shutdown, a blocking order, a false-information law with prison terms), or the press covers policy under documented controls. | yes |
| 3 | No shutdown or blocking in the 12 months to the as-at date, policy documents published, and the press and public discussing digital policy freely on record. | yes |
| 4 | Proactive disclosure practised — draft laws and strategies published for comment, regulator decisions published — with an access-to-information law in force. | yes |
| 5 | The Declaration's end state: universal access affirmed in law and policy, no surveillance abuse on record, an independent oversight body for access to information, and open publication as the norm. | no |

## Finance — the instrument, accepted and cut 2026-09-23

### `finance.budget--sustainable-domestic-financing-of-digital-transformation` — norm: Agenda 2063 Goal 20; DTS sovereignty fund (target, not digital-specific); Broadband Commission Target 1 as reference

This row asks whether a *mechanism* exists; `finance.sustain--financial-sustainability-of-digital-systems` (a measure, task C3) asks what share the state actually carries.

| stage | anchor | interpolated |
|---|---|---|
| 1 | A dated statement that the budget carries no domestic line for digital transformation, or a read budget document (`budgets/`) with none. | yes |
| 2 | Digital lines appropriated project by project within single ministries, with no recurring programme, fund or own-source mechanism. | yes |
| 3 | A recurring programme or budget line for digital transformation in the appropriation, in a read budget document or on record, without a dedicated fund or own-source revenue. | yes |
| 4 | A dedicated mechanism in law: a digital or universal-service fund, a levy or own-source revenue assigned to digital programmes, or a multi-year programme with published execution. | yes |
| 5 | The DTS and Goal 20 posture: a sovereignty fund or equivalent sustained domestic mechanism with published execution, and external finance confined to capital. | no |

The Finance chapter's three measures (`finance.sustain--financial-sustainability-of-digital-systems`, whose rubric is drafted in `indicator-financial-sustainability.md` §5, and the two `finance.new` rows) are task C3 and are not drafted here.

---

## Governance — changes made on CC's first review (2026-09-23)

`maturity-rubric-review.md` returned the chapter with ten items; all ten are in the file above.

- **1** — the stage-selection rule is now *the highest whose anchor's positive conditions are all met*, with the negative clauses declared descriptive; no row edited for it.
- **2** — broadband stage 4 back to `yes`; the *interpolated* paragraph says a reference does not make a rung the norm's.
- **3** — `ai-strategy` stage 4 `no`, citing Phase 1's "national strategies and governance structures". `data-governance-policy` rewritten on the DPF's own implementation figure (formulation → domestication → M&E) after a read of the document found no numbered phases; stage 3 `no`, stage 4 left `yes` with the note, and the register's "five phases" flagged as an A2 item. Readiness per item 7.
- **4** — both Finance references are `finance.sustain--financial-sustainability-of-digital-systems`.
- **5** — DPA stage 5 names the evidence: enforcement decisions and sanctions published, complaints resolved on record.
- **6, 8** — `ict-strategy` stage 5 and `data-localisation-policies` stage 2 kept as drafted.
- **7** — readiness on the ordinary ladder: 2 a bill or draft; 3 a law in force (`no`); 4 law and authority operating with the Guidelines' practices (`no`); 5 all four plus cooperation (`no`).
- **9** — `open-discussion` stages 1–3 keyed on *the 12 months to the as-at date*; the look-back exception is CC's to carry into D2, as the review says.
- **10** — the "aligned with" test is in *How to read an anchor*.

One thing for the second review that the first did not raise: the register's description of the DPF (§3 rows for `data-governance-policy` and `national-data-protection-readiness`, and the §4 entry) carries the research pass's "five implementation phases"; the register has been amended to flag it and the item added to §6, so that the norms lookup is not cut with it as fact.

---

## DPI — accepted and cut 2026-09-23

Thirty-four of the chapter's thirty-six: thirty-one systems and three instruments (`dpi.id--national-maintenance-of-id-and-credentials-systems`, `dpi.pay--governance-role-of-central-bank`, `dpi.pay--consumer-protection`). The two measures — `dpi.id--registration-of-entire-population` and `dpi.pay--population-uptake` — are task C3. The system ladder in *How to read an anchor* applies unless a row says otherwise; where a register row is *rungs*, the norm's own stages are named and marked `no`.

### `dpi.exchange--national-data-exchange-system` — norm: DTS; DPF §5.3; AU Interop. Framework §3.2.1 (top)

| stage | anchor | interpolated |
|---|---|---|
| 1 | A dated statement that no data-exchange layer exists between government systems — the government's own appraisal, an assessment, or a *Not held* row with a source. | yes |
| 2 | An exchange platform procured, under construction, piloted between a few systems, or provided for by decree with no platform running. | yes |
| 3 | An exchange platform in service with a small number of connected systems or services and no published conditions of access or usage. | yes |
| 4 | The platform in service at scale — tens of member institutions, hundreds of services, transaction volumes published — with published conditions of access, a custodian, and registers reused through it on record. | yes |
| 5 | The DTS end state: core registers reused across government through a secure exchange environment on open standards, with levels of assurance defined, private-sector access provided for, and usage reported. | no |

### `dpi.exchange--use-of-digital-id-in-other-systems` — norm: AU Interop. Framework; DTP Arts 14, 19 (top)

| stage | anchor | interpolated |
|---|---|---|
| 1 | A dated statement that no other system relies on the national ID for enrolment or verification. | yes |
| 2 | Use of the ID by another system planned, piloted or contracted (a KYC pilot, a SIM-registration link announced). | yes |
| 3 | The ID used by one or two systems in service — SIM registration, a bank's KYC, a social register — with no verification service offered to others. | yes |
| 4 | Services, public and private, consuming a verification or authentication service built on the ID — banks' KYC, telecoms, health, social programmes — across sectors on record, with usage published; the public registers keyed on the number are `dpi.id--use-by-other-systems`'s evidence, not this row's. | yes |
| 5 | The Framework's end state: the ID the common credential for public and private services, with selective disclosure and privacy protection in law, and mutual recognition provided for (DTP Art. 19). | no |

### `dpi.exchange--interoperability-of-health-systems` — norm: Africa CDC HIE Guidelines and Standards; Smart Africa Digital Health Blueprint (rungs: policy → standards → use cases)

| stage | anchor | interpolated |
|---|---|---|
| 1 | A dated statement that health systems do not exchange data — separate registries, surveillance and supply-chain systems with no linkage. | yes |
| 2 | A health information exchange policy or architecture in drafting, or interoperability between two systems piloted or contracted. | yes |
| 3 | A national HIE policy or digital health architecture adopted — the Guidelines' *policy* pillar — with interoperability in service between a few systems. | no |
| 4 | National standards adopted (a terminology and messaging standard, a facility and patient identifier) — the *standards* pillar — and applied in exchanges in service across the main systems (HMIS, surveillance, registries, supply chain). | no |
| 5 | The *use cases* pillar met: exchanges in service across the health system on the national standards, with the client registry linked to the national ID, and participation in the continental health data space on record. | no |

### `dpi.exchange--interoperability-of-education-systems` — norm: AU Digital Education Strategy SO4 (rungs: EMIS 1.0 → EMIS 2.0)

| stage | anchor | interpolated |
|---|---|---|
| 1 | A dated statement that the education systems — EMIS, examinations, teacher payroll, learner identification — exchange no data. | yes |
| 2 | A link between two education systems planned, contracted or piloted. | yes |
| 3 | One exchange in service — the EMIS with the examinations body, or with teacher payroll, or with the national ID — on record. | yes |
| 4 | Exchanges in service across the main education systems on a shared learner and teacher identifier — the DES's *EMIS 2.0*, individual-level and ID-linked. | no |
| 5 | The DES end state: EMIS 2.0 linked to the national ID and to other sectors through the exchange layer, with the data model published and analytics in use for policy. | no |

### `dpi.exchange--interoperability-of-social-protection-systems` — norm: Protocol on Social Protection Art. 23 (top; World Bank typology as reference)

| stage | anchor | interpolated |
|---|---|---|
| 1 | A dated statement that social protection programmes hold separate beneficiary lists with no exchange between them or with other systems. | yes |
| 2 | A link between programmes, or between a registry and the ID or a payment provider, planned, contracted or piloted. | yes |
| 3 | One exchange in service — the registry or a programme MIS linked to the national ID, or to a payment provider, or two programmes sharing a list — on record. | yes |
| 4 | Exchanges in service across the main programmes on a shared identifier: the registry linked to the ID, to payment providers and to at least one other sector (civil registration, health, education). | yes |
| 5 | The Protocol's end state: an integrated social protection information system interoperable with the ID, civil registration, payments and other sectors, with portability between schemes provided for. | no |

### `dpi.id--robustness-of-system` — norm: AU Interop. Framework §3.1 technical integrity, §3.3.4.1 Levels of Assurance (top; ID4D Principle 3, FATF assurance levels as reference)

| stage | anchor | interpolated |
|---|---|---|
| 1 | A dated statement that no national identity system exists, or that the system in place is paper-based with no unique identifier. | yes |
| 2 | A national ID system procured, under construction or piloted; or a card presented as ready and waiting on its law or decree. | yes |
| 3 | A national ID system in service issuing credentials, with deduplication or a unique number, and no published assurance levels, audit or security certification. | yes |
| 4 | The system in service with biometric deduplication, a documented assurance level or security certification, a published audit or incident record, and credential lifecycle (revocation, renewal) operating. | yes |
| 5 | The Framework's end state: technical integrity demonstrated, levels of assurance defined and published, security baselines met, and the system's trust framework recognised regionally. | no |

### `dpi.id--national-maintenance-of-id-and-credentials-systems` — norm: AU Interop. Framework Principle 7; DPF (top; ID4D Principles 5 and 7 as reference) — kind: instrument

Reads the same evidence as `geopol.sovereignty--digital-sovereignty` for the ID system alone; the sovereignty row reads it for the estate.

| stage | anchor | interpolated |
|---|---|---|
| 1 | A dated statement that the ID or credential system is built, hosted and operated by a foreign supplier with no national capacity, source code or exit terms on record. | yes |
| 2 | National operation stated as a goal, or a transfer of skills or a local operating team announced, with the platform still supplier-dependent. | yes |
| 3 | The national authority operating the system day to day on a platform built abroad, with maintenance, printing or upgrades still under a foreign contract and no funding model settled. | yes |
| 4 | The authority operating and maintaining the system with national staff, contracts carrying exit and portability terms or source-code escrow, and a durable funding model on record. | yes |
| 5 | The Framework's end state: open standards, no vendor or technology lock-in, national ownership of data and platform, and financial and operational sustainability demonstrated. | no |

### `dpi.id--authentication` — norm: AU Interop. Framework §3.2 layers, §3.4 options; DTP Arts 8, 9, 19 (rungs: layers and phases)

| stage | anchor | interpolated |
|---|---|---|
| 1 | A dated statement that no digital authentication service exists — the credential is verified by inspection only. | yes |
| 2 | An authentication, e-signature or PKI service authorised, contracted or piloted; a legal basis for e-signatures granted with no service operating. | yes |
| 3 | An authentication service in service for one channel or one use (a root certification authority operating, OTP verification for one system, a border verification system) — the Framework's *layer 1*. | no |
| 4 | Authentication services in service across channels and consumers — PKI or trust services with accredited providers, an online verification API, mobile authentication — with usage on record — *layer 2*. | no |
| 5 | The Framework's *layer 3*: remote authentication through wallets, federation or signed credentials, and mutual recognition of e-authentication with other states provided for (DTP Art. 19). | no |

### `dpi.id--digital-id-from-birth` — norm: DTS (legal identity as part of civil registration); SDG 17.19.2(b); AU No Name Campaign declaration (target: 100 % of births, 80 % of deaths registered)

| stage | anchor | interpolated |
|---|---|---|
| 1 | A dated statement that a birth creates no identity record — registration and ID are separate systems with no link, or registration is paper-only. | yes |
| 2 | A unique identifier at birth provided for in law or piloted in some districts or facilities. | yes |
| 3 | A unique number assigned at birth registration in service, in part of the country or for registrations in digital offices only. | yes |
| 4 | Assignment at birth in service nationally, with the birth record generating the identity record and coverage of births registered published. | yes |
| 5 | The DTS end state: digital legal identity for every person from birth as part of civil registration, with the SDG 17.19.2(b) target (100 % of births, 80 % of deaths registered) met on the published figure. | no |

### `dpi.id--interoperability-of-birth-registration-and-digital-id` — norm: AU Interop. Framework §2.2; CAMCR 2019 (top; UN Handbook 2022 as reference)

| stage | anchor | interpolated |
|---|---|---|
| 1 | A dated statement that the civil register and the ID system do not exchange records. | yes |
| 2 | A linkage planned, contracted or piloted; a single agency mandated over both registers with no exchange yet. | yes |
| 3 | Exchange in service in one direction or for one event (births feed the ID, or deaths retire credentials), or the two registers held by one agency on separate platforms. | yes |
| 4 | Two-way exchange in service across vital events — births enrol, deaths retire, name and status changes propagate — with reconciliation reported. | yes |
| 5 | The Handbook's end state: civil registration, vital statistics, the population register and the ID system fully interoperable and simultaneous, as recognised by the CRVS programme or a published assessment. | no |

### `dpi.id--use-by-other-systems` — norm: AU Interop. Framework; DPF §5.3.1.2 (top)

Distinct from `dpi.exchange--use-of-digital-id-in-other-systems`: that row reads the exchange from the consuming systems' side; this reads the ID system's own reach as the authoritative source for public registers.

| stage | anchor | interpolated |
|---|---|---|
| 1 | A dated statement that public registers (electoral, tax, social, civil service) do not use the national ID as their identifier. | yes |
| 2 | Adoption of the national number by another register planned or piloted. | yes |
| 3 | One or two public registers keyed on the national ID (the electoral roll drawn from it, a tax register linked). | yes |
| 4 | The main public registers keyed on the national ID — electoral, tax, social protection, civil service, business ownership — with reconciliation between them on record. | yes |
| 5 | The DPF end state: the ID the single source of truth for identity across public registers and for secure online transactions, with private-sector use provided for. | no |

### `dpi.pay--governance-role-of-central-bank` — norm: AfCFTA DTP Annex on Digital Payments; PAPSS (top; PFMI Responsibilities, PAFI GP1–2 as reference) — kind: instrument

| stage | anchor | interpolated |
|---|---|---|
| 1 | A dated statement that the central bank has no mandate over payment systems or e-money. | yes |
| 2 | A payment-systems mandate or e-money regulation in drafting; oversight exercised by circular only. | yes |
| 3 | The central bank's oversight mandate in force, licensing or authorising providers, with no national switch or interoperability mandate. | yes |
| 4 | The central bank operating or overseeing a national switch or interoperability arrangement, with published oversight (statistics, licences, enforcement) and a consumer-protection or dispute function on record. | yes |
| 5 | The DTP Annex end state: interoperability across domestic, regional and continental systems mandated and in effect, participation in PAPSS or a regional system, and AML/CFT and consumer protection embedded in oversight. | no |

### `dpi.pay--g2p-functionality` — norm: DTS "digitize government-to-person payments" (top; PAFI GP7, Findex as reference)

| stage | anchor | interpolated |
|---|---|---|
| 1 | A dated statement that government payments to individuals — transfers, salaries, pensions — are made in cash. | yes |
| 2 | Digital G2P piloted for one programme or district, or contracted. | yes |
| 3 | One programme paying digitally in service (a cash transfer over mobile money, salaries to accounts) with others in cash. | yes |
| 4 | The main G2P streams digital in service — social transfers, salaries, pensions — with beneficiary counts published and a choice of provider or account. | yes |
| 5 | The DTS end state: government-to-person payments digital by default across programmes, interoperable across providers, linked to the ID and the social registry, with beneficiary reach and cost reported. | no |

### `dpi.pay--revenue-collection` — norm: DTP Arts 10, 13; Malabo Art. 7 (top; TADAT POA5 as reference)

| stage | anchor | interpolated |
|---|---|---|
| 1 | A dated statement that taxes, fees or duties are paid in cash or by paper instrument only. | yes |
| 2 | Electronic payment of a tax or fee piloted or contracted; e-filing announced. | yes |
| 3 | Electronic payment in service for some taxes or fees, or for large taxpayers only. | yes |
| 4 | Electronic filing and payment in service for the main taxes and for customs duties, with the share of revenue collected electronically published; e-invoicing or fiscal devices in use. | yes |
| 5 | The DTP end state: electronic invoices legally equivalent, paperless trading, electronic payment accepted for all state dues, and the electronic share reported. | no |

### `dpi.pay--b2b-and-b2g-functionality` — norm: DTP Arts 13, 15, 16 (top; GTMI I-12 as reference)

| stage | anchor | interpolated |
|---|---|---|
| 1 | A dated statement that business payments and government procurement run on paper and cash. | yes |
| 2 | E-procurement or a business payment platform procured, piloted or under construction. | yes |
| 3 | An e-procurement portal or interbank business payment service in service, limited in scope (publication only, some agencies, large firms). | yes |
| 4 | E-procurement in service end to end (tender to payment) across the main agencies, and interbank or instant business payments in service with interoperability across banks. | yes |
| 5 | The DTP end state: e-invoicing, interoperable payment and settlement, and an electronic-transactions framework in force, with B2G volumes published. | no |

### `dpi.pay--p2p-p2g-and-p2b-functionality` — norm: DTS (interoperability of e-money and DFS; low-cost channels and agents) (top; PAFI GP4–5 as reference)

| stage | anchor | interpolated |
|---|---|---|
| 1 | A dated statement that no mobile money or retail digital payment service is licensed. | yes |
| 2 | A mobile money or e-money service licensed or piloted. | yes |
| 3 | Retail digital payment services in service with no interoperability between providers, and payments to government or merchants limited. | yes |
| 4 | Provider interoperability in service (a switch or bilateral links), merchant and government payments accepted through the services, agent networks reported. | yes |
| 5 | The DTS end state: national interoperability across e-money and bank accounts, low-cost channels and agents reaching underserved areas, and usage reported. | no |

### `dpi.pay--cross-border-functionality` — norm: DTS; DTP Art. 15; PAPSS (top; G20/FSB targets as reference)

| stage | anchor | interpolated |
|---|---|---|
| 1 | A dated statement that no regulated cross-border retail or mobile money payment channel exists. | yes |
| 2 | A cross-border corridor piloted or licensed; a regulatory framework for cross-border mobile money in drafting. | yes |
| 3 | One or more corridors in service through bilateral arrangements, with a regulatory framework in force. | yes |
| 4 | Participation in a regional payment system in service (PAPSS, a REC system) with the central bank enrolled, and corridor costs or volumes published. | yes |
| 5 | The DTS end state: participation in a single African payments area, cross-border mobile money framework in force, and costs at or below the reference targets. | no |

### `dpi.pay--consumer-protection` — norm: DTS four dimensions (disclosure, responsible lending, data privacy, dispute resolution); DTP Art. 27 (rungs) — kind: instrument

| stage | anchor | interpolated |
|---|---|---|
| 1 | A dated statement that no consumer-protection rules apply to digital financial services. | yes |
| 2 | Rules in drafting; protection by general consumer law or a regulator's circular only. | yes |
| 3 | Conduct-of-business rules in force covering at least two of the four dimensions, with no redress body operating. | no |
| 4 | Rules in force across the four dimensions with a redress or complaints mechanism operating — a financial ombudsman, a regulator's complaints unit — and decisions or statistics on record. | no |
| 5 | The DTS and DTP end state: all four dimensions in force, redress operating, misleading and fraudulent practices prohibited and enforced, and outcomes reported. | no |

### `dpi.registry--population-register` — norm: DTS (electronic population registry first) (top; UN P&R Rev. 3 as reference)

| stage | anchor | interpolated |
|---|---|---|
| 1 | A dated statement that no population register exists — identity is held per document (ID card, passport) with no consolidated register. | yes |
| 2 | A population register provided for in law, procured or under construction. | yes |
| 3 | A population register in service, incomplete or built from one source (ID enrolment only), not updated from vital events. | yes |
| 4 | A register in service updated from births, deaths and status changes, keyed on the national number, and used by other registers on record. | yes |
| 5 | The DTS end state: an electronic population register as the base register of government, continuously updated from civil registration, and the source for other registers. | no |

### `dpi.registry--civil-register` — norm: DTS; APAI-CRVS; SDG 17.19.2(b) (target: 100 % of births, 80 % of deaths registered)

| stage | anchor | interpolated |
|---|---|---|
| 1 | A dated statement that civil registration is paper-based with no central digital register. | yes |
| 2 | A digital civil registration system procured, piloted or rolled out to some offices. | yes |
| 3 | A digital civil register in service nationally for births, with historic records or other events (deaths, marriages) not yet digitised, and coverage below the targets. | yes |
| 4 | Digital registration of all vital events in service, historic records digitised or in progress, coverage published and rising, and linkage to the ID and statistics on record. | yes |
| 5 | The SDG 17.19.2(b) target (100 % of births, 80 % of deaths registered) met on the published figure and the register the source for legal identity and vital statistics. | no |

### `dpi.registry--address-register` — norm: UPU "Addressing the world" (global tier; top)

| stage | anchor | interpolated |
|---|---|---|
| 1 | A dated statement that no national addressing system exists — no street naming or numbering beyond some cities. | yes |
| 2 | A national addressing policy adopted or a project under way in some cities or districts. | yes |
| 3 | An address register in service for the main cities, not linked to other registers. | yes |
| 4 | A national address register in service with rural coverage, linked to the cadastre, the population register or postal codes, and used by services (delivery, emergency, utilities) on record. | yes |
| 5 | The UPU end state: a national addressing policy implemented, an address for everyone, and the register a base register for other systems. | no |

### `dpi.registry--business-register` — norm: DTS "eBusiness register"; DTP Art. 14 (top; UNCITRAL Legislative Guide as reference)

| stage | anchor | interpolated |
|---|---|---|
| 1 | A dated statement that business registration is paper-based and held locally. | yes |
| 2 | A digital business register procured, or the historic stock being converted, or a one-stop counter opened in the capital only. | yes |
| 3 | Online registration in service with a unique business identifier, in some locations or with the register not public. | yes |
| 4 | Online registration nationwide with a unique identifier shared with tax and social security, public search, and beneficial-ownership information collected on record. | yes |
| 5 | The DTS and DTP end state: an electronic business register as the identity of juridical persons, linked across registers and recognised across borders. | no |

### `dpi.registry--social-protection-register` — norm: Protocol on Social Protection Art. 23 (top; World Bank typology as reference)

| stage | anchor | interpolated |
|---|---|---|
| 1 | A dated statement that no social registry exists — programmes hold their own lists. | yes |
| 2 | A social registry procured, piloted or being populated in some districts. | yes |
| 3 | A social registry in service covering part of the population or one or two programmes. | yes |
| 4 | A social registry in service covering the target population, used by the main programmes for eligibility, linked to the ID and updated dynamically, with coverage published. | yes |
| 5 | The Protocol's end state: a social registry and integrated beneficiary registry as the basis of social protection management, interoperable with civil registration and payments. | no |

### `dpi.registry--electoral-register` — norm: ACDEG Art. 17; AU EOM Guidelines §§4.6.10, 5.2.9, 5.4.1 (rungs: accuracy, non-discrimination, public access, updating)

| stage | anchor | interpolated |
|---|---|---|
| 1 | A dated statement that no electoral register is maintained between elections, or that the register is compiled by hand for each poll. | yes |
| 2 | A digital or biometric register procured or piloted; a register compiled digitally but not maintained. | yes |
| 3 | A digital register in service, with public access to the roll provided (Guidelines §5.2.9) and periodic revision. | no |
| 4 | The register maintained continuously and drawn from or reconciled with the civil or population register, with published audits and non-discriminatory registration on record (§4.6.10). | no |
| 5 | The ACDEG end state: an independent electoral body maintaining a register recognised as accurate by observation missions, continuously updated from the base registers. | no |

### `dpi.registry--tax-register` — norm: TADAT POA1 P1-1 (global tier; rungs A–D)

| stage | anchor | interpolated |
|---|---|---|
| 1 | A dated statement that no taxpayer register exists or that it is paper-based. | yes |
| 2 | TADAT D: a computerised register with multiple identifiers, decentralised, no linkage, or integrity not assessed. | no |
| 3 | TADAT C: decentralised databases linked by a common identifier. | no |
| 4 | TADAT B: a centralised database with more than one identifier scheme linked, or a whole-of-taxpayer view not yet complete. | no |
| 5 | TADAT A: each taxpayer with a unique high-integrity identifier, one centralised database, a whole-of-taxpayer view, and the identifier shared with other registers. | no |

### `dpi.registry--land-register` — norm: AU Declaration on Land (2009); Framework and Guidelines on Land Policy §3.6.2 (top; UN-GGIM FELA, ISO 19152 LADM as reference)

| stage | anchor | interpolated |
|---|---|---|
| 1 | A dated statement that land rights are recorded on paper or not recorded, with no cadastre. | yes |
| 2 | Digitisation of titles or a cadastre project under way in some areas or for some tenure types. | yes |
| 3 | A digital cadastre or title register in service for part of the territory or for formal tenure only. | yes |
| 4 | A national digital cadastre and register in service, parcels counted and published, registration mandatory for transactions, linked to the tax authority or the ID. | yes |
| 5 | The F&G end state (§3.6.2): registration and tracking of land rights through a computerised land information system, customary tenure included as §3.6 requires, with public access — e.g. on the LADM standard and FELA's pathways. | no |

### `dpi.mis--health` — norm: Africa CDC Digital Transformation Strategy; HIE Guidelines (top; WHO GSDH as reference)

| stage | anchor | interpolated |
|---|---|---|
| 1 | A dated statement that health reporting is paper-based with no national HMIS. | yes |
| 2 | An HMIS procured, piloted or rolled out in some districts. | yes |
| 3 | A national HMIS in service (district reporting) with some facilities or the private sector outside it and other systems (surveillance, supply chain, registries) separate. | yes |
| 4 | The HMIS in service across public and private facilities, with surveillance, supply chain and at least one registry (vaccination, patient) integrated or interoperable, and reporting completeness published. | yes |
| 5 | The Africa CDC end state: national digital health systems strengthened to the HIE Guidelines, facilities connected, and participation in continental surveillance and the health data space. | no |

### `dpi.mis--education` — norm: AU Digital Education Strategy SO4 (rungs: EMIS 1.0 → 2.0)

| stage | anchor | interpolated |
|---|---|---|
| 1 | A dated statement that no EMIS exists. | yes |
| 2 | An EMIS procured, piloted or under construction. | yes |
| 3 | EMIS 1.0 in service: aggregate school returns and an annual census published. | no |
| 4 | EMIS 2.0 in service: individual learner, teacher and institution records with unique identifiers, used for planning and payroll. | no |
| 5 | The DES end state: EMIS 2.0 linked to the national ID and other sectors, analytics in use for policy, and the data model published. | no |

### `dpi.mis--social-protection` — norm: Protocol on Social Protection Arts 23, 25 (top; GTMI I-11 as reference)

| stage | anchor | interpolated |
|---|---|---|
| 1 | A dated statement that social protection programmes are administered on paper. | yes |
| 2 | A programme MIS procured, piloted or under construction. | yes |
| 3 | A programme MIS in service for one or a few programmes, not linked to payments or the ID. | yes |
| 4 | An MIS in service across the main programmes, linked to the social registry, the ID and payment providers, with disaggregated data published (Art. 25). | yes |
| 5 | The Protocol's end state: an integrated social protection information system across contributory and non-contributory schemes with portability provided for. | no |

### `dpi.mis--justice` — norm: ACHPR Fair Trial Principles (2003) (top, weak)

| stage | anchor | interpolated |
|---|---|---|
| 1 | A dated statement that court proceedings and records are paper-based with no case-management system. | yes |
| 2 | A case-management or e-justice system procured, piloted in some courts, or under construction. | yes |
| 3 | A case-management system in service in some courts or one tier, with decisions not published online. | yes |
| 4 | Case management in service across the main courts, e-filing available, and decisions published online with public access to case status. | yes |
| 5 | The Principles' end state: systems for recording proceedings, storing information and public access in service across the judiciary, all decisions published, and integration with police, prosecution and prisons on record. | no |

### `dpi.mis--tax` — norm: TADAT P4-14 (use of electronic filing facilities) and P5-15 (use of electronic payment methods) (global tier; rungs A–D)

POA1 is `dpi.registry--tax-register`'s. This row reads two TADAT indicators and **the lower of the two decides the stage**, the qualifier naming which; the assessor applies the Field Guide's criteria to the base's own rows (see the chapter note).

| stage | anchor | interpolated |
|---|---|---|
| 1 | A dated statement that tax administration runs on paper. | yes |
| 2 | D on both: electronic filing or payment unavailable or available for one core tax or segment only, on the base's own rows. | no |
| 3 | C on the lower: electronic filing (P4-14) and payment (P5-15) available for some core taxes or segments, with low uptake or partial coverage on record. | no |
| 4 | B on the lower: electronic filing and payment available for most core taxes and segments, uptake published and rising. | no |
| 5 | A on both: mandatory electronic filing for designated segments across all core taxes with real-time acknowledgment, and electronic payment available for all core taxes and all segments through multiple channels with immediate confirmation. | no |

### `dpi.mis--customs` — norm: AfCFTA Protocol on Trade in Goods Annexes 3 and 4 (top; WCO Revised Kyoto Convention, GTMI I-8/I-23 as reference)

| stage | anchor | interpolated |
|---|---|---|
| 1 | A dated statement that customs declarations are processed on paper. | yes |
| 2 | A customs management system procured, piloted at some posts, or being upgraded. | yes |
| 3 | An automated customs system in service at the main ports and airports, with paper at other posts and no single window. | yes |
| 4 | Automated processing at all posts, risk management in use, electronic payment of duties, and a single window in service or under phased rollout with agencies connected. | yes |
| 5 | The Annexes' end state: customs automation, a national single window connecting all border agencies, electronic exchange with trading partners, and the trade-facilitation measures in effect. | no |

### `dpi.mis--land` — norm: AU Declaration on Land (2009); Framework and Guidelines on Land Policy §3.6.2 (top; UN-GGIM FELA as reference)

| stage | anchor | interpolated |
|---|---|---|
| 1 | A dated statement that land administration (transactions, valuation, planning) runs on paper. | yes |
| 2 | A land information system procured, piloted in some regions or under construction. | yes |
| 3 | A land information system in service for registration in some areas, with valuation, planning and dispute records separate. | yes |
| 4 | A land information system in service nationally linking registration, cadastre and valuation, with transactions processed electronically and linked to the tax authority. | yes |
| 5 | The F&G end state (§3.6.2): a computerised land information system through which land rights are registered and tracked across the administration functions, customary tenure included, with public access — e.g. integrated across FELA's pathways on the LADM standard. | no |

### `dpi.govtech--e-government-services` — norm: DTS single digital gateway; Public Service Charter Art. 8 (top; UN EGDI bands, GTMI groups as reference)

| stage | anchor | interpolated |
|---|---|---|
| 1 | A dated statement that no government service is available online, or that no inventory of online services exists and none is on record. | yes |
| 2 | A portal launched with information only, or a few transactional services piloted, or one-stop service desks under operationalisation. | yes |
| 3 | Transactional services in service — tens of services dematerialised — on several portals with no single gateway or shared authentication. | yes |
| 4 | A single gateway or integrated portal in service carrying the main services with shared authentication through the national ID, usage published, and an inventory of services maintained. | yes |
| 5 | The DTS end state: a single digital gateway integrating all e-government services (G2C, G2B, G2G) on the exchange layer and the national ID, with service levels and usage reported. | no |

## DPI — notes for CC's review

- **Two rows read the same evidence from two sides**: `dpi.exchange--use-of-digital-id-in-other-systems` (the consuming systems) and `dpi.id--use-by-other-systems` (the ID as the base register). The distinction is stated on the second row; if CC finds the assessor cannot keep them apart on real rows, the second could be narrowed to *public registers keyed on the national number* and the first to *services consuming a verification API*, which is roughly what the anchors already say.
- **`dpi.id--national-maintenance-of-id-and-credentials-systems`** overlaps the sovereignty indicator by design; both rows say so and the sovereignty row's *which part decides* rule handles the estate-level reading.
- **The two TADAT rows** (`tax-register`, `mis--tax`) carry TADAT's own A–D scoring as rungs marked `no`; the anchors paraphrase the Field Guide's criteria, checked level by level on 2026-09-23. **The assessor applies TADAT's criteria for the named indicators (P1-1; P4-14 and P5-15) to the base's own rows; a published TADAT assessment is a reference, cited in the qualifier where it disagrees** — never the record (`maturity-assessment-norms.md` §7).
- **`dpi.id--digital-id-from-birth`** is a system with a numeric target on its stage 5; the coverage figure that decides stage 5 belongs to the measure `dpi.id--registration-of-entire-population` (C3), so this row's stage 5 cites the published figure without defining it.
- **Weak anchors** (`land-register`, `mis--land`, `mis--justice`) lean on FELA and the Fair Trial Principles for their end states; the register already marks them weak and the published count will carry them.

## DPI — changes made on CC's first review (2026-09-23)

`maturity-rubric-review.md` returned the chapter with six items; all six are in the file above.

- **1** — no CAMCR 2022 target: `digital-id-from-birth` (heading and stage 5) and `civil-register` (heading and stage 5) now name the SDG 17.19.2(b) target (100 % of births, 80 % of deaths registered), and the digital-ID heading carries the register's anchor (DTS; SDG 17.19.2(b); AU No Name Campaign declaration).
- **2** — the education and social-protection exchange rows are rebased on links (2 a link planned or piloted; 3 one exchange in service; 4 exchanges across the main systems on a shared identifier; 5 as drafted); education stage 3 is now `yes` and stages 4–5 stay `no` on the DES's EMIS 2.0; the MIS rows keep their own ladders.
- **3** — both land rows' stage 5 is the F&G §3.6.2 end state, customary tenure included, with LADM and FELA moved to *e.g.*; headings name the F&G section.
- **4** — the TADAT rule is in the chapter note: the assessor applies the criteria to the base's own rows; a published assessment is a reference in the qualifier.
- **5** — `mis--tax` names P4-14 and P5-15, drops POA1, and takes the lower of the two; the anchors follow the Field Guide's A-level criteria as read on 2026-09-23 (P4-14: mandatory e-filing for designated segments across all core taxes with real-time acknowledgment; P5-15: e-payment for all core taxes and all segments through multiple channels with immediate confirmation).
- **6** — `dpi.exchange--use-of-digital-id-in-other-systems` stage 4 reads services consuming a verification or authentication service; the public registers are left to `dpi.id--use-by-other-systems`.

One correction outside the draft: the register's `dpi.pay--revenue-collection` reference said *TADAT POA5 P5-2*; the 2019 Field Guide numbers indicators continuously and electronic payment is P5-15. The register row is corrected.

---

## Infrastructure, Digitalisation and Technology — accepted and cut 2026-09-23

Three chapters in one leg, because once the measures are held for C3 they are small: Infrastructure's seven non-measure rows (four systems, three instruments), Digitalisation's six systems, Technology's six (four systems, two instruments) — 19 indicators, 95 anchors. Infrastructure's nine measures (penetration, usage, affordability, bandwidth, the two data-centre capacities, energy and water, grid, rural electrification) and Technology's one (`tech.industry--national-capacity-in-dt-related-production`) are C3.

### `infra.connect--national-fibre-backbone` — norm: DTS; PIDA PAP 2; DPF §5.3.1 (top)

Length in kilometres is evidence for reach but is not banded here (no norm sets a figure); the qualifier carries the latest cited length and its date.

| stage | anchor | interpolated |
|---|---|---|
| 1 | A dated statement that no national fibre backbone exists — connectivity by satellite or microwave only, or fibre confined to one city. | yes |
| 2 | A backbone under construction, contracted or planned in a master plan, with segments not yet in service; or fibre reaching some regions with no national plan. | yes |
| 3 | A backbone in service reaching some provinces or regions, with others unserved on record, or reaching all regions on one operator's network with no open access. | yes |
| 4 | A backbone in service reaching every province or region on record, with open-access or wholesale terms published, at least one cross-border link in service, and a current length figure cited. | yes |
| 5 | The DTS and DPF end state: a national infrastructure master plan implemented, the backbone connected to regional backbones and cables with redundancy, infrastructure sharing and rights-of-way rules in force, and reach and capacity reported. | no |

### `infra.connect--internet-exchange-points` — norm: DTS; AXIS; DPF §5.3.1 (top)

| stage | anchor | interpolated |
|---|---|---|
| 1 | A dated statement that no internet exchange point operates in the country. | yes |
| 2 | An IXP established by decree, planned or equipped with no members peering, or peering suspended. | yes |
| 3 | One IXP in service with a small membership (a handful of members), capacity or traffic cited. | yes |
| 4 | One or more IXPs in service with the main operators, content networks and the government network peering, traffic or capacity published at two dates at least 12 months apart showing growth, and a second exchange or a second city on record. | yes |
| 5 | The DTS and AXIS end state: national exchange points keeping domestic traffic local, connected to a regional hub, with barriers to entry removed and traffic reported. | no |

### `infra.connect--satellite-broadband-licensing-and-availability` — norm: ATU-R Rec. 005-0; African Space Strategy (rungs: individual → blanket → mutual recognition) — kind: instrument

| stage | anchor | interpolated |
|---|---|---|
| 1 | A dated statement that satellite broadband is not licensed, or that applications are refused or unanswered. | yes |
| 2 | A licence application pending or a framework in drafting; a licence granted to one operator with no service launched. | yes |
| 3 | Satellite broadband licensed and in service, with user terminals authorised individually or through a single licensee (ATU-R 005-0's *individual* case). | no |
| 4 | Terminals licensed on a blanket or class basis, more than one operator or reseller licensed, and NGSO authorisation streamlined with published fees (the *blanket licensing* case). | no |
| 5 | The ATU recommendation's end state: blanket licensing, free circulation of visiting terminals on mutual recognition, spectrum fees published with no refusal or withdrawal on fee grounds on record, and availability reported. | no |

### `infra.store--off-site-backup-capacity` — norm: Smart Africa Data Center and Cloud Blueprint (continental tier; top; ISO 22301, GTMI CGSI as reference)

| stage | anchor | interpolated |
|---|---|---|
| 1 | A dated statement that government systems have no off-site backup or disaster-recovery site. | yes |
| 2 | Backup or virtualisation equipment procured, a secondary site planned or contracted, or one institution (the central bank, the tax authority) holding its own alternative site with nothing for the estate. | yes |
| 3 | A government backup or recovery site in service for some systems, or a commercial or satellite provider supplying redundancy under contract, with no continuity plan on record. | yes |
| 4 | A government disaster-recovery site in service for the core systems, physically separate, with a continuity plan, tested failover or a recovery exercise on record, and Tier or availability level stated. | yes |
| 5 | The Blueprint's end state: 24/7 availability for e-government on a Tier-classified primary and secondary site, continuity management to a recognised standard, and availability reported. | no |

### `infra.capacity--robustness-of-government-hardware-and-software` — norm: Public Service Charter Art. 8; DTS (top; GTMI CGSI groups as reference)

| stage | anchor | interpolated |
|---|---|---|
| 1 | A dated statement that core government systems run on unsupported or obsolete platforms, with outages on record and no inventory. | yes |
| 2 | Core systems being replaced or procured — a financial system out to tender, a revenue platform contracted — with the estate last described years ago and no inventory. | yes |
| 3 | The main core systems (finance, revenue, payroll, the state network) in service on supported platforms, with a mandated custodian body, and no enterprise architecture or inventory published. | yes |
| 4 | Core systems in service on supported platforms under a custodian with an inventory or enterprise architecture, a government network and data centre operating, and incidents or availability reported. | yes |
| 5 | The Charter's end state: modern technologies used across service delivery, an enterprise architecture and shared platforms (cloud, service bus) in service, and performance reported. | no |

### `infra.capacity--local-capacity-to-maintain-manage-and-develop-government-systems` — norm: Public Service Charter Art. 21; DPF (top; GTMI Enablers Index as reference) — kind: instrument

| stage | anchor | interpolated |
|---|---|---|
| 1 | A dated statement that government systems are built and maintained by external suppliers with no in-house technical staff or programme. | yes |
| 2 | A capacity programme announced, a change-management or training exercise run for one system, or bodies stated to require technical assistance to operate what they hold. | yes |
| 3 | In-house teams maintaining or developing some systems on record (a statistics office building its own portal, a tax authority feeding its own risk system), with no systematic programme. | yes |
| 4 | A systematic capacity programme in force — a government IT cadre or agency with a mandate, training partnerships with institutions, systems built or maintained in-house across several bodies on record. | yes |
| 5 | The Charter's Art. 21 end state: systematic, evidence-based capacity development across the public service, collaboration with management and research institutions, and the estate maintained and developed nationally. | no |

### `infra.cybersec--national-cybersecurity-readiness` — norm: Malabo ch. III; DTS (top; ITU GCI tiers, Oxford CMM as reference) — kind: instrument

A composite of policy, law, institutions and operating record; the anchors count them in the order Malabo's chapter III gives, and the lower element decides.

| stage | anchor | interpolated |
|---|---|---|
| 1 | A dated statement that no national cybersecurity policy, strategy, law or institution exists. | yes |
| 2 | A strategy, council or cyber centre created by decree or announced, none with an operating record; or a law in drafting. | yes |
| 3 | A strategy adopted and a law in force, with the institutions (agency, CERT) constituted but no incident-response, enforcement or reporting record. | yes |
| 4 | Strategy, law and institutions operating: a national CERT responding to incidents on record, enforcement or prosecutions, a critical-infrastructure regime, and reporting published. | yes |
| 5 | Malabo chapter III met — policy, strategy, law, institutional mechanism, Malabo ratified — with regional cooperation on record and readiness reported to a recognised assessment. | no |

### `digital.localgov--ict-infrastructure-for-local-government` — norm: Decentralisation Charter Art. 16 (top; UN LOSI as reference)

| stage | anchor | interpolated |
|---|---|---|
| 1 | A dated statement that local governments have no ICT infrastructure — no connectivity, equipment or systems below national level. | yes |
| 2 | Equipment or connectivity delivered to some local administrations, a contract to extend it, or one province procuring its own system. | yes |
| 3 | Local administrations connected and equipped in some regions or tiers, with no national programme covering the rest. | yes |
| 4 | A national programme in force connecting and equipping local administrations across tiers, coverage published, and local systems (revenue, permits, records) in service in the main units. | yes |
| 5 | The Charter's Art. 16 end state: ICT accessible across local governments and in use for local services on record (revenue, permits, records, citizen feedback), local governments provided the technological resources to discharge their responsibilities, and coverage reported. | no |

### `digital.localgov--digitalisation-of-local-government-records` — norm: DTS; Decentralisation Charter Art. 16 (top; UN EGDI, ISO 15489 as reference)

| stage | anchor | interpolated |
|---|---|---|
| 1 | A dated statement that local government records — civil, land, revenue, minutes — are held on paper. | yes |
| 2 | A records or archive system approved or procured by one or some local governments, or a central platform being built to collect from local units. | yes |
| 3 | Digital records in service in some local governments or for one record type (a parcel register, a revenue roll), with paper elsewhere. | yes |
| 4 | Digital records in service across the main local governments and record types, on a national platform or standard, exchanging with the central registers. | yes |
| 5 | The DTS end state: local registers digitised and reused through the exchange layer as core registers, with coverage reported. | no |

### `digital.rural--digitalisation-of-rural-health-clinics` — norm: Africa CDC Digital Transformation Strategy (HealthConnekt Africa: 100,000 facilities connected and 2 m community health workers equipped by 2030); PHC Digitalisation Framework (90 % digitally enabled PHC by 2035) (target)

The `digital.rural` rows share one ladder — connected · equipped · records digital · linked to the national system — and their stage 5 is the sector target on the published figure.

| stage | anchor | interpolated |
|---|---|---|
| 1 | A dated statement that rural or primary facilities have no connectivity, equipment or digital reporting. | yes |
| 2 | Connectivity or devices delivered to some facilities, staff trained on a digital tool, or a rollout beyond pilot sites planned. | yes |
| 3 | Rural facilities connected and reporting digitally in some districts, or one function digital (surveillance, laboratory, supply chain) with the rest on paper. | yes |
| 4 | Rural facilities connected and equipped across most districts, patient or reporting records digital, linked to the national HMIS, and the share of facilities covered published. | yes |
| 5 | The Africa CDC end state: the country's facilities and community health workers connected and equipped on the published figure, primary care digitally enabled to the framework's standard, and coverage reported. | no |

### `digital.rural--digitalisation-of-rural-primary-schools` — norm: AU Digital Education Strategy (devices for 20 % of students and 50 % of teachers by 2027, a third and all by 2030; 50 % of institutions connected; five maturity categories) (target + rungs; ITU UMC 2030 schools as reference)

| stage | anchor | interpolated |
|---|---|---|
| 1 | A dated statement that rural primary schools have no connectivity or computers. | yes |
| 2 | Devices or connectivity tendered or delivered to some rural schools, or a national school-connectivity programme announced. | yes |
| 3 | Rural schools connected or equipped in some districts on record, with the national shares of connected institutions and equipped students below the DES 2027 figures. | yes |
| 4 | The DES 2027 figures met on the published figure — at least 50 % of institutions connected, devices for 20 % of students and 50 % of teachers — with rural schools inside the count. | no |
| 5 | The DES 2030 figures met — devices for a third of students and all teachers, connectivity at the DES cost line — with the country in the DES's top maturity category. | no |

### `digital.rural--digitalisation-of-rural-registry-offices` — norm: DTS (99.9 % digital legal identity by 2030); APAI-CRVS; Kampala Convention Art. 13 (target)

| stage | anchor | interpolated |
|---|---|---|
| 1 | A dated statement that registration offices outside the main cities work on paper with no connectivity. | yes |
| 2 | A digital registration platform piloted in a first group of communes or districts, or equipment rehabilitated at some posts. | yes |
| 3 | Digital registration in service in some rural offices or districts, with the rest on paper or transmitting by hand. | yes |
| 4 | Rural offices connected and registering digitally across most districts, records flowing to the central register, and the share of offices covered published. | yes |
| 5 | The DTS end state: every office registering digitally into the civil register and the ID system, with the DTS legal-identity target met on the published figure and IDP and displaced populations served (Kampala Art. 13). | no |

### `digital.rural--digitalisation-of-rural-police-stations` — norm: Corpus-defined (no instrument at any tier below the national police agency; AFRIPOL Statute for the national end)

| stage | anchor | interpolated |
|---|---|---|
| 1 | A dated statement that police posts outside the capital have no connectivity or case-recording system. | yes |
| 2 | A centralised police platform under build or piloted with no provincial post named, or an integrated security centre announced for one province. | yes |
| 3 | Provincial or district stations connected and recording on a system in some regions on record. | yes |
| 4 | Stations connected and recording digitally across most provinces, records flowing to a national platform, and coverage published. | yes |
| 5 | Every station on the national platform, linked to the justice case-management system and the national ID for verification, with the national agency connected to AFRIPOL's systems. | yes |

### `tech.ai--use-of-ai-in-government-administration` — norm: Continental AI Strategy, public-sector action area (top)

| stage | anchor | interpolated |
|---|---|---|
| 1 | A dated statement that no AI system is in use in public administration, or that public data is unfit for advanced analytics. | yes |
| 2 | An AI platform for administration authorised, tendered or piloted in one body. | yes |
| 3 | One or two AI systems in service in administration (a chatbot for a service, document processing in one ministry) on record. | yes |
| 4 | AI in service across several bodies with a published inventory or use-case register, procurement rules for AI, and impact or performance reported. | yes |
| 5 | The AI Strategy's end state: AI adopted in the public sector under a governance framework, innovation-friendly procurement, capacity in place, and use cases shared and reported. | no |

### `tech.ai--use-of-ai-in-sectoral-management-information-systems` — norm: Continental AI Strategy, core-sectors action area; DPF §5.3 (top)

| stage | anchor | interpolated |
|---|---|---|
| 1 | A dated statement that no sectoral system (health, agriculture, education, tax, climate) uses AI or advanced analytics. | yes |
| 2 | A sectoral AI tool in pilot or testing (a diagnostic tool in two provinces, a risk-analysis model in testing). | yes |
| 3 | One sectoral AI system in service and producing decisions or outputs on record (a tax risk engine issuing notices, a disease model informing a campaign). | yes |
| 4 | AI in service in several sectors' systems, built or adapted nationally, with data warehouses or pipelines supporting them and results reported. | yes |
| 5 | The AI Strategy's end state: AI adopted in the core sectors, national centres of excellence or datasets supporting it, and outcomes reported. | no |

### `tech.ai--development-of-national-regional-ai-systems` — norm: Continental AI Strategy (infrastructure, datasets, talent; "Local First"); Smart Africa AI Council (top)

| stage | anchor | interpolated |
|---|---|---|
| 1 | A dated statement that no AI model, dataset or compute facility is developed or hosted nationally. | yes |
| 2 | Local AI builds named without funding, users or deployment; a compute facility or national dataset planned. | yes |
| 3 | A national AI model, dataset or compute facility in service on record (a language model deployed, a national data facility with accelerators, a curated national dataset published). | yes |
| 4 | National or regional AI capacity in service across the three — compute, datasets, talent — with a funded programme, a research or industry ecosystem using it, and usage reported. | yes |
| 5 | The AI Strategy's end state: the country able to self-manage its data and AI on "Local First" — sovereign or regional compute, open national datasets, talent pipelines — and participating in continental AI infrastructure. | no |

### `tech.ai--control-of-ai-abuse` — norm: Continental AI Strategy focus area 2; DTP Annex on Emerging and Advanced Technologies (top) — kind: instrument

| stage | anchor | interpolated |
|---|---|---|
| 1 | A dated statement that no authority, rule or mechanism addresses AI harms — misinformation, manipulation, bias, unsafe systems. | yes |
| 2 | A draft law providing for a competent authority without designating it; a workshop, guideline or ethics principle with no legal effect. | yes |
| 3 | A rule in force addressing at least one AI harm (deepfakes, automated decisions, election manipulation) or an authority designated with a mandate, with no enforcement on record. | yes |
| 4 | An authority operating with powers over AI harms, risk-based rules in force, and enforcement, audit or redress decisions on record. | yes |
| 5 | The AI Strategy's end state: risk-based regulation, an independent oversight institution with enforcement and redress, technical safety standards, and participation in regional oversight (the AI Ethics Board or REC arrangements). | no |

### `tech.innovate--technology-hubs` — norm: DTS (a technology park and incubation hub in each region; local innovation centres) (top; WIPO GII, hub counts as reference)

The DTS target is regional; a country's stage reads its own hubs, and the regional park is stage 5's evidence.

| stage | anchor | interpolated |
|---|---|---|
| 1 | A dated statement that no technology hub, incubator or park operates in the country. | yes |
| 2 | A hub or park announced, under construction, or one private hub with no programme on record. | yes |
| 3 | One or more hubs in service with incubation programmes and cohorts on record, in the capital only, or a park inaugurated with no tenants. | yes |
| 4 | Hubs in service in more than one city with public or partner support, programmes and outputs (startups incubated, jobs, funding raised) reported, and a science or technology park operating with tenants. | yes |
| 5 | The DTS end state: the country hosting its region's technology park and incubation hub, or a national park linked to it by an agreement on record; local innovation centres in service; outputs reported. | no |

### `tech.innovate--tech-startup-ecosystem` — norm: DTS (national start-up strategies and laws; innovation fund; angel networks); AU Startup Model Law Framework (rungs: seven areas) — kind: instrument

| stage | anchor | interpolated |
|---|---|---|
| 1 | A dated statement that no startup law, strategy or public support instrument exists and no venture or angel financing is on record. | yes |
| 2 | A startup bill drafted or tabled, a competition or grant scheme opened, or a strategy in consultation. | yes |
| 3 | A startup law or strategy enacted or adopted covering some of the Framework's seven areas (definition, governance, institutional support, taxation, funding, regulatory enablement, skills), with implementing measures pending. | no |
| 4 | The law in force with implementing measures across most of the seven areas — a labelling or registration regime operating, tax or procurement measures applied, a fund or angel network financing startups on record. | no |
| 5 | The DTS end state: a national startup strategy and law in force across the seven areas, an innovation fund and angel networks operating, patents and outcomes reported. | no |

## Infrastructure, Digitalisation and Technology — notes for CC's review

- **Three chapters in one leg.** Nineteen rows; if CC would rather review them as three, the file's headings already carry the chapter and the checker's chapter counts separate them.
- **`digital.rural` shares one ladder** and says so on the health row; the four differ at stage 5 by their sector target. The police row is the register's one `corpus` anchor and all five of its rungs are `yes`, including stage 5, which is Corpus's own end state.
- **The two DES-target rows** (`rural-primary-schools` stages 4–5) are marked `no` because the DES states the 2027 and 2030 figures. The figures are the DES's national ones; the row reads rural schools, which changes what the assessor counts, not who set the bar (CC, first review of this leg). The qualifier carries the rural share where the base holds it.
- **`national-cybersecurity-readiness`** is a composite like data-protection readiness and takes the same shape after the first review's item 7: the lower element decides.
- **`national-fibre-backbone`** does not band length; a norm for kilometres does not exist and the register's row says so. The latest cited length and its date go in the qualifier.
- **AI rows** lean on the AI Strategy's action areas for their end states with no AU numeric target anywhere; all three system rows have four interpolated rungs.

## Infrastructure, Digitalisation and Technology — changes made on CC's first review (2026-09-23)

`maturity-rubric-review.md` returned the leg with three one-line items; all three are in the file above, and the schools note is amended as CC asked.

- **1** — `internet-exchange-points`: *no growth in the window* deleted from stage 3; stage 4 reads *traffic or capacity published at two dates at least 12 months apart showing growth*.
- **2** — `gov.policy--open-data-policy` stage 4 (Governance, already cut): *publication activity in the 12 months to the as-at date*; CC re-cuts Governance with this leg.
- **3** — `technology-hubs` stage 5: *the country hosting its region's technology park, or a national park linked to it by an agreement on record*.
- **Schools** — stage 4 stays `no`; the note now says the figure is the DES's national one and the qualifier carries the rural share.

---

## Capacity, Inclusion, Data and Geopolitics — accepted and cut 2026-09-23

The last twelve instruments and systems: Capacity's one instrument, Inclusion's one system and three instruments, Data's two instruments and four systems, and the sovereignty indicator. Capacity's five measures, Inclusion's two and the rest of the frame's measures are C3. With this leg every assessed instrument and system has a rubric.

### `capacity.research--think-tanks-and-academic-departments-contributing-to-dt-policy` — norm: STISA-2034; Agenda 2063 STYIP (R&D ≥ 1 % of GDP; 10 % of global research output by 2033) (target, proxy) — kind: instrument

Neither instrument counts think tanks; the R&D share is a proxy for the environment, not the indicator's figure. The ladder reads institutions and their contribution on record.

| stage | anchor | interpolated |
|---|---|---|
| 1 | A dated statement that no research institution, think tank or academic department works on digital policy — no programme, chair, centre or publication on record. | yes |
| 2 | A first research activity on record — a workshop, a chair inaugurated, a university joining a research network — with no funded programme behind it. | yes |
| 3 | At least one institution with a funded programme, centre or department on digital transformation, publishing on it, with no role in a policy process on record. | yes |
| 4 | Institutions contributing to policy on record — a commissioned study cited in an instrument, seats on an advisory body, evidence to a consultation — across more than one institution, with public or partner funding. | yes |
| 5 | The STISA end state: a national research system on digital transformation funded toward the R&D benchmark, contributing to continental research output, and institutionalised in policy-making (a standing advisory role, a national research agenda). | no |

### `include.access--citizen-feedback-portals` — norm: Decentralisation Charter Art. 13; ACHPR Declaration Principle 29; ACDEG (top; UN E-Participation Index levels as reference)

| stage | anchor | interpolated |
|---|---|---|
| 1 | A dated statement that no digital channel exists for citizens to complain about or comment on public services — a physical complaints book, an office, or nothing. | yes |
| 2 | A complaints strategy validated, a digital reporting platform presented or piloted for one purpose, or an online channel sitting on a portal with no handling process on record. | yes |
| 3 | A digital feedback or complaints channel in service for one body or one service, with receipts or cases on record and no published outcomes. | yes |
| 4 | A national feedback channel in service across the main services and local governments, with cases, response times or resolutions published, and feedback routed to elected or accountable bodies on record (Charter Art. 13). | yes |
| 5 | The Charter and Declaration end state: ICT used so that residents give feedback to their elected representatives at national and local level, outcomes published proactively, and the channel covering local government on record. | no |

### `include.access--citizen-participation-in-policy` — norm: ACDEG Arts 3(7), 30, 31; Decentralisation Charter Art. 12; Maputo Protocol Art. 9 (top; UN EPI as reference) — kind: instrument

Distinct from `gov.discourse--non-governmental-contribution-to-national-policy`, which reads organised civil society's role in digital policy; this reads the citizen's own channel into policy, digital and otherwise, and the inclusion of special-needs groups.

| stage | anchor | interpolated |
|---|---|---|
| 1 | A dated statement that instruments are adopted with no public consultation and no mechanism for citizens to take part. | yes |
| 2 | An open consultation run on one instrument in the 12 months to the as-at date, on record, with no requirement or standing mechanism. | yes |
| 3 | Public consultation on digital instruments practised — more than one in the 12 months to the as-at date — with a stated procedure, and no published account of what changed. | yes |
| 4 | Consultation required by law or standing procedure, online and offline, with published responses and changes on record, and participation of women, youth and persons with disabilities provided for (ACDEG Art. 31, Maputo Art. 9). | yes |
| 5 | The ACDEG end state: citizen participation in the development process through structures established by law or standing practice at national and local level (ACDEG Art. 30, Charter Art. 12), with representation of special-needs groups reported and participation in decision-making on record. | no |

### `include.access--inclusion-of-persons-with-disabilities` — norm: AU Disability Protocol Arts 23, 24; DTS (top; UN CRPD Arts 9, 21, WCAG as reference) — kind: instrument

| stage | anchor | interpolated |
|---|---|---|
| 1 | A dated statement that no law or policy addresses access to information or digital services for persons with disabilities. | yes |
| 2 | A disability or accessibility bill or policy in drafting, or a general accessibility law in force with no provision on information or ICT. | yes |
| 3 | A law or policy in force requiring accessible formats or digital accessibility, with no standard, body or implementation on record. | yes |
| 4 | Accessibility requirements in force with a standard adopted for public digital services, a responsible body, and implementation on record — accessible portals audited, affordable devices or assistive programmes delivered. | yes |
| 5 | The Protocol's Arts 23–24 end state: public information delivered in formats and technologies suited to different disabilities without extra cost, private providers including internet-based ones mandated to supply accessible formats, and the Protocol ratified. | no |

### `include.access--inclusion-of-refugees-and-idps` — norm: Kampala Convention Art. 13; OAU Refugee Convention; ACHPR Declaration Principle 7 (top; GDC para 13(c), UNHCR digital inclusion as reference) — kind: instrument

| stage | anchor | interpolated |
|---|---|---|
| 1 | A dated statement that refugees or IDPs are not registered, hold no documents, or are excluded from digital services (SIM registration, ID, payments) — or that registration is suspended. | yes |
| 2 | Registration or documentation planned or resumed at one site, or a digital inclusion measure piloted (cash transfers to a group over phones). | yes |
| 3 | Refugees or IDPs registered and documented on record (biometric registration completed, identity documents held), with access to digital services limited or not provided for. | yes |
| 4 | Registration and documentation maintained nationally, documents replaced without unreasonable conditions (Kampala Art. 13), and access to SIM registration, digital ID or payments provided for in law or practice on record. | yes |
| 5 | The Convention and Declaration end state: updated registries, documents in the person's own name for women, men and separated children, participation in decisions affecting them, and digital inclusion of displaced populations reported. | no |

### `data.statistics--national-strategy-for-development-of-statistics` — norm: SHaSA 2 SO 3.1; African Charter on Statistics (top; PARIS21 NSDS guidelines, SPI as reference) — kind: instrument

| stage | anchor | interpolated |
|---|---|---|
| 1 | A dated statement that no national strategy for the development of statistics exists or that the last one expired with no successor. | yes |
| 2 | An NSDS announced as forthcoming, in drafting or under consultation, or expired with a successor in preparation. | yes |
| 3 | An NSDS adopted and published with a stated period, and no funding, implementation reporting or evaluation on record. | yes |
| 4 | The NSDS in force with a costed action plan, funding on record, and a monitoring or mid-term evaluation reported to the statistical system's governing body. | yes |
| 5 | The SHaSA end state: a current NSDS aligned to SHaSA (stating it), implemented and evaluated, with the Charter ratified and the national system coordinated under it. | no |

### `data.statistics--censuses-and-surveys` — norm: SHaSA 2 SO 1.1; Charter Art. 3 (top; ECOSOC E/RES/2025/13 census round as reference) — kind: instrument

| stage | anchor | interpolated |
|---|---|---|
| 1 | A dated statement that no census has been conducted in the current or previous round and no household survey programme runs. | yes |
| 2 | A census planned, mapped or funded for the current round, or a survey programme announced, with no enumeration. | yes |
| 3 | A census enumerated in the current round with preliminary results only, or a survey programme with irregular rounds. | yes |
| 4 | Definitive census results published for the current round with disaggregation and public access (portal, microdata), and a regular survey programme on record. | yes |
| 5 | The SHaSA and Charter end state: censuses in every round and surveys on a published calendar, produced under the Charter's principles and disseminated openly, with the round's requirements met. | no |

### `data.statistics--statistics-from-administrative-data` — norm: SHaSA 2 SO 1.1; Charter Art. 3; DTS (top; UN Fundamental Principle 5, SPI sources pillar as reference)

| stage | anchor | interpolated |
|---|---|---|
| 1 | A dated statement that official statistics are produced from censuses and surveys only, with administrative records unused. | yes |
| 2 | Use of administrative data planned or piloted — training taken, one register assessed, a pilot yearbook. | yes |
| 3 | One or two statistical products compiled from administrative registers on record (a sectoral yearbook, a civil-registration-based series). | yes |
| 4 | Administrative sources exploited systematically — several products across sectors, a quality framework or data-sharing agreements between the statistics office and registers on record. | yes |
| 5 | The SHaSA end state: administrative sources, civil registration included, a routine input to official statistics under the Charter, with the sources documented and quality reported. | no |

### `data.open--use-of-open-data` — norm: DPF; Africa Data Consensus; Charter Art. 3 (top; International Open Data Charter principles, ODIN, Global Data Barometer as reference)

Distinct from `gov.policy--open-data-policy`, which reads the instrument; this reads what is published and used.

| stage | anchor | interpolated |
|---|---|---|
| 1 | A dated statement that no public body publishes data for reuse — statistics behind request or fee, no licence, no portal. | yes |
| 2 | Data published on a portal or site with no open licence, bulk download or interface stated; or a portal planned or piloted. | yes |
| 3 | Data published under an open licence by at least one body (the statistics office), with download and no interface or reuse on record. | yes |
| 4 | Open data published across several bodies under a licence, with bulk download or an interface, and reuse on record — applications, research, journalism citing it, or a published usage figure. | yes |
| 5 | The DPF and Consensus end state: open by default across the data value chain, timely and disaggregated, interoperable through standards, and reuse reported — applications, research and reporting built on it on record. | no |

### `data.satellite--agricultural-use-of-satellite-data` — norm: African Space Strategy; AU Digital Agriculture Strategy (top; Digital Earth Africa, GEOGLAM as reference)

| stage | anchor | interpolated |
|---|---|---|
| 1 | A dated statement that no agricultural service or institution uses satellite or remote-sensing data. | yes |
| 2 | Satellite data used in a one-off exercise (census mapping, a study) or a crop-monitoring platform piloted in one province. | yes |
| 3 | A national crop-monitoring, early-warning or land-use service using satellite data in service for part of the country or one purpose. | yes |
| 4 | Satellite-based services in service nationally across purposes (crop monitoring, drought and locust early warning, land suitability), with outputs published on a schedule and used by the ministry or extension services on record. | yes |
| 5 | The Space Strategy end state: space-derived products used routinely for agricultural decision-making, data shared under a national policy on affordable and equitable access, and participation in a continental or regional programme on record. | no |

### `data.satellite--meteorological-use-of-satellite-data` — norm: Integrated African Strategy on Meteorology 2021–2030 (AMCOMET) (target: 100 % of NMHSs ISO 9001-certified; ≥ 5 % of NMHS budget to research; WIGOS and GBON implemented; WMO Early Warnings for All as reference)

| stage | anchor | interpolated |
|---|---|---|
| 1 | A dated statement that the national meteorological service receives no satellite data stream. | yes |
| 2 | A satellite reception station or data stream contracted or installed, or a viewer publishing satellite layers with no forecasting use on record. | yes |
| 3 | Satellite data received and used in forecasting or nowcasting on record, with the service outside WIGOS or GBON compliance and no early-warning products. | yes |
| 4 | Satellite data used in operational products — impact-based forecasts, early warnings — with WIGOS or GBON implementation on record and the service participating in a regional early-warning programme. | yes |
| 5 | The AMCOMET end state: sustained access to geostationary and polar-orbiting streams, GBON implemented, the service ISO 9001-certified, at least 5 % of its budget to research, and early warnings reaching the population (Early Warnings for All). | no |

### `geopol.sovereignty--digital-sovereignty` — norm: DPF; Continental AI Strategy; AU Interop. Framework Principle 7; DTS; Malabo Art. 14; AfCFTA DTP Arts 20, 22 (rungs: categories → portability → continental mechanism; target: ≥ 30 % of content hosted in Africa) — kind: instrument

The rubric as drafted in `indicator-digital-sovereignty.md` §5, carried here so the lookup has one source; the lowest of the three parts (hosting, maintainability, agreement terms) decides and the qualifier names it.

| stage | anchor | interpolated |
|---|---|---|
| 1 | No policy or law on where state data sits or who may process it; core systems (ID, payments, exchange, government hosting) operated by a foreign provider or partner with no exit, portability or jurisdiction terms on record; a citation for at least one of these. | yes |
| 2 | Sovereignty stated as a goal — a strategy, a DPF adoption, a draft classification or localisation clause, a national cloud announced — with nothing in force; agreements in the 12 months to the as-at date unconditioned. Also here: localisation requirements in force with no portability, interoperability or national capacity to run what is walled in. | yes |
| 3 | A data classification, localisation-by-category or government-hosting policy or law in force — the DPF's *categories* rung; at least one core system hosted under national jurisdiction or maintainable nationally on record; at least one external agreement in the 12 months to the as-at date carrying data-jurisdiction, portability or exit terms. | no |
| 4 | State data classified and hosted per the policy across the estate; core systems maintainable nationally — source code, skills, contracts with exit and portability terms — on record for the ID, payments and exchange layers; external agreements systematically carrying jurisdiction, portability and exit terms — the DPF's *portability* rung; the DPA or regulator having acted on a breach of them. | no |
| 5 | The DPF end state: category-based localisation with portability and interoperability across providers, participation in the continental cross-border data mechanism, national or regional cloud and AI capacity per "Local First", and the DTS hosting target met on the state's own content. | no |

## Capacity, Inclusion, Data and Geopolitics — notes for CC's review

- **Two rows read consultation from two sides**: `gov.discourse--non-governmental-contribution-to-national-policy` (cut; organised civil society's role) and `include.access--citizen-participation-in-policy` (the citizen's own channel and special-needs groups). The distinction is stated on the second row; the 12-month look-back is used on its stages 2–3 and on the sovereignty row's stages 2–3 for the same reason it was on open discussion, and CC's D2 exception should list them.
- **`data.open--use-of-open-data`** is the counterpart of the cut `gov.policy--open-data-policy` (instrument) and reads publication and reuse, as the row says.
- **The sovereignty row** is the indicator document's §5 rubric transcribed with three changes for consistency with the reviews: *in the window* became *the 12 months to the as-at date* (two agreements in one month would otherwise be noise), the DPF rungs are marked `no` per the register's *rungs* entry, and stage 5's `interpolated` follows the register. The indicator document should be brought into line by CC at the cut, or left as the design record with this file as the source — CC's call.
- **`meteorological-use-of-satellite-data`** carries AMCOMET's numeric indicators at stage 5 only; the stages below are interpolated because the strategy states pillars, not rungs.
- **`censuses-and-surveys`** is an instrument (the census programme) whose evidence is events; the ECOSOC round rule sits in the reference and stage 5 says *the round's requirements met* rather than naming 2025–2034, so the anchor survives the next round.

## Capacity, Inclusion, Data and Geopolitics — changes made on CC's first review (2026-09-23)

`maturity-rubric-review.md` returned the leg with two one-line items; both are in the file above.

- **1** — `citizen-feedback-portals` stage 5 stands on the Charter and Declaration: feedback reaching elected representatives at national and local level, outcomes published proactively, the channel covering local government. The E-Participation Index clause is dropped; the qualifier can cite the EPI level where it disagrees.
- **2** — `inclusion-of-persons-with-disabilities` stage 3 loses its second limb; a state report naming the gaps is evidence for stage 1 or 2 and the qualifier, not for a law in force.

Decided by CC and recorded here: D2's look-back exception is general to every anchor keyed on *the 12 months to the as-at date*; the sovereignty rubric's source is this file, with `indicator-digital-sovereignty.md` §5 pointing here.

---

## Measures — drafted 2026-09-24; CC's first review acted on, awaiting second review and cut (task C3)

All 22 measures in one leg, because they share one set of rules and reviewing them apart would mean reviewing the rules four times. Each measure has a specification — the list under its heading, for CC to cut into a proposed `lookups/maturity-measures.csv` (`indicator_id, value, unit, direction, population, record, reference, vintage, band_method, cuts, stage5_condition`) — and the usual five anchors, which state the cut points so that `lookups/maturity-rubric.csv` stands on its own.

### How to read a measure

**The value of record** (`maturity-assessment-norms.md` §7; `maturity-assessment.md` §4): a cited primary figure in the base — a regulator's statistics, a national survey or census, an audited count, a Corpus compile (`budgets/`, `outputs/non-state-finance/`) — takes precedence over the reference dataset's; the reference dataset's figure is used when the base holds nothing, or holds only a claim it contradicts. `value_source` says which, in one of four forms: a `raw/` slug, for a cited primary; `budgets/{ISO3}/{FY}.csv`; `outputs/non-state-finance/{ISO3}-nonstate.csv` (or another Corpus compile named in the row, such as `outputs/datasets/data-centres/data-centres.csv`); or `ref:{dataset}@{release date}`. The date is what makes a new figure a dated cause under the stability rule. A material disagreement goes in the qualifier. **A figure of a different definition is not the value** — SIM subscriptions are not unique subscribers, adults 15+ are not the whole population — and goes in the qualifier; if no figure of the stated definition is held the row is *No evidence*.

**`prep/africa-dpi-data.csv` is never the record.** Its measure variables are banded categories collected by Perplexity (its own chapter note says so); under the base's rule on second-hand syntheses they are leads — useful for finding a primary and for the DPI cross-check (`maturity-assessment.md` §8), not for setting a stage.

**Band methods**, one per measure, named in its specification:

- **target** — the norm states a value T. Stage 4 is T met. Below T the range is cut at fixed thirds of T (stage 1 below T/3, stage 2 from T/3, stage 3 from 2T/3), rounded and stated per row; for a lower-is-better measure the thirds become multiples (stage 3 up to 2T, stage 2 up to 3T, stage 1 above). Stage 5 is the row's stated end state. Fixed cuts do not move with other countries, so a country's stage changes only when its own figure does.
- **quintiles** — no African number. **Africa-only quintiles** *(Bill)* of the figures the assessment carries, cut at the baseline (as at 2026-07-31) and recut each July, the recut flagged `reassessed`. Cut only when at least fifteen countries hold a figure of the stated definition; until then the row's **provisional** absolute cuts apply and the anchor says so. On a row whose norm fixes the top, **the bottom three quintiles are stages 1–3, the top two are stage 4, and stage 5 needs the norm's end state as well**: a top-quintile country without it stays at 4, and a country with it is 5 whatever its quintile. For a lower-is-better measure, "bottom" means the worst-performing quintile.
- **fixed** — cut points stated in the row, where the value is a count or a ratio with natural breaks.

**Boundaries**: for a higher-is-better measure the lower bound is inclusive (*27–53* means 27 or more and less than 53); for a lower-is-better measure the upper bound is inclusive (*20–30* means more than 20 and at most 30).

**Two machine-read lines per specification** (CC, 2026-09-24): `Method` is the band method and the direction; `Cuts` is the lower bound of stages 2, 3, 4 and 5 for *higher*, the upper bound for *lower*, in the value's unit, with the stage-5 number left out where stage 5 is a condition only, and `provisional` marked where the cuts give way to quintiles. **The band is computed from the value and the cuts and is a ceiling**: a compound anchor or a secondary test may hold the stage below it, and stage 5 needs both the band's top and its condition. **Every quintile row states provisional cuts**, so that a stage is computable on the baseline's figures whatever the count; the provisional cuts were set without a distribution in the repo for most rows, and a cut that puts more than half the continent on one stage is revised before the baseline is cut, not after. **Stability**: a measure's stage moves on a new figure — its publication is the dated cause — or on a July recut, flagged `reassessed`; nothing else moves it. The figure's year prints beside the stage.

**What fixes a rung** follows the register as for the other kinds: a target stage is `no`; the thirds and quintiles below it are `yes`; a reference that informs a cut (Broadband Commission, ITU UMC, GPEDC) leaves it `yes`.

---

### `finance.sustain--financial-sustainability-of-digital-systems` — norm: Agenda 2063 Goal 20; AAAA area I; DTS (target (proxy) + Africa quintiles)

- **Value**: domestic-state share of the digital lines of the state's own budget document, latest read fiscal year — domestic-state ÷ (domestic-state + externally financed digital lines in the same document), at the first stage both sides carry. **Unit** per cent · **direction** higher.
- **Record**: `budgets/{ISO3}/{FY}.csv` with `external.csv`, computed by `budget_source.share()`; `value_source` is the country-year's `source_slug`. No reference dataset exists; the only source is Corpus's own.
- **Band**: provisional fixed cuts at 20 · 40 · 60 · 80 until fifteen countries hold a read country-year (five on 2026-09-23), then Africa quintiles. **Secondary**: execution against voted and recurrent coverage can lower the stage by one, never raise it (`indicator-financial-sustainability.md` §5).
- **Method**: fixed · higher
- **Cuts**: 20 · 40 · 60 · 80 — provisional; Africa quintiles at fifteen read countries

| stage | anchor | interpolated |
|---|---|---|
| 1 | Domestic-state share below 20 % (provisional; bottom quintile once cut), or no domestic-state digital line in a read budget document. | yes |
| 2 | Share 20–40 % (provisional; second quintile): digital lines appropriated but the majority externally financed. | yes |
| 3 | Share 40–60 % (provisional; middle quintile), with recurrent lines present and domestic. | yes |
| 4 | Share 60–80 % (provisional; fourth quintile), recurrent costs domestic, and execution against voted on record where an outturn is held. | yes |
| 5 | Share 80 % or more (provisional; top quintile) with multi-year domestic financing, external finance confined to capital, and an audited outturn published — the Goal 20 posture applied to the digital estate. | partly — Goal 20 states the posture, not the digital share |

### `finance.new--mobilisation-of-non-state-finance` — norm: DTS; Smart Africa; Agenda 2063 Goal 20 (target (continental))

- **Value**: non-state finance committed to private digital beneficiaries, as a share of GDP: commitments whose `start_year` is the as-at year or either of the two before, summed and divided by three. From `outputs/non-state-finance/{ISO3}-nonstate.csv`: rows whose `beneficiary_type` is Private Sector, Fund or PPP, any financier, `status` Active, Approved or Closed (Pipeline and Unknown excluded), `instrument` not MoU or Unknown. **Commitments to NGO, Multilateral, Research and Multi-stakeholder beneficiaries count in neither finance row** — they are neither private capital nor finance to the state. **Unit** per cent of GDP · **direction** higher.
- **Record**: the Corpus compile. GDP: World Bank WDI, current USD, latest year, named in the qualifier. **Reference**: none carries this measure.
- **Band**: Africa quintiles, with provisional cuts. Public-sector beneficiaries are `finance.new--development-partner-project-financing`'s evidence, never this row's, so no commitment is counted twice. **Zero is stage 1 whatever the quintile, and the quintiles are cut over the non-zero figures**: on 2026-09-24 more than half the units in the compile had no private digital commitment starting in 2024–26, so quintiles over all units would tie at zero.
- **Method**: quintiles · higher
- **Cuts**: 0.001 · 0.02 · 0.1 · 0.25 — provisional

| stage | anchor | interpolated |
|---|---|---|
| 1 | No non-state commitment to a private digital beneficiary starting in the three years, on the compile. | yes |
| 2 | Bottom two quintiles of the non-zero figures once cut; provisionally above zero and below 0.02 % of GDP a year. | yes |
| 3 | Middle quintile; provisionally 0.02–0.1 %. | yes |
| 4 | Fourth quintile; provisionally 0.1–0.25 %. | yes |
| 5 | Top quintile, provisionally 0.25 % or more, with private digital capital from domestic as well as foreign financiers on record — the Goal 20 and Smart Africa posture of mobilised private finance. | partly — the continental ambition, not a country figure |

### `finance.new--development-partner-project-financing` — norm: Agenda 2063 Goal 20 (target) — on-budget share, Bill 2026-09-24

- **Value**: the on-budget share of development-partner digital finance to the state — partner-financed digital lines printed in the state's own budget document (`budgets/{ISO3}/external.csv`, matched to held deals by the origin gate) ÷ partner digital commitments to public-sector beneficiaries active in the same fiscal year (`outputs/non-state-finance/`, `beneficiary_type` Public Sector). **Unit** per cent · **direction** higher.
- **Excluded beneficiaries**: commitments to NGO, Multilateral, Research and Multi-stakeholder beneficiaries count in neither finance row.
- **Why not the external share**: the external share of the digital budget is 100 % minus `finance.sustain`'s value; banding it here would count one fact twice. This row reads instead whether partner money runs through the state's own budget, which is what "Africa takes full responsibility" asks of partner finance.
- **Record**: the two Corpus compiles; only read country-years qualify, so coverage follows the budget-extract queue. **Reference**: GPEDC's on-budget indicator (development co-operation on budgets subject to parliamentary scrutiny); the 85 % line is the Paris Declaration's indicator 3 target as GPEDC carries it, not verified in this session.
- **Band**: provisional fixed cuts at 20 · 40 · 60 · 85 until fifteen countries hold a read country-year, then Africa quintiles for stages 1–4.
- **Method**: fixed · higher
- **Cuts**: 20 · 40 · 60 · 85 — provisional; Africa quintiles for stages 1–4 at fifteen read countries

| stage | anchor | interpolated |
|---|---|---|
| 1 | Less than 20 % of partner digital finance to the state printed in its budget document (provisional). | yes |
| 2 | 20–40 % on budget (provisional). | yes |
| 3 | 40–60 % on budget (provisional). | yes |
| 4 | 60–85 % on budget (provisional). | yes |
| 5 | 85 % or more of partner digital finance on budget and executed through the state's own systems on record — Goal 20's posture of a continent financing its development through its own institutions. | partly — Goal 20 states the posture; the 85 % line is the reference's |

### `infra.connect--mobile-penetration` — norm: DTS (top)

- **Value**: individuals aged 10 and over owning a mobile phone, per cent — ITU's definition (SDG 5.b.1), the series that exists for most of the continent. **Direction** higher. The UMC 2030 target is stated for people 15+; where a survey gives 15+, it goes in the qualifier.
- **Record**: a national household survey or census that cuts at 10+, over the ITU series; **reference** ITU DataHub mobile-phone ownership, SDG 5.b.1 (latest release; CC to record the year). A survey cut at 15+, SIM subscriptions per 100 and GSMA unique subscribers (total-population base) are different definitions and go in the qualifier only.
- **Band**: Africa quintiles for stages 1–4, with provisional cuts; stage 5 needs the DTS end state.
- **Method**: quintiles · higher
- **Cuts**: 50 · 65 · 80 · 95 — provisional for stages 2–4

| stage | anchor | interpolated |
|---|---|---|
| 1 | Bottom Africa quintile of mobile-phone ownership among people 10+; provisionally below 50 %. | yes |
| 2 | Second quintile; provisionally 50–65 %. | yes |
| 3 | Middle quintile; provisionally 65–80 %. | yes |
| 4 | Fourth or top quintile, short of the DTS end state; provisionally 80–95 %. | yes |
| 5 | The DTS end state — "all our people" with a mobile device — read as ownership of 95 % or more among people 10+. | no |

### `infra.connect--internet-usage` — norm: Agenda 2063 STYIP; DTS (target: 80 % by 2033)

- **Value**: individuals using the internet in the last three months, per cent of the population (SDG 17.8.1). **Direction** higher.
- **Record**: a national household survey over the ITU estimate; **reference** ITU DataHub / WDI IT.NET.USER.ZS (latest release; CC to record the year). The regulator's "internet subscriptions" are a different definition.
- **Band**: target, T = 80. The STYIP's figure is population reached at ≥ 6 Mb/s; the row reads it as use, the one form measured country by country (note for the review).
- **Method**: target · higher
- **Cuts**: 27 · 53 · 80 · 95

| stage | anchor | interpolated |
|---|---|---|
| 1 | Internet use below 27 % of the population. | yes |
| 2 | 27–53 %. | yes |
| 3 | 53–80 %. | yes |
| 4 | 80 % or more — the STYIP 2033 figure. | no |
| 5 | 95 % or more — the DTS 2030 end state of all people online wherever they live. | no |

### `infra.connect--mobile-affordability` — norm: DTS (target: no more than 1 US cent per MB — now a floor every country meets); Broadband Commission Target 2 / ITU UMC 2030 (2 % of monthly GNI per capita) as the banded line

- **Value**: the price of ITU's current data-only mobile broadband basket (5 GB since the 2025 edition: the cheapest 30-day plan of at least 5 GB from the operator with the largest market share) as a percentage of monthly GNI per capita, as ITU computes it. **Unit** per cent of monthly GNI per capita · **direction** lower. **Secondary**: the same basket's price per GB in US dollars, in the qualifier. A 2 GB basket figure from the 2021–24 editions is a different basket and goes in the qualifier.
- **Why the income share and not the DTS price**: on the 2025 basket, 52 of 53 countries are at US$10 per GB or less (CC, 2026-09-24) — prices have fallen well past a line set in 2020, so banding on it would put almost the whole continent on one stage. The share of income separates them (51 countries: quintile points about 1.6 · 4.1 · 6.1 · 9.4 %). The DTS line stays in the anchor as the continental floor that stages 4 and 5 must also meet.
- **Record**: the operator's or regulator's published tariff for a plan of at least 5 GB, dated, over GNI per capita from WDI; **reference** ITU ICT Price Baskets, 5 GB data-only, as a share of GNI per capita (latest release; CC to record the year).
- **Band**: target, T = 2 (the Broadband Commission's line, carried by the UMC 2030 targets), lower-is-better thirds as the preamble sets them. On the 2025 figures: 12 · 8 · 10 · 21 countries on stages 4 to 1 (CC, 2026-09-24).
- **Method**: target · lower
- **Cuts**: 6 · 4 · 2 · 1

| stage | anchor | interpolated |
|---|---|---|
| 1 | The basket costs more than 6 % of monthly GNI per capita — over three times the line. | yes |
| 2 | More than 4 % and at most 6 %. | yes |
| 3 | More than 2 % and at most 4 %. | yes |
| 4 | At most 2 % of monthly GNI per capita, with the DTS price line (US$10 per GB, 1 US cent per MB) also met. | partly — the DTS states the price floor; the 2 % line is the reference's |
| 5 | At most 1 % of monthly GNI per capita, with the DTS price line met. | yes |


### `infra.connect--international-internet-bandwidth` — norm: DTS (target: a minimum of two international connections)

- **Value**: number of international fibre routes in service — submarine cable landings, or terrestrial links to distinct neighbouring networks — with independence as the stage-4 condition and international bandwidth per internet user (kbit/s) as the secondary figure. **Independent** means no shared landing station and, for a landlocked state, not all through one transit country. **Unit** routes · **direction** higher.
- **Record**: the regulator's, the operator's or the consortium's statement of routes in service; **reference** TeleGeography and ITU DataHub for bandwidth per user (latest release; CC to record the year).
- **Band**: fixed on the count; stage 5 adds the Africa top quintile of bandwidth per user.
- **Method**: fixed · higher
- **Cuts**: 1 · 2 · 2 — stage 4 needs two of the routes independent; stage 5 adds the bandwidth-per-user quintile

| stage | anchor | interpolated |
|---|---|---|
| 1 | No international fibre route in service — satellite or microwave only — on a citation. | yes |
| 2 | One international fibre route in service. | yes |
| 3 | Two or more routes sharing a single point of failure (one landing station, or one transit country). | yes |
| 4 | Two or more independent international routes in service — the DTS minimum. | no |
| 5 | Two or more independent routes, and international bandwidth per internet user in the Africa top quintile. | yes |

### `infra.store--local-data-centre-capacity-all-providers` — norm: DTS; Smart Africa Data Center and Cloud Blueprint (target + rungs: Uptime Tier I–IV)

- **Value**: the number of multi-tenant data centres (colocation, carrier-neutral or hyperscale) in service at Tier III or above. **Unit** facilities · **direction** higher. **Tier** is Uptime Institute or TIA-942 certification, or the operator's own statement with the qualifier saying which. Installed IT capacity (MW per million population) moves to the stage-5 condition and the qualifier: it is blank for 434 of the 577 facilities in the Corpus dataset, so it could not be the banded value.
- **Record**: Corpus's own dataset, `outputs/datasets/data-centres/data-centres.csv` (`operational_status` Operational, `facility_type` Colocation/carrier-neutral or Hyperscale; Tier from `security_certifications`, or stated in `comments` and so marked), which covers all 54 countries — on 2026-09-24, 31 had at least one such facility and 22 had two or more. **Reference**: the Africa Data Centres Association and commercial directories, for the qualifier. Population, for the stage-5 condition: UN World Population Prospects.
- **Band**: the Blueprint's Tier rungs, counted; stage 5 adds the Africa top quintile of MW per million and the DTS hosting figure.
- **Method**: fixed · higher
- **Cuts**: 0 · 1 · 2 — stage 2 also needs a Tier I–II multi-tenant facility in service

| stage | anchor | interpolated |
|---|---|---|
| 1 | No commercial multi-tenant data centre in service, on a citation. | yes |
| 2 | Multi-tenant facilities in service, none at Tier III or above. | yes |
| 3 | One multi-tenant facility at Tier III or above in service. | no |
| 4 | Two or more at Tier III or above in service — two, so that one can fail; a single facility of any Tier is a single point of failure. | no |
| 5 | Stage 4's Tiers, capacity per million in the Africa top quintile, and a published figure that 30 % or more of the country's content or traffic is served from facilities in Africa — the DTS 2030 figure. | no |

### `infra.store--local-data-centre-capacity-national-providers` — norm: DPF §5.3.1 (top)

- **Value**: share of the in-country multi-tenant data centres in service (colocation, carrier-neutral or hyperscale) owned by nationally owned providers — the state, a state enterprise, a domestic company or a majority-domestic joint venture. **Unit** per cent of facilities · **direction** higher. By facilities, not MW, for the reason given on the all-providers row.
- **Record**: `outputs/datasets/data-centres/data-centres.csv` — `ownership_type` Government / SOE, Private domestic, Joint venture (majority domestic) or PPP counts as national; the dataset reads for 41 countries on 2026-09-24, so the quintiles can be cut at the baseline. No reference dataset exists.
- **Band**: Africa quintiles for stages 1–4, with provisional cuts; stage 5 needs the DPF condition. A share of 100 % from a single state facility reads stage 4 at most without the condition.
- **Method**: quintiles · higher
- **Cuts**: 0.1 · 25 · 50 — provisional

| stage | anchor | interpolated |
|---|---|---|
| 1 | No nationally owned multi-tenant facility in service, on a citation. | yes |
| 2 | Nationally owned providers hold less than 25 % of in-country multi-tenant facilities (provisional; bottom quintiles once cut). | yes |
| 3 | 25–50 % (provisional). | yes |
| 4 | 50 % or more (provisional), short of the DPF condition. | yes |
| 5 | The DPF end state: national providers hold capacity and the state's sensitive or classified data is hosted under national jurisdiction per a classification in force, on record. | no |

### `infra.energy--sufficient-energy-and-water-for-data-centres` — norm: Smart Africa Blueprint (top)

- **Value**: annualised power usage effectiveness (PUE) of the country's multi-tenant data centres, capacity-weighted where more than one publishes it, with water usage effectiveness (WUE) as the secondary figure. **Direction** lower. The Blueprint names PUE as the metric and dual grid feeds with backup as the supply condition; no document at any tier sets a threshold, so every cut below stage 5 is Corpus's.
- **Record**: operators' published PUE and WUE; **reference** ISO/IEC 30134-2 and 30134-9 for the definitions only.
- **Band**: provisional fixed cuts until fifteen countries hold a figure (the register expects that to take years); stage 5 needs the Blueprint's supply condition.
- **Method**: fixed · lower
- **Cuts**: 2.0 · 1.8 · 1.6 — provisional; stage 5 is the Blueprint condition

| stage | anchor | interpolated |
|---|---|---|
| 1 | PUE above 2.0, or data-centre load carried on diesel as the primary supply on record. | yes |
| 2 | PUE more than 1.8 and at most 2.0. | yes |
| 3 | PUE more than 1.6 and at most 1.8. | yes |
| 4 | PUE 1.6 or less. | yes |
| 5 | PUE 1.6 or less with dual grid feeds and backup generation in service and WUE published — the Blueprint's supply and efficiency conditions. | no |

### `infra.energy--grid-reliability` — norm: AfSEM plans and Continental Power System Master Plan (top)

- **Value**: power interruptions per month — SAIFI ÷ 12 where the regulator or utility publishes SAIFI, otherwise the number of outages in a typical month reported by firms. **Direction** lower.
- **Record**: the regulator's or utility's published SAIFI; **reference** World Bank Enterprise Surveys (survey year varies by country and prints as `value_year`).
- **Band**: Africa quintiles for stages 1–4, with provisional cuts (the Enterprise Surveys cover most of the continent, so the quintiles should cut at the baseline); stage 5 needs the AfSEM condition.
- **Method**: quintiles · lower
- **Cuts**: 10 · 5 · 2 — provisional

| stage | anchor | interpolated |
|---|---|---|
| 1 | Interruptions per month in the worst Africa quintile (the most); provisionally more than 10 a month. | yes |
| 2 | Second-worst quintile; provisionally more than 5 and at most 10. | yes |
| 3 | Middle quintile; provisionally more than 2 and at most 5. | yes |
| 4 | The two best quintiles, short of the AfSEM condition; provisionally 2 or fewer. | yes |
| 5 | Best quintile, with the national grid interconnected to its regional power pool and trading on record — the AfSEM end state of a reliable, interconnected supply. | no |

### `infra.energy--rural-electrification` — norm: Agenda 2063 STYIP; Mission 300 (target: 80 % of households by 2033)

- **Value**: rural population with access to electricity, per cent (SDG 7.1.1, rural). **Direction** higher.
- **Record**: a national household survey or census, or the rural-electrification agency's published figure, over the reference; **reference** Tracking SDG7 and WDI EG.ELC.ACCS.RU.ZS (latest release; CC to record the year).
- **Band**: target, T = 80. The STYIP's figure is national households; the row applies it to the rural population, which changes what is counted, not who set the bar (the rural-schools ruling).
- **Method**: target · higher
- **Cuts**: 27 · 53 · 80 · 95

| stage | anchor | interpolated |
|---|---|---|
| 1 | Rural electricity access below 27 %. | yes |
| 2 | 27–53 %. | yes |
| 3 | 53–80 %. | yes |
| 4 | 80 % or more — the STYIP 2033 figure. | no |
| 5 | 95 % or more — universal access (SDG 7.1). | yes |

### `dpi.id--registration-of-entire-population` — norm: DTS (target: 99.9 % with a digital legal identity by 2030)

- **Value**: persons holding a unique national identity number or credential, all ages, per cent of the population. **Direction** higher. The DTS counts "people in Africa", not adults, so a system that enrols only from age 16 caps its share near the adult share of the population; that is the DTS's point — legal identity from birth — and the qualifier says where the cap applies.
- **Record**: the identity authority's published count of unique persons enrolled (not cards printed), over the population from the statistics office or UN World Population Prospects; a count above the population is capped at 100 % and the qualifier says so. **Reference**: World Bank ID4D Global Dataset and Findex 2025 ID ownership (adults, a different base — qualifier only).
- **Band**: target, T = 99.9.
- **Method**: target · higher
- **Cuts**: 33 · 67 · 99.9 — stage 5 is the civil-registration condition

| stage | anchor | interpolated |
|---|---|---|
| 1 | Below 33 % of the population holding a unique identity number or credential. | yes |
| 2 | 33–67 %. | yes |
| 3 | 67–99.9 %. | yes |
| 4 | 99.9 % or more — the DTS 2030 figure. | no |
| 5 | 99.9 % or more, with the identity assigned through civil registration from birth — the DTS's "as part of a civil registration process". | no |

### `dpi.pay--population-uptake` — norm: World Bank Global Findex (global tier; target: reference values frozen at Findex 2025)

- **Value**: adults 15+ with an account at a financial institution or a mobile-money provider, per cent, with adults who made or received a digital payment in the past year as the secondary figure. **Direction** higher.
- **Record**: a national financial-inclusion survey (FinScope or the central bank's own demand-side survey) over Findex; a central bank's count of accounts is not a count of people and goes in the qualifier. **Reference**: Global Findex 2025 (2024 data), frozen as the vintage: global account ownership 79 %.
- **Band**: target, T = 79.
- **Method**: target · higher
- **Cuts**: 26 · 53 · 79 — stage 5 adds digital-payment use of 79 % or more

| stage | anchor | interpolated |
|---|---|---|
| 1 | Account ownership below 26 % of adults. | yes |
| 2 | 26–53 %. | yes |
| 3 | 53–79 %. | yes |
| 4 | 79 % or more — the global rate at the frozen Findex vintage. | no |
| 5 | Ownership 79 % or more, and 79 % or more of adults making or receiving a digital payment — use as well as access. | yes |

### `tech.industry--national-capacity-in-dt-related-production` — norm: DTS Digital Industry pillar; STISA-2034 (target)

- **Value**: ICT service exports (computer and telecommunications services, balance of payments) as a share of GDP, with ICT goods assembled or manufactured in the country (a plant in production, on record) as the stage-5 condition. **Unit** per cent of GDP · **direction** higher. ISIC J value added was the first draft's value; no reference carries it (the UN aggregates fold section J into *other activities*), so it would have read *No evidence* nearly everywhere. Exports read production capacity in the part of the sector that sells beyond its own economy, which is where the DTS pillar's software, hardware and outsourcing production shows. **Secondary**: ICT service exports as a share of service exports (WDI `BX.GSR.CCIS.ZS`), which reads the composition of service trade and runs high wherever other service exports are small, so it is not the banded value. ICT services in the balance of payments include telecommunications transit; where a cable-transit hub's figure is mostly transit, the qualifier says so.
- **Record**: the central bank's balance-of-payments publication, over the reference; **reference** WDI `BX.GSR.CCIS.CD` (ICT service exports, current US$, from UNCTAD and the IMF) over WDI GDP in current US$ (`reference/denominators.csv`). Read through the World Bank API on 2026-09-24: 49 of the 54 countries carry a figure, 39 of them for 2024 or 2025.
- **Band**: Africa quintiles for stages 1–4, with provisional cuts; stage 5 needs the DTS production condition. With 49 figures the quintiles cut at the baseline. The provisional cuts were tested on those figures: 13 · 14 · 11 · 11 countries on stages 1–4.
- **Method**: quintiles · higher
- **Cuts**: 0.05 · 0.2 · 0.5 — provisional

| stage | anchor | interpolated |
|---|---|---|
| 1 | ICT service exports in the bottom Africa quintile; provisionally below 0.05 % of GDP. | yes |
| 2 | Second quintile; provisionally 0.05–0.2 %. | yes |
| 3 | Middle quintile; provisionally 0.2–0.5 %. | yes |
| 4 | Fourth or top quintile, short of the DTS condition; provisionally 0.5 % or more. | yes |
| 5 | Top quintile, with ICT assembly or manufacturing in production in the country — the DTS pillar's "ICT assembling and manufacturing plants". | no |

### `capacity.literacy--digital-literacy-civil-service` — norm: Public Service Charter Art. 21; DPF (top)

- **Value**: civil servants who have completed a government digital-skills programme or certification, per cent of the civil service headcount. **Direction** higher.
- **Record**: the civil-service body's or digital agency's published completion figure over its published headcount; **reference** GTMI 2025 digital-skills indicators (categorical — qualifier only). Coverage will be thin, and most countries will read *No evidence* until the base holds a figure.
- **Band**: provisional fixed cuts at 0 · 10 · 40 until fifteen countries hold a figure, then Africa quintiles for stages 1–4; stage 5 needs the Charter condition.
- **Method**: quintiles · higher
- **Cuts**: 0.1 · 10 · 40 — provisional; stage 5 is the Charter condition

| stage | anchor | interpolated |
|---|---|---|
| 1 | No civil-service digital-skills programme in operation, on a citation (0 %). | yes |
| 2 | Less than 10 % of the civil service trained (provisional). | yes |
| 3 | 10–40 % (provisional). | yes |
| 4 | 40 % or more (provisional), short of the Charter condition. | yes |
| 5 | The Charter's Art. 21 end state: a systematic programme in force across the public service with results published, and 40 % or more trained. | no |

### `capacity.literacy--digital-literacy-general-population` — norm: DTS; Agenda 2063 STYIP (target: 80 % digitally proficient by 2033)

- **Value**: individuals aged 15+ with basic digital skills, per cent — SDG 4.4.1 on the ITU's 2025 method (at least one activity in each of five skill areas) — with intermediate skills as the secondary figure. **Direction** higher.
- **Record**: the statistics office's household survey module; **reference** ITU DataHub SDG 4.4.1 (few African countries report — CC to record which and the year).
- **Band**: target, T = 80. The STYIP's figure is primary completers with minimum proficiency; no country measures that cohort, so the row applies it to the adult population the ITU measures (note for the review).
- **Method**: target · higher
- **Cuts**: 27 · 53 · 80 — stage 5 adds intermediate skills above 50 %

| stage | anchor | interpolated |
|---|---|---|
| 1 | Basic digital skills below 27 % of people 15+. | yes |
| 2 | 27–53 %. | yes |
| 3 | 53–80 %. | yes |
| 4 | 80 % or more — the STYIP 2033 figure. | no |
| 5 | 80 % or more with basic skills, and more than 50 % with intermediate skills (ITU UMC 2030). | yes |

### `capacity.training--dt-related-training-in-secondary-education` — norm: AU Digital Education Strategy; CESA 26-35 (target: 50 % of institutions connected by 2027)

- **Value**: secondary schools with internet access for pedagogical purposes, per cent (SDG 4.a.1). **Direction** higher.
- **Record**: the education ministry's school census or EMIS; **reference** UIS SDG 4.a.1 (latest release; CC to record the year).
- **Band**: target, T = 50 (the DES's 2027 figure for all institutions, applied to secondary schools).
- **Method**: target · higher
- **Cuts**: 17 · 33 · 50 — stage 5 is the curriculum condition

| stage | anchor | interpolated |
|---|---|---|
| 1 | Below 17 % of secondary schools with internet for teaching. | yes |
| 2 | 17–33 %. | yes |
| 3 | 33–50 %. | yes |
| 4 | 50 % or more — the DES 2027 figure. | no |
| 5 | 50 % or more, with digital literacy or computing a compulsory part of the national secondary curriculum on record — the DES target that all students attain a minimum digital literacy. | no |

### `capacity.training--dt-related-university-facilities-and-qualifications` — norm: AU Digital Education Strategy; Agenda 2063 STYIP (target: 40 % of graduates in STEM by 2033)

- **Value**: tertiary graduates from STEM programmes (ISCED-F 05–07, ICT 06 included), per cent of all tertiary graduates, with the ICT share (ISCED-F 06) as the secondary figure. **Direction** higher.
- **Record**: the higher-education ministry's or statistics office's graduate statistics; **reference** UIS (latest release; CC to record the year).
- **Band**: target, T = 40.
- **Method**: target · higher
- **Cuts**: 13 · 27 · 40 — stage 5 is the NREN condition

| stage | anchor | interpolated |
|---|---|---|
| 1 | STEM graduates below 13 % of tertiary graduates. | yes |
| 2 | 13–27 %. | yes |
| 3 | 27–40 %. | yes |
| 4 | 40 % or more — the STYIP 2033 figure. | no |
| 5 | 40 % or more, with a national research and education network in service connecting the public universities — the DES target of NRENs in every country by 2027. | no |

### `capacity.training--graduates-entering-dt-ecosystem` — norm: Agenda 2063 STYIP; Continental TVET Strategy (target)

- **Value**: employment in information and communication (ISIC Rev. 4 section J), per cent of total employment. **Direction** higher. The STYIP's 40 %-STEM figure is the university row's; using it here would count one fact twice, so this row reads absorption into the sector instead.
- **Record**: the statistics office's labour force survey; **reference** ILOSTAT (latest release; CC to record the year).
- **Band**: Africa quintiles for stages 1–4, with provisional cuts; stage 5 needs the STYIP youth-employment figure.
- **Method**: quintiles · higher
- **Cuts**: 0.3 · 0.6 · 1.0 — provisional

| stage | anchor | interpolated |
|---|---|---|
| 1 | Information and communication employment in the bottom Africa quintile; provisionally below 0.3 % of total employment. | yes |
| 2 | Second quintile; provisionally 0.3–0.6 %. | yes |
| 3 | Middle quintile; provisionally 0.6–1.0 %. | yes |
| 4 | Fourth or top quintile, short of the STYIP figure; provisionally 1.0 % or more. | yes |
| 5 | Top quintile, with youth unemployment at or below 14 % on the labour force survey — the STYIP 2033 figure. | no |

### `include.access--gender-equity` — norm: Maputo Protocol Arts 12, 18, 19; DTS; African Digital Compact (top)

- **Value**: gender gap in internet use — (men's rate − women's rate) ÷ men's rate, per cent. **Direction** lower.
- **Record**: a national household survey with sex-disaggregated internet use; **reference** ITU sex-disaggregated series, with GSMA's Mobile Gender Gap (mobile internet, 2026) in the qualifier only — a different definition.
- **Band**: Africa quintiles for stages 1–4, with provisional cuts; stage 5 is parity.
- **Method**: quintiles · lower
- **Cuts**: 30 · 20 · 10 · 2 — provisional for stages 2–4

| stage | anchor | interpolated |
|---|---|---|
| 1 | Gender gap in internet use in the Africa quintile with the widest gaps; provisionally more than 30 %. | yes |
| 2 | Second-widest quintile; provisionally more than 20 % and at most 30 %. | yes |
| 3 | Middle quintile; provisionally more than 10 % and at most 20 %. | yes |
| 4 | The two narrowest quintiles, short of parity; provisionally more than 2 % and at most 10 %. | yes |
| 5 | Parity — a gap of 2 % or less — on a survey figure: women's access to and use of information technologies on equal terms (Maputo Art. 18(2)(b)). | no |

### `include.divides--bridging-of-digital-divides` — norm: DTS; ACHPR Principle 37; African Digital Compact (target)

- **Value**: rural internet use as a ratio of urban internet use (rural rate ÷ urban rate). **Direction** higher.
- **Record**: a national household survey with urban and rural internet use; **reference** ITU urban/rural series (latest release; CC to record the year).
- **Band**: fixed; stage 5 is the DTS end state of access "wherever they live".
- **Method**: fixed · higher
- **Cuts**: 0.25 · 0.5 · 0.8 · 0.98

| stage | anchor | interpolated |
|---|---|---|
| 1 | Rural internet use below a quarter of the urban rate (ratio below 0.25). | yes |
| 2 | Ratio 0.25–0.5. | yes |
| 3 | Ratio 0.5–0.8. | yes |
| 4 | Ratio 0.8–0.98. | yes |
| 5 | Ratio 0.98 or more — the DTS end state of access for all people wherever they live in the continent. | no |

## Measures — notes for CC's review

**Datasets for CC to confirm (the C3 task's own check).** Each specification names its reference and says *CC to record the year* where the latest vintage was not read in this session. Confirmed on 2026-09-22–23 by the research passes and not repeated here: Global Findex 2025 (2024 data), GSMA Mobile Gender Gap 2026, the ITU UMC 2030 targets, the Broadband Commission targets, the DES and STYIP figures. To reach and date: ITU DataHub (ownership, use, SDG 4.4.1, urban/rural and sex splits, bandwidth), ITU ICT Price Baskets, Tracking SDG7 / WDI rural access, World Bank Enterprise Surveys, UIS (4.a.1, graduates by field), ILOSTAT (employment by activity), UN National Accounts and UNCTADstat, WDI GDP, UN WPP, ID4D. None of the three Corpus compiles needs checking beyond the code that computes it.

**Three readings the draft makes that Bill or CC should see:**

- **Norm figures applied to a neighbouring population.** `internet-usage` reads the STYIP's *population at ≥ 6 Mb/s* as use; `rural-electrification` reads its national-households figure against the rural population; `general-population` literacy reads its *primary completers* figure against adults 15+; secondary training reads the DES's all-institutions figure against secondary schools. Each follows the rural-schools ruling — the norm set the bar, the row chooses what is counted — and each says so in its specification.
- **`finance.new--development-partner-project-financing` is redefined.** The register anchors it on Goal 20's *aid ≤ 25 % of the 2013 level*, an inverse of the external share of the budget — which is 100 % minus the sustainability share and would count one fact twice. The draft reads the on-budget share of partner digital finance instead (partner money running through the state's own budget), with stage 5 `partly`. **Bill ruled on 2026-09-24: keep the on-budget share** (`maturity-assessment.md` §2). The 85 % line at stage 5 is the Paris Declaration's indicator 3 target as carried by GPEDC — not verified against the text in this session.
- **Two measures read absorption, not the norm's headline, to avoid double counting**: `graduates-entering-dt-ecosystem` (ICT-sector employment; the 40 %-STEM figure stays with the university row) and `mobilisation-of-non-state-finance` (private beneficiaries only; public-sector beneficiaries are the partner row's). Neither is a register change; both keep the register's anchors for stage 5.

**Rows CC may want to read first:**

- **`sufficient-energy-and-water-for-data-centres`** is the weakest measure: the Blueprint names PUE, which measures efficiency rather than sufficiency, and no document at any tier sets a threshold, so stages 1–4 are Corpus's cuts on an operator-published figure few operators publish. It will read *No evidence* almost everywhere. If Bill would rather it were a system (supply in service on dual feeds, backup, water source on record), that is a kind change for the frame, not a rubric edit.
- **`mobile-penetration`** holds to ITU's definition, ownership among people 10+ (item 6), so a survey cut at 15+, SIM counts and GSMA's total-population unique-subscriber rate go in the qualifier. CC's banding of the fetched series puts 52 countries on the row.
- **`tech.industry`** bands ICT service exports as a share of GDP after CC's item 8 (below); the DTS production condition stays at stage 5.
- **`registration-of-entire-population`** puts stage 4 at the DTS's 99.9 % of all people, so almost every country will sit at 2 or 3 and systems that enrol only adults are capped near the adult share. That is the truthful reading of the DTS's "from birth", and the qualifier says where the cap applies.

**A checker extension for CC's consideration.** `lint-maturity-rubric.py` checks the four rubric columns; the specifications here want their own lookup (`lookups/maturity-measures.csv`) and, with it, checks that every measure has a value, unit, direction, record rule and band method, that a `target` row's cuts derive from its T, and that a `quintiles` row names its provisional cuts where fewer than fifteen countries hold a figure.

## Measures — changes made on CC's first review (2026-09-24)

`maturity-rubric-review.md` returned the leg with five items; all five are in the file above, with one extension of item 3 that CC should read.

- **1** — every specification carries `Method` (band method · direction) and `Cuts` (lower bounds of stages 2–5 for *higher*, upper bounds for *lower*; the stage-5 number left out where stage 5 is a condition; `provisional` marked). The preamble defines both lines, the upper-inclusive boundary for lower-is-better measures, and the band as a ceiling.
- **2** — provisional cuts on every quintile row: `mobile-penetration` 50 · 65 · 80 · 95, `grid-reliability` 10 · 5 · 2, `tech.industry` 1.5 · 3 · 5, `graduates-entering-dt-ecosystem` 0.3 · 0.6 · 1.0, `gender-equity` 30 · 20 · 10 · 2, `mobilisation-of-non-state-finance` 0.001 · 0.02 · 0.1 · 0.25. **Most were set without a distribution in the repo** (no GDP, employment or survey series is held), so the preamble adds a guard: a cut that puts more than half the continent on one stage is revised before the baseline is cut, not after. The anchors state the provisional band beside the quintile.
- **3** — `local-data-centre-capacity-all-providers` bands the count of multi-tenant facilities at Tier III or above (unit *facilities*), Tier I–II only is stage 2, and MW per million is the stage-5 condition and the qualifier. **The record is Corpus's own `outputs/datasets/data-centres/data-centres.csv`**, which covers all 54 countries and holds Tier in `security_certifications` (or as the operator's statement in `comments`); on 2026-09-24 it gave 31 countries at least one such facility and 22 two or more. It leaves `it_capacity_mw` blank for 434 of 577 facilities, which confirms MW could not be the banded value.
- **3, extended** — `local-data-centre-capacity-national-providers` had the same fault (share of MW) and now bands the share of multi-tenant facilities nationally owned, from the same dataset's `ownership_type`; it reads for 41 countries, so its quintiles cut at the baseline. A 100 % share from a single state facility reads stage 4 at most without the DPF condition.
- **4** — `mobilisation-of-non-state-finance` sums commitments whose `start_year` is the as-at year or either of the two before and divides by three; both finance rows say that NGO, Multilateral, Research and Multi-stakeholder beneficiaries count in neither. A further rule the data forced: more than half the units have no private digital commitment starting in 2024–26, so **zero is stage 1 and the quintiles are cut over the non-zero figures**.
- **5** — the preamble lists the four forms `value_source` takes, the compile form naming the data-centres dataset alongside the finance compile.
- **Also**: `international-internet-bandwidth` now counts routes in service, with independence as the stage-4 condition (as drafted it counted only independent routes and could not separate stage 2 from stage 3); `sufficient-energy-and-water` states its bands in the upper-inclusive form; the partner row records Bill's ruling.

## Measures — items 6–8 (2026-09-24)

Appended to CC's first review after the second began; all three are in the file above, for CC to re-cut before the baseline.

- **6** — `mobile-penetration` reads ITU's definition, ownership among people 10+ (SDG 5.b.1), in the value, the record, stage 1 and stage 5; a survey cut at 15+ goes to the qualifier with the other definitions. Cuts unchanged; CC's banding of the fetched 10+ series (8 · 13 · 16 · 12 · 3 over 52) already fits them.
- **7** — `mobile-affordability` reads price per GB of ITU's current 5 GB data-only basket; a 2 GB figure from 2021–24 goes to the qualifier. The DTS line is unchanged. Stage 5's 2 %-of-GNI test is now applied to the larger basket, which is stricter than the test the Broadband Commission set on 2 GB, and the anchor says so.
- **8** — `tech.industry` is re-pointed at a figure that exists, as CC recommended, but banded as **ICT service exports as a share of GDP** rather than of service exports. The share of GDP reads the scale of the exporting sector against the economy, which is what production capacity asks. The share of service exports reads the composition of service trade and runs high wherever tourism or transport exports are small, so it rides as the secondary figure. Tested on WDI `BX.GSR.CCIS.CD` read through the World Bank API on 2026-09-24 over `reference/denominators.csv` GDP: 49 countries, quintile points at about 0.03 · 0.09 · 0.36 · 0.64 %, and the provisional cuts 0.05 · 0.2 · 0.5 give 13 · 14 · 11 · 11. The top of the list includes a cable-transit hub (Djibouti), which is why the specification sends transit-dominated figures to the qualifier. **For CC**: `reference/measures.csv` wants the series added in C5, and the register's reference column for this indicator (UNIDO CIP; UNCTAD Digital Economy Report) should name `BX.GSR.CCIS.CD`.

## Measures — items 9–10 (2026-09-24)

- **9** — `mobile-affordability` bands the 5 GB basket as a share of monthly GNI per capita, T = 2, lower-is-better thirds (stage 3 at or below 4 %, stage 2 at or below 6 %), as CC recommended; US$ per GB goes to the qualifier. **Stage 5 is 1 % or less** (three countries on the 2025 figures): no norm states a rung beyond the 2 % line, so it is Corpus's, marked `yes`, and set at half the line so that it names a clear margin rather than a tie. **Stage 4 is `partly`**: the 2 % line is the register's reference, not its norm, and by the first review's rule a reference does not make a rung the norm's; what the DTS still states is the price floor, which stages 4 and 5 must also meet and every country now does. **For CC**: the register row's *fixes* and *reference* should say the same — the DTS line as a floor met by all, the 2 % line as the banded reference — so the norms lookup and the rubric agree.
- **10** — `local-data-centre-capacity-all-providers`: the Tier IV clause is gone from the cuts and from stage 4. Stage 4 asks for two facilities at Tier III or above because two give redundancy; a lone Tier IV reads stage 3, which is where the band already holds Seychelles.
