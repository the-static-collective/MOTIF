"""027F: source-anchored *applicability* gate, separate from sensor validation.

This is a manually specified, independent lexical relevance contract. It
does not verify the note's truth, authorship, identity, or permission.
Crucially, the note MUST contain a cited literal substring establishing
both a gate-related subject and an unresolved/problem predicate. Similarity
scores or three agreeing T5 nodes can never generate either witness span.

These patterns are frozen before 027F scored examples are run. A standalone
anchor-only rule is always included to prevent crediting T5 for the lexicon.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from hashlib import sha256
import re

GATE_SUBJECTS = {
    "FOOD": (
        r"\bbuffet\b", r"\bfood\b",r"\bmeal\b",r"\bpotluck\b",
        r"\bsupper\b",r"\bkitchen\b",r"\bsandwich(?:es)?\b",
        r"\bcater(?:er|ing)?\b",r"\btray(?:s)?\b",r"\bsoup\b",
        r"\bhandling\b",r"\bhygiene\b",r"\bserv(?:e|ing|ice)\b",
        r"\btemperature(?:s)?\b",r"\brefrigerat(?:e|ion|or)\b",
    ),
    "AUDIO":(
        r"\bspeaker(?:s)?\b",r"\bmicrophone(?:s)?\b",r"\bmic\b",
        r"\bcable(?:s)?\b",r"\bamplifier\b",r"\bpa\b",
        r"\bmixer\b",r"\bsound\b",r"\bmonitor(?:s)?\b",
        r"\bwireless\b",r"\baudio\b",r"\bsignal\b",
    ),
    "ACCESS":(
        r"\bramp\b",r"\bwheelchair\b",r"\bstairs\b",r"\belevator\b",
        r"\blift\b",r"\bdoorway\b",r"\bthreshold\b",
        r"\bentry\b",r"\bentrance\b",r"\baccessible\b",
        r"\bmobility\b",r"\bturnstile\b",
    ),
    "STAFF":(
        r"\bcrew\b",r"\bhelper(?:s)?\b",r"\bhost(?:s)?\b",
        r"\bvolunteer(?:s)?\b",r"\bstaff\b",r"\bwelcome\b",
        r"\battendant\b",r"\bsupervis(?:e|ion|or)\b",
        r"\bteardown\b",r"\bsetup\b",r"\bcleanup\b",
    ),
}
UNRESOLVED=(
    r"\bno(?:body|one)?\b",r"\bnot\b",r"\bnever\b",
    r"\bwithout\b",r"\bmissing\b",r"\bunknown\b",
    r"\bunclear\b",r"\bunconfirmed\b",r"\buntested\b",
    r"\bunverified\b",r"\bunassigned\b",
    r"\bhasn.t\b",r"\bhaven.t\b",r"\bdoesn.t\b",r"\bdidn.t\b",
    r"\bcan.t\b",r"\bcannot\b",r"\bwon.t\b",
    r"\bblocked\b",r"\bbroken\b",r"\bdamaged\b",
    r"\bfail(?:ed|ure|ing)?\b",r"\bbuzz(?:es|ing)?\b",
    r"\bcrackl(?:e|ing|es)\b",r"\bshut(?:ting)?\b",
    r"\bcuts? out\b",r"\bloose\b",r"\bunsafe\b",
    r"\bproblem\b",r"\bwho (?:is|will|can)\b",
    r"\bwho checks\b",r"\bwho will\b",
    r"\bkeeps?\b",r"\bcan't\b",
)
# Negation or malfunction predicates embedded in a NON-gate activity are NOT
# by themselves relevant. Require a separate matched gate-subject span.
MAX_GAP=125


@dataclass(frozen=True)
class Relevance:
    status: str
    candidate_gate: str
    matched_subject: str | None
    matched_problem: str | None
    source_quote: str | None
    note_sha256: str
    authority: str = "LEXICAL_NOTE_RELEVANCE_ONLY"
    real_source_authenticated: bool = False
    human_permission_granted: bool = False

    @property
    def supported(self)->bool:
        return self.status=="SOURCE_QUOTE_SUPPORTS_REVIEW"


def relevance_witness(note:str,candidate_gate:str)->Relevance:
    if not isinstance(note,str) or not 1<=len(note)<=300:
        raise ValueError("HOLD_BAD_NOTE_LENGTH")
    digest=sha256(note.encode()).hexdigest()
    if candidate_gate not in GATE_SUBJECTS:
        return Relevance("HOLD_NO_GATE_WITNESS_GRAMMAR",candidate_gate,
                         None,None,None,digest)
    subj=[m for pattern in GATE_SUBJECTS[candidate_gate]
          for m in re.finditer(pattern,note,re.IGNORECASE)]
    issues=[m for pattern in UNRESOLVED
            for m in re.finditer(pattern,note,re.IGNORECASE)]
    if not subj or not issues:
        return Relevance("HOLD_RELEVANCE_NOT_WITNESSED",
                         candidate_gate,None,None,None,digest)
    possible=[]
    for a in subj:
        for b in issues:
            gap=max(a.start(),b.start())-min(a.end(),b.end())
            if gap<=MAX_GAP:
                begin=min(a.start(),b.start())
                end=max(a.end(),b.end())
                possible.append((max(0,gap),begin,end,a,b))
    if not possible:
        return Relevance("HOLD_SOURCE_SPANS_TOO_FAR_APART",candidate_gate,
                         None,None,None,digest)
    gap,begin,end,a,b=min(possible,key=lambda t:(t[0],t[1],t[2]))
    quote=note[begin:end]
    return Relevance("SOURCE_QUOTE_SUPPORTS_REVIEW",candidate_gate,
                     a.group(0),b.group(0),quote,digest)


def anchored_native_guess(note:str)->tuple[str,...]:
    """Strong comparator: same explicit lexical evidence without any T5."""
    return tuple(gate for gate in GATE_SUBJECTS
                 if relevance_witness(note,gate).supported)
