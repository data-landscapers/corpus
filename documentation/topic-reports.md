# Topic reports — decision note and drafted BUILD.md stage (2026-08-14)

*(Written from Cowork, for a Claude Code session. Nothing in `BUILD.md`, `RENDER.md` or `scripts/` has been touched — this file holds the drafted text for CC to review operationally before either runbook is edited.)*

## What Bill decided

1. **Topic reports are BUILD's.** The rule is not scripted-vs-authored, it is `outputs/` vs `site/`: everything in `outputs/` comes from BUILD, and whether a stage happens to run a script is an implementation detail, not an architectural boundary. RENDER typesets what it finds and judges nothing.
2. **A topic report has no ledger.** It is a derived view of documents BUILD has already authored, not a rendering of a record layer of its own.
3. **Two documents per Level-2 slug** — `{slug}-monthly` and `{slug}-progress`. No status report.
4. **The country and region build runs first**, in the same run.
5. **Topic documents do not live under `outputs/reports/`.** They go in their own tree, and `outputs/reports/` is renamed to match — see the open point below on what that name should be.

## Why no ledger is the right call, and what it turns on

The topic report inherits its evidence layer. Every sentence it carries was authored by BUILD against the Corpus register, cited on the sentence carrying the fact, and passed checks G, H and M inside a country document before it was lifted. A ledger here would be a second record of positions already recorded once, and a second record is a second thing to keep in step.

**This is what makes "country build first" a correctness condition rather than a convenience.** A topic document derived from a country document that stage 4 has not yet moved is stale in a way nothing downstream can detect: it is well-formed, it cites live sources, and every check passes. The ordering *is* the integrity mechanism, so the stage states it as a precondition and refuses to run when a unit is behind its own ledger.

Consequently the ledger checks do not apply and must not be faked. **J** (no document compiled before the ledger moved) and **L** (no unwritten narrative block) are properties of the source documents, already enforced where the prose was written. **M** (every row stating a position cites a source that resolves) is likewise inherited. **G** (every link is held in `index/`) still applies and is cheap, because a lift can only carry links that already resolved. The register check has nothing to read, since no prose is authored here at all.

## The unit and the documents

**Unit: one Level-2 taxonomy slug.** `outputs/vocab/taxonomy.md` currently carries **38** of them across ten Level-1 categories — its own header says "~36", which is stale in the other direction. All 38 appear in ledgers and all 38 carry at least one narrative block in at least one monthly, so no slug is empty. *(Counted 2026-08-14; this note said 39.)* Level-1 roll-ups are not built now; the taxonomy is a strict single-parent tree, so a Level-1 report is a later composition of the same material and costs nothing to defer.

**Two documents, not three.** The layer already allows this — a region issues the progress report only (`documentation/report-layer.md` §1), and `report-render.py` refuses the other two for an `X__` unit rather than making every caller branch. The status report is the odd one out here for a reason: it answers *where is this now* for a single place, and the cross-place equivalent is a site surface — the Topics page ranging over 54 places — not a document. Building it as a document would be a third thing to keep current for no reader who is not better served by the page.

**Filenames use the hyphenated slug**: `outputs/topics/dpi-pay/dpi-pay-monthly.md`, with `subject: dpi.pay` in the front matter. The dot survives in the vocabulary, where it means something, and does not go into a path, where it reads as an extension. The narrative block keys already do exactly this substitution.

**Sections are places, in alphabetical order by published full name** — not by ISO3. The two orders are not the same and the difference is visible: Eswatini sorts under E and `SWZ` under S, Cape Verde under C and `CPV` under C but Côte d'Ivoire's `CIV` before it. A reader scanning a topic report is scanning country names, so the names are what it sorts on.

**The three regions appear in the progress report only**, because they issue no monthly. Nothing else about them differs.

## It is a lift, with nothing added

Everything under a place heading is carried verbatim from that place's document: for the monthly, the `<!-- narrative: {section}--{subject} -->` block; for the progress report, **the subject's movement table, and nothing else**. A place with nothing to carry for that subject gets no heading, under the same rule that stops the renderer printing an empty section.

**The topic progress report carries no prose at all** *(Bill, 2026-08-14)*. Not by the same argument as the monthly's — there is simply nothing to lift. A country progress report keys its narrative by **section**, not by section-and-subject: `<!-- narrative: infrastructure -->` is one block written across cyber-security, satellite broadband and data centres together, and there is no `infrastructure--infra-connect` block in any of the 57 progress documents to take. Lifting the section block would carry four other subjects' prose into a single-subject document, which is the opposite of what the lift is for. So the topic progress report is movement tables under place headings, and the table is already the substance of that document. *(Found by CC, 2026-08-14: this note originally said "the movement table and its block".)*

