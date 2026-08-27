# Progress filler — throughput record, AGO, 2026-08-27

*(The second run of `PROGRESS-FILLER.md`, and the first under the §4a cap and the §2 objective
form that the ZAF run produced. Batch label `progress-filler-AGO-2026-08-27`. Run CSV:
`logs/progress-filler/AGO-2026-08-27.csv`, with the selected and unselected registers beside it.
The filename keeps the word **cost** because `progress-filler-cost-ZAF.md` is already cited under
it; what it records is throughput, and the currency is Bill's week.)*

## The headline

**55 of 55 gaps had evidence to find. Zero nils, for the second country running.** Not one of the
55 indicators reading ***No evidence*** on the published AGO progress report was a searched
absence; every one was a collection absence. Two countries is not a pattern, but it is now the
second time the report's legend — *"a statement about this base, not about the country"* — has
been shown to be doing real work on every single row it appears on.

**What is new is how much of Angola the base already holds.** ZAF's constraint was volume; AGO's
was duplication. **32 of the 55 indicators lost at least one candidate to the mirror's URL index**,
and the losses fell disproportionately on the obvious baselines — Lei 22/11, Lei 23/11, Lei 40/20,
Lei 7/17, Lei 6/15, DP 214/16, DP 256/25, DP 258/25, DP 263/25, the World Bank ID4D diagnostic, the
MINTTICS AI bill. Angola's core statutes are in the vault. What the filler added was the layer
under them: implementing decrees, regulator avisos, and the IMA/PADA terms of reference by which
the state is **procuring** the instruments it has not yet enacted.

**The substantive finding for the chapter.** Angola has no enacted standalone cloud, data-governance
or open-data policy. In each case the most authoritative document that exists is the government's
own terms of reference commissioning the policy — so the baselines staged for those three
indicators are procurement documents, and the honest reading of the row is *being bought, not yet
held*.

## Stage 1 — the sweep (complete)

| | |
|---|---|
| Gaps worked | 55 of 55 (no skips — no prior run) |
| `agent_run` calls | 110 — 2 per gap, `effort: medium` |
| Candidates returned | 633 |
| Fetched | 180 |
| Staged after the cap | **134** — 50 baselines, 84 progress |
| Dropped | 80, on `reference.md` §7's closed vocabulary |
| Held back by the cap | 18, recorded with URLs in the unselected register |
| Wall clock | ~60 minutes, five sub-agents concurrent (39 minutes for the slowest) |
| Sessions | one |

**The cap bound far less here than on ZAF, and the reason is the dedup.** ZAF fetched 536 and
staged 126 — the cap did three quarters of the work. AGO fetched 180 and staged 134, and only 18
items were excluded by the cap at all. What thinned this run was the base already holding the
document: the briefs found the right things and the index had most of the important ones. **The
distribution is the evidence**: 28 indicators at the full 1+2, 20 at 1+1, five below. Twenty-seven
indicators could not fill the cap, and almost none of them for want of a candidate.

**The §2 objective form works, and the bare-noun family is fixed.** ZAF's finding was that
`{Topic L1} — {Topic}: {Progress indicator}` is needed because 35 of the 121 frame rows are one or
two words. On AGO the `dpi.mis` family — *Land*, *Justice*, *Social protection* — and
`dpi.registry--address-register` resolved on the first brief in every case. No indicator in this
run was unsearchable.

## The defect this run found, and where it was fixed

**Five sub-agents writing into one flat `new-queue/` cannot see each other, and it cost real
files.** Thirteen URLs were staged twice under different slugs, and three more files were silently
overwritten by a sibling that generated the same `YYYY-MM-DD-slug.md` name for the same document.
ZAF hit the same fault (48 redundant files across 44 URLs) and `PROGRESS-FILLER.md` §6 already
makes the parent's dedup pass mandatory because of it — but §6 says *dedup*, and the silent
overwrite is not a duplicate: it is a **loss**, and nothing in the queue records that it happened.

The parent pass here deduplicated by URL rather than by filename, kept the fuller body, reassigned
each survivor to the indicator it most centrally answers, and decremented the losing indicator's
count with a `duplicate-in-run` drop, so 134 files sit against 134 selected rows and the run CSV
adds up. One reassignment was made against the mechanical rule: DP 46/18 (PNAGIA) went to
`gov.standards--national-interoperability-standards` rather than to
`gov.policy--data-interoperability-framework-roadmap`, because the mechanical pick would have left
the standards indicator at 0/0 and been written down as a `nil` — **and a nil is a claim about the
world that this run cannot make when all three of an indicator's items were staged under its
neighbours**. That is the shape of error to watch for if this pass is ever automated.

**Five indicators now stand below the cap purely because a neighbour kept the shared document**
(`gov.policy--data-interoperability-framework-roadmap` and `dpi.mis--justice` at 0+2,
`gov.legislate--statistics-legislation` and `dpi.exchange--use-of-digital-id-in-other-systems` at
0+1, `gov.standards--national-interoperability-standards` and `dpi.pay--consumer-protection` at
1+0). Nothing was lost to the base — the documents are all in the batch — but the run CSV's
per-indicator counts understate coverage by exactly this much, and the mapping pass at stage 3 will
find the evidence under a neighbouring subject.

## Capture quality, declared

- **48 of 134 are `body_completeness: excerpt`.** Nearly all are `lex.ao` statute pages and
  government PDFs truncated at the fetcher's 30,000-character ceiling — flagged, not retried, per
  `capture-rule.md`. This is a materially higher excerpt rate than ZAF's, and the cause is that
  Angolan primary law is served as long single-page HTML.
- **30 carry `date_source: proxy`**, each naming its basis in `note`.
- **One unresolved date conflict**, recorded in the survivor's `note` rather than picked: two
  captures of the IMA digital-government-and-AI governance ToR read `published` as 2026-03-01 and
  2026-03-24.
- **One substitution, flagged in its own `note`**: Lei n.º 6/26 has no page on LEX.AO, so
  Verifica.ao's article-by-article account was staged in its place.
- **Three fetch routes defeated us**: `lexlink.eu` is login-gated on Diário da República texts,
  `governo.gov.ao` and `cipra.gov.ao` return JS-only navigation stubs (the same releases are
  fetchable from `ima.gov.ao`), and FAO's `openknowledge` PDF bitstreams yield no extractable text.
- **One origin adjudication**, the first this process has produced: `livrozilla.com`, `drop`, a
  document-sharing content farm. It is in the share's `progress-filler-drop-list.csv`, which this
  run created, and note 47 carries it to OSINT as an `[ACT]`.

## Stages 2–4 — not yet run

The run's four stages are separated by an ingest and a mirror refresh and cannot be done in one
sitting. Stage 1 is above. The rest are filled in when they happen:

- **Stage 2 — the stage 4 read.** Sources reaching the ledger, rows minted, rows moved. Pending
  Bill's hand-carry of `new-queue/` into `OSINT\new\`, `update wiki`, and the mirror refresh.
- **Stage 3 — the mapping.** Indicators moved off *No evidence*, rows rewritten. Note that
  `BUILD.md` has no indicator-mapping stage: stage 4 moves the ledger and rebuilds the documents,
  and `outputs/reports/AGO/indicators.csv` is rewritten by hand against
  `documentation/indicator-mapping-conventions.md`. On ZAF this half was the expensive one — 119
  unconsidered sources into 64 minted rows and 14 moves, then 43 indicator rows drafted and 4
  rewritten, a working session on its own.
- **Stage 4 — the render.**

**Yield is stated when stage 3 lands**, as gaps closed against the 55 probed and against sessions
spent. On ZAF the sweep closed 43 of 44 — only the address register stayed at *No evidence* — and
AGO's `dpi.registry--address-register` is again one of the thinner rows here.

## What this says about scheduling

**The sweep half remains cheap and the ingest half remains the constraint**, and nothing here
changes `PROGRESS-FILLER.md` §7's ruling that fillers are what to pace and mappings are not.
**134 documents is roughly the size of one night's daily sweep**, so the batch should be carried
across on a day when the week's sweeps are already secured.

**One number is worth watching across the next few countries.** If the dedup rate holds — a third
of indicators losing their first-choice baseline to the base already holding it — then the filler
is buying less per run than the ZAF pilot suggested, and the argument for probing every country
weakens in favour of probing the ones whose ledgers are thin. AGO's ledger held 123 rows before
this run. ZAF's held 153. A country at 25 rows is a different proposition, and `GNB` (21 indicators
from 25 rows) is the natural place to test it.
