#!/usr/bin/env python3
r"""build-names-index.py — the searchable index of names occurring in source bodies.

    python scripts/build-names-index.py            write outputs/names/
    python scripts/build-names-index.py --check     report drift, write nothing
    python scripts/build-names-index.py --stats     size profile, write nothing

Stage 3 of `documentation/catalogue-search.md`. The catalogue's search box reaches
titles, publishers and entity tags; this reaches the **names that occur in the
sources themselves**, so a reader can find the document that mentions a person or
a company nobody tagged.

**What is published is an index, not a text.** Each shard is a list of
`name<TAB>document-ids` — no word order, no sentences, no offsets, nothing from
which prose could be reconstructed, and the page never renders a snippet. Bill
ruled on 2026-08-24 that publishing an index of names is not a licensing or
copyright problem; `design.md` §8's "the boundary that matters is bodies, not
internal reasoning" is the reasoning it was given on. **The line is the snippet**:
match-or-no-match is publishable, an extract is the body in fragments.

Three things this file is careful about.

**Stable document ids.** Postings key on ids from `outputs/catalogue/doc-ids.csv`,
which is append-only — a slug keeps its id forever. The obvious alternative, the
row's position in the catalogue, is wrong for a *tracked* artefact: rows sort by
publication date descending, so one new source shifts every index below it and
rewrites all 800 shards on every cycle. Append-only ids mean a shard changes only
when its own names change, which is what makes this affordable in git.

**Bounded fetches, not a bounded index.** Shards are keyed on the first two
characters of *every word* in a name, so "Cassava Technologies" is reachable from
both `ca` and `te`. A prefix whose shard grows past `SPLIT_BYTES` is re-cut at
three characters and named in the manifest's `splits`, so the page knows to use a
longer key. The page never searches names on fewer than three characters, which
is what makes that safe.

**Tables and frontmatter are not prose.** The first pass at this indexed the
finance records' column headers — `Value`, `Financier`, `Amount`, `Deal ID` were
among the most frequent "names" in the corpus. Fences, pipe tables and stray
frontmatter lines are stripped before extraction.

The raw root resolves through `scripts/.workroot/` like every other vault reader.
`CORPUS_RAW` overrides it, on the same reasoning as `status_lib.EXCHANGE`'s
`CORPUS_OSINT_XFER`: a path that may move should not need a code change.
"""
from __future__ import annotations

import argparse
import collections
import csv
import glob
import gzip
import io
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vault_lib as V                                                # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(V.ROOT)
RAW = Path(os.environ.get("CORPUS_RAW") or (ROOT / "raw"))
CATALOGUE = ROOT / "outputs" / "catalogue" / "raw-catalogue.json"
DOC_IDS = ROOT / "outputs" / "catalogue" / "doc-ids.csv"
OUT_DIR = ROOT / "outputs" / "names"
MANIFEST = OUT_DIR / "manifest.json"

PREFIX = 2                 # shard key length
MIN_QUERY = 3              # the page will not search names on fewer than this
SPLIT_BYTES = 120_000      # a shard past this is re-cut one character deeper (~40 KB gzipped)
MAX_WIDTH = 5              # ...but never deeper than this, or the shard count runs away

# Grammatical filler and calendar words, which are capitalised constantly and name
# nothing. Also the finance records' column vocabulary, which survives the table
# strip when a driver writes a field on its own line.
STOP = set("""the a an and but or if for in on at to of by with from as is was are were be been
it this that these those he she they we you his her their our your there here when where
while after before during since until because however although also not no yes its which who
what how why then than both each other some many most more less new two three one first second
mr mrs dr prof according speaking meanwhile additionally furthermore moreover therefore thus
read see photo image source share follow subscribe advertisement monday tuesday wednesday
thursday friday saturday sunday january february march april may june july august september
october november december value field amount status start end notes total percent recipient
financier beneficiary instrument commitment enrichment definite active""".split())

