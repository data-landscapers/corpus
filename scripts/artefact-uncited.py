#!/usr/bin/env python3
r"""artefact-uncited.py — artefacts nothing declares, and declarations with no artefact.

Housekeeping jobs 108 and 109, strategic review 4 register R39. A Phase A slice fetches a
primary, writes it to `raw/`, and dies before writing the companion page — so the document
lands with no `artefact:` pointer and every check the vault runs looks straight past it.
An orphan is worse than a gap: the document is in the vault, so no acquisition line will
ever be raised for it, and no page can cite what nothing names.

**Both directions, one walk**, because job 108 asks for exactly that: a file no record
declares, and a declaration naming a file that is not there. They are the same parse, and
writing it twice is how the two answers come to disagree.

**The parse is the whole difficulty, and job 108 said so in advance.** `artefact:` takes a
bare name, a flow list (`[a.pdf, b.pdf]`) and a YAML block list, and filenames contain
commas — so a splitter reports false positives in every direction. This reads the key out
of the index, where `vault_lib`'s tolerant frontmatter parser has already resolved the
three forms; a re-implementation here would be a fourth reading of the same key.

**Undeclared is not the same as unreferenced, and the difference is most of the work.** Two
tests run over every artefact:

- **declared** — some record's `artefact:` key names it. This is what the vault's checks and
  the site's citation path use, so it is what reachability means.
- **named** — the basename appears in the text of some `.md` under `raw/` or `wiki/`. This
  is the looser test the 2026-09-12 measurement used, and a file that passes it is visible
  to a reader of that page while remaining invisible to every structured check.

An artefact failing both is the orphan those jobs were registered on. An artefact failing
only the first is a page whose key is missing — a repair, not a judgement — and putting the
two in one column would have sent 126 mechanical fixes to a read-and-judge queue.

**So each row carries a shape, and the shape is the disposition.** They are tested in the
order below, because the earlier ones subsume the later; `SHAPES` carries the same list
with what each one costs to put right.

- `text sidecar` — an undeclared `.txt` beside a declared artefact of the same stem: a
  working extract of a document that *is* held, not a document of its own. One convention
  ruling closes all of them.
- `key missing` — the record in the same directory names the file in its text, and its
  `artefact:` key does not. Add the key; the row carries the record and what cites it.
- `artefact misfiled` — a record in *another* shard names it. A declaration is a bare name
  taken beside the record, so no key repairs this: the file moves first.
- `named off-record` — only a wiki page names it. A wiki page is not a record and holds
  nothing, so the companion-or-delete call stands.
- `record beside it` — nothing names it, but a record of the same stem sits in the same
  directory. The `key missing` repair, found the other way round.
- `no record` — nothing names it and no record matches. **This is the companion-or-delete
  call, and it is OSINT's.**

**`budget-archive/`, `new-budget/` and `new/` are in these jobs' scope and not in Corpus's.**
The interface Corpus may read is `raw/`, `wiki/`, `lookups/` and the cycle manifest
(`CLAUDE.md` -> *The OSINT repo is read-only*), so this run covers `raw/`, and `--tree`
takes the others on OSINT's side. Saying so is better than a table that looks complete.

Usage:
  python artefact-uncited.py                                  # raw/, table to stdout
  python artefact-uncited.py --tree new                       # a tree Corpus cannot read
  python artefact-uncited.py --csv job-NN.csv                 # one CSV, every row
  python artefact-uncited.py --split job-108.csv job-109.csv  # 2026 first, then the rest
  python artefact-uncited.py --inverse                        # declarations with no file

Exit: 0 nothing undeclared, 1 rows found (the expected outcome while the jobs are open),
2 the tree or the index is not where the script was pointed.
"""
from __future__ import annotations

import argparse
import collections
import csv
import json
import os
import re
import sys
import urllib.parse

