import json
import unittest

from discover import HOLD, digest
from trial import certified, bids
from source import deployment
from market import make_receipt
from handoff import CUT, draft, validate_draft


class SourceHandoffTests(unittest.TestCase):
    def setUp(self):
        self.method,self.receiver,_=certified()
        self.market=make_receipt(self.method,self.receiver,bids(),deployment(32))

    def test_review_only_packet_does_not_confer_graft_or_cannon_authority(self):
        raw=draft(self.method,self.market,self.receiver)
        p=validate_draft(raw,self.method,self.market,self.receiver)
        self.assertEqual(len(p["selected_public_source_paths"]),len(CUT))
        self.assertEqual(p["graft"]["target_donor_branch"],"NOT_CREATED")
        self.assertFalse(p["graft"]["approved_for_public_graft"])
        self.assertEqual(p["cannon"]["state"],"NOT_CANON")
        self.assertIsNone(p["cannon"]["selected_revision"])
        self.assertFalse(p["cannon"]["signature_supplied"])
        self.assertTrue(p["cannon"]["owner_selection_required"])
        self.assertFalse(p["GRAFT_called"])
        self.assertFalse(p["CANNON_called"])
        self.assertFalse(p["external_writes"])

    def test_forged_review_and_canon_admission_rejected_even_with_new_checksum(self):
        original=json.loads(draft(self.method,self.market,self.receiver))
        for kind in ("graft","cannon","source","execution"):
            changed=json.loads(json.dumps(original))
            if kind=="graft":
                changed["graft"]["approved_for_public_graft"]=True
            elif kind=="cannon":
                changed["cannon"]["state"]="OWNER_SELECTED"
            elif kind=="source":
                changed["selected_public_source_paths"][0]["git_blob_sha1"]="0"*40
            else:
                changed["external_writes"]=True
            changed["checksum_sha256"]=digest({k:v for k,v in changed.items()
                                              if k!="checksum_sha256"})
            with self.subTest(kind=kind),self.assertRaises(HOLD):
                validate_draft(json.dumps(changed),self.method,self.market,self.receiver)

    def test_bfs_one_off_winner_cannot_request_graft_review(self):
        one=make_receipt(self.method,self.receiver,bids(),deployment(1))
        with self.assertRaises(HOLD):
            draft(self.method,one,self.receiver)


if __name__=="__main__":
    unittest.main()
