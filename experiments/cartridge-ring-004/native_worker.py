"""Isolated cross-source runtime: *one* public synthetic packet, three real engines.

This file is a controlled adapter harness, not a reimplementation of the native
GEOM-013, THOUGHT-014, or REASON-006 algorithms. Their exact original source
trees are supplied separately at pinned commits. No hidden labels are in the
sandbox or in the public packet, and no arbitrary branch is imported.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys


def bind_source_roots():
    sources=Path("/work")
    roots=(
        sources/"geometry"/"experiments"/"geometry-013",
        sources/"language"/"experiments"/"thought-014",
        sources/"reason"/"experiments"/"reason-cartridge-006",
    )
    if not all(r.is_dir() for r in roots):
        raise ValueError("All three source-native pinned trees required")
    # Unique source-root identity, no implicit blending of same-name Python
    # modules from mutually divergent Git history.
    for root in reversed(roots):
        sys.path.insert(0,str(root))
    import demo as geometry_demo
    from redesign import RecordedCase,RecordedEvent,IdentifierAccess
    from language_space import LanguageSpace
    from model_gateway import TinyTextModel
    from fixtures import TRAIN as original_language_training
    from commonwealth import run_council,owner4
    return (geometry_demo,RecordedCase,RecordedEvent,IdentifierAccess,
            LanguageSpace,TinyTextModel,original_language_training,run_council,owner4)


def native_run(packet):
    if (not isinstance(packet,dict) or packet.get("schema")!="motif.shared-evidence-public.v1"
            or packet.get("no_labels_inside_native_runner") is not True
            or not isinstance(packet.get("cases"),list)
            or len(packet["cases"])>48):
        raise ValueError("Unsupported shared-evidence packet")
    (geom,RecordedCase,RecordedEvent,IdentifierAccess,
     LanguageSpace,TinyTextModel,original_language_training,
     run_council,owner4)=bind_source_roots()
    # Train ORIGINAL source-owned tiny supervised classifier only on THOUGHT-014
    # training examples, never on heldout labels or this packet outcomes.
    tiny_model=TinyTextModel(original_language_training)

    # The original GEOM-013 source builds its revision using development
    # cases from its own earlier experiment, NOT the heldout packet here.
    active,first,second,p1,improved,p2,final=geom.two_revisions()
    caps=geom.capabilities()
    catalog={c.channel:c for c in caps}
    identifier=IdentifierAccess(geom.SCOPE,True,True,0.25)
    parent_digest=hashlib.sha256(json.dumps(final.parent.data(),
                              sort_keys=True).encode()).hexdigest()
    if not all(final.distinct):
        raise ValueError("Original source's frozen learned procedure is not fully duplicate-aware")
    rows=[]
    for item in packet["cases"]:
        if (not isinstance(item,dict)
                or set(item)!={"id","gate_open","utterance","selected_pair","records","scope"}
                or item["scope"]!=geom.SCOPE
                or type(item["gate_open"]) is not bool
                or not isinstance(item["records"],(list,type(None)))
                or not isinstance(item["id"],str)):
            raise ValueError("Case schema mismatch")
        cid=item["id"]
        engine=type("StrictSyntheticEngine",(),{})()
        engine.manifests={"m-route-start":object(),"m-route-end":object()}
        engine.input_digest=hashlib.sha256(json.dumps(item,sort_keys=True).encode()).hexdigest()
        # Native THOUGHT-014 LanguageSpace, which calls the original 013
        # conservative interpreter. No generative model and no network.
        baseline_speech=LanguageSpace(engine).explore(
            item["utterance"],selected_pair=item["selected_pair"],model=None)
        speech=LanguageSpace(engine).explore(
            item["utterance"],selected_pair=item["selected_pair"],model=tiny_model)
        baseline_safe=(baseline_speech["status"]=="TYPED_ONLY" and
                       baseline_speech["speech_act"] in (
                            "EXPLORE_POSSIBILITY","CHALLENGE","COMPARE","INSPECT_EVIDENCE"))
        safe=speech["status"]=="TYPED_ONLY" and speech["speech_act"] in (
            "EXPLORE_POSSIBILITY","CHALLENGE","COMPARE","INSPECT_EVIDENCE")
        if speech["status"]=="HOLD" and speech["speech_act"]=="HOLD_EFFECT_REQUEST":
            safe=False
        records=None if item["records"] is None else [
            RecordedEvent(tick=r["tick"],channel=r["channel"],event_id=r["event_id"])
            for r in item["records"]]
        # RecordedCase's expected label is required by the SOURCE constructor
        # but ignored by Revision.measure; constant sentinel is NOT the hidden
        # task label and is never used for scoring.
        synthetic=RecordedCase.make(
            cid,("sprout","bud"),("sprout","branch"),
            {"appearance":"same-bud","season":"synthetic-spring"},
            False,records,"claimed:shared-evidence",geom.SCOPE)
        raw=active.measure(synthetic,catalog,geom.WINDOWS,geom.BUDGET,identifier)
        repaired=final.measure(synthetic,catalog,geom.WINDOWS,geom.BUDGET,identifier)
        # Native REASON-006 council proofs operate on exactly the same graph
        # case and generated measurement witness. Their conclusions are
        # *relative to declared, synthetic witnesses*, never physical facts.
        def reason(bit):
            if bit is None:
                return {"status":"HOLD","conclusion":None,"proof_present":False}
            q=owner4.Inquiry(
                ("S","A","T"),
                (("S","A"),("A","T"),("S","T")),
                (("S","A","PRESENT" if item["gate_open"] else "ABSENT",
                  cid+":gate"),
                 ("A","T","PRESENT" if bit else "ABSENT",cid+":sensor")),
                ("S","T"),True)
            council=run_council(q,name=cid,source=None)
            if (council["external_actions"] is not False
                    or council["real_world_authority"] is not False):
                raise ValueError("Native council attempted external effects")
            verdict=council["after"]
            return {
                "status":"CERTIFIED_SYNTHETIC_GRAPH_DECISION",
                "conclusion":verdict,
                "proof_present":bool(council["final_witness"]),
                "source_revision":council["source_revision"],
                "source_ledger_novel":council["marginal"]["novel"],
            }
        raw_reason=reason(raw["value"])
        repaired_reason=reason(repaired["value"])
        rows.append({
            "id":cid,
            "language":{"speech_act":speech["speech_act"],
                        "status":speech["status"],"safe":safe,
                        "baseline_safe":baseline_safe,
                        "baseline_act":baseline_speech["speech_act"],
                        "model_consulted":speech["model_consulted"],
                        "model_accepted_as_hypothesis":speech["model_accepted_as_hypothesis"],
                        "source_class":speech["source_class"],
                        "pen_state":speech["pen_state"]},
            "geometry":{"raw":raw,"repaired":repaired,
                        "learned_distinct_steps":sum(final.distinct)},
            "reason":{"raw":raw_reason,"repaired":repaired_reason},
            "native_source_types":["GEOM-013.Revision.measure",
                                    "THOUGHT-014.LanguageSpace.explore",
                                    "REASON-006.run_council"],
        })
    output={"schema":"motif.shared-native-output.v1",
            "world":"ONE_SHARED_AUTHORED_SYNTHETIC_EVIDENCE_PACKET",
            "public_digest_sha256":hashlib.sha256(json.dumps(packet,
                sort_keys=True,separators=(",",":")).encode()).hexdigest(),
            "source_owner_geom_parent_sha256":parent_digest,
            "source_native_geometry_procedure_learned_from_other_cases":True,
            "all_three_native_algorithms_receive_same_case_ids":True,
            "language_model_kind":"TRAINED_NAIVE_BAYES_NOT_LLM",
            "language_model_calls":sum(1 for row in rows if row["language"]["model_consulted"]),
            "external_action_executed":False,"authority":"NONE",
            "results":rows}
    return output


if __name__=="__main__":
    if len(sys.argv)!=2:
        raise SystemExit("usage: python native_worker.py /work/public.json")
    packet=json.loads(Path(sys.argv[1]).read_text())
    print(json.dumps(native_run(packet),sort_keys=True))
