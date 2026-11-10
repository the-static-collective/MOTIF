"""INVENTION-DIAGNOSIS-001: decide WHAT remedy is warranted before self-editing.

A bounded question -> observation -> local action -> independently checked result
controller using REAL existing MOTIF graph and synthesis cartridges. Classification
uses observed symptoms (not the fixture's scenario label). No source edits, remote
systems, hidden labels, untrusted code execution, or general causal diagnosis.
"""
from __future__ import annotations
from collections import Counter
from dataclasses import dataclass, asdict
from hashlib import sha256
from itertools import product
from math import log2
from pathlib import Path
from typing import Any
import json
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]
for folder in ('operatorinvention001','controlflow001','languagegrowth001','contractfrontier002','mathal001'):
    p=str(ROOT/folder)
    if p not in sys.path:sys.path.insert(0,p)
from operatorinvention import PROGRAMS as OLD_PROGRAMS, Program as OldProgram
from languagegrowth import Experiment, trials
from contractfrontier import observed_outcome
from controlflow import (outcome as five_cycle_outcome, strong_baseline, discover as grow_control,
                         audit as audit_growth, build_child as build_control_child,
                         run_child as run_control_child)


class DiagnosisRefusal(ValueError):
    pass


TASKS=frozenset({'triangles','five_cycles'})
COSTS={'CROSSCHECK':1,'PROBE_DISAGREEMENT':1,'VALIDATE_MODEL':1,'RAISE_FUEL':2,'GROW_CONTROL_FLOW':4}


@dataclass(frozen=True)
class Reading:
    case: Experiment
    primary: int|None
    corroborator: int|None
    status: str = 'COMPLETE'
    primary_root: str = 'first-graph-implementation'
    corroborator_root: str = 'second-graph-implementation'
    shared_graph_source: bool = True
    fuel_used: int = 0
    work_required: int = 0

    def __post_init__(self):
        if self.status not in {'COMPLETE','TRUNCATED'} or not self.primary_root or not self.corroborator_root:
            raise DiagnosisRefusal('HOLD_BAD_READING_STATUS')
        if self.status=='COMPLETE' and (type(self.primary) is not int or type(self.corroborator) is not int):
            raise DiagnosisRefusal('HOLD_INCOMPLETE_MEASUREMENT')
        if self.status=='TRUNCATED' and (self.primary is not None or self.corroborator is not None or
                                           type(self.fuel_used) is not int or type(self.work_required) is not int or
                                           self.fuel_used<0 or self.work_required<=self.fuel_used):
            raise DiagnosisRefusal('HOLD_FALSE_RESOURCE_MARKER')


@dataclass(frozen=True)
class Request:
    question: str
    budget: int = 8
    max_steps: int = 5
    task_contract_warranted: bool = True  # declared fixture condition, NOT external attestation
    allow_more_evidence: bool = True
    allow_grammar_expansion: bool = True
    allow_more_compute: bool = True
    max_fuel: int = 1024

    def __post_init__(self):
        if (self.question not in TASKS or type(self.budget) is not int or self.budget<0
                or type(self.max_steps) is not int or not 1<=self.max_steps<=8
                or type(self.max_fuel) is not int or self.max_fuel<1
                or any(type(x) is not bool for x in (self.task_contract_warranted,self.allow_more_evidence,
                                                    self.allow_grammar_expansion,self.allow_more_compute))):
            raise DiagnosisRefusal('HOLD_UNLICENSED_REQUEST')


@dataclass(frozen=True)
class Context:
    request: Request
    evidence: tuple[Reading,...]
    candidate_probes: tuple[Experiment,...]
    # An existing, already-implemented operator can be re-executed with more fuel.
    # This is an observed runtime resource failure, not model invention.
    installed_program: OldProgram|None = None

    def __post_init__(self):
        keys=[r.case.key for r in self.evidence]+[c.key for c in self.candidate_probes]
        if not self.evidence or len(keys)!=len(set(keys)):
            raise DiagnosisRefusal('HOLD_DUPLICATE_OR_MISSING_EVIDENCE')
        if any(e.case.split!='train' for e in self.evidence) or any(e.split!='train' for e in self.candidate_probes):
            raise DiagnosisRefusal('HOLD_SPLIT_ORIGIN')
        if self.installed_program is not None and self.installed_program not in OLD_PROGRAMS:
            raise DiagnosisRefusal('HOLD_UNDECLARED_INSTALLED_PROGRAM')


