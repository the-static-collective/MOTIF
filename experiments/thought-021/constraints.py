"""THOUGHT-021: counterexample-guided candidate generation over real model outputs.

An independent director supplies DEV-only observed transition constraints. This
wrapper never invents a target, changes evaluator output, or executes model code.
It screens candidates against already observed examples before spending further
oracle probes, feeding those same witnessed constraints back to a real LLM.
"""
from __future__ import annotations
import hashlib
import json
import sys
from copy import deepcopy
from pathlib import Path

HERE=Path(__file__).resolve().parent
for name in ('thought-017','thought-018','thought-019','thought-020'):
    p=str(HERE.parent/name)
    if p not in sys.path:sys.path.insert(0,p)
from program import digest
from director import ResearchDirector, candidate_mask
from research_model import validate_model_reply
from critic import dev_only, semantic_signature, CriticError

SCHEMA='motif.thought021.constraint-comparison.v1'
MAX_CALLS=6

class ConstraintError(ValueError):pass

def _bit_rows(on, toggle, observed):
    """Directly encode *one observed* bitwise transition, not a general law."""
    colors=('red','blue','green')
    return tuple({'color':colors[i], 'previous':bool(on & 1<<i),
                  'event':bool(toggle & 1<<i),'observed_next':bool(observed & 1<<i)}
                 for i in range(3))


class WitnessLedger:
    def __init__(self):
        self._pairs={}
        self._records=[]

    @property
    def count(self):return len(self._records)

    def observe(self, fact):
        """Only accept director-created probe receipts passed via dev_only().

        Caller auth is outside this object; no evidence is self-authenticating.
        """
        (rec,)=dev_only([fact])
        a,b,expected=(rec[x] for x in ('on_mask','toggles_mask','oracle_expected'))
        key=(a,b)
        if key in self._pairs:
            if self._pairs[key]!=expected:
                raise ConstraintError('CONTRADICTORY_OBSERVATIONS_HOLD')
            # Repeated observations never become extra independent witnesses.
            return False
        self._pairs[key]=expected
        row={'on_mask':a,'toggles_mask':b,'observed_next_mask':expected,
             'observed_bit_rows':_bit_rows(a,b,expected),
             'source':'INDEPENDENT_DIRECTOR_DEV_PROBE_NOT_GLOBAL_AXIOM',
             'authority':'NONE'}
        row['digest']=digest(row)
        self._records.append(row)
        return True

    def satisfies(self, proposal):
        expr=proposal['expression']
        return all(candidate_mask(expr,a,b)==expected
                   for (a,b),expected in self._pairs.items())

    def violations(self, proposal):
        expr=proposal['expression']
        return [{'on_mask':a,'toggles_mask':b,'observed_next_mask':expected,
                 'proposal_output_mask':candidate_mask(expr,a,b)}
                for (a,b),expected in self._pairs.items()
                if candidate_mask(expr,a,b)!=expected]

    def facts(self):return deepcopy(self._records)

    def feedback_sentence(self):
        """Use witnessed *bit behavior*, not a supplied target expression."""
        if not self._records:return ''
        latest=self._records[-1]
        parts=[]
        for bit in latest['observed_bit_rows']:
            before='ON' if bit['previous'] else 'OFF'
            action='TOGGLED' if bit['event'] else 'UNTOUCHED'
            after='ON' if bit['observed_next'] else 'OFF'
            parts.append(f"{bit['color']} {before}+{action}->{after}")
        return (' DEV observation: '+ '; '.join(parts)+
                '. A replacement MUST satisfy these witnessed outcomes; '
                'do not repeat any candidate that contradicts them.')



