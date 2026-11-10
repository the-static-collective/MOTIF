"""FEATURE-FRONTIER-001 — construct useful graph features from primitive edge relations.

Finite relational query enumeration, bounded active version spaces, and a generic
reachability-closure operator. Does NOT invent arbitrary graph concepts, infer
real-world truth, or edit/deploy an operating MOTIF. No named common-neighbor
or connected-component feature is available to the learner.
"""
from __future__ import annotations
from collections import Counter
from dataclasses import dataclass
from functools import lru_cache
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
sys.path.insert(0, str(ROOT/'contractfrontier002'))
from nunumathal import Graph
from contractfrontier import Probe, _graphs, observed_outcome

class FeatureRefusal(ValueError):
    pass

# Bare relational primitives: a,b are insertion endpoints; x is counted,
# y is a possibly existentially quantified helper. Every atom means E(u,v).
ATOM_TYPES = tuple(combinations(('a','b','x','y'), 2))

@dataclass(frozen=True)
class Feature:
    kind: str  # count a generated conjunctive edge query OR existence in E^k / E*
    atoms: tuple[tuple[str,str],...] = ()
    depth: int = 0  # depth==0 is least-fixed-point closure, not a pre-named predicate

    def __post_init__(self):
        if self.kind == 'count':
            if not 1 <= len(self.atoms) <= 3 or self.atoms != tuple(sorted(self.atoms)):
                raise FeatureRefusal('HOLD_QUERY_GRAMMAR')
            if len(set(self.atoms)) != len(self.atoms) or any(a not in ATOM_TYPES for a in self.atoms):
                raise FeatureRefusal('HOLD_QUERY_ATOM')
            if not any('x' in a for a in self.atoms) or self.depth != 0:
                raise FeatureRefusal('HOLD_UNBOUND_COUNT_VARIABLE')
        elif self.kind == 'edge_closure':
            if self.atoms or self.depth not in (0,2,3,4,5):
                raise FeatureRefusal('HOLD_CLOSURE_GRAMMAR')
        else:
            raise FeatureRefusal('HOLD_UNKNOWN_FEATURE_OPERATION')

    def description(self):
        if self.kind == 'count':
            body=' & '.join(f'E({u},{v})' for u,v in self.atoms)
            return f'COUNT_DISTINCT(x : EXISTS y . {body})' if any('y' in p for p in self.atoms) else f'COUNT(x : {body})'
        return 'EXISTS((E)*;a,b)' if self.depth == 0 else f'EXISTS((E)^<= {self.depth};a,b)'

    @property
    def complexity(self):
        # Generic closure is costlier than a short query; an L2 join is cheap.
        return len(self.atoms) if self.kind == 'count' else 2 + (2 if self.depth == 0 else self.depth)

    def evaluate(self, graph: Graph, a: str, b: str) -> int:
        if a == b or a not in graph.vertices or b not in graph.vertices:
            raise FeatureRefusal('HOLD_ENDPOINTS')
        if self.kind == 'edge_closure':
            seen={a}; frontier={a}
            max_depth=len(graph.vertices) if self.depth == 0 else self.depth
            for _ in range(max_depth):
                frontier={v if u==x else u
                          for x in frontier for u,v in graph.edges if x in (u,v)} - seen
                seen |= frontier
                if b in seen:
                    return 1
                if not frontier:
                    break
            return 0
        # Tuple assignment over graph's elementary edge relation. This derives
        # conjunctions by joining relations, rather than calling a prebuilt
        # common-neighbor function. COUNT DISTINCT x with existential y.
        edges=graph.edges
        has_y=any('y' in edge for edge in self.atoms)
        for_x = 0
        for x in graph.vertices:
            base={'a':a,'b':b,'x':x}
            choices=graph.vertices if has_y else (None,)
            for y in choices:
                env=dict(base)
                if has_y:
                    env['y']=y
                if all(tuple(sorted((env[u],env[v]))) in edges for u,v in self.atoms):
                    for_x+=1
                    break
        return for_x


