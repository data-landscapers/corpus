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
