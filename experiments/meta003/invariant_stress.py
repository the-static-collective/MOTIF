"""META-003 — counterexample-guided nonlinear stateful Collatz rank research.

Two actual attacks on the still-OPEN conjecture:
 (A) Fit strictly decreasing quadratic+finite-residue-offset potential to
     small trajectories, then *construct* an infinite-family counterexample
     from a positive residue self-loop and prove a class-wide no-go.
 (B) Refine the META-002 exact 2-adic certificate frontier from 12 to 16 bits.
     A finite branching decision tree certifies NEW infinite subfamilies,
     while adversarial parity-bit continuations prove no fixed-depth cover
     eliminates any currently HOLD base-class by this descent method.

A source of genuinely NEW mathematical theorems is NOT claimed. The grammar,
candidate family, source fixtures, stopping-time certificates and classical
comparators are developer-authored. No actual independent remote agent.
"""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
from itertools import product
import json
import sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"meta001"))
sys.path.insert(0,str(HERE.parent/"meta002"))
from collatz_frontier import T,reference_T,HOLD,canonical,digest,FiniteSourceOwner
from variable_horizon import classical_first_descent

SCHEMA="motif.meta003.nonlinear-stateful-collatz-research.v1"
BASE_K=12
DEEP_K=16
MAX_K=17
OPEN=[
    "The Collatz conjecture remains open; no global theorem or counterexample was proved",
    "The nonlinear rank family and finite-memory residue states were engineered",
    "The all-odd residue self-loop blocks strictly increasing base-size potential plus any finite residue correction, not all possible ranking functions",
    "Adaptive 2-adic finite-depth certificates remain partial, even after refinement",
    "A positive result for infinitely many members of each finite residue cylinder is not a proof for all positive integers",
    "All source owners are local, source identity is not externally authenticated",
    "Classical exact baseline has equal information; no super-classical advantage",
]


def _level(k):
    if type(k) is not int or not 1 <= k <= MAX_K:
        raise HOLD("Invalid finite arithmetic research precision")


def affine_prefixes(k,r):
    """Derive T^j(n)=(a*n+b)/2^j, for ALL n==r mod 2^k, j<=k."""
    _level(k)
    if type(r) is not int or not 0 <= r < (1<<k):
        raise HOLD("Invalid exact residue cylinder")
    n0=r if r>1 else r+(1<<k)
    a,b,d=1,0,1
    out=[]
    for j in range(1,k+1):
        numerator=a*r+b
        if numerator%d:
            raise HOLD("Affine representation not integer")
        parity=numerator//d %2
        # For arbitrary n=r+q*2^k, current iterate differs by
        # a*q*2^k/d, which is even because j-1<k.
        if (a*(1<<k))%(2*d):
            raise HOLD("Parity is not uniform on residue cylinder")
        if parity:
            a,b,d=3*a,3*b+d,2*d
        else:
            d*=2
        out.append({
            "step":j,
            "parity":"ODD" if parity else "EVEN",
            "numerator_a":a,"numerator_b":b,"denominator":d,
            "strict_descent_at_all_members":
                a<d and a*n0+b<d*n0,
            "strictly_increasing_slope":a>d,
        })
    if d != (1<<k):
        raise HOLD("Failed exact k-step denominator")
    return out


def first_class_descent(k,r):
    """Return first j certified to drop for EVERY n>1 in residue class."""
    p=affine_prefixes(k,r)
    for row in p:
        if row["strict_descent_at_all_members"]:
            return row["step"]
    return None


def independent_first_class_descent(k,r):
    """Separate classical algorithm: direct orbit + parity product for slope."""
    _level(k)
    if type(r) is not int or not 0<=r<1<<k:
        raise HOLD("Invalid independent reference residue")
    n0=r if r>1 else r+(1<<k)
    n=n0
    odd_count=0
    for j in range(1,k+1):
        odd_count+=n%2
        n=reference_T(n)
        if 3**odd_count < 2**j and n<n0:
            return j
    return None


def rank(n,p,offsets):
    if type(n) is not int or n<1:
        raise HOLD("Positive state required")
    if type(p) is not int or p not in (1,2,3):
        raise HOLD("Declared nonlinear/linear rank exponent outside grammar")
    if type(offsets) is not list or len(offsets) not in (8,16,32):
        raise HOLD("Finite-state rank modulus outside grammar")
    if any(type(x) is not int for x in offsets):
        raise HOLD("Invalid integer residue-correction")
    return n**p+offsets[n%len(offsets)]


