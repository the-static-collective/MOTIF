"""MOTIF-008: TEXT <-> PICTURES <-> CLOSED-WORLD PROOF.

A first bidirectional critic across source-text constraints, a *modeled* visual
scene, actual GRAFT-generated future PNGs, and finite-state reachability.
Preserves provenance: an assumed picture cannot override a user's explicit
geometric statement. It can supply counterexamples only *under its assumptions*.

Runs the exact source-checked MOTIF-006 compiled visual program (GRAFT-030,
CANNON-095) for every explored transition, with its independent classical
pixel-law check. Does not need T5, neural vision, remote calls or deployments.
"""
from __future__ import annotations
from collections import deque
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import argparse
import json
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"door-foundry-007"))
import text_to_visual as language
import narrate
import visual_in as visual

BASE="A red crate starts left of a blue wall. Move it to the right of the wall."
CLAUSES={
    "": "UNQUALIFIED_REQUEST",
    " Keep the crate on the same row throughout.": "HORIZONTAL_ONLY",
    " The wall makes the destination unreachable.": "ASSERT_NO_PATH",
    " The blue wall stretches from top to bottom.": "FULL_HEIGHT_WALL",
    " Do not move through the blue wall.": "NO_WALL_INTERSECTION",
}
MOVES=((0,-1),(-1,0),(1,0),(0,1))
HORIZONTAL=((1,0),(-1,0))
MAX_STATES=96
class HOLD(ValueError):pass

def doc(path,limit=100000):
    path=Path(path)
    if not path.is_file() or path.stat().st_size>limit:
        raise HOLD("HOLD_MISSING_OR_OVERSIZE_EVIDENCE")
    try:
        value=json.loads(path.read_text())
    except ValueError as exc:
        raise HOLD("HOLD_MALFORMED_RECEIPT") from exc
    if not isinstance(value,dict):raise HOLD("HOLD_RECORD_NOT_OBJECT")
    return value

def claim_kind(text):
    if not isinstance(text,str) or len(text)>300 or not text.startswith(BASE):
        raise HOLD("HOLD_TEXT_NOT_FROM_SUPPORTED_SOURCE_GRAMMAR")
    tail=text[len(BASE):]
    if tail not in CLAUSES:
        raise HOLD("HOLD_UNSUPPORTED_CLAIM_NO_SEMANTIC_GUESSING")
    return CLAUSES[tail]

def _load_verified_native_operator(build):
    root=Path(build).resolve()
    if root.name in ("",".","..") or not (root/"run.py").is_file():
        raise HOLD("HOLD_NO_EXECUTABLE_VISUAL_OPERATOR")
    path=str(root)
    if path not in sys.path:sys.path.insert(0,path)
    # Exact generated source and CANNON-review record are checked by
    # the original unmodified MOTIF-006 compiled operator's own manifest gate.
    spec=spec_from_file_location("motif008_original_visual_runner",root/"run.py")
    if spec is None or spec.loader is None:
        raise HOLD("HOLD_UNREADABLE_GENERATED_RUNNER")
    mod=module_from_spec(spec)
    spec.loader.exec_module(mod)
    try:
        manifest,start,goal=mod.checked_manifest()
    except (ValueError,OSError,KeyError) as exc:
        raise HOLD("HOLD_ORIGINAL_GENERATED_SOURCE_CHANGED") from exc
    if (manifest.get("generated_visual_source_sha256")!=mod.PROGRAM or
        manifest.get("auto_admit") is not False or
        manifest.get("real_actions_authorized") is not False):
        raise HOLD("HOLD_NEW_OPERATOR_PERMISSION_BOUNDARY")
    return mod,manifest,start,goal

