"""META-001 — ask a genuinely OPEN mathematical question, don't fake an answer.

Open question: Does every positive integer reach 1 under the Collatz map?
This code cannot solve it. It synthesizes bounded *new question types*:
  (i) residue-conditioned symbolic k-step maps from primitive arithmetic,
  (ii) universal (infinite arithmetic progression) local descent certificates,
  (iii) new questions targeting the still-unresolved residue classes.

All old/current literature references are research context, not source-owner
oracles. An arithmetic identity about a residue class is NOT a Collatz proof.

Inspired by the independent-source proof weave in COLLECTIVE-001..005.
"""
from __future__ import annotations

from collections import Counter
from copy import deepcopy
from hashlib import sha256
import json
from math import gcd

SCHEMA = "motif.meta001.collatz-open-problem.v1"
CLAIM = "Does every positive integer eventually reach 1 under n/2 if even, 3n+1 if odd?"
REFERENCES = [
    {
        "kind":"published_partial_result",
        "name":"David Barina, Improved verification limit for the convergence of the Collatz conjecture",
        "date":"2025-05-02",
        "doi":"10.1007/s11227-025-07337-0",
        "claim":"All starting integers below 2**71 computationally verified (2025 result)",
        "not_a_global_proof":True,
    },
    {
        "kind":"published_partial_result",
        "name":"Terence Tao, Almost all orbits of the Collatz map attain almost bounded values",
        "year":2022,
        "identifier":"arXiv:1909.03562",
        "claim":"An almost-everywhere logarithmic-density result, not every integer",
        "not_a_global_proof":True,
    },
    {
        "kind":"maintained_project_status",
        "name":"David Barina computational verification project",
        "url":"https://pcbarina.fit.vut.cz/",
        "claim":"Project independently verified well beyond billions of starts",
        "not_a_global_proof":True,
    },
]
PRIMITIVES = [
    "IS_ODD", "MULTIPLY_BY_THREE", "ADD_ONE", "EXACT_HALF",
    "COMPOSE_AFFINE_BRANCH", "REFINE_RESIDUE_MOD_POWER_OF_TWO",
    "COMPARE_AFFINE_WITH_IDENTITY", "QUANTIFY_ALL_IN_RESIDUE_CLASS"
]
HARD_LIMIT = 12


class HOLD(ValueError):
    pass


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False)


def digest(value):
    return sha256(canonical(value).encode()).hexdigest()


def T(n):
    """Accelerated Collatz, odd branch combines 3n+1 then one halving."""
    if type(n) is not int or n < 1:
        raise HOLD("Positive integer input only")
    return (3*n + 1)//2 if (n & 1) else n//2


def C(n):
    """Independent original (unaccelerated) Collatz step."""
    if type(n) is not int or n < 1:
        raise HOLD("Positive integer input only")
    return 3*n+1 if n%2 else n//2


def reference_T(n):
    """Second independent implementation: one OR two original C steps."""
    if type(n) is not int or n < 1:
        raise HOLD("Positive integer input only")
    return C(C(n)) if n%2 else C(n)


