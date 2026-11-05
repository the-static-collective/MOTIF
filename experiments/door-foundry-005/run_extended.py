"""Execute one held new MOTIF build with a source-compiled GRAFT graph organ.
Only synthetic facts, bounded local processes, no physical actions or APIs.
"""
from __future__ import annotations
from collections import deque
from hashlib import sha1,sha256
from pathlib import Path
import json
import subprocess
import sys

HERE=Path(__file__).resolve().parent
MOTIF_ORIGINAL_SHA='b9f1e7b7879a94f7ef3869bc305608c4d7fa8695'
GENERATED_SOURCE_SHA='247243373a558a73b41379ec3505dc5d8e5c1be1aacf89efc926aa9b87895d81'
GRAFT_COMMIT='5023b594b0daa4f0328d01643a7f258b71f60bb9'
CANNON_COMMIT='03f8c012b3d6eb48ed821a2be25aa5fd6a48970c'
GOAL=('inspected','bike1')

class HOLD(ValueError):pass

def hash_obj(obj):
    return sha256(json.dumps(obj,ensure_ascii=False,allow_nan=False,
               separators=(',',':')).encode()).hexdigest()

def git_blob(path):
    raw=Path(path).read_bytes()
    return sha1(b'blob '+str(len(raw)).encode()+bytes([0])+raw).hexdigest()

def manifest():
    p=HERE/'manifest.json'
    if not p.is_file() or p.stat().st_size>30000:raise HOLD('Missing bounded build evidence')
    x=json.loads(p.read_text())
    body=dict(x);claim=body.pop('content_sha256',None)
    if claim!=hash_obj(body):raise HOLD('Build manifest digest changed')
    if (x.get('schema')!='motif.new-operator-built.v0' or
        x.get('candidate_status')!='HELD_GENERATED_OPERATOR_BUILD' or
        x.get('source_motif_original_commit')!='5ee9207f04af2826750863526af7f92b31ef8578' or
        x.get('source_graft_original_commit')!=GRAFT_COMMIT or
        x.get('source_cannon_review_commit')!=CANNON_COMMIT or
        x.get('generated_source_sha256')!=GENERATED_SOURCE_SHA or
        x.get('original_motif_git_blob')!=MOTIF_ORIGINAL_SHA or
        x.get('operator_guard_contract')!=['broken','permits'] or
        x.get('synthetic_only') is not True or
        x.get('permission_to_real_act') is not False or
        x.get('permission_to_write_repos') is not False or
        x.get('field_result_observed') is not False or
        x.get('automatic_admission') is not False):
        raise HOLD('New generated build was not source-owned and held')
    p=HERE/'experiments/002/motif002.py'
    if not p.is_file() or git_blob(p)!=MOTIF_ORIGINAL_SHA:
        raise HOLD('Original MOTIF source mutation')
    for filename,key in [('new_guarded_operator.mjs','generated_source_sha256'),
                         ('apply.mjs','bridge_sha256'),
                         ('run.py','runner_sha256'),
                         ('training_cases.json','train_sha256')]:
        file=HERE/filename
        if not file.is_file() or sha256(file.read_bytes()).hexdigest()!=x[key]:
            raise HOLD('Original generated or runner source changed')
    return x

def module():
    p=str(HERE/'experiments/002')
    if p not in sys.path:sys.path.insert(0,p)
    import motif002 as two
    return two

def allowed_bindings(world):
    people={f[1] for f in world if len(f)==2 and f[0]=='person'}
    bikes=sorted((f[1],f[2]) for f in world
                 if len(f)==3 and f[0]=='owns' and f[2]==GOAL[1])
    return tuple({'owner':owner,'actor':actor,'target':bike}
                 for owner,bike in bikes for actor in sorted(people))

