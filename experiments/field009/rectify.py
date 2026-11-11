"""FIELD-009: conditional planar-photo geometry, NEVER general 3-D measurement.

One known side and a separately established rectangle aspect ratio permit a
metric homography for points on the rectangle's plane. One edge alone is NOT
enough to infer dimensions from an unrectified perspective photograph.
"""
from __future__ import annotations
from dataclasses import dataclass
from math import isfinite
import numpy as np
import cv2
from geometry import Point,Trace

@dataclass(frozen=True)
class RectangleCalibration:
    source_id: str
    plane_id: str
    corners: tuple[Point,Point,Point,Point]
    width_lower: float
    width_upper: float
    width_units: str
    aspect_ratio: float
    corner_provenance: str
    width_provenance: str
    aspect_provenance: str
    human_or_instrument_reviewed: bool = False

    def __post_init__(self):
        if not all((self.source_id,self.plane_id,self.width_units,self.corner_provenance,
                    self.width_provenance,self.aspect_provenance)):
            raise ValueError('Missing source/evidence for photo rectification')
        if len(self.corners)!=4 or not all(isinstance(c,Point) for c in self.corners):
            raise ValueError('Need four ordered plane corners')
        if not all(isfinite(x) for x in (self.width_lower,self.width_upper,self.aspect_ratio)):
            raise ValueError('Invalid rectangle dimensions')
        if not (self.width_lower>0 and self.width_upper>=self.width_lower and self.aspect_ratio>0):
            raise ValueError('Invalid rectangle dimensions')


def homography(cal:RectangleCalibration):
    if not cal.human_or_instrument_reviewed:
        raise ValueError('Unreviewed model-proposed corners/aspect must not calibrate geometry')
    pts=np.float32([(p.x,p.y) for p in cal.corners])
    area=cv2.contourArea(pts.reshape(-1,1,2))
    if abs(area)<50 or not cv2.isContourConvex(pts.reshape(-1,1,2)):
        raise ValueError('Degenerate or concave rectangle projection')
    w=1.0;h=1/cal.aspect_ratio
    dst=np.float32([[0,0],[w,0],[w,h],[0,h]])
    H=cv2.getPerspectiveTransform(pts,dst)
    if not np.isfinite(H).all() or abs(float(np.linalg.det(H)))<1e-14:
        raise ValueError('Unstable rectification')
    return H


def transform(cal:RectangleCalibration,trace:Trace):
    if trace.source_id!=cal.source_id or trace.plane_id!=cal.plane_id:
        raise ValueError('Cannot rectify off-plane or cross-image trace')
    H=homography(cal)
    pts=np.float32([[(p.x,p.y)] for p in trace.vertices])
    out=cv2.perspectiveTransform(pts,H).reshape(-1,2)
    if not np.isfinite(out).all():
        raise ValueError('Transform invalid')
    vertices=tuple(Point(float(x),float(y)) for x,y in out)
    return Trace(trace.id,cal.source_id,cal.plane_id,vertices,
                 'homography:'+cal.corner_provenance,endpoint_tolerance_px=0.)


def estimate_photo_trace(cal:RectangleCalibration,trace:Trace):
    new=transform(cal,trace)
    lo=new.nominal_length*cal.width_lower
    hi=new.nominal_length*cal.width_upper
    return {'id':trace.id,'status':'CONDITIONAL_PLANAR_RECTIFICATION',
            'length_lower':lo,'length_upper':hi,'units':cal.width_units,
            'basis':(cal.corner_provenance,cal.width_provenance,cal.aspect_provenance,trace.provenance),
            'flags':('ONLY verified flat rectangle plane','4 source-image corners independently reviewed',
                     '1 known side PLUS separately known aspect ratio',
                     'Not a general 3-D or varied-depth measurement',
                     'Corner localization, lens distortion and curvature not quantitatively bounded')}
