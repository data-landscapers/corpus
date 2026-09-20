#!/usr/bin/env python3
r"""artefact-dupes.py — byte-identical artefacts under different slugs, with what cites them.

Housekeeping job 106, strategic review 4 register R37. Two `raw/` records were found on
2026-09-10 holding the same 6,106,386-byte PDF under different slugs, differing only in
which URL each companion page cites. **Nothing in the vault would have caught it**: ingest's
tier-3 dedup works on titles and ledes, and the `raw/` URL index works on normalised URLs,
so a document served from two routes defeats both and both pages read as legitimate records
to every check that runs.

This is the measurement half. **The retirement call per pair is OSINT's** — which companion
page survives is `CLAUDE.md` → *Duplicates*, a read of two pages, and it is not a thing a
script decides. What a script can do is put everything that call needs on one line: the two
paths, the record each belongs to, and how much rewiring each side costs.

**Identity is proved by comparing the bytes, not by trusting a digest.** Files are grouped by
size, then by md5 within a size, and then **every candidate group is confirmed by reading the
files and comparing them directly**. The md5 is reported because job 106 names one and
because the index OSINT will build is an md5 index; it is not what the answer rests on.

**The citation count is the cost of retiring a slug.** It counts the distinct pages that
reach the record: `sources:` and `cite_through:` in frontmatter, and `[[slug]]` in a body.
A pair where one side is cited forty times and the other twice answers its own question; a
pair where both are cited is the one that needs the eyes.

**`budget-archive/` is in job 106's scope and is not in Corpus's.** The interface Corpus may
read is `raw/`, `wiki/`, `lookups/` and the cycle manifest (`CLAUDE.md` → *The OSINT repo is
read-only*), so this run covers `raw/` and OSINT runs the same script over the other tree
with `--tree budget-archive`. A cross-tree collision is therefore not measured here, and
saying so is better than a table that looks complete.

Usage:
  python artefact-dupes.py                                  # raw/, table to stdout
  python artefact-dupes.py --tree budget-archive            # the tree Corpus cannot read
  python artefact-dupes.py --csv artefact-dupes.csv         # also write the rows
  python artefact-dupes.py --root C:\OSINT --index ...      # from outside the repo

Exit: 0 no collisions, 1 collisions found (the expected outcome while the job is open), 2
the tree is not where the script was pointed.
"""
from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import json
import os
import sys

CITE_KEYS = ("sources", "cite_through")
CHUNK = 1 << 20


def artefacts(root, tree):
    """Every non-Markdown file under the tree — what a record holds rather than writes."""
    out = []
    for dirpath, _, filenames in os.walk(os.path.join(root, tree)):
        for fn in sorted(filenames):
            if not fn.lower().endswith(".md"):
                out.append(os.path.join(dirpath, fn))
    return out


def md5(path):
    h = hashlib.md5()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(CHUNK), b""):
            h.update(block)
    return h.hexdigest()


def same(a, b):
    """The two files, byte for byte. A digest narrows the candidates; this settles them."""
    with open(a, "rb") as fa, open(b, "rb") as fb:
        while True:
            x, y = fa.read(CHUNK), fb.read(CHUNK)
            if x != y:
                return False
            if not x:
                return True


def groups(paths):
    """Byte-identical groups of two or more, as `[(size, md5, [paths])]`.

    Size first because it is free and rules out almost everything; md5 second because it is
    one read per candidate; the byte comparison last because it is the only one that proves
    anything, and by then there is almost nothing left to compare.
    """
    by_size = collections.defaultdict(list)
    for p in paths:
        try:
            by_size[os.path.getsize(p)].append(p)
        except OSError:
            continue
    out = []
    for size, same_size in sorted(by_size.items(), reverse=True):
        if len(same_size) < 2:
            continue
        by_hash = collections.defaultdict(list)
        for p in same_size:
            by_hash[md5(p)].append(p)
        for digest, candidates in by_hash.items():
            if len(candidates) < 2:
                continue
            # Confirm against the first, and drop anything that only shares the digest.
            first, rest = candidates[0], candidates[1:]
            confirmed = [first] + [p for p in rest if same(first, p)]
            if len(confirmed) > 1:
                out.append((size, digest, sorted(confirmed)))
    return out


