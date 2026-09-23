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
    python scripts/dataset-scan.py --relink data-centres        # raw_slugs rebuilt from source_urls

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
                   "append": {"comments": "<sentence added to the end of the cell>"},
                   "add_slugs": ["<slug>"], "to_source": {...}, "resolves": [...],
                   "summary": "<what changed, for a reader>"},
       "new:1":   {"fields": {"facility_name": "...", "country": "KEN", ...},
                   "add_slugs": ["<slug>"], "why": "<one line: why this is a new facility>",
                   "summary": "<what was added, for a reader>"}}}

**`summary` is what the Data Centres page prints under Recent changes** *(Bill, 2026-09-21)*, so it
is written for a reader, in plain English: what happened to the facility and what the source says,
with no field names, pass names or counts of slugs — *"Construction halted: the contractor
threatened to leave the site over unpaid bills (October 2025)."* A row with `edits`, `append` or
`fields` needs one and the apply stops without it. A row that only gains a source (`add_slugs`
alone) is summarised by the script from the source's own title, publisher and date.

Parts of one place may decide the same row: their `add_slugs`, `resolves`, `to_source` and
`append` are combined, and two parts editing one field to different values stops the apply. Name
new rows `new:{part}-{n}`. The packet shows long cells cut short, so add to one with `append`
rather than rewriting it in `edits`.

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


SKIP = {"facility_id", "country", "country_name", "source_urls", "raw_slugs", "last_verified",
        "hyperscaler_presence", "cloud_act_exposure", "foreign_dependency_score"}


