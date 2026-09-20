#!/usr/bin/env python3
r"""intersection-rename.py — one prefix per place, and every inbound link moved with it.

Housekeeping job 96, strategic review 4 register R47. 68 of 1,091 intersection pages are
named by ISO3 (`gnq--dpi-id.md`) and 1,023 by a place name (`guinea-bissau--dpi-mis.md`).
**No spec states which is right**: `wiki/layout.md` §126 says only that intersections are
created lazily, and neither `schemas.md` nor `facets.md` names a filename shape — so
neither form is a defect and no lint can catch the split. Two countries carry both forms at
once, and a slice writing one of them has to guess.

**The cost is not cosmetic.** A writer looking for `equatorial-guinea--dpi-id` does not find
it; concept-page pointers and index rows have to be written against whichever form happens
to exist; and a `[[wikilink]]` written to the wrong one dangles silently.

**It is a script, not a patch.** A rename plus a link sweep across ~24,000 files is not a
diff anyone should read, and the two index files are edited most days.

**Three things move together or the rename is worse than the split**: the file, every
`[[wikilink]]` pointing at it anywhere under `raw/` and `wiki/`, and any `[[old|label]]`
form. They are done in one pass, and a file is only renamed once its inbound links have
been rewritten successfully.

**Every rewrite is proved, not assumed.** A changed line must differ from the original in
nothing but the slug: the line is reverted by putting the old slug back, and if it does not
then equal the original the file is refused. That catches a substitution that ate a
neighbouring character, which a `grep -rl` sweep would not.

Usage:
  python intersection-rename.py --map intersection-names.csv          # dry run
  python intersection-rename.py --map intersection-names.csv --write
  python intersection-rename.py --map intersection-names.csv --places GNQ,COM

Exit: 0 nothing to do or a clean dry run, 1 a refusal or drift, 2 the tree or the map is
not where the script was pointed.
"""
from __future__ import annotations

import argparse
import collections
import csv
import os
import re
import sys

