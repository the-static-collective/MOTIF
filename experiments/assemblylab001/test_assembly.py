"""Independent behavioral controls for actual-source MOTIF cartridge composition."""
from dataclasses import replace
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
from shutil import copy2
import json
import subprocess
import sys
import unittest

from assembly import (Goal, Stage, STAGES, REGISTRY, DEPENDENCIES,
                      source_pins, plan, compile_assembly, execute, create_child,
                      verify_child, fixture, demonstration, PORT_TYPES, CHILD_NAME)

ROOT=Path(__file__).resolve().parents[1]


class ActualCartridgeComposition(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.immediate=compile_assembly(ROOT,Goal('affordance','immediate'))
        cls.frontier=compile_assembly(ROOT,Goal('affordance','new_choices'))
        cls.witness=compile_assembly(ROOT,Goal('witness'))

    def test_native_interfaces_are_real_source_files(self):
        for path,digest in self.witness.pinned_files:
            data=(ROOT/path).read_bytes()
            self.assertEqual(sha256(data).hexdigest(),digest)
        self.assertEqual(len(self.witness.pinned_files),len(DEPENDENCIES))

    def test_synthetic_graph_plan_uses_three_real_cartridges(self):
        self.assertIn('MOTIF003_ANALYZE',self.immediate.stages)
        self.assertIn('MATHAL_NOMINATE',self.immediate.stages)
        self.assertIn('SELF_MIRROR_IMMEDIATE',self.immediate.stages)
        self.assertEqual(self.immediate.stages[-1],'ASSEMBLE_AFFORDANCE')
        self.assertEqual(self.immediate.cost,4)

    def test_replanning_changes_source_policy_for_different_goal(self):
        self.assertIn('SELF_MIRROR_FRONTIER',self.frontier.stages)
        self.assertNotIn('SELF_MIRROR_IMMEDIATE',self.frontier.stages)
        self.assertNotEqual(self.frontier.stages,self.immediate.stages)

    def test_actual_motif003_and_selfmirror_change_proposed_choice(self):
        faster=execute(self.immediate,ROOT)
        expanding=execute(self.frontier,ROOT)
        self.assertEqual(faster['status'],'EXECUTED_TYPED_COMPOSITION')
        self.assertEqual(expanding['status'],'EXECUTED_TYPED_COMPOSITION')
        self.assertIn('repair',faster['result']['proposed_action'])
        self.assertIn('teach',expanding['result']['proposed_action'])
        self.assertGreater(expanding['result']['new_options_by_move']['teach'],
                           expanding['result']['new_options_by_move']['repair'])

    def test_actual_mathal_restrains_admission_to_ideas(self):
        out=execute(self.frontier,ROOT)
        self.assertEqual(out['result']['fir_proposals'],2)
        self.assertEqual(out['result']['status'],'I_SIMULATED_ACTION_ONLY')
        self.assertFalse(out['result']['new_independent_evidence'])
        self.assertEqual(out['external_actions'],0)
        self.assertFalse(out['autonomous_source_changes'])

    def test_witness_path_uses_actual_question_and_receipt_functions(self):
        self.assertEqual(set(self.witness.stages),
                         {'WITNESS_FIR','WITNESS_FORWARD','WITNESS_ORIENT','ASSEMBLE_WITNESS'})
        out=execute(self.witness,ROOT)
        self.assertEqual(out['status'],'EXECUTED_TYPED_COMPOSITION')
        answer=out['result']
        self.assertEqual(answer['fir_evidence_role'],'F_LOCAL')
        self.assertEqual(answer['fir_model_role'],'I')
        self.assertEqual(answer['original_answer']['status'],'HOLD_GLOBAL_FLIP_SYMMETRY')
        self.assertEqual(answer['executed_operations'],
                         ('ANSWER_RELATIVE','TEST_SYMMETRY','DESIGN_PROBE'))
        self.assertFalse(answer['new_independent_evidence'])

    def test_crosscheck_actual_motif003_module_instead_of_static_stub(self):
        import importlib
        sys.path.insert(0,str(ROOT/'003'))
        a=importlib.import_module('affordance')
        import assembly
        world=fixture('affordance',ROOT)['scene']
        rows=a.analyze_first_moves(world,{},assembly._possibilities,assembly._utility,horizon=3)
        self.assertEqual(len(rows),execute(self.frontier,ROOT)['result']['candidate_actions'])
        self.assertEqual({r['operator'] for r in rows},{'repair','teach'})

    def test_crosscheck_actual_nextstep_rather_than_reimplemented_answer(self):
        import importlib
        sys.path.insert(0,str(ROOT/'nextstep001'))
        nextstep=importlib.import_module('nextstep')
        data=fixture('witness',ROOT)
        real=nextstep.advance(data['witness_state'],data['witness_goal'])
        out=execute(self.witness,ROOT)['result']
        self.assertEqual(out['executed_operations'],
                         tuple(s['action_executed'] for s in real['steps']))

    def test_all_plan_stages_are_named_read_only(self):
        self.assertEqual(len(REGISTRY),len(STAGES))
        for stage in STAGES:
            self.assertFalse(stage.external_effects)
            self.assertIn(stage.provides,PORT_TYPES)
            for port in stage.requires:
                self.assertIn(port,PORT_TYPES)
        for program in (self.immediate,self.frontier,self.witness):
            self.assertTrue(all(name in REGISTRY for name in program.stages))

    def test_insufficient_budget_has_no_assembly(self):
        self.assertIsNone(plan(Goal('affordance',budget=3)))
        self.assertIsNone(plan(Goal('witness',budget=3)))
        with self.assertRaisesRegex(ValueError,'HOLD_NO_TYPED'):
            compile_assembly(ROOT,Goal('witness',budget=0))

    def test_bounded_horizon_cannot_skip_dependencies(self):
        self.assertIsNone(plan(Goal('affordance',max_stages=3)))
        self.assertIsNone(plan(Goal('witness',max_stages=3)))

    def test_unknown_goal_and_bad_budget_are_rejected(self):
        for args in ({'domain':'external'}, {'domain':'witness','budget':-1},
                     {'domain':'witness','budget':True},
                     {'domain':'witness','max_stages':0},
                     {'domain':'witness','max_stages':True},
                     {'domain':'affordance','priority':'execute-world'}):
            with self.assertRaises(ValueError):Goal(**args)

    def test_source_hash_tamper_fails_closed_before_import(self):
        with TemporaryDirectory() as temp:
            root=Path(temp)
            for rel,_ in self.immediate.pinned_files:
                out=root/rel
                out.parent.mkdir(parents=True,exist_ok=True)
                copy2(ROOT/rel,out)
            (root/'003'/'affordance.py').write_text('raise RuntimeError("tampered")\n')
            self.assertEqual(execute(self.immediate,root)['status'],'HOLD_SOURCE_DRIFT')

    def test_transitive_dependency_tamper_also_fails_closed(self):
        with TemporaryDirectory() as temp:
            root=Path(temp)
            for rel,_ in self.immediate.pinned_files:
                out=root/rel;out.parent.mkdir(parents=True,exist_ok=True)
                copy2(ROOT/rel,out)
            with (root/'fir001'/'fir.py').open('a') as f:f.write('\n# changed\n')
            self.assertEqual(execute(self.immediate,root)['status'],'HOLD_SOURCE_DRIFT')

    def test_missing_file_or_symlink_refused_by_pin_inventory(self):
        with TemporaryDirectory() as temp:
            root=Path(temp)
            for rel,_ in self.immediate.pinned_files:
                out=root/rel;out.parent.mkdir(parents=True,exist_ok=True)
                copy2(ROOT/rel,out)
            item=root/'003'/'affordance.py'
            item.unlink()
            with self.assertRaises(ValueError):source_pins(root)
            item.symlink_to(ROOT/'003'/'affordance.py')
            with self.assertRaises(ValueError):source_pins(root)

    def test_changing_stage_chain_does_not_bypass_typed_plan(self):
        altered=replace(self.frontier,stages=self.frontier.stages[:-1])
        out=execute(altered,ROOT)
        self.assertEqual(out['status'],'HOLD_UNPLANNED_OR_MODIFIED_STAGE_CHAIN')

    def test_changing_goal_invalidates_original_stage_chain(self):
        altered=replace(self.frontier,goal=Goal('affordance','immediate'))
        self.assertEqual(execute(altered,ROOT)['status'],'HOLD_UNPLANNED_OR_MODIFIED_STAGE_CHAIN')

    def test_foreign_source_pins_are_rejected(self):
        wrong=replace(self.witness,pinned_files=(('a.py','fake'),))
        self.assertEqual(execute(wrong,ROOT)['status'],'HOLD_SOURCE_DRIFT')

    def test_foreign_input_port_is_held_without_execution(self):
        out=execute(self.immediate,ROOT,data={'shell':'rm -rf /'})
        self.assertEqual(out['status'],'HOLD_INPUT_SCHEMA')
        self.assertEqual(out['external_actions'],0)

    def test_wrong_input_type_is_held_without_execution(self):
        out=execute(self.immediate,ROOT,data={'scene':'user supplied code'})
        self.assertEqual(out['status'],'HOLD_INPUT_SCHEMA')
        out=execute(self.witness,ROOT,data={'witness_state':{},'witness_goal':{}})
        self.assertEqual(out['status'],'HOLD_INPUT_SCHEMA')

    def test_existing_world_is_not_mutated(self):
        x=fixture('affordance',ROOT)
        initial=x['scene']
        out=execute(self.immediate,ROOT,data=x)
        self.assertEqual(x['scene'],initial)
        self.assertTrue(out['result']['external_actions']==0)

    def test_generated_child_is_real_process_with_readable_receipts(self):
        with TemporaryDirectory() as temp:
            child,program=create_child(ROOT,Path(temp),Goal('witness'))
            self.assertEqual(child.name,CHILD_NAME)
            self.assertIn('from assembly import Assembly, Goal, execute',child.read_text())
            result=verify_child(child,ROOT)
            self.assertEqual(result['status'],'VERIFIED_EXECUTION')
            self.assertEqual(tuple(result['output']['assembly_stages']),program.stages)
            self.assertEqual(len(result['output']['receipts']),4)

    def test_generated_child_can_execute_distinct_modules_and_goals(self):
        for kind in ('affordance','witness'):
            with self.subTest(kind=kind),TemporaryDirectory() as temp:
                child,program=create_child(ROOT,Path(temp),Goal(kind))
                r=verify_child(child,ROOT)
                self.assertEqual(r['status'],'VERIFIED_EXECUTION')
                self.assertEqual(r['output']['result']['domain'],kind)

    def test_generated_child_refuses_same_source_file_path_overwrite(self):
        with TemporaryDirectory() as temp:
            child,program=create_child(ROOT,Path(temp),Goal('witness'))
            with self.assertRaises(FileExistsError):
                create_child(ROOT,Path(temp),Goal('witness'))
            self.assertTrue(child.is_file())

    def test_generated_child_resists_injected_plan(self):
        with TemporaryDirectory() as temp:
            child,program=create_child(ROOT,Path(temp),Goal('witness'))
            script=child.read_text()
            child.write_text(script.replace('"WITNESS_FIR"','"SYSTEM_EXEC"'))
            result=verify_child(child,ROOT)
            self.assertIn(result['status'],{'HOLD_CHILD_PROCESS_FAILURE','HOLD_CHILD_RESULT'})

    def test_child_has_no_external_action_interface(self):
        with TemporaryDirectory() as temp:
            child,program=create_child(ROOT,Path(temp),Goal('affordance'))
            text=child.read_text()
            self.assertNotIn('subprocess.run',text)
            self.assertNotIn('requests',text)
            self.assertNotIn('eval(',text)
            self.assertIn('assembly',text)

    def test_stage_contract_rejects_fabricated_truth_and_truncated_search(self):
        from assembly import _valid_output
        proposal=REGISTRY['SELF_MIRROR_FRONTIER']
        self.assertFalse(_valid_output(proposal,{'status':'F','admitted_fact':True}))
        graph=REGISTRY['MOTIF003_ANALYZE']
        self.assertFalse(_valid_output(graph,[{'operator':'repair','roles':('x',),
                         'future':frozenset(),'new_affordances':(), 'truncated':True}]))

    def test_stage_contract_refuses_unwarranted_evidence_and_external_effects(self):
        from assembly import _valid_output
        witness=REGISTRY['WITNESS_FIR']
        self.assertFalse(_valid_output(witness,{'ledger_count_role':'F',
                                               'hypothesis_role':'F'}))
        follow=REGISTRY['WITNESS_FORWARD']
        self.assertFalse(_valid_output(follow,{'real_world_actions':1,
                                               'same_evidence_before_after':True}))

    def test_question_after_question_requires_actual_executed_steps(self):
        answer=execute(self.witness,ROOT)['result']
        self.assertEqual(len(answer['executed_operations']),3)
        self.assertEqual(answer['status'],'EXECUTED_LOCAL_STEPS')
        self.assertTrue(answer['next_question'].startswith('How can'))
        self.assertFalse(answer['new_independent_evidence'])

    def test_replay_is_deterministic_in_three_modes(self):
        a=demonstration(ROOT)
        b=demonstration(ROOT)
        self.assertEqual(a,b)
        self.assertEqual(a['real_world_actions'],0)
        self.assertEqual({x['verified'] for x in a['compositions'].values()},
                         {'VERIFIED_EXECUTION'})

    def test_domain_fixed_baseline_fails_one_out_of_two_tasks(self):
        # Baseline is a fixed witness-only sequence; can't answer graph task.
        naive={'witness':{'WITNESS_FIR','WITNESS_FORWARD','WITNESS_ORIENT','ASSEMBLE_WITNESS'}}
        self.assertEqual(sum(domain in naive for domain in ('witness','affordance')),1)
        self.assertEqual(sum(execute(compile_assembly(ROOT,Goal(domain)),ROOT)['status']
                             =='EXECUTED_TYPED_COMPOSITION' for domain in ('witness','affordance')),2)
        # This only measures *coverage*, not innovation or better prediction.

    def test_source_file_inventory_does_not_prove_capability(self):
        self.assertEqual(self.witness.status,'I_TESTABLE_ASSEMBLY')
        self.assertEqual(execute(self.witness,ROOT)['model_claim'],'I_LOCAL_SYNTHETIC_ONLY')
        self.assertFalse(execute(self.witness,ROOT)['autonomous_source_changes'])


if __name__=='__main__':unittest.main()
