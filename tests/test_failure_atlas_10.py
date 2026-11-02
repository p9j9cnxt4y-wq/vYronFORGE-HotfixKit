import unittest
from vyronforge_failure_atlas.contracts import AtlasRefusal,label_source,check_candidate_coverage
class ArchiveAndSourceTests(unittest.TestCase):
    def test_name_hits_not_source(self):self.assertEqual(label_source(path_hits=3123,manifest_bindings=0,source_bytes_read=False),'PATH_HINTS_ONLY_SOURCE_AUTHORITY_UNKNOWN')
    def test_manifest_unread_not_authority(self):self.assertEqual(label_source(path_hits=100,manifest_bindings=1,source_bytes_read=False),'SOURCE_NOT_CONTENT_VERIFIED')
    def test_read_not_current(self):self.assertEqual(label_source(path_hits=1,manifest_bindings=1,source_bytes_read=True),'CONTENT_READ_NOT_CURRENT_AUTHORITY')
    def test_negative_inventory(self):
        with self.assertRaises(AtlasRefusal):label_source(path_hits=-1,manifest_bindings=0,source_bytes_read=False)
    def test_incomplete_coverage_not_pass(self):self.assertEqual(check_candidate_coverage(covered=3,relevant=200),'WARN_PARTIAL_DISCOVERY')
