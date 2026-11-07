"""QC-001: bounded relational-grammar experiment for MOTIF.

This is classical, deterministic, synthetic rule induction. The word
"quantum" names the source corpus, NOT a claim about quantum computing.
Nothing learns neural weights, invokes a tool, modifies MOTIF's installed
operator catalog, or authorizes an outside-world action.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from hashlib import sha256
import json

SHAPES = frozenset(("POINT", "AXIS", "FORK", "CUP", "LOOP"))
SPLITS = frozenset(("TRAIN", "VALIDATE", "TEST"))
PROVENANCE = "SYNTHETIC_QC001"


def digest(value: object) -> str:
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


@dataclass(frozen=True)
class Observation:
    evidence_id: str
    split: str
    decoder: str
    carrier: str
    operation: str
    result: str
    provenance: str = PROVENANCE

    def validate(self) -> None:
        if (self.provenance != PROVENANCE or self.split not in SPLITS
                or self.carrier not in SHAPES or self.result not in SHAPES
                or not self.decoder or not self.operation or not self.evidence_id):
            raise ValueError("Malformed or non-synthetic observation")

    @property
    def key(self) -> tuple[str, str, str]:
        return self.decoder, self.carrier, self.operation


@dataclass(frozen=True)
class Candidate:
    decoder: str
    carrier: str
    operation: str
    result: str
    train_digest: str
    training_count: int
    status: str = "CANDIDATE_ONLY"

    @property
    def key(self) -> tuple[str, str, str]:
        return self.decoder, self.carrier, self.operation


@dataclass(frozen=True)
class ReviewedRule:
    candidate: Candidate
    validation_digest: str
    validation_count: int
    status: str = "LOCAL_PREVIEW_ONLY"

    @property
    def key(self) -> tuple[str, str, str]:
        return self.candidate.key

    @property
    def pin(self) -> str:
        return digest((self.candidate.train_digest, self.validation_digest,
                       self.candidate.key, self.candidate.result))


def checked_rows(rows: tuple[Observation, ...], split: str) -> None:
    if len({r.evidence_id for r in rows}) != len(rows):
        raise ValueError("Evidence IDs must not repeat within a split")
    for row in rows:
        row.validate()
        if row.split != split:
            raise ValueError("Evidence split boundary crossed")


def propose(train: tuple[Observation, ...],
            minimum: int = 2) -> tuple[Candidate, ...]:
    """Induce only repeat-supported finite lookup transitions from TRAIN."""
    if minimum < 2:
        raise ValueError("Require two distinct synthetic observations")
    checked_rows(train, "TRAIN")
    grouped: dict[tuple[str, str, str], list[Observation]] = defaultdict(list)
    for row in train:
        grouped[row.key].append(row)
    candidates = []
    for key, rows in sorted(grouped.items()):
        if len(rows) < minimum or len({r.result for r in rows}) != 1:
            continue
        canonical = sorted((r.evidence_id, r.result) for r in rows)
        candidates.append(Candidate(*key, rows[0].result,
                                    digest((key, canonical)), len(rows)))
    return tuple(candidates)


def local_review(candidates: tuple[Candidate, ...],
                 train: tuple[Observation, ...],
                 validation: tuple[Observation, ...],
                 minimum: int = 2) -> tuple[ReviewedRule, ...]:
    """Independent validation. Holds contradictory/missing transitions."""
    checked_rows(train, "TRAIN")
    checked_rows(validation, "VALIDATE")
    if {r.evidence_id for r in train} & {r.evidence_id for r in validation}:
        raise ValueError("Training and validation evidence overlap")
    grouped: dict[tuple[str, str, str], list[Observation]] = defaultdict(list)
    for row in validation:
        grouped[row.key].append(row)
    # Never accept a caller-supplied candidate without replaying its training
    # derivation and its evidence checksum against the actual TRAIN split.
    canonical_candidates = {c.key: c for c in propose(train, minimum)}
    if len({c.key for c in candidates}) != len(candidates):
        raise ValueError("Duplicate candidate key")
    reviewed = []
    for candidate in candidates:
        if (candidate.status != "CANDIDATE_ONLY"
                or canonical_candidates.get(candidate.key) != candidate):
            raise ValueError("Candidate lacks matching training evidence")
        rows = grouped.get(candidate.key, ())
        if len(rows) < minimum or any(r.result != candidate.result for r in rows):
            continue
        canonical = sorted((r.evidence_id, r.result) for r in rows)
        reviewed.append(ReviewedRule(candidate,
                                     digest((candidate.key, canonical)), len(rows)))
    return tuple(reviewed)


@dataclass(frozen=True)
class Step:
    previous: str
    operation: str
    next_carrier: str
    rule_pin: str


@dataclass(frozen=True)
class World:
    carrier: str
    decoder: str
    steps: tuple[Step, ...] = ()

    def observable(self) -> tuple[str, str]:
        """Declared projection, not identity of complete formation history."""
        return self.decoder, self.carrier

    def witness(self) -> str:
        return digest((self.decoder, self.carrier,
                       [(s.previous, s.operation, s.next_carrier, s.rule_pin)
                        for s in self.steps]))


def preview(world: World, operation: str,
            rules: tuple[ReviewedRule, ...]) -> World | None:
    """Only locally preview a pinned, validated transition; otherwise HOLD."""
    if world.carrier not in SHAPES or not world.decoder or not operation:
        raise ValueError("Malformed synthetic world or action")
    indexed = {r.key: r for r in rules if r.status == "LOCAL_PREVIEW_ONLY"}
    if len(indexed) != len(rules):
        raise ValueError("Conflicting or unauthorized reviewed rule")
    rule = indexed.get((world.decoder, world.carrier, operation))
    if rule is None:
        return None
    following = rule.candidate.result
    if following == world.carrier:
        return None  # A no-op cannot be counted as a productive transition.
    step = Step(world.carrier, operation, following, rule.pin)
    return World(following, world.decoder, world.steps + (step,))


def route(start: World, operations: tuple[str, ...],
          rules: tuple[ReviewedRule, ...]) -> World | None:
    current = start
    for op in operations:
        following = preview(current, op, rules)
        if following is None:
            return None
        current = following
    return current


@dataclass(frozen=True)
class PathCartridge:
    """New candidate *macro* generated from a successful local output trace."""
    decoder: str
    start_carrier: str
    expected_end: str
    operations: tuple[str, ...]
    source_rule_pins: tuple[str, ...]
    source_witness: str
    status: str = "LOCAL_PREVIEW_ONLY"


def compile_path(start: World, observed: World,
                 rules: tuple[ReviewedRule, ...]) -> PathCartridge:
    """A result becomes a reusable operation, without inventing new primitives."""
    if start.steps or not observed.steps or start.decoder != observed.decoder:
        raise ValueError("Need a finite same-decoder trace from a fresh origin")
    ops = tuple(s.operation for s in observed.steps)
    replayed = route(start, ops, rules)
    if replayed is None or replayed != observed:
        raise ValueError("Cannot compile an unverified or edited synthetic trace")
    return PathCartridge(start.decoder, start.carrier, observed.carrier, ops,
                         tuple(s.rule_pin for s in observed.steps),
                         observed.witness())


def preview_path(start: World, card: PathCartridge,
                 rules: tuple[ReviewedRule, ...]) -> World | None:
    """Re-check every source dependency and step of the generated candidate."""
    if (card.status != "LOCAL_PREVIEW_ONLY" or start.steps
            or start.decoder != card.decoder or start.carrier != card.start_carrier):
        return None
    outcome = route(start, card.operations, rules)
    if (outcome is None or outcome.carrier != card.expected_end
            or tuple(s.rule_pin for s in outcome.steps) != card.source_rule_pins
            or outcome.witness() != card.source_witness):
        return None
    return outcome


# Hidden fixture belongs to the experiment DESIGN / evaluator, not the learner.
# Both contexts share most rules but intentionally disagree on FORK+curve.
# All fields and observations are synthetic, chosen before inspection.
SIMULATOR = {
    ("A", "POINT", "extend"): "AXIS",
    ("A", "AXIS", "branch"): "FORK",
    ("A", "FORK", "curve"): "CUP",
    ("A", "CUP", "close"): "LOOP",
    ("A", "LOOP", "open"): "CUP",
    ("B", "POINT", "extend"): "AXIS",
    ("B", "AXIS", "branch"): "FORK",
    ("B", "FORK", "curve"): "LOOP",
    ("B", "LOOP", "release"): "CUP",
    ("B", "CUP", "close"): "LOOP",
}
KNOWN_PRIMITIVES = frozenset((("A", "POINT", "extend"), ("A", "AXIS", "branch"),
                              ("B", "POINT", "extend"), ("B", "AXIS", "branch")))


def fixture() -> tuple[tuple[Observation, ...], ...]:
    """Separate, explicit TRAIN / VALIDATE / TEST fixtures; no random tuning."""
    buckets: dict[str, list[Observation]] = {s: [] for s in SPLITS}
    for (decoder, carrier, op), output in sorted(SIMULATOR.items()):
        for split in ("TRAIN", "VALIDATE", "TEST"):
            for index in range(2):
                evidence_id = "/".join((split, decoder, carrier, op, str(index)))
                buckets[split].append(Observation(evidence_id, split, decoder,
                                                  carrier, op, output))
    # Deliberate incompatible validation: this spurious proposed rule MUST HOLD.
    for split, output in (("TRAIN", "FORK"), ("VALIDATE", "AXIS"), ("TEST", "AXIS")):
        for index in range(2):
            buckets[split].append(Observation(
                f"{split}/A/CUP/shortcut/{index}", split,
                "A", "CUP", "shortcut", output))
    return tuple(tuple(buckets[k]) for k in ("TRAIN", "VALIDATE", "TEST"))


def fixed_primitive_rows(test: tuple[Observation, ...]) -> dict[str, int]:
    covered = [r for r in test if r.key in KNOWN_PRIMITIVES]
    return {"covered": len(covered), "correct": len(covered), "errors": 0}


def score(rules: tuple[ReviewedRule, ...],
          test: tuple[Observation, ...]) -> dict[str, int]:
    checked_rows(test, "TEST")
    table = {r.key: r.candidate.result for r in rules}
    covered = [r for r in test if r.key in table]
    return {"covered": len(covered),
            "correct": sum(table[r.key] == r.result for r in covered),
            "errors": sum(table[r.key] != r.result for r in covered)}


def context_blind_score(train: tuple[Observation, ...],
                        test: tuple[Observation, ...]) -> dict[str, int]:
    """Matched training data; deliberately discard the decoder coordinate."""
    checked_rows(train, "TRAIN")
    checked_rows(test, "TEST")
    votes: dict[tuple[str, str], Counter[str]] = defaultdict(Counter)
    for row in train:
        votes[row.carrier, row.operation][row.result] += 1
    predictions = {key: sorted(counts.items(), key=lambda x: (-x[1], x[0]))[0][0]
                   for key, counts in votes.items()}
    covered = [r for r in test if (r.carrier, r.operation) in predictions]
    return {"covered": len(covered),
            "correct": sum(predictions[r.carrier, r.operation] == r.result
                           for r in covered),
            "errors": sum(predictions[r.carrier, r.operation] != r.result
                          for r in covered)}


def run_experiment() -> dict[str, object]:
    train, validation, test = fixture()
    candidates = propose(train)
    reviewed = local_review(candidates, train, validation)
    routes = {
        "A": route(World("POINT", "A"),
                   ("extend", "branch", "curve", "close"), reviewed),
        "B": route(World("POINT", "B"),
                   ("extend", "branch", "curve", "release"), reviewed),
    }
    fixed_only = tuple(r for r in reviewed if r.key in KNOWN_PRIMITIVES)
    # The output trace itself is now a checked, reusable macro candidate.
    macro_a = compile_path(World("POINT", "A"), routes["A"], reviewed)
    replay_a = preview_path(World("POINT", "A"), macro_a, reviewed)
    return {
        "experiment": "MOTIF-QC-001",
        "status": "SYNTHETIC_LOCAL_PREVIEW_ONLY",
        "train_count": len(train),
        "validation_count": len(validation),
        "test_count": len(test),
        "proposed": len(candidates),
        "locally_reviewed": len(reviewed),
        "held_candidate_keys": [list(c.key) for c in candidates
                                if c.key not in {r.key for r in reviewed}],
        "frozen_primitive": fixed_primitive_rows(test),
        "typed_lookup": score(reviewed, test),
        "untyped_lookup": context_blind_score(train, test),
        "same_data_classical_table": score(reviewed, test),
        "feedback_route_final": {k: None if v is None else v.carrier
                                 for k, v in routes.items()},
        "generated_macro": {
            "status": macro_a.status,
            "operations": list(macro_a.operations),
            "replay_verified": replay_a == routes["A"],
            "pin_count": len(macro_a.source_rule_pins),
        },
        "frozen_route_final": {
            k: None if route(World("POINT", k), ops, fixed_only) is None
            else route(World("POINT", k), ops, fixed_only).carrier
            for k, ops in (("A", ("extend", "branch", "curve", "close")),
                           ("B", ("extend", "branch", "curve", "release")))},
    }


if __name__ == "__main__":
    print(json.dumps(run_experiment(), sort_keys=True, indent=2))
