import unittest
from datetime import datetime,timezone
from vyronforge_failure_atlas.contracts import AtlasRefusal,readiness_precondition,gate_file_operation
class ReadinessTests(unittest.TestCase):
    def setUp(self):self.r={'status':'FORGE_READY','scope':'alpha','sha256':'a'*64,'expires_at':'2099-01-01T00:00:00Z'}
    def test_reported_readiness_precondition(self):self.assertIn('NOT_EXECUTION',readiness_precondition(self.r,scope='alpha',digest='a'*64,now=datetime(2026,10,24,tzinfo=timezone.utc)))
    def test_wrong_scope_fails(self):
        with self.assertRaises(AtlasRefusal):readiness_precondition(self.r,scope='beta',digest='a'*64)
    def test_wrong_hash_fails(self):
        with self.assertRaises(AtlasRefusal):readiness_precondition(self.r,scope='alpha',digest='b'*64)
    def test_expired_fails(self):
        r=dict(self.r,expires_at='2020-01-01T00:00:00Z')
        with self.assertRaises(AtlasRefusal):readiness_precondition(r,scope='alpha',digest='a'*64)
    def test_extra_fields_fail(self):
        r=dict(self.r,execute=True)
        with self.assertRaises(AtlasRefusal):readiness_precondition(r,scope='alpha',digest='a'*64)
    def test_forge_ready_does_not_allow_deploy(self):self.assertEqual(gate_file_operation(action='DEPLOY',path_safe=True,readiness=True,owner_grant=True),'DENY_MUTATION_NOT_SUPPORTED')
