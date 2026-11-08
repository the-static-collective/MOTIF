"""QC-008: explicitly repair QC-007's 'zero paths' blind spot.

The old fixture World(can_travel=False, has_phone=False, food_in_hand=False)
does not establish inability to walk, locate a neighbor, seek human assistance,
or first improve situational awareness. This adapter reads the exact prior
QC-007 frozen scenario and preserves its result as an historical receipt,
then opens an epistemic/capability **research** stage without modifying it.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"quantumcode007"))
from living_field import action_inventory, scenario, plan
from recover import YES,NO,UNKNOWN, Situation, recover


@dataclass(frozen=True)
class RepairWitness:
    prior_status: str
    prior_world_receipt: str
    prior_viable_paths: int
    new_status: str
    proposed_next_actions: tuple[str,...]
    restored_actual_meals: int
    actual_external_actions: int
    note: str


def upgrade_legacy_hold():
    world,context=scenario("isolated")
    prior=plan(world,context,action_inventory())
    if prior.status!="HOLD_NO_SAFE_COMPLETE_PATH" or prior.viable_paths:
        raise AssertionError("Expected QC-007 no-direct-route regression")
    observations=Situation((),"IMMEDIATE","ORDINARY")
    observations=observations.append("has_phone",NO,
                                     "QC007:"+prior.source_receipt,
                                     kind="SYNTHETIC_FIXTURE")
    observations=observations.append("motor_transport",NO,
                                     "QC007:"+prior.source_receipt,
                                     kind="SYNTHETIC_FIXTURE")
    observations=observations.append("has_food",NO,
                                     "QC007:"+prior.source_receipt,
                                     kind="SYNTHETIC_FIXTURE")
    recovery=recover(observations)
    return RepairWitness(
        prior.status,prior.source_receipt,len(prior.viable_paths),
        recovery.status,recovery.next_field,0,recovery.external_actions,
        "The prior can_travel=False is insufficient evidence about walking "
        "ability, safety, available people or safe destinations. "
        "No meal or local service has been verified.")


if __name__=="__main__":
    import json
    x=upgrade_legacy_hold()
    print(json.dumps(x.__dict__,sort_keys=True,indent=2))
