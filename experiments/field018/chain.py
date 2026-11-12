"""FIELD-018: test the image→3-D→physical-critique→revision *chain*, not just modules.

Two honest execution modes:
  REAL_SOURCE: actual local pixels, source hashes, CV strokes and photo overlap.
    Refuses to invent image semantics, measured site geometry or physical properties.
  CONTROLLED_SYNTHETIC: previously authored FIELD-016 scene, evaluated through
    actual FIELD-017 search → FIELD-016 evaluator → FIELD-015 mechanics.
    A deliberately simulated observation changes the result; it is never
    represented as an observation from the photographed yard.

No data exfiltration, external model inference, or physical actions.
"""
from __future__ import annotations
from dataclasses import asdict
from hashlib import sha256
from pathlib import Path
import importlib.util, json, math, sys

EXPERIMENTS=Path(__file__).resolve().parents[1]
for name in ('field007','field015','field016','field017'):
    sys.path.insert(0,str(EXPERIMENTS/name))
from ink import extract_dashes, trace_receipt
from views import cross_photo_packet
import reconstruction
import engine as f16
import search as f17

MATERIAL_HINTS=('cage panel','privacy screen','chain-link fence','garden netting','old chair','trampoline')


def _sha(path):
    p=Path(path)
    if p.stat().st_size<=0 or p.stat().st_size>30_000_000:
        raise ValueError('Source file too large or empty')
    return sha256(p.read_bytes()).hexdigest()


def inspect_source(sketch, photos=(), *, source_hints=()):
    """Use image pixels; do not pretend a classical stroke matcher is a VLM."""
    sketch=Path(sketch)
    unique={str(p) for p in photos}
    if len(unique)!=len(tuple(photos)):
        raise ValueError('Duplicated photo source')
    if sketch in (Path(p) for p in photos):
        raise ValueError('A sketch must not also be an independent photo witness')
    candidates=extract_dashes(sketch)
    stroke=trace_receipt(sketch,candidates)
    paths=tuple(Path(p) for p in photos)
    pair=cross_photo_packet([(f'photo_{i+1:02d}',str(p)) for i,p in enumerate(paths)]) if paths else dict(photo_count=0,pair_count=0,pairs=[])
    matched=[p for p in pair['pairs'] if p['status']=='TENTATIVE_VISUAL_OVERLAP']
    hints=[]
    for n,item in enumerate(source_hints):
        if not isinstance(item,str) or len(item.strip())<2 or len(item)>180:
            raise ValueError('Invalid source hint')
        hints.append({'id':f'hint-{n+1}','words':item.strip(),
                      'source':'USER_STATEMENT_NOT_IMAGE_RECOGNITION',
                      'photo_bbox':None,'world_position':None,
                      'physical_dimensions':None,'hypothesis_only':True})
    report={
      'experiment':'MOTIF_FIELD_018', 'mode':'REAL_SOURCE_PIXEL_PROCESSING',
      'sources':{'sketch_sha256':_sha(sketch),
                 'photos_sha256':[_sha(p) for p in paths],
                 'user_hints':hints},
      'perception':{'engine':'FIELD-007 OpenCV ink + ORB/RANSAC',
                    'ink_groups':stroke['candidate_count'],
                    'ink_group_axes':[c.axis for c in candidates],
                    'ink_groups_detail':[{'axis':c.axis,'mark_count':len(c.pixel_boxes),
                                           'image_fraction_points':c.points,
                                           'intent':'UNVERIFIED'} for c in candidates],
                    'photos_checked':len(paths),
                    'photo_pairs_checked':pair['pair_count'],
                    'tentative_pair_overlap':len(matched),
                    'photo_pairs_held':sum(p['status']=='HOLD' for p in pair['pairs']),
                    'semantic_objects_detected':0,
                    'note':'Ink strokes are actual pixel detections; no semantic panel recognition was performed.'},
      'reconstruction':{
          'mapanything':'NOT_EXECUTED_NO_CHECKPOINT',
          'depth_anything_3':'NOT_EXECUTED_NO_CHECKPOINT',
          'confirmed_common_3d_frame':False,
          'metric_world_scale':'UNKNOWN',
          'site_registered_points':0,
          'status':'HOLD_NO_CALIBRATED_3D_FROM_SOURCES',
          'what_is_missing':['per-photo semantic object proposals',
                             'camera poses or usable multi-view geometry',
                             'independently measured scale reference']},
      'reasoning':{'available_roles_are_from_user_statements':len(hints),
                   'candidate_reframes':reframe_hints(hints),
                   'physical_arrangements_installable':None,
                   'status':'HOLD_NO_MEASURED_SITE_OR_MATERIAL_GEOMETRY'},
      'physics':{'status':'NOT_EVALUATED_AS_REAL_FENCE',
                 'reason':'Unknown real panel dimensions, anchoring, joints and site geometry',
                 'structural_stability_established':False,
                 'safe_dog_enclosure_established':False},
      'next_direct_input':{
           'kind':'DIRECT_VISUAL_CORRECTION',
           'question':'On the shared board, confirm which detected dashed groups belong to the intended perimeter.',
           'then':'Mark one candidate material in a photo and enter its measured width, or trace one actual opening.',
           'does_not_require_full_3d_model':True},
      'privacy':{'images_sent_to_external_provider':False,
                 'images_shipped_in_public_report':False},
      'claims':{'fully_automatic_photo_to_physics_chain_passed':False,
                'model_inference_calls':0,'simulated_measurement_accepted_as_real':False,
                'animal_containment_certified':False}
    }
    report['receipt_sha256']=sha256(json.dumps(report,sort_keys=True,allow_nan=False).encode()).hexdigest()
    return report


