"""Bridge to the REAL MOTIF-003 affordance-selector implementation.

MOTIF-003 quite properly says its number of newly reachable states has NO
moral significance by itself. Here a controlled synthetic adaptation tests
what happens if a system forgets that warning and optimizes future choices
or immediate gain without considering consent and boundaries.

This is a critic for misuse of MOTIF-003, not a claim that its actual
architecture is unsafe (it explicitly disclaims normative authority).
"""
from __future__ import annotations

from hashlib import sha1
from pathlib import Path
import sys

AFFORDANCE=Path(__file__).resolve().parents[1]/"003"/"affordance.py"
ORIGINAL_BLOB="db25da0d50a9c8e2cd87aa576a22f969405737cf"


def pin():
    raw=AFFORDANCE.read_bytes()
    actual=sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
    if actual!=ORIGINAL_BLOB:
        raise ValueError("MOTIF-003 affordance source changed; re-evaluate baseline")
    return actual


pin()
sys.path.append(str(AFFORDANCE.parent))
from affordance import select_first_move


def unguarded_proxy_selection(s,priority="new-choices"):
    """No moral/consent filter: an intentionally bad standalone policy.

    The options numbers are invented ordinal toy attributes. Placeholder
    tokens do NOT represent actual affordances in a person's life.
    """
    rows=[]
    for a in s["actions"]:
        tokens=tuple(("toy_fictional_option_"+str(i),) for i in
                     range(max(0,a["options"])))
        lost=tuple(("toy_fictional_lost_"+str(i),) for i in
                   range(max(0,-a["options"])))
        rows.append({
            "operator":a["id"],"roles":(s["recipient"],),
            "new_affordances":tokens,
            "lost_affordances":lost,
            "new_skill_facts":tuple(),
            "immediate_delta":a["gain"],
            "reachable_after_first_move":max(1,1+a["options"]),
            "truncated":False,
        })
    if not rows:return None
    selected=select_first_move(rows,priority=priority)
    return selected["operator"] if selected else None
