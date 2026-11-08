"""ADAPTER-INVENTION-001: small, typed program synthesis for a REAL MOTIF port gap.

A bounded DSL is searched against supervised training and validation examples.
The inferred bridge converts MOTIF-003 action rows into SELF-MIRROR-001 Move
records and is then executed by the genuine downstream Policy in a subprocess.
This is finite grammar search, NOT general-purpose code or algorithm invention.
"""
from __future__ import annotations

from dataclasses import dataclass, fields as dataclass_fields
from hashlib import sha256
from pathlib import Path
from random import Random
from typing import Any
import json
import subprocess
import sys

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE/'selfmirror001'))
from selfmirror import Move, Policy

FIELDS = ('operator', 'roles', 'immediate_delta', 'new_affordances',
          'lost_affordances', 'new_skill_facts', 'reachable_after_first_move', 'truncated')
OUTPUTS = ('name', 'immediate', 'affordances', 'reach', 'truncated')

class AdapterRefusal(ValueError):
    """No licensed crossing in the declared source/target worlds."""


@dataclass(frozen=True)
class Expression:
    op: str
    args: tuple[str, ...]

    def __post_init__(self):
        grammar = {
            'field': {(name,) for name in FIELDS},
            'length': {(name,) for name in ('roles','new_affordances','lost_affordances','new_skill_facts')},
            'join_repr': {('operator','roles')},
            'false': {()},
        }
        if self.op not in grammar or self.args not in grammar[self.op]:
            raise AdapterRefusal('unrecognized expression is not executable')

    def evaluate(self, row: dict) -> Any:
        if self.op == 'field':
            return row[self.args[0]]
        if self.op == 'length':
            return len(row[self.args[0]])
        if self.op == 'join_repr':
            return str(row[self.args[0]]) + ':' + repr(tuple(row[self.args[1]]))
        if self.op == 'false':
            return False
        raise AdapterRefusal('unreachable operation')


# This declares a *search language*, not an actual mapping. There is no
# hardcoded assignment from a source field to a destination parameter.
SEARCH = {
    'name': (Expression('field',('operator',)), Expression('join_repr',('operator','roles'))),
    'immediate': tuple(Expression('field',(s,)) for s in
                       ('immediate_delta','reachable_after_first_move')) +
                 tuple(Expression('length',(s,)) for s in
                       ('new_affordances','lost_affordances','new_skill_facts','roles')),
    'affordances': tuple(Expression('field',(s,)) for s in
                       ('immediate_delta','reachable_after_first_move')) +
                   tuple(Expression('length',(s,)) for s in
                       ('new_affordances','lost_affordances','new_skill_facts','roles')),
    'reach': tuple(Expression('field',(s,)) for s in
                   ('immediate_delta','reachable_after_first_move')) +
             tuple(Expression('length',(s,)) for s in
                   ('new_affordances','lost_affordances','new_skill_facts','roles')),
    'truncated': (Expression('false',()), Expression('field',('truncated',))),
}


def validate_row(row: dict) -> None:
    if not isinstance(row, dict) or any(f not in row for f in FIELDS):
        raise AdapterRefusal('HOLD_SOURCE_SCHEMA')
    if (not isinstance(row['operator'],str) or not row['operator']
            or not isinstance(row['roles'],tuple)
            or not all(isinstance(s,str) and s for s in row['roles'])
            or not row['roles']
            or any(not isinstance(row[f],tuple) for f in
                   ('new_affordances','lost_affordances','new_skill_facts'))
            or any(type(row[f]) is not int for f in
                   ('immediate_delta','reachable_after_first_move'))
            or row['reachable_after_first_move'] < 0
            or type(row['truncated']) is not bool):
        raise AdapterRefusal('HOLD_SOURCE_SCHEMA')


@dataclass(frozen=True)
class Example:
    key: str
    row: dict
    expected: tuple[Any, ...]

    def __post_init__(self):
        if not self.key or len(self.expected) != len(OUTPUTS):
            raise AdapterRefusal('invalid fixture example')
        validate_row(self.row)
        if (not isinstance(self.expected[0],str) or not self.expected[0]
                or any(type(self.expected[i]) is not int for i in (1,2,3))
                or self.expected[2] < 0 or self.expected[3] < 0
                or type(self.expected[4]) is not bool):
            raise AdapterRefusal('invalid target Move contract')


