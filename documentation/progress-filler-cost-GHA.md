# Progress filler — throughput record, GHA, 2026-08-29

*(Run against Ghana — no prior GHA run, so §0's skip found nothing to carry forward. Batch
label `progress-filler-GHA-2026-08-29`. Run CSV: `logs/progress-filler/GHA-2026-08-29.csv`,
with the selected and unselected registers beside it.)*

## The headline

**40 of 40 gaps had evidence to find, zero nils — and every single indicator staged both a
baseline and progress.** The first fully complete run in this series: not just zero nils but
zero baseline-only or progress-only outcomes either, a first. Ghana enters this series near the
opposite end from the recent SOM/SSD/SDN run of conflict-affected, thin-base countries — 81 of
121 indicators were already held before this run, and several of today's 40 gap subjects were
already densely populated (`infra.connect` 20 ledger rows, `dpi.pay` 16, `gov.legislate` 14,
`dpi.id` 12), reflecting a stable, high-capacity, well-documented digital-government programme
(Ghana Card/NIA, GhIPSS/MoMo interoperability, GRA's e-VAT and ITAS systems).

## Stage 1 — the sweep (complete)

| | |
|---|---|
| Gaps worked | 40 of 40 (no skips — no prior GHA run) |
| `agent_run` calls | 80 — 2 per gap across four parallel slices |
| Candidates returned | 248 |
| Fetched | 141 |
| Dropped | 8 (mostly `already-seen`, one `duplicate-in-run`, one `headline-only-stub`) |
| Held back by the cap | 29, recorded with URLs in the unselected register |
| **Staged after the cap** | **117 selections — 40 baseline + 77 progress**, over **106 distinct files** after merge (110 staged by the four slices before cross-slice dedup), filed as 36 in `GHA/baseline/` and 70 in `GHA/progress/` |
| Sessions | one (four parallel sub-agents, one parent merge) |

## Slicing and cross-slice dedup

**Four slices, by Level-1 topic**: Governance + ICT Infrastructure Connectivity/Storage/Energy,
DPI A (Data Exchange, Digital Identity/CRVS, Payments), DPI B (Registries, Sectoral MIS,
sub-national digitalisation), Digitalisation (rural) + Inclusion + Data + Geopolitics. All four
completed cleanly, no incidents, no sub-agents spawning sub-agents.

**The smallest merge in the series: 4 duplicate-URL groups, 4 redundant files removed**, plus
one cross-slice overwrite (not a duplicate — one document legitimately answering two indicators
in two different slices, where a sibling's write replaced the first slice's frontmatter rather
than merging it) caught and reconciled at the parent audit: Ghana's Health Information System
Strategic Plan 2022-2025 answers both `dpi.exchange--interoperability-of-health-systems` and
`digital.rural--digitalisation-of-rural-health-clinics`, and both topics/notes are now on the
one surviving file. Final lint: clean, 36 baseline + 70 progress files, no findings.

**No origin adjudications** — `progress-filler-drop-list.csv` untouched; every novel domain
screened KNOWN or NOVEL-report-only.

## What this run tests

Ghana confirms the pattern this series has been building toward at the well-covered end: a
mature digital-ID and payments stack (Ghana Card mandatory biometric re-verification under LI
2523, the NIA's rolling child-registration campaigns, GRA's e-VAT electronic invoicing under Act
1151) generating real, dated, primary-source movement inside the window almost everywhere the
sweep looked, including subjects the run briefed as likely thin (`geopol.china` came back with a
dated 2024 strategic-partnership elevation and a 2025 head-of-state summit rather than the
expected nil). The one substantive judgment call of the run was two dead GSS (Ghana Statistical
Service) links, both recovered by substituting the Statistical Service Act 2019 (Act 1003) as
baseline — arguably a stronger, more durable citation than the strategy PDF it replaced.

## Batch status

Staged and **UNDELIVERED** in `C:\corpus-osint-xfer\new-queue\GHA\` (36 baseline + 70
progress) until Bill hand-carries it into OSINT's `new/`.
