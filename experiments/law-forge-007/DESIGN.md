# LAW-FORGE-007 — CLASSICAL LOOKUP ASSIMILATION
## Preserve what is known; compress what is explainable; refuse what is unmeasured

**Research question:** Can MOTIF assimilate the strongest classical exact lookup method as an executable, first-class, provenance-bound skill *without losing* its previous ability to propose compact explanatory instruments?

**Short answer to test:** A revision-pinned exact lookup should be the authority for predictions on *already measured configurations*; a bounded sensor program may represent the same table when exactly equivalent, with a small explicit correction ledger. No inference is licensed on configurations not observed or on changed source revisions.

This is an experimental branch stacked on LAW-FORGE-006 PR #67, itself draft. It is **not merged or deployed**.

## What is new

006 constructed monotone read-only sensors from six source-owned link reads, but **refused** legitimate nonlinear rules that it could not express. A complete classical lookup table had **better review coverage** (55/65) than the proposed short-sensor grammar (35/65). Instead of hiding the stronger baseline, 007 **makes it part of MOTIF's usable operator repertoire**.

Its new interpreter supports:

- A typed **source capability contract** with the actual source identity, revision and named channels; arity 1–8, not only six bits.
- **Exact classical lookup** for every witnessed binary configuration, including parity or other functions that the bounded DNF vocabulary cannot express.
- An optional **compact, interpretable instrument**, synthesized from the full source table using the previous experiment's real `inventor.Instrument` implementation. Up to **three exact exception cells** may patch an almost-correct short instrument. Every prediction is checked against the authoritative snapshot.
- A deterministic **description-complexity selection**: only choose a compact program if its declared code/exception cost is below the cost of the full truth table. This is a rough, predeclared *description unit*, **not hardware energy, latency or implementation cost**.
- A source-bound `motif.law-forge.lookup-skill.v1` cartridge with content-addressed snapshots, strict schema and clear `PROPOSAL_ONLY` authority.
- A local **JSON-stdio research desk** with `assimilate` and `predict` commands. It refuses malformed, privileged, unrelated or changed-source requests. It makes classical lookup an executable capability for another suitably scoped caller, not a loose result description.

Its key rule is simple:

```text
new source contract
    |
source-owned observations
    |
 exact classical table
    |
 +-- incomplete source domain --> RAW_LOOKUP of only witnessed cells
 |                                  HOLD every unobserved input
 |
 +-- complete source domain --> attempt bounded six-link sensor synthesis
                                  |
                          exact simple program? --> COMPACT_EXACT
                                  |
                  nearly exact (<=3 corrections)? --> COMPACT_WITH_EXCEPTIONS
                                  |
                       otherwise --> RAW_LOOKUP
                                  |
                independent source review
                     /                  \
                falsified              eligible
                    |                     |
                   HOLD            prediction-only proposal
                                          |
                      destination must independently re-review
```

In all cases, an input not present in the source snapshot returns `HOLD_UNOBSERVED_CONFIGURATION`. A changed source revision returns `HOLD_SOURCE_CONTRACT_CHANGED`. Neither a symbol like `UNKNOWN` nor a third/trinary truth value is mistaken for an observed binary outcome.

**Integrity boundary:** Source SHA-256 receipts establish byte consistency, not actual identity, consent or truth. A caller may hold a signed/verified source contract separately; this experiment does not invent authentication.

## New unfamiliar source contracts

The researcher module `lookup.py` is source-separated from the hidden simulator `source.py`. The latter introduces a **seven-channel** contract that 006's hardcoded six-link DNF cannot directly handle. 007 safely falls back to exact classical lookup while acknowledging that it has not invented a seven-input compiled formula.

One deliberately authored six-link world behaves like a normal three-path reachability detector **except for one special configuration**. Here the synthesizer can propose the short path instrument **plus a single explicitly observed correction**, and can validate that hybrid against the *entire* original table. This demonstrates an actual way to combine classical lookup and instrument construction.

Other tasks involve parity, exactly-one-path conditions, source revision shifts and deliberately changing test environments. They are intended to produce raw lookup or HOLD.

