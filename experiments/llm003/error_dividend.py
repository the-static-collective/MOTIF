"""LLM-003 Error Dividend: counterexamples as *tests*, not permission to lie.

Deterministic, independently owned synthetic Boolean task family. The owner
holds truth hidden from policies; source-provenance feedback can be missing,
correlated or unreliable. Same candidate set and query budgets for every arm.
No external data, learning of model weights, users or actual actions.
"""
from __future__ import annotations
import hashlib, json, math, random
from collections import defaultdict

INPUTS=tuple((a,b,c) for a in (0,1) for b in (0,1) for c in (0,1))
POLICIES=("classical_ig","challenge_favorite","confirm_favorite","uniform_random","no_probe")
REGIMES=("truthful","noise20","echo_origin","no_feedback")
BUDGETS=(0,1,2,3)
HELDOUT=tuple(range(8001,8161))
DEV=tuple(range(1201,1221))
QUERY_COST=.04

def functions(x):
    a,b,c=x
    return (a,b,c,a^b,b^c,a&b,a|c,a^b^c)

def outputs(index,x):
    return functions(x)[index]

def seeded(seed,part):
    raw=hashlib.sha256(f"motif-003-error-dividend:{seed}:{part}".encode()).digest()
    return random.Random(int.from_bytes(raw[:8],"big"))

class Owner:
    """Independent read-only oracle. Public policy methods cannot read _truth."""
    def __init__(self,seed,regime):
        if seed not in HELDOUT+DEV:raise ValueError("UNREGISTERED_CASE")
        if regime not in REGIMES:raise ValueError("BAD_REGIME")
        self._truth=seeded(seed,"hidden-owner").randrange(8)
        self._rng=seeded(seed,"truthful-initial")
        self.seed=seed; self.regime=regime; self.used=set()
        self.start_x=INPUTS[seeded(seed,"initial").randrange(len(INPUTS))]
        self.origin=f"owner-{seed}-initial"
        self.initial=self._receipt(self.start_x,first=True)
    def truth(self,x):
        return outputs(self._truth,x)
    def _receipt(self,x,first=False):
        if not first and self.regime=="no_feedback":
            return {"kind":"HOLD_NO_FEEDBACK","source":"NO_SOURCE","root":None}
        if not first and self.regime=="echo_origin":
            return {"kind":"ECHO_ONLY","source":"FORWARDED_INITIAL","root":self.origin,
                    "value":self.initial["value"],"x":self.start_x}
        y=self.truth(x)
        if self.regime=="noise20" and not first and seeded(self.seed,f"noise:{x}").random()<.2:
            y=1-y
        return {"kind":"SOURCE_REPORT","source":"INDEPENDENT_SYNTHETIC_OWNER",
                "root":self.origin if first else f"owner-{self.seed}-probe-{x}",
                "x":x,"value":y}
    def probe(self,x):
        if x not in INPUTS:raise ValueError("UNREGISTERED_PROBE")
        if x in self.used:raise ValueError("REUSED_PROBE")
        self.used.add(x)
        return self._receipt(x)

def update(weights,x,observed,noise=.0):
    # Correct Bayesian update within the known family. Noise-aware: false
    # reporting carries probability noise, not irreversible ground truth.
    numer=[w*((1-noise) if outputs(i,x)==observed else noise)
           for i,w in enumerate(weights)]
    den=sum(numer)
    if den<=0: return list(weights),False
    return [v/den for v in numer],True

def initial_posterior(owner):
    weights=[1/8.0]*8
    receipt=owner.initial
    assert receipt["kind"]=="SOURCE_REPORT"
    w,_=update(weights,receipt["x"],receipt["value"])
    return w

def favorite(weights):
    return max(range(8),key=lambda i:(weights[i],-i))

def predict(weights,x):
    prob=sum(w for i,w in enumerate(weights) if outputs(i,x))
    return int(prob>=.5)

