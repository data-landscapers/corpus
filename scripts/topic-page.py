#!/usr/bin/env python3
"""topic-page.py — forwards each retired `/topics/{slug}/` page to the topic's news.

**The topic landing pages are retired** *(Bill, 2026-10-20)*. Each was an index to the topic's
two reports, and the report head's News · Progress bar now carries that, as the place pages'
did before them (`country.py` → `retire_page`). The boxes on `/topics/` open the news page
directly (`home.topic_href`). A stub rather than a deletion, because `/topics/{slug}/` is linked
from pages already out; `sitemap.py` leaves a refresh page out of the sitemap.

Nothing here reads a ledger or a source: only what BUILD wrote into `outputs/topics/`.

Usage:
  python scripts/topic-page.py            # one stub per topic folder under site/topics/
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from home import SITE_BASE, topic_href  # noqa: E402

SITE = Path(__file__).resolve().parent.parent / "site"


def retire_page(out_dir: Path, url: str) -> None:
    (out_dir / "index.html").write_text(f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Moved — Data Landscapers</title>
<meta name="robots" content="noindex">
<meta http-equiv="refresh" content="0; url={url}">
<link rel="canonical" href="{url}">
</head>
<body>
<p>This page has moved <a href="{url}">here</a>.</p>
</body>
</html>
""", encoding="utf-8", newline="")


def main() -> int:
    wrote = 0
    for folder in sorted(p for p in (SITE / "topics").iterdir() if p.is_dir()):
        # A topic with no report forwards to the topics page, which lists it.
        retire_page(folder, topic_href(folder.name) or f"{SITE_BASE}/topics/")
        wrote += 1
    print(f"topic pages: {wrote} forwarded -> site/topics/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
