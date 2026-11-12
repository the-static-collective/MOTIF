"""FIELD-019: source-linked sketch+image+height joint geometric inference.

A constrained, classical geometric bundle: unknown horizontal sketch scale plus a
camera pose for every photo, conditional on known intrinsics, independently
corresponded post-top/post-base image pixels, a shared ground plane and the
same physical height reference. Estimation cannot prove these assumptions.

Coordinate convention: (X, Y, Z), Y negative above ground, camera +Z forward.
Cameras represented as OpenCV Rodrigues (rvec, tvec); all length units meters.
"""
from __future__ import annotations
from dataclasses import dataclass
from math import exp, log, sqrt, isfinite
import hashlib, json
import numpy as np
import cv2
from scipy.optimize import least_squares

HEIGHT_M = 1.8288

class EvidenceError(ValueError):
    pass

@dataclass
class Candidate:
    status: str
    reason: str
    horizontal_m_per_sketch_unit: float | None
    reprojection_rms_px: float | None
    camera_poses: list[dict]
    predicted_world: list[dict]
    diagnostics: dict

    def to_dict(self):
        return dict(status=self.status, reason=self.reason, horizontal_m_per_sketch_unit=self.horizontal_m_per_sketch_unit,
                    reprojection_rms_px=self.reprojection_rms_px, camera_poses=self.camera_poses,
                    predicted_world=self.predicted_world, diagnostics=self.diagnostics)


def K_from_camera(cam):
    w,h=cam['size']; f=cam.get('focal_px')
    if cam.get('focal_provenance') not in {'SYNTHETIC_CERTAIN','INDEPENDENT_CALIBRATED','USER_REVIEWED_CALIBRATION'}:
        raise EvidenceError('Camera focal prior lacks reviewed provenance; single uncalibrated photo cannot set geometry')
    if f is None or not isinstance(f,(float,int)) or not isfinite(f) or f <=0:
        raise EvidenceError('Independent camera calibration unavailable: focal length needed before metric inference')
    return np.array([[f,0,w/2.],[0,f,h/2.],[0,0,1.]],float)


def validate(packet):
    if packet.get('height_reference_m') is None or not packet.get('height_source'):
        raise EvidenceError('No source-linked known height')
    H=packet['height_reference_m']
    if not (isinstance(H,(float,int)) and 0<H<10):raise EvidenceError('Bad height')
    if packet.get('sketch_proportionality')!='ASSUMED_WITH_TOLERANCE':
        raise EvidenceError('Unreviewed sketch distortion: preserve drawn-only geometry')
    if packet.get('sketch_tolerance_fraction') is None or not 0<=packet['sketch_tolerance_fraction']<=.3:
        raise EvidenceError('Missing explicit sketch assumption tolerance')
    pts=packet.get('landmarks',{})
    if len(pts)<5:raise EvidenceError('Need five or more independently identified landmarks')
    ids=list(pts)
    ground=np.array([pts[k] for k in ids],float)
    if ground.shape!=(len(ids),2) or not np.isfinite(ground).all():raise EvidenceError('Bad sketch coords')
    if np.linalg.matrix_rank(ground-ground.mean(axis=0)) <2:raise EvidenceError('Collinear sketch geometry insufficient')
    views=packet.get('views',[])
    if len(views)<2:raise EvidenceError('At least two photo views required for cross-view acceptance')
    if len(set(cam['source'] for cam in views))!=len(views):raise EvidenceError('Duplicate photo evidence IDs')
    for cam in views:
        K_from_camera(cam)
        if cam.get('correspondences_source') not in ('USER_REVIEWED','INDEPENDENT_REVIEWED'):
            raise EvidenceError('Tentative/model-only pixel correspondences cannot calibrate world geometry')
        obs=cam.get('points',{})
        if len(set(obs)&set(ids))<5:raise EvidenceError('Too few image-sketch correspondences')
        for name, pair in obs.items():
            if name not in pts:raise EvidenceError('Photo contains unmapped landmark')
            p=np.asarray(pair,float)
            if p.shape!=(2,2) or not np.isfinite(p).all():raise EvidenceError('Photo must include top+base 2D point per landmark')
            w,h=cam['size']
            if not ((p[:,0]>=0).all() and (p[:,0]<=w).all() and (p[:,1]>=0).all() and (p[:,1]<=h).all()):
                raise EvidenceError('Pixel outside image')
    return ids,ground


def world_points(ground, scale, height):
    base=np.column_stack((scale*ground[:,0], np.zeros(len(ground)), scale*ground[:,1]))
    top=base.copy();top[:,1]=-height
    return np.stack((top,base),axis=1)


