#!/usr/bin/env python3
"""rebuild.py — JOB 1: build Corpus-owned outputs/ from OSINT's read-only evidence.

The site is two jobs. This is the first.

  JOB 1 (this script)  OSINT (raw + wiki, read-only)  ->  Corpus outputs/
  JOB 2 (render)       Corpus outputs/                 ->  Corpus site/     (build/RENDER-RUNBOOK.md)

Corpus compiles, reports and analyses; OSINT collects and classifies. This driver reads
OSINT's committed raw/, index/ and lookups/ and writes only into Corpus's own outputs/.
**It never writes to OSINT.**

Job 1 has two kinds of work. The deterministic *compiles* below are pure functions of
raw/ and run here. The *report layer* (ledgers and narrative) and *topics* are model
authoring passes — report-render rebuilds their tables from the ledger and carries the
authored narrative across, but the authoring itself (initialisation from the wiki, the
nightly update from new sources, topics) is a model run, not this script. Those stages
are named below and left to the authoring pass; this driver produces everything scriptable
and renders whatever ledgers already exist.

Stages
  1. vocab      snapshot lookups/{countries.csv,taxonomy.md} -> build/vocab/   (so JOB 2
                never has to read outside outputs/ — NOTES-FOR-OSINT #9)
  2. catalogue  raw/ -> outputs/catalogue/{raw-catalogue.csv,json}
  3. finance    raw/ -> outputs/non-state-finance/ + outputs/budgets/ (+ all-nonstate.csv)
  4. update     REPORT-UPDATE — the ledgers' nightly move. `--scan` here prints the work order
                (units holding sources the ledger has not considered); the authoring itself is
                a model stage (see build/BUILD-RUNBOOK.md § Report update), which then calls
                report-scan --mark and report-render.
  5. reports    ledger -> outputs/reports/{unit}/*.md  (tables rebuilt, narrative carried)
  6. summary    what was produced

  OSINT_PATH   where OSINT is checked out (default: the mounted OSINT folder)
  python build/rebuild.py --all                 # vocab + catalogue + finance + scan + summary
  python build/rebuild.py --scan                # the report-update work order, only
  python build/rebuild.py --all --reports all   # ...and re-render every report's tables
  python build/rebuild.py --reports ZAF KEN     # re-render specific units only
"""
import argparse, csv, glob, json, os, shutil, subprocess, sys

CORPUS = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OSINT = os.environ.get("OSINT_PATH", "/sessions/dazzling-intelligent-brown/mnt/OSINT")
TOOLCHAIN = os.path.join(CORPUS, "build", "toolchain")
WORK = os.path.join(CORPUS, "build", ".workroot")     # gitignored; symlinks + a view onto outputs
OUTPUTS = os.path.join(CORPUS, "outputs")
VOCAB = os.path.join(CORPUS, "build", "vocab")


def setup_workroot():
    os.makedirs(WORK, exist_ok=True)
    os.makedirs(OUTPUTS, exist_ok=True)
    for name in ("raw", "index", "lookups"):
        link, target = os.path.join(WORK, name), os.path.join(OSINT, name)
        if os.path.islink(link) or os.path.exists(link):
            if os.path.realpath(link) == os.path.realpath(target):
                continue
            os.remove(link)
        os.symlink(target, link)
    for name, target in (("scripts", TOOLCHAIN), ("outputs", OUTPUTS)):
        link = os.path.join(WORK, name)
        if not (os.path.islink(link) and os.path.realpath(link) == os.path.realpath(target)):
            if os.path.islink(link) or os.path.exists(link):
                os.remove(link)
            os.symlink(target, link)


def run(*args):
    print("  $", " ".join(str(a) for a in args))
    subprocess.run([sys.executable, os.path.join("scripts", args[0]), *map(str, args[1:])],
                   cwd=WORK, check=True)


def snapshot_vocab():
    os.makedirs(VOCAB, exist_ok=True)
    for name in ("countries.csv", "taxonomy.md"):
        shutil.copyfile(os.path.join(OSINT, "lookups", name), os.path.join(VOCAB, name))
    print(f"  vocab -> build/vocab/ ({', '.join(os.listdir(VOCAB))})")


