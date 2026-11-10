"""META-004 — replace finite residue counting with exact 2-adic representations.

The OPEN Collatz problem concerns ordinary positive INTEGERS. A nested
sequence of finite 'unresolved' 2-adic cylinders need not contain an
ordinary positive integer, even though EACH cylinder does.

This module synthesizes exact periodic 2-adic rational points from parity
words, classifies negative/rational 'ghost' points, constructs positive
finite-prefix lookalikes, and tests a nonlocal finite reachable-basin rank.

Neither part solves Collatz. All candidate grammars and test sources are
engineer-authored; the 2-adic parity correspondence is known mathematics.
"""
from __future__ import annotations

from collections import Counter
from fractions import Fraction
from itertools import product
from copy import deepcopy
from hashlib import sha256
import json
import sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"meta001"))
from collatz_frontier import T, reference_T, HOLD, canonical, digest
sys.path.insert(0,str(HERE.parent/"meta003"))
from invariant_stress import first_class_descent, independent_first_class_descent

SCHEMA="motif.meta004.two-adic-boundary-and-nonlocal-rank.v1"
REFERENCE={
    "title":"On the Collatz Conjecture: Martingales, Momentum and Continued Fractions",
    "authors":"Nicholas Polson and Vadim Sokolov",
    "year":2026,
    "section":"Proposition 15.1 and finite-residue exceptional 2-adic set",
    "url":"https://vsokolov.org/books/collatz/results.html",
    "claim_scope":"Reports the exceptional 2-adic set includes negative integers -1, -5, -17.",
    "external_source_not_authenticating_this_experiment":True,
}
BOUNDARY=[
    "Every finite 2-adic cylinder contains infinitely many positive integers.",
    "The intersection of nested cylinders can contain only a negative integer or a noninteger 2-adic rational.",
    "An infinite parity path in Z_2 need not be an actual positive-integer Collatz trajectory.",
    "An undecided finite residue class is not an orbit proved never to descend.",
    "The exact standard periodic parity / 2-adic rational fixed-point construction is known mathematics.",
    "A finite verified basin rank is defined only on that verified closed finite transition graph.",
    "Bounded positive approximants do not prove convergence of all positive integers.",
    "No global proof, novel theorem, real autonomous source owner or independent scholarly adjudication.",
]
FINITE_WORD_DEPTH=8
SHADOW_DEPTHS=(8,12,16,20,24)
CONJECTURE_STATUS="OPEN_NO_GLOBALLY_VALID_TERMINATION_PROOF"


def signed_T(n):
    """Exact accelerated map on ALL ordinary integers, including negatives.
    Only for symbolic 2-adic analysis; positive original task unchanged.
    """
    if type(n) is not int:
        raise HOLD("Signed Collatz state must be integer")
    return (3*n+1)//2 if n&1 else n//2


def rational_parity(x):
    """A Fraction with ODD denominator is a 2-adic integer.
    Its parity is numerator mod 2 since denominator invertible mod 2.
    """
    if not isinstance(x,Fraction) or x.denominator%2==0:
        raise HOLD("Only rational 2-adic integers with odd denominator")
    return x.numerator%2


def rational_T(x):
    bit=rational_parity(x)
    y=(3*x+1)/2 if bit else x/2
    if y.denominator%2==0:
        raise HOLD("A 2-adic rational step left the integral 2-adic ring")
    return y


def program_for_parity_word(word):
    """Compose affine map from raw EVEN/ODD operations; NO prelisted cycle."""
    if type(word) not in (tuple,list) or not 1<=len(word)<=11 or any(
        type(bit) is not int or bit not in (0,1) for bit in word
    ):
        raise HOLD("Unsupported primitive parity program")
    a,b,d=1,0,1
    for bit in word:
        if bit:
            a,b,d=3*a,3*b+d,2*d
        else:
            d*=2
    if d!=(1<<len(word)):
        raise HOLD("Symbolic affine program denominator wrong")
    return {
        "parity_bits":list(word),
        "symbolic_map":{"a":a,"b":b,"d":d},
        "composed_from":["EXACT_HALF","IS_ODD","MULTIPLY_BY_THREE","ADD_ONE"],
        "high_level_negative_cycle_operator_preprovided":False,
    }