def reframe_hints(hints):
    text=' '.join(x['words'].casefold() for x in hints)
    hypotheses=[]
    if any(x in text for x in ('panel','fence','screen')):
        hypotheses.append({'operator':'RELOCATE_EXISTING',
           'idea':'Treat existing barrier sections as candidate inventory if relocation is permitted and practicable.',
           'required_check':'Which sections can actually be moved without opening another hazard?',
           'confirmed':False})
    if any(x in text for x in ('chair','trampoline','post')):
        hypotheses.append({'operator':'OPPORTUNISTIC_SUPPORT',
           'idea':'Consider the object as a support hypothesis, not a proven anchor.',
           'required_check':'Real mass, tip/slide resistance, attachment strength and unintended hazards.',
           'confirmed':False})
    if any(x in text for x in ('cage','netting','mesh')):
        hypotheses.append({'operator':'COMPOSE_FUNCTIONS',
           'idea':'Investigate whether connected pieces cover an opening with safe geometry.',
           'required_check':'Panel width/height, joint load paths, sharp edges and entanglement.',
           'confirmed':False})
    return hypotheses


def selection_gate(search_report):
    """Never treat 'minimum score' as 'feasible' when all searched cases fail."""
    best=search_report['selected']
    failed=best['verdict']=='REJECTED_UNDER_STATED_MODEL' or bool(best['failures'])
    return {
        'status':'HOLD_NO_MODEL_ADMISSIBLE_LAYOUT' if failed else 'HOLD_CONDITIONAL_REVIEW_ONLY',
        'operational_recommendation':None,
        'least_bad_candidate_id':best['layout']['route']+'|'+','.join(best['layout']['pieces']),
        'known_model_failures':list(best['failures']),
        'verified_real_world_safety':False,
        'note':('Every considered candidate failed stated model constraints; the selected least-bad candidate is NOT a viable plan.'
                if failed else 'The candidate does not fail this simplified model, but no installable/safe plan is certified.')
    }


