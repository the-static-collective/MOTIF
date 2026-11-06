"""MOTIF-009 exact classical cost-sensitive active-question optimizer.

Finite Bayesian decision trees over four synthetic scene hypotheses. Entropy
is measured but is NOT the optimization target: the objective is expected
*decision loss including asking cost and cost of abstaining*. All numeric
values are declared experimental assumptions, not human outcomes.
"""
from __future__ import annotations
from fractions import Fraction
from math import log2
import json

WORLD_IDS=("LEFT_PARTIAL","RIGHT_PARTIAL","LEFT_FULL","RIGHT_FULL")
QUESTIONS={
 "ASK_START_SIDE":{
   "prompt":"Is the red crate initially LEFT or RIGHT of the blue wall?",
   "field":"side","tenths":1},
 "ASK_WALL_EXTENT":{
   "prompt":"Does the blue wall stretch from TOP to BOTTOM, blocking any detour?",
   "field":"wall_extent","tenths":3},
 "ASK_EXACT_SCENE":{
   "prompt":"Supply a complete independently verified scene description.",
   "field":"id","tenths":21},
}
ACTIONS=("DECLARE_UNREACHABLE","PLAN_LEFT_TO_RIGHT",
         "PLAN_RIGHT_TO_LEFT","HOLD_NO_ACTION")
class HOLD(ValueError):pass

def standard_costs():
    return {q:Fraction(spec["tenths"],10) for q,spec in QUESTIONS.items()}

def validate_inputs(worlds,weights,costs):
    if (len(worlds)!=4 or {w.get("id") for w in worlds}!=set(WORLD_IDS) or
        any(w.get("side") not in ("left","right") or
            w.get("wall_extent") not in ("partial","full") or
            w["id"]!=w["side"].upper()+"_"+w["wall_extent"].upper()
            for w in worlds)):
        raise HOLD("HOLD_DIFFERENT_PICTURE_FAMILY")
    if (set(weights)!=set(WORLD_IDS) or
        any(type(v) is not Fraction or v<0 for v in weights.values()) or
        sum(weights.values())<=0):
        raise HOLD("HOLD_INVALID_ASSUMED_PRIOR")
    if (set(costs)!=set(QUESTIONS) or
        any(type(v) is not Fraction or v<0 for v in costs.values())):
        raise HOLD("HOLD_INVALID_QUERY_COST_LEDGER")
    return True

def loss(action,world):
    if action=="HOLD_NO_ACTION":return Fraction(2)
    if action=="DECLARE_UNREACHABLE":
        return Fraction(0 if world["wall_extent"]=="full" else 5)
    if action=="PLAN_LEFT_TO_RIGHT":
        return Fraction(0 if world["side"]=="left" and
                        world["wall_extent"]=="partial" else 10)
    if action=="PLAN_RIGHT_TO_LEFT":
        return Fraction(0 if world["side"]=="right" and
                        world["wall_extent"]=="partial" else 10)
    raise HOLD("HOLD_UNKNOWN_SYNTHETIC_DECISION")

def outcome(q,world):
    if q not in QUESTIONS:raise HOLD("HOLD_UNSUPPORTED_QUESTION")
    return world[QUESTIONS[q]["field"]]

def mass(worlds,weights):
    s=sum(weights[w["id"]] for w in worlds)
    if s<=0:raise HOLD("HOLD_ZERO_PROBABILITY_SET")
    return s

def expected_terminal(action,worlds,weights):
    den=mass(worlds,weights)
    return sum(weights[w["id"]]*loss(action,w) for w in worlds)/den

def terminal(worlds,weights):
    options=[(expected_terminal(a,worlds,weights),i,a)
             for i,a in enumerate(ACTIONS)]
    score,_,action=min(options)
    return score,{"kind":"DECIDE","decision":action,"expected_loss":float(score)}

def split(q,worlds):
    out={}
    for w in worlds:out.setdefault(outcome(q,w),[]).append(w)
    return out

def optimal(worlds,weights,costs,depth,available=None):
    """Enumerate all valid question/stop choices; early stop is allowed."""
    if depth not in (0,1,2):raise HOLD("HOLD_MAX_TWO_QUESTIONS")
    if available is None:available=tuple(QUESTIONS)
    best_score,best=terminal(worlds,weights)
    if depth==0 or not available:return best_score,best
    den=mass(worlds,weights)
    for q in available:
        partitions=split(q,worlds)
        if len(partitions)<2:continue
        score=costs[q]
        branches={}
        for ans in sorted(partitions):
            group=partitions[ans]
            child_score,child=optimal(group,weights,costs,depth-1,
                    tuple(x for x in available if x!=q))
            probability=mass(group,weights)/den
            score+=probability*child_score
            branches[ans]={"probability":float(probability),"policy":child}
        if score<best_score:
            best_score=score
            best={"kind":"ASK","question_id":q,
                  "prompt":QUESTIONS[q]["prompt"],
                  "query_cost":float(costs[q]),
                  "expected_total_loss":float(score),
                  "answers_not_observed":True,
                  "branches":branches}
    return best_score,best

def entropy(numbers):
    den=sum(numbers)
    if not den:return 0.
    return -sum(float(v/den)*log2(float(v/den)) for v in numbers if v>0)

def gain(q,worlds,weights):
    h=entropy([weights[w["id"]] for w in worlds])
    den=mass(worlds,weights)
    return h-sum(float(mass(g,weights)/den)*
                  entropy([weights[w["id"]] for w in g])
                  for g in split(q,worlds).values())

