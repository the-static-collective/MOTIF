"""MOTIF-011 — The Skeptical Scientist.

Instead of forcing a comforting 2-input decision tree on contradictory
observations, preserve the contradiction and ABSTAIN. If a *visible* but
previously unmodeled role-relative unary relation uniquely explains the
mismatch, propose a router containing two real MOTIF-009 tree cartridges.

That proposal remains HELD until independent local synthetic review. Genuine
hidden variables, deliberate label flips and indistinguishable proxy concepts
are not "explained away" by inventing a cause.

This is a restricted, transparent symbolic model. It does NOT import the
hidden-rule oracle, authenticate a human, infer physical causation or act.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from itertools import product
import json
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "008"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "009"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "010"))
from scientist import (validated_result, controls_present, candidate_cartridges,
                       make_tree, predicted_under_control, entropy)
from cartridge import (Cartridge, export_cartridge, validate_cartridge,
                       checksum, HOLD as CARTRIDGE_HOLD)

CONTROL_OPTIONS = tuple(product((False, True), repeat=2))
EXCLUDED = frozenset(("role_actor", "role_target", "pending",
                      "achieved"))
SAFE_LABEL = re.compile(r"^[A-Za-z0-9_?.:-]{1,96}$")


class HOLD(ValueError):
    """Model outside grammar, ambiguous evidence, or unavailable permission."""


@dataclass(frozen=True)
class EvidenceScar:
    controls: tuple[bool, bool]
    observed_outcomes: tuple[bool, ...]
    disagreement: bool
    provenance: str = "SYNTHETIC_CONTRADICTION"


@dataclass(frozen=True)
class Extension:
    """A new role-relative relation routing to two 009 tree cartridges."""
    id: str
    relation: str
    role_index: int
    control_names: tuple[str,str]
    allowed_vocabulary: tuple[str,...]
    when_absent: Cartridge
    when_present: Cartridge
    source_count: int
    validation_count: int
    status: str = "PROPOSED_NOT_ADMITTED"

    def predict(self, episode, controls) -> bool:
        if (controls.first_port, controls.second_port) != self.control_names:
            raise HOLD("Unreviewed control vocabulary; no implicit domain transfer")
        present = {fact[0] for fact in episode.before}
        if (not {"role_actor","role_target","pending"}.issubset(present)
                or not present.issubset(self.allowed_vocabulary)):
            raise HOLD("Unreviewed predicate in local concept prediction")
        value = feature_present(episode, self.relation, self.role_index)
        tree = self.when_present if value else self.when_absent
        a, b = controls_present(episode, controls)
        return predicted_under_control(tree, a, b)

    def metadata(self) -> dict:
        return {"id": self.id, "relation": self.relation,
                "role_index": self.role_index,
                "control_names": list(self.control_names),
                "allowed_vocabulary": list(self.allowed_vocabulary),
                "absent_tree": self.when_absent.id,
                "present_tree": self.when_present.id,
                "training_count": self.source_count,
                "validation_count": self.validation_count,
                "status": self.status,
                "real_world_authority": False}


@dataclass(frozen=True)
class Assessment:
    status: str
    contradictions: tuple[EvidenceScar, ...]
    accepted_two_port: Cartridge | None
    extension: Extension | None
    extension_candidates: int
    reason: str

    def predict_two_port(self, episode, controls) -> bool | None:
        if self.status != "TWO_PORT_CONSISTENT" or self.accepted_two_port is None:
            return None
        a, b = controls_present(episode, controls)
        return predicted_under_control(self.accepted_two_port, a, b)


def evidence_scars(records, controls) -> tuple[EvidenceScar, ...]:
    grouped: dict[tuple[bool,bool], list[bool]] = {}
    for row in records:
        key = controls_present(row, controls)
        grouped.setdefault(key, []).append(validated_result(row))
    return tuple(EvidenceScar(key, tuple(outcomes),
                              len(set(outcomes)) > 1)
                 for key,outcomes in sorted(grouped.items()))


def features_to_investigate(records, controls):
    """Anonymous predicate candidates found directly in observed graph facts.

    Restrict to unary facts whose subject is a declared actor/target. This
    grammar is deliberately narrow and cannot infer absent hidden variables.
    """
    known = {controls.first_port, controls.second_port} | EXCLUDED
    found = set()
    for row in records:
        actor, target = row.roles
        for fact in row.before:
            if len(fact) != 2 or fact[0] in known:
                continue
            if fact[1] == actor:
                found.add((fact[0], 0))
            elif fact[1] == target:
                found.add((fact[0], 1))
    return tuple(sorted(found))


def feature_present(episode, relation: str, role_index: int) -> bool:
    return (relation, episode.roles[role_index]) in episode.before


def _truth_table(records, controls, relation: str, role_index: int):
    """Return an exact 8-leaf table iff all cells observed and uncontradicted."""
    observations = {}
    for row in records:
        a,b = controls_present(row, controls)
        c = feature_present(row, relation, role_index)
        key = (a,b,c)
        actual = validated_result(row)
        if key in observations and observations[key] != actual:
            return None
        observations[key] = actual
    if len(observations) != 8:
        return None
    return tuple(observations[a,b,c] for a,b,c in
                 product((False,True), repeat=3))


def _run_table(table, row, controls, relation, role_index):
    a,b = controls_present(row, controls)
    c = feature_present(row, relation, role_index)
    return table[4*int(a)+2*int(b)+int(c)]


def _extension_from_table(records, validation, controls,
                          relation, role_index, truth):
    # Each subtree uses *actual* 009 Cartridge definitions and original 010
    # proposal constructors; a third predicate is used only as local router.
    partition = (
        tuple(x for x in records if not feature_present(x, relation, role_index)),
        tuple(x for x in records if feature_present(x, relation, role_index)))
    if min(map(len, partition)) < 4:
        raise HOLD("Not enough evidence for both routing branches")
    absent = tuple(truth[4*int(a)+2*int(b)] for a,b in CONTROL_OPTIONS)
    present = tuple(truth[4*int(a)+2*int(b)+1] for a,b in CONTROL_OPTIONS)
    first = make_tree(absent, partition[0], controls)
    second = make_tree(present, partition[1], controls)
    # Nothing magical here: when c is false/true, use a separately inspectable
    # two-question decision tree with explicit role-relative tests.
    content = {"relation": relation, "role_index": role_index,
               "absent": first.id, "present": second.id}
    ident = "extension-" + checksum(content)[:16]
    vocab = tuple(sorted({f[0] for row in (tuple(records)+tuple(validation))
                          for f in row.before}))
    return Extension(ident, relation, role_index,
                     (controls.first_port,controls.second_port), vocab,
                     first, second, len(records), len(validation))


def assess(records, validation, controls) -> Assessment:
    """Fail closed if complete source evidence contradicts the two-port model.

    * Training chooses concept candidates.
    * A separate validation split must agree with its 8-leaf predictions.
    * Held-out test data is NEVER used for this decision.
    * There is no automatic admission of a proposed extension.
    """
    train, val = tuple(records), tuple(validation)
    if not train or not val:
        raise ValueError("Independent evidence and validation are required")
    scars = evidence_scars(train, controls)
    conflicts = tuple(x for x in scars if x.disagreement)
    # Cannot promote a concept when the standard two-input model hasn't even
    # been tested on all four settings.
    if len(scars) != 4 or any(len(x.observed_outcomes) < 2 for x in scars):
        return Assessment("ABSTAIN_SPARSE", conflicts, None, None, 0,
                          "Insufficient observation coverage for a two-port model")

    if not conflicts:
        if len({controls_present(x,controls) for x in val}) != 4:
            return Assessment("ABSTAIN_VALIDATION", conflicts, None,None,0,
                              "Validation omitted possible control settings")
        cards = candidate_cartridges(train, controls)
        if len(cards) != 1:
            return Assessment("ABSTAIN_AMBIGUOUS", conflicts,None,None,len(cards),
                              "Multiple two-port hypotheses remain")
        card = cards[0]
        if all(predicted_under_control(card, *controls_present(x,controls)) ==
               validated_result(x) for x in val):
            return Assessment("TWO_PORT_CONSISTENT", (),card,None,0,
                              "Exact structural fit to training and validation only")
        return Assessment("ABSTAIN_VALIDATION", (),None,None,0,
                          "Independent validation contradicts two-port candidate")

    # The two-port hypothesis family is falsified by repeated same-input
    # observations with different outcomes. Preserve scars, not guesses.
    candidates = []
    for relation, index in features_to_investigate(train, controls):
        table = _truth_table(train, controls, relation, index)
        if table is None:
            continue
        if all(_run_table(table,row,controls,relation,index) ==
               validated_result(row) for row in val):
            candidates.append((relation, index, table))
    if len(candidates) == 0:
        return Assessment("ABSTAIN_INADEQUATE",conflicts,None,None,0,
                          "No observed single extra relation predicts both splits")
    if len(candidates) > 1:
        return Assessment("ABSTAIN_AMBIGUOUS",conflicts,None,None,
                          len(candidates),
                          "Multiple observationally equivalent new concepts")
    relation,index,table = candidates[0]
    extension = _extension_from_table(train,val,controls,relation,index,table)
    return Assessment("PROPOSE_EXTENSION",conflicts,None,extension,1,
                      "New observed relation predicts validation, not proven causal")


@dataclass(frozen=True)
class Review:
    decision: str
    extension_id: str
    reviewer_claim: str
    local_examples: int
    heldout_information_used: bool
    real_world_authority: bool = False


class LocalConceptBay:
    """Explicit prediction-only local review; no external authority."""
    def __init__(self):
        self.pending: dict[str, Extension] = {}
        self.admitted: dict[str, Extension] = {}
        self.receipts: list[Review] = []

    def offer(self, assessment: Assessment) -> str:
        if assessment.status != "PROPOSE_EXTENSION" or not assessment.extension:
            raise HOLD("No unique testable concept to review")
        candidate = assessment.extension
        self.pending[candidate.id] = candidate
        return candidate.id

    def review(self, extension_id: str, decision: str, reviewer_claim: str,
               local_records=(), controls=None) -> Review:
        if extension_id not in self.pending:
            raise HOLD("No pending concept extension")
        if not isinstance(reviewer_claim,str) or not SAFE_LABEL.fullmatch(reviewer_claim):
            raise HOLD("Unverified local reviewer label required")
        if decision not in ("ADMIT_PREDICT_ONLY","REFUSE"):
            raise HOLD("Only explicit local predict-only review allowed")
        extension = self.pending[extension_id]
        records = tuple(local_records)
        if decision == "ADMIT_PREDICT_ONLY":
            if len(records) < 8 or controls is None:
                raise HOLD("Missing independent local review observations")
            if len({(controls_present(x,controls),
                     feature_present(x,extension.relation,extension.role_index))
                    for x in records}) < 8:
                raise HOLD("Review does not cover all eight local structures")
            if not all(extension.predict(x,controls) == validated_result(x)
                       for x in records):
                raise HOLD("Independent review fails concept predictions")
            self.admitted[extension_id] = extension
        else:
            self.admitted.pop(extension_id,None)
        receipt = Review(decision,extension_id,reviewer_claim,len(records),
                         heldout_information_used=False)
        self.receipts.append(receipt)
        return receipt

    def predict(self, extension_id, episode, controls):
        if extension_id not in self.admitted:
            raise HOLD("Extension not locally admitted")
        return self.admitted[extension_id].predict(episode,controls)


@dataclass(frozen=True)
class SafetyDecision:
    status: str
    settings: tuple[bool,bool] | None
    gain_bits: float
    cost: int
    why: str
    real_world_authority: bool = False


def safe_experiment(candidates: tuple[Cartridge,...], *,
                    allowed, costs, remaining_budget, already_tested=()):
    """A cost-gated *proposal only*, with no actuation interface.

    Zero-cost actions are not allowed: this experiment uses positive integer
    costs and a finite budget. Unsafe settings are removed BEFORE optimizing.
    """
    if type(remaining_budget) is not int or remaining_budget < 0:
        raise ValueError("Invalid controlled experiment budget")
    permitted = frozenset(allowed)
    if not permitted.issubset(CONTROL_OPTIONS) or set(costs) != set(CONTROL_OPTIONS):
        raise ValueError("Unknown experiment settings")
    if any(type(costs[x]) is not int or costs[x] < 1 for x in costs):
        raise ValueError("Positive integer costs required")
    checked = frozenset(already_tested)
    eligible = []
    informative_any = []
    for a,b in CONTROL_OPTIONS:
        pair=(a,b)
        if pair in checked:
            continue
        votes = tuple(predicted_under_control(x,a,b) for x in candidates)
        gain = entropy(sum(votes)/len(votes))
        if gain<=0:
            continue
        informative_any.append(pair)
        if pair in permitted and costs[pair] <= remaining_budget:
            eligible.append((gain/costs[pair],gain,-costs[pair],pair))
    if not informative_any:
        return SafetyDecision("HOLD_NO_INFORMATION",None,0.0,0,
                              "All current candidates agree")
    if not eligible:
        policy_safe = set(informative_any) & permitted
        status = "HOLD_BUDGET" if policy_safe else "HOLD_UNSAFE"
        return SafetyDecision(status,None,0.0,0,
                              "No informative experiment admitted by local policy")
    _,gain,negative_cost,pair=max(eligible,
        key=lambda x:(x[0],x[1],x[2],tuple(not v for v in x[3])))
    return SafetyDecision("PROPOSE_SYNTHETIC_ONLY",pair,round(gain,6),
                          -negative_cost,
                          "Local policy filter and finite-budget check passed")
