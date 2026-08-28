# Progress filler — targeted gap sweep for one country (procedure)

Trigger: "**run the progress filler for {ISO}**". Probes the indicators a country's progress report reads ***No evidence*** on, stages what it finds for OSINT's ingest, and accounts for what the run consumed. The accounting in §7 is a deliverable, not overhead.

**Where the trigger names no `{ISO}`**, the queue is `logs/progress-report-log.csv`, not a session's choice: read it top to bottom and take the first row whose `Filler Searched` cell is blank. §8 is what keeps this queue honest — a run that finishes without writing that cell back is a run the next trigger will repeat.

## 0. Authorisation and boundary — read before running

**This is the one Corpus-side process authorised to fetch.** The standing rule that Corpus does not probe (`documentation/report-layer.md` §4) is suspended inside this procedure only. Nothing else in Corpus fetches.

**Nothing is written to `C:\OSINT`, ever.** Candidates are staged to **`C:\corpus-osint-xfer\new-queue\{ISO}\baseline\`** and **`…\{ISO}\progress\`** and nowhere else. That tree is **Bill's hand-carry into OSINT** — a file left there is not queued for ingest until he moves it, so the run finishes by saying plainly that the batch is staged and undelivered.

**Nothing this run finds enters a report directly.** No write to `indicators.csv`, the ledger, or any document. The loop is: stage → Bill hand-carries → OSINT ingests to `raw/` → mirror refreshes → a later BUILD maps the new sources and moves the indicator. A staged file that never comes back through ingest changes nothing, which is correct.

**Ingest adjudicates, this run does not** — no value judgement at staging; scope and origin screening only (§4).

**Precondition**: the Exa MCP (`agent_run` and the fetch tools) must be available in the session. If not, stop and tell Bill; do not substitute another search route — the route being measured is Exa's.

**This is a second gap-probe pass, authorised as one.** OSINT's `reference.md` §7a reserves gap probes to the acquire pass; Bill authorised this pass as a scoped exception — its objects are frame indicators, not the named documents the acquire pass chases; its route is the share; its purpose includes measuring what a probe of this kind consumes. An OSINT session reading this file should read authorisation, not breach.

**Re-run policy — a searched nil is not re-bought.** The test is a **subject row count recorded at probe time**: each run-CSV row carries the unit's ledger row count for the gap's subject (`subject_rows_at_probe` — the subject is the only key a gap has). A prior `nil` is **skipped** while the current count equals the recorded one, re-opened when it differs — an arrival moves the count whatever its `published` date, which matters because an old document ingested late is exactly what Brief 1 exists to find. A skipped gap is carried in the new run CSV as `skipped-prior-nil`, so the accounting stays whole. The key is coarse and errs open: under a populated subject any arrival re-opens every nil beside it, which is the right direction to err.

## 1. Input — the gap list

A **set difference**: every `indicator_id` in `lookups/indicators.csv` (the frame, 121 rows) **absent or blank** in `outputs/reports/{ISO}/indicators.csv` (the held view) — blank counts because the renderer treats an empty `progress` as *No evidence* too, and the renderer bakes the absent rows in at render time, so the held CSV itself contains no gap rows to read. The frame also carries the Topic L2 slug §5 needs and the Level-1 grouping §6 batches by. Per the frame, every gap is a named question: country × Topic L2 × indicator.

## 2. The two briefs per gap indicator

Each gap gets **two Exa Agent briefs** (`agent_run`, `effort: "medium"`): a natural-language objective, the date range stated explicitly, per-item reporting of URL / title / publisher / date / one line on why it matters, and the standing preference for primary and official sources.

**The objective names the chapter, the topic and the indicator together, as `{topic_l1} — {topic}: {indicator}`, all in the objective sentence** — not a trailing context line. A large part of the frame is one or two bare words (`dpi.mis--land` is "Land") that mean nothing without the Topic, and the Topic alone can still lack the anchoring chapter (*MoUs and other agreements* does not say **finance**).

- **Brief 1 — baseline, no date restriction.** Does this thing exist at all, and what is its standing state: the instrument, system, institution or published figure itself, its founding or enacting act, any dated authoritative statement of its current position. **Ask for the single most authoritative document, ranked** — §4a keeps one.
- **Brief 2 — progress, windowed.** Movement since the **first day of the current month, one year back**, matching the progress report's window. **Ask for the two or three most significant movements, ranked, one item per distinct event** — §4a keeps two.

**Ask for a ranked shortlist, not everything it can find.** The cap is applied on Corpus's side with the bodies in hand, so the ranking is a hint — but a brief that asks for the most significant items returns fewer and better candidates, the one saving available upstream of the fetch.

**Exclusions are stated in the brief, then enforced at staging** — `agent_run` has no hard domain filter; the firewall is §4.

## 3. Fetch and capture — OSINT's machinery, unchanged

**The Agent returns leads, never bodies; nothing the Agent writes is ever staged.** Every candidate goes through fetch → verify → classify → stage under the sweep-intake rules of `wiki/intake.md` §7 and the capture rule in `wiki/capture-rule.md`: full verbatim body, never an excerpt or a synthesis, `body_completeness` marked honestly, truncated captures flagged not retried. **Never trust the Agent's dates** — establish `published` from the fetched page.

## 4. Screening and dedup — best-effort against a mirror

- **Origin screen**: run the script, not the prose — `python C:\OSINT\scripts\origin-screen.py --domain a.com b.net`, one command per batch before fetching (the script makes no writes and derives its root from its own location, so the absolute call is correct from anywhere). It reads the mirror's drop list. **An adjudication must be written, and Corpus cannot write OSINT's list** — so any new watch/drop adjudication goes to **`C:\corpus-osint-xfer\progress-filler-drop-list.csv`**, header verbatim `domain,network,status,rule,added,note,,` with every row at the same 8 fields, and §8's note asks OSINT to append those rows to its own list.
- **Scope**: drop what is not our subject, coded from `reference.md` §7's closed table. Every drop logged (§7), nothing discarded silently.
- **Dedup before fetching**: run `python C:\OSINT\scripts\raw-url-index.py --check` read-only against the mirror — `DUP-EXACT`/`DUP-SLUG` skip, `REJECTED` drops, `FLAG-SLUG` never skips; and cross-check what already sits under `new-queue\{ISO}\` — **both folders**, since a sibling may have staged your URL under the other brief. **The script is the whole of this check, not one leg of it** — `logs/sweep-url_log.md` sits outside the interface CC may read from `C:\OSINT` (`CLAUDE.md` → *The OSINT repo is read-only*: `raw/`, `wiki/`, `lookups/` and git metadata only), so this run does not grep it. `raw-url-index.py` reaches back for ever where the log reaches back one rotation, so the script is the wider check, not a narrower substitute.
- **The mirror caveat**: `C:\OSINT` is a mirror, so a URL absent from its logs and index is *probably* new, not certainly. This dedup is a cost-saver; OSINT's ingest remains the authoritative door.

## 4a. Selection — the cap, and why it is Corpus's to apply

**Hard cap: per indicator, one baseline and two progress items. Three, maximum.** Everything above the cap is not staged — recorded in the unselected register instead. **The cap is a maximum, never a quota**: where none survives, the indicator is `nil` and that is the finding; padding to three is the failure this section would cause if read as a target.

### What wins

- **The one baseline** establishes the indicator exists and what it now is: the instrument, system or figure **itself**, not commentary and not the announcement. Operative beats superseded; the primary document beats the news of it; a statute beats a summary. Where the baseline is a number, take the most recent authoritative publication of the series.
- **The two progress items** move the indicator furthest inside the window. **Two distinct events, never two reports of one event** — the commonest way a cap gets wasted. A dated event with a stated position beats a restatement; primary beats syndication; a completed step beats an announced intention.
- A baseline document that also carries in-window movement counts once, as the baseline; the indicator stages two.

### Why this is not the value-drop sweeps are forbidden

`reference.md` §7: a sweep may drop on scope, never on value, because value needs the body and the compiled base. **This run has both** — bodies are fetched before selection, and the compiled base is the progress report: the frame, the indicator's row, what the report already says. OSINT has neither, and the question each gap asks — *does this document answer this named indicator* — only the side holding the frame can put. **The cap is applied where the evidence to apply it lives, and declared, not buried**: §8's note tells OSINT the batch is capped and by what rule, because a thin batch that does not say so reads as a thin sweep.

### The unselected register

**`logs/progress-filler/{ISO}-YYYY-MM-DD-unselected.csv`** — every fetched candidate the cap excluded: `indicator_id, url, title, publisher, published, brief, why_not`. The Agent spend is already paid by selection time, so a later decision to widen the cap is served from this register without a single new `agent_run` call. Corpus-side and stays so — leads, not evidence; nothing in it is a source until staged and ingested.

### Where it runs

**The sub-agent selects, before staging** — it holds the bodies and its indicator's context, and staging then discarding is wasted writing. **The parent audits the cap on merge** (§6) and trims any over-cap indicator itself.

## 5. Staging shape

**Two folders per country: `new-queue\{ISO}\baseline\YYYY-MM-DD-slug.md` and `new-queue\{ISO}\progress\YYYY-MM-DD-slug.md`**, flat within each. Best-effort frontmatter per the source schema (`wiki/schemas.md` §4), with `place:` = the ISO-3, the indicator's Topic L2 slug first in `topics:`, and `sweep_batch: progress-filler-{ISO}-YYYY-MM-DD` — the batch label is what tells OSINT's ingest where these came from.

**The split is by brief, and one document goes in one folder.** A document selected as anyone's baseline is staged under `baseline\`, even where other indicators took it as progress — **baseline wins**, because the baseline layer is what a thin week should carry first, and the selected register still records the document under every indicator that chose it. The dedup at §4 and the merge at §6 work **across the pair**; and the batch is splittable by construction — §7's scheduling is a folder move.

**Four staging checks run as one command — `python scripts/lint-staged-queue.py`, over `new-queue/` or one folder — and §8 makes it a step rather than a memory:**

- **A body must belong to its own frontmatter.** A crossed file carries a correct `url:`, filename and frontmatter over another item's verbatim body — invisible to every URL check — and its `note:`, written from the body, is then a finding derived from the wrong document under a citation that checks out. The check is exact where the capture wrote its own `URL:` line into the body, structural otherwise (title tokens, `url:` host and `publisher:`, the body's opening heading). §6 has the cause and the prevention.
- **The date prefix is padded, never partial** — year only takes `YYYY-01-01`, month only `YYYY-MM-01`, `date_precision` carries the truth. A partial prefix sorts wrongly and does not shard.
- **`note:` must be a quoted scalar** — an unquoted value containing `": "` does not parse. Round-trip every staged file through a YAML parser; zero hits is the check working.
- **A title must carry the source's own orthography.** An ASCII-transliterated title over a correct-UTF-8 body is a staging fault, and most are recoverable without a refetch: rewrite the title from a line in its own body that de-accents to exactly the same string, guarding against all-caps PDF headers.

## 6. Delegation

One country per run. **The parent applies §0's skip first** — one cheap read of the prior run CSVs — writes the `skipped-prior-nil` rows itself, and slices only the **live** gaps. Then **~10–12 live gaps per sub-agent, grouped by Level-1, merging adjacent small chapters to fill a batch** (strict grouping spawns mostly-empty agents). The parent owns every spawn, no sub-agent spawns another, and each is labelled with its slice (`filler ZAF 2/4 dpi+digital`). Each sub-agent returns a terse tally only — per indicator, the §7 row fields — never bodies.

**Stage each file as its body is fetched, one file per body — never from a list of bodies held in context and written out at the end.** A batch write at the end of a slice is how bodies shift one place along the list and every file after the slip carries its neighbour's body; a write-as-you-go cannot produce that. And **the parent verifies files, not answers**: a shifted slice reports a clean tally, so run `python scripts/lint-staged-queue.py` on merge and read what it says.

**On merge the parent audits §4a's cap** — a cap nobody counts is a suggestion — and runs **cross-queue dedup, the parent's alone and spanning both folders**: concurrent sub-agents cannot check each other. One pass after the batches return, keeping `full` bodies over `excerpt`. Where two captures of one page disagree on `published`, record the conflict in the survivor's `note` rather than picking — ingest settles it with the document in hand.

**Count selections, not files.** One survivor per URL, every selected row repointed at it, nothing decremented. A document that genuinely answers two indicators is one file and two selections; the cap still audits per indicator, and no indicator falls to zero by bookkeeping — **never let the arithmetic write a `nil`**, which is a searched absence, a claim about the world no bookkeeping decision has standing to make.

**Audit for the silent overwrite separately**: a sibling staging a different document under a name already used replaces the first file, and a pass keyed on filenames sees a clean queue. The check is **selected rows against files on disk** — every batch's `-selected.csv` names the file it wrote, so a filename claimed by two indicators whose rows meant different documents, or a file whose `indicator_id` is not the one its row claims, is an overwrite.

## 7. What a run consumes — the actual deliverable

**The budget this run spends is Bill's week, not money.** He works on a fixed weekly allowance; when it is gone he is dormant until it resets. The question a filler run answers is **how much of a week it takes and what that displaces** — never dollars.

Two files, both Corpus-side:

- **`logs/progress-filler/{ISO}-YYYY-MM-DD.csv`** — one row per gap indicator: `indicator_id, subject, briefs_run, candidates_returned, fetched, staged_baseline, staged_progress, not_selected, dropped, drop_codes, outcome, subject_rows_at_probe`. `staged_baseline` is 0/1 and `staged_progress` 0–2, so **the cap is auditable from this file alone**. `not_selected` is not a drop and is never coded as one; `drop_codes` stays `reference.md` §7's closed vocabulary and codes candidates, not indicators. `outcome` is its own closed set: `staged` / `nil` / `skipped-prior-nil`. A `nil` — both briefs ran, nothing survivable came back — is a searched absence, itself the finding. `subject_rows_at_probe` is what §0's re-run policy reads. A searched nil is recorded **in the run CSV only** — `probe_at` belongs to the ledger's ***Not held*** vocabulary, a different layer.
- **`documentation/progress-filler-cost-{ISO}.md`** — the summary the scale-out decision reads (throughput records; earlier runs sit in `documentation/archived/`). Record the run in **four stages, each with its own session count and wall time** — sweep, stage-4 read, mapping, render — because they are separated by an OSINT ingest and a mirror refresh and cannot be one sitting. State **yield** as gaps closed against gaps probed, and against sessions spent. The sweep is the visible half and the cheap one; the reading after ingest is a working session on its own, so an estimate counting only the sweep is wrong by roughly the whole of the work.

**The week is shared with OSINT, and OSINT is the heavier consumer.** What the allowance must cover first is OSINT's nightly sweeps to the end of the week; the specific threat is OSINT running out before seven sweeps have run. A filler run reaches that risk through its **output**: every staged document is ingest work OSINT pays for from the same pool. Three consequences: **§4a's cap is a sweep-protection measure**, not only an ingest-quality one; **fillers are what to pace, mappings are not** — the mapping pass costs OSINT nothing; and **the batch is timed as well as sized** — hand one over when the week's sweeps are already secured. The four stages are the natural stopping points if a week tightens; stage 4 is resumable in any case.

**The levers that actually bound a national pass are downstream**: a tighter cap, fewer gaps probed, or a thinner ledger update — each trades coverage for a week, and each is Bill's call, not the run's. State the trade in the summary; do not take it.

## 8. Finishing

1. **Run `python scripts/lint-staged-queue.py` over the staged batch and clear it before anything else.** This is the last point at which a defect costs nothing: past here the batch is Bill's to carry, and a crossed file arrives as a falsified finding under a citation that checks out. Anything withdrawn goes to `logs/progress-filler/{ISO}-YYYY-MM-DD-misfiled.csv` (frontmatter `url:`, the body's true one, the commit that still holds the file); its selected rows move out of the register and the run CSV's staged counts come down to what stands.
2. The share is a repo CC commits for both sides: **check `C:\corpus-osint-xfer\` for uncommitted work on opening, commit the staged batch, push immediately** — never at session end — with a subject naming this as Corpus's work.
3. One note in `notes-for-osint.md`: **`[FYI]`** for the batch — label, count staged, one line on what it is; ingest disposition is OSINT's. **Say the batch is capped and state the rule** (one baseline, two progress, selected Corpus-side with the frame in hand). Where the run made origin adjudications, the note is **`[ACT]`** and adds one line: append the rows in `progress-filler-drop-list.csv` to `logs/drop-list.csv`.
4. **On the run that creates `progress-filler-drop-list.csv`, add it to the share's `README.md` file table** — the canonical enumeration of the share; a file it does not name does not exist to the other side.
5. Tell Bill: gaps searched, staged, nil count, what the run consumed against §7's four stages — **and that the batch sits in `new-queue\{ISO}\` undelivered until he moves it** — with the two folders' counts separately, because they are what he decides between when the week is tight.
6. **Update `logs/progress-report-log.csv`**: set this run's `{ISO}` row's `Filler Searched` cell to today's date, `DD/MM/YYYY` as the column already carries. This is the queue the no-`{ISO}` trigger reads — a run that skips this step leaves its own country selectable again.
7. One line in Corpus's log, per the house form.