def scan_work_order():
    """The REPORT-UPDATE gate: which ledgers hold unconsidered sources in raw/.
    Prints the work order; the authoring is the model stage that follows."""
    p = subprocess.run([sys.executable, os.path.join("scripts", "report-scan.py"), "--json"],
                       cwd=WORK, capture_output=True, text=True)
    try:
        d = json.loads(p.stdout)
    except json.JSONDecodeError:
        print("  (scan produced no JSON)"); print(p.stdout[:400]); return
    work = d.get("work", [])
    total = sum(w["unconsidered"] for w in work)
    print(f"  {len(work)} units hold {total} unconsidered sources — REPORT-UPDATE authors these")
    for w in sorted(work, key=lambda w: -w["unconsidered"])[:12]:
        print(f"    {w['unit']}  {w['unconsidered']}")
    if len(work) > 12:
        print(f"    … and {len(work) - 12} more units")
    if d.get("month_overdue"):
        print(f"  month {d.get('month_due')} overdue by {d.get('month_days_owed')} days")


def summary():
    def count_csv(path):
        try:
            with open(path, encoding="utf-8-sig") as fh:
                return max(0, sum(1 for _ in fh) - 1)
        except FileNotFoundError:
            return "—"
    cat = count_csv(os.path.join(OUTPUTS, "catalogue", "raw-catalogue.csv"))
    deals = count_csv(os.path.join(OUTPUTS, "non-state-finance", "all-nonstate.csv"))
    fin = len(glob.glob(os.path.join(OUTPUTS, "non-state-finance", "*-nonstate.csv")))
    bud = len(glob.glob(os.path.join(OUTPUTS, "budgets", "*-budget.csv")))
    units = sorted(os.path.basename(p) for p in glob.glob(os.path.join(OUTPUTS, "reports", "*"))
                   if os.path.isdir(p))
    status = len(glob.glob(os.path.join(OUTPUTS, "reports", "*", "*-status.md")))
    print("\nJOB 1 outputs/ —")
    print(f"  catalogue records : {cat}")
    print(f"  finance places    : {fin}   deals : {deals}   budget files : {bud}")
    print(f"  report units      : {len(units)}   status docs : {status}")
    print(f"  -> {OUTPUTS}")


def main():
    ap = argparse.ArgumentParser(description="JOB 1 — build Corpus outputs/ from OSINT")
    ap.add_argument("--all", action="store_true", help="vocab + catalogue + finance + summary")
    ap.add_argument("--vocab", action="store_true")
    ap.add_argument("--catalogue", action="store_true")
    ap.add_argument("--finance", action="store_true")
    ap.add_argument("--scan", action="store_true", help="print the REPORT-UPDATE work order")
    ap.add_argument("--reports", nargs="*", metavar="ISO3",
                    help="re-render report tables for these units (or 'all')")
    a = ap.parse_args()
    setup_workroot()

    if a.all or a.vocab:
        print("stage 1 — vocab snapshot:"); snapshot_vocab()
    if a.all or a.catalogue:
        print("stage 2 — catalogue:"); run("build-catalogue.py")
    if a.all or a.finance:
        print("stage 3 — finance + budgets (all places):"); run("build-finance-page.py", "--all")
    if a.all or a.scan:
        print("stage 4 — report-update work order (authoring is the model stage that follows):")
        scan_work_order()

    units = a.reports or []
    if units == ["all"] or units == ["--all"]:
        units = sorted(os.path.basename(p) for p in glob.glob(os.path.join(OUTPUTS, "reports", "*"))
                       if os.path.isdir(p))
    if units:
        print(f"stage 4 — report tables ({len(units)} units):")
        for u in units:
            run("report-render.py", "--unit", u, "--render")

    summary()
    print("\nnot in this driver (model authoring / deferred): report initialisation from "
          "wiki, nightly report update, monthly narratives, topics.")


if __name__ == "__main__":
    main()
