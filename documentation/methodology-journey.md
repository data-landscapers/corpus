---
type: draft
title: The life of a document — draft for the methodology section
last_reviewed: 2026-08-31
status: draft; placement undecided
---

# The life of a document — draft

*(Working draft, written to Bill's commission of 2026-08-31 — `prep/workflow.md` → Next → "methodology: trace history of 1 document from search to output." Not yet placed. Two options were left open: append it to `content/methodology.md`, where `scripts/methodology.py` already renders it and no renderer changes — or give it `content/methodology-journey.md` and its own URL at `/methodology/journey/`, which costs a render entry and is a feature under the freeze. Nothing below assumes either.)*

*(The worked example is real and every hop was checked in the tree on 2026-08-31; the verification note at the end says how. Three things want a decision before publication — see* Before this is published *at the foot.)*

---

## The narrative

### One document

On the evening of 29 August 2026, a Somali news site published a short report that the Upper House of Somalia's Federal Parliament had given a cybersecurity bill its first reading.

The next day it was a linked claim in three published documents: a line in Somalia's monthly update, a row in Somalia's progress report, and an entry in that day's bulletin. This is what happened in between, and what each process in the chain was for.

### It is found, not received

Nothing arrives at Corpus. Every document is looked for.

The looking is done by a **sweep cycle** that works one day of a rotation at a time. Some sweeps run every time — a fixed list of trade journals, and a search of the open web beyond it. The rest take turns: national newspapers, academic journals and think tanks on one day; financiers and donors' own structured reporting on another; deep per-country research on a third; regions and regional institutions on a fourth. The Somalia report was caught by the **off-list sweep**, the half of the run that searches the open web rather than a list, because Dawan Africa is on no standing list.

Two kinds of sweep ask two different questions. The list sweeps work a **window** — what did this domain publish between the last run and now, with a day of deliberate overlap so a story indexed late is caught next time rather than lost. The content sweeps ask instead what has appeared since they last ran, however long ago that was. Two kinds of empty result are expected and neither is chased: search indexes lag a day or two, and most publishers do not publish at weekends.

Before anything is fetched, the candidate's **origin** is screened — not what it says, but where it came from. A domain that fabricates, rewrites without attribution, or launders someone else's reporting under its own byline is on a drop list and is never collected, however plausible the individual story looks. This is a separate test from whether the story is any good, because a hostile origin produces items that are fluent, correctly dated, on-topic and specific enough to publish straight onto a page. It cannot be caught by reading them.

What is fetched is the document's **own words, in full**. Not a search-result excerpt, not a summary, not a machine translation. Where a page yields only part of itself the capture is flagged as partial rather than quietly patched, and a fuller capture of the same story later displaces it. The stored text is what makes every downstream claim checkable; it is also why the store is private.

At this point the item is a *candidate*. It is written to a staging folder and nothing else has happened to it. A sweep can only stage: it cannot write to the archive and it cannot touch a wiki page. There is exactly one door into the base, and a sweep is not it.

### It is admitted, or it is not

**Ingest** is that door, and it runs once at the end of the cycle over everything the sweeps caught.

Every item gets one of four dispositions. It is admitted to the archive; or it is turned into a **contradiction brief** because it disagrees with something already held; or it is turned into an **acquisition line** because the real document is the gazette it mentions rather than the story about it; or it is deleted. An item can produce a brief or a line *and* be deleted — leaving the queue is not the same as being admitted. Budget documents take a fifth route to a separate extraction pass, since a 300-page appropriation act is not a news item.

Duplicates are refused in three tiers, cheapest first: an exact URL match against the index of everything already held, then a narrow comparison against sources of similar date and place, then — and only then, on the small residue — a judgement about whether this is genuinely a new event. Sources that *disagree* about the same event are never treated as duplicates; that is the contradiction route.

Admission also produces the document's **one sentence**: a bolded claim about a dated development in a place, with the specifics after it. This sentence is written once, on the source itself, with the full text in hand. Everything downstream assembles it; nothing rewrites it. A source that earns no such sentence is still held in full — it simply makes no claim on a country page, and the refusal is recorded with its reason rather than left blank. Historical material brought in to build a baseline is handled in a separate lane and earns no sentence by rule: an old document arriving late is a baseline, not news.

The Somalia report was admitted on 30 August. It was also a contradiction.

### The disagreement, and what settled it

Corpus already held a January 2026 record that Somalia's parliament had approved a Cybersecurity Law, and its pages said so. A bill at first reading in August cannot easily be squared with a law approved in January.

Ingest does not settle this. It files the conflict, marks the affected pages, and writes a brief stating the claim, each competing value, who asserts each, and which sources are actually held. The separation matters: the pass that spots a conflict is reading one document, and the pass that settles it needs to go and find evidence.

The **reconcile pass** did that on the same run. It went looking for primaries and found two: the regulator's own contemporaneous statement of the January vote, and the Senate of Somalia's own published account of its legislative procedure. Both were fetched, stored in full and admitted as sources in their own right — research notes are never kept, only documents. Read together they settled it: January was passage by the lower house alone, and a bill becomes law in Somalia only after Upper House readings, presidential signature and gazette publication.

So the correction was not that the January record was wrong, but that Corpus had been reading it as more than it said. The pages now carry the corrected position, dated, with the January reading annotated rather than deleted — and with an explicit statement of what is still not established: no gazette record is held either way.

A contradiction gets one attempt. Where research cannot settle it, the finding is written onto the page it bears on — dated, and honest about what is not known — and the brief is closed. Nothing is parked. The acquisition queue works the same way: one automated attempt at each named document, including asking the Internet Archive before concluding that a site published nothing, and then either the document is held, or — where it bears on a particular page — its absence is stated there with the date it was searched for.

### It becomes part of what the base says

An archive of documents is not yet a thing that can be read. Three compilers turn it into one.

The **hub compiler** rebuilds each country's *Recent developments* from the one-sentence claims on the sources themselves — it is a derived view, rewritten between markers, and running it twice changes nothing. The **subject pages** are updated by a separate pass that opens each page once for a whole run's catch rather than once per item, because writing per item produces accretion where a batch produces synthesis. The **financing sections** are recomputed the same way whenever a finance record is admitted.

Alongside all of this a **lint pass** runs. Most of its thirty-odd checks fix rather than report: filling a missing field, correcting a slug to its controlled value, renaming a file whose date prefix is wrong, rewiring a dead link, finding the real document URL behind a bare domain. Everything is in version control, so a wrong automatic fix is a revert. Where a check cannot have one correct action — a genuine conflict between sources, an item stranded in the queue, a vocabulary value nobody has ruled on — it reports instead of guessing. A separate retention pass ages out the worklists, so no queue survives by being forgotten.

The cycle closes with a commit, an account of the run, and a copy of the whole repository to the machine that publishes.

### The second machine reads it

The publishing side reads the evidence and not the working: the archive, the vocabularies, the compiled wiki, and the account each closed cycle writes of itself. It cannot write into the collection repository at all. Where something there needs changing — a corrected path, a document worth chasing, a note for the queues — it is written to a shared folder outside both repositories and carried across by hand. The site is a derived view of the base, and a derived view that writes to its source stops being derivable.

The build first rebuilds what is purely mechanical: the **catalogue** of every record held, the **finance dataset**, the vocabulary snapshot, and a names index. Then it asks the question that needs judgement.

For each country the build lists the sources it has **not yet considered** — a set difference, not a date window, so an interrupted run resumes exactly where it stopped — and reads each one against that country's **ledger**. The ledger is the record layer: one row per named system or instrument, each with a status, the event that fixed it, and the sources that establish it. The test for a row is whether a reader could name the thing and whether its position could be different next quarter. *The National Radio Frequency Plan 2026* is a row; *cybersecurity of state information systems* is not.

Most sources move nothing. That is the normal outcome, and it is the point of having a record layer at all: a report on systems is not an audit of news stories. The Somalia report moved one row — *Cybersecurity Law* — from a position that read as enacted to `In development, passed by the lower house and at first reading in the upper`, with the movement `Advanced`, the milestone *First reading in the Upper House, 29 August 2026*, and three sources behind it: the news report, the regulator's January statement, and the Senate's own procedure.

A row that moves is then mapped into the **indicator frame** — a fixed list of 121 questions asked of every country, so that what appears in a progress report is decided in advance rather than by whichever records happened to accumulate. An indicator with nothing behind it reads *No evidence*, which is a finding rather than a blank.

The same source is also asked one further question: does it change what the **status baseline** can say? A status report answers *where is this now* and carries no period. For most countries it has been written out in full from sources the base will never hold — a 1990 law, a founding statute — and from that point it is revised in place rather than rebuilt, because a rebuild from the ledger would destroy an authored baseline while reporting a successful build. For the remainder it is still rendered from the ledger like the other two documents.

### Three documents, one record layer

The monthly update and the progress report are two slices of the same ledger, which is why they cannot disagree.

The **monthly update** renders the rows whose newest record falls in the last month and a bit. The **progress report** compares each indicator's position at the two ends of a thirteen-month window. A month in which nothing moved still issues a monthly, and the monthly says so — an absence of movement is a finding, not an empty box.

The status report sits outside that guarantee wherever it has been authored, which is the price of its being able to state things the archive does not hold. Keeping it in step with the ledger is a judgement made source by source, not something a script can assert.

The **bulletin** is a different kind of document again, and deliberately so. It has no ledger, nothing derives from it, and it selects on a two-day window of *publication* — what the world published, not what Corpus happened to fetch. So a batch of genuinely new-to-us older material goes unreported there, and an empty window still produces a bulletin that says the window was empty and why. An absent bulletin and a build that did not run are otherwise the same thing.

The Somalia item's three-sentence bulletin summary was written once, stored, and never rewritten. It appeared in the third edition cut on 30 August, under *Legislation and regulation*, with a Somalia box beside it and a cross-reference from *Cybersecurity* — an item carrying several subjects is summarised in the first of them and pointed at from the rest, so the same text is never published twice in two wordings.

### It is checked, then published

Before anything is typeset, five checks run over each unit: every link resolves through the catalogue; every status and movement word is from the controlled list; no document claims to be compiled before its ledger moved; every stated position cites a source that resolves; and no narrative section was left unwritten. The first four are mechanical and each has one repair. The fifth is authoring: a section with nothing to say is either given the sentence explaining why, or removed. Where a position cannot be sourced at all, the answer is ***Not held*** with a line in the gap file — a finished outcome, not a blocked one.

Then the site is rendered: every report to HTML and to a dated PDF, the country and topic pages, the catalogue, the finance tables.

**A published file is never revised.** A new edition is cut when the content changes, not when a build runs — the renderer digests each document's body, reads back the digest from the page it wrote last time, and leaves an unchanged document alone. Two editions on one day take a `-2` suffix, and the first is never renamed, because a citation already rests on it. Every PDF carries the date it was cut and the address of the current edition, so an old file says what it is. The one document that behaves differently is the bulletin, whose *page* is refreshed even when its edition is held — freshness is itself news there, and *we looked and nothing was published* is a claim worth making. The dated PDF is still never rewritten.

The Somalia material is in `SOM-monthly-2026-08-30.pdf`, in `SOM-progress-2026-08-30.pdf`, and in `corpus-bulletin-2026-08-30-3.pdf` — three citable files, cut that day, each linking the claim to Dawan Africa's own page.

Elapsed, from the source's publication to Corpus's: a little over a day.

### Nobody is asleep at the wheel

None of this is scheduled. Both cycles are started by hand, in a session someone is sitting in front of. Nothing polls a clock, nothing fires overnight on its own, and a quiet stretch on the site means nobody ran a cycle rather than that the world went quiet. What *is* automatic is what happens once a cycle is running: it does not stop to ask questions, it records what it decided, and everything it did is reversible.

---

## The table

| Task | Process | Process functionality |
|---|---|---|
| **Decide what this cycle looks for** | `SWEEP-CYCLE.md` | Orchestrates a collection run, started by hand — there is no scheduled trigger. Runs one test search first and abandons the run if the search service is down, rather than recording a false empty result. Selects the least-recently-run day from a rotation, passes that day's sweeps their collection window, runs them, then ingest, then the checks, committing at each boundary. Holds a hard budget on how much work one run may spawn. |
| **Sweep the standing list of trade journals** | `SWEEP-DAILY-LIST.md` | Works a fixed list of domains for what each published since the last run, with a 24-hour overlap so a late-indexed story is caught next time. Three instruments in union, not in sequence: the publisher's own feed where it has one, its listing page, and a date-bounded domain-scoped search. Takes every date from the article body, never from a listing or a page header. Keeps its own high-water mark rather than being handed a window. |
| **Sweep the open web** | `SWEEP-DAILY-OFFLIST.md` | Everything *not* on that list, on two thematic tracks, using a deep research agent rather than a domain-scoped search — one track Africa-scoped, one worldwide for material that bears on Africa. This is the sweep that finds publishers Corpus does not yet know about, and it shares the other's staging machinery but not its searching. |
| **Sweep newspapers, journals and think tanks** | `SWEEP-NEWSPAPERS.md`, `SWEEP-JOURNALS.md`, `SWEEP-THINKTANKS.md` | Content-scoped rather than time-scoped: each works its own list and picks up whatever has appeared since it last ran, however long ago that was. |
| **Sweep the money** | `SWEEP-FINANCIERS.md`, `SWEEP-IATI.md` | The first walks a list of financiers, looking at commitments, plans, reviews and critique from the funder's side rather than the recipient's. The second polls the IATI datastore — donors' own structured reporting, with amounts and dates attached, and the only instrument for a commitment nobody wrote about. |
| **Research a country or region in depth** | `SWEEP-COUNTRY-DEEP.md`, `SWEEP-REGIONAL.md` | Four standing research briefs per country — non-state finance, governance, data exchange, demand and political economy — for the institutional depth the news sweeps pass over. The regional sweep runs two loops: regional institutions (their programmes, relationships, financing and the critique of them), and the regions themselves (policy coordination, legal harmonisation, shared infrastructure). |
| **Refuse a bad origin before fetching it** | `wiki/origin-screen.md` | Screens *where* an item came from against an adjudicated drop list, matched on the registrable domain. Called twice — once by the sweep, to stop the fetch, and again at ingest, to catch anything that arrived another way. A single sighting of a hostile pattern puts a domain on watch; a second adjudicates it. A hosting or CDN domain is never treated as an origin. |
| **Store the document's own words** | `wiki/capture-rule.md` | Requires the full verbatim body at fetch time, never an excerpt, summary or machine translation. A truncated capture is flagged and kept, not retried; the flag is what later lets a fuller capture of the same story replace it. |
| **Fill today's half of the bulletin window** | `SWEEP-BULLETIN.md` | A late-morning top-up, also hand-started. The overnight cycle supplies yesterday and nothing of today; this sweeps today only, ingests what it finds and copies across, so the two-day bulletin window is actually covered at both ends. |
| **Admit, reject or route each candidate** | `INGEST.md` (Phase A) | The only door into the archive. One of four dispositions per item: admitted; turned into a contradiction brief; turned into an acquisition line; or deleted. Out-of-scope material is rejected and deleted rather than parked — there is no holding folder. Where an item announces a gazette, plan or strategy, the *document* is the source and the announcement is secondary. |
| **Handle a budget document** | `INGEST.md` fifth route, `BUDGET-EXTRACT.md` | Estimates volumes, appropriation acts and budget annexes go to a separate staging tree with a manifest row, for structured extraction rather than summary. A budget figure is recorded at its stage — proposed, appropriated, released, executed, audited — and stages are never conflated. |
| **Refuse a duplicate without re-reading the corpus** | `INGEST.md` step 2, OSINT's `scripts/raw-url-index.py` | Three tiers, cheapest first: exact URL against an index of everything held; then sources of similar date, place or actor; then a single judgement on the residue, on titles and ledes only. Sources that *disagree* about one event are never duplicates. |
| **Test a financing claim before it becomes a number** | `wiki/finance-record-spec.md` | The five-fact test: a named financier; an identified recipient country or region; an amount that is a commitment or a disbursement (never an "up to", a target or a valuation); the date of the commitment itself; and a purpose specific enough to classify. Failing any one, the item is kept as context and excluded from every total. A re-announcement merges into the original record only on a definite match; anything less certain stands as its own source and is left out of the aggregate. |
| **Write the document's one sentence** | `INGEST.md` step 4a | Authors the single claim the document earns — a bolded statement of what happened, then the dated specifics — written once, on the source, with the full text in hand. Where several outlets carry one event, one source carries the sentence and names the others. No sentence, no bullet; a refusal is recorded with its reason. |
| **Classify it** | `INGEST.md` steps 3–4 | Assigns place codes from the country list, subjects from the two-level taxonomy, and three to six entities — the actors in the development, not every name mentioned. Officeholders are not tagged where the institution is the story. |
| **File it and record the disposition** | `INGEST.md` step 11 | Moves the item to the dated archive, appends what each affected subject page is owed, and writes the URL's outcome to the log at the moment of disposition — for all four dispositions, never batched to the end of the run. |
| **Bring in historical material without treating it as news** | `INGEST.md` backfill lane, `BACKFILL.md` | A separate lane for baseline material staged deliberately: mechanical de-duplication only, and no claim sentence, because an older document arriving late is a baseline and not a development. Everything else about admission is unchanged. |
| **Rebuild each country's recent developments** | `HUB-COMPILE.md` | Gathers every source for a place that carries a claim sentence, sorts by publication date and rewrites a delimited block on the hub. Aggregates only: it ingests nothing and researches nothing, and running it twice changes nothing. Dated absences, and bullets predating the July 2026 cut-over to compiled hubs, sit outside the markers and are never overwritten. |
| **Write the subject pages** | `WIKI-SYNC.md` (Phase B) | Drains the queue of owed writes *grouped by page*, opening each page once for a whole run's catch. Idempotent by construction — it checks whether the source is already cited before writing — so an interrupted run repairs rather than duplicates. |
| **Recompute the financing sections** | `FINANCE-COMPILE.md` | The same treatment for money: hub financing sections are recomputed from the records held, never written by hand. Fires automatically from any ingest that admitted a finance record. |
| **Settle a disagreement between sources** | `RECONCILE.md` | Takes every open contradiction brief, researches it externally for the *primary* — the gazette, the regulator's bulletin, the filing, the court record — ingests what it finds as ordinary sources, and applies the resolution to every affected page, dated. Research notes are never filed; only documents are. One attempt: where it cannot be settled, what is not established is written onto the page and the brief is closed. A third value settles nothing and is recorded as a live conflict rather than picked between. |
| **Chase a document the base wants and lacks** | `ACQUIRE.md` | Drains the acquisition queue, one automated attempt each, including asking the Internet Archive before concluding that a site published nothing. Success is ingested through the normal door. Failure deletes the line: where the document bears on a particular page, its absence is stated there and dated; where it bears on none, the drop is simply logged. Nothing is carried forward as a standing chore. |
| **Keep the base honest** | `LINT.md` | Around thirty checks, the incremental ones over each run's new records and the whole-corpus ones at the close. Most have one correct action and lint takes it: fill a missing field, correct a slug to its controlled value, rename a file whose date prefix is wrong, rewire a dead link, recover a real document URL behind a bare domain, re-date a stale figure or write the absence. It does not produce a to-do list. Where a check cannot have one correct action — a genuine conflict, a stranded queue item, an unruled vocabulary value — it reports rather than guesses. |
| **Age out the worklists** | `PRUNE.md` | One place for every retention rule: which registers, logs and manifests are cleared, after how long, and by which pass. Closed work is deleted rather than kept as an archive — version control holds it — and anything that ages without a named owner is itself reported. |
| **Keep going until the queues are empty** | `UPDATE-WIKI.md` | The loop used when collection is run on demand rather than as a full cycle: ingest → page writes → reconcile → acquire, repeated, because each can refill another's queue. Capped at three passes, and it stops when the only thing left is what the loop itself generated. Any single item named three times in one run is disposed of at the third. |
| **Hand the run over** | `SWEEP-CYCLE.md` close | Writes a manifest naming the commit, the collection window and the counts the run measured, then copies the whole repository to a read-only mirror the publishing side reads. |
| **Notice a cycle has closed** | `scripts/osint-cycle-ready.py`, `CYCLE.md` | Detects a closed collection cycle with no build since, and runs the build and the render as one job. Every close earns a build; a hold file suspends it while someone is working, and a skipped close is covered whole by the next one, because the build works off a set difference rather than a date. |
| **Check the evidence before building on it** | `scripts/lint-osint-freshness.py`, `scripts/lint-interface.py`, `scripts/lint-scope.py` | Reports how old this copy of the evidence is, and catches one that has gone backwards. Enforces — and shrinks — what the publishing side is allowed to read of the collection side. Sorts every catalogue record for geographic remit and names what it cannot account for, rather than deleting it; applying the remit rule belongs to the collection side. |
| **Rebuild the datasets** | `scripts/rebuild.py --all` | The purely mechanical compiles: the catalogue of every record held, the non-state finance dataset, the budget tables, the vocabulary snapshot and the names index. Pure functions of the evidence — they just run. |
| **Decide whether a document moves a position** | `BUILD.md` stage 4, `documentation/report-layer.md` | Lists the sources a country's ledger has not yet considered — a set difference over identifiers, so an interrupted run resumes cleanly — and reads each against the ledger. Four outcomes: a row moves, a row is minted, a *Not held* row is settled, or nothing moves. Most sources report activity rather than movement, and nothing moves; that is the normal case. |
| **Map it into the fixed frame of questions** | `lookups/indicators.csv` (the frame), `outputs/reports/{unit}/indicators.csv` (the country's answers) | 121 indicators asked of every country, so a progress report is shaped by the frame and not by whichever records accumulated. An indicator the country's file does not answer is rendered *No evidence*. A ledger row that moves without being mapped would leave the progress report stating a position the base no longer holds. |
| **Ask whether the standing account changed** | `BUILD.md` → *Maintaining the status baseline*, `STATUS-INIT.md` | The status report is the baseline all news is read against, and for most countries it has been authored from sources the base will never hold. Once authored it is revised in place and never re-rendered from the ledger — a rebuild would destroy it while reporting success. Where borderline evidence conflicts, the section stands: an error in the baseline is invisible and propagates, a gap is visible and gets filled. |
| **Re-render every report from its ledger** | `scripts/rebuild.py --reports all` | Rebuilds each report's tables from the ledger and carries the written narrative across. Idempotent: a report that agrees with its ledger prints `unchanged` and is not touched. |
| **Roll country reports into subject reports** | `scripts/topic-render.py` | Two documents for each Level-2 subject, whose sections are the countries, carrying each country's material for that subject. Nothing is authored here; the ordering — countries first, subjects after — is what keeps them from going stale. |
| **Write the bulletin** | `BUILD.md` stage 7, `scripts/bulletin.py` | Selects the two-day publication window, asks only for summaries not already written, and stores each one so an item is summarised once and worded once. Refuses to assemble a document with an item that has no summary. An empty window still produces a bulletin that says so. |
| **Check before typesetting** | `scripts/report-render.py --check`, `report-register-check.py`, `status-check.py` | Every link resolves through the catalogue; every status and movement word is from the controlled list; no document is stamped before its ledger moved; every stated position cites a source that resolves; and no section was left unwritten. The first four are mechanical repairs made in the same pass; the last is authoring work. An unsourceable position becomes ***Not held*** with a line in the gap file. |
| **Typeset, and mint an edition only if something changed** | `RENDER.md`, `scripts/render.py` | One template for the web page and the PDF. Digests each document's body and compares it with the digest stamped into the page it wrote last time; an unchanged document keeps its edition and is not re-cut. A second edition in one day takes a `-2` suffix and the first is never renamed, because a citation may already rest on it. The bulletin alone refreshes its page under a held edition. |
| **Publish the pages** | `scripts/home.py`, `country.py`, `topic-page.py`, `catalogue.py`, `finance.py` | The home page and its country and subject matrices, each country's page and finance table, the searchable catalogue of every record held, and the all-Africa finance landing. Counts on every page are drawn from the same catalogue, so they cannot disagree. |
| **Retire editions nobody took** | `scripts/prune-editions.py` | Deletes a superseded edition only where nothing ever downloaded it, and never the current one, nothing under a week old, and nothing published before the rule came in. Bulletins keep a week regardless. Any uncertainty resolves towards keeping the file. |
| **Deploy** | `RENDER.md` step 7 | Commits and pushes; the hosting workflow serves what was committed. The render *is* the build — nothing is compiled at deploy time and nothing is generated when a reader asks for a page. Running the render is the instruction to publish, so there is no separate approval step. |
| **Probe a measured gap** | `PROGRESS-FILLER.md` | Takes the indicators a country's progress report reads *No evidence* on and searches specifically for them. What it finds is staged to a shared folder for the collection side, and enters the base only if it is carried across by hand and then admitted through the normal door. Nothing it finds reaches a report directly. A gap searched and found empty is not re-bought until the underlying evidence moves. |
| **Top up the bulletin at midday** | `BULLETIN-TOPUP.md` | Re-runs the bulletin stage alone against the morning sweep's catch, republishing the catalogue and the counts alongside it so no page states a figure another page contradicts. Deliberately does not trigger a full build. |
| **Send something back the other way** | The exchange folder, `notes-for-osint.md`, `africa-acquire.csv` | The publishing side cannot write into the collection repository. Where something there needs changing, or a document is worth chasing, it is written as a numbered note or a queue row in a folder outside both repositories, and a person carries it across. Nothing on either side polls the other. |

---

## Before this is published

**1. The elapsed time.** The narrative says "a little over a day". That is true of this document and is not a promise — a source whose country report is not otherwise moving, or one published just after a bulletin window closed, takes longer. Either qualify the sentence or drop it; it should not read as a service level.

**2. A worked example ages.** Somalia's cybersecurity bill will get its second reading, and when it does the ledger row moves and this page's example describes a position the site no longer states. The page should either date its example explicitly ("as the base stood at the end of August 2026") or be reviewed whenever the row moves. Dating it is cheaper and is what the rest of the site does.

**3. How much of the status report's position to say out loud.** The draft says plainly that the authored status report sits outside the guarantee the other two documents have. That is honest and it is also the page admitting a weak point. The alternative — describing only the ledger and letting a reader assume all three are slices of it — would be a claim the tree does not support. Recommended as written; flagged because it is a judgement about what the site says of itself, not a fact.

## Verification note

Every hop was checked in the tree on 2026-08-31, not inferred:

- **Source**: `raw/2026/2026-08-29-somalia-senate-cybersecurity-bill-first-reading.md` — published 2026-08-29, retrieved 2026-08-30, `sweep_batch: off-list-2026-08-30`, `body_completeness: full`, ingested 2026-08-30.
- **Contradiction and reconcile**: the source's own `date_note`, and the dated annotation on the January bullet in `wiki/places/SOM.md`. The two primaries reconcile fetched — the regulator's January statement and the Senate's published procedure — both carry `ingested: 2026-08-30`, which is what shows they were found by that pass rather than already held.
- **Compiled**: cited on `wiki/places/SOM.md` (inside the compiled markers), `wiki/intersections/somalia--gov-protect.md`, and the `gov.legislate` and `infra.cybersec` concept pages.
- **Catalogue**: one row in `outputs/catalogue/raw-catalogue.csv`; id 12520 in `outputs/catalogue/doc-ids.csv`.
- **Ledger**: row `SOM-gov.legislate-cybersecurity-law`, movement `Advanced`, three sources with this slug first.
- **Frame**: indicator `gov.legislate--cybersecurity-legislation` in `outputs/reports/SOM/indicators.csv`, against the 121-row frame in `lookups/indicators.csv`.
- **Published**: `SOM-monthly.md` line 26, `SOM-progress.md` line 37, and the bulletin summary in `outputs/bulletins/summaries.json` (written 2026-08-30). The bulletin entry was verified by extracting the text of `site/bulletin/corpus-bulletin-2026-08-30-3.pdf` — the third edition cut that day, under *Legislation and regulation*; the two earlier editions of 30 August predate the ingest.
- **Files a reader can take**: `site/reports/SOM/SOM-monthly-2026-08-30.pdf`, `SOM-progress-2026-08-30.pdf`, `site/bulletin/corpus-bulletin-2026-08-30-3.pdf`, all linked from `site/countries/SOM/index.html`.

### Two things the trace turned up that are not about this page

**`SOM-status.md` carries the framing reconcile corrected.** It was compiled 2026-08-30, the same build, and its legislation sections still read that "Parliament approved the Cybersecurity Law on 26 January 2026". This is the predicted failure mode of the design rather than a stray: the baseline is revised only where a source triggers the question, check J skips the status report on an authored unit, and `--doc all` excludes it — so nothing mechanical would have caught it. A report-layer matter, noted here and not acted on.

**`STATUS-INIT.md` states that all 54 countries are through initialisation.** 40 of the 54 status reports carry `built_by: STATUS-INIT`; the other 14 do not, and are still rendered from their ledgers. One of the two is wrong, and which one decides whether this page can say "the status report is authored" without qualification. It is qualified above on the evidence of the tree.
