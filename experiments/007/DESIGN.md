# MOTIF-007 — INHERITANCE WITHOUT EMPIRE

### Two separate worlds exchange a learned method, not their worlds

**Status:** Executable synthetic proof of a narrow portable-method exchange. Neither a networked federation, verified cryptographic identity, real-world consent engine, proven privacy guarantee, distributed consensus system, nor a causal or neural intelligence.

## The research question

Can a method inferred in one simulated relational world be used in another *without copying either world's observed graph*, without automatically admitting the method, and without granting the donor authority over the receiving world?

Can the recipient then compose an improved method from the inherited method and its own source operators, export the **abstract operation**, and have the donor independently test it in a new local world?

This research builds directly upon [MOTIF-006](../006/DESIGN.md), whose primitive and nested macros are identified by role-relative source fingerprints and checked replay.

## What the implemented experiment does

\`\`\`text
         MOTIF A                                     MOTIF B
    [A's local graph]                           [B's local graph]
           |                                            |
     learns a macro                                  not exported
           |
    EXPORT operator closure
      - abstract types
      - rewrite preconditions
      - rewrite effects
      - nested program
      - source fingerprints
      - content checksum
      - UNVERIFIED origin label
           |
     [portable JSON] ------------------------------> RECEIVE
                                                     |
                                                     HOLD
                                                     |
                                               validate schema
                                               verify closure
                                               check source pins
                                               reject authority-minting effects
                                                     |
                                               PREVIEW ON B'S WORLD
                                               (still HOLD)
                                                     |
                                               EXPLICIT LOCAL REVIEW
                                               (fixture decision, no ID proof)
                                                     |
                                               ADMIT_PLAN_ONLY
                                                     |
                                             REPLAY EACH PRIMITIVE
                                                     |
                                            B adds another local step
                                                     |
                                           LEARN B'S COMPOSITE MACRO
                                                     |
     RECEIVE <--------------------------- [abstract extended method]
        |
       HOLD
        |
    TEST ON A'S WORLD
        |
     LOCAL REVIEW
        |
  ADMIT_PLAN_ONLY
        |
  FOUR-STEP SYMBOLIC REPLAY
\`\`\`

## Synthetic demonstration

A begins with two primitive verbs induced by MOTIF-002: teach and repair. MOTIF-006 builds a two-step macro, then a three-step nested macro. This is the transferable method.

A exports **four** referenced source operator definitions: two primitives and two macros. A does **not** include the world used to learn it (the graph with Jo, Mira, bike1 and bike2), trace histories, personal identity evidence, account tokens, network addresses, or permissions on the recipient's behalf.

B has its own, separately constructed synthetic field: Nina, Omar, three broken bicycles, and explicit *toy* permission facts. It may inspect the package and preview it before admission. The preview remains held.

When B explicitly records a local \`ADMIT_PLAN_ONLY\` decision tied to the artifact checksum and a successful local preview hash, the method can be used for **local simulated planning**. Every constituent checks types, tools and the synthetic permission facts. A package cannot execute anything.

B then observes the *simulated* three-step result and composes the incoming macro with one additional repair operation, producing a four-step source-pinned macro. B exports this revised program and its full dependency closure—**five** source definitions—to A.

A independently receives, previews, and admits that return artifact under its own synthetic reviewer fixture. A's own new local scene, containing a third bicycle, reaches the result of four original primitive transformations.

Neither side's world or authority is transferred. The methods are more portable than the originating situations, but this is only a controlled structural transfer demonstration: the worlds use the same explicit ontology, graph vocabulary and operator semantics.

## Exact technical claims

**Implemented:**

- Explicit portable JSON schema with strict field allowlists and byte/operator limits.
- Deterministic SHA-256 package checksum to detect accidental byte-level alterations **without claiming author identity**.
- Semantic source fingerprints, dependency closure verification, bounded nested lengths, type checks and cycle rejection.
- Reject package attempts to include unrelated fields or fabricate \`permits\`, \`authorizes\`, \`consent\`, \`admitted\` and similar synthetic authority-like relations as effects.
- Receiver-owned pending offers; default \`HOLD\`.
- Successful *local* preview produces an exact checksum of the hypothetical result and a separate preview digest. No resulting world graph is shipped back.
- Separate explicit local \`ADMIT_PLAN_ONLY\` or \`REFUSE\` review, with local decision record.
- Post-admission semantic drift checks on **every** source operator before any simulation.
- Local \`REVOKE_PLAN_ONLY\` blocks further use of that exact admitted package.
- A recipient constructs a composite operation that includes an inherited one, then exports it back.
- The original observed worlds remain immutable in both simulations.

**Not implemented:**

- Signatures, authenticated authorship, real human identity, reLATTE crossings, confidential transport, network access, encryption, or verifiable custody.
- A secure privacy review of arbitrary operator definitions. Even an abstract program can contain identifying constants or dangerous code if schemas become more expressive. The fixture packages do not contain raw world graphs; this **does not** guarantee zero information leakage in all future systems.
- Full transitive revocation across multiple independently re-exported packages. Revocation of a local package currently blocks that receiver's direct use of that **specific** artifact; it does not retroactively revoke every previously imported descendant.
- Real-world availability, human consent, external operation, physical transaction, or verified causal learning.
- Interoperability with heterogeneous ontologies. The current portable type vocabulary remains MOTIF-002's explicit \`person\` and \`bike\`.
- A trained neural model; all programs are transparent symbolic rewrites and the training data are intentionally artificial.
- A proof that SHA-256 makes the provenance label authentic. **An attacker can modify a packet and recompute its checksum**. The receiver must not trust the sender's label as identity.

## Architecture: authority never moves with a program

\`\`\`text
content checksum != authentication
operation definition != evidence of success
source fingerprints != truth
learned macro != ability to act
synthetic permit fact != human consent
local simulation approval != actual authorization
exported method != recipient authority
derived descendant != revocable lineage guarantee
\`\`\`

The local import gate checks only simulated method integrity and the receiver's deliberately explicit *fixture* decision. An eventual production bridge needs actual cryptographic identities, consent, scoped licenses, local signatures, ACLs, publication review, privacy analysis, and reLATTE admission rules.

## Reproduce

Python 3.10+, standard library, no external API or cost:

\`\`\`sh
cd experiments/007
python inheritance.py
python -m unittest -v test_inheritance.py
\`\`\`

GitHub Actions runs this example and all MOTIF-001 through MOTIF-006 tests. [Captured CI result](experiment-results.json) is stored alongside the implementation.

Tests include checksum corruption, rehashed origin impersonation, schema injection, forged permission effects, stale source fingerprints, missing dependencies, mismatched local roles, local permissions/tools, default hold, review denial, admission review hash, revocation, original-world immutability, post-admission source mutation, and two-way inheritance.

## MOTIF-008 research invitation: Predict the novel, not just repackage the known

The seven existing generations still work largely inside a hand-designed and narrow synthetic world. To test whether this architecture provides a different *intelligence*, the next experiment should not simply add another control layer.

It should create a **cross-world generalization laboratory**:

1. Generate multiple distinct graph domains (not only bicycles), with hidden transition rules and partially observed preconditions.
2. Train motifs in some domains, **withhold different graph structures and action configurations**, and measure whether they transfer.
3. Let the system invent candidate relational or composite operators from failed predictions, but require separate, unknown-at-training-time **test worlds** to accept them.
4. Compare to fixed STRIPS-style planning, two-hop relational baselines, and small learned graph models at equal inference/observation budgets.
5. Track calibrated abstention, observed outcome errors, frontier gains, compression, cost and task completion—not only the number of motifs created.
6. Introduce provenance-preserving cross-world transfer with revoked or conflicting donor models; demonstrate real local refusal and safe fallback.
7. Freeze model choices before test-world generation to prevent hand-tuning on the eventual result.

**Falsifier:** if the transfer architecture produces no meaningful predictive or planning improvement over classical symbolic planners under equal conditions, don't claim that new intelligence has emerged. Keep whichever parts improve interoperability and auditability.

The experiment's central hypothesis remains:

> Shared methods can accumulate without accumulating shared sovereignty, but the usefulness of those methods must be independently proven in each receiving world.
