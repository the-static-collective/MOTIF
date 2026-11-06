"""Adversarial identity, ambiguity, multiplicity and replay tests."""
import json
import tempfile
import unittest
from pathlib import Path

from adapter import import_ledger_nodes
from demo import main
from field import FieldError, ThoughtField, canonical


class ThoughtFieldTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "field.jsonl"
        self.f = ThoughtField(self.path)
        self.f.concept("c:home-shelter", "home", "physical dwelling", "source:author")
        self.f.concept("c:home-belonging", "home", "sense of belonging", "source:author")
        self.f.expression("e:home", "home", "source:text", "ambiguous utterance")
        self.f.manifest("m:shelter", "c:home-shelter", "logistics", "resource")
        self.f.manifest("m:belong", "c:home-belonging", "culture", "goal")
        self.f.view("v:assoc", "association", "exploration")
        self.f.view("v:hex", "flower_hex", "alternative view")
        self.f.view("v:none", "NONE", "non-geometric review")

    def test_ambiguous_identical_labels_never_auto_merge(self):
        self.assertEqual(len(self.f.concepts), 2)
        self.assertEqual(self.f.concepts["c:home-shelter"]["label"],
                         self.f.concepts["c:home-belonging"]["label"])
        self.assertNotEqual(self.f.manifestations["m:shelter"]["concept_id"],
                            self.f.manifestations["m:belong"]["concept_id"])

    def test_one_expression_can_have_multiple_proposed_referents(self):
        self.f.propose_referent("r:shelter", "e:home", "c:home-shelter", "maybe literal", "source:author")
        self.f.propose_referent("r:belong", "e:home", "c:home-belonging", "maybe figurative", "source:author")
        self.assertEqual(len(self.f.referents), 2)
        self.assertTrue(all(r["status"] == "HYPOTHESIS_ONLY" for r in self.f.referents.values()))

    def test_nonfungible_manifestation_fork_retains_identity_and_lineage(self):
        self.f.manifest("m:next", "c:home-shelter", "later planning", "goal", "CONCRETE_PENCIL", "m:shelter")
        self.assertEqual(self.f.manifestations["m:next"]["parent_id"], "m:shelter")
        self.assertEqual(self.f.manifestations["m:next"]["concept_id"], "c:home-shelter")
        with self.assertRaisesRegex(FieldError, "switch concept identity"):
            self.f.manifest("m:bad", "c:home-belonging", "later", "goal", parent_id="m:shelter")
        self.assertNotIn("m:bad", self.f.manifestations)

    def test_many_placements_same_manifestation_same_view_and_other_view(self):
        self.f.place("p:one", "m:shelter", "v:assoc", -1, 0, "appearance one")
        self.f.place("p:two", "m:shelter", "v:assoc", +1, 0, "appearance two")
        self.f.place("p:three", "m:shelter", "v:hex", 0, 1, "third placement")
        result = self.f.occurrences("c:home-shelter")
        self.assertEqual(result["manifestation_ids"], ["m:shelter"])
        self.assertEqual(len(result["placements"]), 3)
        self.assertEqual(len({p["id"] for p in result["placements"]}), 3)

    def test_geometry_changes_do_not_modify_semantics(self):
        before = canonical(self.f.semantic_snapshot())
        self.f.place("p:a", "m:shelter", "v:assoc", 0, 0, "initial drawing")
        self.f.place("p:b", "m:shelter", "v:hex", 12, -9, "very far from other idea")
        self.f.move("p:a", 1000000, -1000000, "drift", expected_revision=1)
        self.f.remove_placement("p:b", "no longer useful")
        self.assertEqual(before, canonical(self.f.semantic_snapshot()))
        self.assertEqual(self.f.concepts["c:home-shelter"]["revision"], 1)
        self.assertEqual(self.f.placements["p:a"]["revision"], 2)
        self.assertFalse(self.f.placements["p:b"]["active"])

    def test_none_projection_stays_without_coordinates(self):
        self.f.place("p:none", "m:shelter", "v:none", None, None, "text-only reasoning")
        with self.assertRaisesRegex(FieldError, "NONE view"):
            self.f.place("p:bad", "m:shelter", "v:none", 0, 0, "illegal coordinates")
        with self.assertRaisesRegex(FieldError, "NONE view"):
            self.f.move("p:none", 1, 2, "move", expected_revision=1)

    def test_equivalence_is_only_a_proposal(self):
        self.f.propose_equivalence("eq:one", "c:home-shelter", "c:home-belonging",
                                   "source:analogy", "word overlap")
        self.assertEqual(self.f.equivalence_proposals["eq:one"]["status"], "HYPOTHESIS_ONLY")
        self.assertEqual(len(self.f.concepts), 2)
        with self.assertRaises(FieldError):
            self.f.propose_equivalence("eq:self", "c:home-shelter", "c:home-shelter",
                                       "source:analogy", "same already")

    def test_replay_exact_and_corruption_caught(self):
        self.f.place("p:a", "m:shelter", "v:assoc", 1, 2, "layout")
        self.f.move("p:a", 3, 4, "layout revision", expected_revision=1)
        self.assertEqual(ThoughtField(self.path).snapshot(), self.f.snapshot())
        content = self.path.read_text()
        self.path.write_text(content.replace('physical dwelling', 'physical shelter claim'))
        with self.assertRaisesRegex(FieldError, "hash chain"):
            ThoughtField(self.path)

    def test_stale_writers_blocked(self):
        other = ThoughtField(self.path)
        other.view("v:other", "association", "second author")
        with self.assertRaisesRegex(FieldError, "stale writer"):
            self.f.view("v:stale", "dependency", "stale writer")
        self.f.reload()
        self.f.view("v:current", "dependency", "reloaded")

    def test_duplicate_ids_missing_references_rejected(self):
        with self.assertRaisesRegex(FieldError, "duplicate concept"):
            self.f.concept("c:home-shelter", "again", "again", "source")
        with self.assertRaisesRegex(FieldError, "unknown manifestation"):
            self.f.place("p:missing", "unknown", "v:assoc", 0, 0, "phantom")
        with self.assertRaisesRegex(FieldError, "unknown concept"):
            self.f.propose_referent("r:missing", "e:home", "unknown", "why", "source")
        with self.assertRaises(FieldError):
            self.f.view("v:invalid", "quantum", "not a known lens")

    def test_bad_coordinates_and_revision_are_rejected(self):
        for x in (float("nan"), float("inf"), "1", True, 1000001):
            with self.assertRaises(FieldError):
                self.f.place("p:a", "m:shelter", "v:assoc", x, 0, "bad coordinate")
        self.f.place("p:a", "m:shelter", "v:assoc", 0, 0, "valid coordinate")
        with self.assertRaisesRegex(FieldError, "stale placement"):
            self.f.move("p:a", 1, 1, "wrong revision", expected_revision=2)
        self.assertEqual(self.f.placements["p:a"]["revision"], 1)

    def test_partial_final_line_rejected(self):
        self.path.write_bytes(self.path.read_bytes().rstrip(b"\n"))
        with self.assertRaisesRegex(FieldError, "partial"):
            ThoughtField(self.path)

    def test_concept_relabel_retains_stable_id_and_history(self):
        self.f.revise_concept("c:home-shelter", "dwelling", "physical home only", "clarify")
        self.assertEqual(self.f.manifestations["m:shelter"]["concept_id"], "c:home-shelter")
        self.assertEqual(self.f.concepts["c:home-shelter"]["revision"], 2)
        self.assertEqual(ThoughtField(self.path).semantic_snapshot(), self.f.semantic_snapshot())

    def test_legacy_ledger_nodes_import_as_distinct_not_pen(self):
        target = ThoughtField(Path(self.tmp.name) / "import.jsonl")
        snap = {"schema": "motif.thought-ledger.snapshot.v1",
                "nodes": [{"id": "a", "label": "Home", "kind": "concept"},
                           {"id": "b", "label": "Home", "kind": "concept"}]}
        results = import_ledger_nodes(snap, target)
        self.assertEqual(results, ["legacy:a", "legacy:b"])
        self.assertEqual(len(target.concepts), 2)
        self.assertEqual(target.semantic_snapshot()["external_authority"], "NONE")
        self.assertEqual(target.referents, {})
        self.assertEqual(target.equivalence_proposals, {})

    def test_bad_import_is_atomic_on_validate(self):
        target = ThoughtField(Path(self.tmp.name) / "import.jsonl")
        snap = {"schema": "motif.thought-ledger.snapshot.v1",
                "nodes": [{"id": "a", "label": "Home", "kind": "concept"},
                           {"id": "a", "label": "Same id", "kind": "concept"}]}
        with self.assertRaises(FieldError):
            import_ledger_nodes(snap, target)
        self.assertEqual(target.history(), [])

    def test_demo_complete_with_same_label_two_referents_and_replay(self):
        result = main()
        self.assertEqual(result["distinct_concepts_with_same_label"], 2)
        self.assertEqual(result["ambiguous_word_referent_candidates"], 2)
        self.assertEqual(result["shelter_manifestations"], 3)
        self.assertEqual(result["shelter_active_placements"], 3)
        self.assertTrue(result["semantic_invariant_under_layout_change"])
        self.assertTrue(result["exact_replay"])
        self.assertEqual(result["equivalence_status"], "HYPOTHESIS_ONLY")


if __name__ == "__main__":
    unittest.main()
