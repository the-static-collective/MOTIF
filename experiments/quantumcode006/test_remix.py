"""QC-006 — adversarial semantics remix and graph-world representation tests."""
from dataclasses import replace
import unittest

import networkx as nx
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1] / 'quantumcode005'))

from remix import (
    SYMBOL, WHOLE, LOCAL, STATUS, MAX_COST, Expression, Lexicon,
    enumerate_meanings, interpret, make_before, owner_effect,
    fixture, discover, review, infer_delta, edge, Graph, report, seal,
)
import gardener
from foreign_worlds import hosts, topology
from classical_meanings import learn_classically, predict_classically, native_interpret


class RemixChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.train,cls.valid,cls.test=fixture()
        cls.proposal=discover(cls.train)
        cls.cert=review(cls.proposal,cls.train,cls.valid)
        cls.localtrain,cls.localvalid,_=gardener.fixtures("triangle")
        p=gardener.discover(cls.localtrain)
        cls.localcert=gardener.review(p,cls.localtrain,cls.localvalid)
        cls.lex=(Lexicon()
            .admit_global(SYMBOL,WHOLE,cls.cert,cls.train,cls.valid)
            .admit_local(SYMBOL,LOCAL,cls.localcert,cls.localtrain,cls.localvalid))

    def test_frozen_train_valid_test(self):
        self.assertEqual((len(self.train),len(self.valid),len(self.test)),
                         (12,12,16))
        self.assertEqual(len({r.evidence_id for r in
                              self.train+self.valid+self.test}),40)

    def test_symbolic_grammar_enumerates_many_candidates(self):
        programs=list(enumerate_meanings(MAX_COST))
        self.assertGreater(len(programs),50)
        self.assertTrue(all(p.valid() for p in programs))
        self.assertTrue(all(p.kind=="BOOL" for p in programs))
        self.assertTrue(all(p.cost<=MAX_COST for p in programs))

    def test_typed_expression_is_constructed_from_symbols(self):
        self.assertIsNotNone(self.proposal)
        self.assertEqual(self.proposal.program.kind,"BOOL")
        self.assertIn("ADJ(",self.proposal.program.notation())
        self.assertIn("MINUS(",self.proposal.program.notation())
        self.assertIn("ANY(",self.proposal.program.notation())

    def test_earlier_endpoint_language_could_not_detect_isolates(self):
        previous=report()["previous_language_collision"]
        self.assertEqual(previous,"HOLD_UNEXPRESSIBLE_IN_DECLARED_DSL")

    def test_binary_graph_symbols_are_not_magic_words(self):
        base,ab=make_before("p",9,0)
        with_isolate,_=make_before("p",9,1)
        self.assertFalse(interpret(self.proposal.program,base,ab))
        self.assertTrue(interpret(self.proposal.program,with_isolate,ab))

    def test_parity_shortcut_fails_both_classes(self):
        # Positive examples contain both odd and even graph sizes.
        # Negative path lengths span both parities.
        by_label={True:set(),False:set()}
        for row in self.train:
            before=row.before
            observed=len(before.vertices-used_vertices(before))>0
            by_label[observed].add(len(before.vertices)%2)
        self.assertEqual(by_label[True],{0,1})
        self.assertEqual(by_label[False],{0,1})

    def test_minimum_ast_cost_is_needed(self):
        self.assertEqual(self.proposal.program.cost,5)
        self.assertIsNone(discover(self.train,max_cost=4))

    def test_review_passed_independent_examples(self):
        self.assertEqual(self.cert.validation_count,12)
        self.assertEqual(self.cert.status,STATUS)

    def test_frozen_heldout_predicted_effects(self):
        correct=0
        for row in self.test:
            ab,effect=infer_delta(row)
            result=self.lex.ask(SYMBOL,WHOLE,row.before,ab)
            self.assertEqual(result["status"],STATUS)
            correct+=int(result["effect"]==effect.seal())
        self.assertEqual(correct,len(self.test))

    def test_two_semantics_for_same_symbol(self):
        self.assertEqual({m.symbol for m,_ in self.lex.entries},{SYMBOL})
        self.assertEqual({m.decoder for m,_ in self.lex.entries},{WHOLE,LOCAL})
        self.assertNotEqual(self.lex.entries[0][0].meaning,
                            self.lex.entries[1][0].meaning)

    def test_same_world_polysemy_changes_query(self):
        # Graph contains a triangle but no isolated node.
        graph=Graph.of({"a","b","c","d"},
                       {edge("a","b"),edge("b","c"),
                        edge("a","c"),edge("c","d")})
        global_result=self.lex.ask(SYMBOL,WHOLE,graph,("a","b"))
        local_result=self.lex.ask(SYMBOL,LOCAL,graph,("a","b"))
        self.assertFalse(global_result["value"])
        self.assertTrue(local_result["value"])

    def test_unknown_context_or_missing_decoder_holds(self):
        g,ab=make_before("unknown",9,1)
        self.assertEqual(self.lex.ask(SYMBOL,None,g,ab)["status"],
                         "HOLD_AMBIGUOUS_DECODER")
        self.assertEqual(self.lex.ask(SYMBOL,"OTHER",g,ab)["status"],
                         "HOLD_UNKNOWN_SYMBOL_OR_DECODER")
        self.assertEqual(self.lex.ask("OTHER",WHOLE,g,ab)["status"],
                         "HOLD_UNKNOWN_SYMBOL_OR_DECODER")

    def test_duplicate_symbol_decoder_refused(self):
        with self.assertRaises(ValueError):
            self.lex.admit_global(SYMBOL,WHOLE,self.cert,self.train,self.valid)

    def test_not_allowed_to_switch_record_types(self):
        with self.assertRaises(ValueError):
            Lexicon().admit_global(SYMBOL,LOCAL,self.cert,
                                  self.train,self.valid)
        with self.assertRaises(ValueError):
            Lexicon().admit_local(SYMBOL,WHOLE,self.localcert,
                                 self.localtrain,self.localvalid)

    def test_forged_source_hash_cannot_join_lexicon(self):
        fake=replace(self.cert,validation_digest="invented")
        with self.assertRaises(ValueError):
            Lexicon().admit_global(SYMBOL,WHOLE,fake,self.train,self.valid)

    def test_local_forged_source_hash_cannot_join_lexicon(self):
        fake=replace(self.localcert,validation_hash="invented")
        with self.assertRaises(ValueError):
            Lexicon().admit_local(SYMBOL,LOCAL,fake,
                                 self.localtrain,self.localvalid)

    def test_forged_lexical_pin_means_hold(self):
        index=list(self.lex.entries)
        meaning,record=index[0]
        index[0]=(replace(meaning,pin="spoofed"),record)
        changed=Lexicon(tuple(index))
        g,ab=make_before("tamper",9,1)
        self.assertEqual(changed.ask(SYMBOL,WHOLE,g,ab)["status"],
                         "HOLD_SOURCE_REVOKED")

    def test_mutating_status_never_grants_runtime_authority(self):
        index=list(self.lex.entries)
        meaning,record=index[0]
        index[0]=(replace(meaning,status="INSTALLED"),record)
        changed=Lexicon(tuple(index))
        g,ab=make_before("status",9,1)
        self.assertEqual(changed.ask(SYMBOL,WHOLE,g,ab)["status"],
                         "HOLD_UNAUTHORIZED_MEANING")

    def test_no_invalid_python_expression(self):
        bad=Expression("BOOL","EVAL",())
        good,ab=make_before("bad",9,1)
        with self.assertRaises(ValueError):
            interpret(bad,good,ab)
        with self.assertRaises(ValueError):
            interpret(Expression("VERTEX_SET","ANY",
                                  (Expression("VERTEX_SET","ALL"),)),
                      good,ab)

    def test_validator_refuses_wrong_splits(self):
        with self.assertRaises(ValueError):
            discover(self.valid)
        with self.assertRaises(ValueError):
            review(self.proposal,self.train,self.test)

    def test_validator_refuses_duplicate_training_evidence(self):
        with self.assertRaises(ValueError):
            discover(self.train+(self.train[0],))

    def test_validator_refuses_cross_split_receipt_reuse(self):
        forged=(replace(self.valid[0],evidence_id=self.train[0].evidence_id),) + self.valid[1:]
        with self.assertRaises(ValueError):
            review(self.proposal,self.train,forged)

    def test_validator_refuses_false_training_provenance(self):
        bad=replace(self.train[0],provenance="ACTUAL_GLYPH_PHYSICS")
        with self.assertRaises(ValueError):
            discover((bad,)+self.train[1:])

    def test_validator_refuses_adversarial_validation_label(self):
        fake=list(self.valid)
        first=fake[0]
        a,b=infer_delta(first)[0]
        # This source graph has no isolated vertices, but now claim the
        # opposite graph-edit effect at exactly the same source edge.
        counterpart=next(r for r in self.valid
                         if r.before.vertices-r.before.vertices == frozenset()
                         and len(r.before.vertices) == len(first.before.vertices)+1)
        misleading=owner_effect(first.before,(a,b),"fake")
        # True contradiction achieved by replacing the source edit with
        # an edge subdivision rather than the original brace.
        fresh=misleading.vertices-first.before.vertices
        after=Graph.of(misleading.vertices,misleading.edges-{edge(a,b)})
        fake[0]=replace(first,after=after)
        self.assertIsNone(review(self.proposal,self.train,tuple(fake)))

    def test_foreign_graphs_with_added_isolates(self):
        correct=total=0
        for _,source in hosts():
            for extra in (0,1,2,3):
                copy=source.copy()
                for i in range(extra):
                    copy.add_node(f"new_isolated__{i}")
                graph=topology(copy)
                ab=edge(*next(iter(copy.edges)))
                expected=nx.number_of_isolates(copy)>0
                result=self.lex.ask(SYMBOL,WHOLE,graph,ab)
                total+=1
                correct+=int(result["value"]==expected)
        self.assertEqual((correct,total),(48,48))

    def test_mixed_isolated_and_connected_nonzero_node_counts(self):
        graph,ab=make_before("vary",10,2)
        # changing the total graph size while retaining two isolates
        extra="extra_connected"
        touched=next(iter(graph.vertices-{
            v for v in graph.vertices if "_isolated_" in v
        }))
        after=Graph.of(graph.vertices|{extra},
                       graph.edges|{edge(touched,extra)})
        self.assertTrue(self.lex.ask(SYMBOL,WHOLE,graph,ab)["value"])
        self.assertTrue(self.lex.ask(SYMBOL,WHOLE,after,ab)["value"])

    def test_source_owner_never_becomes_the_learner(self):
        # This is explicitly a separate source-owner oracle; training was
        # constructed from structural deltas and not target-label text.
        for row in self.test:
            ab,effect=infer_delta(row)
            has_isolate=bool(row.before.vertices-used_vertices(row.before))
            self.assertEqual(has_isolate,bool(effect.remove_edges))

    def test_matched_sample_classical_synthesis_selects_same_grammar(self):
        control=learn_classically(self.train,self.valid)
        self.assertEqual(control["status"],"CLASSICAL_REVIEWED")
        self.assertEqual(control["program"],self.proposal.program.notation())
        self.assertEqual(control["examined"],self.proposal.examined)
        self.assertEqual(predict_classically(control,self.test)["correct"],16)

    def test_separately_interpreted_meanings_agree_on_foreign_worlds(self):
        from gardener import Graph
        for _,native in hosts():
            graph=topology(native)
            ab=edge(*next(iter(graph.edges)))
            ours=interpret(self.proposal.program,graph,ab)
            theirs=native_interpret(self.proposal.program,graph,ab)
            self.assertEqual(ours,theirs)

    def test_report_no_unearned_authority(self):
        results=report()
        self.assertEqual(results["heldout_world_meaning_correct"],16)
        self.assertEqual(results["heldout_world_meaning_total"],16)
        self.assertEqual(results["external_graph_correct"],48)
        self.assertEqual(results["external_graphs_and_isolate_interventions"],48)
        self.assertTrue(results["independent_classical_synthesizer"]["same_program"])
        self.assertTrue(results["independent_classical_synthesizer"]["same_candidates_examined"])
        self.assertEqual(results["external_actions"],0)
        self.assertFalse(results["production_installation"])
        self.assertFalse(results["quantum_experiment"])


def used_vertices(graph):
    return {v for a,b in graph.edges for v in (a,b)}


if __name__=="__main__":
    unittest.main()
