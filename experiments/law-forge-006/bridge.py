"""ALEX/Dogram/GRAFT boundaries for LAW-FORGE-006.

- Emit exact-schema specimens for the *original, commit-pinned* Dogram CLI.
- Create layered ALEX-intake and GRAFT-review *proposals* in local JSON.
- Verify Dogram's native returned ablation receipts, no surrogate result.

Neither ALEX nor GRAFT is called by this script: the handoffs are explicitly
NOT STORED / NOT ADMITTED. The only native cross-project test is Dogram's
read-only mathematical calculation in a pinned CI checkout.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from inventor import Proposal, evidence_digest
from owner import LINKS, World, owner_contract
from trial import inspect_source

DOGRAM_COMMIT = "551b5f9df18f17ec69b452ddcdff01718e0ff771"
DOGRAM_REPO = "the-static-collective/Dogram"


def write(path, obj):
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8")


def source_packet():
    model, requests, evidence, status = inspect_source(World("any_three_paths", 1))
    if not isinstance(model, Proposal):
        raise AssertionError("Source did not construct proposed graph instrument")
    owner = World("any_three_paths", 1)
    owner_review = owner.conformance(model.packet(), "review")
    if owner_review["status"] != "PROPOSE_ONLY_REVIEW_PASSED":
        raise AssertionError("Owner refused source-local candidate")
    source = owner_contract()
    source_digest = evidence_digest(evidence)
    alex = {
        "schema": "motif.law-forge.alex-intake-proposal.v1",
        "target_project": "the-static-collective/ALEX.2",
        "status": "PROPOSE_TO_ALEX_NOT_STORED",
        "source_contract": source,
        "witness_layer": {
            "kind": "SIMULATED_SOURCE_OBSERVATIONS",
            "count": len(evidence),
            "source_digest": source_digest,
            "rows": [{"inputs": list(row.inputs), "result": row.result,
                      "token": row.token, "provenance": row.provenance}
                     for row in evidence]
        },
        "hypothesis_layer": {
            "kind": "INFERRED_SENSOR_NOT_HISTORICAL_FACT",
            "model": model.packet(),
            "alternatives_tested": "BOUNDED_MONOTONE_DNF_MAX3_TERMS_WIDTH2"
        },
        "review_layer": {
            "kind": "SIMULATOR_OWNER_CONFORMANCE_ONLY",
            "local_review": owner_review,
            "external_peer_review": "NOT_PERFORMED"
        },
        "data_immutability": "PROPOSE_ONLY_NO_STORAGE",
        "real_world_authority": False
    }
    graft = {
        "schema": "motif.law-forge.graft-intake-proposal.v1",
        "target_project": "the-static-collective/GRAFT",
        "status": "PROPOSE_TO_GRAFT_NOT_IMPORTED",
        "source_repo": "the-static-collective/MOTIF",
        "source_contract": source,
        "proposed_sensor": model.packet(),
        "source_owner_compiler_review": owner_review,
        "sandbox_execution": "SYNTHETIC_READ_ONLY_LOCAL_CONFORMANCE",
        "graft_native_compile": "NOT_ATTEMPTED",
        "human_review": "PENDING",
        "automatic_admission": False,
        "real_world_authority": False
    }
    return alex, graft, model


def dogram_specimens(model):
    """For each path, ablate the only active route; compare three methods.

    Dogram owns the ablation semantics. This function only declares three
    source-typed graph specimens; it does NOT implement ablation.
    """
    specimens = []
    for relay in range(3):
        state = [0] * 6
        state[relay * 2:relay * 2 + 2] = [1, 1]
        expected = model.sensor.predict(state)
        if expected != 1:
            raise AssertionError("Proposed sensor cannot recognize path")
        nodes = sorted(set(node for edge in LINKS for node in edge))
        graph_edges = [list(LINKS[index]) for index, active
                       in enumerate(state) if active]
        specimen = {
            "schema": "dogram.specimen/v0",
            "specimen_id": f"law-forge-006-native-ablate-path-{relay}",
            "operator": "ablate",
            "operator_version": 1,
            "inputs": {
                "graph": {"nodes": nodes, "edges": graph_edges},
                "target": {"kind": "edge",
                           "source": LINKS[2 * relay][0],
                           "target": LINKS[2 * relay][1]},
                "requested_targets": [["S", "T"]]
            },
            "assumptions": [],
            "metadata": {
                "synthetic_only": True,
                "model_id": model.id,
                "source_project": "MOTIF LAW-FORGE-006",
                "dogram_source_revision": DOGRAM_COMMIT,
                "no_causal_or_real_world_truth_claim": True
            }
        }
        specimens.append(specimen)
    return specimens


def emit(directory):
    directory.mkdir(parents=True, exist_ok=True)
    alex, graft, model = source_packet()
    write(directory / "alex-proposal.json", alex)
    write(directory / "graft-proposal.json", graft)
    specimens = dogram_specimens(model)
    for i, spec in enumerate(specimens):
        write(directory / f"dogram-{i}.json", spec)
    write(directory / "manifest.json", {
        "schema": "motif.law-forge.bridge-manifest.v1",
        "source_owner": "LOCAL_SYNTHETIC_SIX_LINK_GRAPH",
        "model_id": model.id,
        "dogram_repo": DOGRAM_REPO,
        "dogram_commit": DOGRAM_COMMIT,
        "dogram_cli_source": "dogram/cli.py",
        "native_dogram_receipts": "PENDING_NATIVE_EXECUTION",
        "alex_status": "PROPOSE_TO_ALEX_NOT_STORED",
        "graft_status": "PROPOSE_TO_GRAFT_NOT_IMPORTED",
        "no_automatic_admission": True
    })


def verify(directory):
    manifest = json.loads((directory / "manifest.json").read_text())
    if manifest["dogram_commit"] != DOGRAM_COMMIT:
        raise ValueError("Unexpected native source commit")
    results = []
    for i in range(3):
        specimen = json.loads((directory / f"dogram-{i}.json").read_text())
        receipt = json.loads((directory / f"dogram-{i}.receipt.json").read_text())
        if (receipt.get("schema") != "dogram.receipt/v0"
                or receipt.get("specimen_id") != specimen["specimen_id"]
                or receipt.get("status") != "OK"
                or receipt.get("operator") != "ablate"
                or receipt.get("operator_version") != 1):
            raise AssertionError("Native Dogram refused or altered specimen")
        data = receipt.get("result")
        if not isinstance(data, dict):
            raise AssertionError("Missing independent Dogram result")
        paths = data.get("requested_targets")
        if (not isinstance(paths, list) or len(paths) != 1
                or paths[0] != {
                    "source": "S", "target": "T",
                    "reachable_before": True, "reachable_after": False
                }):
            raise AssertionError("Native Dogram independent ablation mismatch")
        results.append({
            "specimen": specimen["specimen_id"],
            "native_dogram_status": receipt["status"],
            "independent_path_loss": paths[0],
            "input_digest": receipt.get("input_digest")
        })
    report = {
        "schema": "motif.law-forge.native-dogram-verification.v1",
        "dogram_source_repo": DOGRAM_REPO,
        "dogram_source_commit": DOGRAM_COMMIT,
        "cases": results,
        "verified": len(results) == 3,
        "alex_stored": False,
        "graft_imported": False,
        "graft_admitted": False,
        "real_world_authority": False
    }
    write(directory / "verified-dogram.json", report)
    return report


if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[1] not in ("emit", "verify"):
        raise SystemExit("Usage: python bridge.py emit|verify <output-directory>")
    location = Path(sys.argv[2])
    if sys.argv[1] == "emit":
        emit(location)
    else:
        print(json.dumps(verify(location), indent=2, sort_keys=True))
