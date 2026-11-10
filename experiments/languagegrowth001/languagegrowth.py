"""MOTIF LANGUAGE-GROWTH-001: repair a finite mathematical grammar after falsification.

The agent receives graphs and outcome observations for edge addition. It first
tries a frozen existing query grammar; a contradiction motivates typed operator
proposals. It executes a bounded search over three explicit language extensions,
keeps only proposals justified on separate validation data, and emits an
inspectable executable child. No new universal semantics or general model
invention is claimed; the meta-grammar was authored for this experiment.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from hashlib import sha256
from itertools import combinations
from pathlib import Path
from random import Random
from collections import Counter
from math import log2
import json
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
for dirname in ('featurefrontier001','contractfrontier002','contractdiscovery001','mathal001','fir001'):
    if str(ROOT/dirname) not in sys.path:
        sys.path.insert(0,str(ROOT/dirname))
from nunumathal import Graph
from contractfrontier import Probe, adjacent
from contractdiscovery import apply
from featurefrontier import PROGRAMS as ORIGINAL_GRAMMAR, ATOM_TYPES

class LanguageRefusal(ValueError):
    pass


@dataclass(frozen=True)
class Experiment:
    key: str
    probe: Probe
    split: str

    def __post_init__(self):
        if not self.key or self.split not in {'train','validation','test','ood'} or self.probe.split!=self.split:
            raise LanguageRefusal('HOLD_EVENT_SPLIT')


def count_four_cycles(graph: Graph) -> int:
    """Outcome measurement by enumerating vertex quadruples and 3 distinct cycles.

    Crucially, the learner never sees this code as a candidate expression.
    """
    total=0
    edges=graph.edges
    for a,b,c,d in combinations(sorted(graph.vertices),4):
        for cycle in ((a,b,c,d),(a,b,d,c),(a,c,b,d)):
            if all(tuple(sorted((cycle[i],cycle[(i+1)%4]))) in edges for i in range(4)):
                total+=1
    return total


def path_three_reference(graph:Graph,a:str,b:str)->int:
    """Independent strong classical baseline, not used by synthesis."""
    return sum(1 for x in adjacent(graph,a) for y in adjacent(graph,b)
               if x!=y and tuple(sorted((x,y))) in graph.edges)


def measured_outcome(experiment: Experiment) -> int:
    """Reveal after the experiment was chosen; no feature labels supplied."""
    g=experiment.probe.graph
    return count_four_cycles(apply(experiment.probe.trial()))-count_four_cycles(g)


def _random_experiment(split:str,index:int,rng:Random,size:int)->Experiment:
    names=[f'{split}q{index}v{k}' for k in range(size)]
    a,b=names[:2]
    edges=set()
    mode=index%5
    # 3-path rich families and random cross-links, with an absent a--b edge.
    if mode in (0,1,2):
        middle=names[2:]
        left=middle[:max(1,len(middle)//2)]
        right=middle[max(1,len(middle)//2):]
        for x in left:
            if rng.random()<.95: edges.add(tuple(sorted((a,x))))
        for y in right:
            if rng.random()<.95: edges.add(tuple(sorted((b,y))))
        for x in left:
            for y in right:
                if rng.random() < (.9 if mode==0 else .57 if mode==1 else .26):
                    edges.add(tuple(sorted((x,y))))
    else:
        rate=.30 if mode==3 else .52
        for x,y in combinations(names,2):
            if (x,y)!=(a,b) and rng.random()<rate:
                edges.add((x,y))
    graph=Graph.build(names,edges)
    p=Probe(f'{split}:{index}',graph,a,b,split)
    return Experiment(p.key,p,split)


def trials(split:str,size:int=36)->tuple[Experiment,...]:
    if split not in {'train','validation','test','ood'} or not 1<=size<=200:
        raise LanguageRefusal('HOLD_FIXTURE_REQUEST')
    rng=Random(int.from_bytes(sha256(f'languagegrowth001|{split}|v1'.encode()).digest()[:8],'big'))
    cases=[]
    for i in range(size):
        if split=='ood':
            n=rng.randint(11,16)
        else:
            n=rng.randint(6,10)
        cases.append(_random_experiment(split,i,rng,n))
    return tuple(cases)


@dataclass(frozen=True)
class Query:
    """Data-only expression assembled from generic atom selection + aggregation."""
    atoms: tuple[tuple[str,str],...]
    aggregator: str
    coefficient: int = 1
    intercept: int = 0

    def __post_init__(self):
        if (not 1<=len(self.atoms)<=3 or tuple(sorted(self.atoms))!=self.atoms
                or len(set(self.atoms))!=len(self.atoms)
                or any(atom not in ATOM_TYPES for atom in self.atoms)
                or self.aggregator not in {'COUNT_X','COUNT_Y','COUNT_XY','EXISTS_XY'}
                or self.coefficient not in (-1,1) or self.intercept not in (-1,0,1)):
            raise LanguageRefusal('HOLD_QUERY_GRAMMAR')
        if self.aggregator=='COUNT_X' and not any('x' in atom for atom in self.atoms):
            raise LanguageRefusal('HOLD_UNBOUND_VARIABLE')
        if self.aggregator=='COUNT_Y' and not any('y' in atom for atom in self.atoms):
            raise LanguageRefusal('HOLD_UNBOUND_VARIABLE')
        if self.aggregator in {'COUNT_XY','EXISTS_XY'} and not all(
                any(v in atom for atom in self.atoms) for v in ('x','y')):
            raise LanguageRefusal('HOLD_UNBOUND_VARIABLE')

    def evaluate(self,p:Probe)->int:
        g=p.graph
        results=set()
        has_x=any('x' in atom for atom in self.atoms)
        has_y=any('y' in atom for atom in self.atoms)
        for x in (g.vertices if has_x else (None,)):
            for y in (g.vertices if has_y else (None,)):
                env={'a':p.a,'b':p.b,'x':x,'y':y}
                if all(env[u]!=env[v] and tuple(sorted((env[u],env[v]))) in g.edges
                       for u,v in self.atoms):
                    if self.aggregator=='COUNT_X':results.add(x)
                    elif self.aggregator=='COUNT_Y':results.add(y)
                    elif self.aggregator=='COUNT_XY':results.add((x,y))
                    else:results.add(True)
        return self.coefficient*len(results)+self.intercept

    def text(self)->str:
        return f'{self.coefficient}*{self.aggregator}('+','.join(f'E({u},{v})' for u,v in self.atoms)+f') {self.intercept:+d}'


# Meta-language mutation candidates are generic aggregations; NO explicit four-
# cycle predicate or path-of-length-three symbol is supplied.
PATCHES={
    'COUNT_OTHER_BINDING':('COUNT_Y',),
    'PRESENCE_OF_TWO_BINDINGS':('EXISTS_XY',),
    'COUNT_BINDING_PAIRS':('COUNT_XY',),
}

def programs_for_patch(name:str)->tuple[Query,...]:
    if name not in PATCHES:
        raise LanguageRefusal('HOLD_UNKNOWN_GRAMMAR_EDIT')
    queries=[]
    for n in (1,2,3):
        for atoms in combinations(ATOM_TYPES,n):
            for aggregator in PATCHES[name]:
                try:
                    queries.append(Query(atoms,aggregator))
                except LanguageRefusal:
                    continue
    return tuple(queries)


def _digest(evidence)->str:
    return sha256(json.dumps(tuple(evidence),separators=(',',':'),default=str).encode()).hexdigest()[:20]


def existing_predictions(experiments:tuple[Experiment,...],limit:int|None=None)->tuple[tuple[int,...],...]:
    """The original feature grammar, evaluated against the new output family."""
    return tuple(tuple(expr(e.probe) for expr in ORIGINAL_GRAMMAR) for e in
                 (experiments if limit is None else experiments[:limit]))


def diagnose(experiments:tuple[Experiment,...],budget:int=8)->dict:
    """Observe a bounded prefix: strong CONTRADICTION differs from ambiguity.

    The finite grammar can be falsified on observed data; no proof about all
    mathematical languages is asserted.
    """
    if not experiments or not 1<=budget<=len(experiments) or len({e.key for e in experiments})!=len(experiments):
        raise LanguageRefusal('HOLD_DIAGNOSTIC_INPUT')
    survivors=set(range(len(ORIGINAL_GRAMMAR)))
    receipts=[]
    for e,predictions in zip(experiments[:budget],existing_predictions(experiments,budget)):
        y=measured_outcome(e)
        before=len(survivors)
        survivors={i for i in survivors if predictions[i]==y}
        receipts.append({'question':'Can the currently available language explain this measurement?',
                         'probe':e.key,'observed':y,'remaining_before':before,
                         'remaining_after':len(survivors),'external_actions':0})
        if not survivors:
            break
    return {'status':'HOLD_FINITE_GRAMMAR_FALSIFIED' if not survivors else 'I_OLD_GRAMMAR_NOT_FALSIFIED',
            'inspections':len(receipts),'remaining':len(survivors),
            'receipts':tuple(receipts),
            'exhaustive_old_candidates':len(ORIGINAL_GRAMMAR),
            'evidence_digest':_digest((r['probe'],r['observed']) for r in receipts),
            'not_a_universal_impossibility_proof':True}


@dataclass(frozen=True)
class Growth:
    status: str
    operator: str|None
    formula: Query|None
    observations: int
    examined: int
    calibration_digest: str
    validation_digest: str
    receipts: tuple[dict,...]

    @property
    def usable(self)->bool:
        return self.status=='I_PATCH_VALIDATED' and self.formula is not None


def _partition_entropy(values)->float:
    freq=Counter(values);n=sum(freq.values())
    return -sum((m/n)*log2(m/n) for m in freq.values()) if n else 0.0


def grow(training:tuple[Experiment,...], validation:tuple[Experiment,...],
         *,budget:int=12, allowed_patches:tuple[str,...]=tuple(PATCHES),
         selection:str='active',seed:int=7)->Growth:
    """Try current grammar first, then enumerate expansions and actively probe.

    Validation is read only AFTER operator selection; no heldout input. Input
    pools are authored synthetic graph families, not external experiments.
    """
    if (len(training)<4 or not validation or not 1<=budget<=len(training)
            or selection not in {'active','random'} or not allowed_patches
            or any(p not in PATCHES for p in allowed_patches)
            or len(set(allowed_patches))!=len(allowed_patches)
            or len({e.key for e in training})!=len(training)
            or len({e.key for e in validation})!=len(validation)
            or {e.key for e in training}&{e.key for e in validation}):
        raise LanguageRefusal('HOLD_DISCOVERY_INPUT')
    diagnosis=diagnose(training,min(8,len(training)))
    receipts=list(diagnosis['receipts'])
    if diagnosis['status']!='HOLD_FINITE_GRAMMAR_FALSIFIED':
        return Growth('HOLD_NO_PROVEN_LANGUAGE_GAP',None,None,diagnosis['inspections'],
                      len(ORIGINAL_GRAMMAR),diagnosis['evidence_digest'],'',tuple(receipts))
    # A higher-level program enumerates *candidate language modifications*.
    # The alteration itself isn't user-supplied as a target answer.
    candidates=tuple((patch,q) for patch in allowed_patches for q in programs_for_patch(patch))
    if not candidates:
        return Growth('HOLD_NO_LICENSED_PATCH',None,None,diagnosis['inspections'],0,
                      diagnosis['evidence_digest'],'',tuple(receipts))
    candidates=tuple(sorted(candidates,key=lambda x:(x[0],x[1].text())))
    model_cache={e.key:tuple(q.evaluate(e.probe) for _,q in candidates) for e in training}
    versions=set(range(len(candidates)))
    evidence=[(r['probe'],r['observed']) for r in receipts]
    # Reuse diagnostic readings; do NOT query the simulation a second time.
    observations_by_key=dict(evidence)
    for key,y in evidence:
        pred=model_cache[key]
        versions={i for i in versions if pred[i]==y}
    remaining=[e for e in training if e.key not in observations_by_key]
    rng=Random(seed)
    while remaining and len(evidence)<budget and len(versions)>1:
        if selection=='active':
            e=max(remaining,key=lambda e:(_partition_entropy(model_cache[e.key][i] for i in versions),-int(e.key.rsplit(':',1)[-1])))
        else:
            e=rng.choice(remaining)
        remaining.remove(e)
        y=measured_outcome(e)  # first read of this intervention is after selection
        evidence.append((e.key,y))
        before=len(versions)
        versions={i for i in versions if model_cache[e.key][i]==y}
        receipts.append({'question':'Which experiment distinguishes the proposed new mathematical operators?',
                         'probe':e.key,'observed':y,'remaining_before':before,
                         'remaining_after':len(versions),'external_actions':0})
        if not versions:
            break
        # Remaining syntactic variants may be equivalent over all other TRAIN
        # inputs. Do not pay for observations that cannot distinguish them.
        if len(evidence)>=3 and all(
                len({model_cache[item.key][i] for i in versions})==1
                for item in remaining):
            receipts.append({'question':'Can any remaining permitted experiment distinguish the surviving operators?',
                             'action':'STOP_OBSERVATIONAL_EQUIVALENCE_ON_TRAIN_POOL',
                             'survivors':len(versions),'external_actions':0})
            break
    train_digest=_digest(evidence)
    if not versions:
        return Growth('HOLD_NO_SUPPORTED_OPERATOR',None,None,len(evidence),len(candidates),
                      train_digest,'',tuple(receipts))
    # Resolve aliases across all *training inputs*, not by treating syntax as
    # semantic authority. A best-fit choice under finite budget remains I.
    representatives=sorted((candidates[i] for i in versions),key=lambda x:(len(x[1].atoms),x[0],x[1].text()))
    patch,formula=representatives[0]
    if any(formula.evaluate(e.probe)!=measured_outcome(e) for e in validation):
        return Growth('HOLD_VALIDATION_COUNTEREXAMPLE',None,None,len(evidence),len(candidates),
                      train_digest,_digest((e.key,measured_outcome(e)) for e in validation),tuple(receipts))
    valid_digest=_digest((e.key,measured_outcome(e)) for e in validation)
    receipts.append({'question':'Does the frozen new operator survive independent validation?',
                     'action':'VALIDATE_FROZEN_PATCH','tested':len(validation),
                     'patch':patch,'expression':formula.text(),'status':'F_LOCAL_EXACT_REPLAY',
                     'validation_digest':valid_digest})
    return Growth('I_PATCH_VALIDATED',patch,formula,len(evidence),len(candidates),
                  train_digest,valid_digest,tuple(receipts))


def predict(growth:Growth,e:Experiment)->int:
    if not growth.usable:
        raise LanguageRefusal('HOLD_UNVERIFIED_PATCH')
    return growth.formula.evaluate(e.probe)


def test(growth:Growth,heldout:tuple[Experiment,...])->dict:
    if not growth.usable or not heldout:
        return {'status':'HOLD_NO_MODEL_OR_HOLDOUT'}
    actual=tuple(measured_outcome(e) for e in heldout)
    predictions=tuple(predict(growth,e) for e in heldout)
    independent=tuple(path_three_reference(e.probe.graph,e.probe.a,e.probe.b) for e in heldout)
    return {'cases':len(heldout),'matched':sum(a==b for a,b in zip(actual,predictions)),
            'independent_algorithm_matches_outcome':sum(a==b for a,b in zip(actual,independent)),
            'constant_zero_matches':sum(x==0 for x in actual),
            'status':'F_LOCAL_FINITE_REPLAY' if predictions==actual==independent else 'HOLD_COUNTEREXAMPLE',
            'evidence_digest':_digest((e.key,y) for e,y in zip(heldout,actual)),
            'unrestricted_correctness_claim':False}


def ablation(training,validation)->dict:
    controls={}
    for forbidden in PATCHES:
        allowed=tuple(p for p in PATCHES if p!=forbidden)
        result=grow(training,validation,allowed_patches=allowed)
        controls[forbidden]={'status':result.status,'selected':result.operator}
    return controls


def emit_fir(growth:Growth, heldout:dict)->dict:
    from fir import FIRWorld,Claim,Warrant
    world=FIRWorld('finite undirected synthetic graphs','bounded grammar expansion')
    broad=Claim('The invented operation is universally meaningful and trustworthy','unbounded')
    local=Claim('The frozen operator matched these exact graph measurements','finite:'+str(heldout.get('evidence_digest')))
    world.propose(broad);world.propose(local)
    if growth.usable and heldout.get('status')=='F_LOCAL_FINITE_REPLAY':
        world.admit(local,Warrant('finite_computation','verified via local finite graph measurements',local.scope))
    return {'local_role':'F_LOCAL' if local in world.facts else 'I',
            'universal_role':'I','receipts':tuple(world.receipts)}


PINNED=('fir001/fir.py','mathal001/nunumathal.py','contractdiscovery001/contractdiscovery.py',
        'contractfrontier002/contractfrontier.py','featurefrontier001/featurefrontier.py',
        'languagegrowth001/languagegrowth.py')


def pins(root:Path=ROOT)->tuple[tuple[str,str],...]:
    root=Path(root).resolve(strict=True)
    rows=[]
    for rel in PINNED:
        f=root/rel
        if not f.is_file() or f.is_symlink() or not f.resolve().is_relative_to(root):
            raise LanguageRefusal('HOLD_SOURCE_MISSING_OR_LINKED:'+rel)
        rows.append((rel,sha256(f.read_bytes()).hexdigest()))
    return tuple(rows)


CHILD='''"""Generated executable operator extension; read-only and synthetic."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
p=argparse.ArgumentParser();p.add_argument('--source-root',required=True)
p.add_argument('--index',type=int,default=0);args=p.parse_args()
root=Path(args.source_root).resolve(strict=True)
for rel,digest in json.loads(__PINS__):
    f=root/rel
    if not f.is_file() or f.is_symlink() or sha256(f.read_bytes()).hexdigest()!=digest:
        print(json.dumps({'status':'HOLD_SOURCE_DRIFT','source':rel}));sys.exit(0)
