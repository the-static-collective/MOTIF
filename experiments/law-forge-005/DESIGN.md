# LAW-FORGE-005 — WORLD BREAKER
## A baseless human thought: maybe *trinary*? Let evidence decide.

**Research prompt:** Given a binary event-stream reasoner (LAW-FORGE-004), can the next experiment test whether a different *observational language* is actually useful—without elevating base three, three-valued logic, or any human intuition to a privileged description of reality?

**Hypothesis status:** **SPECULATIVE / UNPROVEN.** `0,1,2` is an optional categorical encoding, not an ontological statement. Its appropriate use depends on the observed task, source, costs, and available alternatives. The implementation deliberately allows ternary to lose, and measures a cost-assumption reversal.

## The distinct new boundary

LAW-FORGE-004 learned bounded state machines over a binary sequence. A bigger automaton cannot help if the observation itself discards which objects relate to each other. Here the evaluator owns an invented four-edge relational graph (two possible source→relay→target paths). The learner does **not import the evaluator's hidden world**. Instead, a finite sensor-program grammar can propose one of several ways to *read* the graph:

- **Binary edge:** is one specific edge present?
- **Binary pair:** retain the identities of two observed edges.
- **Ternary count of two edges:** `0/1/2` edges present; this discards which edge was present when count is 1.
- **Binary relational reachability:** does either two-hop path connect source and target?
- **Ternary path count:** `0/1/2` distinct two-hop paths exist.
- **Binary path pair:** which of two paths exists, preserving identity.
- **Full four-bit graph:** strong classical information-complete control.

`Sensor` is a strict data-only AST. The evaluator-owned `world.py` supplies a **predeclared** and read-only compiler for those sensor expressions; **MOTIF does not invent the primitives, author arbitrary sensor software, or access a live network or external source.** All competing sensor outputs are supplied on the same toy observations. Consequently this is **representation selection on a fixed measurement panel**, not independent hardware sensor discovery, capability invention, or actual instrument acquisition.

The explicit baseline is the complete binary/raw graph view. If a ternary view also succeeds, that shows a potentially compact categorical representation—not a new empirical truth unavailable to binary encoding.

## Cost assumptions matter, and we test that

For sensor ranking we predeclare the number of raw edges read first, then **ideal symbolic capacity** `log2(number_of_sensor_symbols)` (with deterministic rounding), then a binary-preferred complexity tie-breaker. Thus a three-category view has ideal 1.585 bits of state capacity, while a binary pair has 2. This is **not** actual storage cost, sensor price, computation, latency, or physical Joules.

A second independent scoring rule replaces ideal capacity by `ceil(log2(symbol_count))`: a three-category view now takes two binary bits, the same as a two-bit pair. This ablation explicitly tests whether the preferred ternary representation disappears when the arbitrary coding-cost advantage disappears.

No method automatically promotes the ternary hypothesis unless a predeclared development test shows at least two extra correctly reviewed worlds versus the binary-only menu without additional covered errors. A tie is `NO_TERNARY_PRIVILEGE`.

## Ten researcher-authored secret graph mechanisms

| Evaluator-only world | Good representation / expected challenge |
| --- | --- |
| Presence of first edge | One binary bit suffices; ternary unjustified |
| Exactly one first-hop neighbor | Ternary count may be compact, binary pair equally accurate |
| First neighbor only | Binary pair must retain identity; ternary count loses it |
| Any two-hop route | Single graph reachability bit is sufficient |
| Exactly one route | Ternary count may describe the question compactly |
| Both routes | Ternary count may be compact, binary pair equally accurate |
| First route only | Binary path pair retains identity, ternary count fails |
| Parity of all four edges | Full binary graph needed under this tiny supplied menu |
| Apparent reachability that shifts between phases | Independent review must HOLD |
| Apparently identical reachability with unseen evaluation context | Independent review must HOLD |

The source generates eight initial graph cases (one edge fixed absent), then the learner may request the other eight using strict local graph-probe packets under a budget of eight. Each method receives the same resulting **full 16-combination panel** before choosing a sensor. Because we exhaust the small source domain, no superiority of smart/active probing is claimed. Evaluation uses 16 graph settings repeated in two evaluator-controlled snapshots per review and test; **this is not 32 independent real-world cases**, and review/test repeat graph configurations rather than introducing new domain families.

The reviewer requires all 16 graph configurations and two differently tokened snapshots per setting. Even then, token uniqueness and a SHA-256 checksum are *not* real-source authentication; they only validate synthetic fixture bookkeeping.

## Four predeclared competitors

| Method | Available sensors | Purpose |
| --- | --- | --- |
| `all` | Binary, ternary, pair and relational readouts | Unbiased candidate selection via declared score |
| `binary` | All **nonternary** variants including pair/path/raw | Strong no-base-3 control |
| `ternary` | Only ternary count views | Give the trinary conjecture a chance to fail |
| `full_raw` | Four raw binary edge values | Full-information classical baseline |

For each source, fit a deterministic sensor-value→binary-outcome mapping. Reject sensor candidates contradicted by a single observed class collision. Among surviving candidates, select minimum declared cost. Do not use independent-review labels to change the sensor or promotion rule. Separate evaluation seeds 2–6 from development 0–1.

Any discovered view exports a checksummed **prediction-only proposal**, not permission. A destination with renamed graph roles must review afresh; a destination world with a different rule may refuse. Unobserved or changing context is a designed **failure** of the sensor model.

## Reproduce

Python 3.10+, standard library, no paid models or network:

```sh
python -m unittest discover -s experiments/law-forge-005 -p 'test_*.py' -v
python experiments/law-forge-005/trial.py > law-forge-005-results.json
python -m json.tool law-forge-005-results.json > /dev/null
```

Dedicated GitHub Actions checks all inherited Law Forge suites (001–004), runs 005's adversarial tests, stores benchmark JSON and prints the cost-ablation and method decisions. Numerical claims must be grounded in successful actual CI receipts, not projected expectations.

## What this experiment does NOT establish

Ternary fundamentalism; objectively superior base-three computers; new human or machine consciousness; independent discovery of a sensor primitive; real graph-field perception; live GRAFT/Plan Z/ALEX/Dogram integration; verified physical costs; general causal identification; autonomous self-extension; permissions to survey people's resources, services, or private data.

**Next credible step:** Change the readout grammar from a hand-authored menu into *source-contracted, bounded adapter proposals* whose observational affordances are tested by an independent source owner. Challenge it with unseen graph arities and hidden relation types. Keep trinary, binary, n-ary and graph encodings as rival hypotheses with explicit error/cost/permission accounting. A previously unimplemented sensor primitive must be evaluated without letting the learner modify the evaluator or rewrite the test after seeing holdouts.
