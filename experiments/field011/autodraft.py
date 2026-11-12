"""FIELD-011: create an editable FIELD-010 starting board from real FIELD-007 ink.
No source photographs or personal property mapping are committed. CV output stays
tentative: no line intent, completed perimeter, physical scale or safety claim.
"""
from __future__ import annotations
from hashlib import sha256
from pathlib import Path
from math import hypot
import argparse, json, sys

HERE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(HERE/'field007'))
from ink import extract_dashes

def image_to_board(p, width, height):
    """Map source-normalized pixels to SVG 1000x450 xMidYMid meet."""
    if not (isinstance(p,(list,tuple)) and len(p)==2 and
            all(isinstance(x,(int,float)) and 0 <= x <= 1 for x in p)):
        raise ValueError('Bad source point')
    if min(width,height)<=0:raise ValueError('Bad image dimensions')
    s=min(1000/width,450/height)
    sw,sh=width*s,height*s
    return [round(((1000-sw)/2+p[0]*sw)/1000,6),
            round(((450-sh)/2+p[1]*sh)/450,6)]

def propose(path, *, source_id='sketch-1', max_groups=8):
    import cv2
    path=Path(path)
    im=cv2.imread(str(path),cv2.IMREAD_GRAYSCALE)
    if im is None:raise ValueError('Unreadable sketch')
    h,w=im.shape
    source_hash=sha256(path.read_bytes()).hexdigest()
    candidates=extract_dashes(im,max_candidates=max_groups)
    items=[]
    for g in candidates:
        if len(g.points)<3:continue
        start=image_to_board(g.points[0],w,h)
        end=image_to_board(g.points[-1],w,h)
        if hypot((end[0]-start[0])*1000,(end[1]-start[1])*450)<6:continue
        n=len(items)+1
        items.append({
            'id':f'cv-{source_hash[:12]}-{n:02d}',
            'kind':'desired','label':f'Possible dotted fragment {n:02d} · review',
            'status':'tentative','movable':False,'points':[start,end],
            'evidence':{'source_id':source_id,'source_sha256':source_hash,
                'method':'FIELD-007_REAL_OPENCV','axis':g.axis,
                'source_normalized_points':[list(pt) for pt in g.points],
                'semantic_status':'POSSIBLE_MARK__NOT_CONFIRMED_BOUNDARY',
                'drawn_join_hypothesized':True,'safety_certified':False}
        })
    return {'schema':'motif.field011.draft.v1','source_id':source_id,
            'source_sha256':source_hash,'source_size':[w,h],
            'coordinate_frame':'sketch_normalized','source_kind':'USER_SKETCH',
            'method':'FIELD-007_REAL_OPENCV','items':items,
            'asserts_complete_desired_boundary':False,'asserts_physical_scale':False,
            'asserts_safety':False,'photo_to_sketch_registration':'NOT_PERFORMED'}

def to_board(packet):
    """FIELD-010 board JSON; no image bytes included; source upload still required."""
    if packet.get('asserts_complete_desired_boundary') is not False or packet.get('asserts_safety') is not False:
        raise ValueError('Refuse claimed finished/verified geometry')
    return {'schema':'motif.field010.v1',
        'base':{'source':'user_sketch','coordinate_frame':'sketch_normalized',
                'sketch_size':[1000,450],'items':packet['items']},
        'events':[]}

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--sketch',required=True)
    p.add_argument('--out',required=True)
    p.add_argument('--source-id',default='sketch-1')
    a=p.parse_args()
    packet=propose(a.sketch,source_id=a.source_id)
    target=Path(a.out);target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(to_board(packet),indent=2))
    target.with_suffix('.draft.json').write_text(json.dumps(packet,indent=2))
    print(json.dumps({'tentative_fragments':len(packet['items']),
                      'status':'EDITABLE_DRAFT__NOT_VERIFIED_GEOMETRY'}))
if __name__=='__main__':main()
