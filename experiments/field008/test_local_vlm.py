import unittest,tempfile,json,sys
from pathlib import Path
from local_vlm import checked_endpoint,request_payload,perceive_local
class LocalVisionTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.image=Path(self.temp.name)/'x.png'
        self.image.write_bytes(b'\x89PNG\r\n\x1a\n'+b'x'*10)
    def tearDown(self):self.temp.cleanup()
    def test_default_refuses_transfer(self):
        with self.assertRaises(PermissionError):perceive_local('s',self.image)
    def test_remote_refuses(self):
        for x in ['https://api.example.com/api/chat','http://10.0.0.7:11434/api/chat',
                  'http://localhost:8844/api/chat','http://localhost:11434/other',
                  'http://localhost:11434/api/chat?secret=1']:
            with self.assertRaises(ValueError):checked_endpoint(x)
    def test_local_mock_invocation(self):
        calls=[]
        def fake(url,data):
            calls.append((url,json.loads(data)))
            return json.dumps({'model':'qwen3-vl:2b-instruct','done':True,'eval_count':10,
                  'message':{'content':json.dumps({'source_id':'sketch','claims':[]})}}).encode()
        r=perceive_local('sketch',self.image,explicit_local_model=True,transport=fake)
        self.assertEqual(len(calls),1)
        self.assertEqual(r['packet']['source_id'],'sketch')
        self.assertEqual(calls[0][0],'http://127.0.0.1:11434/api/chat')
    def test_packet_includes_image_only_to_local(self):
        p=request_payload('sketch',self.image)
        self.assertIn('images',p['messages'][0]);self.assertEqual(p['format'],'json')
    def test_reject_unsupported_data(self):
        self.image.write_bytes(b'not really an image')
        with self.assertRaises(ValueError):request_payload('sketch',self.image)
    def test_invalid_response_holds(self):
        def fake(url,data):return json.dumps({'message':{'content':'not JSON'}}).encode()
        with self.assertRaises(ValueError):perceive_local('sketch',self.image,explicit_local_model=True,transport=fake)
    def test_mismatched_source_holds(self):
        def fake(url,data):return json.dumps({'message':{'content':'{"source_id":"other","claims":[]}'}}).encode()
        with self.assertRaises(ValueError):perceive_local('sketch',self.image,explicit_local_model=True,transport=fake)
if __name__=='__main__':unittest.main()
