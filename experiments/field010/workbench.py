"""MOTIF FIELD-010: two read-only reasoning branches over one inspectable event ledger.

Pure Python, standard library. A digital edit is not an observation of physical
construction. A drawn length is not a physical measurement. Photo coordinates
are never silently projected into sketch coordinates.
"""
from __future__ import annotations
import copy
from hashlib import sha256
from json import dumps
from math import hypot, isfinite

KINDS = {"current", "desired", "panel", "support", "access"}
STATUSES = {"tentative", "user_confirmed", "user_rejected"}
EVENT_TYPES = {"add", "move", "endpoint", "set", "measure", "ratio", "proportional", "remove", "revert"}
POINT_LIMIT = 200


def _num(x):
    return type(x) in (int,float) and isfinite(x)


def _xy(p):
    return isinstance(p,list) and len(p)==2 and all(_num(x) and 0<=x<=1 for x in p)


def valid_item(i):
    if not isinstance(i,dict) or not isinstance(i.get('id'),str) or not i['id']:
        raise ValueError('Missing item identity')
    if i.get('kind') not in KINDS or i.get('status') not in STATUSES:
        raise ValueError('Invalid item type or epistemic status')
    if not isinstance(i.get('label',''),str) or len(i['label'])>120:
        raise ValueError('Invalid label')
    if type(i.get('movable')) is not bool: raise ValueError('Mobility must be explicit Boolean')
    pts=i.get('points')
    if not isinstance(pts,list) or len(pts) not in (1,2) or not all(_xy(p) for p in pts):
        raise ValueError('Requires one point for support or two for other items')
    if (i['kind']=='support') != (len(pts)==1):
        raise ValueError('Support requires one point; linear item requires two')
    return i


def validate(project):
    if project.get('schema')!='motif.field010.v1':raise ValueError('Unknown schema')
    base=project.get('base',{})
    if base.get('coordinate_frame')!='sketch_normalized' or base.get('source') not in ('synthetic','user_sketch'):
        raise ValueError('Wrong coordinate frame')
    size=base.get('sketch_size')
    if not isinstance(size,list) or len(size)!=2 or any(not _num(x) or x<=0 for x in size):
        raise ValueError('Bad sketch dimensions')
    if len(base.get('items',[]))>POINT_LIMIT:raise ValueError('Too many items')
    ids=set()
    for it in base['items']:
        valid_item(it)
        if it['id'] in ids:raise ValueError('Duplicate base ID')
        ids.add(it['id'])
    ev=project.get('events',[])
    if not isinstance(ev,list) or len(ev)>5000:raise ValueError('Invalid event ledger')
    event_ids=set()
    for e in ev:
        if e.get('type') not in EVENT_TYPES or not isinstance(e.get('id'),str) or e['id'] in event_ids:
            raise ValueError('Invalid/duplicate event')
        event_ids.add(e['id'])
    return project


