import unittest
from vyronforge_failure_atlas.contracts import AtlasRefusal,validate_systemd_metadata,correlate_label,check_candidate_coverage
class RemoteMetadataTests(unittest.TestCase):
    def setUp(self):self.r={'opaque_ref':'a'*32,'unit_type':'service','active':True,'pid':1,'runtime_class':'dotnet'}
    def test_minimal_safe(self):self.assertEqual(validate_systemd_metadata(self.r),'PASS_MINIMAL_METADATA_SCHEMA_ONLY')
    def test_unsafe_extra_arguments_rejected(self):
        with self.assertRaises(AtlasRefusal):validate_systemd_metadata(dict(self.r,argv='not allowed'))
    def test_nonopaque_unit_name_rejected(self):
        with self.assertRaises(AtlasRefusal):validate_systemd_metadata(dict(self.r,opaque_ref='public-unit-name'))
    def test_correlate_same_run(self):self.assertEqual(correlate_label('sample',run_key=b'X'*32),correlate_label('sample',run_key=b'X'*32))
    def test_correlate_different_runs(self):self.assertNotEqual(correlate_label('sample',run_key=b'X'*32),correlate_label('sample',run_key=b'Y'*32))
    def test_coverage_partial(self):self.assertEqual(check_candidate_coverage(covered=8,relevant=9),'WARN_PARTIAL_DISCOVERY')
    def test_coverage_complete(self):self.assertIn('PASS_BOUNDED',check_candidate_coverage(covered=8,relevant=8))
