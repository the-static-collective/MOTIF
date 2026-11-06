"""MOTIF-009: adversarial source, classical benchmark and cost-sensitive questions."""
from __future__ import annotations
import copy,json,os,shutil,tempfile,unittest
from fractions import Fraction
from pathlib import Path
from hashlib import sha256
import decision as decide
import visual_question as module
import visual_in as pixels

class ActiveQuestionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.amb=Path(os.environ["AMBIGUOUS_SCENES"])
        cls.base=Path(os.environ["TEXT_SCENES"])
        cls.imag=Path(os.environ["IMAGINED_FRAMES"])
        cls.build=Path(os.environ["VISUAL_BUILD"])
        cls.temp=tempfile.TemporaryDirectory(prefix="motif009-")
        cls.root=Path(cls.temp.name)
        cls.packet=module.build_packet(
            cls.amb,cls.base,cls.imag,cls.build,cls.root/"questions")
        cls.data=cls.packet["analysis"]
        cls.worlds,cls.context,_=module.generate_worlds(
            cls.amb,cls.base,cls.imag,cls.build)
        cls.weights={k:Fraction(v) for k,v in
            zip(decide.WORLD_IDS,(1,1,4,4))}
        cls.costs=decide.standard_costs()

    @classmethod
    def tearDownClass(cls):cls.temp.cleanup()

    def test_exact_original_007_ambiguous_text_has_two_distinct_image_interpretations(self):
        item=module.verified_ambiguous(self.amb)
        self.assertEqual(item["candidate_count"],2)
        self.assertEqual(item["status"],"UNRESOLVED_MULTIPLE_VISUAL_HYPOTHESES")
        self.assertFalse(item["authority"]["human_question_answered"])
        self.assertEqual(item["automatic_t5_invocations"],0)
        self.assertNotEqual(item["candidate_scenes"][0]["start_png_sha256"],
                            item["candidate_scenes"][1]["start_png_sha256"])

    def test_four_distinct_actual_png_hypotheses_not_labels_only(self):
        self.assertEqual(len(self.packet["visual_worlds"]),4)
        sources={v["start_png_sha256"] for v in self.packet["visual_worlds"]}
        self.assertEqual(len(sources),4)
        for v in self.packet["visual_worlds"]:
            root=self.root/"questions"/"worlds"/v["id"]
            self.assertTrue((root/"start.png").read_bytes().startswith(pixels.SIGN))
            self.assertEqual(sha256((root/"start.png").read_bytes()).hexdigest(),
                             v["start_png_sha256"])
            self.assertEqual(pixels.verify_gap(
                json.loads((root/"image-gap.json").read_text()),
                (root/"start.png").read_bytes(),
                (root/"target.png").read_bytes()),v["image_gap_sha256"])

    def test_full_height_really_changes_four_blue_pixels_to_eight(self):
        for name in ("LEFT","RIGHT"):
            partial=pixels.read_png(self.root/"questions"/"worlds"/
                                    (name+"_PARTIAL")/"start.png")
            full=pixels.read_png(self.root/"questions"/"worlds"/
                                 (name+"_FULL")/"start.png")
            self.assertEqual(len(pixels.coords(partial,"#")),4)
            self.assertEqual(len(pixels.coords(full,"#")),8)
            self.assertEqual(len(pixels.coords(full,"R")),4)

    def test_original_compiled_graft_operator_checks_reachability_of_each_world(self):
        for item in self.worlds:
            self.assertTrue(item["proof"]["closed"])
            self.assertEqual(item["proof"]["reached"],
                             item["wall_extent"]=="partial")
            self.assertFalse(item["world_observed"])
        self.assertEqual(self.context["manifest"]["auto_admit"],False)
        self.assertEqual(self.context["manifest"]["remote_ai_calls"],0)

    def test_prior_probabilities_are_assumptions_not_observations(self):
        values=self.data["cost_model"]["prior_probability"]
        self.assertEqual([values[k] for k in decide.WORLD_IDS],
                         [.1,.1,.4,.4])
        self.assertFalse(self.data["cost_model"]["real_world_calibrated"])

    def test_without_asking_best_action_is_a_risky_no_route_guess(self):
        self.assertEqual(self.data["zero_question_policy"]["kind"],"DECIDE")
        self.assertEqual(self.data["zero_question_policy"]["decision"],
                         "DECLARE_UNREACHABLE")
        self.assertEqual(self.data["zero_question_expected_loss"],1.)

    def test_one_question_optimum_asks_extent_not_higher_entropy_start_side(self):
        p=self.data["one_question_policy"]
        self.assertEqual(p["kind"],"ASK")
        self.assertEqual(p["question_id"],"ASK_WALL_EXTENT")
        self.assertAlmostEqual(self.data["one_question_expected_loss"],.7)

    def test_two_question_optimum_asks_extent_first_and_side_only_when_needed(self):
        policy=self.data["two_question_policy"]
        self.assertEqual(policy["question_id"],"ASK_WALL_EXTENT")
        self.assertEqual(policy["branches"]["full"]["policy"]["kind"],"DECIDE")
        self.assertEqual(policy["branches"]["full"]["policy"]["decision"],
                         "DECLARE_UNREACHABLE")
        partial=policy["branches"]["partial"]["policy"]
        self.assertEqual(partial["kind"],"ASK")
        self.assertEqual(partial["question_id"],"ASK_START_SIDE")
        self.assertEqual(partial["branches"]["left"]["policy"]["decision"],
                         "PLAN_LEFT_TO_RIGHT")
        self.assertEqual(partial["branches"]["right"]["policy"]["decision"],
                         "PLAN_RIGHT_TO_LEFT")
        self.assertAlmostEqual(self.data["two_question_expected_loss"],.32)

    def test_entropy_per_cost_heuristic_chooses_worse_first_question(self):
        greedy=self.data["entropy_greedy"]
        self.assertEqual(greedy["first_question"],"ASK_START_SIDE")
        self.assertGreater(
            greedy["information"]["ASK_START_SIDE"]["information_bits"],
            greedy["information"]["ASK_WALL_EXTENT"]["information_bits"])
        self.assertAlmostEqual(greedy["one_question_expected_loss"],1.1)
        self.assertAlmostEqual(greedy["two_question_expected_loss_if_heuristic_first"],.4)
        self.assertLess(self.data["two_question_expected_loss"],
                        greedy["two_question_expected_loss_if_heuristic_first"])

    def test_cost_of_inaction_is_separate_from_cost_of_not_asking(self):
        self.assertEqual(self.data["inaction_expected_loss"],2.)
        self.assertAlmostEqual(self.data["value_of_two_questions_vs_best_no_query"],.68)
        self.assertAlmostEqual(self.data["cost_of_inaction_vs_two_questions"],1.68)

    def test_exact_classical_brute_force_enumeration_ties_dp_on_all_budgets(self):
        c=self.data["classical_brute_control"]
        self.assertEqual([c["no_query_loss"],c["one_query_loss"],c["two_query_loss"]],
                         [1.,.7,.32])
        self.assertFalse(c["algorithmic_superiority_claimed"])

    def test_synthetic_oracle_does_not_claim_it_contacted_anyone(self):
        for p in self.data["synthetic_oracle_replay"]:
            self.assertTrue(p["simulated_answers_only"])
            self.assertFalse(p["actual_action_executed"])
            self.assertFalse(any(x["human_observation_received"] for x in
                                 p["hypothetical_answers"]))
        self.assertFalse(self.packet["custody"]["actual_answer_observed"])
        self.assertFalse(self.packet["custody"]["current_world_identified"])

    def test_query_is_not_worth_it_if_full_wall_is_very_likely(self):
        high={k:Fraction(v) for k,v in
              zip(decide.WORLD_IDS,(1,1,49,49))}
        r=decide.analyze(self.worlds,high,self.costs)
        self.assertEqual(r["two_question_policy"]["kind"],"DECIDE")
        self.assertEqual(r["zero_question_policy"]["decision"],
                         "DECLARE_UNREACHABLE")

    def test_expensive_questions_make_inaction_or_unasked_declaration_optimal(self):
        expensive={q:Fraction(30) for q in decide.QUESTIONS}
        r=decide.analyze(self.worlds,self.weights,expensive)
        self.assertEqual(r["two_question_policy"]["kind"],"DECIDE")
        self.assertEqual(r["two_question_expected_loss"],1.)

    def test_independent_decision_costs_and_finite_probabilities_required(self):
        with self.assertRaises(decide.HOLD):
            decide.analyze(self.worlds,{**self.weights,"LEFT_FULL":Fraction(0)},
                           self.costs)
        with self.assertRaises(decide.HOLD):
            decide.analyze(self.worlds,self.weights,
                           {**self.costs,"ASK_WALL_EXTENT":Fraction(0)})
        with self.assertRaises(decide.HOLD):
            decide.optimal(self.worlds,self.weights,self.costs,10)

    def test_undocumented_vision_source_cannot_be_selected_from_text(self):
        with self.assertRaises((module.HOLD,Exception)) as cm:
            module.verified_ambiguous(Path("/there/is/no/such/input"))
        self.assertIsNotNone(cm.exception)

    def test_altered_png_cannot_be_silently_promoted_even_if_other_receipt_is_valid(self):
        with tempfile.TemporaryDirectory() as tmp:
            copied=Path(tmp)/"ambiguous"
            shutil.copytree(self.amb,copied)
            p=copied/"H01"/"start.png"
            p.write_bytes(pixels.encode_png(pixels.demo_scene(0,3,
                    [(4,y) for y in range(2,6)])))
            with self.assertRaises(module.HOLD):
                module.verified_ambiguous(copied)

    def test_rehashed_false_permission_cannot_elevate_ambiguity_receipt(self):
        with tempfile.TemporaryDirectory() as tmp:
            copied=Path(tmp)/"ambiguous"
            shutil.copytree(self.amb,copied)
            p=copied/"text-to-picture.json"
            data=json.loads(p.read_text())
            data["authority"]["real_world_actions"]=1
            body=dict(data);body.pop("content_sha256")
            data["content_sha256"]=pixels.digest(body)
            p.write_text(json.dumps(data))
            with self.assertRaises(module.HOLD):
                module.verified_ambiguous(copied)

    def test_serialized_question_receipt_and_image_evidence_rehash(self):
        receipt=json.loads((self.root/"questions"/"active-question.json").read_text())
        body=dict(receipt);claim=body.pop("content_sha256")
        self.assertEqual(pixels.digest(body),claim)
        self.assertEqual(receipt["status"],"UNSENT_QUESTION_WITH_FOUR_IMAGE_HYPOTHESES")
        self.assertEqual(receipt["custody"]["external_api_calls"],0)
        self.assertEqual(receipt["custody"]["T5_calls"],0)
        self.assertFalse(receipt["custody"]["code_automatically_admitted"])

    def test_only_new_output_directories_are_allowed(self):
        with self.assertRaises(module.HOLD):
            module.build_packet(self.amb,self.base,self.imag,self.build,
                                self.root/"questions")

if __name__=="__main__":
    unittest.main()