def _view_arrays(packet,ids,world):
    by_id={name:i for i,name in enumerate(ids)}
    out=[]
    for cam in packet['views']:
        pairs=list(cam['points'].items())
        idx=[by_id[name] for name,_ in pairs]
        X=world[idx].reshape(-1,3)
        q=np.array([pair for _,pair in pairs],float).reshape(-1,2)
        out.append((cam,X,q,K_from_camera(cam),idx))
    return out


def _camera_init(worldviews):
    poses=[];e=[]
    for cam,X,q,K,idx in worldviews:
        success,rvec,tvec=cv2.solvePnP(X.astype(np.float64),q.astype(np.float64),K,np.zeros(5),flags=cv2.SOLVEPNP_EPNP)
        if not success:return None,float('inf')
        success,rvec,tvec=cv2.solvePnP(X.astype(np.float64),q.astype(np.float64),K,np.zeros(5),rvec=rvec,tvec=tvec,useExtrinsicGuess=True,flags=cv2.SOLVEPNP_ITERATIVE)
        if not success:return None,float('inf')
        uv=cv2.projectPoints(X,rvec,tvec,K,None)[0].reshape(-1,2)
        e.extend((uv-q).reshape(-1))
        poses.append(np.concatenate((rvec.reshape(3),tvec.reshape(3))))
    return poses,float(np.linalg.norm(e)/sqrt(max(1,len(e))))


def _project(X,pose,K):
    return cv2.projectPoints(X,pose[:3],pose[3:],K,None)[0].reshape(-1,2)


def _solve_one_scale(packet,ids,ground,scale):
    w=world_points(ground,scale,packet['height_reference_m'])
    return _camera_init(_view_arrays(packet,ids,w))


