# Progress filler — throughput record, SDN, 2026-08-29

*(Run against Sudan — no prior SDN run, so §0's skip found nothing to carry forward. Batch
label `progress-filler-SDN-2026-08-29`. Run CSV: `logs/progress-filler/SDN-2026-08-29.csv`,
with the selected and unselected registers beside it.)*

## The headline

**91 of 92 gaps had evidence to find, one genuine nil** — the largest gap count and largest
frame this series has run, against a state in active civil war (SAF vs RSF, since April 2023)
with its administration territorially fractured. Four indicators legitimately found no
baseline (broadband strategy, the population register specifically — Sudan's identity system
runs through the Civil Registry rather than a distinct population register — citizen feedback
portals, bridging of digital divides), and nine found no in-window progress; none were padded
to fill the cap. This is the messiest merge in the series to date, not because the sweep itself
went badly but because eight parallel slices converged unusually often on the same handful of
Arabic-language primary sources (the Civil Registry Act 2011, the PM's November 2025 decree
founding three digital authorities, the CBOS payments RFP), triggering repeated concurrent
overwrites the parent had to reconstruct rather than simply merge.

## Stage 1 — the sweep (complete)

| | |
|---|---|
| Gaps worked | 92 of 92 (no skips — no prior SDN run) |
| `agent_run` calls | 185 (184 expected at 2/gap; 1 over-count is a cosmetic bookkeeping slip in one slice's run CSV, left as observed rather than corrected post-hoc, per the standing rule) |
| Candidates returned | 546 |
| Fetched | 266 |
| Dropped | 22 (mostly `already-seen`, plus a handful `inadmissible-origin` and `fetch-blocked`) |
| Held back by the cap | 44, recorded with URLs in the unselected register |
| **Staged after the cap** | **241 selections — 88 baseline + 153 progress**, over **187 distinct files** after merge (204 staged by the eight slices before cross-slice dedup), filed as 71 in `SDN/baseline/` and 116 in `SDN/progress/` |
| Sessions | one (eight parallel sub-agents, one parent merge) |

## Slicing and cross-slice dedup — the hardest merge in the series

**Eight slices, by Level-1 topic**: Governance A (policy/legislate), Governance B
(protection/regional/standards/discourse) + Finance, ICT Infrastructure + DPI Data Exchange,
DPI (Digital Identity/CRVS, Payments), DPI Registries + Sectoral MIS, Digitalisation +
Technology, Capacity + Inclusion, Data + Geopolitics.

**14 duplicate-URL groups, 18 redundant files removed**, 204 down to 187. Two of the fourteen
required real reconstruction rather than a routine pick-the-fuller-body merge:

- **The PM's 5 November 2025 decree** founding the Digital Transformation, Data/AI and
  Cybersecurity Authorities was independently captured **three times** under three filenames
  by four different slices, answering **nine separate indicator selections** across `gov.policy`,
  `gov.legislate`, `gov.protect`, `tech.ai` and `data.open`. Concurrent overwrites during the run
  meant no single surviving file's frontmatter still carried all nine topics by the time slices
  finished — the merge reconstructed the full topic list from the `-selected.csv` rows
  themselves (which name the indicator, not just the file) rather than trusting on-disk
  frontmatter, since the frontmatter had already lost information to the churn.
- **The Civil Registry Act 2011** was captured twice (two different truncated excerpt ranges
  of the same long PDF) and, per two independent slice reports, the surviving `dpi.registry`-
  and `data.statistics`-tagged copies were overwritten mid-run by sibling slices claiming the
  same file under `digital.rural` and other topics. Same reconstruction method: six indicator
  selections recovered from the run's own selected-rows and merged onto one survivor.
- **The CBOS National Instant Payment System RFP** was selected as **baseline** by three
  `dpi.pay` indicators but had been staged under `progress/` by the slice that captured it for
  `gov.standards`/`gov.policy` — moved to `baseline/` at merge per §5's baseline-wins rule,
  the first folder-level move this series has needed for a genuine baseline/progress conflict
  rather than a straightforward duplicate.
- **One duplicate-URL group was correctly *not* merged**: two SCA (Sudanese Cybersecurity
  Authority) news items shared the same generic listing-page URL (no per-article permalink
  existed) but described two distinct dated events six weeks apart (an ICAO PKD certificate
  deposit, and the PKI national root-key launch) — verified by reading both bodies before
  treating the shared URL as a signal to merge, and left as two separate files.

**A regex edge case in the merge script itself corrupted three files' `note:` fields** during
the automated merge — an embedded escaped double-quote (`\"`) inside an original note got
mechanically turned into an invalid `\'` by the topic/note-merge step. Caught by
`lint-staged-queue.py`'s YAML round-trip check immediately after merge and hand-repaired before
anything left this session; final lint clean on that front.

## A systemic lint false-positive, not a content defect

**`lint-staged-queue.py`'s title-matching heuristic cannot handle Arabic-script content.**
Sixteen findings surfaced during the run (falling to 13 after merge); every sub-agent that hit
one manually verified its own files by direct read and found the body's opening heading was
character-for-character identical to the frontmatter `title:` in every case — the checker's
`tokens()` function splits only on `[a-z0-9]` after deaccenting, so it extracts zero tokens from
Arabic text and reports a false "thin title, source not traced" or spurious title-overlap
`CROSSED` against an unrelated file. The parent independently re-verified the two structurally
different-looking findings (the founding ICT-policy-style `CROSSED` pattern from prior runs, and
one `CROSSED` on a scanned/OCR'd Official Gazette PDF) by reading both files' bodies directly —
both confirmed correct. **No genuine crossing, misfiling, or data-integrity defect was found in
this run.** This is a real gap in `scripts/lint-staged-queue.py` worth fixing once the freeze
lifts (2026-09-27) — Sudan is unlikely to be the last Arabic-sourced country this series runs.

## What this run tests

The war shows up as documented degradation and restoration rather than absence: land-registrar
and civil-registry offices closing and later partially reopening in Kassala and Gezira, a
Khartoum state data centre destroyed and being restored, a national payment switch and PKI
root-key launching mid-war from wherever the relevant authority now operates, and Sudan's
digital-ID/CRVS legal architecture (the 2011 Civil Registry Act) still being cited as the live
legal basis for systems that are themselves disrupted. Sudan's DPI payments layer was already
comparatively well-populated going in (`dpi.pay` held 6 ledger rows, the densest single-subject
starting point yet), while `gov.regional`, `gov.discourse`, `finance.mou` and most of `data.statistics`
started at zero and largely stayed thin or nil — a coherent picture of a state maintaining its
core financial-transaction rails under crisis while regional and statistical-cooperation
functions have gone dark.

## Batch status

Staged and **UNDELIVERED** in `C:\corpus-osint-xfer\new-queue\SDN\` (71 baseline + 116
progress) until Bill hand-carries it into OSINT's `new/`.
