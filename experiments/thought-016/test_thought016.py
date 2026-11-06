"""Adversarial tests for typed self-developer, not claims of novel intelligence."""
from __future__ import annotations
import ast
import copy
import hashlib
import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from grammar import (baseline_program,complete_program,compile_program,validate_program,
                     GrammarError,expr,ref,digest)
from fixtures import DEV,SAFETY,AUDIT,STRESS
from oracle import independent_optimum,validate_answer,OracleError
from lab import (TinyDesignModel,apply_fragments,proposed_probe,evaluate,run_lab,
                 LabError,FRAGMENTS)
from benchmark import main

class InventorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report,cls.before,cls.after,cls.patch=run_lab()

    def test_trained_model_really_operates(self):
        model=TinyDesignModel()
        self.assertEqual(model.predict('a gate requires a key held in inventory'),'GATE')
        self.assertEqual(model.predict('arrival collects token into inventory'),'PICKUP')
        self.assertEqual(model.predict('loop to origin after pickup is necessary'),'REVISIT')
        initial=evaluate(baseline_program(),DEV)
        order=model.rank_fragments([c for c in initial['cases'] if not c['passed']],[])
        self.assertEqual(set(order),set(FRAGMENTS))
        self.assertEqual(model.calls[0]['seen_data'],'DEV_ONLY')

    def test_compiled_dsl_is_a_real_executable_without_model_code(self):
        code=compile_program(complete_program())
        self.assertIsInstance(ast.parse(code),ast.Module)
        self.assertIn('subset',code)
        self.assertIn('union',code)
        self.assertNotIn('subprocess',code)
        self.assertNotIn('urllib',code)
        self.assertNotIn('eval(',code)
        self.assertNotIn('exec(',code)
        self.assertEqual(evaluate(complete_program(),DEV)['correct'],len(DEV))

    def test_fragments_compose_a_new_state_and_guard(self):
        program=apply_fragments(baseline_program(),FRAGMENTS)
        self.assertEqual(program,complete_program())
        self.assertIn('held_keys',program['identity'])
        self.assertTrue(program['revisit'])
        self.assertEqual(program['guards'][-1]['op'],'subset')
        self.assertEqual(program['effects']['held_keys']['op'],'union')
        self.assertEqual(evaluate(program,SAFETY)['correct'],len(SAFETY))

    def test_shortest_valid_route_may_need_revisiting_a_node(self):
        p=DEV[1]['problem']
        opt=independent_optimum(p)
        self.assertEqual(opt['path'],[0,1,0,3])
        self.assertEqual(opt['cost'],3)
        self.assertFalse(validate_answer(p,{'path':[0,3],'cost':1,'risk':0}))
        good=evaluate(complete_program(),[DEV[1]])['cases'][0]['actual']
        self.assertEqual(good['path'],opt['path'])

    def test_old_keyless_candidate_is_insufficient(self):
        old=evaluate(baseline_program(),DEV)
        new=evaluate(complete_program(),DEV)
        self.assertLess(old['correct'],new['correct'])
        self.assertEqual(new['correct'],len(DEV))
        self.assertFalse(old['cases'][1]['passed'])

    def test_oracle_checks_real_route_not_claimed_cost(self):
        p=DEV[0]['problem']
        bad={'path':[0,3],'cost':1,'risk':0}
        self.assertFalse(validate_answer(p,bad))
        good=evaluate(complete_program(),[DEV[0]])['cases'][0]['actual']
        self.assertTrue(validate_answer(p,good))
        with self.assertRaises(OracleError):independent_optimum({'n':100})

    def test_refuse_arbitrary_code_or_new_grammar_keys(self):
        p=baseline_program()
        attempts=[
            dict(p, python="__import__('os').system('rm -rf /')"),
            dict(p, guards=[{'op':'exec','args':[ref('edge.v'),ref('edge.v')]}]),
            dict(p, effects={**p['effects'],'held_keys':{'ref':'os.system'}}),
            dict(p, identity=['position','__class__']),
            dict(p, frontier='shell'),
            dict(p, revisit='yes'),
        ]
        for x in attempts:
            with self.subTest(x=x):
                with self.assertRaises(GrammarError):compile_program(x)
        with self.assertRaises(GrammarError):apply_fragments(p,['RUN_SHELL'])
        with self.assertRaises(GrammarError):apply_fragments(p,['PICKUP','PICKUP'])

    def test_model_proposed_test_is_independently_graded(self):
        model=TinyDesignModel()
        probe=model.propose_discriminator()
        p=proposed_probe(probe)
        self.assertEqual(p['problem']['pickups']['1'],[])
        self.assertIsNone(independent_optimum(p['problem']))
        self.assertTrue(validate_answer(p['problem'],None))
        self.assertEqual(self.report['model_proposed_test']['audit_membership'],False)
        self.assertEqual(self.report['model_test_result']['passed'],1)
        bad=dict(probe,kind='EXECUTE_PYTHON')
        with self.assertRaises(LabError):proposed_probe(bad)
        bad=dict(probe,case_index=9999)
        with self.assertRaises(LabError):proposed_probe(bad)

    def test_dev_then_frozen_audit_and_stress(self):
        r=self.report
        self.assertEqual(r['status'],'PATCH_FOR_HUMAN_REVIEW_NOT_INSTALLED')
        self.assertEqual(r['development'],{'before':3,'after':9,'total':9})
        self.assertEqual(r['audit'],{'before':62,'after':72,'total':72})
        self.assertEqual(r['stress'],{'after':54,'total':54})
        self.assertEqual(r['safety'],{'before':3,'after':4,'total':4})
        self.assertEqual(r['installed_fragments'],list(FRAGMENTS))
        self.assertTrue(all(x['decision']=='SCRATCH_ONLY_NO_RUNTIME_INSTALL' for x in r['staged_compositions']))
        self.assertEqual(r['counterexample'],None)

    def test_self_developer_has_no_hidden_audit_in_proposer_calls(self):
        model=TinyDesignModel()
        r,_,_,_=run_lab(model=model)
        self.assertEqual(r['status'],'PATCH_FOR_HUMAN_REVIEW_NOT_INSTALLED')
        self.assertNotIn('AUDIT',json.dumps(model.calls))
        self.assertNotIn('unseen synthetic gated graph',json.dumps(model.calls))
        self.assertTrue(all(x['seen_data']=='DEV_ONLY' for x in model.calls))
        self.assertFalse(r['heldout_exposed_to_developer'])

    def test_output_is_patch_for_review_not_runtime_install(self):
        self.assertIn('--- experiments/thought-016/reference_solver.py',self.patch)
        self.assertIn('+++ experiments/thought-016/candidate_solver.py',self.patch)
        self.assertIn('held_keys',self.patch)
        self.assertNotEqual(self.before,self.after)
        self.assertEqual(hashlib.sha256(self.after.encode()).hexdigest(),self.report['candidate_source_sha256'])
        self.assertFalse(self.report['written_to_project_implementation'])
        self.assertFalse(self.report['model_authored_arbitrary_python'])
        self.assertEqual(self.report['pen_state'],'UNCHANGED')
        self.assertEqual(self.report['external_authority'],'NONE')

    def test_bad_model_suggestion_has_no_side_effects(self):
        class Evil:
            model_kind='ADVERSARIAL_PROPOSER'
            def propose_discriminator(self):
                return {'schema':'motif.thought016.probe.v1','kind':'EXECUTE_PYTHON',
                        'case_index':0,'node':1,'rationale':'bad request'}
        with self.assertRaises(LabError):run_lab(model=Evil())
        self.assertEqual(evaluate(complete_program(),DEV)['correct'],9)

    def test_inconsistent_heldout_specimen_fails_closed(self):
        bad=copy.deepcopy(AUDIT[:4])
        bad[0]['problem']['edges'][0]['need']=['__import__']
        with self.assertRaises(OracleError):run_lab(rounds=1,audit=bad,stress=STRESS[:4])

    def test_strict_replay_receipt_and_no_install(self):
        r=self.report
        self.assertEqual(digest({k:v for k,v in r.items() if k!='receipt_digest'}),r['receipt_digest'])
        repeat,before,after,patch=run_lab()
        self.assertEqual(repeat,r)
        self.assertEqual((before,after,patch),(self.before,self.after,self.patch))
        self.assertEqual(r['external_authority'],'NONE')

    def test_budget_limits(self):
        with self.assertRaises(LabError):run_lab(rounds=300)
        with self.assertRaises(LabError):evaluate(complete_program(),DEV*30)
        with self.assertRaises(GrammarError):validate_program(dict(complete_program(),guards=[{'op':'add','args':[{'ref':'edge.v'},{'ref':'MALICIOUS'}]}]))

    def test_output_artifacts_are_review_only_and_generated_locally(self):
        with TemporaryDirectory() as d:
            r=main(d)
            self.assertEqual(r['status'],'PATCH_FOR_HUMAN_REVIEW_NOT_INSTALLED')
            names={x.name for x in Path(d).iterdir()}
            self.assertEqual(names,{'reference_solver.py','candidate_solver.py','candidate.diff','experiment-results.json'})
            report=json.loads((Path(d)/'experiment-results.json').read_text())
            self.assertEqual(report['receipt_digest'],self.report['receipt_digest'])

if __name__=='__main__':unittest.main()
