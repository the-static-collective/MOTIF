"""MOTIF QC-010 — TRACTION LOOP: practical adaptation under uncertain safety.

It is possible to acknowledge historical human resilience, embodied craft
knowledge and improvisation without promoting "it worked once" to "it is
safe", or replacing practical judgment with a static catalogue of warnings.

This research kernel distinguishes:
 * Observed working behavior vs predicted feasibility vs proven safety.
 * Normative instructions vs field observations vs historical analogues.
 * Hard hazards, mitigable concerns, and unresolved questions.
 * Cold/reversible probes vs higher-exposure operations.
 * Valuable alternative actions after an attempted plan loses traction.

No action is executed. No personal record is loaded. All fixtures synthetic.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json

YES, NO, UNKNOWN = "YES", "NO", "UNKNOWN"
TRI = (YES, NO, UNKNOWN)
KINDS = frozenset((
    "FIELD_WITNESS", "BENCH_OBSERVATION", "HISTORICAL_ANALOGY",
    "TECHNICAL_GUIDANCE", "SIMULATED", "USER_REPORT",
))
LEVELS = frozenset(("SEVERE", "SUBSTANTIAL", "MINOR"))
EFFECTS = frozenset(("INQUIRY", "REVERSIBLE", "CONTROLLED", "HIGH_EXPOSURE"))
OUTCOMES = frozenset(("WORKED", "FAILED", "INCONCLUSIVE"))
STATUS="RESEARCH_PREVIEW_ONLY"


def digest(obj):
    return sha256(json.dumps(obj, sort_keys=True, separators=(",", ":"),
                             ensure_ascii=False).encode()).hexdigest()


@dataclass(frozen=True)
class Witness:
    key: str
    value: str
    provenance: str
    kind: str
    step: int
    details: str = ""

    def check(self):
        if (not self.key or self.value not in TRI or not self.provenance
            or self.kind not in KINDS or self.step<1):
            raise ValueError("Untrusted or untyped witness")

    @property
    def pin(self):
        self.check()
        return digest(self.__dict__)


@dataclass(frozen=True)
class Situation:
    history: tuple[Witness,...] = ()

    def __post_init__(self):
        last=0
        for x in self.history:
            x.check()
            if x.step<=last:
                raise ValueError("Cannot backdate evidence")
            last=x.step

    def at(self,key):
        for x in reversed(self.history):
            if x.key==key:
                return x.value
        return UNKNOWN

    def observe(self,key,value,source,kind="FIELD_WITNESS",details=""):
        if value not in (YES,NO) or not key or not source:
            raise ValueError("No guessed truths enter field ledger")
        next_step=self.history[-1].step+1 if self.history else 1
        return Situation(self.history+(Witness(
            key,value,source,kind,next_step,details),))

    def trail(self,key):
        return tuple(x for x in self.history if x.key==key)

    @property
    def pin(self):
        return digest(tuple(x.pin for x in self.history))


@dataclass(frozen=True)
class Hazard:
    id: str
    severity: str
    reason: str
    triggered_by: tuple[str,str]
    cleared_by: tuple[tuple[str,str], ...]
    source: str
    # Some conditions are consequential enough that UNKNOWN is a blocker
    # for high-exposure options, but not for low-exposure observation.
    exposure_floor: str = "CONTROLLED"

    def check(self):
        if (not self.id or self.severity not in LEVELS or not self.reason
            or self.triggered_by[1] not in (YES,NO) or
            any(value not in (YES,NO) for _,value in self.cleared_by)
            or not self.source or self.exposure_floor not in EFFECTS):
            raise ValueError("Bad hazard definition")


@dataclass(frozen=True)
class Action:
    id: str
    domain: str
    purpose: str
    effects: tuple[str,...]
    preconditions: tuple[tuple[str,str],...]
    exposure: str
    reversible: bool
    probe: str
    source: str
    model_kind: str = "RESEARCHER_AUTHORED"

    def check(self):
        if (not self.id or not self.domain or not self.purpose
            or not self.effects or not self.probe or not self.source
            or self.exposure not in EFFECTS or
            any(value not in (YES,NO) for _,value in self.preconditions)
            or self.model_kind!="RESEARCHER_AUTHORED"):
            raise ValueError("Unsafe or unsupported action")
        if self.exposure=="HIGH_EXPOSURE" and self.reversible:
            raise ValueError("High-exposure action cannot be falsely reversible")


@dataclass(frozen=True)
class Assessment:
    action: str
    verdict: str
    blocked: tuple[str,...]
    unknown: tuple[str,...]
    hazards: tuple[str,...]
    source: str
    predicted_effects: tuple[str,...]
    observed_effects: tuple[str,...] = ()
    executed: bool = False


def exposure_rank(exposure):
    return ("INQUIRY","REVERSIBLE","CONTROLLED","HIGH_EXPOSURE").index(exposure)


def hazard_check(h:Hazard,situation:Situation,action:Action):
    h.check()
    if exposure_rank(action.exposure)<exposure_rank(h.exposure_floor):
        return None
    actual=situation.at(h.triggered_by[0])
    if actual==h.triggered_by[1]:
        # Clearing controls must all be positively observed; unsupported
        # promises and historical analogues do not act as controls.
        clear_values=tuple(situation.at(key)==needed for key,needed in h.cleared_by)
        if h.cleared_by and all(clear_values):
            return ("MITIGATED",h.id)
        return ("KNOWN_HAZARD",h.id)
    if actual==UNKNOWN and h.severity=="SEVERE" and action.exposure in (
        "CONTROLLED","HIGH_EXPOSURE"):
        return ("UNRESOLVED_SEVERE",h.id)
    return None


def assess(action:Action,situation:Situation,hazards=()):
    action.check()
    blocked=[]
    unknown=[]
    for key,wanted in action.preconditions:
        got=situation.at(key)
        if got==UNKNOWN:
            unknown.append(key)
        elif got!=wanted:
            blocked.append(key)
    warnings=[]
    severe=False
    unknown_severe=False
    for h in hazards:
        result=hazard_check(h,situation,action)
        if result:
            label,hid=result
            if label!="MITIGATED":
                warnings.append(hid)
            if label=="KNOWN_HAZARD" and h.severity=="SEVERE":
                severe=True
            if label=="UNRESOLVED_SEVERE":
                unknown_severe=True
    if severe:
        verdict="REFUSE_UNMITIGATED_SEVERE_HAZARD"
    elif blocked:
        verdict="BLOCKED_PRECONDITION"
    elif unknown_severe:
        verdict="HOLD_UNKNOWN_SEVERE_SAFETY"
    elif unknown:
        verdict="ASK_FOR_FACTS"
    elif warnings and action.exposure in ("CONTROLLED","HIGH_EXPOSURE"):
        verdict="HOLD_FOR_MITIGATION_REVIEW"
    elif action.exposure in ("CONTROLLED","HIGH_EXPOSURE"):
        verdict="CONDITIONAL_REVIEW_NOT_EXECUTION"
    else:
        verdict="CANDIDATE_SAFE_TO_INSPECT_ONLY"
    return Assessment(
        action.id,verdict,tuple(sorted(set(blocked))),
        tuple(sorted(set(unknown))),tuple(sorted(set(warnings))),
        action.source,action.effects)


@dataclass(frozen=True)
class Feedback:
    action_id: str
    outcome: str
    observed_effects: tuple[str,...]
    source: str
    kind: str
    notes: str = ""

    def check(self):
        if (not self.action_id or self.outcome not in OUTCOMES or not self.source
            or self.kind not in KINDS or not isinstance(self.observed_effects,tuple)):
            raise ValueError("Feedback is a falsifiable sourced report")

    @property
    def pin(self):
        self.check()
        return digest(self.__dict__)


@dataclass(frozen=True)
class Trail:
    prior: Assessment
    outcome: str
    claim_pin: str
    observed_effects: tuple[str,...]
    unverified_safety: bool
    next_status: str
    hypotheses: tuple[str,...]


def reenter(prior:Assessment, feedback:Feedback, candidates):
    """A report of success/failure can revise the action search but NOT safety.

    Feedback is provenance-bearing testimony, not an authenticated sensor.
    It cannot erase an earlier hazard or change a world fact automatically.
    """
    feedback.check()
    if prior.action!=feedback.action_id:
        raise ValueError("Feedback belongs to a different action")
    if prior.executed:
        raise ValueError("Research kernel never issues external execution")
    if feedback.outcome=="FAILED":
        successor=tuple(x.id for x in candidates
                        if x.id!=prior.action)
        return Trail(prior,"FAILED",feedback.pin,feedback.observed_effects,
                     True,"REOPEN_ALTERNATIVE_ACTION_FIELD",
                     successor)
    if feedback.outcome=="WORKED":
        return Trail(prior,"WORKED",feedback.pin,feedback.observed_effects,
                     True,"FUNCTION_OBSERVED_SAFETY_UNVERIFIED",
                     ("check_long_term_effects",
                      "check_material_health_and_exposure",
                      "identify_new_reusable_capability"))
    return Trail(prior,"INCONCLUSIVE",feedback.pin,feedback.observed_effects,
                 True,"REQUIRE_SMALLER_OR_BETTER_MEASURED_PROBE",
                 ("change_observation_method","compare_lower_exposure_alternative"))


def oven_hazards():
    return (
        Hazard(
            "unknown_hot_masonry","SEVERE",
            "Unrated or damp materials can crack/spall under heating; "
            "a static successful cook is not thermal-safety certification.",
            ("masonry_heat_safety_unknown",YES),
            (("masonry_materials_verified",YES),),
            "engineering:material_thermal_behavior","CONTROLLED"),
        Hazard(
            "unverified_metal_surface","SEVERE",
            "Unknown metal coatings or residues must not be heated near food.",
            ("metal_coating_unverified",YES),
            (("food_contact_material_verified",YES),),
            "engineering:contamination_risk","CONTROLLED"),
        Hazard(
            "unsafe_flame_location","SEVERE",
            "Open fire around structures, combustibles or insufficient air "
            "movement can cause fire or harmful smoke exposure.",
            ("fire_location_unsafe",YES),
            (("clearance_verified",YES),),
            "engineering:fire_and_ventilation","CONTROLLED"),
    )


def oven_candidates():
    return (
        Action(
            "draw_new_layout","OVEN","Identify construction alternatives",
            ("design_sketch",),
            (("materials_present",YES),),
            "INQUIRY",True,
            "Draw or describe several heat-transfer and structural layouts "
            "without lighting a fire.", "scenario:human_assembly"),
        Action(
            "cold_fit_masonry","OVEN","Find which salvaged pieces fit",
            ("tested_geometry","candidate_new_cooking_capability"),
            (("materials_present",YES),("site_use_permitted",YES)),
            "REVERSIBLE",True,
            "Dry-fit materials without heating them; inspect stability and "
            "identify suspect materials before considering heat.",
            "scenario:human_assembly"),
        Action(
            "inspect_thermal_compatibility","OVEN",
            "Resolve hazards before cooking",
            ("materials_questions_answered",),
            (("materials_present",YES),),
            "INQUIRY",True,
            "Identify masonry type, moisture, food-contact metals, coatings "
            "and clearances; do not assume unknowns are safe.",
            "engineering:material_limits"),
        Action(
            "operate_proposed_oven","OVEN",
            "Cook only after separate real-world safety evaluation",
            ("cooked_food", "reusable_cooking_capacity"),
            (("materials_present",YES),
             ("site_use_permitted",YES),
             ("masonry_materials_verified",YES),
             ("food_contact_material_verified",YES),
             ("clearance_verified",YES)),
            "HIGH_EXPOSURE",False,
            "No automatic ignition or cooking trial. Needs independently "
            "appropriate safety conditions and operator judgment.",
            "scenario:review_required"),
        Action(
            "find_alternative_cooker","OVEN",
            "Seek a different permitted cooking capability",
            ("alternative_cooking_route",),
            (("safe_alternative_exists",YES),),
            "INQUIRY",True,
            "Explore borrowed, public or other genuinely available safe "
            "cooking options without inventing access.",
            "scenario:resource_search"),
    )


def repair_candidates():
    return (
        Action(
            "examine_components","REPAIR","Observe what actually broke",
            ("observed_failure_mode",),
            (("broken_equipment_present",YES),),
            "INQUIRY",True,"Inspect without energizing equipment.",
            "scenario:repair"),
        Action(
            "dry_fit_component","REPAIR","Explore a reversible fit",
            ("fit_hypothesis",),
            (("broken_equipment_present",YES),("safe_to_handle",YES)),
            "REVERSIBLE",True,"Test fit with the mechanism safely disengaged.",
            "scenario:repair"),
        Action(
            "seek_other_part","REPAIR","Find another component",
            ("new_component_possible",),
            (("part_source_known",YES),),
            "INQUIRY",True,"Investigate known spare parts.",
            "scenario:repair"),
    )


def oven_scene():
    # A synthetic schematic echo of practical material reuse, not a record
    # of any identified person's circumstances or real-world site.
    return (Situation()
        .observe("conventional_oven_usable",NO,"fixture:contamination")
        .observe("materials_present",YES,"fixture:available_salvage")
        .observe("site_use_permitted",YES,"fixture:permission")
        .observe("masonry_heat_safety_unknown",YES,"fixture:risk_unknown")
        .observe("metal_coating_unverified",YES,"fixture:risk_unknown"))


def benchmark():
    situation=oven_scene()
    options=oven_candidates()
    stages=tuple(assess(x,situation,oven_hazards()) for x in options)
    prior=next(x for x in stages if x.action=="cold_fit_masonry")
    trial=reenter(prior,Feedback(
        "cold_fit_masonry","WORKED",("tested_geometry",),
        "fixture:cold_fit_seen","SIMULATED"),options)
    failed=reenter(prior,Feedback(
        "cold_fit_masonry","FAILED",(),"fixture:pieces_did_not_fit",
        "SIMULATED"),options)
    return {
        "experiment":"QC-010",
        "status":STATUS,
        "situation_pin":situation.pin,
        "action_field":[{"id":x.action,"verdict":x.verdict,
                         "hazards":x.hazards,"unknown":x.unknown}
                        for x in stages],
        "observed_fit":trial.next_status,
        "failed_fit":failed.next_status,
        "failure_alternatives":failed.hypotheses,
        "verified_safe_hot_use":False,
        "real_world_actions":0,
        "technical_claim":"SYNTHETIC_TRANSITION_TEST_ONLY",
    }


if __name__=="__main__":
    print(json.dumps(benchmark(),sort_keys=True,indent=2))