def verified_prior(text_scenes, imagined, build):
    scenes=Path(text_scenes)
    images=Path(imagined)
    receipt=doc(scenes/"text-to-picture.json")
    body=dict(receipt);digest=body.pop("content_sha256",None)
    if digest != visual.digest(body):
        raise HOLD("HOLD_TEXT_TO_PICTURE_PROVENANCE_CHANGED")
    if (receipt.get("status")!="UNAMBIGUOUS_GRAMMAR" or
        receipt.get("candidate_count")!=1 or
        receipt.get("grammar")!=language.GRAMMAR or
        receipt.get("compiler")!="DETERMINISTIC_CLASSICAL_RELATIONAL_PARSE" or
        receipt.get("source_text_sha256")!=sha256(BASE.encode()).hexdigest() or
        receipt.get("automatic_t5_invocations")!=0 or
        receipt.get("authority")!={"human_question_answered":True,
          "external_calls":0,"real_world_actions":0,
          "deploy":False,"promote_canon":False}):
        raise HOLD("HOLD_SOURCE_LANGUAGE_EVIDENCE_NOT_SUPPORTED")
    question=receipt["candidate_scenes"][0]
    scene=question["scene"]
    if (scene["start_relation"]!="left" or scene["goal_relation"]!="right" or
        scene["interpretation"]["observed_physical_scene"] is not False or
        scene["canvas"]!=[9,8]):
        raise HOLD("HOLD_SOURCE_SCENE_IS_NOT_DECLARED_SYNTHETIC_MODEL")
    pngdir=scenes/"H01"
    start_raw=(pngdir/"start.png").read_bytes()
    goal_raw=(pngdir/"target.png").read_bytes()
    start=visual.decode_png(start_raw)
    goal=visual.decode_png(goal_raw)
    if (sha256(start_raw).hexdigest()!=question["start_png_sha256"] or
        sha256(goal_raw).hexdigest()!=question["target_png_sha256"]):
        raise HOLD("HOLD_INPUT_IMAGE_CONTENT_CHANGED")
    visual.verify_gap(doc(pngdir/"visual-gap.json"),start_raw,goal_raw)
    program,manifest,from_build,to_build=_load_verified_native_operator(build)
    if (start!=from_build or goal!=to_build or
        manifest["start_png_sha256"]!=sha256(start_raw).hexdigest()):
        raise HOLD("HOLD_VISUAL_PROGRAM_BOUND_TO_DIFFERENT_IMAGES")
    prior=doc(images/"imagination-receipt.json")
    prior_body=dict(prior);proof=prior_body.pop("content_sha256",None)
    if proof!=visual.digest(prior_body) or (
        prior.get("schema")!="motif.visual-imagination-outcome.v0" or
        prior.get("imagined_goal_reached") is not True or
        prior.get("superior_to_classical") is not False or
        prior.get("actual_object_movements")!=0 or
        prior.get("external_network_calls")!=0 or
        prior.get("source_image_sha256")!=sha256(start_raw).hexdigest() or
        prior.get("target_image_sha256")!=sha256(goal_raw).hexdigest()):
        raise HOLD("HOLD_PRIOR_VISUAL_REASONING_UNSUPPORTED")
    paths=sorted((images/"frames").glob("frame-*.png"))
    if not 2<=len(paths)<=20 or len(paths)!=prior["imagined_future_frames"]:
        raise HOLD("HOLD_IMAGINED_FRAME_CUSTODY_INCOMPLETE")
    width,height=scene["canvas"]
    frames=[narrate.shrink_png(p,width,height) for p in paths]
    if frames[0]!=start or frames[-1]!=goal:
        raise HOLD("HOLD_PRIOR_PATH_WRONG_START_OR_GOAL")
    fixed_obstacles=visual.coords(start,"#")
    moves=[]
    for a,b in zip(frames,frames[1:]):
        if visual.coords(a,"#")!=fixed_obstacles or visual.coords(b,"#")!=fixed_obstacles:
            raise HOLD("HOLD_OBSTACLE_MOVED_IN_IMAGINATION")
        pa=narrate.position(a);pb=narrate.position(b)
        delta=(pb[0]-pa[0],pb[1]-pa[1])
        if delta not in MOVES:
            raise HOLD("HOLD_IMAGINED_PICTURES_NOT_CARDINAL_MOTION")
        if len(visual.coords(a,"R"))!=4 or len(visual.coords(b,"R"))!=4:
            raise HOLD("HOLD_VISUAL_OBJECT_NOT_CONSERVED")
        moves.append(delta)
    if ([list(x) for x in moves]!=prior["imagined_moves"] or
        len(moves)!=prior["imagined_actions"] or
        prior["classical_minimum_steps"]!=len(moves)):
        raise HOLD("HOLD_IMAGE_PATH_DISAGREES_WITH_REASONING_RECEIPT")
    return {
        "scene":scene,"start":start,"goal":goal,"frames":frames,
        "moves":moves,"original_receipt":prior,
        "original_image_hash":sha256(start_raw).hexdigest(),
        "original_goal_hash":sha256(goal_raw).hexdigest(),
        "native":program,
        "manifest":manifest
    }

