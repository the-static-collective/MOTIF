"""QC-009: Offline Field Atlas with local observations, freshness and backups.

People with street experience can know resources that never appear in
institutional directories. This module lets an agent *retain volunteered
knowledge with permission* and try different local leads when infrastructure
fails, without declaring observations universal, permanent or guaranteed.

No GPS, stalking, gathering of encampment locations, or service dispatch.
This keeps only arbitrary scenario-local symbolic lead IDs.
"""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
import json

YES,NO,UNKNOWN="YES","NO","UNKNOWN"
CHANNELS=frozenset({"ON_SITE","IN_PERSON","PHONE","WEB"})
CATEGORIES=frozenset({"FOOD","WATER","SHELTER","WARMTH","REST","CONNECTION"})
SOURCES=frozenset({"FIRST_HAND_REPORT","LOCAL_PARTNER_REPORT","PUBLIC_GUIDANCE",
                   "INFERRED_HYPOTHESIS"})
CONTACT_SAFETY=frozenset({"SAFE","UNSAFE","UNASSESSED"})


def seal(x):
    return sha256(json.dumps(x,sort_keys=True,separators=(",", ":")).encode()).hexdigest()


@dataclass(frozen=True)
class LocalLead:
    id: str
    category: str
    channel: str
    source_type: str
    source_ref: str
    observed_tick: int
    freshness_window: int
    availability: str
    access_safety: str
    consent_to_retain: bool
    description: str

    def check(self):
        if (not self.id or self.category not in CATEGORIES or
            self.channel not in CHANNELS or self.source_type not in SOURCES or
            not self.source_ref or self.observed_tick<0 or
            self.freshness_window<1 or self.freshness_window>30 or
            self.availability not in (YES,NO,UNKNOWN) or
            self.access_safety not in CONTACT_SAFETY or
            not self.consent_to_retain or not self.description):
            raise ValueError("Untrusted lead, no retention consent or invalid evidence")

    @property
    def pin(self):
        self.check()
        return seal(self.__dict__)


@dataclass(frozen=True)
class LeadVerdict:
    lead_id: str
    state: str
    why: tuple[str,...]
    source_pin: str
    external_availability_verified: bool = False


@dataclass(frozen=True)
class Atlas:
    leads: tuple[LocalLead,...] = ()

    def append(self,lead:LocalLead):
        lead.check()
        if any(l.id==lead.id for l in self.leads):
            raise ValueError("Do not silently rewrite lead history")
        return Atlas(self.leads+(lead,))

    @property
    def pin(self):
        return seal(tuple(lead.pin for lead in self.leads))

    def as_of(self,tick):
        return Atlas(tuple(x for x in self.leads if x.observed_tick<=tick))


def evaluate(lead:LocalLead,at_tick:int,network_state:dict[str,str]):
    lead.check()
    if at_tick<lead.observed_tick:
        raise ValueError("No evidence from the future")
    age=at_tick-lead.observed_tick
    why=[]
    if lead.availability==NO:
        why.append("PREVIOUSLY_REPORTED_UNAVAILABLE")
    elif lead.availability==UNKNOWN:
        why.append("AVAILABILITY_UNKNOWN")
    if age>=lead.freshness_window:
        why.append("LOCAL_OBSERVATION_STALE")
    if lead.access_safety=="UNSAFE":
        why.append("ACCESS_UNSAFE")
    elif lead.access_safety=="UNASSESSED":
        why.append("ACCESS_SAFETY_UNKNOWN")
    if lead.source_type in ("PUBLIC_GUIDANCE","INFERRED_HYPOTHESIS"):
        why.append("NOT_A_LOCAL_FIRST_HAND_OBSERVATION")
    if lead.channel in ("PHONE","WEB") and network_state.get(lead.channel,NO)!=YES:
        why.append("CHANNEL_DOWN")
    # External availability (today) cannot be certified just from a
    # past observation, even if the past observation was local first-hand.
    state=("BLOCKED" if any(x in why for x in (
        "PREVIOUSLY_REPORTED_UNAVAILABLE","ACCESS_UNSAFE","CHANNEL_DOWN"))
           else "REVALIDATE" if why else "CANDIDATE_FRESH_REPORT")
    return LeadVerdict(lead.id,state,tuple(why),lead.pin)


def atlas_options(atlas:Atlas,at_tick:int,network_state:dict[str,str]):
    rows=tuple(evaluate(x,at_tick,network_state) for x in atlas.leads)
    ready=tuple(x for x in rows if x.state=="CANDIDATE_FRESH_REPORT")
    check=tuple(x for x in rows if x.state=="REVALIDATE")
    blocked=tuple(x for x in rows if x.state=="BLOCKED")
    return {"atlas_pin":atlas.pin,"at_tick":at_tick,
            "candidate_leads":tuple(x.lead_id for x in ready),
            "to_revalidate":tuple(x.lead_id for x in check),
            "blocked":tuple(x.lead_id for x in blocked),
            "detail":tuple((x.lead_id,x.state,x.why) for x in rows),
            "actual_supplies_confirmed_now":0,
            "external_contacts":0}


def fixture():
    entries=(
        LocalLead(
            "local_walkable_contact","CONNECTION","IN_PERSON",
            "FIRST_HAND_REPORT","fixture:face-to-face",1,3,YES,
            "SAFE",True,"A simulated person has offered help previously"),
        LocalLead(
            "locally_seen_water","WATER","ON_SITE",
            "FIRST_HAND_REPORT","fixture:water-recent",2,2,YES,
            "SAFE",True,"A simulated source was observed previously"),
        LocalLead(
            "outdated_food_referral","FOOD","PHONE",
            "LOCAL_PARTNER_REPORT","fixture:old-referral",0,1,YES,
            "SAFE",True,"A simulated phone referral may be stale"),
        LocalLead(
            "unconfirmed_rumor","SHELTER","WEB",
            "INFERRED_HYPOTHESIS","fixture:unconfirmed",1,5,UNKNOWN,
            "UNASSESSED",True,"A rumor about shelter; never certified"),
    )
    atlas=Atlas()
    for item in entries:
        atlas=atlas.append(item)
    return atlas


def report():
    base=fixture()
    online=atlas_options(base,2,{"PHONE":YES,"WEB":YES})
    offline=atlas_options(base,2,{"PHONE":NO,"WEB":NO})
    aged=atlas_options(base,5,{"PHONE":NO,"WEB":NO})
    return {
        "experiment":"QC-009-FIELD-ATLAS",
        "status":"RESEARCH_PREVIEW_ONLY",
        "online":online,
        "network_failure":offline,
        "after_time_passes":aged,
        "historical_receipt_unchanged":base.as_of(2).pin==base.pin,
        "external_actions":0,
        "real_resource_availability_verified":False,
        "user_real_locations_collected":False,
    }


if __name__=="__main__":
    print(json.dumps(report(),sort_keys=True,indent=2))
