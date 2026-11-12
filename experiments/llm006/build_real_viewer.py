"""Offline true pretrained-model/long-chain comparator replay.

Reuses the proven LLM-005 48-sector interactive event viewer with a visible
RESEARCH-SCOPE correction: three policies really execute frozen pretrained
SmolLM2 at each unverified gate. Two classical source-owned controls do not.
Every digit proposal is independently checked by a synthetic owner; the
source experiment contains NO user data or real-world physical task.
"""
import argparse,json
from pathlib import Path
from marathon import GROUPS,Marathon
from viewer_marathon import PAGE,render as verified_render

NEURAL=("llm_flat","llm_memory","llm_verification")
CLASSICAL=("classical_bayes","hypermap_voi")

def build(source_summary,source_traces):
    if source_summary.get("schema")!="motif.llm006.real-marathon/v0" or not source_summary.get("pretrained_model_was_actually_loaded"):
        raise ValueError("NOT_REAL_MODEL_RECEIPT")
    if source_traces.get("schema")!="motif.llm006.model-traces/v0" or source_traces.get("external_actions") is not False:
        raise ValueError("NO_VALID_MODEL_TRACE")
    records=dict(source_traces["arms"])
    if set(records)!=set(NEURAL):raise ValueError("MISSING_PRETRAINED_POLICIES")
    if tuple(source_summary["research_group"])!=GROUPS[0]:raise ValueError("WRONG_REGISTERED_WORLD_GROUP")
    for policy in CLASSICAL:
        m=Marathon(GROUPS[0],policy)
        m.execute()
        records[policy]=m.public_record()
    arms=[]
    for policy in NEURAL+CLASSICAL:
        summary=records[policy]["summary"]
        arms.append({"policy":policy,
          "full_completions":int(summary["completed"]),
          "marathons":1,
          "mean_serial_actions":summary["actual_serial_actions"],
          "mean_synthetic_cost":summary["synthetic_cost"],
          "mean_wrong_commits":summary["wrong_commitments"],
          "mean_completed_decisions":summary["completed_decision_gates"]})
    dataset={"schema":"motif.odyssey-marathon.viewer/v0",
      "scope":"AUTHORED_PUBLIC_SYNTHETIC_TASK_BUT_ACTUAL_FROZEN_PRETRAINED_WEIGHT_INFERENCE",
      "group":list(GROUPS[0]),
      "study":{"author_synthetic_only":True,"arms":arms,
               "model_experiment_real":True,
               "model_revision":source_summary["revision"],
               "not_a_real_world_intelligence_benchmark":True},
      "records":records,"external_actions":False,"real_model":True}
    # Reuse the existing source-sanitizing packet acceptance validation.
    verified_render(dataset)
    page=PAGE
    page=page.replace("MOTIF ODYSSEY MARATHON — 879+ Causal Actions",
                      "MOTIF REAL PRETRAINED ODYSSEY — 879+ Causal Actions")
    page=page.replace("ODYSSEY: THE MARATHON","ODYSSEY: THE PRETRAINED MODEL")
    page=page.replace("Post-hoc Length Escalation","Actual frozen pretrained model crossing")
    page=page.replace(
      "this is a deterministic author-designed fictional simulator\nusing MOTIF's typed Reason Hypermap, not a pretrained LLM, external physical task, or real user decision.\nHandoffs and signatures below are consistency hashes, not real-world witness authentication.",
      "THIS RUN REALLY EXECUTED FROZEN PRETRAINED SmolLM2-135M-Instruct for each unverified checkpoint in the three neural policies. Every input and verifying owner is an authored synthetic Boolean fixture, NOT a real-world task or evidence. Classical controls are non-neural. Handoffs are consistency hashes, NOT external source authentication.")
    page=page.replace("Four registered marathon groups · descriptive study",
                      "Same registered fictional group · three real-model policies and two classical controls")
    page=page.replace("Same source-owner rules and action/cost limits within each group.",
                      "Same synthetic source-owner rules and action/cost limits within this one registered group.")
    page=page.replace(
      'const policyNames={hypermap_voi:',
      'const policyNames={llm_flat:"REAL SmolLM2 — calibration only",'+
      'llm_memory:"REAL SmolLM2 — source memory",'+
      'llm_verification:"REAL SmolLM2 — memory + paid verification",hypermap_voi:')
    page=page.replace('sel.value=D.records.hypermap_voi?"hypermap_voi":Object.keys(D.records)[0];',
                      'sel.value=D.records.llm_memory?"llm_memory":Object.keys(D.records)[0];')
    page=page.replace("__PAYLOAD__",json.dumps(dataset,sort_keys=True,ensure_ascii=False).
        replace("<","\\u003c").replace(">","\\u003e").replace("&","\\u0026"))
    if "__PAYLOAD__" in page:raise ValueError("UNSAFE_UNFILLED_VIEWER")
    return page,dataset

def main():
    p=argparse.ArgumentParser();p.add_argument("--out",default="/tmp/llm006")
    args=p.parse_args()
    folder=Path(args.out)
    summary=json.loads((folder/"real-model-summary.json").read_text())
    traces=json.loads((folder/"real-model-traces.json").read_text())
    page,data=build(summary,traces)
    (folder/"real-model-marathon.html").write_text(page,encoding="utf-8")
    (folder/"real-model-viewer-study.json").write_text(json.dumps({
      "scope":data["scope"],"group":data["group"],
      "model":summary["model"],"revision":summary["revision"],
      "runs":data["study"]["arms"],
      "forward_count":summary["model_forwards"],
      "no_real_world_actions":True,
      "no_pretrained_claim_for_classical_controls":True},sort_keys=True,indent=2)+"\n")
    print("REAL_MODEL_MARATHON_VIEWER_BYTES",len(page.encode()))
    print("PAIRED_FULL_REPLAY",json.dumps(data["study"]["arms"]),flush=True)

if __name__=="__main__":main()