def prove_reachable(native,first,goal,moves=MOVES,limit=MAX_STATES):
    """Complete finite reachable-state closure; no search-depth false negative.

    Every successor is executed by the original source-generated GRAFT JS and
    checked by the independent classical pixel-shift interpreter.
    """
    if len(first)!=len(goal) or len(first[0])!=len(goal[0]):
        raise HOLD("HOLD_UNLIKE_IMAGE_CANVASES")
    if first==goal:return {"reached":True,"closed":True,"states":1,"steps":[]}
    frontier=[first]
    parents={first:None}
    while frontier:
        queries=[(scene,delta) for scene in frontier for delta in moves]
        try:
            predicted=native.native_predict_batch(queries)
        except (ValueError,KeyError,OSError) as exc:
            raise HOLD("HOLD_NATIVE_SOURCE_VISUAL_PREDICTION_FAILED") from exc
        next_frontier=[]
        for (before,delta),(status,new_frame) in zip(queries,predicted):
            if status!="PROPOSED_FRAME":continue
            if new_frame not in parents:
                if len(parents)>=limit:
                    raise HOLD("HOLD_FINITE_CLOSURE_BUDGET_NO_IMPOSSIBILITY_CLAIM")
                parents[new_frame]=(before,delta)
                if new_frame==goal:
                    steps=[]
                    pos=new_frame
                    while parents[pos] is not None:
                        previous,action=parents[pos]
                        steps.append(list(action))
                        pos=previous
                    steps.reverse()
                    return {"reached":True,"closed":True,
                        "states":len(parents),"steps":steps}
                next_frontier.append(new_frame)
        frontier=next_frontier
    return {"reached":False,"closed":True,
            "states":len(parents),"steps":[]}

def render_markdown(text,kind,review,report):
    out=[
      "# MOTIF-008 — TEXT / IMAGE / LOGIC CROSS-EXAMINATION",
      "",
      "**All outcomes below concern a finite simulated model, not reality.**",
      "",
      "## Exact supplied text", "",text,"",
      "## Three witnesses", "",
      "**TEXT:** "+review["text_witness"], "",
      "**IMAGE:** "+review["image_witness"], "",
      "**LOGIC:** "+review["proof_witness"], "",
      "## Ruling: "+report["status"], "",
      "**Reason:** "+report["interpretation"], "",
      "## Assumption ledger", "",
      "The initial wall length, square size and exact coordinates were **chosen",
      "by the text-to-picture renderer**, not observed in the world or stated",
      "in the original sentence. Explicit subsequent user constraints outrank",
      "those synthetic layout assumptions.", "",
      "A generated GRAFT-030 finite pixel operation was the only visual effect",
      "executor; its CANNON-095 source review does not sign off on a real person",
      "or prove any external observation.", "",
      "No T5, external service, human contact, deployment or physical action",
      "was involved. Classical source-native geometry was sufficient.", ""
    ]
    return "\n".join(out)

