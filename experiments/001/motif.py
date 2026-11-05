"""MOTIF-001: a toy, graph-native, non-language world-transition learner.

Proof-of-concept only. Trains on synthetic demonstrated BEFORE/ACTION/AFTER
transitions, induces role-relative graph rewrite motifs, and imagines hypothetical
plans. It neither performs real actions nor identifies human consent.

Python 3.10+, standard library only.
"""
from __future__ import annotations
from collections import Counter, deque
from dataclasses import dataclass
from itertools import product
from typing import FrozenSet, Iterable
import json

Fact = tuple[str, ...]
World = FrozenSet[Fact]


def F(rel: str, *args: str) -> Fact:
    return (rel, *args)


@dataclass(frozen=True)
class Episode:
    action: str
    roles: tuple[str, ...]
    before: World
    after: World
    provenance: str = "SYNTHETIC"


@dataclass(frozen=True)
class Motif:
    action: str
    arity: int
    requires: FrozenSet[Fact]
    adds: FrozenSet[Fact]
    removes: FrozenSet[Fact]
    observations: int

    def friendly(self) -> dict:
        pretty = lambda items: ["(" + ", ".join(x) + ")" for x in sorted(items)]
        return dict(action=self.action, requires=pretty(self.requires),
                    adds=pretty(self.adds), removes=pretty(self.removes),
                    demonstrations=self.observations)


class TransitionLearner:
    """Anti-unifies positive event deltas using action-relative role variables.

    All observations must have complete *before* and *after* worlds in this toy.
    Role identities are provided; independently discovering roles is future work.
    No precondition is inferred from absent facts; closed-world assumption is
    only used inside the explicit synthetic graph during search.
    """
    @staticmethod
    def _normalize(facts: Iterable[Fact], roles: tuple[str, ...]) -> FrozenSet[Fact]:
        if len(roles) != len(set(roles)):
            raise ValueError("Action roles must be distinct in MOTIF-001")
        mapping = {item: f"?{i}" for i, item in enumerate(roles)}
        norm = []
        for fact in facts:
            # Ignore unrelated background facts and avoid accidental names as rules.
            if not any(x in mapping for x in fact[1:]):
                continue
            norm.append(tuple([fact[0]] + [mapping.get(x, x) for x in fact[1:]]))
        return frozenset(norm)

    def fit(self, episodes: Iterable[Episode]) -> dict[str, Motif]:
        grouped = {}
        for ep in episodes:
            if ep.provenance != "SYNTHETIC":
                raise ValueError("Only explicitly marked synthetic fixtures supported here")
            if ep.before == ep.after:
                continue
            before = self._normalize(ep.before, ep.roles)
            adds = self._normalize(ep.after - ep.before, ep.roles)
            removes = self._normalize(ep.before - ep.after, ep.roles)
            # Exclude fixture differences independent of action roles.
            grouped.setdefault((ep.action, len(ep.roles)), []).append((before, adds, removes))
        motifs = {}
        for (name, arity), rows in grouped.items():
            common = lambda i: frozenset.intersection(*(row[i] for row in rows))
            require = common(0)
            add, remove = common(1), common(2)
            if not (add or remove):
                continue
            motifs[name] = Motif(name, arity, require, add, remove, len(rows))
        return motifs


def ground(template: Fact, roles: tuple[str, ...]) -> Fact:
    return tuple(roles[int(x[1:])] if x.startswith('?') and x[1:].isdigit() else x for x in template)


def candidates(state: World, motifs: dict[str, Motif], entities: tuple[str, ...]):
    """Enumerate learned transition affordances; no consent is invented.

    'permits' is an explicitly required observed relation. This toy never
    creates it and cannot verify identity/authority in the outside world.
    """
    for motif in motifs.values():
        for role_assignment in product(entities, repeat=motif.arity):
            # Roles may coincide in new worlds: someone can repair their own bike.
            required = frozenset(ground(f, role_assignment) for f in motif.requires)
            if not required.issubset(state):
                continue
            additions = frozenset(ground(f, role_assignment) for f in motif.adds)
            removals = frozenset(ground(f, role_assignment) for f in motif.removes)
            new_state = (state - removals) | additions
            if new_state != state:
                yield (motif.action, role_assignment, frozenset(new_state))


def value(state: World, initial: World, initial_actors: set[str]) -> int:
    """Illustrative declared objective, NOT a learned universal moral reward."""
    restored = sum(1 for f in state if f[0] == 'usable' and f not in initial)
    newly_skilled = sum(1 for f in state if f[0] == 'skill' and f not in initial
                        and f[1] in initial_actors)
    return restored * 10 + newly_skilled * 4


