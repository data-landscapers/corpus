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
