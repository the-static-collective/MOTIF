"""Executable market: local source-owned lessons -> circuit -> certified offers.

Reproducible source-owned fixtures, not external evidence or general AI.
"""
from __future__ import annotations
import json
from pathlib import Path

from source import Case, TRAIN, CERT, training, deployment, bfs_truth, SOURCE_REVISION
from compiler import propose, validate, classify, pin_source, PROGRAMS
from receiver import Receiver
from market import Bid, DiscoveryMarket, packet, validate_packet, COST
from bridge006 import transfer


def certified():
    artifact=propose(training())
    receiver=Receiver(artifact)
    review=receiver.preview(tuple(Case(n) for n in CERT))
    if review["errors"]==0:
        receiver.admit("ADMIT_READ_ONLY",review["review_digest"])
    return artifact,receiver,review


def offers():
    return (
        Bid("first-compose","MOTIF_COMPILER","COMPILE_SENSOR",advertised_gain=10**9),
        Bid("slow-lookup","CLASSICAL_OWNER","DIRECT_CLASSICAL_QUERY",advertised_gain=42),
        Bid("copy-compose","SECOND_OBSERVER","COMPILE_SENSOR",advertised_gain=10**12),
        Bid("abstention","LOOP_SENTINEL","ABSTAIN",advertised_gain=1),
    )


def run(path=None):
    artifact,receiver,certification=certified()
    wide=deployment(16)
    raw=packet(artifact,receiver,offers(),wide)
    reviewed=validate_packet(raw,receiver)
    inherited_ledger=transfer(raw,receiver)
    market=reviewed["receipt"]
    tiny=DiscoveryMarket(artifact,receiver,offers(),deployment(1)).evaluate()
    larger=DiscoveryMarket(artifact,receiver,offers(),deployment(32)).evaluate()
    actual=[bfs_truth(c) for c in wide]
    predicted=[receiver.suggest(c)["prediction"] for c in wide]
    if predicted != actual:
        raise AssertionError("Source-owned deployment counterexample")
    if (market["winning_kind"]!="COMPILE_SENSOR"
            or tiny["winning_kind"]!="DIRECT_CLASSICAL_QUERY"):
        raise AssertionError("Market failed the payoff reversal")
    result={
        "schema":"motif.reason.discovery-market-experiment.v1",
        "source_contract":SOURCE_REVISION,"source_git_blob":pin_source(),
        "developer_supplied_circuit_candidates":len(PROGRAMS),
        "training_source_observations":len(TRAIN),
        "heldout_certification_cases":certification["cases"],
        "heldout_errors":certification["errors"],
        "proposed_sensor":validate(artifact)["program"],
        "read_only_local_admitted":receiver.admitted,
        "one_task_winner":tiny["winning_kind"],
        "sixteen_task_winner":market["winning_kind"],
        "thirty_two_task_winner":larger["winning_kind"],
        "portfolio_tasks_verified":market["task_count"],
        "portfolio_errors":market["incorrect_or_abstained"],
        "strong_classical_bfs_correct":market["strong_classical_bfs_full_information_correct"],
        "source_owner_direct_lookup_cost":market["direct_query_hypothetical_cost"],
        "composed_sensor_cost":market["winner_hypothetical_cost"],
        "hypothetical_marginal_savings":market["marginal_verified_savings_points"],
        "duplicate_bids_rewarded":sum(e["earned_nontransferable_utility_points"]
                                     for e in market["offers"] if not e["new_validated_offer"]),
        "duplicate_bids_suppressed":market["duplicate_offers"],
        "market_winner_receipt_digest":reviewed["checksum_sha256"],
        "reused_prior_commonwealth_ledger":inherited_ledger,
        "validation_receipt_digest":certification["review_digest"],
        "full_information_classical_solver_would_match_accuracy":True,
        "classical_optimizing_planner_can_make_same_choice":True,
        "new_primitive_invented":False,
        "real_world_observation":False,"real_world_authority":False,
        "external_actions":False,
    }
    if path:
        root=Path(path)
        root.mkdir(parents=True,exist_ok=True)
        (root/"compiled-sensor.json").write_text(artifact,encoding="utf-8")
        (root/"market-receipt.json").write_text(raw,encoding="utf-8")
        (root/"benchmark.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",
                                            encoding="utf-8")
    return result


if __name__=="__main__":
    import sys
    if len(sys.argv)>2:
        raise SystemExit("usage: python trial.py [local-receipt-folder]")
    print(json.dumps(run(sys.argv[1] if len(sys.argv)==2 else None),
                     indent=2,sort_keys=True))
