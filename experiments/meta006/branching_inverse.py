"""META-006: provably broader infinite positive Collatz rank domain.

Extend META-005's sparse *single unbroken odd-prefix* grammar with a
recursive, branching family of odd predecessors separated by EVEN blocks.

An exact finite-state rule chooses reverse-block exponent e using y modulo 9,
keeping every generated odd node y congruent to 2 mod 3 and therefore able to
branch again. Any finite binary string encodes a unique node.

The inverse branch identity + unique decoding provides:
  - positive integer membership, no 2-adic ghosts,
  - exact transition closure including the intermediate even states,
  - a well-founded rank known BEFORE tracing a future orbit,
  - a binary tree with an explicit polynomial cardinality lower bound,
    strictly stronger than META-005's polylogarithmic upper bound.

This is elementary classical inverse-tree mathematics with engineered
selection grammar, not historical theorem discovery or a Collatz proof.
"""
from __future__ import annotations

from collections import deque
from copy import deepcopy
from hashlib import sha256
from math import log
import json
import sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"meta001"))
sys.path.insert(0,str(HERE.parent/"meta005"))

from collatz_frontier import T,reference_T,HOLD,canonical,digest
from infinite_inverse_rank import recognize as old_family_recognize
from infinite_inverse_rank import sparse_family_upper_bound,oracle_exact_rank

SCHEMA="motif.meta006.branching-infinite-ranked-domain.v1"
SEED=5
SEED_RANK=4
# The modular state mapping is DERIVED from 2**(2e+1)*y == 7 (mod 9).
# In order to have x=(2**(2e+1)*y-1)/3 == 2 (mod 3).
BASE_EXPONENT_BY_MOD9={2:1,5:2,8:3}
BINARY_ALPHABET=(0,1)
MAX_OPERATIONAL_LEVEL=12
MAX_POWER_BITS=4096
COVERAGE_CAPS=(64,512,4096,16384)
OPEN_LIMITS=[
    "Constructed domain is a proper subset of positive integers, not all naturals.",
    "Polynomial-in-X LOWER growth for this family does not establish positive density.",
    "Candidate rule is human-authored modular inverse-tree arithmetic, not discovered from unrestricted language.",
    "Fair same-information classical inverse-tree search produces identical family.",
    "Algebraic induction is human-reviewable and bounded instances are independently executed; no Lean check.",
    "Unknown or nonmember states are explicitly held, not labelled nonconvergent.",
    "No remotely authenticated source owner, newly discovered historic theorem or solved Collatz.",
]


def e_base(y):
    """The unique minimal positive e such that B_e(y) == 2 mod 3."""
    if type(y) is not int or y<5 or y%2!=1 or y%3!=2:
        raise HOLD("Odd source y>=5, y mod3=2 required")
    e=BASE_EXPONENT_BY_MOD9.get(y%9)
    if e is None or not 1<=e<=3:
        raise HOLD("No well-typed three-adic modular branch state")
    if (pow(2,2*e+1,9)*y-1)%9!=6:
        raise HOLD("Formula for residue-preserving branch failed modulo 9")
    return e


def child(y,choice):
    """Synthesize new odd inverse graph node. Two options at each y.

    For e=e0(y)+3*choice,
        B_e(y) = (2**(2e+1)*y - 1) // 3.
    Its forward path is:
        B_e(y) -> 2**(2e)*y -> ... -> y.

    Since e>=1, B_e(y) > y. The parent is recoverable from
    T(B_e(y)) by v2, hence each binary path is unique.
    """
    if type(choice) is not int or choice not in BINARY_ALPHABET:
        raise HOLD("Only frozen binary experiment grammar")
    e=e_base(y)+3*choice
    if 2*e+1>MAX_POWER_BITS:
        raise HOLD("Inverse multiplication budget exceeded")
    numerator=(1<<(2*e+1))*y-1
    if numerator%3:
        raise HOLD("Odd inverse child is not an integer")
    x=numerator//3
    if x<=y or x%2==0 or x%3!=2:
        raise HOLD("Inverse child escaped positive branching domain")
    nxt=T(x)
    if nxt!=reference_T(x) or nxt!=(1<<(2*e))*y:
        raise HOLD("Generated inverse step not supported by forward oracle")
    if e_base(x) not in (1,2,3):
        raise HOLD("Child is not permitted to branch further")
    return {
        "parent":y, "choice":choice,
        "residue_y_mod9":y%9, "modular_exponent_e":e,
        "child":x,
        "forward_first_step":nxt,
        "following_even_halvings":2*e,
        "rank_increment":2*e+1,
        "arithmetic_identity":"T(B_e(y))=2**(2e)*y",
        "child_type":"ODD_POSITIVE_2_MOD_3",
        "all_forward_steps_remaining_in_ranked_domain":True,
    }


