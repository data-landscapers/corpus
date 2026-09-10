# REREAD — repairing a unit whose evidence was read and discarded

*(Opened 2026-09-10. The defect, its cause and its scale are
`documentation/considered-not-carried.md`; this is only how to repair one unit.
Written so the work survives a cleared context: everything below is on disk, and
nothing in it needs the session that found the defect.)*

**The one-line brief for a fresh session.** *Stage 4 read evidence, marked it
considered, minted nothing, and the reports then published ***No evidence*** over a
base that holds the answer. `BUILD.md` stage 4 step 2 is corrected; nine units are
reopened; repair them one at a time with the loop below.* Benin is done and is the
worked example.

## State

`python scripts/lint-considered.py` is the ground truth and prints what is left.
It returned 859 sources over 467 indicators in 22 units on 2026-09-10; the nine
worst were reopened the same day (652 slugs), Benin was repaired, and the rest of
that list is the queue.

**The 467 is a floor.** The filler manifests name the *staged* file and OSINT
renames some at ingest — 986 of 9,178 staged names, 11%, match no slug in `raw/`.
The lint matches staged name against `considered.txt`, so a renamed document is
invisible to it. **Work from `report-scan.py --slugs {ISO}`, never from the
manifest**: the scan reads the base and is authoritative about what a unit has not
considered. The manifest is a hint about which indicator a document was staged
for, nothing more.

## The rule this repair exists to apply

`BUILD.md` stage 4 step 2, as corrected on 2026-09-10:

> *"Nothing moves" is about a position the ledger already holds.* Where the ledger
> holds **no** position on the thing a source names, the source is the first record
> of a row and the outcome is **mints a row** with `movement: Baseline not held`.
> The test is the row test of `report-layer.md` §1 and nothing else: could a reader
> name the thing, and could its position be different next quarter.

**Both halves matter.** Minting everything is worse than the original defect,
because it puts positions the base cannot support into published reports. A source
that reports activity on a position already held may move a row or may do nothing,
and *nothing* is still the right answer for most sources.

## The loop, per unit

Run from `scripts/.workroot/` where the junctions resolve, except where noted.

1. **Reopen**, if the unit is not already — from the Corpus root:
   `python scripts/reopen-considered.py --unit {ISO} --apply`.
   It lifts only what `lint-considered.py` reports and leaves a
   `considered.txt.before-reopen` beside the file on the first apply.

2. **Brief**: `python scripts/reread-brief.py {ISO}` (Corpus root). One screen:
   the reopened sources grouped by the indicator they were staged for, each with
   the filler's own `baseline`/`progress` call and its `note:`; the unit's ledger
   by subject; and the subjects the ledger holds **no row at all** for. That last
   list is where the mints are — seven of Benin's forty-eight empty indicators sat
   in subjects with no row of any kind and every one was a mint.

3. **Read the bodies you need.** The `note:` is usually enough for the row
   decision. Open the body where it is not, and always where the decision is close.

4. **Decide, in three groups.** *A row already answers it* → a mapping row in
   `indicators.csv`, no new ledger row. *No row* → mint, then map **in the same
   step**. *The source does not establish this indicator* → leave it, and let step 6
   mark it. Benin ended with two indicators correctly still ***No evidence***.

5. **Write.** Ledger rows carry the full column set (`row_id`, `place`, `subject`,
   `section`, `kind`, `name`, `status`, `published`, `milestone`, `since`,
   `movement`, `position_start`, `position_end`, `sources`, `probe_at`, `note`);
   `section` is the subject's Level-1 chapter and the renderer keeps it in step.
   Indicator rows carry `indicator_id`, `progress`, `summary`, `developments`,
   `row_ids`. Every stated fact carries a citation as `[text](slug)` — check M
   refuses the rest.

   **Append with `csv.writer(lineterminator="\r\n")` over the parsed file.** The
   round-trip is byte-stable on these files, so the diff is only what was added.

6. **Mark**: `python scripts/report-scan.py --mark {ISO} <slugs>` — every slug
   read, moved or not.

7. **Rebuild and check**:
   `python scripts/report-render.py --unit {ISO} --render --doc all`, then
   `--check`, then `python scripts/report-register-check.py --unit {ISO}`.
   **A failing check is work, and it is done in the same pass** — check H means a
   figure with no source to follow, and the register's jargon hits in your own
   prose are rewritten while a hit inside quoted source text stands.

8. **Confirm**: `python scripts/lint-considered.py --unit {ISO}` must come back
   clean. Then render (`python scripts/render.py outputs/reports/{ISO}/{ISO}-progress.md`),
   rebuild the topic reports (`python scripts/topic-render.py`) and the progress
   pages (`python scripts/progress.py`), and commit.

## The two mistakes already made, so they are not made again

**Mint and map are one step.** A row minted and left unmapped leaves the indicator
publishing ***No evidence*** over the row that answers it — the exact defect being
repaired. It happened once on Benin, on the banking statute, and only the final
count caught it.

**`render.py` is not `report-render.py`.** The first turns a markdown document into
HTML and PDF; the second rebuilds the markdown from the ledger and the indicator
frame. A vocabulary or data change needs the second, then the first. An hour was
lost to rendering the old tables faithfully.

## The queue

Repaired: **BEN** (50 ***No evidence*** → 2), **COG** (60 → 2),
**CPV** (57 → 8), **BFA** (51 → 4), **GIN** (46 → 4), **CMR** (40 → 7),
**COD** (42 → 3), **GAB** (47 → 5), **ERI** (61 → 0).

Reopened and waiting: none — the reopened queue is clear.

Not yet reopened, 13 units, 103 sources over 75 indicators — the tail
`lint-considered.py` still reports.

## Two smaller losses, measured only for Benin

- **25 of the 174 documents staged for Benin are not in `raw/` at all** — staged,
  never ingested. Upstream of everything here.
- **28 are in `raw/` and in no unit's considered list**, while `report-scan`
  reports nothing unconsidered — so the unit's scope does not see them. Most likely
  their `places:` does not carry the ISO-3.

Neither has been counted estate-wide.
