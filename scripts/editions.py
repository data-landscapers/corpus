#!/usr/bin/env python3
"""editions.py — what an edition is called, when a new one is cut, and how one is published.

`documentation/design.md` §9. An edition is a dated, retained, immutable artefact: it is cut
when the content changes rather than when a build runs, it is never rewritten after publication,
and **no undated download URL exists at all** — the HTML page is the stable address a reader
browses, and every download it offers is dated.

This is a module rather than a section of `render.py` because three scripts publish editions:
`render.py` the dated PDFs, `country.py` the per-country finance CSVs and their field
dictionaries, `finance.py` the cross-country CSV. A filename grammar with one writer and
several readers is the arrangement that drifts, and it had already drifted before the `-2`
suffix existed — `country.py` and `topic-page.py` each held their own idea of what an edition
looked like, and both were wrong about it in ways that showed only as a page quietly offering
a superseded file.

**Not everything downloadable is an edition.** The catalogue is not *(Bill, 2026-08-18)*: it is
a browse index over other people's records, regenerated wholesale, and nobody cites it as of a
date. The finance CSVs are, because they are a compiled finding of ours that a reader may quote.
"""

from __future__ import annotations

import hashlib
import re
from datetime import date
from pathlib import Path

# **One grammar for an edition.** The date, and a same-day sequence where a second edition was
# cut on the same day (§9). `STEM_EDITION` is anchored at the end so the monthly and progress
# names that still carry a period from before the 2026-08-13 rename —
# `KEN-monthly-2026-07-2026-08-05` — yield the edition rather than the window.
EDITION = re.compile(r"^(?P<date>\d{4}-\d{2}-\d{2})(?:-(?P<seq>\d+))?$")
STEM_EDITION = re.compile(r"-(\d{4}-\d{2}-\d{2}(?:-\d+)?)$")


# **The page is the record of what is published** *(2026-09-09)*.
#
# This module used to say, in `next_edition` below, that *existence on disk is the test* — the
# retained artefacts are the record of which names are spoken for. That was true until
# 2026-09-08, when the editions moved to R2 and `r2-sync.py --prune-local` began deleting the
# local copy once the bucket had it. From that day the folder was empty at the moment these
# functions looked in it, and both of the questions they answer got the wrong answer silently:
# *is today's name taken?* (always no, so the same dated name was reused) and *have the bytes
# moved?* (nothing to compare against, so a fresh edition every render).
#
# On 2026-09-09 that cost 44 topic PDFs: the 02:34 render published them and the 11:30 render,
# whose documents had genuinely moved, cut new ones over the same names. §9 wanted `-2`.
#
# The page is the artefact that answers both and cannot go missing. It is written by the same
# run that cuts the edition, it is never pruned, it is in git, and it is already the gate's
# source of truth for whether a document has moved (`render.py` → `held_edition`). A document
# page carries `data-edition` and `dl-record` for itself; a page that publishes *other* dated
# artefacts — a finance CSV — carries one `dl-artefact` line for each.
ARTEFACT = re.compile(r'<meta name="dl-artefact" content="([^"|]+)\|([^"|]+)\|([0-9a-f]+)">')


def digest(data: bytes) -> str:
    """The content digest recorded beside an edition. Same algorithm and length as
    `render.py`'s `record()`, which digests a document body for the same purpose."""
    return hashlib.sha1(data).hexdigest()[:12]


def artefact_meta(stem: str, edition: str, record: str) -> str:
    """The line a page carries for each dated artefact it publishes. One writer, so the
    emitters cannot disagree with `artefacts_on_page` about the format."""
    return f'<meta name="dl-artefact" content="{stem}|{edition}|{record}">'


def artefacts_on_page(html_path: Path | None) -> dict[str, tuple[str, str]]:
    """`{stem: (edition, record)}` for every dated artefact a page publishes.

    Read from the page as it stands *before* this run rewrites it — which is the state that
    says what is currently published. A page that predates this field, or no page at all,
    yields nothing, and the caller mints: wrong only in the safe direction, the same call
    `held_edition` makes for a document with no stored digest."""
    if html_path is None or not html_path.exists():
        return {}
    return {m.group(1): (m.group(2), m.group(3))
            for m in ARTEFACT.finditer(html_path.read_text(encoding="utf-8"))}


def edition_of(stem: str) -> str | None:
    """The edition a rendered filename carries, or None if it carries none."""
    m = STEM_EDITION.search(stem)
    return m.group(1) if m else None


def edition_key(edition: str) -> tuple[str, int]:
    """Sort key for an edition: the date, then the same-day sequence as a **number**.

    Sorting the strings gets this wrong in both directions, and silently. In a filename
    `-2026-08-18-2.pdf` sorts *before* `-2026-08-18.pdf`, because `-` precedes `.`, so taking
    the last name of a sorted list hands back the older edition. In an edition string `-10`
    sorts before `-2`. Either way the page offers a superseded file and looks entirely correct
    doing it."""
    m = EDITION.match(edition or "")
    return (m.group("date"), int(m.group("seq") or 1)) if m else ("", 0)


def editions_of(out_dir: Path, stem: str, ext: str) -> list[tuple[tuple[str, int], Path]]:
    """Every retained edition of one document, oldest first.

    **The name is checked exactly, not matched by prefix.** `KEN-nonstate-*` also matches
    `KEN-nonstate-fields-2026-08-18.csv`, which is a different document that happens to begin
    with this one's name — and its editions are its own. Stripping the edition and comparing
    what is left is the only test that separates them, and getting it wrong would have the
    finance CSV take its edition from its own field dictionary."""
    found = []
    for f in out_dir.glob(f"{stem}-*{ext}"):
        edition = edition_of(f.stem)
        if edition is None or f.stem != f"{stem}-{edition}":
            continue
        found.append((edition_key(edition), f))
    return sorted(found)


