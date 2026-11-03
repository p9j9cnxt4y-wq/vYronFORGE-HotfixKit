"""Shell contract tests use stub package tools; they do not patch a host."""
import os,shutil,subprocess,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASH=shutil.which('bash') if os.name!='nt' else str(Path(os.environ.get('ProgramFiles','C:/Program Files'))/'Git/bin/bash.exe')

@unittest.skipUnless(BASH and Path(BASH).is_file(),'Bash runtime unavailable')
class LinuxAuditContract(unittest.TestCase):
    def invoke(self,tool,result):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            stub=root/tool
            stub.write_text('#!/bin/sh\nprintf "STUB_AUDIT_ONLY\\n"\nexit '+str(result)+'\n',encoding='utf-8',newline='\n')
            stub.chmod(0o700)
            # Keep system commands available, but the selected package manager is a fixture.
            script=root/'run.sh'
            script.write_text('set -eu\nexport PATH="$(cd "'+root.as_posix()+'" && pwd):/usr/bin:/bin"\nexec bash "'+(ROOT/'scripts/linux/patch-security-updates.sh').as_posix()+'" --audit\n',encoding='utf-8',newline='\n')
            return subprocess.run([BASH,str(script)],capture_output=True,text=True,timeout=20)
    def test_successful_dnf_audit_returns_success(self):
        p=self.invoke('dnf',0);self.assertEqual(p.returncode,0,p.stderr)
        self.assertIn('STUB_AUDIT_ONLY',p.stdout)
    def test_failed_dnf_audit_propagates_failure(self):
        p=self.invoke('dnf',7);self.assertEqual(p.returncode,7,p.stderr)

if __name__=='__main__':unittest.main()
