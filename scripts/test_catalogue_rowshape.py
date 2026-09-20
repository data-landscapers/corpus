#!/usr/bin/env python3
"""test_catalogue_rowshape.py — the row's field numbering, read out of the source.

    python scripts/test_catalogue_rowshape.py

A catalogue row is a positional array of twelve fields, and it is built and read in
four places that must agree on what each position means: `pack_rows` packs it,
`row_html` draws it at build time, `split` projects four of its fields into the row
chunks, and the page's own `rowOf` reassembles it from the filter index and a chunk
before `rowHTML` draws it again. Two of those are Python and two are JavaScript
inside the same file.

**The existing cross-check needs node, and node is not everywhere.**
`test_catalogue_firstscreen.py` lifts `rowHTML` out of the built page and runs it
against `row_html`'s own output, which is the real proof — and it *skips* where node
is absent, which is where a renumbering gets made. This is the part of that proof
that can be had from the text alone: not that the two draw the same markup, but that
they read the same positions. It was written when `lens` came out of the row and the
seven fields above it shifted down by one (strategic review 4, R34a), with no way to
run the JS.

Three invariants, all read by parsing `scripts/catalogue.py`:

1. **`row_html` and `rowHTML` index the same positions.** They are line-for-line
   transliterations of each other; a position read by one and not the other is a
   field one of them has stopped drawing.
2. **`rowOf` returns as many slots as `pack_rows` packs.** A dropped or added field
   on either side is a silent off-by-one for every field after it.
3. **The chunk projection and `rowOf` agree slot for slot.** `split` writes four row
   fields into each chunk row; `rowOf` puts `t[0]`..`t[3]` back at four slots. The
   nth field `split` writes has to land at the slot `rowOf` fills from `t[n]`, or
   every row on the page draws another row's URL under its own title.
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parent / "catalogue.py"

fails = []


def check(name, got, want):
    ok = got == want
    print(f"  {'ok  ' if ok else 'FAIL'} {name}")
    if not ok:
        print(f"       got  {got}\n       want {want}")
        fails.append(name)


def block(text, start, end):
    """The source between a start marker and the first `end` marker after it."""
    i = text.index(start)
    j = text.index(end, i + len(start))
    return text[i:j]


def indices(text, var):
    """Every `{var}[N]` position the block reads, as a sorted set."""
    return sorted({int(n) for n in re.findall(rf"\b{var}\[(\d+)\]", text)})


src = SRC.read_text(encoding="utf-8")

print("the catalogue row's field numbering")

py_draw = block(src, "def row_html(", "def opts_html(")
js_draw = block(src, "  function rowHTML(r){", "  function rowText(i){")
check("row_html and rowHTML read the same positions",
      indices(py_draw, "r"), indices(js_draw, "r"))

# `pack_rows` packs one row as a list literal: count its top-level elements by the
# commas that end a line, which is how the literal is written.
pack = block(src, "    rows = [[", "    ] for i in items]")
packed = [ln for ln in pack.splitlines()[1:]
          if ln.strip() and not ln.strip().startswith("#")]
js_of = block(src, "  function rowOf(i, t){", "\n  }")
# `rowOf`'s slots, by the commas at depth 0 of its returned array literal.
ret = js_of[js_of.index("return [") + len("return ["):js_of.rindex("]")]
depth, slots = 0, 1
for ch in ret:
    if ch in "([{":
        depth += 1
    elif ch in ")]}":
        depth -= 1
    elif ch == "," and depth == 0:
        slots += 1
check("rowOf returns as many slots as pack_rows packs", slots, len(packed))

# The chunk projection: `[r[a], r[b], r[c], r[d]] + e` in `split`, against the slots
# `rowOf` fills from `t[0]`..`t[3]`.
proj = re.search(r"chunks\.append\(\[\[(.*?)\] \+ e", src).group(1)
written = [int(n) for n in re.findall(r"r\[(\d+)\]", proj)]
# Which slot of `rowOf`'s array each `t[n]` sits at.
at = {}
depth, slot = 0, 0
for m in re.finditer(r"[(\[{]|[)\]}]|,|t\[(\d+)\]", ret):
    tok = m.group(0)
    if tok in "([{":
        depth += 1
    elif tok in ")]}":
        depth -= 1
    elif tok == "," and depth == 0:
        slot += 1
    elif tok.startswith("t[") and depth == 0:
        at[int(m.group(1))] = slot
check("the chunk projection lands where rowOf reads it",
      written, [at.get(n) for n in range(len(written))])

print("\n" + ("test_catalogue_rowshape: ok - the four readings of a row agree"
              if not fails else f"test_catalogue_rowshape: {len(fails)} FAILED"))
sys.exit(1 if fails else 0)