def search(start: World, motifs: dict[str, Motif], entities: tuple[str, ...], depth=3):
    """Search counterfactual graph forks. Returns best sequence, no execution."""
    actors = {f[1] for f in start if f[0] == 'person'}
    queue = deque([(start, [])])
    visited = {start: 0}
    best = (value(start, start, actors), start, [])
    explored = 0
    while queue:
        world, path = queue.popleft()
        explored += 1
        score = value(world, start, actors)
        # Prefer fewer steps when target value ties.
        if (score, -len(path)) > (best[0], -len(best[2])):
            best = (score, world, path)
        if len(path) >= depth:
            continue
        for name, roles, next_world in candidates(world, motifs, entities):
            if visited.get(next_world, 10**6) <= len(path) + 1:
                continue
            visited[next_world] = len(path) + 1
            queue.append((next_world, path + [(name, roles)]))
    return dict(score=best[0], path=best[2], resulting_world=best[1],
                states_explored=explored, reached_worlds=len(visited))


def make_episode(action, roles, facts, deletes, adds, noise=()):
    before = frozenset(facts) | frozenset(noise)
    after = (before - frozenset(deletes)) | frozenset(adds)
    return Episode(action, roles, before, after)


def synthetic_lessons():
    """Independent invented demonstrations, not historical or user data."""
    episodes = []
    for owner, helper, item, extra in [
        ('Ava', 'Bo', 'cycleA', (F('likes', 'Ava', 'music'),)),
        ('Dee', 'Em', 'cycleB', (F('likes', 'Dee', 'gardens'),)),
        ('Fin', 'Gil', 'cycleC', (F('weather', 'rain'),)),
    ]:
        before = [F('person', owner), F('person', helper), F('bike', item),
                  F('owns', owner, item), F('broken', item),
                  F('skill', helper, 'repair'), F('tool', helper, 'wrench'),
                  F('permits', owner, helper, item)]
        episodes.append(make_episode('repair', (owner, helper, item), before,
                                     [F('broken', item)], [F('usable', item)], extra))
    for teacher, learner, extra in [
        ('Bo', 'Ava', (F('likes', 'Ava', 'tea'),)),
        ('Em', 'Dee', (F('likes', 'Em', 'coffee'),)),
        ('Gil', 'Fin', (F('weather', 'sunny'),)),
    ]:
        before = [F('person', teacher), F('person', learner),
                  F('skill', teacher, 'repair'),
                  F('permits', learner, teacher, 'teaching')]
        episodes.append(make_episode('teach', (teacher, learner), before, [],
                                     [F('skill', learner, 'repair')], extra))
    return episodes


def scenario(permissions=True):
    world = {
        F('person', 'Jo'), F('person', 'Mira'), F('bike', 'bike1'), F('bike', 'bike2'),
        F('owns', 'Jo', 'bike1'), F('owns', 'Jo', 'bike2'),
        F('broken', 'bike1'), F('broken', 'bike2'),
        F('skill', 'Mira', 'repair'),
        F('tool', 'Mira', 'wrench'), F('tool', 'Jo', 'wrench'),
    }
    if permissions:
        world |= {F('permits', 'Jo', 'Mira', 'bike1'),
                  F('permits', 'Jo', 'Mira', 'teaching'),
                  F('permits', 'Jo', 'Jo', 'bike2')}
    return frozenset(world), ('Jo', 'Mira', 'bike1', 'bike2')


def report():
    learner = TransitionLearner()
    rules = learner.fit(synthetic_lessons())
    start, entities = scenario()
    planned = search(start, rules, entities)
    no_permission, _ = scenario(permissions=False)
    blocked = search(no_permission, rules, entities)
    assert len(rules) == 2
    assert len(planned['path']) == 3, planned
    assert ('usable', 'bike1') in planned['resulting_world']
    assert ('usable', 'bike2') in planned['resulting_world']
    assert ('skill', 'Jo', 'repair') in planned['resulting_world']
    assert blocked['path'] == []
    assert all(x not in start for x in [F('usable','bike1'), F('usable','bike2')])
    return {
        'project': 'MOTIF-001', 'status':'toy research proof; entirely synthetic',
        'learned': [m.friendly() for m in rules.values()],
        'new_names_tested': ['Jo', 'Mira', 'bike1', 'bike2'],
        'counterfactual_plan': [{'event': a, 'roles': r} for a, r in planned['path']],
        'objective_score': planned['score'],
        'states_explored': planned['states_explored'],
        'distinct_worlds_reached': planned['reached_worlds'],
        'without_permission': {'plan': blocked['path'], 'score': blocked['score'],
                               'distinct_worlds_reached': blocked['reached_worlds']},
    }


if __name__ == '__main__':
    print(json.dumps(report(), indent=2))
