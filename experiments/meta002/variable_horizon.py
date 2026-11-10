"""META-002 — variable-time ranking hypotheses against an actual open problem.

The Collatz conjecture remains OPEN. This code attempts/falsifies finite-state
one-step potentials and constructs exact variable-horizon descent certificates
over infinite residue classes. It does not provide a general ranking function.

Research methods are known classical stopping-time methods. Question-selection,
grammar, budgets, and source-owner interface are human-authored; the result
is NOT mathematical novelty, general autonomous invariant invention or proof
of universal convergence.
"""
from __future__ import annotations

from copy import deepcopy
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"meta001"))

from collatz_frontier import (
    HOLD, T, reference_T, certificate, verify_certificate,
    fixed_horizon_diagonal_obstruction, FiniteSourceOwner, digest
)

SCHEMA = "motif.meta002.variable-time-ranking-research.v1"
MAX_K = 12
KNOWN_REFERENCES = [
    {
        "title": "Collatz Stopping Time — Wolfram MathWorld",
        "url": "https://mathworld.wolfram.com/CollatzStoppingTime.html",
        "known_result": "Finite first descent for every n>1 is equivalent to Collatz convergence by strong induction.",
        "does_not_prove_conjecture": True,
    },
    {
        "title": "Lagarias, The 3x+1 problem and its generalizations (1985)",
        "doi": "10.1080/00029890.1985.11971528",
        "known_result": "Classical stopping-time and accelerated-map analysis",
        "does_not_prove_conjecture": True,
    },
    {
        "title": "Terras (1976) and Everett (1977) stopping-time density literature",
        "known_result": "Almost all starts have finite first descent; almost all is not every integer.",
        "does_not_prove_conjecture": True,
    },
]
UNRESOLVED = [
    "Infinitely many positive starts exist in every residue class still marked HOLD.",
    "Showing a finite representative falls below its start does not prove its entire infinite class.",
    "For every fixed K there is at least the all-odd residue 2**K-1 with no descent by K steps.",
    "No well-founded global ranking or total variable-time descent law has been established.",
    "The modular affine and stopping-time methods are known classical mathematics.",
    "Human-designed search grammar and exact arithmetic, not unrestricted concept invention.",
    "The simulated source-owner callback is not an independent scientific witness.",
]


def _check_level(k):
    if type(k) is not int or not 1 <= k <= MAX_K:
        raise HOLD("Finite certificate level out of scope")


def minimum_member_over_one(k,r):
    """First n>1 in the complete class r modulo 2**k."""
    _check_level(k)
    if type(r) is not int or not 0 <= r < 1<<k:
        raise HOLD("Unrecognized residue")
    return r if r > 1 else r+(1<<k)


def classical_first_descent(k,r):
    """Independently implemented known classical exact Fraction baseline.

    Algebra is built directly on the *smallest n>1 in the full k-class*.
    At depth j<=k, future n are this representative + t*2**k. The
    affine slope alpha is the same, and the parity pattern is uniform,
    since before step j a shift of 2**k changes the value by an even int.
    If alpha<1 and T**j(n_min)<n_min, every larger member of this class
    also descends by the same j. This is a proven infinite-family result,
    not a mere finite-sample guess.
    """
    n0=minimum_member_over_one(k,r)
    alpha,beta=Fraction(1),Fraction(0)
    for j in range(1,k+1):
        current=alpha*n0+beta
        if current.denominator!=1:
            raise HOLD("Classical symbolic orbit was not integral")
        shift=alpha*(1<<k)
        if shift.denominator!=1 or shift.numerator%2:
            raise HOLD("Parity not constant on this entire parent class")
        if current.numerator%2:
            alpha,beta=(3*alpha/2),(3*beta+1)/2
        else:
            alpha,beta=alpha/2,beta/2
        if alpha<1 and alpha*n0+beta<n0:
            return j
    return None


def _first_card(k,r,cache=None):
    """Inspect all candidate time horizons; select the earliest PROVED one."""
    n0=minimum_member_over_one(k,r)
    attempts=[]
    chosen=None
    for j in range(1,k+1):
        smaller_residue=r % (1<<j)
        cache_key=(j,smaller_residue)
        if cache is not None and cache_key in cache:
            c=cache[cache_key]
        else:
            c=certificate(*cache_key)
            if cache is not None:
                cache[cache_key]=c
        a,b,d=(c["symbolic_affine"][x] for x in ("a","b","denominator"))
        # A slope <1 is needed for uniform descent on an infinite class.
        # Even with negative slope, the representative must clear the exact
        # positive threshold, or the class-wide assertion is false.
        all_class=(a<d and d*n0>a*n0+b)
        attempt={
            "horizon":j,
            "source_residue":smaller_residue,
            "affine_coefficients":[a,b,d],
            "old_fixed_horizon_inadequacy":
                "SLOPE_NOT_DECREASING" if a>=d else
                "EXCEPTIONAL_SMALL_MEMBER" if not all_class else "NONE",
            "descends_for_every_n_gt_one_in_parent_class":bool(all_class),
        }
        attempts.append(attempt)
        if all_class and chosen is None:
            verify_certificate(c)
            chosen=deepcopy(c)
    return {
        "residue":r, "parent_modulus":1<<k,
        "least_positive_n_gt_one":n0,
        "first_certified_horizon":chosen["k"] if chosen else None,
        "certificate":chosen,
        "all_attempts":attempts,
        "status":("INFINITE_CLASS_CERTIFIED_BY_VARIABLE_HORIZON" if chosen
                  else "HOLD_NO_VARIABLE_HORIZON_CERTIFICATE_WITHIN_K"),
        "global_collatz_proven":False,
    }


