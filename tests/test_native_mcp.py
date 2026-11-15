"""Public, no-secret MCP aperture integration tests against original MOTIF modules."""
import json
import threading
import unittest
import urllib.error
import urllib.request
from http.server import HTTPServer
from unittest.mock import patch

from api.mcp import (
    TOOLS_BY_NAME, VERSION, MAX_BODY, call_tool, dispatch, handler,
    public_branch_leads,
)

CASE = {
    "schema": "motif.reason-case/v1",
    "question": "Why did the imagined fence corner move?",
    "goal": "Choose a useful next observation in a synthetic drawing",
    "hypotheses": [
        {"id": "camera", "predictions": {"angle": "yes", "post": "no"}},
        {"id": "post", "predictions": {"angle": "no", "post": "yes"}},
        {"id": "corner", "predictions": {"angle": "no", "post": "no"}},
    ],
    "tests": [
        {"id": "angle", "cost": 0.04, "risk": 0},
        {"id": "post", "cost": 0.12, "risk": 0.1},
    ],
    "reports": [],
}


def call(method, params=None, id_=7):
    return dispatch({"jsonrpc": "2.0", "id": id_, "method": method,
                     "params": params or {}})


class NativeMcpTests(unittest.TestCase):
    def test_initialize(self):
        data = call("initialize", {"protocolVersion": "2025-06-18"})["result"]
        self.assertEqual(data["protocolVersion"], "2025-06-18")
        self.assertEqual(data["serverInfo"]["version"], VERSION)
        self.assertEqual(data["capabilities"]["tools"]["listChanged"], False)
        self.assertIn("original MOTIF main Python", data["instructions"])
        self.assertEqual(call("initialize", {"protocolVersion": "2026-07-28"})["result"]["protocolVersion"],
                         "2026-07-28")

    def test_list_only_read_tools(self):
        tools = call("tools/list")["result"]["tools"]
        self.assertEqual(len(tools), 5)
        self.assertEqual({row["name"] for row in tools}, set(TOOLS_BY_NAME))
        for spec in tools:
            self.assertTrue(spec["annotations"]["readOnlyHint"])
            self.assertFalse(spec["annotations"]["destructiveHint"])
        for bad in ("execute_reviewed", "forest_execute_reviewed", "write_memory",
                    "merge_branch", "run_native_method", "feedback"):
            self.assertNotIn(bad, TOOLS_BY_NAME)
            self.assertEqual(call("tools/call", {"name": bad})["error"]["code"], -32602)

    def test_actual_native_reason_spine(self):
        response = call("tools/call", {
            "name": "motif_analyze_case", "arguments": {"case": CASE}
        })
        output = response["result"]["structuredContent"]
        self.assertFalse(response["result"]["isError"])
        self.assertEqual(output["schema"], "motif.reason-spine/v1")
        self.assertEqual(output["result"], "PROPOSE_PROBE")
        self.assertEqual(output["next_probe"]["id"], "angle")
        self.assertEqual(output["external_action"], "NONE")
        self.assertEqual(output["truth_status"], "NO_REAL_WORLD_CAUSAL_VERIFICATION")
        self.assertEqual(len(output["roles"]), 5)

    def test_actual_native_baselines_no_llm_fiction(self):
        response = call("tools/call", {
            "name": "motif_compare_policies", "arguments": {"case": CASE}
        })
        out = response["result"]["structuredContent"]
        self.assertEqual(out["schema"], "motif.reason-spine-comparison/v1")
        self.assertEqual(out["fixed_classical"]["next_probe"]["id"], "angle")
        self.assertEqual(out["motif_spine"]["result"], "PROPOSE_PROBE")
        self.assertTrue(out["real_pretrained_llm"]["status"].startswith("NOT_RUN"))
        self.assertIn("NO_CLAIM", out["conclusion"])

    def test_actual_native_shannon_information_gain(self):
        out = call("tools/call", {"name": "motif_information_gain",
                                  "arguments": {"test_id": "angle",
                                                "hypotheses": CASE["hypotheses"]}})["result"]["structuredContent"]
        self.assertAlmostEqual(out["bits"], 0.91829583, places=7)
        self.assertIn("ASSUMED", out["truth_status"])

    def test_merge_is_advisory_never_action(self):
        evidence = {"pinned_source": True, "independent_tests": True,
                    "strong_baseline_compared": True,
                    "no_known_regressions": True, "owner_review": True,
                    "measured_transfer_gain": 0.17}
        out = call("tools/call", {"name": "motif_merge_review",
                                  "arguments": {"evidence": evidence}})["result"]["structuredContent"]
        self.assertEqual(out["verdict"], "RECOMMEND_MERGE_REVIEW")
        self.assertFalse(out["automatic_merge"])
        held = call("tools/call", {"name": "motif_merge_review",
                                  "arguments": {"evidence": {}}})["result"]["structuredContent"]
        self.assertEqual(held["verdict"], "KEEP_UNMERGED_USE_AS_HELD_SOURCE")

    def test_bad_inputs_hold_without_execution(self):
        bad = json.loads(json.dumps(CASE))
        bad["hypotheses"][0]["predictions"]["angle"] = "definitely"
        answer = call("tools/call", {"name": "motif_analyze_case",
                                     "arguments": {"case": bad}})["result"]
        self.assertTrue(answer["isError"])
        self.assertEqual(answer["structuredContent"]["status"], "HOLD")
        self.assertTrue(answer["structuredContent"]["no_external_action"])
        self.assertEqual(call("wrong/unknown")["error"]["code"], -32601)
        self.assertEqual(call("tools/call", {"name": "motif_analyze_case",
                                            "arguments": {"case": CASE, "ignore": True}})["result"]["isError"], True)
        self.assertIsNone(dispatch({"jsonrpc": "2.0", "method": "notifications/initialized"}))

    def test_git_source_only_pins_without_running_code(self):
        data = [
            {"name": "main", "commit": {"sha": "a"*40}},
            {"name": "experiment/reciprocal-004", "commit": {"sha": "b"*40}},
            {"name": "experiment/fence-003", "commit": {"sha": "c"*40}},
        ]
        class Fake:
            def read(self, n): return json.dumps(data).encode("utf-8")
            def __enter__(self): return self
            def __exit__(self, *args): pass
        with patch("api.mcp.urllib.request.urlopen", return_value=Fake()) as mocked:
            leads = public_branch_leads({"query": "reciprocal", "page": 1, "limit": 10})
        self.assertEqual(len(leads["leads"]), 1)
        self.assertEqual(leads["leads"][0]["sha"], "b"*40)
        self.assertEqual(leads["leads"][0]["status"], "PENCIL_SOURCE_POINTER_NOT_ADMITTED")
        self.assertEqual(leads["execution"], "NONE")
        self.assertEqual(leads["completeness"], "SINGLE_GITHUB_PAGE_NOT_WHOLE_FOREST")
        self.assertEqual(mocked.call_count, 1)
        with self.assertRaises(ValueError):
            public_branch_leads({"page": 51})
        with self.assertRaises(ValueError):
            public_branch_leads({"page": True})

    def test_no_database_arbitrary_origin_or_write_tools(self):
        script = __import__("inspect").getsource(__import__("api.mcp", fromlist=["handler"]))
        for bad in ["subprocess.run(", "os.system(", "eval(", "exec(", "docker run", "pickle.loads("]:
            self.assertNotIn(bad, script)
        self.assertNotIn("MOTIF_MCP_API_KEY", script)
        self.assertNotIn("SUPABASE_SERVICE_ROLE_KEY", script)

    def test_actual_http_streamable_json_rpc(self):
        server = HTTPServer(("127.0.0.1", 0), handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        url = "http://127.0.0.1:%d/mcp" % server.server_port
        try:
            payload = json.dumps({
                "jsonrpc": "2.0", "id": 4, "method": "tools/call",
                "params": {"name": "motif_analyze_case", "arguments": {"case": CASE}}
            }).encode()
            request = urllib.request.Request(url, payload,
                headers={"Content-Type": "application/json", "Accept": "application/json"})
            with urllib.request.urlopen(request, timeout=3) as response:
                self.assertEqual(response.status, 200)
                self.assertEqual(response.headers["Content-Type"], "application/json; charset=utf-8")
                answer = json.load(response)
                self.assertEqual(answer["result"]["structuredContent"]["next_probe"]["id"], "angle")
            # A live preview should have no running native worker and no stored session.
            with urllib.request.urlopen(url.replace("/mcp", "/health"), timeout=3) as response:
                health = json.load(response)
                self.assertEqual(health["status"], "READY_READONLY")
                self.assertEqual(health["forest_oauth_gateway"], "NOT_CONNECTED")
            with self.assertRaises(urllib.error.HTTPError) as err:
                urllib.request.urlopen(urllib.request.Request(url, data=b"x"*(MAX_BODY+1),
                    headers={"Content-Type": "application/json"}), timeout=3)
            self.assertEqual(err.exception.code, 413)
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=3)


if __name__ == "__main__":
    unittest.main()
