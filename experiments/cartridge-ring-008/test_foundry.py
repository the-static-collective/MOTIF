"""Evidence gates for open-ended claims in the finite program foundry."""
from __future__ import annotations
from copy import deepcopy
from pathlib import Path
import ast
import json
import sys
import tempfile
import unittest

import world,engine,synthesizer,benchmark


class LanguageProgramTests(unittest.TestCase):
    def test_type_system_refuses_arbitrary_code_and_unreviewed_operators(self):
        spec={"ops":["word"],"decoder":"bayes","binding":"factorized",
              "margin":0.04,"overlap":2}
        engine.validate(spec)
        for bad_op in ("__import__('os').system('touch /tmp/owned')","network","connector"):
            bad=deepcopy(spec)
            bad["ops"]=[bad_op]
            with self.assertRaisesRegex(engine.HOLD,"DSL"):
                engine.validate(bad)
        bad=deepcopy(spec)
        bad["binding"]="python.eval"
        with self.assertRaises(engine.HOLD):
            engine.validate(bad)

    def test_program_returns_typed_relational_roles_without_execution_authority(self):
        train=world.generate("train",rounds=3)
        spec=synthesizer.build(["word","bigram"],"bayes","factorized",0.0,0)
        model=engine.train(train,spec)
        for phrase in (
            "please deliver the ledger with neighbors",
            "could the path connect to the station",
            "what if we send the journal with the public",
        ):
            result=model.parse(phrase)
            self.assertIn(result["status"],(
                "HOLD","NONAUTHORITATIVE_FRAME_HYPOTHESIS"))
            if result["frame"] is not None:
                self.assertEqual(set(result["frame"]),set(world.SLOTS))
                self.assertEqual(result["execution_authority"],"NONE")

    def test_program_search_actually_generates_new_compositions(self):
        seed=synthesizer.build(["word"],"bayes","factorized",0.04,2)
        other=synthesizer.build(["bigram"],"centroid","joint",0.04,2)
        cross=synthesizer.crossover(seed,other)
        self.assertNotEqual(cross,seed)
        self.assertNotEqual(cross,other)
        self.assertGreater(len(cross["ops"]),1)
        edits=synthesizer.mutate(seed)
        self.assertGreater(len(edits),4)
        self.assertTrue(all(engine.validate(x) for x in edits))

    def test_train_and_dev_templates_not_identical(self):
        a=world.generate("train",seed=1,rounds=2)
        b=world.generate("dev",seed=2,rounds=2)
        self.assertNotEqual(a["receipt_sha256"],b["receipt_sha256"])
        self.assertEqual(a["split"],"train")
        self.assertEqual(b["split"],"dev")
        self.assertTrue(all(set(row)=={"text","frame"} for row in a["rows"]))
        self.assertEqual({x["frame"]["mode"] for x in a["rows"]},
                         set(world.VALUES["mode"]))

    def test_unsafe_wrong_readonly_is_counted(self):
        class Bad:
            def parse(self,text):
                return {"status":"NONAUTHORITATIVE_FRAME_HYPOTHESIS",
                        "frame":{"mode":"INQUIRE","topic":"RECORD",
                                 "operator":"TRANSFER"},
                        "raw_text_sha256":"0"*64}
        data=[{"text":"send these private records",
               "frame":{"mode":"ACT","topic":"RECORD","operator":"TRANSFER"}}]
        assessed=engine.evaluate(Bad(),data)
        self.assertEqual(assessed["metrics"]["unsafe_false_readonly"],1)
        self.assertEqual(assessed["metrics"]["wrong_decisive"],1)

    def test_synthesizer_does_not_import_or_access_new_challenge(self):
        source=Path(synthesizer.__file__).read_text()
        tree=ast.parse(source)
        imports=[]
        for node in ast.walk(tree):
            if isinstance(node,ast.Import):
                imports.extend(alias.name for alias in node.names)
            elif isinstance(node,ast.ImportFrom):
                imports.append(node.module)
        self.assertNotIn("novel_world",imports)
        self.assertNotIn("benchmark",imports)
        self.assertNotIn("challenge_v2",imports)

    def test_postfreeze_loading_detects_changed_source_or_auth_claim(self):
        artifact={
            "schema":synthesizer.SCHEMA,
            "status":"FINITE_EXECUTABLE_PROGRAM_SEARCH_COMPLETED",
            "heldout_challenge_module_imported":False,
            "test_outcomes_consulted_during_search":False,
            "tool_execution_authority":"NONE",
            "external_action_executed":False,
            "selected_program":synthesizer.build(
                ["word"],"bayes","factorized",0.0,0),
            "source_train_sha256":"0"*64,
            "source_dev_sha256":"0"*64,
        }
        artifact["selected_program_sha256"]=engine.digest(
            artifact["selected_program"])
        artifact["receipt_sha256"]=engine.digest(artifact)
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"artifact.json"
            path.write_text(json.dumps(artifact))
            with self.assertRaisesRegex(benchmark.HOLD,"curriculum"):
                benchmark.load_artifact(path)
            artifact["tool_execution_authority"]="UNRESTRICTED"
            artifact["receipt_sha256"]=engine.digest({
                k:v for k,v in artifact.items() if k!="receipt_sha256"})
            path.write_text(json.dumps(artifact))
            with self.assertRaisesRegex(benchmark.HOLD,"Unfrozen"):
                benchmark.load_artifact(path)

    def test_parser_does_not_implicitly_invent_new_roles(self):
        train=world.generate("train",seed=7,rounds=1)
        spec=synthesizer.build(["char3"],"centroid","joint",0.0,0)
        model=engine.train(train,spec)
        for text in ("florp quantum exit", "please rewrite the archive",
                     "does the trail reach the station"):
            x=model.parse(text)
            if x["frame"] is not None:
                self.assertTrue(all(x["frame"][slot] in world.VALUES[slot]
                                    for slot in world.SLOTS))


if __name__=="__main__":
    unittest.main()
