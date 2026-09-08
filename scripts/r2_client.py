#!/usr/bin/env python3
r"""r2_client.py — the smallest S3 client that will talk to Cloudflare R2, and nothing more.

`documentation/editions-serving-shape.md` is why this exists. It is imported by `r2-sync.py`,
which moves editions into the bucket, and by `prune-editions.py`, which deletes them from it.

**Why not boto3.** It is not installed on the machine that runs RENDER and pulling a dependency
in for four HTTP verbs would put the render's ability to publish behind a package index. R2's
S3-compatible endpoint needs SigV4 and nothing else, and SigV4 is sixty lines of hmac. The
whole surface used here is HEAD, GET, PUT, DELETE and one list — no multipart (every edition is
under 2 MB against a 5 GB single-`PUT` ceiling), no ACLs, no versioning.

**Credentials are R2's own, and separate from the KV token.** `CF_R2_ACCESS_KEY_ID` and
`CF_R2_SECRET_ACCESS_KEY` are an S3 key pair minted under *R2 · Manage API tokens*; the
`CF_API_TOKEN` the pruner uses for KV is a different credential with a different scope and the
two are not interchangeable. Environment first, then `logs/.cloudflare-r2.json`, which
`.gitignore` excludes.

**Every error raises.** There is no partial success here and nothing in this file decides
policy: a caller that is about to delete a local file because the bucket has it must be able to
trust that a returned `True` means the object was seen, and the only way to promise that is for
every other outcome to be an exception.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import hmac
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CREDS = ROOT / "logs" / ".cloudflare-r2.json"

REGION = "auto"          # R2 is regionless; SigV4 still demands a region and this is the literal
SERVICE = "s3"
ALGORITHM = "AWS4-HMAC-SHA256"
S3_NS = "{http://s3.amazonaws.com/doc/2006-03-01/}"

# Content types for what actually goes in the bucket. R2 serves back exactly what was recorded
# at upload, so a wrong or missing type here is a PDF the browser offers to save as a text file.
TYPES = {
    ".pdf": "application/pdf",
    ".csv": "text/csv; charset=utf-8",
    ".txt": "text/plain; charset=utf-8",     # the catalogue's 5,658 name shards
    ".json": "application/json",
    ".js": "application/javascript",
}


def credentials() -> dict:
    """Account, bucket and S3 key pair, from the environment or the gitignored file. Never git."""
    keys = ("CF_ACCOUNT_ID", "CF_R2_BUCKET", "CF_R2_ACCESS_KEY_ID", "CF_R2_SECRET_ACCESS_KEY")
    got = {k: os.environ.get(k, "") for k in keys}
    if not all(got.values()) and CREDS.exists():
        held = json.loads(CREDS.read_text(encoding="utf-8"))
        for k in keys:
            got[k] = got[k] or str(held.get(k, ""))
    missing = [k for k, v in got.items() if not v]
    if missing:
        raise LookupError(
            f"no credential for {', '.join(missing)} — environment or logs/{CREDS.name}")
    return got


def _sign(key: bytes, msg: str) -> bytes:
    return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()


def _signing_key(secret: str, stamp: str) -> bytes:
    k = _sign(f"AWS4{secret}".encode("utf-8"), stamp)
    k = _sign(k, REGION)
    k = _sign(k, SERVICE)
    return _sign(k, "aws4_request")


def signed_headers(headers: dict) -> str:
    """The `SignedHeaders` list: every header name, lowercased, sorted, semicolon-joined."""
    return ";".join(sorted(headers))


def canonical_request(method: str, canonical_path: str, canonical_query: str,
                      headers: dict, payload_hash: str) -> str:
    """The canonical request, exactly as SigV4 specifies it.

    **Six fields and a trailing blank line, and every one of the ways to get it wrong is
    silent** — an unsorted header list, an unencoded path, a header value with inner whitespace
    left in, a missing newline after the header block. The server answers `403 SignatureDoesNot
    Match` for all of them and says which of none. `test_r2_client.py` pins the shape."""
    canonical_headers = "".join(f"{k}:{headers[k].strip()}\n" for k in sorted(headers))
    return (f"{method}\n{canonical_path}\n{canonical_query}\n"
            f"{canonical_headers}\n{signed_headers(headers)}\n{payload_hash}")


class R2:
    """One bucket, addressed by the key that is also the file's path under `site/`."""

    def __init__(self, creds: dict | None = None, timeout: int = 120):
        c = creds or credentials()
        self.account = c["CF_ACCOUNT_ID"]
        self.bucket = c["CF_R2_BUCKET"]
        self.access = c["CF_R2_ACCESS_KEY_ID"]
        self.secret = c["CF_R2_SECRET_ACCESS_KEY"]
        self.host = f"{self.account}.r2.cloudflarestorage.com"
        self.timeout = timeout

    # ------------------------------------------------------------------ signing

    def _request(self, method: str, key: str = "", query: dict | None = None,
                 body: bytes = b"", headers: dict | None = None) -> urllib.request.Request:
        """A signed request. The canonical path is `/bucket/key` with each segment encoded.

        `safe=""` on the key segments and `safe="/"` on the join is the whole of the encoding
        rule: a literal `/` separates segments and everything else in a segment is escaped, which
        is what makes a signature over a path with a space in it verify."""
        query = query or {}
        headers = {k.lower(): v for k, v in (headers or {}).items()}
        now = dt.datetime.now(dt.timezone.utc)
        stamp, when = now.strftime("%Y%m%d"), now.strftime("%Y%m%dT%H%M%SZ")

        path = "/" + self.bucket + ("/" + key if key else "")
        canonical_path = urllib.parse.quote(path, safe="/")
        canonical_query = "&".join(
            f"{urllib.parse.quote(k, safe='')}={urllib.parse.quote(str(v), safe='')}"
            for k, v in sorted(query.items()))

        payload_hash = hashlib.sha256(body).hexdigest()
        headers.update({"host": self.host, "x-amz-date": when,
                        "x-amz-content-sha256": payload_hash})

        signed = signed_headers(headers)
        canonical = canonical_request(method, canonical_path, canonical_query,
                                      headers, payload_hash)

        scope = f"{stamp}/{REGION}/{SERVICE}/aws4_request"
        to_sign = (f"{ALGORITHM}\n{when}\n{scope}\n"
                   f"{hashlib.sha256(canonical.encode('utf-8')).hexdigest()}")
        signature = hmac.new(_signing_key(self.secret, stamp),
                             to_sign.encode("utf-8"), hashlib.sha256).hexdigest()
        headers["authorization"] = (
            f"{ALGORITHM} Credential={self.access}/{scope}, "
            f"SignedHeaders={signed}, Signature={signature}")

        url = f"https://{self.host}{canonical_path}"
        if canonical_query:
            url += "?" + canonical_query
        req = urllib.request.Request(url, data=body or None, method=method)
        for k, v in headers.items():
            req.add_header(k, v)
        return req

    def _send(self, req: urllib.request.Request, allow_404: bool = False, attempts: int = 5):
        """Send, retrying the faults that mean *try again* and raising the ones that mean *stop*.

        **A 503 from R2 is weather, not a verdict.** Cloudflare returns one occasionally under
        any sustained load, and at 8,139 objects an occasional one is a near certainty — so a
        single transient fault used to abort a whole sync two thirds of the way through. Retried
        with a widening wait; a fault that survives five attempts is real and still raises.

        **Only the transient codes are retried.** A 403 is the wrong token scope and a 404 is a
        missing object; repeating either just asks the same question again more slowly. The
        request is re-signed each time because SigV4 covers a timestamp that goes stale."""
        transient = {408, 429, 500, 502, 503, 504}
        for attempt in range(attempts):
            try:
                return urllib.request.urlopen(req, timeout=self.timeout)
            except urllib.error.HTTPError as e:
                if e.code == 404 and allow_404:
                    return None
                if e.code in transient and attempt < attempts - 1:
                    time.sleep(2 ** attempt * 0.5)
                    req = self._resign(req)
                    continue
                detail = e.read().decode("utf-8", "replace")[:400]
                raise RuntimeError(
                    f"R2 {req.get_method()} {req.full_url} → {e.code}: {detail}") from e
            except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
                # A dropped connection is the same class of problem as a 503 and gets the same
                # answer. The last attempt raises rather than returning something half-read.
                if attempt < attempts - 1:
                    time.sleep(2 ** attempt * 0.5)
                    req = self._resign(req)
                    continue
                raise RuntimeError(f"R2 {req.get_method()} {req.full_url} → {e}") from e

    def _resign(self, req: urllib.request.Request) -> urllib.request.Request:
        """Rebuild a request with a fresh timestamp and signature, keeping method, URL and body.

        SigV4 signs `x-amz-date`, and Cloudflare rejects a signature more than a few minutes old,
        so a retry that replayed the original request would start failing on 403 the moment the
        backoff outlasted the clock skew window."""
        parsed = urllib.parse.urlsplit(req.full_url)
        key = urllib.parse.unquote(parsed.path).lstrip("/")
        key = key[len(self.bucket):].lstrip("/") if key.startswith(self.bucket) else key
        query = dict(urllib.parse.parse_qsl(parsed.query))
        keep = {k: v for k, v in req.headers.items()
                if k.lower() in ("content-type", "content-length")}
        return self._request(req.get_method(), key, query=query,
                             body=req.data or b"", headers=keep)

    # ------------------------------------------------------------------ verbs

    def head(self, key: str) -> dict | None:
        """Size, ETag and content type, or None when the object is not there.

        **The content type is returned because R2 serves back exactly what was recorded at
        upload, and nothing downstream can correct it.** The Worker copies it onto the response
        with `writeHttpMetadata`, so an object stored as `application/octet-stream` is a PDF the
        browser offers to save rather than open — wrong in a way that is invisible from the
        bucket listing and obvious to a reader."""
        r = self._send(self._request("HEAD", key), allow_404=True)
        if r is None:
            return None
        with r:
            return {"size": int(r.headers.get("Content-Length", 0)),
                    "etag": (r.headers.get("ETag") or "").strip('"'),
                    "type": (r.headers.get("Content-Type") or "").strip()}

    def put(self, key: str, data: bytes, content_type: str | None = None) -> str:
        """Upload, returning the ETag. Overwrites — R2 has no versioning here and none is wanted."""
        headers = {"content-type": content_type or "application/octet-stream",
                   "content-length": str(len(data))}
        with self._send(self._request("PUT", key, body=data, headers=headers)) as r:
            return (r.headers.get("ETag") or "").strip('"')

    def get(self, key: str) -> bytes | None:
        r = self._send(self._request("GET", key), allow_404=True)
        if r is None:
            return None
        with r:
            return r.read()

    def delete(self, key: str) -> None:
        self._send(self._request("DELETE", key), allow_404=True)

    def list(self, prefix: str = "") -> dict:
        """Every key under `prefix`, mapped to its size. Paged; a failed page raises.

        **A partial listing is the one shape of wrongness a deletion rule cannot survive** — it
        is a listing missing exactly the objects that would have protected files — so nothing
        here returns what arrived before an error."""
        found: dict[str, int] = {}
        token = ""
        while True:
            query = {"list-type": "2", "max-keys": "1000"}
            if prefix:
                query["prefix"] = prefix
            if token:
                query["continuation-token"] = token
            with self._send(self._request("GET", "", query=query)) as r:
                tree = ET.fromstring(r.read())
            for c in tree.findall(f"{S3_NS}Contents"):
                k = c.findtext(f"{S3_NS}Key")
                if k:
                    found[k] = int(c.findtext(f"{S3_NS}Size") or 0)
            if tree.findtext(f"{S3_NS}IsTruncated") != "true":
                return found
            token = tree.findtext(f"{S3_NS}NextContinuationToken") or ""
            if not token:
                return found


def content_type(path: Path) -> str:
    return TYPES.get(path.suffix.lower(), "application/octet-stream")


def etag_of(data: bytes) -> str:
    """R2's ETag for a single-part upload is the MD5 of the body, which is what this compares."""
    return hashlib.md5(data).hexdigest()
