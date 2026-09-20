#!/usr/bin/env python3
r"""ingested-backfill.py — restore the `ingested:` date on `raw/` records that lost it.

**Runs on OSINT's machine, in OSINT's repository root, against `master`.** Corpus wrote it
and delivered it on the share; it is a script plus its own scope, not a patch, because
`raw/` is rewritten nightly and a patch cut against a mirror across hundreds of files
conflicts by certainty. It reads `raw/` and git and nothing else — no clone, no `logs/`.

Housekeeping job 88. `schemas.md` §4 makes `ingested:` required on a source in `raw/`, and
the backfill lane's staging path dropped it on every country it touched: 655 records at the
2026-09-03 measurement, 368 of them repaired in place that day because their admission date
was that day's own. The remaining 287 are the ones whose date has to be reconstructed,
which is what this script does.

**The date is the first commit that put the path under `raw/`.** Two obvious spellings are
both wrong, and the second is the one that bites:

- `git log --diff-filter=A` **without** `--follow` returns the commit that added the path
  *as spelled today*. Every record older than 2026-08-03 was moved by `housekeeping 18:
  shard raw/ into raw/YYYY/`, so that reading stamps the shard date on the whole pre-shard
  corpus — a move recorded as an admission, which is a false evidentiary date.
- `git log --follow --diff-filter=A` walks back past the move and past `raw/` entirely,
  landing on the sweep that staged the file in `new-queue/` or `new/` — a date one to two
  days earlier than admission, and sometimes a batch older than that.

So: follow the rename chain, and take the **oldest commit at which the path was still under
`raw/`**. Checked against a record whose date survived — MDG, `sweep_batch: MDG-2026-07-17`,
carrying `ingested: 2026-07-18` — the chain runs `new-queue/MDG/` 07-17, `new/` 07-18,
`raw/` 07-18, `raw/YYYY/` 08-03, and the rule returns 07-18. Bare `--diff-filter=A` returns
08-03 and `--follow` returns 07-17.

**A date earlier than the record's own `published:` is refused, not written.** That is the
dry run's headline check: a reconstruction that predates publication has followed the wrong
chain, and the gap is better than a wrong date. Anything refused is listed for a hand call.

Usage:
    python scripts/ingested-backfill.py --check      # audit only, writes nothing
    python scripts/ingested-backfill.py              # dry run: resolve and report
    python scripts/ingested-backfill.py --write      # write the resolved dates

Exit: 0 clean (or, on a dry run, every missing record resolved), 1 findings remain — a
record this cannot date, or an existing `ingested:` earlier than its `published:` — 2 the
repository root is not where the script was pointed.
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys

KEY = "ingested"

# Where the key belongs when it has to be reinserted, in `schemas.md` §4's own order. The
# first of these present in the file is written after; a record with none of them takes the
# key immediately before `places:`, and one with none of those takes it last.
AFTER = ("date_source", "date_precision", "published")
BEFORE = ("places",)

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
KEY_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)\s*:(.*)$")


def git(root, *args):
    """git, read as bytes and decoded as UTF-8.

    `core.quotepath=false` and a byte-level read are both needed: `raw/` carries slugs with
    accents and a couple with invisible characters, and letting git escape them or letting
    Python decode them under the Windows locale codec is how a whole-corpus pass dies on
    two files.
    """
    out = subprocess.run(
        ("git", "-c", "core.quotepath=false", *args),
        cwd=root, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    if out.returncode != 0:
        return None
    return out.stdout.decode("utf-8", "replace")


def frontmatter(path):
    """(lines, start, end, keys) — the frontmatter block and what it says.

    Returns `None` when the file has no closing `---`. Line endings are kept on the lines,
    because a record written with CRLF has to be written back with CRLF.
    """
    with open(path, "rb") as fh:
        raw = fh.read()
    text = raw.decode("utf-8", "replace")
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip().lstrip("﻿") != "---":
        return None
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        return None
    keys = {}
    for ln in lines[1:end]:
        m = KEY_RE.match(ln)
        if m and m.group(1) not in keys:
            keys[m.group(1)] = m.group(2).strip().strip("'\"")
    return lines, 1, end, keys


def records(root):
    for dirpath, _, filenames in os.walk(os.path.join(root, "raw")):
        for fn in sorted(filenames):
            if fn.endswith(".md"):
                yield os.path.join(dirpath, fn)


def admitted(root, path):
    """The date the path first appeared under `raw/`, or None.

    `--follow --name-only` gives the rename chain newest-first; the oldest entry still
    spelled under `raw/` is the admission. Walking past it reaches `new/` and the sweep.
    """
    rel = os.path.relpath(path, root).replace(os.sep, "/")
    out = git(root, "log", "--follow", "--name-only", "--format=%x01%cs", "--", rel)
    if not out:
        return None
    date = None
    answer = None
    for line in out.splitlines():
        if line.startswith("\x01"):
            date = line[1:].strip()
            continue
        name = line.strip()
        if name.startswith("raw/") and date:
            answer = date          # keep overwriting: the last one seen is the oldest
    return answer


def published(keys):
    """`published:` as a comparable YYYY-MM-DD, or None. A month- or year-precision date
    compares at its first day, which is the earliest it could mean."""
    m = re.match(r"^(\d{4})(?:-(\d{2}))?(?:-(\d{2}))?", keys.get("published", ""))
    if not m:
        return None
    return "%s-%s-%s" % (m.group(1), m.group(2) or "01", m.group(3) or "01")


def insert(lines, start, end, date):
    """The frontmatter lines with `ingested:` put back where the schema has it."""
    eol = "\r\n" if lines[start].endswith("\r\n") else "\n"
    line = "%s: %s%s" % (KEY, date, eol)
    for want in AFTER:
        for i in range(start, end):
            m = KEY_RE.match(lines[i])
            if m and m.group(1) == want:
                return lines[:i + 1] + [line] + lines[i + 1:]
    for want in BEFORE:
        for i in range(start, end):
            m = KEY_RE.match(lines[i])
            if m and m.group(1) == want:
                return lines[:i] + [line] + lines[i:]
    return lines[:end] + [line] + lines[end:]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=".", help="the repository root (default: cwd)")
    ap.add_argument("--check", action="store_true",
                    help="audit only: what is missing, and what is dated before publication")
    ap.add_argument("--write", action="store_true", help="write the resolved dates")
    args = ap.parse_args(argv)

    root = os.path.abspath(args.root)
    if not os.path.isdir(os.path.join(root, "raw")):
        print("no raw/ under %s -- point --root at OSINT's repository root" % root,
              file=sys.stderr)
        return 2

    missing, unreadable, backdated = [], [], []
    total = 0
    for path in records(root):
        total += 1
        fm = frontmatter(path)
        if fm is None:
            unreadable.append(path)
            continue
        lines, start, end, keys = fm
        if KEY not in keys:
            missing.append((path, lines, start, end, keys))
            continue
        pub = published(keys)
        if DATE_RE.match(keys[KEY]) and pub and keys[KEY] < pub:
            backdated.append((path, keys[KEY], keys.get("published", "")))

    rel = lambda p: os.path.relpath(p, root).replace(os.sep, "/")
    print("raw/: %d records, %d missing `%s:`" % (total, len(missing), KEY))
    for path in unreadable:
        print("  unreadable frontmatter  %s" % rel(path))
    for path, ing, pub in backdated:
        print("  ingested before published  %s  %s < %s" % (rel(path), ing, pub))

    if args.check:
        return 1 if (missing or unreadable or backdated) else 0

    resolved, refused = [], []
    for path, lines, start, end, keys in missing:
        date = admitted(root, path)
        pub = published(keys)
        if not date or not DATE_RE.match(date):
            refused.append((path, "no commit puts this path under raw/"))
        elif pub and date < pub:
            refused.append((path, "resolved %s is before published %s" % (date, pub)))
        else:
            resolved.append((path, lines, start, end, date))

    for path, why in refused:
        print("  refused  %s  -- %s" % (rel(path), why))
    for path, _, _, _, date in resolved:
        print("  %s  %s" % (date, rel(path)))

    if args.write:
        for path, lines, start, end, date in resolved:
            with open(path, "wb") as fh:
                fh.write("".join(insert(lines, start, end, date)).encode("utf-8"))
        print("written: %d" % len(resolved))
    elif resolved:
        print("dry run: %d would be written -- rerun with --write" % len(resolved))

    return 1 if (refused or unreadable or backdated) else 0


if __name__ == "__main__":
    sys.exit(main())
