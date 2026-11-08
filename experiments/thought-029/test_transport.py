"""HTTP simulation tests; explicitly not actual model inference."""
import json,threading,unittest
from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
from artifact_portal import ArtifactPortal
from interpreter import trial
from direct_artifact_llm import DirectArtifactLLM
from specimens import BY_KEY
from pathlib import Path

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.write({'models':[{'name':'mock:3b','digest':'a'*64}]})
    def do_POST(self):
        body=json.loads(self.rfile.read(int(self.headers['Content-Length'])))
        self.server.queries.append(body)
        item=self.server.answers.pop(0)
        self.write({'model':'mock:3b','done':True,'response':json.dumps(item),
                    'prompt_eval_count':120,'eval_count':40})
    def write(self,obj):
        raw=json.dumps(obj).encode();self.send_response(200)
        self.send_header('Content-Type','application/json')
        self.send_header('Content-Length',str(len(raw)))
        self.end_headers();self.wfile.write(raw)
    def log_message(self,*a):pass

class TransportTests(unittest.TestCase):
    def test_direct_http_model_can_browse_read_and_form_recheckable_interpretation(self):
        server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
        server.queries=[]
        server.answers=[
            {'action':'graphs'},
            {'action':'read','artifact_id':'experiments/thought-027/proof_memory.py'},
            {'action':'final','bindings':{'current':'register_g','event':'register_f'},
             'relation':'DIFFERENCE',
             'evidence_ids':['experiments/thought-027/proof_memory.py'],
             'rationale':'Read-only proof reference helps suggest a difference candidate'},
        ]
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        try:
            class Loopback(DirectArtifactLLM):
                TAGS=f'http://127.0.0.1:{server.server_port}/api/tags'
                GENERATE=f'http://127.0.0.1:{server.server_port}/api/generate'
            model=Loopback('mock:3b')
            portal=ArtifactPortal(Path(__file__).resolve().parents[2])
            out=trial(BY_KEY['food_recalled_elsewhere'],portal,model,max_steps=4)
            self.assertEqual(out['status'],'REVIEW_SCOPED_INTERPRETATION_NOT_INSTALLED')
            self.assertEqual(out['actual_model_call_count'],3)
            self.assertEqual(out['read_only_tool_calls'],2)
            self.assertEqual(out['frozen']['correct'],64)
            self.assertEqual(len(server.queries),3)
            self.assertNotIn('policy',server.queries[0]['prompt'].split('TASK_JSON=')[-1].split('CATALOG=')[0])
            self.assertTrue(all(c['actual_inference_completed'] for c in model.calls))
            self.assertFalse(out['installed'])
            # Stub HTTP round-trip is NEVER a claim that a pretrained LLM ran.
        finally:
            server.shutdown();server.server_close();thread.join(timeout=3)

if __name__=='__main__':unittest.main()
