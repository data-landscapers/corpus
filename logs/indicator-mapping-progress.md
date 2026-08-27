---
type: log
title: Indicator mapping pass — progress and how to resume
---

# Mapping the country ledgers onto the indicator frame

*(Opened 2026-08-26. The decision record is `documentation/progress-report-redesign.md`; the drafting
conventions are `documentation/indicator-mapping-conventions.md` and this file amends neither. This is
only where the pass has got to and what the next session needs to know to carry it on.)*

**The state is on disk, not in this file.** A unit is done when `outputs/reports/{ISO}/indicators.csv`
exists. `ls outputs/reports/*/indicators.csv` is the authoritative count, and this note is a skim that
can go stale. The frame covers the 54 country units only — XAF, XSA and XWA keep the movement
document (`progress-report-redesign.md` §1) and are not in scope.

## Done

ERI and ZAF were the pilots. This pass has since added, in order: **GNB, AGO, BDI, BEN, BFA, BWA,
CAF, CIV, CMR, COD, COG, COM, CPV, DJI, DZA, EGY, ETH, GAB, GHA, GIN, GMB, GNQ, KEN, LBR, LBY, LSO, MAR, MDG, MLI, MOZ, MRT, MUS, MWI, NAM, NER, NGA, RWA, SDN, SEN, SLE, SOM, SSD, STP, SWZ, SYC, TCD, TGO, TUN, TZA, UGA** — 52 of 54, one commit each, all pushed.

Yields so far, as a sense of shape: 21 indicators from GNB's 25 ledger rows, 43 from BDI's 74, 52
from BWA's 107, 57 from BEN's 105, 64 from BFA's 131, 66 from AGO's 122, 43 from CAF's 92, 92 from
CIV's 167, 73 from CMR's 121, 67 from COD's 123, 52 from COG's 103, 45 from COM's 117, 49 from CPV's 140, 43 from DJI's 70, 58 from DZA's 111, 66 from EGY's 199, 66 from ETH's 97, 58 from GAB's 120, 81 from GHA's 175, 59 from GIN's 109, 46 from GMB's 75, 42 from GNQ's 67, 93 from KEN's 219, 43 from LBR's 71, 64 from LBY's 84, 61 from LSO's 69, 79 from MAR's 137, 44 from MDG's 67, 55 from MLI's 87, 77 from MOZ's 159, 39 from MRT's 62, 50 from MUS's 81, 65 from MWI's 183, 62 from NAM's 134, 42 from NER's 68, 92 from NGA's 279, 69 from RWA's 128, 29 from SDN's 52, 55 from SEN's 115, 40 from SLE's 83, 37 from SOM's 60, 44 from SSD's 74, 27 from STP's 49, 43 from SWZ's 86, 34 from SYC's 54, 44 from TCD's 132, 47 from TGO's 124, 39 from TUN's 77, 61 from TZA's 150, 61 from UGA's 159. Between three quarters and nine tenths of ledger rows map; the rest are placeholders with
no source, or real instruments the frame has no question for (a telecoms statute, a broadcasting
transition), and those correctly stay on the ledger and out of the report.

## Remaining

2 country units: ZMB, ZWE.

## The loop, per unit

0. Dump **only the sourced rows** and read those. A one-line filter on `sources` being non-empty is
   the whole of it, and it both sizes the unit honestly and makes the coverage check at the end a
   comparison of two numbers (see *What COM added* and *What CPV added* below).
1. Read the ledger. Every field earns its place: `subject` says where the row was filed and **not**
   which indicator it answers, `movement` is the ledger's vocabulary and not this one, and `note`
   usually carries the qualification the prose needs.
2. Draft the rows and write `outputs/reports/{ISO}/indicators.csv` — columns
   `indicator_id, progress, summary, developments, row_ids`, CRLF, no BOM, ordered however you like
   (the renderer walks the frame, not the file).
3. From `scripts/.workroot`: `python scripts/report-render.py --unit {ISO} --check` — want checks I,
   L and M **(indicators)** all PASS. Then `python scripts/report-register-check.py --unit {ISO}` —
   want 0 register hits, 0 indicator cells outside band, check H 0.
4. Commit that one file and push.

**A `StaleCatalogue` error means the mirror has moved under you**: run
`python scripts/build-catalogue.py` from the workroot first. It happened three times in nine units,
so expect it rather than diagnosing it.

**Check L failing on `{ISO}-progress.md` and `{ISO}-status.md` is expected and gates nothing** — those
are the old documents, and the progress one is replaced the next time the renderer runs.

## What the checks actually catch, and what a drafting lint should test first

Running the two real checks per attempt is slow. Everything below can be tested locally before
writing the file, and every item on it was hit repeatedly during this pass:

- **Every sentence carrying a figure needs a citation in that same sentence.** Sentences split on
  `.` **and `;`** — a semicolon inside a link label splits the label away from its own target, which
  is how `200,000 biometric authentications a day;` came to read as uncited. Figures are 4+ digit
  runs, comma-grouped numbers, percentages and currency amounts; bare years are exempt.
- **Word bands**: summary 8–40, developments 25–200, counted after reducing `[label](target)` to
  `label`, so link text costs words and slugs do not.
- **Register**: no `unveiled`, `landed`, `rolled out`, `paves the way`; no `ecosystem`, `unlock`,
  `at scale`, `leapfrog`, `dematerialis`; no `binding constraint`, `it is worth noting`, `turns out
  to be`; no first person. The banned words appear naturally in official announcements, so watch the
  clauses you are quoting rather than the ones you wrote.
- **Slugs**: cite exactly as the ledger's `sources` field carries them, spaces, parentheses and all,
  and never a URL. Citing only slugs that appear on the mapped rows keeps check M clean by
  construction, because the ledger's own sources have already passed it.
- ***Mixed* needs a qualifying clause after a comma**, naming which instruments moved which way.
- **No-evidence rows are never written out**; an indicator absent from the file renders as
  *No evidence*, which is what makes the frame's gaps visible.

## Two judgement calls worth keeping consistent

**One row may serve several indicators, and should where it genuinely answers several** — but never
with the same sentence twice. Where the temptation is to repeat, the second indicator usually wants
a different fact from the same source: the instrument's passage under legislation, what it will
oblige under use, its cost under financing.

**A *Not held* row with no source is a placeholder and is not mapped**; one that carries a source is
a dated, cited statement that a thing is absent, and it is mapped. Most units carry a handful of the
first kind and they are the reason the mapped-row counts above are not higher.

## What CIV added, 2026-08-26

The thickest ledger mapped so far — 167 rows, 92 indicators — settled two things.

**The pre-lint the section above asks for now exists: `scripts/lint-indicators-draft.py`.** It reads
a draft and the unit's ledger and applies every rule in that list plus the vocabulary, the frame
membership and the placeholder rule, in about a second and without a render. Run it on the draft
before the file goes into `outputs/`. On this unit it caught the semicolon-inside-a-link-label trap
on its first run and a bare figure on its second, and the two real checks then passed first time —
which is the point of it, because on a 92-indicator unit a failing round trip through the renderer
costs several minutes. It does not replace the real checks: it cannot see the catalogue, so check M
still has work to do.

**Three uses of one ledger row is the ceiling, and each use must be a different fact.** One row here
reaches three, the monetary union's digital financial services report, read once for account uptake,
once for what the central bank supervises and once for the country's share of union transaction
value. Two cells were rewritten to get there: the first draft had the regional instant-payment
mandate opening two different indicators with the same sentence. The test is not a count but a
reading — if the second cell's opening clause could be pasted into the first, that indicator has no
evidence of its own and should say so. Counting uses mechanically is still worth doing, as the prompt
to go and reread them.

## What CMR added, 2026-08-26

**Some units carry unsourced *Not held* placeholders and some do not, and the difference is large.**
Every one of CIV's ten Not-held rows carried a source and all ten were mapped; seven of CMR's carried
none and none could be. Those seven are the whole of CMR's unmapped residue — there is no ledger row
here that the frame simply has no question for. Check the placeholders first: it tells you in one
pass how much of a ledger is mappable, and `lint-indicators-draft.py` refuses the mapping outright
rather than letting it reach check I.

**The register's first-person test fires on place names.** `Limbe I` is a real council and reads to
the check as the first-person pronoun, because the pattern is case-sensitive and unanchored to
context. It is not a bug worth changing — the same case-sensitivity is what stops `US$40m` firing —
so the drafting move is to name the place another way. Expect the same on any `Region I`, `Phase II`
or `Zone I` a source uses.

