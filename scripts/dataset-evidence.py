#!/usr/bin/env python3
"""dataset-evidence.py — T6: check each Data Centres row against the sources it cites.

    python scripts/dataset-evidence.py packet SYC     # write prep/dc-evidence/SYC/packet.md
    python scripts/dataset-evidence.py packet ZAF --parts 6   # packet-1.md ... packet-6.md
    python scripts/dataset-evidence.py apply SYC      # apply prep/dc-evidence/SYC/decisions.json
    python scripts/dataset-evidence.py apply SYC --dry-run
    python scripts/dataset-evidence.py status         # rows verified, by country
    python scripts/dataset-evidence.py refetch        # read what T4 could not, through Exa
    python scripts/dataset-evidence.py group-packet raxio AGO-012 CIV-003 ...   # T6b
    python scripts/dataset-evidence.py apply-group raxio [--dry-run]
    python scripts/dataset-evidence.py apply-t8 WEST [--dry-run]              # T8: + "new:*" rows, "retire"
    python scripts/dataset-evidence.py derive         # set the rule-derived fields on every row

A model reads the packet, one country per sitting, and writes `decisions.json`; this script
checks that file and applies it. Nothing here judges a claim.

**The packet** holds each row's filled fields, the fields left empty, and the text of every source
the row cites, from T4's cache (`prep/dc-url-cache/`). A long source is cut to its opening and to
the passages around the row's own names and the usual data-centre terms, so a 300-page annual
report arrives as the pages that mention the facility.

**decisions.json** has one entry per row in the country, and every row must be present:

    {"SYC-001": {
       "supports": {"<url>": ["operational_status", "year_operational"], "<url>": []},
       "edits":    {"<field>": {"value": "<new value>", "why": "<one clause>"}},
       "to_source": {"<field>": "<why it is kept though nothing readable supports it>"},
       "sources":  ["<url an edit rests on>"]}}

`supports` covers every URL the row cites. A list of fields is what the page supports; `[]` means
it was read and supports none of them; `"unreadable"` means no text could be had.

**The rules the reader applies**, written here because they are the method, not the tool:

1. **A source supports a field** when it states the value, or states something the value follows
   from directly. A group-level fact (Airtel Africa's DFI loans) supports a row only as far as the
   row claims it at group level.
2. **Fill empty fields** where a readable source gives the value: years, parents, HQ countries.
3. **A claim a source contradicts is corrected**, from the newest source; the old value goes in
   the log, not in comments.
4. **A claim that overstates its source is softened**: an aspiration is not a relationship, a
   supplier is not an owner, a group partnership in another country is not this facility's.
5. **A claim nothing supports and nothing makes plausible is cleared**, or set to Unknown where the
   field has that value.
6. **A plausible, specific claim that no readable source supports is kept and listed in
   `to_source`** for T9 to source. A dead URL never deletes a fact (§2), and T9 has the search.
7. **Derived fields follow their rule.** `hyperscaler_*` is Yes only where
   `hyperscaler_relationships` names a confirmed relationship at this facility, and the script sets
   `hyperscaler_presence`, `cloud_act_exposure`, `foreign_dependency_score` and `country_name` itself. `control_category` follows
   `ultimate_parent_hq_country`; where the reader departs from it (Liquid: UK-registered, African
   controlled), `control_rationale` must say why. `control_confidence`: high with two independent
   readable sources for the ownership chain, low with one or with sources that conflict.
8. **No restyling.** Cells keep their form; T6 changes what a row says, not how.

**Applying** writes the master through `datasets_lib`, one `modify` log row per changed facility
and one per country for the rows confirmed unchanged, fills `supports` in `url-audit.csv`, appends
`to_source` claims to `claims-to-source.csv`, and sets `last_verified` on every row read.
"""
from __future__ import annotations
import argparse, collections, csv, datetime, io, json, pathlib, re, sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import datasets_lib as dl  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")

