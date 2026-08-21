---
type: runbook
title: Job 1 — build outputs/ from OSINT — instruction for Claude Code
last_reviewed: 2026-08-16
---

# Job 1 — build the outputs — runbook for Claude Code

*(Hand this to Claude Code in the Corpus repo. Job 1 turns OSINT's evidence into Corpus-owned `outputs/`. Job 2 (`RENDER.md`) then renders `outputs/` into the site. **To run both in one go, use `CYCLE.md`**, which orders the two and changes nothing in either; this file is unaffected by it and runs alone exactly as written. Read `documentation/migration-report-layer.md` for the architecture and `documentation/report-layer.md` for the record layer stage 4 works to. OSINT is read-only throughout — never write to it. **Reading is unrestricted** (`CLAUDE.md`; Bill, 2026-08-14): the workroot junctions `raw/`, `wiki/` and `lookups/`, and adding another is a line in `setup_workroot()` rather than a boundary decision. It junctions **only what a stage reads**, because each one is a directory of OSINT's exposed to a process that can write — and `index/` is not among them at all: Corpus builds its own. The boundary is the write, and it is absolute.)*

## Running unattended — a run never stops to ask

**BUILD puts no question mid-stream** *(Bill, 2026-08-16)*. It is run back to back with `RENDER.md` with nobody watching, so a question asked at stage 4 is a job that has silently halted a third of the way through with a prompt on a screen no one is reading — and the units after it never get their work. A run ends exactly two ways: it **finishes**, or it **fails**. A failure is an error the run cannot get past. It is never a decision the run would rather Bill made.

**Where this runbook says a human rules, BUILD rules.** Every such point is named below with the path to take — stage 4's checks, the register check, the status baseline's verification. BUILD is the drafter and the register is its own standard; there is no judgement here that needs Bill's authority, only ones that used to have his attention available.

**Where BUILD wants Bill's attention, it finishes the job and leaves a message.** `logs/messages-for-bill.md` is the channel: newest first, one block per run, inserted under the marker. Write what he would have been asked, what the run did instead, and what his options are. A run that needed nothing writes nothing there, which is the normal outcome.

**Only the leak gate stops a finished run.** Every other check in Job 1 is a work list, not a gate — the tally at check L says so in as many words, and the log shows runs shipping with M outstanding. A failing check is BUILD's work to do, and where it cannot be done the true statement is ***Not held*** with a `gaps.csv` line, which is a completed outcome and not a blocked one.

**An interrupted run is resumable and is not a failure to repair by hand.** Stage 4 reads a set difference over slugs, so a run that dies mid-stage leaves every unit it finished marked and every unit it did not untouched; the next run picks up exactly there. The danger is not the interruption, it is the interruption going unnoticed: a half-moved build typesets cleanly, resolves every link and passes every check, so nothing downstream can tell it from a finished one. That is what stage 0 is for.

## The two kinds of work in Job 1

Job 1 has scripted stages and one model-authoring stage, and they are run differently.

The **compiles** (vocab, catalogue, finance, budgets) are pure functions of OSINT's `raw/` and `lookups/`. They are `scripts/rebuild.py` and they just run.
The **report update** — moving the ledgers forward as new sources arrive — is a model stage. A script (`report-scan.py`) says *which* sources are new; a model reads them and decides what moves. It cannot be a plain script, and it belongs here, in the build, run every time Job 1 runs.

**BUILD authors this content; it does not transcribe it** *(Bill, 2026-08-14)*. BUILD holds editorial control over everything in `outputs/` and its job is to produce the best output it can, full stop. The scan is a convenience that stops the build re-reading what it has read — it is not a work order BUILD is confined to, and a unit the scan did not nominate is still BUILD's to improve. Where a document can be made better, BUILD makes it better. Questions about what is published, what is still being tested and what any of it costs are Bill's, and are not BUILD's to weigh.
Three further stages are deferred and named at the end: report initialisation from the wiki (for a brand-new place), the monthly narratives, and topics.

## Prerequisites

- OSINT checked out and readable (`OSINT_PATH`, default `C:\OSINT`). On this machine `raw/` is local, so the scan and renders are fast.
- Run from the repo root. Commit after each coherent stage.
- **The index is Corpus's own and needs nothing from OSINT** *(Bill, 2026-08-14)*. It is built into the gitignored workroot at `scripts/.workroot/index/` from `raw/` and `wiki/`, rebuilds itself whenever either moves, and takes about 5 seconds over 12,588 files. Nothing here waits on an OSINT maintenance step, and OSINT's own `index/` is not read at all. If a run ever raises `vault_lib.ForeignIndex` or `EmptyIndex`, it was started from the wrong root — stage 4 and 5 run **from `scripts/.workroot/`**, where `raw/` and `wiki/` resolve; from the repo root there is no base to index and the guard says so rather than writing an empty index.

