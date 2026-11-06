"""RING-002: source-native, separately isolated THREE-CARTRIDGE experiment.

Only these explicitly pinned adapters are executable. All other branches are
catalogued as read-only source pointers. Every source-native demonstration
is synthetic, so a joint receipt is NOT a validated answer to a shared real
problem. Docker with no network and readonly mounts is required, never optional.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from hashlib import sha256
import io
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
import tarfile
import tempfile

@dataclass(frozen=True)
class PinnedAdapter:
    id: str
    source_ref: str
    commit: str
    directory: str
    entrypoint: str
    artifact_kind: str

ADAPTERS = (
    PinnedAdapter(
        "geometry.procedure-repair",
        "experiment/geometry-013-self-redesigning-instrument",
        "a3dc551ababa40c29975c9b54c4eaa515d9dc18c",
        "experiments/geometry-013", "demo.py", "synthetic.measurement-procedure"),
    PinnedAdapter(
        "thought.language-dev",
        "experiment/thought-014-native-language-selfdev",
        "a38c617641adffe52cd4df283996a58f0fe7b973",
        "experiments/thought-014", "demo.py", "synthetic.language-interpretation"),
    PinnedAdapter(
        "reason.proof-objection",
        "experiment/reason-cartridge-006-reasoning-commonwealth",
        "d0808c6a829fc6ef15d736c325790ddb4d169ab1",
        "experiments/reason-cartridge-006", "trial.py", "synthetic.proof-reconsideration"),
)
BY_ID = {c.id: c for c in ADAPTERS}
SCHEMA = "motif.triad-adapter-receipt.v1"


class HOLD(ValueError):
    pass


def choose(requested):
    """Typed demand, never guess human intent or execute unknown branch names."""
    if not isinstance(requested, (tuple, list)) or len(requested) > len(ADAPTERS):
        raise HOLD("Invalid requested cartridge set")
    if any(type(x) is not str or x not in BY_ID for x in requested):
        raise HOLD("Unknown or unadmitted executable cartridge")
    if len(set(requested)) != len(requested):
        raise HOLD("Repeated cartridge request")
    return tuple(sorted((BY_ID[x] for x in requested), key=lambda a: a.id))


def _run(cmd, *, cwd, timeout=90, max_stdout=2_500_000):
    try:
        p = subprocess.run(cmd, cwd=cwd, capture_output=True,
                           text=True, timeout=timeout, check=False,
                           env={"PATH": os.environ.get("PATH", "/usr/bin:/bin"),
                                "LANG": "C.UTF-8"})
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise HOLD("Pinned source fetch or isolated adapter failed") from exc
    if p.returncode != 0 or len(p.stdout) > max_stdout:
        raise HOLD("Pinned source fetch / adapter failed or exceeded output bound: "
                   + p.stderr.strip()[-400:])
    return p.stdout.strip()


def _extract_experiments(commit, destination, *, repo_root):
    """Read the exact git commit, not today's mutable branch tip."""
    actual = _run(["git", "rev-parse", commit + "^{commit}"],
                  cwd=repo_root, timeout=10).strip()
    if actual != commit:
        raise HOLD("Pinned source commit unavailable; run git fetch first")
    try:
        b = subprocess.run(
            ["git", "archive", "--format=tar", commit, "experiments"],
            cwd=repo_root, capture_output=True, check=False, timeout=45,
            env={"PATH": os.environ.get("PATH", "/usr/bin:/bin")})
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise HOLD("Pinned git archive unavailable") from exc
    if b.returncode or len(b.stdout) > 40_000_000:
        raise HOLD("Pinned archive missing or exceeds 40 MB")
    total = 0
    with tarfile.open(fileobj=io.BytesIO(b.stdout), mode="r:") as tar:
        members = tar.getmembers()
        if len(members) > 5000:
            raise HOLD("Excessive archive file count")
        for m in members:
            pp = PurePosixPath(m.name)
            if (pp.is_absolute() or ".." in pp.parts or
                    not (pp.parts and pp.parts[0] == "experiments") or
                    not (m.isdir() or m.isfile())):
                raise HOLD("Unsafe source archive entry")
            total += m.size
            if total > 50_000_000:
                raise HOLD("Source tree exceeds 50 MB")
        for m in members:
            target = destination.joinpath(*PurePosixPath(m.name).parts)
            if m.isdir():
                target.mkdir(parents=True, exist_ok=True)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                src = tar.extractfile(m)
                if src is None:
                    raise HOLD("Malformed source archive")
                with open(target, "wb") as stream:
                    shutil.copyfileobj(src, stream)


