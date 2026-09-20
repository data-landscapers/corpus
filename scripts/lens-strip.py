#!/usr/bin/env python3
r"""lens-strip.py — remove the retired `lens:` key from `raw/`, and nothing else.

**Runs on OSINT's machine, in OSINT's repository root, against `master`.** Corpus wrote
it and delivered it on the share with its input; it is a script plus a list, not a patch,
because `raw/` is rewritten nightly and a patch across fifteen thousand files conflicts by
certainty. It reads `raw/` and its own input file and nothing else — no clone, no `logs/`,
no git.

Strategic review 4, R35 (task 20a). `lens:` was retired on 2026-09-08: nothing writes it,
no pass adds it, it is not in the schema, and the catalogue stopped reading it on
2026-09-20 (R34a) — including the facet it was still counting. What is left is the key
sitting in 15,372 `raw/` records, which this removes.

**It reads each file as it stands and removes one line.** It does not parse the
frontmatter as YAML and it does not write it back: a record whose frontmatter YAML cannot
read is still a record whose `lens:` line can be deleted, and re-serialising would rewrite
quoting, ordering and line endings across the whole corpus to delete one field. The whole
file is handled as **bytes**, split on `\n`, one element dropped, rejoined — so the line
endings, the BOM, the trailing newline and every other byte are what they were.

**Every file is proved before it is written.** The removal is reconstructed — the dropped
line is put back at its own index and the result compared to the original bytes — and a
file that does not reproduce exactly is refused rather than written. A file is also
refused where the key appears twice in the frontmatter, where the value is not on the same
line as the key (a block sequence, which would leave its items orphaned), or where the
frontmatter does not open and close. **None of those exists in the corpus as measured**:
all 15,372 carry a single-line flow value, 12,531 of them the empty `[]`. The guards are
there because the measurement was taken against a mirror and the run is against `master`.

**2,841 of the records carry a value, not an empty list** — 2,543 `[sovereignty]`, 200
`[sovereignty, colonialism]`, 69 `[colonialism]`, 26 `[colonialism, sovereignty]`, 2
`[analysis]`, 1 `[reference]`. Those are classifications somebody made, and after this
they exist only in git history. The ruling to strip them is Bill's (2026-09-20, over the
`wiki/schemas.md` note of 2026-09-08 that said to leave them); this says what it costs.

**`wiki/` is not this script's business.** Task 20b is the 1,678 pages there, after a
check of what compiles or reads the key, and a run that reached into `wiki/` would be
doing that job without its check. `lens-slugs.txt` carries only `raw/` paths and anything
else in it is refused.

Usage:
    python lens-strip.py                      # dry run: what would go, and what drifted
    python lens-strip.py --write              # remove the key
    python lens-strip.py --list lens-slugs.txt --root .

Exit: 0 the run is clean, 1 a file was refused or the input drifted from the tree, 2 the
repository root or the input list is not where the script was pointed.
"""
from __future__ import annotations

import argparse
import os
import re
import sys

KEY_RE = re.compile(rb"^lens\s*:(.*)$", re.S)
# A line that continues a block sequence or mapping under the key: `  - sovereignty`, or
# any indented continuation. If one follows an empty `lens:`, the value is not on the key's
# own line and dropping the line alone would orphan it.
CONT_RE = re.compile(rb"^(\s+\S|-\s)")


def frontmatter(raw: bytes):
    """(lines, first, last) — the frontmatter's line indices, or None.

    `lines` is the whole file split on `\\n`, so an element still carries its `\\r` where
    the file is CRLF. `first` is the line after the opening `---`, `last` the index of the
    closing one.
    """
    lines = raw.split(b"\n")
    if not lines:
        return None
    if lines[0].lstrip(b"\xef\xbb\xbf").strip() != b"---":
        return None
    for i in range(1, len(lines)):
        if lines[i].strip() == b"---":
            return lines, 1, i
    return None


def strip_one(raw: bytes):
    """(new_bytes, value) with the `lens:` line gone, or (None, why).

    The removal is reconstructed and compared to the original before it is returned, so a
    caller never writes a file this has not proved it can put back.
    """
    fm = frontmatter(raw)
    if fm is None:
        return None, "frontmatter does not open and close"
    lines, first, last = fm
    hits = [i for i in range(first, last) if KEY_RE.match(lines[i])]
    if not hits:
        return None, "no `lens:` in the frontmatter"
    if len(hits) > 1:
        return None, "`lens:` appears %d times" % len(hits)
    i = hits[0]
    value = KEY_RE.match(lines[i]).group(1).strip()
    if not value and i + 1 < last and CONT_RE.match(lines[i + 1]):
        return None, "the value is a block, not on the key's own line"
    out = lines[:i] + lines[i + 1:]
    back = out[:i] + [lines[i]] + out[i:]
    if b"\n".join(back) != raw:
        return None, "the removal does not reconstruct byte for byte"
    return b"\n".join(out), value.decode("utf-8", "replace")


