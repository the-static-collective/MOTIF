"""LEGIT-015 independent conventional decision-theory reference.

The optimized MOTIF model must NOT claim novelty over classical mathematics:
Bellman dynamic programming and exact stochastic recurrences are standard.
This separately implemented enumerator does not import the MOTIF state
transition or policy solver. It recomputes every affordable action and
success/failure branch from the raw scenario fields, with exact fractions.

For short horizons it uses exhaustive policy-tree recursion WITHOUT any
shared implementation and WITHOUT memoization, providing a strong oracle.
A separate memoized conventional comparator supports larger horizons.
"""
from __future__ import annotations

from fractions import Fraction
from functools import lru_cache

def _choices(scenario,raw):
    turn,cash,rate,attempted,successful=raw
    if turn>=scenario.horizon:return ()
    names={x.name:i for i,x in enumerate(scenario.investments)}
    out=["WORK"]
    for i,a in enumerate(scenario.investments):
        if attempted&(1<<i):continue
        if a.cost>cash:continue
        if any(not (successful & (1<<names[p])) for p in a.requires):
            continue
        out.append(a.name)
    return tuple(out)

def _outcomes(scenario,raw,choice):
    t,c,p,tried,success=raw
    if choice=="WORK":
        return [(Fraction(1),p,(t+1,min(scenario.capital_cap,c+p),p,tried,success))]
    j=next(k for k,a in enumerate(scenario.investments) if a.name==choice)
    a=scenario.investments[j]
    paid=c-a.cost
    mask=tried|(1<<j)
    chance=Fraction(a.numerator,a.denominator)
    branches=[]
    if chance:
        branches.append((chance,0,(
            t+1,paid,min(scenario.power_cap,p*a.factor),mask,success|(1<<j))))
    if chance<1:
        branches.append((1-chance,0,(t+1,paid,p,mask,success)))
    return branches

def tree_optimal(scenario,raw=None):
    """Actual nonmemoized exhaustive expectation over all policy branches."""
    if scenario.horizon>7 or len(scenario.investments)>3:
        raise ValueError("Reference tree bounds exceeded")
    if raw is None:
        raw=(0,scenario.capital,scenario.power,0,0)
    if raw[0]==scenario.horizon:
        return Fraction(0),None
    options={}
    for action in _choices(scenario,raw):
        options[action]=sum(
            p*(gain+tree_optimal(scenario,new)[0])
            for p,gain,new in _outcomes(scenario,raw,action))
    choice=max(options,key=lambda a:(options[a],a=="WORK",-len(a),a))
    return options[choice],choice

def classical_optimal(scenario):
    """Separate conventional optimal expected-value DP; independent code."""
    @lru_cache(None)
    def recurse(raw):
        if raw[0]>=scenario.horizon:
            return Fraction(0)
        return max(sum(prob*(earned+recurse(nxt))
                       for prob,earned,nxt in _outcomes(scenario,raw,act))
                   for act in _choices(scenario,raw))
    return recurse((0,scenario.capital,scenario.power,0,0))

def one_step_action_values(scenario):
    """Independent first-move optimum for falsifying opportunity cost."""
    start=(0,scenario.capital,scenario.power,0,0)
    @lru_cache(None)
    def recurse(raw):
        if raw[0]>=scenario.horizon:return Fraction(0)
        return max(sum(pr*(u+recurse(nxt))
                       for pr,u,nxt in _outcomes(scenario,raw,a))
                   for a in _choices(scenario,raw))
    return {
        a:sum(pr*(u+recurse(nxt))
              for pr,u,nxt in _outcomes(scenario,start,a))
        for a in _choices(scenario,start)
    }

def no_reinvestment(scenario):
    """A strong guarantee: WORK-only returns exactly rate * horizon."""
    return Fraction(scenario.power*scenario.horizon)
