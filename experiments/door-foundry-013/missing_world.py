"""MOTIF-013 — THE MISSING WORLD.

When a new simulated image observation changes a blue obstacle, the original
four original MOTIF-009 worlds and GRAFT-030's stationary-obstacle movement
grammar cannot explain it. Establish *bounded* out-of-support evidence rather
than forcing a posterior onto a false hypothesis; request a source-owned new
GRAFT-031 finite *environmental event* operator. Independently re-run and test
actual generated JS. HOLD the result (nothing installed, operated or observed).

Source images are tiny synthetic PNGs. This does not discover an unconstrained
physical world, real-source identity, or a gate controller.
"""
from __future__ import annotations
import argparse,json,sys,subprocess
from pathlib import Path
from hashlib import sha1,sha256
HERE=Path(__file__).resolve().parent
sys.path[:0]=[str(HERE.parent/"door-foundry-009"),
             str(HERE.parent/"door-foundry-010"),
             str(HERE.parent/"door-foundry-008"),
             str(HERE.parent/"door-foundry-006")]
import visual_in as png
import world_model as original
import cross_examine as prior

GRAFT_OWNER_SHA="8a4e85e2de9bdfdf74cd5bebd95fbab7cf11ab36"
GRAFT_OWNER_BLOB="e2c3348b65c556fb1b6df123e0aa4e7d71eecad1"
OPEN_CELLS=((4,3),(4,4))
WORLD_IDS=original.WORLD_IDS
class HOLD(ValueError):pass
def need(c,why):
    if not c:raise HOLD(why)
def read(p):
    try:return original.read(p)
    except original.HOLD as exc:raise HOLD(str(exc)) from exc
def digest(x):return png.digest(x)
def only_new(path):
    need(not Path(path).exists(),"HOLD_REFUSE_EVIDENCE_OVERWRITE")
def verify_graft(root):
    """A Git SHA alone does not grant source authority: byte/blob pin as well."""
    root=Path(root).resolve()
    src=root/"src"/"world-model-031.mjs"
    need(src.is_file() and src.stat().st_size<20000,
         "HOLD_NEW_MODEL_SOURCE_UNAVAILABLE")
    content=src.read_bytes()
    blob=sha1(b"blob "+str(len(content)).encode()+b"\0"+content).hexdigest()
    need(blob==GRAFT_OWNER_BLOB,
         "HOLD_GRAFT_SOURCE_BYTES_NOT_PREVIOUSLY_REVIEWED")
    try:
        x=subprocess.run(["git","-C",str(root),"rev-parse","HEAD"],
         check=True,capture_output=True,text=True,timeout=10)
    except (subprocess.CalledProcessError,subprocess.TimeoutExpired,OSError) as exc:
        raise HOLD("HOLD_CANNOT_VERIFY_GRAFT_COMMIT") from exc
    need(x.stdout.strip()==GRAFT_OWNER_SHA,
         "HOLD_ORIGINAL_GRAFT_OWNER_COMMIT_CHANGED")
    return blob

