"""MOTIF QC-002 — discover graph-edit operators from unnamed before/after pairs.

All worlds, cues, receipts, evaluations and goals are synthetic. A source
condition key does NOT contain the operation's meaning: the learner must
derive the graph edit. The bounded grammar admits one fresh vertex and
anchor-local edits only. This is classical symbolic program induction,
not quantum computing, an unconstrained invention engine, or an action tool.
"""
from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass
from hashlib import sha256
from itertools import combinations, permutations, product
import json

PROVENANCE = "SYNTHETIC_QC002"
SPLITS = frozenset(("TRAIN", "VALIDATE", "TEST"))
STATUS = "LOCAL_PREVIEW_ONLY"
# Opaque laboratory cues, NOT semantically labeled operator examples.
CUE_BRACE = "signal-17"
CUE_SPLIT = "signal-42"
CUE_DECOY = "signal-99"


def checksum(value) -> str:
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def edge(a: str, b: str) -> tuple[str, str]:
    if not isinstance(a, str) or not isinstance(b, str) or not a or not b or a == b:
        raise ValueError("Edges require two distinct nonempty vertices")
    return tuple(sorted((a, b)))


@dataclass(frozen=True)
class Graph:
    vertices: frozenset[str]
    edges: frozenset[tuple[str, str]]

    def __post_init__(self):
        if not self.vertices or any(not isinstance(n, str) or not n for n in self.vertices):
            raise ValueError("Bad vertices")
        for e in self.edges:
            if len(e) != 2 or not set(e).issubset(self.vertices) or e != edge(*e):
                raise ValueError("Edges must be undirected, canonical and internal")

    @staticmethod
    def of(vertices, edges) -> "Graph":
        return Graph(frozenset(vertices), frozenset(edge(a, b) for a, b in edges))

    def receipt(self) -> str:
        return checksum((sorted(self.vertices), sorted(self.edges)))


@dataclass(frozen=True)
class Episode:
    evidence_id: str
    split: str
    signal: str
    anchors: tuple[str, str]
    before: Graph
    after: Graph
    provenance: str = PROVENANCE

    def validate(self, expected_split: str) -> None:
        if (self.provenance != PROVENANCE or self.split != expected_split or
                not self.signal or not self.evidence_id or
                len(self.anchors) != 2 or self.anchors[0] == self.anchors[1] or
                not set(self.anchors).issubset(self.before.vertices)):
            raise ValueError("Unverified or malformed synthetic observation")


@dataclass(frozen=True)
class Edit:
    """Inferred anonymous local rewrite: NO predefined action-name mapping."""
    anchor_link_present: bool
    remove_link: bool
    # Each pair contains symbolic roles A, B, N (one fresh vertex).
    add_edges: tuple[tuple[str, str], ...]

    def __post_init__(self):
        allowed = {("A", "B"), ("A", "N"), ("B", "N")}
        if (self.remove_link and not self.anchor_link_present or
                any(e not in allowed for e in self.add_edges) or
                len(set(self.add_edges)) != len(self.add_edges) or
                not any("N" in e for e in self.add_edges)):
            raise ValueError("Invalid anchored graph rewrite")


def extract(episode: Episode) -> Edit:
    """Infer edit from two actual graphs, independent of variable spellings."""
    episode.validate(episode.split)
    before, after = episode.before, episode.after
    a, b = episode.anchors
    new = after.vertices - before.vertices
    if not before.vertices.issubset(after.vertices) or len(new) != 1:
        raise ValueError("Only exactly one newly created vertex supported")
    n = next(iter(new))
    removed = before.edges - after.edges
    added = after.edges - before.edges
    ab = edge(a, b)
    if not removed.issubset({ab}):
        raise ValueError("Changed unrelated existing edges")
    lookup = {edge(a, b): ("A", "B"), edge(a, n): ("A", "N"),
              edge(b, n): ("B", "N")}
    if not added.issubset(lookup):
        raise ValueError("Changed edges outside the declared local aperture")
    role_edges = tuple(sorted(lookup[e] for e in added))
    return Edit(ab in before.edges, ab in removed, role_edges)


@dataclass(frozen=True)
class Candidate:
    signal: str
    edit: Edit
    support: int
    training_digest: str
    status: str = "CANDIDATE_ONLY"


