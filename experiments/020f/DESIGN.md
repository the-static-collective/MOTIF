# MOTIF-020F — THE INSIDE-OUT BOX
## planZ × the cost of NOT doing something

**Research question:** How should MOTIF value a decision when waiting can destroy useful future options? The cost of deliberation is not merely CPU or query cost: deadlines, perishability, consent, option preservation, and foregone welfare can dominate.

**Status:** Executable Python 3.10+ and Node 20+ standard-library experiment. Entirely read-only source integration and synthetic planning. No external dispatch, field trial, source-owner permission, verified real deadline or verified welfare valuation. Stacked on MOTIF-019F PR #28 → 017F #23 → 016 #21 → 015 #20.

## 1. The original planZ is integrated, not imitated

Two files are **byte-identical original** planZ/main artifacts in the upstream directory:

| planZ file | Git blob |
| --- | --- |
| public/attention-v1.json | 49e70c0caeaf0bca430338829b69d51c8c617385 |
| scripts/validate-attention.mjs | a6fb92b5242519fa1c72b88cf1d34eb6770063ea |

The JavaScript bridge verifies both source hashes and actually invokes planZ's original native validatePublicAttention function. The Python adapter preserves the validated index's original plan identifiers, source issue links, statuses, blockers and next human gates.

The captured public edition is **ATTENTION-2026-10-28-005** (reviewed October 28, 2026). The index is explicitly INDEX_ONLY and every plan has fieldOutcome=NOT_VERIFIED, executionAllowed=false and thirdPartyApproval=NOT_ESTABLISHED.

**It contains no verified per-plan deadline, reward, harm, time sensitivity, cost, or probability of success.** No time assumption is derived from the edition or date of publication. The real-world adapter returns HOLD_NO_VERIFIED_INACTION_VALUATION rather than manufactured urgency. planZ is not a task dispatcher or an authority over owning projects.

## 2. Turn the reasoning box inside out

The proposed reasoning object is not simply a score assigned to an action. It is the **difference between two reachable futures**.

With a finite-horizon, explicitly modeled environment:

    V*(t, remaining_options, remaining_attention)
       = best modeled future net benefit under permitted synthetic choices
         of ACT, multiple simultaneous ACTs or WAIT.

    LOSS_IF_WAIT_ONE_TICK = V*(t) - V*(t+1 after taking WAIT)
    LOSS_IF_OMIT(i) = V*(all choices) - V*(same world with i unavailable)
    LOSS_IF_EMPTY_DELIBERATION = LOSS_IF_WAIT_ONE_TICK + direct compute expense

These are distinct. The last expression is valid only when deliberation adds **no useful information or decision quality**; information gathering can be worthwhile despite delay.

The engine is an exact **classical finite-horizon dynamic program**, choosing one-tick batches subject to limited attention. It permits WAIT and does not force actions when utility is zero or negative. The engine can preserve several expiring options with simultaneous work where hypothetical parallel capacity permits it.

Each plan's time window, success probability, reward, decay and cost is a **declared fictional scenario overlay**. The source planZ snapshot itself is never promoted to permission or urgency evidence. Negative actor-level outcomes are a hard synthetic stop; positive aggregate utility cannot override a harmed participant.

## 3. Frozen counterfactual, not actual community advice

For this single synthetic example we attach invented welfare units and expiry ticks to two *real public PlanZ plan IDs*. Neither real plan has an asserted deadline:

| Plan pointer | Invented reward units | Invented last available tick | Real field permission |
| --- | ---: | ---: | --- |
| SHELF-001 | 6 | 0 | NOT ESTABLISHED |
| GARDEN-TABLE-001 | 8 | 2 | NOT ESTABLISHED |

One synthetic attention unit per action, budget two, at most one action at a time:

- Fully informed temporal DP: collect the smaller perishable 6 first and the durable 8 later = **14**.
- Myopic greedy: select durable 8 immediately and miss the expiring 6 = **8**.
- WAIT exactly one tick, then plan optimally: **8**.
- **Cost of inaction for one tick: 6 synthetic welfare units**.
- Direct one-tick cognitive cost 0.05; empty deliberation that consumes that tick has combined modeled cost **6.05**.
- Permanent omission of SHELF-001 loses 6, while permanent omission of GARDEN-TABLE-001 loses 8.
- If both options were invented as expiring immediately, parallel capacity two preserves both; capacity one cannot.

No value here is a dollar amount, measured hunger, verified logistical cost, consent, actual emergency or reason to bypass the owning project's review. The synthetic overlay is fully logged in the JSON output.

## 4. Fair comparison and failures

The optimizer **is classical planning**. A strong, independently implemented fully informed finite-horizon optimal planner would tie given the same stated costs, options and deadlines. This experiment only tests the difference between non-myopic temporal planning and a greedy immediate-value heuristic.

It preserves negative controls: if there is no temporal evidence, HOLD; if a proposed action harms an actor, skip it; if a candidate offers zero expected benefit, do nothing; if a real planZ pointer claims permission or verified execution, reject the source contract; if no future value is lost by waiting, waiting is allowed rather than manufactured urgency.

## 5. Next honest boundary: live information value

MOTIF-015/016 already supports simultaneous question portfolios and contingent reasoning. The next integration should allow a read-only question to consume time **and genuinely improve a modeled decision**. Its expected value is:

    Gain from better informed future decisions
      MINUS computation and question costs
      MINUS expected options lost while the question is answered.

That needs explicit noisy observation models, asynchronous latency, safe cancellation, receipt custody and independently checked external deadlines. No verified real deadlines are available in this PlanZ edition.

## Reproduction

Python 3.10+, Node 20+, no paid providers, secrets or network calls:

    cd experiments/020f
    python -m unittest -v test_insideout.py
    python demo.py

Outputs preserve original planZ source pins and human gates, synthetic timing assumptions, independent WAIT and omission measures, future schedule, actor effects and the strict no-dispatch boundary.

**The central question:** What could become impossible, for whom, and when, if we don't act? The answer must remain proportional to verified evidence, not invented urgency.
