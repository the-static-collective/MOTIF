"""Future-growth branch census tests: synthetic extra/moved/vanished pages."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import discovery


class DiscoveryTests(unittest.TestCase):
    def test_frozen_inventory_is_150_branches_total_including_main(self):
        observed = discovery.snapshot(discovery.from_frozen_inventory(),
                                      observed_at="FROZEN_FIXTURE")
        self.assertEqual(observed["branches_total"], 150)
        self.assertEqual(observed["cartridges_indexed_non_executable"], 149)
        self.assertTrue(all(not p["executable"] for p in observed["passports"]))

    def test_live_shape_expands_when_new_branches_appear_after_149(self):
        source = list(discovery.from_frozen_inventory())
        source += [("experiment/future-1", "1"*40),
                   ("experiment/future-2", "2"*40),
                   ("experiment/future-3", "3"*40)]
        pages = [[{"name": n, "commit": {"sha": sha}}
                  for n, sha in source[i:i+100]]
                 for i in range(0,len(source),100)]
        counts = []
        def fetch(page, size):
            self.assertEqual(size, 100)
            counts.append(page)
            return pages[page-1] if page <= len(pages) else []
        got = discovery.get_branches(fetch)
        self.assertEqual(len(got), 153)
        self.assertEqual(counts, [1,2])
        newer = discovery.snapshot(got, observed_at="AFTER")
        older = discovery.snapshot(discovery.from_frozen_inventory(),
                                   observed_at="BEFORE")
        self.assertEqual(newer["cartridges_indexed_non_executable"],152)
        self.assertEqual(discovery.delta(older,newer)["added"],
                         ["experiment/future-1","experiment/future-2",
                          "experiment/future-3"])
        self.assertTrue(all(not p["executable"] for p in newer["passports"]))

    def test_detects_branch_movement_but_preserves_old_snapshot(self):
        original = list(discovery.from_frozen_inventory())
        a = discovery.snapshot(tuple(original), observed_at="T0")
        moved = [(r, "f"*40 if r=="experiment/geometry-013-self-redesigning-instrument"
                  else sha) for r,sha in original]
        b = discovery.snapshot(tuple(moved), observed_at="T1")
        self.assertEqual(discovery.delta(a,b)["moved"],
                         ["experiment/geometry-013-self-redesigning-instrument"])
        self.assertNotEqual(a["passports"],b["passports"])

    def test_no_truncation_if_a_page_is_exactly_full(self):
        def fetch(page,size):
            return [{"name": f"experiment/new-{page}-{i}",
                     "commit":{"sha":"a"*40}} for i in range(size)]
        with patch.object(discovery, "MAX_PAGES",2):
            with self.assertRaisesRegex(discovery.DiscoveryHOLD,"truncated"):
                discovery.get_branches(fetch)

    def test_duplicate_branch_is_refused(self):
        x={"name":"experiment/same","commit":{"sha":"1"*40}}
        with self.assertRaisesRegex(discovery.DiscoveryHOLD,"duplicate"):
            discovery.get_branches(lambda page,size:[x,x])

    def test_census_cannot_execute_code(self):
        r=discovery.passport("experiment/later","d"*40)
        self.assertEqual(r["status"], "INDEXED_NON_EXECUTABLE")
        self.assertFalse(r["executable"])
        self.assertEqual(r["authority"], "NONE")

    def test_corrupt_payload_refused(self):
        for row in (
            {"name":"../evil","commit":{"sha":"a"*40}},
            {"name":"experiment/fake","commit":{"sha":"not-a-sha"}},
        ):
            with self.subTest(row=row):
                if row["name"]=="../evil":
                    # Names with path traversal are denied by a valid-ref check.
                    with self.assertRaises(discovery.DiscoveryHOLD):
                        discovery._validate([row])
                else:
                    with self.assertRaises(discovery.DiscoveryHOLD):
                        discovery._validate([row])


if __name__=="__main__":
    unittest.main()
