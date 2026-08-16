# BUILD changes for CC to review (2026-08-14)

*(Written from Cowork, for a Claude Code session. Bill's process: Cowork designs, CC reviews operationally, then CC modifies RENDER. **Nothing outside BUILD was touched** — `RENDER.md`, `render.py`, `home.py`, `country.py`, `finance.py` and `site/` are untouched. Commits `c54d6a9..HEAD`, 22 of them including logs.*

*Rewritten at the end of the session to describe the settled state. The commit history contains two designs Bill overruled mid-session — narrative blanking at a period boundary, and an "issue" model with dated filenames — and neither is in the code now. Read this rather than the commit sequence.)*

## What Bill decided

1. **`compiled:` changes only when the record changes.**
2. **Empty sections and sub-sections are not printed**, except in the status report. *(The status report is due a major overhaul.)*
3. **An unwritten narrative block is not acceptable in any form** — neither `_(narrative not yet written)_` nor an empty block.
4. **There are no issues.** Each unit has *one* status report, *one* monthly, *one* progress report — living documents whose windows slide. No dated editions, so no period in any markdown filename.
5. **A report is a curated selection of `raw/` records, period-selected by publication date.** The ledger's `as_at` becomes `published`; at turnover, records published outside the new scope drop out.
6. **`prior_status` / `prior_as_at` go.**
7. **BUILD is the author and is responsible for the output.** Not a process to be guarded — where a document can be better, BUILD makes it better, whether or not the scan nominated the unit.

Reasoning is in `documentation/report-layer.md`; the procedure is `BUILD.md` stage 4.

## Interface: `compiled:` and a new `record:` field

`record:` is a 12-character SHA-1 of the document's **content** — with `compiled:`, `record:` itself, and the window's **closing** date all taken out. `compiled:` is the date that content last changed. A build that changes nothing does not open the file, so the mtime does not move either.

Three things about it worth your eye:

- **Why a digest and not a file comparison.** Comparing the fresh render against the file on disk misses a narrative edit entirely, because `blocker()` carries prose across *from the file being compared* — a drafter who writes into a block and rebuilds produces output byte-identical to what is already there. The date would stand still through the change that matters most. **This is the failure your comment at `render.py:350` records**: 116 dated PDFs overwritten in place on 2026-08-13 because bodies moved while `compiled:` did not. I shipped the file-comparison version first and caught it in test; that comment is why I went looking.
- **Why the window's close is masked too.** The windows run to today, so `period:`'s closing date would otherwise change on every build and drag `compiled:` with it — the daily churn rule 1 exists to prevent. Masked, the two always agree and both mean *the day this document last changed*. The window's **opening** date is not masked: a window that has slid onto a new month is a genuinely different document.
- **Migration is non-destructive.** A document written before the field existed canonicalises identically to one written after, so the first build adds `record:` and **keeps** the `compiled:` date already on the file. Nothing is back- or forward-dated.

Whether this lets you take the PDF edition from the document rather than the render date is your call. I have not touched `render.py` or reasoned about editions.

## What CC needs to change in RENDER

- **`RENDER.md` Step 2's glob is dead.** `upstream/reports/*/*-progress-*.md` and `*-monthly-*.md` match nothing. It is `*-progress.md` and `*-monthly.md` now.
- **`render.py`'s `parse_name()` is fine** — it takes `parts[0]` and `parts[1]`, so `AGO-monthly.md` gives `("AGO", "monthly")` exactly as the dated name did. No change needed.
- **`classify_table()`'s docstring is now wrong, though its code is not.** It says the ledger header is `System or instrument | Status | As at`; that third column is now `Milestone`. The code keys on `headers[1].startswith("status")`, which I checked before renaming, so nothing breaks.
- **The section set per document is variable.** Empty sections are no longer printed, so a unit's `##` headings differ between builds. Anything building navigation from them will see fewer, and different ones.
- **`upstream/reports/` is stale** — old column names, old dated filenames — until Step 1's copy from `outputs/` runs.

## The ledger schema

16 columns, not 18. All 57 ledgers migrated in `eb783b7`.

