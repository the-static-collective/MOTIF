"""RING-011 additional author-created challenge, NOT used in source induction.

This grammar was added only after the first two synthetic populations exposed
a polarity-vs-context bug. The algorithm gained an event-local learned
polarity-insertion rule and a developer review guard. This third family is
fresh relative to that repaired algorithm but NOT independently human-written.

All sentences below are new synthetic text; no Google Drive book passages
or private participant details were imported into source control.
"""
from __future__ import annotations
import random
import corpus

LEX={
    "speaker":("veto","alla","kiri","enzo"),
    "agent":("yuma","orio","zena","mari"),
    "verb":("engrave","latch","weave","paint"),
    "patient":("cabin","bucket","ribbon","mural"),
}
THIRD={
    "unmarked_quotation":(
        ("{speaker} asks {agent} to {verb} {patient}","DIRECTIVE","ROOT","POS"),
        ("{speaker} repeats what {agent} said please {verb} {patient}","MENTION","QUOTED","POS"),
        ("{speaker} quotes {agent} saying please do not {verb} {patient}","MENTION","QUOTED","NEG"),
    ),
    "scope_of_double_negative":(
        ("{speaker} says {agent} did {verb} {patient}","ASSERTION","ROOT","POS"),
        ("{speaker} says {agent} did not {verb} {patient}","ASSERTION","ROOT","NEG"),
        ("{speaker} says {agent} did not fail to {verb} {patient}","ASSERTION","ROOT","POS"),
    ),
    "aside_is_not_negation":(
        ("{speaker} asks {agent} to {verb} {patient}","DIRECTIVE","ROOT","POS"),
        ("{speaker} (not the narrator) asks {agent} to {verb} {patient}","DIRECTIVE","ROOT","POS"),
        ("{speaker} says {agent} did not {verb} {patient}","ASSERTION","ROOT","NEG"),
    ),
    "new_condition_word":(
        ("{speaker} asks {agent} to {verb} {patient}","DIRECTIVE","ROOT","POS"),
        ("{speaker} asks {agent} to {verb} {patient} unless the gate shuts","DIRECTIVE","CONDITIONAL","POS"),
        ("{speaker} supposes [{agent} might {verb} {patient}]","MENTION","IMAGINED","POS"),
    ),
    "new_voice_owner":(
        ("{speaker} asks {agent} to {verb} {patient}","DIRECTIVE","ROOT","POS"),
        ("{speaker} says [{agent} asks a stranger to {verb} {patient}]","ASSERTION","QUOTED","POS"),
        ("{speaker} asks {agent} to repeat [{agent} saying please {verb} {patient}]","DIRECTIVE","QUOTED","POS"),
    ),
    "bookish_meta_carrier":(
        ("{speaker} reports {agent} did {verb} {patient}","ASSERTION","ROOT","POS"),
        ("{speaker} writes (as a song) [{agent} saying please {verb} {patient}]","MENTION","QUOTED","POS"),
        ("{speaker} adds (an aside inside the aside) what if [{agent} might {verb} {patient}]","MENTION","IMAGINED","POS"),
    ),
}


def generate(*,seed=2026111119,rounds=6):
    if type(seed) is not int or type(rounds) is not int or not 1<=rounds<=8:
        raise ValueError("Invalid third source experiment")
    rng=random.Random(seed)
    contrasts=[]
    for name,forms in sorted(THIRD.items()):
        for _ in range(rounds):
            source={k:rng.choice(v) for k,v in LEX.items()}
            carrier=rng.choice(corpus.CARRIERS)
            trio={}
            for arm,(pattern,force,scope,polarity) in zip("abc",forms):
                trio[arm]={
                    "text":pattern.format(**source),
                    "observed_event":source,
                    "carrier":carrier,
                    "semantic_graph":corpus.frame(
                        force,scope,polarity,carrier,source),
                }
            contrasts.append(trio)
    rng.shuffle(contrasts)
    result={
        "schema":corpus.SCHEMA,"split":"novel","contrasts":contrasts,
        "family":"COUNTEREXAMPLE_FOLLOWUP_NEW_ARTIFICIAL_CONSTRUCTIONS",
        "private_book_text_included":False,
        "added_after_previous_author_created_falsifier_was_inspected":True,
        "not_independent_corpus_or_real_language_human_annotation":True,
        "all_source_carriers_explicitly_supplied":True,
        "all_event_variables_explicitly_supplied":True,
        "developer_authored_semantic_graph_labels":True,
        "private_work_only_used_as_abstract_stress_inspiration":True,
    }
    result["receipt_sha256"]=corpus.digest(result)
    corpus.validate(result,split="novel")
    return result