def replay(project):
    """Rebuild from original inputs, excluding edits referenced by later reverts.

    Revert events stay visible in the ledger. They do not erase source material.
    """
    validate(project)
    base=project['base']
    items={i['id']:copy.deepcopy(i) for i in base['items']}
    measure={}
    relations=[]
    proportional=False
    tolerance=None
    blocked={e.get('target_event') for e in project['events'] if e['type']=='revert'}
    for e in project['events']:
        t=e['type']
        if t=='revert' or e['id'] in blocked: continue
        target=e.get('target')
        if t=='add':
            o=valid_item(copy.deepcopy(e['item']))
            if o['id'] in items:raise ValueError('Duplicate added item')
            items[o['id']]=o
        elif t=='remove':
            if target in items:items.pop(target)
        elif t=='move':
            if target not in items:raise ValueError('Missing moved item')
            dx,dy=e.get('delta',[])
            if not (_num(dx) and _num(dy)):raise ValueError('Bad delta')
            pts=items[target]['points']
            points=[[round(x+dx,6),round(y+dy,6)] for x,y in pts]
            if any(not _xy(p) for p in points):
                raise ValueError('Rigid move would leave the source image bounds')
            items[target]['points']=points
        elif t=='endpoint':
            if target not in items:raise ValueError('Missing line')
            idx=e.get('index');xy=e.get('point')
            if idx not in (0,1) or not _xy(xy) or idx>=len(items[target]['points']):raise ValueError('Bad endpoint')
            items[target]['points'][idx]=copy.deepcopy(xy)
        elif t=='set':
            if target not in items:raise ValueError('Missing edited item')
            prop=e.get('prop');v=e.get('value')
            if prop not in {'label','movable','kind','status'}:raise ValueError('Invalid property')
            if prop=='kind' and ((v=='support') != (len(items[target]['points'])==1)):
                raise ValueError('Geometry incompatible with kind')
            items[target][prop]=v
            valid_item(items[target])
        elif t=='measure':
            if target not in items or len(items[target]['points'])!=2:raise ValueError('Missing span')
            value=e.get('value');unit=e.get('unit');quality=e.get('quality')
            if not (_num(value) and 0<value<1e7 and unit in ('ft','m') and quality in ('user_measured','rough_guess')):
                raise ValueError('Invalid measurement')
            measure[target]={'value':value,'unit':unit,'quality':quality,'event_id':e['id']}
        elif t=='ratio':
            if target not in items or e.get('other') not in items:
                raise ValueError('Ratio refers to missing object')
            val=e.get('value')
            if not (_num(val) and 0.05<=val<=20):raise ValueError('Bad ratio')
            relations.append({'target':target,'other':e['other'],'ratio':val,'event_id':e['id'],'status':'user_relation_not_measured'})
        elif t=='proportional':
            proportional=e.get('value') is True
            tol=e.get('tolerance',0.4)
            if not (_num(tol) and 0<=tol<=0.85):raise ValueError('Bad tolerance')
            tolerance=tol if proportional else None
    # Optional measurement/relations for deleted items must not be used.
    measure={k:v for k,v in measure.items() if k in items}
    relations=[r for r in relations if r['target'] in items and r['other'] in items]
    return {'items':list(items.values()),'measurements':measure,'relations':relations,
            'proportional':proportional,'tolerance':tolerance,
            'source':base['source'],'sketch_size':base['sketch_size'],
            'version':len(project['events'])}


def span(item, sketch_size):
    if len(item['points'])!=2:return None
    (a,b)=item['points'];w,h=sketch_size
    return hypot((a[0]-b[0])*w,(a[1]-b[1])*h)


def solver(state):
    """Autonomous branch: conservative route ideas, ratios, uncertain material reuse."""
    items=state['items'];size=state['sketch_size'];ms=state['measurements']
    lines=[i for i in items if len(i['points'])==2 and i['status']!='user_rejected']
    desired=[i for i in lines if i['kind']=='desired']
    current=[i for i in lines if i['kind']=='current']
    movable=[i for i in current if i['movable']]
    panels=[i for i in lines if i['kind']=='panel']
    supports=[i for i in items if i['kind']=='support']
    anchors=[(i,ms[i['id']]) for i in lines if i['id'] in ms and ms[i['id']]['quality']=='user_measured']
    estimates=[];factors=[]
    if state['proportional'] and anchors:
        # One unit at a time, avoid conflicting references being treated as a consensus.
        unit=anchors[0][1]['unit']
        scales=[m['value']/span(i,size) for i,m in anchors if m['unit']==unit and span(i,size)>0]
        if scales:
            diff=max(scales)/min(scales)
            if any(m['unit']!=unit for _,m in anchors):
                factors.append('Known references use mixed units; explicitly convert units before calibration.')
            elif diff<=1.08:
                scale=sum(scales)/len(scales)
                t=state['tolerance']
                for i in desired:
                    L=span(i,size)*scale
                    m=state['measurements'].get(i['id'])
                    if m and m['quality']=='user_measured' and m['unit']==unit:
                        estimates.append({'id':i['id'],'status':'human_entered_reference',
                          'nominal':m['value'],'low':m['value'],'high':m['value'],
                          'unit':unit,'assumption':'human-reported measurement, not independently verified'})
                    else:
                        estimates.append({'id':i['id'],'status':'conditional_sketch_guess',
                          'nominal':round(L,2),'low':round(L*(1-t),2),'high':round(L*(1+t),2),
                          'unit':unit,'assumption':'drawing roughly proportional; not surveyed'})
            else:
                factors.append('Known references contradict each other on this drawing: HOLD all scale transfer.')
    elif anchors and not state['proportional']:
        factors.append('A known measurement exists, but the sketch has not been declared approximately proportional.')
    hypothetical=[]
    if desired and movable:
        hypothetical.append({'id':'reuse','label':'Reposition existing boundary modules','evidence':[i['id'] for i in movable[:3]],
            'why':'Moving existing fence sections might cover intended new spans.',
            'hold':'Mobility, length, access, fastening and stability still require checking.'})
    if desired and (panels or supports):
        hypothetical.append({'id':'compose','label':'Compose panels and opportunistic supports',
            'evidence':[i['id'] for i in (panels+supports)[:4]],
            'why':'Panels may gain functionality when connected into a network.',
            'hold':'Mutual support and a rated zip tie do not establish structural capacity or pet safety.'})
    if desired:
        hypothetical.append({'id':'redraw','label':'Explore alternate boundary routing','evidence':[i['id'] for i in desired],
            'why':'Moving a boundary may reduce required material or preserve access.',
            'hold':'Comparing drawn lengths does not prove actual yard lengths.'})
    else:
        hypothetical.append({'id':'capture','label':'Trace the intended boundary first','evidence':[],
            'why':'No desired route is confirmed in the editable board.',
            'hold':'Source image remains evidence; no geometry will be invented.'})
    if desired and len(desired)>1:
        reference=desired[0];rs=span(reference,size)
        if rs>0:
            ratios=[{'id':i['id'],'to':reference['id'],'drawn_ratio':round(span(i,size)/rs,2),
                     'status':'drawn_only' if not state['proportional'] else 'conditional_proportionality_assumption'} for i in desired[1:]]
        else:ratios=[]
    else:ratios=[]
    ratio_cues=[]
    for r in state['relations']:
        m=state['measurements'].get(r['other'])
        cue={'target':r['target'],'other':r['other'],'ratio':r['ratio'],
             'status':'user_asserted_rough_relation_not_physical_measurement'}
        if m and m['quality']=='user_measured':
            cue.update({'implied_nominal':round(m['value']*r['ratio'],2),'unit':m['unit'],
                        'status':'implied_from_user_relation_and_human_entered_reference_unverified'})
        ratio_cues.append(cue)
    return {'branch':'A_AUTONOMOUS_READ_ONLY','draft_hypotheses':hypothetical,'estimates':estimates,
            'ratios':ratios,'ratio_cues':ratio_cues,'warnings':factors,
            'verified_physical_assembly':False,'auto_placed_photo_coordinates':False,
            'human_edits_as_physical_observations':False,'version':state['version']}


