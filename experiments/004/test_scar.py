"""Tests for MOTIF-004: synthetic negative observations and conservative revision."""
import unittest
from dataclasses import replace
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "002"))
from motif002 import F, induce, lessons
from scar import (Attempt, ScarJournal, revise, extras, forecast, examples, run_demo)


class ScarTests(unittest.TestCase):
    def setUp(self):
        self.verbs = induce(lessons())
        self.verb = next(v for v in self.verbs.values() if F('usable', '?0') in v.adds)
        self.cases = examples(self.verb)

    def train(self):
        ledger = ScarJournal()
        for case in self.cases:
            ledger.record(case, self.verbs)
        return ledger

    def test_noop_is_a_recorded_counterexample(self):
        ledger = self.train()
        noops = [x for x in ledger.events if x.outcome == 'no_observed_change']
        self.assertEqual(len(noops), 4)
        self.assertTrue(all(F('usable', x.roles[0]) in x.missing_predicted for x in noops))
        self.assertTrue(all(F('broken', x.roles[0]) in x.unexpected_observed for x in noops))

    def test_induces_one_role_relative_discriminator(self):
        model = revise(self.verb.id, self.train().events)
        self.assertEqual(model.status, 'CONTEXT_CORRELATION')
        self.assertEqual(model.discriminators, frozenset({F('part', '?0', 'brake_kit')}))
        self.assertEqual((model.successes, model.no_effect), (4, 4))

    def test_holdout_separation_and_identity_generalization(self):
        model = revise(self.verb.id, self.train().events)
        fresh = examples(self.verb, positive=3, negative=3, prefix='unseen')
        for case in fresh:
            guess = forecast(model, case.before, self.verb, case.roles)
            expected = 'EFFECT_HYPOTHESIS' if case.observed_after != case.before else 'NO_EFFECT_RISK'
            self.assertEqual(guess, expected)

    def test_training_order_independence(self):
        a = revise(self.verb.id, self.train().events)
        b = ScarJournal()
        for case in reversed(self.cases):
            b.record(case, self.verbs)
        self.assertEqual(a, revise(self.verb.id, b.events))

    def test_sparse_and_one_sided_examples_abstain(self):
        ledger = ScarJournal()
        for case in self.cases[:2]:
            ledger.record(case, self.verbs)
        self.assertEqual(revise(self.verb.id, ledger.events).status, 'ABSTAIN')

    def test_spurious_second_separator_abstains(self):
        extra = []
        for case in self.cases:
            # Perfectly confounded but irrelevant to synthetic outcome.
            prior = set(case.before)
            if case.observed_after != case.before:
                prior.add(F('paint', case.roles[0], 'blue'))
            change = prior - set(case.before)
            observed = frozenset((set(case.observed_after) | change))
            extra.append(replace(case, before=frozenset(prior), observed_after=observed))
        ledger = ScarJournal()
        for case in extra:
            ledger.record(case, self.verbs)
        self.assertEqual(revise(self.verb.id, ledger.events).status, 'ABSTAIN')

    def test_contradictory_success_invalidates_separation(self):
        ledger = self.train()
        sample = examples(self.verb, positive=0, negative=1, prefix='contrary')[0]
        attempted = replace(sample, observed_after=frozenset(
            (set(sample.before) - {F('broken', sample.roles[0])}) |
            {F('usable', sample.roles[0])}))
        ledger.record(attempted, self.verbs)
        self.assertEqual(revise(self.verb.id, ledger.events).status, 'ABSTAIN')

    def test_divergent_observation_forces_abstention(self):
        ledger = self.train()
        case = examples(self.verb, positive=0, negative=1, prefix='divergent')[0]
        alternate = replace(case, observed_after=case.before | {F('paint', case.roles[0], 'red')})
        ledger.record(alternate, self.verbs)
        self.assertEqual(revise(self.verb.id, ledger.events).status, 'ABSTAIN')

    def test_permissions_missing_cannot_be_learned_as_attempt(self):
        ledger = ScarJournal()
        case = self.cases[0]
        owner, helper, bike = case.roles[1], case.roles[2], case.roles[0]
        denied = replace(case, before=case.before - {F('permits', owner, helper, bike)})
        with self.assertRaises(ValueError):
            ledger.record(denied, self.verbs)
        self.assertFalse(ledger.events)

    def test_duplicate_ids_and_untrusted_provenance_rejected(self):
        ledger = ScarJournal()
        ledger.record(self.cases[0], self.verbs)
        with self.assertRaises(ValueError):
            ledger.record(self.cases[0], self.verbs)
        with self.assertRaises(ValueError):
            ledger.record(replace(self.cases[1], provenance='REAL_VERIFIED'), self.verbs)
        self.assertEqual(len(ledger.events), 1)

    def test_synthetic_observations_are_immutable(self):
        case = self.cases[0]
        before = case.before
        observed = case.observed_after
        ledger = self.train()
        self.assertEqual(case.before, before)
        self.assertEqual(case.observed_after, observed)
        self.assertNotEqual(ledger.events[0].before, ledger.events[0].predicted_after)

    def test_explicit_abstention_for_unknown_operator(self):
        model = revise('unknown', self.train().events)
        self.assertEqual(model.status, 'ABSTAIN')

    def test_report_counts_heldout_without_training_on_them(self):
        report = run_demo()
        self.assertEqual((report['train_attempts'], report['held_out_attempts']), (8, 4))
        self.assertEqual((report['naive_correct'], report['revised_correct']), (2, 4))
        self.assertTrue(report['training_journal_unchanged'])


if __name__ == '__main__':
    unittest.main()
