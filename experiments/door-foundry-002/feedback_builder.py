"""DOOR-FOUNDRY-002: MOTIF receives a CANNON reviewed HOLD receipt and builds
new runnable, local-only MOTIF *configurations* from exact source-pinned organs.

No downloaded code execution, GRAFT invention, promotion, Git pushes, consent
inference, or claim of a novel model. Pinned source is original MOTIF-001 Door
Foundry commit. The CANNON receipt is independently validated, unsigned data.
"""
from __future__ import annotations

import argparse
from hashlib import sha1, sha256
import json
from pathlib import Path
import shutil
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "experiments" / "door-foundry-001"))
import door_foundry as door

SOURCE_COMMIT = "5ee9207f04af2826750863526af7f92b31ef8578"
CANNON_COMMIT = "ce54c67f5e830b32a6e754c22da4a1acd51418c0"
CANNON_SCHEMA = "cannon.door-source-review.v1"
MOTIF_SCHEMA = "motif.local-build-candidate.v0"
CAPABILITY_SCOPE = "SYNTHETIC_PROPOSAL_ONLY"
COPY = (
    "experiments/002/motif002.py",
    "experiments/003/affordance.py",
    "experiments/006/composition.py",
    "experiments/door-foundry-001/door_foundry.py",
    "experiments/door-foundry-001/registry.json",
)
# Only these source files can enter a build; no arbitrary downloaded source.
PINNED = {
    "experiments/002/motif002.py": "b9f1e7b7879a94f7ef3869bc305608c4d7fa8695",
    "experiments/003/affordance.py": "db25da0d50a9c8e2cd87aa576a22f969405737cf",
    "experiments/006/composition.py": "953e1cf4072be5a3ff1f29dcef1edbfc39ba8be0",
    "experiments/door-foundry-001/door_foundry.py": "2b2f9d8ead19cf457ae941706e5a059aff22fe81",
    "experiments/door-foundry-001/registry.json": "906a3610ea9544257bb2bbea00a1083296d9ed55",
    "experiments/door-foundry-001/test_door_foundry.py": "367ddee1463a7fb376a4fe4694d4f5cd1846ed34",
}
TARGETS = ("frontier", "macro_replay", "door")
AUTHORITY = {
    "contact_people": False,
    "edit_repositories": False,
    "external_execution": False,
    "auto_promote": False,
    "deployment": False,
}
RUNNER = HERE / "candidate_runner.py"


class HOLD(ValueError):
    pass


def canonical(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False).encode()


def digest(obj) -> str:
    return sha256(canonical(obj)).hexdigest()


def git_blob(path: Path) -> str:
    raw = path.read_bytes()
    return sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def read_json(path: Path, max_bytes=120000) -> dict:
    if not path.is_file() or path.stat().st_size > max_bytes:
        raise HOLD("Required bounded evidence is absent or oversized")
    try:
        obj = json.loads(path.read_text(encoding="utf8"))
    except (ValueError, UnicodeError) as exc:
        raise HOLD("Invalid evidence JSON") from exc
    if not isinstance(obj, dict):
        raise HOLD("Evidence must be an object")
    return obj


def verify_selection(selection: dict) -> None:
    """CANNON's human-selected source envelope, not authentication or consent."""
    if (selection.get("schema") != "cannon.branch-native-door-selection.v1"
            or selection.get("role") != "SOURCE_SELECTED_FOR_INDEPENDENT_REVIEW"
            or selection.get("source_owner") != "the-static-collective/MOTIF"
            or selection.get("selected_commit") != SOURCE_COMMIT
            or selection.get("scope") != "READ_ONLY_SYNTHETIC_LOCAL_REPLAY"
            or selection.get("disposition") != "HOLD_FOR_INDEPENDENT_RECEIVER_REVIEW"
            or selection.get("denied_outcome") != "HOLD"
            or selection.get("pinned_files") != PINNED):
        raise HOLD("CANNON source selection does not match pinned owner or scope")
    authority = selection.get("authority")
    if not isinstance(authority, dict) or not authority or any(
            value is not False for value in authority.values()):
        raise HOLD("CANNON selection has purported external authority")
    expected = selection.get("expected_capabilities")
    if not isinstance(expected, list) or len(expected) != 5:
        raise HOLD("CANNON expected capabilities missing")
    # The source-native registry is validated separately against the original.
    if (len({r.get("id") for r in expected if isinstance(r, dict)}) != 5):
        raise HOLD("Duplicate CANNON capability")


