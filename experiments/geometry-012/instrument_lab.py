"""MOTIF GEOM-012: The Question That Builds Its Own Instrument.

Local, synthetic, permission-declared *procedure synthesis* from recorded raw
traces. A proposed executable recipe is not a new physical sensor, a witnessed
measurement, PEN evidence, or an authorization to access external resources.

The grammar is finite (count/filter/odd/nonzero/not/xor/and/or), but the
underlying graph architecture inherited from GEOM-008 remains free-form.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from math import isfinite
from typing import Mapping, Sequence
import hashlib
import json

GRAMMAR_VERSION = 'geom012-procedural-1'


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)


def fingerprint(prefix, obj):
    return prefix + hashlib.sha256(canonical(obj).encode()).hexdigest()


def name(value, label):
    if not isinstance(value, str) or not 1 <= len(value) <= 256 or not value.strip():
        raise ValueError('invalid ' + label)
    return value


def strict_object(obj, keys, label):
    if not isinstance(obj, dict) or set(obj) != set(keys):
        raise ValueError('invalid ' + label + ' fields')


@dataclass(frozen=True)
class Event:
    tick: int
    channel: str

    def __post_init__(self):
        if type(self.tick) is not int or self.tick < 0:
            raise ValueError('event tick must be a nonnegative integer')
        name(self.channel, 'event channel')

    def data(self):
        return {'tick': self.tick, 'channel': self.channel}


@dataclass(frozen=True)
class TraceCase:
    identity: str
    before: tuple[str, ...]
    after: tuple[str, ...]
    visible: tuple[tuple[str, str], ...]
    expected: bool
    events: tuple[Event, ...] | None
    source_root: str
    scope: str

    def __post_init__(self):
        for key, value in [('case identity', self.identity), ('source root', self.source_root), ('scope', self.scope)]:
            name(value, key)
        if self.before == self.after or not self.before or not self.after:
            raise ValueError('before/after must be nonidentical nonempty expressions')
        for x in self.before + self.after:
            name(x, 'expression token')
        if self.visible != tuple(sorted(self.visible)) or len(set(k for k,_ in self.visible)) != len(self.visible):
            raise ValueError('visible features must be sorted and unique')
        for k,v in self.visible:
            name(k,'visible key');name(v,'visible value')
        if type(self.expected) is not bool:
            raise ValueError('expected label must be boolean')
        if self.events is not None and (not isinstance(self.events,tuple) or any(not isinstance(e, Event) for e in self.events)):
            raise ValueError('events must be a tuple of recorded events or None (unknown)')

    @classmethod
    def make(cls, identity, before, after, visible, expected, events, source_root, scope):
        if not isinstance(visible,Mapping) or any(not isinstance(k,str) or not isinstance(v,str) for k,v in visible.items()):
            raise ValueError('visible must be a string-valued mapping')
        return cls(identity,tuple(before),tuple(after),tuple(sorted(visible.items())),
                   expected, None if events is None else tuple(events), source_root,scope)

    def data(self):
        return {'id':self.identity,'before':list(self.before),'after':list(self.after),
                'visible':dict(self.visible),'expected':self.expected,
                'events':None if self.events is None else [e.data() for e in self.events],
                'source_root':self.source_root,'scope':self.scope}


@dataclass(frozen=True)
class Capability:
    channel: str
    cost: float
    permitted: bool
    available: bool
    scope: str

    def __post_init__(self):
        name(self.channel,'capability channel'); name(self.scope,'scope')
        if type(self.cost) not in (int,float) or not isfinite(self.cost) or self.cost<=0:
            raise ValueError('capability cost must be positive finite')
        if type(self.permitted) is not bool or type(self.available) is not bool:
            raise ValueError('capability flags must be explicit booleans')

    def data(self):
        return {'channel':self.channel,'cost':self.cost,'permitted':self.permitted,
                'available':self.available,'scope':self.scope}


@dataclass(frozen=True)
class Atom:
    channel: str
    start: int
    end: int
    transform: str  # ODD(COUNT(FILTER)) or NONZERO(COUNT(FILTER))

    def __post_init__(self):
        name(self.channel,'atom channel')
        if type(self.start) is not int or type(self.end) is not int or self.start < 0 or self.end <= self.start:
            raise ValueError('invalid temporal window')
        if self.transform not in ('ODD','NONZERO'):
            raise ValueError('unrecognized transform')

    def data(self):
        return {'channel':self.channel,'start':self.start,'end':self.end,'transform':self.transform}

    def run(self, events: Sequence[Event]) -> bool:
        count = sum(e.channel==self.channel and self.start<=e.tick<self.end for e in events)
        return bool(count%2) if self.transform=='ODD' else bool(count)


@dataclass(frozen=True)
class Instrument:
    operator: str
    atoms: tuple[Atom, ...]
    scope: str

    def __post_init__(self):
        name(self.scope,'instrument scope')
        if self.operator not in ('ID','NOT','XOR','AND','OR'):
            raise ValueError('unrecognized program operator')
        if len(self.atoms) != (1 if self.operator in ('ID','NOT') else 2):
            raise ValueError('operator arity mismatch')
        if len(set(self.atoms))!=len(self.atoms):
            raise ValueError('program cannot repeat an identical atom')

    def data(self):
        return {'operator':self.operator,'atoms':[a.data() for a in self.atoms],
                'scope':self.scope,'state':'PENCIL','authority':'NONE'}

    def cost(self,catalog: Mapping[str,Capability]) -> float:
        # Synthetic accounting units, not prices or real permission grants.
        return round(sum(catalog[ch].cost for ch in {a.channel for a in self.atoms})
                     +0.1*len(self.atoms)+(0.2 if self.operator not in ('ID',) else 0),9)

    def validate(self,catalog:Mapping[str,Capability], windows: Sequence[tuple[int,int]],budget:float,scope:str):
        if self.scope!=scope or any(a.channel not in catalog for a in self.atoms):
            raise ValueError('instrument scope or channel not declared')
        if any(not catalog[a.channel].permitted or not catalog[a.channel].available or
               catalog[a.channel].scope!=scope for a in self.atoms):
            raise ValueError('instrument uses unavailable or nonpermitted capability')
        if any((a.start,a.end) not in windows for a in self.atoms):
            raise ValueError('instrument requests undeclared temporal window')
        if self.cost(catalog)>budget:
            raise ValueError('instrument exceeds local cost budget')

    def measure(self, case:TraceCase, catalog:Mapping[str,Capability],windows:Sequence[tuple[int,int]],budget:float):
        self.validate(catalog,windows,budget,case.scope)
        if case.events is None:
            return {'status':'HOLD_NO_RECORDED_TRACE','value':None,'authority':'NONE'}
        values=[atom.run(case.events) for atom in self.atoms]
        if self.operator=='ID': result=values[0]
        elif self.operator=='NOT': result=not values[0]
        elif self.operator=='XOR': result=values[0] != values[1]
        elif self.operator=='AND': result=values[0] and values[1]
        else: result=values[0] or values[1]
        return {'status':'LOCAL_TRACE_REPLAY','value':result,'authority':'NONE'}

    def recipe(self):
        """An executable *plan*; never a claim that live acquisition occurred."""
        steps=[]
        for idx,a in enumerate(self.atoms):
            steps.append({'step':'FILTER_RECORDED_EVENTS','output':f'filtered_{idx}',
                          'channel':a.channel,'window':[a.start,a.end]})
            steps.append({'step':'COUNT','input':f'filtered_{idx}','output':f'count_{idx}'})
            steps.append({'step':a.transform,'input':f'count_{idx}','output':f'bit_{idx}'})
        steps.append({'step':self.operator,'inputs':[f'bit_{i}' for i in range(len(self.atoms))],
                      'output':'proposed_measurement'})
        return steps


def instrument_from_data(obj):
    strict_object(obj,('operator','atoms','scope','state','authority'),'instrument')
    if obj['state']!='PENCIL' or obj['authority']!='NONE' or not isinstance(obj['atoms'],list):
        raise ValueError('instrument cannot claim admission or outside authority')
    ats=[]
    for a in obj['atoms']:
        strict_object(a,('channel','start','end','transform'),'atom')
        ats.append(Atom(**a))
    return Instrument(obj['operator'],tuple(ats),obj['scope'])


class InstrumentLab:
    def __init__(self,development:Sequence[TraceCase],capabilities:Sequence[Capability],
                 windows:Sequence[tuple[int,int]],*,scope:str,budget:float):
        self.scope=name(scope,'scope')
        self.development=tuple(development)
        self.capabilities=tuple(capabilities)
        self.windows=tuple(sorted(set(windows)))
        if type(budget) not in (int,float) or not isfinite(budget) or budget<=0:
            raise ValueError('budget must be positive and finite')
        self.budget=budget
        if not self.development or len(set(c.identity for c in self.development))!=len(self.development):
            raise ValueError('development IDs must be nonempty and unique')
        if not self.capabilities or len(set(c.channel for c in self.capabilities))!=len(self.capabilities):
            raise ValueError('capability declarations must be nonempty and unique')
        if any(x.scope!=scope for x in self.development+self.capabilities):
            raise ValueError('observer/time/decoder scope mismatch')
        if not self.windows or any(type(w)!=tuple or len(w)!=2 or type(w[0]) is not int or
                                   type(w[1]) is not int or w[0]<0 or w[1]<=w[0] for w in self.windows):
            raise ValueError('windows must be nonempty valid pairs')
        self.catalog={c.channel:c for c in self.capabilities}
        self.manifest=fingerprint('geom012-capability-manifest:',
               {'scope':scope,'budget':budget,'capabilities':[c.data() for c in sorted(self.capabilities,key=lambda c:c.channel)],
                'windows':[list(w) for w in self.windows],'grammar':GRAMMAR_VERSION})
        self.dataset=fingerprint('geom012-development:',[c.data() for c in self.development])
        self.domain=fingerprint('geom012-search:',{'manifest':self.manifest,'data':self.dataset})

    def collisions(self):
        buckets={}
        for c in self.development:
            buckets.setdefault((c.before,c.after,c.visible),[]).append(c)
        hits=[]
        for group in buckets.values():
            pos=sorted((c for c in group if c.expected),key=lambda c:c.identity)
            neg=sorted((c for c in group if not c.expected),key=lambda c:c.identity)
            if pos and neg:
                hits.append({'positive_case':pos[0].identity,'negative_case':neg[0].identity,
                             'positive_claimed_root':pos[0].source_root,
                             'negative_claimed_root':neg[0].source_root})
        return sorted(hits,key=lambda x:(x['positive_case'],x['negative_case']))

    def diagnose(self):
        conflicts=self.collisions()
        return {'status':'NEEDS_NEW_MEASUREMENT_DIMENSION' if conflicts else 'NO_VISIBLE_COLLISION',
                'witnesses':conflicts,'scope':self.scope,
                'interpretation':'Opposing labels on identical visible inputs cannot be resolved using those inputs alone.',
                'source_roots_authenticated':False,'authority':'NONE'}

    def _candidates(self):
        eligible=sorted((x for x in self.capabilities if x.available and x.permitted),key=lambda c:c.channel)
        atoms=sorted((Atom(c.channel,w[0],w[1],t) for c in eligible
                      for w in self.windows for t in ('ODD','NONZERO')),
                     key=lambda a:canonical(a.data()))
        plans=[]
        for a in atoms:
            plans.extend((Instrument('ID',(a,),self.scope),Instrument('NOT',(a,),self.scope)))
        for a,b in combinations(atoms,2):
            for op in ('XOR','AND','OR'):
                plans.append(Instrument(op,(a,b),self.scope))
        plans=[p for p in plans if p.cost(self.catalog)<=self.budget]
        # Prioritize small operation trees, then synthetic cost, then stable text.
        return sorted(plans,key=lambda p:(len(p.atoms),p.cost(self.catalog),canonical(p.data())))

    def score(self,plan:Instrument,cases:Sequence[TraceCase]):
        plan.validate(self.catalog,self.windows,self.budget,self.scope)
        correct=wrong=unknown=0
        for c in cases:
            if c.scope!=self.scope:
                raise ValueError('case scope mismatch')
            outcome=plan.measure(c,self.catalog,self.windows,self.budget)
            if outcome['status']=='HOLD_NO_RECORDED_TRACE':unknown+=1
            elif outcome['value']==c.expected:correct+=1
            else:wrong+=1
        return {'total':len(cases),'correct':correct,'wrong':wrong,'abstentions':unknown}

    def propose(self,*,work_budget:int,cursor:dict|None=None):
        if type(work_budget) is not int or work_budget<=0:
            raise ValueError('positive integer work budget required')
        if not self.collisions():
            return {'status':'HOLD_NO_DEMONSTRATED_REPRESENTATIONAL_GAP','authority':'NONE'}
        if len({c.source_root for c in self.development})<2:
            return {'status':'HOLD_INSUFFICIENT_DECLARED_SOURCE_ROOTS','authority':'NONE'}
        if any(c.events is None for c in self.development):
            return {'status':'HOLD_NEEDS_RECORDED_PILOT_TRACE','authority':'NONE'}
        candidates=self._candidates()
        offset=0
        if cursor is not None:
            if (not isinstance(cursor,dict) or set(cursor)!={'domain','offset'} or cursor['domain']!=self.domain or
                    type(cursor['offset']) is not int or not 0<=cursor['offset']<=len(candidates)):
                raise ValueError('invalid or mismatched search cursor')
            offset=cursor['offset']
            # Re-evaluate skipped prefix to reject forged optimality/provenance.
            for earlier in candidates[:offset]:
                s=self.score(earlier,self.development)
                if s['correct']==len(self.development) and s['abstentions']==0:
                    raise ValueError('continuation cursor skipped an earlier exact fit')
        for index in range(offset,min(len(candidates),offset+work_budget)):
            plan=candidates[index]
            result=self.score(plan,self.development)
            if result['correct']==len(self.development) and result['abstentions']==0:
                return {'status':'PENCIL_INSTRUMENT_PROPOSED','instrument':plan.data(),
                        'procedure':plan.recipe(),'development':result,
                        'candidate_rank':index+1,'candidate_space_size':len(candidates),
                        'search_domain':self.domain,'capability_manifest':self.manifest,
                        'development_fingerprint':self.dataset,
                        'synthetic_cost':plan.cost(self.catalog),
                        'completeness':'FIRST_EXACT_FIT_BY_DECLARED_SIZE_COST_ORDER',
                        'live_measurement_performed':False,'source_roots_authenticated':False,
                        'authority':'NONE','state':'PENCIL'}
        position=min(len(candidates),offset+work_budget)
        if position<len(candidates):
            return {'status':'CONTINUE_SEARCH','cursor':{'domain':self.domain,'offset':position},
                    'evaluated_this_slice':position-offset,'candidate_space_size':len(candidates),
                    'completeness':'INCOMPLETE','authority':'NONE'}
        return {'status':'HOLD_NO_EXACT_PROCEDURE_IN_DECLARED_GRAMMAR',
                'candidate_space_size':len(candidates),'authority':'NONE'}

    def evaluate_heldout(self,proposal:dict,heldout:Sequence[TraceCase]):
        plan=self.validate_proposal(proposal)
        cases=tuple(heldout)
        if set(c.identity for c in cases) & set(c.identity for c in self.development):
            raise ValueError('heldout case ID overlaps development')
        if not cases or len(set(c.identity for c in cases))!=len(cases):
            raise ValueError('invalid heldout IDs')
        return {'status':'LOCAL_HELDOUT_TRACE_REPLAY','scores':self.score(plan,cases),
                'heldout_fingerprint':fingerprint('geom012-heldout:',[c.data() for c in cases]),
                'live_measurement_performed':False,'authority':'NONE'}

    def validate_proposal(self,proposal:dict)->Instrument:
        if not isinstance(proposal,dict) or proposal.get('status')!='PENCIL_INSTRUMENT_PROPOSED':
            raise ValueError('expected PENCIL procedure proposal')
        if (proposal.get('search_domain')!=self.domain or proposal.get('capability_manifest')!=self.manifest or
                proposal.get('development_fingerprint')!=self.dataset or proposal.get('authority')!='NONE' or
                proposal.get('state')!='PENCIL' or proposal.get('live_measurement_performed') is not False):
            raise ValueError('forged or incompatible proposal receipt')
        plan=instrument_from_data(proposal['instrument'])
        plan.validate(self.catalog,self.windows,self.budget,self.scope)
        # Critical: recompute full ranked search rather than trusting a claimed
        # winning rule, developer score, or manually edited recipe.
        recomputed=self.propose(work_budget=len(self._candidates())+1)
        if recomputed['status']!='PENCIL_INSTRUMENT_PROPOSED' or proposal!=recomputed:
            raise ValueError('proposal fails exact replay and score verification')
        return plan

    def archive_pencil(self,graph,proposal:dict):
        if graph.scope!=self.scope:
            raise ValueError('graph scope mismatch')
        plan=self.validate_proposal(proposal)
        pid=fingerprint('geom012-instrument:',{'manifest':self.manifest,'development':self.dataset,
                                               'instrument':plan.data()})
        graph.add_node(pid,kind='proposed_measurement_procedure',label=plan.operator,
                       payload={'instrument':plan.data(),'recipe':plan.recipe(),'state':'PENCIL'},
                       source_root='geom012:synthetic-local')
        witnesses=[('proposal',pid)]
        for c in self.development:
            cid=fingerprint('geom012-trace-case:',c.data())
            # Do not archive raw samples from channels the local manifest says
            # cannot be read; a capability restriction also applies to traces.
            public=c.data()
            if public['events'] is not None:
                public['events']=[e.data() for e in c.events if
                    e.channel in self.catalog and
                    self.catalog[e.channel].permitted and self.catalog[e.channel].available]
            graph.add_node(cid,kind='declared_raw_trace_case',label=c.identity,
                           payload=public,source_root=c.source_root)
            witnesses.append(('development_case',cid))
        graph.add_relation('proposed_instrument_supported_by_declared_traces',witnesses,
                           source_root='geom012:synthetic-local',
                           note={'state':'PENCIL','scope':self.scope,'permission':'NO_EXTERNAL_AUTHORITY'})
        return {'status':'ARCHIVED_PENCIL_ONLY','node_id':pid,
                'declared_trace_cases':len(self.development),'authority':'NONE'}


def event_from_document(obj):
    strict_object(obj,('tick','channel'),'event')
    return Event(obj['tick'],obj['channel'])


def case_from_document(obj):
    strict_object(obj,('id','before','after','visible','expected','events','source_root','scope'),'case')
    if not isinstance(obj['before'],list) or not isinstance(obj['after'],list) or not isinstance(obj['events'],(list,type(None))):
        raise ValueError('bad expression or events arrays')
    return TraceCase.make(obj['id'],obj['before'],obj['after'],obj['visible'],obj['expected'],
                          None if obj['events'] is None else [event_from_document(e) for e in obj['events']],
                          obj['source_root'],obj['scope'])


def capability_from_document(obj):
    strict_object(obj,('channel','cost','permitted','available','scope'),'capability')
    return Capability(**obj)


def run_document(doc):
    allowed={'scope','development','capabilities','windows','budget','work_budget','cursor'}
    if not isinstance(doc,dict) or set(doc)-allowed or not allowed-{'cursor'}<=set(doc):
        raise ValueError('unknown or missing instrument request fields')
    if not isinstance(doc['development'],list) or not isinstance(doc['capabilities'],list) or not isinstance(doc['windows'],list):
        raise ValueError('expected array fields')
    lab=InstrumentLab([case_from_document(c) for c in doc['development']],
        [capability_from_document(c) for c in doc['capabilities']],
        [tuple(w) for w in doc['windows']],scope=doc['scope'],budget=doc['budget'])
    return {'diagnosis':lab.diagnose(),
            'synthesis':lab.propose(work_budget=doc['work_budget'],cursor=doc.get('cursor'))}
