#!/usr/bin/env python3
"""test_pull.py — prove the leak gate fires.

A gate that has only ever passed is not evidence of anything. Run after any
change to pull.py's gate:

    python build/test_pull.py
"""

from __future__ import annotations

import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pull import Leak, leak_gate  # noqa: E402

CLEAN_MD = """---
title: Kenya — status report
compiled: 2026-08-06
place: KEN
---

# Kenya: status report

Kenya has a data-protection statute in force since 2019.
"""

SOURCE_MD = """---
type: source
title: Some article
publisher: A newspaper
body_completeness: full
---

The verbatim text of somebody else's article, which must never reach Corpus.
"""

CASES: list[tuple[str, dict[str, str], bool]] = [
    (
        "clean tree passes",
        {
            "reports/KEN/KEN-status.md": CLEAN_MD,
            "reports/KEN/ledger.csv": "system,status,note\neCitizen,Implemented,"
            + "a compiled analytical note. " * 60,          # ~1.6k, under prose cap
            "catalogue/raw-catalogue.csv": "slug,title,url,body_completeness\n"
            "a,Some title,https://example.org,excerpt\n",
            "reports/KEN/considered.txt": "2026-01-01-some-slug\n" * 50,
        },
        True,
    ),
    (
        "raw/ source page is refused",
        {"reports/KEN/KEN-status.md": CLEAN_MD, "leaked.md": SOURCE_MD},
        False,
    ),
    (
        "csv body column is refused",
        {"catalogue/raw-catalogue.csv": "slug,title,body\na,T,short text\n"},
        False,
    ),
    (
        "long value in an ordinary column is refused",
        {"reports/KEN/ledger.csv": "system,status\neCitizen," + "x" * 1200 + "\n"},
        False,
    ),
    (
        "long value in a prose column is allowed up to its cap",
        {"finance/x-nonstate.csv": "id,description\n1," + "y" * 3300 + "\n"},
        True,
    ),
    (
        "prose column beyond its cap is refused",
        {"finance/x-nonstate.csv": "id,description\n1," + "y" * 9000 + "\n"},
        False,
    ),
    (
        "json body key is refused",
        {"catalogue/raw-catalogue.json": '[{"slug":"a","body":"short"}]'},
        False,
    ),
    (
        "a path under raw/ is refused",
        {"raw/2026/2026-01-01 something.md": "anything at all"},
        False,
    ),
]


def run() -> int:
    failures = 0
    for name, files, should_pass in CASES:
        tmp = Path(tempfile.mkdtemp(prefix="gate-test-"))
        try:
            for rel, content in files.items():
                p = tmp / rel
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(content, encoding="utf-8")
            try:
                leak_gate(tmp)
                passed = True
                detail = ""
            except Leak as exc:
                passed = False
                detail = str(exc).splitlines()[-1].strip()

            ok = passed == should_pass
            failures += not ok
            verdict = "ok  " if ok else "FAIL"
            expected = "pass" if should_pass else "refuse"
            print(f"  {verdict} {name}  (expected {expected})")
            if not ok and detail:
                print(f"       gate said: {detail}")
            elif ok and not passed:
                print(f"       refused on: {detail}")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    print()
    if failures:
        print(f"{failures} of {len(CASES)} cases FAILED")
        return 1
    print(f"all {len(CASES)} cases passed")
    return 0


if __name__ == "__main__":
    sys.exit(run())
