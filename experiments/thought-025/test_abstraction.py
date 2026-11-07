"""THOUGHT-025: offline evidence guards and loopback transport (NOT a real LLM)."""
import copy, json, threading, unittest
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from specimens import TASKS,BY_KEY,public_brief,independent_target
from abstraction import (SCHEMA,AbstractionError,validate_proposal,evaluate_reply,
 check_truth,source_owned_program_check,model_trial,classical_without_language,lower_surface_math)
from abstraction_llm import DirectAbstractionLLM
from abstraction_cli import main


def make(task,expr,binding=None):
    id0,id1=(f[0] for f in task.fields)
    return {'schema':SCHEMA,'bindings':binding or {'current':id0,'event':id1},
        'expression':expr,'rationale':'Source-only typed mathematics, not a verified claim'}

def ref(name):return {'ref':name}
def diff(a,b):return {'op':'difference','args':[a,b]}
def union(a,b):return {'op':'union','args':[a,b]}

class Fake:
    def __init__(self,responses):self.responses=list(responses);self.calls=[]
    def propose(self,brief,feedback=()):
        self.calls.append({'brief':copy.deepcopy(brief),'feedback':copy.deepcopy(feedback)})
        return self.responses[min(len(self.calls)-1,len(self.responses)-1)]

class AbstractionTests(unittest.TestCase):
    def test_model_brief_has_no_truth_policy_or_bindings(self):
        for task in TASKS:
            v=public_brief(task)
            self.assertEqual(set(v),{'story','input_fields','feature_count','meaning'})
            self.assertNotIn('policy',str(v).lower())
            self.assertNotIn('roles',str(v).lower())
            self.assertNotIn('DIFF',json.dumps(v))
    def test_switching_roles_changes_semantic_answer(self):
        a=BY_KEY['food_safe'];b=BY_KEY['food_recalled_elsewhere']
        forward=make(a,diff(ref('state.on'),ref('arrival.toggles')))
        backwards=make(b,diff(ref('state.on'),ref('arrival.toggles')),
                       {'current':'register_g','event':'register_f'})
        raw={'register_f':3,'register_g':5}
        self.assertEqual(evaluate_reply(a,forward,raw),2)
        self.assertEqual(evaluate_reply(b,backwards,raw),4)
        self.assertEqual(check_truth(a,forward)['correct'],64)
        self.assertEqual(check_truth(b,backwards)['correct'],64)
    def test_reversed_binding_matters_in_frozen_audit(self):
        task=BY_KEY['food_recalled_elsewhere']
        bad=make(task,diff(ref('state.on'),ref('arrival.toggles')))
        self.assertLess(check_truth(task,bad)['correct'],64)
    def test_universe_const_carries_between_human_domain_and_math(self):
        task=BY_KEY['not_on_shelf']
        r=make(task,diff(ref('universe'),ref('state.on')))
        self.assertEqual(check_truth(task,r)['correct'],64)
        self.assertEqual(source_owned_program_check(task,r)['correct'],64)
    def test_surface_math_is_lowered_to_fixed_source_grammar(self):
        task=BY_KEY['volunteer_eligible']
        a=ref('state.on');b=ref('arrival.toggles')
        high=make(task,{'op':'intersection','args':[a,b]})
        self.assertEqual(check_truth(task,high)['correct'],64)
        self.assertEqual(source_owned_program_check(task,high)['correct'],64)
        flip=BY_KEY['cancel_or_add']
        self.assertEqual(check_truth(flip,make(flip,{'op':'xor','args':[a,b]}))['correct'],64)
        comp=BY_KEY['not_on_shelf']
        self.assertEqual(check_truth(comp,make(comp,{'op':'complement','args':[a]}))['correct'],64)

    def test_unknown_binding_and_unsupported_operator_hold(self):
        task=BY_KEY['food_safe'];base=make(task,ref('state.on'))
        for bad in [{**base,'bindings':{'current':'ghost','event':'register_g'}},
                    {**base,'bindings':{'current':'register_f','event':'register_f'}},
                    {**base,'expression':{'op':'eval','args':[ref('state.on'),ref('arrival.toggles')]}},
                    {**base,'python':'import os'},
                    {**base,'schema':'wrong'}]:
            with self.assertRaises(Exception):validate_proposal(task,bad)
    def test_model_retry_can_correct_binding_after_counterexample(self):
        t=BY_KEY['food_recalled_elsewhere']
        wrong=make(t,diff(ref('state.on'),ref('arrival.toggles')))
        right=make(t,diff(ref('state.on'),ref('arrival.toggles')),
                   {'current':'register_g','event':'register_f'})
        m=Fake([wrong,right]);r=model_trial(t,m)
        self.assertEqual(r['status'],'CANDIDATE_ABSTRACTION_FOR_HUMAN_REVIEW_NOT_INSTALLED')
        self.assertEqual(r['model_calls'],2)
        self.assertEqual(r['frozen']['correct'],64)
        self.assertEqual(r['program']['correct'],64)
        self.assertTrue(m.calls[1]['feedback'])
        self.assertFalse(r['installed'])
    def test_model_failure_is_recorded_not_turned_into_success(self):
        t=BY_KEY['food_safe'];m=Fake([make(t,ref('universe'))]*2)
        r=model_trial(t,m)
        self.assertTrue(r['status'].startswith('HOLD_'))
        self.assertIsNone(r['model_declared_mapping']);self.assertFalse(r['installed'])
    def test_classical_baseline_does_not_need_language_interpreter(self):
        for t in TASKS:
            r=classical_without_language(t)
            if t.representable:
                self.assertEqual(r['status'],'REVIEW_CLASSICAL_CANDIDATE_NOT_INSTALLED',t.key)
                self.assertEqual(r['frozen_correct'],64)
            else:self.assertTrue(r['status'].startswith('HOLD_'))
    def test_nonboolean_gates_are_evaluator_owned_not_llm(self):
        fake=Fake([{}]);t=BY_KEY['unknown_beliefs'];v=BY_KEY['vague_access']
        for task in (t,v):
            r=model_trial(task,fake)
            self.assertTrue(r['status'].startswith('HOLD_'))
            self.assertEqual(r['model_calls'],0)
        self.assertEqual(fake.calls,[])
    def test_frozen_catches_dev_only_overfit(self):
        task=BY_KEY['food_safe']
        candidate=make(task,ref('state.on'))
        self.assertLess(check_truth(task,candidate)['correct'],64)
    def test_offline_cli_never_uses_llm(self):
        from tempfile import TemporaryDirectory
        from pathlib import Path
        with TemporaryDirectory() as d:
            p=Path(d)/'x.json'
            self.assertEqual(main(['--output',str(p)]),0)
            r=json.loads(p.read_text())
            self.assertFalse(r['model_called']);self.assertEqual(r['real_llm_generations'],0)
            self.assertFalse(r['installed'])

class StubServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.server.events.append(('GET',self.path))
        self.send_json({'models':[{'name':'test:1b','digest':'a'*64}]})
    def do_POST(self):
        data=json.loads(self.rfile.read(int(self.headers['Content-Length'])))
        self.server.events.append(('POST',self.path,data))
        value=self.server.replies.pop(0)
        self.send_json({'done':True,'response':json.dumps(value),'model':'test:1b',
                        'prompt_eval_count':150,'eval_count':70})
    def send_json(self,data):
        content=json.dumps(data).encode()
        self.send_response(200);self.send_header('Content-Type','application/json')
        self.send_header('Content-Length',str(len(content)));self.end_headers();self.wfile.write(content)
    def log_message(self,*args):pass

class TransportTests(unittest.TestCase):
    def test_local_transport_receives_language_and_requires_its_own_binding(self):
        t=BY_KEY['food_recalled_elsewhere']
        good=make(t,diff(ref('state.on'),ref('arrival.toggles')),
                  {'current':'register_g','event':'register_f'})
        response={k:v for k,v in good.items() if k!='schema'}
        server=ThreadingHTTPServer(('127.0.0.1',0),StubServer)
        server.events=[];server.replies=[response]
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        try:
            class Loopback(DirectAbstractionLLM):
                TAGS=f'http://127.0.0.1:{server.server_port}/api/tags'
                GENERATE=f'http://127.0.0.1:{server.server_port}/api/generate'
            model=Loopback('test:1b')
            r=model_trial(t,model,max_calls=1)
            self.assertEqual(r['status'],'CANDIDATE_ABSTRACTION_FOR_HUMAN_REVIEW_NOT_INSTALLED')
            self.assertEqual(r['model_calls'],1)
            self.assertEqual(len(model.calls),1)
            posts=[x[2] for x in server.events if x[0]=='POST']
            self.assertEqual(len(posts),1)
            self.assertIn('register_g',posts[0]['prompt'])
            task_data=posts[0]['prompt'].split('TASK_JSON_DATA=')[-1]
            self.assertNotIn('"policy"',task_data)
            self.assertNotIn('"roles"',task_data)
        finally:
            server.shutdown();server.server_close();thread.join(timeout=2)

if __name__=='__main__':unittest.main()
