"""SELF-BUILD-001: ask MOTIF how to build a bounded instance of itself.

Source-based inventory -> next question -> local template instantiation ->
independent process tests -> scope/receipt. This is deliberate classical
bootstrapping, NOT arbitrary synthesis of code, unbounded self-modification,
or autonomous publication. Generated Python is a fixed reviewed template.
"""
from __future__ import annotations

import ast
from dataclasses import asdict, dataclass
from hashlib import sha256
from pathlib import Path
import json
import subprocess
import sys
import tempfile
from typing import Any

# These are *observed interface requirements*, not assertions that the
# modules implement general intelligence. An AST name proves only presence.
INTERFACES = (
    ("MOTIF-003", "003/affordance.py", ("analyze_first_moves", "witness_gap")),
    ("FIR-001", "fir001/fir.py", ("FIRWorld", "Claim")),
    ("MATHAL-001", "mathal001/mathal.py", ("execute", "compose_runs")),
    ("WITNESS-CHAIN-001", "witnesschain001/witnesschain.py", ("State", "propose")),
    ("NEXT-STEP-001", "nextstep001/nextstep.py", ("orient", "advance")),
)
ACTIONS = frozenset({"INSPECT_SOURCE", "GENERATE_SEED", "TEST_SEED", "REPORT_LIMITS"})
CHILD_FILE = "motif_seed.py"
CHILD_TEST_FILE = "test_motif_seed.py"


@dataclass(frozen=True)
class Goal:
    question: str = "How can MOTIF make a small, verifiable instance of itself?"
    budget: int = 4
    max_steps: int = 4

    def __post_init__(self):
        if (not self.question or type(self.budget) is not int or self.budget < 0
                or type(self.max_steps) is not int or not 1 <= self.max_steps <= 4):
            raise ValueError("invalid self-build goal")


@dataclass(frozen=True)
class InterfaceFinding:
    component: str
    path: str
    required: tuple[str, ...]
    present: tuple[str, ...]
    missing: tuple[str, ...]
    file_sha256: str | None
    status: str


@dataclass(frozen=True)
class Orientation:
    request: str
    source_digest: str
    observed: tuple[InterfaceFinding, ...]
    knows_locally: tuple[str, ...]
    can_check_next: tuple[str, ...]
    does_not_yet_know: tuple[str, ...]
    missing_interfaces: tuple[str, ...]
    epistemic_status: str = "F_LOCAL_SOURCE_INVENTORY_ONLY"


@dataclass(frozen=True)
class Candidate:
    question: str
    action: str
    cost: int
    reason: str
    status: str = "I_PROPOSAL"


# Finite grammar implemented *inside the generated child*. It can ask its
# next question and run its own local COUNT action. It cannot edit source.
CHILD_BODY = '''"""A generated bounded MOTIF seed. Inspects input, not its creator's authority."""
from __future__ import annotations
import json
import sys

SPEC = json.loads(__SPEC_JSON__)


def orient(observed):
    if not isinstance(observed, (list, tuple)) or any(not isinstance(x, str) for x in observed):
        raise ValueError('observations must be a list of capability names')
    required = tuple(SPEC['requirements'])
    known = tuple(sorted(set(observed) & set(required)))
    missing = tuple(sorted(set(required) - set(known)))
    return {'known': known, 'missing': missing, 'held': 'general self-construction not established'}


def ask_and_do(observed):
    report = orient(observed)
    if report['missing']:
        question = 'Which required interfaces are still missing?'
        action = 'COUNT_MISSING'
        result = {'count': len(report['missing']), 'names': list(report['missing'])}
    else:
        question = 'Can the declared capability contract be checked locally?'
        action = 'COUNT_VERIFIED_NAMES'
        result = {'count': len(report['known']), 'names': list(report['known'])}
    return {'orientation': report, 'next_question': question, 'action_executed': action,
            'result': result, 'status': 'F_LOCAL_COUNT_ONLY',
            'external_actions': 0, 'can_modify_own_code': False}


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise SystemExit('usage: motif_seed.py <JSON list of capability names>')
    print(json.dumps(ask_and_do(json.loads(sys.argv[1])), sort_keys=True))
'''