def fit_rank(modulus,exponent,training_end):
    """Synthesize residue corrections by classical difference constraints.

    For 2<=n<=N, ranking inequalities become
    b_(T(n) mod m)-b_(n mod m) <= n**p-T(n)**p-1.
    Bellman-Ford derives a solution or an infeasible cycle.
    It does NOT prove any unbounded property.
    """
    if modulus not in (8,16,32) or exponent not in (1,2,3) or (
        type(training_end) is not int or not 2<=training_end<=64
    ):
        raise HOLD("Rank fitting budget exceeded")
    edges=[]
    for n in range(2,training_end+1):
        nxt=T(n)
        edges.append({"from":n%modulus,"to":nxt%modulus,
                      "maximum_difference":n**exponent-nxt**exponent-1,
                      "n":n, "next_n":nxt})
    vals=[0]*modulus
    last_changes=[]
    for repeat in range(modulus):
        changed=False
        last_changes=[]
        for edge in edges:
            a,b,w=(edge[x] for x in ("from","to","maximum_difference"))
            if vals[b]>vals[a]+w:
                vals[b]=vals[a]+w
                changed=True
                last_changes.append(edge["n"])
        if not changed:
            break
    else:
        # If changed in mth iteration, the constraints have a negative cycle.
        return {"status":"HOLD_NO_RESIDUE_OFFSETS_SATISFY_ALL_TRAINING_EDGES",
                "modulus":modulus,"exponent":exponent,
                "training_max":training_end,
                "constraints":edges,
                "negative_cycle_detected":True,
                "negative_cycle_vertex_trace_available":False}
    if any(rank(T(n),exponent,vals)>=rank(n,exponent,vals)
           for n in range(2,training_end+1)):
        raise HOLD("Difference constraint solution violates training observations")
    return {"status":"FITTED_FINITE_SAMPLE_ONLY",
            "modulus":modulus,"exponent":exponent,
            "training_max":training_end,
            "offsets":vals,
            "constraints":edges,
            "not_a_global_rank_proof":True}


def same_residue_increasing_step(modulus):
    """Universal counterexample family to ANY finite-residue monotone-f rank.

    n=2*m*t-1 has residue m-1. T(n)=3*m*t-1 has SAME residue.
    Since T(n)>n, for any strictly increasing f and any fixed offsets
    phi_r, V(T(n))=f(T(n))+phi_r>f(n)+phi_r=V(n).
    More generally, positive class weight w_r has same obstruction.
    """
    if modulus not in (2,4,8,16,32,64,128):
        raise HOLD("Finite-state source graph outside research contract")
    n=2*modulus-1
    succ=T(n)
    if not (succ==3*modulus-1 and succ>n
            and n%modulus==succ%modulus==modulus-1):
        raise HOLD("Odd-prefix residue self-loop did not reproduce")
    return {
        "kind":"ALL_ONE_BITS_RESIDUE_EXPANDING_SELF_LOOP",
        "modulus":modulus,
        "base_residue":modulus-1,
        "positive_example_n":n,
        "positive_example_successor":succ,
        "infinite_family_input":"n=2*m*t-1, for m=modulus and all t>=1",
        "infinite_family_successor":"T(n)=3*m*t-1",
        "same_state_before_and_after":True,
        "strict_size_increase":True,
        "mathematical_no_go":
            "No V(n)=w_(n mod m)*f(n)+phi_(n mod m), with each "
            "w_r>0, arbitrary constant phi_r and STRICTLY INCREASING "
            "f, can strictly decrease on EVERY accelerated Collatz step.",
        "does_not_exclude_variable_horizon_or_nonmonotone_functions":True,
        "does_not_refute_collatz":True,
        "no_claim_of_new_historical_theorem":True,
    }


