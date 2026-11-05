"""DOOR-FOUNDRY-003: original GRAFT generated a NEW executable MOTIF organ.

The source owning GRAFT-027 breeder writes its actual novel (finite-grammar)
numeric sensor module. CANNON independently reviews that source and blind
fixtures. MOTIF receives held evidence, invokes original GRAFT compiler again,
and constructs an executable local instrumentation build using original MOTIF-
002/003 reasoning code. New source is *not* admitted as canonical or deployed.
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
GRAFT_SHA = "6ff59aead0296081e1547d8107e4b6f06ea2381e"
CANNON_SHA = "0fd326c1bb6f222dc572a4877818d63881828801"
MOTIF_SHA = "5ee9207f04af2826750863526af7f92b31ef8578"
PINS_GRAFT = {
    "src/capability-gardener-027.mjs": "a8d74c3b236f1a53018a458b767ed0ac0120d243",
    "src/discovered-adapter-026.mjs": "3227361a543fbfaa19cc445edfa64757f2b52c71",
    "vendor/alex/api-discovery-026.mjs": "67b851c9ea58d4aa92ca159000e982c312cd2335",
    "vendor/alex/eagle-eye-providers-025.mjs": "5c095be409d2ace0d39765c4316471702d88acb5",
    "test/capability-gardener-027.test.mjs": "799d752179ab4f3f24211cd910c19dc790b4933b",
}
PINS_MOTIF = {
    "experiments/002/motif002.py": "b9f1e7b7879a94f7ef3869bc305608c4d7fa8695",
    "experiments/003/affordance.py": "db25da0d50a9c8e2cd87aa576a22f969405737cf",
}
GRANTED = {
    "network": False,
    "external_execution": False,
    "production_install": False,
    "automatic_canon": False,
    "repo_mutation": False,
    "human_contact": False,
}
SELECTOR = ["observed", "reachable_actions"]
SOURCE_ONLY = "SYNTHETIC_SOURCE_FIXTURE_ONLY"
RECEIPT_SCHEMA = "cannon.graft-generated-operator-review.v0"
BUILD_SCHEMA = "motif.graft-born-local-organ.v0"
RUNNER = HERE / "run_sensor_motif.py"
BRIDGE = HERE / "observe.mjs"


class HOLD(ValueError):
    pass


def jsdigest(o):
    """For the chosen all-integer, ASCII receipt: preserve JS insertion order."""
    return sha256(json.dumps(o, ensure_ascii=False, separators=(",", ":"),
                             allow_nan=False).encode()).hexdigest()


def blob(path):
    data = path.read_bytes()
    return sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def read_doc(path, bound=120000):
    path = Path(path)
    if not path.is_file() or path.stat().st_size > bound:
        raise HOLD("Missing or oversized immutable evidence")
    try:
        result = json.loads(path.read_text())
    except ValueError as exc:
        raise HOLD("Malformed immutable evidence") from exc
    if not isinstance(result, dict):
        raise HOLD("Evidence root is not an object")
    return result


def checked_git_source(root, commit, pins):
    root = Path(root).resolve()
    try:
        observed = subprocess.check_output(["git","-C",str(root),"rev-parse","HEAD"],
                stderr=subprocess.DEVNULL, text=True, timeout=8).strip()
    except (subprocess.SubprocessError, OSError) as exc:
        raise HOLD("Missing pinned original source checkout") from exc
    if observed != commit:
        raise HOLD("Original owner Git commit mismatch")
    for rel, sha in pins.items():
        p = (root / rel).resolve()
        if not p.is_relative_to(root) or not p.is_file() or blob(p) != sha:
            raise HOLD("Unverified original owner file " + rel)
    return root


def check_receipt(packet):
    keys = {
        "schema", "disposition", "selected_graft", "source_packet",
        "training_count", "selection_holdout_count", "negative_count",
        "final_blind_cases", "selected_operator", "original_graft_eval",
        "independent_final_check", "authority", "received_by_motif",
        "is_signed", "observed_real_world_outcome", "content_sha256"
    }
    if set(packet) != keys:
        raise HOLD("Unknown CANNON packet fields")
    body = dict(packet)
    claimed = body.pop("content_sha256")
    if not isinstance(claimed, str) or jsdigest(body) != claimed:
        raise HOLD("CANNON reviewer receipt digest invalid")
    source, unit, test = (packet["selected_graft"], packet["selected_operator"],
                          packet["independent_final_check"])
    if (packet["schema"] != RECEIPT_SCHEMA
            or packet["disposition"] != "HOLD_FOR_MOTIF_LOCAL_SYNTHETIC_REVIEW"
            or packet["received_by_motif"] is not False
            or packet["is_signed"] is not False
            or packet["observed_real_world_outcome"] is not False
            or packet["authority"] != GRANTED):
        raise HOLD("CANNON had no authority to promote generated source")
    if (source.get("repository") != "the-static-collective/GRAFT"
            or source.get("commit") != GRAFT_SHA
            or source.get("branch_is_not_main") is not True
            or source.get("source_does_not_imply_authority") is not True
            or {f.get("path"): f.get("git_blob_sha1")
                for f in source.get("source_files",[]) if isinstance(f,dict)}
            != PINS_GRAFT):
        raise HOLD("Unreviewed GRAFT source was substituted")
    src = packet["source_packet"]
    if (src.get("kind") != "SYNTHETIC_ALEX_DISCOVERY_SHAPE_FIXTURE_NOT_REAL_SOURCE"
            or src.get("live_provider_discovered") is not False
            or src.get("live_provider_contacted") is not False):
        raise HOLD("Fake claim that a real source was independently observed")
    if (unit.get("schema") != "motif.graft-numeric-sensor.v0"
            or unit.get("origin") != "ORIGINAL_GRAFT_027_COMPILED_SOURCE"
            or unit.get("selector") != SELECTOR
            or unit.get("source_installed_in_motif") is not False
            or unit.get("network_authority") != "NONE"
            or not isinstance(unit.get("source"),str)
            or not isinstance(unit.get("source_sha256"),str)
            or len(unit["source"]) > 5000
            or sha256(unit["source"].encode()).hexdigest() != unit["source_sha256"]):
        raise HOLD("Generated code is not a known bounded source-owned candidate")
    owner = packet["original_graft_eval"]
    if (owner.get("status") != "HELD_BEST_FIXTURE_CANDIDATE"
            or owner.get("winner",{}).get("selector") != SELECTOR
            or owner.get("winner",{}).get("source_sha256") != unit["source_sha256"]
            or owner.get("variants_tested",0) < 3
            or not owner.get("rejected")):
        raise HOLD("Original GRAFT variant selection not substantiated")
    if (packet["training_count"] != 3 or packet["selection_holdout_count"] != 3
            or packet["negative_count"] != 3
            or test.get("n") != 4 or test.get("generated_correct") != 4
            or test.get("naive_train_only_baseline_correct") != 0
            or test.get("matched_holdout_informed_exhaustive_baseline_correct") != 4
            or test.get("superior_to_matched_classical_baseline") is not False
            or test.get("selection_holdout_used_by_graft") is not True
            or test.get("blind_final_not_used_to_pick_operator") is not True):
        raise HOLD("Native GRAFT blind test or honest classical comparator missing")
    final = packet["final_blind_cases"]
    if (not isinstance(final, list) or len(final) != 4
            or any(not isinstance(f,dict) or set(f) != {"response","expected"}
                   or type(f["expected"]) is not int or
                   type(f.get("response",{}).get("body",{}).get("observed",{}).get("reachable_actions")) is not int
                   for f in final)):
        raise HOLD("Blind synthetic examples malformed")
    return claimed


def regenerate_from_original_graft(graft_root):
    """Actual GRAFT source compiler; MOTIF does not mint lookalike source."""
    js = ("import {pathToFileURL} from 'node:url'; "
          "import {resolve} from 'node:path'; "
          "const x=await import(pathToFileURL(resolve(process.argv[1],"
          "'src/capability-gardener-027.mjs')).href); "
          "process.stdout.write(JSON.stringify(x.compileVariant("
          "['observed','reachable_actions'])));")
    try:
        raw = subprocess.check_output(
            ["node","--input-type=module","-e",js,str(graft_root)],
            text=True,stderr=subprocess.DEVNULL,timeout=15)
        generated = json.loads(raw)
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        raise HOLD("Original GRAFT compiler refused regeneration") from exc
    if (generated.get("selector") != SELECTOR or
            generated.get("generated_from") !=
                "DECLARED_JSON_FIELD_GRAMMAR_WITH_CLOSED_EXECUTOR" or
            generated.get("network_authority") != "NONE" or
            generated.get("code_installed") is not False):
        raise HOLD("Original GRAFT compiler returned unexpected executable")
    return generated


def build(packet_file, graft_source, motif_source, destination):
    packet = read_doc(packet_file)
    receipt_hash = check_receipt(packet)
    graft_root = checked_git_source(graft_source, GRAFT_SHA, PINS_GRAFT)
    motif_root = checked_git_source(motif_source, MOTIF_SHA, PINS_MOTIF)
    generated = regenerate_from_original_graft(graft_root)
    unit = packet["selected_operator"]
    if (generated["source"] != unit["source"] or
            generated["source_sha256"] != unit["source_sha256"]):
        raise HOLD("CANNON candidate differs from source-native GRAFT recompilation")
    destination = Path(destination).resolve()
    if destination.exists():
        raise HOLD("Refuse to overwrite existing build")
    destination.mkdir(parents=True)
    for rel, sha in PINS_MOTIF.items():
        p = destination / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(motif_root / rel, p)
        if blob(p) != sha:
            raise HOLD("Copied owner code changed unexpectedly")
    (destination / "generated_sensor.mjs").write_text(generated["source"])
    shutil.copyfile(RUNNER,destination / "run.py")
    shutil.copyfile(BRIDGE,destination / "observe.mjs")
    manifest = {
        "schema": BUILD_SCHEMA,
        "operator_kind": "GRAFT_GENERATED_NEW_EXECUTABLE_NUMERIC_PROJECTION",
        "graft_source_commit": GRAFT_SHA,
        "cannon_source_commit": CANNON_SHA,
        "motif_original_commit": MOTIF_SHA,
        "graft_source_pins": PINS_GRAFT,
        "motif_source_pins": PINS_MOTIF,
        "cannon_review_sha256": receipt_hash,
        "generated_source_sha256": generated["source_sha256"],
        "runner_sha256": sha256(RUNNER.read_bytes()).hexdigest(),
        "bridge_sha256": sha256(BRIDGE.read_bytes()).hexdigest(),
        "selector": SELECTOR,
        "authority": GRANTED,
        "scope": SOURCE_ONLY,
        "status": "HELD_LOCAL_EXECUTABLE_NOT_ADMITTED",
        "final_blind_cases": packet["final_blind_cases"],
        "baseline":{
            "naive_train_only_correct": 0,
            "fair_classical_with_same_holdout_correct":4,
            "fair_classical_superiority_proven": False,
        },
    }
    manifest["content_sha256"] = jsdigest(manifest)
    (destination / "manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    report = {
        "schema": "motif.graft-born-build-report.v0",
        "status": "NEW_GRAFT_GENERATED_MOTIF_SENSOR_BUILD_CREATED_HELD",
        "build": destination.name,
        "source_owner": "the-static-collective/GRAFT",
        "original_graft_commit": GRAFT_SHA,
        "original_cannon_reviewer": CANNON_SHA,
        "source_sha256": unit["source_sha256"],
        "package_manifest_sha256": manifest["content_sha256"],
        "new_executable_generated_by_original_graft": True,
        "reasoning_policy_tuned_by_new_sensor": True,
        "invented_general_algorithm": False,
        "matched_classical_baseline_beaten": False,
        "field_outcomes": 0,
        "repo_writes": 0,
        "external_requests": 0,
        "admission": False,
    }
    report["content_sha256"] = jsdigest(report)
    print(json.dumps(report,indent=2))
    return report


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--cannon-receipt",type=Path,required=True)
    p.add_argument("--graft-source",type=Path,required=True)
    p.add_argument("--motif-original",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    try:
        build(args.cannon_receipt,args.graft_source,args.motif_original,
              args.output)
    except HOLD as exc:
        print(json.dumps({"stage":"HOLD","reason":str(exc)}))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