CAP = 20        # per-finding lines printed before the rest is counted


def show(items):
    """The first `CAP` of a finding, then a line saying how many were not printed.

    A run that lists every one of fifteen thousand paths is a run nobody reads to the end,
    and the thing worth seeing is usually in the first few."""
    for rel in items[:CAP]:
        yield rel
    if len(items) > CAP:
        yield "... and %d more" % (len(items) - CAP)


def listed(path, root):
    """The input list, as repo-relative paths under `raw/`. Anything else is refused."""
    paths, bad = [], []
    with open(path, "rb") as fh:
        for line in fh:
            rel = line.decode("utf-8", "replace").strip().replace("\\", "/")
            if not rel or rel.startswith("#"):
                continue
            if not rel.startswith("raw/") or not rel.endswith(".md") or ".." in rel:
                bad.append(rel)
                continue
            paths.append(rel)
    return paths, bad


def carrying(root):
    """Every `raw/` record that still has the key, found in the tree itself."""
    out = []
    for dirpath, _, filenames in os.walk(os.path.join(root, "raw")):
        for fn in sorted(filenames):
            if not fn.endswith(".md"):
                continue
            p = os.path.join(dirpath, fn)
            with open(p, "rb") as fh:
                raw = fh.read()
            fm = frontmatter(raw)
            if fm and any(KEY_RE.match(fm[0][i]) for i in range(fm[1], fm[2])):
                out.append(os.path.relpath(p, root).replace(os.sep, "/"))
    return out


def main(argv=None):
    here = os.path.dirname(os.path.abspath(__file__))
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=".", help="the repository root (default: cwd)")
    ap.add_argument("--list", default=os.path.join(here, "lens-slugs.txt"),
                    help="the input: one repo-relative raw/ path per line")
    ap.add_argument("--write", action="store_true", help="remove the key")
    args = ap.parse_args(argv)

    root = os.path.abspath(args.root)
    if not os.path.isdir(os.path.join(root, "raw")):
        print("no raw/ under %s -- point --root at OSINT's repository root" % root,
              file=sys.stderr)
        return 2
    if not os.path.isfile(args.list):
        print("no input list at %s" % args.list, file=sys.stderr)
        return 2

    want, bad = listed(args.list, root)
    found = carrying(root)
    wset, fset = set(want), set(found)

    print("input: %d path(s); raw/ carries the key on %d record(s)" % (len(want), len(found)))
    for rel in bad:
        print("  refused from the input  %s  -- not a raw/ record" % rel)

    # **Drift is reported; a job already done is not drift.** Three things can be true of
    # a listed path that this run will not strip, and they are not the same finding:
    #
    # - **It is not in the tree.** The list was cut against a mirror and the record has
    #   been renamed or deleted since. That is drift and the run is not clean.
    # - **It is there and no longer carries the key** — because a previous run of this
    #   removed it. Run again after a write and that is *every* path on the list, so
    #   reporting them one by one would bury a real finding under fifteen thousand
    #   expected ones. It is counted in a line and it is not a failure.
    # - **A record carries the key and the list does not name it.** That is the one worth
    #   waking up for: nothing has written this key since 2026-09-08, so a new carrier
    #   means something has started again. Reported, and the run is not clean.
    unlisted = sorted(fset - wset)
    absent = sorted(rel for rel in wset - fset
                    if not os.path.isfile(os.path.join(root, rel.replace("/", os.sep))))
    already = len(wset - fset) - len(absent)
    for rel in show(unlisted):
        print("  carries the key, not on the list  %s" % rel)
    for rel in show(absent):
        print("  on the list, not in the tree  %s" % rel)
    if already:
        print("  %d listed record(s) no longer carry the key -- already stripped" % already)

    done, refused = [], []
    for rel in sorted(wset & fset):
        p = os.path.join(root, rel.replace("/", os.sep))
        with open(p, "rb") as fh:
            raw = fh.read()
        out, why = strip_one(raw)
        if out is None:
            refused.append((rel, why))
        else:
            done.append((rel, p, out, why))

    for rel, why in refused[:CAP]:
        print("  refused  %s  -- %s" % (rel, why))
    if len(refused) > CAP:
        print("  ... and %d more refused" % (len(refused) - CAP))

    values = {}
    for _, _, _, value in done:
        values[value] = values.get(value, 0) + 1
    for value, n in sorted(values.items(), key=lambda kv: -kv[1]):
        print("  %6d  lens: %s" % (n, value))

    if args.write:
        for _, p, out, _ in done:
            with open(p, "wb") as fh:
                fh.write(out)
        print("written: %d" % len(done))
    else:
        print("dry run: %d would be stripped -- rerun with --write" % len(done))

    return 1 if (refused or bad or unlisted or absent) else 0


if __name__ == "__main__":
    sys.exit(main())
