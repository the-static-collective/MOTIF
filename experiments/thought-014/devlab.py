"""THOUGHT-014 — MOTIF operates a bounded language-model development laboratory.

The model proposes code-free alias cartridges. An independent exact evaluator
runs source-controlled development and frozen audit fixtures. The model can
receive its failures and propose another candidate; it never rewrites Python,
updates shared rules, admits PEN, or defines ground truth for its own test.
"""
from __future__ import annotations
import json, re,sys
from collections import defaultdict
from pathlib import Path

SIB=Path(__file__).resolve().parent.parent/'thought-013'
if not SIB.is_dir(): SIB=Path(__file__).resolve().parent.parent/'thought013'
if str(SIB) not in sys.path:sys.path.append(str(SIB))
from human_talk import EFFECT_WORDS, interpret, normalize
from inquiry import InquiryCycle, InquiryError
from model_gateway import TinyTextModel, ACTS
from language_space import digest

class TrialError(ValueError):pass
RULE_SCHEMA='motif.thought014.rule-candidate.v1'


def validate_rule(rule):
    if not isinstance(rule,dict) or set(rule)!={'schema','pattern','speech_act','match','origin'}:
        raise TrialError('candidate must be exact non-executable rule DSL')
    if rule['schema'] != RULE_SCHEMA or rule['speech_act'] not in ACTS or rule['match']!='prefix':
        raise TrialError('unsupported rule action or match operation')
    s=rule['pattern']
    if not isinstance(s,str) or not re.fullmatch(r'[a-z ]{5,60}',s) or \
       len(s.split())<3 or s!=s.strip() or '  ' in s:
        raise TrialError('strict 3+-word plain-letter prefix required')
    if not isinstance(rule['origin'],str) or not rule['origin'] or len(rule['origin'])>100:
        raise TrialError('declared proposer origin required')
    return rule


def classify(text, engine, pair, rules=()):
    """Baseline 013 parser has absolute priority and protects effect requests."""
    baseline=interpret(text,engine=engine,selected_pair=pair)
    if baseline['speech_act'] not in ('UNKNOWN','HOLD_EFFECT_REQUEST'):
        return baseline['speech_act']
    if EFFECT_WORDS.search(text): return 'UNKNOWN'
    value=normalize(text)
    for rule in rules:
        validate_rule(rule)
        # Prefix must end on a word boundary; no accidental match 'whethered'.
        prefix=rule['pattern']
        if value.startswith(prefix) and (len(value)==len(prefix) or value[len(prefix)]==' '):
            act=rule['speech_act']
            if act in ('EXPLORE_POSSIBILITY','CHALLENGE','COMPARE') and pair is None:
                return 'UNKNOWN'
            return act
    return 'UNKNOWN'


def evaluate(examples,engine,pair,rules=()):
    cases=[]
    for text,truth in examples:
        assigned=classify(text,engine,pair if truth!='UNKNOWN' else None,rules)
        cases.append({'input':text,'expected':truth,'actual':assigned,'ok':assigned==truth})
    return {'total':len(cases),'correct':sum(x['ok'] for x in cases), 'cases':cases}


def common_prefix_word_sequences(lines):
    if not lines:return ''
    tokenized=[re.findall(r'[a-z]+',s.lower()) for s in lines]
    prefix=[]
    for group in zip(*tokenized):
        if len(set(group))>1:break
        prefix.append(group[0])
    return ' '.join(prefix)