def fingerprint(ctx:Context)->str:
    """Reproducibility digest, NOT authentication of graph evidence."""
    snapshot=[(r.case.key,repr(r.case.probe.graph),r.primary,r.corroborator,
               r.status,r.primary_root,r.corroborator_root,r.fuel_used,r.work_required)
              for r in ctx.evidence]
    return sha256(json.dumps(snapshot,sort_keys=True).encode()).hexdigest()[:24]


def primary_observation(case:Experiment,question:str)->int:
    if question=='triangles':return observed_outcome(case.probe)[0]
    if question=='five_cycles':return five_cycle_outcome(case)
    raise DiagnosisRefusal('HOLD_UNKNOWN_ORACLE')


def second_observation(case:Experiment,question:str)->int:
    graph=case.probe.graph
    if question=='triangles':
        a,b=case.probe.a,case.probe.b
        neighborhood_a={v if u==a else u for u,v in graph.edges if a in (u,v)}
        neighborhood_b={v if u==b else u for u,v in graph.edges if b in (u,v)}
        return len(neighborhood_a & neighborhood_b)
    if question=='five_cycles':return strong_baseline(case.probe)
    raise DiagnosisRefusal('HOLD_UNKNOWN_ORACLE')


def observe(case:Experiment,question:str,*,tamper_primary:int=0,tamper_secondary:int=0,
            primary_root:str='first-graph-implementation',
            corroborator_root:str='second-graph-implementation')->Reading:
    if type(tamper_primary) is not int or type(tamper_secondary) is not int:
        raise DiagnosisRefusal('HOLD_BAD_TAMPER_FIXTURE')
    return Reading(case,primary_observation(case,question)+tamper_primary,
                   second_observation(case,question)+tamper_secondary,
                   primary_root=primary_root,corroborator_root=corroborator_root)


def metered(program:OldProgram,case:Experiment,fuel:int)->dict:
    """Actual bounded interpretation; a partial count is NEVER an answer."""
    if program not in OLD_PROGRAMS or type(fuel) is not int or fuel<0:
        raise DiagnosisRefusal('HOLD_INVALID_PROGRAM_OR_FUEL')
    g=case.probe.graph
    variables=program.binders
    assignments=product(sorted(g.vertices),repeat=len(variables))
    count=0;seen=0
    for values in assignments:
        if seen>=fuel:
            return {'status':'TRUNCATED','answer':None,'inspected':seen,
                    'needed':len(g.vertices)**len(variables)}
        seen+=1
        if program.distinct and values[0]==values[-1]:continue
        env={'a':case.probe.a,'b':case.probe.b}
        env.update(zip(variables,values))
        if all(env[u]!=env[v] and tuple(sorted((env[u],env[v]))) in g.edges for u,v in program.atoms):
            count+=1
    return {'status':'COMPLETE','answer':count,'inspected':seen,'needed':seen}


def resource_reading(case:Experiment,program:OldProgram,fuel:int)->Reading:
    result=metered(program,case,fuel)
    if result['status']!='TRUNCATED':
        raise DiagnosisRefusal('HOLD_NOT_A_RESOURCE_FAILURE')
    return Reading(case,None,None,'TRUNCATED',fuel_used=fuel,work_required=result['needed'])


def candidates(evidence:tuple[Reading,...])->tuple[OldProgram,...]:
    """Existing grammar version space; never silently promote a model to fact."""
    viable=list(OLD_PROGRAMS)
    for record in evidence:
        if record.status!='COMPLETE' or record.primary!=record.corroborator:
            raise DiagnosisRefusal('HOLD_UNRELIABLE_TRAINING_READING')
        viable=[p for p in viable if p.interpret(record.case.probe)==record.primary]
    return tuple(viable)


