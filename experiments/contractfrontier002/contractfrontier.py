"""CONTRACT-FRONTIER-002: active discovery of conditional, topology-dependent laws.

This is an explicit, finite hypothesis language over synthetic simple graphs.
The learner does not receive the target laws or outcome labels in advance. It
selects permitted edge-addition interventions by hypothesis disagreement, reads
actual graph consequences, then builds a typed, read-only adapter from surviving
hypotheses. This does NOT discover arbitrary graph invariants or establish
scientific novelty; source features and search grammar are developer-declared.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from hashlib import sha256
from itertools import combinations
from math import log2
from pathlib import Path
from random import Random
from typing import Iterable
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'mathal001'))
sys.path.insert(0, str(ROOT/'contractdiscovery001'))
sys.path.insert(0, str(ROOT/'fir001'))
from nunumathal import Graph, statistics
from contractdiscovery import Trial, apply, independent_statistics
from fir import FIRWorld, Claim, Warrant


class FrontierRefusal(ValueError):
    pass


@dataclass(frozen=True)
class Probe:
    key: str
    graph: Graph
    a: str
    b: str
    split: str

    def __post_init__(self):
        if not self.key or self.split not in {'train','validation','test','ood'}:
            raise FrontierRefusal('HOLD_PROBE_IDENTITY')
        if (self.a == self.b or self.a not in self.graph.vertices
                or self.b not in self.graph.vertices
                or tuple(sorted((self.a,self.b))) in self.graph.edges):
            raise FrontierRefusal('HOLD_EDGE_ALREADY_PRESENT_OR_INVALID')

    def trial(self) -> Trial:
        return Trial(self.key,self.graph,'add_edge',(self.a,self.b))


def adjacent(graph: Graph, vertex: str) -> frozenset[str]:
    return frozenset(y if x == vertex else x for x,y in graph.edges if vertex in (x,y))


def connected(graph: Graph, a: str, b: str) -> bool:
    frontier={a}; seen={a}
    while frontier:
        if b in frontier:
            return True
        nxt=set()
        for v in frontier:
            nxt.update(adjacent(graph,v)-seen)
        seen|=nxt;frontier=nxt
    return False


def count_triangles(graph: Graph) -> int:
    """Outcome instrument: enumerate unordered triples; never use wedge shortcut."""
    return sum(all(tuple(sorted(edge)) in graph.edges for edge in combinations(triple,2))
               for triple in combinations(sorted(graph.vertices),3))


def alternate_triangles(graph: Graph) -> int:
    """Independent adjacency enumeration for held-out oracle cross-check."""
    neigh={v:adjacent(graph,v) for v in graph.vertices}
    return sum(len(neigh[a]&neigh[b]) for a,b in graph.edges)//3


FEATURES=('one','degree_a','degree_b','sum_degrees','product_degrees',
          'common_neighbors','connected','vertices','edges','isolates',
          'triangles_before','twohop_a')


def features(probe: Probe) -> dict[str,int]:
    graph=probe.graph
    na,nb=adjacent(graph,probe.a),adjacent(graph,probe.b)
    near=set().union(*(adjacent(graph,v) for v in na)) if na else set()
    return {'one':1,'degree_a':len(na),'degree_b':len(nb),
            'sum_degrees':len(na)+len(nb),'product_degrees':len(na)*len(nb),
            'common_neighbors':len(na&nb), 'connected':int(connected(graph,probe.a,probe.b)),
            'vertices':len(graph.vertices),'edges':len(graph.edges),
            'isolates':graph.isolates(),'triangles_before':count_triangles(graph),
            'twohop_a':len(near-{probe.a})}


def observed_outcome(probe: Probe) -> tuple[int,int]:
    """Black-box graph transition readout. No expected expression hardcoded."""
    result=apply(probe.trial())  # real existing contractdiscovery001 implementation
    return count_triangles(result)-count_triangles(probe.graph), result.components()-probe.graph.components()


@dataclass(frozen=True)
class Expr:
    """Integer coefficients on at most 2 developer-supplied graph features."""
    terms: tuple[tuple[str,int], ...]

    def __post_init__(self):
        if (len(self.terms)>2 or len({x for x,_ in self.terms})!=len(self.terms)
                or any(name not in FEATURES or coefficient not in (-2,-1,1,2)
                       for name,coefficient in self.terms)
                or self.terms!=tuple(sorted(self.terms))):
            raise FrontierRefusal('HOLD_EXPRESSION_GRAMMAR')

    def __call__(self, row: dict[str,int]) -> int:
        return sum(row[name]*coefficient for name,coefficient in self.terms)

    @property
    def complexity(self):
        return (len(self.terms),sum(abs(c) for _,c in self.terms))

    def text(self):
        return ' + '.join(f'{c}*{name}' for name,c in self.terms) or '0'


def grammar() -> tuple[Expr,...]:
    programs={Expr(())}
    for feature in FEATURES:
        for c in (-2,-1,1,2):
            programs.add(Expr(((feature,c),)))
    for a,b in combinations(FEATURES,2):
        for c,d in ((-1,-1),(-1,1),(1,-1),(1,1)):
            programs.add(Expr(tuple(sorted(((a,c),(b,d))))))
    return tuple(sorted(programs,key=lambda x:(x.complexity,x.terms)))

PROGRAMS=grammar()


def _graphs(split: str, count: int) -> tuple[Probe,...]:
    """Deterministic split-specific graph interventions, no shared graph IDs.

    OOD uses larger graphs and adversarial topology families. The selection
    process only gets graph pre-states and action ports, not oracle outcomes.
    """
    if split not in {'train','validation','test','ood'} or count<1:
        raise FrontierRefusal('HOLD_BAD_SPLIT')
    rng=Random(int.from_bytes(sha256(f'contractfrontier002:{split}:v2'.encode()).digest()[:8],'big'))
    result=[]
    for i in range(count):
        n=rng.randint(5,9) if split!='ood' else rng.randint(11,18)
        names=[f'{split}_{i}_v{k}' for k in range(n)]
        mode=i%5
        if mode==0:  # sparse independent edges
            chance=.14 if split!='ood' else .08
        elif mode==1:
            chance=.3 if split!='ood' else .2
        elif mode==2:
            chance=.65 if split!='ood' else .6
        elif mode==3:  # two communities; sometimes cross-component edge
            chance=.38 if split!='ood' else .5
        else: # systematic star/path patterns
            chance=.06
        pairs=list(combinations(names,2))
        edges=set()
        for u,v in pairs:
            if mode==3 and ((names.index(u)<n//2)!=(names.index(v)<n//2)):
                continue
            if mode==4:
                k=names.index(u); j=names.index(v)
                if j==k+1 or (i%2==0 and k==0 and j>=2):
                    edges.add((u,v))
            elif rng.random()<chance:
                edges.add((u,v))
        missing=[pair for pair in pairs if pair not in edges]
        if not missing:
            edges.remove(pairs[0]);missing=[pairs[0]]
        # Alternate deliberate connected/disconnected probes, where available.
        graph=Graph.build(names,edges)
        connected_candidates=[(a,b) for a,b in missing if connected(graph,a,b)]
        disconnected_candidates=[(a,b) for a,b in missing if not connected(graph,a,b)]
        requested=connected_candidates if i%2 else disconnected_candidates
        selected=rng.choice(requested if requested else missing)
        result.append(Probe(f'{split}:{i}',graph,*selected,split))
    return tuple(result)


def _histogram(models: tuple[Expr,...], row: dict[str,int]) -> dict[int,int]:
    return dict(Counter(model(row) for model in models))


def entropy(hist: dict[int,int]) -> float:
    n=sum(hist.values())
    return -sum((c/n)*log2(c/n) for c in hist.values()) if n else 0.0


def choose_probe(pool: tuple[Probe,...], target_models: tuple[tuple[Expr,...],...]) -> Probe:
    """Information gain in version-space approximation, no target labels read."""
    if not pool:
        raise FrontierRefusal('HOLD_EMPTY_CANDIDATE_POOL')
    best=None
    for probe in pool:
        row=features(probe)
        score=sum(entropy(_histogram(models,row)) for models in target_models)
        # Stable lexicographic tie-break; never peek at actual outcomes.
        candidate=(-score,probe.key,probe)
        if best is None or candidate[:2]<best[:2]:
            best=candidate
    return best[2]


@dataclass(frozen=True)
class Discovery:
    triangle: Expr|None
    components: Expr|None
    inspected: int
    train_digest: str
    validation_digest: str
    status: str
    receipts: tuple[dict,...]
    remaining: tuple[int,int]

    @property
    def usable(self) -> bool:
        return self.status=='I_FINITE_CONTRACTS_VALIDATED' and self.triangle is not None and self.components is not None


def digest(observations: Iterable[tuple[str,tuple[int,int]]]) -> str:
    return sha256(json.dumps(list(observations),separators=(',',':')).encode()).hexdigest()[:20]


def discover(train: tuple[Probe,...], validation: tuple[Probe,...], *, budget: int=12,
             programs: tuple[Expr,...]=PROGRAMS, selection: str='active', seed:int=7) -> Discovery:
    """Train-only intervention selection. Validation read only after freeze.

    No terminal oracle outcome access until probe chosen. Exact version-space
    filtering is classical, finite and inspectable. The result remains I.
    """
    if (not 1<=budget<=len(train) or not validation or selection not in {'active','random'}
            or len({x.key for x in train})!=len(train)
            or len({x.key for x in validation})!=len(validation)
            or {x.key for x in train}&{x.key for x in validation}
            or not programs or any(not isinstance(p,Expr) for p in programs)):
        raise FrontierRefusal('HOLD_BAD_DISCOVERY_CONTRACT')
    remaining=list(train)
    versions=[tuple(programs),tuple(programs)]
    observations=[];receipts=[]
    rng=Random(seed)
    for step in range(budget):
        if len(versions[0])==len(versions[1])==1:
            break
        chosen=choose_probe(tuple(remaining),tuple(versions)) if selection=='active' else rng.choice(remaining)
        remaining.remove(chosen)
        # This is the only call to the training outcome instrument.
        result=observed_outcome(chosen)
        row=features(chosen)
        before=tuple(len(x) for x in versions)
        versions=[tuple(p for p in programs_for_target if p(row)==target)
                  for programs_for_target,target in zip(versions,result)]
        observations.append((chosen.key,result))
        receipts.append({'question':'Which permitted graph experiment most separates the remaining explanations?',
                         'action':'EXECUTE_ADD_EDGE', 'probe':chosen.key,
                         'models_before':before, 'observed':result,
                         'models_after':tuple(len(x) for x in versions),
                         'selection':selection,'external_actions':0})
        if not all(versions):
            return Discovery(None,None,len(observations),digest(observations),'',
                             'HOLD_NO_SUPPORTED_HYPOTHESIS',tuple(receipts),tuple(len(x) for x in versions))
    if len(versions[0])!=1 or len(versions[1])!=1:
        return Discovery(None,None,len(observations),digest(observations),'',
                         'HOLD_UNIDENTIFIABLE_AT_BUDGET',tuple(receipts),tuple(len(x) for x in versions))
    laws=(versions[0][0],versions[1][0])
    validation_results=[]
    for p in validation:
        actual=observed_outcome(p)
        validation_results.append((p.key,actual))
        row=features(p)
        if (laws[0](row),laws[1](row))!=actual:
            return Discovery(None,None,len(observations),digest(observations),
                digest(validation_results),'HOLD_VALIDATION_COUNTEREXAMPLE',tuple(receipts), (1,1))
    receipts.append({'question':'Do both frozen conditional/topological predictions survive independent graph worlds?',
                     'action':'VALIDATE_EXACT_OUTCOMES','cases':len(validation_results),
                     'digest':digest(validation_results),'status':'F_LOCAL_REPLAY'})
    return Discovery(*laws,len(observations),digest(observations),digest(validation_results),
                     'I_FINITE_CONTRACTS_VALIDATED',tuple(receipts), (1,1))


def infer(discovery: Discovery, probe: Probe) -> dict:
    """Execute an inferred port mapping with no outcome-instrument read."""
    if not discovery.usable:
        raise FrontierRefusal('HOLD_NO_VALIDATED_CONTRACT')
    row=features(probe)
    return {'delta_triangles':discovery.triangle(row),
            'delta_components':discovery.components(row),
            'status':'I_MODEL_PREDICTION','train_digest':discovery.train_digest,
            'external_actions':0}


def audit(discovery: Discovery, tests: tuple[Probe,...]) -> dict:
    if not discovery.usable or not tests:
        return {'status':'HOLD_NO_MODEL_OR_TEST'}
    good=0;recomputed=0; witnessed=[]
    for probe in tests:
        answer=infer(discovery,probe)
        measured=observed_outcome(probe)
        changed=apply(probe.trial())
        independent=(alternate_triangles(changed)-alternate_triangles(probe.graph),
                     independent_statistics(changed)[2]-independent_statistics(probe.graph)[2])
        recomputed += independent==measured
        good += (answer['delta_triangles'],answer['delta_components'])==measured
        witnessed.append((probe.key,measured))
    return {'cases':len(tests),'correct':good,'instrument_crosscheck':recomputed,
            'digest':digest(witnessed),'status':'F_LOCAL_EXACT_TEST' if good==recomputed==len(tests)
                     else 'HOLD_HIDDEN_REGRESSION','generalization_proved':False}


def sabotage_readout(discovery: Discovery, probe: Probe) -> dict:
    """Hostile source: type-correct outcome tampering is detectable if tested."""
    predicted=infer(discovery,probe)
    measured=observed_outcome(probe)
    fake=(measured[0]+1,measured[1])
    return {'original':measured,'tampered':fake,'detected_on_independent_replay':
            (predicted['delta_triangles'],predicted['delta_components'])!=fake,
            'source_authenticity_verified':False}


def coarse_counterexample() -> dict:
    """Identical coarse V/E/C/I/beta and endpoint degrees, different triangle effect."""
    vertices=set('abcdef')
    one=Graph.build(vertices,[('a','c'),('b','c'),('d','e'),('e','f')])
    two=Graph.build(vertices,[('a','c'),('c','d'),('d','b'),('e','f')])
    pa,pb=Probe('test:coarse1',one,'a','b','test'),Probe('test:coarse2',two,'a','b','test')
    return {'equal_coarse_statistics':statistics(one)==statistics(two),
            'equal_endpoint_degrees':(len(adjacent(one,'a')),len(adjacent(one,'b')))==
                   (len(adjacent(two,'a')),len(adjacent(two,'b'))),
            'equal_connectivity':connected(one,'a','b')==connected(two,'a','b'),
            'triangle_changes':(observed_outcome(pa)[0],observed_outcome(pb)[0]),
            'genuine_counterexample':observed_outcome(pa)[0]!=observed_outcome(pb)[0]}


def fir_receipts(discovery: Discovery, result: dict) -> dict:
    world=FIRWorld('finite synthetic simple graphs','topology-dependent readout')
    universal=Claim('These models correctly describe all graphs and real-world systems','unbounded')
    scope='test:'+result['digest']
    local=Claim('Exact replay of both outcomes across the declared held-out finite graph trials',scope)
    world.propose(universal);world.propose(local)
    if result['status']=='F_LOCAL_EXACT_TEST':
        world.admit(local,Warrant('finite_computation','recomputed graph transitions and independent measurement implementation',scope))
    return {'local_status':'F_LOCAL' if local in world.facts else 'I',
            'general_status':'I_ONLY','receipts':tuple(world.receipts)}


PINNED=('mathal001/nunumathal.py','fir001/fir.py',
        'contractdiscovery001/contractdiscovery.py','contractfrontier002/contractfrontier.py')


def source_pins(root:Path=ROOT) -> tuple[tuple[str,str],...]:
    root=Path(root).resolve(strict=True)
    hashes=[]
    for path in PINNED:
        file=root/path
        if not file.is_file() or file.is_symlink() or not file.resolve().is_relative_to(root):
            raise FrontierRefusal('HOLD_MISSING_OR_LINKED_SOURCE:'+path)
        hashes.append((path,sha256(file.read_bytes()).hexdigest()))
    return tuple(hashes)


CHILD='''"""Generated typed graph contract child. Trusted checkout, not sandbox."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
p=argparse.ArgumentParser()
p.add_argument('--source-root',required=True)
p.add_argument('--index',type=int,default=0)
a=p.parse_args()
root=Path(a.source_root).resolve(strict=True)
checks=json.loads(__PINS__)
for path,digest in checks:
    file=root/path
    if not file.is_file() or file.is_symlink() or sha256(file.read_bytes()).hexdigest()!=digest:
        print(json.dumps({'status':'HOLD_SOURCE_DRIFT','source':path}));sys.exit(0)
