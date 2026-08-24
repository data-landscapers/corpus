#!/usr/bin/env python3
"""topic-page.py — the landing page each topic box on the home page opens.

The home page's Level-1 tiles open a row of Level-2 sub-topic boxes, and every one of those links
to `/topics/{slug}/`. A directory is not a page: `site/topics/dpi-pay/` holds
`dpi-pay-monthly.html`, `dpi-pay-progress.html` and their PDFs, and a link to the directory itself
404s. This writes the `index.html` that makes the link land somewhere — the same shape as a
country's, and for the same reason: a place to choose a document from, with the two documents,
their editions and their PDFs on it.

It also writes an `index.html` for each **Level-1** category, because the sub-topic row ends with
an *All {category}* box pointing at `/topics/{l1}/`. That page is an **index, not a report**:
Level-1 roll-up reports are deliberately not built (`documentation/topic-reports.md` — the
taxonomy is a strict single-parent tree, so a Level-1 report is a later composition of the same
material and costs nothing to defer). The page says so, and lists the topics beneath it.

Nothing here reads a ledger or a source. It reads what BUILD wrote into `outputs/topics/` and what
RENDER wrote into `site/topics/`, and links the two together.

Usage:
  python scripts/topic-page.py            # 38 topic pages + 10 category pages
"""
import os
import re
import sys
from datetime import date
from html import escape as e
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import editions  # noqa: E402  — §9's filename grammar has one implementation
import vault_lib  # noqa: E402
from chrome_lib import chrome, foot, styles  # noqa: E402
from copy_lib import copy_inline  # noqa: E402

CORPUS = Path(__file__).resolve().parent.parent
OUTPUTS = CORPUS / "outputs"
SITE = CORPUS / "site"
SITE_BASE = "https://corpus.data-landscapers.io"
MAIN_SITE = "https://data-landscapers.io"

MONTHS = ("January", "February", "March", "April", "May", "June",
          "July", "August", "September", "October", "November", "December")

L1 = {"infra": "ICT Infrastructure", "dpi": "Digital public infrastructure",
      "gov": "Governance and regulation", "include": "Inclusion",
      "tech": "Technology", "geopol": "Geopolitics", "capacity": "Capacity",
      "digital": "Digitalisation", "data": "Data", "finance": "Finance"}

KINDS = (("monthly", "Monthly update",
          "What moved this month, place by place — every block carried from that place&rsquo;s own "
          "monthly update."),
         ("progress", "Progress report",
          "Twelve months of movement, place by place — each place&rsquo;s own movement table for "
          "this topic."))


def front_matter(path: Path) -> dict:
    out = {}
    if not path.exists():
        return out
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return out
    for line in text.split("\n---", 2)[0].split("\n")[1:]:
        if ":" in line:
            k, v = line.split(":", 1)
            out[k.strip()] = v.strip()
    return out


def period_label(kind: str, period: str) -> str:
    """A monthly is named by the month it opens in; a progress report states its window."""
    if kind == "monthly":
        m = re.match(r"(\d{4})-(\d{2})", period or "")
        return f"{MONTHS[int(m.group(2)) - 1]} {m.group(1)}" if m else ""
    return (period or "").replace(" to ", " &ndash; ")


def edition_pdf(folder: Path, stem: str) -> str:
    """The newest dated PDF for this document, or "".

    Read off the directory rather than computed from today: the PDF is retained edition over
    edition and the newest one is whatever the last render actually cut, which is not necessarily
    today — a document that did not change is not re-rendered and keeps the edition it has.

    **Newest by `editions.py`'s ordering, not by filename** *(2026-08-18)*. Sorting the names and
    taking the last was right until §9's same-day `-2` suffix existed, and then quietly wrong in
    the one case it matters: `-2026-08-18-2.pdf` sorts *before* `-2026-08-18.pdf`, because `-`
    precedes `.`, so the newer edition of the two would never be the one offered."""
    dated = [(editions.edition_key(editions.edition_of(p.stem) or ""), p.name)
             for p in folder.glob(f"{stem}-20*.pdf")]
    return max(dated)[1] if dated else ""


def document_rows(slug_path: str) -> str:
    src = OUTPUTS / "topics" / slug_path
    out = SITE / "topics" / slug_path
    rows = []
    for kind, label, blurb in KINDS:
        stem = f"{slug_path}-{kind}"
        html = out / f"{stem}.html"
        if not html.exists():
            continue
        meta = front_matter(src / f"{stem}.md")
        places = len([p for p in (meta.get("places") or "").split(";") if p.strip()])
        period = period_label(kind, meta.get("period", ""))
        pdf = edition_pdf(out, stem)
        bits = [f'{places} places'] if places else []
        if period:
            bits.append(period)
        if meta.get("compiled"):
            bits.append(f'compiled <span class="mono">{e(meta["compiled"])}</span>')
        rows.append(f"""
      <div class="report-row">
        <div class="report-row__main">
          <div class="report-row__kind">{label}</div>
          <div class="report-row__blurb">{blurb}</div>
          <div class="report-row__meta">{' &nbsp;·&nbsp; '.join(bits)}</div>
        </div>
        <div class="report-row__acts">
          <a class="btn" href="{stem}.html">Read</a>
          {f'<a class="btn btn--accent" href="{pdf}">&darr; PDF</a>' if pdf else ''}
        </div>
      </div>""")
    if not rows:
        return f'<p class="table-note">{copy_inline("topic", "no-documents")}</p>'
    return "\n".join(rows)


