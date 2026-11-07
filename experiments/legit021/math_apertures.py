"""LEGIT-021 — APERTURE question formation across graph and bitvector math.

A computationally discriminating experiment need not authorize a natural
language interpretation. This module reuses the *actual* LEGIT-020
semantic aperture protocol and its Z3 interface, while a separately
authored classical mathematical test checks claims of minimality.

A divergent bitvector result can tell which mathematical operations
differ, but it CANNOT tell which meaning a human intended. A proven
equality means that NO input separates those operations.
"""
from __future__ import annotations

from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"legit020"))
from aperture import open_aperture,mathalize,receipt_hash,HOLD
from perspectives import verify_dogram_source,verify_double_math
from vendor_dogram.probe_partition_refinement import analyze_probe_family
from graph_inventor import grammar,characterize,count,all_path_collision

def z3_status(solver):
    import z3
    decision=solver.check()
    if decision not in (z3.sat,z3.unsat):
        raise HOLD("SMT timeout/unknown cannot be treated as a proof")
    return decision

def invent_bitvector_counterprobe():
    """Independently prove minimum unsigned x separating the two shifts.

    This is a known arithmetic distinction, not new mathematics. A
    solver produces the witness and separately proves no unsigned
    smaller word can distinguish the two.
    """
    import z3
    field=mathalize(open_aperture("Shift x right by one bit."))
    ids=[x["id"] for x in field["language_to_math_candidates"]]
    if ids!=["SHIFT_UNSIGNED","SHIFT_SIGNED"]:
        raise HOLD("Interpretations changed without source permission")
    x=z3.BitVec("APERTURE021_unknown_word",64)
    unsigned=z3.LShR(x,1)
    signed=x>>1
    candidate=1<<63
    def make():
        s=z3.Solver();s.set(timeout=4000)
        s.add(unsigned!=signed)
        return s
    solver=make()
    if z3_status(solver)!=z3.sat:
        raise HOLD("Signed/unsigned operator distinction not real")
    # The smallest admissible unsigned counterexample is an exact
    # 2^63 word. Require Z3 SAT at the boundary and UNSAT below it.
    at_boundary=make()
    at_boundary.add(x==z3.BitVecVal(candidate,64))
    if z3_status(at_boundary)!=z3.sat:
        raise HOLD("Bitvector boundary witness not viable")
    below=make()
    below.add(z3.ULT(x,z3.BitVecVal(candidate,64)))
    if z3_status(below)!=z3.unsat:
        raise HOLD("Could not prove witness is minimal")
    u=z3.simplify(z3.LShR(z3.BitVecVal(candidate,64),1)).as_long()
    a=z3.simplify(z3.BitVecVal(candidate,64)>>1).as_long()
    if u==a:
        raise HOLD("Mathematical probe did not distinguish")
    return {
        "original_language":"Shift x right by one bit.",
        "mathalizer_initial_aperture":field,
        "new_question":"Which 64-bit signedness is intended, or what output is expected at this counterexample?",
        "probe_type":"MINIMUM_UNSIGNED_COUNTEREXAMPLE",
        "witness_unsigned_x":hex(candidate),
        "logical_output":hex(u),
        "arithmetic_output_twos_complement":hex(a),
        "independent_Z3_exists_witness":"SAT",
        "independent_Z3_no_smaller_unsigned_witness":"UNSAT",
        "minimal_within_all_unsigned_64bit_inputs":True,
        "interpretation_authority":"HUMAN_CONTEXT_REQUIRED",
        "model_does_not_claim_to_know_user_intent":True,
        "historically_novel_math":False
    }

def indistinguishable_math():
    """Formal impossibility of a separating numeric example."""
    import z3
    source=mathalize(open_aperture("Double x modulo 2^64."))
    ids=[x["id"] for x in source["language_to_math_candidates"]]
    if ids!=["DOUBLE_ADD","DOUBLE_SHIFT"]:
        raise HOLD("Unexpected source mathematical interpretations")
    historical=verify_double_math()
    if not historical["external_Z3_proves_equivalence"]:
        raise HOLD("No prior independently proven identity")
    x=z3.BitVec("APERTURE021_double_x",64)
    solver=z3.Solver()
    solver.set(timeout=4000)
    solver.add(x+x!=x<<1)
    if z3_status(solver)!=z3.unsat:
        raise HOLD("Claimed equivalence not universal in the typed domain")
    return {
        "original_language":"Double x modulo 2^64.",
        "initial_aperture":source,
        "candidate_probes_tested":"ALL_UNSIGNED_64BIT_WORDS_BY_FORMAL_SMT",
        "different_observation_possible":False,
        "separation_query_Z3_result":"UNSAT",
        "suggested_next_action":"HOLD_NO_NUMERICAL_DISTINCTION; ask about implementation or operator intent only when needed",
        "known_identity_reused_from_LEGIT019":True,
        "does_not_erase_source_reading_difference":True,
    }

def perspective_lattice_for_worlds(worlds):
    """Run original pinned Dogram probe-poset over invented observations."""
    if len(worlds)!=3:raise HOLD("Three worlds required")
    exact=grammar()
    tri=next(p for p in exact if characterize(p)["triangle"])
    square=next(p for p in exact if characterize(p)["four_cycle"])
    all_paths=all_path_collision(worlds)
    names=("C8","C3_PLUS_C5","C4_PLUS_C4")
    path=tuple(tuple(all_paths["first_nine_walk_counts"]) for _ in worlds)
    triangle=tuple(count(tri,w) for w in worlds)
    four_cycle=tuple(count(square,w) for w in worlds)
    tree=analyze_probe_family(names,{
        "LINEAR_PATHS":path,
        "TRIANGLE_MAPPINGS":triangle,
        "SQUARE_MAPPINGS":four_cycle
    },("C8","C3_PLUS_C5"))
    if "TRIANGLE_MAPPINGS" not in tree.separating_probes:
        raise HOLD("Generated triangle fails to distinguish required worlds")
    if triangle[0]!=triangle[2] or four_cycle[0]!=four_cycle[1]:
        raise HOLD("Perspective algebra does not match heldout graph carriers")
    return {
        "worlds":names,
        "linear_path_counts_equal_for_all_lengths":True,
        "triangle_counts":triangle,
        "four_cycle_counts":four_cycle,
        "original_Dogram_partition_relations":[list(x) for x in tree.cover_relations],
        "original_Dogram_partitions":{
            k:[list(block) for block in p]
            for k,p in tree.partitions.items()
        },
        "source_probe_is_part_of_mathematical_question":True,
        "graph_identity_not_inferred_from_one_projection":True,
        "no_world_evidence_authority_from_partitions":True,
    }
