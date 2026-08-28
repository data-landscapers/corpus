# Progress filler — throughput record, BEN, 2026-08-28

*(The fifth run of `PROGRESS-FILLER.md`, and the first to run six sub-agents concurrently
rather than the usual four. Batch label `progress-filler-BEN-2026-08-28`. Run CSV:
`logs/progress-filler/BEN-2026-08-28.csv`, with the selected and unselected registers beside
it.)*

## The headline

**64 of 64 gaps had evidence to find. Zero nils, for the fifth country running.** Not one of
the 64 indicators reading ***No evidence*** on the published BEN progress report was a
searched absence; every one was a collection absence.

**Every indicator got a baseline but one.** 63 of 64 — `infra.store--off-site-backup-capacity`
closed with a progress item (the WARDIP2 SOP2 project appraisal document) but no baseline,
because no dedicated off-site or disaster-recovery facility could be evidenced separately from
the national datacentre programme itself. The distribution is 47 indicators at the full 1+2,
16 at 1+1, and the one 0+1. That is the same cap-fill density as BDI's 47/23/8 split, on a
smaller frame.

**The substantive shape of what came back is a different country than the last three runs
described.** ZAF, AGO, GNB and BDI each turned up a state that legislates and plans at the
centre and does not build at the edge. Benin's batch is the first to turn up systems that are
actually **in production**: `PI-SPI`, BCEAO's UEMOA-wide instant-payment interoperability rail,
launched 30 September 2025 with Benin's own mobile operators already connected; ANIP's `RNPP`
digital-identity and civil-registration guichet unique, whose six-month bilan reports a
"spectacular" jump in birth-registration rates and answers seven separate indicators across
identity, health, education, local government and social protection because it is genuinely one
system doing all of it; APDP, the data-protection authority, reporting **782 dossiers examined**
in its 2025 balance sheet rather than merely existing on paper; a national datacentre with
technical testing under way since 2021; ARCEP publishing quarterly and annual observatories on
schedule; and the 2018 *Code du Numérique* (*Loi n° 2017-20*), a single ~600-page statute
covering e-commerce, data protection and much of the legislative chapter at once — the largest
single file this process has staged. Benin's ledger held 108 rows before this run, the densest
of the five countries so far, and the evidence follows: only **24 candidates were lost to
`already-seen`** against the mirror, against BDI's 14 over 78 indicators — proportionally
similar, not worse, despite the much fuller base.

**Two things worth flagging for the mapping pass rather than settling here.** First, the *Code
du Numérique* answers `data-protection-legislation`, `cybersecurity-legislation`,
`e-commerce-legislation`, `national-data-protection-readiness` and (as baseline, once) several
adjacent rows — it is one instrument doing the legislative work of a whole sub-chapter, which
argues for reading it once in full rather than four times in the four places it is cited. Second,
`geopol.usa`, `geopol.china`, `geopol.eu`, `geopol.gulf` and most of `digital.localgov` /
`digital.rural` entered this run at `subject_rows_at_probe = 0` — the ledger held nothing at all
for those subjects — and every one of them still closed, which is a stronger result than the
zero-row subjects returned in earlier countries' geopolitics chapters.

## Stage 1 — the sweep (complete)

| | |
|---|---|
| Gaps worked | 64 of 64 (no skips — no prior BEN run) |
| `agent_run` calls | 128 — 2 per gap, `effort: medium` |
| Candidates returned | 451 |
| Fetched | 190 |
| Dropped | 40, on `intake.md` §7's closed vocabulary (resolved via `reference.md`'s directory) |
| Held back by the cap | 127, recorded with URLs in the unselected register (partial for one slice — see below) |
| **Staged after the cap** | **174 selections — 63 baseline + 111 progress — over 148 distinct files**, filed as 56 in `BEN/baseline/` and 92 in `BEN/progress/` |
| Batch size on disk | 2.4 MB |
| Wall clock | ~39 minutes, six sub-agents concurrent (longest: 39.0 min) |
| Sessions | one |