## Stage 0 — declare the run

```bash
python -c "import datetime,io; io.open('logs/.build-in-progress','w',encoding='utf-8').write('started {:%Y-%m-%d %H:%M}\n'.format(datetime.datetime.now()))"
python scripts/log-line.py --start build
```

**The second line is what puts a duration on the run's log line** *(Bill, 2026-08-17)*. It stamps the clock into the gitignored `logs/.run-start-build`, and the closing call in the ending sequence reads it back and clears it. Run it here, at the top, rather than deriving a start time later: a duration reconstructed at the end of a long session is a recollection, and the reason for logging it at all is to have a measurement. A run that skips this still logs — the line reads `unclocked`, which is the visible version of not knowing.

It does not replace the sentinel above and the two are not interchangeable. The sentinel answers *is a run unaccounted for*, which RENDER Step 0 acts on; this answers *how long did that run take*, which nothing acts on and Bill reads.

**A resumed run re-stamps, so its duration is that sitting and not the whole job** *(corrected 2026-08-17)*. This paragraph used to claim the opposite — that a run which stops and resumes keeps its original stamp and reports the job end to end — and stage 0 is where that falls down: a resuming session runs stage 0 like any other, and `--start build` always overwrites. `scripts/log-line.py` is explicit that it should, because a stamp left behind by a run that died is one the next run clears rather than inherits. Making the resume skip the stamp instead would put a condition on stage 0 for an unattended run to evaluate about its own inputs, and would let a stamp from a run that died last week hand today's run a duration of days.

**So the line says that it resumed.** A resumed build did part of the work in the time it reports, and a reader comparing it against a full run is comparing two different things unless the message says which it is — the same reasoning as `unclocked`, which states a fact about the run rather than dropping the field or guessing at it. Where the whole-job figure is the one worth having, state it outright with `--since` on the closing call; that is what the override is for, and it is a measurement rather than a flattering estimate. `CYCLE.md` step 1 asks for the same note where the sentinel is found at the top of a cycle.

**The file exists for exactly as long as a run is unaccounted for** *(2026-08-16)*. It is written here and removed in the ending sequence — on a clean finish *and* on a logged error, because both of those are runs that reported themselves. What it survives is the third case: a session that dies without saying so, which for stage 4 means running out of context somewhere in the middle of 54 units. `RENDER.md` Step 0 refuses to render while it is present, and that refusal is the whole of the mechanism.

It is gitignored, so it never reaches a commit and never travels. That is correct — it is a statement about this machine at this moment, not history. Note the stage in it as the run moves if that is cheap; the resume does not need it, since the slug set difference already knows, but a message to Bill reads better for naming where the run stopped.

## Stages 1–3 — the compiles (scripted)

```bash
python scripts/rebuild.py --all        # vocab snapshot + catalogue + finance/budgets + the scan work order
```

This writes `outputs/catalogue/`, `outputs/non-state-finance/`, `outputs/budgets/`, refreshes `outputs/vocab/`, and prints the report-update work order (stage 4 below). Commit `outputs/` and `outputs/vocab/`.

**Stage 2 is now a precondition of stages 4 and 5, not just a sibling of them** *(2026-08-14)*. The report layer resolves every citation through `outputs/catalogue/raw-catalogue.csv` — Corpus's own published table, the one a reader can download — rather than through the index it is built from. So a run that renders reports against a catalogue older than `raw/` would be publishing links from a stale table, and `report-render.py` refuses: it recomputes the catalogue's stamp (records and newest mtime, about a quarter of a second) and raises `vault_lib.StaleCatalogue` naming the repair, which is to run this stage first. Running `--all` as written satisfies it in the right order.

### Stage 2a — the scope lint (belts and braces on a rule OSINT owns)

**The remit is Africa, and non-African material is admissible in exactly two cases** *(Bill, 2026-08-20)*: a **sovereignty** issue that files under one of the closed `geopol.*` slugs, and material treating the **global south generally**, which is what the `XGL` place already means — `countries.csv` labels it *Global/Developing Countries*. A single non-African country's domestic story is out however good it is: Japan's training-data rule, Korea's teen-algorithm debate and India's market-regulator AI rules are all digital governance and none of them is this base's subject.

**Applying that rule is OSINT's job and Corpus cannot do it.** The records are OSINT's, `C:\OSINT` is read-only, and the screen belongs where the body is read. `scripts/lint-scope.py` therefore **notices rather than enforces** — it reads the catalogue stage 2 has just written and sorts every record three ways: **in** (an African place, or a `geopol.*` tag), **XGL unverified** (placed `XGL` with no `geopol.*` tag — admissible if it earns the code, which is a reading of the body a lint cannot do), and **unaccounted** (no African place, not `XGL`, no `geopol.*` tag).