def _check_lifted_card(k,r,entry):
    """Actually verify a card lifts from modulus 2**j to modulus 2**k."""
    _check_level(k)
    if entry["residue"]!=r or entry["parent_modulus"]!=1<<k:
        raise HOLD("Variable descent certificate cannot be transported")
    if entry["least_positive_n_gt_one"]!=minimum_member_over_one(k,r):
        raise HOLD("Smallest parent-class member not preserved")
    proven=entry["first_certified_horizon"]
    if proven is None:
        if entry["certificate"] is not None:
            raise HOLD("Claimed missing horizon but supplied certificate")
        return True
    c=entry["certificate"]
    verify_certificate(c)
    if c["k"]!=proven or proven>k or c["residue"]!=r%(1<<proven):
        raise HOLD("Source proof does not match this parent residue")
    n0=minimum_member_over_one(k,r)
    a,b,d=(c["symbolic_affine"][x] for x in ("a","b","denominator"))
    if not (a<d and a*n0+b<d*n0):
        raise HOLD("Exact descent is not uniform over parent class")
    # Additional numerical crosscheck across disjoint infinite-family
    # members. Universal validity follows from affine proof + inequality,
    # *not* from these sample checks alone.
    for offset in (0,1,3,17):
        n=n0+offset*(1<<k)
        value=n
        for _ in range(proven):
            value=reference_T(value)
        if (value*d!=a*n+b or value>=n):
            raise HOLD("Independent trajectory contradicts universal card")
    return True


def compare_finite_horizon(k, *, detailed=False):
    """Try every r; compare against a fully fair exact classical baseline.

    Distinct baselines:
      FIXED: only ask whether T**k(n)<n universally on residue r.
      ADAPTIVE CLASSICAL: exact-first-descent j<=k using Fraction algebra.
      MOTIF ADAPTIVE: source-owned certificate() with earliest valid j.
    The strongest baseline and MOTIF tie; this is no super-classical claim.
    """
    _check_level(k)
    cache={}
    fixed_count=0
    adaptive_count=0
    strongest_count=0
    recorded=[]
    hold_residues=[]
    horizon_histogram={}
    for r in range(1<<k):
        card=_first_card(k,r,cache=cache)
        _check_lifted_card(k,r,card)
        n0=minimum_member_over_one(k,r)
        c=cache[(k,r)]
        a,b,d=(c["symbolic_affine"][x] for x in ("a","b","denominator"))
        fixed=(a<d and a*n0+b<d*n0)
        fixed_count += int(fixed)
        adaptive=card["first_certified_horizon"] is not None
        adaptive_count += int(adaptive)
        independent=classical_first_descent(k,r)
        strongest_count += int(independent is not None)
        if card["first_certified_horizon"] != independent:
            raise HOLD("MOTIF ranking proposal disagrees with fair classical solver")
        if fixed and not adaptive:
            raise HOLD("Adaptive solver missed a valid fixed-horizon certificate")
        if adaptive:
            horizon_histogram[independent]=horizon_histogram.get(independent,0)+1
        else:
            hold_residues.append(r)
        if detailed:
            recorded.append(card)
    # A known obstruction to every *bounded* k:
    if (1<<k)-1 not in hold_residues:
        raise HOLD("All-odd boundary class must remain explicitly unresolved")
    stats={
        "k":k,"modulus":1<<k,
        "fixed_horizon_strict_descent_classes":fixed_count,
        "adaptive_variable_time_certified_infinite_classes":adaptive_count,
        "classical_independent_adaptive_certified_classes":strongest_count,
        "additional_class_distinctions_over_fixed":adaptive_count-fixed_count,
        "honest_uncertified_classes":len(hold_residues),
        "all_odd_residue_is_uncertified":True,
        "horizons_certified_histogram":{str(j):horizon_histogram[j]
                                         for j in sorted(horizon_histogram)},
        "available_answer_not_global":True,
        "unresolved_residues":hold_residues if detailed else (
            hold_residues[:16]
        ),
        "all_residue_classes_accounted_for":True,
        "same_information_strong_classical_tie":adaptive_count==strongest_count,
        "complete_research_cards":recorded if detailed else None,
    }
    return stats


