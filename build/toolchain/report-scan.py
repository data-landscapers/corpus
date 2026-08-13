#!/usr/bin/env python3
"""report-scan.py — the script gate of REPORT-UPDATE.md.

Which initialised units hold sources the report pass has not yet looked at.

The unit of "new" is a **set difference, not a date window**: a source counts as unconsidered
until its slug appears either in the unit's `ledger.csv` or in its `considered.txt`. That makes an
interrupted run repeat exactly the work it did not finish, catches a source published years ago but
ingested last night, and leaves no clock to drift against — the same argument as `new/ -> raw/`.

    python scripts/report-scan.py                 # the work order, one line per unit
    python scripts/report-scan.py --json          # the same, machine-readable
    python scripts/report-scan.py --slugs NGA     # the unconsidered slugs for one unit
    python scripts/report-scan.py --mark NGA a b  # record slugs as considered
    python scripts/report-scan.py --month-due     # is a closed month owed an issue?
"""
import argparse
import collections
import importlib.util
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import vault_lib  # noqa: E402

# One definition of "initialised", imported rather than restated: a header-only shell is an
# interrupted run, not a done unit, and two copies of that test is how the two drift apart.
_spec = importlib.util.spec_from_file_location("rci", os.path.join(HERE, "report-country-init.py"))
_rci = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_rci)

# The region scope rule, imported for the same reason: a nightly set difference taken over a
# different base than the initialisation read would leave a region's institutional sources
# permanently unconsidered (`REPORT-REGION.md` -> Scope).
_spec_r = importlib.util.spec_from_file_location("rri", os.path.join(HERE, "report-region-init.py"))
_rri = importlib.util.module_from_spec(_spec_r)
_spec_r.loader.exec_module(_rri)

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPORTS = "outputs/reports"
MONTH_MARK = os.path.join(REPORTS, "last-monthly.txt")


def units():
    """Initialised units — the folder is the state, and the state is rows (REPORT-COUNTRY.md)."""
    if not os.path.isdir(REPORTS):
        return []
    return sorted(d for d in os.listdir(REPORTS)
                  if os.path.isdir(os.path.join(REPORTS, d)) and _rci.initialised(d))


def sources_by_place():
    """{unit: {slug}} over raw/ — the places facet for a country, the scope rule for a region.

    A region's base is not its place tag alone: an ECOWAS decision reported from Abuja is tagged
    `NGA` and reaches the unit through the institution it names. `XSS` folds into `XAF` and `XGL`
    is not a unit, so neither is left in the map to be reported as a place awaiting a report."""
    rows = vault_lib.load_index()
    out = collections.defaultdict(set)
    for r in rows:
        d, fm = r.get("d") or {}, r.get("fm") or {}
        if d.get("kind") != "source" or d.get("folder") != "raw":
            continue
        slug = d.get("slug") or os.path.basename(r["path"])[:-3]
        for p in (fm.get("places") or []):
            out[str(p).strip()].add(slug)
    for code, slugs in _rri.scope(rows)[0].items():
        out[code] = set(slugs)
    for code in ("XSS", "XGL"):
        out.pop(code, None)
    return out


def cited(unit):
    """Slugs the ledger already carries."""
    path = os.path.join(REPORTS, unit, "ledger.csv")
    out = set()
    if not os.path.isfile(path):     # --slugs on a unit not yet initialised: everything is new
        return out
    import csv
    for row in csv.DictReader(io.open(path, encoding="utf-8", newline="")):
        if vault_lib.blank_csv_row(row):
            continue
        for s in (row.get("sources") or "").split("|"):
            if s.strip():
                out.add(s.strip())
    return out


def considered_path(unit):
    return os.path.join(REPORTS, unit, "considered.txt")


def considered(unit):
    p = considered_path(unit)
    if not os.path.isfile(p):
        return set()
    return {ln.strip() for ln in io.open(p, encoding="utf-8") if ln.strip()}


def held_slugs():
    """Slugs whose source is on `origin_status: hold` — read but not citable, so not considerable."""
    out = set()
    for r in vault_lib.load_index():
        d, fm = r.get("d") or {}, r.get("fm") or {}
        if d.get("kind") != "source" or d.get("folder") != "raw":
            continue
        if str(fm.get("origin_status") or "").strip().lower() == "hold":
            out.add(d.get("slug") or os.path.basename(r["path"])[:-3])
    return out


def mark(unit, slugs):
    """Record slugs as looked at — whether or not they moved a row. A source read once and found
    inert is never read again, which is what keeps the nightly cost proportional to the night.

    A source on `origin_status: hold` is the exception: it is unreadable, not inert, so marking it
    considered would consume it permanently and no pass would return to it once the hold cleared
    (post-run note 138 — 12 held sources across five units, and two RWA rows left unsettled)."""
    have = considered(unit) | held_slugs()
    # Strip before testing. A caller piping `--slugs` through a shell on Windows appends \r to
    # every argument, which matched nothing in `have`, wrote held sources into considered.txt and
    # left no trace — `considered()` strips on read, so the damage was invisible afterwards.
    clean = [s for s in (x.strip() for x in slugs) if s]
    # Refuse a slug that is not in this unit's own source set. Parallel unit passes that stage
    # their slug list under a shared filename can overwrite each other, and a foreign slug written
    # here is silent and permanent: it consumes nothing visible, but the unit it *belongs* to never
    # sees it again. Membership is the only test that catches it.
    own = sources_by_place().get(unit, set())
    alien = [s for s in clean if s not in own]
    if alien:
        sys.stderr.write(f"{unit}: refused {len(alien)} slug(s) not in this unit's source set: "
                         + ", ".join(alien[:5]) + ("…" if len(alien) > 5 else "") + "\n")
    new = [s for s in clean if s in own and s not in have]
    if new:
        with io.open(considered_path(unit), "a", encoding="utf-8", newline="\n") as fh:
            fh.write("\n".join(new) + "\n")
    return len(new)


