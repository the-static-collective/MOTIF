import json
import unittest
from compiler import HOLD
from trial import certified, offers
from source import deployment
from market import packet
from bridge006 import transfer, current_pin

class CommonwealthBridgeTests(unittest.TestCase):
    def setUp(self):
        self.method,self.receiver,_=certified()

    def test_verified_capability_is_one_new_contribution_not_a_new_fact(self):
        raw=packet(self.method,self.receiver,offers(),deployment(16))
        result=transfer(raw,self.receiver)
        self.assertEqual(result["prior_owner"],current_pin())
        self.assertEqual(result["new_credit"],1)
        self.assertEqual(result["repeated_credit"],0)
        self.assertEqual(result["world_facts"],0)
        self.assertFalse(result["external_execution"])

    def test_one_off_query_cannot_masquerade_as_new_capability(self):
        raw=packet(self.method,self.receiver,offers(),deployment(1))
        with self.assertRaises(HOLD):
            transfer(raw,self.receiver)

    def test_unreviewed_document_cannot_enter_prior_ledger(self):
        raw=packet(self.method,self.receiver,offers(),deployment(16))
        tampered=json.loads(raw)
        tampered["receipt"]["independently_verified_correct"]=1000
        with self.assertRaises(HOLD):
            transfer(json.dumps(tampered),self.receiver)

if __name__=="__main__":
    unittest.main()