sys.path.insert(0,str(root/'languagegrowth001'))
from languagegrowth import Query,Growth,trials,grow,predict,measured_outcome
if args.index<0 or args.index>=30:
    print(json.dumps({'status':'HOLD_INVALID_INDEX'}));sys.exit(0)
spec=json.loads(__OPERATOR__)
q=Query(tuple(tuple(x) for x in spec['atoms']),spec['aggregator'],spec['coefficient'],spec['intercept'])
replayed=grow(trials('train'),trials('validation'))
if not replayed.usable or replayed.formula!=q or replayed.calibration_digest!=spec['calibration_digest']:
    print(json.dumps({'status':'HOLD_UNVERIFIED_OPERATOR'}));sys.exit(0)
case=trials('test',30)[args.index]
a=predict(replayed,case);b=measured_outcome(case)
print(json.dumps({'status':'F_LOCAL_CHILD_REPLAY' if a==b else 'HOLD_CHILD_COUNTEREXAMPLE',
                  'predicted':a,'observed':b,'operator':replayed.operator,
                  'scope':'synthetic graph fixture','external_actions':0,'source_edits':0},sort_keys=True))
'''


def build_child(root:Path,output:Path,growth:Growth)->Path:
    if not growth.usable:
        raise LanguageRefusal('HOLD_UNVERIFIED_CHILD')
    frozen=grow(trials('train'),trials('validation'))
    if (growth.formula!=frozen.formula or growth.calibration_digest!=frozen.calibration_digest
            or growth.validation_digest!=frozen.validation_digest):
        raise LanguageRefusal('HOLD_CHILD_REPLAY_MISMATCH')
    checks=pins(root)
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    child=output/'invented_operator_child.py'
    manifest=output/'invented_operator_child.sha256'
    if any(p.exists() or p.is_symlink() for p in (child,manifest)):
        raise FileExistsError('HOLD_REFUSE_TO_OVERWRITE')
    spec={'atoms':growth.formula.atoms,'aggregator':growth.formula.aggregator,
          'coefficient':growth.formula.coefficient,'intercept':growth.formula.intercept,
          'calibration_digest':growth.calibration_digest}
    code=CHILD.replace('__PINS__',repr(json.dumps(checks)))
    code=code.replace('__OPERATOR__',repr(json.dumps(spec)))
    child.write_text(code,encoding='utf8')
    manifest.write_text(sha256(child.read_bytes()).hexdigest()+'\n')
    return child


def run_child(child:Path,root:Path,index:int=0)->dict:
    child=Path(child);manifest=child.with_suffix('.sha256')
    if (not child.is_file() or child.is_symlink() or not manifest.is_file()
            or manifest.is_symlink()):
        return {'status':'HOLD_CHILD_MISSING_OR_LINKED'}
    if manifest.read_text().strip()!=sha256(child.read_bytes()).hexdigest():
        return {'status':'HOLD_CHILD_TAMPER'}
    try:
        proc=subprocess.run([sys.executable,str(child),'--source-root',str(root),'--index',str(index)],
                            cwd=child.parent,timeout=30,capture_output=True,text=True)
    except subprocess.TimeoutExpired:
        return {'status':'HOLD_CHILD_TIMEOUT'}
    if proc.returncode:
        return {'status':'HOLD_CHILD_FAILED','stderr':proc.stderr[-400:]}
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError:
        return {'status':'HOLD_CHILD_NON_JSON'}


def demonstrate()->dict:
    import tempfile
    train,valid=trials('train'),trials('validation')
    initial=diagnose(train)
    result=grow(train,valid)
    heldout=test(result,trials('test',30))
    ood=test(result,trials('ood',30))
    with tempfile.TemporaryDirectory(prefix='motif-lang-grow-') as tmp:
        child=build_child(ROOT,Path(tmp),result)
        execution=run_child(child,ROOT,0)
    return {'experiment':'LANGUAGE-GROWTH-001',
            'initial_diagnostic':{'status':initial['status'],'inspections':initial['inspections'],
                                  'survivors':initial['remaining']},
            'searched_operator_edits':tuple(PATCHES),
            'selected_edit':result.operator,'selected_program':result.formula.text() if result.formula else None,
            'training_interventions':result.observations,'new_candidates':result.examined,
            'validation_status':result.status,'test':heldout,'ood':ood,
            'child':execution,'FIR':{k:v for k,v in emit_fir(result,heldout).items() if k!='receipts'},
            'real_world_actions':0,'auto_repo_edits':0,'general_algorithm_invention':False,
            'next_question':'Can the proposed operator be derived from counterexamples without a preauthorized meta-grammar?'}

if __name__=='__main__':
    print(json.dumps(demonstrate(),indent=2,sort_keys=True))
