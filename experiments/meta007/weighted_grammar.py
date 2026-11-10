"""META-007 — synthesize and EXACTLY CERTIFY a better inverse-branch grammar.

This changes the *measurement* of branch quality from the previous
worst-single-edge depth bound to a variable-cost language-counting
recurrence. The candidate alphabet size K and a rational exponent p/1000
are chosen by an executable constrained search, not hand-picked.

For odd y>=5, y=2 mod 3, generalized branch B_t(y) uses
  e=e0(y mod 9)+3t, 0<=t<K,
  x=(2**(2e+1)*y-1)//3.
This is a real integer, x=2 mod 3, and T(x)=2**(2e)*y.
Every branch has a unique inverse description, and
  x < 2**(7+6t)*y.
For exact-refined integer costs w_t=6+6t and words of cost <=L:
  F(L)=1+sum_t F(L-w_t), F(L<0)=0.
If sum_t 2**(-alpha*w_t) >=1, induction gives
  F(L)>=2**(alpha*(L-max_t(w_t))).
Thus |S∩[1,X]|=Omega(X**alpha).

All comparisons to rational powers of two are certified by PURE INTEGER
power inequalities, with no floating-point numerical proof assumptions.
Unbounded mathematical induction is human-reviewable, not Lean-certified.
The Collatz conjecture remains open; this is classical-style inverse math
and a bounded engineer-designed synthesis grammar.
"""
from __future__ import annotations

from copy import deepcopy
from decimal import Decimal, localcontext
from functools import lru_cache
from hashlib import sha256
from itertools import product
from math import log
import json
import sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"meta001"))
sys.path.insert(0,str(HERE.parent/"meta005"))
sys.path.insert(0,str(HERE.parent/"meta006"))
from collatz_frontier import T,reference_T,HOLD,canonical,digest
from infinite_inverse_rank import oracle_exact_rank
from branching_inverse import (
    BASE_EXPONENT_BY_MOD9, SEED, SEED_RANK,
    decode as previous_binary_decoder,
    rank_member as previous_binary_rank_member,
)

SCHEMA="motif.meta007.weighted-branch-exact-growth.v1"
Q=1000
FLOOR_SCALE=10**12
ALPHABET_MAX=12
ALPHABET_MIN=2
NUMERATOR_MIN=80
NUMERATOR_MAX=180
MAX_MATERIALIZED_DEPTH=3
CERTIFIED_SOURCE="EXACT_ORDINARY_INTEGER_COLLATZ"
PUBLIC_HISTORICAL_REFERENCE={
    "title":"Krasikov & Lagarias, Bounds for the 3x+1 problem using difference inequalities",
    "year":2003,
    "journal":"Acta Arithmetica 109(3):237-258",
    "doi":"10.4064/aa109-3-4",
    "published_bound":"For sufficiently large X, the entire convergent predecessor set has a lower bound of order X**0.84.",
    "stronger_than_our_restricted_family":True,
    "is_independent_historical_mathematics":True,
}
LIMITS=[
    "The original Collatz problem over all positive integers remains OPEN.",
    "The encoded tree is a proper positive-integer subset, not the whole convergence basin.",
    "The alphabet and cost grammar are human-authored; only finite parameters are selected automatically.",
    "All mathematical claims are known-style inverse-tree and weighted-word counting mathematics.",
    "The optimized rational exponent is optimal ONLY over K<=12 and the grid p/1000, 80<=p<=160, using declared uniform branch-cost weights.",
    "Float or Decimal approximations choose/display candidates but never certify their mathematical inequalities.",
    "No positive density, stronger historical exponent, unrestricted operator invention or novel Collatz theorem is claimed.",
    "Symbolic induction is human-reviewable; no independent Lean verification or scholarly adjudication.",
    "A rehashed record is not source identity; source math is regenerated at re-entry.",
]


def _choose_int(value,min_val,max_val,name):
    if type(value) is not int or not min_val<=value<=max_val:
        raise HOLD(f"{name} outside frozen typed grammar")
    return value


