# LAW-FORGE-004 — THE GRAMMAR BREAKER

## Can MOTIF construct a new *stateful* computational operator when a stateless fold language fails?

**Research claim to test:** On synthetic binary event streams, a learner that can previously describe only a one-bit accumulator folded through a binary truth table recognizes when this cannot fit observations; it then proposes a bounded membership experiment and constructs an executable **finite-state memory machine**. Independently withheld long streams must confirm or falsify its predictions.

**Status:** Source-separated, standard-library experimental stack. Stacked on LAW-FORGE-003 draft PR #60, not merged. No physical probes, arbitrary code creation, or automatic authorization.

### The difference from 003

LAW-FORGE-003 searched programs made from up to four NAND gates. Its outputs were combined over a stream by an externally **predeclared one-bit left fold**. It could synthesize XOR or OR, but the language could not separately remember a recent history *and* produce an output.

004 constructs an entirely different **operator representation**:
- A finite set of inferred states (bounded at four), with an inferred output bit in each state.
- Two inferred transitions per state, one for each event symbol.
- A chosen reset state and an executable `trace(sequence)` operation.
- Source evidence digest and an inspectable JSON `PROPOSAL_ONLY` machine packet.

This changes computational expressivity within our controlled research environment. It is not an invention of finite-state automata, the Myhill–Nerode theorem, or a new computational primitive: **the generic finite-state transition interpreter, maximum state capacity, and membership-query protocol are supplied**.

### Distinguishing future histories, not naming causes

The learner sees only opaque words and binary observations; `machine.py` never imports `world.py`.

It initially receives all 31 membership observations for binary words of length 0–4.

It searches all 16 one-bit binary folds, starting each nonempty sequence at its first bit. If one fits, the simplest representation is retained: **no new memory and no extra probes**.

If none fits, it may request the remaining **224** membership observations for all binary words up to length seven. These are explicit typed, local synthetic-only queries, not network calls. The evaluator alone executes the membership batch, under a nonnegative integer query budget. If not permitted, the learner HOLDS.

It then builds a classical finite observation table:
- Candidate history prefixes up to length three.
- Future distinguishing suffixes up to length three.
- Two histories are distinguished when some actually witnessed suffix produces different outcomes.
- Each distinct residual signature becomes a provisional state; successor signatures become its transitions.
- If the table cannot close, disagrees, has contradictory witnesses, or requires more than four states, HOLD.
- Verify the entire inferred machine against every training observation, and preserve each pair's measured distinguishing continuation.

For an example 3-state pattern detector, the system may discover that "the last bit was zero" and "the stream has just ended with zero-one" are distinct operational states, without receiving the target pattern label from its model input. The resulting machine **executes** on arbitrary permitted binary streams up to 12 symbols; independent review is a separate matter.

### Eight secret, evaluator-owned world families

| World family (known ONLY to evaluator) | Intended correct outcome |
| --- | --- |
| Parity | Existing one-bit XOR fold is sufficient; retain it without expansion |
| Any bit on | Existing one-bit OR fold is sufficient; retain |
| Ends with 01 | Infer 3-state history program; review |
| Ends with 001 | Infer 4-state history program; review |
| Contains 101 | Infer 4-state program; review |
| Ends with 0001 | Requires 5 states; HOLD the four-state ceiling |
| Prime number of ones | Counterexample to this small bounded representation; do not claim discovery |
| Deliberate review-phase shift | Training looks stationary; independently sampled review uses a different rule; HOLD |

Review uses a separately generated dataset of long streams (lengths 8–11) and must contain at least 64 typed observations across those lengths. Test streams are sampled with a different seed and kept out of training and review. A separate destination, even with renamed inputs and same mechanism, must re-review. Cross-mechanism reuse must be refused.

The family names and exact transition rules are never passed to the learner. The worlds are nonetheless manually authored and finite; changing seeds does not create independently authored domains.

### Predeclared competing methods

All get identical 31 initial observations. Controls:

- `scalar_only` — classic 16-table one-bit fold. When inadequate, HOLD.
- `stateful_upgrade` — gate on scalar inconsistency; request missing examples and build a stateful program.
- `classical_gated` — **strong classical baseline** using the *same* gated classical observation-table learner; expected to tie our proposed method.
- `classical_full` — always request the complete table, including cases where a simpler fold suffices.

Development: eight families × seeds 0–1; final evaluation: eight families × unseen seeds 2–6. Method promotion requires at least two more review-eligible worlds than `classical_gated`, no more covered errors, and no additional probe cost. A tie produces `NO_METHOD_PROMOTION`. No policy can actually promote itself.

**Costs:** initial 31 observations, optional 224 requested extra synthetic measurements (255 total), no paid model or external API use. This is a simple *batch protocol*, not a claim of optimal active experiment selection.

### Reproduction

Python 3.10+, no dependencies:

```bash
python -m unittest discover -s experiments/law-forge-004 -p 'test_*.py' -v
python experiments/law-forge-004/trial.py > law-forge-004-results.json
python -m json.tool law-forge-004-results.json > /dev/null
```

Dedicated GitHub Actions checks inherited 001–003 experiments, runs 004's adversarial tests, emits measured comparisons and preserves the complete JSON receipt as an artifact for 30 days.

### Crucial nonclaims

This is **classical finite automata identification**, not new computer science, consciousness or open-ended scientific intelligence. The "new language" is new to the experimental learner's *available representation*, not newly invented by humanity. We supply the generic finite-state interpreter, the binary sensor interface and the horizon. No mathematical proof of out-of-family generalization, autonomous API discovery, persistent deployment, GRAFT or Plan Z integration, authenticated human consent, or safety-critical causal knowledge is established. An evidence digest is content identification, **not a source signature**.

### The harder falsifier beyond 004

Freeze the state-machine interpreter and challenge the learner with an independently authored process containing unbounded counting, physical time, changing topology, or relational data absent from the current binary word interface. Can it propose an additional *computational substrate* or sensor representation, rather than enumerating more states, and demonstrate transfer? Treat lack of such an invention as a valid negative result.
