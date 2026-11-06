"""MOTIF THOUGHT-016 — model-guided synthesis of a new *typed composition*.

The model operates as a developer/tester: it ranks repairs, proposes a
counterexample experiment, and receives development-only observations.
An independent oracle grades every output. No arbitrary model code runs and
no proposal is applied to an owned repository by this module.
"""
from __future__ import annotations
import copy
import difflib
import hashlib
import json
import math
import os
import re
import subprocess
import sys
import tempfile
from collections import Counter
from itertools import combinations
from pathlib import Path
from grammar import (GrammarError,baseline_program,compile_program,validate_program,
                     expr,ref,digest)
from oracle import validate,validate_answer,independent_optimum,OracleError
from fixtures import DEV,SAFETY,AUDIT,STRESS,TRAIN

LAB_SCHEMA='motif.thought016.algorithm-inventor.v1'
_EVAL_CACHE = {}  # keyed by exact program and exact fixture bytes; evaluator-owned only
FRAGMENTS=('GATE','PICKUP','KEY_STATE','REVISIT')
class LabError(ValueError):pass

class TinyDesignModel:
    """Trained naive-Bayes classifier, used for experiment suggestions.

    Its vocabulary and targets are human-authored; this is not a generative LLM
    nor invention of a fundamentally new mathematical algorithm.
    """
    model_kind='OFFLINE_SUPERVISED_BAYES_PROGRAM_COMPOSITION_PROPOSER'
    def __init__(self,training=TRAIN):
        self.classes=Counter();self.tokens={c:Counter() for c in ('GATE','PICKUP','KEY_STATE','REVISIT','RISK')}
        self.vocab=set();self.calls=[]
        for message,label in training:
            if label not in self.tokens or not isinstance(message,str):raise LabError('invalid training specimen')
            parts=re.findall(r'[a-z]+',message.lower())
            self.classes[label]+=1;self.tokens[label].update(parts);self.vocab.update(parts)
    def predict(self,message):
        if not isinstance(message,str) or len(message)>240:raise LabError('bounded diagnostic required')
        parts=re.findall(r'[a-z]+',message.lower())
        s={}
        for category in self.tokens:
            c=self.tokens[category];den=max(1,sum(c.values())+len(self.vocab))
            s[category]=math.log((self.classes[category]+1)/(sum(self.classes.values())+len(self.tokens)))+sum(
                math.log((c[w]+1)/den) for w in parts)
        return max(s,key=lambda k:(s[k],-list(self.tokens).index(k)))
    def rank_fragments(self,failures,installed):
        if len(failures)>32 or not isinstance(installed,(tuple,list,set)):
            raise LabError('development input bounds')
        votes=Counter()
        for fail in failures:
            predicted=self.predict(fail['description'])
            votes[predicted]+=1
        remaining=[f for f in FRAGMENTS if f not in installed]
        result=sorted(remaining,key=lambda x:(-votes[x],FRAGMENTS.index(x)))
        self.calls.append({'kind':'MODEL_RANK_COMPOSITION_FRAGMENTS',
            'failure_count':len(failures),'votes':dict(votes),'ranking':result,
            'seen_data':'DEV_ONLY'})
        return result
    def propose_discriminator(self):
        """A model-suggested *test transformation*. Oracle decides expected result.

        This cannot change the independent frozen audit; the mutation and
        specimen are visible development probes only.
        """
        proposal={'schema':'motif.thought016.probe.v1','kind':'REMOVE_PICKUP',
                  'case_index':0,'node':1,'rationale':'challenge claimed key acquisition'}
        self.calls.append({'kind':'MODEL_PROPOSE_COUNTEREXAMPLE',
                           'proposal':proposal,'seen_data':'DEV_ONLY'})
        return proposal
    def observe(self,receipt):
        self.calls.append({'kind':'MODEL_READ_DEV_RESULT','stage':receipt['round'],
                           'score':receipt['development_correct'],'seen_data':'DEV_ONLY'})

def apply_fragments(program,fragments):
    p=copy.deepcopy(validate_program(program))
    if not isinstance(fragments,(list,tuple)) or len(set(fragments))!=len(fragments) or any(f not in FRAGMENTS for f in fragments):
        raise GrammarError('unknown repeated compositional fragment')
    for name in fragments:
        if name=='GATE':
            pred=expr('subset',ref('edge.need'),ref('state.held_keys'))
            if pred not in p['guards']:p['guards'].append(pred)
        elif name=='PICKUP':
            p['effects']['held_keys']=expr('union',ref('state.held_keys'),ref('arrived.pickups'))
        elif name=='KEY_STATE':
            if 'held_keys' not in p['identity']:p['identity'].append('held_keys')
        elif name=='REVISIT':p['revisit']=True
    return validate_program(p)

