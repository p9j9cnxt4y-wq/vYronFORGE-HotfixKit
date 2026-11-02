import importlib.util, unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/'tools'/'codex_path_integrity_regression.py'
spec=importlib.util.spec_from_file_location('cpi',P); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
class T(unittest.TestCase):
  def test_exact(self): self.assertTrue(m.compare(r'Z:\AREA_01',r'Z:\AREA_01')['byte_exact'])
  def test_mutated(self): self.assertFalse(m.compare(r'Z:\AREA_01',r'Z:\AREA\_01')['byte_exact'])
if __name__=='__main__': unittest.main()
