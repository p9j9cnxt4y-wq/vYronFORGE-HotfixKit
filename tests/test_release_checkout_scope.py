"""Regression: repository checkout metadata is not release payload."""
from __future__ import annotations
import json, os, shutil, subprocess, sys, tempfile, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class CheckoutScopeTests(unittest.TestCase):
    def probe(self, extra_manifest_path=None):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / 'source'
            shutil.copytree(ROOT, root, ignore=shutil.ignore_patterns(
                '.git', '__pycache__', '.venv', 'build', 'dist', '*.egg-info'))
            (root / '.git').mkdir()
            (root / '.git' / 'HEAD').write_text(
                'ref: refs/heads/main\n', encoding='utf-8')
            if extra_manifest_path is not None:
                with (root / 'evidence' / 'SHA256SUMS.txt').open(
                        'a', encoding='utf-8', newline='\n') as output:
                    output.write('0' * 64 + '  ' + extra_manifest_path + '\n')
            env = dict(os.environ, PYTHONUTF8='1', PYTHONDONTWRITEBYTECODE='1')
            result = subprocess.run(
                [sys.executable, '-B', 'tools/release_gate_20.py'],
                cwd=root, env=env, capture_output=True, timeout=30)
            return result.returncode, json.loads(result.stdout)

    def test_clean_checkout_metadata_is_allowed(self):
        code, result = self.probe()
        self.assertEqual(code, 0)
        self.assertEqual(result['passed'], result['total'])

    def test_git_metadata_in_release_manifest_is_rejected(self):
        code, result = self.probe('.git/HEAD')
        self.assertEqual(code, 2)
        failures = [x['name'] for x in result['checks'] if x['status'] == 'FAIL']
        self.assertEqual(failures, ['27-no-Git-metadata-in-release-manifest'])

    def test_nested_casefold_git_metadata_is_rejected(self):
        code, result = self.probe('nested/.GIT/config')
        self.assertEqual(code, 2)
        self.assertEqual([x['name'] for x in result['checks']
                          if x['status'] == 'FAIL'],
                         ['27-no-Git-metadata-in-release-manifest'])

