#!/usr/bin/env python3
"""topic-render.py — BUILD stage 6: the topic reports, lifted from the place reports.

One Level-2 taxonomy slug is a unit; it issues two documents, `{slug}-monthly.md` and
`{slug}-progress.md`, into `outputs/topics/{slug}/`.

**Nothing is authored here** *(Bill, 2026-08-14)*. There is no summary, no cross-place block and
no connecting sentence: a topic document is the place documents' material, sliced by subject and
reordered, and that is the whole of it. The design note is `documentation/topic-reports.md`; this
script is that note, executed.

What each document carries:

  monthly    every `<!-- narrative: {section}--{subject} -->` block a place's monthly holds for
             this subject, verbatim, under a `## {place}` heading. **Every** one, not the first: a
             subject may sit in more than one section of a place's report — the ledger carries a
             per-row `section` and five units override it, putting BEN's `gov.regional` in four
             sections at once — so the blocks are matched on the subject half of the key and
             printed in document order under the one place heading. Matching on the key is also
             what makes the section irrelevant here: no section map is consulted and no key is
             guessed.

  progress   **countries only** — the frame covers them and not the three regions
             (`progress-report-redesign.md` §1), and a region's own progress report is not built
             on the frame at all. Sectioned by **indicator**, not by place: each indicator this
             subject's frame carries gets an `## {indicator}` heading and a `| Country |
             Developments | Progress |` table, one row per country whose own progress report
             carries a Developments cell for it — read off that country's rendered document, the
             same table `render_progress_indicators()` writes, never rebuilt here. An indicator no
             country has evidence for prints no heading, the same lift-only rule the monthly
             follows. *(2026-09-02, replacing the section-keyed movement table the pre-indicator
             country progress report used to carry.)*

**Regions issue no monthly and, since 2026-09-02, sit in no topic progress report either** — their
own progress report is slated to move onto topics rather than the country frame, at which point it
rejoins this one.

Usage:
  python scripts/topic-render.py                 write every slug's documents
  python scripts/topic-render.py --slug dpi.pay  one slug
  python scripts/topic-render.py --check         check G over what is written, write nothing
"""
import argparse
import importlib.util
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import indicators_lib  # noqa: E402
import vault_lib  # noqa: E402

_spec = importlib.util.spec_from_file_location(
    "report_render", os.path.join(os.path.dirname(os.path.abspath(__file__)), "report-render.py"))
rr = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(rr)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = vault_lib.ROOT
REPORTS = os.path.join(ROOT, "outputs", "reports")
TOPICS = os.path.join(ROOT, "outputs", "topics")

MONTHS = ("January", "February", "March", "April", "May", "June",
          "July", "August", "September", "October", "November", "December")

PLACEHOLDER = "_(narrative not yet written)_"


def slug_path(subject):
    """`dpi.pay` -> `dpi-pay`. The dot survives in the vocabulary, where it means something, and
    does not go into a path, where it reads as an extension. The narrative block keys already do
    exactly this substitution, which is why the two agree without a mapping."""
    return subject.replace(".", "-")


def front_matter(text):
    out = {}
    if not text.startswith("---"):
        return out
    for line in text.split("\n---", 2)[0].split("\n")[1:]:
        if ":" in line:
            k, v = line.split(":", 1)
            out[k.strip()] = v.strip()
    return out


def units():
    """(country units, region units) — directory names under outputs/reports/."""
    all_units = sorted(d for d in os.listdir(REPORTS) if os.path.isdir(os.path.join(REPORTS, d)))
    return ([u for u in all_units if not u.startswith("X")],
            [u for u in all_units if u.startswith("X")])


def by_full_name(codes):
    """Places in alphabetical order by **published full name**, not by ISO3.

    The two orders are not the same and the difference is visible: Eswatini sorts under E and
    `SWZ` under S, Côte d'Ivoire's `CIV` before Cape Verde's `CPV` while the names go the other
    way. A reader scanning a topic report is scanning country names, so the names are what it
    sorts on."""
    return sorted(codes, key=lambda c: rr.place_name(c).casefold())


def document(unit, kind):
    p = os.path.join(REPORTS, unit, f"{unit}-{kind}.md")
    return open(p, encoding="utf-8").read() if os.path.exists(p) else ""