@dataclass(frozen=True)
class ReviewedRule:
    candidate: Candidate
    validation_count: int
    validation_digest: str
    status: str = STATUS

    @property
    def signal(self) -> str:
        return self.candidate.signal

    @property
    def pin(self) -> str:
        e = self.candidate.edit
        return checksum((self.signal, e.anchor_link_present, e.remove_link,
                         e.add_edges, self.candidate.training_digest,
                         self.validation_digest))


def check_batch(rows: tuple[Episode, ...], split: str) -> None:
    if len({r.evidence_id for r in rows}) != len(rows):
        raise ValueError("Repeated synthetic evidence ID")
    for r in rows:
        r.validate(split)


def evidence_digest(rows: tuple[Episode, ...]) -> str:
    return checksum(sorted((r.evidence_id, r.signal, r.anchors,
                            r.before.receipt(), r.after.receipt()) for r in rows))


def induce(train: tuple[Episode, ...], minimum: int = 3) -> tuple[Candidate, ...]:
    if minimum < 2:
        raise ValueError("Trivial single-demonstration rule prohibited")
    check_batch(train, "TRAIN")
    by_signal = defaultdict(list)
    for episode in train:
        by_signal[episode.signal].append(episode)
    candidates = []
    for signal, rows in sorted(by_signal.items()):
        if len(rows) < minimum:
            continue
        try:
            signatures = {extract(row) for row in rows}
        except ValueError:
            # Invalid/mixed evidence is NOT silently trimmed.
            continue
        if len(signatures) != 1:
            continue
        edit = next(iter(signatures))
        candidates.append(Candidate(signal, edit, len(rows),
                                    evidence_digest(tuple(rows))))
    return tuple(candidates)


def review(candidates: tuple[Candidate, ...],
           train: tuple[Episode, ...],
           validation: tuple[Episode, ...],
           minimum: int = 2) -> tuple[ReviewedRule, ...]:
    check_batch(train, "TRAIN")
    check_batch(validation, "VALIDATE")
    if {r.evidence_id for r in train} & {r.evidence_id for r in validation}:
        raise ValueError("Cross-split evidence reuse")
    original = {c.signal: c for c in induce(train)}
    if len({c.signal for c in candidates}) != len(candidates):
        raise ValueError("Duplicate source cue")
    groups = defaultdict(list)
    for row in validation:
        groups[row.signal].append(row)
    admitted = []
    for candidate in candidates:
        if candidate.status != "CANDIDATE_ONLY" or original.get(candidate.signal) != candidate:
            raise ValueError("Candidate envelope not reconstructible from TRAIN")
        rows = tuple(groups.get(candidate.signal, ()))
        if len(rows) < minimum:
            continue
        try:
            if any(extract(r) != candidate.edit for r in rows):
                continue
        except ValueError:
            continue
        admitted.append(ReviewedRule(candidate, len(rows), evidence_digest(rows)))
    return tuple(admitted)


def fresh(graph: Graph) -> str:
    index = 0
    while f"generated-{index}" in graph.vertices:
        index += 1
    return f"generated-{index}"


def rewrite(graph: Graph, anchors: tuple[str, str], edit: Edit) -> Graph | None:
    """Pure graph rewrite; never touches outside-world objects."""
    if (len(anchors) != 2 or anchors[0] == anchors[1] or
            not set(anchors).issubset(graph.vertices)):
        return None
    a, b = anchors
    ab = edge(a, b)
    if (ab in graph.edges) != edit.anchor_link_present:
        return None
    n = fresh(graph)
    binding = {"A": a, "B": b, "N": n}
    removed = {ab} if edit.remove_link else set()
    added = {edge(binding[x], binding[y]) for x, y in edit.add_edges}
    output = Graph.of(graph.vertices | {n}, (graph.edges - removed) | added)
    if output == graph:
        return None
    return output


@dataclass(frozen=True)
class Step:
    signal: str
    anchors: tuple[str, str]
    source_pin: str
    before_hash: str
    after_hash: str


@dataclass(frozen=True)
class World:
    graph: Graph
    history: tuple[Step, ...] = ()

    def projection(self) -> str:
        return self.graph.receipt()

    def witness(self) -> str:
        return checksum((self.graph.receipt(), [s.__dict__ for s in self.history]))


def preview(world: World, cue: str, anchors: tuple[str, str],
            rules: tuple[ReviewedRule, ...]) -> World | None:
    if any(r.status != STATUS or r.candidate.status != "CANDIDATE_ONLY" for r in rules):
        raise ValueError("Unauthorized rule status")
    if len({r.signal for r in rules}) != len(rules):
        raise ValueError("Ambiguous signal catalog")
    matching = [r for r in rules if r.signal == cue]
    if not matching:
        return None
    rule = matching[0]
    result = rewrite(world.graph, anchors, rule.candidate.edit)
    if result is None:
        return None
    step = Step(cue, anchors, rule.pin, world.graph.receipt(), result.receipt())
    return World(result, world.history + (step,))