def verify_receipt(packet: dict, selection: dict) -> str:
    """Authenticate *content consistency* only. A digest is not a signature."""
    if set(packet) != {
        "schema", "source", "selection", "evidence", "disposition",
        "actor_or_receiver_authorized", "external_effects_performed",
        "no_auto_merge", "content_sha256",
    }:
        raise HOLD("Unexpected CANNON receipt fields")
    body = dict(packet)
    claimed = body.pop("content_sha256")
    if (not isinstance(claimed, str) or len(claimed) != 64 or
            claimed != digest(body)):
        raise HOLD("CANNON receipt content digest mismatch")
    src = packet["source"]
    sel = packet["selection"]
    ev = packet["evidence"]
    if not all(isinstance(item, dict) for item in (src, sel, ev)):
        raise HOLD("CANNON receipt structure invalid")
    if (packet["schema"] != CANNON_SCHEMA
            or packet["disposition"] != "HOLD_FOR_INDEPENDENT_RECEIVER_REVIEW"
            or packet["actor_or_receiver_authorized"] is not False
            or packet["external_effects_performed"] is not False
            or packet["no_auto_merge"] is not True
            or src.get("repository") != selection["source_owner"]
            or src.get("selected_commit") != SOURCE_COMMIT
            or src.get("source_is_not_main") is not True
            or src.get("origin_url_is_not_authentication") is not True
            or sel.get("selected_as_canon") is not False
            or sel.get("selected_for_research_review") is not True
            or sel.get("permission_to_execute_externally") is not False
            or sel.get("signature_verified") is not False
            or ev.get("native_owner_tests_passed") is not True
            or ev.get("observed_human_outcome") is not False):
        raise HOLD("CANNON evidence attempts to promote held source")
    files = src.get("exact_source_files")
    if (not isinstance(files, list) or len(files) != len(PINNED) or
            {f.get("path"): f.get("git_blob_sha1") for f in files
             if isinstance(f, dict)} != PINNED):
        raise HOLD("CANNON checked source provenance incomplete")
    check = ev.get("independent_check")
    if (not isinstance(check, dict)
            or check.get("door_status") != "PROPOSED_NOT_OBSERVED"
            or check.get("capabilities_replayed") != 5
            or check.get("original_modules_verified") != 3
            or check.get("simulated_permission_denial") != "HOLD"
            or check.get("ordinary_fixed_planner_also_succeeds") is not True):
        raise HOLD("CANNON independent check does not support build")
    return claimed


def verify_native_source(src: Path) -> None:
    """Require exact original revision, not a mutable branch alias."""
    src = src.resolve()
    try:
        sha = subprocess.check_output(
            ["git", "-C", str(src), "rev-parse", "HEAD"], timeout=5,
            stderr=subprocess.DEVNULL, text=True).strip()
    except (subprocess.SubprocessError, OSError) as exc:
        raise HOLD("Source has no readable Git commit") from exc
    if sha != SOURCE_COMMIT:
        raise HOLD("Owner checkout is not pinned selected commit")
    for path, blob in PINNED.items():
        file = (src / path).resolve()
        if not file.is_relative_to(src) or not file.is_file() or git_blob(file) != blob:
            raise HOLD("Source file absent or changed: " + path)


def verify_contracts(source_root: Path, selected: dict):
    path = source_root / "experiments/door-foundry-001/registry.json"
    raw = json.loads(path.read_text(encoding="utf8"))
    if not isinstance(raw, list) or len(raw) != 5:
        raise HOLD("Wrong native registry size")
    actual = door.registry(path)
    expected = selected["expected_capabilities"]
    for item in actual:
        matches = [x for x in expected if x["id"] == item.id]
        if len(matches) != 1:
            raise HOLD("CANNON registry disagreement")
        x = matches[0]
        if (x["handler"] != item.handler or x["requires"] != list(item.requires)
                or x["provides"] != item.provides or x["source"] != item.source
                or x["state"] != item.state or x["cost"] != item.cost):
            raise HOLD("CANNON expected interface diverges from native code")
    return actual


