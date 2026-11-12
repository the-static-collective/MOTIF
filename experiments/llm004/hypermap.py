"""LLM-004 REASON HYPERMAP: memory of *tested* wrong hypotheses.

Owner-local, event-sourced multi-relation hypothesis memory. All test worlds
are authored synthetic Boolean fixtures from LLM-003. Historical traversal
may be exported to Free Graph, but this module never grants authority, acts in
the real world, or writes to project sources.

One multi-terminal hyperedge may relate hypotheses + predicted answer + test
+ owner report to counterexample + posterior revision + next questions.
Source-owned receipts, source roots, causal lenses and truth are different.
"""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
import copy,json,math

from error_dividend import (
    Owner,INPUTS,POLICIES,HELDOUT,DEV,outputs,initial_posterior,choose,
    update,entropy,favorite,accuracy,expected_ig,QUERY_COST
)

SCHEMA="motif.reason-hypermap/v0"
LENSES=("epistemic","causal","decision","lineage","narrative")
KINDS={"hypothesis","observation","prediction","test","receipt","counterexample",
       "revision","question","hyperedge"}
MAX_EVENTS=8

def canonical(x):
    return json.dumps(x,sort_keys=True,ensure_ascii=False,separators=(",",":"),allow_nan=False)
def hash_of(x):
    return sha256(canonical(x).encode("utf-8")).hexdigest()
def numbered(prefix,contents):
    return f"{prefix}:sha256:{hash_of(contents)}"
def bayes_accuracy(weights):
    """Expected majority-class accuracy over all future query inputs, given posterior."""
    return sum(max(p,1-p) for p in (
      sum(w for i,w in enumerate(weights) if outputs(i,x)==1)
      for x in INPUTS))/len(INPUTS)
def decision_gain(weights,x,noise=0.):
    """Expected Bayes decision improvement BEFORE knowing answer: no owner truth."""
    before=bayes_accuracy(weights)
    after=0.
    for y in (0,1):
        p=sum(w*((1-noise) if outputs(i,x)==y else noise)
              for i,w in enumerate(weights))
        if p>0:
            posterior,_=update(weights,x,y,noise)
            after+=p*bayes_accuracy(posterior)
    return after-before

@dataclass(frozen=True)
class ProposedTest:
    id:str
    step:int
    x:tuple
    expected:int
    favored:int
    prior_state:str
    rationale:str

