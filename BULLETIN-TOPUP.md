# BULLETIN-TOPUP.md — the lunch-time bulletin, off OSINT's late-morning sweep

Trigger: **"run the bulletin top-up"**, typed by hand, after OSINT has run `SWEEP-BULLETIN.md`. Manual only, for the same reason that one is: it exists to put a time of day on a document, and a time of day is Bill's to choose.

**What it is for.** OSINT's sweep runs overnight, so the bulletin's two-day window holds yesterday in full and nothing at all of today — on 2026-08-22 the window held 24 records and every one of them was published on the 21st. OSINT's `SWEEP-BULLETIN.md` fills that gap on its side: a today-only sweep, a scoped ingest, a mirror, late morning. This is the other half of it. Without this run the top-up reaches `O:\` and stops there, because nothing on this side reads it.

**It is BUILD stage 7 and one document's render, and nothing else.** Every rule stays in `BUILD.md`, `RENDER.md` and `documentation/bulletin.md` and is not restated. What is written here is only what is different about running that stage on its own at midday.

## Why the cycle trigger does not fire, and must not

`scripts/osint-cycle-ready.py` watches `max(End)` over the rotation table in `logs/sweep-cycle_log.md`. **`SWEEP-BULLETIN.md` advances no high-water mark and never touches that table** — deliberately, so a run at 11:00 cannot shorten tonight's cycle window. So the detector stays at exit 1 through a top-up, which is right twice over: a full `CYCLE.md` is three hours of report authoring over a handful of new records, and firing it at midday would put a build over `raw/` while the day's work is going on.

The signal to read instead is **OSINT's ingest clock, against the stamp the bulletin already carries**.

```bash
python -c "import sys; sys.path.insert(0,'scripts'); import osint_lib; print(osint_lib.last_ingest())"
grep '^compiled:' outputs/bulletins/corpus-bulletin.md
```

Newer means there is new material and the run is worth making. Equal means the bulletin is already built off the current ingest and there is nothing to do — which is also the correct answer on a nil morning, where the sweep ran, admitted nothing, and OSINT's clock did not move because its material did not.

**This was `sweep/bulletin/manifest-YYYY-MM-DD.md` until 2026-08-22, and that was wrong the moment OSINT began mirroring after every commit** *(Bill, the same afternoon)*. The original reasoning borrowed the cycle trigger's proof — the artefact is committed before the mirror runs and the mirror is the run's last act, so seeing it here proves the copy carried it. The second half of that stopped being true. Under an after-every-commit mirror the tree is copied at each of `SWEEP-BULLETIN.md`'s two commits, and **the manifest is in the first of them**: `25625b75` at 10:13 carried `new/` and the manifest, and `raw/` did not arrive until `9a1189ee` at 10:17. A check on the manifest would therefore have fired in a four-minute window on a tree where the item was staged and not yet admitted — `--catalogue` would have found nothing, `--scan` nothing to write, and `--assemble` would have stamped the clock and published *we looked and nothing was published today* on the morning something was. A silent wrong answer, which is the exact failure the gate exists to prevent.

**So the gate reads an artefact of the step it is actually waiting for.** `logs/ingested_log.md` is written at the moment of admission, in the ingest commit, and it is already the file `osint_lib` reads for the bulletin's own byline — so the fact that lets the run start is the same fact the page will go on to state, and the two cannot disagree. The general rule is worth keeping past this instance: **a readiness check must key on an artefact of the step it is waiting for, not on one that merely tends to arrive with it.** The manifest was only ever a proxy for *the ingest has run*, and a proxy holds until the thing it stands in for moves.

Do not run the stage against last night's evidence and stamp it midday — that publishes a fresh clock over stale material, which is the one thing the stamp is supposed to make impossible.

## The run

```bash
python scripts/rebuild.py --catalogue                        # stage 2, the only precondition
python scripts/bulletin.py --scan                            # the window, and what needs a summary
python scripts/bulletin.py --write {slug} --text "…"         # one to three sentences, per item
python scripts/bulletin.py --assemble
python scripts/render.py outputs/bulletins/corpus-bulletin.md
python scripts/catalogue.py                                  # publish the catalogue the bulletin was built off
python scripts/log-line.py build "bulletin top-up: window N, K new summaries, rendered — ok"
git add -A && git commit -m "Bulletin top-up: <n> items published today"
```

**`--catalogue`, not `--all`.** Stage 7 reads `outputs/catalogue/raw-catalogue.csv` and nothing the report or finance layers write (`BUILD.md` stage 7, last paragraph), so the finance and vocab compiles are cost with no consumer here.

**No stage 0 sentinel and no `--start build`.** `logs/.build-in-progress` is the assertion that a *cycle* is part-way through, and `RENDER.md` Step 0 gates on it; a ten-minute run that writes one document has nothing for it to protect, and a sentinel left behind by a crash here would block tonight's cycle over a document that rebuilds itself in full on the next run.

**The catalogue page is published, and it was not before** *(Bill, 2026-08-24)*. `--catalogue` at the top of the run rebuilds `outputs/catalogue/`, so from that moment the top-up is working off a catalogue the site is not serving — and `scripts/catalogue.py` is what closes that. It used to be left out on the reasoning that *the site catalogue lags a morning behind by design*, which held only while nothing pointed at the gap. It does not hold now: the count on the catalogue page is a published claim about what the base holds, the bulletin published the same morning says otherwise, and the two are a morning apart every day the top-up runs — 10,731 against 10,747 on the day this was noticed. Running the page costs a few seconds and one commit, against a number on the site that is wrong until the next cycle. **The names index is not rebuilt**, so the morning's new records are searchable by title and publisher and not yet by names inside them; that lag is real, bounded and invisible, which is the difference.

**Nothing else re-renders.** No home page, no report loop, so `RENDER.md` Step 2's coverage assertion is not in play — it counts a full pass and this is one document plus one page.

**The dated PDF is `render.py`'s call as always.** A second cut on one day gets `editions.py`'s `-2`; a body that has not moved holds its edition and refreshes only the page, which is the bulletin's own exception at `RENDER.md` → *The bulletin* and exactly the case this run produces on a nil morning.

## Deploy is Bill's

The commit above lands; the push does not. Deploy is the GitHub Pages workflow firing on a push touching `site/**` (`RENDER.md` Step 7), and Cowork cannot push. **Say so when the run finishes** — a top-up committed and unpushed is a bulletin that reads correctly in git and still says yesterday on the web, which is the failure this whole path exists to prevent, arriving one step later.

## A nil morning is a finished run

OSINT's sweep can stage nothing, and on a today-only window it often will. The stage still runs: `--assemble` moves the stamp, reports `checked` rather than `written`, and the page says the day is empty and why. That is `BUILD.md` stage 7's rule and it is the whole reason the stamp exists — *we looked and nothing was published* is a different claim from *nobody has looked since yesterday*, and only this run can make the first one.

## Boundary

Nothing here writes to OSINT. The manifest check is a read of the mirror; `CLAUDE.md` has the rule and the reasoning.