class ConstraintGuidedModel:
    """Wrap a real model with a finite inference budget and previously seen constraints.

    comparison mode:
      control: only original DEV feedback (same budget)
      semantic: THOUGHT-020 semantic-refutation veto, no further constraints
      constraint: check *all* witnessed input/output examples, and phrase them
                  as constraints in follow-up model prompt.
    """
    def __init__(self, model, *, mode='constraint', max_calls=3):
        if mode not in ('control','semantic','constraint'):raise ConstraintError('unsupported arm')
        if type(max_calls) is not int or not 1<=max_calls<=MAX_CALLS:
            raise ConstraintError('1..6 model inferences required')
        if not callable(getattr(model,'propose',None)):
            raise ConstraintError('real model proposer interface required')
        self.base=model;self.mode=mode;self.max_calls=max_calls
        self.kind=getattr(model,'kind','UNVERIFIED_MODEL')
        self.ledger=WitnessLedger();self.refuted={}
        self.model_generations=0;self.last_candidate=None
        self._feedback_seen=0;self.notes=[];self.admitted=[]

    @property
    def calls(self):return getattr(self.base,'calls',[])

    def _observe(self, feedback):
        cleaned=dev_only(feedback)
        if len(cleaned)<self._feedback_seen or len(cleaned)>self._feedback_seen+1:
            raise ConstraintError('UNEXPECTED_FEEDBACK_SEQUENCE')
        if len(cleaned)>self._feedback_seen:
            if self.last_candidate is None:
                raise ConstraintError('FEEDBACK_WITHOUT_MODEL_CANDIDATE')
            fact=cleaned[-1]
            self.ledger.observe(fact)
            if fact['disposition']=='REFUTED_ON_DEV':
                sig=semantic_signature(self.last_candidate['mechanism'])
                self.refuted[sig]=deepcopy(fact)
            self._feedback_seen=len(cleaned)
        return cleaned

    def _brief(self, original):
        if type(original) is not str or not 8<=len(original)<=300:
            raise ConstraintError('BOUNDED_RESEARCH_BRIEF_REQUIRED')
        if self.mode=='control' or not self.ledger.count:
            return original
        if self.mode=='semantic':
            last=list(self.refuted.values())[-1:] or []
            more=(f' DEV counterexample: on={last[0]["on_mask"]}, toggles={last[0]["toggles_mask"]}, '
                  f'observed={last[0]["oracle_expected"]}; do not repeat a refuted function.') if last else ''
        else:
            more=self.ledger.feedback_sentence()
        return (original[:95]+more)[:300]

    def propose(self, brief, feedback=()):
        observations=self._observe(feedback)
        if type(brief) is not str or not 8<=len(brief)<=300:
            raise ConstraintError('invalid research brief')
        if self.model_generations>=self.max_calls:return None
        while self.model_generations<self.max_calls:
            # Model-generated JSON is passed unchanged to the source owner gate.
            raw=self.base.propose(self._brief(brief), observations)
            if raw is None:return None
            self.model_generations+=1
            proposal, _=validate_model_reply(raw)
            signature=semantic_signature(proposal)
            violations=self.ledger.violations(proposal)
            if self.mode=='semantic' and signature in self.refuted:
                self.notes.append({'generation':self.model_generations,
                   'disposition':'VETO_REFUTED_SEMANTIC_REPLAY',
                   'candidate_digest':digest(proposal),
                   'oracle_probe_spent':False})
                continue
            if self.mode=='constraint' and violations:
                self.notes.append({'generation':self.model_generations,
                   'disposition':'VETO_CONTRADICTS_WITNESSED_DEV',
                   'candidate_digest':digest(proposal),
                   'violations':violations,'oracle_probe_spent':False})
                continue
            self.last_candidate=deepcopy(raw)
            self.admitted.append({'generation':self.model_generations,
              'candidate_digest':digest(proposal),'semantic_signature':signature,
              'constraints_checked':self.ledger.count,
              'disposition':'ADMITTED_TO_INDEPENDENT_DIRECTOR_PROBE'})
            return raw
        self.notes.append({'generation':self.model_generations,
            'disposition':'HOLD_MODEL_BUDGET_EXHAUSTED','oracle_probe_spent':False})
        return None


def run_arm(model, brief, *, mode='constraint', max_calls=3, graph=True):
    wrapped=ConstraintGuidedModel(model,mode=mode,max_calls=max_calls)
    report, candidate=ResearchDirector(brief,model=wrapped,max_rounds=max_calls).run(evaluate_graph=graph)
    assert report['external_authority']=='NONE' and report['installed'] is False
    result={'schema':'motif.thought021.arm.v1','mode':mode,'status':report['status'],
      'model_kind':wrapped.kind,'model_generations':wrapped.model_generations,
      'director_dev_probes':report['dev_probe_count'],
      'constraint_veto_count':sum(x['disposition']=='VETO_CONTRADICTS_WITNESSED_DEV'
                                  for x in wrapped.notes),
      'semantic_veto_count':sum(x['disposition']=='VETO_REFUTED_SEMANTIC_REPLAY'
                                  for x in wrapped.notes),
      'constraints_observed':wrapped.ledger.count,
      'witnessed_dev_only_constraints':wrapped.ledger.facts(),
      'model_notes':wrapped.notes,'accepted_candidates':wrapped.admitted,
      'model_receipts':deepcopy(wrapped.calls),
      'selected_mechanism':report['selected_mechanism'],
      'director_report':report,'candidate':candidate,
      'model_generated_python_executed':False,'frozen_audit_leaked':False,
      'installed':False,'pen_state':'UNCHANGED','external_authority':'NONE'}
    result['receipt_digest']=digest(result)
    return result


def comparison(model_factory, brief, *, max_calls=3, graph=True, modes=('control','semantic','constraint')):
    if not callable(model_factory):raise ConstraintError('explicit model factory required')
    if type(modes) is not tuple or not modes or len(set(modes))!=len(modes) or set(modes)-{'control','semantic','constraint'}:
        raise ConstraintError('unique known comparison arms required')
    outcomes={m:run_arm(model_factory(),brief,mode=m,max_calls=max_calls,graph=graph)
              for m in modes}
    result={'schema':SCHEMA,'status':'COMPARATIVE_TRIAL_NO_AUTONOMOUS_INSTALL',
      'model_inference_limit_per_arm':max_calls,'same_task_brief':True,
      'runs':outcomes,'unseen_frozen_audit_in_model_prompts':True,
      'comparison_limit':'Same maximum calls, not equal token budget or independent task authors. '
        'Observed constraints come only from previous development probes. '
        'Synthetic tasks and known classical transition grammar; no general algorithm discovery.',
      'external_authority':'NONE','pen_state':'UNCHANGED','installed':False}
    result['receipt_digest']=digest(result)
    return result
