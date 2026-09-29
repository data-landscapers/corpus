#!/usr/bin/env python3
r"""hyperscaler-scan.py — the DNS footprint of one country's institutions, attributed and classified.

Implements `R&D/Hyperscaler-dependence/HYPERSCALER-SCAN.md` §A; that runbook is the spec and `R&D/Hyperscaler-dependence/hyperscaler-dependence.md`
§3 is the classification. Everything here is passive: DNS through a public resolver, crt.sh, RDAP,
RIPEstat and the providers' published range files. **No request of any kind goes to a host under an
institution's domain.**

    python scripts/hyperscaler-scan.py "R&D/Hyperscaler-dependence/institutions-ZAF.csv"

Writes `R&D/Hyperscaler-dependence/scan/{ISO3}/nodes.csv`, `organisations.csv` and `run.json`, then writes `status` (and a
blank `email_domain`) back into the input file (runbook Step 4). Resumes: a domain whose names are
already in `nodes.csv` with today's `scan_date` is not queried again. Rows from an earlier day are
dropped on start — `nodes.csv` is one scan, and git holds the earlier ones.

Judgements the runbook left open, taken here:

- A dictionary name that does not resolve to an address — NXDOMAIN, or the empty NOERROR a
  NODATA wildcard gives every name — is a miss, not a node, and is not written; a root or CT name
  that does not resolve is written with `rr_status`. Misses are cached per day for resume.
- A seeded domain that is the parent zone of other seeded domains (`gov.za`) is scanned root-only:
  its dictionary and CT sweep would be every other institution's estate.
- `saas-targets.csv` may say `us-hyperscaler` rather than a final category: a platform suffix
  (`azurewebsites.net`, `cloudfront.net`) names the provider, and the address then gives the region.
- CloudFront, Azure Front Door and Google's non-Cloud ranges carry no region: they are US hyperscaler
  with `region: global`, counted offshore, never as African. Oracle Cloud counts as a US hyperscaler,
  and `af-johannesburg-1` as an African region.
- DMARC is read from `_dmarc.{domain}`, where it lives.
- `--reattribute` re-reads the lookups over the scan in `nodes.csv` whatever its date, keeps that
  date everywhere, and makes no network call: range files and RDAP answers come from the cache
  as they stand, and an address the cache cannot answer stays `unattributed`.
- Routable means an A, AAAA, MX or NS row that resolved. Shares are of routable rows, and
  `african_region_share` is `us-hyperscaler-africa` rows over routable, a subset of the US share.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import ipaddress
import json
import os
import random
import re
import string
import sys
import threading
import time
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import dns.exception
import dns.rdatatype
import dns.resolver
import requests

ROOT = Path(__file__).resolve().parent.parent
RD = ROOT / "R&D" / "Hyperscaler-dependence"
SCAN = RD / "scan"
RANGES = SCAN / "ranges"
CACHE = SCAN / "cache"
ASN_FILE = RD / "asn-owners.csv"
SAAS_FILE = RD / "saas-targets.csv"
DICT_FILE = RD / "subdomains.txt"

UA = {"User-Agent": "corpus-hyperscaler-scan/1.0 (passive research; DNS and public registries only)"}
TODAY = dt.date.today().isoformat()
CACHE_DAYS = 30
IN_FLIGHT = 20

CATEGORIES = [
    "us-hyperscaler-africa", "us-hyperscaler-offshore", "us-saas", "chinese-cloud", "commercial-host",
    "cdn-origin-unknown", "african-colo", "national-dc", "telco-isp", "self-hosted", "unresolved",
    "unattributed",
]
AFRICAN_REGIONS = {"af-south-1", "southafricanorth", "southafricawest", "africa-south1", "af-johannesburg-1"}
ROUTABLE_TYPES = {"A", "AAAA", "MX", "NS"}
MAIL_SECURITY = {
    "mimecast": "mimecast", "pphosted": "proofpoint", "proofpoint": "proofpoint",
    "messagelabs": "broadcom-messagelabs", "barracuda": "barracuda", "iphmx": "cisco-ironport",
    "trendmicro": "trend-micro", "sophos": "sophos", "mailcontrol": "forcepoint",
}

NODE_COLS = ["iso3", "type", "institution", "domain", "name", "source", "rr_type", "rr_status", "target",
             "ip", "cname_chain", "asn", "owner", "category", "region", "provider", "scan_date"]
ORG_COLS = ["iso3", "type", "institution", "domains", "names", "routable", "us_hyperscaler_share",
            "african_region_share", "us_saas_share", "cdn_share", "national_or_self_share", "unattributed",
            "mail_provider", "mail_security", "tangled_hybrid", "scan_date"]


def say(msg: str) -> None:
    print(msg, file=sys.stderr, flush=True)


def fresh(p: Path, days: float) -> bool:
    return p.exists() and (time.time() - p.stat().st_mtime) < days * 86400


# ---------------------------------------------------------------- range files (runbook Step 1, A.4(2))

class PrefixMap:
    """Longest-prefix match over a few thousand prefixes, one dict per prefix length."""

    def __init__(self) -> None:
        self.t: dict[tuple[int, int], dict[int, dict]] = defaultdict(dict)

    def add(self, cidr: str, info: dict, override: bool = False) -> None:
        try:
            n = ipaddress.ip_network(cidr.strip(), strict=False)
        except ValueError:
            return
        d = self.t[(n.version, n.prefixlen)]
        k = int(n.network_address)
        if override or k not in d:
            d[k] = info

    def get(self, ip: str) -> dict | None:
        a = ipaddress.ip_address(ip)
        bits = a.max_prefixlen
        v = int(a)
        for plen in range(bits, -1, -1):
            d = self.t.get((a.version, plen))
            if d:
                k = (v >> (bits - plen)) << (bits - plen)
                if k in d:
                    return d[k]
        return None


RANGE_SOURCES = {
    "aws.json": "https://ip-ranges.amazonaws.com/ip-ranges.json",
    "google-cloud.json": "https://www.gstatic.com/ipranges/cloud.json",
    "google.json": "https://www.gstatic.com/ipranges/goog.json",
    "cloudflare-v4.txt": "https://www.cloudflare.com/ips-v4",
    "cloudflare-v6.txt": "https://www.cloudflare.com/ips-v6",
    "oracle.json": "https://docs.oracle.com/iaas/tools/public_ip_ranges.json",
    "azure.json": None,  # link scraped from the download page, which changes weekly
}
AZURE_PAGE = "https://www.microsoft.com/en-us/download/details.aspx?id=56519"


def refresh_ranges() -> dict:
    """Fetch each range file; on failure keep the cached copy and its old date. Returns the dates."""
    RANGES.mkdir(parents=True, exist_ok=True)
    meta_p = RANGES / "fetched.json"
    meta = json.loads(meta_p.read_text()) if meta_p.exists() else {}
    for fname, url in RANGE_SOURCES.items():
        p = RANGES / fname
        if fresh(p, 1):
            continue
        try:
            if url is None:
                page = requests.get(AZURE_PAGE, headers=UA, timeout=30).text
                m = re.search(r"https://download\.microsoft\.com/download/[^\"'\s]+ServiceTags_Public_\d+\.json", page)
                if not m:
                    raise RuntimeError("no ServiceTags link on the download page")
                url = m.group(0)
            r = requests.get(url, headers=UA, timeout=60)
            r.raise_for_status()
            p.write_bytes(r.content)
            meta[fname] = {"fetched": TODAY, "url": url}
        except Exception as e:  # noqa: BLE001 — a failed fetch is a recorded state, not a stop
            say(f"  range file {fname}: fetch failed ({e}); {'using cache' if p.exists() else 'NO CACHE'}")
            meta.setdefault(fname, {})["error"] = f"{TODAY}: {e}"
            if not p.exists():
                meta[fname]["fetched"] = None
    meta_p.write_text(json.dumps(meta, indent=1))
    return meta


def load_ranges() -> list[tuple[str, PrefixMap]]:
    """Ordered matchers: the first that holds an address attributes it."""
    maps: list[tuple[str, PrefixMap]] = []

    def load(fname):
        p = RANGES / fname
        return p.read_text(encoding="utf-8") if p.exists() else None

    if (t := load("aws.json")):
        m = PrefixMap()
        j = json.loads(t)
        rows = [(x["ip_prefix"], x) for x in j.get("prefixes", [])] + [(x["ipv6_prefix"], x) for x in j.get("ipv6_prefixes", [])]
        for cidr, x in rows:  # a service-specific entry beats the umbrella AMAZON one
            svc, region, nbg = x.get("service"), x.get("region", ""), x.get("network_border_group", "")
            glob = svc == "CLOUDFRONT" or region == "GLOBAL"
            african = region in AFRICAN_REGIONS or any(s in nbg for s in ("-los-", "-cpt-"))
            info = {"provider": "aws-cloudfront" if svc == "CLOUDFRONT" else "aws",
                    "region": "global" if glob else (nbg or region),
                    "category": "us-hyperscaler-africa" if african and not glob else "us-hyperscaler-offshore"}
            m.add(cidr, info, override=svc != "AMAZON")
        maps.append(("aws", m))

    if (t := load("azure.json")):
        regional, other = PrefixMap(), PrefixMap()
        for v in json.loads(t).get("values", []):
            props = v.get("properties", {})
            region = props.get("region", "")
            svc = props.get("systemService", "") or v.get("name", "")
            for cidr in props.get("addressPrefixes", []):
                if region:
                    regional.add(cidr, {"provider": "azure", "region": region,
                                        "category": "us-hyperscaler-africa" if region in AFRICAN_REGIONS else "us-hyperscaler-offshore"},
                                 override=v.get("name", "").startswith("AzureCloud."))
                else:
                    fd = "FrontDoor" in svc
                    other.add(cidr, {"provider": "azure-front-door" if fd else "azure", "region": "global",
                                     "category": "us-hyperscaler-offshore"}, override=fd)
        maps += [("azure", regional), ("azure-global", other)]

    if (t := load("google-cloud.json")):
        m = PrefixMap()
        for x in json.loads(t).get("prefixes", []):
            scope = x.get("scope", "")
            m.add(x.get("ipv4Prefix") or x.get("ipv6Prefix"), {
                "provider": "google-cloud", "region": scope,
                "category": "us-hyperscaler-africa" if scope in AFRICAN_REGIONS else "us-hyperscaler-offshore"})
        maps.append(("google-cloud", m))

    if (t := load("oracle.json")):
        m = PrefixMap()
        for reg in json.loads(t).get("regions", []):
            region = reg.get("region", "")
            for c in reg.get("cidrs", []):
                m.add(c["cidr"], {"provider": "oracle", "region": region,
                                  "category": "us-hyperscaler-africa" if region in AFRICAN_REGIONS else "us-hyperscaler-offshore"})
        maps.append(("oracle", m))

    m = PrefixMap()
    for f in ("cloudflare-v4.txt", "cloudflare-v6.txt"):
        for line in (load(f) or "").split():
            m.add(line, {"provider": "cloudflare", "region": "", "category": "cdn-origin-unknown"})
    maps.append(("cloudflare", m))

    if (t := load("google.json")):  # all of Google; checked after cloud.json so Cloud keeps its scope
        m = PrefixMap()
        for x in json.loads(t).get("prefixes", []):
            m.add(x.get("ipv4Prefix") or x.get("ipv6Prefix"),
                  {"provider": "google", "region": "global", "category": "us-hyperscaler-offshore"})
        maps.append(("google", m))
    return maps


# ---------------------------------------------------------------- reference tables

def read_csv(p: Path) -> list[dict]:
    with open(p, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def load_saas() -> list[tuple[str, str, str]]:
    rows = [(r["suffix"].lower().strip("."), r["provider"], r["category"]) for r in read_csv(SAAS_FILE)]
    return sorted(rows, key=lambda r: -len(r[0]))  # longest suffix wins


def saas_match(host: str, saas) -> tuple[str, str] | None:
    host = host.lower().rstrip(".")
    for suf, prov, cat in saas:
        if host == suf or host.endswith("." + suf):
            return prov, cat
    return None


STOP = {"the", "of", "and", "for", "south", "african", "africa", "republic", "department", "national",
        "service", "services", "ltd", "limited", "pty", "co", "sa", "za", "inc", "group", "holdings", "net",
        "network", "networks", "office", "soc", "company", "corporation", "agency", "authority", "as", "asn"}
# Words two unrelated owners share often enough that they cannot be the evidence on their own:
# "Central Bank of Kenya" and "Commercial Bank of Kenya" overlap in two tokens and nothing else.
GENERIC = {"bank", "plc", "kenya", "kenyan", "nigeria", "nigerian", "federal", "commission", "ministry"}


def tokens(s: str) -> set[str]:
    return {t for t in re.split(r"[^a-z0-9]+", (s or "").lower()) if t and t not in STOP}


def owner_is(institution: str, domain: str, owner: str) -> bool:
    """RDAP or AS owner names the institution: token overlap >= 2 with one of them distinctive, or its one distinctive token
    (4+ characters, and the start of its domain label) when it has only one; or its domain label (3+
    characters) or bracketed acronym (4+) is a token of the owner; or the label (5+) runs inside
    the owner's name with the spaces taken out (`firstrand` in `First Rand Bank Limited`)."""
    if not owner:
        return False
    ot, it = tokens(owner), tokens(institution)
    if len(it & ot) >= 2 and (it & ot) - GENERIC:
        return True
    label = domain.split(".")[0].lower()
    # "NCBA Group" on ncbagroup.com; never a generic word ("Communications Commission" on ncc.gov.ng)
    core = it - GENERIC
    if len(core) == 1 and len(next(iter(core))) >= 4 and core <= ot and label.startswith(next(iter(core))):
        return True
    acr = {a.lower() for a in re.findall(r"\(([A-Za-z]{4,})\)", institution)}
    compact = re.sub(r"[^a-z0-9]", "", owner.lower())
    return (len(label) >= 3 and label in ot) or bool(acr & ot) or (len(label) >= 5 and label in compact)


