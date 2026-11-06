"""MOTIF LEGIT-015: finite compounding improvement economy.

Compounding here is *productive capacity reinvested into later improvements*.
An improvement consumes a finite decision period and scarce capital, and may
increase future productive output. That output can replenish the capital
needed to attempt another improvement. Later upgrades multiply existing
capacity, and a successful "research infrastructure" upgrade may unlock
otherwise unavailable downstream experiments.

This is a bounded ASSUMPTION MODEL, not a calibrated prediction or a live
self-improving program. Synthetic "improvement" probabilities and effects
MUST NOT be mistaken for measured MOTIF performance. LEGIT-014's empirical
rejection is integrated separately and never silently converted into
positive observed returns.

All arithmetic uses integer state and exact fractions. The Bellman plan
optimizes expected useful work, NOT credit accumulation for its own sake.
"""
from __future__ import annotations

from dataclasses import dataclass,replace
from functools import lru_cache
from fractions import Fraction
from typing import NamedTuple

MAX_HORIZON=10
MAX_CAPITAL=64
MAX_POWER=64
MAX_INVESTMENTS=5
MAX_RESEARCH_RATE=16

@dataclass(frozen=True)
class Improvement:
    name: str
    cost: int
    factor: int
    numerator: int=1
    denominator: int=1
    requires: tuple[str,...]=()
    research_factor: int=1  # success improves the ability to attempt later improvements

@dataclass(frozen=True)
class Economy:
    horizon: int
    capital: int
    power: int
    investments: tuple[Improvement,...]
    capital_cap: int=64
    power_cap: int=64

class State(NamedTuple):
    period: int
    capital: int
    power: int
    tried: int
    succeeded: int
    research_rate: int=1

class HOLD(ValueError):
    pass

def validate(e: Economy)->Economy:
    if type(e) is not Economy or not 1<=e.horizon<=MAX_HORIZON:
        raise HOLD("Unknown or unbounded improvement horizon")
    if not (type(e.capital) is int and type(e.power) is int and
            type(e.capital_cap) is int and type(e.power_cap) is int and
            0<=e.capital<=e.capital_cap<=MAX_CAPITAL and
            1<=e.power<=e.power_cap<=MAX_POWER):
        raise HOLD("Invalid finite work/capital budget")
    if type(e.investments) is not tuple or len(e.investments)>MAX_INVESTMENTS:
        raise HOLD("Too many available interventions")
    names=[a.name for a in e.investments]
    if len(set(names))!=len(names) or "WORK" in names:
        raise HOLD("Conflicting action names")
    for a in e.investments:
        if (type(a) is not Improvement or
            not isinstance(a.name,str) or not a.name.isidentifier()
            or a.name.startswith("_") or a.name.upper()!=a.name
            or type(a.cost) is not int or not 1<=a.cost<=MAX_CAPITAL
            or type(a.factor) is not int or not 1<=a.factor<=4
            or type(a.research_factor) is not int or not 1<=a.research_factor<=4
            or type(a.numerator) is not int or type(a.denominator) is not int
            or not 0<=a.numerator<=a.denominator<=100 or
            a.denominator<1 or type(a.requires) is not tuple or
            len(set(a.requires))!=len(a.requires) or
            any(p not in names or p==a.name for p in a.requires)):
            raise HOLD("Improvement is not a typed synthetic action")
    # A success-only dependency must be acyclic, not an impossible circuit.
    depends={a.name:a.requires for a in e.investments}
    visiting=set()
    done=set()
    def visit(name):
        if name in visiting:raise HOLD("Cyclic capability dependency")
        if name in done:return
        visiting.add(name)
        for p in depends[name]:visit(p)
        visiting.remove(name)
        done.add(name)
    for name in names:visit(name)
    return e

