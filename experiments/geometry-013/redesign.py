"""MOTIF GEOM-013: revise a measurement procedure after counterexamples.

Synthesizes insertions of a typed DISTINCT_BY_EVENT_ID step into an inherited
GEOM-012 trace-measurement recipe. A synthetic identifier is a *declaration*,
not a verified physical event ID. The procedure is PENCIL only. No live reads,
source authentication, learning about the outside world, or external actions.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from math import isfinite
from pathlib import Path
from typing import Mapping, Sequence
import sys

# On GitHub this is a stacked dependency, not a copied/reimplemented predecessor.
sys.path.append(str(Path(__file__).resolve().parent.parent / 'geometry-012'))
from instrument_lab import (Atom, Capability, Event, Instrument, TraceCase,
                            canonical, fingerprint, name, instrument_from_data)

GRAMMAR = 'geom013-insert-distinct-record-id/v1'


@dataclass(frozen=True)
class RecordedEvent:
    tick: int
    channel: str
    event_id: str | None

    def __post_init__(self):
        Event(self.tick, self.channel)  # predecessor's original validation
        if self.event_id is not None:
            name(self.event_id, 'declared event identity')

    def data(self):
        return {'tick': self.tick, 'channel': self.channel, 'event_id': self.event_id}


@dataclass(frozen=True)
class RecordedCase:
    identity: str
    before: tuple[str, ...]
    after: tuple[str, ...]
    visible: tuple[tuple[str, str], ...]
    expected: bool
    records: tuple[RecordedEvent, ...] | None
    source_root: str
    scope: str

    def __post_init__(self):
        # Validate against GEOM-012's actual TraceCase type. No label or source
        # is inferred from record count; target labels are declared test data.
        if self.records is not None and (not isinstance(self.records, tuple) or
           not all(isinstance(r, RecordedEvent) for r in self.records)):
            raise ValueError('all records must be RecordedEvent')
        TraceCase(self.identity, self.before, self.after, self.visible, self.expected,
                  None if self.records is None else tuple(Event(r.tick, r.channel) for r in self.records),
                  self.source_root, self.scope)

    @classmethod
    def make(cls, identity, before, after, visible:Mapping[str,str], expected,
             records, source_root, scope):
        if not isinstance(visible,Mapping) or any(not isinstance(k,str) or not isinstance(v,str) for k,v in visible.items()):
            raise ValueError('visible context must map string keys to strings')
        return cls(identity,tuple(before),tuple(after),tuple(sorted(visible.items())),
                   expected,None if records is None else tuple(records),source_root,scope)

    def data(self):
        return {'id':self.identity,'before':list(self.before),'after':list(self.after),
                'visible':dict(self.visible),'expected':self.expected,
                'records':None if self.records is None else [r.data() for r in self.records],
                'source_root':self.source_root,'scope':self.scope}


@dataclass(frozen=True)
class IdentifierAccess:
    scope: str
    permitted: bool
    available: bool
    unit_cost: float

    def __post_init__(self):
        name(self.scope,'scope')
        if type(self.permitted) is not bool or type(self.available) is not bool:
            raise ValueError('identifier access requires explicit permission/availability')
        if type(self.unit_cost) not in (int,float) or not isfinite(self.unit_cost) or self.unit_cost<=0:
            raise ValueError('identifier cost must be positive finite')

    def data(self):
        return {'scope':self.scope,'permitted':self.permitted,
                'available':self.available,'unit_cost':self.unit_cost}


@dataclass(frozen=True)
class Revision:
    """Two GEOM-012 atoms can be deduplicated independently, without changing their meaning.

    `distinct` has an entry per inherited atom; GEOM-012 itself supports up to
    two atoms. This experiment does NOT impose a node or depth bound on GEOM-008.
    """
    parent: Instrument
    distinct: tuple[bool, ...]

    def __post_init__(self):
        if len(self.distinct)!=len(self.parent.atoms) or any(type(v) is not bool for v in self.distinct):
            raise ValueError('revision needs one Boolean step flag per original atom')

    def data(self):
        return {'parent':self.parent.data(), 'distinct_by_declared_event_id':list(self.distinct),
                'grammar':GRAMMAR,'state':'PENCIL','authority':'NONE'}

    def recipe(self):
        steps=[]
        for i, atom in enumerate(self.parent.atoms):
            steps.append({'step':'FILTER_RECORDED_EVENTS','channel':atom.channel,
                          'window':[atom.start,atom.end],'output':f'events_{i}'})
            source=f'events_{i}'
            if self.distinct[i]:
                steps.append({'step':'DISTINCT_BY_DECLARED_EVENT_ID','input':source,
                              'output':f'unique_{i}','identity_authentication':False,
                              'on_missing_or_collision':'HOLD'})
                source=f'unique_{i}'
            steps.append({'step':'COUNT','input':source,'output':f'count_{i}'})
            steps.append({'step':atom.transform,'input':f'count_{i}','output':f'bit_{i}'})
        steps.append({'step':self.parent.operator,'inputs':[f'bit_{i}' for i in range(len(self.distinct))],
                      'output':'proposed_measurement'})
        return steps

    def synthetic_cost(self, catalog:Mapping[str,Capability], access:IdentifierAccess):
        return round(self.parent.cost(catalog)+sum(self.distinct)*access.unit_cost, 9)

    def validate(self,catalog:Mapping[str,Capability],windows:Sequence[tuple[int,int]],
                 budget:float,access:IdentifierAccess,scope:str):
        if self.parent.scope!=scope or access.scope!=scope:
            raise ValueError('observer/decoder/scope mismatch')
        self.parent.validate(catalog,windows,budget,scope)
        if any(self.distinct) and (not access.permitted or not access.available):
            raise ValueError('declared event-id capability unavailable or not permitted')
        if self.synthetic_cost(catalog,access)>budget:
            raise ValueError('redesigned procedure exceeds synthetic cost budget')

    def measure(self,case:RecordedCase,catalog:Mapping[str,Capability],
                windows:Sequence[tuple[int,int]],budget:float,access:IdentifierAccess):
        self.validate(catalog,windows,budget,access,case.scope)
        if case.records is None:
            return {'status':'HOLD_NO_RECORDED_TRACE','value':None,'authority':'NONE'}
        values=[]
        for i,atom in enumerate(self.parent.atoms):
            selected=[r for r in case.records
                      if r.channel==atom.channel and atom.start<=r.tick<atom.end]
            if self.distinct[i]:
                if any(r.event_id is None for r in selected):
                    return {'status':'HOLD_NO_DECLARED_EVENT_ID','value':None,'authority':'NONE'}
                seen={}
                for r in selected:
                    if r.event_id in seen and seen[r.event_id]!=(r.channel,r.tick):
                        return {'status':'HOLD_CONFLICTING_EVENT_ID','value':None,'authority':'NONE'}
                    seen[r.event_id]=(r.channel,r.tick)
                count=len(seen)
            else:
                count=len(selected)
            values.append(bool(count%2) if atom.transform=='ODD' else bool(count))
        op=self.parent.operator
        if op=='ID':value=values[0]
        elif op=='NOT':value=not values[0]
        elif op=='XOR':value=values[0]!=values[1]
        elif op=='AND':value=values[0] and values[1]
        elif op=='OR':value=values[0] or values[1]
        else:raise ValueError('unexpected inherited GEOM-012 operator')
        return {'status':'LOCAL_SYNTHETIC_REPLAY','value':value,'authority':'NONE'}


def revision_from_data(data):
    if not isinstance(data,dict) or set(data)!={'parent','distinct_by_declared_event_id','grammar','state','authority'}:
        raise ValueError('invalid revision receipt fields')
    if data['grammar']!=GRAMMAR or data['state']!='PENCIL' or data['authority']!='NONE':
        raise ValueError('revision cannot claim a different grammar or authority')
    if not isinstance(data['distinct_by_declared_event_id'],list):
        raise ValueError('distinct flags must be list')
    return Revision(instrument_from_data(data['parent']),tuple(data['distinct_by_declared_event_id']))


class RedesignLab:
    """Development-driven instrument debugging. Never consults withheld cases in search."""
    def __init__(self,parent:Instrument,capabilities:Sequence[Capability],
                 windows:Sequence[tuple[int,int]],identifier_access:IdentifierAccess,
                 development:Sequence[RecordedCase],*,budget:float):
        self.parent=parent
        self.scope=parent.scope
        self.capabilities=tuple(capabilities)
        self.catalog={c.channel:c for c in self.capabilities}
        self.windows=tuple(windows)
        self.identifier_access=identifier_access
        self.development=tuple(development)
        self.budget=budget
        if not self.development or type(budget) not in (int,float) or not isfinite(budget) or budget<=0:
            raise ValueError('finite positive cost budget and development required')
        if len(self.catalog)!=len(self.capabilities):
            raise ValueError('duplicate channel capability')
        if len({c.identity for c in self.development})!=len(self.development):
            raise ValueError('duplicate development IDs')
        if any(c.scope!=self.scope for c in self.development):
            raise ValueError('cross-observer/time/decoder cases refused')
        Revision(parent,tuple(False for _ in parent.atoms)).validate(
            self.catalog,self.windows,self.budget,identifier_access,self.scope)
        self.manifest=fingerprint('geom013-capability-manifest:',
              {'base':parent.data(),'capabilities':[c.data() for c in self.capabilities],
               'windows':[list(x) for x in self.windows], 'uid_access':identifier_access.data(),
               'budget':budget,'grammar':GRAMMAR})
        self.dataset=fingerprint('geom013-development:',[c.data() for c in self.development])

    def evaluation(self,revision:Revision,cases:Sequence[RecordedCase]):
        if revision.parent!=self.parent:
            raise ValueError('parent instrument changed')
        revision.validate(self.catalog,self.windows,self.budget,self.identifier_access,self.scope)
        out={'total':len(cases),'correct':0,'wrong':0,'abstentions':0,'false_positives':0,
             'false_negatives':0,'by_status':{},'wrong_ids':[]}
        for c in cases:
            if c.scope!=self.scope:raise ValueError('cross-scope evaluation refused')
            pred=revision.measure(c,self.catalog,self.windows,self.budget,self.identifier_access)
            st=pred['status'];out['by_status'][st]=out['by_status'].get(st,0)+1
            if pred['value'] is None:out['abstentions']+=1
            elif pred['value']==c.expected:out['correct']+=1
            else:
                out['wrong']+=1;out['wrong_ids'].append(c.identity)
                out['false_positives']+=bool(pred['value'] and not c.expected)
                out['false_negatives']+=bool(not pred['value'] and c.expected)
        return out

    def critic(self,revision:Revision):
        scores=self.evaluation(revision,self.development)
        conflicting={}
        for c in self.development:
            # Only exact same observed raw record contents + same visible context;
            # uncertain labels can disagree without proving which is right.
            sig=canonical({'before':c.before,'after':c.after,'visible':c.visible,
                           'records':None if c.records is None else sorted((r.data() for r in c.records),key=canonical)})
            conflicting.setdefault(sig,[]).append(c)
        contradictions=[sorted(c.identity for c in group) for group in conflicting.values()
                        if len({c.expected for c in group})>1]
        witnesses=[]
        by_id={c.identity:c for c in self.development}
        for case_id in scores['wrong_ids']:
            case=by_id[case_id]
            duplicate_channels=[]
            for atom in revision.parent.atoms:
                observed=[x.event_id for x in case.records or ()
                          if x.channel==atom.channel and atom.start<=x.tick<atom.end and x.event_id is not None]
                if len(observed)!=len(set(observed)):
                    duplicate_channels.append(atom.channel)
            witnesses.append({'case':case_id,'declared_root':case.source_root,
                              'candidate_duplicate_channels':sorted(set(duplicate_channels))})
        return {'status':'HOLD_CONTRADICTORY_RECORDED_LABELS' if contradictions else
                'REVISE_MEASUREMENT' if scores['wrong'] or scores['abstentions'] else 'DEVELOPMENT_FIT',
                'scores':scores,'contradictory_record_sets':sorted(contradictions),
                'counterexamples':witnesses,'roots_authenticated':False,'authority':'NONE'}

    def _candidates(self,active:Revision):
        if active.parent!=self.parent:raise ValueError('active plan has different parent')
        if not self.identifier_access.permitted or not self.identifier_access.available:
            return []
        remaining=[i for i,d in enumerate(active.distinct) if not d]
        out=[]
        for n in range(1,len(remaining)+1):
            for positions in combinations(remaining,n):
                flags=list(active.distinct)
                for i in positions:flags[i]=True
                proposed=Revision(self.parent,tuple(flags))
                if proposed.synthetic_cost(self.catalog,self.identifier_access)<=self.budget:
                    out.append(proposed)
        return sorted(out,key=lambda p:(sum(p.distinct)-sum(active.distinct),
                        p.synthetic_cost(self.catalog,self.identifier_access),canonical(p.data())))

    def propose(self,active:Revision,*,work_budget:int,cursor=None):
        if type(work_budget) is not int or work_budget<=0:raise ValueError('work_budget must be positive integer')
        active.validate(self.catalog,self.windows,self.budget,self.identifier_access,self.scope)
        diagnostic=self.critic(active)
        if diagnostic['contradictory_record_sets']:
            return {'status':'HOLD_CONTRADICTORY_RECORDS','conflicts':diagnostic['contradictory_record_sets'],
                    'authority':'NONE'}
        if diagnostic['status']=='DEVELOPMENT_FIT':
            return {'status':'HOLD_NO_FEEDBACK_GAP','authority':'NONE'}
        if len({c.source_root for c in self.development})<2:
            return {'status':'HOLD_DECLARED_SOURCE_ROOTS','authority':'NONE'}
        if any(c.records is None for c in self.development):
            return {'status':'HOLD_NEEDS_RECORDED_DEVELOPMENT','authority':'NONE'}
        candidates=self._candidates(active)
        if not candidates:
            return {'status':'HOLD_NO_PERMITTED_REDESIGN','authority':'NONE'}
        domain=fingerprint('geom013-search:',{'manifest':self.manifest,'development':self.dataset,
                                               'active':active.data()})
        offset=0
        if cursor is not None:
            if (not isinstance(cursor,dict) or set(cursor)!={'domain','offset'} or
                cursor['domain']!=domain or type(cursor['offset']) is not int or
                not 0<=cursor['offset']<=len(candidates)):
                raise ValueError('forged or mismatched cursor')
            offset=cursor['offset']
            for old in candidates[:offset]:
                oldscore=self.evaluation(old,self.development)
                if oldscore['correct']==len(self.development) and not oldscore['abstentions']:
                    raise ValueError('cursor skipped an earlier exact fit')
        for i in range(offset,min(offset+work_budget,len(candidates))):
            candidate=candidates[i]
            result=self.evaluation(candidate,self.development)
            if result['correct']==len(self.development) and result['abstentions']==0:
                return {'status':'PENCIL_INSTRUMENT_REDESIGN_PROPOSED',
                        'from':active.data(),'to':candidate.data(),
                        'recipe':candidate.recipe(),'development':result,
                        'candidate_rank':i+1,'domain':domain,'manifest':self.manifest,
                        'dataset':self.dataset,'candidate_space':len(candidates),
                        'live_measurement_performed':False,'roots_authenticated':False,
                        'authority':'NONE','state':'PENCIL'}
        pos=min(offset+work_budget,len(candidates))
        if pos<len(candidates):
            return {'status':'CONTINUE_SEARCH','cursor':{'domain':domain,'offset':pos},
                    'completeness':'INCOMPLETE','authority':'NONE'}
        return {'status':'HOLD_NO_EXACT_REDESIGN_IN_DECLARED_GRAMMAR',
                'candidate_space':len(candidates),'authority':'NONE'}

    def validate_proposal(self,active:Revision,proposal:dict):
        if not isinstance(proposal,dict) or proposal.get('status')!='PENCIL_INSTRUMENT_REDESIGN_PROPOSED':
            raise ValueError('not an executable proposal')
        recalculated=self.propose(active,work_budget=len(self._candidates(active))+1)
        if proposal!=recalculated:
            raise ValueError('forged/altered redesign receipt or development score')
        result=revision_from_data(proposal['to'])
        result.validate(self.catalog,self.windows,self.budget,self.identifier_access,self.scope)
        return result

    def heldout(self,active:Revision,proposal:dict,cases:Sequence[RecordedCase]):
        candidate=self.validate_proposal(active,proposal)
        cases=tuple(cases)
        if not cases or len({c.identity for c in cases})!=len(cases) or \
           set(c.identity for c in cases) & set(c.identity for c in self.development):
            raise ValueError('invalid heldout IDs / contamination')
        result=self.evaluation(candidate,cases)
        return {'status':'SYNTHETIC_HELDOUT_REPLAY','scores':result,
                'heldout_fingerprint':fingerprint('geom013-heldout:',[c.data() for c in cases]),
                'live_measurement_performed':False,'authority':'NONE'}

    def archive_pencil(self,graph,active:Revision,proposal:dict):
        if graph.scope!=self.scope:raise ValueError('archive scope mismatch')
        candidate=self.validate_proposal(active,proposal)
        ident=fingerprint('geom013-revision:',{'manifest':self.manifest,'dataset':self.dataset,
                'prior':active.data(),'revision':candidate.data()})
        graph.add_node(ident,kind='proposed_revised_measurement_procedure',label='DISTINCT_BY_EVENT_ID',
                       payload={'from':active.data(),'to':candidate.data(),'procedure':candidate.recipe(),
                                'admission':'PENCIL_ONLY'},source_root='geom013:local-synthetic')
        participants=[('candidate',ident)]
        for c in self.development:
            # Archive only attributed CASE IDs and content digests; never raw
            # traces or channel contents, even for forbidden/hidden channels.
            cid=fingerprint('geom013-feedback:',c.data())
            graph.add_node(cid,kind='declared_measurement_feedback',label=c.identity,
                           payload={'id':c.identity,'digest':cid,'root':c.source_root,
                                    'scope':c.scope,'state':'PENCIL'},source_root=c.source_root)
            participants.append(('feedback',cid))
        graph.add_relation('instrument_redesign_feedback_trace',participants,
                           source_root='geom013:local-synthetic',
                           note={'scope':self.scope,'admission':'PENCIL_ONLY'})
        return {'status':'ARCHIVED_PENCIL_ONLY','node_id':ident,
                'feedback_cases':len(self.development),'authority':'NONE'}


def case_from_document(obj):
    if not isinstance(obj,dict) or set(obj)!={'id','before','after','visible','expected','records','source_root','scope'}:
        raise ValueError('invalid recorded case')
    if not isinstance(obj['before'],list) or not isinstance(obj['after'],list) or \
       not isinstance(obj['records'],(list,type(None))):
        raise ValueError('invalid trace fields')
    records=None if obj['records'] is None else []
    if records is not None:
        for r in obj['records']:
            if not isinstance(r,dict) or set(r)!={'tick','channel','event_id'}:
                raise ValueError('invalid recorded event')
            records.append(RecordedEvent(**r))
    return RecordedCase.make(obj['id'],obj['before'],obj['after'],obj['visible'],obj['expected'],
                             records,obj['source_root'],obj['scope'])


def run_document(doc):
    required={'parent','capabilities','windows','identifier_access','development','budget','work_budget'}
    if not isinstance(doc,dict) or not required<=set(doc) or set(doc)-required-{'active','cursor'}:
        raise ValueError('unknown or missing GEOM-013 document field')
    if not all(isinstance(doc[k],list) for k in ('capabilities','windows','development')):
        raise ValueError('expected list inputs')
    from instrument_lab import capability_from_document
    parent=instrument_from_data(doc['parent'])
    cap=[capability_from_document(x) for x in doc['capabilities']]
    access=doc['identifier_access']
    if not isinstance(access,dict) or set(access)!={'scope','permitted','available','unit_cost'}:
        raise ValueError('invalid identifier access declaration')
    lab=RedesignLab(parent,cap,[tuple(x) for x in doc['windows']],IdentifierAccess(**access),
                    [case_from_document(x) for x in doc['development']],budget=doc['budget'])
    active=revision_from_data(doc['active']) if 'active' in doc else Revision(parent,tuple(False for _ in parent.atoms))
    return {'critic':lab.critic(active),'proposal':lab.propose(active,
                            work_budget=doc['work_budget'],cursor=doc.get('cursor'))}