def monthly_blocks(text, subject):
    """[(key, body)] — every narrative block in this document for this subject, in document order.

    Matched on the subject half of the key, so a section override changes nothing here: BEN's
    `gov.policy` prose sits under `dpi--gov-policy` and `infrastructure--gov-policy`, and both are
    this subject's. An empty block, or one still carrying the old placeholder, is not carried — it
    would publish a heading with nothing under it, and check L already counts it where it lives."""
    tail = f"--{slug_path(subject)}"
    out = []
    for key, body in rr.MARKER.findall(text):
        if not key.endswith(tail):
            continue
        body = body.strip()
        if not body or body == PLACEHOLDER:
            continue
        out.append((key, body))
    return out


def indicator_cells(text, topic, indicator):
    """(developments, progress) for one (topic, indicator) pair, read off a rendered country
    progress document's own indicator table — or None where that country's report carries no
    developments for it.

    **Read off the document, never rebuilt from `indicators.csv`**, for the same reason the old
    per-place movement table was always lifted rather than recomputed: a table rebuilt here could
    disagree with the one the country publishes, and citations resolve at render time, not here.
    The row is matched on its first two cells, which is exact because `indicator_id` is unique per
    (subject, indicator-text) pair (`indicators_lib.frame()` refuses a duplicate) and this
    function is always called with both cells drawn from the same frame row.

    A ***No evidence*** row — Developments empty — returns `None`: it carries nothing to lift, the
    same rule that has always kept an empty block out of a topic document."""
    m = re.search(r"^\| " + re.escape(topic) + r" \| " + re.escape(indicator) +
                  r" \| (.*) \| (.+?) \|\s*$", text, re.M)
    if not m:
        return None
    developments = m.group(1).strip()
    if not developments:
        return None
    return developments, m.group(2).strip()


def period_of(texts):
    """(period string, spans_one_window). The sources' period, never a window of this stage's own.

    Nothing is aged here: a block is in the topic monthly exactly when it is in the place's
    monthly. Where the place documents do not share one window the range they span is stated,
    rather than asserting a window none of them has."""
    periods = {front_matter(t).get("period", "") for t in texts if t}
    periods.discard("")
    if not periods:
        return "", True
    if len(periods) == 1:
        return periods.pop(), True
    starts, closes = [], []
    for p in periods:
        parts = p.split(" to ")
        starts.append(parts[0])
        closes.append(parts[-1])
    return f"{min(starts)} to {max(closes)}", False


def month_label(period):
    """`2026-07-01 to 2026-08-14` -> `July 2026` — the month a monthly window opens in."""
    m = re.match(r"(\d{4})-(\d{2})", period or "")
    return f"{MONTHS[int(m.group(2)) - 1]} {m.group(1)}" if m else (period or "")


def build_monthly(subject, label, today):
    countries, _ = units()
    texts = {u: document(u, "monthly") for u in countries}
    carried = [(u, monthly_blocks(texts[u], subject)) for u in by_full_name(countries)]
    carried = [(u, b) for u, b in carried if b]
    if not carried:
        return None, []
    period, one_window = period_of([texts[u] for u, _ in carried])
    places = [u for u, _ in carried]
    out = [
        "---",
        f"title: {label} — monthly update, {month_label(period)}",
        f"compiled: {today}",
        f"period: {period}",
        f"subject: {subject}",
        f"places: {'; '.join(places)}",
        rr.PENDING,
        "---",
        "",
        f"# {label}: monthly update, {month_label(period)}",
        "",
        f"*{len(places)} places. Every block below is carried verbatim from that place's own "
        f"monthly update, where it was written, sourced and checked; nothing is written here.*",
    ]
    if not one_window:
        out += ["", "*The place reports do not share one window; the period above is the range "
                    "they span.*"]
    for unit, blocks in carried:
        out += ["", f"## {rr.place_name(unit)}", ""]
        out.append("\n\n".join(body for _, body in blocks))
    out.append("")
    return out, places