def branch_weight(t):
    """DISCOVER a tighter integer cost by proving the exact 1/3 factor.

    The largest possible exponent e for a given branch symbol is
    e_max=3+3*t. Source branch satisfies
      B_t(y) < (2**(2*e_max+1)/3)*y.
    Select the SMALLEST nonnegative integer w such that
      3*2**w > 2**(2*e_max+1).
    This is an executed conservative-bound tightening step, not a
    hardcoded answer or an unreliable floating log comparison.
    It discovers w_t=6+6*t rather than the original 7+6*t.
    """
    _choose_int(t,0,ALPHABET_MAX-1,"symbol")
    emax=3+3*t
    numerator=1<<(2*emax+1)
    w=0
    while 3*(1<<w)<=numerator:
        w+=1
    if w<1 or 3*(1<<(w-1))>numerator or 3*(1<<w)<=numerator:
        raise HOLD("Cannot certify minimally tightened exact cost")
    return w

def cost_refinement_receipt():
    checks=[]
    for t in range(ALPHABET_MAX):
        old=7+6*t
        new=branch_weight(t)
        source=1<<(7+6*t)
        if new>=old or 3*(1<<new)<=source or 3*(1<<(new-1))>source:
            raise HOLD("Exact source-bound self-tightening did not improve")
        checks.append({
            "symbol":t,"old_overconservative_weight":old,
            "exact_derived_minimal_integer_weight":new,
            "mathematical_source_numerator":source,
            "certificate_3_times_2_power_w_exceeds_numerator":True,
            "certificate_smaller_weight_fails":True,
        })
    return {
        "status":"EXACT_SYMBOLIC_COST_REFINEMENT_SUCCEEDED",
        "reason":"The source expression divided by 3 before quantization; "
                 "the original cost bound ignored that exact divisor.",
        "all_source_branch_costs":checks,
        "old_cost_formula":"w_old(t)=7+6*t",
        "refined_cost_formula":"w_refined(t)=6+6*t",
        "general_method":"Minimize integer log2 growth upper bound by "
                         "exact bigint inequality 3*2**w>2**(7+6*t)",
        "source_owned_not_statistical_inference":True,
    }


def _e0(y):
    if type(y) is not int or y<5 or y%2!=1 or y%3!=2:
        raise HOLD("Only strictly positive odd residue-2-mod3 source nodes")
    e=BASE_EXPONENT_BY_MOD9.get(y%9)
    if e is None or not 1<=e<=3 or (pow(2,2*e+1,9)*y-1)%9!=6:
        raise HOLD("Original modular branch condition false")
    return e


def generalized_branch(y,t,alphabet_size):
    """A real new inverse word operation; never guess Collatz membership."""
    _choose_int(alphabet_size,ALPHABET_MIN,ALPHABET_MAX,"alphabet")
    _choose_int(t,0,alphabet_size-1,"branch symbol")
    e=_e0(y)+3*t
    numerator=(1<<(2*e+1))*y-1
    if numerator%3:
        raise HOLD("Nonintegral inverse branch")
    x=numerator//3
    if not (x>y>=5 and x%2==1 and x%3==2):
        raise HOLD("Source branch exited positive discrete source domain")
    nxt=(1<<(2*e))*y
    if T(x)!=nxt or reference_T(x)!=nxt:
        raise HOLD("Independent exact reference rejects inverse source")
    weight=branch_weight(t)
    if not (3*(1<<weight) > (1<<(2*e+1)) and x<(1<<weight)*y):
        raise HOLD("Variable-cost source growth bound invalid")
    return {
        "parent":y,"child":x,"t":t,"e":e,
        "growth_cost_bits":weight,
        "source_forward_first_step":nxt,
        "following_even_steps":2*e,
        "accelerated_rank_increment":2*e+1,
        "mod9_y":y%9,
        "valid_positive_integer_successor":True,
        "same_residue_mod3_for_infinite_branching":True,
        "coarse_upper_growth_certified":True,
    }


