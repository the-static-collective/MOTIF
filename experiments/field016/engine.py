"""FIELD-016: constrained, evidence-tagged counterfactual revision of material layouts.

Research-only. Imports FIELD-015's *actual* free-body screen as one independent
numeric critic, not a claim of a calibrated physics engine or safe enclosure.
The engine never promotes a hypothetical placement to a witnessed installation.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict, replace
from hashlib import sha256
from itertools import combinations
from math import isfinite
from pathlib import Path
import json, sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'field015'))
from physics import Panel, screen, assembly_screen, Joint  # actual prior code

TRUTH = {'USER_REPORTED', 'MEASURED', 'MODEL_TENTATIVE', 'HYPOTHETICAL'}
CATEGORY = {'RIGID_PANEL', 'POROUS_PANEL', 'PRIVACY_PANEL'}

@dataclass(frozen=True)
class Piece:
    id: str
    kind: str
    width_m: float | None
    height_m: float | None
    mass_kg: float | None
    opacity: float | None
    base_depth_m: float | None
    evidence: str
    source_id: str
    # the following are *always* unresolved for actual assembly until examined
    edges_checked: bool = False
    mesh_entrapment_checked: bool = False
    measured_width: bool = False

    def validate(self):
        if not self.id or self.kind not in CATEGORY or self.evidence not in TRUTH or not self.source_id:
            raise ValueError('invalid piece provenance')
        for key in ('width_m','height_m','mass_kg','base_depth_m'):
            v=getattr(self,key)
            if v is not None and (isinstance(v,bool) or not isinstance(v,(float,int)) or not isfinite(v) or v<=0):
                raise ValueError('invalid '+key)
        if self.opacity is not None and (not isinstance(self.opacity,(int,float)) or not isfinite(self.opacity) or not 0<=self.opacity<=1):
            raise ValueError('invalid opacity')
        return self

@dataclass(frozen=True)
class Route:
    id: str
    span_m: float | None
    maximum_ground_clearance_m: float | None
    source: str
    status: str  # USER_DESIRED | HYPOTHETICAL | MODEL_TENTATIVE
    requires_moving_fence: bool = False
    retains_access: bool | None = None

    def validate(self):
        if not self.id or not self.source or self.status not in {'USER_DESIRED','HYPOTHETICAL','MODEL_TENTATIVE'}:
            raise ValueError('route provenance')
        if self.span_m is not None and (not isfinite(self.span_m) or self.span_m<=0):raise ValueError('span')
        if self.maximum_ground_clearance_m is not None and (not isfinite(self.maximum_ground_clearance_m) or self.maximum_ground_clearance_m<0):raise ValueError('clearance')
        return self

@dataclass(frozen=True)
class Scene:
    pieces: tuple[Piece,...]
    routes: tuple[Route,...]
    wind_mps: float
    piece_clearance_m: dict[str,float | None]
    # symbolic join model: all new joints are uncharacterized, not structural verification
    salvage_connections_available: bool
    user_rules: tuple[str,...] = ()
    source: str = 'SYNTHETIC'
    revision: int = 0

    def validate(self):
        if not self.pieces or not self.routes or len(self.pieces)>10 or len(self.routes)>10:
            raise ValueError('bounded scene required')
        if len({x.id for x in self.pieces})!=len(self.pieces) or len({x.id for x in self.routes})!=len(self.routes):
            raise ValueError('duplicate ids')
        for p in self.pieces:p.validate()
        for r in self.routes:r.validate()
        if not isfinite(self.wind_mps) or not 0<=self.wind_mps<=60:raise ValueError('wind scenario')
        if self.source not in TRUTH and self.source!='SYNTHETIC':raise ValueError('scene source')
        ids={p.id for p in self.pieces}
        if not set(self.piece_clearance_m).issubset(ids):raise ValueError('clearance identity')
        for v in self.piece_clearance_m.values():
            if v is not None and (not isfinite(v) or v<0):raise ValueError('clearance value')
        return self


def _panel(p:Piece)->Panel:
    return Panel(id=p.id,width_m=p.width_m,height_m=p.height_m,mass_kg=p.mass_kg,
                base_depth_m=p.base_depth_m,opacity=p.opacity,
                drag_coefficient=1.4 if p.opacity is not None else None,
                friction_coefficient=.6, support_type='FREESTANDING',
                # do not invent a certified connector strength
                evidence={'width_m':'MEASURED' if p.measured_width else 'GUESSED',
                          'height_m':'GUESSED','opacity':'GUESSED'})


def _piece_candidates(scene:Scene, route:Route):
    """Bounded combinatorial material search with explicit geometry assumptions."""
    for n in range(1,min(3,len(scene.pieces))+1):
        for grouping in combinations(scene.pieces,n):
            if n>1 and not scene.salvage_connections_available:continue
            if any(p.width_m is None for p in grouping):
                yield grouping, 'HOLD_WIDTH_UNKNOWN'
                continue
            nominal=sum(p.width_m for p in grouping)
            if route.span_m is not None and nominal+1e-9<route.span_m:continue
            yield grouping, 'CAN_COVER_SPAN_IN_IDEAL_2D_ONLY' if route.span_m is not None else 'HOLD_ROUTE_SPAN_UNKNOWN'


def evaluate(scene:Scene, route:Route, grouping:tuple[Piece,...], span_flag:str)->dict:
    numeric=[screen(_panel(p),scene.wind_mps) for p in grouping]
    model_failure=any(x['status']=='MODEL_FAILS_ASSUMED_LOAD_CASE' for x in numeric)
    unknowns=[]
    if span_flag.startswith('HOLD'):unknowns.append('unverified_coverage_length')
    if route.requires_moving_fence:unknowns.append('moving_existing_fence_permissions_and_actual_feasibility')
    if route.retains_access is None:unknowns.append('human_access_route_unknown')
    if route.retains_access is False:unknowns.append('human_access_blocked')
    if len(grouping)>1:
        unknowns.append('uncharacterized_joints_and_mutual_bracing')
    if any(p.evidence in {'HYPOTHETICAL','MODEL_TENTATIVE'} for p in grouping):
        unknowns.append('material_properties_not_verified')
    if any(not p.edges_checked for p in grouping):unknowns.append('edges_and_snag_points_not_checked')
    if any(p.kind=='POROUS_PANEL' and not p.mesh_entrapment_checked for p in grouping):
        unknowns.append('mesh_and_body_entrapment_not_checked')
    if any(not p.measured_width for p in grouping):unknowns.append('widths_are_not_independently_measured')
    for p in grouping:
        clearance=scene.piece_clearance_m.get(p.id)
        if clearance is None:
            unknowns.append('ground_clearance_unknown:'+p.id)
        elif route.maximum_ground_clearance_m is None:
            unknowns.append('acceptable_pet_clearance_unspecified')
        elif clearance>route.maximum_ground_clearance_m:
            model_failure=True
            unknowns.append('ground_clearance_exceeds_declared_limit:'+p.id)
    if any(p.height_m is None for p in grouping):unknowns.append('panel_height_unknown')
    if model_failure:verdict='MODEL_FAILS_STATED_SCENARIO'
    else:verdict='HOLD_PHYSICAL_INSTALLATION_UNVERIFIED'
    # Can compare wind screens; must never interpret conditional model result as a structurally safe object.
    simplified=sum((x['load'] or {}).get('force_n',0) for x in numeric)
    load_complete=all(x['load'] is not None for x in numeric)
    effort=len(grouping)*2 + int(route.requires_moving_fence)*4
    # Place these modules in an *invented* 3D frame: x=along run, y=height, z=arbitrary 0.
    # Actual property coordinates and panel clearance remain source-unknown.
    x=0.0;positioned=[]
    for p in grouping:
        positioned.append({'piece':p.id,'x_start_m':round(x,3),
                           'x_end_m':round(x+(p.width_m or 0),3) if p.width_m is not None else None,
                           'y_start_m':scene.piece_clearance_m.get(p.id),
                           'y_top_m':round(scene.piece_clearance_m[p.id]+p.height_m,3) if scene.piece_clearance_m.get(p.id) is not None and p.height_m is not None else None,
                           'z_m':0.0,'coordinate_status':'HYPOTHETICAL_LOCAL_FRAME_NOT_SITE_REGISTERED'})
        x+=p.width_m or 0
    topology=None
    if len(grouping)>1:
        proposed_joints=[Joint(a.id,b.id,'ZIP_TIE','SYNTHETIC_TENTATIVE_CONNECTION',None,False)
                         for a,b in zip(grouping,grouping[1:])]
        topology=assembly_screen([_panel(p) for p in grouping],proposed_joints,scene.wind_mps)
    return {'route_id':route.id,'pieces':[p.id for p in grouping],'nominal_coverage_m':round(sum((p.width_m or 0) for p in grouping),3),
            'target_span_m':route.span_m,'span_status':span_flag,'status':verdict,
            'model_failures':[{'id':x['panel_id'],'failures':x.get('failures',[])} for x in numeric if x['status']=='MODEL_FAILS_ASSUMED_LOAD_CASE'],
            'model_wind_force_n':round(simplified,2) if load_complete else None,
            'physics_sources':['FIELD-015:physics.screen','FIELD-015:physics.assembly_screen'],
            'local_3d_schematic':positioned,
            'joint_topology':{'status':topology['status'],'load_sharing_solved':topology['components'][0]['load_sharing_solved']} if topology else None,
            'uncertainties':sorted(set(unknowns)),
            'estimated_relative_assembly_effort':effort,
            'wind_scenario_mps':scene.wind_mps,
            'safety_certified':False,'pet_containment_certified':False,
            'notes':'No component test, wind code evaluation, load sharing validation, secure gate or real 3D reconstruction.'}


def ranking_key(row:dict):
    # Preserve known failures as worse, but do not award 'safe' to missing data.
    return (row['status']=='MODEL_FAILS_STATED_SCENARIO',
            any(x.startswith('human_access_blocked') for x in row['uncertainties']),
            len(row['uncertainties']),row['estimated_relative_assembly_effort'],
            row['model_wind_force_n'] if row['model_wind_force_n'] is not None else float('inf'),
            row['route_id'],row['pieces'])


def propose(scene:Scene, *, max_results=20)->dict:
    scene.validate()
    candidates=[]
    for route in scene.routes:
        for grouping,span in _piece_candidates(scene,route):
            candidates.append(evaluate(scene,route,grouping,span))
    candidates.sort(key=ranking_key)
    report={'experiment':'MOTIF_FIELD_016','scene_version':scene.revision,'source':scene.source,
            'reasoner':'bounded authored combinatorial arrangement search + actual FIELD-015 screen',
            'candidates_total':len(candidates),'showing':min(len(candidates),max_results),
            'candidates':candidates[:max_results],
            'next_probe':next_probe(scene,candidates),
            'actual_model_reconstruction_calls':0,
            'actual_3d_physical_simulation':False,
            'real_world_installations_tested':0,
            'certifications':0}
    report['digest_sha256']=sha256(json.dumps(report,sort_keys=True).encode()).hexdigest()
    return report


def next_probe(scene:Scene,rows:list[dict]):
    """Value-of-clarification heuristic: question must change a model branch.

    Not calibrated expected information gain: each probe has a named counterfactual.
    """
    if not rows:return {'question':'Can you identify any usable span and material widths?', 'why':'No arrangements can be evaluated.', 'kind':'INPUT'}
    if any(r.span_m is None for r in scene.routes):
        return {'question':'Could you measure or roughly mark one boundary span?', 'why':'Without any span, the component count cannot be checked.', 'kind':'MEASUREMENT'}
    # Try to falsify the *currently highest-ranked* panel span rather than
    # asking a generic measurement question. This is a bounded deterministic
    # counterfactual, not a probability that the true width is 10% smaller.
    leading=rows[0]
    chosen_route=next((r for r in scene.routes if r.id==leading['route_id']),None)
    for identifier in leading['pieces']:
        p=next((p for p in scene.pieces if p.id==identifier),None)
        if not p or p.measured_width or p.width_m is None or not chosen_route:continue
        smaller=replace(p,width_m=p.width_m*0.90)
        changed=replace(scene,pieces=tuple(smaller if x.id==p.id else x for x in scene.pieces))
        still_exists=any([x.id for x in group]==leading['pieces'] for group,_ in _piece_candidates(changed,chosen_route))
        if not still_exists:
            return {'question':f'Could you measure the usable width of {identifier} (or mark an approximate range)?',
                    'why':'A hypothetical 10% smaller width eliminates the currently leading coverage arrangement. That change has not been observed.',
                    'kind':'DECISION_CHANGING_MEASUREMENT','subject':identifier,
                    'counterfactual_test':'UNVERIFIED_MINUS_10_PERCENT','would_eliminate_current_best_if_true':True}
    if any(not x.measured_width for x in scene.pieces):
        return {'question':'Can you confirm a candidate panel width or enter a rough interval?',
                'why':'Unverified panel dimensions can affect route coverage and material count.', 'kind':'DIRECT_MANIPULATION'}
    if any(x.get('status')=='MODEL_FAILS_STATED_SCENARIO' for x in rows[:5]):
        return {'question':'Is there a genuinely stable, independently assessed support or a different mesh piece available?',
                'why':'The simplified load case rejects one or more leading arrangements; a tie strength label is insufficient.',
                'kind':'SUPPORT_AND_MATERIAL_INSPECTION'}
    if any(x.requires_moving_fence for x in scene.routes):
        return {'question':'Can the existing fence section actually be relocated without losing a necessary barrier?',
                'why':'Relocation may shorten the route but requires real permission and verified constraints.', 'kind':'MOVABILITY'}
    return {'question':'Can you inspect ground clearance, edges and actual connections at the proposed junction?',
            'why':'The simplified model cannot certify a physical enclosure.', 'kind':'REVERSIBLE_FIELD_INSPECTION'}

@dataclass(frozen=True)
class Observation:
    event_id:str
    source:str
    kind:str
    subject:str
    value:float|bool
    revision:int


def reenter(scene:Scene, event:Observation)->Scene:
    """Evidence update; a simulation/guess NEVER becomes a measured property."""
    scene.validate()
    if not event.event_id or event.source not in TRUTH or event.revision!=scene.revision+1:
        raise ValueError('bad evidence revision/source')
    if event.kind=='piece_width':
        if not isinstance(event.value,(float,int)) or isinstance(event.value,bool) or not isfinite(event.value) or event.value<=0:
            raise ValueError('invalid width')
        found=False;new=[]
        for p in scene.pieces:
            if p.id==event.subject:
                found=True
                new.append(replace(p,width_m=float(event.value),
                    measured_width=event.source=='MEASURED'))
            else:new.append(p)
        if not found:raise ValueError('unknown piece')
        return replace(scene,pieces=tuple(new),revision=event.revision)
    if event.kind=='route_length':
        if not isinstance(event.value,(float,int)) or isinstance(event.value,bool) or not isfinite(event.value) or event.value<=0:
            raise ValueError('invalid length')
        found=False;new=[]
        for r in scene.routes:
            if r.id==event.subject:
                found=True
                new.append(replace(r,span_m=float(event.value),status='USER_DESIRED' if event.source in {'MEASURED','USER_REPORTED'} else 'MODEL_TENTATIVE'))
            else:new.append(r)
        if not found:raise ValueError('unknown route')
        return replace(scene,routes=tuple(new),revision=event.revision)
    if event.kind=='clearance':
        if not isinstance(event.value,(float,int)) or isinstance(event.value,bool) or not isfinite(event.value) or event.value<0:
            raise ValueError('invalid clearance')
        if event.subject not in {p.id for p in scene.pieces}:raise ValueError('unknown piece')
        return replace(scene,piece_clearance_m={**scene.piece_clearance_m,event.subject:float(event.value)},revision=event.revision)
    raise ValueError('unknown event type')


def to_json_report(scene:Scene,events:tuple[Observation,...]=())->dict:
    initial=propose(scene)
    timeline=[{'revision':scene.revision,'receipt':initial['digest_sha256'],
               'top':initial['candidates'][0] if initial['candidates'] else None}]
    current=scene
    for evt in events:
        current=reenter(current,evt)
        report=propose(current)
        timeline.append({'revision':current.revision,'event':asdict(evt),'receipt':report['digest_sha256'],
                         'top':report['candidates'][0] if report['candidates'] else None})
    return {'initial':initial,'final':propose(current),'timeline':timeline,
            'real_world_action_executed':False,'safety_approved':False}


def invented_scene()->Scene:
    # Completely synthetic. Neither dimensions nor properties refer to a user yard.
    pieces=(
        Piece('privacy','PRIVACY_PANEL',1.5,1.,5.,1.,.35,'HYPOTHETICAL','fixture-opaque'),
        Piece('cage','RIGID_PANEL',1.0,1.,4.,.55,.42,'HYPOTHETICAL','fixture-cage'),
        Piece('porous','POROUS_PANEL',1.5,1.,5.,.20,.35,'HYPOTHETICAL','fixture-porous'),
    )
    routes=(Route('original',2.4,.06,'fixture-route','HYPOTHETICAL',False,True),
            Route('repositioned',1.5,.06,'fixture-shorter','HYPOTHETICAL',True,None))
    return Scene(pieces,routes,8.,{'privacy':0.,'porous':None,'cage':0.},True,
                 ('zip ties reported strong, installed load capacity uncharacterized',),'SYNTHETIC')

if __name__=='__main__':
    print(json.dumps(to_json_report(invented_scene(),(Observation('measure1','MEASURED','piece_width','porous',1.32,1),)),indent=2))
