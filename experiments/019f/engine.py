"""MOTIF-019F: learn a missing STRIPS guard from independently checked questions.

The source-pinned National Treasure engine determines whether the claim is
ready for discriminator inquiry. Native Dogram compares finite probe
partitions. The learner enumerates typed graph features from observed
synthetic relation triples; independent validation selects or refuses them.

A field claim, hash, or prototype acceptance grants NO real-world authority.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Mapping, Sequence

from bridge import gated_discriminator, OrganHold


Edge = tuple[str, str, str]


@dataclass(frozen=True)
class Episode:
    case_id: str
    phase: str  # TRAIN, DISCOVERY, or REVIEW
    edges: tuple[Edge, ...]
    succeeded: bool | None  # DISCOVERY graphs are NOT labeled
    source: str


@dataclass(frozen=True)
class Feature:
    name: str
    kind: str  # DIRECT_BADGE or PATH2_GATE
    relation: str
    second_relation: str | None
    target: str
    guard_fact: str
    probe_cost: float


@dataclass(frozen=True)
class GuardProposal:
    status: str
    feature: Feature | None
    action: str
    question: str
    checked_train: tuple[str, ...]
    checked_review: tuple[str, ...]
    rejected_rivals: tuple[str, ...]
    native_dogram_blob: str | None
    native_question_blob: str | None
    review_error: str | None
    explicit_permission: bool = False
    external_actions: bool = False


def generate_graph_features(training: Sequence[Episode]) -> tuple[Feature, ...]:
    """Induce a small typed question grammar from raw observed edges.

    This does NOT invent a physical sensor. Known relation labels and a
    fixed two-edge grammar are declared; only compositions are generated.
    """
    expressions: dict[str, Feature] = {}
    for episode in training:
        edges = set(episode.edges)
        for start, relation, end in edges:
            if start != "actor":
                continue
            if relation == "wears":
                name = "DIRECT:wears:" + end
                expressions[name] = Feature(name, "DIRECT_BADGE", relation, None,
                                            end, end, .10)
            if relation == "carries":
                for s2, r2, end2 in edges:
                    if s2 != end or end2 != "gate" or r2 != "opens":
                        continue
                    name = "PATH2:" + relation + ":" + r2 + ":" + end2
                    expressions[name] = Feature(name, "PATH2_GATE", relation,
                                                r2, end2, end, .20)
    return tuple(sorted(expressions.values(), key=lambda x: (x.probe_cost, x.name)))


def observes(feature: Feature, edges: Sequence[Edge]) -> bool:
    data = set(edges)
    if feature.kind == "DIRECT_BADGE":
        return ("actor", feature.relation, feature.target) in data
    if feature.kind == "PATH2_GATE":
        return (
            ("actor", feature.relation, feature.guard_fact) in data
            and (feature.guard_fact, feature.second_relation, feature.target) in data
        )
    raise ValueError("Unknown typed relation program")


def sample_clue(*, include_source: bool = True) -> dict:
    return {
        "clue": "A graph action succeeded for some synthetic cases but failed for others.",
        "provenance_class": "speculation",
        "support_confidence": "unsupported",
        "source_locator": "SYNTHETIC_EPISODES/019F" if include_source else "",
        "chronology": "Synthetic training and independent review phases are separately labeled.",
        "counterevidence": "A tempting badge marker is correlated only on training cases.",
        "falsifier": "A new unrelated case with the proposed guard but a failed action.",
        "source_families": ["train-generator", "independent-review-generator"],
        "competing_explanations": ["a badge permits passage", "a token pathway permits passage"],
    }


def propose_guard(
    action: str,
    training: Sequence[Episode],
    discovery: Sequence[Episode],
    independent_review: Sequence[Episode],
    clue: Mapping,
) -> GuardProposal:
    """Read authentic native *algorithms* but only synthetic witness claims.

    A train-perfect shortcut is NOT automatically accepted. An independently
    held reviewed group must confirm one candidate and disprove rivals.
    """
    def hold(status: str, question: str = "", error: str | None = None,
             rivals: tuple[str, ...] = (),
             question_blob: str | None = None, dogram_blob: str | None = None):
        return GuardProposal(status, None, action, question,
                             tuple(x.case_id for x in training),
                             tuple(x.case_id for x in independent_review),
                             rivals, dogram_blob, question_blob, error)
    ids = [x.case_id for x in (*training, *discovery, *independent_review)]
    if (len(ids) != len(set(ids)) or len(training) < 2
        or len(discovery) < 2 or len(independent_review) < 2
        or any(e.phase != "TRAIN" or e.succeeded is None for e in training)
        or any(e.phase != "DISCOVERY" or e.succeeded is not None for e in discovery)
        or any(e.phase != "REVIEW" or e.succeeded is None for e in independent_review)
        or len({e.source for e in independent_review}) < 2
        or {e.succeeded for e in training} != {False, True}):
        return hold("HOLD_INVALID_EVIDENCE_SPLIT")
    candidates = generate_graph_features(training)
    if not candidates:
        return hold("HOLD_NO_EXPRESSIBLE_QUESTION")
    positives = [x for x in training if x.succeeded]
    negatives = [x for x in training if not x.succeeded]
    target = (positives[0].case_id, negatives[0].case_id)
    states = tuple(x.case_id for x in (*training, *discovery))
    probe_vectors = {
        f.name: tuple("Y" if observes(f, x.edges) else "N"
                      for x in (*training, *discovery))
        for f in candidates
    }
    # A duplicate partition is the same finite information and must not be
    # counted as an independent separator. Original Dogram rejects it.
    distinct: dict[tuple[str, ...], str] = {}
    for name, vector in sorted(probe_vectors.items(), key=lambda item: item[0]):
        distinct.setdefault(vector, name)
    probes = {name: vector for vector, name in distinct.items()}
    try:
        native = gated_discriminator(dict(clue), states, probes, target)
    except (OrganHold, ValueError) as exc:
        return hold("HOLD_ORGAN_ERROR", error=str(exc)[:220])
    gate = native["question"]
    question = gate["question"]
    if native["status"] != "PROPOSE_MINIMAL_DISCRIMINATOR":
        return hold("HOLD_MISSING_QUESTION_FOUNDATION", question=question,
                    question_blob=gate.get("original_source_blob"))
    separator_names = set(native["dogram"]["native_result"]["separating_probes"])
    eligible = [
        feature for feature in candidates
        if feature.name in separator_names
        and all(observes(feature, e.edges) == e.succeeded for e in training)
    ]
    survivors = []
    failures = []
    for feature in eligible:
        mismatches = [e.case_id for e in independent_review
                      if observes(feature, e.edges) != e.succeeded]
        if mismatches:
            failures.append(feature.name + ":DISPROVED:" + ",".join(mismatches))
        else:
            survivors.append(feature)
    if len(survivors) != 1:
        return hold("HOLD_AMBIGUOUS_OR_FALSIFIED",
                    question=question, rivals=tuple(failures),
                    question_blob=gate["original_source_blob"],
                    dogram_blob=native["dogram"]["source_blob"])
    chosen = survivors[0]
    # We allow only a declarable modeled fact that an existing action can
    # produce; mapping a new graph relation to a new physical ability is OUT.
    return GuardProposal(
        "ELIGIBLE_MODEL_GUARD_ONLY", chosen, action, question,
        tuple(e.case_id for e in training),
        tuple(e.case_id for e in independent_review),
        tuple(failures),
        native["dogram"]["source_blob"],
        gate["original_source_blob"],
        None,
    )


def episode(case_id: str, phase: str, token: bool, badge: bool,
            succeeded: bool | None, source: str) -> Episode:
    edges: list[Edge] = []
    if token:
        edges += [("actor", "carries", "token"), ("token", "opens", "gate")]
    if badge:
        edges.append(("actor", "wears", "badge"))
    return Episode(case_id, phase, tuple(edges), succeeded, source)


def fixture_cases():
    # The four label-bearing REVIEW cases are separate from unlabeled
    # DISCOVERY scenes and from any later score-only test world.
    training = (
        episode("train-success", "TRAIN", True, True, True, "training-1"),
        episode("train-failure", "TRAIN", False, False, False, "training-2"),
    )
    discovery = (
        episode("unlabeled-one", "DISCOVERY", True, False, None, "discovery-1"),
        episode("unlabeled-two", "DISCOVERY", False, True, None, "discovery-2"),
    )
    review = (
        episode("review-success", "REVIEW", True, False, True, "review-A"),
        episode("review-failure", "REVIEW", False, True, False, "review-B"),
        episode("review-repeat-success", "REVIEW", True, True, True, "review-C"),
        episode("review-repeat-failure", "REVIEW", False, False, False, "review-D"),
    )
    return training, discovery, review
