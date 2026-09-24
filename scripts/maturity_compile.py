r"""
maturity_compile.py — the measures Corpus computes from its own compiles, not from a reference.

`maturity-assess.py` asks `compiled(unit, as_at)` for every measure whose figure of record is a
Corpus file (`maturity-rubric.md`, each row's *Record*). The answer is a verdict in the drafter's
shape: `value, unit, value_year, value_source, qualifier`, and `stage` where the row's rule
decides more than the band does. **A compiled figure outranks a reference**, since it is Corpus's
own primary (`maturity-assessment-norms.md` §7), and a drafter's verdict outranks both.

The four measures computed here:
- `finance.sustain`: the domestic-state share of the digital budget lines, `budget_source.share()`.
- `finance.new--mobilisation-of-non-state-finance`: private non-state digital commitments over
  three years, as a share of GDP.
- the two data-centre rows, from `outputs/datasets/data-centres/data-centres.csv`: the count of
  Tier III-or-higher multi-tenant facilities, and the share nationally owned.

`finance.new--development-partner-project-financing` (the on-budget share, Bill 2026-09-24) is not
here. It matches the partner lines printed in a budget to the deals held, and no country-year has
been matched yet. Until one is, it stands only on a drafter's verdict.

**The as-at rule for a compile** follows the reference's (`maturity-assess.LIVE_FROM`). The two
retrospective snapshots see what Corpus holds today. From the first live snapshot, a record
dated after the as-at does not count. Each `value_source` carries the date of the newest record
that counted, which is the dated cause if the figure moves.
"""
from __future__ import annotations

import csv
import datetime as dt
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import budget_source  # noqa: E402

CORPUS = HERE.parent
NONSTATE = CORPUS / "outputs" / "non-state-finance"
DATACENTRES = CORPUS / "outputs" / "datasets" / "data-centres" / "data-centres.csv"
DENOMINATORS = CORPUS / "reference" / "denominators.csv"
SLUG_DATE = re.compile(r"^(\d{4}-\d{2}-\d{2})")

SUSTAIN = "finance.sustain--financial-sustainability-of-digital-systems"
MOBILISE = "finance.new--mobilisation-of-non-state-finance"
DC_ALL = "infra.store--local-data-centre-capacity-all-providers"
DC_NATIONAL = "infra.store--local-data-centre-capacity-national-providers"

PRIVATE = {"Private Sector", "Fund", "PPP"}
COUNTED_STATUS = {"Active", "Approved", "Closed"}
NOT_INSTRUMENT = {"MoU", "Unknown"}
MULTI_TENANT = {"Colocation/carrier-neutral", "Hyperscale"}
NATIONAL = {"Government / SOE", "Private domestic", "Joint venture (majority domestic)", "PPP"}
TIER3 = re.compile(r"tier[\s-]*(iii|iv|3|4)\b", re.I)


def _date(slug: str) -> dt.date | None:
    m = SLUG_DATE.match((slug or "").strip())
    return dt.date.fromisoformat(m.group(1)) if m else None