CITE_KEYS = ("sources", "cite_through")
# Stripped from a stem before two files are called the same document, so
# `x.ocr.txt`, `x.txt` and `x.pdf` all reduce to `x`. Everything here is a
# *conversion* suffix; a substantive one (`-annexe-1`, `-executive-summary`) is
# not, and two such files are two documents.
SIDECAR_SUFFIX_RE = re.compile(r"\.(ocr|txt|text|extract)$", re.I)
# The shapes below are a judgement about which artefacts are text *of* another
# artefact. A `.pdf` never is; it is the document.
SIDECAR_EXT = (".txt",)
# What may continue a filename. A match with one of these against either end is part of a
# longer name, so it is a different file — `brief.pdf` is not mentioned by a page that
# names `market-brief.pdf`. A space is *not* here: it is inside filenames but it is also
# what a declaration puts in front of one, and treating it as a boundary is what lets the
# scan see `artefact: 2026-07-11 Some Report.pdf` at all.
NAME_CHARS = set("abcdefghijklmnopqrstuvwxyz0123456789-_.")

BATCH_2026 = "2026"
# In the order they are tested, with what each one costs to put right. The gloss is the
# whole point of the column: four of the six are repairs, and only the last two are the
# read-and-judge call the jobs were registered as.
SHAPES = (
    ("text sidecar", "a text extract of a declared document — one convention ruling"),
    ("key missing", "the record beside it names it; add the `artefact:` key"),
    ("artefact misfiled", "a record in another shard names it; move it, then declare it"),
    ("named off-record", "a wiki page names it; no record holds it — companion or delete"),
    ("record beside it", "a record of the same stem; add the key to it"),
    ("no record", "nothing names it — companion or delete, and that call is yours"),
)
CSV_COLS = ["job", "shape", "artefact", "date", "bytes", "ext", "md5",
            "record", "record_path", "how", "citations",
            "in_catalogue", "title", "publisher", "published", "url", "twin"]
INVERSE_COLS = ["record_path", "declares", "resolves_to", "why"]

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


# ---------------------------------------------------------------- the tree

def artefacts(root, tree):
    """Every non-Markdown file under the tree — what a record holds rather than writes."""
    out = []
    for dirpath, _, filenames in os.walk(os.path.join(root, tree)):
        for fn in sorted(filenames):
            if not fn.lower().endswith(".md"):
                out.append(os.path.join(dirpath, fn).replace(os.sep, "/"))
    return out


def records(root, tree):
    """Every `.md` under the tree, as repo-relative paths."""
    out = set()
    for dirpath, _, filenames in os.walk(os.path.join(root, tree)):
        for fn in filenames:
            if fn.lower().endswith(".md"):
                out.add(os.path.relpath(os.path.join(dirpath, fn), root).replace(os.sep, "/"))
    return out


def stem(path):
    """The document a file belongs to, conversion suffixes removed."""
    return SIDECAR_SUFFIX_RE.sub("", os.path.splitext(path)[0])


# ------------------------------------------------------- the index, read once

def index_rows(index_dir):
    """Every Markdown row of `files.jsonl`, keyed by path.

    **Records only.** The index carries a row per *file*, so an artefact has a row of its
    own under the same slug as the record that holds it, with no frontmatter — reading
    those as records blanks the title for exactly the files named after their record.
    """
    out = {}
    with open(os.path.join(index_dir, "files.jsonl"), encoding="utf-8") as fh:
        for line in fh:
            row = json.loads(line)
            if row["d"].get("ext") == ".md":
                out[row["path"]] = row
    return out


def declared(rows):
    """artefact path -> [record path], from every form of the `artefact:` key.

    The key is resolved **relative to the record's own directory**, which is the form the
    vault writes: a bare name almost always, and once a `../budget-archive/...` reaching
    into a tree Corpus cannot see.
    """
    out = collections.defaultdict(list)
    for path, row in rows.items():
        value = (row["fm"] or {}).get("artefact")
        if value is None:
            continue
        for item in (value if isinstance(value, list) else [value]):
            name = str(item).strip()
            if not name:
                continue
            target = os.path.normpath(os.path.join(os.path.dirname(path), name))
            out[target.replace(os.sep, "/")].append(path)
    return out


def citations(index_dir):
    """slug -> the number of distinct pages that reach it.

    A page citing the same record twice is one citing page, and a record citing itself is
    not a citation — both would inflate what a repair or a retirement is worth.
    """
    seen, count = set(), collections.Counter()
    with open(os.path.join(index_dir, "links.jsonl"), encoding="utf-8") as fh:
        for line in fh:
            edge = json.loads(line)
            if edge["via"] not in CITE_KEYS and edge["via"] != "body":
                continue
            key = (edge["from"], edge["to"])
            if key in seen or edge["from"].endswith("/" + edge["to"] + ".md"):
                continue
            seen.add(key)
            count[edge["to"]] += 1
    return count


