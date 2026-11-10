"""META-005 — construct an actually INFINITE transition-closed positive domain.

The accelerated Collatz conjecture is still open. This experiment synthesizes
an explicit backwards Collatz certificate family with arbitrary-long odd
prefixes and a genuinely well-founded, nonlocal rank VALID ON THAT FAMILY.

Construction is known-style elementary number theory (3-adic LTE / inverse
3x+1 tree). A universal mathematical argument is written as human-reviewable
induction, and bounded instances are independently replayed. No Lean proof,
new mathematics or universal convergence theorem is claimed.
"""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
import sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"meta001"))
from collatz_frontier import T, reference_T, HOLD, canonical, digest

SCHEMA="motif.meta005.explicit-infinite-transition-closed-rank.v1"
RESEARCH_STATUS="OPEN_COLLATZ_NOT_PROVEN"
KNOWN_SOURCES=[
    {
        "name":"Jeffrey C. Lagarias, Lower Bounds for the Total Stopping Time of 3x+1 Iterates",
        "url":"https://websites.umich.edu/~lagarias/doc/3x%2B1bound.pdf",
        "fact":"Classical inverse 3x+1 tree with two even and conditional odd preimages",
        "not_a_new_theorem":True,
    },
    {
        "name":"Lifting-the-Exponent Lemma (LTE), prime 3",
        "url":"https://circles.math.ucla.edu/circles/lib/data/Handout-2227-1977.pdf",
        "fact":"For odd m, v_3(2**m+1)=1+v_3(m)",
        "not_a_new_theorem":True,
    },
]
LIMITS=[
    "Explicit infinite subset of positive naturals only; no coverage of all positive integers",
    "All parameterized branch, integrality and rank proofs are classic elementary arithmetic",
    "Symbolic universal induction is human-reviewable, not formalized in Lean",
    "Independent finite computational examples are not substitutes for the induction argument",
    "The classical inverse-tree and direct-iteration baselines have the same information",
    "No unrestricted autonomous invention of new axioms or mathematics",
    "No 2-adic ghost or nonpositive integer is admitted",
]


def v3(n):
    if type(n) is not int or n < 1:
        raise HOLD("3-adic valuation requires a positive integer")
    count=0
    while n%3==0:
        n//=3
        count+=1
    return count


def odd_inverse(y):
    """Classical reverse accelerated Collatz branch: T(x)=y, x odd >1."""
    if type(y) is not int or y < 1:
        raise HOLD("Positive successor required")
    if y%3 != 2:
        return None
    x=(2*y-1)//3
    if x<=1 or x%2==0:
        return None
    if T(x)!=y or reference_T(x)!=y:
        raise HOLD("Odd source inverse fails exact recheck")
    return x


def even_inverse(y):
    """Unconditional reverse accelerated Collatz branch."""
    if type(y) is not int or y < 1:
        raise HOLD("Positive successor required")
    x=2*y
    if T(x)!=y or reference_T(x)!=y:
        raise HOLD("Even inverse fails")
    return x


