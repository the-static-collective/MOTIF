"""Offline proof harness; scripted responders are not generative language models."""
from __future__ import annotations
import copy,tempfile,json,unittest,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
for d in ('thought-025','thought-029','thought-030'):
    p=str(HERE.parent/d)
    if p not in sys.path:sys.path.insert(0,p)
from specimens import BY_KEY,public_brief
from artifact_portal import ArtifactPortal
from pidgin2 import ParameterizedPidgin,PidginProtocolError
from relay import EvidenceRelay,RelayError
from relay_session import trial,scoped_read,RelaySessionError
from relay_run import ScriptedFixture,main
ROOT=HERE.parents[1]

class WrongCitation(ScriptedFixture):
    def conclude(self,*a):
        out=super().conclude(*a)
        out['evidence_ids']=['never/read/this-file']
        return out
class InvalidTool(ScriptedFixture):
    def research(self,*a):
        self.calls.append({'source':'SCRIPTED','phase':'RESEARCH'})
        return {'action':'read','artifact_id':'experiments/thought-025/specimens.py'}

class RouterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.portal=ArtifactPortal(ROOT)
    def test_public_route_never_uses_evaluator_policy(self):
        for key in ('food_safe','food_recalled_elsewhere'):
            public=public_brief(BY_KEY[key])
            selected=EvidenceRelay(self.portal).prepare(public)
            self.assertEqual(len(selected['packet']['cards']),3)
            self.assertTrue(selected['plan']['source_selected_without_target_oracle'])
            self.assertNotIn('policy',selected['plan'])
            self.assertTrue(all('specimens.py' not in x for x in selected['plan']['selected_artifact_ids']))
    def test_proof_and_graph_are_inspected_as_distinct_data(self):
        p=EvidenceRelay(self.portal).prepare(public_brief(BY_KEY['food_safe']))['packet']
        kinds={card['kind'] for card in p['cards']}
        self.assertIn('proof_or_evidence',kinds)
        self.assertTrue(any('native_graph_sample' in card for card in p['cards']))
        self.assertTrue(p['graphs'])
        self.assertTrue(all(x['relationships_not_independently_verified'] for x in p['graphs']))
    def test_all_identifiers_cite_real_portal_reads(self):
        p=EvidenceRelay(self.portal).prepare(public_brief(BY_KEY['food_safe']))['packet']
        for card in p['cards']:
            self.assertIn(card['artifact_id'],self.portal._items)
            self.assertEqual(card['sha256'],self.portal._items[card['artifact_id']][0]['sha256'])
            self.assertTrue(card['retrieved_by_source_owned_portal'])
    def test_payload_does_not_include_source_owner_answers_as_hidden_labels(self):
        p=EvidenceRelay(self.portal).prepare(public_brief(BY_KEY['food_safe']))
        self.assertNotIn('"policy":"DIFF"',json.dumps(p,separators=(',',':')))
        self.assertNotIn('"roles":["register_f","register_g"]',json.dumps(p,separators=(',',':')))
    def test_explicit_model_read_of_evaluator_answer_is_refused(self):
        with self.assertRaises(RelaySessionError):scoped_read(self.portal,{'tool':'read','artifact_id':'experiments/thought-025/specimens.py'})
    def test_parameterized_symbol_can_refer_to_multiple_source_files(self):
        p=ParameterizedPidgin(self.portal)
        p.define('gofer',{'tool':'read','artifact_id':'$artifact','limit':4},'Inspect an approved source artifact')
        a=p.speak('gofer',{'artifact':'experiments/thought-027/reuse.py'})
        b=p.speak('gofer',{'artifact':'experiments/thought-023/grammar.py'})
        self.assertNotEqual(a['artifact_id'],b['artifact_id'])
        self.assertEqual(p.view()['tokens_coined'],1)
        self.assertEqual(p.view()['token_uses'],2)
        self.assertTrue(p.cost_report()['token_costs_not_equivalent_to_bytes'])
    def test_parameterized_search_may_vary_term(self):
        p=ParameterizedPidgin(self.portal)
        p.define('looksy',{'tool':'search','term':'$term','limit':3},'Search read only indexed sources')
        self.assertEqual(p.speak('looksy',{'term':'proof'})['term'],'proof')
        self.assertEqual(p.speak('looksy',{'term':'graph'})['term'],'graph')
    def test_no_undefined_or_invalid_parameterized_meaning(self):
        p=ParameterizedPidgin(self.portal)
        for template in ({'tool':'shell','command':'ls'},
                         {'tool':'read','artifact_id':'$bogus'},
                         {'tool':'search','term':'$node'},
                         {'tool':'read','artifact_id':'../../password'},
                         {'tool':'read','artifact_id':'experiments/thought-027/reuse.py'}):
            with self.subTest(template=template),self.assertRaises(PidginProtocolError):
                p.define('looksy',template,'Inspect source data safely')
        self.assertEqual(p.view()['tokens_coined'],0)
    def test_injected_arguments_dont_escape_typed_read_portal(self):
        p=ParameterizedPidgin(self.portal)
        p.define('gofer',{'tool':'read','artifact_id':'$artifact'},'Read one source artifact')
        with self.assertRaises(PidginProtocolError):p.speak('gofer',{'artifact':'../../../secrets'})
        with self.assertRaises(PidginProtocolError):p.speak('gofer',{'artifact':'experiments/thought-027/reuse.py','shell':'rm'})
        self.assertEqual(p.view()['token_uses'],0)
    def test_reserved_words_and_collision_refused(self):
        p=ParameterizedPidgin(self.portal)
        with self.assertRaises(PidginProtocolError):p.define('eval',{'tool':'search','term':'$term'},'Search sources')
        p.define('looksy',{'tool':'search','term':'$term'},'Search indexed sources')
        with self.assertRaises(PidginProtocolError):p.define('looksy',{'tool':'search','term':'$term'},'Search again')
    def test_scripted_plain_and_pidgin_both_verify_without_truth_leak(self):
        task=BY_KEY['food_recalled_elsewhere']
        a=trial(task,self.portal,ScriptedFixture(task.key,pidgin=False),enable_pidgin=False)
        b=trial(task,self.portal,ScriptedFixture(task.key,pidgin=True),enable_pidgin=True)
        for x in (a,b):
            self.assertEqual(x['status'],'REVIEW_SCOPED_INTERPRETATION_NOT_INSTALLED')
            self.assertEqual(x['frozen']['correct'],64)
            self.assertEqual(x['fixed_template']['correct'],64)
            self.assertEqual(x['actual_model_call_count'],3)
            self.assertFalse(x['installed'])
        self.assertFalse(a['pidgin_was_used']);self.assertEqual(a['pidgin_lexicon']['tokens_coined'],0)
        self.assertTrue(b['pidgin_was_used']);self.assertEqual(b['pidgin_lexicon']['tokens_coined'],1)
        self.assertTrue(any(e.get('origin')=='MODEL_PIDGIN_WITH_AUDITABLE_BACKTRANSLATION' for e in b['research_trace']))
    def test_model_may_ignore_pidgin(self):
        t=BY_KEY['food_safe']
        result=trial(t,self.portal,ScriptedFixture(t.key,pidgin=False),enable_pidgin=True)
        self.assertEqual(result['status'],'REVIEW_SCOPED_INTERPRETATION_NOT_INSTALLED')
        self.assertFalse(result['pidgin_was_used'])
    def test_bad_final_citations_hold_even_with_correct_math(self):
        t=BY_KEY['food_safe'];result=trial(t,self.portal,WrongCitation(t.key))
        self.assertEqual(result['status'],'HOLD_INVALID_FINAL_OR_CITATION')
        self.assertIsNone(result['frozen'])
    def test_wrong_mathematical_binding_holds(self):
        t=BY_KEY['food_safe'];result=trial(t,self.portal,ScriptedFixture(t.key,wrong=True))
        self.assertTrue(result['status'].startswith('HOLD_'))
        self.assertIsNone(result['fixed_template'])
    def test_bad_research_does_not_consume_final_slot(self):
        t=BY_KEY['food_safe'];result=trial(t,self.portal,InvalidTool(t.key))
        self.assertEqual(result['actual_model_call_count'],3)
        self.assertEqual(result['status'],'REVIEW_SCOPED_INTERPRETATION_NOT_INSTALLED')
        self.assertEqual(result['model_research_refusals'],2)
    def test_unsupported_truth_domain_holds_before_model(self):
        t=BY_KEY['unknown_beliefs'];model=ScriptedFixture(t.key)
        result=trial(t,self.portal,model)
        self.assertEqual(result['model_calls'],0)
        self.assertEqual(model.calls,[])
        self.assertTrue(result['status'].startswith('HOLD_'))
    def test_scripted_cli_not_real_llm(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'r.json'
            self.assertEqual(main(['--backend','offline','--repo',str(ROOT),'--output',str(path)]),0)
            data=json.loads(path.read_text())
            self.assertFalse(data['real_llm_inference'])
            self.assertEqual(data['real_llm_generations'],0)
            self.assertTrue(data['tasks']['food_safe']['optional_pidgin']['pidgin_was_used'])
            self.assertFalse(data['installed'])
    def test_budget_guards_refuse_invalid_values(self):
        t=BY_KEY['food_safe'];model=ScriptedFixture(t.key)
        for n in (True,-1,4):
            with self.assertRaises(RelaySessionError):trial(t,self.portal,model,research_steps=n)
        for n in (0,6,True):
            with self.assertRaises(RelaySessionError):trial(t,self.portal,model,preload=n)

if __name__=='__main__':unittest.main()
