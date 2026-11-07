"""RING-010 sealed challenge: new event content and compositional scope.

Imported ONLY by test.py after the derived operator AST and source receipts
are frozen. Both families are written by the same experimenter; these are
NOT independently authored natural utterances, and both use a provided
observed event context. A true free-language parser is not being tested.

Family A tests variable substitution of never-trained people/verbs/objects.
Family B tests misleading nested clauses and operator combinations.
"""
from __future__ import annotations
import random
import world

LEX={
    "people":["zevi","lynx","uma","kato","ori","fi"],
    "verbs":["unfurl","juggle","emboss","hoist","fold","sketch"],
    "patients":["lantern","kettle","scroll","kite","panel","bowl"],
}
ALTERNATE={
    "modal":(
        ("{speaker} asks {agent} to {verb} {patient}",("DIRECTIVE","ROOT","POS"),
         "{speaker} wonders whether {agent} might {verb} {patient}",("MENTION","IMAGINED","POS")),
    ),
    "quote":(
        ("{speaker} asks {agent} to {verb} {patient}",("DIRECTIVE","ROOT","POS"),
         "{speaker} quotes {agent} saying {verb} {patient}",("MENTION","QUOTED","POS")),
    ),
    "neg":(
        ("{speaker} says {agent} did {verb} {patient}",("ASSERTION","ROOT","POS"),
         "{speaker} says {agent} did not {verb} {patient}",("ASSERTION","ROOT","NEG")),
    ),
    "condition":(
        ("{speaker} asks {agent} to {verb} {patient}",("DIRECTIVE","ROOT","POS"),
         "{speaker} asks {agent} to {verb} {patient} if dawn comes",("DIRECTIVE","CONDITIONAL","POS")),
    ),
    "counterfact":(
        ("{speaker} says {agent} did {verb} {patient}",("ASSERTION","ROOT","POS"),
         "{speaker} supposes {agent} might have {verb} {patient}",("MENTION","IMAGINED","POS")),
    ),
}
NESTED={
    "mixed_neg":(
        ("{speaker} asks {agent} to {verb} {patient}",("DIRECTIVE","ROOT","POS"),
         "{speaker} asks {agent} to not {verb} {patient}",("DIRECTIVE","ROOT","NEG")),
    ),
    "quote_in_direct":(
        ("{speaker} asks {agent} to {verb} {patient}",("DIRECTIVE","ROOT","POS"),
         "{speaker} quotes {agent} saying please {verb} {patient}",("MENTION","QUOTED","POS")),
    ),
    "nested_mentioned_request":(
        ("{speaker} asks {agent} to {verb} {patient}",("DIRECTIVE","ROOT","POS"),
         "{speaker} wonders whether {agent} asks someone else to {verb} {patient}",("MENTION","IMAGINED","POS")),
    ),
    "double_negative":(
        ("{speaker} says {agent} did not {verb} {patient}",("ASSERTION","ROOT","NEG"),
         "{speaker} says {agent} did not fail to {verb} {patient}",("ASSERTION","ROOT","POS")),
    ),
    "quoted_conditional":(
        ("{speaker} asks {agent} to {verb} {patient} if dawn comes",("DIRECTIVE","CONDITIONAL","POS"),
         "{speaker} quotes {agent} saying {verb} {patient} if dawn comes",("MENTION","QUOTED","POS")),
    ),
    "hypothetical_neg":(
        ("{speaker} supposes {agent} might have {verb} {patient}",("MENTION","IMAGINED","POS"),
         "{speaker} supposes {agent} might not have {verb} {patient}",("MENTION","IMAGINED","NEG")),
    ),
}


def generate(*,family="OOV_CONTENT_TRANSFER",seed=2026111021,repeats=10):
    if family not in ("OOV_CONTENT_TRANSFER","NESTED_SCOPE_COMPOSITION"):
        raise ValueError("Wrong sealed challenge family")
    if type(seed) is not int or type(repeats) is not int or not 1<=repeats<=12:
        raise ValueError("Bad challenge dimensions")
    rng=random.Random(seed)
    patterns=ALTERNATE if family=="OOV_CONTENT_TRANSFER" else NESTED
    rows=[]
    for pairs in patterns.values():
        for ta,ma,tb,mb in pairs:
            for _ in range(repeats):
                ctx=world.observed(rng,LEX)
                rows.append({
                    "a":world.example(ta,ma,ctx),
                    "b":world.example(tb,mb,ctx),
                })
    rng.shuffle(rows)
    result={
        "schema":world.SCHEMA,"split":"novel","pairs":rows,
        "author_created_phrase_family":family,
        "all_event_verbs_and_entity_names_unseen_in_training":True,
        "source_event_graph_supplied_separately_from_text":True,
        "speaker_and_event_observations_explicitly_provided":True,
        "template_ids_hidden_from_learner":True,
        "semantic_graphs_author_labeled":True,
        "no_real_world_utterances":True,
        "not_imported_by_program_search":True,
    }
    result["receipt_sha256"]=world.digest(result)
    world.check(result,split="novel")
    return result
