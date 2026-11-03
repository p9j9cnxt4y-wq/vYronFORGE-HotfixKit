"""Mocked PowerShell boundaries; these tests never invoke an OS updater."""
import json,os,shutil,subprocess,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PS=shutil.which('pwsh')

@unittest.skipUnless(os.name=='nt' and PS,'Windows PowerShell host required')
class WindowsAuditContract(unittest.TestCase):
    def run_fixture(self,source,prefix,args=''):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'fixture.ps1'
            target=str(ROOT/source).replace("'","''")
            p.write_text(prefix+"\n& '"+target+"' "+args+"\nexit $LASTEXITCODE\n",encoding='utf-8')
            return subprocess.run([PS,'-NoLogo','-NoProfile','-File',str(p)],capture_output=True,text=True,encoding='utf-8',timeout=20)
    def wua(self,result=2,args='',update_fixture=''):
        prefix=r'''
$global:fakeUpdates=@()
$global:fakeSearcher=[pscustomobject]@{Online=$true}
$global:fakeSearcher | Add-Member ScriptMethod Search {param($query) return [pscustomobject]@{ResultCode=RESULT; Updates=$global:fakeUpdates}}
$global:fakeSession=[pscustomobject]@{}
$global:fakeSession | Add-Member ScriptMethod CreateUpdateSearcher {return $global:fakeSearcher}
function New-Object {param($ComObject) if($ComObject -eq 'Microsoft.Update.Session'){return $global:fakeSession}; if($ComObject -eq 'Microsoft.Update.UpdateColl'){return ,([System.Collections.ArrayList]::new())};throw 'UNEXPECTED_COM_OPERATION'}
'''.replace('RESULT',str(result))
        return self.run_fixture('scripts/windows/patch-security-updates.ps1',prefix+update_fixture,args)
    def fixture_update(self,severity,category):
        return "\n$global:fixtureUpdate=[pscustomobject]@{Title='Mise a jour';MsrcSeverity='"+severity+"';RebootRequired=$false;Categories=@([pscustomobject]@{CategoryID='"+category+"'})}\n$global:fakeUpdates=[pscustomobject]@{Count=1}\n$global:fakeUpdates | Add-Member ScriptMethod Item {param($index) return $global:fixtureUpdate}\n"
    def test_localized_security_update_is_not_missed(self):
        for severity,category in [('Moderate',''),('','0FA1201D-4330-4FA8-8AE9-B877473B6441')]:
            with self.subTest(severity=severity):
                p=self.wua(update_fixture=self.fixture_update(severity,category))
                self.assertEqual(p.returncode,0,p.stderr)
                self.assertEqual(json.loads(p.stdout)['SecurityUpdateCount'],1)
    def test_non_security_update_is_excluded(self):
        p=self.wua(update_fixture=self.fixture_update('',''))
        self.assertEqual(p.returncode,0,p.stderr)
        self.assertEqual(json.loads(p.stdout)['SecurityUpdateCount'],0)
    def test_default_audit_never_goes_online(self):
        p=self.wua(); self.assertEqual(p.returncode,0,p.stderr)
        result=json.loads(p.stdout)
        self.assertFalse(result['Online'])
        self.assertEqual(result['Status'],'AUDIT_OFFLINE_CACHE')
        self.assertIn('NOT_CURRENT_COMPLIANCE',result['Coverage'])
    def test_partial_search_is_not_success(self):
        p=self.wua(3);self.assertEqual(p.returncode,2)
        self.assertEqual(json.loads(p.stdout)['Status'],'UNKNOWN_SEARCH_INCOMPLETE')
    def test_explicit_online_scan_is_distinct(self):
        p=self.wua(args='-OnlineScan');self.assertEqual(p.returncode,0,p.stderr)
        self.assertTrue(json.loads(p.stdout)['Online'])
    def test_no_citrix_is_not_applicable(self):
        p=self.run_fixture('scripts/windows/citrix_vda_health.ps1',"function Get-Service {param($Name,$ErrorAction) return $null}")
        self.assertEqual(p.returncode,0,p.stderr)
        self.assertEqual(json.loads(p.stdout)['Status'],'NOT_APPLICABLE')
    def test_unreadable_event_log_is_not_pass(self):
        prefix="function Get-Service {param($Name,$ErrorAction) return [pscustomobject]@{Status='Running'}}\nfunction Get-WinEvent {param($FilterHashtable,$ErrorAction) throw 'SYNTHETIC_ACCESS_DENIED'}"
        p=self.run_fixture('scripts/windows/citrix_vda_health.ps1',prefix)
        self.assertEqual(p.returncode,3,p.stderr)
        self.assertEqual(json.loads(p.stdout)['Status'],'UNKNOWN')
    def test_unreadable_service_state_is_not_not_applicable(self):
        p=self.run_fixture('scripts/windows/citrix_vda_health.ps1',"function Get-Service {param($Name,$ErrorAction) throw 'SYNTHETIC_SERVICE_ACCESS_DENIED'}")
        self.assertEqual(p.returncode,3,p.stderr)
        self.assertEqual(json.loads(p.stdout)['Status'],'UNKNOWN')
    def test_stopped_broker_is_not_healthy(self):
        prefix="function Get-Service {param($Name,$ErrorAction) if($Name -eq 'BrokerAgent'){return [pscustomobject]@{Status='Stopped'}};return [pscustomobject]@{Status='Running'}}\nfunction Get-WinEvent {param($FilterHashtable,$ErrorAction) return $null}"
        p=self.run_fixture('scripts/windows/citrix_vda_health.ps1',prefix)
        self.assertEqual(p.returncode,2,p.stderr)
        self.assertEqual(json.loads(p.stdout)['Status'],'UNHEALTHY')

if __name__=='__main__':unittest.main()
