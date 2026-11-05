"""027F blinded-in-input synthetic case set, frozen before real T5 evaluation.

Fifty author-written cases; gold gate describes an imagined potentially
unresolved problem, NEVER a real permission or fact. Includes NONE cases
which contain superficially dangerous words in negated/resolved contexts.
Do not edit after reading actual scored model outcomes.
"""
from dataclasses import dataclass
from hashlib import sha256
import json

@dataclass(frozen=True)
class Case:
    id:str
    note:str
    gold:str
    issue_is_explicit:bool=True

CASES=(
 Case("F01","Nobody arranged cold storage for the buffet.","FOOD"),
 Case("F02","The sandwich cooler has stopped chilling.","FOOD"),
 Case("F03","We cannot establish a safe temperature at the serving table.","FOOD"),
 Case("F04","Our potluck needs a named person for hygiene.","FOOD"),
 Case("F05","Soup has no assigned server.","FOOD"),
 Case("F06","A donated supper sits out without an owner.","FOOD"),
 Case("F07","Someone forgot the food safety checklist.","FOOD"),
 Case("F08","The caterer has not verified allergy labels.","FOOD"),
 Case("F09","The hot meal is delayed because warming trays are broken.","FOOD"),
 Case("F10","The organizers never checked cold handling for shared portions.","FOOD"),

 Case("A01","The mic drops signal when the vocalist moves.","AUDIO"),
 Case("A02","The PA shuts off mid-song.","AUDIO"),
 Case("A03","A broken monitor leaves singers without a cue.","AUDIO"),
 Case("A04","Nobody signed off on cable routing.","AUDIO"),
 Case("A05","The amplifier keeps buzzing during rehearsal.","AUDIO"),
 Case("A06","One microphone has not been tested.","AUDIO"),
 Case("A07","The singers cannot hear the foldback speakers.","AUDIO"),
 Case("A08","The mixer is failing during the sound check.","AUDIO"),
 Case("A09","The wireless microphone cuts out around the crowd.","AUDIO"),
 Case("A10","The stage audio is unverified after rewiring.","AUDIO"),

 Case("X01","The elevator is unavailable after 6pm.","ACCESS"),
 Case("X02","There is no alternative entrance for someone using a wheelchair.","ACCESS"),
 Case("X03","The entry ramp is blocked by tables.","ACCESS"),
 Case("X04","A raised threshold remains unsafe for walkers.","ACCESS"),
 Case("X05","Nobody checked whether the lift works for guests.","ACCESS"),
 Case("X06","The stairs have a broken railing.","ACCESS"),
 Case("X07","The accessible route has not been confirmed.","ACCESS"),
 Case("X08","The side doorway cannot accommodate a chair.","ACCESS"),
 Case("X09","Guests can't find an accessible entrance after dark.","ACCESS"),
 Case("X10","The turnstile is too narrow to admit strollers.","ACCESS"),

 Case("S01","No helper agreed to watch the door.","STAFF"),
 Case("S02","The cleanup crew is unassigned.","STAFF"),
 Case("S03","Nobody volunteered to run the welcome table.","STAFF"),
 Case("S04","We need a person at each entrance while both hosts perform.","STAFF"),
 Case("S05","The staff lead has not agreed to open the hall.","STAFF"),
 Case("S06","Only one volunteer can handle two check-in points.","STAFF"),
 Case("S07","Teardown has no designated lead.","STAFF"),
 Case("S08","The setup helper canceled without replacement.","STAFF"),
 Case("S09","No attendant will supervise the supply table.","STAFF"),
 Case("S10","The host team never identified a cleanup person.","STAFF"),

 Case("N01","We revised the soup poster; meal is already approved.","NONE",False),
 Case("N02","A musician decided to bring their own microphone.","NONE",False),
 Case("N03","The wheelchair entrance is clear and inspected.","NONE",False),
 Case("N04","The welcome crew has a complete schedule.","NONE",False),
 Case("N05","The food photography looks great on the flyer.","NONE",False),
 Case("N06","No tickets need to be sold for this free gathering.","NONE",False),
 Case("N07","We are not planning to serve a meal.","NONE",False),
 Case("N08","The audio cables do not need replacement.","NONE",False),
 Case("N09","We have no concerns about ramp access.","NONE",False),
 Case("N10","Nobody needs to change the poster showing the buffet.","NONE",False),
)

def digest()->str:
    return sha256(json.dumps([x.__dict__ for x in CASES],
        sort_keys=True,separators=(",",":")).encode()).hexdigest()

assert len(CASES)==50 and len({x.id for x in CASES})==50
assert all(len([x for x in CASES if x.gold==g])==10
           for g in ("FOOD","AUDIO","ACCESS","STAFF","NONE"))