def plan_builds(caps):
    """MOTIF's existing typed composer derives three different build recipes."""
    result = {}
    for target in TARGETS:
        result[target] = door.compose(caps, {"world", "goal"}, target=target)
    if len({tuple(v) for v in result.values()}) != len(TARGETS):
        raise HOLD("Requested targets collapsed to same build")
    return result


def make_builds(packet_path: Path, selection_path: Path,
                source_root: Path, output_root: Path) -> dict:
    selected = read_json(selection_path)
    packet = read_json(packet_path)
    verify_selection(selected)
    receipt_sha = verify_receipt(packet, selected)
    verify_native_source(source_root)
    caps = verify_contracts(source_root, selected)
    recipes = plan_builds(caps)
    if not RUNNER.is_file():
        raise HOLD("Approved candidate runner missing")
    runner_bytes = RUNNER.read_bytes()
    if len(runner_bytes) > 50000:
        raise HOLD("Runner template too large")
    output_root = output_root.resolve()
    # No overwrite or auto-install into repository. A new empty output directory
    # is required; Path.exists includes files and symlinks.
    if output_root.exists():
        raise HOLD("Output destination already exists")
    output_root.mkdir(parents=True)
    built = []
    for target in TARGETS:
        entry = output_root / ("motif-build-" + target.replace("_", "-"))
        entry.mkdir()
        for relative in COPY:
            dest = entry / relative
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source_root / relative, dest)
            if git_blob(dest) != PINNED[relative]:
                raise HOLD("Copied source failed independent byte check")
        shutil.copyfile(RUNNER, entry / "run.py")
        manifest = {
            "schema": MOTIF_SCHEMA,
            "target": target,
            "source_repository": "the-static-collective/MOTIF",
            "source_commit": SOURCE_COMMIT,
            "cannon_review_code_commit": CANNON_COMMIT,
            "cannon_review_receipt_sha256": receipt_sha,
            "selected_capabilities": list(recipes[target]),
            "copied_owner_files": {name: PINNED[name] for name in COPY},
            "runner_sha256": sha256(runner_bytes).hexdigest(),
            "scope": "SYNTHETIC_RESEARCH_ONLY",
            "disposition": "LOCAL_BUILD_CANDIDATE_NOT_ADMITTED",
            "authority": AUTHORITY,
        }
        manifest["content_sha256"] = digest(manifest)
        (entry / "manifest.json").write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n",
            encoding="utf8")
        built.append({
            "target": target, "folder": entry.name,
            "capabilities": manifest["selected_capabilities"],
            "manifest_sha256": manifest["content_sha256"],
            "status": manifest["disposition"],
        })
    report = {
        "schema": "motif.cannon-build-backloop.v0",
        "origin": "CANNON_UNMERGED_SELECTION",
        "cannon_commit": CANNON_COMMIT,
        "motif_source_commit": SOURCE_COMMIT,
        "cannon_receipt_sha256": receipt_sha,
        "generated": built,
        "real_world_actions": 0,
        "source_changed": False,
        "automatic_git_commits": 0,
        "automatic_promotion": False,
        "field_outcomes_observed": 0,
        "disposition": "HOLD_FOR_OPERATOR_REVIEW",
    }
    report["content_sha256"] = digest(report)
    (output_root / "build-report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf8")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cannon-receipt", type=Path, required=True)
    parser.add_argument("--cannon-selection", type=Path, required=True)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        report = make_builds(args.cannon_receipt, args.cannon_selection,
                             args.source_root, args.output)
        print(json.dumps(report, indent=2, sort_keys=True))
    except HOLD as exc:
        print(json.dumps({"stage": "HOLD", "reason": str(exc),
                          "external_actions_executed": False}))
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