class TinyModelDeveloper:
    """The toy ML model drives candidate ranking and receives dev-set critiques.

    Candidate rules come from trained prefix observations; they cannot be Python
    code. This is tiny supervised induction, NOT an LLM rewriting itself.
    """
    def __init__(self, train):
        self.train=list(train)
        self.model=TinyTextModel(train)
        self.rejected=set()
        self.calls=[]

    def propose(self, engine, pair):
        groups=defaultdict(list)
        for phrase,truth in self.train:
            if truth in ACTS and classify(phrase,engine,pair)== 'UNKNOWN':
                groups[truth].append(phrase)
        proposals=[]
        for act,items in groups.items():
            prefix=common_prefix_word_sequences(items)
            if len(prefix.split())<3 or prefix in self.rejected:continue
            # Real learned classifier is invoked for each candidate phrase.
            signals=[self.model.predict(x) for x in items]
            support=sum(x['speech_act']==act for x in signals)
            proposals.append((support,len(items),-len(prefix),prefix,act,signals))
        proposals.sort(key=lambda row:(-row[0],-row[1],row[2],row[3]))
        if not proposals:return None
        _,_,_,pattern,act,signals=proposals[0]
        proposal={'schema':RULE_SCHEMA,'pattern':pattern,'speech_act':act,
                  'match':'prefix','origin':'tiny-supervised-language-model'}
        self.calls.append({'kind':'MODEL_PROPOSE_RULE','rule':proposal,
                           'learned_predictions':signals,
                           'test_truth_access':'TRAIN_ONLY'})
        return proposal

    def critique(self, rule, passed, dev_failures):
        """The model sees an instrument receipt, not labels of the held-out audit."""
        self.calls.append({'kind':'MODEL_RECEIVES_DEV_CRITIQUE','candidate':rule['pattern'],
                           'passed':passed,'dev_error_count':len(dev_failures),
                           'test_truth_access':'DEV_ONLY'})
        self.rejected.add(rule['pattern'])


class SelfDevelopmentLab:
    def __init__(self,engine,pair,train,development,holdout,safety):
        self.engine=engine;self.pair=pair
        self.train=list(train);self.development=list(development)
        self.__heldout=tuple(holdout);self.safety=list(safety)
        if len(self.train)<4 or len(self.development)<4 or not self.__heldout:
            raise TrialError('train, development, frozen audit required')

    def run(self,*,max_rounds=4,developer=None):
        if type(max_rounds) is not int or not 0<=max_rounds<=6:
            raise TrialError('bounded development rounds required')
        developer=developer or TinyModelDeveloper(self.train)
        before=evaluate(self.development,self.engine,self.pair)
        active=[];receipts=[]
        for i in range(max_rounds):
            proposed=developer.propose(self.engine,self.pair)
            if proposed is None:break
            try:validate_rule(proposed)
            except TrialError:
                receipts.append({'round':i+1,'disposition':'HOLD_BAD_DSL'});break
            test=evaluate(self.development,self.engine,self.pair,[*active,proposed])
            unsafe=evaluate(self.safety,self.engine,self.pair,[*active,proposed])
            current=evaluate(self.development,self.engine,self.pair,active)
            regressions=[x for x,y in zip(test['cases'],current['cases']) if y['ok'] and not x['ok']]
            improvement=test['correct']-current['correct']
            acceptable=improvement>0 and unsafe['correct']==unsafe['total'] and not regressions
            dev_failures=[x['input'] for x in test['cases'] if not x['ok']]
            rec={'round':i+1,'candidate':proposed,'dev_before':current['correct'],
                 'dev_after':test['correct'],'dev_improvement':improvement,
                 'safety_correct':unsafe['correct'],'safety_total':unsafe['total'],
                 'regressions':len(regressions),'disposition':
                     'STAGED_PENCIL_CANDIDATE' if acceptable else 'HOLD_FAILED_EVALUATION',
                 'source_digest':self.engine.input_digest,'external_authority':'NONE'}
            rec['receipt_digest']=digest(rec);receipts.append(rec)
            if acceptable:active.append(proposed)
            developer.critique(proposed,acceptable,dev_failures)
        # A single AFTER-SELECTION frozen audit; no further proposal/revision.
        frozen_baseline=evaluate(self.__heldout,self.engine,self.pair)
        frozen_candidate=evaluate(self.__heldout,self.engine,self.pair,active)
        final_safety=evaluate(self.safety,self.engine,self.pair,active)
        if frozen_candidate['correct']<frozen_baseline['correct'] or final_safety['correct']!=final_safety['total']:
            status='HOLD_AUDIT_REGRESSION'
        elif not active:status='HOLD_NO_STAGED_IMPROVEMENT'
        else:status='CANDIDATE_FOR_HUMAN_REVIEW_NOT_INSTALLED'
        result={'schema':'motif.thought014.self-developer.v1',
            'status':status,'model_kind':developer.model.model_kind if hasattr(developer,'model') else 'EXTERNAL_PROPOSER',
            'model_proposals':len(developer.calls) if hasattr(developer,'calls') else None,
            'staged_rules':list(active),'development_baseline':before['correct'],
            'development_final':evaluate(self.development,self.engine,self.pair,active)['correct'],
            'development_total':len(self.development),
            'frozen_baseline':frozen_baseline['correct'],'frozen_candidate':frozen_candidate['correct'],
            'frozen_total':len(self.__heldout),'safety_passed':final_safety['correct'],
            'safety_total':final_safety['total'],'rounds':receipts,
            'independent_audit_after_proposals':True,'source_digest':self.engine.input_digest,
            'pen_state':'UNCHANGED','changed_source_code':False,'installed_rules':False,
            'external_authority':'NONE','limitations':
              'Small author-designed synthetic fixtures. Model used training data; selected on development; heldout checked once. No blind real-world evidence or LLM tested.'}
        result['receipt_digest']=digest(result)
        return result


