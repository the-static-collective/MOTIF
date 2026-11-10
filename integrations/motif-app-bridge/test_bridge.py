import unittest
from bridge import MotifFunctionBridge, BridgeError


class BridgeTests(unittest.TestCase):
    def setUp(self):
        self.calls = []
        self.now = [100.]
        self.bridge = MotifFunctionBridge(
            lambda name, args: self.calls.append((name, args)) or {"ok": True},
            clock=lambda: self.now[0],
        )

    def test_only_reviewed_read_names_exposed(self):
        tools = [{"name": "forest_route", "inputSchema": {"type": "object", "properties": {}}},
                 {"name": "forest_execute_reviewed", "inputSchema": {"type": "object"}},
                 {"name": "new_branch_arbitrary_exec", "inputSchema": {"type": "object"}},
                 {"name": "forest_route", "inputSchema": {"type": "object"}}]
        self.assertEqual([x["name"] for x in self.bridge.model_functions(tools)], ["motif__forest_route"])

    def test_model_reads_and_cannot_write_even_with_approval_field(self):
        self.assertEqual(self.bridge.call_from_model("motif__forest_route", '{"budget":4}'), {"ok": True})
        self.assertEqual(self.calls, [("forest_route", {"budget": 4})])
        for tool in ("forest_execute_reviewed", "record_feedback", "new_branch_arbitrary_exec"):
            with self.assertRaises(BridgeError):
                self.bridge.call_from_model("motif__" + tool, {"approved": True})
        self.assertEqual(len(self.calls), 1)

    def test_requires_human_explicit_exact_one_time_approval(self):
        token = self.bridge.stage_review("forest_start_trial", {"goal": "A"})
        with self.assertRaises(BridgeError):
            self.bridge.call_from_ui("forest_start_trial", {"goal": "A"}, token)
        self.bridge.approve_from_ui(token)
        with self.assertRaises(BridgeError):
            self.bridge.call_from_ui("forest_start_trial", {"goal": "B"}, token)
        self.assertEqual(self.bridge.call_from_ui("forest_start_trial", {"goal": "A"}, token), {"ok": True})
        with self.assertRaises(BridgeError):
            self.bridge.call_from_ui("forest_start_trial", {"goal": "A"}, token)
        self.assertEqual(self.calls, [("forest_start_trial", {"goal": "A"})])

    def test_expiry_and_no_cross_tool_use(self):
        token = self.bridge.stage_review("forest_start_trial", {})
        self.bridge.approve_from_ui(token)
        with self.assertRaises(BridgeError):
            self.bridge.call_from_ui("execute_reviewed", {}, token)
        self.now[0] += 121
        with self.assertRaises(BridgeError):
            self.bridge.call_from_ui("forest_start_trial", {}, token)
        self.assertEqual(self.calls, [])

    def test_argument_limits_invalid_payloads(self):
        for value in ("[1]", "not json", [], {"x": float('nan')}, {"a": "X"*40000}):
            with self.assertRaises(BridgeError):
                self.bridge.call_from_model("motif__forest_route", value)
        self.assertEqual(self.calls, [])

    def test_schema_is_fail_closed(self):
        self.assertEqual(self.bridge.model_functions([
            {"name": "forest_goals", "inputSchema": {"type": "string"}},
            {"name": "forest_catalog", "inputSchema": []},
            {"name": "forest_route", "inputSchema": {"type": "object", "properties": {}}},
        ])[0]["name"], "motif__forest_route")


if __name__ == "__main__":
    unittest.main()
