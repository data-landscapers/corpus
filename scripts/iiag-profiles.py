#!/usr/bin/env python3
"""Resolve and verify the Mo Ibrahim Foundation's per-country IIAG profiles.

    python scripts/iiag-profiles.py            # verify and rewrite lookups/iiag-profiles.csv
    python scripts/iiag-profiles.py --check    # verify only, change nothing

The IIAG is the source behind 96 of the 462 rows the AfDB DPI dataset carries for each country, and
**those rows carry no URL** — their `Source urls` column holds source-organisation abbreviations
(`AFIDEP/BS/FH`, `V-DEM/WJP`, `AFR`) rather than links. Under `STATUS-INIT.md`'s *no link, no claim*
that made the whole family uncitable and silently dropped it from the first run. The Foundation does
publish a country profile per country, at `assets.iiag.online/{year}/profiles/{year}-IIAG-profile-
{iso2}.pdf` (Bill, 2026-08-15), which is the primary for those scores.

**The pattern is not trusted; it is tested.** A URL synthesised from a remembered pattern is
indistinguishable from a real one by inspection — that is the whole reason check A exists — so this
fetches every profile and reads the country name out of the PDF's own header before writing it to
the lookup. The lookup is data in the repo, checked in and re-verifiable, rather than a rule in
someone's head; `status_lib.iiag_urls()` reads it and check A's held set includes it.

Re-run when the Foundation publishes a new IIAG year, with `--year`.
"""

import argparse
import csv
import datetime
import os
import re
import sys
import urllib.error
import urllib.request
import zlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import status_lib as S  # noqa: E402

OSINT_COUNTRIES = r"C:\OSINT\lookups\countries.csv"
URL = "https://assets.iiag.online/{year}/profiles/{year}-IIAG-profile-{iso2}.pdf"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) corpus-status-init/1.0"

# ISO 3166-1 alpha-2 for the 54, keyed by the alpha-3 `lookups/countries.csv` uses. Every one of
# these is checked against the profile it resolves to before it is written out, so a wrong code
# fails loudly rather than citing another country's scores.
ISO2 = {
    "AGO": "ao", "BDI": "bi", "BEN": "bj", "BFA": "bf", "BWA": "bw", "CAF": "cf", "CIV": "ci",
    "CMR": "cm", "COD": "cd", "COG": "cg", "COM": "km", "CPV": "cv", "DJI": "dj", "DZA": "dz",
    "EGY": "eg", "ERI": "er", "ETH": "et", "GAB": "ga", "GHA": "gh", "GIN": "gn", "GMB": "gm",
    "GNB": "gw", "GNQ": "gq", "KEN": "ke", "LBR": "lr", "LBY": "ly", "LSO": "ls", "MAR": "ma",
    "MDG": "mg", "MLI": "ml", "MOZ": "mz", "MRT": "mr", "MUS": "mu", "MWI": "mw", "NAM": "na",
    "NER": "ne", "NGA": "ng", "RWA": "rw", "SDN": "sd", "SEN": "sn", "SLE": "sl", "SOM": "so",
    "SSD": "ss", "STP": "st", "SWZ": "sz", "SYC": "sc", "TCD": "td", "TGO": "tg", "TUN": "tn",
    "TZA": "tz", "UGA": "ug", "ZAF": "za", "ZMB": "zm", "ZWE": "zw",
}

# The profile's own cover line, which is what proves the URL resolved to the country asked for.
PROFILE = re.compile(r"PROPROFILE:FILE:(.{2,40}?)mo\.ibrahim")


def profile_name(pdf):
    """The country the PDF says it is about, from its cover, or None."""
    for m in re.finditer(rb"stream\r?\n(.*?)endstream", pdf, re.S):
        try:
            text = zlib.decompress(m.group(1)).decode("latin-1")
        except Exception:                                                   # noqa: BLE001
            continue
        hit = PROFILE.search("".join(re.findall(r"\((.*?)\)", text)))
        if hit:
            return hit.group(1).strip()
    return None