# ------------------------------------------------------------- the loose test

def named_by(root, pages, names):
    """basename -> the `.md` files whose text contains it.

    One pass over every page, not one search per artefact. Each page is scanned for the
    handful of extensions in use; at every hit the window ending there is looked up at each
    basename length seen for that extension, which is a dict lookup rather than a search.

    **The window is bounded at both ends, and without that the scan over-reports.** A
    filename is a suffix of a longer filename more often than it looks — `brief.pdf` ends
    `market-brief.pdf` — so a match whose neighbouring character could continue the name is
    a different file being mentioned, not this one. A space is a boundary even though
    filenames contain spaces: what is tested is the character the *text* puts against the
    match, and a declaration reads `artefact: 2026-07-11 Data-Center....pdf`.

    Percent-encoded forms are registered alongside the literal one. The vault holds no
    encoded reference today — `%20` and `quote()` find nothing the plain form does not —
    but a filename with a space reached through a Markdown link is one edit away, and a
    reference missed here is reported as an orphan.
    """
    forms = collections.defaultdict(set)
    for name in names:
        for form in {name.lower(),
                     urllib.parse.quote(name).lower(),
                     name.replace(" ", "%20").lower()}:
            forms[form].add(name)
    by_ext = collections.defaultdict(lambda: collections.defaultdict(set))
    for form in forms:
        by_ext[os.path.splitext(form)[1].lower()][len(form)].add(form)
    exts = sorted(by_ext)

    out = collections.defaultdict(set)
    for page_root in pages:
        for dirpath, _, filenames in os.walk(os.path.join(root, page_root)):
            for fn in filenames:
                if not fn.lower().endswith(".md"):
                    continue
                path = os.path.join(dirpath, fn)
                rel = os.path.relpath(path, root).replace(os.sep, "/")
                text = open(path, "rb").read().decode("utf-8", "replace").lower()
                for ext in exts:
                    i = text.find(ext)
                    while i != -1:
                        end = i + len(ext)
                        if end < len(text) and text[end] in NAME_CHARS:
                            i = text.find(ext, i + 1)
                            continue
                        for length, candidates in by_ext[ext].items():
                            window = text[end - length:end]
                            if end < length or window not in candidates:
                                continue
                            before = text[end - length - 1] if end > length else ""
                            if before in NAME_CHARS:
                                continue
                            for name in forms[window]:
                                out[name].add(rel)
                        i = text.find(ext, i + 1)
    return out


# --------------------------------------------------------------- the joins

def md5_index(root):
    """artefact path -> md5, from `lookups/artefact-md5-index.csv` if OSINT has built it.

    **Joined, never recomputed.** The digest is OSINT's own, written under job 106, and
    hashing 1,291 files to restate it would put a second answer to the same question in
    circulation. A missing file costs the column and nothing else.
    """
    path = os.path.join(root, "lookups", "artefact-md5-index.csv")
    if not os.path.isfile(path):
        return {}
    with open(path, encoding="utf-8-sig", newline="") as fh:
        return {r["artefact"]: r["md5"] for r in csv.DictReader(fh) if r.get("artefact")}


def catalogue(path):
    """slug -> the published row, so a repair can be read without opening the record.

    Corpus's own `outputs/catalogue/catalogue-internal.csv`. Membership is the check worth
    having: every `raw/` record is in the catalogue, so a record that is not is a finding
    in its own right rather than a blank cell.
    """
    if not path or not os.path.isfile(path):
        return {}
    with open(path, encoding="utf-8-sig", newline="") as fh:
        return {r["slug"]: r for r in csv.DictReader(fh) if r.get("slug")}


def slug_of(record_path):
    return os.path.splitext(os.path.basename(record_path))[0]


def file_date(path):
    """The date the filename claims, else the year of the shard it sits in."""
    m = re.match(r"(\d{4}-\d{2}-\d{2})", os.path.basename(path))
    if m:
        return m.group(1)
    m = re.search(r"/(\d{4})/", path)
    return m.group(1) if m else ""


# ---------------------------------------------------------------- the rows

