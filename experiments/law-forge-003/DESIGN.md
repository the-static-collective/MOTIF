# LAW-FORGE-003 — THE OPERATOR FOUNDRY

## What happens when no previously supplied named operator can express the phenomenon?

**Hypothesis:** Given only primitive two-input **NAND** semantics, a bounded program synthesizer can discover and construct an executable, reusable operator circuit from examples, choose an inexpensive discriminating inquiry, and transfer a resulting **prediction-only** netlist to sequences longer than any used in training—while withholding false discoveries.

**Scientific status:** A source-separated **synthetic** experiment, not discovery of new mathematics, general autonomous scientific intelligence, physical causality, or unrestricted self-programming. This is a stacked draft on LAW-FORGE-002 (PR #58), itself stacked on LAW-FORGE-001 (PR #57).

### The important new boundary

LAW-FORGE-002 supplied an AST with named `AND`, `OR`, and `XOR` operations and asked the learner to compose them.

**LAW-FORGE-003 removes those named compound operations from the synthesizer's executable grammar.** Its sole logic instruction is `NAND(previous_wire_i, previous_wire_j)`, with a maximum of four gates. It searches every acyclic NAND wiring diagram up to that depth; signatures are **computed from execution on the four possible two-bit inputs**, not retrieved from a labeled XOR/OR catalogue. It keeps the shortest implementation of each behavior.

It can then emit an inspectable **JSON NAND netlist**, including each gate's indices, a checksum, and strict `PROPOSAL_ONLY` status, which the read-only local interpreter can actually execute.

A separate, **pre-supplied left-fold** uses the synthesized binary operator on variable-length binary sequences. The learner is not discovering the fold mechanism itself. This is the crucial honest limit: NAND and folding were already implemented; the particular circuit connections are synthesized.

```text
              seven typed source observations
                          |
          enumerate NAND circuits (0..4 gates)
                          |
            predict each observation by fold
                          |
           two different circuits still fit?
                |                      |
                NO                     YES
                |                      |
          propose operator       propose one local probe
                                       |
                              independent evaluator acts
                                       |
                              re-fit circuit signatures
                                       |
                    single candidate or HOLD_UNIDENTIFIED
                                       |
                          independent full-range review
                                /              \
                        FALSIFIED            ELIGIBLE
                           |                   |
                          HOLD        PREDICT_ONLY_PENDING_HUMAN_REVIEW
                                               |
                                    new destination must re-review
```

### What the worlds demand

The hidden evaluator has seven procedural mechanisms, with seeds that change the review/test examples, not the mathematical families.

| Evaluator-only hidden family | Intended falsification |
| --- | --- |
| Parity over arbitrary binary sequence | NAND-synthesized XOR, a four-gate network, supports unseen lengths. |
| Any-bit-on | NAND-synthesized OR, a three-gate network, supports unseen lengths. |
| All-bits-on | NAND-synthesized AND, a two-gate network, supports unseen lengths. |
| Exactly one bit set | A two-bit XOR proxy fails independent three-bit cases. HOLD. |
| Strict majority | A two-bit AND proxy fails independent three-bit cases. HOLD. |
| Hidden width effect | A two-bit XOR proxy fails on a length-4/5 interaction. HOLD. |
| Deliberate phase shift | The inquiry mechanism differs from independent review. HOLD. |

Initial training includes `00`, `01`, `10` and four three-bit examples. The `11` pair is withheld, so parity and any-bit-on are indistinguishable from the initial two-bit evidence. A scientist may propose that pair as an information-gain question, but **only the independent evaluator** executes it. Each method gets at most **one** query, at declared synthetic cost 3, with allowed/prohibited filtering.

Review requires independent two-bit and three-bit exhaustive coverage, additional lengths 4–11, at least 32 typed examples, and explicit falsifiers. Only proposals surviving that review are tested on a wholly separate held-out partition. Transfer carries neither identity nor permission; a renamed destination must review again.

### Competitors and method governance

Three predeclared methods receive exactly the same information, probe budget and review evidence:

1. `nand_adaptive`: synthesize NAND-only circuits; choose a maximum-entropy-per-cost query.
2. `nand_fixed`: synthesize the same NAND circuits; use a strong fixed query `11`.
3. `table_fixed`: a **strong classical control** directly enumerates binary truth tables (no NAND gate synthesis), uses the same fixed query and the same supplied left-fold.

If adaptive discovery ties the classical truth-table method, report a tie—not novel algorithmic superiority. A fixed development-stage review criterion refuses method promotion unless NAND adaptive has at least two more review-eligible development worlds, no additional wrong covered predictions, and no higher declared inquiry cost. It is only a *proposed review* if that criterion passes; it cannot change any live method.

Development seeds 0–1 and final evaluation seeds 2–6 never overlap. Review and test results cannot mutate the original candidate hypothesis search. All output packets reject privileged fields, arbitrary code, malformed gate indices, tampered IDs or external endpoints.

### Executable reproduction

Python 3.10+, standard library only; no third-party dependencies, cloud inference, token costs or network actions:

```bash
python -m unittest discover -s experiments/law-forge-003 -p 'test_*.py' -v
python experiments/law-forge-003/trial.py > law-forge-003-results.json
python -m json.tool law-forge-003-results.json > /dev/null
```

The dedicated GitHub Actions workflow additionally runs both inherited Law Forge suites and stores an inspectable JSON benchmark artifact with the actual gate-level netlist for a proposed XOR operator. **Do not claim test success or benchmark outcomes before inspecting that workflow.**

### What is and is not invented

**Actually constructed:** A bounded two-input NAND gate circuit with wiring derived from input/output evidence. Its binary behavior can be reused on untrained longer sequences through a predeclared fold interpreter.

**Not invented:** NAND, the Boolean truth-table space, the left-fold recursion operator, the meaning of parity, new hardware, new sensory modalities, real-world causal laws, an unrestricted language compiler, or the verification policy. A fixed exhaustive truth-table algorithm may perform just as well.

**New question beyond this experiment:** Can the machine generate a NEW inductive structure (e.g., delay, relation, memory channel, variable arity or graph grammar), not merely a new circuit over a known fixed two-input interface, and survive an independently authored out-of-family evaluation? That requires a frozen learner, an external challenger, and a real method comparison; changing the hidden world to make the model look good would invalidate the result.

**Authority boundary:** This is an offline, typed synthetic experiment. No GRAFT integration has been shipped, and no operator cartridge may execute in another project without that project's explicit policy, source verification and human review.
