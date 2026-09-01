# Progress filler — throughput record, SYC, 2026-09-01

*(The thirtieth run of `PROGRESS-FILLER.md`, and the first against Seychelles — no prior
SYC run, so §0's skip found nothing to carry forward. Batch label
`progress-filler-SYC-2026-09-01`. Run CSV: `logs/progress-filler/SYC-2026-09-01.csv`, with the
selected and unselected registers beside it.)*

## The headline

**87 of 87 gaps had evidence to find. Zero nils.** The widest gap list of this series so far
(COM's 76 and DJI's 78 were the previous widest; MUS's ledger was denser but its frame carried
71 gaps), against a ledger that held only 56 rows before this run — a much thinner starting
point than Mauritius's 86, reflecting a smaller island administration with less digital-
governance documentation already on record. That combination — wide gap list, thin prior
ledger — made this the largest single-country probe run yet: 174 Exa Agent briefs, 626
candidates, 224 fetches, 216 selections.

**50 of 87 indicators closed at the full 1 baseline + 2 progress.** Ten closed on partial
evidence, each a genuine finding rather than a padded gap: seven closed baseline-only —
`gov.policy--data-interoperability-framework-roadmap`, `infra.connect--international-internet-bandwidth`,
`infra.connect--internet-exchange-points` (no IXP-specific movement in-window, a small
single-exchange market), `dpi.id--interoperability-of-birth-registration-and-digital-id`,
`dpi.mis--land` (LMAIS still in procurement, no operational movement yet),
`digital.localgov--ict-infrastructure-for-local-government` and
`digital.localgov--digitalisation-of-local-government-records` (Seychelles is a small unitary
state with limited devolved local-government apparatus to document); three closed with no
baseline at all — `dpi.exchange--national-data-exchange-system`, `tech.ai--development-of-national-regional-ai-systems`,
and `tech.innovate--tech-startup-ecosystem` — where both baseline briefs returned only
already-mirrored or non-qualifying material and the indicator stands on progress evidence
alone.

## Stage 1 — the sweep (complete)

