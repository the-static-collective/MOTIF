"""QC-008 source-to-affordance compiler: no raw web text becomes an action.

A researcher curates structured, attributable public *navigation* mechanisms
from cited sources. The compiler can incorporate additional source-owned
mechanisms without modifying the domain planner. It cannot read the web,
infer service hours, discover live local providers or execute a route.

The candidate mechanism catalogue is explicitly authored and reviewable;
"discovery" means compiling verified general affordances into a user's
currently feasible/conditional action field, NOT autonomous extraction from
arbitrary untrusted HTML.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from recover import (
    Source, Route, public_source_registry, YES, NO, NUTRITION,
    ONGOING, ROUTING, CAPABILITIES,
)


@dataclass(frozen=True)
class MechanismSpec:
    id: str
    source_ids: tuple[str,...]
    channel: str
    prerequisites: tuple[tuple[str,str],...]
    purpose: str
    description: str
    horizons: tuple[str,...] = ("IMMEDIATE","PERSISTENT")
    source_type: str = "DOCUMENTED_NAVIGATION_ONLY"

    def check(self):
        if (not self.id or not self.source_ids or not self.description or
            self.channel not in ("TELEPHONE","WEB_SEARCH","PERSON","ON_FOOT")
            or self.purpose not in (NUTRITION,ONGOING,ROUTING)
            or self.source_type!="DOCUMENTED_NAVIGATION_ONLY"
            or not self.horizons
            or any(k not in CAPABILITIES or v not in (YES,NO)
                   for k,v in self.prerequisites)):
            raise ValueError("Mechanism is not a safe typed navigation affordance")


def catalogued_public_mechanisms():
    """Human-reviewed claims from three real official guidance pages."""
    return (
        MechanismSpec(
            "call_211",("united_way_211","usagov_emergency_food"),
            "TELEPHONE",(("has_phone",YES),),ROUTING,
            "Contact 211 to ask for local food resources; hours and "
            "eligibility need independent verification."),
        MechanismSpec(
            "feeding_america_search",("feeding_america_locator",),
            "WEB_SEARCH",(("has_internet",YES),),ROUTING,
            "Use ZIP-code lookup to identify food-bank partners; verify "
            "distribution hours, eligibility, travel and present availability."),
        MechanismSpec(
            "ask_in_person_for_food_referral",("usagov_emergency_food",),
            "ON_FOOT",(("can_walk",YES),("safe_to_walk",YES),
                       ("safe_public_destination_known",YES)),ROUTING,
            "If safe and genuinely accessible, approach a known staffed "
            "community organization to request a referral or assistance. "
            "A staffed destination and services are not assumed."),
        MechanismSpec(
            "ask_nearby_person_for_help",("usagov_emergency_food",),
            "PERSON",(("someone_nearby",YES),("safe_person_to_approach",YES)),ROUTING,
            "Ask a safely approachable person for help reaching resources; "
            "no person or food supply is presumed."),
        MechanismSpec(
            "research_ongoing_access",("united_way_211",
                                       "usagov_emergency_food"),
            "TELEPHONE",(("has_phone",YES),),ONGOING,
            "Ask about continuing food sources, eligibility and options "
            "for recurring access; no enrollment is assumed.",
            horizons=("PERSISTENT",)),
    )


def compile_public_routes(sources:tuple[Source,...],
                          specs:tuple[MechanismSpec,...]):
    """Compile documented affordances with strict source and type checking."""
    mapping={}
    for source in sources:
        source.check()
        if source.id in mapping:
            raise ValueError("Duplicate source IDs")
        mapping[source.id]=source
    result=[]
    seen=set()
    for spec in specs:
        spec.check()
        if spec.id in seen:
            raise ValueError("Duplicate candidate identity")
        seen.add(spec.id)
        if any(source_id not in mapping for source_id in spec.source_ids):
            raise ValueError("Candidate lacks a reviewed public source")
        card=Route(
            spec.id,spec.purpose,spec.prerequisites,spec.source_ids,
            spec.channel,spec.description,spec.horizons,
            directly_provides_food=False,local_service_verified=False,
            may_require_user_consent=True,
        )
        card.check()
        result.append(card)
    return tuple(result)


if __name__=="__main__":
    import json
    cards=compile_public_routes(public_source_registry(),
                                 catalogued_public_mechanisms())
    print(json.dumps([c.__dict__ for c in cards],default=list,
                     sort_keys=True,indent=2))
