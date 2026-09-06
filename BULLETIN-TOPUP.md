# BULLETIN-TOPUP.md — the lunch-time bulletin, off OSINT's late-morning sweep

Trigger: **"run the bulletin top-up"**, typed by hand, after OSINT has run `SWEEP-BULLETIN.md`. Manual only: it exists to put a time of day on a document, and a time of day is Bill's to choose.

**What it is for.** OSINT's overnight sweep leaves the bulletin's two-day window holding yesterday in full and nothing of today. `SWEEP-BULLETIN.md` fills that gap on OSINT's side — a today-only sweep, a scoped ingest, a mirror, late morning. This is the other half: without this run the top-up reaches the mirror and stops there, because nothing on this side reads it.

**It is BUILD stage 7, its render, and the pages that publish a count of the base — and nothing else.** Every rule stays in `BUILD.md`, `RENDER.md` and `documentation/bulletin.md`; what is written here is only what differs about running that stage alone at midday.

## Why the cycle trigger does not fire, and must not

`osint-cycle-ready.py` watches `max(End)` over the rotation table, and `SWEEP-BULLETIN.md` never touches that table — deliberately, so a run at 11:00 cannot shorten tonight's cycle window. The detector stays at exit 1 through a top-up, which is right twice over: a full `CYCLE.md` is hours of report authoring over a handful of records, and firing it at midday puts a build over `raw/` while the day's work is going on.

The signal to read instead is **OSINT's ingest clock, against the stamp the bulletin already carries**:

```bash
python -c "import sys; sys.path.insert(0,'scripts'); import osint_lib; print(osint_lib.last_ingest())"
grep '^compiled:' outputs/bulletins/corpus-bulletin.md
```

Newer means new material and the run is worth making. Equal means the bulletin is already built off the current ingest — also the correct answer on a nil morning, where the sweep admitted nothing and OSINT's clock did not move.

**A readiness check must key on an artefact of the step it is waiting for, not one that merely tends to arrive with it.** `cycle-manifest.json` carries `collection.last_admission`, and `SWEEP-BULLETIN` writes the manifest after its final commit and before it mirrors — so the stamp that lets the run start cannot arrive before the records it counts, and it is the same file the bulletin's own byline reads. The fact that starts the run is the fact the page will state, and the two cannot disagree. (A check on the sweep's *staging* manifest fails here: under an after-every-commit mirror that one arrives a commit before `raw/` does, and a run in that window would publish *we looked and nothing was published* on a morning something was.)

Do not run the stage against last night's evidence and stamp it midday — that publishes a fresh clock over stale material, the one thing the stamp exists to make impossible.

## The run

```bash
python scripts/rebuild.py --catalogue                        # stage 2, the only precondition
python scripts/bulletin.py --scan                            # the window, and what needs a summary
python scripts/bulletin.py --write {slug} --text "…"         # one to three sentences, per item
python scripts/bulletin.py --assemble
python scripts/render.py outputs/bulletins/corpus-bulletin.md
python scripts/catalogue.py                                  # publish the catalogue the bulletin was built off
python scripts/home.py                                       # the stat bar makes the same claim on three more pages
python scripts/log-line.py build "bulletin top-up: window N, K new summaries, rendered — ok"
git add -A && git commit -m "Bulletin top-up: <n> items published today"
```

- **`--catalogue`, not `--all`.** Stage 7 reads the catalogue and nothing the report or finance layers write, so those compiles are cost with no consumer here.
- **No stage 0 sentinel and no `--start build`.** The sentinel asserts a *cycle* is part-way through; a ten-minute run writing one document has nothing for it to protect, and a sentinel left by a crash here would block tonight's cycle over a document that rebuilds itself in full next run.
- **The catalogue page is published in the same run.** `--catalogue` rebuilds `outputs/catalogue/`, so from that moment the top-up works off a catalogue the site is not serving; `scripts/catalogue.py` closes the gap. The count on the catalogue page is a published claim about what the base holds, and it would otherwise disagree with the bulletin published the same morning. The names index comes with it — `rebuild.py --catalogue` runs stages 2b and 2c — so the shards are part of the top-up's commit, which is why it is larger than one document.
- **The home page goes with it, for the same reason.** `scripts/home.py` is RENDER Step 3 and its stat bar — total, published this year, published this month — is the same published claim about the same base as the catalogue page's count, on `site/index.html`, `site/countries/` and `site/topics/`. Left out, `/` says one figure and `/catalogue/` another for the rest of the day. The counts are publication-date counts off `raw-catalogue.csv`, so they move on a top-up exactly when the bulletin does. The country and topic matrices come with it and their per-country figures are unchanged; only the bar fills rescale against the new maximum.
- **Nothing else re-renders.** No per-country or per-topic pages, no report loop; RENDER Step 2's coverage assertion is not in play — it counts a full pass and this is one document plus four pages.
- **The dated PDF is `render.py`'s call as always.** A second cut in a day gets `-2`; an unmoved body holds its edition and refreshes only the page — the bulletin's own exception at `RENDER.md` → *The bulletin*, and exactly what a nil morning produces.

## Deploy

Deploy is the GitHub Pages workflow firing on a push touching `site/**` (`RENDER.md` Step 7). A session that can push, pushes. A Cowork session cannot — **say so when the run finishes**: a top-up committed and unpushed reads correctly in git and still says yesterday on the web, which is the failure this whole path exists to prevent, arriving one step later.

## A nil morning is a finished run

The stage still runs: `--assemble` moves the stamp, reports `checked` rather than `written`, and the page says the day is empty and why. *We looked and nothing was published* is a different claim from *nobody has looked since yesterday*, and only this run can make the first one.

## Boundary

Nothing here writes to OSINT. The readiness check is a read of the mirror; `CLAUDE.md` has the rule.
