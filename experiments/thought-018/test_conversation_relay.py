"""MOTIF-018 conversation LLM transport tests; genuinely execute frozen graph evaluator."""
import json
import unittest
from pathlib import Path
from copy import deepcopy
from conversation_relay import run

SOURCE = Path(__file__).with_name('conversation-gpt6-proposals.json')

class ConversationRelayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.proposals=json.loads(SOURCE.read_text())
        cls.result=run(cls.proposals,max_rounds=3)

    def test_model_supplied_proposals_are_data_not_python(self):
        self.assertEqual(len(self.proposals),2)
        self.assertEqual(self.result['report']['model_kind'],'GPT6_CONVERSATION_RELAY_NOT_LOCAL_API')
        self.assertFalse(self.result['motif_autonomously_called_llm'])
        self.assertFalse(self.result['source_code_written_by_model_and_executed'])
        self.assertFalse(self.result['external_model_identity_verified'])

    def test_first_candidate_refuted_by_independent_probe(self):
        a=self.result['report']['steps'][0]
        self.assertEqual(a['model_candidate'],'GROW')
        self.assertEqual(a['disposition'],'REFUTED_ON_DEV')
        self.assertEqual(a['suggestion_disposition'],'MODEL_TEST_DEFERRED_INFORMATIVE_ALTERNATIVE')
        self.assertNotEqual(a['model_candidate_output'],a['independent_oracle_output'])

    def test_second_candidate_survives(self):
        self.assertEqual(self.result['report']['status'],'PATCH_FOR_HUMAN_REVIEW_NOT_INSTALLED')
        self.assertEqual(self.result['report']['selected_mechanism'],'FLIP')
        self.assertEqual(self.result['report']['dev_truth_table'],{'passed':64,'total':64})
        self.assertEqual(self.result['report']['development_graph'],{'passed':8,'total':8})
        self.assertEqual(self.result['report']['safety_graph'],{'passed':4,'total':4})
        self.assertEqual(self.result['report']['frozen_graph_audit'],{'passed':60,'total':60})
        self.assertEqual(self.result['report']['stress_graph_audit'],{'passed':80,'total':80})
        self.assertEqual(self.result['report']['pen_state'],'UNCHANGED')
        self.assertFalse(self.result['report']['installed'])
        self.assertEqual(self.result['report']['external_authority'],'NONE')

    def test_no_hidden_oracle_answer_in_model_transport(self):
        a,b=self.result['model_relay_calls']
        self.assertEqual(list(a['development_feedback_visible']),[])
        self.assertEqual(b['development_feedback_visible'][0]['disposition'],'REFUTED_ON_DEV')
        self.assertTrue(all(c['frozen_audit_disclosed_before_proposal'] is False for c in (a,b)))

    def test_unknown_or_malicious_model_reply_holds(self):
        attacks=deepcopy(self.proposals)
        attacks[0]['mechanism']['exec']='python -c ...'
        bad=run(attacks,max_rounds=2)
        self.assertEqual(bad['report']['status'],'HOLD_NO_VERIFIED_MODEL_PROPOSAL')
        self.assertEqual(bad['report']['steps'][0]['disposition'],'HOLD_MODEL_INVALID_OR_UNAVAILABLE')
        self.assertFalse(bad['report']['installed'])

if __name__=='__main__': unittest.main()
