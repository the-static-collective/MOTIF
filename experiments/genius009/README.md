# MOTIF-GENIUS-009 — THE TWO-CLOCK WEAVE

**RESEARCH HOLD.** The first actual experimentation beyond the GENIUS-008 atlas. Draft branch stacked on GENIUS-008; nothing merged into MOTIF main, connected to live MCP, or deployed to a Trench device.

## The strange crossing

**Enochic textual layers × Nolan's chronology/presentation distinction × Acaster's changed-meaning callback × Bacon's provenance critique × Aquinas's objection ledger.**

**Hypothesis:** later evidence may change how an earlier statement is *understood* without changing the earlier source's *literal testimony*. An intelligent investigator must sometimes maintain **two distinct temporal graphs** at once.

**Clock A — source time:** a statement is tied to the document or observation that actually supplies it. Later authors can reinterpret earlier sources, but cannot be silently credited as the earlier authors.

**Clock B — reader time:** evidence can arrive in a different order. A later revelation may give an earlier observation new meaning in the reader's model. Interpretations can change retrospectively even when the recorded provenance does not.

Established shoulders of giants include the **fabula/syuzhet** distinction between story chronology and presentation order (https://www-archiv.fdm.uni-hamburg.de/lhn/node/91.html) and **bitemporal/event-sourced** record keeping (a distinction between when a fact applies and when it was recorded; see https://link.springer.com/article/10.1007/s42488-026-00162-x). This particular experimental representation is an analogy rather than a faithful implementation of general bitemporal SQL semantics. It also resembles append-only provenance ledgers and literary source criticism. No historically new mathematical concept is claimed.

## Example: Enoch without collapsing textual history

The curated illustrative corpus holds three source-indexed statements:

- Genesis 5: Enoch walks with God.
- 1 Enoch: Enochic visionary material.
- 3 Enoch: the later Enoch–Metatron identification.

An interpretive edge says a later reader may reread Genesis' Enoch through the 3 Enoch Metatron tradition. This is a legitimate **later interpretive relation**, but it does not establish that the wording of Genesis 5 expressly makes that identification, nor that the respective traditions form an uninterrupted historical transmission. The code returns **HOLD_UNSUPPORTED_RETROJECTION** if the claim 'Enoch–Metatron identification' is ascribed directly to Genesis, while acknowledging that the later 3 Enoch example contains the identification in the illustrative source model.

The source layers are schematic indices, **not verified calendar dates** or a complete taxonomy of 1, 2 and 3 Enoch manuscripts. This simulator does not parse original language, examine manuscripts, prove theology, or authenticate the external sources. For sources and caveats see the GENIUS-008 ATLAS.md.

Now change the *reader's* exposure order:

    Genesis → 1 Enoch → 3 Enoch

versus

    3 Enoch → 1 Enoch → Genesis

The meaning-shift edge can become available at a different reader moment. **Its reader effect changes direction:** Genesis-first creates a genuine RETROSPECTIVE_CALLBACK, whereas 3-Enoch-first supplies ANTICIPATORY_CONTEXT for Genesis. Across six orderings, each situation occurs three times. **The source-owned meaning edge and literal historical record do not change.** That's how a retrospective callback can be useful without retroactively rewriting evidence.

## Beyond Enoch

The same code operates over two *other* hand-authored domains:

**Nolan/Acaster-style original fiction:** a blue key initially appears ordinary; a later scene reveals a shared cupboard. A later reading changes what the reader thinks the early key signifies, but does not add statements to the first scene.

**Hypothetical laboratory records:** a sensor reports 12, while a later calibration report finds a 3-unit offset. A later interpretation may suggest how to correct the original measurement, but the raw early recording stays '12'. A real laboratory would require units, calibration uncertainty, observation provenance and a measurement model; no empirically verified correction is asserted here.

## What we actually coded

`two_clocks.py` models distinct typed **Witness**, **Assertion**, **Reading**, and **Corpus** records. It validates that later interpretations cite a later actual source with an explicit proposition, refuse unauthorized cross-lane transfers, and preserve original source attribution. `compose_readings` takes any sequence in which a reader encounters those witnesses and exposes reinterpretations only once both ends have been disclosed. `check_attribution` answers a falsifiable source question and returns an objection/reply receipt if a later claim is incorrectly projected onto an earlier source.

**Counterfactual stress:** for each of the three domains, enumerate all 3! = **six** disclosure permutations. The expected source-claim ledger and final source-bound interpretation relation must remain invariant even when the timing and direction of reader interpretation changes. Exactly **three of six** disclosure permutations per corpus produce a retrospective callback and three provide anticipatory context. This yields **18 source-order trials**.

**Controls:**

- `naive_flatten` deliberately copies the claim supporting the later reinterpretation into the earlier source. It is an intentionally weak and incorrect comparison, not a serious historical method.
- `plain_append_only` is a **strong conventional baseline**: preserve each source's literal claims, never backdate them. It gets the provenance right without the interpretation graph.
- `compose_readings` adds a second interpretive clock on top of that classical source retention. It should **not** be described as outperforming the strong baseline on simple source correctness; its extra value is an inspectable temporal annotation mechanism.

**Failure cases:** future/earlier relation with inverted source layers, unsupported post hoc reinterpretation, wrong epistemic lane, repeated/missing witness IDs, omitted or replayed reading disclosures, and invented assertions are rejected. A later source must not overwrite an earlier one.

## How to reproduce

From the MOTIF checkout of the experiment branch:

```sh
python -m unittest discover -s experiments/genius009 -p 'test_*.py' -v
python experiments/genius009/two_clocks.py > /tmp/motif-genius009-two-clocks.json
python -m json.tool /tmp/motif-genius009-two-clocks.json >/dev/null
```

Scoped GitHub Actions runs the tests and archives the full synthetic receipts.

## Open research frontier

1. Replace manually curated source statements with independently prepared, accurately transcribed and attributed passages, preferably with version/witness identifiers and explicit translation uncertainty.
2. Compare with real event-sourcing/bitemporal graph systems, not only a deliberately bad flatten baseline.
3. Challenge with an unknown original fiction that contains ambiguous callbacks, misdirection and several contradictory character perspectives; measure reader interpretations independently instead of rewarding a hand-coded 'callback detected' marker.
4. Test whether automatically choosing to reinterpret actually improves future forecasting, source retrieval, practical decisions or verifiable predictions, rather than merely generating an interesting graph.
5. Route such temporal/citation work alongside the remaining GENIUS-008 operators: conscience/neighbor reframing, participation/accessibility, multiteam coordination and multi-period musical structure. Preserve incompatible evidence lanes, source custody and authorization.

**Result to seek:** simultaneously achieve *flexible understanding* and *immutable evidence provenance*. Meaning may change without the recorded witness changing. That is a classical idea worth making first-class in MOTIF's reasoning artifacts, not a proof of new mathematics or autonomous genius.