| | |
|---|---|
| Gaps worked | 87 of 87 (no skips — no prior SYC run) |
| `agent_run` calls | 174 — 2 per gap, `effort: medium` |
| Candidates returned | 626 |
| Fetched | 224 |
| Dropped | 63 — `already-seen` 36, `fetch-blocked` 3, `no-development` 3, `url-dead` 2, `inadmissible-origin` 2, `headline-only-stub` 2, `duplicate-in-run` 1, `off-topic` 1, plus a small number of pre-fetch triage exclusions several slices resolved without a separate fetch (not separately coded, per each slice's own account) |
| Held back by the cap | 11, recorded with URLs in the unselected register |
| **Staged after the cap and cross-slice merge** | **216 selections — 84 baseline + 132 progress — over 161 distinct files**, filed as 70 in `SYC/baseline/` and 91 in `SYC/progress/` |
| Batch size on disk | ~1.36 MB |
| Sessions | one |

One gap indicator — `finance.budget--sustainable-domestic-financing-of-digital-transformation`,
the sole member of the Finance Level-1 chapter — was dropped during initial slice assignment
(an off-by-one error merging Finance into a Governance slice) and caught only at merge, when the
run CSV came up one row short of 87. It was searched and staged directly by the parent run
before the batch closed, on the same two-brief protocol as every other gap: baseline is the
enacted Appropriation Act 2026 (R93.813M to DICT, the ICT department line), progress is the
National Assembly Administration Act 2026 (new parliamentary IT/cybersecurity office and
financial-autonomy framework) plus the Cabinet-approved Judiciary Digitalization Programme and
Government Service Centre (shared with two Governance indicators; approved but not costed).

## Slicing and cross-slice dedup

**Eight slices, grouped by Level-1 with small chapters merged to fill a batch**: Governance
split in two (11 + 10 gaps, the second absorbing the misassigned single Finance gap that in the
event was not delivered to any slice — see above); ICT Infrastructure (12); DPI split in two —
Data Exchange + Digital Identity and CRVS (11), and Digital Payments and Fintech + Registries +
Sectoral MIS (12); Digitalisation + Technology (12); Capacity + Inclusion (10); Data +
Geopolitics (8).

**18 cross-slice URL duplicates, all caught and resolved at merge** — the widest count of this
series, tracking the widest gap list run in one sitting (MUS's 22 came from six slices over 71
gaps; this run's 18 came from eight slices over 87). Seychelles' small institutional footprint
concentrates a lot of evidence in a few omnibus sources — Cabinet Business bulletins that report
several unrelated decisions in one page, the National AI in Education Framework PDF (cited by
five different indicators across three Level-1 chapters), joint India-Seychelles state-visit
announcements — that independent slices working in parallel could not see each other stage.
Applied §6's rule mechanically: **one survivor per URL, `full` kept over `excerpt`, the larger
capture kept as tiebreak, and baseline wins** — where any slice had staged the document as
somebody's baseline, that copy survived regardless of what another slice's brief had called it,
with its `topics:` widened to the union of every indicator's Topic L2 that cites it. The widest
single case: the 18 February 2026 Cabinet Business bulletin was independently staged three
times, answering `gov.policy--broadband-strategy` (Starlink ISP licence), `dpi.exchange--interoperability-of-health-systems`
(Health Care Agency repeal/absorption into MoH) and `geopol.usa--usa-hyperscaler-mous-engagements-and-commitments`
(the same Starlink licence, read as a US-hyperscaler engagement) from three different slices in
one sitting. A second merge pass caught one further duplicate the slices' own dedup missed
entirely: the AU/STATAFRIC statistical peer-review press release was staged under two visibly
different filenames by two different slices, discovered only when the selected-register merge
found a citation pointing at a file that did not exist on disk — the surviving file's `topics:`
was widened to cover all three indicators that cite it (`data.statistics`, `gov.legislate`,
`gov.policy`).

**Zero crossed-body defects.** `scripts/lint-staged-queue.py` found zero `MISFILED`, `CROSSED`
or `SUSPECT` findings across all 161 files, both before and after the merge's file deletions and
topic-list rewrites. The one YAML parse failure surfaced during the finance.budget backfill (an
undoubled apostrophe in `Act's` inside a single-quoted `note:` scalar) was caught and fixed
before the batch was declared clean.

## Capture quality, declared

- **119 of 161 are `body_completeness: full`, 38 `excerpt`, 4 `paywalled`** — flagged, not
  retried, per `capture-rule.md`. Excerpts concentrate in long omnibus PDFs (the National AI in
  Education Framework, several Cabinet-bulletin and gazette captures, the National Assembly
  Administration Act 2026) truncated at the fetch tool's character ceiling.
- **136 of 161 carry `date_source: source`, 25 `proxy`** (institutional "about" pages with no
  visible publication date, dated to year of capture as an explicit `proxy`, per
  `capture-rule.md`'s guidance that a blank/proxy date is honest where the page itself gives no
  better evidence). Precision is `day` on 129, `month` on 17, `year` on 15.
- **The three largest files**: the Land Registration Act (Cap. 107) at 96.7 KB, the Spatial Data
  Sharing Policy at 63.6 KB, and the Electronic Transactions Act 2001 at 59.3 KB — all long
  consolidated statutes captured in full.
- Fetch failures were logged, not padded, and substituted with an adequate primary in each
  case: the Information Commission's 10.31 MB Annual Report 2025 PDF (HTTP 500 on both the Exa
  route and a DoH-verified pinned `curl` retry — a server-side fault, not a block); the Bureau of
  Standards Act 2014 (SeyLII's embedded PDF viewer failed, direct-PDF-URL guesses 404'd); the
  PUC 2024 Annual Report (`CRAWL_HTTP_500` on retry, substituted with the 2023 report as baseline
  for two indicators); a claimed CERT-In/DICT cybersecurity MoU PDF that returned scrambled OCR
  text from a scanned document; and a SADC Financial Inclusion Forum report whose claimed
  CBS/SeyID KYC-recognition detail could not be corroborated in the fetched text and was left
  unstaged rather than asserted on medium confidence.

## Origin adjudications — none

**Zero new watch/drop rows.** All eight slices reported every screened domain as either already
known to the mirror or `NOVEL` (report-only, not a gate); `progress-filler-drop-list.csv` is
unchanged from the MUS run. This run's `notes-for-osint.md` entry is a plain `[FYI]`.

## Stages 2–4 — not yet run

- **Stage 2 — the stage 4 read.** Pending Bill's hand-carry of `new-queue/SYC/` into
  `OSINT\new\`, `update wiki`, and the mirror refresh.
- **Stage 3 — the mapping.** `outputs/reports/SYC/indicators.csv` rewritten by hand against
  `documentation/indicator-mapping-conventions.md`.
- **Stage 4 — the render.**

**Yield is stated when stage 3 lands**, as gaps closed against the 87 probed and against
sessions spent.

## Process note — the dropped slice

This run surfaced a delegation-pipeline defect worth recording for future runs: writing eight
parallel sub-agent slice assignments by hand from a 10-11-gap-per-slice plan is exactly the kind
of manual bookkeeping a single dropped row survives silently until the merge step counts rows
against the frame. The catch here worked as designed — the parent's post-merge row count
(86 against an expected 87) caught the gap before the batch was declared finished — but the
right fix for a run this size is to generate slice assignments from the gap CSV programmatically
rather than transcribe them, so the count is correct by construction rather than by audit.
