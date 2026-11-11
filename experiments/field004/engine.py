"""FIELD-004: Autonomous reframe from sparse, attributed visual observations.

Bounded, rule-guided material-function planner. Proposes candidate transformations,
not structural certification, consent, or actual animal containment.
No external effects. Images require a separate perception adapter.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
from typing import Any

VALID_KIND = frozenset({
    'GOAL_BOUNDARY', 'TARGET_ROUTE', 'EXISTING_BARRIER', 'RIGID_PANEL',
    'FLEXIBLE_MESH', 'ANCHOR_CANDIDATE', 'STRUCTURE', 'CONNECTOR',
    'ACCESS_ROUTE', 'HAZARD', 'BEHAVIOR', 'OTHER',
})
VALID_STATUS = frozenset({'PHOTO_OBSERVED', 'SKETCH_LABELED', 'USER_REPORTED',
                          'MODEL_TENTATIVE'})
VALID_STATE = frozenset({'YES','NO','UNKNOWN'})


@dataclass(frozen=True)
class Observation:
    id: str
    kind: str
    subject: str
    status: str
    source: str
    detail: str = ''

    def check(self):
        if not all(isinstance(v, str) and v.strip() for v in (
                self.id, self.subject, self.status, self.source)):
            raise ValueError('observation missing stable ID, subject, status or source')
        if self.kind not in VALID_KIND or self.status not in VALID_STATUS:
            raise ValueError('unrecognized observation type or evidence status')
        if len(self.detail) > 1000 or len(self.subject) > 180:
            raise ValueError('observation too long')


@dataclass(frozen=True)
class Input:
    goal: str
    observations: tuple[Observation, ...]
    permission_to_relocate: str = 'UNKNOWN'
    joiners_available: str = 'UNKNOWN'
    support_stability_verified: str = 'UNKNOWN'
    safe_pet_clearance_verified: str = 'UNKNOWN'
    critical_exit_closed_verified: str = 'UNKNOWN'

    def check(self):
        if not self.goal or len(self.goal) > 2000 or len(self.observations) > 100:
            raise ValueError('invalid goal or evidence volume')
        ids = [o.id for o in self.observations]
        if len(ids) != len(set(ids)):
            raise ValueError('duplicate evidence ID')
        for o in self.observations:
            o.check()
        for field in ('permission_to_relocate','joiners_available',
                      'support_stability_verified','safe_pet_clearance_verified',
                      'critical_exit_closed_verified'):
            if getattr(self, field) not in VALID_STATE:
                raise ValueError('invalid ternary flag: ' + field)


@dataclass(frozen=True)
class Inference:
    id: str
    proposal: str
    witness_ids: tuple[str, ...]
    prerequisites: tuple[str, ...]
    principle: str
    status: str = 'HYPOTHESIS_NOT_OBSERVATION'


@dataclass(frozen=True)
class Strategy:
    id: str
    label: str
    relies_on: tuple[str, ...]
    missing_checks: tuple[str, ...]
    distinguishing_advantage: str
    cost_class: str
    safety_status: str = 'NOT_VERIFIED_FOR_PET_USE'


@dataclass(frozen=True)
class Probe:
    id: str
    question: str
    distinguishes: tuple[str, ...]
    next_test: str
    priority: int
    effort: int
    unresolved: bool
    reason: str


def evidence_for(inp: Input, *kinds: str) -> tuple[Observation, ...]:
    return tuple(o for o in inp.observations if o.kind in kinds)


def refs(inp: Input, *kinds: str) -> tuple[str, ...]:
    return tuple(o.id for o in evidence_for(inp, *kinds))


def infer(inp: Input) -> tuple[Inference, ...]:
    """Seeded transformation rules, NOT a learned general world model."""
    inp.check()
    goals = evidence_for(inp, 'GOAL_BOUNDARY')
    boundaries = evidence_for(inp, 'EXISTING_BARRIER')
    targets = evidence_for(inp, 'TARGET_ROUTE')
    panels = evidence_for(inp, 'RIGID_PANEL')
    supports = evidence_for(inp, 'ANCHOR_CANDIDATE','STRUCTURE')
    joiners = evidence_for(inp, 'CONNECTOR')
    results = []
    def add(code, proposal, witness, prereq, principle):
        if witness:
            results.append(Inference(code, proposal, tuple(witness), tuple(prereq), principle))
    if goals and targets:
        add('reframe_target',
            'Treat marked/dotted proposed boundary as the goal; treat existing lines as evidence and possible resources, not immutable instructions.',
            refs(inp,'GOAL_BOUNDARY','TARGET_ROUTE'),
            ('verify markings indicate intended boundary rather than another annotation',),
            'goal_geometry_separate_from_current_geometry')
    if goals and boundaries:
        add('relocate_installed',
            'Explore moving or recombining an installed fence section as material to reach the desired boundary.',
            refs(inp,'GOAL_BOUNDARY','EXISTING_BARRIER'),
            ('owner permission and section detachability','structural condition after relocation'),
            'role_reassignment_and_counterfactual_reconfiguration')
        add('shorten_route',
            'Explore moving the boundary to take advantage of existing barriers and reduce new unsupported span.',
            refs(inp,'GOAL_BOUNDARY','EXISTING_BARRIER'),
            ('confirm allowed dog area and access paths',),
            'change_environment_before_building_more')
    if goals and panels:
        add('repurpose_panels',
            'Consider wire/cage/other rigid panels as boundary components irrespective of original product category.',
            refs(inp,'GOAL_BOUNDARY','RIGID_PANEL'),
            ('measure dimensions and openings','inspect dangerous edges and animal clearance'),
            'function_over_original_label')
    if goals and panels and supports:
        add('opportunistic_support',
            'Explore rigid objects or existing frames as potential support nodes for repositioned panels, subject to load and tipping checks.',
            refs(inp,'GOAL_BOUNDARY','RIGID_PANEL','ANCHOR_CANDIDATE','STRUCTURE'),
            ('verify anchor will not move, fail, or damage a person/animal',),
            'support_from_environment_not_only_new_posts')
    if goals and len(panels) >= 1:
        add('network_support',
            'Consider joining panels into a corner/braced network: load-sharing is a hypothesis, not guaranteed by connections.',
            refs(inp,'GOAL_BOUNDARY','RIGID_PANEL','CONNECTOR'),
            ('determine connector availability','verify joint behavior and anti-tip support'),
            'emergent_function_of_assembly')
    if goals and not joiners:
        add('invent_join_step',
            'Search for an inexpensive reversible joiner (ties/clamps/approved hardware) as a prerequisite rather than assuming each panel stands alone.',
            refs(inp,'GOAL_BOUNDARY','RIGID_PANEL'),
            ('actual connector availability and suitability unverified',),
            'invent_missing_joining_affordance')
    if goals and evidence_for(inp,'FLEXIBLE_MESH'):
        add('mesh_as_secondary',
            'Keep loose mesh out of direct dog contact; consider only in a separate, reviewed and properly framed design.',
            refs(inp,'GOAL_BOUNDARY','FLEXIBLE_MESH'),
            ('entanglement and edge assessment',),
            'prevent_bad_functional_transfer')
    return tuple(results)


def make_strategies(inp: Input, ideas: tuple[Inference,...]) -> tuple[Strategy,...]:
    have = {i.id for i in ideas}
    out = []
    def put(id, label, depends, checks, edge, cost):
        if set(depends).issubset(have):
            out.append(Strategy(id,label,tuple(depends),tuple(checks),edge,cost))
    put('recompose_perimeter','Recompose movable installed fence along marked route',
        ('reframe_target','relocate_installed'),
        ('relocation permission','physical detachability','real segment lengths','ground-level gaps','access and dog escape checks'),
        'may reuse long existing spans rather than buying new fencing','MEDIUM')
    put('short_boundary','Shift to a shorter boundary using existing structures',
        ('shorten_route',),
        ('human access','dog area approval','continuous no-go line','unsecured exits'),
        'can make an easier problem by moving the problem boundary','LOW')
    put('panel_cluster','Assemble short rigid panel clusters with opportunistic supports',
        ('repurpose_panels','opportunistic_support','network_support'),
        ('joiner availability','joint and tip stability','sharp edges','animal-size apertures','anchor loads'),
        'joined cluster may have useful geometry even if individual pieces do not stand alone','MEDIUM')
    put('rigid_connectors','Use salvaged rigid panels for short closures between verified fixed ends',
        ('repurpose_panels',),
        ('two secure endpoints','opening length and ground profile','human passage','dog clearance'),
        'smallest high-value closure instead of all-new perimeter','LOW')
    return tuple(out)


def probes(inp: Input, ideas: tuple[Inference,...], strategies:tuple[Strategy,...]) -> tuple[Probe,...]:
    ids = {s.id for s in strategies}
    options = [
        Probe('target_meaning','Do marks/dotted lines designate the intended new boundary?',
              ('recompose_perimeter','short_boundary'),
              'Compare sketch markings with a walk-through of the intended dog zone.',95,1,
              bool(evidence_for(inp,'TARGET_ROUTE')),
              'Target geometry determines which solution is even relevant.'),
        Probe('traffic_exit','Could the current or proposed dog area connect to street/driveway through a gap?',
              tuple(ids),
              'Trace each possible route without dogs; treat uncertain openings as not contained.',100,1,
              inp.critical_exit_closed_verified!='YES',
              'Critical exposure can invalidate all layouts irrespective of material savings.'),
        Probe('movability','Are some of the standing fence sections permitted and practically movable?',
              ('recompose_perimeter',),
              'Inspect how one section is mounted without dismantling anything.',90,1,
              inp.permission_to_relocate=='UNKNOWN',
              'One answer opens or removes an entire resource-reuse branch.'),
        Probe('joiners','Are suitable removable connectors available, such as outdoor-rated ties or clamps?',
              ('panel_cluster',),
              'Inspect current hardware supply; inspect tie rating and application limitations.',82,1,
              inp.joiners_available=='UNKNOWN',
              'Enables new assembly operators; connector tensile rating alone proves no frame stability.'),
        Probe('anchors','Which candidate support remains stable under a cautious hands-only load check?',
              ('panel_cluster',),
              'Inspect fixed structure/posts; do not treat furniture, a trampoline, or decaying trim as a verified anchor.',85,2,
              inp.support_stability_verified!='YES',
              'Controls whether joint-support proposals are physically plausible.'),
        Probe('animal_gaps','Could a dog become trapped, entangled, escape under, or reach sharp edges?',
              tuple(ids),
              'Measure dog/panel clearances and inspect materials before use.',100,2,
              inp.safe_pet_clearance_verified!='YES',
              'A visually clear boundary can still be dangerous or ineffective.'),
    ]
    return tuple(sorted((p for p in options if p.unresolved and
                         (set(p.distinguishes)&ids)),
                        key=lambda p: (-p.priority, p.effort, p.id)))


def run(inp: Input) -> dict[str,Any]:
    ideas = infer(inp)
    strategies = make_strategies(inp,ideas)
    questions = probes(inp,ideas,strategies)
    steps = [
        {'step':'separate_goal_from_current_scene',
         'result':'target marks are treated as a provisional goal, not an existing wall',
         'evidence':list(refs(inp,'TARGET_ROUTE'))},
        {'step':'expand_material_roles',
         'result':'searches for uses of installed barriers, rigid panels and supports beyond original labels',
         'evidence':list(refs(inp,'EXISTING_BARRIER','RIGID_PANEL','ANCHOR_CANDIDATE','STRUCTURE'))},
        {'step':'enumerate_transformation_operators','result':[x.id for x in ideas],
         'evidence':list(o.id for o in inp.observations)},
        {'step':'select_conditional_strategies','result':[s.id for s in strategies],
         'evidence':[x.id for x in ideas]},
        {'step':'prevent_uncertainty_promotion',
         'result':'unknown permission, dimensions and connection strength are never promoted to verified safety',
         'evidence':[]},
    ]
    receipt = {
        'experiment':'MOTIF-FIELD-004-AUTONOMOUS-REFRAME',
        'evidence_kind':'ATTRIBUTED_PERCEPTION_PACKET_NOT_NATIVE_VISION',
        'goal':inp.goal,
        'observations':[asdict(o) for o in inp.observations],
        'inferences':[asdict(i) for i in ideas],
        'strategies':[asdict(s) for s in strategies],
        'self_initiated_steps':steps,
        'next_field_probe':asdict(questions[0]) if questions else None,
        'remaining_probes':[asdict(p) for p in questions],
        'dialogue_round_trips_needed_to_propose_options':0,
        'verified_physical_stability':inp.support_stability_verified=='YES',
        'verified_safe_pet_containment':False,
        'physical_actions_executed':0,
        'limits':'No image dimensions, independent structure test, or proof that a dog will remain contained. Model observations may be wrong.',
    }
    encoded = json.dumps(receipt,sort_keys=True,separators=(',',':')).encode()
    receipt['receipt_sha256']=hashlib.sha256(encoded).hexdigest()
    return receipt


def load_packet(raw: dict) -> Input:
    allowed=set(Input.__dataclass_fields__)
    if set(raw)-allowed:
        raise ValueError('unrecognized packet field(s)')
    vals={k:v for k,v in raw.items() if k != 'observations'}
    obs=raw.get('observations')
    if not isinstance(obs,list):
        raise ValueError('observations must be a list')
    parsed=[]
    allowed_obs=set(Observation.__dataclass_fields__)
    for element in obs:
        if not isinstance(element,dict) or set(element)-allowed_obs:
            raise ValueError('invalid observation object')
        parsed.append(Observation(**element))
    packet=Input(observations=tuple(parsed),**vals)
    packet.check()
    return packet
