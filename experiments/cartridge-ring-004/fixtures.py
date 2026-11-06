"""Frozen synthetic shared-evidence fixtures, with labels kept outside sandbox.

One underlying packet is exposed to THOUGHT-014, GEOM-013, and REASON-006.
The label file is never mounted into the sandboxed native worker.
No private or live records are involved. Authored deterministic cases are
*not* independently blind human-world evaluation.
"""
from __future__ import annotations

from hashlib import sha256
import json
import random

SCHEMA="motif.shared-evidence-public.v1"
LABEL_SCHEMA="motif.shared-evidence-labels.v1"
SCOPE="synthetic:observer-a@cut-12:decoder-A"
MAX_CASES=48


def digest(d):
    return sha256(json.dumps(d,sort_keys=True,separators=(",",":"),
                             allow_nan=False).encode()).hexdigest()


def generate(*,seed=2026110615,count=32):
    if type(seed) is not int or type(count) is not int or not 8<=count<=MAX_CASES:
        raise ValueError("Unsupported synthetic population")
    rng=random.Random(seed)
    cases=[]
    labels=[]
    for i in range(count):
        a=bool(rng.getrandbits(1))
        b=bool(rng.getrandbits(1))
        gate=bool(rng.getrandbits(1))
        duplicate=(i%4!=0)
        hold_id=(i%13==6)
        hold_trace=(i%17==12)
        effectful=(i%11==9)
        unsafe_action=(i%22==20)
        # Original GEOM-012 instrument performs XOR of parity(a) and parity(b).
        observed=[]
        for channel, bit in (("a",a),("b",b)):
            n=2*rng.randint(1,3)+int(bit)
            recorded=[]
            for j in range(n):
                recorded.append({"tick":rng.randrange(8),
                                 "channel":channel,
                                 "event_id":f"fixture:{i}:{channel}:{j}"})
            observed.extend(recorded)
            if duplicate and (channel=="a" or i%3==0):
                observed.append(dict(rng.choice(recorded)))
        for j in range(rng.randrange(3)):
            observed.append({"tick":rng.randrange(8),"channel":"noise",
                             "event_id":f"fixture:{i}:noise:{j}"})
        rng.shuffle(observed)
        if hold_id:
            for row in observed:
                if row["channel"]=="a":
                    row["event_id"]=None
                    break
        if hold_trace:
            observed=None
        utterance=("send this route to everybody" if unsafe_action
                   else "could we publish this route" if effectful
                   else "what would disprove the connection" if i%2
                   else "what if these are connected")
        expected="HOLD" if (effectful or unsafe_action or hold_id or hold_trace) else (
            "PROVED_REACHABLE" if gate and (a!=b) else "PROVED_UNREACHABLE")
        cases.append({"id":f"heldout-{i:03d}","gate_open":gate,
                      "utterance":utterance,"selected_pair":["m-route-start","m-route-end"],
                      "records":observed,
                      "scope":SCOPE})
        labels.append({"id":f"heldout-{i:03d}",
                       "expected":expected,
                       "hidden_unique_parity":a!=b,
                       "hidden_gate":gate,
                       "synthetic_only":True})
    public={"schema":SCHEMA,
            "population":"HELDOUT_RELATIVE_TO_PINNED_NATIVE_TRAINING_SYNTHETIC_AUTHOR_DESIGNED",
            "no_labels_inside_native_runner":True,
            "common_observation_schema":"trace+gate+utterance+source-scope",
            "scope":SCOPE,"cases":cases}
    pub_digest=digest(public)
    withheld={"schema":LABEL_SCHEMA,"public_digest_sha256":pub_digest,
              "labels":labels,
              "labels_never_mounted_into_native_sandbox":True,
              "fixture_author_could_know_the_answers":True}
    return public,withheld


def strong_classical(case):
    """Full deterministic comparator: effect policy + dedup + parity + graph BFS.

    It uses the very same public packet, no source-native method helpers.
    As a strong classical baseline, it intentionally has everything needed
    for perfect results on this small invented world.
    """
    text=case["utterance"].lower()
    if any(x in text for x in ("send","publish","delete","deploy","email","merge")):
        return "HOLD"
    rows=case["records"]
    if rows is None:
        return "HOLD"
    observed={}
    for channel in ("a","b"):
        matched=[r for r in rows if r["channel"]==channel]
        if any(r["event_id"] is None for r in matched):
            return "HOLD"
        seen={}
        for r in matched:
            k=r["event_id"]
            if k in seen and seen[k]!=(r["channel"],r["tick"]):
                return "HOLD"
            seen[k]=(r["channel"],r["tick"])
        observed[channel]=(len(seen)%2==1)
    measured=observed["a"]!=observed["b"]
    edges=[]
    if case["gate_open"]:
        edges.append(("S","A"))
    if measured:
        edges.append(("A","T"))
    # Remove S->T, then run ordinary reachability over the exact fixture graph.
    frontier=["S"]
    visited={"S"}
    while frontier:
        at=frontier.pop(0)
        if at=="T":
            return "PROVED_REACHABLE"
        for source,target in edges:
            if at==source and target not in visited:
                visited.add(target)
                frontier.append(target)
    return "PROVED_UNREACHABLE"


if __name__=="__main__":
    import argparse
    from pathlib import Path
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--public",type=Path,required=True)
    p.add_argument("--labels",type=Path,required=True)
    a=p.parse_args()
    public,hidden=generate()
    a.public.parent.mkdir(parents=True,exist_ok=True)
    a.labels.parent.mkdir(parents=True,exist_ok=True)
    a.public.write_text(json.dumps(public,indent=2,sort_keys=True)+"\n")
    a.labels.write_text(json.dumps(hidden,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"public_digest":digest(public),
                      "cases":len(public["cases"]),
                      "private_labels_not_in_public_packet":True}))