def latest(out_dir: Path, stem: str, ext: str) -> Path | None:
    """The newest retained edition of one document, or None."""
    found = editions_of(out_dir, stem, ext)
    return found[-1][1] if found else None


def next_edition(out_dir: Path, stem: str, today: str, ext: str = ".pdf",
                 current: str | None = None) -> str:
    """Today's edition for this document — suffixed if today's name is already taken.

    **The first edition of a day is unsuffixed and the second takes `-2`** (§9). Two editions in
    one day is a normal occurrence rather than an edge case: SWEEP-CYCLE normally runs overnight,
    but a session may be run during the day to force an update on a live issue *(Bill,
    2026-08-06)*.

    **The first is never renamed when the second appears.** Making it `-1` for symmetry would
    break every URL already handed out, which is the one thing §9 exists to prevent — so the
    names are asymmetric, and since most days have one edition most of them stay clean.

    **Two sources say what is taken, and the highest wins** *(2026-09-09)*. Existence on disk
    was the only test until the editions moved to R2; `current` is the edition the page is
    already publishing, which is what survives `--prune-local` and is the answer whenever the
    tree has been emptied. Disk is kept because it is authoritative when it has anything to
    say — a file written earlier in this same run, before any sync — and because it costs a
    stat. Neither alone is sufficient: see the note at the head of this module for the 44 PDFs
    that were overwritten while disk was the only source."""
    taken = 0
    if (out_dir / f"{stem}-{today}{ext}").exists():
        taken = 1
    n = 2
    while (out_dir / f"{stem}-{today}-{n}{ext}").exists():
        taken = n
        n += 1
    if current:
        day, seq = edition_key(current)
        if day == today:
            taken = max(taken, seq)
    return today if taken == 0 else f"{today}-{taken + 1}"


# The edition a rendered document page is offering, written into its byline by `render.py`.
PAGE_EDITION = re.compile(r'data-edition="([^"]+)"')


def edition_on_page(html_path: Path | None) -> str | None:
    """The edition a rendered document is currently offering, read off the page.

    The document's own counterpart to `artefacts_on_page`, which covers the dated files a page
    publishes *besides* itself. Same reasoning, stated at the head of this module: the page is
    written by the run that cut the edition, is never pruned, and is in git.

    Also the answer to *which edition is current* for anything that used to glob the directory
    for the newest dated PDF — `country.py`'s report rows and `topic-page.py`'s download links
    both did, and both went blank on the first render after the tree was pruned."""
    if html_path is None or not html_path.exists():
        return None
    m = PAGE_EDITION.search(html_path.read_text(encoding="utf-8"))
    return m.group(1) if m else None


def retire_undated(out_dir: Path, stem: str, ext: str) -> Path | None:
    """Remove the undated predecessor of a now-dated artefact. Returns it, or None.

    §9 allows no undated download URL, and until 2026-08-18 the finance CSVs were published at
    one. `site/` is generated but never purged (RENDER.md), so a file that simply stops being
    written stays there and goes on being served for ever.

    **Deleting it does break a URL that was published, and that is the lesser of the two
    breakages.** An undated URL invites a citation that changes underneath the person who made
    it — the precise failure §9 exists to prevent — and leaving the file in place would keep
    that invitation open indefinitely, against a handful of days in which the site has served
    these files at all."""
    stale = out_dir / f"{stem}{ext}"
    if stale.exists():
        stale.unlink()
        return stale
    return None


def publish(data: bytes, out_dir: Path, stem: str, ext: str = ".csv",
            today: str | None = None, page: Path | None = None) -> tuple[Path, bool]:
    """Publish `data` as a dated edition of `{stem}{ext}`. Returns `(path, minted)`.

    **A new edition is cut only when the bytes have moved**, which is §9's rule applied to an
    artefact that is published byte-for-byte. The comparison can be direct here, unlike the PDF
    case: a PDF carries its build date inside it and so differs from its predecessor on every
    render, which is why `render.py` has to compare a digest of the *source* instead. A CSV
    written from unchanged data is the same file.

    **`page` is where that comparison goes when the file is not in the tree** *(2026-09-09)*.
    The retained editions were their own record until `--prune-local` started removing them,
    and from then on the file was never there to compare against: every render minted a new
    edition of all 61 finance CSVs, none of which differed from its predecessor by a byte.
    Pass the page that links this artefact — it is written after the CSV precisely because it
    links it by name, so at this moment it still carries the previous run's record — and the
    digest it holds answers the same question. The returned path may then name a file that is
    in the bucket rather than the tree; callers use its *name*, which is what the link needs.

    Disk still wins where it has anything to say: it is exact rather than a digest, and it
    covers an artefact written earlier in the same run."""
    out_dir.mkdir(parents=True, exist_ok=True)
    current = latest(out_dir, stem, ext)
    if current is not None and current.read_bytes() == data:
        retire_undated(out_dir, stem, ext)
        return current, False

    published, record = artefacts_on_page(page).get(stem, (None, None))
    if current is None and published and record == digest(data):
        retire_undated(out_dir, stem, ext)
        return out_dir / f"{stem}-{published}{ext}", False

    edition = next_edition(out_dir, stem, today or date.today().isoformat(), ext,
                           current=published)
    path = out_dir / f"{stem}-{edition}{ext}"
    path.write_bytes(data)
    retire_undated(out_dir, stem, ext)
    return path, True
