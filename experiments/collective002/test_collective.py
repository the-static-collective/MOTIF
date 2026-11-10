"""Falsification tests: topology, permission, provenance, spoofing, replay."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from demo import execute
from node import export
from protocol import AppendOnlyLedger, digest, import_cards, infer_path, sign, verify


def card(origin, fact, a, b, polarity="edge"):
    return {"kind": "source", "source_scope": "private-" + origin,
            "origin": origin, "fact_id": fact, "from": a, "to": b,
            "polarity": polarity, "epistemic_state": "asserted"}


class DistributedTrial(unittest.TestCase):
    def test_three_independent_processes_compose_full_path(self):
        run = execute()
        self.assertEqual(run["processes"], 3)
        self.assertEqual(run["events_replayed"], 2)
        p = run["result"]
        self.assertEqual(p["local_isolated_status"], "UNKNOWN_INSUFFICIENT_EVIDENCE")
        self.assertEqual(p["outcome"]["path"], ["A", "B", "C", "D"])
        self.assertEqual(len(p["outcome"]["evidence_ids"]), 3)
        self.assertEqual(p["source_count"], 3)
        self.assertEqual({x["peer"] for x in p["network_receipts"]}, {"b", "c"})
        self.assertFalse(p["tranch_kernel_accepted"])
        self.assertFalse(p["real_world_claim"])
        self.assertEqual(p["packet_digest"], digest({k:v for k,v in p.items() if k != "packet_digest"}))

    def test_missing_disclosure_stays_unknown_not_false(self):
        p = execute(withhold_b=True)["result"]
        self.assertEqual(p["outcome"]["status"], "UNKNOWN_INSUFFICIENT_EVIDENCE")
        self.assertEqual(p["source_count"], 2)

    def test_one_unavailable_donor_stays_unknown(self):
        p = execute(with_c=False)["result"]
        self.assertEqual(p["outcome"]["status"], "UNKNOWN_INSUFFICIENT_EVIDENCE")
        self.assertEqual(len(p["network_receipts"]), 1)

    def test_conflicting_witness_preserved_as_tension(self):
        p = execute(conflict=True)["result"]
        self.assertEqual(p["outcome"]["status"], "HOLD_CONTRADICTION")
        self.assertEqual(len(p["outcome"]["tensions"]), 1)
        self.assertEqual(p["outcome"]["tensions"][0]["from"], "B")
        self.assertEqual(p["outcome"]["tensions"][0]["to"], "C")

    def test_forwarded_duplicate_does_not_create_fake_support(self):
        a, b = card("a", "a1", "A", "B"), card("b", "b1", "B", "C")
        sources = import_cards([a, b, b], "private-a")
        self.assertEqual(len(sources), 2)
        self.assertEqual(infer_path(sources, "A", "C", "private-a")["status"], "PATH_SUPPORTED_BY_ASSERTIONS")

    def test_source_scope_does_not_become_cross_scope_edge(self):
        sources = import_cards([card("b", "b1", "B", "C")], "private-a")
        self.assertEqual(sources[0]["scopeId"], "private-a")
        self.assertEqual(sources[0]["content"]["transmitted_statement"]["source_scope"], "private-b")
        self.assertTrue(sources[0]["content"]["does_not_inherit_origin_authority"])
        with self.assertRaises(ValueError):
            infer_path(sources, "B", "C", "another-scope")

    def test_caller_cannot_skip_export_grant(self):
        cfg = {"id": "b", "scope": "private-b", "secret": "key-b",
               "claims": [{"fact_id": "b1", "from": "B", "to": "C", "polarity": "edge"}],
               "grants": {"a": []}, "trusted_requesters": {"a": "key-a"}}
        req = sign({"schema": "motif.collective002.request.v1", "requester": "a",
                    "recipient": "b", "request_id": "a" * 32, "purpose": "source-export"}, "key-a")
        result = verify(export(cfg, req), "key-b")
        self.assertEqual(result["cards"], [])
        req["body"]["recipient"] = "c"
        with self.assertRaises(ValueError):
            export(cfg, req)

    def test_toy_mac_rejects_forgery(self):
        packet = sign({"x": "source"}, "secret")
        packet["body"]["x"] = "invented"
        with self.assertRaises(ValueError):
            verify(packet, "secret")
        with self.assertRaises(ValueError):
            verify(sign({"x": "valid"}, "someone-else"), "secret")

    def test_history_is_append_only_verifiable_not_authority(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger = AppendOnlyLedger(Path(tmp) / "events.jsonl")
            ledger.append("source_reception", {"from": "b"})
            ledger.append("inference_proposal", {"adopted": False})
            self.assertEqual(len(ledger.replay()), 2)
            path = Path(tmp) / "events.jsonl"
            path.write_text(path.read_text().replace('"adopted":false', '"adopted":true'))
            with self.assertRaises(ValueError):
                ledger.replay()


if __name__ == "__main__":
    unittest.main()
