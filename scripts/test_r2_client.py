#!/usr/bin/env python3
"""test_r2_client.py — pin the SigV4 canonical request, and what r2-sync decides to move.

    python scripts/test_r2_client.py

**Every way of getting SigV4 wrong produces the same answer: `403 SignatureDoesNotMatch`.** The
server will not say which field was malformed, and the failure arrives only against a live
bucket with real credentials — which is exactly the moment nobody wants to be debugging string
construction. So the canonical request is pinned here character by character, and the two
questions that decide what leaves the tree — *is this an edition?* and *is it safe to delete the
local copy?* — are pinned beside it.

**This proves the request is well formed, not that R2 accepts it.** The first live call is the
only thing that proves the credential and the endpoint, and `r2-sync.py --verify` is what proves
the bucket holds what the tree does.
"""

from __future__ import annotations

import hashlib
import importlib.util
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import r2_client as rc  # noqa: E402

_spec = importlib.util.spec_from_file_location("r2_sync", HERE / "r2-sync.py")
rs = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(rs)

FAILURES: list[str] = []


def check(name: str, got, want) -> None:
    if got != want:
        FAILURES.append(f"{name}\n     got:  {got!r}\n     want: {want!r}")


def ok(name: str, cond: bool, why: str = "") -> None:
    if not cond:
        FAILURES.append(f"{name} — {why}")


# --------------------------------------------------------------------- the canonical request

def test_canonical_shape():
    """Six fields, newline separated, with a blank line closing the header block."""
    headers = {"host": "acct.r2.cloudflarestorage.com", "x-amz-date": "20260908T101500Z",
               "x-amz-content-sha256": "abc"}
    got = rc.canonical_request("PUT", "/bucket/reports/KEN/a.pdf", "", headers, "abc")
    check("canonical request", got, "\n".join([
        "PUT",
        "/bucket/reports/KEN/a.pdf",
        "",
        "host:acct.r2.cloudflarestorage.com",
        "x-amz-content-sha256:abc",
        "x-amz-date:20260908T101500Z",
        "",
        "host;x-amz-content-sha256;x-amz-date",
        "abc",
    ]))


def test_headers_are_sorted_not_insertion_ordered():
    headers = {"x-amz-date": "D", "content-type": "text/csv", "host": "h",
               "x-amz-content-sha256": "S"}
    check("signed headers sorted", rc.signed_headers(headers),
          "content-type;host;x-amz-content-sha256;x-amz-date")


def test_header_values_are_trimmed():
    headers = {"host": "  h  ", "x-amz-date": "D", "x-amz-content-sha256": "S"}
    got = rc.canonical_request("GET", "/b", "", headers, "S")
    ok("header value trimmed", "host:h\n" in got, f"inner whitespace survived: {got!r}")


# --------------------------------------------------------------------- path and query encoding

def test_path_encoding_keeps_slashes_and_escapes_the_rest():
    r2 = rc.R2({"CF_ACCOUNT_ID": "acct", "CF_R2_BUCKET": "editions",
                "CF_R2_ACCESS_KEY_ID": "AK", "CF_R2_SECRET_ACCESS_KEY": "SK"})
    req = r2._request("GET", "reports/KEN/a b.pdf")
    ok("space escaped in path", "/editions/reports/KEN/a%20b.pdf" in req.full_url,
       f"url was {req.full_url}")
    ok("separators kept", req.full_url.count("/editions/reports/KEN/") == 1,
       f"url was {req.full_url}")


def test_query_is_sorted_and_encoded():
    r2 = rc.R2({"CF_ACCOUNT_ID": "acct", "CF_R2_BUCKET": "editions",
                "CF_R2_ACCESS_KEY_ID": "AK", "CF_R2_SECRET_ACCESS_KEY": "SK"})
    req = r2._request("GET", "", query={"prefix": "a/b", "list-type": "2"})
    got = req.full_url.split("?", 1)[1]
    check("query canonical", got, "list-type=2&prefix=a%2Fb")


def test_signature_moves_when_anything_does():
    r2 = rc.R2({"CF_ACCOUNT_ID": "acct", "CF_R2_BUCKET": "editions",
                "CF_R2_ACCESS_KEY_ID": "AK", "CF_R2_SECRET_ACCESS_KEY": "SK"})
    a = r2._request("GET", "x.pdf").get_header("Authorization")
    b = r2._request("GET", "y.pdf").get_header("Authorization")
    c = r2._request("PUT", "x.pdf", body=b"z").get_header("Authorization")
    ok("key changes the signature", a != b, "two keys signed identically")
    ok("method and body change the signature", a != c, "PUT signed as GET")
    ok("algorithm named", a.startswith("AWS4-HMAC-SHA256 Credential=AK/"), a[:60])
    ok("scope is r2's", "/auto/s3/aws4_request" in a, a[:120])


def test_payload_hash_is_the_body():
    r2 = rc.R2({"CF_ACCOUNT_ID": "acct", "CF_R2_BUCKET": "editions",
                "CF_R2_ACCESS_KEY_ID": "AK", "CF_R2_SECRET_ACCESS_KEY": "SK"})
    req = r2._request("PUT", "x.pdf", body=b"hello")
    check("payload hash", req.get_header("X-amz-content-sha256"),
          hashlib.sha256(b"hello").hexdigest())


