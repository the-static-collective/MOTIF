# MOTIF-017F — THE SELF-GROWING FOREST AND THE IMPROVABLE DIAGNOSTIC

**Can MOTIF compose a new question, recognize that its existing diagnostic can be improved even when it is perfectly accurate, and challenge that diagnostic without making the comparison unfair?**

**Status:** Python 3.10+ standard-library experiment. It extends the separate MOTIF-015 Many Roads and MOTIF-016 Living Forest draft PR stack. MOTIF also has an unrelated parallel MOTIF-017 Question Before Question research branch. We use **017F** to avoid overwriting that branch.

## What is implemented

### 1. The question garden (bounded, source-preserving)

The original MOTIF-016 fixture contains two separate permitted primitive questions, GLOBAL_A and GLOBAL_B. A synthetic **provider offer** declares a single PAIR_V1 reading of both components and a quoted cost. That composite question **does not exist as a Road** in the original planner.

The 017F question garden can generate a new typed JOIN(GLOBAL_A,GLOBAL_B) question **from the public component signatures and this provider offer**. It computes the question's predicted partition across the existing candidate worlds, creates a source-pinned SHA-256 digest, and defaults to HOLD_UNREVIEWED/allowed=False. A checksum detects changes but is **not** a signature or trusted identity.

**Critical boundary:** it cannot fabricate physical sensing capability, free compute, a magical truth oracle, or permission. A provider must actually offer the joined measurement at the quoted price; the two source primitives must be permitted, ungated, and semantically compatible. Missing provider contract, a forbidden source, incompatible ontology, impossible prerequisite, or withheld permission prevents admission.

The evaluator (in a separate source module) reports a real **synthetic trial observation** independently of the question generator. The generator never imports or reads the secret-world simulator.

### 2. Independent local review before any proposed question can be used

The garden receives separate **synthetic adjudicated REVIEW fixtures** with independently returned observations, reported prices, declared source, phase and case identifier. The reviewer compares them with the proposed world-partition signatures. It requires a minimum number of unique cases and full structural-state coverage; any mismatch produces REFUSE_INDEPENDENT_FALSIFICATION with retained counterexamples.

A passing question is eligible for **synthetic prediction only**. It does not automatically install a real provider, grant network permission, contact a human, or modify another source repository.

We deliberately submit:
- **FUSED_PORTS**: true in separate REVIEW and TEST regimes, quoted at 0.65.
- **FALSE_SHORTCUT**: cheaper, but lies in one review world. **Rejected.**
- **DRIFT_FUSED_PORTS**: honestly reports in REVIEW but systematically corrupts one bit in a held-out regime. **Passes review but later makes 4/8 wrong predictions**; do not hide this failure.
- **OVERPRICED_PORTS**: accurate but quoted at 1.10. Not a useful replacement for the incumbent.
- **FORBIDDEN_PORTS**: a purportedly cheap offer without permission. **Held.**

### 3. A diagnostic that knows it isn't the ceiling

The old fixed classical diagnostic correctly resolves all eight modeled worlds by asking SCOUT and then two mode-dependent complementary port questions; it pays **0.90** each time.

The meta-diagnostic makes the original method a **versioned incumbent**, not a sacred optimum. It asks:

> Is there an independently reviewed new question or new procedure that preserves prediction quality but lowers cost?

In the clean, invented world, a reviewed FUSED_PORTS composite question costs **0.65** and yields the same decisions in one round. The measured expected savings is **0.25 per case**, on these eight modeled states. The meta-diagnostic marks a proposed revision ELIGIBLE_FOR_EXPLICIT_LOCAL_POLICY_REVIEW, not an automatic installation.

If the candidate loses accuracy, violates a safety gate, has insufficient evidence, or saves no cost, the method returns REFUSE/HOLD instead.

**Classical parity is essential:** an exact classical planner refitted on the SAME new provider offer and known hypothesis family also obtains 0.65 and **ties** the grown forest. This work does not exceed classical optimal planning, prove autonomous tool invention, or establish a universally superior intelligence. It only beats the *historical frozen diagnostic* with a newly reviewed question capability; the exact classical refit reveals the legitimate current ceiling.

### 4. A failure that the review cannot catch

The DRIFT_FUSED_PORTS provider is correct on all REVIEW cases, and becomes misleading after review on one of the two mode families. The forest follows the misleading but still in-grammar report, so it may confidently select the wrong answer. In the eight TEST worlds, it predicts **only 4/8 correctly**. A perfectly syntactic, origin-labeled receipt does not establish truth or future reliability.

This is an important next frontier: joint probabilistic credibility, anomaly-sensitive meta-revision and adversarially frozen shifting-world holdouts. Connect to MOTIF-014W; do not silently treat all review receipts as permanent truth.

## Reproducible benchmark

The synthetic world has three binary properties: MODE, LEFT, RIGHT. The answer is XOR(LEFT,RIGHT). All methods receive identical candidate worlds and can use identical original roads. The new provider offers are declared in a public contract menu, but a composite question cannot be used until separately reviewed.

After review, compare:
1. **Frozen strong diagnostic**: known mode-first policy (cost 0.90, accuracy 8/8).
2. **Growing forest**: select the independently admitted composite question (cost 0.65, accuracy 8/8 on reliable TEST worlds).
3. **Classical exact refit**: identical optimal finite-state planning over the same expanded catalogue (cost 0.65, accuracy 8/8; ties as expected).

The difference between REVIEW and TEST is a separate synthetic sampling *phase*, **not** a statistically independent family of real-world tasks. Eight related simulated configurations do not establish generalization, statistical confidence, or a breakthrough over strong classical methods.

Reproduce:

    cd experiments/017f
    python -m unittest -v test_grow.py
    python benchmark.py

Every false attribution, held question, drift error and unadopted diagnostic revision is included in the JSON result.

## Important next experiments

- Discover **latent structural features** from held-out graph transitions and synthesize candidate roles rather than only compositions of already offered probes.
- Compare with classical dynamic programming, cost-aware CART, Bayesian experimental design and formal CEGIS over the *same* expanded primitive grammar and budget.
- Measure gains in the actual reachable affordance space (MOTIF-003) versus merely compressing two known reports into one reading; no free capability can be conjured.
- Use independently held stochastic noisy test families and MOTIF-014W reliability uncertainty, including cross-source dependence and post-review drift detection.
- Check the effects of constrained human attention, latency, simultaneous answers, asynchronous cancellation and safe early exit.
- Require separately reviewed, scoped permission and authenticated records before ever exposing a synthetic research cartridge to a live JAR;VIS external adapter.

**A diagnostic that is perfectly accurate can still be suboptimal. A newly available probe can improve an old baseline. The optimal classical planner can also use that probe. No research result is permission, and an approved question is not automatically a truthful witness.**
