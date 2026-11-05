"""026F precommitted synthetic transfer cases, not real field reports.

Gold labels are research-author declarations. T5 sees only the note, never
the answer. This is a new 25-note sample, not a genuine independent corpus.
"""
from dataclasses import dataclass
from hashlib import sha256
import json

@dataclass(frozen=True)
class Case:
    id: str
    note: str
    gold_gate: str

CASES=(
    Case("F01","Nobody has agreed to monitor temperatures at the buffet.","FOOD"),
    Case("F02","Who checks whether the sandwiches stay cold until service?","FOOD"),
    Case("F03","Shared casseroles have no appointed safety lead.","FOOD"),
    Case("F04","Catering trays sit out without a handling plan.","FOOD"),
    Case("F05","Nobody specified hygiene procedures for potluck portions.","FOOD"),
    Case("A01","The stage monitor keeps buzzing.","AUDIO"),
    Case("A02","The microphone cable is damaged.","AUDIO"),
    Case("A03","The amplifier keeps shutting itself off.","AUDIO"),
    Case("A04","Nobody tested whether the speakers work.","AUDIO"),
    Case("A05","The wireless mic cuts out during rehearsal.","AUDIO"),
    Case("X01","The ramp leading into the room is blocked.","ACCESS"),
    Case("X02","Guests with mobility scooters cannot use the side entry.","ACCESS"),
    Case("X03","The lift to the lower level will not open.","ACCESS"),
    Case("X04","There is no safe route around a raised threshold.","ACCESS"),
    Case("X05","The elevator has stopped working.","ACCESS"),
    Case("S01","Nobody is covering the guest welcome table.","STAFF"),
    Case("S02","The chairs have no assigned teardown crew.","STAFF"),
    Case("S03","Only one person can manage the two entrances.","STAFF"),
    Case("S04","The supply table has no attendant.","STAFF"),
    Case("S05","Who will supervise setup while both hosts perform?","STAFF"),
    Case("N01","Everyone has an assigned responsibility.","NONE"),
    Case("N02","All necessary arrangements are confirmed in this example.","NONE"),
    Case("N03","We are just revising the invitation artwork.","NONE"),
    Case("N04","The meeting plan is complete and no issue was raised.","NONE"),
    Case("N05","The room is booked; only an optional game poster remains.","NONE"),
)
def digest():
    return sha256(json.dumps([c.__dict__ for c in CASES],
         sort_keys=True,separators=(",",":")).encode()).hexdigest()
assert len(CASES)==25 and len({c.id for c in CASES})==25
assert sorted({c.gold_gate for c in CASES})==["ACCESS","AUDIO","FOOD","NONE","STAFF"]
