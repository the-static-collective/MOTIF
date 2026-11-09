"""SEMANTIC-ADAPTER-001: infer a small bridge from executable behavioral contracts.

No target-labeled Move examples are consumed. The target semantics and the
hypothesis grammar ARE declared by the experimenter; this is not autonomous
understanding of arbitrary interfaces. All probes are synthetic, local, and
side-effect-free. Runtime semantic checks refuse plausible type-correct drift.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Callable
import subprocess
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
for d in ('003','assemblylab001','adapterinvention001','selfmirror001'):
    if str(ROOT/d) not in sys.path:
        sys.path.insert(0, str(ROOT/d))
from affordance import analyze_first_moves
from assembly import _possibilities, _utility
from adapterinvention import SEARCH, OUTPUTS, Adapter, Expression, AdapterRefusal, validate_row
from selfmirror import Move, Policy, preview_motif003


class SemanticRefusal(ValueError):
    pass


@dataclass(frozen=True)
class Probe:
    name: str
    scene: frozenset[tuple[str, str]]
    utility_kind: str = 'base'
    horizon: int = 3
    max_worlds: int = 1000

    def __post_init__(self):
        if (not self.name or not isinstance(self.scene, frozenset)
                or not all(isinstance(x, tuple) and len(x) == 2
                           and all(isinstance(t, str) and t for t in x) for x in self.scene)
                or self.utility_kind not in {'base','skill','completion','share'}
                or self.horizon != 3 or self.max_worlds < 2):
            raise SemanticRefusal('HOLD_INVALID_PROBE_CONTRACT')


def utility(kind: str) -> Callable:
    if kind not in {'base','skill','completion','share'}:
        raise SemanticRefusal('HOLD_UNDECLARED_UTILITY')
    if kind == 'base':
        return _utility
    if kind == 'skill':
        return lambda world, start: _utility(world, start) + 9*int(('skill','repair') in world)
    if kind == 'completion':
        return lambda world, start: _utility(world, start) - 19*int(('state','repaired') in world)
    return lambda world, start: _utility(world,start) + 7*int(('state','shared') in world)


def probes(split: str) -> tuple[Probe,...]:
    """Fixed split-specific synthetic interventions; no Move target labels."""
    if split not in {'train','validation','test','ood'}:
        raise SemanticRefusal('HOLD_UNDECLARED_SPLIT')
    scenes = (
        {('need','repair'),('resource','scrap')},
        {('need','repair'),('resource','scrap'),('skill','repair')},
        {('need','repair'),('resource','scrap'),('state','repaired')},
        {('need','repair'),('resource','scrap'),('skill','repair'),('state','repaired')},
        {('need','repair'),('skill','repair')},
        {('need','repair'),('skill','repair'),('skill','mentoring')},
        {('need','repair'),('skill','repair'),('plan','repair')},
        {('need','repair'),('resource','scrap'),('plan','repair')},
        {('need','repair'),('resource','scrap'),('state','tools_shared')},
    )
    kinds = ('base','skill','completion','share')
    # Different splits use different nonsemantic marker nodes, preserving
    # identical control semantics while ensuring input worlds aren't reused.
    out=[]
    for i,scene in enumerate(scenes):
        for kind in kinds:
            stamp=('experiment:'+split,'case:'+str(i)+':'+kind)
            out.append(Probe(f'{split}:{i}:{kind}', frozenset(scene|{stamp}),kind, max_worlds=(2 if kind == 'share' else 1000)))
    return tuple(out)


def independent_actions(scene: frozenset) -> dict[tuple[str,tuple[str,...]],frozenset]:
    """Re-evaluate the transition relation, do not trust reported action rows."""
    transitions={}
    for op, roles, future in _possibilities(scene,{}):
        key=(op,tuple(roles))
        if key in transitions or not isinstance(future,frozenset):
            raise SemanticRefusal('HOLD_AMBIGUOUS_EXECUTABLE_WORLD')
        transitions[key]=future
    return transitions


def independent_frontier(start: frozenset, horizon: int, limit: int) -> tuple[int,bool]:
    """Independent iterative breadth-first search; does not use 003.frontier_after."""
    visited={start}
    layer={start}
    for depth in range(horizon):
        next_layer=set()
        for world in sorted(layer, key=repr):
            for future in independent_actions(world).values():
                if future in visited:
                    continue
                if len(visited) >= limit:
                    return len(visited),True
                visited.add(future)
                next_layer.add(future)
        layer=next_layer
    return len(visited),False


def target_contract(probe: Probe, row: dict) -> tuple:
    """Compute a Move target from *world behavior*, not hand-entered Move labels.

    The semantics are defined externally: utility difference, difference of
    reachable action identities, independently counted future states. Source
    row metadata must agree with the computed world before any adapter is fit.
    """
    try:
        validate_row(row)
        moves=independent_actions(probe.scene)
        key=(row['operator'], tuple(row['roles']))
        if key not in moves or row.get('future') != moves[key]:
            raise SemanticRefusal('HOLD_INVALID_ACTION_TRACE')
        future=moves[key]
        before=set(moves)
        after=set(independent_actions(future))
        incoming=tuple(sorted(after-before))
        outgoing=tuple(sorted(before-after))
        newskills=tuple(sorted(f for f in future-probe.scene if f[0]=='skill'))
        steps, truncated=independent_frontier(future,probe.horizon-1,probe.max_worlds)
        fn=utility(probe.utility_kind)
        gain=fn(future,probe.scene)-fn(probe.scene,probe.scene)
        # Explicit contracts detect type-preserving meaning changes.
        expected_source={'immediate_delta':gain,
                         'new_affordances':len(incoming),
                         'lost_affordances':len(outgoing),
                         'new_skill_facts':newskills,
                         'reachable_after_first_move':steps,
                         'truncated':truncated}
        mismatches=[]
        for field,value in expected_source.items():
            actual=len(row[field]) if field in {'new_affordances','lost_affordances'} else row[field]
            if actual!=value:
                mismatches.append(field)
        # Rechecking only lengths isn't sufficient for claimed new-affordance
        # identities: validate exact set-valued content, too.
        if set(row['new_affordances']) != after-before:
            mismatches.append('new_affordances_contents')
        if set(row['lost_affordances']) != before-after:
            mismatches.append('lost_affordances_contents')
        if mismatches:
            raise SemanticRefusal('HOLD_SEMANTIC_DRIFT:'+','.join(sorted(set(mismatches))))
        return (f"{row['operator']}:{tuple(row['roles'])!r}",gain,len(incoming),steps,truncated)
    except (AdapterRefusal,ValueError,TypeError,KeyError,IndexError) as exc:
        if isinstance(exc,SemanticRefusal):
            raise
        raise SemanticRefusal('HOLD_SOURCE_CONTRACT') from exc


def observe(probe: Probe) -> tuple[dict,...]:
    """Call actual MOTIF-003; keep the source result (no target labels)."""
    rows=analyze_first_moves(probe.scene, {}, _possibilities, utility(probe.utility_kind),
                             horizon=probe.horizon, max_worlds=probe.max_worlds)
    if not rows:
        raise SemanticRefusal('HOLD_NO_ACTION_AFFORDANCES')
    # Independent preflight on each reported row.
    for row in rows:
        target_contract(probe,row)
    if len({(r['operator'],tuple(r['roles'])) for r in rows})!=len(rows):
        raise SemanticRefusal('HOLD_DUPLICATE_ACTION_IDENTITIES')
    return tuple(rows)


@dataclass(frozen=True)
class InferredBridge:
    adapter: Adapter
    train_digest: str
    validation_digest: str
    formula_tests: int
    question: str = 'Can a declared behavioral contract bridge MOTIF-003 to SELF-MIRROR?'
    status: str = 'I_SYNTHESIZED_BEHAVIORAL_CONTRACT'

    def convert(self, probe: Probe, rows: tuple[dict,...] | None = None) -> tuple[Move,...]:
        observed=observe(probe) if rows is None else rows
        if not observed:
            raise SemanticRefusal('HOLD_NO_ROWS')
        for row in observed:
            target_contract(probe,row)
        output=self.adapter.transform(list(observed))
        for row,move in zip(observed,output):
            if (move.name, move.immediate, move.affordances, move.reach, move.truncated) != target_contract(probe,row):
                raise SemanticRefusal('HOLD_TARGET_MEANING_MISMATCH')
        return output


def source_digest(pairs: list[tuple[Probe,dict]]) -> str:
    payload=[(p.name,sorted(p.scene),p.utility_kind,
              r['operator'],r['roles'],r['immediate_delta'],r['new_affordances'],
              r['reachable_after_first_move'],r['truncated']) for p,r in pairs]
    return sha256(json.dumps(payload,default=str,sort_keys=True).encode()).hexdigest()


def invent(training: tuple[Probe,...], validation: tuple[Probe,...]) -> InferredBridge:
    """Search fixed expression grammar using executable source invariants.

    No target-labeled examples accepted. Observational contract is hand-set.
    Holdout never enters this method. Return HOLD on nonunique expressions.
    """
    if len(training)<12 or len(validation)<12:
        raise SemanticRefusal('HOLD_TOO_FEW_BEHAVIORAL_PROBES')
    train_names={x.name for x in training}
    validate_names={x.name for x in validation}
    if (len(train_names)!=len(training) or len(validate_names)!=len(validation)
            or train_names & validate_names):
        raise SemanticRefusal('HOLD_LEAKED_PROBES')
    train=[(p,r) for p in training for r in observe(p)]
    valid=[(p,r) for p in validation for r in observe(p)]
    chosen=[]
    inspected=0
    for j,target in enumerate(OUTPUTS):
        matched=[]
        for expression in SEARCH[target]:
            inspected+=1
            if (all(expression.evaluate(row)==target_contract(p,row)[j] for p,row in train)
                    and all(expression.evaluate(row)==target_contract(p,row)[j] for p,row in valid)):
                matched.append(expression)
        if len(matched)!=1:
            raise SemanticRefusal('HOLD_AMBIGUOUS_SEMANTIC_MAPPING:'+target+':'+str(len(matched)))
        chosen.append(matched[0])
    t,v=source_digest(train),source_digest(valid)
    calibrated=Adapter(tuple(chosen),sha256((t+v).encode()).hexdigest(),inspected)
    return InferredBridge(calibrated,t,v,inspected)


def check(bridge: InferredBridge, holdouts: tuple[Probe,...]) -> dict:
    accepted=0; refused=0; failures=[]; actions=0
    for p in holdouts:
        try:
            rows=observe(p)
            actual=bridge.convert(p,rows)
            for row,move in zip(rows,actual):
                expected=target_contract(p,row)
                accepted += (move.name, move.immediate, move.affordances, move.reach, move.truncated)==expected
                actions+=1
        except (SemanticRefusal,AdapterRefusal,ValueError) as exc:
            refused+=1
            failures.append((p.name,str(exc)))
    return {'probe_worlds':len(holdouts),'actions':actions,'correct_outputs':accepted,
            'refused_worlds':refused,'failures':tuple(failures),
            'status':'F_LOCAL_FINITE_REPLAY' if refused==0 and accepted==actions and actions>0
                     else 'HOLD_FROZEN_TEST_FAILURE','general_semantics_proved':False}


def adversarial_shift(bridge: InferredBridge, p: Probe, row: dict) -> dict:
    """Type-preserving attack; compare original typed-only synthesis to semantic gate."""
    changed=dict(row)
    changed['immediate_delta'],changed['reachable_after_first_move']=(
        row['reachable_after_first_move'],row['immediate_delta'])
    typed_only_accepts=False
    if changed['reachable_after_first_move']>=0:
        try:
            bridge.adapter.transform([changed])
            typed_only_accepts=True
        except AdapterRefusal:
            pass
    try:
        bridge.convert(p,(changed,))
        semantic='ACCEPTED_SAME_VALUE_COLLISION'
    except SemanticRefusal as exc:
        semantic=str(exc).split(':')[0]
    return {'typed_only_accepts':typed_only_accepts,'semantic_gate':semantic,
            'actual_fields_changed':(changed['immediate_delta']!=row['immediate_delta']),
            'source_values':(row['immediate_delta'],row['reachable_after_first_move'])}


def preview_policy(bridge: InferredBridge, p: Probe, policy: Policy) -> dict:
    rows=observe(p)
    try:
        moves=bridge.convert(p,rows)
    except SemanticRefusal as exc:
        return {'status':str(exc),'choice':None}
    if any(m.truncated for m in moves):
        return {'status':'HOLD_INCOMPLETE_FRONTIER','choice':None}
    idx=policy.choose(moves)
    hand=preview_motif003(list(rows),policy)
    if hand.get('selection')!=moves[idx].name:
        return {'status':'HOLD_MANUAL_CONTROL_DISAGREEMENT','choice':None}
    return {'status':'I_VERIFIED_LOCAL_PROPOSAL','choice':moves[idx].name,
            'manual_bridge_agrees':True,'external_actions':0}


# The child imports only repository modules after checking exact file digests.
# This is a fixed-template runner, not a security sandbox or freeform codegen.
PINNED_SOURCES = (
    '003/affordance.py', 'assemblylab001/assembly.py',
    'adapterinvention001/adapterinvention.py', 'selfmirror001/selfmirror.py',
    'fir001/fir.py', 'mathal001/mathal.py', 'semanticadapter001/semanticadapter.py',
)


def pins(root: Path) -> tuple[tuple[str, str], ...]:
    root = Path(root).resolve(strict=True)
    out = []
    for rel in PINNED_SOURCES:
        source = root/rel
        if (not source.is_file() or source.is_symlink()
                or not source.resolve().is_relative_to(root)):
            raise SemanticRefusal('HOLD_SOURCE_MISSING_OR_LINKED:'+rel)
        out.append((rel, sha256(source.read_bytes()).hexdigest()))
    return tuple(out)


CHILD = '''"""Executable fixed semantic-adapter child; synthetic task only."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
parser=argparse.ArgumentParser()
parser.add_argument('--source-root',required=True)
parser.add_argument('--index',type=int,default=0)
args=parser.parse_args()
root=Path(args.source_root).resolve(strict=True)
expected=json.loads(__PINNED__)
for rel,digest in expected:
    path=root/rel
    if not path.is_file() or path.is_symlink() or sha256(path.read_bytes()).hexdigest()!=digest:
        print(json.dumps({'status':'HOLD_SOURCE_DRIFT','source':rel}))
        sys.exit(0)
