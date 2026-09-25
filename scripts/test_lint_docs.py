#!/usr/bin/env python3
"""test_lint_docs.py — the reader rule and its caps (strategic review 5, R86).

    python scripts/test_lint_docs.py

Runs on temporary files and a temporary cap table; touches nothing real.
"""
from __future__ import annotations
import contextlib, importlib.util, io, os, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("lint_docs", os.path.join(HERE, "lint-docs.py"))
ld = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ld)
failed = 0

TABLE = """| reader | class | `type:` values | cap |
|---|---|---|---|
| cc | runbook | runbook, procedure | 10 words |
| cc | spec | spec, doc | 20 words |
| bill | preamble | any | 8 words |
| bill | block | any | 6 words |
| bill | annotation | any | 4 words |
"""


def case(name, ok):
    global failed
    print(f"  {'ok  ' if ok else 'FAIL'} {name}")
    failed += not ok


with tempfile.TemporaryDirectory() as tmp:
    caps = os.path.join(tmp, "caps.md")
    open(caps, "w", encoding="utf-8").write(TABLE)
    files = {
        "ok-runbook.md": "---\ntype: runbook\nreader: cc\n---\none two three\n```\n" + "x " * 50 + "\n```\n",
        "long-runbook.md": "---\ntype: procedure\nreader: cc\n---\n" + "word " * 11,
        "no-reader.md": "---\ntype: spec\n---\nshort\n",
        "no-class.md": "---\ntype: essay\nreader: cc\n---\nshort\n",
        "osint-style.md": "<!-- reader: cc; type: runbook -->\n# Pass\n" + "word " * 12,
        "bill-ok.md":"<!-- reader: bill -->\n# Title\nfive words in the preamble\n## Part\n- a short bullet here\n",
        "bill-long.md": "---\nreader: bill\n---\none two three four five six seven eight nine\n## Part\n"
                        "- one two three four five six seven\n- *Done 2026-09-25: one two three four five.*\n",
    }
    for name, text in files.items():
        open(os.path.join(tmp, name), "w", encoding="utf-8").write(text)
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        code = ld.main(["--root", tmp, "--glob", "*.md", "--caps", caps])
    o = out.getvalue()
    case("a breach exits 1", code == 1)
    case("fenced code is not counted", "ok-runbook.md" not in o)
    case("a cc file over its class cap fails", "long-runbook.md: 11 words, over the cc runbook cap of 10" in o)
    case("a missing reader fails", "no-reader.md: no `reader:" in o)
    case("a cc type in no class fails", "no-class.md: reader cc, `type: essay` is in no class" in o)
    case("a first-line reader comment is read", "bill-ok.md" not in o)
    case("the comment form carries type: too", "osint-style.md: 14 words, over the cc runbook cap of 10" in o)
    case("a bill preamble over its cap fails", "bill-long.md: preamble 9 words" in o)
    case("a bill block over its cap fails", "bill-long.md: block of 7 words" in o)
    case("a register annotation over its cap fails", "bill-long.md: annotation of 7 words" in o)
    with contextlib.redirect_stdout(io.StringIO()):
        case("--report exits 0", ld.main(["--root", tmp, "--glob", "*.md", "--caps", caps, "--report"]) == 0)
    open(caps, "w", encoding="utf-8").write("no table here\n")
    with contextlib.redirect_stdout(io.StringIO()):
        case("an unreadable cap table exits 2", ld.main(["--root", tmp, "--caps", caps]) == 2)
    with contextlib.redirect_stdout(io.StringIO()):
        case("the real cap table in global-claude.md parses", bool(ld.load_caps(ld.CAPS)[0]))

print("\nall cases pass" if not failed else f"\n{failed} case(s) FAILED")
sys.exit(1 if failed else 0)
