"""THOUGHT-022: matched *oracle-query* trials, not matched compute experiments.

Three strategies: exhaustive finite classical CEGIS; direct local generative LLM
whose only output is a typed DSL AST; and classical-first hybrid using the LLM
ONLY to suggest an uninstalled vocabulary extension after grammar failure.
"""
from __future__ import annotations
from copy import deepcopy
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
for name in ('thought-017','thought-018','thought-019'):
    f=str(HERE.parent/name)
    if f not in sys.path:sys.path.insert(0,f)
from research_model import validate_model_reply
from program import digest
from synth import (TASKS, signature, enumerate_semantics,choose_probe,
                    counterexample_to_current,independent_oracle,classical_cegis)

SCHEMA='motif.thought022.synthesis-race.v1'


def dev_feedback(probe):
    """Existing THOUGHT-019 transport format, with *no* test-set answer labels."""
    return {'mechanism':'UNNAMED_MODEL_CANDIDATE',
            'observed_result':probe['model_predicted'],
            'oracle_expected':probe['observed_mask'],
            'disposition':'REFUTED_ON_DEV' if probe['model_predicted']!=probe['observed_mask'] else 'SURVIVED_DEV_PROBE',
            'on_mask':probe['on_mask'],'toggles_mask':probe['toggle_mask'],
            'surviving_mechanisms':[]}


def llm_cegis(task,model,*,oracle_budget=2,model_budget=3,catalog=None):
    """A true candidate must originate from the proposer, not the synthesizer.

    Classical semantic version space chooses the probes and identifies coverage
    insufficiency. It NEVER supplies its successful expression to this model.
    """
    if task not in TASKS or type(oracle_budget) is not int or not 1<=oracle_budget<=8 or\
        type(model_budget) is not int or not 1<=model_budget<=6:
        raise ValueError('invalid budgets')
    if not callable(getattr(model,'propose',None)):
        raise ValueError('typed LLM proposer required')
    catalog=enumerate_semantics() if catalog is None else catalog
    active=list(catalog); seen=set(); witnessed=[]; receipts=[]; feedback=[]; selected=None;calls=0
    status='HOLD_MODEL_BUDGET_EXHAUSTED'
    for turn in range(model_budget):
        try:
            raw=model.propose(TASKS[task],tuple(deepcopy(feedback)))
            if raw is None:
                status='HOLD_MODEL_REFUSED';break
            prop,_=validate_model_reply(raw)
            expr=prop['expression']; sign=signature(expr)
        except Exception as exc:
            receipts.append({'generation':turn+1,'disposition':'HOLD_INVALID_MODEL_REPLY',
                             'error_type':type(exc).__name__})
            status='HOLD_INVALID_MODEL_REPLY';break
        calls+=1
        row={'generation':turn+1,'proposal_digest':digest(prop),
             'proposal_matches_prior_witnesses':True,'oracle_probed':False}
        mismatch=next(((p['on_mask'],p['toggle_mask'],p['observed_mask'],sign[p['on_mask']*8+p['toggle_mask']])
                       for p in witnessed if sign[p['on_mask']*8+p['toggle_mask']]!=p['observed_mask']),None)
        if mismatch is not None:
            row['proposal_matches_prior_witnesses']=False
            row['disposition']='VETO_CONTRADICTS_PRIOR_DEV'
            receipts.append(row)
            # Previous independent observations already live in feedback;
            # do NOT create another oracle observation or reveal winning AST.
            continue
        if len(active)==1:
            match=next((c for c in active if c['signature']==sign),None)
            if match is not None:
                selected=match;status='REVIEW_MODEL_CANDIDATE_NOT_INSTALLED'
                row['disposition']='MATCHED_UNIQUE_DEV_CANDIDATE'
                receipts.append(row);break
        if len(witnessed)>=oracle_budget:
            row['disposition']='HOLD_ORACLE_BUDGET'
            receipts.append(row)
            status='HOLD_AMBIGUOUS_WITHIN_PROBE_BUDGET';break
        (a,b),choice=counterexample_to_current(task,active,seen)
        expected=independent_oracle(task,a,b)
        prediction=sign[a*8+b]
        before=len(active)
        active=[c for c in active if c['signature'][a*8+b]==expected]
        observed={'on_mask':a,'toggle_mask':b,'observed_mask':expected,
                  'model_predicted':prediction,'selection':choice,
                  'eliminated_semantics':before-len(active),
                  'source':'INDEPENDENT_DEV_ORACLE_NOT_FROZEN_AUDIT'}
        witnessed.append(observed);seen.add((a,b))
        feedback.append(dev_feedback(observed))
        row['oracle_probed']=True
        row['probe']=observed
        row['disposition']='REFUTED_BY_DEV' if prediction!=expected else 'SURVIVED_DEV'
        receipts.append(row)
        if not active:
            status='HOLD_GRAMMAR_INADEQUATE';break
        if len(active)==1 and sign==active[0]['signature']:
            selected=active[0];status='REVIEW_MODEL_CANDIDATE_NOT_INSTALLED';break
    else:
        status='HOLD_MODEL_BUDGET_EXHAUSTED'
    result={'schema':SCHEMA,'arm':'direct_llm','task':task,'status':status,
            'model_call_count':calls,'model_budget':model_budget,
            'independent_oracle_calls':len(witnessed),'oracle_budget':oracle_budget,
            'witnessed_development_probes':witnessed,'model_steps':receipts,
            'version_space_remaining':len(active),
            'model_sourced_final_expression':selected['expression'] if selected else None,
            'model_sourced_final_expression_digest':digest(selected['expression']) if selected else None,
            'audit_evaluated_after_selection':selected is not None,
            'frozen_full_domain_passed':(sum(selected['signature'][a*8+b]==independent_oracle(task,a,b)
                  for a in range(8) for b in range(8)) if selected else None),
            'model_receipts':deepcopy(getattr(model,'calls',[])),
            'model_frozen_test_access':False,'model_wrote_executable_source':False,
            'installed':False,'pen_status':'UNCHANGED','external_authority':'NONE'}
    if result['frozen_full_domain_passed'] is not None and result['frozen_full_domain_passed']!=64:
        result['status']='HOLD_FROZEN_AUDIT_FAILURE'
    result['receipt_digest']=digest(result)
    return result


