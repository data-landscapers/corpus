# Progress filler — throughput record, MUS, 2026-09-01

*(The twenty-ninth run of `PROGRESS-FILLER.md`, and the first against Mauritius — no prior
MUS run, so §0's skip found nothing to carry forward. Batch label
`progress-filler-MUS-2026-09-01`. Run CSV: `logs/progress-filler/MUS-2026-09-01.csv`, with the
selected and unselected registers beside it.)*

## The headline

**71 of 71 gaps had evidence to find. Zero nils.** A mid-sized frame for this series (COM's 76
and DJI's 78 are the widest so far), against a ledger that already held 86 rows before this run
— the densest starting point of any country worked yet, reflecting Mauritius's comparatively
mature digital-government record.

**51 of 71 indicators closed at the full 1 baseline + 2 progress.** Three closed with no
baseline at all (`gov.regional--regional-legal-harmonisation` — Mauritius is not an OHADA
member and no positive regional-harmonisation instrument exists; `dpi.exchange--use-of-digital-id-in-other-systems`
and `dpi.pay--g2p-functionality` — both baseline briefs returned only already-mirrored
material, so those indicators stand on progress evidence alone), each a genuine finding rather
than a padded gap. One (`include.access--inclusion-of-refugees-and-idps`) closed baseline-only
by design: Mauritius has no refugee/IDP framework, and the CERD concluding observations
documenting that dated absence *is* the baseline; the two candidate progress items found
(cyclone-evacuee logistics, an IOM migration MoU) were correctly judged off-topic rather than
stretched to fill the cap.

## Stage 1 — the sweep (complete)

| | |
|---|---|
| Gaps worked | 71 of 71 (no skips — no prior MUS run) |
| `agent_run` calls | 142 — 2 per gap, `effort: medium` |
| Candidates returned | 450 |
| Fetched | 205 |
| Dropped | 12 — `already-seen` 7, `fetch-failed` 2, `thin-capture` 2, 1 uncoded (a candidate excluded on relevance rather than a closed-vocabulary reason) |
| Held back by the cap | 86, recorded with URLs in the unselected register (12 with a stated `why_not`; the remainder were pre-fetch triage choices the sub-agents resolved without a separate fetch, per each slice's notes) |
| **Staged after the cap and cross-slice merge** | **192 selections — 68 baseline + 124 progress — over 145 distinct files**, filed as 59 in `MUS/baseline/` and 86 in `MUS/progress/` |
| Batch size on disk | ~10.8 MB |
| Sessions | one |

## Slicing and cross-slice dedup

**Six slices, grouped by Level-1 with small chapters merged to fill a batch**: Governance (14
gaps); Finance + ICT Infrastructure (11); DPI split in two — Data Exchange + Digital Identity
and CRVS + Digital Payments and Fintech (12), and Registries + Sectoral MIS (11);
Digitalisation + Technology + Capacity (13); Inclusion + Data (10).

**22 cross-slice URL duplicates, all caught and resolved at merge** — the widest count of this
series so far, tracking the widest gap list run in one sitting. Mauritius's own institutions
publish a small number of omnibus documents (the Budget Speech, its Annex, the PSIP, the
National Data Strategy, the Sovereign Cloud RFI Clarification) that genuinely answer several
indicators across different Level-1 chapters at once, and six independent slices working in
parallel could not see each other's fetches. Applied §6's rule mechanically: **one survivor per
URL, `full` kept over `excerpt`, the larger capture kept as tiebreak, and baseline wins** —
where any slice had staged the document as somebody's baseline, that copy survived regardless
of what another slice's brief had called it. 37 redundant files were removed; every affected
selection was repointed at the survivor and the survivor's `topics:` list was widened to the
union of every indicator's Topic L2 that cites it. The widest single case: the Budget Speech
2026-2027 answered `tech.innovate`, `dpi.pay`, `include.access` and `dpi.registry` progress
picks from three different slices; its Annex separately answered `dpi.id`, `include.access` and
`data.open`. The ICT Statistics 2025 release answered four `infra.connect` baselines plus
`digital.rural`'s and `data.statistics`'s — a single annual survey publication legitimately
grounding five indicators' baselines/progress at once.

**No crossed-body defects.** `scripts/lint-staged-queue.py` found zero `MISFILED`, `CROSSED` or
`SUSPECT` findings across all 145 files — every slice staged one file per fetched body,
write-as-you-go, per §6. What it did find, all fixed at merge:

- **9 files with an unescaped apostrophe inside a single-quoted YAML scalar** (`Registrar-General's`,
  `L'Express`, `Mauritius' drive`, `HEC's guidelines`, `Cote d'Or`, `Business Mauritius exhorte
  a reduire...d'electricite`) — a `'` inside a single-quoted YAML string must be doubled (`''`)
  or the frontmatter fails to parse. Fixed mechanically across the whole batch by doubling any
  bare apostrophe found inside a `key: '...'` line; verified every file re-parses.
- **1 filename/`published:` date mismatch** — the Fintech Strategy capture was filed under a
  `2026-06-22` prefix (the day it was fetched) against its own cover date of `2026-05-22`
  (Cabinet endorsement); renamed to the correct prefix per `reference.md` §3.
- **5 ASCII titles with the accented French/Creole form present in their own bodies** — restored
  from each file's own text (`Communique` → `Communiqué`, `electricite/reduire` →
  `électricité/réduire`, `collectivites` → `collectivités`, `apres/complete` → `après/complète`),
  both in `title:` and in the injected `# Publisher | Title` heading line. One case
  (`Communiqué du Bureau du Commissaire Electoral`) was only partly restored: the source PDF's
  own header repeats "Commissaire Electoral" / "Enregistrement des Electeurs" unaccented in two
  independent places while its running prose uses `électeur(s)` correctly, which reads as the
  PDF's own header-rendering quirk rather than a transliteration this run introduced — the
  `Communique` → `Communiqué` word (attested twice in the body's own headings) was fixed; the
  proper-noun heading fragments were left as the source itself renders them.

`scripts/lint-staged-queue.py` reports **clean** over both folders (145 files) after these
fixes. 192 selections resolve to exactly 145 files on disk, verified programmatically: zero rows
pointing at a missing file, zero orphan files, zero cap violations under either per-brief or
per-folder counting.

## Capture quality, declared

- **107 of 145 are `body_completeness: full`, 38 `excerpt`** — flagged, not retried, per
  `capture-rule.md`. Excerpts are concentrated in long omnibus PDFs (Budget Speech and Annex,
  PSIP, Finance Act 2026, several ministry annual reports) truncated at the fetch tool's
  character ceiling; in every case checked, the cited passage was confirmed present before
  staging.
- **129 of 145 carry `date_source: source`, 16 `proxy`.** Precision is `day` on 124, `month` on
  15, `year` on 6.
- **The three largest files**: Mauritius's 11th Periodic Report to the ACHPR (245 KB), the
  Assises de l'Agriculture 2026 satellite-monitoring proceedings (225 KB), and the Mauritius
  Standards Bureau Annual Report 2021/2022 (148 KB).
- Two genuine fetch failures (both logged, not padded): the CSD system-revamp communique on a
  second attempt for `dpi.id--digital-id-from-birth` (`CRAWL_NOT_FOUND`), and the PMO Cabinet
  Highlights of 13 February 2026 for `tech.ai--use-of-ai-in-government-administration`
  (repeated timeout, then a 404 on a malformed URL) — the latter substituted with the FAIR
  Guidelines PDF, an adequate primary in its own right.
- One extraction defect caught and fixed **before** finalising, not after: slice 3 (DPI-A)
  found its own backward-search window for splitting a multi-URL Exa fetch batch was too small,
  causing some early draft bodies to start mid-sentence; all 31 of that slice's files were
  re-verified to open at their true document start before being reported.

## Origin adjudications — none

**Zero new watch/drop rows.** All six slices reported every screened domain as either already
known to the mirror or `NOVEL`; `progress-filler-drop-list.csv` is unchanged from the COM/DJI/ERI
run — still the same rows carried from earlier countries. This run's `notes-for-osint.md` entry
is a plain `[FYI]`.

## Stages 2–4 — not yet run

- **Stage 2 — the stage 4 read.** Pending Bill's hand-carry of `new-queue/MUS/` into
  `OSINT\new\`, `update wiki`, and the mirror refresh.
- **Stage 3 — the mapping.** `outputs/reports/MUS/indicators.csv` rewritten by hand against
  `documentation/indicator-mapping-conventions.md`.
- **Stage 4 — the render.**

**Yield is stated when stage 3 lands**, as gaps closed against the 71 probed and against
sessions spent.
