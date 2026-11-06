"""Independent classical least-fixed-point reference, no engine import.

Returns four-valued statuses for explicitly stipulated fictional case facts.
Uses direct set membership, not the main engine's proof graph or certificates.
"""
from __future__ import annotations

from casebook import cases


def encoded(literal):
    return "|".join((literal["forum"],literal["epoch"],literal["subject"],
                     literal["predicate"],literal["sign"]))


def independent(case):
    truths=set()
    for fact in case["claims"]:
        if fact["source_status"]=="STIPULATED_HYPOTHESIS":
            truths.add(encoded(fact["literal"]))
    for _ in range(40):
        before=set(truths)
        for norm in case["rules"]:
            if all(encoded(p) in truths for p in norm["premises"]):
                truths.add(encoded(norm["conclusion"]))
        if truths==before:
            break
    else:
        raise ValueError("Unbounded independent rule closure")
    outputs={}
    for q in case["queries"]:
        d=q["literal"]
        pos=d["forum"]+"|"+d["epoch"]+"|"+d["subject"]+"|"+d["predicate"]+"|YES"
        neg=d["forum"]+"|"+d["epoch"]+"|"+d["subject"]+"|"+d["predicate"]+"|NO"
        p=pos in truths
        n=neg in truths
        outputs[q["id"]]=("BOTH" if p and n else "SUPPORTED" if p else
                          "REFUTED" if n else "UNDETERMINED")
    return outputs


if __name__=="__main__":
    import json
    print(json.dumps({case["id"]:independent(case) for case in cases()},indent=2))
