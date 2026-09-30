#!/usr/bin/env python3
r"""hyperscaler-publish.py — the 54 hyperscaler fact sheets as country reports.

    python scripts/hyperscaler-publish.py            # every country
    python scripts/hyperscaler-publish.py ZAF KEN    # some

Reads `R&D/Hyperscaler-dependence/scan/{ISO3}/report.md` (written by `hyperscaler-report.py`) and
writes `scan/{ISO3}/{ISO3}-hosting.md` beside it, which `render.py` publishes as
`site/reports/{ISO3}/{ISO3}-hosting.html` and a dated PDF, and `country.py` lists as the
*Institution hosting* report. The source stays under `R&D/`: `render.py` takes the site directory
from the filename's unit, and `outputs/reports/` is read by a dozen scripts that expect the three
ledger kinds only.

What changes on the way *(Bill, 2026-09-30)*:

- **Byline**: compiled by Claude Opus 5.5, in the frontmatter `subtitle` the renderer prints.
  The fact sheet's own date-and-author line is dropped.
- **The claimable names are counted, not attributed.** The fact sheet names the institutions
  whose web addresses point at a deleted cloud name; the published report says how many, as the
  methodology promises. Naming them narrows an attacker's search to a handful of estates.
- **The last paragraph links the dataset** in place of the repository path.
- **The views bar** (Dataset · Methodology · Continental analysis) opens the body.
- **The chart is embedded** as a data URI, so the page and the PDF carry it without a second
  file: `render.py` gives WeasyPrint a base URL in the stylesheet directory, where a relative
  image would not resolve.

Deterministic: an unchanged fact sheet gives byte-identical output, so `render.py` cuts no new
edition.
"""
from __future__ import annotations

import base64
import re
import sys
from pathlib import Path

SCAN = Path(__file__).resolve().parent.parent / "R&D" / "Hyperscaler-dependence" / "scan"
DATASET = "https://corpus.data-landscapers.io/datasets/institution-hosting/"
BYLINE = "compiled by Claude Opus 5.5 from a scan of public internet records"
# The bar the dataset, methodology and continental analysis pages carry (`datasets.py` →
# `IH_VIEWS`), so a country report links the same three views (Bill, 2026-09-30).
VIEWS = """<nav class="article-toc" aria-label="Institution hosting views">
<a href="https://corpus.data-landscapers.io/datasets/institution-hosting/">Dataset</a>
<span class="article-toc__sep" aria-hidden="true">&middot;</span>
<a href="https://corpus.data-landscapers.io/datasets/institution-hosting/methodology/">Methodology</a>
<span class="article-toc__sep" aria-hidden="true">&middot;</span>
<a href="https://data-landscapers.io/2026/09/30/institution-hosting/">Continental analysis</a>
</nav>
"""

CLAIMABLE = re.compile(
    r"(\*\*Names anyone could claim\.\*\* \S+ web address(?:es)? at )(.+?)( points? at a deleted)")
LAST = re.compile(r"^The data and method are in .*$", re.M)


def count_names(match: re.Match) -> str:
    n = len(re.split(r", | and ", match.group(2)))
    return f"{match.group(1)}{'one institution' if n == 1 else f'{n} institutions'}{match.group(3)}"


def publish(iso: str) -> Path:
    d = SCAN / iso
    text = (d / "report.md").read_text(encoding="utf-8")
    head, body = text.split("\n---\n", 1) if text.startswith("---") else ("", text)
    meta = dict(ln.split(":", 1) for ln in head.splitlines()[1:] if ":" in ln)
    lines = body.strip("\n").splitlines()
    h1 = next(ln for ln in lines if ln.startswith("# "))
    country = h1[2:].split(":", 1)[0].strip()
    # the byline under the h1: "29 September 2026 · Bill Anderson · scan of …"
    lines = [ln for ln in lines if not (ln and "·" in ln and not ln.startswith(("#", "|", "-", "!")))]
    body = "\n".join(lines) + "\n"
    body = body.replace(h1 + "\n", h1 + "\n\n" + VIEWS, 1)

    body = CLAIMABLE.sub(count_names, body)
    body = body.replace("Of the 54 countries scanned so far,", "Of the 54 countries scanned,")
    body, n = LAST.subn(
        f"The figures for every institution in {country} and the other 53 countries, and the method "
        f"behind them, are in the [Institution hosting dataset]({DATASET}).", body)
    if n != 1:
        sys.exit(f"{iso}: closing paragraph not found")
    png = d / "report-chart.png"
    uri = "data:image/png;base64," + base64.b64encode(png.read_bytes()).decode("ascii")
    body, n = re.subn(r"\]\(report-chart\.png\)", f"]({uri})", body)
    if n != 1:
        sys.exit(f"{iso}: chart reference not found")

    out = d / f"{iso}-hosting.md"
    front = ("---\n"
             f"title: {h1[2:].strip()}\n"
             f"subtitle: {BYLINE}\n"
             f"scan_date: {meta.get('scan_date', '').strip()}\n"
             "---\n\n")
    data = (front + body).encode("utf-8")
    if not out.exists() or out.read_bytes() != data:
        out.write_bytes(data)
    return out


def main(argv: list[str]) -> int:
    isos = argv or sorted(p.name for p in SCAN.iterdir() if (p / "report.md").exists())
    for iso in isos:
        publish(iso)
    print(f"hyperscaler-publish: {len(isos)} reports -> scan/{{ISO3}}/{{ISO3}}-hosting.md")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
