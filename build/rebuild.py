#!/usr/bin/env python3
"""rebuild.py — regenerate Corpus-owned outputs/ from OSINT's read-only evidence.

Corpus compiles, reports and analyses; OSINT collects and classifies. This driver
reads OSINT's committed raw/, index/ and lookups/ (never writing to them) and rebuilds
the derived layer Corpus owns and serves: the catalogue, the non-state-finance and
budget CSVs, and the report-table renders (narrative blocks are authored per report and
carried across untouched by report-render).

The toolchain in build/toolchain/ resolves paths against its own parent as repo ROOT,
so we run it from a work root whose raw/, index/, lookups/ are read-only symlinks into
OSINT and whose outputs/ is Corpus's own tree.

  OSINT_PATH   where OSINT is checked out (default: the mounted OSINT folder)
  python build/rebuild.py --catalogue --finance --reports ZAF
  python build/rebuild.py --all           # catalogue + finance(all) + all report tables
"""
import argparse, os, subprocess, sys, glob

CORPUS = os.path.dirname(os.path.abspath(__file__ + "/.."))
CORPUS = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OSINT = os.environ.get("OSINT_PATH", "/sessions/dazzling-intelligent-brown/mnt/OSINT")
TOOLCHAIN = os.path.join(CORPUS, "build", "toolchain")
WORK = os.path.join(CORPUS, "build", ".workroot")     # gitignored; symlinks + a view onto outputs
OUTPUTS = os.path.join(CORPUS, "outputs")

def setup_workroot():
    os.makedirs(WORK, exist_ok=True)
    os.makedirs(OUTPUTS, exist_ok=True)
    for name in ("raw", "index", "lookups"):
        link = os.path.join(WORK, name)
        target = os.path.join(OSINT, name)
        if os.path.islink(link) or os.path.exists(link):
            if os.path.realpath(link) == os.path.realpath(target):
                continue
            os.remove(link)
        os.symlink(target, link)
    # scripts and outputs are views, not copies
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

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--catalogue", action="store_true")
    ap.add_argument("--finance", action="store_true")
    ap.add_argument("--reports", nargs="*", metavar="ISO3",
                    help="render report tables for these units (carries narrative across)")
    a = ap.parse_args()
    setup_workroot()
    if a.all or a.catalogue:
        print("catalogue:"); run("build-catalogue.py")
    if a.all or a.finance:
        print("finance (all places):"); run("build-finance-page.py", "--all")
    units = a.reports if a.reports else (["--all"] if a.all else [])
    if units == ["--all"]:
        units = sorted(os.path.basename(p) for p in glob.glob(os.path.join(OUTPUTS, "reports", "*"))
                       if os.path.isdir(p))
    for u in units:
        print(f"report tables: {u}"); run("report-render.py", "--unit", u, "--render")
    print("done ->", OUTPUTS)

if __name__ == "__main__":
    main()
