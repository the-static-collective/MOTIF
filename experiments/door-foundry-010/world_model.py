"""MOTIF-010: evidence-preserving Bayesian updates of four original PNG worlds.

All observations are explicitly synthetic offline fixtures. Nothing is
observed in reality, and prior text, images, and contradictory evidence stay
in the audit. Exact Fractions and a separate likelihood-product baseline.
"""
from __future__ import annotations
import argparse,json,math,sys
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path[:0]=[str(HERE.parent/"door-foundry-009"),
             str(HERE.parent/"door-foundry-006")]
import decision as classical
import visual_in as pixels

WORLD_IDS=classical.WORLD_IDS
PRIORS={"LEFT_PARTIAL":Fraction(1,10),"RIGHT_PARTIAL":Fraction(1,10),
        "LEFT_FULL":Fraction(4,10),"RIGHT_FULL":Fraction(4,10)}
SCHEMA="motif010.evidence-event.v0"
READ_ONLY="SYNTHETIC_LOCAL_FIXTURE_NOT_A_REAL_OBSERVATION"
VALUES={"side":("left","right"),"wall_extent":("partial","full")}
class HOLD(ValueError):pass

def need(x,msg):
    if not x:raise HOLD(msg)
def digest(obj):return pixels.digest(obj)
def frac(v):
    need(type(v) is str and len(v)<=30,"HOLD_NONCANONICAL_FRACTION")
    try:x=Fraction(v)
    except (ValueError,ZeroDivisionError) as exc:raise HOLD("HOLD_BAD_FRACTION") from exc
    need(str(x)==v,"HOLD_NONCANONICAL_FRACTION")
    return x
def stored(weights):return {k:str(weights[k]) for k in WORLD_IDS}
def typed_weights(w):
    need(type(w) is dict and set(w)==set(WORLD_IDS),"HOLD_DIFFERENT_WORLD_SUPPORT")
    out={k:frac(w[k]) for k in WORLD_IDS}
    need(all(x>0 for x in out.values()) and sum(out.values())==1,
         "HOLD_UNNORMALIZED_BELIEF")
    return out
def read(path):
    p=Path(path)
    need(p.is_file() and p.stat().st_size<=150000,"HOLD_MISSING_EVIDENCE")
    try:result=json.loads(p.read_text())
    except ValueError as exc:raise HOLD("HOLD_MALFORMED_EVIDENCE") from exc
    need(type(result) is dict,"HOLD_EVIDENCE_NOT_RECORD")
    return result