def _read(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with open(path, encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def _seen(slug_date: dt.date | None, as_at: dt.date, live_from: dt.date) -> bool:
    """A record counts at the as-at: always on a retrospective snapshot, by its date on a live one."""
    return as_at < live_from or (slug_date is not None and slug_date <= as_at)


def gdp(unit: str, as_at: dt.date) -> tuple[float, int] | None:
    rows = [r for r in _read(DENOMINATORS) if r["iso3"] == unit and r["indicator_id"] == "gdp-current-usd"
            and int(r["year"]) <= as_at.year]
    if not rows:
        return None
    r = max(rows, key=lambda r: int(r["year"]))
    return float(r["value"]), int(r["year"])


def sustain(unit: str, as_at: dt.date, live_from: dt.date) -> dict | None:
    """The latest read fiscal year up to the as-at's year whose share can be taken."""
    for iso3, fy, path in sorted(budget_source.files(unit), key=lambda t: -int(t[1])):
        if int(fy) > as_at.year:
            continue
        s = budget_source.share(unit, fy)
        if s.get("share") is None:
            continue
        slugs = [r.get("source_slug", "") for r in budget_source.read(path)[1]]
        dates = [d for d in map(_date, slugs) if d and _seen(d, as_at, live_from)]
        if not dates:
            continue
        flags = f"; {', '.join(s['flags'])}" if s.get("flags") else ""
        return {"value": f"{s['share']:g}", "unit": "per cent", "value_year": fy,
                "value_source": f"budgets/{unit}/{fy}.csv@{max(dates)}",
                "qualifier": f"on the state's own FY{fy} budget document, {s['stage']} figures{flags}"}
    return None


def mobilise(unit: str, as_at: dt.date, live_from: dt.date) -> dict | None:
    rows = _read(NONSTATE / f"{unit}-nonstate.csv")
    g = gdp(unit, as_at)
    if not rows or not g:
        return None
    years = {as_at.year - 2, as_at.year - 1, as_at.year}
    counted = [r for r in rows
               if r["beneficiary_type"] in PRIVATE and r["status"] in COUNTED_STATUS
               and r["instrument"] not in NOT_INSTRUMENT and r["start_year"].strip().isdigit()
               and int(r["start_year"]) in years and _seen(_date(r["record"]), as_at, live_from)]
    total = sum(float(r["commitment_usd_m"] or 0) for r in counted) * 1e6
    value = 100 * total / 3 / g[0]
    dates = [d for d in (_date(r["record"]) for r in (counted or rows)) if d]
    if not dates:
        return None
    return {"value": f"{value:.4g}" if value else "0", "unit": "per cent of GDP",
            "value_year": str(as_at.year),
            "value_source": f"outputs/non-state-finance/{unit}-nonstate.csv@{max(dates)}",
            "qualifier": (f"{len(counted)} private commitment(s) starting {min(years)}–{max(years)}, "
                          f"over GDP {g[1]} (WDI)" if counted else
                          f"no private digital commitment starting {min(years)}–{max(years)} on record")}


def _facilities(unit: str, as_at: dt.date, live_from: dt.date) -> list[dict]:
    out = []
    for r in _read(DATACENTRES):
        if r["country"] != unit or r["operational_status"] != "Operational":
            continue
        if r["facility_type"] not in MULTI_TENANT:
            continue
        y = r["year_operational"].strip()
        if y[:4].isdigit() and int(y[:4]) > as_at.year:
            continue
        slugs = [s.strip() for s in re.split(r"[|;]", r.get("raw_slugs", "")) if s.strip()]
        dates = [d for d in map(_date, slugs) if d]
        if as_at >= live_from and dates and min(dates) > as_at:
            continue
        r["_date"] = max(dates) if dates else None
        out.append(r)
    return out


def _stamp(rows: list[dict], as_at: dt.date) -> str:
    ds = [r["_date"] for r in rows if r.get("_date")]
    return f"outputs/datasets/data-centres/data-centres.csv@{max(ds) if ds else as_at}"


def dc_all(unit: str, as_at: dt.date, live_from: dt.date) -> dict:
    """Count of Tier III-or-higher multi-tenant facilities, and the rung it gives. Stage 2 needs a
    lower-tier or unstated-tier facility in service; with none at all the dataset's own coverage of
    the 54 is the cited absence, and it is stage 1."""
    fs = _facilities(unit, as_at, live_from)
    t3 = [f for f in fs if TIER3.search(f["security_certifications"]) or TIER3.search(f["comments"])]
    stated = sum(1 for f in t3 if not TIER3.search(f["security_certifications"]))
    stage = 4 if len(t3) >= 2 else 3 if t3 else 2 if fs else 1
    q = (f"{len(t3)} of {len(fs)} multi-tenant facilities in service at Tier III or above"
         + (f", {stated} on the operator's own statement" if stated else "")
         if fs else "no multi-tenant data centre in service in Corpus's dataset of the 54")
    return {"value": str(len(t3)), "unit": "facilities", "value_year": str(as_at.year),
            "value_source": _stamp(fs, as_at), "qualifier": q, "stage": str(stage)}


def dc_national(unit: str, as_at: dt.date, live_from: dt.date) -> dict | None:
    fs = [f for f in _facilities(unit, as_at, live_from) if f["ownership_type"] not in ("Unknown", "")]
    if not fs:
        return None
    nat = [f for f in fs if f["ownership_type"] in NATIONAL]
    return {"value": f"{100 * len(nat) / len(fs):.4g}", "unit": "per cent of facilities",
            "value_year": str(as_at.year), "value_source": _stamp(fs, as_at),
            "qualifier": f"{len(nat)} of {len(fs)} multi-tenant facilities of known ownership "
                         f"nationally owned"}


def compiled(unit: str, as_at: dt.date, live_from: dt.date) -> dict[str, dict]:
    out = {}
    for iid, fn in ((SUSTAIN, sustain), (MOBILISE, mobilise), (DC_ALL, dc_all),
                    (DC_NATIONAL, dc_national)):
        v = fn(unit, as_at, live_from)
        if v:
            out[iid] = {"indicator_id": iid, **v}
    return out