# Never used as a shard key. Wider than STOP, because the particles that glue
# names together — `de`, `van`, `della` — are legitimate parts of a name and must
# not be trimmed off it, but are useless to key on.
KEYSTOP = STOP | set("""de du da do das dos del della di la le les el al van von der den
bin ibn af av ter ten und y e o a i""".split())

NAME = re.compile(r"([A-Z][\w&.'’-]*(?:\s+(?:of|for|and|de|du|da|la|le|des|van|von|the)?"
                  r"\s*[A-Z][\w&.'’-]*){0,5})")
FENCE = re.compile(r"```.*?```", re.S)
TABLE = re.compile(r"(?m)^\s*\|.*$")
FMLINE = re.compile(r"(?m)^[a-z_]+:\s.*$")
WORDKEY = re.compile(r"^[a-z]+$")

# Windows reserves these as device names, **with any extension** — `open("aux.txt", "w")`
# opens the AUX device, succeeds, and writes nothing to disk. So a shard keyed `aux` was
# silently never written while the manifest went on promising it, and the fault surfaced
# three steps downstream as `git add` failing on a file that did not exist. A key is
# escaped with a trailing hyphen in its *filename* only; keys are `[a-z_]+`, so `aux-`
# cannot collide with a real one. The manifest and the page still speak in bare keys.
# (COM1-9 and LPT1-9 are reserved too, but keys carry no digits.)
WIN_RESERVED = {"con", "prn", "aux", "nul"}


def shard_file(key: str) -> str:
    return (key + "-" if key in WIN_RESERVED else key) + ".txt"


def shard_key(filename: str) -> str:
    stem = filename[:-4] if filename.endswith(".txt") else filename
    return stem[:-1] if stem.endswith("-") else stem


def body(text: str) -> str:
    """Prose only — frontmatter, fenced blocks and pipe tables removed."""
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            text = text[end + 4:]
    return FMLINE.sub(" ", TABLE.sub(" ", FENCE.sub(" ", text)))


def names_in(text: str) -> set[str]:
    out = set()
    for m in NAME.finditer(body(text)):
        s = " ".join(m.group(1).split())
        words = s.split()
        while words and words[0].lower() in STOP:
            words = words[1:]
        while words and words[-1].lower() in STOP:
            words = words[:-1]
        if not words:
            continue
        s = " ".join(words)
        if not (4 <= len(s) <= 60):
            continue
        if len(words) == 1 and (s.lower() in STOP or len(s) < 5):
            continue
        out.add(s)
    return out


def doc_ids(slugs: list[str]) -> dict[str, int]:
    """Append-only slug -> id. Existing ids are never reassigned; new slugs go on the end."""
    ids: dict[str, int] = {}
    if DOC_IDS.exists():
        with open(DOC_IDS, encoding="utf-8", newline="") as fh:
            for r in csv.DictReader(fh):
                ids[r["slug"]] = int(r["id"])
    nxt = max(ids.values()) + 1 if ids else 0
    fresh = [s for s in sorted(slugs) if s not in ids]
    for s in fresh:
        ids[s] = nxt
        nxt += 1
    if fresh or not DOC_IDS.exists():
        DOC_IDS.parent.mkdir(parents=True, exist_ok=True)
        with open(DOC_IDS, "w", encoding="utf-8", newline="\n") as fh:
            w = csv.writer(fh, lineterminator="\n")
            w.writerow(["slug", "id"])
            for s, n in sorted(ids.items(), key=lambda kv: kv[1]):
                w.writerow([s, n])
    return ids


def harvest(items, ids):
    """name -> sorted list of stable document ids."""
    post: dict[str, list[int]] = collections.defaultdict(list)
    missing = 0
    for it in items:
        rel = it.get("path") or ""
        if not rel.startswith("raw/"):
            continue
        fp = RAW / rel[len("raw/"):]
        if not fp.exists():
            missing += 1
            continue
        did = ids[it["slug"]]
        try:
            text = fp.read_text(encoding="utf-8", errors="replace")
        except OSError:
            missing += 1
            continue
        for s in names_in(text):
            post[s].append(did)
    for v in post.values():
        v.sort()
    return post, missing