# ---------------------------------------------------------------- DNS (A.3)

_local = threading.local()


def resolver() -> dns.resolver.Resolver:
    r = getattr(_local, "r", None)
    if r is None:
        r = dns.resolver.Resolver(configure=False)
        r.nameservers = ["1.1.1.1", "8.8.8.8"]  # 1.1.1.1 first, 8.8.8.8 on failure
        r.timeout = 5
        r.lifetime = 11  # one retry
        _local.r = r
    return r


def chain_of(response, qname: str) -> list[str]:
    """The CNAME chain in a response's answer section, in order."""
    out, cur = [], qname.lower().rstrip(".")
    if response is None:
        return out
    cn = {}
    for rrset in response.answer:
        if rrset.rdtype == dns.rdatatype.CNAME:
            cn[rrset.name.to_text().lower().rstrip(".")] = rrset[0].target.to_text().lower().rstrip(".")
    while cur in cn and len(out) < 12:
        cur = cn[cur]
        out.append(cur)
    return out


def query(name: str, rdtype: str):
    """(status, records, chain). status: ok, nxdomain, noanswer, servfail, timeout."""
    try:
        ans = resolver().resolve(name, rdtype, raise_on_no_answer=False)
        chain = chain_of(ans.response, name)
        if ans.rrset is None:
            return "noanswer", [], chain
        return "ok", [r.to_text() for r in ans.rrset], chain
    except dns.resolver.NXDOMAIN as e:
        chain = []
        try:
            for resp in e.responses().values():
                chain = chain_of(resp, name) or chain
        except Exception:  # noqa: BLE001
            pass
        return "nxdomain", [], chain
    except dns.resolver.NoNameservers:
        return "servfail", [], []
    except (dns.exception.Timeout, dns.resolver.LifetimeTimeout):
        return "timeout", [], []
    except Exception:  # noqa: BLE001
        return "servfail", [], []