def entropy(values)->float:
    freq=Counter(values)
    n=sum(freq.values())
    return -sum((q/n)*log2(q/n) for q in freq.values()) if n else 0.0


def choose_inquiry(unseen:tuple[Experiment,...],models:tuple[OldProgram,...])->tuple[Experiment|None,float]:
    if not unseen or not models:return None,0.0
    scored=[(entropy(p.interpret(item.probe) for p in models),item.key,item) for item in unseen]
    information,key,probe=min(scored,key=lambda row:(-row[0],row[1]))
    return probe,information


def _step(steps:list[dict],question:str,action:str,output:dict,spent:int,remaining:int):
    steps.append({'next_question':question,'action_executed':action,'result':output,
                  'cost':spent,'budget_remaining':remaining,
                  'scope':'LOCAL_SYNTHETIC_READ_ONLY', 'external_effects':0})


def advance(ctx:Context)->dict:
    """Do the next warranted local action and exhibit receipts. No hidden cause tags.

    Order matters: provenance/measurement conflicts, then explicit truncation,
    then evidence sufficiency, and only then language growth. This is a finite
    policy, not a learned general-purpose diagnostic model.
    """
    goal=ctx.request
    before=fingerprint(ctx)
    states=list(ctx.evidence)
    remaining=list(ctx.candidate_probes)
    steps:list[dict]=[]
    spent=0
    provenance={'algorithms_are_distinct':all(r.primary_root!=r.corroborator_root for r in states),
                'shared_underlying_graph':True,
                'source_authenticity_verified':False,'independent_physical_truth':False}
    def affordable(name:str)->bool:
        return spent+COSTS[name]<=goal.budget and len(steps)<goal.max_steps
    def record(name:str,question:str,result:dict)->bool:
        nonlocal spent
        if not affordable(name):return False
        spent+=COSTS[name]
        _step(steps,question,name,result,COSTS[name],goal.budget-spent)
        return True
    def report(status:str,reason:str,next_question:str,**kwargs)->dict:
        return {'experiment':'INVENTION-DIAGNOSIS-001','status':status,'reason':reason,
                'question':goal.question,'next_question':next_question,
                'steps':steps,'budget_spent':spent,'budget_remaining':goal.budget-spent,
                'initial_evidence_count':len(ctx.evidence),'final_evidence_count':len(states),
                'original_evidence_unchanged':fingerprint(ctx)==before,
                'provenance':provenance,'external_actions':0,
                'repository_edits':0,'general_diagnostic_accuracy_proved':False,**kwargs}
    if not goal.task_contract_warranted:
        return report('HOLD_UNWARRANTED_TASK_CONTRACT',
                      'User goal and measurement semantics lack a declared warrant.',
                      'What independently establishes what quantity the answer is supposed to measure?')
    # One known origin is not two independent witnesses, even when repeated.
    if any(r.primary_root==r.corroborator_root for r in states):
        return report('HOLD_SHARED_WITNESS_ROOT',
                      'Two apparent readings have the same declared upstream source.',
                      'Can we obtain differently sourced measurement evidence?')
    if any(r.status=='COMPLETE' and r.primary!=r.corroborator for r in states):
        if not record('CROSSCHECK','Do the separately implemented measurements agree?',
                      {'conflicts':sum(r.status=='COMPLETE' and r.primary!=r.corroborator for r in states),
                       'attribution':'UNRESOLVED','source_authenticity_verified':False}):
            return report('HOLD_BUDGET','Cannot afford even a witness crosscheck.',
                          'Who can verify the disagreement?')
        return report('HOLD_WITNESS_DISAGREEMENT',
                      'Conflicting synthetic implementations do not identify which is correct.',
                      'Can an independently grounded measurement resolve the conflict?',
                      false_grammar_edit_avoided=True)
    incomplete=[r for r in states if r.status=='TRUNCATED']
    if incomplete:
        if len(incomplete)!=len(states) or len(incomplete)!=1 or ctx.installed_program is None:
            return report('HOLD_MIXED_OR_UNKNOWN_RESOURCE_REPORT',
                          'A truncated computation lacks a known installed program.',
                          'Can the observed budget exhaustion be reproduced?')
        entry=incomplete[0]
        if (not goal.allow_more_compute or entry.work_required>goal.max_fuel):
            return report('HOLD_RESOURCE_BOUND',
                          'The existing computation exceeded the permitted fuel.',
                          'Can resources be increased within the authorized limit?',
                          required_fuel=entry.work_required)
        if not affordable('RAISE_FUEL'):
            return report('HOLD_BUDGET','Resource retry is not affordable.',
                          'Should a bounded compute retry be authorized?')
        original_attempt=metered(ctx.installed_program,entry.case,entry.fuel_used)
        if (original_attempt['status']!='TRUNCATED' or
                original_attempt['needed']!=entry.work_required):
            return report('HOLD_RESOURCE_MARKER_UNCONFIRMED',
                          'The declared incomplete-computation receipt failed reproduction.',
                          'Is this a real computation limit or corrupted measurement?')
        result=metered(ctx.installed_program,entry.case,entry.work_required)
        if result['status']!='COMPLETE':
            return report('HOLD_RESOURCE_RETRY_FAILED',
                          'The authorized rerun did not finish.',
                          'Is there a lower-cost algorithm?')
        observed=primary_observation(entry.case,goal.question)
        corroborated=second_observation(entry.case,goal.question)
        record('RAISE_FUEL','Can the installed program answer with an authorized compute increase?',
               {'initial_fuel':entry.fuel_used,'new_fuel':result['inspected'],
                'completed_result':result['answer'],'instrument':observed,
                'corroborator':corroborated,'outcome_reliable_under_model':result['answer']==observed==corroborated})
        if result['answer']!=observed or result['answer']!=corroborated:
            return report('HOLD_RESOURCE_RETRY_DISAGREEMENT',
                          'Completion did not make the answer correct.',
                          'Which implementation or premise is wrong?')
        return report('SOLVED_BOUNDED_COMPUTE',
                      'Same installed operator succeeded after bounded resource adjustment.',
                      'Does the method remain reliable under larger inputs?',
                      verified_output=result['answer'],grammar_changed=False)
    if not states or not all(r.status=='COMPLETE' for r in states):
        return report('HOLD_NO_COMPLETE_EVIDENCE','No complete model-checkable observations.',
                      'Which bounded observation can be completed first?')
    versions=candidates(tuple(states))
    first_count=len(versions)
    if versions:
        while len(versions)>1:
            best,gain=choose_inquiry(tuple(remaining),versions)
            if best is None or gain<=1e-12:
                return report('HOLD_OBSERVATIONALLY_EQUIVALENT',
                              'Existing explanations make the same predictions on permitted remaining probes.',
                              'What new intervention would separate the explanations?',
                              surviving_models=len(versions))
            if not goal.allow_more_evidence or not affordable('PROBE_DISAGREEMENT'):
                return report('HOLD_MORE_EVIDENCE_REQUIRED',
                              'Existing grammar remains viable, but observed evidence is insufficient.',
                              'Which affordable experiment best separates the remaining models?',
                              surviving_models=len(versions),best_proposal=best.key,
                              expected_disagreement_bits=gain)
            reading=observe(best,goal.question)
            if reading.primary!=reading.corroborator:
                return report('HOLD_NEW_SENSOR_CONFLICT',
                              'Proposed follow-up uncovered disagreement.',
                              'Which observation can independently resolve it?')
            versions=tuple(v for v in versions if v.interpret(best.probe)==reading.primary)
            states.append(reading);remaining.remove(best)
            record('PROBE_DISAGREEMENT','Which affordable observation best reduces the current explanation ambiguity?',
                   {'probe':best.key,'information_bits_before_query':gain,
                    'observed':reading.primary,'models_after':len(versions),
                    'source_authenticity_verified':False})
            if not versions:
                return report('HOLD_FALSIFIED_AFTER_NEW_PROBE',
                              'Previously viable grammar no longer explains observed measurements.',
                              'Are the measurements stable, or must the model grammar change?')
        if not affordable('VALIDATE_MODEL'):
            return report('HOLD_VALIDATION_BUDGET',
                          'A candidate model exists but cannot be checked on fresh data.',
                          'Can a held-out check be performed?')
        winner=versions[0]
        fresh=trials('validation',16)
        failures=[]
        for item in fresh:
            actual=primary_observation(item,goal.question)
            cross=second_observation(item,goal.question)
            if winner.interpret(item.probe)!=actual or actual!=cross:
                failures.append(item.key)
        record('VALIDATE_MODEL','Does the frozen existing model survive new simulated graph inputs?',
               {'cases':len(fresh),'counterexamples':len(failures),'failures':failures[:5],
                'model':winner.name(),'finite_only':True})
        if failures:
            return report('HOLD_VALIDATION_COUNTEREXAMPLE',
                          'A fitting model failed a separate synthetic fixture split.',
                          'Is the source instrument wrong or the model insufficient?')
        return report('SOLVED_EXISTING_REPERTOIRE',
                      'Additional evidence selected an existing validated finite model.',
                      'Would a new domain or external witness falsify this model?',
                      verified_model=winner.name(),additional_probes=len(states)-len(ctx.evidence),
                      grammar_changed=False,starting_models=first_count)
    # MODEL GAP is a conditional inference after a complete finite model search,
    # not a proof that the world or interpreter is wrong.
    if goal.question!='five_cycles' or not goal.allow_grammar_expansion:
        return report('HOLD_UNSUPPORTED_REMEDY',
                      'Known grammar is falsified, but no permitted verified repair applies.',
                      'Is an alternative representation or a new instrument justified?',
                      starting_models=first_count)
    if not affordable('GROW_CONTROL_FLOW'):
        return report('HOLD_GROWTH_NOT_AFFORDABLE',
                      'A model-gap hypothesis cannot authorize expensive grammar work.',
                      'Should a bounded local grammar-extension experiment be approved?')
    grown=grow_control(trials('train',36),trials('validation',24),budget=3)
    exact=all(grown.usable and grown.program.interpret(x.case.probe)==x.primary for x in states)
    tested=audit_growth(grown,trials('test',10)) if grown.usable else {'status':'HOLD_NO_GROWTH'}
    ood=audit_growth(grown,trials('ood',8)) if grown.usable else {'status':'HOLD_NO_GROWTH'}
    child={'status':'HOLD_NOT_BUILT'}
    if grown.usable and exact and tested.get('status')=='F_LOCAL_FINITE_REPLAY' and ood.get('status')=='F_LOCAL_FINITE_REPLAY':
        with tempfile.TemporaryDirectory(prefix='motif-invention-diagnosis-') as temporary:
            generated=build_control_child(ROOT,Path(temporary),grown)
            child=run_control_child(generated,ROOT,index=4)
    record('GROW_CONTROL_FLOW','Does an actual new control-flow composition solve the demonstrated model gap?',
           {'new_search_status':grown.status,'candidate_programs':grown.total_candidates,
            'new_training_probes':grown.probes,'preserves_existing_evidence':exact,
            'heldout':tested,'ood':ood,'generated_child':child,
            'new_code_installed':False,'new_authority_granted':False})
    if (not grown.usable or not exact or tested.get('status')!='F_LOCAL_FINITE_REPLAY'
            or ood.get('status')!='F_LOCAL_FINITE_REPLAY'
            or child.get('status')!='F_LOCAL_CHILD_REPLAY'):
        return report('HOLD_GROWTH_UNVERIFIED',
                      'Extension failed or conflicted with an observation; do not retain.',
                      'Which counterexample explains the failed extension?')
    return report('SOLVED_STAGED_CONTROL_FLOW_EXTENSION',
                  'New control-flow model passed finite replay and is proposed, not installed.',
                  'Would the new operation help across independently authored task families?',
                  proposed_program=grown.program.signature(),grammar_changed_in_stage=True,
                  installed_in_running_motif=False,starting_models=first_count)


