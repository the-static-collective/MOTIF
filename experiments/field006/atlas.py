"""FIELD-006: source-registered visual scratchpad.

A sketch and photographs are *different coordinate systems*. A single photo's
pixel box never becomes a surveyed position in a plan. This module keeps
what the user marked, where it came from, and the uncertain relationships
between views before imagining alternative arrangements.

Stdlib only. Image embedding into SVG is local, opt-in, and never a network call.
"""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
from html import escape
from pathlib import Path
import base64, json, math, mimetypes
from typing import Optional

EVIDENCE_KINDS = {'USER_SKETCH', 'USER_PHOTO', 'USER_STATEMENT', 'MODEL_CANDIDATE', 'SYNTHETIC'}
CLAIM_STATUS = {'OBSERVED', 'USER_STATED', 'TENTATIVE', 'UNKNOWN', 'CONTRADICTED'}
TRACE_TYPES = {'CURRENT', 'DESIRED', 'ACCESS', 'UNKNOWN'}


def num01(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x) and 0 <= x <= 1


@dataclass(frozen=True)
class Source:
    id: str
    kind: str
    description: str
    local_path: str = ''
    private: bool = True


@dataclass(frozen=True)
class Landmark:
    id: str
    label: str
    sketch_xy: tuple[float, float] | None
    evidence: tuple[str, ...]
    status: str = 'OBSERVED'
    note: str = ''


@dataclass(frozen=True)
class PhotoClaim:
    id: str
    source: str
    text: str
    linked_landmarks: tuple[str, ...] = ()
    status: str = 'OBSERVED'
    # Links express topical association, not mapping of photo pixel location to sketch coordinates.


@dataclass(frozen=True)
class Trace:
    id: str
    source: str
    kind: str
    points: tuple[tuple[float, float], ...]
    status: str
    note: str


@dataclass(frozen=True)
class EvidenceAtlas:
    title: str
    sketch_source: str
    sources: tuple[Source, ...]
    landmarks: tuple[Landmark, ...]
    claims: tuple[PhotoClaim, ...]
    traces: tuple[Trace, ...] = ()
    user_rules: tuple[tuple[str, str], ...] = ()
    unresolved: tuple[str, ...] = ()

    def validate(self):
        if not self.title or not self.sources or len(self.sources) > 100:
            raise ValueError('missing title or invalid source count')
        sources = {s.id: s for s in self.sources}
        if len(sources) != len(self.sources) or not all(s.id and s.description and s.kind in EVIDENCE_KINDS for s in self.sources):
            raise ValueError('duplicate, empty or untyped evidence source')
        if self.sketch_source not in sources or sources[self.sketch_source].kind not in {'USER_SKETCH', 'SYNTHETIC'}:
            raise ValueError('sketch source must exist and be a sketch')
        landmarks = {l.id:l for l in self.landmarks}
        if len(landmarks) != len(self.landmarks): raise ValueError('duplicate landmark')
        for l in self.landmarks:
            if not l.id or not l.label or l.status not in CLAIM_STATUS or not l.evidence:
                raise ValueError('invalid landmark')
            if any(e not in sources for e in l.evidence): raise ValueError('landmark cites absent source')
            if l.sketch_xy is not None and (len(l.sketch_xy)!=2 or not all(map(num01,l.sketch_xy))):
                raise ValueError('invalid sketch location')
            if l.sketch_xy and self.sketch_source not in l.evidence:
                raise ValueError('sketch coordinates require sketch provenance')
        seen = set()
        for c in self.claims:
            if not c.id or c.id in seen or c.source not in sources or c.status not in CLAIM_STATUS or not c.text:
                raise ValueError('invalid photo claim')
            seen.add(c.id)
            if any(x not in landmarks for x in c.linked_landmarks): raise ValueError('claim link to absent landmark')
        for tr in self.traces:
            if tr.source != self.sketch_source or tr.kind not in TRACE_TYPES or tr.status not in CLAIM_STATUS:
                raise ValueError('traces must be source-sketch-grounded')
            if len(tr.points) < 2 or len(tr.points)>100 or not all(len(p)==2 and all(map(num01,p)) for p in tr.points):
                raise ValueError('invalid trace geometry')
            if tr.kind == 'DESIRED' and tr.status == 'OBSERVED':
                # A marked desired boundary is an expressed intent, not an existing-world observation.
                raise ValueError('desired trace must not imply physical construction')
        if any(not k or not v for k,v in self.user_rules): raise ValueError('bad user rule')
        return self