def periodic_point(word):
    """Solve T^k(x)=x in Z_2 for a supplied periodically repeated parity word.

    Since 2^k-3^ones is odd, x=b/(2^k-3^ones) belongs to Z_2.
    Verify EXACT parity compliance, not an arbitrary rational root.
    """
    p=program_for_parity_word(word)
    a,b,d=(p["symbolic_map"][k] for k in ("a","b","d"))
    denom=d-a
    if denom==0 or denom%2==0:
        raise HOLD("Invalid 2-adic fixed-point denominator")
    x=Fraction(b,denom)
    if x.denominator%2==0:
        raise HOLD("Candidate not 2-adically integral")
    vals=[]
    cur=x
    for bit in word:
        if rational_parity(cur)!=bit:
            raise HOLD("Algebraic fixed point violates parity program")
        vals.append({"num":cur.numerator,"den":cur.denominator,"parity":bit})
        cur=rational_T(cur)
    if cur!=x:
        raise HOLD("Exact rational 2-adic periodic orbit failed closure")
    typ=(
        "ZERO_NOT_POSITIVE" if x==0 else
        "POSITIVE_INTEGER" if x.denominator==1 and x>0 else
        "NEGATIVE_INTEGER_GHOST" if x.denominator==1 and x<0 else
        "NONINTEGER_RATIONAL_TWO_ADIC_GHOST"
    )
    if x.denominator==1 and signed_T(x.numerator)!=int(rational_T(x)):
        raise HOLD("Independent ordinary signed integer step disagrees")
    return {
        "schema":"motif.meta004.exact-two-adic-periodic-point.v1",
        "input_word":list(word),
        "symbolic_program":p,
        "periodic_x":{"num":x.numerator,"den":x.denominator},
        "exact_cycle_states":vals,
        "classification":typ,
        "2_adic_integrality_proved_by_odd_denominator":True,
        "rational_cycle_verified_exactly":True,
        "positive_collatz_counterexample_proved":False,
        "external_real_world_or_historical_claim":False,
    }


def enumerate_periodic_grammar(max_period=FINITE_WORD_DEPTH):
    if type(max_period) is not int or not 1<=max_period<=8:
        raise HOLD("Finite parity program enumeration budget exceeded")
    tally=Counter()
    distinct={}
    all_word_count=0
    interesting=[]
    for k in range(1,max_period+1):
        for word in product((0,1),repeat=k):
            p=periodic_point(word)
            all_word_count+=1
            tally[p["classification"]]+=1
            f=p["periodic_x"]
            distinct.setdefault((f["num"],f["den"]),p["classification"])
            if p["classification"]=="NEGATIVE_INTEGER_GHOST" and (
                f["num"] in (-1,-5,-7,-10)
            ):
                interesting.append(p)
    if all_word_count!=sum(tally.values()):
        raise HOLD("Omitted exact parity-word programs")
    return {
        "max_word_length":max_period,
        "all_parity_words_examined":all_word_count,
        "classifications":dict(sorted(tally.items())),
        "distinct_rational_two_adic_points":len(distinct),
        "distinguished_negative_integer_records":interesting,
        "every_periodic_word_has_one_exact_two_adic_point":True,
        "positive_ordinary_integer_rational_cycles_never_beyond_trivial_1_2":
            all((n,d) in ((1,1),(2,1))
                for (n,d),t in distinct.items() if t=="POSITIVE_INTEGER"),
        "cannot_extrapolate_finite_period_enumeration_to_all_periods":True,
    }


