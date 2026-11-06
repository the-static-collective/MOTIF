"""THOUGHT-009: bounded, evidence-first selection of zero, one or many thought views.

Classical deterministic metareasoning: not a learned policy, natural-language
understanding, new facts, or an action-granting system. Geometry is display only.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
from pathlib import Path
import sys
SIBLING = str(Path(__file__).resolve().parent.parent / "thought-008")
if SIBLING not in sys.path: sys.path.append(SIBLING)
from multiview import ThoughtViews, ViewError, digest

GOALS = ("association", "dependency", "tension", "affordance", "inventory")
PHASES = ("ABSTRACT_PENCIL", "CONCRETE_PENCIL", "PEN_REVIEW")
LENS_FOR_GOAL = {"association":"association", "dependency":"dependency",
                 "tension":"tension", "affordance":"affordance", "inventory":"NONE"}


@dataclass(frozen=True)
class Task:
    """A caller-defined, typed question; not model-inferred semantics."""
    goals: tuple[str, ...]
    anchor: Optional[str] = None
    max_views: int = 2
    show_geometry: bool = True
    phase: str = "ABSTRACT_PENCIL"
    seed: int = 0

    def __post_init__(self):
        if not isinstance(self.goals, tuple) or not self.goals or len(self.goals)>len(GOALS):
            raise ViewError("one to five explicit task goals required")
        if len(set(self.goals))!=len(self.goals) or any(x not in GOALS for x in self.goals):
            raise ViewError("unknown or repeated task goals")
        if type(self.max_views) is not int or not 0<=self.max_views<=5:
            raise ViewError("view budget must be an integer 0 to 5")
        if type(self.show_geometry) is not bool:
            raise ViewError("show_geometry must be boolean")
        if self.phase not in PHASES:
            raise ViewError("unknown thought phase")
        if type(self.seed) is not int or not -100000<=self.seed<=100000:
            raise ViewError("seed outside bounded range")
        if self.anchor is not None and (not isinstance(self.anchor,str) or not self.anchor):
            raise ViewError("anchor must be a known manifestation ID")


class ViewRouter:
    def __init__(self, engine: ThoughtViews):
        if not isinstance(engine, ThoughtViews):
            raise ViewError("requires a THOUGHT-008 evidence engine")
        self.engine=engine

    @staticmethod
    def _signal(goal, index):
        """How many task-relevant authored witnesses/questions exist?

        These are not confidence weights or coordinate-derived evidence.
        A signal only says *there may be something useful to display*.
        """
        if goal=="association": return len(index["bridge_questions"])
        if goal=="dependency": return len(index["dependency"]["required_edges"])
        if goal=="tension": return len(index["tension"])
        if goal=="affordance": return len(index["affordance"]["conditional_reach"])
        return 0

    @staticmethod
    def _questions(index, goals):
        """Finite evidence-grounded prompts. Same prompts for NONE baseline."""
        result=[]
        if "association" in goals:
            for r in index["bridge_questions"][:8]:
                result.append({"kind":"test_association", "endpoints":[r["source"],r["target"]],
                    "premises":list(r["via"]),"status":"QUESTION_ONLY",
                    "question":"Is there independent evidence for this proposed association?"})
        if "dependency" in goals:
            for c in index["dependency"]["cycles"][:4]:
                result.append({"kind":"check_dependency_cycle", "members":list(c),
                    "status":"QUESTION_ONLY","question":"Can the declared prerequisite cycle be resolved?"})
        if "tension" in goals:
            for c in index["tension"][:8]:
                result.append({"kind":"resolve_contradiction", "relation_id":c["relation_id"],
                    "endpoints":list(c["between"]),"status":"QUESTION_ONLY",
                    "question":"Which conflicting claim, if either, has adequate evidence?"})
        if "affordance" in goals:
            for reach in index["affordance"]["conditional_reach"][:8]:
                if reach["other_declared_requirements"]:
                    result.append({"kind":"check_missing_requirements",
                        "target":reach["manifestation_id"],
                        "requires":list(reach["other_declared_requirements"]),
                        "status":"QUESTION_ONLY",
                        "question":"Are the additional declared prerequisites satisfied?"})
        return result[:20]

    def run(self, task: Task, *, previous=None, avoid_lenses=()) -> dict:
        """Route by typed task and authored evidence before allocating any geometry.

        A prior result is a trace for a *new* phase; never silently reused as
        ground truth when input changes. All analysis can run with 0 views.
        """
        if not isinstance(task, Task):
            raise ViewError("typed Task required")
        if task.anchor is not None and task.anchor not in self.engine.manifests:
            raise ViewError("unknown anchor")
        if previous is not None:
            if not isinstance(previous, dict) or previous.get("schema")!="motif.thought-router.v1":
                raise ViewError("incompatible previous thought-cycle receipt")
            if previous.get("effective_external_authority")!="NONE":
                raise ViewError("previous authority cannot be trusted")
        if (not isinstance(avoid_lenses, (tuple, list)) or
                len(avoid_lenses) != len(set(avoid_lenses)) or
                any(x not in LENS_FOR_GOAL.values() for x in avoid_lenses)):
            raise ViewError("invalid excluded lens list")
        index=self.engine.evidence_index(task.anchor)
        offers=[]
        for order,goal in enumerate(task.goals):
            signal=self._signal(goal,index)
            offers.append({"goal":goal,"lens":LENS_FOR_GOAL[goal],"signal_count":signal,
                "source_only_available":True,"priority":order,
                "source_rule":"typed authored evidence only; no geometry-derived facts"})
        candidates=sorted((x for x in offers if x["lens"]!="NONE" and x["signal_count"]>0),
                          key=lambda x:(-min(4,x["signal_count"]),x["priority"],x["lens"]))
        candidates=[c for c in candidates if c["lens"] not in avoid_lenses]
        chosen={x["lens"] for x in candidates[:task.max_views]} if task.show_geometry else set()
        # Pen review means reviewing source-grounded conclusions, not a right to commit.
        if task.phase=="PEN_REVIEW":
            chosen=set()
        decisions=[]
        for offer in offers:
            if offer["lens"]=="NONE": outcome="NON_GEOMETRIC_GOAL"
            elif not task.show_geometry: outcome="OPERATOR_DISABLED"
            elif task.phase=="PEN_REVIEW": outcome="REVIEW_WITHOUT_GEOMETRY"
            elif task.max_views==0: outcome="BUDGET_ZERO"
            elif offer["lens"] in avoid_lenses: outcome="REVIEW_DECLARED_UNHELPFUL"
            elif offer["signal_count"]==0: outcome="NO_WITNESSED_SIGNAL"
            elif offer["lens"] in chosen: outcome="SELECTED"
            else: outcome="BUDGET_DEFERRED"
            decisions.append({**offer,"decision":outcome})
        # Order is deterministic by task priority, and projected only AFTER evidence routing.
        selected=[x["lens"] for x in offers if x["lens"] in chosen]
        views=[self.engine.project(l,anchor=task.anchor,seed=task.seed) for l in selected]
        if any(v["source_evidence_digest"]!=self.engine.input_digest or
               v["relations"]!=self.engine.relations or
               v["external_authority"]!="NONE" for v in views):
            raise ViewError("projection mutated source evidence")
        qs=self._questions(index,task.goals)
        changed=bool(previous and previous.get("source_evidence_digest")!=self.engine.input_digest)
        return {
            "schema":"motif.thought-router.v1", "mode":"RULE_BASED_SELECTION",
            "phase":task.phase,"task":{"goals":list(task.goals),"anchor":task.anchor,
                        "max_views":task.max_views,"show_geometry":task.show_geometry,"seed":task.seed},
            "source_evidence_digest":self.engine.input_digest,
            "source_snapshot_digest":self.engine.source_snapshot_digest,
            "source_only_answers":{g:self._answer(g,index) for g in task.goals},
            "questions":qs,"decisions":decisions,"selected_lenses":selected,
            "views":views,"view_cost_units":len(views),
            "excluded_after_review":list(avoid_lenses),
            "no_geometry_answer_parity":True,
            "prior_cycle_source_changed":changed,
            "prior_cycle_digest":previous.get("receipt_digest") if previous else None,
            "prior_cycle_needs_revalidation":changed,
            "conclusions":"NONE_ADMITTED", "pen_state":"UNCHANGED",
            "effective_external_authority":"NONE",
            "receipt_digest":digest({"source":self.engine.input_digest,
                                     "task":list(task.goals),"phase":task.phase,
                                     "selected":selected,"questions":qs,
                                     "excluded":list(avoid_lenses)}),
            "limitation":"Rule-based visual selection; questions come from the same classical source-only baseline, not positions or new evidence",
        }

    def reconsider(self, task: Task, previous: dict, *, unhelpful_lenses, reason: str) -> dict:
        """Explicit critique can replace an unhelpful representation, never its evidence.

        This is an operator/validator feedback hook, not self-trained evaluation.
        A new underlying source requires a fresh run, not reuse of old feedback.
        """
        if (not isinstance(previous,dict) or
                previous.get("schema") != "motif.thought-router.v1" or
                previous.get("source_evidence_digest") != self.engine.input_digest):
            raise ViewError("changed/incompatible source: feedback needs fresh review")
        if not isinstance(task,Task) or previous.get("task",{}).get("goals") != list(task.goals) or \
                previous.get("task",{}).get("anchor") != task.anchor:
            raise ViewError("feedback task must match prior goal and anchor")
        if not isinstance(reason,str) or not reason.strip() or len(reason)>300:
            raise ViewError("bounded review reason required")
        if (not isinstance(unhelpful_lenses,(list,tuple)) or not unhelpful_lenses or
                len(unhelpful_lenses)!=len(set(unhelpful_lenses)) or
                not set(unhelpful_lenses).issubset(set(previous["selected_lenses"]))):
            raise ViewError("only previously selected lenses may be marked unhelpful")
        exclusions=tuple(dict.fromkeys([*previous.get("excluded_after_review",[]),
                                         *unhelpful_lenses]))
        result=self.run(task,previous=previous,avoid_lenses=exclusions)
        result["feedback"]={"kind":"OPERATOR_OR_VALIDATOR_DECLARED_UNHELPFUL",
            "lenses":list(unhelpful_lenses),"reason":reason,
            "previous_receipt_digest":previous["receipt_digest"],
            "interpretation":"subjective feedback; does not certify source facts"}
        result["receipt_digest"]=digest({"base_receipt":result["receipt_digest"],
                                         "feedback":result["feedback"]})
        return result

    def _answer(self,goal,index):
        if goal=="association": return index["bridge_questions"]
        if goal=="dependency": return index["dependency"]
        if goal=="tension": return index["tension"]
        if goal=="affordance": return index["affordance"]
        return {"status":"SOURCE_ONLY_INVENTORY",
                "concepts":len(self.engine.concepts),
                "manifestations":len(self.engine.manifests),
                "relations":len(self.engine.relations),
                "external_authority":"NONE"}