- **`published`** replaces `as_at`: the publication date of the most recent record the row cites, read off the slug prefix, since `raw/` names sources by publication date. Bill confirmed the prefix and the record's `published:` field are the same date; where they differ it is only precision (`published: 2015` against a slug padded to `2015-01-01`), and the slug carries the padded form the windows need. So no index lookup is required.
- **`as_at` was a hand-written event date**, empty on 744 of 5,421 rows — every one of which fell out of every window however recently it had been reported. ZAF's monthly was selecting 30 rows where it should have selected 58. Nothing selected under the old rule is lost; `published` is a strict superset on every unit tested.
- **`prior_status` / `prior_as_at` dropped.** No script had ever read them; filled on 9% of rows, consumed by nothing.
- **The status table's third column is headed `Milestone`.** It always printed the milestone; "As at" mislabelled it and, after the rename, named a field that no longer exists. **No fallback to a date** — printing `published` there would put "a source reported it on the 22nd" where "gazetted on the 15th" belongs. 787 rows print an em-dash.

**`position_start` / `position_end` are unresolved**, routed to OSINT as `logs/notes-for-osint.md` note 11. Establishing an earlier position is a wiki traverse INGEST already does and it happens once per row; Bill is not confident the field is currently accurate (75% filled, and a quarter of all rows publish as ***Baseline not held*** in consequence). Nothing in Corpus blocks on it.

## Two behavioural changes to expect on the first build

**A build now names the prose it discards.** Empty sections are not printed, so a rebuild can legitimately drop a section that had writing under it. It used to report this as `N narrative block(s) carried across` — counting blocks *found* rather than blocks *kept*, so a build that threw a paragraph away claimed to have preserved it. It now prints:

```
!! BEN: 7 narrative block(s) with prose DROPPED — their section no longer renders: dpi--dpi-pay, ...
```

Simulating the monthly rebuild over the current ledgers, **expect about 54 such blocks across 29 units** — BEN 7, ERI 4, GNB 4, MUS 3. It does not fail; dropping is often correct and git holds the prose. It simply cannot happen unseen.

**The renderer never clears a placeholder.** It carries block bodies across verbatim, because deleting an author's content is not a script's decision. The 188 existing `_(narrative not yet written)_` blocks therefore survive a rebuild and are cleared by drafting, or by their section going. `--check`'s new **check L** counts them — 38 of 57 units — as BUILD's own tally of the work in front of it, not as a gate. That backlog is BUILD's authoring work and is expected to be drained by doing the job.

## What I could not verify

The Cowork sandbox cannot resolve `scripts/.workroot/`'s Windows junctions, so **I could not run a single render or `--check` end to end**. Everything above was verified by unit-testing `write()`, `blocker()`, the digest and the selection directly, and by reading `outputs/` and OSINT's `index/`.

**Run a real `--render --doc all` and `--check` over one country unit and one `X__` region unit first** — particularly the region, since `render_progress()` is where the section loop changed and a region issues only that document.

Nothing in `outputs/` has been rebuilt yet, which is simply the state before BUILD runs. One visible symptom, logged as `notes-for-osint.md` note 6: KEN's `ledger.csv` holds 172 rows and 6 *Not held*, its status document says 147 and 4, its progress document 169 and 6 — three counts of one ledger, because the documents predate the ledger. A rebuild should clear it, so **note 6 is probably self-clearing** and worth re-checking before anyone actions it in OSINT.

> **The note number above no longer resolves, 2026-08-16.** `notes-for-osint.md` was renumbered from 1 in the 2026-08-13 rewrite, and note 6 in the current file is the UNITEL outage duration, not this KEN row-count discrepancy — which has since cleared on its own, exactly as this paragraph predicted, and carries no number now. The sentence is left as written because it records what was true when it was written; this addendum exists so nobody follows the number and reads the wrong note. *(The renumbering is why `notes-for-osint.md` now keeps a stub at a number whose note has moved, rather than closing the gap.)*

## Also in these commits

The report-layer spec is now Corpus-owned — `documentation/report-layer.md`, plus `report-country-skeleton.md` and `report-region-skeleton.md`, ported from OSINT and adapted. Every `wiki/report-layer.md` citation in `scripts/` and `documentation/` was repointed. Two findings from that:

