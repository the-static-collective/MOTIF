"""FIELD-008: evidence-tethered geometric review of multimodal hypotheses.

A sketch mark is not a surveyed fence; an image-label model is not authority.
Deterministic source-pixel checking detects contradictions but never certifies
scene meaning, placement, structural load or safe real-world use.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from hashlib import sha256
from pathlib import Path
from typing import Any
import json, math
import cv2
import numpy as np

try:
    from ink import extract_dashes, DashCandidate
except ModuleNotFoundError:
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'field007'))
    from ink import extract_dashes, DashCandidate

VALID_STYLES = {'DOTTED','SOLID','UNKNOWN'}
KNOWN_KINDS = {'VISIBLE_MARK','TEXT_LABEL','OBJECT','HYPOTHETICAL_ROUTE'}

@dataclass(frozen=True)
class Review:
    claim_id: str
    style: str
    verdict: str
    matched_dash_ids: tuple[str,...]
    support_score: float
    reasons: tuple[str,...]
    authority: str = 'MODEL_TENTATIVE_NOT_USER_CONFIRMED'


def _point(p:Any)->tuple[float,float]:
    if not isinstance(p,(list,tuple)) or len(p)!=2:raise ValueError('Point must be [x,y]')
    if any(not isinstance(v,(int,float)) or isinstance(v,bool) or not math.isfinite(v) or not 0<=v<=1 for v in p):
        raise ValueError('Normalized points must be finite 0..1')
    return (float(p[0]),float(p[1]))


def validate_packet(packet:dict, source_id:str)->dict:
    if not isinstance(packet,dict):raise ValueError('VLM answer must be a JSON object')
    if packet.get('source_id')!=source_id:raise ValueError('Mismatched image identity')
    claims=packet.get('claims',[])
    if not isinstance(claims,list) or len(claims)>30:raise ValueError('Too many claims')
    used=set()
    checked=[]
    for c in claims:
        if not isinstance(c,dict) or c.get('kind') not in KNOWN_KINDS:raise ValueError('Unknown claim type')
        id=c.get('id')
        if not isinstance(id,str) or not id or len(id)>60 or id in used:raise ValueError('Invalid/duplicate claim id')
        used.add(id)
        pts=c.get('points',[])
        if not isinstance(pts,list) or len(pts)>30:raise ValueError('Malformed geometry')
        if c['kind'] in ('VISIBLE_MARK','HYPOTHETICAL_ROUTE') and len(pts)<2:
            raise ValueError('Line geometry requires two points')
        if c['kind'] in ('TEXT_LABEL','OBJECT') and len(pts)!=1:
            raise ValueError('Label/object requires anchor point')
        pts=[_point(p) for p in pts]
        style=c.get('style','UNKNOWN')
        if style not in VALID_STYLES:raise ValueError('Unknown stroke style')
        label=c.get('label','')
        if not isinstance(label,str) or len(label)>140:raise ValueError('Invalid label')
        if c['kind']=='HYPOTHETICAL_ROUTE' and style!='UNKNOWN':
            # An inferred route cannot also masquerade as ink evidence.
            raise ValueError('Proposed routes cannot be labeled observed ink style')
        checked.append({'id':id,'kind':c['kind'],'style':style,'points':pts,'label':label})
    return {'source_id':source_id,'claims':checked,'model_uncertainty':str(packet.get('uncertainty',''))[:300],
            'claimed_complete_route':bool(packet.get('claimed_complete_route',False))}


def _point_line_distance(p:tuple[float,float],a:tuple[float,float],b:tuple[float,float])->float:
    dx=b[0]-a[0];dy=b[1]-a[1];dd=dx*dx+dy*dy
    if dd<=1e-10:return math.hypot(p[0]-a[0],p[1]-a[1])
    t=max(0,min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/dd))
    return math.hypot(p[0]-(a[0]+t*dx),p[1]-(a[1]+t*dy))


def dash_evidence(points, candidates:tuple[DashCandidate,...], tolerance=.022):
    """Require repeated detected source stroke centers, not just paper lines.

    Score is a *proxy* for proximity, not confidence that a human intended a fence.
    """
    if len(points)<2:return (0.,())
    a,b=points[0],points[-1]
    if math.dist(a,b)<.04:return (0.,())
    matching=[];scores=[]
    for c in candidates:
        if len(c.points)<3:continue
        hits=[p for p in c.points if _point_line_distance(p,a,b)<=tolerance]
        if len(hits)<3:continue
        # Prevent accidental support by tiny patches on a very long imagined line.
        proj=[]
        dx=b[0]-a[0];dy=b[1]-a[1];den=dx*dx+dy*dy
        for p in hits:
            t=((p[0]-a[0])*dx+(p[1]-a[1])*dy)/den
            if 0<=t<=1:proj.append(t)
        if len(proj)<3:continue
        spread=max(proj)-min(proj)
        fraction=len(proj)/len(c.points)
        score=min(1.,(spread/.35))*min(1.,fraction)*min(1.,len(proj)/5)
        if score>=.18:
            matching.append(c.id);scores.append(score)
    return (round(max(scores,default=0.),3),tuple(sorted(set(matching))))


def review(packet:dict,sketch,source_id:str, *, detector=None)->dict:
    norm=validate_packet(packet,source_id)
    candidates=extract_dashes(sketch) if detector is None else tuple(detector)
    reviews=[]
    for c in norm['claims']:
        score,matches=dash_evidence(c['points'],candidates) if c['style']=='DOTTED' else (0.,())
        if c['kind']=='HYPOTHETICAL_ROUTE':
            v='PROPOSAL_ONLY';reasons=['No source drawing can certify an imagined construction']
        elif c['kind'] in ('TEXT_LABEL','OBJECT'):
            v='MODEL_LABEL_REQUIRES_INDEPENDENT_REVIEW';reasons=['Pixel-to-word/object interpretation not independently verified']
        elif c['style']=='DOTTED':
            if matches:
                v='INK_COMPATIBLE_INTENT_UNVERIFIED';reasons=['At least three source-detected dash strokes agree','Mark meaning and unmarked gaps remain unverified']
            else:
                v='HOLD_UNSUPPORTED_DOTTED_TRACE';reasons=['No adequate independent dash-ink support along suggested segment']
        elif c['style']=='SOLID':
            v='HOLD_SOLID_STYLE_NOT_VERIFIED';reasons=['Ruled paper and structures can resemble solid boundary lines']
        else:
            v='HOLD_UNKNOWN_STYLE';reasons=['No proposed mark style']
        reviews.append(Review(c['id'],c['style'],v,matches,score,tuple(reasons)))
    # Critique does not automatically convert HOLD into a positive premise.
    held=sum(r.verdict.startswith('HOLD') for r in reviews)
    good=sum(r.verdict=='INK_COMPATIBLE_INTENT_UNVERIFIED' for r in reviews)
    contradiction=['The model claims a complete route, but no completeness evidence exists'] if norm['claimed_complete_route'] else []
    out={'experiment':'FIELD-008','source_id':source_id,'claims':norm['claims'],
         'reviews':[asdict(x) for x in reviews], 'detected_dash_groups':len(candidates),
         'ink_compatible':good,'held':held,'critic_contradictions':contradiction,
         'complete_route_verified':False,'real_world_length_known':False,
         'model_claims_promoted_to_user_observation':0,'revisions_automatic':False,
         'next_probe':next_probe(reviews, candidates),
         'safety_certified':False,'geometry_space':'SOURCE_IMAGE_NORMALIZED_NOT_SURVEYED'}
    out['receipt_sha256']=sha256(json.dumps(out,sort_keys=True).encode()).hexdigest()
    return out


def next_probe(reviews, candidates):
    # Choose question that has highest decision-relevant epistemic gap.
    if any(r.verdict=='HOLD_UNSUPPORTED_DOTTED_TRACE' for r in reviews):
        return 'Reinspect the unsupported proposed dotted stroke against an enlarged original-image crop.'
    if any(r.verdict=='INK_COMPATIBLE_INTENT_UNVERIFIED' for r in reviews):
        return 'Check whether each ink-supported dashed fragment actually belongs to the intended new boundary.'
    if candidates:return 'Ask a visual model to label the pixel-detected dash groups without inventing connections.'
    return 'Acquire a clearer image or a different view; do not invent missing boundary geometry.'


def overlay(sketch,packet:dict,report:dict,out_file:str|Path):
    """Keep source marks visible. Green = individual *ink boxes*, not fences.

    Unsupported model traces appear as spaced candidate dashes, deliberately
    never as a drawn continuous completed boundary. Image remains unwarped.
    """
    if isinstance(sketch,(str,Path)):
        img=cv2.imread(str(sketch),cv2.IMREAD_COLOR)
        if img is None:raise ValueError('Image not found')
    else:
        img=sketch.copy()
        if img.ndim==2:img=cv2.cvtColor(img,cv2.COLOR_GRAY2BGR)
    H,W=img.shape[:2]
    byid={x['claim_id']:x for x in report['reviews']}
    known={c.id:c for c in extract_dashes(sketch)}

    def draw_questioned_dashes(a,b,col):
        vx=b[0]-a[0];vy=b[1]-a[1]
        length=max(1,math.hypot(vx,vy))
        step=max(9,round(min(W,H)*.02))
        dash=max(3,round(step*.45))
        for j in range(0,int(length),step):
            t=j/length;s=min(1,(j+dash)/length)
            p1=(round(a[0]+vx*t),round(a[1]+vy*t))
            p2=(round(a[0]+vx*s),round(a[1]+vy*s))
            cv2.line(img,p1,p2,col,2,cv2.LINE_AA)
    for c in report['claims']:
        pts=[(round(p[0]*W),round(p[1]*H)) for p in c['points']]
        rv=byid[c['id']]['verdict']
        good=rv=='INK_COMPATIBLE_INTENT_UNVERIFIED'
        color=(10,145,10) if good else (0,50,230)
        if c['kind']=='HYPOTHETICAL_ROUTE':color=(160,90,170)
        if good:
            for candidate_id in byid[c['id']]['matched_dash_ids']:
                candidate=known.get(candidate_id)
                if candidate:
                    for x,y,w,h in candidate.pixel_boxes:
                        cv2.rectangle(img,(x-2,y-2),(x+w+2,y+h+2),color,2)
        elif len(pts)>=2:
            for a,b in zip(pts,pts[1:]):draw_questioned_dashes(a,b,color)
        if pts:
            cv2.circle(img,pts[0],7,color,2,cv2.LINE_AA)
            label=('INK? ' if good else 'CHECK? ')+c['id'][:15]
            cv2.putText(img,label,(max(1,pts[0][0]-20),max(16,pts[0][1]-12)),
                        cv2.FONT_HERSHEY_SIMPLEX,.50,color,2,cv2.LINE_AA)
    cv2.imwrite(str(out_file),img)
    return str(out_file)