## What COD added, 2026-08-27

**Check L can fail on the old progress document and still gate nothing.** COD's `COD-progress.md`
carries four unwritten narrative blocks, so `--check` reports `check L: FAIL` on a unit whose three
indicator checks all pass. That document is replaced the next time the renderer runs and the mapping
pass does not touch it. Read the indicator halves — `check I/L/M (indicators)` — and treat a check-L
failure naming only `{ISO}-progress.md` or `{ISO}-status.md` as noise, which the loop above already
says and which this is the first unit to actually demonstrate.

**Fold a stray row into an existing indicator rather than minting one for it.** COD's Mbororo herder
identification is a provincial operation on a named population and the frame has no question shaped
like that. Writing `dpi.id--registration-of-a-named-population` would have been the natural mistake;
the pre-lint refused it against the frame, and the row belongs in
`dpi.id--registration-of-entire-population` as a second development. **The frame is not extended by a
mapping pass** — an indicator is added by editing `lookups/indicators.csv`, which is a decision about
all fifty-four countries and not about one row.

## What COM added, 2026-08-27

**Ledger size does not predict indicator count; the placeholder share does.** COM's ledger is 117
rows, larger than COG's 103, and yields fewer indicators — 45 against 52 — because thirty-five of its
rows are unsourced *Not held* placeholders and only twelve of COG's are. On a base this thin the
placeholders are the country's own record of what it has said it would build and never has: an
observatory designed in 2018, a data-protection authority provided for in 2021, a start-up statute,
a universal service fund. They are correctly unmapped, and the frame prints them as No evidence,
which is the same finding read from the other end.

**Count the sourced rows before drafting, not the ledger rows.** `ls` on the ledger tells you nothing
about how much work a unit is. One line — rows whose status is *Not held* with an empty `sources`
field — gives the real size, and on the eight units mapped since CIV it has ranged from zero to
thirty-five out of a hundred-odd.

## What CPV added, 2026-08-27

**On a unit with many placeholders, read the sourced rows out first and work only from that.** CPV's
ledger is 140 rows of which 45 carry no source. Filtering the dump to sourced rows before reading cut
the drafting input by a third and made the coverage check trivial — every sourced row mapped, which
is the target on any unit and is easy to verify when the two counts are the same number.

**A figure lifted out of a link label to make a point still needs a citation.** Four of this unit's
five pre-lint failures were the same shape: a percentage quoted in a following sentence to draw a
comparison, its source sitting in the sentence before. Either pull the figure back inside the cited
clause or write the comparison without the number — both read better than a second citation on the
same source two sentences apart.

## What EGY added, 2026-08-27

**The thickest unit so far, and the word band is what bites on it.** 145 sourced rows produced 66
indicators, several of them carrying four or five ledger rows, and two developments cells came back
over the 200-word band on the pre-lint's second pass. On a unit this size the band, not the register,
is the binding constraint: budget about three dated paragraphs per cell and cut the qualifying
clauses first, since they are the part a reader can infer from the citation.

**Ten units in, the pattern in the residue is settled.** Every unit since CIV has left unmapped only
two kinds of row: unsourced *Not held* placeholders, which the conventions and the pre-lint both
refuse, and a handful of instruments the frame has no question for - a telecoms statute, a regulatory
council. Where a sourced row looks unmappable, it almost always belongs in an existing cell as a
second or third development rather than in an indicator of its own.

## What ETH added, 2026-08-27

**The highest mapped share yet, and it came from the ledger rather than the drafting.** 93 of ETH's
97 rows carry a source, so 96% of the ledger mapped and the residue is four unsourced placeholders
and nothing else. The placeholder count is the whole of the variance across this pass: COM's 117
rows yielded 45 indicators on 35 placeholders, ETH's 97 yielded 66 on four. **Count the placeholders
before estimating a unit, not the rows** - the loop already says this, and ETH is the clean end of
the range that CPV and COM sit at the other end of.

**Where a row's own subject has no indicator, read what the row is evidence *of*.** Three of this
unit's rows had no obvious home: a livestock information system in a frame with no agriculture MIS,
a payment-gateway tax assessment, and a copyright amendment. Each mapped once the question was put
the other way round - the livestock standards are national data quality standards, the tax
assessment is a tax administration running on conflated data (`dpi.mis--tax`), and the amendment is
a university law school contributing to policy as well as a platform-liability instrument. None
needed a new indicator, which is what `COD` established and this unit confirms at scale.

**A cell that reuses a row must move the fact, not just the wording.** Nine rows here serve two
indicators and one serves three. The trap this unit sprang was the sovereign cloud: it is named in
the same clause of the same strategy as the cybersecurity foundations, so the cloud-strategy cell
and the cybersecurity-readiness cell were drafting the same sentence. The fix was to split the
clause between them - the cloud and the forensic laboratory to one, the security agency's work to
the other - rather than to drop one cell.

**The semicolon trap has a second form.** CIV found it inside a link label; here it was a long
sentence whose citation sat after the semicolon, leaving `5,000 Chinese-funded training places`
uncited in the fragment before it. The pre-lint caught it as the run's only defect. When a
development runs long enough to need a semicolon, cite before it and start a new sentence after.

## What GAB added, 2026-08-27

**A quarter of the ledger was unsourced placeholder, and that is the story of the unit.** 26 of
GAB's 120 rows carry no source, and every one of them names something the country does not have -
a national digital strategy, a computer emergency response team, an AI policy, a universal service
fund, a gender divide measure. They are correctly unmapped and they print as No evidence, which is
the same finding read from the frame's end. The mapped 94 gave 58 indicators.

**Two frame indicators can want the same row, and the split is by sector rather than by fact.**
The electoral-roll platform is both a register and a use of the identification number; the unified
social register is both a register and social protection. Where two indicators would take the same
row and the same sentence, map it once and leave the other to say No evidence - a second cell
paraphrasing the first is worse than an honest gap. Three rows here were dropped from a second cell
on that test.

**A row whose subject has no indicator often belongs to the country's regional posture.** The draft
Code of Civil Procedure maps twice on genuinely different facts - digitised filings under
`dpi.mis--justice`, harmonisation with the regional uniform acts under
`gov.regional--regional-legal-harmonisation`. Half of GAB's payments evidence is regional
instruments applied nationally, and mapping it to the national payment indicators alone would have
lost the fact that the country is a rule-taker there.

**Five of the six pre-lint failures were the same semicolon.** A long development whose citation
sits after a semicolon leaves every figure before it uncited, because the check splits on `;` as
well as `.`. EGY's note called the band the binding constraint on a thick unit; on this one it was
punctuation. The fix is mechanical: when a development needs a semicolon, close the clause with its
citation and start a new sentence.

## What GHA added, 2026-08-27

**The thickest unit in the pass, and the first where check L passes.** 175 rows, all sourced, 81
indicators. GHA-progress.md has no unwritten narrative blocks, so this is the first unit where the
loop's "check L failure is expected noise" caveat did not apply - worth knowing, because it means a
check-L failure on a later unit is still worth a glance rather than an assumption.

**The semicolon trap is systematic on a thick unit, and it is worth fixing mechanically.** GAB's
note called it punctuation; here it fired 29 times in one pass, because a development long enough to
need a semicolon is exactly what a five-row indicator produces. `scripts/lint-indicators-draft.py`
splits sentences on `;` as well as `.`, so a citation placed after the semicolon leaves every figure
before it uncited. The drafting fix is `scripts/fix-indicator-citations.py`: it walks each paragraph and repeats
that paragraph's own first citation onto any fragment carrying a figure and no citation. It invents
nothing - the citation it adds is already the paragraph's - and it took the unit from 32 defects to
3 in one run. **Keep it for the remaining thick units**; on a 175-row ledger it is the difference
between one pre-lint pass and ten.

**A sourced *Not held* row is only mappable if its source states the absence.** Two of this unit's
rows - the Gulf and India probe rows - carry a source slug that is merely an anchor: an article
about the AI strategy launch, which says nothing about either country. Mapping them would have put
a citation behind a claim the cited document does not make, which check M cannot catch because the
slug is genuinely on the row. **They were left unmapped and the frame prints No evidence, which is
the true position.** The conventions' rule that a sourced Not-held row *is* mapped assumes the
source is evidence of the absence; where it is only an anchor, the rule does not reach it. Three
other sourced Not-held rows here - data-centre power, local government, the card's payment function
- do have sources that state the absence, and all three were mapped.

