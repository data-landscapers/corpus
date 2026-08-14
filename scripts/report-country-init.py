#!/usr/bin/env python3
"""
report-country-init.py — standing. The country report layer's initialisation shell
(`REPORT-COUNTRY.md` -> Initialisation; the record layer it shells is `documentation/report-layer.md`).

**The folder is the state.** A place is *initialised* when `outputs/reports/{ISO3}/ledger.csv`
exists and *outstanding* when it does not — there is no queue file to drift out of step with
the tree, exactly as `new/ -> raw/` carries its own state.

Say how many places you have time for and it takes that many off the top of the outstanding
list, deepest base first, creates each shell, and prints the work order the run needs before
it reads anything: how much the base holds, how it is distributed over the last fourteen
months (the coverage cliff that decides whether a period comparison can honestly be
promised), which intersection pages exist, and which subjects have substantive coverage
mapped to their report sections.

It reads and it creates empty shells. It writes no report and no ledger row — those are the
run's, and the run is a model reading sources.

Usage:
  python scripts/report-country-init.py --status            what is done, what is next
  python scripts/report-country-init.py --count 6           take the next six, create their shells
  python scripts/report-country-init.py --country ZAF KEN   these, in this order
  python scripts/report-country-init.py --count 6 --dry-run print the work order, create nothing
Exit: 0 always, unless there is nothing outstanding to take (1).
"""
import argparse
import collections
import csv
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vault_lib  # noqa: E402

ROOT = vault_lib.ROOT
REPORTS = os.path.join(ROOT, "outputs", "reports")
SECTIONS_CSV = os.path.join(ROOT, "lookups", "report-country-sections.csv")
COUNTRIES_CSV = os.path.join(ROOT, "lookups", "countries.csv")

LEDGER_COLUMNS = ["row_id", "place", "subject", "section", "kind", "name", "status", "as_at", "milestone",
                  "since", "prior_status", "prior_as_at", "movement",
                  "position_start", "position_end", "sources", "probe_at", "note"]
GAPS_COLUMNS = ["row_id", "place", "subject", "section", "name", "what_would_settle_it",
                "probe_at", "disposition"]

WINDOW = 14          # months of history printed
CLIFF_RATIO = 3.0    # later half this many times the earlier half = a cliff worth saying