TREES = ("raw", "wiki")
INTERSECTIONS = os.path.join("wiki", "intersections")

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def read_map(path, only=None):
    """place -> (from_prefix, to_prefix) for every row that actually moves."""
    out = {}
    with open(path, encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            place = (row.get("place") or "").strip()
            src = (row.get("current_prefix") or "").strip()
            dst = (row.get("proposed_prefix") or "").strip()
            if not place or not src or not dst or src == dst:
                continue
            if only and place not in only:
                continue
            out.setdefault(place, []).append((src, dst))
    return out


def renames(root, mapping):
    """[(old_slug, new_slug, old_path, new_path)] — the pages a mapping moves."""
    base = os.path.join(root, INTERSECTIONS)
    out = []
    for place, pairs in sorted(mapping.items()):
        for src, dst in pairs:
            for fn in sorted(os.listdir(base)):
                if not fn.endswith(".md") or "--" not in fn:
                    continue
                prefix, rest = fn[:-3].split("--", 1)
                if prefix != src:
                    continue
                old, new = fn[:-3], "%s--%s" % (dst, rest)
                out.append((old, new, os.path.join(INTERSECTIONS, fn).replace(os.sep, "/"),
                            os.path.join(INTERSECTIONS, new + ".md").replace(os.sep, "/")))
    return out


def link_re(slug):
    """`[[slug]]` and `[[slug|label]]`, and nothing that merely starts with the slug."""
    return re.compile(r"\[\[" + re.escape(slug) + r"(?=[\]|])")


def rewrite(text, pairs):
    """(new_text, hits, refusal). `pairs` is [(old_slug, new_slug)]; `hits` is per slug."""
    out, hits = text, collections.Counter()
    for old, new in pairs:
        out, n = link_re(old).subn("[[" + new, out)
        if n:
            hits[old] += n
    if not hits:
        return text, hits, None
    a, b = text.split("\n"), out.split("\n")
    if len(a) != len(b):
        return text, collections.Counter(), "line count changed"
    for i, (before, after) in enumerate(zip(a, b)):
        if before == after:
            continue
        reverted = after
        for old, new in pairs:
            reverted = link_re(new).sub("[[" + old, reverted)
        # **The changed line must differ in nothing but the slug.** Reverting the
        # substitution has to reproduce the original exactly; if it does not, something
        # other than a link moved and the file is not this script's to touch.
        if reverted != before:
            return (text, collections.Counter(),
                    "line %d changed by more than the slug" % (i + 1))
    return out, hits, None


def sweep(root, pairs, trees=TREES):
    """(files to rewrite, refusals). One walk, every tree, both link forms."""
    wanted = {old for old, _ in pairs}
    changed, refused, per_slug = [], [], collections.Counter()
    for tree in trees:
        base = os.path.join(root, tree)
        if not os.path.isdir(base):
            continue
        for dirpath, _, filenames in os.walk(base):
            for fn in filenames:
                if not fn.lower().endswith(".md"):
                    continue
                path = os.path.join(dirpath, fn)
                rel = os.path.relpath(path, root).replace(os.sep, "/")
                text = open(path, "rb").read().decode("utf-8", "replace")
                if not any(("[[" + s) in text for s in wanted):
                    continue
                new, hits, why = rewrite(text, pairs)
                if why:
                    refused.append("%s: %s" % (rel, why))
                elif hits:
                    per_slug.update(hits)
                    changed.append((rel, new, sum(hits.values())))
    return changed, refused, per_slug


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=".", help="the repository root (default: cwd)")
    ap.add_argument("--map", required=True, help="the prefix table, as CSV")
    ap.add_argument("--places", default=None, help="only these ISO3 places, comma-separated")
    ap.add_argument("--trees", default=",".join(TREES), help="trees to sweep for links")
    ap.add_argument("--write", action="store_true", help="rename the files and rewrite links")
    args = ap.parse_args(argv)

    root = os.path.abspath(args.root)
    if not os.path.isdir(os.path.join(root, INTERSECTIONS)):
        print("no %s under %s" % (INTERSECTIONS, root), file=sys.stderr)
        return 2
    only = {p.strip() for p in args.places.split(",")} if args.places else None
    mapping = read_map(args.map, only)
    moves = renames(root, mapping)
    if not moves:
        print("nothing to rename.")
        return 0

    pairs = [(old, new) for old, new, _, _ in moves]
    clash = [new for _, new, _, dst in moves if os.path.exists(os.path.join(root, dst))]
    changed, refused, per_slug = sweep(root, pairs,
                                       tuple(t for t in args.trees.split(",") if t))
    inbound = sum(h for _, _, h in changed)

    print("%d page(s) to rename across %d place(s)" % (len(moves), len(mapping)))
    for place, prs in sorted(mapping.items()):
        print("   %-5s %s" % (place, ", ".join("%s -> %s" % p for p in prs)))
    print("\n%d inbound link(s) in %d file(s)" % (inbound, len(changed)))
    print("   raw  %d" % sum(1 for r, _, _ in changed if r.startswith("raw/")))
    print("   wiki %d" % sum(1 for r, _, _ in changed if r.startswith("wiki/")))
    for old, new, _, _ in moves[:80]:
        print("      %s  ->  %s" % (old, new))

    for name in clash:
        print("CLASH   %s already exists" % name)
    for line in refused:
        print("REFUSED %s" % line)
    # A page with no inbound link at all is not an error, but it is worth seeing: it means
    # nothing points at it, which is job 89's defect rather than this one. Counted while
    # sweeping — asking the *rewritten* text whether it still names the old slug would
    # report every page as unlinked, by construction.
    unlinked = [old for old, _, _, _ in moves if not per_slug[old]]
    if unlinked:
        print("\n%d page(s) have no inbound link (job 89's defect, not this one)"
              % len(unlinked))

    if clash or refused:
        print("\nnot writing: %d clash(es), %d refusal(s)" % (len(clash), len(refused)))
        return 1
    if not args.write:
        print("\ndry run — nothing written. Add --write.")
        return 0

    # Links first: a rename that lands before its links are rewritten leaves the tree
    # briefly full of dangling pointers, and a failure in between leaves it that way.
    for rel, new, _ in changed:
        with open(os.path.join(root, rel), "wb") as fh:
            fh.write(new.encode("utf-8"))
    for _, _, src, dst in moves:
        os.rename(os.path.join(root, src), os.path.join(root, dst))
    print("\nrewrote %d file(s), renamed %d page(s)." % (len(changed), len(moves)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