def synthetic_chain(budget=16):
    """Strict integration of REAL predecessor code on an authored synthetic world."""
    scene=f16.invented_scene()
    before_digest=f17.canonical_state(scene)
    seed=f17.Layout('original',('privacy',))
    initial=f17.run(scene,seed,budget=budget)
    # This is a simulated field observation, not a user's real measurement.
    simulated_observation=f16.Observation('synthetic-width-narrower',
       'MODEL_TENTATIVE','piece_width','porous',1.32,scene.revision+1)
    changed=f16.reenter(scene,simulated_observation)
    after=f17.run(changed,seed,budget=budget)
    assert before_digest==f17.canonical_state(scene)
    result={
      'experiment':'MOTIF_FIELD_018','mode':'CONTROLLED_SYNTHETIC_FULL_MATERIAL_CHAIN',
      'initial_world_sha256':before_digest,
      'updated_world_sha256':f17.canonical_state(changed),
      'engines_actually_invoked':['FIELD-017 bounded search','FIELD-016 candidate evaluator','FIELD-015 analytic wind/tipping/joint screen'],
      'seed_layout':asdict(seed),
      'first':{'evaluated':initial['evaluated'],'initial_verdict':initial['initial']['verdict'],
               'winner':initial['selected']['layout'],
               'winner_verdict':initial['selected']['verdict'],
               'winner_model_failures':initial['selected']['failures'],
               'selection_gate':selection_gate(initial),
               'winner_unknowns':initial['selected']['unknowns'],
               'next_question':initial['next_input'],
               'iterations':[{'candidate':x['candidate'], 'operator':x['operator'],
                              'verdict':x['verdict']} for x in initial['iterations']]},
      'observation':{'kind':'SIMULATED_DIMENSION_CHANGE',
                     'material':'porous','prior_nominal_width_m':1.50,
                     'changed_nominal_width_m':1.32,
                     'NOT_FROM_REAL_PHOTOGRAPH':True},
      'second':{'evaluated':after['evaluated'],
                'winner':after['selected']['layout'],
                'winner_verdict':after['selected']['verdict'],
                'winner_unknowns':after['selected']['unknowns'],
                'winner_model_failures':after['selected']['failures'],
                'selection_gate':selection_gate(after),
                'next_question':after['next_input']},
      'winning_layout_changed':initial['selected']['layout']!=after['selected']['layout'],
      'revision_found_any_non_rejected_candidate':after['selected']['verdict']!='REJECTED_UNDER_STATED_MODEL',
      'world_changed_only_by_declared_observation':True,
      'physical_assembly_executed':0,
      'real_model_reconstruction_calls':0,
      'animal_containment_certified':False,
      'source_real_world_linked':False}
    result['receipt_sha256']=sha256(json.dumps(result,sort_keys=True,allow_nan=False).encode()).hexdigest()
    return result


def module_gates(real,sim):
    """A stage is green only for the precise claim actually demonstrated."""
    p=real['perception']
    return [
       {'name':'Photographs and sketch loaded','status':'PASS','evidence':f"{p['photos_checked']} photos, SHA-256 source receipts"},
       {'name':'Actual sketch pixel processing','status':'PASS','evidence':f"{p['ink_groups']} tentative ink groups from OpenCV"},
       {'name':'Automatic image-semantic inventory','status':'BLOCKED','evidence':'No installed/running VLM; photo objects not independently identified'},
       {'name':'Multi-view registered metric 3D','status':'BLOCKED','evidence':f"{p['photo_pairs_held']} photo pairs held; MapAnything and Depth Anything 3 not run"},
       {'name':'Source-grounded yard physical calculation','status':'BLOCKED','evidence':'Real material and geometric dimensions unknown'},
       {'name':'Synthetic 3D mechanics + recursive revision','status':'PASS_SYNTHETIC_ONLY','evidence':f"{sim['first']['evaluated']} critic calls; after revision admissible candidate={sim['revision_found_any_non_rejected_candidate']}"},
       {'name':'Verified safe physical construction','status':'NOT_TESTED','evidence':'No installed materials or independent engineering/animal safety inspection'},
    ]


def run(sketch,photos=(),source_hints=(),budget=16):
    if type(budget) is not int or not (1<=budget<=250):raise ValueError('Invalid search budget')
    r=inspect_source(sketch,tuple(photos),source_hints=tuple(source_hints))
    s=synthetic_chain(budget)
    return {'real':r,'synthetic':s,'stage_gate':module_gates(r,s),
            'meaning':'A real-source partial chain plus a separately labeled complete synthetic chain; NOT a fully automatic real-world pipeline',
            'privacy_images_embedded':False}


def dump(report,path):
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    Path(path).write_text(json.dumps(report,indent=2,ensure_ascii=False,allow_nan=False))