**When one row's story spans three indicators, split by who is acting, not by what is said.** The
cybersecurity enforcement series runs across three ledger rows and would have collapsed into one
cell. It maps as the statute and its first penalties under `gov.legislate--cybersecurity-legislation`,
the response team and the loss figures under `infra.cybersec--national-cybersecurity-readiness`, and
the university white paper that carries those figures under `capacity.research`. Each cell says who
did what; none repeats another's sentence.

## What GIN added, 2026-08-27

**The citation helper earns its place on a mid-sized unit too.** Applied from the first draft rather
than after a failing lint, GIN came back with four defects instead of the thirty GHA started with,
and three of the four were ordinary drafting slips rather than the semicolon pattern. **Wire
`scripts/fix-indicator-citations.py` into the draft assembly from the start** - it costs nothing and
it removes the one defect class that scales with ledger thickness.

**A slug typed with a stray space fails as a missing slug, not as a typo.** One cell cited
`{CAURIDOR} )` and the pre-lint reported the slug as not on the mapped rows. The message is right
and the cause is not what it names, so read a slug-not-found error as a possible whitespace fault
before going back to the ledger.

**Where the same row answers two questions, check the row_ids before the prose.** A development
citing the electronic-money licensing count under the central-bank indicator failed check M's
pre-lint equivalent because that row was mapped only under uptake. The fix was to add the row to
both cells, not to drop the sentence - the licence count is genuinely a governance act as well as an
uptake measure, and the two cells say different things about it.

**The StaleCatalogue error appeared again, on schedule.** The loop already tells you to expect it;
this is the fourth occurrence in twenty-two units. Run `python scripts/build-catalogue.py` from the
workroot and re-run the check.

## What GMB added, 2026-08-27

**Pre-lint clean on the first run, which is the first time in this pass.** The only change from GIN
was wiring `scripts/fix-indicator-citations.py` into the draft assembly before drafting rather than
after a failing lint. That is now the default: apply it in the assembly step, and the pre-lint
becomes a check rather than a repair loop.

**Where a country holds two accounts of the same number, say so in the cell rather than picking.**
The mobile incumbent's sale carries an announced winning bid of D6.7bn and a signed commitment of
GMD 6.1bn, and the ledger explicitly does not reconcile them; the electoral roll carries 212,095
registrations announced against 179,445 records distributed. Both cells state both figures and name
the gap. That is the same rule the loop already gives for conflicting `published` dates on one
source, applied to a conflict inside the ledger's own prose.

**A cell can be worth writing for what the country does not hold, when the absence has a date on
it.** The cybersecurity strategy runs out at the end of 2026 with no successor; the incident-response
bodies exist only as a design inside that same document. Both facts come from one sourced row, and
the cell is stronger for saying that the only source describing the country's cyber capability is a
plan rather than a report. Compare EGY's note on the residue: a sourced row that looks thin is
usually thin about something specific.

## What GNQ added, 2026-08-27

**The first unit in this pass to leave a sourced row unmapped on the frame's own terms.** GNQ's
digital terrestrial television project is a broadcasting transition under a diagnostic tender, and
the frame has no question shaped like it - which is exactly the example the residue note at the top
of this file already gives. Every other sourced row mapped. **Do not force such a row into the
nearest cell**: the alternative here would have been to file a television switchover under broadband
strategy, which would make the indicator say something the evidence does not.

**One ledger row can answer two indicators when the law and the institution it creates are both
absent in different ways.** The 2016 data-protection statute maps twice: to
`gov.legislate--data-protection-legislation` for a regime in force for ten years, and to
`gov.protect--data-protection-authority` for the supervisory organ article 15 leaves to a decree the
government never issued. The second cell is the more useful of the two, and it exists only because
the row was read for what it withholds rather than for what it establishes.

**A country can be measured by what its own studies admit.** GNQ's only assessment of government
systems is the state infrastructure operator's own, putting ministry interoperability at about 15
per cent, and its development agency's outgoing Inspector General named limited data-sharing by line
ministries as the obstacle to monitoring the national strategy. Two self-reported facts that
corroborate each other are worth more than either alone, and the cells say so.

## What KEN added, 2026-08-27

**The largest unit so far - 217 sourced rows, 93 indicators - and the frame held.** No new indicator
was needed and no sourced row went unmapped. On a ledger this thick the binding constraint is not
finding a home for a row but keeping each cell inside 200 words: five cells carry five or more rows,
and the cybersecurity cell took four rounds of trimming to come inside the band. **On a unit over
150 rows, draft the developments at about 150 words and let the fifth row make it 190**, rather than
writing to the band and trimming afterwards.

**Where the ledger has reconciled a public dispute, carry the reconciliation into the cell.** Three
of this unit's rows exist because the ledger settled a contradiction rather than recorded an event:
the health framework's US$2.5bn against US$1.63bn headline, the claims platform's KSh 104bn as a
ten-year service fee rather than a lump sum, and a data-centre project reverted from "cancelled" to
"stalled" because no principal announced a cancellation. **Each of those reconciliations is the most
useful sentence in its cell**, and a mapping that reported only the later figure would have thrown
away the ledger's own work.

**A country can be strongest and weakest on the same indicator, and Mixed is how to say it.** Eleven
of KEN's 93 cells are Mixed, against ten of ZAF's 77 - the same shape ZAF's note predicted for a
thick ledger. The pattern here is specific: the platform carries more services and more revenue
while agency migration onto it went backwards; the regulator gained its first appropriation while
its caseload has not been restated in eighteen months; subscribers grew while sign-ups were capped
in seven counties. In each case the stem alone would be false.

**Three heredoc patches corrupted a draft script this session by turning `
` into a real newline.**
Editing a Python drafting script from a bash heredoc is not reliable for escaped characters. Use the
editor for those patches, or keep the replacement strings free of escapes.

## What LBR added, 2026-08-27

**Where a unit's story is a sequence, put the sequence in the cell rather than the latest state.**
Three of LBR's cells are only intelligible in order: a data governance policy of March 2026 named a
regulator under a statute that was not yet enacted, the statute was signed in August, and the
regulator still does not exist. A mandatory identity credential has been unobtainable since June
2025 while the requirement to hold it stayed in force. A riders' union signed a private tracking and
identity memorandum three days before the country's first data-protection law took effect. **In each
case the dates are the finding**, and a cell reporting only the current position would lose it.

**Seven units in one session, and the loop is now stable.** ETH, GAB, GHA, GIN, GMB, GNQ, KEN and
LBR all mapped without a new indicator, without a frame change, and with `lint-indicators-draft.py`
plus `fix-indicator-citations.py` in the assembly step. The two real checks were run once per unit
and passed once per unit on every unit after GHA. **The remaining units need no new method** -
read the sourced rows, map, apply the citation fixer, pre-lint, write, check twice, commit, push.

## What LBY added, 2026-08-27

**The densest unit of the pass so far, 64 indicators from 78 sourced rows on an 84-row ledger,
and it is dense because the country is two states.** Almost every ledger row is a distinct
instrument rather than another account of one, so the usual work of folding several rows into a
cell barely arose: 46 of the 64 cells take a single row. The residue is the smallest yet - six
unsourced *Not held* placeholders and two sourced rows, Law No. 22 of 2010 on telecommunications
and the OZON unified licence granted under it, which are the telecoms-statute case the top of this
file already names as having no question in the frame. Both carry the same fact, that licensing
jurisdiction is contested between the Tripoli regulator and the eastern ministry, and there is no
indicator that asks it.

**Where a divided state produces two accounts of one thing, the cell says both and names the
division.** The salary system reaches 76 per cent of public employees because the eastern
government will not share employee banking data; the cybersecurity law is drafting on the eastern
legislative track with nothing on how it would apply in the west. In each case the qualification
is the finding, and dropping it would make the indicator read as an ordinary partial rollout.

**A stretched frame fit is better declared than forced, and the summary is where to declare it.**
`infra.connect--mobile-penetration` holds a 5G launch and a vendor meeting because the base carries
no subscriber or coverage figure at all; the cell says so in its own summary rather than letting
the indicator name imply a measure that does not exist. The same move covers
`dpi.registry--population-register`, whose only movement is a database of non-citizens. Compare
GNQ's rule - do not force a row into the nearest cell - which still holds for the *row*; this is
the other direction, an indicator with weak evidence saying what it actually has.

