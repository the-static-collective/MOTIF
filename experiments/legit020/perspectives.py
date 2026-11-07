"""LEGIT-020: actual Dogram perspective calculations and bitvector proof.

Same carriers can look the same under one declared family of probes and
different under another. "Same" must be indexed by projection and
question language. This module imports pinned actual Dogram math kernels
and the actual LEGIT-019 third-party Z3 bitvector theorem wrapper.

It does NOT claim a metaphor explains a real riverbank, historical
authority, or the human intent of an ambiguous utterance.
"""
from __future__ import annotations

from hashlib import sha1,sha256
from itertools import permutations
from pathlib import Path
from typing import Any
import json
import sys

HERE=Path(__file__).resolve().parent
PARENT=HERE.parent
sys.path.insert(0,str(PARENT/"legit019"))
from algebra import X,prove_equal,val
from vendor_dogram.anti_collapse_reachability import analyze_collapse
from vendor_dogram.operation_reachability_quotient import analyze_operation_reachability
from vendor_dogram.probe_partition_refinement import analyze_probe_family
from vendor_dogram.path_tree_test_language import (
    adjacency_matrix, total_walk_counts, path_recurrence_certificate,
    branching_star_hom_count,homomorphism_count,
)
from aperture import (SenseField,Reading,HOLD,mathalize,speak_math)

# Canonical Dogram research fixture: C6 + isolated K1, and a subdivided
# three-arm claw. Each has 7 nodes and degree sum 12, but different degree
# cubes 48 vs 54. Dogram's path certificate handles all lengths t>=1.
LEFT=((0,1),(1,2),(2,3),(3,4),(4,5),(5,0))
RIGHT=((0,1),(1,2),(0,3),(3,6),(0,4),(4,5))
N=7
DOGRAM_REVISION="551b5f9df18f17ec69b452ddcdff01718e0ff771"
LEGIT019_ROOT=HERE.parent/"legit019"
ALLOWED_MATH={"WALK_EQ","CLAW_EQ","ISOMORPHIC","SHIFT_UNSIGNED",
              "SHIFT_SIGNED","DOUBLE_ADD","DOUBLE_SHIFT"}

def _git_sha(data):
    return sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()

def verify_dogram_source():
    manifest=json.loads((HERE/"vendor_dogram"/"source_manifest.json")
                        .read_text(encoding="utf-8"))
    if (manifest["upstream_repository"]!="the-static-collective/Dogram"
        or manifest["upstream_commit"]!=DOGRAM_REVISION
        or manifest["read_only"] is not True
        or len(manifest["files"])!=4):
        raise HOLD("Canonical Dogram research origin mismatch")
    confirmed={}
    for f in manifest["files"]:
        path=HERE/"vendor_dogram"/Path(f["vendored_path"]).name
        data=path.read_bytes()
        if (_git_sha(data)!=f["upstream_git_blob_sha"]
            or f["upstream_git_blob_sha"]==""
            or f["raw_byte_count"]!=len(data)):
            raise HOLD("Dogram source changed from pinned upstream blob")
        confirmed[f["path"]]=f["upstream_git_blob_sha"]
    return {"original_repository":manifest["upstream_repository"],
            "original_commit":DOGRAM_REVISION,
            "actual_dogram_modules_verified":confirmed,
            "vendor_copy_is_canonical_project_ownership":False}

def _graphs():
    return adjacency_matrix(N,LEFT),adjacency_matrix(N,RIGHT)

def isomorphic(a,b):
    """Independent finite exact isomorphism check for seven nodes."""
    if len(a)!=len(b):return False
    n=len(a)
    if sorted(map(sum,a))!=sorted(map(sum,b)):
        return False
    for perm in permutations(range(n)):
        if all(a[i][j]==b[perm[i]][perm[j]]
               for i in range(n) for j in range(i+1,n)):
            return True
    return False

