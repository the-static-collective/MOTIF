"""MOTIF-014 — The Witness of Witnesses.

EXACT FINITE-GRID JOINT BAYESIAN ENUMERATION (within a declared grid):
    p(H, r0, r1, q_auditor, c_actuator | calibration, interventions)

Crucially, no adjudicator is assumed to know ground truth. Synthetic
calibration cases have a *latent* event truth; both witnesses and the auditor
report it with unknown reliability. Intervention outcomes and applied controls
are also latent. We marginalize each possibility, not plug in point estimates.

This is a traditional classical Bayesian latent-variable model. Its finite
grid, independent-source assumptions, mechanism grammar, fixed success
probabilities and audit/actuator priors are strong design choices. An
unidentifiable reliability orientation is resolved by a PRIOR favoring an
above-chance auditor, not by discovering absolute truth from agreement.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from itertools import product
from math import exp,log
from pathlib import Path
import sys
import json

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"008"))
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"009"))
from cartridge import Cartridge,checksum,export_cartridge,validate_cartridge
from learner import balanced_accuracy

# FIXED, inspectable finite parameter grid. No fictitious continuous posterior.
R_GRID=(.20,.45,.70,.90)
Q_GRID=(.58,.72,.84,.95)
C_GRID=(.55,.76,.92)
R0_PRIOR=(.12,.15,.28,.45)   # imperfect prior orientation for upstream 0
R1_PRIOR=(.25,.25,.25,.25)
Q_PRIOR=(.10,.30,.40,.20)   # identifiability anchor: presumed >50% auditor
C_PRIOR=(.20,.50,.30)
PRIMARY=("FIRST","SECOND","AND","OR")
OTHER="OTHER"
PROGS={"FIRST":(False,False,True,True),
       "SECOND":(False,True,False,True),
       "AND":(False,False,False,True),
       "OR":(False,True,True,True)}
PAIRS=tuple(product((False,True),repeat=2))
MODEL_PRIOR_OTHER=.15
SOURCES=("s0","s1")
MAX_RECORDS=2000


class HOLD(ValueError):
    pass


@dataclass(frozen=True)
class State:
    hypothesis: str
    r0: float
    r1: float
    q: float
    c: float
    log_prior: float


@dataclass(frozen=True)
class Posterior:
    states: tuple[State,...]
    weights: tuple[float,...]
    grammar: str
    calibration_count: int
    intervention_count: int
    forwarded_duplicates: int
    missing_audit_receipts: int
    missing_reporters: int
    model_type: str="CLASSICAL_EXACT_FINITE_GRID_JOINT_BAYES"

    def model_weights(self):
        result={}
        for state,w in zip(self.states,self.weights):
            result[state.hypothesis]=result.get(state.hypothesis,0)+w
        return dict(sorted(result.items()))

    def parameter_means(self):
        return {name:sum(getattr(s,name)*w for s,w in zip(self.states,self.weights))
                for name in ("r0","r1","q","c")}

    def parameter_interval(self,name,alpha=.10):
        if name not in ("r0","r1","q","c"):
            raise HOLD("Unrecognized credibility parameter")
        groups={}
        for s,w in zip(self.states,self.weights):
            v=getattr(s,name)
            groups[v]=groups.get(v,0)+w
        def quantile(t):
            cdf=0
            for value,weight in sorted(groups.items()):
                cdf+=weight
                if cdf+1e-12>=t:
                    return value
            return max(groups)
        return (quantile(alpha/2),quantile(1-alpha/2))

    def forecast(self,request):
        if request not in PAIRS:
            raise HOLD("Unregistered synthetic action")
        return sum(w*command_success(s,request)
                   for s,w in zip(self.states,self.weights))

    def predictive_interval(self,request,alpha=.10):
        # Interval is over uncertain *success-probability parameter*,
        # NOT a coverage guarantee for individual Bernoulli outcomes.
        values=sorted((command_success(s,request),w)
                      for s,w in zip(self.states,self.weights))
        def quantile(t):
            total=0.0
            for value,w in values:
                total+=w
                if total+1e-12>=t:
                    return value
            return values[-1][0]
        return (quantile(alpha/2),quantile(1-alpha/2))


def _grammar(name):
    if name=="motif":
        return dict(PROGS,OTHER=None)
    if name=="all_boolean":
        options={f"BOOL_{i:04b}":tuple(
            bool((i >> (3-j))&1) for j in range(4)) for i in range(16)}
        options[OTHER]=None
        return options
    raise HOLD("Unknown proposed hypothesis grammar")


def _prior_hypotheses(grammar):
    rules=_grammar(grammar)
    return {h:(MODEL_PRIOR_OTHER if h==OTHER else
               (1-MODEL_PRIOR_OTHER)/(len(rules)-1)) for h in rules}


def _states(grammar):
    models=_prior_hypotheses(grammar)
    for h,p_h in models.items():
        for (i,r0),(j,r1),(k,q),(m,c) in product(
            enumerate(R_GRID),enumerate(R_GRID),
            enumerate(Q_GRID),enumerate(C_GRID)):
            prior=(p_h*R0_PRIOR[i]*R1_PRIOR[j]*
                   Q_PRIOR[k]*C_PRIOR[m])
            yield State(h,r0,r1,q,c,log(prior))


def outcome_probability(hypothesis,applied):
    template=_grammar("motif").get(hypothesis)
    if template is None and hypothesis!=OTHER:
        template=_grammar("all_boolean").get(hypothesis)
    if hypothesis!=OTHER and template is None:
        raise HOLD("Unsupported hypothesis")
    if hypothesis==OTHER:
        return .5
    return .12+.76*int(template[2*int(applied[0])+int(applied[1])])


def command_success(state,request):
    if request not in PAIRS:
        raise HOLD("Unknown requested controls")
    first=state.c*outcome_probability(state.hypothesis,request)
    failed=(1-state.c)*outcome_probability(
        state.hypothesis,(not request[0],request[1]))
    return first+failed


def _credibility(claim,truth,correctness):
    return correctness if claim==truth else 1-correctness


def _checked_reporters(observations):
    claims={}
    duplicates=0
    if not isinstance(observations,tuple):
        raise HOLD("Reporter evidence must be immutable")
    for item in observations:
        if (getattr(item,"provenance",None)!="SYNTHETIC_UNVERIFIED_WITNESS"
                or item.origin not in SOURCES or
                type(item.says_success) is not bool or
                not isinstance(item.reporter,str)):
            raise HOLD("Unverified reporter source or claim")
        if item.origin in claims:
            if claims[item.origin]!=item.says_success:
                raise HOLD("Conflicting testimony with same upstream source")
            duplicates+=1
        else:
            claims[item.origin]=item.says_success
    return (claims.get("s0"),claims.get("s1")),duplicates


def _checked_calibrations(records):
    prepared=[]
    duplicates=missing=0
    for row in records:
        if getattr(row,"provenance",None)!="SYNTHETIC_UNADJUDICATED_CALIBRATION":
            raise HOLD("No authenticated adjudication; synthetic data only")
        sources,extra=_checked_reporters(row.reporters)
        duplicates+=extra
        audit=row.audit_says_success
        if audit is not None and type(audit) is not bool:
            raise HOLD("Invalid fallible auditor claim")
        if audit is None:
            missing+=1
        prepared.append((sources[0],sources[1],audit))
    return Counter(prepared),duplicates,missing


def _checked_trials(records,predicates):
    if (not isinstance(predicates,tuple) or len(predicates)!=2 or
            any(not isinstance(v,str) or not v for v in predicates) or
            predicates[0]==predicates[1]):
        raise HOLD("Need distinct source-declared control predicates")
    prepared=[]
    duplicates=missing_audit=missing_sources=0
    for row in records:
        if getattr(row,"provenance",None)!="SYNTHETIC_UNADJUDICATED_INTERVENTION":
            raise HOLD("Only explicit synthetic interventions admitted")
        if row.requested not in PAIRS or not isinstance(row.before,frozenset):
            raise HOLD("Invalid command or graph snapshot")
        actor,target=row.roles
        expected={("role_actor",actor),("role_target",target),
                  ("pending",target)}
        if row.requested[0]:
            expected.add((predicates[0],actor))
        if row.requested[1]:
            expected.add((predicates[1],target))
        if row.before!=frozenset(expected):
            raise HOLD("Command graph does not match claimed requested settings")
        sources,extra=_checked_reporters(row.reporters)
        duplicates+=extra
        audit=row.audit_says_first_port_applied
        if audit is not None and type(audit) is not bool:
            raise HOLD("Malformed actuator witness claim")
        if audit is None:
            missing_audit+=1
        if sources==(None,None):
            missing_sources+=1
        prepared.append((row.requested,sources[0],sources[1],audit))
    return Counter(prepared),duplicates,missing_audit,missing_sources


def _witness_probability(first,second,r0,r1,truth):
    total=1.0
    if first is not None:
        total*=_credibility(first,truth,r0)
    if second is not None:
        total*=_credibility(second,truth,r1)
    return total


def calibration_likelihood(pattern,state):
    first,second,audit=pattern
    # Hidden calibration truth is independently Bernoulli(.5);
    # even the adjudicator's reported "ground truth" can be wrong.
    return sum(.5*_witness_probability(
        first,second,state.r0,state.r1,truth)*(
        _credibility(audit,truth,state.q) if audit is not None else 1.0)
        for truth in (False,True))


def intervention_likelihood(pattern,state):
    requested,first,second,audit=pattern
    likelihood=0.0
    for actual_first in (False,True):
        applied=(actual_first,requested[1])
        p_applied=(state.c if actual_first==requested[0]
                   else 1-state.c)
        p_audit=(_credibility(audit,actual_first,state.q)
                 if audit is not None else 1.0)
        prob_success=outcome_probability(state.hypothesis,applied)
        reports=(prob_success*_witness_probability(
            first,second,state.r0,state.r1,True)
            +(1-prob_success)*_witness_probability(
                first,second,state.r0,state.r1,False))
        likelihood+=p_applied*p_audit*reports
    return likelihood


def fit(calibration,interventions,predicates,grammar="motif")->Posterior:
    records_c=tuple(calibration)
    records_t=tuple(interventions)
    if not 8<=len(records_c)<=MAX_RECORDS or not 8<=len(records_t)<=MAX_RECORDS:
        raise HOLD("Both calibration and intervention evidence required")
    calib,dupes1,_=_checked_calibrations(records_c)
    trials,dupes2,missing_a,missing_s=_checked_trials(records_t,predicates)
    states=tuple(_states(grammar))
    logs=[]
    # Grouping by witnessed pattern avoids recalculating repeated likelihoods.
    for state in states:
        score=state.log_prior
        for pattern,count in calib.items():
            score+=count*log(max(calibration_likelihood(pattern,state),1e-300))
        for pattern,count in trials.items():
            score+=count*log(max(intervention_likelihood(pattern,state),1e-300))
        logs.append(score)
    pivot=max(logs)
    weights=[exp(x-pivot) for x in logs]
    normalizer=sum(weights)
    weights=tuple(x/normalizer for x in weights)
    return Posterior(states,weights,grammar,len(records_c),len(records_t),
                     dupes1+dupes2,missing_a,missing_s)


def validation_diagnostic(posterior,validation,predicates):
    """Frozen-posterior predictive evidence vs explicitly ignorant .5 claims.

    Pure development heuristic; cannot reliably detect every shift.
    Posterior IS NOT updated on validation or test labels.
    """
    patterns,_,_,_=_checked_trials(tuple(validation),predicates)
    score=0.0
    observed=0
    for pattern,count in patterns.items():
        # same model must jointly explain both noisy outcomes and noisy audit
        likelihood=sum(w*intervention_likelihood(pattern,s)
                       for s,w in zip(posterior.states,posterior.weights))
        # ignorant observation model: each nonmissing binary claim .5;
        # source reports and auditor are not treated as observed truth.
        _,a,b,q=pattern
        seen=sum(x is not None for x in (a,b,q))
        baseline=.5**seen
        score+=count*log(max(likelihood,1e-300)/baseline)
        observed+=count
    return {"records":observed,"log_evidence_ratio_vs_ignorance":round(score,5),
            "warning":observed>=12 and score < -4.5,
            "threshold_is_heuristic_not_calibrated":True}


def decide(posterior,command,shift_warning=False):
    weights=posterior.model_weights()
    strongest=max(v for k,v in weights.items() if k!=OTHER)
    if shift_warning:
        status="HOLD_RELIABILITY_OR_MECHANISM_SHIFT"
    elif weights[OTHER]>=.4:
        status="HOLD_OUTSIDE_GRAMMAR"
    elif strongest<.7:
        status="HOLD_MODEL_UNCERTAIN"
    else:
        status="PREDICT_PROBABILITY_ONLY"
    return {"status":status,
            "forecast_success":round(posterior.forecast(command),6),
            "interval_90_epistemic_probability":[round(x,5) for x in
                posterior.predictive_interval(command)],
            "model_peak":round(strongest,6),
            "unmodeled_posterior_mass":round(weights[OTHER],6),
            "verified_real_world_authority":False}


def propose_inquiry(posterior,*,allowed=("CALIBRATION","INTERVENTION"),
                    costs=None,budget=2):
    """Choose synthetic experiment *type* on expected FULL JOINT state info.

    Assumes A, B and audit all report (no dropout) in hypothetical next
    observation; actual simulator may disagree. This is classical Bayesian
    experimental design, never a dispatch/execution or ethical authorization.
    """
    if type(budget) is not int or budget<0:
        raise HOLD("Unrecognized local synthetic inquiry budget")
    choices=[("CALIBRATION",None)]+[("INTERVENTION",x) for x in PAIRS]
    if costs is None:
        costs={"CALIBRATION":1,"INTERVENTION":2}
    if (set(costs)!={"CALIBRATION","INTERVENTION"}
            or any(type(x) is not int or x<1 for x in costs.values())
            or not set(allowed).issubset(costs)):
        raise HOLD("Missing or invalid synthetic policy")
    possibilities=[]
    informative=[]
    # 8 claim patterns: origin0, origin1, auditor.
    for action,setting in choices:
        table=[]
        for bits in product((False,True),repeat=3):
            pattern=((bits[0],bits[1],bits[2]) if action=="CALIBRATION"
                     else (setting,bits[0],bits[1],bits[2]))
            likelihoods=[
                (calibration_likelihood(pattern,s) if action=="CALIBRATION"
                 else intervention_likelihood(pattern,s))
                for s in posterior.states]
            predicted=sum(w*x for w,x in zip(posterior.weights,likelihoods))
            table.append((predicted,likelihoods))
        info=0.0
        for predictive,likelihoods in table:
            if predictive<=0:
                continue
            info+=sum(w*p*log(p/predictive,2) for w,p in
                      zip(posterior.weights,likelihoods) if p>0)
        if info <= 1e-8:
            continue
        informative.append((action,setting))
        if action in allowed and costs[action]<=budget:
            possibilities.append((info/costs[action],info,action,setting))
    if not informative:
        return {"status":"HOLD_NO_INFORMATION","action":None,
                "settings":None,"expected_joint_information_bits":0,
                "real_world_authority":False}
    if not possibilities:
        status=("HOLD_BUDGET" if any(a in allowed for a,_ in informative)
                else "HOLD_UNSAFE")
        return {"status":status,"action":None,"settings":None,
                "expected_joint_information_bits":0,
                "real_world_authority":False}
    winner=max(possibilities,key=lambda row:(row[0],row[1],row[2],
                                            str(row[3])))
    return {"status":"PROPOSE_SYNTHETIC_ONLY","action":winner[2],
            "settings":list(winner[3]) if winner[3] is not None else None,
            "expected_joint_information_bits":round(winner[1],6),
            "cost":costs[winner[2]],"assumes_all_three_channels_report":True,
            "real_world_authority":False}


def cartridge_ensemble(posterior,public_trials,predicates):
    """Four ACTUAL 009 trees with source-claim (not truth) evidence counts.

    Joint parameter uncertainty and additional other/expanded-model mass
    live in the surrounding bundle. Tree leaf counts are unverified reports,
    not magically adjudicated events or calibrated tree probabilities.
    """
    trials=tuple(public_trials)
    checked,_,_,_=_checked_trials(trials,predicates)
    counts=[[0,0] for _ in PAIRS]
    for (request,a,b,audit),count in checked.items():
        # Only first source's claim, if present; no treatment as ground truth.
        if a is not None:
            counts[2*int(request[0])+int(request[1])][int(a)]+=count
    if min(map(sum,counts))<1:
        raise HOLD("Unobserved command pattern")
    n=sum(map(sum,counts))
    vocab=tuple(sorted(("role_actor","role_target","pending",*predicates)))
    first=((predicates[0],"?0"),)
    second=((predicates[1],"?1"),)
    digest=checksum({"source_report_counts":counts,
                     "not_adjudicated":True,
                     "requested_controls_not_applied_controls":True})
    mixture=posterior.model_weights()
    components=[]
    for name,bits in PROGS.items():
        actual=[];predicted=[]
        for i,(neg,pos) in enumerate(counts):
            actual.extend([False]*neg+[True]*pos)
            predicted.extend([bits[i]]*(neg+pos))
        fit_score=(round(balanced_accuracy(tuple(actual),tuple(predicted)),6)
                   if 0<sum(actual)<len(actual) else .5)
        body={"schema":"motif.decision-tree-cartridge.v0","vocab":list(vocab),
              "first":[list(x) for x in first],
              "second":[list(x) for x in second],
              "leaves":list(bits),"counts":[list(x) for x in counts],
              "fit_balanced":fit_score,"evidence_count":n,
              "source_digest":digest,"status":"PROPOSAL_ONLY"}
        ident="tree-"+checksum(body)[:16]
        card=Cartridge(ident,body["schema"],vocab,first,second,bits,
                       tuple(tuple(row) for row in counts),
                       fit_score,n,digest)
        raw=export_cartridge(card)
        if validate_cartridge(raw)!=card:
            raise HOLD("Invalid decision-tree component")
        components.append({"hypothesis":name,
                           "joint_marginal_weight":round(mixture[name],8),
                           "tree":json.loads(raw)})
    output={
        "schema":"motif.joint-witness-tree-ensemble.v0",
        "status":"HOLD_PROPOSAL_ONLY",
        "components":components,
        "other_mass":round(mixture[OTHER],8),
        "uncertainty_model":"EXACT_DISCRETE_JOINT_PARAMETER_AND_MODEL_POSTERIOR",
        "confidence_values_are_prior_and_synthetic_evidence_dependent":True,
        "counts_are_unadjudicated_upstream_witness_claims":True,
        "source_and_auditor_identities_are_not_authenticated":True,
        "real_world_authority":False,
    }
    return dict(output,checksum_sha256=checksum(output))