def from_dict(payload: dict) -> EvidenceAtlas:
    if set(payload) - set(EvidenceAtlas.__dataclass_fields__): raise ValueError('unknown atlas keys')
    def rows(name, cls):
        allowed = set(cls.__dataclass_fields__)
        values=[]
        for entry in payload.get(name, []):
            if set(entry)-allowed:raise ValueError('unknown '+name+' keys')
            d=dict(entry)
            for k in ('evidence','linked_landmarks'):
                if k in d: d[k]=tuple(d[k])
            if 'sketch_xy' in d and d['sketch_xy'] is not None:d['sketch_xy']=tuple(d['sketch_xy'])
            if 'points' in d:d['points']=tuple(tuple(p) for p in d['points'])
            values.append(cls(**d))
        return tuple(values)
    atlas=EvidenceAtlas(
      title=payload['title'],sketch_source=payload['sketch_source'],
      sources=rows('sources',Source),landmarks=rows('landmarks',Landmark),
      claims=rows('claims',PhotoClaim),traces=rows('traces',Trace),
      user_rules=tuple(tuple(x) for x in payload.get('user_rules',[])),
      unresolved=tuple(payload.get('unresolved',[])))
    return atlas.validate()


def receipt(atlas:EvidenceAtlas) -> dict:
    atlas.validate()
    state={'version':'FIELD-006-source-registered','sources':len(atlas.sources),
           'source_sketch_preserved':True,
           'landmarks':len(atlas.landmarks),'linked_photo_claims':sum(bool(c.linked_landmarks) for c in atlas.claims),
           'photos':sum(s.kind=='USER_PHOTO' for s in atlas.sources),
           'user_declared_rules':len(atlas.user_rules),
           'boundary_traces':{'current':sum(t.kind=='CURRENT' for t in atlas.traces),
                              'desired':sum(t.kind=='DESIRED' for t in atlas.traces)},
           'unresolved':list(atlas.unresolved),
           'claims_proven_safe':0,'automatic_image_recognition_performed':False,
           'photos_assumed_georegistered':False,'actual_dimensions_inferred':False}
    state['sha256']=sha256(json.dumps(state,sort_keys=True).encode()).hexdigest()
    return state


def audit_preservation(atlas:EvidenceAtlas,required_labels:tuple[str,...]):
    """Evaluate whether named sketch facts survived conversion; not vision accuracy."""
    atlas.validate()
    found={l.label.casefold().strip() for l in atlas.landmarks}
    missed=[name for name in required_labels if name.casefold().strip() not in found]
    return {'retained':len(required_labels)-len(missed),'required':len(required_labels),'missing':missed,
            'test_type':'ANNOTATOR_AUTHORED_CONTENT_RETENTION_NOT_AUTONOMOUS_PERCEPTION'}


def _img_uri(p:Path) -> str:
    if not p.is_file() or p.stat().st_size>15_000_000:raise ValueError('missing/oversized local image')
    mime={'.png':'image/png','.jpg':'image/jpeg','.jpeg':'image/jpeg','.webp':'image/webp'}.get(p.suffix.lower())
    if not mime:raise ValueError('unsupported image')
    return 'data:'+mime+';base64,'+base64.b64encode(p.read_bytes()).decode()


