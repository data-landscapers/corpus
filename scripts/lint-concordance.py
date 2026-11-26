#!/usr/bin/env python3
r"""lint-concordance.py — every number and date in a linked sentence, looked for in the source it cites.

    python scripts/lint-concordance.py                 # all three pools -> logs/concordance.csv
    python scripts/lint-concordance.py --type status   # one pool, printed, not written

**Strategic review 9, R183. No model, and it reports, never gates.** It walks the linked sentences
`claim-audit.py` draws from (a Status report's sentences, a maturity paragraph's, a bulletin
summary's against its headline link), takes each figure and date the sentence states, and looks
for it in the held text of the cited source: the body, its title and its publication date. A
figure not found is listed. Not found is not wrong: a sum, a share or a conversion Corpus derived
is listed too, and the reader of the list (R187's weekly checklist) decides.

**Allowing for units and formats**:

- a figure matches a source figure that rounds to it at the claim's precision: *1.4 million* finds
  *1,375,000*; a scale word or suffix is applied either side (*million*, *bn*, *milliards*,
  *mil milhões*), and a figure matches its unscaled digits too, so *US$2.5bn* finds *2.5 billion*
  and *2 500 millions*;
- digit groups in any convention (*1,375,000*, *1 375 000*, *1.375.000*, *2,5*); per cent and
  currency signs are ignored;
- a year is found as itself; a month and year needs the month in English, French or Portuguese, or
  a numeric date; a full date needs the day too, in words or digits.

A number under ten is not checked (it is usually a count written either way), nor a figure inside
a link's address. A claim whose source is not held is skipped, as the claim audit skips it.

`logs/concordance.csv`: `doc_type,where,url,src,missing,claim`, one row per claim with a figure
not found, rewritten each run. Exit 0 always, 2 when the catalogue cannot be read.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import importlib.util
import io
import math
import os
import re
import sys
from collections import Counter
from decimal import ROUND_HALF_UP, Decimal

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)

_spec = importlib.util.spec_from_file_location("claim_audit", os.path.join(HERE, "claim-audit.py"))
ca = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ca)

OUT = os.path.join(REPO, "logs", "concordance.csv")
FIELDS = ["doc_type", "where", "url", "src", "missing", "claim"]
POOLS = {"status": ca.pool_status, "maturity": ca.pool_maturity, "bulletin": ca.pool_bulletin}

SCALE = {"thousand": 1e3, "k": 1e3, "mil": 1e3, "million": 1e6, "millions": 1e6, "m": 1e6, "mn": 1e6,
         "millio": 1e6, "milhões": 1e6, "milhoes": 1e6, "billion": 1e9, "billions": 1e9, "bn": 1e9,
         "b": 1e9, "milliard": 1e9, "milliards": 1e9, "mil milhões": 1e9, "trillion": 1e12, "tn": 1e12}
MONTHS = {
    1: "january janvier janeiro jan", 2: "february février fevrier fevereiro feb fév", 3: "march mars março marco mar",
    4: "april avril abril apr avr", 5: "may mai maio", 6: "june juin junho jun", 7: "july juillet julho jul juil",
    8: "august août aout agosto aug", 9: "september septembre setembro sep sept set",
    10: "october octobre outubro oct out", 11: "november novembre novembro nov",
    12: "december décembre decembre dezembro dec déc dez"}
MONTH_OF = {w: n for n, ws in MONTHS.items() for w in ws.split()}
MONTH_WORD = r"(?:" + "|".join(sorted((w for w in MONTH_OF if len(w) > 3), key=len, reverse=True)) + r")"

# a number in any grouping convention, then an optional scale word
NUM = re.compile(r"(?<![\w.,])(\d{1,3}(?:[ ,. ]\d{3})+(?:[.,]\d+)?|\d+(?:[.,]\d+)?)"
                 r"(?:\s?(mil milhões|thousand|millions?|milhões|milhoes|milliards?|billions?|trillion|bn|mn|tn|[kmb])\b)?",
                 re.I)
FULL_DATE = re.compile(r"\b(\d{1,2})(?:st|nd|rd|th|er)?\s+(?:de\s+)?(" + MONTH_WORD + r")\s+(?:de\s+)?((?:19|20)\d\d)\b", re.I)
FULL_DATE_US = re.compile(r"\b(" + MONTH_WORD + r")\s+(\d{1,2}),?\s+((?:19|20)\d\d)\b", re.I)
MONTH_YEAR = re.compile(r"\b(" + MONTH_WORD + r")\s+(?:de\s+)?((?:19|20)\d\d)\b", re.I)
FISCAL = re.compile(r"\b((?:19|20)\d\d)[/-]((?:19|20)?\d\d)\b")
URLS = re.compile(r"\]\([^)]*\)|https?://\S+")


def value(digits: str) -> float | None:
    """`1,375,000` `1 375 000` `1.375.000` `2,5` `2.5` -> a float."""
    d = digits.replace(" ", "").replace(" ", "")
    if re.fullmatch(r"\d{1,3}(?:[.,]\d{3})+", d) and not re.fullmatch(r"\d{1,3}[.,]\d{3}", d):
        return float(re.sub(r"[.,]", "", d))         # 1,375,000 or 1.375.000
    if re.fullmatch(r"\d{1,3}(?:[.,]\d{3})+[.,]\d+", d):  # 1,375,000.50: the last mark is the decimal
        last = max(d.rfind(","), d.rfind("."))
        return float(re.sub(r"[.,]", "", d[:last]) + "." + d[last + 1:])
    if re.fullmatch(r"\d{1,3}[.,]\d{3}", d):
        return float(d.replace(",", "").replace(".", ""))  # 1,375 read as a thousands group
    try:
        return float(d.replace(",", "."))
    except ValueError:
        return None


def significant(v: float) -> int:
    """The figures a claim states: 1,375,000 has four, 1.4 two, 2500 two, 2.50 two."""
    s = f"{v:.6f}".rstrip("0").rstrip(".").replace(".", "").lstrip("0")
    return max(len(s.rstrip("0")) if float(v).is_integer() else len(s), 1)


def figures(text: str) -> list[tuple[str, float, float | None, int]]:
    """(as written, digits value, scaled value or None, significant figures) for each figure."""
    out = []
    for m in NUM.finditer(text):
        v = value(m.group(1))
        if v is None:
            continue
        unit = (m.group(2) or "").lower()
        scaled = v * SCALE[unit] if unit in SCALE else None
        out.append((m.group(0).strip(), v, scaled, significant(v)))
    return out


def round_sig(x: float, s: int) -> float:
    """Half up, as a writer rounds: 2.5 million at one figure is 3 million, not 2."""
    if x == 0:
        return 0.0
    q = Decimal(1).scaleb(int(math.floor(math.log10(abs(x)))) - s + 1)
    return float(Decimal(repr(x)).quantize(q, rounding=ROUND_HALF_UP))


def source_values(text: str) -> set[float]:
    vals = set()
    for _w, v, scaled, _s in figures(text):
        vals.add(v)
        if scaled:
            vals.add(scaled)
    return vals


def found_number(v: float, scaled: float | None, sig: int, pool: set[float]) -> bool:
    targets = [v] + ([scaled] if scaled else [])
    for t in targets:
        r = round_sig(t, sig)
        for w in pool:
            if w and abs(round_sig(w, sig) - r) <= 1e-9 * max(1, abs(r)):
                return True
            # the source may scale where the claim does not, or the other way: 2.5bn vs 2,500 million;
            # at one figure that would match almost anything, so not there
            for k in ((1e3, 1e6, 1e9) if sig > 1 else ()):
                if abs(round_sig(w * k, sig) - r) <= 1e-9 * max(1, abs(r)):
                    return True
    return False


RELATIVE = re.compile(r"\b(monday|tuesday|wednesday|thursday|friday|saturday|sunday|yesterday|today|this week|"
                      r"last week|lundi|mardi|mercredi|jeudi|vendredi|samedi|dimanche|hier|aujourd'hui|"
                      r"segunda-feira|terça-feira|quarta-feira|quinta-feira|sexta-feira|sábado|domingo|ontem|hoje)\b")


def relative_day(day: str, month: int, year: str, src: str, low: str) -> bool:
    """*Inaugurated on Thursday*: a weekday or *yesterday* in a source published within a week after."""
    pub = re.search(r"^published:\s*(\d{4}-\d\d-\d\d)", src, re.M)
    if not (pub and RELATIVE.search(low)):
        return False
    try:
        gap = (dt.date.fromisoformat(pub.group(1)) - dt.date(int(year), month, int(day))).days
    except ValueError:
        return False
    return 0 <= gap <= 7


def date_found(day: str | None, month: int | None, year: str, src: str, low: str) -> bool:
    if day and month and relative_day(day, month, year, src, low):
        return True
    if year not in src:
        return False
    if month is None:
        return True
    names = [w for w, n in MONTH_OF.items() if n == month]
    mm = f"{month:02d}"
    month_ok = any(re.search(rf"\b{re.escape(w)}\b", low) for w in names) or \
        re.search(rf"\b{year}-{mm}\b|\b\d{{1,2}}[/.-]0?{month}[/.-]{year}\b|\b0?{month}[/.-]\d{{1,2}}[/.-]{year}\b", src)
    if not month_ok:
        return False
    if day is None:
        return True
    d = int(day)
    return bool(re.search(rf"\b0?{d}(?:st|nd|rd|th|er)?\s+(?:de\s+)?(?:{'|'.join(map(re.escape, names))})\b", low)
                or re.search(rf"(?:{'|'.join(map(re.escape, names))})\s+0?{d}\b", low)
                or re.search(rf"\b{year}-{mm}-{d:02d}\b|\b0?{d}[/.-]0?{month}[/.-]{year}\b", src))


def check(claim: str, src: str) -> list[str]:
    """The figures and dates of `claim` not found in `src`."""
    text = URLS.sub("", claim)
    low = src.lower()
    missing, spent = [], []
    for pat, order in ((FULL_DATE, "dmy"), (FULL_DATE_US, "mdy"), (MONTH_YEAR, "my")):
        for m in pat.finditer(text):
            if any(a <= m.start() < b for a, b in spent):
                continue
            spent.append(m.span())
            g = m.groups()
            day, mon, year = ((g[0], g[1], g[2]) if order == "dmy" else
                              (g[1], g[0], g[2]) if order == "mdy" else (None, g[0], g[1]))
            if not date_found(day, MONTH_OF[mon.lower()], year, src, low):
                missing.append(m.group(0))
    # A fiscal year, 2024/25 or 2024-2025, is found by either of its years in any form.
    for m in FISCAL.finditer(text):
        spent.append(m.span())
        first = m.group(1)
        second = first[:4 - len(m.group(2))] + m.group(2)
        if first not in src and second not in src:
            missing.append(m.group(0))
    rest = text
    for a, b in sorted(spent, reverse=True):
        rest = rest[:a] + " " * (b - a) + rest[b:]
    pool = None
    for w, v, scaled, sig in figures(rest):
        if v < 10 and not scaled:
            continue
        if re.fullmatch(r"(?:19|20)\d\d", w):
            if w not in src:
                missing.append(w)
            continue
        if pool is None:
            pool = source_values(src)
        if not found_number(v, scaled, sig, pool):
            missing.append(w)
    return missing


def held_text(held, path: str) -> str:
    """The body, plus the title and publication date from the frontmatter: the source's own words."""
    raw = io.open(path, encoding="utf-8", errors="replace").read()
    head = raw.split("\n---", 2)[0] if raw.startswith("---") else ""
    keep = "\n".join(ln for ln in head.splitlines() if re.match(r"(title|published|retrieved|date):", ln))
    return keep + "\n" + held.text(path)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--type", choices=sorted(POOLS))
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    try:
        held = ca.Held()
    except OSError as e:
        print(f"lint-concordance: cannot read the catalogue: {e}")
        return 2
    rows, tally = [], Counter()
    for kind in ([a.type] if a.type else POOLS):
        claims = POOLS[kind](held)
        for c in claims:
            if not c.get("src"):
                tally[kind, "not held"] += 1
                continue
            text = c.get("part") or c["claim"]
            miss = check(text, held_text(held, c["src"]))
            tally[kind, "checked"] += 1
            if miss:
                tally[kind, "listed"] += 1
                rows.append({"doc_type": kind, "where": c["where"], "url": c["url"],
                             "src": os.path.basename(c["src"])[:-3], "missing": "; ".join(miss),
                             "claim": text})
    for kind in ([a.type] if a.type else POOLS):
        print(f"lint-concordance: {kind}: {tally[kind, 'checked']} claims checked, "
              f"{tally[kind, 'listed']} with a figure not found, {tally[kind, 'not held']} not held")
    if a.type:
        for r in rows[:40]:
            print(f"  {r['where']}: {r['missing']}")
        return 0
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=FIELDS, lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
    with open(OUT, "wb") as fh:
        fh.write(buf.getvalue().encode("utf-8"))
    print(f"lint-concordance: {len(rows)} listed -> logs/concordance.csv (reports, never gates)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
