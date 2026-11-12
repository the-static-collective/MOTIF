"""Reviewed, source-scoped FIELD-010 -> actual FIELD-009 geometry functions.

Must be run inside a checkout of MOTIF where experiments/field009 exists.
It never treats an unrectified photograph as the board's coordinate frame.
"""
from __future__ import annotations
from pathlib import Path
import sys

from workbench import replay
PARENT=Path(__file__).resolve().parents[1]/'field009'
if not PARENT.exists():
    raise RuntimeError('FIELD-009 dependency missing: use the stacked MOTIF branch')
sys.path.insert(0,str(PARENT))
from geometry import Scene,Point,Trace,Anchor,ratio,calibrate


def physical_geometry(project:dict):
    state=replay(project)
    if state['source'] not in {'synthetic','user_sketch'}:
        raise ValueError('Only source-scoped sketch coordinates are supported')
    size=state['sketch_size']
    scene=Scene(source_id='field010:source-sketch',mode='SKETCH_APPROX',
                plane_id='same-sketch-paper',provenance='original drawing with human-edited vectors',
                proportion_tolerance=state['tolerance'] if state['proportional'] else None)
    traces={}
    for obj in state['items']:
        if obj['status']=='user_rejected' or len(obj['points'])!=2:continue
        a,b=obj['points']
        if a==b:continue
        traces[obj['id']]=Trace(id=obj['id'],source_id=scene.source_id,plane_id=scene.plane_id,
            vertices=(Point(a[0]*size[0],a[1]*size[1]),Point(b[0]*size[0],b[1]*size[1])),
            provenance='human-edit-replayed-not-physical-observation',endpoint_tolerance_px=2.0)
    anchors=[]
    for id_,measurement in state['measurements'].items():
        if id_ not in traces or measurement['quality']!='user_measured':continue
        anchors.append((traces[id_],Anchor(trace_id=id_,lower=measurement['value'],
                      upper=measurement['value'],units=measurement['unit'],
                      provenance='human-entered-measurement',verified=True)))
    desired=[(obj['id'],traces[obj['id']]) for obj in state['items']
             if obj['kind']=='desired' and obj['id'] in traces]
    estimates=[]
    for id_,tr in desired:
        result=calibrate(scene,tr,tuple(anchors))
        estimates.append({'id':id_,'estimate':result.packet(),
                          'physical_installation_verified':False})
    return {'source':'FIELD-009 actual geometry library','source_id':scene.source_id,
            'mode':scene.mode,'sketch_tolerance_assumption':scene.proportion_tolerance,
            'estimated_target_spans':estimates,'anchors':len(anchors),
            'photo_pixels_georegistered':False,
            'status':'DRAWN_OR_CONDITIONAL_NOT_SURVEYED'}
