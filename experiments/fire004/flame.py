"""FIRE-004: The Witness of the Flame.

Prequential self-monitoring of evidence methods against strong classical online
learning baselines. Every policy receives only public reports/attestations,
makes a forecast, then learns from a separately issued synthetic label receipt.
No external action, real-world authenticated provenance, or self-edited code.
"""
from __future__ import annotations
from dataclasses import dataclass
from math import exp, log
from random import Random
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'fire003'))
from smoke import Report, Attestation, forecast as fire003_forecast

N_STEPS = 96
REGIMES = ('steady', 'abrupt', 'gradual', 'copied', 'compromised', 'transient')
POLICIES = ('fire003', 'pooled_beta', 'discount_beta', 'hmm_slow', 'hmm_fast',
            'hedge', 'fire004')
SWITCH_AT = 48


def clip(x: float, low: float = .0001, high: float = .9999) -> float:
    return max(low, min(high, x))


def sigmoid(x: float) -> float:
    if x >= 0:
        return 1. / (1. + exp(-x))
    e = exp(x)
    return e / (1. + e)


def aggregate(votes: tuple[tuple[str, bool], ...], accuracies: dict[str, float]) -> float:
    odds = sum((1 if bit else -1) * log(clip(accuracies[root], .03, .97) /
                                          (1 - clip(accuracies[root], .03, .97)))
               for root, bit in votes)
    return clip(sigmoid(odds))


@dataclass(frozen=True)
class PublicEpisode:
    step: int
    reports: tuple[Report, ...]
    attestation: Attestation


@dataclass(frozen=True)
class VerifiedLabel:
    step: int
    actual: bool
    authority: str = "synthetic-independent-result-gate"


@dataclass(frozen=True)
class ToyWorld:
    regime: str
    public: tuple[PublicEpisode, ...]
    hidden_labels: tuple[bool, ...]
    hidden_rates: tuple[dict[str, float], ...]
    hidden_origins: tuple[tuple[str, ...], ...]

    def view(self, step: int) -> PublicEpisode:
        return self.public[step]

    def verify(self, step: int) -> VerifiedLabel:
        # ONLY called after forecasts have been recorded in benchmark.run().
        return VerifiedLabel(step, self.hidden_labels[step])


def source_rates(regime: str, step: int) -> dict[str, float]:
    if regime in ('copied', 'compromised'):
        return {'root-0': .76, 'root-1': .76, 'root-2': .76}
    if regime == 'abrupt':
        return {f'root-{i}': (.88 if step < SWITCH_AT else .12)
                if i < 3 else .72 for i in range(5)}
    if regime == 'gradual':
        fidelity = (.90 if step < 24 else .15 if step >= 80
                    else .90 - .75 * (step - 24) / 56.)
        return {f'root-{i}': fidelity if i < 3 else .68 for i in range(5)}
    if regime == 'transient':
        fidelity = .12 if step in (48, 49) else .78
        return {f'root-{i}': fidelity for i in range(5)}
    return {f'root-{i}': .78 for i in range(5)}


def make_world(seed: int, regime: str) -> ToyWorld:
    if regime not in REGIMES:
        raise ValueError('Unknown synthetic regime')
    rng = Random(seed * 1009 + REGIMES.index(regime) * 13_337)
    cases, labels, rates_by_step, true_origins = [], [], [], []
    for step in range(N_STEPS):
        truth = bool(rng.getrandbits(1))
        rates = source_rates(regime, step)
        if regime in ('copied', 'compromised'):
            roots = ('root-0', 'root-0', 'root-0', 'root-1', 'root-2')
        else:
            roots = tuple(f'root-{i}' for i in range(5))
        actual_reports = {root: truth if rng.random() < rate else not truth
                          for root, rate in rates.items()}
        claims = tuple(Report(f'T{step}', f'claim-{i}', actual_reports[root])
                       for i, root in enumerate(roots))
        audited = (tuple(f'root-{i}' for i in range(5))
                   if regime == 'compromised' else roots)
        cases.append(PublicEpisode(step, claims, Attestation('VERIFIED', audited)))
        labels.append(truth)
        rates_by_step.append(rates)
        true_origins.append(roots)
    return ToyWorld(regime, tuple(cases), tuple(labels),
                    tuple(rates_by_step), tuple(true_origins))