def digest(cases: tuple[Example,...]) -> str:
    rows=[{'key': e.key, 'row': e.row,'target':e.expected} for e in cases]
    return sha256(json.dumps(rows,sort_keys=True,default=str).encode()).hexdigest()


@dataclass(frozen=True)
class Adapter:
    formulas: tuple[Expression, ...]
    calibration_digest: str
    examined: int
    status: str = 'I_VALIDATED_FINITE_FIXTURE'

    def __post_init__(self):
        if len(self.formulas)!=len(OUTPUTS):
            raise AdapterRefusal('partial typed port adapter')
        for name, formula in zip(OUTPUTS,self.formulas):
            if formula not in SEARCH[name]:
                raise AdapterRefusal('expression outside declared target grammar')

    def transform(self, rows: list[dict] | tuple[dict,...]) -> tuple[Move,...]:
        if not isinstance(rows,(list,tuple)) or not rows:
            raise AdapterRefusal('HOLD_EMPTY_SOURCE')
        moves=[]
        for row in rows:
            validate_row(row)
            values=tuple(exp.evaluate(row) for exp in self.formulas)
            if not (isinstance(values[0],str) and values[0]
                    and all(type(values[i]) is int for i in (1,2,3))
                    and values[2]>=0 and values[3]>=0
                    and type(values[4]) is bool):
                raise AdapterRefusal('HOLD_TARGET_SCHEMA')
            moves.append(Move(*values))
        if len({m.name for m in moves}) != len(moves):
            raise AdapterRefusal('HOLD_ALIASING_ACTION_IDENTITIES')
        return tuple(moves)


def invent(training: tuple[Example,...],validation: tuple[Example,...]) -> Adapter:
    """Fit on training, disambiguate on validation; no held-out input parameter.

    The learner cannot invent arbitrary code: it can choose only well-typed
    expressions from the public finite grammar. Ambiguity is a refusal.
    """
    if len(training)<12 or len(validation)<12:
        raise AdapterRefusal('HOLD_INSUFFICIENT_SUPERVISION')
    train_keys={e.key for e in training}
    valid_keys={e.key for e in validation}
    if (len(train_keys)!=len(training) or len(valid_keys)!=len(validation)
            or train_keys & valid_keys):
        raise AdapterRefusal('HOLD_LEAKED_SPLIT')
    chosen=[]
    explored=0
    for output_index,name in enumerate(OUTPUTS):
        fit=[]
        for expr in SEARCH[name]:
            explored+=1
            if all(expr.evaluate(e.row)==e.expected[output_index] for e in training):
                fit.append(expr)
        matches=[expr for expr in fit if all(expr.evaluate(e.row)==e.expected[output_index]
                                          for e in validation)]
        if len(matches)!=1:
            raise AdapterRefusal('HOLD_NO_UNIQUE_ADAPTER:'+name)
        chosen.append(matches[0])
    return Adapter(tuple(chosen),sha256((digest(training)+digest(validation)).encode()).hexdigest(),
                   explored)


def trusted_fixture(split: str, count: int = 64) -> tuple[Example,...]:
    """Synthetic *supervised* examples; labels are given by the fixture author.

    These labels are NOT discovered by MOTIF and do not prove real semantics.
    """
    if split not in {'train','validation','test','ood'} or count<1:
        raise ValueError('unsupported test split')
    seed=int.from_bytes(sha256(f'adapter001:{split}:v1'.encode()).digest()[:8],'big')
    rng=Random(seed)
    examples=[]
    for i in range(count):
        operator=rng.choice(('repair','teach','repair','inspect'))
        roles=(rng.choice(('person','worker','neighbor')),
               rng.choice(('device','bike','house')))
        immediate=rng.randint(-3,19)
        afford=rng.randint(0,6)
        lost=rng.randint(0,5)
        new_skills=rng.randint(0,4)
        reach=rng.randint(0,16)
        truncated=(rng.random()<.16)
        row={'operator':operator,'roles':roles,'immediate_delta':immediate,
             'new_affordances':tuple(('action',str(i),str(j)) for j in range(afford)),
             'lost_affordances':tuple(('lost',str(j)) for j in range(lost)),
             'new_skill_facts':tuple(('skill',str(j)) for j in range(new_skills)),
             'reachable_after_first_move':reach, 'truncated':truncated,
             'future':frozenset({('state','synthetic'),('episode',str(i))})}
        # Gold labels supplied to the program-synthesis experiment. No inference
        # is claimed for the labels themselves.
        expected=(f'{operator}:{roles!r}',immediate,afford,reach,truncated)
        examples.append(Example(f'{split}:{i}',row,expected))
    return tuple(examples)


