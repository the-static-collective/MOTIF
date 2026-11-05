"""Generated MOTIF build runner, copied as a fixed reviewed template.

Runs *only* known, source-pinned MOTIF-002/003/006 handlers in local memory.
This is not a general interpreter or a signed or admitted software package.
"""
from __future__ import annotations
from hashlib import sha256, sha1
import json
from pathlib import Path
import sys

BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE / "experiments" / "door-foundry-001"))
import door_foundry as door

VALID_TARGETS = {"frontier", "macro_replay", "door"}
OWNER_FILES = {
    "experiments/002/motif002.py",
    "experiments/003/affordance.py",
    "experiments/006/composition.py",
    "experiments/door-foundry-001/door_foundry.py",
    "experiments/door-foundry-001/registry.json",
}
AUTHORITY = {
    "contact_people": False,
    "edit_repositories": False,
    "external_execution": False,
    "auto_promote": False,
    "deployment": False,
}


class HOLD(ValueError):
    pass


def canonical(x) -> bytes:
    return json.dumps(x, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False).encode()


def owner_blob(path: Path) -> str:
    b = path.read_bytes()
    return sha1(b"blob " + str(len(b)).encode() + b"\0" + b).hexdigest()


def read_manifest():
    path = BASE / "manifest.json"
    if not path.is_file() or path.stat().st_size > 30000:
        raise HOLD("Manifest missing or oversized")
    try:
        manifest = json.loads(path.read_text())
    except ValueError as exc:
        raise HOLD("Malformed manifest") from exc
    claimed = manifest.get("content_sha256")
    rest = dict(manifest)
    rest.pop("content_sha256", None)
    if claimed != sha256(canonical(rest)).hexdigest():
        raise HOLD("Manifest checksum mismatch")
    if (set(manifest) != {
         "schema", "target", "source_repository", "source_commit",
         "cannon_review_code_commit", "cannon_review_receipt_sha256",
         "selected_capabilities", "copied_owner_files", "runner_sha256",
         "scope", "disposition", "authority", "content_sha256"
         } or manifest["schema"] != "motif.local-build-candidate.v0"
            or manifest["target"] not in VALID_TARGETS
            or manifest["source_repository"] != "the-static-collective/MOTIF"
            or manifest["source_commit"] != "5ee9207f04af2826750863526af7f92b31ef8578"
            or manifest["cannon_review_code_commit"] != "ce54c67f5e830b32a6e754c22da4a1acd51418c0"
            or not isinstance(manifest["cannon_review_receipt_sha256"], str)
            or len(manifest["cannon_review_receipt_sha256"]) != 64
            or manifest["scope"] != "SYNTHETIC_RESEARCH_ONLY"
            or manifest["disposition"] != "LOCAL_BUILD_CANDIDATE_NOT_ADMITTED"
            or manifest["authority"] != AUTHORITY):
        raise HOLD("Manifest changed scope, author, or authority")
    if sha256(Path(__file__).read_bytes()).hexdigest() != manifest["runner_sha256"]:
        raise HOLD("Candidate runner bytes changed")
    if (not isinstance(manifest["copied_owner_files"], dict) or
            set(manifest["copied_owner_files"]) != OWNER_FILES):
        raise HOLD("Unrecognized candidate source files")
    for relative, expected in manifest["copied_owner_files"].items():
        p = (BASE / relative).resolve()
        if (not p.is_relative_to(BASE) or not p.is_file() or
                owner_blob(p) != expected):
            raise HOLD("Copied original source changed: " + relative)
    return manifest


def main():
    m = read_manifest()
    # Verifies original owner source pins and strict registry schema before import.
    two, three, six = door.original_modules()
    caps = door.registry()
    if (not isinstance(m["selected_capabilities"], list) or
            m["selected_capabilities"] != list(door.compose(
                caps, {"world", "goal"}, target=m["target"]))):
        raise HOLD("Generated composition differs from original typed planner")
    names = {c.id: c for c in caps}
    data = {
        "world": two.scene(),
        "goal": frozenset({two.F("skill", "Jo", "repair"),
                         two.F("usable", "bike1"), two.F("usable", "bike2")}),
    }
    for name in m["selected_capabilities"]:
        cap = names[name]
        data[cap.provides] = door.execute_handler(
            cap.handler, data, (two, three, six))
    target = m["target"]
    if target == "door":
        # Original owner implementation includes the fixed classical baseline.
        value = door.run(caps=caps)
        view = {"goal_reached_in_simulation": True,
                "classic_002_also_succeeds":
                    value["fixed_classical_baseline"]["original_002_goal_reached"],
                "native_door_content_sha256": value["content_sha256"],
                "new_affordance_count":
                    value["affordance_first_move"]["new_choice_count"],
                "expanded_primitive_steps":
                    value["replayed_macro"]["expanded_primitive_steps"]}
    elif target == "frontier":
        value = data["frontier"]
        view = {"first_operator": value["first_operator"],
                "new_affordance_count": value["new_choice_count"],
                "candidate_count": value["candidate_count"]}
    else:
        value = data["macro_replay"]
        view = {"macro_operator": value["call"].operator,
                "expanded_primitive_steps": value["expanded_steps"],
                "predicted_new_facts": [list(x)
                                        for x in sorted(value["predicted"] - data["world"])]}
    result = {
        "schema": "motif.candidate-execution.v0",
        "target": target,
        "build_sha256": m["content_sha256"],
        "selected_capabilities": m["selected_capabilities"],
        "result": view,
        "local_synthetic_only": True,
        "no_external_actions": True,
        "no_source_mutation": True,
        "authority": AUTHORITY,
        "status": "EXECUTED_LOCAL_SYNTHETIC_CANDIDATE",
    }
    result["content_sha256"] = sha256(canonical(result)).hexdigest()
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == "__main__":
    try:
        main()
    except (HOLD, door.HOLD) as exc:
        print(json.dumps({"stage": "HOLD", "reason": str(exc)}))
        raise SystemExit(1) from exc
