"""SELF-ASSEMBLY-001: build typed, pinned compositions of ACTUAL MOTIF cartridges.

No arbitrary Python generation/import paths. The finite registry invokes existing
MOTIF-003, MATHAL-001, SELF-MIRROR-001, WITNESS-CHAIN-001 and NEXT-STEP-001.
It plans across typed ports, emits an executable plan, checks source hashes,
executes readonly synthetic fixtures and asks one honest next integration question.
This is constrained software composition, NOT automatic invention of algorithms.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
from heapq import heappop, heappush
from pathlib import Path
from typing import Any
import json
import sys

PORT_TYPES = {
    'scene': 'synthetic_graph_state',
    'rows': 'motif003_move_rows',
    'nominations': 'mathal_proposal_runs',
    'preview': 'read_only_action_proposal',
    'witness_state': 'witnesschain_state',
    'witness_goal': 'nextstep_goal',
    'orientation': 'witness_orientation',
    'followthrough': 'read_only_followthrough',
    'fir': 'local_admission_receipt',
    'answer': 'typed_assembly_answer',
}


@dataclass(frozen=True)
class Goal:
    domain: str
    priority: str = 'new_choices'
    budget: int = 8
    max_stages: int = 8

    def __post_init__(self):
        if self.domain not in {'affordance', 'witness'}:
            raise ValueError('only two declared local experimental domains')
        if self.priority not in {'new_choices', 'immediate'}:
            raise ValueError('unknown scoring objective')
        if type(self.budget) is not int or self.budget < 0 or type(self.max_stages) is not int or not 1 <= self.max_stages <= 10:
            raise ValueError('invalid budget or bounded search horizon')


@dataclass(frozen=True)
class Stage:
    id: str
    requires: tuple[str, ...]
    provides: str
    path: str | None
    base_cost: int = 1
    external_effects: bool = False


STAGES = (
    Stage('MOTIF003_ANALYZE', ('scene',), 'rows', '003/affordance.py'),
    Stage('MATHAL_NOMINATE', ('rows',), 'nominations', 'mathal001/mathal.py'),
    Stage('SELF_MIRROR_FRONTIER', ('rows',), 'preview', 'selfmirror001/selfmirror.py'),
    Stage('SELF_MIRROR_IMMEDIATE', ('rows',), 'preview', 'selfmirror001/selfmirror.py'),
    Stage('ASSEMBLE_AFFORDANCE', ('rows','nominations','preview'), 'answer', None),
    Stage('WITNESS_ORIENT', ('witness_state','witness_goal'), 'orientation', 'nextstep001/nextstep.py'),
    Stage('WITNESS_FORWARD', ('witness_state','witness_goal'), 'followthrough', 'nextstep001/nextstep.py'),
    Stage('WITNESS_FIR', ('witness_state',), 'fir', 'witnesschain001/witnesschain.py'),
    Stage('ASSEMBLE_WITNESS', ('orientation','followthrough','fir'), 'answer', None),
)
REGISTRY = {s.id:s for s in STAGES}
# Transitive source files, beyond the direct stage modules, are pinned too.
DEPENDENCIES = (
    '003/affordance.py', 'fir001/fir.py', 'mathal001/mathal.py',
    'selfmirror001/selfmirror.py', 'nextstep001/nextstep.py',
    'witnesschain001/witnesschain.py', 'assemblylab001/assembly.py',
)
CHILD_NAME = 'assembled_motif.py'


@dataclass(frozen=True)
class Assembly:
    goal: Goal
    stages: tuple[str, ...]
    cost: int
    pinned_files: tuple[tuple[str,str], ...]
    status: str = 'I_TESTABLE_ASSEMBLY'


def stage_cost(stage: Stage, goal: Goal) -> int:
    if stage.id == 'SELF_MIRROR_FRONTIER':
        return 1 if goal.priority == 'new_choices' else 3
    if stage.id == 'SELF_MIRROR_IMMEDIATE':
        return 1 if goal.priority == 'immediate' else 3
    return stage.base_cost


def plan(goal: Goal) -> tuple[str,...] | None:
    """Dijkstra over a typed monotone dataflow graph; not a hardcoded pipeline.

    Each stage can be used once. The same output port cannot be supplied twice.
    The planner never executes a candidate to decide whether it is admissible.
    """
    initial = frozenset(('scene',) if goal.domain=='affordance'
                        else ('witness_state','witness_goal'))
    frontier = [(0, 0, (), initial)]
    visited: dict[frozenset[str], int] = {}
    while frontier:
        cost, length, history, available = heappop(frontier)
        if 'answer' in available:
            return history
        if cost > goal.budget or length >= goal.max_stages:
            continue
        if cost >= visited.get(available, float('inf')):
            continue
        visited[available] = cost
        for stage in STAGES:
            if (stage.external_effects or stage.id in history or stage.provides in available
                    or not set(stage.requires).issubset(available)):
                continue
            cost2 = cost+stage_cost(stage,goal)
            if cost2 > goal.budget:
                continue
            heappush(frontier,(cost2,length+1, history+(stage.id,),
                               available | {stage.provides}))
    return None


def source_pins(root: Path) -> tuple[tuple[str,str],...]:
    """Pin exact source bytes; names/signatures alone are not enough."""
    root=Path(root).resolve(strict=True)
    hashes=[]
    for rel in DEPENDENCIES:
        path=root/rel
        if path.is_symlink() or not path.is_file() or not path.resolve().is_relative_to(root):
            raise ValueError(f'missing, linked, or escaping dependency {rel}')
        hashes.append((rel,sha256(path.read_bytes()).hexdigest()))
    return tuple(hashes)


def compile_assembly(root: Path, goal: Goal) -> Assembly:
    route = plan(goal)
    if route is None:
        raise ValueError('HOLD_NO_TYPED_AFFORDABLE_ASSEMBLY')
    if len(set(route)) != len(route):
        raise AssertionError('duplicate stage in plan')
    return Assembly(goal,route,sum(stage_cost(REGISTRY[s],goal) for s in route),source_pins(root))


def _import_real(root: Path):
    """Import repository-owned modules only, after hash verification.

    This adapter is for checked-out, trusted experiment code; source pinning
    detects changes, not hostile Python dependencies or supply-chain origins.
    """
    for relative in ('fir001','mathal001','selfmirror001','witnesschain001',
                     'nextstep001','003'):
        source = str(root/relative)
        if source not in sys.path:
            sys.path.insert(0,source)
    from affordance import analyze_first_moves
    from mathal import nominate_motif003
    from selfmirror import Policy, preview_motif003
    from witnesschain import fir_receipt, synthetic_cases, State
    from nextstep import Goal as NextGoal, advance, orient
    return locals()


def fixture(domain: str, root: Path) -> dict:
    """Two intentionally small and explicit synthetic problems, no user code."""
    if domain == 'affordance':
        return {'scene': frozenset({('need','repair'), ('resource','scrap')})}
    if domain == 'witness':
        real = _import_real(root)
        state=real['State']()
        for event,_ in real['synthetic_cases']((1,1,1),7,50):
            state=state.add(event)
        return {'witness_state':state,
                'witness_goal':real['NextGoal']('absolute_polarity',budget=4,max_steps=3)}
    raise ValueError('unknown fixture domain')


def _possibilities(world,verbs):
    """Declared toy rewrite rules; real MOTIF-003 performs the search."""
    del verbs
    if ('need','repair') in world:
        yield 'repair',('worker','device'), frozenset((world-{('need','repair')})|{('state','repaired')})
        if ('skill','repair') not in world:
            yield 'teach',('worker','apprentice'), frozenset(world|{('skill','repair')})
    if ('skill','repair') in world and ('need','repair') in world:
        yield 'collaborate',('worker','apprentice'), frozenset((world-{('need','repair')})|{('state','repaired'),('skill','repair')})
        yield 'mentor',('worker','apprentice'), frozenset(world|{('skill','mentoring')})
        yield 'plan',('worker','apprentice'), frozenset(world|{('plan','repair')})
        yield 'share_tools',('worker','neighbor'), frozenset(world|{('state','tools_shared')})
    if ('state','repaired') in world:
        yield 'share',('worker','neighbor'), frozenset(world|{('state','shared')})


def _utility(world,initial):
    del initial
    return 10*int(('state','repaired') in world)+2*int(('state','shared') in world)+4*int(('skill','repair') in world)


def _run_stage(stage: Stage, data: dict, real: dict) -> Any:
    if stage.id=='MOTIF003_ANALYZE':
        return real['analyze_first_moves'](data['scene'],{},_possibilities,_utility,horizon=3)
    if stage.id=='MATHAL_NOMINATE':
        return real['nominate_motif003'](data['rows'])
    if stage.id in {'SELF_MIRROR_FRONTIER','SELF_MIRROR_IMMEDIATE'}:
        policy = real['Policy'](2,1) if stage.id=='SELF_MIRROR_FRONTIER' else real['Policy'](0,0)
        return real['preview_motif003'](data['rows'],policy)
    if stage.id=='WITNESS_ORIENT':
        return real['orient'](data['witness_state'],data['witness_goal'])
    if stage.id=='WITNESS_FORWARD':
        return real['advance'](data['witness_state'],data['witness_goal'])
    if stage.id=='WITNESS_FIR':
        return real['fir_receipt'](data['witness_state'])
    if stage.id=='ASSEMBLE_AFFORDANCE':
        rows=data['rows']; nominations=data['nominations']; preview=data['preview']
        if len(rows)!=len(nominations) or not rows or any(not r.applied or r.world.facts or len(r.world.ideas)!=1 for r in nominations):
            raise ValueError('HOLD_UNSUPPORTED_OR_INCOMPLETE_FIR_NOMINATIONS')
        if preview.get('status')!='I' or preview.get('admitted_fact'):
            raise ValueError('HOLD_PREVIEW_ESCAPED_PROPOSAL_ONLY_BOUNDARY')
        proposal = preview.get('selection')
        if proposal is not None and proposal not in {
                str(row['operator'])+':'+repr(tuple(row['roles'])) for row in rows}:
            raise ValueError('HOLD_PREVIEW_SELECTION_NOT_IN_SOURCE_ROWS')
        return {'domain':'affordance', 'status':'I_SIMULATED_ACTION_ONLY',
                'answered_question':'Which proposed synthetic move should be explored first?',
                'proposed_action':proposal,
                'candidate_actions':len(rows), 'fir_proposals':len(nominations),
                'new_options_by_move':{row['operator']:len(row['new_affordances']) for row in rows},
                'next_question':'Would the selected simulated move actually produce the predicted opportunities?',
                'next_safe_probe':'MOTIF-003 independently recomputed imagined futures; real-world outcome unverified',
                'external_actions':0,'new_independent_evidence':False}
    if stage.id=='ASSEMBLE_WITNESS':
        orientation=data['orientation']; follow=data['followthrough']; receipt=data['fir']
        if receipt['hypothesis_role']!='I' or receipt['ledger_count_role']!='F_LOCAL':
            raise ValueError('HOLD_FIR_WARRANT_LEAKAGE')
        if not follow.get('same_evidence_before_after') or follow.get('real_world_actions'):
            raise ValueError('HOLD_UNTRUSTED_FOLLOWTHROUGH')
        return {'domain':'witness','status':follow['status'],
                'answered_question':orientation['requested_question'],
                'original_answer':orientation['requested_answer'],
                'executed_next_questions':tuple(step['next_question'] for step in follow['steps']),
                'executed_operations':tuple(step['action_executed'] for step in follow['steps']),
                'fir_evidence_role':receipt['ledger_count_role'],
                'fir_model_role':receipt['hypothesis_role'],
                'next_question':'How can a source provide an independently verifiable truth receipt?',
                'external_actions':0,'new_independent_evidence':False}
    raise PermissionError('unrecognized stage must never run')



def _valid_output(stage: Stage, result: Any) -> bool:
    """Second gate: declared port types have *runtime* limited contract checks."""
    if stage.id=='MOTIF003_ANALYZE':
        return (isinstance(result,list) and bool(result)
                and all(isinstance(row,dict) and isinstance(row.get('future'),frozenset)
                        and isinstance(row.get('new_affordances'),tuple)
                        and not row.get('truncated',False) for row in result)
                and len({(r.get('operator'),tuple(r.get('roles',()))) for r in result})==len(result))
    if stage.id=='MATHAL_NOMINATE':
        return (isinstance(result,list) and bool(result) and all(
            run.applied and run.world is not None and
            len(run.world.facts)==0 and len(run.world.ideas)==1
            for run in result))
    if stage.id in {'SELF_MIRROR_IMMEDIATE','SELF_MIRROR_FRONTIER'}:
        return (isinstance(result,dict) and result.get('status')=='I'
                and result.get('admitted_fact') is False)
    if stage.id=='WITNESS_ORIENT':
        return isinstance(result,dict) and 'requested_answer' in result and not result.get('authenticity_verified')
    if stage.id=='WITNESS_FORWARD':
        return (isinstance(result,dict) and result.get('real_world_actions')==0
                and result.get('same_evidence_before_after') is True)
    if stage.id=='WITNESS_FIR':
        return isinstance(result,dict) and result.get('ledger_count_role')=='F_LOCAL' and result.get('hypothesis_role')=='I'
    if stage.id.startswith('ASSEMBLE_'):
        return isinstance(result,dict) and result.get('external_actions')==0 and isinstance(result.get('next_question'),str)
    return False

def execute(assembly: Assembly, root: Path, data: dict | None = None) -> dict:
    """Run pinned typed plan with real repository modules. No arbitrary eval."""
    root=Path(root).resolve(strict=True)
    if assembly.status != 'I_TESTABLE_ASSEMBLY' or source_pins(root)!=assembly.pinned_files:
        return {'status':'HOLD_SOURCE_DRIFT','external_actions':0}
    if assembly.stages!=plan(assembly.goal):
        return {'status':'HOLD_UNPLANNED_OR_MODIFIED_STAGE_CHAIN','external_actions':0}
    real=_import_real(root)
    allowed_inputs = {'scene'} if assembly.goal.domain=='affordance' else {'witness_state','witness_goal'}
    context=fixture(assembly.goal.domain,root) if data is None else dict(data)
    if set(context)!=allowed_inputs:
        return {'status':'HOLD_INPUT_SCHEMA','external_actions':0}
    if assembly.goal.domain == 'affordance' and (
            not isinstance(context['scene'], frozenset) or
            not all(isinstance(x,tuple) and len(x)==2 and
                    all(isinstance(v,str) for v in x) for x in context['scene'])):
        return {'status':'HOLD_INPUT_SCHEMA','external_actions':0}
    if assembly.goal.domain == 'witness' and (
            not isinstance(context['witness_state'],real['State']) or
            not isinstance(context['witness_goal'],real['NextGoal'])):
        return {'status':'HOLD_INPUT_SCHEMA','external_actions':0}
    # No untrusted caller-supplied stage registry, function bodies, or source paths.
    trail=[]
    for name in assembly.stages:
        stage=REGISTRY[name]
        if stage.external_effects or stage.provides in context or not set(stage.requires)<=set(context):
            return {'status':'HOLD_TYPED_PORT_MISMATCH','external_actions':0,'receipts':trail}
        result = _run_stage(stage,context,real)
        if not _valid_output(stage,result):
            return {'status':'HOLD_INVALID_STAGE_OUTPUT','external_actions':0,'receipts':trail}
        context[stage.provides]=result
        trail.append({'stage':name,'input_ports':stage.requires,
                      'output_port':stage.provides,'external_actions':0})
    answer=context.get('answer')
    if not answer:
        return {'status':'HOLD_MISSING_ANSWER','external_actions':0,'receipts':trail}
    return {'status':'EXECUTED_TYPED_COMPOSITION','assembly_stages':assembly.stages,
            'source_digest':sha256(repr(assembly.pinned_files).encode()).hexdigest()[:20],
            'result':answer,'receipts':trail,'external_actions':0,
            'autonomous_source_changes':False,'model_claim':'I_LOCAL_SYNTHETIC_ONLY'}


CHILD_BODY = '''"""Generated planner-selected MOTIF child that imports REAL pinned cartridges."""
from pathlib import Path
import argparse
import json
import sys

parser=argparse.ArgumentParser()
parser.add_argument('--source-root', required=True)
args=parser.parse_args()
root=Path(args.source_root).resolve()
sys.path.insert(0,str(root/'assemblylab001'))
from assembly import Assembly, Goal, execute

spec=json.loads(__ASSEMBLY_JSON__)
artifact=Assembly(Goal(**spec['goal']),tuple(spec['stages']),spec['cost'],
                  tuple(tuple(x) for x in spec['pinned_files']),spec['status'])
print(json.dumps(execute(artifact,root),sort_keys=True,default=str))
'''


def create_child(root: Path, output: Path, goal: Goal) -> tuple[Path,Assembly]:
    """Generate a single pinned launcher in the expressly requested output folder."""
    program=compile_assembly(root,goal)
    output=Path(output)
    output.mkdir(parents=True,exist_ok=True)
    child=output/CHILD_NAME
    if child.exists() or child.is_symlink():
        raise FileExistsError('will not overwrite previously generated child')
    spec=json.dumps(asdict(program),sort_keys=True)
    child.write_text(CHILD_BODY.replace('__ASSEMBLY_JSON__',repr(spec)),encoding='utf8')
    return child,program


def verify_child(child: Path, root: Path) -> dict:
    """Independent interpreter/working-directory check of the emitted child."""
    import subprocess
    if not child.is_file() or child.is_symlink():
        return {'status':'HOLD_CHILD_MISSING_OR_LINKED'}
    result=subprocess.run([sys.executable,str(child),'--source-root',str(root)],
                          cwd=child.parent,timeout=25,capture_output=True,text=True)
    if result.returncode:
        return {'status':'HOLD_CHILD_PROCESS_FAILURE','stderr':result.stderr[:400]}
    try:
        output=json.loads(result.stdout)
    except ValueError:
        return {'status':'HOLD_NON_JSON_CHILD'}
    return {'status':'VERIFIED_EXECUTION' if output.get('status')=='EXECUTED_TYPED_COMPOSITION' else 'HOLD_CHILD_RESULT',
            'output':output,'stdout_bytes':len(result.stdout)}


def demonstration(root: Path) -> dict:
    import tempfile
    demonstrations={}
    for domain, priority in (('affordance','new_choices'),('affordance','immediate'),('witness','new_choices')):
        goal=Goal(domain,priority)
        with tempfile.TemporaryDirectory(prefix='motif-assembly-') as folder:
            child,program=create_child(root,Path(folder),goal)
            verify=verify_child(child,root)
            demonstrations[f'{domain}:{priority}']={
                'selection':program.stages,'cost':program.cost,
                'verified':verify['status'],
                'answer':verify.get('output',{}).get('result')}
    return {'experiment':'SELF-ASSEMBLY-001',
            'scope':'declared local synthetic work; actual source-module wiring',
            'compositions':demonstrations,
            'new_algorithms_invented':0,'real_world_actions':0,
            'remaining_question':'Can independent tests justify a new adapter or policy rather than only recombine existing ones?'}


if __name__=='__main__':
    import json
    print(json.dumps(demonstration(Path(__file__).resolve().parents[1]),indent=2,sort_keys=True,default=str))
