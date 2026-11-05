"""Materialize a complete synthetic decision-tree cartridge and demonstrate HOLD.

Run from experiments/009:
    python cartridge_demo.py

The JSON output contains a *synthetic* tree cartridge, read-only local
review receipt, and an unlabeled proposed question, not any real-world power.
"""
from __future__ import annotations
from pathlib import Path
import sys
import json
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "008"))

from oracle import spec_for, split
from cartridge import fit_cartridge, export_cartridge, CartridgeBay
from experimenter import public_question, propose_question, train_committee


def demonstration():
    spec = spec_for("xor", 11)
    observed = split(spec, "train", 80)
    checking = split(spec, "validation", 32)
    car = fit_cartridge(observed)
    payload = json.loads(export_cartridge(car))
    bay = CartridgeBay()
    ticket = bay.offer(json.dumps(payload))
    held = ticket not in bay.admitted
    reviewed = bay.review(ticket, "ADMIT_PREDICT_ONLY",
                          "LOCAL_SYNTHETIC_REVIEWER", checking)
    question_sources = split(spec, "test", 16)
    unlabeled = [public_question(i, x.before, x.roles)
                 for i,x in enumerate(question_sources)]
    query = propose_question(unlabeled, observed,
                             train_committee(observed, seed=11))
    return {
        "artifact": payload,
        "scope": "SYNTHETIC_PREDICTION_ONLY",
        "held_before_review": held,
        "review": reviewed,
        "next_unlabeled_query": {
            "ticket": query.ticket,
            "tree_cartridge": ticket,
            "reason": query.basis,
            "question_does_not_contain_answer": not query.answer_known
        }
    }


if __name__ == "__main__":
    print(json.dumps(demonstration(), indent=2, sort_keys=True))
