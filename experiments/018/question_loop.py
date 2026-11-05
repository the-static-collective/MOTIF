#!/usr/bin/env python3
"""MOTIF-018 — a bounded, evidence-scored question-making loop.

Baffling question: Which additional measurement is worth *asking for* when
gauges can go missing precisely when the river changes?

The agent revises a declarative question-selection *cartridge* on older
observations only, freezes it, and attempts one unseen physical-sensor test.
It never writes code, dispatches an alarm, claims safety authority, or trains
on its sealed holdout. Stdlib Python, fixed public USGS sources.
"""
from __future__ import annotations
import argparse
from datetime import datetime,timezone,timedelta
from hashlib import sha256
import json
import math
from pathlib import Path
from statistics import mean
import sys
from urllib.parse import urlencode

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"016"))
import watershed as water

SCHEMA="motif.self-question-loop/v1"
PLAN_SCHEMA="motif.self-question-plan/v1"
RUN_SCHEMA="motif.self-question-outcome/v1"
QUESTIONS=("use_last_mankato","use_local_trend","ask_blue","ask_sueur",
           "ask_both","conditional_blue","conditional_both")
FIXED_SITES=dict(water.SITES)
# All dates fixed in source before any of the sealed test source is retrieved.
WINDOWS={
 "training":("2023-05-04","2023-05-13"),
 "development":("2024-06-01","2024-06-10"),
 "new_event":("2025-09-12","2025-09-22")
}
FEATURES={
 "use_local_trend":("local_delta",),
 "ask_blue":("local_delta","blue_delta"),
 "ask_sueur":("local_delta","sueur_delta"),
 "ask_both":("local_delta","blue_delta","sueur_delta"),
 "conditional_blue":("local_delta","blue_delta"),
 "conditional_both":("local_delta","blue_delta","sueur_delta")
}
COST_UNIT_FRACTION=0.03
CONDITIONAL_DELTA_FRACTION=0.035
HOURS_BEFORE_TARGET=7
DELTA_WINDOW=6
MIN_CASES=72
MAX_FEATURES=1800
MAX_ITERATIONS=5
PLAN_REVISIONS=(
 ("QUESTION-0","Is more information always better?",0.0,0.0,0.0,False),
 ("QUESTION-1","Is another measurement worth the observation credit?",1.0,0.0,0.0,False),
 ("QUESTION-2","What if the sensor is missing when we ask?",1.0,2.0,0.0,False),
 ("QUESTION-3","Does the answer survive time-regime drift within development?",1.0,2.0,0.30,False),
 ("QUESTION-4","Should we only ask when local conditions make the question relevant?",1.0,2.0,0.30,True),
)

def require(ok,why):
 if not ok:raise water.HOLD(why)

def digest(x):
 return sha256(json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=True).encode()).hexdigest()

def collect(name):
 require(name in WINDOWS,"UNLISTED_SOURCE_WINDOW")
 begin,end=WINDOWS[name]
 data={}
 for key,site in FIXED_SITES.items():
  query=urlencode({"monitoring_location_id":site,"parameter_code":"00060",
                   "datetime":begin+"/"+end,"limit":str(MAX_FEATURES),"f":"json"})
  data[key]=water.request_json(water.USGS+"?"+query)
 return data

