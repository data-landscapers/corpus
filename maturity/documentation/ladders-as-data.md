---
type: decision
reader: cc
title: ladders-as-data.md — should a ladder be data read by one script? (R172)
date: 2026-11-26
status: decided by CC; the move rides each study's next rebuild
---

# Should a ladder be data read by one script?

**Yes, and half of them already are.** Of the 156 `scripts/study-*` files on 26 November 2026, 114 are ladders. 56 of those are shims of a single call that hand a study id to one of the shared counters (`study_figure.py`, `study_first_ladder.py`, `study_afford.py`), which read the study's questions and aspects from its `study.json`: for them the ladder is already data, and the file is only a name. The other 58 are bespoke rule functions of 45 to 160 lines, such as `study-ladder-police.py`, whose conditions (a share over 90 per cent, dated within two years, both records named) live in code that a reviewer of the study cannot see in `study.json`. The remaining 42 are writers, carriers and shared tools. **Decision:** one entry point, `study-ladder.py {id}`, dispatching on a `counter` field added to `study.json`, replaces the shims (housekeeping job 90, done 2026-11-28: 52 shims removed, 48 `first` and 4 `figure`, the other 62 studies `own`); each bespoke ladder moves into a shared counter at its next whole rebuild (R185 already rewrites the sixteen under 70 % agreement), and stays code only where a rule needs arithmetic the question-and-aspect form cannot hold, saying so in `study.json`. The writers are R162's to retire: `test_maturity_words.py` fails 27 cases on R130's old words, most of them in writers (housekeeping job 89).
