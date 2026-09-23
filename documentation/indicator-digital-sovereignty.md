---
type: task
title: indicator-digital-sovereignty.md — add a digital sovereignty indicator to the Geopolitics chapter
last_reviewed: 2026-09-22
status: planned, for CC to carry out per adding-an-indicator.md; blocked on OSINT adding the geopol.sovereignty subject (§1)
---

# Digital sovereignty — a new indicator in place of the five `geopol.*` rows

*(Written 2026-09-22 in Cowork on Bill's ruling that the five `geopol.*` indicators — MoUs, engagements and commitments with the US and hyperscalers, China, the EU, the Gulf and India — do not reflect maturity and leave the assessment, and that what the Geopolitics chapter needs in their place is a digital sovereignty indicator. This answers `adding-an-indicator.md` §§0–10 for that one indicator. The five retired rows stay in the frame with `assessed = 0`; their 260 mapped rows across the 54 countries are this indicator's first evidence.)*

## 0. The question

**How far does the state control its own digital estate — where its data sits and under whose jurisdiction, who can operate and change its core systems, and on what terms it has bound itself to external providers and powers?**

That is one question with three parts, and one ladder holds because the parts move together: a state that hosts its registers abroad under a foreign provider's terms, cannot maintain its ID system without the vendor, and has signed hyperscaler and bilateral agreements with no exit, portability or jurisdiction clauses is at the bottom on all three; a state with a data classification in force, its core systems maintainable nationally and its agreements systematically conditioned is at the top on all three. Where they diverge, the rubric says which part decides (§5).

It is not a localisation indicator. The AU Data Policy Framework separates sovereignty from localisation and recommends localisation only for categories of data; the AfCFTA Digital Trade Protocol forbids forced location of computing facilities subject to public-policy exceptions. The top of this ladder is *control with portability*, and a wall of localisation requirements with no portability, no interoperability and no national capacity to run what is walled in is stage 2, not stage 5.

It is not the five it replaces. Those recorded *what was signed with whom*; this records *what the state has kept for itself* — and a signed memorandum is evidence for it only through its terms.

## 1. The subject — `geopol.sovereignty`, which does not exist yet

The Geopolitics chapter's five subjects are each an external actor. None can carry a sovereignty indicator without misfiling it under one power. So the indicator needs a sixth subject, **`geopol.sovereignty` — Digital sovereignty**, sort order 39 after `geopol.india`, and that is an OSINT change: the taxonomy is OSINT's vocabulary.

**Step 1 is therefore a patch to OSINT**, cut per Corpus's `CLAUDE.md`: `scripts/osint-patch.py prepare`, add the slug to `lookups/taxonomy.md` in the clone, `cut`, deliver to `prepared/` on the share with the base commit named, and an `[ACT]` note in `notes-for-osint.md` asks OSINT to apply it and mint the concept page, `Affects: lookups/indicators.csv, the maturity assessment's Geopolitics chapter`. `finance.sustain` travels in the same patch (`indicator-financial-sustainability.md` §1). Nothing below is minted until the mirror shows the subject.

Sources tagged `geopol.usa` and the rest keep their tags; a source is tagged `geopol.sovereignty` when sovereignty is what it reports (a hosting decision, a data classification, a contract term), which is a sweep and ingest matter for OSINT and a sweep brief on Bill's call.

## 2. The id

`geopol.sovereignty--digital-sovereignty`. Display text *Digital sovereignty*. No collision in `indicators_lib.ids()`.

## 3. The frame row

`geopol.sovereignty--digital-sovereignty, 40, 1, Geopolitics, Digital sovereignty, geopol.sovereignty, Digital sovereignty, instrument, 1` — `Topic Sort` 40, last in the Geopolitics chapter *(minted 2026-09-23, task B3)*. The five `geopol.*` rows get `assessed = 0` in the same edit.

**Kind: instrument.** The evidence is policy, law and contract terms, with hosting and maintenance facts as their test; the ladder is the instrument family's (absent → stated → in force for categories → applied across the estate → the continental end state). A measure form — share of state data hosted under national jurisdiction — was considered and set aside: no country publishes it, and the base cannot compute it.

## 4. The norm

Already in `maturity-assessment-norms.md` §3 (Geopolitics). Tier **AU**; anchor the **AU Data Policy Framework (2022)** — sovereignty distinct from localisation; localisation "for certain categories of data" only; "politically neutral partnerships that take into account individual sovereignty and national ownership"; cloud interoperability and portability "so that data subjects are not locked into a single provider"; participation in a regional cross-border data flow mechanism — with the **Continental AI Strategy (2024)** ("Local First"; "self-manage their data and AI"), the **AU Interoperability Framework for Digital ID** Principle 7 ("prevent vendor and technology lock-in"), the **DTS** (≥ 30 % of content developed and hosted in Africa by 2030), **Malabo Art. 14** (adequacy-based transfers) and the **AfCFTA DTP Arts 20 and 22** (cross-border transfer subject to the annex; no forced location of computing facilities). Fixes: rungs from the DPF's own sequence — categories → portability → continental mechanism — plus the DTS hosting target. Reference: the UN Universal DPI Safeguards Framework (2024) and the Global Digital Compact para 17 on open standards.

## 5. The rubric

| stage | anchor | interpolated |
|---|---|---|
| 1 Absent | No policy or law on where state data sits or who may process it; core systems (ID, payments, exchange, government hosting) operated by a foreign provider or partner with no exit, portability or jurisdiction terms on record; and the base holds a citation for at least one of these, not merely silence | yes |
| 2 Nascent | Sovereignty stated as a goal — in a strategy, a DPF adoption, a draft classification or localisation clause, a national cloud announced — with nothing in force; agreements signed in the window still unconditioned. Also here: localisation requirements in force with no portability, interoperability or national capacity to run what is walled in | yes |
| 3 Established | A data classification, localisation-by-category or government-hosting policy or law **in force**; at least one core system hosted under national jurisdiction or maintainable nationally on record; at least one external agreement in the window carrying data-jurisdiction, portability or exit terms | yes |
| 4 Operating | State data classified and hosted per the policy across the estate; core systems maintainable nationally — source code, skills, contracts with exit and portability terms — on record for the ID, payments and exchange layers; external agreements systematically carry jurisdiction, portability and exit terms; the DPA or regulator has acted on a breach of them | yes |
| 5 Leading | The DPF end state: category-based localisation with portability and interoperability across providers; participation in the continental cross-border data mechanism; national or regional cloud and AI capacity per "Local First"; the DTS hosting target met on the state's own content | no — the DPF and DTS state it |

**Which part decides.** Where hosting, maintainability and agreement terms diverge, the stage is the lowest of the three unless the qualifier says why not — a state cannot be *Operating* on sovereignty while its ID system's source code sits with a vendor, whatever its hosting policy says. The qualifier names the part that holds the stage down.

**What is never evidence for a higher stage:** the number or size of agreements signed; a hyperscaler region announced; a data centre built by a foreign vendor without terms on record; a localisation law with no portability. The five retired indicators counted those things; this one asks what they carried.

## 6. The status outline

Under a new `### geopol.sovereignty — Digital sovereignty` sub-section in `status-outline.md`, the question in §0 and the bullets: where state data is hosted and under whose law (`ict-storage-govcloud`, `ict-storage-dcpresence`, `ict-storage-cloudadoption` as weak proxies, none attributing a provider); what the data classification or localisation instrument says (`reg-cyber-cloud`, `reg-data-*` where they exist — CC to check the DPI variable list); vendor dependence of core systems (no DPI variable; wiki); the terms of external agreements (no DPI variable; wiki). The section will be answered mainly from the wiki, as the five `geopol.*` sections are today, and the outline says so.

