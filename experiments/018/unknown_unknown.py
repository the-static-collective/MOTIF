"""MOTIF-018: finite, synthetic representation-expansion experiment.

Nothing here is an LLM, online learner, external agent, or consciousness test.
The generator and evaluator know the simulated mechanism; the proposer receives
only labelled training and validation episodes and raw typed graph edges.
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from hashlib import sha256
from itertools import product
import json


@dataclass(frozen=True)
class Episode:
    identity: str
    x: int
    edges: tuple[tuple[str, str, str], ...]
    outcome: int
    authorized: bool

    def surface(self) -> tuple[int]:
        """The initial observer can see x, but not derived graph relations."""
        return (self.x,)


@dataclass(frozen=True, order=True)
class RelationProgram:
    """An induced boolean concept, composed from raw typed graph edges."""
    kind: str  # direct or path2
    relations: tuple[str, ...]

    def read(self, episode: Episode) -> int:
        edges = episode.edges
        if self.kind == "direct":
            return int(("actor", self.relations[0], "goal") in edges)
        if self.kind == "path2":
            first, second = self.relations
            mids = {dst for src, rel, dst in edges
                    if src == "actor" and rel == first}
            return int(any((mid, second, "goal") in edges for mid in mids))
        raise ValueError("UNKNOWN_CONCEPT_GRAMMAR")

    def name(self) -> str:
        return self.kind + "(" + ",".join(self.relations) + ")"


@dataclass(frozen=True)
class PredictionModel:
    concept: RelationProgram | None
    table: tuple[tuple[int, int, int], ...]  # x, concept_value, predicted_outcome

    def predict(self, episode: Episode) -> int | None:
        key = (episode.x, self.concept.read(episode) if self.concept else 0)
        for x, feature, value in self.table:
            if (x, feature) == key:
                return value
        return None


def build_episode(identity: str, x: int, path: int, badge: int,
                  outcome: int, authorized: bool = True) -> Episode:
    if any(v not in (0, 1) for v in (x, path, badge, outcome)):
        raise ValueError("BINARY_SYNTHETIC_FIXTURE_ONLY")
    relay = "relay-" + identity
    edges = [
        ("actor", "carries", relay),
        (relay, "reaches" if path else "wanders", "goal" if path else "nowhere"),
        ("observer", "records", "actor"),
    ]
    if badge:
        edges.append(("actor", "marked", "goal"))
    return Episode(identity, x, tuple(edges), outcome, authorized)


def world(regime: str, split: str) -> tuple[Episode, ...]:
    """Frozen constructed worlds. A decoy is correlated in train only.

    path: outcome = x XOR path
    badge: outcome = x XOR badge (a transfer counterexample)
    latent: outcome = x XOR unrepresented hidden bit; duplicated visible
            signatures with opposite labels make it unidentifiable.
    """
    if regime not in ("path", "badge", "latent"):
        raise ValueError("UNKNOWN_WORLD")
    if split not in ("train", "validation", "holdout"):
        raise ValueError("UNKNOWN_SPLIT")
    rows: list[Episode] = []
    for x, path in product((0, 1), repeat=2):
        badges = (path,) if split == "train" else (
            (1 - path,) if split == "validation" else (0, 1))
        for badge in badges:
            hidden_states = (0, 1) if regime == "latent" else (0,)
            for hidden in hidden_states:
                target = path if regime == "path" else (
                    badge if regime == "badge" else hidden)
                label = x ^ target
                identity = f"{regime}-{split}-{x}{path}{badge}{hidden}"
                # Independent simulated permission: a correct prediction
                # never grants or overrides this authorizing condition.
                authorized = x == 0 or badge == 0
                rows.append(build_episode(identity, x, path, badge, label,
                                          authorized))
    return tuple(rows)


def propose_concepts(train: tuple[Episode, ...]) -> tuple[RelationProgram, ...]:
    """Enumerate relational programs from unlabeled graph topology alone.

    The grammar is supplied, but the specific relations and their pairings
    are extracted rather than supplied as a list of candidate concepts.
    """
    found: set[RelationProgram] = set()
    for episode in train:
        edges = episode.edges
        for src, rel, dst in edges:
            if src != "actor":
                continue
            if dst == "goal":
                found.add(RelationProgram("direct", (rel,)))
            for mid_src, next_rel, next_dst in edges:
                if mid_src == dst and next_dst == "goal":
                    found.add(RelationProgram("path2", (rel, next_rel)))
    return tuple(sorted(found))


def fit(examples: tuple[Episode, ...],
        concept: RelationProgram | None = None) -> PredictionModel:
    votes: dict[tuple[int, int], list[int]] = defaultdict(list)
    for episode in examples:
        feature = concept.read(episode) if concept else 0
        votes[(episode.x, feature)].append(episode.outcome)
    # A tie is reported by the chosen 0; it must not masquerade as certainty.
    table = tuple(sorted((x, feature, int(sum(ys) > len(ys) / 2))
                         for (x, feature), ys in votes.items()))
    return PredictionModel(concept, table)


def assess(model: PredictionModel, cases: tuple[Episode, ...]) -> dict:
    predictions = [(case, model.predict(case)) for case in cases]
    covered = [(case, p) for case, p in predictions if p is not None]
    correct = sum(case.outcome == p for case, p in covered)
    true_permitted = sum(p == 1 and case.outcome == 1 and case.authorized
                         for case, p in covered)
    # Predictions are not action proposals without explicit toy permission.
    # Preserve the number withheld by the permission fence separately.
    withheld = sum(p == 1 and not case.authorized for case, p in covered)
    wrong_or_unpermitted = sum(
        p == 1 and case.authorized and case.outcome != 1
        for case, p in covered)
    return {
        "total": len(cases),
        "covered": len(covered),
        "correct": correct,
        "accuracy": round(correct / len(cases), 6) if cases else None,
        "coverage": round(len(covered) / len(cases), 6) if cases else None,
        "correct_permitted_positive_plans": true_permitted,
        "wrong_or_unpermitted_positive_proposals": wrong_or_unpermitted,
        "positive_predictions_withheld_by_permission": withheld,
    }


def surface_collisions(train: tuple[Episode, ...]) -> int:
    groups: dict[tuple[int], set[int]] = defaultdict(set)
    for episode in train:
        groups[episode.surface()].add(episode.outcome)
    return sum(len(values) > 1 for values in groups.values())


def admissible(model: PredictionModel, train: tuple[Episode, ...],
               validation: tuple[Episode, ...]) -> bool:
    """Perfect frozen validation is deliberate; no noise robustness claimed."""
    a, b = assess(model, train), assess(model, validation)
    return (a["coverage"] == 1 and b["coverage"] == 1
            and a["accuracy"] == 1 and b["accuracy"] == 1)


def classical_exhaustive_selector(train: tuple[Episode, ...],
                                 validation: tuple[Episode, ...]
                                 ) -> PredictionModel | None:
    """Strong conventional finite feature-selection comparator.

    Searches exactly the same permitted feature grammar, and has access
    to the same evidence. Expected to tie, not to lose artificially.
    """
    feasible: list[PredictionModel] = []
    for program in propose_concepts(train):
        candidate = fit(train, program)
        if admissible(candidate, train, validation):
            feasible.append(candidate)
    return feasible[0] if len(feasible) == 1 else None


def discover(train: tuple[Episode, ...],
             validation: tuple[Episode, ...]) -> dict:
    collisions = surface_collisions(train)
    diagnostics = {
        "v0": "HOLD_CONTRADICTORY_SURFACE" if collisions else "NO_SURPRISE",
        "surface_collision_groups": collisions,
        "proposed_revision": "search_composed_graph_relations"
                             if collisions else None,
        "revision_installed": False,
    }
    if not collisions:
        return {"status": "HOLD_NO_OBSERVED_GAP", "diagnostics": diagnostics,
                "candidates": [], "model": None}
    candidates = propose_concepts(train)
    assessments = []
    accepted = []
    for concept in candidates:
        model = fit(train, concept)
        training = assess(model, train)
        validation_score = assess(model, validation)
        passed = admissible(model, train, validation)
        assessments.append({"concept": concept.name(), "train": training,
                            "validation": validation_score, "passes": passed})
        if passed:
            accepted.append(model)
    if len(accepted) != 1:
        return {"status": "HOLD_RIVAL_MODELS" if accepted else
                "HOLD_UNEXPLAINED_SURPRISE", "diagnostics": diagnostics,
                "candidates": assessments, "model": None}
    model = accepted[0]
    receipt = {
        "kind": "representation-expansion-cartridge/v0",
        "scope": "SYNTHETIC_PREDICTION_ONLY",
        "program": model.concept.name(),
        "truth_table": model.table,
        "source_train_ids": [case.identity for case in train],
        "source_validation_ids": [case.identity for case in validation],
        "authority": "NONE",
        "human_review_required": True,
    }
    receipt["checksum_sha256"] = sha256(
        json.dumps(receipt, sort_keys=True).encode()).hexdigest()
    return {"status": "HOLD_FOR_HUMAN_REVIEW", "diagnostics": diagnostics,
            "candidates": assessments, "model": model, "cartridge": receipt}


def intervention_audit(model: PredictionModel) -> dict:
    """Evaluator-only controlled changes to the synthetic path relation.

    The model did not see these records or their true simulator mechanism.
    Holding x and badge fixed while toggling a path is an explicit toy
    intervention, NOT a claim of real-world causal identification.
    """
    pairs = []
    for x, badge in product((0, 1), repeat=2):
        low = build_episode(f"intervene-{x}{badge}-0", x, 0, badge, x)
        high = build_episode(f"intervene-{x}{badge}-1", x, 1, badge, x ^ 1)
        pair = {"x": x, "badge_held_fixed": badge,
                "prediction_before": model.predict(low),
                "prediction_after": model.predict(high),
                "observed_before": low.outcome,
                "observed_after": high.outcome}
        pairs.append(pair)
    passed = all(p["prediction_before"] == p["observed_before"] and
                 p["prediction_after"] == p["observed_after"] for p in pairs)
    return {"pairs": pairs, "all_interventions_predicted": passed,
            "interventions_executed_in_real_world": False}


def run() -> dict:
    train, validation, holdout = (world("path", s)
                                  for s in ("train", "validation", "holdout"))
    result = discover(train, validation)
    base = fit(train)
    classical = classical_exhaustive_selector(train, validation)
    assert result["model"] is not None and classical is not None
    selected = result["model"]
    transfer = world("badge", "holdout")
    unrepresented = discover(world("latent", "train"),
                             world("latent", "validation"))
    report = {
        "schema": "motif018.benchmark/v0",
        "title": "THE UNKNOWN UNKNOWN",
        "world_family": "invented_binary_graphs_only",
        "selection_used_holdout": False,
        "status": result["status"],
        "diagnostics": result["diagnostics"],
        "proposed_concepts": result["candidates"],
        "cartridge": result["cartridge"],
        "heldout_surface_only": assess(base, holdout),
        "heldout_expanded": assess(selected, holdout),
        "heldout_classical_exhaustive_feature_search":
            assess(classical, holdout),
        "synthetic_path_interventions": intervention_audit(selected),
        "negative_transfer_to_badge_cause": assess(selected, transfer),
        "unrepresented_hidden_cause_status": unrepresented["status"],
        "external_actions": 0,
        "automatically_deployed": False,
        "consciousness_claim": False,
        "limits": [
            "The grammar and world generators are hand supplied.",
            "The model learns a two-variable table, not general causal laws.",
            "Perfect validation is incompatible with noisy real evidence.",
            "The classical exhaustive feature selector ties in this toy world.",
            "Source ids and checksums do not authenticate external evidence.",
        ],
    }
    return report


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
