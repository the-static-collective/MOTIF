"""MOTIF-005: impossibility -> actual GRAFT source-owner rule -> CANNON HOLD
-> new runnable MOTIF graph planner whose reachable goal set is larger.

The invariant proof is about a frozen synthetic grammar, not reality.
The generated rule is finite-grammar JS, not arbitrary agent invention.
"""
from __future__ import annotations
from hashlib import sha256,sha1
from pathlib import Path
import argparse
import json
import shutil
import subprocess
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
import impossibility as gap_owner
GRAFT_COMMIT='5023b594b0daa4f0328d01643a7f258b71f60bb9'
CANNON_COMMIT='03f8c012b3d6eb48ed821a2be25aa5fd6a48970c'
GRAFT_SOURCE_BLOB='3ce0366a26b927a63cf22f0e99a70e4f3db89258'
MOTIF_SOURCE_BLOB='b9f1e7b7879a94f7ef3869bc305608c4d7fa8695'
BRIDGE=HERE/'apply.mjs'
RUNNER=HERE/'run_extended.py'

class HOLD(ValueError):pass

def hashjs(x):
    return sha256(json.dumps(x,separators=(',',':'),ensure_ascii=False,
                            allow_nan=False).encode()).hexdigest()

def read_doc(path):
    p=Path(path)
    if not p.is_file() or p.stat().st_size>170000:
        raise HOLD('Missing or oversized research evidence')
    try:r=json.loads(p.read_text())
    except ValueError as e:raise HOLD('Malformed receipt') from e
    if not isinstance(r,dict):raise HOLD('Expected object receipt')
    return r

def blob(data):
    return sha1(b'blob '+str(len(data)).encode()+bytes([0])+data).hexdigest()

def verify_graft_root(root):
    root=Path(root).resolve()
    try:commit=subprocess.check_output(['git','-C',str(root),'rev-parse','HEAD'],
         text=True,stderr=subprocess.DEVNULL,timeout=5).strip()
    except (OSError,subprocess.SubprocessError) as e:raise HOLD('No original GRAFT repo') from e
    source=root/'src/missing-operator-forge-029.mjs'
    if commit!=GRAFT_COMMIT or not source.is_file() or blob(source.read_bytes())!=GRAFT_SOURCE_BLOB:
        raise HOLD('Not original GRAFT-029 source revision')
    return root

def check_review(packet,question):
    if not isinstance(packet,dict) or set(packet)!={
      'schema','status','original_motif_gap_sha256','source_owner',
      'original_original_motif_commit','classical_reference','generated',
      'native_evidence','independent_final',
      'synthetic_original_fixed_grammar_unreachable',
      'synthesized_extended_grammar_can_reach_goal',
      'fair_classical_learner_can_receive_same_examples',
      'superior_to_classical_not_claimed','no_observed_physical_inspection',
      'consent_from_packet','signed','automatic_repo_writes',
      'external_requests','operator_admitted','content_sha256'}:
        raise HOLD('Unexpected CANNON claims')
    raw=dict(packet);digest=raw.pop('content_sha256')
    if digest!=hashjs(raw):raise HOLD('CANNON review content mismatch')
    g=packet['generated']
    x=packet['source_owner']
    c=packet['classical_reference']
    final=packet['independent_final']
    if (packet['schema']!='cannon.graft-new-operator-review.v0' or
        packet['status']!='HOLD_GENERATED_OPERATOR_UNADMITTED' or
        packet['original_motif_gap_sha256']!=question['content_sha256'] or
        packet['original_original_motif_commit']!=gap_owner.SOURCE or
        x.get('commit')!=GRAFT_COMMIT or
        x.get('repo')!='the-static-collective/GRAFT' or
        x.get('authority_from_sha') is not False or
        not any(f.get('git_blob_sha1')==GRAFT_SOURCE_BLOB and
         f.get('path')=='src/missing-operator-forge-029.mjs'
         for f in x.get('verified_git_blobs',[])) or
        g.get('head_relation')!=gap_owner.GOAL[0] or
        g.get('required_guards')!=['broken','permits'] or
        g.get('genuine_original_graft_compiler') is not True or
        g.get('installed') is not False or
        g.get('executable_permissions')!='NONE' or
        not isinstance(g.get('source'),str) or len(g['source'])>5000 or
        sha256(g['source'].encode()).hexdigest()!=g.get('source_sha256') or
        packet['native_evidence'].get('variants_generated')!=3 or
        len(packet['native_evidence'].get('rejected',[]))!=2 or
        final.get('n')!=6 or final.get('correct')!=6 or
        c.get('fixed_step8_reaches') is not False or
        c.get('invariant_holds') is not True or
        c.get('fair_classical_denied_permission_leak') is not False or
        packet['synthetic_original_fixed_grammar_unreachable'] is not True or
        packet['synthesized_extended_grammar_can_reach_goal'] is not True or
        packet['superior_to_classical_not_claimed'] is not True or
        packet['fair_classical_learner_can_receive_same_examples'] is not True or
        packet['consent_from_packet'] is not False or
        packet['signed'] is not False or
        packet['operator_admitted'] is not False or
        packet['no_observed_physical_inspection'] is not True or
        packet['automatic_repo_writes']!=0 or packet['external_requests']!=0):
        raise HOLD('Unreviewed operator, authority claim, or misleading comparator')
    return digest

