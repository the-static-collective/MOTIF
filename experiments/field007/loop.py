"""FIELD-007: photo-private look -> trace -> critique -> redraw loop.

Reuses FIELD-006's provenance gate. Original sketch and photo coordinate spaces
stay separate. No physical action. No completed route or dog safety asserted.
"""
from __future__ import annotations
from hashlib import sha256
from pathlib import Path
import json,sys
from ink import extract_dashes,trace_receipt,overlay
from views import cross_photo_packet
p6=Path(__file__).resolve().parents[1]/'field006'
if not p6.exists():p6=Path(__file__).resolve().parents[1]/'motif_field006'
sys.path.insert(0,str(p6))
from atlas import from_dict
from vision_contract import review_model_packet,next_evidence_actions

def analyze(image: str|Path, source_id: str, *, atlas_packet:dict|None=None, photos:list[tuple[str,str]]|None=None) -> dict:
    traces=extract_dashes(image)
    original=trace_receipt(image,traces)
    result={
        'version':'FIELD-007-photo-private-candidate-tracing',
        'source_id':source_id,'ink':original,
        'sketch_boundary_intent_inferred':False,
        'desired_perimeter_complete':False,
        'real_multimodal_model_run':False,
        'actual_fence_assembly_tested':False,
        'no_unjustified_photo_to_map_coordinates':True,
        'reconstruction_policy':'draw only observed ink boxes and original image; no interpolated fence',
        'next_question':'Which candidate dashed strokes belong to the intended new boundary, and which parts remain untraced?',
    }
    if atlas_packet is not None:
        a=from_dict(atlas_packet)
        if source_id!=a.sketch_source:raise ValueError('sketch identity does not match atlas')
        review=review_model_packet(a,{'candidate_traces':[x.as_packet(source_id) for x in traces]})
        result['model_contract']={'tentative_candidates_accepted':len(review.accepted_traces),
                                  'held':list(review.held),'original_traces_unchanged':True,
                                  'next_evidence_actions':list(next_evidence_actions(a))[:4]}
        result['photo_witnesses_registered']=sum(s.kind=='USER_PHOTO' for s in a.sources)
        result['authored_photo_claims_not_newly_perceived']=len(a.claims)
    if photos:
        correspond=cross_photo_packet(photos)
        result['photo_correspondence']={k:v for k,v in correspond.items() if k!='pairs'}
        result['photo_correspondence']['tentative_pairs']=[x for x in correspond['pairs'] if x['status']=='TENTATIVE_VISUAL_OVERLAP']
        result['photo_correspondence']['held_pairs']=sum(x['status']=='HOLD' for x in correspond['pairs'])
    result['unlinked_ink_groups']=len(traces)
    result['claim_level']='DETECTED_PIXELS_AND_TENTATIVE_LINE_GROUPS_ONLY'
    result['receipt_sha256']=sha256(json.dumps(result,sort_keys=True).encode()).hexdigest()
    return result

def run_local(image,source_id,report_path,preview_path,atlas_path=None,photos=()):
    atlas_packet=json.loads(Path(atlas_path).read_text()) if atlas_path else None
    result=analyze(image,source_id,atlas_packet=atlas_packet,photos=list(photos))
    Path(report_path).parent.mkdir(parents=True,exist_ok=True)
    Path(report_path).write_text(json.dumps(result,indent=2,sort_keys=True))
    overlay(image,extract_dashes(image),preview_path)
    return result