def counterexample_guided_ranking(modulus=16,exponent=2,starting_training=14):
    """Generate an attractive finite-fit rank, then reject it with witnesses."""
    loop=same_residue_increasing_step(modulus)
    trials=[]
    max_n=2*modulus-1
    N=starting_training
    while N<=max_n:
        fit=fit_rank(modulus,exponent,N)
        if fit["status"]!="FITTED_FINITE_SAMPLE_ONLY":
            trials.append({"status":"TRAINING_GRAMMAR_INFEASIBLE",
                           "training_max":N,"result":fit})
            break
        offsets=fit["offsets"]
        first_bad=next((
            n for n in range(N+1,max_n+1)
            if rank(T(n),exponent,offsets)>=rank(n,exponent,offsets)
        ),None)
        trials.append({
            "status":"CANDIDATE_REFUTED_ON_HELDOUT" if first_bad else (
                "NO_COUNTEREXAMPLE_FOUND_IN_LOCAL_WINDOW"
            ),
            "source_model":fit,
            "first_heldout_counterexample_n":first_bad,
            "first_heldout_counterexample_successor":(
                T(first_bad) if first_bad else None
            ),
            "counterexample_measured_rank_before":(
                rank(first_bad,exponent,offsets) if first_bad else None
            ),
            "counterexample_measured_rank_after":(
                rank(T(first_bad),exponent,offsets) if first_bad else None
            ),
            "not_a_global_proof":True,
        })
        if first_bad is None:
            break
        N=first_bad
    if not trials or trials[0]["status"]!="CANDIDATE_REFUTED_ON_HELDOUT":
        raise HOLD("The research candidate did not exhibit tested failure")
    return {
        "schema":"motif.meta003.cegis-rejected-ranking.v1",
        "model_family":"n**p + b_(n modulo m)",
        "initial_training_window":[2,starting_training],
        "attempts":trials,
        "formal_family_counterexample":loop,
        "candidate_fits_a_finite_window_but_cannot_prove_every_step":True,
        "status":"REFUTED_BOUNDED_NONLINEAR_RESIDUE_RANK_GRAMMAR",
    }


def choose_adversarial_odd_continuation(k_base,r,k_final):
    """Exact 2-adic adversary: extend unresolved prefix, then select odd bits.

    At each j, the two lifts r and r+2**j have opposite parity at T**j,
    because T**j(n+2**j)-T**j(n) = 3**odd_count (odd). Thus an
    ALL-ODD extension exists for any desired finite extra length.
    """
    _level(k_base);_level(k_final)
    if k_final<k_base or type(r) is not int or not 0<=r<(1<<k_base):
        raise HOLD("Invalid 2-adic proof-tree scope")
    p=affine_prefixes(k_base,r)
    if any(row["numerator_a"] < row["denominator"] for row in p):
        raise HOLD("Parent has an eventual-descent slope; cannot apply strong all-odd no-go")
    selected=r
    choices=[]
    for j in range(k_base,k_final):
        current=selected
        lifted=selected+(1<<j)
        def value_at_depth(n):
            value=n
            for _ in range(j):
                value=reference_T(value)
            return value
        a=value_at_depth(current)
        b=value_at_depth(lifted)
        if (a-b)%2==0:
            raise HOLD("Next parity bit is not freely controllable")
        selected=(current if a%2 else lifted)
        choices.append({"from_precision":j,"to_precision":j+1,
                        "selected_residue":selected,
                        "jth_iterate_odd":True})
    pnew=affine_prefixes(k_final,selected)
    if any(row["numerator_a"]<row["denominator"] for row in pnew):
        raise HOLD("Adversarial extension unexpectedly has a decreasing slope")
    if any(row["strict_descent_at_all_members"] for row in pnew):
        raise HOLD("Adversarial extension unexpectedly certified")
    if any(x["parity"]!="ODD" for x in pnew[k_base:]):
        raise HOLD("Parity-continuation schedule was not achieved")
    return {
        "base_k":k_base,"base_residue":r,
        "new_k":k_final,"selected_residue":selected,
        "odd_tail_bit_choices":choices,
        "parent_has_no_decreasing_prefix_slope":True,
        "selected_descendant_has_no_strict_descent_up_to_depth":k_final,
        "all_integers_in_descendant_have_no_strict_descent_by_that_depth":True,
        "general_symbolic_argument":
            "For any additional finite precision each next parity bit "
            "can be chosen ODD because lifting n by 2**j toggles "
            "the parity of T**j(n). Starting from a prefix where all "
            "affine slopes are >=1, odd steps multiply the slope by 3/2 "
            "and preserve nonnegative intercept. Hence a descendant "
            "cylinder survives any predetermined finite horizon.",
        "does_not_prove_infinite_divergence_or_refute_collatz":True,
    }