# Test scenarios are authored outside advance(): it receives only symptoms,
# grants, and graph observations. Scenario names are not included in Context.
def scenario(kind:str,seed:int=0)->Context:
    if type(seed) is not int or not 0<=seed<=20:
        raise DiagnosisRefusal('HOLD_FIXTURE_SEED')
    train=trials('train',36)
    triangle=next(p for p in OLD_PROGRAMS if p.binders==('x',)
                  and p.atoms==( ('a','x'), ('b','x')) and not p.distinct)
    if kind=='more_evidence':
        first=seed%4
        start=observe(train[first],'triangles')
        return Context(Request('triangles',budget=5), (start,), tuple(t for i,t in enumerate(train) if i!=first))
    if kind=='missing_control':
        # Observe a small diverse prefix until every old program contradicts.
        data=[];survivors=tuple(OLD_PROGRAMS)
        rotated=train[seed:]+train[:seed]
        for p in rotated:
            reading=observe(p,'five_cycles')
            data.append(reading)
            survivors=tuple(x for x in survivors if x.interpret(p.probe)==reading.primary)
            if not survivors:break
        seen={r.case.key for r in data}
        return Context(Request('five_cycles',budget=5),tuple(data),tuple(t for t in train if t.key not in seen))
    if kind=='corrupt_sensor':
        return Context(Request('triangles',budget=5),
                       (observe(train[4+seed],'triangles',tamper_primary=1),),tuple(train[15:]))
    if kind=='resource_cap':
        p=train[4+seed]
        return Context(Request('triangles',budget=3,max_fuel=64),
                       (resource_reading(p,triangle,1),),tuple(train[15:]),triangle)
    if kind=='compute_denied':
        ctx=scenario('resource_cap',seed)
        return Context(Request('triangles',budget=3,max_fuel=2),ctx.evidence,ctx.candidate_probes,ctx.installed_program)
    if kind=='ambiguous_sources':
        return Context(Request('triangles',budget=5),
                       (observe(train[4+seed],'triangles',primary_root='same',corroborator_root='same'),),
                       tuple(train[15:]))
    if kind=='unwarranted_contract':
        return Context(Request('five_cycles',budget=5,task_contract_warranted=False),
                       (observe(train[4+seed],'five_cycles'),),tuple(train[15:]))
    if kind=='unaffordable_growth':
        ctx=scenario('missing_control')
        return Context(Request('five_cycles',budget=3),ctx.evidence,ctx.candidate_probes)
    if kind=='denied_evidence':
        ctx=scenario('more_evidence')
        return Context(Request('triangles',allow_more_evidence=False),ctx.evidence,ctx.candidate_probes)
    if kind=='denied_growth':
        ctx=scenario('missing_control')
        return Context(Request('five_cycles',allow_grammar_expansion=False),ctx.evidence,ctx.candidate_probes)
    if kind=='colluding_readouts':
        # Negative control: BOTH local implementations falsified in the same way;
        # their agreement is not a guarantee of independence or truth.
        p=train[4+seed]
        reading=observe(p,'triangles',tamper_primary=1,tamper_secondary=1)
        return Context(Request('triangles',budget=5), (reading,), tuple(train[15:]))
    raise DiagnosisRefusal('HOLD_UNKNOWN_FIXTURE')


def demonstration()->dict:
    results={}
    for kind in ('more_evidence','missing_control','corrupt_sensor','resource_cap',
                 'compute_denied','ambiguous_sources','unwarranted_contract'):
        output=advance(scenario(kind))
        results[kind]={'status':output['status'],'spent':output['budget_spent'],
                       'questions':tuple(s['next_question'] for s in output['steps']),
                       'actions':tuple(s['action_executed'] for s in output['steps']),
                       'next_question':output['next_question']}
    return {'experiment':'INVENTION-DIAGNOSIS-001',
            'scope':'controlled local graph fixtures; simple diagnostic policy, not general causal intelligence',
            'diagnostic_paths':results,'automatic_external_actions':0,
            'code_deployed':False,'next_frontier':'Blind trials using independent problem families and unfamiliar kinds of failures.'}


if __name__=='__main__':print(json.dumps(demonstration(),indent=2,sort_keys=True))
