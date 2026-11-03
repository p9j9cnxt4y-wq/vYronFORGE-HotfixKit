"""Regression checks for unsafe RC planner acceptance, using synthetic inputs."""
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from vyronforge_hotfix.planner import plan
from vyronforge_hotfix.versioning import at_least

ITEM={'id':'TEST','vendor':'Example','products':['Widget'],'severity':'HIGH','minimum_fixed_version':'3.12.2','action':'Verify vendor fix.','verify':'Check exact version.','sources':['https://example.com/advisory']}
def asset(version='3.12.2',**changes):
    value={'id':'fixture','vendor':'Example','product':'Widget','version':version}
    value.update(changes)
    return value

class StableFailClosed(unittest.TestCase):
    def test_unknown_versions_never_pass(self):
        for version in ['unknown','latest','3.12.2-rc1','garbage999','3.12.2+unverified']:
            with self.subTest(version=version):
                self.assertFalse(at_least(version,'3.12.2'))
                report=plan({'assets':[asset(version)]},{'items':[ITEM]})
                self.assertEqual(report['findings'][0]['state'],'DENY_UNKNOWN')
    def test_duplicate_asset_ids_cannot_hide_unassessed(self):
        report=plan({'assets':[asset(),asset(vendor='Other')]},{'items':[ITEM]})
        self.assertEqual(report['terminal_status'],'WARN_UNASSESSED_ASSETS')
        self.assertEqual(report['unassessed_assets'],['fixture'])
    def test_missing_ids_cannot_hide_unassessed(self):
        first=asset();second=asset(vendor='Other');first.pop('id');second.pop('id')
        report=plan({'assets':[first,second]},{'items':[ITEM]})
        self.assertEqual(report['terminal_status'],'WARN_UNASSESSED_ASSETS')
    def test_branch_prefix_requires_component_boundary(self):
        item=dict(ITEM);item.pop('minimum_fixed_version')
        item.update(auto_compare_fixed_versions=True,fixed_versions={'7.24':'7.24.3'})
        report=plan({'assets':[asset('7.240.99')]},{'items':[item]})
        self.assertEqual(report['findings'][0]['state'],'REQUIRES_VENDOR_VERIFY')
    def test_unverified_advisory_cannot_pass(self):
        item=dict(ITEM,verification_status='UNKNOWN')
        report=plan({'assets':[asset()]},{'items':[item]})
        self.assertEqual(report['findings'][0]['state'],'REQUIRES_VENDOR_VERIFY')
    def test_cross_format_version_is_not_comparable(self):
        self.assertFalse(at_least('26H1u1','3.12.2'))
        self.assertFalse(at_least('3.12.2-1','3.12.2'))
        self.assertNotEqual(plan({'assets':[asset('3.12.2-1')]},{'items':[ITEM]})['terminal_status'],'PASS_FIXED')
    def test_vendor_build_and_numeric_versions_preserved(self):
        self.assertTrue(at_least('12.4.3-03526','12.4.3-03526'))
        self.assertTrue(at_least('26H1u1','25H2'))
        self.assertFalse(at_least('26H1','26H1u1'))

if __name__=='__main__':unittest.main()