CHILD_TEST_BODY = '''"""Independent tests of the generated seed's limited contract."""
import unittest
from motif_seed import SPEC, ask_and_do, orient


class SeedContract(unittest.TestCase):
    def test_full_inventory_selects_validation(self):
        r = ask_and_do(SPEC['requirements'])
        self.assertEqual(r['action_executed'], 'COUNT_VERIFIED_NAMES')
        self.assertEqual(r['result']['count'], len(SPEC['requirements']))
        self.assertEqual(r['external_actions'], 0)

    def test_single_missing_selects_gap(self):
        r = ask_and_do(SPEC['requirements'][:-1])
        self.assertEqual(r['action_executed'], 'COUNT_MISSING')
        self.assertEqual(r['result']['count'], 1)

    def test_empty_and_unrecognized_are_not_admitted(self):
        r = ask_and_do(['invented interface'])
        self.assertEqual(r['result']['count'], len(SPEC['requirements']))
        self.assertFalse(r['orientation']['known'])

    def test_input_validation_and_immutability(self):
        with self.assertRaises(ValueError):
            orient('not-an-inventory')
        with self.assertRaises(ValueError):
            orient(['okay', 42])
        self.assertFalse(ask_and_do(SPEC['requirements'])['can_modify_own_code'])


if __name__ == '__main__':
    unittest.main()
'''


def scan(root: Path, request: str = "How can MOTIF make itself?") -> Orientation:
    """Static local observation. File names and symbols are not proof of behavior."""
    root = Path(root)
    if not root.is_dir():
        raise ValueError("source inventory root must be an existing directory")
    findings = []
    hashes = []
    missing = []
    for component, relative, required in INTERFACES:
        path = root / relative
        if path.is_symlink() or not path.is_file():
            findings.append(InterfaceFinding(component, relative, required, (), required,
                                             None, "HOLD_MISSING_OR_SYMLINK"))
            missing.extend(f"{component}.{name}" for name in required)
            hashes.append((relative, "MISSING_OR_SYMLINK"))
            continue
        data = path.read_bytes()
        file_hash = sha256(data).hexdigest()
        hashes.append((relative, file_hash))
        try:
            parsed = ast.parse(data, filename=relative)
        except (SyntaxError, UnicodeDecodeError):
            findings.append(InterfaceFinding(component, relative, required, (), required,
                                             file_hash, "HOLD_UNPARSEABLE"))
            missing.extend(f"{component}.{name}" for name in required)
            continue
        defined = {x.name for x in parsed.body
                   if isinstance(x, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))}
        present = tuple(name for name in required if name in defined)
        absent = tuple(name for name in required if name not in defined)
        missing.extend(f"{component}.{name}" for name in absent)
        findings.append(InterfaceFinding(component, relative, required, present, absent,
                                         file_hash, "PRESENT_UNVERIFIED" if not absent
                                         else "HOLD_INTERFACE_GAP"))
    digest = sha256(json.dumps(hashes, separators=(",", ":")).encode()).hexdigest()[:24]
    seen = tuple(f"{x.component}.{name} (AST only)" for x in findings for name in x.present)
    return Orientation(
        request, digest, tuple(findings), seen,
        ("Can a generated seed reproduce a bounded next-question/execute cycle?",
         "Do independent tests reject missing interfaces and tampering?",
         "Which integrations can run without external side effects?"),
        ("Whether the interfaces work together in arbitrary environments",
         "Whether any source or build result implies an original general algorithm",
         "Whether a generated program is safe against hostile inputs outside tested scope",
         "Whether the machine can independently build or deploy its full architecture"),
        tuple(missing),
    )


def next_questions(orientation: Orientation, completed: frozenset[str] = frozenset()) -> tuple[Candidate, ...]:
    """The next question depends on actual observed source gaps and progress."""
    if not completed <= ACTIONS:
        raise ValueError("unknown completed actions")
    all_steps = [
        Candidate("What code is actually present, and what remains unverified?",
                  "INSPECT_SOURCE", 1, "Read the current source, not memory of claims."),
        Candidate("Can I construct a bounded child that asks and acts on its next question?",
                  "GENERATE_SEED", 1, "Build a fixed-template child in a designated local staging directory."),
        Candidate("Does the child satisfy its contract on complete, missing, and hostile inputs?",
                  "TEST_SEED", 1, "Execute only the reviewed child and unittest template."),
        Candidate("What can this result justify and what must still be built?",
                  "REPORT_LIMITS", 1, "Preserve the difference between local test success and general self-construction."),
    ]
    if orientation.missing_interfaces:
        all_steps[1] = Candidate("Can I make a minimal seed while preserving missing upstream prerequisites?",
                                 "GENERATE_SEED", 1, "Instantiation is not upstream integration.")
    return tuple(x for x in all_steps if x.action not in completed)