def fuse(packet, *, max_rms_px=6., scale_grid=None, allow_sketch_correction=True):
    """Reconstruct conditional scale + camera poses, fail closed on poor fit.

    Pose is conditional on GIVEN approximate camera intrinsics and reviewed top/base
    matches. A small residual is not independent evidence of matching correctness.
    """
    try:ids,ground=validate(packet)
    except EvidenceError as err:return Candidate('HOLD_UNDERCONSTRAINED',str(err),None,None,[],[],{})
    if scale_grid is None:scale_grid=np.geomspace(.12,8.,32)
    scored=[]
    for s in scale_grid:
        poses,error=_solve_one_scale(packet,ids,ground,float(s))
        if poses is not None and np.isfinite(error):scored.append((error,s,poses))
    if not scored:return Candidate('HOLD_CAMERA_FIT','No valid camera pose estimates',None,None,[],[],{})
    scored.sort(key=lambda x:x[0]); _,s0,pose0=scored[0]
    def get_resid(z):
        s=np.exp(z[0]);w=world_points(ground,s,packet['height_reference_m'])
        ret=[]
        for i,(_,X,q,K,idx) in enumerate(_view_arrays(packet,ids,w)):
            ret.extend((_project(X,z[1+i*6:1+(i+1)*6],K)-q).reshape(-1))
        return np.array(ret)
    x0=np.concatenate(([np.log(s0)], *pose0))
    initial=get_resid(x0)
    fit=least_squares(get_resid,x0,loss='linear',max_nfev=150,ftol=1e-9,xtol=1e-9,gtol=1e-9)
    res=get_resid(fit.x)
    initial_rms=float(np.sqrt(np.mean(res*res)))
    raw_offsets=np.zeros((len(ids),2))
    if allow_sketch_correction and initial_rms>1.2:
        # Jointly modify *hypothetical* sketch points, never the original source.
        # A soft prior bounds repairs: marked sketch coordinates are noisy clues,
        # not surveyed ground truth. The evidence receipt retains corrections.
        span=float(np.linalg.norm(np.ptp(ground,axis=0)))
        sigma=max(.015, span*packet['sketch_tolerance_fraction']*.65)
        def _adjusted_residual(z):
            off=z[-len(ids)*2:].reshape(-1,2)
            adjusted=ground+off
            scale=np.exp(z[0]); world=world_points(adjusted,scale,packet['height_reference_m'])
            out=[]
            for i,(_,X,q,K,idx) in enumerate(_view_arrays(packet,ids,world)):
                out.extend((_project(X,z[1+i*6:1+(i+1)*6],K)-q).reshape(-1))
            # Place the soft sketch-metric prior in pixel units to balance terms.
            out.extend((off/sigma*2.0).reshape(-1))
            return np.array(out)
        adjusted_x0=np.concatenate((fit.x,np.zeros(len(ids)*2)))
        a=least_squares(_adjusted_residual,adjusted_x0,loss='soft_l1',f_scale=3.0,max_nfev=300)
        off=a.x[-len(ids)*2:].reshape(-1,2)
        adjusted=ground+off
        world=world_points(adjusted,np.exp(a.x[0]),packet['height_reference_m'])
        final_data=[]
        for i,(_,X,q,K,idx) in enumerate(_view_arrays(packet,ids,world)):
            final_data.extend((_project(X,a.x[1+i*6:1+(i+1)*6],K)-q).reshape(-1))
        updated=np.array(final_data)
        if np.sqrt(np.mean(updated*updated))<initial_rms:
            fit=a;res=updated;raw_offsets=off
    rms=float(np.sqrt(np.mean(res*res)))
    # Diagnostic: if a large family of scales provides indistinguishable fit,
    # the problem has not identified metric ground scale.
    local_s=np.exp(fit.x[0]);
    scale_test=[]
    for factor in (.7,1.0,1.3):
        poses,e=_solve_one_scale(packet,ids,ground+raw_offsets,local_s*factor)
        scale_test.append({'factor':factor,'rms_px':round(e,4)})
    xnorm=np.linalg.norm(res.reshape(-1,2),axis=1)
    outlier_count=int(np.sum(xnorm>max_rms_px*2))
    info={ 'height_source':packet['height_source'],'sketch_proportionality':'ASSUMED_WITH_TOLERANCE',
          'camera_intrinsics':'EXTERNALLY_SUPPLIED_NOT_INFERRED',
          'camera_focal_provenance':[v.get('focal_provenance') for v in packet['views']],
          'max_reprojection_rms_px':max_rms_px,'worst_point_error_px':round(float(np.max(xnorm)),3),
          'large_residual_point_count':outlier_count,'scale_sensitivity_given_fitted_sketch_correction':scale_test,
          'independent_ground_truth':False,'assumed_sketch_distortion_fraction':packet['sketch_tolerance_fraction'],
          'photo_pair_auto_registered':False, 'real_model_inference':False,
          'initial_fit_rms_px':round(initial_rms,3),
          'sketch_correction_max_fraction_of_extent':round(float(np.max(np.linalg.norm(raw_offsets,axis=1)) / max(1e-6,np.linalg.norm(np.ptp(ground,axis=0)))),4),
          'sketch_correction_proposed_not_observed':True}
    # A scale profile holds fitted sketch offsets fixed: conditional local check,
    # not a global identifiability proof when sketch corrections are free.
    # An unusually wide scale ambiguity remains a HOLD even if the best error is small.
    # Use a relative increase threshold of 0.6px at +/-30% scale as an illustrative identifiability probe.
    sensitivity=min(scale_test[0]['rms_px']-scale_test[1]['rms_px'],scale_test[2]['rms_px']-scale_test[1]['rms_px'])
    if info['sketch_correction_max_fraction_of_extent']>packet['sketch_tolerance_fraction']*1.15:
        status='HOLD_SKETCH_CORRECTION_TOO_LARGE';reason='Photos disagree with the assumed sketch proportionality beyond its stated tolerance'
    elif rms>max_rms_px or outlier_count>0: status='HOLD_CONTRADICTORY_CORRESPONDENCE';reason='Reprojection fit inconsistent with reviewed correspondences and geometry'
    elif sensitivity<.6:status='HOLD_SCALE_AMBIGUOUS';reason='Horizontal scale remains weakly identifiable under alternate camera poses'
    else:status='CONDITIONAL_CROSS_DOMAIN_GEOMETRY';reason='Reprojection internally consistent under supplied correspondence, sketch and camera assumptions; not surveyed'
    pose_packets=[]
    for i,cam in enumerate(packet['views']):
        pose=fit.x[1+i*6:1+(i+1)*6];R=cv2.Rodrigues(pose[:3])[0];C=-R.T@pose[3:]
        pose_packets.append({'source':cam['source'],'rvec_world_to_camera':[round(float(x),5) for x in pose[:3]],
                             'camera_center_m':[round(float(x),3) for x in C]})
    if len(pose_packets)>=2:
        center_a=np.asarray(pose_packets[0]['camera_center_m'])
        center_b=np.asarray(pose_packets[1]['camera_center_m'])
        info['camera_baseline_m_conditional']=round(float(np.linalg.norm(center_b-center_a)),3)
    w=world_points(ground+raw_offsets,local_s,packet['height_reference_m'])
    modeled=[{'id':name,'base_m':[round(float(t),3) for t in w[j,1]],'top_m':[round(float(t),3) for t in w[j,0]]} for j,name in enumerate(ids)]
    # Suppress apparently exact geometry when hold
    return Candidate(status,reason,round(float(local_s),4) if status.startswith('CONDITIONAL') else None,
                     round(rms,3),pose_packets if status.startswith('CONDITIONAL') else [],
                     modeled if status.startswith('CONDITIONAL') else [],info)


def save_receipt(packet,candidate):
    q={'project':'MOTIF FIELD019','input_hash':hashlib.sha256(json.dumps(packet,sort_keys=True).encode()).hexdigest(),
       'output':candidate.to_dict()}
    q['receipt_hash']=hashlib.sha256(json.dumps(q,sort_keys=True).encode()).hexdigest()
    return q