**Drop codes** (from the run CSV's per-indicator tallies; a handful of rows under-record a
repeated code against a >1 count, so the code tally undercounts the dropped total by 2):
`already-seen` 24, `fetch-blocked` 8, `url-dead` 2, `inadmissible-origin` 2,
`headline-only-stub` 1, `off-topic` 1.

**The unselected register is partial for one slice.** Five of six sub-agents transcribed their
full fetched-but-uncapped candidate list; the sixth (`inclusion+data+geopol`, the widest slice
at 14 indicators) returned "a representative sample" rather than the complete set, by its own
account. Nothing is lost — the Agent-run spend is already paid and a later cap widening would
re-run those two briefs rather than reuse a register — but the unselected CSV for this batch is
not exhaustive the way BDI's and GNB's are.

## Six concurrent slices, and the concurrency fault partly recurred

**Five cross-slice URL duplicates, caught and merged; one capture defect, caught by the lint
and fixed by refetch.** Six sub-agents run concurrently cannot see each other's queues (§6), and
this run is the first to actually run six rather than four — the wider fan-out found more
collisions than BDI's zero, though far short of GNB's fifteen crossed bodies.

**The five duplicates** were all genuine: the same document, independently fetched and staged
by two different slices under two different filenames (never the same filename, so no silent
overwrite occurred — every case was a live-URL grep at merge, not a lint finding):

- `Loi n° 2017-20` (*Code du Numérique*) — staged full by one slice, excerpt by another;
  kept the full 618 KB capture, repointed the excerpt's four indicator selections onto it.
- The Council of Ministers communiqué of 2026-07-01 — staged full (APDP appointment) by one
  slice, excerpt (the same communiqué, different item) by another; kept the full capture.
- *Déclaration de Cotonou* (the ECOWAS regional digital-transformation summit) — staged full
  by two slices independently; kept the marginally larger capture.
- The World Bank's WARDIP2 $137M press release — staged full by two slices independently for
  three different indicators between them; kept the larger capture.
- The Benin Open Government Partnership co-creation roadmap — staged full by two slices; kept
  the larger capture.

Each repoint is reflected in the selected register; **174 selections resolve to exactly 148
files on disk, with zero rows pointing at a missing file and zero files with no selected row** —
verified programmatically at merge, not by eye.

**One real capture defect, found by `lint-staged-queue.py`'s TITLE check on its way to a
different conclusion.** The EU-Benin PAGODES announcement (`2023-07-20-ec-europa-eu-pagodes-launch.md`)
staged with `body_completeness: full` but a body full of `�` replacement characters everywhere
the source used `é` or `€` — an encoding mismatch in the fetching sub-agent's own tool call, not
a website fault. The lint's title-orthography check flagged it (correctly, if for the wrong
reason: it read the replacement characters as "the accented form"), which is exactly what caught
it. Re-fetched directly and rewrote the file with clean UTF-8; the second lint pass returns the
same TITLE finding, now confirmed a **false positive** rather than a defect — the page's English
title genuinely spells the country without an accent while French-language quotes inside the
same body correctly carry one, which is the source's own bilingual orthography and not a
transliteration error. Left as published.

**No other lint findings.** `scripts/lint-staged-queue.py` over the full merged batch of 148
files returns one finding (above, resolved) and reports the batch otherwise clean: zero crossed
bodies, zero unquoted `note:` scalars, zero partial date prefixes.

## Cross-queue dedup — the parent's pass

Covered above. **Selections were repointed, not decremented**, per §6: no indicator's
`staged_baseline`/`staged_progress` count in the run CSV changed as a result of the merge: the
run rows report each sub-agent's own selection count, and the physical dedup only ever collapses
two *files* representing the same selection onto one, never removes a selection.