def greedy_control(worlds,weights,costs):
    info={}
    for q in QUESTIONS:
        bit=gain(q,worlds,weights)
        price=costs[q]
        info[q]={"information_bits":round(bit,9),
                 "price_units":float(price),
                 "bits_per_cost":round(bit/float(price),9) if price>0 else
                      (float("inf") if bit else 0.)}
    best=max(QUESTIONS,key=lambda q:info[q]["bits_per_cost"])
    # Simplistic 1-query entropy/cost heuristic: always asks its chosen query.
    den=mass(worlds,weights)
    one=costs[best]+sum(mass(g,weights)/den*terminal(g,weights)[0]
                 for g in split(best,worlds).values())
    # The best SECOND decision question following the naive FIRST query.
    two=costs[best]+sum(
        mass(g,weights)/den*
        optimal(g,weights,costs,1,tuple(x for x in QUESTIONS if x!=best))[0]
        for g in split(best,worlds).values())
    return {"first_question":best,
       "first_question_sent":False,
       "information":info,
       "one_question_expected_loss":float(one),
       "two_question_expected_loss_if_heuristic_first":float(two),
       "ranks_bits_per_price_not_decision_regret":True}

def brute_control(worlds,weights,costs,depth):
    """Independent direct enumeration of root/child possible questions.

    Uses terminal losses directly and no optimal-policy recursion. This is
    a conventional exhaustive classical comparator (not a new AI method).
    """
    den=mass(worlds,weights)
    best=min(expected_terminal(a,worlds,weights) for a in ACTIONS)
    if depth==0:return best
    for q in QUESTIONS:
        first=split(q,worlds)
        if len(first)<2:continue
        total=costs[q]
        for group in first.values():
            sub=min(expected_terminal(a,group,weights) for a in ACTIONS)
            if depth>1:
                for q2 in QUESTIONS:
                    if q2==q:continue
                    subparts=split(q2,group)
                    if len(subparts)<2:continue
                    t=costs[q2]+sum(
                        mass(part,weights)/mass(group,weights)*
                        min(expected_terminal(a,part,weights) for a in ACTIONS)
                        for part in subparts.values())
                    sub=min(sub,t)
            total+=mass(group,weights)/den*sub
        best=min(best,total)
    return best

def replay(world,policy,costs):
    """Oracle is simulated from the hypothesized world, not an external answer."""
    node=policy;spent=Fraction(0);responses=[]
    while node["kind"]=="ASK":
        q=node["question_id"];ans=outcome(q,world)
        spent+=costs[q]
        responses.append({"question":q,"synthetic_oracle_answer":ans,
          "human_observation_received":False})
        node=node["branches"][ans]["policy"]
    return {"world":world["id"],"simulated_answers_only":True,
       "hypothetical_answers":responses,
       "hypothetical_decision":node["decision"],
       "question_spend":float(spent),
       "regret":float(loss(node["decision"],world)),
       "total_loss":float(spent+loss(node["decision"],world)),
       "actual_action_executed":False}

def analyze(worlds,weights,costs):
    validate_inputs(worlds,weights,costs)
    values=[optimal(worlds,weights,costs,n) for n in (0,1,2)]
    control=[brute_control(worlds,weights,costs,n) for n in (0,1,2)]
    if any(a[0]!=b for a,b in zip(values,control)):
        raise HOLD("HOLD_EXACT_SEARCH_DISAGREES_WITH_CLASSICAL_ENUMERATOR")
    score0,p0=values[0];score1,p1=values[1];score2,p2=values[2]
    if not score2<=score1<=score0:
        raise HOLD("HOLD_ASK_MORE_BUDGET_WORSENED_BEST_POLICY")
    den=mass(worlds,weights)
    cases=[replay(w,p2,costs) for w in worlds]
    actual=sum(weights[x["world"]]/den*
        Fraction(str(x["total_loss"])) for x in cases)
    if abs(float(actual-score2))>1e-10:
        raise HOLD("HOLD_SIMULATED_ORACLE_REPLAY_MISMATCH")
    greedy=greedy_control(worlds,weights,costs)
    return {
      "cost_model":{
        "scope":"SUBJECTIVE_SYNTHETIC_LOSS_UNITS",
        "hold_no_action_loss":2,
        "false_unreachable_claim_loss":5,
        "invalid_route_loss":10,
        "query_prices":{q:float(costs[q]) for q in QUESTIONS},
        "prior_probability":{w:float(weights[w]/den) for w in WORLD_IDS},
        "real_world_calibrated":False,
      },
      "questions":{q:{
        "prompt":d["prompt"],"unknown_attribute":d["field"],
        "simulated_cost":float(costs[q]),"human_answer_received":False
        } for q,d in QUESTIONS.items()},
      "zero_question_expected_loss":float(score0),
      "one_question_expected_loss":float(score1),
      "two_question_expected_loss":float(score2),
      "inaction_expected_loss":2.,
      "value_of_two_questions_vs_best_no_query":float(score0-score2),
      "cost_of_inaction_vs_two_questions":float(Fraction(2)-score2),
      "zero_question_policy":p0,
      "one_question_policy":p1,
      "two_question_policy":p2,
      "entropy_greedy":greedy,
      "classical_brute_control":{
        "no_query_loss":float(control[0]),
        "one_query_loss":float(control[1]),
        "two_query_loss":float(control[2]),
        "algorithmic_superiority_claimed":False,
      },
      "synthetic_oracle_replay":cases,
      "maximum_question_depth":2,
      "query_dispatched":False,
      "actual_hypothesis_identified":False,
    }
