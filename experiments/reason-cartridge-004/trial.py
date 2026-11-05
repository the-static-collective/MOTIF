"""Independent synthetic observation-budget trial for REASON-004.

The hidden world is a fixture, NOT accessed by the inquiry engine.
An unoptimized declared-order questioner is a weak baseline;
a full-information classical oracle is a separate upper bound.
"""
import json

from reason004 import Inquiry, evidence, make, validate, observe, Receiver


def specimen():
    return Inquiry(
        ("S","A","B","T"),
        (("S","B"),("S","A"),("A","T"),("B","T"),("S","T")),
        (("S","A","PRESENT","known1"),("B","T","ABSENT","known2")),
        ("S","T"), True)


def review_cases():
    return (
        (Inquiry(("S","T"),(("S","T"),("T","S")),
                 (("T","S","PRESENT","r1"),),("S","T"),True,
                 "T","S"),"PROVED_REACHABLE"),
        (Inquiry(("S","A","T"),(("S","A"),("A","T"),("S","T")),
                 (("S","A","PRESENT","r2"),("A","T","ABSENT","r3")),
                 ("S","T"),True),"PROVED_UNREACHABLE"),
        (Inquiry(("S","A","T"),(("S","A"),("A","T"),("S","T")),
                 (("S","A","PRESENT","r4"),),("S","T"),True),"UNKNOWN"),
        (Inquiry(("S","A","T"),(("S","A"),("A","T"),("S","T")),
                 (("S","A","PRESENT","r5"),),("S","T"),False),"HOLD_OPEN_WORLD"),
    )


def simulate(mode, hidden):
    case = specimen()
    history = []
    for index in range(3):
        packet = validate(make(case, false_negative_cost=8,
                               false_positive_cost=3, question_cost=.1))
        if packet["conclusion"] != "UNKNOWN":
            return {"status": packet["conclusion"],
                    "observations": len(history),
                    "questions": history, "external_queries": 0}
        available = evidence(case)[3]
        if mode == "consequence":
            falsifier = packet["refutation_program"]
            if falsifier["kind"] != "OBSERVE_DISCRIMINATING_EDGE":
                break
            edge = tuple(falsifier["edge"])
        else:
            # Weak baseline: inspect unknown edges in the operator's
            # original declared universe order without consequence ranking.
            edge = next(e for e in case.universe if e in available)
        if edge not in hidden:
            raise AssertionError("Unowned synthetic oracle case")
        answer = "PRESENT" if hidden[edge] else "ABSENT"
        outcome = observe(case, edge, answer, f"local-fixture-{mode}-{index}")
        history.append({"edge": list(edge), "synthetic_truth": answer})
        case = outcome["updated_inquiry"]
    return {"status": "HOLD_UNRESOLVED", "observations": len(history),
            "questions": history, "external_queries": 0}


def run():
    raw = make(specimen(), false_negative_cost=8,
               false_positive_cost=3, question_cost=.1)
    receiver = Receiver(raw)
    assessment = receiver.preview(review_cases())
    if assessment["errors"] == 0:
        receiver.admit("ADMIT_READ_ONLY", assessment["review_digest"])
    tests = []
    for a in (False,True):
        for b in (False,True):
            truths={("S","B"):a, ("A","T"):b}
            fast=simulate("consequence", truths)
            fixed=simulate("declared_order", truths)
            expected="PROVED_REACHABLE" if b else "PROVED_UNREACHABLE"
            assert fast["status"] == expected and fixed["status"] == expected
            tests.append({"oracle_synthetic_edges": {"S-B":a, "A-T":b},
                          "result": expected,
                          "consequence_observations": fast["observations"],
                          "fixed_order_observations": fixed["observations"]})
    return {
        "schema": "motif.reason.self-objection-receipt.v1",
        "source_owner": "MOTIF-003 objection.py pinned unmodified",
        "review": {"cases":assessment["cases"],"errors":assessment["errors"]},
        "synthetic_local_read_only_admission": receiver.admitted,
        "claim": receiver.suggest(),
        "worlds": tests,
        "mean_consequence_questions": sum(x["consequence_observations"] for x in tests)/len(tests),
        "mean_fixed_order_questions": sum(x["fixed_order_observations"] for x in tests)/len(tests),
        "full_information_classical_upper_bound_correct": len(tests),
        "no_classical_optimality_claim": True,
        "external_questions_sent": 0,
        "real_world_authority": False,
    }


if __name__=="__main__":
    print(json.dumps(run(),indent=2))