def rows(raw,name):
 require(name in WINDOWS and type(raw) is dict and set(raw)==set(FIXED_SITES),
         "INVALID_SOURCE_ENVELOPE")
 d={key:water.gauges(raw[key],key) for key in FIXED_SITES}
 lo=datetime.fromisoformat(WINDOWS[name][0]).replace(tzinfo=timezone.utc)
 hi=(datetime.fromisoformat(WINDOWS[name][1]).replace(tzinfo=timezone.utc)
       +timedelta(days=1))
 result=[]
 # Only downstream supplies target labels. Upstream missingness NEVER removes a
 # downstream case from the denominator.
 for hour in sorted(d["mankato"]):
  origin=hour-timedelta(hours=HOURS_BEFORE_TARGET)
  past=origin-timedelta(hours=DELTA_WINDOW)
  if not (lo<=hour<hi and origin in d["mankato"] and
          past in d["mankato"]):continue
  row={
   "target_utc":hour.isoformat().replace("+00:00","Z"),
   "known":d["mankato"][origin],"y":d["mankato"][hour],
   "local_delta":d["mankato"][origin]-d["mankato"][past],
   "blue_delta":None,"sueur_delta":None,
  }
  for key in ("blue","sueur"):
   if origin in d[key] and past in d[key]:
    row[key+"_delta"]=d[key][origin]-d[key][past]
  result.append(row)
 require(MIN_CASES<=len(result)<=600,"MISSING_DOWNSTREAM_HISTORY")
 return result,{"all_downstream_targets":len(result),
   "upstream_feature_available":{
     key:sum(row[key+"_delta"] is not None for row in result)
     for key in ("blue","sueur")
   },
   "paired_both_available":sum(row["blue_delta"] is not None and
                               row["sueur_delta"] is not None for row in result),
   "start":result[0]["target_utc"],"end":result[-1]["target_utc"]}

def applicable(row,question):
 if question in ("use_last_mankato","use_local_trend"):return True
 if question.startswith("conditional_"):
  if abs(row["local_delta"])/max(abs(row["known"]),1)<CONDITIONAL_DELTA_FRACTION:
   return False
 return True

def inputs_available(row,question):
 return all(row.get(f) is not None for f in FEATURES.get(question,()))

def question_count(question):
 if question.endswith("_both"):return 2
 if "blue" in question or "sueur" in question:return 1
 return 0

def fit_bank(training):
 models={"use_last_mankato":None}
 available=[]
 for question in QUESTIONS[1:]:
  fitted=[r for r in training if inputs_available(r,question)]
  if len(fitted)>=40:
   models[question]=water.fit_ridge(fitted,FEATURES[question])
   available.append(question)
 return models

def predict_row(row,name,bank):
 requested=question_count(name) if applicable(row,name) else 0
 missing=requested and not inputs_available(row,name)
 use=name if not missing and requested or (requested==0 and applicable(row,name)) else "use_last_mankato"
 if name.startswith("conditional_") and not applicable(row,name):
  use="use_last_mankato"
 model=bank.get(use)
 return water.predict(row,model),requested,bool(missing)

