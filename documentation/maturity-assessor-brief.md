# Maturity assessor — brief for one unit and one as-at date

*(CC, 2026-09-24. The drafter's instructions for `maturity-assess.py`'s model half: give it this file and the unit's packet, then run `apply` on what it writes. Tried first on STP as at 2026-07-31; rule 4's unplaced case came out of that run.)*

You are assessing one country's position on each indicator against a five-stage rubric, as at a month-end date. The packet file lists every indicator to assess. For each one it gives the norm, the five stage anchors, the prior snapshot's stage (if any) and the ledger rows mapped to it, each with its sources dated on or before the as-at.

**Output**: one CSV, UTF-8, with header exactly
`indicator_id,stage,stage_rows,value,unit,value_year,value_source,next_milestone,due,qualifier,reassessed,cause`
and one row per `## ` indicator in the packet. Nothing else goes in the file.

## How to set the stage

1. **Read the anchors from 5 down.** The stage is the highest anchor the cited rows fully satisfy. When a stage's anchor asks for several things (a law *and* regulations *and* an authority *and* an act on record), every part has to be on record. If one is missing, drop to the stage below.
2. **Evidence is the rows and their listed sources, nothing else.** Don't use outside knowledge of the country, even if you are sure of it. If the rows don't show something, it isn't on record.
3. **A row flagged `LATER`** also has sources after the as-at that are not listed. Its status, milestone and position may describe that later position. Assess only what the listed sources support. When in doubt, take the lower stage and say why in `qualifier`.
4. **Stage 1 needs a cited, dated absence**: a `Not held` row whose position states the thing does not exist, from a source. A row that only shows related activity (a passport system mapped to ID maintenance, DHIS2 mapped to health interoperability) is not a cited absence. **If the rows satisfy no anchor at all, stage 1 included, leave `stage` and `stage_rows` empty** and say why in `qualifier`. That marks the indicator *unplaced*: evidence is held but places no rung, and the indicator prints as unassessed. Never invent a stage the rows cannot carry.
5. **Rows mapped to an indicator are not all relevant to it.** Cite in `stage_rows` only the rows that satisfy the anchor you chose, joined with `|` and copied exactly from the packet (the backticked id). Every stage needs at least one.
6. **`qualifier`**: one short clause saying who says so, or what is missing for the next stage. Examples: *on the regulator's own figures*; *law in force; no enforcement act on record*; *secondary legal survey only*. Keep it under 25 words, no commas-in-quotes trouble: wrap the field in double quotes.
7. **Instruments and systems leave `value, unit, value_year, value_source` empty.** A **measure** stands on a figure, not a row. The packet shows its band cuts and any reference figure. Write a verdict only when:
   - the rows hold a **primary figure of the stated definition**: a regulator's, a census, an audited count. Give `value`, `unit`, `value_year` and `value_source` (the raw slug, which carries its date), and cite the row in `stage_rows` if there is one. Or:
   - an anchor's **condition** decides the stage: stage 5's end state, or a compound anchor that holds the stage below the band.

   Otherwise leave the measure out. The script takes the reference figure at its band, or marks it *No evidence*. The stage may not exceed the band the figure falls in; the script refuses one that does. A figure of a different definition goes in `qualifier`, never in `value`.
8. **`next_milestone`, `due`**: only when a cited instrument itself states a dated target (e.g. *approval of the AI law*, `2028-12-31`). Otherwise leave both empty. Never invent a date.
9. **`reassessed`**: `0`. **`cause`**: empty. Both are for later snapshots.

## Calibration

- Most countries sit at 2–3 on most indicators. A 4 needs the operating evidence the anchor names. A 5 is rare: it needs the continental end state, which is almost never on record.
- An instrument in force but held only through a secondary survey is still in force. Say so in `qualifier`.
- A draft or version-0.1 framework with no approval instrument is stage 2 ("in drafting"), not 3.

When done, report the count of rows written, the stage distribution, and any indicator where the choice was genuinely borderline (id, the two stages, one line why).
