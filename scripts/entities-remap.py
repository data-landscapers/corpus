#!/usr/bin/env python3
r"""entities-remap.py — one entity, one slug: rewrite the losing variants in `entities:`.

Housekeeping job 105, strategic review 4 register R43. The Nigerian Communications
Commission is tagged under four different slugs, so a grep for the regulator finds most of
its record and misses the rest **silently** — and the miss reads as thin coverage rather
than as a tagging fault. `CLAUDE.md` -> *Entities* retired entity pages precisely because a
tag is a terminal state and `raw/` is greppable; a fragmented slug is what breaks that.

**The canonical slug is OSINT's ruling, so it is an argument and not a constant.** The map
file names the variants and proposes a canonical; `--canonical` overrides the proposal
without editing anything. **A ruling either way is one flag, not a re-cut.**

**The file is handled as bytes and exactly one line changes.** Split on line endings, the
one `entities:` line rebuilt, rejoined — so CRLF, a BOM, a missing trailing newline,
quoting and key order are untouched and no YAML loader ever sees a record. Every rewrite is
reconstructed and compared against the original before it is written, and **the comparison
is of every line except the one**: a run that changed a second line would be a bug that a
diff of 561 files is a poor place to discover.

**It refuses rather than guesses.** The vault writes `entities:` in the canonical flow form
`[[a], [b]]` (`reference.md` §1) on one line, and all 147 files in this job's scope do. A
block list, a bare scalar, a value spanning lines, a doubled key, an `entities:` line
outside the frontmatter — each is reported and skipped, never interpreted.

**Selecting and refusing are different jobs, and the selector is the blunt one.** `scan()`
picks a file by tokenising its `entities:` value, not by looking for `[slug]`; `rewrite()`
alone decides whether the form is one it understands. They were once the same test, and a
carrier written in the plain flow form `entities: [afdb, x]` was therefore dropped before
the refusal path could name it — not refused, missed, which is the one outcome a report
cannot show (`notes-for-corpus` 37, 2026-09-20).

**The expected file list is an input, not an output.** Given `--expect`, a path the tree
carries and the list does not means something has started writing the variant again since
the list was cut; a path the list carries and the tree does not means the record moved.
Both are reported and both stop a `--write`, because either one means the measurement the
ruling was made on has moved.

Usage:
  python entities-remap.py --map ncc-slugs.csv                       # dry run
  python entities-remap.py --map ncc-slugs.csv --expect ncc-files.txt
  python entities-remap.py --map ncc-slugs.csv --canonical nigerian-communications-commission
  python entities-remap.py --map ncc-slugs.csv --write

Exit: 0 nothing to do or a clean dry run, 1 a refusal or drift, 2 the map or the tree is
not where the script was pointed.
"""
from __future__ import annotations

import argparse
import csv
import os
import re
import sys

KEY = "entities"
# The canonical form, and the only one this rewrites: one line, an outer flow list whose
# items are each bracketed. `reference.md` §1.
LINE_RE = re.compile(r"^entities:[ \t]*\[(.*)\][ \t]*$")
ITEM_RE = re.compile(r"\[\s*([^\[\]]+?)\s*\]")
# What `scan()` selects on, and deliberately not `ITEM_RE`. Any run of characters that is
# not list punctuation, so a slug is found whatever form the value is written in.
TOKEN_RE = re.compile(r"[^\[\],\s'\"]+")
TREES = ("raw", "wiki")

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def read_map(path, canonical=None):
    """[(variant, canonical)], from a CSV of `slug,records,proposed_canonical`.

    `--canonical` replaces the proposal for every row. It has to name one of the slugs in
    the file: remapping an entity onto a slug nothing in the group uses would invent a tag
    rather than settle one, and that is a different decision from the one being ruled.
    """
    with open(path, encoding="utf-8-sig", newline="") as fh:
        rows = [r for r in csv.DictReader(fh) if (r.get("slug") or "").strip()]
    if not rows:
        raise SystemExit("no slugs in %s" % path)
    slugs = [r["slug"].strip() for r in rows]
    if canonical and canonical not in slugs:
        raise SystemExit("--canonical %s is not one of the group's slugs: %s"
                         % (canonical, ", ".join(slugs)))
    target = canonical or rows[0].get("proposed_canonical", "").strip() or slugs[0]
    return [(s, target) for s in slugs], target


