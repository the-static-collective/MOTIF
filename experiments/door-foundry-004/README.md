# MOTIF-004 — THE QUESTION BEFORE THE TOOL

The first deliberate step from "we specify which new organ to build" toward **MOTIF itself recognizing that a missing observation could change its decision**.

## Scope and outcome

This remains an **offline, finite, synthetic experiment**. The objective, two possible policies and the source fixture domain are defined by the experiment author. It does not show general autonomous curiosity, arbitrary software synthesis or a real need discovered independently of the designer.

The new causal ordering is:

1. **Original MOTIF-002/003**, independently pinned at commit `5ee9207f04af2826750863526af7f92b31ef8578`, simulates its original graph world.
2. It independently determines that its **immediate-result** and **new-options** declared priorities select **different first moves**. The ambiguity supplies an actual source-native reason to ask for additional information.
3. Without inspecting any candidate executable or naming its desired JSON field, MOTIF emits `motif.self-inquiry.v0` asking for a bounded numeric observation that could determine which declared policy to use.
4. A **control world with no simulated permission** generates no question and ends in `HOLD`. This check precedes the GRAFT call in the hosted workflow.
5. Only after the question is saved, **original GRAFT-027** generates a finite-grammar numeric projection module. **Original CANNON-093** independently reviews its source and blind cases, producing an unsigned `HOLD` receipt.
6. **MOTIF-003's original local builder** checks that receipt, independently recompiles the original GRAFT candidate, and creates another local runnable MOTIF build. The new code reads the synthetic numeric field and influences **actual original MOTIF-003 policy selection**. MOTIF-004 checks the answer against the *question it saved before seeing the program*.
7. MOTIF writes a new **unsent research question** about unfamiliar observation schemas. This is a proposal, not a background/self-modifying software loop.

This exercise improves the provenance of inquiry, not the intrinsic intelligence of the underlying algorithms.

## Fixed synthetic comparison

The selected original GRAFT module is a finite numeric JSON path extractor using a **synthetic ALEX-shaped packet**. Its original source is pinned at `6ff59aead0296081e1547d8107e4b6f06ea2381e`; the CANNON review code is pinned at `0fd326c1bb6f222dc572a4877818d63881828801`.

On four synthetic final examples, the declared decision rule is "numbers >=2 → new-choices; otherwise immediate." A policy that never measures and always chooses immediate agrees with the declared synthetic rule in **2/4** cases. The GRAFT-generated field reader and original MOTIF policy agree **4/4**.

A **fair classical selector with the same labeled selection evidence also reaches 4/4**. This is not a claim of superior general intelligence or of observed real-world value.

Note that the actual GRAFT source-selection fixtures are still predetermined by CANNON-093; MOTIF-004 does **not** autonomously generate them or search an open-ended source catalog. The question is field-agnostic, but the current donor workflow is not. That is an intentionally unresolved frontier.

## Run

Use the CI workflow for three read-only original GitHub source checkouts: `motif-original`, `graft-source`, `cannon-source`. Then:

```sh
mkdir -p evidence
python experiments/door-foundry-004/question.py --source motif-original --out evidence/motif-self-question.json

# The no-permission control must fail and leave no file:
python experiments/door-foundry-004/question.py --source motif-original --mode no-permissions --out evidence/unapproved.json

node cannon-source/experiments/cannon-graft-motif-001/review.mjs --graft graft-source --output evidence/cannon-generated-operator.json

python experiments/door-foundry-004/answer.py \
  --question evidence/motif-self-question.json \
  --cannon-receipt evidence/cannon-generated-operator.json \
  --graft-source graft-source \
  --motif-original motif-original \
  --build generated-motif-self-answer \
  --report evidence/motif-self-answer.json
```

GitHub Actions also runs the native-source, question-integrity, denial, forged-receipt, fair-baseline and runnable-build tests and saves the evidence and entire runnable local build as one artifact.

## What is not authorized

The question, source review and held generated code cannot authorize connections to people or accounts, new permissions, access to an arbitrary third-party host, production deployment, code changes to other repositories, canon promotion, or real action. Git hashes establish content identity rather than trusted human approval.

### Next falsifiable question

Can MOTIF choose a missing **operator family** rather than merely a missing numeric observation? It would need to (a) demonstrate a task that its present bounded grammar cannot represent, (b) request a source-owned GRAFT grammar extension, (c) let CANNON verify true source evolution, and (d) run a new heldout test against a **matched classical synthesis/search baseline**. That would be a meaningful next step beyond predeclared questions and predetermined synthetic field examples.

**Question posed ≠ source discovered ≠ operator admitted ≠ observed outcome.**
