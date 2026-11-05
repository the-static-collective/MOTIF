"""MOTIF-006 visual imagination runner.

Read actual tiny PNGs, load a source-pinned GRAFT-generated image transition
operator, simulate counterfactual futures and render predicted PNG frames.
No photographic semantics, neural image generation, or external action.
"""
from __future__ import annotations
from collections import deque
from hashlib import sha256
from pathlib import Path
import argparse
import json
import subprocess
import sys
import visual_in as v

HERE=Path(__file__).resolve().parent
GRAFT='0347c492c5e517788c0cbd87ee6f57aef3ce2a81'
CANNON='3f2210ba6272a9538843d093edb64d1b29d2f294'
READER_BLOB='1feded3526746c2af30346acfba191487bc705d2'
PROGRAM='493ecef0320408eed87ec4e9e56c3960f2b6a168caafaa050a22d003f0e5ebe6'
MOVES=((0,-1),(-1,0),(1,0),(0,1))
MAX_STATES=96
MAX_DEPTH=18

class HOLD(ValueError):pass

def checked_manifest():
    path=HERE/'manifest.json'
    if not path.is_file() or path.stat().st_size>30000:
        raise HOLD('Missing review-bound image-in manifest')
    m=json.loads(path.read_text())
    body=dict(m);digest=body.pop('content_sha256',None)
    if digest!=v.digest(body):
        raise HOLD('Mutated build manifest content digest')
    if (m.get('schema')!='motif.visual-build.v0' or
        m.get('status')!='HELD_LOCAL_IMAGE_IMAGINATION_BUILD' or
        m.get('original_graft_commit')!=GRAFT or
        m.get('original_cannon_commit')!=CANNON or
        m.get('generated_visual_source_sha256')!=PROGRAM or
        m.get('original_png_reader_blob')!=READER_BLOB or
        m.get('scope')!='TINY_THREE_COLOR_PNG_ONLY' or
        m.get('synthetic_only') is not True or
        m.get('remote_ai_calls')!=0 or
        m.get('real_actions_authorized') is not False or
        m.get('auto_admit') is not False):
        raise HOLD('Unsupported new source, privileges or scope')
    from hashlib import sha1
    raw=(HERE/'visual_in.py').read_bytes()
    sha=sha1(b'blob '+str(len(raw)).encode()+bytes([0])+raw).hexdigest()
    if sha!=READER_BLOB:
        raise HOLD('Original source-owned PNG reader bytes changed')
    for file,key in (
      ('new_visual_rule.mjs','generated_visual_source_sha256'),
      ('apply.mjs','bridge_sha256'),('run.py','runner_sha256'),
      ('start.png','start_png_sha256'),('goal.png','goal_png_sha256')):
        p=HERE/file
        if not p.is_file() or sha256(p.read_bytes()).hexdigest()!=m[key]:
            raise HOLD('Source-bundled executable or image bytes changed')
    start=v.read_png(HERE/'start.png')
    target=v.read_png(HERE/'goal.png')
    q=v.question((HERE/'start.png').read_bytes(),(HERE/'goal.png').read_bytes())
    if q['content_sha256']!=m['image_gap_sha256']:
        raise HOLD('Original pixel gap does not match source evidence')
    return m,start,target

def reference_move(rows,delta):
    width=len(rows[0]);height=len(rows)
    pixels=[(x,y) for y,r in enumerate(rows)
       for x,c in enumerate(r) if c=='R']
    if len(pixels)!=4:raise HOLD('Invalid object mass during imaginary state')
    nx=[(x+delta[0],y+delta[1]) for x,y in pixels]
    if any(x<0 or y<0 or x>=width or y>=height for x,y in nx):
        return ('HOLD_OUTSIDE_IMAGE',None)
    if any(rows[y][x]=='#' for x,y in nx):
        return ('HOLD_OBSTACLE',None)
    frame=[list(r) for r in rows]
    for x,y in pixels:frame[y][x]='.'
    for x,y in nx:frame[y][x]='R'
    return ('PROPOSED_FRAME',tuple(''.join(r) for r in frame))

def native_predict_batch(calls):
    answers=[]
    for i in range(0,len(calls),48):
        chunk=calls[i:i+48]
        data=json.dumps({'queries':[{'rows':list(rows),'delta':list(delta)}
                      for rows,delta in chunk]},separators=(',',':'))
        if len(data)>90000:raise HOLD('Exceeded bounded local visual horizon')
        try:
            p=subprocess.run(['node','apply.mjs'],cwd=HERE,input=data,text=True,
                capture_output=True,timeout=10)
        except (OSError,subprocess.TimeoutExpired) as e:
            raise HOLD('GRAFT-generated local operator did not respond') from e
        if p.returncode or len(p.stdout)>90000:
            raise HOLD('Generated program rejected bounded imagery')
        obj=json.loads(p.stdout)
        if obj.get('status')!='LOCAL_SYNTHETIC_ONLY' or
           not isinstance(obj.get('answers'),list) or len(obj['answers'])!=len(chunk):
            raise HOLD('Unexpected generated program output')
        for (rows,delta),result in zip(chunk,obj['answers']):
            expected,expect_rows=reference_move(rows,delta)
            if (not isinstance(result,dict) or result.get('status')!=expected or
                (tuple(result['frame']) if isinstance(result.get('frame'),list)
                 else result.get('frame'))!=expect_rows):
                raise HOLD('Independent classical pixel law disagrees with source-generated visual step')
            answers.append((expected,expect_rows))
    return answers

