"""FIELD-016 bridge to both FIELD-015 3D model-reconstruction witness types.

Cannot extract a real-world length from a relative point cloud. Cannot use agreement
of MapAnything and DA3 to authenticate structural mass/anchor/fastener physics.
"""
from __future__ import annotations
from dataclasses import asdict
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'field015'))
from reconstruction import Reconstruction, report_pair
from engine import Scene, propose


def evaluate_with_vision(scene:Scene, reconstructions:tuple[Reconstruction,...]=())->dict:
    if len(reconstructions)>2:raise ValueError('At most two explicit reconstruction witnesses')
    scene.validate()
    packets=[w.packet() for w in reconstructions]
    if len(reconstructions)==2:
        pairing=report_pair(*reconstructions)
    else:
        pairing={'status':'HOLD_INSUFFICIENT_RECONSTRUCTION_WITNESSES'}
    plan=propose(scene)
    return {
        'field016_replanning':plan,
        'field015_3d_witnesses':[{'engine':p['engine'],'checkpoint':p['checkpoint'],'scale':p['scale'],
                                  'point_count':p['point_count'],'inference_executed':p['inference_executed'],
                                  'registered_to_site':p['registered_to_site']} for p in packets],
        'cross_model_alignment':pairing,
        'site_coordinates_from_model_clouds':False,
        'physical_panel_widths_from_model_clouds':False,
        'next_real_evidence':('Confirm which objects from photos correspond to which parts of the sketch',
                              'Establish a measured scale on the same plane as any proposed placement',
                              'Inspect actual supports and joint behavior before animal use'),
        'all_initial_layouts_author_designs_not_reconstruction_results':True,
    }
