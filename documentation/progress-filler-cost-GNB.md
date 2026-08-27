# Progress filler — throughput record, GNB, 2026-08-27

*(The third run of `PROGRESS-FILLER.md`, and the one the AGO record asked for by name:
"a country at 25 rows is a different proposition, and `GNB` is the natural place to test
it." Batch label `progress-filler-GNB-2026-08-27`. Run CSV:
`logs/progress-filler/GNB-2026-08-27.csv`, with the selected and unselected registers
beside it. The filename keeps the word **cost** because `progress-filler-cost-ZAF.md` is
already cited under it; what it records is throughput, and the currency is Bill's week.)*

## The headline

**100 of 100 gaps had evidence to find. Zero nils, for the third country running.** Not
one of the 100 indicators reading ***No evidence*** on the published GNB progress report
was a searched absence; every one was a collection absence. Three countries at three very
different densities — ZAF's 153-row ledger, AGO's 123, GNB's 25 — and the report's legend
has now been shown to be doing real work on every single row it appears on in all three.

**The thin-ledger hypothesis is confirmed, and the number is the dedup rate.** AGO's
constraint was duplication: 32 of its 55 indicators lost at least one candidate to the
mirror's URL index, because Angola's core statutes were already in the vault. GNB lost
**21 of 100** — a fifth against three-fifths. A thin base dedups thinly, which is the
whole of the argument for probing the thin ledgers first. GNB entered this run holding
**25 ledger rows and 21 of 121 indicators**; it is the emptiest country unit in the
corpus bar ERI, and it returned the largest batch the process has produced.

**The substantive finding for the chapter, and it is one finding repeated a hundred
times.** Guinea-Bissau's digital state is almost entirely **donor-authored and stops one
step short of law**. There is no data protection law, no cybersecurity statute, no access
to information law, no e-commerce law, no AI instrument of any kind, no foundational
digital-ID law, no IXP, no government data centre and no disaster-recovery site. What
exists in force is thin and old — *Lei 5/2010* (ICT framework), *Lei 6/2007* (statistics),
a **1967** decree-law still governing civil registration — with a layer of BCEAO, UEMOA
and ECOWAS instruments doing the real regulatory work above it. Almost every substantive
national instrument inside the window exists as a Council of Ministers *projeto* or a
ministerial announcement that could not be evidenced reaching the *Boletim Oficial*. So
for a large part of this batch the most authoritative document that exists is a **draft, a
terms of reference, or a donor project document** — the same shape AGO showed, one stage
earlier.

**And the 26 November 2025 military takeover is visible directly in the evidence**, not
as background. It is the window's sharpest event in the access-to-information rows
(broadcasters silenced, platforms blocked, a January 2026 order on unauthorised press
conferences); it is why the World Bank paused disbursements in January 2026 and resumed
only for existing operations in April; it is why the European Parliament put EU funding
under review; and the World Bank's March 2026 report puts WARDIP disbursement at 13.35%
with committees unreactivated and legal reforms slowed — which is the mechanism by which
those drafts stayed drafts.

## Stage 1 — the sweep (complete)

| | |
|---|---|
| Gaps worked | 100 of 100 (no skips — no prior run) |
| `agent_run` calls | 200 — 2 per gap, `effort: medium` |
| Candidates returned | 1,111 |
| Fetched | 285 |
| Dropped | 57, on `reference.md` §7's closed vocabulary |
| Held back by the cap | 589, recorded with URLs in the unselected register |
| **Staged after the cap** | **259 selections — 97 baseline + 162 progress — over 205 distinct files**, filed as 80 in `GNB/baseline/` and 125 in `GNB/progress/`; **249 over 195 after the ten crossed progress files were withdrawn** — see *A third defect* below |
| Wall clock | ~50 minutes, nine sub-agents concurrent (43 minutes for the slowest) |
| Sessions | one |

**The cap bound hard here, and that is the difference from AGO.** AGO fetched 180 and
staged 134 — only 18 items excluded. GNB fetched 285 and the cap held back 589 leads it
never needed to fetch at all. **The distribution is the evidence**: 65 indicators at the
full 1+2, 26 at 1+1, six at 1+0, three at 0+2. Only nine of a hundred could not fill the
progress side, and only three had no baseline instrument to point at — all three in the
AI family, where the honest baseline is that no instrument exists.

**Drop codes**: `already-seen` 24, `headline-only-stub` 10, `fetch-blocked` 4,
`inadmissible-origin` 4, `off-topic` 3, `out-of-window` 3, `url-dead` 2, `no-development`
2, `duplicate-in-run` 1.

## Two procedure defects fixed in this run rather than sent on

**The counting rule was wrong, and this run retired it.** `PROGRESS-FILLER.md` §6 required
the run CSV to balance against the **file** count, one document to one indicator — so a
document genuinely answering two indicators had to be taken away from one, which is why
AGO needed an escape hatch to stop the arithmetic writing a `nil` it had not searched for,
and why its own summary admitted the counts "understate coverage by exactly this much".
GNB counts **selections, not files**: one survivor per URL, every selected row repointed
at it, nothing decremented. 259 selections over 205 files as staged, cap still auditable per
indicator, no indicator zeroed by bookkeeping, no invented judgement about which
neighbour loses. **The sub-agents got there before the procedure did** — nine recorded a
sibling's existing file in their own selected rows rather than re-staging it, and three
wrote *do not zero these indicators when de-duplicating* into their returns unprompted.

**The flat queue's third showing of the concurrency fault.** Nine sub-agents wrote into
one folder and could not see each other: **31 URLs were staged under more than one slug**
(39 redundant files, removed at merge), and **one true silent overwrite** occurred — a
sibling's capture of the DGCI instruction 25/2025, replaced and unrecoverable. Fourteen
filenames were claimed by more than one indicator and thirteen of those were benign: the
agents had checked the path first and recorded the existing file rather than overwriting
it, which is the §5 instruction working. The fault is now down to what a check cannot
catch, and the residue is one file. **The queue is no longer flat**: from 2026-08-27 a batch is staged as `{ISO}/baseline/` and `{ISO}/progress/`, which halves the namespace each sub-agent writes into but does not remove the fault — two agents can still pick one slug inside one folder, so the check stays.

**Three staging defects were checked before hand-off, two of them on OSINT's report.**
`notes-for-corpus.md` note 14 arrived from OSINT's ingest of the AGO batch during this
run. Unquoted `note:` scalars: **zero** in this batch — the check passed rather than the
defect being absent. ASCII-transliterated Portuguese and French titles over correct UTF-8
bodies: **35 found**, 12 restored here from a line in each file's own body that de-accents
to exactly the same string, 22 left because they need the source URL and are OSINT
housekeeping job 81's. Partial date prefixes, which `reference.md` §3 requires padded:
**10 found and padded**, with `date_precision` left honest. All three checks are now
written into `PROGRESS-FILLER.md` §5.

## A third defect, found after the record was written: fifteen crossed bodies

*(2026-08-27, on OSINT's `notes-for-corpus.md` note 15, opened by its `update-wiki` ingest
of the baseline half of this batch.)*

**Fifteen of the 205 staged files carried another item's verbatim body under their own
frontmatter.** The frontmatter was right, the `url:` was right, the filename was right,
and a URL-index check passed on every one of them. OSINT's ingest found five while reading
full text — three slices found them independently — and its parent-level title-token check
over the other 69 baseline files found no sixth. That check is weak on short titles and it
was checking the wrong half: **ten more sat in the 125 progress items**, which had not been
carried, and this record's own numbers were counting them as delivered evidence.

**What it costs is a falsified finding under a citation that checks out.** The `note:` is
written from the body. GNB's ASYCUDA compendium item asserted that the document recorded
Guinea-Bissau's off-site backup and disaster-recovery architecture — DR site, full
failover, real-time replication, a six-hour delayed standby. Fetched and read, that passage
is **Cambodia's**; Guinea-Bissau appears in the document once, in a list of programme
countries. OSINT deleted the file before ingest, so the claim never entered the base.

**It is one sub-agent, and the evidence says so plainly.** All fifteen fall inside the
eleven `infra.capacity/connect/energy/store` indicators — one slice of the ~10–12
`PROGRESS-FILLER.md` §6 hands to a sub-agent. Of that slice's 29 files, 24 carried the
capture's own `URL:` line in the body and **15 of the 24 were wrong**; across every other
slice, 30 files carried the line and **none was wrong**. The crossings chain rather than
scatter — each file holds the body of the next selection in the slice's order — which is a
shift along a list, the signature of a batch write at the end of a slice rather than a
write as each body is fetched. §6 now says so, and §5 carries the check.

**The check is cheap and it is now a script.** `scripts/lint-staged-queue.py` runs §5's
four checks over a staged batch: the body's own `URL:` line against the frontmatter's
(exact, and it caught all fifteen), then a structural pass for the files that carry no such
line — title tokens against the body, the `url:` host and `publisher:` against it, the
body's own opening heading, and a batch-internal search for whose body a title fits better
than its own. Run against the recovered baseline half it returns the five OSINT found by
hand and one further file — a 522-character UPU postal-addressing profile whose body is too
short to repeat its own title — which is the false-positive rate at this size.

**Disposition.** The ten progress files are **withdrawn from the hand-carry**, recorded in
`logs/progress-filler/GNB-2026-08-27-misfiled.csv` with the frontmatter `url:`, the body's
true one and what the body actually held; their rows are out of the selected register and
the run CSV's `staged_progress` is down to what stands. They were not repaired: the `note:`
on each was written from the wrong body, so the only sound thing in the file is the URL,
and the leads are kept rather than the files. The bodies are recoverable at commit
`3d8b48f` in the share if a later run wants them. **The four `infra.*` progress files
carrying no `URL:` line were read by hand and hold their own bodies.**

**So the numbers in this record are restated.** 249 selections over **195** files, not 259
over 205: **80 baseline** (as carried, of which OSINT deleted two, repaired two and routed
one to acquisition) and **115 progress**. Two indicators are left with nothing admitted at
all once OSINT's dispositions are counted beside the withdrawals —
`infra.connect--mobile-affordability` and `infra.energy--rural-electrification` — and
neither is a `nil`: both were searched, both returned candidates, and the staging was void.
They stay `staged` in the run CSV with the count at zero, and the frame/held difference at
§1 will present them again as gaps on the next pass, which is the correct outcome.

## Capture quality, declared

- **58 of 205 are `body_completeness: excerpt`** — flagged, not retried, per
  `capture-rule.md`. Almost all are large PDFs truncated at the fetcher's character
  ceiling: World Bank appraisal documents, the *Boletim Oficial* gazette scans, the eGIF-GW
  framework, ARN annual reports.
- **44 carry `date_source: proxy`**, each naming its basis in `note`; precision is
  `day` on 163, `month` on 30, `year` on 12.
- **25 files carry a recorded date conflict** in `note` rather than a picked date — a
  materially higher rate than either prior run, and the cause is that a large part of this
  batch is donor PDFs hosted under upload paths that disagree with their own cover dates.
- **Two substantive conflicts a merge cannot settle, recorded for ingest.** *Decreto
  27/2025*, the national interoperability regulation: one batch staged it from WARDIP's
  own article, and a second, working the same object independently, concluded no
  promulgated decree could be evidenced — a draft approved 10 July 2025, a Council decision
  deferred, an adoption claim tracing only to a LinkedIn post. And the UNECA DTRI country
  profile is undated, with one capture bounding it to 2023 and the other to 2024-or-later
  from a BCEAO instruction it cites; it is filed at a padded `2023-01-01` floor with both
  bounds in the note.
- **A claim that appears to be unfounded, and is worth a correction rather than a
  source.** A widely repeated statement that Guinea-Bissau enacted *Lei n.º 10/2021* on
  data protection and *Lei n.º 11/2021* creating a data protection authority could not be
  verified against any primary or institutional source. Every authoritative document
  located says the opposite — that the country has no data protection law. It is flagged
  in the staged notes.
- **Fetch routes that defeated us**, and may defeat ingest too: `arn.gw` publishes its
  Q3 and Q4 2025 market observatories **as slide images with no text body**, so the mobile
  and market baselines fall back to Q2 2025; `imf.org` news-article pages and
  `documents.worldbank.org` detail pages render bodies via JavaScript (the PDF and
  `documents1.worldbank.org/…/txt/` paths work); `cyberportal.ecowas.int`,
  `paloptl-ebudgets.org` and the UN treaty-body document viewers return loading stubs;
  `kontaktu.mef.gw` serves UTF-8 without declaring it, so it was taken by `curl` rather
  than the fetcher. Two PDFs carry unmappable CID fonts and one gazette scan has a
  corrupted text layer past Article 6.
- **Three origin adjudications**, all `watch`, none `drop`: `gov-gb.com` (declares itself
  a prototype carrying fictitious data), `fbgroup.com.tr` and `funiber.org.br` (each
  primary for its own document, neither a publisher). They are in the share's
  `progress-filler-drop-list.csv` and note 48 carries them to OSINT as an `[ACT]`.

## Stages 2–4 — not yet run

- **Stage 2 — the stage 4 read.** Pending Bill's hand-carry of `new-queue/` into
  `OSINT\new\`, `update wiki`, and the mirror refresh.
- **Stage 3 — the mapping.** `outputs/reports/GNB/indicators.csv` rewritten by hand
  against `documentation/indicator-mapping-conventions.md`.
- **Stage 4 — the render.**

**Yield is stated when stage 3 lands**, as gaps closed against the 100 probed and against
sessions spent. On ZAF the sweep closed 43 of 44.

## What this says about scheduling — and the number that has changed

**This is the batch to be careful with.** 205 documents is roughly **one and a half
nights of daily sweep**, handed to a system whose scarce resource is exactly that. ZAF
sent 126, AGO 134; this is a step up, and it is a step up because the country is empty,
not because the run was loose — the cap held back 589 leads.

**The recommendation was to split the hand-carry, and Bill made it the layout the same
day.** A filler batch is now staged as `new-queue/{ISO}/baseline/` and
`new-queue/{ISO}/progress/` rather than one flat pile — **GNB is 80 and 125** — so carrying
one half and not the other is a folder move rather than a sort of 205 files by hand.
`PROGRESS-FILLER.md` §5 carries the rule and the share's `README.md` states it for both
sides.

**Baselines first is the recommendation inside that split.** They are the instruments, the
standing positions and the statements of absence — the layer the progress items attach to,
and the half that does not age. Deferring the movement layer costs the report its most
recent month and nothing structural. **The file counts and the selection counts differ and
both are right**: 97 baseline selections over 80 files, 162 progress selections over 125
(152 over 115 after the withdrawals),
because five documents answer one indicator's baseline and another's progress and are
staged once, under `baseline/`. Trading coverage for a week remains Bill's call, not the
run's; what has changed is that the trade is now cheap to make.

**The AGO question is answered and it changes the priority order.** AGO asked whether the
filler buys less where the base is already dense. It does: three-fifths of AGO's
indicators lost their first-choice baseline to the index against a fifth of GNB's. **So
probe the thin ledgers first** — they dedup less, they yield more per brief, and the
indicators they fill are the foundational ones a dense country already holds. On the
corpus as it stands that means ERI (13 held), STP (27), SDN (29), SYC (34) and SOM (37)
ahead of the KEN/CIV/NGA end of the range, where 28 or 29 gaps remain and most of what a
brief would find is already in the vault.

**The counter-consideration, stated because it is real.** A thin ledger yields a large
batch, and a large batch is the thing that displaces sweeps. Probing the thin countries
first maximises what the filler buys per brief and simultaneously maximises what it costs
OSINT per run. The two do not point the same way, and the lever between them is §4a's cap
rather than the country order.
