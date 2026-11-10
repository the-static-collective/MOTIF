"""OPERATOR-INVENTION-001: synthesize actual loop-based operator code from graph probes.

The target outputs are observed *after* choosing each graph intervention. No
prewritten implementation of the new COUNT_BINDING_PAIRS operator, and no
labelled source-to-target mappings, enter the candidate generator. The typed
compiler uses FOR vertices, EDGE tests, optional DISTINCT, and ADD_ONE.
This finite, researcher-authored grammar is NOT general code or math invention.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from hashlib import sha256
from itertools import combinations
from math import log2
from pathlib import Path
from random import Random
import ast
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
for module in ('languagegrowth001','featurefrontier001','contractfrontier002','contractdiscovery001','mathal001','fir001'):
    if str(ROOT/module) not in sys.path:
        sys.path.insert(0,str(ROOT/module))
from languagegrowth import Experiment, trials, measured_outcome, diagnose, path_three_reference
from contractfrontier import Probe, observed_outcome


class OperatorRefusal(ValueError):
    """Fail closed on unsupported, unverified, or ambiguous program proposals."""


EDGE_ATOMS = tuple(combinations(('a','b','x','y'),2))


@dataclass(frozen=True)
class Program:
    """Typed AST for nested loops, conjunction, and accumulator increment.

    There is no primitive COUNT_XY or path-three operator in this grammar.
    """
    binders: tuple[str, ...]
    atoms: tuple[tuple[str,str], ...]
    distinct: bool = False

    def __post_init__(self):
        if (self.binders not in (('x',),('x','y')) or
                not 1 <= len(self.atoms) <= 3 or self.atoms != tuple(sorted(self.atoms)) or
                len(set(self.atoms)) != len(self.atoms) or
                any(atom not in EDGE_ATOMS for atom in self.atoms) or
                any(any(v not in {'a','b',*self.binders} for v in atom) for atom in self.atoms) or
                not all(any(b in atom for atom in self.atoms) for b in self.binders) or
                type(self.distinct) is not bool or
                (self.distinct and len(self.binders)!=2)):
            raise OperatorRefusal('HOLD_TYPED_OPERATOR_GRAMMAR')

    @property
    def complexity(self) -> tuple[int,int,int]:
        return len(self.binders),len(self.atoms),int(self.distinct)

    def name(self) -> str:
        return f"FOR({','.join(self.binders)}) IF({' & '.join('E'+repr(a) for a in self.atoms)}),DISTINCT={self.distinct} THEN INC"

    def interpret(self, probe: Probe) -> int:
        """Execute the AST with a data interpreter, not generated Python code."""
        g = probe.graph
        if probe.a==probe.b or probe.a not in g.vertices or probe.b not in g.vertices:
            raise OperatorRefusal('HOLD_ENDPOINTS')
        answer=0
        verts=sorted(g.vertices)
        for x in verts:
            for y in (verts if len(self.binders)==2 else (None,)):
                if self.distinct and x==y:
                    continue
                env={'a':probe.a,'b':probe.b,'x':x,'y':y}
                if all(env[u]!=env[v] and tuple(sorted((env[u],env[v]))) in g.edges
                       for u,v in self.atoms):
                    answer += 1
        return answer

    def emit_source(self, function_name: str='constructed_operator') -> str:
        """Actual Python source assembled from primitive syntax and checked AST.

        Caller controls neither variable names nor statements, imports, code,
        field expressions, or function name. This is executable code synthesis
        within a narrow fixed grammar (not arbitrary source generation).
        """
        if function_name!='constructed_operator':
            raise OperatorRefusal('HOLD_EXECUTABLE_NAME')
        terms=[f"(env[{u!r}] != env[{v!r}] and tuple(sorted((env[{u!r}], env[{v!r}]))) in edges)"
               for u,v in self.atoms]
        condition=' and '.join(terms)
        if self.distinct:
            condition='(x != y) and '+condition
        rows=[
            'def constructed_operator(graph, a, b):',
            '    if a == b or a not in graph.vertices or b not in graph.vertices:',
            "        raise ValueError('HOLD_ENDPOINTS')",
            '    vertices = tuple(sorted(graph.vertices))',
            '    edges = graph.edges',
            '    count = 0',
            '    for x in vertices:',
        ]
        if len(self.binders)==2:
            rows.extend(('        for y in vertices:',
                         "            env = {'a': a, 'b': b, 'x': x, 'y': y}",
                         f'            if {condition}:',
                         '                count += 1'))
        else:
            rows.extend(("        env = {'a': a, 'b': b, 'x': x}",
                         f'        if {condition}:',
                         '            count += 1'))
        rows.append('    return count')
        result='\n'.join(rows)+'\n'
        tree=ast.parse(result)
        assert len(tree.body)==1 and isinstance(tree.body[0],ast.FunctionDef)
        return result


def grammar(*, allow_two_binders: bool=True, allow_distinct: bool=True) -> tuple[Program, ...]:
    models=[]
    for binders in (('x',),('x','y')):
        if len(binders)==2 and not allow_two_binders:
            continue
        for k in (1,2,3):
            for atoms in combinations(EDGE_ATOMS,k):
                for distinct in ((False,True) if len(binders)==2 and allow_distinct else (False,)):
                    try:models.append(Program(binders,atoms,distinct))
                    except OperatorRefusal: pass
    return tuple(sorted(models,key=lambda p:(p.complexity,p.name())))


PROGRAMS=grammar()


def target(experiment: Experiment, task: str) -> int:
    """Oracle instruments are separate old-source routines; never learned code."""
    if task=='four_cycles':return measured_outcome(experiment)
    if task=='triangles':return observed_outcome(experiment.probe)[0]
    raise OperatorRefusal('HOLD_UNKNOWN_TASK')


def _fingerprint(records) -> str:
    return sha256(json.dumps(tuple(records),sort_keys=True,default=str).encode()).hexdigest()[:24]


def entropy(predictions) -> float:
    counts=Counter(predictions);n=sum(counts.values())
    return -sum((k/n)*log2(k/n) for k in counts.values()) if n else 0.0


@dataclass(frozen=True)
class Discovery:
    task: str
    program: Program|None
    status: str
    interventions: int
    candidate_count: int
    survivor_count: int
    training_digest: str
    validation_digest: str
    receipts: tuple[dict,...]

    @property
    def usable(self) -> bool:
        return self.status=='I_EXECUTABLE_OPERATOR_VALIDATED' and self.program is not None


def discover(train:tuple[Experiment,...],validation:tuple[Experiment,...],*,task:str='four_cycles',
             budget:int=12,selection:str='active',seed:int=7,
             candidates:tuple[Program,...]=PROGRAMS) -> Discovery:
    """Select interventions without seeing oracle outputs until after selection.

    Validation is only read after freeze; a failed candidate is not retuned.
    Ambiguous programs may select a canonical *simple* expression, never claim
    universal uniqueness. A budget failure abstains.
    """
    if (task not in {'four_cycles','triangles'} or selection not in {'active','random'} or
            not train or not validation or type(budget) is not int or not 1<=budget<=len(train) or not candidates or
            len({e.key for e in train})!=len(train) or len({e.key for e in validation})!=len(validation)
            or {e.key for e in train}&{e.key for e in validation}
            or any(type(c) is not Program for c in candidates)):
        raise OperatorRefusal('HOLD_DISCOVERY_CONTRACT')
    rng=Random(seed)
    # Only graph *inputs* and the candidate programs are visible before probe.
    cache={e.key:tuple(p.interpret(e.probe) for p in candidates) for e in train}
    available=list(train)
    remaining=set(range(len(candidates)))
    receipts=[]
    evidence=[]
    for step in range(budget):
        if selection=='active':
            entry=min(available,key=lambda e:(-entropy(cache[e.key][j] for j in remaining),e.key))
        else:
            entry=rng.choice(available)
        available.remove(entry)
        result=target(entry,task)  # first oracle reveal, post-selection
        predictions=cache[entry.key]
        before=len(remaining)
        remaining={j for j in remaining if predictions[j]==result}
        evidence.append((entry.key,result))
        receipts.append({'next_question':'Which graph transformation most distinguishes candidate loop programs?',
                         'operation':'EXECUTE_OBSERVED_GRAPH_PROBE','probe':entry.key,
                         'hypotheses_before':before,'hypotheses_after':len(remaining),
                         'answer':result,'new_real_world_evidence':False})
        if not remaining:
            return Discovery(task,None,'HOLD_NO_PROGRAM_FITS_EVIDENCE',len(evidence),len(candidates),0,
                             _fingerprint(evidence),'',tuple(receipts))
        if (len(evidence)>=3 and all(len({cache[e.key][j] for j in remaining})==1 for e in available)):
            break
    if not remaining:
        raise AssertionError('unreachable')
    if len(evidence) < 3:
        return Discovery(task,None,'HOLD_INSUFFICIENT_INDEPENDENT_INTERVENTIONS',len(evidence),len(candidates),
                         len(remaining),_fingerprint(evidence),'',tuple(receipts))
    # Complexity is a declared inductive bias, not a proof of uniqueness.
    winner=candidates[min(remaining,key=lambda j:(candidates[j].complexity,candidates[j].name()))]
    inspected_validation=[]
    for entry in validation:
        y=target(entry,task)
        inspected_validation.append((entry.key,y))
        if winner.interpret(entry.probe)!=y:
            return Discovery(task,None,'HOLD_VALIDATION_COUNTEREXAMPLE',len(evidence),len(candidates),
                             len(remaining),_fingerprint(evidence),_fingerprint(inspected_validation),tuple(receipts))
    return Discovery(task,winner,'I_EXECUTABLE_OPERATOR_VALIDATED',len(evidence),len(candidates),
                     len(remaining),_fingerprint(evidence),_fingerprint(inspected_validation),
                     tuple(receipts)+({'next_question':'Does the frozen constructed program survive fresh graph worlds?',
                                       'operation':'CHECK_FROZEN_VALIDATION','status':'F_LOCAL_EXACT_REPLAY',
                                       'cases':len(validation),'digest':_fingerprint(inspected_validation)},))


def heldout(model:Discovery, cases:tuple[Experiment,...]) -> dict:
    if not model.usable or not cases:return {'status':'HOLD_UNVERIFIED_MODEL_OR_CASES'}
    matched=0;reference=0;comparison=[]
    for e in cases:
        predicted=model.program.interpret(e.probe)
        measured=target(e,model.task)
        # independent reference from prior authored modules (not a new truth source)
        baseline=(path_three_reference(e.probe.graph,e.probe.a,e.probe.b)
                  if model.task=='four_cycles' else
                  observed_outcome(e.probe)[0])
        matched+=predicted==measured
        reference+=baseline==measured
        comparison.append((e.key,measured))
    return {'cases':len(cases),'matched':matched,'strong_baseline_matches':reference,
            'status':'F_LOCAL_FINITE_REPLAY' if matched==reference==len(cases) else 'HOLD_REGRESSION',
            'digest':_fingerprint(comparison),'general_math_claim':False}


PINNED=('fir001/fir.py','mathal001/nunumathal.py','contractdiscovery001/contractdiscovery.py',
        'contractfrontier002/contractfrontier.py','featurefrontier001/featurefrontier.py',
        'languagegrowth001/languagegrowth.py','operatorinvention001/operatorinvention.py')


def pins(root:Path=ROOT)->tuple[tuple[str,str],...]:
    root=Path(root).resolve(strict=True)
    out=[]
    for rel in PINNED:
        path=root/rel
        if not path.is_file() or path.is_symlink() or not path.resolve().is_relative_to(root):
            raise OperatorRefusal('HOLD_MISSING_OR_LINKED:'+rel)
        out.append((rel,sha256(path.read_bytes()).hexdigest()))
    return tuple(out)


# Generated Python is a literal implementation of the learned loop AST, not
# a closure over a prewritten COUNT_XY evaluator. Source pins are drift checks,
# NOT proof of origin or an isolation/sandbox guarantee.
CHILD='''"""Synthesized loop program; trusted local graph experiment only."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
parser=argparse.ArgumentParser()
parser.add_argument('--source-root',required=True)
parser.add_argument('--index',type=int,default=0)
args=parser.parse_args()
root=Path(args.source_root).resolve(strict=True)
for rel,digest in json.loads(__PINS__):
    path=root/rel
    if not path.is_file() or path.is_symlink() or sha256(path.read_bytes()).hexdigest()!=digest:
        print(json.dumps({'status':'HOLD_SOURCE_DRIFT','file':rel}));sys.exit(0)
