"""Provenance and release-claim consistency checks for the public reference atlas."""
from __future__ import annotations
import json,re,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
INDEX=json.loads((ROOT/'docs/failure-atlas/CASE_INDEX.json').read_text())
REG=json.loads((ROOT/'docs/failure-atlas/FINDINGS_REGISTER_20261029.json').read_text())
UP=json.loads((ROOT/'docs/failure-atlas/UPSTREAM_STATUS_20261029.json').read_text())
class RegisterTests(unittest.TestCase):
    def test_register_count_and_unique_ids(self):
        a=REG['findings'];self.assertEqual(REG['finding_count'],len(a));self.assertEqual(len(a),len({x['id'] for x in a}))
    def test_registered_topic_count_matches_casepacks(self):
        expected={t['id'] for t in INDEX['topics']}
        self.assertEqual(len(expected),11)
        self.assertEqual({x['topic_id'] for x in REG['findings']},expected)
        self.assertEqual(REG['topics'],len(expected))
    def test_each_category_is_covered(self):
        for x in REG['findings']:
            self.assertRegex(x['id'],r'^\d\d-[a-z0-9_]+$')
            self.assertTrue(x['statement'] and x['proposed_mitigation'])
    def test_no_vendor_binary_fix_claim(self):
        self.assertTrue(all(x['vendor_binary_fixed'] is False for x in REG['findings']))
    def test_no_false_root_cause_proof(self):
        self.assertTrue(all(x['authoritative_root_cause_proven'] is False for x in REG['findings']))
    def test_implemented_means_local_reference_only(self):
        allowed={'REFERENCE_IMPLEMENTED','REFERENCE_ONLY','FIXED_IN_LOCAL_CANDIDATE','PROPOSED_ONLY','DOCUMENT_ONLY','NOT_IMPLEMENTED'}
        self.assertTrue(all(x['fix_status'] in allowed for x in REG['findings']))
    def test_upstream_links_checked_and_in_repo(self):
        known={x['number'] for x in UP['issues']}
        self.assertTrue(all(set(x['upstream_issues'])<=known for x in REG['findings']))
        self.assertTrue(all(x['url'].startswith('https://github.com/openai/codex/issues/') for x in UP['issues']))
    def test_upstream_not_misreported_closed(self):
        self.assertTrue(all(x['state'] in ('open','closed') for x in UP['issues']))
        self.assertEqual(UP['retrieval_date'],'2026-10-29')
    def test_product_runtime_not_attested(self):
        self.assertEqual(REG['boundary']['fpp_actual_host'],'NOT_RUN')
        self.assertEqual(REG['boundary']['windows_remote_ci'],'NOT_RUN')
        self.assertEqual(REG['boundary']['github_publication'],'NOT_DONE')
    def test_casepack_publication_not_claimed(self):
        for p in (ROOT/'packages/failure-atlas').glob('*/cases.json'):
            x=json.loads(p.read_text());self.assertEqual(x['publication_status'],'NOT_PUBLISHED')
            self.assertNotIn('published_as_of',x)
    def test_pyproject_module_and_docs_same_release(self):
        p=(ROOT/'pyproject.toml').read_text();v=(ROOT/'src/vyronforge_hotfix/__init__.py').read_text()
        self.assertIn('version = "0.4.1"',p);self.assertIn('0.4.1',v)
        self.assertEqual(INDEX['repository_candidate'],'v0.4.1-rc1')
        self.assertIn('0.4.1-rc1',(ROOT/'README.md').read_text())
    def test_no_duplicate_top_level_changelog_title(self):
        self.assertEqual((ROOT/'CHANGELOG.md').read_text().count('# Changelog'),1)
if __name__=='__main__': unittest.main()