# The header and footer this file used to carry were deleted on 2026-08-24 and
# come from `chrome_lib` now. They were a fourth variant of the site chrome: no
# main-site row at all, a nav offering Home but neither Regions nor Method, and
# a footer in prose where every other page carries the licence line. That is
# exactly what `chrome_lib`'s own header note predicted would happen to a copy
# nothing compares against — see documentation/house-style-review-2026-08-24.md
# §2. Nothing about the chrome belongs in this file.

PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} — Data Landscapers</title>
<meta name="description" content="{description}">
<link rel="canonical" href="{base}/topics/{path}/">
{styles}
<link rel="icon" href="{favicon}" type="image/svg+xml">
<meta property="og:title" content="{title} — Data Landscapers">
<meta property="og:description" content="{description}">
<meta property="og:url" content="{base}/topics/{path}/">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Data Landscapers">
</head>
<body>
<div class="site-wrap">

{chrome}

  <main id="main">
  <div class="container">

    <div class="crumb"><a href="{base}/#topics">Topics</a> &nbsp;/&nbsp; {crumb}</div>

    <div class="country-head">
      <h1>{title}</h1>
      <div class="country-head__meta">{meta}</div>
    </div>

{body}

  </div>
  </main>

{foot}

</div>
</body>
</html>
"""

TOPIC_BODY = """    <h2 class="section-heading">Documents</h2>
{rows}

    <h2 class="section-heading">How to read these</h2>
    <p>{how_to_read}</p>
    <p>Where a place has nothing on record for this topic in the period, it has no section: an
       absent heading means no evidence held, not nothing happening. The place&rsquo;s own report
       is the fuller account &mdash; <a href="{base}/#countries">browse by country</a>.</p>
"""

CATEGORY_BODY = """    <p class="section-intro">{intro}</p>

    <h2 class="section-heading">Topics in this category</h2>
    <div class="tsub__inner">
{boxes}
    </div>

    <p class="caveat">{category_caveat}</p>
"""


def write(path: str, title: str, description: str, crumb: str, meta: str, body: str) -> Path:
    out_dir = SITE / "topics" / path
    out_dir.mkdir(parents=True, exist_ok=True)
    dst = out_dir / "index.html"
    dst.write_text(PAGE.format(
        base=SITE_BASE, path=path, title=e(title), description=e(description),
        crumb=crumb, meta=meta, body=body,
        favicon=f"{MAIN_SITE}/assets/favicon.svg",
        styles=styles(2, "home.css", "country.css"),
        chrome=chrome("topics", depth=2),
        foot=foot(depth=2),
    ), encoding="utf-8")
    return dst


def taxonomy_path() -> Path:
    """The vocabulary snapshot, never OSINT's `lookups/`.

    RENDER runs from the repo root and must never have to read outside `outputs/` — which is why
    stage 1 of the build snapshots the vocabularies into `outputs/vocab/` in the first place.
    `vault_lib.load_taxonomy()`'s default resolves to `ROOT/lookups/`, which does not exist here,
    so the path is passed rather than defaulted."""
    for p in (OUTPUTS / "vocab" / "taxonomy.md", CORPUS / "outputs" / "vocab" / "taxonomy.md"):
        if p.exists():
            return p
    raise SystemExit("no taxonomy snapshot: run `python scripts/rebuild.py --vocab` first")


def main() -> int:
    _, label, _ = vault_lib.load_taxonomy(str(taxonomy_path()))
    built = date.today().isoformat()
    wrote = 0

    for slug in sorted(label):
        path = slug.replace(".", "-")
        if not (SITE / "topics" / path).is_dir():
            print(f"  {slug}: nothing rendered under site/topics/{path}/ — skipped")
            continue
        cat = L1.get(slug.split(".")[0], slug.split(".")[0])
        write(path, label[slug],
              f"{label[slug]} across Africa: monthly and progress reports compiled place by place "
              f"from the Data Landscapers base.",
              e(label[slug]),
              f'<span class="mono">{e(slug)}</span> &nbsp;·&nbsp; {e(cat)} '
              f'&nbsp;·&nbsp; page built {built}',
              TOPIC_BODY.format(rows=document_rows(path), base=SITE_BASE,
                                how_to_read=copy_inline("topic", "how-to-read")))
        wrote += 1

    for key, name in L1.items():
        kids = sorted(s for s in label if s.split(".")[0] == key)
        if not kids:
            continue
        # `--fill:0` is not decoration: `.sbox`'s background is
        # `color-mix(… calc(var(--fill) * 12%) …)`, so an unset `--fill` makes the whole
        # declaration invalid and the box renders with no background at all. These boxes carry
        # no count to scale, so zero is the accurate value as well as the working one.
        boxes = "\n".join(
            f'      <a class="sbox" href="../{s.replace(".", "-")}/" title="{s}"'
            f' style="--fill:0">'
            f'<span class="sbox__l">{e(label[s])}</span>'
            f'<span class="sbox__n" aria-hidden="true">&rarr;</span></a>' for s in kids)
        write(key, name,
              f"{name}: the topics beneath it, each with its own monthly and progress reports.",
              e(name),
              f'<span class="mono">{key}.*</span> &nbsp;·&nbsp; {len(kids)} topics '
              f'&nbsp;·&nbsp; page built {built}',
              CATEGORY_BODY.format(
                  category_caveat=copy_inline("topic", "category-caveat"),
                  intro=f"{name} rolls up {len(kids)} topics. Each carries a monthly update and a "
                        f"progress report, compiled place by place from the same base.",
                  boxes=boxes))
        wrote += 1

    print(f"topic pages: {wrote} written -> site/topics/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
