#!/usr/bin/env python3
r"""
copy_lib.py — the reader-facing prose, kept in markdown rather than in Python.

**Every explanatory paragraph the site shows a reader lives in `content/`**
*(Bill, 2026-08-19)*, one file per page type, each holding named blocks under `##`
headings. The builders ask for a block by name and get HTML back:

    from copy_lib import copy
    intro = copy("country", "finance-intro", name="South Africa")

The reason is editorial rather than architectural. The wording of these blocks is
the part of the site most in need of revision and the part hardest to revise,
because it was distributed across eight scripts as string constants, HTML entities
and all, where changing a sentence meant reading Python to find it. Prose in a
markdown file can be read end to end and edited as prose. Nothing about the build
needed this; the person writing the sentences did.

## The file format

    ## key-name
    The paragraph, in markdown. Blank line between paragraphs, as usual.

    A second paragraph belongs to the same key until the next `##`.

    ## another-key
    ...

Anything above the first `##` is a comment for whoever is editing and is never
rendered — use it to say what the file is for.

## Placeholders

A block may carry `{name}` placeholders, filled by keyword argument:

    ## finance-intro
    Every non-state commitment the base holds for {name}.

**Values must arrive pre-formatted.** `{total:,.0f}` is not available: a format
spec inside the prose puts presentation logic back in the file we just took it out
of, and the failure mode is a `ValueError` at build time in a file the editor
thinks is plain text. Format the number in Python and pass the string.

A `{` that is not a placeholder must be doubled `{{`, as in `str.format` — this
comes up in almost nothing, because CSS and JS do not belong in prose.

## What this deliberately does not do

**No default, no fallback, no empty string on a missing key.** A block that cannot
be found raises, and the build stops. A page that quietly renders without its
explanatory paragraph is a page that looks finished and is not, and the whole point
of the move is that these paragraphs are the ones nobody notices are wrong.

**Two outputs, because there are two kinds of page.** `copy()` returns HTML, for
the builders that write HTML directly. `copy_md()` returns the block's markdown
untouched, for `report-render.py`, which emits markdown documents that `render.py`
converts later — running those through a converter here would produce HTML inside
a markdown file. `markdown` is already a hard dependency of the build
(`render.py`), so the HTML side costs nothing new.
"""
from __future__ import annotations

import re
from pathlib import Path

import markdown

CORPUS = Path(__file__).resolve().parent.parent
CONTENT = CORPUS / "content"

# Deliberately a narrow extension set. These blocks are paragraphs, links and the
# occasional list — a table or a footnote in one is a sign it should be a page.
_EXTENSIONS = ["sane_lists", "attr_list"]

_cache: dict[str, dict[str, str]] = {}
_html: dict[tuple[str, str], str] = {}


def _parse(path: Path) -> dict[str, str]:
    """Split a content file into `{key: markdown}`.

    The preamble above the first `##` is dropped: it is a note to the editor, and
    a file whose purpose is to be edited by hand should be able to say what it is
    for without that text appearing on the site."""
    text = path.read_text(encoding="utf-8")
    parts = re.split(r"(?m)^##[ \t]+(\S.*?)[ \t]*$", text)
    if len(parts) < 3:
        raise ValueError(f"{path.name}: no '## key' blocks found")

    blocks: dict[str, str] = {}
    for i in range(1, len(parts), 2):
        key, body = parts[i].strip(), parts[i + 1].strip()
        if key in blocks:
            raise ValueError(f"{path.name}: '{key}' is defined twice")
        blocks[key] = body
    return blocks


def load(page: str) -> dict[str, str]:
    """Every block in `content/{page}.md` as markdown, cached for the process."""
    if page not in _cache:
        path = CONTENT / f"{page}.md"
        if not path.exists():
            raise FileNotFoundError(
                f"copy_lib: {path.relative_to(CORPUS)} is missing. The build reads the "
                f"site's explanatory prose from there; it cannot invent it.")
        _cache[page] = _parse(path)
    return _cache[page]


def _block(page: str, key: str) -> str:
    blocks = load(page)
    if key not in blocks:
        raise KeyError(
            f"copy_lib: no '## {key}' in content/{page}.md. "
            f"It holds: {', '.join(sorted(blocks)) or '(nothing)'}")
    return blocks[key]


def _fill(page: str, key: str, text: str, fields: dict) -> str:
    if not fields:
        return text
    try:
        return text.format(**fields)
    except KeyError as e:                       # a {name} nobody passed a value for
        raise KeyError(
            f"copy_lib: content/{page}.md '## {key}' uses {e} but the build did not "
            f"supply it. Given: {', '.join(sorted(fields)) or '(nothing)'}") from None
    except (IndexError, ValueError) as e:       # a stray brace, or a format spec
        raise ValueError(
            f"copy_lib: content/{page}.md '## {key}' will not format ({e}). A literal "
            f"brace must be doubled, and a value must arrive already formatted — "
            f"'{{n:,.0f}}' is not available here.") from None


def copy(page: str, key: str, **fields: object) -> str:
    """One block as HTML, with any `{placeholders}` filled from `fields`.

    Converted once per key and cached: the country builder asks for the same six
    blocks fifty-four times over, and running the markdown parser over them 324
    times to get 324 identical results is work for nothing."""
    if (page, key) not in _html:
        body = _block(page, key)
        _html[(page, key)] = markdown.markdown(body, extensions=_EXTENSIONS) if body else ""
    return _fill(page, key, _html[(page, key)], fields)


def copy_inline(page: str, key: str, **fields: object) -> str:
    """One block as HTML *without* its wrapping `<p>`, for a slot that supplies its
    own — `<p class="section-intro">…</p>` and the rest of the classed paragraphs.

    A block with more than one paragraph cannot go in such a slot, and saying so
    here is better than emitting a `<p>` nested inside a `<p>` and leaving the
    browser to guess: it closes the outer one early, and the styling silently comes
    off the second half of the text."""
    html = copy(page, key, **fields)
    if not (html.startswith("<p>") and html.endswith("</p>")) or "<p>" in html[3:]:
        raise ValueError(
            f"copy_lib: content/{page}.md '## {key}' is more than one paragraph, and "
            f"the page puts it inside a <p> of its own. Either shorten it to one "
            f"paragraph or give it a slot that takes block-level HTML.")
    return html[3:-4]


def copy_md(page: str, key: str, **fields: object) -> str:
    """One block as markdown, unconverted — for the builders that emit markdown."""
    return _fill(page, key, _block(page, key), fields)


def check(page: str, keys: list[str]) -> None:
    """Assert a page's file holds every block that page needs, before building any
    of it. Called at the top of a builder so a typo in a key fails on the first
    line rather than half way through writing 54 countries."""
    have = load(page)
    missing = [k for k in keys if k not in have]
    if missing:
        raise SystemExit(
            f"copy_lib: content/{page}.md is missing: {', '.join(missing)}\n"
            f"  It holds: {', '.join(sorted(have))}")


if __name__ == "__main__":                      # a quick look at what is where
    import sys
    files = sorted(CONTENT.glob("*.md")) if len(sys.argv) < 2 else [CONTENT / f"{sys.argv[1]}.md"]
    for f in files:
        blocks = load(f.stem)
        strip = lambda s: len(re.sub(r"<[^>]+>", " ", s).split())
        print(f"{f.stem:16s} {len(blocks):3d} blocks {sum(strip(v) for v in blocks.values()):5d} words")
        for k, v in blocks.items():
            print(f"    {k:30s} {strip(v):4d} w"
                  + ("  {placeholders}" if re.search(r"\{[a-z_]+\}", v) else ""))