def resolve_name(name: str) -> dict:
    st, a, chain = query(name, "A")
    res = {"name": name, "status": st, "A": a, "AAAA": [], "chain": chain}
    if st != "nxdomain":
        st6, aaaa, chain6 = query(name, "AAAA")
        res["AAAA"] = aaaa
        res["chain"] = chain or chain6
        if st != "ok" and st6 == "ok":
            res["status"] = "ok"
    return res


def first_ip(host: str) -> str:
    st, a, _ = query(host, "A")
    return a[0] if a else ""


# ---------------------------------------------------------------- enumeration (A.2)

def crtsh(domain: str) -> tuple[str, set[str]]:
    url = f"https://crt.sh/?q=%25.{domain}&output=json"
    for attempt in (0, 1):
        try:
            r = requests.get(url, headers=UA, timeout=90)
            r.raise_for_status()
            names = set()
            for row in r.json():
                for n in row.get("name_value", "").split("\n"):
                    n = n.strip().lower().rstrip(".")
                    if n.startswith("*."):
                        n = n[2:]
                    if re.fullmatch(r"[a-z0-9_.-]+", n) and (n == domain or n.endswith("." + domain)):
                        names.add(n)
            return "ok", names
        except Exception as e:  # noqa: BLE001
            if attempt == 0:
                say(f"  crt.sh {domain}: {e.__class__.__name__}; retrying in 30 s")
                time.sleep(30)
    return "failed", set()


