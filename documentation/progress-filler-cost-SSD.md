# Progress filler — throughput record, SSD, 2026-08-29

*(Run against South Sudan — no prior SSD run, so §0's skip found nothing to carry forward.
Batch label `progress-filler-SSD-2026-08-29`. Run CSV: `logs/progress-filler/SSD-2026-08-29.csv`,
with the selected and unselected registers beside it.)*

## The headline

**77 of 77 gaps had evidence to find. Zero nils**, in a conflict-affected, low-capacity state
where a genuine nil was expected on several subjects (`gov.standards`, `gov.discourse`,
`digital.rural`, `tech.innovate`, `capacity.literacy`, `include.divides` all entered the run
with zero ledger rows). Every one of them still staged — South Sudan's DPI and payments layer
in particular is unusually well-populated already (`dpi.id` and `dpi.pay` both held 7-8 ledger
rows going in, the highest starting density seen in this series), and the run's genuine absences
surfaced as baseline-only or progress-only outcomes rather than empty ones: one indicator
(`gov.policy--data-governance-policy`) found no adopted policy and staged progress alone (a
governance-strategy consultancy tender), and several others staged a baseline with no in-window
movement rather than being padded to fill the cap.

## Stage 1 — the sweep (complete)

| | |
|---|---|
| Gaps worked | 77 of 77 (no skips — no prior SSD run) |
| `agent_run` calls | 154 — 2 per gap across seven parallel slices |
| Candidates returned | 596 |
| Fetched | 230 |
| Dropped | 70 (`already-seen` ~29, `inadmissible-origin` ~5, `duplicate-in-run` 1, `headline-only-stub` 1 — South Sudan's dense DPI/legislative layer meant heavy overlap with material already in `raw/`) |
| Held back by the cap | 72, recorded with URLs in the unselected register |
| **Staged after the cap** | **202 selections — 76 baseline + 126 progress**, over **158 distinct files** after merge (186 staged by the seven slices before cross-slice dedup), filed as 63 in `SSD/baseline/` and 95 in `SSD/progress/` |
| Sessions | one (seven parallel sub-agents, one parent merge) |

## Slicing and cross-slice dedup

**Seven slices, by Level-1 topic**: Governance A (policy/legislate/protect), Governance B
(regional/standards/discourse) + Finance + the IXP indicator, ICT Infrastructure + DPI Data
Exchange, DPI (Digital Identity/CRVS, Payments, Sectoral MIS), DPI Registries +
Digitalisation, Technology + Capacity, Inclusion + Data + Geopolitics. All seven completed
cleanly — zero indicators skipped or reassigned, zero sub-agents spawning sub-agents.

**Cross-slice URL dedup: 20 duplicate-URL groups, 29 redundant files removed**, taking 186
staged files down to 158 — proportionally the densest dedup pass in the series (16% of files
removed, against SOM's 14%), reflecting how tightly South Sudan's DPI/CRVS/registry chapters
interlock: the World Bank ID4D Country Diagnostic alone was independently staged four times
across three slices before merge, answering six indicators once consolidated. Every group was
resolved on completeness (fullest body, most precise date) with topics and notes merged across
every indicator that selected it. Where a document was any indicator's baseline it stayed filed
under `baseline/` even when a sibling slice had staged it as progress, per §5's baseline-wins
rule; three of the 20 groups required moving the more complete body into the `baseline/`-filed
survivor.

**One lint finding investigated and cleared, not merge-caused**: `lint-staged-queue.py`
flagged `baseline/2012-01-01-south-sudan-national-ict-policy.md` as `CROSSED` against a
sibling's `2009-08-24-taxation-act-2009-south-sudan.md` throughout the run — the originating
sub-agent traced it to a mechanical false positive (the title's only distinctive token, "2012",
isn't printed on the captured page, so the title-match heuristic scored 0% against its own body
and coincidentally matched an incidental "2012" in the unrelated Taxation Act's body). The
parent independently re-verified by reading both bodies directly: the ICT Policy file's content
(postal/telecommunications/IT sector policy statement) matches its own frontmatter exactly.
No crossing occurred. Final lint after merge: clean except this one confirmed false positive,
across 63 baseline + 95 progress files.

**No origin adjudications this run** — `progress-filler-drop-list.csv` untouched; every novel
domain screened KNOWN or NOVEL-report-only, nothing hit the closed inadmissible-origin table.

## What this run tests

South Sudan is the first genuinely conflict-affected state this series has run against, and it
did not produce the thin, absence-heavy batch that framing might predict. The Cybersecurity/ID
legislative programme (Nationality Act 2011, National ID card rollout January 2026, the
Civil Registration and National Identification Regulations 2024, a January 2026 data-protection
bill workshop) reads as active and recent; digital payments and the World Bank BOOST-style
social-registry/G2P work (SNSOP cash transfers, NCA's mandatory e-service platform circular)
is likewise dated and specific. Where the state genuinely has not moved — regional standards
adoption, non-governmental policy discourse, rural digitalisation of health/education/registry/
police infrastructure, innovation-ecosystem indicators — the run found baseline-only or
progress-only outcomes rather than nils, which is the more informative shape: the frame
indicators exist as questions the state has partially answered, not as empty boxes.

## Batch status

Staged and **UNDELIVERED** in `C:\corpus-osint-xfer\new-queue\SSD\` (63 baseline + 95
progress) until Bill hand-carries it into OSINT's `new/`.
