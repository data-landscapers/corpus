#!/usr/bin/env python3
r"""shard_lib.py — the prefix-shard index: bucket postings by word prefix, split, write.

Two indexes are built on this and the catalogue page fetches from both:
`build-names-index.py` over the names occurring in source bodies, and
`build-title-index.py` over the titles and hero lines the catalogue itself holds.
It was written by lifting the machinery out of the first when the second appeared
— the same point at which `names_lib.py` was made, and for the same reason.

**What the two share is the shape, not the text.** Each is `text<TAB>ids` lines,
bucketed on the first two characters of every word, a fat bucket re-cut one
character deeper, and a manifest naming every shard written. What differs is how
the text is found and how it is split into words, so both of those are arguments.

Three properties the callers depend on, all of them load-bearing:

**Stable document ids.** Postings key on `outputs/catalogue/doc-ids.csv`, which is
append-only — a slug keeps its id forever. The obvious alternative, the row's
position in the catalogue, is wrong for a tracked artefact: rows sort by date
descending, so one new source shifts every index below it and rewrites every shard
on every cycle. Append-only ids mean a shard changes only when its own text
changes, which is what makes this affordable in git.

**Every word lands in exactly one shard at every width.** Words shorter than the
width are padded rather than dropped, so a split leaves no leftover bucket behind
and the page can walk the key list from longest to shortest knowing that no key is
a prefix of another.

**A promised shard exists.** `write_shards` fails the build on a shard named in
what it returns but absent from disk. That is not defensive coding: on Windows
`open("aux.txt", "w")` opens the AUX device, succeeds, and writes nothing, so a
write really can report success and produce no file. A missing shard is a search
that silently returns less rather than an error anyone would ever see.
"""
from __future__ import annotations

import collections
import csv
import gzip
from pathlib import Path

from names_lib import KEYSTOP, WORDKEY, shard_file

PREFIX = 2                 # shard key length
MIN_QUERY = 3              # the page will not search an index on fewer than this
SPLIT_BYTES = 120_000      # a shard past this is re-cut one character deeper (~40 KB gzipped)
MAX_WIDTH = 5              # ...but never deeper than this, or the shard count runs away


def doc_ids(path: Path, slugs, write: bool = True) -> dict[str, int]:
    """Append-only slug -> id. Existing ids are never reassigned; new slugs go on the end.

    `write=False` mints the new ids in memory and leaves the file alone. A `--check`
    or `--stats` run promises to write nothing, and this is a *tracked* registry —
    minting ids from a read-only probe dirties the working tree and quietly commits
    the numbering to whatever the vault happened to hold at the time.

    **Both builders may extend it and neither may renumber.** Whichever runs first
    mints the ids for slugs new since the last run; the other finds them already
    there. That is safe precisely because the file is append-only — the order two
    runs happen in can decide which numbers new slugs get, and nothing anywhere
    depends on which numbers those are, only on their never changing afterwards.
    """
    ids: dict[str, int] = {}
    if path.exists():
        with open(path, encoding="utf-8", newline="") as fh:
            for r in csv.DictReader(fh):
                ids[r["slug"]] = int(r["id"])
    nxt = max(ids.values()) + 1 if ids else 0
    fresh = [s for s in sorted(slugs) if s not in ids]
    for s in fresh:
        ids[s] = nxt
        nxt += 1
    if write and (fresh or not path.exists()):
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            w = csv.writer(fh, lineterminator="\n")
            w.writerow(["slug", "id"])
            for s, n in sorted(ids.items(), key=lambda kv: kv[1]):
                w.writerow([s, n])
    return ids


def line(text: str, docs: list[int]) -> str:
    """`Text<TAB>d,d,d` with ids delta-encoded — most postings become one or two digits."""
    out, prev = [], 0
    for d in docs:
        out.append(d - prev)
        prev = d
    return text + "\t" + ",".join(str(x) for x in out)


def key_of(word: str, width: int) -> str | None:
    """A word's shard key at a given width, or None where the word is not one to key on.

    A word nobody would ever search is a bad shard key and an expensive one: keying
    on `of` and `the` collects every text containing them into one bucket that no
    amount of re-cutting can split, because the word itself is too short to cut. The
    text stays reachable through its other words — and a *query* that opens with one
    of them reaches nothing, which is the cost, recorded where each index is built.
    """
    w = word.lower().strip(".,'’-")
    if not w or not w[0].isalpha() or w in KEYSTOP:
        return None
    k = (w + "__")[:width]
    return k if WORDKEY.match(k.replace("_", "a")) else None