**Pre-lint clean on the first run, second time in the pass.** The assembly script reads every slug
out of the ledger by row id and index rather than transcribing it, which removes the
whitespace-in-slug fault GIN found and makes a slug typo impossible by construction. **Worth
keeping for the remaining units**: `S(row_id, i)` over the ledger's own `sources` field costs three
lines and retires a whole defect class.

## What LSO added, 2026-08-27

**The first unit with no residue: 69 ledger rows, 69 mapped, 61 indicators.** No unsourced *Not held*
placeholder and no instrument the frame has no question for. That is not a property of the mapping but
of the ledger - every row on it is sourced, and every row is about something the frame asks about - so
it is worth reading as a statement about the unit rather than as a target other units failed to hit.

**A *Not held, searched* row with a source that genuinely states the absence can carry two indicators.**
The 2021 capacity assessment found both no government open-data programme and no access-to-information
statute in force; those are two findings in one document, and they map to `data.open--use-of-open-data`
and `gov.legislate--access-to-information-legislation` respectively. Compare GHA's rule about anchor
sources - the test is whether the cited document *states* the absence, and here it states two.

**`Stalled` earns its place on this unit, twice.** The MISSA procurement closed in August 2024 with no
award since, and the Mohale's Hoek backup data centre was toured near-complete in 2018 and never
confirmed live. Both are things that started and stopped, which is what the value is for; *No change*
would have read as a standing position and *No evidence* would have been false. Ten units of this pass
used the value not at all, and it is worth reaching for where the record shows an abandonment.

**Where the ledger's own row is a measure of a gap, put both numbers in the cell and withhold the
direction.** The ministry's own figures are 100 per cent broadband coverage against about 50 per cent
regular internet use. There is no earlier measurement, so the cell is *No change, a first statement of
the gap with no earlier figure behind it* - ZAF's first-measurement rule applied to a ratio rather than
to a count.

## What MAR added, 2026-08-27

**The largest indicator count of the pass, 79, and it came from breadth rather than thickness.**
120 sourced rows produced 79 cells because the unit's evidence is spread across the whole frame -
five separate 5G rows, ten data-centre rows, six identity rows, four cybersecurity rows - rather
than piled onto a few subjects the way KEN's 217 rows were. **Count the distinct subjects, not the
rows, when estimating how many indicators a unit will yield.**

**The semicolon trap has a third form, and this one cannot be drafted around.** GHA found it in a
link label and ETH in a long sentence; here the `;` sits inside a catalogue **slug** -
`2026-01-14 Morocco — 16.5m voters on electoral rolls; most 2026 registrations via digital channels`.
The checks split the sentence inside the citation's own target, so the fragment carrying the figures
can never hold a complete `](...)`, wherever the citation is placed. `fix-indicator-citations.py`
cannot repair it either, because the repair it makes is to repeat that same broken citation.
**Where a slug contains a semicolon, no figure can share a sentence with it**: state the fact as a
ratio or a proportion instead, or cite a different source for the number. This unit's electoral-roll
figures became "two to one in favour of the online channel", which is what the numbers say anyway.

**A row whose whole content is a reconciliation is still worth mapping, for the reconciliation.**
Two rows here exist because the base settled a contradiction rather than recorded an event: one
confirms that a 2023-dated cybersecurity strategy and the 2030 strategy are a single instrument, and
one establishes that the widely-repeated "23 data centres, ahead of South Africa" figure is a 2023
certification count and not a facility census. Both map, and in both cases **the reconciliation is
the most useful sentence in the cell** - the same finding KEN's note made about a public dispute.

**Where a country's own regulator publishes a periodic observatory, it is worth two cells and not
one.** The first-quarter 2026 telecoms observatory carries mobile park, penetration and traffic on
one hand and fixed lines and fibre on the other; those answer different frame questions and belong
in `infra.connect--mobile-penetration` and `infra.connect--national-fibre-backbone` respectively.
That is the CIV rule about one row serving several indicators, applied to a statistical release
rather than to an instrument.

## What MDG added, 2026-08-27

**Three units in a row with no unmapped sourced row, and the reason is the same each time: a ledger
built of instruments the frame asks about.** LSO, MAR and MDG between them left nothing on the table
but unsourced placeholders. The residue class named at the top of this file - a real instrument the
frame has no question for - has not appeared since GNQ, which is worth knowing when estimating a unit:
**the expected residue is the placeholder count and nothing else.**

**A donor project row can be the evidence for three different indicators, and each use is a different
number in the same document.** The connectivity project here carries a US$375m envelope (partner
financing), 664,000 devices distributed (bridging divides) and a US$15m skills sub-component that is
its own ledger row. Where a supervision record is the source, the sub-components are usually the facts
the frame wants, not the headline envelope.

**Where a country's own institution states an absence about itself, that is stronger evidence than a
missing source.** The base's open-data row records three of four platforms tested and reachable and
**no whole-of-government policy found**, and the finance ministry's own portal failing to resolve. That
maps to `gov.policy--open-data-policy` as *No change* on a searched absence, and the four-platform test
is what makes it a finding rather than a gap.

## What MLI added, 2026-08-27

**One event can produce eight ledger rows, and they should be mapped apart rather than together.**
The national digital week of August 2026 generated recommendations for a digital council, a
data-management law, a startups law, a regional artificial-intelligence protocol, a single transport
operator, a public key infrastructure, a national artificial-intelligence strategy and a universal
connectivity target - eight rows on one slug. Bundling them into a "policy" cell would have hidden
which questions the country has an answer to; mapped apart, each indicator says plainly that the
answer is a recommendation. **Where several rows share one source, the test is still what each row
is, not where it came from.**

**A cell can be worth writing to name a contradiction the frame would otherwise split.** The
cybercrime pole appears twice in this unit: as an institutional build under
`infra.cybersec--national-cybersecurity-readiness`, where it is progress, and as the venue that
sentenced a newspaper editor under `gov.discourse--open-discussion-of-government-policy`, where it is
regression. Both cells say so and each points at the other, which is more useful than either alone.

**Where the ledger holds two halves of one ratio, put both in the cell and let the shape carry the
finding.** Birth registration at 89.5 per cent against death registration at about 20 per cent is one
*Mixed* cell, not two; mobile money volume growing 18.58 per cent while the distributor network fell
46.34 per cent is another. In both cases the two numbers together say something neither says alone,
which is what *Mixed*'s qualifying clause exists for.

## What MOZ added, 2026-08-27

**The commonest pre-lint defect on a thick unit is now a borrowed figure, not a semicolon.** All four
defects here were the same shape: a number lifted from a ledger row that the cell does not map, cited
to a slug that is therefore not on its `allowed` set - a rural-urban ratio quoted inside a schools
cell, a penetration figure quoted inside a coverage-portal cell. The citation fixer cannot help,
because the paragraph has no citation that covers the claim. **The rule is that a figure may only
appear in a cell that maps the row it came from**; where the context genuinely needs it, add the row
or drop the number. GHA's semicolon pattern did not fire once on this unit.

**Where the state's own instrument records what the state has not done, the cell is stronger for
carrying the omission verbatim.** Three cases here: the payments law's own notice sets a
twenty-five-second availability ceiling while the instant-payment system carries 11,000 transfers a
day against twenty-five million wallet accounts; the cyber security statute creates a fund that has
no line in the budget passed weeks earlier; and the risk assessment rates nineteen of twenty-nine
critical systems very high risk while naming no system, so it publishes a distribution without a
register. In each case the gap is the finding.

**A bilateral instrument another state drafted can be the only document describing a country's own
architecture, and the cell should say so.** Mozambique's health information systems - the electronic
medical record, the laboratory, surveillance and logistics systems and the data exchange behind them -
are named in a United States memorandum the government signed, and no Mozambican document naming them
is held. The cell maps the row and states that provenance in its own sentence, which is what stops the
reader taking the architecture for a national plan.

## What MRT added, 2026-08-27

**Six units running with no unmapped sourced row, and the residue class at the top of this file has
not appeared since GNQ.** LSO, MAR, MDG, MLI, MOZ and MRT all left nothing but unsourced placeholders.
On present evidence **the expected residue for a unit is its placeholder count and nothing else**, and
a sourced row that looks unmappable is worth another minute rather than a note.