def is_wildcard(domain: str) -> bool:
    label = "".join(random.choices(string.ascii_lowercase + string.digits, k=16))
    st, a, _ = query(f"{label}.{domain}", "A")
    return st == "ok" and bool(a)


# ---------------------------------------------------------------- attribution (A.4)

class Attributor:
    def __init__(self, maps, saas):
        self.maps, self.saas = maps, saas
        self.asn = {r["asn"].strip(): r for r in read_csv(ASN_FILE)}
        self.new_asns: dict[str, str] = {}
        self.offline = False  # --reattribute: answer from the cache alone, however old; never fetch
        self.rdap_nets: list[tuple[int, int, int, dict]] = []
        self.lock = threading.Lock()
        self.last_call = 0.0
        (CACHE / "rdap").mkdir(parents=True, exist_ok=True)
        (CACHE / "ripe").mkdir(parents=True, exist_ok=True)
        (CACHE / "asn").mkdir(parents=True, exist_ok=True)

    def _throttled_get(self, url: str, rate: float = 0.5):
        with self.lock:
            wait = self.last_call + rate - time.time()
            if wait > 0:
                time.sleep(wait)
            self.last_call = time.time()
        for attempt in (0, 1):
            try:
                r = requests.get(url, headers=UA, timeout=30)
                if r.status_code == 429:
                    time.sleep(10)
                    continue
                r.raise_for_status()
                return r.json()
            except Exception:  # noqa: BLE001
                if attempt:
                    return None
                time.sleep(2)
        return None

    def _cached(self, sub: str, key: str, url: str):
        p = CACHE / sub / (re.sub(r"[^0-9A-Za-z.]", "_", key) + ".json")
        if fresh(p, CACHE_DAYS) or (self.offline and p.exists()):
            try:
                return json.loads(p.read_text(encoding="utf-8"))
            except ValueError:  # half-written by a scan running beside this one; fetch it again
                pass
        if self.offline:
            return None
        j = self._throttled_get(url)
        if j is not None:
            # Atomic swap: up to three country scans share this cache (HYPERSCALER-DRAIN.md step 02).
            tmp = p.with_suffix(f".{os.getpid()}.tmp")
            tmp.write_text(json.dumps(j), encoding="utf-8")
            tmp.replace(p)
        return j

    def rdap(self, ip: str) -> dict:
        """Registered owner of the address; one RDAP call serves every address in its network."""
        a = ipaddress.ip_address(ip)
        for v, lo, hi, info in self.rdap_nets:
            if v == a.version and lo <= int(a) <= hi:
                return info
        j = self._cached("rdap", ip, f"https://rdap.org/ip/{ip}") or {}
        # the registrant only: an admin or tech contact's name is often a person's, never the owner's
        owner = ""
        for ent in j.get("entities", []) or []:
            if "registrant" in ent.get("roles", []) and not owner:
                for item in (ent.get("vcardArray") or [None, []])[1]:
                    if item[0] == "fn" and item[3]:
                        owner = item[3]
        info = {"owner": owner, "net": j.get("name", "")}
        try:
            lo, hi = int(ipaddress.ip_address(j["startAddress"])), int(ipaddress.ip_address(j["endAddress"]))
            if hi - lo < 2 ** 24 or a.version == 6:
                self.rdap_nets.append((a.version, lo, hi, info))
        except Exception:  # noqa: BLE001
            pass
        return info

    def asn_of(self, ip: str) -> tuple[str, str]:
        j = self._cached("ripe", ip, f"https://stat.ripe.net/data/network-info/data.json?resource={ip}") or {}
        asns = (j.get("data") or {}).get("asns") or []
        if not asns:
            return "", ""
        asn = str(asns[0])
        h = self._cached("asn", asn, f"https://stat.ripe.net/data/as-overview/data.json?resource=AS{asn}") or {}
        return asn, ((h.get("data") or {}).get("holder") or "")

    def by_suffix(self, hosts: list[str]):
        for h in hosts:
            m = saas_match(h, self.saas)
            if m:
                return m
        return None

    def attribute(self, hosts: list[str], ip: str, institution: str, domain: str) -> dict:
        """hosts: the CNAME chain (or MX/NS target), ip: an address or ''. First hit wins."""
        out = {"asn": "", "owner": "", "category": "", "region": "", "provider": ""}
        hint = self.by_suffix(hosts)
        if hint and hint[1] != "us-hyperscaler":
            out.update(provider=hint[0], category=hint[1], owner=hint[0])
            return out
        if not ip:
            if hint:
                out.update(provider=hint[0], category="us-hyperscaler-offshore", region="unknown", owner=hint[0])
            return out
        a = ipaddress.ip_address(ip)
        if a.is_private or a.is_loopback or a.is_reserved or a.is_link_local or a.is_unspecified:
            out.update(category="unresolved", owner="non-public address")
            return out
        for _, m in self.maps:
            info = m.get(ip)
            if info:
                out.update(provider=info["provider"], region=info["region"], category=info["category"],
                           owner=info["provider"])
                return out
        if hint:  # a platform suffix whose address is outside the published ranges
            out.update(provider=hint[0], category="us-hyperscaler-offshore", region="unknown", owner=hint[0])
            return out
        r = self.rdap(ip)
        asn, holder = self.asn_of(ip)
        out.update(asn=asn, owner=r["owner"] or holder or r["net"])
        known = self.asn.get(asn)
        if owner_is(institution, domain, r["owner"]) or owner_is(institution, domain, holder) or \
                (known and owner_is(institution, domain, known.get("owner", ""))):
            out["category"] = "self-hosted"
        elif known and known.get("category"):
            out.update(category=known["category"], provider=known.get("owner", ""))
        else:
            out["category"] = "unattributed"
            if asn and asn not in self.asn:
                self.new_asns[asn] = holder or r["owner"]
        return out

    def save_new_asns(self) -> None:
        if not self.new_asns:
            return
        # Re-read before appending: a scan running beside this one may have added the same ASN since start.
        have = {r["asn"].strip() for r in read_csv(ASN_FILE)}
        with open(ASN_FILE, "a", encoding="utf-8", newline="") as f:
            w = csv.writer(f, lineterminator="\n")
            for asn, owner in sorted(self.new_asns.items(), key=lambda x: int(x[0])):
                if asn in have:
                    continue
                w.writerow([asn, owner, "", f"added by scan {TODAY}; classify by hand"])