**The unaccounted bucket is a review list and not a delete list, and that was learned from its first run.** It put Jumia's capital raise, Flutterwave's correspondent accounts and MTN Bayobab's management appointment in the same bucket as Thailand's passport — African stories whose `places` field is simply empty, where deleting the record would lose real material. A third group belongs in neither: the ITU Global Connectivity Report and the SubOptic cable programme should carry `XGL` and do not. So the bucket asks *has this record accounted for its geography*, and the answer is one of delete it, place it, or code it `XGL` — each of them OSINT's call.

**It reports and never gates**, under *Only the leak gate stops a finished run* above. An out-of-remit record is a work item for OSINT, not a reason to withhold a build of the other ten thousand. Carry the counts in the run's log line; where the arrivals are new, write them into a note for OSINT rather than a message to Bill, because the repair is not Corpus's to make.

**Clearing a deletion means checking every layer, and the first attempt checked two** *(OSINT's `notes-for-corpus.md` note 2, 2026-08-20)*. Before telling OSINT a set of records is safe to delete, Corpus says what it would cost here. Note 30's clearance read the **ledgers** and the **status baselines**, found nothing, and said so — correct as far as it went. But 18 of the 48 records were cited inside OSINT's own `wiki/`, which Corpus reads and reports from, and the 26 deletions left 19 dangling references across eight concept pages. OSINT found and repaired them itself. **The lesson is the method, not the incident**: a clearance that reads only the layers Corpus writes will keep missing the layers Corpus *reads*. Check `wiki/` alongside `outputs/reports/*/ledger.csv` and the baselines, and say which layers were searched rather than reporting a bare *nothing found* — a check that read two of three looks exactly like one that read all of them.

**And the leak was never only at the door.** Those eight concept pages had a settled practice of holding non-African domestic stories as comparators under `[[XGL]]` — self-described in the bullets as *"comparators rather than African news"*. The remit rule retires that practice, which means the arrival counts this lint reports are the smaller half of the problem; the standing stock inside the wiki was the other. That half is OSINT's and is done.

```bash
python scripts/lint-scope.py --since {last build's date}   # what the last sweep sent
python scripts/lint-scope.py                               # the whole backlog
```

`--since` reads the `ingested` column rather than `published`, because the question is what the last sweep sent and a 2019 paper ingested last night is a new arrival.

## Stage 4 — report update (the ledgers' move; model authoring)

This is the report update. `documentation/report-layer.md` is the spec — Corpus-owned, and the only one; the register below governs the prose. It reads only the sources the ledger has **not** yet considered — a set difference over slugs, not a date window — so an interrupted run resumes cleanly and nothing is re-read.

The work order (from `--all` above, or `python scripts/rebuild.py --scan`) lists each initialised unit and how many unconsidered sources it holds. For **each** such unit:

1. **List the new slugs.** `python scripts/report-scan.py --slugs {ISO3}` (run from `scripts/.workroot/`, which `rebuild.py` sets up). Read each slug's `hub_line`, facets, and body from `raw/` only where the line is not enough.
2. **Decide per source, against that unit's `outputs/reports/{ISO3}/ledger.csv`** — the four outcomes (`documentation/report-layer.md` §1 for the row test and columns, §3 for the two closed vocabularies):
   - *moves a row* — a status, milestone, position or figure changed: set `movement`, put the slug **first** in `sources`, and set `published` to that record's publication date, which is the date at the front of its slug. **`published` is what ages the row out of a report**, so a move that does not update it leaves the row in a window it has left. **The slug goes first, not last** *(2026-08-19)*: `report-render.py`'s `row_url()` hyperlinks the claim cell to the **first** source that resolves, on the stated rule that "sources are listed with the one that establishes the present status first". Appending puts the new record behind the one it superseded, so the table links a reader to the old evidence for the new position — which every check passes, because the link resolves and the row cites something;
   - *mints a row* — a named system or instrument the ledger lacks, passing the row test (a named object whose position can move — not a topic the news covered);
   - *settles a **Not held** row* — strike it from `gaps.csv`, give it a status;
   - *default: nothing moves* — most sources report activity, not movement. Do **not** attach a slug to a row that did not move.
3. **On an initialised unit only, ask the same source the second question** — see *Maintaining the status baseline* below. It is asked of the record already open, not on a second pass, and it is independent of step 2: a source can move a row without touching the baseline, or touch the baseline without moving a row.
4. **Mark every slug read**, moved or not: `python scripts/report-scan.py --mark {ISO3} <slugs>`. (Sources on `origin_status: hold` are dropped by the script, not marked — pass them in regardless.)
5. **Rebuild the unit's documents**: `--doc all`. Each unit has one monthly, one progress report and — until `STATUS-INIT` has run on it — one rendered status report; these are living documents, not dated editions, and a moved row can show in any of them. A build that changes nothing leaves a file untouched and prints `unchanged`.

   **`--doc all` means all of *this* unit's documents, and the renderer decides which those are.** A region issues the progress report only; a unit whose status report carries `built_by: STATUS-INIT` no longer issues a rendered status report at all, and `--doc all` renders its other two. Naming a document a unit does not issue prints the reason and skips. So this line is the same on every unit and no caller has to know which is which.

   **No fact is added without a source** *(Bill, 2026-08-14)*. The citation goes on the sentence carrying the fact, not somewhere else in the block: a paragraph whose opening sentence is linked does not thereby source the three that follow it. Check H asks only that a block carries a citation at all, which is the cheap half — the rule is the drafter's. Three kinds of sentence carry no link and are right not to: a statement of what the base does **not** hold, which is a claim about the record rather than about the world; a qualification of a fact already cited in the same sentence (*the figures are the operator's own*); and the single connecting sentence the register allows, which asserts nothing. Everything else needs its link, and a summary block is where this goes wrong most easily, because it restates facts drafted elsewhere and their citations are easy to leave behind.

   **A source being in scope does not make every fact in it in scope** *(Bill, 2026-08-14)*. The window selects *rows*, by the publication date of the newest record they cite. It does not select *facts*. A July source that restates a 2023 measurement puts its row in the monthly, and the 2023 measurement still has no business in a report of what moved this month — it belongs in the status report, where the current position lives. The same goes for a stock figure a year old carried forward by a fresh article. **The monthly reports developments; selection is the drafter's, not the scan's.** Where the standing position is the only thing a row offers, the right outcome is to leave that row out of the prose and let the ledger carry it.

   **Moving a window on is an editing job.** The renderer carries every narrative block across; deciding what still belongs is BUILD's. Both windows overlap their previous position heavily — the monthly always spans a month boundary, the progress report keeps eleven of its twelve months — so **BUILD removes what has aged out and writes in what has arrived**. A carried sentence describing a period that has moved on is well-formed prose and passes every check; finding it is the point of the revision.
