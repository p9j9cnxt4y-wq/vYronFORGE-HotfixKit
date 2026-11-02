import unittest
from vyronforge_failure_atlas.contracts import AtlasRefusal,classify_build,classify_evidence
class BuildAndEvidenceTests(unittest.TestCase):
    def test_msb5021_not_source_error(self):self.assertEqual(classify_build(exit_code=1,observed_errors=['MSB5021']),'BLOCKED_CANCELLATION_CAUSE_UNKNOWN')
    def test_failed_without_log_unknown(self):self.assertEqual(classify_build(exit_code=1,observed_errors=[]),'FAILED_NO_ROOT_CAUSE_TELEMETRY')
    def test_success_only_process_exit(self):self.assertEqual(classify_build(exit_code=0,observed_errors=[]),'BUILD_PROCESS_EXIT_ZERO_ONLY')
    def test_scanner_permission_errors_no_pass(self):self.assertEqual(classify_evidence(errors=2947,unknown=0,mandatory_skipped=0,claimed_pass=True),'FAIL_FALSE_PASS_CLAIM')
    def test_skipped_mandatory_no_pass(self):self.assertEqual(classify_evidence(errors=0,unknown=0,mandatory_skipped=1,claimed_pass=False),'WARN_INCOMPLETE')
    def test_unknown_candidate_no_pass(self):self.assertEqual(classify_evidence(errors=0,unknown=1,mandatory_skipped=0,claimed_pass=False),'WARN_INCOMPLETE')
    def test_clean_bounded_pass(self):self.assertEqual(classify_evidence(errors=0,unknown=0,mandatory_skipped=0,claimed_pass=True),'PASS_BOUNDED_EVIDENCE_ONLY')
    def test_negative_counts_fail(self):
        with self.assertRaises(AtlasRefusal):classify_evidence(errors=-1,unknown=0,mandatory_skipped=0,claimed_pass=False)
