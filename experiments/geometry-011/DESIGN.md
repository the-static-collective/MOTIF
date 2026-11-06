# MOTIF-GEOM-011 — THE MISSING DIMENSION

**Status:** executable isolated, synthetic, read-only reasoning research, stacked on open GEOM-010. Python 3.11+ standard library. PENCIL-only. No independent source verification or outside observations performed.

## Question

When two cases appear identical under MOTIF's current representation but have opposing declared labels, can MOTIF detect the representational deficiency, propose a *permitted* observational distinction, and compose a more expressive operator that explains the supplied examples—without hallucinating values for unseen facts?

GEOM-010 already returns `UNRESOLVABLE_IN_OBSERVED_VOCABULARY` for exactly colliding cases. GEOM-011 deliberately starts **there**, not with another search over the same insufficient conjunctions.

### The distinction: a new *description* is not a new *observation*

- **Critic:** group by supplied `(before, after, visible facts)`. Opposing label groups produce a two-case impossibility witness for any deterministic rule using *only* that visible signature. This is conditional on unverified synthetic labels, **not** evidence that a real hidden cause exists.
- **Probe planner:** only examines explicitly listed and **declared-permitted/available** candidate sensors. Scores entropy change using recorded *development PILOT* data, not guessed sensor measurements. No pilot → HOLD; no permission → HOLD. Outputs `PROPOSED_ONLY`, never invokes a sensor.
- **Inventor:** enumerates explicit small Boolean operator templates (`IDENTITY`, `NOT`, `AND`, `OR`, `XOR`, `XNOR`, `NAND`, `NOR`) on up to two binary pilot signals and applies the resulting *guard* to the existing `bud → branch` rewrite. The first complete development fit in declared arity and lexicographic enumeration is a revisable **PENCIL** cartridge.
- **Evaluator:** after choosing the cartridge from development data, evaluate on different case IDs with newly supplied heldout readings. If a required value is missing, return an **abstention** (`None`), not an asserted outcome. No automatic THOUGHT-006 PEN admission or GEOM-008 graph grammar replacement.
- **Archive:** optional read-only-on-meaning SQLite append to GEOM-008's existing `LivingGraph` via a revalidated PENCIL proposal node and N-ary case/reading witness relation. Recomputes development selection and rejects forged scores and scope mismatch. Sources are mere declared strings.

### No fixed *graph* ceiling is reintroduced

The finite **operator search arity 1–2** is the *experimental reasoning-vocabulary bound*, not a bound on the free graph's nodes, edges or depth. GEOM-008/009's persistent, arbitrarily large synthetic hypergraphs remain available. Extending this lab to higher-arity operators would increase search cost exponentially, requiring a persisted candidate frontier rather than eager enumeration. Compute remains physically finite even with large requested work budgets.

## The key synthetic counterexample

Six arbitrary plant-name contexts share identical visible `growth=bud` and `period=spring` within each named plant. For each, four supplied synthetic situations have two separately pilot-recorded binary signals and declared outcome `signal-a XOR signal-b`.

```
         A     B    labeled bud→branch
         0     0    false
         0     1    true
         1     0    true
         1     1    false
```

Each signal **alone has zero training information gain** about the declared label; together their tuple yields **1 bit**, and the inventor selects `XOR`. A previously unavailable derived dimension is expressible from the *recorded* joint values. This is an elementary classical feature-construction task, **not** autonomous discovery of a physical sensor, causal variable or novel mathematics.

The intentionally cheap `forbidden-leak` sensor records the exact answer in synthetic pilot data but is declared unpermitted. It cannot be selected even though it would improve fit. A declared but unmeasured `missing-sensor` cannot be scored. A declared unavailable sensor cannot be used. These are **synthetic policy flags**, not external account authorization.

## Results and controls

See `experiment-results.json`, `benchmark-results.json`, tests and strict machine JSON input.

| Question | Observed result |
|---|---|
| Identical visible inputs with opposite declared outcomes | Six contradiction witnesses (one per original plant) |
| Gain per individual candidate signal | 0 bits each |
| Joint A+B gain | 1 bit pilot information gain; 1 bit synergy over best single |
| Synthesized rule | `bud → branch IF XOR(signal-a, signal-b)` |
| Development | 24 correct / 24, no incorrect predictions |
| Different-name heldout | 240 correct / 260, 0 incorrect, **20 missing-reading abstentions** |
| Classical full two-sensor truth-table baseline | **Tied**: 240 correct, 0 incorrect, 20 abstained |
| Visible-only always-false baseline | 130 / 260 correct; no missing-value abstentions |

The heldout generator is written by us using the same fixed XOR law; this is **not a genuinely external frozen dataset**, so claims of independent scientific generalization would be unjustified. The system is matching classical finite Boolean learning, not surpassing it. A standard depth-two decision tree could learn the same XOR.

### Guardrails and falsifiers

- Source roots are declarations; two strings do not establish independence. Results remain **PENCIL / authority NONE**.
- Even a plausible candidate *sensor name* cannot be automatically measured. The pilot table is a fixture from the caller, not something the reasoner gathered.
- An unresolved collision after all permitted/piloted features produces **HOLD**, not a newly imagined variable.
- Scope strings (observer/time/decoder) must be exactly equal. This does not implement 3rdi's real observer cuts or LOADOUT's permissions.
- No internet, camera, microphone, private files, shell, background process, GitHub mutation or real-world experiment execution inside the lab.
- The full source/heldout partition must be externally frozen before making stronger generalization claims.
- An operator search only covers the listed two-signal Boolean functions; it does not synthesize arbitrary new algorithms or sensor hardware. Candidate catalog construction is still eager, not memory-bounded for enormous sensor catalogs.
- **Independent test to run next:** blind, preregistered cases with nuisance correlation shift, noisy/false pilot labels, unreliable claimed roots and missing sensors, against full classical decision-tree, program-synthesis and information-gain baselines. Evaluate downstream decision utility, calibrated abstention and source-leakage errors, not visual appeal.

## Source lineage / review stack

- GEOM-010: Critic's indistinguishable-label conflict and guarded grammar refinement.
- GEOM-009: single-span symbolic rule induction and isolated graph forks.
- GEOM-008: persistent, arbitrary-structure PENCIL hypergraph; optional append-only cartridge witness.
- GEOM-007: representation-blindness concept and cost-aware question planning.
- GEOM-006: observer-specific knowledge cuts and historical edge access.
- Project owners **not integrated**: 3rdi (actual observer views), ALEX (documentary provenance), Free Graph (relational history), LOADOUT (capability boundaries), THOUGHT-006 (revisable PEN commitments), MOTIF/Plan Z (operational routing).

This branch is stacked on GEOM-010, which itself is **not merged into `main`**. Review dependencies before merging. Do not present isolated synthetic evidence as deployment or verified autonomous cognition.

## Reproduce

```bash
cd experiments/geometry-011
python3 -m unittest -v test_missing_dimension.py
python3 demo.py
python3 benchmark.py
python3 interface.py example-input.json
```

The JSON CLI caps input at 2 MB; that is an interface safety bound, not a graph-size bound. GEOM-011 does **not** repeat GEOM-009's 10^15-requested-work synthetic graph stress, because larger graph size cannot independently provide missing sensor readings.

**Principle:** A contradiction can justify **asking for a distinction**; it cannot justify inventing the distinguishing fact. The new lens may reveal a question. Only additional attributable measurements can support an answer.