# ---------------------------------------------------------------- per-domain scan

def scan_domain(row, iso3, domains_all, dictionary, att, wr, misses, runinfo):
    domain = row["domain"].strip().lower()
    base = {"iso3": iso3, "type": row["type"], "institution": row["institution"], "domain": domain,
            "scan_date": TODAY}
    info = {"wildcard": False, "ct_status": "not run", "ct_names": 0, "dictionary_hits": 0, "scope": "full"}
    sources: dict[str, set[str]] = defaultdict(set)
    sources[domain].add("root")
    sources["www." + domain].add("root")

    # a parent zone of other seeded domains is scanned root-only
    children = [d for d in domains_all if d != domain and d.endswith("." + domain)]
    if children:
        info["scope"] = f"root-only: parent zone of {len(children)} seeded domains"
    else:
        info["ct_status"], ct = crtsh(domain)
        # a CT name that sits under a more specific seeded domain belongs to that domain
        ct = {n for n in ct if not any(n == d or n.endswith("." + d) for d in domains_all
                                       if d != domain and d.endswith("." + domain))}
        info["ct_names"] = len(ct)
        for n in ct:
            sources[n].add("ct")
        info["wildcard"] = is_wildcard(domain)
        for w in dictionary:
            sources[f"{w}.{domain}"].add("dictionary")

    names = sorted(sources)
    with ThreadPoolExecutor(IN_FLIGHT) as ex:
        results = list(ex.map(lambda n: (n, resolve_name(n) if n not in misses else None), names))

    rows = []
    for name, res in results:
        src = sources[name]
        dict_only = src == {"dictionary"}
        if res is None or (dict_only and res["status"] != "ok"):
            misses.add(name)
            continue
        if dict_only and info["wildcard"]:
            continue  # a wildcard answers every name; only CT can vouch for one
        if dict_only:
            info["dictionary_hits"] += 1
        common = dict(base, name=name, source=";".join(s for s in ("root", "dictionary", "ct") if s in src),
                      cname_chain=">".join(res["chain"]))
        target = res["chain"][-1] if res["chain"] else ""
        ips = [("A", ip) for ip in res["A"]] + [("AAAA", ip) for ip in res["AAAA"]]
        if ips:
            for rr, ip in ips:
                rows.append(dict(common, rr_type=rr, rr_status="ok", target=target, ip=ip,
                                 **att.attribute(res["chain"], ip, row["institution"], domain)))
        elif res["chain"]:  # a CNAME that leads nowhere
            rows.append(dict(common, rr_type="CNAME", rr_status=res["status"], target=target, ip="",
                             **att.attribute(res["chain"], "", row["institution"], domain)))
        else:
            rows.append(dict(common, rr_type="A", rr_status=res["status"], target="", ip="",
                             asn="", owner="", category="unresolved", region="", provider=""))

    # root-only record types: MX, NS, and TXT kept only for SPF and DMARC
    rcommon = dict(base, name=domain, source="root", cname_chain="")
    root_mx_status = "nxdomain"
    for rr in ("MX", "NS"):
        st, recs, _ = query(domain, rr)
        if rr == "MX":
            root_mx_status = st
        if st != "ok":
            if st != "noanswer":
                rows.append(dict(rcommon, rr_type=rr, rr_status=st, target="", ip="", asn="", owner="",
                                 category="unresolved", region="", provider=""))
            continue
        for rec in recs:
            host = (rec.split()[-1]).lower().rstrip(".")
            if not host:  # null MX
                continue
            ip = first_ip(host)
            rows.append(dict(rcommon, rr_type=rr, rr_status="ok" if ip else "noaddress", target=host, ip=ip,
                             **att.attribute([host], ip, row["institution"], domain)))
    for qname, prefix in ((domain, "v=spf1"), ("_dmarc." + domain, "v=dmarc1")):
        st, recs, _ = query(qname, "TXT")
        for rec in recs:
            txt = "".join(re.findall(r'"((?:[^"\\]|\\.)*)"', rec)) or rec
            if txt.lower().startswith(prefix):
                rows.append(dict(rcommon, name=qname, rr_type="TXT", rr_status="ok", target=txt[:500], ip="",
                                 asn="", owner="", category="", region="", provider=""))

    root_dead = all(r["rr_status"] == "nxdomain" for r in rows if r["name"] == domain and r["rr_type"] in ("A", "MX")) \
        and root_mx_status == "nxdomain"
    info["dead"] = root_dead
    info["has_mx"] = root_mx_status == "ok"
    for r in rows:
        wr.writerow(r)
    runinfo[domain] = info
    return rows