def line(name: str, docs: list[int]) -> str:
    """`Name<TAB>d,d,d` with ids delta-encoded — most postings become one or two digits."""
    out, prev = [], 0
    for d in docs:
        out.append(d - prev)
        prev = d
    return name + "\t" + ",".join(str(x) for x in out)


def key_of(word: str, width: int) -> str | None:
    """A word's shard key at a given width.

    Words shorter than the width are **padded**, not dropped, so that every word
    lands in exactly one shard at every width and a split leaves no leftover
    bucket behind. Without that, splitting `sa` would strand the names whose only
    `sa` word is two characters long, and the page would have to fetch both the
    short shard and the long one to be sure it had seen them.
    """
    w = word.lower().strip(".,'’-")
    if not w or not w[0].isalpha() or w in KEYSTOP:
        # A word nobody would ever search is a bad shard key and an expensive one:
        # keying on `of` and `the` collected every name containing them into one
        # bucket that no amount of re-cutting could split, because the word itself
        # is too short to cut. The name stays reachable through its other words.
        return None
    k = (w + "__")[:width]
    return k if WORDKEY.match(k.replace("_", "a")) else None


def shard(post):
    """Bucket by word prefix, re-cutting any bucket that is still too fat.

    Iterative rather than one-shot: `co` re-cut at three characters still left a
    248 KB shard, because English prefixes are not uniformly distributed and one
    pass only moves the problem one letter along.
    """
    lines = {n: line(n, post[n]) for n in sorted(post)}

    def cut(members, width):
        """-> {key: names} for these names at this width."""
        b = collections.defaultdict(set)
        for n in members:
            for w in n.split():
                k = key_of(w, width)
                if k:
                    b[k].add(n)
        return b

    out, splits = {}, []

    def place(key, members, width):
        text = "\n".join(lines[n] for n in sorted(members))
        if len(text.encode("utf-8")) <= SPLIT_BYTES or width >= MAX_WIDTH:
            out[key] = text
            return
        splits.append(key)
        for k2, m2 in cut(members, width + 1).items():
            if k2.startswith(key):
                place(k2, m2, width + 1)

    for k, members in cut(lines, PREFIX).items():
        place(k, members, PREFIX)
    return out, sorted(splits), lines