def accuracy(owner,weights):
    return sum(predict(weights,x)==owner.truth(x) for x in INPUTS)/8

def entropy(weights):
    return -sum(p*math.log2(p) for p in weights if p>0)

def expected_ig(weights,x,noise=.0):
    h0=entropy(weights); expected=0.
    for y in (0,1):
        probability=sum(w*((1-noise) if outputs(i,x)==y else noise)
                        for i,w in enumerate(weights))
        if probability>0:
            posterior,_=update(weights,x,y,noise)
            expected+=probability*entropy(posterior)
    return h0-expected

def choose(policy,weights,remaining,seed,step,noise=.0):
    if policy=="no_probe":return None
    if not remaining:return None
    if policy=="uniform_random":
        return remaining[seeded(seed,f"random-probe:{step}").randrange(len(remaining))]
    lead=favorite(weights)
    if policy=="classical_ig":
        return max(remaining,key=lambda x:(round(expected_ig(weights,x,noise),12),tuple(-z for z in x)))
    if policy=="challenge_favorite":
        # Probe plausible near-misses: where the leader predicts a result
        # that supported rival hypotheses collectively oppose. Unlike IG,
        # it maximizes probability of catching the leading candidate wrong.
        return max(remaining,key=lambda x:(
          sum(w for i,w in enumerate(weights) if outputs(i,x)!=outputs(lead,x)),
          round(expected_ig(weights,x,noise),12),tuple(-z for z in x)))
    if policy=="confirm_favorite":
        # Deliberately weak confirmation-seeking comparator.
        return min(remaining,key=lambda x:(
          sum(w for i,w in enumerate(weights) if outputs(i,x)!=outputs(lead,x)),
          -round(expected_ig(weights,x,noise),12),x))
    raise ValueError("BAD_POLICY")

def episode(seed,regime,policy,budget):
    if budget not in BUDGETS or policy not in POLICIES:raise ValueError("BAD_POLICY_BUDGET")
    owner=Owner(seed,regime)
    weights=initial_posterior(owner)
    start_acc=accuracy(owner,weights)
    seen_roots={owner.initial["root"]}
    trace=[];last_utility=start_acc
    for step in range(budget):
        if policy=="no_probe":break
        remaining=tuple(x for x in INPUTS if x!=owner.start_x and x not in owner.used)
        x=choose(policy,weights,remaining,seed,step,.2 if regime=="noise20" else 0)
        if x is None:break
        lead=favorite(weights);prior_acc=accuracy(owner,weights)
        prior_entropy=entropy(weights);prior_choice=outputs(lead,x)
        r=owner.probe(x)
        truthful_observation=(r["kind"]=="SOURCE_REPORT" and r["value"]==owner.truth(x))
        actually_wrong=prior_choice!=owner.truth(x)
        verified_wrong=truthful_observation and actually_wrong
        changed=False
        if r.get("root") and r["root"] not in seen_roots and r["kind"]=="SOURCE_REPORT":
            seen_roots.add(r["root"])
            weights,changed=update(weights,x,r["value"],.2 if regime=="noise20" else 0)
        updated=accuracy(owner,weights)
        decision_delta=updated-prior_acc
        net_delta=decision_delta-QUERY_COST
        trace.append({"x":x,"reported_kind":r["kind"],"source_root":r.get("root"),
            "verified_wrong_proposal":verified_wrong,"underlying_wrong":actually_wrong,
            "false_owner_report":r["kind"]=="SOURCE_REPORT" and not truthful_observation,
            "changed_posterior":changed,"entropy_change":prior_entropy-entropy(weights),
            "accuracy_before":prior_acc,"accuracy_after":updated,"accuracy_delta":decision_delta,
            "net_step_utility":net_delta,"wrong_helpful_net":verified_wrong and net_delta>0,
            "correct_to_wrong_regression":prior_acc>updated})
    final_acc=accuracy(owner,weights)
    posterior_true=weights[owner._truth] # reporting only after all policy steps
    final_log_loss=-math.log(max(posterior_true,1e-12))
    cost=len(trace)*QUERY_COST
    return {"seed":seed,"regime":regime,"policy":policy,"budget":budget,
      "start_accuracy":start_acc,"final_accuracy":final_acc,
      "net_utility":final_acc-cost,"posterior_log_loss":final_log_loss,
      "probes":len(trace),"wrong_proposals":sum(t["underlying_wrong"] for t in trace),
      "verified_wrong":sum(t["verified_wrong_proposal"] for t in trace),
      "wrong_helpful_net":sum(t["wrong_helpful_net"] for t in trace),
      "wrong_no_gain":sum(t["verified_wrong_proposal"] and t["accuracy_delta"]<=0 for t in trace),
      "false_reports":sum(t["false_owner_report"] for t in trace),
      "regressions":sum(t["correct_to_wrong_regression"] for t in trace),
      "echo_ignored":sum(t["reported_kind"]=="ECHO_ONLY" and not t["changed_posterior"] for t in trace),
      "hold_no_feedback":sum(t["reported_kind"]=="HOLD_NO_FEEDBACK" for t in trace),
      "records":trace}

