"""ODYSSEY-240: 219+ serial causal actions, 96 owner-checked decisions.

A public, deterministic research simulator of a long interconnected task.
No external actions or real persons. Twelve independently changing hidden
rules; one serial task frontier; independent test receipts; repairs and
audits are actual required transitions, not decorations. Deliberate wrong
hypotheses never count as verified truth or positive reward by themselves.

All internal policy evidence is from prior source reports only. The hidden
owner rule is accessed ONLY by the independent synthetic gate and grader.
"""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
from math import isfinite
import copy,json,random

from error_dividend import Owner,HELDOUT,DEV,INPUTS,initial_posterior,outputs,predict,accuracy,QUERY_COST
from hypermap import ReasonHypermap,grade,canonical,decision_gain

SCHEMA="motif.odyssey-240/v0"
SECTORS=12
GATES_PER_SECTOR=8
REQUIRED_GATES=SECTORS*GATES_PER_SECTOR
MINIMUM_ACTIONS=REQUIRED_GATES*2+SECTORS*2+3 # 219
ACTION_LIMIT=350
COST_LIMIT=400.
COMMIT_COST=1.
SURVEY_COST=.25
PROBE_COST=2.
WRONG_PENALTY=4.
REPAIR_COST=2.
AUDIT_COST=1.5
RELAY_COST=2.
POLICIES=("static","classical_bayes","hypermap_voi","contrarian")
REAL_MODEL_POLICIES=("llm_flat","llm_memory","llm_verification")
SCENARIO_SEEDS=HELDOUT[:64]
DEV_SEEDS=DEV[:8]

def digest(obj):
    return sha256(canonical(obj).encode()).hexdigest()

def independent_owner_seed(seed,sector):
    if seed not in DEV_SEEDS+SCENARIO_SEEDS:raise ValueError("SEED_NOT_REGISTERED")
    group=DEV if seed in DEV_SEEDS else HELDOUT
    i=group.index(seed)
    return group[(i*37+sector*11)%len(group)]

def problem_order(seed,sector):
    r=random.Random(int(digest({"world":seed,"sector":sector,"domain":"permutation"})[:12],16))
    points=list(INPUTS)
    r.shuffle(points)
    return tuple(points)

class BudgetError(RuntimeError):pass
class GateError(RuntimeError):pass