def imagine(initial,target,use_generated):
    if initial==target:return ([initial],[],1)
    current=[initial]
    parent={initial:None}
    states=1
    for depth in range(MAX_DEPTH):
        requests=[(scene,delta) for scene in current for delta in MOVES]
        if not requests:break
        if use_generated:
            answers=native_predict_batch(requests)
        else:
            answers=[reference_move(rows,delta) for rows,delta in requests]
        next_frontier=[]
        for (world,delta),(status,new_world) in zip(requests,answers):
            if status!='PROPOSED_FRAME':continue
            if new_world not in parent:
                parent[new_world]=(world,delta)
                next_frontier.append(new_world)
                states+=1
                if states>MAX_STATES:
                    raise HOLD('Simulation state budget exhausted: no reachability claim')
                if new_world==target:
                    nodes=[new_world];deltas=[]
                    while parent[nodes[-1]] is not None:
                        prev,action=parent[nodes[-1]]
                        deltas.append(action);nodes.append(prev)
                    nodes.reverse();deltas.reverse()
                    return nodes,deltas,states
        current=next_frontier
    return None,None,states

def run(output):
    m,first,goal=checked_manifest()
    if output.exists():raise HOLD('Refuse to overwrite visual evidence')
    # As an ablation, a purely add-only operator can never erase any of the
    # four original occupied pixels while preserving object mass.
    original_red=v.coords(first,'R');target_red=v.coords(goal,'R')
    if len(original_red)!=4 or len(target_red)!=4 or original_red&target_red:
        raise HOLD('Proof of frozen add-only impossibility no longer applies')
    observed_counterfactuals=[]
    for delta,(status,nxt) in zip(MOVES,native_predict_batch(
          [(first,d) for d in MOVES])):
        observed_counterfactuals.append({
          'imagined_delta':list(delta),
          'prediction_status':status,
          'predicted_frame_png_sha256':v.digest(list(nxt)) if nxt else None,
          'real_action_executed':False})
    frames,steps,seen=imagine(first,goal,True)
    classic_frames,classic_steps,classic_seen=imagine(first,goal,False)
    if frames is None or classic_frames is None or len(steps)!=len(classic_steps):
        raise HOLD('New visual grammar did not reach task under equal classical simulation budget')
    if len(frames)!=len(steps)+1 or frames[0]!=first or frames[-1]!=goal:
        raise HOLD('Visual imagination produces invalid path')
    output.mkdir(parents=True)
    clips=output/'frames'
    clips.mkdir()
    for i,frame in enumerate(frames):
        (clips/f'frame-{i:02d}.png').write_bytes(v.encode_png(frame,scale=10))
    rows=['.'.join(f[y] for f in frames) for y in range(len(first))]
    storyboard=v.encode_png(rows,scale=10)
    (output/'imagined-storyboard.png').write_bytes(storyboard)
    info={
      'schema':'motif.visual-imagination-outcome.v0',
      'status':'LOCAL_PNG_IMAGE_IN_FUTURE_FRAMES_RENDERED',
      'source_image_sha256':m['start_png_sha256'],
      'target_image_sha256':m['goal_png_sha256'],
      'generated_graft_program_sha256':PROGRAM,
      'source_owner_reviewed_by_cannon':True,
      'new_visual_operator_family':'ATOMIC_RIGID_TRANSLATION_REMOVES_AND_ADDS',
      'initial_add_only_grammar_can_reach_target':False,
      'imagined_goal_reached':True,
      'imagined_future_frames':len(frames),
      'imagined_actions':len(steps),
      'imagined_moves':[list(x) for x in steps],
      'visited_imagined_worlds':seen,
      'counterfactual_first_moves':observed_counterfactuals,
      'classical_equal_information_goal_reached':True,
      'classical_minimum_steps':len(classic_steps),
      'classical_visited_worlds':classic_seen,
      'superior_to_classical':False,
      'storyboard_png_sha256':sha256(storyboard).hexdigest(),
      'original_images_are_tiny_three_color_pngs':True,
      'model_imagines_semantically':False,
      'image_gen_model_used':False,
      'actual_object_movements':0,
      'external_network_calls':0,
      'automatic_installation':False
    }
    info['content_sha256']=v.digest(info)
    (output/'imagination-receipt.json').write_text(json.dumps(info,indent=2)+'\n')
    return info

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out',type=Path,required=True)
    args=p.parse_args()
    try:print(json.dumps(run(args.out),indent=2))
    except (HOLD,v.HOLD) as exc:
        print(json.dumps({'stage':'HOLD','reason':str(exc)}))
        raise SystemExit(1)
