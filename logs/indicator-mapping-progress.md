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
CAF, CIV, CMR, COD, COG, COM, CPV, DJI, DZA, EGY, ETH, GAB, GHA, GIN, GMB, GNQ, KEN, LBR, LBY** — 27 of 54, one commit each, all pushed.

Yields so far, as a sense of shape: 21 indicators from GNB's 25 ledger rows, 43 from BDI's 74, 52
from BWA's 107, 57 from BEN's 105, 64 from BFA's 131, 66 from AGO's 122, 43 from CAF's 92, 92 from
CIV's 167, 73 from CMR's 121, 67 from COD's 123, 52 from COG's 103, 45 from COM's 117, 49 from CPV's 140, 43 from DJI's 70, 58 from DZA's 111, 66 from EGY's 199, 66 from ETH's 97, 58 from GAB's 120, 81 from GHA's 175, 59 from GIN's 109, 46 from GMB's 75, 42 from GNQ's 67, 93 from KEN's 219, 43 from LBR's 71, 64 from LBY's 84. Between three quarters and nine tenths of ledger rows map; the rest are placeholders with
no source, or real instruments the frame has no question for (a telecoms statute, a broadcasting
transition), and those correctly stay on the ledger and out of the report.

## Remaining

27 country units: LSO, MAR, MDG, MLI, MOZ, MRT, MUS,
MWI, NAM, NER, NGA, RWA, SDN, SEN, SLE, SOM, SSD, STP, SWZ, SYC, TCD, TGO, TUN, TZA, UGA, ZMB, ZWE.

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
