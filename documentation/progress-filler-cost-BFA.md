# Progress filler — throughput record, BFA, 2026-08-28

*(The sixth run of `PROGRESS-FILLER.md`, and the first to record a full mojibake round-trip:
one sub-agent caught, diagnosed and refetched a genuine U+FFFD corruption itself; two others
independently investigated a suspected corruption and correctly ruled it a display artefact
rather than "fixing" text that was already right. Batch label
`progress-filler-BFA-2026-08-28`. Run CSV: `logs/progress-filler/BFA-2026-08-28.csv`, with
the selected and unselected registers beside it.)*

## The headline

**57 of 57 gaps had evidence to find. Zero nils, for the sixth country running.**

**Every single indicator got a baseline — the first 100% baseline-fill run of the six.**
ZAF, AGO, BDI and BEN each left at least one indicator without one; GNB left three. BFA left
none. The distribution is 47 indicators at the full 1+2 and 10 at 1+1 — **no indicator fell
below 1+1**, which no prior run has managed either. This is the densest cap-fill this process
has produced: 161 selections over 57 indicators is 2.82 per gap, ahead of BEN's 2.72 and BDI's
2.50.

**The substantive finding cuts against the obvious prior.** Burkina Faso has been under
military-junta rule since September 2022, faces an active jihadist insurgency holding a third
or more of the country, withdrew from ECOWAS in January 2025, and pivoted its foreign
partnerships toward Russia and the Alliance of Sahel States (AES, with Mali and Niger). The
obvious expectation is a state layer under strain, with digital governance stalled behind the
security crisis. **The batch does not show that.** The legislative and institutional layer kept
moving through the period this run's window covers, and in places accelerated: a data
protection law reform (creating ARCOD by merging the CIL and the broadcasting regulator CSC)
passed 3 August 2026 — six days before this run; a national identification law (*Loi
n°027-2024/ALT*) followed by an implementing mass-enrolment decree on 30 July 2026; PI-SPI
(BCEAO's UEMOA-wide instant-payment interoperability rail) live since September 2025 with
Burkina Faso's own connection-deadline extensions tracked into June 2026; e-invoicing
(`eSINTAX`) launched February 2026; and a national AI roadmap (2026-2030) adopted mid-2026. The
one indicator where the security context is directly legible in the evidence — regional legal
harmonisation — captured a clean before/after: the baseline **is** the ECOWAS withdrawal press
statement itself, and the two progress items are the AES's own emerging protocols filling the
vacuum it left. That one indicator is the exception that shows the pattern is read, not assumed.

**Two structural things worth flagging for the mapping pass.** First, Burkina Faso's tightly
interlinked national-ID ecosystem meant a handful of documents legitimately answer several
indicators at once: the 30 July 2026 Council of Ministers decree on mass ID enrolment answers
five separate `dpi.exchange`/`dpi.id`/`dpi.registry` indicators, and ONI's `missions` page
answers both `dpi.id--national-maintenance-of-id-and-credentials-systems` and
`dpi.id--authentication`. Second, `gov.regional`, `finance.mou`, `digital.rural`,
`tech.industry`, `capacity.research` and `geopol.india` all entered this run at
`subject_rows_at_probe = 0` — ten indicators with an empty ledger for their subject — and every
one of them still closed at 1+1 or better, which argues the country's evidence base is
genuinely rich rather than the mapping pass having simply not reached those subjects yet.

## Stage 1 — the sweep (complete)

| | |
|---|---|
| Gaps worked | 57 of 57 (no skips — no prior BFA run) |
| `agent_run` calls | 114 — 2 per gap, `effort: medium` |
| Candidates returned | 393 |
| Fetched | 160 |
| Dropped | 31, on `intake.md` §7's closed vocabulary (resolved via `reference.md`'s directory) |
| Held back by the cap | 35, recorded with URLs in the unselected register (complete this run — all four slices returned their full list, not a sample) |
| **Staged after the cap** | **161 selections — 57 baseline + 104 progress — over 139 distinct files**, filed as 50 in `BFA/baseline/` and 89 in `BFA/progress/` |
| Batch size on disk | 2.1 MB |
| Wall clock | ~48 minutes, four sub-agents concurrent (longest: 47.7 min, the 18-indicator DPI slice) |
| Sessions | one |

**Drop codes**: `already-seen` 24, `headline-only-stub` 6, `fetch-blocked` 3,
`inadmissible-origin` 2, `out-of-window` 1, `url-dead` 1, `duplicate-in-run` 1,
`no-development` 1.

## Four slices this time, not six — and it shows in the dedup count