def cycle4(graph: Graph) -> bool:
    """Four-cycle must be induced: the two chords are absent."""
    for quartet in combinations(sorted(graph.vertices), 4):
        for path in permutations(quartet):
            if all(edge(path[i], path[(i+1) % 4]) in graph.edges for i in range(4)):
                if (edge(path[0], path[2]) not in graph.edges and
                        edge(path[1], path[3]) not in graph.edges):
                    return True
    return False


@dataclass(frozen=True)
class Plan:
    outcome: World | None
    depth: int | None
    explored: int
    status: str = "RESEARCH_PREVIEW_ONLY"


def search(seed: World, rules: tuple[ReviewedRule, ...],
           max_depth: int = 2, max_states: int = 500) -> Plan:
    """Short finite search; no optimizer is granted action permissions."""
    if max_depth < 0 or max_states < 1:
        raise ValueError("Invalid budget")
    queue = deque([(seed, 0)])
    visited = {seed.graph}
    examined = 0
    while queue:
        if examined >= max_states:
            return Plan(None, None, examined, "HOLD_STATE_BUDGET")
        world, depth = queue.popleft()
        examined += 1
        if cycle4(world.graph):
            return Plan(world, depth, examined)
        if depth >= max_depth:
            continue
        # Anchors are a declared local aperture; the learner does not know which
        # cue constructs a triangle or which subdivides an edge.
        for a, b in combinations(sorted(world.graph.vertices), 2):
            for rule in sorted(rules, key=lambda x: x.signal):
                next_world = preview(world, rule.signal, (a, b), rules)
                if next_world is None or next_world.graph in visited:
                    continue
                visited.add(next_world.graph)
                queue.append((next_world, depth + 1))
    return Plan(None, None, examined, "HOLD_UNREACHABLE")


def exact_classical_control(seed: Graph, rules: tuple[ReviewedRule, ...],
                            depth: int = 2) -> int | None:
    """Separate exhaustive depth-limited recursive enumerator (not a new algo)."""
    if cycle4(seed):
        return 0
    def walk(graph, remaining):
        if remaining == 0:
            return False
        for pair in combinations(sorted(graph.vertices), 2):
            for r in rules:
                nxt = rewrite(graph, pair, r.candidate.edit)
                if nxt is not None and (cycle4(nxt) or walk(nxt, remaining-1)):
                    return True
        return False
    for length in range(1, depth+1):
        if walk(seed, length):
            return length
    return None


@dataclass(frozen=True)
class Macro:
    initial_hash: str
    steps: tuple[Step, ...]
    expected_projection: str
    expected_witness: str
    status: str = STATUS


def compile_macro(start: World, outcome: World,
                  rules: tuple[ReviewedRule, ...]) -> Macro:
    if start.history or not outcome.history:
        raise ValueError("Macro needs a fresh origin and real trace")
    replay = start
    for step in outcome.history:
        if replay.graph.receipt() != step.before_hash:
            raise ValueError("Unverified intermediate state")
        replay = preview(replay, step.signal, step.anchors, rules)
        if (replay is None or replay.graph.receipt() != step.after_hash or
                replay.history[-1] != step):
            raise ValueError("Unpinned transition in macro training")
    if replay != outcome:
        raise ValueError("Cannot promote altered output as a macro")
    return Macro(start.graph.receipt(), outcome.history,
                 outcome.projection(), outcome.witness())


def replay_macro(start: World, macro: Macro,
                 rules: tuple[ReviewedRule, ...]) -> World | None:
    if macro.status != STATUS or start.history or start.graph.receipt() != macro.initial_hash:
        return None
    current = start
    for step in macro.steps:
        if current.graph.receipt() != step.before_hash:
            return None
        current = preview(current, step.signal, step.anchors, rules)
        if (current is None or current.graph.receipt() != step.after_hash or
                current.history[-1] != step):
            return None
    if (current.projection() != macro.expected_projection or
            current.witness() != macro.expected_witness):
        return None
    return current


