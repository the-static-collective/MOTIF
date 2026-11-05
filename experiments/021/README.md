# MOTIF-021 — Learn from a Verified Game Result

**Experimental interpretation engine, not a cryptographic or human-witness verifier.**

This research companion to MOTIF-020 consumes a reLATTE-009 *independently verified* game-return receipt and asks: what did the selected instrument teach us, and which question should come next?

The original instrument is:
- Official vanilla Minecraft 26.1.1, World B, seed `918273645`;
- New game-only repeater fault at `x=-13, y=66, z=46`;
- Nine redstone lamps, count threshold `>=4`;
- Two intentionally seeded hypothetical models previously predicted **3** versus **4** lamps.

The source of the claimed game observation **must** be verified by reLATTE's independent verifier `experiments/motif-instrument-009/verify.mjs`. That verifier rechecks the original 004/005 signed world histories, the 008 instrument crossing, the 009 game crossing, the readout from the fresh non-OP Minecraft client and the raw server blockstates. This MOTIF script **does not perform those cryptographic checks** and cannot independently establish provenance.

The interpreter is intentionally conservative:

1. If the new observed count is **3**, it computes a conditional posterior favoring the position-invariant model under the stipulated sensor reliability.
2. If the count is **4**, it favors the rival world-local hidden-relay model.
3. If the count is **anything else**, it produces **HOLD_OUT_OF_MODEL_OBSERVATION** rather than forcing the result into one of the two seeded explanations.
4. It removes the already tested target from future candidate measurements, keeps older game observations unchanged, and re-evaluates *affordable* remaining instruments. In this seed, the only remaining discriminating target exceeds the current budget, so the system **HOLDS** and poses a new question about budget or better measurements.
5. All posterior probabilities remain conditional on *seeded priors* and *assumed reliability*. They are not claims of certainty, live sensor truth, permission, owner admission or persistent UNDERSTORY memory.

The new game cannot be called observed until the official game CI and independent replay both pass. The model's interpretation must not be fed back as if it were an independent game observation. This is **one epistemic update**, not an autonomous universal learner.

Tests: `node --test experiments/021/learn_from_game.test.mjs` (hypothetical receipts only). Connected native verification runs separately in the reLATTE repository.

The next architectural step is to preserve the authenticated game receipt's digest in a new UNDERSTORY contact/decoder/HOLD/activation chain, without rewriting the old synthetic investigation or claiming the non-human game observer was a human witness.