def stage_seed(orientation: Orientation, stage: Path) -> dict:
    """Write exactly two reviewed template files into an empty stage directory."""
    stage = Path(stage)
    if stage.exists() and any(stage.iterdir()):
        raise ValueError("stage must be empty; refusing overwrite")
    stage.mkdir(parents=True, exist_ok=True)
    requirements = [component for component, _, _ in INTERFACES]
    spec = {"schema": "motif.self-build.seed.v1", "requirements": requirements,
            "source_digest": orientation.source_digest, "admission": "I_TEMPLATE_INSTANCE"}
    # The only interpolated input is serialized DATA, never Python syntax.
    serialized = json.dumps(spec, sort_keys=True, separators=(",", ":"))
    source = CHILD_BODY.replace("__SPEC_JSON__", repr(serialized))
    tests = CHILD_TEST_BODY
    (stage / CHILD_FILE).write_text(source, encoding="utf8")
    (stage / CHILD_TEST_FILE).write_text(tests, encoding="utf8")
    return {"kind": "LOCAL_ARTIFACT", "generated": (CHILD_FILE, CHILD_TEST_FILE),
            "source_sha256": sha256(source.encode()).hexdigest(),
            "tests_sha256": sha256(tests.encode()).hexdigest(),
            "parent_source_digest": orientation.source_digest,
            "status": "I_TEMPLATE_INSTANCE_NOT_TESTED", "external_actions": 0}


def test_seed(orientation: Orientation, stage: Path, manifest: dict) -> dict:
    """Run precisely generated source (checked byte-for-byte) in a subprocess.

    -I isolates Python import configuration; it is NOT a general OS sandbox.
    No adversarial code is executed: static templates are compared first.
    """
    stage = Path(stage)
    expected = CHILD_BODY.replace("__SPEC_JSON__", repr(json.dumps({
        "schema": "motif.self-build.seed.v1",
        "requirements": [component for component, _, _ in INTERFACES],
        "source_digest": orientation.source_digest,
        "admission": "I_TEMPLATE_INSTANCE",
    }, sort_keys=True, separators=(",", ":"))))
    source_path, test_path = stage / CHILD_FILE, stage / CHILD_TEST_FILE
    if (not source_path.is_file() or not test_path.is_file()
            or source_path.read_text(encoding="utf8") != expected
            or test_path.read_text(encoding="utf8") != CHILD_TEST_BODY
            or sha256(expected.encode()).hexdigest() != manifest.get("source_sha256")
            or sha256(CHILD_TEST_BODY.encode()).hexdigest() != manifest.get("tests_sha256")
            or manifest.get("parent_source_digest") != orientation.source_digest):
        return {"status": "HOLD_TAMPERED_OR_UNTRUSTED_SOURCE", "tests_passed": False,
                "child_output": None, "external_actions": 0}
    try:
        # Python -I removes the script directory from sys.path for imports.
        # Explicitly execute a fixed tiny -c harness with stage inserted, but
        # *only* after verifying the reviewed template and without arbitrary user code.
        harness = ("import sys,unittest;sys.path.insert(0,sys.argv[1]);"
                   "s=unittest.defaultTestLoader.discover(sys.argv[1],pattern='test_motif_seed.py');"
                   "r=unittest.TextTestRunner(verbosity=0).run(s);"
                   "sys.exit(0 if r.wasSuccessful() and r.testsRun==4 else 1)")
        verified = subprocess.run([sys.executable,"-I","-B","-c",harness,str(stage.resolve())],
                                  cwd=stage,capture_output=True,text=True,timeout=8,check=False)
        observed = subprocess.run([sys.executable,"-I","-B",str(source_path),
                                   json.dumps([component for component, _, _ in INTERFACES])],
                                  cwd=stage,capture_output=True,text=True,timeout=8,check=False)
        child = json.loads(observed.stdout) if observed.returncode == 0 else None
        contract = (verified.returncode == 0 and observed.returncode == 0 and child is not None
                    and child.get("action_executed") == "COUNT_VERIFIED_NAMES"
                    and child.get("result",{}).get("count") == len(INTERFACES)
                    and child.get("external_actions") == 0
                    and child.get("can_modify_own_code") is False)
        return {"status": "F_LOCAL_TEMPLATE_TESTED" if contract else "HOLD_CHILD_TEST_FAILURE",
                "tests_passed": bool(contract), "test_cases": 4 if verified.returncode == 0 else None,
                "child_output": child if contract else None, "external_actions": 0,
                "test_run_exit": verified.returncode, "child_run_exit": observed.returncode,
                "note": "full interface inventory is SPEC data, not independently verified child imports"}
    except (subprocess.TimeoutExpired, ValueError, OSError, json.JSONDecodeError):
        return {"status": "HOLD_CHILD_TEST_FAILURE", "tests_passed": False,
                "child_output": None, "external_actions": 0}