**Where several instruments expired without successors, say so once and let the cells carry it.**
This unit's digital agenda ran to 2025, its cybersecurity strategy to 2025 and its university research
accreditation to May 2024, all with no renewal on record. Each cell states its own expiry, and the
policy cell names the pattern; that is enough. *Stalled* is the right value where something started
and stopped (the research unit), and *No change* where an instrument simply ran its term and nobody
replaced it.

**A figure quoted from a second source on the same row still needs its own citation.** The three
pre-lint defects here were satellite bid amounts stated in a sentence whose citation had been left to
the paragraph's first anchor, which the fixer could not reach across a sentence boundary. Cheaper than
rewriting: close the clause with its own citation and start a new sentence for the caveats.

## What MUS added, 2026-08-27

**One omnibus bill can be the evidence for six different indicators, and each use is a different part
of the same statute.** The July 2026 bill here amends fifty-eight Acts and carries the fintech
governance committee, the artificial-intelligence city scheme, the central bank threat-sharing
platform, the virtual-asset solicitation rule, the digital travel authorisation and the clinical-trial
licensing system - and the ledger has each of those as its own row, so the frame gets six cells and
none of them repeats a sentence. **Where a ledger has already split a vehicle into its provisions,
map the provisions; where it has not, the vehicle is one row and one cell.**

**A banned register term can arrive inside the evidence, and the drafting has to route around it.**
Two ledger rows here use *binding constraint* and *unveiled* in their own prose - the register check
does not read the ledger, but a cell that quotes it verbatim would fail. The paraphrases are "what
limits the economy" and "presented", and the check caught neither because they never reached the
draft. **Read the row for banned terms before quoting it**, which is the same discipline CMR's note
gives for place names that read as first person.

**Where the country's own instruments contradict each other on safeguards, that is the cell.** The
data-protection statute was left out of an omnibus amending fifty-eight Acts in the same month the
statistics office was empowered to share more data and a plate-recognition system went live at the
airport with no retention rule. Three rows, three cells, and each names the omission the others
imply - which reads better than one cell trying to carry the whole argument.

## What MWI added, 2026-08-27

**The largest placeholder count of the pass, fifty-seven of 183 rows, and it changes what the ledger
size means.** A 183-row ledger yields 65 indicators here where MOZ's 159 yielded 77, because a third
of this unit's rows are unsourced *Not held* markers. COM's note said the placeholder share predicts
the indicator count better than the row count does; this unit is the extreme case and confirms it.
**Count the placeholders first and the unit sizes itself.**

**Where a unit's own record contradicts a minister, carry the contradiction rather than the minister.**
The spectrum fee cut is stated at 50 per cent in Parliament and at 20 by five contemporaneous accounts
of the regulator's own announcement; the cell states the 20 and names the parliamentary figure as the
outlier. The same shape recurs on the presidential 80-per-cent internet target, which has no baseline,
and on the trade association's coverage figures, which come from a party whose policy asks include
cutting its own taxes. **Naming who is speaking is most of the work on a unit this thinly sourced.**

**A ledger row can be the only evidence for an indicator the frame asks about and the country has
never measured.** Malawi has no state internet-usage measurement at all: the first usable current
figure is the operators' trade association's, and the cell says so. Where the only number is an
interested party's, the cell should carry the number, the party and the interest in the same
paragraph - which is what stops the frame reading it as a national statistic.

## What NAM added, 2026-08-27

**Where two ledger rows record the same object at different moments, map them into one cell and let
the dates do the work.** This unit has a crop-monitoring contract recorded twice - once as awarded and
once as cancelled by cabinet three weeks later - and a data protection bill recorded as a 2022 draft, as
an untabled bill and as a set of rights provisions deleted between two drafts. Each pair reads as one
story with a direction, which is what the *progress* value is for; mapped apart they would have read as
two unrelated facts.

**An enacted statute that has never commenced is *Advanced*, not *Implemented*, and the cell should say
which section holds it up.** The access-to-information Act is gazetted with its commencement left to a
ministerial date that has not come, and its appointment machinery was gazetted first, so the annual
report the Act requires cannot yet exist. Naming the section is what stops the reader treating a
gazetted Act as a working one.

**Nine units in a row with no unmapped sourced row, and the second pre-lint-clean first run of this
session.** The two together suggest the method has converged: read the sourced rows, group by what each
row *is*, apply the citation fixer in the assembly step, and the remaining defects are borrowed figures
rather than anything structural.

## What NER added, 2026-08-27

**The register check caught a banned phrase the drafter wrote, not one quoted from a row.** *At scale*
appeared in a summarising clause about a biometric programme "now enrolling at scale". Ten units into
this session the quoted-term trap CMR and MUS describe has been the only register risk; this is the
first time the phrase was the drafter's own. **The pre-lint is the only thing standing between a
natural-sounding clause and a register failure**, which is the argument for running it on every draft
rather than on thick units alone.

**A figure in a closing clause is uncited even when the paragraph opened with the citation.** Three of
the four defects here were of that shape: "at 16,500 digitised of about 200,000 agents the work is
under a tenth done", written as a conclusion after the cited sentence. The fix is to draw the
conclusion without repeating the numbers, which reads better anyway.

**Where a country's own registers are created by one instrument and none of them yet accepts an
enrolment, say which is which.** This unit's April 2026 ordonnance institutes the civil, nationality
and population registers together; the population register is in build with a sensitisation tour
running ahead of it, and the cell says that a campaign preceding a register that cannot yet enrol is
the whole of what is dated. A cleaner legal basis than most units in this base have, and no operating
system behind it, is the finding.

## What NGA added, 2026-08-27

The largest unit in the corpus by a wide margin: 279 ledger rows, 271 of them sourced, against KEN's
219 and EGY's 199. It yields 92 indicators, and — for the first time in this pass — **every sourced
row is carried by a cell**. That was not a target. It fell out of the volume: at 271 rows there is
almost no subject the frame has no question for, so the usual residue of unmappable instruments never
formed. The five rows left over at first pass were placed by appending a clause to a neighbouring
cell rather than by inventing a home for them, which is the right order — the cell has to be about
something before a row can join it.

**At this size the constraint stops being coverage and becomes the word band.** Several cells carry
five or six rows, and the only way to keep `developments` under 200 words is one clause per row with
the qualification attached rather than spun out. Where a row genuinely needed a paragraph — the birth
register's zero health-facility notifications, the fibre-cut series, the voter-accreditation failures
— it got a cell of its own and the neighbours took the short clauses. Deciding which rows deserve
prose and which deserve a clause is the whole of the drafting at this scale.

**Two placements are worth stating because they cut across the frame's own filing.** The AI
surveillance estate, the naval maritime system being pitched inland for banditry, the state
facial-recognition network and the concessioned transport databank sit together under
`tech.ai--control-of-ai-abuse`, not under the sectors that procured them. What the evidence
establishes about all four is the same absence — no lawful basis, no retention rule, no oversight —
and splitting them across transport, defence and local government would have lost the only finding
they share. Symmetrically, the fibre-cut series (155,397 cuts in two months) sits under
`infra.capacity--local-capacity-to-maintain-manage-and-develop-government-systems` rather than under
the backbone indicator, because it is a maintenance finding, not a coverage one; the backbone cell
carries the build.

**A slug the base holds without a URL fails check M and is not the draft's fault.** The cloud policy
row cites three records and the middle one has no URL, so check M reads it as uncitable. The fix was
to cite the 08-18 record of the same policy instead — the cell did not depend on the first — and the
underlying record is OSINT's to repair. Worth knowing the failure mode: the draft lint cannot see it
(it has no catalogue), so it survives to the render check and looks like a drafting error when it is
a base error. Read the message, which says so.

**The apostrophe trap has a third form.** Earlier units hit `\"` and `\'` inside f-string
expressions; this one hit a possessive plural — `parties' digital rights` — inside a single-quoted
`L()` label. Same cause, same fix: triple-quote the label. Reading slugs through `S(row_id, index)`
still makes slug typos impossible, but it does nothing for the label text, which is where every
remaining syntax error in this pass has come from.

## What RWA added, 2026-08-27

128 ledger rows, **every one of them sourced** — the first unit in the pass with no unsourced
placeholders at all. So the 100 per cent mapping here means something different from NGA's: there was
no residue to clear, only rows to place. 69 indicators.