if args.index<0 or args.index>=36:
    print(json.dumps({'status':'HOLD_INVALID_PROBE_INDEX'}))
    sys.exit(0)
sys.path.insert(0,str(root/'semanticadapter001'))
from semanticadapter import InferredBridge, probes, preview_policy
from adapterinvention import Adapter, Expression
from selfmirror import Policy
spec=json.loads(__BRIDGE__)
formulas=tuple(Expression(item['op'],tuple(item['args'])) for item in spec['formulas'])
adapter=Adapter(formulas,spec['calibration_digest'],spec['examined'])
bridge=InferredBridge(adapter,spec['train_digest'],spec['validation_digest'],spec['formula_tests'])
p=probes('test')[args.index]
answer=preview_policy(bridge,p,Policy(2,1))
print(json.dumps({'status':answer['status'], 'choice':answer.get('choice'),
                  'synthetic_probe':p.name, 'source_hashes_verified':len(expected),
                  'external_actions':0, 'automatic_code_edits':0},sort_keys=True))
'''


def build_child(root: Path, out: Path, bridge: InferredBridge) -> Path:
    if bridge.status != 'I_SYNTHESIZED_BEHAVIORAL_CONTRACT':
        raise SemanticRefusal('HOLD_NOT_AN_INFERRED_BRIDGE')
    checks = pins(root)
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    child = out/'semantic_adapter_child.py'
    digest_file = out/'semantic_adapter_child.sha256'
    if any(p.exists() or p.is_symlink() for p in (child,digest_file)):
        raise FileExistsError('refusing to overwrite generated source')
    spec = {
        'formulas':[{'op':e.op,'args':e.args} for e in bridge.adapter.formulas],
        'calibration_digest':bridge.adapter.calibration_digest,
        'examined':bridge.adapter.examined,
        'train_digest':bridge.train_digest,
        'validation_digest':bridge.validation_digest,
        'formula_tests':bridge.formula_tests,
    }
    body=CHILD.replace('__PINNED__', repr(json.dumps(checks,sort_keys=True)))
    body=body.replace('__BRIDGE__', repr(json.dumps(spec,sort_keys=True)))
    child.write_text(body,encoding='utf8')
    digest_file.write_text(sha256(child.read_bytes()).hexdigest()+'\n',encoding='ascii')
    return child


def run_child(child: Path, root: Path, index: int = 0) -> dict:
    child=Path(child)
    manifest=child.with_suffix('.sha256')
    if child.is_symlink() or not child.is_file():
        return {'status':'HOLD_CHILD_MISSING_OR_LINKED'}
    if (manifest.is_symlink() or not manifest.is_file()
            or manifest.read_text().strip()!=sha256(child.read_bytes()).hexdigest()):
        return {'status':'HOLD_CHILD_DIGEST_DRIFT'}
    try:
        outcome=subprocess.run([sys.executable,str(child),'--source-root',str(root),
                                '--index',str(index)],cwd=child.parent,capture_output=True,
                               text=True,timeout=25)
    except subprocess.TimeoutExpired:
        return {'status':'HOLD_CHILD_TIMEOUT'}
    if outcome.returncode:
        return {'status':'HOLD_CHILD_PROCESS_FAILURE','stderr':outcome.stderr[-300:]}
    try:
        return json.loads(outcome.stdout)
    except json.JSONDecodeError:
        return {'status':'HOLD_CHILD_NON_JSON'}


def demonstration() -> dict:
    bridge=invent(probes('train'),probes('validation'))
    held=check(bridge,probes('test'))
    shifted=0; typable=0; cases=0; collisions=0
    for p in probes('ood'):
        for row in observe(p):
            if row['immediate_delta']<0 or row['immediate_delta']==row['reachable_after_first_move']:
                collisions+=1
                continue
            cases+=1
            attack=adversarial_shift(bridge,p,row)
            shifted+=attack['semantic_gate'].startswith('HOLD')
            typable+=attack['typed_only_accepts']
    import tempfile
    with tempfile.TemporaryDirectory(prefix='motif-semantic-child-') as folder:
        child=build_child(ROOT,Path(folder),bridge)
        subprocess_result=run_child(child,ROOT,index=0)
    return {'experiment':'SEMANTIC-ADAPTER-001',
            'answer':'A small bridge can be chosen from executable semantic invariants without target Move labels.',
            'limited_scope':'declared synthetic world and manually authored behavioral target semantics',
            'expression_candidates_inspected':bridge.formula_tests,
            'learned_expression_ops':tuple(e.op for e in bridge.adapter.formulas),
            'frozen_holdout':held,
            'real_child_process':subprocess_result,
            'shift_attack':{'eligible':cases,'typed_only_accepted':typable,
                            'semantically_refused':shifted,'excluded_negative_or_equal':collisions},
            'strong_baseline':'Existing handwritten SELF-MIRROR bridge; expected tie, not claimed improvement',
            'next_question':'Can inferred semantic contracts transfer to a new family without author-supplied invariants?',
            'external_actions':0,'autonomous_source_modifications':False,
            'general_algorithm_invention':False}


if __name__=='__main__':
    print(json.dumps(demonstration(),indent=2,sort_keys=True,default=str))
