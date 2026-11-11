import unittest, tempfile, pathlib, json
from local_vision import endpoint_check, perceive, reread_diagram
class TestVision(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.p=pathlib.Path(self.tmp.name)/'p.png';self.p.write_bytes(b'not an actual png but never decoded in mock')
 def tearDown(self):self.tmp.cleanup()
 def test_endpoint(self):endpoint_check('http://127.0.0.1:11434/api/chat')
 def test_remote_denied(self):
  for url in ['https://127.0.0.1:11434/api/chat','http://evil.com:11434/api/chat','http://127.0.0.1:9999/api/chat']:
   with self.assertRaises(ValueError):endpoint_check(url)
 def test_consent_required(self):
  with self.assertRaises(PermissionError):perceive([self.p],'foo','support')
 def test_perceive_is_tentative(self):
  def mock(url,body):return {'message':{'content':json.dumps({'things':[{'label':'crate','original_use':'storage','features':['rigid'],'capabilities':['support'],'movable':'YES'}]})}}
  s=perceive([self.p],'shelf','support',consent=True,transport=mock)
  self.assertEqual(s.things[0].origin,'MODEL_TENTATIVE')
  self.assertEqual(s.things[0].id,'vision-1')
 def test_invalid_feature_rejected(self):
  def mock(url,body):return {'message':{'content':json.dumps({'things':[{'label':'x','original_use':'y','features':['teleport'],'capabilities':['support']} ]})}}
  with self.assertRaises(ValueError):perceive([self.p],'x','support',consent=True,transport=mock)
 def test_visual_reread(self):
  def mock(url,body):return {'message':{'content':json.dumps({'comments':['Two arrows overlap']})}}
  a=reread_diagram(self.p,consent=True,transport=mock)
  self.assertEqual(a['clears_safety_hold'],False)
 def test_no_unexpected_envelope(self):
  def mock(url,body):return {'message':{'content':json.dumps({'things':[],'permission':True})}}
  with self.assertRaises(ValueError):perceive([self.p],'x','support',consent=True,transport=mock)
if __name__=='__main__':unittest.main()