def roots_only(case: PublicEpisode) -> tuple[tuple[str, bool], ...]:
    if case.attestation.status != 'VERIFIED':
        raise ValueError('No signed/verified synthetic lineage')
    if len(case.reports) != len(case.attestation.origins):
        raise ValueError('Missing source ancestry')
    mapping = {}
    for receipt, root in zip(case.reports, case.attestation.origins):
        if root in mapping and mapping[root] != receipt.answer:
            raise ValueError('Contradiction within claimed common source')
        mapping[root] = receipt.answer
    return tuple(sorted(mapping.items()))


class Fixed003:
    def predict(self, case: PublicEpisode) -> float:
        return fire003_forecast(case.reports, case.attestation, .8)['p_true']

    def update(self, case: PublicEpisode, receipt: VerifiedLabel):
        validate_receipt(case, receipt)


def validate_receipt(case: PublicEpisode, receipt: VerifiedLabel):
    if receipt.step != case.step or receipt.authority != 'synthetic-independent-result-gate'             or type(receipt.actual) is not bool:
        raise ValueError('Unverified, stale, or malformed feedback')


class PooledBeta:
    def __init__(self):
        self.a, self.b = 4., 1.

    def predict(self, case: PublicEpisode) -> float:
        votes = roots_only(case)
        p = self.a / (self.a + self.b)
        return aggregate(votes, {root: p for root, _ in votes})

    def update(self, case: PublicEpisode, receipt: VerifiedLabel):
        validate_receipt(case, receipt)
        for _, answer in roots_only(case):
            self.a += int(answer is receipt.actual)
            self.b += int(answer is not receipt.actual)


class DiscountBeta:
    def __init__(self, decay: float = .92):
        self.decay = decay
        self.counts: dict[str, tuple[float, float]] = {}

    def predict(self, case: PublicEpisode) -> float:
        votes = roots_only(case)
        return aggregate(votes, {root: self.counts.get(root, (2.4, .6))[0] /
                                        sum(self.counts.get(root, (2.4, .6)))
                                for root, _ in votes})

    def update(self, case: PublicEpisode, receipt: VerifiedLabel):
        validate_receipt(case, receipt)
        for root, bit in roots_only(case):
            a, b = self.counts.get(root, (2.4, .6))
            a = 2.4 + self.decay * (a - 2.4) + int(bit is receipt.actual)
            b = .6 + self.decay * (b - .6) + int(bit is not receipt.actual)
            self.counts[root] = (a, b)


class BayesianHMM:
    """Exact Bayesian two-state reliability filter per *attested root*."""
    def __init__(self, hazard: float):
        self.hazard = hazard
        self.trust: dict[str, float] = {}

    def predict(self, case: PublicEpisode) -> float:
        votes = roots_only(case)
        return aggregate(votes, {root: .1 + .8 * self.trust.get(root, .85)
                                for root, _ in votes})

    def update(self, case: PublicEpisode, receipt: VerifiedLabel):
        validate_receipt(case, receipt)
        for root, bit in roots_only(case):
            w = self.trust.get(root, .85)
            high_likelihood = .9 if bit is receipt.actual else .1
            low_likelihood = .1 if bit is receipt.actual else .9
            evidence = w * high_likelihood + (1. - w) * low_likelihood
            posterior = (w * high_likelihood / evidence)
            self.trust[root] = ((1. - self.hazard) * posterior +
                                self.hazard * (1. - posterior))


