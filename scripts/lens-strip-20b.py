#!/usr/bin/env python3
r"""lens-strip-20b.py — remove the retired `lens:` key from everywhere `raw/` is not.

**Runs on OSINT's machine, in OSINT's repository root, against `master`.** Corpus wrote
it and delivered it on the share with its input; it is a script plus a list, not a patch,
because it rewrites Markdown that OSINT's own passes touch and a whole-file patch across
1,696 of them conflicts by certainty. It reads the four roots named in its input and
nothing else — no clone, no `logs/`, no git, no network.

Strategic review 4, R49 (task 20b), following R35/R36 which did the same to `raw/`. That
run stripped 15,372 records; what is left is **1,696 files outside `raw/`**, counted by
OSINT on `master` on 2026-09-20 and written into `wiki/schemas.md` §4:

    wiki/            1,089   (1,051 intersections, 38 concepts)
    budget-archive/    599   (the archived companions)
    new-budget/          6
    scratchpad/          2

**The check R49 asks for, first, because the job is conditional on it.** Corpus read
OSINT's `scripts/`, `lookups/` and `wiki/` — the trees the interface and the patch lane
let it read — for anything that compiles, exports or branches on the key. **Nothing
compiles it and nothing breaks when it goes.** Four reads exist and all four survive:

- `scripts/build-catalogue.py` lifts `lens` into `raw-catalogue.json` and counts it as a
  facet. It is **unwired** (`wiki/index.md` line 117: retired from the cycle 2026-08-16,
  left standing) and it walks `raw/` only, which is already zero.
- `scripts/vault_lib.py` indexes `lens` as a facet of the local vault index. The index is
  rebuilt from the tree, so the facet empties itself; nothing queries it by name.
- `scripts/lint-deterministic.py` check #2 refuses an out-of-vocabulary `lens:` value.
  After this it has nothing to read anywhere in the corpus and becomes a permanently
  vacuous guard. That is a reason to retire the clause, not a reason not to run this.
- `scripts/lint-deterministic.py` `check_links` whitelists `sovereignty` and `colonialism`
  as intentional-dead wikilink targets. **It reads `LENS_VALUES`, a constant, not the
  frontmatter** — so it is untouched by the strip, and it must stay: the words remain
  wikilinked in legacy *body prose*, which this does not touch. Retiring #2's clause and
  deleting the constant with it would turn every one of those links into a §9 finding.

Nothing **writes** the key. Six spent generators under `scripts/archive/` still emit
`lens: []` in their record templates; they are spent by definition, and an unlisted
carrier appearing at run time is what this reports if one is ever re-run.
`wiki/capture-rule.md` already carries *"Never write `lens:`"* as the standing instruction
to the writers. Corpus does not read OSINT's procedure files, so the procedures are the
one place it could not look; that is OSINT's own grep and it is named in the brief.

**Two kinds of root, because Corpus may not read three of the four.** The interface lets
Corpus read `raw/`, `wiki/` and `lookups/`; `budget-archive/`, `new-budget/` and
`scratchpad/` are outside it, so no list of their paths could honestly be cut here.

- A **listed** root comes with every one of its paths, and drift is reported exactly as in
  20a: a listed path missing from the tree, a carrier the list does not name, and (after a
  write) the listed paths that no longer carry the key, counted in one line.
- A **counted** root comes with the count *OSINT itself published* in `wiki/schemas.md`
  §4, and the script walks it. The count matching is the whole of the check. A count of
  zero is the job already done. Any other disagreement is drift, and that root is
  **skipped rather than stripped** — the conservative option, since there is no list to
  say which files the difference is in.

**`raw/` is refused by name.** It is 20a's and it is finished; a root line naming it, or a
listed path under it, stops the run rather than quietly doing the job twice.

**586 of the 1,089 `wiki/` pages carry a value, not an empty list** — 516 `[sovereignty]`,
60 `[sovereignty, colonialism]`, 6 `[colonialism]`, 4 `[colonialism, sovereignty]`. Those
are classifications somebody made, and after this they exist only in git history, as
R35's 2,841 already do. The budget roots were not read here and their values are unknown
until the dry run prints them.

**The removal is the same one, byte for byte.** The file is handled as bytes, split on
`\n`, one element dropped, rejoined — line endings, the BOM, a missing trailing newline,
quoting and key order are what they were (96 of the 1,089 `wiki/` pages are CRLF). Every
removal is reconstructed and compared to the original before it is written, and a doubled
key, a block value or unclosed frontmatter is refused rather than written.

Usage:
    python lens-strip-20b.py                            # dry run: what would go
    python lens-strip-20b.py --write                    # remove the key
    python lens-strip-20b.py --only wiki                # one root
    python lens-strip-20b.py --roots lens-roots-20b.csv --list lens-slugs-20b.txt --root .

Exit: 0 the run is clean, 1 a file was refused or a root drifted from its input, 2 the
repository root or an input file is not where the script was pointed.
"""
from __future__ import annotations

