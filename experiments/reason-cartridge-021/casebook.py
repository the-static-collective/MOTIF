"""REASON-021 public cases: *how* another corrects the helper's model.

Every person/answer is fictional. The model begins with TWO observable
features (PRIVATE, CHOICE). The synthetic source may disclose another
previously unrepresented distinction, but its answer key, response labels,
new-feature name and target rule never appear in these case inputs.

The contexts are simply preference examples, NOT actual offers or consents.
A subsequent permission-to-discuss question is mandatory before even a
review-only proposed action is eligible.
"""
from __future__ import annotations

SCHEMA="motif.reason.other-teaches-self.case.v1"
VERSION="motif.reason.other-teaches-self.public.v1"
BASE_FEATURES=("PRIVATE","CHOICE")


def c(id,person,revision=1,*,contact=True,questions=10,
      self_pref="YES",target=7,train=False):
    return {"schema":SCHEMA,"case_id":id,"recipient":person,
            "consent_revision":revision,"contact_allowed":contact,
            "allowed_source_questions":questions,
            "self_role_reversal_preference":self_pref,
            "target_context":target,
            "base_features":list(BASE_FEATURES),
            "origin":"SYNTHETIC_FICTIONAL_SOURCE",
            "version":VERSION,"train":train,
            "world_actions_executed":False}


CASES=(
 c("T01","P01",train=True),
 c("T02","P02",train=True),
 c("T03","P03",train=True),
 c("H01","P04"),
 c("H02","P05",self_pref="NO"),
 c("H03","P06"),
 c("H04","P07",contact=False,questions=0),
 c("H05","P_REVISED"),
 c("H06","P_REVISED",revision=2,contact=False,questions=0),
 c("H07","P08",target=1),
 c("H08","P09"),
)

# Eight training interventions: all combinations of the three *source*
# variables. Their public view deliberately excludes the third variable.
# Each hidden-feature pair has identical initially observed attributes.
ORDER=(6,7,2,3,4,5,0,1)


def world(index,split="TRAIN"):
    if split not in ("TRAIN","HELDOUT") or type(index) is not int or not 0<=index<8:
        raise ValueError("Unrecognized source-owned hypothetical context")
    return {
        "schema":"motif.reason.other-teaches-self.world.v1",
        "id":split+"-"+str(index),
        "source_partition":split,
        "initial_features":{
            "PRIVATE":bool(index&4),"CHOICE":bool(index&2),
        },
        # Heldout involves a new irrelevant setting and a different source
        # context, while testing the same eight boolean conditions. This is
        # NOT generalization to unseen language or feature distributions.
        "setting":"PORCH" if split=="TRAIN" else "COMMUNITY_ROOM",
        "source_only_hypothetical":True,
        "real_person_not_observed":True,
    }


def training():
    return tuple(c for c in CASES if c["train"])


def heldout():
    return tuple(c for c in CASES if not c["train"])


def by_id(id):
    return next(c for c in CASES if c["case_id"]==id)