class Hedge:
    """Classical multiplicative-weights expert mixture with prequential labels."""
    def __init__(self, monitor: bool = False):
        self.monitor = monitor
        self.experts = (Fixed003(), BayesianHMM(.005), BayesianHMM(.08),
                        DiscountBeta(.92))
        self.weights = [1. / len(self.experts)] * len(self.experts)
        self.last_preds: tuple[float, ...] | None = None
        self.last_p: float | None = None
        self.ewma_slow = .12
        self.ewma_fast = .12
        self.last_alarm = -20
        self.alarm_steps: list[int] = []

    def predict(self, case: PublicEpisode) -> float:
        preds = tuple(expert.predict(case) for expert in self.experts)
        p = clip(sum(w * x for w, x in zip(self.weights, preds)))
        self.last_preds = preds
        self.last_p = p
        return p

    def update(self, case: PublicEpisode, receipt: VerifiedLabel):
        validate_receipt(case, receipt)
        if self.last_preds is None or self.last_p is None:
            raise ValueError('Cannot learn before forecasting')
        actual = int(receipt.actual)
        # All experts, including unselected ones, see the same independently
        # verified label AFTER they have forecast.
        for expert in self.experts:
            expert.update(case, receipt)
        # Conventional discounted exponential-weighting: keep finite past.
        scores = [(w ** .985) * exp(.7 * log(clip(p if actual else 1 - p)))
                  for w, p in zip(self.weights, self.last_preds)]
        total = sum(scores)
        self.weights = [w / total for w in scores]
        loss = (self.last_p - actual) ** 2
        self.ewma_fast = .60 * self.ewma_fast + .40 * loss
        self.ewma_slow = .98 * self.ewma_slow + .02 * loss
        if self.monitor:
            # Frozen, predeclared surprise alarm; it does not prove actual drift.
            if (case.step - self.last_alarm >= 12 and
                    self.ewma_fast > .19 and
                    self.ewma_fast - self.ewma_slow > .12):
                self.last_alarm = case.step
                self.alarm_steps.append(case.step)
                # A bounded future-only intervention: prefer quickly adjusting
                # experts, never tamper with older observations.
                self.weights = [
                    .50 * self.weights[0] + .50 * .08,
                    .50 * self.weights[1] + .50 * .12,
                    .50 * self.weights[2] + .50 * .55,
                    .50 * self.weights[3] + .50 * .25,
                ]
        self.last_preds, self.last_p = None, None


def construct_models():
    return {'fire003': Fixed003(),
            'pooled_beta': PooledBeta(),
            'discount_beta': DiscountBeta(),
            'hmm_slow': BayesianHMM(.005),
            'hmm_fast': BayesianHMM(.08),
            'hedge': Hedge(False),
            'fire004': Hedge(True)}


def oracle_prediction(w: ToyWorld, step: int) -> float:
    """Privileged evaluation ceiling; forbidden to live policies."""
    case = w.view(step)
    votes = {}
    for report, root in zip(case.reports, w.hidden_origins[step]):
        votes[root] = report.answer
    return aggregate(tuple(sorted(votes.items())), w.hidden_rates[step])


def evaluate(seed: int, regime: str) -> dict:
    w = make_world(seed, regime)
    models = construct_models()
    store = {name: {'brier': 0., 'log_loss': 0., 'high_confidence_wrong': 0,
                    'answered': 0, 'answered_correct': 0,
                    'forecasts': [], 'square_errors': []} for name in (*POLICIES, 'oracle')}
    for step in range(N_STEPS):
        case = w.view(step)
        predictions = {name: model.predict(case) for name, model in models.items()}
        predictions['oracle'] = oracle_prediction(w, step)
        receipt = w.verify(step)
        actual = int(receipt.actual)
        for name, prob in predictions.items():
            row = store[name]
            p = clip(prob)
            row['brier'] += (p - actual) ** 2
            row['square_errors'].append((p - actual) ** 2)
            row['log_loss'] -= log(p if actual else 1. - p)
            if max(p, 1. - p) >= .95 and (p >= .5) != receipt.actual:
                row['high_confidence_wrong'] += 1
            if max(p, 1. - p) >= .70:
                row['answered'] += 1
                row['answered_correct'] += int((p >= .5) == receipt.actual)
            row['forecasts'].append(round(p, 8))
        for model in models.values():
            model.update(case, receipt)
    output = {}
    for name, row in store.items():
        row['brier'] = round(row['brier'] / N_STEPS, 8)
        row['early_post_shift_brier'] = round(sum(row['square_errors'][48:64]) / 16, 8)
        row['late_post_shift_brier'] = round(sum(row['square_errors'][80:96]) / 16, 8)
        row.pop('square_errors')
        row['log_loss'] = round(row['log_loss'] / N_STEPS, 8)
        row['coverage'] = round(row['answered'] / N_STEPS, 8)
        row['selective_accuracy'] = round(row['answered_correct'] / row['answered'], 8)                                     if row['answered'] else None
        row['overconfident_errors'] = row.pop('high_confidence_wrong')
        row.pop('answered_correct')
        row.pop('answered')
        row.pop('forecasts')
        row.pop('alarms')
        output[name] = row
    output['fire004']['alerts'] = list(models['fire004'].alarm_steps)
    output['hedge']['alerts'] = list(models['hedge'].alarm_steps)
    return output