**The unit's defining feature is that the instruments are not published, and the cells have to say
so.** The ICT sector plan is held as front matter; the data-sharing policy's seven annexes are
absent; the data protection Act's text and law number are not held; the single digital identification
law's number and enactment date are not held; the DPI strategy document is not held; the payments
directive is absent from the central bank's own enumerated document library and two sources give it
different issue dates; both licence-passporting memoranda are unpublished; the health data-sharing
arrangement is known only through one rights organisation's reading of it. The temptation is to
paraphrase the secondary summary and let it stand as the instrument. **The rule that held: state the
claim, then state that the text behind it is not held, in the same cell.** A reader who cannot check
a summary needs to be told they cannot, and it is a finding about the country rather than a gap in
the base — a government that announces and summarises but does not publish.

**Ledger rows here carry no `start` or `end` text at all — only `milestone` and `note`.** That
changes the drafting: there are almost no figures to place, so check H barely bites (one defect in
the whole unit) and the prose runs on dates, sequence and attribution instead. Where a figure does
appear it is almost always in a `note` and almost always someone's own — the correction rate is the
directorate's, the inclusion figure is the minister's, the health-centre latency claims are the
partner's, the operator results are the operator's. Naming whose figure it is did most of the
analytical work in this unit.

**Two appropriation findings were worth carrying across cells rather than burying in one.** The
data-protection supervisory authority is funded at about US$114,000 and held flat; the cyber
standards and skills line executed at 11.5 per cent; the national identification line outturned at
140.7 per cent. Read together they say which parts of the digital agenda the fisc actually funds, and
that reading only exists because the cells for protection, cybersecurity and identity each state
their own line. Worth repeating in any unit whose ledger carries finance-law rows.

## What SDN added, 2026-08-27

39 sourced rows of 52, 29 indicators. A wartime ledger, and two things in it needed the cell to hold a
shape rather than a list.

**The sequencing is the finding, and it only shows if the cells cross-reference each other.** Three
authorities exist by prime-ministerial decree — digital transformation, data and artificial
intelligence, cybersecurity — while all three statutes that would give them powers are still in
redrafting, and the platforms they would govern are already live. Written cell by cell in isolation,
that reads as ordinary progress in four places. The cells were drafted to say it once in each: the
authority precedes the law, the law follows the systems, and **no account held connects the decree to
any platform**, so which authority owns which system is not established. Resisting the urge to supply
the missing chain of authority is the whole job here.

**Where a ledger row states a risk as realised, the cell says so.** The identity credential's note
records that tying bank-account continuity to a credential of unmeasured coverage was flagged as an
exclusion risk before launch, and that the August 2026 eKYC integration is that risk being realised
rather than answered. That judgement is the ledger's and it is load-bearing; softening it to "the
integration raises questions" would have thrown away the only analysis in the row.

**A decade-old instrument can be the finding.** The 2016 stock-exchange trading system was financed
under a public financial management project whose payroll, electronic-invoicing and
electronic-procurement list is substantially the one being re-announced in 2026, and nothing on file
says what happened to the first attempt. Worth checking for in any unit with a long tail of dormant
rows: the oldest row sometimes reads on the newest.

**Conflict units put the regulator outside the frame.** Satellite service here was never licensed,
arrived through smuggled terminals, and is switched off locality by locality by whoever holds the
ground. The satellite indicator is written about who actually controls access rather than about
licensing, because licensing is not what governs it.

## What SEN added, 2026-08-27

104 sourced rows of 115, 55 indicators, third unit running with nothing unmapped.

**The unit has one recurring shape and it only reads if several cells state it.** Systems get built and
the rules meant to govern them get written afterwards: the health ministry is building a single
patient record ahead of the digital-health law that would govern confidentiality and transfer; the
social-protection workshop lists data governance as an *output*; two new biometric collections — a
public-service headcount audit and an artisanal-miners register — were agreed within two months, in a
country whose identity directorate was breached in February and whose data-protection law is still
under revision; and the civil-status computerisation bill is validated but not enacted while the
register it would govern already holds millions of records. Each cell says its own instance. Naming
the pattern once and cross-referencing would have been shorter and would have put the finding in one
cell that a reader of any other might never reach.

**Two placements cut across the frame's filing and both are defensible on the same test — what does
the evidence establish?** The three breached state systems went to
`infra.capacity--robustness-of-government-hardware-and-software`, not to cybersecurity readiness:
they establish what the estate *did*, and readiness is about what the state is equipped to do (which
that cell covers separately, with the finding that there is still no national agency and no response
team). The student-computer programme under a 129-0 commission of inquiry went to
`capacity.training--dt-related-university-facilities-and-qualifications` rather than to access,
because the inquiry's FCFA envelope is the only quantity published about it, so it is evidence about
procurement and delivery rather than about who got a computer.

**Where a ledger note forbids a rendering, obey it in the prose.** One row carries "the source is
proxy-dated, so the workshop's own date is unknown and **must not** be rendered as July 2026". The
cell says a workshop was convened and repeats the warning. Two other rows carry month-precision
dates. In a unit this dense the temptation to smooth all of it into a clean date series is strong and
would have manufactured precision the base does not have.

**Third recurrence of the apostrophe trap, and it is now clearly the dominant failure mode.** Two
possessives inside single-quoted `L()` labels ("civil-status agency's", "statistics school's"). The
fix is the same triple-quote each time. Worth simply avoiding possessives in labels from the start.

## What SLE added, 2026-08-27

73 sourced rows of 83, 40 indicators, fourth unit running with nothing unmapped.

**When one absence frames the whole unit, state it once and let the affected cells name what they
lack.** No data-protection law has been in force here at any point in the period. That belongs in
`gov.legislate--data-protection-legislation` as the finding, and then the identity, disclosure and
registry cells each say the thing they are missing — police requests answered with no warrant
requirement or oversight on the record, a farmer registry keyed to the identity number with no
data-protection arrangement, a health data platform joined at continental level with no published
data-sharing terms. Restating "there is no law" in every cell would be padding; naming what each
system does without one is the finding.

**Where the record substitutes literacy for regulation, say so.** Two instances here and they are the
same move: a consumer-education campaign on fraud while no rule allocates the loss, and a deepfake
awareness campaign with no legislative or platform-facing instrument. The ledger notes say it
directly in both cases ("public literacy is standing in for regulation"; "the consumer's position
after a fraud is exactly where it was"). Carry that judgement into the cell — it is the analysis, and
a neutral summary of the campaign would have discarded it.

**File by what the evidence establishes, not by the instrument's own subject.** The satellite rollout
to 300 health facilities went to `digital.rural--digitalisation-of-rural-health-clinics`, not to
satellite availability: the finding is the dependency — one foreign operator, no public contract, no
alternative transport named — rather than the connectivity. Same test as NGA's surveillance cluster
and SEN's breach placement.

**A dispute inside government is stronger evidence than an outside observation.** Two identity
platforms are being built at once and the identity agency has *publicly warned against parallel
systems*. That makes the duplication contested on the record rather than merely noticed, which is
what lets the cell say it plainly.

## What SOM added, 2026-08-27

50 sourced rows of 60, 37 indicators, fifth unit running with nothing unmapped.

**Hold both halves of a split verdict in the same cell rather than picking one.** This unit is
genuinely ahead of several larger ones on institutional sequence — a data protection statute in force
since 2023, regulations adopted February 2026, the authority's first nationwide enforcement step in
June; a cybersecurity law, a framework and an incident response team inside twelve months. It is also
a state where about 2m of an estimated 19.7m people hold the identity credential, two member states
sit outside the national register, and one runs its own identification authority. Writing either half
alone produces a false unit. Each institutional cell states its own qualification — the authority's
independence is qualified by executive appointment and override powers; no caseload, budget or
enforcement action is published for the cyber stack — so the reader gets the sequence and the capacity
in the same place.

**An operating-reality note belongs in the cell, not just on the ledger.** The immunisation register
carries "power and connectivity gaps force recording on paper and uploading later". That single line
is the honest qualifier on every digitisation claim in the unit, and it only reaches a reader if the
cell keeps it.

**Where two accounts of legality are unreconciled, say they are unreconciled.** The credential was
made compulsory for inter-state travel; a published legal analysis holds the proclamation exceeds a
statute that confers a *right* to a credential and imposes no *duty* to obtain one. The ledger says
the two accounts have not been reconciled. The cell says the same and adds the consequence — that
compulsion at ~2m of ~19.7m is an exclusion question before it is a legal one — without adjudicating
the law.

**A regional gap can only be seen from a national ledger sometimes.** The e-commerce strategy row
records that the lender finds no strategy in this country, in a neighbour, *or* at the regional body.
That is worth stating plainly when a national row happens to carry a regional finding.

## What SSD added, 2026-08-27

66 sourced rows of 74, 44 indicators, sixth unit running with nothing unmapped.

**When one fact explains half the other cells, give it its own cell and let the others point back.**
This unit has no operating Official Gazette — a committee was given fourteen days in January 2026 to
launch one and clear a backlog of every law since 2011, no edition is on file, and a protocol issued
the week before classifies documents bearing the President's signature as privileged executive
communication that cannot be photographed, scanned or shared. That single entry is why the ICT
Authority's statutory basis is unresolvable, why the cybercrime Act's text is withheld, and why a
passport validity change is reported as both done and pending. It went to
`gov.legislate--access-to-information-legislation` as the finding, and the affected cells say "which
is recorded separately" rather than each re-explaining it. Compare SLE, where the framing absence (no
data-protection law) belonged in the legislation cell and the others named what they lacked: same
shape, and the choice each time is which cell a reader would actually look in.

