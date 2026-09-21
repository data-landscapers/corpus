"""datasets_lib.py — read, write, check and log the datasets under outputs/datasets/.

A dataset is maintained, never rebuilt (documentation/datasets.md §1): every change goes
through `write()` and is recorded by `log()`. Nothing here decides what changes.

Layout, per dataset:
  outputs/datasets/{name}/{name}.csv   the master, one row per record, columns in metadata order
  outputs/datasets/{name}/metadata.csv the field dictionary (column, v2_name, label, type,
                                       values, derived, definition, guidance)
  logs/dataset-updates.csv             every change to every dataset, newest row first

**The log carries two accounts of each change** *(Bill, 2026-09-21)*. `details` is the working
record — which field, which pass, how many sources — and `summary` is the sentence a reader sees
under the table and in the changes download: what happened to the facility, in plain English.
Rows logged before the column existed have no summary and are not back-filled; the page shows
their `details` instead.
"""
import csv, datetime, io, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATASETS = ROOT / "outputs" / "datasets"
LOG = ROOT / "logs" / "dataset-updates.csv"
LOG_HEADER = ["dataset", "date", "record", "action", "details", "sources", "summary"]
ACTIONS = {"import", "add", "modify", "retire"}


def master_path(name):
    return DATASETS / name / f"{name}.csv"


def metadata(name):
    with open(DATASETS / name / "metadata.csv", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def columns(name):
    return [m["column"] for m in metadata(name)]


def read(name):
    with open(master_path(name), encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def _csv_text(header, rows):
    # LF endings whatever the platform: the master feeds dated editions, and an edition that
    # differs only in line endings is still a new edition (RENDER.md -> The finance tables).
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=header, lineterminator="\n", extrasaction="raise")
    w.writeheader()
    w.writerows(rows)
    return buf.getvalue()


def _put(path, text):
    """Write, retrying briefly: on Windows a reader holding the file open (a sync client, an agent
    reading the log) makes a write fail with EINVAL, and an apply that dies between the master and
    the log leaves the two disagreeing (T7, 2026-09-21)."""
    import time
    for i in range(8):
        try:
            path.write_text(text, encoding="utf-8", newline="")
            return
        except OSError:
            if i == 7:
                raise
            time.sleep(0.5 * (i + 1))


def write(name, rows):
    """Write the master in metadata column order. Refuses a row with an unknown column."""
    cols = columns(name)
    for r in rows:
        extra = set(r) - set(cols)
        if extra:
            raise ValueError(f"{r.get(cols[0])}: columns not in metadata: {sorted(extra)}")
    ids = [r[cols[0]] for r in rows]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate record IDs")
    master_path(name).parent.mkdir(parents=True, exist_ok=True)
    _put(master_path(name), _csv_text(cols, [{c: r.get(c, "") for c in cols} for r in rows]))


def check(name, rows=None):
    """Values outside a category's allowed set, and IDs out of form. Returns a list of strings."""
    rows = read(name) if rows is None else rows
    out = []
    meta = metadata(name)
    key = meta[0]["column"]
    for m in meta:
        c = m["column"]
        if m["type"] == "category":
            allowed = {v.strip() for v in m["values"].split(";")}
            for r in rows:
                if r.get(c, "") and r[c] not in allowed:
                    out.append(f"{r[key]}: {c} = {r[c]!r}")
        elif m["type"] == "id":
            for r in rows:
                if not re.fullmatch(r"[A-Z]{3}-\d{3}", r.get(c, "")):
                    out.append(f"{c} out of form: {r.get(c)!r}")
    return out


def retired_path(name):
    return DATASETS / name / "retired.csv"


def retired(name):
    p = retired_path(name)
    if not p.exists():
        return []
    with open(p, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def retire(name, rows, record_id, reason, date=None, id_col="facility_id"):
    """Take a record out of the master into `retired.csv`, with the date and the reason: a duplicate
    of another record, or a facility no source shows exists. The dated editions that carried it are
    never revised, so a citation to one still resolves; `next_id` reads this file too, so the ID is
    never reissued. Returns the rows left. The caller writes the master and logs `retire`."""
    keep = [r for r in rows if r[id_col] != record_id]
    gone = [r for r in rows if r[id_col] == record_id]
    if len(gone) != 1:
        raise ValueError(f"{record_id}: not in the master")
    row = {"retired": date or datetime.date.today().isoformat(), "retired_reason": reason, **gone[0]}
    old = retired(name)
    header = ["retired", "retired_reason"] + columns(name)
    _put(retired_path(name), _csv_text(header, old + [{c: row.get(c, "") for c in header}]))
    return keep


def next_id(rows, iso3, id_col="facility_id", name="data-centres"):
    """The next free ID in a country, counting retired records, so an ID is never reissued."""
    n = [int(r[id_col][4:]) for r in list(rows) + retired(name) if r[id_col].startswith(iso3 + "-")]
    return f"{iso3}-{(max(n) if n else 0) + 1:03d}"


def log(dataset, record, action, details, sources="", date=None, summary=""):
    """Add a change to logs/dataset-updates.csv, directly under the header (newest first).

    `summary` is reader-facing: a sentence in plain English, no field names or pass names."""
    if action not in ACTIONS:
        raise ValueError(f"action must be one of {sorted(ACTIONS)}")
    row = {"dataset": dataset, "date": date or datetime.date.today().isoformat(),
           "record": record, "action": action, "details": details, "sources": sources,
           "summary": summary}
    old = []
    if LOG.exists():
        with open(LOG, encoding="utf-8", newline="") as f:
            old = list(csv.DictReader(f))
    _put(LOG, _csv_text(LOG_HEADER, [row] + old))