# ---------------------------------------------------------------- roll-ups (A.6)

def shares(rows: list[dict]) -> dict:
    rt = [r for r in rows if r["rr_type"] in ROUTABLE_TYPES and r["rr_status"] == "ok"]
    n = len(rt)
    c = Counter(r["category"] for r in rt)
    pct = lambda k: round(100 * k / n, 1) if n else 0.0  # noqa: E731
    return {
        "routable": n,
        "us_hyperscaler_share": pct(c["us-hyperscaler-africa"] + c["us-hyperscaler-offshore"]),
        "african_region_share": pct(c["us-hyperscaler-africa"]),
        "us_saas_share": pct(c["us-saas"]),
        "cdn_share": pct(c["cdn-origin-unknown"]),
        "national_or_self_share": pct(c["national-dc"] + c["self-hosted"]),
        "unattributed": c["unattributed"],
        "by_category": dict(c),
    }


def mail_of(rows: list[dict], domains: list[str]) -> tuple[str, str]:
    mx = [r for r in rows if r["rr_type"] == "MX" and r["name"] in domains and r["target"]]
    spf = " ".join(r["target"].lower() for r in rows if r["rr_type"] == "TXT" and r["name"] in domains)
    hay = " ".join(r["target"] for r in mx) + " " + spf
    security = sorted({v for k, v in MAIL_SECURITY.items() if k in hay})
    targets = " ".join(r["target"] for r in mx)
    if not mx:
        prov = "none"
    elif "protection.outlook.com" in targets:
        prov = "m365"
    elif re.search(r"google(mail)?\.com|googlehosted", targets):
        prov = "google"
    elif any(r["category"] in ("self-hosted",) for r in mx):
        prov = "self"
    elif "spf.protection.outlook.com" in spf:  # behind a mail gateway
        prov = "m365"
    elif "_spf.google.com" in spf:
        prov = "google"
    else:
        owners = sorted({(r["provider"] or r["owner"] or r["target"]) for r in mx})
        prov = "other:" + "|".join(o for o in owners if o)[:80]
    return prov, ";".join(security)