def write(shards, splits, stats):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    keep = set()          # shard KEYS, not filenames — the page looks a query up by key
    for k, text in shards.items():
        if not text:
            continue
        keep.add(k)
        p = OUT_DIR / shard_file(k)
        new = text + "\n"
        # Only rewrite a shard that actually changed — the whole point of stable
        # ids is that most shards are byte-identical between cycles, and rewriting
        # them anyway would put the churn straight back into git.
        if p.exists() and p.read_text(encoding="utf-8") == new:
            continue
        p.write_text(new, encoding="utf-8", newline="\n")
    # Prune against the exact **filenames** wanted, not against the keys they decode to.
    # Deciding by key kept a stray `aux.txt` alive, because it decodes to the key `aux`
    # which is genuinely wanted — so the unopenable leftover of the device-name bug was
    # preserved by the very loop meant to clear it, and git then choked on a directory
    # entry nothing can read.
    want_files = {shard_file(k) for k in keep}
    for stale in OUT_DIR.glob("*.txt"):
        if stale.name in want_files:
            continue
        try:
            stale.unlink()
        except OSError as exc:
            # A reserved-name entry cannot be opened *or* deleted by its plain path.
            # Say so precisely, with the command that works, rather than failing the
            # build on something no rebuild can fix.
            print(f"names: could not delete {stale.name} ({exc}). If it is a Windows "
                  f"device name, remove it with:  del \\\\?\\{stale.resolve()}")

    # **Every promised shard must exist on disk.** A manifest is a promise the page
    # acts on, and the AUX bug proved that a write can report success and produce
    # nothing — so the promise is checked rather than assumed. This is cheap and it
    # fails the build, because a missing shard is a search that silently returns
    # less rather than an error anyone would see.
    missing = sorted(k for k in keep if not (OUT_DIR / shard_file(k)).is_file())
    if missing:
        raise SystemExit(f"names: {len(missing)} shard(s) named in the manifest were not "
                         f"written to disk: {', '.join(missing[:10])}")
    MANIFEST.write_text(json.dumps({
        "built": stats["built"],
        "prefix": PREFIX,
        "min_query": MIN_QUERY,
        "splits": splits,
        "shards": sorted(keep),
        "names": stats["names"],
        "postings": stats["postings"],
        "documents": stats["documents"],
        "note": "Index of names occurring in source bodies. Name -> document ids, "
                "delta-encoded; ids resolve through outputs/catalogue/doc-ids.csv. "
                "No word order, no offsets, no text. Derived by "
                "scripts/build-names-index.py; do not edit.",
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    return keep


def profile(shards):
    sizes = sorted(len(gzip.compress(t.encode("utf-8"), 9)) for t in shards.values() if t)
    if not sizes:
        return {}
    n = len(sizes)
    return {"files": n, "total": sum(sizes), "median": sizes[n // 2],
            "mean": sum(sizes) / n, "p90": sizes[int(n * 0.9)], "max": sizes[-1]}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true", help="report drift, write nothing")
    ap.add_argument("--stats", action="store_true", help="size profile, write nothing")
    a = ap.parse_args()

    if not CATALOGUE.exists():
        print(f"names: no catalogue at {CATALOGUE} — run scripts/build-catalogue.py first")
        return 1
    if not RAW.exists():
        print(f"names: no raw/ at {RAW} — run from scripts/.workroot/, or set CORPUS_RAW")
        return 1

    doc = json.loads(CATALOGUE.read_text(encoding="utf-8"))
    items = doc["items"] if isinstance(doc, dict) and "items" in doc else doc
    ids = doc_ids([i["slug"] for i in items])
    post, missing = harvest(items, ids)
    shards, splits, lines = shard(post)
    stats = {"built": doc.get("built", ""), "names": len(post),
             "postings": sum(len(v) for v in post.values()), "documents": len(items) - missing}

    if a.check:
        if not MANIFEST.exists():
            print(f"names: not written yet ({len(post):,} names would be)")
            return 1
        held = json.loads(MANIFEST.read_text(encoding="utf-8"))
        drift = len(post) - held.get("names", 0)
        print(f"names: {held.get('names', 0):,} written {held.get('built')}, "
              f"{len(post):,} in the vault ({drift:+,})")
        return 0 if drift == 0 else 1

    p = profile(shards)
    if a.stats:
        print(f"names: {len(post):,} names, {stats['postings']:,} postings, "
              f"{stats['documents']:,} documents")
        print(f"  {p['files']} shards, {p['total']/1e6:.2f} MB gzipped on the server")
        print(f"  per query: median {p['median']/1024:.1f} KB  mean {p['mean']/1024:.1f} KB  "
              f"p90 {p['p90']/1024:.1f} KB  max {p['max']/1024:.1f} KB")
        print(f"  {len(splits)} prefix(es) re-cut at {PREFIX+1} chars: {', '.join(splits) or 'none'}")
        return 0

    keep = write(shards, splits, stats)
    if missing:
        print(f"names: {missing:,} catalogue records had no readable body — skipped")
    print(f"names: {len(post):,} names over {stats['documents']:,} documents -> outputs/names/")
    print(f"  {len(keep)} shards, {p['total']/1e6:.2f} MB gzipped; per query "
          f"median {p['median']/1024:.1f} KB, p90 {p['p90']/1024:.1f} KB, max {p['max']/1024:.1f} KB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
