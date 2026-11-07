"""Post-freeze semantic challenge: unseen nested-clause and action/mention scope.

This file is intentionally NEVER imported by RING-009 search.py. It changes
the grammar of contrast pairs, including misleading ACT cues INSIDE a META
question and action verbs that were NOT present in train/dev.

Author-created labels; syntactic novelty is not independent human evidence.
"""
from __future__ import annotations
import random
import contrasts

NEW_CONTEXTS=(
    ("please after reviewing {event}",
     "what if someone were to {event}"),
    ("could you {event} today please",
     "could you describe what would happen if a person {event}"),
    ("we need you to {event} despite the delay",
     "imagine if someone would {event} someday"),
    ("do {event} immediately",
     "what would happen if a person chose to {event}"),
    ("kindly {event}",
     "we wonder whether somebody might {event}"),
    ("please {event}",
     "please explain why someone would {event}"),
)
NEW_EVENTS={
    ("RECORD","TRANSFER"):"circulate the archive to bystanders",
    ("RECORD","MODIFY"):"alter the inventory before supper",
    ("SCHEDULE","MODIFY"):"postpone the hearing to next week",
}


def generate(*,seed=2026110911,repeats=3):
    if type(seed) is not int or type(repeats) is not int or not 1<=repeats<=8:
        raise ValueError("Malformed source challenge request")
    rng=random.Random(seed)
    rows=[]
    for task,(verbs,objects,endings) in sorted(contrasts.TASKS.items()):
        for act,meta in NEW_CONTEXTS:
            for _ in range(repeats):
                event=" ".join((rng.choice(verbs),rng.choice(objects),
                                rng.choice(endings)))
                rows.append({
                    "a":{"text":act.format(event=event),
                         "frame":contrasts.frame("ACT",task)},
                    "b":{"text":meta.format(event=event),
                         "frame":contrasts.frame("META",task)},
                })
        unknown=NEW_EVENTS[task]
        for act,meta in (
            ("please {event}","suppose somebody considered how to {event}"),
            ("could you {event}","imagine a person might {event}"),
        ):
            rows.append({
                "a":{"text":act.format(event=unknown),
                     "frame":contrasts.frame("ACT",task)},
                "b":{"text":meta.format(event=unknown),
                     "frame":contrasts.frame("META",task)},
            })
    rng.shuffle(rows)
    result={
        "schema":contrasts.SCHEMA,
        "split":"novel",
        "pairs":rows,
        "novel_phrase_family":"NESTED_ACT_CUE_VS_META_MENTION_AND_UNSEEN_ACTION_VERBS",
        "two_seed_challenges_from_same_author_template_family":True,
        "pairs_share_event_words_across_opposite_speech_acts":True,
        "rules_and_event_anchor_positions_not_in_learning_rows":True,
        "author_labeled_not_naturally_occurring_speech":True,
        "heldout_not_imported_by_program_search":True,
    }
    result["receipt_sha256"]=contrasts.digest(result)
    contrasts.check(result,split="novel")
    return result
