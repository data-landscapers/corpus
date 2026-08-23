#!/usr/bin/env python3
"""test_leak_check.py — prove the leak gate fires.

A gate that has only ever passed is not evidence of anything. Run after any
change to `leak-check.py`:

    python scripts/test_leak_check.py

*(Was `test_pull.py`, which tested the same eight cases against the copy of the
gate inside `scripts/pull.py`. That pull was retired by the 2026-08-13 migration
and the script deleted on 2026-08-16, so the test was proving a gate nothing ran.
It now runs against `leak-check.py`, which is the gate BUILD and RENDER actually
invoke — `scan()` returns findings rather than raising, so a clean tree is an
empty list.)*
"""

from __future__ import annotations

import importlib.util
import json
import shutil
import sys
import tempfile
from pathlib import Path

# leak-check.py is hyphenated, so it cannot be imported by name.
_spec = importlib.util.spec_from_file_location(
    "leak_check", Path(__file__).resolve().parent / "leak-check.py")
leak_check = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(leak_check)
scan = leak_check.scan

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


CLEAN_HTML = ("<html><body><p>Kenya has a data-protection statute in force since 2019.</p>"
              "</body></html>")
LEAKED_HTML = "<html><body><p>" + ("the verbatim text of someone else's article " * 400) + "</p></body></html>"


def cache_cases() -> int:
    """Prove the verdict cache saves work without ever letting a fault through.

    Added 2026-08-23 with the cache itself. A cache on a **gate** is the one kind of optimisation
    that can turn a check into a formality, so the properties worth holding are not about speed:
    an entry may only be opened by identical bytes, a file that moves must be scanned again, and
    an edit to the gate must throw the lot away. The speed follows from those and needs no test.
    """
    failures = 0
    results: list[tuple[str, bool, str]] = []

    def case(name: str, ok: bool, detail: str = "") -> None:
        nonlocal failures
        failures += not ok
        results.append((name, ok, detail))

    tmp = Path(tempfile.mkdtemp(prefix="gate-cache-test-"))
    try:
        page = tmp / "reports" / "KEN" / "KEN-status.html"
        page.parent.mkdir(parents=True, exist_ok=True)

        # 1. a clean page is scanned once and remembered
        page.write_text(CLEAN_HTML, encoding="utf-8")
        clean: dict = {}
        first = scan(tmp, clean)
        remembered = len(clean)
        second = scan(tmp, clean)
        case("a clean page is scanned once and remembered",
             not first and not second and remembered == 1 and len(clean) == 1,
             f"{remembered} entry after the first scan, {len(clean)} after the second")

        # 2. the same path with different bytes is a different key, so it is scanned again
        page.write_text(LEAKED_HTML, encoding="utf-8")
        found = scan(tmp, clean)
        case("a page that changes is scanned again and its fault is caught",
             bool(found), found[0] if found else "the gate stayed silent")

        # 3. only identical bytes open an entry — stated as a test because it is the trust
        #    boundary the whole cache rests on
        planted = {leak_check.file_digest(page): "2026-08-23"}
        case("an entry is opened by content identity and nothing else",
             not scan(tmp, planted),
             "a planted digest for these exact bytes skips them, as designed")

        # 4. an edit to the gate throws every entry away
        leak_check.CACHE = tmp / "cache.json"
        leak_check.save_cache({"abc": "2026-08-23"})
        kept = leak_check.load_cache()
        stale = json.loads(leak_check.CACHE.read_text(encoding="utf-8"))
        stale["rules"] = "0000000000000000"
        leak_check.CACHE.write_text(json.dumps(stale), encoding="utf-8")
        dropped = leak_check.load_cache()
        case("an edit to the gate drops every entry",
             kept == {"abc": "2026-08-23"} and dropped == {},
             f"held {len(kept)} under its own rules, {len(dropped)} under another's")

        # 5. csv and markdown are never cached, so they are read in full every run
        page.unlink()
        (tmp / "ledger.csv").write_text("system,body\neCitizen,short text\n", encoding="utf-8")
        clean = {}
        a, b = scan(tmp, clean), scan(tmp, clean)
        case("csv and markdown are never cached and are refused every time",
             bool(a) and bool(b) and not clean,
             f"{len(clean)} cached entr(ies) after two scans of a faulty csv")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    for name, ok, detail in results:
        print(f"  {'ok  ' if ok else 'FAIL'} {name}")
        if detail:
            print(f"       {detail}")
    return failures


def run() -> int:
    failures = 0
    for name, files, should_pass in CASES:
        tmp = Path(tempfile.mkdtemp(prefix="gate-test-"))
        try:
            for rel, content in files.items():
                p = tmp / rel
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(content, encoding="utf-8")

            findings = scan(tmp)
            passed = not findings
            detail = findings[0].strip() if findings else ""

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

    failures += cache_cases()
    total = len(CASES) + 5

    print()
    if failures:
        print(f"{failures} of {total} cases FAILED")
        return 1
    print(f"all {total} cases passed")
    return 0


if __name__ == "__main__":
    sys.exit(run())
