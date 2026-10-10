---
type: task
reader: cc
title: maturity-study-registry.md — the third maturity study: rural registry offices, as civil registration
last_reviewed: 2026-10-10
status: CC's proposal of 2026-10-10, for Bill's rulings; not yet run
---

# Maturity study: registry — civil registration

*(Commissioned by Bill on 2026-10-10, the third study under `maturity/documentation/maturity-study-method.md`. Lines marked (Bill) are his; the rest is CC's proposal, modelled on `maturity/schools/maturity-study-schools.md`. Study id `registry`. Triggers: "**run maturity study registry**", then "**run maturity study registry phase 2**".)*

## 1. The question, and the rows it redraws

**Does the local civil registration office enter a birth or a death digitally, when it is declared?** Two frame rows ask near it. `digital.rural--digitalisation-of-rural-registry-offices` has no settled subject: its 54 cells hold civil registration, identity-card enrolment, land and deeds offices, mobile drives and the scanning of old registers, staged as one thing. `dpi.registry--civil-register` stages a central digital register, which a country reaches by keying or scanning paper its offices still write.

**A scanned register is an archive, and an identity drive is a campaign. Neither is an office registering digitally, and the study must not read either as one.**

**One sub-indicator replaces both rows**:

| Sub-indicator | Indicator text | Id |
|---|---|---|
| Civil registration | Digitalisation of rural registry offices: civil registration | `digital.rural--digitalisation-of-rural-registry-offices-civil-registration` |

The id enters `lookups/indicators.csv` only at acceptance, when both old rows are retired. **Identity enrolment and land registration get no ladder here**: `dpi.id` and `dpi.registry--land-register` hold them.

`dpi.id--interoperability-of-birth-registration-and-digital-id` is not redrawn. Its evidence is logged in `maturity/registry/exchange.csv`.

## 2. Typology

| Class | What it is | Treatment |
|---|---|---|
| `civil` | The civil registrar's system, in which **the office where a birth or death is declared makes the digital record of it** | Assessed |
| `archive` | Scanning, indexing or keying of registers already written: back-capture of past years | Noted, not assessed |
| `notification` | A health facility, a chief or a community agent tells the registrar of an event, by app, SMS or form, and the registrar registers it elsewhere | Noted, not assessed |
| `certificate` | A portal or counter for requesting, paying for or verifying a copy of an act | Noted, not assessed |
| `outreach` | Mobile teams, registration drives, mobile court hearings for late registration | Noted, not assessed |
| `identity` | National identity and population-register enrolment, cards, biometrics | Noted, not assessed |
| `land` | Land, deeds and cadastre offices; business and electoral registers | Out of scope |
| `enabling` | Connectivity, devices, power, premises | Noted, not assessed |
| `exchange` | Links from the civil register to the identity system, health or statistics | Logged for `dpi.id` |

**The test that separates `civil` from the rest: is the event entered as a digital record where and when it is registered?** A register written by hand and digitised afterwards by a project is `archive`. A paper register keyed elsewhere as routine, for each new event, is `civil` kept `keyed-elsewhere`.

**Classified by what the source says the system does, never by name.** A source that gives only the name is unclassified, a gap for the search.

**A registrar's desk in a maternity is a registry office** where the source says the birth is registered there; where the facility only notifies, it is `notification`. A mobile team is `outreach` even when it registers on a tablet: it is not an office.

**Offices.** A local office is any office below the national one that registers events: commune, sub-prefecture and secondary centres, district and sub-county registrars, *conservatórias*, civil-status bureaux. The denominator is the country's own count of them; its names are mapped in `systems.csv`. Consulates are out.

**Events.** B births, D deaths. Marriages and divorces are noted.

## 3. Aspects

| # | Aspect | Role | Values |
|---|---|---|---|
| 1 | Governance, planning, finance | qualifier | Owner: ministry or agency, partner or vendor. Plan: a current strategy or costed plan naming the system, or none. Finance: domestic budget line, donor only, or not stated |
| 2 | Events registered digitally | coverage | B, D, or none |
| 3 | How the record is made | coverage | `connected`: at the office, at registration, and held in the national register, online or by synchronising. `local`: at the office, in a system that stays in the office. `keyed-elsewhere`: at a higher level, from the office's paper register, as routine. `paper` |
| 4 | Last twelve months | qualifier | Advancing, no change on record, or regressing, with the dated event |
| 5 | Local offices doing the digital entry | coverage | Share of local offices, with numerator, denominator, year and who says so; else a count; else *not published* |

**Aspects 2, 3 and 5 set the stage; 1 and 4 cap or flag it and never raise it. The cap rule and aspect 4 are the health study's, unchanged** (its §3): without the registrar's ministry or agency as owner and a domestic budget line or current plan, stage 4 or 5 is capped at 3 and flagged *externally run*.

**Rural.** The stage reads local offices nationally. Where a dated source says rural offices are outside the system, or register less, the cell is flagged *rural gap* and the short summary gives the figure.

## 4. The ladder

A draft, tested and fixed at R3.

**Civil registration**

| Stage | Events | How the record is made | Local offices |
|---|---|---|---|
| 1 Absent | A dated statement that local offices register on paper only | | |
| 2 Preparing | A system for local offices is being prepared or piloted; or one runs at the national office or in the capital only | Any, or not stated | Pilot offices, or none |
| 3 Establishing | B: past its pilot and live in some local offices | `connected`, `local` or `keyed-elsewhere` | A minority, a count with no total, or not published |
| 4 Operating | B and D | `connected` | More than half, on a share or a count with a denominator |
| 5 Leading | B and D | `connected` | 90 per cent or more, on a figure published within two years that gives the rural share |

**Pilot or live is the source's word**, and **preparation is the health study's** (§4), both as the schools study applies them.

**An archive never places a country above stage 1.** A country holding only noted classes is unplaced, or stage 1 where a source states that offices register on paper; what it holds prints under *Noted, not assessed*.

**A share of communes or districts with a digital office is read as the share of offices**; the short summary says which. A share of offices *equipped* or *connected* is not a share registering: it places by the lower rung. A share of births registered is not a share of offices, and places nothing.

## 5. The norm

The frame's anchor (`lookups/maturity-norms.csv`): the AU Digital Transformation Strategy's 99.9 per cent legal identity by 2030, and the 100 per cent of births and 80 per cent of deaths of SDG 17.19.2(b) that the APAI-CRVS papers restate.

**It does not measure what the sub-indicator measures.** It counts people and events registered, which a paper office meets. No norm addresses how a local office registers. The ladder borrows nothing from it; the 90 per cent line is the health study's. *Read from the texts at R3; this paragraph is from the lookup.*

## 6. What Phase 1 reads and searches for

- **Subjects**: `digital.rural`, `dpi.registry`, `dpi.id`.
- **Term list**: in `study.json`. Archive and notification terms are in it on purpose.
- **Source types for the briefs**, ranked: the registrar's annual reports, manuals and circulars, which say which offices enter what; CRVS strategies, comprehensive assessments and costed plans; World Bank, UNICEF, UNDP and UNFPA appraisal and implementation reports; UNECA and APAI-CRVS country papers; the civil registration law and its decrees, for what the electronic record is in law; dated news of a rollout, an outage or a withdrawal, for aspect 4.

## 7. Tasks, in order

- [ ] **R1. Bill's rulings**, below.
- [ ] **R2. Review all 54 countries in one run**, method §4.
- [ ] **R3. Test and fix the ladder** on the profiles; read the norm's texts.
- [ ] **R4. Search, select and hand over**, method §5.
- [ ] **R5. Phase 2**, on Bill's trigger, method §6 and §7.
- [ ] **R6. Write, render and lint**, method §8.
- [ ] **R7. Report to Bill.** Acceptance is his.

**For Bill's rulings at R1**, each with CC's proposal taken unless he says otherwise:

1. **Civil registration only.** Identity enrolment and land offices are noted or out.
2. **Both rows redrawn**, `dpi.registry--civil-register` with the rural row.
3. **Scanning old registers places nothing**; routine keying of new events elsewhere reaches stage 3.
4. **Stage 4 needs deaths as well as births**, and the record in the national register.
5. **A maternity desk is an office; a mobile team is not.**

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
