"""A new MOTIF build with an actual GRAFT-GENERATED new executable sensor.

The generated JavaScript is content-pinned and only reads bounded JSON input.
Its result controls which declared original MOTIF-003 hypothetical policy to
apply. Neither numeric measurements nor actions are real-world observations.
"""
from __future__ import annotations
from hashlib import sha1, sha256
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
PINS = {
    "experiments/002/motif002.py": "b9f1e7b7879a94f7ef3869bc305608c4d7fa8695",
    "experiments/003/affordance.py": "db25da0d50a9c8e2cd87aa576a22f969405737cf",
}
AUTHORITY = {
    "network": False, "external_execution": False,
    "production_install": False, "automatic_canon": False,
    "repo_mutation": False, "human_contact": False,
}


class HOLD(ValueError):
    pass


def jsdigest(obj):
    return sha256(json.dumps(obj, separators=(",", ":"), ensure_ascii=False,
                             allow_nan=False).encode()).hexdigest()


def git_blob(path):
    data = path.read_bytes()
    return sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def manifest():
    path = ROOT / "manifest.json"
    if not path.is_file() or path.stat().st_size > 30000:
        raise HOLD("Bounded build manifest absent or oversized")
    try:
        m = json.loads(path.read_text())
    except ValueError as exc:
        raise HOLD("Malformed build") from exc
    content = dict(m)
    claimed = content.pop("content_sha256", None)
    if claimed != jsdigest(content):
        raise HOLD("Changed build manifest")
    if (m.get("schema") != "motif.graft-born-local-organ.v0"
            or m.get("operator_kind") != "GRAFT_GENERATED_NEW_EXECUTABLE_NUMERIC_PROJECTION"
            or m.get("graft_source_commit") != "6ff59aead0296081e1547d8107e4b6f06ea2381e"
            or m.get("cannon_source_commit") != "0fd326c1bb6f222dc572a4877818d63881828801"
            or m.get("motif_original_commit") != "5ee9207f04af2826750863526af7f92b31ef8578"
            or m.get("selector") != ["observed", "reachable_actions"]
            or m.get("authority") != AUTHORITY
            or m.get("scope") != "SYNTHETIC_SOURCE_FIXTURE_ONLY"
            or m.get("status") != "HELD_LOCAL_EXECUTABLE_NOT_ADMITTED"
            or m.get("motif_source_pins") != PINS
            or type(m.get("baseline",{}).get("fair_classical_superiority_proven")) is not bool
            or m["baseline"]["fair_classical_superiority_proven"] is not False):
        raise HOLD("Build scope or ownership changed")
    for name, expected in PINS.items():
        file = (ROOT / name).resolve()
        if not file.is_relative_to(ROOT) or not file.is_file() or git_blob(file) != expected:
            raise HOLD("Original source file changed")
    for name, field in (("generated_sensor.mjs","generated_source_sha256"),
                        ("run.py","runner_sha256"),
                        ("observe.mjs","bridge_sha256")):
        file = ROOT / name
        if not file.is_file() or sha256(file.read_bytes()).hexdigest() != m[field]:
            raise HOLD("Compiled source or runner integrity mismatch")
    cases = m.get("final_blind_cases")
    if (not isinstance(cases,list) or len(cases)!=4
            or any(not isinstance(c,dict) or set(c)!={"response","expected"}
                   or type(c["expected"]) is not int for c in cases)):
        raise HOLD("Blind final fixtures malformed")
    return m


def observe_fixture(case):
    proc = subprocess.run(
        ["node", "observe.mjs"], cwd=ROOT,
        input=json.dumps(case["response"], separators=(",", ":")),
        text=True, capture_output=True, timeout=10, check=False)
    if proc.returncode != 0 or len(proc.stdout)>1000:
        raise HOLD("Local compiled sensor refused fixture")
    try:
        answer = json.loads(proc.stdout)
    except ValueError as exc:
        raise HOLD("Compiled source has invalid output") from exc
    if (not isinstance(answer,dict) or set(answer)!={"status","value"}
            or answer["status"] != "OBSERVED_NUMERIC_FIELD"
            or type(answer["value"]) is not int
            or answer["value"] < 0 or answer["value"] > 10):
        raise HOLD("Compiled sensor returned out-of-scope reading")
    return answer["value"]


def run():
    m = manifest()
    for dir in ("002","003"):
        path = str(ROOT / "experiments" / dir)
        if path not in sys.path:
            sys.path.insert(0,path)
    import motif002 as two
    import affordance as three
    world = two.scene()
    verbs = two.induce(two.lessons())
    rows = three.analyze_first_moves(world, verbs, two.possibilities,
                                    two.utility, horizon=3,max_worlds=500)
    if not rows or any(x["truncated"] for x in rows):
        raise HOLD("Original MOTIF hypothetical frontier unavailable")
    first_actions = {
        policy: three.select_first_move(rows, policy)
        for policy in ("new-choices","immediate")
    }
    if ((first_actions["new-choices"]["operator"],
         first_actions["new-choices"]["roles"]) ==
        (first_actions["immediate"]["operator"],
         first_actions["immediate"]["roles"])):
        raise HOLD("No demonstrable effect on native MOTIF choice")
    observations = []
    for example in m["final_blind_cases"]:
        selected = observe_fixture(example)
        if selected != example["expected"]:
            raise HOLD("Generated sensor disagrees with independent final label")
        priority = "new-choices" if selected >= 2 else "immediate"
        candidate = first_actions[priority]
        # A naive training-first static shortcut follows 'advertised'; wrong
        # on these final data. But an exhaustive holdout-informed selector
        # would find 'observed' and tie GRAFT: no algorithmic superiority.
        advertised = example["response"]["body"]["advertised"]["reachable_actions"]
        static_priority = "new-choices" if advertised >= 2 else "immediate"
        observations.append({
            "generated_sensor_value": selected,
            "declared_threshold": 2,
            "selected_original_003_policy": priority,
            "recommended_original_003_operator": candidate["operator"],
            "recommended_roles": list(candidate["roles"]),
            "naive_train_only_priority": static_priority,
            "naive_priority_differs": priority != static_priority,
            "same_information_classical_can_equal_result": True,
            "simulated_effects_executed": 0,
        })
    result = {
        "schema": "motif.graft-born-sensor-result.v0",
        "status": "EXECUTED_NEW_LOCAL_SENSOR_WITH_ORIGINAL_MOTIF_POLICY",
        "build_manifest_sha256": m["content_sha256"],
        "source_owned_generated_operator": m["operator_kind"],
        "original_motif_003_policy_determined_by_sensor": True,
        "observations": observations,
        "final_blind_correct": len(observations),
        "naive_baseline_correct": 0,
        "fair_classical_selector_would_tie": True,
        "new_general_reasoning_algorithm_proven": False,
        "real_world_observations": 0,
        "network_requests": 0,
        "external_actions": 0,
        "operator_admitted": False,
    }
    result["content_sha256"] = jsdigest(result)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    try:
        run()
    except (HOLD, subprocess.TimeoutExpired) as exc:
        print(json.dumps({"stage":"HOLD","reason":str(exc)}))
        raise SystemExit(1)
