"""Current advisory boundaries; fixtures do not contact or patch vendor products."""
import hashlib,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from vyronforge_hotfix.planner import plan
POL=json.loads((ROOT/'policies/critical-2026-11-02.json').read_text('utf-8'))
ITEMS={x['id']:x for x in POL['items']}

def state(pid,version,**extra):
    item=ITEMS[pid]
    a={'id':'fixture','vendor':item['vendor'].split('/')[0],'product':item['products'][0],'version':version,**extra}
    return plan({'assets':[a]},{'items':[item]})['findings'][0]['state']

class CurrentPolicy(unittest.TestCase):
    def test_historical_bytes_and_current_bundle(self):
        old=(ROOT/'policies/critical-2026-09-14.json').read_bytes()
        self.assertEqual(hashlib.sha256(old).hexdigest(),POL['historical_snapshot_sha256'])
        self.assertEqual(old,(ROOT/'src/vyronforge_hotfix/data/critical-2026-09-14.json').read_bytes())
        self.assertEqual((ROOT/'policies/critical-2026-11-02.json').read_bytes(),(ROOT/'src/vyronforge_hotfix/data/critical-2026-11-02.json').read_bytes())
    def test_mikrotik_incomplete_fix_not_accepted(self):
        for v in ('7.24.2','7.23.5'):
            self.assertEqual(state('MIKROTIK-MIKROTRICK-SEP2026',v),'DENY_VULNERABLE')
        for v in ('7.24.3','7.23.6','6.49.21'):
            self.assertEqual(state('MIKROTIK-MIKROTRICK-SEP2026',v),'PASS_FIXED')
    def test_gitea_edition_is_required(self):
        pid='GITEA-CVE-2026-60004'
        self.assertEqual(state(pid,'27.2.0'),'REQUIRES_VENDOR_VERIFY')
        self.assertEqual(state(pid,'27.2.0',edition='enterprise'),'DENY_VULNERABLE')
        self.assertEqual(state(pid,'27.3.0',edition='enterprise'),'PASS_FIXED')
        self.assertEqual(state(pid,'1.27.1',edition='community'),'PASS_FIXED')
        self.assertEqual(state(pid,'1.27.0',edition='community'),'DENY_VULNERABLE')
    def test_screenconnect_server_does_not_prove_clients(self):
        pid='CONNECTWISE-SCREENCONNECT-CVE-2026-84869'
        for component in ('','server','cloud'):
            self.assertEqual(state(pid,'26.6.5',component=component),'REQUIRES_VENDOR_VERIFY')
        self.assertEqual(state(pid,'26.6.4',component='client'),'DENY_VULNERABLE')
        self.assertEqual(state(pid,'26.6.5',component='client'),'PASS_FIXED')
    def test_mlflow_followup_baseline(self):
        self.assertEqual(state('MLFLOW-CVE-2026-64849','3.15.0'),'DENY_VULNERABLE')
        self.assertEqual(state('MLFLOW-CVE-2026-64849','3.16.0'),'PASS_FIXED')
    def test_sonicwall_october_baseline(self):
        pid='SONICWALL-SMA1000-SEP2026'
        self.assertEqual(state(pid,'12.4.3-03526'),'DENY_VULNERABLE')
        self.assertEqual(state(pid,'12.4.3-03670'),'PASS_FIXED')
        self.assertEqual(state(pid,'12.5.0-03082'),'PASS_FIXED')
    def test_gitlab_backports(self):
        pid='GITLAB-CVE-2026-85706'
        self.assertEqual(state(pid,'18.11.11'),'DENY_VULNERABLE')
        self.assertEqual(state(pid,'18.11.12'),'PASS_FIXED')
        self.assertEqual(state(pid,'19.0.9'),'PASS_FIXED')
        self.assertEqual(state(pid,'19.00.9'),'REQUIRES_VENDOR_VERIFY')
    def test_chrome_platform_gate_and_current_baseline(self):
        pid='GOOGLE-CHROME-SEP2026-KEV'
        self.assertEqual(state(pid,'156.0.8078.79'),'REQUIRES_VENDOR_VERIFY')
        for platform in ('windows','linux','macos'):
            self.assertEqual(state(pid,'153.0.8010.37',platform=platform),'DENY_VULNERABLE')
            self.assertEqual(state(pid,'156.0.8078.79',platform=platform),'PASS_FIXED')
    def test_every_unverified_item_fails_closed(self):
        unknown=[i for i in POL['items'] if i['verification_status']=='UNKNOWN']
        self.assertTrue(unknown)
        for item in unknown:
            self.assertEqual(state(item['id'],'999.999.999'),'REQUIRES_VENDOR_VERIFY')

if __name__=='__main__':unittest.main()
