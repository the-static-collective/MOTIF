# MOTIF RING-012 — Ambiguity as the Native Representation

**Experimental premise:** Language should not require a single forced interpretation. A source phrase can support multiple incompatible perspectives, one reading with additional unmodeled possibilities, or no sufficiently grounded reading. **Ambiguity is ordinary information**, not an error automatically resolved by choosing the most popular guess.

**Status:** source-authored executable research experiment, stacked on RING-011. No outside actions, production deployments, program/connector admissions or automatic merges. None of the algorithms authenticates real events or the intentions of a human speaker.

## Why this was needed

RING-011 derived 119 contextual rules and nine semantic rewrites but produced **16 false outer-root action readings** on its 288 authored cases and performed worse than its classical controls. Simply adding more relations and aggressively choosing a single graph did not solve perspective ownership.

RING-012 takes a different approach. Even a confident-looking reading remains **an untrusted possibility** with an explicit open-world remainder.

The user's private Google Drive *How to Live* inspired the general distinction between a narrator's voice, nested quotations, imagined events, recollections, and documentary carriers (SONG vs NOTE vs MEMORY vs RECORD). **No book passages, personal details, prior chat quotations, or raw private text were copied into this public GitHub experiment.** All test language, source-bound entities, and acceptable interpretations are freshly authored synthetic examples.

## An actual set-valued language output

The runtime does not return a single event claim or imperative. It returns an **ambiguity lattice**:

```text
  ORIGINAL UTTERANCE + EXPLICIT SOURCE EVENT + DOCUMENT CARRIER
                               |
                        THREE MODEL VIEWS
             ┌─────────────────┼─────────────────┐
             ▼                 ▼                 ▼
         RING-011          Same-data          Same-data
      inferred binder      word Bayes       word+bigram Bayes
             └─────────────────┼─────────────────┘
                               ▼
                   retain raw method claims
                     and disagreements
                               |
                         OPEN-WORLD LATTICE
          ┌────────────────────┼─────────────────────┐
          ▼                    ▼                     ▼
    plausible reading A  incompatible reading B   OTHER / NOT MODELED
          │                    │                     │
          └────────────────────┼─────────────────────┘
                               ▼
             source-conditioned meaning possibilities
             WITHOUT external-action authorization
```

The three source methods are **correlated**, because they use the same author-generated training examples. Their agreement never counts as three independent witnesses.

Each supported interpretation is a typed graph with ROOT FORCE, EVENT SCOPE and POLARITY; the source-provided speaker/agent roles determine potential voice ownership. Each also retains the originally supplied SONG/NOTE/MEMORY/RECORD carrier and its **non-authenticating** evidence-status marker. Even if only one concrete graph survives, `other_unmodeled_readings_remain_possible = true`.

An unreadable, cryptic or source-unbound utterance yields `UNRESOLVED_SOURCE` with **no invented event graph**, but the unresolved question remains available for investigation.

No graph can authorize an action. `root_action_authorized = false` always, even when some candidate graph appears to describe an outer directive.

### Useful conclusions without demanding that ambiguity disappear

MOTIF also extracts **conditional invariants**: relations that agree across *all of the currently modeled candidate graphs*, while explicitly preserving the possibility of other, unmodeled readings. For example, it can represent that competing perspectives differ about *who* requested an action but agree on the **carrier** or another bounded property. These invariants are source-conditional, **not independently authenticated real-world facts**.

If a consequential relationship varies across its candidate graphs, the system can attach an **optional discrimination question kind**: Who requested the event? Which scope owns it? Is the utterance direct or reported speech? Does negation attach to the event? This is an inspectable question identifier, **not** an autonomous request or a claim that the user must resolve ambiguity. `auto_interrupt_user_for_ambiguity = false` always.

## Calibration and training provenance

`calibration.py` uses the **original RING-011 train and development data**, not the RING-012 challenge labels. The RING-011 source binder is reconstructed and checked against its exact training source. Word and bigram Bayes are trained on exactly the same source. RING-012 performs **32 finite uncertainty-policy calibration trials** that vary model-vote inclusion, source-text novelty sensitivity and whether disagreement causes wider interpretation sets.

Selection prioritizes coverage of authored development interpretations and then fewer concrete possible worlds. **This is a manually designed preference, not a theoretical probability guarantee.**

The frozen selected policy uses:

```json
{
  "vote_threshold": 0.0,
  "novelty_threshold": 0.45,
  "widen_on_disagreement": false
}
```

On the 90 authored RING-011 development examples, this retained 90/90 selected example graphs with an average **1.39 concrete candidate graphs per phrase**. That score was used for selecting policy parameters; it is **not** a legitimate independent test result. No RING-012 challenge labels were imported during calibration.

## Freshly authored multi-reading challenge

Unlike earlier rings that assigned exactly one acceptable graph to each synthetic utterance, `world.py` constructs cases with **zero, one or multiple admissible readings**. Ambiguity is ground-truth *set-valued* in this deliberately authored task.