One incidental fix at merge: a stray scratch file (`urls_check_ben5.txt`, a working URL list one
sub-agent left in its scratchpad rather than deleting) had landed in the shared xfer repository's
working tree rather than the sub-agent's own workspace. Removed before commit; nothing was staged
from it and it never reached OSINT's side.

## Capture quality, declared

- **130 of 148 are `body_completeness: full`, 18 `excerpt`** — flagged, not retried, per
  `capture-rule.md`. A better ratio than GNB's 58 of 205 and close to BDI's 13 of 141.
- **144 carry `date_source: source`**, 3 `retrieved` and 1 `derived`; precision is `day` on
  134, `month` on 13, `year` on 1.
- **Four files record a date conflict in `note` rather than a picked value**, left for ingest
  to settle with the document in hand.
- **Nineteen files carry a note mentioning a scan, OCR or large-PDF limit** — a much lighter
  constraint than Burundi's, and none of Benin's core legislative texts needed OCR: the *Code du
  Numérique*, the statistics law and the access-to-information code all yielded clean text
  layers, if at the cost of three retries at increasing `maxCharacters` for the 618 KB Digital
  Code.
- **The most-reused document is ANIP's guichet-unique six-month bilan**, selected under seven
  different indicators (digital identity, birth registration, social protection interoperability,
  local-government records and rural registry digitisation) — the single clearest instance yet
  of one Beninese system doing the substantive work several separate indicators ask about.

## Origin adjudications — none, for the first time

**Zero new watch/drop rows.** `origin-screen.py` returned only `KNOWN` and `NOVEL` verdicts
across every domain screened by all six slices (`NOVEL` is informational only, per the script's
own note, retired as a gate on 2026-08-26); one `DROP` fired (`globaltenders.com`, already on
record from an earlier run) and cost two candidates, both replaced or left uncapped rather than
routed around. `progress-filler-drop-list.csv` is unchanged by this run, and this run's
`notes-for-osint.md` entry is a plain `[FYI]`, not an `[ACT]` — the first of the five runs
without a drop-list action attached.

## Stages 2–4 — not yet run

- **Stage 2 — the stage 4 read.** Pending Bill's hand-carry of `new-queue/BEN/` into
  `OSINT\new\`, `update wiki`, and the mirror refresh.
- **Stage 3 — the mapping.** `outputs/reports/BEN/indicators.csv` rewritten by hand against
  `documentation/indicator-mapping-conventions.md`.
- **Stage 4 — the render.**

**Yield is stated when stage 3 lands**, as gaps closed against the 64 probed and against
sessions spent.

## What this says about scheduling

**148 files is the lightest batch the process has produced** — lighter than AGO's 134, and well
under half of GNB's 205 or BDI's 141-with-heavier-PDFs. 2.4 MB on disk against BDI's 8.2 MB and
GNB's larger PDF-heavy batch. 174 selections over 64 indicators is 2.7 per gap — denser cap-fill
than BDI's 2.5 over 78 — achieved with fewer, shorter documents rather than more of them, because
Benin's primary sources are mostly born-digital government press releases and PDFs with real text
layers rather than scans.

**The six-slice fan-out cost more coordination than the four-slice runs did**, in exactly the
place §6 predicts: five cross-slice duplicates against BDI's zero. It did not cost any actual
data quality — every duplicate was caught before commit and every file that reached the queue
resolves to a real, correctly-attributed body — but it argues for either keeping slice count at
four-to-five for a similarly-sized frame, or explicitly telling each slice which subjects its
siblings are covering so a shared subject (like the guichet-unique bilan, which touches three
different Level-1 chapters) is spotted before the fetch rather than after.

**The split still works and is still the lever.** 56 baseline against 92 progress: carrying the
baselines alone delivers every one of the 64 indicators' standing instruments bar the one nil
baseline, and defers only the movement layer. That remains Bill's call rather than the run's.
