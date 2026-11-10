"""LEGIT-027 — two intentionally different, finitely verified question domains.

Polynomial identity REFUTATION: a modular evaluation with unequal residues
is an exact witness to different integer polynomials. Equal residues do
NOT establish identity.

Bounded integer constraint EQUIVALENCE REFUTATION: an assignment with
different satisfiability outcomes is an exact witness. Equal outcomes
do NOT establish equivalent constraints.

Every case is engineer-generated, selected to defeat two cheap probes.
Future seeds are separate, but not externally authored or blind.
"""
from __future__ import annotations

from functools import lru_cache
from itertools import product
from random import Random

TRAIN_SEEDS = (27011, 27012)
FUTURE_SEEDS = (27013, 27014)
PER_WORLD = 16
DOMAINS = ("polynomial_modular_witness", "integer_constraint_countermodel")
PRIMES = (2, 3, 5, 7, 11)
POLY_X = (-3, -2, -1, 0, 1, 2, 3)
MAX_COEFF = 400

class Hold(ValueError):
    pass


def questions(domain):
    if domain == DOMAINS[0]:
        # Keep the old failed probes first in the fixed canonical baseline.
        return tuple([(0,2),(1,2)] + [(x,p) for p in PRIMES for x in POLY_X
                                      if (x,p) not in ((0,2),(1,2))])
    if domain == DOMAINS[1]:
        return tuple([(0,0),(5,5)] + [(x,y) for x in range(6)
                                      for y in range(6)
                                      if (x,y) not in ((0,0),(5,5))])
    raise Hold("unknown task domain")


def _mul(a,b):
    out=[0]*(len(a)+len(b)-1)
    for i,c in enumerate(a):
        for j,d in enumerate(b):
            out[i+j]+=c*d
    return out


def polynomial_value(coeff,x):
    """Horner implementation for candidate observations."""
    total=0
    for c in reversed(coeff):
        total=total*x+c
    return total


def independent_polynomial_value(coeff,x):
    """Different implementation for final verification."""
    return sum(c*(x**i) for i,c in enumerate(coeff))


def valid_poly(case):
    for poly in case["objects"]:
        if not isinstance(poly,tuple) or len(poly)!=4 or any(
                type(c) is not int or abs(c)>MAX_COEFF for c in poly):
            raise Hold("invalid polynomial task")
    return True


def _random_poly(rng):
    base=tuple(rng.randint(-4,4) for _ in range(4))
    roots=(0,1,rng.choice((-3,-2,-1,2,3)))
    factor=rng.choice((1,2,3,5,6,10,14,15,21,35,55,77))
    diff=_mul(_mul(_mul((0,1),(-1,1)),(-roots[2],1)),(factor,))
    partner=tuple(a+b for a,b in zip(base,diff))
    case={"objects":(base,partner),"roots":roots,"factor":factor}
    valid_poly(case)
    if polynomial_value(base,0)!=polynomial_value(partner,0) or (
        polynomial_value(base,1)!=polynomial_value(partner,1)):
        raise Hold("engineered old probe collision failed")
    return case


def _row(rng):
    a,b=rng.choice((-2,-1,0,1,2)),rng.choice((-2,-1,0,1,2))
    if a==b==0:
        a=1
    vals=sorted({a*x+b*y for x in range(6) for y in range(6)})
    if len(vals)<3:
        raise Hold("insufficient constraint row diversity")
    cutoff=rng.choice(vals[1:-1])
    return (a,b,cutoff)


def constraint_value(formula,assignment):
    """Candidate interpreter: conjunction of <= linear inequalities."""
    x,y=assignment
    return all(a*x+b*y <= limit for a,b,limit in formula)


def independent_constraint_value(formula,assignment):
    """Oracle independently enumerates and aggregates violations."""
    for a,b,limit in formula:
        if (a*assignment[0]+b*assignment[1]-limit)>0:
            return False
    return True


def _random_constraint(rng):
    first=_row(rng)
    second=_row(rng)
    # Modify exactly one linear-constraint boundary.
    delta=rng.choice((-1,1))
    change=(first[0],first[1],first[2]+delta)
    left=(first,second)
    right=(change,second)
    return {"objects":(left,right),"modified_bound_by":delta}


def observe(domain,case,question):
    """Two actual candidate object-observations, not a proof by itself."""
    a,b=case["objects"]
    if domain == DOMAINS[0]:
        valid_poly(case)
        x,p=question
        if (x,p) not in questions(domain):
            raise Hold("unregistered modular question")
        return polynomial_value(a,x)%p,polynomial_value(b,x)%p
    if domain == DOMAINS[1]:
        if question not in questions(domain):
            raise Hold("unregistered integer assignment")
        return constraint_value(a,question),constraint_value(b,question)
    raise Hold("unknown domain")


def independent_observe(domain,case,question):
    a,b=case["objects"]
    if domain == DOMAINS[0]:
        x,p=question
        return (independent_polynomial_value(a,x)%p,
                independent_polynomial_value(b,x)%p)
    if domain == DOMAINS[1]:
        return (independent_constraint_value(a,question),
                independent_constraint_value(b,question))
    raise Hold("unknown domain")


def oracle_nonidentical(domain,case):
    """Exact independent finite/coeff test, not an inspection by the planner."""
    a,b=case["objects"]
    if domain == DOMAINS[0]:
        valid_poly(case)
        return a!=b
    if domain == DOMAINS[1]:
        return any(independent_constraint_value(a,q)!=
                   independent_constraint_value(b,q) for q in questions(domain))
    raise Hold("unknown domain")


@lru_cache(maxsize=16)
def world(domain,seed):
    if domain not in DOMAINS or seed not in TRAIN_SEEDS + FUTURE_SEEDS:
        raise Hold("unregistered world request")
    rng=Random(seed + 1_000_003*DOMAINS.index(domain))
    tasks=[]
    attempts=0
    while len(tasks)<PER_WORLD and attempts<50_000:
        attempts+=1
        case=_random_poly(rng) if domain==DOMAINS[0] else _random_constraint(rng)
        # Select only tasks for which old questions fail; ensure there
        # IS a valid witness in the candidate question vocabulary.
        # This witness-existence filtering is an engineer design choice.
        if any(observe(domain,case,q)[0]!=observe(domain,case,q)[1]
               for q in questions(domain)[:2]):
            continue
        if not oracle_nonidentical(domain,case):
            continue
        if not any(observe(domain,case,q)[0]!=observe(domain,case,q)[1]
                   for q in questions(domain)):
            continue
        tasks.append({"case_id":"%s_%d_%02d"%(domain,seed,len(tasks)),
                      "objects":case["objects"]})
    if len(tasks)!=PER_WORLD:
        raise Hold("not enough witnessed old-question blindspots")
    return tuple(tasks), {
        "domain":domain, "seed":seed,"case_count":len(tasks),
        "candidate_question_count":len(questions(domain)),
        "generator_attempts":attempts,
        "engineer_authored":True,
        "selection_conditioned_on_old_probe_failure":True,
        "candidate_witness_existence_checked_during_generation":True,
        "ranking_or_policy_not_selected_using_future_cases":True,
        "no_external_independent_task_administration":True
    }