def places_from_csv():
    """ISO-3 codes, countries only — regions are not report units."""
    out = []
    with open(COUNTRIES_CSV, encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            code = (row.get("iso-3") or "").strip()
            if code and not code.startswith("X"):
                out.append((code, (row.get("country-name") or "").strip()))
    return out


def section_map():
    with open(SECTIONS_CSV, encoding="utf-8", newline="") as fh:
        return {r["subject"]: r["section"] for r in csv.DictReader(fh)}


def base_shape(rows):
    """Per place: source count, month histogram, subject counter, intersection pages."""
    sources = collections.Counter()
    months = collections.defaultdict(collections.Counter)
    subjects = collections.defaultdict(collections.Counter)
    inters = collections.defaultdict(list)
    for r in rows:
        d, fm = r.get("d") or {}, r.get("fm") or {}
        if d.get("folder") == "raw" and d.get("kind") == "source":
            month = str(fm.get("published") or "")[:7]
            if not re.fullmatch(r"\d{4}-\d{2}", month):
                month = ""
            for p in vault_lib.as_list(fm.get("places")):
                sources[p] += 1
                if month:
                    months[p][month] += 1
                for t in vault_lib.as_list(fm.get("topics")):
                    subjects[p][str(t)] += 1
        elif r.get("path", "").startswith("wiki/intersections/"):
            place = str(fm.get("place") or "")
            if place:
                inters[place].append((str(fm.get("topic") or "?"), r["path"]))
    return sources, months, subjects, inters


def initialised(code):
    """A shell with a header-only ledger is NOT initialised — it is an interrupted run.

    The folder is the state, but the state is *rows*: a run that created the shell and stopped
    before writing a ledger row must come back as outstanding, or the interruption reads as
    completed work.

    An **all-empty row does not count**. Opening a ledger in an editor can leave a trailing
    newline behind, which `csv.DictReader` returns as a row of empty strings — and a header-only
    shell plus one of those would read as initialised, so `--count N` would skip that country for
    good. The same skip is in `report-render.py`'s loader, for the same reason."""
    path = os.path.join(REPORTS, code, "ledger.csv")
    if not os.path.exists(path):
        return False
    with open(path, encoding="utf-8", newline="") as fh:
        return any(not vault_lib.blank_csv_row(r) for r in csv.DictReader(fh))


def create_shell(code):
    folder = os.path.join(REPORTS, code)
    os.makedirs(folder, exist_ok=True)
    for name, cols in (("ledger.csv", LEDGER_COLUMNS), ("gaps.csv", GAPS_COLUMNS)):
        path = os.path.join(folder, name)
        if os.path.exists(path):
            # A shell left by an interrupted run predates any column the schema has gained since.
            # Rewrite its header while it is still empty; never touch a file that has rows, which
            # is a migration and not this function's business.
            with open(path, encoding="utf-8", newline="") as fh:
                rd = csv.reader(fh)
                head = next(rd, None)
                has_rows = any(any((c or "").strip() for c in row) for row in rd)
            if head == cols or has_rows:
                continue
        with open(path, "w", encoding="utf-8", newline="") as fh:
            csv.writer(fh).writerow(cols)
    return folder


def work_order(code, name, sources, months, subjects, inters, secmap):
    total = sources.get(code, 0)
    hist = months.get(code, collections.Counter())
    keys = sorted(hist)[-WINDOW:]
    print(f"\n=== {code} — {name} ===")
    print(f"  base: {total} sources held")
    if keys:
        print("  by month: " + "  ".join(f"{k[5:]}:{hist[k]}" for k in keys))
        half = len(keys) // 2
        early = sum(hist[k] for k in keys[:half]) or 0
        late = sum(hist[k] for k in keys[half:]) or 0
        if early == 0 or late / max(early, 1) >= CLIFF_RATIO:
            print(f"  ** COVERAGE CLIFF: {early} sources in the earlier half against {late} in the later.")
            print("     Narrow the window, or say in the document that it is a shorter comparison"
                  " wearing a longer label (documentation/report-layer.md 7).")
    pages = sorted(inters.get(code, []))
    print(f"  intersection pages: {len(pages)}" + (" — the primary input" if pages else " — none; read the hub's Active topics"))
    for topic, path in pages:
        kb = os.path.getsize(os.path.join(ROOT, path)) // 1024
        print(f"     {topic:<18} {path}  ({kb}KB)")
    subs = subjects.get(code, collections.Counter())
    covered = [(n, s) for s, n in subs.items() if n >= 3 and s in secmap]
    covered.sort(reverse=True)
    print(f"  subjects with 3+ sources: {len(covered)} of {len(secmap)}")
    by_section = collections.defaultdict(list)
    for n, s in covered:
        by_section[secmap.get(s, "(unmapped)")].append(f"{s}:{n}")
    for sec in sorted(by_section):
        print(f"     {sec}: " + ", ".join(by_section[sec][:8]))
    thin = [s for s in secmap if subs.get(s, 0) == 0]
    print(f"  subjects with nothing held: {len(thin)} — these are Not held rows, and gaps.csv lines")
    hub = os.path.join("wiki", "places", f"{code}.md")
    if os.path.exists(os.path.join(ROOT, hub)):
        print(f"  hub: {hub.replace(os.sep, '/')} ({os.path.getsize(os.path.join(ROOT, hub)) // 1024}KB)"
              " — grep headings, read by range; never open it whole")


def main():
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--count", type=int, help="take this many outstanding places")
    ap.add_argument("--country", nargs="+", help="these places, in this order")
    ap.add_argument("--order", choices=("depth", "alpha"), default="depth",
                    help="depth = deepest base first (default); alpha = by country name, "
                         "so successive sessions walk the alphabet — initialised countries "
                         "drop off the list by themselves")
    ap.add_argument("--status", action="store_true", help="what is initialised and what is next")
    ap.add_argument("--dry-run", action="store_true", help="print the work order, create nothing")
    args = ap.parse_args()

    rows = vault_lib.load_index()
    sources, months, subjects, inters = base_shape(rows)
    secmap = section_map()
    names = dict(places_from_csv())
    done = [c for c in names if initialised(c)]
    key = ((lambda c: (names[c], c)) if args.order == "alpha"
           else (lambda c: (-sources.get(c, 0), c)))
    outstanding = sorted((c for c in names if c not in done), key=key)

    if args.status or not (args.count or args.country):
        print(f"country reports: {len(done)} of {len(names)} initialised, {len(outstanding)} outstanding")
        if done:
            print("  initialised: " + " ".join(sorted(done)))
        print("  next up (%s):" % ("alphabetical" if args.order == "alpha" else "deepest base first"))
        for c in outstanding[:12]:
            print(f"     {c} {names[c]:<28} {sources.get(c, 0):4d} sources")
        if not args.status:
            print("\n  --count N to take the next N; --country XXX to override the order")
        return 0

    if args.country:
        take = [c.upper() for c in args.country]
        unknown = [c for c in take if c not in names]
        if unknown:
            print("not places in countries.csv:", " ".join(unknown))
            return 1
    else:
        take = outstanding[:args.count]
    if not take:
        print("nothing outstanding — every place has a ledger")
        return 1

    print(f"taking {len(take)}: " + " ".join(take))
    for code in take:
        if initialised(code) and not args.country:
            continue
        work_order(code, names[code], sources, months, subjects, inters, secmap)
        if args.dry_run:
            print("  (dry run — no shell created)")
        else:
            print("  shell: " + os.path.relpath(create_shell(code), ROOT))
    print("\nNow run REPORT-COUNTRY.md step 3 for each — read the compiled layer, not the hub whole.")
    print("Format, register and the drafting contract: documentation/report-country-skeleton.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