# Hidden evaluator fixtures. These rules are NOT imported by induce/review.
def specimen(prefix: str, extras: int) -> tuple[Graph, tuple[str, str]]:
    a, b = f"{prefix}_a", f"{prefix}_b"
    rest = [f"{prefix}_d{i}" for i in range(extras)]
    vertices = {a, b, *rest}
    # A graph with an unrelated path grows in complexity with the split.
    chain = [edge(a, rest[0])] + [
        edge(rest[i-1], rest[i]) for i in range(1, extras)
    ] if extras else []
    return Graph.of(vertices, [edge(a, b), *chain]), (a, b)


def controlled_episode(split: str, cue: str, extras: int) -> Episode:
    prefix = f"{split}/{cue}/{extras}"
    before, anchors = specimen(prefix, extras)
    a, b = anchors
    n = f"{prefix}_made"
    # The oracle alone knows the semantic effects:
    if cue == CUE_SPLIT:
        after = Graph.of(before.vertices | {n},
                         (before.edges - {edge(a, b)}) | {edge(a, n), edge(b, n)})
    elif cue == CUE_BRACE or (cue == CUE_DECOY and split != "TRAIN"):
        after = Graph.of(before.vertices | {n},
                         before.edges | {edge(a, n), edge(b, n)})
    elif cue == CUE_DECOY:
        after = Graph.of(before.vertices | {n}, before.edges | {edge(a, n)})
    else:
        raise ValueError("Unknown evaluator signal")
    return Episode(prefix, split, cue, anchors, before, after)


def fixture():
    buckets = {}
    for split, extras in (("TRAIN", range(1, 4)),
                          ("VALIDATE", range(4, 6)),
                          ("TEST", range(6, 12))):
        buckets[split] = tuple(controlled_episode(split, cue, i)
                               for cue in (CUE_BRACE, CUE_SPLIT, CUE_DECOY)
                               for i in extras)
    return buckets["TRAIN"], buckets["VALIDATE"], buckets["TEST"]


def score(rules: tuple[ReviewedRule, ...], test: tuple[Episode, ...]):
    check_batch(test, "TEST")
    covered = correct = 0
    for episode in test:
        result = preview(World(episode.before), episode.signal,
                         episode.anchors, rules)
        if result is None:
            continue
        covered += 1
        correct += int(result.graph == episode.after)
    return {"covered": covered, "correct": correct, "wrong": covered-correct,
            "held": len(test)-covered}


def named_graph_memorization(train: tuple[Episode, ...],
                             test: tuple[Episode, ...]) -> dict[str, int]:
    """Strong exact-input memory baseline; no schema generalization."""
    known = {(r.signal, r.anchors, r.before.receipt()): r.after for r in train}
    covered = sum((r.signal, r.anchors, r.before.receipt()) in known for r in test)
    return {"covered": covered, "held": len(test)-covered}


def experiment_report() -> dict:
    train, valid, test = fixture()
    candidates = induce(train)
    approved = review(candidates, train, valid)
    seed = World(Graph.of({"root0", "root1"}, {edge("root0", "root1")}))
    result = search(seed, approved)
    if result.outcome is None:
        macro_report = {"composed": False}
    else:
        card = compile_macro(seed, result.outcome, approved)
        macro_report = {
            "composed": True,
            "macro_step_count": len(card.steps),
            "replayed": replay_macro(seed, card, approved) == result.outcome,
            "source_pins": [s.source_pin for s in card.steps],
        }
    return {
        "experiment": "MOTIF-QC-002",
        "status": "SYNTHETIC_LOCAL_RESEARCH_ONLY",
        "training_examples": len(train),
        "validation_examples": len(valid),
        "frozen_test_examples": len(test),
        "discovered_effects": len(candidates),
        "locally_validated_effects": len(approved),
        "held_signals": sorted({c.signal for c in candidates}-
                               {r.signal for r in approved}),
        "heldout_graph_prediction": score(approved, test),
        "exact_graph_memorization": named_graph_memorization(train, test),
        "new_topology_goal": "INDUCED_4_CYCLE",
        "goal_seen_in_training_outputs": any(cycle4(r.after) for r in train),
        "goal_seen_in_validation_outputs": any(cycle4(r.after) for r in valid),
        "goal_seen_in_test_outputs": any(cycle4(r.after) for r in test),
        "planned_depth": result.depth,
        "planned_status": result.status,
        "states_examined": result.explored,
        "exact_classical_minimum_depth": exact_classical_control(seed.graph, approved),
        "macro": macro_report,
        "external_actions": 0,
    }


if __name__ == "__main__":
    print(json.dumps(experiment_report(), indent=2, sort_keys=True))
