#!/usr/bin/env python3
"""test_maturity_words.py — R130's substitution, and no maturity writer carrying the old words.

Strategic review 7, R136. The second half is the guard the register asked for: a writer that
still carries *Not held* would write it back on its next study night, and `lint-prose.py` would
fail that night's gate. It reads every `study-*.py`, `study_*.py` and the two maturity site
scripts with `lint-prose.py`'s own word list.

    python scripts/test_maturity_words.py
"""
from __future__ import annotations

import glob
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import maturity_words as mw  # noqa: E402

_spec = importlib.util.spec_from_file_location("lint_prose", os.path.join(HERE, "lint-prose.py"))
lp = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(lp)

failed = 0


def check(name, got, want):
    global failed
    if got != want:
        failed += 1
        print(f"  FAIL  {name}\n        got:  {got!r}\n        want: {want!r}")


def words(text: str) -> list[str]:
    return [m.group(0) for rx in lp.WORDS for m in rx.finditer(text)]


# --- the substitution ---------------------------------------------------------------------------
CASES = [
    ("***Not held***. Clinic shares.", "***Not found***. Clinic shares."),
    ("***Noted, not assessed***. None held.", "***Also on file***. None found."),
    ("Nothing held names a backup site.", "Nothing found names a backup site."),
    ("No source held since October 2023 says so.", "No source found since October 2023 says so."),
    ("No figure for 2023 or later is held.", "No figure for 2023 or later has been found."),
    ("No measured results are held.", "No measured results have been found."),
    ("A switch ran in 2024; volumes are not known.", "A switch ran in 2024; no source found reports volumes."),
    ("Fibre ran by 2020; whether it reaches every region is not known.",
     "Fibre ran by 2020; no source found says whether it reaches every region."),
    ("A plan was adopted, but its results are not known.",
     "A plan was adopted, but no source found reports its results."),
    ("Elections were held in May.", "Elections were held in May."),
]
for old, new in CASES:
    check(f"rewrite: {old}", mw.rewrite(old), new)
    check(f"idempotent: {new}", mw.rewrite(new), new)
    check(f"no old words left: {new}", words(mw.rewrite(old)), [])

check("the closing labels are the ruled words", mw.CLOSING, ("***Also on file***", "***Not found***"))

# --- the writers --------------------------------------------------------------------------------
writers = sorted(glob.glob(os.path.join(HERE, "study-*.py")) + glob.glob(os.path.join(HERE, "study_*.py"))
                 + [os.path.join(HERE, f) for f in ("maturity-site.py", "maturity-render.py", "lint-study.py")])
for path in writers:
    with open(path, encoding="utf-8") as fh:
        hits = words(fh.read())
    check(f"{os.path.basename(path)} carries none of R130's old words", hits, [])

if failed:
    print(f"test_maturity_words: {failed} failed")
    sys.exit(1)
print("test_maturity_words: ok")
