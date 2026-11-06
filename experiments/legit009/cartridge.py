"""LEGIT-009: actual LEGIT-007 source-witness diagnostic crosswire.

The newly synthesized circuit is called as executable typed DATA.
It flags whether two independently declared origins express opposing
Boolean claims. It does NOT override legacy probabilistic inference.

A separate XOR/odd-parity fold is a reusable cartridge composition.
The proof is conditional on the two-input truth table and ordinary
Boolean induction; all outputs remain READ-ONLY research notices.
"""
from __future__ import annotations
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"legit007"))
from provenance import validate,route as legacy_route
from independent_oracle import IndependentVerifier, canonical_sop_xor
from synthesizer import HOLD, eval_pair, load_verified


def parity_fold(bits,cartridge):
    if not isinstance(bits,(list,tuple)) or len(bits)>100000 or any(type(x) is not bool for x in bits):
        raise HOLD("Bounded Boolean sequence required")
    checker=IndependentVerifier("DISAGREEMENT")
    load_verified(cartridge,checker)
    result=False
    gates=cartridge["gates"]
    output=cartridge["output"]
    for bit in bits:
        result=eval_pair(gates,result,bit,output)
    return {
        "odd_parity":result,
        "input_bits":len(bits),
        "generated_NAND_operations":len(gates)*len(bits),
        "canonical_NAND_SOP_operations":len(canonical_sop_xor())*len(bits),
        "inductive_step_invariant":(
            "P(next) = P(previous) XOR bit for each binary next input; "
            "base P(empty)=false. Applies to arbitrary finite lengths."),
        "safety":"SYNTHETIC_OR_TYPED_BOOLEAN_ONLY",
        "real_world_authority":False,
    }


def conflicting_independent_origins(packet,cartridge):
    verifier=IndependentVerifier("DISAGREEMENT")
    certificate=load_verified(cartridge,verifier)
    graph=validate(packet)
    # Use exactly the original 007 interpretation of root identity:
    # this is a declaration, not external proof of provenance.
    origins=sorted(graph["origin_signature"].items())
    conflicts=[]
    for i,(first,(a,_)) in enumerate(origins):
        for second,(b,_) in origins[i+1:]:
            # This call executes a program the synthesizer constructed.
            if eval_pair(cartridge["gates"],a,b,cartridge["output"]):
                conflicts.append([first,second])
    previous=legacy_route(packet)
    return {
        "schema":"motif.generated-witness-disagreement.v1",
        "status":"RESEARCH_HOLD",
        "generated_cartridge":certificate,
        "source_packet_sha256":previous["source_packet_sha256"],
        "distinct_declared_origins":len(origins),
        "pairs_compared":len(origins)*(len(origins)-1)//2,
        "opposing_source_pairs":conflicts,
        "legacy_inference_unmodified":True,
        "original_posterior_true":previous["posterior_true_given_declared_calibration"],
        "source_identity_authenticated":False,
        "truth_about_world_inferred_from_conflict":False,
        "real_world_authority":False,
        "actions_issued":0,
    }