def last_closed_month(today):
    y, m = int(today[:4]), int(today[5:7])
    return f"{y - 1}-12" if m == 1 else f"{y}-{m - 1:02d}"


def month_due(today):
    """The closed month owed an issue, or None. One repo-level marker, not one per unit: the
    cadence is the cycle's, and 54 copies of it is 54 chances to drift."""
    want = last_closed_month(today)
    done = ""
    if os.path.isfile(MONTH_MARK):
        done = io.open(MONTH_MARK, encoding="utf-8").read().strip()
    return want if want > done else None


BACKSTOP_DAYS = 14


def days_owed(today, month):
    """Days since the owed month closed. The monthly leg prefers a light night, but a preference
    that can be missed forever is a schedule nobody keeps: past BACKSTOP_DAYS any run issues it.
    Fourteen is more than two turns of a five-row rotation, so the backstop only fires when
    something actually went wrong — a re-cut rotation, or a run of failed nights."""
    import datetime
    y, m = int(month[:4]), int(month[5:7])
    closed = datetime.date(y + (m == 12), (m % 12) + 1, 1) - datetime.timedelta(days=1)
    return (datetime.date.fromisoformat(today) - closed).days


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--slugs", metavar="UNIT")
    ap.add_argument("--mark", nargs="+", metavar=("UNIT", "SLUG"))
    ap.add_argument("--seed", metavar="UNIT",
                    help="mark every source the unit currently holds as considered — what "
                         "initialisation owes, because it has already read the base")
    ap.add_argument("--month-due", action="store_true")
    ap.add_argument("--gate", action="store_true",
                    help="rotation gate: exit 0 if a closed month is owed an issue, 1 if not, "
                         "2 on error. A gated row is passed over when this is non-zero.")
    ap.add_argument("--close-month", metavar="YYYY-MM")
    ap.add_argument("--today", default=None)
    a = ap.parse_args()

    if a.mark:
        print(f"{a.mark[0]}: {mark(a.mark[0], a.mark[1:])} slug(s) marked considered")
        return
    if a.seed:
        held = sorted(sources_by_place().get(a.seed, set()))
        print(f"{a.seed}: seeded {mark(a.seed, held)} of {len(held)} held source(s)")
        return
    if a.close_month:
        io.open(MONTH_MARK, "w", encoding="utf-8", newline="\n").write(a.close_month + "\n")
        print(f"monthly issue closed for {a.close_month}")
        return

    today = a.today or __import__("datetime").date.today().isoformat()
    if a.gate:
        # Exit codes are the interface: 0 due, 1 not due, 2 error. A broken gate must not read
        # as "not due" — that would silently retire the night and every run would log a success.
        try:
            due = month_due(today)
        except Exception as exc:                                    # noqa: BLE001
            print(f"gate error: {exc}", file=sys.stderr)
            sys.exit(2)
        print(due or "not due")
        sys.exit(0 if due else 1)
    if a.month_due:
        due = month_due(today)
        if not due:
            print("none")
        else:
            n = days_owed(today, due)
            print(f"{due} owed {n}d"
                  + (f" — OVERDUE past {BACKSTOP_DAYS}d, issue tonight" if n > BACKSTOP_DAYS
                     else " — wait for the host night"))
        return

    by_place = sources_by_place()
    done = units()
    if a.slugs:
        left = sorted(by_place.get(a.slugs, set()) - cited(a.slugs) - considered(a.slugs))
        print("\n".join(left))
        return

    work, skipped = [], []
    for u in done:
        n = len(by_place.get(u, set()) - cited(u) - considered(u))
        if n:
            work.append({"unit": u, "unconsidered": n})
    for p, s in sorted(by_place.items()):
        if p not in done and len(s):
            skipped.append({"place": p, "sources": len(s)})

    due_json = month_due(today)
    if a.json:
        print(json.dumps({"month_due": due_json,
                          "month_days_owed": days_owed(today, due_json) if due_json else None,
                          "month_overdue": bool(due_json and days_owed(today, due_json) > BACKSTOP_DAYS),
                          "work": work, "uninitialised": skipped}, indent=1))
        return
    due = month_due(today)
    print(f"monthly issue due: {due or 'no'}")
    print(f"initialised units with unconsidered sources: {len(work)}")
    for w in sorted(work, key=lambda w: -w["unconsidered"]):
        print(f"  {w['unit']}  {w['unconsidered']}")
    print(f"uninitialised places holding sources: {len(skipped)}"
          + (" — " + ", ".join(f"{s['place']} {s['sources']}" for s in
                               sorted(skipped, key=lambda s: -s["sources"])[:8]) if skipped else ""))


if __name__ == "__main__":
    main()
