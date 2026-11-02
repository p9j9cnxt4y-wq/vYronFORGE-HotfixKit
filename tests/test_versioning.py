import sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'src'))
from vyronforge_hotfix.versioning import at_least
class T(unittest.TestCase):
  def test_semver(self):
    self.assertTrue(at_least('3.12.2','3.12.2'))
    self.assertTrue(at_least('3.12.3','3.12.2'))
    self.assertFalse(at_least('3.11.8','3.12.2'))
  def test_vendorish(self):
    self.assertTrue(at_least('26H1u1','26H1u1'))
    self.assertFalse(at_least('25H2','26H1u1'))
if __name__=='__main__': unittest.main()