def encode_word(word,alphabet_size):
    if type(word) not in (list,tuple) or len(word)>MAX_MATERIALIZED_DEPTH:
        raise HOLD("Finite materialization budget exceeded")
    _choose_int(alphabet_size,ALPHABET_MIN,ALPHABET_MAX,"alphabet")
    n=SEED
    rank=SEED_RANK
    cost=0
    source=[]
    for t in word:
        edge=generalized_branch(n,t,alphabet_size)
        n=edge["child"]
        rank+=edge["accelerated_rank_increment"]
        cost+=edge["growth_cost_bits"]
        source.append(edge)
    if n >= SEED*(1<<cost) and word:
        raise HOLD("Encoded source contradicts certified weighted cost")
    return {
        "schema":"motif.meta007.verified-branch-word.v1",
        "word":list(word),"alphabet_size":alphabet_size,
        "odd_positive_integer":n,
        "forward_rank":rank,
        "weighted_cost_bits":cost,
        "complete_macro_edge_source":source,
        "strict_positive_integer_membership":True,
        "all_successors_in_ranked_domain":True,
        "not_the_whole_positive_integer_domain":True,
    }


def decode_word(n,alphabet_size,*,max_depth=MAX_MATERIALIZED_DEPTH):
    """Unique inverse of generated branch code, no future orbit-to-1 oracle."""
    _choose_int(alphabet_size,ALPHABET_MIN,ALPHABET_MAX,"alphabet")
    if type(max_depth) is not int or not 0<=max_depth<=MAX_MATERIALIZED_DEPTH:
        raise HOLD("Decoder budget exceeded")
    if type(n) is not int or n<5 or n%2==0 or n%3!=2:
        return {"status":"HOLD_UNSUPPORTED_INTEGER","word":None}
    x=n
    reversed_word=[]
    while x!=SEED:
        if len(reversed_word)>=max_depth:
            return {"status":"HOLD_OUTSIDE_DECODER_DEPTH","word":None}
        nxt=reference_T(x)
        v=0
        while nxt%2==0:
            nxt//=2
            v+=1
        if v<2 or v%2 or nxt>=x or nxt<SEED or nxt%2!=1 or nxt%3!=2:
            return {"status":"HOLD_OUTSIDE_INVERSE_GRAMMAR","word":None}
        exponent=v//2
        base=_e0(nxt)
        delta=exponent-base
        if delta<0 or delta%3:
            return {"status":"HOLD_OUTSIDE_INVERSE_GRAMMAR","word":None}
        t=delta//3
        if t>=alphabet_size:
            return {"status":"HOLD_OUTSIDE_SELECTED_ALPHABET","word":None}
        if generalized_branch(nxt,t,alphabet_size)["child"]!=x:
            raise HOLD("Decoding inverse branch contradicts source math")
        reversed_word.append(t)
        x=nxt
    word=list(reversed(reversed_word))
    back=encode_word(word,alphabet_size)
    if back["odd_positive_integer"]!=n:
        raise HOLD("Decoded source word does not reconstruct original integer")
    return {
        "status":"EXACT_SOURCE_WORD_RECONSTRUCTED",
        "word":word,"rank":back["forward_rank"],
        "cost":back["weighted_cost_bits"],
        "real_positive_integer_only":True,
    }


def _pow_rational_bound(p,w):
    """Return certified integer floor(Q*2**(-p*w/1000)).

    For z=floor(Q*2**(-p*w/1000)), the entire mathematical
    certificate is precisely:
       z**1000 * 2**(p*w) <= Q**1000
       (z+1)**1000 * 2**(p*w) > Q**1000.
    Uses approximations only to initialize an integer candidate,
    then EXACT integer inequalities to finalize and verify.
    """
    _choose_int(p,NUMERATOR_MIN,NUMERATOR_MAX,"rational exponent numerator")
    if type(w) is not int or w<branch_weight(0) or w>branch_weight(ALPHABET_MAX-1):
        raise HOLD("Weight outside tested inverse grammar")
    target=FLOOR_SCALE**Q
    tw=1<<(p*w)
    z=max(0,int(FLOOR_SCALE*(2.0**(-p*w/Q)))-2)
    while (z+1)**Q*tw<=target:
        z+=1
    while z**Q*tw>target:
        z-=1
    if z<0 or not (z**Q*tw<=target<(z+1)**Q*tw):
        raise HOLD("Cannot certify dyadic rational power interval")
    return z


