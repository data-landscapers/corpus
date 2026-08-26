# Progress filler — targeted gap sweep for one country (procedure)

*(Cowork, 2026-08-26, from Bill's outline in `prep/country-progress-filler.md`; revised same day after CC's verification — gap source corrected to the frame/held set difference, REJECTED verdict added, drop-list write path, §7a authorisation and re-run policy stated. Trigger: "**run the progress filler for {ISO}**". First run is **ZAF**, and the first run is the evidence — this is a **cost investigation** before it is a gap-filler, so the accounting in §7 is a deliverable, not overhead.)*

## 0. Authorisation and boundary — read before running

**This is the one Corpus-side process authorised to fetch** *(Bill, 2026-08-26)*. The standing rule that Corpus does not probe (`documentation/report-layer.md` §4) is not changed by this file: it is suspended inside this procedure only, because Bill wants the sweep run here and the returns handed to OSINT. Nothing else in Corpus fetches.

**Nothing is written to `C:\OSINT`, ever.** Candidates are staged to **`C:\corpus-osint-xfer\new-queue\`** and nowhere else. That folder is **Bill's hand-carry into OSINT** — a file left there is **not queued for ingest until he moves it**, so the run finishes by saying plainly that the batch is staged and undelivered.

**Nothing this run finds enters a report directly.** No write to `indicators.csv`, the ledger, or any document. The loop is: stage → Bill hand-carries → OSINT ingests to `raw/` → mirror refreshes → a later BUILD maps the new sources and moves the indicator. A staged file that never comes back through ingest changes nothing, which is correct.

**Ingest adjudicates, this run does not** — same as every OSINT sweep: no value judgement at staging, scope and origin screening only (§4).

**Precondition**: the Exa MCP (`agent_run` and the fetch tools) must be available in the CC session running this — it normally lives OSINT-side. If it is not connected, stop and tell Bill; do not substitute another search route, because the cost being measured is Exa's.

**This is a second gap-probe pass, and it is authorised as one.** OSINT's `reference.md` §7a rules that gap probes are *"the acquire pass's, and no other's"*, precisely on the cost argument this run exists to measure. Bill authorised this pass on 2026-08-26 as a deliberate, scoped exception: its objects are **frame indicators**, not the named documents §7a's acquire pass chases; its route is the share, not OSINT's queues; and its purpose is to price the probe. An OSINT session reading this file should read authorisation, not breach.

**Re-run policy — a searched nil is not re-bought** *(the rule both `report-layer.md` §4 and `reference.md` §7a state: a re-search over an unchanged base returns the same nothing at full price)*. The test is a **subject row count, recorded at probe time**: each run CSV row carries the count of the unit's ledger rows for the gap's subject (`subject_rows_at_probe` — the subject is the only key a gap has, since by definition it holds no `indicators.csv` row). A prior `nil` is **skipped** while the current count equals the recorded one, and re-opened when it differs — an arrival moves the count whatever its `published` date, which matters because an old document ingested late is exactly what Brief 1 exists to find. A skipped gap is carried in the new run CSV with outcome `skipped-prior-nil`, so the accounting stays whole. **The key is coarse, and errs open**: under a subject with zero ledger rows the skip holds until the filler's own staging comes back through ingest, but under a populated subject *any* arrival re-opens *every* nil beside it — on ZAF's shape, 18 of the 44 gaps sit under empty subjects where the skip is reliable, and 15 under subjects holding 5–22 rows where it will re-buy some nils. Re-probing too often is the right direction to err; just don't read this as a per-indicator memory.

## 1. Input — the gap list

The gap list is a **set difference**: every `indicator_id` in `lookups/indicators.csv` (the frame, 121 rows) **absent or blank** in `outputs/reports/{ISO}/indicators.csv` (the held view) — blank because the renderer treats an empty `progress` as *No evidence* too, so a held row with nothing in that column is a gap the plain difference would miss. The renderer fills those absent rows in as *No evidence* at bake time, so the held CSV itself contains no gap rows — reading it for them returns nothing *(CC's verification, 2026-08-26, correcting this file's first draft)*. The difference is also the cleaner source: the frame carries the Topic L2 slug §5 needs and the Level-1 grouping §6 batches by, with no HTML parsing. ZAF currently: 121 − 77 held = **44 gaps**, and per the frame every one is a named question: country × Topic L2 × indicator.

## 2. The two briefs per gap indicator

Each gap gets **two Exa Agent briefs** (`agent_run`, `effort: "medium"`), composed per `SWEEP-COUNTRY-DEEP.md` §3 — a natural-language objective with `{country}` and the indicator filled in, the date range stated explicitly, per-item reporting of URL / title / publisher / date / one line on why it matters, and the standing instruction to prefer primary and official sources.

- **Brief 1 — baseline, no date restriction.** Does this thing exist at all, and what is its standing state? For *{indicator}* in *{country}*: the instrument, system, institution or published figure itself, its founding or enacting act, and any dated authoritative statement of its current position.
- **Brief 2 — progress, windowed.** Movement on *{indicator}* in *{country}* since the **first day of the current month, one year back** (a run in August 2026 searches from 1 August 2025) — matching the progress report's window.

**Exclusions are stated in the brief, then enforced at staging** — `agent_run` has no hard domain filter; the firewall is §4.

## 3. Fetch and capture — OSINT's machinery, unchanged

**The Agent returns leads, never bodies; nothing the Agent writes is ever staged.** Every candidate goes through fetch → verify → classify → stage exactly as `SWEEP-DAILY-OFFLIST.md` runs it, under the standing capture rule in `C:\OSINT\wiki\capture-rule.md`: full verbatim body, never a search excerpt or an AI synthesis, `body_completeness` marked honestly, truncated captures flagged not retried. **Never trust the Agent's dates** — establish `published` from the fetched page (`SWEEP-COUNTRY-DEEP.md` §3a records what that mistake cost).

## 4. Screening and dedup — best-effort against a mirror

- **Origin screen**: run the script, not the prose — `python C:\OSINT\scripts\origin-screen.py` in its `--domain a.com b.net` mode, **one command per batch before fetching** (that mode exists for exactly this case, and the script makes no writes; the prose file `wiki/origin-screen.md` is its spec; the path is absolute because a Corpus session's cwd is not the mirror, and both scripts derive their root from their own location, so an absolute call is correct from anywhere). It reads the mirror's `logs/drop-list.csv` (stale-read caveat below applies). **The screen's contract is that an adjudication is written, and Corpus cannot write OSINT's list** — so any new watch/drop adjudication this run makes goes to **`C:\corpus-osint-xfer\progress-filler-drop-list.csv`**, header **verbatim** `domain,network,status,rule,added,note,,` — including the two trailing empty fields, **and every row written at the same 8 fields** (the live file's ragged tail is not the model; "same columns" composed from memory is how a shared file forks) — and §8's note asks OSINT to append those rows to its own list. An adjudication noted but not written is the failure the screen exists to prevent; this is the writable path this route has.
- **Scope**: drop what is not our subject, coded from `reference.md` §7's closed table. Every drop logged (§7 below), nothing discarded silently.
- **Dedup before fetching**: grep the mirror's `logs/sweep-url_log.md`; run `python C:\OSINT\scripts\raw-url-index.py --check` read-only against the mirror's index — `DUP-EXACT`/`DUP-SLUG` skip, **`REJECTED` drops** (`--check` loads `lookups/rejected-urls.csv` itself, the store that outlives the record: dropped, never fetched, never read), `FLAG-SLUG` never skips; cross-check what already sits in `new-queue\`.
- **The mirror caveat**: `C:\OSINT` is a mirror, so its logs and index read as whatever the last sync left. A URL absent from them is *probably* new, not certainly — this dedup is a cost-saver, not a guarantee, and OSINT's ingest remains the authoritative door where any duplicate that slips through is settled with the body in hand.

## 5. Staging shape

Flat to `new-queue\YYYY-MM-DD-slug.md`, best-effort frontmatter per the daily sweep's schema (`SWEEP-DAILY-LIST.md`), with `place:` = the ISO-3, the indicator's `Topic L2` slug first in `topics:`, and `sweep_batch: progress-filler-{ISO}-YYYY-MM-DD` — the batch label is what tells OSINT's ingest where these came from.

## 6. Delegation

One country per run. **The parent applies §0's skip first** — one cheap read of the prior run CSVs — writes the `skipped-prior-nil` rows itself, and slices only the **live** gaps, so batches are sized on work rather than part-filled with no-ops. Then **~10–12 live gaps per sub-agent, grouped by Level-1** so related briefs are screened and deduped side by side — **merging adjacent small chapters to fill a batch**, which the label example below already shows, because the chapters are not the right size on their own: ZAF's 44 gaps sit across ten Level-1 chapters and only DPI (11) reaches the band, seven holding five or fewer and two holding one. Strict grouping would spawn ten mostly-empty sub-agents; merged, ZAF is four. The parent owns every spawn, no sub-agent spawns another, and each is labelled with its slice (`filler ZAF 2/4 dpi+digital`). Each sub-agent returns a terse tally only — per indicator, the §7 row fields (`outcome`, counts, `subject_rows_at_probe`) — never bodies.

## 7. Cost accounting — the actual deliverable

Two files, both Corpus-side (`logs/progress-filler/` does not exist yet — the first run creates it):

- **`logs/progress-filler/{ISO}-YYYY-MM-DD.csv`** — one row per gap indicator: `indicator_id, subject, briefs_run, candidates_returned, fetched, staged, dropped, drop_codes, outcome, subject_rows_at_probe`. `outcome` is its own closed set of three — `staged` / `nil` / `skipped-prior-nil` — because `drop_codes` is `reference.md` §7's closed vocabulary and codes **candidates**, not indicators, and must not be bent to carry an indicator state. A `nil` (both briefs ran, nothing survivable came back) is **a searched absence, which is itself the finding** the cost question needs; `subject_rows_at_probe` is what §0's re-run policy reads.
- **`prep/progress-filler-cost-{ISO}.md`** — the summary the scale-out decision reads: wall time, `agent_run` count and effort, fetch count, staged/dropped totals, estimated spend (~$0.10 per `agent_run` — ZAF's 44 gaps × 2 briefs ≈ 88 calls ≈ $8.80 before fetching), and **yield**: staged candidates per gap and per dollar. **State the extrapolation the pilot exists to price**: at ZAF's shape, a full sweep is of the order of 54 countries × ~44 gaps × 2 ≈ 4,700 `agent_run` calls ≈ **$470 per pass** — the summary's job is to say whether the yield justifies that, and if not, which lever moves it: merge the two briefs into one, batch several same-L2 indicators into one brief, or drop effort. The **first run measures Bill's design as specified**, unmodified, or the measurement answers a different question.

A searched nil is recorded **in the run CSV only** — it is what §0's re-run policy reads. It is not stamped anywhere else: `probe_at` is a `gaps.csv` column belonging to the ledger's ***Not held*** vocabulary, a different layer with a different closed set, and the indicator file has no probe field by design.

## 8. Finishing

1. The share is a repo CC commits for both sides: **check `C:\corpus-osint-xfer\` for uncommitted work on opening, commit the staged batch, push immediately** — never at session end — with a subject naming this as Corpus's work.
2. One note in `notes-for-osint.md`: **`[FYI]`** for the batch itself — label, count staged, one line on what it is; ingest disposition is OSINT's. Where the run made origin adjudications, the note is **`[ACT]`** instead and adds one line: append the rows in `progress-filler-drop-list.csv` to `logs/drop-list.csv` — decided, the reader executes.
3. **On the run that creates `progress-filler-drop-list.csv`, add it to the share's `README.md` file table** — that table is the canonical enumeration of the share for both sides, CC maintains it, and a file it does not name does not exist to the other side.
4. Tell Bill: gaps searched, staged, nil count, cost — **and that the batch sits in `new-queue\` undelivered until he moves it**.
5. One line in Corpus's log, per the house form.
