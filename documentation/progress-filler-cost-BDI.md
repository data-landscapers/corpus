# Progress filler — throughput record, BDI, 2026-08-28

*(The fourth run of `PROGRESS-FILLER.md`, and the first at mid-density. Batch label
`progress-filler-BDI-2026-08-28`. Run CSV: `logs/progress-filler/BDI-2026-08-28.csv`, with
the selected and unselected registers beside it. The filename keeps the word **cost**
because `progress-filler-cost-ZAF.md` is already cited under it; what it records is
throughput, and the currency is Bill's week.)*

## The headline

**78 of 78 gaps had evidence to find. Zero nils, for the fourth country running.** Not one
of the 78 indicators reading ***No evidence*** on the published BDI progress report was a
searched absence; every one was a collection absence. Four countries at four densities —
ZAF's 153-row ledger, AGO's 123, BDI's 77, GNB's 25 — and the report's legend has now been
shown to be doing real work on every row it appears on in all four.

**Every indicator got a baseline.** 78 of 78, where GNB left three without one and had to
say so. The distribution is 47 indicators at the full 1+2, 23 at 1+1, and 8 at 1+0 — so
only eight of seventy-eight could not fill the progress side, and none failed on the
baseline. That is the densest cap fill the process has produced.

**The mid-density prediction from the GNB record is confirmed.** GNB argued that thin
ledgers dedup thinly and should therefore be probed first. BDI entered with **77 ledger rows
and 43 of 121 indicators held** — squarely between AGO's 123 and GNB's 25 — and lost **14
candidates to `already-seen`** against GNB's 21 over a hundred indicators, and against AGO's
much heavier loss of a first-choice baseline on three-fifths of its rows. Per indicator the
dedup rate lands between the two, which is what the hypothesis said it would do. The country
order argument stands.

**The substantive finding for the chapter, and it is one finding stated four different
ways.** Burundi **legislates and plans at the centre, and does not build at the edge**.
The instruments are real and recent: a cybercrime law in force since 2022, a national
payment system statute, an electronic communications code of 2024 carrying e-commerce, a
data protection law promulgated 10 March 2026, a data governance strategy validated in
November 2025 and a six-pillar AI strategy in April 2026. What sits under them is thin.
There is **no national data exchange layer** — the government's own project safeguards
document says so in terms. There is **no national population register**, and the state's
Isôko portal says the instituting texts are still to be adopted. There is **no address
register**, **no shared government data centre**, **no national case-management system for
justice**, **no interoperability framework**, and **no AI in operational use in government
administration**. Broadband reaches commune level; the commune-level services do not exist.
DHIS2 reaches the health centre; the health centre still compiles on paper.

**Two numbers must not be merged, and a report that merges them says something false.**
ARCT's Q4 2025 observatory gives **29.26% internet penetration** on 3,609,308
subscriptions; ITU and the World Bank put **individuals actually using the internet at 8.6%
(2024)**. One counts subscriptions, the other counts people. The gap is the story.

**Two widely-cited external readings of Burundi are now demonstrably out of date**, and the
batch carries the primary sources that retire them. The Council of Europe's Octopus profile
still describes only the pre-2022 Penal Code, when *Loi n°1/10 du 16 mars 2022* on
cybercrime has been in force for four years and is marked *En vigueur* on the state legal
database. And the UNCTAD/UNECA "no e-transactions law" position is a 2021 reading:
e-commerce is legislated inside *Loi n°1/22 du 22 août 2024*, which ARCT operationalised
in-window with ecosystem guidelines on 2026-05-29 and a compulsory conformity declaration
for platforms on 2026-06-26.

## Stage 1 — the sweep (complete)

| | |
|---|---|
| Gaps worked | 78 of 78 (no skips — no prior BDI run) |
| `agent_run` calls | 156 — 2 per gap, `effort: medium` |
| Candidates returned | 678 |
| Fetched | 239 |
| Dropped | 59, on `reference.md` §7's closed vocabulary |
| Held back by the cap | 287, recorded with URLs in the unselected register |
| **Staged after the cap** | **195 selections — 78 baseline + 117 progress — over 141 distinct files**, filed as 58 in `BDI/baseline/` and 83 in `BDI/progress/` |
| Batch size on disk | 8.2 MB |
| Wall clock | ~38 minutes, eight sub-agents concurrent (37.6 for the slowest) |
| Sessions | one |

**Drop codes**: `already-seen` 14, `headline-only-stub` 9, `off-topic` 9, `fetch-blocked` 6,
`duplicate-in-run` 5, `out-of-window` 4, `inadmissible-origin` 4, `no-development` 3,
`url-dead` 2.

**The cap bound moderately.** 239 fetched against 287 held back — roughly one lead excluded
for every one fetched, where GNB excluded two for every one and AGO excluded almost none.
That ratio is the density signal in its cleanest form: at 77 ledger rows there is enough in
the vault to dedup against and enough missing to be worth fetching.

## The concurrency fault did not recur, and that is the news

**Zero silent overwrites, and zero crossed bodies.** GNB's run produced one unrecoverable
overwrite and fifteen files carrying a neighbour's verbatim body — the defect that arrives
as a falsified finding under a citation that checks out. This run produced neither. The
merge audit of selected rows against files on disk returned **0 rows pointing at a missing
file, 0 files with no selected row, and 0 filenames claimed by rows meaning different
documents**; `scripts/lint-staged-queue.py` returned two findings over 141 files and both
are documented false positives (below).

**Three things changed between the runs and all three appear to have worked.** The
`baseline/`/`progress/` split halved the namespace each sub-agent writes into. §5's
instruction to check the path before writing was followed — several slices recorded a
sibling's existing file in their own selected rows rather than overwriting it, exactly as
GNB's agents had started doing unprompted. And §6's *write as each body is fetched* is now
in the procedure rather than inferred: every slice reported writing one file per fetch, and
one slice cross-checked its own register against its files and found zero URL, date, batch
or place mismatches.

**One residual collision, and it is in the scratchpad rather than the queue.** Two slices
wrote a helper named `stage.py` into the shared scratchpad and one overwrote the other
mid-run. No body was mis-filed — the slice that was overwritten verified its captures — but
the fix is trivial and was applied during the run: helper scripts are now slice-keyed
(`fetchstage-dpi-a.py`, `ocr-infra.py`). Worth writing into the briefing next time rather
than discovering again.

## Cross-queue dedup — the parent's pass

**21 URLs were staged more than once, across 45 files; 24 redundant captures were
removed**, leaving 141. Every one is a concurrent-sibling collision invisible at write
time, and five slices reported theirs unprompted rather than leaving them to be found. The
survivor was chosen by §5 and §6's rules: **baseline wins over progress** (four pairs,
including the UNDP AI roadmap and the World Bank social-protection results page), then the
fuller body. **Selections were repointed, not decremented** — 28 rows moved onto survivors
and no indicator lost a selection to bookkeeping, which is the rule GNB's run put into the
procedure.

