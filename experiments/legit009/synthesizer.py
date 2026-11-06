"""LEGIT-009: CEGIS invention of bounded, executable NAND reasoning cartridges.

Learner has a typed instruction language (two input wires and two-input NAND).
The learner is NOT handed candidate circuits, XOR, parity, or expected
functions. A separate verifier supplies one counterexample at a time.
Code generation is DATA, not Python eval or unrestricted source synthesis.
"""
from __future__ import annotations

import hashlib
import itertools
import json

MASK = 0b1111
INPUT_A = 0b1100  # rows (0,0), (0,1), (1,0), (1,1)
INPUT_B = 0b1010
MAX_GATES = 5
MAX_ROUNDS = 6
SCHEMA = "motif.nand-reason-cartridge.v1"


class HOLD(ValueError):
    pass


def checksum(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":"),
                                     allow_nan=False).encode()).hexdigest()


def _assert_program(gates):
    if not isinstance(gates, (list,tuple)) or len(gates)>MAX_GATES:
        raise HOLD("Unknown or oversized circuit")
    for i, pair in enumerate(gates):
        if (not isinstance(pair,(list,tuple)) or len(pair)!=2 or
                any(type(pin) is not int or not 0<=pin<i+2 for pin in pair)):
            raise HOLD("Bad noncausal circuit wiring")
        if pair[0]>pair[1]:
            raise HOLD("Unnormalized NAND gate inputs")
    return True


def mask(gates,output=None):
    _assert_program(gates)
    wires=[INPUT_A,INPUT_B]
    for a,b in gates:
        wires.append((~(wires[a]&wires[b]))&MASK)
    end=len(wires)-1 if output is None else output
    if type(end) is not int or not 0<=end<len(wires):
        raise HOLD("Unknown output pin")
    return wires[end]


def eval_pair(gates,a,b,output=None):
    if type(a) is not bool or type(b) is not bool:
        raise HOLD("Boolean input required")
    output_mask=mask(gates,output)
    return bool((output_mask >> (2*int(a)+int(b))) & 1)


def _circuits(gate_count):
    """Iterative type-safe DAG enumerator; last gate is the output.

    Enumeration includes (a,a), (a,b), (b,b) as possible NAND gates.
    We do NOT have an XOR/OR/AND/NOT or parity operator.
    """
    if gate_count==0:
        yield (),0,INPUT_A
        yield (),1,INPUT_B
        return

    def grow(gates,wire_masks):
        if len(gates)==gate_count:
            yield gates,len(wire_masks)-1,wire_masks[-1]
            return
        maxpin=len(wire_masks)
        for a in range(maxpin):
            for b in range(a,maxpin):
                nxt=(~(wire_masks[a]&wire_masks[b]))&MASK
                yield from grow(gates+((a,b),),wire_masks+(nxt,))
    yield from grow((),(INPUT_A,INPUT_B))


def synthesize_samples(examples,max_gates=MAX_GATES):
    """Find least-gate program satisfying ALL currently known cases."""
    if (not isinstance(examples,dict) or not 1<=len(examples)<=4 or
            type(max_gates) is not int or not 0<=max_gates<=MAX_GATES):
        raise HOLD("Invalid bounded synthesis specification")
    for inputs,out in examples.items():
        if (not isinstance(inputs,tuple) or len(inputs)!=2 or
                any(type(x) is not bool for x in inputs) or type(out) is not bool):
            raise HOLD("Unknown truth-example contract")
    checked=0
    for g in range(max_gates+1):
        for gates,output,result in _circuits(g):
            checked+=1
            if all(bool(result >> (2*int(a)+int(b)) & 1)==expected
                   for (a,b),expected in examples.items()):
                return {"gates":[list(pair) for pair in gates],
                        "output":output,
                        "truth_mask":result,
                        "gate_count":g,
                        "enumerated_candidates":checked}
    raise HOLD("No candidate in bounded type grammar")


