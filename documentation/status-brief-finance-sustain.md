---
type: spec
title: finance.sustain — the status sub-section: what it says, what it reads, what Not established looks like
reader: cc
last_reviewed: 2026-09-25
---

# `finance.sustain` — the status sub-section

*(Cowork, 2026-09-25, on Bill's framing, register R77. The drafting brief for the `### Financial sustainability` sub-section of every country status report, written across the 54 units by R78. `STATUS-INIT.md`'s rules on evidence, writing and verification govern this sub-section as they govern the other 38; nothing here overrides them. Pairs with `indicator-financial-sustainability.md` and the outline entry in `status-outline-part-2.md`. The last section is the mechanics of R78 for both sub-sections.)*

## The question

**Is the digital state paying for itself, and is it moving that way?** The sub-section tracks the move away from dependence on external money, and looks for three kinds of evidence of a government making that move: that it recognises the long-term value of investing in data and digital transformation where it counts — a costed strategy with a budget line behind it; that it is reprioritising its own budget, so the share its treasury carries rises and the lines that keep systems running are its own; and that where it brings in the private sector it does so on terms that last — a stated revenue model, a state obligation that is provided for, cost recovery in law rather than in a press release.

Two neighbours ask adjacent questions. `finance.budget` is the facts of the budget and stays suspended; this sub-section does not lift it. `finance.new` is the money arriving from outside, with its counts and totals; this sub-section never repeats those figures and reads them for one thing — when each commitment's window closes, because a system financed by a five-year credit is a liability from year six unless something is designed to carry it. The taxonomy draws the line as facts against effort (OSINT `lookups/taxonomy.md`, 2026-09-23): a budget document is `finance.budget`; a finance-law article creating a levy is both.

## What the section says

**The first sentence carries the news, and the news is usually the share** — the domestic-state share of the digital lines of the latest read budget document, its direction across the three fiscal years held, and the one thing that explains the movement: a loan-financed programme arriving or ending, a ministry's own line doubling, a levy taking over from a grant. Where the share is an inference because the document prints no financing column, the news is whatever else is best evidenced: a transition plan, a fund created in law, an execution rate.

Then, in whatever order the evidence dictates and never as a checklist walked in order, four things.

**What the state carries.** The share, dated by fiscal year, in the state's own currency, with the prior year where the direction means something and never a longer series. Whether the lines that keep systems in service — maintenance, licences, subscriptions, connectivity — are the state's own or sit inside an external project, where the document's economic classification lets the extract tell. Whether what is voted is spent, on the appropriated basis, where an outturn is held, with the qualifier the extract carries — a rate excluding personnel is a floor and says so.

**What the state has put in law to carry it.** Own-source financing of digital programmes — a universal service levy, a regulator's licence income, a digital fund, a fee schedule for identity or e-services, a revenue-share key in the finance law's articles — named by instrument and article where the extract read one, with its scale where the document prints it. Cost recovery in force, not proposed.

**What the state is doing to get there.** Intent that carries money: a strategy costed and then appropriated, or costed and not, which is itself the finding — Kenya's AI strategy, costed at KSh 152bn and in its second year with no allocation, is the shape. Plans to bring externally built systems onto the recurrent budget, with the date the external window closes and whether a line has appeared. A new domestic line; a domestic line growing while the external side falls.

**Whether the private sector carries any of it on terms that last.** A PPP, concession or revenue-share for a data centre, a cloud, a switch or a service platform, stated with the state's obligation and the revenue model — a take-or-pay lease is the state's obligation; a licence fee to keep using a system the state paid to develop is a liability, not a partnership. A stalled deal is stalled, dated. A memorandum, an investment announcement or a vendor's own investment figure establishes nothing here and is `finance.new`'s.

One continuous narrative, up to 350 words, no sub-headings, bullets or tables, every claim hyperlinked on the claim, every time-varying figure dated, money in the announcing party's currency, no opinion. A thin section is short.

## What evidence it reads

**The budget extract is the figure of record and the first thing read.** `budgets/{ISO3}/{FY}.csv` and `external.csv`, and `python scripts/budget_source.py --share` for the arithmetic — the domestic-state share at the first stage both sides carry, with its flags. The rows carry what the share does not: `econ_class` and `line_name` say which lines are recurrent; `exec_vs_voted`, `actual` and `audited` whether the money moved; `funding_source` whether a line is own-source; `notes` and `doc_locator` where in the finance law an article was read. The document is the citation — its `source_slug` resolves through the catalogue to the URL the sentence links, which is how check A holds. **The share is the report's own arithmetic and goes in its own `<!-- derived -->` paragraph**, dated by fiscal year and naming the stage; the lines it was computed from link to the document, the share itself links nothing. On 2026-09-25 the extract held 10,960 lines across 52 units; ERI and SDN have no folder, and GHA's three years carry no common stage and yield no share.

**The unit's own status report, second.** `finance.new` names the external commitments and their windows — the year each closes is the question this section asks of the budget; `gov.policy` the costed strategies; `dpi.*` the systems built with other people's money and who runs them; `infra.store` the data-centre PPPs. A fact stated there is not restated; it is read for who pays after the grant.

