# Progress filler — throughput record, MOZ, 2026-08-28

*(The eleventh run of `PROGRESS-FILLER.md`, back to four slices on a smaller frame. No prior
MOZ run, so §0's skip found nothing to carry forward. Batch label
`progress-filler-MOZ-2026-08-28`. Run CSV: `logs/progress-filler/MOZ-2026-08-28.csv`, with
the selected and unselected registers beside it.)*

## The headline

**43 of 44 gaps had evidence to find. One nil**: `gov.policy--open-data-policy` — genuinely
not evidenced as a named instrument. Two further indicators closed with 0 baseline + 2
progress rather than the usual 1+2 —
`gov.legislate--digital-payments-legislation` (its only baseline candidates were already
admitted to `raw/`, correctly left unstaged per dedup rather than restaged) and
`gov.discourse--non-governmental-contribution-to-national-policy` (no baseline candidate
survived selection; two distinct in-window movements did). 118 selections over 96 distinct
files, 2.68 per gap.

## Stage 1 — the sweep (complete)

| | |
|---|---|
| Gaps worked | 44 of 44 (no skips — no prior MOZ run) |
| `agent_run` calls | 88 — 2 per gap, `effort: medium` |
| Candidates returned | 293 |
| Fetched | 129 |
| Dropped | 16 — mostly `already-seen` (candidates already admitted to `raw/`) |
| Held back by the cap | 30, recorded with URLs in the unselected register |
| **Staged after the cap** | **118 selections — 41 baseline + 77 progress — over 96 distinct files**, filed as 31 in `MOZ/baseline/` and 65 in `MOZ/progress/` |
| Batch size on disk | ~0.51 MB |
| Sessions | one |

## Four slices, the cross-slice warning held, and one real overwrite caught anyway

**Grouped**: Governance+Finance+Infra (12), DPI exchange/ID/payments (9), DPI
registries/MIS + Digitalisation (12), Technology+Capacity+Inclusion+Data+Geopolitics (11).
Every slice carried ETH's cross-slice-URL warning.

**Four cross-slice URL duplicates, all caught and resolved at merge**, plus **one genuine
silent overwrite — the first of this kind since GNB** (which is why `lint-staged-queue.py`
exists at all):

- **The overwrite.** Batch A staged
  `2019-10-16-plano-estrategico-sociedade-informacao-2019-2028.md` as
  `gov.policy--ict-strategy`'s baseline. Batch D, working the same URL independently for
  `capacity.training--graduates-entering-dt-ecosystem`, wrote to the **same filename** and
  **replaced** the frontmatter wholesale — `topics:`, `entities:` and `note:` — rather than
  merging, per the cross-slice instruction both slices had been given. Batch A caught it on
  its own post-write check, correctly declined to self-revert a sibling's write, and flagged
  it for the parent. Fixed at merge: both indicators' `topics:` and rationale restored onto
  the one surviving file. The instruction to merge rather than overwrite was in every slice's
  brief this run (unlike RWA, where it wasn't); it simply wasn't followed in one case. The
  fix is procedural rather than a new instruction: the parent's post-merge check for "a file
  whose current content doesn't match one of the indicators that selected it" — which this
  run's audit already runs as a matter of course — is what caught it, not a new rule.
- The DNIC civil-identification-system presentation — staged twice
  (`dpi.id--national-maintenance-of-id-and-credentials-systems`'s baseline at 12 KB `full`,
  `gov.legislate--legislation-covering-digital-id`'s baseline at 11 KB `excerpt`). Kept the
  full capture.
- The ATDI/World Bank mobile digital-ID tender — staged twice, both `full`
  (`dpi.id`'s progress pick at 8.1 KB, and a copy shared by
  `gov.legislate--legislation-covering-digital-id` and
  `dpi.registry--population-register` at 7.7 KB). Kept the larger, now carrying three
  indicators.
- INTIC's eGIF4M2 interoperability-regulation review — staged twice under different
  filenames, one already legitimately shared by four indicators, the other by two more. Kept
  the larger (already the four-indicator file), now carrying **six** indicators — the single
  largest multi-indicator file this series has produced.
- The mass World Bank-funded civil-registration campaign article — staged twice, both `full`
  (`dpi.id--digital-id-from-birth`'s progress pick at 3.2 KB,
  `dpi.registry--population-register`'s progress pick at 2.7 KB). Kept the larger.

**Nine further files legitimately serve two indicators each** (not duplicates), on top of the
six-indicator eGIF4M2 file above.

**One origin-screen adjudication — the first `[ACT]` note since GNB.** `bidsfactory.com`
(an excerpt aggregator re-serving World Bank procurement notices) was adjudicated `drop` when
it surfaced as a route to a civil-registry digitisation contract award; the primary
`documents1.worldbank.org` procurement plan was used instead. One row appended to
`progress-filler-drop-list.csv` — 10 rows now, across six countries.

**`scripts/lint-staged-queue.py` reports clean** over both folders (96 files) after the
merge. 118 selections resolve to exactly 96 files on disk, verified programmatically: zero
rows pointing at a missing file, zero orphan files, zero cap violations, zero duplicate URLs
remaining.

## Capture quality, declared

- **73 of 96 are `body_completeness: full`, 23 `excerpt`** — flagged, not retried, per
  `capture-rule.md`.
- **89 of 96 carry `date_source: source`, 7 `proxy`.** Precision is `day` on 86, `month` on
  8, `year` on 2.
- **The three largest files**: the 1997 Land Law (19/97, 19 KB), a UNCTAD science/technology
  parks assessment (17 KB), and Decree 67/2017 establishing the e-government interoperability
  framework (14 KB) — a notably smaller ceiling than every prior country in this series
  (largest file elsewhere has run 70–280 KB), consistent with Mozambican government
  publications running shorter and this run's higher `excerpt` share reflecting genuinely
  short primary documents rather than truncation at the fetcher's cap.
- No mojibake (`�`) found in a scan of all 96 staged bodies. Sources ran heavily Portuguese;
  titles and bodies preserved their own orthography throughout (accents, ç) with no
  transliteration.

## Stages 2–4 — not yet run

- **Stage 2 — the stage 4 read.** Pending Bill's hand-carry of `new-queue/MOZ/` into
  `OSINT\new\`, `update wiki`, and the mirror refresh.
- **Stage 3 — the mapping.** `outputs/reports/MOZ/indicators.csv` rewritten by hand against
  `documentation/indicator-mapping-conventions.md`.
- **Stage 4 — the render.**

**Yield is stated when stage 3 lands**, as gaps closed against the 44 probed and against
sessions spent.

## What this says about scheduling

**Warning every slice about cross-cutting URLs cuts the duplicate rate but doesn't eliminate
overwrites** — the instruction was in every brief this run, and one slice still replaced
rather than merged when it hit the collision. The backstop that actually caught it wasn't a
new rule but the parent's existing post-merge audit (files-vs-selected-rows,
content-vs-claimed-indicator), which is why that audit stays mandatory every run regardless of
how well the slice briefings are worded.
