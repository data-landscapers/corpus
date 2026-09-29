#!/usr/bin/env python3
r"""hyperscaler-report.py — one country's hyperscaler fact sheet, from its scan alone.

Implements `R&D/Hyperscaler-dependence/HYPERSCALER-DRAIN.md` step 04:

    python scripts/hyperscaler-report.py ISO3 [--date YYYY-MM-DD]

Reads `scan/{ISO3}/nodes.csv`, `organisations.csv` and `run.json`, the input file, `progress.csv`
and every other country's `run.json` for comparisons; writes `scan/{ISO3}/report.md` and
`report-chart.png`, and adds any dangling cloud names to `run.json` → `findings`. No network.

Judgements taken here, which the runbook leaves open:

- Every figure in the text is computed; nothing is typed by hand. The prose is templated so that
  54 fact sheets read alike and a continental report can cite any of them the same way.
- Comparisons use only countries whose step 03 cell is a date (the drain's rule), and say how many.
- "Institution by institution" follows the row order of the input file, which is the type order of
  `strategic-institutions.csv`; a type with no domain is listed under the table, not in it.
- A dangling name is a CNAME that returns NXDOMAIN and ends at a cloud or platform suffix where
  anyone can register the name. It is recorded in `run.json` and counted in the report, never named.
- Owners are shown by their plain name: the AS handle before " - " or the leading capitals is dropped.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import io
import json
import re
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RD = ROOT / "R&D" / "Hyperscaler-dependence"
SCAN = RD / "scan"
ROUTABLE = {"A", "AAAA", "MX", "NS"}
US = {"us-hyperscaler-africa", "us-hyperscaler-offshore"}
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

# chart rows: category, label, colour group
CHART = [
    ("cdn-origin-unknown", "Hidden behind a shield (Cloudflare and others)", "hidden"),
    ("us-hyperscaler-offshore", "US cloud, in data centres outside Africa", "us"),
    ("us-hyperscaler-africa", "US cloud, in Africa", "us"),
    ("us-saas", "US online services (Microsoft 365 and others)", "us"),
    ("telco-isp", "Telecoms companies", "home"),
    ("self-hosted", "The institution's own systems", "home"),
    ("national-dc", "Government data centres", "home"),
    ("african-colo", "African data centres and IT firms", "home"),
    ("commercial-host", "Other foreign hosting firms", "hidden"),
    ("chinese-cloud", "Chinese cloud", "hidden"),
    ("unattributed", "Not identified", "hidden"),
    ("unresolved", "Private or unusable addresses", "hidden"),
]
COLOURS = {"us": "#2a7bd6", "home": "#e8693a", "hidden": "#c4c3b6"}
LEGEND = {"us": "US company", "home": "National or African", "hidden": "Hidden, foreign or unknown"}

TAKEOVER = ("cloudapp.azure.com", "cloudapp.net", "azurewebsites.net", "trafficmanager.net",
            "blob.core.windows.net", "azureedge.net", "azurefd.net", "azure-api.net", "azurecontainer.io",
            "azurestaticapps.net", "s3.amazonaws.com", "elasticbeanstalk.com", "herokuapp.com",
            "herokudns.com", "github.io", "netlify.app", "pantheonsite.io", "ghost.io", "surge.sh",
            "bitbucket.io", "webflow.io", "fly.dev", "vercel.app", "unbouncepages.com", "readme.io",
            "helpscoutdocs.com", "freshdesk.com", "zendesk.com", "wordpress.com", "myshopify.com")

EUROPE = {"northeurope", "westeurope", "uksouth", "ukwest", "swedencentral", "centralfrance", "francecentral",
          "germanywc", "germanywestcentral", "denmarkeast", "italynorth", "spaincentral", "norwayeast",
          "switzerlandnorth", "polandcentral"}


def read_csv(p: Path) -> list[dict]:
    with open(p, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def pct(k: float, n: float) -> str:
    if not n:
        return "—"
    v = 100 * k / n
    if 0 < v < 1:
        return "<1%"
    return f"{int(v + 0.5)}%"


def num(n: int) -> str:
    return f"{n:,}"


def ordinal(n: int) -> str:
    return f"{n}{'th' if 10 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"


def listing(xs: list[str]) -> str:
    xs = list(xs)
    if len(xs) <= 1:
        return "".join(xs)
    return ", ".join(xs[:-1]) + " and " + xs[-1]


def clean_owner(s: str) -> str:
    s = (s or "").strip()
    if " - " in s:
        a, b = [x.strip() for x in s.split(" - ", 1)]
        s = b if b and not b.startswith("IDDQD") else a
    parts = s.split(" ", 1)
    if len(parts) == 2 and re.fullmatch(r"[A-Z0-9_\-]{3,}", parts[0]) and parts[1][:1].isupper() \
            and not parts[1].isupper():
        s = parts[1]
    return s


def short(s: str) -> str:
    return re.sub(r"\s*\([^)]*\)\s*$", "", clean_owner(s)).strip()


def area(r: dict) -> str:
    if r["category"] == "us-hyperscaler-africa":
        return "africa"
    g = r["region"].lower()
    if g == "global":
        return "global"
    if not g or g == "unknown":
        return "unknown"
    if g.startswith(("eu-", "europe-", "uk")) or g in EUROPE:
        return "europe"
    if g.startswith(("us-", "ca-")) or g.endswith("us") or g.endswith("us2") or g in {"centralus"}:
        return "namerica"
    return "other"


def rw_json(p: Path, fn) -> None:
    j = json.loads(p.read_text(encoding="utf-8"))
    fn(j)
    p.write_text(json.dumps(j, indent=1), encoding="utf-8")


def chart(path: Path, counts: Counter, routable: int, us: str, cdn: str, date: str) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    rows = [(lab, 100 * counts[c] / routable, grp) for c, lab, grp in CHART if counts[c]]
    rows.sort(key=lambda x: -x[1])
    plt.rcParams["font.family"] = "Segoe UI"
    fig, ax = plt.subplots(figsize=(10, 0.42 * len(rows) + 1.9), dpi=130)
    y = list(range(len(rows)))[::-1]
    ax.barh(y, [v for _, v, _ in rows], color=[COLOURS[g] for _, _, g in rows], height=0.62)
    ax.set_yticks(y, [lab for lab, _, _ in rows], fontsize=11)
    top = max(v for _, v, _ in rows)
    for yy, (_, v, _) in zip(y, rows):
        ax.text(v + top * 0.01, yy, f"{v:.1f}%" if v < 10 else f"{v:.0f}%", va="center", fontsize=10.5)
    ax.set_xlim(0, top * 1.12)
    ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:.0f}%"))
    ax.grid(axis="x", color="#e2e2e2")
    ax.set_axisbelow(True)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color("#bbbbbb")
    ax.tick_params(length=0)
    h = fig.get_figheight()
    fig.suptitle(f"US cloud: {us} of working addresses. Behind shields: {cdn}", x=0.015, y=1 - 0.12 / h, ha="left",
                 va="top", fontsize=14, fontweight="bold")
    fig.text(0.015, 1 - 0.5 / h, f"Share of the {num(routable)} working server addresses, by who hosts them. "
             f"Scan of {date}.", ha="left", va="top", fontsize=10.5, color="#555555")
    used = [g for g in ("us", "home", "hidden") if any(gg == g for _, _, gg in rows)]
    handles = [plt.Rectangle((0, 0), 1, 1, color=COLOURS[g]) for g in used]
    fig.legend(handles, [LEGEND[g] for g in used], loc="upper left", bbox_to_anchor=(0.01, 1 - 0.8 / h), ncol=3,
               frameon=False, fontsize=10, handlelength=1)
    fig.tight_layout(rect=(0, 0, 1, 1 - 0.95 / h))
    fig.savefig(path)
    plt.close(fig)


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("iso3")
    ap.add_argument("--date", default=dt.date.today().isoformat())
    args = ap.parse_args()
    iso = args.iso3.upper()
    out = SCAN / iso
    nodes = read_csv(out / "nodes.csv")
    orgs = read_csv(out / "organisations.csv")
    run = json.loads((out / "run.json").read_text(encoding="utf-8"))
    inp = read_csv(RD / f"institutions-{iso}.csv")
    tiers = {r["institution"]: r["tier"] for r in read_csv(RD / "strategic-institutions.csv")}
    ntypes = len(tiers)
    progress = read_csv(RD / "progress.csv")
    country = next(r["country"] for r in progress if r["iso3"] == iso)
    scan_date = run["scan_date"]
    sd = dt.date.fromisoformat(scan_date)
    sdate = f"{sd.day} {sd.strftime('%B %Y')}"
    rd = dt.date.fromisoformat(args.date)
    rdate = f"{rd.day} {rd.strftime('%B %Y')}"

    rt = [r for r in nodes if r["rr_type"] in ROUTABLE and r["rr_status"] == "ok"]
    n_rt = len(rt)
    cat = Counter(r["category"] for r in rt)
    by_org = defaultdict(list)
    for r in nodes:
        by_org[(r["type"], r["institution"])].append(r)
    orgmap = {(o["type"], o["institution"]): o for o in orgs}
    n_org = len(orgs)
    bank = lambda t: t.strip().lower() == "commercial banks"  # noqa: E731
    covered = {r["type"] for r in inp if r["domain"].strip() and r["status"].strip().lower() != "dead"}
    absent = [t for t in tiers if t not in covered]
    elsewhere = {r["type"]: m.group(1) for r in inp if r["type"] in absent and
                 (m := re.search(r"covered by the (.+?) row", r["note"]))}
    absent = [t for t in absent if t not in elsewhere]

    def share(o, cats):
        rows = [r for r in by_org[(o["type"], o["institution"])] if r["rr_type"] in ROUTABLE and r["rr_status"] == "ok"]
        return sum(r["category"] in cats for r in rows), len(rows)

    us_n = cat["us-hyperscaler-africa"] + cat["us-hyperscaler-offshore"]
    US_P, AF_P, CDN_P = pct(us_n, n_rt), pct(cat["us-hyperscaler-africa"], n_rt), pct(cat["cdn-origin-unknown"], n_rt)
    NAT_P = pct(cat["national-dc"] + cat["self-hosted"], n_rt)
    any_us = [o for o in orgs if share(o, US)[0]]
    m365 = [o for o in orgs if o["mail_provider"] == "m365"]
    goog = [o for o in orgs if o["mail_provider"] == "google"]

    # comparisons: countries whose step 03 cell is a date
    peers = {}
    for p in progress:
        if DATE.match(p["s03_classify"].strip()):
            try:
                roll = json.loads((SCAN / p["iso3"] / "run.json").read_text(encoding="utf-8"))["rollup"]["all"]
                peers[p["iso3"]] = roll
            except (OSError, KeyError, ValueError):
                pass
    N = len(peers)

    def rank(key):
        vals = sorted(peers.values(), key=lambda x: -x[key])
        me = peers[iso][key]
        return 1 + sum(v[key] > me for v in vals), statistics.median(v[key] for v in vals)

    us_rank, us_med = rank("us_hyperscaler_share")
    cdn_rank, cdn_med = rank("cdn_share")

    # dangling cloud names -> run.json findings
    dangling = []
    for r in nodes:
        if r["rr_type"] == "CNAME" and r["rr_status"] == "nxdomain":
            tgt = (r["cname_chain"].split(">")[-1] if r["cname_chain"] else r["target"]).lower().rstrip(".")
            if tgt.endswith(TAKEOVER):
                dangling.append((r["institution"], r["domain"], r["name"], tgt))
    dangling = sorted(set(dangling))

    def add_findings(j):
        have = {f.get("name") for f in j.setdefault("findings", [])}
        for inst, dom, name, tgt in dangling:
            if name not in have:
                j["findings"].append({"kind": "dangling-cloud-cname", "domain": dom, "name": name, "target": tgt,
                                      "finding": "CNAME to a cloud name that no longer exists and that anyone can "
                                                 "register: whoever does can serve content under this name."})
    rw_json(out / "run.json", add_findings)

    L = []
    w = L.append
    w("---")
    w(f"title: {country} — who hosts the state's front door")
    w(f"date: {args.date}")
    w("author: Bill Anderson")
    w(f"source: R&D/Hyperscaler-dependence/scan/{iso}/ (nodes.csv, organisations.csv, run.json)")
    w(f"scan_date: {scan_date}")
    w("---")
    w("")
    w(f"# {country}: who hosts the state's front door")
    w("")
    w(f"{rdate} · Bill Anderson · scan of {sdate}")
    w("")
    w(f"The scan covered {n_org} state bodies, banks and state-owned companies in {country}. "
      f"{US_P} of their working server addresses are on US cloud: Amazon, Microsoft, Google or Oracle. "
      f"{CDN_P} are behind shields such as Cloudflare, which hide the host. "
      f"{NAT_P} are on government data centres or the institutions' own systems.")
    w("")
    w(f"The scan found {num(len({r['name'] for r in nodes}))} web and mail names and {num(n_rt)} working addresses. "
      f"{len(any_us)} of the {n_org} institutions use US cloud for at least part of their estate. "
      f"{len(m365)} use Microsoft for email and {len(goog) or 'none'} use Google.")
    w("")
    w(f"Of the {N} countries scanned so far, {country} has the {ordinal(us_rank)} highest US cloud share "
      f"(median {us_med:.0f}%) and the {ordinal(cdn_rank)} highest share behind shields (median {cdn_med:.0f}%).")
    w("")

    # --- Where it lives
    w("## Where it lives")
    w("")
    w(f"![US cloud: {US_P} of working addresses; behind shields: {CDN_P}](report-chart.png)")
    w("")
    usrows = [r for r in rt if r["category"] in US]
    if usrows:
        a = Counter(area(r) for r in usrows)
        parts = [(a["europe"], "in Europe"), (a["global"], "on worldwide delivery networks (no fixed location)"),
                 (a["africa"], "in Africa"), (a["namerica"], "in North America"), (a["other"], "in Asia or the Middle East"),
                 (a["unknown"], "in a region the providers do not publish")]
        parts = [f"{pct(k, len(usrows))} {t}" for k, t in sorted(parts, key=lambda x: -x[0]) if k]
        w(f"{num(len(usrows))} addresses are on US cloud. Where they are: {listing(parts)}.")
        w("")
    shield = [r for r in rt if r["category"] == "cdn-origin-unknown"]
    if shield:
        s = Counter(clean_owner(r["provider"] or r["owner"]).split(" ")[0].capitalize() for r in shield)
        top = [f"{k} ({pct(v, len(shield))})" for k, v in s.most_common(3)]
        w(f"{num(len(shield))} addresses are behind shields: {listing(top)}. "
          f"The host behind a shield cannot be seen, so the US cloud share is a minimum.")
        w("")

    # --- Banks against government
    w("## Banks against government")
    w("")
    grp = {"Government": [o for o in orgs if not bank(o["type"])], "Banks": [o for o in orgs if bank(o["type"])]}
    rows_of = {g: [r for o in os_ for r in by_org[(o["type"], o["institution"])]
                   if r["rr_type"] in ROUTABLE and r["rr_status"] == "ok"] for g, os_ in grp.items()}
    w(f"| Share of working addresses | Government ({len(grp['Government'])}) | Banks ({len(grp['Banks'])}) |")
    w("| --- | --- | --- |")
    for lab, cs in [("On US cloud", US), ("…of which in Africa", {"us-hyperscaler-africa"}),
                    ("US online services (Microsoft 365 and others)", {"us-saas"}),
                    ("Behind a shield", {"cdn-origin-unknown"}), ("Government data centres", {"national-dc"}),
                    ("Run by the institution itself", {"self-hosted"}), ("Telecoms companies", {"telco-isp"}),
                    ("African data centres and IT firms", {"african-colo"}),
                    ("Other foreign hosting firms", {"commercial-host"})]:
        cells = [pct(sum(r["category"] in cs for r in rows_of[g]), len(rows_of[g])) for g in grp]
        w(f"| {lab} | {cells[0]} | {cells[1]} |")
    w("")
    ug = sum(1 for o in grp["Government"] if share(o, US)[0])
    ub = sum(1 for o in grp["Banks"] if share(o, US)[0])
    w(f"{ub} of {len(grp['Banks'])} banks and {ug} of {len(grp['Government'])} government bodies use US cloud somewhere. "
      f"\"Government\" includes the central bank, the payment switch, the stock exchange and the state-owned companies.")
    w("")

    # --- Email
    w("## Email")
    w("")
    mail = defaultdict(list)
    for o in orgs:
        mp = o["mail_provider"]
        if mp == "m365":
            mail["Microsoft 365"].append(o["institution"])
        elif mp == "google":
            mail["Google"].append(o["institution"])
        elif mp == "self":
            mail["Own mail servers"].append(o["institution"])
        elif mp == "none":
            mail["No mail on the domain scanned"].append(o["institution"])
        else:
            doms = o["domains"].split(";")
            mx = [r for r in by_org[(o["type"], o["institution"])] if r["rr_type"] == "MX" and r["name"] in doms]
            c = Counter(r["category"] for r in mx).most_common(1)
            c = c[0][0] if c else ""
            owner = Counter(short(r["provider"] or r["owner"]) for r in mx if r["category"] == c).most_common(1)
            owner = owner[0][0] if owner else ""
            if o["mail_security"]:
                mail["Behind a mail filter, provider not visible"].append(o["institution"])
            elif c == "national-dc":
                mail[f"Government data centre"].append(f"{o['institution']} ({owner})" if owner else o["institution"])
            elif c in US:
                mail["US cloud"].append(o["institution"])
            elif c == "telco-isp":
                mail["Telecoms companies"].append(f"{o['institution']} ({owner})" if owner else o["institution"])
            elif c == "african-colo":
                mail["African hosts"].append(f"{o['institution']} ({owner})" if owner else o["institution"])
            elif c == "commercial-host":
                mail["Foreign hosting firms"].append(f"{o['institution']} ({owner})" if owner else o["institution"])
            elif c == "cdn-origin-unknown":
                mail["Behind a mail filter, provider not visible"].append(o["institution"])
            else:
                mail["Not identified"].append(o["institution"])
    w(f"{len(m365)} of the {n_org} institutions use Microsoft 365 for email and {len(goog) or 'none'} use Google.")
    w("")
    order = ["Microsoft 365", "Google", "Government data centre", "Own mail servers", "Telecoms companies",
             "African hosts", "US cloud", "Foreign hosting firms", "Behind a mail filter, provider not visible",
             "Not identified", "No mail on the domain scanned"]
    for k in order:
        if mail[k]:
            w(f"- **{k}:** {len(mail[k])}. {listing(mail[k])}.")
    w("")

    # --- Institution by institution
    w("## Institution by institution")
    w("")
    w("Each figure is a share of that institution's working addresses. The rest are with telecoms companies, "
      "African data centres, US online services or foreign hosts. Rows follow the order of institution types.")
    w("")
    w("| Institution | Type | On US cloud | …in Africa | Behind a shield | Own or government | Email |")
    w("| --- | --- | --- | --- | --- | --- | --- |")
    mail_lab = {"m365": "Microsoft", "google": "Google", "self": "Own servers", "none": "—"}
    for inst in dict.fromkeys((r["type"], r["institution"]) for r in inp):
        o = orgmap.get(inst)
        if not o:
            continue
        u, n = share(o, US)
        af, _ = share(o, {"us-hyperscaler-africa"})
        cd, _ = share(o, {"cdn-origin-unknown"})
        ns, _ = share(o, {"national-dc", "self-hosted"})
        ml = mail_lab.get(o["mail_provider"])
        if ml is None:
            ml = next((k for k, v in mail.items() if any(x.startswith(o["institution"]) for x in v)), "Other")
            ml = {"Behind a mail filter, provider not visible": "Filtered", "Government data centre": "Government",
                  "Telecoms companies": "Telecoms", "African hosts": "African host", "Foreign hosting firms": "Foreign host",
                  "No mail on the domain scanned": "—"}.get(ml, ml)
        if not n:
            w(f"| {o['institution']} | {o['type']} | no working address | | | | {ml} |")
        else:
            w(f"| {o['institution']} | {o['type']} | {pct(u, n)} | {pct(af, n)} | {pct(cd, n)} | {pct(ns, n)} | {ml} |")
    w("")
    if elsewhere:
        w(f"{len(elsewhere)} of the {ntypes} types are covered by another institution in the table: "
          f"{listing([f'{t} (in {v})' for t, v in elsewhere.items()])}.")
        w("")
    if absent:
        w(f"No institution or working domain was found for {len(absent)} of the {ntypes} types: {listing(absent)}.")
        w("")

    # --- What stood out
    w("## What stood out")
    w("")
    bullets = []
    heavy = []
    for o in orgs:
        u, n = share(o, US)
        if n >= 5 and u / n >= 0.5:
            heavy.append((u / n, o["institution"]))
    if heavy:
        heavy.sort(reverse=True)
        bullets.append(f"**Most on US cloud.** {listing([f'{i} ({pct(v, 1)})' for v, i in heavy[:5]])} "
                       f"{'has' if len(heavy) == 1 else 'have'} more than half {'its' if len(heavy) == 1 else 'their'} "
                       f"working addresses on US cloud." + (f" {len(heavy) - 5} more are over half." if len(heavy) > 5 else ""))
    afr = sorted(((share(o, {"us-hyperscaler-africa"})[0] / max(share(o, US)[1], 1), o["institution"]) for o in orgs), reverse=True)
    if afr and afr[0][0] >= 0.2:
        bullets.append(f"**US cloud in Africa.** {afr[0][1]} has {pct(afr[0][0], 1)} of its working addresses in US "
                       f"cloud data centres in Africa, the highest share in {country}.")
    elif us_n:
        bullets.append(f"**Little US cloud in Africa.** {pct(cat['us-hyperscaler-africa'], us_n)} of {country}'s US cloud "
                       f"addresses are in the providers' African data centres.")
    spine = [o for o in orgs if tiers.get(o["type"]) == "1 sovereign spine" and not bank(o["type"])]
    home = []
    for o in spine:
        ns, n = share(o, {"national-dc", "self-hosted"})
        if n >= 3 and ns / n >= 0.8:
            home.append(f"{o['institution']} ({pct(ns, n)})")
    if home:
        bullets.append(f"**Core state bodies at home.** {listing(home)} keep{'s' if len(home) == 1 else ''} at least 80% "
                       f"of {'its' if len(home) == 1 else 'their'} working addresses on government data centres or "
                       f"{'its' if len(home) == 1 else 'their'} own systems.")
    cheap = []
    for o in spine:
        hosts = Counter(clean_owner(r["provider"] or r["owner"]) for r in by_org[(o["type"], o["institution"])]
                        if r["rr_type"] in ("A", "AAAA") and r["rr_status"] == "ok" and r["category"] == "commercial-host")
        if hosts:
            cheap.append(f"{o['institution']} ({listing([h for h, _ in hosts.most_common(2) if h])})")
    if cheap:
        bullets.append(f"**Core state bodies on foreign hosting firms.** {listing(cheap[:6])}"
                       + (f", and {len(cheap) - 6} more" if len(cheap) > 6 else "") + ".")
    cn = Counter(o for (t, o), rows in by_org.items() for r in rows
                 if r["category"] == "chinese-cloud" and r["rr_type"] in ROUTABLE and r["rr_status"] == "ok")
    if cn:
        bullets.append(f"**Chinese cloud.** {sum(cn.values())} address{'es' if sum(cn.values()) != 1 else ''} "
                       f"{'are' if sum(cn.values()) != 1 else 'is'} on Chinese cloud: {listing([f'{k} ({v})' for k, v in cn.most_common()])}.")
    else:
        bullets.append("**No Chinese cloud.** The scan found no address on Huawei, Alibaba or Tencent cloud.")
    if dangling:
        insts = sorted({d[0] for d in dangling})
        bullets.append(f"**Names anyone could claim.** {len(dangling)} web address{'es' if len(dangling) != 1 else ''} at "
                       f"{listing(insts)} point{'s' if len(dangling) == 1 else ''} at a deleted cloud name that anyone "
                       f"could register and then publish under. We have flagged {'it' if len(dangling) == 1 else 'them'} "
                       f"and do not name {'it' if len(dangling) == 1 else 'them'} here.")
    for b in bullets:
        w(f"- {b}")
    w("")

    # --- What this can and cannot tell you
    w("## What this can and cannot tell you")
    w("")
    w("The scan sees only the front door: websites, email, login portals, remote-access gateways and online banking. "
      "It cannot see where a bank's core ledger, the ID register or the payroll run.")
    w("")
    w(f"- **Every US figure is a minimum.** Anything behind a shield or a mail filter could also be on US cloud. "
      f"In {country} that is {CDN_P} of working addresses.")
    w("- **It counts addresses, not importance.** An institution with many test and marketing sites weighs more than one with few.")
    w("- **The list of institutions was drawn up for this scan.** Each domain was checked to exist, not confirmed as the institution's main one.")
    w(f"- **It is a snapshot.** Every figure is as of {sdate}.")
    w("- **Nothing was touched.** The scan used public address lookups, public certificate records and the cloud "
      "companies' published address lists. It never connected to any institution's systems.")
    w("")
    w(f"The data and method are in `R&D/Hyperscaler-dependence/scan/{iso}/` and "
      "`R&D/Hyperscaler-dependence/HYPERSCALER-SCAN.md` in the Corpus repository.")
    w("")
    (out / "report.md").write_text("\n".join(L), encoding="utf-8", newline="\n")
    chart(out / "report-chart.png", cat, n_rt, US_P, CDN_P, sdate)
    print(f"{iso} · institutions {n_org} · US {US_P} · shield {CDN_P} · rank {us_rank}/{N} · dangling {len(dangling)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