def positive_shadow(rational_cycle,depth,trajectory_cap=1400):
    """Positive n with same FIRST depth parity bits as 2-adic periodic x.

    x=p/q with q odd. n ≡ p*q^(-1) (mod 2**depth).
    This is exact modular arithmetic and is NOT equality n=x in Z_2.
    """
    if type(depth) is not int or depth not in SHADOW_DEPTHS:
        raise HOLD("Unapproved finite shadow precision")
    r=rational_cycle["periodic_x"]
    x=Fraction(r["num"],r["den"])
    period=rational_cycle["input_word"]
    q=1<<depth
    first=(x.numerator*pow(x.denominator,-1,q))%q
    n=first if first>1 else first+q
    cur_n=n
    cur_x=x
    for i in range(depth):
        if cur_n%2!=rational_parity(cur_x):
            raise HOLD("Finite positive integer does not shadow 2-adic parity")
        if cur_n%2 != period[i%len(period)]:
            raise HOLD("Periodic 2-adic parity pattern drift")
        cur_n=reference_T(cur_n)
        cur_x=rational_T(cur_x)
    # A finite sample convergence test, whose answer is never promoted.
    current=n
    steps=0
    while current!=1 and steps<trajectory_cap:
        current=reference_T(current)
        steps+=1
    return {
        "depth":depth,"modulus":q,
        "two_adic_rational":r,
        "positive_shadow_n":n,
        "parity_match_for_all_declared_prefix_steps":True,
        "periodic_parity_word":list(period),
        "n_is_exactly_equal_to_the_two_adic_point":False,
        "finite_shadow_reached_one":current==1,
        "finite_shadow_steps_to_one_if_verified":steps if current==1 else None,
        "no_general_positive_integer_convergence_proof":True,
    }


def ghost_branches():
    # Native graph grammar discovers all-periodic rational points up to 8.
    # Explicit period-11 historical negative orbit is separately verified.
    cases={
        "all_odd_negative_minus_one":(1,),
        "negative_three_cycle_minus_five":(1,1,0),
        "negative_eleven_cycle_minus_seventeen":(1,1,1,1,0,1,1,1,0,0,0),
        "noninteger_rational_four_fifths":(0,0,1),
        "legitimate_positive_one_two":(1,0),
    }
    result={}
    for name,word in cases.items():
        p=periodic_point(word)
        shadows=[positive_shadow(p,k) for k in SHADOW_DEPTHS]
        if not all(x["finite_shadow_reached_one"] for x in shadows):
            raise HOLD("Source-owned positive shadow finite convergence control failed")
        result[name]={"periodic_program":p,"finite_positive_shadows":shadows}
    if result["all_odd_negative_minus_one"]["periodic_program"]["periodic_x"]!={"num":-1,"den":1}:
        raise HOLD("Wrong exact inverse limit of all-odd branch")
    if result["negative_three_cycle_minus_five"]["periodic_program"]["periodic_x"]!={"num":-5,"den":1}:
        raise HOLD("Wrong exact negative 2-adic three-cycle")
    if result["negative_eleven_cycle_minus_seventeen"]["periodic_program"]["periodic_x"]!={"num":-17,"den":1}:
        raise HOLD("Wrong exact negative 2-adic eleven-cycle")
    if result["noninteger_rational_four_fifths"]["periodic_program"]["periodic_x"]!={"num":4,"den":5}:
        raise HOLD("Wrong nonordinary rational 2-adic cycle")
    # Cross-wire to genuine META-003 unresolved cylinders. For each of
    # three negative periodic 2-adic states, EVERY tested finite K cylinder
    # contains infinitely many positive lookalikes yet has no class-wide
    # certified descent within K. This remains true only at the stated K.
    overlaps=[]
    for negative in (-1,-5,-17):
        for k in (8,12,16):
            residue=negative%(1<<k)
            a=first_class_descent(k,residue)
            b=independent_first_class_descent(k,residue)
            if a is not None or b is not None:
                raise HOLD("Negative ghost not in original bounded HOLD scope")
            overlaps.append({
                "two_adic_negative_integer":negative,
                "k":k,"positive_integers_same_class_modulus":1<<k,
                "residue":residue,
                "inherited_META003_first_descent_status":"HOLD_WITHIN_K",
                "no_positive_counterexample_proven":True,
            })
    return {
        "schema":"motif.meta004.genuine-two-adic-versus-natural-integer-frontier.v1",
        "special_cases":result,
        "crosscheck_against_original_META003_residue_HOLDs":overlaps,
        "all_ones_nested_cylinders":"n congruent 2**k-1 mod 2**k for every k",
        "all_ones_unique_intersection_in_two_adics":{"num":-1,"den":1},
        "all_ones_intersection_with_positive_integers_is_empty":True,
        "each_finite_all_ones_cylinder_contains_infinite_positive_integers":True,
        "same_parity_prefix_does_not_mean_same_infinite_integer":True,
        "infinite_undecided_path_does_not_prove_actual_positive_divergence":True,
        "reason":"The positive integers are dense but NOT closed in the 2-adic topology.",
        "nonlocal_question":"Does the infinite unresolved parity path correspond to "
                            "an ordinary positive integer, rather than a 2-adic ghost?",
        "provenance":{"external_known_analysis":REFERENCE,
                      "new_historical_mathematics_discovered":False},
    }