class ReasonHypermap:
    def __init__(self,owner:Owner,cost=QUERY_COST):
        if not isinstance(owner,Owner):raise ValueError("SYNTHETIC_OWNER_ONLY")
        if not (0<cost<=.5):raise ValueError("BAD_COST")
        self.seed=owner.seed
        self.regime=owner.regime
        self.cost=cost
        self.weights=list(initial_posterior(owner))
        self.nodes={}
        self.edges={}
        self.sources={}
        self.events=[]
        self.queries=set()
        self.active=None
        self.hypotheses={}
        self._model_source=self._source("fixture-hypothesis-family-v0",kind="project-source",
            content="Eight author-defined binary Boolean programs in LLM-003 error_dividend.py")
        self._first_source=self._source(owner.initial["root"],kind="specimen-receipt",
            content={"x":list(owner.initial["x"]),"value":owner.initial["value"],
                     "regime":"initial independently synthesized fixture"},
            observed=True)
        for i in range(8):
            self.hypotheses[i]=self._node("hypothesis",f"H{i}: authored possible rule {i}",
                "proposed",[self._model_source],{"program_index":i})
        self.initial_observation=self._node(
            "observation",f"Starting verified fixture: {owner.start_x} -> {owner.initial['value']}",
            "tested",[self._first_source],
            {"x":list(owner.start_x),"reported_value":owner.initial["value"]})
        self.initial_x=owner.start_x
        self.initial_value=owner.initial["value"]
        self.snapshots=[self.snapshot()]
    def _source(self,root,*,kind,content,observed=False):
        if not isinstance(root,str) or not root or len(root)>180:raise ValueError("BAD_SOURCE_ROOT")
        if root in self.sources:return root
        if len(self.sources)>=80:raise ValueError("SOURCE_LIMIT")
        self.sources[root]={"root":root,"kind":kind,"content":copy.deepcopy(content),
                            "observed":bool(observed)}
        return root
    def _node(self,kind,label,status,source_roots,meta=None):
        if kind not in KINDS or not label or status not in ("proposed","tested","unresolved"):
            raise ValueError("BAD_NODE")
        if not source_roots or any(r not in self.sources for r in source_roots):
            raise ValueError("UNSOURCED_NODE")
        record={"kind":kind,"label":label,"status":status,
                "source_roots":sorted(set(source_roots)),"metadata":copy.deepcopy(meta or {})}
        nid=numbered("hmn",record)
        if len(self.nodes)>=400 and nid not in self.nodes:raise ValueError("NODE_LIMIT")
        self.nodes.setdefault(nid,record)
        return nid
    def _edge(self,relation,tails,heads,source_roots,status="proposed",details=None):
        if not tails or not heads or len(tails)>16 or len(heads)>16:
            raise ValueError("BAD_HYPEREDGE")
        if any(n not in self.nodes for n in (*tails,*heads)):
            raise ValueError("DANGLING_HYPEREDGE")
        if any(s not in self.sources for s in source_roots):
            raise ValueError("UNSOURCED_EDGE")
        record={"relation":relation,"tails":sorted(set(tails)),"heads":sorted(set(heads)),
                "source_roots":sorted(set(source_roots)),"status":status,
                "metadata":copy.deepcopy(details or {})}
        eid=numbered("hme",record)
        if len(self.edges)>=200 and eid not in self.edges:raise ValueError("EDGE_LIMIT")
        self.edges.setdefault(eid,record)
        return eid
    def _state(self):
        return {"posterior":[round(x,14) for x in self.weights],
                "events":[e["id"] for e in self.events],
                "used_queries":[list(x) for x in sorted(self.queries)]}
    def state_id(self):
        return numbered("hms",{"seed":self.seed,"state":self._state()})
    def snapshot(self):
        return copy.deepcopy({"state_id":self.state_id(),"posterior":self.weights,
                              "events":self.events,"queries":sorted(self.queries)})
    def choose_test(self,policy="challenge_favorite",allow_costly=False):
        if policy not in (*POLICIES,"decision_gain","classical_ig_stop"):
            raise ValueError("UNKNOWN_POLICY")
        if self.active is not None:raise ValueError("ONE_OUTSTANDING_TEST")
        if len(self.events)>=MAX_EVENTS or policy=="no_probe":return None
        remaining=tuple(x for x in INPUTS if x!=self.initial_x and x not in self.queries)
        if not remaining:return None
        noise=.2 if self.regime=="noise20" else 0.
        if policy in ("decision_gain","classical_ig_stop"):
            x=(max(remaining,key=lambda q:(round(decision_gain(self.weights,q,noise),12),
                                            tuple(-v for v in q)))
               if policy=="decision_gain"
               else choose("classical_ig",self.weights,remaining,self.seed,len(self.events),noise))
            # Same stopping criterion for both: only *choice* differs.
            if decision_gain(self.weights,x,noise)<=self.cost and not allow_costly:
                return None
        else:x=choose(policy,self.weights,remaining,self.seed,len(self.events),noise)
        if x is None:return None
        favored=favorite(self.weights)
        predicted=outputs(favored,x)
        prior=self.state_id()
        rationale=("counterexample-search" if policy=="challenge_favorite" else
                   "bayes-decision-value" if policy=="decision_gain" else
                   "classical-IG-cost-stop" if policy=="classical_ig_stop" else policy)
        predicted_node=self._node("prediction",f"PENCIL: H{favored} predicts {predicted} for {x}",
            "proposed",[self._model_source],{"world":self.seed,"x":list(x),
                  "answer":predicted,"favorite":favored,"not_verified":True})
        test=self._node("test",f"Fictional owner probe at {x} ({rationale})",
            "proposed",[self._model_source],{"x":list(x),"policy":policy})
        self._edge("proposes-test",[self.hypotheses[favored],predicted_node],[test],
                   [self._model_source],"proposed",{"lens":"causal","not_an_action":True})
        p=ProposedTest(numbered("hmp",{"step":len(self.events),"state":prior,
             "x":x,"predicted":predicted,"policy":policy}),len(self.events),x,predicted,
             favored,prior,rationale)
        self.active={"proposal":p,"test":test,"prediction":predicted_node,"policy":policy}
        return p
    def imagined_outcomes(self,proposal):
        if self.active is None or proposal!=self.active["proposal"]:
            raise ValueError("PROPOSAL_NOT_ACTIVE")
        noise=.2 if self.regime=="noise20" else 0.
        outcomes=[]
        for y in (0,1):
            posterior,_=update(self.weights,proposal.x,y,noise)
            p=sum(w*((1-noise) if outputs(i,proposal.x)==y else noise)
                  for i,w in enumerate(self.weights))
            outcomes.append({"imagined_result":y,"hypothetical_probability":round(p,6),
                 "hypothetical_posterior":[round(v,8) for v in posterior],
                 "hypothetical_bayes_accuracy":round(bayes_accuracy(posterior),6),
                 "status":"PENCIL_ONLY_NOT_OBSERVED"})
        return outcomes
    def resolve(self,owner:Owner,proposal:ProposedTest):
        if self.active is None or proposal!=self.active["proposal"]:
            raise ValueError("NO_ACTIVE_PROPOSAL")
        if not isinstance(owner,Owner) or owner.seed!=self.seed or owner.regime!=self.regime:
            raise ValueError("WRONG_SIMULATED_OWNER")
        if proposal.prior_state!=self.state_id() or proposal.x in self.queries:
            raise ValueError("STALE_OR_REPLAYED_TEST")
        if len(self.events)>=MAX_EVENTS:raise ValueError("EVENT_LIMIT")
        # Synthetic owner is actually called; this is not a model-created receipt.
        response=owner.probe(proposal.x)
        self.queries.add(proposal.x)
        before=list(self.weights)
        root=response.get("root")
        independent=(response.get("kind")=="SOURCE_REPORT" and
                     isinstance(root,str) and root not in self.sources and
                     response.get("x")==proposal.x and response.get("value") in (0,1))
        new_source=None
        if independent:
            new_source=self._source(root,kind="specimen-receipt",
                content={"x":list(proposal.x),"reported":response["value"],
                         "regime":self.regime},observed=True)
            noise=.2 if self.regime=="noise20" else 0.
            posterior,updated=update(self.weights,proposal.x,response["value"],noise)
            if updated:self.weights=posterior
        else:updated=False
        evidence_roots=[self._model_source]+([new_source] if new_source else [])
        if independent:
            receipt=self._node("receipt",f"Independent fictional report {proposal.x} -> {response['value']}",
                "tested",[new_source],{"reported_value":response["value"],
                   "x":list(proposal.x),"synthetic_owner":True,
                   "not_real_world_authority":True})
        else:
            receipt=self._node("receipt",f"HOLD: {response.get('kind','INVALID')} at {proposal.x}",
                "unresolved",[self._model_source],
                {"kind":response.get("kind","INVALID"),"not_a_new_witness":True})
        if independent and updated:
            change=self._node("revision","Posterior revision after sourced fictitious probe",
                "tested",evidence_roots,{"before":[round(v,10) for v in before],
                "after":[round(v,10) for v in self.weights],
                "cost":self.cost,"difference_not_owner_truth":True})
        else:change=self._node("question","Unverified result: hold previous posterior",
            "unresolved",[self._model_source],{"reason":"no independent usable report"})
        contradiction=bool(independent and proposal.expected!=response["value"])
        heads=[receipt,change]
        if contradiction:
            counter=self._node("counterexample","A report contradicts the previously favored PENCIL prediction",
              "tested",[new_source],{"x":list(proposal.x),"favored":proposal.favored,
               "reported":response["value"],"prior_prediction":proposal.expected,
               "truth_not_proven":self.regime!="truthful"})
            heads.append(counter)
        # This is truly multi-terminal: a set of causes -> a set of results.
        hyper=self._edge("test-revises-possibilities",
            [self.hypotheses[proposal.favored],self.active["prediction"],self.active["test"]],
            heads,evidence_roots,"tested" if independent else "unresolved",
            {"independent_origin":independent,"contradicts_favorite":contradiction,
             "step":proposal.step,"not_authorizing":True})
        if independent:
            # One result may bear differently on several rival hypotheses.
            conflicting=[i for i in range(8) if outputs(i,proposal.x)!=response["value"]]
            supporting=[i for i in range(8) if outputs(i,proposal.x)==response["value"]]
            if conflicting:
                self._edge("report-bears-on-rivals",[receipt],
                    [self.hypotheses[i] for i in conflicting], [new_source],"tested",
                    {"bearing":"refuses","reported_not_truth":True})
            if supporting:
                self._edge("report-supports-rivals",[receipt],
                    [self.hypotheses[i] for i in supporting], [new_source],"tested",
                    {"bearing":"supports","reported_not_truth":True})
        old_state=proposal.prior_state
        e={"id":numbered("hmev",{"step":proposal.step,"proposal":proposal.id,
                "response_kind":response.get("kind"),"root":root,
                "reported":response.get("value"),"independent":independent}),
           "step":proposal.step,"proposal_id":proposal.id,"x":list(proposal.x),
           "policy":self.active["policy"],"favored":proposal.favored,
           "predicted":proposal.expected,"response_kind":response.get("kind"),
           "reported_value":response.get("value") if independent else None,
           "source_root":root if independent else None,
           "independent":independent,"receipt_node":receipt,
           "hyperedge":hyper,"contradiction_reported":contradiction,
           "posterior_changed":self.weights!=before,
           "entropy_before":round(entropy(before),8),
           "entropy_after":round(entropy(self.weights),8),
           "bayes_decision_value_before":round(bayes_accuracy(before),8),
           "bayes_decision_value_after":round(bayes_accuracy(self.weights),8),
           "cost":self.cost,"world_id":self.seed,
           "origin_state":old_state,"no_fact_promotion":True}
        self.events.append(e)
        self.active=None
        self.snapshots.append(self.snapshot())
        return copy.deepcopy(e)
    def view(self,lens):
        if lens not in LENSES:raise ValueError("UNKNOWN_LENS")
        core={"schema":SCHEMA,"world":"public-author-synthetic","seed":self.seed,
              "state_id":self.state_id(),"nodes":self.nodes,"hyperedges":self.edges,
              "source_roots":self.sources}
        identity=numbered("hmidentity",core)
        labels={"epistemic":"which claims survived reports?",
                "causal":"which tests produced which revisions?",
                "decision":"which alternative changes reachable actions?",
                "lineage":"which sources and states descend from what?",
                "narrative":"how did a provisional mistake change the story?"}
        selected=[eid for eid,e in self.edges.items() if lens=="causal" or
          (lens=="epistemic" and e["relation"] in ("report-bears-on-rivals","report-supports-rivals")) or
          (lens=="decision" and e["relation"]=="test-revises-possibilities") or
          (lens=="lineage" and e["relation"]=="proposes-test") or
          (lens=="narrative" and e["relation"]=="test-revises-possibilities")]
        return {"lens":lens,"question":labels[lens],"immutable_identity":identity,
                "nodes":list(self.nodes.keys()),"selected_hyperedge_ids":selected,
                "source_roots":sorted(self.sources),
                "authority":"none","external_actions":False}
    def public_graph(self):
        return copy.deepcopy({"schema":SCHEMA,"world":"PUBLIC_AUTHOR_SYNTHETIC_ONLY",
                "seed":self.seed,"regime":self.regime,"state_id":self.state_id(),
                "posterior":[round(x,12) for x in self.weights],
                "nodes":self.nodes,"hyperedges":self.edges,"sources":self.sources,
                "events":self.events,"snapshots":self.snapshots,
                "authority":"none","external_actions":False,
                "owner_hidden_truth_excluded":True})

def grade(owner,states,event,cost=QUERY_COST):
    """Separate owning synthetic oracle evaluator. NEVER included in graph export."""
    before,after=states
    if not isinstance(owner,Owner):raise ValueError("OWNER_ONLY")
    original=accuracy(owner,before)
    revised=accuracy(owner,after)
    actually_wrong=outputs(event["favored"],tuple(event["x"]))!=owner.truth(tuple(event["x"]))
    truly_independent_right=(event["independent"] and
      event["reported_value"]==owner.truth(tuple(event["x"])))
    return {"actual_wrong_provisional":actually_wrong,
        "verified_counterexample":bool(event["contradiction_reported"] and
             truly_independent_right and actually_wrong),
        "reported_contradiction_not_ground_truth":bool(event["contradiction_reported"] and
             not truly_independent_right),
        "accuracy_before":original,"accuracy_after":revised,
        "accuracy_gain":revised-original,"net_gain":revised-original-cost,
        "wrong_helpful_net":bool(actually_wrong and truly_independent_right and
             revised-original>cost),
        "regression":revised<original,"probe_cost":cost,
        "hidden_owner_used_only_in_grader":True}
