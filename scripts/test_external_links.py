#!/usr/bin/env python3
"""test_external_links.py — prove outbound anchors get a new tab and inbound ones do not.

The rule is applied as a post-pass over a finished page (`chrome_lib.external_links`),
so a case it gets wrong is wrong on every page at once, in both directions: an internal
link that opens a tab spawns one on every click of the masthead logo, and an outbound
link that does not is the defect this was written to fix. Neither is visible in a diff
of 55,000 anchors, so the cases are asserted here instead.

    python scripts/test_external_links.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from chrome_lib import MAIN_SITE, SITE_BASE, external_links, is_external  # noqa: E402

failures: list[str] = []


def check(label, got, want):
    ok = got == want
    print(f"  {'ok  ' if ok else 'FAIL'} {label}")
    if not ok:
        print(f"       got  {got!r}\n       want {want!r}")
        failures.append(label)


print("outbound links open in a new tab")
check("a source link gets target and rel",
      external_links('<a href="https://techafricanews.com/x">t</a>'),
      '<a href="https://techafricanews.com/x" target="_blank" rel="noopener">t</a>')
check("so does a protocol-relative one",
      external_links('<a href="//cdn.example.com/a">x</a>'),
      '<a href="//cdn.example.com/a" target="_blank" rel="noopener">x</a>')
check("the attribute goes last, after the ones already there",
      external_links('<a class="ttl" href="https://x.io/a">x</a>'),
      '<a class="ttl" href="https://x.io/a" target="_blank" rel="noopener">x</a>')
check("trailing whitespace in the tag is not carried into it",
      external_links('<a href="https://x.io/a" >x</a>'),
      '<a href="https://x.io/a" target="_blank" rel="noopener">x</a>')
check("an existing rel is merged rather than replaced",
      external_links('<a rel="license" href="https://creativecommons.org/x">c</a>'),
      '<a rel="license noopener" href="https://creativecommons.org/x" target="_blank">c</a>')
check("noopener is not doubled",
      external_links('<a rel="noopener" href="https://x.io/a">x</a>'),
      '<a rel="noopener" href="https://x.io/a" target="_blank">x</a>')

print()
print("inbound links stay in the tab")
for href in (f"{SITE_BASE}/countries/", f"{MAIN_SITE}/", f"{MAIN_SITE}/portfolio/",
             "index.html", "../assets/x.css", "#top", "mailto:bill@example.com",
             "ZAF-nonstate-2026-09-01.csv"):
    tag = f'<a href="{href}">x</a>'
    check(f"untouched: {href}", external_links(tag), tag)

print()
print("a stated target is believed")
for tag in ('<a href="https://x.io/a" target="_blank" rel="noopener">x</a>',
            '<a href="https://x.io/a" target="_self">x</a>'):
    check("left as written", external_links(tag), tag)

print()
print("an href built in JavaScript is not an attribute and is not touched")
js = """h += '<p class="ttl"><a href="' + r[6] + '" target="_blank" rel="noopener">'"""
check("the catalogue's row template survives verbatim", external_links(js), js)

print()
print("is_external, on its own")
check("the corpus host is internal", is_external(f"{SITE_BASE}/x"), False)
check("the main site is internal", is_external(f"{MAIN_SITE}/x"), False)
check("www of the main site is internal", is_external("https://www.data-landscapers.io/"), False)
check("a lookalike host is not", is_external("https://data-landscapers.io.evil.test/"), True)
check("a userinfo trick does not smuggle one past", is_external("https://evil.test@data-landscapers.io/"), False)
check("...and the other way round is external",
      is_external("https://data-landscapers.io@evil.test/"), True)
check("case and port are ignored", is_external("HTTPS://Corpus.Data-Landscapers.IO:443/x"), False)
check("a bare path is not external", is_external("finance.html"), False)

print()
print("whole documents")
page = (f'<a href="{MAIN_SITE}/" class="site-logo">L</a>'
        '<p>See <a href="https://itweb.africa/a">the report</a> and '
        f'<a href="{SITE_BASE}/finance/">Finance</a>.</p>')
out = external_links(page)
check("one anchor changed, two did not", out.count('target="_blank"'), 1)
check("the logo still opens in place", f'<a href="{MAIN_SITE}/" class="site-logo">' in out, True)
check("running it twice changes nothing more", external_links(out), out)

print()
if failures:
    print(f"FAILED: {len(failures)} case(s) — {', '.join(failures)}")
    sys.exit(1)
print("all cases pass")
