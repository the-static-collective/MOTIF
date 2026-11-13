"""Run one *reviewed* unmerged experiment in an isolated, no-network container.

This does not grant general execution of every branch. The entire branch
forest is discoverable/readable; runtime profiles are explicitly narrow.
Docker isolation reduces risk but is not a formal security proof.
"""
from __future__ import annotations

import argparse
import io
import json
import os
import subprocess
import tarfile
import tempfile
from pathlib import Path, PurePosixPath

from .branch_garden import HoldError, _git
from .branch_source import observe

PROFILES = {
    "reciprocal-004-smoke": {
        "ref": "experiment/reciprocal-004-ecosystem-crosswire-20261112",
        "paths": ("experiments/reciprocal-002", "experiments/reciprocal-003"),
        "image": "node:22-alpine",
        "commands": (
            ("node", "experiments/reciprocal-002/test_engine.cjs"),
            ("node", "experiments/reciprocal-003/test_research.cjs"),
        ),
        "scope": "Original unmerged synthetic reciprocal JS tests only",
    },
}
MAX_TAR_BYTES = 3_000_000
MAX_FILES = 300
MAX_LOG_BYTES = 16_000


def plan(profile, pointer):
    cfg = PROFILES.get(profile)
    if cfg is None or cfg["ref"] != pointer.ref:
        raise HoldError("No independently reviewed runtime profile for this head")
    return {
        "schema": "motif.branch-execution-plan/v1",
        "profile": profile, "source": pointer.as_dict(),
        "image": cfg["image"],
        "commands": [list(c) for c in cfg["commands"]],
        "scope": cfg["scope"],
        "execution_requested": False,
        "automatic_merge": False,
        "authority": "EXPLICIT_OPERATOR_EXECUTION_ONLY",
        "constraints": ["network:none", "read-only-fs", "no-mounted-credentials",
                        "non-root", "dropped-capabilities", "CPU_RAM_PID_LIMITS",
                        "hard-timeout"],
    }


def _extract_safe_tar(blob, directory, prefixes):
    """Materialize only regular Git files; reject link devices and traversal."""
    total, count = 0, 0
    with tarfile.open(fileobj=io.BytesIO(blob), mode="r:") as tar:
        for member in tar:
            name = member.name.rstrip("/")
            path = PurePosixPath(name)
            if (path.is_absolute() or ".." in path.parts or
                    not any(name == p or name.startswith(p + "/") for p in prefixes)):
                raise HoldError("Unsafe or unexpected Git archive path")
            if not (member.isdir() or member.isfile()):
                raise HoldError("Git archive contains an unsupported link/device")
            dest = directory.joinpath(*path.parts)
            if member.isdir():
                dest.mkdir(parents=True, exist_ok=True)
                dest.chmod(0o755)
                continue
            count += 1
            total += member.size
            if count > MAX_FILES or total > MAX_TAR_BYTES:
                raise HoldError("Archive exceeds execution fixture budget")
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.parent.chmod(0o755)
            stream = tar.extractfile(member)
            if stream is None:
                raise HoldError("File entry could not be materialized")
            data = stream.read(member.size + 1)
            if len(data) != member.size:
                raise HoldError("Unexpected archive file length")
            dest.write_bytes(data)
            dest.chmod(0o644)


def execute(repo, pointer, profile):
    cfg = PROFILES.get(profile)
    summary = plan(profile, pointer)
    # The committed SHA is acquired from the live named ref by observe(),
    # not supplied as arbitrary user text. Same commit is read as Git archive.
    blob = _git(repo, "archive", "--format=tar", pointer.sha, *cfg["paths"],
                max_bytes=MAX_TAR_BYTES)
    with tempfile.TemporaryDirectory(prefix="motif-reviewed-branch-") as tmp:
        root = Path(tmp)
        root.chmod(0o755)
        _extract_safe_tar(blob, root, cfg["paths"])
        outcomes = []
        for command in cfg["commands"]:
            cmd = [
                "docker", "run", "--rm", "--pull=missing",
                "--network=none", "--read-only", "--cap-drop=ALL",
                "--security-opt=no-new-privileges", "--pids-limit=64",
                "--memory=256m", "--cpus=1",
                "--user=65534:65534",
                "--tmpfs=/tmp:size=16m,mode=1777",
                "--mount", "type=bind,source=" + str(root) + ",target=/work,readonly",
                "--workdir=/work", cfg["image"], *command,
            ]
            try:
                run = subprocess.run(cmd, capture_output=True, timeout=90, check=False)
            except (OSError, subprocess.TimeoutExpired) as exc:
                raise HoldError("Isolated runner missing or timed out; HOLD") from exc
            if len(run.stdout) > MAX_LOG_BYTES or len(run.stderr) > MAX_LOG_BYTES:
                raise HoldError("Unbounded test output; HOLD")
            outcomes.append({
                "command": list(command),
                "exit_code": run.returncode,
                "stdout_tail": run.stdout.decode("utf-8", errors="replace")[-4000:],
                "stderr_tail": run.stderr.decode("utf-8", errors="replace")[-4000:],
            })
            if run.returncode != 0:
                break
    summary["execution_requested"] = True
    summary["results"] = outcomes
    summary["status"] = ("HELD_NATIVE_TESTS_PASSED"
                         if len(outcomes) == len(cfg["commands"]) and
                         all(x["exit_code"] == 0 for x in outcomes)
                         else "HELD_NATIVE_TESTS_FAILED")
    summary["executed_source_code_in_isolated_container"] = True
    summary["merge_verdict"] = "KEEP_UNMERGED_PENDING_INDEPENDENT_COMPARISON_AND_OWNER_REVIEW"
    summary["automatic_merge"] = False
    return summary


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--repo", default=".")
    p.add_argument("--ref", required=True)
    p.add_argument("--profile", choices=sorted(PROFILES), required=True)
    p.add_argument("--execute", action="store_true",
                   help="explicitly run the reviewed profile inside Docker")
    args = p.parse_args(argv)
    try:
        pointer = observe(args.repo, args.ref)
        output = execute(args.repo, pointer, args.profile) if args.execute else plan(args.profile, pointer)
    except HoldError as exc:
        print(json.dumps({"disposition": "HOLD", "reason": str(exc)}, indent=2))
        return 2
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0 if output.get("status") != "HELD_NATIVE_TESTS_FAILED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
