"""Offline regression tests. Scripted actors here are NOT generative models."""
from __future__ import annotations
import copy,json,tempfile,unittest,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
for name in ("thought-029","thought-025"):
    parent=str(HERE.parent/name)
    if parent not in sys.path:sys.path.insert(0,parent)
from artifact_portal import ArtifactPortal,PortalError
from navigation import EvidenceNavigator,NavigationError
from pidgin import PidginLexicon,PidginError
from session import session
from experiment import ScriptedModel,main
from specimens import BY_KEY,public_brief

REPO=Path(__file__).resolve().parents[2]
SOURCE='experiments/thought-027/reuse.py'

class DeterministicModel:
    def __init__(self,sequence):self.sequence=list(sequence);self.calls=[]
    def next(self,task,history,context):
        self.calls.append({'simulation_only':True,'history_length':len(history)})
        return copy.deepcopy(self.sequence[min(len(self.calls)-1,len(self.sequence)-1)])


def final_for(key,evidence=(SOURCE,)):
    task=BY_KEY[key]
    ids=[x[0] for x in task.fields]
    if key=='food_recalled_elsewhere':ids=ids[::-1]
    return {'action':'final','bindings':{'current':ids[0],'event':ids[1]},
            'relation':'DIFFERENCE','evidence_ids':list(evidence),
            'rationale':'Source-owned fixture shows typed mathematical operation'}

class RouteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.portal=ArtifactPortal(REPO)
    def test_evidence_orientation_is_not_answer_and_artifacts_are_indexed(self):
        r=EvidenceNavigator(self.portal).orient(public_brief(BY_KEY['food_safe']))
        self.assertTrue(r['suggestions'])
        self.assertTrue(r['not_a_task_answer'])
        self.assertTrue(r['relevance_is_unverified'])
        self.assertNotIn('policy',json.dumps(r))
        self.assertFalse(any('correct_relation' in json.dumps(x) for x in r['suggestions']))
        self.assertEqual(len({x['artifact_id'] for x in r['suggestions']}),len(r['suggestions']))
        self.assertTrue(any(x['kind']=='geometry_or_thought_space' for x in self.portal.catalog(limit=30)['items']) or
                        any('geometry' in x for x in self.portal._items))
    def test_route_tracks_inspected_sources_and_prioritizes_unvisited(self):
        navigator=EvidenceNavigator(self.portal)
        original=navigator.orient(public_brief(BY_KEY['food_recalled_elsewhere']))
        aid=original['suggestions'][0]['artifact_id']
        history=[{'stage':'READ_ONLY_TOOL','request':{'tool':'read','artifact_id':aid},'result':{}}]
        revised=navigator.orient(public_brief(BY_KEY['food_recalled_elsewhere']),history)
        self.assertIn(aid, revised['already_inspected_artifacts'])
        self.assertNotIn(aid,[x['artifact_id'] for x in revised['suggestions']])
    def test_large_or_untyped_navigation_request_refused(self):
        n=EvidenceNavigator(self.portal)
        for bad in (0,13,True):
            with self.assertRaises(NavigationError):n.orient(public_brief(BY_KEY['food_safe']),max_suggestions=bad)
        with self.assertRaises(NavigationError):n.orient({'story':'foo'})
    def test_symbol_is_model_chosen_read_only_and_backtranslated(self):
        lex=PidginLexicon(self.portal)
        a=lex.define('mipana',{'tool':'read','artifact_id':SOURCE,'limit':3},'Read a proof reuse source')
        self.assertEqual(a['symbol'],'mipana')
        self.assertEqual(lex.view()['tokens_coined'],1)
        self.assertEqual(lex.view()['token_uses'],0)
        request=lex.translate('mipana')
        self.assertEqual(request['tool'],'read')
        self.assertEqual(request['artifact_id'],SOURCE)
        self.assertEqual(lex.view()['terms']['mipana']['uses'],1)
    def test_symbol_cannot_gain_host_or_external_tool_authority(self):
        l=PidginLexicon(self.portal)
        for m in ({'tool':'shell','command':'ls'},
                  {'tool':'read','artifact_id':'../../private/secrets'},
                  {'tool':'search','term':'x'},
                  {'tool':'neighbors','graph_id':'invented','node_id':'ghost'},
                  {'tool':'read','artifact_id':SOURCE,'exec':'yes'},
                  {'tool':'open_url','url':'https://example.com'}):
            with self.subTest(m=m),self.assertRaises(PidginError):l.define('mockword',m,'Cannot execute code')
        self.assertEqual(len(l.definitions),0)
    def test_pidgin_collisions_and_unknown_symbols_fail_closed(self):
        l=PidginLexicon(self.portal)
        l.define('hoodu',{'tool':'search','term':'proof'},'Find proof material')
        with self.assertRaises(PidginError):l.define('hoodu',{'tool':'catalog'},'Second meaning refused')
        with self.assertRaises(PidginError):l.translate('unknown')
        with self.assertRaises(PidginError):l.define('eval',{'tool':'catalog'},'Reserved label')
        self.assertEqual(len(l.definitions),1)
    def test_opt_out_stays_unused(self):
        r=session(BY_KEY['food_safe'],self.portal,ScriptedModel('food_safe',False),max_steps=5,enable_pidgin=True)
        self.assertEqual(r['status'],'REVIEW_SCOPED_INTERPRETATION_NOT_INSTALLED')
        self.assertFalse(r['pidgin_used'])
        self.assertEqual(r['pidgin_lexicon']['tokens_coined'],0)
        self.assertEqual(r['frozen']['correct'],64)
    def test_pidgin_opt_in_is_real_machine_decoded_action(self):
        r=session(BY_KEY['food_recalled_elsewhere'],self.portal,ScriptedModel('food_recalled_elsewhere',True),max_steps=5)
        self.assertEqual(r['status'],'REVIEW_SCOPED_INTERPRETATION_NOT_INSTALLED')
        self.assertTrue(r['pidgin_used']);self.assertEqual(r['pidgin_lexicon']['tokens_coined'],1)
        self.assertEqual(r['actual_model_call_count'],3)
        self.assertEqual(r['read_only_tool_calls'],1)
        self.assertEqual(r['frozen']['correct'],64)
        self.assertEqual(r['trusted_template_audit']['correct'],64)
        self.assertTrue(any(e['origin'].get('pidgin_symbol')=='nawe' for e in r['transcript'] if e['stage']=='READ_ONLY_TOOL'))
    def test_no_pidgin_access_when_arm_disabled(self):
        actor=ScriptedModel('food_safe',True)
        r=session(BY_KEY['food_safe'],self.portal,actor,enable_pidgin=False,max_steps=5)
        self.assertTrue(r['status'].startswith('HOLD_'))
        self.assertFalse(r['pidgin_used'])
        self.assertEqual(r['pidgin_lexicon']['tokens_coined'],0)
    def test_final_cannot_cite_only_a_search_hit(self):
        m=DeterministicModel([{'action':'search','term':'reuse'},final_for('food_safe')])
        r=session(BY_KEY['food_safe'],self.portal,m,max_steps=5)
        self.assertEqual(r['status'],'HOLD_INVALID_MODEL_OR_ARTIFACT_ACTION')
        self.assertEqual(r['read_only_tool_calls'],1)
        self.assertFalse(r['installed'])
    def test_final_cannot_cite_an_invented_artifact(self):
        m=DeterministicModel([{'action':'read','artifact_id':SOURCE},final_for('food_safe',['ghost/unknown.py'])])
        r=session(BY_KEY['food_safe'],self.portal,m,max_steps=5)
        self.assertEqual(r['status'],'HOLD_INVALID_MODEL_OR_ARTIFACT_ACTION')
        self.assertEqual(r['frozen'],None)
    def test_identical_tool_requests_suppressed_even_with_alias(self):
        actions=[{'action':'define','symbol':'xoya','meaning':{'tool':'read','artifact_id':SOURCE},'gloss':'Read a known file'},
                 {'action':'speak','symbol':'xoya'},{'action':'read','artifact_id':SOURCE},final_for('food_safe')]
        r=session(BY_KEY['food_safe'],self.portal,DeterministicModel(actions),max_steps=5)
        self.assertEqual(r['redundant_queries_suppressed'],1)
        self.assertEqual(r['read_only_tool_calls'],1)
        self.assertEqual(r['status'],'REVIEW_SCOPED_INTERPRETATION_NOT_INSTALLED')
    def test_refused_fabricated_file_does_not_prevent_recovery(self):
        m=DeterministicModel([{'action':'read','artifact_id':'ghost/outside'},
                     {'action':'read','artifact_id':SOURCE},final_for('food_safe')])
        r=session(BY_KEY['food_safe'],self.portal,m,max_steps=5)
        self.assertEqual(r['refused_calls'],1)
        self.assertEqual(r['read_only_tool_calls'],1)
        self.assertEqual(r['frozen']['correct'],64)
        self.assertFalse(r['installed'])
    def test_unknown_beliefs_hold_without_model_or_portal_action(self):
        m=DeterministicModel([{'action':'catalog'}])
        r=session(BY_KEY['unknown_beliefs'],self.portal,m)
        self.assertEqual(r['actual_model_call_count'],0)
        self.assertEqual(m.calls,[])
        self.assertTrue(r['status'].startswith('HOLD_'))
    def test_scripted_comparison_is_not_claimed_to_be_real_llm(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'x.json'
            self.assertEqual(main(['--backend','offline','--tasks','food_safe',
                    '--steps','5','--repo',str(REPO),'--output',str(path)]),0)
            r=json.loads(path.read_text())
            self.assertFalse(r['actual_llm_inference'])
            self.assertEqual(r['model_calls'],0)
            self.assertTrue(r['tasks']['food_safe']['routed_optional_pidgin']['pidgin_used'])
            self.assertFalse(r['installed'])

if __name__=='__main__':unittest.main()