BOM = "﻿"


def frontmatter_span(lines):
    """(first, last) line indices of the frontmatter body, or None.

    The `entities:` line is only ever the frontmatter's; a line in a body that happens to
    start with the key is prose, and rewriting it would edit someone else's words.

    **A byte-order mark is stripped for the comparison and never for the file.** No
    Markdown in the vault carries one today, but a fence that reads `\\ufeff---` would
    otherwise fail this test, and a file that fails it is not refused — it is dropped by
    `scan()` before anything looks at it, which is a silent miss rather than a report.
    """
    if not lines or lines[0].lstrip(BOM).rstrip("\r") != "---":
        return None
    for i in range(1, len(lines)):
        if lines[i].rstrip("\r") in ("---", "..."):
            return 1, i
    return None


def rewrite(text, mapping):
    """(new_text, changed, refusal). One line touched, or a stated reason for none."""
    lines = text.split("\n")
    span = frontmatter_span(lines)
    if span is None:
        return text, False, "no frontmatter"
    first, last = span
    hits = [i for i in range(first, last)
            if lines[i].rstrip("\r").startswith(KEY + ":")]
    if not hits:
        return text, False, "no entities key"
    if len(hits) > 1:
        return text, False, "entities key appears %d times" % len(hits)
    i = hits[0]
    line = lines[i]
    eol = "\r" if line.endswith("\r") else ""
    m = LINE_RE.match(line.rstrip("\r"))
    if not m:
        return text, False, "entities value is not the one-line flow form"
    inner = m.group(1)
    items = ITEM_RE.findall(inner)
    # Every character between the items has to be list punctuation. If anything else is in
    # there — a bare unbracketed slug, a comment, a quote — the line is not what this
    # understands, and rewriting what is left would drop the part it could not read.
    if ITEM_RE.sub("", inner).strip(" ,\t"):
        return text, False, "entities value carries something other than [slug] items"
    out, seen = [], set()
    for item in items:
        slug = mapping.get(item, item)
        if slug not in seen:
            seen.add(slug)
            out.append(slug)
    rebuilt = "%s: [%s]%s" % (KEY, ", ".join("[%s]" % s for s in out), eol)
    if rebuilt == line:
        return text, False, None
    lines[i] = rebuilt
    return "\n".join(lines), True, None


def read_text(path):
    return open(path, "rb").read().decode("utf-8", "replace")


def entities_value(text):
    """The frontmatter's `entities:` value, continuation lines included, or None.

    The value, not the line: a block list keeps its slugs on the lines *after* the key, and
    a selector that reads only the key line cannot see them. Continuation is anything
    indented or starting a list item; a key at column 0 ends it.
    """
    lines = text.split("\n")
    span = frontmatter_span(lines)
    if span is None:
        return None
    first, last = span
    for i in range(first, last):
        line = lines[i].rstrip("\r")
        if not line.startswith(KEY + ":"):
            continue
        out = [line.split(":", 1)[1]]
        for j in range(i + 1, last):
            s = lines[j].rstrip("\r")
            if s.strip() and s[0] in " \t-":
                out.append(s)
                continue
            break
        return "\n".join(out)
    return None


def mentions(value, wanted):
    """True if an `entities:` value names one of `wanted`, in whatever form it is written.

    **This is the selector and it is blunter than `rewrite()` on purpose.** Selecting with
    `ITEM_RE` — or with an `"[%s]" % slug` substring test over the file — hands `rewrite()`
    only the files already in the canonical form, so the refusal path, which is the whole
    report, is never reached: a carrier written `entities: [afdb, x]` is not refused, it is
    *missed*. Tokenising means such a file is selected and then refused by name.
    """
    return any(t in wanted for t in TOKEN_RE.findall(value))