def build_finite_nonlocal_basin(train_max=128, heldout_max=512):
    """Construct a real WELL-FOUNDED rank over a finite source-verified basin.

    Ranking is distance to terminal 1, via *actual transition graph*
    (future nonlocal knowledge). Closure is checked on the FINITE
    enumerated node set, not all positive integers. The proof is
    existential source replay, not a uniform predictive rank formula.
    """
    if ((train_max,heldout_max)!=(128,512)):
        raise HOLD("Only predeclared frozen train/heldout source scope")
    distances={1:0}
    edges={}
    traces=[]
    source_calls=0
    train_new=0
    heldout_new=0
    def absorb(n,phase):
        nonlocal source_calls,train_new,heldout_new
        path=[]
        seen=set()
        cur=n
        while cur not in distances:
            if cur in seen or len(path)>1400:
                raise HOLD("Unresolved cyclic or out-of-budget real positive path")
            seen.add(cur)
            nxt=T(cur)
            if nxt!=reference_T(cur):
                raise HOLD("Independent Collatz source oracle disagreement")
            edges[cur]=nxt
            path.append(cur)
            cur=nxt
            source_calls+=1
        rank=distances[cur]
        for x in reversed(path):
            rank+=1
            distances[x]=rank
        if phase=="train":
            train_new+=len(path)
        else:
            heldout_new+=len(path)
        return {"start":n,"phase":phase,
                "new_transition_questions":len(path),
                "reused_known_suffix":cur,
                "rank":distances[n],
                "status":"FINITE_SOURCE_CLOSED_BASIN_PROVED"}
    for n in range(2,train_max+1):
        traces.append(absorb(n,"train"))
    training_size=len(distances)
    for n in range(train_max+1,heldout_max+1):
        traces.append(absorb(n,"heldout"))
    # The transition set is mathematically CLOSED with absorbing 1:
    # every nonterminal edge stays within the finite certified basin.
    if set(edges)!=(set(distances)-{1}):
        raise HOLD("Cannot close finite graph")
    if any(y not in distances or distances[x]!=distances[y]+1
           for x,y in edges.items()):
        raise HOLD("Well-founded nonlocal distance rank failed exact replay")
    # Fair classical memoized baseline: from scratch exact dynamic oracle
    # returns same known endpoint evidence, same discovered node set.
    classical={1:0}
    for n in range(2,heldout_max+1):
        path=[];cur=n
        while cur not in classical:
            if len(path)>1400 or cur in path:
                raise HOLD("Classical baseline reached unresolved state")
            path.append(cur)
            cur=reference_T(cur)
        d=classical[cur]
        for u in reversed(path):
            d+=1;classical[u]=d
    if distances!=classical:
        raise HOLD("Strong classical memoized oracle disagrees")
    naive_total=sum(distances[n] for n in range(2,heldout_max+1))
    if naive_total<=source_calls:
        raise HOLD("No transition-memory reuse measured")
    by_train=traces[:train_max-1]
    by_hold=traces[train_max-1:]
    return {
        "schema":"motif.meta004.nonlocal-finite-basin-certificate.v1",
        "terminal":1,"terminal_absorbing_by_program_semantics":True,
        "training_start_range":[2,train_max],
        "heldout_start_range":[train_max+1,heldout_max],
        "finite_basin_nodes":len(distances),
        "train_basin_nodes_including_terminal":training_size,
        "all_transitions_closed_in_exact_finite_basin":True,
        "nonlocal_rank_kind":"EXACT_DISTANCE_TO_TERMINAL_ON_VERIFIED_SOURCE_GRAPH",
        "source_ranking_witnesses":[
            {"n":n,"next":edges[n],"rank":distances[n],
             "next_rank":distances[edges[n]]}
            for n in sorted(edges)
        ],
        "all_source_starts_and_proof_reuse":traces,
        "max_verified_rank":max(distances.values()),
        "max_integer_encountered_in_finite_basin":max(distances),
        "train_new_transition_queries":train_new,
        "heldout_new_transition_queries":heldout_new,
        "total_unique_source_transition_queries":source_calls,
        "naive_unmemoized_all_starts_transition_queries":naive_total,
        "source_queries_avoided_vs_unmemoized_baseline":naive_total-source_calls,
        "strong_classical_memoization_exact_tie":True,
        "this_does_not_supply_a_total_rank_on_all_positive_integers":True,
        "this_does_not_prove_collatz":True,
    }


