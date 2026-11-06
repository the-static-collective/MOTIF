"""THOUGHT-018: MOTIF directs a proposer model through a bounded inquiry cycle.

Separation of duties: model proposes a DSL mechanism + diagnostic probe;
director chooses which probe is informative; independent bitmask oracle grades;
program evaluator runs the source-owned THOUGHT-017 fixed Python template;
frozen audit is disclosed only after development selection. No self-installation.
"""
from __future__ import annotations
from copy import deepcopy
from collections import Counter
from pathlib import Path
import sys
SIBLING=str(Path(__file__).resolve().parent.parent/'thought-017')
if SIBLING not in sys.path:sys.path.append(SIBLING)
from program import digest, evaluate_macro, validate_proposal, generate_source, ProposalError
from lab import evaluate_candidate
from fixtures import DEV, SAFETY, AUDIT, STRESS
from research_model import (ORDER, PATTERNS, TinyResearchModel, candidate,
                            validate_model_reply, guard_probe)

SCHEMA='motif.thought018.research-director.v1'
COLORS=('red','blue','green')


def bitmask(items):
    return sum(1<<COLORS.index(c) for c in items)


def color_set(mask):
    return frozenset(c for i,c in enumerate(COLORS) if mask & 1<<i)


def independent_spec(name, left, right):
    """Independent integer-bitmask semantics; does not call DSL interpreter."""
    if name not in ORDER or any(type(x) is not int or not 0<=x<=7 for x in (left,right)):
        raise ValueError('unknown independent bitmask target')
    return {
        'KEEP':left, 'GROW':left|right, 'DRAIN':left&(~right&7),
        'REPLACE':right, 'FLIP':left^right,
    }[name]


def candidate_mask(expr, left, right):
    return bitmask(evaluate_macro(expr, color_set(left), color_set(right)))


def info_score(expressions, left, right):
    outputs=Counter(candidate_mask(expr,left,right) for expr in expressions.values())
    total=sum(outputs.values())
    return total*total - sum(c*c for c in outputs.values())


def choose_probe(expressions, seen, suggested=None, mode='adaptive'):
    if mode not in ('adaptive','fixed'):raise ValueError('unsupported test-selection policy')
    possible=[(a,b) for a in range(8) for b in range(8) if (a,b) not in seen]
    if not possible:return None,'EXHAUSTED'
    if mode=='fixed':
        # Strong, task-agnostic predeclared fixed probes, not a deliberately
        # useless 0/0 enumeration. No feedback-adaptive reorder.
        schedule=[(1,1),(0,1),(1,0),(1,2),(3,1),(3,3),(2,3)]
        return next((v for v in schedule if v in possible),possible[0]),'FIXED_PREDECLARED_CONTROL'
    ranks=[(info_score(expressions,a,b), int(a!=0 and b!=0), int((a&b)!=0), -a,-b, (a,b))
           for a,b in possible]
    best=max(ranks)
    if suggested is not None:
        proposed=(bitmask(suggested['on']),bitmask(suggested['toggles']))
        if proposed in possible and info_score(expressions,*proposed)==best[0] and best[0]>0:
            return proposed,'MODEL_TEST_ACCEPTED_INDEPENDENT_UTILITY_CHECK'
    return best[-1], ('MODEL_TEST_DEFERRED_INFORMATIVE_ALTERNATIVE' if suggested is not None
                      else 'DIRECTOR_ACTIVE_INFORMATION_TEST')


def control_trial(target,policy='adaptive'):
    """Matched finite mechanism-search baselines, same first-class oracle budget."""
    if target not in ORDER:raise ValueError('unsupported target')
    alive=dict(PATTERNS);seen=set();trace=[]
    for turn in range(6):
        if len(alive)<=1:break
        probe,why=choose_probe(alive,seen,mode=policy)
        if probe is None:break
        a,b=probe;expected=independent_spec(target,a,b)
        alive={k:v for k,v in alive.items() if candidate_mask(v,a,b)==expected}
        trace.append({'on_mask':a,'toggle_mask':b,'survivors':sorted(alive),'policy':why})
        seen.add(probe)
        if not alive:break
    return {'target':target,'policy':policy,'questions':len(trace),
            'resolved':len(alive)==1 and next(iter(alive))==target,
            'survivors':sorted(alive),'steps':trace}