sys.path.insert(0,str(root/'languagegrowth001'))
from languagegrowth import trials, path_three_reference
__GENERATED_OPERATOR__
checks=trials('test',30)
if args.index<0 or args.index>=len(checks):
    print(json.dumps({'status':'HOLD_BAD_INDEX'}));sys.exit(0)
entry=checks[args.index]
graph=entry.probe.graph
observed=path_three_reference(graph,entry.probe.a,entry.probe.b)
claimed=constructed_operator(graph,entry.probe.a,entry.probe.b)
print(json.dumps({'status':'F_LOCAL_INDEPENDENT_CHILD_CHECK' if observed==claimed else 'HOLD_COUNTEREXAMPLE',
                  'prediction':claimed,'reference':observed,'probe':entry.key,
                  'real_world_actions':0,'repository_edits':0},sort_keys=True))
'''


def build_child(root:Path,out:Path,model:Discovery)->Path:
    if not model.usable or model.task!='four_cycles':
        raise OperatorRefusal('HOLD_NO_VALIDATED_PROGRAM_FOR_CHILD')
    # Reconfirm exact *calibration* experiment against trusted checked-out source.
    calibration=discover(trials('train',36),trials('validation',24))
    if (model.program!=calibration.program or
        model.training_digest!=calibration.training_digest or
        model.validation_digest!=calibration.validation_digest):
        raise OperatorRefusal('HOLD_FORGED_CALIBRATION')
    checks=pins(root)
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    child=out/'invented_operator.py';digest=out/'invented_operator.sha256'
    if any(x.exists() or x.is_symlink() for x in (child,digest)):
        raise FileExistsError('HOLD_EXISTING_CHILD')
    code=CHILD.replace('__PINS__',repr(json.dumps(checks)))
    code=code.replace('__GENERATED_OPERATOR__',model.program.emit_source())
    ast.parse(code)
    child.write_text(code,encoding='utf8')
    digest.write_text(sha256(child.read_bytes()).hexdigest()+'\n',encoding='ascii')
    return child


def run_child(child:Path,root:Path,index:int=0)->dict:
    child=Path(child);receipt=child.with_suffix('.sha256')
    if (not child.is_file() or child.is_symlink() or not receipt.is_file() or receipt.is_symlink()):
        return {'status':'HOLD_CHILD_MISSING_OR_LINKED'}
    if receipt.read_text().strip()!=sha256(child.read_bytes()).hexdigest():
        return {'status':'HOLD_CHILD_TAMPER'}
    try:
        p=subprocess.run([sys.executable,str(child),'--source-root',str(root),'--index',str(index)],
                         cwd=child.parent,capture_output=True,text=True,timeout=30)
    except subprocess.TimeoutExpired:
        return {'status':'HOLD_CHILD_TIMEOUT'}
    if p.returncode:
        return {'status':'HOLD_CHILD_PROCESS_ERROR','stderr':p.stderr[-300:]}
    try:return json.loads(p.stdout)
    except ValueError:return {'status':'HOLD_CHILD_OUTPUT_NOT_JSON'}


def demonstration() -> dict:
    import tempfile
    train=trials('train',36);val=trials('validation',24)
    diagnosis=diagnose(train)
    model=discover(train,val)
    check=heldout(model,trials('test',30))
    ood=heldout(model,trials('ood',25))
    restricted=discover(train,val,candidates=grammar(allow_two_binders=False))
    with tempfile.TemporaryDirectory(prefix='motif-operator-child-') as tmp:
        child=build_child(ROOT,Path(tmp),model)
        result=run_child(child,ROOT)
    return {'experiment':'OPERATOR-INVENTION-001',
            'old_grammar_diagnosis':diagnosis['status'],
            'problem':'How do I construct a missing executable counting operation from elementary loops?',
            'candidates':model.candidate_count,'probes':model.interventions,
            'program':model.program.name() if model.program else None,
            'generated_python':model.program.emit_source() if model.program else None,
            'status':model.status,'test':check,'ood':ood,
            'single_loop_ablation':restricted.status,'child':result,
            'external_actions':0,'auto_merge':False,'original_graph_modified':False,
            'novel_algorithm_claim':False,
            'next_question':'Can MOTIF learn new control-flow patterns without a human specifying the loop skeleton?'}

if __name__=='__main__':
    print(json.dumps(demonstration(),indent=2,sort_keys=True))