def vault(index_dir):
    """(holder, cites, about) — who declares each artefact, what cites each slug, and
    the title and URL of each record.

    Read from Corpus's own index rather than by walking the vault again: `files.jsonl`
    already carries every record's parsed frontmatter and `links.jsonl` the edges.
    """
    holder = collections.defaultdict(list)     # artefact basename -> [slug]
    cites = collections.Counter()              # slug -> distinct citing pages
    about = {}                                 # slug -> (title, url)
    seen = set()
    with open(os.path.join(index_dir, "files.jsonl"), encoding="utf-8") as fh:
        for line in fh:
            row = json.loads(line)
            # **Records only.** The index carries a row per *file*, so an artefact has a row
            # of its own under the same slug as the record that holds it, with no
            # frontmatter — and reading those too overwrites the record's title with an
            # empty one, silently, for exactly the pairs whose artefact is named after its
            # record. That is how this first ran.
            if not row["path"].startswith("raw/") or row["d"].get("ext") != ".md":
                continue
            slug = row["d"]["slug"]
            fm = row["fm"] or {}
            about[slug] = (fm.get("title") or "",
                           fm.get("url") if isinstance(fm.get("url"), str) else "")
            held = fm.get("artefact")
            if isinstance(held, str):
                held = [held]
            for name in held or []:
                holder[str(name).strip()].append(slug)
    with open(os.path.join(index_dir, "links.jsonl"), encoding="utf-8") as fh:
        for line in fh:
            edge = json.loads(line)
            if edge["via"] not in CITE_KEYS and edge["via"] != "body":
                continue
            # A page citing the same record twice is one citing page, and a record citing
            # itself is not a citation — both would inflate the cost of a retirement.
            key = (edge["from"], edge["to"])
            if key in seen or edge["from"].endswith("/" + edge["to"] + ".md"):
                continue
            seen.add(key)
            cites[edge["to"]] += 1
    return holder, cites, about


def rows(root, tree, index_dir):
    holder, cites, about = vault(index_dir)
    out = []
    for n, (size, digest, paths) in enumerate(groups(artefacts(root, tree)), 1):
        for p in paths:
            rel = os.path.relpath(p, root).replace(os.sep, "/")
            name = os.path.basename(p)
            slugs = holder.get(name) or []
            out.append({
                "group": n,
                "bytes": size,
                "md5": digest,
                "artefact": rel,
                # An artefact no record declares is its own finding: it is held in the tree
                # and nothing in the vault points at it, so retiring the other side of the
                # pair would leave it unreachable rather than duplicated.
                "record": "; ".join(slugs) or "(no record declares it)",
                "citations": sum(cites.get(s, 0) for s in slugs),
                "title": "; ".join(about.get(s, ("", ""))[0] for s in slugs),
                # **The URL is what tells a duplicate from a republication.** The pair job
                # 106 was registered on differed only in the route each record captured the
                # same file from; a pair whose records cite the same URL is one document
                # taken twice, and a pair citing different publishers may be a document
                # genuinely reissued and not a thing to retire at all.
                "url": " | ".join(about.get(s, ("", ""))[1] for s in slugs),
            })
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=".", help="the repository root (default: cwd)")
    ap.add_argument("--tree", default="raw", help="the tree to hash (default: raw)")
    ap.add_argument("--index", default=None,
                    help="an index/ with files.jsonl and links.jsonl (default: <root>/index)")
    ap.add_argument("--csv", default=None, help="also write the rows here")
    args = ap.parse_args(argv)

    root = os.path.abspath(args.root)
    if not os.path.isdir(os.path.join(root, args.tree)):
        print("no %s/ under %s" % (args.tree, root), file=sys.stderr)
        return 2
    index_dir = args.index or os.path.join(root, "index")
    if not os.path.isfile(os.path.join(index_dir, "files.jsonl")):
        print("no files.jsonl under %s -- build the index first" % index_dir, file=sys.stderr)
        return 2

    found = rows(root, args.tree, index_dir)
    total = len(artefacts(root, args.tree))
    n = len({r["group"] for r in found})
    print("%s/: %d artefact(s), %d byte-identical group(s), %d file(s) in them\n"
          % (args.tree, total, n, len(found)))
    for g in range(1, n + 1):
        members = [r for r in found if r["group"] == g]
        print("group %d - %s bytes, md5 %s" % (g, f"{members[0]['bytes']:,}",
                                               members[0]["md5"]))
        for r in members:
            print("    %-5s cites  %s" % (r["citations"], r["artefact"]))
            print("          record  %s" % r["record"])
            if r["title"]:
                print("          title   %s" % r["title"])
            if r["url"]:
                print("          url     %s" % r["url"])
        print()

    if args.csv:
        with open(args.csv, "w", encoding="utf-8-sig", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=["group", "bytes", "md5", "artefact",
                                               "record", "citations", "title", "url"])
            w.writeheader()
            w.writerows(found)
        print("rows -> %s" % args.csv)

    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
