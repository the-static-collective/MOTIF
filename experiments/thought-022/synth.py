"""THOUGHT-022: finite typed grammar synthesizer, independent target evaluator.

Candidate semantics come from source-owned MOTIF-017 set interpreter.
Target truth comes from separate integer bitmask spec. The oracle never
imports the candidate interpreter. No generated Python or code from an LLM
is executed, and no patch is installed.
"""
from __future__ import annotations
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
for name in ('thought-017','thought-018'):
    sibling=str(HERE.parent/name)
    if sibling not in sys.path:sys.path.insert(0,sibling)
from program import validate_expr,op,r,digest
from director import candidate_mask

BITS=7
SCHEMA='motif.thought022.classical-cegis.v1'


def independent_oracle(task, a, b):
    """Evaluator-owned semantics expressed with integer bit logic only."""
    if task not in ('flip','intersection','drain','replace','invert'):
        raise ValueError('invalid evaluator task')
    if any(type(z) is not int or not 0<=z<=7 for z in (a,b)):
        raise ValueError('invalid masks')
    return {'flip':lambda:a^b,'intersection':lambda:a&b,
            'drain':lambda:a&(~b&7), 'replace':lambda:b,
            'invert':lambda:(~a)&7}[task]()

TASKS={
  'flip': 'Each switch named by the event reverses its ON/OFF status; unnamed switches retain their previous status.',
  'intersection': 'Keep ON exactly those switches that were ON before and also are marked by this event. All other switches are OFF.',
  'drain': 'An event turns OFF every switch it names; switches it does not name keep their former state.',
  'replace': 'Discard prior switch states. The event names exactly those switches that will now be ON.',
  'invert': 'Reverse the ON/OFF state of every switch, even those not named by this event. The event names do not matter.',
}


def signature(expr):
    """Finite semantic fingerprint; absence of a pair cannot be treated as evidence."""
    validate_expr(expr)
    return tuple(candidate_mask(expr,a,b) for a in range(8) for b in range(8))


def _node_count(expr):
    return 1 if 'ref' in expr else 1+sum(_node_count(x) for x in expr['args'])


def enumerate_semantics(max_depth=4):
    """Enumerate *all distinct expressible 3-bit transition functions* by closure.

    These two atom operands and two binary set operators generate a finite
    algebra of bitwise functions. Dedup by exact full-domain output, retaining
    smallest source expression. Explicit fixed point proves grammar closure;
    it does not prove language-model creativity or general programming ability.
    """
    if type(max_depth) is not int or not 1<=max_depth<=4:raise ValueError('depth 1..4')
    entries={}
    for expr in (r('state.on'),r('arrival.toggles')):
        entries[signature(expr)]=(expr,0)
    levels=[[] for _ in range(max_depth+1)]
    levels[0]=[(ex,0) for ex,_ in entries.values()]
    old_count=-1
    for depth in range(1,max_depth+1):
        existing=list(entries.values())
        for left,dl in existing:
            for right,dr in existing:
                if max(dl,dr)+1!=depth:continue
                for operator in ('union','difference'):
                    expr=op(operator,left,right)
                    if _node_count(expr)>19:continue
                    key=signature(expr)
                    if key not in entries:
                        entries[key]=(expr,depth)
                        levels[depth].append((expr,depth))
    ordered=sorted(entries.items(),key=lambda item:(_node_count(item[1][0]),str(item[1][0])))
    return [{'id':'candidate:'+digest(key)[:16], 'expression':expr,
             'depth':depth,'nodes':_node_count(expr), 'signature':key}
            for key,(expr,depth) in ordered]


def choose_probe(candidates,seen):
    """Look only at competing candidate predictions, never the target answer."""
    if not candidates: return None
    best=None;best_key=None
    for a in range(8):
        for b in range(8):
            if (a,b) in seen:continue
            counts=Counter(c['signature'][a*8+b] for c in candidates)
            information=len(candidates)**2-sum(z*z for z in counts.values())
            # Deterministically prefer informative overlaps and balanced inputs.
            key=(information,len(counts),int(a & b != 0),-a,-b)
            if best_key is None or key>best_key:
                best=(a,b);best_key=key
    return best if best_key and best_key[0]>0 else None


def counterexample_to_current(task,candidates,seen):
    """If predictions agree everywhere, no further source-based probe can help."""
    if (0,0) not in seen:
        return (0,0),'OUT_OF_VOCABULARY_COVERAGE_GUARD'
    probe=choose_probe(candidates,seen)
    if probe is not None:return probe,'MAX_DISAGREEMENT'
    for a in range(8):
        for b in range(8):
            if (a,b) not in seen:return (a,b),'GRAMMAR_COVERAGE_TEST'
    return None,'EXHAUSTED'


def _record(task,probes,active,mode,status,candidate=None):
    report={'schema':SCHEMA,'task':task,'mode':mode,'status':status,
            'oracle_calls':len(probes),'development_witnesses':list(probes),
            'remaining_consistent_semantics':len(active),
            'candidate_expression':candidate['expression'] if candidate else None,
            'candidate_nodes':candidate['nodes'] if candidate else None,
            'frozen_full_domain_passed':None,
            'installed':False,'pen_status':'UNCHANGED','external_authority':'NONE'}
    if candidate is not None:
        report['frozen_full_domain_passed']=sum(candidate['signature'][a*8+b]==
                   independent_oracle(task,a,b) for a in range(8) for b in range(8))
    report['receipt_digest']=digest(report)
    return report


def classical_cegis(task, *, oracle_budget=4, catalog=None):
    if task not in TASKS or type(oracle_budget) is not int or not 1<=oracle_budget<=8:
        raise ValueError('invalid synthesis task or budget')
    catalog=enumerate_semantics() if catalog is None else catalog
    active=list(catalog);probes=[];seen=set()
    for _ in range(oracle_budget):
        if len(active)==1:break
        probe,selection=counterexample_to_current(task,active,seen)
        if probe is None:break
        a,b=probe
        actual=independent_oracle(task,a,b)
        old_count=len(active)
        active=[c for c in active if c['signature'][a*8+b]==actual]
        probes.append({'on_mask':a,'toggle_mask':b,'observed_mask':actual,
                       'eliminated_count':old_count-len(active),'selection':selection,
                       'observation':'DEV_ONLY_ORACLE_BITMASK'})
        seen.add(probe)
        if not active:
            return _record(task,probes,active,'classical','HOLD_GRAMMAR_INADEQUATE')
    if len(active)!=1:
        return _record(task,probes,active,'classical','HOLD_AMBIGUOUS_WITHIN_PROBE_BUDGET')
    candidate=active[0]
    result=_record(task,probes,active,'classical','REVIEW_CANDIDATE_NOT_INSTALLED',candidate)
    if result['frozen_full_domain_passed']!=64:
        result['status']='HOLD_FROZEN_EVALUATION_FAILED'
        result['receipt_digest']=digest({k:v for k,v in result.items() if k!='receipt_digest'})
    return result
