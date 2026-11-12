"""Contract tests for the bounded MEMENTO structural adapter."""
import json
import subprocess
import sys
import unittest
from pathlib import Path

from interop_stdio import process
from unknown_unknown import world


def pack(cases):
    return [{"identity": e.identity, "x": e.x,
             "edges": [list(edge) for edge in e.edges],
             "outcome": e.outcome, "authorized": e.authorized} for e in cases]


def fixture():
    return {"schema": "motif018.memento-evidence/v0",
            "train": pack(world("path", "train")),
            "validation": pack(world("path", "validation")),
            "holdout": pack(world("path", "holdout"))}


class TestInterop(unittest.TestCase):
    def test_real_native_discovery(self):
        p = process(fixture())
        self.assertEqual(p["status"], "HOLD_FOR_HUMAN_REVIEW")
        self.assertEqual(p["selected_holdout"]["accuracy"], 1)
        self.assertEqual(p["classical_holdout"]["accuracy"], 1)
        self.assertEqual(p["surface_holdout"]["accuracy"], 0.5)
        self.assertEqual(p["external_actions"], 0)
        self.assertFalse(p["observation_authenticated"])
        self.assertFalse(p["selection_used_holdout"])

    def test_sealed_holdout_cannot_select_concept(self):
        original = fixture()
        initial = process(original)
        alternative = fixture()
        for row in alternative["holdout"]:
            row["outcome"] ^= 1
        changed = process(alternative)
        self.assertEqual(initial["cartridge"], changed["cartridge"])
        self.assertEqual(changed["selected_holdout"]["accuracy"], 0)

    def test_cross_split_id_collision_refused(self):
        item = fixture()
        item["holdout"][0]["identity"] = item["train"][0]["identity"]
        with self.assertRaisesRegex(ValueError, "CROSS_SPLIT"):
            process(item)

    def test_unexpected_fields_refused(self):
        item = fixture()
        item["train"][0]["secret_source_text"] = "PRIVATE"
        with self.assertRaisesRegex(ValueError, "BAD_ROW_SCHEMA"):
            process(item)

    def test_unbounded_edges_refused(self):
        item = fixture()
        item["train"][0]["edges"] *= 100
        with self.assertRaisesRegex(ValueError, "BAD_EDGE_LIST"):
            process(item)

    def test_binary_booleans_not_borrowed_as_measurements(self):
        item = fixture()
        item["train"][0]["outcome"] = True
        with self.assertRaisesRegex(ValueError, "NON_BINARY_OUTCOME"):
            process(item)

    def test_stdio_refusal_never_echos_payload(self):
        item = fixture()
        item["train"][0]["private_note"] = "DO_NOT_ECHO"
        result = subprocess.run(
            [sys.executable, str(Path(__file__).parent / "interop_stdio.py")],
            input=json.dumps(item), text=True, capture_output=True)
        self.assertEqual(result.returncode, 2)
        self.assertNotIn("DO_NOT_ECHO", result.stdout)
        self.assertEqual(json.loads(result.stdout)["authority"], "NONE")


if __name__ == "__main__":
    unittest.main()
