---
type: task
reader: cc
title: maturity-study-police.md — the fourth maturity study: rural police stations, as station records
last_reviewed: 2026-10-10
status: CC's proposal, run unamended on Bill's word of 2026-10-10; step 3 under way
---

# Maturity study: police — station records

*(Commissioned by Bill on 2026-10-10, under `maturity/documentation/maturity-study-method.md`. Lines marked (Bill) are his; the rest is CC's proposal, modelled on the registry study. Trigger: "**run maturity study police**".)*

## 1. The question, and the row it redraws

**Does the police station make a digital record of a report or a case, when it takes it?** `digital.rural--digitalisation-of-rural-police-stations` has no settled subject. Its 43 staged cells hold fingerprint systems, surveillance centres, border posts, reporting portals, radios, computers and training as one thing; 34 sit at stage 2.

**One sub-indicator replaces the row**:

| Sub-indicator | Indicator text | Id |
|---|---|---|
| Station records | Digitalisation of rural police stations: station records | `digital.rural--digitalisation-of-rural-police-stations-station-records` |

The id enters `lookups/indicators.csv` at acceptance. **`dpi.mis--justice` is not redrawn**: it stages the courts' case management, and its evidence is logged in `exchange.csv`.

## 2. Typology

| Class | What it is | Treatment |
|---|---|---|
| `record` | The force's system, in which **the station that takes a report or opens a case makes the digital record of it**: the occurrence book, the complaints register, the case file | Assessed |
| `statistics` | Crime counts compiled from stations' periodic returns, and the system that collects them | Noted, not assessed |
| `identification` | Fingerprint systems, criminal records, wanted and stolen-property files, forensic laboratories | Noted, not assessed |
| `single-function` | One function only: traffic fines and licences, one class of offence, the custody register, firearms, lost documents | Noted, not assessed |
| `public` | A portal, app or number through which the public reports, pays or asks for a certificate | Noted, not assessed |
| `surveillance` | Cameras, command and dispatch centres, integrated security centres, radar | Noted, not assessed |
| `personnel` | The force's own staff: payroll, biometric enrolment of officers, deployment | Noted, not assessed |
| `enabling` | Connectivity, computers, radios, power, premises, computer training | Noted, not assessed |
| `border` | Immigration and border-control systems, at a border post or elsewhere; customs | Out of scope |
| `exchange` | Links from the police system to prosecution, courts, prisons, the national identity system or another country's police | Logged for `dpi.mis--justice` |

**The test: is the report or the case entered as a digital record at the station, when it is taken?** A monthly count is `statistics`. A paper form keyed at headquarters as routine, for each new case, is `record`, `keyed-elsewhere`. A statement typed on a computer and printed for the file is paper.

**Classified by what the source says the system does**; a name alone is unclassified. The West African police information system is `record` only where a source says stations enter their cases in it.

**Stations.** A station is any local unit of a national force that takes reports from the public: stations, posts, *commissariats*, gendarmerie brigades, *esquadras*. **The gendarmerie counts**: in much of the continent it is the rural police. Out: municipal police, chiefs, customs, immigration and the military. The denominator is the force's own count of its stations.

**Records.** O the occurrence or complaint as first recorded; C the case file that follows it.

**One flag that never changes the stage.** *Justice linked*: the case file passes digitally to the prosecutor or the court.

## 3. Aspects

| # | Aspect | Role | Values |
|---|---|---|---|
| 1 | Governance, planning, finance | qualifier | Owner: the force or its ministry, partner or vendor. Plan: a current strategy or costed plan naming the system, or none. Finance: domestic budget line, donor only, or not stated |
| 2 | Records made digitally | coverage | O, C, or none |
| 3 | How the record is made | coverage | `connected`: at the station, when the report is taken, and held in the national system, online or by synchronising. `local`: at the station, in a system that stays in the station. `keyed-elsewhere`: at headquarters or a regional command, from the station's paper forms, as routine. `paper` |
| 4 | Last twelve months | qualifier | Advancing, no change on record, or regressing, with the dated event |
| 5 | Stations doing the digital entry | coverage | Share of stations, with numerator, denominator, year and who says so; else `equipped`, a share given or connected to the system; else a count; else *not published* |

**Aspects 2, 3 and 5 set the stage; 1 and 4 cap or flag it and never raise it. The cap rule and aspect 4 are the health study's, unchanged** (its §3): without the force or its ministry as owner and a domestic budget line or current plan, stage 4 or 5 is capped at 3 and flagged *externally run*.

**Rural.** The stage reads stations nationally. Where a dated source says rural stations are outside the system, or that the force policing the countryside is, the cell is flagged *rural gap* and the short summary gives the figure.

**Two forces.** Where police and gendarmerie keep separate systems, the cell is staged on the force with more stations, and the long summary states the other. The short summary names the force its figure counts.

## 4. The ladder

A draft, tested and fixed at P3.

**Station records**

| Stage | Records | How the record is made | Stations |
|---|---|---|---|
| 1 Absent | A dated statement that stations record on paper only | | |
| 2 Preparing | A system for stations is being prepared or piloted; or one runs at headquarters or in the capital only | Any, or not stated | Pilot stations, or none |
| 3 Establishing | O or C: past its pilot and live in some stations outside the capital | `connected`, `local` or `keyed-elsewhere` | A minority, a count with no total, or not published |
| 4 Operating | O or C | `connected` | More than half, on a share or a count with a denominator |
| 5 Leading | O and C | `connected` | 90 per cent or more, on a figure published within two years that gives the rural share |

**Pilot or live, and preparation, are read as the schools study reads them** (its §4).

**A noted class never places a country above stage 1.** A country holding only noted classes is unplaced, or stage 1 where a source states that stations record on paper; what it holds prints under *Noted, not assessed*.

**A share of districts with a digital station is read as the share of stations.** A share of stations *equipped*, *connected*, *computerised* or *digitised* is not a share recording: it is `equipped` and places at stage 3 only where a `record` system is live. *All stations*, said by the force beside a count of stations, is 100 per cent.

**The registry study's R3 fixes hold** (its §4): `connected` is read from the fact's words, and a law places nothing. A digital record with neither O nor C named is read as O.

## 5. The norm

The frame's anchor (`lookups/maturity-norms.csv`) is Corpus-defined: the AFRIPOL Statute of 2017 connects national police agencies and says nothing below the national level, and the lookup's search found no AU instrument on local stations.

**No norm measures what the sub-indicator measures.** The ladder borrows nothing; the 90 per cent line is the health study's. **Owed a reading at P3**: the African Commission's guidelines on arrest and police custody, for what they require of a station's registers. *From the lookup.*

## 6. What the review reads and the search asks for

- **Subjects and term list**: in `study.json`.
- **Source types for the briefs**, ranked: the force's annual reports, standing orders and strategic plans; budget performance reports and parliamentary answers; audit reports; UNDP, UNODC, INTERPOL, European Union and World Bank project documents and evaluations; vendor case studies, for what the system does only; dated news of a rollout, an outage or a withdrawal, for aspect 4.

## 7. Tasks, in order

- [x] **P1. Bill's rulings**: the five proposals stand, 2026-10-10.
- [ ] **P2. Review all 54 countries**, method §4.
- [ ] **P3. Test and fix the ladder** on the profiles; read the norm's texts.
- [ ] **P4. Search and hand over**, method §5.
- [ ] **P5. Re-read and stage**, method §6 and §7.
- [ ] **P6. Write, render and lint**, method §8.
- [ ] **P7. Report to Bill.** Acceptance is his.

**The rulings of P1**, CC's proposals, which Bill ran without amendment:

1. **Station records only**: the occurrence book and the case file. The rest is noted.
2. **Only the rural row is redrawn**; `dpi.mis--justice` stands.
3. **The gendarmerie counts as police**; chiefs and municipal police do not.
4. **Stage 5 needs both records**; stages 3 and 4 need either.
5. **Crime statistics place nothing**; routine keying of each case at headquarters reaches stage 3.

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
