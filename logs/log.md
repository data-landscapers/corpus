---
type: log
title: Corpus process log
---

# Corpus log

*(One line per job run. Form: `YYYY-MM-DD HH:MM · job · what happened`. BUILD (Job 1) and RENDER (Job 2) each append a line on completion or error — see their runbooks. The detail is in git; this is a skim.)*
2026-08-13 19:25 · render · 165 reports (54 status, 57 progress, 54 monthly) + home, 54 countries, catalogue 9,407, finance 1,243 deals; editions re-cut render-dated after 116 were overwritten in place; leak gate clean; deployed — ok
2026-08-14 09:04 · build · report-layer spec ported into documentation/, all wiki/report-layer.md citations repointed, check K unblocked · revert: c54d6a9
2026-08-14 09:31 · build · report-layer rules: compiled date only on change, empty sections dropped from monthly/progress, check L added · revert: 3d5aa86
2026-08-14 09:36 · build · compiled: judged against new record: digest — a file-vs-render diff missed hand-written narrative · revert: 7e76d41
2026-08-14 09:52 · build · no issue closed to new evidence: step 4 re-cuts the period a late as_at falls in; BUILD stated as author not transcriber · revert: 04870e7
2026-08-14 09:59 · build · monthly/progress filenames drop the month; same_issue() guards narrative carry-across and period read-back · revert: b7412d3
2026-08-14 10:06 · build · progress carries narrative across the roll (11/12 months shared); monthly still starts empty · revert: 3885650
2026-08-14 10:15 · build · issue model removed: living documents, sliding windows, window close masked with compiled: · revert: a20b657
2026-08-14 10:44 · build · ledger as_at->published (from slug date), prior_* dropped, period selection off the ledger · revert: eb783b7
2026-08-14 10:48 · build · status table header As at -> Milestone; CC note updated with the schema change and the unrendered state · revert: cd5ccd7
2026-08-14 10:52 · build · renderer reports prose blocks dropped when their section stops rendering (was miscounted as carried) · revert: dfab90b
2026-08-14 10:55 · build · reworded check L and narrative integrity: BUILD is the author, the check is its own tally · revert: e655deb
2026-08-14 11:07 · build · check split corrected (A-F OSINT, G-K Corpus); H and J marked not implemented; R3 no longer tells OSINT to drop A and D · revert: 1a08dac
2026-08-14 11:42 · build · window close rendered as a sentinel and substituted on write, so an unchanged document keeps its date and its window; nil month now issues a monthly that says so · revert: c6a4631
2026-08-14 11:52 · build · vault_lib refuses to rebuild an index reached through a junction — a Corpus render could have rebuilt C:\OSINT\index as a side effect of reading it · revert: b70b0cc
2026-08-14 12:06 · build · empty index/ removed and gitignored; build_index refuses to write an index of 0 artefacts and slug_urls refuses to read one — the state reported itself fresh and stripped every citation in silence · revert: HEAD
2026-08-14 12:22 · build · check M added — every row that states a position must cite a source; absolute rule stated in report-layer.md §6 and BUILD.md. 12 unsourced rows found, all ZAF, left for BUILD · revert: HEAD
2026-08-14 12:38 · render · Step 2 glob fixed for the undated monthly/progress filenames, plus a pattern-free coverage assertion — the old patterns matched nothing and would have rendered 54 of 165 silently · revert: HEAD
2026-08-14 12:55 · build · check H replaced: a figure in narrative must have a source, not a ledger row — the old rule was OSINT's retired ~90%-false-positive scan and fought §2's chronology rule; 67 blocks reported. documentation/ linked into the workroot · revert: HEAD
2026-08-14 13:14 · build · check J implemented — a document compiled before its ledger's newest source fails (34 today); the shape check is asserted; the "dated ahead" direction is reported not judged, being governed at the cause by the window-close rule · revert: HEAD
