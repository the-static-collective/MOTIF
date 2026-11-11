"""FIRE-001: bounded cognitive-combustion scheduling over synthetic inquiry.

All questions, follow-up links and sources are engineer-authored/generated fixtures.
The scheduler receives public task metadata and returned source receipts, NEVER
hidden ground truth. The oracle only certifies (or rejects) attempted claims.
No external effects, arbitrary code execution, or real-world permissions.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from random import Random
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / '003'))
from affordance import affordance_keys  # Actual original MOTIF-003 observer.


@dataclass(frozen=True)
class Question:
    key: str
    value: int
    evidence_need: int
    heat_need: int
    source_count: int
    children: tuple[str, ...] = ()


@dataclass(frozen=True)
class Receipt:
    question: str
    origin: str
    answer: bool


@dataclass(frozen=True)
class Owner:
    """Independent synthetic source/oracle seam, not exposed to policies."""
    truth: dict[str, bool]
    reports: dict[str, tuple[bool, ...]]

    def observe(self, key: str, index: int) -> Receipt:
        return Receipt(key, f'synthetic:{key}:origin:{index}', self.reports[key][index])

    def verify(self, key: str, guess: bool) -> bool:
        return self.truth[key] is guess


def make_world(seed: int) -> tuple[dict[str, Question], Owner]:
    rng = Random(seed)
    children: dict[str, list[str]] = {f'Q{i}': [] for i in range(8)}
    for i in range(4, 8):
        children[f'Q{rng.randrange(4)}'].append(f'Q{i}')
    questions = {}
    truth = {}
    reports = {}
    for i in range(8):
        key = f'Q{i}'
        need = rng.choice((1, 3, 3, 5))
        count = max(0, need + rng.choice((-2, 0, 0, 1, 2)))
        questions[key] = Question(key, rng.randint(1, 7), need,
                                  rng.randint(1, 3), count,
                                  tuple(children[key]))
        truth[key] = bool(rng.getrandbits(1))
        reports[key] = tuple(truth[key] if rng.random() < .82 else not truth[key]
                             for _ in range(count))
    return questions, Owner(truth, reports)


def hypothetical_actions(world: frozenset, verbs, possibilities=None):
    """Only a read-only *hypothetical* discovery, never a certification."""
    for edge in sorted(world):
        if edge[0] != 'unlocked':
            continue
        key = edge[1]
        if ('finished', key) not in world:
            yield 'inquire', (key,), world | {('finished', key)}


def new_affordances(questions: dict[str, Question], unlocked: set[str],
                    finished: set[str], key: str) -> int:
    """Original MOTIF-003 affordance_keys: count *potential* new inquiries."""
    before = frozenset({('unlocked', q) for q in unlocked} |
                       {('finished', q) for q in finished})
    after = before | {('finished', key)} | {
        ('unlocked', child) for child in questions[key].children}
    prior = affordance_keys(before, None, hypothetical_actions)
    future = affordance_keys(after, None, hypothetical_actions)
    return len(future - prior)


@dataclass(frozen=True)
class PublicView:
    """Only source receipts and public metadata; never owner truth/reports."""
    questions: dict[str, Question]
    budget: int
    spent: int
    unlocked: frozenset[str]
    finished: frozenset[str]
    observed: dict[str, tuple[Receipt, ...]]
    heat: dict[str, int]
    eligible: tuple[str, ...]
    remaining: dict[str, int]


@dataclass
class Furnace:
    questions: dict[str, Question]
    owner: Owner
    budget: int = 24
    unlocked: set[str] = field(default_factory=lambda: {f'Q{i}' for i in range(4)})
    observed: dict[str, list[Receipt]] = field(default_factory=dict)
    heat: dict[str, int] = field(default_factory=dict)
    finished: set[str] = field(default_factory=set)
    failed: set[str] = field(default_factory=set)
    history: list[dict] = field(default_factory=list)
    score: int = 0
    false_attempts: int = 0
    spent: int = 0

    def next_action(self, key: str) -> str | None:
        if key not in self.unlocked or key in self.finished or key in self.failed:
            return None
        question = self.questions[key]
        if len(self.observed.get(key, [])) < question.evidence_need:
            return ('observe' if question.source_count >
                    len(self.observed.get(key, [])) else None)
        if self.heat.get(key, 0) < question.heat_need:
            return 'reason'
        return 'verify'

    def remaining_cost(self, key: str) -> int:
        q = self.questions[key]
        return (max(0, q.evidence_need - len(self.observed.get(key, []))) +
                max(0, q.heat_need - self.heat.get(key, 0)) + 1)

    def eligible(self) -> list[str]:
        """Require remaining independent sources and sufficient total budget."""
        result = []
        for key in sorted(self.unlocked):
            q = self.questions[key]
            if (self.next_action(key) is not None and
                q.source_count >= q.evidence_need and
                self.remaining_cost(key) <= self.budget - self.spent):
                result.append(key)
        return result

    def public_view(self) -> PublicView:
        return PublicView(self.questions, self.budget, self.spent,
                          frozenset(self.unlocked), frozenset(self.finished),
                          {k: tuple(v) for k, v in self.observed.items()},
                          dict(self.heat), tuple(self.eligible()),
                          {key: self.remaining_cost(key) for key in self.eligible()})

    def apply(self, key: str) -> dict:
        if self.spent >= self.budget:
            raise ValueError('Resource limit exhausted')
        action = self.next_action(key)
        if action is None:
            raise ValueError('Unreachable, completed, or source-starved question')
        q = self.questions[key]
        receipt = {'step': self.spent + 1, 'question': key, 'action': action}
        if action == 'observe':
            index = len(self.observed.get(key, []))
            record = self.owner.observe(key, index)
            if record.question != key or any(x.origin == record.origin
                                              for x in self.observed.get(key, [])):
                raise ValueError('Nonindependent or malformed source receipt')
            self.observed.setdefault(key, []).append(record)
            receipt.update(origin=record.origin, answer=record.answer)
        elif action == 'reason':
            self.heat[key] = self.heat.get(key, 0) + 1
        else:
            records = self.observed[key]
            votes = sum(x.answer for x in records)
            guess = votes > len(records) // 2
            correct = self.owner.verify(key, guess)
            receipt.update(guess=guess, certified=correct)
            if correct:
                self.finished.add(key)
                self.score += q.value
                self.unlocked.update(q.children)
                receipt['new_questions'] = list(q.children)
            else:
                self.failed.add(key)
                self.false_attempts += 1
        self.spent += 1
        self.history.append(receipt)
        return receipt


def select(view: PublicView, policy: str, spark_weight: float = 0.) -> str | None:
    candidates = view.eligible
    if not candidates:
        return None
    questions = view.questions
    def priority(key):
        q = questions[key]
        cost = view.remaining[key]
        pending = q.evidence_need - len(view.observed.get(key, []))
        unlocked_delta = new_affordances(questions, set(view.unlocked),
                                          set(view.finished), key)
        child_value = sum(questions[c].value for c in q.children
                          if c not in view.unlocked)
        if policy == 'value':
            return (q.value, -cost, key)
        if policy == 'information':
            # Naive but legal uncertainty from existing receipts, not hidden truth.
            observations = view.observed.get(key, [])
            if observations:
                certainty = abs(sum(x.answer for x in observations) /
                                len(observations) - .5) * 2
            else:
                certainty = 0.
            return ((1. - certainty) / (1. + len(observations)),
                    q.value / cost, key)
        if policy == 'ratio':
            return (q.value / cost, -cost, key)
        if policy == 'fire':
            # Synthetic epistemic resource balance: fuel=potential payoff,
            # oxygen=independent sources available, heat=work budget sufficiency.
            potential = q.value + spark_weight * child_value * bool(unlocked_delta)
            fuel = min(1., potential / 10.)
            source_left = q.source_count - len(view.observed.get(key, []))
            oxygen = (source_left / (source_left + pending)) if pending else 1.
            budget_left = view.budget - view.spent
            heat_work = q.heat_need - view.heat.get(key, 0)
            heat = (budget_left - cost + 1) / (budget_left + heat_work + 1)
            burn = min(fuel, oxygen, heat)
            return (burn * potential / cost, -cost, key)
        raise ValueError('Unknown policy')
    return max(candidates, key=priority)


def run(seed: int, policy: str, spark_weight: float = 0., budget: int = 24) -> dict:
    questions, owner = make_world(seed)
    furnace = Furnace(questions, owner, budget=budget)
    while furnace.spent < budget:
        key = select(furnace.public_view(), policy, spark_weight)
        if key is None:
            break  # Extinguish, do not hallucinate fresh oxygen or fuel.
        furnace.apply(key)
    return {
        'seed': seed, 'policy': policy, 'weight': spark_weight,
        'verified_value': furnace.score, 'correct_tasks': len(furnace.finished),
        'false_attempts': furnace.false_attempts,
        'steps': furnace.spent,
        'unlocked': len(furnace.unlocked),
        'embers': sum(q.source_count < q.evidence_need for q in questions.values()),
        'history': furnace.history,
    }