@dataclass(frozen=True)
class Expression:
    feature: Feature|None
    coefficient: int
    intercept: int

    def __post_init__(self):
        if (self.coefficient not in (-1,0,1) or self.intercept not in (-1,0,1)
                or (self.feature is None) != (self.coefficient==0)):
            raise FeatureRefusal('HOLD_LINEAR_WRAPPER_GRAMMAR')

    @property
    def complexity(self):
        return (0 if self.feature is None else self.feature.complexity) + (self.intercept!=0) + (self.coefficient!=0)

    def __call__(self, p: Probe) -> int:
        return self.intercept + (self.coefficient*self.feature.evaluate(p.graph,p.a,p.b)
                                 if self.feature else 0)

    def text(self):
        if self.feature is None: return str(self.intercept)
        return f'{self.coefficient}*[{self.feature.description()}] {self.intercept:+d}'


def grammar() -> tuple[Expression,...]:
    features=[]
    for n in (1,2,3):
        for atoms in combinations(ATOM_TYPES,n):
            if any('x' in atom for atom in atoms):
                features.append(Feature('count',atoms))
    features += [Feature('edge_closure',depth=k) for k in (2,3,4,5,0)]
    models={Expression(None,0,b) for b in (-1,0,1)}
    for f in features:
        for c in (-1,1):
            for b in (-1,0,1):
                models.add(Expression(f,c,b))
    return tuple(sorted(models,key=lambda e:(e.complexity,e.text())))

PROGRAMS = grammar()