def graph_spectrum():
    g,h=_graphs()
    sequence_g=total_walk_counts(g,8)
    sequence_h=total_walk_counts(h,8)
    left=path_recurrence_certificate(g,2)
    right=path_recurrence_certificate(h,2)
    if (not left["valid"] or not right["valid"]
        or sequence_g!=sequence_h or
        left["first_walk_count"]!=right["first_walk_count"]
        or left["vertex_count"]!=right["vertex_count"]):
        raise HOLD("No mathematical proof that EVERY path probe collides")
    probes=[]
    for leaves in (1,2,3):
        x=branching_star_hom_count(g,leaves)
        y=branching_star_hom_count(h,leaves)
        probes.append({"probe":"K1_"+str(leaves),
                       "leaves":leaves,"left_count":x,"right_count":y,
                       "distinguishes":x!=y})
    if (probes[0]["distinguishes"] or probes[1]["distinguishes"]
        or not probes[2]["distinguishes"]):
        raise HOLD("Expected minimal branching aperture not found")
    # Brute force actual 7^4=2401 mapping assignments of K1,3.
    star=adjacency_matrix(4,((0,1),(0,2),(0,3)))
    brute_left=homomorphism_count(star,g)
    brute_right=homomorphism_count(star,h)
    if brute_left!=probes[2]["left_count"] or brute_right!=probes[2]["right_count"]:
        raise HOLD("Independent homomorphism enumeration refuted Dogram count")
    equals=isomorphic(g,h)
    if equals:
        raise HOLD("Actual graph identity contradicts branching witness")
    return {
        "perspective_PATH":{
            "meaning":"equal homomorphism counts from every finite linear path",
            "equal":True,"finite_sample_walks":sequence_g,
            "left_linear_path_recurrence":left,
            "right_linear_path_recurrence":right,
            "all_lengths_proof_by_exact_recurrence":True,
        },
        "perspective_BRANCH":{
            "meaning":"equal three-leaf star-homomorphism counts",
            "equal":False,
            "smallest_separating_star_within_1_to_3":3,
            "star_sequence":probes,
            "independent_complete_four_node_claw_mapping":{
                "left":brute_left,"right":brute_right
            },
        },
        "perspective_ISOMORPHISM":{
            "meaning":"graph isomorphism under bijective vertex relabelling",
            "equal":equals,
            "different_degree_multisets_certify_nonisomorphism":True,
        },
        "same_under_one_projection_not_same_under_all":True,
        "general_new_mathematics_claimed":False,
    }

def prove_signedness_difference():
    import z3
    x=z3.BitVec("MOTIF_APERTURE_PERSPECTIVE_x",64)
    solver=z3.Solver()
    solver.set(timeout=3000)
    solver.add(z3.LShR(x,1) != (x>>1))
    if solver.check()!=z3.sat:raise HOLD("Signed/unsigned viewpoint loss not witnessed")
    model=solver.model()
    witness=model.eval(x,model_completion=True).as_long()
    lo=z3.simplify(z3.LShR(z3.BitVecVal(witness,64),1)).as_long()
    ar=z3.simplify(z3.BitVecVal(witness,64)>>1).as_long()
    if lo==ar or witness<(1<<63):
        raise HOLD("Not a proper signedness witness")
    # Critical: both equal 0 on x=0; a single probe falsely suggests same.
    return {
        "mathal":"SHIFT_RIGHT_ONE",
        "ambiguous_untyped_language":"Shift x right by one bit.",
        "candidate_semantics":["64-bit logical unsigned shift",
                               "64-bit arithmetic signed shift"],
        "external_z3_status":"SAT_COUNTEREXAMPLE_TO_EQUIVALENCE",
        "example_x":hex(witness),
        "unsigned_logical_result":hex(lo),
        "signed_arithmetic_result_twos_complement":hex(ar),
        "low_magnitude_inputs_may_collide":True,
        "forced_early_type_resolution_would_erase_a_math_difference":True,
        "semantics_after_context_is_compatibility_not_human_intent":True,
    }

