"""Regression: Git checkout must preserve immutable source-manifest bytes."""
from pathlib import Path
import os
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
GIT = shutil.which("git")

@unittest.skipUnless(GIT, "Git executable is required for checkout regression")
class CheckoutByteIntegrityTests(unittest.TestCase):
    def checkout(self, use_attributes):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "repo"
            root.mkdir()
            out = Path(td) / "out"
            out.mkdir()
            env = dict(os.environ, GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull)
            for key in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE"):
                env.pop(key, None)
            def git(*args):
                result = subprocess.run(
                    [GIT, "-C", str(root), "-c", "core.autocrlf=true", *args],
                    env=env, capture_output=True, timeout=30)
                self.assertEqual(result.returncode, 0, "Git checkout fixture failed")
            git("init", "--quiet")
            payload = {"lf.txt": b"first\nsecond\n",
                       "crlf.txt": b"first\r\nsecond\r\n"}
            for name, data in payload.items():
                (root / name).write_bytes(data)
            if use_attributes:
                (root / ".gitattributes").write_bytes(
                    (ROOT / ".gitattributes").read_bytes())
            git("-c", "core.autocrlf=false", "add", "--all")
            git("checkout-index", "--all", "--prefix=" + out.as_posix() + "/")
            return payload, {name: (out / name).read_bytes() for name in payload}

    def test_attributes_preserve_lf_and_crlf_bytes(self):
        expected, actual = self.checkout(True)
        self.assertEqual(actual, expected)

    def test_without_attributes_windows_checkout_changes_lf(self):
        expected, actual = self.checkout(False)
        self.assertNotEqual(actual["lf.txt"], expected["lf.txt"])
        self.assertEqual(actual["lf.txt"], expected["lf.txt"].replace(b"\n", b"\r\n"))
