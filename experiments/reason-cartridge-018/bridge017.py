"""Control: original REASON-017 can store a phrase, not discover its structure.

This is a *source-pinned live import* of the actual prior engine, not a
reimplementation. REASON-017's deliberately minimal method is valuable:
it declines to invent semantics for copied unfamiliar words. REASON-018
proposes the additional step of learning a BOUNDED graph formula from examples.
"""
from __future__ import annotations

from hashlib import sha1
from importlib.util import spec_from_file_location,module_from_spec
from pathlib import Path

PREVIOUS=Path(__file__).resolve().parents[1]/"reason-cartridge-017"/"engine.py"
PIN="d45d44962031538f340132547b08ac975ca1d418"


def probe():
    raw=PREVIOUS.read_bytes()
    actual=sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
    if actual!=PIN:
        raise ValueError("Original REASON-017 source code changed")
    spec=spec_from_file_location("motif_reason017_original",PREVIOUS)
    module=module_from_spec(spec)
    spec.loader.exec_module(module)
    phrase="a way to receive help without surrendering future choices"
    original_reply="Neither. I need "+phrase+"."
    extracted=module.extract_goal(original_reply,"INITIAL")
    if extracted!=phrase:
        raise AssertionError("Previous system no longer source-preserves unknown goals")
    return {
        "prior_real_source_git_blob":actual,
        "prior_literal_unfamiliar_phrase":extracted,
        "prior_extracted_meaning_type":"QUOTED_GOAL_NOT_SEMANTIC_CONCEPT",
        "prior_hypothesis_identifier":module.hypothesis(extracted),
        "prior_graph_schema":None,
        "new_experiment_only_invents_bounded_relational_composition":True,
        "no_machine_subjective_emotion":True,
    }