def refine_frontier(*,base_k=BASE_K,deep_k=DEEP_K):
    """Proof-producing finite-state decision-tree cylinder refinement.

    Only previously uncategorized parents are split. Each child is an
    INFINITE congruence progression. Do not count individual numbers.
    """
    if (base_k!=BASE_K or deep_k not in (13,14,15,16)
        or deep_k<=base_k):
        raise HOLD("Unfrozen proof tree research budget")
    base_count=1<<base_k
    old_holds=[]
    previous_certified=0
    for r in range(base_count):
        result=first_class_descent(base_k,r)
        independent=independent_first_class_descent(base_k,r)
        if result!=independent or result!=classical_first_descent(base_k,r):
            raise HOLD("Known META-002 classical exact method disagrees at parent level")
        if result is None:
            old_holds.append(r)
        else:
            previous_certified+=1
    if (previous_certified,len(old_holds))!=(3870,226):
        raise HOLD("Original META-002 regression changed")
    children_per_parent=1<<(deep_k-base_k)
    new_cards=[]
    still_held=[]
    parent_stats=[]
    for r in old_holds:
        covered=0
        for t in range(children_per_parent):
            child=r+(t<<base_k)
            first=first_class_descent(deep_k,child)
            classical=independent_first_class_descent(deep_k,child)
            if first!=classical:
                raise HOLD("Independent classical descendant's result differs")
            entry={"parent_residue":r,"child_residue":child,
                   "child_modulus":1<<deep_k,
                   "first_proved_strict_descent_time":first,
                   "status":("INFINITE_CHILD_CLASS_CERTIFIED" if first is not None
                             else "HOLD_INFINITE_CHILD_CLASS_UNRESOLVED"),
                   "not_a_global_collatz_proof":True}
            if first is None:
                still_held.append(entry)
            else:
                # Store only the exact ancestor proof card needed for transfer.
                j=first
                row=affine_prefixes(j,child%(1<<j))[-1]
                if not (row["numerator_a"] < row["denominator"]):
                    raise HOLD("Certificate slope inconsistent")
                n0=child if child>1 else child+(1<<deep_k)
                if row["numerator_a"]*n0+row["numerator_b"] >= row["denominator"]*n0:
                    raise HOLD("Certificate exception lost")
                entry["proof_affine"]={
                    "k":j,"modulus":1<<j,"residue":child%(1<<j),
                    "a":row["numerator_a"],
                    "b":row["numerator_b"],
                    "d":row["denominator"],
                    "smallest_descendant_integer_gt_one":n0,
                    "whole_descendant_cylinder_certified":True,
                }
                new_cards.append(entry)
                covered+=1
        # Independent symbolic adversarial extension for EVERY unresolved parent.
        adversary=choose_adversarial_odd_continuation(base_k,r,deep_k)
        if adversary["selected_residue"] not in {
            x["child_residue"] for x in still_held[-children_per_parent:]
        }:
            raise HOLD("Constructed untouched parity descendant not found")
        parent_stats.append({
            "base_residue":r,
            "children":children_per_parent,
            "newly_certified_children":covered,
            "uncertified_children":children_per_parent-covered,
            "full_parent_class_certified":covered==children_per_parent,
            "adversarial_no_full_parent_cert":adversary,
        })
    originally_covered_at_deep=previous_certified*children_per_parent
    total=1<<deep_k
    certified_total=originally_covered_at_deep+len(new_cards)
    if certified_total+len(still_held)!=total:
        raise HOLD("Incomplete 2-adic proof partition")
    if any(x["full_parent_class_certified"] for x in parent_stats):
        raise HOLD("A fully certified parent contradicts proven all-odd extension")
    return {
        "schema":"motif.meta003.two-adic-stateful-refinement.v1",
        "base_k":base_k,"deep_k":deep_k,
        "initial_modular_parent_classes":base_count,
        "previously_certified_base_classes":previous_certified,
        "previously_held_base_classes":len(old_holds),
        "exact_new_subclasses_examined":len(old_holds)*children_per_parent,
        "already_proven_descendants_reused_not_requeried":originally_covered_at_deep,
        "newly_certified_infinite_descendant_classes":len(new_cards),
        "remaining_uncertified_descendant_classes":len(still_held),
        "total_certified_deep_residue_classes":certified_total,
        "total_deep_residue_classes":total,
        "complete_new_child_certificates":new_cards,
        "complete_remaining_holds":still_held,
        "parent_refinements":parent_stats,
        "one_child_per_held_parent_still_uncertified_at_every_chosen_finite_depth":True,
        "classical_exact_reference_agrees_for_all_new_queries":True,
        "saved_prior_certificates_are_reused":True,
        "this_is_infinite_family_coverage_not_individual_orbit_proof":True,
        "no_completeness_of_infinite_collatz_conjecture":True,
    }


