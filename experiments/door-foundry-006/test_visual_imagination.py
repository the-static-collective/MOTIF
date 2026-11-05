"""MOTIF-006: bounded PNG image-in, GRAFT visual source and hypothetical frames."""
import json,os,shutil,subprocess,sys,tempfile,unittest
from pathlib import Path
from hashlib import sha256
import visual_in as v
import build as forge

class ImageImaginationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.src=Path(os.environ['IMG_START'])
        cls.goal=Path(os.environ['IMG_TARGET'])
        cls.gap=Path(os.environ['IMG_GAP'])
        cls.cannon=Path(os.environ['CANNON_RECEIPT'])
        cls.graft=Path(os.environ['GRAFT_SOURCE'])
        cls.temp=tempfile.TemporaryDirectory(prefix='motif006-')
        cls.home=Path(cls.temp.name)
        cls.output=cls.home/'new-build'
        cls.manifest=forge.build(cls.src,cls.goal,cls.gap,
                                 cls.cannon,cls.graft,cls.output)
        cls.actual=subprocess.run([sys.executable,'run.py','--out',str(cls.home/'drawn')],
            cwd=cls.output,text=True,capture_output=True,timeout=45)
        cls.result=json.loads(cls.actual.stdout)

    @classmethod
    def tearDownClass(cls):cls.temp.cleanup()

    def rerun(self,root):
        return subprocess.run([sys.executable,'run.py','--out',
            str(root.parent/'new-frames')],cwd=root,text=True,capture_output=True,timeout=45)

    def test_actual_binary_png_image_in_roundtrips_without_external_models(self):
        source=self.src.read_bytes()
        self.assertTrue(source.startswith(v.SIGN))
        original=v.decode_png(source)
        self.assertEqual(original,v.decode_png(v.encode_png(original)))
        self.assertEqual(len(original),8)
        self.assertEqual(len(original[0]),9)

    def test_user_supplied_tiny_paletted_pngs_work_without_special_demo_flag(self):
        a=v.encode_png(v.demo_scene(0,1,[]))
        b=v.encode_png(v.demo_scene(5,1,[]))
        q=v.question(a,b)
        self.assertEqual(q['scope'],'SYNTHETIC_RASTER_ONLY')
        self.assertEqual(q['proof']['old_red_pixels_must_be_cleared'],4)
        self.assertEqual(q['start_png_sha256'],sha256(a).hexdigest())

    def test_corrupted_png_crc_is_refused(self):
        bad=bytearray(self.src.read_bytes())
        bad[-19]^=1
        with self.assertRaises(v.HOLD):v.decode_png(bytes(bad))

    def test_oversized_real_png_is_refused_before_symbolic_mapping(self):
        large=v.encode_png(['.'*17]*8)
        with self.assertRaises(v.HOLD):v.decode_png(large)

    def test_unrecognized_pixel_color_fails_closed_palette(self):
        import struct,zlib
        raw=b'\0'+bytes([1,2,3])*3
        source=v.SIGN+v.png_chunk(b'IHDR',
          struct.pack('>IIBBBBB',3,3,8,2,0,0,0))+v.png_chunk(
          b'IDAT',zlib.compress(raw*3))+v.png_chunk(b'IEND',b'')
        with self.assertRaises(v.HOLD):v.decode_png(source)

    def test_gap_is_a_real_pixel_removal_invariant_not_failed_depth_search(self):
        q=v.question(self.src.read_bytes(),self.goal.read_bytes())
        self.assertEqual(q['status'],'PROVED_ADD_ONLY_GRAMMAR_CANNOT_RELOCATE')
        self.assertTrue(q['proof']['fixed_graft029_add_only_insufficient'])
        self.assertEqual(q['proof']['new_red_pixels_must_be_filled'],4)
        self.assertEqual(set(v.coords(q['start_rows'],'R'))&
                         set(v.coords(q['goal_rows'],'R')),set())

    def test_ghost_move_of_blue_obstacles_refused_at_image_gap(self):
        a=list(v.read_png(self.src));b=list(v.read_png(self.goal))
        b[3]=b[3].replace('#','.',1)
        with self.assertRaises(v.HOLD):
            v.question(v.encode_png(a),v.encode_png(b))

    def test_cannon_review_matches_exact_original_source_owned_program(self):
        packet=forge.load(self.cannon)
        question=forge.load(self.gap)
        receipt,compiled=forge.verify(self.graft,packet,question,
          self.src.read_bytes(),self.goal.read_bytes(),self.gap)
        self.assertEqual(receipt,packet['content_sha256'])
        self.assertEqual(compiled['source_sha256'],forge.PROGRAM)
        self.assertEqual(compiled['source'],packet['source_owned_generated']['source'])
        self.assertEqual(packet['independent_final']['correct'],8)

    def test_new_executable_build_is_real_not_a_planning_document(self):
        self.assertTrue((self.output/'new_visual_rule.mjs').is_file())
        self.assertTrue((self.output/'run.py').is_file())
        self.assertTrue((self.output/'start.png').is_file())
        self.assertEqual(self.manifest['generated_visual_source_sha256'],
                         sha256((self.output/'new_visual_rule.mjs').read_bytes()).hexdigest())
        self.assertEqual(self.manifest['status'],'HELD_LOCAL_IMAGE_IMAGINATION_BUILD')

    def test_new_image_in_future_planner_executed_successfully(self):
        self.assertEqual(self.actual.returncode,0,self.actual.stderr+self.actual.stdout)
        self.assertEqual(self.result['status'],'LOCAL_PNG_IMAGE_IN_FUTURE_FRAMES_RENDERED')
        self.assertTrue(self.result['imagined_goal_reached'])
        self.assertGreater(self.result['imagined_future_frames'],3)

    def test_obstacle_requires_genuine_imagined_detour(self):
        self.assertGreater(self.result['imagined_actions'],5)
        self.assertEqual(self.result['imagined_actions'],
                         self.result['classical_minimum_steps'])
        self.assertEqual(len(self.result['imagined_moves']),
                         self.result['imagined_actions'])

    def test_native_generated_program_proposes_multiple_counterfactual_first_steps(self):
        rows=self.result['counterfactual_first_moves']
        self.assertEqual(len(rows),4)
        self.assertTrue(any(c['prediction_status']=='PROPOSED_FRAME' for c in rows))
        self.assertTrue(all(c['real_action_executed'] is False for c in rows))

    def test_imagined_frames_really_render_as_nonempty_png(self):
        sheet=self.home/'drawn'/'imagined-storyboard.png'
        self.assertTrue(sheet.read_bytes().startswith(v.SIGN))
        self.assertEqual(sha256(sheet.read_bytes()).hexdigest(),
                         self.result['storyboard_png_sha256'])
        allframes=sorted((self.home/'drawn'/'frames').glob('frame-*.png'))
        self.assertEqual(len(allframes),self.result['imagined_future_frames'])
        self.assertEqual(v.decode_png(allframes[0].read_bytes(),limit=160)[:2],
                         v.decode_png(v.encode_png(v.read_png(self.src),scale=10),
                                      limit=160)[:2])

    def test_all_rendered_steps_preserve_obstacle_and_object_mass(self):
        files=sorted((self.home/'drawn'/'frames').glob('frame-*.png'))
        object_blocks=[]
        for path in files:
            rendered=v.decode_png(path.read_bytes(),limit=160)
            red=v.coords(rendered,'R')
            self.assertEqual(len(red),400)
            object_blocks.append(red)
            self.assertEqual(len(v.coords(rendered,'#')),len(v.coords(v.read_png(self.src),'#'))*100)
        self.assertNotEqual(object_blocks[0],object_blocks[-1])

    def test_rehashed_false_authority_still_rejected(self):
        packet=forge.load(self.cannon)
        packet['authority']['operator_admitted']=True
        body=dict(packet);body.pop('content_sha256')
        packet['content_sha256']=v.digest(body)
        with self.assertRaises(forge.HOLD):
            forge.verify(self.graft,packet,forge.load(self.gap),
               self.src.read_bytes(),self.goal.read_bytes(),self.gap)

    def test_source_recompiled_from_unmerged_graft_exact_revision(self):
        self.assertEqual(self.manifest['original_graft_commit'],forge.GRAFT)
        self.assertEqual(self.manifest['original_cannon_commit'],forge.CANNON)
        self.assertFalse(self.manifest['auto_admit'])
        self.assertFalse(self.manifest['real_actions_authorized'])

    def test_rewrite_generated_source_after_build_causes_hold(self):
        with tempfile.TemporaryDirectory() as t:
            target=Path(t)/'copy'
            shutil.copytree(self.output,target)
            p=target/'new_visual_rule.mjs'
            p.write_text(p.read_text()+'\n// changed')
            run=self.rerun(target)
            self.assertNotEqual(run.returncode,0)
            self.assertEqual(json.loads(run.stdout)['stage'],'HOLD')

    def test_rehashed_manifest_false_permission_refused(self):
        with tempfile.TemporaryDirectory() as t:
            target=Path(t)/'copy'
            shutil.copytree(self.output,target)
            p=target/'manifest.json'
            manifest=json.loads(p.read_text())
            manifest['real_actions_authorized']=True
            body=dict(manifest);body.pop('content_sha256')
            manifest['content_sha256']=v.digest(body)
            p.write_text(json.dumps(manifest))
            run=self.rerun(target)
            self.assertNotEqual(run.returncode,0)
            self.assertEqual(json.loads(run.stdout)['stage'],'HOLD')

    def test_no_real_action_or_claimed_alg_superiority(self):
        self.assertEqual(self.result['actual_object_movements'],0)
        self.assertEqual(self.result['external_network_calls'],0)
        self.assertFalse(self.result['superior_to_classical'])
        self.assertFalse(self.result['model_imagines_semantically'])
        self.assertFalse(self.result['image_gen_model_used'])

    def test_receipt_content_digest_matches_actual_record(self):
        p=forge.load(self.home/'drawn'/'imagination-receipt.json')
        body=dict(p);claim=body.pop('content_sha256')
        self.assertEqual(v.digest(body),claim)

if __name__=='__main__':unittest.main()