def certificate(k, residue):
    """Derive all-n symbolic T**k formula on n mod 2**k.

    After j branch steps value is (a*n+b)/2**j. The parity of
    that value is fixed across the residue class because, for j<k,
    replacing n with n+2**k changes the value by a*2**(k-j),
    an even integer. This is a constructive induction certificate.
    """
    if type(k) is not int or not 1 <= k <= HARD_LIMIT:
        raise HOLD("Unbounded residue proof depth")
    m=1<<k
    if type(residue) is not int or not 0 <= residue < m:
        raise HOLD("Residue is outside exact power-of-two scope")
    a,b,d=1,0,1
    branches=[]
    for j in range(k):
        numerator=a*residue+b
        if numerator%d:
            raise HOLD("Symbolic transition not integral on representative")
        representative=numerator//d
        is_odd=bool(representative%2)
        if (a*(1<<k))%(d*2) != 0:
            raise HOLD("Current branch parity is not uniform on residue class")
        old_a,old_b,old_d=a,b,d
        if is_odd:
            a,b,d=3*a,3*b+d,2*d
        else:
            d*=2
        branches.append({
            "step":j+1, "parity":"ODD" if is_odd else "EVEN",
            "input_affine":[old_a,old_b,old_d],
            "output_affine":[a,b,d],
        })
    if d!=m or a!=3**sum(z["parity"]=="ODD" for z in branches) or b<0:
        raise HOLD("Affine branch grammar lost its invariant")
    # Strict-descent condition T**k(n)<n iff (d-a)*n > b.
    if a < d:
        first_positive=residue if residue else m
        first_gt_one=first_positive if first_positive>1 else first_positive+m
        bound=b//(d-a)
        first_certified=first_gt_one
        if first_certified<=bound:
            first_certified += ((bound-first_certified)//m + 1)*m
        all_n_gt_one=first_certified==first_gt_one
        classification="UNIFORM_STRICT_DESCENT_N_GT_ONE" if all_n_gt_one else (
            "EVENTUAL_STRICT_DESCENT_ABOVE_THRESHOLD"
        )
    else:
        first_certified=None
        all_n_gt_one=False
        classification="NO_STRICT_DESCENT_AT_THIS_FIXED_DEPTH_FOR_CLASS"
    return {
        "schema":"motif.meta001.residue-affine-proof.v1",
        "k":k,"modulus":m,"residue":residue,
        "step_operator":"T_EVEN_HALF_ODD_3N_PLUS_1_HALF",
        "branch_history":branches,
        "symbolic_affine": {"a":a,"b":b,"denominator":d},
        "strict_descent_inequality":f"({d}-{a})*n > {b}",
        "classification":classification,
        "first_certified_n_gt_one":first_certified,
        "uniform_for_every_n_gt_one_in_class":all_n_gt_one,
        "quantification_scope":"ALL_POSITIVE_INTEGERS_IN_DECLARED_RESIDUE_CLASS",
        "global_collatz_conjecture_proven":False,
        "proof_method":"EXACT_MODULAR_PARITY_INDUCTION_AND_AFFINE_INEQUALITY",
    }


def independent_classical_certificate(k, r):
    """Separate algebra by following the parity pattern with rational affine
    transforms; integers and fractions, no use of symbolic branch_history."""
    from fractions import Fraction
    if not (type(k) is int and 1<=k<=HARD_LIMIT and
            type(r) is int and 0<=r<1<<k):
        raise HOLD("Invalid classical problem")
    a=Fraction(1); b=Fraction(0)
    m=1<<k
    for _ in range(k):
        v=a*r+b
        if v.denominator!=1:
            raise HOLD("Bad exact fraction parity")
        if v.numerator%2:
            a,b=3*a/2,(3*b+1)/2
        else:
            a,b=a/2,b/2
    return {"a":a.numerator*m//a.denominator,
            "b":b.numerator*m//b.denominator,
            "denominator":m}


def verify_certificate(card):
    """Rebuild the whole structural proof, not just its SHA256."""
    if type(card) is not dict or card.get("schema")!="motif.meta001.residue-affine-proof.v1":
        raise HOLD("Unknown residue certificate")
    derived=certificate(card["k"],card["residue"])
    if card!=derived:
        raise HOLD("Rehashed residue, parity branch or descent claim differs")
    ref=independent_classical_certificate(card["k"],card["residue"])
    if card["symbolic_affine"]!=ref:
        raise HOLD("Independent fraction algebra disagrees")
    # Stress test witnesses; these *checks* are not the universal proof.
    m=card["modulus"]
    r=card["residue"]
    for extra in (0,1,2,3,7,13):
        n=r+extra*m
        if n<1:
            continue
        observed=n
        for _ in range(card["k"]):
            observed=reference_T(observed)
        a,b,d=(card["symbolic_affine"][x] for x in ("a","b","denominator"))
        if observed*d!=a*n+b:
            raise HOLD("Exact finite experiment contradicts symbolic certificate")
        guaranteed=(card["first_certified_n_gt_one"] is not None
                    and n>=card["first_certified_n_gt_one"] and n>1)
        if guaranteed and not observed<n:
            raise HOLD("Universal descent claim has a counterexample")
    return True


class FiniteSourceOwner:
    """No independent authorship; local deterministic source-owner callback."""
    def __init__(self,revision=1):
        if type(revision) is not int or revision<1:
            raise HOLD("Source version invalid")
        self.revision=revision
        self.questions=0
        self.rechecks=0

    def contract(self):
        return {"source_kind":"LOCAL_FINITE_ARITHMETIC_FIXTURE",
                "revision":self.revision,
                "source_authentication":"NOT_AUTHENTICATED",
                "does_not_establish_open_conjecture":True,
                "external_authority":"NONE"}

    def ask(self,start,limit=1200):
        if type(start) is not int or not 1<=start<2**21:
            raise HOLD("Finite source survey bound exceeded")
        if type(limit) is not int or not 1<=limit<=4000:
            raise HOLD("Finite source trajectory limit exceeded")
        self.questions+=1
        trace=[start];seen={start}
        while trace[-1]!=1 and len(trace)-1<limit:
            nxt=T(trace[-1])
            trace.append(nxt)
            if nxt in seen:
                break
            seen.add(nxt)
        status="REACHED_ONE" if trace[-1]==1 else (
            "FOUND_REPEATED_STATE_NEEDS_REVIEW" if trace[-1] in trace[:-1] else
            "HOLD_TRAJECTORY_BUDGET"
        )
        result={
            "schema":"motif.meta001.finite-orbit-evidence.v1",
            "contract":self.contract(),"start":start,
            "step_limit":limit,"trace":trace,
            "status":status,
            "global_conjecture_proved":False,
        }
        result["integrity_digest"]=digest(result)
        return result

    def recheck(self,receipt):
        self.rechecks+=1
        if type(receipt) is not dict or set(receipt)!={
            "schema","contract","start","step_limit","trace","status",
            "global_conjecture_proved","integrity_digest"
        }:
            raise HOLD("Missing finite-source receipt fields")
        if receipt["integrity_digest"]!=digest({
            k:v for k,v in receipt.items() if k!="integrity_digest"
        }):
            raise HOLD("Finite-source record altered")
        if (receipt["schema"]!="motif.meta001.finite-orbit-evidence.v1"
            or receipt["contract"]!=self.contract()
            or receipt["global_conjecture_proved"] is not False
            or type(receipt["start"]) is not int
            or type(receipt["trace"]) is not list
            or not receipt["trace"] or receipt["trace"][0]!=receipt["start"]
            or type(receipt["step_limit"]) is not int
            or len(receipt["trace"])-1>receipt["step_limit"]
            or any(type(n) is not int or n<1 for n in receipt["trace"])):
            raise HOLD("Bad finite-source scope or unsupported authority")
        for before,after in zip(receipt["trace"],receipt["trace"][1:]):
            if reference_T(before)!=after:
                raise HOLD("Independently replayed Collatz step disagrees")
        actual_status=("REACHED_ONE" if receipt["trace"][-1]==1
                       else "FOUND_REPEATED_STATE_NEEDS_REVIEW"
                       if receipt["trace"][-1] in receipt["trace"][:-1]
                       else "HOLD_TRAJECTORY_BUDGET")
        if receipt["status"]!=actual_status:
            raise HOLD("Claimed terminal status unsupported")
        if actual_status=="REACHED_ONE" and 1 in receipt["trace"][:-1]:
            raise HOLD("Source continued after terminal 1")
        if actual_status=="HOLD_TRAJECTORY_BUDGET" and (
            len(receipt["trace"])-1!=receipt["step_limit"]
        ):
            raise HOLD("Source claimed budget exhaustion prematurely")
        return True


def investigate_open_problem(*,max_k=9,finite_n=8192):
    """Ask the genuinely open question; answer only what bounded evidence proves."""
    if type(max_k) is not int or not 2<=max_k<=HARD_LIMIT:
        raise HOLD("Unbounded question-language growth")
    if type(finite_n) is not int or not 1<=finite_n<=20000:
        raise HOLD("Finite survey range outside research contract")
    # ACTUAL counterexample to wrong proposed shortcut: every step decreases.
    naive={"question":"Is T(n)<n for every integer n>1?",
           "claim":"ALL_POSITIVE_N_GT_ONE_DESCEND_IN_ONE_T_STEP",
           "counterexample":{"n":3,"T_n":T(3)},
           "result":"REFUTED_BY_EXACT_COUNTEREXAMPLE",
           "conjecture_original_question_not_refuted":True}
    if naive["counterexample"]["T_n"]<=3:
        raise HOLD("Missing counterexample to naive method")

    # Generate new question type: modular-conditioned universal descent
    # certificate. This differs qualitatively from finite-orbit sampling.
    tree=[]
    for k in range(1,max_k+1):
        cards=[]
        for r in range(1<<k):
            card=certificate(k,r)
            verify_certificate(card)
            cards.append(card)
        counts=dict(sorted(Counter(x["classification"] for x in cards).items()))
        tree.append({
            "k":k,"modulus":1<<k,
            "source_question":f"Which residue classes mod 2**{k} rigorously "
                              f"descend after exactly {k} T steps?",
            "all_residue_classes_exhausted":True,
            "classification_counts":counts,
            "guaranteed_eventual_descent_class_count":sum(
                x["first_certified_n_gt_one"] is not None for x in cards
            ),
            "non_descent_at_this_fixed_depth_class_count":sum(
                x["first_certified_n_gt_one"] is None for x in cards
            ),
            "proof_cards":cards,
        })
    # Explicitly derive the known 1(mod4) infinite-family certificate:
    card=tree[1]["proof_cards"][1]
    if (card["symbolic_affine"]!={"a":3,"b":1,"denominator":4}
        or not card["uniform_for_every_n_gt_one_in_class"]):
        raise HOLD("The asserted local infinite-family lemma is not proven")

    owner=FiniteSourceOwner()
    receipts=[]
    for start in [1,3,5,7,27,97,871,6171,finite_n]:
        if start<=finite_n:
            rec=owner.ask(start,1200)
            owner.recheck(rec)
            receipts.append(rec)
    # Sampled finite sweeps are not novel: vastly stronger published bounds
    # already exist. Run classical reference and fail closed on disagreement.
    finite={"first":1,"last":finite_n,"saw_reach_one":0,
            "saw_hold":0,"max_T_steps":0,"max_T_steps_start":1}
    for n in range(1,finite_n+1):
        current=n
        t=0
        while current!=1 and t<1200:
            next_value=T(current)
            if next_value!=reference_T(current):
                raise HOLD("Finite source step disagrees with original Collatz")
            current=next_value
            t+=1
        if current==1:
            finite["saw_reach_one"]+=1
        else:
            finite["saw_hold"]+=1
        if t>finite["max_T_steps"]:
            finite["max_T_steps"]=t
            finite["max_T_steps_start"]=n

    result={
        "schema":SCHEMA,
        "question":CLAIM,
        "research_status":"OPEN_PROBLEM_GLOBAL_ANSWER_NOT_ESTABLISHED",
        "sources":REFERENCES,
        "known_public_prior_computation_exceeds_this_sweep":True,
        "user_directed_investigation":True,
        "counterexample_to_naive_question":naive,
        "question_primitive_library":PRIMITIVES,
        "meta_generated_question_type":
            "MODULAR_CONDITIONED_SYMBOLIC_K_STEP_STRICT_DESCENT_CERTIFICATE",
        "generated_research_question":"Which residue classes and observation "
            "depths provably exhibit local descent for infinitely many integers?",
        "globally_valid_but_restricted_lemma":{
            "statement":"For every n>1 with n = 1 (mod 4), T(T(n)) = (3n+1)/4 < n",
            "proof_card":card,
            "this_is_known_elementary_mathematics_not_novel":True,
            "this_does_not_prove_collatz":True,
        },
        "all_depths_and_proof_cards":tree,
        "finite_source_receipts":receipts,
        "finite_local_sweep":finite,
        "source_owner_contract":owner.contract(),
        "source_questions_asked":owner.questions,
        "next_unanswered_question":"Can one find a finite, rigorously proved "
           "descent certificate or an invariant for every remaining residue "
           "class without assuming random independence of parity trajectories?",
        "next_question_automatically_marked_unresolved":True,
        "why_open_problem_still_unanswered":[
            "Each finite k leaves classes with no fixed-depth descent proof",
            "Certifying infinitely many members of one residue class does not cover all positive integers",
            "Finite orbit checks never prove the universal quantified claim",
            "Published computation and almost-everywhere results do not solve every starting integer",
        ],
        "no_new_mathematical_theorem_claimed":True,
        "no_general_meta_primitive_invention_claimed":True,
        "no_real_external_agent_or_source_identity_authentication":True,
        "automatic_admission":False,"installed":False,
        "external_authority":"NONE",
    }
    result["integrity_digest"]=digest(result)
    return result


def verify_packet(packet):
    if type(packet) is not dict or packet.get("schema")!=SCHEMA:
        raise HOLD("Unknown open mathematics packet")
    if packet["integrity_digest"]!=digest({
        k:v for k,v in packet.items() if k!="integrity_digest"
    }):
        raise HOLD("Record checksum altered")
    # Independent reproduction from original math—not trusting checksum:
    fresh=investigate_open_problem(
        max_k=len(packet["all_depths_and_proof_cards"]),
        finite_n=packet["finite_local_sweep"]["last"]
    )
    if packet != fresh:
        raise HOLD("Proposed local proof, graph, question or global claim cannot be replayed")
    return True


def reenter(packet):
    verify_packet(packet)
    return {"status":"OPEN_QUESTION_PARTIAL_PROOFS_REVERIFIED",
            "new_investigative_questions":0,
            "symbolic_and_finite_proofs_recomputed":True,
            "global_answer_available":False,
            "answer_packet_digest":packet["integrity_digest"]}


if __name__=="__main__":
    print(json.dumps(investigate_open_problem(),indent=2,sort_keys=True))