NAME = "data-centres"
DIR = dl.DATASETS / NAME
AUDIT = DIR / "url-audit.csv"
CLAIMS = DIR / "claims-to-source.csv"
CLAIMS_HEADER = ["facility_id", "field", "claim", "reason", "date"]
CACHE = dl.ROOT / "prep" / "dc-url-cache"
WORK = dl.ROOT / "prep" / "dc-evidence"
DERIVED_BY_SCRIPT = {"hyperscaler_presence", "cloud_act_exposure", "foreign_dependency_score", "country_name", "last_verified", "raw_slugs",
                     "facility_id", "country"}
HYPER = ["hyperscaler_microsoft", "hyperscaler_aws", "hyperscaler_google"]
FULL = 9000        # a source shorter than this goes in whole
HEAD = 2500        # otherwise its opening ...
WINDOW = 700       # ... and this much either side of each hit ...
CAP = 14000        # ... up to this much in all
TERMS = [r"data ?cent(?:re|er)", r"\bMW\b", r"megawatt", r"\bracks?\b", r"\btier ?(?:I{1,4}|[1-4])\b",
         r"square met", r"\bsqm\b", r"\bm²", r"colocation", r"shareholder", r"subsidiar", r"stake"]
GENERIC = {"data", "centre", "center", "centres", "centers", "limited", "ltd", "group", "the", "and",
           "africa", "african", "company", "holdings", "plc", "national", "facility", "cloud", "tier"}