def generated_action(world,roles):
    data={'world':[list(f) for f in sorted(world)],'roles':roles}
    try:
        run=subprocess.run(['node','apply.mjs'],cwd=HERE,
             text=True,input=json.dumps(data,separators=(',',':')),
             capture_output=True,timeout=6)
    except (OSError,subprocess.TimeoutExpired) as e:
        raise HOLD('Generated local JS refused bounded execution') from e
    if run.returncode or len(run.stdout)>1500:
        raise HOLD('Generated local JS could not produce reviewable output')
    try:result=json.loads(run.stdout)
    except ValueError as e:raise HOLD('Generated JS emitted malformed response') from e
    if not isinstance(result,dict) or set(result)!={'status','added'}:
        raise HOLD('Generated JS output schema changed')
    if result['status']=='PROPOSED_SYNTHETIC_ADD':
        added=result['added']
        if added!=['inspected',roles['target']] or tuple(added) in world:
            raise HOLD('Generated JS attempted unverified graph edit')
        return frozenset(set(world)|{tuple(added)})
    if result['added'] is not None or result['status'] not in {
       'HOLD_GUARD','HOLD_UNTYPED','HOLD_ALREADY_PRESENT','HOLD_BAD_INPUT'}:
        raise HOLD('Unknown effect from generated JS')
    return None

def explore(two,initial,verbs,with_generated,max_depth=3,max_states=100):
    queue=deque([(initial,())])
    seen={initial}
    while queue:
        world,path=queue.popleft()
        if GOAL in world:
            return {'reached':True,'path':path,'visited':len(seen)}
        if len(path)>=max_depth:continue
        subsequent=[]
        for name,roles,next_world in two.possibilities(world,verbs):
            subsequent.append((next_world,('original:'+name,list(roles))))
        if with_generated:
            for binding in allowed_bindings(world):
                next_world=generated_action(world,binding)
                if next_world is not None:
                    subsequent.append((next_world,('graft029:guarded-add',binding)))
        for after,step in subsequent:
            if after not in seen:
                if len(seen)>=max_states:
                    raise HOLD('Bounded search exhausted; cannot claim impossibility')
                seen.add(after)
                queue.append((after,path+(step,)))
    return {'reached':False,'path':(),'visited':len(seen)}

def run():
    m=manifest()
    two=module()
    before=two.scene()
    original_verbs=two.induce(two.lessons())
    if (GOAL in before or any(f[0]=='inspected'
          for verb in original_verbs.values() for f in verb.adds)):
        raise HOLD('Original fixed operator impossible-proof premise failed')
    original=explore(two,before,original_verbs,False)
    extended=explore(two,before,original_verbs,True)
    forbidden=explore(two,two.scene(permissions=False),original_verbs,True)
    if original['reached'] or not extended['reached'] or forbidden['reached']:
        raise HOLD('New graph operator does not expand only permitted reachable world')
    training=json.loads((HERE/'training_cases.json').read_text())
    if not isinstance(training,list) or len(training)!=2:
        raise HOLD('Fair classical comparator lacks same training demonstrations')
    episodes=[]
    for case in training:
        prior=frozenset(tuple(f) for f in case['world'])
        target=case['roles']['target']
        episodes.append(two.Transition(prior,frozenset(set(prior)|{
           ('inspected',target)}),'SYNTHETIC'))
    fair_verbs=two.induce(episodes)
    fair=explore(two,before,fair_verbs,False)
    fair_denied=explore(two,two.scene(permissions=False),fair_verbs,False)
    if not fair['reached'] or fair_denied['reached']:
        raise HOLD('Matched classical comparator was incorrectly credited')
    report={
      'schema':'motif.new-grammar-reachability.v0',
      'status':'GENERATED_CLOSED_GRAMMAR_EXPANDS_SYNTHETIC_REACHABILITY',
      'manifest_sha256':m['content_sha256'],
      'original_fixed_verbs':len(original_verbs),
      'original_fixed_goal_reached':original['reached'],
      'source_owned_new_generated_operator':True,
      'new_generated_operator_goal_reached':extended['reached'],
      'new_generated_operator_path':list(extended['path']),
      'original_fixed_search_states':original['visited'],
      'extended_search_states':extended['visited'],
      'without_permission_goal_reached':forbidden['reached'],
      'fair_original_motif_002_newly_trained_goal_reached':fair['reached'],
      'fair_original_motif_002_newly_trained_denied_leak':fair_denied['reached'],
      'fair_classical_comparison_matches':True,
      'claimed_better_than_classical':False,
      'all_graph_states_synthetic':True,
      'actual_bicycle_inspections':0,
      'human_contacts':0,
      'production_promotions':0,
      'external_requests':0
    }
    report['content_sha256']=hash_obj(report)
    print(json.dumps(report,indent=2))

if __name__=='__main__':
    try:run()
    except HOLD as e:
        print(json.dumps({'stage':'HOLD','reason':str(e)}));raise SystemExit(1)