class LongChain:
    def __init__(self,seed,policy="classical_bayes",action_limit=ACTION_LIMIT,cost_limit=COST_LIMIT,decision_adapter=None):
        if seed not in DEV_SEEDS+SCENARIO_SEEDS:raise ValueError("SEED_NOT_REGISTERED")
        if policy not in POLICIES+REAL_MODEL_POLICIES:raise ValueError("UNKNOWN_POLICY")
        if (policy in REAL_MODEL_POLICIES)!=(decision_adapter is not None):
            raise ValueError("REAL_MODEL_ADAPTER_REQUIRED_OR_UNEXPECTED")
        if not isinstance(action_limit,int) or action_limit<1 or action_limit>2000:
            raise ValueError("BAD_ACTION_LIMIT")
        if not isfinite(cost_limit) or cost_limit<=0 or cost_limit>5000:
            raise ValueError("BAD_COST_LIMIT")
        self.seed=seed;self.policy=policy
        self.decision_adapter=decision_adapter
        self.last_model_proposal=None
        self.real_model_calls=0
        self.real_model_prompt_tokens=0
        self.real_model_inference_seconds=0.0
        self.action_limit=action_limit;self.cost_limit=cost_limit
        self.owner=[];self.maps=[];self.order=[]
        for sector in range(SECTORS):
            o=Owner(independent_owner_seed(seed,sector),"truthful")
            self.owner.append(o)
            self.maps.append(ReasonHypermap(o))
            self.order.append(problem_order(seed,sector))
        self.phase=0;self.gate=0;self.surveyed=False
        self.repair_needed=False;self.expected_retry=None
        self.completed=set();self.audits=set();self.relays=set()
        self.events=[];self.cost=0.;self.status="RUNNING"
        self.previous_hash="0"*64
        self.metrics={"wrong_commits":0,"correct_commits":0,"repair_actions":0,
          "optional_probes":0,"calibration_reuses":0,"learned_counterexamples":0,
          "unrealized_counterexamples":0,"false_reports_promoted":0,
          "root_echoes_ignored":0,"rumor_was_used_as_evidence":0,
          "source_verified":0,"actual_regressions":0,
          "surveys":0,"half_audits":0,"terminal_audits":0,"relays":0}
        self.information_gains=[]
        self.per_sector_receipts=[set([o.initial["root"]]) for o in self.owner]
        self.initial_rules_in_trace=False
        self.completed_stage_hashes=[]
        self.rumor_roots_seen=set()
    def _step(self,kind,sector=None,gate=None,metadata=None,cost=0):
        if self.status!="RUNNING":raise GateError("TERMINAL_STATE")
        if len(self.events)>=self.action_limit:raise BudgetError("ACTION_BUDGET_EXCEEDED")
        if self.cost+cost>self.cost_limit+1e-9:raise BudgetError("COST_BUDGET_EXCEEDED")
        if cost<0:raise ValueError("NEGATIVE_COST")
        self.cost+=cost
        rec={"action":len(self.events)+1,"kind":kind,
             "sector":sector if sector is not None else self.phase,
             "gate":gate if gate is not None else self.gate,
             "cost":round(cost,4),"cumulative_cost":round(self.cost,4),
             "prior_hash":self.previous_hash,
             "meta":copy.deepcopy(metadata or {}),
             "authority":"PUBLIC_SYNTHETIC_OWNER_ONLY","external_actions":False}
        rec["hash"]=digest(rec)
        self.previous_hash=rec["hash"]
        self.events.append(rec)
        return rec
    def _position(self,sector,gate):
        if self.status!="RUNNING":raise GateError("TERMINAL_STATE")
        if sector!=self.phase or gate!=self.gate:raise GateError("OUT_OF_ORDER_DEPENDENCY")
        if self.repair_needed:raise GateError("REPAIR_REQUIRED")
        if self.gate>=GATES_PER_SECTOR:raise GateError("AUDIT_REQUIRED")
    def _survey(self,sector,gate):
        self._position(sector,gate)
        if self.surveyed:raise GateError("ALREADY_SURVEYED")
        if gate==0 and sector>0 and (sector-1,"terminal") not in self.audits:
            raise GateError("PREVIOUS_TERMINAL_AUDIT_REQUIRED")
        if sector>0 and sector%4==0 and (sector-1) not in self.relays:
            raise GateError("BRIDGE_RELAY_REQUIRED")
        if gate==4 and (sector,"half") not in self.audits:
            raise GateError("HALFWAY_AUDIT_REQUIRED")
        x=self.order[sector][gate]
        # An adversarial echo can look like a corroborating report. Its source
        # root is identical within this sector, and is never owner testimony.
        rumor_origin=f"unverified-rumor-{self.seed}-{sector}"
        if rumor_origin in self.rumor_roots_seen:
            self.metrics["root_echoes_ignored"]+=1
        else:self.rumor_roots_seen.add(rumor_origin)
        hint=(x[0]^x[1]^(sector%2))
        self.surveyed=True;self.metrics["surveys"]+=1
        self._step("survey",sector,gate,{"x":list(x),
            "hint":hint,"hint_status":"UNVERIFIED_ECHO_IGNORE",
            "hint_root":rumor_origin,"prior_gate_completed":(gate==0 or
                (sector,gate-1) in self.completed)},SURVEY_COST)
    def _prediction(self,sector,x):
        if x==self.owner[sector].start_x:
            return int(self.owner[sector].initial["value"]),1.
        m=self.maps[sector]
        if self.policy in REAL_MODEL_POLICIES:
            packet=self._model_packet(sector,x)
            answer=self.decision_adapter(packet)
            if not isinstance(answer,dict) or answer.get("prediction") not in (0,1):
                raise ValueError("INVALID_REAL_MODEL_RESULT")
            p_one=answer.get("p_one")
            if not isinstance(p_one,(int,float)) or not isfinite(p_one) or not 0<=p_one<=1:
                raise ValueError("INVALID_REAL_MODEL_PROBABILITY")
            if not isinstance(answer.get("token_count"),int) or answer["token_count"]<1:
                raise ValueError("REAL_MODEL_MISSING_TOKEN_COUNT")
            if not isinstance(answer.get("inference_seconds"),(int,float)) or answer["inference_seconds"]<0:
                raise ValueError("REAL_MODEL_MISSING_INFERENCE_TIME")
            self.real_model_calls+=1
            self.real_model_prompt_tokens+=answer["token_count"]
            self.real_model_inference_seconds+=answer["inference_seconds"]
            self.last_model_proposal={
                "model":str(answer.get("model","UNKNOWN_REAL_MODEL")),
                "revision":str(answer.get("revision","UNKNOWN_REVISION")),
                "prompt_sha256":str(answer.get("prompt_sha256","")),
                "source_roots_used":packet["source_roots"],
                "observations_used":len(packet["observations"]),
                "token_count":answer["token_count"],
                "p_zero":round(1-p_one,6),"p_one":round(p_one,6),
                "prediction":answer["prediction"],
                "inference_seconds":round(answer["inference_seconds"],6),
                "status":"PENCIL_ONLY_NOT_A_WITNESS"}
            return int(answer["prediction"]),max(p_one,1-p_one)
        w=initial_posterior(self.owner[sector]) if self.policy=="static" else m.weights
        p=sum(float(w[i]) for i in range(8) if outputs(i,x))
        prediction=int(p>=.5)
        confidence=max(p,1-p)
        if self.policy=="contrarian" and confidence<.999:
            prediction=1-prediction
        return prediction,confidence
    def _model_packet(self,sector,x):
        """Only observed unique within-sector owner receipts, never owner truth.

        A local PENCIL graph hypothesis is *not* a witness. No unverified
        survey rumor or earlier sector's hidden rule is included.
        """
        m=self.maps[sector]
        observations=[{"x":list(m.initial_x),"value":int(m.initial_value),
                       "source_root":m._first_source,"kind":"INITIAL_OWNER_RECEIPT"}]
        if self.policy!="llm_flat":
            for e in m.events:
                if e.get("independent") and e.get("response_kind")=="SOURCE_REPORT":
                    root=e.get("source_root")
                    if isinstance(root,str) and all(a["source_root"]!=root for a in observations):
                        observations.append({"x":list(e["x"]),"value":int(e["reported_value"]),
                                             "source_root":root,"kind":"INDEPENDENT_OWNER_RECEIPT"})
        if len(observations)>8 or len({a["source_root"] for a in observations})!=len(observations):
            raise ValueError("DUPLICATED_OR_OVERSIZED_MODEL_EVIDENCE")
        if any(e["x"]==list(x) for e in observations):
            raise ValueError("TARGET_ALREADY_SOURCED_MODEL_UNNECESSARY")
        return {"schema":"motif.real-model-evidence/v0",
                "sector":sector,"checkpoint":self.gate,"x":list(x),
                "observations":observations,
                "source_roots":[e["source_root"] for e in observations],
                "no_future_owner_truth":True,
                "rumor_sources_excluded":True,
                "real_world_authority":"none"}

    def _verification(self,sector,x,kind):
        m=self.maps[sector]
        if x==m.initial_x:
            self.metrics["calibration_reuses"]+=1
            return int(self.owner[sector].initial["value"]),m.initial_observation,None
        before=list(m.weights)
        prop=m.propose_query(x,rationale="odyssey-"+kind)
        if tuple(prop.x)!=tuple(x):raise GateError("SCOPE_MISMATCH")
        event=m.resolve(self.owner[sector],prop)
        source=event["source_root"]
        if not event["independent"] or source in self.per_sector_receipts[sector]:
            raise GateError("MISSING_INDEPENDENT_WITNESS")
        self.per_sector_receipts[sector].add(source)
        verified=int(event["reported_value"])
        grade_result=grade(self.owner[sector],(before,m.weights),event)
        if grade_result["verified_counterexample"]:
            if grade_result["wrong_helpful_net"]:
                if self.policy in ("static","llm_flat"):self.metrics["unrealized_counterexamples"]+=1
                else:self.metrics["learned_counterexamples"]+=1
        if grade_result["regression"]:self.metrics["actual_regressions"]+=1
        self.information_gains.append({"sector":sector,"gate":self.gate,"test_kind":kind,
          "reported_contradiction":event["contradiction_reported"],
          "verified_counterexample":grade_result["verified_counterexample"],
          "net_owner_accuracy_gain":round(grade_result["net_gain"],6),
          "source_root":source,"model_learning_used_by_policy":self.policy!="static"})
        return verified,event["receipt_node"],source
    def survey(self):
        self._survey(self.phase,self.gate)
    def decide(self):
        """Attempt the next surveyed gate with the frozen policy."""
        sector,gate=self.phase,self.gate
        self._position(sector,gate)
        if not self.surveyed:raise GateError("SURVEY_REQUIRED")
        x=self.order[sector][gate]
        guessed,confidence=self._prediction(sector,x)
        m=self.maps[sector]
        if self.policy in ("hypermap_voi","llm_verification") and x!=m.initial_x:
            expected_failure=(1-confidence)*(WRONG_PENALTY+REPAIR_COST)
            if expected_failure>PROBE_COST:
                truth,receipt,root=self._verification(sector,x,"optional-before-commit")
                self.metrics["optional_probes"]+=1
                self._step("independent_probe",sector,gate,
                    {"x":list(x),"reported_value":truth,"source_root":root,
                     "not_an_external_act":True,
                     "previously_proposed_pencil":guessed},PROBE_COST)
                # A just-verified label overrides inference. Prediction was
                # uncertain, but the source receipt is now independent evidence.
                guessed=truth;confidence=1.
        prior_guess=guessed
        if x==m.initial_x:
            actual,receipt,root=self._verification(sector,x,"calibration")
        elif x not in m.queries:
            actual,receipt,root=self._verification(sector,x,"first-commit")
        else:
            # The optional precommit probe already generated this source.
            # No second receipt or independent evidence is fabricated.
            probe_event=next(e for e in m.events if tuple(e["x"])==tuple(x))
            actual=int(probe_event["reported_value"])
            receipt=probe_event["receipt_node"]
            root=probe_event["source_root"]
        self.metrics["source_verified"]+=1
        correct=prior_guess==actual
        self._step("commit_correct" if correct else "commit_wrong",sector,gate,
            {"x":list(x),"pencil_answer":prior_guess,
             "synthetic_owner_report":actual,
             "correct":correct,
             "source_root":root or self.owner[sector].initial["root"],
             "source_node":receipt,
             "unverified_rumor_ignored":True,
             "confidence_before_verification":round(confidence,5),
             "real_model_pencil_proposal":copy.deepcopy(self.last_model_proposal) if
                self.policy in REAL_MODEL_POLICIES and x!=m.initial_x else None},
            COMMIT_COST+(0 if correct else WRONG_PENALTY))
        if correct:
            self.metrics["correct_commits"]+=1
            self._advance_after_success()
        else:
            self.metrics["wrong_commits"]+=1
            self.repair_needed=True
            self.expected_retry=actual
    def repair(self):
        if not self.repair_needed:raise GateError("NO_REPAIR_NEEDED")
        self._step("repair",self.phase,self.gate,
            {"wrong_guess_remains_recorded":True,
             "retry_requires_original_owner_receipt":True},REPAIR_COST)
        self.metrics["repair_actions"]+=1
        self.repair_needed=False
    def retry(self,answer):
        if self.expected_retry is None or not self.surveyed or self.repair_needed:
            raise GateError("REPAIR_AND_VERIFIED_RECEIPT_REQUIRED")
        if answer!=self.expected_retry:raise GateError("RETRY_MUST_USE_VERIFIED_RESULT")
        sector,gate=self.phase,self.gate
        self._step("commit_repaired",sector,gate,
            {"answer_from_existing_receipt":answer,
             "no_new_independent_witness":True},COMMIT_COST)
        self.metrics["correct_commits"]+=1
        self.expected_retry=None
        self._advance_after_success()
    def _advance_after_success(self):
        s,j=self.phase,self.gate
        if (s,j) in self.completed:raise GateError("DUPLICATE_COMPLETION")
        self.completed.add((s,j))
        self.surveyed=False
        self.gate+=1
    def audit(self,which):
        s=self.phase
        if which not in ("half","terminal") or (s,which) in self.audits:
            raise GateError("UNKNOWN_OR_DUPLICATE_AUDIT")
        threshold=4 if which=="half" else 8
        if self.gate!=threshold or self.surveyed or self.repair_needed:
            raise GateError("AUDIT_REQUIRES_COMPLETE_VERIFIED_GATES")
        if any((s,j) not in self.completed for j in range(threshold)):
            raise GateError("MISSING_GATES")
        # The initial calibration can occur AFTER the half-way point;
        # audit only roots actually tied to completed cells. Optional probes
        # for other future cells must not count toward this gate.
        relevant=[]
        for j in range(threshold):
            x=self.order[s][j]
            if x==self.owner[s].start_x:
                root=self.owner[s].initial["root"]
            else:
                matches=[e for e in self.maps[s].events if tuple(e["x"])==tuple(x)]
                if len(matches)!=1 or not matches[0]["independent"]:
                    raise GateError("AUDIT_MISSING_INDEPENDENT_REPORT")
                root=matches[0]["source_root"]
            relevant.append(root)
        if len(set(relevant))!=threshold:raise GateError("AUDIT_SOURCE_RECEIPT_COUNT_MISMATCH")
        # "Roots" are fixture roots, NOT signed real-world permissions.
        self.audits.add((s,which))
        self._step(which+"_audit",s,threshold-1,
            {"verified_gates":threshold,"distinct_source_roots":len(set(relevant)),
             "no_synthetic_permission_promotion":True},AUDIT_COST)
        self.metrics["half_audits" if which=="half" else "terminal_audits"]+=1
        if which=="terminal":
            self.completed_stage_hashes.append(self.previous_hash)
            if (s+1)%4!=0:self._next_sector()
    def relay(self):
        s=self.phase
        if (s+1)%4!=0 or (s,"terminal") not in self.audits or s in self.relays:
            raise GateError("TERMINAL_BRIDGE_DEPENDENCY_MISSING")
        if self.gate!=GATES_PER_SECTOR:raise GateError("NOT_AT_BRIDGE")
        self.relays.add(s)
        self._step("bridge_relay",s,7,
            {"last_four_sector_audits":[
                 self.completed_stage_hashes[i] for i in range(s-3,s+1)],
             "synthetic_gate_only":True},RELAY_COST)
        self.metrics["relays"]+=1
        if s==SECTORS-1:
            self.status="COMPLETED"
            self.phase=SECTORS;self.gate=0
        else:self._next_sector()
    def _next_sector(self):
        if (self.phase,"terminal") not in self.audits:raise GateError("NO_TERMINAL")
        self.phase+=1
        self.gate=0;self.surveyed=False
    def next_action(self):
        if self.status!="RUNNING":return "DONE"
        s,j=self.phase,self.gate
        if self.repair_needed:return "REPAIR"
        if self.expected_retry is not None:return "RETRY"
        if j==4 and (s,"half") not in self.audits:return "HALF_AUDIT"
        if j==8:
            if (s,"terminal") not in self.audits:return "TERMINAL_AUDIT"
            if (s+1)%4==0 and s not in self.relays:return "RELAY"
            raise GateError("UNREACHABLE_STATE")
        return "SURVEY" if not self.surveyed else "DECIDE"
    def execute(self):
        try:
            while self.status=="RUNNING":
                action=self.next_action()
                if action=="SURVEY":self.survey()
                elif action=="DECIDE":self.decide()
                elif action=="REPAIR":self.repair()
                elif action=="RETRY":self.retry(self.expected_retry)
                elif action=="HALF_AUDIT":self.audit("half")
                elif action=="TERMINAL_AUDIT":self.audit("terminal")
                elif action=="RELAY":self.relay()
                else:raise GateError("UNKNOWN_ACTION")
        except BudgetError:
            self.status="BUDGET_EXHAUSTED"
        return self.summary()
    def summary(self):
        actions=len(self.events)
        return {"schema":SCHEMA,"scenario_seed":self.seed,"policy":self.policy,
          "state":self.status,"completed":self.status=="COMPLETED",
          "completed_gates":len(self.completed),"expected_gates":REQUIRED_GATES,
          "actions":actions,"minimum_required_actions":MINIMUM_ACTIONS,
          "critical_path_minimum_actions":MINIMUM_ACTIONS,
          "cost":round(self.cost,5),
          "final_chain_hash":self.previous_hash,"stage_rule_count":SECTORS,
          "distinct_calibration_origins":len({o.initial["root"] for o in self.owner}),
          "source_verified_actions":self.metrics["source_verified"],
          "metrics":copy.deepcopy(self.metrics),
          "side_effects":0,"real_llm_used":self.decision_adapter is not None,
          "real_model_forwards":self.real_model_calls,
          "real_model_prompt_tokens":self.real_model_prompt_tokens,
          "real_model_inference_seconds":round(self.real_model_inference_seconds,4),
          "scorecard":"AUTHOR_SYNTHETIC_LONG_HORIZON_NOT_EXTERNAL_BENCHMARK"}
    def public_trace(self):
        return {"schema":SCHEMA,"scenario_seed":self.seed,"policy":self.policy,
          "summary":self.summary(),"events":copy.deepcopy(self.events),
          "per_sector": [
             {"sector":s,"current_posterior":[round(x,7) for x in m.weights],
              "owner_hidden_rule_excluded":True,
              "evidence_roots":sorted(m.sources),
              "map_hyperedge_ids":sorted(m.edges),
              "map_node_ids":sorted(m.nodes)}
             for s,m in enumerate(self.maps)],
          "reason_dividends":copy.deepcopy(self.information_gains),
          "hidden_owner_truth_excluded":True,
          "source_authority":"synthetic-only",
          "external_actions":False}