def sector(t: str) -> str:
    return "bank" if t.strip().lower() == "commercial banks" else "government"


# ---------------------------------------------------------------- main

def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("--reattribute", action="store_true",
                    help="no DNS: re-run attribution over today's nodes.csv (after asn-owners.csv is classified by hand)")
    args = ap.parse_args()
    inp = Path(args.input)
    m = re.search(r"institutions-([A-Z]{3})\.csv$", inp.name)
    if not m:
        say("SCAN STOP: input must be institutions-{ISO3}.csv")
        return 1
    iso3 = m.group(1)
    raw = inp.read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    crlf = b"\r\n" in raw
    text = raw.decode("utf-8-sig")
    reader = csv.DictReader(text.splitlines())
    fields = reader.fieldnames
    inst = list(reader)

    out = SCAN / iso3
    run_p = out / "run.json"
    prev = json.loads(run_p.read_text()) if run_p.exists() else {}
    if args.reattribute:
        # No network, and the scan's own date stands: a re-attribution is not a new scan (HYPERSCALER-DRAIN.md step 03).
        say(f"Re-attributing {iso3} from the lookups")
        fetched = {k: {"fetched": v} for k, v in prev.get("range_files", {}).items()}
        scan_date = prev.get("scan_date", TODAY)
    else:
        say(f"Scanning {iso3}: {len(inst)} rows")
        say("  refreshing range files")
        fetched = refresh_ranges()
        scan_date = TODAY
    maps = load_ranges()
    saas = load_saas()
    dictionary = [l.strip().lower() for l in DICT_FILE.read_text(encoding="utf-8").splitlines()
                  if l.strip() and not l.startswith("#")]
    att = Attributor(maps, saas)
    att.offline = args.reattribute

    out.mkdir(parents=True, exist_ok=True)
    nodes_p = out / "nodes.csv"
    existing = [r for r in read_csv(nodes_p) if r["scan_date"] == scan_date] if nodes_p.exists() else []
    done = {r["domain"] for r in existing}
    misses_p = CACHE / f"misses-{iso3}-{TODAY}.txt"
    misses = set(misses_p.read_text().split()) if misses_p.exists() else set()
    runinfo = prev.get("domains", {}) if prev.get("scan_date") == scan_date else {}

    # An `absent` row carries no domain: it records coverage, and there is nothing to scan.
    live = [r for r in inst if r["domain"].strip() and r["status"].strip().lower() != "dead"]
    domains_all = [r["domain"].strip().lower() for r in live]
    if args.reattribute:
        by_dom = {r["domain"].strip().lower(): r for r in live}
        for r in existing:
            if r["rr_type"] in ("A", "AAAA", "MX", "NS", "CNAME") and (r["ip"] or r["cname_chain"] or r["target"]):
                hosts = r["cname_chain"].split(">") if r["cname_chain"] else ([r["target"]] if r["target"] else [])
                r.update(att.attribute(hosts, r["ip"], by_dom[r["domain"]]["institution"], r["domain"]))
        done = {r["domain"] for r in existing}
        runinfo = {d: i for d, i in runinfo.items() if d in done}
    all_rows = list(existing)
    with open(nodes_p, "w", encoding="utf-8", newline="") as f:
        wr = csv.DictWriter(f, NODE_COLS, lineterminator="\n")
        wr.writeheader()
        for r in existing:
            wr.writerow(r)
        f.flush()
        for i, row in enumerate(live, 1):
            d = row["domain"].strip().lower()
            if (d in done and d in runinfo) or args.reattribute:
                continue
            say(f"  [{i}/{len(live)}] {row['institution']} — {d}")
            all_rows += scan_domain(row, iso3, domains_all, dictionary, att, wr, misses, runinfo)
            f.flush()
            misses_p.write_text("\n".join(sorted(misses)))
            run_p.write_text(json.dumps({"iso3": iso3, "scan_date": TODAY, "domains": runinfo}, indent=1))
    att.save_new_asns()

    # organisations.csv
    by_inst: dict[tuple[str, str], list[dict]] = defaultdict(list)
    doms: dict[tuple[str, str], list[str]] = defaultdict(list)
    for row in live:
        doms[(row["type"], row["institution"])].append(row["domain"].strip().lower())
    for r in all_rows:
        by_inst[(r["type"], r["institution"])].append(r)
    orgs = []
    for key, dl in doms.items():
        rows = by_inst.get(key, [])
        s = shares(rows)
        mp, ms = mail_of(rows, dl)
        cats = {r["category"] for r in rows if r["rr_status"] == "ok"}
        orgs.append({
            "iso3": iso3, "type": key[0], "institution": key[1], "domains": ";".join(dl),
            "names": len({r["name"] for r in rows}), "routable": s["routable"],
            **{k: s[k] for k in ("us_hyperscaler_share", "african_region_share", "us_saas_share", "cdn_share",
                                 "national_or_self_share", "unattributed")},
            "mail_provider": mp, "mail_security": ms,
            "tangled_hybrid": str(bool(cats & {"national-dc", "self-hosted"}) and
                                  bool(cats & {"us-hyperscaler-africa", "us-hyperscaler-offshore"})).lower(),
            "scan_date": scan_date,
        })
    with open(out / "organisations.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, ORG_COLS, lineterminator="\n")
        w.writeheader()
        w.writerows(orgs)

    # run.json
    def rollup(rows, org_rows):
        s = shares(rows)
        s.update(institutions=len(org_rows), names=len({r["name"] for r in rows}),
                 m365=sum(o["mail_provider"] == "m365" for o in org_rows),
                 google=sum(o["mail_provider"] == "google" for o in org_rows),
                 tangled_hybrid=sum(o["tangled_hybrid"] == "true" for o in org_rows),
                 any_us_hyperscaler=sum(o["us_hyperscaler_share"] > 0 for o in org_rows))
        return s
    roll = {"all": rollup(all_rows, orgs)}
    for sec in ("government", "bank"):
        roll[sec] = rollup([r for r in all_rows if sector(r["type"]) == sec],
                           [o for o in orgs if sector(o["type"]) == sec])
    run = {"iso3": iso3, "scan_date": scan_date,
           "range_files": {k: v.get("fetched") for k, v in fetched.items() if k != "fetched.json"},
           "range_file_errors": prev.get("range_file_errors", {}) if args.reattribute else
                                {k: v["error"] for k, v in fetched.items() if v.get("error")},
           "domains": runinfo, "new_asns": att.new_asns, "rollup": roll,
           "findings": prev.get("findings", []) if prev.get("scan_date") == scan_date else []}
    run_p.write_text(json.dumps(run, indent=1))

    # Step 4: status and a blank email_domain back into the input file
    for row in inst:
        d = row["domain"].strip().lower()
        i = runinfo.get(d)
        if not i:
            continue
        row["status"] = "dead" if i.get("dead") else f"scanned {scan_date}"
        if not row["email_domain"].strip() and i.get("has_mx"):
            row["email_domain"] = d
    import io
    buf = io.StringIO()
    w = csv.DictWriter(buf, fields, lineterminator="\r\n" if crlf else "\n")
    w.writeheader()
    w.writerows(inst)
    try:
        inp.write_bytes((b"\xef\xbb\xbf" if bom else b"") + buf.getvalue().encode("utf-8"))
    except PermissionError:  # open in Excel: the scan stands, and `--reattribute` writes it back later
        say(f"  {inp.name} is locked; status not written back: close it and re-run with --reattribute")

    a = roll["all"]
    print(f"{iso3} · institutions {a['institutions']} · names {a['names']} · routable {a['routable']} · "
          f"us-hyperscaler {a['us_hyperscaler_share']:.0f}% (african region {a['african_region_share']:.0f}%) · "
          f"m365 {a['m365']} · google {a['google']} · cdn-fronted {a['cdn_share']:.0f}% · "
          f"national/self {a['national_or_self_share']:.0f}% · unattributed {a['unattributed']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