def check(adapter: Adapter, fixtures: tuple[Example,...]) -> dict:
    good=0
    bad=[]
    for e in fixtures:
        try:
            move=adapter.transform([e.row])[0]
            actual=(move.name,move.immediate,move.affordances,move.reach,move.truncated)
            if actual==e.expected:
                good+=1
            else:
                bad.append(e.key)
        except (AdapterRefusal,ValueError,TypeError):
            bad.append(e.key)
    return {'tested':len(fixtures),'matched':good,'failed':tuple(bad),
            'status':'F_LOCAL_CONTRACT_REPLAY' if good==len(fixtures) else 'HOLD_HIDDEN_REGRESSION',
            'generalization_claim':False}


def missing_port_report() -> dict:
    """Inspect live target dataclass and actually try passing a source-shaped row.

    The source shape here is a synthetic fixture reflecting the MOTIF-003
    public row contract; actual module cross-check happens in the repository CI.
    """
    sample = trusted_fixture('train',1)[0].row
    try:
        Policy().choose((sample,))
        direct = 'DIRECT_EXECUTION_SUSPECT_UNEXPECTED'
    except (ValueError,AttributeError,TypeError):
        direct = 'HOLD_INCOMPATIBLE_PORTS'
    return {'source':'MOTIF003 list[dict] action rows',
            'source_observed_fields':tuple(sorted(sample)),
            'target':'SELF_MIRROR001 tuple[Move] accepted by Policy.choose',
            'target_runtime_fields':tuple(f.name for f in dataclass_fields(Move)),
            'direct_connection':direct,
            'synthesis_language':'finite field/length/join grammar',
            'pre_existing_manual_bridge':'selfmirror.preview_motif003',
            'source_of_supervision':'explicit, independent synthetic labeled examples'}


# Fixed template; only generated constant data can vary and each formula is
# checked against SEARCH before serializing. NOT arbitrary model-written Python.
CHILD = '''"""Generated typed adapter; no arbitrary plugins, eval or shell commands."""
import argparse
from hashlib import sha256
from pathlib import Path
import json
import sys
p=argparse.ArgumentParser()
p.add_argument('--source-root',required=True)
a=p.parse_args()
root=Path(a.source_root).resolve(strict=True)
module=root/'selfmirror001'/'selfmirror.py'
source=root/'adapterinvention001'/'adapterinvention.py'
if (not module.is_file() or module.is_symlink() or
        sha256(module.read_bytes()).hexdigest()!=__SOURCE_SHA__ or
        not source.is_file() or source.is_symlink() or
        sha256(source.read_bytes()).hexdigest()!=__ADAPTER_SHA__):
    print(json.dumps({'status':'HOLD_UPSTREAM_SOURCE_DRIFT'}))
    sys.exit(0)
sys.path.insert(0,str(root/'selfmirror001'))
from selfmirror import Policy, Move
sys.path.insert(0,str(root/'adapterinvention001'))
from adapterinvention import Adapter,Expression,AdapterRefusal
spec=json.loads(__ADAPTER_JSON__)
adapter=Adapter(tuple(Expression(x['op'],tuple(x['args'])) for x in spec['formulas']),
                spec['calibration_digest'],spec['examined'],spec['status'])
try:
    rows=json.loads(sys.stdin.read())
    # JSON cannot encode tuples. Restore ONLY declared tuple-valued fields.
    if not isinstance(rows,list):
        raise AdapterRefusal('HOLD_SOURCE_SCHEMA')
    for row in rows:
        if not isinstance(row,dict):
            raise AdapterRefusal('HOLD_SOURCE_SCHEMA')
        for key in ('roles','new_affordances','lost_affordances','new_skill_facts'):
            if key in row and isinstance(row[key],list):
                row[key]=tuple(row[key])
    moves=adapter.transform(rows)
    chosen=None if any(m.truncated for m in moves) else moves[Policy(2,1).choose(moves)].name
    print(json.dumps({'status':'I_VALIDATED_ADAPTER_OUTPUT' if chosen is not None else 'HOLD_INCOMPLETE_FRONTIER',
                      'choice':chosen,'moves':[m.__dict__ for m in moves],
                      'external_actions':0, 'code_edits':0},sort_keys=True))
except (ValueError,TypeError,KeyError,AttributeError) as exc:
    print(json.dumps({'status':'HOLD_INVALID_INPUT_OR_ADAPTER','reason':str(exc)[:120],
                      'external_actions':0,'code_edits':0}))
'''


