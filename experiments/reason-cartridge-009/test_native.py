import unittest

from native import ORIGINAL_DOGRAM_COMMIT, pin, specimen
from source import Case,FAMILIES,bfs


class NativeSourceChecks(unittest.TestCase):
    def test_source_reader_is_exact_and_original_commit_is_pinned(self):
        self.assertEqual(len(ORIGINAL_DOGRAM_COMMIT),40)
        self.assertEqual(len(pin()),40)

    def test_two_real_source_topologies_generate_native_ablation_contract(self):
        for family in FAMILIES:
            for mask in range(32):
                sp=specimen(family,mask)
                self.assertEqual(sp["operator"],"ablate")
                self.assertEqual(sp["inputs"]["target"],
                                 {"kind":"edge","source":"U","target":"V"})
                self.assertEqual(sp["inputs"]["requested_targets"],[["S","T"]])
                self.assertIn(["U","V"],sp["inputs"]["graph"]["edges"])
                self.assertEqual(len(sp["inputs"]["graph"]["nodes"]),7)
                self.assertFalse(sp["metadata"]["source_world_authentication"])

    def test_source_truth_is_not_native_provenance(self):
        for family in FAMILIES:
            self.assertGreater(sum(bfs(Case(m,family)) for m in range(32)),0)
            self.assertLess(sum(bfs(Case(m,family)) for m in range(32)),32)


if __name__=="__main__":
    unittest.main()
