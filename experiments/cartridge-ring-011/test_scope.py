"""RING-011 source-provenance, nested-voice, graph safety and leakage tests."""
from __future__ import annotations
import ast
from copy import deepcopy
from pathlib import Path
import unittest

import corpus,binder,search


class ScopeGrammarTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source=corpus.generate("train",seed=2026111101,rounds=5)
        cls.model=binder.derive(cls.source,min_support=2,n=2,gap=18,
                                purity=1.0,binder="SCOPED",min_margin=1)

    def test_three_way_contrasts_have_stable_event_and_carrier(self):
        corpus.validate(self.source,split="train")
        self.assertEqual(len(self.source["contrasts"]),30)
        self.assertEqual(len(corpus.flatten(self.source)),90)
        for row in self.source["contrasts"]:
            vals=list(row.values())
            self.assertTrue(all(x["carrier"]==vals[0]["carrier"] for x in vals))
            self.assertTrue(all(x["observed_event"]==vals[0]["observed_event"]
                                for x in vals))

    def test_book_carriers_are_not_convertible_into_factual_proof(self):
        context={"speaker":"mina","agent":"noa","verb":"carry","patient":"map"}
        for carrier in corpus.CARRIERS:
            graph=corpus.frame("DIRECTIVE","ROOT","POS",carrier,context)
            m=corpus.graph_map(graph)
            self.assertEqual(m[("DOCUMENT","EVIDENCE_STATUS")],
                             corpus.EPISTEMIC[carrier])
            self.assertNotIn("AUTHENTICATED",m[("DOCUMENT","EVIDENCE_STATUS")])
            self.assertNotIn("CORROBORATED",m[("DOCUMENT","EVIDENCE_STATUS")])

    def test_nested_quote_transforms_authority_separately_from_outer_force(self):
        ctx={"speaker":"mina","agent":"noa","verb":"carry","patient":"map"}
        outer=corpus.graph_map(corpus.frame("DIRECTIVE","ROOT","POS","SONG",ctx))
        direct_to_quote=corpus.graph_map(
            corpus.frame("DIRECTIVE","QUOTED","POS","SONG",ctx))
        self.assertTrue(outer[("EVENT","REQUESTED_BY_ROOT")])
        self.assertFalse(direct_to_quote[("EVENT","REQUESTED_BY_ROOT")])
        self.assertEqual(outer[("ROOT","FORCE")],
                         direct_to_quote[("ROOT","FORCE")])
        self.assertEqual(direct_to_quote[("EVENT","VOICE_OWNER")],"noa")

    def test_bracket_binder_reconstructs_source_containment_structure(self):
        ctx={"speaker":"mina","agent":"noa","verb":"carry","patient":"map"}
        out=binder.abstract(
            "mina quotes ([noa saying please carry map])",ctx)
        self.assertEqual(out["event_depth"],2)
        self.assertEqual(out["segments"][out["event_index"]],"(/[")

    def test_rejects_unbalanced_brackets_before_language_hypothesis(self):
        ctx={"speaker":"mina","agent":"noa","verb":"carry","patient":"map"}
        for text in (
            "mina quotes ([noa saying please carry map]",
            "mina quotes ]) noa saying please carry map",
            "mina asks noa to carry map (",
        ):
            result=binder.predict(self.model,text,ctx,"SONG")
            self.assertEqual(result["status"],"HOLD")
            self.assertIsNone(result["graph"])

    def test_pseudonymous_unfamiliar_event_can_be_source_abstracted(self):
        ctx={"speaker":"zeva","agent":"tyn","verb":"unfurl","patient":"flag"}
        x=binder.abstract("zeva quotes [tyn saying please unfurl flag]",ctx)
        self.assertEqual(x["tokens"],[
            "<speaker>","quotes","[","<agent>","saying","please",
            "<verb>","<patient>","]"])

    def test_unknown_event_is_not_hallucinated_from_cryptic_phrase(self):
        ctx={"speaker":"mina","agent":"noa","verb":"carry","patient":"map"}
        for text in (
            "the telescope is a folded promise inside another promise",
            "the cup forgot which voice requested it (unless nobody did)",
            "never a report just a remembered echo",
        ):
            response=binder.predict(self.model,text,ctx,"SONG")
            self.assertEqual(response["status"],"HOLD")
            self.assertIsNone(response["graph"])

    def test_derived_operators_are_source_instances_not_new_computational_opcodes(self):
        p=self.model
        self.assertGreater(p["source_induced_edge_rewrites"],3)
        self.assertGreater(p["source_induced_relation_count"],3)
        self.assertEqual(p["authority"],"NONE")
        self.assertFalse(p["new_base_computational_primitives_invented"])
        self.assertTrue(p["carrier_proof_promotion_forbidden"])
        self.assertTrue(all(x["source"]==
            "MEANING_DIFFERENCE_OF_SAME_EVENT_CONTRASTS"
            for x in p["derived_contextual_binding_rules"]))

    def test_forged_rehashed_shell_operator_cannot_execute(self):
        p=deepcopy(self.model)
        p["derived_contextual_binding_rules"][0]["opcode"]="EVAL_PYTHON"
        p["receipt_sha256"]=corpus.digest({
            k:v for k,v in p.items() if k!="receipt_sha256"})
        with self.assertRaisesRegex(binder.HOLD,"Invalid executable"):
            binder.validate(p)

    def test_forged_default_directive_not_allowed(self):
        p=deepcopy(self.model)
        p["defaults_only_for_polarity"]["ROOT_FORCE"]="DIRECTIVE"
        p["receipt_sha256"]=corpus.digest({
            k:v for k,v in p.items() if k!="receipt_sha256"})
        with self.assertRaisesRegex(binder.HOLD,"Unreviewed default"):
            binder.validate(p)

    def test_changed_source_carrier_even_with_recomputed_checksum_refused(self):
        corrupted=deepcopy(self.source)
        corrupted["contrasts"][0]["b"]["carrier"]="RECORD"
        corrupted["receipt_sha256"]=corpus.digest({
            k:v for k,v in corrupted.items() if k!="receipt_sha256"})
        with self.assertRaisesRegex(ValueError,"Unbound source"):
            corpus.validate(corrupted,split="train")

    def test_no_heldout_module_import_in_search_or_inducer(self):
        modules=[]
        for file in ("search.py","binder.py","corpus.py"):
            source=(Path(__file__).resolve().parent/file).read_text()
            for node in ast.walk(ast.parse(source)):
                if isinstance(node,ast.Import):
                    modules.extend(x.name for x in node.names)
                if isinstance(node,ast.ImportFrom):
                    modules.append(node.module)
        self.assertNotIn("novel",modules)
        self.assertNotIn("benchmark",modules)

    def test_non_authority_even_for_correctly_inferred_root_directive(self):
        ctx={"speaker":"mina","agent":"noa","verb":"carry","patient":"map"}
        x=binder.predict(self.model,"mina asks noa to carry map",ctx,"SONG")
        self.assertIn(x["status"],(
            "HOLD","NONAUTHORITATIVE_NESTED_GRAPH_HYPOTHESIS"))
        if x["graph"] is not None:
            self.assertEqual(x["external_effect_permission"],"NONE")
            self.assertEqual(corpus.graph_map(x["graph"])[
                ("DOCUMENT","CARRIER")],"SONG")


if __name__=="__main__":
    unittest.main()