def synthesize_event(root,source_scene=None):
    """A fixture outside the original closed four-world family, never a sensor.

    Start from the *original* LEFT_FULL PNG and remove exactly two blue cells.
    A 2-high aperture is big enough for a 2x2 red block. Old visuals forbid
    blue loss, so the new state transition is not reducible to old action rules.
    """
    record,worlds=original.verify_original(root)
    image_dir=Path(root)/"worlds"/"LEFT_FULL"
    before=(image_dir/"start.png").read_bytes()
    source=(image_dir/"target.png").read_bytes()
    a=png.decode_png(before)
    b=png.decode_png(source)
    need(len(a)==8 and len(a[0])==9,"HOLD_ORIGINAL_SCENE_DIMENSIONS_CHANGED")
    need(png.coords(a,'#')=={(4,y) for y in range(8)} and
         png.coords(a,'R')=={(1,3),(2,3),(1,4),(2,4)},
         "HOLD_ORIGINAL_FULL_WALL_UNEXPECTED")
    if source_scene is None:
        new=tuple(''.join('.' if (x,y) in OPEN_CELLS else ch
                          for x,ch in enumerate(row))
                  for y,row in enumerate(a))
        after=png.encode_png(new)
    else:
        after=source_scene
        new=png.decode_png(after)
    changed={(x,y) for y,(u,v) in enumerate(zip(a,new))
             for x,(old,latest) in enumerate(zip(u,v)) if old!=latest}
    need(changed==set(OPEN_CELLS) and
         all(a[y][x]=='#' and new[y][x]=='.' for x,y in changed),
         "HOLD_NOT_SUPPORTED_TWO_CELL_EXTERNAL_EVENT")
    need(png.coords(a,'R')==png.coords(new,'R') and
         len(png.coords(new,'#'))==6 and
         len(png.coords(a,'#'))==8,
         "HOLD_SYNTHETIC_EXTERNAL_EVENT_MUST_PRESERVE_RED")
    goal=tuple(''.join('.' if (x,y) in OPEN_CELLS else ch
                       for x,ch in enumerate(row))
               for y,row in enumerate(b))
    goal_bytes=png.encode_png(goal)
    png.question(after,goal_bytes) # new scene is now stationary and movable
    # The observation cannot be explained by any of the FOUR original masks,
    # and GRAFT-030 modes never remove blue. No probability is normalized.
    old_blue_counts={w["id"]:len(png.coords(
       png.decode_png((Path(root)/"worlds"/w["id"]/"start.png").read_bytes()),'#'))
       for w in worlds}
    need(set(old_blue_counts.values())=={4,8} and
        len(png.coords(new,'#')) not in set(old_blue_counts.values()),
        "HOLD_NO_OUT_OF_SUPPORT_GEOMETRY")
    # Existing original image-only parser must reject changed obstacle layers
    # when used as an old-format agent-movement question.
    try:png.question(before,after)
    except png.HOLD:old_representation_rejected=True
    else:old_representation_rejected=False
    need(old_representation_rejected,"HOLD_STATIC_WORLD_FALSELY_ADMITS_EVENT")
    return record,worlds,before,after,goal_bytes,old_blue_counts

def issue_question(question_dir,out,synthetic_after=None):
    only_new(out)
    source,worlds,before,after,goal,counts=synthesize_event(
       question_dir,synthetic_after)
    scene_before=png.decode_png(before)
    scene_after=png.decode_png(after)
    changed=[[x,y] for x,y in OPEN_CELLS]
    body={
       "schema":"motif013.missing-world-question.v0",
       "status":"HOLD_ALL_ORIGINAL_FOUR_WORLDS_OUT_OF_SUPPORT",
       "original_009_question_sha256":source["content_sha256"],
       "original_world_ids":list(WORLD_IDS),
       "original_world_blue_counts":counts,
       "original_source_original_four_worlds_replayed":True,
       "synthetic_observation":True,
       "observation_is_from_actual_sensors":False,
       "before_png_sha256":sha256(before).hexdigest(),
       "outside_png_sha256":sha256(after).hexdigest(),
       "new_model_goal_png_sha256":sha256(goal).hexdigest(),
       "before_rows":list(scene_before),
       "outside_rows":list(scene_after),
       "new_model_goal_rows":list(png.decode_png(goal)),
       "old_constraint":"BLUE_OBSTACLE_COUNT_NONDECREASING_FOR_GRAFT030_MODES",
       "original_png_question_rejects_changed_blue_obstacles":True,
       "old_four_obstacle_counts_exclude_six":True,
       "observed_synthetic_blue_count":6,
       "original_synthetic_blue_count":8,
       "difference_cells":changed,
       "missing_kind":"SYNTHETIC_EXTERNAL_ENVIRONMENT_STATE_UPDATE",
       "automatic_generated_operator_authorized":False,
       "real_world_input_received":False,
       "closed_world_impossibility_not_global_truth":True,
       "authority":{"external_requests":0,"people_contacted":0,
        "real_environment_changed":False,"network_access":False,
        "run_generated_operator_on_real_device":False,
        "deploy":False,"admit_to_main":False}
    }
    body["content_sha256"]=digest(body)
    out=Path(out);out.mkdir(parents=True)
    (out/"missing-question.json").write_text(json.dumps(body,indent=2)+"\n")
    for name,data in (("before.png",before),("outside.png",after),
                       ("new-goal.png",goal)):
        (out/name).write_bytes(data)
    return body

