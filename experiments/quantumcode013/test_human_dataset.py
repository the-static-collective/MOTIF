"""QC-013 synthetic parser tests (real 100-episode dataset is not committed)."""
import io
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

import numpy as np
from human_dataset import analyze,as_replay,get_stats,members,preview


def fake_npz(*,bad=False):
    n=7
    fields={
        "action":np.asarray([0,5,8,11,5,0,0],np.int64),
        "done":np.asarray([False]*6+[True]),
        "player_pos":np.asarray([[0,0],[32,32],[32,32],[32,32],
                                  [33,32],[33,32],[34,32]],np.int64),
        "inventory_health":np.asarray([9]*7,np.int64),
        "inventory_food":np.asarray([0,9,9,8,8,8,8],np.int64),
        "inventory_drink":np.asarray([0,9,9,9,9,8,8],np.int64),
        "inventory_energy":np.asarray([0,9,9,9,9,9,8],np.int64),
        "inventory_wood":np.asarray([0,1,1,0,0,0,0],np.int64),
        "achivement_collect_wood":np.asarray([0,1,1,1,1,1,1],np.int64),
        "achivement_place_table":np.asarray([0,0,1,1,1,1,1],np.int64),
        "achivement_make_wood_pickaxe":np.asarray([0,0,0,1,1,1,1],np.int64),
    }
    if bad:
        fields["action"][2]=500
    blob=io.BytesIO()
    np.savez_compressed(blob,**fields)
    return blob.getvalue()


def fake_archive(path,blob=None,name="dataset/replay.npz"):
    with zipfile.ZipFile(path,"w") as z:
        z.writestr(name,blob or fake_npz())


class HumanReplayTests(unittest.TestCase):
    def test_initial_state_is_not_counted_as_an_action(self):
        with np.load(io.BytesIO(fake_npz()),allow_pickle=False) as a:
            r=get_stats(a)
        self.assertEqual(r["recorded_actions"],6)
        self.assertEqual(r["paired_steps"],5)
        self.assertEqual(r["first"]["collect_wood"],1)
        self.assertEqual(r["first"]["place_table"],2)
        self.assertEqual(r["first"]["make_wood_pickaxe"],3)

    def test_original_dataset_typo_is_explicitly_supported(self):
        with np.load(io.BytesIO(fake_npz()),allow_pickle=False) as a:
            r=get_stats(a)
        self.assertIn("make_wood_pickaxe",r["first"])

    def test_converting_real_style_npz_to_qc011_contiguous_replay(self):
        replay=as_replay(fake_npz(),"sample")
        self.assertEqual(len(replay.episodes),5)
        self.assertEqual(replay.episodes[0].action,"place_table")
        self.assertEqual(replay.episodes[1].action,"make_wood_pickaxe")
        self.assertEqual(replay.episodes[0].after.pin,
                         replay.episodes[1].before.pin)
        self.assertEqual(replay.episodes[0].source,"GAME_TELEMETRY")
        self.assertTrue(all(ep.game=="OTHER_GAME" for ep in replay.episodes))

    def test_outcome_success_only_new_achievement_is_observed(self):
        r=as_replay(fake_npz(),"sample")
        self.assertEqual(r.episodes[0].outcome,"SUCCESS")
        self.assertEqual(r.episodes[1].outcome,"SUCCESS")
        self.assertEqual(r.episodes[2].outcome,"INCONCLUSIVE")

    def test_replay_record_does_not_claim_human_physiology(self):
        replay=as_replay(fake_npz(),"sample")
        self.assertIn("expert_gameplay",replay.provenance)
        self.assertTrue(all(ep.after.hazards==() for ep in replay.episodes))

    def test_limits_allow_a_short_replay_without_skipping_transition(self):
        replay=as_replay(fake_npz(),"sample",max_steps=2)
        self.assertEqual(len(replay.episodes),2)

    def test_per_episode_summary_records_order_not_causal_proof(self):
        with tempfile.TemporaryDirectory() as t:
            path=Path(t)/"dataset.zip"
            fake_archive(path)
            result=analyze(path)
        self.assertEqual(result["episodes"],1)
        self.assertEqual(result["recorded_actions"],6)
        self.assertEqual(result["paired_steps"],5)
        self.assertFalse(result["ordered_achievement_hypotheses"])
        self.assertTrue(result["boundaries"]["temporal_precedence_not_causality"])

    def test_no_implicit_publication_or_crossing(self):
        with tempfile.TemporaryDirectory() as t:
            path=Path(t)/"dataset.zip"
            fake_archive(path)
            p=preview(path)
        self.assertFalse(p["crossing_sent"])
        self.assertEqual(p["real_world_actions"],0)
        self.assertEqual(p["reLATTE"],
                         "HOLD_FOR_SEPARATE_RELATTE_OWNER_REVIEW")

    def test_reject_invalid_file_outside_dataset_scope(self):
        with tempfile.TemporaryDirectory() as t:
            path=Path(t)/"dataset.zip"
            fake_archive(path,name="../bad.npz")
            with self.assertRaises(ValueError):
                analyze(path)

    def test_reject_unexpected_json_instead_of_npz(self):
        with tempfile.TemporaryDirectory() as t:
            path=Path(t)/"dataset.zip"
            fake_archive(path,name="dataset/bad.json")
            with self.assertRaises(ValueError):
                analyze(path)

    def test_reject_crafted_out_of_range_action(self):
        with np.load(io.BytesIO(fake_npz(bad=True)),allow_pickle=False) as a:
            with self.assertRaises(ValueError):
                get_stats(a)

    def test_reject_empty_episode_archive(self):
        with tempfile.TemporaryDirectory() as t:
            path=Path(t)/"dataset.zip"
            with zipfile.ZipFile(path,"w") as z:
                z.writestr("meta/","")
            with self.assertRaises(ValueError):
                analyze(path)

    def test_archive_receipt_is_immutable_for_same_bytes(self):
        with tempfile.TemporaryDirectory() as t:
            path=Path(t)/"dataset.zip"
            fake_archive(path)
            one=analyze(path)
            two=analyze(path)
        self.assertEqual(one["archive_sha256"],two["archive_sha256"])

    def test_source_file_is_not_embedded_in_profile(self):
        with tempfile.TemporaryDirectory() as t:
            path=Path(t)/"dataset.zip"
            fake_archive(path)
            r=analyze(path)
        self.assertNotIn("image",r)
        self.assertNotIn("player_names",r)
        self.assertEqual(r["source"],
                         "https://archive.org/details/crafter_human_dataset")


if __name__=="__main__":
    unittest.main()
