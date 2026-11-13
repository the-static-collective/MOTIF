"""MOTIF Method Tournament 003 — source-owned branch algorithm versus matched controls.

A *reviewed* unmerged research implementation can be evaluated as a pinned,
temporary donor without merging or installing it. Strong classical controls
and adverse context shifts are mandatory; failures remain in the receipt.

This is an explicitly invoked local CLI. It uses a fixed Docker image and
read-only / no-network execution, not an arbitrary code runner. The keeper is
a HELD, content-addressed source locator, not a new approved executable method.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import tempfile
from pathlib import Path

from .branch_garden import HoldError, _git
from .branch_runner import _extract_safe_tar, MAX_TAR_BYTES
from .branch_source import observe, read_text
from .source_council import score_docs

PROFILE = {
    "id": "reciprocal-003-role-predictor",
    "source_branch": "experiment/reciprocal-004-ecosystem-crosswire-20261112",
    "reviewed_source_commit": "586be3530d2b5b4d41f810515f9c457d2a27a371",
    "module": "experiments/reciprocal-003/reason_loop.js",
    "source_paths": (
        "experiments/reciprocal-002",
        "experiments/reciprocal-003",
    ),
    "source_docs": (
        "experiments/reciprocal-003/README.md",
        "experiments/reciprocal-003/PREREGISTRATION.md",
    ),
    "fixed_commands": (
        ("node", "experiments/reciprocal-002/test_engine.cjs"),
        ("node", "experiments/reciprocal-003/test_research.cjs"),
        ("node", "evaluation/evaluate.cjs", "evaluation/fixtures.v1.json"),
    ),
    "image": "node:22-alpine",
}
ROOT = Path(__file__).resolve().parent.parent
HARNESS = ROOT / "experiments" / "method-tournament-003"
FIXTURE = HARNESS / "fixtures.v1.json"
EVALUATOR = HARNESS / "evaluate.cjs"
MAX_STDOUT = 64000
MAX_RECEIPT = 100000
RECEIPT_SCHEMA = "motif.held-method-receipt/v1"
SCORE_SCHEMA = "motif.method-tournament-scorecard/v1"


def _canonical(data):
    return json.dumps(data, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("utf-8")


def _digest(data):
    return hashlib.sha256(_canonical(data)).hexdigest()


def _bounded_file(path, max_size):
    try:
        payload = path.read_bytes()
    except OSError as exc:
        raise HoldError("Required independent harness unavailable") from exc
    if len(payload) > max_size:
        raise HoldError("Independent harness exceeds budget")
    return payload


def select_reviewed_source(repo, query):
    """Use actual original source documents to select ONE reviewed donor profile.

    No compatibility is inferred from names alone. Future profiles must be
    individually reviewed rather than accepted from discovered source claims.
    """
    if not isinstance(query, str) or not 3 <= len(query) <= 180 or not query.strip():
        raise HoldError("A bounded consequential research query is required")
    source = observe(repo, PROFILE["source_branch"])
    if source.sha != PROFILE["reviewed_source_commit"]:
        raise HoldError("Donor head changed since source review; refuse unreviewed code execution")
    docs = [read_text(repo, source, p, include_text=True)
            for p in PROFILE["source_docs"]]
    signals = score_docs(query, docs, list(PROFILE["source_paths"]) + [PROFILE["module"]])
    if not signals["document_terms_matched"]:
        raise HoldError("No source-document match: do not execute an unrelated method")
    return source, signals


def _run_isolated(folder, argv):
    command = [
        "docker", "run", "--rm", "--pull=never",
        "--network=none", "--read-only", "--cap-drop=ALL",
        "--security-opt=no-new-privileges", "--pids-limit=64",
        "--memory=256m", "--cpus=1", "--user=65534:65534",
        "--tmpfs=/tmp:size=16m,mode=1777",
        "--mount", "type=bind,source=" + str(folder) + ",target=/work,readonly",
        "--workdir=/work", PROFILE["image"], *argv,
    ]
    try:
        p = subprocess.run(command, capture_output=True, timeout=60, check=False,
                           env={"PATH": os.environ.get("PATH", "/usr/bin:/bin"),
                                "HOME": "/nonexistent"})
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise HoldError("Reviewed donor runner unavailable or exceeded time budget") from exc
    if len(p.stdout) > MAX_STDOUT or len(p.stderr) > MAX_STDOUT:
        raise HoldError("Reviewed donor produced unbounded output")
    if p.returncode:
        raise HoldError("Original source native test or independent tournament failed")
    try:
        return p.stdout.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise HoldError("Original runner produced non-text output") from exc


def _verified_scorecard(text, fixture_sha):
    prefix = "MOTIF_TOURNAMENT_RESULT "
    lines = [l[len(prefix):] for l in text.splitlines() if l.startswith(prefix)]
    if len(lines) != 1:
        raise HoldError("Missing or multiple independent scorecards")
    try:
        score = json.loads(lines[0])
    except json.JSONDecodeError as exc:
        raise HoldError("Invalid independent scorecard") from exc
    if (score.get("schema") != SCORE_SCHEMA or
        score.get("fixture_sha256") != fixture_sha or
        score.get("original_native_algorithm_executed") is not True or
        score.get("independent_future_separate_from_candidate_input") is not True or
        score.get("independent_strong_baseline_implemented") is not True or
        score.get("reliable_improvement_over_strong_classical") is not False or
        score.get("disposition") != "RETAIN_SOURCE_POINTER_HELD_NOT_INSTALL" or
        score.get("automatic_merge") is not False or
        score.get("external_action") is not False or
        score.get("real_human_reports") is not False):
        raise HoldError("Scorecard attempts to overclaim source capability")
    cases = score.get("cases")
    if not isinstance(cases, list) or len(cases) != 6:
        raise HoldError("Independent cases missing")
    aggregate = score.get("aggregate_on_proposed_only", {})
    if aggregate.get("candidate_minus_strong_correct") != 0:
        raise HoldError("Claimed superiority over independently matched strong control")
    if not aggregate.get("cases_regressing_vs_global"):
        raise HoldError("Adverse transfer test did not expose an actual regression")
    return score


def assemble_held_receipt(source, signals, score, fixture_sha):
    body = {
        "schema": RECEIPT_SCHEMA,
        "profile": PROFILE["id"],
        "owner": "the-static-collective/MOTIF",
        "source_branch": source.ref,
        "source_commit": source.sha,
        "source_module": PROFILE["module"],
        "source_status": "UNMERGED_ORIGINAL_EXPERIMENT",
        "source_documents": signals["source_witnesses"],
        "independent_harness_sha256": {
            "fixtures": fixture_sha,
            "evaluator": hashlib.sha256(_bounded_file(EVALUATOR, 65536)).hexdigest(),
        },
        "scorecard": score,
        "source_runtime": "ORIGINAL_UNMERGED_CODE_EXECUTED_IN_FIXED_NO_NETWORK_CONTAINER",
        "retained_kind": "HELD_CONTENT_ADDRESSED_SOURCE_LOCATOR",
        "candidate_reuse": "OPERATOR_MAY_RERUN_FIXED_PROFILE_AFTER_REVERIFYING_SOURCE",
        "independent_strong_control_won": False,
        "real_world_transfer_proven": False,
        "method_installed": False,
        "automatic_merge": False,
        "merging_authority": "NONE",
        "operator_review_required": True,
        "next_gate": "NEW_UNSEEN_TASKS_AND_STRONGER_CLASSICAL_BENCHMARKS",
    }
    return {"content": body, "content_sha256": _digest(body),
            "digest_is_not_authenticity": True}


def verify_receipt(data):
    if (not isinstance(data, dict) or
        data.get("digest_is_not_authenticity") is not True or
        not isinstance(data.get("content"), dict) or
        data.get("content_sha256") != _digest(data["content"])):
        raise HoldError("Tampered, invalid or absent held receipt")
    c = data["content"]
    if (c.get("schema") != RECEIPT_SCHEMA or
        c.get("profile") != PROFILE["id"] or
        c.get("owner") != "the-static-collective/MOTIF" or
        c.get("source_branch") != PROFILE["source_branch"] or
        c.get("source_module") != PROFILE["module"] or
        c.get("retained_kind") != "HELD_CONTENT_ADDRESSED_SOURCE_LOCATOR" or
        c.get("source_status") != "UNMERGED_ORIGINAL_EXPERIMENT" or
        not isinstance(c.get("source_commit"), str) or
        len(c["source_commit"]) != 40 or
        not all(v in "0123456789abcdef" for v in c["source_commit"]) or
        c.get("method_installed") is not False or
        c.get("automatic_merge") is not False or
        c.get("independent_strong_control_won") is not False or
        c.get("real_world_transfer_proven") is not False):
        raise HoldError("Receipt tried to grant method authority")
    return c


def run(repo, query, execute=False, receipt=None):
    source, signals = select_reviewed_source(repo, query)
    old = verify_receipt(receipt) if receipt is not None else None
    if old and source.sha != old["source_commit"]:
        raise HoldError("Source branch moved since retained receipt; review and rerun")
    fixture = _bounded_file(FIXTURE, 65536)
    evaluator = _bounded_file(EVALUATOR, 65536)
    fixture_sha = hashlib.sha256(fixture).hexdigest()
    preview = {
        "schema": "motif.method-tournament-plan/v1",
        "source": source.as_dict(),
        "profile": PROFILE["id"],
        "selection": signals,
        "fixture_sha256": fixture_sha,
        "evaluator_sha256": hashlib.sha256(evaluator).hexdigest(),
        "fixed_original_commands": [list(c) for c in PROFILE["fixed_commands"]],
        "execution_requested": bool(execute),
        "live_people": False,
        "external_actions": False,
        "automatic_merge": False,
        "method_installed": False,
        "retained_receipt_reused": old is not None,
        "source_branch_compared_but_not_merged": True,
        "status": "PREVIEW_NO_DONOR_EXECUTION",
    }
    if not execute:
        return preview
    blob = _git(repo, "archive", "--format=tar", source.sha,
                *PROFILE["source_paths"], max_bytes=MAX_TAR_BYTES)
    with tempfile.TemporaryDirectory(prefix="motif-method-tournament-") as tmp:
        base = Path(tmp)
        base.chmod(0o755)
        _extract_safe_tar(blob, base, PROFILE["source_paths"])
        eval_dir = base / "evaluation"
        eval_dir.mkdir(mode=0o755)
        (eval_dir / "evaluate.cjs").write_bytes(evaluator)
        (eval_dir / "fixtures.v1.json").write_bytes(fixture)
        for file in eval_dir.iterdir():
            file.chmod(0o644)
        trial_results = []
        for argv in PROFILE["fixed_commands"]:
            out = _run_isolated(base, argv)
            if argv[1] == "evaluation/evaluate.cjs":
                score = _verified_scorecard(out, fixture_sha)
                trial_results.append({"command": list(argv),
                                      "verified": True, "output_kind": SCORE_SCHEMA})
            else:
                trial_results.append({"command": list(argv),
                                      "verified": True, "output_kind": "NATIVE_ORIGINAL_TEST_SUITE"})
    result = assemble_held_receipt(source, signals, score, fixture_sha)
    return {
        **preview,
        "status": "ORIGINAL_DONOR_EXECUTED_AND_STRONG_CLASSICAL_TOURNAMENT_COMPLETE",
        "native_runs": trial_results,
        "scorecard": score,
        "held_receipt": result,
        "automatic_reuse_or_install": False,
        "retention": "HELD_PACKET_CAN_BE_SAVED_AND_REUSED_WITHOUT_MERGING",
    }


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--repo", default=".")
    p.add_argument("--query", default="reciprocal role-conditioned prediction")
    p.add_argument("--execute", action="store_true",
                   help="Explicitly invoke fixed Docker runner; never automatic")
    p.add_argument("--receipt", help="Prior retained HELD locator to verify/reuse")
    p.add_argument("--out", help="Opt-in create-only JSON result file, e.g. /tmp/motif-tournament.json")
    args = p.parse_args(argv)
    try:
        prior = None
        if args.receipt:
            source = Path(args.receipt)
            if source.stat().st_size > MAX_RECEIPT:
                raise HoldError("Oversized retained receipt")
            prior = json.loads(source.read_text("utf-8"))
            if isinstance(prior, dict) and "held_receipt" in prior:
                prior = prior["held_receipt"]
        result = run(args.repo, args.query, args.execute, prior)
        payload = json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n"
        if args.out:
            target = Path(args.out)
            with target.open("x", encoding="utf-8") as stream:
                stream.write(payload)
        print(payload)
        return 0
    except (HoldError, OSError, ValueError, TypeError, KeyError,
            json.JSONDecodeError) as exc:
        print(json.dumps({"disposition": "HOLD", "reason": str(exc),
                          "automatic_merge": False, "method_installed": False}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
