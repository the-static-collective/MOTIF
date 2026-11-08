"""MOTIF QC-008: Source-pinned affordance recovery when nourishment has no route.

The central correction: no viable path to a terminal need does NOT imply no
useful next action. The agent may preserve safe epistemic, grounding, inquiry
and capability-bridge options with strict guards. Grounding/breathing does not
provide calories. Deliberate fasting is not inferred as a response to unwanted
food deprivation.

Research harness: official public resource *navigation* documents (not local
availability); synthetic situations; user-answer simulations; no outbound
actions, calls, browsing or automatic personal data reads at runtime.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from collections import defaultdict
import json
from typing import Literal

AS_OF = "2026-11-07"
CAPABILITIES = frozenset({
    "has_food", "has_phone", "has_internet", "motor_transport",
    "can_walk", "safe_to_walk", "safe_public_destination_known",
    "someone_nearby", "medical_red_flags", "has_water",
})
YES, NO, UNKNOWN = "YES", "NO", "UNKNOWN"
VALUES = (YES,NO,UNKNOWN)
NUTRITION = "NUTRITION"
ONGOING = "ONGOING_NUTRITION"
ROUTING = "ASSISTANCE_ROUTING"
STATUS = "RESEARCH_PREVIEW_ONLY"
SOURCE_STATES = {"PUBLIC_GUIDANCE", "PERSON_REPORT", "SYNTHETIC_FIXTURE"}
MAX_ITEMS = 100


def receipt(data):
    return sha256(json.dumps(data, separators=(",", ":"),
                             sort_keys=True, ensure_ascii=False).encode()).hexdigest()


@dataclass(frozen=True)
class Source:
    id: str
    url: str
    claim: str
    scope: str
    captured: str

    def check(self):
        if (not self.id or not self.url.startswith("https://")
            or self.scope != "GENERAL_NAVIGATION_ONLY"
            or not self.claim or not self.captured):
            raise ValueError("Invalid evidence source; never infer local availability")

    @property
    def pin(self):
        self.check()
        return receipt(self.__dict__)


def public_source_registry():
    """Public source claims manually verified from official pages on AS_OF.

    This registry deliberately contains no phone location, address, provider
    hours, real-time acceptance, appointment, eligibility, food guarantee,
    or implied response to any outbound request.
    """
    return (
        Source(
            "united_way_211",
            "https://211.org/get-help/food-programs-food-benefits",
            "211 describes phone and online contact methods for locally "
            "referred food-assistance information; actual help depends on area",
            "GENERAL_NAVIGATION_ONLY",AS_OF),
        Source(
            "feeding_america_locator",
            "https://www.feedingamerica.org/need-help-find-food",
            "Feeding America describes a ZIP-based food-bank locator; "
            "food bank partners can provide local distribution details",
            "GENERAL_NAVIGATION_ONLY",AS_OF),
        Source(
            "usagov_emergency_food",
            "https://www.usa.gov/emergency-food-assistance",
            "USAGov lists contacting community and religious organizations, "
            "211 and national referral lines among possible food-help pathways",
            "GENERAL_NAVIGATION_ONLY",AS_OF),
    )


def registry_receipts(sources):
    if len({s.id for s in sources})!=len(sources):
        raise ValueError("Duplicate claim identity")
    return tuple((s.id,s.pin) for s in sources)


@dataclass(frozen=True)
class Observation:
    predicate: str
    value: str
    ref: str
    kind: str
    step: int

    def check(self):
        if (self.predicate not in CAPABILITIES or self.value not in VALUES
            or not self.ref or self.kind not in SOURCE_STATES
            or not isinstance(self.step,int) or self.step < 0):
            raise ValueError("Ill-typed or unattributed observation")

    @property
    def pin(self):
        self.check()
        return receipt(self.__dict__)


@dataclass(frozen=True)
class Situation:
    history: tuple[Observation,...]
    horizon: str
    urgency: str

    def __post_init__(self):
        if self.horizon not in ("IMMEDIATE","PERSISTENT"):
            raise ValueError("Ill-typed need horizon")
        if self.urgency not in ("ORDINARY","URGENT"):
            raise ValueError("Ill-typed urgency")
        seen=set()
        last=-1
        for event in self.history:
            event.check()
            if event.step<=last or event.pin in seen:
                raise ValueError("Evidence history must have unique increasing steps")
            seen.add(event.pin)
            last=event.step

    def at(self,predicate):
        if predicate not in CAPABILITIES:
            raise ValueError("Unknown predicate")
        for e in reversed(self.history):
            if e.predicate==predicate:
                return e.value
        return UNKNOWN

    def trace(self,predicate):
        return tuple(e for e in self.history if e.predicate==predicate)

    def append(self, predicate, value, source_ref, kind="PERSON_REPORT"):
        if predicate not in CAPABILITIES or value not in (YES,NO):
            raise ValueError("Answers must be explicit typed observations")
        event=Observation(predicate,value,source_ref,kind,
                          self.history[-1].step+1 if self.history else 1)
        return Situation(self.history+(event,),self.horizon,self.urgency)

    @property
    def pin(self):
        return receipt((self.horizon,self.urgency,
                        tuple(x.pin for x in self.history)))


@dataclass(frozen=True)
class Route:
    """Route to seek *help*, not a claim to have reached nourishment."""
    id: str
    purpose: str
    prereqs: tuple[tuple[str,str],...]
    source_ids: tuple[str,...]
    channel: str
    description: str
    helps_horizons: tuple[str,...] = ("IMMEDIATE","PERSISTENT")
    directly_provides_food: bool = False
    local_service_verified: bool = False
    may_require_user_consent: bool = True

    def check(self):
        if (not self.id or self.purpose not in (NUTRITION,ONGOING,ROUTING)
            or not self.source_ids or not self.description
            or any(k not in CAPABILITIES or v not in (YES,NO)
                   for k,v in self.prereqs)
            or self.directly_provides_food or self.local_service_verified
            or any(h not in ("IMMEDIATE","PERSISTENT")
                   for h in self.helps_horizons)):
            raise ValueError("No fabricated provider outcomes may be admitted")


@dataclass(frozen=True)
class RouteStatus:
    route_id: str
    verdict: str
    blocked: tuple[str,...]
    unknown: tuple[str,...]
    source_pins: tuple[str,...]
    guaranteed_food: bool = False


def routing_cards():
    return (
        Route(
            "call_211",ROUTING,(("has_phone",YES),),
            ("united_way_211","usagov_emergency_food"),"TELEPHONE",
            "Contact 211 to ask for local food resources; hours and "
            "eligibility need independent verification."),
        Route(
            "feeding_america_search",ROUTING,(("has_internet",YES),),
            ("feeding_america_locator",),"WEB_SEARCH",
            "Use ZIP-code lookup to identify food-bank partners; verify "
            "distribution hours, eligibility, travel and present availability."),
        Route(
            "ask_in_person_for_food_referral",ROUTING,
            (("can_walk",YES),("safe_to_walk",YES),
             ("safe_public_destination_known",YES)),
            ("usagov_emergency_food",),"ON_FOOT",
            "If safe and genuinely accessible, approach a known staffed "
            "community organization to request a referral or assistance. "
            "A staffed destination and services are not assumed."),
        Route(
            "ask_nearby_person_for_help",ROUTING,
            (("someone_nearby",YES),),
            ("usagov_emergency_food",),"PERSON",
            "Ask a safely approachable person for help reaching resources; "
            "no person or food supply is presumed."),
        Route(
            "research_ongoing_access",ONGOING,
            (("has_phone",YES),),
            ("united_way_211","usagov_emergency_food"),"TELEPHONE",
            "Ask about continuing food sources, eligibility and options "
            "for recurring access; no enrollment is assumed.",
            helps_horizons=("PERSISTENT",)),
    )


def route_status(route:Route,situation:Situation,sources):
    route.check()
    pins=dict(registry_receipts(sources))
    if any(source not in pins for source in route.source_ids):
        raise ValueError("Route lacks attributable public source")
    blocked,unknown=[],[]
    for key,wanted in route.prereqs:
        actual=situation.at(key)
        if actual==UNKNOWN:
            unknown.append(key)
        elif actual != wanted:
            blocked.append(key)
    verdict="BLOCKED" if blocked else "CONDITIONAL" if unknown else "POSSIBLE_REFERRAL"
    return RouteStatus(route.id,verdict,tuple(blocked),tuple(unknown),
                       tuple(pins[k] for k in route.source_ids))


@dataclass(frozen=True)
class Bridge:
    """No transition to YES is assumed: each is a *conditional capability*."""
    id: str
    target: str
    category: str
    steps: tuple[str,...]
    guard: str
    min_minutes: int
    effort: int
    harm_risk: int
    source_ids: tuple[str,...] = ()
    claimed_nutrition: int = 0
    automatically_changes_world: bool = False

    def check(self):
        if (not self.id or not self.target or
            self.category not in ("ORIENTATION","INQUIRY","CAPABILITY","HUMAN_HELP")
            or not self.steps or not self.guard or self.min_minutes < 1
            or self.effort < 0 or not 0<=self.harm_risk<=2
            or self.claimed_nutrition!=0 or self.automatically_changes_world):
            raise ValueError("Bridge cannot conjure food or evidence")


def bridge_library():
    return (
        Bridge(
            "brief_grounding","decision_readiness","ORIENTATION",
            ("If safe, take a few comfortable, slow breaths.",
             "Notice surroundings and identify one immediate safe question."),
            "Optional support for attention, NOT nourishment or a reason to "
            "delay urgent medical assistance.",
            2,1,0),
        Bridge(
            "assess_physical_safety","medical_red_flags","INQUIRY",
            ("Notice dizziness, fainting, severe weakness or inability to stay alert.",
             "If these are present, prioritize urgent assistance instead of walking."),
            "No diagnosis; the user must supply the result of this assessment.",
            1,1,0),
        Bridge(
            "check_walking_safety","safe_to_walk","INQUIRY",
            ("Can you safely move on foot without exposure, injury or danger?",
             "Do you have appropriate clothing, footwear and hydration?"),
            "Do NOT suggest travel when walking is unsafe or serious symptoms exist.",
            2,1,0),
        Bridge(
            "assess_walking_ability","can_walk","INQUIRY",
            ("Can you physically walk a safe distance? A lack of a car "
             "or bus does not establish inability to walk.",),
            "Obtain explicit context; never infer physical ability.",
            1,1,0),
        Bridge(
            "look_for_safe_public_destination","safe_public_destination_known",
            "INQUIRY",
            ("From a safe position, identify whether a staffed public location "
             "is actually known and reachable.",
             "Confirm its existence and safer access before traveling."),
            "Observing or imagining a place does not guarantee that one exists "
            "or is open; never fabricate nearby resources.",
            4,2,1),
        Bridge(
            "notice_nearby_people","someone_nearby","INQUIRY",
            ("If safe, notice whether a trusted or approachable person is present.",
             "Ask whether help can be requested without entering an unsafe situation."),
            "No person is presumed to be present, willing or safe.",
            2,1,0),
        Bridge(
            "seek_safe_shared_contact","has_phone","CAPABILITY",
            ("If a safe person or staffed location is confirmed, ask "
             "whether a phone call for food referral is possible.",),
            "A borrowed phone is a possibility, not acquired property or consent.",
            5,2,1),
        Bridge(
            "find_connection_point","has_internet","CAPABILITY",
            ("If safe access is established, inquire whether public internet "
             "or an accessible device is available.",),
            "Do not claim a library or internet kiosk exists locally.",
            8,2,1),
        Bridge(
            "request_human_assistance","human_help","HUMAN_HELP",
            ("If somebody can safely hear you, explain that you need "
             "food assistance and ask how to reach help.",),
            "Only if safe, without assuming a responder exists.",
            3,1,0),
    )


@dataclass(frozen=True)
class Question:
    predicate: str
    text: str
    unlocks: tuple[str,...]
    effort: int
    safety_priority: int
    status: str = "NEEDS_OBSERVATION_NOT_ASSUMPTION"


def question_text(predicate):
    queries={
        "medical_red_flags":"Are there urgent symptoms such as faintness, confusion or severe weakness?",
        "can_walk":"Can the person physically walk safely for a short distance?",
        "safe_to_walk":"Is walking actually safe given health, weather, terrain and local conditions?",
        "safe_public_destination_known":"Is an accessible, staffed public or community location definitely known?",
        "someone_nearby":"Is a safely approachable person nearby?",
        "has_phone":"Has a usable phone or borrowed call become available?",
        "has_internet":"Is an accessible internet connection currently available?",
        "has_food":"Is there safe food available right now?",
        "has_water":"Is there safe drinking water right now?",
        "motor_transport":"Is any safe motorized transport actually available?",
    }
    return queries[predicate]


def questions_from_routes(situation, assessed, bridges):
    """Only ask about unknowns that could change a current actionable route.

    The first question is a safety sentinel, not a guessed personal diagnosis.
    Ties in discriminating information are retained as a *question fiber*.
    """
    relevant=set()
    blockers=defaultdict(set)
    for status in assessed:
        if status.verdict in ("CONDITIONAL","BLOCKED"):
            for key in status.unknown+status.blocked:
                blockers[key].add(status.route_id)
                if situation.at(key)==UNKNOWN:
                    relevant.add(key)
    for b in bridges:
        if b.target in CAPABILITIES and situation.at(b.target)==UNKNOWN:
            if b.category=="INQUIRY":
                relevant.add(b.target)
    # Danger is a first-class unknown and outranks route convenience.
    if situation.at("medical_red_flags")==UNKNOWN:
        relevant.add("medical_red_flags")
    if situation.at("has_water")==UNKNOWN:
        relevant.add("has_water")
    result=[]
    for key in relevant:
        risk=0 if key in ("medical_red_flags","safe_to_walk","has_water") else 1
        effort=1 if key in ("medical_red_flags","can_walk","someone_nearby","has_water") else 2
        result.append(Question(key,question_text(key),
                               tuple(sorted(blockers[key])),effort,risk))
    result.sort(key=lambda q:(q.safety_priority,q.effort,q.predicate))
    return tuple(result)


def bridges_for(situation, routes):
    required={key for route in routes for key,_ in route.prereqs}
    result=[]
    for bridge in bridge_library():
        bridge.check()
        if bridge.target=="decision_readiness":
            result.append(bridge)
        elif bridge.target=="human_help":
            # A no-phone situation still admits the *possibility* of
            # non-electronic human connection, not an invented helper.
            result.append(bridge)
        elif bridge.target in required or bridge.target in ("medical_red_flags","has_water"):
            # Do not ask to make a known medically unsafe walk "safe".
            if (bridge.target in ("safe_to_walk","can_walk") and
                (situation.at("medical_red_flags")==YES or
                 situation.at("safe_to_walk")==NO or
                 situation.at("can_walk")==NO)):
                continue
            if situation.at(bridge.target)!=YES:
                result.append(bridge)
    return tuple(result)


@dataclass(frozen=True)
class Recovery:
    situation_pin: str
    source_pins: tuple[tuple[str,str],...]
    goal: str
    status: str
    routes: tuple[RouteStatus,...]
    bridges: tuple[Bridge,...]
    questions: tuple[Question,...]
    next_field: tuple[str,...]
    food_confirmed: bool = False
    actual_services_verified: bool = False
    external_actions: int = 0
    boundedness: str = "FINITE_TYPED_CANDIDATES"
    notes: str = ""


def recover(situation:Situation, sources=None):
    """Recover a *next useful move* even when there is no known food route.

    Critical principle: an information action is not a meal, yet can be
    valuable by turning a blocked/unknown prerequisite into an observed
    possibility. This routine never unilaterally makes those observations.
    """
    if not isinstance(situation,Situation):
        raise ValueError("Missing typed situation")
    if sources is None:
        sources=public_source_registry()
    pins=registry_receipts(sources)
    routes=tuple(r for r in routing_cards()
                 if situation.horizon in r.helps_horizons)
    assessed=tuple(route_status(r,situation,sources) for r in routes)
    available=tuple(x.route_id for x in assessed
                    if x.verdict=="POSSIBLE_REFERRAL")
    bridges=bridges_for(situation,routes)
    questions=questions_from_routes(situation,assessed,bridges)
    alarm=situation.at("medical_red_flags")
    food=situation.at("has_food")
    direct_food=food==YES
    if alarm==YES:
        status="PRIORITIZE_URGENT_HUMAN_ASSISTANCE"
        next_field=("seek_urgent_human_assistance",)
    elif direct_food:
        status="FOOD_PRESENT_VERIFY_SAFE_NOURISHMENT"
        next_field=("use_known_safe_food_if_appropriate",)+available
    elif available:
        status="REFERRAL_PATH_POSSIBLE_NOT_FOOD"
        next_field=available
    else:
        status="NO_FOOD_ROUTE_YET__NEXT_CAPABILITY"
        # Keeping a *field* of alternatives avoids choosing a singular
        # guessed path. Important, use safety inquiry before travel.
        next_field=tuple(b.id for b in bridges
                         if b.category in ("ORIENTATION","INQUIRY","HUMAN_HELP"))
    return Recovery(
        situation.pin,pins,
        "FIND_REPEATABLE_FOOD_ACCESS" if situation.horizon=="PERSISTENT" else
        "FIND_IMMEDIATE_NOURISHMENT",
        status,assessed,bridges,questions,next_field,
        food_confirmed=direct_food,
        notes="Navigation is a route toward assessment, not evidence food is "
              "available. Mindfulness can support attention but supplies "
              "no calories; involuntary deprivation is not therapeutic fasting.")


def synthetic_case(name):
    base=Situation((), "IMMEDIATE", "ORDINARY")
    if name=="no_phone_no_car_no_food":
        return (base.append("has_phone",NO,"fixture:user")
                    .append("motor_transport",NO,"fixture:user")
                    .append("has_food",NO,"fixture:user"))
    if name=="known_safe_walk":
        return (synthetic_case("no_phone_no_car_no_food")
                    .append("medical_red_flags",NO,"fixture:user")
                    .append("can_walk",YES,"fixture:user")
                    .append("safe_to_walk",YES,"fixture:user")
                    .append("safe_public_destination_known",YES,
                            "fixture:confirmed-destination"))
    if name=="not_safe_to_walk":
        return (synthetic_case("no_phone_no_car_no_food")
                    .append("medical_red_flags",NO,"fixture:user")
                    .append("can_walk",YES,"fixture:user")
                    .append("safe_to_walk",NO,"fixture:hazard"))
    if name=="symptomatic":
        return (synthetic_case("no_phone_no_car_no_food")
                    .append("medical_red_flags",YES,"fixture:serious-symptom"))
    if name=="persistent_no_phone":
        s=synthetic_case("no_phone_no_car_no_food")
        return Situation(s.history,"PERSISTENT","ORDINARY")
    if name=="phone_available":
        return (base.append("has_phone",YES,"fixture:user")
                    .append("has_food",NO,"fixture:user"))
    raise ValueError("Unknown scenario")


def report():
    cases={}
    for name in (
        "no_phone_no_car_no_food","known_safe_walk","not_safe_to_walk",
        "symptomatic","persistent_no_phone","phone_available"
    ):
        result=recover(synthetic_case(name))
        cases[name]={
            "status":result.status,
            "next_field":result.next_field,
            "confirmed_local_services":result.actual_services_verified,
            "confirmed_food":result.food_confirmed,
            "possible_referrals":tuple(r.route_id for r in result.routes
                                       if r.verdict=="POSSIBLE_REFERRAL"),
            "conditional_routes":tuple(r.route_id for r in result.routes
                                       if r.verdict=="CONDITIONAL"),
            "blocked_routes":tuple(r.route_id for r in result.routes
                                   if r.verdict=="BLOCKED"),
            "open_questions":tuple(q.predicate for q in result.questions),
            "recovery_options":tuple(b.id for b in result.bridges),
        }
    return {"experiment":"QC-008","status":STATUS,
            "public_source_pins":registry_receipts(public_source_registry()),
            "source_scope":"GENERAL_NAVIGATION_NOT_LOCAL_AVAILABILITY",
            "cases":cases,
            "external_actions":0,
            "real_meals_provided":0,
            "verified_real_world_impact":False,
            "epistemic_design":"NO_ROUTE_TO_NEED != NO_USEFUL_NEXT_ACTION",
            "health_guard":"GROUNDING_IS_NOT_CALORIES__FASTING_NOT_A_FOOD_ROUTE"}


if __name__=="__main__":
    print(json.dumps(report(),indent=2,sort_keys=True))