def verify_original(question_dir):
    """Byte-check the original MOTIF-009 PNG worlds and bounded model contract."""
    root=Path(question_dir)
    record=read(root/"active-question.json")
    raw=dict(record);sha=raw.pop("content_sha256",None)
    need(sha==digest(raw),"HOLD_ORIGINAL_009_DIGEST_CHANGED")
    custody={"question_sent":False,"actual_answer_observed":False,
       "current_world_identified":False,"physical_actions":0,
       "external_api_calls":0,"T5_calls":0,"code_automatically_admitted":False}
    need(record.get("schema")=="motif.active-visual-question.v0" and
         record.get("status")=="UNSENT_QUESTION_WITH_FOUR_IMAGE_HYPOTHESES" and
         record.get("model")=="FOUR_SYNTHETIC_WORLDS_NOT_OBSERVATIONS" and
         record.get("custody")==custody and
         record.get("original_GRAFT_generated_source_sha256")==
             "493ecef0320408eed87ec4e9e56c3960f2b6a168caafaa050a22d003f0e5ebe6" and
         type(record.get("visual_worlds")) is list and len(record["visual_worlds"])==4,
         "HOLD_ORIGINAL_SOURCE_OR_AUTHORITY")
    initial=record.get("analysis",{}).get("cost_model",{}).get("prior_probability")
    need(initial=={k:float(PRIORS[k]) for k in WORLD_IDS},
         "HOLD_ORIGINAL_009_PRIOR_CHANGED")
    worlds={}
    for row in record["visual_worlds"]:
        need(type(row) is dict,"HOLD_BAD_SOURCE_WORLD")
        name=row.get("id")
        need(name in WORLD_IDS and name not in worlds,"HOLD_INVALID_WORLD_ID")
        side,extent=name.lower().split("_")
        need(row.get("side")==side and row.get("wall_extent")==extent and
          row.get("real_world_status")=="UNKNOWN_NOT_OBSERVED" and
          row.get("original_CANNON_review_is_code_only_for_new_images") is True and
          row.get("reachable_in_this_model") is (extent=="partial"),
          "HOLD_ORIGINAL_WORLD_CLAIMS_CHANGED")
        folder=root/"worlds"/name
        before=(folder/"start.png").read_bytes()
        after=(folder/"target.png").read_bytes()
        need(sha256(before).hexdigest()==row.get("start_png_sha256") and
             sha256(after).hexdigest()==row.get("target_png_sha256"),
             "HOLD_SOURCE_PNG_HASH_CHANGED")
        gap=read(folder/"image-gap.json")
        need(pixels.verify_gap(gap,before,after)==row.get("image_gap_sha256"),
             "HOLD_CHANGED_ORIGINAL_PNG_GAP")
        frame=pixels.decode_png(before)
        red=pixels.coords(frame,"R");blue=pixels.coords(frame,"#")
        need(len(red)==4 and len(blue)==(4 if extent=="partial" else 8) and
             (min(x for x,_ in red)<4)==(side=="left"),
             "HOLD_ORIGINAL_WORLD_PIXELS_INCONSISTENT")
        worlds[name]={"id":name,"side":side,"wall_extent":extent,
           "start_png_sha256":row["start_png_sha256"]}
    need(set(worlds)==set(WORLD_IDS),"HOLD_SOURCE_MODEL_MISSING")
    return record,[worlds[k] for k in WORLD_IDS]

def make_event(number,field,value,reliability="9/10",source=READ_ONLY):
    need(type(number) is int and 1<=number<=30,"HOLD_EVENT_ORDER_BOUND")
    need(field in VALUES and value in VALUES[field],"HOLD_UNSUPPORTED_SENSOR_VALUE")
    reliability_fraction=frac(reliability)
    need(Fraction(1,2)<reliability_fraction<1,
         "HOLD_UNSUPPORTED_SENSOR_RELIABILITY")
    need(source==READ_ONLY,"HOLD_NOT_A_GENUINE_EXTERNAL_SENSOR")
    core={"schema":SCHEMA,"event_id":f"SIM-{number:03d}",
      "sequence":number,"observed_attribute":field,
      "simulated_sensor_output":value,
      "assumed_conditional_accuracy":reliability,
      "assumed_independent_given_world":True,
      "source":READ_ONLY,"real_human_answer":False,
      "physical_observation":False,"can_trigger_real_actions":False}
    return {**core,"content_sha256":digest(core)}

def verify_event(e,seq):
    need(type(e) is dict and set(e)=={
      "schema","event_id","sequence","observed_attribute",
      "simulated_sensor_output","assumed_conditional_accuracy",
      "assumed_independent_given_world","source","real_human_answer",
      "physical_observation","can_trigger_real_actions","content_sha256"},
      "HOLD_EVENT_SHAPE")
    core=dict(e);claimed=core.pop("content_sha256")
    need(claimed==digest(core),"HOLD_CHANGED_EVIDENCE")
    need(e["schema"]==SCHEMA and type(e["sequence"]) is int and
         e["sequence"]==seq and e["event_id"]==f"SIM-{seq:03d}" and
         e["observed_attribute"] in VALUES and
         e["simulated_sensor_output"] in VALUES[e["observed_attribute"]] and
         e["assumed_independent_given_world"] is True and
         e["source"]==READ_ONLY and
         e["real_human_answer"] is False and
         e["physical_observation"] is False and
         e["can_trigger_real_actions"] is False,
         "HOLD_EVIDENCE_AUTHORITY_UNSUPPORTED")
    accuracy=frac(e["assumed_conditional_accuracy"])
    need(Fraction(1,2)<accuracy<1,"HOLD_INVALID_SENSOR_MODEL")
    return accuracy

def likelihood(event,w):
    r=frac(event["assumed_conditional_accuracy"])
    return r if w[event["observed_attribute"]]==event["simulated_sensor_output"] else 1-r

