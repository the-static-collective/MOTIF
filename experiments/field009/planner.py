"""FIELD-009 visual thinking: compare route alternatives without inventing lengths."""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
import json
from geometry import Scene,Trace,Anchor,ratio,calibrate,panel_requirements

@dataclass(frozen=True)
class Alternative:
    id: str
    route: Trace
    source_claim: str


def explore(scene: Scene, reference: Trace, alternatives: tuple[Alternative,...],
            anchor: Anchor|None=None, panel_width:float|None=None) -> dict:
    if not alternatives or len(alternatives)>16:
        raise ValueError('Expect 1..16 explicitly sourced candidate routes')
    if len({a.id for a in alternatives})!=len(alternatives):
        raise ValueError('Duplicate route ids')
    if anchor is not None and anchor.trace_id!=reference.id:
        raise ValueError('Reference/anchor mismatch')
    rows=[]
    for alt in alternatives:
        if not alt.source_claim:
            raise ValueError('Routes must cite a human or model-authored hypothesis')
        rr=ratio(scene,alt.route,reference)
        scaled=calibrate(scene,alt.route,((reference,anchor),) if anchor else ())
        item={'id':alt.id,'provenance':alt.source_claim,'ratio':rr.packet(),'length':scaled.packet()}
        if panel_width is not None:
            item['panel_scenario']=panel_requirements(scaled,panel_width)
        rows.append(item)
    ordered=sorted(rows,key=lambda r: next(a.route.nominal_length for a in alternatives if a.id==r['id']))
    answer={'research':'FIELD-009','scene_source':scene.source_id,'mode':scene.mode,
            'status':'PROVISIONAL_2D_VISUAL_COMPARISON','alternatives':rows,
            'visual_shortest':ordered[0]['id'],
            'visual_shortest_is_proven_physical_shortest':False,
            'recommendation':'Check whether the drawing is approximately proportional or measure an accessible reference',
            'verified_dog_containment':False,'verified_load_capacity':False,
            'missing_3d_geometry':'not established from one hand sketch or an unrectified perspective photo'}
    if anchor is None:
        answer['decision_confidence']='DRAWN_ONLY__NO_PHYSICAL_SCALE'
        answer['next_probe']='Measure one accessible known span AND check whether the source sketch is approximately proportional.'
    elif any(r['length']['status']=='HOLD' for r in rows):
        answer['decision_confidence']='HOLD_UNSCALABLE'
        answer['next_probe']='Resolve scale, source plane, and geometric uncertainty before material estimates.'
    elif len(rows)>1:
        lowrow=next(r for r in rows if r['id']==ordered[0]['id'])
        other_lower=min(r['length']['lower'] for r in rows if r['id']!=lowrow['id'])
        if lowrow['length']['upper'] < other_lower:
            answer['decision_confidence']='ROBUST_UNDER_STATED_GEOMETRIC_ASSUMPTIONS'
            answer['next_probe']='Verify route access, anchoring, slopes and actual material conditions.'
        else:
            answer['decision_confidence']='OVERLAPPING_INTERVALS__NO_CONFIDENT_ROUTE_RANK'
            answer['next_probe']='Measure the short candidate opening directly, then revise the comparison.'
    else:
        answer['decision_confidence']='SINGLE_CONDITIONAL_ROUTE'
        answer['next_probe']='Check the proposed route against an independent physical measurement.'
    answer['receipt_sha256']=sha256(json.dumps(answer,sort_keys=True).encode()).hexdigest()
    return answer
