#!/usr/bin/env python3
"""status-reorder.py — put an existing STATUS-INIT baseline into the taxonomy's order.

    python scripts/status-reorder.py            every initialised country
    python scripts/status-reorder.py ZAF NGA    named ones
    python scripts/status-reorder.py --check    report what would move, write nothing

`status-assemble.py` writes a baseline in `status_lib.outline()` order, and on 2026-08-25 that
order became `lookups/taxonomy.csv`'s rather than `documentation/status-outline.md`'s — so a
report opens on Governance where it used to open on ICT Infrastructure, and its Level-1 chapters
now match the monthly and progress reports beside it (Bill: *"re-order as per lookups\\taxonomy
.csv"*). Forty baselines were already on disk in the old order, and re-assembling them is not
available: the chapter drafts under `prep/scope/{ISO3}/draft/` are cleared once a country is
initialised, and for most of these countries they are long gone.

**So this moves the sections a baseline already holds and writes nothing else.** It is a
permutation, not a render: every sub-section's prose, its heading text and its `<!-- slug -->`
marker cross over exactly as they are, the frontmatter is untouched, and a file already in order
is left alone rather than rewritten. That is what makes it safe to run over documents nobody is
in a position to regenerate — the worst case is a diff that moves blocks around, and git holds
the before.

It refuses a file it does not fully understand rather than writing a partial one. A baseline
carrying a sub-section the outline does not name, or prose sitting outside any sub-section, is
reported and skipped: the first is a vocabulary question and the second is content this cannot
place, and dropping either silently is the one failure mode a reorder must not have.
"""

import argparse
import glob
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import status_lib as S  # noqa: E402

# `### Heading` / `<!-- slug -->` / prose, up to the next heading of either level. The slug is
# the key, exactly as in `status-assemble.py`: a writer who retitled a heading has not moved the
# section, and matching on the title would lose it.
SECTION = re.compile(
    r"^###[ \t]+(.+?)[ \t]*\n<!--\s*([a-z]+\.[a-z]+)\s*-->[ \t]*\n(.*?)(?=^##[ \t]|^###[ \t]|\Z)",
    re.M | re.S)


def split(text):
    """(frontmatter, {slug: (label, prose)}, leftovers) for a baseline document."""
    fm, body = "", text
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end >= 0:
            cut = text.find("\n", end + 1) + 1
            fm, body = text[:cut], text[cut:]
    found, spans = {}, []
    for m in SECTION.finditer(body):
        label, slug, prose = m.group(1).strip(), m.group(2), m.group(3)
        found[slug] = (label, prose.strip())
        spans.append((m.start(), m.end()))
    # Anything outside a sub-section that is not a chapter heading or blank. Chapter headings are
    # rebuilt from the outline, so they are expected leftovers; prose is not.
    leftover, at = [], 0
    for a, b in spans + [(len(body), len(body))]:
        chunk = body[at:a]
        at = b
        for line in chunk.splitlines():
            if line.strip() and not re.match(r"^##[ \t]", line):
                leftover.append(line.strip())
    return fm, found, leftover


def rebuild(found):
    """The document body, in outline order, from the sections the file already holds."""
    out, chapter = [], None
    for c, slug, label in S.outline():
        if slug not in found:
            continue
        if c != chapter:
            chapter = c
            out.append(f"## {chapter}\n")
        drafted, prose = found[slug]
        out.append(f"### {drafted or label}\n<!-- {slug} -->\n\n{prose}\n")
    return "\n".join(out).rstrip() + "\n"


def one(path, check):
    iso = os.path.basename(path).split("-")[0]
    text = open(path, encoding="utf-8").read()
    if "built_by: STATUS-INIT" not in text[:400]:
        return 0, f"{iso}: not a STATUS-INIT baseline — left alone"
    fm, found, leftover = split(text)
    if not found:
        return 1, f"{iso}: no `<!-- slug -->` sub-sections found — refusing to touch it"
    known = {slug for _c, slug, _l in S.outline()}
    spare = sorted(set(found) - known)
    if spare:
        return 1, (f"{iso}: carries {', '.join(spare)}, which the outline does not name — "
                   f"skipped. Settle the vocabulary first; a reorder must not decide it.")
    if leftover:
        return 1, (f"{iso}: {len(leftover)} line(s) sit outside any sub-section, the first being "
                   f"{leftover[0][:60]!r} — skipped rather than dropped.")
    new = fm + rebuild(found)
    if new == text:
        return 0, f"{iso}: already in taxonomy order"
    if check:
        return 0, f"{iso}: {len(found)} sections WOULD move"
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(new)
    return 0, f"{iso}: reordered, {len(found)} sections"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("iso3", nargs="*")
    ap.add_argument("--check", action="store_true", help="report, write nothing")
    args = ap.parse_args()
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass
    paths = ([os.path.join(S.REPORTS, i.upper(), f"{i.upper()}-status.md") for i in args.iso3]
             or sorted(glob.glob(os.path.join(S.REPORTS, "*", "*-status.md"))))
    rc = 0
    for p in paths:
        if not os.path.exists(p):
            print(f"! no such file: {p}")
            rc = 1
            continue
        bad, line = one(p, args.check)
        rc |= bad
        print(("! " if bad else "  ") + line)
    return rc


if __name__ == "__main__":
    sys.exit(main())
