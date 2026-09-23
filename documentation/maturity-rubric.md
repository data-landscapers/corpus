---
type: reference
title: maturity-rubric.md — the five-stage anchors per indicator, drafted chapter by chapter for lookups/maturity-rubric.csv
last_reviewed: 2026-09-23
status: task C2 in progress — Governance (29) and the Finance instrument drafted 2026-09-23; CC's first review (maturity-rubric-review.md) acted on the same day, all ten items; awaiting CC's second review and cut; nothing cut to lookups/
---

# The rubric

*(Task C2 of `maturity-assessment-tasks.md`: Cowork drafts one chapter and stops; CC reviews it against `indicator-mapping-conventions.md`, the generic scale in `maturity-assessment.md` §3 and the two worked rubrics in the indicator documents, and either cuts it to `lookups/maturity-rubric.csv` or sends it back. The order is instruments first, so this file opens with Governance and the one Finance instrument; systems follow, measures last (task C3, where each also needs its value definition and band). `maturity-assessment-norms.md` is the source of every norm named below and is not restated here beyond the short name.)*

## How to read an anchor

**An anchor is evidence a mapped row can satisfy.** Each stage names what the base has to hold — an instrument published, a body constituted, a decision taken, a figure cited — not a quality the assessor feels. The stage is the highest whose anchor's positive conditions are all met. Clauses saying what is still missing — *with no plan on record*, *regulations pending* — describe the typical case at that stage and are not conditions; a country with part of the next stage stays at this one, and the qualifier names what it has.

**"Aligned with" a continental instrument** means the national instrument says so, or the AU or a REC records the country as compliant; an assessor's own comparison is not alignment.

**Stage 1 needs a citation.** *Absent* is a dated statement that the thing does not exist — a tracker, a ministry's own admission, a *Not held* row with a source. Silence is *No evidence* (unassessed), never stage 1.

**The instrument ladder, applied everywhere below** unless a row says otherwise: 1 *Absent* — nothing of the kind, cited · 2 *Nascent* — drafted, tabled, announced, under consultation, or an expired instrument with a successor in preparation · 3 *Established* — adopted or enacted and published, but not yet operating: commencement, regulations, a body or a budget still pending, or in force in a limited form · 4 *Operating* — in force with the machinery to give it effect: implementing regulations or a plan, a body with a mandate and a budget, and at least one act of implementation on record (an enforcement decision, a progress report, a funded action) · 5 *Leading* — the continental instrument's own end state: aligned with or ratifying it, reviewed or reported against, and sustained.

**Vocabulary used in the anchors.** *Adopted*: approved by cabinet, council of ministers or the competent authority and published. *Enacted*: passed and promulgated. *In force*: commenced, with the commencement date passed. *Constituted*: members appointed and a first act on record. *On record*: cited in a mapped row. *In the window*: dated inside the snapshot's window, for a stage to change (`maturity-assessment.md` §6).

**`interpolated`** is `no` where the anchoring norm itself states the rung (the register's *fixes* column: a *rungs* row states several; a *top* row states only stage 5) and `yes` where the rung is Corpus's reading of the ladder between absence and the norm's end state. A reference that informs a rung does not make it the norm's: a rung drawn from ID4D, a REC model law, the Broadband Commission or ISO membership classes stays `yes`.

**What is never evidence for a higher stage:** the announcement of an instrument (that is stage 2); a foreign partner's programme to draft one; a global index score (a reference, not the record — `maturity-assessment-norms.md` §7); a strategy that names the thing among its actions without an instrument of its own.

---

## Governance — drafted 2026-09-23, awaiting CC review

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
| 4 | The policy in force with an open licence, a portal publishing datasets under it, an obligation on public bodies to publish, and a custodian; publication activity in the window on record. | yes |
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

## Finance — the instrument, drafted 2026-09-23, awaiting CC review

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

## Changes made on CC's first review (2026-09-23)

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
