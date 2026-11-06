import unittest
from native import specimen, pin, ORIGINAL_DOGRAM_COMMIT
from pupil import digest
from source import Case, bfs_truth


class NativePreparationTests(unittest.TestCase):
    def test_original_source_is_pinned(self):
        self.assertEqual(len(pin()),40)
        self.assertEqual(len(ORIGINAL_DOGRAM_COMMIT),40)

    def test_isolated_decoy_edge_does_not_change_target_route(self):
        for mask in range(32):
            sp=specimen(mask)
            self.assertEqual(sp["operator"],"ablate")
            self.assertEqual(sp["inputs"]["target"],
                             {"kind":"edge","source":"U","target":"V"})
            self.assertIn(["U","V"],sp["inputs"]["graph"]["edges"])
            self.assertEqual(sp["inputs"]["requested_targets"],[["S","T"]])
            self.assertEqual(sp["metadata"]["independent_world_witness"],False)
            self.assertEqual(len(digest(sp)),64)

    def test_source_witnesses_include_both_positive_and_negative_cases(self):
        self.assertEqual(sum(bfs_truth(Case(mask)) for mask in range(32)),11)
        self.assertEqual(sum(not bfs_truth(Case(mask)) for mask in range(32)),21)


if __name__=="__main__":
    unittest.main()