def encode(word):
    """A binary path code is a proof-carrying node address, not a number guess."""
    if type(word) not in (list,tuple) or len(word)>MAX_OPERATIONAL_LEVEL:
        raise HOLD("Bounded materialization path required")
    y=SEED
    rank=SEED_RANK
    receipts=[]
    for bit in word:
        step=child(y,bit)
        rank+=step["rank_increment"]
        y=step["child"]
        receipts.append(step)
    return {
        "schema":"motif.meta006.branch-code-witness.v1",
        "word":list(word), "odd_node":y,
        "strict_rank":rank,
        "source_seed":SEED,
        "inverse_macro_edges":receipts,
        "source_odd_nodes_proven":True,
        "explicit_positive_natural_integer":True,
        "entire_domain_admitted":False,
    }


def decode(n,*,max_depth=MAX_OPERATIONAL_LEVEL):
    """Independent inverse of the typed binary path grammar.

    If x is a generated odd child, T(x)=2**(2e)*y and y is odd.
    Recover e=v2(T(x))/2 and choice=(e-e0(y))/3.
    The required parent is STRICTLY smaller than x; this is a
    terminating graph decoding proof for every generated finite word.
    """
    if type(n) is not int or n<5 or n%2!=1 or n%3!=2:
        return {"status":"HOLD_NOT_AN_ADMITTED_ODD_NODE","n":n,"word":None}
    x=n
    bits=[]
    ranks=[]
    while x!=SEED:
        if len(bits)>=max_depth:
            return {"status":"HOLD_RECOGNIZER_DEPTH_BUDGET","n":n,"word":None}
        succ=reference_T(x)
        v=0
        while succ%2==0 and succ>0:
            v+=1
            succ//=2
        if not v or v%2 or succ>=x or succ<SEED or succ%2!=1 or succ%3!=2:
            return {"status":"HOLD_OUTSIDE_GENERATED_BRANCH_TREE",
                    "n":n,"word":None}
        e=v//2
        try:
            minimal=e_base(succ)
        except HOLD:
            return {"status":"HOLD_OUTSIDE_GENERATED_BRANCH_TREE",
                    "n":n,"word":None}
        delta=e-minimal
        if delta not in (0,3):
            return {"status":"HOLD_OUTSIDE_BINARY_BRANCH_GRAMMAR",
                    "n":n,"word":None}
        if child(succ,delta//3)["child"]!=x:
            raise HOLD("Reverse oracle disagrees with generated branch")
        bits.append(delta//3)
        ranks.append(2*e+1)
        x=succ
    word=list(reversed(bits))
    proof=encode(word)
    if proof["odd_node"]!=n or proof["strict_rank"]!=SEED_RANK+sum(ranks):
        raise HOLD("Independent decoder cannot reproduce rank")
    return {
        "status":"CERTIFIED_BINARY_INVERSE_BRANCH",
        "n":n,"word":word,
        "rank":proof["strict_rank"],
        "macro_depth":len(word),
        "decoded_without_tracing_to_terminal":True,
        "n_is_positive_integer":True,
    }


def rank_member(n,*,max_depth=MAX_OPERATIONAL_LEVEL):
    """Rank on the explicit closed domain: 1, powers-of-two, even lifts of tree."""
    if type(n) is not int or n<1:
        raise HOLD("A positive natural integer is required")
    if n==1:
        return {"status":"CERTIFIED_TERMINAL","n":n,"rank":0,
                "odd_source_word":None,"even_lift":0}
    h=0
    odd=n
    while odd%2==0:
        odd//=2
        h+=1
    if odd==1:
        return {"status":"CERTIFIED_POWER_OF_TWO","n":n,"rank":h,
                "odd_source_word":None,"even_lift":h}
    source=decode(odd,max_depth=max_depth)
    if source["status"]!="CERTIFIED_BINARY_INVERSE_BRANCH":
        return {"status":"HOLD_NOT_IN_EXPLICIT_BRANCHING_DOMAIN",
                "n":n,"rank":None,"odd_source_word":None,"even_lift":h}
    return {"status":"CERTIFIED_BRANCHING_INFINITE_FAMILY",
            "n":n,"rank":h+source["rank"],
            "odd_source_word":source["word"],"even_lift":h}


def transition_proof(n):
    """Proof-carrying STRICT decrease and actual successor closure on tested node."""
    before=rank_member(n)
    if before["rank"] is None or before["status"].startswith("HOLD_"):
        raise HOLD("Unknown source integer not silently admitted")
    if n==1:
        return {"status":"TERMINAL","n":1,"rank":0}
    following=T(n)
    if following!=reference_T(n):
        raise HOLD("Independent source Collatz oracle disagrees")
    after=rank_member(following)
    if after["rank"] is None or after["rank"]!=before["rank"]-1:
        raise HOLD("Closure or well-founded rank fails")
    return {
        "status":"PROVEN_ONE_STEP_ON_DECLARED_FAMILY",
        "from":before,"to":after,
        "source_T":following,
        "rank_decreases_exactly_one":True,
        "every_step_keeps_positive_integer":True,
        "restricted_subset_not_all_positive_integers":True,
    }


def old_family_status(n):
    status=old_family_recognize(n)["status"]
    return status.startswith("CERTIFIED_")


def enumerate_family(cap):
    """Enumerate all members <=cap in a FINITE binary inverse subtree.

    Child nodes strictly exceed parents, so BFS prunes exhaustively for
    the BINARY grammar under cap. Extend each odd tree node by 2**h.
    """
    if type(cap) is not int or not 2<=cap<=10**7:
        raise HOLD("Finite source membership enumeration cap exceeded")
    seed={SEED:[]}
    frontier=[SEED]
    while frontier:
        new=[]
        for y in frontier:
            for bit in BINARY_ALPHABET:
                node=child(y,bit)["child"]
                if node>cap:
                    continue
                if node in seed:
                    raise HOLD("Distinct inverse word paths collided")
                seed[node]=seed[y]+[bit]
                new.append(node)
        frontier=new
    members={1}
    power=2
    while power<=cap:
        members.add(power)
        power*=2
    for odd,word in seed.items():
        lifted=odd
        while lifted<=cap:
            members.add(lifted)
            lifted*=2
    new_not_in_old=[]
    for n in sorted(members):
        proof=rank_member(n)
        if proof["rank"] is None or oracle_exact_rank(n)!=proof["rank"]:
            raise HOLD("Independently verified source rank fails enumeration")
        if not old_family_status(n):
            new_not_in_old.append(n)
            # Non-root new odd nodes have first odd successor equal
            # to an EVEN *non-power-of-two*: previous META-005 language
            # is incapable of accepting this extra alternation.
            odd=n
            while odd%2==0:
                odd//=2
            if odd==SEED or (T(odd)&(T(odd)-1))==0:
                raise HOLD("New grammar distinction from previous family lost")
    return {
        "cap":cap,
        "all_odd_inverse_words_below_cap":len(seed),
        "new_nonroot_odd_nodes":len(seed)-1,
        "closed_tree_family_members_below_cap":len(members),
        "new_members_not_in_prior_META005_family":len(new_not_in_old),
        "example_new_members":new_not_in_old[:35],
        "separate_old_family_exact_source_recognizer_used":True,
        "all_bounded_source_members_replay_exact_rank":True,
        "old_language_was_strictly_less_expressive":bool(new_not_in_old),
        "all_positive_integers_claimed_covered":False,
    }


def symbolic_growth_lower_bound(depth):
    """Proof of polynomial-in-X family size, without an empirical fit.

    For y>=5, e0(y)<=3; for each choice bit in {0,1}, e<=6.
    B_e(y)=(2**(2e+1)*y-1)/3 < (8192/3)*y.
    Starting at 5, every length-d word is < 5*(8192/3)**d.
    Unique decoding via v2(T(x)) and strictly decreasing parents
    means ALL 2**d words have distinct positive n values.

    Thus for X>=5, at least 2**floor(log_(8192/3)(X/5))
    distinct generated nodes lie below X (up to strict edge cases).
    => |S intersect [1,X]|=Omega(X**alpha),
       alpha = ln(2)/ln(8192/3) ~= 0.08760374.

    That is asymptotically faster growth than the verified
    O(log(X)**2 loglog(X)) upper bound of previous META-005 family.
    This does NOT imply the new family has positive natural density.
    """
    if type(depth) is not int or not 0<=depth<=10:
        raise HOLD("Bounded finite growth proof witness only")
    bound_num=5*(8192**depth)
    bound_den=3**depth
    from itertools import product
    all_nodes={}
    for word in product(BINARY_ALPHABET,repeat=depth):
        state=encode(word)
        n=state["odd_node"]
        if n*bound_den>bound_num:
            raise HOLD("Symbolic branch growth bound violated")
        if n in all_nodes:
            raise HOLD("Inverse-word decoding not injective")
        if decode(n)["word"]!=list(word):
            raise HOLD("Two distinct codes map to same inverse state")
        if oracle_exact_rank(n,max_steps=2000)!=state["strict_rank"]:
            raise HOLD("Source owner exact accelerated rank disagrees")
        all_nodes[n]=list(word)
    if len(all_nodes)!=1<<depth:
        raise HOLD("Binary subtree did not attain 2**depth nodes")
    return {
        "depth":depth,
        "different_binary_paths":1<<depth,
        "unique_positive_odd_members":len(all_nodes),
        "each_node_below_or_equal_to_bound":True,
        "uniform_rational_upper_bound_numerator":bound_num,
        "uniform_rational_upper_bound_denominator":bound_den,
        "bound_compound_factor":"8192/3",
        "alpha_as_log_expression":"ln(2)/ln(8192/3)",
        "alpha_reference_decimal":round(log(2)/log(8192/3),8),
        "general_proof":"Each branch e<=6 multiplies y by <8192/3; "
                        "each code is uniquely decodable from v2(T(x)); "
                        "therefore at most exponential magnitude but "
                        "2**depth distinct positive integers per level.",
        "polynomial_lower_bound_asymptotically_proved":True,
        "natural_density_proven_positive":False,
        "prior_META005_polylog_upper_bound_strictly_smaller_growth":True,
    }


def classical_inverse_tree_control(max_depth):
    """Fair classical same-grammar BFS, independent from encode()/decode()."""
    if type(max_depth) is not int or not 0<=max_depth<=10:
        raise HOLD("Invalid classical source budget")
    observed={5}
    frontier={5}
    for _ in range(max_depth):
        next_frontier=set()
        for y in frontier:
            if y%9==2:
                e0=1
            elif y%9==5:
                e0=2
            elif y%9==8:
                e0=3
            else:
                raise HOLD("Classical inverse graph escaped its modular state")
            for t in (0,1):
                e=e0+3*t
                n=(2**(2*e+1)*y-1)//3
                if ((2**(2*e+1)*y-1)%3 or n in observed
                    or reference_T(n)!=2**(2*e)*y):
                    raise HOLD("Independent classical inverse edge refuted")
                observed.add(n)
                next_frontier.add(n)
        frontier=next_frontier
    return {
        "max_depth":max_depth,
        "distinct_classical_nodes":len(observed),
        "expected_full_binary_tree_nodes":(1<<(max_depth+1))-1,
        "same_information_classical_exact_tie":
            len(observed)==(1<<(max_depth+1))-1,
    }


def investigate():
    coverage=[enumerate_family(x) for x in COVERAGE_CAPS]
    growth=[symbolic_growth_lower_bound(k) for k in (0,1,2,3,5,8,10)]
    classical=classical_inverse_tree_control(10)
    comparisons=[]
    old_counts={64:18,512:38,4096:64,16384:85}
    new_counts={64:1,512:4,4096:9,16384:18}
    for row in coverage:
        cap=row["cap"]
        old=old_counts[cap]
        additional=row["new_members_not_in_prior_META005_family"]
        if additional!=new_counts[cap]:
            raise HOLD("Observed new inverse language source coverage changed")
        if row["closed_tree_family_members_below_cap"]-additional > old:
            raise HOLD("Old-family containment/admission conflict")
        comparisons.append({
            "cap":cap,
            "prior_META005_exact_members":old,
            "new_inverse_branch_nonmembers_of_prior":additional,
            "provable_union_exact_members":old+additional,
            "relative_improvement_percent":round(100*additional/old,4),
            "all_new_members_have_exact_nonlocal_rank":True,
            "same_information_classical_inverse_tree_can_reproduce":True,
        })
    old_upper=sparse_family_upper_bound(10**30)
    if not (classical["same_information_classical_exact_tie"]
            and growth[-1]["unique_positive_odd_members"]==1024):
        raise HOLD("Synthesis and fair classical controls disagree")
    p={
        "schema":SCHEMA,
        "open_question":"Does every positive integer eventually reach 1 under the Collatz map?",
        "global_status":"COLLATZ_CONJECTURE_STILL_OPEN",
        "question_language_change":
            "FROM_SINGLE_ODD_PREFIX_INVERSE_TO_RECURSIVE_MOD9_STATE_PRESERVING_ODD_INVERSE_BLOCKS",
        "new_branching_program":{
            "seed":5,"seed_accelerated_steps_to_one":4,
            "modular_state_to_minimal_e":{
                str(k):v for k,v in sorted(BASE_EXPONENT_BY_MOD9.items())
            },
            "human_authored_branch_choices":[0,1],
            "odd_inverse_formula":"B_e(y)=(2**(2e+1)*y-1)/3",
            "selected_e":"e0(y mod9)+3*choice",
            "forward_return":"T(B_e(y))=2**(2e)*y followed by 2e even halves",
            "all_created_odd_nodes_mod3":2,
            "e_always_positive":True,
            "inverse_word_uniqueness_recoverable_from":"v2(T(node))/2",
            "exact_rank_of_word":"R(5)=4; R(B_e(y))=R(y)+2e+1; R(2**h*y)=h+R(y)",
            "admitted_nonterminal_states":"All even lifts of every odd node, plus powers of two",
            "general_closure_induction":"Each x=B_e(y) goes to 2**(2e)*y, "
                "an allowed even lift, which halves 2e times to y. "
                "Ranks decrease by exactly one on each intermediate state.",
            "not_all_natural_numbers":True,
        },
        "general_mathematical_growth_certificate":{
            "bounded_inverse_multiplier":"B_e(y)<(8192/3)*y since e<=6",
            "distinct_level_d_nodes": "2**d from binary inverse words of depth d",
            "injectivity":"Each generated x has unique parent from "
                          "T(x)=2**(2e)*y, with v2(T(x))=2e and y odd",
            "all_nodes_level_d_below":"5*(8192/3)**d",
            "counting_lower_bound":"|S intersect [1,X]| >= "
                "2**floor(log_(8192/3)(X/5)) for all sufficiently large X",
            "polynomial_power":"ln(2)/ln(8192/3)",
            "asymptotic":"Omega(X**(ln(2)/ln(8192/3)))",
            "prior_family_asymptotic_upper":
                "O((log X)**2*loglog X) from META-005",
            "strictly_faster_proven_asymptotic_growth":True,
            "neither_natural_density_nor_full_collatz_conjecture_proven":True,
            "general_algebraic_proof_human_review_required":True,
            "independent_formal_proof_assistant_not_run":True,
        },
        "checked_growth_levels":growth,
        "exact_increased_coverage_against_prior_research":comparisons,
        "closed_branch_graph_enumerations":coverage,
        "classical_equal_information_baseline":classical,
        "source_owned_nonmember_refusal":{
            "n":7,"status":rank_member(7)["status"],
            "known_to_converge_by_independent_forward_oracle":
                oracle_exact_rank(7)>0,
            "must_not_promote_nonmembership_to_nonconvergence":True,
        },
        "next_relevant_question":
            "Can an enlarged recursive inverse grammar achieve a rigorous "
            "better polynomial exponent, a nonzero density lower bound, "
            "or a coverage result outside known classical inverse-tree "
            "methods without circularly assuming Collatz?",
        "original_meta005_family_density_zero_preserved":True,
        "no_historically_novel_mathematics_claimed":True,
        "strong_classical_baseline_ties":True,
        "humans_supplied_the_reverse_grammar_and_finite_budget":True,
        "open_limitations":OPEN_LIMITS,
        "automatic_admission":False,"installed":False,
        "external_authority":"NONE",
    }
    p["integrity_digest"]=digest(p)
    return p


def verify_packet(packet):
    if type(packet) is not dict or packet.get("schema")!=SCHEMA:
        raise HOLD("Unknown ranked tree research packet")
    if packet.get("integrity_digest")!=digest({
        k:v for k,v in packet.items() if k!="integrity_digest"
    }):
        raise HOLD("Checksum of original research packet changed")
    if packet!=investigate():
        raise HOLD("Rehashed false math, coverage, status or source graph refused")
    return True


def reenter(packet):
    verify_packet(packet)
    return {
        "status":"INFINITE_BRANCHING_RANK_AND_GROWTH_CERTIFICATES_REVERIFIED",
        "new_external_investigative_questions":0,
        "original_global_collatz_conjecture_solved":False,
        "full_mathematical_source_replay":True,
        "packet_digest":packet["integrity_digest"],
    }


if __name__=="__main__":
    print(json.dumps(investigate(),indent=2,sort_keys=True))
