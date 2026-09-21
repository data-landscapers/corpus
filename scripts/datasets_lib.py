"""datasets_lib.py — read, write, check and log the datasets under outputs/datasets/.

A dataset is maintained, never rebuilt (documentation/datasets.md §1): every change goes
through `write()` and is recorded by `log()`. Nothing here decides what changes.

Layout, per dataset:
  outputs/datasets/{name}/{name}.csv   the master, one row per record, columns in metadata order
  outputs/datasets/{name}/metadata.csv the field dictionary (column, v2_name, label, type,
                                       values, derived, definition, guidance)
  logs/dataset-updates.csv             every change to every dataset, newest row first
"""
import csv, datetime, io, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATASETS = ROOT / "outputs" / "datasets"
LOG = ROOT / "logs" / "dataset-updates.csv"
LOG_HEADER = ["dataset", "date", "record", "action", "details", "sources"]
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


def next_id(rows, iso3, id_col="facility_id"):
    """The next free ID in a country. Retired rows stay in the master, so an ID is never reissued."""
    n = [int(r[id_col][4:]) for r in rows if r[id_col].startswith(iso3 + "-")]
    return f"{iso3}-{(max(n) if n else 0) + 1:03d}"


def log(dataset, record, action, details, sources="", date=None):
    """Add a change to logs/dataset-updates.csv, directly under the header (newest first)."""
    if action not in ACTIONS:
        raise ValueError(f"action must be one of {sorted(ACTIONS)}")
    row = {"dataset": dataset, "date": date or datetime.date.today().isoformat(),
           "record": record, "action": action, "details": details, "sources": sources}
    old = []
    if LOG.exists():
        with open(LOG, encoding="utf-8", newline="") as f:
            old = list(csv.DictReader(f))
    _put(LOG, _csv_text(LOG_HEADER, [row] + old))