def svg_atlas(atlas:EvidenceAtlas, *, allow_private_images=False, path_root:Optional[Path]=None):
    """Preserve the original paper, then index photo evidence WITHOUT false common coordinates.

    Default output does not embed private files. Only explicit allow_private_images=True
    and local paths can include source imagery in an output SVG.
    """
    atlas.validate()
    src={s.id:s for s in atlas.sources}
    W,H=1800,1500
    out=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}">',
         '<rect width="1800" height="1500" fill="#f8f6f1"/>',
         '<text x="52" y="63" font-family="sans-serif" font-weight="bold" font-size="34" fill="#222f38">FIELD-006  /  SOURCE-REGISTERED ATLAS</text>',
         '<text x="54" y="98" font-family="sans-serif" font-size="17" fill="#596771">Original sketch retained · photo observations indexed · no invented scale or camera pose</text>',
         '<rect x="48" y="122" width="1088" height="565" rx="10" fill="white" stroke="#c5cac8"/>',
         '<text x="70" y="154" font-family="sans-serif" font-weight="bold" font-size="18" fill="#283943">01  USER SKETCH / AUTHORITATIVE MARKS</text>',
         '<rect x="66" y="172" width="1052" height="470" rx="7" fill="#e9ece9"/>']
    sk=src[atlas.sketch_source]
    if allow_private_images and sk.local_path:
        p=(path_root/ sk.local_path) if path_root else Path(sk.local_path)
        uri=_img_uri(p)
        out.append(f'<image x="66" y="172" width="1052" height="470" preserveAspectRatio="xMidYMid meet" href="{uri}"/>')
    else:
        out.append('<text x="345" y="398" font-size="18" font-family="sans-serif" fill="#666">Source sketch image intentionally not embedded</text>')
    # The user paper is used as the spatial record. Numbered badges only index content,
    # never make a new claim about metric geometry.
    for i,l in enumerate(atlas.landmarks):
        if l.sketch_xy is None:continue
        x=66+l.sketch_xy[0]*1052;y=172+l.sketch_xy[1]*470
        out.extend([f'<circle cx="{x:.1f}" cy="{y:.1f}" r="16" fill="#f7f1dd" stroke="#172c38" stroke-width="2"/>',
                    f'<text x="{x:.1f}" y="{y+5:.1f}" text-anchor="middle" font-size="13" font-weight="bold" font-family="sans-serif" fill="#172c38">{i+1}</text>'])
    # Never approximate a dotted line from an uninterpreted image. Only render explicit source-derived traces.
    for t in atlas.traces:
        pts=' '.join(f'{66+x*1052:.1f},{172+y*470:.1f}' for x,y in t.points)
        dash='stroke-dasharray="12 8"' if t.kind=='DESIRED' else ''
        color='#117d89' if t.kind=='DESIRED' else '#6d7069'
        out.append(f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="3" {dash}/>')
    out.append('<text x="70" y="672" font-family="sans-serif" font-size="14" fill="#586a73">Badges index labels; blue dashed means desired (not built), where manually traced. Not to scale.</text>')
    out.extend(['<rect x="48" y="707" width="1088" height="320" rx="10" fill="white" stroke="#c5cac8"/>',
                '<text x="70" y="741" font-size="20" font-family="sans-serif" font-weight="bold" fill="#283943">02  LANDMARKS &amp; RELATIONS PRESERVED</text>'])
    for i,l in enumerate(atlas.landmarks[:12]):
        col=i%3;row=i//3;x=70+col*348;y=785+row*59
        out.append(f'<text x="{x}" y="{y}" font-size="15" font-family="sans-serif" fill="#243743"><tspan font-weight="bold">{i+1:02d}</tspan>  {escape(l.label[:34])}</text>')
        out.append(f'<text x="{x+38}" y="{y+18}" font-size="11" font-family="sans-serif" fill="#63717b">{escape(l.status)} · {escape(l.evidence[0])}</text>')
    out.extend(['<rect x="48" y="1047" width="1088" height="395" rx="10" fill="white" stroke="#c5cac8"/>',
                '<text x="70" y="1082" font-size="20" font-family="sans-serif" font-weight="bold" fill="#283943">03  REASONING INPUT / SEPARATE FACT FROM HYPOTHESIS</text>'])
    y=1110
    for i,(k,v) in enumerate(atlas.user_rules[:6]):
        y+=42
        out.append(f'<text x="72" y="{y}" font-size="15" font-family="sans-serif" fill="#283943"><tspan font-weight="bold">{escape(k[:28])}:</tspan> {escape(v[:112])}</text>')
    if atlas.unresolved:
        out.append('<text x="72" y="1416" font-size="15" font-family="sans-serif" fill="#aa6330">UNKNOWN: '+escape(' · '.join(atlas.unresolved[:3])[:126])+'</text>')
    # Photos are displayed as per-source cards, NOT overlaid at invented yard positions.
    out.extend(['<text x="1172" y="155" font-size="20" font-weight="bold" font-family="sans-serif" fill="#283943">04  PHOTO WITNESSES</text>',
                '<text x="1172" y="178" font-size="13" font-family="sans-serif" fill="#5f6d75">Photo pixels ≠ yard map coordinates</text>'])
    photos=[s for s in atlas.sources if s.kind=='USER_PHOTO']
    for j,s in enumerate(photos[:10]):
        x=1170+(j%2)*316;y=194+(j//2)*239
        out.append(f'<rect x="{x}" y="{y}" width="296" height="224" rx="8" fill="#fff" stroke="#c8cfce"/>')
        if allow_private_images and s.local_path:
            p=(path_root/s.local_path) if path_root else Path(s.local_path)
            uri=_img_uri(p)
            out.append(f'<image x="{x+7}" y="{y+7}" width="282" height="153" preserveAspectRatio="xMidYMid meet" href="{uri}"/>')
        else:
            out.append(f'<rect x="{x+7}" y="{y+7}" width="282" height="153" fill="#e7ecea"/>')
        out.append(f'<text x="{x+12}" y="{y+181}" font-size="13" font-family="sans-serif" font-weight="bold" fill="#293d47">{escape(s.id)}</text>')
        # Description is prose about photographed objects, not claims of placement.
        words=s.description.split();chunks=[];line=[]
        for word in words:
            if len(' '.join(line+[word]))>38:chunks.append(' '.join(line));line=[word]
            else:line.append(word)
        if line:chunks.append(' '.join(line))
        for k,chunk in enumerate(chunks[:2]):
            out.append(f'<text x="{x+12}" y="{y+199+k*16}" font-size="12" font-family="sans-serif" fill="#55666d">{escape(chunk)}</text>')
    out.extend(['<line x1="48" x2="1752" y1="1461" y2="1461" stroke="#d1d6d3"/>',
                '<text x="55" y="1484" font-size="13" font-family="sans-serif" fill="#4d5f66">Source-linked draft. Authored annotation is not autonomous image understanding or structural certification.</text>',
                '</svg>'])
    return '\n'.join(out)