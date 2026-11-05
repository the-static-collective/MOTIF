"""MOTIF-013 — The Probabilistic Witness.

A bounded *plug-in Bayesian* ensemble over four explicit 009 decision-tree
hypotheses and an OTHER catch-all. Independent adjudication estimates source
reliability and actuator compliance with Beta posteriors. Model evidence
marginalizes the unobserved true outcome, de-duplicates forwarded testimony,
and never silently converts an unverified command into an applied action.

It is NOT a full hierarchical Bayesian posterior: source reliabilities are
plug-in posterior means, evidence likelihoods assume independent upstream
origins conditional on truth, response probabilities .15/.85 are prescribed,
and the UNKNOWN catch-all is a simple .5 likelihood, not a discovered theory.

No import of hidden oracle, access to withheld truths or real-world authority.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from itertools import product
from math import exp,log,log2
from pathlib import Path
from random import Random
import json
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"008"))
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"009"))

from cartridge import Cartridge,checksum,export_cartridge,validate_cartridge
from learner import balanced_accuracy

KNOWN=("FIRST","SECOND","AND","OR")
ALL=KNOWN+("OTHER",)
PROGRAMS={
    "FIRST":(False,False,True,True),
    "SECOND":(False,True,False,True),
    "AND":(False,False,False,True),
    "OR":(False,True,True,True),
}
PAIRS=tuple(product((False,True),repeat=2))
SOURCE_PRIOR=(2,2)
COMPLIANCE_PRIOR=(2,2)
DEFAULT_OTHER=.15


class HOLD(ValueError):
    pass


@dataclass(frozen=True)
class Fit:
    posterior: tuple[tuple[str,float],...]
    reliabilities: tuple[tuple[str,int,int],...]
    compliance: tuple[tuple[int,int,int],...]
    admissible_records: int
    unverifiable_actuation: int
    missing_witnesses: int
    witness_claims: int
    independent_origins: int
    duplicate_forwarded_claims: int
    source_calibration_samples: int
    applied_calibration_samples: int
    log_joint: tuple[tuple[str,float],...]

    def masses(self):
        return dict(self.posterior)

    def origins(self):
        return {name: a/(a+b) for name,a,b in self.reliabilities}

    def compliance_means(self):
        return {slot:a/(a+b) for slot,a,b in self.compliance}


def _validate_calibration(calibration):
    if getattr(calibration,"provenance",None)!="INDEPENDENT_SYNTHETIC_CALIBRATION":
        raise HOLD("Missing independent synthetic source/actuator calibration")
    origins={}
    for source,correct,total in calibration.source_accuracy_counts:
        if (not isinstance(source,str) or not source or source in origins
                or type(correct) is not int or type(total) is not int
                or total<8 or not 0<=correct<=total):
            raise HOLD("Malformed or sparse source adjudication")
        origins[source]=(SOURCE_PRIOR[0]+correct,
                         SOURCE_PRIOR[1]+total-correct)
    controls={}
    for index,complied,total in calibration.actuator_compliance_counts:
        if (type(index) is not int or index not in (0,1) or index in controls
                or type(complied) is not int or type(total) is not int
                or total<8 or not 0<=complied<=total):
            raise HOLD("Malformed or sparse verified intervention history")
        controls[index]=(COMPLIANCE_PRIOR[0]+complied,
                         COMPLIANCE_PRIOR[1]+total-complied)
    if len(origins)<2 or set(controls)!={0,1}:
        raise HOLD("Missing independent source or actuator calibration")
    return origins,controls


def _independent_claims(trial,known_sources):
    if getattr(trial,"provenance",None)!="SYNTHETIC_UNADJUDICATED":
        raise HOLD("Only local synthetic unadjudicated records allowed")
    if not isinstance(trial.before,frozenset) or len(trial.roles)!=2:
        raise HOLD("Malformed graph evidence")
    a,t=trial.roles
    if not {("role_actor",a),("role_target",t),("pending",t)}.issubset(
            trial.before):
        raise HOLD("Missing observed graph role/initial-state facts")
    commanded=trial.commanded
    if (not isinstance(commanded,tuple) or len(commanded)!=2 or
            any(type(x) is not bool for x in commanded)):
        raise HOLD("Invalid requested intervention")
    realized=trial.audited_applied
    if realized is not None and (not isinstance(realized,tuple)
            or len(realized)!=2 or any(type(x) is not bool for x in realized)):
        raise HOLD("Unverified/invalid applied intervention")
    claims={}
    duplicate=0
    for source in trial.witnesses:
        if (source.provenance!="SYNTHETIC_WITNESS"
                or source.origin not in known_sources
                or type(source.claim) is not bool):
            raise HOLD("Uncalibrated or unverified witness source")
        if source.origin in claims:
            if claims[source.origin]!=source.claim:
                raise HOLD("Contradictory reports from same upstream origin")
            duplicate+=1
        else:
            claims[source.origin]=source.claim
    return tuple(sorted(claims.items())),duplicate


def outcome_probability(program,actual):
    if program=="OTHER":
        return .5
    return .15+.70*int(PROGRAMS[program][2*int(actual[0])+int(actual[1])])


def _witness_likelihood(claims,reliabilities,truth):
    likelihood=1.0
    for origin,observed in claims:
        r=reliabilities[origin]
        likelihood*=r if observed==truth else 1-r
    return likelihood


def _mixture_likelihood(claims,reliabilities,q):
    if not claims:
        return 1.0
    return (q*_witness_likelihood(claims,reliabilities,True)
            +(1-q)*_witness_likelihood(claims,reliabilities,False))


def _normalize(logs):
    pivot=max(logs.values())
    weights={name:exp(value-pivot) for name,value in logs.items()}
    total=sum(weights.values())
    return {name:weights[name]/total for name in ALL}


def fit(calibration,observations) -> Fit:
    source_beta,control_beta=_validate_calibration(calibration)
    reliability={k:a/(a+b) for k,(a,b) in source_beta.items()}
    prior={m:(1-DEFAULT_OTHER)/len(KNOWN) for m in KNOWN}
    prior["OTHER"]=DEFAULT_OTHER
    logs={m:log(prior[m]) for m in ALL}
    used=missing_receipt=missing_reports=reports=origins_seen=duplicates=0
    for case in observations:
        claims,extra=_independent_claims(case,reliability)
        reports+=len(case.witnesses)
        origins_seen+=len(claims)
        duplicates+=extra
        if case.audited_applied is None:
            missing_receipt+=1
            # Deliberately conservative: no verified realized controls means
            # no attribution of the outcome to any *specific* applied setting.
            continue
        if not claims:
            missing_reports+=1
            continue
        applied=case.audited_applied
        used+=1
        for model in ALL:
            likelihood=_mixture_likelihood(
                claims,reliability,outcome_probability(model,applied))
            logs[model]+=log(max(likelihood,1e-300))
    post=_normalize(logs)
    return Fit(tuple((name,post[name]) for name in ALL),
               tuple((s,*source_beta[s]) for s in sorted(source_beta)),
               tuple((i,*control_beta[i]) for i in (0,1)),
               used,missing_receipt,missing_reports,reports,origins_seen,
               duplicates,
               sum(x[2] for x in calibration.source_accuracy_counts),
               sum(x[2] for x in calibration.actuator_compliance_counts),
               tuple((m,logs[m]) for m in ALL))


def plan_likelihoods(fit_state,command):
    if (not isinstance(command,tuple) or len(command)!=2 or
            any(type(x) is not bool for x in command)):
        raise HOLD("Two explicit Boolean command settings required")
    compliance=fit_state.compliance_means()
    estimates={}
    for model in ALL:
        value=0.0
        for actual in PAIRS:
            w=1.0
            for i in (0,1):
                w*=compliance[i] if actual[i]==command[i] else 1-compliance[i]
            value+=w*outcome_probability(model,actual)
        estimates[model]=value
    return estimates


def predict(fit_state,command):
    prior=fit_state.masses()
    likelihoods=plan_likelihoods(fit_state,command)
    p=sum(prior[m]*likelihoods[m] for m in ALL)
    return min(max(p,1e-9),1-1e-9)


def event_predictive_log_ratio(fit_state,validation):
    """Evidence-only distribution-shift flag from an untouched validation set.

    Compare frozen training posterior likelihood to OTHER, without adjusting
    model weights. Negative log ratio can indicate shift or misspecification;
    it CANNOT identify whether witness error, hidden cause or drift produced it.
    """
    reliabilities=fit_state.origins()
    masses=fit_state.masses()
    ratio=0.0
    verified=0
    for item in validation:
        claims,_=_independent_claims(item,reliabilities)
        if item.audited_applied is None or not claims:
            continue
        with_model=sum(masses[name]*_mixture_likelihood(
            claims,reliabilities,outcome_probability(name,item.audited_applied))
            for name in ALL)
        with_unknown=_mixture_likelihood(claims,reliabilities,.5)
        ratio+=log(max(with_model,1e-300)/max(with_unknown,1e-300))
        verified+=1
    return {"log_bayes_factor_against_half":round(ratio,5),
            "validation_independent_records":verified,
            "shift_warning":verified>=12 and ratio < -6.0}


def decision(fit_state,command,validation_flag=False):
    probability=predict(fit_state,command)
    masses=fit_state.masses()
    named=max(masses[m] for m in KNOWN)
    if validation_flag:
        status="HOLD_PREDICTIVE_SHIFT"
    elif masses["OTHER"]>=.40:
        status="HOLD_OUTSIDE_MODEL_FAMILY"
    elif named<.70:
        status="HOLD_MODEL_UNCERTAINTY"
    else:
        status="PREDICT_PROBABILITY_ONLY"
    return {"status":status,"probability":round(probability,6),
            "top_named_weight":round(named,6),
            "other_weight":round(masses["OTHER"],6),
            "admitted_for_real_action":False}


def confidence_intervals(fit_state,command,seed=0,draws=500):
    """Posterior over four/five model templates + uncertain compliance only.

    Source reliability uncertainty is NOT resampled; this is NOT a complete
    Bayesian credible interval or a guaranteed frequentist coverage bound.
    """
    if type(draws) is not int or not 64<=draws<=5000:
        raise ValueError("Bounded Monte Carlo sampling required")
    rng=Random(seed)
    posterior=fit_state.masses()
    weights=list(posterior.values())
    models=list(posterior)
    beta={i:(a,b) for i,a,b in fit_state.compliance}
    vals=[]
    for _ in range(draws):
        key=rng.choices(models,weights=weights,k=1)[0]
        compliance={i:rng.betavariate(*beta[i]) for i in (0,1)}
        total=0.0
        for actual in PAIRS:
            w=1.0
            for i in (0,1):
                w*=compliance[i] if command[i]==actual[i] else (
                    1-compliance[i])
            total+=w*outcome_probability(key,actual)
        vals.append(total)
    vals.sort()
    return (round(vals[int(.05*draws)],5),
            round(vals[int(.95*draws)],5))


def source_reliability_intervals(fit_state,seed=0,draws=1000):
    """90% Monte Carlo intervals from independently adjudicated Beta
    source-reliability calibration posteriors. This estimates each witness
    channel's report correctness, not truth probability or source identity.
    """
    if type(draws) is not int or not 100<=draws<=10000:
        raise ValueError("Bounded source calibration interval sampling")
    rng=Random(seed)
    output={}
    for name,a,b in fit_state.reliabilities:
        sample=sorted(rng.betavariate(a,b) for _ in range(draws))
        output[name]={
            "posterior_mean":round(a/(a+b),5),
            "interval_90":(round(sample[int(.05*draws)],5),
                           round(sample[int(.95*draws)],5)),
            "adjudicated_evidence":a+b-sum(SOURCE_PRIOR),
            "real_world_source_identity_verified":False
        }
    return output


def _source_likelihood_for_pattern(pattern,reliabilities,q):
    return _mixture_likelihood(
        tuple(zip(sorted(reliabilities),pattern)),reliabilities,q)


def proposal_information_gain(fit_state,command):
    """Classical posterior mutual information under a hypothetical full
    set of unique sources reporting, before dropout. No real-world authority.
    """
    masses=fit_state.masses()
    qs=plan_likelihoods(fit_state,command)
    reliability=fit_state.origins()
    total_info=0.0
    for bits in product((False,True),repeat=len(reliability)):
        evidence={m:_source_likelihood_for_pattern(bits,reliability,qs[m])
                  for m in ALL}
        p_observed=sum(masses[m]*evidence[m] for m in ALL)
        if p_observed==0:
            continue
        posterior={m:masses[m]*evidence[m]/p_observed for m in ALL}
        divergence=sum(posterior[m]*log2(posterior[m]/masses[m])
                       for m in ALL if posterior[m]>0)
        total_info+=p_observed*divergence
    return max(0.0,total_info)


def choose_question(fit_state,*,allowed=PAIRS,costs=None,budget=2):
    if type(budget) is not int or budget<0:
        raise ValueError("Invalid local cost budget")
    if costs is None:
        costs={x:1 for x in PAIRS}
    if (set(costs)!=set(PAIRS) or any(
         type(costs[x]) is not int or costs[x]<=0 for x in PAIRS)
            or not set(allowed).issubset(PAIRS)):
        raise HOLD("Unreviewed scope or nonpositive synthetic cost")
    candidate=[]
    informative=[]
    for command in PAIRS:
        info=proposal_information_gain(fit_state,command)
        if info<1e-7:
            continue
        informative.append(command)
        if command in allowed and costs[command]<=budget:
            candidate.append((info/costs[command],info,command))
    if not informative:
        status="HOLD_NO_INFORMATION"
        winner=None
    elif not candidate:
        status=("HOLD_BUDGET" if set(informative)&set(allowed)
                else "HOLD_UNSAFE")
        winner=None
    else:
        winner=max(candidate,key=lambda x:(x[0],x[1],
                                           tuple(not k for k in x[2])))
        status="PROPOSE_SYNTHETIC_ONLY"
    return {
        "status":status,
        "command":list(winner[2]) if winner else None,
        "information_bits_if_all_origins_report":
            round(winner[1],6) if winner else 0.0,
        "cost":costs[winner[2]] if winner else 0,
        "world_actuated":False,"human_authority_verified":False}


def tree_cartridges(fit_state,records,control_predicates):
    """Pack four *hypothesized* 009 trees with witnessed, NON-adjudicated
    reporter counts. Counts are NOT verified ground-truth outcomes.
    The fifth OTHER model has no deterministic tree; its posterior is retained
    explicitly and is never quietly converted into a fake tree.
    """
    if len(control_predicates)!=2 or control_predicates[0]==control_predicates[1]:
        raise HOLD("Two distinct opaque port predicates required")
    cards=[]
    source=[]
    for case in records:
        claims,_=_independent_claims(case,fit_state.origins())
        if case.audited_applied is not None and claims:
            source.append((case.audited_applied,claims))
    if len(source)<4:
        raise HOLD("Insufficient observed witness reports for cartridges")
    # Pick a single, explicitly named origin per record; other sources remain
    # part of posterior inference but not duplicated as independent labels.
    count=[[0,0] for _ in PAIRS]
    for applied,claims in source:
        value=claims[0][1]
        count[2*int(applied[0])+int(applied[1])][int(value)]+=1
    if min(sum(pair) for pair in count)==0:
        raise HOLD("Not all four input configurations were observed")
    n=sum(sum(row) for row in count)
    trace=checksum({"witness_counts":count,
                    "calibration_source":"SYNTHETIC_UNADJUDICATED_WITNESS_REPORTS",
                    "opaque_ports":list(control_predicates)})
    vocab=tuple(sorted(("role_actor","role_target","pending",
                        *control_predicates)))
    first=((control_predicates[0],"?0"),)
    second=((control_predicates[1],"?1"),)
    for name in KNOWN:
        leaves=PROGRAMS[name]
        truth=[]
        guess=[]
        for i,pair in enumerate(count):
            truth += [False]*pair[0]+[True]*pair[1]
            guess += [leaves[i]]*sum(pair)
        fit_score=round(balanced_accuracy(tuple(truth),tuple(guess)),6) if (
            any(truth) and not all(truth)) else .5
        body={"schema":"motif.decision-tree-cartridge.v0",
              "vocab":list(vocab),
              "first":[list(f) for f in first],
              "second":[list(f) for f in second],
              "leaves":list(leaves),"counts":[list(x) for x in count],
              "fit_balanced":fit_score,"evidence_count":n,
              "source_digest":trace,"status":"PROPOSAL_ONLY"}
        identity="tree-"+checksum(body)[:16]
        car=Cartridge(identity,body["schema"],vocab,first,second,leaves,
                      tuple(tuple(x) for x in count),fit_score,n,trace)
        raw=export_cartridge(car)
        if validate_cartridge(raw)!=car:
            raise HOLD("Invalid nested tree cartridge")
        cards.append({"model":name,"posterior_weight":round(
            fit_state.masses()[name],8),"tree":json.loads(raw)})
    package={
        "schema":"motif.probabilistic-tree-ensemble.v0",
        "status":"HOLD_PROPOSAL_ONLY",
        "components":cards,
        "unmodeled_mass":round(fit_state.masses()["OTHER"],8),
        "source_counts_are_unadjudicated_witness_claims":True,
        "real_world_authority":False,
    }
    return dict(package,checksum_sha256=checksum(package))