**Two ledger rows here carry the whole of their own reconciliation history in the note, closed
unresolved.** The ICT Authority and the national data centre both record two attempts, what registers
were checked, and why the silence settles nothing. **Compress that into the cell, do not summarise it
away.** "The registers are not current enough for their silence to settle anything" is a finding; "the
status is unclear" is not.

**State a concentration plainly when nothing published explains it.** One privately held Swiss company
of about nine people holds the international gateway *and* the national data centre. The exclusive
e-government concession behind the visa portal and the tax platform was signed without tender, its
revenue share put at 75 per cent by a UN commission and 2 per cent by the company, and the company was
sanctioned by the United States. Each fact is on the ledger; putting them where a reader meets them
together is the mapping's contribution.

**Register-check bites differently on a short cell.** One cell failed the 25-word floor on
`developments` — the first time in this pass. A single-row cell about a ministerial visit genuinely
has little to say; the fix was to state what it is *against* (untendered backbone, consultant-led
spectrum strategy, privately operated gateway), which is analysis rather than padding.

## What STP added, 2026-08-27

36 sourced rows of 49, 27 indicators. Seventh unit running with nothing unmapped, and **the first
with a clean pre-lint on the first attempt** — the ledger carries almost no figures, so check H had
nothing to bite on. Worth knowing: the defect rate tracks the ledger's figure density, not the unit's
size or difficulty.

**Name the evidential condition when it is the finding.** Here one lender mission report of September
2025 is the sole source for four separate items — the identification law, the submarine cable, the
incident response team, the business registry diagnostic — and the same lender's project finances the
digital identity, the citizen portal, the interoperability platform, the response team and the data
centre. The finance cell says that concentration outright. Writing each item as if independently
evidenced would have made a thinly-sourced programme look like five programmes.

**A superseded model is a substantive finding, not a footnote.** The 2016 data-protection law is
modelled on a European directive Europe itself replaced in 2018. The cell says so and says what
follows: the regime the authority enforces is two generations behind the standard its own cooperation
partners work to. That reading is available from the ledger note and vanishes under a neutral
summary.

**A specific failure sometimes carries a general lesson — state both.** The first automatic electoral
roll derived from the civil registry missed about 1,860 eligible voters, because the derivation
reproduced the source register's own omissions. The cell states the incident and the lesson:
automating a derivation inherits the source's gaps. That is the kind of sentence the frame exists to
produce.

**Record an unusual governance arrangement as unusual.** The data-protection authority was assigned to
supervise the registry-to-electoral-database interconnection at the point it went live — the only
such assignment seen in this pass. Saying "the only instance in this base" is a claim about the
corpus, so make it only when the pass actually supports it.

## What SWZ added, 2026-08-27

79 sourced rows of 86, 43 indicators. Eighth unit running with nothing unmapped.

