#!/usr/bin/env python3
"""topic-render.py — BUILD stage 6: the topic reports, lifted from the place reports.

One Level-2 taxonomy slug is a unit; it issues two documents, `{slug}-monthly.md` and
`{slug}-progress.md`, into `outputs/topics/{slug}/`. Sections are **places**, in alphabetical
order by published full name, carrying that place's own prose for that subject.

**Nothing is authored here** *(Bill, 2026-08-14)*. There is no summary, no cross-place block and
no connecting sentence: a topic document is the place documents' material, sliced by subject and
reordered by place, and that is the whole of it. The design note is
`documentation/topic-reports.md`; this script is that note, executed.

What each document carries:

  monthly    every `<!-- narrative: {section}--{subject} -->` block a place's monthly holds for
             this subject, verbatim. **Every** one, not the first: a subject may sit in more than
             one section of a place's report — the ledger carries a per-row `section` and five
             units override it, putting BEN's `gov.regional` in four sections at once — so the
             blocks are matched on the subject half of the key and printed in document order under
             the one place heading. Matching on the key is also what makes the section irrelevant
             here: no section map is consulted and no key is guessed.

  progress   the subject's movement table from each place's progress report, and no prose. Not by
             the same argument as the monthly: a progress report keys its narrative by *section*
             only — `<!-- narrative: infrastructure -->` covers cyber, satellite broadband and
             data centres together — so there is no per-subject block in any of the 57 documents
             to lift, and lifting the section block would carry four other subjects into a
             single-subject document. The table is that document's substance in any case.

**The three regions appear in the progress report only**, because they issue no monthly.

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


def movement_table(text, label):
    """The lines under `### {label}` in a progress report, up to the next heading or block.

    Read off the rendered document rather than rebuilt from the ledger, because the point of this
    stage is that it lifts: a table rebuilt here could differ from the one the place publishes,
    and then two documents would state the same movement differently."""
    out = []
    for m in re.finditer(r"^### " + re.escape(label) + r"\s*$", text, re.M):
        chunk = text[m.end():]
        stop = re.search(r"^(#{2,3} |<!-- narrative)", chunk, re.M)
        chunk = chunk[:stop.start()] if stop else chunk
        rows = [ln for ln in chunk.strip().split("\n") if ln.strip()]
        if rows and rows[0].lstrip().startswith("|"):
            out.append("\n".join(rows))
    return out


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
    countries, regions = units()
    order = by_full_name(countries) + by_full_name(regions)
    texts = {u: document(u, "progress") for u in order}
    carried = [(u, movement_table(texts[u], label)) for u in order]
    carried = [(u, t) for u, t in carried if t]
    if not carried:
        return None, []
    period, one_window = period_of([texts[u] for u, _ in carried])
    places = [u for u, _ in carried]
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
        f"*{len(places)} places. Every table below is carried verbatim from that place's own "
        f"progress report; nothing is written here.*",
        "",
        rr.MOVE_VOCAB,
    ]
    if not one_window:
        out += ["", "*The place reports do not share one window; the period above is the range "
                    "they span.*"]
    for unit, tables in carried:
        out += ["", f"## {rr.place_name(unit)}", ""]
        out.append("\n\n".join(tables))
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
