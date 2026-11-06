"""REASON-017 reproducible experiment: a new wish was outside the model.

No actual person was queried or assisted. Developer-authored scripted replies,
bounded parser, and source-owner answer keys are synthetic. Metrics evaluate
source-controlled dialogue mechanics, not understanding of love or empathy.
"""
from __future__ import annotations
from pathlib import Path
import json

from casebook import CASES,training,heldout,by_id
from source_owner_private import EXPECTED
from owner import SyntheticPerson
from engine import HOLD,RevisionMemory,export,extract_goal,run
from reviewer import validate,Receiver
from bridge016 import closed_vocabulary_control


def run_trial(output=None):
    rows=[]
    for s in CASES:
        person=SyntheticPerson(s["case_id"])
        raw=export(s,person.answer)
        receipt=validate(raw)
        desired=EXPECTED[s["case_id"]]
        actual=(receipt["result"],receipt["current_reported_phrase"])
        if actual!=desired:raise AssertionError("Synthetic owner expected outcome mismatch: "+s["case_id"])
        if len(person.history)!=receipt["source_reply_count"]:
            raise AssertionError("Undocumented question to a simulated recipient")
        rows.append({
            "id":s["case_id"],"evaluation":not s["training"],
            "publicly_known_options":s["offered_options"],
            "current_result":receipt["result"],
            "source_expected_result":desired[0],
            "matches_source_author":actual==desired,
            "question_count":receipt["source_reply_count"],
            "new_hypothesis_versions":receipt["new_hypothesis_versions"],
            "old_hypotheses_rejected":receipt["rejected_prior_hypotheses"],
            "newly_reported_goal":receipt["current_reported_phrase"],
            "consent_scoped_to_options_discussion_only":
                receipt["source_scope_permission_for_options_only"],
            "real_world_action_executed":False,
        })
        if output:
            path=Path(output);path.mkdir(parents=True,exist_ok=True)
            (path/(s["case_id"].lower()+".json")).write_text(raw,encoding="utf8")
    peer=Receiver()
    holdout_receipt=peer.preview(heldout())
    if holdout_receipt["errors"]:raise AssertionError("Unseen synthetic source review failed")
    peer.admit("ADMIT_READ_ONLY",holdout_receipt["review_digest"])
    for s in heldout():
        if peer.suggest(s)["result"]!=EXPECTED[s["case_id"]][0]:
            raise AssertionError("Independent source-owner decision changed")
    before=by_id("H05_PRIOR_CONSENT")
    after=by_id("H06_REVOKED")
    cache=RevisionMemory()
    cache.admit(export(before,SyntheticPerson(before["case_id"]).answer),validate)
    initial=cache.recall(before)["result"]
    cache.admit(export(after,SyntheticPerson(after["case_id"]).answer),validate)
    revoked=cache.recall(after)["result"]
    old_replay_refused=False
    try:cache.recall(before)
    except HOLD:old_replay_refused=True
    if (not old_replay_refused or initial!="SUGGEST_OPTIONS_DISCUSSION_ONLY"
            or revoked!="HOLD_NO_CONTACT_AUTHORITY"):
        raise AssertionError("Revoked recipient permission replayed incorrectly")
    original_closed=closed_vocabulary_control()
    reports={
        "schema":"motif.reason.unexpected-other.benchmark-v1",
        "case_count":len(CASES),
        "development_cases":len(training()),
        "unseen_synthetic_cases":len(heldout()),
        "source_owned_expected_matches":sum(x["matches_source_author"] for x in rows),
        "question_count":sum(x["question_count"] for x in rows),
        "novel_hypotheses_created":sum(len(x["new_hypothesis_versions"]) for x in rows),
        "two_step_human_author_correction":next(
            r for r in rows if r["id"]=="H02_CORRECTION"),
        "read_only_options_suggestions":sum(
            x["current_result"]=="SUGGEST_OPTIONS_DISCUSSION_ONLY" for x in rows),
        "always_hold_source_reference_matches":sum(
            x["current_result"].startswith("HOLD_") for x in rows),
        "no_contact_cases_rejected":sum(
            x["current_result"]=="HOLD_NO_CONTACT_AUTHORITY" for x in rows),
        "older_consent_recall_refused_after_new_revision":old_replay_refused,
        "original_reason016_closed_grammar_control":original_closed,
        "heldout_independent_review":holdout_receipt,
        "individual_proposals":rows,
        "source_owner_answers_are_synthetic_not_people":True,
        "no_empathy_or_human_mental_state_inferred":True,
        "not_general_natural_language_semantic_parsing":True,
        "literal_words_are_not_source_authenticated_human_consent":True,
        "no_actuation_or_external_network":True,
        "strong_classical_rules_can_replicate_result":True,
        "no_measured_love_or_human_welfare":True,
        "external_actions":False,"real_world_authority":False,
    }
    if output:
        path=Path(output)
        (path/"benchmark.json").write_text(
            json.dumps(reports,indent=2,sort_keys=True,ensure_ascii=False)+"\n",
            encoding="utf8")
        (path/"heldout-review.json").write_text(
            json.dumps(holdout_receipt,indent=2,sort_keys=True,ensure_ascii=False)+"\n",
            encoding="utf8")
    return reports


if __name__=="__main__":
    import sys
    if len(sys.argv)>2:raise SystemExit("usage: python trial.py [evidence-directory]")
    r=run_trial(sys.argv[1] if len(sys.argv)==2 else None)
    print(json.dumps({
        "cases":r["case_count"],
        "heldout":r["unseen_synthetic_cases"],
        "author_expected_matches":r["source_owned_expected_matches"],
        "novel_goal_versions":r["novel_hypotheses_created"],
        "questions":r["question_count"],
        "suggestions":r["read_only_options_suggestions"],
        "always_hold_matches":r["always_hold_source_reference_matches"],
        "two_step_repair":r["two_step_human_author_correction"]["new_hypothesis_versions"],
        "original_reason016_closed_grammar":r["original_reason016_closed_grammar_control"]["previous_reader_result"],
        "revoked_permission_blocked":r["older_consent_recall_refused_after_new_revision"],
    },indent=2,sort_keys=True,ensure_ascii=False))