def cegis(verifier,task_id,seed_inputs=((False,False),)):
    """Verifier must expose check(gates,output) -> (a,b,expected) or None.

    It is a narrow research interface, not access to hidden source files.
    Whenever the verifier rejects a candidate, that exact counterexample is
    fed to the next synthesis phase. Exhaustive verification authority is
    outside this module.
    """
    if not isinstance(task_id,str) or not task_id.isidentifier():
        raise HOLD("Invalid task provenance")
    known={}
    for a,b in seed_inputs:
        if type(a) is not bool or type(b) is not bool:
            raise HOLD("Boolean counterexample key required")
        known[(a,b)]=verifier.label_initial(a,b)
    attempts=[]
    for round_id in range(MAX_ROUNDS):
        proposal=synthesize_samples(known)
        challenge=verifier.check(proposal["gates"],proposal["output"])
        record={"round":round_id+1,"candidate":proposal,
                "observed_counterexample":None}
        if challenge is None:
            attempts.append(record)
            raw={
                "schema":SCHEMA,"task_id":task_id,
                "status":"PROVED_FINITE_DOMAIN_PROPOSAL_ONLY",
                "instruction_set":"NAND_DAG_WITH_INPUTS_A_B",
                "gates":proposal["gates"],"output":proposal["output"],
                "gate_count":proposal["gate_count"],
                "truth_mask":proposal["truth_mask"],
                "verifier_exhausted_two_bit_domain":True,
                "cegis_rounds":len(attempts),
                "counterexample_count":sum(
                    x["observed_counterexample"] is not None for x in attempts),
                "source_of_semantic_labels":"INDEPENDENT_FINITE_VERIFIER",
                "real_world_authority":False,
            }
            return {"cartridge":dict(raw,sha256=checksum(raw)),
                    "transcript":attempts}
        if (not isinstance(challenge,tuple) or len(challenge)!=3 or
                any(type(c) is not bool for c in challenge)):
            raise HOLD("Invalid verifier counterexample")
        a,b,expected=challenge
        if (a,b) in known:
            raise HOLD("Verifier returned inconsistent previously examined input")
        if eval_pair(proposal["gates"],a,b,proposal["output"])==expected:
            raise HOLD("Verifier returned false counterexample")
        record["observed_counterexample"]={
            "a":a,"b":b,"expected":expected,"proposed":not expected}
        attempts.append(record)
        known[(a,b)]=expected
    raise HOLD("Exceeded counterexample budget")


def load_verified(cartridge,verifier):
    """Reverify any learned portable data cartridge before running it."""
    if not isinstance(cartridge,dict) or set(cartridge)!={
            "schema","task_id","status","instruction_set","gates","output",
            "gate_count","truth_mask","verifier_exhausted_two_bit_domain",
            "cegis_rounds","counterexample_count","source_of_semantic_labels",
            "real_world_authority","sha256"}:
        raise HOLD("Malformed candidate cartridge")
    raw={k:v for k,v in cartridge.items() if k!="sha256"}
    if checksum(raw)!=cartridge["sha256"]:
        raise HOLD("Modified program or unsigned content")
    if (cartridge["schema"]!=SCHEMA or
            cartridge["status"]!="PROVED_FINITE_DOMAIN_PROPOSAL_ONLY" or
            cartridge["instruction_set"]!="NAND_DAG_WITH_INPUTS_A_B" or
            cartridge["source_of_semantic_labels"]!="INDEPENDENT_FINITE_VERIFIER" or
            cartridge["real_world_authority"] is not False or
            cartridge["verifier_exhausted_two_bit_domain"] is not True):
        raise HOLD("Unknown proof scope")
    gates=cartridge["gates"]
    if (not isinstance(cartridge["gate_count"],int) or
            cartridge["gate_count"]!=len(gates) or
            mask(gates,cartridge["output"])!=cartridge["truth_mask"]):
        raise HOLD("Unverified program content")
    if verifier.check(gates,cartridge["output"]) is not None:
        raise HOLD("Independent finite verifier rejects program")
    return {"status":"FINITE_TRUTH_TABLE_VERIFIED",
            "task_id":cartridge["task_id"],
            "gate_count":len(gates),
            "output_truth_mask":cartridge["truth_mask"],
            "source_identity_authenticated":False,
            "autonomous_algorithm_discovery_claim":"BOUNDED_NAND_CIRCUIT_SYNTHESIS_ONLY",
            "real_world_authority":False}
