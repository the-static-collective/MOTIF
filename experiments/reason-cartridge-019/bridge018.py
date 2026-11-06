"""Real code crosswire to REASON-018's composed relational concept.

A proof that some synthetic "unowned offer" graph exists is NOT proof that
a specific recipient wants a visit. Keep graph fact recognition and human
permission separate. This imports the actual source-pinned REASON-018 code,
not a rewritten simulator.
"""
from __future__ import annotations

from hashlib import sha1
from importlib.util import module_from_spec,spec_from_file_location
from pathlib import Path
import sys

FROM=Path(__file__).resolve().parents[1]/"reason-cartridge-018"/"inventor.py"
BLOB="0a206449bc313070479df3a4897f1a8e7ad12435"


def probe():
    data=FROM.read_bytes()
    actual=sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()
    if actual!=BLOB:
        raise ValueError("Prior relational meaning-maker source code changed")
    sys.path.insert(0,str(FROM.parent))
    spec=spec_from_file_location("motif_reason018_actual_inventor",FROM)
    module=module_from_spec(spec)
    spec.loader.exec_module(module)
    import worlds
    example=worlds.make(0,"HELDOUT")
    program=(0,"OFFER","OPEN","RELEASE","FREE")
    witness=module.prove(program,example)
    if witness is None or module.status(program,example)!="SUPPORTED":
        raise AssertionError("Original REASON-018 source relational witness changed")
    from scenes import by_id
    from golden_mirror import think
    refusal=think(by_id("T01_PROJECTION"))
    if refusal["selected_action"]!="WAIT":
        raise AssertionError("Structural benefit was incorrectly promoted to consent")
    return {
        "prior_reason018_original_source_blob":actual,
        "prior_source_owned_structure":"SUPPORTED",
        "original_shared_node_witness":witness["bound_witness"],
        "reciprocity_trial":refusal["scene_id"],
        "recipient_explicitly_declined":"VISIT",
        "golden_mirror_selected":"WAIT",
        "independent_graph_proof_does_not_authorize_interference":True,
        "claims_about_actual_persons":False,
        "external_actions":False,
    }
