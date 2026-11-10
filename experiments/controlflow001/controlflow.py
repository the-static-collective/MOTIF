"""CONTROL-FLOW-GROWTH-001: derive a deeper loop nest by recursive AST wrapping.

Finite program synthesis on synthetic simple graphs. The experiment starts with
OPERATOR-INVENTION-001's at-most-two-binder grammar, witnesses a finite failure
on five-cycle increments, and applies a generic FOR EACH binder rewrite to
extend the executable syntax tree by one level. A 3-loop path-counting program
is selected by interventions and checked on held-out graphs. The compiler and
search language are researcher-authored; this is NOT invention of an unknown
principle, arbitrary Python synthesis, real-world agency, or secure sandboxing.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from hashlib import sha256
from itertools import combinations, permutations, product
from math import log2
from pathlib import Path
from random import Random
from typing import Any
import ast
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
for directory in ('operatorinvention001','languagegrowth001','contractdiscovery001',
                  'contractfrontier002','mathal001','fir001'):
    if str(ROOT/directory) not in sys.path:
        sys.path.insert(0, str(ROOT/directory))
from operatorinvention import Program as OldProgram, PROGRAMS as OLD_PROGRAMS
from languagegrowth import Experiment, trials
from contractdiscovery import apply
from nunumathal import Graph


class FlowRefusal(ValueError):
    pass


# These primitives are *not* a prewritten 5-cycle or length-four-path routine.
# The unbounded-in-principle FOR rewrite is explicitly provided by the author;
# the experiment bounds depth to 3 to remain computationally inspectable.
SYMBOLS = ('a','b','x','y','z')
BINDERS = ('x','y','z')


@dataclass(frozen=True)
class Increment:
    pass


@dataclass(frozen=True)
class IfEdges:
    atoms: tuple[tuple[str,str],...]
    distinct_all: bool
    body: Increment


@dataclass(frozen=True)
class ForEach:
    binder: str
    body: Any


def tree_for(binders:tuple[str,...],atoms:tuple[tuple[str,str],...],distinct:bool):
    """Generic repeated wrapping: no 3-loop source template or fixed AST."""
    tree=IfEdges(atoms,distinct,Increment())
    for name in reversed(binders):
        tree=ForEach(name,tree)
    return tree


def _connected_tree(atoms:tuple[tuple[str,str], ...],names:tuple[str,...])->bool:
    reachable={'a'}
    while True:
        other=reachable | {v for u,v in atoms if u in reachable} | {u for u,v in atoms if v in reachable}
        if other == reachable:
            break
        reachable=other
    return len(reachable)==len(names)


def _canonical(atoms:tuple[tuple[str,str], ...],binders:tuple[str,...])->tuple[tuple[str,str],...]:
    """Alpha-equivalent programs must not masquerade as separate discoveries."""
    names=tuple(binders)
    options=[]
    for perm in permutations(names):
        rebind=dict(zip(names,perm))
        options.append(tuple(sorted(tuple(sorted((rebind.get(a,a),rebind.get(b,b)))) for a,b in atoms)))
    return min(options)


@dataclass(frozen=True)
class ControlProgram:
    binders:tuple[str,...]
    atoms:tuple[tuple[str,str],...]
    distinct_all:bool

    def __post_init__(self):
        names=('a','b')+self.binders
        allowed=set(combinations(names,2))
        if (not 1<=len(self.binders)<=3 or self.binders!=BINDERS[:len(self.binders)]
                or type(self.distinct_all) is not bool
                or len(self.atoms)!=len(self.binders)+1
                or self.atoms!=tuple(sorted(self.atoms))
                or len(set(self.atoms))!=len(self.atoms)
                or any(pair not in allowed for pair in self.atoms)
                or not _connected_tree(self.atoms,names)
                or self.atoms!=_canonical(self.atoms,self.binders)):
            raise FlowRefusal('HOLD_INVALID_CONTROL_AST')

    @property
    def loop_tree(self):
        return tree_for(self.binders,self.atoms,self.distinct_all)

    def signature(self)->str:
        return f'bind={self.binders}, atoms={self.atoms}, distinct={self.distinct_all}'

    def interpret(self,probe)->int:
        count=0
        g=probe.graph
        for args in product(sorted(g.vertices),repeat=len(self.binders)):
            if self.distinct_all and len(set((probe.a,probe.b)+args))!=len(self.binders)+2:
                continue
            env={'a':probe.a,'b':probe.b}
            env.update(zip(self.binders,args))
            if all(env[u]!=env[v] and tuple(sorted((env[u],env[v]))) in g.edges for u,v in self.atoms):
                count+=1
        return count

    def emit_source(self)->str:
        """Compile compositional AST nodes to real Python loops and IF, not eval.

        The generator is recursive for each ForEach node, regardless of depth.
        """
        lines=['def discovered_operation(graph, a, b):',
               "    if a == b or a not in graph.vertices or b not in graph.vertices:",
               "        raise ValueError('HOLD_INVALID_ENDPOINTS')",
               '    vertices = tuple(sorted(graph.vertices))',
               '    edges = graph.edges',
               '    count = 0']
        def emit(node,level):
            indent='    '*level
            if isinstance(node,ForEach):
                lines.append(indent+f'for {node.binder} in vertices:')
                emit(node.body,level+1)
            elif isinstance(node,IfEdges):
                conditions=[f'({u} != {v} and tuple(sorted(({u}, {v}))) in edges)' for u,v in node.atoms]
                if node.distinct_all:
                    variables=('a','b')+self.binders
                    conditions.insert(0,f'(len({{{", ".join(variables)}}}) == {len(variables)})')
                lines.append(indent+'if '+' and '.join(conditions)+':')
                emit(node.body,level+1)
            elif isinstance(node,Increment):
                lines.append(indent+'count += 1')
            else:
                raise FlowRefusal('HOLD_FOREIGN_AST_NODE')
        emit(self.loop_tree,1)
        lines.append('    return count')
        code='\n'.join(lines)+'\n'
        parsed=ast.parse(code)
        if len(parsed.body)!=1 or not isinstance(parsed.body[0],ast.FunctionDef):
            raise FlowRefusal('HOLD_BAD_EMITTED_AST')
        return code


def grammar(depth:int)->tuple[ControlProgram,...]:
    """Enumerate spanning-tree predicates by primitive undirected EDGE atoms.

    The target path topology is NOT enumerated as an explicit named operator.
    Other tree structures are included and tested against the outcome instrument.
    """
    if type(depth) is not int or not 1<=depth<=3:
        raise FlowRefusal('HOLD_DEPTH_OUTSIDE_EXPERIMENT')
    binders=BINDERS[:depth]
    symbols=('a','b')+binders
    edges=combinations(symbols,2)
    choices=set()
    for atoms in combinations(tuple(edges),depth+1):
        atoms=tuple(sorted(atoms))
        if not _connected_tree(atoms,symbols):
            continue
        canonical=_canonical(atoms,binders)
        for distinct in (False,True):
            choices.add(ControlProgram(binders,canonical,distinct))
    return tuple(sorted(choices,key=lambda x:(x.distinct_all,x.atoms)))


def cycle_count(g:Graph,size:int=5)->int:
    """Independent outcome instrument enumerates vertex cycles, not paths.

    Each undirected cycle appears once (rotate to least vertex; reverse canonical).
    """
    if size!=5:
        raise FlowRefusal('HOLD_ONLY_FIVE_CYCLE_INSTRUMENT')
    count=0
    for selected in combinations(sorted(g.vertices),size):
        start=selected[0]
        for rest in permutations(selected[1:]):
            if rest[0]>rest[-1]:
                continue
            order=(start,)+rest
            if all(tuple(sorted((order[i],order[(i+1)%size]))) in g.edges for i in range(size)):
                count+=1
    return count


def outcome(case:Experiment)->int:
    return cycle_count(apply(case.probe.trial()))-cycle_count(case.probe.graph)


def strong_baseline(probe)->int:
    """Independent classical DFS counts simple 4-edge paths, not 5-cycle oracle."""
    graph=probe.graph
    near={v:set() for v in graph.vertices}
    for a,b in graph.edges:
        near[a].add(b)
        near[b].add(a)
    count=0
    def visit(vertex,seen,remaining):
        nonlocal count
        if remaining==0:
            if vertex==probe.b:
                count+=1
            return
        for nxt in near[vertex]-seen:
            if nxt==probe.b and remaining!=1:
                continue
            visit(nxt,seen|{nxt},remaining-1)
    visit(probe.a,{probe.a},4)
    return count


def _row_signatures(case:Experiment, candidates:tuple[ControlProgram,...]):
    """Cache edge masks for 3-binder programs; no oracle outcome reads."""
    graph=case.probe.graph
    names=('a','b')+BINDERS
    all_edges=tuple(combinations(names,2))
    positions={edge:i for i,edge in enumerate(all_edges)}
    masks=[sum(1<<positions[edge] for edge in program.atoms) for program in candidates]
    vertices=tuple(sorted(graph.vertices))
    all_masks=[]
    distinct_masks=[]
    for values in product(vertices,repeat=3):
        env={'a':case.probe.a,'b':case.probe.b,'x':values[0],'y':values[1],'z':values[2]}
        flags=0
        for index,(a,b) in enumerate(all_edges):
            if env[a]!=env[b] and tuple(sorted((env[a],env[b]))) in graph.edges:
                flags|=1<<index
        all_masks.append(flags)
        if len(set((case.probe.a,case.probe.b)+values))==5:
            distinct_masks.append(flags)
    hist_all=Counter(all_masks)
    hist_distinct=Counter(distinct_masks)
    result=[]
    for mask, program in zip(masks,candidates):
        hist=hist_distinct if program.distinct_all else hist_all
        result.append(sum(quantity for present,quantity in hist.items() if present & mask==mask))
    return tuple(result)


def _key(records)->str:
    return sha256(json.dumps(tuple(records),sort_keys=True,default=str).encode()).hexdigest()[:24]


def _entropy(numbers)->float:
    tally=Counter(numbers)
    total=sum(tally.values())
    return -sum((value/total)*log2(value/total) for value in tally.values()) if total else 0.0


@dataclass(frozen=True)
class Discovery:
    status:str
    program:ControlProgram|None
    probes:int
    total_candidates:int
    remaining:int
    training_digest:str
    validation_digest:str
    receipts:tuple[dict,...]

    @property
    def usable(self):
        return self.status=='I_EXTENDED_LOOP_AST_VALIDATED' and self.program is not None


def diagnose(cases:tuple[Experiment,...],budget:int=12)->dict:
    """Actually try old 62-program grammar before proposing a new control node."""
    if not cases or type(budget) is not int or not 1<=budget<=len(cases):
        raise FlowRefusal('HOLD_DIAGNOSTIC_BUDGET')
    remaining=tuple(OLD_PROGRAMS)
    receipts=[]
    for case in cases[:budget]:
        prediction=[x.interpret(case.probe) for x in remaining]
        truth=outcome(case)
        before=len(remaining)
        remaining=tuple(x for x,y in zip(remaining,prediction) if y==truth)
        receipts.append({'probe':case.key,'models_before':before,'models_after':len(remaining),
                         'observed':truth,'real_world_actions':0})
        if not remaining:break
    return {'status':'HOLD_OLD_CONTROL_GRAMMAR_FALSIFIED' if not remaining else 'I_MORE_EVIDENCE_NEEDED',
            'inspected':len(receipts),'remaining':len(remaining),'receipts':tuple(receipts),
            'old_grammar_count':len(OLD_PROGRAMS),'model_limit':'finite, synthetic only'}


def discover(train:tuple[Experiment,...],validation:tuple[Experiment,...],*,
             max_depth:int=3,budget:int=12,selection:str='active',seed:int=7,
             allow_distinct:bool=True)->Discovery:
    """One generic ForEach rewrite grows a failed language; test frozen results.

    No validation or held-out labels enter selection. The train candidate pool
    is inspected at input-only level. It may select models on train probes, then
    must pass all validation probes unchanged.
    """
    if (type(max_depth) is not int or not 1<=max_depth<=3 or type(budget) is not int
            or budget<3 or budget>len(train) or not validation
            or selection not in {'active','random'} or type(allow_distinct) is not bool
            or len({x.key for x in train})!=len(train)
            or len({x.key for x in validation})!=len(validation)
            or set(x.key for x in train)&set(x.key for x in validation)):
        raise FlowRefusal('HOLD_DISCOVERY_CONTRACT')
    diagnosis=diagnose(train)
    receipt=[{'step':'diagnose-existing-control-flow','outcome':diagnosis['status'],
              'old_grammar_count':diagnosis['old_grammar_count']}]
    if diagnosis['status']!='HOLD_OLD_CONTROL_GRAMMAR_FALSIFIED':
        return Discovery('HOLD_NOT_YET_A_CONTROL_FLOW_GAP',None,diagnosis['inspected'],
                         len(OLD_PROGRAMS),diagnosis['remaining'],'','',tuple(receipt))
    if max_depth < 3:
        return Discovery('HOLD_MAX_LOOP_DEPTH_BELOW_NEEDED',None,diagnosis['inspected'],
                         len(OLD_PROGRAMS),diagnosis['remaining'],'', '',tuple(receipt))
    candidates=tuple(p for p in grammar(3) if allow_distinct or not p.distinct_all)
    cache={e.key:_row_signatures(e,candidates) for e in train}
    surviving=set(range(len(candidates)))
    rng=Random(seed)
    observed=[]
    available=list(train)
    for i in range(budget):
        if selection=='active':
            case=min(available,key=lambda e:(-_entropy(cache[e.key][j] for j in surviving),e.key))
        else:
            case=rng.choice(available)
        available.remove(case)
        true=outcome(case)   # First target access, *after* choosing experiment
        before=len(surviving)
        surviving={j for j in surviving if cache[case.key][j]==true}
        observed.append((case.key,true))
        receipt.append({'action':'RUN_SYNTHETIC_INTERVENTION','case':case.key,'outcome':true,
                        'survivors_before':before,'survivors_after':len(surviving),
                        'external_actions':0})
        if not surviving:
            return Discovery('HOLD_NO_COMPOSABLE_PROGRAM',None,len(observed),len(candidates),0,
                             _key(observed),'',tuple(receipt))
        # Residual aliases are not evidence of unique syntax. Stop only if all
        # remaining train input worlds make the same predictions.
        if i>=2 and all(len({cache[e.key][j] for j in surviving})==1 for e in available):
            break
    if len(observed)<3:
        return Discovery('HOLD_TOO_FEW_INTERVENTIONS',None,len(observed),len(candidates),len(surviving),
                         _key(observed),'',tuple(receipt))
    # canonical lexical minimum after alpha-equivalence, simplicity of no guard
    # preferred when evidence permits. Neither implies proof of global identity.
    winner=candidates[min(surviving,key=lambda j:(candidates[j].distinct_all,candidates[j].atoms))]
    checked=[]
    for e in validation:
        measured=outcome(e)
        checked.append((e.key,measured))
        if winner.interpret(e.probe)!=measured:
            return Discovery('HOLD_VALIDATION_COUNTEREXAMPLE',None,len(observed),len(candidates),
                             len(surviving),_key(observed),_key(checked),tuple(receipt))
    receipt.append({'action':'VALIDATE_FROZEN_RECURSIVE_PROGRAM','tested':len(checked),
                    'validation_digest':_key(checked),'epistemic_role':'F_LOCAL_REPLAY'})
    return Discovery('I_EXTENDED_LOOP_AST_VALIDATED',winner,len(observed),len(candidates),
                     len(surviving),_key(observed),_key(checked),tuple(receipt))


def audit(d:Discovery,cases:tuple[Experiment,...])->dict:
    if not d.usable or not cases:
        return {'status':'HOLD_UNVERIFIED_OR_EMPTY'}
    correct=0;classical=0;code_correct=0
    namespace={}
    compiled=d.program.emit_source()
    exec(compile(compiled,'<generated_controlflow>','exec'),{'__builtins__':{'tuple':tuple,'sorted':sorted,'len':len}},namespace)
    child=namespace['discovered_operation']
    for e in cases:
        y=outcome(e)
        correct+=d.program.interpret(e.probe)==y
        classical+=strong_baseline(e.probe)==y
        code_correct+=child(e.probe.graph,e.probe.a,e.probe.b)==y
    return {'cases':len(cases),'AST_correct':correct,'emitted_code_correct':code_correct,
            'strong_classical_correct':classical,'status':'F_LOCAL_FINITE_REPLAY'
                    if correct==classical==code_correct==len(cases) else 'HOLD_COUNTEREXAMPLE',
            'unrestricted_algorithm_claim':False}


PINS=('mathal001/nunumathal.py','contractdiscovery001/contractdiscovery.py',
      'contractfrontier002/contractfrontier.py','featurefrontier001/featurefrontier.py',
      'languagegrowth001/languagegrowth.py','operatorinvention001/operatorinvention.py',
      'controlflow001/controlflow.py','fir001/fir.py')


def pins(root:Path=ROOT)->tuple[tuple[str,str],...]:
    root=Path(root).resolve(strict=True)
    hashes=[]
    for rel in PINS:
        f=root/rel
        if not f.is_file() or f.is_symlink() or not f.resolve().is_relative_to(root):
            raise FlowRefusal('HOLD_SOURCE_DRIFT_OR_LINK:'+rel)
        hashes.append((rel,sha256(f.read_bytes()).hexdigest()))
    return tuple(hashes)


CHILD='''"""Generated executable loop-depth-3 child for synthetic five-cycle task."""
from pathlib import Path
from hashlib import sha256
import argparse,sys,json
parser=argparse.ArgumentParser()
parser.add_argument('--source-root',required=True)
parser.add_argument('--index',type=int,default=0)
a=parser.parse_args()
root=Path(a.source_root).resolve(strict=True)
for rel,digest in json.loads(__PINNED__):
    f=root/rel
    if not f.is_file() or f.is_symlink() or sha256(f.read_bytes()).hexdigest()!=digest:
        print(json.dumps({'status':'HOLD_SOURCE_DRIFT','source':rel}));sys.exit(0)
sys.path.insert(0,str(root/'controlflow001'))
from controlflow import outcome, strong_baseline
from languagegrowth import trials
__GENERATED_FUNCTION__
checks=trials('test',24)
if a.index<0 or a.index>=len(checks):
    print(json.dumps({'status':'HOLD_INVALID_TEST_INDEX'}));sys.exit(0)
case=checks[a.index]
y=outcome(case)
answer=discovered_operation(case.probe.graph,case.probe.a,case.probe.b)
other=strong_baseline(case.probe)
print(json.dumps({'status':'F_LOCAL_CHILD_REPLAY' if answer==y==other else 'HOLD_COUNTEREXAMPLE',
                  'observed':y,'computed':answer,'strong_classical':other,
                  'external_actions':0,'original_source_edits':0},sort_keys=True))
'''


def build_child(root:Path,destination:Path,d:Discovery)->Path:
    if not d.usable:
        raise FlowRefusal('HOLD_UNVERIFIED_CHILD_SOURCE')
    frozen=discover(trials('train',36),trials('validation',24))
    if (d.program!=frozen.program or d.training_digest!=frozen.training_digest
            or d.validation_digest!=frozen.validation_digest):
        raise FlowRefusal('HOLD_CANNOT_ATTEST_FROZEN_PROGRAM')
    checks=pins(root)
    destination=Path(destination)
    destination.mkdir(parents=True,exist_ok=True)
    child=destination/'grown_controlflow.py'
    digest=destination/'grown_controlflow.sha256'
    if any(x.exists() or x.is_symlink() for x in (child,digest)):
        raise FileExistsError('HOLD_REFUSE_OVERWRITE')
    source=CHILD.replace('__PINNED__',repr(json.dumps(checks)))
    source=source.replace('__GENERATED_FUNCTION__',d.program.emit_source())
    ast.parse(source)
    child.write_text(source,encoding='utf8')
    digest.write_text(sha256(child.read_bytes()).hexdigest()+'\n')
    return child


def run_child(child:Path,root:Path,index:int=0)->dict:
    child=Path(child);receipt=child.with_suffix('.sha256')
    if (not child.is_file() or child.is_symlink()
            or not receipt.is_file() or receipt.is_symlink()
            or receipt.read_text().strip()!=sha256(child.read_bytes()).hexdigest()):
        return {'status':'HOLD_MISSING_OR_TAMPERED_CHILD'}
    try:
        process=subprocess.run([sys.executable,str(child),'--source-root',str(root),'--index',str(index)],
                               cwd=child.parent,capture_output=True,text=True,timeout=30)
    except subprocess.TimeoutExpired:
        return {'status':'HOLD_CHILD_TIMEOUT'}
    if process.returncode:
        return {'status':'HOLD_CHILD_PROCESS_ERROR','stderr':process.stderr[-400:]}
    try:
        return json.loads(process.stdout)
    except ValueError:
        return {'status':'HOLD_CHILD_NON_JSON'}


def demonstration()->dict:
    import tempfile
    train=trials('train',36);validation=trials('validation',24)
    diagnostic=diagnose(train)
    found=discover(train,validation)
    test=audit(found,trials('test',24))
    ood=audit(found,trials('ood',20))
    with tempfile.TemporaryDirectory(prefix='motif-controlflow-') as folder:
        child=build_child(ROOT,Path(folder),found)
        child_result=run_child(child,ROOT,index=4)
    return {'experiment':'CONTROL-FLOW-GROWTH-001','starting_grammar':diagnostic,
            'expanded_grammar_size':found.total_candidates,
            'learned_AST':found.program.signature() if found.program else None,
            'generated_source':found.program.emit_source() if found.program else None,
            'active_probes':found.probes,'validation_status':found.status,
            'test':test,'ood':ood,'child':child_result,
            'source_not_self_modified':True,'real_world_actions':0,
            'historical_novelty_claim':False,
            'next_question':'Can MOTIF diagnose a genuine new computation need, rather than a missing loop depth, and validate a less prespecified AST rewrite?'}


if __name__=='__main__':
    print(json.dumps(demonstration(),indent=2,sort_keys=True))
