"""Source-checked hypergraph evidence prevents suppressing generated-parser failures."""
from __future__ import annotations
from copy import deepcopy
import unittest

import engine,synthesizer,evidence_graph


def example():
    spec=synthesizer.build(["char3","skip"],"bayes","factorized",0.0,2)
    program={
        "schema":synthesizer.SCHEMA,
        "source_train_sha256":"a"*64,
        "source_dev_sha256":"b"*64,
        "selected_program":spec,
        "selected_program_sha256":engine.digest(spec),
        "status":"FINITE_EXECUTABLE_PROGRAM_SEARCH_COMPLETED",
        "heldout_challenge_module_imported":False,
        "test_outcomes_consulted_during_search":False,
        "tool_execution_authority":"NONE",
        "found_beyond_seed_set":True,
        "external_action_executed":False,
        "candidate_programs_tried":120,
    }
    program["receipt_sha256"]=engine.digest(program)
    labels={
        "synthesized":[True,False],
        "atomic_seed":[False,False],
        "old_single_path_grammar":[False,False],
        "always_abstain":[False,False],
        "unsafe_permissive_foil":[False,False],
    }
    packets=[]
    for i in range(2):
        systems={}
        for name,booleans in labels.items():
            m={"count":2,"exact_frames":int(booleans[0])+int(booleans[1]),
               "decisive":1,"wrong_decisive":1,
               "unsafe_false_readonly":1 if name=="synthesized" and i==0 else 0}
            cases=[
                {"exact":booleans[0],
                 "false_readonly":m["unsafe_false_readonly"]==1,
                 "source_sha256":str(i+1)*64},
                {"exact":booleans[1],"false_readonly":False,
                 "source_sha256":str(i+1)*64},
            ]
            systems[name]={"metrics":m,"per_case":cases}
        packets.append({
            "heldout_source_packet_sha256":str(i+1)*64,
            "labels_not_used_for_program_search":True,
            "case_count":2,"systems":systems,
        })
    combined={}
    for name in labels:
        combined[name]={k:sum(p["systems"][name]["metrics"][k]
                               for p in packets)
                        for k in ("count","exact_frames","decisive",
                                  "wrong_decisive","unsafe_false_readonly")}
    bench={
        "schema":"motif.ring008.postfreeze-semantic-falsification.v1",
        "program_receipt_sha256":program["receipt_sha256"],
        "program_ast":spec,
        "test_packets":packets,
        "combined":combined,
        "external_action_executed":False,
        "new_native_executable_admissions":0,
        "authority":"NONE",
    }
    bench["receipt_sha256"]=engine.digest(bench)
    return program,bench


class HypergraphEvidenceTests(unittest.TestCase):
    def test_benefit_and_unsafe_confusion_both_retained(self):
        program,bench=example()
        g=evidence_graph.build(program,bench)
        self.assertEqual(g["schema"],evidence_graph.SCHEMA)
        self.assertEqual(len(g["hyperedges"]),2)
        self.assertTrue(g["source_falsification_preserved"])
        self.assertFalse(g["true_general_language_invention_verified"])
        self.assertEqual(g["real_world_algorithm_permission_promotions"],0)
        self.assertEqual(g["hyperedges"][1]["synthesized_metrics"][
            "unsafe_false_readonly"],1)
        self.assertEqual(g["hyperedges"][1]["synthesized_minus_atomic"][
            "exact_frames"],2)
        self.assertGreaterEqual(len(g["hyperedges"][1]["heads"]),4)

    def test_rehashed_wrong_tally_is_still_rejected(self):
        program,bench=example()
        bench["test_packets"][0]["systems"]["synthesized"][
            "metrics"]["unsafe_false_readonly"]=0
        bench["receipt_sha256"]=engine.digest({
            k:v for k,v in bench.items() if k!="receipt_sha256"})
        with self.assertRaisesRegex(evidence_graph.HOLD,"Wrong error count"):
            evidence_graph.build(program,bench)

    def test_changed_development_program_source_is_rejected(self):
        program,bench=example()
        program["selected_program"]["ops"]=["word"]
        program["receipt_sha256"]=engine.digest({
            k:v for k,v in program.items() if k!="receipt_sha256"})
        with self.assertRaisesRegex(evidence_graph.HOLD,"Generated solution"):
            evidence_graph.build(program,bench)

    def test_duplicate_evaluation_source_is_rejected(self):
        program,bench=example()
        bench["test_packets"][1]["heldout_source_packet_sha256"]=(
            bench["test_packets"][0]["heldout_source_packet_sha256"])
        bench["receipt_sha256"]=engine.digest({
            k:v for k,v in bench.items() if k!="receipt_sha256"})
        with self.assertRaisesRegex(evidence_graph.HOLD,"Duplicate"):
            evidence_graph.build(program,bench)


if __name__=="__main__":
    unittest.main()
