"""HTTP-format fixture, NOT a generative LLM. Validates read/word/final transport."""
from __future__ import annotations
import sys,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent
for d in ('thought-019','thought-025','thought-029'):
    p=str(HERE.parent/d)
    if p not in sys.path:sys.path.insert(0,p)
from test_direct_model import ServerFixture
from specimens import BY_KEY
from artifact_portal import ArtifactPortal
from relay_llm import DirectRelayLLM
from relay_session import trial

ROOT=HERE.parents[1]
class TestLocalHTTP(unittest.TestCase):
    def test_actual_http_transport_distinguished_from_fake_language_model(self):
        task=BY_KEY['food_recalled_elsewhere']
        sequence=[
            {'action':'define','symbol':'gobbo','template':{
                'tool':'read','artifact_id':'$artifact','limit':4},
                'gloss':'Visit the chosen source document'},
            {'action':'speak','symbol':'gobbo','values':{
                'artifact':'experiments/thought-023/grammar.py'}},
            {'bindings':{'current':'register_g','event':'register_f'},
             'relation':'DIFFERENCE',
             'evidence_ids':['experiments/thought-027/proof_memory.py'],
             'rationale':'The recalled items set is reduced by items on the shelf.'}
        ]
        with ServerFixture(sequence) as server:
            class Local(DirectRelayLLM):
                TAGS=server.Model.TAGS;GENERATE=server.Model.GENERATE
            model=Local('test-llm:0.5b')
            result=trial(task,ArtifactPortal(ROOT),model,enable_pidgin=True)
            self.assertEqual(result['status'],'REVIEW_SCOPED_INTERPRETATION_NOT_INSTALLED')
            self.assertEqual(result['frozen']['correct'],64)
            self.assertEqual(result['actual_model_call_count'],3)
            self.assertTrue(result['pidgin_was_used'])
            self.assertTrue(all(r['transport']=='DIRECT_LOOPBACK_OLLAMA_HTTP' for r in model.calls))
            self.assertTrue(all(r['http_generation_completed'] for r in model.calls))
            posts=[p[2] for p in server.http.record if p[0]=='POST']
            self.assertEqual(len(posts),3)
            self.assertIn('OPTIONAL CO-INVENTED PIDGIN',posts[0]['prompt'])
            self.assertIn('gobbo',posts[2]['prompt'])
            self.assertIn('FINAL PHASE',posts[-1]['prompt'])
            self.assertNotIn('task.policy',posts[0]['prompt'])
            self.assertFalse(result['installed'])
    def test_no_pidgin_is_optional_but_reserved_final_still_runs(self):
        task=BY_KEY['food_safe']
        sequence=[{'action':'skip'},{'action':'skip'},
             {'bindings':{'current':'register_f','event':'register_g'},
              'relation':'DIFFERENCE','evidence_ids':['experiments/thought-027/proof_memory.py'],
              'rationale':'Subtract recalled items from the shelf items.'}]
        with ServerFixture(sequence) as server:
            class Local(DirectRelayLLM):
                TAGS=server.Model.TAGS;GENERATE=server.Model.GENERATE
            model=Local('test-llm:0.5b')
            result=trial(task,ArtifactPortal(ROOT),model,enable_pidgin=True)
            self.assertEqual(result['status'],'REVIEW_SCOPED_INTERPRETATION_NOT_INSTALLED')
            self.assertFalse(result['pidgin_was_used'])
            self.assertEqual(result['actual_model_call_count'],3)
            self.assertEqual(model.calls[-1]['phase'],'FINAL')

if __name__=='__main__':unittest.main()
