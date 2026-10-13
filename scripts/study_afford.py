#!/usr/bin/env python3
r"""study_afford.py — a mobile-data figure as a share of income, for the mobile affordability study.

`maturity-study-mobileaffordability.md` §3, read by `study-ladder-mobileaffordability.py` and
`study-affordability-write.py` so both turn a fact into the same number.

A `cost` value is one of two things:

- `share:{per cent}`: a stated share of average monthly income, used as stated;
- `price:{currency}:{amount}:{gigabytes}`: a stated price, **brought to 5 GB for a month** (a
  plan of 5 GB or more as priced, a smaller plan or a price per gigabyte multiplied up) and set
  against a twelfth of the World Bank's gross national income per person, in the price's
  currency, for the latest year held.

**A price Corpus cannot set against income gives no share**: one in a currency that is neither
the country's nor the US dollar, or for a country whose income figure is older than `INCOME_FROM`.
The rand counts as the currency of Lesotho, Namibia and Eswatini, where it is at par.
"""
from __future__ import annotations

import os

import study_lib

BASKET_GB = 5.0
INCOME_FROM = 2023
WDI_URL = "https://data.worldbank.org/indicator/NY.GNP.PCAP.CN"
CURRENCY = {
    "AGO": "AOA", "BDI": "BIF", "BEN": "XOF", "BFA": "XOF", "BWA": "BWP", "CAF": "XAF", "CIV": "XOF",
    "CMR": "XAF", "COD": "CDF", "COG": "XAF", "COM": "KMF", "CPV": "CVE", "DJI": "DJF", "DZA": "DZD",
    "EGY": "EGP", "ERI": "ERN", "ETH": "ETB", "GAB": "XAF", "GHA": "GHS", "GIN": "GNF", "GMB": "GMD",
    "GNB": "XOF", "GNQ": "XAF", "KEN": "KES", "LBR": "LRD", "LBY": "LYD", "LSO": "LSL", "MAR": "MAD",
    "MDG": "MGA", "MLI": "XOF", "MOZ": "MZN", "MRT": "MRU", "MUS": "MUR", "MWI": "MWK", "NAM": "NAD",
    "NER": "XOF", "NGA": "NGN", "RWA": "RWF", "SDN": "SDG", "SEN": "XOF", "SLE": "SLE", "SOM": "SOS",
    "SSD": "SSP", "STP": "STN", "SWZ": "SZL", "SYC": "SCR", "TCD": "XAF", "TGO": "XOF", "TUN": "TND",
    "TZA": "TZS", "UGA": "UGX", "ZAF": "ZAR", "ZMB": "ZMW", "ZWE": "ZWG",
}
RAND_AT_PAR = {"LSO", "NAM", "SWZ"}
_income: dict | None = None


def income(iso: str, currency: str) -> tuple[float, str] | None:
    """`(income per person for a year, that year)` in `currency`, or None where none is usable."""
    global _income
    if _income is None:
        _income = {}
        for r in study_lib.read_csv(os.path.join(study_lib.CORPUS, "reference", "denominators.csv")):
            if r["indicator_id"] in ("gni-per-capita-lcu", "gni-per-capita-usd"):
                k = (r["iso3"], r["indicator_id"][-3:])
                if k not in _income or r["year"] > _income[k][1]:
                    _income[k] = (float(r["value"]), r["year"])
    local = currency == CURRENCY.get(iso) or (currency == "ZAR" and iso in RAND_AT_PAR)
    got = _income.get((iso, "lcu" if local else "usd")) if local or currency == "USD" else None
    return got if got and int(got[1]) >= INCOME_FROM else None


def share(iso: str, value: str) -> float | None:
    """The per cent of average monthly income the value comes to, or None where it gives none."""
    kind, _, rest = value.partition(":")
    if kind == "share":
        return float(rest)
    currency, amount, gb = rest.split(":")
    got = income(iso, currency)
    if not got or float(gb) <= 0:
        return None
    month = float(amount) * (1.0 if float(gb) >= BASKET_GB else BASKET_GB / float(gb))
    return round(100.0 * month / (got[0] / 12.0), 2)
