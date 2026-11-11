"""Non-blind author-generated sketch regression; not a general vision benchmark."""
import json
import numpy as np
import cv2
from ink import extract_dashes

def gen(seed,mode):
    rng=np.random.default_rng(seed);H,W=420,640
    g=np.clip(224+rng.normal(0,3.5,(H,W)),0,255).astype(np.uint8)
    for y in range(27,H,23):cv2.line(g,(20,y),(W-22,y),185,1)
    cv2.line(g,(120,332),(510,332),30,3)
    if mode in ('both','horizontal'):
        for x in range(95,435,38):
            dy=int(rng.integers(-2,3));cv2.line(g,(x,91+dy),(x+15,91+dy),35,2)
    if mode=='both':
        for y in range(146,331,30):
            dx=int(rng.integers(-2,3));cv2.line(g,(531+dx,y),(531+dx,y+13),35,2)
    cv2.rectangle(g,(30,150),(92,295),38,2)
    cv2.putText(g,'A',(230,275),cv2.FONT_HERSHEY_SIMPLEX,1.4,40,2)
    return g

def detected(found):
    def eligible(c,axis,coord,tol):
        if c.axis!=axis or len(c.points)<3:return False
        avg=sum(p[1 if axis=='H' else 0] for p in c.points)/len(c.points)
        return abs(avg-coord)<=tol
    return {'H':any(eligible(c,'H',91/420,.035) for c in found),
            'V':any(eligible(c,'V',531/640,.035) for c in found)}

def run(n=18,stress=8):
    cases=[]
    for i in range(n):
        mode=('both','horizontal','ruled_solid_only')[i%3]
        pred=detected(extract_dashes(gen(130+i,mode)))
        expected={'H':mode in ('both','horizontal'),'V':mode=='both'}
        cases.append({'seed':130+i,'mode':mode,'pred':pred,'expected':expected})
    tp=sum(c['pred'][k] and c['expected'][k] for c in cases for k in ('H','V'))
    fp=sum(c['pred'][k] and not c['expected'][k] for c in cases for k in ('H','V'))
    fn=sum(not c['pred'][k] and c['expected'][k] for c in cases for k in ('H','V'))
    rotated=[]
    for j,angle in enumerate([4,-4,9,-9,14,-14,20,-20][:stress]):
        im=gen(888+j,'both')
        M=cv2.getRotationMatrix2D((320,210),angle,1.)
        im=cv2.warpAffine(im,M,(640,420),borderValue=224)
        found=extract_dashes(im)
        rotated.append({'angle_degrees':angle,'found_both_axes':set(c.axis for c in found)>={'H','V'}})
    return {'type':'AUTHOR_GENERATED_TEST_NOT_BLIND','scenes':n,
            'rotated_stress_scenes':len(rotated),
            'rotated_found_both_axes':sum(r['found_both_axes'] for r in rotated),
            'rotated_controls':rotated,'true_positive':tp,'false_positive':fp,'false_negative':fn,
            'precision':round(tp/(tp+fp),3) if tp+fp else None,
            'recall':round(tp/(tp+fn),3) if tp+fn else None,
            'cases':cases,'true_real_photo_VLM_trials':0,'certified_complete_boundaries':0}
if __name__=='__main__':
    r=run()
    print(json.dumps({k:v for k,v in r.items() if k not in ('cases','rotated_controls')},indent=2))
