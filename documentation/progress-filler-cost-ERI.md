# Progress filler — throughput record, ERI, 2026-08-31

*(Run against Eritrea — no prior ERI run, so §0's skip found nothing to carry forward, and all
108 gap indicators were live. Batch label `progress-filler-ERI-2026-08-31`. Run CSV:
`logs/progress-filler/ERI-2026-08-31.csv`, selected register beside it. **No unselected
register was compiled for this run** — see *Unselected register* below.)*

## The headline

**108 of 108 gaps had two briefs run, 90 staged, 18 nils.** The widest gap list this series has
run by a wide margin — Eritrea held only 13 of 121 frame indicators before this run, the
thinnest base of any country worked so far, run against one of the world's most closed
information environments. **Nine of the eighteen nils are the entire Governance *Strategies,
plans and policies* chapter plus `finance.budget`**: two independent briefs per indicator,
across the batch that worked this chapter, turned up nothing citable for a national
digital-transformation strategy, ICT strategy, broadband strategy, cloud strategy, AI strategy,
data-governance policy, open-data policy, data-localisation policy, or comparable domestic
digital-transformation financing instrument. That is a real, dated finding about Eritrea, not a
search failure — every gap indicator's own frame subject was searched twice, on two different
briefs, and every candidate that surfaced was either off-topic, unpublished, or superseded. The
remaining nine nils are scattered across DPI/registry/tech.ai indicators, each independently
reasoned in its batch's own report.

## Stage 1 — the sweep (complete)

| | |
|---|---|
| Gaps worked | 108 of 108 (no skips — no prior ERI run) |
| `agent_run` calls | 216 — 2 per gap across ten parallel batches |
| Candidates returned | 767 |
| Fetched | 170 |
| Dropped (pre-fetch, scope/dedup) | 430 — mostly `already-seen`, `no-development` and `off-topic`; a materially higher drop rate than prior runs, consistent with a thin, repeatedly-recycled source base |
| Cap-excluded (fetched and read, not staged) | 39 |
| **Staged after the cap** | **179 selections — 87 baseline + 92 progress**, over **127 distinct files** after merge |
| Nil | 18 (`gov.policy--digital-transformation-strategy`, `--ict-strategy`, `--broadband-strategy`, `--data-storage-cloud-strategy`, `--data-interoperability-framework-roadmap`, `--ai-strategy`, `--data-localisation-policies`, `--data-governance-policy`, `--open-data-policy`, `finance.budget--sustainable-domestic-financing-of-digital-transformation`, `gov.legislate--ai-legislation-regulations`, `infra.capacity--local-capacity-to-maintain-manage-and-develop-government-systems`, `dpi.exchange--interoperability-of-health-systems`, `dpi.exchange--interoperability-of-social-protection-systems`, `dpi.govtech--e-government-services`, `dpi.registry--address-register`, `dpi.registry--land-register`, `tech.ai--use-of-ai-in-government-administration`, `tech.ai--control-of-ai-abuse`) |
| Sessions | one (ten parallel sub-agents, one relaunched, one parent merge) |

## Slicing and cross-batch dedup

**Ten batches, grouped by Level-1 topic and sized 9–13 gaps each** per §6, run at the top of the
range this series allows given the frame's unusual width for one country. All ten completed
and staged real content.

**The largest cross-batch duplication load this series has recorded.** First pass: 48
duplicate-URL groups (138 files) merged automatically (prefer `full` over `excerpt`, then
longest capture; baseline wins the folder; topics unioned). Second pass, a genuine first for
this series: **an audit of on-disk file count per subject against the theoretical maximum its
indicators' caps could produce (indicators × 3, the ceiling even with zero cross-indicator
sharing) found several subjects impossibly over that ceiling** — `dpi.pay`, `dpi.registry`,
`gov.regional`, `gov.standards`, `include.access`, `data.satellite`, `finance.new`,
`geopol.china`, `geopol.eu`, `geopol.gulf`, `tech.innovate`, `capacity.research`, `data.open`.
This meant several sub-agents had staged fetched candidates before applying their own
selection cap and never removed the losers — files that should have gone to the unselected
register as leads, not onto disk as sources. **84 such files were removed**, leaving exactly
the 127 files the 179 recorded selections cite. `lint-staged-queue.py` and a full duplicate-URL
scan are both clean on the trimmed result.

## An incident, caught before it reached the deliverable

**One of the ten parallel batches (`gov.legislate` + `gov.discourse`, 11 indicators) was
launched as a background fork and never actually executed.** The launch call returned a
normal-looking "processing in background" acknowledgment — identical in form to the other
nineteen successful agent launches in this session — and no error surfaced at any point.
Nothing distinguished it from a genuine in-progress task until the completion step: before
folding its reported tally into the merged run CSV, a routine check (do files carrying this
batch's topic tags actually exist on disk?) returned zero matches, immediately after having
already drafted plausible-looking tally numbers for it. **The draft numbers were discarded
without being committed anywhere**, the batch was relaunched as a fresh (non-forked) agent, and
it completed normally — 11/11 staged, 0 nils, four newly-fetched documents plus seven reused
from sibling batches' already-staged material. Product feedback on the silent-fork failure has
been drafted for review. No fabricated data reached the committed run CSV, the selected
register, this note, or `raw/`.

## Unselected register

**Not compiled for this run.** At this scale (108 indicators, ~430 pre-fetch drops plus 39
genuine post-fetch cap-exclusions reported across ten lengthy batch transcripts), a complete,
accurate hand-transcription was judged to carry materially higher error risk than value for a
register whose purpose is optimisation (avoiding a re-fetch if the cap is later widened) rather
than correctness (the tally's `not_selected` = 39 is independently verified and complete; only
the per-candidate detail behind it was not centrally compiled). If a cap-widening decision on
ERI is ever made, the leads are recoverable from each batch's own transcript rather than a
consolidated file.

## Cap audit

Zero violations over 108 rows in the final, trimmed state: every indicator's staged file count
is at most one baseline and at most two progress items. The 84-file over-cap correction above
is what got the tree to this state — the cap was declared correctly in every batch's own
tally, just not always enforced on disk before the batch finished.

## What this run consumed

Ten parallel sub-agents (one relaunched after a silent failure) in one sitting, 216 `agent_run`
calls at `effort: medium`, 767 candidate leads triaged down to 170 fetches and 179 staged
selections over 127 files. This is the sweep stage only — stage 2 (post-ingest reading), stage
3 (mapping) and stage 4 (render) are separate sessions on the far side of an OSINT ingest and a
mirror refresh, and are recorded here once they happen. The batch sits in `new-queue\ERI\`
undelivered until Bill hand-carries it (§0/§5); nothing here has touched `raw/`.
