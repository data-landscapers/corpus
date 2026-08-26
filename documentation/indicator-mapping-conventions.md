---
type: procedure
title: indicator-mapping-conventions.md — how a ledger row is mapped onto the frame
last_reviewed: 2026-08-26
status: written from the ERI pilot, 2026-08-26. Binds the mapping pass over the remaining country ledgers.
---

# Mapping conventions for the indicator frame

*(`documentation/progress-report-redesign.md` is the decision record and this does not amend it.
What follows is the set of calls the pilot pass over ERI had to make, written down so the other
fifty-three units make them the same way. A convention that lives only in the head of whichever
pass ran first is how fifty-four countries end up answering fifty-four different questions.)*

## The file holds what is mapped and nothing else

`outputs/reports/{unit}/indicators.csv` carries **only the indicators with evidence behind them**.
An indicator absent from the file renders as ***No evidence***, which is what `load_unit()` and
check I both already assume — so ERI's file is thirteen rows, not a hundred and twenty-one with a
hundred and eight blanks. Writing the No evidence rows out explicitly is noise that has to be
maintained, and the frame is the thing that guarantees they print.

## Which indicator a row belongs to

**The indicator is chosen by what the row is, not by the subject the ledger filed it under.** The
ledger's `subject` is a taxonomy position assigned when the row was minted; the frame asks a
different question and the two do not always land together. ASYCUDA World sits on ERI's ledger
under `dpi.exchange`, and it is a customs system: it maps to `dpi.mis--customs`. Following the
subject would have put a customs platform under national data exchange and left the customs
indicator reading No evidence with the evidence sitting one row away.

**One row may map to several indicators, and should where it genuinely answers several.** ERI's
EriTel expansion row carries both a fibre figure and a bandwidth figure, and it is mapped to
`infra.connect--national-fibre-backbone` and `infra.connect--international-internet-bandwidth`
with different prose in each. What it must not do is carry the *same* sentence twice: if the second
indicator has nothing of its own to say, it has no evidence and should be left to say so.

**One indicator may take several rows.** `row_ids` is pipe-separated, like the ledger's own
`sources`. Where the rows point in different directions, that is what *Mixed* is for, and §3 makes
its qualifying clause mandatory.

## Placeholder rows are not evidence

A ledger row whose status is *Not held* **with no source on file** — ERI's `gov.protect-none` and
`dpi.pay-none` are the pattern — is a marker that the base looked and found nothing. It is
**not mapped**. Mapping it would make the indicator ineligible for No evidence under check I's
first rule, and the row would then have to state a position resting on a citation that does not
exist.

A *Not held* row that **does** carry a source is different and **is** mapped: Starlink listing
Eritrea with no planned launch date, or the cable industry's registry showing no landing, are
dated, cited, checkable statements that the thing is absent. They are normally *No change* —
the base held the absence at the start of the window and holds it still — and the citation is
what distinguishes a reported absence from an unexamined one.

## Choosing the value

The vocabulary is §3's and the judgement is the drafter's. Two calls recur:

- **A row published inside the window that restates a standing position is *No change*, not
  *Advanced*.** Starlink's July 2026 map entry is new evidence of an old position. What makes a
  row *Advanced* is that something moved — a system entered service, a stage completed, an
  instrument was made — not that a source was published.
- **A government's own claim is reported as a government claim, in the qualifier.** ERI's fibre
  and bandwidth figures are the minister's, carried by state media, with nothing on the ledger
  testing them: *Advanced, on the ministry's own figures*. The stem records the direction and the
  qualifier records who says so, which is cheaper and clearer than declining to state a direction.

Measures follow §6 — a dated story that a figure moved, cited, with no absolute level asserted as
current state.

## The prose

Two texts per mapped indicator, both cited on the claim, both register-checked
(`report-register-check.py` reads them and the bands are in `report-country-skeleton.md`).

- **`summary`, 8–40 words** — what the table shows. One clause or two, the link on the claim.
- **`developments`, 25–200 words** — behind the expander. Dated events first, each carrying its
  own citation; then what the base does *not* hold on the indicator, which is usually the more
  useful half. A blank line separates one development from the next and becomes a line break in
  the cell.

**Cite by catalogue slug, never by URL.** `cite_prose()` resolves the slug at render time, and
check M refuses a raw URL. This base's slugs are record titles, so most carry spaces and 364 of
them carry a bracketed qualifier — `2025-11-08 Digital 2026 Eritrea (DataReportal)`. Both are
handled; write the slug exactly as the ledger's `sources` field carries it.

## What ZAF added, 2026-08-26

The thick-ledger pass (153 rows, 77 indicators mapped) settled three more calls.

**A first measurement is *No change*, with the clause saying so.** The vocabulary has no value
for a figure the base has never held before — 360,000 uncollected identity documents, an 18th
place in a research ranking. *Advanced* would assert a direction the evidence cannot support and
*No evidence* is false. Write *No change, a first count with no earlier figure behind it*: the
level is stated, the direction is withheld, and the reader can see which is which.

**Mixed is common in a thick ledger and rare in a thin one.** Ten of ZAF's 77 are Mixed and none
of ERI's thirteen. That is the expected shape: Mixed needs two instruments under one indicator
moving opposite ways, which only happens where the base holds several rows per indicator. Do not
reach for it to express uncertainty — an indicator whose single row is ambiguous is a stem plus a
qualifier, not Mixed.

**The unmapped placeholders are not lost — they surface in the gaps section.** The renderer still
prints *Where the record is thin* from the ledger's Not-held rows, so a `-none` row that the
mapping pass declines to map appears there with what would settle it. That is the second half of
the argument for not mapping them: the reader sees the absence twice, once as No evidence in the
frame and once as a probe target, and neither states a position on a citation that does not exist.

**Two mechanical traps, both now fixed in the renderer and both worth knowing while drafting.**
Citations carry the slug verbatim: some slugs hold double spaces and 364 hold parentheses, and
both used to break silently. And check H reads sentence by sentence — a figure in a sentence
whose citation sits in the *previous* sentence fails it. Put the figure inside the cited clause.
