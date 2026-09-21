#!/usr/bin/env python3
"""dataset-scan.py — the script gate of the datasets stage (BUILD.md stage 4b; datasets.md T7).

Which raw/ records a dataset has not yet considered, and the packet a model reads to decide them.
Run from `scripts/.workroot/`, like `report-scan.py`, whose set-difference logic this follows: a
record counts as unconsidered until its slug is in the dataset's `considered.txt`, so an
interrupted run repeats exactly what it did not finish and the nightly cost is the night's.

    python scripts/dataset-scan.py                              # the work order, by place
    python scripts/dataset-scan.py --slugs data-centres [PLACE] # unconsidered candidate slugs
    python scripts/dataset-scan.py --packet data-centres PLACE [--parts N]   # PLACE may be ALL
    python scripts/dataset-scan.py --apply data-centres PLACE [--dry-run]
    python scripts/dataset-scan.py --seed data-centres SLUG ... # mark without a decision (baseline)

**The trigger** (datasets.md §2): a record is a candidate if it carries an `infra.store` topic, or
its title or hub_line names a data centre. Records on `origin_status: hold` are left out, as in
stage 4: unreadable is not inert.

**A record belongs to one place**, the first in its `places`, so a record naming three countries
is read once. Its packet shows the current rows of every country the packet's records name, and a
decision may change any of them.

**The decisions file** (`prep/dc-evidence/t7/{PLACE}/decisions*.json`) accounts for every slug in
its packet, and applying it marks exactly those slugs considered:

    {"considered": {"<slug>": "<one line: what it changed, or why nothing>", ...},
     "rows": {
       "KEN-003": {"edits": {"<field>": {"value": "...", "why": "..."}},
                   "add_slugs": ["<slug>"], "to_source": {...}, "resolves": [...]},
       "new:1":   {"fields": {"facility_name": "...", "country": "KEN", ...},
                   "add_slugs": ["<slug>"], "why": "<one line: why this is a new facility>"}}}

`add_slugs` puts the record's URL in `source_urls` and its slug in `raw_slugs`: a raw record is
already in the catalogue, so nothing is staged. A new row takes the next free ID in its country.
The rules a reader applies are T6's (`scripts/dataset-evidence.py` docstring, and
`prep/dc-evidence/BRIEF.md`), plus: **a record moves a row only where it states something newer or
more specific than the row**, and **most records change nothing** — an announcement a row already
reflects is considered and left.
"""
from __future__ import annotations
import argparse, collections, csv, datetime, importlib.util, io, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import vault_lib  # noqa: E402
import datasets_lib as dl  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

_spec = importlib.util.spec_from_file_location("de", os.path.join(HERE, "dataset-evidence.py"))
de = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(de)

TRIGGER = re.compile(r"data cent(?:re|er)|colocation|hyperscale|tier (?:III|IV)", re.I)
WORK = dl.ROOT / "prep" / "dc-evidence" / "t7"
BODY = 6000       # body excerpt per record


def considered_path(name):
    return dl.DATASETS / name / "considered.txt"


def considered(name):
    p = considered_path(name)
    return {ln.strip() for ln in io.open(p, encoding="utf-8") if ln.strip()} if p.exists() else set()


def topics(fm):
    t = fm.get("topics") or []
    return [str(x) for x in (t if isinstance(t, list) else [t])]


def candidates(name):
    """{slug: index row} for every raw record the dataset's trigger selects."""
    if name != "data-centres":
        sys.exit(f"no trigger defined for {name}")
    out = {}
    for r in vault_lib.load_index(quiet=True):
        d, fm = r.get("d") or {}, r.get("fm") or {}
        if d.get("kind") != "source" or d.get("folder") != "raw":
            continue
        if str(fm.get("origin_status") or "").strip().lower() == "hold":
            continue
        text = f"{fm.get('title', '')} {fm.get('hub_line', '')}"
        if any(t.startswith("infra.store") for t in topics(fm)) or TRIGGER.search(text):
            out[d.get("slug") or os.path.basename(r["path"])[:-3]] = r
    return out