## 7. The mapping pass

**The base already holds the evidence.** 260 rows are mapped to the five retired indicators across all 54 countries; a keyword read of their prose on 2026-09-22 found *memorandum* or *MoU* in 135 of the 260 rows, *loan* or *grant* in 39, *data centre* in 37, *sovereign* in 29, *hosted* in a handful, *jurisdiction* in two and *portab-* in one — which is the picture the rubric expects: agreements are on record, their terms almost never are. The pass re-reads those 260 rows against §5, maps the ones that answer the sovereignty question (a hosting decision, a contract term, a vendor dependency, a classification) with prose written for this indicator, and leaves the rest where they are. It then reads the rows mapped to `gov.policy--data-localisation-policies`, `infra.store--local-data-centre-capacity-national-providers`, `dpi.id--national-maintenance-of-id-and-credentials-systems` and `gov.regional--cross-border-data-transfers` for the same purpose; one row may serve several indicators. **Expect most countries at 2, a good many at 3, few above, and a fair number *No evidence* on terms** — the *No evidence* rows are the sweep brief.

## 8. Snapshots

Assessed retrospectively as at 2026-07-31 and 2026-08-31 with the rest of the frame, since it is added before the baseline is cut; no `added` flag is needed unless the subject arrives from OSINT after the baseline has been written, in which case `adding-an-indicator.md` §8 applies and the July and August rows are written into the history file flagged `added`.

## 9. Checks, methodology, changelog

The frame checks in `maturity-assessment.md` §11; the assessed count on the methodology page moves from the five to the one; a changelog entry: *The Geopolitics chapter of the maturity assessment now carries one indicator, digital sovereignty, in place of five that recorded engagements with external powers. A reader sees where a country stands on control of its own data and systems, not how many memoranda it has signed.*

## 10. The five that retire

`geopol.usa`, `geopol.china`, `geopol.eu`, `geopol.gulf`, `geopol.india` — `assessed = 0`, `retired = 2026-09-22` in the frame; rows, mapped rows and prose kept; the status report's five sub-sections and the monthly's blocks are unaffected, since neither reads the frame.

## Build steps, in order

1. CC: cut the taxonomy patch (§1) and deliver it; write the `[ACT]` note if `taxonomy.md` needs it. Blocked until OSINT applies.
2. CC: on the mirror showing `geopol.sovereignty`, edit `lookups/indicators.csv` (§3), the norms lookup row (§4, cut from the register), the five rubric rows (§5), the status outline (§6). One commit.
3. CC: the mapping pass over the 54 units (§7), in the same run as the baseline assessment if the timing allows, otherwise as its own pass with the July and August rows flagged `added`.
4. CC: checks, methodology count, changelog (§9). One commit with step 2 if the pass is quick; otherwise its own.

Nothing here has been done. The subject does not exist, the frame is unchanged, no row has been mapped.
