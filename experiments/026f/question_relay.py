"""026F: route held semantic hints through original 022F question review.
SidecarRun is a STRUCTURAL ADAPTER, not an executed 021F text worker.
All world states and observations are synthetic. No field authorization.
"""
from __future__ import annotations
from dataclasses import asdict, replace
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
for name in ("016","021f","022f","025f","026f"):
    p=str(ROOT/name)
    if p not in sys.path:sys.path.append(p)
from chorus import SidecarNote,SidecarRun
from feedback import QuestionLedger,submit_critic_question
from forest import LivingForest
from sealed_oracle import modeled_problem,SealedSyntheticOracle
from semantic_router import route_semantic_hint,operator_projection

GATE_TESTS={"FOOD":"FOOD_SERVICE_GATE","AUDIO":"REPEAT_AUDIO_TEST"}

def review_semantic_question(text,classifier=None,*,hidden_world="10"):
    hint=route_semantic_hint(text,classifier)
    worlds,base_roads,catalog=modeled_problem()
    baseline=LivingForest(worlds,base_roads,budget=.65,rounds=1,max_parallel=2).plan()
    output={
        "schema":"motif026f.native-semantic-question/v0",
        "hint":asdict(hint),"original_native_plan":asdict(baseline),
        "test_id":None,"status":hint.status,
        "new_sandbox_plan":None,"independent_synthetic_run":None,
        "bridge_kind":"TRUSTED_STRUCTURE_NOT_REAL_CHORUS_WORKER",
        "external_actions":0,"field_facts_changed":False,
        "human_permissions_inferred":False,
        "primary_native_plan_overwritten":False,
    }
    if hint.status not in ("UNVERIFIED_SEMANTIC_QUESTION","NATIVE_REVIEW_QUESTION"):
        return output
    if hint.possible_gate not in GATE_TESTS:
        output["status"]="HOLD_NO_REGISTERED_TEST_FOR_GATE"
        return output
    name=GATE_TESTS[hint.possible_gate]
    output["test_id"]=name
    projection=operator_projection(text)
    # Structured suggestion is NOT model-generated evidence or authority.
    adapter=SidecarRun(
        native=baseline,
        notes=(SidecarNote(
            role="CRITIC",status="UNVERIFIED_TEXT_AVAILABLE",
            text="TEST_ID="+name,backend="026F_TYPED_SEMANTIC_ADAPTER",
            snapshot_sha256=projection.digest()),),
        sidecar_completed=True,native_completed=True,native_wall_ms=0.,
        end_to_end_wall_ms=0.,sidecar_budget_ms=0.,
        mode="SYNTHETIC_STRUCTURE_WRAPPER",
    )
    reviews={t.road.name:SealedSyntheticOracle.calibration(t) for t in catalog}
    proposal=submit_critic_question(
        adapter,projection,worlds,base_roads,catalog,reviews,
        QuestionLedger(),budget=.65,
    )
    output["status"]=proposal.status
    output["new_sandbox_plan"]=asdict(proposal.challenged_plan) if proposal.challenged_plan else None
    if proposal.status!="ELIGIBLE_SYNTHETIC_REPLAN_ONLY":
        return output
    road=next(t.road for t in catalog if t.road.name==name)
    planner=LivingForest(worlds,(*base_roads,replace(road,allowed=True)),
                         budget=.65,rounds=1,max_parallel=2)
    witness=SealedSyntheticOracle(hidden_world)
    before,_=planner.run_synthetic_round(witness.execute)
    answer=planner.plan().tentative_answer
    truth=next(w.answer for w in worlds if w.name==hidden_world)
    output["independent_synthetic_run"]={
        "chosen_questions":before.selected,"observations":witness.executed,
        "answer":answer,"synthetic_truth":truth,"correct":answer==truth,
        "authenticated_real_world":False,
    }
    return output
