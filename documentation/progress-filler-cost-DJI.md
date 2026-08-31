# Progress filler — throughput record, DJI, 2026-08-31

*(Run against Djibouti — no prior DJI run, so §0's skip found nothing to carry forward, and
all 78 gap indicators were live. Batch label `progress-filler-DJI-2026-08-31`. Run CSV:
`logs/progress-filler/DJI-2026-08-31.csv`, with the selected and unselected registers beside
it.)*

## The headline

**78 of 78 gaps had two briefs run, all 78 staged, zero nils.** The widest gap list this series
has run — Djibouti held only 43 of 121 frame indicators before this run — and the first fully
complete pass since GHA: every single indicator staged at least a baseline, several with a
documented absence rather than an empty search (`digital.rural--digitalisation-of-rural-police-stations`
stages a baseline that is itself the negative finding — a World Bank IEG review confirming the
e-ID subcomponent was dropped and no rural-station evidence exists — rather than a blank).

## Stage 1 — the sweep (complete)

| | |
|---|---|
| Gaps worked | 78 of 78 (no skips — no prior DJI run) |
| `agent_run` calls | 156 — 2 per gap across eight parallel batches |
| Candidates returned | 462 |
| Fetched | 182 |
| Dropped (pre-fetch, scope/dedup) | 46 — mostly `already-seen` (candidate already in `raw/` under another topic), plus `fetch-blocked`, `inadmissible-origin`, `duplicate-in-run`, `out-of-window` |
| Cap-excluded (fetched and read, not staged) | 8, recorded with URLs in the unselected register — plus a further set of "ranked but never fetched" leads the register also carries, each flagged `Not fetched` in `why_not` and excluded from this count |
| **Staged after the cap** | **201 selections — 75 baseline + 126 progress**, over **136 distinct files** after merge (175 staged by the eight batches before cross-batch dedup), filed as 59 in `DJI/baseline/` and 77 in `DJI/progress/` |
| Nil | 0 |
| Sessions | one (eight parallel sub-agents plus one relaunch, one parent merge) |

## Slicing and cross-batch dedup

**Eight batches, grouped by Level-1 topic and sized 8–11 gaps each** per §6: Governance split
three ways (policy/finance/discourse, legislation/regional, standards+ICT-infrastructure — 10,
9, 10), DPI split three ways (exchange/identity, payments/registries, sectoral-MIS+
digitalisation — 9, 11, 11), Technology+Capacity+Data-statistics (8), and Inclusion+Data-
satellite+Geopolitics (10).

**One batch (A, Governance policy) crashed mid-run** on a spurious model content-classifier API
error (`[bio]`) unrelated to anything in the task — government ICT strategy, broadband policy,
MoUs. All 10 of its baselines had already been staged before the crash and survived on disk;
it was relaunched fresh with a directive to run only the remaining progress briefs, picking up
cleanly without re-fetching any baseline. Flagged separately as model-behaviour feedback.

**The heaviest cross-batch duplication load this series has recorded: 39 duplicate-URL files
removed across 24 groups**, against COM's 20/16 the run before. One document — the Mobile ID
national-launch article — was independently found and staged under **seven** different
filenames by seven of the eight concurrent batches (every batch whose indicators touched
identity, registries, local government or standards cited it), and a ministerial-attributions
decree under five. Both merged correctly onto one survivor file with a union of all the
topics/indicators they served, matching §6's "count selections, not files."

**A merge-script bug cost one document's content**, discovered and fixed within the same
session: three duplicate captures of a World Bank ISR (Digital Foundations project, P174461)
were deleted before the topics-merge step completed on that group, leaving no surviving file.
Recovered by the parent session re-fetching the same URL directly and reconstructing the
frontmatter/body from the batches' own prior descriptions of its content — the only loss in
the run, and fully recovered before the batch was staged.

`scripts/lint-staged-queue.py` reported one finding after the full merge — a `SUSPECT`
crossed-body flag on a Chinese-language capture (the MAZU-Urban early-warning system article) —
confirmed a false positive on direct read: the body's own opening heading is character-for-
character identical to the title, and the publisher is correctly named in the frontmatter; the
linter's title-token overlap check has no CJK tokenizer and can't score it correctly.

**A counting-rule fix, carried over from the COM run, mostly worked.** Sub-agents were briefed
explicitly to count `not_selected` only for candidates actually fetched and read, never
candidates judged inferior from the Exa Agent's summary text alone. Most batches self-audited
correctly this time; two small residual corrections were still needed at merge (a transcription
slip on the resumed batch A's brief numbering, and one ambiguously-worded row). The final
`not_selected` total (8) is now fully reconciled against the unselected register.

## Cap audit

Zero violations over 78 rows: every indicator staged at most one baseline and at most two
progress items. 201 selections landed on 136 files — the largest gap between selections and
files this series has produced, reflecting how densely a well-documented, infrastructure-heavy
country like Djibouti (submarine cables, regional payment systems, a national Digital Code)
generates single documents that answer several indicators at once.

## What this run consumed

Eight parallel sub-agents (one relaunched) in one sitting, 156 `agent_run` calls at
`effort: medium`, roughly 462 candidate leads triaged down to 182 fetches and 201 staged
selections. This is the sweep stage only — stage 2 (post-ingest reading), stage 3 (mapping) and
stage 4 (render) are separate sessions on the far side of an OSINT ingest and a mirror refresh,
and are recorded here once they happen. The batch sits in `new-queue\DJI\` undelivered until
Bill hand-carries it (§0/§5); nothing here has touched `raw/`.