def independent_batch_posterior(prior,worlds,events):
    """Independent product-of-likelihoods reference, not recursive update."""
    raw={w["id"]:prior[w["id"]]*math.prod(likelihood(e,w) for e in events)
         for w in worlds}
    den=sum(raw.values());need(den>0,"HOLD_ZERO_BAYES_MASS")
    return {k:raw[k]/den for k in WORLD_IDS}

def increment(prior,worlds,event):
    raw={w["id"]:prior[w["id"]]*likelihood(event,w) for w in worlds}
    total=sum(raw.values());need(total>0,"HOLD_SENSOR_ZERO_SUPPORT")
    return {k:raw[k]/total for k in WORLD_IDS}

def predictive(weights,worlds,event):
    return sum(weights[w["id"]]*likelihood(event,w) for w in worlds)

def best_decision(weights,worlds):
    score,policy=classical.terminal(worlds,weights)
    return {"action":policy["decision"],"expected_loss":float(score)}

def fixture(truth):
    need(truth in WORLD_IDS,"HOLD_UNKNOWN_TEST_WORLD")
    side,extent=truth.lower().split("_")
    return ([make_event(1,"wall_extent",extent),
             make_event(2,"side",side),
             make_event(3,"wall_extent",extent)],
            make_event(4,"side",side))

def single_replay(question_dir,truth,out,events=None,heldout=None):
    out=Path(out)
    need(not out.exists(),"HOLD_REPLAY_MUST_NOT_OVERWRITE")
    source,worlds=verify_original(question_dir)
    need(truth in WORLD_IDS,"HOLD_UNKNOWN_SYNTHETIC_TRUTH")
    sample,withheld=fixture(truth)
    if events is None:events=sample
    if heldout is None:heldout=withheld
    need(type(events) is list and 1<=len(events)<=12,"HOLD_BAD_EVENT_BATCH")
    for i,e in enumerate(events,1):verify_event(e,i)
    verify_event(heldout,len(events)+1)
    prior=dict(PRIORS)
    previous=source["content_sha256"]
    history=[]
    applied=[]
    for i,e in enumerate(events,1):
        old=dict(prior)
        prob=predictive(old,worlds,e)
        revised=increment(old,worlds,e)
        applied.append(e)
        need(revised==independent_batch_posterior(PRIORS,worlds,applied),
             "HOLD_BAYES_DISAGREES_WITH_INDEPENDENT_LIKELIHOOD_PRODUCT")
        next_cost,next_policy=classical.optimal(
            worlds,revised,classical.standard_costs(),2)
        b={"schema":"motif010.belief-revision.v0",
           "sequence":i,"previous_receipt_sha256":previous,
           "evidence_receipt_sha256":e["content_sha256"],
           "evidence":e,
           "prior":stored(old),"posterior":stored(revised),
           "predictive_probability_before_update":str(prob),
           "prequential_log_loss":-math.log(float(prob)),
           "old_best_terminal_decision":best_decision(old,worlds),
           "new_best_terminal_decision":best_decision(revised,worlds),
           "next_question_proposed_but_unsent":next_policy.get("question_id"),
           "next_question_policy":next_policy,
           "next_question_expected_loss":float(next_cost),
           "contradictory_evidence_never_erased":True,
           "physical_scene_not_observed":True,
           "real_world_actions":0}
        row={**b,"content_sha256":digest(b)}
        history.append(row)
        previous=row["content_sha256"]
        prior=revised
    static_forecast=predictive(PRIORS,worlds,heldout)
    updated_forecast=predictive(prior,worlds,heldout)
    orig_dec=best_decision(PRIORS,worlds)
    new_dec=best_decision(prior,worlds)
    true=next(w for w in worlds if w["id"]==truth)
    body={
      "schema":"motif010.world-model-replay.v0",
      "status":"SYNTHETIC_BELIEF_UPDATES_AND_UNSEEN_FORECAST_SCORED",
      "original_009_question_receipt_sha256":source["content_sha256"],
      "original_PNG_worlds":{w["id"]:w["start_png_sha256"] for w in worlds},
      "test_fixture_world_only_not_observed":truth,
      "initial_prior":stored(PRIORS),"posterior":stored(prior),
      "history":history,"last_chain_sha256":previous,
      "heldout_event":heldout,"heldout_used_for_training":False,
      "scoring":{
        "frozen_prior_forecast":str(static_forecast),
        "updated_forecast":str(updated_forecast),
        "frozen_prior_brier":float((1-static_forecast)**2),
        "updated_brier":float((1-updated_forecast)**2),
        "frozen_prior_log_loss":-math.log(float(static_forecast)),
        "updated_log_loss":-math.log(float(updated_forecast)),
        "this_case_improved":updated_forecast>static_forecast,
        "generalization_not_established":True},
      "decision":{
        "frozen":orig_dec,"updated":new_dec,
        "frozen_simulated_regret":float(classical.loss(orig_dec["action"],true)),
        "updated_simulated_regret":float(classical.loss(new_dec["action"],true)),
        "physical_action_taken":False},
      "assumptions":{
        "authored_sensor_reliability_not_calibrated":True,
        "sensor_samples_independent_given_world_by_fixture":True,
        "priors_not_measured_in_the_field":True,
        "out_of_support_worlds_not_considered":True},
      "custody":{"human_observations_received":0,
        "real_scene_identified":False,"external_requests":0,
        "T5_calls":0,"actual_actions":0,"automatic_admission":False}
    }
    body["content_sha256"]=digest(body)
    out.mkdir(parents=True)
    for i,row in enumerate(history,1):
        (out/f"belief-{i:02d}.json").write_text(json.dumps(row,indent=2)+"\n")
    (out/"replay.json").write_text(json.dumps(body,indent=2)+"\n")
    return body

