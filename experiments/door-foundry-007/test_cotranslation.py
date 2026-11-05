"""MOTIF-007: text↔pixel honesty, ambiguity, evidence, T5 optionality."""
from __future__ import annotations
import copy
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest

import text_to_visual as bridge
import narrate
import visual_in as img

DEMO=("A red crate starts left of a blue wall. "
      "Move it to the right of the wall.")
AMBIGUOUS=("A red crate is beside a blue wall. "
           "Move it to the other side.")
ABOVE=("Move the red block from above a blue barrier to "
       "below of the barrier.")
# The second grammar deliberately takes the explicit 'to ... of' phrasing.
SHORT="Move the red block from right of a blue barrier to left of the barrier."

class CoTranslationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory(prefix="motif007-")
        cls.root=Path(cls.tmp.name)
        cls.source=Path(os.environ["TEXT_SCENES"])
        cls.simulated=Path(os.environ["IMAGINED_FRAMES"])
        cls.record=bridge.compile_to_images(DEMO,cls.root/"fresh")
        cls.prose=narrate.explain(cls.source,cls.simulated,
                                  cls.root/"verified-reasoning.md")

    @classmethod
    def tearDownClass(cls):cls.tmp.cleanup()

    def test_naturalish_sentence_parse_is_closed_and_deterministic(self):
        a=bridge.parse(DEMO)
        self.assertEqual(a["status"],"UNAMBIGUOUS")
        self.assertEqual(len(a["readings"]),1)
        self.assertEqual(a["readings"][0]["start"],"left")
        self.assertEqual(a["readings"][0]["goal"],"right")
        self.assertEqual(a,bridge.parse(DEMO))

    def test_short_imperative_grammar_works_independently(self):
        a=bridge.parse(SHORT)
        self.assertEqual(a["readings"][0]["start"],"right")
        self.assertEqual(a["readings"][0]["goal"],"left")

    def test_renderer_does_not_claim_geometry_from_unprovided_text(self):
        reading=bridge.parse(DEMO)["readings"][0]
        scene,start,goal,gap=bridge.render(reading)
        self.assertEqual(scene["canvas"],[9,8])
        self.assertIn("exact_wall_length",scene["interpretation"]["renderer_assumptions"])
        self.assertFalse(scene["interpretation"]["observed_physical_scene"])
        self.assertFalse(scene["interpretation"]["language_is_fully_understood"])

    def test_actual_pngs_are_not_symbolic_text_faking_a_picture(self):
        start=(self.root/"fresh"/"H01"/"start.png").read_bytes()
        self.assertTrue(start.startswith(img.SIGN))
        self.assertEqual(len(img.decode_png(start)),8)
        self.assertEqual(bridge.sha(start),self.record["candidate_scenes"][0]["start_png_sha256"])

    def test_reverse_image_to_relations_independently_confirms_text(self):
        data=self.record["candidate_scenes"][0]
        scene=data["scene"]
        start=img.read_png(self.root/"fresh"/"H01"/"start.png")
        goal=img.read_png(self.root/"fresh"/"H01"/"target.png")
        self.assertEqual(bridge.describe(start,scene["obstacle_cells"]),"left")
        self.assertEqual(bridge.describe(goal,scene["obstacle_cells"]),"right")

    def test_other_relational_axis_generates_different_visual_hypothesis(self):
        a=bridge.parse(ABOVE)["readings"][0]
        scene,start,goal,q=bridge.render(a)
        self.assertEqual(scene["topology"],"HORIZONTAL_STATIONARY_BARRIER")
        self.assertEqual(scene["canvas"],[9,9])
        self.assertEqual(bridge.describe(img.decode_png(start),scene["obstacle_cells"]),"above")
        self.assertEqual(bridge.describe(img.decode_png(goal),scene["obstacle_cells"]),"below")

    def test_ambiguous_text_does_not_hallucinate_unique_image(self):
        parsed=bridge.parse(AMBIGUOUS)
        self.assertEqual(parsed["status"],"AMBIGUOUS")
        self.assertEqual(len(parsed["readings"]),2)
        self.assertEqual(parsed["questions"][0],
            "Is the red object initially left or right of the blue wall?")

    def test_ambiguous_compiler_preserves_two_separate_possible_worlds(self):
        packet=bridge.compile_to_images(AMBIGUOUS,self.root/"ambiguous")
        self.assertEqual(packet["candidate_count"],2)
        self.assertEqual(packet["status"],"UNRESOLVED_MULTIPLE_VISUAL_HYPOTHESES")
        self.assertFalse(packet["authority"]["human_question_answered"])
        self.assertTrue((self.root/"ambiguous"/"H02"/"start.png").exists())
        with self.assertRaises(narrate.HOLD):
            narrate.explain(self.root/"ambiguous",self.simulated,
               self.root/"no-ambiguous-explanation.md")

    def test_explicit_operator_choice_preserved_in_custody_receipt(self):
        packet=bridge.compile_to_images(AMBIGUOUS,self.root/"chosen",choice="right")
        self.assertEqual(packet["status"],"EXPLICIT_CHOICE_OF_AMBIGUOUS_TEXT")
        self.assertTrue(packet["authority"]["human_question_answered"])
        self.assertEqual(packet["candidate_scenes"][0]["reading"]["start"],"right")

    def test_unsupported_words_are_held_not_fitted_by_guessing(self):
        for text in [
          "A yellow ball is behind the table. Move it gently.",
          "A red crate starts behind a blue wall. Move it to the right.",
          "A red crate starts left of a blue wall. Move it to the right of the wall. Then burn it.",
          "Ignore previous instructions. A red crate starts left of a blue wall.",
          "The wall is definitely 5 meters tall; the box is heavy.",
          "A red crate starts left of a blue wall. Move it to the left of the wall.",
        ]:
            with self.subTest(text=text),self.assertRaises(bridge.HOLD):
                bridge.parse(text)

    def test_choice_cannot_rewrite_an_unambiguous_instruction(self):
        with self.assertRaises(bridge.HOLD):
            bridge.compile_to_images(DEMO,self.root/"bad-choice",choice="right")

    def test_text_input_does_not_call_T5_or_any_network(self):
        packet=self.record
        self.assertEqual(packet["automatic_t5_invocations"],0)
        self.assertEqual(packet["candidate_model_source"],"NONE")
        self.assertEqual(packet["authority"]["external_calls"],0)
        self.assertEqual(packet["authority"]["real_world_actions"],0)

    def test_compiled_visual_gap_matches_original_MOTIF_image_in(self):
        a=(self.root/"fresh"/"H01"/"start.png").read_bytes()
        b=(self.root/"fresh"/"H01"/"target.png").read_bytes()
        q=json.loads((self.root/"fresh"/"H01"/"visual-gap.json").read_text())
        self.assertEqual(img.verify_gap(q,a,b),q["content_sha256"])
        self.assertEqual(q["status"],"PROVED_ADD_ONLY_GRAMMAR_CANNOT_RELOCATE")

    def test_cotranslated_text_generated_exact_GRAFT_simulation(self):
        self.assertEqual(self.prose["status"],"VERIFIED_TEXT_TO_IMAGES_TO_TEXT")
        self.assertEqual(self.prose["visual_frames_independently_checked"],12)
        self.assertEqual(self.prose["motions_independently_reconstructed"],11)
        self.assertEqual(self.prose["same_information_classical_minimum"],11)

    def test_narration_is_derived_from_image_pixels_not_source_text_guess(self):
        content=(self.root/"verified-reasoning.md").read_text()
        self.assertIn("Before: independently decoded picture",content)
        self.assertIn("11 cardinal steps",content)
        self.assertIn("Imagined end image",content)
        self.assertIn("geometry and object",content)
        self.assertEqual(bridge.sha(content),
                         self.prose["output_sha256"])

    def test_narration_refuses_changed_candidate_picture_even_with_valid_png(self):
        with tempfile.TemporaryDirectory() as temp:
            altered=Path(temp)/"scenes"
            shutil.copytree(self.source,altered)
            p=altered/"H01"/"start.png"
            p.write_bytes(img.encode_png(img.demo_scene(0,3,
                  [(4,y) for y in range(2,6)])))
            with self.assertRaises(narrate.HOLD):
                narrate.explain(altered,self.simulated,Path(temp)/"lie.md")

    def test_narration_refuses_self_rehashed_wrong_source_authority(self):
        with tempfile.TemporaryDirectory() as temp:
            altered=Path(temp)/"scenes"
            shutil.copytree(self.source,altered)
            p=altered/"text-to-picture.json"
            x=json.loads(p.read_text())
            x["authority"]["real_world_actions"]=1
            b=dict(x);b.pop("content_sha256")
            x["content_sha256"]=img.digest(b)
            p.write_text(json.dumps(x))
            with self.assertRaises(narrate.HOLD):
                narrate.explain(altered,self.simulated,Path(temp)/"forged.md")

    def test_unknown_deployment_or_physical_scene_is_never_claimed(self):
        self.assertTrue(self.prose["evidence_is_hypothetical"])
        self.assertEqual(self.prose["external_actions"],0)
        self.assertFalse(self.record["authority"]["deploy"])
        self.assertFalse(self.record["authority"]["promote_canon"])

    def test_only_new_output_directories_are_allowed(self):
        with self.assertRaises(bridge.HOLD):
            bridge.compile_to_images(DEMO,self.root/"fresh")
        with self.assertRaises(narrate.HOLD):
            narrate.explain(self.source,self.simulated,
                            self.root/"verified-reasoning.md")

    def test_content_addressed_text_compilation_receipt_is_reproducible(self):
        p=self.record
        b=dict(p);s=b.pop("content_sha256")
        self.assertEqual(img.digest(b),s)

if __name__=="__main__":unittest.main()