def create_child(root: Path,out: Path,adapter: Adapter) -> Path:
    """Materialize one fixed interpreter launcher, never overwrite existing files."""
    if adapter.status!='I_VALIDATED_FINITE_FIXTURE':
        raise AdapterRefusal('not a validated proposal')
    source=Path(root)/'selfmirror001'/'selfmirror.py'
    bridge=Path(root)/'adapterinvention001'/'adapterinvention.py'
    if any(x.is_symlink() or not x.is_file() for x in (source,bridge)):
        raise AdapterRefusal('trusted local source missing or linked')
    out=Path(out)
    out.mkdir(parents=True,exist_ok=True)
    target=out/'discovered_adapter.py'
    receipt=out/'discovered_adapter.sha256'
    if any(x.exists() or x.is_symlink() for x in (target,receipt)):
        raise FileExistsError('refusing to overwrite generated adapter or receipt')
    specs={'formulas':[{'op':x.op,'args':x.args} for x in adapter.formulas],
           'calibration_digest':adapter.calibration_digest,'examined':adapter.examined,
           'status':adapter.status}
    text=CHILD.replace('__SOURCE_SHA__',repr(sha256(source.read_bytes()).hexdigest()))
    text=text.replace('__ADAPTER_SHA__',repr(sha256(bridge.read_bytes()).hexdigest()))
    text=text.replace('__ADAPTER_JSON__',repr(json.dumps(specs,sort_keys=True)))
    target.write_text(text,encoding='utf8')
    receipt.write_text(sha256(target.read_bytes()).hexdigest()+'\n',encoding='ascii')
    return target


def run_child(child: Path,root: Path,rows: list[dict]) -> dict:
    """Run generated bridge in another interpreter against trusted repo modules."""
    if not child.is_file() or child.is_symlink():
        return {'status':'HOLD_CHILD_MISSING_OR_LINKED'}
    receipt=child.with_suffix('.sha256')
    if (not receipt.is_file() or receipt.is_symlink() or
            receipt.read_text().strip()!=sha256(child.read_bytes()).hexdigest()):
        return {'status':'HOLD_GENERATED_CHILD_DRIFT'}
    # This subprocess is isolation of interpreter state, not a security sandbox.
    p=subprocess.run([sys.executable,str(child),'--source-root',str(root)],
                     input=json.dumps(rows,default=list),capture_output=True,text=True,
                     timeout=15,cwd=child.parent)
    if p.returncode:
        return {'status':'HOLD_CHILD_PROCESS_FAILURE','stderr':p.stderr[-300:]}
    try:
        return json.loads(p.stdout)
    except ValueError:
        return {'status':'HOLD_CHILD_NON_JSON'}


def demonstration(root: Path) -> dict:
    """Whole question -> infer missing port -> build -> verify -> next question."""
    training=trusted_fixture('train')
    validation=trusted_fixture('validation')
    adapter=invent(training,validation)
    tested=check(adapter,trusted_fixture('test',100))
    out={'experiment':'ADAPTER-INVENTION-001',
         'question':'What missing typed crossing connects MOTIF-003 rows to SELF-MIRROR Move?',
         'orientation':missing_port_report(),
         'synthesized':[{'output':name,'op':e.op,'args':e.args}
                        for name,e in zip(OUTPUTS,adapter.formulas)],
         'candidates_examined':adapter.examined,
         'finite_test':tested,'status':'HOLD_UNPROVEN_GENERALITY',
         'external_actions':0,'automatic_repo_writes':0}
    import tempfile
    with tempfile.TemporaryDirectory(prefix='motif-adapter-') as tmp:
        child=create_child(root,Path(tmp),adapter)
        example=trusted_fixture('ood',3)
        # Force an ordinary complete toy frontier for demonstration.
        rows=[dict(e.row,truncated=False) for e in example]
        output=run_child(child,root,rows)
        out['generated_child']={'status':output['status'],
                               'selected':output.get('choice'),
                               'moves':len(output.get('moves',())),
                               'source_code_sha256':sha256(child.read_bytes()).hexdigest()[:20]}
    out['next_question']='Can the bridge be discovered with less supervision and remain correct under schema drift?'
    return out


if __name__=='__main__':
    print(json.dumps(demonstration(HERE),indent=2,sort_keys=True))