def scan(root, mapping, trees=TREES):
    """Every file under the trees whose `entities:` value names one of the variants."""
    wanted = set(mapping)
    out = []
    for tree in trees:
        base = os.path.join(root, tree)
        if not os.path.isdir(base):
            continue
        for dirpath, _, filenames in os.walk(base):
            for fn in filenames:
                if not fn.lower().endswith(".md"):
                    continue
                path = os.path.join(dirpath, fn)
                value = entities_value(read_text(path))
                if value is None or not mentions(value, wanted):
                    continue
                out.append(os.path.relpath(path, root).replace(os.sep, "/"))
    return sorted(out)


def verify(before, after, path):
    """Every line but one is untouched, and the one that moved is the entities line.

    Cheap, and it is the check that would have caught a rewrite that consumed a stray
    bracket somewhere else in the frontmatter.
    """
    a, b = before.split("\n"), after.split("\n")
    if len(a) != len(b):
        return "%s: line count changed" % path
    moved = [i for i in range(len(a)) if a[i] != b[i]]
    if len(moved) != 1:
        return "%s: %d lines changed, expected 1" % (path, len(moved))
    if not b[moved[0]].startswith(KEY + ":"):
        return "%s: the changed line is not the entities line" % path
    return None


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=".", help="the repository root (default: cwd)")
    ap.add_argument("--map", required=True, help="the group's slugs, as CSV")
    ap.add_argument("--canonical", default=None,
                    help="override the map's proposal (must be one of the group's slugs)")
    ap.add_argument("--expect", default=None,
                    help="a file list to assert the tree against before writing")
    ap.add_argument("--trees", default=",".join(TREES),
                    help="trees to walk (default: raw,wiki)")
    ap.add_argument("--write", action="store_true", help="write the files")
    args = ap.parse_args(argv)

    root = os.path.abspath(args.root)
    pairs, target = read_map(args.map, args.canonical)
    mapping = {a: b for a, b in pairs if a != b}
    trees = tuple(t for t in args.trees.split(",") if t)
    if not any(os.path.isdir(os.path.join(root, t)) for t in trees):
        print("none of %s under %s" % (", ".join(trees), root), file=sys.stderr)
        return 2

    print("canonical: %s" % target)
    print("rewriting: %s\n" % (", ".join(sorted(mapping)) or "(nothing — "
                               "every slug in the map is already the canonical one)"))
    found = scan(root, {**mapping, target: target}, trees)
    carriers = [p for p in found
                if mentions(entities_value(read_text(os.path.join(root, p))) or "",
                            set(mapping))]

    drift = []
    if args.expect:
        with open(args.expect, encoding="utf-8") as fh:
            listed = {ln.strip().replace("\\", "/") for ln in fh if ln.strip()}
        for p in sorted(set(found) - listed):
            drift.append("not in the expected list: %s" % p)
        for p in sorted(listed - set(found)):
            drift.append("listed but not carrying the tag now: %s" % p)

    changed, refused, problems = [], [], []
    for rel in carriers:
        path = os.path.join(root, rel)
        text = read_text(path)
        new, did, why = rewrite(text, mapping)
        if why:
            refused.append("%s: %s" % (rel, why))
            continue
        if not did:
            continue
        bad = verify(text, new, rel)
        if bad:
            problems.append(bad)
            continue
        changed.append((rel, new))

    print("%d file(s) carry the entity, %d to rewrite" % (len(found), len(changed)))
    print("   raw  %d" % sum(1 for p, _ in changed if p.startswith("raw/")))
    print("   wiki %d" % sum(1 for p, _ in changed if p.startswith("wiki/")))
    for rel, _ in changed:
        print("      %s" % rel)
    for line in drift:
        print("DRIFT   %s" % line)
    for line in refused:
        print("REFUSED %s" % line)
    for line in problems:
        print("PROBLEM %s" % line)

    if drift or refused or problems:
        print("\nnot writing: %d drift, %d refusal(s), %d problem(s)"
              % (len(drift), len(refused), len(problems)))
        return 1
    if not args.write:
        print("\ndry run — nothing written. Add --write.")
        return 0
    for rel, new in changed:
        with open(os.path.join(root, rel), "wb") as fh:
            fh.write(new.encode("utf-8"))
    print("\nwrote %d file(s)." % len(changed))
    return 0


if __name__ == "__main__":
    sys.exit(main())
