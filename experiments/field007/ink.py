"""FIELD-007: local, tentative dash-ink candidates from a source sketch.

No text recognition, no geographic mapping. Depends on OpenCV and numpy.
Every candidate is tentative, never a verified user's intended fence boundary.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from hashlib import sha256
from pathlib import Path
import cv2
import numpy as np

@dataclass(frozen=True)
class DashCandidate:
    id: str
    axis: str
    points: tuple[tuple[float,float], ...]
    pixel_boxes: tuple[tuple[int,int,int,int], ...]
    width_pixels: int
    ink_support: float
    quality: str = 'TENTATIVE_DASH_LIKE_NOT_CONFIRMED_INTENT'

    def as_packet(self, source: str) -> dict:
        return {'source':source,'kind':'DESIRED','points':[list(p) for p in self.points],
                'status':'TENTATIVE','note':f'CV dash-like candidate {self.id}, axis={self.axis}, ink_support={self.ink_support:.2f}; original mark meaning unknown'}

def page_bbox(g: np.ndarray) -> tuple[int,int,int,int]:
    h,w=g.shape
    bright=cv2.morphologyEx((g>145).astype('uint8')*255,cv2.MORPH_CLOSE,
                              cv2.getStructuringElement(cv2.MORPH_RECT,(21,21)))
    contours,_=cv2.findContours(bright,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    if not contours:return (0,0,w,h)
    box=max((cv2.boundingRect(c) for c in contours),key=lambda r:r[2]*r[3])
    if box[2]*box[3]<.22*w*h:return (0,0,w,h)
    return tuple(int(x) for x in box)

def _bridge_ink_fraction(ink, chunk, axis):
    """Recheck dark pixels in detected dash gaps on original, pre-removal image."""
    occ=[]
    for a,b in zip(chunk,chunk[1:]):
        axis_i=0 if axis=='H' else 1
        width0=a[2][2+axis_i];width1=b[2][2+axis_i]
        gap=b[axis_i]-a[axis_i]-(width0+width1)/2
        if gap<8:continue
        samples=[]
        for j in range(max(3,int(gap))):
            t=(j+0.5)/max(3,int(gap))
            if t<.12 or t>.88:continue
            loc=(1-t)*np.array(a[:2])+t*np.array(b[:2]);px=int(round(loc[0]));py=int(round(loc[1]))
            if axis=='H':
                pix=ink[max(0,py-2):py+3,min(max(0,px),ink.shape[1]-1)]
            else:
                pix=ink[min(max(0,py),ink.shape[0]-1),max(0,px-2):px+3]
            if pix.size:samples.append(bool(np.any(pix)))
        if samples:occ.append(sum(samples)/len(samples))
    return sum(occ)/len(occ) if occ else 0.0

def extract_dashes(image: str|Path|np.ndarray, *, max_candidates=12, paper_bbox=None) -> tuple[DashCandidate,...]:
    """Detect broken strokes; do not convert them into completed perimeter paths."""
    if isinstance(image,(str,Path)):
        raw=cv2.imread(str(image),cv2.IMREAD_GRAYSCALE)
        if raw is None:raise ValueError('Unable to read source image')
    elif isinstance(image,np.ndarray):
        raw=cv2.cvtColor(image,cv2.COLOR_BGR2GRAY) if image.ndim==3 else image
        if raw.ndim!=2:raise ValueError('Expected mono/rgb image')
    else:raise TypeError('Unsupported image input')
    H,W=raw.shape
    if H<90 or W<90:raise ValueError('Image too small')
    x0,y0,pw,ph=paper_bbox or page_bbox(raw)
    if not(0<=x0<W and 0<=y0<H and pw>70 and ph>70 and x0+pw<=W and y0+ph<=H):
        raise ValueError('Invalid page extent')
    bg=cv2.GaussianBlur(raw,(0,0),max(6.0,min(W,H)/55.0))
    ink=(cv2.subtract(bg,raw)>34).astype('uint8')*255
    long_h=cv2.morphologyEx(ink,cv2.MORPH_OPEN,
             cv2.getStructuringElement(cv2.MORPH_RECT,(max(65,int(W*.055)),1)))
    clean=cv2.subtract(ink,cv2.dilate(long_h,np.ones((3,3),np.uint8)))
    _,_,stats,centroids=cv2.connectedComponentsWithStats(clean)
    strokes={'H':[],'V':[]}
    for i in range(1,len(stats)):
        x,y,w,h,area=map(int,stats[i]);cx,cy=map(float,centroids[i])
        if not (x0+pw*.023<cx<x0+pw*.978 and y0+ph*.075<cy<y0+ph*.982):continue
        if w>=7 and w<=max(45,W*.06) and 1<=h<=8 and area>=9 and w/h>=1.7:
            strokes['H'].append((cx,cy,(x,y,w,h)))
        if h>=7 and h<=max(45,H*.07) and 1<=w<=8 and area>=9 and h/w>=1.7:
            strokes['V'].append((cx,cy,(x,y,w,h)))
    groups=[]
    raw_ink=(cv2.subtract(bg,raw)>34)
    for axis,arr in strokes.items():
        axis_idx=0 if axis=='H' else 1
        cross=1-axis_idx
        arr.sort(key=lambda z:z[axis_idx])
        candidates=[]
        for i,a in enumerate(arr):
            for b in arr[i+1:min(i+28,len(arr))]:
                delta=b[axis_idx]-a[axis_idx]
                if not 12<=delta<=110:continue
                dc=b[cross]-a[cross]
                if abs(dc)>max(8,delta*(.45 if axis=='V' else .10)):continue
                slope=dc/delta
                inliers=[]
                for p in arr:
                    dist=p[axis_idx]-a[axis_idx]
                    if abs((p[cross]-a[cross])-dist*slope)<=4.8:
                        inliers.append(p)
                inliers.sort(key=lambda p:p[axis_idx])
                chunks=[];current=[]
                for p in inliers:
                    if current and p[axis_idx]-current[-1][axis_idx]>90:
                        if len(current)>=3:chunks.append(current)
                        current=[]
                    current.append(p)
                if len(current)>=3:chunks.append(current)
                for chunk in chunks:
                    span=chunk[-1][axis_idx]-chunk[0][axis_idx]
                    if span < (42 if axis=='V' else 58):continue
                    gaps=[]
                    for left,right in zip(chunk,chunk[1:]):
                        edge0=left[axis_idx]+left[2][2+axis_idx]/2
                        edge1=right[axis_idx]-right[2][2+axis_idx]/2
                        gaps.append(edge1-edge0)
                    nreal=sum(z>=4 for z in gaps)
                    if nreal < 2 or nreal < (len(chunk)-1)*.6:continue
                    raw_bridge=_bridge_ink_fraction(raw_ink,chunk,axis)
                    if raw_bridge>=.68:continue
                    ink_width=sum(p[2][2+axis_idx] for p in chunk)
                    score=len(chunk)+min(span/50,8)+nreal*1.2 - max(0,(ink_width/span)-.5)*10
                    candidates.append((score,tuple(chunk)))
        candidates.sort(key=lambda z:(-z[0],-len(z[1])))
        used=set()
        for score,chunk in candidates:
            inds=set((int(p[0]),int(p[1])) for p in chunk)
            if any(len(inds & other)/max(1,min(len(inds),len(other)))>.6 for other in used):continue
            used.add(frozenset(inds))
            pts=tuple((round(p[0]/W,5),round(p[1]/H,5)) for p in chunk)
            boxes=tuple(tuple(map(int,p[2])) for p in chunk)
            span=int(chunk[-1][axis_idx]-chunk[0][axis_idx])
            support=round(min(1.0,len(chunk)/8)*min(1.,span/180),3)
            groups.append((score,DashCandidate(f'{axis.lower()}-{len(groups)+1:02d}',axis,pts,boxes,span,support)))
    groups.sort(key=lambda x:-x[0])
    return tuple(x[1] for x in groups[:max_candidates])

def trace_receipt(image: str|Path|np.ndarray, candidates:tuple[DashCandidate,...]) -> dict:
    if isinstance(image,np.ndarray):
        ok,blob=cv2.imencode('.png',image)
        if not ok:raise ValueError('Cannot encode source image')
        data=blob.tobytes()
    else:
        data=Path(image).read_bytes()
    return {'algorithm':'FIELD-007-dash-segments-v1','input_sha256':sha256(data).hexdigest(),
            'candidate_count':len(candidates),'candidates':[asdict(c) for c in candidates],
            'boundary_confirmed':False,'geometric_scale_known':False,'real_model_calls':0}

def overlay(image:str|Path, candidates:tuple[DashCandidate,...], out:str|Path):
    """Only measured boxes: never fill the gaps to invent a fence."""
    raw=cv2.imread(str(image))
    if raw is None:raise ValueError('missing image')
    H,W=raw.shape[:2]
    canvas=raw.copy()
    color={'H':(0,110,240),'V':(190,80,215)}
    for k,c in enumerate(candidates):
        col=color[c.axis]
        for x,y,w,h in c.pixel_boxes:
            cv2.rectangle(canvas,(x-2,y-2),(x+w+2,y+h+2),col,2)
        if c.points:
            x,y=c.points[0];px=int(x*W);py=int(y*H)
            cv2.putText(canvas,f'?{k+1} {c.axis}',(max(0,px),max(18,py-11)),
                        cv2.FONT_HERSHEY_SIMPLEX,.55,col,2,cv2.LINE_AA)
    cv2.imwrite(str(out),canvas)
    return str(out)