def read_csv(p):
    with open(p, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(p, header, rows):
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=header, lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
    p.write_text(buf.getvalue(), encoding="utf-8", newline="")


def african():
    with open(dl.ROOT / "lookups" / "countries.csv", encoding="utf-8-sig", newline="") as f:
        return {r["iso-3"] for r in csv.DictReader(f) if r["Region"].startswith("X") and r["Region"] != "XGL"}


def rule_category(hq, af):
    cs = [c.strip() for c in hq.split("|") if c.strip()]
    if not cs:
        return ""
    inside = [c in af for c in cs]
    if all(inside):
        return "African control"
    if any(inside):
        return "Joint African/foreign control"
    return "US control" if cs == ["USA"] else "Other foreign control"


def cloud_act(row):
    """metadata.csv -> cloud_act_exposure: set by rule from two columns, never judged."""
    hq = {c.strip() for c in row["ultimate_parent_hq_country"].split("|") if c.strip()}
    if not hq:
        return "Unknown"
    if "USA" in hq or row["control_category"] == "US control":  # Africell: Jersey-registered, US-controlled
        return "Yes (US-parented operator)"
    if any(row[h] == "Yes" for h in HYPER):
        return "Partial (US hyperscaler service on site)"
    return "No (no US parent or hyperscaler service)"


FOREIGN_OWN = {"Private foreign", "Joint venture (majority foreign)"}
DOMESTIC_OWN = {"Private domestic", "Government / SOE", "Joint venture (majority domestic)", "PPP"}


def foreign_dependency(row):
    """metadata.csv -> foreign_dependency_score: set by rule. Foreign means foreign equity or a
    non-African controller; Low needs domestic ownership, no US reach and a stack not known to be
    proprietary (an open stack is rarely documented, so requiring one would leave Low empty)."""
    own, ctl = row["ownership_type"], row["control_category"]
    if own in ("", "Unknown") and not ctl:
        return "Insufficient data"
    foreign = own in FOREIGN_OWN or ctl in ("US control", "Other foreign control")
    domestic = not foreign and (own in DOMESTIC_OWN or ctl == "African control")
    cloud = row["cloud_act_exposure"].split(" (")[0]
    proprietary = row["open_source_stack"] == "Predominantly proprietary"
    if foreign and (cloud == "Yes" or proprietary):
        return "High"
    if domestic and cloud == "No" and not proprietary:
        return "Low"
    return "Moderate"


def derive_all():
    """Set cloud_act_exposure from its rule on every row: the one-off pass when the rule replaced
    v2's judgements (2026-09-21). `apply` keeps it true row by row after that."""
    rows = dl.read(NAME)
    changed = 0
    fds = 0
    for r in rows:
        new = cloud_act(r)
        old = r["cloud_act_exposure"]
        if new.split(" (")[0] != old.split(" (")[0]:
            changed += 1
        r["cloud_act_exposure"] = new
        fd = foreign_dependency(r)
        fds += fd != r["foreign_dependency_score"]
        r["foreign_dependency_score"] = fd
    bad = dl.check(NAME, rows)
    if bad:
        sys.exit("\n".join(bad))
    dl.write(NAME, rows)
    if changed:
        dl.log(NAME, "ALL", "modify", f"cloud_act_exposure set by its rule: {changed} of {len(rows)} rows changed.")
    if fds:
        dl.log(NAME, "ALL", "modify", f"foreign_dependency_score set by its rule from ownership, control, CLOUD Act "
               f"exposure and software stack: {fds} of {len(rows)} rows changed.")
    print(f"cloud_act {changed}, foreign_dependency {fds} of {len(rows)} changed")


def names(row):
    words = set()
    for c in ("facility_name", "operator_name", "city", "country_name", "parent_company", "ultimate_parent_company"):
        for w in re.findall(r"[A-Za-zÀ-ÿ0-9][\w&'-]{2,}", row.get(c, "")):
            if w.lower() not in GENERIC:
                words.add(w)
    return words


def excerpt(text, row):
    if len(text) <= FULL:
        return text
    pats = [re.compile(re.escape(w), re.I) for w in names(row)] + [re.compile(t, re.I) for t in TERMS]
    spans = []
    for p in pats:
        for m in p.finditer(text, HEAD):
            spans.append((max(HEAD, m.start() - WINDOW), min(len(text), m.end() + WINDOW)))
    spans.sort()
    merged = []
    for s, e in spans:
        if merged and s <= merged[-1][1]:
            if e - merged[-1][0] <= 3 * WINDOW:
                merged[-1][1] = max(merged[-1][1], e)
                continue
            s = merged[-1][1]  # too long to merge: start where the last passage ended
            if s >= e:
                continue
        merged.append([s, e])
    # Passages naming the row come first: they are what the check needs.
    own = [re.compile(re.escape(w), re.I) for w in names(row)]
    merged.sort(key=lambda se: -sum(bool(p.search(text, se[0], se[1])) for p in own))
    out, used = [text[:HEAD]], HEAD
    for s, e in merged:
        if used + (e - s) > CAP:
            continue
        out.append(f"[… {s:,}]\n{text[s:e]}")
        used += e - s
    return "\n\n".join(out) + f"\n\n[excerpted: {used:,} of {len(text):,} characters]"


def packet(iso, parts=1):
    """With parts > 1, a large country is cut into packet-1.md ... packet-N.md, rows in ID order, so
    several readers can take it; each writes decisions-K.json, and apply reads them all."""
    everyone = [r for r in dl.read(NAME) if r["country"] == iso]
    if parts > 1:
        size = -(-len(everyone) // parts)
        for k in range(parts):
            _packet(iso, everyone[k * size:(k + 1) * size], f"packet-{k + 1}.md")
        return
    _packet(iso, everyone, "packet.md")


def _packet(iso, rows, name):
    if not rows:
        sys.exit(f"no rows for {iso}")
    audit = collections.defaultdict(list)
    for a in read_csv(AUDIT):
        audit[a["facility_id"]].append(a)
    cols = dl.columns(NAME)
    out = [f"# T6 evidence packet — {iso}, {len(rows)} row(s)\n",
           "Method: `scripts/dataset-evidence.py` docstring. Write `decisions.json` beside this file.\n"]
    for r in rows:
        fid = r["facility_id"]
        out.append(f"\n\n======== {fid} — {r['facility_name']} ========\n")
        out.append("## Row\n")
        for c in cols:
            if r[c] and c not in ("source_urls", "raw_slugs"):
                out.append(f"- **{c}**: {r[c]}")
        out.append("\n**Empty**: " + ", ".join(c for c in cols if not r[c]))
        out.append("\n## Sources\n")
        for a in sorted(audit[fid], key=lambda a: a["url"]):
            status = a["status"] + (f", read from {a['wayback_url']}" if a["wayback_url"] not in ("", "none") and a["cached"] else "")
            out.append(f"\n### {a['url']}\n*{status}*{' — ' + a['note'] if a['note'] else ''}\n")
            if a["cached"] and (CACHE / a["cached"]).exists() and not unreadable(a):
                text = (CACHE / a["cached"]).read_text(encoding="utf-8", errors="replace")
                out.append("```text\n" + excerpt(text, r).replace("```", "'''") + "\n```")
            else:
                out.append("*(no text: unreadable)*")
    p = WORK / iso / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("\n".join(out), encoding="utf-8")
    print(f"{p.relative_to(dl.ROOT)}: {len(rows)} rows, {p.stat().st_size:,} bytes")


def group_packet(name, ids):
    """T6b: every row in an operator group, across countries, with each source once."""
    by_id = {r["facility_id"]: r for r in dl.read(NAME)}
    rows = [by_id[i] for i in ids]
    audit = collections.defaultdict(list)
    for a in read_csv(AUDIT):
        audit[a["url"]].append(a)
    cols = dl.columns(NAME)
    want = {r["facility_id"] for r in rows}
    claims = collections.defaultdict(list)
    for c in (read_csv(CLAIMS) if CLAIMS.exists() else []):
        claims[c["facility_id"]].append(c)
    cited = {u: sorted({a["facility_id"] for a in aa} & want) for u, aa in audit.items()}
    cited = {u: c for u, c in cited.items() if c}
    merged = {c: " ".join(r[c] for r in rows) for c in ("facility_name", "operator_name", "city", "country_name",
                                                         "parent_company", "ultimate_parent_company")}
    nl = chr(10)
    fence = "`" * 3
    out = [f"# T6b group packet - {name}, {len(rows)} row(s)", "",
           "Method: `scripts/dataset-evidence.py` docstring and `prep/dc-evidence/GROUP-BRIEF.md`.", ""]
    for r in rows:
        out += ["", f"======== {r['facility_id']} - {r['facility_name']} ({r['country_name']}) ========"]
        for c in cols:
            if r[c] and c not in ("source_urls", "raw_slugs"):
                out.append(f"- **{c}**: {r[c]}")
        for c in claims.get(r["facility_id"], []):
            out.append(f"- *to source* **{c['field']}**: {c['reason']}")
    out += ["", "", "# Sources (each once; cited by the rows named)", ""]
    for u in sorted(cited, key=lambda u: (-len(cited[u]), u)):
        a = audit[u][0]
        out += ["", f"### {u}", f"*{a['status']}* - cited by {' '.join(cited[u])}", ""]
        if a["cached"] and (CACHE / a["cached"]).exists() and not unreadable(a):
            text = (CACHE / a["cached"]).read_text(encoding="utf-8", errors="replace")
            out += [fence + "text", excerpt(text, merged).replace(fence, "'" * 3), fence]
        else:
            out.append("*(no text: unreadable)*")
    p = WORK / "groups" / name / "packet.md"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(nl.join(out), encoding="utf-8")
    print(f"{p.relative_to(dl.ROOT)}: {len(rows)} rows, {len(cited)} sources, {p.stat().st_size:,} bytes")


def t8_packet(name, isos):
    """T8: a region's rows in full, their open facility-level flags, and the other countries' names,
    for a reader who will search the web for what the dataset lacks."""
    rows = dl.read(NAME)
    flags = collections.defaultdict(list)
    for c in (read_csv(CLAIMS) if CLAIMS.exists() else []):
        if c["field"] in ("facility_name", "operational_status", "ultimate_parent_company"):
            flags[c["facility_id"]].append(c)
    skip = {"source_urls", "raw_slugs", "last_verified", "hyperscaler_presence", "cloud_act_exposure",
            "foreign_dependency_score", "country_name"}
    cut = lambda v: v if len(v) <= 500 else v[:500] + "…"
    out = [f"# T8 packet — {name}: {' '.join(isos)}", "",
           "Brief: `prep/dc-evidence/T8-BRIEF.md`. Leads: `prep/dc-evidence/T8-LEADS.md`.", ""]
    for iso in isos:
        mine = [r for r in rows if r["country"] == iso]
        out += ["", f"## {iso} — {len(mine)} row(s)", ""]
        for r in mine:
            out.append(f"### {r['facility_id']} — {r['facility_name']}")
            out.append(" | ".join(f"{k}: {cut(v)}" for k, v in r.items() if v and k not in skip))
            out.append(f"sources: {r['source_urls']}")
            for c in flags.get(r["facility_id"], []):
                out.append(f"- FLAG {c['field']}: {c['reason']}")
            out.append("")
    out += ["", "## Every facility in the dataset", "",
            "; ".join(f"{r['facility_id']} {r['facility_name']}" for r in rows)]
    p = WORK / "t8" / name / "packet.md"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("\n".join(out), encoding="utf-8")
    print(f"{p.relative_to(dl.ROOT)}: {sum(r['country'] in isos for r in rows)} rows, {p.stat().st_size:,} bytes")


def load_decisions(folder):
    dec = {}
    for f in sorted(folder.glob("decisions*.json")):
        part = json.loads(f.read_text(encoding="utf-8"))
        clash = set(part) & set(dec)
        if clash:
            sys.exit(f"{f.name}: rows decided twice: {sorted(clash)}")
        dec.update(part)
    return dec


def apply(iso, dry):
    dec = load_decisions(WORK / iso)
    rows = dl.read(NAME)
    mine = {r["facility_id"]: r for r in rows if r["country"] == iso}
    problems = [f"{fid}: not in {iso}" for fid in dec if fid not in mine]
    missing = [fid for fid in mine if fid not in dec]
    if dry and missing:  # another part's reader may still be writing them
        print(f"note: no decision yet for {len(missing)} row(s): {' '.join(missing)}")
    elif missing:
        problems += [f"{fid}: no decision" for fid in missing]
    _apply(dec, rows, mine, iso, dry, problems, group=None)


def apply_group(name, dry, base="groups"):
    """T6b: one reader settles an operator group's facts across countries. A group's decisions
    need not cover every URL a row cites (T6 did that); they may add sources, and they add to a
    row's unsourced claims or resolve them rather than replacing the row's list."""
    dec = load_decisions(WORK / base / name)
    rows = dl.read(NAME)
    meta = {m["column"]: m for m in dl.metadata(NAME)}
    today = datetime.date.today().isoformat()
    problems, adds, retires = [], [], []
    # T8: new facilities found on the web. Their sources are checked and cached by
    # `dataset-urls.py --check`, which reads source_urls from the master, then staged through T5.
    for key in [k for k in dec if k.startswith("new:")]:
        d = dec.pop(key)
        f = {c: str(v).strip() for c, v in d.get("fields", {}).items()}
        iso = f.get("country", "")
        bad = [c for c in f if c not in meta or (c in DERIVED_BY_SCRIPT and c != "country")]
        if not re.fullmatch(r"[A-Z]{3}", iso) or not f.get("facility_name") or bad or not d.get("source_urls"):
            problems.append(f"{key}: a new row needs country, facility_name and source_urls, and only editable fields {bad}")
            continue
        r = {c: "" for c in meta}
        r.update(f)
        r["facility_id"] = dl.next_id(rows, iso)
        r["source_urls"] = "; ".join(dict.fromkeys(u.strip() for u in d["source_urls"] if u.strip()))
        with open(dl.ROOT / "lookups" / "countries.csv", encoding="utf-8-sig", newline="") as fh:
            r["country_name"] = {x["iso-3"]: x["country-name"] for x in csv.DictReader(fh)}.get(iso, "")
        rows.append(r)
        adds.append((r["facility_id"], d.get("why", ""), r["source_urls"]))
        dec[r["facility_id"]] = {k: v for k, v in d.items() if k in ("to_source", "sources")}
    # T8: a duplicate folds its sources into the row it repeats; a facility nothing shows exists goes.
    for fid in list(dec):
        rt = dec[fid].get("retire")
        if rt:
            into = rt.get("into", "")
            if into and into not in {x["facility_id"] for x in rows}:
                problems.append(f"{fid}: retire into unknown row {into}")
            retires.append((fid, into, rt.get("reason", "").strip()))
    by_id = {r["facility_id"]: r for r in rows}
    problems += [f"{fid}: no such row" for fid in dec if fid not in by_id]
    mine = {fid: by_id[fid] for fid in dec if fid in by_id}
    for fid, why, src in adds:
        print(f"{fid} add: {why}")
    for fid, into, why in retires:
        print(f"{fid} retire{' into ' + into if into else ''}: {why}")
    _apply(dec, rows, mine, name, dry, problems, group=name)
    if dry:
        return
    for fid, why, src in adds:
        dl.log(NAME, fid, "add", f"Added from a coverage search: {why.rstrip('.')}.", src, date=today)
    if retires:
        rows = dl.read(NAME)
        by_id = {r["facility_id"]: r for r in rows}
        for fid, into, why in retires:
            if into:  # its sources are the other row's evidence now
                t, g = by_id[into], by_id[fid]
                for col in ("source_urls", "raw_slugs"):
                    have = [u.strip() for u in t[col].split(";") if u.strip()]
                    t[col] = "; ".join(dict.fromkeys(have + [u.strip() for u in g[col].split(";") if u.strip()]))
            rows = dl.retire(NAME, rows, fid, (f"duplicate of {into}: " if into else "") + why, date=today)
            by_id = {r["facility_id"]: r for r in rows}
        dl.write(NAME, rows)
        for fid, into, why in retires:
            dl.log(NAME, fid, "retire", (f"Retired as a duplicate of {into}: " if into else "Retired: ") + why.rstrip(".") + ".",
                   date=today)


def _apply(dec, rows, mine, scope, dry, problems, group):
    today = datetime.date.today().isoformat()
    meta = {m["column"]: m for m in dl.metadata(NAME)}
    af = african()
    audit = read_csv(AUDIT)
    cited = collections.defaultdict(set)
    for a in audit:
        cited[a["facility_id"]].add(a["url"])
    log_rows, claims, unchanged = [], [], []
    for fid, d in dec.items():
        if fid not in mine:
            continue
        r = mine[fid]
        sup = d.get("supports", {})
        added = [u.strip() for u in d.get("add_sources", []) if u.strip()]
        for u in added:
            if u in cited[fid]:
                problems.append(f"{fid}: add_sources names a URL the row already cites: {u}")
        if group is None:
            for u in cited[fid] - set(sup):
                problems.append(f"{fid}: no supports entry for {u}")
        cited[fid] |= set(added)
        for u, fs in sup.items():
            if u not in cited[fid]:  # cited[fid] already includes add_sources
                problems.append(f"{fid}: supports names an uncited URL {u}")
            elif fs != "unreadable":
                problems += [f"{fid}: {u} supports unknown field {f}" for f in fs if f not in meta]
        changes = []
        for f, e in d.get("edits", {}).items():
            if f not in meta or f in DERIVED_BY_SCRIPT:
                problems.append(f"{fid}: cannot edit {f}")
                continue
            new = str(e["value"]).strip()
            if new == r[f]:
                continue
            old = r[f]
            r[f] = new
            short = lambda v: (repr(v) if len(v) <= 60 else "rewritten") if v else "empty"
            desc = (f"{f} {short(old)} → {short(new)}" if len(old) <= 60 and len(new) <= 60
                    else f"{f} {'cleared' if not new else 'filled' if not old else 'rewritten'}")
            changes.append(f"{desc}: {e['why'].rstrip('.')}.")
        for f, text in d.get("append", {}).items():  # T8: add to a long cell without rewriting it
            if f not in meta or f in DERIVED_BY_SCRIPT:
                problems.append(f"{fid}: cannot append to {f}")
                continue
            r[f] = f"{r[f].rstrip()} {text.strip()}".strip()
            changes.append(f"{f}: added \"{text.strip()[:80]}\".")
        r["hyperscaler_presence"] = "Yes" if any(r[h] == "Yes" for h in HYPER) else "No"
        r["cloud_act_exposure"] = cloud_act(r)
        r["foreign_dependency_score"] = foreign_dependency(r)
        rule = rule_category(r["ultimate_parent_hq_country"], af)
        if rule and r["control_category"] != rule and "control_rationale" not in d.get("edits", {}) \
                and "control_category" in d.get("edits", {}):
            problems.append(f"{fid}: control_category departs from the registration rule ({rule}) "
                            "without a new control_rationale")
        if added:
            have = [u.strip() for u in r["source_urls"].split(";") if u.strip()]
            r["source_urls"] = "; ".join(have + [u for u in added if u not in have])
            changes.append(f"source_urls: {len(added)} source(s) added.")
            known = {a["url"]: a for a in audit}
            for u in added:  # a URL another row cites keeps its T4 check and cached text
                base = known.get(u, {"status": "added", "checked": today})
                audit.append({**{k: "" for k in audit[0]}, **{k: base.get(k, "") for k in
                              ("status", "http_code", "final_url", "wayback_url", "cached", "checked", "raw_slug")},
                              "facility_id": fid, "url": u,
                              "supports": "; ".join(sup.get(u, [])) if isinstance(sup.get(u), list) else "",
                              "note": f"added by {'group check ' + group if group else 'T6'}"})
        problems += [f"{fid}: resolves names unknown field {f}" for f in d.get("resolves", []) if f not in meta]
        for f, why in d.get("to_source", {}).items():
            if f not in meta:
                problems.append(f"{fid}: to_source names unknown field {f}")
            else:
                claims.append({"facility_id": fid, "field": f, "claim": r[f], "reason": why, "date": today})
        r["last_verified"] = today
        for a in audit:
            if a["facility_id"] == fid and a["url"] in sup:
                v = sup[a["url"]]
                a["supports"] = v if v == "unreadable" else ("; ".join(v) if v else "none")
        if changes:
            log_rows.append((fid, " ".join(changes), "; ".join(d.get("sources", []))))
        else:
            unchanged.append(fid)
    bad = dl.check(NAME, rows)
    problems += [b for b in bad if b.split(":")[0] in mine]
    if problems:
        print("\n".join(problems))
        sys.exit(f"{len(problems)} problem(s); nothing written")
    for fid, details, src in log_rows:
        print(f"{fid}: {details}")
    print(f"{len(log_rows)} changed, {len(unchanged)} confirmed unchanged, {len(claims)} claim(s) to source")
    if dry:
        return
    dl.write(NAME, rows)
    write_csv(AUDIT, list(audit[0].keys()), audit)
    old = read_csv(CLAIMS) if CLAIMS.exists() else []
    if group is None:
        keep = [c for c in old if c["facility_id"] not in mine]
    else:  # a group check resolves claims by field and adds its own; the rest of a row's list stays
        gone = {(fid, f) for fid, d in dec.items() for f in d.get("resolves", [])}
        keep = [c for c in old if (c["facility_id"], c["field"]) not in gone]
    if claims or keep != old:
        write_csv(CLAIMS, CLAIMS_HEADER, keep + claims)
    if unchanged and group is None:
        dl.log(NAME, scope, "modify", f"Evidence check: {len(unchanged)} row(s) confirmed against their "
               f"sources with no change ({', '.join(unchanged)}).", date=today)
    label = f"Group check ({group}). " if group else "Evidence check. "
    for fid, details, src in reversed(log_rows):
        dl.log(NAME, fid, "modify", label + details, src, date=today)


WALLS = re.compile(r"^title: (Page View Limit Reached|Just a moment|Access denied|Attention Required)", re.I | re.M)


def unreadable(a):
    """No text, or text that is a wall: datacentermap's view limit caches as a 200 with 700 bytes."""
    if not a["cached"] or not (CACHE / a["cached"]).exists():
        return a["status"] in ("blocked", "thin", "error", "dead", "soft404")
    return bool(WALLS.search((CACHE / a["cached"]).read_text(encoding="utf-8", errors="replace")[:600]))


def refetch():
    """Ask Exa's contents endpoint for every URL T4 could not read. Exa reads from its own crawl,
    so a bot wall or a view limit that stopped T4 usually does not stop it. Cached like T4's text."""
    import hashlib, os, requests
    key = os.environ.get("EXA_API_KEY") or sys.exit("EXA_API_KEY is not set")
    audit = read_csv(AUDIT)
    todo = sorted({a["url"] for a in audit if unreadable(a) and "via Exa" not in a["note"]})
    print(f"{len(todo)} unreadable URL(s)")
    got = {}
    for i in range(0, len(todo), 25):
        batch = todo[i:i + 25]
        r = requests.post("https://api.exa.ai/contents", headers={"x-api-key": key},
                          json={"urls": batch, "text": True, "livecrawl": "fallback"}, timeout=180)
        r.raise_for_status()
        for res in r.json().get("results", []):
            text = (res.get("text") or "").strip()
            if len(text) >= 300 and not WALLS.search("title: " + (res.get("title") or "")):
                got[res.get("id") or res["url"]] = (res.get("title") or "", text)
        print(f"  {min(i + 25, len(todo))}/{len(todo)}: {len(got)} read")
    for a in audit:
        hit = got.get(a["url"])
        if hit and "via Exa" not in a["note"]:
            name = hashlib.sha1(a["url"].encode("utf-8")).hexdigest() + ".txt"
            (CACHE / name).write_text(f"url: {a['url']}\nsource: exa\ntitle: {hit[0]}\n\n{hit[1]}",
                                      encoding="utf-8")
            a["cached"] = name
            a["note"] = "; ".join(x for x in (a["note"], "text via Exa") if x)
    write_csv(AUDIT, list(audit[0].keys()), audit)
    print(f"{len(got)} of {len(todo)} now readable")


def status():
    rows = dl.read(NAME)
    by = collections.defaultdict(lambda: [0, 0])
    for r in rows:
        by[r["country"]][0] += 1
        by[r["country"]][1] += bool(r["last_verified"])
    order = sorted(by, key=lambda c: (by[c][0], c))
    done = [c for c in order if by[c][1] == by[c][0]]
    todo = [c for c in order if by[c][1] < by[c][0]]
    print(f"done {len(done)} countries, {sum(by[c][0] for c in done)} rows: {' '.join(done)}")
    print(f"to do {len(todo)} countries, {sum(by[c][0] for c in todo)} rows, smallest first: "
          + " ".join(f"{c}({by[c][0]})" for c in todo))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["packet", "apply", "status", "refetch", "derive", "group-packet", "apply-group", "apply-t8", "t8-packet"])
    ap.add_argument("iso", nargs="?", help="ISO3, or a group name for group-packet / apply-group")
    ap.add_argument("ids", nargs="*", help="group-packet: the group's facility IDs")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--parts", type=int, default=1, help="packet: cut a large country into N packets")
    a = ap.parse_args()
    if a.cmd == "status":
        status()
    elif a.cmd == "refetch":
        refetch()
    elif a.cmd == "derive":
        derive_all()
    elif a.cmd == "group-packet":
        group_packet(a.iso, a.ids)
    elif a.cmd == "apply-group":
        apply_group(a.iso, a.dry_run)
    elif a.cmd == "t8-packet":
        t8_packet(a.iso, a.ids)
    elif a.cmd == "apply-t8":  # prep/dc-evidence/t8/{REGION}/decisions*.json, same format plus new rows and retire
        apply_group(a.iso, a.dry_run, base="t8")
    elif not a.iso:
        ap.error("give an ISO3")
    elif a.cmd == "packet":
        packet(a.iso.upper(), a.parts)
    else:
        apply(a.iso.upper(), a.dry_run)
