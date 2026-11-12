"""FIELD-011: FIELD-007 source-pixel candidates -> FIELD-010 editable proposal packet.

Draft geometry is not a physical site map or evidence of user intent. No photo-to-
map projection. Explicitly retains separate source and board coordinate frames.
"""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
from math import hypot, isfinite
from pathlib import Path
import json
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'field007'))
from ink import extract_dashes, trace_receipt  # actual earlier committed component

FRAME = 'sketch_normalized'
SCHEMA = 'motif.field011.draft.v1'


def fit_point(p: tuple[float, float], width: int, height: int,
              board_width: int=1000, board_height: int=450) -> list[float]:
    """image normalized -> actual SVG image placement with xMidYMid meet."""
    if not all(isinstance(v, (float, int)) and isfinite(v) for v in p):
        raise ValueError('Nonfinite coordinate')
    if not all(0 <= v <= 1 for v in p):
        raise ValueError('Image coordinate outside source')
    if min(width, height, board_width, board_height) <= 0:
        raise ValueError('Invalid frame')
    scale = min(board_width / width, board_height / height)
    scaled_width, scaled_height = width * scale, height * scale
    mx, my = (board_width - scaled_width) / 2, (board_height - scaled_height) / 2
    return [round((mx + p[0] * scaled_width) / board_width, 6),
            round((my + p[1] * scaled_height) / board_height, 6)]


def packet_from_components(*, width: int, height: int, groups: list[dict],
                           source_sha256: str, source_id: str='sketch-1',
                           desired_dotted_rule: bool=False) -> dict[str, Any]:
    """Accept component groups (from CV or pixel tests), never infer joins or length."""
    if not (2 <= len(source_id) <= 80 and source_id.replace('-', '').replace('_', '').isalnum()):
        raise ValueError('Bad source id')
    if not isinstance(source_sha256, str) or len(source_sha256) != 64 or any(c not in '0123456789abcdef' for c in source_sha256):
        raise ValueError('Invalid source digest')
    if min(width, height) < 90 or width*height > 25_000_000:
        raise ValueError('Invalid source dimensions')
    items=[]
    for g in groups[:12]:
        if g.get('axis') not in ('H', 'V'):
            raise ValueError('Invalid axis')
        pts=g.get('points')
        if not isinstance(pts, list) or len(pts) < 3 or len(pts)>100:
            raise ValueError('Insufficient or excessive ink witnesses')
        if not all(isinstance(p, list) and len(p)==2 for p in pts):
            raise ValueError('Invalid pixel candidate')
        b1=fit_point(tuple(pts[0]), width, height)
        b2=fit_point(tuple(pts[-1]), width, height)
        if hypot((b1[0]-b2[0])*1000,(b1[1]-b2[1])*450)<6:
            continue
        i=len(items)+1
        item={
            'id': f'cv-{source_sha256[:12]}-{i:02d}',
            'kind':'desired', # UI 'desired' is an unverified classification, never user_confirmed
            'label':f'Possible dotted fragment {i:02d} · review',
            'points':[b1,b2],
            'status':'tentative',
            'movable':False,
            'evidence':{
                'source_id':source_id,
                'source_sha256':source_sha256,
                'method':'FIELD-007_CV_DASH_GROUP',
                'source_normalized_points':pts,
                'axis':g['axis'],
                'semantic_status':'POSSIBLE_MARK__NOT_CONFIRMED_BOUNDARY',
                'drawn_join_hypothesized':True,
                'user_rule_dotted_is_desired':bool(desired_dotted_rule),
                'safety_certified':False,
            }
        }
        items.append(item)
    out={
        'schema':SCHEMA,'source_id':source_id,'source_sha256':source_sha256,
        'source_size':[width,height],'board_size':[1000,450],
        'coordinate_frame':FRAME,'source_kind':'USER_SKETCH',
        'method':'FIELD-007_CV_OR_AUTHORED_FIXTURE',
        'items':items,
        'source_line_count':len(groups),
        'candidate_count':len(items),
        'asserts_complete_desired_boundary':False,
        'asserts_physical_scale':False,
        'asserts_safety':False,
        'photo_to_sketch_registration':'NOT_PERFORMED',
        'note':'Tentative line hypotheses connect detected dash centroids. They do not verify intervening ink, intended route or geometry. Confirm, reject or reshape each one.',
        'next_inputs':['Confirm or reject each possible dotted fragment',
                       'Draw missing desired-route pieces',
                       'Enter one actual span measurement if available',
                       'Mark existing materials that can be moved'],
    }
    return out


def from_image(source: str | Path, *, source_id='sketch-1', desired_dotted_rule=False,
               max_candidates=8) -> dict[str, Any]:
    """Actual local CV inference; does not require language/semantic label data."""
    import cv2
    path=Path(source)
    raw=cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
    if raw is None:
        raise ValueError('Cannot load sketch')
    h,w=raw.shape
    groups=extract_dashes(raw, max_candidates=max_candidates)
    pin=sha256(path.read_bytes()).hexdigest()
    payload=[{'axis':g.axis,'points':[list(p) for p in g.points]} for g in groups]
    out=packet_from_components(width=w,height=h,groups=payload,source_sha256=pin,
                               source_id=source_id,desired_dotted_rule=desired_dotted_rule)
    out['method']='FIELD-007_OPENCV_REAL_PIXELS'
    out['cv_receipt']=trace_receipt(path, groups)['algorithm']
    out['real_model_calls']=0
    return out


def pack_model_claims(raw:dict, *, source_sha256: str, width:int, height:int,
                      source_id:str) -> dict:
    """Review a potential local VLM response, never promote unsupported labels to truth.

    This is a strictly limited auxiliary adapter; it isn't proof the VLM executed.
    """
    if not isinstance(raw, dict) or raw.get('source_id') != source_id:
        raise ValueError('VLM packet source mismatch')
    if raw.get('claimed_complete_route') is not False:
        raise ValueError('VLM claims full route or omitted refusal')
    groups=[]
    for c in raw.get('claims',[])[:20]:
        if not isinstance(c,dict) or c.get('kind') != 'VISIBLE_MARK' or c.get('style') != 'DOTTED':
            continue
        pts=c.get('points')
        if not isinstance(pts,list) or len(pts)<2 or len(pts)>100:
            continue
        # No claim about actual visual evidence at this stage. Require 3 points
        # to form an editable group and a later CV critique for independent support.
        if len(pts)<3:
            continue
        groups.append({'axis':'H' if abs(pts[-1][0]-pts[0][0]) >= abs(pts[-1][1]-pts[0][1]) else 'V','points':pts})
    out=packet_from_components(width=width,height=height,groups=groups,
                               source_sha256=source_sha256,source_id=source_id)
    out['method']='UNVERIFIED_VLM_PROPOSAL_REQUIRES_PIXEL_CRITIQUE'
    return out


def emit(source, output, source_id='sketch-1', desired_dotted_rule=False):
    result=from_image(source,source_id=source_id,desired_dotted_rule=desired_dotted_rule)
    out=Path(output);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2))
    return result


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(description='Opt-in private local sketch -> tentative editable proposal JSON')
    p.add_argument('--sketch',required=True)
    p.add_argument('--out',required=True)
    p.add_argument('--source-id',default='sketch-1')
    p.add_argument('--user-says-dotted-is-desired',action='store_true')
    a=p.parse_args()
    result=emit(a.sketch,a.out,source_id=a.source_id,desired_dotted_rule=a.user_says_dotted_is_desired)
    print(json.dumps({'candidates':result['candidate_count'], 'status':'TENTATIVE_EDITABLE_NOT_PHYSICAL'}))
