import unittest
import importlib.util
import json
from pathlib import Path
spec=importlib.util.spec_from_file_location("meta017",Path(__file__).with_name("meta_diagnostic.py"))
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
ROOT=Path(__file__).resolve().parents[2]
def cards():
    return (json.loads((ROOT/"016/evidence/actual-watershed-2026-11-05.json").read_text()),
            json.loads((ROOT/"017/evidence/first-real-event-2026-11-05.json").read_text()))

class MetaLessons(unittest.TestCase):
    def test_real_research_cards_explicitly_capture_both_losses(self):
        a,b=cards()
        out=m.examine(a,b)
        self.assertEqual(out["wins_on_test"],{"016_low_flow":"persistence","017_historical_event":"cross_gauges"})
        self.assertFalse(out["caution_outperformed_legacy_on_017"])
        self.assertEqual(len(out["lessons"]),3)
        self.assertTrue(out["diagnostic_is_fallible"])
        self.assertEqual(out["lessons"][1]["evidence"]["fallback_hours"],74)
        self.assertEqual(out["lessons"][2]["evidence"]["complete_hours"],117)
        self.assertFalse(out["automatic_promotion"])
        self.assertEqual(out["next_model_admission"],"HOLD_UNTIL_INDEPENDENT_EVENT_REPLICATION")

    def test_forged_wins_and_bad_denominators_refuse(self):
        import copy
        a,b=cards()
        for change in (
            lambda x:x.update(authority=True),
            lambda x:x.update(matched_test_hours=200),
            lambda x:x.update(cautious_vs_old_error_reduction_cfs=99999),
            lambda x:x["candidate_event_mae_cfs"].update(old_selection=float("nan"))
        ):
            fake=copy.deepcopy(b)
            change(fake)
            with self.assertRaises(m.HOLD):
                m.examine(a,fake)

    def test_corrupt_016_refused_and_result_deterministic(self):
        a,b=cards()
        x=m.examine(a,b)
        self.assertEqual(x,m.examine(a,b))
        a["automatic_promotion"]=True
        with self.assertRaises(m.HOLD):
            m.examine(a,b)

if __name__=="__main__":
    unittest.main()
