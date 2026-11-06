"""Integration tests for live index first, selective method work second."""
import unittest
from pathlib import Path
from unittest.mock import patch

import living_ring


def page_with_three_future(page,size):
    refs=[
        {"name":"main","commit":{"sha":"a"*40}},
        {"name":"experiment/future-triple-1","commit":{"sha":"b"*40}},
        {"name":"experiment/future-triple-2","commit":{"sha":"c"*40}},
        {"name":"experiment/future-triple-3","commit":{"sha":"d"*40}},
    ]
    return refs[(page-1)*size:page*size]


class LivingRingTests(unittest.TestCase):
    def test_future_branches_appear_without_any_new_code_installation(self):
        with patch.object(living_ring.ring,"run",
                          side_effect=AssertionError("no reason requested")), \
             patch.object(living_ring.triad,"run",
                          side_effect=AssertionError("no specialist requested")):
            r=living_ring.session(fetch_page=page_with_three_future,
                                  observed_at="FIXTURE")
        self.assertEqual(r["source_only_cartridges_addressable"],3)
        self.assertEqual(r["branches_observed_total"],4)
        self.assertIsNone(r["ring_work"])
        self.assertIsNone(r["native_specialist_work"])
        self.assertEqual(r["authority"],"NONE")
        self.assertTrue(r["this_census_does_not_admit_new_code"])

    def test_selects_one_installed_handler_only_when_requested(self):
        # Actual already-approved original RING-001 local module.
        r=living_ring.session(fetch_page=page_with_three_future,
                              read_outputs=("verbs",),observed_at="FIXTURE")
        self.assertEqual(len(r["ring_work"]["selected_cartridges"]),1)
        self.assertEqual(r["ring_work"]["stage"],"PROPOSED")
        self.assertIsNone(r["native_specialist_work"])

    def test_specialist_selection_is_declared_until_native_is_explicit(self):
        r=living_ring.session(fetch_page=page_with_three_future,
                              specialist_ids=("thought.language-dev",),
                              observed_at="FIXTURE")
        self.assertEqual(r["native_specialist_work"]["status"],"DECLARED_ONLY")
        self.assertEqual(r["selected_specialists"],["thought.language-dev"])

    def test_run_native_only_calls_explicit_allowlist(self):
        def native_methods(*args,**kwargs):
            self.assertEqual(args[0],("reason.proof-objection",))
            return {"status":"SOURCE_NATIVE_SYNTHETIC_TRIAL","selected":list(args[0])}
        with patch.object(living_ring.triad,"run",side_effect=native_methods):
            r=living_ring.session(fetch_page=page_with_three_future,
                                  specialist_ids=("reason.proof-objection",),
                                  native=True,observed_at="FIXTURE")
        self.assertEqual(r["native_specialist_work"]["selected"],
                         ["reason.proof-objection"])

    def test_bad_ref_never_becomes_executable_handler(self):
        with self.assertRaises(living_ring.source_reader.HOLD):
            living_ring.session(fetch_page=page_with_three_future,
                                source_ref="experiment/future-nonexistent",
                                source_query="hello",observed_at="FIXTURE")


if __name__=="__main__":
    unittest.main()