@lru_cache(maxsize=None)
def exact_growth_score(K,p):
    """Mathematically rigorous lower AND upper bound for weighted Kraft sum."""
    _choose_int(K,ALPHABET_MIN,ALPHABET_MAX,"alphabet size")
    _choose_int(p,NUMERATOR_MIN,NUMERATOR_MAX,"numerator")
    floors=[_pow_rational_bound(p,branch_weight(t)) for t in range(K)]
    low=sum(floors)
    high=low+K
    if low>=FLOOR_SCALE:
        verdict="CERTIFIED_SUPERCRITICAL"
    elif high<FLOOR_SCALE:
        verdict="CERTIFIED_SUBCRITICAL"
    else:
        raise HOLD("Tight exponent cannot be certified at chosen exact precision")
    return {
        "alphabet_size":K,"rational_exponent":{"p":p,"q":Q},
        "cost_weights_bits":[branch_weight(t) for t in range(K)],
        "exact_scaled_interval_scale":FLOOR_SCALE,
        "each_term_exact_lower_numerators":floors,
        "sum_lower_numerator":low,
        "sum_upper_numerator_exclusive":high,
        "verdict":verdict,
        "all_integer_power_comparisons_verified":True,
    }


def optimize_grammar():
    """Source-owned finite synthesis, not hand-picked 11-branch grammar.

    Binary search certified rational growth grid p/1000 for every K
    from 2 to 12. Exact monotonicity in alpha makes search complete.
    """
    searches=[]
    for K in range(ALPHABET_MIN,ALPHABET_MAX+1):
        lo=NUMERATOR_MIN
        hi=NUMERATOR_MAX
        tested=[]
        optimum=None
        while lo<=hi:
            p=(lo+hi)//2
            score=exact_growth_score(K,p)
            tested.append({
                "p":p,"verdict":score["verdict"],
                "dyadic_lower_sum":score["sum_lower_numerator"],
            })
            if score["verdict"]=="CERTIFIED_SUPERCRITICAL":
                optimum=p
                lo=p+1
            else:
                hi=p-1
        if optimum is None:
            raise HOLD("No legitimate exponent for candidate grammar")
        success=exact_growth_score(K,optimum)
        next_score=(exact_growth_score(K,optimum+1)
                    if optimum<NUMERATOR_MAX else None)
        if (next_score and next_score["verdict"]!="CERTIFIED_SUBCRITICAL"):
            raise HOLD("Unproved optimality on finite exponent grid")
        searches.append({
            "K":K,"complete_binary_search_decisions":tested,
            "best_certified_p":optimum,
            "success":success,
            "first_excluded_exponent":next_score,
            "verified_finite_search_range":[NUMERATOR_MIN,NUMERATOR_MAX],
        })
    selected=min(
        (x for x in searches),
        key=lambda x:(-x["best_certified_p"],x["K"])
    )
    if selected["best_certified_p"]!=166 or selected["K"]!=8:
        raise HOLD("Rational alphabet optimization changed on source replay")
    return {
        "schema":"motif.meta007.exact-grammar-optimizer.v1",
        "source_candidate_alphabet_sizes":[ALPHABET_MIN,ALPHABET_MAX],
        "exponent_grid":{"p_min":NUMERATOR_MIN,"p_max":NUMERATOR_MAX,"q":Q},
        "all_alphabet_trials":searches,
        "winning_alphabet_size":selected["K"],
        "winning_rational_growth_exponent":selected["best_certified_p"],
        "winning_Kraft_certificate":selected["success"],
        "optimization_tie_rule":"maximize proved p/q; then minimize K",
        "optimal_ONLY_within_predeclared_grammar_and_rational_grid":True,
        "no_general_math_novelty_claimed":True,
    }


def independent_classical_approximate_score(K,p):
    """Independent high precision classical geometric-sum baseline."""
    _choose_int(K,ALPHABET_MIN,ALPHABET_MAX,"classic K")
    _choose_int(p,NUMERATOR_MIN,NUMERATOR_MAX,"classic p")
    with localcontext() as ctx:
        ctx.prec=75
        alpha=Decimal(p)/Decimal(Q)
        two=Decimal(2)
        base=two**(-Decimal(branch_weight(0))*alpha)
        ratio=two**(-Decimal(6)*alpha)
        geometric=base*(Decimal(1)-ratio**K)/(Decimal(1)-ratio)
        return geometric>1,format(geometric,".20f")