def investigate():
    proposals=[
        counterexample_guided_ranking(16,1,14),
        counterexample_guided_ranking(16,2,14),
        counterexample_guided_ranking(16,3,14),
    ]
    all_states=[same_residue_increasing_step(m)
                for m in (2,4,8,16,32,64,128)]
    # Four different stateful candidate bases n, n^2, n^3, log(n)
    # are monotone f; common residue self-loop disproves all
    # (with arbitrary positive residue-specific weight and offsets).
    frontier=refine_frontier()
    if (frontier["newly_certified_infinite_descendant_classes"]!=1502 or
        frontier["remaining_uncertified_descendant_classes"]!=2114 or
        frontier["total_certified_deep_residue_classes"]!=63422):
        raise HOLD("Declared source-independent 2-adic class partition changed")
    return_packet={
        "schema":SCHEMA,
        "original_open_question":"Does every positive integer reach 1 under Collatz?",
        "status":"OPEN_UNRESOLVED_MATHEMATICAL_RESEARCH_HOLD",
        "meta002_source_status":"226 modulo-4096 cylinders lack first-descent certificate by 12 steps",
        "new_nonlinear_finite_state_potential_proposals":proposals,
        "self_loop_general_counterexamples":all_states,
        "new_conditional_question_type":
            "CAN_A_FINITE_STATE_CYLINDER_TREE_CERTIFY_VARIABLE_HORIZON_DESCENT",
        "stateful_two_adic_question_frontier":frontier,
        "strategy_rejected":
            "SAME_RESIDUE_STRICTLY_INCREASING_SIZE_POTENTIAL_ON_EVERY_STEP",
        "strategy_remaining":
            "UNBOUNDED_MEMORY_NONLOCAL_PROGRESS_OR_NONMONOTONE_WELL_FOUNDED_RANKING",
        "next_relevant_question":
            "Can an explicitly well-founded, nonlocal or unbounded-memory "
            "progress certificate handle the 2-adic adverse parity continuation "
            "without relying on unproved randomness, a fixed horizon, "
            "or finite-residue monotone-size potentials?",
        "known_mathematics_not_historically_new":True,
        "strong_classical_adaptive_baseline_ties":True,
        "engineer_authored_candidate_grammar_and_budgets":True,
        "source_owner_independent_human_authenticated":False,
        "open_limitations":list(OPEN),
        "automatic_admission":False,"installed":False,
        "external_authority":"NONE",
    }
    return_packet["integrity_digest"]=digest(return_packet)
    return return_packet


def verify_packet(packet):
    if type(packet) is not dict or packet.get("schema")!=SCHEMA:
        raise HOLD("Wrong nonlinear rank research packet schema")
    if packet.get("integrity_digest")!=digest({
        k:v for k,v in packet.items() if k!="integrity_digest"
    }):
        raise HOLD("Corrupted nonlinear rank research record")
    if packet!=investigate():
        raise HOLD("Rehashed non-mathematical or falsified evidence refused")
    return True


def reenter(packet):
    verify_packet(packet)
    return {
        "status":"OPEN_RANK_HYPOTHESES_AND_2ADIC_CERTIFICATES_REVERIFIED",
        "new_investigative_source_questions":0,
        "all_source_observations_recomputed":True,
        "global_collatz_conjecture_solved":False,
        "packet_digest":packet["integrity_digest"],
    }


if __name__=="__main__":
    packet=investigate()
    print(json.dumps(packet,indent=2,sort_keys=True))