**Four date conflicts were recorded in the survivor's `note` rather than settled**, per §6:
the ACO census page (workshop date in the body against the page's own post date), the ARCT
2024 indicators report (cover month against web date), the INSBU open licence (a Wayback
first-capture proxy against a second capture that had used the retrieval date, which is not
a publication date at all), and the MININTER page (a body-stated *"En date du 12 mars"*
against the page's 16 March). Ingest settles each with the document in hand.

**The batch was committed before the dedup pass**, at `41ce4fd` in the share, so the 24
discarded captures are recoverable if a later run wants them.

## Capture quality, declared

- **13 of 141 are `body_completeness: excerpt`** — flagged, not retried, per
  `capture-rule.md`. 128 are `full`. That is a materially better ratio than GNB's 58 of 205,
  and the reason is that fewer of this batch are large donor PDFs.
- **27 carry `date_source: proxy`**, each naming its basis in `note`; precision is `day` on
  118, `month` on 18, `year` on 5.
- **21 files record a conflict in `note` rather than a picked value**, four of them written
  by the merge pass above and the rest by the slices.
- **46 files carry a note about a scan or OCR limit**, which is the single defining
  constraint of Burundian sourcing and is treated on its own below.
- **Two lint TITLE findings, both verified false positives, both left alone.** The ARCT Q4
  observatory's title is genuinely all-caps and unaccented on the PDF cover *and* the ARCT
  landing page, with no mixed-case accented form anywhere in the body. The ONPRA/UNHCR
  communiqué's title is unaccented in **both** the English and French locales of UNHCR's own
  record, verified on the day. Each file carries the reasoning in its own `note`, so the
  explanation travels with the document instead of living only in this record.

## The constraint that defines Burundi as a source country

**Burundian primary law is published as image-only scans with no text layer.** This is not
an occasional failure; it is the norm, and it cost this run more than any other single
factor. *Loi n°1/03* of 2026 (data protection), *Loi n°1/07* of 2018 (payments), *Loi
n°1/22* of 2024 (electronic communications), *Décret 100/085* of 2018, the OBR constituting
law, the tax procedures law, the Umutangakori and electronic-land-title ordonnances, the
ARCT e-commerce guidelines and the census arrêté all returned **zero characters** from
`pdftotext`, pdfminer and pypdf alike. Three routes were found and all three are worth
keeping:

1. **`amategeko.gov.bi`'s *Bulletin Officiel* issues do carry text layers**, and that is how
   the 2022 cybercrime law and the 2021 statistics law were captured in full. Its search and
   most `laws_and_other_acts` slugs return HTTP 500, so a BOB issue is reachable only by a
   link someone already holds. **This is the single most valuable finding for future Burundi
   work.**
2. **A local OCR route** — pypdfium2 at 300 dpi plus tesseract `fra` — was built by the
   infra slice and staged five decrees through it, each naming its observed character errors
   in `note` (the IXP decree's header survives as `N° 1001222 DU 75 MAI 2014`). Honest and
   citable; not clean.
3. **FAOLEX's OCR copies**, used where they are good (the Code de commerce) and refused
   where they are not (the Code foncier, degraded to "droits forc ers"), with the land
   baseline moved to a clean technical manual instead.

**Where none worked, the item is staged as `excerpt` with an explicit capture-failure note
and routed to manual clip** rather than padded or dropped. Three high-value instruments have
citations and no bodies: *Loi n°1/03*, *Loi n°1/07* and *Loi n°1/22*.

**A second, smaller obstacle: `.bi` DNS.** A large part of the Burundian government estate —
`abpinfo.bi`, `finances.gov.bi`, `arct.gov.bi`, `rtnb.bi`, `mininterinfos.gov.bi`,
`ceniburundi.bi` — does not resolve through this machine's resolver but is alive on
**41.79.224.90** over DoH. Four slices hit it independently and worked around it; the fix
was broadcast mid-run. **Nothing was coded `url-dead` on this fault**, and one slice
re-fetched its three affected captures pinned to the real IP and verified them line by line
against what it had staged. The one genuine NXDOMAIN is `mintic.gov.bi`, whose PNDTIC copy
was recovered from the Primature.

**Other routes that defeated or nearly defeated us**: `bbs.bi` — the national backbone
operator — serves `/cgi-sys/suspendedpage.cgi` on every path, so its June 2026 core-network
tender is unretrievable; `insbu.bi` is a JS app serving 93 characters to a plain fetch but
**full bodies through Exa**, which is worth knowing before routing around it; `undp.org`
returns 403 to requests and curl but 200 to the Exa crawler; `regideso.bi` and `obr.bi`
return 500 and a Joomla error to curl and serve fine to Exa; `isoko.gov.bi` serves an
**expired TLS certificate**; `open.enabel.be` and the BBN catalogue are JS-only; and
**LinkedIn is a hard block**, which cost the standards row BBN's own claim of 21 new
Burundian standards.

## Origin adjudications — four rows, and the note is an `[ACT]`

Four rows were appended to `C:\corpus-osint-xfer\progress-filler-drop-list.csv`:
`readkong.com` and `kamdem.blogspot.com` as **drop** (a document-sharing content farm and a
personal blog reposting project material, neither with publisher control), `idate.fr` and
`pcdn.co` as **watch** (a consultancy publishing its own commissioned mandates as news; a
CDN alias that should always be resolved to its canonical publisher host). Nothing was
staged from any of them. Five slices screened and adjudicated nothing, which is the expected
shape.

## Stages 2–4 — not yet run

- **Stage 2 — the stage 4 read.** Pending Bill's hand-carry of `new-queue/BDI/` into
  `OSINT\new\`, `update wiki`, and the mirror refresh.
- **Stage 3 — the mapping.** `outputs/reports/BDI/indicators.csv` rewritten by hand against
  `documentation/indicator-mapping-conventions.md`.
- **Stage 4 — the render.**

**Yield is stated when stage 3 lands**, as gaps closed against the 78 probed and against
sessions spent. On ZAF the sweep closed 43 of 44.

## What this says about scheduling

**141 documents is about one night of daily sweep**, against GNB's 205 and AGO's 134. It is
the cheapest batch per gap closed the process has produced, because the cap filled almost
completely: 195 selections over 78 indicators is 2.5 per gap, where GNB managed 2.49 over a
hundred and needed 205 files to do it. **Fewer files, denser coverage** — the mid-density
country is the efficient one to probe, which neither the AGO nor the GNB record predicted.
It does not overturn GNB's *probe the thin ledgers first* recommendation, which was about
yield per brief; it adds that the cost side of that trade is worst at the thin end, because
a thin ledger buys its coverage with more files.

**The split still works and is still the lever.** 58 baseline against 83 progress: carrying
the baselines alone is a folder move that delivers every one of the 78 indicators' standing
instruments and defers only the movement layer. That remains the right trade when a week
tightens, and it remains Bill's call rather than the run's.

**One caution specific to this batch.** Three files carry 4.3 MB of the 8.2 MB total —
EDSB-III at 3.3 MB, ENIF 2024 at 605 KB, the World Bank digital economy assessment at
354 KB. EDSB-III is the primary publication of Burundi's 83.5% birth-registration figure and
the only sex-disaggregated device-ownership source in the country, so it earns its place;
but if ingest wants a lighter night, those three are where the weight is.
