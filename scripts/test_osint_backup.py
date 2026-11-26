"""Tests for osint-backup.py's rules, against a stand-in bucket: no network, no mirror."""
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("osint_backup", HERE / "osint-backup.py")
ob = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ob)


class FakeBucket:
    def __init__(self, held=None):
        self.held = dict(held or {})
        self.puts = []

    def listing(self, prefix=""):
        return dict(self.held)

    def put(self, key, data, content_type=None):
        self.puts.append(key)
        self.held[key] = (len(data), ob.r2_client.etag_of(data))
        return ob.r2_client.etag_of(data)


class Rules(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        t = Path(self.tmp.name)
        (t / "raw" / "2026").mkdir(parents=True)
        (t / "budget-archive" / "AGO").mkdir(parents=True)
        (t / "raw" / "2026" / "a.pdf").write_bytes(b"aaaa")
        (t / "raw" / "2026" / "a.md").write_text("tracked")
        (t / "budget-archive" / "AGO" / "b.PDF").write_bytes(b"bb")
        (t / "budget-archive" / "AGO" / "c.xlsx").write_bytes(b"tracked")
        ob.MIRROR = str(t)
        ob.BASELINE = {"raw": 1, "budget-archive": 1}
        ob.STATE = t / "state.json"
        ob.LOCK = t / ".lock"

    def tearDown(self):
        self.tmp.cleanup()

    def run_with(self, bucket, *args):
        ob.credentials = lambda: {}
        ob.r2_client.R2 = lambda creds: bucket
        sys.argv = ["osint-backup.py", *args]
        return ob.main()

    def test_selects_ignored_extensions_only(self):
        self.assertEqual(sorted(ob.local_files()), ["budget-archive/AGO/b.PDF", "raw/2026/a.pdf"])

    def test_sends_missing_and_skips_held(self):
        b = FakeBucket({"raw/2026/a.pdf": (4, "x")})
        self.assertEqual(self.run_with(b, "run", "--quiet"), 0)
        self.assertEqual(b.puts, ["budget-archive/AGO/b.PDF"])

    def test_short_mirror_sends_nothing(self):
        b = FakeBucket({"raw/2026/a.pdf": (4, "x"), "raw/2026/gone.pdf": (1, "y")})
        self.assertEqual(self.run_with(b, "run"), 2)
        self.assertEqual(b.puts, [])

    def test_baseline_floor_when_bucket_empty(self):
        ob.BASELINE = {"raw": 5, "budget-archive": 1}
        b = FakeBucket()
        self.assertEqual(self.run_with(b, "run"), 2)
        self.assertEqual(b.puts, [])

    def test_size_mismatch_not_overwritten_without_replace(self):
        b = FakeBucket({"raw/2026/a.pdf": (999, "x"), "budget-archive/AGO/b.PDF": (2, "z")})
        self.run_with(b, "run", "--quiet")
        self.assertEqual(b.puts, [])
        self.run_with(b, "run", "--quiet", "--replace")
        self.assertEqual(b.puts, ["raw/2026/a.pdf"])

    def test_lock_blocks_second_run(self):
        ob.LOCK.write_text("held")
        b = FakeBucket()
        self.assertEqual(self.run_with(b, "run", "--quiet"), 0)
        self.assertEqual(b.puts, [])


if __name__ == "__main__":
    unittest.main()
