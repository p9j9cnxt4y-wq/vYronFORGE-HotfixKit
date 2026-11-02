"""Offline regression tests for defects found in the previous release candidate.

Only synthetic fixtures under temporary directories. Never runs a patch,
performs remote work, touches installed software or creates many processes.
"""
from __future__ import annotations
import base64,csv,hashlib,importlib.util,io,json,stat,sys,tempfile,unittest,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
sys.path.insert(0,str(ROOT/'tools'))
from vyronforge_hotfix.planner import plan
from vyronforge_hotfix.redact import redact,redact_data
from publication_scan import scan_tree
from verify_wheel import verify_wheel, WheelRefusal

POL=json.loads((ROOT/'policies/critical-2026-09-14.json').read_text())

class VendorBoundaryTests(unittest.TestCase):
    def _states(self,vendor,product='Google Chrome',version='153.0.8010.37'):
        r=plan({'assets':[{'id':'synthetic','vendor':vendor,'product':product,'version':version,'platform':'windows'}]}, POL)
        return r, {f['policy_id']:f['state'] for f in r['findings']}
    def test_shortened_vendor_cannot_pass(self):
        r,states=self._states('Goo')
        self.assertNotIn('GOOGLE-CHROME-SEP2026-KEV',states)
        self.assertEqual(r['terminal_status'],'WARN_UNASSESSED_ASSETS')
    def test_extended_vendor_cannot_pass(self):
        _,states=self._states('GoogleSomethingElse')
        self.assertNotIn('GOOGLE-CHROME-SEP2026-KEV',states)
    def test_exact_declared_vendor_passes(self):
        _,states=self._states('Google')
        self.assertEqual(states['GOOGLE-CHROME-SEP2026-KEV'],'PASS_FIXED')
    def test_casing_and_punctuation_normalization(self):
        _,states=self._states('G-O-O-G-L-E')
        self.assertEqual(states['GOOGLE-CHROME-SEP2026-KEV'],'PASS_FIXED')
    def test_explicit_slash_alias_remains_supported(self):
        r=plan({'assets':[{'id':'test','vendor':'VMware','product':'VMware Workstation','version':'26H1u1'}]},POL)
        self.assertIn('VMWARE-VMSA-2026-0007',{f['policy_id'] for f in r['findings']})
    def test_nested_name_cannot_pass(self):
        _,states=self._states('NotGoogle')
        self.assertNotIn('GOOGLE-CHROME-SEP2026-KEV',states)

class SecretBoundaryTests(unittest.TestCase):
    def test_bearer_free_text(self):
        raw='Authorization' + ': Bearer ' + ('SyntheticValue123'*2)
        red=redact(raw)
        self.assertNotIn('SyntheticValue123',red)
        self.assertIn('[REDACTED_SECRET]',red)
    def test_bearer_equals_syntax(self):
        raw='authorization' + '=Bearer ' + ('Synthetic123'*3)
        self.assertNotIn('Synthetic123',redact(raw))
    def test_basic_and_proxy_auth(self):
        raw='proxy-' + 'authorization' + ': Basic ' + ('EncodedExample'*3)
        self.assertNotIn('EncodedExample',redact(raw))
    def test_refresh_token(self):
        raw='refresh_' + 'token: ' + ('SyntheticSecret'*2)
        self.assertNotIn('SyntheticSecret',redact(raw))
    def test_structured_credential_variants(self):
        keys=['access_token','refresh_token','auth_token','client_secret','x_api_key','cookie','session_id']
        data={x:'PRIVATE_SYNTHETIC_'+x for x in keys}
        scrub=redact_data(data)
        self.assertEqual(set(scrub),set(data))
        self.assertTrue(all(v=='[REDACTED_SECRET]' for v in scrub.values()))
    def test_text_redaction_idempotent(self):
        raw='Authorization' + ': Bearer ' + ('SYNTHETIC123'*3)
        self.assertEqual(redact(redact(raw)),redact(raw))
    def test_publication_scanner_rejects_bearer(self):
        with tempfile.TemporaryDirectory() as td:
            (Path(td)/'synthetic.txt').write_text('Authorization' + ': Bearer ' + ('fakeXYZ123'*4))
            n, errors=scan_tree(Path(td))
            self.assertEqual(n,1)
            self.assertTrue(any('bearer_header' in x for x in errors))
    def test_publication_scanner_accepts_redacted_header(self):
        with tempfile.TemporaryDirectory() as td:
            (Path(td)/'synthetic.txt').write_text(redact('Authorization' + ': Bearer '+('fakeXYZ123'*4)))
            n, errors=scan_tree(Path(td))
            self.assertEqual(n,1)
            self.assertFalse(errors,errors)
    def test_publication_scanner_rejects_symlink(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); (root/'target.txt').write_text('safe')
            from unittest.mock import patch
            (root/'link.txt').write_text('safe synthetic')
            old=Path.is_symlink
            with patch.object(Path,'is_symlink',autospec=True,side_effect=lambda p: p.name=='link.txt'):
                _,errors=scan_tree(root)
            self.assertTrue(any('SYMLINK' in x for x in errors))

class WheelIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        pkg=self.root/'src/vyronforge_hotfix';pkg.mkdir(parents=True)
        (pkg/'__init__.py').write_text('__version__ = "0.4.1rc1"\n')
        (pkg/'cli.py').write_text('def main(): return 0\n')
        self.dinfo='vyronforge_hotfixkit-0.4.1rc1.dist-info'
        self.required={'vyronforge_hotfix/__init__.py','vyronforge_hotfix/cli.py'}
        self.payloads={
            'vyronforge_hotfix/__init__.py':(pkg/'__init__.py').read_bytes(),
            'vyronforge_hotfix/cli.py':(pkg/'cli.py').read_bytes(),
            self.dinfo+'/METADATA':b'Metadata-Version: 2.1\nName: vyronforge-hotfixkit\nVersion: 0.4.1rc1\n'
        }
    def make_wheel(self, *,mutate=None,record_transform=None,extra=None):
        data=dict(self.payloads)
        if mutate: data.update(mutate)
        if extra:data.update(extra)
        rows=[]
        for k,v in data.items():
            h=base64.urlsafe_b64encode(hashlib.sha256(v).digest()).decode().rstrip('=')
            rows.append([k,'sha256='+h,str(len(v))])
        rec=self.dinfo+'/RECORD';rows.append([rec,'',''])
        if record_transform: rows=record_transform(rows)
        out=io.StringIO();csv.writer(out,lineterminator='\n').writerows(rows)
        wheel=self.root/'candidate.whl'
        with zipfile.ZipFile(wheel,'w',zipfile.ZIP_DEFLATED) as z:
            for k,v in data.items():z.writestr(k,v)
            z.writestr(rec,out.getvalue().encode())
        return wheel
    def rejects(self,path,code):
        with self.assertRaisesRegex(WheelRefusal,code):
            verify_wheel(path,self.root,self.required)
    def test_good_wheel_passes(self):
        self.assertEqual(verify_wheel(self.make_wheel(),self.root,self.required),4)
    def test_wheel_missing_record_member(self):
        p=self.make_wheel()
        with zipfile.ZipFile(p) as z: items=[(n,z.read(n)) for n in z.namelist() if not n.endswith('/RECORD')]
        with zipfile.ZipFile(p,'w') as z:
            for n,v in items:z.writestr(n,v)
        self.rejects(p,'RECORD_MISSING')
    def test_record_hash_corruption(self):
        self.rejects(self.make_wheel(record_transform=lambda rows:[[x,'sha256=BAD',z] if i==0 else [x,y,z] for i,(x,y,z) in enumerate(rows)]),'RECORD_CONTENT_MISMATCH')
    def test_record_coverage_missing(self):
        self.rejects(self.make_wheel(record_transform=lambda rows: rows[1:]),'RECORD_COVERAGE')
    def test_record_duplicate_row(self):
        self.rejects(self.make_wheel(record_transform=lambda rows: rows+[rows[0]]),'RECORD_COVERAGE')
    def test_duplicate_archive_member(self):
        p=self.make_wheel()
        with zipfile.ZipFile(p,'a') as z:
            import warnings
            with warnings.catch_warnings():
                warnings.simplefilter('ignore',UserWarning)
                z.writestr('vyronforge_hotfix/cli.py',b'extra')
        self.rejects(p,'DUPLICATE_MEMBER')
    def test_casefold_path_collision(self):
        self.rejects(self.make_wheel(extra={'Vyronforge_hotfix/cli.py':b'malicious'}),'DUPLICATE_MEMBER')
    def test_unsafe_archive_member(self):
        self.rejects(self.make_wheel(extra={'../escape.py':b'x'}),'UNSAFE_MEMBER')
    def test_source_mismatch_with_valid_record(self):
        self.rejects(self.make_wheel(mutate={'vyronforge_hotfix/cli.py':b'def main(): return 4\n'}),'SOURCE_CONTENT_MISMATCH')
    def test_version_mismatch_with_valid_record(self):
        self.rejects(self.make_wheel(mutate={self.dinfo+'/METADATA':b'Version: 9.9.9\n'}),'VERSION_MISMATCH')
    def test_declared_missing_payload(self):
        self.rejects(self.make_wheel(mutate={'vyronforge_hotfix/cli.py':b'def main(): return 1\n'}),'SOURCE_CONTENT_MISMATCH')
    def test_invalid_record_size(self):
        self.rejects(self.make_wheel(record_transform=lambda rows:[[x,y,'500'] if i==0 else [x,y,z] for i,(x,y,z) in enumerate(rows)]),'RECORD_CONTENT_MISMATCH')

if __name__=='__main__':unittest.main()