6. **Verify** before moving on: `python scripts/report-render.py --unit {ISO3} --check` — checks G (every link held in `index/`), I (vocabulary), **J (no document compiled before the ledger moved)**, **L (no unwritten narrative block)** and **M (every row that states a position cites a source that resolves)**; then the register check `python scripts/report-register-check.py --unit {ISO3}`.

   **A failing check is work, and BUILD does it in the same pass** *(2026-08-16)*. This is the rule that replaces *must all pass*, which was never what happened — the log shows full runs shipping with L at 44 and M at 22 — and an instruction the runs visibly do not follow is worse than none, because it leaves the actual policy undeclared. G, I, J and M are mechanical: a link that does not resolve, a term outside the vocabulary, a document behind its ledger, a row citing a slug that is not there. Each has one repair and BUILD makes it. L is authoring work and the two outcomes are the ones under *Narrative integrity* — write the sentence or remove the section.
   **Where a check cannot be cleared, the fallback is already in this runbook and it is a finished outcome.** A position BUILD cannot source is ***Not held*** with a `gaps.csv` line; a link that resolves to nothing is struck along with the claim standing on it. Neither is a question for Bill. What is left after the repair pass goes in the run's log line as a count, unit by unit, exactly as it does today.
   **The register check reports and BUILD rules** *(2026-08-16)*. The script says a person rules, and under `RENDER.md`'s back-to-back run BUILD is that person: it holds editorial control over everything in `outputs/`, and the register is Corpus's own standard rather than an external one it needs permission to apply. A hit inside quoted source text stands — an agency that says *attack surface* is quoted as saying it. A hit in BUILD's own prose is rewritten. Log the residual count; message Bill only if clearing a hit would mean dropping a fact the report needs.

   Check J skips the status report on an initialised unit. It asks whether a document is behind the ledger it is rendered from, and the baseline is not rendered from that ledger — its sources are largely ones the wiki does not hold, which is what `STATUS-INIT.md` means by the baseline sitting outside the collection perimeter. Whether the baseline is current is the question step 3 asks, and it is answered by revising the section rather than by re-rendering the file.

## Maintaining the status baseline

**Once `STATUS-INIT` has run on a unit, the status report is BUILD's to keep current, and BUILD never re-renders it** *(Bill, 2026-08-15)*. `STATUS-INIT.md` establishes the baseline once and says so: *"Keeping the baseline current is a successor's job, not this one's."* This is that job.

