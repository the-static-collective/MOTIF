"""FIELD-015 dual local 3D reconstruction: source-owned, unregistered proposals.

Checkpoint inference is intentionally opt-in. No model weights, photos or
independently verified world coordinates are shipped in this research draft.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np

def digest(path):
    p=Path(path)
    if not p.is_file() or p.stat().st_size>30_000_000: raise ValueError("Missing/oversized local image")
    return hashlib.sha256(p.read_bytes()).hexdigest()

def as_numpy(value):
    return value.detach().cpu().numpy() if hasattr(value,"detach") else np.asarray(value)

def mapanything_points(predictions):
    if isinstance(predictions,dict): predictions=[predictions]
    if not predictions: raise ValueError("Empty MapAnything inference")
    result=[]
    for view in predictions:
        if "pts3d" not in view: raise ValueError("World-frame pts3d absent; cannot substitute camera coordinates")
        pts=as_numpy(view["pts3d"])
        if pts.shape[-1]!=3: raise ValueError("Bad points")
        result.append(pts.reshape(-1,3))
    return np.concatenate(result)

def da3_points(prediction):
    depth=as_numpy(prediction.depth)
    if prediction.extrinsics is None or prediction.intrinsics is None: raise ValueError("No valid camera predictions")
    ext=as_numpy(prediction.extrinsics);K=as_numpy(prediction.intrinsics)
    if depth.ndim!=3 or K.shape!=(len(depth),3,3) or ext.shape not in ((len(depth),4,4),(len(depth),3,4)):
        raise ValueError("Malformed DA3 projection arrays")
    out=[]
    for i,D in enumerate(depth):
        H,W=D.shape; step=max(1,int(max(H,W)/48))
        yy,xx=np.mgrid[0:H:step,0:W:step];z=D[::step,::step]
        valid=np.isfinite(z)&(z>0)&(z<1e6)
        fx,fy=K[i,0,0],K[i,1,1]
        if not np.isfinite(fx*fy) or abs(fx*fy)<1e-10: raise ValueError("Invalid intrinsics")
        cam=np.column_stack(((xx[valid]-K[i,0,2])*z[valid]/fx,
                             (yy[valid]-K[i,1,2])*z[valid]/fy,z[valid],np.ones(valid.sum())))
        pose=np.eye(4);pose[:ext.shape[1],:]=ext[i]
        out.append((np.linalg.inv(pose)@cam.T).T[:,:3])
    return np.concatenate(out)

def witness(engine,checkpoint,sources,xyz,real_call=False):
    if engine not in ("MAPANYTHING","DEPTH_ANYTHING_3"):raise ValueError("Unknown engine")
    xyz=as_numpy(xyz).reshape(-1,3)
    xyz=xyz[np.isfinite(xyz).all(axis=1)]
    if len(xyz)<3:raise ValueError("No finite 3D points")
    idx=np.linspace(0,len(xyz)-1,min(450,len(xyz)),dtype=int)
    return dict(engine=engine,checkpoint=checkpoint,image_sha256=[digest(p) for p in sources],
        xyz=[[round(float(a),6) for a in q] for q in xyz[idx]],
        scale="MODEL_METRIC_UNVERIFIED" if engine=="MAPANYTHING" else "RELATIVE",
        coordinate_frame="MODEL_LOCAL_UNREGISTERED",registered_to_site=False,
        real_model_executed=real_call,structural_safety_verified=False)

def compare(a,b):
    if a["image_sha256"]!=b["image_sha256"]:return "HOLD_DIFFERENT_IMAGE_SOURCES"
    return "HOLD_NO_INDEPENDENT_POINT_CORRESPONDENCE_OR_METRIC_SITE_FRAME"

def run(engine,checkpoint,images,output,allow=False,device="cpu"):
    if not allow:raise PermissionError("Explicit --allow-local-inference required")
    cp=Path(checkpoint).expanduser()
    if not cp.exists() or not images or len(images)>40:raise ValueError("Local checkpoint and 1-40 images required")
    for p in images:digest(p)
    if engine=="mapanything":
        import torch
        from mapanything.models import MapAnything
        from mapanything.utils.image import load_images
        m=MapAnything.from_pretrained(str(cp)).to(device).eval()
        with torch.no_grad():
            points=mapanything_points(m.infer(load_images(images),memory_efficient_inference=True,
                            minibatch_size=1,use_amp=(device!="cpu"),apply_mask=True))
        label="MAPANYTHING"
    elif engine=="da3":
        from depth_anything_3.api import DepthAnything3
        m=DepthAnything3.from_pretrained(str(cp)).to(device)
        points=da3_points(m.inference(image=images,export_format="mini_npz"))
        label="DEPTH_ANYTHING_3"
    else:raise ValueError("Unknown engine")
    packet=witness(label,cp.name,images,points,real_call=True)
    Path(output).write_text(json.dumps(packet,indent=2))
    return packet

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--engine",choices=["mapanything","da3"],required=True)
    parser.add_argument("--checkpoint",required=True)
    parser.add_argument("--photos",nargs="+",required=True)
    parser.add_argument("--output",required=True)
    parser.add_argument("--device",choices=["cpu","cuda","mps"],default="cpu")
    parser.add_argument("--allow-local-inference",action="store_true")
    a=parser.parse_args()
    print(json.dumps(run(a.engine,a.checkpoint,a.photos,a.output,a.allow_local_inference,a.device),indent=2))
