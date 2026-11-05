"""MOTIF-005: source-native impossibility certificate for the ORIGINAL fixed verbs.

Proves a reachability invariant before requesting GRAFT source: the target
predicate is absent in the initial synthetic world and no fixed MOTIF-002
rewrite adds it. Therefore no finite sequence of those fixed verbs can reach
the goal (stronger than a depth-limited unsuccessful search).

This is a closed, artificial domain. NOT a proof that the physical world is
impossible or that no other planner could invent a new edit.
"""
from __future__ import annotations
from hashlib import sha1,sha256
from pathlib import Path
import argparse
import json
import subprocess
import sys

SOURCE="5ee9207f04af2826750863526af7f92b31ef8578"
SOURCE_BLOB="b9f1e7b7879a94f7ef3869bc305608c4d7fa8695"
GOAL=("inspected","bike1")
TYPE="bike"

class HOLD(ValueError): pass

def hash_obj(x):
    return sha256(json.dumps(x,separators=(',',':'),ensure_ascii=False,
        allow_nan=False).encode()).hexdigest()

def git_blob(path):
    raw=Path(path).read_bytes()
    return sha1(b'blob '+str(len(raw)).encode()+bytes([0])+raw).hexdigest()

def original(root):
    root=Path(root).resolve()
    try:
        commit=subprocess.check_output(['git','-C',str(root),'rev-parse','HEAD'],
                 text=True,stderr=subprocess.DEVNULL,timeout=6).strip()
    except (OSError,subprocess.SubprocessError) as e:
        raise HOLD('Original source is not an exact Git checkout') from e
    source=root/'experiments/002/motif002.py'
    if commit!=SOURCE or not source.is_file() or git_blob(source)!=SOURCE_BLOB:
        raise HOLD('Fixed original MOTIF source revision or code changed')
    p=str(source.parent)
    if p not in sys.path:sys.path.insert(0,p)
    import motif002 as original_two
    return original_two

def prove(original_root,with_permission=True):
    two=original(original_root)
    world=two.scene(permissions=with_permission)
    verbs=two.induce(two.lessons())
    if not with_permission:raise HOLD('No synthetic permission for operator gap trial')
    if not {('permits','Jo','Mira','bike1'),('broken','bike1'),
            ('bike','bike1')}.issubset(world):
        raise HOLD('No explicit synthetic permission and broken bike fixture')
    before=GOAL in world
    adding=[v.id for v in verbs.values() if
            any(f[0]==GOAL[0] for f in v.adds)]
    no_emitter=len(adding)==0
    if before or not no_emitter:
        raise HOLD('Requested goal can already be added by original grammar')
    classical=two.explore(world,verbs,steps=8)
    if GOAL in classical['final']:
        raise HOLD('Original fixed baseline already reaches goal')
    # Actual invariant proof: no initial goal predicate, no fixed verb adds it.
    # This is independent of any incomplete search horizon.
    body={
      'schema':'motif.missing-operator.v0',
      'scope':'CLOSED_SYNTHETIC_REWRITE_ONLY',
      'status':'PROVEN_UNREACHABLE_UNDER_ORIGINAL_FIXED_VERBS',
      'original_source_commit':SOURCE,
      'requested_goal':list(GOAL),
      'requested_target_type':TYPE,
      'proof':{
        'invariant':'NO_ORIGINAL_VERB_ADDS_REQUESTED_PREDICATE',
        'exact_predicate_absent_from_start':not before,
        'all_original_effects_exclude_predicate':no_emitter,
        'original_verb_count':len(verbs),
        'original_emitting_verbs':adding,
        'finite_replay_horizon':8,
        'finite_replay_states':classical['reachable'],
        'original_fixed_replay_reaches_goal':False,
        'source_git_blob_sha1':SOURCE_BLOB,
        'goal_predicate':GOAL[0],
        'semantic_scope':'FORMAL_CLOSED_GRAMMAR_ONLY'
      },
      'permission_to_propose_local_code':True,
      'permission_to_deploy':False,
      'permission_to_contact':False
    }
    return {**body,'content_sha256':hash_obj(body)}

def verify(packet,original_root):
    if not isinstance(packet,dict) or set(packet)!={
       'schema','scope','status','original_source_commit','requested_goal',
       'requested_target_type','proof','permission_to_propose_local_code',
       'permission_to_deploy','permission_to_contact','content_sha256'
    }:raise HOLD('Impossibility packet has unknown fields')
    body=dict(packet);claimed=body.pop('content_sha256')
    if claimed!=hash_obj(body):raise HOLD('Impossibility proof digest mismatch')
    expected=prove(original_root)
    if packet!=expected:raise HOLD('Impossibility proof does not replay from original source')
    return claimed

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--original',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--deny',action='store_true')
    opts=parser.parse_args()
    try:
        packet=prove(opts.original,not opts.deny)
        if opts.out.exists():raise HOLD('Never overwrite question evidence')
        opts.out.write_text(json.dumps(packet,indent=2)+'\n')
        print(json.dumps({'status':packet['status'],
                          'sha256':packet['content_sha256'],
                          'original_verb_count':packet['proof']['original_verb_count'],
                          'unbounded_invariant':True}))
    except HOLD as exc:
        print(json.dumps({'stage':'HOLD','reason':str(exc)}))
        raise SystemExit(1)

if __name__=='__main__':main()