JS_REGENERATE=r"""
import fs from 'node:fs';
import {pathToFileURL} from 'node:url';
import {join} from 'node:path';
import {createHash} from 'node:crypto';
const [graft,root]=process.argv.slice(1);
const g=await import(pathToFileURL(join(graft,'src','world-model-031.mjs')).href);
const q=JSON.parse(fs.readFileSync(join(root,'graft-ticket.json'),'utf8'));
const receipt=JSON.parse(fs.readFileSync(join(root,'graft-receipt.json'),'utf8'));
const proposal=JSON.parse(fs.readFileSync(join(root,'missing-question.json'),'utf8'));
g.verifyTicket(q);
const expected=await g.cultivate(q,g.fixtureSets());
if(JSON.stringify(expected)!==JSON.stringify(receipt))
  throw Error('Generator receipt not reproducible from pinned GRAFT owner');
if(receipt.status!=='HELD_NEW_EXTERNAL_EVENT_MODEL'||
    receipt.chosen?.mode!=='open_observed_pair'||
    receipt.chosen.synthetic_external_event_only!==true||
    receipt.chosen.permission_to_operate_a_physical_gate!==false||
    receipt.chosen.installed!==false)
  throw Error('No bounded held new environmental model');
const emitted=fs.readFileSync(join(root,'generated-environment.mjs'),'utf8');
if(emitted!==receipt.chosen.source||
    createHash('sha256').update(emitted).digest('hex')!==receipt.chosen.source_sha256)
  throw Error('Candidate source bytes differ from pinned original GRAFT');
const loaded=await import('data:text/javascript;base64,'+
  Buffer.from(emitted).toString('base64'));
const result=loaded.execute({
  rows:proposal.before_rows,
  event:'SIMULATED_ENVIRONMENT_GATE_OPEN'
});
const realCommand=loaded.execute({rows:proposal.before_rows,event:'PHYSICAL_GATE_OPEN'});
const again=loaded.execute({rows:proposal.outside_rows,
                            event:'SIMULATED_ENVIRONMENT_GATE_OPEN'});
if(result.status!=='PROPOSED_ENVIRONMENT_FRAME'||
   JSON.stringify(result.frame)!==JSON.stringify(proposal.outside_rows)||
   realCommand.status!=='HOLD_EVENT_NOT_SIMULATED'||
   again.status!=='HOLD_GATE_ANCHOR_NOT_CLOSED')
  throw Error('Generated program fails original external-only effect test');
console.log(JSON.stringify({generated_model_replayed:true,
    program_sha256:receipt.chosen.source_sha256,
    chosen_mode:receipt.chosen.mode,
    predicted_frame:result.frame,
    physical_control_denied:true,
    physical_action_executed:false}));
"""