The rule is the inversion of the one it replaces. The ledger render treated the status report as a derived view, so every build could rebuild it from scratch; the baseline is authored, drawing on sources the wiki does not hold, and a rebuild from the ledger would not update it but destroy it — while reporting a normal successful build. So `report-render.py` narrows the document set on an initialised unit and `--doc all` no longer includes status. **The units that have not yet been through `STATUS-INIT` are not part of this**: their status reports stay ledger renders, rebuilt as before, and the question below is not asked of them until the day initialisation reaches them.

**It is one more question asked of a record already open, not a stage.** BUILD is reading each new source against the unit anyway, which is the expensive part; asking a second question of it costs almost nothing, and asking it at any other moment would mean re-entering a base someone has already left.

**The question is whether the source changes what a sub-section can say — not whether it is relevant to one.** Most sources are relevant to a sub-section and change nothing: the baseline states the current position, and a report of activity consistent with that position leaves it exactly where it was. **Nothing changing is the normal outcome and is not a failure**, the same as the *default: nothing moves* outcome in step 2. The source changes the baseline in two cases: the position it states is no longer the position the baseline states, or the baseline says nothing can be established and now something can.

**Where it does change, revise that one sub-section in place.** Not the document, not the chapter — the sub-section whose slug the fact answers, edited as prose.

- **The superseded fact comes out.** A baseline that accumulates is an archive, which is the decay `STATUS-INIT.md` exists to prevent. A revision replaces; it does not append.
- **A borderline source changes nothing.** `STATUS-INIT.md` → *When the evidence is borderline* governs a revision exactly as it governs an initialised section, and the asymmetry it rests on is sharper here: the baseline is what BUILD reads every subsequent source against, so an error written into it corrupts the judgement that decides what gets written into it next. A source that would only support a coarser statement than the section already makes is not an improvement, and one that merely disagrees with a held position without outranking it settles nothing. Where two accounts of equal tier conflict, the section is left as it stands.
- **The first sentence may have to change.** The status writing rules are `STATUS-INIT.md` → *Writing*, unchanged and in force: the opening sentence carries the news — the best-evidenced news — so a revision that changes what is newest in a section changes its opening line and not only a figure buried in the third one.
- **No apparatus, and every time-varying figure dated.** A maintained section is indistinguishable from an initialised one; nothing marks it as revised, and the document carries no changelog.
- **The citation resolves by construction.** The source arrived through the daily flow, so it is in `raw/` and therefore in `outputs/catalogue/raw-catalogue.csv` — which is the one respect in which maintenance is easier than initialisation, where most links come from the AfDB dataset and the vault does not hold them.
- **No acquire line is ever written here.** `C:\corpus-osint-xfer\africa-acquire.csv` reports 2024-or-later material found during initialisation that the daily sweep should have caught and did not. A source reaching BUILD has by definition been caught, so nothing is owed, whatever its date.

**Frontmatter.** Move `compiled:` to the date of the edit, and only when the document actually changed — the house rule, `documentation/report-layer.md` §2. Update `sources_cited`. Leave `built_by`, `hub_last_reviewed` and `intersections_read` alone: they date the initialisation and stay true of it.

**Verification.** `python scripts/status-check.py --unit {ISO3}` — the baseline's own checks, `STATUS-INIT.md` → *Verification*, A to I. Re-run it after the edit pass, not at the end of the unit: check A is set membership, and a URL synthesised from a remembered pattern is indistinguishable from a real one by reading, so an edit that introduces one is invisible until something tests it.

**"Not issued" means the edit does not stand** *(2026-08-16)*. In `STATUS-INIT.md` that sentence governed a document about to be published for the first time, where withholding it was available. Maintenance has no such option — the baseline is already published and is edited in place — so the thing withheld is the revision, not the document. Commit the unit's other work before the baseline edit pass, which puts the last good baseline at `HEAD` and makes this a one-line reversal.
So: a failing A, B or G is repaired first, like any other check. If it still fails, revert the file — `git checkout -- outputs/reports/{ISO3}/{ISO3}-status.md` — re-run `status-check.py` to confirm the baseline is back where it stood, and write the message saying which source prompted the edit and why it could not be made to pass. The published baseline passed; a revision that does not is a regression, and A is the sharpest case, because a URL synthesised from a remembered pattern reads exactly like a real one and an unverifiable link left standing is a fabricated citation in a document a reader can download. C to F, H and I are repaired in place and never trigger a revert.

`report-render.py --check` covers the other two documents and applies check G's widened set to the baseline as well, so both commands are run and neither substitutes for the other.

**Every piece of evidence has a source** *(Bill, 2026-08-14)*. This is absolute and it is not a property of the checks — the checks only find where it has been broken. Nothing BUILD publishes states a position the base cannot show a reader the origin of. A row whose position cannot be sourced is ***Not held*** with a `gaps.csv` line, which is the true statement and the one the layer is built to make; it is never a bare status standing on nothing. `documentation/report-layer.md` §6 has the rule and the single exemption.