def metrics(data,name,bank,cost_unit,weights):
 err,questions,unanswered=0.0,0,0
 halves=[[],[]]
 for idx,row in enumerate(data):
  yhat,asked,missing=predict_row(row,name,bank)
  err+=abs(row["y"]-yhat)
  questions+=asked
  unanswered+=int(missing)
  halves[0 if idx<len(data)//2 else 1].append(abs(row["y"]-yhat))
 n=len(data)
 error=err/n
 extra=(weights[0]*cost_unit*questions/n+
        weights[1]*cost_unit*unanswered/n)
 drift=abs(mean(halves[0])-mean(halves[1]))
 objective=error+extra+weights[2]*drift
 return {
  "observed_mae_cfs":round(error,4),
  "question_credits_per_hour":round(questions/n,4),
  "asked_and_missing_fraction":round(unanswered/n,4),
  "first_half_mae_cfs":round(mean(halves[0]),4),
  "second_half_mae_cfs":round(mean(halves[1]),4),
  "instability_cfs":round(drift,4),
  "declared_development_objective_cfs_equivalent":round(objective,4),
  "full_downstream_case_count":n,
  "total_questions":questions,"unanswered_questions":unanswered
 }

def evolve(training,development):
 bank=fit_bank(training)
 require("use_local_trend" in bank,"NO_LOCAL_TREND_TRAINING")
 train_persistence=mean(abs(r["y"]-r["known"]) for r in training)
 cost_unit=train_persistence*COST_UNIT_FRACTION
 require(cost_unit>0,"ZERO_TRAINING_BASELINE_CANNOT_PRICE_QUESTIONS")
 history=[]
 selected=None
 for idx,(code,why,price,unanswered,drift,allow_conditional) in enumerate(PLAN_REVISIONS):
  weights=(price,unanswered,drift)
  names=[n for n in QUESTIONS if n in bank and
         (allow_conditional or not n.startswith("conditional_"))]
  scores={n:metrics(development,n,bank,cost_unit,weights) for n in names}
  choice=min(names,key=lambda n:(
    scores[n]["declared_development_objective_cfs_equivalent"],
    question_count(n),
    QUESTIONS.index(n)))
  # A full trace of the changed decision instrument: every revision's
  # explicitly altered objective, the winner, measured failure and next probe.
  controls=scores["use_last_mankato"]
  rationale=("New policy gains against same-objective persistence on development"
    if scores[choice]["declared_development_objective_cfs_equivalent"]<
       controls["declared_development_objective_cfs_equivalent"] else
    "No question justified relative to same-objective persistence")
  history.append({
   "step":idx,"version":code,"question_that_caused_revision":why,
   "bounded_rule_change":{
    "observation_credit_weight":price,"unanswered_query_weight":unanswered,
    "temporal_instability_weight":drift,"conditional_questioning":allow_conditional
   },
   "available_candidates":names,
   "candidate_development_scores":scores,
   "new_selected_question":choice,
   "rationale":rationale,
   "previous_selection":selected,
   "changed_selection":selected is not None and choice!=selected,
   "test_outcomes_seen":0,"source_code_changed":False,
   "next_testable_question":(
     "Do the selected extra sensor requests reduce later real downstream error after costs and absent sensor hours count?"
   )
  })
  selected=choice
 require(len(history)==MAX_ITERATIONS and selected in bank,"LOOP_FAILED_TO_FREEZE")
 return {
  "history":history,
  "selected":selected,
  "bank":bank,
  "cost_unit":cost_unit,
  "train_persistence_mae_cfs":train_persistence
 }

def freeze(train_raw,dev_raw):
 train,train_coverage=rows(train_raw,"training")
 dev,dev_coverage=rows(dev_raw,"development")
 result=evolve(train,dev)
 card={
  "schema":PLAN_SCHEMA,
  "protocol":SCHEMA,
  "windows":WINDOWS,
  "train_count":len(train),"development_count":len(dev),
  "source_sha256":{"training":digest(train_raw),"development":digest(dev_raw)},
  "training_coverage":train_coverage,"development_coverage":dev_coverage,
  "trained_model_names":sorted(result["bank"]),
  "training_only_question_cost_unit_cfs_equivalent":round(result["cost_unit"],6),
  "training_persistence_mae_cfs":round(result["train_persistence_mae_cfs"],6),
  "frozen_final_question_policy":result["selected"],
  "models":result["bank"],
  "loop":result["history"],
  "final_research_question":"Do extra measurement questions really help in a NEW year when missingness, credits, and regime instability count?",
  "method":"BOUNDED_DECLARATIVE_META_POLICY_REVISION_NOT_CODE_GENERATION",
  "note":"Costs are arbitrary, transparent cfs-equivalent research prices. Not real money, environmental risk or flood severity.",
  "automatic_promotion":False,"authority":False,
  "source_data_queried_in_loop":["training","development"],
  "heldout_data_seen_before_freeze":False
 }
 return dict(card, plan_sha256=digest(card))

def verify_plan(card):
 require(type(card) is dict and card.get("schema")==PLAN_SCHEMA,"NOT_A_FROZEN_PLAN")
 provided=card.get("plan_sha256")
 require(type(provided) is str and provided==digest({
   k:v for k,v in card.items() if k!="plan_sha256"}),"FROZEN_PLAN_SHA_MISMATCH")
 require(card.get("windows")=={k:list(v) for k,v in WINDOWS.items()} or
         card.get("windows")==WINDOWS,"WINDOW_CHANGED")
 require(card.get("source_data_queried_in_loop")==["training","development"] and
         card.get("heldout_data_seen_before_freeze") is False and
         card.get("automatic_promotion") is False and
         card.get("authority") is False,"UNAUTHORISED_PROVENANCE")
 require(card.get("frozen_final_question_policy") in QUESTIONS and
         isinstance(card.get("loop"),list) and len(card["loop"])==MAX_ITERATIONS and
         [s.get("version") for s in card["loop"]]==[r[0] for r in PLAN_REVISIONS],
         "INVALID_REVISION_HISTORY")
 for step,proposal in zip(card["loop"],PLAN_REVISIONS):
  _,question,c,m,s,conditional=proposal
  require(step.get("question_that_caused_revision")==question and
          step.get("bounded_rule_change")=={
           "observation_credit_weight":c,"unanswered_query_weight":m,
           "temporal_instability_weight":s,"conditional_questioning":conditional
          } and step.get("source_code_changed") is False and
          step.get("test_outcomes_seen")==0,
          "REVISED_HISTORY_AFTER_FREEZE")
 require(card["frozen_final_question_policy"]==
         card["loop"][-1]["new_selected_question"],"SELECTED_POLICY_NOT_FROZEN")
 require(card.get("trained_model_names")==sorted(card.get("models",{})),
         "TRAINED_BANK_CHANGED")
 require(all(q in QUESTIONS for q in card["trained_model_names"]),"UNKNOWN_QUESTION")
 require(set(card["models"])==set(card["trained_model_names"]) and
         card["models"]["use_last_mankato"] is None,"UNEXPECTED_BASELINE_MODEL")
 for question,model in card["models"].items():
  if question=="use_last_mankato":continue
  require(type(model) is dict and set(model)=={"names","mean","scale","weights"} and
          model["names"]==list(FEATURES[question]),"BAD_QUESTION_MODEL")
  n=len(model["names"])
  require(type(model["mean"]) is list and type(model["scale"]) is list and
          type(model["weights"]) is list and
          len(model["mean"])==n and len(model["scale"])==n and
          len(model["weights"])==n+1 and
          all(type(x) in (float,int) and math.isfinite(x)
              for name in ("mean","scale","weights") for x in model[name]) and
          all(x>0 for x in model["scale"]),"UNSAFE_QUESTION_COEFFICIENTS")

def challenge(frozen,test_raw):
 verify_plan(frozen)
 test,coverage=rows(test_raw,"new_event")
 plan=frozen["loop"][-1]
 cfg=plan["bounded_rule_change"]
 w=(cfg["observation_credit_weight"],cfg["unanswered_query_weight"],
    cfg["temporal_instability_weight"])
 bank=frozen["models"]
 cost=frozen["training_only_question_cost_unit_cfs_equivalent"]
 outcomes={}
 for question in QUESTIONS:
  if question in bank:
   outcomes[question]=metrics(test,question,bank,cost,w)
 selected=frozen["frozen_final_question_policy"]
 base=outcomes["use_last_mankato"]
 selected_score=outcomes[selected]
 baseline_error=base["observed_mae_cfs"]
 chosen_error=selected_score["observed_mae_cfs"]
 delta=round(baseline_error-chosen_error,4)
 utility_delta=round(base["declared_development_objective_cfs_equivalent"]-
                    selected_score["declared_development_objective_cfs_equivalent"],4)
 if utility_delta<=0 or delta<=0:
  verdict="HOLD_NO_HELDOUT_QUESTION_VALUE"
 elif selected_score["unanswered_questions"]>selected_score["total_questions"]*.25:
  verdict="HOLD_TOO_MANY_MISSING_SENSOR_ANSWERS"
 else:
  verdict="HELD_CANDIDATE_NEEDS_MORE_EVENTS"
 # Ask something *falsifiable* in response to the observed failure.
 next_question=(
  "Which unavailable sensor hours bias the value estimate, and could a one-sensor baseline retain more cases?"
  if selected_score["unanswered_questions"]>0 else
  "Can this question policy beat persistence again in a different, independently selected year?"
 )
 return {
  "schema":RUN_SCHEMA,
  "status":"RETROSPECTIVE_REAL_SENSOR_QUESTION_TEST_NOT_ACTUAL_ISSUED_FORECAST",
  "frozen_plan_sha256":frozen["plan_sha256"],
  "heldout_source_json_sha256":digest(test_raw),
  "heldout_window":WINDOWS["new_event"],
  "heldout_outcomes":outcomes,
  "selected_policy":selected,"heldout_baseline_mae_cfs":baseline_error,
  "heldout_selected_mae_cfs":chosen_error,
  "heldout_mae_reduction_cfs":delta,
  "heldout_utility_improvement_cfs_equivalent":utility_delta,
  "denominator":coverage,
  "source_type":"USGS_REPORTED_HISTORICAL_DISCHARGE_ESTIMATES",
  "run_disposition":verdict,
  "next_best_question":next_question,
  "metric_diagnostic":{
   "source_missingness_can_select_population":True,
   "cost_weights_are_assumed_not_empirically_valued":True,
   "the_diagnostic_may_need_revision":True,
   "counterhypothesis":"A policy that looks valuable during development can lose when river conditions, reporting latency or sensor availability change.",
   "needed_next_test":"Lock this question policy and test a different future period, including original observation reporting times."
  },
  "causal_inference":False,"actual_issue_time_availability_verified":False,
  "data_were_revealed_to_reviser_before_freeze":False,
  "new_executable_capability_autogenerated":False,
  "model_retrained_on_holdout":False,"automatic_promotion":False,
  "real_world_action":False,"authority":False
 }

def write(path,data):
 path.write_text(json.dumps(data,sort_keys=True,indent=2,ensure_ascii=True)+"\n")

def main():
 cli=argparse.ArgumentParser()
 cli.add_argument("stage",choices=("develop","challenge"))
 cli.add_argument("--out-dir",type=Path,default=Path("question-018-evidence"))
 cli.add_argument("--offline",action="store_true")
 args=cli.parse_args()
 folder=args.out_dir
 try:
  if args.stage=="develop":
   require(not (folder/"frozen.json").exists(),"NO_OVERWRITE_SEAL")
   if not args.offline:folder.mkdir(parents=True,exist_ok=True)
   train=json.loads((folder/"training-raw.json").read_text()) if args.offline else collect("training")
   dev=json.loads((folder/"development-raw.json").read_text()) if args.offline else collect("development")
   card=freeze(train,dev)
   if not args.offline:
    write(folder/"training-raw.json",train)
    write(folder/"development-raw.json",dev)
   write(folder/"frozen.json",card)
   print(json.dumps({
    "phase":"LOOP_REVISED_AND_FROZEN_WITHOUT_NEW_EVENT",
    "plan_sha256":card["plan_sha256"],
    "selected":card["frozen_final_question_policy"],
    "iteration_summaries":[{
      "version":h["version"],"reason":h["question_that_caused_revision"],
      "selected":h["new_selected_question"],
      "changed":h["changed_selection"],
      "relative_to_baseline":h["rationale"]
     }for h in card["loop"]]
   },indent=2))
  else:
   plan=json.loads((folder/"frozen.json").read_text())
   verify_plan(plan)
   require(not (folder/"test.json").exists(),"NO_OVERWRITE_HELDOUT")
   observed=json.loads((folder/"new-event-raw.json").read_text()) if args.offline else collect("new_event")
   scored=challenge(plan,observed)
   if not args.offline:
    write(folder/"new-event-raw.json",observed)
   write(folder/"test.json",scored)
   print(json.dumps(scored,indent=2,sort_keys=True))
  return 0
 except (OSError,ValueError,TypeError,KeyError,ZeroDivisionError) as error:
  print("HOLD: "+str(error)[:190],file=sys.stderr)
  return 2

if __name__=="__main__":
 raise SystemExit(main())
