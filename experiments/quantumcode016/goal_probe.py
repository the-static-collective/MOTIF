"""QC-016 — goal-dependent information dividend, not novelty for novelty's sake.

A candidate probe only matters if it can resolve a *currently missing goal
requirement* or establish a *goal-enabling capability*. Underlying predictions
stay hypotheses; evidence can support choosing to inspect, not certify future
success. High/unknown exposure, inaccessible paths and absent permission
never become actions. Pareto alternatives preserve ties instead of forcing
an invented probability or arbitrary total order.

No network requests, physical interventions, automated game movement or
authorization to contact people.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json

YES, NO, UNKNOWN="YES","NO","UNKNOWN"
VERDICTS=(
    "CANDIDATE_GOAL_PROBE",
    "HOLD_UNVERIFIED_ACCESS",
    "BLOCKED_PERMISSION_OR_HAZARD",
    "NOT_RELEVANT_TO_MISSING_GOAL",
    "GOAL_ALREADY_OBSERVED",
)
SOURCES=frozenset((
    "ACTUAL_GAME_SENSOR","CANONICAL_GAME_RULE",
    "ATTRIBUTED_HUMAN_REPORT","PROVISIONAL_MODEL",
    "RESEARCHER_FIXTURE",
))
EXPOSURES=frozenset(("LOW","MODERATE","HIGH"))
WORLD_SCOPES=frozenset(("GAME_ONLY","HUMAN_CONTEXT_UNVERIFIED"))


def seal(x):
    return sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()


@dataclass(frozen=True)
class Goal:
    id: str
    absent_facts: tuple[str,...]
    desired_capabilities: tuple[str,...]
    priority: int
    source_ref: str
    domain: str="GAME_ONLY"

    def validate(self):
        if (not self.id or not self.source_ref or self.domain not in WORLD_SCOPES
            or not 1<=self.priority<=3
            or not (self.absent_facts or self.desired_capabilities)
            or len(set(self.absent_facts))!=len(self.absent_facts)
            or len(set(self.desired_capabilities))!=len(self.desired_capabilities)):
            raise ValueError("Incomplete or invalid goal")


@dataclass(frozen=True)
class Probe:
    id: str
    action: str
    predicted_answers: tuple[str,...]
    predicted_enablers: tuple[str,...]
    step_cost: int
    resource_cost: int
    exposure: str
    permission: str
    reachable: str
    hazard_assessed: str
    source_kind: str
    source_ref: str
    domain: str="GAME_ONLY"

    def validate(self):
        if (not self.id or not self.action or not self.source_ref
            or self.source_kind not in SOURCES or
            self.domain not in WORLD_SCOPES
            or self.exposure not in EXPOSURES
            or any(x not in (YES,NO,UNKNOWN) for x in
                   (self.permission,self.reachable,self.hazard_assessed))
            or not isinstance(self.step_cost,int)
            or not isinstance(self.resource_cost,int)
            or self.step_cost<0 or self.resource_cost<0
            or not (self.predicted_answers or self.predicted_enablers)):
            raise ValueError("Malformed evidence-grounded probe")

    @property
    def pin(self):
        self.validate()
        return seal(self.__dict__)


@dataclass(frozen=True)
class ProbeVerdict:
    probe_id: str
    verdict: str
    matches: tuple[str,...]
    predicted_dividend: int
    step_cost: int
    resource_cost: int
    exposure_penalty: int
    evidence_ref: str
    receipt: str
    evidence_scope: str
    predicted_not_verified: bool=True
    automatically_executed: bool=False


def evaluate(goal:Goal,probe:Probe,known_facts=(),known_capabilities=()):
    goal.validate()
    probe.validate()
    if goal.domain!=probe.domain:
        raise ValueError("Cross-world analogy is not physical-world proof")
    already=set(known_facts)|set(known_capabilities)
    relevant=(set(goal.absent_facts)|set(goal.desired_capabilities))-already
    matches=tuple(sorted(relevant &
                         (set(probe.predicted_answers)|
                          set(probe.predicted_enablers))))
    if not relevant:
        status="GOAL_ALREADY_OBSERVED"
    elif not matches:
        status="NOT_RELEVANT_TO_MISSING_GOAL"
    elif (probe.permission==NO or probe.reachable==NO or
          probe.hazard_assessed==NO or probe.exposure=="HIGH"):
        status="BLOCKED_PERMISSION_OR_HAZARD"
    elif (probe.permission!=YES or probe.reachable!=YES or
          probe.hazard_assessed!=YES or
          (probe.source_kind in ("PROVISIONAL_MODEL",)
           and probe.exposure=="MODERATE")):
        status="HOLD_UNVERIFIED_ACCESS"
    else:
        status="CANDIDATE_GOAL_PROBE"
    # Deliberately transparent *ordinal* research utility, not a
    # probability of success, expert safety classification, or medical
    # valuation. The number is NOT offered as proven benefit.
    dividend=len(matches)*goal.priority
    return ProbeVerdict(
        probe.id,status,matches,dividend,probe.step_cost,
        probe.resource_cost,{"LOW":0,"MODERATE":1,"HIGH":3}[probe.exposure],
        probe.source_ref,probe.pin,probe.domain)


def dominates(a:ProbeVerdict,b:ProbeVerdict):
    """Pareto across relevance, expense and exposure; no forced uniqueness."""
    if a.verdict!=b.verdict or a.verdict!="CANDIDATE_GOAL_PROBE":
        return False
    inequalities=(
        a.predicted_dividend>=b.predicted_dividend,
        a.step_cost<=b.step_cost,
        a.resource_cost<=b.resource_cost,
        a.exposure_penalty<=b.exposure_penalty)
    return all(inequalities) and (
        a.predicted_dividend>b.predicted_dividend or
        a.step_cost<b.step_cost or a.resource_cost<b.resource_cost or
        a.exposure_penalty<b.exposure_penalty)


def select(goal,probes,known_facts=(),known_capabilities=()):
    candidates=[evaluate(goal,p,known_facts,known_capabilities)
                for p in probes]
    ready=[x for x in candidates if x.verdict=="CANDIDATE_GOAL_PROBE"]
    fiber=tuple(sorted((x for x in ready if not any(
        dominates(y,x) for y in ready if y.probe_id!=x.probe_id)),
        key=lambda v:(-v.predicted_dividend,v.step_cost,
                      v.resource_cost,v.probe_id)))
    return {
        "goal":goal.id,
        "goal_source":goal.source_ref,
        "pareto_candidate_ids":tuple(x.probe_id for x in fiber),
        "verdicts":tuple(candidates),
        "holds":tuple(x.probe_id for x in candidates if
                      x.verdict=="HOLD_UNVERIFIED_ACCESS"),
        "rejected":tuple(x.probe_id for x in candidates if
                         x.verdict in (
                             "NOT_RELEVANT_TO_MISSING_GOAL",
                             "BLOCKED_PERMISSION_OR_HAZARD")),
        "predictions_verified":False,
        "external_effects":0,
    }


@dataclass(frozen=True)
class ProbeOutcome:
    probe_id: str
    predicted: tuple[str,...]
    witnessed: tuple[str,...]
    witness_ref: str
    world_scope: str
    success_proven_in_source_world: bool
    actual_external_effects: int=0


def reenter(verdict:ProbeVerdict,witnessed,witness_ref):
    if not witness_ref or verdict.verdict!="CANDIDATE_GOAL_PROBE":
        raise ValueError("Only evaluated candidates can receive attributed feedback")
    observed=tuple(sorted(set(witnessed)))
    if not all(isinstance(x,str) and x for x in observed):
        raise ValueError("Witnessed fact keys must be typed")
    prediction=set(verdict.matches)
    return ProbeOutcome(
        verdict.probe_id,verdict.matches,observed,witness_ref,
        verdict.evidence_scope,
        bool(prediction & set(observed)),
        0)


def example():
    g=Goal("need_stable_water",("water_access","water_source_quality"),(),
           3,"fictional_game:water_need")
    probes=(
        Probe("inspect_known_water","move_toward_water",
              ("water_access",),(),1,0,"LOW",YES,YES,YES,
              "ACTUAL_GAME_SENSOR","synthetic:visible_water"),
        Probe("wander_to_novel_tile","move_away",
              ("unrelated_terrain",),(),1,0,"LOW",YES,YES,YES,
              "ACTUAL_GAME_SENSOR","synthetic:open_tile"),
        Probe("investigate_quality","observe_water_quality",
              ("water_source_quality",),(),2,0,"LOW",YES,YES,YES,
              "RESEARCHER_FIXTURE","synthetic:quality_probe"),
        Probe("unverified_risky_shortcut","cross_unknown_hazard",
              ("water_access",),(),1,0,"HIGH",YES,YES,UNKNOWN,
              "PROVISIONAL_MODEL","synthetic:unsafe"),
    )
    return g,probes


def report():
    g,p=example()
    result=select(g,p)
    return {
        "experiment":"QC016-GOAL-DIVIDEND",
        "status":"RESEARCH_ONLY",
        "goal":g.id,
        "pareto":result["pareto_candidate_ids"],
        "all":tuple((x.probe_id,x.verdict,x.matches,x.predicted_dividend)
                    for x in result["verdicts"]),
        "real_world_actions":0,
        "gameplay_actions":0,
        "source_has_verified_actual_gain":False,
    }


if __name__=="__main__":
    print(json.dumps(report(),sort_keys=True,indent=2))