def count_weighted_words(K,budget):
    """Count distinct binary-like inverse WORDS by cost, no graph simulation.

    C(L)=1+Σ C(L-w_t) for L>=0 and C(negative)=0;
    includes the empty word of cost zero. Every distinct word has
    unique exact positive integer encoding, proved by v2 decoding.
    """
    _choose_int(K,ALPHABET_MIN,ALPHABET_MAX,"grammar K")
    if type(budget) is not int or not 0<=budget<=200:
        raise HOLD("Bounded finite generating-function witness only")
    c=[]
    costs=[branch_weight(t) for t in range(K)]
    for L in range(budget+1):
        c.append(1+sum(c[L-w] for w in costs if w<=L))
    return c


def brute_force_count(K,budget):
    """Independent complete depth-first combinatorial enumeration, tiny L."""
    _choose_int(K,ALPHABET_MIN,ALPHABET_MAX,"grammar K")
    if type(budget) is not int or not 0<=budget<=32:
        raise HOLD("Naive classical enumeration must remain small")
    weights=[branch_weight(t) for t in range(K)]
    stack=[((),0)]
    visited=0
    while stack:
        word,total=stack.pop()
        if total>budget:
            raise HOLD("Classical word budget changed")
        visited+=1
        for t,w in enumerate(weights):
            if total+w<=budget:
                stack.append((word+(t,),total+w))
    return visited


def lower_growth_certificate(opt,*,budget=120):
    """Prove a generic Ω(X**(p/q)) lower bound with an exact inequality.

    For L<Wmax, C(L)>=1>=2**(alpha*(L-Wmax)).
    For L>=Wmax, induction on L and the EXACT verified
    Σ2**(-alpha*w)>1 yields C(L)>=2**(alpha*(L-Wmax)).
    Thus for X>=5*2**Wmax and L=floor(log2(X/5)),
      |S∩[1,X]| >= C(L) >= 2**(alpha*(L-Wmax))
                    > 2**(-alpha*(Wmax+1))*(X/5)**alpha.
    """
    K=opt["winning_alphabet_size"]
    p=opt["winning_rational_growth_exponent"]
    score=opt["winning_Kraft_certificate"]
    if (score!=exact_growth_score(K,p)
        or score["verdict"]!="CERTIFIED_SUPERCRITICAL"):
        raise HOLD("Selected exponent has no exact Kraft certificate")
    W=branch_weight(K-1)
    counts=count_weighted_words(K,budget)
    checkpoints=[]
    for L in (0,7,12,20,32,W,80,100,120):
        if L>budget:
            continue
        n=counts[L]
        # integer comparison n^q >= 2^(p*(L-W)) for L>=W
        # / equivalently n^q*2^(p*W) >= 2^(p*L).
        if n**Q*(1<<(p*W)) < 1<<(p*L):
            raise HOLD("Finite word-count counterexample to symbolic induction")
        checkpoints.append({
            "weighted_budget_L":L,
            "distinct_executable_words_from_recurrence":n,
            "integer_power_lower_bound_proved":True,
        })
    return {
        "schema":"motif.meta007.exact-weighted-words-growth-proof.v1",
        "weighted_cost_expression":"w(t)=6+6*t discovered by exact /3 source-bound refinement",
        "unique_positive_integer_code_injection":"recover t from v2(T(child))/2 and parent mod9",
        "selected_K":K,"rational_alpha_p":p,"rational_alpha_q":Q,
        "maximum_symbol_weight_W":W,
        "verified_strict_sum_lower_than_one_claim":False,
        "exact_Kraft_sum_strictly_greater_than_one":True,
        "exact_Kraft_sum_integer_certificate":score,
        "recurrence":"C(L)=1+sum(C(L-w(t)) for t if w(t)<=L), C(L<0)=0",
        "base_case":"For 0<=L<W, C(L)>=1>=2**(alpha*(L-W))",
        "induction":"For L>=W, every L-w(t)>=0; the recurrence and "
                    "source-certified sum(2**(-alpha*w(t)))>1 imply "
                    "C(L)>=2**(alpha*(L-W))",
        "mapping_to_integer_magnitude":"Each word of weighted cost<=L "
            "encodes distinct positive n<5*2**L",
        "natural_integer_domain_growth":"|S∩[1,X]|=Omega(X**(p/q)) "
            "with p/q=166/1000, X>=5*2**W",
        "constant_lower_bound":"C(L)>=2**(alpha*(L-W)); L=floor(log2(X/5))",
        "complete_symbolic_induction_human_review_required":True,
        "formal_proof_assistant_verification":"NOT_PERFORMED",
        "checkpoints":checkpoints,
        "new_established_historic_math_result":False,
        "global_Collatz_conjecture_proved":False,
        "positive_natural_density_proved":False,
    }