A re-render that changes nothing now leaves the file untouched and prints `unchanged` — `compiled:` is the date the document last changed, not the date the build last ran (`documentation/report-layer.md` §2). A unit that reports `unchanged` for all its documents did no work, which is the normal outcome and not a failure.

Commit the moved ledgers, `considered.txt`, `gaps.csv` and re-rendered docs.

**The Corpus register governs the narrative**: light touch, evidence-led, the lens carried mostly by selection, at most one plain connecting sentence per section, and **no figure a reader cannot get to a source for** — which is not the same as no figure beyond the ledger *(2026-08-14)*. A monthly reports developments, and §2 forbids the build becoming a chronology, so event detail that is deliberately not a ledger position belongs in the prose with its citation attached. The ledger is one route to a source, not the definition of one; check H asks only that a source exists. Full statement in `documentation/migration-report-layer.md` → *Corpus editorial register*. The evidential spine — tables, dated figures, the *Not held* count — stays exactly as disciplined as OSINT's.

## Narrative integrity — BUILD owns what is fit to publish

**No document may leave BUILD carrying an unwritten narrative block** *(Bill, 2026-08-13; tightened 2026-08-14)*. Where a narrative block has no prose, BUILD does one of two things, never a third:

- **remove the section**, if there is nothing to say about it; or
- **write the sentence that explains why there is no suitable narrative** — the ledger holds no movement this period, the evidence is too thin to connect, the place has no rows under this heading. Stating the absence is itself evidence-led reporting, and it is the same discipline as publishing a *Not held* count rather than a silence.

Leaving the block unwritten is the third thing, and it is not available. The renderer no longer mints `_(narrative not yet written)_` — a placeholder is a note-to-self that has escaped into a document a reader may download — and the empty block that replaced it says the same thing with the evidence removed. **The renderer does not clear either one**: it carries block bodies across verbatim, because deleting an author's content is not a script's decision. Clearing them is BUILD's, as the whole document is. `report-render.py --check` counts them (check L) so BUILD can see the work; the count is a tally, not a gate on someone else's behalf.

**Empty sections do not arise here at all.** The renderer prints no heading for a section or sub-section with nothing in it, in the monthly and the progress report, so there is no empty box to fill. Only the status report states an absence, and it writes that sentence itself.

**RENDER does not check this and must not.** It renders whatever BUILD produced, because a downstream guard is a second copy of a judgement that belongs here — and one that, when it existed, stopped every render instead of improving a single document. Integrity is maintained where the prose is written, not where it is typeset.

## Stage 5 — re-render (mechanical, always run)

```bash
python scripts/rebuild.py --reports all      # rebuild every report's tables from its ledger, carry narrative across
```

**Run it every time** *(2026-08-16)*. It used to be conditional — *needed only after a format change, or to refresh tables outside a unit you already re-rendered in stage 4* — and that is a judgement an unattended run should not be making about its own inputs, because the condition it turns on is whether something changed underneath the documents, which is exactly what a build is not in a position to be sure of. It is idempotent and it is cheap: a unit whose tables already agree with its ledger prints `unchanged` and its file is not touched, so the cost of running it needlessly is a pass over 165 documents and the cost of skipping it wrongly is a published table that disagrees with the ledger under it.

This is safe to run over every unit, initialised or not: it goes through `report-render.py --doc all`, which does not issue a rendered status report for an initialised unit. A format change therefore reaches the monthlies and the progress reports and leaves the status baselines untouched — which is right, because a baseline has no rendered tables to reformat.

## Stage 6 — topic reports (derived from the place documents)

```bash
python scripts/topic-render.py            # 38 slugs, two documents each -> outputs/topics/
python scripts/topic-render.py --check    # check G over what it wrote
```

Each Level-2 taxonomy slug issues `outputs/topics/{slug}/{slug}-monthly.md` and `{slug}-progress.md`, whose sections are places in alphabetical order by full name, carrying that place's own material for that subject. The design note and its reasoning are `documentation/topic-reports.md`.

**Precondition: stages 4 and 5 first, in the same run.** A topic document derived from a place document stage 4 has not yet moved is stale in a way nothing downstream can detect — it is well-formed, its links resolve, and every check passes. The ordering *is* the integrity mechanism, so run `python scripts/rebuild.py --scan` and finish stage 4 before this, rather than trusting that it was done.

**Nothing is authored here** *(Bill, 2026-08-14)*. No summary, no cross-place block, no connecting sentence. The monthly carries every `{section}--{subject}` narrative block a place holds — every one, since a subject can sit in more than one section of a place's report — and the progress report carries the subject's movement table and no prose at all, because a place's progress report keys its narrative by section only and there is no per-subject block in any of the 57 to lift. The one thing the script writes is the standing provenance line under each H1, which is identical in all 76 documents and says where the material came from.

