#!/usr/bin/env python3
r"""names_lib.py — extracting names from source prose, and naming the files they go in.

Three readers now share this: `build-names-index.py` (the searchable index),
`build-entity-names.py` (display names for entity slugs) and `catalogue.py` (which
only needs the filename rules). It was duplicated across the first two before the
third appeared, which is the point at which duplication stops being cheaper than a
module.

**The extraction is deliberately conservative.** It takes runs of capitalised words,
allowing the particles that glue names together (`of`, `de`, `van`), and then trims
grammatical filler and calendar words off both ends. It will miss lowercase names and
it will admit some phrases that are not names at all. That is the right trade for a
search index, where a false positive costs a line in a shard and a false negative
costs a document nobody can find.

**Tables and frontmatter are stripped first, and that is not an optimisation.** The
first pass at this indexed the finance records' column headers: `Value`, `Financier`,
`Amount`, `Deal ID` and `Status` were among the most frequent "names" in the corpus.
"""
from __future__ import annotations

import re

# Grammatical filler, calendar words, and the finance records' column vocabulary —
# the last of these survives the table strip when a driver writes a field on its own
# line, so it is trimmed by name.
STOP = set("""the a an and but or if for in on at to of by with from as is was are were be been
it this that these those he she they we you his her their our your there here when where
while after before during since until because however although also not no yes its which who
what how why then than both each other some many most more less new two three one
mr mrs dr prof according speaking meanwhile additionally furthermore moreover therefore thus
read see photo image source share follow subscribe advertisement monday tuesday wednesday
thursday friday saturday sunday january february march april may june july august september
october november december value field amount status start end notes total percent recipient
financier beneficiary instrument commitment enrichment definite active""".split())
# `first` and `second` are deliberately absent: they open a sentence often enough to
# look like filler, but they open a company name more usefully — trimming them turned
# `first-capital-bank-botswana` into "Capital Bank Botswana", which is a different bank.

# Never used as a shard key or scored as a distinguishing token. Wider than STOP,
# because the particles inside a name — `de`, `van`, `della` — are legitimate parts
# of it and must not be trimmed, but are useless to key on or to match against.
KEYSTOP = STOP | set("""de du da do das dos del della di la le les el al van von der den
bin ibn af av ter ten und y e o a i""".split())

# Legal-form words: present in a slug, absent from how anyone writes the name, and
# vice versa. Neither side should be penalised for them.
LEGAL = set("""ltd limited plc inc incorporated corp corporation co company group holdings
holding sa nv bv ag gmbh llc spa srl pty the""".split())

NAME = re.compile(r"([A-Z][\w&.'’-]*(?:\s+(?:of|for|and|de|du|da|la|le|des|van|von|the)?"
                  r"\s*[A-Z][\w&.'’-]*){0,5})")
FENCE = re.compile(r"```.*?```", re.S)
TABLE = re.compile(r"(?m)^\s*\|.*$")
FMLINE = re.compile(r"(?m)^[a-z_]+:\s.*$")
WORDKEY = re.compile(r"^[a-z]+$")

MIN_NAME, MAX_NAME = 4, 60          # the extraction cap the leak gate checks against

# Windows reserves these as device names, **with any extension** — `open("aux.txt", "w")`
# opens the AUX device, succeeds, and writes nothing to disk. A shard keyed `aux` was
# therefore never written while the manifest went on promising it, and the fault
# surfaced three steps downstream as `git add` failing on a file that did not exist.
# The escape applies to the *filename* only; keys are `[a-z_]+`, so `aux-` cannot
# collide with a real one, and the manifest and the page still speak in bare keys.
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
    """Every distinct name-shaped run in a source's prose."""
    out = set()
    for m in NAME.finditer(body(text)):
        s = clean(m.group(1))
        if not s:
            continue
        words = s.split()
        if len(words) == 1 and (s.lower() in STOP or len(s) < 5):
            continue
        out.add(s)
    return out


def clean(raw: str) -> str:
    """Trim a candidate to the name itself: filler off both ends, possessive off the tail."""
    s = " ".join(raw.split())
    s = re.sub(r"[’']s$", "", s)
    words = s.split()
    while words and words[0].lower() in STOP:
        words = words[1:]
    while words and words[-1].lower() in STOP:
        words = words[:-1]
    s = " ".join(words).strip(" .,;:'’")
    return s if MIN_NAME <= len(s) <= MAX_NAME else ""


def tokens(s: str) -> list[str]:
    """Lowercase word tokens, punctuation dropped — the comparable form of a name or slug."""
    return [t for t in re.split(r"[^a-z0-9]+", s.lower()) if t]


def initials(words: list[str]) -> str:
    return "".join(w[0] for w in words if w)