def shape_of(path, tree, holds, names, record_files):
    """The disposition class, and the record the row attaches to.

    Returns `(shape, [record paths], how, twin)`. The order of the tests is the argument:
    a sidecar is a sidecar whether or not a page happens to mention it, and a page that
    names the file is a better answer than a stem that merely matches.

    **Where the naming page sits decides the repair, so it decides the shape.** A record in
    the same directory is a missing key and nothing more. A record in another shard cannot
    be repaired with a key at all, because a declaration is a bare name taken beside the
    record — the file has to move first. And a wiki page is not a record: it can name a
    document, but nothing in `raw/` holds it, so the companion-or-delete call stands.
    """
    twins = sorted(p for p in holds
                   if p != path and stem(p) == stem(path) and holds[p])
    if twins and os.path.splitext(path)[1].lower() in SIDECAR_EXT:
        return "text sidecar", holds[twins[0]], "declares the twin", twins[0]
    mentions = sorted(names.get(os.path.basename(path), ()))
    here = [p for p in mentions if os.path.dirname(p) == os.path.dirname(path)]
    if here:
        return "key missing", here, "named by the record beside it", ""
    in_tree = [p for p in mentions if p.startswith(tree + "/")]
    if in_tree:
        return "artefact misfiled", in_tree, "named by a record in another shard", ""
    if mentions:
        return "named off-record", mentions, "named by a page outside " + tree, ""
    sibling = stem(path) + ".md"
    if sibling in record_files:
        return "record beside it", [sibling], "same stem, nothing names it", ""
    return "no record", [], "", ""


def rows(root, tree, index_dir, pages, catalogue_path):
    idx = index_rows(index_dir)
    holds = declared(idx)
    cites = citations(index_dir)
    cat = catalogue(catalogue_path)
    digests = md5_index(root)
    found = artefacts(root, tree)
    record_files = records(root, tree)
    names = named_by(root, pages, {os.path.basename(p) for p in found})

    out = []
    for path in found:
        rel = os.path.relpath(path, root).replace(os.sep, "/")
        if holds.get(rel):
            continue
        shape, attached, how, twin = shape_of(rel, tree, holds, names, record_files)
        slugs = [slug_of(p) for p in attached]
        row = cat.get(slugs[0], {}) if slugs else {}
        date = file_date(rel)
        out.append({
            "job": "108" if date.startswith(BATCH_2026) else "109",
            "shape": shape,
            "artefact": rel,
            "date": date,
            "bytes": os.path.getsize(path),
            "ext": os.path.splitext(rel)[1].lower(),
            "md5": digests.get(rel, ""),
            "record": "; ".join(slugs),
            "record_path": "; ".join(attached),
            "how": how,
            # The cost of the repair, and the reason to make it: a record nothing cites is
            # holding evidence for nobody, and one cited forty times is a page the site
            # already sends readers to with the document missing from its own frontmatter.
            "citations": sum(cites.get(s, 0) for s in slugs),
            # Only a record is in the catalogue, and a wiki page is not a record — asking
            # the question of one gets `no` for a page that was never eligible, which reads
            # as a defect. Left blank instead, so a `no` here is always a real finding.
            "in_catalogue": (("yes" if slugs[0] in cat else "no")
                             if attached and attached[0].startswith(tree + "/") else ""),
            "title": row.get("title", ""),
            "publisher": row.get("publisher", ""),
            "published": row.get("published", ""),
            "url": row.get("url", ""),
            "twin": twin,
        })
    return out


def inverse(root, tree, index_dir):
    """The other direction: a declaration naming a file that is not beside the record.

    The diagnosis matters more than the count, because the three shapes are three
    different repairs and only one of them is a missing file:

    - **a path form.** The vault declares a bare name and resolves it beside the record;
      exactly one declaration spells a path instead, and neither resolution reads it as its
      author meant. Reported as its own shape rather than as an absence.
    - **elsewhere in the tree.** The named file exists under another shard — the record
      moved and its artefact did not, or the other way round. The repair is a move.
    - **absent.** Nothing of that name is anywhere Corpus may look. Job 108's two worked
      cases were files left behind in `new/`, which is outside the interface, so *absent
      here* is not the same as *gone*, and the row says which it is claiming.
    """
    holds = declared(index_rows(index_dir))
    elsewhere = collections.defaultdict(list)
    for path in artefacts(root, tree):
        elsewhere[os.path.basename(path)].append(os.path.relpath(path, root)
                                                 .replace(os.sep, "/"))
    out = []
    for target, sources in sorted(holds.items()):
        for record_path in sources:
            if not record_path.startswith(tree + "/"):
                continue
            if os.path.isfile(os.path.join(root, target)):
                continue
            name = os.path.relpath(target, os.path.dirname(record_path)).replace(os.sep, "/")
            found = elsewhere.get(os.path.basename(target), [])
            if "/" in name or "\\" in name:
                why = ("a path, not a bare name: it resolves to %s, and the vault's other "
                       "declarations are bare names taken beside the record" % target)
            elif found:
                why = "the file is under another shard: " + "; ".join(found)
            else:
                why = ("no file of that name under %s/ — Corpus cannot see `new/`, so this "
                       "claims absence here, not absence" % tree)
            out.append({"record_path": record_path,
                        "declares": name,
                        "resolves_to": target,
                        "why": why})
    return out


