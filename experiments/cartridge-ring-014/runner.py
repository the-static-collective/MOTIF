"""RING-014 host bridge. Every allowed action runs REAL source-owned tests.

Execution boundary:
  Docker, --network none, --read-only, --cap-drop ALL,
  no-new-privileges, unprivileged UID, memory/CPU/PID quotas, tiny tmpfs,
  explicit read-only mounts for reviewed source and generated fixture copies,
  no Docker socket, no cloud tokens, no GitHub credentials.

No silent host-Python fallback. A failed Docker invocation is a tool error,
not a test PASS, and never triggers a network or permission workaround.
Only the fixed phase enum and generated reviewed source case ID can execute.

NOTE: Docker isolation is a practical research boundary, not a security proof
for arbitrary hostile code; this runner accepts reviewed repo source only.
"""
from __future__ import annotations
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import time

import fixtures

IMAGE="python:3.11-slim"
PHASES=("AST","SMOKE","DEEP")
SCHEMA="motif.ring014.audited-isolated-source-execution.v1"

class SandboxError(RuntimeError):
    pass


def observe(case_dir,case,phase,repo_root,*,seconds=35):
    if (phase not in PHASES
            or not re.fullmatch("[a-z0-9-]{4,64}",case)
            or type(seconds) is not int or not 1<=seconds<=60):
        raise SandboxError("Unrecognized executable cartridge")
    source=Path(repo_root).resolve()
    fixtures_root=Path(case_dir).resolve()
    # Even with --read-only mounting, the source and generated case need
    # to be the intended reviewed files, not arbitrary host paths.
    if not (source/"experiments"/"cartridge-ring-014"/"worker.py").is_file():
        raise SandboxError("Reviewed source entrypoint unavailable")
    case_path=fixtures_root/case
    if not (case_path/"manifest.json").is_file():
        raise SandboxError("Explicit source case manifest missing")
    if not shutil.which("docker"):
        raise SandboxError("Docker required: no unsandboxed execution fallback")
    manifest=json.loads((case_path/"manifest.json").read_text())
    if manifest.get("case_id")!=case:
        raise SandboxError("Fixture manifest case identity mismatch")
    cmd=[
        "docker","run","--rm",
        "--network","none",
        "--read-only",
        "--user","65534:65534",
        "--cap-drop","ALL",
        "--security-opt","no-new-privileges",
        "--pids-limit","64",
        "--memory","384m",
        "--cpus","1",
        "--tmpfs","/tmp:rw,nosuid,nodev,size=32m",
        "--env","PYTHONDONTWRITEBYTECODE=1",
        "--env","HOME=/tmp",
        "--mount",f"type=bind,src={source},dst=/src,readonly",
        "--mount",f"type=bind,src={fixtures_root},dst=/cases,readonly",
        "--workdir","/src",
        IMAGE,
        "python","-I","-S",
        "/src/experiments/cartridge-ring-014/worker.py",
        "--case",case,"--phase",phase,
    ]
    wall_start=time.perf_counter()
    try:
        p=subprocess.run(
            cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
            text=True,timeout=seconds,check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise SandboxError(f"Bounded {phase} test exceeded {seconds}s") from exc
    elapsed=round(time.perf_counter()-wall_start,6)
    if p.returncode!=0:
        raise SandboxError(
            f"Sandbox command failed with exit={p.returncode}: "
            +p.stderr[-650:])
    if len(p.stdout)>16000 or len(p.stderr)>10000:
        raise SandboxError("Sandbox exceeded bounded evidence output")
    try:
        out=json.loads(p.stdout.strip())
    except json.JSONDecodeError as exc:
        raise SandboxError("Sandbox returned no machine-readable source receipt") from exc
    if (out.get("schema")!="motif.ring014.measured-source-test-outcome.v1"
            or out.get("case")!=case
            or out.get("phase")!=phase
            or out.get("source_copy_sha256")!=manifest[
                "tested_copy_sha256"]["value.py"]
            or out.get("external_effects")!=0
            or out.get("sandbox_claim")!="DOCKER_RUNTIME_ENFORCED_BY_HOST"
            or type(out.get("ok")) is not bool):
        raise SandboxError("Wrong source receipt, swapped case or unreviewed effect")
    return {
        "schema":SCHEMA,
        "case":case,"phase":phase,
        "actual_source_tests_passed":out["ok"],
        "real_source_assertions_executed":out[
            "executed_real_source_tests"],
        "observed_test_failure":out.get("test_error"),
        "source_copy_sha256":out["source_copy_sha256"],
        "sandbox_elapsed_wall_seconds":elapsed,
        "inside_runtime_seconds":out["runtime_seconds_inside_container"],
        "isolation_controls":{
            "docker_network_disabled":True,
            "root_fs_readonly":True,
            "source_mount_readonly":True,
            "fixture_mount_readonly":True,
            "no_host_docker_socket":True,
            "unprivileged_user":True,
            "capabilities_dropped":True,
            "no_new_privileges":True,
            "cpu_memory_pids_bounded":True,
        },
        "sandbox_is_not_arbitrary_hostile_code_security_proof":True,
        "user_private_source_executed":False,
        "outside_actions_executed":0,
        "no_unreviewed_code_execution":True,
    }


def preflight(repo_root):
    if not shutil.which("docker"):
        raise SandboxError("Docker not available; refuse host fallback")
    result=subprocess.run(["docker","image","inspect",IMAGE],
                          capture_output=True,text=True,timeout=15)
    if result.returncode!=0:
        raise SandboxError("Pinned Docker image tag not yet provisioned")
    root=fixtures.root_for_source(repo_root)
    return {
        "source_files":{
            name:sha256((root/name).read_bytes()).hexdigest()
            for name in fixtures.SOURCE
        },
        "image":IMAGE,
        "docker_available":True,
        "network_disabled_for_every_actual_test":True,
        "read_only_inputs":True,
        "no_untrusted_method_fallback":True,
    }
