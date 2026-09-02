#!/usr/bin/env python3
r"""
lint-external-links.py — does every link that leaves the site open in a new tab?

**The rule** (`documentation/house-style.md` → *Links*): an anchor whose host is
outside `chrome_lib.INTERNAL_HOSTS` carries `target="_blank" rel="noopener"`; one
that stays on the site carries neither. `chrome_lib.external_links()` applies it
as a post-pass over each finished page.

**Why a linter and not just the post-pass.** The post-pass is a function a builder
has to remember to call, and there are nine call sites. That is the shape
`chrome_lib`'s own header warns about — the header that was written out five times
and fixed in four. A tenth builder gets written, ships without the call, and the
pages it writes are wrong in a way no diff shows: `target` is one attribute among
fifty thousand anchors, and its absence looks exactly like a page nobody edited.

So this asserts the outcome on the built tree, where the answer cannot be argued
with, and asserts the mechanism in the scripts, where the answer arrives a render
earlier.

**Both directions are failures.** An outbound link that keeps the tab costs a
reader their place mid-report. An inbound one that opens a tab spawns a window
every time somebody clicks the masthead logo. A linter that only checked the first
would let the site drift into the second while reporting itself clean.

**What is deliberately not flagged.** An anchor whose `href` is built in
JavaScript — the catalogue's result rows, `datatable.js`'s source column — is a
string concatenation rather than a URL, and both already set their own `target`.
An anchor that *states* `target="_self"` on an outbound link is honoured for the
same reason `external_links()` honours it: an emitter that says so should be
believed, and a linter that overrode it would make the attribute meaningless.

**The URL test runs before the template test, and the order is the whole of it.**
Written the other way round, a first draft of this file skipped any href holding a
`+` or an apostrophe as JavaScript — and 221 published source links have one, from
`Maroc+Telecom+-+Rapport+financier` to `Rapport annuel sur l'Inclusion`. It
reported clean over every one of them. A linter that quietly declines to look at
part of its input is worse than no linter, because it is also a claim that it
looked, so anything shaped like a URL is classified as a URL and the template test
only ever sees what is left.

Usage:  python scripts/lint-external-links.py [--site PATH] [--quiet]
Exit:   0 clean, 1 a page or a script is wrong.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

CORPUS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(CORPUS / "scripts"))
from chrome_lib import INTERNAL_HOSTS  # noqa: E402

A_TAG = re.compile(r"<a\b[^>]*>", re.I)
HREF = re.compile(r"""\bhref\s*=\s*(?:"([^"]*)"|'([^']*)')""", re.I)
TARGET = re.compile(r"\btarget\s*=", re.I)
URL = re.compile(r"(?i)^(?:https?:)?//([^/?#]+)")

# An href that names somewhere on this site rather than a URL: a site-absolute
# path, a fragment, a relative path or a bare filename.
INTERNAL_SHAPE = re.compile(r"^(?:[/#.]|[A-Za-z0-9_][A-Za-z0-9._-]*(?:[/?#]|$))")

# A quote or a brace inside an attribute value the emitters wrote means the value
# is a JavaScript expression: a real href carrying one arrives as `&#39;` or
# `&quot;`. `+` is *not* a marker — it is ordinary in a query string, and treating
# it as one is the bug the header describes.
TEMPLATE = re.compile(r"""['"{}`]""")


def classify(href: str) -> str:
    """`external`, `internal`, or `skip` for an href that is not a link at all.

    A URL is settled by its host and nothing else — see the header on why that test
    comes first. Only what does not parse as one reaches the template test."""
    u = href.strip()
    m = URL.match(u)
    if m:
        host = m.group(1).split("@")[-1].split(":")[0].lower()
        return "internal" if host in INTERNAL_HOSTS else "external"
    if u.lower().startswith(("mailto:", "tel:", "javascript:", "data:")):
        return "skip"                       # opens no tab, or opens nothing
    if TEMPLATE.search(u):
        return "skip"                       # a JavaScript expression, not an href
    return "internal" if INTERNAL_SHAPE.match(u) else "skip"


def check_pages(site: Path) -> tuple[list[str], int, int]:
    """Every anchor in the built tree, against the rule."""
    problems: list[str] = []
    ext = internal = 0
    for page in sorted(site.rglob("*.html")):
        # Named relative to the repo where it is under it, and in full where it is
        # not — `--site` takes any tree, and a crash on one outside Corpus would
        # make the option unusable from a test or a staging build.
        try:
            rel = page.relative_to(CORPUS).as_posix()
        except ValueError:
            rel = page.as_posix()
        bare: list[str] = []
        tabbed: list[str] = []
        for m in A_TAG.finditer(page.read_text(encoding="utf-8", errors="replace")):
            tag = m.group(0)
            h = HREF.search(tag)
            if h is None:
                continue
            url = h.group(1) if h.group(1) is not None else h.group(2)
            kind = classify(url)
            has = bool(TARGET.search(tag))
            if kind == "external":
                ext += 1
                if not has:
                    bare.append(url)
            elif kind == "internal":
                internal += 1
                if has:
                    tabbed.append(url)
        if bare:
            problems.append(f"{rel}: {len(bare)} outbound link(s) with no target — "
                            f"first is {bare[0][:90]}")
        if tabbed:
            problems.append(f"{rel}: {len(tabbed)} link(s) that stay on the site open a "
                            f"new tab — first is {tabbed[0][:90]}")
    return problems, ext, internal


# A builder is anything importing the site chrome and writing a file. If it writes
# a page it must put that page through the post-pass; `chrome_lib` itself is where
# the post-pass lives, and the tests exercise it directly.
EXEMPT = {"chrome_lib.py", "lint-external-links.py", "test_external_links.py"}


def check_builders(scripts: Path) -> list[str]:
    """The mechanism, a render earlier than the outcome."""
    problems: list[str] = []
    for src in sorted(scripts.glob("*.py")):
        if src.name in EXEMPT:
            continue
        text = src.read_text(encoding="utf-8", errors="replace")
        if "chrome_lib" not in text or "write_text" not in text:
            continue
        if "external_links" not in text:
            problems.append(f"scripts/{src.name}: builds pages from chrome_lib and writes "
                            f"them without external_links() — see house-style.md -> Links")
    return problems


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--site", default=str(CORPUS / "site"))
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args()

    site = Path(a.site)
    if not site.is_dir():
        print(f"lint-external-links: no site tree at {site}")
        return 1

    page_problems, ext, internal = check_pages(site)
    build_problems = check_builders(CORPUS / "scripts")
    problems = build_problems + page_problems

    if not a.quiet:
        pages = sum(1 for _ in site.rglob("*.html"))
        print(f"lint-external-links: {pages} page(s), {ext:,} outbound and "
              f"{internal:,} on-site link(s)")
        print(f"  this site: {', '.join(sorted(INTERNAL_HOSTS))}")
    for p in problems:
        print(f"  WRONG  {p}")
    if not problems and not a.quiet:
        print("  ok — every outbound link opens a new tab, every on-site link does not")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
