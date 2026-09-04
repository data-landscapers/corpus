# Progress filler — TGO (Togo) — slice brief, 2026-09-04 (slice 8, recovery slice)

You are one slice of a `PROGRESS-FILLER.md` run over **TGO (Togo)**. The parent owns the merge;
you own your slice's gaps end to end. Read `C:\CORPUS\PROGRESS-FILLER.md` if you need the full
procedure — this file is the operative extract.

**Why this slice exists.** An earlier session of this run probed 73 TGO gaps across seven slices
and staged 152 files, then died on a session limit before two slices' tallies were written. The
parent has reconstructed those tallies from the staged files. Three indicators could not be
resolved that way: they have no attributable staged file, and bookkeeping has no standing to
write a `nil` — a `nil` is a searched absence, a claim about the world. **So these three are
probed properly, by you.** Everything else in the run is settled.

## Hard boundaries

- **Never write anything to `C:\OSINT`.** It is read-only, always. You may READ only its
  `raw/`, `wiki/`, `lookups/` and run its two scripts named below.
- **Do no git operations at all.** No `git add`, no commit, no status in any repo. The parent commits.
- Stage ONLY to `C:\corpus-osint-xfer\new-queue\TGO\baseline\` and
  `C:\corpus-osint-xfer\new-queue\TGO\progress\`. Both already exist and already hold 152 files
  from this same run. Flat, no subfolders.
- Write your own logs ONLY to the three slice files named at the end. Do not touch any other
  file under `C:\CORPUS\logs\`.
- Do not spawn sub-agents.

## Your three gaps

| indicator_id | subject | objective sentence must name | subject_rows_at_probe |
|---|---|---|---|
| `include.access--inclusion-of-refugees-and-idps` | `include.access` | Inclusion — Access to services: Inclusion of refugees and IDPs | 4 |
| `dpi.mis--social-protection` | `dpi.mis` | DPI — Sectoral management information systems: Social protection | 6 |
| `dpi.mis--tax` | `dpi.mis` | DPI — Sectoral management information systems: Tax | 6 |

## The window

Brief 2's window is **2025-09-01 to today (2026-09-04)** — the first day of the current month,
one year back. State that range explicitly in the brief.

## Batch label

`sweep_batch: progress-filler-TGO-2026-09-04`

## 1. Two Exa Agent briefs per gap indicator

For each of your three indicators, run **two** `mcp__exa__agent_run` calls with
`effort: "medium"`. If a call returns "still running", resume it with its `runId` until it
completes — never start a duplicate run for the same brief.

The objective sentence must name the chapter, topic and indicator together as
`{topic_l1} — {topic}: {indicator}`, inside the sentence, not as a trailing context line.

Ask for, per item: URL, title, publisher, date, and one line on why it matters. State the
standing preference for **primary and official sources** (see section 7 for Togo's primaries).

**Togo's official language is French and its national documents are overwhelmingly in French.**
Say so in every brief and ask explicitly for French-language primary sources — an English-only
search returns donor and aggregator material and misses the instrument itself. Search terms worth
naming: *Togo*, *Journal officiel de la République togolaise*, *décret*, *arrêté*, *loi*,
*conseil des ministres*, *ministère*, *stratégie nationale*, *numérique*.

- **Brief 1 — baseline, no date restriction.** Does this thing exist at all in Togo and what is
  its standing state: the instrument, system, institution or published figure itself, its
  founding or enacting act, any dated authoritative statement of its current position.
  **Ask for the single most authoritative document, ranked.**
- **Brief 2 — progress, windowed to 2025-09-01 through 2026-09-04.** Movement in that window.
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
  `date_precision: year` or `month` with `date_source: inferred` (or `proxy` for a retrieval-date
  proxy, said plainly in the note).
- **A body must be the French page's own text where the source is French.** Do not stage a
  machine-translated mirror of a French original; fetch the original.

## 3. Screening and dedup — before you fetch, once per batch of candidates

- **Origin screen**: `python C:\OSINT\scripts\origin-screen.py --domain a.com b.net`
  — one command per batch of candidate domains, before fetching. It makes no writes.
- **Scope**: drop what is not our subject, coded from OSINT `wiki/reference.md` section 7's
  closed table. Every drop goes in your run CSV with its code. Nothing discarded silently.
- **Dedup**: `python C:\OSINT\scripts\raw-url-index.py --check` (read-only) on candidate URLs.
  `DUP-EXACT`/`DUP-SLUG` skip. `REJECTED` drops. `FLAG-SLUG` never skips.
  **Do NOT grep `C:\OSINT\logs\` — it is outside the readable interface.**
- **This matters more for you than for a normal slice: 152 files from this same run are already
  staged under `C:\corpus-osint-xfer\new-queue\TGO\`.** Cross-check **BOTH folders** before
  staging anything — `grep -rl "<url>" C:/corpus-osint-xfer/new-queue/TGO/`. If your selected
  document is already staged there, **do not restage it**: point your selected-CSV row at the
  existing path and say in `why` that the file was already staged by a sibling slice. Top up,
  never restage, never overwrite.
- **New origin adjudications** (a domain you had to rule on that OSINT's list does not carry)
  go to `C:\corpus-osint-xfer\progress-filler-drop-list.csv`, **appended**, header verbatim
  `domain,network,status,rule,added,note,,` — every row at the same **8** fields (two trailing
  empty). `added` is `2026-09-04`, `note` says it was adjudicated during progress-filler TGO
  slice 8. Only append if you genuinely adjudicated; re-read the file before appending, and
  append with a single shell append so you never rewrite the file.

## 4. Selection — the cap

**Hard cap, per indicator: one baseline and two progress items. Three maximum.**

- **The cap is a maximum, never a quota.** Where nothing survives, the indicator is `nil` and
  that is the finding. Padding to three is a failure, not a success. Two of your three
  indicators may well be genuine nils — that is a legitimate and useful answer, and it is the
  answer this slice exists to establish honestly.
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

`new-queue\TGO\baseline\YYYY-MM-DD-slug.md` and `new-queue\TGO\progress\YYYY-MM-DD-slug.md`.

**One document goes in one folder. Baseline wins**: a document selected as anyone's baseline is
staged under `baseline\` even where another indicator took it as progress.

Filename: date prefix **padded, never partial** — year-only precision takes `YYYY-01-01`,
month-only takes `YYYY-MM-01`; `date_precision` carries the truth. Then a short descriptive
slug: lowercase ASCII, hyphens, **no accents in the filename**, naming the country/publisher and
the thing. **Check the name is not already taken** before writing — a silent overwrite of a
sibling's file is the one failure a clean tally hides.

Frontmatter (best-effort per OSINT `wiki/schemas.md` section 4) — the shape is:

    ---
    type: source
    title: "<the source's own title, in the source's own orthography>"
    url: <the fetched URL>
    publisher: "<the publishing body>"
    published: YYYY-MM-DD
    date_precision: day
    date_source: source
    retrieved: 2026-09-04
    places: [TGO]
    topics: [<the indicator's Topic L2 slug FIRST>, <others if clearly apt>]
    body_completeness: full
    sweep_batch: progress-filler-TGO-2026-09-04
    note: "<quoted scalar, see below>"
    ---

    # <title>

    URL: <the fetched URL>

    <the full verbatim body>

Rules that the lint enforces and that cost a refetch if broken:

- **The key is `places:` — plural, bracketed — never `place:`.**
- **The `title:` keeps the source's own orthography, accents and all.** A French title
  de-accented to ASCII over a correct-UTF-8 body is a staging fault the lint catches. Write
  `Décret`, `Ministère`, `protection sociale` — the *filename* is ASCII, the title is not.
- **`note:` MUST be a quoted scalar.** An unquoted value containing a colon-space does not
  parse. Always wrap it in double quotes and avoid internal double quotes.
- **The `note:` may say only what its own source says.** Never carry a statistic you did not
  read in this document's own body; one file, one finding, one note; never state a fact that
  belongs to a different document. Verify provenance, not just plausibility. The note names the
  indicator it answers, says whether it is the baseline or the movement, and states in one or two
  sentences what **this document** actually says that answers the indicator. State there anything
  irregular: an inferred date, a truncated capture, a paywall.
- **`URL: <url>` as the second body line is mandatory** — it is what the crossed-body lint reads.
- **Never invent a controlled value.** Do not write `entities:`, `lens:` or `origin_status:`
  unless you have verified the slug against OSINT's `raw/`. Leaving them out is correct.

### Write as you go — this is not optional

**Stage each file the moment its body is fetched, one file per body.** Never hold a list of
bodies in context and write them all out at the end: that is how bodies shift one place along
the list and every file after the slip carries its neighbour's body, and the tally still reads
clean. Fetch one, write one, move on.

Write files with a shell heredoc using a quoted delimiter so no escaping mangles the body.
Do not re-read the whole file to verify; the heredoc either wrote or errored.

## 6. What you write and what you return

Write **three CSVs**, all under `C:\CORPUS\logs\progress-filler\slices\`:

1. `TGO-2026-09-04-slice8.csv` — one row per gap indicator, header exactly:
   `indicator_id,subject,briefs_run,candidates_returned,fetched,staged_baseline,staged_progress,not_selected,dropped,drop_codes,outcome,subject_rows_at_probe`
   `briefs_run` is 2. `staged_baseline` is 0 or 1, `staged_progress` is 0, 1 or 2 — the cap must
   be auditable from this file alone. Count a selection repointed at an already-staged sibling
   file in these columns too: they count selections, not new writes. `not_selected` is a count
   and is **never** coded as a drop. `drop_codes` is joined with a pipe character and codes
   candidates, not indicators. `outcome` is exactly one of `staged` or `nil`.
   `subject_rows_at_probe` is in the table above — copy it verbatim.
2. `TGO-2026-09-04-slice8-selected.csv` — header `indicator_id,file,brief,rank,why`.
   `file` is the path relative to `new-queue\TGO\`, e.g. `baseline/2025-01-01-foo.md`, forward
   slashes. `brief` is 1 or 2. One row per selection: if one file answers two indicators, that
   is one file and two rows.
3. `TGO-2026-09-04-slice8-unselected.csv` — header
   `indicator_id,url,title,publisher,published,brief,why_not`. Every fetched candidate the cap
   excluded. `why_not` in a clause, quoted.

Write all three even if empty (header row only). Use Python's `csv` module so every field
containing a comma or a quote is escaped correctly.

**Return to the parent a terse tally only — never bodies, never full text.** Per indicator:
`indicator_id staged_baseline/staged_progress outcome`, plus a two-line summary (indicators
probed, files newly staged baseline/progress, selections repointed at existing files, nils, any
origin adjudications appended, any fetch failures). Nothing else.

## 7. Judgement notes for Togo specifically

- The usual primaries: the **Journal officiel de la République togolaise** (`jo.gouv.tg`), the
  **République Togolaise** government portal (`republiquetogolaise.com`, `republicoftogo.com`),
  **service-public.gouv.tg**, the ministries (Action sociale et Promotion de la femme; Santé;
  Économie et Finances; Économie numérique et Transformation digitale; Planification), **ANADEB**
  (Agence nationale d'appui au développement à la base), **ANID**, the **OTR** (Office togolais
  des recettes, `otr.tg`), **INSEED**, **ARCEP Togo**, **CNSS** and **INAM**. Prefer them to
  press accounts. `togofirst.com` is a competent local business outlet and acceptable where no
  primary exists.
- **The donor layer is a legitimate primary for the donor project, and only for that.** World
  Bank, UNHCR, WFP, UNICEF, UNDP, EU and AfDB produce much of the written record. A World Bank
  project document is a proper baseline **where the thing itself is that project**; it is not a
  substitute for the national instrument when the indicator asks about the instrument.
- **On `include.access--inclusion-of-refugees-and-idps`**: Togo hosts a modest refugee population
  (largely Ghanaian, plus a more recent influx of Burkinabè into the Savanes region) and has an
  internal displacement problem in the Savanes driven by Sahel security spillover. The indicator
  asks whether refugees and IDPs are **included in digital public services and data systems** —
  registration, digital ID, social registry inclusion, cash-transfer targeting, biometric
  registration by UNHCR or the state, access to civil documentation — not the humanitarian
  response in general. **CNAR** (Coordination nationale d'assistance aux réfugiés) is the
  national body. Watch the scope line: a UNHCR situation report on food distribution is not this
  indicator; UNHCR or state biometric registration, or inclusion of displaced people in the RSPM
  social registry, is.
- **On `dpi.mis--social-protection` and `dpi.mis--tax`**: the indicator is the **sectoral
  management information system itself** — the operational system a ministry or agency runs to
  manage its sector — not the register and not the payment rail. For social protection that
  means ANADEB's or the ministry's programme MIS, the système d'information for the PNPS, the
  MIS behind the cash-transfer programme (Novissi and its successor arrangements), and CNSS and
  INAM information systems where they are the sector's management system. For tax it means the
  OTR's core operational systems — **SIGTAS**, the OTR e-services stack, **SYDONIA/ASYCUDA** on
  the customs side, the système d'information of the Commissariat des impôts. A sibling slice has
  already staged material on the RSPM social registry, on the AMU/INAM information system and on
  OTR platforms; check what is staged before you buy, and where an already-staged document is the
  right answer, repoint rather than restage.
- Togo's held ledger for these subjects is thin (4 rows under `include.access`, 6 under
  `dpi.mis`), so the dedup against OSINT's index will rarely fire and the quality judgement at
  step 4 does the work.

**The Exa tools are deferred in this session.** Load them before first use with
`ToolSearch` query `select:mcp__exa__agent_run,mcp__exa__web_fetch_exa` — calling them without
loading the schema fails.

**Budget discipline.** Work steadily. If a brief returns nothing usable, take the `nil` and move
on rather than reformulating it a third time.
