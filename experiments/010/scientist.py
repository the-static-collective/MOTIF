"""MOTIF-010 — the Scientist.

Infer a *version space of inspectable MOTIF-009 decision-tree cartridges*
from synthetic natural observations, then select a controlled intervention
whose possible outcomes most sharply divide rival explanations.

The learner imports NO oracle and never sees hidden family names, hidden
rules, or test labels. It receives only graph before/after snapshots and an
explicit public schema of two Boolean intervention ports.

A graph experiment is not a real-world action. Neither the cards nor the
scientist have any authority to dispatch external operations.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from math import log2
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "008"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "009"))

from cartridge import Cartridge, checksum, export_cartridge, validate_cartridge
from learner import features, balanced_accuracy

OPTIONS = tuple(product((False, True), repeat=2))
PROVENANCES = frozenset(("SYNTHETIC_NATURAL", "SYNTHETIC_INTERVENTION"))


class NoConsistentExplanation(ValueError):
    pass


def validated_result(episode) -> bool:
    """Evidence is a graph change, not an oracle-provided success label."""
    if getattr(episode, "provenance", None) not in PROVENANCES:
        raise ValueError("Unverified or non-synthetic observation")
    before, after = episode.before, episode.observed_after
    if not isinstance(before, frozenset) or not isinstance(after, frozenset):
        raise ValueError("Observation graph must be immutable")
    actor, target = episode.roles
    if ("role_actor", actor) not in before or ("role_target", target) not in before:
        raise ValueError("Missing declared roles")
    if ("pending", target) not in before:
        raise ValueError("Missing source state")
    expected = frozenset((before - {("pending", target)}) |
                         {("achieved", target)})
    if after == before:
        return False
    if after == expected:
        return True
    raise ValueError("Partial or unrelated observation cannot label this toy outcome")


def schema_motifs(controls):
    a, b = controls.first_port, controls.second_port
    if not isinstance(a, str) or not isinstance(b, str) or a == b:
        raise ValueError("Need two distinct named synthetic intervention ports")
    return ((a, "?0"),), ((b, "?1"),)


def controls_present(episode, controls) -> tuple[bool, bool]:
    a, b = schema_motifs(controls)
    actor, target = episode.roles
    return ( (controls.first_port, actor) in episode.before,
             (controls.second_port, target) in episode.before )


def _source_digest(records, controls):
    # Role-relative fact projections + labels only. No original IDs exported.
    normalized = sorted(
        [list(controls_present(row, controls)), int(validated_result(row))]
        for row in records)
    return checksum({"synthetic_role_relative_observations": normalized})


def make_tree(bits: tuple[bool,bool,bool,bool], observed, controls) -> Cartridge:
    """Materialize one possible two-question tree as a portable cartridge.

    The four Boolean leaves are hypotheses, never represented as independently
    observed events. Leaf counts represent real *synthetic* observations.
    """
    items = tuple(observed)
    if not items:
        raise ValueError("Need source observations")
    if len(bits) != 4 or any(type(v) is not bool for v in bits):
        raise ValueError("Expected four Boolean hypothetical leaves")
    first, second = schema_motifs(controls)
    tally = [[0, 0] for _ in range(4)]
    rows = []
    for case in items:
        p, q = controls_present(case, controls)
        y = validated_result(case)
        slot = 2*int(p)+int(q)
        tally[slot][int(y)] += 1
        rows.append((slot,y))
    truth = tuple(y for _,y in rows)
    guess = tuple(bits[slot] for slot,_ in rows)
    fit = (round(balanced_accuracy(truth, guess), 6)
           if 0 < sum(truth) < len(truth) else 0.5)
    vocab = tuple(sorted({"role_actor", "role_target", "pending",
                          controls.first_port, controls.second_port}))
    data = {
        "schema": "motif.decision-tree-cartridge.v0",
        "vocab": list(vocab),
        "first": [list(x) for x in first],
        "second": [list(x) for x in second],
        "leaves": list(bits),
        "counts": tally,
        "fit_balanced": fit,
        "evidence_count": len(items),
        "source_digest": _source_digest(items, controls),
        "status": "PROPOSAL_ONLY"
    }
    identifier = "tree-" + checksum(data)[:16]
    card = Cartridge(identifier, data["schema"], vocab, first, second,
                     bits, tuple(tuple(x) for x in tally), fit, len(items),
                     data["source_digest"])
    return card


def candidate_cartridges(observed, controls) -> tuple[Cartridge, ...]:
    """Discover viable explanations by enumerating ALL 16 two-bit trees.

    This is a complete version space for *this fixed two-control grammar*;
    it is not inductive causal discovery from raw physics.
    """
    evidence = tuple(observed)
    if not evidence:
        raise ValueError("Need independent synthetic observations")
    seen = []
    for row in evidence:
        flags = controls_present(row, controls)
        y = validated_result(row)
        seen.append((2*int(flags[0])+int(flags[1]), y))
    candidates = []
    for bits in product((False,True), repeat=4):
        if all(bits[slot] == outcome for slot,outcome in seen):
            candidates.append(make_tree(bits, evidence, controls))
    if not candidates:
        raise NoConsistentExplanation("No two-control tree explains the observations")
    return tuple(candidates)


def entropy(portion_true: float) -> float:
    if not 0 < portion_true < 1:
        return 0.0
    return (-portion_true*log2(portion_true)
            -(1-portion_true)*log2(1-portion_true))


def predicted_under_control(card: Cartridge, first: bool, second: bool) -> bool:
    """The abstract intervention sets each visible port, NOT the outcome."""
    if type(first) is not bool or type(second) is not bool:
        raise ValueError("Controlled intervention values must be Boolean")
    tokens = set()
    if first:
        tokens.add(card.first)
    if second:
        tokens.add(card.second)
    return card.predict(frozenset(tokens))


@dataclass(frozen=True)
class Proposal:
    first: bool
    second: bool
    information_gain_bits: float
    competing_tree_ids: tuple[str, ...]
    predicted_votes: tuple[bool, ...]
    action: str = "DO_SYNTHETIC_PORT_SETTINGS"
    real_world_authority: bool = False


def propose_intervention(candidates: tuple[Cartridge, ...],
                         already_tested=()) -> Proposal | None:
    """Select the experiment that maximizes expected posterior information.

    Uniformly weighted, exact, deterministic model set; zero observation noise.
    This is classical version-space information gain, not a novel algorithm.
    An intentionally independent simulator must execute the proposal.
    """
    if not candidates:
        raise ValueError("No candidate hypotheses")
    exhausted = set(already_tested)
    available = [pair for pair in OPTIONS if pair not in exhausted]
    if not available:
        return None
    best = None
    for first, second in available:
        votes = tuple(predicted_under_control(c,first,second) for c in candidates)
        gain = entropy(sum(votes) / len(votes))
        proposal = Proposal(first, second, round(gain, 6),
                            tuple(c.id for c in candidates), votes)
        if best is None or proposal.information_gain_bits > best.information_gain_bits:
            best = proposal
    return best if best.information_gain_bits > 0 else None


def consensus(candidates: tuple[Cartridge, ...], first: bool, second: bool):
    if not candidates:
        raise ValueError("No hypotheses")
    votes = {predicted_under_control(card, first, second) for card in candidates}
    return next(iter(votes)) if len(votes) == 1 else None


def explanation_report(candidates: tuple[Cartridge, ...]) -> dict:
    return {
        "candidate_tree_cartridges": len(candidates),
        "hypotheses": [{"id": c.id, "leaves": list(c.leaves),
                        "observed_samples": c.evidence_count}
                       for c in candidates],
        "consensus_coverage_of_four_controls":
            sum(consensus(candidates, *pair) is not None
                for pair in OPTIONS) / len(OPTIONS),
        "real_world_authority": False,
        "cartridge_status": "PROPOSAL_ONLY"
    }