**It is a script, not a model stage**, which is the whole point of a pure derivation: nothing here decides anything. It is idempotent on the same inputs — a second run reports all 76 `unchanged` — and it never edits a place document.

**Check** `G` — every link resolves through the catalogue — and nothing else. The ledger checks belong to the place documents, where the prose was written; there is no topic ledger and there is not meant to be one. `--check` runs G over the whole tree in one pass.

Commit the topic tree. 38 slugs × 2 documents takes the render set from 165 to 241.

## Stage 7 — the bulletin (window select; model authoring)

One document over a two-day window: `outputs/bulletins/corpus-bulletin.md`, published at `/bulletin/`. The design note is `documentation/bulletin.md`.

**The country bulletin was retired on 2026-08-21** *(Bill, `prep/bulletin.md`)*. It covered the same items as the topic bulletin and differed only in how it grouped them, so a reader who opened both read every summary twice. The place dimension is now on the item — a country box beside each headline, linking to that country's page — which is what the grouping was for, at one click rather than a second document.

```bash
python scripts/bulletin.py --scan          # the window, and which items still need a summary
```

For **each** item in the work order, read it — `raw/{year}/{slug}.md` from `scripts/.workroot/`, the `hub_line` first and the body only where the line is not enough — and write one to three sentences:

```bash
python scripts/bulletin.py --write {slug} --text "…"
```

Then assemble the document and commit `outputs/bulletins/`:

```bash
python scripts/bulletin.py --assemble
```

**`--assemble` leaves the file alone when nothing but the stamp has moved.** The page states when it was last updated, and a stamp moved on a run that changed nothing would claim the bulletin had. The comparison is the **whole file**, rebuilt with the stamp already on disk: if that reproduces what is there, only the clock moved. *(It was the body below the frontmatter until 2026-08-21, which excluded the subtitle along with the stamp — so the correction to the byline ran, reported `unchanged`, and left the wrong wording on disk.)* `render.py`'s edition gate is taken over the subtitle as well as the body for this document and no other, so a byline that has been corrected in the source reaches the served page too. *Last updated* therefore means *the ingest whose catch produced what you are reading*.

**The window is publication, not acquisition** *(Bill, 2026-08-17, asked directly and chosen over the alternative)*. An item is in the bulletin when its `published` date is today or yesterday. The corpus acquires in batches — the 2026-08-16 run ingested 184 records carrying publication dates spread across the ten days before it, eleven of them inside a two-day window — so a typical run selects a handful and some select none. **An empty window is a finished bulletin, not a failure and not a thing to widen the window over**: `--assemble` writes the document saying the window was empty and saying why, because a bulletin that is simply absent is indistinguishable from a build that did not run.

**A summary is written once and kept.** The window is two days wide and the build runs daily, so nearly every item is selected twice; `outputs/bulletins/summaries.json` is the store and `--scan` asks only for what is not in it. Entries age out 30 days after publication. So the model stage costs one day's news per run, not two.

**`--assemble` stops rather than publishing a gap.** An item in the window with no summary fails the command and names the slugs. That is the same rule as *Narrative integrity* above and it is mechanical: the repair is to write the summary, and there is no third option in which the item appears with nothing under it.

**Everything in a summary is sourced by construction, and that is the only reason the register is satisfied cheaply here.** Each entry opens with the item's title linked to the publisher's own record, so a fact in the sentences beneath it carries its citation two lines up. What that does *not* license is a fact the item does not carry: the summary reports the source, and where the source states a figure the figure is the best thing to put in the sentence. It is Corpus's prose either way — a verbatim sentence lifted from the body is both a register failure and the thing the leak gate exists to catch.

**Detail sits in one place** *(Bill, 2026-08-17)*. An item carrying five topics is summarised once and cross-referenced from each of the other four. That is the script's doing, not the drafter's: one summary is written per item and `bulletin.py` decides where it lands.

**The summary lands where the item first appears in the document** *(Bill, 2026-08-21)* — the earliest of its topics in taxonomy order, so every cross-reference points backwards to text the reader has already passed. It used to be the first topic the record listed, which was the same thing while the sections were in facet order and stopped being so when the taxonomy's order took over.

**The sections are `lookups/taxonomy.csv`'s order and its labels** *(Bill, 2026-08-21)*, Level-1 groups and the Level-2 sections inside them, with a nav bar at the head of the document listing the categories this edition reached. Nothing to do here — `taxonomy_lib` is the single vocabulary and the bar is built from the sections that exist.

