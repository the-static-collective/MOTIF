"""Adversarial finite tests for source-oriented, bounded MOTIF construction."""
from dataclasses import replace
from pathlib import Path
import ast
import json
import tempfile
import unittest

from selfbuild import (ACTIONS, INTERFACES, CHILD_BODY, CHILD_TEST_BODY,
    CHILD_FILE, Goal, Orientation, advance, demonstration, next_questions,
    scan, stage_seed, test_seed)


def fixture(root: Path, omit: tuple[str,...] = ()) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    for component, rel, symbols in INTERFACES:
        if rel in omit:
            continue
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        code = '\n'.join(f'def {name}():\n    pass\n' for name in symbols)
        path.write_text(code)
    return root


class SelfBuildTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.source = fixture(self.base/'repo')
        self.stage = self.base/'stage'

    def test_inventory_reports_existing_symbols_without_promotion(self):
        o = scan(self.source)
        self.assertEqual(len(o.knows_locally), 10)
        self.assertEqual(o.missing_interfaces, ())
        self.assertTrue(all(f.status == 'PRESENT_UNVERIFIED' for f in o.observed))
        self.assertIn('ONLY', o.epistemic_status)

    def test_missing_upstream_symbols_are_visible(self):
        code = self.source / 'nextstep001/nextstep.py'
        code.write_text('def orient():\n    return None\n')
        o=scan(self.source)
        self.assertIn('NEXT-STEP-001.advance',o.missing_interfaces)
        self.assertNotIn('NEXT-STEP-001.orient',o.missing_interfaces)
        self.assertTrue(any(f.status=='HOLD_INTERFACE_GAP' for f in o.observed))

    def test_missing_file_is_not_fabricated(self):
        (self.source/'003/affordance.py').unlink()
        o=scan(self.source)
        self.assertEqual(len(o.missing_interfaces),2)
        self.assertTrue(any(f.status=='HOLD_MISSING_OR_SYMLINK' for f in o.observed))

    def test_syntax_error_is_not_mistaken_for_working_interface(self):
        (self.source/'fir001/fir.py').write_text('def FIRWorld(??):\n    pass')
        self.assertIn('FIR-001.FIRWorld',scan(self.source).missing_interfaces)

    def test_imported_symbol_only_is_not_claimed_as_own(self):
        (self.source/'fir001/fir.py').write_text('from elsewhere import FIRWorld\n')
        self.assertIn('FIR-001.FIRWorld',scan(self.source).missing_interfaces)

    def test_source_digest_changes_with_content(self):
        before = scan(self.source).source_digest
        (self.source/'003/affordance.py').write_text('def witness_gap(): pass\n')
        self.assertNotEqual(before,scan(self.source).source_digest)

    def test_scan_read_only_and_reproducible(self):
        before = sorted((str(p.relative_to(self.source)),p.read_bytes())
                        for p in self.source.rglob('*.py'))
        self.assertEqual(scan(self.source),scan(self.source))
        after = sorted((str(p.relative_to(self.source)),p.read_bytes())
                       for p in self.source.rglob('*.py'))
        self.assertEqual(before,after)

    def test_symlink_is_not_trusted(self):
        path=self.source/'fir001/fir.py'
        external=self.base/'untrusted.py'
        external.write_text('class FIRWorld: pass\nclass Claim: pass')
        path.unlink()
        path.symlink_to(external)
        self.assertIn('FIR-001.FIRWorld',scan(self.source).missing_interfaces)

    def test_invalid_goal_limits_rejected(self):
        for kwargs in ({'budget':-1},{'budget':True},{'max_steps':0},
                       {'max_steps':5},{'question':''}):
            with self.assertRaises(ValueError):Goal(**kwargs)

    def test_question_graph_is_dependency_ordered(self):
        o=scan(self.source)
        c=next_questions(o)
        self.assertEqual(tuple(x.action for x in c),
                         ('INSPECT_SOURCE','GENERATE_SEED','TEST_SEED','REPORT_LIMITS'))
        self.assertEqual(tuple(x.action for x in next_questions(o,frozenset({'INSPECT_SOURCE'}))),
                         ('GENERATE_SEED','TEST_SEED','REPORT_LIMITS'))
        with self.assertRaises(ValueError):next_questions(o,frozenset({'BAD_EXTERNAL_ACTION'}))

    def test_static_template_and_child_contract(self):
        o=scan(self.source)
        m=stage_seed(o,self.stage)
        self.assertEqual(m['status'],'I_TEMPLATE_INSTANCE_NOT_TESTED')
        self.assertEqual(m['generated'],(CHILD_FILE,'test_motif_seed.py'))
        result=test_seed(o,self.stage,m)
        self.assertEqual(result['status'],'F_LOCAL_TEMPLATE_TESTED',result)
        self.assertTrue(result['tests_passed'])
        self.assertEqual(result['test_cases'],4)
        self.assertEqual(result['child_output']['result']['count'],len(INTERFACES))
        self.assertEqual(result['child_output']['external_actions'],0)

    def test_stage_refuses_overwrite(self):
        o=scan(self.source)
        stage_seed(o,self.stage)
        with self.assertRaises(ValueError):stage_seed(o,self.stage)

    def test_child_source_tamper_is_held_without_execution(self):
        o=scan(self.source)
        m=stage_seed(o,self.stage)
        child=self.stage/CHILD_FILE
        child.write_text(child.read_text()+"\nraise RuntimeError('tampered')\n")
        result=test_seed(o,self.stage,m)
        self.assertEqual(result['status'],'HOLD_TAMPERED_OR_UNTRUSTED_SOURCE')
        self.assertIsNone(result['child_output'])

    def test_child_tests_tamper_is_held(self):
        o=scan(self.source);m=stage_seed(o,self.stage)
        (self.stage/'test_motif_seed.py').write_text('pass')
        self.assertEqual(test_seed(o,self.stage,m)['status'],
                         'HOLD_TAMPERED_OR_UNTRUSTED_SOURCE')

    def test_stale_parent_invalidates_child(self):
        o=scan(self.source);m=stage_seed(o,self.stage)
        (self.source/'003/affordance.py').write_text('def analyze_first_moves(): pass')
        self.assertEqual(test_seed(scan(self.source),self.stage,m)['status'],
                         'HOLD_TAMPERED_OR_UNTRUSTED_SOURCE')

    def test_missing_build_manifest_refuses(self):
        o=scan(self.source)
        m=stage_seed(o,self.stage)
        m['source_sha256']='bad'
        self.assertEqual(test_seed(o,self.stage,m)['status'],
                         'HOLD_TAMPERED_OR_UNTRUSTED_SOURCE')

    def test_no_budget_no_steps(self):
        r=advance(self.source,self.stage,Goal(budget=0))
        self.assertEqual(r['steps'],[])
        self.assertEqual(r['status'],'HOLD_NO_VERIFIED_CHILD')
        self.assertFalse(self.stage.exists())

    def test_one_step_only_inventory(self):
        r=advance(self.source,self.stage,Goal(max_steps=1))
        self.assertEqual([s['action'] for s in r['steps']],['INSPECT_SOURCE'])
        self.assertFalse(self.stage.exists())

    def test_budget_two_generates_but_cannot_claim_verified(self):
        r=advance(self.source,self.stage,Goal(budget=2))
        self.assertEqual([s['action'] for s in r['steps']],['INSPECT_SOURCE','GENERATE_SEED'])
        self.assertEqual(r['status'],'HOLD_NO_VERIFIED_CHILD')
        self.assertTrue((self.stage/CHILD_FILE).is_file())

    def test_full_advance_really_executes_child(self):
        r=advance(self.source,self.stage)
        self.assertEqual(r['status'],'F_LOCAL_CHILD_VERIFIED')
        self.assertEqual(len(r['steps']),4)
        self.assertEqual(r['steps'][2]['result']['status'],'F_LOCAL_TEMPLATE_TESTED')
        self.assertEqual(r['steps'][3]['result']['next_question'],
                         'Can real cartridge wiring and independent integration checks replace the template?')
        self.assertEqual(r['budget_spent'],4)
        self.assertFalse(r['general_self_replication'])
        self.assertEqual(r['publication'],'NONE')

    def test_missing_interface_kept_visible_even_if_seed_passes(self):
        (self.source/'nextstep001/nextstep.py').unlink()
        r=advance(self.source,self.stage)
        self.assertIn('NEXT-STEP-001.advance',r['orientation']['missing_interfaces'])
        self.assertEqual(r['status'],'F_LOCAL_CHILD_VERIFIED')
        self.assertEqual(r['steps'][1]['result']['status'],'I_TEMPLATE_INSTANCE_NOT_TESTED')

    def test_generated_source_imports_are_only_stdlib(self):
        o=scan(self.source);stage_seed(o,self.stage)
        tree=ast.parse((self.stage/CHILD_FILE).read_text())
        imports={alias.name.split('.')[0] for node in ast.walk(tree)
                 if isinstance(node,(ast.Import,ast.ImportFrom))
                 for alias in (node.names if isinstance(node,ast.Import) else [type('X',(),{'name':node.module})()])}
        self.assertTrue(imports <= {'json','sys','__future__'})

    def test_receipt_never_claims_external_action(self):
        r=advance(self.source,self.stage)
        self.assertTrue(all(x['receipt']['external_actions']==0 for x in r['steps']))
        self.assertFalse(r['child_can_act_externally'])
        self.assertFalse(r['source_code_autonomously_changed'])

    def test_demo_does_not_leave_artifacts_in_original_repo(self):
        before=scan(self.source)
        r=demonstration(self.source)
        self.assertEqual(r['status'],'F_LOCAL_CHILD_VERIFIED')
        self.assertEqual(before,scan(self.source))
        self.assertEqual(len(r['questions_asked']),4)

    def test_integration_full_repo_if_available(self):
        full=Path(__file__).resolve().parents[1]
        if not (full/'003'/'affordance.py').exists():
            self.skipTest('full MOTIF repo only present after GitHub checkout')
        orientation=scan(full)
        self.assertFalse(orientation.missing_interfaces,orientation.missing_interfaces)
        with tempfile.TemporaryDirectory() as t:
            r=advance(full,Path(t)/'child')
        self.assertEqual(r['status'],'F_LOCAL_CHILD_VERIFIED')


if __name__ == '__main__':
    unittest.main()