def compare_all(question_dir,out):
    out=Path(out)
    need(not out.exists(),"HOLD_BENCHMARK_MUST_NOT_OVERWRITE")
    out.mkdir(parents=True)
    cases=[]
    for world in WORLD_IDS:
        r=single_replay(question_dir,world,out/world)
        cases.append({"world":world,
          "frozen_brier":r["scoring"]["frozen_prior_brier"],
          "updated_brier":r["scoring"]["updated_brier"],
          "frozen_log_loss":r["scoring"]["frozen_prior_log_loss"],
          "updated_log_loss":r["scoring"]["updated_log_loss"],
          "frozen_decision_regret":r["decision"]["frozen_simulated_regret"],
          "updated_decision_regret":r["decision"]["updated_simulated_regret"],
          "synthetic_truth_known_to_evaluator_only":True})
    mean=lambda k:sum(r[k] for r in cases)/len(cases)
    b={"schema":"motif010.four-world-forecast-benchmark.v0",
       "status":"SYNTHETIC_BAYES_PREDICTION_AND_DECISION_REPLAY",
       "four_synthetic_cases":cases,
       "frozen_mean_brier":mean("frozen_brier"),
       "updated_mean_brier":mean("updated_brier"),
       "frozen_mean_log_loss":mean("frozen_log_loss"),
       "updated_mean_log_loss":mean("updated_log_loss"),
       "frozen_mean_decision_regret":mean("frozen_decision_regret"),
       "updated_mean_decision_regret":mean("updated_decision_regret"),
       "fair_classical_Bayes_matches_exactly":True,
       "designed_perfect_agreement_sensor_fixtures":True,
       "results_do_not_prove_generalization":True,
       "reality_was_not_observed":True,
       "real_effects":0}
    b["content_sha256"]=digest(b)
    (out/"benchmark.json").write_text(json.dumps(b,indent=2)+"\n")
    return b

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--question-dir",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    try:
        r=compare_all(a.question_dir,a.out)
        print(json.dumps({"status":r["status"],
          "frozen_Brier":r["frozen_mean_brier"],
          "updated_Brier":r["updated_mean_brier"],
          "frozen_decision_regret":r["frozen_mean_decision_regret"],
          "updated_decision_regret":r["updated_mean_decision_regret"],
          "no_external_actions":r["real_effects"]==0},indent=2))
    except HOLD as e:
        print(json.dumps({"stage":"HOLD","reason":str(e)}))
        raise SystemExit(1)

if __name__=="__main__":main()
