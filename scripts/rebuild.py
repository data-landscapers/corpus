#!/usr/bin/env python3
"""rebuild.py — JOB 1: build Corpus-owned outputs/ from OSINT's read-only evidence.

The site is two jobs. This is the first.

  JOB 1 (this script)  OSINT (raw + wiki, read-only)  ->  Corpus outputs/
  JOB 2 (render)       Corpus outputs/                 ->  Corpus site/     (RENDER.md)

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
  1. vocab      snapshot lookups/{countries.csv,taxonomy.md} -> outputs/vocab/   (so JOB 2
                never has to read outside outputs/ — NOTES-FOR-OSINT #9)
  2. catalogue  raw/ -> outputs/catalogue/{raw-catalogue.csv,json}
  3. finance    raw/ -> outputs/non-state-finance/ + outputs/budgets/ (+ all-nonstate.csv)
  4. update     the report update — the ledgers' move. `--scan` here prints the work order
                (units holding sources the ledger has not considered); the authoring itself is
                a model stage (see BUILD.md § Report update), which then calls
                report-scan --mark and report-render.
  5. reports    ledger -> outputs/reports/{unit}/*.md  (tables rebuilt, narrative carried)
  6. summary    what was produced

  OSINT_PATH   where OSINT is checked out (default: the mounted OSINT folder)
  python scripts/rebuild.py --all                 # vocab + catalogue + finance + scan + summary
  python scripts/rebuild.py --scan                # the report-update work order, only
  python scripts/rebuild.py --all --reports all   # ...and re-render every report's tables
  python scripts/rebuild.py --reports ZAF KEN     # re-render specific units only
"""
import argparse, csv, glob, json, os, shutil, subprocess, sys

CORPUS = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OSINT = os.environ.get("OSINT_PATH", r"C:\OSINT")
TOOLCHAIN = os.path.join(CORPUS, "scripts")           # all .py live here now
WORK = os.path.join(CORPUS, "scripts", ".workroot")   # gitignored; symlinks + a view onto outputs
OUTPUTS = os.path.join(CORPUS, "outputs")
VOCAB = os.path.join(CORPUS, "outputs", "vocab")      # Job 2 reads vocab from outputs/ only


def _link_dir(link, target):
    """Point `link` at directory `target`, replacing whatever is there.

    Windows: a **junction** (`mklink /J`), which needs no privilege — unlike a
    symlink, which needs Developer Mode or elevation (WinError 1314). POSIX: a
    symlink, so this still works when run in the Cowork container for testing.
    Junctions are directory-only and local-disk-only; every link here is both.
    """
    # lexists, not islink-or-exists: a link whose target is gone reports False to
    # BOTH of those, so the old guard skipped the removal and mklink then failed
    # with "Cannot create a file when that file already exists". A broken link is
    # the normal state after OSINT moves or a container run leaves POSIX symlinks
    # behind, so this is the case that has to work, not the edge case.
    if os.path.lexists(link):
        try:
            os.rmdir(link)            # junction or empty dir: unlinks, leaves target
        except OSError:
            try:
                os.remove(link)       # symlink, broken or live
            except OSError:
                shutil.rmtree(link, ignore_errors=True)
    if os.name == "nt":
        # Capture the failure text: a bare exit code here costs an hour of guessing.
        p = subprocess.run(["cmd", "/c", "mklink", "/J", link, target],
                           capture_output=True, text=True)
        if p.returncode != 0:
            raise RuntimeError(
                f"mklink /J {link} -> {target} failed: "
                f"{(p.stdout + p.stderr).strip() or 'no output'}")
    else:
        os.symlink(target, link)


def setup_workroot():
    os.makedirs(WORK, exist_ok=True)
    os.makedirs(OUTPUTS, exist_ok=True)
    for name, target in (("raw", os.path.join(OSINT, "raw")),
                         ("index", os.path.join(OSINT, "index")),
                         ("lookups", os.path.join(OSINT, "lookups")),
                         ("scripts", TOOLCHAIN),
                         # `report-register-check.py` reads its word budgets from the skeletons in
                         # documentation/, so without this it dies on FileNotFoundError when run
                         # from the workroot — which is where BUILD.md tells stage 4 to run
                         # everything. Corpus's own directory, linked for the same reason outputs/
                         # is: one working directory for the whole stage.
                         ("documentation", os.path.join(CORPUS, "documentation")),
                         ("outputs", OUTPUTS)):
        _link_dir(os.path.join(WORK, name), target)


def run(*args):
    print("  $", " ".join(str(a) for a in args))
    subprocess.run([sys.executable, os.path.join("scripts", args[0]), *map(str, args[1:])],
                   cwd=WORK, check=True)


def snapshot_vocab():
    os.makedirs(VOCAB, exist_ok=True)
    for name in ("countries.csv", "taxonomy.md"):
        shutil.copyfile(os.path.join(OSINT, "lookups", name), os.path.join(VOCAB, name))
    print(f"  vocab -> outputs/vocab/ ({', '.join(os.listdir(VOCAB))})")


def scan_work_order():
    """The report-update gate: which ledgers hold unconsidered sources in raw/.
    Prints the work order; the authoring is the model stage that follows."""
    p = subprocess.run([sys.executable, os.path.join("scripts", "report-scan.py"), "--json"],
                       cwd=WORK, capture_output=True, text=True)
    try:
        d = json.loads(p.stdout)
    except json.JSONDecodeError:
        print("  (scan produced no JSON)"); print(p.stdout[:400]); return
    work = d.get("work", [])
    total = sum(w["unconsidered"] for w in work)
    print(f"  {len(work)} units hold {total} unconsidered sources — stage 4 authors these")
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
        print(f"stage 5 — report tables ({len(units)} units):")
        for u in units:
            # `--doc all`, not the default status report *(2026-08-14)*. Each unit issues three
            # living documents and a moved row can show in any of them, so re-rendering only the
            # live one leaves the monthly and the progress report behind their own ledger — which
            # is exactly what check J then reports. `--doc all` means all of *this* unit's
            # documents, so a region still renders only its progress report.
            run("report-render.py", "--unit", u, "--doc", "all", "--render")

    summary()
    print("\nnot in this driver (model authoring / deferred): report initialisation from "
          "wiki, nightly report update, monthly narratives, topics.")


if __name__ == "__main__":
    main()