def _validate(adapter, result):
    if not isinstance(result, dict):
        raise HOLD("Adapter did not return a JSON object")
    if adapter.id == "geometry.procedure-repair":
        if (result.get("experiment") != "GEOM-013 self-redesigning measurement instrument"
                or result.get("state") != "PENCIL"
                or result.get("authority") != "NONE"
                or not isinstance(result.get("summary", {}).get("inserted_steps"), list)
                or len(result["summary"]["inserted_steps"]) < 2):
            raise HOLD("Geometry schema, scope or method result invalid")
        return {"method": "bounded-duplicate-aware measurement revision",
                "revised_record_id_steps": len(result["summary"]["inserted_steps"]),
                "first_revision_status": result.get("first_revision", {}).get("status"),
                "second_revision_status": result.get("second_revision", {}).get("status")}
    if adapter.id == "thought.language-dev":
        if (result.get("schema") != "motif.thought014.demo.v1"
                or result.get("authority") != "NONE"
                or result.get("installed") is not False
                or result.get("staged_only") is not True
                or not isinstance(result.get("language_frozen_correct"), list)):
            raise HOLD("Language-source schema or uninstalled candidate guarantee invalid")
        return {"method": "bounded tiny trained text classifier / language rules",
                "frozen_accuracy_counts": result["language_frozen_correct"],
                "model_inference_calls": result.get("model_inference_calls"),
                "language_rules_staged": result.get("language_rules_staged"),
                "candidate_rules_installed": False}
    if adapter.id == "reason.proof-objection":
        if (result.get("schema") != "motif.reason.commonwealth-benchmark.v1"
                or result.get("real_world_authority") is not False
                or result.get("external_actions") is not False
                or result.get("native_foreign_teacher_mode") != "NOT_RUN_LOCAL_ONLY"
                or not isinstance(result.get("source_owner_tests"), list)
                or len(result["source_owner_tests"]) != 5):
            raise HOLD("Reasoning-commonwealth local benchmark schema invalid")
        return {"method": "source-owned proof/objection/question council",
                "synthetic_cases": len(result["source_owner_tests"]),
                "source_reviews": result.get("source_reviews"),
                "changed_conclusions": result.get(
                    "new_conclusions_from_local_fixture_reviews"),
                "foreign_teacher": "NOT_RUN_LOCAL_ONLY"}
    raise HOLD("Unregistered adapter")


def probe(adapter: PinnedAdapter, *, repo_root: Path, python_image: str):
    # The Docker daemon gets no GitHub token, checkout credentials, network, or
    # host socket. Only an ephemeral read-only copy of pinned source is mounted.
    if shutil.which("docker") is None:
        raise HOLD("Docker is required for no-network isolated source execution")
    with tempfile.TemporaryDirectory(prefix="motif-triad-") as td:
        folder = Path(td)
        folder.chmod(0o755)  # unprivileged container can traverse its read-only mount
        _extract_experiments(adapter.commit, folder, repo_root=repo_root)
        cmd = [
            "docker", "run", "--rm", "--network", "none", "--read-only",
            "--cap-drop", "ALL", "--security-opt", "no-new-privileges",
            "--pids-limit", "96", "--memory", "768m", "--cpus", "1.0",
            "--user", "65534:65534", "--tmpfs", "/tmp:rw,noexec,nosuid,size=64m",
            "--mount", "type=bind,source=" + str(folder) + ",target=/work,readonly",
            "--workdir", "/work/" + adapter.directory,
            python_image, "python", "-B", adapter.entrypoint,
        ]
        output = _run(cmd, cwd=repo_root, timeout=120)
        try:
            result = json.loads(output)
        except ValueError as exc:
            raise HOLD("Native source result is not strict JSON") from exc
        summary = _validate(adapter, result)
        return {
            "adapter": adapter.id,
            "source_ref_observed_initially": adapter.source_ref,
            "source_commit": adapter.commit,
            "artifact_kind": adapter.artifact_kind,
            "source_native_demo": True,
            "this_is_synthetic_not_shared_real_evidence": True,
            "isolated_no_network_read_only": True,
            "reduced_result": summary,
            "native_receipt_sha256": sha256(
                json.dumps(result, sort_keys=True, separators=(",", ":")).encode()
            ).hexdigest(),
        }


def run(requested, *, repo_root: Path, python_image="python:3.11-slim",
        concurrent=True):
    selected = choose(requested)
    if len(selected) == 0:
        receipt = {"schema": SCHEMA, "status": "IDLE",
                   "selected": [], "results": [],
                   "external_action_executed": False, "authority": "NONE"}
    else:
        if concurrent and len(selected) > 1:
            with ThreadPoolExecutor(max_workers=len(selected)) as pool:
                futures = [pool.submit(probe, x, repo_root=repo_root,
                                       python_image=python_image) for x in selected]
                results = [f.result() for f in futures]
        else:
            results = [probe(x, repo_root=repo_root, python_image=python_image)
                       for x in selected]
        receipt = {
            "schema": SCHEMA,
            "status": "SOURCE_NATIVE_SYNTHETIC_TRIAL",
            "selected": [x.id for x in selected],
            "results": results,
            "no_inference_transfer_across_distinct_synthetic_worlds": True,
            "cross_method_compatibility": "UNPROVEN",
            "automatically_approved_additional_branches": 0,
            "external_action_executed": False,
            "authority": "NONE",
        }
    payload = json.dumps(receipt, sort_keys=True, separators=(",", ":"))
    receipt["receipt_sha256"] = sha256(payload.encode()).hexdigest()
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--select", nargs="*", default=[x.id for x in ADAPTERS])
    parser.add_argument("--serial", action="store_true")
    parser.add_argument("--repo-root", type=Path,
                        default=Path(__file__).resolve().parents[2])
    parser.add_argument("--image", default="python:3.11-slim")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        result = run(tuple(args.select), repo_root=args.repo_root,
                     python_image=args.image, concurrent=not args.serial)
        output = json.dumps(result, sort_keys=True, indent=2) + "\n"
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(output)
            print(json.dumps({"status": result["status"],
                              "receipt_sha256": result["receipt_sha256"],
                              "output": str(args.output)}, sort_keys=True))
        else:
            print(output, end="")
    except HOLD as exc:
        print(json.dumps({"status": "HOLD", "reason": str(exc),
                          "no_external_effect": True}), file=sys.stderr)
        raise SystemExit(2)


if __name__ == "__main__":
    main()