def advance(root: Path, stage: Path, goal: Goal = Goal()) -> dict:
    """Carry out the next permitted questions and local actions without re-prompting.

    The trusted dispatcher decides the action; candidates never grant permissions.
    """
    original = scan(root, goal.question)
    steps: list[dict[str, Any]] = []
    done = frozenset()
    spent = 0
    manifest = None
    tested = None
    for _ in range(goal.max_steps):
        candidates = next_questions(original, done)
        feasible = [x for x in candidates if x.cost <= goal.budget - spent
                    and x.status == "I_PROPOSAL" and x.action in ACTIONS]
        if not feasible:
            break
        chosen = feasible[0]  # dependency order is deliberate, NOT open-ended planning
        if chosen.action == "INSPECT_SOURCE":
            result = {"observed_interfaces": len(original.knows_locally),
                      "missing_interfaces": original.missing_interfaces,
                      "digest": original.source_digest, "status": "F_LOCAL_AST_INSPECTION"}
        elif chosen.action == "GENERATE_SEED":
            manifest = stage_seed(original, stage)
            result = manifest
        elif chosen.action == "TEST_SEED":
            if manifest is None:
                result = {"status": "HOLD_NO_SEED_TO_TEST"}
            else:
                tested = test_seed(original, stage, manifest)
                result = tested
        elif chosen.action == "REPORT_LIMITS":
            result = {"status": "I_SCOPE_REPORT",
                      "can_claim": ["local parsed interface names",
                                    "fixed-template child generated in staging" if manifest else "no child generated",
                                    "four local child contract tests passed" if tested and tested["tests_passed"] else "child unverified"],
                      "cannot_claim": original.does_not_yet_know,
                      "next_question": "Can real cartridge wiring and independent integration checks replace the template?"}
        else:
            raise PermissionError("unknown action cannot be executed")
        steps.append({"next_question": chosen.question, "action": chosen.action,
                      "result": result, "receipt": {"action": chosen.action,
                        "parent_source_digest": original.source_digest,
                        "role": "F_LOCAL" if chosen.action in {"INSPECT_SOURCE", "TEST_SEED"}
                                 and result.get("status", "").startswith("F_LOCAL") else "I",
                        "external_actions": 0}})
        spent += chosen.cost
        done = done | {chosen.action}
    return {"experiment": "SELF-BUILD-001", "question": goal.question,
            "orientation": asdict(original), "steps": steps,
            "status": "F_LOCAL_CHILD_VERIFIED" if tested and tested.get("tests_passed")
                      else "HOLD_NO_VERIFIED_CHILD", "budget_spent": spent,
            "child_can_act_externally": False,
            "general_self_replication": False,
            "source_code_autonomously_changed": False,
            "publication": "NONE"}


def demonstration(root: Path) -> dict:
    with tempfile.TemporaryDirectory(prefix="motif-selfbuild-") as folder:
        result = advance(root, Path(folder) / "staging")
        return {"experiment": result["experiment"],
                "question": result["question"],
                "source_digest": result["orientation"]["source_digest"],
                "present_symbols": len(result["orientation"]["knows_locally"]),
                "missing_interfaces": result["orientation"]["missing_interfaces"],
                "questions_asked": [s["next_question"] for s in result["steps"]],
                "actions_completed": [s["action"] for s in result["steps"]],
                "child_result": next((s["result"] for s in result["steps"]
                                      if s["action"] == "TEST_SEED"), None),
                "status": result["status"], "external_actions": 0,
                "general_self_replication": False}


if __name__ == "__main__":
    # Parent of experiments/selfbuild001 is the experiments inventory directory.
    print(json.dumps(demonstration(Path(__file__).resolve().parents[1]), indent=2,sort_keys=True))
