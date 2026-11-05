"""Receipt-driven static desk quality gates."""
import json
import re
import unittest

from field_desk import payload, render


class DeskTests(unittest.TestCase):
    def test_fixture_examples_are_from_same_solver(self):
        cases = {c["id"]: c for c in payload()}
        self.assertEqual(len(cases), 7)
        self.assertEqual(cases["workshop"]["receipt"]["known_cost"], 3)
        self.assertEqual(cases["workshop-free"]["receipt"]["known_cost"], 1)
        self.assertEqual(cases["workshop-hold"]["receipt"]["status"],
                         "HOLD_UNVERIFIED_BRIDGE")
        self.assertEqual(cases["food"]["receipt"]["known_minutes"], 14)
        self.assertEqual(cases["food-urgent"]["receipt"]["status"],
                         "ABSTAIN_NO_BOUNDED_BRIDGE")
        self.assertEqual(cases["relay"]["receipt"]["status"],
                         "PROPOSED_SYNTHETIC_ONLY")
        self.assertEqual(cases["relay-hold"]["receipt"]["status"],
                         "HOLD_UNVERIFIED_BRIDGE")

    def test_standalone_file_has_no_network_dependencies(self):
        html = render()
        self.assertIn('id="case-data"', html)
        self.assertIn('aria-label="Synthetic scenario selector"', html)
        self.assertNotIn("<script src=", html)
        self.assertNotIn("https://", html)
        self.assertNotIn("fetch(", html)
        self.assertNotIn("XMLHttpRequest", html)
        self.assertNotIn("analytics", html.lower().split("<footer>")[0])
        self.assertEqual(html.count("<!doctype html>"), 1)

    def test_embedded_json_is_bounded_and_decodes(self):
        html = render()
        match = re.search(
            r'<script type="application/json" id="case-data">(.*?)</script>',
            html, re.DOTALL)
        self.assertIsNotNone(match)
        records = json.loads(match.group(1))
        self.assertEqual(len(records), 7)
        self.assertEqual(records[0]["receipt"]["schema"],
                         "motif.bridge-synthesis/v0")
        self.assertLess(len(html), 300_000)

    def test_no_outbound_contact_claims(self):
        for case in payload():
            card = case["card"]
            if card["state"] == "DRAFT_NOT_SENT":
                self.assertTrue(card["no_auto_contact"])
                self.assertTrue(card["requires_human_review"])


if __name__ == "__main__":
    unittest.main()
