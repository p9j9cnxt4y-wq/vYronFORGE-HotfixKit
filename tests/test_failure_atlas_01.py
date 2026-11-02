import unittest
from vyronforge_failure_atlas.contracts import AtlasRefusal, compare_exact_bytes, verify_guest_completion
class CharacterAndProcessTransportTests(unittest.TestCase):
    def test_binary_identity(self): self.assertEqual(compare_exact_bytes(b'x\ny',b'x\ny')['status'],'PASS')
    def test_lf_to_crlf_fails(self):
        with self.assertRaisesRegex(AtlasRefusal,'BOUNDARY_BYTE_MUTATION'): compare_exact_bytes(b'x\ny',b'x\r\ny')
    def test_backslash_underscore_mutation_fails(self):
        with self.assertRaises(AtlasRefusal): compare_exact_bytes(br'X:\AREA_01',br'X:\AREA\_01')
    def test_true_tab_not_literal_tab(self):
        with self.assertRaises(AtlasRefusal): compare_exact_bytes(b'KEY\tSAFE',br'KEY\tSAFE')
    def test_guest_empty_exit_zero_fails(self):
        with self.assertRaisesRegex(AtlasRefusal,'GUEST_OUTPUT_EMPTY'): verify_guest_completion(b'',exit_code=0,expected_count=1)
    def test_guest_valid_structured(self):
        payload=b'{"records":[{"label":"SYNTHETIC","state":"SAFE"}],"completed":true}'
        self.assertEqual(verify_guest_completion(payload,exit_code=0,expected_count=1)['record_count'],1)
    def test_guest_missing_completed_fails(self):
        with self.assertRaises(AtlasRefusal): verify_guest_completion(b'{"records":[]}',exit_code=0,expected_count=1)
    def test_guest_nonzero_exit_fails(self):
        with self.assertRaisesRegex(AtlasRefusal,'GUEST_NONZERO'): verify_guest_completion(b'{}',exit_code=1,expected_count=1)
    def test_guest_wrong_schema_fails(self):
        with self.assertRaises(AtlasRefusal): verify_guest_completion(b'{"records":[{"label":"x","state":"BAD"}],"completed":true}',exit_code=0,expected_count=1)
