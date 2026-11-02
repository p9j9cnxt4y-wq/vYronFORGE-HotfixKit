import unittest
from vyronforge_failure_atlas.contracts import publication_gate
class PublicationTests(unittest.TestCase):
    def test_no_owner_denies(self):self.assertEqual(publication_gate(unit_tests=True,native_windows_ci=True,redacted=True,license_reviewed=True,owner_approved=False),'NO_PUBLICATION_AUTHORITY')
    def test_no_windows_ci_denies(self):self.assertEqual(publication_gate(unit_tests=True,native_windows_ci=False,redacted=True,license_reviewed=True,owner_approved=True),'NO_PUBLICATION_AUTHORITY')
    def test_no_redaction_denies(self):self.assertEqual(publication_gate(unit_tests=True,native_windows_ci=True,redacted=False,license_reviewed=True,owner_approved=True),'NO_PUBLICATION_AUTHORITY')
    def test_no_license_review_denies(self):self.assertEqual(publication_gate(unit_tests=True,native_windows_ci=True,redacted=True,license_reviewed=False,owner_approved=True),'NO_PUBLICATION_AUTHORITY')
    def test_all_gates_not_automatic_push(self):self.assertEqual(publication_gate(unit_tests=True,native_windows_ci=True,redacted=True,license_reviewed=True,owner_approved=True),'PUBLISH_PREREQUISITES_REPORTED_REQUIRES_AUTHORIZED_PUBLISHER')
