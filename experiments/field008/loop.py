"""Bounded *optional* local vision, geometry, critic and crop-driven second look.

No images leave localhost. Independent pixel checking is NOT a second
independent visual interpretation; same-model repeated answer is correlated.
"""
from __future__ import annotations
from pathlib import Path
from hashlib import sha256
import json
from critic import review,overlay
from reinspect import focus_crop
from local_vlm import perceive_local


def run(image:str|Path,source_id:str,out_dir:str|Path,*, use_local_model=False,
        model='qwen3-vl:2b-instruct', first_packet=None, second_packet=None,
        transport=None):
    out=Path(out_dir);out.mkdir(parents=True,exist_ok=True)
    if first_packet is None:
        if use_local_model:
            res=perceive_local(source_id,image,explicit_local_model=True,model=model,transport=transport)
            first_packet=res['packet'];receipts=[res['model_receipt']]
        else:
            first_packet={'source_id':source_id,'claims':[]};receipts=[]
    else:receipts=[]
    first=review(first_packet,image,source_id)
    overlay(image,first_packet,first,out/'first_pass.png')
    focus=focus_crop(image,first,out/'focus.png')
    second=None
    if second_packet is not None:
        second=review(second_packet,image,source_id)
        overlay(image,second_packet,second,out/'second_pass.png')
    elif use_local_model and focus['status']=='CROP_CREATED_FOR_HUMAN_OR_OPT_IN_LOCAL_VLM':
        # Reuse source coordinates? NO: a crop's normalized coords are not
        # coordinates in the original sketch; demand separate crop-only review.
        crop_id=source_id+':crop'
        crop_res=perceive_local(crop_id,out/'focus.png',explicit_local_model=True,model=model,transport=transport)
        receipts.append(crop_res['model_receipt'])
        second=review(crop_res['packet'],out/'focus.png',crop_id)
        overlay(out/'focus.png',crop_res['packet'],second,out/'second_crop.png')
    if second is not None:
        # Never auto-promote an original source claim even when repeated passes agree.
        delta={'held_count_change':second['held']-first['held'],
               'ink_compatible_count_change':second['ink_compatible']-first['ink_compatible'],
               'notes':'Different crop coordinate space; counts are diagnostic, not comparable proof of correctness.',
               'automatic_evidence_promotion':False}
    else:delta=None
    result={'experiment':'FIELD-008','first':first,'focus':focus,'second':second,'change':delta,
            'model_call_count':len(receipts), 'model_receipts':receipts,
            'complete_route_verified':False,'image_source_private':True,
            'real_world_safety_certified':False,
            'source_strokes_preserved_not_replaced':True,
            'review_authority':'Human verification needed to resolve intended boundary'}
    # File paths may differ from run to run; hash explicit trace/claims, not files.
    result['evidence_digest']=sha256(json.dumps({'first':first['receipt_sha256'],
        'second':second['receipt_sha256'] if second else None},sort_keys=True).encode()).hexdigest()
    (out/'report.json').write_text(json.dumps(result,indent=2))
    return result
