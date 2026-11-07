"""RING-011 heldout-only complex nested meaning and cryptic-reader stress.

The source book supplied the *design concerns*, not any public source prose.
All test utterances are NEW, artificial text written for this benchmark.
Never imported by program selection; no actual user memoir is uploaded.

FAMILY ONE: unseen event vocabulary, familiar conversation scope forms.
FAMILY TWO: nested brackets, editorial asides, quotation-within-request,
and uncertain/provisional language patterns (none copied from the book).

A third adversarial diagnostic tests intentionally ungrounded, unknown or
malformed lines and must HOLD, not invent a source event or testimony.
"""
from __future__ import annotations
import random
import corpus

VOCAB={
    "speaker":("zeva","opal","rin","mero","uri"),
    "agent":("tyn","kairo","noel","nila","vee"),
    "verb":("unfurl","polish","mend","spin","stack"),
    "patient":("flag","compass","booklet","vase","shelf"),
}
# Each group has THREE source interpretations of the SAME observed event.
# These templates are omitted from the learner's import graph.
OOV={
 "quote":(
  ("{speaker} asks {agent} to {verb} {patient}","DIRECTIVE","ROOT","POS"),
  ("{speaker} quotes [{agent} saying please {verb} {patient}]","MENTION","QUOTED","POS"),
  ("{speaker} asks {agent} to quote [{agent} saying please {verb} {patient}]","DIRECTIVE","QUOTED","POS")),
 "imagine":(
  ("{speaker} asks {agent} to {verb} {patient}","DIRECTIVE","ROOT","POS"),
  ("{speaker} imagines [{agent} asking to {verb} {patient}]","MENTION","IMAGINED","POS"),
  ("{speaker} says what if [{agent} were to {verb} {patient}]","MENTION","IMAGINED","POS")),
 "negate":(
  ("{speaker} says {agent} did {verb} {patient}","ASSERTION","ROOT","POS"),
  ("{speaker} says {agent} did not {verb} {patient}","ASSERTION","ROOT","NEG"),
  ("{speaker} asks {agent} not to {verb} {patient}","DIRECTIVE","ROOT","NEG")),
 "condition":(
  ("{speaker} asks {agent} to {verb} {patient}","DIRECTIVE","ROOT","POS"),
  ("{speaker} asks {agent} to {verb} {patient} if the bell rings","DIRECTIVE","CONDITIONAL","POS"),
  ("{speaker} wonders if [{agent} might {verb} {patient}]","MENTION","IMAGINED","POS")),
 "quoted_negative":(
  ("{speaker} quotes [{agent} saying please {verb} {patient}]","MENTION","QUOTED","POS"),
  ("{speaker} quotes [{agent} saying please do not {verb} {patient}]","MENTION","QUOTED","NEG"),
  ("{speaker} asks {agent} to quote [{agent} saying please do not {verb} {patient}]","DIRECTIVE","QUOTED","NEG")),
 "aside":(
  ("{speaker} says {agent} did {verb} {patient}","ASSERTION","ROOT","POS"),
  ("{speaker} says ({agent} did {verb} {patient})","ASSERTION","ROOT","POS"),
  ("{speaker} wonders ([{agent} might {verb} {patient}])","MENTION","IMAGINED","POS")),
}
CRYPTIC={
 "voice_in_voice":(
  ("{speaker} asks {agent} to {verb} {patient}","DIRECTIVE","ROOT","POS"),
  ("{speaker} quotes ([{agent} saying please {verb} {patient}])","MENTION","QUOTED","POS"),
  ("{speaker} asks {agent} to quote ([{agent} saying please {verb} {patient}])","DIRECTIVE","QUOTED","POS")),
 "parenthetical_reader":(
  ("{speaker} says {agent} did {verb} {patient}","ASSERTION","ROOT","POS"),
  ("{speaker} says (({agent} did not {verb} {patient}))","ASSERTION","ROOT","NEG"),
  ("{speaker} wonders (([{agent} might {verb} {patient}]))","MENTION","IMAGINED","POS")),
 "conditional_inside_aside":(
  ("{speaker} asks {agent} to {verb} {patient}","DIRECTIVE","ROOT","POS"),
  ("{speaker} asks {agent} to {verb} {patient} (if the bell rings)","DIRECTIVE","CONDITIONAL","POS"),
  ("{speaker} imagines (({agent} asking to {verb} {patient}))","MENTION","IMAGINED","POS")),
 "inverted_action":(
  ("{speaker} requests {agent} to {verb} {patient}","DIRECTIVE","ROOT","POS"),
  ("{speaker} reports {agent} did not {verb} {patient}","ASSERTION","ROOT","NEG"),
  ("{speaker} quotes [[{agent} saying please {verb} {patient}]]","MENTION","QUOTED","POS")),
 "nested_negation":(
  ("{speaker} asks {agent} to {verb} {patient}","DIRECTIVE","ROOT","POS"),
  ("{speaker} quotes (({agent} saying please do not {verb} {patient}))","MENTION","QUOTED","NEG"),
  ("{speaker} asks {agent} to quote (({agent} saying please do not {verb} {patient}))","DIRECTIVE","QUOTED","NEG")),
 "hypothetical_narrator":(
  ("{speaker} says {agent} did {verb} {patient}","ASSERTION","ROOT","POS"),
  ("{speaker} says what if (({agent} were to {verb} {patient}))","MENTION","IMAGINED","POS"),
  ("{speaker} asks {agent} to quote [{agent} saying please {verb} {patient}]","DIRECTIVE","QUOTED","POS")),
}

def generate(*,family="OOV_CONTENT",seed=2026111108,rounds=5):
    forms={"OOV_CONTENT":OOV,"CRYPTIC_NESTED":CRYPTIC}.get(family)
    if forms is None or type(seed) is not int or type(rounds) is not int or not 1<=rounds<=10:
        raise ValueError("Unknown postfreeze source family")
    rng=random.Random(seed)
    triples=[]
    for label,variants in sorted(forms.items()):
        for _ in range(rounds):
            source={k:rng.choice(v) for k,v in VOCAB.items()}
            carrier=rng.choice(corpus.CARRIERS)
            triple={}
            for suffix,(template,force,scope,polarity) in zip("abc",variants):
                triple[suffix]={
                    "text":template.format(**source),
                    "observed_event":source,
                    "carrier":carrier,
                    "semantic_graph":corpus.frame(
                        force,scope,polarity,carrier,source),
                }
            triples.append(triple)
    rng.shuffle(triples)
    out={
        "schema":corpus.SCHEMA,"split":"novel","contrasts":triples,
        "family":family,
        "private_book_text_included":False,
        "all_source_carriers_explicitly_supplied":True,
        "all_event_variables_explicitly_supplied":True,
        "developer_authored_semantic_graph_labels":True,
        "private_work_only_used_as_abstract_stress_inspiration":True,
        "novel_module_not_imported_by_search":True,
    }
    out["receipt_sha256"]=corpus.digest(out)
    corpus.validate(out,split="novel")
    return out


# New artificial observations; these intentionally have *no* valid source
# binding and cannot legitimately map to a directive or factual proof.
UNBOUND_UTTERANCES=(
    "perhaps the cup is a door inside somebody else's weather",
    "the parenthesis (wonders what its parent was (before the book))",
    "what if [the fourth wall asked the stage for a witness]",
    "one voice calls another voice (which may not be speaking)",
    "a song is not an event; a note is not a corroborating record",
    "the map remembers [someone telling someone else] to move a shadow",
)
