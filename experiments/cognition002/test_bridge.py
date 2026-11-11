"""COGNITION-002 source/authority and cross-day activation falsifiers."""
import json
import tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import unittest

from bridge import (integrated_demo, understory_fixture, public_free_graph,
                    validate_understory_owner, council_vs_single, _fg_native)
from circuit import (AppState, demo_book)


def allowed():
    return AppState(True,True,50,False,94,True,37.0,.14,"abundant")


class CrossroadsTests(unittest.TestCase):
    def test_source_native_free_graph_packet(self):
        packet=public_free_graph(demo_book(),"What independent observation can test the link?")
        _,_,validate=_fg_native()
        self.assertEqual(validate(packet),[])
        self.assertEqual(len(packet["nodes"]),4)
        self.assertEqual(len(packet["links"]),3)
        self.assertTrue(all(x["verb"]=="connects" for x in packet["links"]))
        self.assertTrue(all(x["status"]=="unresolved" for x in packet["links"]))
        self.assertTrue(all(x["authority"]=="none" for x in packet["links"]))
        self.assertEqual(packet["task_world_cut"]["status"],"unresolved")
        self.assertFalse(any("constitutes"==x["verb"] for x in packet["links"]))

    def test_packet_tamper_is_detected_by_native_validator(self):
        packet=public_free_graph(demo_book(),"Falsify connection")
        _,_,validate=_fg_native()
        packet["links"][0]["status"]="locally-adopted"
        self.assertTrue(validate(packet))
        packet["links"][0]["status"]="unresolved"
        packet["links"][0]["authority"]="owner-local"
        self.assertTrue(validate(packet))

    def test_historical_activation_never_overwrites_original(self):
        book=demo_book()
        before=[r.public() for r in book.rows]
        packet=understory_fixture(book)
        self.assertEqual([r["family"] for r in packet["records"]],
                         ["contact","contact","association","activation"])
        self.assertEqual(packet["records"][2]["status"],"unresolved")
        self.assertEqual(packet["records"][3]["trace_refs"],
                         [packet["records"][2]["id"]])
        self.assertEqual([r.public() for r in book.rows],before)
        self.assertFalse(any(r.get("canon",False) for r in packet["records"]))

    def test_understory_contact_times_are_valid_utc_hour(self):
        from datetime import datetime
        rows=understory_fixture(demo_book())["records"]
        for r in rows:
            parsed=datetime.fromisoformat(r["recorded_at"].replace("Z","+00:00"))
            self.assertEqual(parsed.utcoffset().total_seconds(),0)
        self.assertEqual(rows[1]["sensed_at"],"2026-11-10T10:00:00Z")

    def test_no_ignored_attention_inferred(self):
        records=understory_fixture(demo_book())["records"]
        self.assertFalse(any(r["family"]=="attention" for r in records))
        self.assertFalse(any(r.get("action")=="ignored" for r in records))

    def test_private_memento_missing_holds(self):
        packet=understory_fixture(demo_book())
        self.assertEqual(validate_understory_owner(packet,None)["status"],
                         "HOLD_NATIVE_MEMENTO_UNAVAILABLE")
        with tempfile.TemporaryDirectory() as temp:
            self.assertFalse(validate_understory_owner(packet,temp)["validated"])

    def test_forged_success_string_is_not_accepted(self):
        fixture=understory_fixture(demo_book())
        with tempfile.TemporaryDirectory() as temp:
            script=Path(temp)/"scripts/validate-understory-contemplation.mjs"
            script.parent.mkdir()
            script.write_text("// test stub, not an owner validator")
            stub=SimpleNamespace(returncode=0,stdout=json.dumps({
                "schema":"memento.understory-contemplation-check/v0",
                "status":"validated-nonconstituting",
                "source":"native-memento-understory-validator",
                "record_count":4,"record_ids":[],
                "digest":"sha256:"+"0"*64,"admission":"none","authority":"none",
                "writes":0,"real_world_actions":0
            }),stderr="")
            with patch("bridge.subprocess.run",return_value=stub):
                result=validate_understory_owner(fixture,temp)
            self.assertEqual(result["status"],"HOLD_NATIVE_MEMENTO_INCONSISTENT")

    def test_reject_unsanctioned_input(self):
        book=demo_book()
        from circuit import Record
        book.append(Record("real-123","2026-11-11","private-source","x","y","reported","fake"))
        with self.assertRaisesRegex(ValueError,"NOT_AUTHORIZED"):
            understory_fixture(book)

    def test_user_does_not_opt_in(self):
        output=integrated_demo(state=AppState(True,False,50,False,94,True,37.0,.14,"abundant"))
        self.assertEqual(output["status"],"HOLD_APP_OR_GHOT")
        self.assertIsNone(output["free_graph"])

    def test_app_hidden_or_user_active_holds(self):
        for state in [AppState(False,True,50,False,94,True,37.0,.14,"abundant"),
                      AppState(True,True,0,True,94,True,37.0,.14,"abundant")]:
            r=integrated_demo(state=state)
            self.assertEqual(r["status"],"HOLD_APP_OR_GHOT")

    def test_synthetic_integration_no_secret_import_or_output(self):
        out=integrated_demo(state=allowed())
        self.assertEqual(out["status"],"RESEARCH_PROPOSAL_ONLY")
        self.assertTrue(out["free_graph"]["native_validator"])
        self.assertFalse(out["native_memento"]["validated"])
        self.assertEqual(out["native_memento"]["status"],
                         "HOLD_NATIVE_MEMENTO_UNAVAILABLE")
        self.assertEqual(out["real_world_effects"],out["model_calls"])
        self.assertFalse(out["private_data_read"])
        self.assertFalse(out["app_deployed"])
        self.assertEqual(out["understory"]["admission"],"none")

    def test_fair_question_budget_and_no_fabricated_winner(self):
        x=council_vs_single(demo_book())
        self.assertEqual(x["budget_each"],5)
        self.assertEqual(len(x["single_critic"]),5)
        self.assertEqual(len(x["five_lens_council"]),5)
        self.assertTrue(x["successes_not_measured"])
        self.assertEqual(x["verified_downstream_successes"],
                         {"single_critic":0,"five_lens_council":0})
        self.assertEqual(len({y["perspective"] for y in x["five_lens_council"]}),5)

    def test_no_private_understory_contents_enter_graph(self):
        result=integrated_demo(state=allowed())
        graph=result["free_graph"]["graph"]
        txt=json.dumps(graph)
        self.assertNotIn("memento.understory-record",txt)
        self.assertNotIn("cognition002-contact-",txt)
        self.assertNotIn("UNDERSTORY_OWNER_CURRENT_FACT",txt)
        self.assertFalse(any(x["source_class"]=="world-head" for x in graph["sources"]))


if __name__=="__main__":
    unittest.main()