- **`report-register-check.py` was crashing, not passing.** `SKELETONS` pointed at `ROOT/wiki/report-country-skeleton.md`, which has never existed in Corpus, so BUILD stage 4 step 5's register check died with `FileNotFoundError` on every run. Fixed by the port; ZAF now checks clean.
- **`documentation/archived/osint-migration.md` R7 was wrong on its own premise.** It retired the three spec files from OSINT on the grounds that "CORPUS holds working copies in its `scripts/`" — true of the `.py` files, false of the `.md` ones, which Corpus did not hold at all. Had R7 run as written, stage 4 would have lost its spec and check K its budget. R7 now says what is true.

## Questions for CC

Five things I found and deliberately did not act on, either because they are RENDER's or because guessing would have been worse than asking. Roughly in order of how much they matter.

**1. Checks H and J do not exist, and the spec claimed they bind.** *(This started as a question about `report-lint.py` and Bill's ruling of 2026-08-13 answered it: "REPORT-LINT splits along a seam already inside it — checks A–F stay in OSINT next to what they verify; G–K travel to Corpus." So `report-lint.py`, which implements A–E, has no place in Corpus at all and should be retired here rather than trimmed. Nothing invokes it anyway — not BUILD.md, RENDER.md, `rebuild.py` or `mirror.bat`.)*

The real finding is what Corpus does **not** run. Of the five checks that travelled:

| | | |
|---|---|---|
| G | every link held in `index/` | `report-render.py --check` |
| H | prose agrees with the ledger | **not implemented** |
| I | vocabulary closed | `report-render.py --check` |
| J | as-of honesty | **not implemented** |
| K | register and word budget | `report-register-check.py` |
| L | no unwritten narrative | `report-render.py --check` *(new)* |

**H is the one that matters.** It catches a figure written by hand into narrative that the ledger does not carry — and the Corpus register explicitly permits a connecting sentence where OSINT's §10 did not. `migration-report-layer.md` says it plainly: a position, however light, *raises* the cost of an unchecked figure. H is the check that pays that cost, and it has never existed here. Its rule is fully specified in `report-layer.md` §6, including the only two exemptions, so it is implementable as written.

**J** is smaller — no document dated ahead of its newest source, no period comparison without the shape check recorded — and both halves are now cheap, since `published` on the ledger gives the newest source date directly.

I have marked both ***Not implemented*** in `report-layer.md` §6 rather than leave the spec claiming verification the layer does not perform. Building them is a judgement about BUILD's priorities against the 188-block drafting backlog, which is why I have not just written them.

**Two documents had the split wrong**, both now corrected: `documentation/archived/osint-migration.md` R3 told OSINT to **drop checks A and D**, which under the ruling it should keep — that one would have cost OSINT verification it needs — and `report-layer.md` §6 claimed A and D for Corpus. `documentation/migration-report-layer.md` still carries the older wording in two places; it is a proposal marked *agreed* and I have not rewritten it, so read R3 and the spec as authoritative over it.

**2. `report-scan.py --month-due` is issue vocabulary in a model with no issues.** It asks "is a closed month owed an issue?" against a repo-level `last-monthly.txt` marker, and gates a monthly rotation. With one living monthly per unit whose window slides, I could not work out what the gate should now mean — whether it still has a job, or whether the window sliding is the whole of it. Left untouched on purpose.

**3. Does the PDF edition now come from the document?** `record:` gives you a content identity and `compiled:` a trustworthy change date, which is what was missing on 2026-08-13 when 116 dated PDFs were overwritten in place. Whether that changes how `render.py` names an edition is entirely yours — I raise it only because the field was added partly with that failure in mind.

**4. `pull.py` and `test_pull.py` are still in `scripts/`.** `RENDER.md` §14 says the build no longer starts with `pull.py`, and §46 lists retiring it as the durable repoint. `test_pull.py` still carries ledger fixtures in the pre-2026-08-14 shape (`system,status,note`), so it will read as stale to anyone who opens it. Not urgent; worth knowing they are there.

**5. Was `documentation/archived/2026-08-13-cowork-review-of-cc.md` §27.2 ever true?** My own review of your 08-13 work said "RENDER skips them, so nothing bad publishes" about the unwritten-narrative blocks. The skip had already been removed that same day. I have added a dated addendum rather than editing the review, but if I misread the sequence, correct it there.

## Still open, and Bill's

- **The status report overhaul** he has signalled. It is the only document that still prints empty sections, deliberately, and that decision may not survive the overhaul.
- **The 188-block authoring backlog**, which is BUILD's work to drain rather than a defect to fix.
