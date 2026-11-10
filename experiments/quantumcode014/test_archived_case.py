"""QC-014: replay a reduced *real recorded* QC-013 failure excerpt.

Receipt came from the separate archived original 220-action Crafter run.
The tests work on a compact extracted excerpt, not on the full original ZIP:
they establish detection timing, NOT independent full-archive authenticity.
"""
from pathlib import Path
import json
import unittest
from insanity import Snapshot,Observation,StagnationGuard

HERE=Path(__file__).resolve().parent
RECEIPT=json.loads((HERE/"observed_qc013_stall.json").read_text())


def moment(row,before):
    key="before" if before else "after"
    return Snapshot(
        (("wood",row["wood_"+key]),
         ("wood_pickaxe",row["wood_pickaxe_"+key])),
        tuple(row["achievement_"+key]),
        tuple(int(x) for x in row["location_"+key].split(":")[1].split(",")),
        facing=None,step=row["game_step"]-int(before),
    )


class ActualArchivedExcerptsTests(unittest.TestCase):
    def test_actual_prior_run_had_161_retries(self):
        self.assertEqual(RECEIPT["actual_make_wood_pickaxe_attempts"],161)
        self.assertEqual(sum(x["count"] for x in
                             RECEIPT["actual_consecutive_craft_attempt_runs"]),161)

    def test_three_initial_failures_come_from_steps_17_18_19(self):
        self.assertEqual([r["game_step"] for r in
                          RECEIPT["first_three_unproductive_attempts"]],
                         [17,18,19])
        self.assertTrue(all(
            x["wood_pickaxe_before"]==x["wood_pickaxe_after"]==0
            for x in RECEIPT["first_three_unproductive_attempts"]))

    def test_detector_triggers_at_step_19_without_seeing_future_steps(self):
        g=StagnationGuard(3)
        results=[]
        for row in RECEIPT["first_three_unproductive_attempts"]:
            obs=Observation(
                row["action"],moment(row,True),moment(row,False),
                "source:previous_actual_game:"+RECEIPT["recorded_member_sha256"])
            results.append(g.observe(obs))
        self.assertEqual(results[:2],[None,None])
        self.assertEqual(results[2].step,19)
        self.assertEqual(results[2].failures,3)
        self.assertTrue(g.should_hold("make_wood_pickaxe"))

    def test_source_receipt_is_cryptographically_addressable_not_verified_here(self):
        self.assertEqual(len(RECEIPT["originating_artifact_zip_sha256"]),64)
        self.assertEqual(len(RECEIPT["recorded_member_sha256"]),64)
        self.assertEqual(RECEIPT["source_type"],
                         "DERIVED_FROM_REAL_PRIOR_GAME_ENGINE_TELEMETRY")

    def test_no_false_material_creation_from_repeated_action(self):
        rows=RECEIPT["first_three_unproductive_attempts"]
        self.assertEqual(rows[0]["wood_before"],1)
        self.assertEqual(rows[-1]["wood_after"],1)
        self.assertFalse(RECEIPT["fabricated_live_availability"])
        self.assertEqual(RECEIPT["real_human_survival_inferences"],0)


if __name__=="__main__":
    unittest.main()
