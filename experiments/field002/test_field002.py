"""Adversarial reproducibility checks for FIELD-002 (stdlib unittest)."""
import json
from pathlib import Path
import unittest

from field002 import (WORLDS, Witness, World, best_query, check_packet,
                      connected, consistent, digest, experiment, investigate,
                      plan, programs)


class Field002Tests(unittest.TestCase):
    def test_one_fact_and_no_predicted_promotions(self):
        for world in WORLDS:
            proof = investigate(world)
            self.assertEqual(proof['starting_fact']['state_mask'], 0)
            self.assertEqual(len(proof['observations']), proof['source_queries'])
            self.assertEqual({r['state_mask'] for r in proof['observations']},
                             {0} | {s['target'] for s in proof['steps']})
            self.assertTrue(all(r['kind'] == 'SIMULATOR_OBSERVATION'
                                for r in proof['observations']))
            self.assertTrue(check_packet(proof, world))

    def test_revision_and_rehashed_false_witness_fail(self):
        world = WORLDS[0]
        witness = Witness(world)
        good = witness.observe(0)
        self.assertTrue(witness.verify(good))
        fake = {**good, 'observed': not good['observed']}
        fake['sha256'] = digest({k: v for k, v in fake.items() if k != 'sha256'})
        self.assertFalse(witness.verify(fake))
        proof = investigate(world)
        proof['observations'][0] = fake
        proof['packet_sha256'] = digest({k:v for k,v in proof.items() if k!='packet_sha256'})
        self.assertFalse(check_packet(proof, world))

    def test_wrong_revision_and_unknown_world_rejected(self):
        proof = investigate(WORLDS[1])
        wrong = World(WORLDS[1].name, WORLDS[1].axes, 'revision-changed')
        self.assertFalse(check_packet(proof, wrong))
        with self.assertRaises(ValueError):
            World('unknown', ('a',), 'r').outcome(0)

    def test_compositional_grammar_is_actually_more_expressive(self):
        for world in WORLDS[:3]:
            exact = tuple(int(world.outcome(s)) for s in range(1 << world.n))
            self.assertNotIn(exact, programs(world.n, 'UNARY'))
            self.assertIn(exact, programs(world.n, 'DNF2'))
            proof = investigate(world)
            self.assertEqual(proof['status'], 'FINITE_DOMAIN_VERIFIED')
            self.assertTrue(proof['grammar_expansions'])
            self.assertEqual(proof['surviving_functions'], 1)
            self.assertEqual(len(proof['observations']), 1 << world.n)
            self.assertEqual(tuple(int(r['observed']) for r in proof['observations']), exact)

    def test_unavailable_parity_stays_hold(self):
        world = WORLDS[3]
        exact = tuple(int(world.outcome(s)) for s in range(1 << world.n))
        self.assertNotIn(exact, programs(world.n, 'DNF2'))
        proof = investigate(world)
        self.assertEqual(proof['status'], 'HOLD_GRAMMAR_INSUFFICIENT')
        self.assertEqual(proof['surviving_functions'], 0)
        self.assertIsNone(proof['program'])
        self.assertTrue(check_packet(proof, world))

    def test_queries_are_frozen_before_independent_observations(self):
        for world in WORLDS:
            proof = investigate(world)
            memory = {0: proof['starting_fact']}
            current = 0
            for step in proof['steps']:
                grammar = step['grammar']
                avail = consistent(programs(world.n, grammar), memory)
                expected = best_query(avail, memory, current, world.n)
                self.assertEqual(step['target'], expected)
                self.assertEqual(step['candidate_count'], len(avail))
                self.assertEqual(step['predicted_true'], sum(sig[expected] for sig in avail))
                self.assertEqual(step['plan'], plan(current, expected, world.n))
                memory[expected] = next(r for r in proof['observations'] if r['state_mask'] == expected)
                self.assertEqual(step['actual'], memory[expected]['observed'])
                current = expected

    def test_no_shortcut_to_source_observation(self):
        source = Witness(WORLDS[0])
        self.assertEqual(source.queries, 0)
        candidates = programs(2, 'UNARY')
        self.assertIsNotNone(best_query(candidates, {}, 0, 2))
        self.assertEqual(source.queries, 0)
        self.assertEqual(len(plan(0, 3, 2)), 2)
        self.assertFalse(connected([('a','b')], 'a', 'z'))

    def test_baselines_and_cost_truthfulness(self):
        result = experiment()
        self.assertEqual(result['summary']['finite_exact'], 3)
        self.assertEqual(result['summary']['honest_holds'], 1)
        self.assertEqual(result['summary']['grammar_expansion_worlds'], 4)
        self.assertEqual(result['summary']['exact_cases_query_savings_vs_exhaustive'], 0)
        for case in result['cases']:
            proof, comparison = case['proof'], case['comparison']
            self.assertTrue(comparison['strong_classical_exact'])
            self.assertTrue(comparison['discovery_reconstructed_exact'] or proof['status'].startswith('HOLD'))
            self.assertEqual(proof['source_queries'], comparison['preexpanded_DNF2_queries'])
            self.assertEqual(comparison['unary_only_status'], 'HOLD_GRAMMAR_INSUFFICIENT')

    def test_output_exactly_reproduces_checked_in_record(self):
        path = Path(__file__).with_name('experiment-results.json')
        self.assertEqual(json.loads(json.dumps(experiment())), json.loads(path.read_text()))

    def test_negative_cases_and_edge_validation(self):
        with self.assertRaises(ValueError):
            programs(2, 'random')
        with self.assertRaises(ValueError):
            investigate(WORLDS[0], initial_grammar='bad')
        with self.assertRaises(ValueError):
            WORLDS[0].outcome(-1)
        with self.assertRaises(ValueError):
            WORLDS[0].outcome(16)
        bad = investigate(WORLDS[2])
        bad['steps'][0]['candidate_count'] += 1
        self.assertFalse(check_packet(bad, WORLDS[2]))


if __name__ == '__main__':
    unittest.main()