**The *Last updated* stamp is OSINT's last ingest, read from the mirror** *(Bill, 2026-08-21)* — `logs/ingested_log.md`, via `scripts/osint_lib.py`, a read and nothing more. A run that writes prints which stamp it used, and `build clock (mirror unreadable)` means the page is stamped with when we ran rather than when the material moved. A run that writes nothing prints a `mirror … unreadable` line of its own, because the quiet run is the one where an unreadable mirror would otherwise go unmentioned.

**It is its own stage rather than a question asked during stage 4**, which is the opposite of the ruling under *Maintaining the status baseline* and for a reason that does not apply there. Stage 4 iterates by unit over a set difference, so an item already marked considered on an earlier run is never reopened, and an item carrying no place is in no unit's scope at all — a bulletin riding along inside it would silently drop exactly the items a two-day window is most likely to hold. Its only precondition is stage 2: it reads `outputs/catalogue/raw-catalogue.csv` and nothing the report layer writes.

## Deferred stages — not yet in this build

- **Report initialisation from the wiki** — for a place with no ledger. Reads the compiled wiki (`wiki/places/{ISO}.md`, `wiki/intersections/`) to distil a new ledger and write the first reports. `report-country-init.py` is the shell; the authoring is a session's model work. Bill's decision (2026-08-13): the current ledgers are the accepted baseline, so initialisation is not run now.
- **Monthly narratives** — some monthly issues carry empty per-subject blocks; authoring them is tracked.

## Leak gate — before any commit of outputs/

`outputs/` must carry metadata and compiled prose only, never a verbatim source body. Before **any** commit that includes `outputs/` — the compile commits above and the final one below — run the gate:

```bash
python scripts/leak-check.py outputs      # exit 0 = clean; exit 1 = a body leaked
```

If it exits non-zero, **do not commit** — a compiler is wrong; stop and fix it. A leak into public history is permanent (`documentation/design.md` §8), so this is the one check that fails the build rather than warning.

## Ending the run — message, gate, log, commit, stand down

**1. Message Bill, if anything is owed him.** Insert a block under the marker in `logs/messages-for-bill.md`: what would have been asked, what the run did instead, what his options are. A run that needed nothing writes nothing there, which is the normal outcome.

**2. Leak gate.** Nothing commits until this passes.

```bash
python scripts/leak-check.py outputs || exit 1
```

**3. Log one terse line**, in the form `YYYY-MM-DD HH:MM · build · took · what happened`.

```bash
python scripts/log-line.py build "catalogue N, finance N places, scan N units, K ledgers updated — ok"
```

**The duration writes itself** *(Bill, 2026-08-17)*, from the `--start build` stamp taken in stage 0 — the call above is unchanged and takes no extra argument. It reports the gap between that stamp and now, then clears it. Where stage 0's stamp was never taken, state it instead of leaving the field empty: `--since "2026-08-17 06:41"` or `--took 3h02m`. Do not hand-write a duration that flatters the run — the field exists to be compared across runs, and one made-up number makes the whole column unreadable.

**The log reads newest first** *(2026-08-16)*, so the line is inserted at the top, under the marker comment — `>> logs/log.md` is no longer the recipe. It would still write a correct line, in the wrong place, which is the version of this that nobody notices. `scripts/log-line.py` does the insert and takes the message as an argument, so `·`, em-dashes, slashes and backticks in it are content rather than syntax; it exits 1 rather than guessing if the marker is missing.

**4. Commit everything**, so the build ends clean with nothing outstanding.

```bash
git add -A && git diff --cached --quiet || git commit -m "Build run: outputs, log and messages"
```

**5. Stand down** — remove the stage 0 sentinel, and only now, after the commit has landed.

```bash
rm -f logs/.build-in-progress
```

**Last, because it is the assertion that a run is accounted for** *(2026-08-16)*. Removing it before the commit would open a window in which `RENDER.md` Step 0 sees a finished build whose work is still uncommitted; removing it after closes that window, and a crash in between leaves the file present, which fails safe in the only direction that matters.

**On failure, the word is `errored`** *(2026-08-16)*. Log the stage and the error in place of the completion line — `… errored at stage 3: <message>` — commit whatever is committable, remove the sentinel, and stop. A logged failure is a run that reported itself, so it stands down like any other; what the sentinel is for is the run that never got to say anything. `RENDER.md` Step 0 matches the word `errored` to tell a failed build from a finished one, so a failure line phrased around it reads downstream as a success. A failure writes a message as well only where it left something Bill has to undo; otherwise the log line is the whole report. One line per run either way — the detail is in git.

## Boundary

Nothing in Job 1 writes to OSINT. The only Corpus→OSINT channel is the gaps request-feed (a *Not held* row asking OSINT's sweeps to fetch a named document) — a file OSINT reads, never a write.