def path_probe(split: str, length: int, disconnected: bool=False) -> Probe:
    if split not in ('train','validation','test','ood') or length<2:
        raise FeatureRefusal('HOLD_PATH_FIXTURE')
    vertices=[f'{split}_path{length}_{int(disconnected)}_{i}' for i in range(length+1)]
    edges=[(vertices[i],vertices[i+1]) for i in range(length) if not(disconnected and i==length//2)]
    return Probe(f'{split}:path:{length}:gap{int(disconnected)}',
                 Graph.build(vertices,edges),vertices[0],vertices[-1],split)


def pool(split: str, random_cases:int=45) -> tuple[Probe,...]:
    if split not in ('train','validation','test','ood') or random_cases < 1:
        raise FeatureRefusal('HOLD_POOL_SPLIT')
    base=list(_graphs(split,random_cases))
    if split=='train':
        lengths=(2,3,4,5,6,8,10)
    elif split=='validation':
        lengths=(2,3,6,8,11)
    elif split=='test':
        lengths=(2,5,7,12)
    else:
        lengths=(2,6,13,18,23)
    for k in lengths:
        base.append(path_probe(split,k))
        base.append(path_probe(split,k,True))
    return tuple(base)


def _entropy(values: Iterable[int]) -> float:
    c=Counter(values); n=sum(c.values())
    return -sum((v/n)*log2(v/n) for v in c.values()) if n else 0.0


@dataclass(frozen=True)
class Discovery:
    triangle: Expression|None
    components: Expression|None
    train_digest: str
    valid_digest: str
    inspections: int
    remaining_hypotheses: tuple[int,int]
    status: str
    receipts: tuple[dict,...]

    @property
    def usable(self):
        return self.status=='I_VALIDATED_SYNTHESIZED_FEATURES' and self.triangle is not None and self.components is not None


def _digest(evidence:Iterable):
    return sha256(json.dumps(list(evidence),sort_keys=True,default=str).encode()).hexdigest()[:24]


def discover(training:tuple[Probe,...], validation:tuple[Probe,...],
             budget:int=16, select:str='active', seed:int=7,
             programs:tuple[Expression,...]=PROGRAMS) -> Discovery:
    """Probe selection sees graph inputs only; graph consequences opened after choice.

    All code uses a frozen generic graph-query grammar. Never reads test/ood.
    Validation cannot select a replacement law when the training candidate fails.
    """
    if (not training or not validation or not 1<=budget<=len(training)
            or select not in ('active','random') or not programs
            or len({p.key for p in training})!=len(training)
            or len({p.key for p in validation})!=len(validation)
            or set(p.key for p in training)&set(p.key for p in validation)):
        raise FeatureRefusal('HOLD_SPLIT_OR_BUDGET')
    rng=Random(seed)
    # Computing candidate programs from unlabelled pre-intervention graphs is
    # permitted. This cache has no observed outcome or privileged hidden labels.
    cache={p.key:tuple(m(p) for m in programs) for p in training}
    versions=[set(range(len(programs))),set(range(len(programs)))]
    evidence=[];receipts=[];remaining=list(training)
    for index in range(budget):
        if select=='active':
            rated=[]
            for p in remaining:
                predictions=cache[p.key]
                gain=sum(_entropy(predictions[j] for j in vs) for vs in versions)
                rated.append((-gain,p.key,p))
            chosen=min(rated,key=lambda x:(x[0],x[1]))[2]
        else:
            chosen=rng.choice(remaining)
        remaining.remove(chosen)
        outcome=observed_outcome(chosen)  # *** first outcome access, after choice ***
        prediction=cache[chosen.key]
        before=tuple(len(vs) for vs in versions)
        versions=[{j for j in vs if prediction[j]==outcome[head]}
                  for head,vs in enumerate(versions)]
        evidence.append((chosen.key,outcome))
        receipts.append({'step':index+1,'next_question':'Which graph intervention distinguishes the surviving relational programs?',
                         'probe':chosen.key,'prediction_entropy_selected_without_outcome':True,
                         'measured':outcome,'version_space_before':before,
                         'version_space_after':tuple(len(vs) for vs in versions),'external_actions':0})
        if not all(versions):
            return Discovery(None,None,_digest(evidence),'',len(evidence),tuple(len(v) for v in versions),
                             'HOLD_NO_RELATIONAL_EXPLANATION',tuple(receipts))
        # Stop only when every surviving model makes identical predictions on
        # *all remaining TRAIN candidate inputs*. This is not universality.
        if len(evidence)>=2 and all(all(len({cache[p.key][j] for j in vs})==1 for p in remaining)
                                  for vs in versions):
            break
    winners=[]
    for vs in versions:
        if not vs:
            return Discovery(None,None,_digest(evidence),'',len(evidence),tuple(len(v) for v in versions),
                             'HOLD_EMPTY_VERSION_SPACE',tuple(receipts))
        minimal=min(programs[j].complexity for j in vs)
        best=[programs[j] for j in vs if programs[j].complexity==minimal]
        if len({m.text() for m in best})!=1:
            return Discovery(None,None,_digest(evidence),'',len(evidence),tuple(len(v) for v in versions),
                             'HOLD_EQUAL_COMPLEXITY_AMBIGUITY',tuple(receipts))
        winners.append(best[0])
    validation_evidence=[]
    for p in validation:
        observed=observed_outcome(p)
        validation_evidence.append((p.key,observed))
        if tuple(m(p) for m in winners)!=observed:
            return Discovery(None,None,_digest(evidence),_digest(validation_evidence),len(evidence),
                             tuple(len(v) for v in versions),'HOLD_VALIDATION_COUNTEREXAMPLE',tuple(receipts))
    receipts.append({'action':'VALIDATE_FROZEN_DISCOVERED_PROGRAMS','cases':len(validation_evidence),
                     'digest':_digest(validation_evidence),'status':'F_LOCAL_EXACT_REPLAY'})
    return Discovery(winners[0],winners[1],_digest(evidence),_digest(validation_evidence),
                     len(evidence),tuple(len(v) for v in versions),'I_VALIDATED_SYNTHESIZED_FEATURES',tuple(receipts))


def infer(d: Discovery,p: Probe) -> tuple[int,int]:
    if not d.usable:
        raise FeatureRefusal('HOLD_UNVALIDATED_FEATURES')
    return d.triangle(p),d.components(p)


def heldout(d:Discovery, probes:tuple[Probe,...]) -> dict:
    if not d.usable or not probes:
        return {'status':'HOLD_NO_VALIDATED_FEATURES'}
    actual=tuple(observed_outcome(p) for p in probes)
    predicted=tuple(infer(d,p) for p in probes)
    return {'cases':len(probes),'matched':sum(a==b for a,b in zip(predicted,actual)),
            'digest':_digest(zip((p.key for p in probes),actual)),
            'status':'F_LOCAL_REPLAY' if predicted==actual else 'HOLD_HIDDEN_COUNTEREXAMPLE',
            'general_claim':False}


def ablate(training:tuple[Probe,...], validation:tuple[Probe,...], *,
           remove_join:bool=False, remove_closure:bool=False, budget:int=16)->dict:
    """Actual refit under an ablated grammar, not merely hiding a good answer."""
    expressions=tuple(p for p in PROGRAMS if p.feature is None or (
        (not remove_join or p.feature.kind!='count' or len(p.feature.atoms)==1)
        and (not remove_closure or p.feature.kind!='edge_closure' or p.feature.depth!=0)))
    result=discover(training,validation,budget=budget,programs=expressions)
    return {'programs':len(expressions),'status':result.status,
            'inspections':result.inspections,'triangle':result.triangle.text() if result.triangle else None,
            'components':result.components.text() if result.components else None}


def fir_receipt(d:Discovery, checked:dict)->dict:
    """Admit exact finite arithmetic only; leave general feature correctness I."""
    from fir import FIRWorld, Claim, Warrant
    scope='finite-feature-replay:'+str(checked.get('digest','unknown'))
    finite=Claim('The frozen synthesized feature programs matched these exact graph fixtures',scope)
    universal=Claim('The synthesized programs are authentic, correct in any real environment','unbounded')
    world=FIRWorld('synthetic graph relations','bounded feature-program evidence')
    world.propose(finite)
    world.propose(universal)
    if checked.get('status')=='F_LOCAL_REPLAY' and d.usable:
        world.admit(finite,Warrant('finite_computation','exact synthetic graph replay, not an independent physical instrument',scope))
    return {'finite_role':'F_LOCAL' if finite in world.facts else 'I',
            'universal_role':'I','receipts':tuple(world.receipts)}

def anti_corruption(d:Discovery,p:Probe)->dict:
    known=observed_outcome(p)
    forged=(known[0]+1,known[1])
    return {'type_correct_corruption':True,'detected_by_independent_replay':forged!=infer(d,p),
            'trusted_source_authenticity_proved':False}

# Emitted code is a parameterized fixed interpreter of synthesized query programs.
# It imports trusted repo modules: subprocess alone is NOT a security sandbox.
PINNED=('fir001/fir.py','mathal001/nunumathal.py','contractdiscovery001/contractdiscovery.py',
        'contractfrontier002/contractfrontier.py','featurefrontier001/featurefrontier.py')

def pins(root:Path=ROOT):
    root=Path(root).resolve(strict=True)
    result=[]
    for rel in PINNED:
        f=root/rel
        if not f.is_file() or f.is_symlink() or not f.resolve().is_relative_to(root):
            raise FeatureRefusal('HOLD_MISSING_SOURCE:'+rel)
        result.append((rel,sha256(f.read_bytes()).hexdigest()))
    return tuple(result)

CHILD = '''"""Generated feature-composer child; no real-world effects."""
from pathlib import Path
from hashlib import sha256
import argparse,sys,json
p=argparse.ArgumentParser();p.add_argument('--source-root',required=True)
p.add_argument('--index',type=int,default=0);a=p.parse_args()
root=Path(a.source_root).resolve(strict=True)
checks=json.loads(__PINS__)
for rel,digest in checks:
    f=root/rel
    if not f.is_file() or f.is_symlink() or sha256(f.read_bytes()).hexdigest()!=digest:
        print(json.dumps({'status':'HOLD_SOURCE_DRIFT','source':rel}));sys.exit(0)
sys.path.insert(0,str(root/'featurefrontier001'))
from featurefrontier import Feature,Expression,Discovery,pool,infer,observed_outcome
raw=json.loads(__PROGRAMS__)
def rebuild(spec):
    f=spec['feature']
    feature=None if f is None else Feature(f['kind'],tuple(tuple(p) for p in f['atoms']),f['depth'])
    return Expression(feature,spec['coefficient'],spec['intercept'])
first,second=tuple(rebuild(x) for x in raw)
# Child is replay verified against the pinned training/validation experiment.
from featurefrontier import discover
verified=discover(pool('train'),pool('validation'))
if verified.triangle!=first or verified.components!=second:
    print(json.dumps({'status':'HOLD_UNVERIFIED_PROGRAM'}));sys.exit(0)
checks=pool('test',30)
if a.index<0 or a.index>=len(checks):
    print(json.dumps({'status':'HOLD_INDEX'}));sys.exit(0)
probe=checks[a.index]
observed=observed_outcome(probe)
predicted=infer(verified,probe)
print(json.dumps({'status':'F_LOCAL_CHILD_REPLAY' if observed==predicted else 'HOLD_CHILD_COUNTEREXAMPLE',
                  'programs':[first.text(),second.text()],'observed':observed,
                  'predicted':predicted,'real_actions':0,'source_changes':0},sort_keys=True))
'''

def build_child(root:Path,out:Path,discovery:Discovery)->Path:
    if not discovery.usable:
        raise FeatureRefusal('HOLD_CHILD_UNVERIFIED')
    confirmed=discover(pool('train'),pool('validation'))
    if (confirmed.triangle!=discovery.triangle or confirmed.components!=discovery.components
            or confirmed.train_digest!=discovery.train_digest or confirmed.valid_digest!=discovery.valid_digest):
        raise FeatureRefusal('HOLD_CHILD_FORGED_CONTRACT')
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    child=out/'inferred_feature_child.py';receipt=out/'inferred_feature_child.sha256'
    if child.exists() or child.is_symlink() or receipt.exists() or receipt.is_symlink():
        raise FileExistsError('HOLD_REFUSE_TO_OVERWRITE_CHILD')
    from dataclasses import asdict
    programs=[asdict(discovery.triangle),asdict(discovery.components)]
    source=CHILD.replace('__PINS__',repr(json.dumps(pins(root))))
    source=source.replace('__PROGRAMS__',repr(json.dumps(programs)))
    child.write_text(source,encoding='utf8')
    receipt.write_text(sha256(child.read_bytes()).hexdigest()+'\n')
    return child

def run_child(child:Path,root:Path,index:int=0)->dict:
    child=Path(child);receipt=child.with_suffix('.sha256')
    if not child.is_file() or child.is_symlink() or not receipt.is_file() or receipt.is_symlink():
        return {'status':'HOLD_CHILD_MISSING_OR_LINKED'}
    if receipt.read_text().strip()!=sha256(child.read_bytes()).hexdigest():
        return {'status':'HOLD_CHILD_TAMPER'}
    try:
        call=subprocess.run([sys.executable,str(child),'--source-root',str(root),'--index',str(index)],
                            capture_output=True,text=True,cwd=child.parent,timeout=35)
    except subprocess.TimeoutExpired:
        return {'status':'HOLD_CHILD_TIMEOUT'}
    if call.returncode:
        return {'status':'HOLD_CHILD_PROCESS_ERROR','stderr':call.stderr[-400:]}
    try:
        return json.loads(call.stdout)
    except json.JSONDecodeError:
        return {'status':'HOLD_CHILD_NON_JSON'}

def demonstration():
    import tempfile
    d=discover(pool('train'),pool('validation'))
    a=heldout(d,pool('test',100))
    b=heldout(d,pool('ood',100))
    with tempfile.TemporaryDirectory(prefix='motif-generated-feature-') as tmp:
        child=build_child(ROOT,Path(tmp),d)
        c=run_child(child,ROOT)
    return {'experiment':'FEATURE-FRONTIER-001',
            'question':'Can MOTIF construct previously unnamed relational graph features from edge observations?',
            'candidate_programs':len(PROGRAMS),'inspected_interventions':d.inspections,
            'remaining_candidate_counts':d.remaining_hypotheses,
            'inferred_laws':(d.triangle.text() if d.triangle else None,d.components.text() if d.components else None),
            'status':d.status,'test':a,'ood':b,'child':c,
            'FIR':{'finite_role':fir_receipt(d,a)['finite_role'],
                   'universal_role':fir_receipt(d,a)['universal_role']},
            'no_labels_from_test_used_in_learning':True,'general_invention_claim':False,
            'real_world_actions':0,'external_evidence':False,
            'next_question':'Can the relational language itself grow when its current operators cannot express a needed property?'}

if __name__=='__main__':
    print(json.dumps(demonstration(),sort_keys=True,indent=2))