All 13 challenge families are researcher-authored; seed splits vary simulation instances, not independently invented scientific domains. Review/test phases exercise the same exhaustive finite inputs under independently generated outcomes. This does not prove out-of-domain generalization.

## Strong controls

Every method gets the **same** complete training truth table (64 configurations for six channels, 128 for seven), except the deliberate incomplete-data negative control.

1. `assimilated_hybrid` — complete classical lookup with optional checked exact compression and a small correction ledger.
2. `classical_full_lookup` — strong unconstrained exact lookup control, no compression.
3. `old_four_channel_only` — prior limited observational interface, projected onto four channels.
4. `partial_unobserved` — receives only half the source configurations; any unobserved request must HOLD, and independent review may not certify a complete domain.

**Accuracy expectation:** Hybrid and complete lookup should **tie** wherever the source is stationary. Any claim of accuracy superiority would be invalid. The hybrid's distinctive deliverable is a portable verified program when shorter, transparent exception handling, strict interface/version handling, and the ability to preserve exact knowledge when symbolic grammar fails.

A frozen nonpromotion rule demands >=2 more review-eligible development worlds than full classical lookup with no extra test errors. A tie results in `NO_METHOD_PROMOTION`. No CI success, method selection or downstream write grants real-world authority.

## Output: a callable executable skill

All messages are strict JSON via:

```bash
python experiments/law-forge-007/desk.py < request.json
```

For `assimilate`, input shape:

```json
{
  "schema": "motif.law-forge.lookup-desk.v1",
  "action": "assimilate",
  "contract": {
    "schema": "motif.law-forge.lookup-source.v1",
    "source": "synthetic-unfamiliar-source-pack",
    "revision": "source-rev-1",
    "channels": ["channel_0", "channel_1"],
    "allowed_operation": "LOCAL_BINARY_READ_ONLY",
    "real_world_authority": false
  },
  "observations": [
    {"inputs":[0,0],"outcome":0,"contract_id":"<computed SHA256 contract id>","provenance":"SYNTHETIC_SOURCE_OBSERVATION"}
  ]
}
```

For `predict`, pass the resulting `cartridge`, the **currently presented** source contract and an exact `controls` vector. Only previously observed source settings can return `SUPPORTED_SYNTHETIC_SNAPSHOT`. Every other case returns HOLD or REFUSE, never a guessed value or external action.

Do not treat the short example above as an independently witnessed observation: it is a shape illustration, and the contract SHA is a placeholder that must be computed from the real input packet. Complete reproducible cartridges are saved in the CI artifact.

## Source-owned integration status

This 007 experiment **reuses** the original native `inventor.Instrument` and `generated_programs()` from 006 rather than rewriting that skill. It does not modify 006. The original cross-project native Dogram `ablate@1` verification from 006 remains independently evidenced on its dedicated CI run. 007 does **not** add native ALEX storage, GRAFT compilation, cloud source browsing, real source authentication or autonomous deployed adapter creation.

Potential handoff into JAR;VIS, GRAFT, ALEX and Dogram can use the strict skill packet and revision-mismatch behavior, but each owning project must separately approve its integration. No automatic adapter grant is inferred.

## Verify

```sh
python -m unittest discover -s experiments/law-forge-007 -p 'test_*.py' -v
python experiments/law-forge-007/trial.py > law-forge-007-results.json
python -m json.tool law-forge-007-results.json > /dev/null
```

GitHub Actions additionally exercises inherited experiments 001–006, prints the heldout classical comparisons, emits a sample portable skill cartridge, and preserves all receipts for 30 days. **Do not claim measured pass counts or benchmark results before checking the actual CI evidence.**

## Next falsifier

Do not simply enumerate larger truth tables and call it intelligence. Require a previously unseen, source-owner-authenticated capability schema and a domain too large to exhaustively sample. Ask whether MOTIF can construct a *cost-effective discriminating question* and prove limited generalization with a formally specified confidence/abstention contract. Integrate genuine GRAFT and ALEX runtime validators **only after** source-owned schema and real permissions have been audited. Report negative results instead of expanding training after seeing heldout labels.