def interface(state):
    """Interface branch: offers the smallest direct-manipulation clarifications."""
    items=state['items'];ms=state['measurements'];lines=[i for i in items if len(i['points'])==2]
    desired=[i for i in lines if i['kind']=='desired']
    current=[i for i in lines if i['kind']=='current']
    choices=[]
    if not desired:
        choices.append({'id':'trace_route','label':'Trace the intended boundary','action':'trace_desired','value':100,
                        'reason':'Required before route evaluation; editing the source directly avoids another verbal explanation.'})
    else:
        choices.append({'id':'review_route','label':'Check the traced route against the sketch','action':'select_route','value':55,
                        'reason':'User intent cannot be inferred from plausible geometry alone.'})
    if desired and not state['proportional']:
        choices.append({'id':'declare_distortion','label':'Is the sketch roughly proportional?','action':'inspect_proportions','value':72,
                        'reason':'Controls whether ratios can become bounded physical guesses.'})
    if desired and not any(x['quality']=='user_measured' for x in ms.values()):
        choices.append({'id':'measure_reference','label':'Enter one known physical span','action':'measure','value':68,
                        'reason':'One same-plane reference could reduce uncertainty after proportionality is established.'})
    if current and desired:
        choices.append({'id':'confirm_mobility','label':'Correct which existing pieces can move','action':'mobility','value':64,
                        'reason':'Reusing current fence may be easier than building new fencing.'})
    if any(i['kind'] in ('panel','support') for i in items):
        choices.append({'id':'check_support','label':'Mark a connection or unsafe support','action':'support','value':60,
                        'reason':'Temporary attachments must be assessed before animals enter.'})
    if not current:
        choices.append({'id':'mark_current','label':'Trace current movable fencing','action':'trace_current','value':59,
                        'reason':'Existing fencing may be modular inventory, not an immovable boundary.'})
    choices.sort(key=lambda c:-c['value'])
    return {'branch':'B_CONTEXTUAL_EDITING','version':state['version'],'actions':choices[:4],
            'never_required_to_answer':True,'images_transmitted':False}


def think(project):
    state=replay(project)
    out={'schema':'motif.field010.reasoning.v1','state_version':state['version'],
         'solver':solver(state),'interface':interface(state),
         'status':'HYPOTHETICAL_EDITABLE_SKETCH_NOT_ENGINEERING_PLAN'}
    out['receipt_sha256']=sha256(dumps(out,sort_keys=True).encode()).hexdigest()
    return out