def _legal(e,state):
    if state.period>=e.horizon:
        return ()
    ids={a.name:i for i,a in enumerate(e.investments)}
    available=["WORK"]
    for i,a in enumerate(e.investments):
        if (state.tried>>i)&1:continue
        if max(1,(a.cost+state.research_rate-1)//state.research_rate)>state.capital:continue
        if any(not((state.succeeded>>ids[p])&1) for p in a.requires):
            continue
        available.append(a.name)
    return tuple(available)

def transition(e,state,action):
    """(probability, next-state, immediate useful work) branches."""
    if state.period>=e.horizon:
        raise HOLD("Action after horizon")
    if action not in _legal(e,state):
        raise HOLD("Unavailable action or insufficient resources")
    if action=="WORK":
        nxt=State(state.period+1,
                  min(e.capital_cap,state.capital+state.power),
                  state.power,state.tried,state.succeeded,state.research_rate)
        return ((Fraction(1),nxt,Fraction(state.power)),)
    i=next(i for i,a in enumerate(e.investments) if a.name==action)
    a=e.investments[i]
    effective_cost=max(1,(a.cost+state.research_rate-1)//state.research_rate)
    base=State(state.period+1,state.capital-effective_cost,state.power,
               state.tried|(1<<i),state.succeeded,state.research_rate)
    p=Fraction(a.numerator,a.denominator)
    success=State(base.period,base.capital,
                  min(e.power_cap,base.power*a.factor),
                  base.tried,base.succeeded|(1<<i),
                  min(MAX_RESEARCH_RATE,base.research_rate*a.research_factor))
    if p==0:return ((Fraction(1),base,Fraction(0)),)
    if p==1:return ((Fraction(1),success,Fraction(0)),)
    return ((p,success,Fraction(0)),
            (1-p,base,Fraction(0)))

def initial(e):
    return State(0,e.capital,e.power,0,0)

def planner(e):
    e=validate(e)
    @lru_cache(None)
    def solve(state):
        if state.period==e.horizon:
            return Fraction(0),None
        values={}
        for action in _legal(e,state):
            values[action]=sum(
                p*(reward+solve(next_state)[0])
                for p,next_state,reward in transition(e,state,action)
            )
        # Equal value prefers useful work and then lexical order, never
        # unnecessary optimizer cycles just to gain "self improvement".
        choice=max(values,key=lambda a:(values[a],a=="WORK",-len(a),a))
        return values[choice],choice
    return solve

def action_values(e,state=None):
    e=validate(e)
    state=initial(e) if state is None else state
    if state.period>=e.horizon:return {}
    solve=planner(e)
    return {
        action:sum(p*(reward+solve(next_state)[0])
                   for p,next_state,reward in transition(e,state,action))
        for action in _legal(e,state)
    }

def evaluate(e):
    e=validate(e)
    solve=planner(e)
    state=initial(e)
    expected,first=solve(state)
    first_choices=action_values(e,state)
    work=first_choices["WORK"]
    lost_by_forcing_work=expected-work
    if lost_by_forcing_work<0:
        raise AssertionError("Bellman result less than a legal action")
    trace=[]
    while state.period<e.horizon:
        val,choice=solve(state)
        branches=transition(e,state,choice)
        # This is illustrative all-success branch only, not a promise.
        prob,next_state,reward=branches[0]
        trace.append({
            "period":state.period,"action":choice,
            "research_rate_before":state.research_rate,
            "research_rate_after":next_state.research_rate,
            "improvement_cash_cost_at_current_research_rate":(
                0 if choice=="WORK" else state.capital-next_state.capital),
            "capital_before":state.capital,
            "power_before":state.power,
            "success_branch_probability":str(prob),
            "success_branch_credit_after":next_state.capital,
            "success_branch_power_after":next_state.power,
            "immediate_work":str(reward),
            "expected_remaining_utility":str(val),
        })
        state=next_state
    return {
        "best_expected_useful_work":expected,
        "first_action":first,
        "action_values":first_choices,
        "baseline_work_only":Fraction(e.horizon*e.power),
        "gain_vs_never_invest":expected-e.horizon*e.power,
        "cost_of_forcing_work_before_improvement":lost_by_forcing_work,
        "success_path_only_not_expected_trajectory":trace,
        "bellman_states_evaluated":solve.cache_info().currsize,
    }

def independent_only(e,keep):
    """Counterfactual removal of opportunities, preserving initial budget.

    If dependencies become impossible, remove those actions too.
    These are *model comparisons*, not claims about observed causation.
    """
    validate(e)
    keep=set(keep)
    universe={a.name:a for a in e.investments}
    # Remove actions whose dependencies have themselves been removed.
    feasible=set(keep)
    changed=True
    while changed:
        changed=False
        for a in e.investments:
            if a.name in feasible and not all(p in feasible for p in a.requires):
                feasible.remove(a.name)
                changed=True
    filtered=tuple(a for a in e.investments if a.name in feasible)
    return replace(e,investments=filtered)

def interaction(e,a,b):
    """Synergy over optimal policies: V(AB)-V(A)-V(B)+V(empty).

    A positive number establishes superadditivity *in this scenario*,
    not universal exponential growth. The factor can also be negative.
    """
    validate(e)
    if a==b or a not in {x.name for x in e.investments} or b not in {
            x.name for x in e.investments}:
        raise HOLD("Unknown independent interaction candidates")
    base=evaluate(independent_only(e,[]))["best_expected_useful_work"]
    av=evaluate(independent_only(e,[a]))["best_expected_useful_work"]
    bv=evaluate(independent_only(e,[b]))["best_expected_useful_work"]
    ab=evaluate(independent_only(e,[a,b]))["best_expected_useful_work"]
    return {
        "base":base,"A_only":av,"B_only":bv,"both":ab,
        "net_synergy":ab-av-bv+base,
        "formula":"V(A,B) - V(A) - V(B) + V(no improvements)",
        "causation_not_observed":True,
    }

def sensitivity(e,name):
    """Assumption sensitivity, not an estimated probability distribution."""
    validate(e)
    indices={a.name:i for i,a in enumerate(e.investments)}
    if name not in indices:raise HOLD("Unknown hypothetical investment")
    output=[]
    for p,q in ((0,1),(1,4),(1,2),(3,4),(1,1)):
        altered=list(e.investments)
        altered[indices[name]]=replace(altered[indices[name]],
                                       numerator=p,denominator=q)
        trial=replace(e,investments=tuple(altered))
        result=evaluate(trial)
        output.append({"probability":str(Fraction(p,q)),
                       "best_expected_work":str(result["best_expected_useful_work"]),
                       "first_action":result["first_action"]})
    return output

def rational(x):
    return str(x) if isinstance(x,Fraction) else x