def reasoning_policy_trial(engine,worlds,pair):
    """MOTIF also tests its own typed question-routing policies on model worlds.

    Strategy selection on 8 development worlds, frozen 8-world audit afterwards.
    This is a classical self-test (not model-written executable algorithms).
    """
    if len(worlds)<8 or len(worlds)>64:raise TrialError('bounded worlds required')
    dev_worlds=worlds[:len(worlds)//2];held=worlds[len(worlds)//2:]
    def trial(data,strategy):
        resolved=0;questions=0;replies=[]
        for w in data:
            cycle=InquiryCycle(engine,worlds,seed_pair=pair,strategy=strategy,geometry=False)
            result=cycle.run(lambda atom:w['atoms'][atom],budget=3)
            right=result['proposed_decision']==w['decision']
            resolved+=right;questions+=len(result['question_steps'])
            replies.append({'world':w['id'],'success':right,'questions':len(result['question_steps'])})
        return {'resolved':resolved,'queries':questions,'cases':len(data),'receipts':replies}
    develop={mode:trial(dev_worlds,mode) for mode in ('decision','world')}
    chosen=min(develop,key=lambda k:(-develop[k]['resolved'],develop[k]['queries'],k))
    frozen={mode:trial(held,mode) for mode in ('decision','world')}
    return {'schema':'motif.thought014.policy-self-test.v1','selected_after_dev':chosen,
            'development':develop,'heldout':frozen,'selected_improvement_over_alternate_queries':
              frozen['world']['queries']-frozen['decision']['queries'],
            'selection_uses_hidden_worlds':False,'source_digest':engine.input_digest,
            'external_authority':'NONE','policy_installed':False,
            'warning':'Hypothetical worlds and fixed rules; matched classical comparators, not a model objectively proving itself.'}

class OllamaDeveloper:
    """Optional actual LLM developer role; exact typed DSL and independent tests.

    Requires a local operator-provisioned Ollama model. No automatic model
    download, prompt-to-shell, source commit, or remote network access.
    """
    def __init__(self, local_model, train):
        if not hasattr(local_model,'suggest_rule'):
            raise TrialError('local generative model must support typed rule proposal')
        self.model=local_model
        self.train=list(train)
        self.feedback=[]
        self.calls=[]
    def propose(self,engine,pair):
        try:raw=self.model.suggest_rule(self.train,self.feedback)
        except Exception as e:
            self.calls.append({'kind':'MODEL_PROPOSAL_FAILED','error':type(e).__name__})
            return None
        rule={**raw,'schema':RULE_SCHEMA,'origin':'local-generative-model-unverified'}
        self.calls.append({'kind':'MODEL_PROPOSE_RULE','rule':rule,'test_truth_access':'TRAIN_AND_DEV_FEEDBACK_ONLY'})
        return rule
    def critique(self,rule,passed,dev_failures):
        self.feedback.append({'pattern':rule['pattern'],'accepted':bool(passed),
                              'development_failed_cases':dev_failures[:10]})
        self.calls.append({'kind':'MODEL_RECEIVES_DEV_CRITIQUE','candidate':rule['pattern'],
                           'passed':passed,'dev_error_count':len(dev_failures),
                           'test_truth_access':'DEV_ONLY'})
