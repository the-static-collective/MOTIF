"""MOTIF FIELD-017 — bounded, provenance-safe proposal → physical critic → revision.

A *search* over reversible descriptions, not a physics discovery engine.
All material properties, weather, measured clearances, and access permissions
are read-only. The solver may change only the declared design arrangement.

A strong counterexample stops a plan but doesn't overwrite the evidence ledger.
No proposal is an installed object, an authorized action or dog-safe fencing.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict, replace
from hashlib import sha256
from itertools import combinations
import heapq, json, math
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'field016'))
import engine as field016

@dataclass(frozen=True)
class Layout:
    route: str
    pieces: tuple[str, ...]
    operation: str = 'SEED'
    parent: str | None = None

    @property
    def id(self):
        return self.route+'|'+','.join(self.pieces)

@dataclass(frozen=True)
class Assessment:
    layout: Layout
    verdict: str
    failures: tuple[str, ...]
    unknowns: tuple[str, ...]
    effort: int
    wind_force_n: float | None
    score: tuple[int,...]
    source_receipt: str
    physical_safety_verified: bool = False

    def packet(self):
        d=asdict(self)
        d['score']=list(self.score)
        return d

@dataclass(frozen=True)
class Experiment:
    step: int
    candidate: str
    parent: str | None
    operator: str
    verdict: str
    model_failures: tuple[str,...]
    remaining_unknowns: tuple[str,...]
    score: tuple[int,...]
    verdict_changed_from_parent: bool


def canonical_state(scene:field016.Scene):
    scene.validate()
    return sha256(json.dumps(asdict(scene),sort_keys=True,allow_nan=False).encode()).hexdigest()


def _by_id(scene):
    return {p.id:p for p in scene.pieces},{r.id:r for r in scene.routes}


def _assessment(scene:field016.Scene, layout:Layout)->Assessment:
    pieces,routes=_by_id(scene)
    if layout.route not in routes or len(layout.pieces)>3 or not layout.pieces or len(set(layout.pieces))!=len(layout.pieces) or any(p not in pieces for p in layout.pieces):
        raise ValueError('Invalid candidate; cannot synthesize new materials or routes')
    route=routes[layout.route]
    members=tuple(pieces[p] for p in layout.pieces)
    measured_lengths=[p.width_m for p in members]
    unknown=[];fail=[];force=None
    if len(members)>1 and not scene.salvage_connections_available:
        fail.append('CONNECTION_MATERIAL_NOT_AVAILABLE')
    if route.span_m is None or any(x is None for x in measured_lengths):
        unknown.append('MISSING_COVERAGE_DIMENSIONS')
        # We can evaluate the other aspects without asserting that length fits.
        span_flag='HOLD_WIDTH_UNKNOWN' if any(x is None for x in measured_lengths) else 'HOLD_ROUTE_SPAN_UNKNOWN'
    elif sum(measured_lengths)+1e-9<route.span_m:
        fail.append('NOMINAL_COVERAGE_TOO_SHORT')
        span_flag='HOLD_GAP'
    else:
        span_flag='CAN_COVER_SPAN_IN_IDEAL_2D_ONLY'
    # Actual F016/F015 evaluation. No alternate local physics implementation.
    result=field016.evaluate(scene,route,members,span_flag)
    force=result.get('model_wind_force_n')
    if result['status']=='MODEL_FAILS_STATED_SCENARIO':
        fail.append('FIELD016_PHYSICS_OR_CLEARANCE_SCREEN_FAILED')
    unknown+=result['uncertainties']
    if route.retains_access is False:fail.append('USER_MARKED_ACCESS_BLOCKED')
    if route.retains_access is None:unknown.append('ACCESS_NOT_ESTABLISHED')
    # The score is a DECLARED policy, not learned values or a safety rating.
    # Penalize hard failures, then gaps in evidence, then relative effort.
    unknowns=tuple(sorted(set(unknown)))
    failures=tuple(sorted(set(fail)))
    wind_penalty=int(round(force*10)) if force is not None else 100000
    score=(int(bool(failures)),len(failures),len(unknowns),result['estimated_relative_assembly_effort'],wind_penalty)
    verdict='REJECTED_UNDER_STATED_MODEL' if failures else 'CONDITIONAL_HOLD_NOT_CERTIFIED'
    return Assessment(layout,verdict,failures,unknowns,result['estimated_relative_assembly_effort'],force,score,canonical_state(scene))


def neighbors(layout:Layout, scene:field016.Scene):
    """Bounded forward design transformations, no mutation of world measurements."""
    pieces,routes=_by_id(scene)
    for route in routes:
        if route!=layout.route:
            yield Layout(route,layout.pieces,'MOVE_BOUNDARY',layout.id)
    for old in layout.pieces:
        for new in pieces:
            if new not in layout.pieces:
                p=tuple(new if x==old else x for x in layout.pieces)
                yield Layout(layout.route,p,'SUBSTITUTE_MATERIAL',layout.id)
    if len(layout.pieces)<min(3,len(pieces)) and scene.salvage_connections_available:
        for new in pieces:
            if new not in layout.pieces:
                yield Layout(layout.route,layout.pieces+(new,),'COMPOSE_PANELS',layout.id)
    if len(layout.pieces)>1:
        for old in layout.pieces:
            yield Layout(layout.route,tuple(p for p in layout.pieces if p!=old),'REMOVE_REDUNDANT_PIECE',layout.id)


def question_for(scene:field016.Scene, a:Assessment|None)->dict:
    """Direct input surface: choose a source-grounded, decision-sensitive fact.

    A question merely requests information; unanswered questions never fill inputs.
    """
    if a is None:
        return {'kind':'SELECT_SOURCE','question':'Which existing objects and boundary routes are available?', 'can_answer_by':'mark objects or trace the route'}
    ids=a.layout.pieces
    pieces,routes=_by_id(scene)
    route=routes[a.layout.route]
    if route.span_m is None:
        return {'kind':'MEASURE_ROUTE','subject':route.id,'question':'What is the approximate length of this proposed boundary?', 'can_answer_by':'enter length or rough interval'}
    if route.retains_access is None:
        return {'kind':'VERIFY_ACCESS','subject':route.id,'question':'Will this layout preserve the needed human access?', 'can_answer_by':'tap yes/no/unknown on board'}
    for id in ids:
        p=pieces[id]
        if p.width_m is None or not p.measured_width:
            return {'kind':'MEASURE_PIECE','subject':id,'question':f'What is the usable width of {id}?', 'can_answer_by':'enter measured width or a rough range'}
    if any('ground_clearance_unknown' in x for x in a.unknowns):
        return {'kind':'CHECK_GROUND_GAP','subject':ids[0],'question':'How large is the worst ground opening, and where?', 'can_answer_by':'mark the opening in 3D or enter gap'}
    if any('uncharacterized_joints' in x for x in a.unknowns):
        return {'kind':'CHECK_CONNECTION','question':'What would physically prevent this connected assembly from rotating or tipping?', 'can_answer_by':'mark actual support and test a reversible unloaded fit'}
    return {'kind':'VISUAL_PROBE','question':'Inspect stability, sharp edges, openings and real anchors before any animal use.', 'can_answer_by':'source-linked inspection notes'}


def run(scene:field016.Scene, initial:Layout, *, budget=16, beam=0)->dict:
    """Evidence-conserving bounded search; each FIELD-015 physical screen consumes budget.

    A candidate's `score` is available only *after* physically screening it.
    `beam=0`: unbounded queue; >0 retains at most beam successors per
    expansion. The budget counts screened layouts, including rejected ones.
    """
    if type(budget) is not int or not 1<=budget<=250:raise ValueError('budget must be 1..250')
    if type(beam) is not int or not 0<=beam<=100:raise ValueError('beam must be 0..100')
    source=canonical_state(scene)
    first=_assessment(scene,initial)
    frontier=[(first.score,0,0,first)]
    seen={initial.id};evaluated={initial.id:first}
    sequence=0; expanded=0
    trace=[Experiment(1,first.layout.id,None,'SEED',first.verdict,first.failures,
                      first.unknowns,first.score,False)]
    while frontier and len(trace)<budget:
        _,depth,_,now=heapq.heappop(frontier)
        expanded+=1
        candidates=[]
        for layout in neighbors(now.layout,scene):
            if layout.id in seen:continue
            seen.add(layout.id)
            candidates.append(layout)
        # An intentionally cheap proposal ordering: does not call the critic.
        # Prefer first investigating relocation and replacement before adding
        # structurally uncharacterized joins. Not a learned general policy.
        order={'MOVE_BOUNDARY':0,'SUBSTITUTE_MATERIAL':1,
               'COMPOSE_PANELS':2,'REMOVE_REDUNDANT_PIECE':3}
        candidates.sort(key=lambda x:(order.get(x.operation,9), x.id))
        if beam:candidates=candidates[:beam]
        for layout in candidates:
            if len(trace)>=budget:break
            assess=_assessment(scene,layout)
            evaluated[layout.id]=assess
            prior=evaluated[layout.parent]
            changed=assess.verdict!=prior.verdict
            trace.append(Experiment(len(trace)+1,layout.id,layout.parent,layout.operation,
                                    assess.verdict,assess.failures,assess.unknowns,assess.score,changed))
            sequence+=1
            heapq.heappush(frontier,(assess.score,depth+1,sequence,assess))
    selected=min(evaluated.values(),key=lambda x:(x.score,x.layout.id))
    output={
        'experiment':'FIELD-017','search':'budgeted_best_first_repair_with_actual_field015_critic',
        'world_sha256':source,'source_version':scene.revision,
        'budget_evaluations':budget,'evaluated':len(trace),'expanded_parents':expanded,
        'remaining_frontier':len(frontier),'initial':first.packet(),'selected':selected.packet(),
        'improved_declared_score':selected.score<first.score,
        'iterations':[asdict(t) for t in trace],
        'next_input':question_for(scene,selected),
        'physical_actions':0,'real_model_calls':0,'installation_safety_certified':False,
        'pet_containment_certified':False,'site_reconstruction_verified':False,
        'hypothesis_is_not_measured_fact':True,
    }
    output['receipt_sha256']=sha256(json.dumps(output,sort_keys=True).encode()).hexdigest()
    return output

def update_and_repeat(scene:field016.Scene, seed:Layout, observation:field016.Observation, budget=16):
    """Real user evidence changes the world only via F016's guarded input path."""
    before=run(scene,seed,budget=budget)
    after_scene=field016.reenter(scene,observation)
    after=run(after_scene,seed,budget=budget)
    return {'observation':asdict(observation),'before':before,'after':after,
            'world_changed_only_by_event':True,'simulated_actions_added_as_observations':0}


def demonstration():
    scene=field016.invented_scene()
    seed=Layout('original',('privacy',))
    r=run(scene,seed,budget=16)
    measured=field016.Observation('observer-width-1','MEASURED','piece_width','porous',1.32,1)
    return {'first':r,'measured_update':update_and_repeat(scene,seed,measured,budget=16)}

if __name__=='__main__':
    report=demonstration()
    print(json.dumps({'first':{'initial':report['first']['initial']['layout']['id'] if 'id' in report['first']['initial']['layout'] else report['first']['initial']['layout'],
                                'selected':report['first']['selected']['layout'], 'evaluated':report['first']['evaluated'],
                                'next_input':report['first']['next_input']},
                      'second':{'selected':report['measured_update']['after']['selected']['layout'],
                                'next_input':report['measured_update']['after']['next_input']}},indent=2))
