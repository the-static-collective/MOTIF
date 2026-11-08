"""RING-013 sealed experiments: novel language and misleading value estimates.

Imported ONLY by trial.py after a complete policy artifact is frozen and
reproduced from earlier authored training/development trials.

Both test families are newly experimenter-written synthetic tasks, NOT
independently sourced human actions, true motivation, factual consequences
or a proper prospective study of real-world action value.

MISLEADING priors deliberately violate the authored model; finding zero
regret under this shift would be unlikely and should not be asserted.
"""
from __future__ import annotations
import scenario

FORMS={
    "NOVEL_LANGUAGE":(
        "{speaker} recounts ({agent} might {verb} {patient})",
        "{speaker} records [{agent} saying {verb} {patient}]",
        "{speaker} asks whether {agent} could ever {verb} {patient}",
        "{speaker} writes (inside a poem) that {agent} did {verb} {patient}",
        "{speaker} asks {agent} to {verb} {patient}, conditionally",
        "the forgotten clock asks which of its seconds is worth saving",
    ),
    "MISLEADING_OPPORTUNITIES":(
        "{speaker} claims {agent} will definitely {verb} {patient}",
        "{speaker} remembers ({agent} might {verb} {patient})",
        "{speaker} quotes [{agent} saying promise to {verb} {patient}]",
        "{speaker} wonders why {agent} should {verb} {patient}",
        "{speaker} asks {agent} to {verb} {patient} with no proof",
        "the unfinished manuscript calls the missing page a beginning",
    ),
    "NO_VALUE_BUT_CURIOSITY":(
        "{speaker} imagines [{agent} perhaps {verb} {patient}]",
        "{speaker} asks to inspect why {agent} might {verb} {patient}",
        "{speaker} quotes [{agent} saying (consider {verb} {patient})]",
        "{speaker} wonders if {agent} might {verb} {patient}",
        "{speaker} remembers ({agent} maybe did {verb} {patient})",
        "a lantern turns toward the question it has not yet asked",
    ),
}
VOCAB={
    "speaker":("uma","ivra","zefi","omer","kaito"),
    "agent":("rhys","sena","voro","talia","jeli"),
    "verb":("engrave","hoist","balance","unfurl","polish"),
    "patient":("compass","kettle","panel","bowl","ribbon"),
}
FAMILIES=tuple(FORMS)


def generate(family,*,seed,n=20):
    if family not in FAMILIES or type(seed) is not int or type(n) is not int or not 1<=n<=60:
        raise ValueError("Unapproved benchmark family")
    examples=scenario.make_cases(
        split="novel",seed=seed,n=n,forms=FORMS[family],lex=VOCAB)
    if family=="MISLEADING_OPPORTUNITIES":
        # The published priors remain optimistic but the hidden viability
        # becomes unfavorable in 3/4 cases. Even the planner never sees
        # this changed label until the simulator produces the observation.
        for i,x in enumerate(examples):
            if i%4!=0:x["hidden"]["true_world"]="UNHELPFUL"
    elif family=="NO_VALUE_BUT_CURIOSITY":
        # Most actions provide NO useful work or future options; pure
        # epistemic interest can waste budget. ASK still costs attention.
        # The test is intentionally a tradeoff, not a fixed pass label.
        for x in examples:
            for name in ("SMASH_A","SMASH_B"):
                act=x["public"]["actions"][name]
                act["rewards"]={w:0.0 for w in scenario.WORLDS}
                act["affordances"]={w:0 for w in scenario.WORLDS}
    for x in examples:
        scenario.verify_public(x["public"])
    return examples
