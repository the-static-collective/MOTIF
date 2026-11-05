"""MOTIF-005: falsifiable tests for composite graph concept induction."""
import unittest
from dataclasses import replace
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "002"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "004"))
from motif002 import F, induce, lessons, possibilities
from scar import ScarJournal
from concept import (canonical, candidate_motifs, holds, discover,
                     concept_projection, guarded_moves, repair_operator,
                     examples, labeled, run_demo)


class BirthOfConceptTests(unittest.TestCase):
    def setUp(self):
        self.verbs = induce(lessons())
        self.verb = repair_operator(self.verbs)
        self.episodes = examples(self.verb)
        self.scars = labeled(self.episodes, self.verbs)
        self.model = discover(self.scars, self.verb.id)

    def test_training_episodes_are_attempts_with_independent_outcome(self):
        self.assertEqual(len(self.scars), 18)
        self.assertEqual(sum(x.outcome == 'effect_confirmed_in_fixture'
                             for x in self.scars), 6)
        self.assertEqual(sum(x.outcome == 'no_observed_change'
                             for x in self.scars), 12)
        self.assertEqual({x.provenance for x in self.scars},
                         {'SYNTHETIC_WITNESS'})

    def test_composite_predicate_is_induced_not_hardcoded(self):
        self.assertEqual(self.model.status, 'PROPOSED')
        self.assertEqual(len(self.model.definition), 2)
        self.assertEqual(self.model.support_success, 6)
        self.assertEqual(self.model.support_failure, 12)
        self.assertTrue(self.model.id.startswith('concept-'))
        self.assertEqual(self.model.definition,
                         (F('carries', '?2', '?e0'), F('fits', '?e0', '?0')))

    def test_single_edge_baseline_cannot_separate(self):
        self.assertEqual(self.model.best_single_accuracy, 0.5)

    def test_held_out_new_id_generalization(self):
        holdout = labeled(examples(self.verb, positive=4, negative=8,
                                    namespace='totally_new'), self.verbs)
        outcomes = [(bool(concept_projection(self.model, x.before, x.roles)),
                     x.outcome == 'effect_confirmed_in_fixture') for x in holdout]
        self.assertEqual(len(outcomes), 12)
        self.assertTrue(all(a == b for a, b in outcomes))

    def test_hard_negative_contains_both_predicates_but_not_join(self):
        no = next(x for x in self.scars if x.outcome == 'no_observed_change')
        predicates = {f[0] for f in no.before}
        self.assertIn('carries', predicates)
        self.assertIn('fits', predicates)
        self.assertFalse(holds(self.model.definition, no.before, no.roles))

    def test_shared_witness_is_not_optional(self):
        yes = next(x for x in self.scars if x.outcome == 'effect_confirmed_in_fixture')
        matches = [f for f in yes.before if f[0] == 'carries' and
                   f[1] == yes.roles[2] and
                   any(g[0] == 'fits' and g[1] == f[2] and g[2] == yes.roles[0]
                       for g in yes.before)]
        self.assertEqual(len(matches), 1)
        self.assertTrue(holds(self.model.definition, yes.before, yes.roles))

    def test_anonymization_is_invariant_under_entity_renaming(self):
        a = (F('carries', 'worker_x', 'component_x'),
             F('fits', 'component_x', 'bike_x'))
        b = (F('carries', 'worker_98', 'component_177'),
             F('fits', 'component_177', 'bike_14'))
        self.assertEqual(canonical(a, ('bike_x', 'owner_x', 'worker_x')),
                         canonical(b, ('bike_14', 'owner_98', 'worker_98')))

    def test_projected_concept_is_not_an_observation(self):
        yes = next(x for x in self.scars if x.outcome == 'effect_confirmed_in_fixture')
        observed_snapshot = yes.before
        inferred = concept_projection(self.model, yes.before, yes.roles)
        self.assertEqual(inferred, frozenset({F(self.model.id, *yes.roles)}))
        self.assertEqual(yes.before, observed_snapshot)
        self.assertFalse(inferred.issubset(yes.before))

    def test_guarded_affordance_rejects_unjoined_repair(self):
        yes = next(x for x in self.scars if x.outcome == 'effect_confirmed_in_fixture')
        no = next(x for x in self.scars if x.outcome == 'no_observed_change')
        self.assertGreater(len(tuple(possibilities(no.before, {self.verb.id:self.verb}))), 0)
        self.assertTrue(guarded_moves(yes.before, self.verb, self.model))
        self.assertFalse(guarded_moves(no.before, self.verb, self.model))

    def test_permission_guard_is_preserved(self):
        yes = next(x for x in self.scars if x.outcome == 'effect_confirmed_in_fixture')
        bike, owner, worker = yes.roles
        denied = yes.before - {F('permits', owner, worker, bike)}
        self.assertTrue(concept_projection(self.model, denied, yes.roles))
        self.assertFalse(guarded_moves(denied, self.verb, self.model))

    def test_ambiguous_spurious_single_edge_makes_model_abstain(self):
        confounded = labeled(examples(self.verb, confound=True), self.verbs)
        ambiguous = discover(confounded, self.verb.id)
        self.assertEqual(ambiguous.status, 'ABSTAIN_AMBIGUOUS')
        self.assertGreaterEqual(ambiguous.alternatives, 2)
        self.assertFalse(concept_projection(ambiguous,
                         confounded[0].before, confounded[0].roles))

    def test_not_enough_data_means_abstention(self):
        sparse = discover(self.scars[:3], self.verb.id)
        self.assertEqual(sparse.status, 'ABSTAIN')

    def test_divergence_causes_abstention(self):
        positive = next(x for x in self.episodes if x.observed_after != x.before)
        mutated = replace(positive, attempt_id='divergent-case',
                          observed_after=positive.before |
                          {F('painted', positive.roles[0])})
        journal = ScarJournal()
        journal.record(mutated, self.verbs)
        new_model = discover(self.scars + journal.events, self.verb.id)
        self.assertEqual(new_model.status, 'ABSTAIN')

    def test_relabeling_outcomes_without_graph_changes_makes_model_abstain(self):
        # Same graph form, opposite declared result -> no perfect concept.
        positive = next(x for x in self.episodes if x.observed_after != x.before)
        contradictory = replace(positive, attempt_id='counterexample',
                                observed_after=positive.before)
        journal = ScarJournal()
        journal.record(contradictory, self.verbs)
        model = discover(self.scars + journal.events, self.verb.id)
        self.assertEqual(model.status, 'ABSTAIN_NO_SEPARATION')

    def test_report_documents_scoped_synthetic_success(self):
        r = run_demo()
        self.assertEqual(r['train_episodes'], 18)
        self.assertEqual(r['heldout_episodes'], 12)
        self.assertEqual(r['correct_heldout'], 12)
        self.assertEqual(r['concept']['status'], 'PROPOSED')
        self.assertTrue(r['observed_world_unchanged'])
        self.assertTrue(r['join_mismatch_rejected'])
        self.assertTrue(r['unjoined_case_held_from_simulation'])


if __name__ == '__main__':
    unittest.main()