def proposed_probe(proposal,development=DEV):
    if type(proposal) is not dict or set(proposal)!={'schema','kind','case_index','node','rationale'} or \
        proposal['schema']!='motif.thought016.probe.v1' or proposal['kind']!='REMOVE_PICKUP' or \
        type(proposal['case_index']) is not int or not 0<=proposal['case_index']<len(development) or \
        type(proposal['node']) is not int or not 0<=proposal['node']<development[proposal['case_index']]['problem']['n'] or \
        not isinstance(proposal['rationale'],str) or not 1<=len(proposal['rationale'])<=160:
        raise LabError('invalid model-proposed test transformation')
    item=copy.deepcopy(development[proposal['case_index']]);p=item['problem'];node=str(proposal['node'])
    if not p['pickups'][node]:raise LabError('counterexample mutation did not remove anything')
    p['pickups'][node]=[]
    validate(p)
    item['category']='MODEL_PROPOSED_TEST_NOT_BLIND_AUDIT'
    item['note']='Model-proposed: remove acquired key and check reachability against owner oracle'
    return item

def evaluate(program,specimens,*,timeout=5):
    validate_program(program)
    if not isinstance(specimens,(list,tuple)) or len(specimens)>128:raise LabError('bounded specimens')
    for s in specimens:
        if not isinstance(s,dict) or not isinstance(s.get('problem'),dict):raise LabError('invalid specimen')
        validate(s['problem'])
    cache_key=(digest(program),digest(specimens))
    if cache_key in _EVAL_CACHE:return copy.deepcopy(_EVAL_CACHE[cache_key])
    source=compile_program(program)
    with tempfile.TemporaryDirectory(prefix='motif-016-fixed-template-') as temp:
        candidate=Path(temp)/'candidate.py';candidate.write_text(source,encoding='utf-8')
        try:
            completed=subprocess.run([sys.executable,'-I','-B',str(candidate)],
                input=json.dumps([s['problem'] for s in specimens]),text=True,
                stdout=subprocess.PIPE,stderr=subprocess.PIPE,cwd=temp,
                env={'PATH':os.environ.get('PATH',''),'PYTHONNOUSERSITE':'1'},
                timeout=timeout,check=False)
        except subprocess.TimeoutExpired as exc:raise LabError('fixed-template execution time bound') from exc
    if completed.returncode!=0:raise LabError('fixed-template executor failed')
    if len(completed.stdout.encode('utf-8'))>80000:raise LabError('excess output')
    try:answers=json.loads(completed.stdout)
    except (ValueError,TypeError) as exc:raise LabError('invalid program output') from exc
    if not isinstance(answers,list) or len(answers)!=len(specimens):raise LabError('wrong output shape')
    cases=[]
    for i,(s,ans) in enumerate(zip(specimens,answers)):
        correct=validate_answer(s['problem'],ans)
        cases.append({'index':i,'category':s.get('category',''),'passed':correct,
                      'description':s.get('note','')[:200],
                      'actual':ans,'oracle_minimum':(independent_optimum(s['problem']) or {}).get('cost')})
    result={'total':len(cases),'correct':sum(x['passed'] for x in cases),
            'cases':cases,'source_digest':hashlib.sha256(source.encode()).hexdigest()}
    _EVAL_CACHE[cache_key]=copy.deepcopy(result)
    return result

