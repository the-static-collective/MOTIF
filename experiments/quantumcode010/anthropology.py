"""QC-010: anthropological analogy is an affordance clue, never an exemption.

Human making-do has a substantial anthropological literature on bricolage:
Claude Lévi-Strauss, The Savage Mind (1962), and contemporary work on
improvisation under constraints. The method is to derive a HYPOTHESIS from
a documented similarity, preserve disanalogies and then test materially.

The source PIN here protects the manually curated research claim, not proof
that a modern reused construction is safe. No field visits or human subjects.
"""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
import json

SOURCE_INDEX={
    "bricolage_2024":{
        "url":"https://www.harvard-yenching.org/research/improvisation-collective-structure-and-culture-change-a-theory-of-bricolage/",
        "claim":"Anthropological theory describes bricolage as regulated "
                "improvisation using a limited repertoire of resources; "
                "it does not validate the safety of specific constructions.",
    },
    "archaeological_bricolage":{
        "url":"https://doi.org/10.4000/PM.1980",
        "claim":"Archaeological study uses the concept of combining repurposed "
                "existing material, techniques and attributes into new designs. "
                "Historical existence is not current-context safety clearance.",
    },
    "safety_II":{
        "url":"https://www.sciencedirect.com/science/article/pii/S0951832018309864",
        "claim":"Resilience engineering distinguishes centralized specification "
                "from guided adaptive behavior in emergent real situations.",
    },
    "safety_II_critique":{
        "url":"https://www.sciencedirect.com/science/article/pii/S0925753520304446",
        "claim":"Safety-II's empirical demonstration and framework have been "
                "contested; do not infer effectiveness without testing.",
    },
}


def seal(o):
    return sha256(json.dumps(o,sort_keys=True,separators=(",", ":")).encode()).hexdigest()


@dataclass(frozen=True)
class HistoricalPattern:
    name: str
    supporting_sources: tuple[str,...]
    operative_features: tuple[str,...]
    source_scope: str = "ABSTRACT_COMPOSITION_ONLY"

    def check(self):
        if (not self.name or not self.operative_features
            or not self.supporting_sources
            or self.source_scope!="ABSTRACT_COMPOSITION_ONLY"
            or any(k not in SOURCE_INDEX for k in self.supporting_sources)):
            raise ValueError("Historical inference lacks valid scope/provenance")


@dataclass(frozen=True)
class ContemporaryProblem:
    name: str
    known_shared_features: tuple[str,...]
    necessary_physical_unknowns: tuple[str,...]
    limits: tuple[str,...]


@dataclass(frozen=True)
class Transfer:
    original: str
    current: str
    shared: tuple[str,...]
    unverified: tuple[str,...]
    cautions: tuple[str,...]
    disposition: str
    source_pins: tuple[str,...]
    inferred_safe_to_operate: bool = False
    verified_outcome: bool = False


def compare(history:HistoricalPattern,present:ContemporaryProblem):
    history.check()
    common=tuple(sorted(set(history.operative_features) &
                        set(present.known_shared_features)))
    proof=tuple(sorted(set(present.necessary_physical_unknowns)))
    cautions=tuple(sorted(set(present.limits)))
    sources=tuple(seal((k,SOURCE_INDEX[k]))
                  for k in history.supporting_sources)
    if not common:
        verdict="NO_USEFUL_SHARED_MECHANISM"
    elif proof:
        verdict="ANALOGICAL_FEASIBILITY_HYPOTHESIS__INSPECT_FIRST"
    else:
        verdict="ANALOGICAL_IDEA_ONLY__INDEPENDENT_TEST_REQUIRED"
    return Transfer(history.name,present.name,common,proof,cautions,
                    verdict,sources)


def samples():
    pattern=HistoricalPattern(
        "documented_bricolage",
        ("bricolage_2024","archaeological_bricolage",
         "safety_II","safety_II_critique"),
        ("reassign_existing_materials","test_geometry",
         "assemble_parts","test_under_constraints"),
    )
    oven=ContemporaryProblem(
        "reused_materials_for_cooking",
        ("reassign_existing_materials","test_geometry","assemble_parts"),
        ("actual_heat_rating","unknown_coatings",
         "fire_clearance","food_contact_suitability"),
        ("Historic material recombination does not certify concrete pavers",
         "A successful meal does not establish future thermal/fire safety"),
    )
    repair=ContemporaryProblem(
        "resource_limited_equipment_repair",
        ("reassign_existing_materials","assemble_parts"),
        ("electrical_state","mechanical_compatibility"),
        ("Do not infer compatibility from appearance alone",),
    )
    unrelated=ContemporaryProblem(
        "unrelated_spiritual_claim",("non_overlapping_mechanism",),
        (),("Do not force an analogy",),
    )
    return pattern,(oven,repair,unrelated)


def report():
    source,problems=samples()
    results=tuple(compare(source,p) for p in problems)
    return {
        "experiment":"QC-010-ANTHROPOLOGICAL-TRANSFER",
        "source_index":SOURCE_INDEX,
        "cases":[x.__dict__ for x in results],
        "safety_assumed_from_historical_precedent":False,
        "historical_analogy_automatically_executed":False,
        "real_world_interventions":0,
    }


if __name__=="__main__":
    print(json.dumps(report(),sort_keys=True,indent=2))
