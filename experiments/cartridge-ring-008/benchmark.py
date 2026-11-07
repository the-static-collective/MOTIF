"""Post-freeze falsification of RING-008 generated language programs.

Runs ONLY after a separately saved candidate-program artifact is frozen.
Importing this module is part of heldout evaluation, NOT program search.
The source labels are author-designed synthetic roles across several domains.

There is no network, external action or generated executable code: this parser
produces untrusted PENCIL hypotheses to investigate, never authorizes effects.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys

import engine,world,synthesizer

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"cartridge-ring-007"))
import frames  # frozen hand-coded earlier restricted PATH inquiry baseline

SCHEMA="motif.ring008.postfreeze-semantic-falsification.v1"

class HOLD(ValueError):
    pass


class OldFrame:
    """Strict RING-007's single read-only path question grammar: limited scope."""
    def parse(self,text):
        result=frames.review(text)
        if result["verdict"]=="EXPLORE":
            prediction={"mode":"INQUIRE","topic":"PATH","operator":"REACH"}
        else:
            prediction=None
        return {"status":"NONAUTHORITATIVE_FRAME_HYPOTHESIS"
                if prediction is not None else "HOLD",
                "frame":prediction,
                "raw_text_sha256":sha256(text.encode()).hexdigest()}


class AlwaysHold:
    def parse(self,text):
        return {"status":"HOLD","frame":None,
                "raw_text_sha256":sha256(text.encode()).hexdigest()}


class PrematureAssumer:
    """Probes failure mode, NOT a deployable option."""
    def parse(self,text):
        return {"status":"NONAUTHORITATIVE_FRAME_HYPOTHESIS",
                "frame":{"mode":"INQUIRE","topic":"PATH","operator":"REACH"},
                "raw_text_sha256":sha256(text.encode()).hexdigest()}


def load_artifact(path):
    artifact=json.loads(Path(path).read_text())
    if (not isinstance(artifact,dict) or artifact.get("schema")!=synthesizer.SCHEMA
            or artifact.get("status")!="FINITE_EXECUTABLE_PROGRAM_SEARCH_COMPLETED"
            or artifact.get("heldout_challenge_module_imported") is not False
            or artifact.get("test_outcomes_consulted_during_search") is not False
            or artifact.get("tool_execution_authority")!="NONE"
            or artifact.get("external_action_executed") is not False
            or artifact.get("receipt_sha256")!=engine.digest({
                k:v for k,v in artifact.items() if k!="receipt_sha256"})):
        raise HOLD("Unfrozen, tampered or evaluation-contaminated program")
    spec=engine.validate(artifact.get("selected_program"))
    if engine.digest(spec)!=artifact.get("selected_program_sha256"):
        raise HOLD("Changed invented program identity")
    train=world.generate("train",seed=2026110801,rounds=5)
    dev=world.generate("dev",seed=2026110802,rounds=5)
    if (train["receipt_sha256"]!=artifact["source_train_sha256"]
            or dev["receipt_sha256"]!=artifact["source_dev_sha256"]):
        raise HOLD("Developer source curriculum doesn't match frozen program")
    return artifact,train


def evaluate_frozen(artifact,train):
    # Required split: only NOW, after artifact verification, import new-world
    # challenge labels. The synthesizer never imports this module.
    import novel_world
    champion=engine.train(train,artifact["selected_program"])
    atomic=engine.train(train,artifact["strongest_atomic_seed"])
    baseline_specs={
        "synthesized":champion,
        "atomic_seed":atomic,
        "old_single_path_grammar":OldFrame(),
        "always_abstain":AlwaysHold(),
        "unsafe_permissive_foil":PrematureAssumer(),
    }
    suites=[]
    for seed in (2026110810,2026110811):
        challenge=novel_world.generate(seed=seed,rounds=4)
        results={name:engine.evaluate(decoder,challenge["rows"])
                 for name,decoder in baseline_specs.items()}
        # Do not remove wrong answers: ALL per-case receipts remain inspectable.
        suites.append({
            "seed":seed,
            "heldout_source_packet_sha256":challenge["receipt_sha256"],
            "case_count":len(challenge["rows"]),
            "authored_challenge_families":challenge[
                "author_generated_heldout_families"],
            "systems":results,
            "labels_not_used_for_program_search":True,
        })
    total={}
    for name in baseline_specs:
        metrics={
            key:sum(suite["systems"][name]["metrics"][key] for suite in suites)
            for key in suites[0]["systems"][name]["metrics"]
        }
        total[name]=metrics
    report={
        "schema":SCHEMA,
        "status":"GENERATED_PROGRAM_TESTED_AFTER_FREEZE",
        "program_receipt_sha256":artifact["receipt_sha256"],
        "program_ast":artifact["selected_program"],
        "program_is_not_native_language_general_intelligence":True,
        "source_program_derived_in_finite_audited_dsl":True,
        "heldout_templates_not_trained_or_selected_against":True,
        "utterances_and_labels_author_generated":True,
        "normal_language_human_intent_verification":"NOT_DEMONSTRATED",
        "test_packets":suites,
        "combined":total,
        "candidate_programs_tried_before_heldout":artifact[
            "candidate_programs_tried"],
        "generated_program_found_beyond_seeds":artifact[
            "found_beyond_seed_set"],
        "new_code_executed":False,
        "new_native_executable_admissions":0,
        "external_action_executed":False,
        "authority":"NONE",
    }
    report["receipt_sha256"]=engine.digest(report)
    return report


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--artifact",required=True)
    p.add_argument("--out")
    args=p.parse_args()
    try:
        artifact,train=load_artifact(args.artifact)
        result=evaluate_frozen(artifact,train)
        data=json.dumps(result,sort_keys=True,indent=2)+"\n"
        if args.out:
            path=Path(args.out)
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_text(data)
        print(json.dumps({
            "schema":result["schema"],
            "total_cases":sum(x["case_count"] for x in result["test_packets"]),
            "generated_program":result["program_ast"],
            "result_by_system":result["combined"],
            "beyond_seeds":result["generated_program_found_beyond_seeds"],
            "receipt_sha256":result["receipt_sha256"],
        },sort_keys=True))
    except (HOLD,engine.HOLD,ValueError) as exc:
        print(json.dumps({"status":"HOLD","reason":str(exc),
                          "no_program_execution_fallback":True}))
        raise SystemExit(2)


if __name__=="__main__":
    main()