**Nothing is authored here — no summary, no cross-place block, no connecting sentence** *(Bill, 2026-08-14)*. A proposal for an authored summary at the top was put and refused. The document is the country prose, sliced by subject and ordered by place, and that is the whole of it.

The consequence worth keeping in view: **no prose in a topic report is written for a topic reader.** Every sentence in it was drafted to sit inside a country document, where the country is given by the page and the subject by the heading. Read in a topic report the country is given by the heading instead, which mostly works, and where it does not the fix is upstream — a sentence that only parses in its home document is a sentence the country report should not have been carrying either.

## Open point — what `outputs/reports/` is renamed to

Bill's instruction: if topics get their own tree, the existing tree is renamed for symmetry, and he is happy with `outputs/countries/`.

**`countries/` would be inaccurate, because three of the 57 units are regions** — `XAF`, `XSA`, `XWA`, which the layer treats as first-class places, not as countries. The system's own word for *country or region* is **place**: it is the facet name, it is the `place` column in every ledger, and `countries.csv` is the vocabulary that carries both.

So the symmetric pair is either the facet names — **`outputs/places/` and `outputs/subjects/`** — or the site's section names, *countries* and *topics*, which is the pair that misdescribes the regions. `outputs/` is the record layer and is named in the record layer's vocabulary; what the site calls these sections in its navigation is a presentation choice and stays RENDER's. Recommendation: **`outputs/places/` and `outputs/subjects/`**, with the site continuing to say Countries, Regions and Topics.

**The rename does not block the topic stage and should not be folded into it.** Topic documents can be written to their new tree on day one; moving 57 directories is a separate mechanical commit touching `report-render.py`, `report-scan.py`, `rebuild.py`, `country.py`, `render.py`, both runbooks, `documentation/report-layer.md` and the `compiled from` line the renderer writes into every document. Two commits, reviewed separately.

**What forced the question**, for the record: `rebuild.py --reports all` globs every directory under `outputs/reports/` and hands each to `report-render.py`, which opens `{unit}/ledger.csv`. A ledger-less topic directory sitting in that tree breaks an invariant three scripts assume. `country.py` is safe — it filters on `FULL_NAMES`.

---

# Drafted text — `BUILD.md`

Add as **Stage 6**, after the stage 5 re-render, and delete **Topics** from *Deferred stages*.

## Stage 6 — topic reports (derived from the unit documents)

Each Level-2 taxonomy slug issues two documents — `outputs/topics/{slug}/{slug}-monthly.md` and `{slug}-progress.md` — whose sections are places, in alphabetical order by full name, carrying that place's prose for that subject.

**There is no topic ledger, and there is not meant to be one.** A topic document is a derived view of documents BUILD has already authored: every fact in it was cited on its own sentence and checked inside a unit document before it was lifted. The evidence layer is inherited, which is why this stage adds no sourcing decisions and no new ledger to keep in step.

**Precondition: every unit is current.** Stage 4 must have completed for every unit holding unconsidered sources, and no unit may report a document behind its own ledger. A topic document derived from a stale unit document is itself stale and nothing downstream can see it — it is well-formed, its links resolve, and every check passes. The ordering is the integrity mechanism, so it is checked rather than assumed:

```bash
python scripts/rebuild.py --scan          # must report no unit with unconsidered sources
```

If it does not, finish stage 4 first. This stage never initialises and never moves a ledger row.

**Build each slug:**

1. **Collect.** For each place in `outputs/reports/`, take every block keyed `{section}--{subject}` from `{ISO3}-monthly.md`, and for the progress report the subject's movement table from `{ISO3}-progress.md`. **The section is read off the ledger row, never derived from the subject** *(corrected 2026-08-14)*: `ledger.csv` carries a per-row `section`, `report-render.py` checks only that its value is a known section, and 170 rows across BEN, ETH, GNB, NGA and ZAF sit somewhere other than the section map's default — BEN's `gov.regional` in four different sections at once. **A place can therefore hold more than one block for one subject.** Take them all and print them in document order under the single place heading; a subject scattered across a place's sections is still that place's account of the subject.
2. **Carry it verbatim.** The prose and its citations move together and are not re-edited here. A place with nothing for the subject — no block in its monthly, no rows in its movement table — gets no heading, the same rule that stops the renderer printing an empty section, and for the same reason.
3. **Regions appear in the progress report only.** The three `X__` units issue no monthly, so the topic monthly has no section for them.
4. **Write nothing.** There is no summary block and no connecting prose *(Bill, 2026-08-14)*. A topic monthly is its lifted blocks and a topic progress report its lifted tables, so *Narrative integrity* above has no work to do here: what prose there is was written, and checked, in the documents it came from. A topic document with nothing to carry at all is not issued.
5. **Front matter** carries `subject`, `compiled`, `period`, `places` and `record`, on the same discipline as the unit documents: `record` is a digest of the content, `compiled` is the date that content last changed, and a build that changes nothing leaves the file untouched and prints `unchanged`.