def enumerate_finite_source(opt,depth=MAX_MATERIALIZED_DEPTH):
    """Actual generated node execution: compare old language vs new.

    Use the ORIGINAL META006 binary grammar and the independent direct
    positive-Collatz oracle, not model-generated expected answers.
    """
    _choose_int(depth,0,MAX_MATERIALIZED_DEPTH,"proof-word depth")
    K=opt["winning_alphabet_size"]
    all_nodes=set()
    count_by_depth=[]
    new_from_old=0
    first_examples=[]
    recorded=[]
    for d in range(depth+1):
        seen=set()
        words=list(product(range(K),repeat=d))
        for word in words:
            card=encode_word(word,K)
            n=card["odd_positive_integer"]
            if n in all_nodes or n in seen:
                raise HOLD("Inverse code collision")
            seen.add(n)
            reconstructed=decode_word(n,K)
            if (reconstructed["word"]!=list(word)
                or reconstructed["rank"]!=card["forward_rank"]):
                raise HOLD("Generated word cannot be decoded")
            baseline=previous_binary_decoder(n,max_depth=12)
            in_prior=baseline["status"]=="CERTIFIED_BINARY_INVERSE_BRANCH"
            expected_old=all(t in (0,1) for t in word)
            if in_prior!=expected_old:
                raise HOLD("Reference META006 inverse grammar disagrees with comparison")
            if in_prior:
                if baseline["rank"]!=card["forward_rank"]:
                    raise HOLD("Prior source rank differs")
            else:
                new_from_old+=1
                if len(first_examples)<12:
                    first_examples.append({"word":list(word),"n":n,
                        "strict_rank":card["forward_rank"],
                        "prior_verdict":baseline["status"]})
            actual=oracle_exact_rank(n,max_steps=1000)
            if actual!=card["forward_rank"]:
                raise HOLD("Independent Collatz trajectory defeats rank")
            # Explicitly verify each step of the macro transition.
            if word:
                edge=card["complete_macro_edge_source"][-1]
                x=edge["child"]
                y=edge["parent"]
                val=x
                for _ in range(edge["accelerated_rank_increment"]):
                    val=reference_T(val)
                if val!=y:
                    raise HOLD("Real macro transition not closed")
            if d<=1:
                recorded.append({
                    "word":list(word),"node":n,
                    "exact_rank":actual,
                    "new_to_previous_grammar":not in_prior,
                    "complete_macro_edge_source":card[
                        "complete_macro_edge_source"],
                })
        all_nodes.update(seen)
        count_by_depth.append({"depth":d,"exact_new_nodes":len(seen)})
    if len(all_nodes)!=sum(K**d for d in range(depth+1)):
        raise HOLD("Bounded source graph not exact full K-way tree")
    return {
        "schema":"motif.meta007.finite-source-cross-language-proof.v1",
        "selected_grammar_K":K,
        "max_depth":depth,
        "source_checked_nodes":len(all_nodes),
        "full_K_way_tree_count":sum(K**d for d in range(depth+1)),
        "new_nodes_outside_original_META006_binary_grammar":new_from_old,
        "source_verified_finite_growth_by_depth":count_by_depth,
        "first_new_integer_instances":first_examples,
        "complete_seed_and_first_level_records":recorded,
        "independent_forward_source_rank_checked_for_every_node":True,
        "original_source_grammar_strictly_less_expressive":True,
        "real_graph_and_math_semantics_not_only_string_code":True,
        "no_claim_of_unrestricted_external_source":True,
    }


