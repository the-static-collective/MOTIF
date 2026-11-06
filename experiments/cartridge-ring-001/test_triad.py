"""Uninstalled branch refusal, three adapter schema checks, truthful abstention."""
import unittest
from pathlib import Path
from unittest.mock import patch

import triad


class TriadTests(unittest.TestCase):
    def test_three_independent_pinned_source_adapters(self):
        self.assertEqual(len(triad.ADAPTERS),3)
        self.assertEqual(len({x.commit for x in triad.ADAPTERS}),3)
        self.assertTrue(all(len(x.commit)==40 for x in triad.ADAPTERS))
        self.assertTrue(all(x.directory.startswith("experiments/")
                            for x in triad.ADAPTERS))

    def test_none_one_three_are_selected_only_as_requested(self):
        self.assertEqual(triad.choose(()), ())
        self.assertEqual(len(triad.choose(("thought.language-dev",))),1)
        self.assertEqual(len(triad.choose(tuple(x.id for x in triad.ADAPTERS))),3)
        with self.assertRaisesRegex(triad.HOLD,"unadmitted"):
            triad.choose(("experiment/new-future-branch",))
        with self.assertRaisesRegex(triad.HOLD,"Repeated"):
            triad.choose(("thought.language-dev","thought.language-dev"))

    def test_empty_request_does_not_run_native_code(self):
        with patch.object(triad,"probe",side_effect=AssertionError("should not run")):
            r=triad.run((),repo_root=Path.cwd())
        self.assertEqual(r["status"],"IDLE")
        self.assertEqual(r["selected"],[])
        self.assertFalse(r["external_action_executed"])

    def test_separate_receipts_never_become_shared_world_proof(self):
        def mock_probe(adapter,*,repo_root,python_image):
            return {"adapter":adapter.id,"source_commit":adapter.commit,
                    "this_is_synthetic_not_shared_real_evidence":True}
        with patch.object(triad,"probe",side_effect=mock_probe):
            a=triad.run(tuple(x.id for x in triad.ADAPTERS),
                        repo_root=Path.cwd(),concurrent=True)
            b=triad.run(tuple(x.id for x in triad.ADAPTERS),
                        repo_root=Path.cwd(),concurrent=False)
        self.assertEqual(a,b)
        self.assertEqual(len(a["results"]),3)
        self.assertEqual(a["cross_method_compatibility"],"UNPROVEN")
        self.assertEqual(a["authority"],"NONE")
        self.assertEqual(a["automatically_approved_additional_branches"],0)

    def test_geometry_rejects_fake_measured_claims(self):
        g=triad.BY_ID["geometry.procedure-repair"]
        with self.assertRaisesRegex(triad.HOLD,"Geometry"):
            triad._validate(g,{"experiment":"GEOM-013 self-redesigning measurement instrument",
                               "state":"PENCIL","authority":"NONE",
                               "summary":{"inserted_steps":[]}})

    def test_language_model_development_does_not_install_candidate_rule(self):
        t=triad.BY_ID["thought.language-dev"]
        with self.assertRaisesRegex(triad.HOLD,"Language"):
            triad._validate(t,{"schema":"motif.thought014.demo.v1",
                                "installed":True,"staged_only":True,"authority":"NONE",
                                "language_frozen_correct":[1,2,3]})

    def test_reason_council_requires_explicit_no_external_action(self):
        r=triad.BY_ID["reason.proof-objection"]
        with self.assertRaisesRegex(triad.HOLD,"Reason"):
            triad._validate(r,{"schema":"motif.reason.commonwealth-benchmark.v1",
                               "real_world_authority":False,
                               "external_actions":True,"source_owner_tests":[{}]*5,
                               "native_foreign_teacher_mode":"NOT_RUN_LOCAL_ONLY"})

    def test_no_docker_is_a_hold_not_an_unsafe_fallback(self):
        with patch.object(triad.shutil,"which",return_value=None):
            with self.assertRaisesRegex(triad.HOLD,"Docker"):
                triad.probe(triad.ADAPTERS[0],repo_root=Path.cwd(),
                            python_image="python:3.11-slim")


if __name__=="__main__":
    unittest.main()