**The catalogue, third**, filtered to the place on `finance.sustain`, `finance.budget`, `finance.new`, `gov.policy` and `dpi.*`, opened in `raw/`. `finance.sustain` carried no source before 2026-09-23 and the back catalogue is not re-tagged, so the slug alone finds nothing: the read is a keyword pass over the place's sources under the other slugs — *levy, fund, own revenue, cost recovery, fee, sustainab-, recurrent, maintenance, licence, subscription, transition, handover, exit strategy, on-budget, counterpart, PPP, concession, revenue share, universal service, take-or-pay*. Bill's published analysis is cited by author as analysis, never as evidence for a figure.

**Check A is set membership, and it binds.** A URL outside the four held bodies of evidence — the catalogue, the DPI source URLs, `all-nonstate.csv`, the IIAG profiles — is not cited, whatever the writer knows about the document. An instrument the section needs and none of them carries is a `gaps.csv` row, and an acquire line if dated 2024 or later; the section states the position at the grain the held evidence supports. **No DPI variable answers this sub-section**: the `govtech-financial-*`, `govtech-treasury-*` and `iiag-pubadmin-*` rows describe the finance machinery, belong to `finance.budget`, and are not cited here.

## What is never said

The share is never labelled. *Aid-dependent*, *self-financing*, *sustainable* are the assessment's words; the status report states the figure, the direction and the mechanism and lets the reader conclude. A 100 % share flagged *origin inferred* is never stated as the state financing everything — it is a document that prints no financing column, and the section says so (below). An MTEF outer year, a plan-period total, a commitment plan and an in-year execution figure are not the section's figures. A PPP announced is not a partnership in force; a vendor's stated investment is not state money. The section never says why a share moved without a source that says it — the extract's `notes` often do, linked through the document they cite; where they do not, the movement is stated and the cause is not.

## What *Not established* looks like

Four cases, each one dated sentence about the country, never about the evidence — not "the base holds", not "no source could be found", not "the budget has not been extracted".

**The budget has not been read.** ERI and SDN today, and any unit whose folder still holds migrated rows: *"No fiscal-year budget for the digital estate had been read as at September 2026."* That is the whole sub-section, two sentences at most, no link, which check B accepts; it is the extraction queue stated as a finding, and it changes the day the year is read.

**The document does not say whose money it is.** Fifteen units' latest shares are *origin inferred* (AGO, BWA, CMR, COG, COM, DJI, DZA, LBR, LBY, LSO, MAR, MUS, SSD, ZAF, ZWE on 2026-09-25) — the estimates print no financing column, so every line reads as domestic by default. The section states the appropriation, dated and linked, then: *"The 2026 estimates print no financing source against their digital lines (FY2026)."* (Not "no source of financing": check G bars "no source".) It does not print the 100 %. Where part of the document does print financing — a development volume or an external-programme annex — say so for that part and confine the sentence to the rest.

**No outturn is held.** Where no `actual` or `audited` stage exists for any digital line: *"No outturn against the digital appropriations had been published as at September 2026."* Where the outturn is in-year only, the section says so and gives no rate.

**No mechanism is in law.** *"No own-source levy, fund or fee financing digital programmes was on the statute book as at September 2026."* Stated only where the extract's enumeration of that document was complete (`budget-extract.md` → *An absence is a finding, and it has to be earned*); where the articles were not read, nothing is said about them.

A sub-section may carry a linked share and one *not established* sentence together; `not_established` in the frontmatter counts only sub-sections that are the sentence alone.

## Writing the two sub-sections across 54 units (R78)

Both briefs run under one pass; this is the only statement of its mechanics, and `status-brief-geopol-sovereignty.md` points here.

**It is an initialisation, not maintenance.** The sub-sections do not exist, so `STATUS-INIT.md`'s rules govern, not `BUILD.md` → *Maintaining the status baseline*: the four held bodies of evidence may be cited; a source found, dated 2024 or later and not held earns one line in `C:\corpus-osint-xfer\africa-acquire.csv` — a contract term or a finance law the sweep has not caught is exactly the sweep brief; a *Not held* position earns a `gaps.csv` row. No ledger is read or written.

**Eighteen units a sitting, three sittings, in ISO3 order, the register line repeated each time.** Per unit: read the two briefs, the unit's status report, its budget folder and the catalogue cut; write the two sub-sections into `outputs/reports/{ISO3}/{ISO3}-status.md` at the outline's position — `finance.sustain` closing Finance, `geopol.sovereignty` closing Geopolitics, each `###` heading carrying its `<!-- slug -->` comment; move `compiled:` to the day, set `sections_written` to 39, recount `sources_cited`, `not_established` and `acquire_lines`. Then `python scripts/status-check.py --unit {ISO3}` A to I clean and `python scripts/report-render.py --unit {ISO3} --check`; a unit whose A, B or G will not pass is reverted to `HEAD` for that file and the commit body names the source it could not cite. Read every opening sentence (`--openings`) before the sitting closes — H needs a reader.

**On the last sitting**: `STATUS-INIT.md`'s *37 sub-sections* and check E's caption in `status-check.py` become 39; one change-log entry, two sentences, dated. No stage line prints under either heading — R80 tests that on one country after R99.
