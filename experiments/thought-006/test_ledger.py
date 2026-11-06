"""Adversarial tests for epistemic non-promotion, audit integrity and replay."""
import json
import tempfile
import unittest
from pathlib import Path

from adapter import import_geom005
from demo import run_demo
from ledger import LedgerError, ThoughtLedger


class LedgerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / 'events.jsonl'
        self.l = ThoughtLedger(self.path)
        for n in ('shelf', 'meal'):
            self.l.register_node(n, n.title())
        self.l.register_source('idea', 'root:idea', 'inference', 'Unverified intuition')
        self.l.register_source('a1', 'root:A', 'validated_fixture', 'Synthetic fixture A')
        self.l.register_source('a2', 'root:A', 'validated_fixture', 'Repeated fixture A')
        self.l.register_source('b1', 'root:B', 'validated_fixture', 'Synthetic fixture B')
        self.l.register_source('x1', 'root:C', 'validated_fixture', 'Contradicting fixture')
        self.l.sketch('c', 'shelf', 'enables', 'meal',
                      'fixture:event-1', 'A shelf can help this meal', 'idea')

    def test_full_replay_and_separate_pen_receipts(self):
        self.l.support('c', 'a1', 'independent A')
        self.l.support('c', 'b1', 'independent B')
        self.l.commit('c', 'fixture-reviewer', 'Reviewed synthetic scoped fixtures')
        self.assertEqual(self.l.receipt('c')['status'], 'PEN_SCOPED')
        self.assertEqual(self.l.receipt('c')['effective_external_authority'], 'NONE')
        self.assertEqual(self.l.snapshot(), ThoughtLedger(self.path).snapshot())

    def test_unverified_sketch_cannot_autopromote(self):
        with self.assertRaisesRegex(LedgerError, 'two independent'):
            self.l.commit('c', 'fixture-reviewer', 'Map looks convincing')
        self.assertEqual(self.l.assertions['c'].mode, 'PENCIL')
        self.assertEqual(len(self.l.history()), 8)

    def test_echoes_do_not_increase_independent_origins(self):
        self.l.support('c', 'a1', 'evidence')
        self.l.support('c', 'a2', 'same upstream root')
        with self.assertRaisesRegex(LedgerError, 'two independent'):
            self.l.commit('c', 'reviewer', 'duplicate sources')
        self.l.support('c', 'b1', 'independent')
        self.l.commit('c', 'reviewer', 'distinct fixture roots')
        self.assertEqual(self.l.receipt('c')['dispositions'][-1]['evidence_roots'],
                         ['root:A', 'root:B'])

    def test_unresolved_contradiction_blocks_pen(self):
        self.l.support('c', 'a1', 'A')
        self.l.support('c', 'b1', 'B')
        self.l.challenge('c', 'x1', 'counterexample exists')
        with self.assertRaisesRegex(LedgerError, 'challenged'):
            self.l.commit('c', 'reviewer', 'ignoring counterexample')
        self.assertEqual(self.l.receipt('c')['status'], 'PENCIL_CHALLENGED')

    def test_challenging_pen_revokes_uncontested_status(self):
        self.l.support('c', 'a1', 'A')
        self.l.support('c', 'b1', 'B')
        self.l.commit('c', 'reviewer', 'reviewed')
        self.l.challenge('c', 'x1', 'new counterexample')
        self.assertEqual(self.l.receipt('c')['status'], 'PEN_CHALLENGED')
        self.l.withdraw('c', 'reviewer', 'no longer stable')
        self.assertEqual(self.l.receipt('c')['instrument'], 'RETIRED')
        with self.assertRaisesRegex(LedgerError, 'pencil'):
            self.l.support('c', 'x1', 'supporting a retired conclusion')

    def test_pen_can_be_reopened_as_pencil_without_erasure(self):
        self.l.support('c', 'a1', 'A')
        self.l.support('c', 'b1', 'B')
        self.l.commit('c', 'reviewer', 'reviewed')
        committed_digest = self.l.head_digest
        self.l.reopen('c', 'reviewer', 'new line of inquiry')
        receipt = self.l.receipt('c')
        self.assertEqual(receipt['instrument'], 'PENCIL')
        self.assertEqual(receipt['revision'], 2)
        self.assertEqual(receipt['supports'], [])
        self.assertEqual([d['decision'] for d in receipt['dispositions']],
                         ['PEN_SCOPED', 'REOPENED'])
        self.assertTrue(any(ev['digest'] == committed_digest for ev in self.l.history()))
        with self.assertRaisesRegex(LedgerError, 'two independent'):
            self.l.commit('c', 'reviewer', 'stale sources are insufficient')

    def test_corruption_is_not_ignored(self):
        data = self.path.read_text()
        self.path.write_text(data.replace('A shelf can help this meal',
                                          'A shelf always guarantees the meal'))
        with self.assertRaisesRegex(LedgerError, 'chain/schema'):
            ThoughtLedger(self.path)

    def test_missing_terminal_newline_fails_closed(self):
        self.path.write_bytes(self.path.read_bytes().rstrip(b'\n'))
        with self.assertRaisesRegex(LedgerError, 'partial'):
            ThoughtLedger(self.path)

    def test_stale_writer_rejects_append(self):
        second = ThoughtLedger(self.path)
        second.register_node('visitor', 'Visitor')
        with self.assertRaisesRegex(LedgerError, 'changed'):
            self.l.register_node('stale', 'Stale')
        self.l.reload()
        self.l.register_node('fresh', 'Fresh')

    def test_unsupported_ends_or_broad_scope_fail_closed(self):
        with self.assertRaises(LedgerError):
            self.l.sketch('unknown', 'shelf', 'enables', 'missing',
                          'fixture:local', 'unsupported endpoint', 'idea')
        with self.assertRaises(LedgerError):
            self.l.sketch('universal', 'shelf', 'enables', 'meal',
                          '*', 'global without basis', 'idea')
        with self.assertRaises(LedgerError):
            self.l.sketch('unfounded', 'shelf', 'causes', 'meal',
                          'fixture:local', 'unknown relation', 'idea')
        with self.assertRaises(LedgerError):
            self.l.support('c', 'unknown', 'unresolved source')

    def test_failed_event_does_not_append_or_mutate(self):
        events = len(self.l.history())
        state = self.l.snapshot()
        with self.assertRaises(LedgerError):
            self.l.commit('c', 'reviewer', 'not supported')
        self.assertEqual(len(self.l.history()), events)
        self.assertEqual(self.l.snapshot(), state)

    def test_no_layout_data_can_change_commit(self):
        before = self.l.snapshot()
        arbitrary_layouts = [
            {'shelf': (0, 0), 'meal': (0.00001, 0)},
            {'shelf': (1, 1000000), 'meal': (-1000000, 0)}]
        for layout in arbitrary_layouts:
            self.assertEqual(set(layout), set(self.l.nodes))
            self.assertEqual(before, self.l.snapshot())
        with self.assertRaises(LedgerError):
            self.l.commit('c', 'reviewer', 'looked close in flower layout')

    def test_imported_geom005_graph_is_not_pen(self):
        graph = {
            'nodes': [{'id': 'a', 'label': 'Home', 'kind': 'concept'},
                      {'id': 'b', 'label': 'Shelter', 'kind': 'concept'}],
            'edges': [{'source': 'a', 'target': 'b', 'relation': 'associated',
                       'origin': 'fixture-graph', 'confidence': 0.9,
                       'observed': True}]}
        l = ThoughtLedger(Path(self.temp.name) / 'adapter.jsonl')
        imported = import_geom005(graph, l, scope='fixture:language-example')
        self.assertEqual(imported, ['import-edge-00001'])
        self.assertEqual(l.receipt(imported[0])['instrument'], 'PENCIL')
        self.assertEqual(l.receipt(imported[0])['status'], 'SKETCH')
        self.assertEqual(l.receipt(imported[0])['supports'], [])
        self.assertEqual(l.assertions[imported[0]].observed_input, True)
        with self.assertRaises(LedgerError):
            l.commit(imported[0], 'reviewer', 'observed in old graph')

    def test_import_is_bounded_and_no_phantom_endpoints(self):
        l = ThoughtLedger(Path(self.temp.name) / 'adapter.jsonl')
        bad = {'nodes': [], 'edges': [{'source': 'a', 'target': 'b',
               'relation': 'associated', 'origin': 'unknown',
               'confidence': 0.9, 'observed': True}]}
        with self.assertRaises(ValueError):
            import_geom005(bad, l, scope='fixture:bad')
        self.assertEqual(l.snapshot()['events'], 0)

    def test_demo_end_to_end(self):
        report = run_demo()
        self.assertTrue(report['initial_universal_promotion_rejected'])
        self.assertTrue(report['echoed_root_rejected'])
        self.assertTrue(report['exact_replay'])
        self.assertEqual(report['pen_receipt']['status'], 'PEN_SCOPED')
        self.assertEqual(report['pen_challenged']['status'], 'PEN_CHALLENGED')
        self.assertEqual(report['withdrawn_receipt']['status'], 'WITHDRAWN')
        self.assertEqual(report['reopened_receipt']['instrument'], 'PENCIL')


if __name__ == '__main__':
    unittest.main()
