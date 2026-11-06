"""Falsifiers for a shared-world experiment: labels hidden, no fake synergy."""
import copy
import unittest
from pathlib import Path

import fixtures
import comparator


def native_fixture(public):
    rows=[]
    for c in public["cases"]:
        expected=fixtures.strong_classical(c)
        safe=expected!="HOLD" or not any(
            v in c["utterance"].lower() for v in ("send","publish","merge"))
        raw_v=None if c["records"] is None else True
        repaired_v=None if expected=="HOLD" and c["records"] is None else True
        row={
            "id":c["id"],
            "native_source_types":[
                "GEOM-013.Revision.measure",
                "THOUGHT-014.LanguageSpace.explore",
                "REASON-006.run_council"],
            "language":{"speech_act":"CHALLENGE" if safe else "HOLD_EFFECT_REQUEST",
                        "status":"TYPED_ONLY" if safe else "HOLD","safe":safe,
                        "baseline_safe":safe,
                        "pen_state":"UNCHANGED"},
            "geometry":{"raw":{"value":raw_v,"authority":"NONE","status":"LOCAL_SYNTHETIC_REPLAY"},
                        "repaired":{"value":repaired_v,"authority":"NONE","status":"LOCAL_SYNTHETIC_REPLAY"},
                        "learned_distinct_steps":2},
            "reason":{"raw":{"conclusion":"PROVED_REACHABLE",
                             "status":"CERTIFIED_SYNTHETIC_GRAPH_DECISION",
                             "source_revision":"test-revision"},
                      "repaired":{"conclusion":"PROVED_REACHABLE",
                             "status":"CERTIFIED_SYNTHETIC_GRAPH_DECISION",
                             "source_revision":"test-revision"}},
        }
        rows.append(row)
    return {
        "schema":"motif.shared-native-output.v1",
        "world":"ONE_SHARED_AUTHORED_SYNTHETIC_EVIDENCE_PACKET",
        "public_digest_sha256":comparator.canonical_digest(public),
        "authority":"NONE","external_action_executed":False,
        "language_model_kind":"TRAINED_NAIVE_BAYES_NOT_LLM",
        "language_model_calls":0,
        "results":rows
    }


class SharedEvidenceTests(unittest.TestCase):
    def test_fixture_labels_are_not_mounted_in_public_packet(self):
        public,labels=fixtures.generate()
        self.assertEqual(public["schema"],fixtures.SCHEMA)
        self.assertEqual(len(public["cases"]),32)
        self.assertTrue(all("expected" not in x for x in public["cases"]))
        self.assertNotIn("labels",public)
        self.assertEqual(labels["public_digest_sha256"],fixtures.digest(public))
        self.assertTrue(labels["labels_never_mounted_into_native_sandbox"])

    def test_same_seed_replay_and_different_seed_are_distinct(self):
        self.assertEqual(fixtures.generate(),fixtures.generate())
        self.assertNotEqual(fixtures.generate(seed=3),fixtures.generate(seed=4))

    def test_strong_classical_is_exact_on_author_generated_labels(self):
        for seed in (2026110615,2026110616,2026110617):
            pub,lbl=fixtures.generate(seed=seed)
            labels={x["id"]:x["expected"] for x in lbl["labels"]}
            self.assertTrue(all(fixtures.strong_classical(c)==labels[c["id"]]
                                for c in pub["cases"]))

    def test_bad_source_packet_checksum_holds(self):
        pub,hidden=fixtures.generate(count=8)
        native=native_fixture(pub)
        corrupted=copy.deepcopy(pub)
        corrupted["cases"][0]["gate_open"]=not corrupted["cases"][0]["gate_open"]
        with self.assertRaisesRegex(comparator.HOLD,"ground truth"):
            comparator.summarize(corrupted,hidden,native)

    def test_extra_or_missing_native_case_is_hold(self):
        pub,hidden=fixtures.generate(count=8)
        native=native_fixture(pub)
        native["results"].pop()
        with self.assertRaisesRegex(comparator.HOLD,"omitted"):
            comparator.summarize(pub,hidden,native)

    def test_fake_source_method_is_hold(self):
        pub,hidden=fixtures.generate(count=8)
        native=native_fixture(pub)
        native["results"][0]["native_source_types"]=["untrusted"]*3
        with self.assertRaisesRegex(comparator.HOLD,"original source"):
            comparator.summarize(pub,hidden,native)

    def test_native_authority_not_allowed(self):
        pub,hidden=fixtures.generate(count=8)
        native=native_fixture(pub)
        native["authority"]="PEN"
        with self.assertRaisesRegex(comparator.HOLD,"overclaimed"):
            comparator.summarize(pub,hidden,native)

    def test_no_docker_is_hold(self):
        from unittest.mock import patch
        with patch.object(comparator.shutil,"which",return_value=None):
            with self.assertRaisesRegex(comparator.HOLD,"Docker"):
                comparator.run(repo_root=Path.cwd(),count=8)

    def test_comparator_scores_classical_without_claiming_universal_gain(self):
        pub,hidden=fixtures.generate(count=8)
        native=native_fixture(pub)
        # Toy fixtures here do not represent actual native predictions; the
        # experiment's true CI will run original native algorithms.
        r=comparator.summarize(pub,hidden,native)
        self.assertEqual(r["count"],8)
        self.assertEqual(r["method_results"]["strong_classical_dedup_and_bfs"]["correct"],8)
        self.assertEqual(r["status"],"SOURCE_NATIVE_COMMON_WORLD_SYNTHETIC_EVALUATION")
        self.assertFalse(r["independent_human_labeled_real_data"])
        self.assertEqual(r["native_methods_invoked"],list(comparator.STAGES))

    def test_malformed_holdout_identity_denied(self):
        pub,hidden=fixtures.generate(count=8)
        hidden["labels"][0]["id"]="unseen-other-source"
        native=native_fixture(pub)
        with self.assertRaisesRegex(comparator.HOLD,"Invalid or absent"):
            comparator.summarize(pub,hidden,native)


if __name__=="__main__":
    unittest.main()
