"""RING-015 host tool bridge; actual tests, no unsandboxed fallback.

All action choices are from TRIAGE/MATH/CONTROL/FULL only; phase and
case are serialized as arguments to a reviewable Docker worker.
No host-network, writable host mounts, credentials, checkout tokens,
unrestricted Python, extra capabilities or Docker daemon in containers.

The source copies contain ONLY reviewed, experimenter-authored mutations;
this is not a safe arbitrary hostile-code execution product.
"""
from __future__ import annotations
from importlib.util import module_from_spec,spec_from_file_location
from pathlib import Path
import json,re,shutil,subprocess,time

HERE=Path(__file__).resolve().parent
spec=spec_from_file_location("ring014_sandbox_preflight",
                             HERE.parent/"cartridge-ring-014"/"runner.py")
prior=module_from_spec(spec)
spec.loader.exec_module(prior)

PHASES=("TRIAGE","MATH","CONTROL","FULL")
SCHEMA="motif.ring015.measured-no-network-sandbox.v1"
IMAGE=prior.IMAGE
SandboxError=prior.SandboxError


def preflight(repo):
    checked=prior.preflight(repo)
    if not (Path(repo)/"experiments"/"cartridge-ring-015"/"worker.py").is_file():
        raise SandboxError("Missing reviewed RING-015 worker")
    return checked


def observe(root,case,phase,repo_root,*,seconds=40):
    if (phase not in PHASES
            or not isinstance(case,str)
            or not re.fullmatch("[a-z0-9-]{4,64}",case)
            or type(seconds) is not int or not 1<=seconds<=60):
        raise SandboxError("Unknown or unapproved code test")
    repo=Path(repo_root).resolve()
    fixtures=Path(root).resolve()
    case_path=fixtures/case
    if not (case_path/"manifest.json").is_file():
        raise SandboxError("No reviewed source-copy manifest")
    manifest=json.loads((case_path/"manifest.json").read_text())
    if manifest.get("case_id")!=case:
        raise SandboxError("Case identity mismatch")
    if not shutil.which("docker"):
        raise SandboxError("Docker mandatory: no host execution fallback")
    cmd=[
        "docker","run","--rm",
        "--network","none","--read-only",
        "--user","65534:65534",
        "--cap-drop","ALL",
        "--security-opt","no-new-privileges",
        "--pids-limit","64","--memory","384m","--cpus","1",
        "--tmpfs","/tmp:rw,nosuid,nodev,size=32m",
        "--env","PYTHONDONTWRITEBYTECODE=1",
        "--env","HOME=/tmp",
        "--mount",f"type=bind,src={repo},dst=/src,readonly",
        "--mount",f"type=bind,src={fixtures},dst=/cases,readonly",
        "--workdir","/src",
        IMAGE,"python","-I","-S",
        "/src/experiments/cartridge-ring-015/worker.py",
        "--case",case,"--phase",phase,
    ]
    started=time.perf_counter()
    try:
        result=subprocess.run(cmd,text=True,capture_output=True,
                              timeout=seconds,check=False)
    except subprocess.TimeoutExpired as exc:
        raise SandboxError("Bounded approved test exceeded wall time") from exc
    wall=round(time.perf_counter()-started,6)
    if (result.returncode!=0 or len(result.stdout)>12000
            or len(result.stderr)>8000):
        raise SandboxError(
            "Docker source test was not auditable: "+result.stderr[-600:])
    try:
        receipt=json.loads(result.stdout.strip())
    except json.JSONDecodeError as exc:
        raise SandboxError("Source test produced no JSON evidence") from exc
    if (receipt.get("schema")!="motif.ring015.observed-source-test-result.v1"
            or receipt.get("case")!=case
            or receipt.get("phase")!=phase
            or receipt.get("source_copy_sha256")!=manifest[
                "tested_copy_sha256"]["value.py"]
            or type(receipt.get("actual_source_tests_passed")) is not bool
            or receipt.get("outside_actions_executed")!=0
            or receipt.get("authority")!="NONE"
            or receipt.get("source_mutation_labels_not_consulted") is not True
            or receipt.get("real_source_assertions_executed",0)<0):
        raise SandboxError("A source result or action permission was forged")
    if phase=="TRIAGE" and receipt.get("observed_source_cue") not in (
            "MATH","CONTROL","MIXED","UNCHANGED","SYNTAX_ERROR","OTHER"):
        raise SandboxError("Unreviewed observation from static triage")
    return {
        "schema":SCHEMA,"case_id":case,"phase":phase,
        "actual_source_tests_passed":receipt["actual_source_tests_passed"],
        "source_cue":receipt.get("observed_source_cue"),
        "reviewed_changed_functions":receipt.get("reviewed_changed_functions"),
        "real_source_assertions_executed":receipt[
            "real_source_assertions_executed"],
        "source_copy_sha256":receipt["source_copy_sha256"],
        "observed_test_failure":receipt.get("observed_test_failure"),
        "measured_wall_seconds":wall,
        "inside_container_seconds":receipt["runtime_seconds_inside_container"],
        "isolation":{
            "network_none":True,"readonly_root":True,
            "source_readonly":True,"fixture_readonly":True,
            "uid_unprivileged":True,"cap_drop_all":True,
            "no_new_privileges":True,"resource_budgets":True,
            "no_host_docker_socket":True,
        },
        "source_labels_not_supplied_to_planner":True,
        "host_approved_method_only":True,
        "external_effects_executed":0,"authority":"NONE",
    }
