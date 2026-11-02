import json, sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'src'))
from vyronforge_hotfix.redact import redact, redact_data

class T(unittest.TestCase):
  def test_ip_secret(self):
    ip='192'+'.0.2.20'; mac='02'+':00'*5
    key='to'+'ken'; value='abc'+'123'
    s=redact(f'ip={ip} {key}={value} {mac}')
    self.assertNotIn(ip,s); self.assertNotIn(value,s); self.assertNotIn(mac,s)
  def test_unassessed_asset_array_is_redacted(self):
    x=redact_data({'unassessed_assets':['internal-edge-01','db-private-02'],'findings':[{'asset_id':'node-1'}]})
    self.assertEqual(x['unassessed_assets'],['[REDACTED_IDENTIFIER]','[REDACTED_IDENTIFIER]'])
    self.assertEqual(x['findings'][0]['asset_id'],'[REDACTED_IDENTIFIER]')
  def test_json_secret_and_asset(self):
    email='a'+'@example.test'; key='api_'+'key'; value='super'+'secret'
    payload=json.dumps({'asset_id':'prod-host-01',key:value,'email':email})
    s=redact(payload)
    self.assertNotIn('prod-host-01',s); self.assertNotIn(value,s); self.assertNotIn(email,s)
    self.assertIn('[REDACTED_IDENTIFIER]',s); self.assertIn('[REDACTED_SECRET]',s)
if __name__=='__main__': unittest.main()
