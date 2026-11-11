"""VOID-006 falsifiers: source-verified habit formation and interruptibility."""
import unittest
from copy import deepcopy
from procedural import (HabitBook, LocalEvidence, NewWorldOwner, POLICIES, DEV_SEEDS,
                        TEST_SEEDS, REGIMES, EpistemicLedger, public_route,
                        seal, run_case, benchmark, MIN_HABIT_REPETITIONS)


def sourced(kind, *, wave=1, gate="N", actual_gate="N", held=True, epoch=0):
    row = {"source": "AUTHOR_BUILT_FORTRESS_ENGINE", "kind": kind,
           "attempt": 1, "sequence": wave,
           "source_epoch": epoch}
    if kind == "DEFEND":
        row.update(wave=wave, actual_gate=actual_gate,
                   guessed_gate=gate, held=held, completed=False, lives_after=int(held))
    elif kind == "SONAR":
        row.update(wave=wave, gate=gate)
    elif kind == "RELAY":
        row.update(relay="A", facts=[[1,gate],[5,"N"],[9,"W"]], position=(3,2))
    row["seal"] = seal(row)
    return row


class ProceduralTests(unittest.TestCase):
    def test_scoped_new_seeds(self):
        self.assertEqual(len(TEST_SEEDS),20)
        self.assertTrue(set(DEV_SEEDS).isdisjoint(TEST_SEEDS))
        self.assertEqual(len(POLICIES),4)
        self.assertEqual(len(REGIMES),3)

    def test_no_reflex_from_hearsay_or_single_success(self):
        book = HabitBook()
        book.learn(sourced("RELAY",gate="E"))
        self.assertIsNone(book.reflex(1))
        book.learn(sourced("SONAR",gate="N"))
        self.assertIsNone(book.reflex(1))
        book.learn(sourced("DEFEND",wave=1,gate="N",actual_gate="N"))
        self.assertIsNone(book.reflex(1))
        book.learn(sourced("DEFEND",wave=1,gate="N",actual_gate="N"))
        self.assertEqual(book.reflex(1)["gate"],"N")
        self.assertEqual(book.reflex(1)["prior_confirmed_successes"],MIN_HABIT_REPETITIONS)

    def test_contiguous_chunk_and_verified_failure_breaks_it(self):
        book = HabitBook()
        for wave in (1,2,3):
            for _ in range(2):
                book.learn(sourced("DEFEND",wave=wave,gate="E",actual_gate="E"))
        self.assertEqual(book.chunks,((1,2,3),))
        self.assertTrue(book.reflex(2)["chunked"])
        book.learn(sourced("DEFEND",wave=2,gate="E",actual_gate="W",held=False,epoch=1))
        self.assertIsNone(book.reflex(2))
        self.assertFalse(book.chunks)
        self.assertTrue(book.reflex(1))
        self.assertTrue(book.reflex(3))
        self.assertGreater(book.invalidations,0)

    def test_sonar_contradiction_interrupts_before_defense(self):
        book = HabitBook()
        for _ in range(2):
            book.learn(sourced("DEFEND",wave=7,gate="S",actual_gate="S"))
        book.learn(sourced("SONAR",wave=7,gate="W",epoch=1))
        self.assertIsNone(book.reflex(7))

    def test_sealed_false_relay_not_promoted(self):
        book = HabitBook()
        for _ in range(2):
            book.learn(sourced("DEFEND",wave=1,gate="N",actual_gate="N"))
        book.learn(sourced("RELAY",gate="W",epoch=1))
        self.assertEqual(book.reflex(1)["gate"],"N")
        forged=deepcopy(sourced("DEFEND",wave=1))
        forged["actual_gate"]="W"
        with self.assertRaises(ValueError):
            book.learn(forged)
        self.assertEqual(book.reflex(1)["gate"],"N")

    def test_sparse_old_owner_fact_not_globally_erased(self):
        ledger = EpistemicLedger()
        local = LocalEvidence()
        r=sourced("DEFEND",wave=4,gate="E",actual_gate="E",epoch=0)
        ledger.learn(r);local.learn(r)
        self.assertEqual(local.confidence(ledger,4),1.0)
        for epoch in (1,2):
            notice={"source":"AUTHOR_BUILT_FORTRESS_ENGINE","kind":"RESET",
                    "attempt":epoch+1,"sequence":20+epoch,
                    "source_epoch":epoch,"position":(5,4),"sonar":1,"wave":1}
            notice["seal"]=seal(notice)
            ledger.learn(notice);local.learn(notice)
        self.assertGreaterEqual(local.confidence(ledger,4),.90)
        self.assertEqual(local.predict(ledger,4),"E")
        self.assertEqual(local.confidence(ledger,11),.25)

    def test_owner_never_leaks_secret_in_public_view(self):
        for regime in REGIMES:
            owner=NewWorldOwner(DEV_SEEDS[0],regime)
            view=owner.public_view()
            self.assertNotIn("_lanes",view)
            self.assertNotIn("changed_waves",view)
            self.assertNotIn("actual_gate",str(view))
            owner.begin()
            with self.assertRaises(RuntimeError):
                owner.read_relay()
            for move in public_route("A"):
                owner.walk(move)
            report=owner.read_relay()
            self.assertEqual(report["kind"],"RELAY")

    def test_game_run_preserves_receipts_and_attempt_accounting(self):
        for policy in POLICIES:
            row=run_case(DEV_SEEDS[0],"reactive_deceptive",policy,full=True)
            self.assertLessEqual(row["total_attempts"],14)
            self.assertEqual(row["restricted_attempts"],row["first_clear_attempt"] or 15)
            self.assertEqual(row["defenses"],
                             sum(sum(r["kind"]=="DEFEND" for r in a["receipts"])
                                 for a in row["attempts"]))
            self.assertEqual(row["deliberative_gate_lookups"]+row["automatic_defenses"],
                             row["defenses"])
            self.assertEqual(row["cleared_by_14"],row["first_clear_attempt"] is not None)
            self.assertEqual(row["seal"],seal({k:v for k,v in row.items() if k!="seal"}))

    def test_dev_benchmark_repeatable(self):
        a=benchmark("development",full=False)
        b=benchmark("development",full=False)
        self.assertEqual(a["seal"],b["seal"])
        self.assertEqual(a["cases"],len(DEV_SEEDS)*len(POLICIES)*len(REGIMES))
        self.assertEqual(len(a["paired"]),len(DEV_SEEDS)*len(REGIMES))
        self.assertTrue(all(x["external_actions"]==0 for x in a["rows"]))


if __name__=="__main__":
    unittest.main()
