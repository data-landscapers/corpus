#!/usr/bin/env python3
"""test_lint_external_links.py — prove the linter fails where it should.

A linter that only ever passes is indistinguishable from one that has stopped
looking, and this one nearly shipped in exactly that state: its first draft
skipped any href holding a `+` or an apostrophe as a JavaScript template, which
is 221 published source links, and reported clean over all of them. So the cases
below are mostly failures — a synthetic page built to be wrong, checked to see
that it is caught, and one real URL of each awkward shape.

    python scripts/test_lint_external_links.py
"""

from __future__ import annotations

import importlib.util
import io
import sys
import tempfile
from contextlib import redirect_stdout
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))
_spec = importlib.util.spec_from_file_location(
    "lint_external_links", SCRIPTS / "lint-external-links.py")
lint = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(lint)

failures: list[str] = []


def check(label, got, want):
    ok = got == want
    print(f"  {'ok  ' if ok else 'FAIL'} {label}")
    if not ok:
        print(f"       got  {got!r}\n       want {want!r}")
        failures.append(label)


def run(page_html: str) -> tuple[int, str]:
    """The page checks, over a one-page site tree. Returns (exit code, output)."""
    with tempfile.TemporaryDirectory() as td:
        site = Path(td) / "site"
        site.mkdir()
        (site / "index.html").write_text(page_html, encoding="utf-8")
        buf = io.StringIO()
        with redirect_stdout(buf):
            problems, _, _ = lint.check_pages(site)
        for p in problems:
            print(p)
        return (1 if problems else 0), " ".join(problems)


print("classify settles a URL by its host, before anything else looks at it")
check("a plain source link", lint.classify("https://itweb.africa/a"), "external")
check("a query string full of pluses",
      lint.classify("https://www.times.co.sz/business/readmore.php?x=FinTech+Strategy+to+transform"),
      "external")
check("an apostrophe in the path",
      lint.classify("https://www.bkam.ma/Rapport%20annuel%20sur%20l'Inclusion.pdf"), "external")
check("a plus in the filename",
      lint.classify("https://www.iam.ma/documents/Maroc+Telecom+-+Rapport.pdf"), "external")
check("the corpus host", lint.classify("https://corpus.data-landscapers.io/finance/"), "internal")
check("the main site", lint.classify("https://data-landscapers.io/portfolio/"), "internal")
check("a lookalike host", lint.classify("https://data-landscapers.io.evil.test/"), "external")
check("a relative path", lint.classify("ZAF-nonstate-2026-09-01.csv"), "internal")
check("a fragment", lint.classify("#top"), "internal")
check("mailto opens no tab", lint.classify("mailto:bill@example.com"), "skip")
check("a JavaScript row template", lint.classify("' + r[6] + '"), "skip")

print()
print("a page that breaks the rule fails, in both directions")
rc, out = run('<a href="https://itweb.africa/a">source</a>')
check("an outbound link with no target exits 1", rc, 1)
check("...and says which", "no target" in out, True)

rc, out = run('<a href="https://corpus.data-landscapers.io/finance/" target="_blank">F</a>')
check("an on-site link that opens a tab exits 1", rc, 1)
check("...and says so the other way round", "stay on the site" in out, True)

rc, out = run('<a href="https://data-landscapers.io/" target="_blank">logo</a>')
check("the main site counts as on-site here too", rc, 1)

rc, out = run('<a href="index.html" target="_blank">next</a>')
check("so does a relative link", rc, 1)

print()
print("a page that keeps it passes")
rc, _ = run('<a href="https://itweb.africa/a" target="_blank" rel="noopener">s</a>'
            '<a href="https://corpus.data-landscapers.io/finance/">F</a>'
            '<a href="#top">top</a><a href="mailto:b@e.test">mail</a>')
check("exit 0", rc, 0)

rc, _ = run("""<script>h += '<a href="' + r[6] + '" target="_blank">' + t + '</a>';</script>""")
check("a JavaScript row template is not a finding", rc, 0)

rc, _ = run('<a href="https://itweb.africa/a" target="_self">deliberate</a>')
check("a stated target=_self is believed", rc, 0)

print()
print("the builder check catches the emitter that forgot the call")
with tempfile.TemporaryDirectory() as td:
    d = Path(td)
    (d / "chrome_lib.py").write_text("INTERNAL_HOSTS = set()\n", encoding="utf-8")
    (d / "good.py").write_text(
        "from chrome_lib import chrome, external_links\n"
        "p.write_text(external_links(doc))\n", encoding="utf-8")
    (d / "forgot.py").write_text(
        "from chrome_lib import chrome, foot\n"
        "p.write_text(doc)\n", encoding="utf-8")
    (d / "not_a_builder.py").write_text("import json\nx = 1\n", encoding="utf-8")
    found = lint.check_builders(d)
    check("one finding", len(found), 1)
    check("and it names the right script", "forgot.py" in found[0], True)

print()
print("the shipped tree and the shipped scripts are clean")
check("no builder is missing the call", lint.check_builders(SCRIPTS), [])
problems, ext, internal = lint.check_pages(SCRIPTS.parent / "site")
check("no page breaks the rule", problems, [])
check("and it looked at every outbound link (none skipped)", ext > 55_000, True)

print()
if failures:
    print(f"FAILED: {len(failures)} case(s) — {', '.join(failures)}")
    sys.exit(1)
print("all cases pass")
