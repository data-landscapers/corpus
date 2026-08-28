---
type: spec
title: report-region-skeleton.md — the shape and drafting contract for region reports
last_reviewed: 2026-08-28
status: in force; Corpus-owned
---

# report-region-skeleton.md — the shape and drafting contract for region reports

**This is the knob for what a region report looks like.** Section order, front matter, word budget and the instructions given to a drafting agent live here, in one file. **The register is not here** — house style is the Corpus editorial register (`documentation/report-layer.md` → §10 *The register*), in one copy, and it binds this document exactly as it binds a country report. `BUILD.md` stage 4 governs the process and `documentation/report-layer.md` the record layer all the report processes share.

Change it, then `python scripts/report-render.py --unit {X__} --render --doc progress` — tables rebuild from `ledger.csv`, narrative blocks are carried across by marker id, and nothing is re-read from the base.

---

## One document, for now

**A region issues the progress report only.** The renderer refuses `status` and `monthly` for an `X__` unit rather than writing an empty one, so nothing downstream needs a branch: `--doc all` over every unit lets a region silently yield its one document.

That is a scope decision, not a claim that the other two are wrong for a region. A regional status report is the obvious next one — it needs no new ledger and no new reading, only this file's sections rendered as an inventory. **What a region has that a country does not is a period question**: a convention gains ratifications, a working group meets or does not, a secretariat is funded or is not, and none of that is legible in a single-date snapshot. Start where the unit's own evidence is.

## Front matter

```yaml
---
title: {Region} — progress report, YYYY-MM-DD to YYYY-MM-DD
compiled: YYYY-MM-DD               # the render date
period: YYYY-MM-DD to YYYY-MM-DD
place: X__
ledger_rows: N                     # script-emitted
not_held: N                        # script-emitted; the count a reader is owed
---
```

## Sections, in this order

| # | Heading | Holds |
|---|---|---|
| 1 | Summary of the period | The three or four things a reader who stops here must have. Prose only, no table. |
| 2 | Institutions and mandates | The bodies themselves: mandate, leadership, membership, secretariat capacity, restructuring, the programmes a body owns. `gov.regional`, `gov.discourse` |
| 3 | Instruments and harmonisation | Conventions, model laws, protocols, standards and their ratification and domestication. `gov.legislate`, `gov.policy`, `gov.standards`, `gov.protect`, `data.open`, `tech.ai` |
| 4 | Shared systems and infrastructure | The rails that actually cross a border: interconnection, cables and exchange points, roaming, payment and identity interoperability, shared statistical systems. `infra.*`, `dpi.*`, `data.statistics`, `data.satellite`, `digital.*` |
| 5 | Coordination and collaboration | Working groups, committees, joint programmes; partnership with actors outside the region; and the evidence on where coordination is *not* happening. `geopol.*`, `tech.industry`, `tech.innovate` |
| 6 | Capacity and inclusion | `include.*`, `capacity.*` |
| 7 | Finance | What funds the regional layer and what it is able to absorb. `finance.new`, `finance.mou`, `finance.budget` |
| 8 | Where the record is thin | The ***Not held*** rows, with what would settle each. |

The mapping is `lookups/report-region-sections.csv` and is what the renderer reads; this table is the readable copy. **A section with no ledger rows is written as one sentence saying so** — never padded to parity with a thick one, and never silently dropped. On a thin region that will be most of the document, and it should be.

**Within a section, the renderer sub-groups by taxonomy Level-2 subject and prints a `###` sub-heading with that subject's `lookups/taxonomy.csv` label, in the taxonomy's own order** — one small table per subject rather than one table for the whole section, exactly as `documentation/report-country-skeleton.md` describes. A region issues the progress report only, so this affects that one document.

**Section follows the object class, and the subject map is the fallback.** This is the first way a region report differs from a country one. A country row lands in its section by subject because the subject *is* the object's field; a regional row's section is decided by **what kind of thing it is** — a body, an instrument, a running system, a coordination mechanism, a financing line — and the same `gov.regional` slug sits on all five. The map gives the default; the run overrides `section` per row and is expected to, often. A body is *Institutions* whatever slug the sources carry.

## What the ledger carries that a country's does not

Same schema, `documentation/report-layer.md` §1 — but three of its columns do different work here, and the run must know which:

- **A body is a row.** The African Telecommunications Union is a named object whose position can move — mandate, membership, leadership, whether it is meeting or funded — so it passes §1's test and it is the row a region report is most about. Its `name` is the body as a reader would name it, not the body plus its latest communiqué.
- **Ratification and accession counts are `measure` rows**, not statuses. *Malabo Convention ratifications* moving `15 of 55 (2025-06)` → `17 of 55 (2026-05)` is the single most legible movement the regional layer produces, and it is a measure of a named instrument rather than a status of one. The instrument itself is a separate `instrument` row.
- **`position_start` and `position_end` carry the substance**, as everywhere: `Nine member states connected, three tariffs harmonised`, not *Piloting*. A coordination mechanism's substance is usually **when it last met and what it published** — `Last met 2024-11, no work programme published` is a position, and it is the one that matters.

## What must not be in it

- **A national development, because it happened in the region.** A regional report is not a digest of its members' news. The test is `SWEEP-REGIONAL.md` §4B's: the thing is regional, or it bears on at least three of the region's countries. A country's own programme belongs to that country's ledger, and `documentation/report-layer.md` says a row lives in exactly one.
- **A roll-up of member states.** A region is a first-class place, not the sum of its children. Counting how many members have a data-protection law is a **measure of a regional instrument's take-up** and is a row; summarising each member's position is the country reports, restated worse.
- **A bilateral.** Two members signing with each other is a national development twice over unless a regional body is party to it or it is the first instance of a regional instrument being used.
- **A body's non-digital work.** Most of these institutions are only fractionally digital (`SWEEP-REGIONAL.md` §4A). Their health, agriculture, energy and trade-in-goods programmes are not our subject and are not rows.

## Word budget

**Prose only, tables excluded: 800–1,150 words for a progress report.**

Deliberately low: a region's ledger is short outside `XAF`, and the failure mode of a thin ledger with a fat budget is prose that fills the gap with the general knowledge the model brought with it. `scripts/report-register-check.py` reads this line — the same script, this skeleton, for an `X__` unit.

Count prose with links reduced to their anchor text (`re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', body)`).

## Markers

```markdown
<!-- narrative: {section-key} -->
…model-authored prose…
<!-- /narrative -->
```

Keys are `summary`, `institutions`, `instruments`, `systems`, `coordination`, `capacity`, `finance`, `gaps`. Everything outside the markers belongs to the renderer and is overwritten without warning; everything inside belongs to the model and is never touched by a script.

## The drafting contract — what a delegated agent is given and must return

**Partition by institution first, section second.** This is the second way a region report differs. A country's compiled layer is its intersection pages, so its agents split by section; a region has almost no intersection pages (`XEA` has one, `XAF` none), and its compiled layer is **the institution entity pages** — one per body, each already carrying that body's activity and its source list. So the practical split is: one agent per group of institutions, plus one agent for the region hub and the region-placed sources that no institution owns.

Every agent prompt carries these seven, verbatim in substance:

1. **The output shape, exactly** — a ledger row per body, instrument, system or measure (`name | kind | section | status | milestone | position_start | position_end | movement | source-slug`), then six to ten dated facts formatted `fact — [slug]`, then anything the wiki itself flags as unreconciled.
   - **`name` is a named object, short enough to scan** — *SADC Model Law on Data Protection*, not *data protection harmonisation in Southern Africa*.
   - **`milestone` is the event that fixed the position**, not the date it happened.
   - **`kind` is `measure` for a count** (ratifications, members connected, states domesticated) and `instrument` for everything else, bodies included.
2. **Both ends dated, always.** Ask explicitly what the base said about each row twelve months ago: the same position carried earlier is `since` and is *not* movement; a different one is `prior_*` and is; nothing at all is ***Baseline not held***. An agent that is not asked returns only the newest date, and the report then reads the ledger's build date as a year of change.
3. **Resolve slugs yourself** against `index/` (`scripts/vault_lib.py`), and **if a slug is not in the index, say so and drop the claim** — never reconstruct a plausible URL.
4. **Report absence rather than filling it.** A body that has published nothing in the window is a finding, and the most common one: say *no work programme, communiqué or meeting record is held for this body since {date}* and stop. **This is where a region report is most at risk** — every one of these institutions has a public reputation a model can write from, and a paragraph about what the AU "is working towards" that rests on no source is the exact failure the register and check H exist for.
5. **The regional test, stated** — the item is regional, or bears on at least three of the region's countries; a member state's own programme is not a row. Give the agent the *What must not be in it* list above.
6. **No web search. Local files only.** An agent that helpfully fetches a fresh source has broken the sweep containment boundary and put unadmitted material into a deliverable.
7. **The Corpus editorial register — `documentation/report-layer.md` → §10 *The register* — in full**, wherever the agent writes narrative rather than ledger rows.