# The bucket for text that no query prefix can reach through a word: 337 Arabic
# titles, and the handful whose every word is a stopword or a number. A key cannot
# contain a digit — `key_of` builds them out of `[a-z_]` — so this one can never
# collide with a real prefix, and the page falls back to it when a query yields no
# key of its own. Without it those records are searchable by facet and by nothing
# else, which is a silent hole rather than a visible one.
FALLBACK = "0"


def shard(post: dict, words=str.split, fallback: str | None = None,
          prefix: int = PREFIX, split_bytes: int = SPLIT_BYTES,
          max_width: int = MAX_WIDTH):
    """{text: [ids]} -> ({key: shard text}, [split keys], {text: line}).

    Iterative rather than one-shot: `co` re-cut at three characters still left a
    248 KB shard, because English prefixes are not uniformly distributed and one
    pass only moves the problem one letter along.

    `words` splits a text into the words it should be keyed on. Whitespace is right
    for a name; a title wants punctuation gone and its accents folded as well, or
    `e-Government` keys on `e-` and `Côte d'Ivoire` on `cô`, and both land nowhere.

    `fallback` collects the texts no word could key, under that one key. Passing
    None leaves them out of the index entirely, which is what the names build does:
    a name with no keyable word is a name nobody was going to type.
    """
    lines = {t: line(t, post[t]) for t in sorted(post)}

    def cut(members, width):
        """-> {key: texts} for these texts at this width."""
        b = collections.defaultdict(set)
        for t in members:
            for w in words(t):
                k = key_of(w, width)
                if k:
                    b[k].add(t)
        return b

    out, splits = {}, []

    def place(key, members, width):
        text = "\n".join(lines[t] for t in sorted(members))
        if len(text.encode("utf-8")) <= split_bytes or width >= max_width:
            out[key] = text
            return
        splits.append(key)
        for k2, m2 in cut(members, width + 1).items():
            if k2.startswith(key):
                place(k2, m2, width + 1)

    first = cut(lines, prefix)
    for k, members in first.items():
        place(k, members, prefix)
    if fallback is not None:
        keyed = set()
        for m in first.values():
            keyed |= m
        rest = [t for t in sorted(lines) if t not in keyed]
        if rest:
            out[fallback] = "\n".join(lines[t] for t in rest)
    return out, sorted(splits), lines


def write_shards(out_dir: Path, shards: dict, label: str) -> set:
    """Write, prune and verify a shard directory. Returns the keys actually kept."""
    out_dir.mkdir(parents=True, exist_ok=True)
    keep = set()          # shard KEYS, not filenames — the page looks a query up by key
    for k, text in shards.items():
        if not text:
            continue
        keep.add(k)
        p = out_dir / shard_file(k)
        new = text + "\n"
        # Only rewrite a shard that actually changed — the whole point of stable ids
        # is that most shards are byte-identical between cycles, and rewriting them
        # anyway would put the churn straight back into git.
        if p.exists() and p.read_text(encoding="utf-8") == new:
            continue
        p.write_text(new, encoding="utf-8", newline="\n")
    # Prune against the exact **filenames** wanted, not against the keys they decode to.
    # Deciding by key kept a stray `aux.txt` alive, because it decodes to the key `aux`
    # which is genuinely wanted — so the unopenable leftover of the device-name bug was
    # preserved by the very loop meant to clear it, and git then choked on a directory
    # entry nothing can read.
    want_files = {shard_file(k) for k in keep}
    for stale in out_dir.glob("*.txt"):
        if stale.name in want_files:
            continue
        try:
            stale.unlink()
        except OSError as exc:
            # A reserved-name entry cannot be opened *or* deleted by its plain path.
            # Say so precisely, with the command that works, rather than failing the
            # build on something no rebuild can fix.
            print(f"{label}: could not delete {stale.name} ({exc}). If it is a Windows "
                  f"device name, remove it with:  del \\\\?\\{stale.resolve()}")

    missing = sorted(k for k in keep if not (out_dir / shard_file(k)).is_file())
    if missing:
        raise SystemExit(f"{label}: {len(missing)} shard(s) named in the manifest were not "
                         f"written to disk: {', '.join(missing[:10])}")
    return keep


def profile(shards: dict) -> dict:
    """Gzipped size profile — what a reader actually pays, per query and in total."""
    sizes = sorted(len(gzip.compress(t.encode("utf-8"), 9)) for t in shards.values() if t)
    if not sizes:
        return {}
    n = len(sizes)
    return {"files": n, "total": sum(sizes), "median": sizes[n // 2],
            "mean": sum(sizes) / n, "p90": sizes[int(n * 0.9)], "max": sizes[-1]}