def place(r):
    p = (r.get("fm") or {}).get("places") or []
    return str(p[0]).strip() if p else "XGL"


def pending(name, where=None):
    have = considered(name)
    c = {s: r for s, r in candidates(name).items() if s not in have}
    if where and where != "ALL":  # ALL: the night's arrivals, whatever their place
        c = {s: r for s, r in c.items() if place(r) == where}
    return dict(sorted(c.items()))


def work_order(name):
    c = pending(name)
    by = collections.Counter(place(r) for r in c.values())
    print(f"{name}: {len(c)} unconsidered of {len(candidates(name))} candidates")
    for p, n in sorted(by.items(), key=lambda kv: (-kv[1], kv[0])):
        print(f"  {p} {n}")


def row_line(r):
    keep = ("facility_name", "city", "operational_status", "year_operational", "facility_type", "operator_name",
            "ultimate_parent_company", "it_capacity_mw", "rack_capacity", "total_floor_space_sqm",
            "investment_usd", "expansion_plans", "hyperscaler_relationships", "chinese_involvement",
            "chinese_entities", "control_category")
    return f"- **{r['facility_id']}** " + " | ".join(f"{k}: {r[k]}" for k in keep if r[k])


def packet(name, where, parts=1):
    c = pending(name, where)
    if not c:
        print(f"{where}: nothing unconsidered")
        return
    rows = dl.read(name)
    slugs = list(c)
    size = -(-len(slugs) // parts)
    for k in range(parts):
        chunk = slugs[k * size:(k + 1) * size]
        if not chunk:
            continue
        named = {str(p).strip() for s in chunk for p in (c[s]["fm"].get("places") or [])} | {where}
        out = [f"# T7 packet — {name}, {where}" + (f", part {k + 1} of {parts}" if parts > 1 else "")
               + f": {len(chunk)} record(s)", "",
               "Method: `scripts/dataset-scan.py` docstring. Every slug below needs an entry under "
               "`considered` in your decisions file.", "",
               "## Current rows in the countries these records name", ""]
        for r in rows:
            if r["country"] in named:
                out.append(row_line(r))
        out += ["", "## Every facility in the dataset (to catch one listed under another country)", "",
                "; ".join(f"{r['facility_id']} {r['facility_name']}" for r in rows), "", "## Records", ""]
        for s in chunk:
            r = c[s]
            fm = r["fm"]
            out += [f"### {s}", f"*{fm.get('published', '')} · {fm.get('publisher', '')} · places "
                    f"{', '.join(map(str, fm.get('places') or []))} · topics {', '.join(topics(fm))}*",
                    f"**{fm.get('title', '')}** — {fm.get('url', '')}", ""]
            if fm.get("hub_line"):
                out += [str(fm["hub_line"]).strip(), ""]
            try:
                raw = open(r["path"], encoding="utf-8").read()
                body = raw.split("\n---", 1)[1] if raw.startswith("---") and "\n---" in raw else raw
            except OSError:
                body = ""
            row = {"facility_name": " ".join(x["facility_name"] for x in rows if x["country"] in named),
                   "operator_name": "", "city": "", "country_name": "", "parent_company": "",
                   "ultimate_parent_company": ""}
            text = body if len(body) <= BODY else de.excerpt(body, row)[:BODY + 2000]
            out += ["```text", text.replace("```", "'''").strip(), "```", ""]
        folder = WORK / where
        folder.mkdir(parents=True, exist_ok=True)
        p = folder / (f"packet-{k + 1}.md" if parts > 1 else "packet.md")
        p.write_text("\n".join(out), encoding="utf-8")
        print(f"{p.relative_to(dl.ROOT)}: {len(chunk)} records, {p.stat().st_size:,} bytes")


STOP = {"data", "centre", "center", "centres", "centers", "dc", "the", "de", "du", "la", "le", "and", "of",
         "limited", "ltd", "campus", "facility", "national", "tier", "iii", "iv"}


def similar(a, b):
    ta = {w for w in re.findall(r"[a-z0-9]+", a.lower()) if w not in STOP}
    tb = {w for w in re.findall(r"[a-z0-9]+", b.lower()) if w not in STOP}
    return bool(ta and tb) and len(ta & tb) / len(ta | tb) >= 0.5


def mark(name, slugs):
    have = considered(name)
    new = [s for s in dict.fromkeys(x.strip() for x in slugs) if s and s not in have]
    if new:
        with io.open(considered_path(name), "a", encoding="utf-8", newline="\n") as fh:
            fh.write("\n".join(new) + "\n")
    return len(new)


def apply(name, where, dry):
    """Check a place's decisions and apply them: edits and new rows through datasets_lib, each
    logged with the records it rests on, then every accounted slug marked considered."""
    dec = {"considered": {}, "rows": {}}
    for f in sorted((WORK / where).glob("decisions*.json")):
        part = json.loads(f.read_text(encoding="utf-8"))
        dec["considered"].update(part.get("considered", {}))
        clash = set(part.get("rows", {})) & set(dec["rows"])
        if clash:
            sys.exit(f"{f.name}: rows decided twice: {sorted(clash)}")
        dec["rows"].update(part.get("rows", {}))
    cand = candidates(name)
    todo = pending(name, where)
    problems = [f"{s}: not a candidate" for s in dec["considered"] if s not in cand]
    missing = [s for s in todo if s not in dec["considered"]]
    if missing and not dry:
        problems += [f"{s}: no outcome under considered" for s in missing]
    elif missing:
        print(f"note: {len(missing)} slug(s) not yet accounted for")
    today = datetime.date.today().isoformat()
    rows = dl.read(name)
    meta = {m["column"]: m for m in dl.metadata(name)}
    by = {r["facility_id"]: r for r in rows}
    url = {s: str(r["fm"].get("url") or "") for s, r in cand.items()}
    logs, claims, resolved, added = [], [], set(), []
    for key, d in dec["rows"].items():
        slugs = d.get("add_slugs", [])
        problems += [f"{key}: add_slugs names a non-candidate {s}" for s in slugs if s not in cand]
        if key.startswith("new:"):
            f = dict(d.get("fields", {}))
            iso = f.get("country", "")
            if not re.fullmatch(r"[A-Z]{3}", iso) or not f.get("facility_name"):
                problems.append(f"{key}: a new row needs country and facility_name")
                continue
            bad = [c for c in f if c not in meta or c in de.DERIVED_BY_SCRIPT and c != "country"]
            if bad:
                problems.append(f"{key}: cannot set {bad}")
                continue
            r = {c: "" for c in meta}
            r.update({c: str(v).strip() for c, v in f.items()})
            for other in rows:  # parallel readers cannot see each other's new rows: say so, loudly
                if other["country"] == iso and similar(other["facility_name"], r["facility_name"]):
                    print(f"POSSIBLE DUPLICATE {key} '{r['facility_name']}' ~ {other['facility_id']} "
                          f"'{other['facility_name']}'")
            r["facility_id"] = dl.next_id(rows, iso)
            names = {x["iso-3"]: x["country-name"] for x in csv.DictReader(
                open(dl.ROOT / "lookups" / "countries.csv", encoding="utf-8-sig"))}
            r["country_name"] = names.get(iso, "")
            rows.append(r)
            by[r["facility_id"]] = r
            target, action, det = r, "add", f"Added from raw/: {d.get('why', '').rstrip('.')}."
        else:
            if key not in by:
                problems.append(f"{key}: no such row")
                continue
            target, action, changes = by[key], "modify", []
            for fld, e in d.get("edits", {}).items():
                if fld not in meta or fld in de.DERIVED_BY_SCRIPT:
                    problems.append(f"{key}: cannot edit {fld}")
                    continue
                new, old = str(e["value"]).strip(), target[fld]
                if new == old:
                    continue
                target[fld] = new
                short = lambda v: (repr(v) if len(v) <= 60 else "rewritten") if v else "empty"
                desc = (f"{fld} {short(old)} → {short(new)}" if len(old) <= 60 and len(new) <= 60
                        else f"{fld} {'cleared' if not new else 'filled' if not old else 'rewritten'}")
                changes.append(f"{desc}: {e['why'].rstrip('.')}.")
            det = ("From raw/. " + " ".join(changes)).strip()
        have = [u.strip() for u in target["source_urls"].split(";") if u.strip()]
        hs = [u.strip() for u in target["raw_slugs"].split(";") if u.strip()]
        n_new = 0
        for s in slugs:
            if url.get(s) and url[s] not in have:
                have.append(url[s])
                added.append((target["facility_id"], s))
                n_new += 1
            if s not in hs:
                hs.append(s)
        if n_new and action == "modify":
            det += f" {n_new} source(s) added from the catalogue."
        target["source_urls"], target["raw_slugs"] = "; ".join(have), "; ".join(hs)
        target["hyperscaler_presence"] = "Yes" if any(target[h] == "Yes" for h in de.HYPER) else "No"
        target["cloud_act_exposure"] = de.cloud_act(target)
        target["foreign_dependency_score"] = de.foreign_dependency(target)
        target["last_verified"] = today
        for fld, why in d.get("to_source", {}).items():
            claims.append({"facility_id": target["facility_id"], "field": fld, "claim": target.get(fld, ""),
                           "reason": why, "date": today})
        resolved |= {(target["facility_id"], fld) for fld in d.get("resolves", [])}
        if action == "add" or det != "From raw/.":
            logs.append((target["facility_id"], action, det, "; ".join(url.get(s, "") for s in slugs)))
    problems += dl.check(name, rows)
    if problems:
        print("\n".join(problems))
        sys.exit(f"{len(problems)} problem(s); nothing written")
    for fid, action, det, src in logs:
        print(f"{fid} {action}: {det[:300]}")
    print(f"{len(logs)} row change(s), {sum(1 for _, a, *_ in logs if a == 'add')} new, "
          f"{len(dec['considered'])} slug(s) accounted for")
    if dry:
        return
    dl.write(name, rows)
    audit = de.read_csv(de.AUDIT)
    known = {a["url"]: a for a in audit}
    for fid, s in added:
        base = known.get(url[s], {})
        audit.append({**{k: "" for k in audit[0]}, **{k: base.get(k, "") for k in ("status", "http_code", "final_url",
                      "wayback_url", "cached")}, "facility_id": fid, "url": url[s], "checked": today,
                      "raw_slug": s, "status": base.get("status", "catalogue"), "note": "added by T7 from raw/"})
    de.write_csv(de.AUDIT, list(audit[0].keys()), audit)
    old = de.read_csv(de.CLAIMS) if de.CLAIMS.exists() else []
    keep = [c for c in old if (c["facility_id"], c["field"]) not in resolved]
    if claims or keep != old:
        de.write_csv(de.CLAIMS, de.CLAIMS_HEADER, keep + claims)
    for fid, action, det, src in reversed(logs):
        dl.log(name, fid, action, det, src, date=today)
    print(f"{mark(name, dec['considered'])} slug(s) marked considered")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slugs", nargs="+", metavar=("DATASET", "PLACE"))
    ap.add_argument("--packet", nargs=2, metavar=("DATASET", "PLACE"))
    ap.add_argument("--apply", nargs=2, metavar=("DATASET", "PLACE"))
    ap.add_argument("--seed", nargs="+", metavar=("DATASET", "SLUG"))
    ap.add_argument("--parts", type=int, default=1)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    if not os.path.isdir("raw"):
        sys.exit("run from scripts/.workroot/, where raw/ resolves")
    if a.slugs:
        for s in pending(a.slugs[0], a.slugs[1] if len(a.slugs) > 1 else None):
            print(s)
    elif a.packet:
        packet(a.packet[0], a.packet[1], a.parts)
    elif a.apply:
        apply(a.apply[0], a.apply[1], a.dry_run)
    elif a.seed:
        print(f"{mark(a.seed[0], a.seed[1:])} slug(s) marked considered")
    else:
        work_order("data-centres")


if __name__ == "__main__":
    main()