def investigate():
    words=enumerate_periodic_grammar()
    ghosts=ghost_branches()
    basin=build_finite_nonlocal_basin()
    if words["classifications"]!={"NEGATIVE_INTEGER_GHOST":14,
           "NONINTEGER_RATIONAL_TWO_ADIC_GHOST":480,
           "POSITIVE_INTEGER":8,"ZERO_NOT_POSITIVE":8}:
        raise HOLD("Original 2-adic periodic word grammar drift")
    if (basin["finite_basin_nodes"]!=800 or
        basin["total_unique_source_transition_queries"]!=799):
        raise HOLD("Original bounded nonlocal rank scope changed")
    result={
        "schema":SCHEMA,
        "question":"Can a nonlocal or infinite-state progress representation "
                   "distinguish a true positive Collatz counterexample from "
                   "an unresolved 2-adic parity ghost?",
        "global_collatz_status":CONJECTURE_STATUS,
        "representation_shift":"FROM_FINITE_PARITY_CYLINDERS_TO_EXACT_TWO_ADIC_BOUNDARY_AND_CLOSED_FINITE_RANK",
        "original_external_math_reference":REFERENCE,
        "exact_periodic_two_adic_program_enumeration":words,
        "ghost_positive_boundary":ghosts,
        "genuine_nonlocal_closed_finite_ranking":basin,
        "next_unanswered_question":
            "Can a well-founded ranking cover an infinite class of positive "
            "integer trajectories with verified closure, rather than only "
            "a source-replayed finite basin, while separating 2-adic "
            "nonordinary limit paths from natural-number orbits?",
        "what_was_falsified":
            "Every nested family of nonempty unresolved finite 2-adic "
            "residue cylinders necessarily contains a common positive integer.",
        "counterexample_to_false_topological_inference":
            "Cylinders n=-1 mod 2**k are nonempty in positive integers "
            "for each finite k, but their entire intersection in Z_2 "
            "is the negative integer -1, not a positive integer.",
        "open_limitations":BOUNDARY,
        "human_supplied_grammar_and_source_budget":True,
        "equal_information_classical_strong_baseline_tied":True,
        "no_historically_novel_mathematics_claimed":True,
        "no_unrestricted_operator_invention_claimed":True,
        "automatic_admission":False,"installed":False,
        "external_authority":"NONE",
    }
    result["integrity_digest"]=digest(result)
    return result


def verify_packet(packet):
    if type(packet) is not dict or packet.get("schema")!=SCHEMA:
        raise HOLD("Unknown nonlocal 2-adic proof packet")
    if packet.get("integrity_digest")!=digest({
        k:v for k,v in packet.items() if k!="integrity_digest"
    }):
        raise HOLD("Source packet checksum mismatch")
    if packet!=investigate():
        raise HOLD("Rehashed altered proof, ghost, source rank, or authority label rejected")
    return True


def reenter(packet):
    verify_packet(packet)
    return {
        "status":"TWO_ADIC_LIMIT_AND_NONLOCAL_FINITE_RANK_REVERIFIED",
        "new_investigative_source_questions":0,
        "complete_transition_and_symbolic_source_replay":True,
        "collatz_global_proof":False,
        "source_digest":packet["integrity_digest"],
    }


if __name__=="__main__":
    print(json.dumps(investigate(),indent=2,sort_keys=True))