def compare_controls():
    cases={mode:[control_trial(target,mode) for target in ORDER]
           for mode in ('adaptive','fixed')}
    return {'cases':cases,
            'adaptive':{'resolved':sum(x['resolved'] for x in cases['adaptive']),
                        'total_questions':sum(x['questions'] for x in cases['adaptive'])},
            'fixed':{'resolved':sum(x['resolved'] for x in cases['fixed']),
                     'total_questions':sum(x['questions'] for x in cases['fixed'])},
            'honest_note':'These are five author-designed finite transition families. Not evidence of open-ended algorithm discovery.'}


class ResearchDirector:
    def __init__(self, brief, *, target='FLIP', model=None, max_rounds=5):
        if type(brief) is not str or not 8<=len(brief)<=300:
            raise ValueError('bounded human-readable research brief required')
        if target not in ORDER:raise ValueError('independent task owner must choose known evaluation target')
        if type(max_rounds) is not int or not 1<=max_rounds<=6:
            raise ValueError('research budget must be 1..6 rounds')
        self.brief=brief;self.target=target
        self.model=model if model is not None else TinyResearchModel()
        self.max_rounds=max_rounds

    def run(self, *, audit=AUDIT, stress=STRESS, evaluate_graph=True):
        # Tests received as an argument are owned by the evaluator, never the model.
        universe={k:deepcopy(v) for k,v in PATTERNS.items()};active=deepcopy(universe)
        seen=set();feedback=[];steps=[];proposed_expressions={}
        last_proposal=None;was_found=False
        for round_no in range(1,self.max_rounds+1):
            try:
                raw=self.model.propose(self.brief,tuple(deepcopy(feedback)))
                if raw is None:break
                proposal,suggested=validate_model_reply(raw)
            except Exception as exc:
                steps.append({'round':round_no,'disposition':'HOLD_MODEL_INVALID_OR_UNAVAILABLE',
                              'error_type':type(exc).__name__,'authority':'NONE'})
                break
            expression=proposal['expression']
            name=next((k for k,v in universe.items() if v==expression),None)
            if name is None:
                name='GENERATED_'+str(round_no)
                # At most one extra model-supplied bounded AST per round.
                universe[name]=expression
                active[name]=expression
            proposed_expressions[name]=proposal
            last_proposal=proposal
            if len(active)==1 and name in active:
                was_found=True
                steps.append({'round':round_no,'model_candidate':name,
                    'disposition':'CANDIDATE_MATCHES_PRIOR_DEV_DISCRIMINATION',
                    'authority':'NONE'})
                break
            probe,why=choose_probe(active,seen,suggested)
            if probe is None:
                steps.append({'round':round_no,'model_candidate':name,
                              'disposition':'HOLD_NO_DISCRIMINATING_PROBE','authority':'NONE'})
                break
            a,b=probe;expected=independent_spec(self.target,a,b)
            actual=candidate_mask(expression,a,b)
            active={k:v for k,v in active.items() if candidate_mask(v,a,b)==expected}
            seen.add(probe)
            disposition='SURVIVED_DEV_PROBE' if expected==actual else 'REFUTED_ON_DEV'
            feedback.append({'mechanism':name,'observed_result':actual,'oracle_expected':expected,
                             'disposition':disposition,'on_mask':a,'toggles_mask':b,
                             'surviving_mechanisms':sorted(active)})
            rec={'round':round_no,'model_candidate':name,'model_proposal_digest':digest(proposal),
                 'suggestion_disposition':why,
                 'model_suggested_test':suggested,
                 'director_chosen_test':{'on_mask':a,'toggles_mask':b},
                 'model_candidate_output':actual,'independent_oracle_output':expected,
                 'disposition':disposition,'remaining_mechanisms':sorted(active),
                 'source_graph_modified':False,'authority':'NONE'}
            rec['receipt_digest']=digest(rec);steps.append(rec)
            if len(active)==1 and name in active:
                was_found=True;break
        # Frozen after development; no improvement based on heldout findings.
        surviving=[name for name in active if name in proposed_expressions]
        if len(active)==1 and surviving:
            selected_name=surviving[0];selected=proposed_expressions[selected_name]
        else:
            selected_name=None;selected=None
        exact=0
        if selected is not None:
            exact=sum(candidate_mask(selected['expression'],a,b)==independent_spec(self.target,a,b)
                      for a in range(8) for b in range(8))
        if selected is None:
            status='HOLD_NO_VERIFIED_MODEL_PROPOSAL'
        elif exact!=64:
            status='HOLD_MACRO_COUNTEREXAMPLE'
        else:
            status='CANDIDATE_FOR_TESTING'
        dev=safe=frozen=stress_result=None
        # Graph evaluations are owner-owned, independent from model input; only
        # FLIP has the THOUGHT-017 executable graph/task oracle.
        if status=='CANDIDATE_FOR_TESTING' and evaluate_graph and self.target=='FLIP':
            dev=evaluate_candidate(selected,DEV)
            safe=evaluate_candidate(selected,SAFETY)
            if dev['passed']==dev['total'] and safe['passed']==safe['total']:
                frozen=evaluate_candidate(selected,audit)
                stress_result=evaluate_candidate(selected,stress)
                if frozen['passed']==frozen['total'] and stress_result['passed']==stress_result['total']:
                    status='PATCH_FOR_HUMAN_REVIEW_NOT_INSTALLED'
                else:status='HOLD_INDEPENDENT_AUDIT_FAILURE'
            else:status='HOLD_DEVELOPMENT_OR_SAFETY'
        elif status=='CANDIDATE_FOR_TESTING':
            status='MECHANISM_VERIFIED_ON_FINITE_TRUTH_TABLE_NOT_INSTALLED'
        out={'schema':SCHEMA,'status':status,'research_brief':self.brief,
             'model_kind':getattr(self.model,'kind','UNSPECIFIED_MODEL'),
             'model_calls':len(getattr(self.model,'calls',[])),
             'model_output_grants_authority':False,'selected_mechanism':selected_name,
             'selected_proposal_digest':digest(selected) if selected else None,
             'dev_probe_count':len(seen),'model_feedback_records':len(feedback),
             'steps':steps,'dev_truth_table':{'passed':exact,'total':64} if selected else None,
             'development_graph':{'passed':dev['passed'],'total':dev['total']} if dev else None,
             'safety_graph':{'passed':safe['passed'],'total':safe['total']} if safe else None,
             'frozen_graph_audit':{'passed':frozen['passed'],'total':frozen['total']} if frozen else None,
             'stress_graph_audit':{'passed':stress_result['passed'],'total':stress_result['total']} if stress_result else None,
             'frozen_audit_seen_by_model':False,'audit_inspected_after_selection':frozen is not None,
             'failed_audit_counterexample':frozen['first_failure'] if frozen and frozen['first_failure'] else None,
             'next_research_question':'Can a mechanism generalize to a new state grammar and independently authored test family without increasing false positives?',
             'learned_new_general_algorithm':False,'model_written_python_executed':False,
             'trusted_template_only':True,
             'local_ollama_http_calls':len(getattr(self.model,'calls',[])) if getattr(self.model,'kind',None)=='OPT_IN_LOCAL_GENERATIVE_MODEL' else 0,
             'real_model_identity_verified':False,
             'installed':False,'pen_state':'UNCHANGED','external_authority':'NONE',
             'limitations':'Finite typed macro grammar and author-designed synthetic oracle. NB model ranks familiar templates; generative backend optional. Model cannot self-grade. No proof of novel algorithms or improvement at general development.'}
        out['receipt_digest']=digest(out)
        return out, selected
