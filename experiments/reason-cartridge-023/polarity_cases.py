"""Synthetic signed testimony; deliberately NOT the independent bAbI corpus.

Two plausible distinct answers to a transfer query are *ambiguity*, not the
four-valued BOTH. BOTH means there is an explicit YES and an explicit NO
about the exact SAME scoped proposition. Different speakers/revisions are
not silently collapsed. These source assertions are fictional.
"""
from __future__ import annotations

SCHEMA="motif.reason023.signed-casebook.v1"
CASES=(
 {"id":"AFFIRMED","subject":"RECIPIENT_A","epoch":"R1",
  "predicate":"WELCOME_QUIET_HELP","claims":[
   ("S1","YES","The fictional recipient says quiet help is welcome.")]},
 {"id":"DENIED","subject":"RECIPIENT_B","epoch":"R1",
  "predicate":"WELCOME_QUIET_HELP","claims":[
   ("S2","NO","The fictional recipient says quiet help is not welcome.")]},
 {"id":"BOTH","subject":"RECIPIENT_C","epoch":"R1",
  "predicate":"WELCOME_QUIET_HELP","claims":[
   ("S3","YES","The fictional recipient says quiet help is welcome."),
   ("S4","NO","The same fictional recipient says it is not welcome.")]},
 {"id":"MISSING","subject":"RECIPIENT_D","epoch":"R1",
  "predicate":"WELCOME_QUIET_HELP","claims":[]},
 {"id":"DIFFERENT_SPEAKER","subject":"RECIPIENT_E","epoch":"R1",
  "predicate":"WELCOME_QUIET_HELP","claims":[
   ("S5","YES","Recipient E says the proposal is welcome."),
   ("S6","NO","Recipient F says the proposal is not welcome.")],
  "external_subject_for_claim":{"S6":"RECIPIENT_F"}},
 {"id":"CHANGED_REVISION","subject":"RECIPIENT_G","epoch":"R2",
  "predicate":"WELCOME_QUIET_HELP","claims":[
   ("S7","YES","Recipient G earlier allowed discussion."),
   ("S8","NO","Recipient G now withdraws permission.")],
  "external_epoch_for_claim":{"S7":"R1"}},
)


def case(id):
    return next(row for row in CASES if row["id"]==id)
