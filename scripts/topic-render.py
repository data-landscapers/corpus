#!/usr/bin/env python3
"""topic-render.py — BUILD stage 6: the topic reports, lifted from the place reports.

One Level-2 taxonomy slug is a unit; it issues one document, `{slug}-monthly.md`, into
`outputs/topics/{slug}/`. The topic progress report retired on 2026-10-17 (Bill).

**Nothing is authored here** *(Bill, 2026-08-14)*. There is no summary, no cross-place block and
no connecting sentence: a topic document is the place documents' material, sliced by subject and
reordered, and that is the whole of it. The design note is `documentation/topic-reports.md`; this
script is that note, executed.

What the document carries:

  monthly    every `### {topic}` block of story cards a place's monthly holds for this subject,
             verbatim, under a `## {place}` heading. **Every** one, not the first: a subject may
             sit in more than one section of a place's report — the ledger carries a per-row
             `section` and five units override it — so the blocks are matched on the topic
             heading and printed in document order under the one place heading. No section map
             is consulted.

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
import taxonomy_lib  # noqa: E402
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


HEADING = re.compile(r"^(#{2,3}) (.+)$", re.M)
CARD = re.compile(r'<div class="bulletin-item" markdown="1">\n\n(.+?)\n\n.*?</div>\n', re.S)
XREF = re.compile(r'<div class="bulletin-item bulletin-item--xref" markdown="1">\n\n(.+?)\n\n'
                  r'Summarised under .*?</div>\n', re.S)
EMPTY_STORY = re.compile(r'<div class="monthly-story" markdown="1">\n\n'
                         r'<p class="monthly-story__name">[^<]*</p>\s*</div>\n')


def monthly_blocks(text, subject):
    """[body] — every `### {topic}` block this place's monthly holds, in document order.

    **Lifted by heading, not by marker** *(2026-10-20)*. The place monthly carried a
    `<!-- narrative: section--subject -->` block per subject until 2026-10-16, when it became story
    cards under `### {topic}` headings and this matched nothing, so no topic report was issued.
    A subject may still sit in more than one section of a place's report, so every block under its
    heading is taken. A card summarised under another topic of the same report is a link to an
    anchor this page does not have, so the full card it points to stands in for it, once."""
    label = taxonomy_lib.label(subject)
    home = {m.group(1): m.group(0) for m in CARD.finditer(text)}
    parts = HEADING.split(text)
    out, seen = [], set()
    # `split` with two groups gives [lead, hashes, title, body, hashes, title, body, ...].
    for i in range(1, len(parts) - 2, 3):
        if parts[i] != "###" or parts[i + 1].strip() != label:
            continue

        def card(m):
            head = m.group(1)
            if head in seen:
                return ""
            seen.add(head)
            return home.get(head, "") if m.re is XREF else m.group(0)
        body = CARD.sub(card, XREF.sub(card, parts[i + 2]))
        body = EMPTY_STORY.sub("", body).strip()
        if body:
            out.append(body)
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


def span_label(period, short=False):
    """`2025-09-01 to 2026-09-08` -> `September 2025 – September 2026`; a window inside one month
    gives that month alone.

    **The same label the place reports carry** *(Bill, 2026-09-09)*. This was `month_label`, which
    printed the month a window *opened* in and nothing else: a topic monthly covering the same
    2026-08-01 to 2026-09-08 window as the country monthlies it is lifted from was headed "August
    2026" where every one of them said "August – September 2026", and the topic progress report
    was headed with the raw ISO period, "2025-09-01 to 2026-09-08", because it had no label
    function at all. `rr.month_span` is the country reports' own, so the two cannot now disagree.
    """
    parts = (period or "").split(" to ")
    try:
        return rr.month_span(parts[0], parts[-1], short=short)
    except (ValueError, IndexError):
        return period or ""


def build_monthly(subject, label, today):
    countries, _ = units()
    texts = {u: document(u, "monthly") for u in countries}
    carried = [(u, monthly_blocks(texts[u], subject)) for u in by_full_name(countries)]
    carried = [(u, b) for u, b in carried if b]
    if not carried:
        return None, []
    period, _ = period_of([texts[u] for u, _ in carried])
    places = [u for u, _ in carried]
    out = [
        "---",
        f"title: {label} — News, {span_label(period)}",
        f"compiled: {today}",
        f"period: {period}",
        f"subject: {subject}",
        f"places: {'; '.join(places)}",
        rr.PENDING,
        "---",
        "",
        # The place monthly's title and nothing else *(Bill, 2026-10-20)*: the kicker above it
        # names the topic, and the places bar below it replaces the standfirst that counted them.
        f"# News, {span_label(period, short=True)}",
        "",
    ]
    out += rr.jump_bar([rr.place_name(u) for u in places], "monthly-subnav topic-places",
                       "Places in this report")[:-1]
    for unit, blocks in carried:
        out += ["", f"## {rr.place_name(unit)}", ""]
        out.append("\n\n".join(blocks))
    out.append("")
    return out, places



def render(subject, label, today):
    folder = os.path.join(TOPICS, slug_path(subject))
    wrote = 0
    for kind, builder in (("monthly", build_monthly),):
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
    catches a link the lift itself mangled.

    **The held set is the one `report-render.check_links()` uses, and it has to be** *(2026-09-08)*.
    It was `slug_urls()` alone, which is the publisher addresses and not the catalogue entries a
    record with a documented absence of a URL resolves to (`slug_offline()`). Those entries had
    never reached a topic document before; the first that did failed here while passing in the
    place document it was lifted from, which is the one thing this check's own docstring says
    cannot happen. A check that fails on a link its own renderer produced correctly is worse than
    no check, because the next real failure is read as this one."""
    held = set(rr.slug_urls().values()) | set(rr.slug_offline().values())
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
