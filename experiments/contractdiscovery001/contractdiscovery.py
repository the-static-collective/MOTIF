"""CONTRACT-DISCOVERY-001: infer a missing executable port law from interventions.

The learner sees opaque integer channels, not their meanings or the intended
invariant. A finite graph instrument (real MOTIF nunumathal.Graph/statistics)
provides the readings. Exact rational nullspace search discovers a candidate
homogeneous linear relation, subject to rank, independent splits, and attacks.

This is classical finite linear algebra on a predeclared five-channel grammar.
There is no general semantic understanding, causal identification, proof of
universal graph theory, or autonomous deployment here.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from functools import reduce
from hashlib import sha256
from itertools import product
from math import gcd, lcm
from pathlib import Path
from typing import Iterable
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'mathal001'))
sys.path.insert(0, str(ROOT / 'fir001'))
from nunumathal import Graph, perform, statistics
from fir import Claim, FIRWorld, Warrant

N_CHANNELS = 5
CHANNELS = tuple(f'u{j}' for j in range(N_CHANNELS))
# The permutation is an input encoding (the instrument's wire layout), NOT
# an answer key given to the learner. It deliberately hides source field names.
PERMUTATION = (3, 0, 4, 1, 2)


class ContractRefusal(ValueError):
    pass


@dataclass(frozen=True)
class Trial:
    key: str
    source: Graph
    operation: str
    operands: tuple[str, ...] = ()

    def __post_init__(self):
        if not self.key or self.operation not in {
            'isolated','leaf','subdivide','add_edge','remove_edge','remove_isolate'
        }:
            raise ContractRefusal('HOLD_UNKNOWN_INTERVENTION')


def apply(trial: Trial) -> Graph:
    """Allowed interventions only. First three invoke real NUNUMATHAL rules."""
    before = trial.source
    op, args = trial.operation, trial.operands
    if op == 'isolated' and len(args) == 1:
        return perform(before, 'isolated', args[0]).target
    if op == 'leaf' and len(args) == 2:
        return perform(before, 'leaf', args[0], anchor=args[1]).target
    if op == 'subdivide' and len(args) == 3:
        return perform(before, 'subdivide', args[0], edge=args[1:]).target
    if op == 'add_edge' and len(args) == 2:
        a, b = args
        edge = tuple(sorted((a,b)))
        if a == b or a not in before.vertices or b not in before.vertices or edge in before.edges:
            raise ContractRefusal('HOLD_ADD_EDGE_PRECONDITION')
        return Graph.build(before.vertices, before.edges | {edge})
    if op == 'remove_edge' and len(args) == 2:
        edge = tuple(sorted(args))
        if edge not in before.edges:
            raise ContractRefusal('HOLD_REMOVE_EDGE_PRECONDITION')
        return Graph.build(before.vertices, before.edges - {edge})
    if op == 'remove_isolate' and len(args) == 1:
        vertex = args[0]
        if vertex not in before.vertices or any(vertex in e for e in before.edges):
            raise ContractRefusal('HOLD_REMOVE_ISOLATE_PRECONDITION')
        return Graph.build(before.vertices - {vertex}, before.edges)
    raise ContractRefusal('HOLD_BAD_INTERVENTION_ARGUMENTS')


def _path(prefix: str) -> Graph:
    a,b,c = (prefix+x for x in 'abc')
    return Graph.build((a,b,c),((a,b),(b,c)))


def _isolate_pair(prefix: str) -> Graph:
    return Graph.build((prefix+'a', prefix+'b'), ())


def _extra(g: Graph, prefix: str, count: int) -> Graph:
    """Vary absolute topology while retaining a stable named intervention site."""
    nodes = set(g.vertices)
    edges = set(g.edges)
    for i in range(count):
        names = (f'{prefix}extra{i}x',f'{prefix}extra{i}y',f'{prefix}extra{i}z')
        nodes.update(names)
        edges.update((tuple(sorted((names[0], names[1]))),
                      tuple(sorted((names[1], names[2])))))
        if i % 2:
            edges.add(tuple(sorted((names[0],names[2]))))
    return Graph.build(nodes,edges)


def trials(split: str) -> tuple[Trial, ...]:
    """No reused IDs or graph labels across train/validation/test/OOD.

    Train never uses deletion. OOD deliberately adds source topologies,
    reverse interventions, and cyclic/disconnected graphs.
    """
    if split not in {'train','validation','test','ood'}:
        raise ContractRefusal('HOLD_UNKNOWN_SPLIT')
    groups = {'train':4, 'validation':3, 'test':7, 'ood':6}[split]
    result = []
    for i in range(groups):
        prefix = f'{split}{i}_'
        p = _extra(_path(prefix),prefix,i%3)
        iso = _extra(_isolate_pair(prefix+'iso_'),prefix,i%3)
        a,b,c=(prefix+x for x in 'abc')
        x,y=(prefix+'iso_a',prefix+'iso_b')
        examples = [
            (p,'isolated',(prefix+'new_iso',)),
            (p,'leaf',(prefix+'new_leaf',a)),
            (p,'subdivide',(prefix+'new_sub',a,b)),
            (p,'add_edge',(a,c)),                 # inside-component cycle
            (iso,'add_edge',(x,y)),               # bridges two isolated components
        ]
        if split == 'ood':
            examples += [
                (p,'remove_edge',(a,b)),          # previously unseen inverse mechanism
                (iso,'remove_isolate',(x,)),      # previously unseen vertex deletion
                (_extra(_path(prefix+'other_'),prefix,3),'remove_edge',
                    (prefix+'other_a',prefix+'other_b')),
            ]
        for j,(graph,op,args) in enumerate(examples):
            result.append(Trial(f'{split}:{i}:{j}', graph,op,args))
    return tuple(result)


def measure(trial: Trial, permutation: tuple[int,...] = PERMUTATION) -> tuple[int,...]:
    """Black-box numerical observation: learner is never given coordinate names."""
    if tuple(sorted(permutation)) != tuple(range(N_CHANNELS)):
        raise ContractRefusal('HOLD_CHANNEL_ENCODING')
    before = statistics(trial.source)
    after = statistics(apply(trial))
    delta = tuple(b-a for a,b in zip(before,after))
    return tuple(delta[j] for j in permutation)


def _forest_cycles(g: Graph) -> int:
    """A separately implemented graph-cycle count (spanning-forest surplus).

    Unlike the source statistics function, this does not calculate E - V + C.
    This is still author-written verification, not an independent laboratory.
    """
    parent = {v:v for v in g.vertices}
    def find(v):
        while parent[v] != v:
            v = parent[v]
        return v
    surplus = 0
    for a,b in sorted(g.edges):
        x,y=find(a),find(b)
        if x == y:
            surplus += 1
        else:
            parent[x]=y
    return surplus


def independent_statistics(g: Graph) -> tuple[int,int,int,int,int]:
    components = []
    pending = set(g.vertices)
    while pending:
        group = {pending.pop()}
        while True:
            touching = {v for e in g.edges for v in e if e[0] in group or e[1] in group}
            new = touching & pending
            if not new:
                break
            group |= new
            pending -= new
        components.append(group)
    incident = {v for e in g.edges for v in e}
    return (len(g.vertices),len(g.edges),len(components),
            len(g.vertices-incident),_forest_cycles(g))


def independently_measure(trial: Trial, permutation: tuple[int,...] = PERMUTATION) -> tuple[int,...]:
    """Independent implementation for evaluation; learner does not call this."""
    old,new=independent_statistics(trial.source),independent_statistics(apply(trial))
    return tuple((new[i]-old[i]) for i in permutation)


def row_reduce(matrix: Iterable[tuple[int,...]]) -> tuple[list[list[Fraction]],tuple[int,...]]:
    data=[list(map(Fraction,row)) for row in matrix]
    if any(len(row)!=N_CHANNELS for row in data):
        raise ContractRefusal('HOLD_ROW_WIDTH')
    pivot=[]
    rank=0
    for col in range(N_CHANNELS):
        candidate=next((i for i in range(rank,len(data)) if data[i][col]),None)
        if candidate is None:
            continue
        data[rank],data[candidate]=data[candidate],data[rank]
        div=data[rank][col]
        data[rank]=[x/div for x in data[rank]]
        for j in range(len(data)):
            if j != rank and data[j][col]:
                amount=data[j][col]
                data[j]=[x-amount*y for x,y in zip(data[j],data[rank])]
        pivot.append(col)
        rank+=1
        if rank==len(data):
            break
    return data,tuple(pivot)


def rank(rows: Iterable[tuple[int,...]]) -> int:
    return len(row_reduce(rows)[1])


def primitive(values: Iterable[Fraction | int]) -> tuple[int,...]:
    numbers=tuple(Fraction(v) for v in values)
    denom=lcm(*(x.denominator for x in numbers))
    integers=tuple(int(x*denom) for x in numbers)
    divider=reduce(gcd,(abs(x) for x in integers),0)
    if not divider:
        raise ContractRefusal('HOLD_ZERO_RELATION')
    result=tuple(x//divider for x in integers)
    first=next(x for x in result if x)
    return tuple(-x for x in result) if first<0 else result


def nullspace(matrix: Iterable[tuple[int,...]]) -> tuple[tuple[int,...],...]:
    reduced,pivots=row_reduce(matrix)
    free=[j for j in range(N_CHANNELS) if j not in pivots]
    basis=[]
    for f in free:
        v=[Fraction(0)]*N_CHANNELS
        v[f]=Fraction(1)
        for index,col in enumerate(pivots):
            v[col]=-reduced[index][f]
        basis.append(primitive(v))
    return tuple(basis)


def digest(rows: Iterable[tuple[str,tuple[int,...]]]) -> str:
    return sha256(json.dumps(list(rows),separators=(',',':')).encode()).hexdigest()[:20]


@dataclass(frozen=True)
class Discovery:
    relation: tuple[int,...] | None
    rank: int
    alternatives: int
    inspections: int
    informative_inspections: int
    train_digest: str
    validation_digest: str
    status: str
    receipts: tuple[dict,...]

    def __post_init__(self):
        if self.relation is not None and (len(self.relation)!=N_CHANNELS or
                                           self.status!='I_UNIQUE_FINITE_LINEAR_CONTRACT'):
            raise ContractRefusal('HOLD_MALFORMED_CONTRACT')


def discover(training: tuple[Trial,...], validation: tuple[Trial,...],
             max_probes: int=40, min_probe_count: int=8,
             permutation: tuple[int,...]=PERMUTATION) -> Discovery:
    """Sequentially perform allowed experiments, preserving candidate ambiguity.

    The learner receives no true coefficient vector or target-column labels.
    It tries new intervention types first; it cannot inspect unused readouts.
    Only TRAIN probes can determine the coefficient vector; only VALIDATION can
    check the frozen result. A rank-deficient world must abstain.
    """
    if (not training or not validation or max_probes<1 or min_probe_count<1
            or len({t.key for t in training})!=len(training)
            or len({t.key for t in validation})!=len(validation)
            or {t.key for t in training}&{t.key for t in validation}):
        raise ContractRefusal('HOLD_LEAKED_OR_INCOMPLETE_SPLITS')
    unseen=list(training)
    used_ops:set[str]=set()
    receipts=[]
    observed=[]
    old_rank=0
    while unseen and len(observed)<max_probes:
        index=next((i for i,t in enumerate(unseen) if t.operation not in used_ops),0)
        trial=unseen.pop(index)
        # The reading is requested here, not read in a planning lookahead.
        reading=measure(trial,permutation)
        observed.append((trial.key,reading))
        used_ops.add(trial.operation)
        current=rank([v for _,v in observed])
        receipts.append({'question':'Which new intervention can resolve a remaining contract ambiguity?',
                         'action':'EXECUTE_LOCAL_GRAPH_PROBE','event':trial.key,
                         'operation':trial.operation,'readout':reading,
                         'rank_before':old_rank,'rank_after':current,
                         'new_information':current>old_rank})
        old_rank=current
        if current==N_CHANNELS-1 and len(observed)>=min_probe_count:
            break
    basis=nullspace([v for _,v in observed])
    train_hash=digest(observed)
    if len(observed)<min_probe_count:
        return Discovery(None,old_rank,len(basis),len(observed),
                         sum(x['new_information'] for x in receipts),train_hash,'',
                         'HOLD_INSUFFICIENT_PROBE_BUDGET',tuple(receipts))
    if len(basis)!=1:
        return Discovery(None,old_rank,len(basis),len(observed),
                         sum(x['new_information'] for x in receipts),train_hash,'',
                         'HOLD_UNIDENTIFIABLE_CONTRACT',tuple(receipts))
    relation=basis[0]
    tested=[(t.key,measure(t,permutation)) for t in validation]
    if not tested or any(sum(a*x for a,x in zip(relation,v)) != 0 for _,v in tested):
        return Discovery(None,old_rank,len(basis),len(observed),
                         sum(x['new_information'] for x in receipts),train_hash,digest(tested),
                         'HOLD_VALIDATION_COUNTEREXAMPLE',tuple(receipts)+
                         ({'operation':'refuse','reason':'out-of-sample relation failed'},))
    receipts.append({'question':'Does the frozen inferred relation survive independent validation worlds?',
                     'action':'CHECK_FINITE_LINEAR_CONTRACT',
                     'validation_count':len(tested),'validation_digest':digest(tested),
                     'status':'F_LOCAL_EXACT_REPLAY'})
    return Discovery(relation,old_rank,len(basis),len(observed),
                     sum(x['new_information'] for x in receipts if 'new_information' in x),
                     train_hash,digest(tested),'I_UNIQUE_FINITE_LINEAR_CONTRACT',tuple(receipts))


def check_relation(discovery: Discovery, raw: tuple[int,...]) -> bool:
    if discovery.relation is None or len(raw)!=N_CHANNELS or any(type(v) is not int for v in raw):
        raise ContractRefusal('HOLD_INCOMPLETE_CONTRACT_OR_READING')
    return sum(a*x for a,x in zip(discovery.relation,raw))==0


@dataclass(frozen=True)
class MissingPortAdapter:
    contract: Discovery
    absent: str

    def __post_init__(self):
        if self.absent not in CHANNELS or self.contract.relation is None:
            raise ContractRefusal('HOLD_UNKNOWN_OR_UNPROVEN_PORT')
        if self.contract.relation[CHANNELS.index(self.absent)] == 0:
            raise ContractRefusal('HOLD_PORT_NOT_IDENTIFIABLE_FROM_CONTRACT')

    def reconstruct(self, available: dict[str,int]) -> dict:
        if (not isinstance(available,dict) or set(available)!=set(CHANNELS)-{self.absent}
                or any(type(v) is not int for v in available.values())):
            raise ContractRefusal('HOLD_TYPED_INPUT_PORTS')
        missing_index=CHANNELS.index(self.absent)
        total=sum(Fraction(self.contract.relation[i]*available[name])
                  for i,name in enumerate(CHANNELS) if name!=self.absent)
        value=-total/Fraction(self.contract.relation[missing_index])
        if value.denominator!=1:
            raise ContractRefusal('HOLD_NONINTEGER_RECONSTRUCTION')
        return {'status':'I_DERIVED_MISSING_PORT','channel':self.absent,'value':int(value),
                'source_digest':self.contract.train_digest,
                'validation_digest':self.contract.validation_digest,
                'external_actions':0}


def test_heldout(discovery: Discovery, cases: tuple[Trial,...]) -> dict:
    """Heldout uses a separate graph-metric implementation for source checks."""
    if discovery.relation is None:
        return {'status':'HOLD_NO_DISCOVERED_RELATION'}
    observed=0; verified=0; contracts=0; reconstructions=0
    for t in cases:
        reading=measure(t)
        independently=independently_measure(t)
        observed+=1
        verified+= reading==independently
        contracts+=check_relation(discovery,reading)
        for absent,coefficient in zip(CHANNELS,discovery.relation):
            if not coefficient:
                continue
            a=MissingPortAdapter(discovery,absent)
            partial={name:reading[i] for i,name in enumerate(CHANNELS) if name!=absent}
            reconstructions += (a.reconstruct(partial)['value'] == reading[CHANNELS.index(absent)])
    return {'worlds':observed,'independently_recomputed':verified,
            'relations_hold':contracts,'reconstructed_ports_correct':reconstructions,
            'reconstructions_possible':observed*sum(bool(c) for c in discovery.relation),
            'status':'F_LOCAL_EXACT_HOLDOUT' if verified==observed and contracts==observed
                        and reconstructions==observed*sum(bool(c) for c in discovery.relation)
                     else 'HOLD_HIDDEN_REGRESSION',
            'generalization_proved':False}


def exhaustive_classical_control(readings: Iterable[tuple[int,...]]) -> tuple[tuple[int,...],...]:
    """Independent, much slower integer enumeration over the declared grammar."""
    rows=tuple(readings)
    candidates=set()
    for vector in product((-1,0,1),repeat=N_CHANNELS):
        if not any(vector):
            continue
        if all(sum(c*x for c,x in zip(vector,row))==0 for row in rows):
            candidates.add(primitive(vector))
    return tuple(sorted(candidates))


def fir_record(discovery: Discovery, heldout: dict) -> dict:
    """Finite evidence may be F_LOCAL; unrestricted graph law remains I."""
    scope='test:'+discovery.validation_digest+':'+str(heldout['worlds'])
    local=Claim('Discovered opaque linear relation verified on the declared finite graph probes',scope)
    global_claim=Claim('Discovered relation holds for all future physical or mathematical systems','unbounded')
    world=FIRWorld('finite synthetic undirected graphs','opaque 5-channel numerical readout')
    world.propose(global_claim)
    world.propose(local)
    status='I_LOCAL_UNCHECKED'
    if heldout['status']=='F_LOCAL_EXACT_HOLDOUT':
        world.admit(local,Warrant('finite_computation',
             'exact rational check on independent split, nonindependent human-written verification implementation',scope))
        status='F_LOCAL_OBSERVATION'
    return {'local_status':status,'universal_status':'I_ONLY',
            'scope':scope,'receipts':tuple(world.receipts)}


PINNED_SOURCES=('mathal001/nunumathal.py','fir001/fir.py',
                'contractdiscovery001/contractdiscovery.py')


def pins(root: Path) -> tuple[tuple[str,str],...]:
    root=Path(root).resolve(strict=True)
    checks=[]
    for rel in PINNED_SOURCES:
        file=root/rel
        if (not file.is_file() or file.is_symlink() or
                not file.resolve().is_relative_to(root)):
            raise ContractRefusal('HOLD_SOURCE_NOT_REGULAR:'+rel)
        checks.append((rel,sha256(file.read_bytes()).hexdigest()))
    return tuple(checks)


CHILD='''"""Pinned executable finite-graph contract child; local-only witness."""
import argparse,json,sys
from hashlib import sha256
from pathlib import Path
p=argparse.ArgumentParser()
p.add_argument('--source-root',required=True)
p.add_argument('--index',type=int,default=0)
p.add_argument('--missing',default='u0')
a=p.parse_args()
root=Path(a.source_root).resolve(strict=True)
expected=json.loads(__PINS__)
for rel,digest in expected:
    path=root/rel
    if not path.is_file() or path.is_symlink() or sha256(path.read_bytes()).hexdigest()!=digest:
        print(json.dumps({'status':'HOLD_SOURCE_DRIFT','source':rel}));sys.exit(0)
sys.path.insert(0,str(root/'contractdiscovery001'))
from contractdiscovery import Discovery,MissingPortAdapter,CHANNELS,trials,measure,independently_measure,discover
coeff=tuple(json.loads(__RELATION__))
if len(coeff)!=5 or not all(type(x) is int for x in coeff):
    print(json.dumps({'status':'HOLD_CHILD_CONTRACT_INVALID'}));sys.exit(0)
verified=discover(trials('train'),trials('validation'))
if verified.relation!=coeff:
    print(json.dumps({'status':'HOLD_CHILD_NOT_REPLAYED'}));sys.exit(0)
if a.index<0 or a.index>=len(trials('test')):
    print(json.dumps({'status':'HOLD_CHILD_INDEX'}));sys.exit(0)
fixture=trials('test')[a.index]
reading=measure(fixture)
contract=verified
try:
    adapter=MissingPortAdapter(contract,a.missing)
    partial={label:reading[i] for i,label in enumerate(CHANNELS) if label!=a.missing}
    response=adapter.reconstruct(partial)
    independent=independently_measure(fixture)
    print(json.dumps({'status':'F_LOCAL_REPLAY' if independent==reading and
                      response['value']==reading[CHANNELS.index(a.missing)] else 'HOLD_RECONSTRUCTION_MISMATCH',
                      'derived':response['value'],'observed':reading[CHANNELS.index(a.missing)],
                      'independent_instrument_agrees':independent==reading,
                      'external_actions':0,'automatic_repo_edits':0},sort_keys=True))
except (ValueError,TypeError) as e:
    print(json.dumps({'status':str(e).split(':')[0], 'external_actions':0}))
'''


def build_child(root: Path, output: Path, discovery: Discovery) -> Path:
    if discovery.relation is None:
        raise ContractRefusal('HOLD_NO_CONTRACT_TO_BUILD')
    # A caller cannot forge a plausible tuple of coefficients into a child.
    # Reconstruct the pinned training/validation evidence before building.
    reference=discover(trials('train'),trials('validation'))
    if (discovery.relation!=reference.relation or
            discovery.train_digest!=reference.train_digest or
            discovery.validation_digest!=reference.validation_digest or
            discovery.status!=reference.status):
        raise ContractRefusal('HOLD_UNVERIFIED_CONTRACT_BUILD')
    checks=pins(root)
    output=Path(output)
    output.mkdir(parents=True,exist_ok=True)
    child=output/'learned_graph_contract.py'
    digest_file=output/'learned_graph_contract.sha256'
    if any(x.exists() or x.is_symlink() for x in (child,digest_file)):
        raise FileExistsError('HOLD_WILL_NOT_OVERWRITE_CHILD')
    source=CHILD.replace('__PINS__',repr(json.dumps(checks)))
    source=source.replace('__RELATION__',repr(json.dumps(discovery.relation)))
    child.write_text(source,encoding='utf8')
    digest_file.write_text(sha256(child.read_bytes()).hexdigest()+'\n',encoding='ascii')
    return child


def run_child(child: Path, root: Path, missing: str, index: int = 0) -> dict:
    child=Path(child)
    digest_file=child.with_suffix('.sha256')
    if (not child.is_file() or child.is_symlink()
            or not digest_file.is_file() or digest_file.is_symlink()):
        return {'status':'HOLD_CHILD_MISSING_OR_SYMLINK'}
    if digest_file.read_text().strip()!=sha256(child.read_bytes()).hexdigest():
        return {'status':'HOLD_CHILD_TAMPER'}
    try:
        process=subprocess.run([sys.executable,str(child),'--source-root',str(root),
                    '--missing',missing,'--index',str(index)],capture_output=True,
                    text=True,timeout=15,cwd=child.parent)
    except subprocess.TimeoutExpired:
        return {'status':'HOLD_CHILD_TIMEOUT'}
    if process.returncode:
        return {'status':'HOLD_CHILD_PROCESS_ERROR','stderr':process.stderr[-300:]}
    try:
        return json.loads(process.stdout)
    except json.JSONDecodeError:
        return {'status':'HOLD_CHILD_OUTPUT_NOT_JSON'}


def demonstration(root: Path=ROOT) -> dict:
    discovery=discover(trials('train'),trials('validation'))
    holdout=test_heldout(discovery,trials('test'))
    ood=test_heldout(discovery,trials('ood'))
    baseline=exhaustive_classical_control(measure(t) for t in trials('train'))
    import tempfile
    with tempfile.TemporaryDirectory(prefix='motif-contract-child-') as directory:
        child=build_child(root,Path(directory),discovery)
        can=next(x for x,c in zip(CHANNELS,discovery.relation) if c)
        impossible=next(x for x,c in zip(CHANNELS,discovery.relation) if not c)
        working=run_child(child,root,can)
        impossible_result=run_child(child,root,impossible)
    return {'experiment':'CONTRACT-DISCOVERY-001',
        'question':'What mathematical connection do these five anonymous cartridge output channels satisfy?',
        'next_questions':tuple(r['question'] for r in discovery.receipts[-2:]),
        'probes_executed':discovery.inspections,'rank':discovery.rank,
        'candidate_integer_relation':discovery.relation,
        'identified_basis_count':discovery.alternatives,
        'zero_coefficient_ports':tuple(x for x,c in zip(CHANNELS,discovery.relation) if not c),
        'training_digest':discovery.train_digest,'validation_digest':discovery.validation_digest,
        'classical_brute_force_agrees':baseline==(discovery.relation,),
        'test':holdout,'ood_unseen_operations':ood,
        'FIR':{'local_status':fir_record(discovery,holdout)['local_status'],
               'universal_status':fir_record(discovery,holdout)['universal_status']},
        'child':working,'underidentified_child':impossible_result,
        'external_actions':0,'unrestricted_contract_discovery':False,
        'automatic_repo_changes':False,
        'generalization_status':'HOLD_UNPROVEN_OUTSIDE_DECLARED_FINITE_GRAPH_FAMILY',
        'next_frontier':'Find relationships that are not linear, or infer operational meaning from independent measurements.'}


if __name__=='__main__':
    print(json.dumps(demonstration(),indent=2,sort_keys=True))