if a.index<0 or a.index>=100:
    print(json.dumps({'status':'HOLD_INDEX'}));sys.exit(0)
sys.path.insert(0,str(root/'contractfrontier002'))
from contractfrontier import Expr,Discovery,_graphs,infer,observed_outcome
law=json.loads(__CONTRACT__)
tri=Expr(tuple((n,c) for n,c in law['triangle']))
comp=Expr(tuple((n,c) for n,c in law['components']))
model=Discovery(tri,comp,law['inspected'],law['train_digest'],law['validation_digest'],
               'I_FINITE_CONTRACTS_VALIDATED',(),(1,1))
probe=_graphs('test',100)[a.index]
pred=infer(model,probe)
real=observed_outcome(probe)
print(json.dumps({'status':'F_LOCAL_CHILD_REPLAY' if
      (pred['delta_triangles'],pred['delta_components'])==real else 'HOLD_CHILD_MISMATCH',
      'predictions':[pred['delta_triangles'],pred['delta_components']],
      'observed':real,'tested_index':a.index,'external_actions':0,'repo_edits':0},sort_keys=True))
'''


def build_child(root:Path,output:Path,discovery:Discovery) -> Path:
    if not discovery.usable:
        raise FrontierRefusal('HOLD_UNVALIDATED_CHILD_INPUT')
    # Compare with frozen train/validation fixture replay, not user-supplied labels.
    verified=discover(_graphs('train',120),_graphs('validation',60))
    if (verified.triangle!=discovery.triangle or verified.components!=discovery.components
            or verified.train_digest!=discovery.train_digest
            or verified.validation_digest!=discovery.validation_digest):
        raise FrontierRefusal('HOLD_UNAUTHENTICATED_FINITE_CONTRACT')
    files=source_pins(root)
    output=Path(output)
    output.mkdir(parents=True,exist_ok=True)
    child=output/'discovered_topology_child.py'
    receipt=output/'discovered_topology_child.sha256'
    if any(x.exists() or x.is_symlink() for x in (child,receipt)):
        raise FileExistsError('HOLD_REFUSE_OVERWRITE')
    law={'triangle':discovery.triangle.terms,'components':discovery.components.terms,
         'inspected':discovery.inspected,'train_digest':discovery.train_digest,
         'validation_digest':discovery.validation_digest}
    code=CHILD.replace('__PINS__',repr(json.dumps(files))).replace('__CONTRACT__',repr(json.dumps(law)))
    child.write_text(code,encoding='utf8')
    receipt.write_text(sha256(child.read_bytes()).hexdigest()+'\n',encoding='ascii')
    return child


def run_child(child:Path,root:Path,index:int=0) -> dict:
    child=Path(child);receipt=child.with_suffix('.sha256')
    if (not child.is_file() or child.is_symlink() or not receipt.is_file() or
            receipt.is_symlink() or receipt.read_text().strip()!=sha256(child.read_bytes()).hexdigest()):
        return {'status':'HOLD_CHILD_TAMPER_OR_MISSING'}
    try:
        result=subprocess.run([sys.executable,str(child),'--source-root',str(root),
                '--index',str(index)],cwd=child.parent,capture_output=True,text=True,timeout=25)
    except subprocess.TimeoutExpired:
        return {'status':'HOLD_CHILD_TIMEOUT'}
    if result.returncode:
        return {'status':'HOLD_CHILD_PROCESS_ERROR','stderr':result.stderr[-300:]}
    try:
        return json.loads(result.stdout)
    except ValueError:
        return {'status':'HOLD_CHILD_NON_JSON'}


def demonstration() -> dict:
    import tempfile
    train,validation,test,ood=(_graphs(split,n) for split,n in
        (('train',120),('validation',60),('test',100),('ood',100)))
    discovered=discover(train,validation)
    on_test=audit(discovered,test)
    on_ood=audit(discovered,ood)
    with tempfile.TemporaryDirectory(prefix='motif-contract-frontier-') as folder:
        child=build_child(ROOT,Path(folder),discovered)
        child_result=run_child(child,ROOT,4)
    return {'experiment':'CONTRACT-FRONTIER-002',
            'question':'Can an unfamiliar cartridge discover topology-dependent and conditional graph laws?',
            'observed_training_probes':discovered.inspected,
            'candidate_programs':len(PROGRAMS),
            'inferred_laws':{'triangle_delta':discovered.triangle.text() if discovered.triangle else None,
                             'component_delta':discovered.components.text() if discovered.components else None},
            'test':on_test,'ood':on_ood,'ablation':coarse_counterexample(),
            'child':child_result,'FIR':fir_receipts(discovered,on_test),
            'status':discovered.status,'real_world_actions':0,
            'self_modified_live_code':False,'generalization_proved':False,
            'next_question':'Which higher-order graph relations survive new feature grammars and truly independent world families?'}


if __name__=='__main__':
    print(json.dumps(demonstration(),indent=2,sort_keys=True,default=str))
