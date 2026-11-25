import threading
import unittest
from demo import fixture
from multiplex import Avenue, Hypothesis, best_answer, choose, execute_synthetic, revise


class MultiplexTests(unittest.TestCase):
    def setUp(self):
        self.hypotheses, self.avenues = fixture()

    def test_joint_synergy_beats_myopic_bait(self):
        single = choose(self.hypotheses, self.avenues, max_parallel=1)
        self.assertEqual(single.selected, ("BAIT",))
        self.assertAlmostEqual(single.expected_accuracy, 0.75)
        joint = choose(self.hypotheses, self.avenues, max_parallel=2)
        self.assertEqual(joint.selected, ("LEFT", "RIGHT"))
        self.assertAlmostEqual(joint.expected_accuracy, 1.0)
        self.assertEqual(joint.status, "MULTI_INQUIRY")

    def test_budget_safe_and_human_limits(self):
        a = choose(self.hypotheses, self.avenues, budget=1)
        self.assertEqual(a.selected, ("BAIT",))
        limited = choose(self.hypotheses, self.avenues, budget=0)
        self.assertEqual(limited.selected, ())
        blocked = [Avenue(x.name, x.kind, x.cost, x.predicted, x.origin, x.prompt, x.human, x.name != "RIGHT") for x in self.avenues]
        self.assertNotIn("RIGHT", choose(self.hypotheses, blocked).selected)
        human = [Avenue(x.name,x.kind,x.cost,x.predicted,x.origin,x.prompt,True,x.allowed) for x in self.avenues]
        self.assertEqual(len(choose(self.hypotheses, human, max_human=1).selected),1)

    def test_parallel_execution_and_revise(self):
        plan = choose(self.hypotheses, self.avenues, max_parallel=2)
        barrier = threading.Barrier(2)
        def resolve(a):
            barrier.wait(timeout=2)
            return a.predicted["01"]
        observed = execute_synthetic(plan, self.avenues, resolve)
        self.assertEqual(set(observed), {"LEFT", "RIGHT"})
        status, survivors = revise(self.hypotheses, self.avenues, observed)
        self.assertEqual(status, "UPDATED")
        self.assertEqual(best_answer(survivors), ("YES",1.0))

    def test_tentative_answer_and_inquiry_coexist(self):
        h = [Hypothesis("yes","YES",0.9),Hypothesis("no","NO",0.1)]
        a = Avenue("CHECK","ASK",1,{"yes":"Y","no":"N"},"independent")
        plan = choose(h,[a])
        self.assertEqual(plan.status,"ANSWER_AND_EXPLORE")
        self.assertEqual(plan.tentative_answer,"YES")
        self.assertEqual(plan.selected,("CHECK",))

    def test_outside_grammar_is_not_ignored(self):
        plan = choose(self.hypotheses,self.avenues,max_parallel=2)
        status, survivors = revise(self.hypotheses,self.avenues,{"LEFT":"unknown"})
        self.assertEqual(status,"HOLD_MODEL_FALSIFIED")
        self.assertEqual(len(survivors),4)

    def test_reject_malformed(self):
        with self.assertRaises(ValueError):
            choose(self.hypotheses,[Avenue("broken","ASK",1,{"00":"x"},"test")])
        with self.assertRaises(ValueError):
            choose(self.hypotheses,self.avenues * 4)
        with self.assertRaises(ValueError):
            revise(self.hypotheses,self.avenues,{"imaginary":"x"})


if __name__ == '__main__':
    unittest.main()

