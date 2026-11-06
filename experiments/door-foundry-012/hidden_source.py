"""MOTIF-012 — THE HIDDEN SOURCE.

Infer *hypothetical* hidden common origins among five apparently independent
simulated reports. Joint finite Bayesian model over latent source partitions
and the original four genuine PNG world hypotheses (MOTIF-009), with:
- exact rational posterior over ONE/TWO/FIVE source-group hypotheses;
- explicitly assumed joint cue likelihoods; no duplicate cue multiplication;
- nontrivial independent-but-similar control (avoids forced copy judgment);
- finite cost-sensitive adaptive requests for provenance information;
- matched classical exhaustive optimizer and naive aggregation controls;
- append-only hashes and strict HOLD on any false attestation/authority.

Nothing in this program verifies a real person, photograph, origin, API,
observation, or source identity. All upstream clues/answers are authored fixtures.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from fractions import Fraction
from hashlib import sha256
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path[:0]=[str(HERE.parent/"door-foundry-011"),
              str(HERE.parent/"door-foundry-010"),
              str(HERE.parent/"door-foundry-009")]
import source_graph as prior_graph
import world_model as images
import decision as world_decision

HYPOTHESES=("ONE_ORIGIN","TWO_CLUSTERS","INDEPENDENT_FIVE")
CLUSTER_COUNTS={"ONE_ORIGIN":1,"TWO_CLUSTERS":2,"INDEPENDENT_FIVE":5}
REPORT_IDS=tuple(f"SIMW-{i:02d}" for i in range(1,6))
SOURCE_IDS=tuple(f"DECLARED-{i:02d}" for i in range(1,6))
WORLD_IDS=images.WORLD_IDS
FIELD="wall_extent"
SCOPE="SIMULATED_UNATTESTED_HIDDEN_COMMON_SOURCE"
REPORT_SCHEMA="motif012.synthetic-report.v0"
CUE_SCHEMA="motif012.synthetic-joint-cue.v0"
SENSOR=Fraction(4,5)
H_PRIORS={h:Fraction(1,3) for h in HYPOTHESES}
# Joint cue likelihoods: each bundle is ONE factor; its phrase/timing/token
# components are NOT treated as conditionally independent observations.
CUES={
 "PHRASE_ONLY":("1/4","1/2","3/4"),
 "SHARED_UPSTREAM_TOKEN":("9/10","1/20","1/1000"),
 "INDEPENDENT_CAPTURE_AUDIT":("1/1000","1/100","9/10"),
 "TWO_SEPARATE_UPSTREAM_RECEIPTS":("1/50","9/10","1/50"),
 "NO_CUE":("1","1","1"),
}
# A simulator-defined question-answer channel; the user has not answered any.
QUESTION_MODELS={
 "ASK_ORIGINAL_ARTIFACTS":{
  "prompt":"Can we inspect each original, independently captured artifact or source receipt?",
  "cost":"1/4",
  "responses":{
   "one_receipt":("17/20","1/25","1/50"),
   "two_receipts":("1/25","41/50","3/100"),
   "five_receipts":("1/50","1/25","17/20"),
   "unavailable":("9/100","1/10","1/10")}},
 "ASK_CAPTURE_PATHS":{
  "prompt":"Can we compare the original capture paths and first-hand creation times?",
  "cost":"3/20",
  "responses":{
   "shared":("4/5","11/20","1/10"),
   "separate":("1/20","3/10","3/4"),
   "unclear":("3/20","3/20","3/20")}},
}
# Verified sums for both question channels: all rows must sum to 1.
DECISIONS=("GROUP_ONE","GROUP_TWO","COUNT_FIVE","HOLD_NO_ORIGIN_CLAIM")
# Declared asymmetric consequences discourage both false dismissal of actual
# independence and reckless multiplication of source-derived assertions.
LOSS={
 "GROUP_ONE":("0","3","6"),
 "GROUP_TWO":("3","0","4"),
 "COUNT_FIVE":("8","5","0"),
 "HOLD_NO_ORIGIN_CLAIM":("6/5","6/5","6/5")
}
class HOLD(images.HOLD):pass

def need(ok,why):
    if not ok:raise HOLD(why)
def digest(record):return images.digest(record)
def frac(x):
    try:return images.frac(x)
    except images.HOLD as e:raise HOLD(str(e)) from e
def signed(body):return {**body,"content_sha256":digest(body)}
def check_hash(value,why):
    need(type(value) is dict and type(value.get("content_sha256")) is str,why)
    body=dict(value);claim=body.pop("content_sha256")
    need(digest(body)==claim,why)
    return claim
def probability_prior():
    return dict(H_PRIORS)
def validate_tables():
    need(set(CLUSTER_COUNTS)==set(HYPOTHESES),"HOLD_MISSING_PARTITION")
    for bundle,weights in CUES.items():
        need(len(weights)==3 and all(frac(x)>0 and frac(x)<=1 for x in weights),
             "HOLD_UNSUPPORTED_CUE_MODEL")
    for q,v in QUESTION_MODELS.items():
        need(frac(v["cost"])>0,"HOLD_NO_QUESTION_COST")
        for i,h in enumerate(HYPOTHESES):
            need(sum((frac(row[i]) for row in v["responses"].values()),Fraction(0))==1,
                 "HOLD_QUERY_RESPONSE_LIKELIHOOD_NOT_NORMALIZED")
    for a in DECISIONS:
        need(len(LOSS[a])==3 and all(frac(x)>=0 for x in LOSS[a]),
             "HOLD_UNSUPPORTED_DECISION_LOSS")

def report(n,value="full"):
    need(type(n) is int and 1<=n<=5 and value in ("full","partial"),
         "HOLD_REPORT_INDEX_OR_VALUE")
    core={"schema":REPORT_SCHEMA,"report_id":REPORT_IDS[n-1],
      "claimed_origin_id":SOURCE_IDS[n-1],
      "claims_independent_origin":True,
      "observed_property":FIELD,"synthetic_claim":value,
      "peculiar_phrase_marker":"THE-QUIET-BLUE-LINE",
      "simulated_publication_minute":600+n,
      "upstream_receipt_supplied":False,
      "synthetic_not_real_testimony":True,
      "real_witness_authenticated":False,"real_actions_allowed":False}
    return signed(core)

def cue(kind):
    need(kind in CUES,"HOLD_UNKNOWN_CUE_BUNDLE")
    # One bundled forensic hypothesis: apparent phrasing similarity and
    # time proximity alone cannot certify shared upstream content.
    body={"schema":CUE_SCHEMA,"bundle":kind,
      "reported_phrase_pattern":"THE-QUIET-BLUE-LINE",
      "reported_temporal_cluster":True,
      "source":"SYNTHETIC_UNVERIFIED_JOINT_FORENSIC_FIXTURE",
      "joint_cue_likelihoods":{h:CUES[kind][i] for i,h in enumerate(HYPOTHESES)},
      "phrase_and_timestamp_independently_counted":False,
      "human_identity_confirmed":False,"real_observation":False,
      "external_authentication_performed":False}
    return signed(body)

def verify_fixture(reports,clue):
    validate_tables()
    need(type(reports) is list and len(reports)==5,"HOLD_MISSING_FIVE_REPORTS")
    for i,r in enumerate(reports,1):
        check_hash(r,"HOLD_REPORT_TAMPERED")
        need(set(r)=={
          "schema","report_id","claimed_origin_id",
          "claims_independent_origin","observed_property","synthetic_claim",
          "peculiar_phrase_marker","simulated_publication_minute",
          "upstream_receipt_supplied","synthetic_not_real_testimony",
          "real_witness_authenticated","real_actions_allowed","content_sha256"},
          "HOLD_UNKNOWN_REPORT_FIELD")
        need(r["schema"]==REPORT_SCHEMA and
           r["report_id"]==REPORT_IDS[i-1] and
           r["claimed_origin_id"]==SOURCE_IDS[i-1] and
           r["claims_independent_origin"] is True and
           r["observed_property"]==FIELD and
           r["synthetic_claim"]=="full" and
           r["peculiar_phrase_marker"]=="THE-QUIET-BLUE-LINE" and
           type(r["simulated_publication_minute"]) is int and
           r["simulated_publication_minute"]==600+i and
           r["upstream_receipt_supplied"] is False and
           r["synthetic_not_real_testimony"] is True and
           r["real_witness_authenticated"] is False and
           r["real_actions_allowed"] is False,
           "HOLD_FALSELY_AUTHENTICATED_OR_UNSUPPORTED_REPORT")
    check_hash(clue,"HOLD_CUE_CHANGED")
    kind=clue.get("bundle")
    need(clue.get("schema")==CUE_SCHEMA and kind in CUES and
      clue.get("reported_phrase_pattern")=="THE-QUIET-BLUE-LINE" and
      clue.get("reported_temporal_cluster") is True and
      clue.get("source")=="SYNTHETIC_UNVERIFIED_JOINT_FORENSIC_FIXTURE" and
      clue.get("joint_cue_likelihoods")=={h:CUES[kind][i] for i,h in enumerate(HYPOTHESES)} and
      clue.get("phrase_and_timestamp_independently_counted") is False and
      clue.get("human_identity_confirmed") is False and
      clue.get("real_observation") is False and
      clue.get("external_authentication_performed") is False,
      "HOLD_CUE_CANNOT_GRANT_SOURCE_ATTESTATION")
    return kind

def posterior_origin_and_world(worlds,kind):
    """Five full claims, with 1/2/5 possible common-source roots.

    Exact joint Bayes over H×W. A shared root produces ONE measurement,
    whereas five truly independent measurements are five likelihoods.
    The source's declared independence is explicitly NOT treated as proof.
    """
    need(kind in CUES,"HOLD_INVALID_CUE")
    weights={}
    for h in HYPOTHESES:
        k=CLUSTER_COUNTS[h]
        joint_factor=frac(CUES[kind][HYPOTHESES.index(h)])
        for w in worlds:
            # all five reports are 'full'; model error likelihood for full
            sensor_p=SENSOR if w["wall_extent"]=="full" else 1-SENSOR
            weights[(h,w["id"])]=H_PRIORS[h]*images.PRIORS[w["id"]]*sensor_p**k*joint_factor
    total=sum(weights.values(),Fraction(0))
    need(total>0,"HOLD_NO_BAYESIAN_MODEL_SUPPORT")
    joint={key:weight/total for key,weight in weights.items()}
    origin={h:sum((joint[h,w["id"]] for w in worlds),Fraction(0))
            for h in HYPOTHESES}
    world={w["id"]:sum((joint[h,w["id"]] for h in HYPOTHESES),Fraction(0))
           for w in worlds}
    need(sum(origin.values())==1 and sum(world.values())==1,
         "HOLD_NONNORMALIZED_LATENT_BELIEF")
    return joint,origin,world

def conventional_direct_product(worlds,kind):
    """An independently ordered classical joint-enumeration comparator."""
    states=[]
    for w in worlds:
        for h in reversed(HYPOTHESES):
            sensor=(SENSOR if w["wall_extent"]=="full" else 1-SENSOR)
            states.append((h,w["id"],images.PRIORS[w["id"]]*
                           H_PRIORS[h]*sensor**CLUSTER_COUNTS[h]*
                           frac(CUES[kind][HYPOTHESES.index(h)])))
    den=sum((x[2] for x in states),Fraction(0))
    return {
      h:sum((num for hi,wi,num in states if hi==h),Fraction(0))/den
      for h in HYPOTHESES
    }

def answer_prob(question,response,h):
    need(question in QUESTION_MODELS,"HOLD_UNSUPPORTED_QUESTION")
    models=QUESTION_MODELS[question]
    need(response in models["responses"],"HOLD_UNSUPPORTED_ANSWER")
    return frac(models["responses"][response][HYPOTHESES.index(h)])

def update_origin(weights,q,response):
    raw={h:weights[h]*answer_prob(q,response,h) for h in HYPOTHESES}
    den=sum(raw.values(),Fraction(0))
    need(den>0,"HOLD_ZERO_QUESTION_POSTERIOR")
    return {h:raw[h]/den for h in HYPOTHESES}

def origin_action_loss(action,h):
    need(action in DECISIONS,"HOLD_UNSUPPORTED_ORIGIN_DECISION")
    return frac(LOSS[action][HYPOTHESES.index(h)])

def terminal(belief):
    options=[]
    for idx,action in enumerate(DECISIONS):
        expected=sum((belief[h]*origin_action_loss(action,h)
                      for h in HYPOTHESES),Fraction(0))
        options.append((expected,idx,action))
    score,_,action=min(options)
    return score,{"kind":"DECIDE","action":action,"expected_loss":float(score)}

def active_policy(belief,depth=2,available=None):
    need(depth in (0,1,2),"HOLD_UNBOUNDED_ASK_TREE")
    if available is None:available=tuple(QUESTION_MODELS)
    current,policy=terminal(belief)
    if depth==0 or not available:return current,policy
    for q in available:
        price=frac(QUESTION_MODELS[q]["cost"])
        sum_loss=price
        outcomes={}
        for response in QUESTION_MODELS[q]["responses"]:
            mass=sum((belief[h]*answer_prob(q,response,h)
                      for h in HYPOTHESES),Fraction(0))
            if mass==0:continue
            after=update_origin(belief,q,response)
            child,sub=active_policy(after,depth-1,tuple(z for z in available if z!=q))
            sum_loss+=mass*child
            outcomes[response]={"simulated_probability":float(mass),
                                "policy":sub}
        if sum_loss<current:
            current=sum_loss
            policy={"kind":"ASK","question_id":q,
                "prompt":QUESTION_MODELS[q]["prompt"],
                "expected_total_loss":float(sum_loss),
                "simulated_cost":float(price),
                "branches":outcomes,"sent_to_human":False}
    return current,policy

def independent_enumerator(belief,depth):
    """Exhaustive cost equation with no call to recursive active_policy."""
    base=terminal(belief)[0]
    if depth==0:return base
    best=base
    for q in QUESTION_MODELS:
        first=frac(QUESTION_MODELS[q]["cost"])
        for resp in QUESTION_MODELS[q]["responses"]:
            mass=sum((belief[h]*answer_prob(q,resp,h)
                      for h in HYPOTHESES),Fraction(0))
            if not mass:continue
            child=update_origin(belief,q,resp)
            minimum=terminal(child)[0]
            if depth>1:
                for other in QUESTION_MODELS:
                    if q==other:continue
                    continuation=frac(QUESTION_MODELS[other]["cost"])
                    for r2 in QUESTION_MODELS[other]["responses"]:
                        prob=sum((child[h]*answer_prob(other,r2,h)
                                  for h in HYPOTHESES),Fraction(0))
                        if not prob:continue
                        continuation+=prob*terminal(update_origin(child,other,r2))[0]
                    minimum=min(minimum,continuation)
            first+=mass*minimum
        best=min(best,first)
    return best

def hypothetical_replay(tree,truth):
    need(truth in HYPOTHESES,"HOLD_SIMULATED_ORIGIN_ONLY")
    node=tree
    trace=[]
    while node["kind"]=="ASK":
        q=node["question_id"]
        # This deliberately does NOT pretend a noisy answer is known.
        # Evaluator follows a modal synthetic answer only for explainability;
        # full randomized/noisy outcomes are integrated in expected-loss tree.
        scores={r:answer_prob(q,r,truth) for r in QUESTION_MODELS[q]["responses"]}
        answer=max(scores,key=scores.get)
        trace.append({"question":q,"most_likely_synthetic_response":answer,
                      "human_contacted":False,"response_was_observed":False})
        node=node["branches"][answer]["policy"]
    return {"true_origin_hypothesis_hidden_in_fixture":truth,
            "synthetic_modal_path":trace,"terminal_action":node["action"],
            "not_a_real_observation":True}

def read_origin_pins(original_dir):
    original,worlds=images.verify_original(original_dir)
    # Reuse source-owned MOTIF-011 validation on a known synthetic fixture.
    roots,graph,conflict=prior_graph.verify_graph(
        prior_graph.fixture("LEFT_PARTIAL"))
    need(len(roots)==4 and len(graph)==10 and
         conflict["independent_roots_contradict"] and
         conflict["actual_independence_attested"] is False,
         "HOLD_ORIGINAL_SOURCE_GRAPH_MECHANISM_CHANGED")
    return original,worlds

def scene(fixture_name):
    cases={
      "HIDDEN_SHARED":("SHARED_UPSTREAM_TOKEN","ONE_ORIGIN"),
      "INDEPENDENT_CONVERGENCE":("INDEPENDENT_CAPTURE_AUDIT","INDEPENDENT_FIVE"),
      "TWO_ACTUAL_CLUSTERS":("TWO_SEPARATE_UPSTREAM_RECEIPTS","TWO_CLUSTERS"),
      "SIMILAR_WORDING_ONLY":("PHRASE_ONLY",None),
      "NO_ORIGIN_EVIDENCE":("NO_CUE",None),
    }
    need(fixture_name in cases,"HOLD_UNSUPPORTED_SYNTHETIC_CASE")
    return cases[fixture_name]

def run_case(question_dir,name,out):
    out=Path(out)
    need(not out.exists(),"HOLD_REFUSE_OVERWRITING_EVIDENCE")
    original,worlds=read_origin_pins(question_dir)
    cue_name,hidden_truth=scene(name)
    reports=[report(i) for i in range(1,6)]
    clue=cue(cue_name)
    need(verify_fixture(reports,clue)==cue_name,"HOLD_CUE_SOURCE_WRONG")
    joint,belief,world_posterior=posterior_origin_and_world(worlds,cue_name)
    reference=conventional_direct_product(worlds,cue_name)
    need(belief==reference,"HOLD_LATENT_POSTERIOR_DIFFERS_FROM_CLASSICAL_CONTROL")
    values=[active_policy(belief,depth) for depth in (0,1,2)]
    checks=[independent_enumerator(belief,depth) for depth in (0,1,2)]
    need(all(a[0]==b for a,b in zip(values,checks)),
         "HOLD_ACTIVE_QUESTION_LOSS_DISAGREES_WITH_CLASSICAL_ENUMERATOR")
    full_prob=sum((world_posterior[w["id"]] for w in worlds
                   if w["wall_extent"]=="full"),Fraction(0))
    always_five=Fraction(4,5)**5*Fraction(4,5)
    naive_posterior_full=always_five/(always_five+
         (Fraction(1,5)**5)*Fraction(1,5))
    # Independently equivalent conventional naive posterior is above;
    # no physical world truth known to this inference engine.
    no_question=values[0][1]
    follow=values[2][1]
    records=[]
    parent=original["content_sha256"]
    for i,r in enumerate(reports):
        entry={"schema":"motif012.unattested-claim-ledger.v0",
          "sequence":i+1,"report":r,"previous_sha256":parent,
          "report_sha256":r["content_sha256"],
          "source_independence_remains_unverified":True,
          "physical_observation_count":0}
        entry=signed(entry)
        records.append(entry)
        parent=entry["content_sha256"]
    belief_labels={h:str(belief[h]) for h in HYPOTHESES}
    body={
      "schema":"motif012.hidden-source-inference.v0",
      "status":"HOLD_HIDDEN_SOURCE_HYPOTHESES_UNATTESTED",
      "fixture":name,
      "original_009_question_sha256":original["content_sha256"],
      "original_four_visual_world_sha256":{
         w["id"]:w["start_png_sha256"] for w in worlds},
      "original_011_source_dependency_mechanism_replayed":True,
      "new_simulated_reports":reports,
      "report_claims_consistent_but_origins_undemonstrated":True,
      "joint_cue_evidence":clue,
      "prior_origin_hypotheses":{h:str(H_PRIORS[h]) for h in HYPOTHESES},
      "source_origin_posterior":belief_labels,
      "world_posterior":{w["id"]:str(world_posterior[w["id"]]) for w in worlds},
      "posterior_wall_full":str(full_prob),
      "naive_five_independent_report_posterior_wall_full":str(naive_posterior_full),
      "closed_hypotheses":{h:CLUSTER_COUNTS[h] for h in HYPOTHESES},
      "no_decision_without_asking":no_question,
      "question_policy_no_ask_loss":float(values[0][0]),
      "question_policy_up_to_one_loss":float(values[1][0]),
      "question_policy_up_to_two_loss":float(values[2][0]),
      "question_policy_up_to_two":follow,
      "information_value_of_questioning":float(values[0][0]-values[2][0]),
      "independently_enumerated_classical_control_equal":True,
      "synthetic_truth_for_evaluator_only":hidden_truth,
      "synthetic_modal_oracle_path":
        hypothetical_replay(follow,hidden_truth) if hidden_truth else None,
      "evidence_ledger":records,"last_receipt_sha256":parent,
      "assumptions":{
        "same_wording_and_close_times_are_not_proof_of_copying":True,
        "joint_cue_likelihoods_are_authored_not_calibrated":True,
        "clue_features_not_multiplied_as_independent":True,
        "latent_partition_options_restricted_to_one_two_five":True,
        "two_cluster_partition_fixed_for_test":True,
        "report_likelihood_conditional_on_true_world_and_partition":True,
        "noisy_answer_channels_are_synthetic":True,
        "hidden_root_source_not_attested":True,
        "all_origin_posterior_values_conditional_on_closed_model":True
      },
      "authority":{
        "actual_people_identified":0,"real_reporters_contacted":0,
        "actual_question_sent":False,"external_source_verified":False,
        "original_witness_identity_authenticated":False,
        "real_world_images_observed":0,"external_api_calls":0,
        "T5_calls":0,"actions_executed":0,"auto_admitted":False
      }
    }
    body=signed(body)
    out.mkdir(parents=True)
    for r in records:
        (out/f"report-{r['sequence']:02d}.json").write_text(json.dumps(r,indent=2)+"\n")
    (out/"inference.json").write_text(json.dumps(body,indent=2)+"\n")
    (out/"proposed-question.md").write_text(
       "# MOTIF-012 — possible hidden common sources\n\n"+
       "Five apparently independent synthetic reports agree. Their phrasing "+
       "and timing do **not** establish independent origin or copying.\n\n"+
       "All three latent explanations remain possible:\n\n"+
       "\n".join(f"- {h}: posterior **{float(belief[h]):.3f}** (model-dependent)"
           for h in HYPOTHESES)+
       "\n\nBest first proposed question (NOT SENT):\n\n"+
       ("> "+QUESTION_MODELS[follow["question_id"]]["prompt"] if follow["kind"]=="ASK"
        else "**No question is worth its synthetic cost.**")+
       "\n\nEvidence, sensor accuracies, hidden truth labels and question outcomes "+
       "are simulated. This is not a real witness investigation.\n")
    return body

def benchmark(question_dir,out):
    out=Path(out)
    need(not out.exists(),"HOLD_BENCHMARK_EXISTS")
    out.mkdir(parents=True)
    names=("HIDDEN_SHARED","INDEPENDENT_CONVERGENCE",
           "TWO_ACTUAL_CLUSTERS","SIMILAR_WORDING_ONLY","NO_ORIGIN_EVIDENCE")
    cases=[]
    for name in names:
        r=run_case(question_dir,name,out/name)
        truth=r["synthetic_truth_for_evaluator_only"]
        belief={h:frac(v) for h,v in r["source_origin_posterior"].items()}
        cases.append({
          "fixture":name,
          "truth_known_only_to_synthetic_evaluator":truth,
          "posterior_support_for_fixture_origin":float(belief[truth]) if truth else None,
          "origin_selected_without_proof":False,
          "best_immediate_decision":r["no_decision_without_asking"]["action"],
          "first_question_unsent":r["question_policy_up_to_two"].get("question_id"),
          "expected_loss_no_question":r["question_policy_no_ask_loss"],
          "expected_loss_two_questions":r["question_policy_up_to_two_loss"],
          "possible_worlds_unobserved":True
        })
    body={"schema":"motif012.hidden-source-benchmark.v0",
          "status":"HOLD_SYNTHETIC_LATENT_SOURCE_REASONING_ONLY",
          "cases":cases,
          "independent_and_hidden_shared_controls_both_present":True,
          "matched_classical_latent_model_and_question_tree_equal":True,
          "same_wording_not_automatically_classified_as_copying":True,
          "real_source_independence_proven":False,"actual_world_observed":False,
          "total_human_contacts":0,"total_real_actions":0}
    body=signed(body)
    (out/"benchmark.json").write_text(json.dumps(body,indent=2)+"\n")
    return body

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--question-dir",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    try:
        b=benchmark(a.question_dir,a.out)
        print(json.dumps({"status":b["status"],
          "fixtures":len(b["cases"]),
          "independent_control":next(x for x in b["cases"]
                                    if x["fixture"]=="INDEPENDENT_CONVERGENCE"),
          "hidden_copy":next(x for x in b["cases"]
                             if x["fixture"]=="HIDDEN_SHARED"),
          "no_people_contacted":True},indent=2))
    except (HOLD,images.HOLD,ValueError) as exc:
        print(json.dumps({"stage":"HOLD","reason":str(exc)}))
        raise SystemExit(1)

if __name__=="__main__":
    main()
