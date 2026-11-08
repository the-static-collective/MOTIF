"""QC-009: STREET SENSE — offline-first, lived-experience-aware survival reasoning.

A small *research* planner for disrupted infrastructure, unsheltered living,
and immediate low-resource situations. It models potential safety, mobility,
water, human and food options without inventing a working service, a meal,
safe drinking water, shelter, consent, local opening hours or a human helper.

UNTESTED RESULTS ARE NOT REAL-WORLD ADVICE. An actual crisis needs accurate,
location-specific observation, trusted people, and emergency help as relevant.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from hashlib import sha256
import json

YES, NO, UNKNOWN = "YES","NO","UNKNOWN"
VALUES = frozenset((YES,NO,UNKNOWN))
STATUS="RESEARCH_PREVIEW_ONLY"
FACTS = frozenset((
    "has_food", "has_safe_water", "has_phone", "has_internet",
    "can_walk", "walking_safe", "safe_public_place_known", "safe_person_present",
    "shelter_available", "shade_available", "dry_layers_available",
    "cold_exposure", "heat_exposure", "urgent_symptoms",
    "suspected_water_contamination", "ongoing_access_verified",
))
INFRA = frozenset(("has_phone","has_internet"))
ACTION_CHANNELS=frozenset((
    "ON_SITE", "INQUIRY", "FOOT", "HUMAN", "NETWORK", "SUPPLY", "RECURRENCE",
))
PURPOSES=frozenset((
    "STABILIZE", "OBSERVE", "ENABLE", "NOURISH", "CONNECT", "CONTINUE",
))
SOURCES={
    "cdc_cold":"https://www.cdc.gov/winter-weather/prevention/",
    "cdc_heat":"https://www.cdc.gov/extreme-heat/risk-factors/extreme-heat-and-low-income.html",
    "cdc_water":"https://www.cdc.gov/water-emergency/about/",
    "cdc_water_find":"https://www.cdc.gov/water-emergency/about/how-to-find-clean-water-in-an-emergency.html",
    "outreach_lived":"https://www.chcs.org/resource-center-item/street-medicine-and-outreach-bringing-care-to-people-where-they-are/",
    "outreach_practice":"https://endhomelessness.org/wp-content/uploads/2025/02/NAEH_Housing-Focused-Street-Outreach-Framework.pdf",
}
# These URLs support high-level boundary guidelines, not a local resource directory.
# The network is never contacted by the runtime.


def seal(obj):
    return sha256(json.dumps(obj,sort_keys=True,separators=(",", ":")).encode()).hexdigest()


@dataclass(frozen=True)
class Fact:
    name: str
    value: str
    source: str
    step: int

    def check(self):
        if (self.name not in FACTS or self.value not in VALUES
            or not self.source or self.step<1):
            raise ValueError("Unattributed or untyped observed state")


@dataclass(frozen=True)
class Scene:
    """Append-only facts; latest accepted report may change, history cannot."""
    observations: tuple[Fact,...]
    need_horizon: str = "IMMEDIATE"

    def __post_init__(self):
        if self.need_horizon not in ("IMMEDIATE","REPEATED"):
            raise ValueError("Invalid horizon")
        previous=0
        for f in self.observations:
            f.check()
            if f.step<=previous:
                raise ValueError("Cannot backdate observations")
            previous=f.step

    def get(self,name):
        if name not in FACTS:
            raise ValueError("Unknown fact")
        for f in reversed(self.observations):
            if f.name==name:
                return f.value
        return UNKNOWN

    def add(self,name,value,source):
        if value not in (YES,NO):
            raise ValueError("Unknown or guessed observations cannot be admitted")
        f=Fact(name,value,source,
               1 if not self.observations else self.observations[-1].step+1)
        return Scene(self.observations+(f,),self.need_horizon)

    @property
    def pin(self):
        return seal((self.need_horizon,tuple(f.__dict__ for f in self.observations)))


@dataclass(frozen=True)
class StreetOption:
    id: str
    purpose: str
    channel: str
    requires: tuple[tuple[str,str],...]
    proposed_effect: str
    horizon: str
    minutes: int
    risk: int
    evidence_ids: tuple[str,...]
    question: str
    priority: str = "ROUTINE"
    verified_benefit: bool = False

    def check(self):
        if (not self.id or self.purpose not in PURPOSES or
            self.channel not in ACTION_CHANNELS or
            self.horizon not in ("NOW","BRIDGE","SUSTAIN") or
            self.minutes<1 or self.risk not in (0,1,2) or
            not self.proposed_effect or not self.question or
            not self.evidence_ids or
            any(k not in FACTS or v not in (YES,NO) for k,v in self.requires)
            or any(k not in SOURCES for k in self.evidence_ids)
            or self.verified_benefit):
            raise ValueError("No unsigned or unsupported effects may be admitted")
        if self.channel=="FOOT" and not {("can_walk",YES),("walking_safe",YES)}.issubset(self.requires):
            raise ValueError("Cannot move without confirmed ability and safe route")
        if self.channel=="HUMAN" and ("safe_person_present",YES) not in self.requires:
            raise ValueError("Cannot manufacture a safely approachable person")
        if self.channel=="NETWORK" and not any(
            x in self.requires for x in (("has_phone",YES),("has_internet",YES))
        ):
            raise ValueError("Cannot manufacture a phone or connection")
        if self.purpose=="NOURISH" and self.id=="ingest_safe_water" and (
            ("has_safe_water",YES) not in self.requires
            or ("suspected_water_contamination",NO) not in self.requires
        ):
            raise ValueError("Cannot label unverified water safe to drink")


@dataclass(frozen=True)
class OptionStatus:
    option: StreetOption
    verdict: str
    blocked: tuple[str,...]
    unresolved: tuple[str,...]
    # More than one type of value: a low-level action can open an option
    # without delivering the goal. This is not a quantified probability.
    kind: str

    @property
    def pin(self):
        return seal((self.option.id,self.verdict,self.blocked,self.unresolved))


def catalogue():
    """Researcher-written candidates, NOT evidence of available supplies.

    Distinguish five channels: on-site self-stabilization, safety observations,
    foot movement, consensual human networks, unreliable digital infrastructure.
    """
    return (
        StreetOption(
            "pause_and_orient","STABILIZE","ON_SITE",(),
            "Optional awareness and decision readiness; no calories",
            "NOW",2,0,("outreach_lived",),
            "Is it safe to stop briefly and notice immediate conditions?"),
        StreetOption(
            "check_urgent_signs","OBSERVE","INQUIRY",(),
            "Find whether emergency symptoms require urgent human help",
            "NOW",1,0,("cdc_cold","cdc_heat"),
            "Are there fainting, confusion, severe weakness, heat stroke or cold illness signs?"),
        StreetOption(
            "check_water_condition","OBSERVE","INQUIRY",(),
            "Determine whether any available water is actually safe",
            "NOW",2,0,("cdc_water",),
            "Is potable water really available and free of suspected chemical contamination?"),
        StreetOption(
            "check_exposure","OBSERVE","INQUIRY",(),
            "Identify immediately threatening cold, wet clothing or heat",
            "NOW",2,0,("cdc_cold","cdc_heat"),
            "Is cold, wetness or heat an immediate threat?"),
        StreetOption(
            "check_mobility","OBSERVE","INQUIRY",(),
            "Find out if a short walk is actually safe",
            "BRIDGE",2,0,("outreach_lived",),
            "Can the person walk without danger, illness, exposure or unsafe roads?"),
        StreetOption(
            "identify_human_connections","OBSERVE","INQUIRY",(),
            "Check whether a genuinely safe and consenting human contact exists",
            "BRIDGE",3,0,("outreach_lived",),
            "Is anyone nearby safe to approach or able to help?"),
        StreetOption(
            "move_into_known_shelter","STABILIZE","FOOT",
            (("can_walk",YES),("walking_safe",YES),("shelter_available",YES)),
            "Reach confirmed safe shelter without claiming it is open",
            "NOW",15,1,("cdc_cold","cdc_heat"),
            "Is a real safe shelter accessible, with permission?"),
        StreetOption(
            "move_into_known_shade","STABILIZE","FOOT",
            (("can_walk",YES),("walking_safe",YES),("shade_available",YES)),
            "Reduce modeled heat exposure without claiming recovery",
            "NOW",5,0,("cdc_heat",),
            "Is shade accessible without increasing exposure or risk?"),
        StreetOption(
            "use_known_dry_layers","STABILIZE","ON_SITE",
            (("dry_layers_available",YES),),
            "Use actually available dry layers against cold/wet exposure",
            "NOW",3,0,("cdc_cold",),
            "Are safe, dry garments available now?"),
        StreetOption(
            "ingest_safe_water","NOURISH","SUPPLY",
            (("has_safe_water",YES),("suspected_water_contamination",NO)),
            "Use verified safe water for hydration if able to drink",
            "NOW",2,0,("cdc_water",),
            "Is the available water safe? Can the person drink?"),
        StreetOption(
            "eat_verified_food","NOURISH","SUPPLY",
            (("has_food",YES),),
            "Eat actually available safe food; never assume a meal arrived",
            "NOW",15,0,("outreach_lived",),
            "Is safe, appropriate food in hand?"),
        StreetOption(
            "walk_to_verified_public_place","ENABLE","FOOT",
            (("can_walk",YES),("walking_safe",YES),
             ("safe_public_place_known",YES)),
            "Reach known public help point; service and hours unverified",
            "BRIDGE",25,1,("outreach_lived",),
            "Is the actual staffed destination reachable and accepting visitors?"),
        StreetOption(
            "request_help_from_safe_person","CONNECT","HUMAN",
            (("safe_person_present",YES),),
            "Request information or basic needs help from someone safely approachable",
            "BRIDGE",5,0,("outreach_lived",),
            "Is the person willing, able and comfortable being asked?"),
        StreetOption(
            "ask_for_borrowed_call","ENABLE","HUMAN",
            (("safe_person_present",YES),),
            "Ask permission to use phone; do not infer the phone is granted",
            "BRIDGE",5,0,("outreach_lived",),
            "Could a safe person consent to placing a call?"),
        StreetOption(
            "online_food_referral","ENABLE","NETWORK",
            (("has_internet",YES),),
            "Investigate real local resource information if internet works",
            "BRIDGE",10,0,("outreach_lived",),
            "Is the connection working, and are local providers verifiable?"),
        StreetOption(
            "call_for_support","CONNECT","NETWORK",
            (("has_phone",YES),),
            "Contact actual trusted support/referral number if phone works",
            "BRIDGE",10,0,("outreach_lived",),
            "Who is reachable, and will they respond?"),
        StreetOption(
            "build_recurring_food_route","CONTINUE","HUMAN",
            (("safe_person_present",YES),),
            "Discuss a durable food-access arrangement; acceptance not assumed",
            "SUSTAIN",25,0,("outreach_lived",),
            "Can a voluntarily participating network support repeated needs?"),
    )


def assess(option:StreetOption, scene:Scene):
    option.check()
    blocked,unresolved=[],[]
    for name,expected in option.requires:
        value=scene.get(name)
        if value==UNKNOWN:
            unresolved.append(name)
        elif value!=expected:
            blocked.append(name)
    if option.channel=="FOOT" and scene.get("urgent_symptoms")==YES:
        blocked.append("urgent_symptoms")
    if option.id=="move_into_known_shade" and scene.get("heat_exposure")==NO:
        blocked.append("heat_exposure")
    if option.id=="use_known_dry_layers" and scene.get("cold_exposure")==NO:
        blocked.append("cold_exposure")
    if option.id=="ingest_safe_water" and scene.get("suspected_water_contamination")==YES:
        blocked.append("suspected_water_contamination")
    verdict="BLOCKED" if blocked else "CONDITIONAL" if unresolved else "CANDIDATE_READY"
    return OptionStatus(option,verdict,tuple(sorted(set(blocked))),
                        tuple(sorted(set(unresolved))),option.purpose)


@dataclass(frozen=True)
class SkillWitness:
    """Lived-experience reports stay sourced, consented and fallible.

    Nothing gets automatically imported into general safety authority.
    """
    id: str
    description: str
    provenance: str
    consent_to_store: bool
    scope: str
    verification: str = "UNVERIFIED_EXPERIENCE"

    def admit(self):
        if not (self.id and self.description and self.provenance
                and self.consent_to_store and self.scope
                and self.verification in ("UNVERIFIED_EXPERIENCE",
                                          "EXTERNALLY_REVIEWED")):
            raise ValueError("Lived field observations need consent and context")
        return self


@dataclass(frozen=True)
class StreetResult:
    scene_pin: str
    status: str
    preferred_urgencies: tuple[str,...]
    ready: tuple[OptionStatus,...]
    conditional: tuple[OptionStatus,...]
    blocked: tuple[OptionStatus,...]
    offline_ready: tuple[str,...]
    online_ready: tuple[str,...]
    unknowns_worth_asking: tuple[str,...]
    source_urls: tuple[str,...]
    external_effects: int = 0
    food_supplied: bool = False
    shelter_delivered: bool = False
    field_expertise_automatically_verified: bool = False


def reason(scene:Scene, options=None):
    """Expose the meaningful action *field*, not one guessed survival trick."""
    if options is None:
        options=catalogue()
    if len({x.id for x in options})!=len(options):
        raise ValueError("Duplicate option IDs")
    results=tuple(assess(o,scene) for o in options)
    ready=tuple(x for x in results if x.verdict=="CANDIDATE_READY")
    conditional=tuple(x for x in results if x.verdict=="CONDITIONAL")
    blocked=tuple(x for x in results if x.verdict=="BLOCKED")
    offline=tuple(x.option.id for x in ready
                  if x.option.channel!="NETWORK")
    online=tuple(x.option.id for x in ready
                 if x.option.channel=="NETWORK")
    unknown=set(x for e in conditional for x in e.unresolved)
    severe=scene.get("urgent_symptoms")==YES
    cold=scene.get("cold_exposure")==YES
    hot=scene.get("heat_exposure")==YES
    water=scene.get("has_safe_water") == NO
    if severe:
        status="URGENT_HUMAN_ASSISTANCE_REQUIRED"
        priorities=("URGENT_HUMAN_HELP", "DO_NOT_WALK_IF_UNSAFE")
    elif cold:
        status="COLD_EXPOSURE_PRIORITY"
        priorities=("SAFE_DRY_WARMTH", "HUMAN_HELP", "WATER", "FOOD", "CONTINUITY")
    elif hot:
        status="HEAT_EXPOSURE_PRIORITY"
        priorities=("SHADE_COOLING", "WATER", "HUMAN_HELP", "FOOD", "CONTINUITY")
    elif water:
        status="SAFE_WATER_GAP_PRIORITY"
        priorities=("FIND_SAFE_WATER", "HUMAN_HELP", "FOOD", "CONTINUITY")
    else:
        status="ACTION_FIELD_AVAILABLE"
        priorities=("ASSESS_SAFETY", "PRESERVE_OPTIONS", "MEET_NEED", "CONTINUITY")
    if scene.need_horizon=="REPEATED":
        priorities+=("ESTABLISH_RECURRING_ACCESS",)
    evidence_urls=tuple(sorted({SOURCES[k] for s in results
                                for k in s.option.evidence_ids}))
    return StreetResult(
        scene.pin,status,priorities,ready,conditional,blocked,
        offline,online,tuple(sorted(unknown)),evidence_urls,
        external_effects=0,food_supplied=False,shelter_delivered=False)


def counterfactual_disconnect(scene):
    """Does loss of digital infrastructure erase independent alternatives?"""
    unplugged=(scene.add("has_phone",NO,"fixture:connection-failed")
                .add("has_internet",NO,"fixture:network-failed"))
    before=reason(scene)
    after=reason(unplugged)
    retained=set(before.offline_ready)&set(after.offline_ready)
    return {
        "before_scene":scene.pin,
        "after_scene":unplugged.pin,
        "before_online_candidates":before.online_ready,
        "after_online_candidates":after.online_ready,
        "retained_offline_candidates":tuple(sorted(retained)),
        "new_real_world_supplies":0,
    }


def case(name):
    base=Scene(())
    if name=="offline_unknown":
        return (base.add("has_phone",NO,"fixture:no_phone")
                .add("has_internet",NO,"fixture:no_net")
                .add("has_food",NO,"fixture:no_food")
                .add("has_safe_water",NO,"fixture:no_water"))
    if name=="hot_and_offline":
        return (case("offline_unknown")
                .add("heat_exposure",YES,"fixture:hot")
                .add("shade_available",YES,"fixture:known_shade")
                .add("can_walk",YES,"fixture:can_walk")
                .add("walking_safe",YES,"fixture:walk_appropriate"))
    if name=="wet_cold_and_unprepared":
        return (case("offline_unknown")
                .add("cold_exposure",YES,"fixture:wet_cold")
                .add("dry_layers_available",NO,"fixture:no_change")
                .add("shelter_available",NO,"fixture:no_shelter"))
    if name=="with_safe_contact":
        return (case("offline_unknown")
                .add("safe_person_present",YES,"fixture:consenting_contact"))
    if name=="danger_signs":
        return (case("hot_and_offline")
                .add("urgent_symptoms",YES,"fixture:danger"))
    if name=="network_connected":
        return (base.add("has_phone",YES,"fixture:working_phone")
                .add("has_internet",YES,"fixture:working_net")
                .add("has_food",NO,"fixture:no_food"))
    if name=="unverified_water":
        return (case("offline_unknown")
                .add("has_safe_water",YES,"fixture:person_hypothesis")
                .add("suspected_water_contamination",YES,"fixture:warning"))
    if name=="repeated_needs":
        first=case("with_safe_contact")
        return Scene(first.observations,"REPEATED")
    raise ValueError("Not a defined synthetic scene")


def run():
    scenes={}
    for name in ("offline_unknown","hot_and_offline",
                 "wet_cold_and_unprepared","with_safe_contact",
                 "danger_signs","network_connected",
                 "unverified_water","repeated_needs"):
        r=reason(case(name))
        scenes[name]={
            "status":r.status,
            "urgent_priorities":r.preferred_urgencies,
            "ready_offline":r.offline_ready,
            "ready_online":r.online_ready,
            "conditional":len(r.conditional),
            "blocked":len(r.blocked),
            "unknowns":r.unknowns_worth_asking,
            "actual_food":r.food_supplied,
            "actual_shelter":r.shelter_delivered,
        }
    return {
        "experiment":"QC-009",
        "status":STATUS,
        "scenes":scenes,
        "network_cut":counterfactual_disconnect(case("network_connected")),
        "sources":SOURCES,
        "external_effects":0,
        "real_world_expertise_claims":0,
        "source_evidence":"GENERAL_PUBLIC_SAFETY_CONTEXT_NOT_LOCAL_AVAILABILITY",
        "measured_real_world_outcomes":0,
    }


if __name__=="__main__":
    print(json.dumps(run(),indent=2,sort_keys=True))