def parameter(j,t,i,h):
    """Typed finite description of INFINITE-FAMILY member, not a guessed orbit.

    Choose j>=1, t>=0; m=3**(j-1)*(2t+1).
    For 0<=i<=j, A=2**m+1 is divisible by 3**i (LTE).
    n_i = 2**i * (A/3**i) - 1, with n_0=2**m.
    Even preimages 2**h*n_i are included for all h>=0.

    The sole degeneracy j=1,t=0,i=1 produces n=1, which
    must have rank 0 as terminal; exclude it as a ranked odd member.
    """
    if any(type(v) is not int for v in (j,t,i,h)):
        raise HOLD("Parameters must be exact integers")
    if not 1<=j<=8 or not 0<=t<=6 or not 0<=i<=j or not 0<=h<=10:
        raise HOLD("Materialization budget exceeded; symbolic claim is unbounded")
    m=3**(j-1)*(2*t+1)
    if j==1 and t==0 and i>0:
        raise HOLD("The terminal 1 cannot be admitted as a positive-rank odd point")
    numerator=(1<<m)+1
    d=3**i
    if numerator % d:
        raise HOLD("3-adic integrality of inverse family falsified")
    core=(1<<i)*(numerator//d)-1
    if core<2 or (i>0 and not core&1) or (i==0 and core!=(1<<m)):
        raise HOLD("Generated core is not an admitted positive source state")
    n=(1<<h)*core
    rank=m+i+h
    if n<=1 or rank<=0:
        raise HOLD("Well-founded positive-rank family contract broken")
    return {
        "schema":"motif.meta005.parameterized-inverse-construct.v1",
        "j":j,"t":t,"i":i,"h":h,"m":m,
        "valuation_guarantee":"v3(2**m+1) = 1+v3(m) >= j",
        "core_integer":core,"positive_integer":n,"rank":rank,
        "odd_inverse_chain_length":i,
        "exact_2_adic_valuation":h if i>=1 else m+h,
        "all_transitions_remain_inside_explicit_family":True,
        "this_is_not_a_membership_proof_for_all_positive_integers":True,
    }


def _compressed_member(j,t,i,h):
    """Construct high-level symbolic proof without computing massive 2**m."""
    if any(type(v) is not int for v in (j,t,i,h)) or (
        j<1 or t<0 or i<0 or i>j or h<0
    ):
        raise HOLD("Invalid symbolic family word")
    m=3**(j-1)*(2*t+1)
    if m==1 and i>0:
        raise HOLD("Terminal 1 has rank zero")
    return {
        "j":j,"t":t,"i":i,"h":h,"m":"3**(j-1)*(2*t+1)",
        "core_symbolic":"2**i*((2**m+1)/3**i)-1",
        "n_symbolic":"2**h * (2**i*((2**m+1)/3**i)-1)",
        "rank_symbolic":"m+i+h",
        "valuation_condition":"v3(2**m+1) = 1+v3(m) >= j >= i",
        "proof_scope":"ALL_NONNEGATIVE_T_H_AND_ALL_J_GE_1_WITH_i_LE_j",
    }


def successor(card):
    """Algorithmic structural transition on a proven inverse family member."""
    if type(card) is not dict or card.get("schema")!=(
        "motif.meta005.parameterized-inverse-construct.v1"
    ):
        raise HOLD("Cannot treat unknown integer as proven family member")
    actual=parameter(card["j"],card["t"],card["i"],card["h"])
    if actual!=card:
        raise HOLD("Altered family member proof")
    j,t,i,h=(card[x] for x in ("j","t","i","h"))
    if h>0:
        dest=parameter(j,t,i,h-1)
        origin="REMOVE_EVEN_INVERSE"
    elif i>0:
        dest=parameter(j,t,i-1,0)
        origin="REMOVE_ONE_ODD_INVERSE"
    else:
        # Power of two already; rank m and exact next power 2**(m-1).
        m=card["m"]
        if m==1:
            dest={
                "schema":"motif.meta005.terminal.v1",
                "positive_integer":1,"rank":0,
            }
        else:
            # This is same positive power-of-two family, not a newly
            # inferred membership for unknown integers. It need not have
            # an admissible odd-m parametrization as m-1 may be even.
            dest={
                "schema":"motif.meta005.power-two.v1",
                "positive_integer":1<<(m-1),"exponent":m-1,
                "rank":m-1,
            }
        origin="POWER_OF_TWO_DECREMENT"
    if not (T(card["positive_integer"])==dest["positive_integer"]
            and reference_T(card["positive_integer"])==dest["positive_integer"]
            and dest["rank"]==card["rank"]-1):
        raise HOLD("Exact family closure or strict rank decrease refuted")
    return {"source":card,"target":dest,"rank_before":card["rank"],
            "rank_after":dest["rank"],
            "move":origin,"strictly_decreases":True,
            "all_natural_integer_states":True}


def power_two_state(k):
    if type(k) is not int or not 0<=k<=40000:
        raise HOLD("Materialized exponent budget exceeded")
    return {"schema":"motif.meta005.power-two.v1",
            "positive_integer":1<<k,"exponent":k,"rank":k}


def verify_power_two_edge(k):
    if type(k) is not int or not 1<=k<=10000:
        raise HOLD("Power of two proof edge bound")
    a,b=power_two_state(k),power_two_state(k-1)
    if T(a["positive_integer"])!=b["positive_integer"] or (
        a["rank"]!=b["rank"]+1
    ):
        raise HOLD("Power-two branch not decreasing")
    return {"from":a,"to":b,"edge":"EVEN_HALF",
            "verified":True}


def oracle_exact_rank(n,*,max_steps=30000):
    """Independent direct forward iteration; not a universal theorem."""
    if type(n) is not int or n<1 or type(max_steps) is not int or max_steps<1:
        raise HOLD("Outside finite reference source scope")
    x=n
    visited=set()
    steps=0
    while x!=1:
        if x in visited or steps>=max_steps:
            raise HOLD("Unverified orbit beyond declared source budget")
        visited.add(x)
        x=reference_T(x)
        steps+=1
    return steps


def recognize(n,*,max_odd_prefix=100):
    """Safely recognize a restricted family; HOLD is not divergence.

    The closed family is the inverse of a power of two through an INITIAL
    consecutive odd prefix, preceded by any number of even preimages.
    This intentionally does not include *all* known convergent starts.
    """
    if type(n) is not int or n<1 or type(max_odd_prefix) is not int or (
        max_odd_prefix<1 or max_odd_prefix>10000
    ):
        raise HOLD("Unknown positive source state or unsafe search budget")
    if n==1:
        return {"status":"CERTIFIED_TERMINAL_1",
                "n":1,"rank":0,"all_positive_integers_covered":False}
    k=0
    q=n
    while q%2==0:
        q//=2
        k+=1
    if q==1:
        return {"status":"CERTIFIED_POWERS_OF_TWO",
                "n":n,"rank":k,"all_positive_integers_covered":False}
    current=q
    odd_steps=0
    while current>1 and current%2:
        if odd_steps>=max_odd_prefix:
            return {"status":"HOLD_OUTSIDE_BOUNDED_RECOGNIZER",
                    "n":n,"rank":None,"all_positive_integers_covered":False}
        current=reference_T(current)
        odd_steps+=1
    if current<2 or current&(current-1):
        return {"status":"HOLD_OUTSIDE_EXPLICIT_PARAMETRIC_FAMILY",
                "n":n,"rank":None,"all_positive_integers_covered":False}
    m=current.bit_length()-1
    if m<1 or m%2==0 or v3(m)<odd_steps-1:
        raise HOLD("Odd-prefix inverse failed mandatory 3-adic membership")
    j=odd_steps
    t=((m//3**(j-1))-1)//2
    if 3**(j-1)*(2*t+1)!=m or t<0:
        raise HOLD("Parameter witness failed")
    if q!=((1<<j)*(((1<<m)+1)//3**j)-1):
        raise HOLD("Independent source trajectory and inverse formula disagree")
    return {"status":"CERTIFIED_NONTRIVIAL_ODD_INVERSE_FAMILY",
            "n":n,"odd_core":q,"m":m,"j":j,"t":t,
            "even_prefix_halvings":k,"rank":k+j+m,
            "all_positive_integers_covered":False}


def verify_lte_induction_examples(jmax=7,tmax=5):
    """Finite cross-check of general LTE induction; not its universal proof."""
    if jmax>7 or jmax<1 or tmax>5 or tmax<0:
        raise HOLD("Bounded symbolic-replay limits")
    records=[]
    for j in range(1,jmax+1):
        for t in range(tmax+1):
            m=3**(j-1)*(2*t+1)
            number=(1<<m)+1
            classical=v3(number)
            expected=1+v3(m)
            if classical!=expected or classical<j:
                raise HOLD("Classical independent LTE valuation disagrees")
            if j>=2 or t>0:
                final=parameter(j,t,j,0)
                recognized=recognize(final["positive_integer"],max_odd_prefix=j)
                if (recognized["status"]!=
                    "CERTIFIED_NONTRIVIAL_ODD_INVERSE_FAMILY" or
                    recognized["rank"]!=final["rank"]):
                    raise HOLD("Symbolic chain not recognized by independent T trace")
                records.append({
                    "j":j,"t":t,"m":m,
                    "v3_2_power_m_plus_1":classical,
                    "first_j_steps_odd":True,
                    "rank_without_tracing_full_orbit":final["rank"],
                    "direct_reference_rank":oracle_exact_rank(
                        final["positive_integer"],max_steps=12000),
                })
    if any(x["rank_without_tracing_full_orbit"]!=x["direct_reference_rank"]
           for x in records):
        raise HOLD("Independent direct trajectory differs from symbolic rank")
    return records


def sparse_family_upper_bound(X):
    """Proof that the EXPLICIT INFINITE family has natural density ZERO.

    For each admissible odd core n_i with m odd >=3, i<=1+v3(m),
    3**i <= 3*m, hence n_i+1 >= 2**m/(3*m).
    For every integer m>=4, m<=2**(m/2) (elementary induction
    from m=4,5, advancing by 2), so n_i+1 >= 2**(m/2)/3.
    If n_i<=X, m <= 2*log2(3*(X+1)).
    The small m=1,3 also satisfy the loose integer bound M below.

    Let H=floor(log2(X)), M=2*bit_length(3*(X+1)),
    J=1+floor(log3(M)). Every member <=X is either one of
    H+1 powers of two or described by at most M choices of m,
    J choices of the inverse-odd index i, and H+1 even lifts h.
    So the cardinality is at most (H+1)*(1+M*J), i.e.,
    O((log X)**2 * loglog X) = o(X). That's a symbolic
    DENSITY-ZERO result, not merely observed sparsity in samples.

    This explicit family cannot solve all-n Collatz by density or
    infinitude alone. Classic constructions, not historically new.
    """
    if type(X) is not int or X < 2:
        raise HOLD("Positive finite density-bound parameter required")
    H=X.bit_length()-1
    M=2*(3*(X+1)).bit_length()
    J=1
    threshold=M
    while threshold>=3:
        threshold//=3
        J+=1
    upper=(H+1)*(1+M*J)
    return {
        "X":X,
        "H_floor_log2_X":H,
        "M_upper_bound_on_power_of_two_core_exponent":M,
        "J_upper_bound_on_odd_inverse_depth":J,
        "symbolic_max_family_members_below_X":upper,
        "rigorous_asymptotic":"O(log(X)**2*loglog(X)) = o(X)",
        "natural_density_of_this_explicit_family":0,
        "asserts_natural_density_of_full_Collatz_basin":False,
        "proof_uses_3_adic_depth_and_elementary_exponential_growth":True,
    }


def enumerate_bounded_family(X):
    """Independent complete INTEGER enumeration for a small finite X."""
    if type(X) is not int or not 2<=X<=20000:
        raise HOLD("Finite family coverage sweep out of budget")
    observed=[]
    for n in range(1,X+1):
        if recognize(n)["status"].startswith("CERTIFIED_"):
            observed.append(n)
    upper=sparse_family_upper_bound(X)
    if len(observed)>upper["symbolic_max_family_members_below_X"]:
        raise HOLD("Bounded enumeration violated symbolic density bound")
    if 7 in observed:
        raise HOLD("Wrongly admitted convergent 7 to explicit restricted grammar")
    return {
        "X":X,
        "members_of_explicit_inverse_family_below_X":len(observed),
        "fraction_of_positive_starts_observed":f"{len(observed)}/{X}",
        "mathematical_upper_bound":upper,
        "all_members_from_separate_forward_recognizer":True,
        "observed_nonmembers_not_declared_nonconvergent":True,
        "examples":observed[:35],
    }


def inverse_tree_fair_baseline(max_depth=13):
    """Predeclared classical inverse-tree baseline, not claimed as novelty."""
    if type(max_depth) is not int or not 1<=max_depth<=15:
        raise HOLD("Inverse-tree depth budget exceeded")
    by_rank={1:0}
    layers=[{"depth":0,"new_nodes":[1]}]
    frontier=[1]
    for d in range(1,max_depth+1):
        following=[]
        for y in frontier:
            for x in (even_inverse(y),odd_inverse(y)):
                if x is None or x in by_rank:
                    continue
                if T(x)!=y or reference_T(x)!=y:
                    raise HOLD("Independent inverse source not closed")
                by_rank[x]=d
                following.append(x)
        frontier=sorted(following)
        layers.append({"depth":d,"new_nodes":frontier})
    for n,rank in by_rank.items():
        if n!=1 and oracle_exact_rank(n,max_steps=10000)!=rank:
            raise HOLD("Classical inverse-tree depth is not Collatz rank")
    return {"max_depth":max_depth,
            "source_nodes":len(by_rank),
            "direct_calculated_depths_match_all_inverse_edges":True,
            "layers":layers,
            "not_a_proof_of_every_n_positive":True}


def investigate():
    symbolic=[
        {
            "j":j,
            "parameter_t_symbolic":"t>=0 integer; exclude terminal i=1,j=1,t=0",
            "m_symbolic":"3**(j-1)*(2*t+1)",
            "first_j_accelerated_steps_odd":True,
            "rank_symbolic":"m+j (and +h for any even lift 2**h)",
            "general_integer_positivity_and_rank_proof":"LTE + inverse recurrence + inductive rank descent",
            "representative":_compressed_member(j,0 if j>1 else 1,j,2)
        }
        for j in range(1,9)
    ]
    replay=verify_lte_induction_examples()
    hold=recognize(7)
    if hold["status"]!="HOLD_OUTSIDE_EXPLICIT_PARAMETRIC_FAMILY":
        raise HOLD("Misrepresenting this subset as the full Collatz basin")
    known7_rank=oracle_exact_rank(7)
    if known7_rank<=0:
        raise HOLD("Seven reference orbit did not converge")
    classical=inverse_tree_fair_baseline()
    density=[enumerate_bounded_family(X) for X in (64,512,4096,16384)]
    output={
        "schema":SCHEMA,
        "question":"Can MOTIF provide a non-circular, infinitely parametrized, "
                   "transition-closed positive-integer domain with a verified "
                   "well-founded Collatz rank, while not falsely claiming "
                   "the entire set of positive integers?",
        "global_collatz_problem_status":RESEARCH_STATUS,
        "original_source_provenance":KNOWN_SOURCES,
        "new_structural_question":"Which explicitly constructible inverse-branch "
                                  "words yield closed infinite families with "
                                  "rank known symbolically before orbit simulation?",
        "grammar_primitives":["EVEN_PREIMAGE_2Y","ODD_PREIMAGE_(2Y-1)/3",
                              "THREE_ADIC_DIVISIBILITY","EXACT_POWER_OF_TWO",
                              "INDUCTIVE_WELL_FOUNDED_RANK"],
        "ranked_family_symbolic":[
            "Terminal 1 has rank 0.",
            "Every power 2**e (e>=0) has rank e, with terminal 1 at e=0.",
            "For j>=1,t>=0, set m=3**(j-1)*(2t+1), A=2**m+1.",
            "For 0<=i<=j, n_i=2**i*(A/3**i)-1 is an integer.",
            "Exclude only j=1,t=0,i=1 (n_i=1 as positive-ranked odd core).",
            "Every n=2**h*n_i for h>=0 belongs to the family.",
            "Rank(n)=h+i+m, except the excluded n=1 terminal.",
            "T(2**h*n_i)=2**(h-1)*n_i for h>0.",
            "T(n_i)=n_(i-1) for i>0.",
            "T(2**m)=2**(m-1), terminating at 1.",
        ],
        "general_induction_certificate":{
            "statement":"For every j>=1,t>=0,h>=0 and 0<=i<=j "
                        "(excluding j=1,t=0,i=1), all members are "
                        "positive natural integers with finite rank "
                        "h+i+m strictly decreasing by 1 on every accelerated "
                        "Collatz step before reaching terminal 1.",
            "valuation_proof_steps":[
                "Write m=3**s*u where u is odd not divisible by 3.",
                "For such u, u mod6 is 1 or 5; 2**u mod9 is 2 or 5, "
                "so v3(2**u+1)=1.",
                "For any x=-1+3q, x**3+1=(x+1)*(x**2-x+1), "
                "and x**2-x+1=3*(1-3q+3q**2), adding exactly "
                "one factor of 3.",
                "Cubing s times yields v3(2**m+1)=1+v3(m)>=j.",
                "Therefore every A/3**i in the stated range is a "
                "positive integer; n_i is positive and odd for i>0, "
                "except the explicitly excluded terminal degeneracy.",
            ],
            "rank_proof_steps":[
                "For i>0, (3*n_i+1)/2 = "
                "2**(i-1)*(A/3**(i-1))-1=n_(i-1).",
                "For h>0, T(2**h*n_i)=2**(h-1)*n_i.",
                "For i=0, n_0=2**m; repeated even halves reach 1.",
                "Rank h+i+m is a nonnegative integer, zero only "
                "at terminal 1, and decreases by exactly one on "
                "each verified nonterminal edge.",
                "Thus every parametrized family member reaches 1 "
                "in exactly its asserted rank; the family is infinite "
                "and closed under nonterminal accelerated transitions.",
            ],
            "formal_proof_assistant_check":"NOT_PERFORMED",
            "human_review_of_general_induction_required":True,
            "classical_known_inversion_not_historically_new":True,
        },
        "arbitrarily_long_odd_prefix_programs":symbolic,
        "bounded_LTE_and_direct_orbit_crosschecks":replay,
        "counterexample_to_false_family_completeness":{
            "integer":7,
            "proven_convergent_by_direct_reference":True,
            "reference_accelerated_steps_to_one":known7_rank,
            "explicit_family_membership_attempt":hold,
            "nonmembership_does_not_imply_divergence":True,
        },
        "classical_inverse_tree_baseline":classical,
        "new_finite_parameter_family_density_obstruction":density,
        "full_density_zero_proof_scope":"ONLY_THIS_RESTRICTED_EXPLICIT_FAMILY",
        "new_question_from_density_limitation":"Which independent, rigorously "
            "described infinite inverse families could improve quantitative "
            "coverage beyond a known density-zero subfamily, while retaining "
            "exact natural-integer admission and proof-carrying rank?",
        "next_unresolved_mathematical_question":
            "Can this proof-carrying inverse-family grammar establish "
            "a transition-closed infinite family with a quantitatively "
            "new coverage result beyond already-known inverse-tree "
            "methods, or demonstrate that every positive integer "
            "belongs to some certified family WITHOUT assuming Collatz?",
        "unresolved_limits":LIMITS,
        "equal_information_classical_inverse_tree_not_beaten":True,
        "real_independent_agents_or_unrestricted_math_invention":False,
        "all_positive_integers_claimed_certified":False,
        "automatic_admission":False,"installed":False,
        "external_authority":"NONE",
    }
    output["integrity_digest"]=digest(output)
    return output


def verify_packet(packet):
    if type(packet) is not dict or packet.get("schema")!=SCHEMA:
        raise HOLD("Unknown infinite-family certificate")
    if packet.get("integrity_digest")!=digest({
        k:v for k,v in packet.items() if k!="integrity_digest"
    }):
        raise HOLD("Tampered certificate checksum")
    if packet!=investigate():
        raise HOLD("Rehashed false family rank, source, limit or theorem rejected")
    return True


def reenter(packet):
    verify_packet(packet)
    return {
        "status":"EXPLICIT_INFINITE_CLOSED_FAMILY_RANK_REVERIFIED",
        "new_external_investigative_questions":0,
        "finite_exact_source_examples_and_general_induction_replayed":True,
        "theorem_prover_formalization":False,
        "collatz_conjecture_globally_solved":False,
        "packet_digest":packet["integrity_digest"],
    }


if __name__=="__main__":
    print(json.dumps(investigate(),indent=2,sort_keys=True))
