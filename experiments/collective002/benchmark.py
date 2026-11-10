"""Matched-information classical controls; no claim of superlinear emergence."""
import json
from demo import execute
from protocol import infer_path


def classical_equal_information(packet):
    """An ordinary centrally pooled breadth-first search sees identical cards."""
    return infer_path(packet["source_nodes"], "A", "D", packet["local_scope"])


def run():
    normal = execute()
    missing = execute(with_c=False)
    withheld = execute(withhold_b=True)
    contradiction = execute(conflict=True)
    packet = normal["result"]
    local_only = packet["local_isolated_status"]
    center = classical_equal_information(packet)
    outcomes = {
        "case_full_disclosure": packet["outcome"]["status"],
        "case_missing_node": missing["result"]["outcome"]["status"],
        "case_private_grant_withheld": withheld["result"]["outcome"]["status"],
        "case_explicit_contradiction": contradiction["result"]["outcome"]["status"],
        "isolated_A_same_private_evidence": local_only,
        "classical_central_BFS_same_transmitted_evidence": center["status"],
        "network_superiority_over_equal_information_central": False,
        "all_three_sources_present": packet["source_count"] == 3,
        "transport": "three separate loopback-only server OS processes",
        "epistemic_limit": "only conditional reachability from synthetic reported edges",
    }
    assert outcomes["case_full_disclosure"] == "PATH_SUPPORTED_BY_ASSERTIONS"
    assert outcomes["classical_central_BFS_same_transmitted_evidence"] == "PATH_SUPPORTED_BY_ASSERTIONS"
    assert outcomes["isolated_A_same_private_evidence"] == "UNKNOWN_INSUFFICIENT_EVIDENCE"
    assert outcomes["case_missing_node"] == "UNKNOWN_INSUFFICIENT_EVIDENCE"
    assert outcomes["case_private_grant_withheld"] == "UNKNOWN_INSUFFICIENT_EVIDENCE"
    assert outcomes["case_explicit_contradiction"] == "HOLD_CONTRADICTION"
    return outcomes

if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
