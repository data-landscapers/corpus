# BULLETIN-TOPUP.md — the lunch-time bulletin, off OSINT's late-morning sweep

Trigger: **"run the bulletin top-up"**, typed by hand, after OSINT has run `SWEEP-BULLETIN.md`. Manual only, for the same reason that one is: it exists to put a time of day on a document, and a time of day is Bill's to choose.

**What it is for.** OSINT's sweep runs overnight, so the bulletin's two-day window holds yesterday in full and nothing at all of today — on 2026-08-22 the window held 24 records and every one of them was published on the 21st. OSINT's `SWEEP-BULLETIN.md` fills that gap on its side: a today-only sweep, a scoped ingest, a mirror, late morning. This is the other half of it. Without this run the top-up reaches `O:\` and stops there, because nothing on this side reads it.

**It is BUILD stage 7 and one document's render, and nothing else.** Every rule stays in `BUILD.md`, `RENDER.md` and `documentation/bulletin.md` and is not restated. What is written here is only what is different about running that stage on its own at midday.

## Why the cycle trigger does not fire, and must not

`scripts/osint-cycle-ready.py` watches `max(End)` over the rotation table in `logs/sweep-cycle_log.md`. **`SWEEP-BULLETIN.md` advances no high-water mark and never touches that table** — deliberately, so a run at 11:00 cannot shorten tonight's cycle window. So the detector stays at exit 1 through a top-up, which is right twice over: a full `CYCLE.md` is three hours of report authoring over a handful of new records, and firing it at midday would put a build over `raw/` while the day's work is going on.

The signal to read instead is **`sweep/bulletin/manifest-YYYY-MM-DD.md` on the mirror**. Same proof as the cycle's: the manifest is committed before the mirror runs and the mirror is that run's last act, so a manifest visible here cannot have arrived except by an FFS run that started after it was written.

```bash
ls "${CORPUS_OSINT_MIRROR:-/c/OSINT}/sweep/bulletin/manifest-$(date +%F).md"
```

Absent means the top-up has not landed and there is nothing to build. Do not run the stage against last night's evidence and stamp it midday — that publishes a fresh clock over stale material, which is the one thing the stamp is supposed to make impossible.

## The run

```bash
python scripts/rebuild.py --catalogue                        # stage 2, the only precondition
python scripts/bulletin.py --scan                            # the window, and what needs a summary
python scripts/bulletin.py --write {slug} --text "…"         # one to three sentences, per item
python scripts/bulletin.py --assemble
python scripts/leak-check.py outputs || exit 1               # the gate, unchanged and not optional
python scripts/render.py outputs/bulletins/corpus-bulletin.md
python scripts/log-line.py build "bulletin top-up: window N, K new summaries, rendered — ok"
git add -A && git commit -m "Bulletin top-up: <n> items published today"
```

**`--catalogue`, not `--all`.** Stage 7 reads `outputs/catalogue/raw-catalogue.csv` and nothing the report or finance layers write (`BUILD.md` stage 7, last paragraph), so the finance and vocab compiles are cost with no consumer here.

**No stage 0 sentinel and no `--start build`.** `logs/.build-in-progress` is the assertion that a *cycle* is part-way through, and `RENDER.md` Step 0 gates on it; a ten-minute run that writes one document has nothing for it to protect, and a sentinel left behind by a crash here would block tonight's cycle over a document that rebuilds itself in full on the next run.

**Nothing else re-renders.** No home page, no catalogue page, no report loop, so `RENDER.md` Step 2's coverage assertion is not in play — it counts a full pass and this is one file. The site catalogue lags a morning behind by design; the bulletin's own links go to publishers' records rather than to catalogue rows, so nothing it publishes points at the gap.

**The dated PDF is `render.py`'s call as always.** A second cut on one day gets `editions.py`'s `-2`; a body that has not moved holds its edition and refreshes only the page, which is the bulletin's own exception at `RENDER.md` → *The bulletin* and exactly the case this run produces on a nil morning.

## Deploy is Bill's

The commit above lands; the push does not. Deploy is the GitHub Pages workflow firing on a push touching `site/**` (`RENDER.md` Step 7), and Cowork cannot push. **Say so when the run finishes** — a top-up committed and unpushed is a bulletin that reads correctly in git and still says yesterday on the web, which is the failure this whole path exists to prevent, arriving one step later.

## A nil morning is a finished run

OSINT's sweep can stage nothing, and on a today-only window it often will. The stage still runs: `--assemble` moves the stamp, reports `checked` rather than `written`, and the page says the day is empty and why. That is `BUILD.md` stage 7's rule and it is the whole reason the stamp exists — *we looked and nothing was published* is a different claim from *nobody has looked since yesterday*, and only this run can make the first one.

## Boundary

Nothing here writes to OSINT. The manifest check is a read of the mirror; `CLAUDE.md` has the rule and the reasoning.
