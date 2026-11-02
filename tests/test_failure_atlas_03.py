import unittest
from vyronforge_failure_atlas.contracts import AtlasRefusal,check_budget
class MemoryAndProcessTests(unittest.TestCase):
    def test_bounded_ok(self):self.assertIn('WITHIN',check_budget(children=1,max_children=2,ram_mib=32,max_ram_mib=64,elapsed_s=5,timeout_s=10))
    def test_children_exceed(self):
        with self.assertRaisesRegex(AtlasRefusal,'RESOURCE_ENVELOPE'):check_budget(children=8,max_children=2,ram_mib=1,max_ram_mib=64,elapsed_s=1,timeout_s=10)
    def test_memory_exceed(self):
        with self.assertRaises(AtlasRefusal):check_budget(children=1,max_children=2,ram_mib=65,max_ram_mib=64,elapsed_s=1,timeout_s=10)
    def test_timeout_exceed(self):
        with self.assertRaises(AtlasRefusal):check_budget(children=1,max_children=2,ram_mib=1,max_ram_mib=64,elapsed_s=11,timeout_s=10)
    def test_unbounded_rejected(self):
        with self.assertRaisesRegex(AtlasRefusal,'INVALID_RESOURCE'):check_budget(children=1,max_children=0,ram_mib=1,max_ram_mib=64,elapsed_s=1,timeout_s=10)
    def test_negative_budget_rejected(self):
        with self.assertRaises(AtlasRefusal):check_budget(children=-1,max_children=2,ram_mib=1,max_ram_mib=64,elapsed_s=1,timeout_s=10)