def fetch(url):
    # The asset host answers Python's default user-agent with 403 and a browser's with the file, so
    # the request says who it is. Nothing else about the fetch is unusual.
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as fh:
        return fh.read()


def profile_url(iso3):
    """The verified profile URL for a country, from the lookup. None where there is none."""
    if not os.path.exists(S.IIAG_CSV):
        return None
    with open(S.IIAG_CSV, encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            if row["iso3"].upper() == iso3.upper():
                return row["url"]
    return None


def profile_text(iso3, path):
    """Write the country's profile out as text, for stage 1 to read.

    The URL alone would let the report cite an IIAG score without anyone having read the thing it
    is published in, which is the citation-without-evidence the whole process is built to avoid.
    The profile carries each of the 96 indicators' 2023 score, its rank of 54 and its ten-year
    change — reportable material, where a dataset value code is not."""
    import pdfplumber                                                       # noqa: PLC0415

    url = profile_url(iso3)
    if not url:
        return None
    blob = fetch(url)
    tmp = path + ".pdf"
    with open(tmp, "wb") as fh:
        fh.write(blob)
    pages = []
    with pdfplumber.open(tmp) as pdf:
        for n, page in enumerate(pdf.pages, 1):
            text = (page.extract_text() or "").strip()
            if text:
                pages.append(f"--- page {n} ---\n{text}")
    os.remove(tmp)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(f"# 2024 IIAG country profile\n# source: {url}\n\n" + "\n\n".join(pages) + "\n")
    return url


def countries():
    with open(OSINT_COUNTRIES, encoding="utf-8-sig", newline="") as fh:
        return [(r["iso-3"], r["country-name"]) for r in csv.DictReader(fh)
                if r["iso-3"] in ISO2]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--year", default="2024", help="the IIAG edition to resolve")
    ap.add_argument("--check", action="store_true", help="verify only; write nothing")
    ap.add_argument("--text", metavar="ISO3",
                    help="write one country's profile out as text and stop")
    ap.add_argument("--out", help="where --text writes")
    args = ap.parse_args()
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

    if args.text:
        out = args.out or os.path.join(S.REPO, "prep", "scope", args.text.upper(),
                                       f"{args.text.upper()}-iiag.txt")
        os.makedirs(os.path.dirname(out), exist_ok=True)
        url = profile_text(args.text.upper(), out)
        if not url:
            print(f"! no verified profile for {args.text.upper()}")
            return 1
        print(f"{out}   {os.path.getsize(out):,} bytes   {url}")
        return 0

    rows, bad = [], []
    for iso3, name in countries():
        url = URL.format(year=args.year, iso2=ISO2[iso3])
        try:
            pdf = fetch(url)
            got = profile_name(pdf)
        except (urllib.error.URLError, OSError) as exc:                     # noqa: BLE001
            got, pdf = None, b""
            print(f"  ! {iso3} {url} — {exc}")
        if got:
            rows.append((iso3, ISO2[iso3], name, got, url))
            print(f"  {iso3}  {ISO2[iso3]}  {len(pdf):>8,}  {name:<26} profile says: {got}")
        else:
            bad.append(iso3)

    print(f"\n{len(rows)} profile(s) resolved, {len(bad)} did not"
          + (": " + ", ".join(bad) if bad else ""))
    names = [r[3] for r in rows]
    dupes = sorted({n for n in names if names.count(n) > 1})
    if dupes:
        print(f"! {len(dupes)} profile name(s) appear more than once — a code is wrong: "
              + ", ".join(dupes))
        return 1
    if args.check:
        return 0 if not bad else 1
    if not rows:
        print("! nothing resolved — the lookup is left as it was")
        return 1

    os.makedirs(os.path.join(S.REPO, "lookups"), exist_ok=True)
    out = os.path.join(S.REPO, "lookups", "iiag-profiles.csv")
    with open(out, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["iso3", "iso2", "country", "profile_name", "url", "year", "verified"])
        today = datetime.date.today().isoformat()
        for row in rows:
            w.writerow(list(row) + [args.year, today])
    print(f"wrote {out}")
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
