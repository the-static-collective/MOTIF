"""Regression tests for the bounded missing-world experiment."""
import unittest,os,json,tempfile
from pathlib import Path
import missing_world as exp
import visual_in as png
import world_model as old

class MissingWorldTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        env=os.environ
        cls.source=Path(env["MOTIF009_QUESTION_DIR"])
        cls.probe=Path(env["MOTIF013_PROBE_DIR"])
        cls.answer=Path(env["MOTIF013_ANSWER_DIR"])
        cls.graft=Path(env["GRAFT031_SOURCE"])
        cls.receipt=exp.read(cls.answer/"held-new-model-answer.json")
    def test_four_old_worlds_are_unchanged(self):
        rec,worlds=old.verify_original(self.source)
        self.assertEqual(len(worlds),4)
        self.assertEqual(len({w["start_png_sha256"] for w in worlds}),4)
    def test_new_observation_not_in_original_grammar(self):
        a=png.read_png(self.probe/"before.png")
        b=png.read_png(self.probe/"outside.png")
        self.assertEqual(len(png.coords(a,"#")),8)
        self.assertEqual(len(png.coords(b,"#")),6)
    def test_two_cells_change_without_moving_red(self):
        a=png.read_png(self.probe/"before.png")
        b=png.read_png(self.probe/"outside.png")
        self.assertEqual(png.coords(a,"#")-png.coords(b,"#"),
                         set(exp.OPEN_CELLS))
        self.assertEqual(png.coords(a,"R"),png.coords(b,"R"))
    def test_old_image_language_cannot_absorb_event_as_movement(self):
        with self.assertRaises(png.HOLD):
            png.question((self.probe/"before.png").read_bytes(),
                         (self.probe/"outside.png").read_bytes())
    def test_only_one_new_generated_family_survives(self):
        packet=exp.read(self.probe/"graft-receipt.json")
        self.assertEqual(packet["candidate_count"],3)
        self.assertEqual(packet["chosen"]["mode"],"open_observed_pair")
        self.assertEqual(len([x for x in packet["considered"] if x["accepted"]]),1)
    def test_source_owning_graft_is_pinned(self):
        self.assertEqual(exp.verify_graft(self.graft),exp.GRAFT_OWNER_BLOB)
    def test_original_full_wall_cannot_be_crossed(self):
        result=self.receipt["result_before_model_update"]
        self.assertTrue(result["proof_complete"])
        self.assertFalse(result["reachable"])
    def test_hypothetical_route_after_changed_environment(self):
        result=self.receipt["result_after_simulated_environment_event"]
        self.assertTrue(result["proof_complete"])
        self.assertTrue(result["reachable"])
        self.assertGreater(len(result["hypothetical_steps"]),0)
    def test_model_is_held_and_not_an_external_effect(self):
        self.assertFalse(self.receipt["model_auto_admitted"])
        self.assertTrue(self.receipt["synthetic_environment_event_only"])
        self.assertFalse(self.receipt["current_physical_world_identified"])
    def test_original_report_is_content_addressed(self):
        result=dict(self.receipt)
        signature=result.pop("content_sha256")
        self.assertEqual(png.digest(result),signature)
    def test_unchanged_image_does_not_trigger_new_model(self):
        with self.assertRaises(exp.HOLD):
            exp.synthesize_event(self.source,
                (self.probe/"before.png").read_bytes())
    def test_shorter_single_cell_event_is_outside_generator(self):
        rows=png.read_png(self.probe/"before.png")
        changed=tuple("".join("." if (x,y)==(4,3) else c
                       for x,c in enumerate(row))
                      for y,row in enumerate(rows))
        with self.assertRaises(exp.HOLD):
            exp.synthesize_event(self.source,png.encode_png(changed))
if __name__=="__main__":unittest.main()