def verify_double_math():
    # Pull actual LEGIT-019 proof machinery, not a hand-written arithmetic
    # replacement. The expression relation remains a known textbook law.
    lhs=("add",X,X)
    rhs=("shl1",X)
    proof=prove_equal(lhs,rhs,64)
    if not proof["identity_valid"]:
        raise HOLD("Actual external theorem prover refuted the bridge")
    actual=json.loads((LEGIT019_ROOT/"generated"/
                       "two_frontier_external_challenge_receipt.json")
                       .read_text(encoding="utf-8"))
    if (actual.get("experiment")!="MOTIF-LEGIT-019" or
        actual.get("claimed_novel_mathematics") is not False or
        actual.get("math_discovery",{}).get("proved_64bit_equations",0)<1):
        raise HOLD("Prior independent Z3 source corpus cannot be trusted")
    # Historical evidence: actual discovered identity, not just arbitrary
    # fresh proof; proof direction may be swapped.
    found=False
    for row in actual["math_discovery"]["conjecture_search"]["z3_formal_proved"]:
        left,right=row["lhs"],row["rhs"]
        normalized=lambda obj:tuple(normalized(x) for x in obj) if isinstance(obj,list) else obj
        left,right=normalized(left),normalized(right)
        if {left,right}=={lhs,rhs} and row["formal"]["identity_valid"]:
            found=True
    if not found:
        raise HOLD("Cannot cite 'double' relationship as old discovered theorem")
    return {
        "English":"Double x modulo 2^64.",
        "possible_maths":["64-bit bitvector x+x","64-bit left shift by one"],
        "translation_variants_distinct":True,
        "external_Z3_proves_equivalence":True,
        "proof_width_bits":64,
        "historically_novel_math":False,
        "prior_actual_LEGIT019_receipt_verified":True,
        "math_to_language_is_gloss_not_proof_of_user_intent":True,
        "proven_formula_relation":proof,
    }

def collapse_receipt(field):
    """Actual Dogram quotient plus operation-reachability receipt.

    WARNING: richer output -> collapsed output is not evidence or semantics.
    This tests only loss of distinguishability/available mathematical probes
    on the declared possible readings.
    """
    if not isinstance(field,SenseField):raise HOLD("No source field")
    if len(field.candidates)<2:raise HOLD("Need multiple possible meanings")
    states=tuple(r.name for r in field.candidates)
    rich=tuple((r.name,r.domain,r.executable_question) for r in field.candidates)
    collapsed=tuple("SINGLE_UNQUALIFIED_ANSWER" for r in states)
    receipt=analyze_collapse(states,rich,collapsed)
    # Mathematically distinct operations are available to different
    # candidate readings; all are lost when the perspective is erased.
    ops=tuple("RUN_"+r.name for r in field.candidates)
    enabled=tuple(tuple(i==j for j in range(len(states)))
                  for i in range(len(states)))
    op=analyze_operation_reachability(states,collapsed,ops,enabled)
    if (not receipt.lawful_quotient or
        not op.ambiguous_classes or op.exact_factorization):
        raise HOLD("Dogram failed to detect the cost of losing an aperture")
    return {
        "source_readings":list(states),
        "dogram_original_api":"analyze_collapse / analyze_operation_reachability",
        "lawful_quotient":receipt.lawful_quotient,
        "deterministic_factorization":[list(x) for x in receipt.factorization_witness],
        "lost_reading_pairs":[list(x) for x in receipt.lost_distinctions],
        "lost_operation_questions":[list(x) for x in op.lost_operation_questions],
        "lost_future_operation_executability":True,
        "collapsed_projection":"SINGLE_UNQUALIFIED_ANSWER",
        "mathematical_loss_is_not_world_meaning_or_authority":True,
    }

def graph_probe_ladder():
    """Analyze the original Dogram path-vs-star view as a probe-poset."""
    data=graph_spectrum()
    g,h=_graphs()
    states=("G","H")
    path=tuple(total_walk_counts(graph,8) for graph in (g,h))
    star1=tuple(branching_star_hom_count(graph,1) for graph in (g,h))
    star2=tuple(branching_star_hom_count(graph,2) for graph in (g,h))
    star3=tuple(branching_star_hom_count(graph,3) for graph in (g,h))
    # Dogram probe families reject duplicate induced partitions.
    ladder=analyze_probe_family(states,{
        "LINEAR_WALKS_0_8":path,
        "BRANCH_3":star3,
    },("G","H"))
    if ladder.separating_probes!=("BRANCH_3",):
        raise HOLD("Perspective proof did not find branching separator")
    return {
        "min_separating_probe_in_supplied_family":ladder.minimal_separators,
        "path_projection_equivalence_class":ladder.partitions["LINEAR_WALKS_0_8"],
        "branch_projection_equivalence_class":ladder.partitions["BRANCH_3"],
        "path_is_strictly_weaker_than_branch_on_this_pair":
            ("BRANCH_3","LINEAR_WALKS_0_8") in ladder.cover_relations,
        "minimality_only_in_supplied_family":True,
        "separation_underlying_carrier_change":False,
    }