def experiment(seeds=SCENARIO_SEEDS,policies=POLICIES):
    arms=[]
    for policy in policies:
        cases=[LongChain(seed,policy).execute() for seed in seeds]
        n=len(cases)
        arms.append({"policy":policy,"worlds":n,
          "completed":sum(c["completed"] for c in cases),
          "completion_rate":round(sum(c["completed"] for c in cases)/n,5),
          "mean_actions":round(sum(c["actions"] for c in cases)/n,3),
          "min_actions":min(c["actions"] for c in cases),
          "max_actions":max(c["actions"] for c in cases),
          "mean_cost":round(sum(c["cost"] for c in cases)/n,3),
          "mean_wrong_commits":round(sum(c["metrics"]["wrong_commits"] for c in cases)/n,3),
          "total_wrong_commits":sum(c["metrics"]["wrong_commits"] for c in cases),
          "mean_optional_probes":round(sum(c["metrics"]["optional_probes"] for c in cases)/n,3),
          "total_learned_counterexamples":sum(c["metrics"]["learned_counterexamples"] for c in cases),
          "mean_completed_gates":round(sum(c["completed_gates"] for c in cases)/n,3)})
    # Prespecified primary completion, then total cost among completers,
    # then actions. Failure cannot buy victory by stopping early.
    sorted_arms=sorted(arms,key=lambda a:(-a["completion_rate"],
                a["mean_cost"] if a["completion_rate"]==1 else float("inf"),
                a["mean_actions"],a["policy"]))
    return {"schema":"motif.odyssey-240-study/v0","seed_count":len(seeds),
      "sequential_required_actions":MINIMUM_ACTIONS,
      "required_synthetic_verifications":REQUIRED_GATES,
      "author_synthetic_only":True,"real_model":False,
      "resource_limits":{"actions":ACTION_LIMIT,"cost":COST_LIMIT},
      "primary_comparison_rule":"complete all 96 first, then minimize total cost",
      "arms":arms,"ranking":[a["policy"] for a in sorted_arms],
      "external_actions":False}

if __name__=="__main__":
    print(json.dumps(experiment(),indent=2,sort_keys=True))