def weighted_potential_value(n,weights,offsets):
    if type(n) is not int or n<1:
        raise HOLD("Positive integer only")
    if (type(weights) is not list or type(offsets) is not list
        or len(weights)!=len(offsets)):
        raise HOLD("Bad finite-state candidate ranking definition")
    m=len(weights)
    if m not in (2,4,8,16):
        raise HOLD("Only tested finite residue ranking moduli")
    if any(type(w) is not int or not 1<=w<=64 for w in weights):
        raise HOLD("Positive bounded integer coefficients required")
    if any(type(b) is not int or not -1000<=b<=1000 for b in offsets):
        raise HOLD("Integer bounded offsets required")
    return weights[n%m]*n+offsets[n%m]


def refute_everywhere_one_step_linear_potential(weights,offsets):
    """Constructively refute n->w_(n mod m)*n+b_(n mod m) decreasing EVERY T step.

    A GENERAL mathematical proof for ANY finite positive weights and finite
    bounded offsets follows from the all-odd diagonal: let w_min>0, w_max,
    B=max|b|. Choose k with w_min*3**k > w_max*2**k. Choose t sufficiently
    large. For n=2**k*t-1 and T**k(n)=3**k*t-1,
    P(T**k(n)) >= w_min*(3**k*t-1)-B >
       w_max*(2**k*t-1)+B >= P(n).
    Telescoping contradicts P strictly decreasing on every step.
    This cannot refute variable-horizon / non-linear ranking functions.
    """
    weighted_potential_value(2,weights,offsets)
    low,high=min(weights),max(weights)
    B=max(abs(x) for x in offsets)
    k=1
    while low*(3**k) <= high*(2**k):
        k+=1
        if k>70:
            raise HOLD("Rank-obstruction witness exceeded declared search budget")
    delta=low*(3**k)-high*(2**k)
    required=low-high+2*B
    t=max(2,required//delta + 1)
    n=(1<<k)*t-1
    endpoint=(3**k)*t-1
    lower=low*endpoint-B
    upper=high*n+B
    if lower<=upper:
        raise HOLD("Constructive general rank obstruction did not separate")
    before=weighted_potential_value(n,weights,offsets)
    after=weighted_potential_value(endpoint,weights,offsets)
    if after<=before:
        raise HOLD("Actual potential values did not contradict monotonicity")
    value=n
    steps=[]
    first_failure=None
    for j in range(k):
        nxt=reference_T(value)
        f_before=weighted_potential_value(value,weights,offsets)
        f_after=weighted_potential_value(nxt,weights,offsets)
        record={"step":j+1,"start":value,"end":nxt,
                "potential_before":f_before,"potential_after":f_after,
                "strictly_decreased":f_after<f_before}
        steps.append(record)
        if first_failure is None and not record["strictly_decreased"]:
            first_failure=record
        value=nxt
    if value!=endpoint or first_failure is None:
        raise HOLD("No concrete counterexample to one-step ranking guarantee")
    return {
        "status":"REFUTED_ALL_STEP_MONOTONE_FINITE_RESIDUE_LINEAR_POTENTIAL",
        "candidate_weights":list(weights),"candidate_offsets":list(offsets),
        "candidate_modulus":len(weights),
        "all_odd_diagonal_k":k,"n":n,
        "end_after_k_steps":endpoint,
        "rigorous_lower_bound_at_end":lower,
        "rigorous_upper_bound_at_start":upper,
        "actual_potential_start":before,
        "actual_potential_end":after,
        "first_non_decreasing_step":first_failure,
        "full_source_trajectory":steps,
        "general_no_go_statement":
            "No positive finite-residue linear potential w_r*n+b_r "
            "with finite bounded weights and offsets can strictly "
            "decrease on EVERY accelerated Collatz step for every n>1.",
        "general_proof_uses_only_positive_min_max_weights_and_finite_offset_bound":True,
        "refutes_global_collatz_conjecture":False,
        "does_not_exclude_variable_time_or_non_linear_potentials":True,
        "historically_novel_math_claimed":False,
    }


def verify_weighted_obstruction(record):
    if type(record) is not dict or record.get("status")!=(
        "REFUTED_ALL_STEP_MONOTONE_FINITE_RESIDUE_LINEAR_POTENTIAL"
    ):
        raise HOLD("Unrecognized rank candidate evidence")
    reconstructed=refute_everywhere_one_step_linear_potential(
        record["candidate_weights"],record["candidate_offsets"])
    if reconstructed!=record:
        raise HOLD("Modified weighted-ranking counterexample or generic proof")
    return True


def _unresolved_probes(k,holds,*,max_probes=5):
    owner=FiniteSourceOwner()
    example=[]
    for r in holds[:max_probes]:
        n=minimum_member_over_one(k,r)
        rec=owner.ask(n,1200)
        owner.recheck(rec)
        below=next((i for i,x in enumerate(rec["trace"]) if i>0 and x<n),None)
        example.append({
            "class_residue":r,"original_n":n,
            "observed_first_descent_step_for_this_one_integer":below,
            "source_observation":rec,
            "proves_entire_infinite_class":False,
            "status":"FINITE_REPRESENTATIVE_NOT_UNIVERSAL_EVIDENCE",
        })
    return example


def investigate(*,k=9):
    if type(k) is not int or not 3<=k<=MAX_K:
        raise HOLD("Out of budget research horizon")
    baseline_fixed=compare_finite_horizon(k,detailed=True)
    if not baseline_fixed["same_information_strong_classical_tie"]:
        raise HOLD("No fair exact comparison")
    all_odd=fixed_horizon_diagonal_obstruction(k)
    weighted_candidates=[
        ([1,1],[0,0]),([1,2],[0,0]),([2,1],[1,-1]),
        ([2,1,3,2],[2,-1,3,-5]),
        ([6,1,2,7,4,8,1,9],[10,-10,1,-7,2,8,0,-4]),
    ]
    weighted=[refute_everywhere_one_step_linear_potential(w,b)
              for w,b in weighted_candidates]
    for card in weighted:
        verify_weighted_obstruction(card)
    holds=baseline_fixed["unresolved_residues"]
    if not holds:
        raise HOLD("Falsely advertised total stopping-time solution")
    observations=_unresolved_probes(k,holds)
    # Compare depth-by-depth, allowing user to see both advantages and cost.
    summaries=[compare_finite_horizon(j,detailed=False)
               for j in range(1,k+1)]
    result={
        "schema":SCHEMA,
        "open_question":"Does every positive integer reach 1 under Collatz?",
        "global_status":"OPEN_HOLD_NO_UNIVERSAL_PROOF",
        "known_prior_sources":KNOWN_REFERENCES,
        "inherited_negative_fixed_k_strategy":all_odd,
        "newly_falsified_candidate_ranking_family":
            "FINITE_MODULAR_POSITIVE_AFFINE_POTENTIAL_STRICTLY_DECREASING_EVERY_STEP",
        "general_rank_no_go_evidence":weighted,
        "new_research_method":"ADAPTIVE_RESIDUE_CLASS_FIRST_DESCENT_CERTIFICATE",
        "new_method_formal_specification":
            "For n>1, choose the earliest j<=k whose exact all-n residue "
            "affine identity proves T**j(n)<n. Every designated infinite "
            "residue class has its own fixed j. Uncovered classes are HOLD.",
        "proof_of_global_equivalence":
            "All n>1 eventually reach 1 iff all n>1 have some iterate "
            "strictly below n: forward implication chooses iterate=1; "
            "reverse implication is strong induction on n.",
        "equivalence_known_classical_not_new":True,
        "summary_by_maximum_depth":summaries,
        "main_level":baseline_fixed,
        "finite_observations_on_uncovered_classes":observations,
        "next_discriminating_question":
            "Can a new, verifiably well-founded nonlinear or unbounded-memory "
            "ranking system certify variable-time descent on the remaining "
            "2-adic residue frontier WITHOUT assuming random parity?",
        "methodology_discovered_historically_novel":False,
        "same_information_classical_solver_tied":True,
        "unresolved":list(UNRESOLVED),
        "automatic_admission":False,
        "installed":False,
        "external_authority":"NONE",
    }
    result["integrity_digest"]=digest(result)
    return result


def verify_packet(packet):
    if type(packet) is not dict or packet.get("schema")!=SCHEMA:
        raise HOLD("Unknown variable-horizon evidence packet")
    if (packet.get("integrity_digest") != digest({
        k:v for k,v in packet.items() if k!="integrity_digest"
    })):
        raise HOLD("Evidence checksum incorrect")
    actual=investigate(k=packet["main_level"]["k"])
    if packet!=actual:
        raise HOLD("Reconstructed source-owned rank and question evidence differ")
    return True


def reenter(packet):
    verify_packet(packet)
    return {
        "status":"VARIABLE_HORIZON_PARTIAL_CERTIFICATES_REVERIFIED",
        "new_discovery_questions":0,
        "proofs_and_finite_source_observations_fully_replayed":True,
        "collatz_globally_solved":False,
        "research_packet_integrity_digest":packet["integrity_digest"],
    }


if __name__=="__main__":
    import argparse,json
    parser=argparse.ArgumentParser()
    parser.add_argument("--k",type=int,default=9)
    args=parser.parse_args()
    print(json.dumps(investigate(k=args.k),sort_keys=True,indent=2))
