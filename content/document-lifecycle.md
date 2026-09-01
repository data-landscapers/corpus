Building a site of this nature has involved a lot more than a simple request to a large language model. This page sets out to explain the complexities involved by tracing the journey of a single document through the system.

On the evening of 29 August 2026, a Somali news site reported that the Upper House of Somalia's Federal Parliament had given a cybersecurity bill its first reading.

The next day it was a linked claim in three Corpus documents: a line in Somalia's monthly update, a row in its progress report, and an entry in that day's bulletin. This is what happened in between.

## Systematic discovery

Nothing arrives in Corpus without a search. The looking is done by a **sweep cycle** working one day of a rotation at a time. Some sweeps run every time: a fixed list of trade journals, and a search of the open web for the last 36 hours. The rest take turns — newspapers, academic journals and think tanks on one day; financiers and donors' own structured reporting on another; deep per-country and regional research on a third. (Budgets, expenditure and audits will be a fourth.)

The list sweeps work a **window**: what this domain published since the last run, with a day of overlap so a story indexed late is caught next time. The content sweeps ask what has appeared since they last ran, however long ago. Two kinds of empty result are expected and neither is chased: search indexes lag a day or two, and most publishers do not publish at weekends.

## Two-tier searching

Searching and fetching go through [Exa](https://exa.ai/), in two modes, depending on whether the target is a *place to look* or a *thing to find out*. (The donor-finance sweep is the exception: it reads IATI's datastore through its API.)

**Standard search**, where the target is known — a query scoped to one domain, bounded by the run's dates, in that source's own language, with a separate fetch call to retrieve the page. Its virtue is hard scope: such a query *cannot* return anything from off the list, which makes the list a boundary rather than a preference.

**Agent mode**, where the target is a topic — no query string but a written brief, from which the Agent composes and follows its own searches. This is what the open-web sweep runs on, and the per-country, regional and financier briefs. It finds what a query would not, because it can follow a lead. The Somalia report came in that way: Dawan Africa is on no list.

A brief cannot be fenced, so two rules are absolute. **Nothing the Agent writes is ever stored** — its output is a synthesis, exactly the second-hand material the base refuses, so its job ends at discovery. **And its dates are not evidence**: every publication date is re-established from the fetched page.

## Screening and storing

Before anything is fetched, the candidate's **origin** is screened — where it came from, not what it says. A domain that fabricates, rewrites without attribution or launders others' reporting under its own byline is on a drop list and is never collected. It has to be a separate test: a hostile origin produces items fluent and specific enough to publish straight onto a page.

What is fetched is the document's **own words, in full** — never an excerpt, a summary or a machine translation. That stored text is what makes every downstream claim checkable, and it is why the store is private. A sweep can only stage a candidate: it cannot write to the archive or touch a wiki page.

## Adjudicate

**Ingest** is the one door, and it runs once at the end of the cycle. Four dispositions: admitted to the archive; turned into a **contradiction brief**, because it disagrees with something held; turned into an **acquisition line**, because the real document is the gazette it mentions rather than the story about it; or deleted. Leaving the queue is not the same as being admitted. Budget documents take a fifth route, to structured extraction.

Duplicates are refused in three tiers, cheapest first: an exact URL match against everything held, a narrow comparison against sources of similar date and place, then — on the small residue only — a judgement about whether this is genuinely a new event. Sources that *disagree* about one event are never duplicates.

Admission also produces the document's **one sentence**: a bolded claim about a dated development in a place, written once, on the source, with the full text in hand. Everything downstream assembles it; nothing rewrites it.

The Somalia report was admitted on 30 August. It was also a contradiction.

## Resolving contradictions

Corpus held a January 2026 record that Somalia's parliament had approved a Cybersecurity Law, and its pages said so. A bill at first reading in August cannot easily be squared with that.

Ingest does not settle it: it files the conflict and writes a brief — the claim, each competing value, who asserts each, which sources are held. The pass that spots a conflict is reading one document; the pass that settles it has to go and find evidence. The **reconcile pass** did that on the same run and found two primaries: the regulator's own statement of the January vote, and the Senate's published account of its legislative procedure. January was passage by the lower house alone; a bill becomes law in Somalia only after Upper House readings, presidential signature and gazette publication.

So the January record was not wrong — Corpus had been reading it as more than it said. The pages carry the corrected position, dated, and the gap stated: no gazette record is held either way. A contradiction gets one attempt, and where research cannot settle it, what is not established is written onto the page it bears on. Nothing is parked.

## Classification

Classification happens at admission, with the document's full text in hand, and it lives in the document's own metadata. Three facets are classified:

- **Place** — ISO-3 country codes and eight region codes, from one list. They form a tree: country, sub-region, Africa, global.
- **Topic** — one or more slugs from a hierarchical taxonomy of ten categories and about thirty-six topics.
- **Entity** — three to six actors named in the document are tagged.

A value outside a vocabulary is rejected rather than accepted and noted. That refusal is the whole basis on which any count on the site means anything.

Two decisions are where this usually goes wrong. **Multi-tagging, not a polyhierarchy**: rather than give a topic two parents, the tree stays single-parent and the *document* carries both slugs, so "everything in Governance" is still a clean roll-up. **Blocs are entities, not places**, because place is geographic — and a region code is earned by the development, not by the cast list.

## Storing metadata

An archive of classified documents is still not something anyone can read. The wiki is the compiled layer that makes it one — three kinds of page over the same evidence:

- **62 place hubs**, one per country and region: a compiled *Recent developments* section, with the standing account of the place written around it.
- **38 topic pages**, one per Level-2 topic: not a list of what happened, but the argument — what is true of the topic once it is lifted off the country it came from.
- **599 intersections**, a place crossed with a topic, where there is sufficient material to require a page of its own.

62 places against 38 topics allows more than two thousand intersections; 599 exist. That is the design, not a backlog: the wiki is built to depth on demand, so a thin country page reflects what is being asked of the base rather than how quiet that country is.

All three are compiled from the sources rather than written into, so running a compile twice changes nothing.

## Classification is the product

Facets are not description; they are the join. Everything Corpus publishes is a query over those three values, which is why the same evidence appears five ways without being written five times.

The Somalia report carried five: place `SOM`; topics `gov.legislate` then `infra.cybersec`; the cybersecurity law and the Senate as entities. Everything that followed came from those five, none of it decided document by document. It reached Somalia's hub, both topic pages, and `somalia--gov-protect`, the intersection holding that country's legal stack. Its ledger row takes its chapter in the report — *Governance* — from `gov.legislate`'s parent. The bulletin filed it under *Legislation and regulation* and cross-referenced it from *Cybersecurity*, because the first slug is the primary topic. The progress-report row it answers is Somalia × legislation and regulation × cybersecurity legislation. And the catalogue lets a reader filter to exactly that intersection.

A **lint pass** runs alongside. Most of its thirty-odd checks fix rather than report — a missing field, a drifted slug, a wrong date prefix, a dead link — and everything is in version control, so a wrong fix is a revert. Where a check cannot have one correct action, it reports rather than guesses. The cycle closes with a commit and a copy of the repository to the machine that publishes.

## From storage to publication

The publishing side reads the evidence and not the working, and cannot write into the collection repository at all: anything it needs to send back goes to a shared folder outside both, carried across by hand. The site is a derived view of the base, and a derived view that writes to its source stops being derivable.

The build rebuilds what is mechanical — the catalogue, the finance dataset, the vocabularies, a names index — then asks the question that needs judgement. For each country it lists the sources **not yet considered** (a set difference, not a date window, so an interrupted run resumes where it stopped) and reads each against that country's **ledger**: one row per named system or instrument, with a status, the event that fixed it, and the sources that establish it. The test for a row is whether a reader could name the thing and whether its position could be different next quarter.

Most sources move nothing, and that is the point of a record layer: a report on systems is not an audit of news stories. The Somalia report moved one row — *Cybersecurity Law* — from a position reading as enacted to `In development, passed by the lower house and at first reading in the upper`. A row that moves is then mapped into the **indicator frame**, a fixed list of 121 questions asked of every country, so a progress report is shaped in advance rather than by whichever records accumulated; an indicator with nothing behind it reads *No evidence*, a finding rather than a blank.

## Different outputs for different needs

The monthly update and the progress report are two slices of the same ledger, which is why they cannot disagree: the monthly renders the rows that moved in the last month, the progress report compares each indicator at the two ends of a thirteen-month window. A month in which nothing moved still issues a monthly that says so. The **status report** answers *where is this now*: for most countries it is authored from sources the base will never hold, and revised in place rather than rebuilt — the price of its being able to state things the archive does not.

The **bulletin** has no ledger and selects on a two-day window of *publication* — what the world published, not what Corpus fetched — so an empty window still produces a bulletin saying so, and why. An absent bulletin and a build that did not run are otherwise the same thing.

## Final checks and publications

Five checks run over each unit before anything is typeset: every link resolves through the catalogue, every status word is from the controlled list, no document is stamped before its ledger moved, every stated position cites a source that resolves, and no narrative section was left unwritten. The first four are mechanical; the fifth is authoring. A position that cannot be sourced becomes ***Not held*** with a line in the gap file — a finished outcome, not a blocked one.

**A published file is never revised.** An edition is cut when the content changes, not when a build runs, and two editions in a day take a `-2` suffix — the first is never renamed, because a citation may already rest on it.

The Somalia material is in `SOM-monthly-2026-08-30.pdf`, `SOM-progress-2026-08-30.pdf` and `corpus-bulletin-2026-08-30-3.pdf`, each linking the claim to Dawan Africa's own page. Elapsed, from the source's publication to Corpus's: a little over a day.
