"""FIELD-009: source-scoped, uncertainty-carrying visual ratios and one-anchor estimates.

Geometric inference is not physical verification. A single known length only sets a
scale for measurements in a compatible, approximately metric 2-D representation.
Unrectified perspective photos, cross-image features and arbitrary scribbles HOLD.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from math import hypot, isfinite, ceil
from typing import Optional

MODES = frozenset({'PLAN_METRIC', 'SKETCH_APPROX', 'RECTIFIED_PLANE', 'PHOTO_UNRECTIFIED'})


@dataclass(frozen=True)
class Point:
    x: float
    y: float

    def __post_init__(self):
        if not (isfinite(self.x) and isfinite(self.y)):
            raise ValueError('Nonfinite point')


@dataclass(frozen=True)
class Scene:
    source_id: str
    mode: str
    plane_id: str
    provenance: str
    proportion_tolerance: Optional[float] = None
    rectification_verified: bool = False

    def __post_init__(self):
        if not self.source_id or not self.plane_id or not self.provenance or self.mode not in MODES:
            raise ValueError('Invalid scene or source')
        if self.proportion_tolerance is not None and not (0 <= self.proportion_tolerance <= .85):
            raise ValueError('Proportion tolerance must be 0..0.85')
        if self.mode == 'RECTIFIED_PLANE' and not self.rectification_verified:
            raise ValueError('Rectification must have explicit verification')


@dataclass(frozen=True)
class Trace:
    id: str
    source_id: str
    plane_id: str
    vertices: tuple[Point,...]
    provenance: str
    endpoint_tolerance_px: float = 2.

    def __post_init__(self):
        if not self.id or not self.source_id or not self.plane_id or not self.provenance:
            raise ValueError('Missing trace identity or provenance')
        if len(self.vertices) < 2 or not all(isinstance(v,Point) for v in self.vertices):
            raise ValueError('Trace requires two or more points')
        if not (isfinite(self.endpoint_tolerance_px) and 0 <= self.endpoint_tolerance_px <= 100):
            raise ValueError('Bad pixel tolerance')
        if self.nominal_length < 1e-9:
            raise ValueError('Degenerate trace')

    @property
    def nominal_length(self):
        return sum(hypot(b.x-a.x,b.y-a.y) for a,b in zip(self.vertices,self.vertices[1:]))

    def pixel_range(self):
        spread = 2 * self.endpoint_tolerance_px * (len(self.vertices)-1)
        return (max(0.,self.nominal_length-spread), self.nominal_length+spread)


@dataclass(frozen=True)
class Anchor:
    trace_id: str
    lower: float
    upper: float
    units: str
    provenance: str
    verified: bool = True

    def __post_init__(self):
        if not self.trace_id or not self.provenance or not self.units:
            raise ValueError('Anchor lacks evidence')
        if not (isfinite(self.lower) and isfinite(self.upper) and 0 < self.lower <= self.upper):
            raise ValueError('Anchor length interval invalid')


@dataclass(frozen=True)
class Estimate:
    subject: str
    quantity: str
    status: str
    center: Optional[float]
    lower: Optional[float]
    upper: Optional[float]
    units: str
    basis: tuple[str,...]
    assumptions: tuple[str,...]

    def packet(self):
        return asdict(self)


def _hold(subject,qty,why,basis=()):
    return Estimate(subject,qty,'HOLD',None,None,None,'',tuple(basis),(why,))


def _match(scene: Scene, *traces: Trace):
    return all(t.source_id==scene.source_id and t.plane_id==scene.plane_id for t in traces)


def _metric_admissible(scene: Scene):
    return scene.mode in ('PLAN_METRIC','RECTIFIED_PLANE') or (scene.mode=='SKETCH_APPROX' and scene.proportion_tolerance is not None)


def ratio(scene: Scene, target: Trace, reference: Trace) -> Estimate:
    if not _match(scene,target,reference):
        return _hold(target.id,'length_ratio','Cross-source or cross-plane geometry cannot be compared',(target.id,reference.id))
    if scene.mode=='PHOTO_UNRECTIFIED':
        return _hold(target.id,'length_ratio','Perspective photo lengths may have different depth-dependent scales',(target.id,reference.id))
    if not _metric_admissible(scene):
        r=target.nominal_length/reference.nominal_length
        return Estimate(target.id,'drawn_ratio','DRAWN_ONLY',r,None,None,'drawing units / drawing units',
                        (target.id,reference.id,scene.source_id),
                        ('Sketch is not declared proportional: no physical ratio inferred',))
    r=target.nominal_length/reference.nominal_length
    tl,th=target.pixel_range();rl,rh=reference.pixel_range()
    if rl < 1e-6:
        return _hold(target.id,'length_ratio','Reference too small relative to endpoint error',(target.id,reference.id))
    e=scene.proportion_tolerance or 0.
    lo=(tl/rh)*(1-e)
    hi=(th/rl)*(1+e)
    status='CONDITIONAL_ROUGH_RATIO' if scene.mode=='SKETCH_APPROX' else 'PLAN_RATIO'
    return Estimate(target.id,'length_ratio',status,r,lo,hi,'ratio',
                    (target.id,reference.id,scene.source_id),
                    ('Same source and same represented plane',
                     'Proportional drawing distortion bounded by an assumed tolerance' if e else 'Planar metric coordinates assumed',
                     'Interval is an assumption envelope, not measured confidence'))


def calibrate(scene: Scene, subject: Trace, anchors: tuple[tuple[Trace,Anchor],...]) -> Estimate:
    if not _match(scene,subject):
        return _hold(subject.id,'length','Subject coordinate frame does not match scene',(subject.id,))
    if scene.mode=='PHOTO_UNRECTIFIED':
        return _hold(subject.id,'length','One reference length does not correct perspective or depth',(subject.id,))
    if scene.mode=='SKETCH_APPROX' and scene.proportion_tolerance is None:
        return _hold(subject.id,'length','Sketch may not be proportional: explicitly authorize rough distortion assumptions',(subject.id,))
    if not anchors:
        return _hold(subject.id,'length','No known physical reference: report ratios only',(subject.id,))
    low_scales=[];high_scales=[];units=None;trace_ids=[]
    for measured,anchor in anchors:
        if anchor.trace_id!=measured.id or not _match(scene,measured):
            return _hold(subject.id,'length','Anchor refers to incompatible trace/source/plane',(subject.id,measured.id))
        if not anchor.verified:
            return _hold(subject.id,'length','Reference length is only a guess, not an independent anchor',(subject.id,measured.id))
        if units is not None and anchor.units!=units:
            return _hold(subject.id,'length','Unit mismatch between anchors',(subject.id,measured.id))
        units=anchor.units
        lo_px,hi_px=measured.pixel_range()
        if lo_px <= 1e-6:
            return _hold(subject.id,'length','Anchor shorter than endpoint uncertainty',(subject.id,measured.id))
        low_scales.append(anchor.lower/hi_px)
        high_scales.append(anchor.upper/lo_px)
        trace_ids.append(measured.id)
    low=max(low_scales);high=min(high_scales)
    if low>high:
        return _hold(subject.id,'length','Conflicting known-reference scales; investigate before planning',tuple(trace_ids))
    pixel_lo,pixel_hi=subject.pixel_range()
    e=scene.proportion_tolerance if scene.mode=='SKETCH_APPROX' else 0.
    lo=max(0.,pixel_lo*low*(1-e))
    hi=pixel_hi*high*(1+e)
    center=subject.nominal_length*(low+high)/2
    status='CONDITIONAL_SKETCH_GUESS' if scene.mode=='SKETCH_APPROX' else 'REFERENCE_SCALED_ESTIMATE'
    return Estimate(subject.id,'length',status,center,lo,hi,units,
                    (scene.source_id,subject.id,*trace_ids),
                    ('Known reference applies to the same 2-D plane and source',
                     'Assumed sketch nonuniformity ±'+str(round(100*e))+'%' if e else 'Metric 2-D drawing or verified planar rectification',
                     'No perspective correction, 3-D load rating or real-world fit certified'))


def panel_requirements(length: Estimate, panel_width: float, min_overlap: float=0.0) -> dict:
    if not (isfinite(panel_width) and isfinite(min_overlap) and panel_width>0 and 0<=min_overlap<panel_width):
        raise ValueError('Invalid panel coverage')
    effective=panel_width-min_overlap
    if length.lower is None or length.upper is None or length.status=='HOLD':
        return {'status':'HOLD_UNSCALED','panels_possible':None,'panels_if_upper_bound':None,
                'reason':'Needs verified reference and usable proportional representation'}
    return {'status':'CONDITIONAL_MATERIAL_SCENARIO','panels_possible':ceil(length.lower/effective),
            'panels_if_upper_bound':ceil(length.upper/effective),
            'effective_span_per_panel':effective,'units':length.units,
            'note':'Geometry-only material count; no anchors, ties, gates, gaps, safety or installed fit certified'}
