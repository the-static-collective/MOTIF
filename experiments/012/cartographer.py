"""MOTIF-012 — The Causal Cartographer.

A deliberately limited intervention experiment built on MOTIF-009 tree
cartridges and MOTIF-011 ambiguity/abstention.

Natural observations make two candidate relations perfectly correlated.
The scientist discovers those *unnamed graph predicates*, constructs FOUR
observationally equivalent 009 tree-cartridge hypotheses, and proposes
synthetic interventions which break the correlation. An independent evaluator
runs the interventions, and a separate local-review suite can still REFUSE
a provisionally identified mechanism if hidden causes or noise falsify it.

This file imports NO oracle. The baseline XOR of two known input ports is a
DECLARED prior, not autonomously inferred; candidate mechanism grammar is
handcrafted; no physical causal inference, real permission or execution.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "008"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "009"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "010"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "011"))

from cartridge import Cartridge, checksum, export_cartridge, validate_cartridge
from scientist import validated_result, controls_present, entropy
from skeptic import assess, features_to_investigate, feature_present

PAIRS=tuple(product((False,True),repeat=2))
PROGRAMS={
    "FIRST":(False,False,True,True),
    "SECOND":(False,True,False,True),
    "JOINT":(False,False,False,True),
    "EITHER":(False,True,True,True),
}
SAFE_RESULTS=("PROPOSE_SYNTHETIC_ONLY","HOLD_UNSAFE","HOLD_BUDGET",
              "HOLD_NO_INFORMATION")


class HOLD(ValueError):
    """Missing, incompatible, insufficient or forbidden synthetic evidence."""


@dataclass(frozen=True)
class Relation:
    name: str
    role_index: int


@dataclass(frozen=True)
class CausalModel:
    label: str  # a hypothesis program, NEVER a verified source family name
    tree: Cartridge
    first: Relation
    second: Relation
    known_vocabulary: tuple[str,...]

    def residual(self, c: bool, p: bool) -> bool:
        if type(c) is not bool or type(p) is not bool:
            raise ValueError("Explicit Boolean settings required")
        row=frozenset((
            ((self.first.name, "?"+str(self.first.role_index)),)
            if c else (),
            ((self.second.name, "?"+str(self.second.role_index)),)
            if p else ()
        )) - {()}
        return self.tree.predict(row)

    def predict(self, episode, original_controls) -> bool:
        if not source_compatible(episode,self.first,self.second,original_controls,
                                 self.known_vocabulary):
            raise HOLD("Unreviewed original or candidate predicate vocabulary")
        a,b=controls_present(episode,original_controls)
        c=feature_present(episode,self.first.name,self.first.role_index)
        p=feature_present(episode,self.second.name,self.second.role_index)
        # Base XOR(A,B) is an explicitly declared prior, not a discovered law.
        return (a != b) != self.residual(c,p)


@dataclass(frozen=True)
class Scar:
    setting: tuple[bool,bool]
    observed: bool
    predicted: tuple[bool,...]
    source: str
    reason: str


@dataclass(frozen=True)
class TrialState:
    models: tuple[CausalModel,...]
    scars: tuple[Scar,...]
    status: str


@dataclass(frozen=True)
class Proposal:
    status: str
    settings: tuple[bool,bool] | None
    expected_gain_bits: float
    cost: int
    predictions: tuple[bool,...]
    model_ids: tuple[str,...]
    reason: str
    real_world_authority: bool = False


@dataclass(frozen=True)
class Review:
    status: str
    proposed_model: str | None
    independently_checked: int
    contradictions: tuple[Scar,...]
    source: str = "INDEPENDENT_SYNTHETIC_LOCAL_REVIEW"
    real_world_authority: bool = False


def source_compatible(episode,first,second,original_controls,known_vocabulary):
    relations={original_controls.first_port,original_controls.second_port,
               first.name,second.name,"role_actor","role_target","pending"}
    actual={fact[0] for fact in episode.before}
    # Nuisance predicates unrelated to the two candidates may be present in
    # original observations. The candidate learner never depends on those.
    return ({"role_actor","role_target","pending"}.issubset(actual)
            and actual.issubset(known_vocabulary)
            and original_controls.first_port!=original_controls.second_port
            and first!=second
            and first.name != second.name)


def _residual(episode, controls):
    a,b=controls_present(episode,controls)
    return validated_result(episode) != (a!=b)


def _full_table(records,controls,relation):
    """Find a predictive relation without using its semantic name.

    A required 8-cell table includes original A/B and the candidate bit;
    observations with the same visible setting and different results REFUSE.
    """
    table={}
    for case in records:
        a,b=controls_present(case,controls)
        present=feature_present(case,relation.name,relation.role_index)
        slot=(a,b,present)
        value=validated_result(case)
        if slot in table and table[slot]!=value:
            return None
        table[slot]=value
    if len(table)!=8:
        return None
    return table


def discover_candidate_relations(train, validation, controls):
    training,local=tuple(train),tuple(validation)
    appraisal=assess(training,local,controls)
    if appraisal.status!="ABSTAIN_AMBIGUOUS":
        raise HOLD("Expected unresolved observational proxy ambiguity")
    matches=[]
    for name,role in features_to_investigate(training,controls):
        concept=Relation(name,role)
        table=_full_table(training,controls,concept)
        if table is None:
            continue
        if all(table.get((*controls_present(row,controls),
                          feature_present(row,name,role))) ==
               validated_result(row) for row in local):
            matches.append(concept)
    if len(matches)!=2:
        raise HOLD("Need exactly two independently supported visible proxy candidates")
    if matches[0].role_index==matches[1].role_index:
        # This narrow cartridge model requires one candidate per public role;
        # a broader grammar is a future experiment, not a guessed equivalence.
        raise HOLD("Candidate roles not representable in this bounded grammar")
    # Canonical role order; opaque names are still arbitrary and uninformative.
    return tuple(sorted(matches,key=lambda x:x.role_index))


def _candidate_tree(program, observed, controls, candidates):
    first,second=candidates
    first_motif=((first.name, "?"+str(first.role_index)),)
    second_motif=((second.name, "?"+str(second.role_index)),)
    bins=[[0,0] for _ in PAIRS]
    evidence=[]
    for row in observed:
        c=feature_present(row,first.name,first.role_index)
        p=feature_present(row,second.name,second.role_index)
        residual=_residual(row,controls)
        bins[2*int(c)+int(p)][int(residual)]+=1
        evidence.append([int(c),int(p),int(residual)])
        if program[2*int(c)+int(p)]!=residual:
            raise HOLD("Hypothesis conflicts with source observational evidence")
    counts=tuple(tuple(x) for x in bins)
    truth=tuple(_residual(x,controls) for x in observed)
    if not (any(truth) and not all(truth)):
        raise HOLD("Insufficient contrasting observational evidence")
    vocab=tuple(sorted({"role_actor","role_target","pending",first.name,second.name}))
    source_digest=checksum({"observed_role_relative_residuals":sorted(evidence),
                            "known_prior":"XOR_TWO_PUBLIC_INPUTS"})
    template={
        "schema":"motif.decision-tree-cartridge.v0",
        "vocab":list(vocab),
        "first":[list(f) for f in first_motif],
        "second":[list(f) for f in second_motif],
        "leaves":list(program),
        "counts":[list(x) for x in counts],
        "fit_balanced":1.0,
        "evidence_count":len(observed),
        "source_digest":source_digest,
        "status":"PROPOSAL_ONLY",
    }
    ident="tree-"+checksum(template)[:16]
    card=Cartridge(ident,template["schema"],vocab,first_motif,second_motif,
                   tuple(program),counts,1.0,len(observed),source_digest)
    if validate_cartridge(export_cartridge(card))!=card:
        raise AssertionError("Proposed 009 cartridge failed roundtrip")
    return card


def opening_model_space(train,validation,controls) -> TrialState:
    inputs=tuple(train)
    candidates=discover_candidate_relations(inputs,validation,controls)
    vocab=tuple(sorted({fact[0] for row in inputs for fact in row.before}))
    models=tuple(CausalModel(name,_candidate_tree(bits,inputs,controls,
                                                 candidates),*candidates,vocab)
                 for name,bits in PROGRAMS.items())
    return TrialState(models,(),"COMPETING_EXPLANATIONS")


def choose(state: TrialState, *, allowed=PAIRS, costs=None,
           remaining_budget=2, used=()) -> Proposal:
    """Maximize model disagreement per positive cost, after policy filtering.

    Uncertain model votes are exactly uniform-posterior version-space entropy.
    A held proposal is NEVER passed to a simulator by this module.
    """
    if type(remaining_budget) is not int or remaining_budget<0:
        raise ValueError("Invalid observation budget")
    if costs is None:
        costs={key:1 for key in PAIRS}
    if set(costs)!=set(PAIRS) or any(
        type(costs[x]) is not int or costs[x]<1 for x in PAIRS):
        raise ValueError("Every control setting requires positive integer cost")
    permitted=frozenset(allowed)
    if not permitted.issubset(PAIRS) or not frozenset(used).issubset(PAIRS):
        raise ValueError("Invalid local intervention scope")
    if not state.models or state.status=="OUTSIDE_GRAMMAR":
        return Proposal("HOLD_NO_MODEL",None,0,0,(),(),
                        "Current candidate grammar has been falsified")
    eligible=[]
    informative=[]
    for setting in PAIRS:
        if setting in used:
            continue
        votes=tuple(model.residual(*setting) for model in state.models)
        gain=entropy(sum(votes)/len(votes))
        if gain<=0:
            continue
        informative.append(setting)
        if setting in permitted and costs[setting]<=remaining_budget:
            eligible.append((gain/costs[setting],gain,-costs[setting],
                             setting,votes))
    common=tuple(x.tree.id for x in state.models)
    if not informative:
        return Proposal("HOLD_NO_INFORMATION",None,0,0,(),common,
                        "All remaining hypothetical programs agree")
    if not eligible:
        admissible=set(informative)&permitted
        status="HOLD_BUDGET" if admissible else "HOLD_UNSAFE"
        return Proposal(status,None,0,0,(),common,
                        "No informative experiment is within permitted cost/scope")
    score,gain,negcost,setting,votes=max(
        eligible,key=lambda x:(round(x[0],12),round(x[1],12),
                               x[2],tuple(not v for v in x[3])))
    return Proposal("PROPOSE_SYNTHETIC_ONLY",setting,round(gain,6),
                    -negcost,votes,common,
                    "Expected synthetic information per permitted unit cost")


def revise(state: TrialState, evidence, controls) -> TrialState:
    """Preserve a prediction-evidence scar; never turn a simulation into fact."""
    if not state.models:
        return state
    if not source_compatible(evidence,state.models[0].first,
                             state.models[0].second,controls,
                             state.models[0].known_vocabulary):
        raise HOLD("Unreviewed intervention source vocabulary")
    a,b=controls_present(evidence,controls)
    residual=_residual(evidence,controls)
    c=feature_present(evidence,state.models[0].first.name,
                      state.models[0].first.role_index)
    p=feature_present(evidence,state.models[0].second.name,
                      state.models[0].second.role_index)
    predictions=tuple(x.residual(c,p) for x in state.models)
    survivors=tuple(x for x,guess in zip(state.models,predictions)
                    if guess==residual)
    scar=Scar((c,p),residual,predictions,evidence.provenance,
              "INDEPENDENT_SYNTHETIC_OBSERVATION")
    new_status=("OUTSIDE_GRAMMAR" if not survivors else
                "SINGLE_PROVISIONAL" if len(survivors)==1 else
                "COMPETING_EXPLANATIONS")
    return TrialState(survivors,state.scars+(scar,),new_status)


def independent_review(state: TrialState, local_evidence, controls) -> Review:
    """Independent intervention evidence is never used for query selection."""
    source=tuple(local_evidence)
    if len(state.models)!=1:
        return Review("HOLD_AMBIGUOUS_OR_FALSIFIED",None,len(source),())
    proposed=state.models[0]
    conflicts=[]
    seen={}
    for row in source:
        if row.provenance!="SYNTHETIC_INTERVENTION":
            raise HOLD("Independent review requires new intervention evidence")
        if not source_compatible(row,proposed.first,proposed.second,controls,
                                 proposed.known_vocabulary):
            raise HOLD("Unreviewed local schema")
        a,b=controls_present(row,controls)
        c=feature_present(row,proposed.first.name,proposed.first.role_index)
        p=feature_present(row,proposed.second.name,proposed.second.role_index)
        actual=_residual(row,controls)
        expected=proposed.residual(c,p)
        seen.setdefault((c,p),[]).append(actual)
        if actual!=expected:
            conflicts.append(Scar((c,p),actual,(expected,),row.provenance,
                                  "INDEPENDENT_REVIEW_FALSIFIED_PROPOSAL"))
    if len(source)<8 or set(seen)!=set(PAIRS):
        return Review("HOLD_INSUFFICIENT_LOCAL_REVIEW",proposed.tree.id,
                      len(source),tuple(conflicts))
    if conflicts:
        return Review("HOLD_INDEPENDENT_FALSIFIER",proposed.tree.id,
                      len(source),tuple(conflicts))
    return Review("ADMIT_PREDICT_ONLY_IN_SYNTHETIC_LAB",proposed.tree.id,
                  len(source),())


def retained_contradictions(state,review):
    return {
        "experiment_scars":len(state.scars),
        "independent_falsification_scars":len(review.contradictions),
        "real_world_authority":False,
        "cartridge_checksums_authenticate_source":False,
    }
