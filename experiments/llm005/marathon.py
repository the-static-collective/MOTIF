"""ODYSSEY-MARATHON: 879+ causally linked actions across 48 owner worlds.

FOUR complete serial 12-sector chains. Each must independently finish before
the next can begin, and each handoff witnesses its preceding terminal digest.
The global ledger includes original child's hash and its own previous hash.
This is a public author-designed toy stress case, NOT real LLM inference.
"""
from __future__ import annotations
import copy,json
from odyssey import LongChain,SCENARIO_SEEDS,POLICIES,REAL_MODEL_POLICIES,MINIMUM_ACTIONS,REQUIRED_GATES,digest

GROUPS=(
 (8001,8002,8003,8004),
 (8005,8006,8007,8008),
 (8009,8010,8011,8012),
 (8013,8014,8015,8016),
)
SEGMENTS=4
INTERLINKS=3
MIN_ACTIONS=MINIMUM_ACTIONS*SEGMENTS+INTERLINKS
MIN_GATES=REQUIRED_GATES*SEGMENTS
ACTION_CAP=1350
COST_CAP=1800

class Marathon:
    def __init__(self,seeds=GROUPS[0],policy="hypermap_voi",decision_adapter=None):
        if not isinstance(seeds,tuple) or seeds not in GROUPS:raise ValueError("BAD_REGISTERED_GROUP")
        if policy not in POLICIES+REAL_MODEL_POLICIES:raise ValueError("BAD_POLICY")
        if (policy in REAL_MODEL_POLICIES)!=(decision_adapter is not None):
            raise ValueError("MISSING_REAL_MODEL_OR_UNEXPECTED_ADAPTER")
        self.seeds=seeds;self.policy=policy
        self.decision_adapter=decision_adapter
        self.children=[];self.events=[];self.status="PENDING"
        self.hash="0"*64;self.cost=0
        self.stop_reason=None
        self.handoffs=[]
        self.complete_segments=0
    def _emit(self,kind,segment,payload,cost):
        if len(self.events)>=ACTION_CAP or self.cost+cost>COST_CAP+1e-9:
            raise ValueError("GLOBAL_BUDGET")
        self.cost+=cost
        event={"index":len(self.events)+1,"kind":kind,
            "segment":segment,"payload":copy.deepcopy(payload),
            "prior_hash":self.hash,"cost":round(cost,5),
            "cumulative_cost":round(self.cost,5),
            "real_world_effects":False,"source":"AUTHOR_SYNTHETIC_ONLY"}
        event["hash"]=digest(event)
        self.hash=event["hash"]
        self.events.append(event)
        return event
    def execute(self):
        if self.status!="PENDING":raise ValueError("MARATHON_ALREADY_EXECUTED")
        self.status="RUNNING"
        for i,seed in enumerate(self.seeds):
            if i!=self.complete_segments:
                raise ValueError("CHAIN_SEGMENT_SKIPPED")
            if i>0 and len(self.handoffs)!=i:
                raise ValueError("HANDOFF_REQUIRED")
            runner=LongChain(seed,self.policy,decision_adapter=self.decision_adapter)
            outcome=runner.execute()
            # Append only actual performed actions; unfinished child is not
            # considered a completed segment or a valid next-segment origin.
            for event in runner.events:
                try:self._emit("odyssey_action",i,{"child_action":event["action"],
                     "child_hash":event["hash"],"child_previous":event["prior_hash"],
                     "child_kind":event["kind"],"child_sector":event["sector"],
                     "child_gate":event["gate"],"child_meta":event["meta"]},
                     event["cost"])
                except ValueError:
                    self.status="GLOBAL_BUDGET_EXHAUSTED"
                    self.stop_reason="GLOBAL_BUDGET"
                    return self.summary()
            self.children.append({"seed":seed,"summary":outcome,
                "first_action_digest":runner.events[0]["hash"] if runner.events else None,
                "last_action_digest":runner.events[-1]["hash"] if runner.events else None,
                "segment_terminal_global_hash":self.hash,
                "distinct_source_owners":[o.seed for o in runner.owner]})
            if not outcome["completed"]:
                self.status="SEGMENT_INCOMPLETE"
                self.stop_reason=f"SEGMENT_{i+1}:{outcome['state']}"
                return self.summary()
            self.complete_segments+=1
            if i<SEGMENTS-1:
                # This is a REAL DEPENDENCY TRANSITION in the synthetic
                # serial chain, not a decorative reference in a document.
                last=self.children[-1]
                handoff=self._emit("mandatory_handoff",i,{
                    "verified_previous_segment_terminal_digest":last["last_action_digest"],
                    "previous_complete_96_gates":True,
                    "previous_stage_global_hash":last["segment_terminal_global_hash"],
                    "next_registered_seed":self.seeds[i+1],
                    "no_project_authority":True},1.)
                self.handoffs.append(handoff["hash"])
        self.status="COMPLETED"
        return self.summary()
    def summary(self):
        done=self.status=="COMPLETED"
        sources=sum(len(c.get("distinct_source_owners",[])) for c in self.children)
        return {"schema":"motif.odyssey-marathon/v0","seeds":list(self.seeds),
           "policy":self.policy,"state":self.status,"completed":done,
           "completed_subchains":self.complete_segments,
           "total_required_subchains":SEGMENTS,
           "mandatory_handoffs_completed":len(self.handoffs),
           "minimal_sequential_actions":MIN_ACTIONS,
           "actual_serial_actions":len(self.events),
           "synthetic_cost":round(self.cost,5),
           "completed_decision_gates":sum(c["summary"]["completed_gates"] for c in self.children),
           "required_gates":MIN_GATES,
           "distinct_source_owner_seeds":len(set(seed for c in self.children for seed in c["distinct_source_owners"])),
           "global_final_digest":self.hash,"stop_reason":self.stop_reason,
           "wrong_commitments":sum(c["summary"]["metrics"]["wrong_commits"] for c in self.children),
           "optional_independent_probes":sum(c["summary"]["metrics"]["optional_probes"] for c in self.children),
           "learned_verified_counterexamples":sum(c["summary"]["metrics"]["learned_counterexamples"] for c in self.children),
           "verified_commitments":sum(c["summary"]["metrics"]["source_verified"] for c in self.children),
           "audits":sum(c["summary"]["metrics"]["half_audits"]+
                        c["summary"]["metrics"]["terminal_audits"] for c in self.children),
           "relays":sum(c["summary"]["metrics"]["relays"] for c in self.children),
           "real_model_forwards":sum(c["summary"].get("real_model_forwards",0) for c in self.children),
           "real_model_prompt_tokens":sum(c["summary"].get("real_model_prompt_tokens",0) for c in self.children),
           "real_model_inference_seconds":round(sum(c["summary"].get("real_model_inference_seconds",0) for c in self.children),4),
           "source_authority":"fictional-only","decision_adapter_used":self.decision_adapter is not None,
           "real_llm":getattr(self.decision_adapter,"is_real_pretrained",False) is True,
           "external_actions":False,"hidden_owner_truth_excluded":True}
    def public_record(self):
        return copy.deepcopy({"schema":"motif.odyssey-marathon/v0",
              "summary":self.summary(),"segments":self.children,
              "global_events":self.events,
              "authority":"none","hidden_owner_truth_excluded":True,
              "external_actions":False})