Two separately frozen author-written language families yield **120 total cases**: 48 with one acceptable interpretation, 48 with at least two acceptable interpretations, and 24 unbound statements requiring no invented graph. The second family adds new editorial framing to test under-specified passages and source novelty. There is no independent human review, real historical witness, or independently authored test designer.

### Results — post-freeze authored language

| Model or control | Complete coverage of author's allowed readings (of 120) | Average concrete candidate worlds | Unbound cases correctly held | False *exclusive* operative-root readings |
| --- | ---: | ---: | ---: | ---: |
| **RING-012 ambiguity-first lattice** | **104** | **10.2** | **24/24** | **0** |
| Uncalibrated union of the three source methods | 72 | 1.4 | 24/24 | 0 |
| Single RING-011 binder graph | 64 | 0.8 | 24/24 | **8** |
| Single word Bayes graph | 60 | 0.8 | 24/24 | 0 |
| Single word+bigram Bayes graph | 60 | 0.8 | 24/24 | 0 |
| All 24 allowed graphs whenever an event is bound | **120** | **19.2** | 24/24 | 0 |
| Always HOLD | 24 (vacuously: no authorized readings for unbound cases) | 0 | 24/24 | 0 |

**Important denominator:** A method trivially covers all admissible meanings on the 24 unbound cases when it returns no graphs. Among the **96 actually interpretable cases**, RING-012 retained all author-admissible readings on **80/96 (83.3%)**, and missed one or more allowed readings in **16**. The full 24-world ontology control had exhaustive nominal coverage but was much less informative.

**44 of 48** explicitly multi-reading examples received more than one candidate graph. The other four still have an explicit **open-world remainder** and were not declared certain. The system's 10.2 average candidate worlds means it is **substantially less decisive** than the earlier classifiers. It proposed **1,096 extra candidate readings** across 120 examples. This is an exposed cost, not a hidden victory.

The 0 false *exclusive* root-action readings means none of the source challenges was represented **only** by a root-action candidate when the author's admissible readings contained no such root request. It **does not** mean there were no erroneous possibilities among the 1,224 proposed candidate graphs, and it is **not** proof of safety on real-world instructions. All methods were already barred from executing effects.

## Hypergraph feedback

`evidence_graph.py` reconciles every case-level result and source claim with summary metrics and publishes conditional source-bound evidence:

- Frozen training + development + three dependent methods → a composed **open-world ambiguity policy**, with no claim of independence.
- The policy + two test worlds → **104/120 complete interpretation-set coverage**, **16 omitted authored readings**, **1,096 extra hypothesized readings**, **zero exclusive false root-action readings**, **24 correctly unresolved unbound utterances**, and the explicit unresolved challenge of interpreting cryptic natural language.

Rehashing an altered error count, forging independence, duplicating a trial packet, or changing the policy to assert automatic authority fails the contract checks. Hashes identify content, not external factual authenticity.

## How to reproduce

```bash
python -m unittest discover -s experiments/cartridge-ring-011 -p 'test_*.py' -v
python -m unittest discover -s experiments/cartridge-ring-012 -p 'test_*.py' -v

python experiments/cartridge-ring-012/calibration.py \
  --out /tmp/ring012-frozen-policy.json

# The separate author-created multi-reading challenge enters only now.
python experiments/cartridge-ring-012/benchmark.py \
  --policy /tmp/ring012-frozen-policy.json \
  --out /tmp/ring012-postfreeze.json

python experiments/cartridge-ring-012/evidence_graph.py \
  --policy /tmp/ring012-frozen-policy.json \
  --trial /tmp/ring012-postfreeze.json \
  --out /tmp/ring012-ambiguity-graph.json
```

GitHub Actions uploads three machine-readable evidence artifacts: the frozen parameter and source manifest, every individual target/prediction outcome, and the verified many-tail hypergraph evidence.

## What this establishes — and what it does not

**Established within this authored toy world:** MOTIF can represent **multiple competing relational perspectives without forcing any to be definitive**, retain method disagreements and provenance, refuse ungrounded texts, and choose how broadly to preserve possibilities based on prior heldout-for-calibration examples. This is an executable step toward source-aware ambiguity management rather than just another yes/no classifier.

**Not established:** Independent discovery of the semantic ontology, a probabilistically calibrated uncertainty estimate on real language, coherent handling of every cryptic utterance, authenticated historical testimony, general natural-language understanding, or automatic invention of new fundamental mathematical operators. All source events are supplied, all labels are author-defined, and all three models share correlated training and errors.

**Next critical experiment:** Evaluate the *value* of an optional discriminator with a separate source of evidence. Our current code can identify conditional invariants and suggest which typed relation would distinguish alternatives, but has **not** measured whether requesting that observation helps a human or costs more attention than it saves. The system should ask only when ambiguity materially changes the user's goal; it should otherwise proceed using jointly supported, source-qualified conclusions.

**Ambiguity is now an explicit state of the machine, not a defect it has to erase.**
