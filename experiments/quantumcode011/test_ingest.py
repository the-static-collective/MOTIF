"""QC-011 local replay-intake tests, preserving rights, observation and consent."""
import json
from pathlib import Path
import tempfile
import unittest

from ingest import parse_bundle,read_bundle,preview_bundle,MAX_EPISODES
from game_replay import NO_REALWORLD


HERE=Path(__file__).parent


class ReplayIntakeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture=json.loads((HERE/"example_annotation.json").read_text())

    def test_sample_real_json_is_ingestible(self):
        r=parse_bundle(self.fixture)
        self.assertEqual(len(r.episodes),2)
        self.assertEqual(r.game,"LAST_OF_US_LIKE")
        self.assertEqual(r.episodes[0].after.pin,
                         r.episodes[1].before.pin)

    def test_instrumenting_annotation_never_decodes_video(self):
        p=preview_bundle(HERE/"example_annotation.json")
        self.assertFalse(p["actual_gameplay_video_decoded"])
        self.assertFalse(p["sent"])
        self.assertFalse(p["signed"])
        self.assertFalse(p["admitted"])
        self.assertEqual(p["real_world_actions"],0)

    def test_packet_is_relatte_hold_and_no_native_crossing(self):
        p=preview_bundle(HERE/"example_annotation.json")
        self.assertEqual(p["crossing_status"],
                         "HOLD_FOR_SEPARATE_RELATTE_OWNER_REVIEW")
        self.assertEqual(len(p["crossing_packet_sha256"]),64)

    def test_changes_stay_within_game_world(self):
        p=preview_bundle(HERE/"example_annotation.json")
        self.assertEqual(p["replay"]["conclusions"],
                         "GAME_HYPOTHESES_WITH_UNRESOLVED_CAUSALITY")

    def test_no_derived_research_without_consent(self):
        clone=json.loads(json.dumps(self.fixture))
        clone["consent_for_derived_research"]=False
        r=parse_bundle(clone)
        from game_replay import relatte_preview
        self.assertEqual(relatte_preview(r)["status"],
                         "REFUSE_NO_DERIVATION_CONSENT")

    def test_missing_keys_refuse_strictly(self):
        clone=json.loads(json.dumps(self.fixture))
        del clone["provenance"]
        with self.assertRaises(ValueError):
            parse_bundle(clone)

    def test_malicious_extra_tool_key_refused(self):
        clone=json.loads(json.dumps(self.fixture))
        clone["run_bash"]="curl unknown-server"
        with self.assertRaises(ValueError):
            parse_bundle(clone)

    def test_untrusted_video_url_not_fetchable(self):
        clone=json.loads(json.dumps(self.fixture))
        clone["video_url"]="https://example.org"
        with self.assertRaises(ValueError):
            parse_bundle(clone)

    def test_source_type_mismatch_does_not_upgrade_to_observed(self):
        clone=json.loads(json.dumps(self.fixture))
        clone["episodes"][0]["source"]="VISION_MODEL_UNVERIFIED"
        clone["episodes"][0]["certainty"]="OBSERVED"
        with self.assertRaises(ValueError):
            parse_bundle(clone)

    def test_partial_video_inference_can_be_marked_provisional(self):
        clone=json.loads(json.dumps(self.fixture))
        clone["episodes"][0]["source"]="VISION_MODEL_UNVERIFIED"
        clone["episodes"][0]["certainty"]="INFERRED"
        clone["episodes"][0]["rights"]="ANNOTATION_ONLY"
        r=parse_bundle(clone)
        from game_replay import next_questions
        self.assertTrue(any(q.kind=="VERIFY_VIEW"
                            for q in next_questions(r)))

    def test_malformed_resources_refused(self):
        clone=json.loads(json.dumps(self.fixture))
        clone["episodes"][0]["before"]["resources"]={"wood":9}
        with self.assertRaises(ValueError):
            parse_bundle(clone)

    def test_out_of_order_unwitnessed_state_transition_refuses(self):
        clone=json.loads(json.dumps(self.fixture))
        clone["episodes"][1]["before"]["capabilities"]=["mystery_item"]
        with self.assertRaises(ValueError):
            parse_bundle(clone)

    def test_empty_replay_refused(self):
        clone=json.loads(json.dumps(self.fixture))
        clone["episodes"]=[]
        with self.assertRaises(ValueError):
            parse_bundle(clone)

    def test_size_and_count_bounded(self):
        clone=json.loads(json.dumps(self.fixture))
        clone["episodes"]=clone["episodes"]*MAX_EPISODES
        with self.assertRaises(ValueError):
            parse_bundle(clone)

    def test_file_decoder_does_not_emit_unauthorized_effects(self):
        r=read_bundle(HERE/"example_annotation.json")
        self.assertEqual(r.episodes[0].rights,"SYNTHETIC")
        self.assertEqual(r.episodes[0].source,"SYNTHETIC_FIXTURE")

    def test_path_outbound_execution_not_supported(self):
        r=preview_bundle(HERE/"example_annotation.json")
        self.assertTrue(all(x!="REAL_WORLD"
                            for x in r["replay"].get("conclusions",{})))
        self.assertEqual(r["real_world_actions"],0)


if __name__=="__main__":
    unittest.main()
