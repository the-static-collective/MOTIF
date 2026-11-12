"""FIELD-016 bridge to the actual parent FIELD-015 reconstruction contract.

Raw model-local point clouds are not surveyed coordinates or reliable panel
physics. Parent branches have published a dict `witness` API and a separate
standalone typed `Reconstruction` API; both are checked before use.
"""
from __future__ import annotations
from pathlib import Path
import math, sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'field015'))
import reconstruction as field015_reconstruction
from engine import Scene,propose


def _checked_packet(w):
    if hasattr(w,'packet') and callable(w.packet):
        p=w.packet()
    elif isinstance(w,dict):
        p=dict(w)
    else:raise ValueError('Unsupported reconstruction witness')
    if p.get('engine') not in ('MAPANYTHING','DEPTH_ANYTHING_3'):
        raise ValueError('Unsupported model engine')
    if not p.get('checkpoint') or p.get('registered_to_site') is not False:
        raise ValueError('Unverified model output claiming world registration')
    digests=p.get('image_sha256')
    if not isinstance(digests,(list,tuple)) or not digests or any(not isinstance(x,str) or len(x)!=64 for x in digests):
        raise ValueError('Missing hashed image sources')
    pts=p.get('xyz',[])
    if not 3<=len(pts)<=12000 or not all(len(pt)==3 and all(math.isfinite(float(v)) for v in pt) for pt in pts):
        raise ValueError('Bad model-local points')
    if p.get('scale') not in ('RELATIVE','MODEL_METRIC_UNVERIFIED'):
        raise ValueError('No measured scale can be claimed from a raw model')
    return p


def evaluate_with_vision(scene:Scene,reconstructions:tuple=()):
    if len(reconstructions)>2:raise ValueError('Use at most two reconstruction hypotheses')
    scene.validate(); packets=[_checked_packet(w) for w in reconstructions]
    if len(packets)==2:
        if hasattr(field015_reconstruction,'compare'):
            status=field015_reconstruction.compare(packets[0],packets[1])
            pairing={'status':status,'site_geometry_certified':False}
        else:
            # Typed standalone FIELD-015 API: retain actual compare without elevation.
            if all(hasattr(w,'check') for w in reconstructions):
                result=field015_reconstruction.report_pair(*reconstructions)
                pairing={'status':result['status'],'site_geometry_certified':False}
            else:
                pairing={'status':'HOLD_UNSUPPORTED_CROSS_WITNESS_CONTRACT','site_geometry_certified':False}
    else:pairing={'status':'HOLD_INSUFFICIENT_RECONSTRUCTION_WITNESSES','site_geometry_certified':False}
    return {'field016_replanning':propose(scene),
        'field015_3d_witnesses':[{'engine':p['engine'],'checkpoint':p['checkpoint'],'scale':p['scale'],
                                 'point_count':len(p['xyz']),
                                 'inference_executed':p.get('real_model_executed',p.get('inference_executed',False)),
                                 'registered_to_site':p['registered_to_site']} for p in packets],
        'cross_model_alignment':pairing,
        'site_coordinates_from_model_clouds':False,
        'physical_panel_widths_from_model_clouds':False,
        'next_real_evidence':('Identify shared objects across photographs and sketch',
                              'Measure a physical length on a compatible plane',
                              'Assess real anchors, joints and material behavior'),
        'all_initial_layouts_author_designs_not_reconstruction_results':True}