# ---------------------------------------------------------------- reporting

def write_csv(path, cols, rows_):
    with open(path, "w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        w.writerows(rows_)
    print("%d row(s) -> %s" % (len(rows_), path))


def report(tree, total, found):
    by_shape = collections.Counter(r["shape"] for r in found)
    by_job = collections.Counter(r["job"] for r in found)
    print("%s/: %d artefact(s), %d declared by no record\n" % (tree, total, len(found)))
    print("  job 108 (2026)      %4d" % by_job["108"])
    print("  job 109 (pre-2026)  %4d\n" % by_job["109"])
    for shape, gloss in SHAPES:
        if by_shape[shape]:
            print("  %-18s %4d   %s" % (shape, by_shape[shape], gloss))
    print()
    for r in found:
        if r["shape"] not in ("no record", "named off-record"):
            continue
        print("    %s  (%s bytes)" % (r["artefact"], f"{r['bytes']:,}"))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=".", help="the repository root (default: cwd)")
    ap.add_argument("--tree", default="raw", help="the tree to walk (default: raw)")
    ap.add_argument("--pages", default="raw,wiki",
                    help="trees whose Markdown may name an artefact (default: raw,wiki)")
    ap.add_argument("--index", default=None,
                    help="an index/ with files.jsonl and links.jsonl (default: <root>/index)")
    ap.add_argument("--catalogue", default=None,
                    help="catalogue-internal.csv (default: Corpus's own, if it is there)")
    ap.add_argument("--csv", default=None, help="write every row here")
    ap.add_argument("--split", nargs=2, metavar=("JOB108", "JOB109"),
                    help="write the 2026 rows and the rest to two files")
    ap.add_argument("--inverse", action="store_true",
                    help="report declarations whose file is not beside the record")
    ap.add_argument("--inverse-csv", default=None,
                    help="write those rows here (implies --inverse)")
    args = ap.parse_args(argv)

    root = os.path.abspath(args.root)
    if not os.path.isdir(os.path.join(root, args.tree)):
        print("no %s/ under %s" % (args.tree, root), file=sys.stderr)
        return 2
    index_dir = args.index or os.path.join(root, "index")
    if not os.path.isfile(os.path.join(index_dir, "files.jsonl")):
        print("no files.jsonl under %s -- build the index first" % index_dir, file=sys.stderr)
        return 2

    # `realpath`, not `abspath`: `scripts/` is itself a junction in the workroot, so an
    # unresolved parent lands on `scripts/.workroot/outputs`, which is not Corpus's.
    default_cat = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
                               "outputs", "catalogue", "catalogue-internal.csv")
    found = rows(root, args.tree, index_dir,
                 [p for p in args.pages.split(",") if p],
                 args.catalogue or default_cat)
    report(args.tree, len(artefacts(root, args.tree)), found)

    if args.inverse or args.inverse_csv:
        backwards = inverse(root, args.tree, index_dir)
        print("\n%d declaration(s) naming a file that is not beside the record" % len(backwards))
        for r in backwards:
            print("    %s\n        declares %s  (%s)" % (r["record_path"], r["declares"], r["why"]))
        if args.inverse_csv:
            write_csv(args.inverse_csv, INVERSE_COLS, backwards)

    if args.csv:
        write_csv(args.csv, CSV_COLS, found)
    if args.split:
        write_csv(args.split[0], CSV_COLS, [r for r in found if r["job"] == "108"])
        write_csv(args.split[1], CSV_COLS, [r for r in found if r["job"] == "109"])

    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
