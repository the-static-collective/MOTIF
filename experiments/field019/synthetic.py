"""Synthetic calibrated multi-view scene, including purposely corrupted controls.
Not a demonstration of parsing real property photographs.
"""
import numpy as np, cv2, json
from scipy.spatial.transform import Rotation
from fusion import HEIGHT_M,world_points

NAMES=['p1','p2','p3','p4','p5','p6']
SKETCH=np.array([[0.,0.],[.7,0.],[1.35,.4],[1.5,1.25],[.4,1.5],[-.3,.6]])
TRUE_SCALE=2.8
CAMS=[(np.array([.3,-1.70,-10.5]),np.array([.025,-.06,.012]),1100.),
      (np.array([3.7,-1.58,-9.5]),np.array([-.025,.18,-.015]),1100.)]

def packet(seed=0,sketch_noise=0.,pixel_noise=.4,height=HEIGHT_M,corrupt=False, views=2):
    rng=np.random.default_rng(seed)
    sketch=SKETCH + rng.normal(0,sketch_noise,SKETCH.shape)
    packet={'height_reference_m':height,'height_source':'SYNTHETIC_CERTAIN',
            'sketch_proportionality':'ASSUMED_WITH_TOLERANCE','sketch_tolerance_fraction':.1,
            'landmarks':{n:list(map(float,p)) for n,p in zip(NAMES,sketch)}, 'views':[]}
    points=world_points(SKETCH,TRUE_SCALE,HEIGHT_M)
    for c,(center,rpy,f) in enumerate(CAMS[:views]):
        R=Rotation.from_euler('xyz',rpy).as_matrix();rvec=cv2.Rodrigues(R)[0];t=-R@center
        K=np.array([[f,0,480],[0,f,360],[0,0,1]],float)
        pix=cv2.projectPoints(points.reshape(-1,3),rvec,t,K,None)[0].reshape(-1,2,2)
        pix=pix+rng.normal(0,pixel_noise,pix.shape)
        if corrupt and c==1: pix[2,0]+=np.array([70,-60])
        packet['views'].append({'source':f'synthetic_camera_{c+1}','size':[960,720],
                                'focal_px':float(f),'focal_provenance':'SYNTHETIC_CERTAIN','correspondences_source':'INDEPENDENT_REVIEWED',
                                'points':{n:np.clip(pix[j],[0,0],[960,720]).tolist() for j,n in enumerate(NAMES)}})
    return packet

if __name__=='__main__':
    from fusion import fuse
    for label,cfg in [('clean',{}),('sketch_noisy',{'sketch_noise':.08}),('mismatch',{'corrupt':True})]:
        out=fuse(packet(2,**cfg))
        print(label,out.status,out.horizontal_m_per_sketch_unit,out.reprojection_rms_px, out.diagnostics)
