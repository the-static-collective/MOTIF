# MOTIF-024 — The Right to Be Wrong

The MOTIF-023 handshake was conservative but sometimes too abstract: "Any source or both named sources?" People can often answer more accurately when they can **see concrete examples of a finished response**.

This new experimental organ accepts a bounded original question and responds with exactly **two distinct concrete outcome examples**:

- **Example A:** "One USGS river discharge report, from any one of the three named public stations, timestamped within the last 12 hours, would be enough."
- **Example B:** "I need a discharge report from Blue Earth AND a separate report from Le Sueur, each timestamped within the last 12 hours."

Then it asks **"Would either be enough? Or write your own example."** It never selects on the person's behalf.

A custom typed "enough" example goes through the actual source-owned MOTIF-023 finite grammar. A narrow positive example such as "One report from within the last 6 hours would be enough" can become a new, inspectable contract; a custom criterion that is unsupported, negated, high stakes, or ambiguous **HOLDs** rather than being hallucinated into a confident intent. If it is clear *which* source matters but freshness is missing, ask just the freshness question, not an unrelated interrogation.

Confirmation is attached to the **exact SHA-256** of the resulting evidence contract, and a correction that changes the contract's digest requires a new confirmation. No change is applied to the person's original words, nor to a shared/global policy. There is no persistence or machine learning in this iteration. The old contract does not authorize any action. Even the correctly confirmed contract is HELD: no network source request, no model/API credits, no log, no actuation, and no model promotion.

The two examples are *illustrations*, not actual recent agency measurements. Both propose a 12-hour recency rule, which must be explicitly chosen, not inferred; if the original request specified a conflicting rule, the example is refused and the person can rewrite their own. Historical GHoT-004 physical evidence showed that the one-source and two-named-source tasks required **one and two actual HTTP GETs** in that earlier experiment. The example chooser makes no forecast of future resource use, and electrical Joules remain unknown.

## Use

From the MOTIF repository root:

    python3 -m unittest discover -s experiments/024 -p 'test_*.py' -v
    printf '%s' '{"text":"Could you check the rivers?"}' | python3 experiments/024/goal_examples.py
    printf '%s' '{"text":"Could you check the rivers?","choice":"custom","own_example":"One report from within the last 6 hours would be enough"}' | python3 experiments/024/goal_examples.py

The intended JAR;VIS page displays two cards reading "Would this be enough?" and a textarea for "Or type your own example." Corrections happen only in the browser session and must be reconfirmed. The local Python bridge never transmits raw personal input to GHoT or remote services. The finite grammar is not a general understanding engine; genuine real-user validation and independent outcome tests remain outstanding.

**No custom criterion is discarded or silently overwritten. If it cannot be parsed safely, the user is shown that boundary and invited to restate it.**