import argparse
import csv
import os
import re
import sys

KEY_RE = re.compile(rb"^lens\s*:(.*)$", re.S)
# A line that continues a block sequence or mapping under the key: `  - sovereignty`, or
# any indented continuation. If one follows an empty `lens:`, the value is not on the key's
# own line and dropping the line alone would orphan it.
CONT_RE = re.compile(rb"^(\s+\S|-\s)")

# 20a's root, finished on 2026-09-20. Named here so a scope that overlaps it stops rather
# than doing the job a second time against a tree ingest rewrites nightly.
FORBIDDEN_ROOTS = {"raw"}

CAP = 20        # per-finding lines printed before the rest is counted


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


def show(items):
    """The first `CAP` of a finding, then a line saying how many were not printed.

    A run that lists every one of a thousand paths is a run nobody reads to the end, and
    the thing worth seeing is usually in the first few."""
    for rel in items[:CAP]:
        yield rel
    if len(items) > CAP:
        yield "... and %d more" % (len(items) - CAP)


def read_roots(path):
    """The scope: [(root, mode, expected, source)], or a list of complaints.

    `root,mode,expected,source`. `mode` is `listed` — the input names every path under it
    — or `counted`, where only the count is known because Corpus may not read the tree.
    """
    rows, bad = [], []
    with open(path, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            root = (row.get("root") or "").strip().strip("/")
            mode = (row.get("mode") or "").strip()
            expected = (row.get("expected") or "").strip()
            if not root or root.startswith("#"):
                continue
            if "/" in root or "\\" in root or ".." in root:
                bad.append("root `%s` is not a single top-level directory" % root)
                continue
            if root in FORBIDDEN_ROOTS:
                bad.append("root `%s` is task 20a's and is finished -- refused" % root)
                continue
            if mode not in ("listed", "counted"):
                bad.append("root `%s` has mode `%s`, not listed or counted" % (root, mode))
                continue
            if not expected.isdigit():
                bad.append("root `%s` has no expected count" % root)
                continue
            rows.append((root, mode, int(expected), (row.get("source") or "").strip()))
    return rows, bad


def read_list(path, listed_roots):
    """The input list, as repo-relative paths under a listed root. Anything else is refused."""
    paths, bad = [], []
    with open(path, "rb") as fh:
        for line in fh:
            rel = line.decode("utf-8", "replace").strip().replace("\\", "/")
            if not rel or rel.startswith("#"):
                continue
            head = rel.split("/")[0]
            if not rel.endswith(".md") or ".." in rel:
                bad.append(rel)
            elif head in FORBIDDEN_ROOTS:
                bad.append(rel)
            elif head not in listed_roots:
                bad.append(rel)
            else:
                paths.append(rel)
    return paths, bad


def carrying(root_abs, root, repo):
    """Every `.md` under one root that still has the key, found in the tree itself."""
    out = []
    for dirpath, dirnames, filenames in os.walk(root_abs):
        dirnames[:] = [d for d in dirnames if d != ".git"]
        for fn in sorted(filenames):
            if not fn.endswith(".md"):
                continue
            p = os.path.join(dirpath, fn)
            with open(p, "rb") as fh:
                raw = fh.read()
            fm = frontmatter(raw)
            if fm and any(KEY_RE.match(fm[0][i]) for i in range(fm[1], fm[2])):
                out.append(os.path.relpath(p, repo).replace(os.sep, "/"))
    return out


def plan_listed(want, found, repo):
    """(to_strip, findings, clean) for a root whose every path was named in the input."""
    wset, fset = set(want), set(found)
    findings = []
    unlisted = sorted(fset - wset)
    absent = sorted(rel for rel in wset - fset
                    if not os.path.isfile(os.path.join(repo, rel.replace("/", os.sep))))
    already = len(wset - fset) - len(absent)
    for rel in show(unlisted):
        findings.append("carries the key, not on the list  %s" % rel)
    for rel in show(absent):
        findings.append("on the list, not in the tree  %s" % rel)
    if already:
        findings.append("%d listed file(s) no longer carry the key -- already stripped"
                        % already)
    return sorted(wset & fset), findings, not (unlisted or absent)


def plan_counted(found, expected, source):
    """(to_strip, findings, clean) for a root Corpus could not enumerate.

    The count is the whole of the check, so a count that disagrees strips nothing here:
    with no list there is nothing to say which files the difference is in, and skipping a
    root is recoverable where stripping the wrong thousand files is not.
    """
    n = len(found)
    if n == expected:
        return sorted(found), [], True
    if n == 0:
        return [], ["carries the key on no file -- already stripped"], True
    return [], ["expected %d file(s) carrying the key, found %d -- skipped, not stripped "
                "(count from: %s)" % (expected, n, source or "unstated")], False


def main(argv=None):
    here = os.path.dirname(os.path.abspath(__file__))
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=".", help="the repository root (default: cwd)")
    ap.add_argument("--roots", default=os.path.join(here, "lens-roots-20b.csv"),
                    help="the scope: root,mode,expected,source")
    ap.add_argument("--list", default=os.path.join(here, "lens-slugs-20b.txt"),
                    help="the input: one repo-relative path per line, for listed roots")
    ap.add_argument("--only", action="append", default=None,
                    help="run one root only; repeatable")
    ap.add_argument("--write", action="store_true", help="remove the key")
    args = ap.parse_args(argv)

    repo = os.path.abspath(args.root)
    for path, what in ((args.roots, "scope"), (args.list, "input list")):
        if not os.path.isfile(path):
            print("no %s at %s" % (what, path), file=sys.stderr)
            return 2

    scope, bad_roots = read_roots(args.roots)
    for why in bad_roots:
        print("  refused from the scope  %s" % why)
    # **`--only` narrows what runs, not what the input may name.** The listed roots are
    # taken from the whole scope, so running one root does not turn another root's paths
    # into refusals and report a scope problem that is not there.
    listed_roots = {r for r, mode, _, _ in scope if mode == "listed"}
    if args.only:
        scope = [r for r in scope if r[0] in set(args.only)]
        if not scope:
            print("no root in the scope matches --only %s" % ", ".join(args.only),
                  file=sys.stderr)
            return 2
    missing = [r for r, _, _, _ in scope if not os.path.isdir(os.path.join(repo, r))]
    if missing:
        print("no %s under %s -- point --root at OSINT's repository root"
              % ("/, ".join(missing) + "/", repo), file=sys.stderr)
        return 2

    want, bad_paths = read_list(args.list, listed_roots)
    for rel in show(bad_paths):
        print("  refused from the input  %s  -- not under a listed root" % rel)

    todo, findings, clean = [], [], not (bad_roots or bad_paths)
    for root, mode, expected, source in scope:
        found = carrying(os.path.join(repo, root), root, repo)
        if mode == "listed":
            mine = [p for p in want if p.split("/")[0] == root]
            picked, said, ok = plan_listed(mine, found, repo)
            print("%-16s listed   input %5d   tree %5d" % (root + "/", len(mine), len(found)))
        else:
            picked, said, ok = plan_counted(found, expected, source)
            print("%-16s counted  expect %4d   tree %5d" % (root + "/", expected, len(found)))
        for line in said:
            print("  %s" % line)
        todo.extend(picked)
        clean = clean and ok

    done, refused = [], []
    for rel in todo:
        p = os.path.join(repo, rel.replace("/", os.sep))
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

    return 0 if (clean and not refused) else 1


if __name__ == "__main__":
    sys.exit(main())