def regenerate(graft,question_path):
    # Run ORIGINAL GRAFT-029 source. No code from the CANNON envelope is
    # executed before independent source-owner recompilation matches bytes.
    js=("import {pathToFileURL} from 'node:url';"+
        "import {readFileSync} from 'node:fs';"+
        "import {resolve} from 'node:path';"+
        "const root=resolve(process.argv[1]);"+
        "const m=await import(pathToFileURL(resolve(root,"+
        "'src/missing-operator-forge-029.mjs')).href);"+
        "const gap=JSON.parse(readFileSync(process.argv[2],'utf8'));"+
        "const x=m.compileVariant(gap,['broken','permits']);"+
        "const training=m.casesForSyntheticGraph().train;"+
        "console.log(JSON.stringify({x,training}));")
    try:r=subprocess.check_output(['node','--input-type=module','-e',js,
                  str(graft),str(Path(question_path).resolve())],
                  text=True,timeout=12,stderr=subprocess.DEVNULL)
    except (OSError,subprocess.SubprocessError) as e:
        raise HOLD('Original GRAFT could not regenerate program') from e
    out=json.loads(r)
    if out.get('x',{}).get('schema')!='graft029.generated-graph-operator/v0':
        raise HOLD('Native GRAFT compiler contract changed')
    return out

def build(original_root,graft_root,question_path,review_path,out):
    question=read_doc(question_path)
    gap_owner.verify(question,original_root)
    donor=verify_graft_root(graft_root)
    receipt=read_doc(review_path)
    review_sha=check_review(receipt,question)
    actual=regenerate(donor,question_path)
    program=actual['x']
    if (program['source']!=receipt['generated']['source'] or
        program['source_sha256']!=receipt['generated']['source_sha256'] or
        program.get('code_installed') is not False or
        program.get('guard_contract')!=['broken','permits'] or
        program.get('external_authority') is not False):
        raise HOLD('CANNON proposed different source from ORIGINAL GRAFT compiler')
    out=Path(out).resolve()
    if out.exists():raise HOLD('Refuse to overwrite existing build')
    out.mkdir(parents=True)
    p=out/'experiments/002/motif002.py'
    p.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(Path(original_root)/'experiments/002/motif002.py',p)
    if blob(p.read_bytes())!=MOTIF_SOURCE_BLOB:raise HOLD('Original MOTIF source modified')
    (out/'new_guarded_operator.mjs').write_text(program['source'])
    (out/'training_cases.json').write_text(json.dumps(actual['training'],indent=2)+'\n')
    shutil.copyfile(RUNNER,out/'run.py')
    shutil.copyfile(BRIDGE,out/'apply.mjs')
    body={
      'schema':'motif.new-operator-built.v0',
      'source_motif_original_commit':gap_owner.SOURCE,
      'source_graft_original_commit':GRAFT_COMMIT,
      'source_cannon_review_commit':CANNON_COMMIT,
      'impossibility_certificate_sha256':question['content_sha256'],
      'cannon_review_receipt_sha256':review_sha,
      'generated_source_sha256':program['source_sha256'],
      'generated_grammar':'TYPED_GUARDED_ADDITION_2_OPTIONAL_ANTECEDENTS_V0',
      'operator_guard_contract':program['guard_contract'],
      'original_motif_git_blob':MOTIF_SOURCE_BLOB,
      'runner_sha256':sha256(RUNNER.read_bytes()).hexdigest(),
      'bridge_sha256':sha256(BRIDGE.read_bytes()).hexdigest(),
      'train_sha256':sha256((out/'training_cases.json').read_bytes()).hexdigest(),
      'synthetic_only':True,
      'permission_to_real_act':False,
      'permission_to_write_repos':False,
      'field_result_observed':False,
      'automatic_admission':False,
      'candidate_status':'HELD_GENERATED_OPERATOR_BUILD'
    }
    body['content_sha256']=gap_owner.hash_obj(body)
    (out/'manifest.json').write_text(json.dumps(body,indent=2)+'\n')
    return body

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('original','graft','question','review','out'):
        p.add_argument('--'+name,type=Path,required=True)
    args=p.parse_args()
    try:
        record=build(args.original,args.graft,args.question,args.review,args.out)
        print(json.dumps({'status':record['candidate_status'],
              'operator_source_sha256':record['generated_source_sha256'],
              'build_receipt_sha256':record['content_sha256']}))
    except (HOLD,gap_owner.HOLD) as e:
        print(json.dumps({'stage':'HOLD','reason':str(e)}));raise SystemExit(1)

if __name__=='__main__':main()
