"""A hypothetical fourth representation: ordered, quantified, multi-party duties.

The independent bAbI dataset measures quantities, ordered locations and
three-argument transfer, but does NOT test ethical promises or duties. This
additional source-author FICTIONAL counterexample explicitly distinguishes:
- timing ("before the prior deadline"),
- bounded resources (units available),
- a previously incurred third-party obligation (directed duty),
- a person's refusal/consent (NOT derivable from any source story).

This model is a hand-authored typed constraint checker, not discovered law,
verified ethics or an automatic capability to fulfill promises in the world.
"""
from __future__ import annotations
from hashlib import sha256
import json


def fixture(id,capacity,due_hour,amount,prior,contact=True,scope=True,\n            current_hour=12,max_units_per_hour=2):
    return {
        "id":id,"schema":"motif.reason022.typed-duty.v1",
        "source_is_synthetic":True,
        "person":"OTHER_RECIPIENT_"+id,
        "capacity_units":capacity,
        "new_help_units":amount,"new_help_due_hour":due_hour,\n        "current_hour":current_hour,"max_units_per_hour":max_units_per_hour,
        "prior_duties":prior,
        "contact_allowed":contact,"options_discussion_allowed":scope,
        "real_world_permission":False,
    }


# Units and clock times have different types. A promise to someone else is
# a directed relationship, not a Boolean "there is a duty" marker.
CASES=(
    fixture("D01_CAPACITY_AVAILABLE",5,18,2,[
        {"owed_to":"EARLIER_NEIGHBOR","units":2,"due_hour":17}]),
    fixture("D02_PRIOR_PROMISE",4,15,3,[
        {"owed_to":"EARLIER_NEIGHBOR","units":3,"due_hour":16}]),
    fixture("D03_NO_SCOPE",6,18,2,[
        {"owed_to":"EARLIER_NEIGHBOR","units":1,"due_hour":15}],scope=False),
    fixture("D04_NO_CONTACT",6,18,2,[],contact=False),
    fixture("D05_TOO_EARLY",5,12,1,[
        {"owed_to":"EARLIER_NEIGHBOR","units":4,"due_hour":16}]),
    fixture("D06_MULTIPLE_OTHERS",9,20,3,[
        {"owed_to":"OLDER_PROMISE_A","units":3,"due_hour":12},
        {"owed_to":"OLDER_PROMISE_B","units":2,"due_hour":19}]),
    fixture("D07_THIRD_PARTY_CONSTRAINT",6,20,3,[
        {"owed_to":"OLDER_PROMISE_A","units":4,"due_hour":18},
        {"owed_to":"OLDER_PROMISE_B","units":1,"due_hour":19}]),
)


def source_proof(source):
    if (not isinstance(source,dict) or set(source)!={
        "id","schema","source_is_synthetic","person","capacity_units",
        "new_help_units","new_help_due_hour","prior_duties",\n        "current_hour","max_units_per_hour",
        "contact_allowed","options_discussion_allowed","real_world_permission"}
        or source["schema"]!="motif.reason022.typed-duty.v1"
        or source["source_is_synthetic"] is not True
        or source["real_world_permission"] is not False
        or source not in CASES):
        raise ValueError("Untrusted or changed synthetic directed-duty evidence")
    if not source["contact_allowed"]:
        state="HOLD_NO_CONTACT";reason="SOURCE_REFUSES_CONTACT"
    elif not source["options_discussion_allowed"]:
        state="HOLD_NO_SCOPED_PERMISSION";reason="PREFERENCE_NOT_BLANKET_AUTHORITY"
    else:
        prior_units=sum(d["units"] for d in source["prior_duties"])
        remaining=source["capacity_units"]-prior_units
        # This toy constraint deliberately makes no assumptions about
        # replenishment, divisible scheduling, labor fungibility, etc.
        if source["new_help_units"]>remaining:
            state="HOLD_PRIOR_DUTIES";reason="DIRECTED_COMMITMENTS_EXCEED_FIXED_CAPACITY"
        else:
            state="SUGGEST_DISCUSSION_ONLY";reason="FIXTURE_CONSTRAINTS_SATISFIED"
    body={
        "schema":"motif.reason022.typed-duty-proof.v1",
        "source_case_id":source["id"],
        "recipient":source["person"],
        "state":state,"reason":reason,
        "prior_directed_duty_units":sum(x["units"] for x in source["prior_duties"]),
        "capacity_units":source["capacity_units"],
        "requested_units":source["new_help_units"],
        "relevant_deadlines":[{
            "owed_to":d["owed_to"],"hour":d["due_hour"]} for d in source["prior_duties"]],
        "new_request_deadline":source["new_help_due_hour"],\n        "current_hour":source["current_hour"],\n        "production_capacity_per_hour":source["max_units_per_hour"],
        "synthetic_source_fixed_budget_not_dynamic_scheduling":True,
        "source_consent_not_inferred_from_a_model":True,
        "permission_to_execute":False,
    }
    return body


def old_binary_projection(s):
    return {
        "can_assist":s["capacity_units"]>0,
        "already_owes_someone":bool(s["prior_duties"]),
        "wants_options_discussion":s["options_discussion_allowed"],
        "contact_allowed":s["contact_allowed"],
    }


def contradiction():
    # D01 and D02 have the SAME impoverished Boolean projection:
    # available capacity and prior duty both exist; scoped permission YES.
    a=CASES[0];b=CASES[1]
    if old_binary_projection(a)!=old_binary_projection(b):
        raise AssertionError("Old Boolean model unexpectedly grew more expressive")
    ra=source_proof(a);rb=source_proof(b)
    if ra["state"]==rb["state"]:
        raise AssertionError("Old model has no source-backed contrary answers")
    return {
        "old_boolean_view":old_binary_projection(a),
        "case_a":a["id"],"case_b":b["id"],
        "case_a_result":ra["state"],"case_b_result":rb["state"],
        "missing_feature_types":[
            "QUANTITY_UNITS","DIRECTED_THIRD_PARTY_DUTY","DEADLINE_ORDERING"],
        "real_person_not_involved":True,
    }


def all_proofs():
    return [source_proof(c) for c in CASES]