def test_empty_body_hashes_the_empty_string():
    """A GET must still carry the hash of nothing, not an empty header."""
    r2 = rc.R2({"CF_ACCOUNT_ID": "acct", "CF_R2_BUCKET": "editions",
                "CF_R2_ACCESS_KEY_ID": "AK", "CF_R2_SECRET_ACCESS_KEY": "SK"})
    req = r2._request("GET", "x.pdf")
    check("empty payload hash", req.get_header("X-amz-content-sha256"),
          hashlib.sha256(b"").hexdigest())


def test_etag_is_md5():
    check("etag", rc.etag_of(b"hello"), hashlib.md5(b"hello").hexdigest())


def test_content_types():
    check("pdf type", rc.content_type(Path("a.pdf")), "application/pdf")
    check("csv type", rc.content_type(Path("a.csv")), "text/csv; charset=utf-8")
    check("unknown type", rc.content_type(Path("a.bin")), "application/octet-stream")


# --------------------------------------------------------------------- what moves

def test_candidates_pick_editions_and_names_only():
    """A dated edition and a names shard move; a page, an asset and the catalogue CSV do not.

    `raw-catalogue.csv` is the case worth pinning: §9 keeps it deliberately undated, so it is
    not an edition, and a rule that moved it would take the one download URL that is supposed to
    be republished wholesale on every build."""
    with tempfile.TemporaryDirectory() as tmp:
        site = Path(tmp)
        made = {
            "reports/KEN/KEN-status-2026-08-19.pdf": True,
            "reports/KEN/KEN-monthly-2026-07-2026-08-19-2.pdf": True,
            "countries/KEN/KEN-nonstate-2026-08-19.csv": True,
            "catalogue/names/ab.json": True,
            "catalogue/raw-catalogue.csv": False,
            "catalogue/raw-catalogue.json": False,
            "reports/KEN/index.html": False,
            "assets/css/main.css": False,
            # The bulletin is a dated edition by the grammar and still must not move: its
            # manifest rebuild reads the directory off disk after every deletion.
            "bulletin/corpus-bulletin-2026-09-08.pdf": False,
        }
        for rel in made:
            p = site / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(b"x")
        got = {f.relative_to(site).as_posix() for f in rs.candidates(site)}
        check("candidates", got, {r for r, want in made.items() if want})


def test_verify_refuses_on_size_and_on_md5():
    """The two ways a bucket copy can be wrong, and both must block the local delete."""
    class FakeR2:
        def __init__(self, held):
            self.held = held

        def head(self, key):
            return self.held.get(key)

    with tempfile.TemporaryDirectory() as tmp:
        site = Path(tmp)
        f = site / "reports/KEN/KEN-status-2026-08-19.pdf"
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_bytes(b"the real bytes")
        key = "reports/KEN/KEN-status-2026-08-19.pdf"
        good = {"size": 14, "etag": rc.etag_of(b"the real bytes")}

        check("intact verifies", rs.verify(FakeR2({key: good}), site, [f]), [])
        ok("missing blocks", rs.verify(FakeR2({}), site, [f]), "a missing object verified")
        ok("wrong size blocks",
           rs.verify(FakeR2({key: {"size": 3, "etag": good["etag"]}}), site, [f]),
           "a truncated object verified")
        ok("wrong md5 blocks",
           rs.verify(FakeR2({key: {"size": 14, "etag": "0" * 32}}), site, [f]),
           "a corrupt object verified")


def test_upload_skips_what_already_matches():
    """A re-run after a failure must upload only what did not land."""
    class FakeR2:
        def __init__(self, held):
            self.held = held
            self.put_keys = []

        def head(self, key):
            return self.held.get(key)

        def put(self, key, data, ctype):
            self.put_keys.append(key)
            return rc.etag_of(data)

    with tempfile.TemporaryDirectory() as tmp:
        site = Path(tmp)
        for rel in ("reports/A/A-status-2026-08-19.pdf", "reports/B/B-status-2026-08-19.pdf"):
            p = site / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(b"body")
        files = sorted(rs.candidates(site))
        held = {"reports/A/A-status-2026-08-19.pdf":
                {"size": 4, "etag": rc.etag_of(b"body")}}
        fake = FakeR2(held)
        counts = rs.upload(fake, site, files, apply=True)
        check("uploaded only the missing one", fake.put_keys,
              ["reports/B/B-status-2026-08-19.pdf"])
        check("counts", (counts["sent"], counts["skipped"]), (1, 1))


def main() -> int:
    tests = [v for k, v in sorted(globals().items())
             if k.startswith("test_") and callable(v)]
    for t in tests:
        t()
    if FAILURES:
        print(f"FAIL — {len(FAILURES)} of {len(tests)} checks")
        for f in FAILURES:
            print(f"  {f}")
        return 1
    print(f"ok — {len(tests)} tests, canonical request and move rule pinned")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