def build_progress(subject, label, today):
    """Progress — one table per indicator, columns Country | Developments | Progress.

    **Countries only** *(Bill, 2026-09-02)*. The indicator frame covers the 54 countries
    (`progress-report-redesign.md` §1); the three regions still answer the old per-subject
    movement ledger, which has no indicator to key a table on, and their own progress report is
    slated to move onto topics rather than the country frame. Mixing the two table shapes under
    one heading would misrepresent one of them as the other, so regions are simply absent here
    until their report changes, rather than carried in a shape this document does not use.

    The unit is the **indicator**, not the place: every indicator this subject's frame carries
    gets its own `## {indicator}` heading, holding every country whose own progress report has a
    Developments cell for it. An indicator no country has evidence for prints no heading at all —
    the lift-only rule the monthly has always followed, extended from places to indicators."""
    countries, _ = units()
    order = by_full_name(countries)
    texts = {u: document(u, "progress") for u in order}
    inds = [i for i in indicators_lib.frame() if i["subject"] == subject]
    sections_out, seen_places = [], []
    for ind in inds:
        rows = []
        for u in order:
            cells = indicator_cells(texts[u], ind["topic"], ind["indicator"]) if texts[u] else None
            if cells is None:
                continue
            rows.append((u,) + cells)
            if u not in seen_places:
                seen_places.append(u)
        if rows:
            sections_out.append((ind["indicator"], rows))
    if not sections_out:
        return None, []
    places = by_full_name(seen_places)
    period, one_window = period_of([texts[u] for u in places])
    out = [
        "---",
        f"title: {label} — progress report, {period}",
        f"compiled: {today}",
        f"period: {period}",
        f"subject: {subject}",
        f"places: {'; '.join(places)}",
        rr.PENDING,
        "---",
        "",
        f"# {label}: progress report, {period}",
        "",
        f"*{len(places)} countries. Each row below is carried verbatim from that country's own "
        f"progress report, which answers a fixed frame of indicators over the period; nothing is "
        f"written here. A country not listed under an indicator has ***No evidence*** on it in "
        f"its own report.*",
        "",
        rr.PROGRESS_VOCAB,
    ]
    if not one_window:
        out += ["", "*The place reports do not share one window; the period above is the range "
                    "they span.*"]
    for indicator, rows in sections_out:
        out += ["", f"## {indicator}", "", "| Country | Developments | Progress |", "|---|---|---|"]
        for unit, developments, progress in rows:
            out.append(f"| {rr.place_name(unit)} | {developments} | {progress} |")
    out.append("")
    return out, places


def render(subject, label, today):
    folder = os.path.join(TOPICS, slug_path(subject))
    wrote = 0
    for kind, builder in (("monthly", build_monthly), ("progress", build_progress)):
        out, places = builder(subject, label, today)
        path = os.path.join(folder, f"{slug_path(subject)}-{kind}.md")
        if out is None:
            # A topic document with nothing to carry is not issued. An existing one is left
            # alone rather than deleted: removing a published document is not this script's
            # decision, and the gap is visible in the run's own count.
            print(f"{subject}: no {kind} material in any place — not issued")
            continue
        os.makedirs(folder, exist_ok=True)
        rr.write(path, out, subject, f"{len(places)} places", today=today)
        wrote += 1
    return wrote


def check():
    """Check G — every URL in a topic document resolves through the catalogue.

    Cheap by construction, because a lift can only carry links that already resolved where they
    were written. It is run anyway: cheap and redundant is the right shape for the check that
    catches a link the lift itself mangled."""
    held = set(rr.slug_urls().values())
    held |= {rr.link_target(u) for u in held}
    bad = docs = 0
    for folder in sorted(os.listdir(TOPICS)) if os.path.isdir(TOPICS) else []:
        for fn in sorted(os.listdir(os.path.join(TOPICS, folder))):
            if not fn.endswith(".md"):
                continue
            docs += 1
            text = open(os.path.join(TOPICS, folder, fn), encoding="utf-8").read()
            urls = set(re.findall(r"\]\((https?://[^)\s]+)\)", text))
            miss = [u for u in urls if u not in held]
            for u in miss:
                print(f"     NOT HELD in {fn}: {u}")
            bad += len(miss)
    print(f"check G over {docs} topic document(s): "
          f"{'PASS' if not bad else 'FAIL — ' + str(bad) + ' link(s) not held'}")
    return 1 if bad else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--slug", help="one Level-2 subject, e.g. dpi.pay")
    ap.add_argument("--check", action="store_true", help="check G over outputs/topics/")
    ap.add_argument("--today", default=None)
    a = ap.parse_args()

    if a.check:
        return check()

    today = a.today or __import__("datetime").date.today().isoformat()
    _, label, _ = vault_lib.load_taxonomy()
    subjects = [a.slug] if a.slug else sorted(label)
    unknown = [s for s in subjects if s not in label]
    if unknown:
        print(f"not in the taxonomy: {', '.join(unknown)}", file=sys.stderr)
        return 2
    wrote = 0
    for s in subjects:
        wrote += render(s, label[s], today)
    print(f"\ntopics: {len(subjects)} subject(s), {wrote} document(s) issued -> outputs/topics/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