def run_lab(*,model=None,rounds=3,development=DEV,audit=AUDIT,stress=STRESS):
    if type(rounds) is not int or not 0<=rounds<=5:raise LabError('invalid round budget')
    if len(development)<4 or len(development)>40 or len(audit)<4 or len(stress)<4:raise LabError('missing audit split')
    for group in (development,audit,stress,SAFETY):
        for item in group:validate(item['problem'])
    model=model or TinyDesignModel()
    start=baseline_program();current=copy.deepcopy(start)
    baseline=evaluate(start,development)
    safety_baseline=evaluate(start,SAFETY)
    installed=[];receipts=[]
    # The developer sees only development failures and generated test probes.
    proposal=model.propose_discriminator()
    extra=proposed_probe(proposal,development)
    probe_truth=independent_optimum(extra['problem'])
    probe_evidence={'proposal':proposal,'test_problem_digest':digest(extra['problem']),
                    'oracle_answer_cost':probe_truth['cost'] if probe_truth else None,
                    'independent_grade_not_model_answer':True,'audit_membership':False}
    for stage in range(rounds):
        current_result=evaluate(current,development)
        failures=[x for x in current_result['cases'] if not x['passed']]
        if not failures:break
        ranking=model.rank_fragments(failures,installed)
        # Model restricts each round's candidates to its top two diagnosed
        # mechanisms. The evaluator—not the model—grades singles and their
        # one pair. Without a successful model proposal the run holds.
        choices=[]
        for count in (1,2):
            for group in combinations(ranking[:2],count):
                proposed=apply_fragments(current,group)
                trial=evaluate(proposed,development)
                safety=evaluate(proposed,SAFETY)
                probe_grade=evaluate(proposed,[extra])
                regressions=sum(a['passed'] and not b['passed']
                                for a,b in zip(current_result['cases'],trial['cases']))
                viable=safety['correct']==safety['total'] and regressions==0
                choices.append({'fragments':list(group),'program':proposed,
                    'development':trial,'safety':safety,'probe':probe_grade,
                    'regressions':regressions,'viable':viable})
        viable=[x for x in choices if x['viable']]
        if not viable:
            receipts.append({'round':stage+1,'decision':'HOLD_NO_VALID_COMPOSITION',
                             'diagnostic_failures':len(failures)})
            break
        # Score by independent correctness; prefer simple stage then model rank.
        viable.sort(key=lambda x:(-x['development']['correct'],
                                  -x['probe']['correct'],len(x['fragments']),
                                  tuple(ranking.index(f) for f in x['fragments'])))
        chosen=viable[0]
        if chosen['development']['correct']<current_result['correct']:
            raise LabError('explicit regression gate violated')
        current=chosen['program'];installed.extend(chosen['fragments'])
        rec={'round':stage+1,'model_ranked_fragments':ranking,
             'selected_typed_expression_changes':chosen['fragments'],
             'candidate_count':len(choices),
             'development_correct':chosen['development']['correct'],
             'development_total':len(development),
             'safety_correct':chosen['safety']['correct'],
             'model_probe_correct':chosen['probe']['correct'],
             'source_digest':chosen['development']['source_digest'],
             'decision':'SCRATCH_ONLY_NO_RUNTIME_INSTALL',
             'external_authority':'NONE'}
        rec['receipt_digest']=digest(rec);receipts.append(rec)
        model.observe(rec)
    frozen=copy.deepcopy(current)
    # AFTER freezing, evaluate held-out and stress. The model gets none of them.
    audit_before=evaluate(start,audit)
    audit_after=evaluate(frozen,audit)
    stress_after=evaluate(frozen,stress)
    safety_after=evaluate(frozen,SAFETY)
    probe_after=evaluate(frozen,[extra])
    good=(audit_after['correct']==audit_after['total'] and
          stress_after['correct']==stress_after['total'] and
          safety_after['correct']==safety_after['total'] and
          evaluate(frozen,development)['correct']==len(development))
    status='PATCH_FOR_HUMAN_REVIEW_NOT_INSTALLED' if good else 'HOLD_FAILED_INDEPENDENT_AUDIT'
    before_source=compile_program(start);after_source=compile_program(frozen)
    diff=''.join(difflib.unified_diff(before_source.splitlines(True),after_source.splitlines(True),
         fromfile='experiments/thought-016/reference_solver.py',
         tofile='experiments/thought-016/candidate_solver.py'))
    report={'schema':LAB_SCHEMA,'status':status,'model_kind':getattr(model,'model_kind','UNVERIFIED_PROPOSER'),
        'staged_compositions':receipts,'model_calls':len(getattr(model,'calls',[])),
        'development':{'before':baseline['correct'],'after':evaluate(frozen,development)['correct'],
                       'total':len(development)},
        'safety':{'before':safety_baseline['correct'],'after':safety_after['correct'],
                  'total':safety_after['total']},
        'audit':{'before':audit_before['correct'],'after':audit_after['correct'],
                 'total':audit_after['total']},
        'stress':{'after':stress_after['correct'],'total':stress_after['total']},
        'model_proposed_test':probe_evidence,
        'model_test_result':{'passed':probe_after['correct'],'total':1},
        'installed_fragments':installed,
        'base_program':start,'candidate_program':frozen,
        'reference_source_sha256':hashlib.sha256(before_source.encode()).hexdigest(),
        'candidate_source_sha256':hashlib.sha256(after_source.encode()).hexdigest(),
        'counterexample':next((x for x in audit_after['cases']+stress_after['cases'] if not x['passed']),None),
        'heldout_exposed_to_developer':False,'model_authored_arbitrary_python':False,
        'model_output_is_program_ast_not_python':True,'execution_is_os_sandbox':False,
        'old_four_repair_dsl_sufficient_for_new_key_state_problem':False,
        'new_mathematics_proven':False,'human_merge_required':True,
        'written_to_project_implementation':False,'pen_state':'UNCHANGED',
        'external_authority':'NONE',
        'limitations':'Synthetic key-gate problem, human-designed grammar, tiny classifier, fixed trusted source template; no arbitrary model-code sandbox, no claim of novel search mathematics or live LLM.'}
    report['receipt_digest']=digest(report)
    return report,before_source,after_source,diff