def row_line(r):
    """Every field a reader can edit, so an edit never lands on a value the reader did not see."""
    cut = lambda v: v if len(v) <= 400 else v[:400] + "…"
    return f"- **{r['facility_id']}** " + " | ".join(f"{k}: {cut(v)}" for k, v in r.items() if v and k not in SKIP)


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
               "Method: `scripts/dataset-scan.py` docstring. Every record starts with a line `=== RECORD {slug} ===`; "
               f"there are {len(chunk)}, and each needs an entry under `considered` in your decisions file.", "",
               "## Current rows in the countries these records name", ""]
        for r in rows:
            if r["country"] in named:
                out.append(row_line(r))
        out += ["", "## Every facility in the dataset (to catch one listed under another country)", "",
                "; ".join(f"{r['facility_id']} {r['facility_name']}" for r in rows), "", "## Records", ""]
        for s in chunk:
            r = c[s]
            fm = r["fm"]
            out += [f"=== RECORD {s} ===", f"*{fm.get('published', '')} · {fm.get('publisher', '')} · places "
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


def norm(u):
    """A URL as a citation: scheme, www and a trailing slash do not make a second source."""
    return re.sub(r"^https?://(www\.)?", "", u.strip().lower()).rstrip("/")


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
    clashes = []
    files = sorted((WORK / where).glob("decisions*.json"))
    for f in files:
        part = json.loads(f.read_text(encoding="utf-8"))
        dec["considered"].update(part.get("considered", {}))
        for key, d in part.get("rows", {}).items():
            if key.startswith("new:"):  # every part numbers from 1: keep them apart
                dec["rows"][f"new:{f.stem}:{key[4:]}"] = d
                continue
            have = dec["rows"].setdefault(key, {})
            for fld, e in d.get("edits", {}).items():  # parts of one place may both touch a row
                old = have.setdefault("edits", {}).get(fld)
                if old and str(old["value"]).strip() != str(e["value"]).strip():
                    clashes.append(f"{key}.{fld}: {f.name} says {e['value']!r}, an earlier part {old['value']!r}")
                have["edits"][fld] = e
            for k in ("add_slugs", "resolves"):
                have[k] = list(dict.fromkeys(have.get(k, []) + d.get(k, [])))
            have.setdefault("to_source", {}).update(d.get("to_source", {}))
            for fld, text in d.get("append", {}).items():
                have.setdefault("append", {})[fld] = (have.get("append", {}).get(fld, "") + " " + text).strip()
            if str(d.get("summary", "")).strip():  # two parts may each summarise their change to one row
                have["summary"] = (have.get("summary", "") + " " + d["summary"].strip()).strip()
    if clashes:
        sys.exit("parts disagree:\n" + "\n".join(clashes))
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
            if not str(d.get("summary", "")).strip():
                problems.append(f"{key}: a new row needs a summary for the page")
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
            for fld, text in d.get("append", {}).items():  # add to a cell the packet shows cut short
                if fld not in meta or fld in de.DERIVED_BY_SCRIPT:
                    problems.append(f"{key}: cannot append to {fld}")
                    continue
                target[fld] = f"{target[fld].rstrip()} {text.strip()}".strip()
                changes.append(f"{fld}: added \"{text.strip()[:80]}\".")
            det = ("From raw/. " + " ".join(changes)).strip()
            if changes and not str(d.get("summary", "")).strip():
                problems.append(f"{key}: an edit or append needs a summary for the page")
        have = [u.strip() for u in target["source_urls"].split(";") if u.strip()]
        hs = [u.strip() for u in target["raw_slugs"].split(";") if u.strip()]
        n_new = n_slug = 0
        seen = {norm(u) for u in have}
        for s in slugs:
            if url.get(s) and norm(url[s]) not in seen:
                seen.add(norm(url[s]))
                have.append(url[s])
                added.append((target["facility_id"], s))
                n_new += 1
            if s not in hs:
                hs.append(s)
                n_slug += 1
        if n_new and action == "modify":
            det += f" {n_new} source(s) added from the catalogue."
        elif n_slug and action == "modify":
            det += f" {n_slug} catalogue record(s) joined the row."
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
            summary = str(d.get("summary", "")).strip() or joined(target["facility_name"], slugs, cand)
            logs.append((target["facility_id"], action, det, "; ".join(url.get(s, "") for s in slugs),
                         summary))
    problems += dl.check(name, rows)
    if problems:
        print("\n".join(problems))
        sys.exit(f"{len(problems)} problem(s); nothing written")
    for fid, action, det, src, summary in logs:
        print(f"{fid} {action}: {det[:300]}\n    page: {summary}")
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
    for fid, action, det, src, summary in reversed(logs):
        dl.log(name, fid, action, det, src, date=today, summary=summary)
    print(f"{mark(name, dec['considered'])} slug(s) marked considered")
    # Applied files leave the folder: --apply reads every decisions*.json there, so one left behind
    # replays at the next apply and re-adds rows since merged (Teraco CT3, 2026-09-23).
    done = WORK / where / f"applied-{today}"
    done.mkdir(exist_ok=True)
    for f in files:
        f.replace(done / f.name)


def joined(facility, slugs, cand):
    """The page's sentence for a row that only gained sources: what the source is, not how many."""
    def one(s):
        fm = cand[s]["fm"] if s in cand else {}
        title = str(fm.get("title") or s).strip()
        pub, when = str(fm.get("publisher") or "").strip(), str(fm.get("published") or "").strip()
        tail = ", ".join(x for x in (pub, when) if x)
        return f"\u201c{title}\u201d" + (f" ({tail})" if tail else "")
    if not slugs:
        return f"{facility}: sources updated."
    return f"{facility}: new source{'s' if len(slugs) > 1 else ''} " + "; ".join(one(s) for s in slugs) + "."


def relink(name):
    """Rebuild every row's raw_slugs from its source_urls: each URL the catalogue holds, by the
    catalogue's own key. T5's matcher wrote a URL-derived key the catalogue does not use (282 dead
    entries, found 2026-09-21); this keeps the column true whatever wrote it."""
    by_url = collections.defaultdict(list)
    valid = set()
    for r in vault_lib.load_index(quiet=True):
        d, fm = r.get("d") or {}, r.get("fm") or {}
        if d.get("kind") == "source" and d.get("folder") == "raw":
            s = d.get("slug") or os.path.basename(r["path"])[:-3]
            valid.add(s)
            if fm.get("url"):
                by_url[norm(str(fm["url"]))].append(s)
    rows = dl.read(name)
    dead = changed = 0
    for r in rows:
        old = [s.strip() for s in r["raw_slugs"].split(";") if s.strip()]
        dead += sum(s not in valid for s in old)
        keep = [s for s in old if s in valid]
        for u in r["source_urls"].split(";"):
            keep += by_url.get(norm(u), []) if u.strip() else []
        new = "; ".join(dict.fromkeys(keep))
        if new != r["raw_slugs"]:
            r["raw_slugs"] = new
            changed += 1
    dl.write(name, rows)
    if changed:
        dl.log(name, "ALL", "modify", f"raw_slugs rebuilt from source_urls on {changed} rows: {dead} entries were keys "
               "the catalogue does not use, and every cited URL the catalogue holds is now linked. No fact changed.")
    print(f"{changed} rows relinked, {dead} dead entries dropped")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slugs", nargs="+", metavar=("DATASET", "PLACE"))
    ap.add_argument("--packet", nargs=2, metavar=("DATASET", "PLACE"))
    ap.add_argument("--apply", nargs=2, metavar=("DATASET", "PLACE"))
    ap.add_argument("--seed", nargs="+", metavar=("DATASET", "SLUG"))
    ap.add_argument("--relink", metavar="DATASET")
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
    elif a.relink:
        relink(a.relink)
    elif a.seed:
        print(f"{mark(a.seed[0], a.seed[1:])} slug(s) marked considered")
    else:
        work_order("data-centres")


if __name__ == "__main__":
    main()
