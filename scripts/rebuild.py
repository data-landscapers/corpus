#!/usr/bin/env python3
"""rebuild.py — JOB 1: build Corpus-owned outputs/ from OSINT's read-only evidence.

The site is two jobs. This is the first.

  JOB 1 (this script)  OSINT (raw + wiki, read-only)  ->  Corpus outputs/
  JOB 2 (render)       Corpus outputs/                 ->  Corpus site/     (RENDER.md)

Corpus compiles, reports and analyses; OSINT collects and classifies. This driver reads
raw/, wiki/ and lookups/ through the junctions setup_workroot() makes, indexes raw/ and
wiki/ into an index of its own, and writes only into Corpus's own outputs/. **It never
writes to OSINT.**

**What those junctions resolve to is the mirror, not OSINT's working tree** *(corrected
2026-08-22, `notes-for-corpus.md` note 5)*. Since 2026-08-20 OSINT works on its own
machine's `C:\\OSINT` and syncs to `O:\\` = `\\\\bill-vivobook\\osint` as the last act of
`SWEEP-CYCLE`; this is bill-vivobook, so that share resolves back to *this* machine's
`C:\\OSINT`, which is therefore the mirror's landing point and the only OSINT path Corpus
can name. `O:\\` is not mapped here and would loop back to the same folder if it were.
`scripts/lint-osint-freshness.py` is what says how old that copy is — it used to say
nothing, which is the whole of note 5.

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

  OSINT_PATH   where the OSINT mirror is (legacy alias; CORPUS_OSINT_MIRROR is the name
               osint_lib and the rest of Corpus use, and supplies the default)
  python scripts/rebuild.py --all                 # vocab + catalogue + finance + scan + summary
  python scripts/rebuild.py --scan                # the report-update work order, only
  python scripts/rebuild.py --all --reports all   # ...and re-render every report's tables
  python scripts/rebuild.py --reports ZAF KEN     # re-render specific units only
"""
import argparse, csv, glob, json, os, shutil, subprocess, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import osint_lib  # noqa: E402  — for MIRROR, the one path to OSINT Corpus states
import vault_lib  # noqa: E402  — for INDEX_ROOTS; see setup_workroot()

CORPUS = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# **One default, three names, and this was the third copy** *(2026-08-22)*. `osint_lib` was
# made the single constant because `osint-cycle-ready.py` and `bulletin.py` were about to hold
# two; this file already held a third, under its own `OSINT_PATH`, and a path to another
# repository stated in three places is one that will one day be moved in two of them.
# `OSINT_PATH` still wins where it is set — an environment variable that silently stops being
# read is worse than a second name for it — but the default now comes from `osint_lib.MIRROR`,
# so `CORPUS_OSINT_MIRROR` moves this along with everything else.
OSINT = os.environ.get("OSINT_PATH") or osint_lib.MIRROR
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


def _unlink_foreign(path):
    """Remove `path` if it is a link pointing outside Corpus. A real directory is left alone.

    Dropping a name from the link list is not enough on its own: `.workroot/index` was a junction
    to `C:\\OSINT\\index`, and an unlisted junction simply stays, so every read would still go to
    OSINT and the change would look applied while doing nothing. Removing a junction unlinks it
    and leaves its target untouched — but a *real* directory here is Corpus's own index, which
    must survive, hence the resolve-and-compare rather than a blind delete."""
    if not os.path.lexists(path):
        return
    real = os.path.realpath(path)
    try:
        inside = os.path.commonpath([os.path.realpath(CORPUS), real]) == os.path.realpath(CORPUS)
    except ValueError:                                  # different drives
        inside = False
    if inside:
        return
    print(f"  workroot: unlinking {os.path.basename(path)} -> {real} (Corpus owns its index now)")
    try:
        os.rmdir(path)                                  # junction: unlinks, leaves the target
    except OSError:
        os.remove(path)                                 # symlink


