"""Ollama-looking localhost server fixture: NOT a pretrained LLM test."""
from __future__ import annotations
import sys,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent
for d in ('thought-019','thought-025'):
    p=str(HERE.parent/d)
    if p not in sys.path:sys.path.insert(0,p)
from test_direct_model import ServerFixture
from specimens import BY_KEY
from direct_routed_llm import DirectRoutedLLM
from artifact_portal import ArtifactPortal
from session import session

REPO=HERE.parents[1]
SOURCE='experiments/thought-027/reuse.py'

class TransportTests(unittest.TestCase):
    def test_model_may_define_and_use_own_word_with_real_http_fixture(self):
        task=BY_KEY['food_recalled_elsewhere']
        messages=[
          {'action':'define','symbol':'mowie','meaning':{'tool':'read','artifact_id':SOURCE},
           'gloss':'Inspect a reusable mathematical program'},
          {'action':'speak','symbol':'mowie'},
          {'action':'final','bindings':{'current':'register_g','event':'register_f'},
           'relation':'DIFFERENCE','evidence_ids':[SOURCE],
           'rationale':'Subtract inventory from recall register'}]
        with ServerFixture(messages) as s:
            class Local(DirectRoutedLLM):
                TAGS=s.Model.TAGS;GENERATE=s.Model.GENERATE
            model=Local('test-llm:0.5b')
            r=session(task,ArtifactPortal(REPO),model,max_steps=5)
            self.assertEqual(r['status'],'REVIEW_SCOPED_INTERPRETATION_NOT_INSTALLED')
            self.assertTrue(r['pidgin_used'])
            self.assertEqual(len(model.calls),3)
            self.assertTrue(all(x['actual_inference_completed'] for x in model.calls))
            self.assertEqual(r['frozen']['correct'],64)
            posts=[p[2] for p in s.http.record if p[0]=='POST']
            self.assertIn('EXPERIMENTAL OPTIONAL PIDGIN',posts[0]['prompt'])
            self.assertIn('mowie',posts[2]['prompt'])
            self.assertNotIn('task.policy',posts[0]['prompt'])
            self.assertFalse(r['installed'])
    def test_model_is_not_forced_to_use_pidgin_when_available(self):
        task=BY_KEY['food_safe']
        messages=[{'action':'read','artifact_id':SOURCE},
                  {'action':'final','bindings':{'current':'register_f','event':'register_g'},
                   'relation':'DIFFERENCE','evidence_ids':[SOURCE],
                   'rationale':'Exclude recalled inventory'}]
        with ServerFixture(messages) as s:
            class Local(DirectRoutedLLM):
                TAGS=s.Model.TAGS;GENERATE=s.Model.GENERATE
            model=Local('test-llm:0.5b')
            r=session(task,ArtifactPortal(REPO),model,max_steps=5)
            self.assertEqual(r['status'],'REVIEW_SCOPED_INTERPRETATION_NOT_INSTALLED')
            self.assertFalse(r['pidgin_used'])
            self.assertEqual(r['pidgin_lexicon']['tokens_coined'],0)

if __name__=='__main__':unittest.main()