def hybrid_cegis(task,advisor=None,*,oracle_budget=2,catalog=None):
    """Classical-first, model ONLY on verified grammar inadequacy.

    The advisor may suggest one *review-only* missing concept; it may NOT add
    instructions, extend grammar, execute, alter the oracle or approve itself.
    """
    base=classical_cegis(task,oracle_budget=oracle_budget,catalog=catalog)
    hint=None; advisor_called=False; receipts=[]
    if base['status']=='HOLD_GRAMMAR_INADEQUATE' and advisor is not None:
        try:
            advisor_called=True
            hint=advisor.advise(TASKS[task],base['development_witnesses'])
            if type(hint) is not dict or set(hint)!={'missing_primitive','reason'} or\
                hint['missing_primitive'] not in ('complement','constant_universe','unknown') or\
                type(hint['reason']) is not str or not 8<=len(hint['reason'])<=200:
                hint=None
        except Exception as exc:
            receipts.append({'disposition':'HOLD_ADVISOR_RESPONSE','error_type':type(exc).__name__})
            hint=None
    out={'schema':SCHEMA,'arm':'classical_first_hybrid','task':task,
         'status':'HOLD_GRAMMAR_EXTENSION_REVIEW' if base['status']=='HOLD_GRAMMAR_INADEQUATE' and hint else base['status'],
         'classical_result':base,'advisor_invoked':advisor_called,
         'advisor_recommendation_unverified':hint,'advisor_receipts':receipts,
         'model_receipts':deepcopy(getattr(advisor,'calls',[])) if advisor else [],
         'oracle_budget':oracle_budget,'independent_oracle_calls':base['oracle_calls'],
         'grammar_extended':False,'installed':False,'pen_status':'UNCHANGED','external_authority':'NONE'}
    out['receipt_digest']=digest(out)
    return out


def offline_matrix(tasks=('flip','intersection','drain','replace','invert'),budget=2):
    catalog=enumerate_semantics()
    rows=[classical_cegis(t,oracle_budget=budget,catalog=catalog) for t in tasks]
    return {'schema':'motif.thought022.source-only-baselines.v1',
            'tasks':list(tasks),'grammar_distinct_functions':len(catalog),
            'classical':rows,'oracle_budget_per_task':budget,
            'total_oracle_calls':sum(r['oracle_calls'] for r in rows),
            'solved':sum(r['status']=='REVIEW_CANDIDATE_NOT_INSTALLED' for r in rows),
            'grammar_inadequate':sum(r['status']=='HOLD_GRAMMAR_INADEQUATE' for r in rows),
            'not_external_benchmark':True,'installed':False,'external_authority':'NONE'}
