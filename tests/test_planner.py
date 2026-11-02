import json, sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'src'))
from vyronforge_hotfix.planner import plan
ROOT=Path(__file__).resolve().parents[1]
POL=json.loads((ROOT/'policies/critical-2026-09-14.json').read_text())
class T(unittest.TestCase):
  def test_bundled_policy_matches_repository_policy(self):
    bundled=ROOT/'src'/'vyronforge_hotfix'/'data'/'critical-2026-09-14.json'
    self.assertEqual(bundled.read_bytes(),(ROOT/'policies/critical-2026-09-14.json').read_bytes())
  def test_vm2_denied(self):
    r=plan({'assets':[{'id':'x','vendor':'vm2','product':'vm2','version':'3.11.6'}]}, POL)
    self.assertEqual(r['findings'][0]['state'],'DENY_VULNERABLE')
    self.assertEqual(r['terminal_status'],'WARN_REMEDIATION_REQUIRED')
  def test_vm2_fixed(self):
    r=plan({'assets':[{'id':'x','vendor':'vm2','product':'vm2','version':'3.12.2'}]}, POL)
    self.assertEqual(r['findings'][0]['state'],'PASS_FIXED')
    self.assertEqual(r['terminal_status'],'PASS_FIXED')
  def test_vendor_verify_not_false_pass(self):
    r=plan({'assets':[{'id':'x','vendor':'Cisco','product':'Nexus 9000 Silicon One','version':'unknown'}]}, POL)
    self.assertEqual(r['findings'][0]['state'],'REQUIRES_VENDOR_VERIFY')
    self.assertEqual(r['terminal_status'],'WARN_VENDOR_VERIFICATION_REQUIRED')
  def test_unmatched_asset_not_false_pass(self):
    r=plan({'assets':[{'id':'x','vendor':'Unknown','product':'Unknown Product','version':'1.0'}]}, POL)
    self.assertEqual(r['unassessed_assets'],['x'])
    self.assertEqual(r['terminal_status'],'WARN_UNASSESSED_ASSETS')
  def test_product_name_does_not_cross_vendor_boundary(self):
    r=plan({'assets':[{'id':'x','vendor':'Fortinet','product':'FortiPAM Chrome Extension','version':'8.0'}]},POL)
    ids={f['policy_id'] for f in r['findings']}
    self.assertNotIn('GOOGLE-CHROME-SEP2026-KEV',ids)
  def test_missing_vendor_is_unassessed_fail_closed(self):
    r=plan({'assets':[{'id':'x','product':'Google Chrome','version':'153.0.8010.37'}]},POL)
    self.assertEqual(r['findings'],[])
    self.assertEqual(r['terminal_status'],'WARN_UNASSESSED_ASSETS')
  def test_vendor_alias_vmware_matches(self):
    r=plan({'assets':[{'id':'x','vendor':'VMware','product':'VMware Workstation','version':'26H1u1'}]},POL)
    hit=[f for f in r['findings'] if f['policy_id']=='VMWARE-VMSA-2026-0007']
    self.assertEqual(hit[0]['state'],'PASS_FIXED')
  def test_nable_minimum(self):
    bad=plan({'assets':[{'id':'x','vendor':'N-able','product':'N-central','version':'2026.3.1.13'}]},POL)
    good=plan({'assets':[{'id':'x','vendor':'N-able','product':'N-central','version':'2026.3.1.14'}]},POL)
    self.assertEqual(bad['findings'][0]['state'],'DENY_VULNERABLE')
    self.assertEqual(good['findings'][0]['state'],'PASS_FIXED')
  def test_jfrog_branch_gate(self):
    bad=plan({'assets':[{'id':'x','vendor':'JFrog','product':'Artifactory','version':'7.161.19'}]},POL)
    good=plan({'assets':[{'id':'x','vendor':'JFrog','product':'Artifactory','version':'7.161.20'}]},POL)
    self.assertEqual(bad['findings'][0]['state'],'DENY_VULNERABLE')
    self.assertEqual(good['findings'][0]['state'],'PASS_FIXED')
  def test_empty_inventory_not_pass(self):
    r=plan({'assets':[]},POL)
    self.assertEqual(r['terminal_status'],'WARN_EMPTY_INVENTORY')
  def test_declared_minimums_pass_exactly(self):
    for item in POL['items']:
      minimum=item.get('minimum_fixed_version') or item.get('minimum_operational_baseline')
      if not minimum: continue
      asset={'id':'x','vendor':item['vendor'],'product':item['products'][0],'version':minimum}
      r=plan({'assets':[asset]},POL)
      hit=[f for f in r['findings'] if f['policy_id']==item['id']]
      self.assertTrue(hit, item['id'])
      self.assertEqual(hit[0]['state'],'PASS_FIXED',item['id'])
  def test_declared_branch_fixed_versions_pass_exactly(self):
    for item in POL['items']:
      if not item.get('auto_compare_fixed_versions'): continue
      for branch, minimum in item.get('fixed_versions',{}).items():
        asset={'id':'x','vendor':item['vendor'],'product':item['products'][0],'version':minimum}
        r=plan({'assets':[asset]},POL)
        hit=[f for f in r['findings'] if f['policy_id']==item['id']]
        self.assertTrue(hit,(item['id'],branch))
        self.assertEqual(hit[0]['state'],'PASS_FIXED',(item['id'],branch,minimum,hit[0]))
