"""MOTIF-003: perception of *newly reachable actions* in an imagined world.

No neural weights, real-world observation, authorization or external effects.
A pure read-only observer of the MOTIF-002 synthetic rewrite simulator.
"""
from __future__ import annotations
from dataclasses import dataclass
from collections import deque
from typing import Callable


@dataclass(frozen=True)
class Move:
    operator: str
    roles: tuple[str, ...]
    future: frozenset[tuple[str, ...]]


def actions(world, verbs, possibilities: Callable):
    """Actions are identities of hypothetical grounded rewrites, not abilities of real people."""
    moves = [Move(name, tuple(roles), future)
             for name, roles, future in possibilities(world, verbs)]
    return sorted(moves, key=lambda m: (m.operator, m.roles))


def affordance_keys(world, verbs, possibilities):
    return frozenset((m.operator, m.roles) for m in actions(world, verbs, possibilities))


def frontier_after(initial, verbs, possibilities, horizon=2, max_worlds=1000):
    """Bounded, exhaustive simulated futures from one proposed first action.

    Returns (#distinct reached states, truncated?) not external opportunity claims.
    """
    if horizon < 0 or max_worlds < 1:
        raise ValueError('horizon must be >= 0 and max_worlds must be >= 1')
    queue = deque([(initial, 0)])
    seen = {initial}
    truncated = False
    while queue:
        world, depth = queue.popleft()
        if depth >= horizon:
            continue
        for move in actions(world, verbs, possibilities):
            if move.future not in seen:
                if len(seen) >= max_worlds:
                    truncated = True
                    break
                seen.add(move.future)
                queue.append((move.future, depth + 1))
        if truncated:
            break
    return len(seen), truncated


def analyze_first_moves(initial, verbs, possibilities, utility: Callable,
                        horizon=3, max_worlds=1000):
    """Measure new choices and downstream reach after every first move.

    No moral scoring is inferred. The `utility` function is explicitly supplied.
    """
    if horizon < 1:
        raise ValueError('horizon must include at least one move')
    current = affordance_keys(initial, verbs, possibilities)
    baseline_value = utility(initial, initial)
    results = []
    for move in actions(initial, verbs, possibilities):
        newly_available = affordance_keys(move.future, verbs, possibilities) - current
        no_longer_available = current - affordance_keys(move.future, verbs, possibilities)
        reached, truncated = frontier_after(move.future, verbs, possibilities,
                                            horizon=horizon - 1,
                                            max_worlds=max_worlds)
        skill_created = tuple(sorted(f for f in move.future - initial if f[0] == 'skill'))
        results.append({
            'operator': move.operator, 'roles': move.roles,
            'immediate_delta': utility(move.future, initial) - baseline_value,
            'new_affordances': tuple(sorted(newly_available)),
            'lost_affordances': tuple(sorted(no_longer_available)),
            'new_skill_facts': skill_created,
            'reachable_after_first_move': reached,
            'truncated': truncated,
            'future': move.future,
        })
    return results


def select_first_move(rows, priority='new-choices'):
    """Return a recommendation, not an instruction or executed action.

    Both priorities are declared, limited policies, not learned ethics.
    """
    if priority not in ('new-choices', 'immediate'):
        raise ValueError('Unknown declared policy')
    if not rows:
        return None
    if priority == 'new-choices':
        key = lambda x: (len(x['new_affordances']),
                         len(x['new_skill_facts']),
                         x['immediate_delta'],
                         x['reachable_after_first_move'])
    else:
        key = lambda x: (x['immediate_delta'],
                         len(x['new_affordances']),
                         x['reachable_after_first_move'])
    # Stable order under ties. Never treat opportunity count as a human value.
    return max(rows, key=key)


def witness_gap(predicted, independently_observed):
    """Return errors without amending either original snapshot.

    `independently_observed` must come from an external, authorized provenance
    mechanism in a real system. Here it is another synthetic test input.
    """
    return {'unexpected': tuple(sorted(independently_observed - predicted)),
            'missing': tuple(sorted(predicted - independently_observed)),
            'agrees': predicted == independently_observed}


def report(verbs, initial, possibilities, utility):
    rows = analyze_first_moves(initial, verbs, possibilities, utility)
    immediate = select_first_move(rows, 'immediate')
    choices = select_first_move(rows, 'new-choices')
    clean = lambda x: None if x is None else {
        'anonymous_operator': x['operator'],
        'roles': x['roles'],
        'immediate_delta': x['immediate_delta'],
        'new_choice_count': len(x['new_affordances']),
        'new_skill_count': len(x['new_skill_facts']),
        'remaining_horizon_states': x['reachable_after_first_move'],
        'truncated': x['truncated']}
    return {
        'experiment': 'MOTIF-003',
        'scope': 'counterfactual synthetic world ONLY',
        'candidate_first_moves': len(rows),
        'immediate_first': clean(immediate),
        'capability_first': clean(choices),
        'different_first_moves': (
            immediate is not None and choices is not None
            and (immediate['operator'],immediate['roles']) !=
                (choices['operator'],choices['roles'])),
    }


def run_demo():
    # No import dependency while the metric module is being tested in isolation.
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / '002'))
    from motif002 import induce, lessons, scene, possibilities, utility
    return report(induce(lessons()), scene(), possibilities, utility)


if __name__ == '__main__':
    import json
    print(json.dumps(run_demo(), indent=2))