def setup_workroot():
    """Link the workroot at OSINT's evidence and Corpus's own trees.

    **`index/` is deliberately not junctioned** *(Bill, 2026-08-14)*. It is the one thing here
    Corpus does not read out of OSINT, and not junctioning it is what ends the dependency: with
    no link, `vault_lib.INDEX_DIR` resolves to a real directory *inside* the workroot, so Corpus
    builds and owns its index, `_assert_own_index()` is satisfied by construction, and
    `ensure_fresh()` may rebuild the moment `raw/` or `wiki/` moves. An index is a cache of a
    tree Corpus can already read in full; nothing about it needs to be the same *file* OSINT
    uses, and sharing it made a Corpus build wait on an OSINT maintenance step it cannot run.
    The workroot is gitignored, so the cache is untracked wherever it lands.

    **Junction only what a stage reads.** Every entry below is a directory exposed to a process
    that can write, so the list is a boundary surface and is kept as small as the build allows.
    `raw/` and `wiki/` are the evidence (`INDEX_ROOTS`), `lookups/` the vocabularies. *(The six
    other roots OSINT's index walks were junctioned earlier today to satisfy a freshness check
    against OSINT's copy; Corpus owning the index removes the reason, and with it the path by
    which `finance-compile-scope.py --commit` would have written into `C:\\OSINT\\reviews\\`.)*

    **Corpus may read anything in OSINT** *(Bill, 2026-08-14)* — this list is what the build
    needs, not what it is allowed. The boundary is one-directional: nothing here ever writes.
    """
    os.makedirs(WORK, exist_ok=True)
    os.makedirs(OUTPUTS, exist_ok=True)
    links = (*((r, os.path.join(OSINT, r)) for r in vault_lib.INDEX_ROOTS),
             ("lookups", os.path.join(OSINT, "lookups")),
             ("scripts", TOOLCHAIN),
             # `report-register-check.py` reads its word budgets from the skeletons in
             # documentation/, so without this it dies on FileNotFoundError when run
             # from the workroot — which is where BUILD.md tells stage 4 to run
             # everything. Corpus's own directory, linked for the same reason outputs/
             # is: one working directory for the whole stage.
             ("documentation", os.path.join(CORPUS, "documentation")),
             ("outputs", OUTPUTS))
    # Withdraw first, then link. A link this list no longer names is a door left open into
    # OSINT — `index/` as of today, and any root a future narrowing drops — so the sweep runs
    # every time rather than as a one-off migration. Only links out of Corpus are removed;
    # a real directory (the index Corpus now builds here) is never touched.
    for name in sorted(os.listdir(WORK)):
        if name not in {n for n, _ in links}:
            _unlink_foreign(os.path.join(WORK, name))
    for name, target in links:
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


def scope_lint():
    """The geographic remit, checked on the catalogue stage 2 has just written.

    **Belts and braces on a rule OSINT owns** *(Bill, 2026-08-20)*. The remit — Africa,
    plus `geopol.*` sovereignty material, plus `XGL` material on the global south — is
    OSINT's to apply at ingest, and Corpus cannot enforce it: the records are OSINT's and
    `C:\\OSINT` is read-only. What Corpus can do is notice, on the run that admits them,
    that something arrived carrying no account of its geography at all.

    **It reports and never gates.** `BUILD.md` → *No check stops a finished run*
    is the rule and nothing in Job 1 is an exception: an out-of-remit record is a work item for
    OSINT, not a reason to withhold a build of the other ten thousand. A non-zero count
    goes in the run's log line and, where it is new, into a note for OSINT."""
    rc = subprocess.run([sys.executable, os.path.join("scripts", "lint-scope.py"), "--list", "5"],
                        cwd=WORK).returncode
    if rc == 2:
        print("  scope lint: no catalogue to read — skipped")


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
        # The names index reads the bodies and keys on the catalogue's own slugs,
        # so it belongs to this stage and must follow it. `catalogue.py` (RENDER
        # step 5) then packs the shard keys into the page.
        print("stage 2b — names index:"); run("build-names-index.py")
        # Display names for entity slugs. Reads the same bodies as 2b and depends on
        # the same catalogue, so it belongs here; hand corrections in
        # `lookups/entity-names.csv` survive a rebuild.
        print("stage 2c — entity display names:"); run("build-entity-names.py")
        print("stage 2a — scope lint (reports, never gates):"); scope_lint()
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
