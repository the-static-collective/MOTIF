"""Conservative photo feature matching, not camera pose or world coordinates.

Repeated chain-link textures can create false correspondences. Failure to match
never means two photos show different physical objects. Local-only OpenCV.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from pathlib import Path
import cv2
import numpy as np

@dataclass(frozen=True)
class Pair:
    left: str
    right: str
    raw_ratio_matches: int
    geometric_inliers: int
    source_coverage: float
    target_coverage: float
    status: str
    reason: str

def _image(src):
    if isinstance(src,(str,Path)):
        im=cv2.imread(str(src),cv2.IMREAD_GRAYSCALE)
        if im is None:raise ValueError('Missing photo')
    else:
        im=cv2.cvtColor(src,cv2.COLOR_BGR2GRAY) if src.ndim==3 else src
    if im.ndim!=2 or min(im.shape)<90:raise ValueError('Unsupported photo')
    H,W=im.shape
    target=900
    if max(H,W)>target:
        q=target/max(H,W)
        im=cv2.resize(im,(round(W*q),round(H*q)),interpolation=cv2.INTER_AREA)
    return im

def compare(left,right,left_id='photo-a',right_id='photo-b') -> Pair:
    a=_image(left);b=_image(right)
    orb=cv2.ORB_create(nfeatures=1400,fastThreshold=14)
    ka,da=orb.detectAndCompute(a,None)
    kb,db=orb.detectAndCompute(b,None)
    if da is None or db is None or len(ka)<16 or len(kb)<16:
        return Pair(left_id,right_id,0,0,0.,0.,'HOLD','INSUFFICIENT_FEATURES')
    matcher=cv2.BFMatcher(cv2.NORM_HAMMING)
    fw=matcher.knnMatch(da,db,k=2)
    bw=matcher.knnMatch(db,da,k=2)
    rfw={m.queryIdx:m.trainIdx for two in fw if len(two)==2 for m,n in [two] if m.distance<.67*n.distance}
    rbw={m.queryIdx:m.trainIdx for two in bw if len(two)==2 for m,n in [two] if m.distance<.67*n.distance}
    pairs=[(ka[i].pt,kb[j].pt) for i,j in rfw.items() if rbw.get(j)==i]
    if len(pairs)<12:
        return Pair(left_id,right_id,len(pairs),0,0.,0.,'HOLD','NOT_ENOUGH_SYMMETRIC_MATCHES')
    pa=np.float32([p[0] for p in pairs]).reshape(-1,1,2)
    pb=np.float32([p[1] for p in pairs]).reshape(-1,1,2)
    _,mask=cv2.findHomography(pa,pb,cv2.RANSAC,4.0)
    if mask is None:
        return Pair(left_id,right_id,len(pairs),0,0.,0.,'HOLD','NO_GEOMETRIC_CONSENSUS')
    ok=mask.ravel().astype(bool)
    inliers=int(ok.sum())
    if inliers<10:
        return Pair(left_id,right_id,len(pairs),inliers,0.,0.,'HOLD','FEW_GEOMETRIC_INLIERS')
    def cov(points,shape):
        q=points.reshape(-1,2)[ok]
        if len(q)<3:return 0.
        x1,y1=q.min(axis=0);x2,y2=q.max(axis=0)
        return round(float((x2-x1)*(y2-y1)/(shape[0]*shape[1])),4)
    ca,cb=cov(pa,a.shape),cov(pb,b.shape)
    if min(ca,cb)<.045:
        return Pair(left_id,right_id,len(pairs),inliers,ca,cb,'HOLD','MATCHES_TOO_LOCALIZED_OR_REPETITIVE')
    return Pair(left_id,right_id,len(pairs),inliers,ca,cb,'TENTATIVE_VISUAL_OVERLAP','IMAGE_FEATURE_MATCH_ONLY__NOT_GEOREGISTERED')

def cross_photo_packet(entries:list[tuple[str,str]],max_photos=15) -> dict:
    if not 0<=len(entries)<=max_photos:raise ValueError('Too many photos')
    ids=[x[0] for x in entries]
    if len(ids)!=len(set(ids)):raise ValueError('Duplicate photo ids')
    results=[asdict(compare(path1,path2,id1,id2))
             for i,(id1,path1) in enumerate(entries)
             for (id2,path2) in entries[i+1:]]
    return {'type':'LOCAL_TENTATIVE_IMAGE_CORRESPONDENCE',
            'auto_world_coordinates':False,'photo_count':len(entries),
            'pair_count':len(results),'pairs':results,
            'verified_shared_scene':False,'model_calls':0}
