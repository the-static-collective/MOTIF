"""MOTIF GEOM-010: scoped, evidence-segregated reasoning-grammar refinement.

Three explicit roles: Explorer (counterfactual paths), Critic (falsifiers), Inventor
(exhaustive budget-resumable conjunction search). This is classical symbolic rule
learning under declared synthetic facts, *not* unsupervised intelligence.
New rules are PENCIL; they never rebind a live graph or confer permission.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from itertools import combinations, islice
from pathlib import Path
from math import isfinite
from typing import Mapping, Sequence
import hashlib
import json
import sys
import time

# Exact dependency on preceding experiment, stacked in this GitHub branch.
sys.path.append(str(Path(__file__).resolve().parent.parent / 'geometry-009'))
from living_graph import RewriteRule, RewriteGrammar, LivingGraph, canonical, stable_id, nonempty
from grammar_invention import Example, propose_revision, rule_from_proposal, predicts


@dataclass(frozen=True)
class SituatedCase:
    identity: str
    before: tuple[str, ...]
    after: tuple[str, ...]
    expected: bool
    facts: tuple[tuple[str, str], ...]
    source_root: str
    scope: str

    def __post_init__(self):
        for x, name in [(self.identity, 'case ID'), (self.source_root, 'source root'), (self.scope, 'scope')]:
            nonempty(x, name)
        if type(self.expected) is not bool:
            raise ValueError('expected label must be boolean')
        if self.before == self.after:
            raise ValueError('identity rewrites cannot be labeled examples')
        for token in self.before + self.after:
            nonempty(token, 'token')
        if tuple(sorted(self.facts)) != self.facts or len(set(k for k, _ in self.facts)) != len(self.facts):
            raise ValueError('facts must be sorted, unique feature keys')
        for k, v in self.facts:
            nonempty(k, 'fact key'); nonempty(v, 'fact value')

    def data(self):
        return {'id': self.identity, 'before': list(self.before), 'after': list(self.after),
                'expected': self.expected, 'facts': dict(self.facts),
                'source_root': self.source_root, 'scope': self.scope}

    @staticmethod
    def make(identity, before, after, expected, facts: Mapping, source_root, scope):
        if not isinstance(facts, Mapping) or any(not isinstance(k, str) or not isinstance(v, str)
                                                 for k, v in facts.items()):
            raise ValueError('fact values must be strings in a mapping')
        return SituatedCase(identity, tuple(before), tuple(after), expected,
                           tuple(sorted(facts.items())), source_root, scope)


@dataclass(frozen=True)
class ConditionalRule:
    base: RewriteRule
    guard: tuple[tuple[str, str], ...]
    scope: str

    def __post_init__(self):
        nonempty(self.scope, 'scope')
        if tuple(sorted(self.guard)) != self.guard or len(set(k for k, _ in self.guard)) != len(self.guard):
            raise ValueError('guard conditions must have unique ordered feature keys')
        for k,v in self.guard:
            nonempty(k,'guard key'); nonempty(v,'guard value')

    def data(self):
        return {'base': {'name':self.base.name, 'find':list(self.base.find), 'replace':list(self.base.replace)},
                'guard':dict(self.guard), 'scope':self.scope, 'admission':'PENCIL_ONLY'}

    def decide(self, case: SituatedCase):
        """Tri-valued result. Missing needed facts -> UNKNOWN, never a fabricated negative.

        Distinguish a categorical mismatch from missing context. A mismatch is
        enough to reject, even if a separate guard fact is absent.
        """
        if case.scope != self.scope:
            raise ValueError('cross-scope evaluation refused')
        if not any(out == case.after for _, out in self.base.outcomes(case.before)):
            return False
        facts = dict(case.facts)
        if any(k in facts and facts[k] != v for k,v in self.guard):
            return False
        if any(k not in facts for k,_ in self.guard):
            return None
        return True


def score(rule: ConditionalRule, cases: Sequence[SituatedCase]):
    tp=fp=tn=fn=unknown=0
    for c in cases:
        p=rule.decide(c)
        if p is None: unknown += 1
        elif p and c.expected:tp += 1
        elif p and not c.expected:fp += 1
        elif not p and not c.expected:tn += 1
        else:fn += 1
    return {'total':len(cases), 'correct':tp+tn, 'true_positives':tp,
            'false_positives':fp, 'true_negatives':tn, 'false_negatives':fn,
            'abstentions':unknown}


def _verify_cases(cases: Sequence[SituatedCase], *, scope: str):
    if any(c.scope != scope for c in cases):
        raise ValueError('cross-scope cases refused')
    ids=[c.identity for c in cases]
    if len(ids)!=len(set(ids)):
        raise ValueError('duplicate case IDs across data partitions')


def critic(rule: ConditionalRule, cases: Sequence[SituatedCase]):
    """Diagnostic, not an autonomous judge of real-world truth."""
    _verify_cases(cases, scope=rule.scope)
    false_pos, false_neg, unknown=[],[],[]
    signatures={}
    for case in cases:
        prediction=rule.decide(case)
        if prediction is None:unknown.append(case.identity)
        elif prediction and not case.expected:false_pos.append(case.identity)
        elif not prediction and case.expected:false_neg.append(case.identity)
        sig=(case.before,case.after,case.facts)
        signatures.setdefault(sig,[]).append(case)
    # If exact visible inputs have opposing labels, *no deterministic rule using
    # only these inputs* can satisfy every case. Do not invent a missing sensor.
    collisions=[]
    for group in signatures.values():
        if len(set(x.expected for x in group))>1:
            collisions.append(sorted(x.identity for x in group))
    return {'status': ('UNRESOLVABLE_IN_OBSERVED_VOCABULARY' if collisions else
                       'REFINEMENT_NEEDED' if false_pos or false_neg or unknown else 'DEVELOPMENT_FIT'),
            'false_positives':false_pos,'false_negatives':false_neg,
            'missing_context_abstentions':unknown,'indistinguishable_label_conflicts':sorted(collisions),
            'authority':'NONE','instrument':'PENCIL'}


def possible_guards(base: RewriteRule, cases: Sequence[SituatedCase]):
    """Enumerate conjunctions drawn exclusively from *shared positive* facts.

    No fixed feature-count cap; the combinatorial cost is controlled by a
    per-invocation search work/time slice. Empty conjunction is first.
    """
    positives=[c for c in cases if c.expected and any(out==c.after for _,out in base.outcomes(c.before))]
    if not positives:
        return
    common=set(positives[0].facts)
    for c in positives[1:]:common &= set(c.facts)
    universe=sorted(common)
    yield ()
    for arity in range(1,len(universe)+1):
        yield from combinations(universe,arity)


def invent_guard(base: RewriteRule, cases: Sequence[SituatedCase], *, scope: str,
                 work_budget: int, cursor: dict | None=None, seconds:float | None=None):
    """Deterministic complete candidate search in slices, no heldout exposure.

    Recompute earlier prefix of search on resume to prevent cursor-forged winning
    candidate. This is intentionally expensive for huge candidate spaces; a future
    SQLite frontier will avoid replay while retaining the source-bound contract.
    """
    cases=tuple(cases)
    _verify_cases(cases,scope=scope)
    if not cases or not any(c.expected for c in cases) or not any(not c.expected for c in cases):
        return {'status':'HOLD','reason':'positive and negative development feedback required','authority':'NONE'}
    if type(work_budget) is not int or work_budget<=0:
        raise ValueError('work_budget must be positive integer')
    if seconds is not None and (type(seconds) not in (int,float) or not isfinite(seconds) or seconds<=0):
        raise ValueError('seconds must be finite positive')
    domain=stable_id('geom010-guard-search:',{'base':(base.name,base.find,base.replace),
        'scope':scope,'cases':[c.data() for c in cases]})
    if cursor is None:offset=0
    else:
        if not isinstance(cursor,dict) or set(cursor)!={'domain','offset'} or cursor['domain']!=domain \
           or type(cursor['offset']) is not int or cursor['offset']<0:
            raise ValueError('mismatched or forged cursor')
        offset=cursor['offset']
    # Replay and validate the entire skipped prefix on resume; a client may
    # not forge a large offset and skip simpler explanations.
    stream=possible_guards(base,cases)
    for _ in range(offset):
        skipped=next(stream,None)
        if skipped is None:
            raise ValueError('cursor beyond candidate search domain')
        earlier=ConditionalRule(base,skipped,scope)
        previous=score(earlier,cases)
        if previous['correct']==len(cases) and previous['abstentions']==0:
            raise ValueError('cursor skipped an already successful shorter guard')
    deadline=time.monotonic()+seconds if seconds is not None else None
    evaluated=0
    for guard in stream:
        if evaluated >= work_budget or (deadline is not None and time.monotonic() >= deadline):
            return {'status':'CONTINUE_SEARCH','cursor':{'domain':domain,'offset':offset+evaluated},
                    'evaluated_this_slice':evaluated,'completeness':'INCOMPLETE','authority':'NONE'}
        evaluated+=1
        r=ConditionalRule(base,guard,scope)
        result=score(r,cases)
        if result['correct']==len(cases) and result['abstentions']==0:
            # First complete fit has lowest number of terms by generator order.
            best=r
            # Search is complete *only* if no later stronger candidate is needed.
            # Here our stated objective is minimum guard length; all remaining
            # guards are equal/longer and lexicographically later.
            return {'status':'PENCIL_GUARD_INVENTED', 'rule':r.data(), 'development':result,
                    'tested_candidates':offset+evaluated,'optimality':
                    'FIRST_EXACT_FIT_IN_SIZE_LEX_ORDER', 'search_scope':domain,
                    'authority':'NONE','instrument':'PENCIL'}
    return {'status':'HOLD','reason':'no single conjunction fits all development cases',
            'evaluated_this_slice':evaluated,'completeness':'COMPLETE_FOR_CONJUNCTION_GRAMMAR',
            'authority':'NONE'}


def guarded_from_data(data: dict) -> ConditionalRule:
    if not isinstance(data,dict) or set(data)!={'base','guard','scope','admission'} or data['admission']!='PENCIL_ONLY':
        raise ValueError('invalid PENCIL guard declaration')
    base=data['base']
    if not isinstance(base,dict) or set(base)!={'name','find','replace'} or not isinstance(base['find'],list) or not isinstance(base['replace'],list):
        raise ValueError('invalid base rewrite declaration')
    if not isinstance(data['guard'],dict) or any(not isinstance(k,str) or not isinstance(v,str)
                                                for k,v in data['guard'].items()):
        raise ValueError('guard must be a string mapping')
    return ConditionalRule(RewriteRule(base['name'],tuple(base['find']),tuple(base['replace'])),
                           tuple(sorted(data['guard'].items())),data['scope'])


def explore(seed: Sequence[str], target: Sequence[str], parent: RewriteGrammar,
            candidate: ConditionalRule | None, facts: Mapping[str,str], *, work_budget: int):
    """Read-only, finite, context-aware BFS of hypothetical graph futures.

    GEOM-009's LivingGraph cannot execute guarded rules; rather than bypass its
    immutable grammar fingerprint, this separate scratch explorer branches
    only in memory. No nodes or edges become historical assertions.
    """
    if candidate is not None and candidate.scope != parent.scope:
        raise ValueError('cross-scope graph fork refused')
    if type(work_budget) is not int or work_budget<=0:
        raise ValueError('positive graph work_budget required')
    before=tuple(seed);goal=tuple(target)
    if any(not isinstance(t,str) or not t.strip() for t in before+goal):
        raise ValueError('invalid graph tokens')
    if not isinstance(facts,Mapping) or any(not isinstance(k,str) or not isinstance(v,str)
                                           for k,v in facts.items()):
        raise ValueError('invalid context facts')
    seen={before};front=deque([(before, ())]); expanded=0; unknown_context=False
    if before==goal:
        return {'status':'PATH','steps':0,'expanded':0,'authority':'NONE'}
    while front and expanded<work_budget:
        tokens,path=front.popleft();expanded+=1
        applications=[]
        for r in parent.rules:
            applications.extend((r.name,output) for _,output in r.outcomes(tokens))
        if candidate is not None:
            required=dict(candidate.guard)
            matched=all(k in facts and facts[k]==v for k,v in required.items())
            if matched:
                applications.extend((candidate.base.name,output)
                                    for _,output in candidate.base.outcomes(tokens))
            elif any(k not in facts for k in required) and not any(
                    k in facts and facts[k]!=v for k,v in required.items()):
                if any(True for _ in candidate.base.outcomes(tokens)):
                    unknown_context=True
        for name,next_tokens in applications:
            if next_tokens not in seen:
                trace=path+(name,)
                if next_tokens==goal:
                    return {'status':'PATH','steps':len(trace),'rules':list(trace),
                            'expanded':expanded,'authority':'NONE'}
                seen.add(next_tokens);front.append((next_tokens,trace))
    return {'status':'HOLD_RESOURCE_INCOMPLETE' if front else
            'HOLD_UNKNOWN_CONTEXT' if unknown_context else 'SATURATED_NO_TARGET',
            'expanded':expanded,'seen':len(seen),'authority':'NONE'}


def archive_pencil(graph: LivingGraph, parent: RewriteGrammar,
                   initial: RewriteRule, feedback: Sequence[SituatedCase],
                   proposal: dict, *, work_budget: int=100000):
    """Recompute winner from supplied feedback; never trust external scores."""
    if graph.scope!=parent.scope:
        raise ValueError('archive scope mismatch')
    recomputed=invent_guard(initial,feedback,scope=parent.scope,work_budget=work_budget)
    if recomputed['status']!='PENCIL_GUARD_INVENTED' or proposal.get('rule')!=recomputed['rule'] \
       or proposal.get('development')!=recomputed['development'] \
       or proposal.get('status')!='PENCIL_GUARD_INVENTED' \
       or proposal.get('authority')!='NONE' or proposal.get('instrument')!='PENCIL':
        raise ValueError('forged / unsupported proposed grammar revision')
    data={'parent':parent.fingerprint,'candidate':recomputed['rule'],
          'feedback_digest':stable_id('feedback:',[c.data() for c in feedback]),
          'rule_status':'PENCIL_ONLY'}
    node=stable_id('conditional-revision:',data)
    graph.add_node(node,kind='conditional_reason_cartridge',label='guarded-'+initial.name,
                   payload=data,source_root='local:synthetic-reason-lab')
    participants=[('cartridge',node)]
    for c in feedback:
        cid=stable_id('conditional-feedback:',c.data())
        graph.add_node(cid,kind='conditional_feedback_case',label=c.identity,
                       payload=c.data(),source_root=c.source_root)
        participants.append(('feedback',cid))
    graph.add_relation('reasoning_cartridge_trace',participants,
                       source_root='local:synthetic-reason-lab',
                       note={'scope':graph.scope,'admission':'PENCIL_ONLY'})
    return {'status':'ARCHIVED_PENCIL_ONLY','node_id':node,'feedback_cases':len(feedback),
            'authority':'NONE'}


def stage(parent: RewriteGrammar, initial: RewriteRule, feedback: Sequence[SituatedCase],
          *, work_budget:int=10000, cursor=None, seconds:float | None=None,
          active: ConditionalRule | None=None):
    if active is not None and (active.scope!=parent.scope or active.base!=initial):
        raise ValueError('active revision must share original parent/scope')
    state=critic(active if active is not None else ConditionalRule(initial,(),parent.scope),feedback)
    if state['status']=='UNRESOLVABLE_IN_OBSERVED_VOCABULARY':
        return {'critic':state,'inventor':{'status':'HOLD','reason':'conflicting identical inputs','authority':'NONE'}}
    if state['status']=='DEVELOPMENT_FIT':
        return {'critic':state,'inventor':{'status':'HOLD','reason':'no demonstrated representational gap',
                                         'authority':'NONE'},'authority':'NONE'}
    new=invent_guard(initial,feedback,scope=parent.scope,work_budget=work_budget,
                     cursor=cursor,seconds=seconds)
    if new['status']=='PENCIL_GUARD_INVENTED':
        after=critic(guarded_from_data(new['rule']),feedback)
    else:
        after=None
    return {'critic':state,'inventor':new,'critic_after':after,
            'reviewed_active_guard':dict(active.guard) if active is not None else {},
            'authority':'NONE'}


def case_from_document(doc):
    allowed={'id','before','after','expected','facts','source_root','scope'}
    if not isinstance(doc,dict) or set(doc)!=allowed or not isinstance(doc['before'],list) or not isinstance(doc['after'],list):
        raise ValueError('invalid situated case declaration')
    return SituatedCase.make(doc['id'],doc['before'],doc['after'],doc['expected'],doc['facts'],
                             doc['source_root'],doc['scope'])


def run_document(doc):
    """Strict bounded local JSON interface. No code execution or outside actions."""
    from living_graph import grammar_from_document
    required={'parent_grammar','initial_rule','development','work_budget'}
    if not isinstance(doc,dict) or not required <= set(doc) or set(doc)-required-{'cursor','seconds'}:
        raise ValueError('unknown or missing lab field')
    parent=grammar_from_document(doc['parent_grammar'])
    base=doc['initial_rule']
    if not isinstance(base,dict) or set(base)!={'name','find','replace'} or not isinstance(base['find'],list) or not isinstance(base['replace'],list):
        raise ValueError('invalid initial rule')
    initial=RewriteRule(base['name'],tuple(base['find']),tuple(base['replace']))
    if any((r.find,r.replace)==(initial.find,initial.replace) for r in parent.rules):
        raise ValueError('initial rule is already in parent grammar')
    if not isinstance(doc['development'],list):
        raise ValueError('development must be an array')
    cases=[case_from_document(c) for c in doc['development']]
    return stage(parent,initial,cases,work_budget=doc['work_budget'],
                 cursor=doc.get('cursor'),seconds=doc.get('seconds'))
