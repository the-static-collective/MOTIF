import json
import unittest
from dataclasses import replace
from language import Case, State, HOLD, SOURCE_REVISION, digest, execute, transition
from teachers import lesson_set
from distillery import Distillery, LocalReceiver, validate
from bench import independent_cases, evaluate, classical_bfs
from demo import main


def raw():
    return Distillery(lesson_set()).synthesize()


class DistilleryTest(unittest.TestCase):
    def test_two_teachers_induce_unshown_joint_procedure(self):
        lessons = lesson_set()
        self.assertEqual({(l.case.need_lookup, l.case.need_challenge) for l in lessons},
                         {(True, False), (False, True), (False, False)})
        obj = validate(raw())
        self.assertEqual([row['op'] for row in obj['program']],
                         ['VERIFY_SOURCE', 'EXACT_LOOKUP', 'TEST_COUNTEREXAMPLE',
                          'DRAFT_HYPOTHESIS'])
        self.assertEqual([row['guard'] for row in obj['program']],
                         ['ALWAYS', 'NEED_LOOKUP', 'NEED_CHALLENGE', 'ALWAYS'])
        self.assertEqual(obj['possible_orders'], 2)
        self.assertEqual(obj['unobserved_order_pairs'],
                         [['EXACT_LOOKUP', 'TEST_COUNTEREXAMPLE']])

    def test_independent_combined_case_and_full_classical_control(self):
        obj = validate(raw())
        scores = evaluate(obj['program'])
        self.assertEqual(scores['learned']['correct'], 9)
        self.assertEqual(scores['single_teacher_router']['correct'], 8)
        self.assertEqual(scores['full_classical_bfs']['correct'], 9)
        self.assertTrue(scores['learned']['joint_positive'])
        self.assertFalse(scores['single_teacher_router']['joint_positive'])
        self.assertTrue(scores['full_classical_bfs']['joint_positive'])
        self.assertEqual(classical_bfs(Case('both', True, True))['length'], 4)

    def test_unreviewed_reception_and_exact_review_digest(self):
        r = LocalReceiver(raw())
        with self.assertRaises(HOLD):
            r.suggest(Case('task', True, True))
        with self.assertRaises(HOLD):
            r.admit('ADMIT_READ_ONLY', 'guess')
        review = r.preview(independent_cases())
        self.assertEqual((review['cases'], review['errors']), (9, 0))
        self.assertEqual(review['unresolved_order_disagreements'], 0)
        with self.assertRaises(HOLD):
            r.admit('WRONG_PERMISSION', review['review_digest'])
        with self.assertRaises(HOLD):
            r.admit('ADMIT_READ_ONLY', 'stale')
        r.admit('ADMIT_READ_ONLY', review['review_digest'])
        result = r.suggest(Case('task', True, True))
        self.assertEqual(result['toy_outcome']['result'], 'DRAFT')
        self.assertFalse(result['executed_externally'])
        self.assertFalse(result['authority'])

    def test_negative_cases_hold(self):
        obj = validate(raw())
        for case, expected in independent_cases():
            self.assertEqual(execute(obj['program'], case)['result'], expected)
        with self.assertRaises(HOLD):
            LocalReceiver(raw(), source_revision='reason-method-sandbox-r2')
        with self.assertRaises(HOLD):
            Case('bad-revision', False, True, source_revision='r2')

    def test_corrupted_teacher_trace_rejected_even_if_rehashed(self):
        samples = list(lesson_set())
        corrupted = list(samples[0].events)
        corrupted[0] = dict(corrupted[0], after=State().packet())
        samples[0] = replace(samples[0], events=tuple(corrupted))
        with self.assertRaises(HOLD):
            Distillery(tuple(samples))
        s = samples[0]
        forged = digest({'teacher': s.teacher_claim, 'ref': s.case.ref,
                         'context': s.case.context(), 'events': list(s.events),
                         'revision': SOURCE_REVISION})
        samples[0] = replace(s, receipt=forged)
        with self.assertRaises(HOLD):
            Distillery(tuple(samples))

    def test_no_hidden_teacher_source_or_thoughts(self):
        obj = validate(raw())
        self.assertNotIn('teacher_code', obj)
        self.assertNotIn('private_chain_of_thought', obj)
        self.assertEqual(obj['origin_claim'], 'TWO_SYNTHETIC_TEACHERS_UNVERIFIED')
        self.assertFalse(obj['real_world_authority'])

    def test_no_neutral_or_duplicate_coverage_refuses(self):
        lessons = lesson_set()
        with self.assertRaises(HOLD):
            Distillery(lessons[:2])
        with self.assertRaises(HOLD):
            Distillery((lessons[0], lessons[0], lessons[1]))
        with self.assertRaises(HOLD):
            Distillery((lessons[0], lessons[1], lessons[1]))

    def test_checksum_corruption_and_rehash_privilege_escalation(self):
        obj = validate(raw())
        obj['program'][1]['guard'] = 'ALWAYS'
        with self.assertRaises(HOLD):
            validate(json.dumps(obj))
        obj['checksum_sha256'] = digest({k:v for k,v in obj.items()
                                         if k != 'checksum_sha256'})
        with self.assertRaises(HOLD):
            validate(json.dumps(obj))
        obj = validate(raw())
        obj['real_world_authority'] = True
        obj['checksum_sha256'] = digest({k:v for k,v in obj.items()
                                         if k != 'checksum_sha256'})
        with self.assertRaises(HOLD):
            validate(json.dumps(obj))
        obj = validate(raw())
        obj['program'].insert(2, {'op': 'SEND_EMAIL', 'guard': 'ALWAYS'})
        obj['checksum_sha256'] = digest({k:v for k,v in obj.items()
                                         if k != 'checksum_sha256'})
        with self.assertRaises(HOLD):
            validate(json.dumps(obj))

    def test_rehashed_known_order_requires_independent_review(self):
        obj = validate(raw())
        obj['program'][1],obj['program'][2] = obj['program'][2],obj['program'][1]
        obj['checksum_sha256'] = digest({k:v for k,v in obj.items()
                                         if k != 'checksum_sha256'})
        r = LocalReceiver(json.dumps(obj))
        with self.assertRaises(HOLD):
            r.suggest(Case('not-authed', True, True))
        review = r.preview(independent_cases())
        self.assertEqual(review['errors'], 0)
        self.assertEqual(review['unresolved_order_disagreements'], 0)
        # Content checksums are not authentication; this local receiver merely
        # rechecks the current sandbox semantics after a changed source packet.
        r.admit('ADMIT_READ_ONLY', review['review_digest'])
        self.assertTrue(r.admitted)

    def test_review_needs_joint_case_and_negative_control(self):
        r = LocalReceiver(raw())
        with self.assertRaises(HOLD):
            r.preview(tuple((c, label) for c,label in independent_cases()
                            if not c.need_lookup or not c.need_challenge))
        with self.assertRaises(HOLD):
            r.preview(tuple((c, label) for c,label in independent_cases()
                            if label == 'DRAFT'))
        with self.assertRaises(HOLD):
            r.preview(((Case('duplicate', True, True), 'DRAFT'),
                       (Case('duplicate', True, True), 'DRAFT')))

    def test_source_guard_not_bypassable(self):
        with self.assertRaises(HOLD):
            transition('DRAFT_HYPOTHESIS', State(), Case('x', True, True))

    def test_receipt(self):
        receipt=main()
        self.assertEqual(receipt['review'],
                         {'correct':9, 'total':9, 'unresolved_order_disagreements':0})
        self.assertTrue(receipt['read_only_admission'])
        self.assertFalse(receipt['real_world_authority'])


if __name__ == '__main__':
    unittest.main()