def assess(question_dir,base_scenes,imagined,build,graft,probe_dir,out):
    only_new(out)
    verify_graft(graft)
    actual=read(Path(probe_dir)/"missing-question.json")
    check=dict(actual);claimed=check.pop("content_sha256",None)
    need(digest(check)==claimed,"HOLD_MISSING_WORLD_CERTIFICATE_CHANGED")
    source,worlds,before,after,goal,counts=synthesize_event(question_dir)
    need(actual.get("schema")=="motif013.missing-world-question.v0" and
         actual.get("status")=="HOLD_ALL_ORIGINAL_FOUR_WORLDS_OUT_OF_SUPPORT" and
         actual.get("original_009_question_sha256")==source["content_sha256"] and
         actual.get("original_world_ids")==list(WORLD_IDS) and
         actual.get("original_world_blue_counts")==counts and
         actual.get("synthetic_observation") is True and
         actual.get("observation_is_from_actual_sensors") is False and
         actual.get("before_png_sha256")==sha256(before).hexdigest() and
         actual.get("outside_png_sha256")==sha256(after).hexdigest() and
         actual.get("new_model_goal_png_sha256")==sha256(goal).hexdigest() and
         actual.get("before_rows")==list(png.decode_png(before)) and
         actual.get("outside_rows")==list(png.decode_png(after)) and
         actual.get("new_model_goal_rows")==list(png.decode_png(goal)) and
         actual.get("difference_cells")==[list(p) for p in OPEN_CELLS] and
         actual.get("missing_kind")=="SYNTHETIC_EXTERNAL_ENVIRONMENT_STATE_UPDATE" and
         actual.get("closed_world_impossibility_not_global_truth") is True and
         actual.get("authority")=={"external_requests":0,"people_contacted":0,
          "real_environment_changed":False,"network_access":False,
          "run_generated_operator_on_real_device":False,
          "deploy":False,"admit_to_main":False},
         "HOLD_ORIGINAL_MISSING_WORLD_CERTIFICATE_INCONSISTENT")
    for name,data in (("before.png",before),("outside.png",after),
                      ("new-goal.png",goal)):
        need((Path(probe_dir)/name).read_bytes()==data,
             "HOLD_SYNTHETIC_PNG_BYTES_NOT_SOURCE_OWNED")
    ticket=read(Path(probe_dir)/"graft-ticket.json")
    receipt=read(Path(probe_dir)/"graft-receipt.json")
    ticket_body=dict(ticket);sha=ticket_body.pop("content_sha256",None)
    need(png.digest(ticket_body)==sha and
         ticket.get("before_rows")==list(png.decode_png(before)) and
         ticket.get("after_rows")==list(png.decode_png(after)) and
         ticket.get("opened_cells")==[list(p) for p in OPEN_CELLS] and
         ticket.get("blue_before")==8 and ticket.get("blue_after")==6 and
         ticket.get("source")=="SYNTHETIC_PAIRED_PNG_CELLS_NOT_PHYSICAL_OBSERVATION",
         "HOLD_GRAFT_PROBLEM_NOT_FROM_IMAGE_PAIR")
    core=dict(receipt);hashval=core.pop("content_sha256",None)
    need(png.digest(core)==hashval,
         "HOLD_GRAFT_CANDIDATE_SELECTION_CHANGED")
    try:
        code=subprocess.run(
         ["node","--input-type=module","--eval",JS_REGENERATE,
          str(Path(graft).resolve()),str(Path(probe_dir).resolve())],
         capture_output=True,text=True,check=True,timeout=30)
        report=json.loads(code.stdout)
    except (OSError,ValueError,subprocess.CalledProcessError,
            subprocess.TimeoutExpired) as exc:
        raise HOLD("HOLD_GENERATED_JS_DOES_NOT_REPLAY_FROM_PINNED_GRAFT") from exc
    need(report.get("generated_model_replayed") is True and
         report.get("physical_control_denied") is True and
         report.get("predicted_frame")==list(png.decode_png(after)),
         "HOLD_GRAFT_GENERATED_MODEL_DID_NOT_MATCH_OBSERVED_SYNTHETIC_FRAME")
    # Reuse actual source-owned original GRAFT-030 compiled move operator
    # to show closure under the old world, and a possible route AFTER the
    # simulated external event, not an unauthorized actor opening the gate.
    context=prior.verified_prior(base_scenes,imagined,build)
    native=context["native"]
    old_goal=(Path(question_dir)/"worlds"/"LEFT_FULL"/"target.png").read_bytes()
    old_reach=prior.prove_reachable(native,png.decode_png(before),
                                   png.decode_png(old_goal))
    new_reach=prior.prove_reachable(native,png.decode_png(after),
                                   png.decode_png(goal))
    need(old_reach["closed"] is True and old_reach["reached"] is False and
         new_reach["closed"] is True and new_reach["reached"] is True and
         len(new_reach["steps"])>0,
         "HOLD_NO_PROVEN_BOUNDED_REACHABILITY_EXPANSION")
    base={
     "schema":"motif013.new-world-held-answer.v0",
     "status":"HOLD_NEW_MODEL_EXPLAINS_SYNTHETIC_OOD_EVENT_NOT_ADMITTED",
     "question_sha256":actual["content_sha256"],
     "source_question_original_009_sha256":source["content_sha256"],
     "graft_owner_commit":GRAFT_OWNER_SHA,
     "graft_owner_git_blob":GRAFT_OWNER_BLOB,
     "original_graft030_visual_source":context["manifest"]["generated_visual_source_sha256"],
     "new_source_generated_sha256":receipt["chosen"]["source_sha256"],
     "new_graft_problem_sha256":ticket["content_sha256"],
     "new_graft_receipt_sha256":receipt["content_sha256"],
     "old_four_possible_worlds":list(WORLD_IDS),
     "old_blue_mass_cannot_decrease":True,
     "old_world_model_contains_new_image":False,
     "synthetic_environment_event_only":True,
     "result_before_model_update":{"reachable":old_reach["reached"],
      "proof_complete":old_reach["closed"],
      "reachable_states":old_reach["states"]},
     "result_after_simulated_environment_event":{
      "reachable":new_reach["reached"],
      "proof_complete":new_reach["closed"],
      "reachable_states":new_reach["states"],
      "hypothetical_steps":new_reach["steps"]},
     "fair_classical_source_model_can_match":True,
     "candidate_family_finite_author_defined":True,
     "heldout_real_world_tests":0,
     "model_auto_admitted":False,
     "current_physical_world_identified":False,
     "source_authority":{"real_sensor_data":False,"external_api_calls":0,
      "physical_events_triggered":0,"people_contacted":0,
      "deployment":False,"new_source_installed":False}
    }
    answer={**base,"content_sha256":png.digest(base)}
    out=Path(out);out.mkdir(parents=True)
    (out/"held-new-model-answer.json").write_text(json.dumps(answer,indent=2)+"\n")
    (out/"new-environment-state.png").write_bytes(after)
    (out/"new-environment-goal.png").write_bytes(goal)
    (out/"thought.md").write_text(
     "# MOTIF-013 — WHAT IF THE CURRENT WORLDS ARE WRONG?\n\n"+
     "The original four source-replayed visual models and stationary-obstacle "+
     "grammar **cannot explain a synthetic time-ordered blue-barrier change**. "+
     "The original blue-pixel count is eight, the next synthetic PNG has six. "+
     "No previous program mode removes blue; this is a finite **closed-model** "+
     "incompatibility certificate, not a universal impossibility theorem.\n\n"+
     "GRAFT-031 generated a distinct executable environmental event model "+
     "from bounded pixel pairs, and held it. Its source passed training, "+
     "selection and negative controls. An unmodified original GRAFT-030 "+
     "movement planner has no route before the simulated event but a route "+
     "after the event.\n\n"+
     "**The environmental opening is not an agent action or real observation.** "+
     "The GRAFT source is not installed, and no live gate is operated. "+
     "The true world remains unknown, including possibilities outside this "+
     "new small candidate family.\n")
    return answer

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--question-dir",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    p.add_argument("--base-scenes",type=Path)
    p.add_argument("--imagined",type=Path)
    p.add_argument("--build",type=Path)
    p.add_argument("--graft",type=Path)
    p.add_argument("--probe",type=Path)
    a=p.parse_args()
    try:
        if a.probe:
            need(all([a.base_scenes,a.imagined,a.build,a.graft]),
                 "HOLD_MISSING_SOURCE_EVIDENCE_ARGUMENTS")
            result=assess(a.question_dir,a.base_scenes,a.imagined,
                          a.build,a.graft,a.probe,a.out)
        else:result=issue_question(a.question_dir,a.out)
        print(json.dumps({"status":result["status"],
          "content_sha256":result["content_sha256"],
          "actual_physical_action":False},indent=2))
    except (HOLD,png.HOLD,original.HOLD,prior.HOLD,KeyError) as exc:
        print(json.dumps({"status":"HOLD","reason":str(exc)}))
        raise SystemExit(1)
if __name__=="__main__":main()
