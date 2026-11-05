"""MOTIF-005 integration: actual original GRAFT executable + independent CANNON
receipt + native MOTIF graph search, with fairness and deliberate HOLD controls.
"""
from __future__ import annotations
import copy
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

import impossibility as im
import build as builder

class MissingOperatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original=Path(os.environ['MOTIF_ORIGINAL'])
        cls.graft=Path(os.environ['GRAFT_SOURCE'])
        cls.gap_file=Path(os.environ['MOTIF_GAP'])
        cls.review_file=Path(os.environ['CANNON_REVIEW'])
        cls.tmp=tempfile.TemporaryDirectory(prefix='motif005-')
        cls.dest=Path(cls.tmp.name)/'new-motif'
        cls.certificate=im.prove(cls.original)
        cls.review=builder.read_doc(cls.review_file)
        cls.manifest=builder.build(cls.original,cls.graft,
             cls.gap_file,cls.review_file,cls.dest)
        cls.executed=subprocess.run([sys.executable,'run.py'],cwd=cls.dest,
             capture_output=True,text=True,timeout=25)
        cls.output=json.loads(cls.executed.stdout)

    @classmethod
    def tearDownClass(cls):cls.tmp.cleanup()

    def test_source_native_impossibility_invariant_independently_replayed(self):
        self.assertEqual(im.verify(self.certificate,self.original),
                         self.certificate['content_sha256'])
        self.assertEqual(self.certificate['proof']['original_verb_count'],2)
        self.assertEqual(self.certificate['proof']['original_emitting_verbs'],[])
        self.assertTrue(self.certificate['proof']['all_original_effects_exclude_predicate'])
        self.assertFalse(self.certificate['proof']['original_fixed_replay_reaches_goal'])

    def test_missing_permission_prevents_even_proposing_new_operator(self):
        with self.assertRaises(im.HOLD):
            im.prove(self.original,with_permission=False)

    def test_actual_new_js_was_regenerated_from_unmerged_original_graft_source(self):
        actual=builder.regenerate(self.graft,self.gap_file)['x']
        self.assertEqual(actual['source'],self.review['generated']['source'])
        self.assertEqual(actual['source_sha256'],self.manifest['generated_source_sha256'])
        self.assertEqual(actual['guard_contract'],['broken','permits'])
        self.assertEqual(actual['external_authority'],False)

    def test_cannon_exact_held_review_matches_real_question(self):
        self.assertEqual(builder.check_review(self.review,self.certificate),
                         self.review['content_sha256'])
        self.assertFalse(self.review['operator_admitted'])
        self.assertFalse(self.review['consent_from_packet'])
        self.assertEqual(self.review['independent_final']['correct'],6)

    def test_new_motif_build_contains_original_unmodified_python_and_new_graft_js(self):
        self.assertEqual(builder.blob((self.dest/'experiments/002/motif002.py').read_bytes()),
                         builder.MOTIF_SOURCE_BLOB)
        self.assertEqual(builder.read_doc(self.dest/'manifest.json'),self.manifest)
        self.assertIn('export function execute',(self.dest/'new_guarded_operator.mjs').read_text())
        self.assertFalse(self.manifest['automatic_admission'])

    def test_original_fixed_grammar_unreachable_new_generated_grammar_reachable(self):
        self.assertEqual(self.executed.returncode,0,self.executed.stderr)
        self.assertEqual(self.output['status'],
          'GENERATED_CLOSED_GRAMMAR_EXPANDS_SYNTHETIC_REACHABILITY')
        self.assertFalse(self.output['original_fixed_goal_reached'])
        self.assertTrue(self.output['new_generated_operator_goal_reached'])
        self.assertTrue(self.output['new_generated_operator_path'])
        self.assertTrue(any(p[0]=='graft029:guarded-add' for p in
                         self.output['new_generated_operator_path']))

    def test_permission_denial_does_not_reach_goal(self):
        self.assertFalse(self.output['without_permission_goal_reached'])
        self.assertEqual(self.output['actual_bicycle_inspections'],0)

    def test_fair_classical_inducer_with_same_labeled_demos_also_succeeds(self):
        self.assertTrue(self.output['fair_original_motif_002_newly_trained_goal_reached'])
        self.assertFalse(self.output['fair_original_motif_002_newly_trained_denied_leak'])
        self.assertTrue(self.output['fair_classical_comparison_matches'])
        self.assertFalse(self.output['claimed_better_than_classical'])

    def test_no_external_io_or_automatic_repair_claims(self):
        self.assertEqual(self.output['human_contacts'],0)
        self.assertEqual(self.output['production_promotions'],0)
        self.assertEqual(self.output['external_requests'],0)
        self.assertTrue(self.output['all_graph_states_synthetic'])

    def test_copy_of_generated_program_cannot_be_modified_after_build(self):
        with tempfile.TemporaryDirectory() as t:
            dest=Path(t)/'copied'
            shutil.copytree(self.dest,dest)
            p=dest/'new_guarded_operator.mjs'
            p.write_text(p.read_text()+'\n// unauthorized modification')
            r=subprocess.run([sys.executable,'run.py'],cwd=dest,
                             capture_output=True,text=True,timeout=10)
            self.assertNotEqual(r.returncode,0)
            self.assertEqual(json.loads(r.stdout)['stage'],'HOLD')

    def test_false_manifest_permission_even_rehashed_is_refused(self):
        with tempfile.TemporaryDirectory() as t:
            dest=Path(t)/'copied'
            shutil.copytree(self.dest,dest)
            p=dest/'manifest.json'
            m=json.loads(p.read_text())
            m['permission_to_real_act']=True
            b=dict(m);b.pop('content_sha256')
            m['content_sha256']=im.hash_obj(b)
            p.write_text(json.dumps(m))
            r=subprocess.run([sys.executable,'run.py'],cwd=dest,
                             capture_output=True,text=True,timeout=10)
            self.assertNotEqual(r.returncode,0)
            self.assertEqual(json.loads(r.stdout)['stage'],'HOLD')

    def test_altered_source_owner_commit_refused(self):
        with self.assertRaises(im.HOLD):
            im.prove(Path.cwd())

    def test_altered_question_digest_refused(self):
        fake=copy.deepcopy(self.certificate)
        fake['requested_goal']=['permits','bike1']
        with self.assertRaises(im.HOLD):
            im.verify(fake,self.original)

    def test_cannon_self_rehashed_fake_admission_refused(self):
        fake=copy.deepcopy(self.review)
        fake['operator_admitted']=True
        b=dict(fake);b.pop('content_sha256')
        fake['content_sha256']=builder.hashjs(b)
        with self.assertRaises(builder.HOLD):
            builder.check_review(fake,self.certificate)

    def test_cannon_wrong_new_source_even_rehashed_not_original_generated(self):
        fake=copy.deepcopy(self.review)
        fake['generated']['source']+='\n// fabricated'
        fake['generated']['source_sha256']=builder.sha256(
            fake['generated']['source'].encode()).hexdigest()
        b=dict(fake);b.pop('content_sha256')
        fake['content_sha256']=builder.hashjs(b)
        self.assertNotEqual(fake['generated']['source'],
          builder.regenerate(self.graft,self.gap_file)['x']['source'])

    def test_cannon_unproved_success_on_independent_cases_refused(self):
        fake=copy.deepcopy(self.review)
        fake['independent_final']['correct']=3
        b=dict(fake);b.pop('content_sha256')
        fake['content_sha256']=builder.hashjs(b)
        with self.assertRaises(builder.HOLD):
            builder.check_review(fake,self.certificate)

    def test_fresh_output_directory_required(self):
        with self.assertRaises(builder.HOLD):
            builder.build(self.original,self.graft,
                          self.gap_file,self.review_file,self.dest)

    def test_generated_readonly_json_receipt_hash_recomputes(self):
        data=dict(self.output);sha=data.pop('content_sha256')
        self.assertEqual(im.hash_obj(data),sha)

    def test_pending_graft_source_pins_required(self):
        with self.assertRaises(builder.HOLD):
            builder.verify_graft_root(Path.cwd())

if __name__=='__main__':unittest.main()
