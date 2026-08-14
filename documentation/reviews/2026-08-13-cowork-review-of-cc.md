# Cowork review of CC's final changes (2026-08-13)

*(Reviewed against `cacc093..HEAD`. Verdict: approve; all sound, and three fixed real defects in my code.)*

## The leak gate (F10 / F19 / F20) — the substantive one, and now materially better

CC extended `scripts/leak-check.py` from CSV/JSON/MD/TXT to also scan **HTML, PDF and JS** — the formats the site actually publishes. `design.md` §8 explicitly demanded a gate that checks "the HTML it becomes", not just the markdown; my version didn't meet that, CC's does. `site/` is 273 HTML + 165 PDF vs 107 CSV, so my gate was looking away from most of what ships.

Three genuine bugs in my version, all fixed:

- **Markdown body was unchecked (F19).** My `check_markdown` read only the frontmatter, so a source body pasted into a report's *prose* passed the gate and would only fail once rendered. CC added a body-line scan (with a measured 6,000-char cap; the marker regex catches leaked `type: source` / `body_completeness:`).
- **`raw/` path test false-positived.** My `rel.startswith("raw")` also matched `raw-catalogue.csv`, so the verdict depended on which root you passed — clean under `site`, false-positive under `site/catalogue`. CC's checks path *components*, which is correct.
- **Caps were guessed; now measured.** HTML block cap 8,000 (max legit 3,238), PDF page 12,000 (max 5,490), calibrated against the real site rather than raised until quiet.

Design quality is high: block (not page) is the unit; `pypdf` missing → **fail, not pass** (an unscannable PDF is an unchecked PDF); the PDF page-break split limit is stated honestly rather than papered over; the two "non-rules" (no class/id scan because the report markup is `article-body`; marker needs the colon) are the right exclusions. Verified: runs clean over `outputs/`.

## `rebuild.py` workroot recovery (F2) — a real fix to my code

My `_link_dir` guarded removal with `islink or exists`; a **broken** junction (target moved) reports False to both, so it skipped removal and `mklink` then failed "already exists" — which is the *normal* state after OSINT moves or a container leaves symlinks behind, i.e. the case that has to work. CC switched to `os.path.lexists` and surfaced `mklink`'s error text instead of my `DEVNULL`. Verified on a real Windows broken junction. Correct and necessary.

## Operational changes — all sound

- **Monthly marker moved** to `outputs/reports/last-monthly.txt` where `report-scan.py` looks (it only existed in `upstream/`, so the month-overdue check had been running blind and `/MIR` was about to purge it); RENDER Step 1 gained `/XF README.md`; the stale `upstream/README.md` rewritten.
- **Ran Job 1** — the report-update moved the ledgers forward from the frozen `raw/` (considered/ledger/monthly changes across ~28 units), then re-rendered under the per-subject monthly markers.
- **`finance.py` wired** into RENDER as its own step, correctly flagged as a shell.

## Two things to note (not blockers)

1. **The gate now depends on `pypdf`** on the render machine. It fails-closed if absent (correct), so confirm it's installed or every PDF reports "cannot scan". CC noted `pip install pypdf`.
2. **Monthly backlog grew.** The per-subject marker split minted more `_(narrative not yet written)_` blocks; RENDER skips them, so nothing bad publishes, but the authoring backlog (my task) is now per-subject.

> **Overtaken by events, 2026-08-14.** Two halves of this are no longer true. RENDER does **not** skip them — that rule was removed on 2026-08-13 as worse than useless (`RENDER.md`, and the TCD/TGO stale-page case), so nothing has been standing between an unwritten block and the site. And the renderer no longer mints the placeholder at all: an unwritten block is emitted empty, and `report-render.py --check`'s new check L counts them. The backlog itself stands at 188 blocks across 38 of 57 units and is BUILD's to drain. See `documentation/reviews/2026-08-14-build-changes.md`.

## notes-for-osint #10 — a real finding, correctly routed

A slug (`2026-08-07-nitda-...`) sits in `index/vault.db` but its source has left `raw/` between two catalogue builds — a dangling index entry, or a source that left the vault unnoticed. It matters against the permanent-slug constraint (a citation that can break once live). Written to the OSINT channel for Bill to action, not touched in OSINT. Exactly right.

## Verdict

Approve. Nothing to route back for change. The one action is Bill's: settle OSINT note #10 before launch.
