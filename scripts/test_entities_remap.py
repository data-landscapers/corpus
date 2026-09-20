#!/usr/bin/env python3
r"""test_entities_remap.py — one line changes, or nothing does and it says why.

    python scripts/test_entities_remap.py

`entities-remap.py` rewrites frontmatter in OSINT's tree (housekeeping job 105), so the
things worth pinning are the ways a rewrite goes wrong quietly:

- **The file, byte for byte.** CRLF, a missing trailing newline, a byte-order mark, key
  order, quoting — every one of them survives, because a corpus-wide pass that flipped
  line endings would be found later by a diff of hundreds of files and blamed on anything.
- **The refusals.** A block list, a bare scalar, a doubled key, a value carrying something
  other than `[slug]` items: each is skipped with a reason. A rewrite that interpreted one
  of these would drop the part it could not read, and the record would still look fine.
- **The body is not the frontmatter.** A prose line beginning `entities:` is someone
  else's words.
- **The de-duplication.** A record carrying both a variant and the canonical must end with
  one tag, not the same tag twice.
- **The ruling is a flag.** `--canonical` has to be one of the group's own slugs, or a
  typo would invent a tag instead of settling one.
"""
from __future__ import annotations

import importlib.util
import sys
import tempfile
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "entities_remap", Path(__file__).resolve().parent / "entities-remap.py")
er = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(er)

MAP = {"ncc-nigeria": "ncc", "nigerian-communications-commission": "ncc"}
fails = []


def check(name, got, want):
    ok = got == want
    print(f"  {'ok  ' if ok else 'FAIL'} {name}")
    if not ok:
        print(f"        got  {got!r}\n        want {want!r}")
        fails.append(name)


def doc(entities_line, eol="\n", bom="", tail="\n"):
    body = ("---%s"
            "type: source%s"
            "title: 'A record'%s"
            "%s%s"
            "published: 2026-01-01%s"
            "---%s"
            "%s"
            "entities: this line is prose and must not move%s"
            % (eol, eol, eol, entities_line, eol, eol, eol, eol, eol))
    return bom + body + ("" if tail is None else "")


# -- the rewrite -----------------------------------------------------------

print("the one line that changes")
text = doc("entities: [[mtn-group], [ncc-nigeria]]")
new, did, why = er.rewrite(text, MAP)
check("the variant is replaced", (did, why), (True, None))
check("and only that line moves", er.verify(text, new, "x"), None)
# The first match only: the fixture deliberately carries a *second* `entities:` line in
# the body, which the next check is about.
check("the canonical flow form is rebuilt",
      next(ln for ln in new.split("\n") if ln.startswith("entities:")),
      "entities: [[mtn-group], [ncc]]")
check("the prose line beginning `entities:` is untouched",
      new.split("\n")[-2], "entities: this line is prose and must not move")

text = doc("entities: [[ncc], [mtn-group]]")
check("a file already canonical is left alone", er.rewrite(text, MAP)[:2], (text, False))

text = doc("entities: [[ncc], [ncc-nigeria], [mtn-group]]")
new, did, _ = er.rewrite(text, MAP)
check("a record carrying both ends with one tag, not two",
      [ln for ln in new.split("\n") if ln.startswith("entities:")][0],
      "entities: [[ncc], [mtn-group]]")


# -- the bytes -------------------------------------------------------------

print("\nwhat survives a rewrite")
crlf = doc("entities: [[ncc-nigeria]]", eol="\r\n")
new, did, _ = er.rewrite(crlf, MAP)
check("CRLF endings are preserved", (did, new.count("\r\n")), (True, crlf.count("\r\n")))
check("  …including on the line that changed", "entities: [[ncc]]\r" in new.split("\n"),
      True)

bommed = doc("entities: [[ncc-nigeria]]", bom="﻿")
new, did, why = er.rewrite(bommed, MAP)
check("a byte-order mark is read past, not refused", (did, why), (True, None))
check("  …and kept", new.startswith("﻿"), True)

no_tail = doc("entities: [[ncc-nigeria]]").rstrip("\n")
new, did, _ = er.rewrite(no_tail, MAP)
check("a missing trailing newline stays missing", new.endswith("\n"), False)


# -- the refusals ----------------------------------------------------------

print("\nwhat it refuses rather than guesses")
for label, line, reason in (
        ("a block list", "entities:\n  - ncc-nigeria",
         "entities value is not the one-line flow form"),
        ("a bare scalar", "entities: ncc-nigeria",
         "entities value is not the one-line flow form"),
        ("an unbracketed item in the list", "entities: [[mtn-group], ncc-nigeria]",
         "entities value carries something other than [slug] items"),
):
    check(label, er.rewrite(doc(line), MAP)[2], reason)

check("a doubled key",
      er.rewrite(doc("entities: [[ncc-nigeria]]\nentities: [[ncc]]"), MAP)[2],
      "entities key appears 2 times")
check("no frontmatter at all",
      er.rewrite("just a body naming [ncc-nigeria]\n", MAP)[2], "no frontmatter")
check("frontmatter without the key",
      er.rewrite("---\ntitle: x\n---\n\nbody\n", MAP)[2], "no entities key")


# -- the verifier ----------------------------------------------------------

print("\nthe verifier is not a formality")
before = doc("entities: [[ncc-nigeria]]")
check("a second changed line is caught",
      er.verify(before, before.replace("type: source", "type: other")
                .replace("[ncc-nigeria]", "[ncc]"), "x"),
      "x: 2 lines changed, expected 1")
check("a dropped line is caught",
      er.verify(before, "\n".join(before.split("\n")[1:]), "x"),
      "x: line count changed")


# -- the map ---------------------------------------------------------------

print("\nthe ruling, as a flag")
with tempfile.TemporaryDirectory() as tmp:
    path = Path(tmp) / "m.csv"
    path.write_text("slug,records,proposed_canonical\n"
                    "ncc,101,ncc\nncc-nigeria,12,ncc\n"
                    "nigerian-communications-commission,6,ncc\n", encoding="utf-8")
    pairs, target = er.read_map(str(path))
    check("the proposal is read from the file", target, "ncc")
    pairs, target = er.read_map(str(path), "nigerian-communications-commission")
    check("--canonical overrides it", target, "nigerian-communications-commission")
    check("  …and every variant points at it",
          sorted({b for _, b in pairs}), ["nigerian-communications-commission"])
    try:
        er.read_map(str(path), "ncc-nigéria")
        check("a canonical outside the group is refused", "no refusal", "a refusal")
    except SystemExit as exc:
        check("a canonical outside the group is refused",
              str(exc).startswith("--canonical ncc-nigéria is not one of"), True)

print()
if fails:
    print("%d FAILED: %s" % (len(fails), ", ".join(fails)))
    sys.exit(1)
print("all checks passed")