**Put the unit's single strongest fact where a reader will meet it, and let the qualification travel
with it.** The data-protection authority's first major investigation was opened against a *government
ministry* — which had published unblurred national identity documents and missed the statutory
72-hour notification. That sits in `gov.protect--data-protection-authority` with the mandate
statement (the ICT ministry saying on the record that enforcement is the regulator's, not its own)
beside it, because the two together are what make the authority's position legible.

**A statute that names its own enforcer ambiguously is a limit on every downstream cell — state it
once, upstream.** The gazetted Act names a Commission; the regulator's pages describe it as the
designated Agency. That went in the legislation cell with the sentence "a statute whose enforcing body
is ambiguous on the face of the record is a limit on everything the protection cells below can say".
Same move as SSD's gazette and SLE's absent law: one cell carries the constraint, the rest inherit it.

**Name the gap between the regime being written and the practice on the ground.** Sector and health
data-protection guidelines are in validation workshops while individual public schools already charge
pupils about E200 for biometric gate passes without ministry approval. Four laws — cybersecurity,
critical infrastructure, e-commerce, AI — were named as forthcoming a year ago *alongside* a capital
deployment of 59 AI-enabled cameras that is in progress. In both cases the cell states the sequence
rather than reporting the instrument and the practice as separate items.

**A self-assessment is stronger evidence than an external one — say whose it is.** The Digital
Landscape Assessment finding that critical information is at risk in nine ministries and systems are
not interoperable was *received and endorsed by the ICT ministry*. That makes it the state documenting
its own exposure, which is why the cell reads Regressed rather than hedging.

**Ninth and tenth apostrophe-in-label failures.** "prime minister's year-end statement", "women's
digital academy". The rule from SEN stands and is still being broken: do not put possessives in `L()`
labels.

## What SYC added, 2026-08-27

48 sourced rows of 54, 34 indicators. Ninth unit running with nothing unmapped, and the second
consecutive clean pre-lint — again a low-figure ledger, which confirms the STP observation that the
defect rate follows figure density.

**Where a law and its enforcement diverge, put them in adjacent cells and make each point at the
other.** The Data Protection Act 2023 is fully in force with an express cross-border interoperability
provision, which is genuinely ahead of most of the frame. The Information Commission that enforces it
states in its own whitepaper that it has *no clear power to enforce its orders*. The legislation cell
closes with "what it lacks is recorded in the next cell"; the protection cell says the gap is what
decides how much weight the statute carries. Neither cell overclaims and the reader gets the whole
picture from either entry point.

**A live pairing like that then earns its keep in a third cell.** The video-enforcement pilot
repurposing the public camera estate for automated ticketing states no data-protection basis — and
the cell says this matters *more* here than in a unit with no statute, because the safeguard exists in
law and not in practice. That is the kind of sentence that only exists because the two governance
cells were written to be read together.

**State a sovereignty question as open when the record leaves it open.** The national digital identity
runs on a foreign vendor's platform with no source addressing licensing, hosting or exit terms; the
ledger note calls the question open and the cell says so. Same for the Chinese vendor relationship
supplying the incumbent 5G core, a schools programme and a proposed emergency-communications core with
no procurement terms or security review published.

**A comparative observation is allowed when the pass supports it.** This unit required local
incorporation before licensing the satellite operator, where several others in the frame licensed the
same operator on a full foreign-ownership basis. That is a claim about the corpus and the pass has now
seen enough units to make it.

## What TCD added, 2026-08-27

90 sourced rows of 132, 44 indicators. Tenth unit running with nothing unmapped. Note the ratio: 42
rows carry no source at all, the largest unsourced share in the pass so far, so 100 per cent here
means every *sourced* row placed and a third of the ledger correctly left out.

**When a unit inverts the frame's usual sequence, say so once, plainly, in the cell where the
inversion happens.** A law on biometric data in judicial procedures was adopted 138 to 1 while no
general data-protection statute or authority exists — the function was folded into the security
agency. The legislation cell says: "Legislating the collection of biometric data for judicial use
before legislating data protection at all is the sequence, and it is the reverse of the order every
other unit in this frame attempts." That is a claim about the corpus, and by unit ten the pass
supports it.

**Then let each downstream cell name its own missing safeguard rather than restating the absence.**
Five separate collections run without protection: the register's real-time feed to the finance
ministry, the subscriber-data partnership, the satellite order's identification-and-retention
mandate, the police cybercrime equipment, the refugee enrolment. Each cell names the specific thing
unstated for *that* system. Same discipline as SLE.

**Carry unresolved figures as unresolved.** Three accounts round one birth-registration total to
2.948m, 2.95m and 2.958m — the cell gives all three and says they are three figures for one number.
The digital transformation project's envelope appears as FCFA 76.45bn and US$92.2m, close to total
project cost and to grant alone respectively, with no source saying so. Picking one would have been
inventing a reconciliation.

**A `KeyError` from the row-id lookup is the cheap failure mode.** One row was cited under the wrong
subject prefix (`data.statistics-` for a `finance.new-` row). `S(row_id, i)` raises immediately, so it
costs one run — which is exactly the argument for reading slugs through the ledger rather than
transcribing them.

## What TGO added, 2026-08-27

85 sourced rows of 124, 47 indicators. Eleventh unit running with nothing unmapped.

**The unreadable-instrument problem has now appeared in four units (SSD, SWZ, TCD, TGO) and TGO is its
purest form.** Both overarching strategies unheld, with the base unable to say whether two names denote
one instrument or two; two decrees adopted at a single Council session, neither readable, and the
parent fee decree held as an image scan with no text layer so the baseline rates are unreadable too;
an anti-money-laundering law with no promulgation date, number or gazette reference; and rules on
mobile commercial offers evidenced *solely in one line of the accounts of the company they bind*. The
policy cell states the frame once — "two overarching instruments, neither readable, is the frame
against which every delivery below has to be read" — and the rest inherit it.

**Sequencing findings belong in the cell where the sequence happens, not in a summary.** Satellite
spectrum royalties were amended while no satellite licence has been granted, twelve months after the
operator listed the country as available: that goes in the satellite cell. Digital cadastral
submission was made mandatory with no fallback, *before* the georeferencing that would give it a
reliable base and four months after the positioning network that would underpin both was launched with
no operator named: that goes in the land cell. Neither reads as a finding if written as a bare
chronology.

**Where the accounts describe one thing four incompatible ways, say so and give none.** Instant-payment
participation is variously "integrated", "operational", "committed" and "authorised to open to the
public" across four sources, and the counts are not one series. The cell says that, and adds that a
single participation figure would be manufactured. Same discipline as TCD's three birth-registration
totals.

**Register terms still catch idiomatic prose.** "start-up ecosystem" tripped the jargon rule — the word
is banned outright, including inside a compound where it reads naturally. Cheap to fix, worth
remembering that the lint does not care about idiom.

## What TUN added, 2026-08-27

73 sourced rows of 77, 39 indicators. Twelfth unit running with nothing unmapped.

**Get the instrument type right, because the ledger has done the work and a summary would lose it.**
The 2020-2025 digital strategy lapsed at term and what replaced it is a *chapter of the development
plan*, not a strategy — the ledger note says explicitly "a change of instrument type, not a renewal:
what the wiki and outside commentary called a national digital strategy is a plan chapter". The cell
carries that and states why it matters: a plan chapter is approved by finance law and has no delivery
machinery of its own. And every volume of the annex held is marked draft with no as-enacted printing,
so the legally binding content of the digital plan cannot be read.

**Three unresolved counts, three different reasons, all carried.** The data-protection bill's article
count is settled at 132 from the tabled Arabic text — a committee account's 123 reads as a
transposition matching the tabled structure section for section, and a third account's 32 is a
leading-digit loss in optical transcription. Active wallets differ by ~1.7× between an aggregator and
direct bulletin reporting, and only the aggregator side is held. The project portfolio is 114 in
execution against 192 under tracking with no reconciliation. **Where the ledger has already done the
reconciliation work, carry its conclusion *and* its reasoning; where it has not, say the divergence
stands.**

**Adjacent cells again, for a specific contrast.** The linked health dataset has no legal basis held
while the portal serving it has completed a cybersecurity audit — technical assurance ahead of legal
assurance. Placed in `gov.protect--national-data-protection-readiness` and `dpi.mis--health` so each
names the other.

**A withheld licence can be a policy position rather than a delay.** The satellite licence is withheld
over *routing* — the state wants low-earth-orbit traffic through a local ground station and a national
interconnection point. Stated as the sovereignty position it is, not as an administrative backlog.

**check H can fail on a file the pass did not touch.** Here `TUN-monthly.md:134` carries an uncited
block; `indicators.csv` passed clean. Read the path in the message before assuming the draft is at
fault — the register check covers the whole unit, not just the new file.

## What TZA added, 2026-08-28

137 sourced rows of 150, 61 indicators — second-largest unit after NGA. Thirteenth running with
nothing unmapped, and **the first in this pass where the render check passes clean on every check
including L**, which has failed on every other unit for unwritten narrative blocks in the progress or
status document.

**By unit thirteen, a corpus-wide superlative is a claim the pass can support — state it and bound
it.** Two here. The identity register's 138-plus connected institutions is "the hardest adoption
figure this base holds for any African identity-verification rail" (the ledger's own words, carried).
The ports authority chatbot carries "the only measured outcome attached to a public-sector AI
deployment anywhere in the base" — and the same sentence says fifteen domain experts is a usability
study rather than a deployment audit. **Make the claim and bound it in one breath**, or it reads as
promotion.

**Three unreconciled figures, three different reasons, all carried.** Under-five birth registration
quoted at 65 and 68 per cent a week apart by the same minister — the ledger calls that "the clearest
available demonstration that the figure is quoted rather than published", which is a better sentence
than any paraphrase. Smartphone users falling quarter on quarter while the percentage rises. Cables
and landing stations counted on two bases nothing reconciles. **And where the ledger has already done
the reconciliation** — the backbone's 16,280 planned / 13,820 at April 2025 / 15,167 at December 2025,
with the "over 15,000 km" quoted at a July 2026 summit correctly identified as the December figure —
carry the resolution *and* the reasoning.

**An asymmetry between two enforcement numbers is itself the finding.** 39,117 numbers blocked against
56 incident reports to the police, no conviction or restitution figure held. The ledger says "blocking
is not prosecution"; the cell says it too, and adds that prosecution running three orders of magnitude
below disconnection is the shape of enforcement rather than a reporting gap.

**Register terms keep catching ordinary phrases.** "at scale" tripped the jargon rule inside
"disconnection at that scale" — grammatically innocent, still banned. Same lesson as TGO's "start-up
ecosystem": the lint matches the string, not the sense.

## What UGA added, 2026-08-28

143 sourced rows of 159, 61 indicators — third-largest ledger after NGA and TZA. Fourteenth running
with nothing unmapped.

**When a system both works and fails, the cell holds both.** 28,571,893 legacy records migrated
successfully in the platform's first brownfield migration; the enhanced card's machine-readable code
does not work and has not since at least February 2026; over 60 per cent of printed cards are
uncollected. Three facts, one credential, and the temptation is to lead with whichever fits a
direction. The `dpi.id--robustness-of-system` cell carries the migration and the code failure
together, with the parliamentary record's detail (functionality never integrated, fix promised by 31
March) kept because that is what makes it a failure rather than a delay.

**A fee, a population and an enrolment rate are one finding when read together.** The alien identity
card: 1,875 enrolled in ten weeks, a scope of which ~1.95m are refugees or asylum-seekers, a US$100
fee, and nothing published about a waiver or what a resident foreigner does who cannot pay but needs
a SIM or a bank account. The ledger note assembles that; the cell keeps the assembly intact.

**A ratio inside a headline count is often the finding.** The state technology institute reports 48,000+
trained in one year — of whom fewer than 4 per cent were government officers. The cell says the
institute is largely not training the state, which the headline number conceals.

**Two reconciliations carried with their reasoning.** The election shutdown's duration depends on which
endpoint is named (four days / almost five / thirteen) — "a duration must name its endpoint" is the
ledger's phrase and it is better than any paraphrase. And the US health arrangement: the signed
memorandum provides only for a *future* data-sharing agreement, while a published investigation
describes reviewing that agreement and finding real-time access to nine systems. **Different
instruments, not a conflict** — and saying so is what stops the cell reading as either a denial or an
exposé.

**Word-band failures come from summaries, not developments.** The first 8-40 band failure of this pass
was a 42-word summary that had absorbed an em-dash aside. Developments has 25-200 words of room;
summary does not.
