# Progress filler — throughput record, TZA, 2026-08-28

*(The twelfth run of `PROGRESS-FILLER.md`, the largest frame this series has run (60 gaps)
and the first to close with zero nils on a frame this size. No prior TZA run, so §0's skip
found nothing to carry forward. Batch label `progress-filler-TZA-2026-08-28`. Run CSV:
`logs/progress-filler/TZA-2026-08-28.csv`, with the selected and unselected registers beside
it.)*

## The headline

**60 of 60 gaps had evidence to find. Zero nils** — the largest frame in the series and the
first at this scale with none. 53 indicators closed at the full 1 baseline + 2 progress, 7 at
1+1; no indicator fell below 1+1 or lost its baseline. 173 selections over 145 distinct files,
2.88 per gap, the second-densest cap-fill of the series (behind only KEN's 2.96).

## Stage 1 — the sweep (complete)

| | |
|---|---|
| Gaps worked | 60 of 60 (no skips — no prior TZA run) |
| `agent_run` calls | 120 — 2 per gap, `effort: medium` |
| Candidates returned | 504 |
| Fetched | 180 |
| Dropped | 17 |
| Held back by the cap | 241, recorded with URLs in the unselected register — the largest unselected register this series has produced, reflecting the frame's size and unusually dense candidate return per gap |
| **Staged after the cap** | **173 selections — 60 baseline + 113 progress — over 145 distinct files**, filed as 52 in `TZA/baseline/` and 93 in `TZA/progress/` |
| Batch size on disk | ~6.0 MB — by far the largest batch this series has produced |
| Sessions | one |

## Five slices, self-repairing merges, and the largest duplicate cluster yet

**Grouped by ~12-indicator chunks** rather than strict Level-1 boundaries, given the frame
size: gov.policy+gov.legislate (12), gov.regional/standards/discourse+infra (12), DPI
exchange/ID/registries (12), DPI MIS+digitalisation+technology (12),
capacity/inclusion/data/geopolitics (12). Every slice carried the explicit "merge
additively, never overwrite" instruction added after MOZ's silent-overwrite incident.

**The instruction worked as designed this time — twice.** Two more cross-slice overwrites
occurred (a document one slice had already merged got wholesale-replaced by a second slice
hitting the same URL independently), and **both times the sub-agent that discovered its own
work had been wiped repaired it itself**, restoring the wiped indicator's contribution
additively rather than escalating to the parent or reverting the other slice's write outright.
This is the first run where the merge-additively instruction visibly changed behaviour
mid-run rather than only being caught at the parent's post-merge audit.

**Nine cross-slice URL duplicates survived to the parent audit anyway** — the largest cluster
this series has produced, consistent with the frame's density (504 candidates across 60 gaps,
more per gap than any prior run). All resolved the same way: keep `full` over `excerpt`,
keep the larger where both are `full`, merge `topics:` and `note:` onto the survivor, delete
the loser, repoint every affected selected-register row. Two of the nine collapsed **four**
indicators onto one survivor (a NAOT birth/death-certificate performance audit and an RITA
48-hour-certificate announcement, both central to Tanzania's CRVS/NIDA identity chain); most
of the rest collapsed two or three. **Fifteen further files legitimately serve two to four
indicators each** without being duplicates — one document, several indicators, staged once —
led by a data-centre standards guideline answering four governance/infrastructure indicators
at once.

**`scripts/lint-staged-queue.py` reports clean** over both folders (145 files) after the
merge. 173 selections resolve to exactly 145 files on disk, verified programmatically: zero
rows pointing at a missing file, zero orphan files, zero cap violations, zero duplicate URLs
remaining.

## Capture quality, declared

- **115 of 145 are `body_completeness: full`, 30 `excerpt`** — flagged, not retried, per
  `capture-rule.md`.
- **136 of 145 carry `date_source: source`, 9 `proxy`.** Precision is `day` on 114, `month` on
  22, `year` on 9.
- **The three largest files**: a NAOT performance audit of PO-RALG and LGAs FY2024/25
  (738 KB — by far the largest single file this series has produced), the TPF/NBS Crime
  Report 2020 (499 KB), and the Local Government (District Authorities) Act, Cap. 287
  (405 KB).
- **A genuine but low-severity capture defect, declared rather than silently carried**: 20 of
  145 files contain one or more U+FFFD replacement characters, checked individually rather
  than dismissed. Every instance sampled traces to the same cause — PDF text extraction
  losing bullet-point glyphs (`•`), degree signs (`°`) and, in one bibliography citation, an
  accented Latin letter (`é` in "Pérez") — never a corrupted word or a lost clause. This is a
  structural PDF-extraction artifact, not a narrative one: the substantive text in every
  sampled case reads correctly around the dropped glyph. Not refetched — the cost of
  re-fetching 20 large PDFs for a bullet-point marker is not proportionate to what would be
  recovered, and `capture-rule.md`'s truncation rule (flag, don't retry) applies by the same
  logic to a dropped non-alphanumeric glyph.

## Origin adjudications — none

**Zero new watch/drop rows.** All five slices reported every candidate domain as either
already-known or novel-and-informational; `progress-filler-drop-list.csv` is unchanged — still
10 rows across six countries. This run's `notes-for-osint.md` entry is a plain `[FYI]`.

## Stages 2–4 — not yet run

- **Stage 2 — the stage 4 read.** Pending Bill's hand-carry of `new-queue/TZA/` into
  `OSINT\new\`, `update wiki`, and the mirror refresh.
- **Stage 3 — the mapping.** `outputs/reports/TZA/indicators.csv` rewritten by hand against
  `documentation/indicator-mapping-conventions.md`.
- **Stage 4 — the render.**

**Yield is stated when stage 3 lands**, as gaps closed against the 60 probed and against
sessions spent.

## What this says about scheduling

**The merge-additively instruction is earning its keep**: after MOZ's single overwrite caught
only by the parent, this run had two more overwrites and both were self-corrected by the
affected sub-agent before the parent ever saw them. That is the instruction doing its job —
worth keeping as a standing element of every multi-slice brief, not just a one-off response to
MOZ. The nine-duplicate cluster on this run's 504-candidate frame, against RWA's five on 400
and ETH's four on 417, suggests duplicate rate scales with candidate density more than with
gap count as such — a signal for sizing future slice counts by expected candidate volume, not
just indicator count, on very well-covered subjects like Tanzania's CRVS/NIDA layer.
