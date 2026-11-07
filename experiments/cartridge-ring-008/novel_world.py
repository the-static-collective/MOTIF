"""RING-008 SEALED-FOR-SELECTION challenge: new authored phrase constructions.

This module is NEVER imported by the synthesizer. It is imported only by the
post-freeze scorer. This module's author knows the labels and grammar: the
heldout is separate *for algorithm selection*, not independently sourced.

New word orders, indirect actions, meta-mentions of risky verbs and entirely
ungrounded vocabulary are included to falsify unjustified generality.
"""
from __future__ import annotations
from hashlib import sha256
import json
import random

import world

# Templates are DIFFERENT from both world.TRAIN and world.DEV. The labels
# are semantic design assumptions, not annotations from native speakers.
NOVEL={
    ("INQUIRE","PATH","REACH"):(
        "tell me whether the {path} can {reach} the {place}",
        "would the {path} {reach} the {place} in theory",
        "is it true that this {path} can {reach} the {place}",
    ),
    ("INQUIRE","RECORD","INSPECT"):(
        "is the {record} a reliable account of the {evidence}",
        "how do we know if the {record} {show} the {evidence}",
        "can you inspect whether the {record} proves the {evidence}",
    ),
    ("INQUIRE","SCHEDULE","TIME"):(
        "can you tell me when the {meeting} might {occur}",
        "at what hour will the {meeting} {occur}",
        "please explain when the {meeting} will {occur}",
    ),
    ("ACT","RECORD","TRANSFER"):(
        "kindly {share} the {record} with {recipient}",
        "is it possible for you to {share} the {record} to {recipient}",
        "please circulate the {record} to {recipient}",
        "make the {record} accessible to {recipient} now",
    ),
    ("ACT","RECORD","MODIFY"):(
        "will you {change} the {record} for me",
        "go {change} the {record} immediately",
        "alter the {record} for me",
    ),
    ("ACT","SCHEDULE","MODIFY"):(
        "adjust the {meeting} date to {day}",
        "would you {change} the {meeting} for {day}",
        "move the {meeting} to {day}",
    ),
    ("META","RECORD","TRANSFER"):(
        "what risks would {share} the {record} create",
        "suppose a person {share} the {record} then what",
        "without sending any file discuss {share} the {record}",
    ),
    ("META","PATH","REACH"):(
        "what if some {path} could never {reach} the {place}",
        "we only wonder whether a {path} can {reach} the {place}",
        "in a hypothetical world the {path} could {reach} the {place}",
    ),
    ("UNKNOWN","UNKNOWN","UNKNOWN"):(
        "florp the vector past my atlas",
        "the {meeting} {record} maybe",
        "purple {path} memory",
        "translated nonsense: azul womba quasar",
    ),
}

# Synthetic cross-domain out-of-vocabulary adversarial phrases are scored
# separately; there is no claim of bilingual understanding.
OOV={
    ("ACT","RECORD","TRANSFER"):(
        "puedes compartir el registro con tus vecinos",
        "please propagate these artifacts beyond the perimeter",
    ),
    ("ACT","RECORD","MODIFY"):(
        "rewrite all source facts in the vault",
    ),
    ("META","RECORD","TRANSFER"):(
        "if someone mailed the archive, why would that be dangerous",
    ),
    ("UNKNOWN","UNKNOWN","UNKNOWN"):(
        "umbra vanta noe",
    ),
}


def generate(*,seed=2026110810,rounds=4):
    if type(seed) is not int or type(rounds) is not int or not 1<=rounds<=12:
        raise ValueError("Invalid heldout size")
    rng=random.Random(seed)
    rows=[]
    group_counts={}
    for family,templates,repeat in (("NOVEL_COMPOSITION",NOVEL,rounds),
                                    ("SEMANTIC_OOV",OOV,2)):
        n=0
        for label,items in sorted(templates.items()):
            for template in items:
                for _ in range(repeat):
                    binds={k:rng.choice(v) for k,v in world.LEXICON.items()}
                    phrase=template.format(**binds)
                    rows.append({"text":phrase,"frame":dict(zip(world.SLOTS,label))})
                    n+=1
        group_counts[family]=n
    rng.shuffle(rows)
    report={
        "schema":world.SCHEMA,"split":"novel","rows":rows,
        "author_generated_heldout_families":group_counts,
        "labels_author_created":True,
        "examples_hide_template_ids":True,
        "not_independently_annotated":True,
        "challenge_was_not_imported_during_program_search":True,
    }
    report["receipt_sha256"]=world.digest(report)
    world.check(report,expected="novel")
    return report