**The period is the source documents' period, not a window of this stage's own.** Nothing is aged here: a block is in the topic monthly exactly when it is in the place's monthly. Where the unit documents do not share a single period, the topic document states the range they span rather than asserting one they do not have.

**Check** `G` — every link held in `index/` — and nothing else. The register check has no authored prose to read here, and running it over lifted blocks would only re-report the source documents. The ledger checks (`J`, `L`, `M`) are properties of the source documents and are enforced where the prose was written; they do not apply here and are not to be re-implemented against a ledger this unit does not have.

Commit the topic tree. 38 slugs × 2 documents adds 76 documents to the render set, taking it from 165 to 241.

---

# Drafted text — `RENDER.md`

**Replace** the section *Not in this runbook — Topics* with the following, and extend Step 2 as shown.

## Topics

Topic documents are authored by BUILD (`BUILD.md` stage 6) and arrive in `outputs/topics/{slug}/`, two per Level-2 taxonomy slug. They render exactly like the unit reports and RENDER judges them no more than it judges anything else.

Step 2's loop and its coverage assertion must reach them. Both trees, one assertion:

```bash
rendered=0; failed=0
for md in upstream/reports/*/*-status.md upstream/reports/*/*-progress.md upstream/reports/*/*-monthly.md \
          upstream/topics/*/*-progress.md upstream/topics/*/*-monthly.md; do
  [ -e "$md" ] || continue
  if python scripts/render.py "$md"; then rendered=$((rendered+1)); else echo "RENDER FAIL: $md"; failed=$((failed+1)); fi
done

present=$(find upstream/reports upstream/topics -name '*.md' | wc -l)
echo "rendered $rendered of $present report documents ($failed failed)"
if [ "$rendered" -ne "$present" ]; then
  echo "RENDER ABORT: $((present - rendered)) document(s) did not render — do not deploy"
  [ "$failed" -gt 0 ] && echo "  $failed failed in render.py (see RENDER FAIL above)"
  echo "  and any listed below matched no pattern in the loop:"
  find upstream/reports upstream/topics -name '*.md' | grep -Ev -- '-(status|progress|monthly)\.md$'
fi
```

*(The abort message says "did not render" rather than "matched no pattern": a render failure and an unmatched filename both leave `rendered` short, and the old wording named only one of the two causes while printing a list that cannot show the other. Same defect in `RENDER.md` Step 2 as it stands today — fix both when this lands.)*

Step 1's mirror already carries the new tree, since it mirrors `outputs/` whole.

The home page's Topics boxes can link to the rendered documents once this runs; until then they keep their coming-soon state.

---

# Checked by CC (2026-08-14)

All four, against the code and today's `outputs/`. The full record, including two findings this note did not ask for, is `documentation/reviews/2026-08-14-cc-review-of-topics-and-index.md`.

1. **Does `render.py` care where its input sits? Yes, and its filename grammar mattered more.** `parse_name()` was `stem.split("-")` returning `parts[0], parts[1]`, which is fine while every unit is an ISO3 code and wrong the moment a unit is hyphenated: `dpi-pay-monthly.md` parsed as unit `dpi`, kind `pay`, and `dpi-pay-progress.md` parsed as *the same pair*, so both documents wrote `dpi-pay.html` and the second replaced the first. All 38 slugs are hyphenated. **Fixed** — it now splits from the right on a known kind, and a new `tree_of()` takes the output tree from the source path, so `outputs/topics/…` renders to `site/topics/…` with a permalink that agrees. Unit reports are byte-for-byte unaffected.
2. **Do all unit monthlies share one period? Today yes, but keep the clause.** All 54 monthlies read `2026-07-01 to 2026-08-14` and all 57 progress reports `2025-08-01 to 2026-08-14`. The period is a render-time window and `rebuild.py --reports` takes a unit list, so any partial re-render leaves units on different windows until the next full pass. The clause is live, not a hedge.
3. **Is the block key derivable from the subject alone? No — overrides are in use.** 170 rows across BEN, ETH, GNB, NGA and ZAF sit in a section other than the map's default, and 39 (unit, subject) pairs span more than one section. Step 1 above is corrected accordingly.
4. **Should the tree rename go first? Deferred, and it no longer has to** *(Bill, 2026-08-14)*. `render.py` derives the tree from the source path rather than a constant, so the topic stage can be written against `outputs/topics/` now and the rename made whenever it suits, without rework.

**One thing this note could not have known and the stage now turns on:** the country progress report has no per-subject narrative block, only a per-section one, so the topic progress report carries movement tables and no prose (Bill's ruling, recorded above under *It is a lift, with nothing added*).