def experiment(seeds=HELDOUT):
    rows=[]
    for regime in REGIMES:
        for budget in BUDGETS:
            for policy in POLICIES:
                eps=[episode(seed,regime,policy,budget) for seed in seeds]
                n=len(eps);total_wrong=sum(e["verified_wrong"] for e in eps)
                rows.append({"regime":regime,"budget":budget,"policy":policy,"n":n,
                   "start_accuracy":round(sum(e["start_accuracy"] for e in eps)/n,5),
                   "end_accuracy":round(sum(e["final_accuracy"] for e in eps)/n,5),
                   "net_utility":round(sum(e["net_utility"] for e in eps)/n,5),
                   "log_loss":round(sum(e["posterior_log_loss"] for e in eps)/n,5),
                   "mean_probes":round(sum(e["probes"] for e in eps)/n,5),
                   "verified_wrong":total_wrong,
                   "wrong_helpful_net":sum(e["wrong_helpful_net"] for e in eps),
                   "wrong_helpful_rate":round(sum(e["wrong_helpful_net"] for e in eps)/total_wrong,4) if total_wrong else None,
                   "wrong_no_gain":sum(e["wrong_no_gain"] for e in eps),
                   "regressions":sum(e["regressions"] for e in eps),
                   "false_reports":sum(e["false_reports"] for e in eps),
                   "echo_ignored":sum(e["echo_ignored"] for e in eps),
                   "holds":sum(e["hold_no_feedback"] for e in eps)})
    winners=[]
    for regime in REGIMES:
        for budget in BUDGETS:
            candidates=[r for r in rows if r["regime"]==regime and r["budget"]==budget]
            top=max(r["net_utility"] for r in candidates)
            winners.append({"regime":regime,"budget":budget,
                "winner_ties":[r["policy"] for r in candidates if abs(r["net_utility"]-top)<1e-9],
                "winning_net_utility":top,
                "classical_ig_net":next(r["net_utility"] for r in candidates if r["policy"]=="classical_ig")})
    return {"test":"ERROR_DIVIDEND_V0","status":"INDEPENDENT_AUTHOR_SIMULATOR_ONLY",
      "seed_count":len(seeds),"case_split":"HELDOUT" if tuple(seeds)==HELDOUT else "DEVELOPMENT",
      "prior_hypotheses":8,"input_combinations":8,"query_cost":QUERY_COST,
      "policy_information":"SAME_PRIOR_AND_IDENTICAL_QUERY_BUDGETS",
      "real_model":False,"external_actions":False,
      "conditions":rows,"winners":winners}

if __name__=="__main__":
    print(json.dumps(experiment(),sort_keys=True,indent=2))
