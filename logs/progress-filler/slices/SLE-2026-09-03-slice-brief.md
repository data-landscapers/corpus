# Progress filler — SLE (Sierra Leone) — slice brief, 2026-09-03

You are one slice of a `PROGRESS-FILLER.md` run over **SLE (Sierra Leone)**. The parent owns the
merge; you own your slice's gaps end to end. Read `C:\CORPUS\PROGRESS-FILLER.md` if you need the
full procedure — this file is the operative extract.

## Hard boundaries

- **Never write anything to `C:\OSINT`.** It is read-only, always. You may READ only its
  `raw/`, `wiki/`, `lookups/` and run its two scripts named below.
- **Do no git operations at all.** No `git add`, no commit, no status in any repo. The parent commits.
- Stage ONLY to `C:\corpus-osint-xfer\new-queue\SLE\baseline\` and
  `C:\corpus-osint-xfer\new-queue\SLE\progress\`. Both already exist. Flat, no subfolders.
- Write your own logs ONLY to the three slice files named at the end. Do not touch any other
  file under `C:\CORPUS\logs\`.
- Do not spawn sub-agents.

## The window

Brief 2's window is **2025-09-01 to today (2026-09-03)** — the first day of the current month,
one year back. State that range explicitly in the brief.

## Batch label

`sweep_batch: progress-filler-SLE-2026-09-03`

## 1. Two Exa Agent briefs per gap indicator

For each indicator in your slice, run **two** `mcp__exa__agent_run` calls with
`effort: "medium"`. If a call returns "still running", resume it with its `runId` until it
completes — never start a duplicate run for the same brief.

The objective sentence must name the chapter, topic and indicator together as
`{topic_l1} — {topic}: {indicator}`, inside the sentence, not as a trailing context line.
A bare indicator name ("Land", "Customs") means nothing without its topic and chapter.

Ask for, per item: URL, title, publisher, date, and one line on why it matters. State the
standing preference for **primary and official sources** (government ministries, NATCOM,
Bank of Sierra Leone, Statistics Sierra Leone, Parliament, the Sierra Leone Gazette, NCRA,
the operating institution itself, multilateral primary documents). Sierra Leone's official
language is **English**, so language is not a barrier here — but that also means the open web
carries a great deal of low-grade English aggregation about Sierra Leone. Prefer the issuing
body over the report of it, every time.

- **Brief 1 — baseline, no date restriction.** Does this thing exist at all in Sierra Leone and
  what is its standing state: the instrument, system, institution or published figure itself,
  its founding or enacting act, any dated authoritative statement of its current position.
  **Ask for the single most authoritative document, ranked.**
- **Brief 2 — progress, windowed to 2025-09-01 through 2026-09-03.** Movement in that window.
  **Ask for the two or three most significant movements, ranked, one item per distinct event.**

State exclusions in the brief (no content farms, no PDF re-hosting aggregators, no AI-generated
summary sites, no machine translations of another page) — but the exclusions are *enforced* at
staging by the screen at step 3, not by the Agent.

## 2. Fetch and capture — the Agent returns leads, never bodies

**Nothing the Agent writes is ever staged.** Every candidate you intend to stage must be fetched
with `mcp__exa__web_fetch_exa` (use `maxCharacters: 50000`) and staged with the **full verbatim
body** the fetch returned.

- The stored body is always the source's own words. A search excerpt or any paraphrase is
  **never** an acceptable body.
- These bodies are never republished — a private personal research vault, matching the curator's
  established web-clipper practice, under the UK CDPA s.29 research / private-study exception.
- **A truncated capture is flagged, not retried**: stage what came back with
  `body_completeness: excerpt` and say so in one line of `note:`.
- A hard fetch failure or refusal is a **per-item** failure, logged, never a run-stopper.
- A **paywall serving a free lede** is `body_completeness: paywalled`, kept only where the free
  body excluding the title adds value. **Drop headline-only stubs** rather than stage them.
- **Never trust the Agent's dates.** Establish `published` from the fetched page itself. Where
  the page carries no date, infer at the coarsest honest precision and mark
  `date_precision: year` or `month` with `date_source: inferred`.

## 3. Screening and dedup — before you fetch, once per batch of candidates

- **Origin screen**: `python C:\OSINT\scripts\origin-screen.py --domain a.com b.net`
  — one command per batch of candidate domains, before fetching. It makes no writes.
- **Scope**: drop what is not our subject, coded from OSINT `wiki/reference.md` section 7's
  closed table. Every drop goes in your run CSV with its code. Nothing discarded silently.
- **Dedup**: `python C:\OSINT\scripts\raw-url-index.py --check` (read-only) on candidate URLs.
  `DUP-EXACT`/`DUP-SLUG` skip. `REJECTED` drops. `FLAG-SLUG` never skips.
  **Do NOT grep `C:\OSINT\logs\` — it is outside the readable interface.**
- **Also cross-check `C:\corpus-osint-xfer\new-queue\SLE\` — BOTH folders** — before staging:
  a sibling slice may already have staged your URL under the other brief. `grep -rl "<url>"`.
  Files may already be there from an earlier attempt; top up, never restage.
- **New origin adjudications** (a domain you had to rule on that OSINT's list does not carry)
  go to `C:\corpus-osint-xfer\progress-filler-drop-list.csv`, **appended**, header verbatim
  `domain,network,status,rule,added,note,,` — every row at the same **8** fields (two trailing
  empty). `added` is `2026-09-03`, `note` says it was adjudicated during progress-filler SLE
  slice N. Only append if you genuinely adjudicated; re-read the file before appending because
  siblings append too, and append with a single shell append so you never rewrite the file.

## 4. Selection — the cap

**Hard cap, per indicator: one baseline and two progress items. Three maximum.**

- **The cap is a maximum, never a quota.** Where nothing survives, the indicator is `nil` and
  that is the finding. Padding to three is a failure, not a success.
- **The one baseline** establishes the indicator exists and what it now is: the instrument,
  system or figure **itself**, not commentary and not the announcement of it. Operative beats
  superseded; the primary document beats the news of it; a statute beats a summary. Where the
  baseline is a number, take the most recent authoritative publication of the series.
- **The two progress items** move the indicator furthest inside the window. **Two distinct
  events, never two reports of one event.** A dated event with a stated position beats a
  restatement; primary beats syndication; a completed step beats an announced intention.
- A baseline document that also carries in-window movement counts once, as the baseline; that
  indicator then stages two files total.
- **Select before staging**, with the bodies in hand. Everything fetched and excluded by the cap
  goes in your unselected CSV — that register is what a later widening of the cap is served from.

## 5. Staging shape

`new-queue\SLE\baseline\YYYY-MM-DD-slug.md` and `new-queue\SLE\progress\YYYY-MM-DD-slug.md`.

**One document goes in one folder. Baseline wins**: a document selected as anyone's baseline is
staged under `baseline\` even where another indicator took it as progress.

Filename: date prefix **padded, never partial** — year-only precision takes `YYYY-01-01`,
month-only takes `YYYY-MM-01`; `date_precision` carries the truth. Then a short descriptive
slug: lowercase ASCII, hyphens, no accents, naming the country/publisher and the thing.

Frontmatter (best-effort per OSINT `wiki/schemas.md` section 4) — the shape is:

    ---
    type: source
    title: "<the source's own title, in the source's own orthography>"
    url: <the fetched URL>
    publisher: "<the publishing body>"
    published: YYYY-MM-DD
    date_precision: day
    date_source: source
    retrieved: 2026-09-03
    places: [SLE]
    topics: [<the indicator's Topic L2 slug FIRST>, <others if clearly apt>]
    body_completeness: full
    sweep_batch: progress-filler-SLE-2026-09-03
    note: "<quoted scalar, see below>"
    ---

    # <title>

    URL: <the fetched URL>

    <the full verbatim body>

Rules that the lint enforces and that cost a refetch if broken:

- **The key is `places:` — plural, bracketed — never `place:`.** OSINT has flagged the singular
  form arriving from this pipeline; do not emit it.
- **`note:` MUST be a quoted scalar.** An unquoted value containing a colon-space does not
  parse. Always wrap it in double quotes and avoid internal double quotes.
- **The `note:` may say only what its own source says.** OSINT has flagged three failures here
  and every one of them is expensive downstream: (a) a note asserting a **figure that exists in
  no held source** — never carry a statistic you did not read in this document's own body;
  (b) **two drafts concatenated** into one note, the second beginning "ALSO: ..." — one file,
  one finding, one note; (c) a note stating a fact that is **true but belongs to a different
  document** — a claim taken from the publisher's website rather than the page being staged.
  Verify provenance, not just plausibility. The note names the indicator it answers, says
  whether it is the baseline or the movement, and states in one or two sentences what **this
  document** actually says that answers the indicator. State there anything irregular: an
  inferred date, a truncated capture, a paywall. **An empty note is free; an invented figure
  is not.**
- **`URL: <url>` as the second body line is mandatory** — it is what the crossed-body lint reads.
- **Never invent a controlled value.** Do not write `entities:`, `lens:` or `origin_status:`
  unless you have verified the slug against OSINT's `raw/`. Leaving them out is correct.

### Write as you go — this is not optional

**Stage each file the moment its body is fetched, one file per body.** Never hold a list of
bodies in context and write them all out at the end of the slice: that is exactly how bodies
shift one place along the list and every file after the slip carries its neighbour's body, and
the tally still reads clean. Fetch one, write one, move on.

Write files with a shell heredoc using a quoted delimiter so no escaping mangles the body.
Do not re-read the whole file to verify; the heredoc either wrote or errored.

## 6. What you return and what you write

Write **three CSVs**, all under `C:\CORPUS\logs\progress-filler\slices\`, replacing `N` with
your slice number:

1. `SLE-2026-09-03-sliceN.csv` — one row per gap indicator in your slice, header exactly:
   `indicator_id,subject,briefs_run,candidates_returned,fetched,staged_baseline,staged_progress,not_selected,dropped,drop_codes,outcome,subject_rows_at_probe`
   `subject` is the Topic L2 slug. `briefs_run` is 2. `staged_baseline` is 0 or 1,
   `staged_progress` is 0, 1 or 2 — the cap must be auditable from this file alone.
   `not_selected` is a count and is **never** coded as a drop. `drop_codes` is joined with
   a pipe character and codes candidates, not indicators. `outcome` is exactly one of
   `staged` or `nil`. `subject_rows_at_probe` is supplied per indicator in your slice input
   CSV — copy it verbatim.
2. `SLE-2026-09-03-sliceN-selected.csv` — header `indicator_id,file,brief,rank,why`.
   `file` is the path relative to `new-queue\SLE\`, e.g. `baseline/2025-01-01-foo.md`, using
   forward slashes. `brief` is 1 or 2. One row per selection: if one file answers two
   indicators, that is one file and two rows.
3. `SLE-2026-09-03-sliceN-unselected.csv` — header
   `indicator_id,url,title,publisher,published,brief,why_not`. Every fetched candidate the cap
   excluded. `why_not` in a clause, quoted.

Write all three even if empty (header row only). Use Python's `csv` module so every field
containing a comma or a quote is escaped correctly.

**Return to the parent a terse tally only — never bodies, never full text.** Per indicator:
`indicator_id staged_baseline/staged_progress outcome`, plus a two-line summary of the slice
(indicators probed, files staged baseline/progress, nils, any origin adjudications appended,
any fetch failures). Nothing else.

## 7. Judgement notes for Sierra Leone specifically

- The usual primaries: the Ministry of Communication, Technology and Innovation (MoCTI), the
  National Telecommunications Commission (NATCOM), the Directorate of Science, Technology and
  Innovation (DSTI), the National Civil Registration Authority (NCRA), Bank of Sierra Leone,
  Statistics Sierra Leone (Stats SL), the Sierra Leone Gazette, Parliament of Sierra Leone,
  State House, and the National Public Procurement Authority. Prefer them to press accounts.
- Sierra Leone has a dense NGO/donor reporting layer (World Bank, UNDP, UNICEF, GIZ, IFC).
  A donor project document is a legitimate primary **for the project**, and a legitimate
  baseline where the thing itself is the donor programme; it is not a substitute for the
  national instrument when the indicator asks about the instrument.
- Sierra Leone's ledger already holds strong coverage of mobile money and fraud, connectivity
  and cybersecurity. Where a candidate is another account of something already dense there,
  the dedup at step 3 should catch it — but prefer a genuinely new document over a fourth
  telling of a held story.
- Many indicators will genuinely be nil for a low-income country of 8 million. **A nil is a
  finding and is cheaper than a wrong stage.** Do not reach for an ECOWAS, Mano River Union or
  pan-African document as a substitute for a national one; a regional instrument is a baseline
  only where Sierra Leone's own accession, domestication or implementation is what the document
  records.

## 8. This is a RESUMED run — read before you start

The first attempt at this run (2026-09-03 22:55) was cut off by a session limit after its slices
had staged 32 files but before any slice wrote its CSVs. Those 32 files are still on disk under
`new-queue\SLE\`. The parent has read every one of them and reconstructed which indicator each
answers, so:

- **Nine indicators are already complete at the cap (1 baseline + 2 progress).** The parent
  carries their run-CSV and selected rows itself. They are named in your prompt as SKIP. **Do
  not probe them, do not fetch for them, do not write rows for them.**
- **Three indicators are partially staged** (named in your prompt with exactly what is already
  on disk for them). Probe them normally, but **the existing files count against the cap** — an
  indicator holding 1 baseline + 1 progress may stage at most one further progress item, and
  only if it is a genuinely distinct, genuinely stronger event. **The cap is a maximum, not a
  quota**: adding nothing is a correct outcome. In your run CSV, `staged_baseline` and
  `staged_progress` for these indicators count **all** files standing for that indicator at the
  end, the carried ones included, so the cap audits from the file alone. In your selected CSV,
  write a row for a carried file **only if** you are adopting it as your own selection — the
  parent has already written rows for the carried files, so **do not duplicate them**; leave
  carried files out of your selected CSV entirely.
- Every other indicator in your input CSV is untouched and is normal work.

**The 32 carried files are also a dedup surface for the whole slice.** Before you fetch anything,
`grep -rl "<url>" C:\corpus-osint-xfer\new-queue\SLE\` — a URL already staged for another
indicator is never staged twice; if it genuinely answers your indicator too, that is one file
and a second selected row pointing at the existing path.

**The Exa tools are deferred in this session.** Load them before first use with
`ToolSearch` query `select:mcp__exa__agent_run,mcp__exa__web_fetch_exa` — calling them without
loading the schema fails.

**Budget discipline.** The previous attempt died on a session limit. Work steadily, do not
re-probe anything the parent told you to skip, and if a brief returns nothing usable, take the
`nil` and move on rather than reformulating it a third time.
