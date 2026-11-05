"""MOTIF-010: inspectable two-step scientific inquiry receipt.

The evaluator alone imports its own synthetic oracle. The scientist sees only
the public control schema and past observed before/after graphs, and uses real
MOTIF-009 decision-tree cartridges for competing explanations.

Run: python demo.py
"""
from __future__ import annotations
import json
from oracle import world, natural_observations, intervene
from scientist import (candidate_cartridges, propose_intervention,
                       validated_result, explanation_report, consensus)
from cartridge import export_cartridge


def demonstrate():
    # XOR is chosen by the *evaluator*, not a hidden mechanism argument
    # supplied to the scientist or to its question-selection function.
    spec = world("exclusive", 11)
    observations = list(natural_observations(spec))
    originals = tuple(x.before for x in observations)
    first_state = candidate_cartridges(observations, spec.controls)
    transcript = []
    used = set()
    for idx in range(2):
        candidates = candidate_cartridges(observations, spec.controls)
        proposal = propose_intervention(candidates, used)
        if proposal is None:
            raise AssertionError("Two diagnostics were required")
        setting = (proposal.first, proposal.second)
        used.add(setting)
        response = intervene(spec, *setting, 77_000 + idx)
        observations.append(response)
        after = candidate_cartridges(observations, spec.controls)
        transcript.append({
            "step": idx+1,
            "tree_cartridge_ids_before": list(proposal.competing_tree_ids),
            "experiment": proposal.action,
            "control_values": list(setting),
            "expected_information_gain_bits": proposal.information_gain_bits,
            "predicted_votes_before_observation": list(proposal.predicted_votes),
            "resulting_observed_change": validated_result(response),
            "remaining_tree_cartridges": len(after),
            "actual_real_world_action": False,
        })
    final = candidate_cartridges(observations, spec.controls)
    if len(final) != 1:
        raise AssertionError("Simulator outcome not identifiable within grammar")
    serialized = json.loads(export_cartridge(final[0]))
    return {
        "experiment": "MOTIF-010",
        "receipt": "SYNTHETIC_INTERVENTION_TRANSCRIPT",
        "initial_tree_hypotheses": len(first_state),
        "interventions": transcript,
        "final_tree": serialized,
        "full_two_input_truth_table": [
            {"controls": list(pair), "prediction": consensus(final,*pair)}
            for pair in ((False,False),(False,True),(True,False),(True,True))
        ],
        "original_natural_observations_unmodified":
            originals == tuple(x.before for x in observations[:2]),
        "real_world_authority": False,
    }


if __name__ == "__main__":
    print(json.dumps(demonstrate(), indent=2, sort_keys=True))