def interrogate(text,text_scenes,imagined,build,output):
    kind=claim_kind(text)
    output=Path(output)
    if output.exists():raise HOLD("HOLD_NEVER_OVERWRITE_DEBATE_RESULT")
    context=verified_prior(text_scenes,imagined,build)
    source=context["start"];goal=context["goal"]
    program=context["native"]
    baseline_path=context["moves"]
    baseline={"step_count":len(baseline_path),
      "has_vertical":any(step[1]!=0 for step in baseline_path),
      "passed_independent_frame_checks":True}
    checks={"model_custody_checked":True,
       "source_text_sha256":sha256(text.encode()).hexdigest(),
       "original_text_sha256":sha256(BASE.encode()).hexdigest(),
       "GRAFT_visual_executable_source_sha256":context["manifest"]["generated_visual_source_sha256"],
       "original_CANNON_source_review_sha256":context["manifest"]["cannon_review_sha256"],
       "classical_reference_matches_original_plan":True}
    revised=None
    if kind=="HORIZONTAL_ONLY":
        closure=prove_reachable(program,source,goal,HORIZONTAL)
        if closure["reached"] or not baseline["has_vertical"]:
            raise HOLD("HOLD_FAILED_TO_DEMONSTRATE_TEXT_VISUAL_CONFLICT")
        status="TEXT_VETOES_VISUAL_PLAN"
        interpretation=("A visually feasible 11-step detour violates the explicit "
           "'same row' instruction. Exhaustive horizontal-only exploration "
           "finds no path in this chosen synthetic scene. Do not claim success.")
        proof={"horizontal_only_closed":closure["closed"],
          "horizontal_only_reachable":closure["reached"],
          "horizontal_only_states":closure["states"],
          "relaxed_model_path_exists":True,
          "relaxed_path_uses_vertical_motion":True,
          "missing_permission_to_relax_text_constraint":True}
        witness={
          "text_witness":"The user explicitly forbade vertical movement.",
          "image_witness":"The verified imagined PNG sequence includes vertical movement.",
          "proof_witness":("A complete finite reachability closure using only "
            "horizontal generated-program actions excludes the goal.")}
    elif kind=="ASSERT_NO_PATH":
        if len(baseline_path)==0:
            raise HOLD("HOLD_NO_PICTURE_COUNTEREXAMPLE")
        status="IMAGE_COUNTEREXAMPLE_UNDER_ASSUMED_GEOMETRY"
        interpretation=("The proposed synthetic picture has a path around "
           "the wall. Its saved PNG frames refute the added no-path claim "
           "only **for this assumed finite layout**. The real wall's extent "
           "is not established by the original text.")
        proof={"original_model_goal_reachable":True,
          "counterexample_frames_verified":len(context["frames"]),
          "counterexample_steps":len(baseline_path),
          "claim_about_physical_world_disproved":False}
        witness={
          "text_witness":"The added sentence claims the destination is unreachable.",
          "image_witness":("The source-checked PNG sequence reaches the target "
            "without occupying any blue obstacle pixels."),
          "proof_witness":("An explicit valid path is a counterexample to "
            "unreachability, conditional on the chosen geometry.")}
    elif kind=="FULL_HEIGHT_WALL":
        width,height=context["scene"]["canvas"]
        if context["scene"]["topology"]!="VERTICAL_STATIONARY_BARRIER":
            raise HOLD("HOLD_UNSUPPORTED_ORIENTATION")
        vertical_wall=[(4,y) for y in range(height)]
        first=visual.demo_scene(1,3,vertical_wall,width,height)
        last=visual.demo_scene(6,3,vertical_wall,width,height)
        first_png=visual.encode_png(first)
        goal_png=visual.encode_png(last)
        new_gap=visual.question(first_png,goal_png)
        closure=prove_reachable(program,first,last,MOVES)
        if closure["reached"] or not closure["closed"]:
            raise HOLD("HOLD_REVISED_IMAGE_DID_NOT_RESPECT_FULL_HEIGHT_WALL")
        status="TEXT_OVERRIDES_UNGROUNDED_PICTURE_ASSUMPTION"
        interpretation=("The text explicitly says the wall spans the picture's "
          "entire height. The earlier renderer silently assumed a shorter "
          "barrier, which falsely allowed a detour for this added constraint. "
          "A revised PNG picture with a full-height wall is unreachable under "
          "complete finite-state generated-program exploration.")
        proof={"original_renderer_wall_height":len(visual.coords(source,"#")),
          "revised_renderer_wall_height":len(visual.coords(first,"#")),
          "revised_goal_reachable":False,
          "complete_state_closure":True,
          "revised_states_explored":closure["states"],
          "revised_input_is_independently_cannon_reviewed":False}
        revised=(first_png,goal_png,new_gap)
        witness={
          "text_witness":"The added words explicitly specify a top-to-bottom wall.",
          "image_witness":("The originally assumed PNG has a shorter blue wall, "
            "which contradicts this newly supplied textual condition."),
          "proof_witness":("Regenerate a new bounded full-height image model; "
            "the source-generated visual operator proves no route exists.")}
    elif kind=="NO_WALL_INTERSECTION":
        if not all(visual.coords(frame,"R").isdisjoint(
                      visual.coords(frame,"#")) for frame in context["frames"]):
            raise HOLD("HOLD_VISUAL_PATH_CROSSES_BARRIER")
        status="TEXT_IMAGE_LOGIC_AGREE"
        interpretation=("The text forbids occupying wall pixels; every actual "
           "imagined PNG frame preserves that constraint while reaching the "
           "declared target under the synthetic scene assumptions.")
        proof={"all_source_rendered_frames_preserve_wall_separation":True,
          "imagined_goal_reached":True,
          "classical_equal_information_minimum_steps":len(baseline_path)}
        witness={
          "text_witness":"The user forbade passing through the wall.",
          "image_witness":"All verified future PNG frames keep the red pixels outside blue cells.",
          "proof_witness":"The accepted source-generated path respects the text constraint."}
    else:
        status="NO_EXPLICIT_EXTRA_CONSTRAINT"
        interpretation=("The narrow initial text and its source-rendered "
           "hypothetical image are consistent; no added conflict is tested.")
        proof={"goal_reached_in_modeled_scene":True}
        witness={
          "text_witness":"Only the original relational goal was supplied.",
          "image_witness":"The source-checked PNG planner reaches the goal in the chosen layout.",
          "proof_witness":"The saved finite path is valid under the renderer assumptions."}

    body={
      "schema":"motif.three-witness-cross-examination.v0",
      "status":status,"input_clause":kind,
      "input_text_sha256":sha256(text.encode()).hexdigest(),
      "source_text_sha256":sha256(BASE.encode()).hexdigest(),
      "source_model_is_assumed_geometry":True,
      "checked_sources":checks,
      "baseline_visual_path":baseline,
      "proof":proof,"witnesses":witness,
      "interpretation":interpretation,
      "requires_manual_disambiguation_or_model_update":
          kind in ("HORIZONTAL_ONLY","FULL_HEIGHT_WALL"),
      "explicit_text_statement_downgraded_to_model_assumption":False,
      "generated_source_operator_used":True,
      "neural_T5_calls":0,
      "model_picture_is_external_observation":False,
      "real_world_events_observed":0,
      "physical_effects":0,
      "repository_writes":0,
      "external_network_calls":0,
      "automatic_operator_admission":False,
    }
    body["content_sha256"]=visual.digest(body)
    output.mkdir(parents=True)
    if revised:
        a,b,q=revised
        (output/"revised-start.png").write_bytes(a)
        (output/"revised-goal.png").write_bytes(b)
        (output/"revised-visual-gap.json").write_text(json.dumps(q,indent=2)+"\n")
    (output/"judgment.json").write_text(json.dumps(body,indent=2)+"\n")
    (output/"witnesses.md").write_text(render_markdown(text,kind,witness,body))
    return body

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--text",required=True)
    p.add_argument("--text-scenes",type=Path,required=True)
    p.add_argument("--imagined",type=Path,required=True)
    p.add_argument("--build",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    try:
        result=interrogate(args.text,args.text_scenes,args.imagined,args.build,args.out)
        print(json.dumps({"status":result["status"],
           "proof":result["proof"],
           "no_external_actions":result["physical_effects"]==0},indent=2))
    except (HOLD,visual.HOLD,language.HOLD,narrate.HOLD) as exc:
        print(json.dumps({"status":"HOLD","reason":str(exc)}))
        raise SystemExit(1)
if __name__=="__main__":main()