def experiment(groups=GROUPS,policies=POLICIES):
    rows=[]
    for policy in policies:
        cases=[]
        for group in groups:
            m=Marathon(group,policy)
            cases.append(m.execute())
        n=len(cases)
        rows.append({"policy":policy,"marathons":n,
          "full_completions":sum(x["completed"] for x in cases),
          "mean_serial_actions":round(sum(x["actual_serial_actions"] for x in cases)/n,4),
          "mean_synthetic_cost":round(sum(x["synthetic_cost"] for x in cases)/n,4),
          "mean_wrong_commits":round(sum(x["wrong_commitments"] for x in cases)/n,4),
          "mean_optional_probes":round(sum(x["optional_independent_probes"] for x in cases)/n,4),
          "mean_completed_decisions":round(sum(x["completed_decision_gates"] for x in cases)/n,4),
          "min_serial_actions":min(x["actual_serial_actions"] for x in cases),
          "max_serial_actions":max(x["actual_serial_actions"] for x in cases)})
    return {"schema":"motif.odyssey-marathon.study/v0",
       "author_synthetic_only":True,"independent_registered_groups":len(groups),
       "sequential_minimum":MIN_ACTIONS,"required_decision_gates":MIN_GATES,
       "actions_cap":ACTION_CAP,"cost_cap":COST_CAP,
       "real_llm_used":False,"external_actions":False,
       "arms":rows}

if __name__=="__main__":
    print(json.dumps(experiment(),sort_keys=True,indent=2))
