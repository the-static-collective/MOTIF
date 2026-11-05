"""Independent, entirely invented fixture for MOTIF-017F.

The question builder and planner do NOT import this module. The evaluator's
separate synthetic reporter is where actual probe outcomes are generated.
"""
from __future__ import annotations

from dataclasses import dataclass
import json

from grower import QuestionOffer, IndependentReceipt
from forest import Road
from multiplex import Hypothesis


@dataclass(frozen=True)
class TestWorld:
    name: str
    phase: str
    repetition: int = 0


def problem():
    hypotheses = [
        Hypothesis(f"{mode}{left}{right}",
                   "YES" if left != right else "NO")
        for mode in "01" for left in "01" for right in "01"
    ]
    names = [h.name for h in hypotheses]
    bit = lambda at: {name: name[at] for name in names}
    roads = [
        Road("SCOUT", "ASK", .20, bit(0), "scout"),
        Road("BAIT", "VERIFY", .60,
             {name: str(name == "000") for name in names}, "bait"),
        Road("GLOBAL_A", "ASK", 1., bit(1), "port-a"),
        Road("GLOBAL_B", "ASK", 1., bit(2), "port-b"),
    ]
    for mode in "01":
        roads += [
            Road(f"FAST_A_{mode}", "ASK", .35, bit(1), f"fast-a-{mode}",
                 requires=(("SCOUT", mode),)),
            Road(f"FAST_B_{mode}", "ANSWER", .35, bit(2), f"fast-b-{mode}",
                 requires=(("SCOUT", mode),)),
        ]
    offers = (
        QuestionOffer("FUSED_PORTS", ("GLOBAL_A", "GLOBAL_B"),
                      "offered-composite-sensor", .65),
        QuestionOffer("FALSE_SHORTCUT", ("GLOBAL_A", "GLOBAL_B"),
                      "misreporting-sensor", .25),
        QuestionOffer("DRIFT_FUSED_PORTS", ("GLOBAL_A", "GLOBAL_B"),
                      "drift-sensor", .45),
        QuestionOffer("OVERPRICED_PORTS", ("GLOBAL_A", "GLOBAL_B"),
                      "pricey-sensor", 1.10),
        QuestionOffer("FORBIDDEN_PORTS", ("GLOBAL_A", "GLOBAL_B"),
                      "no-permission", .05, allowed=False),
    )
    return hypotheses, roads, offers


def measure(offer: QuestionOffer, world: TestWorld) -> str:
    """Independent simulator response, not the planner's predicted map."""
    if world.name not in ("000", "001", "010", "011", "100", "101", "110", "111"):
        raise ValueError("Unknown evaluator-only world")
    a, b = world.name[1], world.name[2]
    if offer.name == "FALSE_SHORTCUT" and world.name == "111":
        a = "0" if a == "1" else "1"
    if offer.name == "DRIFT_FUSED_PORTS" and world.phase == "TEST" and world.name[0] == "1":
        b = "0" if b == "1" else "1"
    return json.dumps([a, b], separators=(",", ":"))


def reviewed_receipts(offer: QuestionOffer):
    # REVIEW cases are separately generated, and never supplied to
    # question invention or to the TEST oracle. We know these truth labels
    # only because this is an adjudicated *synthetic* calibration fixture.
    records = []
    for i, name in enumerate(("000", "001", "010", "011", "100", "101", "110", "111")):
        for repetition in range(2):
            world = TestWorld(name, "REVIEW", repetition)
            records.append(IndependentReceipt(
                case_id=f"review-{i}-{repetition}",
                known_world=name,
                declared_provider=offer.provider,
                observed=measure(offer, world),
                charged_cost=offer.price,
            ))
    return tuple(records)