def investigate():
    refined_costs=cost_refinement_receipt()
    optimized=optimize_grammar()
    strongest=optimized["winning_Kraft_certificate"]
    K=optimized["winning_alphabet_size"]
    p=optimized["winning_rational_growth_exponent"]
    classical=[]
    for row in optimized["all_alphabet_trials"]:
        k=row["K"];champ=row["best_certified_p"]
        expected,amount=independent_classical_approximate_score(k,champ)
        if not expected:
            raise HOLD("Classical analytical geometrical sum contradicts exact proof")
        if champ<NUMERATOR_MAX:
            beyond,other=independent_classical_approximate_score(k,champ+1)
            if beyond:
                raise HOLD("Classical analysis contradicts bounded grid optimality")
        classical.append({
            "K":k,"classical_max_certified_p":champ,
            "independent_decimal_geometric_sum":amount,
            "same_information_classical_grammar_tie":True,
        })
    growth=lower_growth_certificate(optimized)
    finite=enumerate_finite_source(optimized)
    if (K,p)!=(8,166):
        raise HOLD("Proof grammar unexpectedly changed")
    if (finite["source_checked_nodes"]!=585 or
        finite["new_nodes_outside_original_META006_binary_grammar"]!=570):
        raise HOLD("Source comparison unexpectedly changed")
    previous={"prior_grammar":2,"prior_worst_case_power_lower_alpha":
        round(log(2)/log(8192/3),10)}
    new_ratio=(p/Q)/previous["prior_worst_case_power_lower_alpha"]
    result={
        "schema":SCHEMA,
        "open_math_question":"Does every positive integer eventually reach 1 under Collatz?",
        "global_open_status":"COLLATZ_UNRESOLVED_NO_GENERAL_PROOF",
        "new_research_question":"Which source-verifiable inverse-branch alphabet "
            "maximizes a RIGOROUS growth exponent when unequal branch "
            "costs and exact source decoding are counted?",
        "method_breakthrough":"WEIGHTED_LANGUAGE_GENERATING_FUNCTION_REPLACES_WORST_BRANCH_BOUND",
        "primitive_graph_operator_source":
            "META006 exact modulo-9 odd-inverse macro construction",
        "exact_self_critique_of_operator_costs":refined_costs,
        "grammar_optimizer":optimized,
        "weighted_combinatorial_growth_certificate":growth,
        "independent_exact_integer_source_crosscheck":finite,
        "independent_classical_geometric_baseline":classical,
        "comparison_against_META006":{
            **previous,
            "new_grammar_K":K,
            "new_exact_lower_bound_exponent":f"{p}/{Q}",
            "improvement_factor_over_prior_guaranteed_lower_exponent":
                round(new_ratio,6),
            "finite_new_nodes_not_available_in_META006":finite[
                "new_nodes_outside_original_META006_binary_grammar"],
            "does_not_beat_historical_Krasikov_Lagarias":True,
        },
        "historical_published_global_predecessor_bound":
            PUBLIC_HISTORICAL_REFERENCE,
        "next_unresolved_question":
            "Can a source-proven multitype state-transition grammar with "
            "residue-dependent exponents, and an exact spectral or "
            "difference-inequality certificate, improve on this simple "
            "uniform cost bound under a matched classical baseline?",
        "not_general_autonomous_axiom_invention":True,
        "not_historically_novel_mathematics":True,
        "not_a_Collatz_global_proof":True,
        "not_positive_density":True,
        "limitations":LIMITS,
        "automatic_admission":False,"installed":False,
        "external_authority":"NONE",
    }
    result["integrity_digest"]=digest(result)
    return result


def verify_packet(packet):
    if type(packet) is not dict or packet.get("schema")!=SCHEMA:
        raise HOLD("Unknown optimized inverse research packet")
    if packet.get("integrity_digest")!=digest({
        k:v for k,v in packet.items() if k!="integrity_digest"
    }):
        raise HOLD("Tampered optimized research checksum")
    if packet!=investigate():
        raise HOLD("Rehashed false optimality, rank, source, historical or global claim")
    return True


def reenter(packet):
    verify_packet(packet)
    return {
        "status":"EXACT_WEIGHTED_BRANCH_GRAMMAR_REPROVED",
        "new_investigative_source_questions":0,
        "all_mathematical_and_source_claims_recomputed":True,
        "global_collatz_conjecture_solved":False,
        "exact_proof_digest":packet["integrity_digest"],
    }


if __name__=="__main__":
    print(json.dumps(investigate(),indent=2,sort_keys=True))