**Only eight cross-slice URL duplicates, against BEN's five on a smaller frame but a much
higher per-slice indicator density (DPI's slice alone carried 18 tightly related indicators).**
BEN's cost record argued for fewer, larger slices after six slices produced five collisions on
64 gaps; this run used four slices on 57 gaps, with the DPI chapter kept whole rather than
split. The collision rate per gap (8/57 = 0.14) is close to BEN's (5/64 = 0.08) despite BFA's
national-ID ecosystem being unusually interconnected — several of the eight collisions are the
30 July 2026 mass-enrolment decree and the September 2025 Yaadga/family-code stories, which
were always going to be found from more than one angle in a country this size with a topic this
central. **All eight were caught by a URL grep across the merged queue before commit** — none
reached OSINT, and none was a same-filename overwrite (every collision used two distinct
filenames, so the older auditing method — filenames claimed by conflicting rows — would have
missed all eight; the URL grep is what actually catches this class of duplicate).

**Every duplicate resolved by keeping the fuller (or, where both were `full`, the larger)
capture** and repointing every affected indicator's selection onto the survivor:

- The 30 July 2026 mass-enrolment decree (2 duplicate captures, feeding five indicators total)
- The MDENP national AI workshop article (2 duplicate captures)
- The e-invoicing (`eSINTAX`) launch article (2 duplicate captures)
- *Loi n°001-2021/AN* on personal data protection — one `full`, one `excerpt`; kept the full
- The Koloko VENEEM civil-registration training article (2 duplicate captures)
- The new *Code des personnes et de la famille* adoption article (2 duplicate captures)
- The Yaadga regional-actors identification article (2 duplicate captures)
- The Africa Frontline First community-health digitisation article (2 duplicate captures,
  the larger at 11.3 KB against 7.4 KB)

**174 → 161 selections resolve to exactly 139 files on disk** — verified programmatically, not
by eye — with zero rows pointing at a missing file and zero files with no selected row. One
transcription slip was caught in this same pass: a baseline selection for
`gov.regional--cross-border-data-transfers` still pointed at a duplicate file removed at merge;
corrected before the CSVs were finalised, which is exactly the class of error this
programmatic cross-check exists to catch rather than let through.

**No stray scratch files landed in the shared repository this run** — the fix broadcast to
sub-agents after BEN's `urls_check_ben5.txt` incident held.

## The mojibake check earns its place in the briefing

**One genuine correction, two correctly-dismissed false alarms — the full range of outcomes the
check was added for.** Following BEN's PAGODES encoding defect (found by the lint, not by the
fetching agent), this run's briefing told every slice to scan for `�` immediately after
fetching and re-fetch on sight.

- **The real one**: the STAES/MDENP digital-maturity diagnostic report initially decoded with
  U+FFFD replacement characters in place of apostrophes and accents. The sub-agent caught it
  itself, re-fetched, and staged the clean version — the first time in this series a fetching
  agent has caught and fixed this class of defect without the parent's lint pass finding it
  afterward.
- **Two false alarms, correctly ruled out**: one sub-agent's own terminal display rendered
  correct UTF-8 bytes (`°`, `é`) as `�` and it verified via hex inspection before concluding
  nothing was wrong; another investigated a suspected corruption in a World Bank PAD text file
  and confirmed the bytes were genuinely correct UTF-8, not a fetch artefact, before staging.
  A third apparent case turned out to be **decorative bold Unicode styling** (U+1D400 block
  mathematical alphanumeric symbols) used by two Burkinabè government sites for web-page
  emphasis — real source text, not corruption, and not a diacritic either, which is why
  `lint-staged-queue.py`'s title check flagged it as "the accented form" without being wrong
  that *something* unusual was there.
- **Verified independently at merge**: a `grep` for the UTF-8 encoding of U+FFFD across all 139
  staged files returns zero hits. The batch is clean.

## Capture quality, declared

- **116 of 139 are `body_completeness: full`, 23 `excerpt`** — flagged, not retried, per
  `capture-rule.md`. A similar ratio to BEN's 130/148.
- **All 139 carry `date_source: source`** — no `proxy` or `retrieved` fallbacks needed this
  run, a cleaner dating record than any prior country in this series. Precision is `day` on
  117, `month` on 18, `year` on 4.
- **`lint-staged-queue.py` returns three findings, all verified false positives** (documented
  above): two decorative-Unicode-styling cases and one bilingual-document case (a World Bank
  Project Appraisal Document whose English title correctly omits accents while French
  institution names inside the body correctly carry them — the same class of false positive
  BEN's PAGODES file produced, now seen twice). Zero crossed bodies, zero unquoted `note:`
  scalars, zero partial date prefixes.
- **The three largest files** are CONASUR's national IDP-recovery strategy (213 KB — the
  primary humanitarian-crisis document, earning its size), the health ministry's digital-health
  strategic plan (107 KB), and MDENP's digital-maturity diagnostic (106 KB, the file that needed
  the mojibake refetch above).

## Origin adjudications — none, for the second run running

**Zero new watch/drop rows.** Two `DROP` verdicts fired during screening — a Pravda-network
mirror site and a generated-content "Telecom Observer" site — and both were **pre-existing**
adjudications, costing one candidate each rather than producing new rows.
`progress-filler-drop-list.csv` is unchanged; this run's `notes-for-osint.md` entry is a plain
`[FYI]`.

## Stages 2–4 — not yet run

- **Stage 2 — the stage 4 read.** Pending Bill's hand-carry of `new-queue/BFA/` into
  `OSINT\new\`, `update wiki`, and the mirror refresh.
- **Stage 3 — the mapping.** `outputs/reports/BFA/indicators.csv` rewritten by hand against
  `documentation/indicator-mapping-conventions.md`.
- **Stage 4 — the render.**

**Yield is stated when stage 3 lands**, as gaps closed against the 57 probed and against
sessions spent.

## What this says about scheduling

**139 files is lighter than BEN's 148 and much lighter than GNB's 205**, on a smaller frame (57
gaps against BEN's 64) but a denser cap-fill (2.82 selections/gap against BEN's 2.72). 2.1 MB on
disk. The four-slice structure — one slice per Level-1-adjacent group rather than six —
produced fewer cross-slice collisions per gap than BEN's six-slice run, though the DPI chapter's
internal density (18 indicators sharing one national-ID ecosystem) meant most of this run's
eight collisions were concentrated there regardless of slice count. **The lesson for the next
run is probably not slice count but subject clustering**: telling a slice explicitly which
other subjects are running concurrently, so a document it expects to be widely reused (a
Council of Ministers decree, a national strategy document) gets checked against the shared
queue before the fetch rather than after.

**The split still works and is still the lever.** 50 baseline against 89 progress: carrying
the baselines alone delivers every one of the 57 indicators' standing instruments — for the
first time in this series, with no exceptions — and defers only the movement layer. That
remains Bill's call rather than the run's.
