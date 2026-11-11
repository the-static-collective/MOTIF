"""A fail-closed interface for tentative local-VLM sketch/photo annotations.

This module does not call a VLM. It reviews its *proposed* structured output.
In particular an image bbox is NEVER a property coordinate, even if a vision
model says otherwise, and its trace cannot overwrite a user's marked trace.
"""
from __future__ import annotations
from dataclasses import dataclass
from atlas import EvidenceAtlas, Trace, num01


@dataclass(frozen=True)
class Review:
    accepted_traces: tuple[Trace, ...]
    held: tuple[str, ...]
    candidate_labels: tuple[tuple[str,str], ...]
    note: str = 'MODEL_TENTATIVE_ONLY; HUMAN_SKETCH_MARKS_UNCHANGED'


def review_model_packet(atlas:EvidenceAtlas, packet:dict) -> Review:
    atlas.validate()
    if not isinstance(packet,dict) or set(packet)-{'candidate_landmarks','candidate_traces'}:
        raise ValueError('invalid model envelope')
    sources={s.id:s for s in atlas.sources}
    known={l.label.strip().casefold() for l in atlas.landmarks}
    traces=[];held=[];labels=[]
    for i,l in enumerate(packet.get('candidate_landmarks',[])):
        if not isinstance(l,dict) or set(l)-{'label','source','sketch_xy','status'}:
            raise ValueError('invalid model landmark')
        source=l.get('source');label=l.get('label')
        if source not in sources or not isinstance(label,str) or not label.strip() or len(label)>120:
            raise ValueError('unidentified or overlong proposed label')
        if l.get('status') != 'TENTATIVE':
            held.append('model_landmark_'+str(i)+':MUST_REMAIN_TENTATIVE');continue
        xy=l.get('sketch_xy')
        if xy is not None and (source!=atlas.sketch_source or not isinstance(xy,list) or len(xy)!=2 or not all(map(num01,xy))):
            held.append('model_landmark_'+str(i)+':NO_PHOTO_TO_WORLD_COORDINATES');continue
        if label.strip().casefold() in known:
            held.append('model_landmark_'+str(i)+':MATCHES_EXISTING_REVIEWED_LABEL');continue
        labels.append((source,label.strip()))
    for i,tr in enumerate(packet.get('candidate_traces',[])):
        if not isinstance(tr,dict) or set(tr)-{'source','kind','points','status','note'}:
            raise ValueError('invalid model trace')
        if tr.get('source')!=atlas.sketch_source:
            held.append('model_trace_'+str(i)+':UNREGISTERED_COORDINATE_SPACE');continue
        if tr.get('status')!='TENTATIVE':
            held.append('model_trace_'+str(i)+':MODEL_CANNOT_DECLARE_USER_INTENT');continue
        try:
            t=Trace(id='model_trace_'+str(i),source=tr['source'],kind=tr['kind'],
                    points=tuple(tuple(p) for p in tr['points']),status='TENTATIVE',
                    note=str(tr.get('note',''))[:200])
            # Run the same strong geometry/source validation as first-class atlas lines.
            a=EvidenceAtlas(atlas.title,atlas.sketch_source,atlas.sources,atlas.landmarks,
                            atlas.claims,atlas.traces+(t,),atlas.user_rules,atlas.unresolved)
            a.validate()
            traces.append(t)
        except (ValueError,KeyError,TypeError):
            held.append('model_trace_'+str(i)+':INVALID_OR_UNSUPPORTED_TRACE')
    return Review(tuple(traces),tuple(held),tuple(labels))


def next_evidence_actions(atlas:EvidenceAtlas) -> tuple[dict, ...]:
    """Prioritize informative inspection rather than generating fake dimensions."""
    atlas.validate()
    pending=[]
    rule_text=' '.join(k+' '+v for k,v in atlas.user_rules).lower()
    if any(w in rule_text for w in ('dotted','desired','new route')) and not any(t.kind=='DESIRED' for t in atlas.traces):
        pending.append({'id':'TRACE_INTENDED_BOUNDARY', 'priority':100,
                        'action':'Read the hand-drawn dotted marks as candidate path segments in paper coordinates',
                        'needs':'local image interpretation or explicit human trace','physical_work':False})
    if any(s.kind=='USER_PHOTO' for s in atlas.sources):
        pending.append({'id':'LINK_MULTI_VIEW_WITNESSES','priority':80,
                        'action':'Relate photo observations by identity or view correspondence without assigning yard coordinates',
                        'needs':'matching visual features plus source attribution','physical_work':False})
    if any('mov' in v.lower() or 'anchor' in v.lower() or 'support' in v.lower() for k,v in atlas.user_rules):
        pending.append({'id':'COLD_FIT_AND_ANCHOR_CHECK','priority':70,
                        'action':'Propose a reversible fit check for one candidate move or tie location',
                        'needs':'actual structure, stable attachment points, supervised no-dog trial','physical_work':False})
    if any('measure' in x.lower() for x in atlas.unresolved):
        pending.append({'id':'MEASURE_DECISION_CRITICAL_GAP','priority':60,
                        'action':'Only measure the gap that changes which material arrangement is possible',
                        'needs':'safe site access and ruler/tape','physical_work':False})
    pending.append({'id':'HAZARD_REVIEW','priority':55,
                    'action':'Inspect tipping, entanglement, sharp wire, entrances, and potential traffic exposure',
                    'needs':'actual conditions; no safety proof from photographs','physical_work':False})
    return tuple(sorted(pending,key=lambda x:(-x['priority'],x['id'])))