class PlatformAndCoverageT(unittest.TestCase):
  def test_chrome_platform_specific_fixed_builds(self):
    cases=[
      ('windows','153.0.8010.35','DENY_VULNERABLE'),
      ('windows','153.0.8010.36','DENY_VULNERABLE'),
      ('windows','153.0.8010.37','PASS_FIXED'),
      ('linux','153.0.8010.36','PASS_FIXED'),
      ('macos','153.0.8010.36','DENY_VULNERABLE'),
      ('macos','153.0.8010.37','PASS_FIXED'),
    ]
    for platform,version,state in cases:
      r=plan({'assets':[{'id':'x','vendor':'Google','product':'Google Chrome','version':version,'platform':platform}]},POL)
      hit=[f for f in r['findings'] if f['policy_id']=='GOOGLE-CHROME-SEP2026-KEV'][0]
      self.assertEqual(hit['state'],state,(platform,version,hit))
  def test_chrome_missing_platform_fails_closed(self):
    r=plan({'assets':[{'id':'x','vendor':'Google','product':'Google Chrome','version':'153.0.8010.37'}]},POL)
    hit=[f for f in r['findings'] if f['policy_id']=='GOOGLE-CHROME-SEP2026-KEV'][0]
    self.assertEqual(hit['state'],'REQUIRES_VENDOR_VERIFY')
    self.assertEqual(r['terminal_status'],'WARN_VENDOR_VERIFICATION_REQUIRED')
  def test_cert_eu_2026_advisories_all_mapped(self):
    coverage=POL.get('cert_eu_2026_advisory_coverage',{})
    self.assertEqual(set(coverage),{f'2026-{i:03d}' for i in range(1,13)})
    ids={x['id'] for x in POL['items']}
    for adv,pids in coverage.items():
      self.assertTrue(pids,adv)
      self.assertTrue(set(pids)<=ids,(adv,pids))

  def test_screenconnect_kev_fixed_boundary(self):
    bad=plan({'assets':[{'id':'x','vendor':'ConnectWise','product':'ScreenConnect','version':'26.6.4'}]},POL)
    good=plan({'assets':[{'id':'x','vendor':'ConnectWise','product':'ScreenConnect','version':'26.6.5'}]},POL)
    bh=[f for f in bad['findings'] if f['policy_id']=='CONNECTWISE-SCREENCONNECT-CVE-2026-84869'][0]
    gh=[f for f in good['findings'] if f['policy_id']=='CONNECTWISE-SCREENCONNECT-CVE-2026-84869'][0]
    self.assertEqual(bh['state'],'DENY_VULNERABLE')
    self.assertEqual(gh['state'],'PASS_FIXED')

if __name__=='__main__': unittest.main()
